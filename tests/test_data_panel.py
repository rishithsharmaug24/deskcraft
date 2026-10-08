"""D3b's bars: the panel is on the grid it claims, carries only what it may, and knew nothing early.

This is the first suite in this repository that reads numbers. Everything before it guarded an
empty room, so these seven bars are the first exercise of guards D1 through D5 wrote against
data that did not exist yet.

Three of them re-derive their subject from curvecast at test time rather than trusting the
committed file -- `C42` the session grid, `C44` the vintage collapse -- for the reason
`graded_universe()` gives upstream: a hardcoded copy goes stale silently, and a fixture that
has drifted from the source it came from should fail at gate time rather than quietly become
the source of truth. They **skip loudly** when curvecast is absent, because a bar that needs a
sibling repository is not a bar on a machine without one.

`C43` and `C47` are a pair. The check is `panel.refuse_uncommittable`, called by the loader at
run time and by the bar over the committed bytes, so the guard the test exercises is the guard
that runs; `C47` mutates that one function rather than a plausible-looking copy of it.
"""

from __future__ import annotations

import csv
import re
from datetime import date, datetime

import pytest

from deskcraft.generator import CANDIDATE_SERIES
from deskcraft.panel import (
    DAILY_FIXTURE,
    DAILY_SERIES,
    MONTHLY_FIXTURE,
    MONTHLY_SERIES,
    UncommittableSeries,
    complete_cases,
    load_daily,
    load_monthly,
    refuse_uncommittable,
)
from deskcraft.sources import SOURCES, Licence
from deskcraft.window import DEV_END, DEV_START, FitWindow

from test_deskcraft_boundary import CURVECAST, REPO_ROOT, _read
from upstream_certificate import SESSION_GRID, VINTAGE_COLLAPSE, digest

#: `AMENDMENT_A7` §0 rows 1 and 3, and the window every admission test has run on since DD122.
#: `DFII30` opens 2010-02-22, and clause 2's projection needs every basis series on the same row,
#: so the eleven-series pool is jointly observed on 17.3% of a twenty-seven-year panel.
EXPECTED_JOINT_POOL_ROWS = 1_217

AMENDMENT_A7 = REPO_ROOT / "docs" / "AMENDMENT_A7_the_admission_test_ran.md"

_PANEL_ROW = re.compile(r"Rows in the DEV daily panel \|\s*\*\*([\d,]+)\*\*")
_JOINT_ROW = re.compile(
    r"\*\*eleven\*\* of `CANDIDATE_SERIES` are jointly observed \|\s*\*\*([\d,]+)\*\*"
)


def _stated(pattern: re.Pattern[str], text: str, label: str) -> int:
    """The one figure `AMENDMENT_A7` §0 states for `label`. Two statements of a number disagree."""
    found = pattern.findall(text)
    assert len(found) == 1, f"{label}: {len(found)} matches in `AMENDMENT_A7` §0, expected one"
    return int(found[0].replace(",", ""))


#: Measured 2026-09-14 by curvecast's `scripts/make_deskcraft_panel.py` and predicted in
#: `PRECOMMIT_deskcraft_d3b_data_panel.md` section 0.5 before the generator was written.
EXPECTED_SESSIONS = 7_044
EXPECTED_GSW_BLANK = 309
EXPECTED_MONTHLY = 323
EXPECTED_COVERAGE = {
    "DGS3MO": 6_504,
    "DGS6MO": 6_504,
    "DGS1": 6_504,
    "DGS2": 6_504,
    "DGS10": 6_504,
    "DFII5": 3_002,
    "DFII10": 3_002,
    "DFII30": 1_217,
    "DEXUSEU": 4_019,
}

#: The five observations whose only vintage falls after DEV_END -- the 2014-12-31 closes,
#: published 2015-01-05. Named rather than counted: "five rows were dropped" and "these five
#: rows were dropped" are different claims, and only the second says the filter worked.
REFUSED_FOR_VINTAGE = frozenset(
    {("DGS3MO", "2014-12-31"), ("DGS6MO", "2014-12-31"), ("DGS1", "2014-12-31"),
     ("DGS2", "2014-12-31"), ("DGS10", "2014-12-31")}
)

#: The register refuses these four. No column may be one and no byte of either file may contain
#: one. `T10YIE` is here although both of its inputs are columns (DD45).
REFUSED_SERIES = ("VIXCLS", "BAA10Y", "AAA10Y", "T10YIE")

GSW_COLUMNS = tuple(name for name in DAILY_SERIES if name.startswith("SVENY"))
VINTAGE_SOURCES = {
    "cmt_daily_dev.csv": ("DGS3MO", "DGS6MO", "DGS1", "DGS2", "DGS10"),
    "block_i_vintages_dev.csv": ("DFII5", "DFII10", "DFII30"),
    "fx_vintages_dev.csv": ("DEXUSEU",),
}


def _rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return tuple(reader.fieldnames or ()), list(reader)


def _as_date(text: str) -> date:
    year, month, day = text.split("-")
    return date(int(year), int(month), int(day))


def _blank(value: str) -> bool:
    return value in ("", "NA")


# ---------------------------------------------------------------------------
# C42 -- the grid
# ---------------------------------------------------------------------------


def test_c42_the_panel_is_on_curvecasts_gsw_session_grid() -> None:
    """C42. B42, DD42. The grid is re-parsed from curvecast, not asserted as a count.

    `len(dates) == 7044` is satisfied by any seven thousand strings. What is claimed is that
    this panel sits on **curvecast's** GSW DEV sessions, in that order, so the grid is read
    from `gsw_zero_dev.csv` at test time and compared date for date.

    **Off-machine the grid is the certificate's** (DD69). `len(dates) == 7044` is still
    satisfied by any seven thousand strings, but a digest over the dates in order is not, so
    the claim survives the reviewer's machine in the form that carries content.
    """
    header, panel = _rows(DAILY_FIXTURE)
    assert header == ("Date", *DAILY_SERIES), f"unexpected columns: {header}"
    assert len(header) == 18, f"the panel has {len(header)} columns, expected 18"

    dates = [row["Date"] for row in panel]
    assert digest(dates) == SESSION_GRID, "the panel has left the certified GSW session grid"
    assert len(dates) == EXPECTED_SESSIONS == len(set(dates))
    assert dates == sorted(dates), "the panel is not in date order"
    assert (dates[0], dates[-1]) == ("1988-01-01", "2014-12-31")
    assert DEV_START == _as_date(dates[0]) and DEV_END == _as_date(dates[-1])

    upstream = CURVECAST / "tests" / "fixtures" / "gsw_zero_dev.csv"
    if upstream.exists():
        _, source = _rows(upstream)
        grid = [row["Date"] for row in source]
        assert dates == grid, "the panel is not on curvecast's GSW session grid"
        assert digest(grid) == SESSION_GRID, (
            "curvecast's grid has moved; the certificate is stale and must be regenerated"
        )


# ---------------------------------------------------------------------------
# C43 / C47 -- licence closure, and the mutation that proves it bites
# ---------------------------------------------------------------------------


def test_c43_every_committed_column_is_public_domain() -> None:
    """C43. B43, DD48. Per column against the register, then over the bytes.

    The column check is the claim; the byte scan is what catches a restricted series arriving
    somewhere a column list does not reach -- inside a value, a header this package forgot to
    name, or a comment.
    """
    for fixture, expected in ((DAILY_FIXTURE, DAILY_SERIES), (MONTHLY_FIXTURE, MONTHLY_SERIES)):
        header, _ = _rows(fixture)
        assert header[0] == "Date", f"{fixture.name} does not open with a Date column"
        columns = header[1:]
        assert columns == expected, f"{fixture.name} carries {columns}, expected {expected}"

        refuse_uncommittable(columns)  # the loader's own check, not a copy of it
        for name in columns:
            row = SOURCES[name]
            assert row.committable, f"{name} is {row.licence.name} and is in a committed file"
            assert row.licence is Licence.PUBLIC_DOMAIN

        text = fixture.read_text(encoding="utf-8")
        present = [name for name in REFUSED_SERIES if name in text]
        assert not present, f"{fixture.name} contains refused series {present}"

    assert len(DAILY_SERIES) + len(MONTHLY_SERIES) == 18


def test_c47_a_fixture_carrying_a_restricted_series_is_refused() -> None:
    """C47. B47. The mutation: C43's checker must reject what C43 says it never sees.

    Three shapes, because the register refuses for three different reasons and a guard that
    only caught one of them would pass this suite while admitting the other two.

    **Two of the three shapes were retired by DD137 on 2026-09-23**, and that is recorded here
    rather than deleted. `BAA10Y` and `T10YIE` were this bar's redistribution-prohibited and
    citation-required refusals; the owner admitted both by name. Asserting that they still
    raise would be asserting a guarantee that was deliberately given up, and quietly dropping
    the lines would leave a gap where a refusal used to be. They are asserted to **pass**
    instead, so the lift stays visible at the exact site it changed.
    """
    refuse_uncommittable(DAILY_SERIES)  # the real thing does not raise

    refuse_uncommittable((*DAILY_SERIES[:-1], "BAA10Y"))  # admitted by name, DD137
    refuse_uncommittable(("T10YIE",))  # admitted by name, DD137

    # What still refuses, and it is the axis DD137's reasoning cannot cross: Cboe's words
    # forbid the computation, not the sending, so no decision about sending reaches it.
    with pytest.raises(UncommittableSeries, match="VIXCLS"):
        refuse_uncommittable(("VIXCLS",))

    with pytest.raises(UncommittableSeries, match="DE_ZERO_10Y"):
        refuse_uncommittable(("DE_ZERO_10Y",))  # UNMEASURED is strictest, not absent

    with pytest.raises(UncommittableSeries, match="register"):
        refuse_uncommittable(("DGS7",))  # a real FRED series with no row here


# ---------------------------------------------------------------------------
# C44 -- the vintage rule
# ---------------------------------------------------------------------------


def test_c44_no_committed_value_needed_a_vintage_after_dev_ended() -> None:
    """C44. B44, DD43. The collapse is recomputed from curvecast, not trusted.

    `DEV_END` is 2014-12-31 and the five constant-maturity closes for that date were published
    2015-01-05. A panel that took `obs_date` at face value would carry five numbers first
    known inside VAL into the sample `FitWindow` exists to bound -- five rows out of 32,525,
    and the whole reason the filter is on the vintage.

    **Off-machine the collapse is certified rather than recomputed** (DD69). What the digest
    pins is this panel's committed values for the nine vintage-sourced series -- the side the
    archive contains -- against the bytes that did equal curvecast's collapse on the
    certificate's date. The five refusals are asserted on every machine.
    """
    fixtures = CURVECAST / "tests" / "fixtures"
    _, panel = _rows(DAILY_FIXTURE)
    committed = {
        series: {row["Date"]: row[series] for row in panel if not _blank(row[series])}
        for series in EXPECTED_COVERAGE
    }

    assert digest(sorted((k, sorted(v.items())) for k, v in committed.items())) == (
        VINTAGE_COLLAPSE
    ), "the panel is no longer the certified DEV_END-vintage collapse"
    for series, observed in REFUSED_FOR_VINTAGE:
        assert observed not in committed[series], f"{series} {observed} was committed anyway"

    if not fixtures.exists():
        return

    refused: set[tuple[str, str]] = set()
    for filename, series_names in VINTAGE_SOURCES.items():
        _, source = _rows(fixtures / filename)
        for series in series_names:
            best: dict[str, tuple[str, str]] = {}
            seen: set[str] = set()
            for row in source:
                if row["series_id"] != series:
                    continue
                observed, vintage = row["obs_date"], row["vintage_date"]
                if not DEV_START <= _as_date(observed) <= DEV_END:
                    continue
                seen.add(observed)
                if _as_date(vintage) > DEV_END:
                    continue
                if observed not in best or vintage > best[observed][0]:
                    best[observed] = (vintage, row["value"])

            refused |= {(series, observed) for observed in seen - set(best)}
            assert committed[series] == {
                observed: value for observed, (_, value) in best.items()
            }, f"{series} in the panel is not the DEV_END-vintage collapse of {filename}"
            for observed, (vintage, _) in best.items():
                assert _as_date(vintage) <= DEV_END, f"{series} {observed} used vintage {vintage}"

    assert refused == REFUSED_FOR_VINTAGE, f"vintage refusals are {sorted(refused)}"


# ---------------------------------------------------------------------------
# C45 -- coverage
# ---------------------------------------------------------------------------


def test_c45_coverage_is_the_coverage_that_was_measured() -> None:
    """C45. B45, DD42. Counts by name, so padding and dropping both fail.

    A generator that forward-filled would raise every count; one that dropped sparse rows
    would lower the session total and leave the counts alone. Both are caught by asserting
    the pair.
    """
    _, panel = _rows(DAILY_FIXTURE)
    assert len(panel) == EXPECTED_SESSIONS

    coverage = {
        series: sum(1 for row in panel if not _blank(row[series])) for series in EXPECTED_COVERAGE
    }
    assert coverage == EXPECTED_COVERAGE, f"coverage moved: {coverage}"

    assert len(GSW_COLUMNS) == 8
    blank_rows = [row["Date"] for row in panel if all(row[name] == "NA" for name in GSW_COLUMNS)]
    assert len(blank_rows) == EXPECTED_GSW_BLANK, "the federal holiday calendar changed size"
    for name in GSW_COLUMNS:
        assert sum(1 for row in panel if not _blank(row[name])) == EXPECTED_SESSIONS - EXPECTED_GSW_BLANK

    # DD43's visible consequence: the last session has GSW values and no constant maturities.
    last = panel[-1]
    assert last["Date"] == "2014-12-31"
    assert not _blank(last["SVENY01"]), "GSW is carried on observation date and has no vintage axis"
    assert all(_blank(last[name]) for name in ("DGS3MO", "DGS6MO", "DGS1", "DGS2", "DGS10"))

    _, monthly = _rows(MONTHLY_FIXTURE)
    assert len(monthly) == EXPECTED_MONTHLY
    assert all(not _blank(row["GZ_SPREAD"]) for row in monthly), "a monthly row is empty"


# ---------------------------------------------------------------------------
# C46 -- the loader
# ---------------------------------------------------------------------------


def test_c46_the_loader_takes_a_window_and_reports_what_completeness_costs() -> None:
    """C46. B46, DD42. The window is a type, and the dropped count is returned.

    The second half is the one with teeth. Complete cases across all seventeen series costs
    **5,831 of 7,044 sessions**, because `DFII30` opens in 2010 -- so a `complete_cases` that
    returned only the shorter panel would let a caller lose twenty-two years of sample without
    anyone writing the number down.
    """
    whole = load_daily(FitWindow.dev())
    assert len(whole.dates) == EXPECTED_SESSIONS
    assert whole.series == DAILY_SERIES
    assert whole.dates[0] == DEV_START and whole.dates[-1] == DEV_END

    narrow = load_daily(FitWindow(date(2010, 1, 1), date(2010, 12, 31)))
    assert all(date(2010, 1, 1) <= stamp <= date(2010, 12, 31) for stamp in narrow.dates)
    assert len(narrow.dates) < len(whole.dates)

    # The bound is the type's, and it is checked where a window is made rather than where it
    # is used: a fit reaching into the years every out-of-sample test runs on is refused.
    with pytest.raises(ValueError, match="DEV_END"):
        FitWindow(date(2014, 1, 1), date(2015, 1, 2))
    with pytest.raises(TypeError, match="datetime.date exactly"):
        FitWindow(datetime(2010, 1, 1), date(2010, 12, 31))  # type: ignore[arg-type]

    kept, dropped = complete_cases(whole)
    assert len(kept.dates) == 1_213 and dropped == EXPECTED_SESSIONS - 1_213 == 5_831
    assert kept.series == whole.series, "complete_cases must not silently narrow the columns"

    front, front_dropped = complete_cases(whole, ("DGS3MO", "DGS6MO", "DGS1", "DGS2", "DGS10"))
    assert len(front.dates) == 6_504 and front_dropped == 540

    legs, _ = complete_cases(whole, ("SVENY05", "DFII5"))
    assert len(legs.dates) == 3_002, "the breakeven leg's complete sample is DFII5's coverage"

    with pytest.raises(KeyError, match="T10YIE"):
        complete_cases(whole, ("T10YIE",))


# ---------------------------------------------------------------------------
# C48 -- the frequencies stay apart
# ---------------------------------------------------------------------------



def test_c117_the_pool_states_how_much_of_dev_it_is_jointly_observed_on() -> None:
    """C117. DD122, `AMENDMENT_A7` §7. A pool that shortened its own test window in silence.

    `AMENDMENT_A6` DD120 clause 4 makes an admission restate three counts in the same commit:
    the pool, the structure count and the leg count. It does not mention the one count
    `AMENDMENT_A7` measured to matter most -- the sample the admission test itself runs on.

    `complete_cases` needs every basis series present on the same row, so the window clause 2
    computes over is set by the SHORTEST member of the pool. `DFII30` opens 2010-02-22 and takes
    a 7,044-row panel down to 1,217 rows, every one of them inside the zero lower bound. That is
    not a presentational detail: on those rows the same-bonds floor the hurdle is derived from
    reads 0.1905 against 0.074 on the long sample, so a short series does not merely add a
    column -- it moves the threshold every later candidate is judged against, and nothing in
    the diff would say so.

    Held as an equality against the tree rather than as a figure in prose, because the number is
    a function of the pool and moves the moment the pool does. Green two ways, like C116: restate
    the sample, or do not shorten it.

    **Mutation:** with §0's stated joint sample replaced by the panel's own length, the bar
    reports the pool's true joint sample against it.
    """
    panel = load_daily(FitWindow.dev())
    joint, dropped = complete_cases(panel, tuple(CANDIDATE_SERIES))
    text = _read(AMENDMENT_A7)

    stated_panel = _stated(_PANEL_ROW, text, "the panel's row count")
    assert stated_panel == len(panel.dates) == EXPECTED_SESSIONS

    stated_joint = _stated(_JOINT_ROW, text, "the pool's joint sample")
    assert stated_joint == len(joint.dates) == EXPECTED_JOINT_POOL_ROWS, (
        f"the {len(CANDIDATE_SERIES)} series of `CANDIDATE_SERIES` are jointly observed on "
        f"{len(joint.dates)} rows and `AMENDMENT_A7` §0 row 3 states {stated_joint}. DD122 "
        "part 1: an admission reports the sample it ran on, and a pool that shortens that "
        "sample restates it in the same commit rather than leaving the figure stale."
    )
    assert dropped == len(panel.dates) - len(joint.dates)

    # The whole reason the figure is worth a bar. If this ever stops holding, the joint sample
    # is no longer the surprising quantity and DD122 part 1 can be reconsidered on the evidence.
    assert len(joint.dates) * 2 < len(panel.dates), (
        f"the joint sample is now {len(joint.dates)} of {len(panel.dates)} rows, no longer the "
        "minority `AMENDMENT_A7` §2 was written about"
    )

    mutated = text.replace(f"**{stated_joint:,}**", f"**{len(panel.dates):,}**", 1)
    assert _stated(_JOINT_ROW, mutated, "mutated") != len(joint.dates)


def test_c48_the_monthly_panel_is_not_a_daily_panel() -> None:
    """C48. B48, DD44. Two files, and 92 labels that are not sessions at all.

    The number is the argument. Of 323 month-start labels, **92 fall on a date the GSW session
    grid does not contain** -- weekends and holidays. A merge onto the daily grid would have to
    decide what to do with them, and the only answers are to drop a published observation or to
    invent a session; both are decisions this package refuses to make on a later package's
    behalf.
    """
    assert DAILY_FIXTURE != MONTHLY_FIXTURE
    assert DAILY_FIXTURE.exists() and MONTHLY_FIXTURE.exists()
    assert "GZ_SPREAD" not in DAILY_SERIES and MONTHLY_SERIES == ("GZ_SPREAD",)

    monthly = load_monthly(FitWindow.dev())
    assert monthly.series == MONTHLY_SERIES
    assert len(monthly.dates) == EXPECTED_MONTHLY
    assert all(stamp.day == 1 for stamp in monthly.dates), "a label is not a month start"
    assert monthly.dates[0] == date(1988, 1, 1) and monthly.dates[-1] == date(2014, 11, 1)

    sessions = set(load_daily(FitWindow.dev()).dates)
    off_grid = [stamp for stamp in monthly.dates if stamp not in sessions]
    assert len(off_grid) == 92, f"{len(off_grid)} month starts are not sessions"

    # No join is offered, and the absence is asserted rather than assumed: a helper that put
    # these on the daily grid is one keyword argument away from being used by default.
    import deskcraft.panel as module

    offered = {name for name in module.__all__ if name.islower()}
    forbidden = {"merge", "join", "align", "resample", "reindex", "fill", "ffill", "interpolate"}
    assert not {name for name in offered if any(word in name for word in forbidden)}, offered


def test_c168_the_h10_majors_arrive_in_a_file_of_their_own() -> None:
    """C168. DD168. Six public-domain exchange rates, DEV only, on the grid, quoted as published.

    The owner decided hedges carry currency legs in the H.10 majors and that the panel holds them
    before the first out-of-sample read. They arrive as `panel_daily_fx_dev_20260926.csv`, from one
    ALFRED as-of-`DEV_END` read per series in curvecast, and the two panels every registered
    verdict reads are not rewritten, so nothing pinned can move.

    **Mutation:** the quote conventions are checked against the data, not the docstring. Sterling
    is quoted like the euro, in dollars per unit, so their log returns correlate positively; the
    Swiss franc is quoted per dollar, so its returns correlate negatively with the euro's. A table
    that had the franc's quote backwards would pass every other assertion here and fail this one.
    """
    from deskcraft import covariance as cv
    from deskcraft.panel import FX_FIXTURE, FX_QUOTES, FX_SERIES, load_daily_fx

    with FX_FIXTURE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    header, body = tuple(rows[0]), rows[1:]
    assert header == ("Date", *FX_SERIES)
    refuse_uncommittable(header[1:])
    assert all(SOURCES[s].licence is Licence.PUBLIC_DOMAIN for s in FX_SERIES)

    with DAILY_FIXTURE.open(newline="", encoding="utf-8") as handle:
        grid = [row[0] for row in csv.reader(handle)][1:]
    assert [row[0] for row in body] == grid, "the fx panel is not on the daily panel's grid"
    assert max(date.fromisoformat(row[0]) for row in body) <= DEV_END

    coverage = {s: sum(1 for row in body if row[k + 1] != "") for k, s in enumerate(FX_SERIES)}
    assert coverage == {
        "DEXJPUS": 6_785, "DEXUSUK": 6_785, "DEXCAUS": 6_785,
        "DEXSZUS": 6_785, "DEXCHUS": 6_724, "DEXMXUS": 5_308,
    }
    last = {s: max(row[0] for row in body if row[k + 1] != "") for k, s in enumerate(FX_SERIES)}
    assert set(last.values()) == {"2014-12-24"}, "the vintage rule's footprint: the last print known by DEV_END"

    panel = load_daily_fx(FitWindow(DEV_START, DEV_END))
    assert panel.series == FX_SERIES and len(panel.dates) == len(grid)
    assert all(cv.UNIT_OF[s] is cv.Unit.PERCENT_LOG_RETURN for s in FX_SERIES)
    assert set(FX_QUOTES) == {"DEXUSEU", *FX_SERIES}
    per_foreign = {s for s, (_, quote) in FX_QUOTES.items() if quote.startswith("USD per")}
    assert per_foreign == {"DEXUSEU", "DEXUSUK"}

    fitted = cv.fit(("DEXUSEU", "DEXUSUK", "DEXSZUS"), FitWindow(date(1999, 1, 4), DEV_END))
    assert fitted.correlation("DEXUSEU", "DEXUSUK") > 0.5
    assert fitted.correlation("DEXUSEU", "DEXSZUS") < -0.5
