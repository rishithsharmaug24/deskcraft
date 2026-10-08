"""The scenario engine's machinery. D12, registered in the joint pre-commit (DD134).

**Dated replay**: a book held into a dated window, its P&L computed from what happened, and the
window's own realised correlations reported as a statistic of the scenario (DD29 -- never fed back
into an estimator). **Filtered historical simulation**: per-series GARCH(1,1), hand-rolled and fitted
by Gaussian likelihood on a `FitWindow`, whose standardised residuals are resampled a whole day at
a time so the cross-section keeps its dependence. **The three-factor model** H7 is about: the first
three principal components of the fit window's covariance, Gaussian, whose cumulative P&L over h
days has a closed form -- the limit of its Monte Carlo, computed exactly rather than sampled.

The replay windows are fixed by rule (`REPLAY_WINDOWS`): the NBER recessions dated in the whole
record, and the 2022 calendar year the build order names. Nothing here reads a row after
`DEV_END`: an out-of-sample window is a date pair until the one commit DD102 reserves.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from statistics import NormalDist

import numpy as np
from scipy import optimize, signal

from deskcraft.covariance import CRISIS_WINDOWS
from deskcraft.window import FitWindow, OosWindow

__all__ = [
    "REPLAY_WINDOWS",
    "Garch",
    "ReplayWindow",
    "fhs_cumulative",
    "fit_garch",
    "garch_filter",
    "gross_change",
    "three_factor_quantile",
]

_NORMAL = NormalDist()


@dataclass(frozen=True)
class ReplayWindow:
    """A dated stress window and where its dates come from."""

    name: str
    window: FitWindow | OosWindow
    source: str


#: DEV's three from D8 (DD144), then the out-of-sample record's: the NBER recession of 2020
#: (peak February, trough April) and the calendar year 2022, which the build order names.
REPLAY_WINDOWS: tuple[ReplayWindow, ...] = (
    *(ReplayWindow(c.name, c.window, c.source) for c in CRISIS_WINDOWS),
    ReplayWindow(
        "NBER_2020",
        OosWindow(date(2020, 2, 1), date(2020, 4, 30)),
        "NBER Business Cycle Dating Committee, peak 2020-02, trough 2020-04",
    ),
    ReplayWindow(
        "RATES_2022",
        OosWindow(date(2022, 1, 1), date(2022, 12, 31)),
        "BUILD_ORDER_D3_D16.md section 4, D12 row: 'including 2020 and 2022'",
    ),
)


@dataclass(frozen=True, slots=True)
class Garch:
    """sigma2_t = omega + alpha x_{t-1}^2 + beta sigma2_{t-1}, zero mean."""

    omega: float
    alpha: float
    beta: float

    @property
    def persistence(self) -> float:
        return self.alpha + self.beta


def garch_filter(x: np.ndarray, model: Garch, start_variance: float | None = None) -> np.ndarray:
    """The conditional variance path, each value using only earlier observations."""
    first = float(np.var(x)) if start_variance is None else start_variance
    out = np.empty(x.size)
    out[0] = first
    if x.size > 1:
        # v_t = beta v_{t-1} + (omega + alpha x_{t-1}^2): a first-order linear filter, exactly.
        drive = model.omega + model.alpha * x[:-1] * x[:-1]
        out[1:] = signal.lfilter([1.0], [1.0, -model.beta], drive, zi=[model.beta * first])[0]
    return out


def fit_garch(x: np.ndarray) -> Garch:
    """Variance-targeted Gaussian likelihood: omega is pinned to the sample variance times
    (1 - alpha - beta), and alpha, beta are fitted with alpha + beta < 1 by the parameterisation.
    A two-step estimator, not full maximum likelihood over three parameters.
    """
    sample = float(np.var(x))

    def unpack(theta: np.ndarray) -> Garch:
        persistence = 1.0 / (1.0 + math.exp(-theta[0]))
        share = 1.0 / (1.0 + math.exp(-theta[1]))
        alpha, beta = persistence * share, persistence * (1.0 - share)
        return Garch(sample * (1.0 - persistence), alpha, beta)

    def negative_ll(theta: np.ndarray) -> float:
        variance = garch_filter(x, unpack(theta), sample)
        return float(0.5 * np.sum(np.log(variance) + x * x / variance))

    best = min(
        (optimize.minimize(negative_ll, np.array(s), method="Nelder-Mead",
                           options={"xatol": 1e-8, "fatol": 1e-10, "maxiter": 4000})
         for s in ((3.0, -2.0), (4.0, -2.5), (2.0, -1.0))),
        key=lambda r: r.fun,
    )
    return unpack(best.x)


def fhs_cumulative(
    changes: np.ndarray,
    models: tuple[Garch, ...],
    start_variance: np.ndarray,
    exposure: np.ndarray,
    horizon: int,
    rng: np.random.Generator,
    paths: int = 5000,
) -> np.ndarray:
    """Filtered historical simulation of a book's cumulative P&L over `horizon` days.

    `changes` is the fit window's T x k daily changes; each series is standardised by its own
    GARCH path, whole days of residual vectors are resampled, and each simulated day rescales them
    by the simulated variance and feeds the recursion.
    """
    k = changes.shape[1]
    residuals = np.empty_like(changes)
    for j in range(k):
        residuals[:, j] = changes[:, j] / np.sqrt(garch_filter(changes[:, j], models[j]))
    omega = np.array([m.omega for m in models])
    alpha = np.array([m.alpha for m in models])
    beta = np.array([m.beta for m in models])
    variance = np.tile(start_variance, (paths, 1))
    total = np.zeros(paths)
    for _ in range(horizon):
        draw = residuals[rng.integers(residuals.shape[0], size=paths)]
        move = draw * np.sqrt(variance)
        total += move @ exposure
        variance = omega + alpha * move * move + beta * variance
    return total


def three_factor_quantile(covariance: np.ndarray, exposure: np.ndarray, horizon: int, level: float) -> float:
    """The level-quantile of |cumulative P&L| under a Gaussian three-component model, exact."""
    values, vectors = np.linalg.eigh(covariance)
    order = np.argsort(values)[::-1][:3]
    reduced = vectors[:, order] @ np.diag(values[order]) @ vectors[:, order].T
    sigma = math.sqrt(float(exposure @ reduced @ exposure) * horizon)
    return _NORMAL.inv_cdf(0.5 + level / 2.0) * sigma


def gross_change(first: np.ndarray, second: np.ndarray) -> float:
    """sum |second - first| / sum |first|: how much of the book's gross a sizing moved."""
    a, b = np.asarray(first, dtype=float), np.asarray(second, dtype=float)
    return float(np.abs(b - a).sum() / np.abs(a).sum())
