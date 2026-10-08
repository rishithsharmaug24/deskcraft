"""The covariance. D8, decisions DD130 and DD139-DD145, bars C130-C138.

**The sample covariance is primary** and is the same object D6 already used: over the eight
nominal zeros on DEV, `fit` returns exactly the matrix `factors._pca` computes (C130). Ledoit-Wolf,
EWMA and the crisis windows are robustness, reported beside the primary and never substituted
for it because they look better.

**Units are part of the result** (DD141). A yield or spread moves in basis points; `DEXUSEU`
moves in percent log-return. The two live in one matrix because `US_CASH_BOOK` holds both
(DD139), and a consumer multiplies by an exposure in the matching unit -- which is why
`Covariance.units` travels with the numbers instead of living in a docstring.

**One frequency per covariance** (DD130). A daily fit refuses a monthly series by name, and there
is no argument that forward-fills one onto the daily grid. `fit_monthly` is the companion: it
samples daily series down at month-end (DD145), which is lawful, and never samples up.

**Every series must be readable** (X22, DD136). The first package to read the panel by series is
the first that has to act on DD118's middle cell, so every estimator asks `Source.readable` and
refuses by name.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from enum import StrEnum

import numpy as np

from deskcraft.panel import (
    ADMITTED_SERIES,
    DAILY_SERIES,
    FX_SERIES,
    MONTHLY_SERIES,
    Panel,
    complete_cases,
    load_daily,
    load_daily_admitted,
    load_daily_fx,
    load_monthly,
)
from deskcraft.sources import SOURCES
from deskcraft.window import FitWindow

__all__ = [
    "CRISIS_WINDOWS",
    "EWMA_LAMBDA",
    "UNIT_OF",
    "Covariance",
    "CrisisWindow",
    "FrequencyRefused",
    "Frequency",
    "Method",
    "OrientationRow",
    "Unit",
    "UnfittableSeries",
    "changes",
    "daily_changes",
    "fit",
    "fit_crisis",
    "fit_monthly",
    "ledoit_wolf",
    "orientation_by_window",
]


class UnfittableSeries(ValueError):
    """A series D8 cannot fit: no unit, not readable, or not observed in the window."""


class FrequencyRefused(ValueError):
    """A monthly series asked into a daily covariance (DD130)."""


class Unit(StrEnum):
    """What one unit of a series' change is (DD141)."""

    #: 100 x the change in a published percent. Yields and spreads.
    BASIS_POINTS = "BASIS_POINTS"
    #: 100 x ln(S_t / S_t-1). An exchange rate.
    PERCENT_LOG_RETURN = "PERCENT_LOG_RETURN"


class Method(StrEnum):
    SAMPLE = "SAMPLE"
    LEDOIT_WOLF = "LEDOIT_WOLF"
    EWMA = "EWMA"


class Frequency(StrEnum):
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"


#: Measured, never defaulted: a series with no row is refused. `DEXUSEU` is the one that is not a
#: rate, and it is here because DD139 put it here; the H.10 majors joined it under DD168. A log
#: return is the one unit in which a rate quoted per dollar and its inverse differ only in sign.
UNIT_OF: dict[str, Unit] = {
    **{
        series: Unit.BASIS_POINTS
        for series in (*DAILY_SERIES, *ADMITTED_SERIES, *MONTHLY_SERIES)
        if series != "DEXUSEU"
    },
    "DEXUSEU": Unit.PERCENT_LOG_RETURN,
    **{series: Unit.PERCENT_LOG_RETURN for series in FX_SERIES},
}

#: RiskMetrics (1996) decay factors, zero mean (DD143). Constants, not tuned.
EWMA_LAMBDA: dict[Frequency, float] = {Frequency.DAILY: 0.94, Frequency.MONTHLY: 0.97}


@dataclass(frozen=True)
class CrisisWindow:
    """One NBER recession inside DEV, peak month start to trough month end (DD144)."""

    name: str
    window: FitWindow
    source: str


_NBER = "NBER Business Cycle Dating Committee, US business cycle expansions and contractions"

#: The three NBER recessions dated inside DEV. A published chronology with one answer, so no
#: window is chosen by what it shows.
CRISIS_WINDOWS: tuple[CrisisWindow, ...] = (
    CrisisWindow("NBER_1990", FitWindow(date(1990, 7, 1), date(1991, 3, 31)), _NBER),
    CrisisWindow("NBER_2001", FitWindow(date(2001, 3, 1), date(2001, 11, 30)), _NBER),
    CrisisWindow("NBER_2007", FitWindow(date(2007, 12, 1), date(2009, 6, 30)), _NBER),
)


@dataclass(frozen=True)
class Covariance:
    """A fitted covariance and everything needed to read it without guessing."""

    series: tuple[str, ...]
    units: tuple[Unit, ...]
    method: Method
    frequency: Frequency
    window: FitWindow
    #: Changes the estimate was computed from.
    observations: int
    #: Rows of the requested window lost to completeness across `series`, before differencing.
    dropped: int
    #: Ledoit-Wolf's intensity, or `None` for any other method.
    shrinkage: float | None
    matrix: tuple[tuple[float, ...], ...]

    def array(self) -> np.ndarray:
        return np.array(self.matrix, dtype=float)

    def volatility(self) -> tuple[float, ...]:
        return tuple(math.sqrt(self.matrix[i][i]) for i in range(len(self.series)))

    def correlation(self, first: str, second: str) -> float:
        i, j = self.series.index(first), self.series.index(second)
        return self.matrix[i][j] / math.sqrt(self.matrix[i][i] * self.matrix[j][j])


def _check_series(series: tuple[str, ...]) -> None:
    if not isinstance(series, tuple) or not series:
        raise TypeError("series must be a non-empty tuple of series names")
    if len(set(series)) != len(series):
        raise ValueError(f"a series is named twice: {series}")
    for name in series:
        if name not in UNIT_OF:
            raise UnfittableSeries(
                f"{name!r} has no unit row (DD141). It is refused rather than defaulted: a basis "
                "point and a percent differ by the level of the series, and a default would be "
                "a silent answer to that."
            )
        source = SOURCES.get(name)
        if source is None or not source.readable:
            raise UnfittableSeries(
                f"{name!r} is not readable (X22, DD118): its words do not let this repository "
                "compute on it, so no estimator here will."
            )


def _check_window(window: FitWindow) -> None:
    if not isinstance(window, FitWindow):
        raise TypeError(
            f"an estimator takes a FitWindow, not {type(window).__name__}. The type is what "
            "refuses a fit reaching past DEV_END; raw dates would skip that refusal."
        )


def _daily_panel(window: FitWindow, series: tuple[str, ...]) -> Panel:
    monthly = [name for name in series if name in MONTHLY_SERIES]
    if monthly:
        raise FrequencyRefused(
            f"{monthly} are monthly and this is a daily covariance (DD130). Forward-filling a "
            "monthly series onto the daily grid is refused by name: it would be unchanged on "
            "~95% of days, which DD122 refuses as a candidate. Use `fit_monthly`."
        )
    panel = load_daily(window)
    # Each further file is joined only when a series in it is asked for, so a caller registered
    # before a file existed reads exactly the bytes it read then (DD140, DD168).
    for wanted, loader, name in (
        (ADMITTED_SERIES, load_daily_admitted, "admitted"),
        (FX_SERIES, load_daily_fx, "fx"),
    ):
        if not any(s in wanted for s in series):
            continue
        extra = loader(window)
        if extra.dates != panel.dates:
            raise ValueError(f"the {name} panel is not on the rates panel's grid")
        panel = Panel(
            dates=panel.dates,
            series=panel.series + extra.series,
            values={**panel.values, **extra.values},
        )
    return panel


def changes(panel: Panel, series: tuple[str, ...]) -> tuple[tuple[date, ...], np.ndarray, int]:
    """Changes over consecutive complete rows, in each series' unit (DD141).

    Returns the end date of each change, the T x N matrix, and the rows completeness dropped.
    """
    kept, dropped = complete_cases(panel, series)
    levels = np.asarray(
        [[kept.column(name)[row] for name in series] for row in range(len(kept.dates))],
        dtype=float,
    ).reshape(len(kept.dates), len(series))
    out = np.empty((max(len(kept.dates) - 1, 0), len(series)))
    for k, name in enumerate(series):
        if UNIT_OF[name] is Unit.PERCENT_LOG_RETURN:
            out[:, k] = 100.0 * np.diff(np.log(levels[:, k]))
        else:
            out[:, k] = 100.0 * np.diff(levels[:, k])
    return kept.dates[1:], out, dropped


def ledoit_wolf(sample: np.ndarray) -> tuple[np.ndarray, float]:
    """Ledoit-Wolf (2004) shrinkage towards constant correlation, on standardised changes (DD142).

    `sample` is T x N. Demeaned, then each column divided by its 1/T standard deviation; the
    intensity and the shrunk correlation are computed there and rescaled back. Their loss is the
    Frobenius norm, which on raw mixed units lets the unit choose the intensity -- a basis point
    and a percent would disagree about how much to shrink the same data. Returns the shrunk
    matrix and the intensity, clipped to [0, 1].
    """
    t, n = sample.shape
    centred = sample - sample.mean(axis=0)
    scale = np.sqrt((centred**2).mean(axis=0))
    x = centred / scale
    s = x.T @ x / t
    sd = np.sqrt(np.diag(s))
    corr = s / np.outer(sd, sd)
    rbar = (corr.sum() - n) / (n * (n - 1))
    target = rbar * np.outer(sd, sd)
    np.fill_diagonal(target, np.diag(s))

    y = x**2
    pi_mat = y.T @ y / t - s**2
    pi_hat = pi_mat.sum()
    theta_ii = (x**3).T @ x / t - np.diag(s)[:, None] * s
    rho_off = 0.0
    for i in range(n):
        for j in range(n):
            if i != j:
                rho_off += (rbar / 2.0) * (
                    math.sqrt(s[j, j] / s[i, i]) * theta_ii[i, j]
                    + math.sqrt(s[i, i] / s[j, j]) * theta_ii[j, i]
                )
    rho_hat = float(np.trace(pi_mat)) + rho_off
    gamma_hat = float(((target - s) ** 2).sum())
    kappa = (pi_hat - rho_hat) / gamma_hat if gamma_hat > 0.0 else 0.0
    intensity = float(min(1.0, max(0.0, kappa / t)))
    shrunk = intensity * target + (1.0 - intensity) * s
    return shrunk * np.outer(scale, scale), intensity


def _ewma(sample: np.ndarray, decay: float) -> np.ndarray:
    """Zero-mean EWMA as of the last row, weights normalised over the finite sample (DD143)."""
    t = sample.shape[0]
    ages = np.arange(t - 1, -1, -1, dtype=float)
    weights = (1.0 - decay) * decay**ages
    weights /= weights.sum()
    return (sample * weights[:, None]).T @ sample


def _estimate(
    sample: np.ndarray, method: Method, frequency: Frequency
) -> tuple[np.ndarray, float | None]:
    if method is Method.SAMPLE:
        centred = sample - sample.mean(axis=0)
        return np.cov(centred, rowvar=False).reshape(sample.shape[1], sample.shape[1]), None
    if method is Method.LEDOIT_WOLF:
        return ledoit_wolf(sample)
    return _ewma(sample, EWMA_LAMBDA[frequency]), None


def _result(
    series: tuple[str, ...],
    method: Method,
    frequency: Frequency,
    window: FitWindow,
    sample: np.ndarray,
    dropped: int,
) -> Covariance:
    if sample.shape[0] <= len(series):
        raise UnfittableSeries(
            f"{series} have {sample.shape[0]} jointly observed changes in {window.start} -> "
            f"{window.end}, which cannot identify {len(series)} variances. Refused rather than "
            "shortened: a smaller series set is a different question."
        )
    matrix, shrinkage = _estimate(sample, method, frequency)
    return Covariance(
        series=series,
        units=tuple(UNIT_OF[name] for name in series),
        method=method,
        frequency=frequency,
        window=window,
        observations=int(sample.shape[0]),
        dropped=dropped,
        shrinkage=shrinkage,
        matrix=tuple(tuple(float(v) for v in row) for row in matrix),
    )


def daily_changes(
    series: tuple[str, ...], window: FitWindow | None = None
) -> tuple[tuple[date, ...], np.ndarray, int]:
    """The daily changes `fit` estimates from, checked the same way. D9 replays them."""
    fit_window = FitWindow.dev() if window is None else window
    _check_window(fit_window)
    _check_series(series)
    return changes(_daily_panel(fit_window, series), series)


def fit(
    series: tuple[str, ...], window: FitWindow | None = None, method: Method = Method.SAMPLE
) -> Covariance:
    """A daily covariance of `series` over `window` (DEV when omitted). Sample is primary."""
    fit_window = FitWindow.dev() if window is None else window
    _, sample, dropped = daily_changes(series, fit_window)
    return _result(series, Method(method), Frequency.DAILY, fit_window, sample, dropped)


def fit_crisis(series: tuple[str, ...], crisis: CrisisWindow) -> Covariance:
    """The sample covariance on one NBER window (DD144). Refuses a set the window cannot see."""
    if not isinstance(crisis, CrisisWindow):
        raise TypeError("fit_crisis takes one of CRISIS_WINDOWS")
    return fit(series, crisis.window, Method.SAMPLE)


def fit_monthly(
    series: tuple[str, ...], window: FitWindow | None = None, method: Method = Method.SAMPLE
) -> Covariance:
    """The monthly companion (DD130, DD145): daily series sampled down at month-end.

    A daily series takes its last observed session in each month, labelled with that month's
    start, which is the label `GZ_SPREAD` carries. Nothing is sampled up.
    """
    fit_window = FitWindow.dev() if window is None else window
    _check_window(fit_window)
    _check_series(series)
    daily_names = tuple(name for name in series if name not in MONTHLY_SERIES)
    monthly = load_monthly(fit_window)
    by_month: dict[date, dict[str, float | None]] = {
        stamp: {name: monthly.column(name)[k] for name in monthly.series}
        for k, stamp in enumerate(monthly.dates)
    }
    if daily_names:
        daily = _daily_panel(fit_window, daily_names)
        for name in daily_names:
            last: dict[date, float] = {}
            for stamp, value in zip(daily.dates, daily.column(name)):
                if value is not None:
                    last[date(stamp.year, stamp.month, 1)] = value
            for stamp, row in by_month.items():
                row[name] = last.get(stamp)
    months = tuple(sorted(by_month))
    panel = Panel(
        dates=months,
        series=series,
        values={name: tuple(by_month[m].get(name) for m in months) for name in series},
    )
    _, sample, dropped = changes(panel, series)
    return _result(series, Method(method), Frequency.MONTHLY, fit_window, sample, dropped)


@dataclass(frozen=True, slots=True)
class OrientationRow:
    """One fitted factor on one window: X6's measurement, window length beside the sign."""

    window: str
    sessions: int
    factor: str
    #: The orientation statistic on the sign-normalised eigenvector, before any flip.
    statistic: float
    #: +1 where curvecast's sign rule already points the stated way; -1 where it is flipped.
    sign: float
    #: Zero crossings across the tenor grid: 0 / 1 / 2 for a clean level / slope / curvature.
    crossings: int


def orientation_by_window() -> tuple[OrientationRow, ...]:
    """The three orientation statistics on DEV and on each crisis window (X6).

    The PCA is `factors.fit_spectrum`, curvecast's restated arithmetic, on each window's own
    complete nominal sample, so a flip here is a property of the sample and not of a second
    implementation.
    """
    from deskcraft.factors import fit_spectrum, orient, sign_changes

    windows = (("DEV", FitWindow.dev()), *((c.name, c.window) for c in CRISIS_WINDOWS))
    rows: list[OrientationRow] = []
    for name, window in windows:
        spectrum = fit_spectrum(window)
        for factor, orientation in orient(spectrum).items():
            rows.append(
                OrientationRow(
                    window=name,
                    sessions=spectrum.sessions,
                    factor=str(factor),
                    statistic=orientation.value,
                    sign=orientation.sign,
                    crossings=sign_changes(spectrum.loading(orientation.component)),
                )
            )
    return tuple(rows)
