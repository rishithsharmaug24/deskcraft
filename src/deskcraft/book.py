"""The book and its legs. D2, decisions DD8-DD20, bars C10-C22.

This is the module curvecast could not contain. Its boundary bans a field whose name carries
`notional`, `direction`, `position`, `size`, `weight`, `side` or `order`, because its output
is text and a directive is one field name away from a forecast; `EXEMPT_FIELDS` is `{}` and
four packages renamed their own fields rather than add the first entry. Portfolio risk is a
function *of positions*, so `Direction` and `Notional` are this repo's subject matter, and
they live here and in no other module -- which C10 asserts by scanning `src/` rather than by
convention.

Five properties are worth reading before using any of this.

**The sign of a position lives in `Direction` and is unrepresentable anywhere else** (DD8).
`Notional.amount` is strictly positive and finite; `Direction` is an `IntEnum` whose *value*
is the sign, so `Leg.signed_amount` is one multiplication with no branch in it. The bug this
forecloses is a leg carrying a negative amount *and* `Direction.SHORT` -- a long position that
reads as a short one in every table downstream. That book cannot be constructed here.

**Immutability is asserted by hashability, not by the `frozen=True` keyword** (DD9).
`frozen=True` rebinds `__setattr__` and stops there: a `list` smuggled into a frozen dataclass
is still mutable. What it does buy is that the instance stops being hashable at any depth, so
`hash(book)` is a deeper check than any annotation scan. Every container field here is a
`tuple` and C11 hashes the fixtures.

**Money never crosses currencies implicitly** (DD10). `gross_notional` raises on a
multi-currency book; `gross_by_currency` always answers. There is no exchange rate in this
repo, and inventing one here would be the first fitted number in a package that has none.

**An instrument is a signed combination of series, so relative value is representable at all**
(DD16). Four of the six legs of the reference structure are differences rather than outright
positions, and every construction the D6 view language needs -- slope, curvature, real versus
nominal, credit versus rates -- is a spread. So a ten-year steepener is
`(+1 SVENY10, -1 SVENY02)` and its `structure` is **derived** from the component count rather
than declared, because a declared structure is a second place the truth lives.

**A spread declares what it is neutral to, and a cross-currency one declares whether it is
hedged** (DD17, DD18). Neutrality is what makes a spread a relative-value leg rather than an
outright position wearing two names, and it carries a checkable law: coefficients sum to zero
unless the neutrality is `NONE`. Hedging has no default, because an unhedged cross-market
spread is two bets and a hedged one is one, and every effective-number-of-bets reading below
depends on which.

Nothing in this module computes risk. DV01 is D4, covariance D8, component ES D9. What is here
is bookkeeping strict enough that the arithmetic above it cannot be handed a book whose sign,
currency, structure or leg identity is already wrong.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from enum import IntEnum, StrEnum

__all__ = [
    "ASSET_CLASS_OF",
    "AssetClass",
    "Book",
    "Component",
    "Currency",
    "Direction",
    "Instrument",
    "InstrumentKind",
    "Leg",
    "Neutrality",
    "Notional",
    "ReExpression",
    "Structure",
    "TENORED_KINDS",
    "TENORLESS_KINDS",
    "UNSERIESED_KINDS",
]

#: Coefficients are compared to zero at this tolerance. A spread's coefficients are written
#: by hand as small integers, so anything looser would pass a genuinely unbalanced structure
#: and anything tighter would fail on a legitimate DV01 ratio like 0.1 written as a decimal.
COEFFICIENT_TOLERANCE = 1e-12


class Direction(IntEnum):
    """The only place the sign of a position lives (DD8).

    The member *value* is the sign, so `int(direction) * amount` needs no lookup table and no
    branch, and there is exactly one representation of a short position rather than two that
    can disagree.
    """

    LONG = 1
    SHORT = -1


class Currency(StrEnum):
    """Currencies the reference structures are denominated in.

    A closed set rather than a free string: a typo in a currency code is otherwise a silent
    third currency, and DD10's refusal to add across currencies would then quietly stop
    binding on the book that needed it most.
    """

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"


class AssetClass(StrEnum):
    """The coarse cut a desk reports risk by, alongside the per-leg one.

    It exists because a structure is routinely sold as spanning several asset classes while
    its risk spans one or two, and reporting component risk by class as well as by leg is
    what shows the difference. `ASSET_CLASS_OF` is total over `InstrumentKind` (DD19).
    """

    RATES = "RATES"
    INFLATION = "INFLATION"
    CREDIT = "CREDIT"
    FX = "FX"
    VOLATILITY = "VOLATILITY"


class InstrumentKind(StrEnum):
    """What an instrument *is*, which decides its tenor, its series and its asset class.

    Deliberately closed, and deliberately not a taxonomy of markets: the distinctions that
    earn a member here are the ones a bar downstream has to branch on.
    """

    ZERO_YIELD = "ZERO_YIELD"
    REAL_YIELD = "REAL_YIELD"
    BREAKEVEN = "BREAKEVEN"
    CREDIT_SPREAD = "CREDIT_SPREAD"
    SWAP_SPREAD = "SWAP_SPREAD"
    CROSS_MARKET_SPREAD = "CROSS_MARKET_SPREAD"
    CROSS_CURRENCY_BASIS = "CROSS_CURRENCY_BASIS"
    FX_SPOT = "FX_SPOT"
    EQUITY_VOL = "EQUITY_VOL"
    RATE_VOL = "RATE_VOL"
    FUTURE = "FUTURE"
    OPTION = "OPTION"


#: Total and single-valued over `InstrumentKind` (DD19). C21 asserts both, and asserts that
#: the image is exactly `AssetClass` -- a class no kind maps to is a column that will be
#: empty in every attribution and a kind with no class is an exception discovered mid-run.
ASSET_CLASS_OF: dict[InstrumentKind, AssetClass] = {
    InstrumentKind.ZERO_YIELD: AssetClass.RATES,
    InstrumentKind.REAL_YIELD: AssetClass.RATES,
    InstrumentKind.BREAKEVEN: AssetClass.INFLATION,
    InstrumentKind.CREDIT_SPREAD: AssetClass.CREDIT,
    InstrumentKind.SWAP_SPREAD: AssetClass.RATES,
    InstrumentKind.CROSS_MARKET_SPREAD: AssetClass.RATES,
    InstrumentKind.CROSS_CURRENCY_BASIS: AssetClass.FX,
    InstrumentKind.FX_SPOT: AssetClass.FX,
    InstrumentKind.EQUITY_VOL: AssetClass.VOLATILITY,
    InstrumentKind.RATE_VOL: AssetClass.VOLATILITY,
    InstrumentKind.FUTURE: AssetClass.RATES,
    InstrumentKind.OPTION: AssetClass.VOLATILITY,
}


class Structure(StrEnum):
    """Derived from the component count, never declared (DD16)."""

    OUTRIGHT = "OUTRIGHT"
    SPREAD = "SPREAD"
    BUTTERFLY = "BUTTERFLY"
    BASKET = "BASKET"


class Neutrality(StrEnum):
    """What a relative-value structure is hedged against.

    The first question a desk asks about a curve trade, and the one that changes its risk
    most: a DV01-neutral 2s10s steepener and a cash-neutral one have different level
    exposure and therefore different component risk. `NONE` means outright and directional,
    which is a legitimate answer and is why the field is an enum rather than a flag.
    """

    NONE = "NONE"
    DV01 = "DV01"
    CASH = "CASH"
    VEGA = "VEGA"
    BETA = "BETA"


#: Kinds that are a point on a term structure and therefore must carry a tenor.
TENORED_KINDS = frozenset(
    {
        InstrumentKind.ZERO_YIELD,
        InstrumentKind.REAL_YIELD,
        InstrumentKind.BREAKEVEN,
        InstrumentKind.CREDIT_SPREAD,
        InstrumentKind.SWAP_SPREAD,
        InstrumentKind.CROSS_MARKET_SPREAD,
        InstrumentKind.CROSS_CURRENCY_BASIS,
        InstrumentKind.RATE_VOL,
        InstrumentKind.FUTURE,
        InstrumentKind.OPTION,
    }
)

#: Kinds with no term structure, which must NOT carry one. A tenor on a spot rate is a number
#: nothing can use and everything downstream would be entitled to read.
TENORLESS_KINDS = frozenset({InstrumentKind.FX_SPOT, InstrumentKind.EQUITY_VOL})

#: Kinds with no observable series in this repo's universe, which must declare no components.
#: Not a claim that no such data exists anywhere -- a claim that none of it is free and
#: point-in-time gradeable, which is the approved plan's §4 and the reason the reference
#: structure's option leg is carried but never priced.
UNSERIESED_KINDS = frozenset({InstrumentKind.FUTURE, InstrumentKind.OPTION})


def _positive_finite(value: object, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{what} must be a real number, got {type(value).__name__}")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{what} must be finite, got {value!r}")
    if number <= 0.0:
        raise ValueError(f"{what} must be strictly positive, got {value!r}")
    return number


def _identifier(value: object, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{what} must be a non-empty string, got {value!r}")
    return value


@dataclass(frozen=True, slots=True)
class Component:
    """One signed series inside an instrument (DD16).

    `coefficient` is signed and is what makes a spread a spread: a ten-year steepener is
    `+1` on the ten-year zero and `-1` on the two-year, and a butterfly is `+1, -2, +1`.
    `currency` is per component rather than per instrument, because that is the only place a
    cross-currency structure can be detected -- an instrument denominated in USD may still
    have a EUR-denominated leg inside it, and DD18's hedging question turns on exactly that.
    """

    series: str
    coefficient: float
    currency: Currency

    def __post_init__(self) -> None:
        _identifier(self.series, "Component.series")
        if isinstance(self.coefficient, bool) or not isinstance(self.coefficient, (int, float)):
            raise TypeError(
                f"Component.coefficient must be a real number, got {self.coefficient!r}"
            )
        if not math.isfinite(self.coefficient):
            raise ValueError(f"Component.coefficient must be finite, got {self.coefficient!r}")
        if self.coefficient == 0.0:
            raise ValueError(
                f"Component {self.series!r} has a zero coefficient and is not in the structure"
            )
        if not isinstance(self.currency, Currency):
            raise TypeError(f"Component.currency must be a Currency, got {self.currency!r}")


@dataclass(frozen=True, slots=True)
class Notional:
    """An unsigned amount of one currency (DD8).

    Unsigned is the decision. A negative amount is refused, so the sign of a position exists
    once, in `Direction`, and the two cannot contradict each other. Zero is refused too: a
    zero-amount leg contributes nothing and survives every subsequent filter, which makes it a
    leg that exists only to be miscounted in a leg count.
    """

    amount: float
    currency: Currency

    def __post_init__(self) -> None:
        _positive_finite(self.amount, "Notional.amount")
        if not isinstance(self.currency, Currency):
            raise TypeError(f"Notional.currency must be a Currency, got {self.currency!r}")


@dataclass(frozen=True, slots=True)
class Instrument:
    """A priceable-or-not thing on which a leg is expressed.

    `components` is what makes both priceability and structure *derived* rather than declared
    (DD11, DD16). It names the signed series the instrument is computed from, so a five-year
    breakeven is `(+1 SVENY05, -1 DFII5)` and its grade is the worse of the two. A bar checks
    those names against curvecast's measured archive floors **at test time**, which means the
    partition into priceable and deferred goes stale on its own when the graded universe
    changes, instead of being a list in this repo that someone has to remember to update.

    The invariant that earns its place: **coefficients sum to zero unless neutrality is
    `NONE`** (DD17). That one line catches a spread written with two `+1`s, which is the most
    common way a relative-value leg is silently a doubled outright.
    """

    symbol: str
    kind: InstrumentKind
    currency: Currency
    tenor_years: float | None = None
    components: tuple[Component, ...] = ()
    neutrality: Neutrality = Neutrality.NONE
    fx_hedged: bool | None = None

    def __post_init__(self) -> None:
        _identifier(self.symbol, "Instrument.symbol")
        if not isinstance(self.kind, InstrumentKind):
            raise TypeError(f"Instrument.kind must be an InstrumentKind, got {self.kind!r}")
        if not isinstance(self.currency, Currency):
            raise TypeError(f"Instrument.currency must be a Currency, got {self.currency!r}")
        if not isinstance(self.neutrality, Neutrality):
            raise TypeError(f"Instrument.neutrality must be a Neutrality, got {self.neutrality!r}")

        if self.kind in TENORLESS_KINDS:
            if self.tenor_years is not None:
                raise ValueError(f"{self.kind} carries no tenor, got {self.tenor_years!r}")
        else:
            if self.tenor_years is None:
                raise ValueError(f"{self.kind} requires a tenor, got None")
            _positive_finite(self.tenor_years, "Instrument.tenor_years")

        if not isinstance(self.components, tuple):
            raise TypeError(
                f"Instrument.components must be a tuple, got {type(self.components).__name__}"
            )
        for item in self.components:
            if not isinstance(item, Component):
                raise TypeError(f"Instrument.components holds a {type(item).__name__}")
        names = [item.series for item in self.components]
        if len(set(names)) != len(names):
            raise ValueError(f"Instrument.components repeats a series: {names}")

        if self.kind in UNSERIESED_KINDS:
            if self.components:
                raise ValueError(f"{self.kind} has no observable series here, got {names}")
        elif not self.components:
            raise ValueError(f"{self.kind} must name the series it is computed from")

        # DD16/DD17: the structure is derived, and the neutrality law is checked against it.
        if self.components:
            total = math.fsum(item.coefficient for item in self.components)
            balanced = abs(total) <= COEFFICIENT_TOLERANCE
            if self.structure is Structure.OUTRIGHT:
                if self.neutrality is not Neutrality.NONE:
                    raise ValueError(
                        f"a single-component instrument cannot be {self.neutrality}-neutral"
                    )
                if self.components[0].coefficient != 1.0:
                    raise ValueError(
                        "an OUTRIGHT must be a single unit component, got "
                        f"{self.components[0].coefficient!r}"
                    )
            elif balanced and self.neutrality is Neutrality.NONE:
                raise ValueError(
                    f"{self.symbol!r} has coefficients that cancel but declares no neutrality; a "
                    "balanced difference is hedged against something and the basis has to be "
                    "named, because DV01-neutral and cash-neutral are different positions"
                )
            elif not balanced and self.neutrality is not Neutrality.NONE:
                raise ValueError(
                    f"{self.symbol!r} declares {self.neutrality} but its coefficients sum to "
                    f"{total!r}; a structure hedged against something has coefficients that "
                    "cancel, and one that does not is an outright position wearing two names"
                )

        # DD18: the hedging question has no default when it is live, and no answer when it is not.
        spans = self.component_currencies
        if len(spans) > 1:
            if not isinstance(self.fx_hedged, bool):
                raise ValueError(
                    f"{self.symbol!r} spans {list(spans)} and must state fx_hedged; an unhedged "
                    "cross-market structure is two bets and a hedged one is one, and no default "
                    "answers that"
                )
        elif self.fx_hedged is not None:
            raise ValueError(
                f"{self.symbol!r} is single-currency, so fx_hedged must be None, got "
                f"{self.fx_hedged!r}"
            )

    @property
    def structure(self) -> Structure:
        """Derived from the component count, never declared (DD16)."""
        count = len(self.components)
        if count <= 1:
            return Structure.OUTRIGHT
        if count == 2:
            return Structure.SPREAD
        if count == 3:
            return Structure.BUTTERFLY
        return Structure.BASKET

    @property
    def asset_class(self) -> AssetClass:
        return ASSET_CLASS_OF[self.kind]

    @property
    def series(self) -> tuple[str, ...]:
        return tuple(item.series for item in self.components)

    @property
    def component_currencies(self) -> tuple[Currency, ...]:
        return tuple(sorted({item.currency for item in self.components}))

    @property
    def is_cross_currency(self) -> bool:
        return len(self.component_currencies) > 1

    @property
    def is_relative_value(self) -> bool:
        """True when the instrument is a difference rather than an outright position."""
        return self.structure is not Structure.OUTRIGHT


@dataclass(frozen=True, slots=True)
class ReExpression:
    """A record that a leg is not the instrument the source structure named (DD12).

    The reference structure is stated in futures and the approved plan's §4 declines futures
    for want of a free point-in-time term structure, so the rate legs are carried as
    DV01-matched cash. That is a first-order equivalence and this field is what keeps it
    stated rather than assumed: `unmodelled` names what the substitution drops, and any later
    package reporting a carry number on such a leg has to read it or it is reporting a number
    the data does not support.
    """

    original_kind: InstrumentKind
    unmodelled: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.original_kind, InstrumentKind):
            raise TypeError("ReExpression.original_kind must be an InstrumentKind")
        if not isinstance(self.unmodelled, tuple) or not self.unmodelled:
            raise ValueError("ReExpression.unmodelled must be a non-empty tuple")
        for item in self.unmodelled:
            _identifier(item, "ReExpression.unmodelled entry")


@dataclass(frozen=True, slots=True)
class Leg:
    """One position in a hypothetical book.

    `leg_id` is how every downstream attribution addresses this row, which is why a book
    refuses duplicates (DD15): two rows called `us_2y` in an Euler decomposition cannot be
    told apart by the thing that reads them.
    """

    leg_id: str
    instrument: Instrument
    direction: Direction
    notional: Notional
    re_expressed: ReExpression | None = None

    def __post_init__(self) -> None:
        _identifier(self.leg_id, "Leg.leg_id")
        if not isinstance(self.instrument, Instrument):
            raise TypeError(f"Leg.instrument must be an Instrument, got {self.instrument!r}")
        if not isinstance(self.direction, Direction):
            raise TypeError(f"Leg.direction must be a Direction, got {self.direction!r}")
        if not isinstance(self.notional, Notional):
            raise TypeError(f"Leg.notional must be a Notional, got {self.notional!r}")
        if self.re_expressed is not None and not isinstance(self.re_expressed, ReExpression):
            raise TypeError("Leg.re_expressed must be a ReExpression or None")

    @property
    def currency(self) -> Currency:
        return self.notional.currency

    @property
    def asset_class(self) -> AssetClass:
        return self.instrument.asset_class

    @property
    def signed_amount(self) -> float:
        """The amount with its sign, which exists only here and only as this product."""
        return int(self.direction) * self.notional.amount


@dataclass(frozen=True, slots=True)
class Book:
    """A stated hypothetical structure. Never a claim that it is worth holding.

    That sentence is the boundary of this repo, and it is why `thesis` is a description of a
    macro view rather than a case for a position. The imperative phrase scan (C15) reads this
    field out of the source, which is the reason it had to be widened at D2: D1's version saw
    only module-level uppercase assignments, and a thesis sits in constructor-argument
    position, invisible to it.
    """

    book_id: str
    as_of: date
    thesis: str
    legs: tuple[Leg, ...]

    def __post_init__(self) -> None:
        _identifier(self.book_id, "Book.book_id")
        _identifier(self.thesis, "Book.thesis")
        if not isinstance(self.as_of, date):
            raise TypeError(f"Book.as_of must be a date, got {type(self.as_of).__name__}")
        if not isinstance(self.legs, tuple):
            raise TypeError(f"Book.legs must be a tuple, got {type(self.legs).__name__}")
        if not self.legs:
            raise ValueError("Book.legs is empty; every ratio below divides by zero on it")
        for leg in self.legs:
            if not isinstance(leg, Leg):
                raise TypeError(f"Book.legs holds a {type(leg).__name__}")
        ids = [leg.leg_id for leg in self.legs]
        if len(set(ids)) != len(ids):
            repeated = sorted({name for name in ids if ids.count(name) > 1})
            raise ValueError(f"Book.legs repeats a leg_id: {repeated}")

    def __len__(self) -> int:
        return len(self.legs)

    @property
    def leg_ids(self) -> tuple[str, ...]:
        return tuple(leg.leg_id for leg in self.legs)

    @property
    def currencies(self) -> tuple[Currency, ...]:
        return tuple(sorted({leg.currency for leg in self.legs}))

    @property
    def asset_classes(self) -> tuple[AssetClass, ...]:
        return tuple(sorted({leg.asset_class for leg in self.legs}))

    @property
    def series(self) -> tuple[str, ...]:
        """Every series any leg is computed from, deduplicated and ordered."""
        return tuple(sorted({name for leg in self.legs for name in leg.instrument.series}))

    @property
    def relative_value_legs(self) -> tuple[str, ...]:
        return tuple(leg.leg_id for leg in self.legs if leg.instrument.is_relative_value)

    @property
    def cross_currency_legs(self) -> tuple[str, ...]:
        return tuple(leg.leg_id for leg in self.legs if leg.instrument.is_cross_currency)

    def leg(self, leg_id: str) -> Leg:
        for candidate in self.legs:
            if candidate.leg_id == leg_id:
                return candidate
        raise KeyError(f"{leg_id!r} is not a leg of {self.book_id!r}")

    def gross_by_currency(self) -> dict[Currency, float]:
        totals: dict[Currency, float] = {}
        for leg in self.legs:
            totals[leg.currency] = totals.get(leg.currency, 0.0) + leg.notional.amount
        return totals

    def net_by_currency(self) -> dict[Currency, float]:
        totals: dict[Currency, float] = {}
        for leg in self.legs:
            totals[leg.currency] = totals.get(leg.currency, 0.0) + leg.signed_amount
        return totals

    def gross_by_asset_class(self) -> dict[AssetClass, float]:
        """Unsigned amount per asset class, within a single currency only (DD10).

        Raises on a multi-currency book for the same reason `gross_notional` does: the sum
        would be adding USD to EUR, and this is the cut most likely to be quoted as evidence
        that a structure spans several markets.
        """
        if len(self.currencies) != 1:
            raise ValueError(
                f"{self.book_id!r} spans {list(self.currencies)}; there is no exchange rate in "
                "this repo, so read gross_by_currency instead"
            )
        totals: dict[AssetClass, float] = {}
        for leg in self.legs:
            totals[leg.asset_class] = totals.get(leg.asset_class, 0.0) + leg.notional.amount
        return totals

    @property
    def gross_notional(self) -> float:
        """Total unsigned amount. Raises on a multi-currency book, by decision (DD10)."""
        return self._single_currency_total(self.gross_by_currency())

    @property
    def net_notional(self) -> float:
        """Signed total. Raises on a multi-currency book, by decision (DD10)."""
        return self._single_currency_total(self.net_by_currency())

    def _single_currency_total(self, totals: dict[Currency, float]) -> float:
        if len(totals) != 1:
            raise ValueError(
                f"{self.book_id!r} spans {sorted(totals)}; there is no exchange rate in this "
                "repo, so read gross_by_currency or net_by_currency instead"
            )
        return next(iter(totals.values()))

    def restricted_to(self, book_id: str, leg_ids: Iterable[str]) -> Book:
        """A new book over a subset of these legs, in this book's order.

        Used to derive the priceable subset of a reference structure from the structure
        itself, so the two cannot drift apart in the way two hand-written fixtures would.
        """
        wanted = set(leg_ids)
        missing = sorted(wanted - set(self.leg_ids))
        if missing:
            raise KeyError(f"{missing} are not legs of {self.book_id!r}")
        return Book(
            book_id=book_id,
            as_of=self.as_of,
            thesis=self.thesis,
            legs=tuple(leg for leg in self.legs if leg.leg_id in wanted),
        )
