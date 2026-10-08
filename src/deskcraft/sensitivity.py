"""DV01, convexity and leg P&L under a stated shift. D4, decisions DD49-DD56, bars C49-C57.

**The build order says this package wraps `meip.rates.cascade.par_bond_duration_convexity`,
and it wraps it for one of the four legs.** Three of `US_CASH_BOOK`'s legs are expressed on
`SVENY02`, `SVENY05` and `SVENY10`, and the Gurkaynak-Sack-Wright file says what those are in
its own header block, three lines above the data:

    Series,Compounding Convention,Mnemonic(s)
    Zero-coupon yield,Continuously Compounded,SVENYXX
    Par yield,Coupon-Equivalent,SVENPYXX

A zero under continuous compounding has `-(dP/dy)/P = T` **exactly** and convexity `T**2`
exactly; there is nothing to fit and no proxy to choose. MEIP's function is a par-bond
approximation written for a repository that *"holds no index constituents"* and needed
something derivable rather than a hand-set index duration. Applied to `SVENY10` on
2014-12-24 it returns 8.826975 where the instrument's duration is 10, which is **11.730%**
of the ten-year leg's DV01 given away to a proxy whose own docstring says it is one.

So the wrap is kept where the quote convention earns it -- `DFII5` is H.15's constant
maturity on an investment basis, and D3a's register already records its fallback as
*"Treasury Daily **Par** Real Yield Curve Rates"* -- and declined where it does not. The
build-order row is annotated rather than rewritten (D70).

**The convention is read from the licensor and refused by default** (DD49). `COMPOUNDING_OF`
carries no default branch: a series with no row raises. DD18 set this repository's rule for
that shape when it refused a default for `fx_hedged`, *"because a default is a silent answer"*,
and the thing a default would silently answer here is worth 11.7% at ten years. `DEXUSEU` and
`GZ_SPREAD` are deliberately absent -- an exchange rate has no duration, and a credit spread's
DV01 belongs to the bond portfolio it is a spread over rather than to the spread.

**`RATE_SENSE_OF` exists because `LONG` means two different things** (DD53). A `ZERO_YIELD`
leg held long is long a bond and loses when its yield rises; a `BREAKEVEN` leg held long is
long a spread and gains when that spread widens. Nothing in D2's types says which, and the two
are opposite signs on the same series. `UNPRICEABLE` is a fourth member and not a zero: the
option leg has enormous rate sensitivity and no free volatility surface, and a zero would be a
number that every downstream sum then adds.

**The shift is per series, not per tenor** (DD54). The build order asked for a per-tenor bp
shift. `US_BREAKEVEN_5Y` holds two curves at the same tenor, so a five-year shift cannot say
which one moved -- and the difference between those two is the whole of the residual below.
`CurveShift.parallel` builds a per-curve move over named series, so a per-tenor shift is a
convenience over the primitive rather than the primitive.

**What this module measures about the reference book, and does not act on.**
`US_BREAKEVEN_5Y` declares `Neutrality.DV01` and `book.py` admits the declaration because its
coefficients sum to zero. Its two components are quoted on different conventions, so on
2014-12-24 they carry 25,000.00 and 24,629.33 per basis point: a parallel one-basis-point rise
in both curves leaves the breakeven unchanged and moves the leg by **370.67**, 1.483% of the
nominal component. Coefficient-neutral is not DV01-neutral, which is the distinction
`book.py`'s own refusal message has drawn since D2 without being able to compute it.
`reference.py` is annotated and not edited: whether that leg should be DV01-matched is D7b's
decision, the way D5's DD40 left leg 1 to D7b when `DGS2`'s floor landed.

**First order only, and the second order is reported rather than omitted** (DD56). `leg_pnl`
is `sum(dv01 * bp)`. `second_order_pnl` is a separate function with a separate name that
refuses for a `RATE`-sense spread, because a convexity term on a spread needs it decomposed
into two separately priced bond legs with their own notionals, and that is D7b's job. On
`us_10y` at a 100 bp parallel move the dropped term is 5% of the first-order one, which C57
asserts so it cannot become invisible.

**MEIP's par form is annual-pay and US Treasuries pay semi-annually** (DD52). Measured at
+0.12% of duration on `DFII5`, the one leg that reaches this branch, and +0.51% at ten years.
It is **not corrected**: a wrap that silently improves on what it wraps is a second
implementation wearing the same name, and the next reader comparing the two numbers would find
a difference no document explains.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum

from deskcraft.book import Book, InstrumentKind, Leg

__all__ = [
    "BASIS_POINT",
    "COMPOUNDING_OF",
    "RATE_SENSE_OF",
    "TENOR_OF",
    "Compounding",
    "CurveShift",
    "LegSensitivity",
    "RateSense",
    "SeriesSensitivity",
    "Unpriceable",
    "UnknownConvention",
    "book_dv01",
    "book_pnl",
    "convexity",
    "leg_pnl",
    "leg_sensitivity",
    "modified_duration",
    "par_bond_duration_convexity",
    "second_order_pnl",
]

#: One basis point as a decimal. Named because `1e-4` appears in three formulas and a stray
#: factor of ten in a DV01 is the arithmetic error that reads as plausible.
BASIS_POINT = 1e-4


class UnknownConvention(ValueError):
    """A series whose compounding convention or tenor this module has not measured (DD49)."""


class Unpriceable(ValueError):
    """A leg with real rate sensitivity that free graded data here cannot compute (DD53)."""


class Compounding(StrEnum):
    """How a quoted yield compounds, which decides which duration formula is the right one."""

    #: `P = exp(-yT)`. Modified duration is `T` and convexity `T**2`, both exactly.
    CONTINUOUS = "CONTINUOUS"
    #: A par bond's cash flows, discounted at its own yield. MEIP's form, annual-pay (DD52).
    COUPON_EQUIVALENT = "COUPON_EQUIVALENT"


#: Measured, never assumed (DD49). The `SVENY` rows are the Gurkaynak-Sack-Wright file's own
#: header block, which C49 parses out of `feds200628.csv` at test time. The H.15 rows are
#: Treasury's constant-maturity methodology, which D3a's register already records by naming
#: `Treasury Daily Par Yield Curve Rates` and `Treasury Daily Par Real Yield Curve Rates` as
#: their fallbacks -- C49 reads that wording out of `sources.py` rather than restating it.
#:
#: `DEXUSEU` and `GZ_SPREAD` are absent on purpose and asking for either raises by name.
COMPOUNDING_OF: dict[str, Compounding] = {
    **{f"SVENY{tenor:02d}": Compounding.CONTINUOUS for tenor in (1, 2, 3, 5, 7, 10, 20, 30)},
    **{
        series: Compounding.COUPON_EQUIVALENT
        for series in ("DGS3MO", "DGS6MO", "DGS1", "DGS2", "DGS10", "DFII5", "DFII10", "DFII30")
    },
}

#: The maturity each series is quoted at, in years. Held here rather than parsed out of the
#: name: `DGS3MO` is 0.25 and `SVENY03` is 3, and a rule that reads digits out of a mnemonic
#: gets that pair wrong in the direction that produces a plausible number.
#:
#: A component's tenor comes from **its own series**, never from the instrument that holds it.
#: A steepener is one instrument with one declared tenor and two components at different
#: points on the curve, and reading the instrument's tenor for both would price it as a
#: doubled outright -- the same failure DD17's coefficient rule catches one layer up.
TENOR_OF: dict[str, float] = {
    **{f"SVENY{tenor:02d}": float(tenor) for tenor in (1, 2, 3, 5, 7, 10, 20, 30)},
    "DGS3MO": 0.25,
    "DGS6MO": 0.5,
    "DGS1": 1.0,
    "DGS2": 2.0,
    "DGS10": 10.0,
    "DFII5": 5.0,
    "DFII10": 10.0,
    "DFII30": 30.0,
}


class RateSense(StrEnum):
    """What being `LONG` an instrument means for its sign against a rate move (DD53)."""

    #: Long the price. A rate rise is a loss. A bond, a real bond, a bond future.
    PRICE = "PRICE"
    #: Long the quoted rate. A rise is a gain. Every spread quoted as a rate.
    RATE = "RATE"
    #: No first-order rate sensitivity at all, structurally. Not a missing number.
    NONE = "NONE"
    #: Real rate sensitivity that free graded data cannot compute here. Raises, never zero.
    UNPRICEABLE = "UNPRICEABLE"


#: Total and single-valued over `InstrumentKind`, in `ASSET_CLASS_OF`'s shape, and its image is
#: the whole of `RateSense` (C52). A kind with no sense is an exception discovered mid-run, and
#: a sense no kind carries is a branch no bar ever exercises.
RATE_SENSE_OF: dict[InstrumentKind, RateSense] = {
    InstrumentKind.ZERO_YIELD: RateSense.PRICE,
    InstrumentKind.REAL_YIELD: RateSense.PRICE,
    InstrumentKind.FUTURE: RateSense.PRICE,
    InstrumentKind.BREAKEVEN: RateSense.RATE,
    InstrumentKind.CREDIT_SPREAD: RateSense.RATE,
    InstrumentKind.SWAP_SPREAD: RateSense.RATE,
    InstrumentKind.CROSS_MARKET_SPREAD: RateSense.RATE,
    InstrumentKind.CROSS_CURRENCY_BASIS: RateSense.RATE,
    InstrumentKind.FX_SPOT: RateSense.NONE,
    InstrumentKind.EQUITY_VOL: RateSense.NONE,
    InstrumentKind.OPTION: RateSense.UNPRICEABLE,
    InstrumentKind.RATE_VOL: RateSense.UNPRICEABLE,
}

#: `PRICE` carries the minus sign, `RATE` the plus. Read once, here, so no formula below
#: writes a bare `-1` that a later reader has to reverse-engineer.
_SIGN_OF = {RateSense.PRICE: -1.0, RateSense.RATE: 1.0}


def par_bond_duration_convexity(ytm_pct: float, maturity_years: int) -> tuple[float, float]:
    """Modified duration and convexity of a par bond at this yield, from its cash flows.

    **A restatement of `meip.rates.cascade.par_bond_duration_convexity`, line for line**, and
    C50 executes MEIP's own bytes out of `cascade.py` to prove the two agree at exact equality
    rather than within a tolerance. It is restated rather than imported because `meip` is not
    importable on this repository's interpreter and `cascade.py` reaches numpy, pydantic and
    two stores at module level -- the same condition `window.py` met with curvecast's DEV
    bounds, answered the same way.

    `sum` rather than `math.fsum`, and the flows in MEIP's order, deliberately: the bar is an
    exact equality and a reordered summation would break it for a reason that is not an error.

    **Annual-pay** (DD52), while a Treasury pays semi-annually. Measured at +0.12% of duration
    on `DFII5` and +0.51% at ten years. Not corrected here; see this module's docstring.

    **Integral years only**, which is MEIP's signature. `DGS3MO` and `DGS6MO` -- the front end
    D5 graded -- are therefore out of this branch's reach, and D7b meets that when it goes
    looking for a short leg.
    """
    if maturity_years <= 0:
        raise ValueError(f"maturity_years must be positive, got {maturity_years}")
    y = ytm_pct / 100.0
    if y <= -1.0:
        raise ValueError(f"yield {ytm_pct}% implies a non-positive discount factor")
    coupon = y * 100.0
    flows = [
        (t, coupon + (100.0 if t == maturity_years else 0.0))
        for t in range(1, maturity_years + 1)
    ]

    price = sum(cf / (1.0 + y) ** t for t, cf in flows)
    macaulay = sum(t * cf / (1.0 + y) ** t for t, cf in flows) / price
    convexity_ = sum(t * (t + 1) * cf / (1.0 + y) ** (t + 2) for t, cf in flows) / price
    return macaulay / (1.0 + y), convexity_


def _convention(series: str) -> tuple[Compounding, float]:
    try:
        return COMPOUNDING_OF[series], TENOR_OF[series]
    except KeyError:
        raise UnknownConvention(
            f"{series!r} has no measured compounding convention in this module. It is refused "
            "rather than defaulted: the two branches disagree by 11.7% at ten years, so a "
            "default would be a silent answer to the question this table exists to ask. An "
            "exchange rate has no duration, and a credit spread's DV01 belongs to the bond "
            "portfolio it is a spread over."
        ) from None


def modified_duration(series: str, ytm_pct: float, tenor_years: float | None = None) -> float:
    """Modified duration of one unit of `series`, per its own measured convention (DD50).

    `tenor_years` defaults to the series' own quoted maturity and may be given only to
    restate it; a value that disagrees with `TENOR_OF` is refused rather than honoured,
    because the series is the thing whose convention was measured.
    """
    compounding, quoted = _convention(series)
    tenor = quoted if tenor_years is None else float(tenor_years)
    if tenor != quoted:
        raise UnknownConvention(
            f"{series!r} is quoted at {quoted} years and was asked for at {tenor}. The "
            "convention was measured for the series, not for an arbitrary point on it."
        )
    if compounding is Compounding.CONTINUOUS:
        return tenor
    return par_bond_duration_convexity(ytm_pct, _integral_years(series, tenor))[0]


def convexity(series: str, ytm_pct: float, tenor_years: float | None = None) -> float:
    """Convexity of one unit of `series`. `T**2` exactly under continuous compounding."""
    compounding, quoted = _convention(series)
    tenor = quoted if tenor_years is None else float(tenor_years)
    if tenor != quoted:
        raise UnknownConvention(
            f"{series!r} is quoted at {quoted} years and was asked for at {tenor}."
        )
    if compounding is Compounding.CONTINUOUS:
        return tenor * tenor
    return par_bond_duration_convexity(ytm_pct, _integral_years(series, tenor))[1]


def _integral_years(series: str, tenor: float) -> int:
    if tenor != int(tenor):
        raise UnknownConvention(
            f"{series!r} is quoted at {tenor} years and the par-bond form takes whole years. "
            "That is MEIP's signature, restated rather than widened (DD52), so the front end "
            "D5 graded is out of this branch's reach until a package needs it."
        )
    return int(tenor)


@dataclass(frozen=True, slots=True)
class SeriesSensitivity:
    """One component of one leg: its convention, its duration, and its signed DV01."""

    series: str
    compounding: Compounding
    #: The instrument's signed coefficient on this series, carried through from `Component`.
    coefficient: float
    modified_duration: float
    convexity: float
    #: Signed, per basis point, in the leg's notional currency. Sign carries the direction,
    #: the rate sense and the coefficient together; nothing downstream re-applies any of them.
    dv01: float


@dataclass(frozen=True, slots=True)
class LegSensitivity:
    """A leg's first-order rate risk, component by component.

    `net_dv01` reads two ways and they are the same number. On an outright it is the leg's
    DV01. On a structure declaring a neutrality it is the **residual** a parallel move leaves
    behind -- which is zero when the declaration holds and 370.67 per basis point on
    `us_breakeven_5y`, where it does not.
    """

    leg_id: str
    sense: RateSense
    components: tuple[SeriesSensitivity, ...]

    @property
    def net_dv01(self) -> float:
        return math.fsum(item.dv01 for item in self.components)

    @property
    def series(self) -> tuple[str, ...]:
        return tuple(item.series for item in self.components)


@dataclass(frozen=True, slots=True)
class CurveShift:
    """A stated move, in basis points, keyed by **series** (DD54).

    Not by tenor: `US_BREAKEVEN_5Y` holds a nominal and a real curve at the same five years,
    and a per-tenor shift cannot name which of them moved. A series the shift does not name is
    unshifted, which is what a partial move means; a series **no leg holds** is refused by
    `book_pnl`, because a mistyped mnemonic that silently contributes nothing is a stress test
    reporting "no effect" for a reason that has nothing to do with the book (DD55).
    """

    moves: tuple[tuple[str, float], ...]

    def __post_init__(self) -> None:
        if not isinstance(self.moves, tuple):
            raise TypeError(f"CurveShift.moves must be a tuple, got {type(self.moves).__name__}")
        if not self.moves:
            raise ValueError("a CurveShift moves nothing; state the series it moves")
        names = [series for series, _ in self.moves]
        if len(set(names)) != len(names):
            raise ValueError(f"CurveShift names a series twice: {names}")
        for series, basis_points in self.moves:
            if not isinstance(series, str) or not series.strip():
                raise ValueError(f"CurveShift series must be a non-empty string, got {series!r}")
            if isinstance(basis_points, bool) or not isinstance(basis_points, (int, float)):
                raise TypeError(f"{series}: a shift must be a real number of basis points")
            if not math.isfinite(basis_points):
                raise ValueError(f"{series}: a shift must be finite, got {basis_points!r}")

    @classmethod
    def parallel(cls, series: Iterable[str], basis_points: float) -> CurveShift:
        """The same move on every named series. A per-curve or per-tenor shift is built here."""
        return cls(tuple((name, float(basis_points)) for name in series))

    @property
    def series(self) -> tuple[str, ...]:
        return tuple(name for name, _ in self.moves)

    def basis_points(self, series: str) -> float:
        """This series' move, or `0.0` where the shift does not name it."""
        for name, value in self.moves:
            if name == series:
                return value
        return 0.0


def leg_sensitivity(leg: Leg, yields: Mapping[str, float]) -> LegSensitivity:
    """One leg's DV01, decomposed over the series its instrument names.

    `yields` are in **percent**, as every series in the panel is published. A leg whose sense
    is `NONE` returns no components at all -- declared, not empty by accident -- and one whose
    sense is `UNPRICEABLE` raises.
    """
    if not isinstance(leg, Leg):
        raise TypeError(f"leg must be a Leg, got {type(leg).__name__}")
    sense = RATE_SENSE_OF[leg.instrument.kind]
    if sense is RateSense.UNPRICEABLE:
        raise Unpriceable(
            f"{leg.leg_id!r} is a {leg.instrument.kind} and carries real rate sensitivity that "
            "free graded data cannot compute here -- an option needs a volatility surface that "
            "does not exist free, and a rate-vol instrument the same. It is refused rather "
            "than returned as 0.0, because a zero is a number and every sum downstream will "
            "add it. `reference.DEFERRED_LEGS` names the leg and `US_CASH_BOOK` is the book "
            "without it."
        )
    if sense is RateSense.NONE:
        return LegSensitivity(leg.leg_id, sense, ())

    sign = _SIGN_OF[sense]
    amount = leg.notional.amount
    direction = float(int(leg.direction))
    found: list[SeriesSensitivity] = []
    for component in leg.instrument.components:
        series = component.series
        if series not in yields:
            raise KeyError(
                f"{leg.leg_id!r} needs a yield for {series!r} and the mapping carries "
                f"{tuple(sorted(yields))}"
            )
        ytm = float(yields[series])
        compounding, _ = _convention(series)
        duration = modified_duration(series, ytm)
        found.append(
            SeriesSensitivity(
                series=series,
                compounding=compounding,
                coefficient=component.coefficient,
                modified_duration=duration,
                convexity=convexity(series, ytm),
                dv01=sign * direction * amount * duration * component.coefficient * BASIS_POINT,
            )
        )
    return LegSensitivity(leg.leg_id, sense, tuple(found))


def leg_pnl(leg: Leg, shift: CurveShift, yields: Mapping[str, float]) -> float:
    """First-order P&L of one leg under `shift`, in the leg's notional currency (DD56).

    `sum(dv01 * basis_points)` and nothing else. The second-order term is `second_order_pnl`,
    which is a different function with a different name because it is not included here.
    """
    sensitivity = leg_sensitivity(leg, yields)
    return math.fsum(
        item.dv01 * shift.basis_points(item.series) for item in sensitivity.components
    )


def second_order_pnl(leg: Leg, shift: CurveShift, yields: Mapping[str, float]) -> float:
    """The convexity term `1/2 * C * dy**2 * notional`, which `leg_pnl` does **not** include.

    Refuses for a `RATE`-sense leg. A convexity term on a spread needs the spread decomposed
    into two separately priced bond legs with their own notionals, and that is D7b's work; it
    is refused here rather than computed for one sense and silently skipped for the other.
    """
    sensitivity = leg_sensitivity(leg, yields)
    if sensitivity.sense is RateSense.RATE:
        raise Unpriceable(
            f"{leg.leg_id!r} is a spread quoted as a rate, and its convexity is a property of "
            "the two bond legs it would be built from, each with its own notional. D7b "
            "generates those legs; this package reports the first order and says so."
        )
    direction = float(int(leg.direction))
    amount = leg.notional.amount
    return math.fsum(
        0.5
        * direction
        * amount
        * item.convexity
        * (shift.basis_points(item.series) * BASIS_POINT) ** 2
        for item in sensitivity.components
    )


def _priced_legs(book: Book) -> Sequence[Leg]:
    unpriceable = [
        leg.leg_id
        for leg in book.legs
        if RATE_SENSE_OF[leg.instrument.kind] is RateSense.UNPRICEABLE
    ]
    if unpriceable:
        raise Unpriceable(
            f"{book.book_id!r} holds {unpriceable}, which free graded data cannot price here. "
            "The whole book is refused rather than the leg quietly dropped: a total over five "
            "of six legs presented as the book's risk is the omission this repository exists "
            "to refuse. `reference.US_CASH_BOOK` is the four that are reachable."
        )
    return book.legs


def book_dv01(book: Book, yields: Mapping[str, float]) -> dict[str, LegSensitivity]:
    """Every leg's sensitivity, by `leg_id`. Refuses a book holding an unpriceable leg."""
    return {leg.leg_id: leg_sensitivity(leg, yields) for leg in _priced_legs(book)}


def book_pnl(
    book: Book, shift: CurveShift, yields: Mapping[str, float]
) -> dict[str, float]:
    """First-order P&L by `leg_id`, refusing a shift that names a series the book cannot hold.

    Per DD55: a series **no leg reaches** is a typo or a stale mnemonic, and honouring it as a
    zero turns a stress test into a report of "no effect" for the wrong reason. A series the
    book holds but this shift omits is simply unshifted.
    """
    legs = _priced_legs(book)
    held = {series for leg in legs for series in leg.instrument.series}
    stray = [series for series in shift.series if series not in held]
    if stray:
        raise ValueError(
            f"the shift names {stray}, which no leg of {book.book_id!r} reaches; it holds "
            f"{tuple(sorted(held))}. A shift on a series the book cannot see contributes zero, "
            "and a stress test reporting no effect for that reason is worse than one that "
            "refuses."
        )
    return {leg.leg_id: leg_pnl(leg, shift, yields) for leg in legs}
