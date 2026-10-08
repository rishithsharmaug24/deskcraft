"""D7a's bars: the cost numbers are conventions, the absences are declared, and the denominator is gross.

Eleven bars, and not one of them reaches a sibling repository. That is deliberate and it is
checked elsewhere: the whole of this package is this repository's own arithmetic over its own
committed panel, so nothing here joins the environment census, and C72's eighteen and C73's
seven do not move.

Three of the eleven exist because a number here could be quietly replaced by a worse one that
still looks right.

`C77` holds the **shape** of every nominal half-spread rather than its value -- an exact dyadic
fraction of one thirty-second of a point -- because the thing that would go wrong is a fitted
decimal arriving where a quoting convention was, and `0.42` reads as plausible while `1/8 of a
32nd` does not.

`C82` holds that the denominator is **gross** DV01. `LegSensitivity.net_dv01` is a residual on
any leg declaring a neutrality, and on `us_breakeven_5y` the two differ by a factor of 133.89;
on a spread whose declared neutrality actually held, the net is zero and a cost divided by it is
infinite. A well-hedged structure priced as infinitely expensive is the failure this bar exists
to foreclose.

`C84` recomputes the convention arm from the committed fixture rather than restating 13.289%, so
a panel that moved would move the bar rather than leaving it agreeing with a stale constant --
which is `C51`'s shape, one package along.
"""

from __future__ import annotations

import ast
import math
import re
from datetime import date
from pathlib import Path

import pytest

from deskcraft.book import (
    Component,
    Currency,
    Direction,
    Instrument,
    InstrumentKind,
    Leg,
    Neutrality,
    Notional,
    ReExpression,
)
from deskcraft.costs import (
    BIASES,
    BUCKET_INCREMENT,
    COST_HURDLE,
    COST_MULTIPLIERS,
    COST_OF,
    FRBSF_ABSOLUTE_BOUND_BP,
    HURDLE_HOLDING_YEARS,
    SEASONING_PENALTY,
    THIRTY_SECOND_BP,
    TIPS_ILLIQUIDITY,
    UNGRADED_TERMS,
    UNPRICED_SERIES,
    AnnualisedCost,
    Bias,
    BiasSense,
    CostBasis,
    CostProfile,
    CostTerm,
    DurationConvention,
    LegCountEffect,
    Maintenance,
    Market,
    MarketDepth,
    MaturityBucket,
    NoRateRisk,
    TermNotAvailable,
    Untradeable,
    annualised_cost,
    bucket_of,
    compounded_bias,
    cost_ladder,
    cost_of,
    cost_per_dv01,
    gross_dv01,
    instrument_half_spread,
)
from deskcraft.generator import candidate_legs
from deskcraft.panel import load_daily
from deskcraft.reference import REFERENCE_BOOK, US_CASH_BOOK
from deskcraft.sensitivity import TENOR_OF, leg_sensitivity, modified_duration
from deskcraft.sources import SOURCES
from deskcraft.window import FitWindow
from test_deskcraft_boundary import SRC, _read
from test_guards_and_registers import BUILD_ORDER, DOCS

#: `AMENDMENT_A2`'s own file, so C91 can hold the hurdle against the document that fixed it.
AMENDMENT_A2 = DOCS / "AMENDMENT_A2_cost_hurdle_and_absent_terms.md"
AMENDMENT_A3 = DOCS / "AMENDMENT_A3_the_unchecked_sections.md"

#: Blockquote markers dropped and whitespace collapsed, so a figure the author wrapped across a
#: line is still one string. Annotations live inside `>` blocks and wrap where markdown wraps;
#: a bar that broke on rewrapping would be a bar people delete.
_WRAPPED = re.compile(r"^\s*>\s?", re.MULTILINE)


def _flat(text: str) -> str:
    return " ".join(_WRAPPED.sub("", text).split())

#: D4's session, reused rather than chosen again: the last DEV session on which every series
#: `US_CASH_BOOK` needs is published. Every figure below is measured on it.
MEASURED_ON = date(2014, 12, 24)

#: Predicted in this package's pre-commit §3 as P6, before the table was written, because the
#: rider that closed X1 left exactly that habit behind. The build order's row says "~20".
#: Seventeen at D7a; the six H.10 majors joined under DD168 (2026-09-26).
EXPECTED_PROFILES = 23
EXPECTED_REFUSALS = 6

#: §0.6. `gross ÷ net` on the one leg of `US_CASH_BOOK` that declares a neutrality.
GROSS_OVER_NET_BREAKEVEN = 133.8915

#: §0.4 and §0.9. The par proxy against the quoted convention at ten years, and the same number
#: in ladder rungs -- rungs a factor of two apart, so one rung is 1.0 in log₂.
CONVENTION_EFFECT_10Y = 1.132891
RUNG_FRACTION = 0.1800

#: §0.7b. §3.2's `half_spread × n_components` against the compositional sum, on the breakeven.
COMPOSITION_RATIO = 1.5

#: The same defect on §3.1's own butterfly row, where it does not even need two markets: a
#: 2s5s10s is `(+1, -2, +1)`, four units of notional across three components, and the table reads
#: *"Components: 3, Cost: 3 x"*. Found while writing C79's mutation, not predicted.
BUTTERFLY_RATIO = 4.0 / 3.0

#: §0.8. The two series D5 graded that the par-bond branch cannot reach, so they have a
#: half-spread and no cost per unit of risk.
NO_DURATION = ("DGS3MO", "DGS6MO")

#: Round-trip spread cost per unit of gross DV01, in basis points of yield, at `AS_QUOTED`.
#: Notional cancels out of this ratio, so these are properties of the instruments.
EXPECTED_COST_PER_DV01 = {
    "us_2y": 0.390625,
    "us_10y": 0.156250,
    "us_breakeven_5y": 0.472251,
}


def _dev_yields(stamp: date) -> dict[str, float]:
    """Every series published on `stamp`, in percent, read from the committed panel."""
    panel = load_daily(FitWindow.dev())
    index = panel.dates.index(stamp)
    return {
        name: value
        for name in panel.series
        if (value := panel.values[name][index]) is not None
    }


def _leg(leg_id: str) -> Leg:
    return next(leg for leg in US_CASH_BOOK.legs if leg.leg_id == leg_id)


def test_every_quoted_half_spread_is_a_dyadic_fraction_of_a_thirty_second() -> None:
    """C77. B77, DD75-DD76. The shape of the number, not its value.

    A quoting convention is a fraction of an increment. A calibration is a decimal. The failure
    this forecloses is the second arriving where the first was, under a comment still claiming a
    convention -- and `0.42` bp reads as plausible in a way `1/8 of a 32nd` cannot.

    The second half is DD76: a profile is a function of (market, bucket), so the two series that
    are the same note at the same point on the curve agree by construction rather than by two
    hands writing the same number twice.
    """
    assert THIRTY_SECOND_BP == 3.125, "a point is one per cent of par, so a 32nd is 3.125 bp"

    for series, profile in COST_OF.items():
        if profile.basis is not CostBasis.QUOTING_CONVENTION:
            continue
        fraction = profile.half_spread_bp / THIRTY_SECOND_BP
        scaled = fraction * 1024.0
        assert scaled == int(scaled), (series, fraction)
        assert int(scaled) & (int(scaled) - 1) == 0, (series, "not a power of two", fraction)
        assert 0.0 < fraction <= 1.0, (series, fraction)

    # The same note at the same point, quoted two ways, cannot disagree about what it costs.
    for zero, par in (("SVENY10", "DGS10"), ("SVENY02", "DGS2"), ("SVENY01", "DGS1")):
        assert COST_OF[zero].half_spread_bp == COST_OF[par].half_spread_bp, (zero, par)
        assert COST_OF[zero].bucket is COST_OF[par].bucket
        assert COST_OF[zero].market is COST_OF[par].market is Market.US_NOMINAL_TREASURY

    # The buckets are FR 2004B's, and the front end quotes in finer increments than the long end.
    assert bucket_of(0.25) is MaturityBucket.Y0_2
    assert bucket_of(2.0) is MaturityBucket.Y0_2
    assert bucket_of(3.0) is MaturityBucket.Y2_3
    assert bucket_of(6.0) is MaturityBucket.Y3_6
    assert bucket_of(7.0) is MaturityBucket.Y6_7
    assert bucket_of(11.0) is MaturityBucket.Y7_11
    assert bucket_of(30.0) is MaturityBucket.Y11_PLUS
    assert set(BUCKET_INCREMENT) == set(MaturityBucket)
    assert BUCKET_INCREMENT[MaturityBucket.Y0_2] < BUCKET_INCREMENT[MaturityBucket.Y11_PLUS]
    for bad in (0.0, -1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            bucket_of(bad)


def test_a_cost_cannot_be_recorded_here_as_a_measurement() -> None:
    """C78. B78, DD74. The build order says it twice in prose; the type says it once.

    §3.5: *"The cost numbers are calibrated assumptions from public sources, never measurements,
    and no package may describe them otherwise."* §6 lists *"a cost number reported as a
    measurement"* among the things that would make the plan wrong.

    `CostBasis` has three members and no fourth, so a profile claiming to be a measurement does
    not fail a check -- it fails to be constructible. That is `Direction`'s move at D2: the bug is
    not caught, it is made unrepresentable.
    """
    assert {member.name for member in CostBasis} == {
        "QUOTING_CONVENTION",
        "PUBLISHED_RESEARCH",
        "STATED_ASSUMPTION",
    }
    for member in CostBasis:
        assert "MEASUR" not in member.name.upper()
        assert "MEASUR" not in member.value.upper()

    for series, profile in COST_OF.items():
        assert isinstance(profile.basis, CostBasis), series
        assert profile.evidence.strip(), series
        assert profile.series == series

    # The three bases are all in use, so none of them is a branch no row exercises.
    assert {profile.basis for profile in COST_OF.values()} == set(CostBasis)

    # A basis that is not a CostBasis is refused at construction, string or not.
    with pytest.raises(TypeError, match="no fourth member"):
        CostProfile("X", Market.US_NOMINAL_TREASURY, MaturityBucket.Y0_2, 0.5, "MEASURED", "e")
    # A number with no evidence is a guess.
    with pytest.raises(ValueError, match="evidence"):
        CostProfile(
            "X", Market.US_NOMINAL_TREASURY, MaturityBucket.Y0_2, 0.5,
            CostBasis.STATED_ASSUMPTION, "   ",
        )
    # A bucket is absent if and only if the market has no maturity.
    with pytest.raises(ValueError, match="if and only if"):
        CostProfile("X", Market.FX_MAJOR, MaturityBucket.Y0_2, 0.5, CostBasis.STATED_ASSUMPTION, "e")
    with pytest.raises(ValueError, match="if and only if"):
        CostProfile("X", Market.US_TIPS, None, 0.5, CostBasis.PUBLISHED_RESEARCH, "e")


def test_cost_is_compositional_and_even_in_the_coefficients_sign() -> None:
    """C79. B79, DD77. §3.1 and §3.2 disagree, and §3.1 is the correct one.

    §3.1 prices a breakeven as *"1 × nominal + 1 × TIPS"* -- a sum over components with different
    per-component spreads. §3.2's single `half_spread × n_components` is that sum only when every
    component costs the same, and `US_BREAKEVEN_5Y` is the reference book's own counterexample.

    The absolute value is load-bearing rather than defensive: you pay the spread whichever way you
    trade, so cost is **even** in the coefficient while DV01 is **odd**. That is the whole reason a
    spread can be risk-neutral and cost twice an outright, and it is asserted rather than assumed.
    """
    breakeven = _leg("us_breakeven_5y").instrument
    compositional = instrument_half_spread(breakeven)
    section_3_2 = COST_OF["SVENY05"].half_spread_bp * len(breakeven.components)
    assert compositional / section_3_2 == COMPOSITION_RATIO
    assert compositional == COST_OF["SVENY05"].half_spread_bp + COST_OF["DFII5"].half_spread_bp

    # Even in the sign: flipping a coefficient changes the DV01 and not the cost. The neutrality
    # has to be declared -- `book.py` refuses a balanced difference that names no basis, which is
    # DD17 and is the first thing that happened when this mutation was written without one.
    flipped = Instrument(
        symbol="FLIPPED",
        kind=InstrumentKind.BREAKEVEN,
        currency=Currency.USD,
        tenor_years=5.0,
        components=(
            Component("SVENY05", -1.0, Currency.USD),
            Component("DFII5", 1.0, Currency.USD),
        ),
        neutrality=Neutrality.DV01,
    )
    assert instrument_half_spread(flipped) == compositional

    # And linear in the *size* of the coefficient, which is where §3.1's own table understates
    # itself a second time. Its butterfly row reads "Components: 3, Cost: 3 x", and a 2s5s10s
    # butterfly is `(+1, -2, +1)` -- four units of notional across three components. `book.py`
    # refuses a doubled OUTRIGHT (size lives in `Notional`, DD8), so the belly weight is the only
    # place a coefficient other than one can legitimately appear, and it appears in the example
    # the build order chose. Counting components rather than summing them is low by a third here,
    # before any difference in per-component spreads is reached.
    butterfly = Instrument(
        symbol="US_2S5S10S",
        kind=InstrumentKind.ZERO_YIELD,
        currency=Currency.USD,
        tenor_years=5.0,
        components=(
            Component("SVENY02", 1.0, Currency.USD),
            Component("SVENY05", -2.0, Currency.USD),
            Component("SVENY10", 1.0, Currency.USD),
        ),
        neutrality=Neutrality.DV01,
    )
    assert instrument_half_spread(butterfly) == math.fsum(
        (
            COST_OF["SVENY02"].half_spread_bp,
            2.0 * COST_OF["SVENY05"].half_spread_bp,
            COST_OF["SVENY10"].half_spread_bp,
        )
    )
    equal_spread = COST_OF["SVENY05"].half_spread_bp
    tickets = sum(abs(item.coefficient) for item in butterfly.components)
    assert tickets == 4.0 and len(butterfly.components) == 3
    assert (tickets * equal_spread) / (len(butterfly.components) * equal_spread) == BUTTERFLY_RATIO

    # An instrument that declares no series has nothing to price a spread on.
    option = next(leg for leg in REFERENCE_BOOK.legs if leg.leg_id == "us_10y_call").instrument
    with pytest.raises(Untradeable, match="declares no series"):
        instrument_half_spread(option)


def test_an_ungraded_term_is_absent_rather_than_zero_and_the_total_refuses() -> None:
    """C80. B80, DD78-DD79. A zero is a number and every sum downstream adds it.

    Two of §3.2's four terms have no graded input here: §3.3 names NY Fed FR 2004B for the impact
    term and `sources.py` has no row for it, and says of the financing term *"Fed H.15 and SOFR,
    both already graded"*, which is false -- H.15 is graded here for yields. That is X11.

    So the load-bearing assertion is not that a total is wrong. It is that **there is no total**,
    and that asking for one names every absent term rather than returning the sum of what happens
    to be present.
    """
    for leg in US_CASH_BOOK.legs:
        cost = annualised_cost(leg, 1.0)
        assert cost.present == (CostTerm.HALF_SPREAD.value,), leg.leg_id
        assert cost.financing is None, leg.leg_id
        assert len(cost.absent) == 3, (leg.leg_id, cost.absent)
        with pytest.raises(TermNotAvailable, match="three of|3 of"):
            cost.total

    # Financing is absent on every leg under the inputs D7a shipped, and the assertions below are
    # unchanged -- but **the reason stated here until 2026-09-16 was wrong by one word.** It read
    # *"the term no caller can supply, because the missing thing is a graded series and not an
    # argument"*, and at D7a the missing thing was **both**: `annualised_cost` had no parameter a
    # financing input could be passed to, which is the half of X11 D7b closed with
    # `costs.Financing`. What is missing now is only the graded series, which is what this
    # sentence always claimed and did not describe. C110 holds the other half.
    depth = MarketDepth(
        average_daily_volume=500e9, order_size=50e6, daily_volatility_bp=5.0, coefficient=1.0
    )
    supplied = annualised_cost(_leg("us_breakeven_5y"), 1.0, depth, Maintenance(4.0))
    assert supplied.impact is not None and supplied.roll is not None
    assert supplied.financing is None
    assert [term for term, _ in supplied.absent] == [CostTerm.FINANCING.value]
    assert "already graded" in dict(supplied.absent)[CostTerm.FINANCING.value]
    assert set(UNGRADED_TERMS) == {CostTerm.IMPACT, CostTerm.FINANCING}

    # `rolls_per_year = 0.0` is the held-to-horizon statement, and it is not the silent zero.
    held = annualised_cost(_leg("us_breakeven_5y"), 1.0, depth, Maintenance(0.0))
    assert held.roll == 0.0

    # The holding period has no default, and the shorter it is the more the spread term dominates.
    quarterly = annualised_cost(_leg("us_10y"), 0.25)
    annual = annualised_cost(_leg("us_10y"), 1.0)
    assert quarterly.half_spread == pytest.approx(4.0 * annual.half_spread)
    for bad in (0.0, -1.0, float("inf")):
        with pytest.raises(ValueError):
            annualised_cost(_leg("us_10y"), bad)

    # The sum itself works; it is the inputs that are missing. Built synthetically here because
    # no leg reaches four terms from **graded data** -- which is not the same as the sentence that
    # stood here until 2026-09-16, *"no leg in this repository can reach a complete set of four"*.
    # Since `costs.Financing` landed, a caller stating all three inputs reaches four on a real
    # leg, and C110 does exactly that. The absent terms are a fact about this repository's source
    # register, never about what the type can hold.
    complete = AnnualisedCost("synthetic", 1.0, 1.0, 2.0, 4.0, 8.0, ())
    assert complete.total == 15.0
    assert complete.present == tuple(term.value for term in CostTerm)


def test_a_term_the_leg_declared_unmodelled_at_d2_is_refused_on_that_leg() -> None:
    """C81. B81, DD80. The field was written three packages before the cost model existed.

    `reference.py`'s `_FUTURES_TO_CASH` carries `("financing", "delivery option", "roll")` on legs
    1 and 2, and DD12 said what it was for: *"any later package reporting a carry number on such a
    leg has to read it or it is reporting a number the data does not support."* This is that later
    package, and two of those three strings are cost terms.

    Read **from the leg**, never from a list here -- which is what the mutation checks: a leg that
    declares a different set gets a different refusal, and one that declares none gets none.
    """
    for leg_id in ("us_2y", "us_10y"):
        cost = annualised_cost(_leg(leg_id), 1.0, maintenance=Maintenance(4.0))
        refused = dict(cost.absent)
        assert CostTerm.ROLL.value in refused and "unmodelled" in refused[CostTerm.ROLL.value]
        assert "D2, DD12" in refused[CostTerm.ROLL.value]
        # Stated maintenance does not buy back a term the leg declared unmodelled.
        assert cost.roll is None

    # Nothing here lists which legs those are: a leg declaring all four loses all four.
    everything = Leg(
        "synthetic",
        _leg("us_10y").instrument,
        Direction.LONG,
        Notional(10e6, Currency.USD),
        ReExpression(
            original_kind=InstrumentKind.FUTURE,
            unmodelled=tuple(term.value for term in CostTerm),
        ),
    )
    stripped = annualised_cost(everything, 1.0)
    assert stripped.present == ()
    assert len(stripped.absent) == 4
    assert all("unmodelled" in reason for _, reason in stripped.absent)

    # And a leg declaring none of them loses only what this repository has not graded.
    plain = Leg("plain", _leg("us_10y").instrument, Direction.LONG, Notional(10e6, Currency.USD))
    assert annualised_cost(plain, 1.0).half_spread is not None


def test_cost_per_risk_divides_by_gross_dv01_and_refuses_a_leg_with_none() -> None:
    """C82. B82, DD81. `net_dv01` is a residual, and the reference book contains one.

    On `us_breakeven_5y` the gross is 49,629.33 and the net is 370.67 -- a factor of 133.89 -- and
    on a spread whose declared neutrality actually held the net would be exactly zero. Dividing a
    cost by that prices a well-hedged structure as infinitely expensive.

    `eurusd` has no rate sense at all, so it has no such denominator under either reading. It is
    refused by name rather than returned as an infinity, because an infinity propagates into every
    total that adds it -- D4's `UNPRICEABLE` reasoning, one ratio along.
    """
    yields = _dev_yields(MEASURED_ON)

    breakeven = _leg("us_breakeven_5y")
    gross = gross_dv01(breakeven, yields)
    net = leg_sensitivity(breakeven, yields).net_dv01
    assert round(gross / net, 4) == GROSS_OVER_NET_BREAKEVEN
    assert gross == pytest.approx(
        sum(abs(item.dv01) for item in leg_sensitivity(breakeven, yields).components)
    )

    # On an outright with one component the two readings coincide, which is why the trap is quiet.
    for leg_id in ("us_2y", "us_10y"):
        leg = _leg(leg_id)
        assert gross_dv01(leg, yields) == pytest.approx(
            abs(leg_sensitivity(leg, yields).net_dv01)
        )

    with pytest.raises(NoRateRisk, match="rate sense NONE"):
        gross_dv01(_leg("eurusd"), yields)
    with pytest.raises(NoRateRisk, match="expected shortfall"):
        cost_per_dv01(_leg("eurusd"), yields)

    for leg_id, expected in EXPECTED_COST_PER_DV01.items():
        assert round(cost_per_dv01(_leg(leg_id), yields), 6) == expected, leg_id

    # The notional cancels out of the ratio exactly, which is what makes it comparable across
    # candidate structures of different sizes -- the thing a stopping rule needs of it.
    resized = Leg(
        "resized", _leg("us_10y").instrument, Direction.SHORT, Notional(7e6, Currency.USD)
    )
    assert cost_per_dv01(resized, yields) == pytest.approx(cost_per_dv01(_leg("us_10y"), yields))

    # The front end costs more per unit of risk than the long end, which is the structural reason
    # front-end relative value dies net of costs. A consequence of the table, not an input to it.
    assert cost_per_dv01(_leg("us_2y"), yields) == pytest.approx(
        2.5 * cost_per_dv01(_leg("us_10y"), yields)
    )

    with pytest.raises(ValueError, match="multiplier"):
        cost_per_dv01(_leg("us_10y"), yields, multiplier=0.0)


def test_the_tips_profiles_respect_the_frbsf_papers_own_absolute_bound() -> None:
    """C83. B83, DD75. A check against the source, not against another number chosen here.

    FRBSF `wp2017-10` gives two statements: a seasoned-versus-on-the-run range of 30-100%, and an
    absolute bound -- the magnitude is *under a basis point*. The range is carried as a range, and
    the bound is what this bar holds, in **yield**, which is the unit the paper speaks in.

    That the conversion has to go through a duration is the point. A table written in yield would
    satisfy this bar by construction and would have thrown away the convention question with it.
    """
    yields = _dev_yields(MEASURED_ON)
    assert SEASONING_PENALTY == (1.30, 2.00)
    assert TIPS_ILLIQUIDITY == SEASONING_PENALTY[1], "the conservative end, and it is a bias"

    tips = [series for series, p in COST_OF.items() if p.market is Market.US_TIPS]
    assert sorted(tips) == ["DFII10", "DFII30", "DFII5"]
    for series in tips:
        profile = COST_OF[series]
        duration = modified_duration(series, yields[series])
        full_spread = 2.0 * profile.yield_equivalent_bp(duration)
        assert full_spread < FRBSF_ABSOLUTE_BOUND_BP, (series, full_spread)
        # And the TIPS row is dearer than the nominal at the same bucket, which is the whole claim.
        nominal = BUCKET_INCREMENT[profile.bucket] * THIRTY_SECOND_BP / 2.0
        assert profile.half_spread_bp == nominal * TIPS_ILLIQUIDITY

    with pytest.raises(ValueError, match="duration must be positive"):
        COST_OF["DFII5"].yield_equivalent_bp(0.0)


def test_the_ladder_has_a_convention_arm_and_it_is_a_fifth_of_a_rung() -> None:
    """C84. B84, DD82, carried item X5. Recomputed from the panel, not restated.

    §3.5 mandates 0.5× / 1× / 2× / 4×. X5 adds the duration convention as a second axis, and the
    arithmetic is why it had to be an axis: the rungs are a factor of two apart -- one unit in
    log₂ -- and the convention effect at ten years is 0.1800 of a rung. A ladder detects a flip
    between rungs, so no widening or narrowing of the cost multiplier could ever separate the
    convention's contribution from the multiplier's.

    The effect is the same ratio at every multiplier, which is what makes the two axes genuinely
    orthogonal rather than two names for one sweep.
    """
    yields = _dev_yields(MEASURED_ON)
    ladder = cost_ladder(_leg("us_10y"), yields)

    assert len(ladder.cells) == len(COST_MULTIPLIERS) * len(DurationConvention) == 8
    assert {cell.multiplier for cell in ladder.cells} == set(COST_MULTIPLIERS)
    assert {cell.convention for cell in ladder.cells} == set(DurationConvention)
    assert ladder.terms == (CostTerm.HALF_SPREAD.value,), "never assume all four terms"

    assert round(ladder.convention_effect, 6) == CONVENTION_EFFECT_10Y
    assert round(math.log2(ladder.convention_effect), 4) == RUNG_FRACTION

    # The arm is the same ratio at every rung, and the rungs are exactly §3.5's multipliers.
    for multiplier in COST_MULTIPLIERS:
        proxy = ladder.at(multiplier, DurationConvention.PAR_PROXY)
        quoted = ladder.at(multiplier, DurationConvention.AS_QUOTED)
        assert proxy / quoted == pytest.approx(ladder.convention_effect)
        assert quoted == pytest.approx(
            multiplier * ladder.at(1.0, DurationConvention.AS_QUOTED)
        )

    # The arm is derived from D4's own numbers, so a moved panel moves the bar.
    proxy_duration = 10.0 * ladder.at(1.0, DurationConvention.AS_QUOTED) / ladder.at(
        1.0, DurationConvention.PAR_PROXY
    )
    assert round(100.0 * (10.0 - proxy_duration) / 10.0, 3) == 11.730, "D4's §0.4 figure"

    with pytest.raises(KeyError):
        ladder.at(3.0, DurationConvention.AS_QUOTED)


def test_every_bias_carries_a_direction_and_an_unquantified_one_is_not_zero() -> None:
    """C85. B85, DD83, carried items X4 and X5. The count is returned so it cannot be dropped.

    X4's stated closure condition is that the bias sits *"on the cost object rather than in
    prose"* and carries its **direction**, because a direction is what turns an unknown into a
    bound: a cost known to be overstated gives a leg count that is a lower bound on the leg count
    the unbiased number would give.

    X5 says two conservative biases point the same way. There are **three** -- D4's DD52 left the
    annual-pay approximation as a magnitude with no direction, and it points the same way as the
    other two. So the answer here is the unflattering one, and `compounded_bias` returns the count
    of arms it could not include beside the product, because a single number would answer X5's
    concern with the arms that happen to be quantified and silently drop the ones that are not.
    """
    assert len(BIASES) == 5
    for bias_id, bias in BIASES.items():
        assert bias.bias_id == bias_id
        assert isinstance(bias.direction, BiasSense)
        assert isinstance(bias.effect, LegCountEffect)
        assert bias.source.strip()
        assert (bias.magnitude is None) == (bias.measured_on is None)
        if bias.magnitude is None:
            assert bias.signed_magnitude is None
        else:
            assert bias.signed_magnitude == int(bias.direction) * bias.magnitude

    # All of them conservative, which is the finding rather than the reassurance.
    # Four calibration biases run one way and the coverage bias runs the other (DD84,
    # `AMENDMENT_A2` §3). Read as a set, `{OVERSTATES_COST}` said the leg count was a lower
    # bound; the model's largest effect -- three of four terms absent -- is `MORE_LEGS`, and it
    # was missing from the register because the register held calibration and not coverage.
    calibration = {k: b for k, b in BIASES.items() if k != "absent_cost_terms"}
    assert {b.direction for b in calibration.values()} == {BiasSense.OVERSTATES_COST}
    assert {b.effect for b in calibration.values()} == {LegCountEffect.FEWER_LEGS}
    coverage = BIASES["absent_cost_terms"]
    assert coverage.direction is BiasSense.UNDERSTATES_COST
    assert coverage.effect is LegCountEffect.MORE_LEGS
    assert coverage.magnitude is None, "two of the three missing terms are X11; there is no number"
    assert {b.carried_item for b in BIASES.values()} == {"X4", "X5", "X11", None}

    # X4's magnitude is the ratio's, not the denominator's: 13.289% and not 11.730%.
    par_proxy = BIASES["par_proxy_duration"]
    assert par_proxy.magnitude == 0.13289
    assert par_proxy.conditional_on is DurationConvention.PAR_PROXY
    assert round(1.0 / (1.0 - 0.11730) - 1.0, 5) == par_proxy.magnitude

    # Unquantified is not zero, and writing it as zero is refused at construction.
    assert BIASES["indicative_bid_ask"].magnitude is None
    with pytest.raises(ValueError, match="unquantified"):
        Bias("z", "s", BiasSense.OVERSTATES_COST, 0.0, LegCountEffect.FEWER_LEGS, "src")
    with pytest.raises(ValueError, match="if and only if"):
        Bias(
            "z", "s", BiasSense.OVERSTATES_COST, 0.5, LegCountEffect.FEWER_LEGS, "src",
            measured_on=None,
        )

    # Two values, always. The default arm carries none of X4's, because D4 declined the proxy.
    quoted, unquantified = compounded_bias()
    # 2 before DD84. The coverage bias has no magnitude, so it moves the count and not the
    # product -- which is exactly what the two-value return exists to force a caller to see.
    assert unquantified == 3
    assert round(quoted, 6) == 1.001232, "the annual-pay bias alone, on the quoted convention"

    proxy, proxy_unquantified = compounded_bias(DurationConvention.PAR_PROXY)
    assert proxy_unquantified == unquantified
    assert proxy > quoted
    assert round(proxy, 6) == round(1.13289 * 1.001232, 6)


def test_the_front_end_d5_graded_has_a_half_spread_and_no_cost_per_risk() -> None:
    """C86. B86, DD75, DD81. Named, so D7b meets it here rather than in a traceback.

    `modified_duration` refuses `DGS3MO` and `DGS6MO`: the par-bond branch takes whole years,
    which is MEIP's signature restated rather than widened (DD52). So the two front-end names D5
    went and graded can be given a cost and cannot be given a cost per unit of risk, and a leg
    generator looking for a short leg meets that at the denominator rather than at the data.

    An equality over the whole table, not a spot check: a third series losing its duration would
    turn this red rather than joining the two quietly.
    """
    yields = _dev_yields(MEASURED_ON)
    without = []
    for series in sorted(TENOR_OF):
        assert series in COST_OF, series
        assert COST_OF[series].half_spread_bp > 0.0
        try:
            modified_duration(series, yields.get(series, 1.0))
        except Exception:  # noqa: BLE001 -- the identity of the refusal is C51's, not this bar's
            without.append(series)
    assert tuple(without) == NO_DURATION

    short = Leg(
        "front_end",
        Instrument(
            symbol="US_BILL_3M",
            kind=InstrumentKind.ZERO_YIELD,
            currency=Currency.USD,
            tenor_years=0.25,
            components=(Component("DGS3MO", 1.0, Currency.USD),),
        ),
        Direction.LONG,
        Notional(25e6, Currency.USD),
    )
    assert instrument_half_spread(short.instrument) == COST_OF["DGS3MO"].half_spread_bp
    assert annualised_cost(short, 1.0).half_spread is not None
    with pytest.raises(Exception, match="whole years"):
        cost_per_dv01(short, yields)


def test_every_graded_series_is_either_tradeable_or_refused_with_a_reason() -> None:
    """C87. B87, DD76. An exact partition, in `MODULES`' and `ENGINE_IMPORT_ROOTS`' shape.

    A floor would notice only shrinkage. An equality means a series added to `sources.py` turns
    this red until somebody decides whether it is a thing a desk trades or a thing computed from
    what a desk trades -- which is a decision, and the kind that otherwise gets made by whichever
    lookup happens to be reached first.

    Predicted before the table was written, as P6: seventeen priced and six refused against the
    build-order row's *"~20 instrument cost profiles"*, the difference being refusals rather than
    omissions.
    """
    priced, refused = set(COST_OF), set(UNPRICED_SERIES)
    assert len(priced) == EXPECTED_PROFILES
    assert len(refused) == EXPECTED_REFUSALS
    assert not priced & refused, sorted(priced & refused)
    assert priced | refused == set(SOURCES), {
        "graded and unplaced": sorted(set(SOURCES) - priced - refused),
        "placed and ungraded": sorted((priced | refused) - set(SOURCES)),
    }

    for series in refused:
        assert UNPRICED_SERIES[series].strip()
        with pytest.raises(Untradeable, match="carries no cost profile"):
            cost_of(series)
    for series in priced:
        assert cost_of(series) is COST_OF[series]

    # A series in neither is a decision nobody made, and is refused as one rather than defaulted.
    with pytest.raises(Untradeable, match="neither"):
        cost_of("SVENY99")
    # Every priced series has a market, and every market is used by at least one row.
    assert {profile.market for profile in COST_OF.values()} == set(Market)


# ---------------------------------------------------------------------------
# C89-C91: the rider that closed the audit's seven findings (`AMENDMENT_A2`)
# ---------------------------------------------------------------------------


def net_dv01_divisions(source: str) -> list[int]:
    """Line numbers where something is divided by an attribute named `net_dv01`.

    An AST walk rather than a text search, because `cost / leg_sensitivity(...).net_dv01` and
    `cost / sens.net_dv01` are the same defect spelled two ways and a grep for `/ net_dv01`
    finds neither. Precedent is `test_deskcraft_boundary.py`'s `os`-attribute scan, which walks
    for `ast.Attribute` on `ast.Name` for the same reason.
    """
    return [
        node.lineno
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.BinOp)
        and isinstance(node.op, ast.Div)
        and isinstance(node.right, ast.Attribute)
        and node.right.attr == "net_dv01"
    ]


def test_no_cost_is_ever_divided_by_net_dv01_anywhere_in_the_engine() -> None:
    """C89. B89, DD89. `AMENDMENT_A2` §6. DD81 was a docstring; this is the bar.

    **Why a repo-wide scan and not a unit test.** C82 above checks `gross == |net|` on the two
    outrights, and its own docstring names the hazard: on a leg with one component the two
    readings coincide, so the trap is quiet exactly where a new package would first meet it. A
    D7b unit test dividing by `net_dv01` on `us_10y` would pass and the defect would surface on
    `us_breakeven_5y` at **133.89x**, or on a spread whose declared neutrality holds as a
    division by zero.

    `LegSensitivity.net_dv01` stays and is not deprecated. It is the right number for the
    question D4 asks of it -- what a parallel move leaves on a leg declaring neutrality, 370.67
    per bp on $50m -- and that is a finding rather than a bug. What is banned is one use of it:
    as a denominator. The standing rule applies as it does to C10, a boundary hit is answered by
    changing the code and never by an exemption, so there is no allowlist here to add a line to.

    **Mutation:** a synthetic module containing each spelling, through the same walk.
    """
    offences = {
        path.name: lines
        for path in sorted(SRC.rglob("*.py"))
        if (lines := net_dv01_divisions(path.read_text(encoding="utf-8")))
    }
    assert not offences, (
        "cost divided by a residual: net_dv01 is 133.89x gross on us_breakeven_5y, 0/0 on "
        f"eurusd, and exactly zero on a spread whose neutrality holds (DD81). {offences}"
    )

    mutant = (
        "def f(cost, sens):\n"
        "    return cost / sens.net_dv01\n"
        "def g(cost, leg, ys):\n"
        "    return cost / leg_sensitivity(leg, ys).net_dv01\n"
    )
    assert net_dv01_divisions(mutant) == [2, 4]
    # Reading it is not dividing by it, and the property itself is untouched.
    assert net_dv01_divisions("x = sens.net_dv01\ny = sens.net_dv01 * 2\n") == []


def test_the_build_orders_annotations_still_say_what_the_module_computes() -> None:
    """C90. B90, DD90. `AMENDMENT_A2` §9. Document and module, held at equality.

    D7a annotated four of §3's five subsections rather than rewriting them, on D4's precedent:
    what executes is the module, and the commissioning text stays as written so the correction
    reads as a difference. The annotations carry **numbers** -- and nothing held them to the
    module that produced them, so the module could move and §3's correction would quietly become
    wrong. That is the failure mode the annotations exist to prevent, restored one level up.

    Every figure below is **recomputed here** and then looked for in the document, in the shape
    the document renders it. This is deliberately brittle in the ordinary way: reformatting the
    table breaks the bar. That is the intended cost of an annotation being load-bearing.

    `AMENDMENT_A2` §7's arithmetic on §1's evaluation count is held the same way -- six greedy
    rounds over ~300 structures is 1,785, and H9's predicted three or four legs is 897 or 1,194,
    so the plan carried two values for a number that reaches D15's Deflated Sharpe.
    """
    order = _flat(_read(BUILD_ORDER))
    yields = _dev_yields(MEASURED_ON)

    # §3.2, defect 2: `half_spread x n_components` against the compositional sum, on the breakeven.
    breakeven = _leg("us_breakeven_5y")
    notional = breakeven.notional.amount
    compositional = 2.0 * instrument_half_spread(breakeven.instrument) * 1e-4 * notional
    as_written = (
        2.0
        * cost_of(breakeven.instrument.components[0].series).half_spread_bp
        * len(breakeven.instrument.components)
        * 1e-4
        * notional
    )
    assert compositional / as_written == pytest.approx(COMPOSITION_RATIO)
    assert f"${as_written:,.2f} against ${compositional:,.2f}" in order
    assert f"**low by {round(100.0 * (COMPOSITION_RATIO - 1.0))}%**" in order

    # §3.1, the row nothing predicted: a 2s5s10s is four units of notional across three names.
    assert BUTTERFLY_RATIO == 4.0 / 3.0
    assert "Cost is `4 ×`, not the `3 ×` written" in order

    # §3.5, X5's arm: the convention effect as a fraction of a rung, and X4's restated figure.
    ladder = cost_ladder(_leg("us_10y"), yields)
    assert f"**{100.0 * BIASES['par_proxy_duration'].magnitude:.3f}%**" in order
    assert f"**{math.log2(ladder.convention_effect):.2f} of a single rung**" in order
    assert f"effect at ten years is {ladder.convention_effect:.6f}" in _flat(
        _read(SRC / "deskcraft" / "costs.py")
    )

    # §1, the evaluation count: six rounds is the cap H9 predicts against.
    def greedy(rounds: int) -> int:
        return sum(300 - taken for taken in range(rounds))

    assert f"is **{greedy(6):,}**" in order
    assert f"it is **{greedy(3):,} or {greedy(4):,}**" in order


def test_the_cost_hurdle_is_fixed_and_is_not_a_degree_of_freedom() -> None:
    """C91. B91, DD85-DD87. `AMENDMENT_A2` §2. The number §1.3 said §3 fixed, and §3 did not.

    **The defect this closes.** Build order §1.3: *"Each addition must clear a cost hurdle fixed
    in advance (§3)."* §3's five subsections fix no hurdle. §1.4 then makes the hurdle identical
    to the leg count, and §5's **H9** predicts that count -- scored by **D7b**, which is the
    package that would have chosen the hurdle, with the structures in front of it. §6 forbids
    precisely this one flag over (*"a flag threshold set after seeing which legs it fires on"*)
    and said nothing here.

    **Why the value is 1.0 and not a judgement call.** Selecting at hurdle `h` against cost `c`
    is the same function as selecting at `1.0` against `h * c`, and `COST_MULTIPLIERS` already
    runs the whole selection at four scalings. Any other value is a rung of a ladder the rule
    already reports, under a second name free to move late. The identity is asserted here rather
    than argued, at every rung, on the one term that exists.

    **And the ladder is already a holding-period ladder**, which is why `HURDLE_HOLDING_YEARS`
    is not a second free parameter: `m * cost(1.0)` equals `cost(1.0 / m)` to the last bit, so
    the four rungs span 2y / 1y / 0.5y / 0.25y. **That identity is a property of a one-term cost
    model** -- annualised financing is constant in the holding period -- so closing X11 breaks
    it, and the assertion below is what will notice.
    """
    assert COST_HURDLE == 1.0
    assert HURDLE_HOLDING_YEARS == 1.0

    leg = _leg("us_10y")
    central = annualised_cost(leg, HURDLE_HOLDING_YEARS).half_spread
    for multiplier in COST_MULTIPLIERS:
        scaled = annualised_cost(leg, HURDLE_HOLDING_YEARS / multiplier)
        assert scaled.half_spread == multiplier * central, multiplier
        # A multiplier is a rung, so a hurdle of `m` decides what rung `m` decides at hurdle 1.
        assert COST_HURDLE * scaled.half_spread == multiplier * central

    # The identity holds on the term that exists, and three of four do not. When X11 closes,
    # financing arrives as a term that is constant in the holding period, and this stops being
    # one axis -- which is the obligation CARRIED_ITEMS §X11 carries.
    absent = {term for term, _ in annualised_cost(leg, HURDLE_HOLDING_YEARS).absent}
    assert absent == {"financing", "impact", "roll"}, absent

    # The hurdle's denominator (DD86): the spread term, because there is no total to divide.
    with pytest.raises(TermNotAvailable, match="four cost terms absent"):
        annualised_cost(leg, HURDLE_HOLDING_YEARS).total
    assert cost_per_dv01(leg, _dev_yields(MEASURED_ON)) == EXPECTED_COST_PER_DV01["us_10y"]

    # And the value is fixed in a document a package cannot quietly disagree with.
    amendment = _read(AMENDMENT_A2)
    assert "`COST_HURDLE = 1.0`" in amendment
    assert "COST_HURDLE = 1.0" in _flat(_read(BUILD_ORDER))


def module_names(source: str) -> set[str]:
    """Every bare name, attribute and imported name a module mentions, by AST rather than text.

    A text scan would count the token inside a docstring that talks *about* the hurdle. This
    counts only the places a value could actually be read from.
    """
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.ImportFrom):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            continue
    return names


def hurdle_readers_without_the_ladder(root: Path) -> list[str]:
    """Modules reading `COST_HURDLE` and not `COST_MULTIPLIERS`. `AMENDMENT_A3` §2.2."""
    out = []
    for path in sorted(root.rglob("*.py")):
        names = module_names(_read(path))
        if "COST_HURDLE" in names and "COST_MULTIPLIERS" not in names:
            out.append(path.relative_to(root).as_posix())
    return out


def test_a_module_reading_the_cost_hurdle_also_reads_the_ladder(tmp_path: Path) -> None:
    """C92. B92, DD91. `AMENDMENT_A3` §2, and X12.

    `COST_HURDLE = 1.0` removes a parameter rather than choosing one -- selecting at hurdle `h`
    against cost `c` is the same function as selecting at `1.0` against `h*c`, and
    `COST_MULTIPLIERS` already runs the whole selection at four scalings. **That argument holds
    only while the ladder is reported.** A selector that reads the hurdle, compares one cost
    against it and publishes one cell has a free parameter again under a different name.

    `AMENDMENT_A2` §12.5 saw the gap and said the bar *"belongs in D7b's pre-commit and this
    document cannot write it"*. That was wrong. `C76` and `C34` are both bars written by one
    package that arm immediately and bind when a later one lands, and this is the same shape:
    **the reader census is an equality**, so the bar is armed and true today rather than
    vacuously passing, and the day D7b imports the hurdle alone the suite turns red before its
    pre-commit is written.

    **What this cannot do, and is why X12 exists:** it proves a module *mentions* the ladder,
    never that it *sweeps* it. That residue is not closeable by a bar over a package that does
    not exist.

    **Mutation:** a module reading the hurdle alone is reported, and one reading both is not.
    """
    assert not hurdle_readers_without_the_ladder(SRC), hurdle_readers_without_the_ladder(SRC)

    # The census is an equality, and it moved at D7b exactly as written: `costs.py`, which
    # defines both, and `generator.py`, the selector this bar was armed against. A bar that
    # passed because nothing read it would be worth nothing, and for one landing it did not.
    readers = [
        path.relative_to(SRC).as_posix()
        for path in sorted(SRC.rglob("*.py"))
        if "COST_HURDLE" in module_names(_read(path))
    ]
    assert readers == ["deskcraft/costs.py", "deskcraft/generator.py"]
    assert COST_HURDLE == 1.0 and len(COST_MULTIPLIERS) == 4

    one_cell = '''from deskcraft.costs import COST_HURDLE


def keep(cost: float) -> bool:
    return cost < COST_HURDLE
'''
    the_ladder = '''from deskcraft.costs import COST_HURDLE, COST_MULTIPLIERS


def ladder(cost: float) -> list[bool]:
    return [cost * m < COST_HURDLE for m in COST_MULTIPLIERS]
'''
    selector = tmp_path / "selector.py"
    selector.write_text(one_cell, encoding="utf-8")
    assert hurdle_readers_without_the_ladder(tmp_path) == ["selector.py"]

    selector.write_text(the_ladder, encoding="utf-8")
    assert not hurdle_readers_without_the_ladder(tmp_path)


def test_the_third_amendment_is_on_disk_and_says_what_it_closed() -> None:
    """C95. B95, DD92. `AMENDMENT_A3` §11.

    A2 §12.5 left two statements open. This holds that the document closing them exists and
    still carries the two measurements the restatement rests on, recomputed here.
    """
    amendment = _flat(_read(AMENDMENT_A3))
    assert f"**{len(US_CASH_BOOK.leg_ids)}** — the priceable book" in amendment
    assert f"{100.0 * 3.0 / len(US_CASH_BOOK.leg_ids):.1f}% of maximum" in amendment
    assert "1 of 15" in amendment and "us_2y` ≡ `eurusd" in amendment


# ---------------------------------------------------------------------------
# C102: how each module reads the ladder, rather than whether it names it
# ---------------------------------------------------------------------------

#: Every module under `src/` that reaches the ladder, and what it does with it. An equality, not a
#: floor: a module appearing here with a new disposition, or a module arriving that is not here at
#: all, is the event this bar exists for. Today exactly one module reaches it and it sweeps.
LADDER_READERS = {
    "deskcraft/costs.py": ("sweeps the ladder",),
    #: D7b, the landing C102 was armed for. `selection_ladder` runs the whole selection at
    #: every rung and hands back eight `Selection`s, so a leg count cannot be quoted without
    #: the cell it came from -- carried item X12, discharged.
    "deskcraft/generator.py": ("sweeps the ladder",),
}

#: The three things a module can do with `COST_MULTIPLIERS` and `Ladder.at`. `d7a` §3.5 and X12
#: both said no bar could tell them apart. Both were wrong, and neither had been tried.
_SWEEPS, _PICKS, _ONE_CELL = "sweeps the ladder", "picks a rung", "reports one cell"


def ladder_disposition(source: str) -> tuple[str, ...]:
    """What `source` does with the ladder, by AST rather than by whether it says the name.

    Defining the tuple is not reading it, so the `Store` on `COST_MULTIPLIERS = (...)` and the
    string inside `__all__` are both invisible here -- otherwise the module that owns the ladder
    would be indistinguishable from a selector that picks one rung out of it.
    """
    tree = ast.parse(source)
    found: set[str] = set()

    reads = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and node.id == "COST_MULTIPLIERS"
        and isinstance(node.ctx, ast.Load)
    ]
    swept = {
        id(node.iter)
        for node in ast.walk(tree)
        if isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension))
    }
    if any(id(node) in swept for node in reads):
        found.add(_SWEEPS)
    if any(id(node) not in swept for node in reads):
        found.add(_PICKS)

    # X5's other axis. A function that reaches into the ladder once and hands that scalar back has
    # reported a point estimate, whatever it named the variable. `convention_effect` reads two and
    # divides, so it is a ratio and not a cell.
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        cells = [
            inner
            for inner in ast.walk(node)
            if isinstance(inner, ast.Call)
            and isinstance(inner.func, ast.Attribute)
            and inner.func.attr == "at"
        ]
        if len(cells) != 1:
            continue
        if any(
            ret.value is not None and ret.value is cells[0]
            for ret in ast.walk(node)
            if isinstance(ret, ast.Return)
        ):
            found.add(_ONE_CELL)

    return tuple(sorted(found))


def ladder_readers(root: Path) -> dict[str, tuple[str, ...]]:
    """Every module under `root` that reaches the ladder at all, and how."""
    return {
        path.relative_to(root).as_posix(): disposition
        for path in sorted(root.rglob("*.py"))
        if (disposition := ladder_disposition(_read(path)))
    }


def test_a_module_that_reads_the_ladder_sweeps_it(tmp_path: Path) -> None:
    """C102. B102, DD109. `RIDER_the_impossibility_claims_X16_does_not_cover.md` §2.

    Two landed documents said this bar could not exist, and neither had tried to write it.

    `d7a` §3.5: *"a caller taking the 1x `AS_QUOTED` cell and reporting it alone has defeated the
    whole apparatus, and no bar can stop that -- it is a reading discipline"*. The sentence's own
    word is **caller**, and a caller is what an AST scanner reaches. The repository was already
    banning `net_dv01` as a divisor the same way when that was written.

    X12: *"a selector may import `COST_MULTIPLIERS` and evaluate one element, and no bar over a
    package that does not exist can catch that"* -- three paragraphs below X12's own *"a bar
    written by one package can arm now and bind when a later one lands"*, with C76 and C34 named
    as standing proof of it.

    **This does not forbid a single rung.** X12 grants D7b a documented one-rung decision, and a
    bar that refused it would overrule the discharge the register offers. `LADDER_READERS` is an
    equality, so a module that starts picking a rung turns the suite red until the rung and its
    reason are written into the census -- which is the decision X12 asks to be fixed in advance.
    C99's shape: refuse the silence, not the act.

    **Mutation:** the two planted selectors the documents describe, the sweeping one they allow,
    and the two-cell ratio that must stay invisible.
    """
    assert ladder_readers(SRC) == LADDER_READERS, ladder_readers(SRC)
    assert len(COST_MULTIPLIERS) == 4 and len(cost_ladder(_leg("us_10y"), _dev_yields(
        MEASURED_ON
    )).cells) == 8, "the census is about a ladder that is still eight cells"

    picks = tmp_path / "picks.py"
    picks.write_text(
        "from deskcraft.costs import COST_HURDLE, COST_MULTIPLIERS\n\n\n"
        "def stopping_rule(costs: list[float]) -> list[float]:\n"
        "    rung = COST_MULTIPLIERS[1]\n"
        "    return [c for c in costs if c * rung < COST_HURDLE]\n",
        encoding="utf-8",
    )
    assert ladder_readers(tmp_path) == {"picks.py": (_PICKS,)}

    picks.write_text(
        "from deskcraft.costs import COST_HURDLE, COST_MULTIPLIERS\n\n\n"
        "def stopping_rule(costs: list[float]) -> dict[float, list[float]]:\n"
        "    return {m: [c for c in costs if c * m < COST_HURDLE] for m in COST_MULTIPLIERS}\n",
        encoding="utf-8",
    )
    assert ladder_readers(tmp_path) == {"picks.py": (_SWEEPS,)}

    picks.write_text(
        "def headline(ladder: object) -> float:\n"
        "    return ladder.at(1.0, DurationConvention.AS_QUOTED)\n",
        encoding="utf-8",
    )
    assert ladder_readers(tmp_path) == {"picks.py": (_ONE_CELL,)}

    picks.write_text(
        "def effect(ladder: object) -> float:\n"
        "    return ladder.at(1.0, DurationConvention.PAR_PROXY) / ladder.at(\n"
        "        1.0, DurationConvention.AS_QUOTED\n"
        "    )\n",
        encoding="utf-8",
    )
    assert ladder_readers(tmp_path) == {}, "a ratio over two cells is not a point estimate"
#: `cost_per_dv01`'s return, as it stood until 2026-09-16: the multiplier applied to the spread
#: term in place. Kept as text rather than as a description, because C114's whole subject is what
#: the source says and a paraphrase of it could not be run.
_MULTIPLIER_INSIDE = """def cost_per_dv01(leg, yields, convention=None, multiplier=1.0):
    spread = multiplier * 2.0 * instrument_half_spread(leg.instrument) * BASIS_POINT
    return spread * leg.notional.amount / gross_dv01(leg, yields, convention)
"""

_MULTIPLIER_OUTSIDE = """def cost_per_dv01(leg, yields, convention=None, multiplier=1.0):
    spread = 2.0 * instrument_half_spread(leg.instrument) * BASIS_POINT
    return multiplier * (
        spread * leg.notional.amount / gross_dv01(leg, yields, convention)
    )
"""


def multiplier_is_outermost(source: str) -> bool:
    """True when every `return` of `cost_per_dv01` is `multiplier * <anything>`.

    Read from the syntax rather than from the arithmetic on purpose. The arithmetic is equal under
    both placements while one term is graded -- that is the whole finding -- so a numeric bar
    cannot see the difference and this one can.
    """
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.FunctionDef) and node.name == "cost_per_dv01":
            returns = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
            if not returns:
                return False
            return all(
                isinstance(r.value, ast.BinOp)
                and isinstance(r.value.op, ast.Mult)
                and isinstance(r.value.left, ast.Name)
                and r.value.left.id == "multiplier"
                for r in returns
            )
    raise AssertionError("cost_per_dv01 is not defined in this source")


def test_a_cost_multiplier_scales_the_total_and_never_one_term() -> None:
    """C113. B113, DD112. The ladder's own axis, held as an equality over the whole universe.

    `COST_MULTIPLIERS` had **two implementations** in this tree until 2026-09-16, and they scaled
    different things: `cost_per_dv01` applied the rung to the spread term, and `generator.select`
    applied it to the whole cost (`multiplier * cost`, on a cost computed at the default). While
    the spread is the only graded term those are the same number -- and not merely close, which is
    what this bar measures: **bit-identical at every one of the 3,696 cells**.

    They stop being the same number the moment X11's second term is graded. Written `s + f`, the
    two readings are `m*(s + f)` and `m*s + f`; at 4x with a second term the size of the spread
    they differ by a factor of **3.38**, and run through the real selector they choose different
    books at three of twenty-eight swept cells -- differences of one leg, which is H9's subject.
    C115 measures that half.

    **So the equality is the guard.** DD112 fixes the scope to the total, and this bar holds the
    consequence: a second term added to `cost_per_dv01` without the multiplication moving outside
    it turns this red. That is C99's shape -- the act is allowed and the silence is not. D8 grades
    the term; D8 does not get to grade it quietly.

    **Mutation:** the second term added outside the multiplier, where the equality must fail.
    """
    yields = _dev_yields(MEASURED_ON)
    cells = 0
    for leg in candidate_legs():
        for convention in DurationConvention:
            base = cost_per_dv01(leg, yields, convention)
            for multiplier in COST_MULTIPLIERS:
                cells += 1
                assert cost_per_dv01(leg, yields, convention, multiplier) == multiplier * base, (
                    leg.leg_id,
                    convention,
                    multiplier,
                )
    assert cells == 3696, cells

    # The mutation. A second cost term is modelled at half the spread, and the two placements are
    # compared against the property this bar asserts of the real function.
    leg = candidate_legs()[0]
    spread = cost_per_dv01(leg, yields, DurationConvention.AS_QUOTED)
    extra = 0.5 * spread

    def scaled(multiplier: float) -> float:
        return multiplier * (spread + extra)  # DD112: the rung scales the total

    def leaky(multiplier: float) -> float:
        return multiplier * spread + extra  # the term added outside the multiplier

    assert all(scaled(m) == m * scaled(1.0) for m in COST_MULTIPLIERS)
    assert [m for m in COST_MULTIPLIERS if leaky(m) != m * leaky(1.0)] == [0.5, 2.0, 4.0]


def test_the_multiplier_is_the_outermost_factor_of_the_cost(tmp_path: Path) -> None:
    """C114. B114, DD112. The scope made structural, because a docstring is a sign next to a hole.

    C113 holds the equality and would go red *after* a second term landed on the wrong side of the
    multiplication. This holds the placement that makes landing it on the wrong side awkward
    rather than natural: the multiplier is the **outermost factor of the return value**, so a term
    added inside the ratio is scaled by construction and a term added outside sits on the same
    line as the multiplier, in the diff, next to the decision.

    The phrase is `RIDER_the_impossibility_claims_X16_does_not_cover.md`'s, turned on this
    package: a docstring saying *the multiplier scales the total* is a sign next to a hole. The
    hole is filled by reading the syntax.

    **Mutation, and the prediction it scores.** The pre-2026-09-16 text is kept verbatim above and
    the scanner is run against it. P5 predicted this bar would have caught the defect; a bar that
    claims it would have caught something has to be shown failing on the thing it claims to catch,
    or the claim is the `X16` class again.
    """
    assert multiplier_is_outermost(_read(SRC / "deskcraft" / "costs.py"))

    # The mutation: the placement this repository had until DD112, and the one it has now.
    assert not multiplier_is_outermost(_MULTIPLIER_INSIDE)
    assert multiplier_is_outermost(_MULTIPLIER_OUTSIDE)

    # A function with no return at all is not vacuously compliant.
    empty = "def cost_per_dv01(leg, yields, convention=None, multiplier=1.0):\n    pass\n"
    assert not multiplier_is_outermost(empty)

    # And the scanner is looking at this function rather than at any multiplication in the file.
    decoy = tmp_path / "decoy.py"
    decoy.write_text(
        "def other(multiplier, cost):\n"
        "    return multiplier * cost\n\n\n"
        "def cost_per_dv01(leg, yields, convention=None, multiplier=1.0):\n"
        "    return cost(leg) * multiplier\n",
        encoding="utf-8",
    )
    assert not multiplier_is_outermost(_read(decoy)), (
        "`cost * multiplier` is the same number and not the same statement: the guard is that the "
        "multiplier is the outermost *left* factor, so what follows it is the whole cost"
    )
