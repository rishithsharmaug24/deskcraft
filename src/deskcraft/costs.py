"""The cost model. D7a, decisions DD74-DD83, bars C77-C87.

**The build order says this package implements four cost terms, and graded data here reaches
one of them.** §3.2 names `half_spread`, `impact`, `financing` and `roll`. Two of those four
were declared unmodelled on two of the four legs of `US_CASH_BOOK` at **D2**, by a field nobody
was then writing as a statement about costs:

    ReExpression(original_kind=InstrumentKind.FUTURE,
                 unmodelled=("financing", "delivery option", "roll"))

and the same two have no graded input in this repository in any case. §3.3 names NY Fed FR 2004B
primary-dealer volumes for the impact term and says of the financing term's inputs *"Fed H.15 and
SOFR, both already graded"* -- which is false: H.15 is graded here for *yields*, and neither an
overnight rate nor SOFR has a row in `sources.py` or a column in the committed panel. Two
independent reasons, written three packages apart, agree on which terms cannot be computed. That
is carried item **X11**, opened by this package and owned by D7b.

So an absent term is `None` and never `0.0` (DD79), and `AnnualisedCost.total` refuses and names
what is missing. A zero is a number and every sum downstream adds it -- D4's reasoning for
`UNPRICEABLE` not being zero, applied to a term instead of a leg.

**A cost cannot be recorded here as a measurement, because the type cannot hold one** (DD74).
`CostBasis` has three members and there is no fourth. The build order says the rule twice -- §3.5
*"calibrated assumptions from public sources, never measurements, and no package may describe them
otherwise"*, and §6 listing *"a cost number reported as a measurement"* among the things that would
make the plan wrong -- and a rule stated twice in prose is one this repository mechanises. It is
`Direction`'s move at D2: the bug is not caught, it is made unconstructible.

**The half-spread is carried in price, and that decides whether the bias X4 describes exists at
all** (DD75). Carried in price, `cost / DV01 = half_spread_price / duration` and a wrong duration
moves the answer. Carried in yield, `cost = half_spread_yield * DV01` and the duration **cancels
exactly** -- the model would be internally consistent, would report a cost per unit of risk that no
convention choice could move, and would be wrong. The question is not a preference: a dealer quotes
a Treasury in 32nds of a point, which is price. Every entry in the nominal table is a quarter, a
half or one of a 32nd, so the numbers are a quoting convention rather than fitted decimals, and C77
holds that property rather than the values.

**A profile is a function of (market, maturity bucket), never of a series** (DD76). `SVENY10` and
`DGS10` are the same note at the same point on the curve, quoted two ways. D4's tables are keyed by
series because the *compounding convention* genuinely differs by series; a *cost* does not, because
a dealer quotes the note and not the curve fit. Two rows would be two places for one truth.

**Cost is compositional and even in the coefficient's sign** (DD77). §3.1 prices a breakeven as
*"1 x nominal + 1 x TIPS"* -- a sum over components with different per-component spreads -- and
§3.2's single `half_spread * n_components` is that sum only when every component costs the same.
`US_BREAKEVEN_5Y` is exactly where they do not, and §3.2's form is low by 50.0% on it. DV01 is odd
in the coefficient and cost is even, which is why a spread can be risk-neutral and cost twice an
outright. The build-order formula is annotated rather than rewritten, as D4 annotated its own row.

**The risk denominator is gross DV01, never net** (DD81). `LegSensitivity.net_dv01` is a residual
on any leg declaring a neutrality: 370.67 against a gross of 49,629.33 on `us_breakeven_5y`, a
factor of **133.89**, and exactly zero on a spread whose declared neutrality holds -- which would
price a well-hedged structure as infinitely expensive. You pay the spread on every component you
trade, so the risk that spread buys is the components' risk. A leg whose `RateSense` is `NONE` has
no such denominator and is refused by name rather than returned as an infinity, because `eurusd` is
in the reference book and an infinity propagates into every total that adds it.

**What this package does not do.** It does not run the selection: greedy addition, the cost hurdle,
leave-one-out and the counterfactual are §1's stopping rule and belong to D7b, which scores H9. It
does not supply the denominator that rule actually uses -- expected shortfall at 97.5%, component
ES under Euler, which is D9. Cost per gross DV01 is a rates-only stand-in and is named as one. And
it resizes nothing: `reference.py` is untouched for the third package running.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from enum import IntEnum, StrEnum

from deskcraft.book import Instrument, Leg
from deskcraft.sensitivity import (
    BASIS_POINT,
    RATE_SENSE_OF,
    TENOR_OF,
    RateSense,
    modified_duration,
    par_bond_duration_convexity,
)

__all__ = [
    "BIASES",
    "BUCKET_INCREMENT",
    "COST_HURDLE",
    "COST_MULTIPLIERS",
    "COST_OF",
    "FRBSF_ABSOLUTE_BOUND_BP",
    "FX_HALF_SPREAD_BP",
    "HURDLE_HOLDING_YEARS",
    "SEASONING_PENALTY",
    "THIRTY_SECOND_BP",
    "TIPS_ILLIQUIDITY",
    "UNGRADED_TERMS",
    "UNPRICED_SERIES",
    "AnnualisedCost",
    "Bias",
    "BiasSense",
    "CostBasis",
    "CostProfile",
    "CostTerm",
    "DurationConvention",
    "Financing",
    "Ladder",
    "LadderCell",
    "LegCountEffect",
    "Maintenance",
    "MarketDepth",
    "Market",
    "MaturityBucket",
    "NoRateRisk",
    "TermNotAvailable",
    "Untradeable",
    "annualised_cost",
    "bucket_of",
    "compounded_bias",
    "cost_ladder",
    "cost_of",
    "cost_per_dv01",
    "gross_dv01",
    "instrument_half_spread",
]

#: One thirty-second of a point, in basis points of par. A point is one per cent of par, so a
#: 32nd is 0.03125% and this is 3.125. Named because every nominal half-spread below is a dyadic
#: fraction of it, and C77 holds that property rather than the resulting decimals.
THIRTY_SECOND_BP = 100.0 / 32.0

#: The Federal Reserve Bank of San Francisco's `wp2017-10` finds seasoned TIPS bid-ask running
#: 30-100% above on-the-run. Carried as the range the paper states, not as a midpoint: §3.4's rule
#: is that the model is never reported at a point estimate, and inventing one here would break that
#: in the first table. `TIPS_ILLIQUIDITY` below takes the top of it, which is a bias and is recorded
#: as one in `BIASES`.
SEASONING_PENALTY = (1.30, 2.00)

#: The same paper's absolute statement: the magnitude is *under a basis point*. C83 converts every
#: TIPS profile to yield and holds it under this, which is a check against the source rather than
#: against another number chosen here.
FRBSF_ABSOLUTE_BOUND_BP = 1.0

#: A TIPS half-spread against the nominal at the same bucket. A `STATED_ASSUMPTION`: no source read
#: for this package quantifies the TIPS-versus-nominal ratio, and the FRBSF range above is a
#: seasoned-versus-on-the-run ratio *within* TIPS, which is a different comparison. Taking the top
#: of it here is the conservative direction and is in `BIASES`.
TIPS_ILLIQUIDITY = 2.0

#: EUR/USD spot, in basis points of notional. Quoted in pips rather than in 32nds, which is why its
#: basis is `STATED_ASSUMPTION` and why C77's dyadic law does not reach it: one pip on a rate near
#: 1.10 is about 0.9 bp of notional, so this is roughly a quarter of a pip.
FX_HALF_SPREAD_BP = 0.25

#: DD168's renminbi and peso, four times the major figure: chosen to err wide, which is this
#: table's conservative direction. Nothing read for this repository quantifies either spread,
#: and no registered verdict prices a currency leg, so the figure moves no result.
FX_EMERGING_HALF_SPREAD_BP = 1.0

#: §3.5, mandatory and not optional. The whole selection runs at each, and D7b reports the leg count
#: beside the result. A flip between 1x and 2x means the honest headline is that the result is a
#: statement about costs rather than about structure.
#:
#: **A rung scales the total cost (DD112), never one term of it.** The distinction is invisible
#: while the spread is the only graded term and decides a leg count once it is not, so it is stated
#: here and enforced at `cost_per_dv01`'s return. X18 carries the re-measurement to D8.
COST_MULTIPLIERS = (0.5, 1.0, 2.0, 4.0)

#: §1.3's cost hurdle, fixed here before D7b exists (`AMENDMENT_A2` §2, DD85). §1.3 says it is
#: *"fixed in advance (§3)"* and §3 fixed nothing, while §1.4 makes the hurdle identical to the leg
#: count and §5 registers H9 against that count -- scored by D7b, the package that would otherwise
#: choose it. A threshold picked by the package it scores is not a prediction.
#:
#: **It is 1.0 because it is not a degree of freedom.** An addition enters when gained view exposure
#: per unit of risk, over cost per unit of risk, clears `h`; selecting under `(h, cost)` is the same
#: function as selecting under `(1.0, h * cost)`, and `COST_MULTIPLIERS` already runs the whole
#: selection at four scalings of cost. Any `h != 1` is a rung of a ladder the rule already reports,
#: under a second name that would be free to move late. C91 holds the value and the identity.
COST_HURDLE = 1.0

#: The holding period the hurdle is evaluated at (DD87). Stated because §3.2's own note is that a
#: cost model without one is not a cost model, and `annualised_cost` has no default.
#:
#: Not a second free parameter, for `COST_HURDLE`'s reason and measured rather than argued: the
#: spread term is `2 * half_spread * notional / holding_years`, so `m * cost(1.0)` equals
#: `cost(1.0 / m)` exactly at every rung, and the ladder already spans 2y / 1y / 0.5y / 0.25y.
#: **The identity is a property of a one-term cost model.** Financing is constant in the holding
#: period once annualised, so grading it (X11) makes the multiplier and the holding period two axes
#: again -- an obligation X11 carries and C91 states.
HURDLE_HOLDING_YEARS = 1.0


class Untradeable(ValueError):
    """A series that is published but is not a thing a desk trades (DD76)."""


class NoRateRisk(ValueError):
    """A leg with no rate sense, so no DV01 to divide a cost by (DD81)."""


class TermNotAvailable(ValueError):
    """A cost term whose input this repository has not graded, or the leg refuses (DD79)."""


class Market(StrEnum):
    """The market a component actually trades in, which is what a cost is a property of."""

    US_NOMINAL_TREASURY = "US_NOMINAL_TREASURY"
    US_TIPS = "US_TIPS"
    FX_MAJOR = "FX_MAJOR"
    #: DD168: the renminbi and the peso. Onshore CNY is capital-controlled and MXN gaps in
    #: stress, so neither is costed as if it were the euro.
    FX_EMERGING = "FX_EMERGING"


#: The markets with no maturity, where a bucket is meaningless.
_SPOT_FX = frozenset({Market.FX_MAJOR, Market.FX_EMERGING})


class MaturityBucket(StrEnum):
    """The NY Fed FR 2004B buckets, which §3.3 already names as the impact term's own cut.

    Reused for the spread term so that one maturity partition serves both, rather than this
    package inventing a second one that would have to be kept in step with the first.
    """

    Y0_2 = "0-2"
    Y2_3 = "2-3"
    Y3_6 = "3-6"
    Y6_7 = "6-7"
    Y7_11 = "7-11"
    Y11_PLUS = "11+"


class CostBasis(StrEnum):
    """What kind of statement a cost number is (DD74).

    **There is no member meaning "measured", and that is the point.** §3.5: the cost numbers are
    calibrated assumptions from public sources, never measurements, and no package may describe
    them otherwise. A rule in prose is a rule held by whoever remembers it; a missing enum member
    is held by the constructor.
    """

    #: The increment the instrument is quoted in, which bounds the spread from above.
    QUOTING_CONVENTION = "QUOTING_CONVENTION"
    #: A number or a ratio stated in a cited public paper.
    PUBLISHED_RESEARCH = "PUBLISHED_RESEARCH"
    #: Chosen here, with a reason, and nothing upstream says it.
    STATED_ASSUMPTION = "STATED_ASSUMPTION"


class CostTerm(StrEnum):
    """§3.2's four terms, named so an absent one can be reported by name rather than as a gap."""

    HALF_SPREAD = "half_spread"
    IMPACT = "impact"
    FINANCING = "financing"
    ROLL = "roll"


class BiasSense(IntEnum):
    """Which way a bias moves a reported cost. The member value is the sign (DD83).

    Named for D4's `RateSense` rather than for `Direction`. The first draft called it
    `BiasDirection` and C10 refused it on the run that introduced it -- a near-name of
    `Direction` growing beside the real one is how "one binding site" stops being true
    without anything being renamed. D6 met the same bar with `ViewDirection` and answered
    it the same way: the symbol is renamed, never exempted.
    """

    OVERSTATES_COST = 1
    UNDERSTATES_COST = -1


class LegCountEffect(StrEnum):
    """What a bias does to the stopping rule's answer, which is the thing anyone will read."""

    FEWER_LEGS = "FEWER_LEGS"
    MORE_LEGS = "MORE_LEGS"


class DurationConvention(StrEnum):
    """The second axis of §3.5's ladder, added by carried item X5 (DD82).

    A ladder detects a flip between rungs, and its rungs are a factor of two apart. The convention
    effect at ten years is 1.132891x -- 0.1800 of a rung -- so no widening or narrowing of the cost
    multiplier can separate the convention's contribution from the multiplier's. It needs its own
    axis.
    """

    #: D4's decision, per series: continuous compounding where the licensor says so, the par-bond
    #: proxy where the quote is genuinely par.
    AS_QUOTED = "AS_QUOTED"
    #: MEIP's par-bond proxy everywhere, which is the world X4 describes.
    PAR_PROXY = "PAR_PROXY"


#: Which term §3.2 names has no input in this repository, and why. Module-level rather than a
#: `None` field repeated on seventeen profiles: the reason is a property of this repository's
#: source register, not of any one series.
UNGRADED_TERMS: dict[CostTerm, str] = {
    CostTerm.IMPACT: (
        "§3.3 names NY Fed FR 2004B primary-dealer statistics as the average-daily-volume input. "
        "`sources.py` has no row for it and the committed panel has no column, so there is no "
        "graded ADV here. State a `MarketDepth` to compute this term; there is no default, "
        "because a default would be this repository inventing the number §3.3 said would come "
        "from the NY Fed. Carried item X11, owned by D7b."
    ),
    CostTerm.FINANCING: (
        "§3.3 says of this term's inputs *'Fed H.15 and SOFR, both already graded'*. H.15 is "
        "graded here for YIELDS -- DGS3MO through DGS10 and the three DFII rows -- and neither "
        "an overnight rate nor SOFR has a row in `sources.py` or a column in the panel. Nothing "
        "here can compute a financing drag. Carried item X11, owned by D7b."
    ),
}

#: A published series that is not a thing a desk trades, with the reason (DD76). Every one of these
#: is either computed from other series or is an index, and giving it a cost would be inventing an
#: instrument. C87 holds this and `COST_OF` as an exact partition of `sources.SOURCES`, so a series
#: added to the register turns red here until it is placed in one or the other.
UNPRICED_SERIES: dict[str, str] = {
    "T10YIE": (
        "A breakeven computed by FRED as DGS10 - DFII10. You trade the two components, and §3.1's "
        "compositional rule is what prices the pair -- which is the whole point of the rule."
    ),
    "AAA10Y": "A spread computed over a bond index. The tradeable objects are the bonds beneath it.",
    "BAA10Y": "A spread computed over a bond index. The tradeable objects are the bonds beneath it.",
    "GZ_SPREAD": (
        "The Gilchrist-Zakrajsek spread: monthly, over a constructed bond universe, and not a "
        "quoted instrument. D8's frequency policy is carried item X2 and reaches this row first."
    ),
    "VIXCLS": (
        "An index. VIX futures and options are tradeable and are different instruments with their "
        "own term structure; `InstrumentKind.EQUITY_VOL` carries no series here for that reason."
    ),
    "DE_ZERO_10Y": (
        "A foreign curve whose only leg is declined (DD126): no package in the budget of twenty-one "
        "reaches it. A US quoting convention is not a German one, and this table holds no German "
        "market."
    ),
}


def bucket_of(tenor_years: float) -> MaturityBucket:
    """The FR 2004B bucket a maturity falls in. Upper bounds inclusive, as the Fed states them."""
    if not math.isfinite(tenor_years) or tenor_years <= 0.0:
        raise ValueError(f"a maturity must be positive and finite, got {tenor_years!r}")
    if tenor_years <= 2.0:
        return MaturityBucket.Y0_2
    if tenor_years <= 3.0:
        return MaturityBucket.Y2_3
    if tenor_years <= 6.0:
        return MaturityBucket.Y3_6
    if tenor_years <= 7.0:
        return MaturityBucket.Y6_7
    if tenor_years <= 11.0:
        return MaturityBucket.Y7_11
    return MaturityBucket.Y11_PLUS


#: The quoting increment a bucket trades in, as a fraction of one 32nd of a point. The front end
#: quotes in finer increments than the long end, which is the shape of every dealer's runs, and in
#: *yield* terms it inverts -- a quarter of a 32nd on a two-year note is 0.195 bp of yield against
#: 0.078 bp at ten years, because the same price increment is a larger yield move on a shorter
#: duration. That inversion is the structural reason front-end relative value dies net of costs, and
#: it is a consequence of the table rather than an input to it.
BUCKET_INCREMENT: dict[MaturityBucket, float] = {
    MaturityBucket.Y0_2: 0.25,
    MaturityBucket.Y2_3: 0.25,
    MaturityBucket.Y3_6: 0.5,
    MaturityBucket.Y6_7: 0.5,
    MaturityBucket.Y7_11: 0.5,
    MaturityBucket.Y11_PLUS: 1.0,
}


@dataclass(frozen=True, slots=True)
class CostProfile:
    """One component's cost of being traded: a half-spread, its basis, and its evidence.

    `half_spread_bp` is **one side**, in basis points of **par** -- price, never yield (DD75). A
    round trip is twice it. The unit is load-bearing: in yield the duration would cancel out of
    every cost-per-risk ratio and the convention bias X4 describes would vanish from the arithmetic
    while remaining in the world.
    """

    series: str
    market: Market
    #: `None` if and only if the market has no maturity, which is the FX row and only that row.
    bucket: MaturityBucket | None
    half_spread_bp: float
    basis: CostBasis
    evidence: str

    def __post_init__(self) -> None:
        if (self.bucket is None) != (self.market in _SPOT_FX):
            raise ValueError(
                f"{self.series}: a maturity bucket is absent if and only if the market has no "
                f"maturity; got market {self.market} and bucket {self.bucket}"
            )
        if isinstance(self.half_spread_bp, bool) or not isinstance(self.half_spread_bp, float):
            raise TypeError(f"{self.series}: half_spread_bp must be a float")
        if not math.isfinite(self.half_spread_bp) or self.half_spread_bp <= 0.0:
            raise ValueError(f"{self.series}: half_spread_bp must be positive and finite")
        if not isinstance(self.basis, CostBasis):
            raise TypeError(f"{self.series}: basis must be a CostBasis; there is no fourth member")
        if not self.evidence.strip():
            raise ValueError(f"{self.series}: a cost number carries its evidence or it is a guess")

    @property
    def round_trip_bp(self) -> float:
        """Entry and exit, which is what §3.2's leading `2 x` means."""
        return 2.0 * self.half_spread_bp

    def yield_equivalent_bp(self, duration: float) -> float:
        """This half-spread expressed in basis points of yield, at a stated duration.

        Derived, never stored. Storing it would be the unit DD75 refuses, one field along.
        """
        if duration <= 0.0:
            raise ValueError(f"{self.series}: a duration must be positive, got {duration}")
        return self.half_spread_bp / duration


_TREASURY_QUOTE = (
    "US Treasury notes and bonds are quoted in 32nds of a point and fractions of a 32nd. The "
    "increment bounds the spread from above, which is what makes this a convention rather than a "
    "calibration: every value is a quarter, a half or one of 3.125 bp of par."
)
_TIPS_QUOTE = (
    "The nominal increment at the same bucket, times TIPS_ILLIQUIDITY. FRBSF wp2017-10 gives a "
    "seasoned-versus-on-the-run range of 30-100% within TIPS and an absolute bound of under a "
    "basis point; the TIPS-versus-nominal ratio is stated here and by nobody upstream."
)
_FX_QUOTE = (
    "EUR/USD spot is quoted in pips, not in 32nds. One pip near a rate of 1.10 is about 0.9 bp of "
    "notional, so this is roughly a quarter of a pip. Stated here; no source read for this package "
    "quantifies an institutional spot spread."
)

_FX_EMERGING_QUOTE = (
    "Four times the major pairs' stated half-spread, chosen to err wide. Onshore renminbi is "
    "capital-controlled and the peso gaps in stress; no source read for this repository "
    "quantifies an institutional spot spread in either."
)

_MARKET_OF: dict[str, Market] = {
    **{f"SVENY{tenor:02d}": Market.US_NOMINAL_TREASURY for tenor in (1, 2, 3, 5, 7, 10, 20, 30)},
    **{
        series: Market.US_NOMINAL_TREASURY
        for series in ("DGS3MO", "DGS6MO", "DGS1", "DGS2", "DGS10")
    },
    **{series: Market.US_TIPS for series in ("DFII5", "DFII10", "DFII30")},
    "DEXUSEU": Market.FX_MAJOR,
    # DD168. The four G10 majors take the euro's stated spread, which was stated for the
    # tightest pair there is and is therefore a floor for these.
    **{series: Market.FX_MAJOR for series in ("DEXJPUS", "DEXUSUK", "DEXCAUS", "DEXSZUS")},
    **{series: Market.FX_EMERGING for series in ("DEXCHUS", "DEXMXUS")},
}


def _profile(series: str) -> CostProfile:
    """Build a series' profile from its market and bucket, never from a per-series table (DD76).

    `SVENY10` and `DGS10` are the same note at the same point on the curve, so they reach this
    function with the same two arguments and cannot disagree. C77 asserts that they do not.
    """
    market = _MARKET_OF[series]
    if market is Market.FX_MAJOR:
        return CostProfile(
            series, market, None, FX_HALF_SPREAD_BP, CostBasis.STATED_ASSUMPTION, _FX_QUOTE
        )
    if market is Market.FX_EMERGING:
        return CostProfile(
            series,
            market,
            None,
            FX_EMERGING_HALF_SPREAD_BP,
            CostBasis.STATED_ASSUMPTION,
            _FX_EMERGING_QUOTE,
        )
    bucket = bucket_of(TENOR_OF[series])
    nominal = BUCKET_INCREMENT[bucket] * THIRTY_SECOND_BP / 2.0
    if market is Market.US_TIPS:
        return CostProfile(
            series,
            market,
            bucket,
            nominal * TIPS_ILLIQUIDITY,
            CostBasis.PUBLISHED_RESEARCH,
            _TIPS_QUOTE,
        )
    return CostProfile(
        series, market, bucket, nominal, CostBasis.QUOTING_CONVENTION, _TREASURY_QUOTE
    )


#: Seventeen profiles at D7a and six more under DD168, against the build-order row's *"~20
#: instrument cost profiles"*, with six
#: published series refused above. The difference is refusals, not omissions, and C87 holds the two
#: as a partition of the source register.
COST_OF: dict[str, CostProfile] = {series: _profile(series) for series in _MARKET_OF}


def cost_of(series: str) -> CostProfile:
    """This series' cost profile, or a refusal naming why it is not a tradeable instrument."""
    try:
        return COST_OF[series]
    except KeyError:
        pass
    if series in UNPRICED_SERIES:
        raise Untradeable(f"{series!r} carries no cost profile: {UNPRICED_SERIES[series]}")
    raise Untradeable(
        f"{series!r} is in neither `COST_OF` nor `UNPRICED_SERIES`. A series this repository "
        "grades is either something a desk trades or something computed from what it trades, and "
        "which one is a decision rather than a default."
    )


def instrument_half_spread(instrument: Instrument) -> float:
    """One-way spread cost of the whole structure, in basis points of notional (DD77).

    `sum(|coefficient| * half_spread)` over the components. The absolute value is load-bearing:
    you pay the spread whichever way you trade, so cost is **even** in the coefficient's sign while
    DV01 is odd -- which is exactly why a spread can be risk-neutral and cost twice an outright.

    §3.2's `half_spread * n_components` is this sum only when every component costs the same.
    `US_BREAKEVEN_5Y` is the case where they do not, and §3.2's form is low by 50.0% on it.
    """
    if not isinstance(instrument, Instrument):
        raise TypeError(f"instrument must be an Instrument, got {type(instrument).__name__}")
    if not instrument.components:
        raise Untradeable(
            f"{instrument.symbol!r} is a {instrument.kind} and declares no series at all, so there "
            "is nothing to price a spread on. `UNSERIESED_KINDS` names the two kinds this reaches, "
            "and `reference.DEFERRED_LEGS` says why the option leg is carried and never priced."
        )
    return math.fsum(
        abs(component.coefficient) * cost_of(component.series).half_spread_bp
        for component in instrument.components
    )


def _duration(series: str, ytm_pct: float, convention: DurationConvention) -> float:
    """One component's modified duration under a stated convention (DD82).

    `AS_QUOTED` is D4's decision per series. `PAR_PROXY` is MEIP's par-bond form everywhere, which
    is the world carried item X4 describes -- and where it is applied to a continuously compounded
    zero it understates the duration by up to 11.730%, overstating every cost per unit of risk that
    divides by it by up to 13.289%.
    """
    if convention is DurationConvention.AS_QUOTED:
        return modified_duration(series, ytm_pct)
    tenor = TENOR_OF[series]
    if tenor != int(tenor):
        raise ValueError(
            f"{series!r} is quoted at {tenor} years and the par-bond form takes whole years, so "
            "this convention arm cannot reach it. That is MEIP's signature, not a widening (DD52)."
        )
    return par_bond_duration_convexity(ytm_pct, int(tenor))[0]


def gross_dv01(
    leg: Leg,
    yields: Mapping[str, float],
    convention: DurationConvention = DurationConvention.AS_QUOTED,
) -> float:
    """The leg's DV01 summed over components **without** offsetting them (DD81).

    Not `LegSensitivity.net_dv01`, which is a residual on any leg declaring a neutrality: 370.67
    against this function's 49,629.33 on `us_breakeven_5y`, a factor of 133.89, and exactly zero on
    a spread whose declared neutrality holds. Dividing a cost by a residual prices a well-hedged
    structure as infinitely expensive; dividing it by this asks what risk the spread bought.
    """
    if not isinstance(leg, Leg):
        raise TypeError(f"leg must be a Leg, got {type(leg).__name__}")
    sense = RATE_SENSE_OF[leg.instrument.kind]
    if sense is not RateSense.PRICE and sense is not RateSense.RATE:
        raise NoRateRisk(
            f"{leg.leg_id!r} has rate sense {sense} and therefore no DV01 to divide a cost by. "
            "`eurusd` is in the reference book and this is refused rather than returned as an "
            "infinity, because an infinity propagates into every total that adds it. The stopping "
            "rule's own denominator is expected shortfall at 97.5%, which is D9's."
        )
    parts: list[float] = []
    for component in leg.instrument.components:
        if component.series not in yields:
            raise KeyError(
                f"{leg.leg_id!r} needs a yield for {component.series!r} and the mapping carries "
                f"{tuple(sorted(yields))}"
            )
        duration = _duration(component.series, float(yields[component.series]), convention)
        parts.append(
            abs(component.coefficient) * duration * leg.notional.amount * BASIS_POINT
        )
    total = math.fsum(parts)
    if total <= 0.0:
        raise NoRateRisk(f"{leg.leg_id!r} has a gross DV01 of {total}, which nothing can divide by")
    return total


def cost_per_dv01(
    leg: Leg,
    yields: Mapping[str, float],
    convention: DurationConvention = DurationConvention.AS_QUOTED,
    multiplier: float = 1.0,
) -> float:
    """Round-trip spread cost per unit of gross DV01, in basis points of yield.

    The notional cancels out of this ratio exactly -- cost is linear in it and so is DV01 -- so
    this is a property of the instrument, the convention and the yields, and not of how much of it
    anyone holds. That is what makes it the right thing for a stopping rule to compare across
    candidate structures of different sizes.

    **Spread only.** The other three of §3.2's terms are absent for the reasons `UNGRADED_TERMS`
    and `annualised_cost` give, and a ratio silently built from one term of four would be the
    failure this module exists to refuse. `annualised_cost` is where the absences are reported.

    **The multiplier scales the total, not the spread (DD112).** While the spread is the only
    graded term those are the same number, so the scope was free to be read either way and was
    read both ways at once: this function applied it to the spread term and `generator.select`
    applied it to the whole cost. Under a second term the two disagree -- by a factor of 3.38 at
    4x -- and they select different books, which moves H9's leg count. §3.5's ladder asks whether
    a reported count is *a statement about costs*, and that question is about the cost entire, so
    the total is what a rung scales. See `RIDER_the_cost_multiplier_is_implemented_twice.md`.
    """
    if not math.isfinite(multiplier) or multiplier <= 0.0:
        raise ValueError(f"a cost multiplier must be positive and finite, got {multiplier!r}")
    spread = 2.0 * instrument_half_spread(leg.instrument) * BASIS_POINT
    # DD112. The multiplier is the **outermost factor of the return value**, and that placement is
    # the decision rather than a style. Until 2026-09-16 it multiplied the spread term in place,
    # which is the same number while the spread is the only graded term -- measured bit-identical
    # at all 3,696 cells -- and a different number the moment X11's second term lands. A term
    # added inside this ratio is scaled by construction; a term added outside sits on this line,
    # where a reader and a diff both see it. C113 holds the equality, C114 holds the placement.
    return multiplier * (
        spread * leg.notional.amount / gross_dv01(leg, yields, convention)
    )


@dataclass(frozen=True, slots=True)
class MarketDepth:
    """What the impact term needs and this repository has not graded (DD79, X11).

    Stated by the caller, with no default and no table: §3.3 says the average daily volume comes
    from NY Fed FR 2004B, `sources.py` has no row for it, and a default here would be this
    repository inventing the number it said would come from the Fed.
    """

    average_daily_volume: float
    order_size: float
    daily_volatility_bp: float
    #: The square-root law's proportionality constant. Required rather than defaulted to 1.0,
    #: because a normalisation chosen silently is a calibration nobody agreed to.
    coefficient: float

    def __post_init__(self) -> None:
        for name in ("average_daily_volume", "order_size", "daily_volatility_bp", "coefficient"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"MarketDepth.{name} must be a real number")
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"MarketDepth.{name} must be positive and finite, got {value!r}")

    @property
    def impact_bp(self) -> float:
        """The square-root law §3.2 names: `k * sigma * sqrt(order / ADV)`, in bp of notional."""
        return self.coefficient * self.daily_volatility_bp * math.sqrt(
            self.order_size / self.average_daily_volume
        )


@dataclass(frozen=True, slots=True)
class Financing:
    """What the financing term needs and this repository has not graded (DD111, X11).

    **Added by D7b to close the half of X11 that was never a data problem.** The item's own §0
    row reads *"`annualised_cost` has **no parameter** a financing input could be passed to, so
    that term is a code gap first"* -- literally true until this class existed: the term was
    refused unconditionally, with no argument any caller could ever have supplied. It is now
    absent because nothing here has graded an overnight rate, and no longer because the function
    cannot take one.

    Stated by the caller with no default, for `MarketDepth`'s reason. **And the series §3.3 names
    cannot be the one supplied**: curvecast's D218 measured that SOFR opens in 2018 and the DEV
    window ends 2014-12-31, so SOFR is a decline and not a fetch. `DFF` reaches 1954 and H.15 is
    public domain, so a route exists -- and whoever takes it writes down that substitution rather
    than grading a different series under §3.3's sentence. That decision is carried to D8 with the
    rest of the item, because FR 2004B is weekly and the frequency policy is X2's.

    `repo_rate_pct` is the rate the position is financed at and `spread_bp` the haircut over it,
    both per year. A zero spread is a statement the caller made and not a silence, which is the
    distinction DD79 turns on.
    """

    repo_rate_pct: float
    spread_bp: float

    def __post_init__(self) -> None:
        for name in ("repo_rate_pct", "spread_bp"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"Financing.{name} must be a real number")
            if not math.isfinite(value):
                raise ValueError(f"Financing.{name} must be finite, got {value!r}")
        if self.spread_bp < 0.0:
            raise ValueError(f"a financing spread is not negative, got {self.spread_bp!r}")

    @property
    def annual_rate(self) -> float:
        """The all-in financing rate as a fraction per year, which is what the drag multiplies."""
        return self.repo_rate_pct / 100.0 + self.spread_bp * BASIS_POINT


@dataclass(frozen=True, slots=True)
class Maintenance:
    """How the position is kept, which is what decides the roll term rather than the instrument.

    A roll costs a round trip in the same instrument, so `roll_cost` is derived from the spread
    profile and needs no second calibration. `rolls_per_year = 0.0` is a real and meaningful
    statement -- the position is held to its horizon -- and is not the silent zero DD79 refuses,
    because the caller had to write it.
    """

    rolls_per_year: float

    def __post_init__(self) -> None:
        if isinstance(self.rolls_per_year, bool) or not isinstance(self.rolls_per_year, (int, float)):
            raise TypeError("Maintenance.rolls_per_year must be a real number")
        if not math.isfinite(self.rolls_per_year) or self.rolls_per_year < 0.0:
            raise ValueError(f"rolls per year must be finite and non-negative, got {self.rolls_per_year!r}")


@dataclass(frozen=True, slots=True)
class AnnualisedCost:
    """§3.2's four terms, annualised consistently, with the absent ones named (DD78, DD79).

    §3.2 as written is not annualised in two of its four terms. Against the correct form, its
    financing term is out by a factor of `holding_years` and its impact term by `holding_years / 2`
    -- so the financing term is right at exactly one year and the impact term at exactly two, which
    is the likeliest reason the error survived being read. The build-order formula is annotated
    rather than rewritten.

    `total` **refuses** when any term is absent rather than summing what is present. A partial sum
    presented as the cost is the omission this repository exists to refuse, and there is
    deliberately no property that returns one.
    """

    leg_id: str
    holding_years: float
    half_spread: float | None
    impact: float | None
    financing: float | None
    roll: float | None
    #: `(term, reason)` for every term that is not a number, in `CostTerm` order.
    absent: tuple[tuple[str, str], ...]

    @property
    def present(self) -> tuple[str, ...]:
        """The terms that are numbers, in `CostTerm` order. Never a sum of them."""
        return tuple(term.value for term in CostTerm if getattr(self, term.value) is not None)

    @property
    def total(self) -> float:
        if self.absent:
            lines = "; ".join(f"{term}: {reason}" for term, reason in self.absent)
            raise TermNotAvailable(
                f"{self.leg_id!r} has {len(self.absent)} of §3.2's four cost terms absent, so "
                f"there is no total. Absent -- {lines}"
            )
        return math.fsum(
            value for value in (self.half_spread, self.impact, self.financing, self.roll)
            if value is not None
        )


def annualised_cost(
    leg: Leg,
    holding_years: float,
    depth: MarketDepth | None = None,
    maintenance: Maintenance | None = None,
    financing_input: Financing | None = None,
) -> AnnualisedCost:
    """The four terms for one leg, in the leg's notional currency, per year.

    `holding_years` has **no default**: §3.2's own note is that *"a cost model with no
    holding-period assumption is not a cost model"*, and the shorter the hold the more the spread
    term dominates without limit.

    A term is absent for one of two reasons, and both are read rather than restated here:

    - **this repository has not graded its input** -- `UNGRADED_TERMS`, which is carried item X11;
    - **the leg's own re-expression declared it unmodelled** -- `leg.re_expressed.unmodelled`,
      written at D2 by DD12, which says that any later package reporting a carry number on such a
      leg has to read that field or it is reporting a number the data does not support. This is
      that later package. `us_2y` and `us_10y` carry `("financing", "delivery option", "roll")`,
      two of which are cost terms.
    """
    if isinstance(holding_years, bool) or not isinstance(holding_years, (int, float)):
        raise TypeError("holding_years must be a real number")
    if not math.isfinite(holding_years) or holding_years <= 0.0:
        raise ValueError(f"holding_years must be positive and finite, got {holding_years!r}")
    if depth is not None and not isinstance(depth, MarketDepth):
        raise TypeError(
            f"depth must be a MarketDepth, got {type(depth).__name__}. The two optional "
            "arguments carry different terms and are not interchangeable: a Maintenance passed "
            "here would leave the impact term silently absent and the roll term silently so too."
        )
    if maintenance is not None and not isinstance(maintenance, Maintenance):
        raise TypeError(f"maintenance must be a Maintenance, got {type(maintenance).__name__}")
    if financing_input is not None and not isinstance(financing_input, Financing):
        raise TypeError(
            f"financing_input must be a Financing, got {type(financing_input).__name__}"
        )

    unmodelled = set(leg.re_expressed.unmodelled) if leg.re_expressed is not None else set()
    amount = leg.notional.amount
    absent: list[tuple[str, str]] = []

    def refuse(term: CostTerm, reason: str) -> None:
        absent.append((term.value, reason))
        return None

    def declined_at_d2(term: CostTerm) -> str:
        return (
            f"{leg.leg_id!r} is re-expressed from {leg.re_expressed.original_kind} and declares "
            f"{term.value!r} unmodelled (D2, DD12). Reporting it here would be the carry number "
            "that field was written to prevent."
        )

    one_way = instrument_half_spread(leg.instrument) * BASIS_POINT * amount

    if CostTerm.HALF_SPREAD.value in unmodelled:
        half_spread = refuse(CostTerm.HALF_SPREAD, declined_at_d2(CostTerm.HALF_SPREAD))
    else:
        half_spread = 2.0 * one_way / holding_years

    if CostTerm.IMPACT.value in unmodelled:
        impact = refuse(CostTerm.IMPACT, declined_at_d2(CostTerm.IMPACT))
    elif depth is None:
        impact = refuse(CostTerm.IMPACT, UNGRADED_TERMS[CostTerm.IMPACT])
    else:
        impact = 2.0 * depth.impact_bp * BASIS_POINT * amount / holding_years

    if CostTerm.FINANCING.value in unmodelled:
        financing = refuse(CostTerm.FINANCING, declined_at_d2(CostTerm.FINANCING))
    elif financing_input is None:
        financing = refuse(CostTerm.FINANCING, UNGRADED_TERMS[CostTerm.FINANCING])
    else:
        # Already per year, so it does not divide by the holding period -- which is the half of
        # `AMENDMENT_A2` §2.3's identity that X11 says breaks when this term is graded: the cost
        # multiplier and the holding period stop being one axis the moment a term is constant in
        # the hold. Nothing in this repository can supply the input, so the identity is untouched
        # in the committed tree and C110 states the dependency rather than discovering it later.
        financing = financing_input.annual_rate * amount

    if CostTerm.ROLL.value in unmodelled:
        roll = refuse(CostTerm.ROLL, declined_at_d2(CostTerm.ROLL))
    elif maintenance is None:
        roll = refuse(
            CostTerm.ROLL,
            "a roll is a property of how the position is kept, not of the instrument. State a "
            "`Maintenance`; `rolls_per_year=0.0` is the held-to-horizon case and is a statement "
            "rather than a silence.",
        )
    else:
        roll = 2.0 * one_way * maintenance.rolls_per_year

    return AnnualisedCost(
        leg_id=leg.leg_id,
        holding_years=float(holding_years),
        half_spread=half_spread,
        impact=impact,
        financing=financing,
        roll=roll,
        absent=tuple(sorted(absent)),
    )


@dataclass(frozen=True, slots=True)
class LadderCell:
    """One cell of §3.5's ladder, on both of its axes (DD82)."""

    multiplier: float
    convention: DurationConvention
    cost_per_dv01: float


@dataclass(frozen=True, slots=True)
class Ladder:
    """§3.5's four cost multipliers crossed with X5's two duration conventions.

    Eight cells, reported together and never one at a time. §3.5 exists because a point estimate of
    a cost is a claim nobody can support, and a caller taking the 1x `AS_QUOTED` cell and reporting
    it alone has defeated the apparatus.

    Until 2026-09-16 this docstring added *"which no bar can stop"*. That was false for callers,
    which is what it said, and true only for a reader quoting a number out of a report, which is
    not. **C102** holds the disposition of every module that reads the ladder, as an equality, and
    a module that picks one rung or hands back one cell turns the suite red (DD109).
    """

    leg_id: str
    cells: tuple[LadderCell, ...]
    #: Which of §3.2's four terms these numbers include. Never assume all four.
    terms: tuple[str, ...]

    def at(self, multiplier: float, convention: DurationConvention) -> float:
        for cell in self.cells:
            if cell.multiplier == multiplier and cell.convention is convention:
                return cell.cost_per_dv01
        raise KeyError(f"no cell at {multiplier}x under {convention}")

    @property
    def convention_effect(self) -> float:
        """`PAR_PROXY / AS_QUOTED` at 1x, which is the same ratio at every multiplier.

        The number X5 asked to be separated out. It is 1.132891 on `us_10y` -- 0.1800 of a ladder
        rung, where the rungs are a factor of two apart -- which is why the convention had to be a
        second axis and could not be found by widening the first.
        """
        return self.at(1.0, DurationConvention.PAR_PROXY) / self.at(1.0, DurationConvention.AS_QUOTED)


def cost_ladder(leg: Leg, yields: Mapping[str, float]) -> Ladder:
    """The eight cells, for one leg. §3.5 on one axis, carried item X5 on the other."""
    cells = tuple(
        LadderCell(multiplier, convention, cost_per_dv01(leg, yields, convention, multiplier))
        for convention in DurationConvention
        for multiplier in COST_MULTIPLIERS
    )
    return Ladder(leg.leg_id, cells, (CostTerm.HALF_SPREAD.value,))


@dataclass(frozen=True, slots=True)
class Bias:
    """A known, directional error in a cost number, on the object rather than in prose (DD83).

    X4's stated closure condition, and §3.4's existing shape. The direction is what turns an
    unknown into a bound: a cost that is known to be overstated gives a leg count that is a
    **lower** bound on the leg count the unbiased number would give.

    `magnitude` is `None` where the source does not quantify it, which is the Board's own 2025
    paper on indicative bid-ask. It is not `0.0`, for DD79's reason.
    """

    bias_id: str
    subject: str
    direction: BiasSense
    #: Fractional, so 0.13289 is thirteen and a quarter per cent. `None` = the source states a
    #: direction and no magnitude.
    magnitude: float | None
    effect: LegCountEffect
    source: str
    #: The carried item that owns this bias, where one does.
    carried_item: str | None = None
    #: The ladder arm this bias is live under, or `None` for one that is live under both.
    conditional_on: DurationConvention | None = None
    #: When the magnitude was measured, for one that depends on a market level.
    measured_on: date | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.direction, BiasSense):
            raise TypeError(f"{self.bias_id}: direction must be a BiasSense")
        if self.magnitude is not None and (
            not math.isfinite(self.magnitude) or self.magnitude <= 0.0
        ):
            raise ValueError(
                f"{self.bias_id}: a magnitude is a positive fraction or None. Zero is not the "
                "same statement as unquantified, and writing it as zero is how an unquantified "
                "bias stops being counted."
            )
        if (self.magnitude is None) != (self.measured_on is None):
            raise ValueError(
                f"{self.bias_id}: a magnitude is measured on a date if and only if it exists"
            )
        if not self.source.strip():
            raise ValueError(f"{self.bias_id}: a bias names the source that establishes it")

    @property
    def signed_magnitude(self) -> float | None:
        """The magnitude with `direction`'s sign, which is the only form that composes."""
        return None if self.magnitude is None else int(self.direction) * self.magnitude


#: Every known directional error in the numbers this module produces. Three of them, and **all
#: three point the same way** -- which is one more than carried item X5 states.
#:
#: X5's two are §3.4's bid-ask overstatement and X4's convention bias. The third was left by D4's
#: DD52 as a magnitude with no direction: *"MEIP's par form is annual-pay and US Treasuries pay
#: semi-annually. Measured at +0.12% of duration on DFII5."* D4's §0.7 table gives semi-annual
#: minus annual-pay, so the branch this repository actually runs **understates** the duration, and
#: an understated denominator overstates cost per unit of risk. Same direction as the other two.
#:
#: So D7a's answer to X5 is not the reassuring one: the compounding concern is worse than the
#: register states, by a third term -- though that term is two orders of magnitude smaller than the
#: second, which is the whole reason magnitudes live on objects and not in a count.
BIASES: dict[str, Bias] = {
    "indicative_bid_ask": Bias(
        bias_id="indicative_bid_ask",
        subject="Every half-spread in COST_OF that is calibrated from an indicative quote",
        direction=BiasSense.OVERSTATES_COST,
        magnitude=None,
        effect=LegCountEffect.FEWER_LEGS,
        source=(
            "Federal Reserve Board, *Trading Costs vs. Indicative Liquidity in the Off-the-Run "
            "Treasury Market* (2025): indicative bid-ask *'systematically overstate trading costs "
            "of more seasoned Treasuries'*, with the bias larger for larger orders. The paper "
            "does not quantify the magnitude, so neither does this row."
        ),
        carried_item="X5",
    ),
    "par_proxy_duration": Bias(
        bias_id="par_proxy_duration",
        subject="cost_per_dv01 under DurationConvention.PAR_PROXY, on a continuously compounded leg",
        direction=BiasSense.OVERSTATES_COST,
        magnitude=0.13289,
        effect=LegCountEffect.FEWER_LEGS,
        source=(
            "D4 §0.4: MEIP's par-bond proxy returns 8.826975 for SVENY10 on 2014-12-24 where the "
            "instrument's duration is 10 exactly, understating it by 11.730%. Understating a "
            "denominator by x overstates the ratio by x/(1-x), so the figure that belongs on a "
            "reported cost per unit of risk is 13.289% and not X4's own 11.730%."
        ),
        carried_item="X4",
        conditional_on=DurationConvention.PAR_PROXY,
        measured_on=date(2014, 12, 24),
    ),
    "annual_pay_duration": Bias(
        bias_id="annual_pay_duration",
        subject="cost_per_dv01 on DFII5, the one leg that reaches the par-bond branch under either arm",
        direction=BiasSense.OVERSTATES_COST,
        magnitude=0.001232,
        effect=LegCountEffect.FEWER_LEGS,
        source=(
            "D4 DD52 and its §0.7 table: MEIP's par form is annual-pay and a Treasury pays "
            "semi-annually. On 2014-12-24 the annual-pay duration is 4.925866 against 4.931932 "
            "semi-annual, so the branch this repository runs understates DFII5's duration by "
            "0.1231% and overstates a cost divided by it by 0.1232%. D4 recorded the magnitude "
            "and left the direction; this is the direction."
        ),
        carried_item="X5",
        measured_on=date(2014, 12, 24),
    ),
    "seasoned_tips_top_of_range": Bias(
        bias_id="seasoned_tips_top_of_range",
        subject="Every US_TIPS profile, through TIPS_ILLIQUIDITY",
        direction=BiasSense.OVERSTATES_COST,
        magnitude=None,
        effect=LegCountEffect.FEWER_LEGS,
        source=(
            "FRBSF wp2017-10 states a range of 30-100% and this table takes the top of it, which "
            "is the conservative end. The range is a seasoned-versus-on-the-run ratio within "
            "TIPS and is being used as a TIPS-versus-nominal ratio, which the paper does not "
            "license; the substitution is recorded here rather than buried in the constant."
        ),
    ),
    "absent_cost_terms": Bias(
        bias_id="absent_cost_terms",
        subject="Every cost this module reports, because three of §3.2's four terms are absent",
        direction=BiasSense.UNDERSTATES_COST,
        magnitude=None,
        effect=LegCountEffect.MORE_LEGS,
        source=(
            "`AMENDMENT_A2` §3, DD84. The four rows above are calibration biases and every one of "
            "them runs OVERSTATES_COST / FEWER_LEGS, which read together say the leg count is a "
            "lower bound. The model's largest effect is not a calibration bias and runs the other "
            "way: an absent cost term is a cost not charged, and a cost not charged lets a "
            "marginal leg clear the hurdle. Measured on US_CASH_BOOK with a MarketDepth and a "
            "Maintenance both stated -- the most a caller can supply -- `AnnualisedCost.total` "
            "refuses on all four legs, because `annualised_cost` has no parameter that could carry "
            "a financing input at all, and `us_2y` and `us_10y` additionally decline `financing` "
            "and `roll` at D2 under DD12. Unquantified in the same sense the Board's own bias is: "
            "two of the three missing terms have no graded input (X11) and the third is a "
            "re-expression's own refusal, so there is no number to put here. With this row the "
            "register holds two opposing unquantified biases, and the sign of the net effect on "
            "the leg count is unknown rather than bounded."
        ),
        carried_item="X11",
    ),
}


def compounded_bias(
    convention: DurationConvention = DurationConvention.AS_QUOTED,
    biases: Sequence[Bias] | None = None,
) -> tuple[float, int]:
    """`(product of the quantified biases, count of the unquantified ones)` under one ladder arm.

    **Two values, always, and that is the point.** X5's concern is that conservative biases
    compound; a single compounded number would answer it with the arms that happen to have a
    magnitude and silently drop the ones that do not -- which restates the problem as a
    reassurance. The count is returned so a caller cannot report the product alone without having
    seen it.
    """
    rows = list(BIASES.values()) if biases is None else list(biases)
    live = [b for b in rows if b.conditional_on is None or b.conditional_on is convention]
    product = 1.0
    unquantified = 0
    for bias in live:
        signed = bias.signed_magnitude
        if signed is None:
            unquantified += 1
        else:
            product *= 1.0 + signed
    return product, unquantified


# ---------------------------------------------------------------------------------------------
# A futures contract's row: DD176's WTI half-spread, owed before D22 builds (DD205, DD212)
# ---------------------------------------------------------------------------------------------
#
# Appended rather than placed beside `COST_OF`, so that no line X20's register body cites in this
# file moves (C118), and `__all__` is extended here for the same reason.


@dataclass(frozen=True, slots=True)
class ContractCost:
    """A futures contract's cost of being traded, per unit of its underlying (DD212).

    Not a `CostProfile`: a profile is basis points of par in a market with a maturity bucket, and a
    futures half-spread is a price increment per unit. Not in `COST_OF` either, which partitions the
    committed source register (C87); the one contract here is read through a results-only route.
    """

    instrument: str
    unit: str
    #: One side, in US dollars per unit. A round trip is twice it.
    half_spread_usd: float
    basis: CostBasis
    evidence: str

    def __post_init__(self) -> None:
        if isinstance(self.half_spread_usd, bool) or not isinstance(self.half_spread_usd, float):
            raise TypeError(f"{self.instrument}: half_spread_usd must be a float")
        if not math.isfinite(self.half_spread_usd) or self.half_spread_usd <= 0.0:
            raise ValueError(f"{self.instrument}: half_spread_usd must be positive and finite")
        if not isinstance(self.basis, CostBasis):
            raise TypeError(f"{self.instrument}: basis must be a CostBasis; there is no fourth member")
        if not self.evidence.strip():
            raise ValueError(f"{self.instrument}: a cost number carries its evidence or it is a guess")

    def roll_cost(self, quantity: float) -> float:
        """DD212 item 2: a roll closes the held contract and opens the next, crossing the spread
        twice, whichever way the position faces."""
        return 2.0 * self.half_spread_usd * abs(quantity)


#: DD176: one full tick. CME's contract specification sets the minimum fluctuation at $0.01 a
#: barrel, so a quoted spread cannot be narrower than one tick and this half-spread overstates the
#: cost whenever the spread is exactly one tick wide, which is this table's conservative direction.
WTI_TICK_USD_PER_BARREL = 0.01

CONTRACT_COST_OF: dict[str, ContractCost] = {
    "WTI_C2": ContractCost(
        "WTI_C2",
        "barrel",
        WTI_TICK_USD_PER_BARREL,
        CostBasis.QUOTING_CONVENTION,
        "NYMEX light sweet crude oil futures (CL): minimum price fluctuation $0.01 per barrel, "
        "1,000 barrels a contract, CME Group's contract specification. One tick is taken as the "
        "half-spread (DD176), which is wide if the market quotes a one-tick spread.",
    ),
}

__all__ += ["CONTRACT_COST_OF", "WTI_TICK_USD_PER_BARREL", "ContractCost"]
