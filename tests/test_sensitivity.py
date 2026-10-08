"""D4's bars: the duration is the right one for the quote, and the signs are not accidents.

Nine bars, and three of them re-derive their subject from a sibling repository at test time
rather than trusting a constant here -- `C49` the compounding conventions out of the
Gurkaynak-Sack-Wright file's own header block, `C50` MEIP's `par_bond_duration_convexity`
executed from its own bytes, and `C51` the understatement percentages recomputed from the
committed panel. They **skip loudly** when the sibling is absent, in `C31`'s shape.

`C50` is the whole of what "wraps `meip.rates.cascade.par_bond_duration_convexity`" can mean
here: `meip` is not importable on this interpreter and `cascade.py` reaches numpy, pydantic and
two stores at module level, so the function node is parsed out, compiled alone and run. Exact
equality, not a tolerance -- the restatement is line for line and a tolerance would hide a
reordered summation.

`C55` records a contradiction rather than repairing one. `US_BREAKEVEN_5Y` declares
`Neutrality.DV01`, `book.py` admits that because its coefficients cancel, and its two
components are quoted on different conventions -- so a parallel move leaves a residual. The
instrument is not edited here; D7b decides whether that leg should be matched on duration
rather than on coefficients, which is where D5's `DD40` left the same shape of question.
"""

from __future__ import annotations

import ast
import math
from datetime import date

import pytest

from deskcraft.book import (
    Component,
    Currency,
    Instrument,
    InstrumentKind,
    Leg,
    Neutrality,
    Notional,
)
from deskcraft.panel import load_daily
from deskcraft.reference import REFERENCE_BOOK, SCENARIO_SIGNS, US_CASH_BOOK
from deskcraft.sensitivity import (
    BASIS_POINT,
    COMPOUNDING_OF,
    RATE_SENSE_OF,
    TENOR_OF,
    Compounding,
    CurveShift,
    RateSense,
    UnknownConvention,
    Unpriceable,
    book_dv01,
    book_pnl,
    convexity,
    leg_pnl,
    leg_sensitivity,
    modified_duration,
    par_bond_duration_convexity,
    second_order_pnl,
)
from deskcraft.sources import SOURCES
from deskcraft.window import FitWindow

from test_deskcraft_boundary import MEIP
from upstream_certificate import GSW_CONVENTIONS, PAR_BOND_GRID, digest

#: The Board's fitted curve, as curvecast pins it in its seal manifest under `gsw_svensson`.
#: Its first nine lines carry a compounding-convention block, which is what `C49` reads.
GSW_SOURCE = MEIP / "data" / "gsw" / "feds200628.csv"
CASCADE = MEIP / "src" / "meip" / "rates" / "cascade.py"

#: The last DEV session on which every series `US_CASH_BOOK` needs is published -- the 2,998th
#: and last complete case over `SVENY02, SVENY05, SVENY10, DFII5, DEXUSEU`. Measured
#: 2026-09-15 and fixed in `PRECOMMIT_deskcraft_d4_dv01_and_leg_pnl.md` section 0.4 before any
#: of this was written.
MEASURED_ON = date(2014, 12, 24)

#: What the par proxy gives away on a zero-quoted leg, per section 0.4. Recomputed from the
#: committed fixture by `C51` rather than restated: the yields are read, so a fixture that
#: moved would move these.
EXPECTED_UNDERSTATEMENT = {"SVENY02": 1.142, "SVENY05": 5.177, "SVENY10": 11.730}

#: Section 0.6. The residual a parallel one-basis-point move leaves on a leg that declares
#: itself DV01-neutral, in dollars per basis point on the stated $50m.
EXPECTED_BREAKEVEN_RESIDUAL = 370.67

#: Section 0.7's cross-check, stated here so `C55` cannot be tuned to the annual-pay figure:
#: recomputing `DFII5` semi-annually gives 340.34, the same sign and the same order.
SEMI_ANNUAL_RESIDUAL = 340.34


def _dev_yields(stamp: date) -> dict[str, float]:
    """Every series published on `stamp`, in percent, read from the committed panel."""
    panel = load_daily(FitWindow.dev())
    index = panel.dates.index(stamp)
    return {
        name: value
        for name in panel.series
        if (value := panel.values[name][index]) is not None
    }


def _meip_par_bond():
    """MEIP's own function, parsed out of `cascade.py` and compiled alone.

    Importing `meip.rates.cascade` is not available here -- `meip` is not on this
    interpreter's path, and the module reaches numpy, pydantic, `MacroStore` and
    `UnexplainedMoveStore` at import time, which would put a store into a test process that is
    forbidden to read `data/meip.duckdb`. The function's body reaches only `ValueError`,
    `range`, `sum` and arithmetic, so it compiles and runs on its own.
    """
    tree = ast.parse(CASCADE.read_text(encoding="utf-8"))
    node = next(
        item
        for item in tree.body
        if isinstance(item, ast.FunctionDef) and item.name == "par_bond_duration_convexity"
    )
    namespace: dict[str, object] = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(CASCADE), "exec"), namespace)
    return namespace["par_bond_duration_convexity"]


def _leg(book, leg_id: str) -> Leg:
    return book.leg(leg_id)


# ---------------------------------------------------------------------------
# C49 -- the convention is read from the licensor, and refused by default
# ---------------------------------------------------------------------------


def test_the_compounding_convention_is_the_licensors_own_word() -> None:
    """C49. B49, DD49. Parsed from the source file, not asserted as a constant here.

    The Board publishes the convention three lines above the data, and it distinguishes
    `SVENYXX` from `SVENPYXX` in exactly the way this package turns on. A hardcoded copy here
    would be a second statement about the same bytes, which is the drift `C31` was written to
    prevent for the DEV bounds.

    The H.15 half is read out of D3a's own register: the DFII rows' fallback is Treasury's
    *par real* yield curve and the nominal rows' is Treasury's *par* yield curve, recorded on
    2026-09-11, three days before a package needed the word.

    **Off-machine the licensor's words come from the certificate** (DD69), and the assertion
    that carries content is the one below it: `COMPOUNDING_OF`, which is engine code and ships
    in the archive, must agree with them. When the panel IS here the header is parsed and the
    certificate is held at equality against all four of its `XX` rows -- including the two this
    package never reads, which is what shows the block was parsed and not remembered.
    """
    conventions = dict(GSW_CONVENTIONS)
    if GSW_SOURCE.exists():
        conventions = {}
        with GSW_SOURCE.open(encoding="utf-8", newline="") as handle:
            for position, line in enumerate(handle):
                if position >= 9:
                    break
                fields = line.rstrip("\r\n").split(",")
                if len(fields) == 3 and fields[2].endswith("XX"):
                    conventions[fields[2]] = fields[1]
        assert conventions == GSW_CONVENTIONS, conventions

    assert conventions.get("SVENYXX") == "Continuously Compounded", conventions
    assert conventions.get("SVENPYXX") == "Coupon-Equivalent", conventions

    zeros = [name for name in COMPOUNDING_OF if name.startswith("SVENY")]
    assert len(zeros) == 8, zeros
    for name in zeros:
        assert COMPOUNDING_OF[name] is Compounding.CONTINUOUS, name

    # The par-quoted half, from the register rather than from memory.
    assert "Par Real Yield Curve Rates" in SOURCES["DFII5"].fallback
    assert "Par Yield Curve Rates" in SOURCES["DGS10"].fallback
    for name in ("DFII5", "DFII10", "DFII30", "DGS2", "DGS10"):
        assert COMPOUNDING_OF[name] is Compounding.COUPON_EQUIVALENT, name

    # Refused by default (DD49): neither has a duration this module can compute.
    for name in ("DEXUSEU", "GZ_SPREAD"):
        assert name not in COMPOUNDING_OF
        with pytest.raises(UnknownConvention, match=name):
            modified_duration(name, 1.0)

    assert set(COMPOUNDING_OF) == set(TENOR_OF), "a series with a convention needs a tenor"


# ---------------------------------------------------------------------------
# C50 -- the wrap, measured against MEIP's own bytes
# ---------------------------------------------------------------------------


def test_the_par_bond_restatement_reproduces_meip_exactly() -> None:
    """C50. B50, DD50-DD51. MEIP's function is executed, not paraphrased.

    Exact equality on both returned values. The restatement is line for line -- `sum` rather
    than `math.fsum`, the flows in MEIP's order -- precisely so that this bar can be an
    equality: a tolerance would pass a reordered summation, and a reordered summation is how a
    restatement stops being one.

    **Off-machine the equality is against the certificate** (DD69), which is a digest of MEIP's
    own 72 answers taken on the date above. `repr` round-trips a float exactly, so the digest is
    still an equality and not a tolerance -- the distinction this bar exists for survives the
    reviewer's machine intact.
    """
    grid = [
        (yield_pct, maturity)
        for yield_pct in (-0.5, 0.0, 0.5, 1.0, 2.0, 2.335, 4.0, 7.25, 15.0)
        for maturity in (1, 2, 3, 5, 7, 10, 20, 30)
    ]
    assert len(grid) == 72
    ours = [par_bond_duration_convexity(yield_pct, maturity) for yield_pct, maturity in grid]
    assert digest(ours) == PAR_BOND_GRID, "the restatement has left MEIP's certified answers"

    for bad_maturity in (0, -1):
        with pytest.raises(ValueError):
            par_bond_duration_convexity(4.0, bad_maturity)
    with pytest.raises(ValueError):
        par_bond_duration_convexity(-100.0, 5)

    if not CASCADE.exists():
        return

    theirs = _meip_par_bond()
    for (yield_pct, maturity), mine in zip(grid, ours, strict=True):
        assert mine == theirs(yield_pct, maturity), (
            f"restatement diverges at ytm={yield_pct}%, T={maturity}"
        )
    assert digest([theirs(y, m) for y, m in grid]) == PAR_BOND_GRID, (
        "MEIP's answers have moved; the certificate is stale and must be regenerated"
    )

    # Both refusals, reproduced as refusals.
    for bad_maturity in (0, -1):
        with pytest.raises(ValueError):
            theirs(4.0, bad_maturity)
    with pytest.raises(ValueError):
        theirs(-100.0, 5)


# ---------------------------------------------------------------------------
# C51 -- the zero branch is the exact form, and the proxy costs 11.7% at ten years
# ---------------------------------------------------------------------------


def test_the_zero_branch_is_exact_and_the_proxy_is_not() -> None:
    """C51. B51, DD50. The gap is recomputed from the committed panel, not restated.

    `-(dP/dy)/P = T` under continuous compounding, for every yield, which is the whole reason
    the wrap is declined for three of the four legs. The three percentages are what applying
    MEIP's par proxy to a zero-quoted series would give away.

    **The two forms coincide at exactly one yield, and this bar was written not knowing it.**
    At `y = 0` the par bond's coupon is zero, so it *is* the zero it is being compared with and
    its modified duration is the maturity exactly. The first run of this bar asserted the
    proxy differed everywhere and failed there, correctly. The coincidence is duration-only:
    the convexities still disagree at that point, 110 against 100, because the compounding
    convention has not stopped differing just because the cash flows have collapsed.
    """
    for yield_pct in (-0.5, 0.0, 0.5, 2.3354, 6.0, 12.0):
        assert modified_duration("SVENY10", yield_pct) == 10.0
        assert convexity("SVENY10", yield_pct) == 100.0
    for yield_pct in (-0.5, 0.5, 2.3354, 6.0, 12.0):
        assert par_bond_duration_convexity(yield_pct, 10)[0] != 10.0
    assert par_bond_duration_convexity(0.0, 10) == (10.0, 110.0)
    assert convexity("SVENY10", 0.0) == 100.0

    yields = _dev_yields(MEASURED_ON)
    for series, expected in EXPECTED_UNDERSTATEMENT.items():
        tenor = TENOR_OF[series]
        proxy, _ = par_bond_duration_convexity(yields[series], int(tenor))
        understatement = (tenor - proxy) / tenor * 100.0
        assert round(understatement, 3) == expected, (series, understatement)

    # The tenor comes from the series, and restating it wrongly is refused rather than honoured.
    with pytest.raises(UnknownConvention, match="quoted at"):
        modified_duration("SVENY10", 2.0, tenor_years=7.0)
    # MEIP's signature takes whole years, so D5's front end is out of the par branch's reach.
    with pytest.raises(UnknownConvention, match="whole years"):
        modified_duration("DGS3MO", 0.1)


# ---------------------------------------------------------------------------
# C52 -- the sense table is total, single-valued, and its image is the whole enum
# ---------------------------------------------------------------------------


def _sense_table_offences(table: dict) -> list[str]:
    """What is wrong with a candidate sense table. Shared by the real check and its mutation."""
    out = []
    missing = sorted(kind.name for kind in InstrumentKind if kind not in table)
    if missing:
        out.append(f"kinds with no sense: {missing}")
    stray = sorted(str(key) for key in table if not isinstance(key, InstrumentKind))
    if stray:
        out.append(f"keys that are not kinds: {stray}")
    unreached = sorted(sense.name for sense in RateSense if sense not in set(table.values()))
    if unreached:
        out.append(f"senses no kind carries: {unreached}")
    return out


def test_the_rate_sense_table_is_total_and_its_image_is_the_whole_enum() -> None:
    """C52. B52, DD53. A kind with no sense is an exception discovered mid-run.

    **Mutation:** a kind deleted and a foreign key added, both through the same function the
    real check reads, so the mutation exercises the scan rather than a copy of it.
    """
    assert _sense_table_offences(RATE_SENSE_OF) == []
    assert len(RATE_SENSE_OF) == len(InstrumentKind) == 12

    deleted = {k: v for k, v in RATE_SENSE_OF.items() if k is not InstrumentKind.SWAP_SPREAD}
    assert _sense_table_offences(deleted) == ["kinds with no sense: ['SWAP_SPREAD']"]

    widened = dict(RATE_SENSE_OF) | {"SWAPTION": RateSense.RATE}
    assert _sense_table_offences(widened) == ["keys that are not kinds: ['SWAPTION']"]

    flattened = dict.fromkeys(RATE_SENSE_OF, RateSense.PRICE)
    assert _sense_table_offences(flattened) == [
        "senses no kind carries: ['NONE', 'RATE', 'UNPRICEABLE']"
    ]


# ---------------------------------------------------------------------------
# C53 -- the signs reproduce the matrix D2 wrote and DD53 never consulted
# ---------------------------------------------------------------------------


def test_the_signs_reproduce_the_reference_scenario_matrix() -> None:
    """C53. B53, DD20, DD53. Signs only, which is all `SCENARIO_SIGNS` asserts.

    `RATE_SENSE_OF` was decided from what each instrument *is* -- a bond is long its price, a
    spread is long its rate -- and this bar then checks it against a matrix written at D2 for
    a different purpose. The three rows below are the ones where the source's table makes a
    claim about a rate move; the rest of the matrix is about scenarios this package cannot
    express, and D12 scores those.
    """
    yields = _dev_yields(MEASURED_ON)
    cases = (
        # scenario, leg, the move the scenario describes
        ("fed_signals_fewer_cuts", "us_2y", CurveShift((("SVENY02", 10.0),))),
        ("fed_signals_fewer_cuts", "us_10y", CurveShift((("SVENY10", 10.0),))),
        ("supply_shock", "us_10y", CurveShift((("SVENY10", 25.0),))),
        ("supply_shock", "us_breakeven_5y", CurveShift((("SVENY05", 25.0),))),
        ("inflation_surprises_higher", "us_breakeven_5y", CurveShift((("SVENY05", 15.0),))),
    )
    for scenario, leg_id, shift in cases:
        expected = SCENARIO_SIGNS[scenario][leg_id]
        assert expected == 1, (scenario, leg_id)
        pnl = leg_pnl(_leg(US_CASH_BOOK, leg_id), shift, yields)
        assert pnl > 0.0, f"{scenario}/{leg_id} was asserted a gain and came out {pnl}"

    # And the other direction, which the matrix's `everything_goes_wrong` row implies for the
    # two short bond legs: a rate fall is a loss on a short.
    for leg_id, series in (("us_2y", "SVENY02"), ("us_10y", "SVENY10")):
        assert leg_pnl(_leg(US_CASH_BOOK, leg_id), CurveShift(((series, -10.0),)), yields) < 0.0


# ---------------------------------------------------------------------------
# C54 -- a declared zero and a refusal are different facts
# ---------------------------------------------------------------------------


def test_no_rate_sensitivity_and_unpriceable_are_distinguishable() -> None:
    """C54. B54, DD53. `eurusd` returns 0.0; the option leg raises.

    A single zero would merge two facts: *this instrument has no first-order rate sensitivity*
    and *this instrument has plenty and free data cannot compute it*. The second is
    `reference.DEFERRED_LEGS`' stated reason for carrying the option leg unpriced, and a zero
    is a number every sum downstream would add.
    """
    yields = _dev_yields(MEASURED_ON)
    eurusd = leg_sensitivity(_leg(US_CASH_BOOK, "eurusd"), yields)
    assert eurusd.sense is RateSense.NONE
    assert eurusd.components == ()
    assert eurusd.net_dv01 == 0.0
    assert leg_pnl(_leg(US_CASH_BOOK, "eurusd"), CurveShift((("SVENY10", 100.0),)), yields) == 0.0

    option = _leg(REFERENCE_BOOK, "us_10y_call")
    assert RATE_SENSE_OF[option.instrument.kind] is RateSense.UNPRICEABLE
    with pytest.raises(Unpriceable, match="us_10y_call"):
        leg_sensitivity(option, yields)

    # The mutation: the same notional and direction under a priceable kind is not a refusal,
    # so the refusal is the kind's and not the leg's shape.
    priceable = Leg(
        "us_10y_call",
        Instrument(
            symbol="US_ZERO_10Y",
            kind=InstrumentKind.ZERO_YIELD,
            currency=Currency.USD,
            tenor_years=10.0,
            components=(Component("SVENY10", 1.0, Currency.USD),),
        ),
        option.direction,
        Notional(option.notional.amount, Currency.USD),
    )
    assert leg_sensitivity(priceable, yields).net_dv01 != 0.0

    # And a whole book holding an unpriceable leg is refused rather than partially totalled.
    with pytest.raises(Unpriceable, match="us_10y_call"):
        book_dv01(REFERENCE_BOOK, yields)
    assert set(book_dv01(US_CASH_BOOK, yields)) == set(US_CASH_BOOK.leg_ids)


# ---------------------------------------------------------------------------
# C55 -- the declared neutrality, and the residual it does not have
# ---------------------------------------------------------------------------


def test_the_breakeven_leg_declares_dv01_neutrality_it_does_not_have() -> None:
    """C55. B55, DD49, DD53. Coefficient-neutral is not DV01-neutral.

    `book.py` admits `Neutrality.DV01` on this instrument because `+1` and `-1` sum to zero.
    Its nominal component is a continuously compounded zero and its real component is a
    coupon-equivalent par constant maturity, so equal coefficients are not equal DV01 and a
    parallel move does not cancel.

    The instrument is **not edited here** (D70). This bar records the contradiction; whether
    the leg should be matched on duration is D7b's decision.
    """
    yields = _dev_yields(MEASURED_ON)
    leg = _leg(US_CASH_BOOK, "us_breakeven_5y")
    assert leg.instrument.neutrality is Neutrality.DV01
    assert math.fsum(item.coefficient for item in leg.instrument.components) == 0.0

    sensitivity = leg_sensitivity(leg, yields)
    assert sensitivity.sense is RateSense.RATE
    by_series = {item.series: item for item in sensitivity.components}
    assert by_series["SVENY05"].compounding is Compounding.CONTINUOUS
    assert by_series["DFII5"].compounding is Compounding.COUPON_EQUIVALENT
    assert by_series["SVENY05"].modified_duration == 5.0
    assert by_series["DFII5"].modified_duration != 5.0

    parallel = CurveShift.parallel(("SVENY05", "DFII5"), 1.0)
    residual = leg_pnl(leg, parallel, yields)
    assert residual != 0.0, "a leg declaring DV01 neutrality came out neutral; check the panel"
    assert round(residual, 2) == EXPECTED_BREAKEVEN_RESIDUAL
    assert round(sensitivity.net_dv01, 2) == EXPECTED_BREAKEVEN_RESIDUAL

    # Not an artefact of MEIP's annual-pay form: the semi-annual recomputation is the same
    # sign and the same order, and it is stated so this bar cannot be tuned to either figure.
    assert 0.0 < SEMI_ANNUAL_RESIDUAL < EXPECTED_BREAKEVEN_RESIDUAL
    assert residual / leg.notional.amount / BASIS_POINT == pytest.approx(0.074133, abs=1e-6)


# ---------------------------------------------------------------------------
# C56 -- the shift is keyed by series, and a stray name is refused
# ---------------------------------------------------------------------------


def test_the_shift_is_per_series_and_a_stray_series_is_refused() -> None:
    """C56. B56, DD54-DD55. A mistyped mnemonic must not report "no effect".

    A per-tenor shift cannot address `US_BREAKEVEN_5Y`, which holds two curves at five years,
    and the first two assertions are that measurement: the same tenor, two different answers.
    """
    yields = _dev_yields(MEASURED_ON)
    leg = _leg(US_CASH_BOOK, "us_breakeven_5y")
    nominal_only = leg_pnl(leg, CurveShift((("SVENY05", 1.0),)), yields)
    real_only = leg_pnl(leg, CurveShift((("DFII5", 1.0),)), yields)
    assert nominal_only > 0.0 > real_only
    assert nominal_only != -real_only, "the two five-year curves are not interchangeable"

    with pytest.raises(ValueError, match="SVENY07"):
        book_pnl(US_CASH_BOOK, CurveShift((("SVENY07", 5.0),)), yields)

    # A series the book holds but this shift omits is unshifted, which is a partial move and
    # not an error.
    partial = book_pnl(US_CASH_BOOK, CurveShift((("SVENY02", 5.0),)), yields)
    assert partial["us_2y"] != 0.0
    assert partial["us_10y"] == 0.0

    for bad in ((), (("SVENY02", 1.0), ("SVENY02", 2.0)), (("", 1.0),)):
        with pytest.raises(ValueError):
            CurveShift(bad)
    with pytest.raises(ValueError, match="finite"):
        CurveShift((("SVENY02", float("nan")),))
    with pytest.raises(TypeError):
        CurveShift((("SVENY02", True),))
    assert CurveShift.parallel(("SVENY02", "SVENY10"), 5.0).basis_points("DFII5") == 0.0


# ---------------------------------------------------------------------------
# C57 -- first order, and the size of what that drops
# ---------------------------------------------------------------------------


def test_the_book_totals_and_the_dropped_second_order_term_is_named() -> None:
    """C57. B57, DD56. `leg_pnl` is first order and the convexity term is 5% at 100 bp.

    Asserted rather than described, so that a later package folding convexity into `leg_pnl`
    -- or dropping it further -- moves a number a bar is watching. The second-order term is
    **negative** on `us_10y`, which is a short: convexity works for the long.
    """
    yields = _dev_yields(MEASURED_ON)
    shift = CurveShift.parallel(("SVENY02", "SVENY05", "SVENY10", "DFII5"), 25.0)

    by_leg = book_pnl(US_CASH_BOOK, shift, yields)
    assert set(by_leg) == set(US_CASH_BOOK.leg_ids)
    # The same total, reached through `book_dv01` instead, which shares no arithmetic with
    # `book_pnl` beyond `leg_sensitivity`.
    through_dv01 = math.fsum(
        item.dv01 * shift.basis_points(item.series)
        for sensitivity in book_dv01(US_CASH_BOOK, yields).values()
        for item in sensitivity.components
    )
    assert math.fsum(by_leg.values()) == through_dv01

    hundred = CurveShift((("SVENY10", 100.0),))
    us_10y = _leg(US_CASH_BOOK, "us_10y")
    first = leg_pnl(us_10y, hundred, yields)
    second = second_order_pnl(us_10y, hundred, yields)
    assert first > 0.0 > second, (first, second)
    assert round(abs(second / first) * 100.0, 3) == 5.0

    # Refused for a spread quoted as a rate: that convexity belongs to legs D7b generates.
    with pytest.raises(Unpriceable, match="spread quoted as a rate"):
        second_order_pnl(_leg(US_CASH_BOOK, "us_breakeven_5y"), hundred, yields)
