"""C200-C207. D22, the funding path and crisis-conditional effectiveness (the joint registration §11).

Registered and not landed (DD172), so every rule is held on cases whose answer is known and the
registration is held against drift. Every exposure here is D17's committed stated fixture or
invented, and every price is invented: EIA's settles, the Fed's file and `companyfacts` after 2014 are
read only by curvecast's script, at D22's own read. Nothing here touches the network.
"""

from __future__ import annotations

import csv
import math
from dataclasses import replace
from datetime import date, timedelta

import numpy as np
import pytest

from deskcraft import funding as f
from deskcraft.costs import (
    COST_OF,
    CONTRACT_COST_OF,
    WTI_TICK_USD_PER_BARREL,
    ContractCost,
    CostBasis,
    DurationConvention,
)
from deskcraft.effectiveness import ImpliedReleases, ewma_volatility, worst_fall
from deskcraft.factors import build_basis
from deskcraft.hedging import Exposure, Payoff, hedge_target, load_stated
from deskcraft.generator import select
from deskcraft.panel import FitWindow, load_daily
from deskcraft.registers import CLAIMS, Verdict
from deskcraft.window import OosWindow
from test_deskcraft_boundary import REPO_ROOT, _read
from test_guards_and_registers import closed

FIXTURES = REPO_ROOT / "tests" / "fixtures"
STATED = FIXTURES / "d17_stated_dev_20260926.csv"
REGISTRATION = sorted((REPO_ROOT / "docs").glob("PRECOMMIT_deskcraft_d12_d14_d15_d22*.md"))[0]

#: ExxonMobil's FY2013 operating cash flow, from its 10-K instance (accession 0000034088-14-000012,
#: filed 2014-02-26), tagged only as the continuing-operations concept (DD215 item 3). SEC data, public
#: domain; the only figure here not in a committed fixture, and it is dated before construction.
XOM_FY2013_OCF = 44_914_000_000.0

#: §11's rules, as the registration spells them. A phrase dropped or reworded turns C207 red.
FIXED = (
    "**DD212 — DD176's WTI cost row lands in D7a's cost model, before D22 builds, as DD205 owed it.**",
    "a half-spread of **one tick, $0.01 a barrel**",
    "**A roll crosses the half-spread twice**",
    "**The 1× rung is the row as stated.**",
    "**DD213 — the hedge D22 replays is D17's stated exposure: every leg, at 100%, sign-flipped and frozen.**",
    "**−s × N × Δy**",
    "**−s × N × Δ ln(USD per unit)**",
    "**The crude leg holds Q = N ÷ the 2014-12-24 contract-2 settle barrels**",
    "**−s × Q × (F_t − F_{t−1}) on one contract's two settles**",
    "**The window that contains a refused change is refused for that client, and counted as not exceeding.**",
    "**A change counts toward a window iff both of its sessions lie in the window**",
    "**If the filing carries no such fact, `NetCashProvidedByUsedInOperatingActivitiesContinuingOperations`**",
    "**So this reading moves H16 toward its predicted PASS, the flattering direction.**",
    "An earlier 10-K is never used in place of the latest.",
    "**The lock's \"at-the-money strike on the frozen level\" is read as at the money on the level of the day the",
    "**`NBER_2020` holds no roll date**",
    "**zero by the calendar**",
    "**counts iff its peak drawdown exceeds 25% of its trailing operating cash flow**",
    "**H15 is refused by name** (DD180)",
    "**It refuses before any request** unless the authorisation exists, names DD37 **and D22**",
    "statistics only: never a price, never a settle, never a quantity of barrels",
)


def _flat(text: str) -> str:
    return " ".join(line.lstrip("> ").strip() for line in text.splitlines())


def _section_11() -> str:
    text = _read(REGISTRATION)
    return text[text.index("## 11. D22's code, built to §6.1 and rehearsed on DEV, not run") :]


def _weekdays(start: date, end: date) -> list[date]:
    out, day = [], start
    while day <= end:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def _exposure(cls: str, instrument: str, sign: int, amount: float, rank: int = 9) -> Exposure:
    return Exposure(rank, "0", cls, instrument, sign, amount)


def _leg(cls: str, instrument: str, sign: int, amount: float, settle: float | None = None) -> f.HedgeLeg:
    (leg,) = f.hedge_legs((_exposure(cls, instrument, sign, amount),), settle)
    return leg


# --------------------------------------------------------------------------------------------
# C200: DD212's cost row
# --------------------------------------------------------------------------------------------


def test_c200_the_wti_cost_row_is_one_tick_and_a_roll_pays_it_twice() -> None:
    """C200. DD212, owed by DD205. The row is one tick a barrel on CME's quoting convention, outside
    `COST_OF` (C87's partition of the committed register is untouched), and a roll crosses it twice
    whichever way the position faces. The only cost on a window's path is the crude rolls.

    **Mutation:** a row with no evidence, a zero spread, an integer spread or a fourth basis is
    refused; a doubled tick doubles a roll session's cost on the path.
    """
    row = CONTRACT_COST_OF["WTI_C2"]
    assert row.half_spread_usd == WTI_TICK_USD_PER_BARREL == 0.01
    assert row.unit == "barrel" and row.basis is CostBasis.QUOTING_CONVENTION
    assert "$0.01 per barrel" in row.evidence
    assert "WTI_C2" not in COST_OF
    assert row.roll_cost(1_000_000.0) == row.roll_cost(-1_000_000.0) == 20_000.0

    for bad in (
        dict(evidence=" "),
        dict(half_spread_usd=0.0),
        dict(half_spread_usd=1),
        dict(basis="MEASURED"),
    ):
        with pytest.raises((TypeError, ValueError)):
            ContractCost(**{**dict(instrument="X", unit="barrel", half_spread_usd=0.01,
                                   basis=CostBasis.QUOTING_CONVENTION, evidence="e"), **bad})

    leg = _leg("crude", "WTI_C2", -1, 5_000.0, settle=50.0)
    days = [date(2020, 3, 2), date(2020, 3, 3), date(2020, 3, 4)]
    path = f.crude_path(leg, days, [40.0, 41.0, 42.0], [50.0, 51.0, 52.0], [False, True, False])
    assert list(path.cost) == [2 * 0.01 * 100.0, 0.0]


# --------------------------------------------------------------------------------------------
# C201: DD213's legs
# --------------------------------------------------------------------------------------------


def test_c201_the_hedge_is_every_stated_leg_at_100_percent_and_d7b_takes_sveny01() -> None:
    """C201. DD213 items 1, 2 and 5. The case clients are cohort ranks 1-3 with every leg they state:
    GE two, ExxonMobil six, AT&T one. Crude is held in barrels, N over the construction settle. Each
    leg carries DD175's and DD179's labels. D7b's `select` on each case client's rates target takes
    `OUT_SVENY01` alone at cosine 1, the check C184 made for GE, made for all three.

    **Mutation:** a rates leg off `SVENY01`, a crude leg without a settle, and a currency outside the
    seven are refused.
    """
    clients = f.case_clients(load_stated(STATED))
    assert {rank: sorted((e.cls, e.instrument) for e in legs) for rank, legs in clients.items()} == {
        1: [("crude", "WTI_C2"), ("rates", "SVENY01")],
        2: [("crude", "WTI_C2"), ("currency", "CAD"), ("currency", "EUR"), ("currency", "GBP"),
            ("currency", "JPY"), ("rates", "SVENY01")],
        3: [("rates", "SVENY01")],
    }
    legs = f.hedge_legs(clients[2], crude_settle=61.0)
    crude = next(leg for leg in legs if leg.exposure.cls == "crude")
    assert crude.barrels == crude.exposure.amount_usd / 61.0
    assert all(leg.barrels is None for leg in legs if leg is not crude)
    by_class = {leg.exposure.cls: leg for leg in legs}
    assert by_class["rates"].unmodelled == ("financing", "delivery option", "roll", "futures-cash basis", "swap spread")
    assert by_class["currency"].unmodelled == ("forward points", "cross-currency basis")
    assert crude.unmodelled == ("product-over-crude spread",)
    assert {leg.series for leg in legs} == {"WTI_C2", "DEXCAUS", "DEXUSEU", "DEXUSUK", "DEXJPUS", "SVENY01"}

    basis = build_basis()
    daily = load_daily(FitWindow.dev())
    row = daily.dates.index(date(2014, 12, 24))
    yields = {s: v for s in daily.series if (v := daily.values[s][row]) is not None}
    for rank, stated in clients.items():
        (rates,) = [e for e in stated if e.cls == "rates"]
        selection = select(hedge_target((rates,)), basis, yields, convention=DurationConvention.AS_QUOTED)
        assert [a.symbol for a in selection.additions] == ["OUT_SVENY01"], rank
        assert math.isclose(selection.cosine, 1.0, abs_tol=1e-12), rank

    with pytest.raises(ValueError):
        f.hedge_legs((_exposure("rates", "SVENY02", -1, 1.0),), None)
    with pytest.raises(ValueError):
        f.hedge_legs((_exposure("crude", "WTI_C2", 1, 1.0),), None)
    with pytest.raises(ValueError):
        f.hedge_legs((_exposure("currency", "AUD", 1, 1.0),), None)


# --------------------------------------------------------------------------------------------
# C202: each leg's arithmetic
# --------------------------------------------------------------------------------------------


def test_c202_each_leg_marks_its_own_instrument_the_right_way() -> None:
    """C202. DD213 items 2-4 and 6. Rates and currency legs telescope to −s·N times the factor's
    whole move; a yen revenue's hedge gains when the yen weakens, though H.10 quotes yen per dollar;
    crude marks barrels times a price change, on one contract's two settles, contract 1 against
    yesterday's contract 2 on a roll session; a non-positive settle refuses exactly the changes that
    use it; and crude's roll-aware return is D17's.

    **Mutation:** reading the roll session as contract 2 against contract 2 moves its P&L by the
    calendar spread; a negative contract 1 on a session the hedge holds contract 2 refuses nothing,
    which is April 2020's shape.
    """
    days = _weekdays(date(2022, 3, 1), date(2022, 3, 10))
    yields = np.linspace(1.00, 1.40, len(days))
    ge = _leg("rates", "SVENY01", -1, 77.89e9)
    path = f.rates_path(ge, days, yields)
    assert math.isclose(path.pnl.sum(), 77.89e9 * 0.0040, rel_tol=1e-12)
    assert path.pnl.sum() > 0.0, "a pay-fixed hedge on floating debt gains when the yield rises"

    euro = _leg("currency", "EUR", 1, 1e9)
    quotes = [1.10, 1.21]
    assert math.isclose(f.currency_path(euro, days[:2], quotes).pnl[0], -1e9 * math.log(1.21 / 1.10))
    yen = _leg("currency", "JPY", 1, 1e9)
    weaker = f.currency_path(yen, days[:2], [110.0, 121.0]).pnl[0]
    assert math.isclose(weaker, 1e9 * math.log(121.0 / 110.0)) and weaker > 0.0

    xom = _leg("crude", "WTI_C2", -1, 1_000.0, settle=50.0)  # 20 barrels, long
    c1 = [48.0, 49.0, 51.0, 52.0]
    c2 = [50.0, 50.5, 53.0, 54.0]
    rolled = [False, False, True, False]
    crude = f.crude_path(xom, days[:4], c1, c2, rolled)
    assert np.allclose(crude.pnl, [20 * 0.5, 20 * (51.0 - 50.5), 20 * 1.0])
    naive = 20 * (53.0 - 50.5)
    assert not math.isclose(crude.pnl[1], naive)
    returns = f.crude_returns(c1, c2, rolled)
    assert np.allclose(returns, [math.log(50.5 / 50.0), math.log(51.0 / 50.5), math.log(54.0 / 53.0)])

    unheld = f.crude_path(xom, days[:4], [48.0, -37.63, 51.0, 52.0], c2, rolled)
    assert not unheld.refused.any(), "a negative contract 1 the hedge does not hold refuses nothing"
    bad = f.crude_path(xom, days[:4], c1, [50.0, 50.5, -1.0, 54.0], [False] * 4)
    assert list(bad.refused) == [False, True, True]
    assert np.isnan(bad.pnl[1:]).all() and np.isnan(f.crude_returns(c1, [50.0, 50.5, -1.0, 54.0], [False] * 4)[1:]).all()


# --------------------------------------------------------------------------------------------
# C203: the path and its peak drawdown
# --------------------------------------------------------------------------------------------


def test_c203_the_path_counts_changes_inside_the_window_and_sums_legs_by_date() -> None:
    """C203. DD214. A change counts iff both of its sessions lie in the window; two legs on different
    calendars sum by date; roll costs come off the path; a refused change is counted, not summed; and
    the peak drawdown is `worst_fall` of the path.

    **Mutation:** a window opening one session earlier takes in the change that straddled it.
    """
    days = [date(2020, 1, 31), date(2020, 2, 3), date(2020, 2, 4), date(2020, 2, 5)]
    one = f._path(days, np.array([5.0, -3.0, -4.0]))
    other = f._path([days[1], days[3]], np.array([1.0]), cost=np.array([0.5]))
    window = f.WINDOWS["NBER_2020"]
    path = f.window_path([one, other], window)
    assert path.days == (days[2], days[3])
    assert np.allclose(path.pnl, [-3.0, -4.0 + 1.0 - 0.5])
    assert path.rolls == 1 and path.cost == 0.5 and path.refused == 0
    assert path.peak_drawdown == worst_fall(path.pnl) == 6.5

    earlier = OosWindow(date(2020, 1, 31), window.end)
    assert f.window_path([one, other], earlier).days[0] == days[1]

    refused = f.LegPath(one.starts, one.ends, one.pnl, np.array([False, True, False]), np.zeros(3))
    assert f.window_path([refused], window).refused == 1


# --------------------------------------------------------------------------------------------
# C204: the options beside
# --------------------------------------------------------------------------------------------


def test_c204_the_options_are_bought_at_the_money_on_the_roll_calendar_and_lose_no_more_than_paid() -> None:
    """C204. DD216. Options roll on 2014-12-24's six-month calendar, bought on the first session on or
    after each date; `NBER_2020` holds no purchase and `RATES_2022` holds two; each is struck at the
    money and pays in the losing direction; the book never loses more than it paid; the EWMA the
    marks read is D8's on every prefix; and the Fed's share of marks is counted on mapped legs only.

    **Mutation:** a roll calendar started two months later puts a purchase inside `NBER_2020`.
    """
    assert f.roll_dates(date(2019, 12, 24), date(2020, 6, 24))[:2] == [date(2019, 12, 24), date(2020, 6, 24)]
    days = _weekdays(date(2019, 1, 1), date(2023, 3, 31))
    rng = np.random.default_rng(1)
    level = np.cumsum(np.r_[0.0, rng.standard_normal(len(days) - 1) * 0.02])
    ewma = np.r_[np.nan, f.ewma_path(np.diff(level))]
    changes = np.diff(level)
    for i in (5, 200, 900):
        assert math.isclose(ewma[i + 1], ewma_volatility(changes[: i + 1]), rel_tol=1e-12)

    xom = _leg("crude", "WTI_C2", -1, 1e9, settle=50.0)
    scale = np.full(len(days), xom.barrels * 50.0)
    options = f.option_path(xom, days, level, ewma, scale)
    purchases = sorted(options.premiums)
    assert date(2019, 12, 24) in purchases and date(2020, 6, 24) in purchases
    assert not [d for d in purchases if f.WINDOWS["NBER_2020"].start <= d <= f.WINDOWS["NBER_2020"].end]
    in_2022 = [d for d in purchases if d.year == 2022]
    assert in_2022 == [date(2022, 6, 24), date(2022, 12, 26)]
    assert f.option_window([(xom, options)], f.WINDOWS["NBER_2020"], set()).premium == 0.0
    window_2022 = f.option_window([(xom, options)], f.WINDOWS["RATES_2022"], set())
    assert math.isclose(window_2022.premium, options.premiums[in_2022[0]] + options.premiums[in_2022[1]])
    assert options.pnl.sum() >= -sum(options.premiums.values())

    i = days.index(date(2022, 6, 24))
    tau = (date(2022, 12, 24) - days[i]).days / 365.0
    atm = math.erf(ewma[i] * math.sqrt(tau) / (2.0 * math.sqrt(2.0)))  # Black-76 at F = K = 1
    assert math.isclose(options.premiums[days[i]] / scale[i], atm, rel_tol=1e-12)
    assert xom.exposure.protective is Payoff.CALL
    assert _leg("currency", "EUR", 1, 1.0).exposure.protective is Payoff.PUT
    assert _leg("rates", "SVENY01", -1, 1.0).exposure.protective is Payoff.CALL

    window = f.WINDOWS["NBER_2020"]
    calendar = [f.add_months(f.CONSTRUCTION, f.ROLL_MONTHS * k) for k in range(12)]
    shifted = [f.add_months(f.CONSTRUCTION, 2 + f.ROLL_MONTHS * k) for k in range(12)]
    assert not any(window.start <= d <= window.end for d in calendar)
    assert any(window.start <= d <= window.end for d in shifted)

    releases = ImpliedReleases({"oil": (np.array([date(2022, 6, 20).toordinal()]), np.array([0.5]))})
    vols, fed = f.leg_vols(xom, days, ewma, releases)
    assert fed[days.index(date(2022, 6, 24))] and not fed[days.index(date(2022, 7, 1))]
    priced = f.option_path(xom, days, level, vols, scale, fed)
    mapped = f.option_window([(xom, priced)], f.WINDOWS["RATES_2022"], {"WTI_C2"})
    assert 0.0 < mapped.implied_fraction < 0.05
    assert f.option_window([(xom, priced)], f.WINDOWS["RATES_2022"], set()).implied_fraction is None


# --------------------------------------------------------------------------------------------
# C205: trailing operating cash flow
# --------------------------------------------------------------------------------------------


def _fact(concept: str, filed: str, accn: str, start: str, end: str, val: float, form: str = "10-K") -> dict:
    return {"concept": concept, "form": form, "filed": filed, "accn": accn, "start": start, "end": end, "val": val}


def test_c205_trailing_cash_flow_is_the_latest_10k_before_the_window_by_rule() -> None:
    """C205. DD215. The latest filing whose form is exactly 10-K, dated before the window's first day,
    found among every concept's facts; in it, the latest fiscal-year fact of §6.1's concept, else of
    the continuing-operations concept; never an earlier 10-K; and a refusal names why. ExxonMobil's
    FY2013 10-K, as its instance tags it, reads $44.914bn under the second concept.

    **Mutation:** the continuing-operations fact removed refuses ExxonMobil instead of falling back to
    the FY2012 10-K that carries §6.1's concept.
    """
    plain, continuing = f.OCF_CONCEPTS
    facts = [
        _fact(plain, "2019-02-26", "a18", "2016-01-01", "2016-12-31", 10.0),
        _fact(plain, "2019-02-26", "a18", "2018-01-01", "2018-12-31", 30.0),
        _fact(plain, "2019-02-26", "a18", "2018-10-01", "2018-12-31", 9.0),
        _fact(plain, "2019-03-01", "b18", "2018-01-01", "2018-12-31", 99.0, form="10-K/A"),
        _fact(plain, "2020-02-26", "a19", "2019-01-01", "2019-12-31", 40.0),
    ]
    read = f.trailing_ocf(facts, date(2020, 2, 1))
    assert (read.value, read.filed, read.concept, read.fy_end, read.refused) == (30.0, "2019-02-26", plain, "2018-12-31", "")
    assert f.trailing_ocf(facts, date(2014, 1, 1)).refused.startswith("no 10-K filed before")

    xom = [
        _fact(plain, "2013-02-27", "0000034088-13-000011", "2012-01-01", "2012-12-31", 56_170_000_000.0),
        _fact("Assets", "2014-02-26", "0000034088-14-000012", "", "2013-12-31", 1.0),
        _fact(continuing, "2014-02-26", "0000034088-14-000012", "2013-01-01", "2013-12-31", XOM_FY2013_OCF),
        _fact(continuing, "2014-02-26", "0000034088-14-000012", "2012-01-01", "2012-12-31", 56_170_000_000.0),
    ]
    read = f.trailing_ocf(xom, date(2014, 12, 25))
    assert (read.value, read.concept, read.fy_end) == (XOM_FY2013_OCF, continuing, "2013-12-31")

    stripped = [x for x in xom if x["concept"] != continuing]
    refused = f.trailing_ocf(stripped, date(2014, 12, 25))
    assert refused.value is None and refused.filed == "2014-02-26" and "carries neither" in refused.refused

    negative = [_fact(plain, "2019-02-26", "a18", "2018-01-01", "2018-12-31", -5.0)]
    assert "not positive" in f.trailing_ocf(negative, date(2020, 2, 1)).refused


# --------------------------------------------------------------------------------------------
# C206: the scorers and the fixture
# --------------------------------------------------------------------------------------------


def _row(rank: int, window: str, drawdown: float | None, ocf: float | None, refused: str = "") -> f.FundingRow:
    return f.FundingRow(rank, str(rank), window, 60, 2, drawdown, 0, 0.0, ocf, "2019-02-26",
                        f.OCF_CONCEPTS[0], "2018-12-31", refused, 1.0, 0.5, None, "EWMA")


def test_c206_h16_passes_on_one_client_window_and_h15_is_refused_by_name(tmp_path) -> None:
    """C206. DD217. H16 reads exactly the six case-client verdict windows; one drawdown above a
    quarter of trailing cash flow passes it, a refusal counts as not exceeding, exactly a quarter
    does not count, and six refusals are `NOT_PERFORMED`. The DEV windows are never read. H15 is
    `NOT_PERFORMED` for DD180's reason, and its rule scores synthetic firms as §6.1 wrote it. The
    fixture round-trips through DD219's columns and refuses any others.

    **Mutation:** a missing client-window raises rather than scoring five.
    """
    rows = [_row(rank, window, 1.0, 10.0) for rank in (1, 2, 3) for window in f.VERDICT_WINDOWS]
    assert f.h16(rows).verdict is Verdict.FAIL
    rows[0] = _row(1, "NBER_2020", 2.5, 10.0)
    assert f.h16(rows).verdict is Verdict.FAIL, "exactly a quarter does not exceed it"
    rows[3] = _row(2, "RATES_2022", 2.6, 10.0)
    result = f.h16(rows)
    assert (result.verdict, result.counted, result.evaluable) == (Verdict.PASS, 1, 6)
    dev = [_row(1, "NBER_2007", 99.0, 1.0)]
    assert f.h16([r if r.window != "RATES_2022" or r.cohort_rank != 2 else _row(2, "RATES_2022", 1.0, 10.0)
                  for r in rows] + dev).verdict is Verdict.FAIL
    refused = [replace(r, refused="no 10-K filed before 2020-02-01") for r in rows]
    assert f.h16(refused).verdict is Verdict.NOT_PERFORMED
    assert f.h16(refused[:5] + [rows[5]]).verdict is Verdict.FAIL
    with pytest.raises(ValueError):
        f.h16(rows[:5])

    none = f.h15_refused()
    assert none.verdict is Verdict.NOT_PERFORMED and none.reason.startswith("DD180")
    counts = f.h15([(0.6, 0.2), (0.6, 0.35), (-0.1, -0.5), (0.4, 0.1), (0.5, 0.2)])
    assert (counts.counted, counts.firms, counts.verdict) == (3, 5, Verdict.PASS)
    assert f.h15([(0.6, 0.2), (0.6, 0.35), (-0.1, -0.5)]).verdict is Verdict.FAIL
    assert [c.scorer for c in CLAIMS if c.claim_id in ("H15", "H16")] == ["D22", "D22"]

    path = tmp_path / "d22_funding_oos_x.csv"
    lines = [",".join(f.COLUMNS)] + [",".join(f.row_cells(r, date(2025, 12, 31)).values()) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert f.load_funding(path) == tuple(rows)
    path.write_text("\n".join([",".join(f.COLUMNS) + ",price"] + [line + ",1" for line in lines[1:]]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError):
        f.load_funding(path)


# --------------------------------------------------------------------------------------------
# C207: the registration, and what H16 can show before the read
# --------------------------------------------------------------------------------------------


def test_c207_d22s_rules_are_registered_and_h16_is_close_to_decided_before_the_read() -> None:
    """C207. §11, DD212-DD219, and DD218 (X15, X16). The rules are in the registration as written,
    D22 is still registered and not landed, and DD218's arithmetic holds from committed figures:
    ExxonMobil's stated crude purchases are 5.4 times its FY2013 operating cash flow, a hedge of them
    crosses a quarter of it on a 4.6% move, and at a crude volatility of 10% a year, about DEV's
    lowest, a driftless path of `RATES_2022`'s length crosses it 98% of the time or more. AT&T's
    $20m cannot cross its threshold at any volatility on the ladder.

    **Mutation:** the flattering-direction sentence removed from DD215 is reported.
    """
    section = _flat(_section_11())

    def missing(body: str) -> list[str]:
        return [phrase for phrase in FIXED if phrase not in body]

    assert not missing(section), missing(section)
    flattering = "**So this reading moves H16 toward its predicted PASS, the flattering direction.**"
    assert missing(section.replace(flattering, "")) == [flattering]
    text = _read(REGISTRATION)
    # D22 is still registered: before the read the whole document was, and since the read of
    # 2026-09-28 its status line registers D22 alone (DD172), D12, D14 and D15 having landed.
    header = text.split("\n## 0.")[0]
    # Registered until its read; landed 2026-09-28, section 14, with the rules above unchanged.
    assert "**Status: LANDED 2026-09-28.**" in header
    assert closed("D22", REGISTRATION.parent)
    for prediction in ("D22-P1", "D22-P2", "D22-P3", "D22-P4"):
        assert f"| {prediction} |" in _section_11(), prediction

    stated = {(e.cohort_rank, e.cls): e for e in load_stated(STATED)}
    crude = stated[(2, "crude")]
    assert round(crude.amount_usd / XOM_FY2013_OCF, 1) == 5.4
    assert round(f.DRAWDOWN_SHARE * XOM_FY2013_OCF / crude.amount_usd, 3) == 0.046
    threshold = f.DRAWDOWN_SHARE * XOM_FY2013_OCF
    at_dev_low = [f.crossing_probability([f.dollar_sd(crude, 0.10)], threshold, n) for n in (61, 250)]
    assert np.allclose(at_dev_low, [0.5515, 0.98335], rtol=0.0, atol=1e-12), at_dev_low
    att = stated[(3, "rates")]
    assert f.crossing_probability([f.dollar_sd(att, 0.01)], f.DRAWDOWN_SHARE * 34.796e9, 250) == 0.0


#: The file D22's read wrote, named here as the tests name the record's (DD240).
RECORD_RESULT = FIXTURES / "d22_funding_oos_20260928.csv"


def test_c221_d22s_read_is_the_registers() -> None:
    """C221. The joint registration §14, DD240. D22's read of 2026-09-28: the file dated as a result of
    the record, the six verdict client-windows, both verdicts, and `CLAIMS` holding the same.

    **Mutation:** with GE's and ExxonMobil's drawdowns set to exactly a quarter of their cash flow,
    AT&T's $20m cannot carry an existence claim, and H16 fails.
    """
    rows = f.load_funding(RECORD_RESULT)
    with open(RECORD_RESULT, newline="", encoding="utf-8") as handle:
        header = next(csv.reader(handle))
        dates = {line[0] for line in csv.reader(handle)}
    assert header[0] == "oos_end_date" and dates == {"2025-12-31"}
    assert not [c for c in header if any(word in c for word in ("price", "settle", "barrel", "quantity", "level"))]

    ratio = {(r.cohort_rank, r.window): r.ratio for r in rows if r.window in f.VERDICT_WINDOWS}
    expected = {
        (1, "NBER_2020"): 0.6214,
        (1, "RATES_2022"): 4.0421,
        (2, "NBER_2020"): 5.4118,
        (2, "RATES_2022"): 11.9555,
        (3, "NBER_2020"): 0.0,
        (3, "RATES_2022"): 0.0,
    }
    assert set(ratio) == set(expected)
    for key, value in expected.items():
        assert ratio[key] == pytest.approx(value, abs=5e-5), key

    result = f.h16(rows)
    assert (result.verdict, result.counted, result.evaluable) == (Verdict.PASS, 4, 6)
    assert f.h15_refused().verdict is Verdict.NOT_PERFORMED
    register = {c.claim_id: c.verdict for c in CLAIMS}
    assert register["H16"] is Verdict.PASS and register["H15"] is Verdict.NOT_PERFORMED
    concepts = {r.ocf_concept for r in rows if r.window in f.VERDICT_WINDOWS}
    assert concepts == {f.OCF_CONCEPTS[0]}, "D22-P3: the fallback concept was never read in a verdict window"
    assert all(r.implied_basis.startswith("not performed") for r in rows), "DD216, not performed by name"

    quarter = [
        replace(r, peak_drawdown=0.25 * r.ocf_usd) if r.cohort_rank in (1, 2) and r.window in f.VERDICT_WINDOWS else r
        for r in rows
    ]
    assert f.h16(quarter).verdict is Verdict.FAIL
