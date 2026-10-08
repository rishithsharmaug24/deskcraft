"""D18: five structures on a stated exposure, the gate that refuses leverage, and H13.

`PRECOMMIT_deskcraft_d18_structures_and_gate.md` fixes every rule here (DD193-DD198), before any
structure was priced.

**The menu** (DD193). One exposure, five structures, each on 100% of the stated exposure for one
year at a discount factor of one: the forward; the protective option bought at the forward; the
zero-cost collar; the participating forward, which sells half what it buys; and the 2:1 ratio
forward, which sells twice what it buys and stands in for KIKO without its knock-out.

**The gate is a type** (DD194). `HedgeStructure` constructs iff the structure pays in the
exposure's losing direction, declares the worst-state obligation its legs derive, and that
obligation is at most the exposure. Otherwise it raises `Unsuitable`, and there is no warning
path. Leverage is research §6's: the worst-state notional the client must transact over the
stated exposure. A bought option obliges nothing.

**Premium paid and optionality sold are two numbers** (DD195). The only quantity that nets them is
`Priced.headline_cost`, the objective a quote sheet shows and the one the unconstrained minimiser
sees. Put-call parity makes its answer arithmetic: a one-strike zero-premium structure beats the
forward by (p - 1) x one sold option, so the only structure below zero is the one selling more
than it hedges, at every volatility above zero. H13 therefore cannot fail, and the pre-commit's §3
says so before the run.

**Prices are optcraft's, restated** (DD196). The three value formulas below repeat optcraft's
operations in optcraft's order, and C179 holds them to exact equality against its source. The
engine imports no sibling repository, as with meip (C59) and curvecast (C60).
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.special import ndtr

from deskcraft import covariance, panel
from deskcraft.generator import CANDIDATE_SERIES
from deskcraft.registers import Verdict
from deskcraft.views import ExposureTerm, HedgeTarget, UnreachableFactor
from deskcraft.window import DEV_START, FitWindow

__all__ = [
    "CONSTRUCTION",
    "LOGNORMAL_LADDER",
    "MENU",
    "NORMAL_LADDER",
    "Case",
    "CaseRung",
    "Exposure",
    "H13Result",
    "HedgeStructure",
    "Model",
    "Payoff",
    "Priced",
    "Side",
    "StructureLeg",
    "Unsuitable",
    "bachelier_value",
    "black76_value",
    "case_exposures",
    "constrained_pick",
    "gk_value",
    "h13",
    "hedge_target",
    "load_stated",
    "price_menu",
    "rates_at_construction",
    "rungs_for",
    "score_case",
    "unconstrained_pick",
    "worst_obligation",
]

#: D22's lock: every input is dated on or before it.
CONSTRUCTION = date(2014, 12, 24)
#: DD193. D17's naive hedge is twelve months; rates are zero, so the discount factor is one.
TENOR_YEARS = 1.0
RATE = 0.0
#: DD193. What the participating forward and the ratio forward sell, per unit bought.
PARTICIPATION = 0.5
RATIO = 2.0
#: DD193. The collar's protective strike, in standard deviations adverse of the forward.
COLLAR_OFFSET_SD = 0.5
#: DD196. Lognormal volatility as a fraction; normal volatility in percent a year, on a yield
#: quoted in percent.
LOGNORMAL_LADDER = (0.05, 0.10, 0.20, 0.40, 0.80)
NORMAL_LADDER = (0.05, 0.10, 0.25, 0.50, 1.00)
#: How far either side of the forward, in standard deviations, a strike is searched for.
_BRACKET_SD = 20.0

MENU = (
    "forward",
    "bought option",
    "zero-cost collar",
    "participating forward",
    "2:1 ratio forward",
)


# --------------------------------------------------------------------------------------------
# optcraft's values, restated (DD196, C179)
# --------------------------------------------------------------------------------------------


_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


def _pdf(x: np.ndarray) -> np.ndarray:
    return _INV_SQRT_2PI * np.exp(-0.5 * x * x)


def _check(tau, vol) -> tuple[np.ndarray, np.ndarray]:
    tau, vol = np.asarray(tau, dtype=float), np.asarray(vol, dtype=float)
    if np.any(tau <= 0.0):
        raise ValueError("an option with no time left has no model value")
    if np.any(vol <= 0.0):
        raise ValueError("volatility must be positive")
    return tau, vol


def gk_value(call: bool, s, k, tau, vol, rd=0.0, rf=0.0) -> np.ndarray:
    """Garman-Kohlhagen, optcraft's `_gk` value line for line."""
    s, k, rd, rf = (np.asarray(x, dtype=float) for x in (s, k, rd, rf))
    tau, vol = _check(tau, vol)
    if np.any(s <= 0.0) or np.any(k <= 0.0):
        raise ValueError("a lognormal model needs a positive underlying and strike")
    root = np.sqrt(tau)
    d1 = (np.log(s / k) + (rd - rf + 0.5 * vol * vol) * tau) / (vol * root)
    d2 = d1 - vol * root
    df_d, df_f = np.exp(-rd * tau), np.exp(-rf * tau)
    if call:
        return s * df_f * ndtr(d1) - k * df_d * ndtr(d2)
    return k * df_d * ndtr(-d2) - s * df_f * ndtr(-d1)


def black76_value(call: bool, f, k, tau, vol, r=0.0) -> np.ndarray:
    """Black-76: Garman-Kohlhagen on a forward with both rates the discount rate, as optcraft."""
    return gk_value(call, f, k, tau, vol, r, r)


def bachelier_value(call: bool, f, k, tau, vol, r=0.0) -> np.ndarray:
    """Bachelier, optcraft's `_bachelier` value line for line."""
    f, k, r = (np.asarray(x, dtype=float) for x in (f, k, r))
    tau, vol = _check(tau, vol)
    root = np.sqrt(tau)
    spread = vol * root
    d = (f - k) / spread
    df = np.exp(-r * tau)
    n = _pdf(d)
    if call:
        return df * ((f - k) * ndtr(d) + spread * n)
    return df * ((k - f) * ndtr(-d) + spread * n)


# --------------------------------------------------------------------------------------------
# The exposure
# --------------------------------------------------------------------------------------------


class Model(StrEnum):
    GARMAN_KOHLHAGEN = "GARMAN_KOHLHAGEN"
    BLACK76 = "BLACK76"
    BACHELIER = "BACHELIER"


#: DD196. Currency on GK at zero differential, crude on Black-76, both in moneyness; rates on
#: Bachelier on the yield.
MODEL_OF = {"currency": Model.GARMAN_KOHLHAGEN, "crude": Model.BLACK76, "rates": Model.BACHELIER}


class Payoff(StrEnum):
    FORWARD = "FORWARD"
    CALL = "CALL"
    PUT = "PUT"


class Side(StrEnum):
    """For an option, bought or sold. For a forward, BOUGHT is long the underlying."""

    BOUGHT = "BOUGHT"
    SOLD = "SOLD"


@dataclass(frozen=True)
class Exposure:
    """One stated exposure from D17's stated fixture. `sign` +1 means the firm gains when the
    underlying rises: revenue in a currency, crude sold. -1 means it loses: crude bought, debt
    whose cost rises with the yield."""

    cohort_rank: int
    cik: str
    cls: str
    instrument: str
    sign: int
    amount_usd: float

    def __post_init__(self) -> None:
        if self.cls not in MODEL_OF:
            raise ValueError(f"no model prices a {self.cls!r} exposure")
        if self.sign not in (1, -1):
            raise ValueError(f"an exposure's sign is +1 or -1, got {self.sign!r}")
        if not (math.isfinite(self.amount_usd) and self.amount_usd > 0.0):
            raise ValueError(f"an exposure of {self.amount_usd!r} dollars states nothing")

    @property
    def model(self) -> Model:
        return MODEL_OF[self.cls]

    @property
    def protective(self) -> Payoff:
        """The option that pays when the firm loses."""
        return Payoff.PUT if self.sign > 0 else Payoff.CALL

    @property
    def opposite(self) -> Payoff:
        return Payoff.CALL if self.protective is Payoff.PUT else Payoff.PUT

    @property
    def adverse(self) -> int:
        """Which way the underlying moves when the firm loses."""
        return -self.sign


def load_stated(path: Path) -> tuple[Exposure, ...]:
    """D17's stated fixture, one exposure per row."""
    with open(path, newline="", encoding="utf-8") as handle:
        return tuple(
            Exposure(
                cohort_rank=int(row["cohort_rank"]),
                cik=row["cik"],
                cls=row["class"],
                instrument=row["instrument"],
                sign=int(row["sign"]),
                amount_usd=float(row["amount_usd"]),
            )
            for row in csv.DictReader(handle)
        )


def case_exposures(exposures: tuple[Exposure, ...], clients: int = 3) -> tuple[Exposure, ...]:
    """The first `clients` firms of the cohort ordering, each by its largest stated exposure (§0)."""
    out = []
    for rank in range(1, clients + 1):
        mine = [e for e in exposures if e.cohort_rank == rank]
        if not mine:
            raise ValueError(f"cohort rank {rank} states no exposure")
        out.append(max(mine, key=lambda e: e.amount_usd))
    return tuple(out)


def hedge_target(exposures: tuple[Exposure, ...]) -> HedgeTarget:
    """DD197: exposures sign-flipped, as a target D7b's `select` runs on unchanged.

    Reach is checked here, not in D7b: a series outside the candidate pool would return a book
    about something else under this exposure's name (X19).
    """
    terms = []
    for exposure in exposures:
        if exposure.instrument not in CANDIDATE_SERIES:
            raise UnreachableFactor(
                f"{exposure.instrument!r} is outside D7b's candidate pool {CANDIDATE_SERIES}; "
                "no generated leg can point along it"
            )
        terms.append(ExposureTerm(exposure.instrument, exposure.sign * exposure.amount_usd))
    return HedgeTarget(tuple(terms))


def rates_at_construction() -> tuple[float, float]:
    """`SVENY01` at the construction date, in percent, and its EWMA normal volatility in percent a
    year: D8's EWMA over the committed DEV panel through 2014-12-24 (DD196)."""
    window = FitWindow(DEV_START, CONSTRUCTION)
    levels = [v for v in panel.load_daily(window).column("SVENY01") if v is not None]
    fitted = covariance.fit(("SVENY01",), window, covariance.Method.EWMA)
    return float(levels[-1]), fitted.volatility()[0] * math.sqrt(252.0) / 100.0


# --------------------------------------------------------------------------------------------
# Structures and the gate
# --------------------------------------------------------------------------------------------


class Unsuitable(ValueError):
    """A structure the gate refuses to construct (DD194). Never a warning."""


@dataclass(frozen=True)
class StructureLeg:
    payoff: Payoff
    side: Side
    #: Of the exposure's notional.
    multiple: float
    strike: float


def _obliged(legs: tuple[StructureLeg, ...], level: float) -> float:
    total = 0.0
    for leg in legs:
        if leg.payoff is Payoff.FORWARD:
            total += leg.multiple
        elif leg.side is Side.SOLD and (
            (leg.payoff is Payoff.CALL and level > leg.strike)
            or (leg.payoff is Payoff.PUT and level < leg.strike)
        ):
            total += leg.multiple
    return total


def worst_obligation(legs: tuple[StructureLeg, ...]) -> float:
    """The most the client is obliged to transact in any state, as a multiple of the exposure.

    A forward obliges in every state, a sold option where it finishes in the money, and a bought
    option never: it is a right. Probed at both extremes and on each side of every strike.
    """
    probes = [-math.inf, math.inf]
    for leg in legs:
        probes += [math.nextafter(leg.strike, -math.inf), math.nextafter(leg.strike, math.inf)]
    return max(_obliged(legs, level) for level in probes)


def _pays_when_adverse(legs: tuple[StructureLeg, ...], exposure: Exposure) -> bool:
    for leg in legs:
        if leg.payoff is Payoff.FORWARD:
            long = leg.side is Side.BOUGHT
            if (long and exposure.adverse > 0) or (not long and exposure.adverse < 0):
                return True
        elif leg.side is Side.BOUGHT and leg.payoff is exposure.protective:
            return True
    return False


@dataclass(frozen=True)
class HedgeStructure:
    """A structure that names the exposure it hedges and its worst case, or is unconstructible.

    The iff in `Neutrality`'s shape (DD16, DD17, DD194): the declared worst-state obligation must
    be the one the legs derive, and the derived obligation must not exceed the exposure.
    """

    exposure: Exposure
    legs: tuple[StructureLeg, ...]
    worst_obligation: float

    def __post_init__(self) -> None:
        if not isinstance(self.exposure, Exposure):
            raise TypeError("a hedge names the exposure it hedges")
        if not isinstance(self.legs, tuple) or not self.legs:
            raise TypeError("a hedge has at least one leg")
        if not _pays_when_adverse(self.legs, self.exposure):
            raise Unsuitable("no leg pays when the firm loses, so this structure hedges nothing")
        derived = worst_obligation(self.legs)
        if self.worst_obligation != derived:
            raise Unsuitable(
                f"declares a worst-state obligation of {self.worst_obligation} and its legs "
                f"oblige {derived}"
            )
        if derived > 1.0:
            raise Unsuitable(
                f"leverage {derived}: the worst state obliges the client to transact {derived} "
                "times the exposure it has. That is not a hedge (research §6)"
            )

    @property
    def leverage(self) -> float:
        return self.worst_obligation


# --------------------------------------------------------------------------------------------
# Pricing the menu
# --------------------------------------------------------------------------------------------


def _value(model: Model, payoff: Payoff, forward: float, strike: float, vol: float) -> float:
    call = payoff is Payoff.CALL
    if model is Model.GARMAN_KOHLHAGEN:
        return float(gk_value(call, forward, strike, TENOR_YEARS, vol, RATE, RATE))
    if model is Model.BLACK76:
        return float(black76_value(call, forward, strike, TENOR_YEARS, vol, RATE))
    return float(bachelier_value(call, forward, strike, TENOR_YEARS, vol, RATE))


def _shift(model: Model, forward: float, vol: float, sds: float) -> float:
    """The level `sds` standard deviations from the forward, in the model's own space."""
    step = sds * vol * math.sqrt(TENOR_YEARS)
    return forward + step if model is Model.BACHELIER else forward * math.exp(step)


def _solve(model: Model, forward: float, vol: float, gap) -> float:
    low = _shift(model, forward, vol, -_BRACKET_SD)
    high = _shift(model, forward, vol, _BRACKET_SD)
    return float(brentq(gap, low, high, xtol=1e-15, maxiter=500))


def _unit(model: Model) -> float:
    """Dollars per dollar of exposure per unit of the model's value: a yield in percent accrues
    over the tenor; a moneyness value already is one."""
    return TENOR_YEARS / 100.0 if model is Model.BACHELIER else 1.0


@dataclass(frozen=True)
class Priced:
    """One structure on one exposure at one volatility, per dollar of exposure.

    `premium_paid` and `optionality_sold` are never netted in a field of their own.
    `headline_cost` nets them, and nets in the rate, because it is DD195's objective: what a
    quote sheet shows and what the unconstrained minimiser minimises. It is not what the
    structure costs.
    """

    name: str
    legs: tuple[StructureLeg, ...]
    obligation: float
    premium_paid: float
    optionality_sold: float
    forward: float
    protected: float
    rate_improvement: float

    @property
    def headline_cost(self) -> float:
        return self.premium_paid - self.optionality_sold - self.rate_improvement


def price_menu(exposure: Exposure, forward: float, vol: float) -> tuple[Priced, ...]:
    """DD193's five structures on `exposure`, the forward level and volatility given."""
    model, protective, opposite = exposure.model, exposure.protective, exposure.opposite
    unit, a = _unit(model), exposure.adverse

    def value(payoff: Payoff, strike: float) -> float:
        return _value(model, payoff, forward, strike, vol)

    hedge_side = Side.BOUGHT if a > 0 else Side.SOLD
    collar_strike = _shift(model, forward, vol, a * COLLAR_OFFSET_SD)
    collar_sold = _solve(model, forward, vol, lambda k: value(opposite, k) - value(protective, collar_strike))
    one_strike = {
        p: _solve(model, forward, vol, lambda k, p=p: value(protective, k) - p * value(opposite, k))
        for p in (PARTICIPATION, RATIO)
    }
    structures = {
        "forward": ((StructureLeg(Payoff.FORWARD, hedge_side, 1.0, forward),), forward),
        "bought option": ((StructureLeg(protective, Side.BOUGHT, 1.0, forward),), forward),
        "zero-cost collar": (
            (
                StructureLeg(protective, Side.BOUGHT, 1.0, collar_strike),
                StructureLeg(opposite, Side.SOLD, 1.0, collar_sold),
            ),
            collar_strike,
        ),
        "participating forward": (
            (
                StructureLeg(protective, Side.BOUGHT, 1.0, one_strike[PARTICIPATION]),
                StructureLeg(opposite, Side.SOLD, PARTICIPATION, one_strike[PARTICIPATION]),
            ),
            one_strike[PARTICIPATION],
        ),
        "2:1 ratio forward": (
            (
                StructureLeg(protective, Side.BOUGHT, 1.0, one_strike[RATIO]),
                StructureLeg(opposite, Side.SOLD, RATIO, one_strike[RATIO]),
            ),
            one_strike[RATIO],
        ),
    }
    out = []
    for name in MENU:
        legs, protected = structures[name]
        options = [leg for leg in legs if leg.payoff is not Payoff.FORWARD]
        paid = math.fsum(leg.multiple * value(leg.payoff, leg.strike) for leg in options if leg.side is Side.BOUGHT)
        sold = math.fsum(leg.multiple * value(leg.payoff, leg.strike) for leg in options if leg.side is Side.SOLD)
        out.append(
            Priced(
                name=name,
                legs=legs,
                obligation=worst_obligation(legs),
                premium_paid=paid * unit,
                optionality_sold=sold * unit,
                forward=forward,
                protected=protected,
                # In the client's favour: a higher floor for a seller, a lower cap for a buyer.
                rate_improvement=0.0 - a * (protected - forward) * unit,
            )
        )
    return tuple(out)


def admits(exposure: Exposure, priced: Priced) -> bool:
    try:
        HedgeStructure(exposure, priced.legs, priced.obligation)
    except Unsuitable:
        return False
    return True


def unconstrained_pick(menu: tuple[Priced, ...]) -> Priced:
    """DD195: the lowest headline cost, gate unseen. Ties go to the earlier entry of `MENU`."""
    return min(menu, key=lambda p: p.headline_cost)


def constrained_pick(exposure: Exposure, menu: tuple[Priced, ...]) -> Priced:
    """The lowest headline cost among the structures the gate constructs."""
    return min((p for p in menu if admits(exposure, p)), key=lambda p: p.headline_cost)


# --------------------------------------------------------------------------------------------
# H13
# --------------------------------------------------------------------------------------------


def rungs_for(exposure: Exposure, ewma: float | None = None) -> tuple[tuple[float, str], ...]:
    """DD196: the ladder of the exposure's model family, and the EWMA rung where one exists."""
    ladder = NORMAL_LADDER if exposure.model is Model.BACHELIER else LOGNORMAL_LADDER
    rungs = tuple((vol, "ladder") for vol in ladder)
    return rungs + (((ewma, "EWMA"),) if ewma is not None else ())


@dataclass(frozen=True)
class CaseRung:
    vol: float
    source: str
    unconstrained: str
    leverage: float
    refused: bool
    constrained: str


@dataclass(frozen=True)
class Case:
    exposure: Exposure
    rungs: tuple[CaseRung, ...]

    @property
    def counts(self) -> bool:
        """H13 counts a case iff the unconstrained pick is refused at every rung."""
        return all(rung.refused and rung.leverage > 1.0 for rung in self.rungs)


def score_case(exposure: Exposure, forward: float, rungs: tuple[tuple[float, str], ...]) -> Case:
    out = []
    for vol, source in rungs:
        menu = price_menu(exposure, forward, vol)
        pick = unconstrained_pick(menu)
        out.append(
            CaseRung(
                vol=vol,
                source=source,
                unconstrained=pick.name,
                leverage=pick.obligation,
                refused=not admits(exposure, pick),
                constrained=constrained_pick(exposure, menu).name,
            )
        )
    return Case(exposure, tuple(out))


@dataclass(frozen=True)
class H13Result:
    cases: tuple[Case, ...]
    counted: int
    verdict: Verdict


def h13(cases: tuple[Case, ...]) -> H13Result:
    """PASS iff at least one case counts. §3: on DD193's menu the count is 3, by arithmetic."""
    counted = sum(1 for case in cases if case.counts)
    return H13Result(cases, counted, Verdict.PASS if counted >= 1 else Verdict.FAIL)
