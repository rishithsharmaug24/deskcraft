"""D22: the funding path and crisis-conditional effectiveness (the joint registration §6.1 and §11).

Registered and not landed (DD172). §6.1 locked every rule before D17, D18 and D21 existed, and §11
fixes what the lock left to the code (DD212-DD219) without re-choosing any rule. This module holds
the arithmetic. curvecast's `measure_deskcraft_d22_funding.py` hands it the paths: the one
extraction's rates and currencies, EIA's two crude contracts, the Fed's file and three
`companyfacts`, none of which may be committed here. What comes back is statistics.

**The hedge** is D17's stated exposure: every leg, at 100%, sign-flipped and frozen (DD213). Rates sit
on the one-year zero, currencies at spot as frozen dollar deltas, and crude in frozen barrels of
NYMEX contract 2. **The path** sums each leg's own-session changes by date and cumulates them inside
a window from its first session. Its peak drawdown is `effectiveness.worst_fall` (DD214). **H16**
compares that drawdown with 25% of the operating cash flow in the latest 10-K filed before the
window opens (DD215, DD217). **The options** are bought, six-month and at the money, rolled from
2014-12-24, and reported beside with no verdict (DD216).

**H15 is refused by name** (DD180): the admitted daily equity route does not reach. Its scorer is
here so that the rule the lock fixed runs and is tested. Nothing feeds it.
"""

from __future__ import annotations

import csv
import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np

from deskcraft.costs import CONTRACT_COST_OF
from deskcraft.covariance import EWMA_LAMBDA, Frequency
from deskcraft.effectiveness import SESSIONS, ImpliedReleases, _price, worst_fall
from deskcraft.exposure import clopper_pearson
from deskcraft.hedging import CONSTRUCTION, Exposure, Model
from deskcraft.panel import FX_QUOTES
from deskcraft.registers import Verdict
from deskcraft.scenarios import REPLAY_WINDOWS
from deskcraft.window import FitWindow, OosWindow

#: §6.1's H16: the first three firms of the cohort ordering.
CASE_CLIENTS = 3
#: §6.1's H16: a client-window counts iff its peak drawdown exceeds this share of trailing cash flow.
DRAWDOWN_SHARE = 0.25
#: DD167 applied to D22 (§6.1): the two windows the verdict reads, and the three reported beside.
VERDICT_WINDOWS = ("NBER_2020", "RATES_2022")
BESIDE_WINDOWS = ("NBER_1990", "NBER_2001", "NBER_2007")
WINDOWS: dict[str, FitWindow | OosWindow] = {w.name: w.window for w in REPLAY_WINDOWS}
#: DD216: options roll every six calendar months from the construction date.
ROLL_MONTHS = 6
#: DD215: the lock's concept, then the same line for a filer with nothing discontinued.
OCF_CONCEPTS = (
    "NetCashProvidedByUsedInOperatingActivities",
    "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
)
#: DD215: a fiscal year's duration in days, as D17 §3 reads one.
ANNUAL_DAYS = (350, 380)
#: §6.1's H15: a firm counts iff conditional effectiveness is under this share of unconditional,
#: and the claim passes iff at least `H15_SHARE` of the firms count.
H15_FRACTION = 0.5
H15_SHARE = 0.60
H15_REFUSAL = (
    "DD180: the admitted daily equity route serves only the last 100 sessions, so no daily return "
    "reaches the two years ending 2014-12-24, and H15 is refused by name"
)
#: DD216 item 3: D8's daily decay.
EWMA_DECAY = EWMA_LAMBDA[Frequency.DAILY]
#: DD218's simulations.
SEED = 20260928
CROSSING_PATHS = 20_000

#: DD213 item 5 (DD175, DD179): what each class's leg stands for, and what the substitution drops.
STANDS_FOR: dict[str, tuple[str, tuple[str, ...]]] = {
    "rates": (
        "an interest-rate swap or Treasury future, carried as the one-year zero",
        ("financing", "delivery option", "roll", "futures-cash basis", "swap spread"),
    ),
    "currency": ("a forward, carried at spot", ("forward points", "cross-currency basis")),
    "crude": ("NYMEX WTI contract 2", ("product-over-crude spread",)),
}

#: Each currency's H.10 series, and whether H.10 quotes it in dollars per unit (`panel.FX_QUOTES`).
FX_SERIES_OF: dict[str, str] = {code: series for series, (code, _) in FX_QUOTES.items()}
USD_PER_UNIT: dict[str, bool] = {code: quote.startswith("USD per") for code, quote in FX_QUOTES.values()}


# --------------------------------------------------------------------------------------------
# The hedge (DD213)
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class HedgeLeg:
    """One stated exposure, hedged at 100% and frozen at construction."""

    exposure: Exposure
    #: Crude only: N over the 2014-12-24 contract-2 settle, carried through every roll (DD176).
    barrels: float | None
    stands_for: str
    unmodelled: tuple[str, ...]

    @property
    def series(self) -> str:
        """The factor the leg is marked on: a panel series, or `WTI_C2`."""
        if self.exposure.cls == "currency":
            return FX_SERIES_OF[self.exposure.instrument]
        return self.exposure.instrument


def hedge_legs(exposures: Sequence[Exposure], crude_settle: float | None) -> tuple[HedgeLeg, ...]:
    """DD213: each exposure's leg. `crude_settle` is contract 2's settle on 2014-12-24, needed only
    if an exposure is crude. A rates exposure off `SVENY01` is refused: C184 and C201 hold that D7b's
    generator takes that one series for it, and a leg on another would be a choice."""
    legs = []
    for exposure in exposures:
        stands_for, unmodelled = STANDS_FOR[exposure.cls]
        barrels = None
        if exposure.cls == "crude":
            if exposure.instrument != "WTI_C2":
                raise ValueError(f"a crude exposure is hedged in WTI_C2, not {exposure.instrument!r}")
            if crude_settle is None or not (math.isfinite(crude_settle) and crude_settle > 0.0):
                raise ValueError(f"a crude leg needs a positive construction settle, got {crude_settle!r}")
            barrels = exposure.amount_usd / crude_settle
        elif exposure.cls == "currency" and exposure.instrument not in FX_SERIES_OF:
            raise ValueError(f"{exposure.instrument!r} is not one of the seven H.10 currencies")
        elif exposure.cls == "rates" and exposure.instrument != "SVENY01":
            raise ValueError(f"a rates exposure sits on SVENY01, not {exposure.instrument!r}")
        legs.append(HedgeLeg(exposure, barrels, stands_for, unmodelled))
    return tuple(legs)


def case_clients(exposures: Sequence[Exposure]) -> dict[int, tuple[Exposure, ...]]:
    """§6.1's case clients, cohort ranks 1 to 3, each with every stated exposure it has."""
    out = {}
    for rank in range(1, CASE_CLIENTS + 1):
        mine = tuple(e for e in exposures if e.cohort_rank == rank)
        if not mine:
            raise ValueError(f"cohort rank {rank} states no exposure")
        out[rank] = mine
    return out


# --------------------------------------------------------------------------------------------
# A leg's changes on its own sessions (DD213 items 2-4 and 6)
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class LegPath:
    """A leg's changes, each from `starts[i]` to `ends[i]`: its P&L in dollars before costs, whether
    DD213 item 6 refuses it, and what it paid in costs."""

    starts: tuple[date, ...]
    ends: tuple[date, ...]
    pnl: np.ndarray
    refused: np.ndarray
    cost: np.ndarray


def _path(days: Sequence[date], pnl: np.ndarray, refused: np.ndarray | None = None, cost: np.ndarray | None = None) -> LegPath:
    days = tuple(days)
    if len(pnl) != len(days) - 1:
        raise ValueError("a path of n sessions has n - 1 changes")
    if any(b <= a for a, b in zip(days, days[1:])):
        raise ValueError("sessions must be strictly increasing")
    zeros = np.zeros(len(pnl))
    return LegPath(
        days[:-1],
        days[1:],
        pnl,
        zeros.astype(bool) if refused is None else refused,
        zeros if cost is None else cost,
    )


def rates_path(leg: HedgeLeg, days: Sequence[date], yields_pct: Sequence[float]) -> LegPath:
    """Item 2: −s × N × Δy, the one-year zero in percent turned to a decimal."""
    y = np.asarray(yields_pct, dtype=float)
    return _path(days, -leg.exposure.sign * leg.exposure.amount_usd * np.diff(y) / 100.0)


def currency_path(leg: HedgeLeg, days: Sequence[date], quotes: Sequence[float]) -> LegPath:
    """Item 3: −s × N × Δ ln(USD per unit), each H.10 quote turned the right way."""
    q = np.asarray(quotes, dtype=float)
    if np.any(~np.isfinite(q)) or np.any(q <= 0.0):
        raise ValueError(f"{leg.series}: an exchange rate is positive and finite")
    usd = np.log(q) if USD_PER_UNIT[leg.exposure.instrument] else -np.log(q)
    return _path(days, -leg.exposure.sign * leg.exposure.amount_usd * np.diff(usd))


def held_settles(c1: Sequence[float], c2: Sequence[float], rolled: Sequence[bool]) -> tuple[np.ndarray, np.ndarray]:
    """Each change's two settles of the one contract held across it (DD176). `rolled[i]` says session
    i is the first after contract 1 expired, when yesterday's contract 2 is today's contract 1."""
    c1, c2 = np.asarray(c1, dtype=float), np.asarray(c2, dtype=float)
    roll = np.asarray(rolled, dtype=bool)
    return c2[:-1], np.where(roll[1:], c1[1:], c2[1:])


def crude_path(
    leg: HedgeLeg,
    days: Sequence[date],
    c1: Sequence[float],
    c2: Sequence[float],
    rolled: Sequence[bool],
) -> LegPath:
    """Item 4: −s × Q × (F_t − F_{t−1}) on one contract's two settles, and on a roll session the
    roll's cost. Item 6: a change with a settle at or below zero is refused, never imputed."""
    before, after = held_settles(c1, c2, rolled)
    refused = ~(np.isfinite(before) & np.isfinite(after) & (before > 0.0) & (after > 0.0))
    pnl = -leg.exposure.sign * leg.barrels * (after - before)
    pnl[refused] = np.nan
    roll_cost = CONTRACT_COST_OF["WTI_C2"].roll_cost(leg.barrels)
    cost = np.where(np.asarray(rolled, dtype=bool)[1:], roll_cost, 0.0)
    return _path(days, pnl, refused, cost)


def crude_returns(c1: Sequence[float], c2: Sequence[float], rolled: Sequence[bool]) -> np.ndarray:
    """Contract 2's roll-aware log return on each change: D17's `contract_two_returns`, on arrays.
    A refused change returns NaN."""
    before, after = held_settles(c1, c2, rolled)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.log(after / before)
    out[~((before > 0.0) & (after > 0.0))] = np.nan
    return out


# --------------------------------------------------------------------------------------------
# The window's path and its peak drawdown (DD214)
# --------------------------------------------------------------------------------------------


def inside(window: FitWindow | OosWindow, start: date, end: date) -> bool:
    """DD214: a change counts toward a window iff both of its sessions lie in it."""
    return window.start <= start and end <= window.end


@dataclass(frozen=True)
class WindowPath:
    """A hedge's P&L inside one window, summed across legs by date, net of costs."""

    days: tuple[date, ...]
    pnl: np.ndarray
    #: Changes DD213 item 6 refused; any refuses the client-window.
    refused: int
    #: Crude roll sessions inside the window, and what they cost (DD212 item 3).
    rolls: int
    cost: float

    @property
    def peak_drawdown(self) -> float:
        return worst_fall(self.pnl)


def window_path(paths: Sequence[LegPath], window: FitWindow | OosWindow) -> WindowPath:
    totals: dict[date, float] = {}
    refused = rolls = 0
    cost = 0.0
    for path in paths:
        for a, b, value, bad, paid in zip(path.starts, path.ends, path.pnl, path.refused, path.cost):
            if not inside(window, a, b):
                continue
            if bad:
                refused += 1
                continue
            totals[b] = totals.get(b, 0.0) + float(value) - float(paid)
            if paid > 0.0:
                rolls += 1
                cost += float(paid)
    days = tuple(sorted(totals))
    return WindowPath(days, np.array([totals[d] for d in days]), refused, rolls, cost)


# --------------------------------------------------------------------------------------------
# The bought options beside (DD216)
# --------------------------------------------------------------------------------------------


def ewma_path(changes: Sequence[float]) -> np.ndarray:
    """D8's EWMA through each change, normalised weights, annualised on 252 sessions: the i-th value
    reads `changes[: i + 1]`, and equals `effectiveness.ewma_volatility` on that slice. A NaN change
    (a refused crude day) is skipped, not imputed."""
    out = np.empty(len(changes))
    weighted = total = 0.0
    for i, x in enumerate(changes):
        if math.isfinite(x):
            weighted = EWMA_DECAY * weighted + x * x
            total = EWMA_DECAY * total + 1.0
        out[i] = math.sqrt(weighted / total * SESSIONS) if total > 0.0 else math.nan
    return out


def add_months(day: date, months: int) -> date:
    years, month = divmod(day.month - 1 + months, 12)
    return date(day.year + years, month + 1, day.day)


def roll_dates(first: date, last: date) -> list[date]:
    """Item 2: 2014-12-24 and every six calendar months from it, forwards and backwards, from the
    last one on or before `first` through the first one after `last`."""
    k = 0
    while add_months(CONSTRUCTION, ROLL_MONTHS * k) > first:
        k -= 1
    while add_months(CONSTRUCTION, ROLL_MONTHS * (k + 1)) <= first:
        k += 1
    out = [add_months(CONSTRUCTION, ROLL_MONTHS * k)]
    while out[-1] <= last:
        k += 1
        out.append(add_months(CONSTRUCTION, ROLL_MONTHS * k))
    return out


@dataclass(frozen=True)
class OptionPath:
    """A leg's bought options, marked on its sessions: each change's mark-to-market in dollars net
    of premium paid and payoff received, and the premium paid on each purchase session."""

    starts: tuple[date, ...]
    ends: tuple[date, ...]
    pnl: np.ndarray
    premiums: dict[date, float]
    #: Marks on each session, and whether the Fed's volatility priced it (DD210's mapping).
    marked: tuple[date, ...]
    by_fed: tuple[bool, ...]


def _model_spot(model: Model, level: np.ndarray, i: int, bought: int) -> tuple[float, float]:
    """Forward and strike in the model's own space: the yield in percent for Bachelier, moneyness
    against the purchase day's level otherwise (item 1)."""
    if model is Model.BACHELIER:
        return float(level[i]), float(level[bought])
    return math.exp(float(level[i] - level[bought])), 1.0


def option_path(
    leg: HedgeLeg,
    days: Sequence[date],
    level: Sequence[float],
    vols: Sequence[float],
    scale: Sequence[float],
    by_fed: Sequence[bool] | None = None,
) -> OptionPath:
    """DD216 on one leg. `level` is the factor in the model's space on each session: the yield in
    percent for rates, ln(USD per unit) for currency, crude's cumulative roll-aware log return.
    `vols` is each session's annualised volatility in that space, and `scale` the dollars per unit
    of model value for an option bought that session: N × 0.01 for rates, N for currency, and
    barrels × that session's contract-2 settle for crude.

    Each roll date's option is bought on the first session on or after it, at the money, and
    expires at the next roll date, settling at intrinsic on the first session on or after that. A
    roll dated before the first session, or whose session has no volatility yet, buys nothing: its
    true purchase session is not on the path, and a stub bought later would be a different option.
    `live[i]` is the option held at the close of session i, after any settlement and purchase."""
    days = tuple(days)
    level, vols, scale = (np.asarray(a, dtype=float) for a in (level, vols, scale))
    fed = tuple(bool(b) for b in by_fed) if by_fed is not None else (False,) * len(days)
    model, payoff = leg.exposure.model, leg.exposure.protective
    ordinals = np.array([d.toordinal() for d in days])
    rolls = roll_dates(days[0], days[-1])
    bought: dict[int, date] = {}
    for when, expiry in zip(rolls, rolls[1:]):
        if when < days[0]:
            continue
        at = int(np.searchsorted(ordinals, when.toordinal(), side="left"))
        if at < len(days) and at not in bought and math.isfinite(vols[at]) and vols[at] > 0.0:
            bought[at] = expiry
    live: list[tuple[int, date] | None] = [None] * len(days)
    current: tuple[int, date] | None = None
    for i in range(len(days)):
        if current is not None and days[i] >= current[1]:
            current = None
        if i in bought:
            current = (i, bought[i])
        live[i] = current

    def worth(i: int, option: tuple[int, date]) -> float:
        start, expiry = option
        tau = max((expiry - days[i]).days, 0) / 365.0
        forward, strike = _model_spot(model, level, i, start)
        return float(scale[start]) * _price(model, payoff, forward, strike, tau, float(vols[i]))

    pnl = np.zeros(len(days) - 1)
    for i in range(1, len(days)):
        option = live[i - 1]
        if option is not None:
            pnl[i - 1] = worth(i, option) - worth(i - 1, option)
    premiums = {days[i]: worth(i, (i, expiry)) for i, expiry in sorted(bought.items())}
    return OptionPath(days[:-1], days[1:], pnl, premiums, days, fed)


@dataclass(frozen=True)
class OptionWindow:
    """DD216 items 4 and 5 inside one window."""

    #: The registered number: premiums paid for purchases inside the window.
    premium: float
    #: The option book's own worst fall inside the window.
    worst_fall: float
    #: Of the marks inside the window on legs DD210 maps, the fraction the Fed priced; None if the
    #: client has no mapped leg.
    implied_fraction: float | None


def option_window(paths: Sequence[tuple[HedgeLeg, OptionPath]], window: FitWindow | OosWindow, mapped: set[str]) -> OptionWindow:
    totals: dict[date, float] = {}
    premium = 0.0
    marks = fed = 0
    for leg, path in paths:
        for a, b, value in zip(path.starts, path.ends, path.pnl):
            if inside(window, a, b):
                totals[b] = totals.get(b, 0.0) + float(value)
        premium += sum(v for d, v in path.premiums.items() if window.start <= d <= window.end)
        if leg.exposure.instrument in mapped:
            for d, priced in zip(path.marked, path.by_fed):
                if window.start <= d <= window.end:
                    marks += 1
                    fed += priced
    days = sorted(totals)
    return OptionWindow(premium, worst_fall(np.array([totals[d] for d in days])), fed / marks if marks else None)


def leg_vols(leg: HedgeLeg, days: Sequence[date], ewma: Sequence[float], releases: ImpliedReleases | None) -> tuple[np.ndarray, tuple[bool, ...]]:
    """DD216 item 3: the Fed's release where DD210 maps the leg and one is fresh, else EWMA's."""
    vols, fed = [], []
    for day, fallback in zip(days, ewma):
        implied = releases.volatility(leg.exposure.instrument, day) if releases is not None else None
        vols.append(implied if implied is not None else fallback)
        fed.append(implied is not None)
    return np.array(vols), tuple(fed)


# --------------------------------------------------------------------------------------------
# Trailing operating cash flow (DD215)
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class CashFlowRead:
    value: float | None
    filed: str
    concept: str
    fy_end: str
    refused: str


def _days(fact: dict) -> int:
    return (date.fromisoformat(fact["end"]) - date.fromisoformat(fact["start"])).days


def trailing_ocf(facts: Sequence[dict], before: date) -> CashFlowRead:
    """DD215 on a firm's `companyfacts` facts, each with `concept`, `form`, `filed` and `accn`, and
    `start`, `end` and `val` where it is a cash-flow fact. The latest 10-K filed before `before` is
    found among every concept's facts; an earlier 10-K is never used in its place."""
    tenk = [f for f in facts if f.get("form") == "10-K" and f.get("filed") and date.fromisoformat(f["filed"]) < before]
    if not tenk:
        return CashFlowRead(None, "", "", "", f"no 10-K filed before {before.isoformat()}")
    filed, accn = max((f["filed"], f.get("accn", "")) for f in tenk)
    mine = [f for f in tenk if f["filed"] == filed and f.get("accn", "") == accn]
    for concept in OCF_CONCEPTS:
        annual = [
            f
            for f in mine
            if f.get("concept") == concept
            and f.get("start")
            and f.get("end")
            and ANNUAL_DAYS[0] <= _days(f) <= ANNUAL_DAYS[1]
        ]
        if not annual:
            continue
        fact = max(annual, key=lambda f: f["end"])
        value = float(fact["val"])
        if not (math.isfinite(value) and value > 0.0):
            return CashFlowRead(value, filed, concept, fact["end"], f"operating cash flow of {value:.0f} is not positive")
        return CashFlowRead(value, filed, concept, fact["end"], "")
    return CashFlowRead(None, filed, "", "", f"the 10-K filed {filed} carries neither {' nor '.join(OCF_CONCEPTS)}")


# --------------------------------------------------------------------------------------------
# What leaves curvecast, and the scorers (DD217, DD219)
# --------------------------------------------------------------------------------------------

#: DD219: the fixture's columns, in order. Statistics only: never a price, a settle or a quantity.
#: DD240. The first column dates the file by the end of the panel it was read from, as D21's
#: `oos_end_date` does, so C119 and C97 read a result of the record as one. The first file of
#: 2026-09-28 lacked it and those bars could not date it; it was re-run, not edited.
COLUMNS = (
    "oos_end_date",
    "cohort_rank",
    "cik",
    "window",
    "changes",
    "legs_marked",
    "peak_drawdown",
    "rolls",
    "roll_cost",
    "ocf_usd",
    "ocf_filed",
    "ocf_concept",
    "ocf_fy_end",
    "refused",
    "option_premium",
    "option_worst_fall",
    "implied_fraction",
    "implied_basis",
)


@dataclass(frozen=True)
class FundingRow:
    """One case client in one window."""

    cohort_rank: int
    cik: str
    window: str
    changes: int
    #: Legs with at least one change inside the window, of the client's stated legs.
    legs_marked: int
    peak_drawdown: float | None
    rolls: int
    roll_cost: float
    ocf_usd: float | None
    ocf_filed: str
    ocf_concept: str
    ocf_fy_end: str
    #: Why the client-window is not scored, or empty.
    refused: str
    option_premium: float | None
    option_worst_fall: float | None
    implied_fraction: float | None
    implied_basis: str

    @property
    def ratio(self) -> float | None:
        """Peak drawdown over trailing operating cash flow, where both exist and nothing refuses it."""
        if self.refused or self.peak_drawdown is None or self.ocf_usd is None or self.ocf_usd <= 0.0:
            return None
        return self.peak_drawdown / self.ocf_usd

    @property
    def exceeds(self) -> bool:
        return self.ratio is not None and self.ratio > DRAWDOWN_SHARE


def funding_row(
    rank: int,
    cik: str,
    window: str,
    path: WindowPath,
    legs_marked: int,
    cash: CashFlowRead,
    options: OptionWindow | None,
    basis: str,
) -> FundingRow:
    """A client-window's row. DD213 item 6 and DD215 item 4 decide `refused`, in that order."""
    refused = f"{path.refused} crude changes refused (DD213 item 6)" if path.refused else cash.refused
    if not path.days and not refused:
        refused = "no change inside the window"
    return FundingRow(
        cohort_rank=rank,
        cik=cik,
        window=window,
        changes=len(path.days),
        legs_marked=legs_marked,
        peak_drawdown=path.peak_drawdown if path.days else None,
        rolls=path.rolls,
        roll_cost=path.cost,
        ocf_usd=cash.value,
        ocf_filed=cash.filed,
        ocf_concept=cash.concept,
        ocf_fy_end=cash.fy_end,
        refused=refused,
        option_premium=None if options is None else options.premium,
        option_worst_fall=None if options is None else options.worst_fall,
        implied_fraction=None if options is None else options.implied_fraction,
        implied_basis=basis,
    )


def _cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return repr(value)
    return str(value)


def row_cells(row: FundingRow, end: date) -> dict[str, str]:
    """The row as the fixture writes it, dated by the end of the panel it was read from (DD240)."""
    return {"oos_end_date": end.isoformat(), **{name: _cell(getattr(row, name)) for name in COLUMNS[1:]}}


def _float(text: str) -> float | None:
    return float(text) if text not in ("", None) else None


def load_funding(path: Path) -> tuple[FundingRow, ...]:
    """D22's fixture. Taken as a path: no module here names an out-of-sample file (C119)."""
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != COLUMNS:
            raise ValueError(f"{path.name}: columns {reader.fieldnames} are not DD219's")
        rows = list(reader)
    if len({date.fromisoformat(row["oos_end_date"]) for row in rows}) > 1:
        raise ValueError(f"{path.name}: rows read from more than one panel (DD240)")
    return tuple(
        FundingRow(
            cohort_rank=int(row["cohort_rank"]),
            cik=row["cik"],
            window=row["window"],
            changes=int(row["changes"]),
            legs_marked=int(row["legs_marked"]),
            peak_drawdown=_float(row["peak_drawdown"]),
            rolls=int(row["rolls"]),
            roll_cost=float(row["roll_cost"]),
            ocf_usd=_float(row["ocf_usd"]),
            ocf_filed=row["ocf_filed"],
            ocf_concept=row["ocf_concept"],
            ocf_fy_end=row["ocf_fy_end"],
            refused=row["refused"],
            option_premium=_float(row["option_premium"]),
            option_worst_fall=_float(row["option_worst_fall"]),
            implied_fraction=_float(row["implied_fraction"]),
            implied_basis=row["implied_basis"],
        )
        for row in rows
    )


@dataclass(frozen=True)
class H16Result:
    verdict: Verdict
    counted: int
    evaluable: int
    #: (cohort rank, window) to drawdown over cash flow, or None where refused.
    ratios: dict[tuple[int, str], float | None]
    refusals: dict[tuple[int, str], str]


def h16(rows: Sequence[FundingRow]) -> H16Result:
    """DD217 item 1: PASS iff at least one case client's drawdown exceeds 25% of its trailing cash
    flow in a verdict window. A refused client-window counts as not exceeding; all six refused is
    `NOT_PERFORMED`. The DEV windows are never read here."""
    scored = {(r.cohort_rank, r.window): r for r in rows if r.window in VERDICT_WINDOWS and r.cohort_rank <= CASE_CLIENTS}
    expected = {(rank, window) for rank in range(1, CASE_CLIENTS + 1) for window in VERDICT_WINDOWS}
    if set(scored) != expected:
        raise ValueError(f"H16 reads six client-windows; missing {sorted(expected - set(scored))}")
    evaluable = [r for r in scored.values() if r.ratio is not None]
    counted = sum(r.exceeds for r in evaluable)
    if not evaluable:
        verdict = Verdict.NOT_PERFORMED
    else:
        verdict = Verdict.PASS if counted else Verdict.FAIL
    return H16Result(
        verdict=verdict,
        counted=counted,
        evaluable=len(evaluable),
        ratios={key: row.ratio for key, row in sorted(scored.items())},
        refusals={key: row.refused for key, row in sorted(scored.items()) if row.refused},
    )


@dataclass(frozen=True)
class H15Result:
    firms: int
    counted: int
    interval: tuple[float, float]
    verdict: Verdict
    reason: str


def h15(pairs: Sequence[tuple[float, float]]) -> H15Result:
    """§6.1's H15 on each firm's (unconditional, conditional) Ederington effectiveness. A firm counts
    iff conditional < ½ × unconditional; an unconditional effectiveness at or below zero does not
    count. PASS iff at least 60% count. DD217 item 2: nothing feeds this, and `h15_refused` is the
    verdict D22 records."""
    if not pairs:
        return H15Result(0, 0, (math.nan, math.nan), Verdict.NOT_PERFORMED, "no firm to score")
    counted = sum(1 for u, c in pairs if u > 0.0 and c < H15_FRACTION * u)
    verdict = Verdict.PASS if counted / len(pairs) >= H15_SHARE else Verdict.FAIL
    return H15Result(len(pairs), counted, clopper_pearson(counted, len(pairs)), verdict, "")


def h15_refused() -> H15Result:
    """DD180 and DD217 item 2."""
    return H15Result(0, 0, (math.nan, math.nan), Verdict.NOT_PERFORMED, H15_REFUSAL)


# --------------------------------------------------------------------------------------------
# What H16 can show before the read (DD218)
# --------------------------------------------------------------------------------------------


def dollar_sd(exposure: Exposure, annual_vol: float) -> float:
    """A 100% leg's daily dollar deviation at construction: N × σ / √252. For rates σ is the yield's
    in decimal a year; for currency and crude, the log return's, crude's at the construction price."""
    return exposure.amount_usd * annual_vol / math.sqrt(SESSIONS)


def crossing_probability(
    deviations: Sequence[float],
    threshold: float,
    changes: int,
    paths: int = CROSSING_PATHS,
    seed: int = SEED,
) -> float:
    """DD218: the probability that a driftless Gaussian hedge path of `changes` daily steps, its legs
    independent with these daily dollar deviations, falls further than `threshold` from a running
    peak that starts at zero. Independent legs sum to one leg with the root-sum-square deviation."""
    total = math.sqrt(sum(d * d for d in deviations))
    if total == 0.0:
        return 0.0
    rng = np.random.default_rng(seed)
    steps = rng.standard_normal((paths, changes)) * total
    path = np.concatenate([np.zeros((paths, 1)), np.cumsum(steps, axis=1)], axis=1)
    fall = np.max(np.maximum.accumulate(path, axis=1) - path, axis=1)
    return float(np.mean(fall > threshold))
