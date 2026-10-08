"""The construction backtest's machinery. D15, registered in the joint pre-commit (DD134).

Nothing here reads a row dated after `DEV_END`. Every function takes arrays or a `FitWindow`, so
the dry run is a DEV pseudo-out-of-sample split and the real run is the same code handed the
out-of-sample record in the one commit DD102 reserves for it.

**The statistics, each the published form and nothing tuned:**

- **Ledoit-Wolf (2008)** Sharpe-difference test, HAC with VAR(1) prewhitening and the
  quadratic-spectral kernel at Andrews' (1991) AR(1) plug-in bandwidth -- their `HACPW`.
- **Politis-Romano (1994)** stationary bootstrap indices.
- **Bailey-Lopez de Prado (2014)** Deflated Sharpe, on a trial count stated in advance.
- **Bailey, Borwein, Lopez de Prado, Zhu (2017)** probability of backtest overfitting by CSCV.
- **Hansen (2005)** SPA, consistent p-value, on the stationary bootstrap.
- **Risk per view** (DD169): view per unit of realised Acerbi-Tasche ES, one book against another,
  its error by the same stationary bootstrap.

**The construction** is a book held from its construction date and walked forward: the basis,
the covariance and the sizing are all estimated on a fit window, and the test window only ever
supplies the P&L. That is the same discipline `FitWindow` enforces everywhere else.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Mapping
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np

from deskcraft.attribution import ALPHA, leg_exposure
from deskcraft.book import Book
from deskcraft.costs import DurationConvention, gross_dv01
from deskcraft.covariance import daily_changes
from deskcraft.sizing import tail_mean
from deskcraft.window import FitWindow

__all__ = [
    "TRADING_DAYS",
    "RiskPerView",
    "SharpeDifference",
    "deflated_sharpe",
    "held_pnl",
    "minimum_detectable_difference",
    "pbo_cscv",
    "power",
    "risk_per_view",
    "sharpe",
    "sharpe_difference",
    "spa_pvalue",
    "stationary_bootstrap",
]

#: Annualisation. The panel runs at 260.89 sessions a year (`AMENDMENT_A4` §3.2); 252 is the
#: convention every cited paper uses, and a Sharpe ratio is reported in their units.
TRADING_DAYS = 252

_NORMAL = NormalDist()


def sharpe(returns: np.ndarray) -> float:
    """Annualised Sharpe ratio of a daily P&L series, zero benchmark."""
    r = np.asarray(returns, dtype=float)
    return float(r.mean() / r.std(ddof=1) * math.sqrt(TRADING_DAYS))


def _qs_kernel(x: np.ndarray) -> np.ndarray:
    """The quadratic-spectral kernel, with k(0) = 1."""
    out = np.ones_like(x, dtype=float)
    nz = x != 0.0
    z = 6.0 * math.pi * x[nz] / 5.0
    out[nz] = 25.0 / (12.0 * math.pi**2 * x[nz] ** 2) * (np.sin(z) / z - np.cos(z))
    return out


def _andrews_bandwidth(e: np.ndarray) -> float:
    """Andrews (1991) AR(1) plug-in bandwidth for the QS kernel."""
    t = e.shape[0]
    numerator = 0.0
    denominator = 0.0
    for k in range(e.shape[1]):
        x = e[:, k]
        rho = float(np.dot(x[1:], x[:-1]) / np.dot(x[:-1], x[:-1]))
        rho = min(max(rho, -0.97), 0.97)
        sigma2 = float(np.mean((x[1:] - rho * x[:-1]) ** 2))
        numerator += 4.0 * rho**2 * sigma2**2 / (1.0 - rho) ** 8
        denominator += sigma2**2 / (1.0 - rho) ** 4
    alpha2 = numerator / denominator
    return 1.3221 * (alpha2 * t) ** 0.2


def _hac_prewhitened(y: np.ndarray) -> np.ndarray:
    """Long-run covariance of `y` (T x k, demeaned here): VAR(1) prewhitening, QS kernel."""
    x = y - y.mean(axis=0)
    lagged, current = x[:-1], x[1:]
    a = np.linalg.lstsq(lagged, current, rcond=None)[0].T
    e = current - lagged @ a.T
    t = e.shape[0]
    bandwidth = _andrews_bandwidth(e)
    omega = e.T @ e / t
    lags = np.arange(1, t)
    weights = _qs_kernel(lags / bandwidth)
    for j, w in zip(lags, weights):
        if abs(w) < 1e-12 and j > 5 * bandwidth:
            break
        gamma = e[j:].T @ e[:-j] / t
        omega += w * (gamma + gamma.T)
    recolour = np.linalg.inv(np.eye(x.shape[1]) - a)
    return recolour @ omega @ recolour.T


@dataclass(frozen=True, slots=True)
class SharpeDifference:
    """Ledoit-Wolf's test of H0: SR_a = SR_b, annualised."""

    sharpe_a: float
    sharpe_b: float
    difference: float
    standard_error: float
    p_value: float
    correlation: float
    observations: int


def sharpe_difference(a: np.ndarray, b: np.ndarray) -> SharpeDifference:
    """Ledoit and Wolf (2008), `HACPW`: the delta method on the first two moments."""
    ra, rb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    t = ra.size
    y = np.column_stack([ra, rb, ra**2, rb**2])
    mu_a, mu_b, g_a, g_b = y.mean(axis=0)
    va, vb = g_a - mu_a**2, g_b - mu_b**2
    delta = mu_a / math.sqrt(va) - mu_b / math.sqrt(vb)
    gradient = np.array(
        [g_a / va**1.5, -g_b / vb**1.5, -0.5 * mu_a / va**1.5, 0.5 * mu_b / vb**1.5]
    )
    psi = _hac_prewhitened(y)
    se = math.sqrt(float(gradient @ psi @ gradient) / t)
    scale = math.sqrt(TRADING_DAYS)
    z = delta / se
    return SharpeDifference(
        sharpe_a=mu_a / math.sqrt(va) * scale,
        sharpe_b=mu_b / math.sqrt(vb) * scale,
        difference=delta * scale,
        standard_error=se * scale,
        p_value=2.0 * (1.0 - _NORMAL.cdf(abs(z))),
        correlation=float(np.corrcoef(ra, rb)[0, 1]),
        observations=t,
    )


def power(effect: float, standard_error: float, alpha: float = 0.05) -> float:
    """Two-sided power of a normal test against an annualised Sharpe difference of `effect`."""
    z = _NORMAL.inv_cdf(1.0 - alpha / 2.0)
    shift = abs(effect) / standard_error
    return float(_NORMAL.cdf(shift - z) + _NORMAL.cdf(-shift - z))


def minimum_detectable_difference(
    standard_error: float, alpha: float = 0.05, target: float = 0.8
) -> float:
    """The annualised Sharpe difference detected with probability `target` at level `alpha`."""
    return (_NORMAL.inv_cdf(1.0 - alpha / 2.0) + _NORMAL.inv_cdf(target)) * standard_error


def stationary_bootstrap(t: int, mean_block: float, rng: np.random.Generator) -> np.ndarray:
    """Politis and Romano (1994): one resample of `range(t)` in blocks of geometric length."""
    starts = rng.random(t) < 1.0 / mean_block
    starts[0] = True
    fresh = rng.integers(t, size=t)
    positions = np.arange(t)
    # Each index continues the block that began at the latest start at or before it.
    last = np.maximum.accumulate(np.where(starts, positions, 0))
    return (fresh[last] + positions - last) % t


@dataclass(frozen=True, slots=True)
class RiskPerView:
    """View carried per unit of realised tail risk, one held book against another (DD169).

    `g` is **G = ln(v_a / ES_a) - ln(v_b / ES_b)**, with ES the historical expected shortfall
    of the held daily P&L. Positive G: the first book holds more view per unit of realised tail
    risk. `plausible` is **G* = ln(v_a / v_b)**, the first book's ex-ante advantage at equal
    Gaussian ES carried unchanged into realised risk, and `power` is the two-sided 5% power at it.
    """

    g: float
    es_a: float
    es_b: float
    standard_error: float
    p_value: float
    interval: tuple[float, float]
    plausible: float
    power: float


def risk_per_view(
    a: np.ndarray,
    b: np.ndarray,
    view_a: float,
    view_b: float,
    rng: np.random.Generator,
    resamples: int = 10_000,
    mean_block: float = 21.0,
    alpha: float = ALPHA,
) -> RiskPerView:
    """G for two books held over the same days, with its stationary-bootstrap error and power.

    G is scale-free in each book, because realised ES and view exposure both scale linearly with
    it, so the covariance a book was sized on cancels, as it does from a Sharpe ratio. The two
    books are resampled on the same indices: the test is paired, as the Sharpe test is.
    """
    ra, rb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if ra.shape != rb.shape:
        raise ValueError(f"the books are not over the same days: {ra.shape} and {rb.shape}")
    if view_a <= 0.0 or view_b <= 0.0:
        raise ValueError(f"a book carries no view: {view_a}, {view_b}")

    def statistic(x: np.ndarray, y: np.ndarray) -> float:
        es_x, es_y = tail_mean(-x, alpha), tail_mean(-y, alpha)
        if es_x <= 0.0 or es_y <= 0.0:
            raise ValueError("a book's realised tail is a gain, so risk per view is undefined")
        return math.log(view_a / es_x) - math.log(view_b / es_y)

    g = statistic(ra, rb)
    draws = np.empty(resamples)
    for k in range(resamples):
        idx = stationary_bootstrap(ra.size, mean_block, rng)
        draws[k] = statistic(ra[idx], rb[idx])
    se = float(draws.std(ddof=1))
    plausible = math.log(view_a / view_b)
    # Two books whose P&L are proportional are one book: G does not move under resampling, and
    # there is nothing to test. Reported as no evidence and no power rather than a division.
    degenerate = se <= 1e-12
    return RiskPerView(
        g=g,
        es_a=tail_mean(-ra, alpha),
        es_b=tail_mean(-rb, alpha),
        standard_error=se,
        p_value=1.0 if degenerate else 2.0 * (1.0 - _NORMAL.cdf(abs(g) / se)),
        interval=(float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))),
        plausible=plausible,
        power=0.0 if degenerate else power(plausible, se),
    )


def deflated_sharpe(
    returns: np.ndarray, trials: int, trial_sharpe_variance: float
) -> float:
    """Bailey and Lopez de Prado (2014): the probability the true Sharpe exceeds zero after
    selection among `trials`, in daily (non-annualised) units, with moments from `returns`.
    """
    r = np.asarray(returns, dtype=float)
    t = r.size
    sr = r.mean() / r.std(ddof=1)
    centred = r - r.mean()
    skew = float((centred**3).mean() / centred.std() ** 3)
    kurt = float((centred**4).mean() / centred.std() ** 4)
    gamma = 0.5772156649015329
    expected_max = math.sqrt(trial_sharpe_variance) * (
        (1.0 - gamma) * _NORMAL.inv_cdf(1.0 - 1.0 / trials)
        + gamma * _NORMAL.inv_cdf(1.0 - 1.0 / (trials * math.e))
    )
    denominator = math.sqrt(1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr * sr)
    return float(_NORMAL.cdf((sr - expected_max) * math.sqrt(t - 1) / denominator))


def pbo_cscv(returns: np.ndarray, blocks: int = 16) -> float:
    """Probability of backtest overfitting by combinatorially symmetric cross-validation.

    `returns` is T x N, one column per configuration. The sample is cut into `blocks` equal
    parts; each half of the parts is an in-sample choice of the best Sharpe, and the logit of
    its out-of-sample rank is recorded. PBO is the share of splits where that logit is <= 0.
    """
    m = np.asarray(returns, dtype=float)
    t, n = m.shape
    size = t // blocks
    parts = [m[i * size : (i + 1) * size] for i in range(blocks)]
    logits = []
    for chosen in itertools.combinations(range(blocks), blocks // 2):
        ins = np.vstack([parts[i] for i in chosen])
        outs = np.vstack([parts[i] for i in range(blocks) if i not in chosen])
        sr_in = ins.mean(axis=0) / ins.std(axis=0, ddof=1)
        sr_out = outs.mean(axis=0) / outs.std(axis=0, ddof=1)
        best = int(np.argmax(sr_in))
        rank = (np.argsort(np.argsort(sr_out))[best] + 1) / (n + 1)
        logits.append(math.log(rank / (1.0 - rank)))
    return float(np.mean(np.array(logits) <= 0.0))


def spa_pvalue(
    losses: np.ndarray,
    benchmark: np.ndarray,
    rng: np.random.Generator,
    resamples: int = 1000,
    mean_block: float = 10.0,
) -> float:
    """Hansen (2005) SPA, consistent p-value: does any alternative beat the benchmark?

    `losses` is T x K for the alternatives, `benchmark` length T; performance is the benchmark's
    loss minus each alternative's, so a positive mean is an alternative doing better.
    """
    d = np.asarray(benchmark, dtype=float)[:, None] - np.asarray(losses, dtype=float)
    t, _ = d.shape
    mean = d.mean(axis=0)
    omega = np.sqrt(np.array([_hac_prewhitened(d[:, [k]])[0, 0] for k in range(d.shape[1])]))
    statistic = max(0.0, float(np.max(math.sqrt(t) * mean / omega)))
    threshold = mean * (mean >= -np.sqrt(omega**2 / t * 2.0 * math.log(math.log(t))))
    count = 0
    for _ in range(resamples):
        idx = stationary_bootstrap(t, mean_block, rng)
        # Hansen's recentring: resampled means less the thresholded sample mean, so a clearly
        # inferior alternative cannot inflate the null distribution.
        centred = d[idx].mean(axis=0) - threshold
        value = max(0.0, float(np.max(math.sqrt(t) * centred / omega)))
        count += value >= statistic
    return count / resamples


def held_pnl(
    book: Book,
    levels: Mapping[str, float],
    window: FitWindow,
    unit_gross_dv01: bool,
) -> np.ndarray:
    """Daily P&L per leg over `window`, each leg's exposure frozen at `levels` (T x legs).

    A book is held from its construction date: the exposure is computed once, at the levels of
    that date, and the window only supplies the moves.
    """
    exposures = []
    for leg in book.legs:
        e = leg_exposure(leg, levels)
        if unit_gross_dv01:
            scale = gross_dv01(leg, levels, DurationConvention.AS_QUOTED)
            e = {s: v / scale for s, v in e.items()}
        exposures.append(e)
    series = tuple(dict.fromkeys(s for e in exposures for s in e))
    _, changes, _ = daily_changes(series, window)
    matrix = np.array([[e.get(s, 0.0) for s in series] for e in exposures])
    return changes @ matrix.T
