"""The four registered readers, end to end. `PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md`.

Each reader takes a **fit window** inside DEV that ends on the **construction date**, where every
exposure is frozen, and a **surface**: a function returning daily changes for a series tuple over
the test period. The dry run hands it a DEV split through `dev_surface`. The real run hands it the
out-of-sample record through `panel_surface(receive_oos(panel))` -- the same path, so the dry run
exercises the code the read will run. The trigger commit DD102 reserves added only the fixtures
and the line that names them, `2acbd39`, after the owner's authorisation (DD133); the read ran
on 2026-09-28 and the registration's §13 records it.

D22 is not run from here. It needed D17, D18 and D21, and since 2026-09-28 its arithmetic and scorers
are `funding.py`, built to the registration's §6.1 and §11 and run by curvecast at its own read.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import numpy as np

from deskcraft import construction as c
from deskcraft import covariance as cv
from deskcraft import riskbacktest as rb
from deskcraft import scenarios as sc
from deskcraft import sizing as sz
from deskcraft.attribution import leg_exposure, levels_at
from deskcraft.book import Book
from deskcraft.costs import DurationConvention, gross_dv01
from deskcraft.factors import NOMINAL_SERIES, build_basis, fit_spectrum
from deskcraft.generator import candidate_legs, select
from deskcraft.panel import (
    ADMITTED_SERIES,
    DAILY_SERIES,
    FX_SERIES,
    Panel,
    load_daily,
    load_daily_admitted,
    load_record,
)
from deskcraft.reference import US_CASH_BOOK
from deskcraft.views import REFERENCE_VIEW
from deskcraft.window import DEV_START, FitWindow, OosWindow

__all__ = [
    "BOOTSTRAP_BLOCK",
    "BOOTSTRAP_RESAMPLES",
    "D15_TRIALS",
    "REAL_AS_OF",
    "REAL_FIT",
    "SEED",
    "VARIANTS",
    "VERDICT_WINDOWS",
    "D12Window",
    "D14Result",
    "D15Result",
    "Descriptives",
    "Surface",
    "crisis_window_for",
    "dev_surface",
    "oos_panel",
    "h1_verdict",
    "h2_verdict",
    "h5_verdict",
    "h6_verdict",
    "h7_verdict",
    "panel_surface",
    "receive_oos",
    "run_d12",
    "run_d14",
    "run_d15",
    "window_surface",
]

#: A surface: series -> (dates, T x k daily changes) over the test period.
Surface = Callable[[tuple[str, ...]], tuple[tuple[date, ...], np.ndarray]]

#: The real run's construction date and fit window. The fit window **ends on the construction
#: date**: a book constructed on 2014-12-24 is built from data through 2014-12-24, not through
#: DEV's last session (the independent review's finding 10).
REAL_AS_OF = date(2014, 12, 24)
REAL_FIT = FitWindow(DEV_START, REAL_AS_OF)

#: Politis-Romano mean block length for every bootstrap in D15: a trading month.
BOOTSTRAP_BLOCK = 21.0
BOOTSTRAP_RESAMPLES = 10_000

#: D15's Deflated Sharpe trial count, by rule: every leg evaluation D7b reported across its whole
#: ladder (7,830) plus the six sizing rules D11 offers. The largest count on the record.
D15_TRIALS = 7_830 + 6

#: One seed for every simulated or resampled statistic, so a re-run reproduces to the bit.
SEED = 20260925

#: D14's four covariance variants, each fitted on the fit window (D8).
VARIANTS = ("SAMPLE", "LEDOIT_WOLF", "EWMA", "CRISIS")

#: DD167: H6 and H7 are read on the out-of-sample windows only. The three DEV windows lie inside
#: every fitted object's sample, so their values were visible before the read; they are reported.
VERDICT_WINDOWS = ("NBER_2020", "RATES_2022")


# ---------------------------------------------------------------------------------------------
# Surfaces and the receiving side (X13)
# ---------------------------------------------------------------------------------------------


def panel_surface(panel: Panel) -> Surface:
    """A surface over a loaded panel. The real run and the dry run both come through here."""

    def surface(series: tuple[str, ...]) -> tuple[tuple[date, ...], np.ndarray]:
        cv._check_series(series)
        monthly = [name for name in series if name in cv.MONTHLY_SERIES]
        if monthly:
            raise cv.FrequencyRefused(f"{monthly} are monthly; a surface is daily (DD130)")
        dates, changes, _ = cv.changes(panel, series)
        return dates, changes

    return surface


def _merged(rates: Panel, credit: Panel) -> Panel:
    if rates.dates != credit.dates:
        raise ValueError("the admitted panel is not on the rates panel's grid")
    return Panel(rates.dates, rates.series + credit.series, {**rates.values, **credit.values})


def dev_surface(window: FitWindow) -> Surface:
    """A DEV test period as a surface: the dry run's stand-in for the out-of-sample record."""
    return panel_surface(_merged(load_daily(window), load_daily_admitted(window)))


def receive_oos(panel: Panel) -> Panel:
    """X13's receiving checks, run before any statistic touches the out-of-sample record.

    Every date lies inside `OosWindow.whole()`, and the dates are exactly the weekdays of that
    window: the GSW grid, holidays included as blank rows, with nothing missing and nothing extra.
    Every daily series of the register is present. Refusals for vintage are named by curvecast's
    generator at extraction, against the rule the registration fixes.
    """
    whole = OosWindow.whole()
    if not panel.dates or panel.dates[0] < whole.start or panel.dates[-1] > whole.end:
        raise ValueError("the out-of-sample panel reaches outside OosWindow.whole()")
    expected = []
    day = whole.start
    while day <= whole.end:
        if day.weekday() < 5:
            expected.append(day)
        day += timedelta(days=1)
    if tuple(expected) != panel.dates:
        missing = sorted(set(expected) - set(panel.dates))[:5]
        extra = sorted(set(panel.dates) - set(expected))[:5]
        raise ValueError(f"the grid is not GSW's weekday grid: missing {missing}, extra {extra}")
    # DD168: the H.10 majors ride the one extraction, so D22 never needs a second read.
    absent = [
        s for s in (*cv.DAILY_SERIES, *cv.ADMITTED_SERIES, *cv.FX_SERIES) if s not in panel.series
    ]
    if absent:
        raise ValueError(f"the out-of-sample panel lacks {absent}")
    return panel


def oos_panel(daily: Path, admitted: Path, fx: Path) -> Panel:
    """The record, from the three files the trigger commit lands, checked before anything reads it.

    Written before the read so the trigger commit adds only the fixtures and the one line that
    passes their paths here (DD102). The three are joined on one grid, as the DEV panels are, and
    handed to `receive_oos` before any statistic can see them.
    """
    parts = [
        load_record(daily, DAILY_SERIES),
        load_record(admitted, ADMITTED_SERIES),
        load_record(fx, FX_SERIES),
    ]
    if any(part.dates != parts[0].dates for part in parts[1:]):
        raise ValueError("the out-of-sample files are not on one grid")
    merged = Panel(
        parts[0].dates,
        tuple(s for part in parts for s in part.series),
        {s: v for part in parts for s, v in part.values.items()},
    )
    return receive_oos(merged)


def window_surface(panel: Panel, window: OosWindow) -> Surface:
    """DD238. A replay window of the record: its sessions, differenced inside the window.

    `dev_surface` hands D12 a DEV window by loading that window's rows and nothing else. The record
    arrives as one panel, so this is the same restriction: the first change is the window's second
    session less its first, never a change across the window's opening.
    """
    keep = [i for i, day in enumerate(panel.dates) if window.start <= day <= window.end]
    return panel_surface(
        Panel(
            tuple(panel.dates[i] for i in keep),
            panel.series,
            {s: tuple(panel.values[s][i] for i in keep) for s in panel.series},
        )
    )


#: DD102. The record's three files, extracted by curvecast 2026-09-28 under the owner's authorisation (DD133); DD37 fired.
RECORD_FILES = tuple(Path(__file__).resolve().parents[2] / "tests" / "fixtures" / name for name in ("panel_daily_oos_20260928.csv", "panel_daily_admitted_oos_20260928.csv", "panel_daily_fx_oos_20260928.csv"))


def _after(dates: tuple[date, ...], fit_window: FitWindow) -> None:
    """A surface must start after the fit window ends (the review's finding 13)."""
    if dates and dates[0] <= fit_window.end:
        raise ValueError(f"the surface starts {dates[0]}, inside the fit window ending {fit_window.end}")


# ---------------------------------------------------------------------------------------------
# Shared construction
# ---------------------------------------------------------------------------------------------


def crisis_window_for(fit_window: FitWindow) -> FitWindow:
    """The latest NBER window lying wholly inside the fit window: 2007-09 on the real run."""
    inside = [
        w.window
        for w in cv.CRISIS_WINDOWS
        if fit_window.start <= w.window.start and w.window.end <= fit_window.end
    ]
    if not inside:
        raise cv.UnfittableSeries(f"no NBER window lies inside {fit_window.start} -> {fit_window.end}")
    return inside[-1]


def _variant_covariance(series: tuple[str, ...], fit_window: FitWindow, variant: str) -> np.ndarray:
    if variant == "CRISIS":
        return cv.fit(series, crisis_window_for(fit_window)).array()
    return cv.fit(series, fit_window, cv.Method(variant)).array()


def _exposures(book: Book, levels: dict[str, float], unit: sz.Unit) -> tuple[tuple[str, ...], np.ndarray]:
    """Series held, and the legs x series exposure matrix at `unit` size (DD157)."""
    rows = []
    for leg in book.legs:
        e = leg_exposure(leg, levels)
        if unit is sz.Unit.GROSS_DV01:
            scale = gross_dv01(leg, levels, DurationConvention.AS_QUOTED)
            e = {s: v / scale for s, v in e.items()}
        rows.append(e)
    series = tuple(dict.fromkeys(s for e in rows for s in e))
    return series, np.array([[e.get(s, 0.0) for s in series] for e in rows])


def _constructed(fit_window: FitWindow, as_of: date):
    """The basis refitted on the fit window, the levels of the construction date, the headline book."""
    if as_of != fit_window.end:
        raise ValueError(f"construction on {as_of} with a fit window ending {fit_window.end}")
    basis = build_basis(fit_spectrum(fit_window))
    levels = levels_at(as_of)
    book = select(REFERENCE_VIEW, basis, levels, pool=tuple(levels)).book("constructed", "headline cell")
    return basis, levels, book


# ---------------------------------------------------------------------------------------------
# D14
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class D14Result:
    observations: int
    #: variant -> level -> Coverage
    coverage: dict[str, dict[float, rb.Coverage]]
    traffic_light: dict[str, tuple[str, ...]]
    es_tests: dict[str, rb.EsTest]
    fz0: dict[str, float]
    #: variant -> (mean FZ0 of the variant minus SAMPLE's, two-sided Diebold-Mariano p-value)
    against_primary: dict[str, tuple[float, float]]
    #: DD135's rule, evaluated on the record: the variant D15's *secondary* descriptives use.
    first_ranked: str
    #: Kupiec's power against 1.5% / 2% / 3% at 99%, and 3.75% / 5% / 7.5% at 97.5%.
    kupiec_power: dict[tuple[float, float], float]
    refused: dict[str, str]


def run_d14(fit_window: FitWindow, as_of: date, surface: Surface) -> D14Result:
    """`US_CASH_BOOK` held from `as_of`, four variants fitted on `fit_window`, the full battery."""
    levels = levels_at(as_of)
    series, matrix = _exposures(US_CASH_BOOK, levels, sz.Unit.STATED)
    total = matrix.sum(axis=0)
    dates, changes = surface(series)
    _after(dates, fit_window)
    pnl = changes @ total
    rng = np.random.default_rng(SEED)

    def flat(cov: np.ndarray) -> np.ndarray:
        return np.full(pnl.size, math.sqrt(float(total @ cov @ total)))

    ewma_start = float(total @ _variant_covariance(series, fit_window, "EWMA") @ total)
    sigmas = {
        "SAMPLE": flat(_variant_covariance(series, fit_window, "SAMPLE")),
        "LEDOIT_WOLF": flat(_variant_covariance(series, fit_window, "LEDOIT_WOLF")),
        "EWMA": rb.ewma_sigma(pnl, ewma_start, cv.EWMA_LAMBDA[cv.Frequency.DAILY]),
    }
    refused: dict[str, str] = {}
    try:
        sigmas["CRISIS"] = flat(_variant_covariance(series, fit_window, "CRISIS"))
    except cv.UnfittableSeries as error:
        refused["CRISIS"] = str(error)
    coverage: dict[str, dict[float, rb.Coverage]] = {}
    lights, es_tests, fz0, losses = {}, {}, {}, {}
    for name, sigma in sigmas.items():
        coverage[name] = {}
        for level in (0.975, 0.99):
            var, _ = rb.gaussian_forecasts(sigma, level)
            coverage[name][level] = rb.christoffersen(pnl < -var, 1.0 - level)
        var99, _ = rb.gaussian_forecasts(sigma, 0.99)
        lights[name] = rb.traffic_light(pnl < -var99)
        es_tests[name] = rb.acerbi_szekely(pnl, sigma, 0.975, rng)
        var, es = rb.gaussian_forecasts(sigma, 0.975)
        losses[name] = rb.fz0_loss(pnl, var, es, 0.975)
        fz0[name] = float(losses[name].mean())
    against = {n: rb.diebold_mariano(losses[n], losses["SAMPLE"]) for n in sigmas if n != "SAMPLE"}
    # DD135's rule: lowest mean FZ0 among variants with a negative difference and a two-sided DM
    # p-value below 5% (one-sided 2.5%); if none, the primary.
    beaters = [n for n, (d, p) in against.items() if d < 0.0 and p < 0.05]
    n = int(pnl.size)
    return D14Result(
        observations=n,
        coverage=coverage,
        traffic_light=lights,
        es_tests=es_tests,
        fz0=fz0,
        against_primary=against,
        first_ranked=min(beaters, key=lambda v: fz0[v]) if beaters else "SAMPLE",
        kupiec_power={
            (level, p): rb.kupiec_power(n, 1.0 - level, p)
            for level, rates in ((0.99, (0.015, 0.02, 0.03)), (0.975, (0.0375, 0.05, 0.075)))
            for p in rates
        },
        refused=refused,
    )


def h1_verdict(result: D14Result) -> bool:
    """H1, DD163: Kupiec p >= 0.05 at 97.5% and at 99%, and Acerbi-Szekely Z2 p >= 0.05."""
    sample = result.coverage["SAMPLE"]
    return (
        sample[0.975].kupiec_p >= 0.05
        and sample[0.99].kupiec_p >= 0.05
        and result.es_tests["SAMPLE"].z2_p >= 0.05
    )


def h2_verdict(result: D14Result) -> bool:
    """H2: Christoffersen's independence test at 97.5% on the primary has p >= 0.05."""
    return result.coverage["SAMPLE"][0.975].independence_p >= 0.05


# ---------------------------------------------------------------------------------------------
# D15
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Descriptives:
    """D15's separating and ensemble statistics under one covariance variant."""

    variant: str
    weight_distance: float
    ex_ante_difference: float
    view_ratio: float
    power_at_bound: float
    rules_sharpe: dict[str, float]
    #: Rules whose books duplicate an earlier rule's, merged before PBO and SPA (the review's 9).
    merged: dict[str, str]
    pbo: float
    spa_p: float


@dataclass(frozen=True)
class D15Result:
    legs: tuple[str, ...]
    observations: int
    sharpe: dict[str, float]
    tests: dict[str, c.SharpeDifference]
    intervals: dict[str, tuple[float, float]]
    minimum_detectable: dict[str, float]
    deflated_sharpe: float
    #: DD169: the ES-constrained book's view per unit of realised ES against 1/N's. Scale-free,
    #: so invariant to the covariance variant, as H5 is. Its own seeded bootstrap, so adding it
    #: moved no other statistic.
    risk_per_view: c.RiskPerView
    #: Under `SAMPLE`, the primary.
    primary: Descriptives
    #: Under D14's first-ranked variant, labelled: it was selected on the record itself.
    secondary: Descriptives


def run_d15(fit_window: FitWindow, as_of: date, surface: Surface, d14: D14Result) -> D15Result:
    """The construction backtest: build on `fit_window`, hold through the surface, test H5.

    H5 and the three null tests are invariant to the covariance variant, because a variant only
    rescales a book and a Sharpe ratio is scale-free. The descriptives that are not invariant are
    reported under `SAMPLE` as primary and under D14's first-ranked variant as secondary.
    """
    basis, levels, headline = _constructed(fit_window, as_of)
    unit = sz.Unit.GROSS_DV01
    single_book = headline.restricted_to("single", headline.leg_ids[:1])

    exposures = {
        "headline": _exposures(headline, levels, unit),
        "single": _exposures(single_book, levels, unit),
        "hand": _exposures(US_CASH_BOOK, levels, sz.Unit.STATED),
    }
    union = tuple(dict.fromkeys(s for series, _ in exposures.values() for s in series))
    dates, changes = surface(union)
    _after(dates, fit_window)
    # One complete-case sample over every series any book holds, differenced once: every book's
    # P&L is then over the same intervals, not merely the same end-dates (the review's finding 8).
    column = {s: k for k, s in enumerate(union)}

    def held(which: str, weights: tuple[float, ...]) -> np.ndarray:
        series, matrix = exposures[which]
        return changes[:, [column[s] for s in series]] @ matrix.T @ np.array(weights)

    def leg_set(book: Book, u: sz.Unit, which: str, variant: str) -> sz.LegSet:
        legs = sz.leg_set(book, REFERENCE_VIEW, basis, u, levels, window=fit_window)
        series, matrix = exposures[which]
        cov = _variant_covariance(series, fit_window, variant)
        return sz.LegSet(legs.book_id, legs.leg_ids, legs.unit, legs.view, legs.pnl, matrix @ cov @ matrix.T)

    def descriptives(variant: str) -> tuple[Descriptives, dict[str, sz.SizedBook]]:
        legs = leg_set(headline, unit, "headline", variant)
        rules = {rule: sz.size(legs, rule) for rule in sz.Rule}
        opt, flat = rules[sz.Rule.CVAR_LP], rules[sz.Rule.ONE_OVER_N]
        by_rule = {rule.name: held("headline", book.weights) for rule, book in rules.items()}
        kept, merged = [], {}
        for rule in sz.Rule:
            shares = np.array(rules[rule].weight_shares)
            twin = next((k for k in kept if np.abs(np.array(rules[sz.Rule[k]].weight_shares) - shares).max() < 1e-6), None)
            if twin is None:
                kept.append(rule.name)
            else:
                merged[rule.name] = twin
        rng = np.random.default_rng(SEED)
        ratio = opt.view_exposure / flat.view_exposure
        se = c.sharpe_difference(by_rule["CVAR_LP"], by_rule["ONE_OVER_N"]).standard_error
        alternatives = [k for k in kept if k != "ONE_OVER_N"]
        return (
            Descriptives(
                variant=variant,
                weight_distance=0.5 * sum(abs(a - b) for a, b in zip(opt.weight_shares, flat.weight_shares)),
                ex_ante_difference=sz.tracking_error(opt, flat, legs),
                view_ratio=ratio,
                power_at_bound=c.power(ratio - 1.0, se),
                rules_sharpe={k: c.sharpe(v) for k, v in by_rule.items()},
                merged=merged,
                pbo=c.pbo_cscv(np.column_stack([by_rule[k] for k in kept]), blocks=16),
                spa_p=c.spa_pvalue(
                    np.column_stack([-by_rule[k] for k in alternatives]),
                    -by_rule["ONE_OVER_N"],
                    rng,
                    resamples=2000,
                    mean_block=BOOTSTRAP_BLOCK,
                ),
            ),
            rules,
        )

    primary, rules = descriptives("SAMPLE")
    secondary, _ = descriptives(d14.first_ranked)
    single = sz.size(leg_set(single_book, unit, "single", "SAMPLE"), sz.Rule.ONE_OVER_N)
    hand = sz.size(leg_set(US_CASH_BOOK, sz.Unit.STATED, "hand", "SAMPLE"), sz.Rule.ONE_OVER_N)
    books = {
        "ES_CONSTRAINED": held("headline", rules[sz.Rule.CVAR_LP].weights),
        "ONE_OVER_N": held("headline", rules[sz.Rule.ONE_OVER_N].weights),
        "SINGLE_INSTRUMENT": held("single", single.weights),
        "HAND_BUILT": held("hand", hand.weights),
    }
    n = changes.shape[0]
    rng = np.random.default_rng(SEED)
    tests, intervals, detectable = {}, {}, {}
    opt = books["ES_CONSTRAINED"]
    for null in ("ONE_OVER_N", "SINGLE_INSTRUMENT", "HAND_BUILT"):
        other = books[null]
        tests[null] = c.sharpe_difference(opt, other)
        detectable[null] = c.minimum_detectable_difference(tests[null].standard_error)
        draws = np.empty(BOOTSTRAP_RESAMPLES)
        for b in range(BOOTSTRAP_RESAMPLES):
            idx = c.stationary_bootstrap(n, BOOTSTRAP_BLOCK, rng)
            draws[b] = c.sharpe(opt[idx]) - c.sharpe(other[idx])
        intervals[null] = (float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975)))

    # The Deflated Sharpe is the ES-constrained book's. Its trial variance, by rule: every
    # candidate leg the pool allows, held alone over the fit window, in daily units.
    pool = tuple(levels)
    fit_sharpes = []
    for leg in candidate_legs():
        if not all(s in pool for s in leg.instrument.series):
            continue
        e = leg_exposure(leg, levels)
        series = tuple(e)
        _, fit_changes, _ = cv.daily_changes(series, fit_window)
        fit_sharpes.append(c.sharpe(fit_changes @ np.array([e[s] for s in series])) / math.sqrt(c.TRADING_DAYS))

    return D15Result(
        legs=headline.leg_ids,
        observations=n,
        sharpe={k: c.sharpe(v) for k, v in books.items()},
        tests=tests,
        intervals=intervals,
        minimum_detectable=detectable,
        deflated_sharpe=c.deflated_sharpe(opt, D15_TRIALS, float(np.var(fit_sharpes, ddof=1))),
        risk_per_view=c.risk_per_view(
            opt,
            books["ONE_OVER_N"],
            rules[sz.Rule.CVAR_LP].view_exposure,
            rules[sz.Rule.ONE_OVER_N].view_exposure,
            np.random.default_rng(SEED),
            resamples=BOOTSTRAP_RESAMPLES,
            mean_block=BOOTSTRAP_BLOCK,
        ),
        primary=primary,
        secondary=secondary,
    )


def h5_verdict(result: D15Result) -> bool:
    """H5: the ES-constrained book beats 1/N on Sharpe, difference positive at p < 0.05."""
    test = result.tests["ONE_OVER_N"]
    return test.difference > 0.0 and test.p_value < 0.05


# ---------------------------------------------------------------------------------------------
# D12
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class D12Window:
    name: str
    days: int
    #: A window that could not be computed, and why; it then counts as not above either bar.
    refused: str | None
    realised: float
    #: 97.5% quantile of |cumulative P&L| under the three-factor model of the eight-zero curve.
    three_factor: float
    fhs: float
    understated: bool
    sizing_change: float
    leg_signs: dict[str, int]


def run_d12(
    fit_window: FitWindow,
    as_of: date,
    windows: tuple[sc.ReplayWindow, ...],
    surface_of: Callable[[sc.ReplayWindow], Surface],
) -> tuple[D12Window, ...]:
    """Dated replay of the constructed book through each window, with H6's and H7's statistics.

    The three-factor model is the first three principal components of DEV's covariance of the
    **whole eight-zero curve**, Gaussian, cumulated over the window (the review's finding 4: on the
    book's own two series a three-component truncation is no truncation at all). The FHS start
    state is GARCH's unconditional variance (DD165).
    """
    basis, levels, book = _constructed(fit_window, as_of)
    unit_legs = sz.leg_set(book, REFERENCE_VIEW, basis, sz.Unit.GROSS_DV01, levels, window=fit_window)
    weights = np.array(sz.size(unit_legs, sz.Rule.MIN_VARIANCE).weights)
    series, matrix = _exposures(book, levels, sz.Unit.GROSS_DV01)
    outside = [s for s in series if s not in NOMINAL_SERIES]
    if outside:
        raise ValueError(f"the replayed book holds {outside}, off the curve the three-factor model spans")
    exposure = matrix.T @ weights
    curve_exposure = np.array([dict(zip(series, exposure)).get(s, 0.0) for s in NOMINAL_SERIES])
    curve_cov = cv.fit(NOMINAL_SERIES, fit_window).array()
    _, fit_changes, _ = cv.daily_changes(series, fit_window)
    models = tuple(sc.fit_garch(fit_changes[:, j]) for j in range(len(series)))
    start = np.array([m.omega / (1.0 - m.persistence) for m in models])
    dev_sd = np.sqrt(np.diag(unit_legs.covariance))
    cash_series, cash_matrix = _exposures(US_CASH_BOOK, levels, sz.Unit.STATED)
    rng = np.random.default_rng(SEED)

    out = []
    for window in windows:
        surface = surface_of(window)
        _, changes = surface(series)
        days = changes.shape[0]
        if days < 3:
            out.append(D12Window(window.name, days, f"{days} changes in the window", 0.0, 0.0, 0.0, False, 0.0, {}))
            continue
        realised = float((changes @ exposure).sum())
        simulated = sc.fhs_cumulative(fit_changes, models, start, exposure, days, rng, paths=5000)
        three = sc.three_factor_quantile(curve_cov, curve_exposure, days, 0.975)
        corr = np.corrcoef(changes @ matrix.T, rowvar=False)
        try:
            crisis = sz.LegSet(unit_legs.book_id, unit_legs.leg_ids, unit_legs.unit, unit_legs.view,
                               unit_legs.pnl, corr * np.outer(dev_sd, dev_sd))
            change = sc.gross_change(sz.weights(unit_legs, sz.Rule.MIN_VARIANCE),
                                     sz.weights(crisis, sz.Rule.MIN_VARIANCE))
            refused = None
        except ValueError as error:
            change, refused = 0.0, f"sizing under the window's correlations failed: {error}"
        _, cash_changes = surface(cash_series)
        signs = (
            {leg: int(np.sign((cash_changes @ row).sum())) for leg, row in zip(US_CASH_BOOK.leg_ids, cash_matrix)}
            if cash_changes.shape[0] > 0
            else {}
        )
        out.append(
            D12Window(window.name, days, refused, realised, three,
                      float(np.quantile(np.abs(simulated), 0.975)), abs(realised) > three, change, signs)
        )
    return tuple(out)


def _scored(windows: tuple[D12Window, ...]) -> list[D12Window]:
    found = {w.name: w for w in windows}
    missing = [name for name in VERDICT_WINDOWS if name not in found]
    if missing:
        raise ValueError(f"H6 and H7 are read on {VERDICT_WINDOWS}; {missing} were not replayed")
    return [found[name] for name in VERDICT_WINDOWS]


def h6_verdict(windows: tuple[D12Window, ...]) -> bool:
    """H6, DD167: sizing moves more than 20% of gross in both out-of-sample windows."""
    return all(w.refused is None and w.sizing_change > 0.20 for w in _scored(windows))


def h7_verdict(windows: tuple[D12Window, ...]) -> bool:
    """H7, DD167: the three-factor model understates the realised magnitude in both windows."""
    return all(w.refused is None and w.understated for w in _scored(windows))
