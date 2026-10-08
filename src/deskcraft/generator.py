"""D7b -- the leg generator, and the cost-aware stopping rule.

`BUILD_ORDER_D3_D16.md` §1 settles the rule and §4's row commissions this module. Risk budget
in, leg count out: there is no leg-count input and no cap anywhere below.

**The parameter §1 did not name.** §1.3's hurdle compares a gain in view fidelity -- a
dimensionless number -- against `costs.cost_per_dv01`, which its own docstring says is *"in basis
points of yield"*. Those are not the same unit, and `COST_HURDLE = 1.0` fixes the threshold rather
than the units. What closes the gap is a stated view magnitude, `VIEW_MOVE_BP`, and it is fixed
here for `AMENDMENT_A2` §2's reason applied one parameter over: it is a rung of a ladder §3.5
already reports, so it is not a degree of freedom. `C107` holds the identity.

**What this module deliberately does not read.** `views.ViewFidelity.dominant_share` -- carried
item X3, which says the statistic over-attributes on a non-orthogonal basis and that D7b would
rank legs with it two packages before D9 can fix it. The ordering here is `cosine`, an angle
between two vectors, which claims no decomposition and is unharmed by the basis's angles. `C111`
holds that as a census of the tree rather than as this sentence.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date

from deskcraft.book import (
    Book,
    Component,
    Currency,
    Direction,
    Instrument,
    InstrumentKind,
    Leg,
    Neutrality,
    Notional,
)
from deskcraft.costs import (
    COST_HURDLE,
    COST_MULTIPLIERS,
    COST_OF,
    DurationConvention,
    cost_per_dv01,
    gross_dv01,
)
from deskcraft.factors import FACTOR_SERIES, REAL_SERIES, FactorBasis
from deskcraft.sensitivity import TENOR_OF, leg_sensitivity
from deskcraft.views import UnreachableFactor, View, compile_view

__all__ = [
    "CANDIDATE_SERIES",
    "UNIT_NOTIONAL",
    "VIEW_MOVE_BP",
    "Addition",
    "Cell",
    "Forced",
    "Removal",
    "Selection",
    "SelectionLadder",
    "candidate_legs",
    "enumerate_universe",
    "select",
    "selection_ladder",
    "unit_risk_exposure",
]


#: The move the stated view asserts, in basis points, which is the unit the benefit side of
#: §1.3's hurdle is missing (DD110).
#:
#: **Fixed at 1.0 because it is not a degree of freedom**, by `AMENDMENT_A2` §2's argument applied
#: to the quantity that document did not name. Only the quotient `move / multiplier` enters the
#: comparison, so the selection at multiplier `m` and move `1.0` is the same function as the
#: selection at multiplier `1.0` and move `1/m` -- measured leg for leg at all four rungs by
#: `C107`. One basis point is the unit `cost_per_dv01` is already quoted in, which is the same
#: move `AMENDMENT_A2` made in setting `HURDLE_HOLDING_YEARS` to the unit of the annualisation.
#:
#: **And the collapse is not reassuring, which is why the number is here rather than inline.**
#: Read as view magnitudes, `COST_MULTIPLIERS`' four rungs span two basis points down to a
#: quarter of one. A macro view that yields rise is tens of basis points, and at ten the leg
#: count is six rather than two -- so the ladder does not span the region a reader assumes, and
#: `H9`'s margin is a property of the grid. The pre-commit's §2.3 reports the sweep.
VIEW_MOVE_BP = 1.0

#: The notional every candidate is evaluated at. **It cancels**: `cost_per_dv01` is a ratio in
#: which the notional divides out exactly, and the exposure is normalised by the same leg's gross
#: DV01, so nothing below is a function of this number. Stated once, as a constant, rather than
#: defaulted per call -- and `C107` proves the invariance rather than asserting it, because a
#: quantity that is claimed not to matter is exactly the kind that turns out to.
UNIT_NOTIONAL = 1.0e8

#: Every series a generated structure may name: it has a cost profile **and** a direction in the
#: factor basis. Derived from the two registers, never listed, so a series added to either moves
#: this and `C103` turns red until the count is restated.
#:
#: Eleven today. The intersection drops six priced series the basis cannot see -- `DEXUSEU` and
#: the five `DGS` constant maturities -- and two basis series nothing prices, `GZ_SPREAD` and
#: `DE_ZERO_10Y`. It also drops `DGS3MO` and `DGS6MO` **without naming them**, which is the
#: question D7a left open when it found the two front-end series D5 graded have a half-spread and
#: no computable duration. They are excluded one step earlier than the denominator, by not being
#: in the basis at all, and `C104` holds that this is the reason and not a coincidence.
CANDIDATE_SERIES: tuple[str, ...] = tuple(
    series for series in FACTOR_SERIES if series in COST_OF
)

#: The as-of date every generated `Book` carries. The panel date D7a's bars already measure at.
GENERATED_AS_OF = date(2014, 12, 24)


class NoCandidate(ValueError):
    """The universe is empty, or every candidate refuses a price (DD110)."""


def _kind(series: str) -> InstrumentKind:
    return InstrumentKind.REAL_YIELD if series in REAL_SERIES else InstrumentKind.ZERO_YIELD


def _instrument(symbol: str, weights: Sequence[tuple[str, float]]) -> Instrument:
    """One enumerated structure. Neutrality is derived from the coefficients, never asserted.

    **`CASH` and not `DV01`**, which is D4's carried question answered. A `(+1, -1)` pair on one
    notional buys and sells equal cash by construction, so cash-neutrality is true of it without
    being measured. It is *not* DV01-neutral -- `SVENY05` is a continuously compounded zero and
    `DFII5` a par quote, so the same pair leaves 370.67 per basis point on $50m, which D4
    measured and `reference.py` carries annotated. Nothing generated here declares a neutrality it
    has not got, and `C109` holds that over the whole enumeration.
    """
    tenor = max(TENOR_OF[series] for series, _ in weights)
    kinds = {_kind(series) for series, _ in weights}
    kind = InstrumentKind.BREAKEVEN if len(kinds) > 1 else kinds.pop()
    balanced = abs(math.fsum(coefficient for _, coefficient in weights)) <= 1e-12
    return Instrument(
        symbol=symbol,
        kind=kind,
        currency=Currency.USD,
        tenor_years=tenor,
        components=tuple(
            Component(series, coefficient, Currency.USD) for series, coefficient in weights
        ),
        neutrality=Neutrality.CASH if balanced else Neutrality.NONE,
    )


def enumerate_universe() -> tuple[Instrument, ...]:
    """Every structure the rule in the pre-commit's §1.1 admits, over `CANDIDATE_SERIES`.

    Three families, with the coefficients §3.1 already prices: an outright `(+1)`, a spread
    `(+1, -1)` over each unordered pair, and a butterfly `(+1, -2, +1)` over each curve-ordered
    triple with the body in the middle. Eleven, fifty-five and one hundred and sixty-five, which
    is **231** -- against the row's *"~300"*, which is a plan number and not a measured one. The
    count follows from this rule; wings at any position would give 495, and neither figure is
    *the* universe.

    Direction is **not** enumerated here. It belongs to the leg, not to the instrument, so each
    structure is evaluated both ways by `candidate_legs` and 231 structures give 462 legs.
    """
    ordered = sorted(CANDIDATE_SERIES, key=lambda series: (TENOR_OF[series], series))
    out: list[Instrument] = [
        _instrument(f"OUT_{series}", ((series, 1.0),)) for series in ordered
    ]
    for i in range(len(ordered)):
        for j in range(i + 1, len(ordered)):
            near, far = ordered[i], ordered[j]
            out.append(_instrument(f"SPR_{near}_{far}", ((near, 1.0), (far, -1.0))))
    for i in range(len(ordered)):
        for j in range(i + 1, len(ordered)):
            for k in range(j + 1, len(ordered)):
                low, body, high = ordered[i], ordered[j], ordered[k]
                out.append(
                    _instrument(
                        f"FLY_{low}_{body}_{high}",
                        ((low, 1.0), (body, -2.0), (high, 1.0)),
                    )
                )
    return tuple(out)


def candidate_legs(
    universe: Sequence[Instrument] | None = None, notional: float = UNIT_NOTIONAL
) -> tuple[Leg, ...]:
    """Each structure as two legs, one per direction. The 462 the evaluation count counts."""
    structures = enumerate_universe() if universe is None else tuple(universe)
    return tuple(
        Leg(
            leg_id=f"{instrument.symbol.lower()}_{direction.name.lower()}",
            instrument=instrument,
            direction=direction,
            notional=Notional(notional, Currency.USD),
        )
        for instrument in structures
        for direction in Direction
    )


def unit_risk_exposure(
    leg: Leg, yields: Mapping[str, float], convention: DurationConvention
) -> tuple[float, ...]:
    """The leg's signed DV01 by series, divided by its own gross DV01, over `FACTOR_SERIES`.

    Dividing by gross DV01 is what makes the vector a *direction per unit of risk taken*, which is
    the object the stopping rule compares -- and the same denominator `cost_per_dv01` uses, so a
    cell of the ladder is one world rather than an exposure measured one way and priced another.
    D4's `leg_sensitivity` supplies the numerator and nothing re-signs it: `RATE_SENSE_OF` already
    decided whether long means long the price or long the rate.
    """
    per_series: dict[str, float] = {}
    for component in leg_sensitivity(leg, yields).components:
        per_series[component.series] = per_series.get(component.series, 0.0) + component.dv01
    scale = gross_dv01(leg, yields, convention)
    return tuple(per_series.get(series, 0.0) / scale for series in FACTOR_SERIES)


def _cosine(vector: Sequence[float], target: Sequence[float]) -> float:
    """The angle between a book's exposure and the compiled view, in series space.

    Zero for an empty book, which is what makes the first addition's gain its own fidelity and is
    the only place this differs from `views.fidelity` -- which refuses an empty book, correctly,
    because a fidelity of zero and a book of nothing are different statements.
    """
    norm = math.sqrt(math.fsum(value * value for value in vector))
    if norm == 0.0:
        return 0.0
    return math.fsum(a * b for a, b in zip(vector, target)) / norm


@dataclass(frozen=True, slots=True)
class Cell:
    """One cell of §3.5's ladder, as the stopping rule runs at it."""

    multiplier: float
    convention: DurationConvention


@dataclass(frozen=True, slots=True)
class Addition:
    """One leg the greedy took, and the number that defends its place."""

    leg_id: str
    symbol: str
    direction: Direction
    #: The book's cosine after this leg, minus before it.
    gain: float
    cost_per_dv01: float
    #: `gain * VIEW_MOVE_BP / (multiplier * cost_per_dv01)`, against `COST_HURDLE`.
    ratio: float


@dataclass(frozen=True, slots=True)
class Removal:
    """§1.5's leave-one-out: what the book's fidelity is without one surviving leg."""

    leg_id: str
    cosine_without: float
    loss: float


@dataclass(frozen=True, slots=True)
class Forced:
    """§1.6's counterfactual: what forcing a count costs, with the price tag attached."""

    legs: int
    cosine: float
    #: Signed. Positive where forcing the count buys fidelity the rule declined to pay for.
    against_stopped: float


@dataclass(frozen=True, slots=True)
class Selection:
    """What the rule returns at one cell. A count is never published without its cell.

    An **empty** selection is an outcome and not a failure: at a quarter of a basis point of
    assumed move, no structure in the universe repays its spread, and that is a true statement
    about costs. `refused` carries the best candidate that did not clear the hurdle, so a zero
    cannot be read as the rule breaking. `book()` refuses rather than inventing a leg, because
    `Book.legs` refuses to be empty and forcing one would be this engine stating a position.
    """

    cell: Cell
    view: View
    additions: tuple[Addition, ...]
    cosine: float
    #: Candidate legs scored, summed over rounds. The number D15's trial adjustment is owed.
    evaluations: int
    #: `(leg_id, ratio)` of the best addition that failed the hurdle, or `None` at the cap.
    refused: tuple[str, float] | None
    leave_one_out: tuple[Removal, ...]
    counterfactual: tuple[Forced, ...]

    def __len__(self) -> int:
        return len(self.additions)

    @property
    def leg_ids(self) -> tuple[str, ...]:
        return tuple(addition.leg_id for addition in self.additions)

    def book(self, book_id: str, thesis: str) -> Book:
        """The selection as a `Book`, or a refusal when the rule took nothing."""
        if not self.additions:
            raise NoCandidate(
                f"the rule took no structure at {self.cell.multiplier}x under "
                f"{self.cell.convention}, so there is no book. The best candidate refused was "
                f"{self.refused!r} against a hurdle of {COST_HURDLE}. That is a statement about "
                "costs at this cell and not a failure of the rule; the other cells of the ladder "
                "are where it is read."
            )
        universe = {leg.leg_id: leg for leg in candidate_legs()}
        return Book(
            book_id=book_id,
            as_of=GENERATED_AS_OF,
            thesis=thesis,
            legs=tuple(universe[leg_id] for leg_id in self.leg_ids),
        )


def _prepared(
    yields: Mapping[str, float],
    convention: DurationConvention,
    pool: tuple[str, ...] | None = None,
) -> tuple[tuple[Leg, tuple[float, ...], float], ...]:
    """Every candidate leg with its unit-risk direction and its cost, at one convention.

    `pool`, when given, keeps only structures whose every series is in it (DD162).
    """
    return tuple(
        (leg, unit_risk_exposure(leg, yields, convention), cost_per_dv01(leg, yields, convention))
        for leg in candidate_legs()
        if pool is None or all(series in pool for series in leg.instrument.series)
    )


def select(
    view: View,
    basis: FactorBasis,
    yields: Mapping[str, float],
    *,
    multiplier: float = 1.0,
    convention: DurationConvention = DurationConvention.AS_QUOTED,
    move_bp: float = VIEW_MOVE_BP,
    cap: int = 40,
    pool: tuple[str, ...] | None = None,
) -> Selection:
    """§1's stopping rule at one cell of the ladder. Risk budget in, leg count out.

    Greedy, as §1.2 states: the structure with the highest fidelity enters first, then whichever
    addition most improves the book, one at a time, until the next-best fails the hurdle.

    **Every leg carries equal gross DV01**, which is stated rather than optimised. The budget's
    *level* then cancels out of the cosine entirely, so the leg count is a function of the
    budget's composition and not of its size -- and that is a consequence of `AMENDMENT_A2` §2's
    substitution of gross DV01 for expected shortfall, worth naming: **gross DV01 is strictly
    additive, so it prices no diversification.** The greedy still adds legs, because the cosine is
    normalised by the net exposure's norm and a leg earns its place by cancelling off-thesis
    exposure -- F3's subject -- but the mechanism is geometric until D9's component ES arrives.
    The counts here are a lower bound on the count under ES, not an estimate of it.

    `cap` exists so a caller can measure the ceiling rather than to bound the answer; §1 has no
    leg cap and the hurdle is what stops the rule at every cell of the reported ladder.

    `pool` is for a construction dated before every candidate series existed (DD162): `DFII30`
    opens in 2010, so a book built in 2003 may not name it. The default is every candidate,
    which is the universe H3 and H9 were scored at, and nothing published is moved by it.
    """
    # X19, DD152: a factor reached by only part of its series is refused for selection, in
    # `views.fidelity`'s shape. Otherwise a cross-market view returns a US ten-year leg and an
    # empty selection blames costs for an absence of data, and the caller cannot tell which.
    for term in view.terms:
        available = CANDIDATE_SERIES if pool is None else tuple(s for s in CANDIDATE_SERIES if s in pool)
        absent = [s for s in basis.reaches(term.factor) if s not in available]
        if absent:
            raise UnreachableFactor(
                f"{term.factor} reaches {basis.reaches(term.factor)} and the candidate pool "
                f"carries none of {absent}. Selecting on the rest would return a book about a "
                "different factor under this one's name, so the view is refused for selection."
            )
    target = compile_view(view, basis)
    norm = target.norm
    if norm == 0.0:
        raise NoCandidate(f"{view!r} compiles to a zero direction; nothing can point along it")
    unit_target = tuple(value / norm for value in target.vector)

    prepared = _prepared(yields, convention, pool)
    exposure = [0.0] * len(FACTOR_SERIES)
    path: list[tuple[Addition, float, int, list[float]]] = []

    # One pass to the geometric ceiling, ignoring the hurdle. The rule's answer is a prefix of
    # this path and §1.6's counterfactual is the rest of it, so continuing past the stop costs
    # nothing and is the only way the price of a forced count can be quoted (DD110).
    while len(path) < cap:
        here = _cosine(exposure, unit_target)
        seen = {row[0].symbol for row in path}
        rounds = 0
        best: tuple[float, Leg, float, float, list[float]] | None = None
        for leg, direction_vector, cost in prepared:
            if leg.instrument.symbol in seen:
                continue
            rounds += 1
            trial = [a + b for a, b in zip(exposure, direction_vector)]
            gain = _cosine(trial, unit_target) - here
            ratio = gain * move_bp / (multiplier * cost)
            if best is None or ratio > best[0]:
                best = (ratio, leg, gain, cost, trial)
        if best is None:
            break
        ratio, leg, gain, cost, trial = best
        if gain <= 0.0:
            # The ceiling: no remaining structure points any more of the book at the view. This
            # is where the rule runs out of fidelity rather than out of money, and the count here
            # bounds every count a cheaper cost model could produce.
            path.append(
                (
                    Addition(leg.leg_id, leg.instrument.symbol, leg.direction, gain, cost, ratio),
                    here,
                    rounds,
                    exposure,
                )
            )
            break
        exposure = trial
        path.append(
            (
                Addition(leg.leg_id, leg.instrument.symbol, leg.direction, gain, cost, ratio),
                _cosine(exposure, unit_target),
                rounds,
                trial,
            )
        )

    stop = len(path)
    for index, (addition, _, _, _) in enumerate(path):
        if addition.ratio < COST_HURDLE:
            stop = index
            break
    taken = [row[0] for row in path[:stop]]
    refused = (path[stop][0].leg_id, path[stop][0].ratio) if stop < len(path) else None
    evaluations = sum(row[2] for row in path[: stop + 1])
    stopped = path[stop - 1][1] if stop else 0.0

    by_id = {leg.leg_id: vector for leg, vector, _ in prepared}
    removals = []
    for addition in taken:
        rest = [0.0] * len(FACTOR_SERIES)
        for other in taken:
            if other.leg_id == addition.leg_id:
                continue
            rest = [a + b for a, b in zip(rest, by_id[other.leg_id])]
        without = _cosine(rest, unit_target)
        removals.append(Removal(addition.leg_id, without, stopped - without))

    return Selection(
        cell=Cell(float(multiplier), convention),
        view=view,
        additions=tuple(taken),
        cosine=stopped,
        evaluations=evaluations,
        refused=refused,
        leave_one_out=tuple(removals),
        counterfactual=tuple(
            Forced(count + 1, value, value - stopped)
            for count, (_, value, _, _) in enumerate(path)
            if count + 1 <= _ceiling(path)
        ),
    )


def _ceiling(path: Sequence[tuple[Addition, float, int, Sequence[float]]]) -> int:
    """How many legs the greedy would take if every structure were free.

    The last step of the path is the one that did not raise the cosine, so it is the ceiling's
    witness rather than part of it. A path that hit `cap` has no witness and the whole path is
    reported.
    """
    if path and path[-1][0].gain <= 0.0:
        return len(path) - 1
    return len(path)


@dataclass(frozen=True, slots=True)
class SelectionLadder:
    """§3.5's ladder, carrying a whole selection at every cell rather than a count.

    Eight cells, reported together and never one at a time -- carried item **X12**, which says
    `COST_HURDLE = 1.0` removes a parameter only while the ladder is reported. A caller holding
    this object cannot quote a leg count without the cell it came from, because `Selection` is
    keyed by its `Cell`.
    """

    view: View
    cells: tuple[Selection, ...]
    #: Which of §3.2's four cost terms the numbers include. Never assume all four (X11).
    terms: tuple[str, ...]

    @property
    def leg_counts(self) -> tuple[tuple[Cell, int], ...]:
        return tuple((selection.cell, len(selection)) for selection in self.cells)

    @property
    def flips(self) -> bool:
        """True when the count is not the same at every cell.

        §3.5's own stated trigger: *"a flip between 1x and 2x means the honest headline is that
        the result is a statement about costs rather than about structure."* It fires on this
        tree, and `C105` records that as a measured fact rather than a possibility.
        """
        return len({count for _, count in self.leg_counts}) > 1

    @property
    def evaluations(self) -> int:
        return sum(selection.evaluations for selection in self.cells)


def selection_ladder(
    view: View,
    basis: FactorBasis,
    yields: Mapping[str, float],
    move_bp: float = VIEW_MOVE_BP,
) -> SelectionLadder:
    """The whole selection at every rung of `COST_MULTIPLIERS`, crossed with X5's two conventions.

    The ladder is swept and never indexed. `C102` measures that by AST, after two landed documents
    said no bar could tell sweeping from picking a rung; this is the first module the bar binds on.
    """
    cells = tuple(
        select(view, basis, yields, multiplier=multiplier, convention=convention, move_bp=move_bp)
        for convention in DurationConvention
        for multiplier in COST_MULTIPLIERS
    )
    return SelectionLadder(view=view, cells=cells, terms=("half_spread",))
