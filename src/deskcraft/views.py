"""The view language, and what a book's fidelity to a view actually is. D6, DD66-DD68, C65-C71.

A **view** is a statement about how the market moves, in a closed grammar of six terms each
carrying a direction. It is never a statement that a position is worth holding, and the
distinction is the boundary of this repository rather than a nicety: `compile_view` turns
*"the level rises"* into a direction in series space, and `fidelity` reports how much of a
**stated** book already points that way. Neither function proposes a book, sizes one, or
ranks one. D7b generates legs and reads this; D9's F3 flag reads it to find risk pointing
somewhere the view never asked for.

**The names live in `factors.py` and the move lives here** (DD68). A `Factor` is a thing the
market does and exists whether anyone has a view on it; a `Move` is the part somebody asserts.
`UP = 1` and `DOWN = -1`, so the member's *value* is the sign and compiling a term is one
multiplication with no lookup table -- D2's `Direction` decision, for D2's reason: there is
exactly one representation of a downward view rather than two that can disagree.

**It is `Move` and not `ViewDirection`, and D2's C10 is why.** The first draft of this module
called it `ViewDirection`, and C10 -- which asserts `Direction` and `Notional` are defined in
`book.py` and nowhere else, and scans for *near-names* precisely because *"a near-name growing
beside the real one is how 'one binding site' stops being true without anything being
renamed"* -- turned red on it. It was right to. The two types are structurally identical, an
`IntEnum` whose value is a sign, and their subjects are opposite: `Direction` is the sign of a
**position** and this is the sign of a **market move**. Nothing in the names would have told a
reader which, and the rule carried from curvecast is that a boundary hit is fixed by renaming
the symbol, never by exempting it. The field is `move` for the same reason.

**The reference view is `(LEVEL, UP)` and it was fixed before any loading was computed**
(DD66). `REFERENCE_THESIS` is *"Fewer policy cuts than priced, plus a fiscal-driven repricing
of the term premium"*, and `reference.py` glosses leg 1 as the policy-expectations component
and leg 2 as the term-premium one. Both clauses raise yields. The thesis names two **drivers**
and says nothing about which end of the curve moves further, so reading a steepener into it
would be an inference made by the very package about to be graded on whether the book matches
it. `REFERENCE_VIEW_TWO_TERM` is the alternative reading, written down at the same time so
neither can be presented afterwards as the one that was meant.

**H3 is dominance *and* sign** (DD67). *"The book loads on the view's factor"* is qualitative
and had to be made checkable: `loads_on_view` is true when the view's factor carries the
largest absolute loading of the six **and** that loading's sign agrees with the direction the
view states. Dominance alone would pass a book positioned for exactly the opposite view, which
is not a subtle failure -- it is the whole claim, backwards.

**`dominant_share` is not a variance decomposition.** The six directions are not orthogonal
(`factors.FactorBasis.gram`), so the loadings do not partition anything. The share is a
readable magnitude and the docstring on the field says what it is not.

**A view naming a factor the book structurally cannot reach is refused** (DD65). D4's DD55
made the same call one layer down: a `CurveShift` naming a series no leg holds raises,
*"because a mistyped mnemonic that silently contributes nothing is a stress test reporting 'no
effect' for a reason that has nothing to do with the book."* Asking `US_CASH_BOOK` for its
`CREDIT_VS_RATES` fidelity raises, because no leg reaches `GZ_SPREAD` and a reported zero
would be indistinguishable from a measured absence of credit risk. **Partial reach is not
refusal**: the book holds `SVENY10` and therefore genuinely loads on `CROSS_MARKET`, because
holding one side of a spread is an exposure to that spread.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import IntEnum

from deskcraft.book import Book
from deskcraft.factors import FACTOR_SERIES, Factor, FactorBasis
from deskcraft.sensitivity import book_dv01

__all__ = [
    "REFERENCE_VIEW",
    "REFERENCE_VIEW_TWO_TERM",
    "ExposureTerm",
    "HedgeTarget",
    "Move",
    "TargetVector",
    "UnreachableFactor",
    "View",
    "ViewFidelity",
    "ViewTerm",
    "book_exposure",
    "compile_view",
    "fidelity",
]


class Move(IntEnum):
    """Which way a view says a factor moves. The member value is the sign (DD68)."""

    UP = 1
    DOWN = -1


class UnreachableFactor(ValueError):
    """A view naming a factor no leg of the book can reach (DD65)."""


@dataclass(frozen=True, slots=True)
class ViewTerm:
    """One term of a view: a factor, and which way it is asserted to move."""

    factor: Factor
    move: Move

    def __post_init__(self) -> None:
        if not isinstance(self.factor, Factor):
            raise TypeError(f"ViewTerm.factor must be a Factor, got {self.factor!r}")
        if not isinstance(self.move, Move):
            raise TypeError(f"ViewTerm.move must be a Move, got {self.move!r}")

    @property
    def sign(self) -> float:
        return float(int(self.move))


@dataclass(frozen=True, slots=True)
class View:
    """A stated macro view: one or more directed factors, each factor named at most once.

    Deliberately not a claim that anything should be held. A view is an input to this engine
    in the same sense a book is -- somebody states it, and what is computed is what follows.
    """

    terms: tuple[ViewTerm, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.terms, tuple):
            raise TypeError(f"View.terms must be a tuple, got {type(self.terms).__name__}")
        if not self.terms:
            raise ValueError(
                "a view states nothing; every statistic below divides by its target's norm"
            )
        for term in self.terms:
            if not isinstance(term, ViewTerm):
                raise TypeError(f"View.terms holds a {type(term).__name__}")
        named = [term.factor for term in self.terms]
        if len(set(named)) != len(named):
            repeated = sorted({f for f in named if named.count(f) > 1})
            raise ValueError(
                f"a view names {repeated} twice; one factor cannot be asserted to move two "
                "ways, and a repeated term would double its weight in the target"
            )

    @classmethod
    def of(cls, *terms: tuple[Factor, Move]) -> View:
        """`View.of((Factor.LEVEL, Move.UP))`, which is how every view here is written."""
        return cls(tuple(ViewTerm(factor, move) for factor, move in terms))

    @property
    def factors(self) -> tuple[Factor, ...]:
        return tuple(term.factor for term in self.terms)

    def move_of(self, factor: Factor) -> Move | None:
        for term in self.terms:
            if term.factor is factor:
                return term.move
        return None


#: The reference structure's thesis, compiled from its own text before any loading existed
#: (DD66). One term: both clauses raise yields and neither says which end moves further.
REFERENCE_VIEW = View.of((Factor.LEVEL, Move.UP))

#: The alternative reading, written at the same time as the one above so that the choice
#: between them cannot be made after seeing which scores better. It reads the term-premium
#: clause as a statement about the long end specifically.
REFERENCE_VIEW_TWO_TERM = View.of((Factor.LEVEL, Move.UP), (Factor.SLOPE, Move.UP))


@dataclass(frozen=True, slots=True)
class TargetVector:
    """What a view compiles to: coordinates in the factor basis, and the direction they span.

    Both forms travel because both are used. `coordinates` is the view as the grammar states
    it -- what §4's row calls a target vector in the DEV factor basis. `vector` is the same
    thing in series space, which is the only space a book's DV01 also lives in.
    """

    coordinates: dict[Factor, float]
    series: tuple[str, ...]
    vector: tuple[float, ...]

    @property
    def norm(self) -> float:
        return math.sqrt(math.fsum(value * value for value in self.vector))


@dataclass(frozen=True, slots=True)
class ExposureTerm:
    """One stated exposure as the grammar reads it (D18, DD197): a firm's P&L per unit **rise**
    in one series, sign times amount. Not a view: nobody asserts the series will move.
    """

    series: str
    weight: float

    def __post_init__(self) -> None:
        if self.series not in FACTOR_SERIES:
            raise UnreachableFactor(f"{self.series!r} has no direction in the factor basis")
        if not math.isfinite(self.weight) or self.weight == 0.0:
            raise ValueError(f"an exposure of {self.weight!r} states nothing to hedge")


@dataclass(frozen=True, slots=True)
class HedgeTarget:
    """What a hedge points along: stated exposures, sign-flipped (D18, DD197).

    It states no factor, so `terms` is empty and D7b's factor-reach loop has nothing to iterate.
    Reach is checked where a target is built, by `hedging.hedge_target`, against the candidate
    pool: X19's rule applied to a series rather than to a factor.
    """

    exposures: tuple[ExposureTerm, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.exposures, tuple) or not self.exposures:
            raise ValueError("a hedge target needs at least one exposure")
        for term in self.exposures:
            if not isinstance(term, ExposureTerm):
                raise TypeError(f"HedgeTarget.exposures holds a {type(term).__name__}")
        named = [term.series for term in self.exposures]
        if len(set(named)) != len(named):
            raise ValueError(f"a hedge target names a series twice: {named}")

    @property
    def terms(self) -> tuple[ViewTerm, ...]:
        return ()


def compile_view(view: View | HedgeTarget, basis: FactorBasis) -> TargetVector:
    """Turn a stated view into a direction in series space.

    The signed sum of its terms' factor directions. Because the factors are not orthogonal
    (DD64), a two-term target is **not** the hypotenuse of two independent axes and its norm
    is not the root sum of squares; it is the honest sum of two overlapping directions.

    A `HedgeTarget` compiles to its exposures sign-flipped, series by series, with no factor
    coordinates: the hedge gains where the firm loses (DD197).
    """
    if isinstance(view, HedgeTarget):
        weights = {term.series: term.weight for term in view.exposures}
        vector = tuple(0.0 - weights.get(series, 0.0) for series in basis.series)
        return TargetVector(coordinates={}, series=basis.series, vector=vector)
    coordinates = {term.factor: term.sign for term in view.terms}
    vector = tuple(
        math.fsum(
            sign * basis.vector(factor)[position] for factor, sign in coordinates.items()
        )
        for position in range(len(basis.series))
    )
    return TargetVector(coordinates=coordinates, series=basis.series, vector=vector)


def book_exposure(book: Book, yields: Mapping[str, float]) -> dict[str, float]:
    """The book's signed DV01 collapsed by series, in the order factors are indexed.

    D4's `book_dv01` and nothing else -- no re-signing, no re-weighting. `RATE_SENSE_OF`
    already decided whether `LONG` means long the price or long the rate, so a positive entry
    here is P&L per basis point rise in that series and the inner product with a factor
    direction needs no further convention. A leg whose sense is `NONE` contributes no series
    at all, which is why `eurusd` is absent rather than zero.

    Refuses the whole book if any leg is `UNPRICEABLE`, because `book_dv01` does.
    """
    out: dict[str, float] = {}
    for sensitivity in book_dv01(book, yields).values():
        for component in sensitivity.components:
            out[component.series] = out.get(component.series, 0.0) + component.dv01
    return out


@dataclass(frozen=True)
class ViewFidelity:
    """How much of a stated book already points the way a stated view says the market moves.

    Never a score of the book, and never a recommendation. The number D7b will maximise and
    D9's F3 flag will read, reported here for a book somebody else wrote.
    """

    book_id: str
    view: View
    #: Signed, per basis point of each factor's move, in the book's notional currency.
    loadings: dict[Factor, float]
    #: Factors the book puts no weight on at all. Their loading is a **structural** zero, not
    #: a measured one, and they are listed so the two cannot be confused (D4's `RateSense`
    #: distinction, one layer up).
    unreachable: tuple[Factor, ...]
    dominant: Factor
    #: `|largest| / sum of |all six|`. **Not a variance share**: the six directions are not
    #: orthogonal (DD64), so these loadings decompose nothing.
    dominant_share: float
    #: Cosine between the book's exposure and the compiled target, in series space.
    cosine: float
    #: DD67: the view's factor is dominant **and** its sign agrees with the stated direction.
    loads_on_view: bool


def fidelity(
    book: Book, view: View, basis: FactorBasis, yields: Mapping[str, float]
) -> ViewFidelity:
    """Score a stated book against a stated view (DD67). Refuses an unreachable factor (DD65)."""
    exposure = book_exposure(book, yields)
    held = {series for series, value in exposure.items() if value != 0.0}

    unreachable = tuple(
        factor for factor in Factor if not (set(basis.reaches(factor)) & held)
    )
    refused = [factor for factor in view.factors if factor in unreachable]
    if refused:
        detail = ", ".join(
            f"{factor} (reaches {basis.reaches(factor)})" for factor in refused
        )
        raise UnreachableFactor(
            f"{book.book_id!r} puts no weight on any series of {detail}; it holds "
            f"{tuple(sorted(held))}. The view is refused rather than scored at zero, because a "
            "fidelity of zero reported here would be indistinguishable from a book measured "
            "and found to carry none of that risk."
        )

    vector = [exposure.get(series, 0.0) for series in FACTOR_SERIES]
    loadings = {
        factor: math.fsum(a * b for a, b in zip(vector, basis.vector(factor)))
        for factor in Factor
    }

    total = math.fsum(abs(value) for value in loadings.values())
    dominant = max(loadings, key=lambda factor: abs(loadings[factor]))
    stated = view.move_of(dominant)
    agrees = stated is not None and math.copysign(1.0, loadings[dominant]) == float(int(stated))

    target = compile_view(view, basis)
    exposure_norm = math.sqrt(math.fsum(value * value for value in vector))
    denominator = exposure_norm * target.norm
    inner = math.fsum(a * b for a, b in zip(vector, target.vector))

    return ViewFidelity(
        book_id=book.book_id,
        view=view,
        loadings=loadings,
        unreachable=unreachable,
        dominant=dominant,
        dominant_share=abs(loadings[dominant]) / total if total > 0.0 else 0.0,
        cosine=inner / denominator if denominator > 0.0 else 0.0,
        loads_on_view=agrees,
    )
