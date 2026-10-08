"""Sizing under the risk budget. D11, decisions DD156-DD160, bars C153-C157.

**The objective is the view, never a return** (DD156). The engine states no expected return, so
the two optimising rules minimise tail risk **per unit of view exposure**: subject to `v'w = 1`,
with `v_i` a leg's P&L per basis point of the compiled view direction and `w >= 0`. Min-variance
is the Gaussian form of that problem. Max-diversification, ERC and 1/N take no view and are the
benchmarks. Every sized book is then scaled to one budget on one measure (DD158), so the rules
differ in shape and never in size.

**The two linear programs** (DD159) are Rockafellar-Uryasev CVaR and Chekhlov-Uryasev-Zabarankin
CDaR on DEV's daily leg P&L, solved by SciPy's HiGHS. Their optimum is the Acerbi-Tasche form of
historical CVaR, which weights the fractional tail observation; `tail_mean` computes it directly
so the programs can be checked against arithmetic rather than against themselves.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

import numpy as np
from scipy import optimize, sparse

from deskcraft.attribution import ALPHA, leg_exposure, levels_at
from deskcraft.book import Book
from deskcraft.costs import DurationConvention, gross_dv01
from deskcraft.covariance import daily_changes, fit
from deskcraft.factors import FACTOR_SERIES, FactorBasis
from deskcraft.views import View, compile_view
from deskcraft.window import FitWindow

__all__ = [
    "RISK_BUDGET_ES",
    "LegSet",
    "Rule",
    "SizedBook",
    "Unit",
    "drawdowns",
    "leg_set",
    "size",
    "size_all",
    "tail_mean",
    "tracking_error",
    "weights",
]

#: DD158. A unit, not a view on how much risk to take: it cancels from every comparison.
RISK_BUDGET_ES = 1_000_000.0


class Unit(StrEnum):
    """What one unit of a leg is (DD157)."""

    #: One dollar of gross DV01: D7b's convention for generated legs.
    GROSS_DV01 = "GROSS_DV01"
    #: The leg as stated: the hand-built book's convention.
    STATED = "STATED"


class Rule(StrEnum):
    CVAR_LP = "CVAR_LP"
    CDAR_LP = "CDAR_LP"
    MIN_VARIANCE = "MIN_VARIANCE"
    MAX_DIVERSIFICATION = "MAX_DIVERSIFICATION"
    EQUAL_RISK_CONTRIBUTION = "EQUAL_RISK_CONTRIBUTION"
    ONE_OVER_N = "ONE_OVER_N"


def _es_scale(alpha: float = ALPHA) -> float:
    from statistics import NormalDist

    z = NormalDist().inv_cdf(alpha)
    return math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi) / (1.0 - alpha)


@dataclass(frozen=True)
class LegSet:
    """Legs at unit size: their exposures, view loadings, P&L history and P&L covariance."""

    book_id: str
    leg_ids: tuple[str, ...]
    unit: Unit
    #: v_i: P&L per basis point of the unit view direction, per unit of leg i.
    view: np.ndarray
    #: T x n daily P&L per unit, DEV.
    pnl: np.ndarray
    #: n x n P&L covariance per unit, from D8's primary covariance.
    covariance: np.ndarray


def leg_set(
    book: Book,
    view: View,
    basis: FactorBasis,
    unit: Unit,
    levels: Mapping[str, float] | None = None,
    window: FitWindow | None = None,
) -> LegSet:
    """The book's legs at unit size (DD157), on D8's primary over their series and the view's."""
    levels = levels_at() if levels is None else dict(levels)
    exposures = []
    for leg in book.legs:
        e = leg_exposure(leg, levels)
        if unit is Unit.GROSS_DV01:
            scale = gross_dv01(leg, levels, DurationConvention.AS_QUOTED)
            e = {s: v / scale for s, v in e.items()}
        exposures.append(e)
    target = compile_view(view, basis)
    reached = [s for s, v in zip(FACTOR_SERIES, target.vector) if v != 0.0]
    series = tuple(dict.fromkeys([*(s for e in exposures for s in e), *reached]))
    matrix = np.array([[e.get(s, 0.0) for s in series] for e in exposures])
    lookup = dict(zip(FACTOR_SERIES, target.vector))
    t = np.array([lookup.get(s, 0.0) for s in series])
    t = t / np.linalg.norm(t)
    _, changes, _ = daily_changes(series, window)
    sigma = fit(series, window).array()
    return LegSet(
        book_id=book.book_id,
        leg_ids=book.leg_ids,
        unit=unit,
        view=matrix @ t,
        pnl=changes @ matrix.T,
        covariance=matrix @ sigma @ matrix.T,
    )


def tail_mean(losses: np.ndarray, alpha: float = ALPHA) -> float:
    """Historical CVaR in the Acerbi-Tasche form, which is the Rockafellar-Uryasev optimum.

    The mean of the worst `(1 - alpha) T` observations, the last one counted fractionally.
    """
    ordered = np.sort(np.asarray(losses, dtype=float))[::-1]
    m = (1.0 - alpha) * ordered.size
    j = int(math.floor(m + 1e-12))
    head = float(ordered[:j].sum())
    if j < ordered.size and m - j > 1e-12:
        head += (m - j) * float(ordered[j])
    return head / m


def drawdowns(pnl: np.ndarray) -> np.ndarray:
    """Drawdown from the running peak of cumulative P&L, the peak including the start at zero."""
    cumulative = np.cumsum(pnl)
    peak = np.maximum.accumulate(np.maximum(cumulative, 0.0))
    return peak - cumulative


def _cvar_lp(legs: LegSet, alpha: float) -> tuple[np.ndarray, float]:
    t, n = legs.pnl.shape
    k = 1.0 / ((1.0 - alpha) * t)
    c = np.concatenate([np.zeros(n), [1.0], np.full(t, k)])
    a = sparse.hstack(
        [sparse.csr_matrix(-legs.pnl), sparse.csr_matrix(-np.ones((t, 1))), -sparse.eye(t)]
    ).tocsr()
    eq = sparse.csr_matrix(np.concatenate([legs.view, [0.0], np.zeros(t)])[None, :])
    bounds = [(0.0, None)] * n + [(None, None)] + [(0.0, None)] * t
    result = optimize.linprog(c, A_ub=a, b_ub=np.zeros(t), A_eq=eq, b_eq=[1.0],
                              bounds=bounds, method="highs")
    if result.status != 0:
        raise ValueError(f"the CVaR program did not solve: {result.message}")
    return result.x[:n], float(result.fun)


def _cdar_lp(legs: LegSet, alpha: float) -> tuple[np.ndarray, float]:
    t, n = legs.pnl.shape
    cumulative = np.cumsum(legs.pnl, axis=0)
    k = 1.0 / ((1.0 - alpha) * t)
    # x = [w (n), zeta, y (t), z (t)]
    c = np.concatenate([np.zeros(n), [1.0], np.zeros(t), np.full(t, k)])
    eye = sparse.eye(t, format="csr")
    zeros_t1 = sparse.csr_matrix((t, 1))
    zeros_tt = sparse.csr_matrix((t, t))
    # y_t >= C_t w   ->   C_t w - y_t <= 0
    peak = sparse.hstack([sparse.csr_matrix(cumulative), zeros_t1, -eye, zeros_tt])
    # y_{t-1} - y_t <= 0
    step = sparse.diags([np.ones(t - 1), -np.ones(t - 1)], [0, 1], shape=(t - 1, t))
    monotone = sparse.hstack(
        [sparse.csr_matrix((t - 1, n)), sparse.csr_matrix((t - 1, 1)), step, sparse.csr_matrix((t - 1, t))]
    )
    # y_t - C_t w - zeta - z_t <= 0
    tail = sparse.hstack([sparse.csr_matrix(-cumulative), sparse.csr_matrix(-np.ones((t, 1))), eye, -eye])
    a = sparse.vstack([peak, monotone, tail]).tocsr()
    b = np.zeros(a.shape[0])
    eq = sparse.csr_matrix(np.concatenate([legs.view, [0.0], np.zeros(2 * t)])[None, :])
    bounds = [(0.0, None)] * n + [(None, None)] + [(0.0, None)] * (2 * t)
    result = optimize.linprog(c, A_ub=a, b_ub=b, A_eq=eq, b_eq=[1.0], bounds=bounds, method="highs")
    if result.status != 0:
        raise ValueError(f"the CDaR program did not solve: {result.message}")
    return result.x[:n], float(result.fun)


def _min_quadratic(covariance: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """min w'Sw subject to direction'w = 1 and w >= 0, by exact enumeration of supports.

    Small n, so every support is tried and the KKT-feasible one with least variance kept: exact
    and deterministic where an iterative solver would be a tolerance.
    """
    n = covariance.shape[0]
    best: tuple[float, np.ndarray] | None = None
    for size in range(1, n + 1):
        for support in itertools.combinations(range(n), size):
            idx = list(support)
            s = covariance[np.ix_(idx, idx)]
            d = direction[idx]
            try:
                solved = np.linalg.solve(s, d)
            except np.linalg.LinAlgError:
                continue
            denominator = float(d @ solved)
            if denominator <= 0.0:
                continue
            w_s = solved / denominator
            if (w_s < -1e-12).any():
                continue
            w = np.zeros(n)
            w[idx] = np.clip(w_s, 0.0, None)
            variance = float(w @ covariance @ w)
            if best is None or variance < best[0] - 1e-15:
                best = (variance, w)
    if best is None:
        raise ValueError("no long-only book reaches the constraint")
    return best[1]


def _erc(covariance: np.ndarray) -> np.ndarray:
    """Spinu (2013): min 1/2 w'Sw - (1/n) sum ln w, whose optimum equalises Euler contributions."""
    n = covariance.shape[0]

    def objective(y: np.ndarray) -> tuple[float, np.ndarray]:
        w = np.exp(y)
        sw = covariance @ w
        value = 0.5 * float(w @ sw) - float(y.sum()) / n
        return value, w * sw - 1.0 / n

    start = -0.5 * np.log(np.diag(covariance))
    result = optimize.minimize(objective, start, jac=True, method="BFGS",
                               options={"gtol": 1e-13, "maxiter": 10_000})
    return np.exp(result.x)


def weights(legs: LegSet, rule: Rule, alpha: float = ALPHA) -> np.ndarray:
    """The rule's multipliers, unscaled."""
    n = len(legs.leg_ids)
    if rule is Rule.ONE_OVER_N:
        return np.ones(n)
    if rule is Rule.EQUAL_RISK_CONTRIBUTION:
        return _erc(legs.covariance)
    if rule is Rule.MIN_VARIANCE:
        return _min_quadratic(legs.covariance, legs.view)
    if rule is Rule.MAX_DIVERSIFICATION:
        return _min_quadratic(legs.covariance, np.sqrt(np.diag(legs.covariance)))
    if rule is Rule.CVAR_LP:
        return _cvar_lp(legs, alpha)[0]
    if rule is Rule.CDAR_LP:
        return _cdar_lp(legs, alpha)[0]
    raise ValueError(f"unknown rule {rule!r}")


@dataclass(frozen=True)
class SizedBook:
    """One rule's book at the budget (DD158)."""

    rule: Rule
    leg_ids: tuple[str, ...]
    weights: tuple[float, ...]
    #: USD per basis point of the view direction, at the budget.
    view_exposure: float
    gaussian_es: float
    historical_es: float
    cdar: float
    max_drawdown: float
    #: Euler shares of Gaussian ES, by leg.
    shares: tuple[float, ...]

    @property
    def weight_shares(self) -> tuple[float, ...]:
        total = math.fsum(self.weights)
        return tuple(w / total for w in self.weights)


def size(legs: LegSet, rule: Rule, alpha: float = ALPHA) -> SizedBook:
    """One rule's weights, scaled so Gaussian ES equals `RISK_BUDGET_ES`."""
    raw = weights(legs, rule, alpha)
    sigma = math.sqrt(float(raw @ legs.covariance @ raw))
    scale = RISK_BUDGET_ES / (sigma * _es_scale(alpha))
    w = raw * scale
    book_pnl = legs.pnl @ w
    gradient = legs.covariance @ w
    variance = float(w @ gradient)
    return SizedBook(
        rule=rule,
        leg_ids=legs.leg_ids,
        weights=tuple(float(x) for x in w),
        view_exposure=float(legs.view @ w),
        gaussian_es=math.sqrt(variance) * _es_scale(alpha),
        historical_es=tail_mean(-book_pnl, alpha),
        cdar=tail_mean(drawdowns(book_pnl), alpha),
        max_drawdown=float(drawdowns(book_pnl).max()),
        shares=tuple(float(x) for x in w * gradient / variance),
    )


def size_all(legs: LegSet, alpha: float = ALPHA) -> dict[Rule, SizedBook]:
    return {rule: size(legs, rule, alpha) for rule in Rule}


def tracking_error(first: SizedBook, second: SizedBook, legs: LegSet) -> float:
    """Gaussian ES of the difference between two sized books, as a fraction of the budget."""
    diff = np.array(first.weights) - np.array(second.weights)
    return math.sqrt(float(diff @ legs.covariance @ diff)) * _es_scale() / RISK_BUDGET_ES
