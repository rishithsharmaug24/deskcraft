"""D7b -- the leg generator and the cost-aware stopping rule. Bars C103-C112, decision DD110.

Every bar carries a mutation, in the inherited discipline: a state is built in which the property
would be false, and the scanner is shown to say so.

**What this file is about, in one sentence.** §1's stopping rule compares a dimensionless gain in
view fidelity against a cost quoted in basis points of yield, and until `VIEW_MOVE_BP` is stated
that comparison has no units -- which is `AMENDMENT_A2` §2's own finding about `COST_HURDLE`, one
parameter over, missed by the document that made it and by the three that read it after.
"""

from __future__ import annotations

import ast
import math
from datetime import date

import pytest

from deskcraft import generator
from deskcraft.book import (
    Component,
    Currency,
    Direction,
    Instrument,
    InstrumentKind,
    Leg,
    Neutrality,
    Notional,
    Structure,
)
from deskcraft.costs import (
    COST_HURDLE,
    COST_MULTIPLIERS,
    COST_OF,
    DurationConvention,
    Financing,
    Maintenance,
    MarketDepth,
    TermNotAvailable,
    annualised_cost,
    cost_per_dv01,
)
from deskcraft.factors import FACTOR_SERIES, Factor, build_basis
from deskcraft.generator import (
    CANDIDATE_SERIES,
    NoCandidate,
    candidate_legs,
    enumerate_universe,
    select,
    selection_ladder,
    unit_risk_exposure,
)
from deskcraft.panel import FitWindow, load_daily
from deskcraft.sensitivity import TENOR_OF, UnknownConvention, leg_sensitivity
from deskcraft.views import REFERENCE_VIEW, Move, View

from test_deskcraft_boundary import REPO_ROOT, _read

SRC = REPO_ROOT / "src"

#: The panel date D7a's bars already measure at, so the two packages' numbers are comparable.
MEASURED_ON = date(2014, 12, 24)

#: What §4's row says the universe is, and what the rule in the pre-commit's §1.1 produces. The
#: gap is recorded rather than tuned away: "~300" is a plan number and 231 is a measured one.
UNIVERSE = 231
OUTRIGHTS, SPREADS, BUTTERFLIES = 11, 55, 165


@pytest.fixture(scope="module")
def yields() -> dict[str, float]:
    panel = load_daily(FitWindow.dev())
    row = panel.dates.index(MEASURED_ON)
    return {
        series: value
        for series in panel.series
        if (value := panel.values[series][row]) is not None
    }


@pytest.fixture(scope="module")
def basis():
    return build_basis()


@pytest.fixture(scope="module")
def ladder(basis, yields):
    return selection_ladder(REFERENCE_VIEW, basis, yields)


def test_the_candidate_pool_is_the_intersection_of_the_two_registers() -> None:
    """C103. B103, DD110. The universe is derived from the registers, never listed.

    A structure is a candidate when every series it names has a cost profile **and** a direction
    in the factor basis. Neither register alone is enough: `COST_OF` carries six series the basis
    cannot see (twelve since DD168) and `FACTOR_SERIES` carries two nothing prices, so a list written by hand would be
    a third place for the truth to live and the first to go stale.

    The counts are equalities rather than floors, which is D7a's disposition for `COST_OF` as an
    exact partition of `sources.SOURCES`: a series added to either register lands here, and the
    author restates the count in a diff instead of discovering it in a number nobody checked.

    **Mutation:** the derivation is re-run against perturbed registers, so what is exercised is the
    rule and not a second copy of the expected answer.
    """
    assert CANDIDATE_SERIES == tuple(s for s in FACTOR_SERIES if s in COST_OF)
    assert len(CANDIDATE_SERIES) == 11
    assert set(CANDIDATE_SERIES) == {
        "SVENY01", "SVENY02", "SVENY03", "SVENY05", "SVENY07", "SVENY10", "SVENY20", "SVENY30",
        "DFII5", "DFII10", "DFII30",
    }

    # DD168 added six priced currencies and the pool above did not move: they are hedge
    # instruments with no direction in the basis, so no view can select them (DD120, DD138).
    assert set(COST_OF) - set(FACTOR_SERIES) == {
        "DEXUSEU", "DGS1", "DGS2", "DGS10", "DGS3MO", "DGS6MO",
        "DEXJPUS", "DEXUSUK", "DEXCAUS", "DEXSZUS", "DEXCHUS", "DEXMXUS",
    }
    assert set(FACTOR_SERIES) - set(COST_OF) == {"GZ_SPREAD", "DE_ZERO_10Y"}

    universe = enumerate_universe()
    assert len(universe) == UNIVERSE == OUTRIGHTS + SPREADS + BUTTERFLIES
    families = [instrument.structure for instrument in universe]
    assert families.count(Structure.OUTRIGHT) == OUTRIGHTS == len(CANDIDATE_SERIES)
    assert families.count(Structure.SPREAD) == SPREADS
    assert families.count(Structure.BUTTERFLY) == BUTTERFLIES
    assert not [f for f in families if f is Structure.BASKET]
    assert len({instrument.symbol for instrument in universe}) == UNIVERSE
    assert len(candidate_legs()) == 2 * UNIVERSE == 462

    def pool(priced: set[str], faced: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(series for series in faced if series in priced)

    assert "T10YIE" not in pool(set(COST_OF), FACTOR_SERIES + ("T10YIE",))
    assert "DGS2" not in pool(set(COST_OF), FACTOR_SERIES)
    assert "DGS2" in pool(set(COST_OF), FACTOR_SERIES + ("DGS2",))


def test_every_candidate_prices_and_the_front_end_is_excluded_by_the_rule(yields) -> None:
    """C104. B104, DD110. D7a's open question, answered one step earlier than it expected.

    D7a closed saying *"the two front-end series D5 went and graded, `DGS3MO` and `DGS6MO`, have a
    half-spread and no computable duration, so they have no cost per risk -- D7b meets that at the
    denominator rather than at the data."* **It is met at neither.** They are not in
    `FACTOR_SERIES`, so the pool rule drops them before any denominator is formed, and the
    exclusion is a property of the rule rather than a special case anybody wrote.

    Both halves are asserted, because the two facts are independent: the rule excludes them today,
    and the denominator is what would refuse them if the basis were ever widened.

    **Mutation:** a structure built on `DGS3MO` refuses, by name, at the duration.
    """
    every = candidate_legs()
    assert len(every) == 462
    for leg in every:
        assert cost_per_dv01(leg, yields) > 0.0
        assert leg_sensitivity(leg, yields).components

    for series in ("DGS3MO", "DGS6MO"):
        assert series in COST_OF and series not in FACTOR_SERIES
        assert series not in CANDIDATE_SERIES
        front = Leg(
            leg_id=f"front_{series.lower()}",
            instrument=Instrument(
                symbol=f"OUT_{series}",
                kind=InstrumentKind.ZERO_YIELD,
                currency=Currency.USD,
                tenor_years=TENOR_OF[series],
                components=(Component(series, 1.0, Currency.USD),),
            ),
            direction=Direction.LONG,
            notional=Notional(generator.UNIT_NOTIONAL, Currency.USD),
        )
        with pytest.raises(UnknownConvention) as caught:
            cost_per_dv01(front, yields)
        assert series in str(caught.value)

    # `DEXUSEU` is the third priced series with no cost per risk, refused for a different reason:
    # no rate sense at all, which is D7a's `NoRateRisk` and not a convention.
    assert "DEXUSEU" in COST_OF and "DEXUSEU" not in CANDIDATE_SERIES


def test_the_ladder_carries_eight_selections_and_the_leg_count_flips(ladder) -> None:
    """C105. B105, DD110. Carried item X12, and §3.5's own trigger firing.

    X12: *"`COST_HURDLE = 1.0` removes a parameter only while the ladder is reported, and nothing
    requires D7b to report it."* This is the report. `selection_ladder` returns a whole
    `Selection` at every cell -- not a count, a selection -- and each is keyed by its `Cell`, so a
    leg count cannot travel without the rung it was computed at.

    **And the flip fires.** `COST_MULTIPLIERS`' own docstring: *"a flip between 1x and 2x means the
    honest headline is that the result is a statement about costs rather than about structure."* It
    flips, on that exact pair, on this tree. The headline is therefore the one §3.5 pre-wrote, and
    this bar records it as measured rather than as possible.

    **The convention axis changes the composition, not only the count**, which is more than X5
    claimed for it: at 0.5x the two conventions select disjoint books.

    **Mutation:** a ladder of one cell, and a ladder whose cells agree, are both distinguished.
    """
    assert len(ladder.cells) == len(COST_MULTIPLIERS) * len(DurationConvention) == 8
    assert {cell.cell.multiplier for cell in ladder.cells} == set(COST_MULTIPLIERS)
    assert {cell.cell.convention for cell in ladder.cells} == set(DurationConvention)
    assert ladder.terms == ("half_spread",)

    quoted, proxy = DurationConvention.AS_QUOTED, DurationConvention.PAR_PROXY
    counts = {(s.cell.convention, s.cell.multiplier): len(s) for s in ladder.cells}
    assert [counts[(quoted, m)] for m in COST_MULTIPLIERS] == [2, 2, 1, 0]
    assert [counts[(proxy, m)] for m in COST_MULTIPLIERS] == [2, 1, 1, 0]

    assert ladder.flips
    assert counts[(quoted, 1.0)] != counts[(quoted, 2.0)], "§3.5's named pair"

    at = {(s.cell.convention, s.cell.multiplier): s for s in ladder.cells}
    assert at[(quoted, 1.0)].leg_ids == ("out_sveny30_short", "spr_sveny10_sveny30_short")
    assert at[(proxy, 0.5)].leg_ids == ("out_sveny10_short", "fly_sveny07_sveny10_sveny20_short")
    assert not set(at[(quoted, 0.5)].leg_ids) & set(at[(proxy, 0.5)].leg_ids), (
        "the two conventions select disjoint books at 0.5x, which is more than X5 claimed"
    )
    assert ladder.evaluations == 7830

    flat = generator.SelectionLadder(REFERENCE_VIEW, (at[(quoted, 1.0)],), ("half_spread",))
    assert len(flat.cells) == 1 and not flat.flips
    same = generator.SelectionLadder(
        REFERENCE_VIEW, (at[(quoted, 0.5)], at[(quoted, 1.0)]), ("half_spread",)
    )
    assert len(same.cells) == 2 and not same.flips


def test_h9_holds_at_every_rung_and_six_is_a_ceiling(basis, yields, ladder) -> None:
    """C106. B106, DD110. **H9's subject, and X15's discharge.**

    > H9 -- for the reference view, the cost-aware stopping rule terminates below six legs.
    > Predicted PASS, at three or four.

    **PASS at all eight cells, and the predicted value is wrong on the low side at every one of
    them**: the counts are 0, 1 and 2, never 3 or 4.

    **X15's discharge, which is what makes the pass readable.** The attainable range of the leg
    count over the pre-registered grid is `{0, 1, 2}`; the threshold is `< 6`; the fraction of that
    range admitted is **100%**. Within the grid the rule runs on, H9 **could not have failed** --
    which is `AMENDMENT_A3` §14.4's H8 defect, and the reason X15 was filed STANDING.

    It differs from H8's in the way that decides the disposition. H8's threshold could not fail for
    an algebraic reason (`ENB <= leg count`), so it was withdrawn. H9's can: six is attainable and
    is reached here at an assumed view move of ten basis points. The defect is in the **grid** --
    whose four rungs are view magnitudes between a quarter of a basis point and two -- and not in
    the claim, so the claim is scored and the grid's span is reported beside it.

    **And six is a ceiling set by geometry, not by cost.** At a cost model of effectively zero the
    greedy stops at six because no remaining structure of the 231 raises the book's cosine at all.
    That bounds carried item X11 on one side: grading every absent cost term can only raise the
    count, and the count cannot pass six.

    **Mutation:** the move is raised until the count touches the threshold, so the bar is shown to
    be capable of failing rather than asserted to be.
    """
    for selection in ladder.cells:
        assert len(selection) < 6, (selection.cell, len(selection))
    assert {len(s) for s in ladder.cells} == {0, 1, 2}

    quoted = DurationConvention.AS_QUOTED
    free = select(REFERENCE_VIEW, basis, yields, convention=quoted, move_bp=1e8)
    assert len(free) == 6
    assert free.refused is not None and free.refused[1] < 0.0, (
        "the greedy stops for want of fidelity, not for want of money"
    )
    assert free.cosine == pytest.approx(0.906494022, abs=5e-9)

    for move in (1e2, 1e4, 1e8, 1e12):
        assert len(select(REFERENCE_VIEW, basis, yields, convention=quoted, move_bp=move)) == 6

    # The mutation. H9 is falsifiable and this is where it falsifies: the threshold is touched at
    # an assumed view move the plan never fixed, and which the ladder's rungs do not span.
    sweep = {
        move: len(select(REFERENCE_VIEW, basis, yields, convention=quoted, move_bp=move))
        for move in (0.25, 0.5, 1.0, 2.0, 4.0, 10.0)
    }
    assert sweep == {0.25: 0, 0.5: 1, 1.0: 2, 2.0: 2, 4.0: 4, 10.0: 6}
    assert sweep[10.0] == 6, "not below six -- H9 fails here, and no cell of the ladder reaches it"

    # `AMENDMENT_A3` §6 annotated H9: "six" is `REFERENCE_BOOK`'s count and two of those legs
    # cannot be priced, so the priceable comparand is `US_CASH_BOOK`'s four. The annotation
    # tightens the bar without moving the verdict, exactly as it predicted.
    for selection in ladder.cells:
        assert len(selection) < 4


def test_the_move_and_the_notional_are_not_degrees_of_freedom(basis, yields) -> None:
    """C107. B107, DD110. C91's shape, for the parameter `AMENDMENT_A2` did not name.

    A2 §2 fixed `COST_HURDLE = 1.0` by showing that selecting at hurdle `h` against cost `c` is the
    same function as selecting at `1.0` against `h*c`, so any other value is a rung of a ladder
    already reported. **`VIEW_MOVE_BP` is the third quantity in that family and the only one of the
    three that moves H9's verdict.** Only the quotient `move / multiplier` enters, so the identity
    is exact and is asserted leg for leg rather than count for count -- two selections of the same
    size can be different books, as C105 measures at 0.5x.

    The second half is the notional. `cost_per_dv01`'s docstring says the notional divides out of
    it exactly, and the exposure here is normalised by the same leg's gross DV01, so the whole
    selection is scale-free. **A quantity claimed not to matter is exactly the kind that turns out
    to**, so it is measured across three orders of magnitude rather than argued from the algebra.

    **Mutation:** a move that is not the reciprocal of the multiplier gives a different answer, so
    the identity is not vacuously true of every pair.
    """
    quoted = DurationConvention.AS_QUOTED
    for multiplier in COST_MULTIPLIERS:
        scaled = select(REFERENCE_VIEW, basis, yields, multiplier=multiplier, convention=quoted)
        moved = select(REFERENCE_VIEW, basis, yields, convention=quoted, move_bp=1.0 / multiplier)
        assert scaled.leg_ids == moved.leg_ids, multiplier
        assert scaled.cosine == pytest.approx(moved.cosine, abs=1e-12)

    base = select(REFERENCE_VIEW, basis, yields, convention=quoted)
    assert base.leg_ids == ("out_sveny30_short", "spr_sveny10_sveny30_short")
    reference = next(
        leg
        for leg in candidate_legs(notional=generator.UNIT_NOTIONAL)
        if leg.instrument.symbol == "OUT_SVENY30" and leg.direction is Direction.SHORT
    )
    for notional in (1.0e6, 1.0e7, 5.0e9):
        legs = candidate_legs(notional=notional)
        assert {leg.notional.amount for leg in legs} == {notional}
        one = next(
            leg
            for leg in legs
            if leg.instrument.symbol == "OUT_SVENY30" and leg.direction is Direction.SHORT
        )
        assert cost_per_dv01(one, yields) == pytest.approx(
            cost_per_dv01(reference, yields), rel=1e-12
        )
        assert unit_risk_exposure(one, yields, quoted) == pytest.approx(
            unit_risk_exposure(reference, yields, quoted), abs=1e-15
        )

    wrong = select(REFERENCE_VIEW, basis, yields, convention=quoted, move_bp=4.0)
    forced = select(REFERENCE_VIEW, basis, yields, multiplier=4.0, convention=quoted)
    assert len(wrong) != len(forced)


def test_every_surviving_leg_is_defended_and_a_forced_count_carries_its_price(ladder) -> None:
    """C108. B108, DD110. §1.5 and §1.6, which are the two points of §1 that are reports.

    §1.5: *"leave-one-out is reported for every surviving leg, so each leg's place is defended by a
    number rather than by the fact that it was added."* Every addition, every cell, no exceptions
    -- a selection that reports a count without them is what this refuses.

    §1.6: *"if a fixed count is wanted for presentation, the counterfactual is reported: what
    forcing the extra leg cost in view-exposure per unit of risk."* The counterfactual therefore has
    to run **past** the stop, which is the only place a forced count's price can be read, and it
    runs to the geometric ceiling.

    **The measured defence is sharper than the rule needed.** Removing the first leg of the 1x
    `AS_QUOTED` book leaves a cosine of **-0.1575**: the second leg alone points *against* the view
    and holds its place only by what it cancels. That is F3's mechanism, two packages early.

    **Mutation:** a selection whose leave-one-out is short by a leg, and one whose counterfactual
    stops at the stop.
    """
    for selection in ladder.cells:
        assert len(selection.leave_one_out) == len(selection.additions)
        assert {r.leg_id for r in selection.leave_one_out} == set(selection.leg_ids)
        for removal in selection.leave_one_out:
            assert removal.loss == pytest.approx(selection.cosine - removal.cosine_without)
        if selection.additions:
            assert len(selection.counterfactual) >= len(selection.additions)
            at_stop = [f for f in selection.counterfactual if f.legs == len(selection)]
            assert len(at_stop) == 1 and at_stop[0].against_stopped == pytest.approx(0.0)
            for forced in selection.counterfactual:
                if forced.legs > len(selection):
                    assert forced.against_stopped > 0.0, "a forced count buys fidelity, at a price"

    quoted = DurationConvention.AS_QUOTED
    headline = next(
        s for s in ladder.cells if s.cell.convention is quoted and s.cell.multiplier == 1.0
    )
    assert [f.legs for f in headline.counterfactual] == [1, 2, 3, 4, 5, 6]
    assert headline.counterfactual[-1].cosine == pytest.approx(0.906494022, abs=5e-9)
    assert headline.counterfactual[-1].against_stopped == pytest.approx(0.426794488, abs=5e-9)

    first, second = headline.leave_one_out
    assert first.cosine_without == pytest.approx(-0.157504583, abs=5e-9)
    assert first.cosine_without < 0.0 < second.cosine_without

    short = generator.Selection(
        cell=headline.cell,
        view=headline.view,
        additions=headline.additions,
        cosine=headline.cosine,
        evaluations=headline.evaluations,
        refused=headline.refused,
        leave_one_out=headline.leave_one_out[:1],
        counterfactual=headline.counterfactual,
    )
    assert len(short.leave_one_out) != len(short.additions)
    truncated = generator.Selection(
        cell=headline.cell,
        view=headline.view,
        additions=headline.additions,
        cosine=headline.cosine,
        evaluations=headline.evaluations,
        refused=headline.refused,
        leave_one_out=headline.leave_one_out,
        counterfactual=headline.counterfactual[: len(headline.additions)],
    )
    assert not [f for f in truncated.counterfactual if f.legs > len(truncated)]


def test_nothing_generated_declares_a_neutrality_it_has_not_got(yields) -> None:
    """C109. B109, DD110. D4's carried question, answered by declining to repeat it.

    D4 measured that `US_BREAKEVEN_5Y` declares `Neutrality.DV01` and leaves **370.67 per basis
    point** on $50m, and left the re-expression here: *"whether this leg is better matched on
    duration than on coefficients is a decision for D7b, the leg generator, which has a reason to
    make it."*

    **The decision is `CASH`, and it is true without being measured.** A `(+1, -1)` pair on one
    notional buys and sells equal cash by construction. It is not DV01-neutral and nothing
    generated here says it is.

    The generator's own enumeration contains the reference leg, so D4's number is reproduced from
    the rule rather than quoted from the document -- and `reference.py` stays annotated and unedited
    for the fourth package running, which is the disposition D5's DD40 reached.

    **Mutation, and the reason X17 exists:** the wrong declaration is constructible, and the *right*
    one -- DV01-matched coefficients -- is what `book.py` refuses, because DD17 reads "coefficients
    sum to zero" as "hedged against something".
    """
    universe = enumerate_universe()
    for instrument in universe:
        total = math.fsum(c.coefficient for c in instrument.components)
        if instrument.structure is Structure.OUTRIGHT:
            assert instrument.neutrality is Neutrality.NONE
            continue
        assert abs(total) <= 1e-12, instrument.symbol
        assert instrument.neutrality is Neutrality.CASH, instrument.symbol
    assert not [i for i in universe if i.neutrality is Neutrality.DV01]

    # The generator names the pair in its own enumeration order, so this is `reference.py`'s
    # `US_BREAKEVEN_5Y` with the two components the other way round -- the same structure, with
    # `Direction` carrying the difference, which is exactly why the sign lives on the leg.
    reference_pair = next(
        leg
        for leg in candidate_legs(notional=5.0e7)
        if leg.instrument.symbol == "SPR_DFII5_SVENY05" and leg.direction is Direction.LONG
    )
    assert reference_pair.instrument.series == ("DFII5", "SVENY05")
    per_series = {c.series: c.dv01 for c in leg_sensitivity(reference_pair, yields).components}
    assert abs(math.fsum(per_series.values())) == pytest.approx(370.67, abs=0.01), (
        "D4's number, regenerated by the rule rather than copied from the document"
    )
    assert reference_pair.instrument.neutrality is Neutrality.CASH

    wrong = Instrument(
        symbol="SPR_SVENY05_DFII5_DV01",
        kind=InstrumentKind.BREAKEVEN,
        currency=Currency.USD,
        tenor_years=5.0,
        components=(
            Component("SVENY05", 1.0, Currency.USD),
            Component("DFII5", -1.0, Currency.USD),
        ),
        neutrality=Neutrality.DV01,
    )
    assert wrong.neutrality is Neutrality.DV01
    with pytest.raises(ValueError) as caught:
        Instrument(
            symbol="SPR_SVENY05_DFII5_MATCHED",
            kind=InstrumentKind.BREAKEVEN,
            currency=Currency.USD,
            tenor_years=5.0,
            components=(
                Component("SVENY05", 1.0, Currency.USD),
                Component("DFII5", -5.0 / 4.925866, Currency.USD),
            ),
            neutrality=Neutrality.DV01,
        )
    assert "coefficients that cancel" in str(caught.value) or "sum to" in str(caught.value)


def test_the_financing_term_has_a_parameter_and_is_absent_for_the_data_reason(yields) -> None:
    """C110. B110, DD111. Carried item X11's code half, closed where the item is owned.

    X11's §0 row: *"`annualised_cost` has **no parameter** a financing input could be passed to, so
    that term is a code gap first."* Literally true until this commit -- the term was refused
    unconditionally, with no argument any caller could have supplied. `costs.Financing` is that
    argument, with no default and no table, for `MarketDepth`'s reason.

    **What has changed is the reason for the absence, not the absence.** Nothing here grades an
    overnight rate: §3.3 names SOFR, which curvecast's D218 measured as opening in 2018 against a
    DEV window ending 2014-12-31, so SOFR is a decline and not a fetch. The term is now absent
    because the data is not here, and no longer because the function could not take it. The rest of
    the item is carried to D8 with the frequency policy X2 already owns.

    **And it states the dependency X11 says must be re-measured.** `AMENDMENT_A2` §2.3's identity --
    that the cost multiplier and the holding period are one axis -- holds *because the spread term
    is the only term there is*. Financing, once annualised, is constant in the holding period, so a
    graded financing input splits them. Asserted at two holding periods rather than left as a
    sentence.

    **Mutation:** a `Maintenance` passed where a `Financing` belongs, and a negative spread.
    """
    leg = next(
        leg
        for leg in candidate_legs()
        if leg.instrument.symbol == "OUT_SVENY10" and leg.direction is Direction.LONG
    )

    bare = annualised_cost(leg, 1.0)
    assert bare.financing is None
    absent = dict(bare.absent)
    assert "financing" in absent and "X11" in absent["financing"] and "SOFR" in absent["financing"]
    with pytest.raises(TermNotAvailable):
        _ = bare.total

    stated = Financing(repo_rate_pct=0.12, spread_bp=5.0)
    assert stated.annual_rate == pytest.approx(0.0012 + 0.0005)
    priced = annualised_cost(leg, 1.0, financing_input=stated)
    assert priced.financing == pytest.approx(stated.annual_rate * leg.notional.amount)
    assert "financing" not in dict(priced.absent)
    assert "financing" in priced.present

    # Still not a total: two of four terms remain absent, for the reasons D7a recorded. Closing
    # X11's code half does not make the model whole, which is what X11 itself says.
    with pytest.raises(TermNotAvailable) as caught:
        _ = priced.total
    assert "impact" in str(caught.value) and "roll" in str(caught.value)

    whole = annualised_cost(
        leg,
        1.0,
        depth=MarketDepth(
            average_daily_volume=1.0e10,
            order_size=1.0e8,
            daily_volatility_bp=5.0,
            coefficient=1.0,
        ),
        maintenance=Maintenance(rolls_per_year=0.0),
        financing_input=stated,
    )
    assert whole.absent == () and whole.total > 0.0

    # X11's inherited obligation: the multiplier and the holding period stop being one axis.
    half = annualised_cost(leg, 0.5, financing_input=stated)
    assert half.financing == pytest.approx(priced.financing), "constant in the hold"
    assert half.half_spread == pytest.approx(2.0 * priced.half_spread), "not constant in the hold"

    assert Financing(repo_rate_pct=0.0, spread_bp=0.0).annual_rate == 0.0, (
        "a stated zero is a statement, which is the distinction DD79 turns on"
    )
    with pytest.raises(TypeError):
        annualised_cost(leg, 1.0, financing_input=Maintenance(rolls_per_year=1.0))
    with pytest.raises(ValueError):
        Financing(repo_rate_pct=0.12, spread_bp=-1.0)


def _fidelity_names(source: str) -> tuple[str, ...]:
    """Which of `ViewFidelity`'s two statistics a module reads. Shared by C111 and its mutation."""
    tree = ast.parse(source)
    seen = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)} | {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    }
    return tuple(sorted({"dominant_share", "cosine"} & seen))


def test_no_module_that_orders_candidates_reads_dominant_share() -> None:
    """C111. B111, DD110. Carried item X3's discharge, as a census rather than as a sentence.

    X3: *"`dominant_share` over-attributes on a non-orthogonal basis"*, owned by D9 for the fix and
    by D7b to *"pre-register the re-score"*. `BUILD_ORDER` §2's annotation sharpens it: *"D7b ranks
    legs by fidelity two packages before D9 can fix the statistic."*

    **It does not.** `ViewFidelity` carries two statistics and they are not interchangeable.
    `dominant_share` is a share of a sum and needs the six directions to partition something, which
    `factors.FactorBasis.gram` says they do not. `cosine` is an angle between two vectors in series
    space and claims no decomposition at all, so the basis's angles do not touch it. The ordering
    here is `cosine`, so there is nothing ranked by the broken statistic to re-score.

    **A census, in C102's shape.** X3 was a worry about a sentence in a document, so the answer is
    not another sentence: the reader set is an equality, and the day a module orders candidates by
    `dominant_share` the suite is red before its pre-commit is written. It **names** rather than
    forbids, for C102's reason -- D9 will legitimately read the statistic in order to fix it.

    **Mutation:** a planted ranker that reads it is found; one that reads `cosine` is not, through
    the same scanner rather than through a copy of it.
    """
    census = {
        path.relative_to(SRC).as_posix(): found
        for path in sorted(SRC.rglob("*.py"))
        if (found := _fidelity_names(_read(path)))
    }
    assert census == {
        # D6 defines both and orders nothing with either.
        "deskcraft/views.py": ("cosine", "dominant_share"),
        # D7b orders by the angle, and by nothing else.
        "deskcraft/generator.py": ("cosine",),
    }, census

    # The distinction C102 drew one level down, and it matters here too: `generator.py`'s module
    # docstring *names* `dominant_share`, to say why it is not used. Naming is not reading, and a
    # scan that could not tell the two apart would force a module to stay silent about the thing
    # it declines -- which is the opposite of what this repository wants written down.
    source = _read(SRC / "deskcraft" / "generator.py")
    assert "dominant_share" in source
    assert "dominant_share" not in _fidelity_names(source)

    by_share = '''from deskcraft.views import fidelity


def rank(books, view, basis, yields):
    return sorted(books, key=lambda b: -fidelity(b, view, basis, yields).dominant_share)
'''
    by_angle = by_share.replace("dominant_share", "cosine")
    assert _fidelity_names(by_share) == ("dominant_share",)
    assert _fidelity_names(by_angle) == ("cosine",)


def test_an_empty_selection_is_an_outcome_and_not_a_book(basis, yields, ladder) -> None:
    """C112. B112, DD110. §1 has no floor, and the zero is a true statement.

    At 4x on both conventions the rule takes nothing: at a quarter of a basis point of assumed
    move, no structure in the universe repays its spread. `Book.legs` refuses to be empty --
    *"every ratio below divides by zero on it"* -- so the generator refuses rather than inventing a
    leg, because a one-leg book emitted to avoid an awkward output would be this engine stating a
    position.

    **What must not happen is a zero read as the rule breaking**, so `refused` carries the best
    candidate that failed and its ratio, and the refusal says where the answer is read instead.

    **Mutation:** the non-empty cells build books, so the refusal is about emptiness and not about
    `book()` being broken.
    """
    empty = [s for s in ladder.cells if not s.additions]
    assert len(empty) == 2
    assert {s.cell.multiplier for s in empty} == {4.0}
    for selection in empty:
        assert selection.cosine == 0.0
        assert selection.refused is not None
        leg_id, ratio = selection.refused
        assert 0.0 < ratio < COST_HURDLE
        assert selection.evaluations == 462
        with pytest.raises(NoCandidate) as caught:
            selection.book("empty", "nothing cleared the hurdle at this cell")
        assert "statement about costs at this cell" in str(caught.value)
        assert leg_id in str(caught.value)

    for selection in ladder.cells:
        if selection.additions:
            book = selection.book("generated", "A generated expression of the reference view")
            assert book.leg_ids == selection.leg_ids
            assert len(book) == len(selection)

    # A two-term view is reachable and selects a different book, so the machinery is not wired to
    # one view -- the alternative reading D6 wrote at the same time as the reference one.
    two_term = select(
        View.of((Factor.LEVEL, Move.UP), (Factor.SLOPE, Move.UP)), basis, yields
    )
    assert two_term.leg_ids != ladder.cells[1].leg_ids or two_term.cosine != ladder.cells[1].cosine
def _two_term(real, reading: str, multiplier: float, fraction: float):
    """A cost of two terms, scaled the two ways this tree scaled one term.

    `reading` is `"A"` when the rung scales the total -- DD112, and what `generator.select`
    computes -- and `"B"` when it scales the spread, which is where `cost_per_dv01` applied it
    until 2026-09-16. `fraction` sizes the second term as a multiple of the graded spread.

    `select` computes the cost once at the default rung and multiplies by the rung at the point of
    comparison, so the effective per-rung cost is handed back divided by the rung. That routes
    either reading through the untouched selection code rather than through a second copy of it.

    `real` is passed in rather than read from the module, because this helper is called once per
    cell and reading it here would capture the previous cell's patch and compound it.
    """

    def inner(leg, yields, convention=DurationConvention.AS_QUOTED, multiplier_=1.0):
        spread = real(leg, yields, convention)
        extra = fraction * spread
        total = (
            multiplier * (spread + extra)
            if reading == "A"
            else multiplier * spread + extra
        )
        return total / multiplier

    return inner


def _book(monkeypatch, real, basis, yields, reading: str, multiplier: float, fraction: float):
    monkeypatch.setattr(
        generator, "cost_per_dv01", _two_term(real, reading, multiplier, fraction)
    )
    selection = select(
        REFERENCE_VIEW,
        basis,
        yields,
        multiplier=multiplier,
        convention=DurationConvention.AS_QUOTED,
    )
    return tuple(addition.symbol + addition.direction.name for addition in selection.additions)


def test_the_two_scopes_of_the_rung_select_different_books(monkeypatch, basis, yields) -> None:
    """C115. B115, DD112. The half of the finding that is a leg count rather than an identity.

    `C113` holds that the two placements of the cost multiplier are bit-identical while the spread
    is the only graded term. This holds what they do once it is not, and it is the reason DD112 is
    a decision rather than a tidy-up: **the two readings choose different structures**, so the
    scope nobody stated is a parameter that moves H9's answer.

    Measured over a sweep of second-term magnitudes, the readings disagree at **three of
    twenty-eight** cells. The three are asserted below by value. They are differences of one leg
    in the count, at 0.5x and 2.0x -- and 1x-to-2x is the pair §3.5 nominates by name as the one
    whose flip makes the headline *a statement about costs rather than about structure*.

    **What this bar is not.** It is not evidence that a second cost term should be graded, nor
    that these magnitudes are the right ones -- nothing here grades a source, and the second term
    is synthetic, which §9 of the rider states. The claim is qualitative and needs one divergent
    cell; three are asserted because three is what was measured, and a bar that rounded that to
    *"they can differ"* would be the prose this repository keeps finding.

    **Mutation:** the second term set to zero, where the two readings must agree again at every
    rung -- so the bar is shown to be measuring the term and not the patching.
    """
    # Captured before anything is patched: each cell below builds its cost from the real graded
    # spread, so a cell never reads the previous cell's patch.
    real = generator.cost_per_dv01

    # The mutation first, because it is the state that says the harness is honest: with one graded
    # term the two readings are the same function, which is exactly why this went unseen.
    for multiplier in COST_MULTIPLIERS:
        under_a = _book(monkeypatch, real, basis, yields, "A", multiplier, 0.0)
        under_b = _book(monkeypatch, real, basis, yields, "B", multiplier, 0.0)
        assert under_a == under_b, multiplier

    # And the three cells where a second term separates them. `fraction` is the second term as a
    # multiple of that leg's spread; the counts are the measured ones.
    divergent = {
        (0.5, 2.0): (0, 1),
        (2.0, 0.5): (2, 1),
        (4.0, 0.5): (1, 0),
    }
    for (fraction, multiplier), (expected_a, expected_b) in divergent.items():
        under_a = _book(monkeypatch, real, basis, yields, "A", multiplier, fraction)
        under_b = _book(monkeypatch, real, basis, yields, "B", multiplier, fraction)
        assert len(under_a) == expected_a, (fraction, multiplier, under_a)
        assert len(under_b) == expected_b, (fraction, multiplier, under_b)
        assert under_a != under_b
