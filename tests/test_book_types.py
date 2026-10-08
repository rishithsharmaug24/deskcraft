"""The book types and the reference structure. D2, bars C10-C14 and C16-C22.

C15 lives in `test_deskcraft_boundary.py` because it is the widening of that file's own
scanner, and a bar about a guard belongs beside the guard.

Two of these bars check this repo against **curvecast**, read from its source at test time
rather than copied into a constant here. That is C9's shape, and the reason is the same: a
fact about the graded universe that lives in two places goes stale in one of them, and the
one that goes stale is always the copy.

**Amended by the environment-census rider, 2026-09-15 (DD69).** There now IS a copy, in
`upstream_certificate.py`, and the objection above is answered rather than waived: it is held
at equality against the live parse on every machine that has curvecast, so it is the one kind
of copy that cannot go stale in silence. What it buys is that C14 no longer vanishes on a
reviewer's machine -- which it did, along with thirteen other bars.
"""

from __future__ import annotations

import ast
import dataclasses
import math
from pathlib import Path

import pytest

from deskcraft.book import (
    ASSET_CLASS_OF,
    AssetClass,
    Book,
    Component,
    Currency,
    Direction,
    Instrument,
    InstrumentKind,
    Neutrality,
    Notional,
    Structure,
    TENORED_KINDS,
    TENORLESS_KINDS,
    UNSERIESED_KINDS,
)
from upstream_certificate import GRADED_UNIVERSE

from deskcraft.reference import (
    DEFERRED_LEGS,
    NOTIONAL_PROVENANCE,
    REFERENCE_BOOK,
    SCENARIO_SIGNS,
    US_CASH_BOOK,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
CURVECAST = Path("C:/Users/rishi/curvecast")

BOOKS = (REFERENCE_BOOK, US_CASH_BOOK)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def python_files(*roots: Path) -> list[Path]:
    return sorted(path for root in roots for path in root.rglob("*.py"))


def class_names(source: str) -> list[str]:
    return [node.name for node in ast.walk(ast.parse(source)) if isinstance(node, ast.ClassDef)]


# ---------------------------------------------------------------------------
# C10-C13: the decisions that make a wrong book unrepresentable
# ---------------------------------------------------------------------------


def test_direction_and_notional_are_defined_exactly_once() -> None:
    """C10. B10. The plan says they live here and nowhere else; this is what checks it.

    Nothing in the boundary test forbids these names -- that is the whole inversion, and it is
    why the discipline has to be a bar of its own. The scan is for *definitions*: importing
    them elsewhere is necessary and fine, and `reference.py` does exactly that.

    **Mutation:** a synthetic module defining `class SignedNotional` is caught by the same
    scanner, because a near-name growing beside the real one is how "one binding site" stops
    being true without anything being renamed.

    **The message names the convention, since 2026-09-15** (`AMENDMENT_A2` §8). This bar has
    fired on two consecutive packages -- D6's `ViewDirection`, D7a's `BiasDirection` -- and both
    were answered by renaming to `...Sense`, beside D4's `RateSense`. The convention had been
    paid for twice and appeared in nobody's error message, so a third author met the refusal
    without meeting the answer. The check and the mutation are unchanged; only what it says.
    """
    definitions: dict[str, list[str]] = {}
    for path in python_files(SRC):
        for name in class_names(_read(path)):
            definitions.setdefault(name, []).append(path.name)

    assert definitions.get("Direction") == ["book.py"], definitions.get("Direction")
    assert definitions.get("Notional") == ["book.py"], definitions.get("Notional")

    near = [
        name
        for name in definitions
        if name not in {"Direction", "Notional"}
        and ("direction" in name.lower() or "notional" in name.lower())
    ]
    assert not near, (
        f"a near-name grew beside the real one: {near}. Rename the symbol -- this bar has no "
        "exemption list and gains none. Two packages have met it and both answered the same "
        "way: D6's `ViewDirection` and D7a's `BiasDirection` are `Move` and `BiasSense`, beside "
        "D4's `RateSense`. When a package needs to say which way something points, `...Sense` "
        "is the word that is free; `Direction` and `Notional` bind once, in book.py."
    )

    mutant = "class SignedNotional:\n    pass\n"
    caught = [n for n in class_names(mutant) if "notional" in n.lower()]
    assert caught == ["SignedNotional"]


def test_the_objects_are_immutable_in_fact_and_not_only_by_keyword() -> None:
    """C11. B11, DD9. `frozen=True` stops rebinding and nothing else.

    Measured before deciding: `x.xs.append(2)` succeeds on a frozen dataclass holding a list.
    What `frozen=True` does buy is that the instance stops being **hashable**, at any depth,
    because the generated `__hash__` hashes the field tuple. So one `hash(book)` is a deeper
    check than an annotation scan, and it is what this bar rests on.

    **Mutation:** the same predicate is shown to reject a frozen dataclass carrying a list.
    """

    def deeply_immutable(value: object) -> bool:
        try:
            hash(value)
        except TypeError:
            return False
        return True

    for book in BOOKS:
        assert deeply_immutable(book), f"{book.book_id} holds a mutable field somewhere"
        with pytest.raises(dataclasses.FrozenInstanceError):
            book.book_id = "renamed"  # type: ignore[misc]
        for leg in book.legs:
            assert deeply_immutable(leg)
            with pytest.raises(dataclasses.FrozenInstanceError):
                leg.direction = Direction.LONG  # type: ignore[misc]

    @dataclasses.dataclass(frozen=True)
    class Smuggled:
        xs: list  # noqa: UP006 -- the point is that this is mutable

    smuggled = Smuggled([1])
    smuggled.xs.append(2)
    assert smuggled.xs == [1, 2], "frozen=True did not stop the mutation, which is the finding"
    assert not deeply_immutable(smuggled), "the hashability predicate must reject this"

    with pytest.raises(TypeError):
        Book(book_id="b", as_of=REFERENCE_BOOK.as_of, thesis="t", legs=list(REFERENCE_BOOK.legs))


def test_the_sign_lives_only_in_direction() -> None:
    """C12. B12, DD8. A negative amount and a SHORT direction is a long position.

    That book is unrepresentable here rather than merely wrong, which is the difference
    between a validation and a design. Zero is refused for the neighbouring reason: a
    zero-amount leg contributes nothing and survives every downstream filter.
    """
    assert {int(member) for member in Direction} == {1, -1}

    for value in (-2e8, 0.0, -0.0, float("nan"), float("inf"), -float("inf")):
        with pytest.raises(ValueError):
            Notional(value, Currency.USD)
    with pytest.raises(TypeError):
        Notional(True, Currency.USD)  # a bool is an int and would otherwise pass

    for book in BOOKS:
        for leg in book.legs:
            assert leg.notional.amount > 0.0
            assert leg.signed_amount == int(leg.direction) * leg.notional.amount
            if leg.direction is Direction.SHORT:
                assert leg.signed_amount < 0.0
            else:
                assert leg.signed_amount > 0.0


def test_money_never_crosses_currencies_implicitly() -> None:
    """C13. B13, DD10. The raising path is the one the fixture exercises.

    The reference book has a EUR leg, so `gross_notional` raises on it rather than on a
    contrived input. There is no exchange rate in this repo and a default one here would be
    the first fitted number in a package that has none.
    """
    assert REFERENCE_BOOK.currencies == (Currency.EUR, Currency.USD)

    with pytest.raises(ValueError, match="no exchange rate"):
        REFERENCE_BOOK.gross_notional
    with pytest.raises(ValueError, match="no exchange rate"):
        REFERENCE_BOOK.net_notional
    with pytest.raises(ValueError, match="no exchange rate"):
        REFERENCE_BOOK.gross_by_asset_class()

    gross = REFERENCE_BOOK.gross_by_currency()
    assert set(gross) == {Currency.USD, Currency.EUR}
    assert gross[Currency.USD] == pytest.approx(200e6 + 60e6 + 50e6 + 50e6 + 40e6)
    assert gross[Currency.EUR] == pytest.approx(75e6)

    net = REFERENCE_BOOK.net_by_currency()
    assert net[Currency.USD] == pytest.approx(-200e6 - 60e6 + 50e6 + 50e6 - 40e6)
    assert net[Currency.EUR] == pytest.approx(-75e6)

    assert US_CASH_BOOK.currencies == (Currency.EUR, Currency.USD)


# ---------------------------------------------------------------------------
# C14: the partition, checked against curvecast rather than against a copy
# ---------------------------------------------------------------------------


def graded_universe() -> set[str]:
    """Series with a measured archive floor, plus the pinned GSW zero columns.

    Parsed out of curvecast at test time (C9's shape). A hardcoded copy here would have gone
    stale the moment D5 probes the four front-end floors, and going stale silently is the
    failure this arrangement exists to prevent.

    **D5, 2026-09-12, DD39.** It probed them. curvecast `e78d2f7` took `FLOORS` 30 to 34, and
    this parse returned the four new rows with no edit here, which is the arrangement working.
    The floor below did not move on its own, though — `>= 30` is satisfied by 34 as well as by
    30 — so it is raised to the count that was measured. It stays an inequality because
    curvecast owns that table and will add to it without asking; what this guard is for is a
    row **disappearing**, or the scan silently matching nothing after an upstream refactor.
    `test_front_end_universe.py` names the four by hand, because a count does not say which.

    **Off-machine it returns the certificate rather than skipping** (DD69). What is conditional
    is the parse, not the partition C14 and C39 draw with it. When curvecast IS here the parse
    runs and the certificate is held at equality against it, so the committed copy cannot be
    the thing that drifts -- which is the whole objection to keeping one.
    """
    archive_floors = CURVECAST / "src" / "curvecast" / "pit" / "archive_floors.py"
    if not archive_floors.exists():
        return set(GRADED_UNIVERSE)

    floors = _read(archive_floors)
    series = {
        node.value.value
        for node in ast.walk(ast.parse(floors))
        if isinstance(node, ast.keyword)
        and node.arg == "series_id"
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    }
    factor_space = _read(CURVECAST / "src" / "curvecast" / "stage3" / "factor_space.py")
    columns = {
        node.value
        for assign in ast.walk(ast.parse(factor_space))
        if isinstance(assign, ast.AnnAssign)
        and isinstance(assign.target, ast.Name)
        and assign.target.id == "TENOR_GRID"
        for node in ast.walk(assign)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.startswith("SVENY")
    }
    assert len(series) >= 34, f"only {len(series)} archive floors parsed; the scan is wrong"
    assert len(columns) == 8, f"expected 8 GSW zero columns, parsed {sorted(columns)}"

    parsed = series | columns
    assert parsed == set(GRADED_UNIVERSE), (
        "curvecast's graded universe has moved away from the certificate: "
        f"gained {sorted(parsed - set(GRADED_UNIVERSE))}, "
        f"lost {sorted(set(GRADED_UNIVERSE) - parsed)}"
    )
    return parsed


def test_the_priceable_partition_is_derived_from_what_is_actually_graded() -> None:
    """C14. B14, DD11. Priceability is derived, and the source of truth is next door.

    Every leg is in exactly one of two sets. A priceable leg has all its components inside the
    graded universe; a deferred one has a component outside it, or a kind with no series at
    all. The floor is four, which is the approved plan's §10 NO-BUILD condition: fewer than
    four independently graded instruments and there is no multi-leg question to ask.

    Conditional only in where the universe comes from (DD69). The partition itself -- which is
    what this bar asserts -- is drawn and checked on every machine.
    """
    universe = graded_universe()

    assert set(DEFERRED_LEGS) < set(REFERENCE_BOOK.leg_ids)
    assert set(US_CASH_BOOK.leg_ids) | set(DEFERRED_LEGS) == set(REFERENCE_BOOK.leg_ids)
    assert not set(US_CASH_BOOK.leg_ids) & set(DEFERRED_LEGS)

    for leg in US_CASH_BOOK.legs:
        outside = set(leg.instrument.series) - universe
        assert not outside, f"{leg.leg_id} is priceable but reaches ungraded {sorted(outside)}"
        assert leg.instrument.series, f"{leg.leg_id} is priceable but names no series"

    for leg_id, reason in DEFERRED_LEGS.items():
        instrument = REFERENCE_BOOK.leg(leg_id).instrument
        outside = set(instrument.series) - universe
        assert outside or instrument.kind in UNSERIESED_KINDS, (
            f"{leg_id} is deferred but every component is graded; the reason given is {reason!r}"
        )

    assert len(US_CASH_BOOK) >= 4, (
        f"only {len(US_CASH_BOOK)} graded legs; §10's NO-BUILD floor is four"
    )
    assert set(NOTIONAL_PROVENANCE) == set(REFERENCE_BOOK.leg_ids)


# ---------------------------------------------------------------------------
# C16-C18: well-formedness
# ---------------------------------------------------------------------------


def test_a_book_is_addressable_and_non_empty() -> None:
    """C16. B16, DD15. Zero legs divides by zero downstream; duplicate ids are unaddressable."""
    one = REFERENCE_BOOK.legs[0]

    with pytest.raises(ValueError, match="empty"):
        Book(book_id="b", as_of=REFERENCE_BOOK.as_of, thesis="t", legs=())
    with pytest.raises(ValueError, match="repeats a leg_id"):
        Book(book_id="b", as_of=REFERENCE_BOOK.as_of, thesis="t", legs=(one, one))

    twin = dataclasses.replace(one, leg_id="us_2y_second_clip")
    both = Book(
        book_id="two_clips",
        as_of=REFERENCE_BOOK.as_of,
        thesis=REFERENCE_BOOK.thesis,
        legs=(one, twin),
    )
    assert len(both) == 2 and both.leg(twin.leg_id) is twin

    with pytest.raises(KeyError):
        REFERENCE_BOOK.leg("no_such_leg")
    with pytest.raises(KeyError):
        REFERENCE_BOOK.restricted_to("x", ("no_such_leg",))


def test_the_reference_structure_matches_its_source() -> None:
    """C17. B17, DD12. Six legs, the stated directions, and the re-expression recorded.

    The source states legs 1 and 2 as Treasury futures and §4 declines any futures leg, so
    they are carried as cash with a `ReExpression` naming what that drops. A leg that silently
    claimed to be the original would be the interesting failure here, not a missing one.
    """
    assert REFERENCE_BOOK.leg_ids == (
        "us_2y",
        "us_10y",
        "us_breakeven_5y",
        "eurusd",
        "us_10y_call",
        "us_de_10y",
    )
    expected = {
        "us_2y": Direction.SHORT,
        "us_10y": Direction.SHORT,
        "us_breakeven_5y": Direction.LONG,
        "eurusd": Direction.SHORT,
        "us_10y_call": Direction.LONG,
        "us_de_10y": Direction.SHORT,
    }
    assert {leg.leg_id: leg.direction for leg in REFERENCE_BOOK.legs} == expected

    for leg_id in ("us_2y", "us_10y"):
        leg = REFERENCE_BOOK.leg(leg_id)
        assert leg.re_expressed is not None, f"{leg_id} claims to be the instrument it is not"
        assert leg.re_expressed.original_kind is InstrumentKind.FUTURE
        assert set(leg.re_expressed.unmodelled) == {"financing", "delivery option", "roll"}
        assert leg.instrument.kind is InstrumentKind.ZERO_YIELD

    assert REFERENCE_BOOK.leg("us_10y_call").instrument.kind is InstrumentKind.OPTION
    assert REFERENCE_BOOK.leg("us_2y").notional.amount == 200e6


def test_a_tenor_is_present_exactly_where_it_means_something() -> None:
    """C18. B18. The kind partition is total and disjoint; both mutations are caught."""
    assert TENORED_KINDS | TENORLESS_KINDS == set(InstrumentKind)
    assert not TENORED_KINDS & TENORLESS_KINDS

    with pytest.raises(ValueError, match="carries no tenor"):
        Instrument(
            symbol="EURUSD",
            kind=InstrumentKind.FX_SPOT,
            currency=Currency.EUR,
            tenor_years=10.0,
            components=(Component("DEXUSEU", 1.0, Currency.EUR),),
        )
    with pytest.raises(ValueError, match="requires a tenor"):
        Instrument(
            symbol="US_ZERO_10Y",
            kind=InstrumentKind.ZERO_YIELD,
            currency=Currency.USD,
            components=(Component("SVENY10", 1.0, Currency.USD),),
        )
    with pytest.raises(ValueError, match="has no observable series"):
        Instrument(
            symbol="US_10Y_CALL",
            kind=InstrumentKind.OPTION,
            currency=Currency.USD,
            tenor_years=10.0,
            components=(Component("SVENY10", 1.0, Currency.USD),),
        )
    with pytest.raises(ValueError, match="must name the series"):
        Instrument(
            symbol="US_ZERO_10Y",
            kind=InstrumentKind.ZERO_YIELD,
            currency=Currency.USD,
            tenor_years=10.0,
        )

    for book in BOOKS:
        for leg in book.legs:
            instrument = leg.instrument
            if instrument.kind in TENORLESS_KINDS:
                assert instrument.tenor_years is None
            else:
                assert instrument.tenor_years is not None and instrument.tenor_years > 0.0


# ---------------------------------------------------------------------------
# C19-C22: relative value, cross-currency, asset class, and the sign matrix
# ---------------------------------------------------------------------------


def test_a_relative_value_leg_is_distinguishable_from_a_doubled_outright() -> None:
    """C19. B19, DD16-DD17. The neutrality iff, checked in both directions.

    Four of the six reference legs are differences rather than outright positions, and the
    structure is derived from the component count so it cannot disagree with the components.
    The law that earns its place is an equivalence: coefficients cancel **iff** a neutrality
    basis is named. Forwards it catches a "spread" written with two `+1`s; backwards it
    catches a balanced spread that declines to say what it is balanced against, which matters
    because DV01-neutral and cash-neutral are different positions.
    """
    seen = {leg.leg_id: leg.instrument.structure for leg in REFERENCE_BOOK.legs}
    assert seen == {
        "us_2y": Structure.OUTRIGHT,
        "us_10y": Structure.OUTRIGHT,
        "us_breakeven_5y": Structure.SPREAD,
        "eurusd": Structure.OUTRIGHT,
        "us_10y_call": Structure.OUTRIGHT,
        "us_de_10y": Structure.SPREAD,
    }
    assert REFERENCE_BOOK.relative_value_legs == ("us_breakeven_5y", "us_de_10y")

    for book in BOOKS:
        for leg in book.legs:
            instrument = leg.instrument
            assert instrument.structure is Structure.OUTRIGHT or len(instrument.components) >= 2
            if not instrument.components:
                continue
            total = math.fsum(item.coefficient for item in instrument.components)
            balanced = abs(total) <= 1e-12
            if instrument.structure is Structure.OUTRIGHT:
                assert instrument.neutrality is Neutrality.NONE
                assert instrument.components[0].coefficient == 1.0
            else:
                assert balanced == (instrument.neutrality is not Neutrality.NONE)

    with pytest.raises(ValueError, match="coefficients sum to"):
        Instrument(
            symbol="DOUBLED",
            kind=InstrumentKind.CROSS_MARKET_SPREAD,
            currency=Currency.USD,
            tenor_years=10.0,
            components=(
                Component("SVENY10", 1.0, Currency.USD),
                Component("SVENY02", 1.0, Currency.USD),
            ),
            neutrality=Neutrality.DV01,
        )

    with pytest.raises(ValueError, match="declares no neutrality"):
        Instrument(
            symbol="UNNAMED_BASIS",
            kind=InstrumentKind.CROSS_MARKET_SPREAD,
            currency=Currency.USD,
            tenor_years=10.0,
            components=(
                Component("SVENY10", 1.0, Currency.USD),
                Component("SVENY02", -1.0, Currency.USD),
            ),
        )

    with pytest.raises(ValueError, match="cannot be"):
        Instrument(
            symbol="OUTRIGHT_HEDGED",
            kind=InstrumentKind.ZERO_YIELD,
            currency=Currency.USD,
            tenor_years=10.0,
            components=(Component("SVENY10", 1.0, Currency.USD),),
            neutrality=Neutrality.DV01,
        )

    with pytest.raises(ValueError, match="zero coefficient"):
        Component("SVENY10", 0.0, Currency.USD)

    butterfly = Instrument(
        symbol="US_2S5S10S_FLY",
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
    assert butterfly.structure is Structure.BUTTERFLY and butterfly.is_relative_value


def test_a_cross_currency_leg_answers_the_hedging_question() -> None:
    """C20. B20, DD18. No default, because a default is a silent answer to the H4 question.

    An unhedged US-versus-Bund spread is two bets, the spread and the currency; a hedged one
    is one. Every effective-number-of-bets reading below turns on which, so the object refuses
    to be constructed without an answer -- and refuses an answer where there is no question.
    """
    assert REFERENCE_BOOK.cross_currency_legs == ("us_de_10y",)
    spread = REFERENCE_BOOK.leg("us_de_10y").instrument
    assert spread.component_currencies == (Currency.EUR, Currency.USD)
    assert spread.fx_hedged is True

    eurusd = REFERENCE_BOOK.leg("eurusd").instrument
    assert eurusd.component_currencies == (Currency.EUR,)
    assert eurusd.is_cross_currency is False and eurusd.fx_hedged is None

    with pytest.raises(ValueError, match="must state fx_hedged"):
        Instrument(
            symbol="US_DE_SPREAD_10Y",
            kind=InstrumentKind.CROSS_MARKET_SPREAD,
            currency=Currency.USD,
            tenor_years=10.0,
            components=(
                Component("SVENY10", 1.0, Currency.USD),
                Component("DE_ZERO_10Y", -1.0, Currency.EUR),
            ),
            neutrality=Neutrality.DV01,
        )

    with pytest.raises(ValueError, match="single-currency"):
        Instrument(
            symbol="US_ZERO_10Y",
            kind=InstrumentKind.ZERO_YIELD,
            currency=Currency.USD,
            tenor_years=10.0,
            components=(Component("SVENY10", 1.0, Currency.USD),),
            fx_hedged=False,
        )

    unhedged = Instrument(
        symbol="US_DE_SPREAD_10Y_UNHEDGED",
        kind=InstrumentKind.CROSS_MARKET_SPREAD,
        currency=Currency.USD,
        tenor_years=10.0,
        components=(
            Component("SVENY10", 1.0, Currency.USD),
            Component("DE_ZERO_10Y", -1.0, Currency.EUR),
        ),
        neutrality=Neutrality.DV01,
        fx_hedged=False,
    )
    assert unhedged.is_cross_currency and unhedged.fx_hedged is False


def test_every_kind_has_exactly_one_asset_class() -> None:
    """C21. B21, DD19. Total, single-valued, and its image is the whole enum.

    A kind with no class is an exception discovered in the middle of D9's attribution; a class
    no kind maps to is a column that is empty in every report. Both are cheap here and
    expensive there.
    """
    assert set(ASSET_CLASS_OF) == set(InstrumentKind)
    assert set(ASSET_CLASS_OF.values()) == set(AssetClass)
    for kind, klass in ASSET_CLASS_OF.items():
        assert isinstance(klass, AssetClass), kind

    classes = REFERENCE_BOOK.asset_classes
    assert len(classes) >= 4, f"the structure is sold as multi-asset and spans {classes}"
    assert AssetClass.RATES in classes and AssetClass.FX in classes

    single = US_CASH_BOOK.restricted_to(
        "usd_only", [leg.leg_id for leg in US_CASH_BOOK.legs if leg.currency is Currency.USD]
    )
    by_class = single.gross_by_asset_class()
    assert sum(by_class.values()) == pytest.approx(single.gross_notional)


def test_the_scenario_sign_matrix_is_complete_and_only_claims_signs() -> None:
    """C22. B22, DD20. The source's justification, in a form that can be scored.

    The structure was argued for on the ground that its legs profit from different aspects of
    one thesis, with four scenarios naming the winners in each. That is a claim about signs,
    so it is recorded as signs -- one cell per leg per scenario, before any replay, and D12
    scores it.

    The source's "wins" versus "partially wins" distinction is deliberately absent: it is a
    magnitude claim with no stated threshold, and recording it would be inventing a bar after
    the fact. What was asserted is a direction.
    """
    assert set(SCENARIO_SIGNS) == {
        "fed_signals_fewer_cuts",
        "supply_shock",
        "inflation_surprises_higher",
        "everything_goes_wrong",
    }

    legs = set(REFERENCE_BOOK.leg_ids)
    for scenario, cells in SCENARIO_SIGNS.items():
        assert set(cells) == legs, f"{scenario} does not cover the book exactly"
        for leg_id, sign in cells.items():
            assert sign in (-1, 0, 1), f"{scenario}/{leg_id} carries {sign!r}, not a sign"
        assert any(sign != 0 for sign in cells.values()), f"{scenario} claims nothing"

    stressed = SCENARIO_SIGNS["everything_goes_wrong"]
    assert stressed["us_10y_call"] == +1, "the convex leg is the one claimed to pay in the tail"
    assert sum(1 for sign in stressed.values() if sign < 0) == 5

    # The claim H4 is pre-registered against, in its cheapest observable form: two legs whose
    # sign patterns agree across every scenario are not two bets, whatever the leg table says.
    # No covariance is needed to see this -- it is already in the source's own table.
    patterns = {
        leg_id: tuple(SCENARIO_SIGNS[s][leg_id] for s in sorted(SCENARIO_SIGNS)) for leg_id in legs
    }
    identical = {(a, b) for a in patterns for b in patterns if a < b and patterns[a] == patterns[b]}

    # Pinned as measured, and the prediction that named a different pair is scored as MISSED in
    # the pre-commit rather than edited away. The guess was `us_2y` / `us_10y`, on the reasoning
    # that two Treasury legs must be one bet; they are NOT identical here, because the source
    # gives leg 2 the supply-shock win and leg 1 none. What is identical is `us_2y` / `eurusd` --
    # and the source argues for leg 4 on the ground that "FX is driven by different flows than
    # rates". Under its own four scenarios the short EUR/USD is indistinguishable from the short
    # two-year: both win only on fewer cuts, both lose in the tail, both are flat elsewhere.
    assert identical == {("eurusd", "us_2y")}, (
        f"the sign matrix's collapsing pair has moved: {sorted(identical)}"
    )
    assert patterns["us_2y"] != patterns["us_10y"], (
        "leg 1 and leg 2 are distinguished by the supply-shock column, which is the "
        "policy-versus-term-premium separation the source is built on"
    )

    # And the null, without which the collision above is an anecdote (DD21).
    #
    # Four scenarios over three values is 81 patterns. Six legs drawn uniformly from 81 give a
    # 17.3% chance of some collision by luck alone, and the tail column is -1 for five of the
    # six legs, so conditional on it only three columns discriminate: 27 patterns, five legs,
    # 32.5%. A one-in-three event is not evidence of anything.
    #
    # What is NOT one-in-three is that the collision lands on the leg the source singles out as
    # the diversifier. That is a one-cell test named in advance by the source itself, not a
    # search over fifteen pairs: 6.0% uniform, 14.0% conditional. Still not significance -- and
    # the honest reading is that the collision is corroborating detail, while the finding that
    # carries weight is the one below.
    informative = [s for s in SCENARIO_SIGNS if len(set(SCENARIO_SIGNS[s].values())) > 1]
    blank = sum(1 for cells in SCENARIO_SIGNS.values() for sign in cells.values() if sign == 0)
    total = sum(len(cells) for cells in SCENARIO_SIGNS.values())

    assert blank / total > 0.4, (
        "over 40% of the source's own cells are 'no claim', which is why the table cannot "
        "carry the diversification conclusion drawn from it in EITHER direction"
    )
    tail = SCENARIO_SIGNS["everything_goes_wrong"]
    assert sum(1 for sign in tail.values() if sign == -1) == 5, (
        "the tail column is near-constant and therefore discriminates almost nothing; a "
        "scenario that moves five of six legs the same way is not a test of their independence"
    )
    assert len(informative) == 4 and len(SCENARIO_SIGNS) < len(legs), (
        "four scenarios cannot separate six legs even in principle, which is the finding: the "
        "table is under-determined, and D12's dated replay is what replaces it"
    )
