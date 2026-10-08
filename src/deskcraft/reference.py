"""The reference structure of `PLAN_deskcraft.md` §6, expressed in D2's types.

Six legs: short 2Y Treasury futures, short 10Y Treasury futures, long 5Y inflation
breakevens, short EUR/USD, long 10Y Treasury calls, short the US-German 10Y spread. It is a
good fixture precisely because it is articulate and plausible, which is what makes its risk
structure worth decomposing rather than dismissing -- and §5.2 pre-registers the finding that
its effective number of bets will land well below six.

Four things about it are not what a leg table shows, and all four are on the objects rather
than in prose.

**Four of the six legs are relative value, not outright** (DD16). The breakeven is nominal
minus real, the cross-market leg is US minus German, and the two futures legs are a
policy-versus-term-premium decomposition that only means anything as a pair. Each carries
signed components and a named neutrality, so `structure` and `is_relative_value` are derived
from what the instrument *is* rather than from what it is called.

**It is re-expressed in cash** (DD12). The source states legs 1 and 2 as futures and the
approved plan's §4 declines any futures leg: no free point-in-time term structure exists, and
every roll-adjusted continuous series is a vendor product or a reconstruction whose splice
rule is the model. So they are carried as DV01-matched cash on the GSW zero curve, each with a
`ReExpression` naming what the substitution drops -- financing, the delivery option, and roll.
First-order equivalence, stated as one.

**Two of the six cannot be priced from free graded data** and are carried anyway. The option
leg has no observable series at all here, and the cross-market spread reaches a foreign curve
that no package builds: DD126 declined it, the budget being twenty-one packages, one in and one
out. `DEFERRED_LEGS` keeps its name and names both, each with the reason it is declined;
`US_CASH_BOOK` is the four that remain, derived from `REFERENCE_BOOK` rather than written out
a second time, so the two cannot drift apart. C14 checks that partition against curvecast's
measured archive floors **at test time**, which is what makes it go stale on its own when D5
grades the front end.

**The source's own justification is carried as a hypothesis** (DD20). It argues the structure
is diversified because *different legs profit from different aspects of the same macro
thesis*, and gives a four-scenario table saying which legs win in each. That is a claim about
signs, so `SCENARIO_SIGNS` records it cell by cell before any replay and D12 scores it. It is
also the claim the approved plan's **H4** pre-registers as false, predicting an effective
number of bets below 3.0 on six legs. Both cannot hold, and which one survives is a
measurement rather than an argument.

**On the notionals.** Only the 2Y figure comes from the plan. The rest are stated round
hypotheticals, recorded as such in `NOTIONAL_PROVENANCE`, and they stand in for the
DV01-matched set D4 will derive once there is a duration transform to derive it from. Nothing
here should be read as a sized structure.

**ANNOTATED 2026-09-15 (D4).** The duration transform now exists -- `deskcraft.sensitivity`
-- and the DV01-matched set was **not** derived. Deriving it means re-expressing these
legs, and a package that both measures a book and resizes it is a package whose
measurement cannot be checked against anything. D4 reports what the stated notionals
carry, and D7b generates legs. What D4 did find is that the matching question is live
one layer below the notionals: see leg 3 below, where two components at the same tenor
are quoted on different conventions and a declared DV01 neutrality does not hold.
"""

from __future__ import annotations

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
    ReExpression,
)

__all__ = [
    "DEFERRED_LEGS",
    "NOTIONAL_PROVENANCE",
    "REFERENCE_AS_OF",
    "REFERENCE_BOOK",
    "REFERENCE_THESIS",
    "SCENARIO_SIGNS",
    "US_CASH_BOOK",
]

REFERENCE_AS_OF = date(2026, 9, 5)

REFERENCE_THESIS = (
    "Fewer policy cuts than priced, plus a fiscal-driven repricing of the term premium."
)

#: What a futures-to-cash substitution drops (DD12). A zero-coupon cash leg carries no repo
#: rate and no cheapest-to-deliver option, and a carry number computed on one of these legs
#: without reading this field is a number the data does not support.
_FUTURES_TO_CASH = ReExpression(
    original_kind=InstrumentKind.FUTURE,
    unmodelled=("financing", "delivery option", "roll"),
)

#: Leg 1. The policy-expectations component: if the path prices fewer cuts, the two-year
#: yield rises. Outright on the GSW two-year zero rather than on the FRED two-year constant
#: maturity, because `DGS2` carries no measured archive floor yet and `SVENY02` is pinned.
#:
#: **D5, 2026-09-12, DD40 — the first half of that reason expired and the leg did not move.**
#: curvecast `e78d2f7` graded `DGS2`: archive floor 2005-06-28, P0 from it and P1 before it,
#: 4 revisions in 12,566 observation dates. The second half stands, and on its own it is the
#: stronger one: `SVENY02` is a zero yield off the pinned GSW file and `DGS2` is a par
#: constant maturity off H.15, so they are different instruments and substituting one for the
#: other moves a number rather than tidying a comment. Whether this leg is better expressed on
#: the constant maturity is a decision for D7, the leg generator, which has a reason to make
#: it; recorded here so a later reader knows the alternative arrived and was not taken.
_US_2Y = Instrument(
    symbol="US_ZERO_2Y",
    kind=InstrumentKind.ZERO_YIELD,
    currency=Currency.USD,
    tenor_years=2.0,
    components=(Component("SVENY02", 1.0, Currency.USD),),
)

#: Leg 2. The term-premium component. Outright in the same sense, and the pair with leg 1 is
#: the decomposition curvecast item 17 measured cannot be graded point-in-time before 2016 --
#: which is a limit on the thesis discovered independently of it.
_US_10Y = Instrument(
    symbol="US_ZERO_10Y",
    kind=InstrumentKind.ZERO_YIELD,
    currency=Currency.USD,
    tenor_years=10.0,
    components=(Component("SVENY10", 1.0, Currency.USD),),
)

#: Leg 3. Relative value across asset classes: nominal minus real at the same tenor. Not a
#: series here -- `T5YIE` carries no measured archive floor -- so it is the GSW five-year zero
#: minus the five-year TIPS real yield, which is what `T5YIE` is anyway, and its grade is the
#: worse of the two components (DD11). Same-tenor, so the hedge basis is duration.
#:
#: **ANNOTATED 2026-09-15 (D4, C55) -- the last clause assumes something that is false.**
#: Same-tenor implies same-duration only if both components are quoted the same way, and
#: these two are not. `SVENY05` is a continuously compounded zero, so its modified
#: duration is 5 exactly; `DFII5` is H.15's constant maturity on an investment basis, a
#: par quote, whose duration on 2014-12-24 is 4.925866. The Board publishes the
#: distinction in `feds200628.csv`'s own header block, three lines above the data.
#:
#: So `+1, -1` is coefficient-neutral and not DV01-neutral, and the `Neutrality.DV01`
#: declared below leaves a residual of **370.67 per basis point on the stated $50m** --
#: 1.483% of the nominal component -- which a parallel move in both curves does not
#: cancel. `book.py`'s own refusal message has drawn the adjacent distinction since D2:
#: *DV01-neutral and cash-neutral are different positions.*
#:
#: **The instrument is deliberately unchanged.** Whether this leg is better matched on
#: duration than on coefficients is a decision for D7b, the leg generator, which has a
#: reason to make it -- the same disposition D5's DD40 reached when `DGS2`'s floor landed
#: and leg 1 did not move. Recorded here so a later reader knows the measurement arrived
#: and the re-expression was declined rather than missed.
_US_BREAKEVEN_5Y = Instrument(
    symbol="US_BREAKEVEN_5Y",
    kind=InstrumentKind.BREAKEVEN,
    currency=Currency.USD,
    tenor_years=5.0,
    components=(
        Component("SVENY05", 1.0, Currency.USD),
        Component("DFII5", -1.0, Currency.USD),
    ),
    neutrality=Neutrality.DV01,
)

#: Leg 4. The relative-rate-differential component, and the only outright FX position. One
#: series, so it is single-currency in the sense DD18 means: a spot rate is one observable,
#: not a structure spanning two curves, and `fx_hedged` is therefore None rather than False.
_EURUSD = Instrument(
    symbol="EURUSD",
    kind=InstrumentKind.FX_SPOT,
    currency=Currency.EUR,
    components=(Component("DEXUSEU", 1.0, Currency.EUR),),
)

#: Leg 5. The tail-convexity component, and the one leg doing something different in kind:
#: §6.3 is right that a convex payoff is understated by construction in a linear framework.
#: No free implied-volatility surface exists, so this instrument declares no series at all and
#: `InstrumentKind.OPTION` is in `UNSERIESED_KINDS`. It is carried rather than dropped because
#: a structure that quietly deletes its convex leg reports a tail it does not understand.
_US_10Y_CALL = Instrument(
    symbol="US_10Y_CALL",
    kind=InstrumentKind.OPTION,
    currency=Currency.USD,
    tenor_years=10.0,
)

#: Leg 6. Relative value across markets and across currencies: US ten-year minus German
#: ten-year, the relative-supply component. `fx_hedged=True` is a **decision, not a
#: measurement** -- the source does not say, and DD18 refuses a default because an unhedged
#: cross-market spread is two bets and a hedged one is one. Hedged is the desk convention for
#: a quoted spread and it is the reading least flattering to the structure's diversification
#: claim, since an unhedged version would add a currency bet that H4 would then count.
_US_DE_10Y = Instrument(
    symbol="US_DE_SPREAD_10Y",
    kind=InstrumentKind.CROSS_MARKET_SPREAD,
    currency=Currency.USD,
    tenor_years=10.0,
    components=(
        Component("SVENY10", 1.0, Currency.USD),
        Component("DE_ZERO_10Y", -1.0, Currency.EUR),
    ),
    neutrality=Neutrality.DV01,
    fx_hedged=True,
)

REFERENCE_BOOK = Book(
    book_id="reference_six_leg",
    as_of=REFERENCE_AS_OF,
    thesis=REFERENCE_THESIS,
    legs=(
        Leg("us_2y", _US_2Y, Direction.SHORT, Notional(200e6, Currency.USD), _FUTURES_TO_CASH),
        Leg("us_10y", _US_10Y, Direction.SHORT, Notional(60e6, Currency.USD), _FUTURES_TO_CASH),
        Leg("us_breakeven_5y", _US_BREAKEVEN_5Y, Direction.LONG, Notional(50e6, Currency.USD)),
        Leg("eurusd", _EURUSD, Direction.SHORT, Notional(75e6, Currency.EUR)),
        Leg("us_10y_call", _US_10Y_CALL, Direction.LONG, Notional(50e6, Currency.USD)),
        Leg("us_de_10y", _US_DE_10Y, Direction.SHORT, Notional(40e6, Currency.USD)),
    ),
)

#: Where each figure came from. Only one of the six is from the plan; the rest are stated
#: round hypotheticals standing in for the DV01-matched set D4 will derive. Machine-readable,
#: because a provenance note in a docstring is a provenance note nothing checks.
#:
#: **ANNOTATED 2026-09-15 (D4).** D4 closed without deriving that set, so every string
#: below saying *pending the DV01 match at D4* is now pending **D7b** instead. The values
#: are left as written rather than edited: they record what was true when each figure was
#: stated, and the package that will replace them is named here instead of in five
#: separate strings that would then each have to be kept in step.
NOTIONAL_PROVENANCE = {
    "us_2y": "PLAN_deskcraft.md §2, which states a $200m two-year leg.",
    "us_10y": "Stated round hypothetical, pending the DV01 match at D4.",
    "us_breakeven_5y": "Stated round hypothetical, pending the DV01 match at D4.",
    "eurusd": "Stated round hypothetical, pending the DV01 match at D4.",
    "us_10y_call": "Stated round hypothetical; this leg is never priced here in any case.",
    "us_de_10y": "Stated round hypothetical, pending the DV01 match at D4.",
}

#: The legs of `REFERENCE_BOOK` that free graded data cannot reach today, with the reason.
#: Declared here and verified against curvecast's measured floors by C14, so the claim is
#: checkable rather than asserted -- and so it turns red on its own if the graded universe
#: moves under it.
DEFERRED_LEGS = {
    "us_10y_call": (
        "No free implied-volatility surface exists, so this leg is carried and never priced. "
        "A Black-76 leg fed from realised volatility would produce risk numbers that are "
        "artefacts of the input, and the refusal is more credible than the leg."
    ),
    "us_de_10y": (
        "Reaches a foreign zero curve, and is declined (DD126): the budget is twenty-one packages, "
        "one in and one out, and none builds a cross-market leg, so it is carried and never priced. "
        "The foreign curves' licences were measured at AMENDMENT_A5 section 3."
    ),
}

#: The source's scenario table, as a pre-registered sign matrix (DD20).
#:
#: The structure was justified on the ground that its legs profit from different aspects of
#: one thesis, and four scenarios were given with the legs that win in each. Signs only:
#: `+1` is a gain, `-1` a loss, `0` no material directional claim. The source's distinction
#: between "wins" and "partially wins" is deliberately dropped -- it is a magnitude claim with
#: no stated threshold, and recording it would be inventing a bar after the fact. What was
#: asserted is a sign, and a sign is what D12 scores against realised windows.
#:
#: Read against the approved plan's H4, this matrix is the falsifiable form of the source's
#: diversification claim: if the legs really do carry independent bets, the sign patterns
#: across scenarios should differ. Columns that move together are what an effective number of
#: bets below 3.0 looks like before the covariance is even computed.
SCENARIO_SIGNS = {
    "fed_signals_fewer_cuts": {
        "us_2y": +1,
        "us_10y": +1,
        "us_breakeven_5y": 0,
        "eurusd": +1,
        "us_10y_call": 0,
        "us_de_10y": 0,
    },
    "supply_shock": {
        "us_2y": 0,
        "us_10y": +1,
        "us_breakeven_5y": +1,
        "eurusd": 0,
        "us_10y_call": 0,
        "us_de_10y": +1,
    },
    "inflation_surprises_higher": {
        "us_2y": 0,
        "us_10y": 0,
        "us_breakeven_5y": +1,
        "eurusd": 0,
        "us_10y_call": +1,
        "us_de_10y": 0,
    },
    "everything_goes_wrong": {
        "us_2y": -1,
        "us_10y": -1,
        "us_breakeven_5y": -1,
        "eurusd": -1,
        "us_10y_call": +1,
        "us_de_10y": -1,
    },
}

#: The four legs that free graded data reaches today, derived from the six rather than written
#: out again. This is the book D4 through D16 actually measure, and its leg count is the
#: approved plan's §10 NO-BUILD floor exactly -- four independently graded instruments.
US_CASH_BOOK = REFERENCE_BOOK.restricted_to(
    "reference_us_cash",
    tuple(leg_id for leg_id in REFERENCE_BOOK.leg_ids if leg_id not in DEFERRED_LEGS),
)
