"""Component risk under Euler, and the four flags. D9, decisions DD146-DD152, bars C139-C146.

**ES at 97.5% is primary** (DD146): Gaussian, on D8's primary sample covariance, over DEV. The
historical-simulation figure over the same changes is reported beside it and never substituted.

**Every leg is measured, including the one the grammar cannot say** (DD139, DD147). A rate leg's
exposure is D4's signed DV01; an FX leg's is its USD P&L per 1% log-move, which is the unit D8's
covariance carries `DEXUSEU` in. D4's `book_dv01` returns nothing for `eurusd`, because an
exchange rate has no duration, and a risk figure built on it would carry that leg at zero.

**Components sum to the total by construction** (DD148). Under the Gaussian measure a leg's
component is `e_i' S e / sigma` scaled to the measure; under historical simulation it is the
leg's mean loss over the scenarios the book's ES averages. Both are linear in the leg's
exposure, which is also why DD150's on/off-thesis split partitions each component exactly.

**A declared DV01 neutrality is measured, not widened** (DD151, X17). `book.py` holds types and
no yields, so it cannot compute a duration; its syntactic invariant stays, and the residual rides
on the report instead.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from statistics import NormalDist

import numpy as np

from deskcraft.book import Book, Currency, InstrumentKind, Leg, Neutrality
from deskcraft.covariance import daily_changes, fit
from deskcraft.factors import FACTOR_SERIES, FactorBasis
from deskcraft.panel import load_daily, load_daily_admitted
from deskcraft.sensitivity import RATE_SENSE_OF, RateSense, leg_sensitivity
from deskcraft.views import View, compile_view
from deskcraft.window import FitWindow

__all__ = [
    "ALPHA",
    "AS_OF",
    "F1_DEAD_WEIGHT",
    "F2_CONCENTRATION",
    "F3_OFF_THESIS",
    "F4_REDUNDANCY",
    "VAR_LEVELS",
    "DeclaredNeutrality",
    "Flag",
    "LegRisk",
    "RiskReport",
    "UnmappedLeg",
    "declared_neutralities",
    "discrete_var_es",
    "gaussian_risk",
    "historical_risk",
    "leg_exposure",
    "levels_at",
    "subadditivity_search",
    "textbook_exhibit",
]

#: The as-of date D7a and D7b already measure at, and the last session `DEXUSEU` carries in DEV.
AS_OF = date(2014, 12, 24)

#: DD146. The Basel FRTB level, and the one §1 of the build order names.
ALPHA = 0.975
#: Reported beside ES for comparison, never as the budget.
VAR_LEVELS = (0.975, 0.99)

#: DD149, fixed before any book was scored. Shares of book ES.
F1_DEAD_WEIGHT = 0.05
F2_CONCENTRATION = 0.50
F3_OFF_THESIS = 0.25
#: Absolute partial correlation of two legs' P&L, given every other leg.
F4_REDUNDANCY = 0.9

#: The FX series D9 can map a leg onto: series -> (the leg's notional currency, the quote). An FX
#: leg on any other series is refused by name rather than mapped by guess.
_FX_QUOTE = {"DEXUSEU": (Currency.EUR, "USD per EUR")}


class UnmappedLeg(ValueError):
    """A leg D9 cannot turn into an exposure: an FX pair it has no quote for."""


def levels_at(as_of: date = AS_OF) -> dict[str, float]:
    """Every daily series' published level on `as_of`, from both committed daily panels."""
    window = FitWindow.dev()
    out: dict[str, float] = {}
    for panel in (load_daily(window), load_daily_admitted(window)):
        row = panel.dates.index(as_of)
        for series in panel.series:
            value = panel.values[series][row]
            if value is not None:
                out[series] = value
    return out


def leg_exposure(leg: Leg, levels: Mapping[str, float]) -> dict[str, float]:
    """USD P&L per unit change in each series the leg holds (DD147).

    A rate leg returns D4's signed DV01 per series, per basis point, unchanged. An FX leg returns
    `direction x notional x level x 0.01`, per 1% log-move. An unpriceable leg raises, because D4
    raises.
    """
    if RATE_SENSE_OF[leg.instrument.kind] is RateSense.NONE:
        if leg.instrument.kind is not InstrumentKind.FX_SPOT:
            raise UnmappedLeg(f"{leg.leg_id!r} is a {leg.instrument.kind} with no rate sense")
        (component,) = leg.instrument.components
        quote = _FX_QUOTE.get(component.series)
        if quote is None or leg.notional.currency is not quote[0]:
            raise UnmappedLeg(
                f"{leg.leg_id!r} holds {component.series} in {leg.notional.currency}; D9 maps "
                f"{sorted(_FX_QUOTE)} only, each against the currency its quote is per unit of."
            )
        level = float(levels[component.series])
        per_percent = float(int(leg.direction)) * leg.notional.amount * level * 0.01
        return {component.series: per_percent * component.coefficient}
    out: dict[str, float] = {}
    for item in leg_sensitivity(leg, levels).components:
        out[item.series] = out.get(item.series, 0.0) + item.dv01
    return out


@dataclass(frozen=True, slots=True)
class DeclaredNeutrality:
    """A leg declaring DV01 neutrality, and what a parallel one-basis-point move leaves (X17)."""

    leg_id: str
    declared: Neutrality
    residual_per_bp: float
    #: `|residual| / largest |component DV01|`.
    residual_share: float


def declared_neutralities(book: Book, levels: Mapping[str, float]) -> tuple[DeclaredNeutrality, ...]:
    """Every `DV01`-declaring leg's measured residual (DD151). Empty when none declares it."""
    out = []
    for leg in book.legs:
        if leg.instrument.neutrality is not Neutrality.DV01:
            continue
        dv01s = [item.dv01 for item in leg_sensitivity(leg, levels).components]
        residual = math.fsum(dv01s)
        out.append(
            DeclaredNeutrality(
                leg_id=leg.leg_id,
                declared=leg.instrument.neutrality,
                residual_per_bp=residual,
                residual_share=abs(residual) / max(abs(value) for value in dv01s),
            )
        )
    return tuple(out)


@dataclass(frozen=True, slots=True)
class LegRisk:
    """One leg's share of the book's ES, split along the view (DD148, DD150)."""

    leg_id: str
    component: float
    share: float
    on_thesis: float
    off_thesis: float


@dataclass(frozen=True, slots=True)
class Flag:
    """One of build order §2's four, with the number that fired it and its threshold."""

    code: str
    legs: tuple[str, ...]
    value: float
    threshold: float


@dataclass(frozen=True)
class RiskReport:
    book_id: str
    method: str
    alpha: float
    series: tuple[str, ...]
    observations: int
    es: float
    var: dict[float, float]
    legs: tuple[LegRisk, ...]
    flags: tuple[Flag, ...]
    #: F4's statistic for every pair, `(leg, leg) -> partial correlation`.
    partial_correlations: dict[tuple[str, str], float]
    neutralities: tuple[DeclaredNeutrality, ...]
    screened: int

    def leg(self, leg_id: str) -> LegRisk:
        return next(item for item in self.legs if item.leg_id == leg_id)


def _setup(
    book: Book, view: View, basis: FactorBasis, levels: Mapping[str, float] | None
) -> tuple[dict[str, float], tuple[str, ...], np.ndarray, np.ndarray]:
    """Levels, the series set, the legs x series exposure matrix, and the unit view target."""
    levels = levels_at() if levels is None else dict(levels)
    exposures = {leg.leg_id: leg_exposure(leg, levels) for leg in book.legs}
    target = compile_view(view, basis)
    reached = [s for s, v in zip(FACTOR_SERIES, target.vector) if v != 0.0]
    held = [s for e in exposures.values() for s in e]
    series = tuple(dict.fromkeys([*held, *reached]))
    matrix = np.array([[exposures[leg.leg_id].get(s, 0.0) for s in series] for leg in book.legs])
    lookup = dict(zip(FACTOR_SERIES, target.vector))
    t = np.array([lookup.get(s, 0.0) for s in series])
    return levels, series, matrix, t / np.linalg.norm(t)


def _flags(
    legs: tuple[LegRisk, ...], es: float, partial: dict[tuple[str, str], float]
) -> tuple[Flag, ...]:
    out: list[Flag] = []
    for leg in legs:
        if abs(leg.share) < F1_DEAD_WEIGHT:
            out.append(Flag("F1", (leg.leg_id,), leg.share, F1_DEAD_WEIGHT))
        if leg.share > F2_CONCENTRATION:
            out.append(Flag("F2", (leg.leg_id,), leg.share, F2_CONCENTRATION))
        if leg.off_thesis / es >= F3_OFF_THESIS:
            out.append(Flag("F3", (leg.leg_id,), leg.off_thesis / es, F3_OFF_THESIS))
    for pair, value in partial.items():
        if abs(value) >= F4_REDUNDANCY:
            out.append(Flag("F4", pair, value, F4_REDUNDANCY))
    return tuple(out)


def _partial(book: Book, pnl_cov: np.ndarray) -> dict[tuple[str, str], float]:
    ids = book.leg_ids
    if len(ids) < 3:
        # With two legs there is nothing to condition on; the partial is the raw correlation.
        sd = np.sqrt(np.diag(pnl_cov))
        corr = pnl_cov / np.outer(sd, sd)
        return {(ids[i], ids[j]): float(corr[i, j]) for i in range(len(ids)) for j in range(i + 1, len(ids))}
    precision = np.linalg.inv(pnl_cov)
    d = np.sqrt(np.diag(precision))
    return {
        (ids[i], ids[j]): float(-precision[i, j] / (d[i] * d[j]))
        for i in range(len(ids))
        for j in range(i + 1, len(ids))
    }


def gaussian_risk(
    book: Book,
    view: View,
    basis: FactorBasis,
    levels: Mapping[str, float] | None = None,
    window: FitWindow | None = None,
) -> RiskReport:
    """The primary measure (DD146): Gaussian ES at `ALPHA` on D8's sample covariance."""
    levels, series, exposure, t = _setup(book, view, basis, levels)
    covariance = fit(series, window)
    sigma_matrix = covariance.array()
    total = exposure.sum(axis=0)
    gradient = sigma_matrix @ total
    sigma = math.sqrt(float(total @ gradient))
    z = NormalDist().inv_cdf(ALPHA)
    es_scale = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi) / (1.0 - ALPHA)
    es = sigma * es_scale

    legs = []
    for leg, row in zip(book.legs, exposure):
        component = float(row @ gradient) / sigma * es_scale
        on = float(row @ t) * float(t @ gradient) / sigma * es_scale
        legs.append(LegRisk(leg.leg_id, component, component / es, on, component - on))
    pnl_cov = exposure @ sigma_matrix @ exposure.T
    partial = _partial(book, pnl_cov)
    legs_t = tuple(legs)
    return RiskReport(
        book_id=book.book_id,
        method="GAUSSIAN",
        alpha=ALPHA,
        series=series,
        observations=covariance.observations,
        es=es,
        var={level: sigma * NormalDist().inv_cdf(level) for level in VAR_LEVELS},
        legs=legs_t,
        flags=_flags(legs_t, es, partial),
        partial_correlations=partial,
        neutralities=declared_neutralities(book, levels),
        screened=len(legs_t),
    )


def _tail(losses: np.ndarray, alpha: float) -> np.ndarray:
    """Indices of the ceil((1 - alpha) T) largest losses, in a stable order."""
    k = math.ceil((1.0 - alpha) * losses.shape[0] - 1e-9)
    return np.argsort(-losses, kind="stable")[:k]


def historical_risk(
    book: Book,
    view: View,
    basis: FactorBasis,
    levels: Mapping[str, float] | None = None,
    window: FitWindow | None = None,
) -> RiskReport:
    """Historical simulation over DEV's daily changes: ES as the mean of the worst `1 - ALPHA`."""
    levels, series, exposure, t = _setup(book, view, basis, levels)
    _, changes, _ = daily_changes(series, window)
    leg_loss = -(changes @ exposure.T)  # T x legs
    loss = leg_loss.sum(axis=1)
    tail = _tail(loss, ALPHA)
    es = float(loss[tail].mean())
    on_loss = -np.outer(changes @ t, exposure @ t)  # T x legs
    legs = []
    for k, leg in enumerate(book.legs):
        component = float(leg_loss[tail, k].mean())
        on = float(on_loss[tail, k].mean())
        legs.append(LegRisk(leg.leg_id, component, component / es, on, component - on))
    var = {}
    for level in VAR_LEVELS:
        worst = _tail(loss, level)
        var[level] = float(loss[worst[-1]])
    pnl_cov = np.cov(-leg_loss, rowvar=False).reshape(len(book.legs), len(book.legs))
    partial = _partial(book, pnl_cov)
    legs_t = tuple(legs)
    return RiskReport(
        book_id=book.book_id,
        method="HISTORICAL",
        alpha=ALPHA,
        series=series,
        observations=int(changes.shape[0]),
        es=es,
        var=var,
        legs=legs_t,
        flags=_flags(legs_t, es, partial),
        partial_correlations=partial,
        neutralities=declared_neutralities(book, levels),
        screened=len(legs_t),
    )


def subadditivity_search(
    book: Book,
    levels: Mapping[str, float] | None = None,
    window: FitWindow | None = None,
    alphas: tuple[float, ...] = VAR_LEVELS,
) -> dict[str, list[tuple[float, tuple[str, ...], float, float]]]:
    """Every sub-book of two or more legs, under DEV historical simulation.

    Returns violations by measure: `(alpha, legs, risk of the sum, sum of the risks)` wherever the
    first exceeds the second. ES never should; VaR may.
    """
    levels = levels_at() if levels is None else dict(levels)
    exposures = {leg.leg_id: leg_exposure(leg, levels) for leg in book.legs}
    series = tuple(dict.fromkeys(s for e in exposures.values() for s in e))
    _, changes, _ = daily_changes(series, window)
    loss = {
        leg_id: -(changes @ np.array([e.get(s, 0.0) for s in series]))
        for leg_id, e in exposures.items()
    }

    def var(x: np.ndarray, a: float) -> float:
        return float(x[_tail(x, a)[-1]])

    def es(x: np.ndarray, a: float) -> float:
        return float(x[_tail(x, a)].mean())

    ids = book.leg_ids
    found: dict[str, list[tuple[float, tuple[str, ...], float, float]]] = {"VAR": [], "ES": []}
    for mask in range(1, 1 << len(ids)):
        subset = tuple(ids[i] for i in range(len(ids)) if mask >> i & 1)
        if len(subset) < 2:
            continue
        joint = sum(loss[i] for i in subset)
        for a in alphas:
            for name, measure in (("VAR", var), ("ES", es)):
                whole = measure(joint, a)
                parts = math.fsum(measure(loss[i], a) for i in subset)
                if whole > parts + 1e-9 * abs(parts):
                    found[name].append((a, subset, whole, parts))
    return found


def discrete_var_es(outcomes: Mapping[float, float], alpha: float) -> tuple[float, float]:
    """VaR and ES of a discrete loss distribution `{loss: probability}` (Acerbi-Tasche 2002)."""
    cumulative = 0.0
    var = max(outcomes)
    for loss in sorted(outcomes):
        cumulative += outcomes[loss]
        if cumulative >= alpha - 1e-15:
            var = loss
            break
    above = math.fsum(loss * p for loss, p in outcomes.items() if loss > var)
    at_or_below = math.fsum(p for loss, p in outcomes.items() if loss <= var)
    return var, (above + var * (at_or_below - alpha)) / (1.0 - alpha)


def textbook_exhibit(alpha: float = ALPHA) -> dict[str, float]:
    """Two independent bonds, each losing 100 with probability 2%: VaR fails, ES does not.

    Synthetic, and labelled so. At 97.5% each bond alone has VaR 0 -- a 2% default sits inside
    the 2.5% tail -- while the pair defaults somewhere with probability 3.96% and has VaR 100.
    """
    p = 0.02
    single = {0.0: 1.0 - p, 100.0: p}
    pair = {0.0: (1.0 - p) ** 2, 100.0: 2.0 * p * (1.0 - p), 200.0: p * p}
    var_one, es_one = discrete_var_es(single, alpha)
    var_two, es_two = discrete_var_es(pair, alpha)
    return {
        "var_single": var_one,
        "var_pair": var_two,
        "es_single": es_one,
        "es_pair": es_two,
    }
