"""D17, the exposure extractor. Landed 2026-09-27: H11 PASS and H17 FAIL on the equity denominator.

C173 still holds every rule the registration fixed, because a rule edited after an exposure was
read is the defect research §9.2 exists to prevent. C192-C194 hold what the run produced: the
verdicts, the fixture's shape, and the reach of the defect found after the read (DD208).
"""

from __future__ import annotations

import csv
import math
from collections import Counter
from dataclasses import replace
from pathlib import Path

from deskcraft.exposure import ALL, CASH, EQUITY, OVERHEDGE, Measured, clopper_pearson, h11, h17, load_measured, ratio
from deskcraft.registers import CLAIMS, Verdict
from test_deskcraft_boundary import REPO_ROOT, _read
from test_guards_and_registers import REGISTERED_DOCUMENTS, REGISTERED_MARKER, closed

DOCS = REPO_ROOT / "docs"
PRECOMMIT = DOCS / "PRECOMMIT_deskcraft_d17_exposure_extractor.md"

#: What the registration fixes, as it spells each rule. A phrase dropped or reworded turns this red,
#: which is the point: the rules are frozen until the package lands, and then the landing commit
#: edits the status line and nothing above it.
FIXED = (
    "**Forty firms, by rule.**",
    "**Filter (iii) is skipped** (DD180)",
    "**DD183 — \"disclosed\" in H11 and in §6.1 means the figures the 10-K tags",
    "**the hedge covers the next twelve months of the stated flow.**",
    "F_net = V + max(CP, STB) + FVH − CFH",
    "**DD185 — the measured exposure is k, the variance-minimising multiple of the naive hedge.**",
    "**k < 1/1.3**",
    "**1/k**",
    "**(2009-12-24, 2014-12-24]**",
    "**100** weekly returns",
    "**12** year-on-year quarters",
    "expected block **4 weeks**",
    "expected block **4 quarters**",
    "**Pass iff the ratio is in [0.35, 1.30]**",
    "**every row dated after 2014-12-24 is discarded before anything is written or computed**",
    "**PASS iff at least 70% of the evaluable firms count.**",
    "**above 2.0**",
    "**below 1.5**",
    "**A half with fewer than five evaluable units is refused, and H17 is then `NOT_PERFORMED`.**",
    "seed **20260926**",
    "**X2** — discharged:",
    "**X21** — discharged:",
)


def test_c173_d17_landed_with_its_rules_unedited() -> None:
    """C173. DD181-DD189. D17's rules were fixed before any exposure existed, and landing edited
    none of them.

    Registered 2026-09-26 and landed 2026-09-27. The document now carries the landed status line and
    not the registered marker, has left C158's declared set, and closes D17 (so C34 requires H11
    and H17 scored), and it still holds every rule §2-§5 fixed.

    **Mutation:** the same check over the text with the window's closing date moved.
    """
    text = _read(PRECOMMIT)
    assert REGISTERED_MARKER not in text and "**Status: LANDED 2026-09-27.**" in text
    # A rule wraps across lines, and inside a quoted block each line starts with `>`.
    text = " ".join(line.lstrip("> ").strip() for line in text.splitlines())
    assert PRECOMMIT.name not in REGISTERED_DOCUMENTS
    assert closed("D17", DOCS), "D17's verdicts exist and the package does not count as landed"

    def missing(body: str) -> list[str]:
        return [phrase for phrase in FIXED if phrase not in body]

    assert not missing(text), missing(text)
    moved = text.replace("**(2009-12-24, 2014-12-24]**", "**(2009-12-24, 2014-12-31]**")
    assert missing(moved) == ["**(2009-12-24, 2014-12-24]**"]


# ---------------------------------------------------------------------------
# The scorers, built ahead of the fixtures (§5), on rows whose answer is known
# ---------------------------------------------------------------------------

def _row(rank: int, k: float | None, cls: str = ALL, denominator: str = EQUITY) -> Measured:
    lo = None if k is None else k - 0.1
    hi = None if k is None else k + 0.1
    return Measured(rank, f"cik{rank}", denominator, cls, k, lo, hi, None if k is None else 261, "" if k else "x")


def test_c174_h11_counts_k_below_one_over_one_point_three() -> None:
    """C174. §5's H11. k <= 0 counts; a firm without k is not evaluable and moves only the bounds;
    exactly 70% passes and one firm fewer fails; the other denominator is never read.

    **Mutation:** the same rows with one counting firm's k raised above 1/1.3 fail.
    """
    assert ratio(0.5) == 2.0 and math.isinf(ratio(0.0)) and math.isinf(ratio(-0.2))
    rows = tuple(
        [_row(i, 0.2) for i in range(1, 6)]
        + [_row(6, -0.4), _row(7, 0.0)]
        + [_row(i, 1.1) for i in range(8, 11)]
        + [_row(11, None), _row(12, 5.0, denominator=CASH)]
    )
    result = h11(rows, cohort_size=40)
    assert (result.evaluable, result.counted, result.share) == (10, 7, 0.7)
    assert result.verdict is Verdict.PASS
    assert (result.bound_low, result.bound_high) == (7 / 40, 37 / 40)
    assert result.resolved_below == 7 and result.resolved_above == 3
    mutated = tuple(_row(1, 0.9) if r.cohort_rank == 1 else r for r in rows)
    assert h11(mutated).verdict is Verdict.FAIL
    assert h11((_row(1, None),)).verdict is Verdict.NOT_PERFORMED


def test_c175_h17_pools_currency_and_crude_and_refuses_a_thin_half() -> None:
    """C175. §5's H17. The first half pools every currency and crude unit, reading k <= 0 as +∞;
    the second half is the rates firms; both must hold; fewer than five units refuses the claim.

    **Mutation:** with four rates firms instead of five, H17 is `NOT_PERFORMED`, never FAIL.
    """
    first = [_row(i, 0.25, "currency") for i in range(1, 4)] + [_row(4, -1.0, "crude"), _row(5, 0.8, "crude")]
    second = [_row(i, 1.0, "rates") for i in range(10, 15)]
    result = h17(tuple(first + second))
    assert result.first.units == 5 and result.first.median_ratio == 4.0 and result.first.holds
    assert result.second.median_ratio == 1.0 and result.second.holds
    assert result.verdict is Verdict.PASS
    assert result.by_class["crude"].units == 2 and result.by_class["crude"].holds is None
    thin = h17(tuple(first + second[:4]))
    assert thin.second.holds is None and thin.verdict is Verdict.NOT_PERFORMED
    backwards = h17(tuple(first + [_row(i, 0.5, "rates") for i in range(10, 15)]))
    assert backwards.verdict is Verdict.FAIL


def test_c176_clopper_pearson_reproduces_a1s_table() -> None:
    """C176. `AMENDMENT_A1` §5.5's exact intervals at n = 40, to its three decimals.

    **Mutation:** 33 of 40 does not exclude 0.70, and 34 is the smallest count that does.
    """
    for count, lo, hi in ((40, 0.912, 1.000), (36, 0.763, 0.972), (34, 0.702, 0.943), (32, 0.644, 0.909), (28, 0.535, 0.834), (24, 0.433, 0.751)):
        got = clopper_pearson(count, 40)
        assert (round(got[0], 3), round(got[1], 3)) == (lo, hi), (count, got)
    assert clopper_pearson(33, 40)[0] < 0.70 < clopper_pearson(34, 40)[0]


FIXTURES = REPO_ROOT / "tests" / "fixtures"
COHORT = FIXTURES / "d17_cohort_dev_20260926.csv"
STATED = FIXTURES / "d17_stated_dev_20260926.csv"


def _rows(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_c177_the_cohort_fixture_is_section_2s_walk() -> None:
    """C177. §2, DD191, DD192. The walk is contiguous from rank 1 in `Assets` order, every walked
    firm has exactly one outcome, exactly forty are the cohort, ranked 1-40 in walk order, and the
    walk stops at the fortieth. Every stated leg belongs to a cohort firm, names a class §3 defines
    and an instrument D22 holds, and nothing in either fixture is dated after 2014-12-24.

    **Mutation:** a forty-first cohort row, and a leg on a firm the walk dropped, are each reported.
    """

    def problems(cohort: list[dict], stated: list[dict]) -> list[str]:
        out = []
        ranks = [int(r["rank"]) for r in cohort]
        if ranks != list(range(1, len(ranks) + 1)):
            out.append("walk not contiguous")
        assets = [float(r["assets_usd"]) for r in cohort]
        if assets != sorted(assets, reverse=True):
            out.append("not in Assets order")
        if any(not r["outcome"] for r in cohort):
            out.append("a walked firm without an outcome")
        members = [r for r in cohort if r["outcome"] == "cohort"]
        if [int(r["cohort_rank"]) for r in members] != list(range(1, 41)):
            out.append("cohort is not ranks 1-40")
        if cohort and cohort[-1]["outcome"] != "cohort":
            out.append("walk ran past the fortieth")
        ciks = {r["cik"] for r in members}
        instruments = {"currency": {"EUR", "JPY", "GBP", "CAD", "CHF", "CNY", "MXN"}, "rates": {"SVENY01"}, "crude": {"WTI_C2"}}
        for leg in stated:
            if leg["cik"] not in ciks:
                out.append(f"a leg on {leg['cik']}, which is not in the cohort")
            if leg["instrument"] not in instruments.get(leg["class"], set()):
                out.append(f"{leg['class']}:{leg['instrument']} is not a leg §3 defines")
            if float(leg["amount_usd"]) <= 0 or leg["sign"] not in ("1", "-1"):
                out.append("a leg without a positive amount and a sign")
        dates = [r["accepted_date"] for r in cohort] + [r["fy_end_date"] for r in stated]
        if max(dates) > "2014-12-24":
            out.append("a row dated after the construction date")
        return out

    cohort, stated = _rows(COHORT), _rows(STATED)
    assert not problems(cohort, stated), problems(cohort, stated)
    extra = dict(cohort[-1], rank=str(len(cohort) + 1), cohort_rank="41", assets_usd="0")
    assert "cohort is not ranks 1-40" in problems(cohort + [extra], stated)
    dropped = next(r for r in cohort if r["outcome"] != "cohort")
    stray = dict(stated[0], cik=dropped["cik"])
    assert problems(cohort, stated + [stray]) == [f"a leg on {dropped['cik']}, which is not in the cohort"]


MEASURED_COLUMNS = [
    "construction_date", "cohort_rank", "cik", "denominator", "class", "k", "k_lo", "k_hi", "n", "r2",
    "identity_ratio", "drop_reason",
]


def test_c178_the_measured_fixture_carries_statistics_only() -> None:
    """C178. DD187 item 5. Every measured fixture holds exactly the declared statistics: no price,
    no market value, no return, since the routes they were computed from may never be committed.

    **Mutation:** a header with a `market_value` column is refused.
    """

    def refused(header: list[str]) -> list[str]:
        return [] if header == MEASURED_COLUMNS else [f"columns {header}"]

    fixtures = sorted(FIXTURES.glob("d17_measured_dev_*.csv"))
    assert fixtures, "no measured fixture"
    for path in fixtures:
        with open(path, newline="", encoding="utf-8") as handle:
            assert not refused(next(csv.reader(handle))), path.name
    assert refused(MEASURED_COLUMNS + ["market_value"])


# ---------------------------------------------------------------------------
# What the run produced (§14)
# ---------------------------------------------------------------------------

MEASURED = FIXTURES / "d17_measured_dev_20260926.csv"


def _measured() -> tuple[Measured, ...]:
    return load_measured(MEASURED)


def test_c192_the_verdicts_are_the_fixtures() -> None:
    """C192. §5, §14. H11 and H17 recompute from the committed fixture to the numbers §14 reports,
    and the claims register carries those verdicts: H11 PASS, 24 of 32; H17 FAIL, neither half
    holding. The cash-flow denominator gives the opposite verdict on both, reported beside.

    **Mutation:** one counting firm's k raised to 1.0 still passes (23 of 32 is 0.719); a second
    fails (22 of 32 is 0.688), so the verdict sits two firms from the bar.
    """
    rows = _measured()
    eleven, seventeen = h11(rows, EQUITY), h17(rows, EQUITY)
    assert (eleven.evaluable, eleven.counted, eleven.verdict) == (32, 24, Verdict.PASS)
    assert [round(x, 3) for x in eleven.share_interval] == [0.566, 0.885]
    assert round(eleven.median_k, 2) == -9.17 and (eleven.bound_low, eleven.bound_high) == (0.6, 0.8)
    assert (eleven.resolved_below, eleven.resolved_above) == (10, 6)
    assert (seventeen.first.units, round(seventeen.first.median_ratio, 2), seventeen.first.holds) == (22, 1.55, False)
    assert (seventeen.second.units, seventeen.second.median_ratio, seventeen.second.holds) == (25, math.inf, False)
    assert round(seventeen.by_class["currency"].median_ratio, 3) == 0.130
    assert seventeen.by_class["crude"].holds is True and seventeen.verdict is Verdict.FAIL
    assert h11(rows, CASH).verdict is Verdict.FAIL and h17(rows, CASH).verdict is Verdict.PASS
    register = {claim.claim_id: claim.verdict for claim in CLAIMS}
    assert (register["H11"], register["H17"]) == (Verdict.PASS, Verdict.FAIL)

    counting = [r for r in rows if r.denominator == EQUITY and r.cls == ALL and r.k is not None and r.k < OVERHEDGE]

    def raised(n: int) -> tuple[Measured, ...]:
        chosen = {r.cik for r in counting[:n]}
        return tuple(replace(r, k=1.0) if r.cik in chosen and r.denominator == EQUITY and r.cls == ALL else r for r in rows)

    assert h11(raised(1)).verdict is Verdict.PASS and h11(raised(2)).verdict is Verdict.FAIL


#: §4's drop reasons, as the measuring script writes them. A firm without k carries one of these.
DROP_REASONS = {
    "no leg",
    "no symbol active on 2014-12-24",
    "no weekly history served",
    "no public float or share count to check identity",
    "identity check failed",
    "no market value at construction",
    "fewer than 100 weekly returns",
}


def test_c193_every_cohort_firm_is_measured_or_dropped_for_a_declared_reason() -> None:
    """C193. §4, §5, DD187. The equity rows cover the cohort once each at class `all`; a row has k
    iff it has no drop reason, and every reason is one §4 declares; every k rests on at least 100
    weekly returns and an identity ratio inside [0.35, 1.30]; the tally is §14's 32 + 4 + 3 + 1.

    **Mutation:** a k on the firm whose identity ratio is 1.88 (Exelon) is reported.
    """

    def problems(rows: tuple[Measured, ...], ratios: dict[str, float | None]) -> list[str]:
        out = []
        equity = [r for r in rows if r.denominator == EQUITY]
        firms = [r.cik for r in equity if r.cls == ALL]
        if len(firms) != 40 or len(set(firms)) != 40:
            out.append("the equity rows do not cover the cohort once each")
        for r in equity:
            if (r.k is None) == (r.drop_reason == ""):
                out.append(f"{r.cik} {r.cls}: k and drop reason disagree")
            if r.drop_reason and r.drop_reason not in DROP_REASONS:
                out.append(f"{r.cik}: undeclared reason {r.drop_reason!r}")
            if r.k is not None:
                ratio_ = ratios[r.cik]
                if r.n is None or r.n < 100:
                    out.append(f"{r.cik} {r.cls}: k on fewer than 100 returns")
                if ratio_ is None or not 0.35 <= ratio_ <= 1.30:
                    out.append(f"{r.cik} {r.cls}: k without a passed identity check")
        return out

    with open(MEASURED, newline="", encoding="utf-8") as handle:
        ratios = {
            row["cik"]: float(row["identity_ratio"]) if row["identity_ratio"] else None
            for row in csv.DictReader(handle)
            if row["denominator"] == EQUITY and row["class"] == ALL
        }
    rows = _measured()
    assert not problems(rows, ratios), problems(rows, ratios)
    tally = Counter(r.drop_reason for r in rows if r.denominator == EQUITY and r.cls == ALL)
    assert tally == Counter({"": 32, "no leg": 4, "identity check failed": 3, "no symbol active on 2014-12-24": 1})
    exelon = tuple(replace(r, k=0.5, k_lo=0.4, k_hi=0.6, n=260, drop_reason="") if r.cik == "1109357" and r.denominator == EQUITY else r for r in rows)
    assert problems(exelon, ratios) == [f"1109357 {cls}: k without a passed identity check" for cls in ("all", "crude", "rates")]


#: DD208. The firm the co-registrant defect dropped, and the factor by which it inflated each kept
#: firm's share count, read from the filings' own instances.
DEFECT_DROPPED = "1166691"  # Comcast: its only leg is rates
DEFECT_SCALE = {"1004980": 1.5777, "4904": 1.1218, "92122": 1.0522}  # PG&E, AEP, Southern


def verdicts_under_every_correction(rows: tuple[Measured, ...]) -> set[tuple[Verdict, Verdict]]:
    """H11's and H17's equity verdicts over every way correcting DD208 could come out: the kept
    firms' k divided by their factor, and Comcast back in as a rates-only firm that counts or not."""
    scaled = tuple(
        replace(r, k=r.k / DEFECT_SCALE[r.cik], k_lo=r.k_lo / DEFECT_SCALE[r.cik], k_hi=r.k_hi / DEFECT_SCALE[r.cik])
        if r.cik in DEFECT_SCALE and r.denominator == EQUITY and r.k is not None
        else r
        for r in rows
    )
    out = set()
    for k in (-1.0, 1.0):
        comcast = tuple(
            Measured(10, DEFECT_DROPPED, EQUITY, cls, k, k - 0.1, k + 0.1, 260, "") for cls in (ALL, "rates")
        )
        fixed = tuple(r for r in scaled if not (r.cik == DEFECT_DROPPED and r.denominator == EQUITY)) + comcast
        out.add((h11(fixed).verdict, h17(fixed).verdict))
    return out


def test_c194_no_correction_of_the_co_registrant_defect_moves_a_verdict() -> None:
    """C194. DD208. The extractor read co-registrants' cover facts as the filer's. Every way the
    correction could come out leaves H11 PASS and H17 FAIL, which is why the fixture stays as run.

    **Mutation:** one counting firm fewer (23 of 32, still PASS as run) and the check reports that
    Comcast returning without counting would fail H11 (23 of 33).
    """
    rows = _measured()
    assert verdicts_under_every_correction(rows) == {(Verdict.PASS, Verdict.FAIL)}
    first = next(r for r in rows if r.denominator == EQUITY and r.cls == ALL and r.k is not None and r.k < OVERHEDGE)
    thinner = tuple(replace(r, k=1.0) if r.cik == first.cik and r.denominator == EQUITY and r.cls == ALL else r for r in rows)
    assert h11(thinner).verdict is Verdict.PASS
    assert verdicts_under_every_correction(thinner) == {(Verdict.PASS, Verdict.FAIL), (Verdict.FAIL, Verdict.FAIL)}
