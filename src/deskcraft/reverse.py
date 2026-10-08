"""D13: reverse stress, the smallest plausible move that breaches a stated loss.

`PRECOMMIT_deskcraft_d13_reverse_stress.md` fixes every rule here (DD220-DD224) before the run.

**The stated loss is the budget** (DD220). Each book is scaled so that its Gaussian ES at 97.5% on
the `SAMPLE` covariance is `sizing.RISK_BUDGET_ES`, and the loss asked about is that budget, lost
in one session.

**The closed form, and why on one covariance it is D9** (DD221). The move of least Mahalanobis
distance that loses L is Δ* = −L·Σe/(e′Σe), at distance L/√(e′Σe). The loss it puts on each series
is L·eᵢ(Σe)ᵢ/(e′Σe), which is D9's Euler share. So on the covariance the budget was set on, the
distance is φ(z)/(1 − α) for every book and the weak axis is the one D9 reports. What reverse
stress adds is the same breach on other covariances (DD222) and the breaches that happened (DD223).

Every covariance is fitted over D9's series set, the book's series and the view's. Every distance
and scenario is over the series the book holds, and the cosine is taken in `SAMPLE`'s metric.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from statistics import NormalDist

import numpy as np

from deskcraft import covariance as cv
from deskcraft.attribution import ALPHA, leg_exposure, levels_at
from deskcraft.book import Book
from deskcraft.factors import FACTOR_SERIES, FactorBasis, build_basis, fit_spectrum
from deskcraft.generator import select
from deskcraft.readers import REAL_AS_OF, REAL_FIT
from deskcraft.reference import US_CASH_BOOK
from deskcraft.sizing import RISK_BUDGET_ES
from deskcraft.views import REFERENCE_VIEW, View, compile_view
from deskcraft.window import FitWindow

__all__ = [
    "ES_SCALE",
    "LOSS",
    "VARIANTS",
    "Breach",
    "D13Result",
    "Exposed",
    "History",
    "exposed",
    "historical",
    "mahalanobis",
    "most_plausible",
    "run_d13",
    "sample_cosine",
    "the_two_books",
]

#: DD220: the loss asked about, in one session.
LOSS = RISK_BUDGET_ES
#: DD221: Gaussian ES over sigma at `ALPHA`, so the budget loss is this many `SAMPLE` sigmas.
_Z = NormalDist().inv_cdf(ALPHA)
ES_SCALE = math.exp(-0.5 * _Z * _Z) / math.sqrt(2.0 * math.pi) / (1.0 - ALPHA)
#: DD222: D8's variants on the fit window, `SAMPLE` first; the crisis windows follow them.
VARIANTS = ("SAMPLE", "LEDOIT_WOLF", "EWMA")


@dataclass(frozen=True)
class Exposed:
    """A book as D9 sees it, scaled to the budget (DD220)."""

    book_id: str
    #: D9's series set: the book's series, then those the view reaches.
    series: tuple[str, ...]
    #: The series the book holds; every distance and scenario is over these.
    held: tuple[str, ...]
    leg_ids: tuple[str, ...]
    #: Legs x series, USD per unit move, already scaled.
    matrix: np.ndarray
    #: The compiled view, unit length, over `series`.
    target: np.ndarray

    @property
    def exposure(self) -> np.ndarray:
        return self.matrix.sum(axis=0)

    def block(self) -> np.ndarray:
        """Indices of `held` within `series`."""
        return np.array([self.series.index(s) for s in self.held])


def exposed(book: Book, view: View, basis: FactorBasis, levels: Mapping[str, float], window: FitWindow) -> Exposed:
    """D9's setup (DD147, DD150), then the budget scaling on `SAMPLE` over `window` (DD220)."""
    rows = {leg.leg_id: leg_exposure(leg, levels) for leg in book.legs}
    compiled = compile_view(view, basis)
    reached = [s for s, v in zip(FACTOR_SERIES, compiled.vector) if v != 0.0]
    held = tuple(dict.fromkeys(s for row in rows.values() for s in row))
    series = tuple(dict.fromkeys([*held, *reached]))
    matrix = np.array([[rows[leg.leg_id].get(s, 0.0) for s in series] for leg in book.legs])
    lookup = dict(zip(FACTOR_SERIES, compiled.vector))
    t = np.array([lookup.get(s, 0.0) for s in series])
    sigma = cv.fit(series, window).array()
    total = matrix.sum(axis=0)
    scale = LOSS / (math.sqrt(float(total @ sigma @ total)) * ES_SCALE)
    return Exposed(book.book_id, series, held, book.leg_ids, matrix * scale, t / np.linalg.norm(t))


def most_plausible(e: np.ndarray, sigma: np.ndarray, loss: float = LOSS) -> tuple[np.ndarray, float]:
    """DD221: Δ* = −L·Σe/(e′Σe), and its distance L/√(e′Σe)."""
    gradient = sigma @ e
    variance = float(e @ gradient)
    return -loss * gradient / variance, loss / math.sqrt(variance)


def mahalanobis(delta: np.ndarray, sigma: np.ndarray) -> float:
    return math.sqrt(float(delta @ np.linalg.solve(sigma, delta)))


def sample_cosine(first: np.ndarray, second: np.ndarray, sigma: np.ndarray) -> float:
    """DD222: the cosine in `SAMPLE`'s metric, which no choice of unit can move."""
    inner = float(first @ np.linalg.solve(sigma, second))
    return inner / (mahalanobis(first, sigma) * mahalanobis(second, sigma))


@dataclass(frozen=True)
class Breach:
    """The most plausible budget breach on one covariance (DD221, DD222)."""

    covariance: str
    #: Why this covariance could not be fitted, or empty.
    refused: str
    #: The budget loss in this covariance's own sigmas.
    distance: float
    #: The same scenario's distance under `SAMPLE`: at least `ES_SCALE`.
    sample_distance: float
    #: Held series to the move, in each series' unit.
    scenario: dict[str, float]
    series_shares: dict[str, float]
    leg_shares: dict[str, float]
    on_thesis: float
    #: The cosine with the `SAMPLE` scenario, in `SAMPLE`'s metric. Not called `cosine`: that name
    #: is `ViewFidelity`'s statistic, and C111's census reads it (X3).
    alignment: float


def _refused(name: str, why: str) -> Breach:
    nan = math.nan
    return Breach(name, why, nan, nan, {}, {}, {}, nan, nan)


def _breach(book: Exposed, name: str, sigma: np.ndarray, sample: np.ndarray, sample_scenario: np.ndarray | None) -> Breach:
    held = book.block()
    e = book.exposure
    scenario, distance = most_plausible(e[held], sigma[np.ix_(held, held)])
    gradient = sigma @ e
    variance = float(e @ gradient)
    sample_block = sample[np.ix_(held, held)]
    return Breach(
        covariance=name,
        refused="",
        distance=distance,
        sample_distance=mahalanobis(scenario, sample_block),
        scenario=dict(zip(book.held, (float(v) for v in scenario))),
        series_shares={s: float(e[i] * gradient[i] / variance) for i, s in enumerate(book.series) if s in book.held},
        leg_shares={leg: float(row @ gradient / variance) for leg, row in zip(book.leg_ids, book.matrix)},
        on_thesis=float(e @ book.target) * float(book.target @ gradient) / variance,
        alignment=sample_cosine(scenario, scenario if sample_scenario is None else sample_scenario, sample_block),
    )


@dataclass(frozen=True)
class History:
    """DD223: the sessions of the fit window on which the scaled book lost at least L."""

    sessions: int
    breaches: int
    #: T·(1 − Φ(ES_SCALE)): how many a Gaussian model expects.
    expected: float
    #: The breach of least `SAMPLE` distance, its distance, and its move over the held series.
    nearest: date | None
    nearest_distance: float
    nearest_move: dict[str, float]


def historical(book: Exposed, window: FitWindow, sample: np.ndarray) -> History:
    days, changes, _ = cv.daily_changes(book.series, window)
    held = book.block()
    losses = -(changes @ book.exposure)
    hit = np.flatnonzero(losses >= LOSS)
    block = sample[np.ix_(held, held)]
    expected = changes.shape[0] * (1.0 - NormalDist().cdf(ES_SCALE))
    if not len(hit):
        return History(changes.shape[0], 0, expected, None, math.nan, {})
    distances = np.array([mahalanobis(changes[i, held], block) for i in hit])
    best = int(hit[int(np.argmin(distances))])
    return History(
        sessions=int(changes.shape[0]),
        breaches=int(len(hit)),
        expected=expected,
        nearest=days[best],
        nearest_distance=float(distances.min()),
        nearest_move={s: float(changes[best, j]) for s, j in zip(book.held, held)},
    )


@dataclass(frozen=True)
class D13Result:
    book: Exposed
    breaches: tuple[Breach, ...]
    history: History

    def on(self, name: str) -> Breach:
        return next(b for b in self.breaches if b.covariance == name)


def run_d13(book: Book, basis: FactorBasis, levels: Mapping[str, float], window: FitWindow = REAL_FIT) -> D13Result:
    """DD220-DD223 for one book: the closed form on every covariance its series reach, then history."""
    scaled = exposed(book, REFERENCE_VIEW, basis, levels, window)
    sample = cv.fit(scaled.series, window).array()
    breaches = [_breach(scaled, "SAMPLE", sample, sample, None)]
    sample_scenario = np.array([breaches[0].scenario[s] for s in scaled.held])
    candidates: list[tuple[str, object]] = [(name, cv.Method(name)) for name in VARIANTS[1:]]
    candidates += [(crisis.name, crisis) for crisis in cv.CRISIS_WINDOWS]
    for name, how in candidates:
        try:
            if isinstance(how, cv.CrisisWindow):
                sigma = cv.fit_crisis(scaled.series, how).array()
            else:
                sigma = cv.fit(scaled.series, window, how).array()
        except cv.UnfittableSeries as why:
            breaches.append(_refused(name, str(why)))
            continue
        breaches.append(_breach(scaled, name, sigma, sample, sample_scenario))
    return D13Result(scaled, tuple(breaches), historical(scaled, window, sample))


def the_two_books(window: FitWindow = REAL_FIT, as_of: date = REAL_AS_OF) -> tuple[FactorBasis, dict[str, float], tuple[Book, Book]]:
    """The joint registration §2's two books at the construction date, on the fit window's basis."""
    basis = build_basis(fit_spectrum(window))
    levels = levels_at(as_of)
    constructed = select(REFERENCE_VIEW, basis, levels, pool=tuple(levels)).book("constructed", "headline cell")
    return basis, levels, (US_CASH_BOOK, constructed)
