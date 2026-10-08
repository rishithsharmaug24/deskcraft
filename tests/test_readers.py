"""C159-C164. The four registered readers: their machinery, the power check, and the DEV dry run.

`docs/PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md`. Nothing here reads a row after
`DEV_END`: the dry run fits on 1988-2003 and hands each reader 2004-2014 as its surface.
"""

from __future__ import annotations

import dataclasses
import math
import re
from datetime import date

import numpy as np
import pytest

from deskcraft import construction as c
from deskcraft import readers as r
from deskcraft import riskbacktest as rb
from deskcraft import scenarios as sc
from deskcraft.attribution import levels_at
from deskcraft.factors import build_basis, fit_spectrum
from deskcraft.generator import select
from deskcraft.registers import CLAIMS, Verdict
from deskcraft.views import REFERENCE_VIEW
from deskcraft.window import FitWindow

from test_deskcraft_boundary import REPO_ROOT, _read

FIT = FitWindow(date(1988, 1, 1), date(2003, 12, 31))
TEST = FitWindow(date(2004, 1, 1), date(2014, 12, 31))
AS_OF = date(2003, 12, 31)
REGISTRATION = REPO_ROOT / "docs" / "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md"


@pytest.fixture(scope="module")
def d14() -> r.D14Result:
    return r.run_d14(FIT, AS_OF, r.dev_surface(TEST))


@pytest.fixture(scope="module")
def d15(d14) -> r.D15Result:
    return r.run_d15(FIT, AS_OF, r.dev_surface(TEST), d14)


@pytest.fixture(scope="module")
def d12() -> tuple[r.D12Window, ...]:
    windows = tuple(w for w in sc.REPLAY_WINDOWS if isinstance(w.window, FitWindow))
    return r.run_d12(FIT, AS_OF, windows, lambda w: r.dev_surface(w.window))


def test_c159_a_construction_draws_only_on_series_that_existed() -> None:
    """C159. DD162. In 2003 `DFII30` did not exist; without the pool the generator cannot run."""
    basis = build_basis(fit_spectrum(FIT))
    levels = levels_at(AS_OF)
    assert "DFII30" not in levels
    with pytest.raises(KeyError, match="DFII30"):
        select(REFERENCE_VIEW, basis, levels)
    selection = select(REFERENCE_VIEW, basis, levels, pool=tuple(levels))
    assert selection.leg_ids == ("out_sveny30_short", "spr_sveny03_sveny30_short")


def test_c160_the_risk_backtest_statistics_answer_known_questions() -> None:
    """C160. D14's battery on inputs whose answer is known before the code runs."""
    hits = np.zeros(1000, dtype=bool)
    hits[:10] = True
    assert rb.kupiec(hits, 0.01) == pytest.approx(1.0)
    paired = np.zeros(1000, dtype=bool)
    paired[np.arange(0, 1000, 100)] = paired[np.arange(1, 1000, 100)] = True
    assert rb.christoffersen(paired, 0.02).independence_p < 0.001, "clustered exceptions"
    zone = [rb.traffic_light(np.r_[np.ones(k, bool), np.zeros(250 - k, bool)])[0] for k in (4, 5, 9, 10)]
    assert zone == ["GREEN", "YELLOW", "YELLOW", "RED"]
    power = {p: round(rb.kupiec_power(2870, 0.01, p), 3) for p in (0.015, 0.02, 0.03)}
    assert power == {0.015: 0.701, 0.02: 0.994, 0.03: 1.0}

    rng = np.random.default_rng(7)
    sigma = np.ones(3000)
    gaussian = rng.standard_normal(3000)
    fat = rng.standard_t(3, 3000) / math.sqrt(3.0)
    assert rb.acerbi_szekely(gaussian, sigma, 0.975, rng, 2000).z1_p > 0.01
    assert rb.acerbi_szekely(fat, sigma, 0.975, rng, 2000).z1_p < 0.01
    var, es = rb.gaussian_forecasts(sigma, 0.975)
    wrong_var, wrong_es = rb.gaussian_forecasts(2.0 * sigma, 0.975)
    assert rb.fz0_loss(gaussian, var, es, 0.975).mean() < rb.fz0_loss(gaussian, wrong_var, wrong_es, 0.975).mean()


def test_c161_the_scenario_engine_is_what_it_says() -> None:
    """C161. GARCH by filter and by likelihood, the three-factor quantile, and the dated windows."""
    rng = np.random.default_rng(5)
    true = sc.Garch(0.05, 0.08, 0.90)
    x = np.empty(6000)
    v = 1.0
    for t in range(x.size):
        x[t] = rng.standard_normal() * math.sqrt(v)
        v = true.omega + true.alpha * x[t] ** 2 + true.beta * v
    loop = np.empty(x.size)
    v = float(np.var(x))
    for t in range(x.size):
        loop[t] = v
        v = true.omega + true.alpha * x[t] ** 2 + true.beta * v
    assert np.allclose(sc.garch_filter(x, true), loop, rtol=1e-12)
    fitted = sc.fit_garch(x)
    assert abs(fitted.alpha - 0.08) < 0.02 and abs(fitted.beta - 0.90) < 0.03

    cov = np.array([[4.0, 1.0, 0.5, 0.1], [1.0, 3.0, 0.4, 0.2], [0.5, 0.4, 2.0, 0.3], [0.1, 0.2, 0.3, 1.0]])
    exposure = np.array([1.0, -0.5, 2.0, 1.0])
    values, vectors = np.linalg.eigh(cov)
    top = np.argsort(values)[::-1][:3]
    reduced = vectors[:, top] @ np.diag(values[top]) @ vectors[:, top].T
    draws = rng.multivariate_normal(np.zeros(4), reduced * 10, size=400_000) @ exposure
    assert sc.three_factor_quantile(cov, exposure, 10, 0.975) == pytest.approx(
        np.quantile(np.abs(draws), 0.975), rel=0.01
    )
    assert [(w.name, w.window.start, w.window.end) for w in sc.REPLAY_WINDOWS] == [
        ("NBER_1990", date(1990, 7, 1), date(1991, 3, 31)),
        ("NBER_2001", date(2001, 3, 1), date(2001, 11, 30)),
        ("NBER_2007", date(2007, 12, 1), date(2009, 6, 30)),
        ("NBER_2020", date(2020, 2, 1), date(2020, 4, 30)),
        ("RATES_2022", date(2022, 1, 1), date(2022, 12, 31)),
    ]
    assert sc.gross_change(np.array([1.0, 1.0]), np.array([1.5, 0.5])) == 0.5
    assert r.crisis_window_for(FitWindow.dev()).start == date(2007, 12, 1)


def test_c162_the_construction_statistics_answer_known_questions() -> None:
    """C162. D15's statistics: the Sharpe test's error, the bootstrap, PBO, DSR, SPA, power."""
    rng = np.random.default_rng(1)
    t = 2870
    z = rng.standard_normal((t, 2))
    z[:, 0] += 0.1
    test = c.sharpe_difference(z[:, 0], z[:, 1])
    assert test.standard_error == pytest.approx(math.sqrt((2 + 0.5 * 0.01) / t) * math.sqrt(252), rel=0.1)
    mde = c.minimum_detectable_difference(test.standard_error)
    assert c.power(mde, test.standard_error) == pytest.approx(0.8, abs=1e-3)

    idx = c.stationary_bootstrap(100_000, 10.0, rng)
    assert 9.0 < 100_000 / (int((np.diff(idx) != 1).sum()) + 1) < 11.0
    noise = rng.standard_normal((1600, 10))
    assert 0.25 < c.pbo_cscv(noise, blocks=8) < 0.75
    edge = noise.copy()
    edge[:, 3] += 0.15
    assert c.pbo_cscv(edge, blocks=8) < 0.05
    x = rng.standard_normal(2870) * 0.01 + 0.0005
    assert c.deflated_sharpe(x, 2, 1e-4) > c.deflated_sharpe(x, 1000, 1e-4)
    # SPA's size was measured at 5.5% over 200 null draws before this bar was written; a null case
    # therefore fails 5% of the time by construction, so the comparison is against a set that is
    # genuinely worse (losses half as large again as the benchmark's), not merely equal.
    bench = rng.standard_normal(1000) ** 2
    equal = rng.standard_normal((1000, 3)) ** 2
    better = equal.copy()
    better[:, 1] *= 0.5
    worse = 1.5 * equal
    assert c.spa_pvalue(better, bench, rng, 300) < 0.05 < c.spa_pvalue(worse, bench, rng, 300)


def test_c163_question_two_settled_by_the_power_check(d15) -> None:
    """C163. DD164. The registered power check, through the D15 runner, and the rule it fires.

    Power at the plausible effect is 8%, below the registered 0.5, so no fourth null is added.
    Read under `SAMPLE`, the primary descriptives.
    """
    primary = d15.primary
    assert primary.variant == "SAMPLE"
    assert round(primary.weight_distance, 4) == 0.0135
    assert round(primary.ex_ante_difference, 4) == 0.1921
    assert round(primary.view_ratio - 1.0, 4) == 0.0343
    assert round(d15.minimum_detectable["ONE_OVER_N"], 3) == 0.190
    assert round(primary.power_at_bound, 3) == 0.080 and primary.power_at_bound < 0.5
    assert set(d15.tests) == {"ONE_OVER_N", "SINGLE_INSTRUMENT", "HAND_BUILT"}, "three nulls, no fourth"
    assert "D15 gains no fourth null" in _read(REGISTRATION)


def test_c164_the_dev_dry_run_end_to_end(d14, d15, d12) -> None:
    """C164. The whole chain on DEV: D14's variants, the hand-off to D15, D12's windows.

    Every verdict function runs; its DEV answer is about the code, not the record.
    """
    sample = d14.coverage["SAMPLE"]
    assert d14.observations == 2747
    assert (sample[0.975].exceptions, sample[0.99].exceptions) == (35, 19)
    assert "CRISIS" in d14.refused, "the 2001 window cannot see TIPS; refused, never replaced"
    assert d14.first_ranked == "EWMA" and d15.secondary.variant == "EWMA"
    assert not r.h1_verdict(d14), "DD163: Kupiec at 97.5% rejects an over-conservative model"
    assert r.h2_verdict(d14)
    assert round(d14.kupiec_power[(0.975, 0.0375)], 3) == 0.964

    test = d15.tests["ONE_OVER_N"]
    assert d15.observations == 2747 and d15.legs == ("out_sveny30_short", "spr_sveny03_sveny30_short")
    assert round(test.difference, 4) == 0.0314 and not r.h5_verdict(d15)
    assert d15.primary.merged == {"EQUAL_RISK_CONTRIBUTION": "MAX_DIVERSIFICATION"}
    assert round(d15.secondary.view_ratio, 3) == 0.965

    by_name = {w.name: w for w in d12}
    assert [round(by_name[n].sizing_change, 4) for n in ("NBER_1990", "NBER_2001", "NBER_2007")] == [
        0.3501, 0.4598, 0.1069,
    ]
    assert not any(w.understated for w in d12)
    assert by_name["NBER_2007"].leg_signs == {"us_2y": -1, "us_10y": -1, "us_breakeven_5y": -1, "eurusd": 1}
    with pytest.raises(ValueError, match="were not replayed"):
        r.h6_verdict(d12)


def test_c165_the_real_construction_is_frozen_before_the_read() -> None:
    """C165. Every object the real run computes from DEV, pinned before the read.

    The read then only multiplies frozen objects by the surface (the independent review's finding 5).
    The fit window ends on the construction date, 2014-12-24 (its finding 10). H6 and H7's DEV windows
    are pinned here too, under the real construction: they run **against** both predictions, which
    is why DD167 reads the verdicts on the two out-of-sample windows and reports these beside them.
    """
    import math

    from deskcraft import covariance as cv
    from deskcraft import sizing as sz
    from deskcraft.factors import NOMINAL_SERIES
    from deskcraft.reference import US_CASH_BOOK

    assert r.REAL_FIT.end == r.REAL_AS_OF == date(2014, 12, 24)
    basis, levels, book = r._constructed(r.REAL_FIT, r.REAL_AS_OF)
    assert book.leg_ids == ("out_sveny30_short", "spr_sveny10_sveny30_short")
    legs = sz.leg_set(book, REFERENCE_VIEW, basis, sz.Unit.GROSS_DV01, levels, window=r.REAL_FIT)
    assert legs.pnl.shape == (6_730, 2)
    cvar, flat = sz.size(legs, sz.Rule.CVAR_LP), sz.size(legs, sz.Rule.ONE_OVER_N)
    assert tuple(round(x, 4) for x in cvar.weight_shares) == (0.4403, 0.5597)
    assert round(cvar.view_exposure / flat.view_exposure, 4) == 1.0398
    series, matrix = r._exposures(book, levels, sz.Unit.GROSS_DV01)
    exposure = matrix.T @ np.array(sz.size(legs, sz.Rule.MIN_VARIANCE).weights)
    assert {s: round(x, 1) for s, x in zip(series, exposure)} == {"SVENY30": 9960.6, "SVENY10": 63542.2}

    cash_series, cash_matrix = r._exposures(US_CASH_BOOK, levels, sz.Unit.STATED)
    total = cash_matrix.sum(axis=0)
    sigma = {
        v: round(math.sqrt(float(total @ r._variant_covariance(cash_series, r.REAL_FIT, v) @ total)), 1)
        for v in r.VARIANTS
    }
    assert sigma == {"SAMPLE": 832814.7, "LEDOIT_WOLF": 832181.9, "EWMA": 848781.3, "CRISIS": 1259782.9}

    _, fit_changes, _ = cv.daily_changes(series, r.REAL_FIT)
    garch = [sc.fit_garch(fit_changes[:, j]) for j in range(len(series))]
    assert [(round(m.alpha, 4), round(m.beta, 4)) for m in garch] == [(0.0484, 0.9386), (0.0322, 0.9602)]
    curve = cv.fit(NOMINAL_SERIES, r.REAL_FIT).array()
    curve_exposure = np.array([dict(zip(series, exposure)).get(s, 0.0) for s in NOMINAL_SERIES])
    assert round(sc.three_factor_quantile(curve, curve_exposure, 1, 0.975), 2) == 955061.31

    dev_windows = tuple(w for w in sc.REPLAY_WINDOWS if isinstance(w.window, FitWindow))
    real = r.run_d12(r.REAL_FIT, r.REAL_AS_OF, dev_windows, lambda w: r.dev_surface(w.window))
    assert [round(w.sizing_change, 4) for w in real] == [0.0071, 0.2144, 0.0402]
    assert not any(w.understated for w in real)


def test_c166_the_receiving_path_and_the_guards(d14, d15) -> None:
    """C166. X13's checks, the surface the read uses, H5's invariance, the date guard, dedup.

    The receiving checks run on a synthetic panel dated inside the out-of-sample window, built in
    memory from nothing: no row of the record exists or is read.
    """
    from deskcraft.panel import Panel
    from deskcraft.window import OosWindow

    whole = OosWindow.whole()
    days = []
    day = whole.start
    while day <= whole.end:
        if day.weekday() < 5:
            days.append(day)
        day = date.fromordinal(day.toordinal() + 1)
    names = (*r.cv.DAILY_SERIES, *r.cv.ADMITTED_SERIES, *r.cv.FX_SERIES)
    synthetic = Panel(tuple(days), names, {s: tuple(1.0 for _ in days) for s in names})
    assert r.receive_oos(synthetic) is synthetic
    gap = Panel(tuple(days[:10] + days[11:]), names, {s: tuple(1.0 for _ in days[1:]) for s in names})
    with pytest.raises(ValueError, match="weekday grid"):
        r.receive_oos(gap)
    short = Panel(tuple(days), names[:-1], {s: tuple(1.0 for _ in days) for s in names[:-1]})
    with pytest.raises(ValueError, match="lacks"):
        r.receive_oos(short)

    with pytest.raises(ValueError, match="inside the fit window"):
        r.run_d14(FIT, AS_OF, r.dev_surface(FitWindow(date(2003, 6, 1), date(2004, 6, 1))))

    # H5 is invariant to the covariance variant: a variant rescales a book, and Sharpe is scale-free.
    ewma = d15
    sample_d14 = r.D14Result(**{**d14.__dict__, "first_ranked": "SAMPLE"})
    sample = r.run_d15(FIT, AS_OF, r.dev_surface(TEST), sample_d14)
    for null in ewma.tests:
        assert ewma.tests[null].difference == pytest.approx(sample.tests[null].difference, rel=1e-12)
    assert r.h5_verdict(ewma) == r.h5_verdict(sample)


def test_c167_risk_per_view_measured_and_h18_not_registered(d15) -> None:
    """C167. DD169, DD170. The risk-per-view statistic, its power check, and the rule it fires.

    §5.4 fixed the plan before the check ran (`71ceee9`) and §5.5 records it. Power at the plausible
    effect is 0.334 on the DEV split and 0.404 on the real construction's books, both under the
    registered 0.5, so H18 is not registered and G stays §5.2's verdict-free separating statistic.

    **Mutation:** G is scale-free and paired. Multiplying one book and its view by seven leaves G
    and its bootstrap error unmoved to the bit on one seed; making a book's losses heavier with the
    same view drives G positive; two proportional books are one book and carry no power.
    """
    from deskcraft import sizing as sz
    from deskcraft.reference import US_CASH_BOOK
    from deskcraft.registers import CLAIMS

    rng = np.random.default_rng(3)
    x = rng.standard_normal(2000)
    y = 0.8 * x + 0.6 * rng.standard_normal(2000)
    base = c.risk_per_view(x, y, 1.0, 1.0, np.random.default_rng(5), resamples=400)
    scaled = c.risk_per_view(7.0 * x, y, 7.0, 1.0, np.random.default_rng(5), resamples=400)
    assert scaled.g == pytest.approx(base.g, abs=1e-12)
    assert scaled.standard_error == pytest.approx(base.standard_error, abs=1e-12)
    heavier = c.risk_per_view(x, np.where(y < 0, 1.5 * y, y), 1.0, 1.0, np.random.default_rng(5), resamples=400)
    assert heavier.g > 0.3 and heavier.p_value < 0.001
    one_book = c.risk_per_view(x, 2.0 * x, 1.0, 2.0, np.random.default_rng(5), resamples=50)
    assert one_book.g == pytest.approx(0.0, abs=1e-12) and one_book.power == 0.0

    # (a) The DEV split, through the runner the read uses.
    a = d15.risk_per_view
    assert round(a.plausible, 4) == 0.0337 and round(a.standard_error, 4) == 0.0221
    assert round(a.power, 3) == 0.334
    assert (round(a.g, 4), round(a.p_value, 4)) == (0.0433, 0.0497), "would have passed; not registered"

    # (b) The real construction's books, their dispersion over the last eleven years of DEV.
    basis, levels, headline = r._constructed(r.REAL_FIT, r.REAL_AS_OF)
    exposures = {
        "headline": r._exposures(headline, levels, sz.Unit.GROSS_DV01),
        "hand": r._exposures(US_CASH_BOOK, levels, sz.Unit.STATED),
    }
    union = tuple(dict.fromkeys(s for series, _ in exposures.values() for s in series))
    _, changes = r.dev_surface(FitWindow(date(2004, 1, 1), r.REAL_AS_OF))(union)
    series, matrix = exposures["headline"]
    held = changes[:, [union.index(s) for s in series]] @ matrix.T
    legs = sz.leg_set(headline, REFERENCE_VIEW, basis, sz.Unit.GROSS_DV01, levels, window=r.REAL_FIT)
    opt, flat = sz.size(legs, sz.Rule.CVAR_LP), sz.size(legs, sz.Rule.ONE_OVER_N)
    b = c.risk_per_view(
        held @ np.array(opt.weights),
        held @ np.array(flat.weights),
        opt.view_exposure,
        flat.view_exposure,
        np.random.default_rng(r.SEED),
        resamples=r.BOOTSTRAP_RESAMPLES,
        mean_block=r.BOOTSTRAP_BLOCK,
    )
    assert round(b.plausible, 4) == 0.0391 and round(b.power, 3) == 0.404

    # The rule, as §5.4 wrote it, and what it leaves.
    assert not (a.power >= 0.5 and b.power >= 0.5)
    assert "H18" not in {claim.claim_id for claim in CLAIMS}
    assert "H18 is not registered" in _read(REGISTRATION)


def test_c170_the_triggers_loader_is_written_and_names_no_file(tmp_path) -> None:
    """C170. DD102, DD173. What the trigger commit will call, exercised on files built from nothing.

    curvecast's `make_deskcraft_oos_panel.py` is prepared, rehearsed on DEV and refuses to run on the
    record without the owner's authorisation. This is its other half: `oos_panel` takes the three
    files' paths, so no module names an out-of-sample panel and C119 stays on its unauthorised
    branch. The files here are synthetic, dated inside the record, written under `tmp_path` and
    never under `tests/fixtures/`: no row of the record exists or is read.

    **Mutation:** one DEV row in the daily file is refused, not filtered, and a file missing a
    weekday fails `receive_oos`.
    """
    import csv as _csv

    from deskcraft.panel import ADMITTED_SERIES, DAILY_SERIES, FX_SERIES
    from deskcraft.window import OosWindow

    whole = OosWindow.whole()
    days, day = [], whole.start
    while day <= whole.end:
        if day.weekday() < 5:
            days.append(day.isoformat())
        day = date.fromordinal(day.toordinal() + 1)

    def write(name: str, columns: tuple[str, ...], stamps: list[str]):
        path = tmp_path / name
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = _csv.writer(handle, lineterminator="\n")
            writer.writerow(("Date", *columns))
            writer.writerows((stamp, *("1.0" for _ in columns)) for stamp in stamps)
        return path

    daily = write("d.csv", DAILY_SERIES, days)
    admitted = write("a.csv", ADMITTED_SERIES, days)
    fx = write("f.csv", FX_SERIES, days)
    panel = r.oos_panel(daily, admitted, fx)
    assert panel.series == (*DAILY_SERIES, *ADMITTED_SERIES, *FX_SERIES)
    assert len(panel.dates) == len(days)

    early = write("d_early.csv", DAILY_SERIES, ["2014-12-31", *days])
    with pytest.raises(ValueError, match="outside"):
        r.oos_panel(early, admitted, fx)
    short = [write(n, cols, days[:100] + days[101:]) for n, cols in
             (("d2.csv", DAILY_SERIES), ("a2.csv", ADMITTED_SERIES), ("f2.csv", FX_SERIES))]
    with pytest.raises(ValueError, match="weekday grid"):
        r.oos_panel(*short)

    source = (REPO_ROOT / "src" / "deskcraft" / "readers.py").read_text(encoding="utf-8")
    if not (REPO_ROOT / "docs" / "OWNER_AUTHORISATION_the_first_oos_read.md").exists():
        assert "_oos_" not in source and ".csv" not in source, "a module names an out-of-sample file"
    else:
        # DD102: the trigger commit added one line naming the record's three files, and no other.
        named = re.findall(r'"([\w.-]+\.csv)"', source)
        assert sorted(named) == sorted(path.name for path in r.RECORD_FILES) and len(named) == 3, named
        assert all(path.exists() for path in r.RECORD_FILES)


@pytest.fixture(scope="module")
def record_run():
    """The joint registration's §10 step 5, re-run: the three readers on the record, as on 2026-09-28."""
    record = r.oos_panel(*r.RECORD_FILES)
    surface = r.panel_surface(record)
    d14 = r.run_d14(r.REAL_FIT, r.REAL_AS_OF, surface)
    d15 = r.run_d15(r.REAL_FIT, r.REAL_AS_OF, surface, d14)
    windows = tuple(w for w in sc.REPLAY_WINDOWS if w.name in r.VERDICT_WINDOWS)
    d12 = r.run_d12(r.REAL_FIT, r.REAL_AS_OF, windows, lambda w: r.window_surface(record, w.window))
    return d14, d15, d12


def test_c220_the_reads_verdicts_are_the_registers(record_run) -> None:
    """C220. DD238. The out-of-sample read of 2026-09-28, re-run through the code that ran it.

    Every statistic is seeded (`SEED`), so the re-run reproduces the read to the bit. A difference
    here is a change to the code or the record after the read, and must not pass silently. The
    verdicts are held three ways at once: the scorers on the re-run, `CLAIMS`, and the lines of the
    registration's §13 that state them.

    **Mutation:** H6 and H7 each need both out-of-sample windows (DD167). With RATES_2022's sizing
    change raised past 20%, H6 passes; with NBER_2020 marked understated, H7 passes. One window was
    never enough, and on the record each held in exactly one.
    """
    d14, d15, d12 = record_run
    sample = d14.coverage["SAMPLE"]
    assert d14.observations == 2736 and d15.observations == 2736
    assert (sample[0.975].exceptions, sample[0.99].exceptions) == (58, 34)
    assert sample[0.975].kupiec_p == pytest.approx(0.19116, abs=5e-6)
    assert sample[0.99].kupiec_p == pytest.approx(0.21895, abs=5e-6)
    assert sample[0.975].independence_p == pytest.approx(0.0013225, abs=5e-8)
    assert d14.es_tests["SAMPLE"].z2_p == pytest.approx(0.5384, abs=1e-9)
    assert d14.first_ranked == "EWMA" and not d14.refused

    assert d15.legs == ("out_sveny30_short", "spr_sveny10_sveny30_short")
    test = d15.tests["ONE_OVER_N"]
    assert test.difference == pytest.approx(-0.012246, abs=5e-7)
    assert test.p_value == pytest.approx(0.82329, abs=5e-6)
    assert d15.risk_per_view.g == pytest.approx(0.068323, abs=5e-7)

    found = {w.name: w for w in d12}
    assert found["NBER_2020"].sizing_change == pytest.approx(0.657479, abs=5e-7)
    assert found["RATES_2022"].sizing_change == pytest.approx(0.027273, abs=5e-7)
    assert (found["NBER_2020"].understated, found["RATES_2022"].understated) == (False, True)
    assert found["NBER_2020"].leg_signs == {"us_2y": -1, "us_10y": -1, "us_breakeven_5y": -1, "eurusd": 1}
    assert found["RATES_2022"].leg_signs == {"us_2y": 1, "us_10y": 1, "us_breakeven_5y": -1, "eurusd": 1}

    verdicts = {
        "H1": r.h1_verdict(d14),
        "H2": r.h2_verdict(d14),
        "H5": r.h5_verdict(d15),
        "H6": r.h6_verdict(d12),
        "H7": r.h7_verdict(d12),
    }
    assert verdicts == {"H1": True, "H2": False, "H5": False, "H6": False, "H7": False}
    register = {claim.claim_id: claim.verdict for claim in CLAIMS}
    for claim_id, passed in verdicts.items():
        assert register[claim_id] is (Verdict.PASS if passed else Verdict.FAIL), claim_id
    assert register["SCENARIO_SIGNS"] is Verdict.REPORTED

    section = _read(REGISTRATION).split("## 13. The read, 2026-09-28")[1]
    for line in (
        "**H1 — PASS, as predicted.**",
        "**H2 — FAIL, as predicted.**",
        "**H5 — FAIL, as predicted, and by §5.2's grammar it says nothing.**",
        "**H6 — FAIL, against the prediction.**",
        "**H7 — FAIL, against the prediction.**",
        "**`SCENARIO_SIGNS` — reported.**",
        "**DD238 — a replay window of the record is its own sessions, differenced inside the window.**",
    ):
        assert line in section, line

    raised = tuple(dataclasses.replace(w, sizing_change=0.25) if w.name == "RATES_2022" else w for w in d12)
    assert r.h6_verdict(raised)
    flagged = tuple(dataclasses.replace(w, understated=True) if w.name == "NBER_2020" else w for w in d12)
    assert r.h7_verdict(flagged)
