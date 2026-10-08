"""D21, the end-to-end hedge backtest. Registered before either half existed (DD199) and landed on
its read of 2026-09-29 (§13 of its registration, C223). The scorers are held on cases whose answer
is known, the registration is held against drift, and the read is held to the register.

What could be wrong before the read was a rule edited after a number was seen, a table the document
publishes that its own code does not produce, or a scorer that does not do what §5 says. After it,
C223 adds the one more thing that can drift: a verdict that no longer follows from its file.
"""

from __future__ import annotations

import csv
import math
import re
from dataclasses import replace
from datetime import date, timedelta

import numpy as np
import pytest

from deskcraft.effectiveness import (
    ALTERNATIVES,
    GAP_COLUMNS,
    GAP_WINDOWS,
    H12A_CAPTURE,
    IMPLIED_MARKETS,
    IMPLIED_STALE_DAYS,
    MIN_OOS_WEEKS,
    REFUSED,
    STRUCTURES,
    TENOR_WEEKS,
    VERDICT_END,
    ImpliedUnreadable,
    InSample,
    Replayed,
    after_the_read_basis,
    captures,
    ederington,
    h12a,
    h12a_implied,
    h14,
    implied_releases,
    implied_releases_after_the_read,
    implied_rows,
    implied_rows_after_the_read,
    load_in_sample,
    load_replayed,
    null_decay,
    null_r2_threshold,
    ratio_beside,
    refused,
    strike,
    structure_pnl,
    verdict_weeks,
    window_weeks,
    worst_fall,
)
from deskcraft.hedging import RATIO, Exposure, Payoff, Side, Unsuitable
from deskcraft.registers import CLAIMS, Verdict
from deskcraft.scenarios import REPLAY_WINDOWS
from deskcraft.window import OOS_END, OOS_START, OosWindow
from test_deskcraft_boundary import REPO_ROOT, _read
from test_guards_and_registers import REGISTERED_DOCUMENTS, REGISTERED_MARKER, closed

DOCS = REPO_ROOT / "docs"
PRECOMMIT = DOCS / "PRECOMMIT_deskcraft_d21_hedge_backtest.md"
FIXTURES = REPO_ROOT / "tests" / "fixtures"

#: D17's in-sample half, and the file D21's read wrote (DD202, DD240): named here as the tests name
#: the record's.
IN_SAMPLE = FIXTURES / "d17_measured_dev_20260926.csv"
RECORD_RESULT = FIXTURES / "d21_replayed_oos_20260929.csv"

#: What the registration fixes, as it spells each rule. A phrase dropped or reworded turns this red:
#: the rules are frozen until the package lands, and then the landing commit edits the status line
#: and nothing above it.
FIXED = (
    "**DD199 — D21 reads the out-of-sample record, so it registers before the first read, in its own",
    "**amended, not repealed**",
    "**five** readers and **both** registration documents by name",
    "**k·N_leg on every leg**, one scalar per firm",
    "**never re-estimated**",
    "**the in-sample effectiveness is exactly the regression's R²**",
    "1 − Var(MV_T·r_t − k·E_t) / Var(MV_T·r_t)",
    "**It can be negative**",
    "**min(k, 1)**",
    "**[2015-01-01, 2024-04-05]**",
    "**every firm's verdict window ends there**",
    "**100** out-of-sample weekly returns",
    "**21 days**",
    "**fetched again**",
    "**effectiveness_OOS < 0.5**",
    "**effectiveness_OOS < ½ × R²_in**",
    "**Each passes iff at least 70% of the evaluable firms count.**",
    "block **4 weeks**, 10,000 resamples, seed **20260926**",
    "**0.0148** at n = 261",
    "**wholly above zero**",
    "**2:1 ratio forward is not an alternative**",
    "**26th**",
    "**182** days",
    "**Volatility: EWMA, λ 0.94, D8's normalised weights**",
    "**times 1.0**",
    "**VR_forward ≥ 0.9 × VR_best**",
    "**VR_forward ≥ VR_best**",
    "**PASS iff at least half the eligible firms count.**",
    "**Fewer than five eligible firms, and H12a is `NOT_PERFORMED`**",
    "**100% of the stated exposure**",
    "**before D22 builds**",
    "**Never a price, never MV_T, never a weekly series.**",
    "**X15** — discharged",
    "**X7** — discharged",
)


def _flat(text: str) -> str:
    """A rule wraps across lines, and inside a quoted block each line starts with `>`."""
    return " ".join(line.lstrip("> ").strip() for line in text.splitlines())


def test_c186_d21_is_registered_with_its_rules_fixed() -> None:
    """C186. DD199-DD206. D21's rules exist before either half does, and it has not landed.

    The document must carry the registered marker, be one of C158's declared documents, leave D21
    unclosed (so H12a, H14a and H14b stay unscored under C34), and hold every rule §2-§7 fix.

    **Mutation:** the same check over the text with the verdict window's end moved.
    """
    text = _read(PRECOMMIT)
    # Registered until its read; landed 2026-09-29, section 13, with every rule above it unchanged.
    header = text.split("\n## 0.")[0]
    if not RECORD_RESULT.exists():
        assert REGISTERED_MARKER in header
        assert PRECOMMIT.name in REGISTERED_DOCUMENTS
        assert not closed("D21", DOCS), "D21 counted as landed while neither half has run"
        for claim in CLAIMS:
            if claim.scorer == "D21" and claim.claim_id != "H14":
                assert claim.verdict is None, f"{claim.claim_id} carries a verdict before D21 has read"
    else:
        assert "**Status: LANDED 2026-09-29.**" in header and REGISTERED_MARKER not in header
        assert PRECOMMIT.name not in REGISTERED_DOCUMENTS, "a landed document still declared registered"
        assert closed("D21", DOCS)
        for claim in CLAIMS:
            if claim.scorer == "D21" and claim.claim_id != "H14":
                assert claim.verdict is not None, f"{claim.claim_id} unscored after D21's read"

    flat = _flat(text)

    def missing(body: str) -> list[str]:
        return [phrase for phrase in FIXED if phrase not in body]

    assert not missing(flat), missing(flat)
    moved = flat.replace("**[2015-01-01, 2024-04-05]**", "**[2015-01-01, 2025-12-31]**")
    assert missing(moved) == ["**[2015-01-01, 2024-04-05]**"]
    # The window the rule names is one the type admits, and its end is the constant that runs.
    OosWindow(OOS_START, VERDICT_END)


def _table(text: str, heading: str) -> list[list[str]]:
    """The body rows of the first markdown table after `heading`, as cells."""
    after = text[text.index(heading) :]
    block = []
    for line in after.splitlines()[1:]:
        if line.startswith("|"):
            block.append(line)
        elif block:
            break
    assert block, heading
    return [[cell.strip().strip("*") for cell in line.strip("|").split("|")] for line in block[2:]]


def test_c187_the_published_null_tables_are_what_the_code_produces() -> None:
    """C187. §6. Every cell of Tables A and A2 recomputed at the stated seed and replications.

    A power table typed into a document is an assertion; one the suite recomputes is a measurement
    anyone can repeat. The in-sample null threshold §5 quotes is recomputed with them.

    **Mutation:** a cell altered in the text is reported.
    """
    text = _read(PRECOMMIT)
    assert round(null_r2_threshold(261), 4) == 0.0148

    cache: dict[tuple[float, float, float], tuple[float, float, float]] = {}

    def null(r2: float, v: float, d: float = 1.0) -> tuple[float, float, float]:
        if (r2, v, d) not in cache:
            cache[(r2, v, d)] = null_decay(r2, 261, 482, v, decay=d)
        return cache[(r2, v, d)]

    def disagreements(body: str) -> list[str]:
        out = []
        for cells in _table(body, "**Table A. H14 under no true decay.**"):
            r2 = float(cells[0])
            lo = [null(r2, v) for v in (0.5, 1.0, 2.0, 4.0, 8.0)]
            expected = [lo[0][0]] + [row[1] for row in lo[:4]] + [row[2] for row in lo]
            for stated, value in zip(cells[1:], expected):
                if stated != f"{value:.3f}":
                    out.append(f"A r2={r2}: {stated} vs {value:.3f}")
        for cells in _table(body, "**Table A2. H14b's power**"):
            r2 = float(cells[0])
            for stated, d in zip(cells[1:], (1.0, 0.75, 0.5, 0.25, 0.0)):
                value = null(r2, 1.0, d)[2]
                if stated != f"{value:.3f}":
                    out.append(f"A2 r2={r2} d={d}: {stated} vs {value:.3f}")
        return out

    assert not disagreements(text), disagreements(text)
    altered = text.replace("| 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | **0.744**", "| 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | **0.700**")
    assert disagreements(altered) == ["A r2=0.0: 0.700 vs 0.744"]


# ---------------------------------------------------------------------------
# The scorers, on rows whose answer is known (§5)
# ---------------------------------------------------------------------------


def _in(rank: int, r2: float | None, k: float = 0.5, lo: float = -1.0, n: int = 261) -> InSample:
    fitted = r2 is not None
    return InSample(rank, f"cik{rank}", k if fitted else None, lo if fitted else None, k + 1.0 if fitted else None, n if fitted else None, r2, "" if fitted else "x")


def _out(rank: int, eff: float | None, n: int = 482, **vr: float) -> Replayed:
    reduction = {name: vr.get(name.split()[0]) for name in STRUCTURES}
    return Replayed(rank, f"cik{rank}", n, eff, None, None, reduction, "")


def test_c188_h14_counts_and_the_beside_numbers() -> None:
    """C188. DD203. H14a below one half, H14b below half of in-sample; exactly 70% passes and one
    fewer fails; a firm without a fit or with under 100 weeks moves only the bounds; H14b ⊆ H14a;
    the in-sample shadow and the resolved subset are counted.

    **Mutation:** the same rows with one H14b firm's decay removed fail H14b and not H14a.
    """
    ins = tuple(
        [_in(i, 0.01) for i in range(1, 8)]  # seven noise-level fits
        + [_in(8, 0.30), _in(9, 0.30), _in(10, 0.60)]
        + [_in(11, None), _in(12, 0.2)]
    )
    outs = tuple(
        [_out(i, -0.01) for i in range(1, 8)]  # each below half of 0.01: H14a and H14b
        + [_out(8, 0.20), _out(9, 0.40), _out(10, 0.55)]  # 8, 9 in H14a only; 10 in neither
        + [_out(11, 0.0), _out(12, 0.0, n=MIN_OOS_WEEKS - 1)]
    )
    result = h14(ins, outs, cohort_size=40)
    assert result.evaluable == 10
    assert (result.level.counted, result.decay.counted) == (9, 7)
    assert result.level.verdict is Verdict.PASS and result.decay.verdict is Verdict.PASS
    assert result.weak_not_decaying == 2
    assert result.level_in_sample == 9, "the in-sample shadow: nine of ten fits are already below 1/2"
    assert result.resolved == 3 and result.decay_resolved == 0
    assert result.bounds_decay == (7 / 40, 37 / 40)
    assert math.isclose(result.median_out, -0.01)
    assert math.isclose(result.median_ratio, -1.0), "seven of ten firms kept minus their whole R²"

    fewer = tuple(_out(1, 0.009) if r.cohort_rank == 1 else r for r in outs)
    mutated = h14(ins, fewer)
    assert mutated.decay.counted == 6 and mutated.decay.verdict is Verdict.FAIL
    assert mutated.level.verdict is Verdict.PASS

    # H14b ⊆ H14a on any rows at all: in-sample R² is at most one.
    rng = np.random.default_rng(0)
    for _ in range(200):
        r2, eff = float(rng.uniform(0, 1)), float(rng.uniform(-1, 1))
        if eff < 0.5 * r2:
            assert eff < 0.5


def test_c189_h12a_compares_the_forward_with_the_best_admitted_alternative() -> None:
    """C189. DD204. Only resolved firms are eligible; the ratio forward is never an alternative;
    90% of a positive reduction counts, and where none is positive the forward must do no worse;
    exactly half passes; fewer than five eligible firms is `NOT_PERFORMED`, never FAIL.

    **Mutation:** one counting firm's forward reduced below 90% turns PASS to FAIL.
    """
    assert "2:1 ratio forward" not in ALTERNATIVES and STRUCTURES[0] == "forward"
    assert captures(0.9, 1.0) and not captures(0.89, 1.0)
    assert captures(-0.2, -0.2) and not captures(-0.3, -0.2)

    resolved = [_in(i, 0.2, k=0.6, lo=0.1) for i in range(1, 7)] + [_in(7, 0.2, k=0.6, lo=-0.1)]
    outs = [
        _out(1, 0.1, forward=0.20, bought=0.10, **{"zero-cost": 0.12, "participating": 0.15}),
        _out(2, 0.1, forward=0.19, bought=0.10, **{"zero-cost": 0.20, "participating": 0.15}),
        _out(3, 0.1, forward=0.10, bought=0.20, **{"zero-cost": 0.12, "participating": 0.15}),
        _out(4, 0.1, forward=-0.30, bought=-0.10, **{"zero-cost": -0.20, "participating": -0.15}),
        _out(5, 0.1, forward=-0.10, bought=-0.30, **{"zero-cost": -0.20, "participating": -0.15}),
        _out(6, 0.1, forward=0.05, bought=0.30, **{"zero-cost": 0.12, "participating": 0.15}),
        _out(7, 0.1, forward=0.90, bought=0.10, **{"zero-cost": 0.12, "participating": 0.15}),
    ]
    result = h12a(tuple(resolved), tuple(outs))
    assert result.eligible == 6, "firm 7's k interval reaches zero, so it is not eligible"
    assert result.counted == 3 and result.verdict is Verdict.PASS  # firms 1, 2 and 5: exactly half
    assert result.nothing_to_capture == 2
    assert result.best_by_name == {"bought option": 3, "zero-cost collar": 1, "participating forward": 2}

    mutated = list(outs)
    mutated[1] = _out(2, 0.1, forward=0.17, bought=0.10, **{"zero-cost": 0.20, "participating": 0.15})
    assert h12a(tuple(resolved), tuple(mutated)).verdict is Verdict.FAIL
    assert h12a(tuple(resolved[:4]), tuple(outs)).verdict is Verdict.NOT_PERFORMED


# ---------------------------------------------------------------------------
# The structure engine (DD200, DD204)
# ---------------------------------------------------------------------------


def _path(n: int, seed: int, weekly: float) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    return np.concatenate([[0.0], np.cumsum(rng.standard_normal(n - 1) * weekly)]), np.arange(n) * 7.0


def test_c190_the_engine_is_the_loop_d17_and_d18_describe() -> None:
    """C190. DD200, DD204. The forward is D17's linear leg exactly; in sample, Ederington's measure
    at the least-squares ratio is the regression's R²; every struck structure passes D18's gate and
    one sized above the stated exposure is refused; a zero-cost structure is worth nothing when
    struck, so a period's P&L sums to its payoff; the protective structure gains when the firm
    loses; the verdict weeks start inside the out-of-sample record.

    **Mutation:** a structure struck at 1.2 of the exposure raises `Unsuitable`.
    """
    euro = Exposure(1, "c", "currency", "EUR", 1, 2.0e9)
    debt = Exposure(2, "c", "rates", "SVENY01", -1, 5.0e10)
    levels, days = _path(TENOR_WEEKS * 2 + 5, 1, 0.10 / math.sqrt(52.0))
    vols = np.full(len(levels), 0.10)

    forward = structure_pnl("forward", euro, levels, days, vols, 0.7)
    assert np.array_equal(forward, -0.7 * euro.amount_usd * euro.sign * np.diff(levels))

    # DD200's identity, on a sample with an intercept.
    rng = np.random.default_rng(2)
    x = rng.standard_normal(261)
    y = 0.4 * x + rng.standard_normal(261) + 3.0
    xc = x - x.mean()
    k = float(xc @ (y - y.mean()) / (xc @ xc))
    assert math.isclose(ederington(y, -k * x), float(np.corrcoef(x, y)[0, 1] ** 2), rel_tol=1e-12)

    for name in STRUCTURES:
        legs = strike(name, euro, 1.0, 0.10, 0.5, 1.0)
        assert all(leg.multiple <= 1.0 for leg in legs)
    # A bought option obliges nothing and a participating forward sells half, so only these two
    # can oblige more than the exposure when sized above it.
    for name in ("forward", "zero-cost collar"):
        with pytest.raises(Unsuitable):
            strike(name, euro, 1.0, 0.10, 0.5, 1.2)

    # Zero cost: a period's weekly P&L sums to its payoff, since nothing was paid to strike it.
    period = slice(0, TENOR_WEEKS)
    for name in ("zero-cost collar", "participating forward"):
        pnl = structure_pnl(name, euro, levels, days, vols, 1.0)
        legs = strike(name, euro, 1.0, 0.10, 182 / 365.0, 1.0)
        spot = math.exp(levels[TENOR_WEEKS] - levels[0])
        payoff = 0.0
        for leg in legs:
            intrinsic = max(spot - leg.strike, 0.0) if leg.payoff is Payoff.CALL else max(leg.strike - spot, 0.0)
            payoff += (1.0 if leg.side is Side.BOUGHT else -1.0) * leg.multiple * intrinsic
        assert math.isclose(pnl[period].sum(), payoff * euro.amount_usd, rel_tol=1e-9, abs_tol=1e-3)

    # Direction: each structure's P&L moves against the firm's own exposure P&L.
    exposure_pnl = euro.amount_usd * euro.sign * np.diff(levels)
    for name in STRUCTURES:
        assert np.corrcoef(structure_pnl(name, euro, levels, days, vols, 1.0), exposure_pnl)[0, 1] < -0.5, name
    yields = 0.01 + _path(len(levels), 3, 0.0007)[0]
    rate_pnl = debt.amount_usd * debt.sign * np.diff(yields)
    for name in STRUCTURES:
        pnl = structure_pnl(name, debt, yields, days, np.full(len(yields), 0.5), 1.0)
        assert np.corrcoef(pnl, rate_pnl)[0, 1] < -0.5, name

    from datetime import date, timedelta

    fridays = [date(2014, 12, 19) + timedelta(days=7 * i) for i in range(500)]
    weeks = verdict_weeks(fridays)
    assert fridays[weeks[0]] == date(2015, 1, 2) and fridays[weeks[-1]] <= VERDICT_END
    assert fridays[weeks[-1] + 1] > VERDICT_END


def test_c190b_d21s_three_claims_are_the_registers() -> None:
    """C190b. DD206. D21 adds no claim and moves none: the three it scores keep their predicted
    PASS, H14 stays withdrawn with its two successors, and the H12a capture share is 90%."""
    by_id = {claim.claim_id: claim for claim in CLAIMS}
    for claim_id in ("H12a", "H14a", "H14b"):
        assert by_id[claim_id].scorer == "D21" and by_id[claim_id].predicted is Verdict.PASS
    assert by_id["H14"].successors == ("H14a", "H14b")
    assert H12A_CAPTURE == 0.9
    assert re.search(r"≥ 90%", by_id["H12a"].statement.replace(">=", "≥"))


# ---------------------------------------------------------------------------
# §12: two numbers beside the verdicts (DD210, DD211)
# ---------------------------------------------------------------------------

ADMISSION = DOCS / "OWNER_ADMISSION_d22_results_only_routes.md"

#: §12 as it spells each rule, held as `FIXED` holds §2-§7.
FIXED_BESIDE = (
    "**DD210 — H12a's structures are marked a second time at the Minneapolis Fed's implied volatility, beside the verdict and never in it.**",
    "**`SVENY01`, `CAD`, `CHF`, `CNY` and `MXN` are not mapped and stay on EWMA**",
    "**σ = sd / √½**",
    "**The latest release on or before the observation date, and no more than 10 days before it**",
    "**the sensitivity is `NOT_PERFORMED` and says why; it never falls back silently**",
    "**If a mapped market's median `sd` over the rows kept exceeds 1, that market's `sd` is read as percent and divided by 100**",
    "**H12a's count, median capture and winners are reported again on these, beside the verdict. The verdict is DD204's, on EWMA, and this does not move it.**",
    "**Never a volatility.**",
    "**D22 takes the same mapping.**",
    "**DD211 — the refused 2:1 ratio forward is marked on the record's path, beside H12a, with no pass or fail.**",
    "**At 100% of the stated exposure its worst state obliges twice the exposure, so D18's gate refuses it on every firm.**",
    "**the largest fall from a running peak that starts at zero, per dollar of stated exposure**",
    "**Variance reduction cannot see the obligation.**",
)

#: The columns §12 appends after DD202's, in order: DD210's, then DD211's.
APPENDED = (
    "vr_bought_option_implied",
    "vr_zero_cost_collar_implied",
    "vr_participating_forward_implied",
    "implied_fraction",
    "implied_basis",
    "vr_ratio_forward",
    "vr_ratio_forward_stated",
    "ratio_gap",
    "ratio_gap_2020",
    "ratio_gap_2022",
)

#: DD202 item 3's columns, in its order.
DD202_COLUMNS = (
    "oos_end_date", "cohort_rank", "cik", "n", "effectiveness", "eff_lo", "eff_hi", "multiple",
    "vr_forward", "vr_bought_option", "vr_zero_cost_collar", "vr_participating_forward",
    "effectiveness_to_2025",
    "vr_forward_stated", "vr_bought_option_stated", "vr_zero_cost_collar_stated", "vr_participating_forward_stated",
    "drop_reason",
)


def _section_12() -> str:
    text = _read(PRECOMMIT)
    return text[text.index("## 12. Two numbers beside the verdicts") :]


def _mapping(section: str) -> dict[str, str]:
    """DD210 item 2's table, as factor to market."""
    out = {}
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.lstrip("> ").strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0].startswith("`") and cells[1].startswith("`"):
            out[cells[0].strip("`")] = cells[1].split("`")[1]
    return out


def test_c195_the_two_beside_numbers_are_fixed_before_the_read() -> None:
    """C195. DD210, DD211. §12 fixes both beside numbers before any row exists: for DD210 the
    mapping, the conversion, the release rule, the reading rule and what leaves; for DD211 the
    structure, the measure and what leaves. The mapping table is the code's, every appended column
    is named, the four predictions are written, and no claim is added.

    **Mutation:** the release window moved to 14 days, and `oil` mapped to another market, are each
    reported.
    """
    section = _section_12()
    flat = _flat(section)

    def missing(body: str) -> list[str]:
        return [phrase for phrase in FIXED_BESIDE if phrase not in body]

    assert not missing(flat), missing(flat)
    assert missing(flat.replace("no more than 10 days", "no more than 14 days")) == [FIXED_BESIDE[3]]
    assert IMPLIED_STALE_DAYS == 10
    assert _mapping(section) == IMPLIED_MARKETS
    assert _mapping(section.replace("`oil` (WTI", "`gold` (WTI")) != IMPLIED_MARKETS
    for column in APPENDED:
        assert f"`{column}`" in section, column
    for prediction in ("P7", "P8", "P9", "P10"):
        assert f"| {prediction} |" in section, prediction
    assert sorted(c.claim_id for c in CLAIMS if c.scorer == "D21") == ["H12a", "H14", "H14a", "H14b"]


def test_c196_the_route_is_extended_in_writing_and_d22_takes_the_mapping() -> None:
    """C196. DD210 items 6 and 11, and the admission's §7. The Minneapolis Fed's route reaches D21
    only through a dated record that quotes what was put and what the owner said, says the owner
    may refuse it, and drops rows on arrival. The joint registration's §6.1 row and DD176 carry the
    mapping in place, and the rule C170 pins in that row is intact.

    **Mutation:** the admission's §7 without its refusal clause is reported.
    """
    admission = _read(ADMISSION)
    section = _flat(admission[admission.index("## 7. One later decision on the Minneapolis Fed's route") :])
    told = "**the owner is told so and may say otherwise**"

    def missing(body: str) -> list[str]:
        required = (
            "you'd extend that admission to D21",
            '*"please compelete this one by one"*',
            "**The Minneapolis Fed's option-implied distributions may be read at D21's own read and "
            "computed on for D21's DD210, on the terms of §1: never committed, only statistics reported.**",
            "Every row dated after 2025-12-31, and every market DD210 does not map, is dropped on arrival",
            told,
            "**Nothing from the Fed is read before the authorisation**",
        )
        return [phrase for phrase in required if phrase not in body]

    assert not missing(section), missing(section)
    assert missing(section.replace(told, "")) == [told]
    assert OOS_END.isoformat() == "2025-12-31"

    registration = _flat(_read(sorted(DOCS.glob("PRECOMMIT_deskcraft_d12_d14_d15_d22*.md"))[0]))
    for phrase in (
        "**An ordered list, and the first source available on the day decides.**",
        "mapped 2026-09-28 by D21's DD210, which this row lacked",
        "source (1) only if the Minneapolis Fed publishes crude oil *(it does, as `oil`; mapped "
        "2026-09-28 by D21's DD210)*",
    ):
        assert phrase in registration, phrase


def _mpd(*rows: str, header: str = "idt,market,maturity_target,mu,sd") -> str:
    """An invented statistics file in the columns the data dictionary names."""
    return "\n".join((header, *rows)) + "\n"


def test_c197_the_feds_file_is_read_by_the_rule_or_not_at_all() -> None:
    """C197. DD210 items 3 to 6. The date and market columns are found by what they hold, not by a
    name guessed before the file is seen; rows past the record's end and every unmapped market are
    dropped before anything is kept; a file the rule cannot read raises instead of falling back; an
    `sd` that is not finite or not positive refuses its row; a market whose median `sd` exceeds one
    is in percent; σ = sd / √½; and a release is used for ten days and no longer.

    **Mutation:** a release eleven days old is not used.
    """
    text = _mpd(
        "2014-12-26 00:00:00,euro,6,0,0.05",
        "1/2/2015,euro,6,0,0.06",
        "2026-01-02,euro,6,0,0.07",
        "2015-01-02,pound,6,0,4.0",
        "2015-01-09,pound,6,0,6.0",
        "2015-01-02,yen,6,0,nan",
        "2015-01-09,yen,6,0,0",
        "2015-01-16,yen,6,0,0.04",
        "2015-01-02,oil,6,0,0.30",
        "2015-01-09,oil,6,0,1.40",
        "2015-01-16,oil,6,0,0.35",
        "2015-01-02,sp6m,6,0,0.10",
        "2015-01-02,tr10yr,6,0,0.02",
    )
    rows = implied_rows(text, OOS_END)
    assert len(rows) == 10, "the 2026 row and both unmapped markets are dropped on arrival"
    assert {row["market"] for row in rows} == set(IMPLIED_MARKETS.values())
    assert all(row["date"] <= OOS_END.isoformat() for row in rows)
    assert set(rows[0]) == {"date", "market", "sd"}, "only what item 6 keeps"
    assert [rows[0]["date"], rows[1]["date"]] == ["2014-12-26", "2015-01-02"]

    releases = implied_releases(rows)
    assert releases.percent == ("pound",), "a median of 5 is percent; oil's one value above 1 is not"
    assert releases.refused == 2
    root = math.sqrt(0.5)
    assert releases.volatility("EUR", date(2015, 1, 2)) == 0.06 / root
    assert math.isclose(releases.volatility("GBP", date(2015, 1, 12)), 0.06 / root, rel_tol=1e-15)
    assert releases.volatility("WTI_C2", date(2015, 1, 12)) == 1.40 / root
    assert releases.volatility("JPY", date(2015, 1, 9)) is None, "a refused row is not a release"
    assert releases.volatility("EUR", date(2014, 12, 25)) is None, "before the first release"
    for instrument in ("SVENY01", "CAD", "CHF", "CNY", "MXN"):
        assert releases.volatility(instrument, date(2015, 1, 2)) is None, instrument
    last = date(2015, 1, 16)
    assert releases.volatility("WTI_C2", last + timedelta(days=IMPLIED_STALE_DAYS)) == 0.35 / root
    assert releases.volatility("WTI_C2", last + timedelta(days=IMPLIED_STALE_DAYS + 1)) is None, "the mutation"
    assert "read as percent: pound" in releases.basis and "rows refused: 2" in releases.basis

    four = ("2015-01-02,euro,6,0,0.05", "2015-01-02,pound,6,0,0.05", "2015-01-02,yen,6,0,0.05")
    unreadable = {
        "no rows": _mpd(),
        "two date columns": _mpd(*(r.replace(",6,", ",2015-07-02,") for r in four), "2015-01-02,oil,2015-07-02,0,0.05"),
        "one value not a date": _mpd(*four, "Jan 2 2015,oil,6,0,0.05"),
        "a market missing": _mpd(*four),
        "no sd column": _mpd(*four, "2015-01-02,oil,6,0,0.05", header="idt,market,maturity_target,mu,stdev"),
    }
    for why, bad in unreadable.items():
        with pytest.raises(ImpliedUnreadable):
            implied_rows(bad, OOS_END)
            pytest.fail(why)
    twice = implied_rows(_mpd(*four, four[0], "2015-01-02,oil,6,0,0.05"), OOS_END)
    with pytest.raises(ImpliedUnreadable, match="two rows"):
        implied_releases(twice)


def _implied(out: Replayed, fraction: float | None, **vr: float) -> Replayed:
    """`out` with DD210's columns: its own EWMA numbers unless one is given."""
    values = {name: vr.get(name.split()[0], out.reduction[name]) for name in ALTERNATIVES}
    return replace(out, reduction_implied=values, implied_fraction=fraction, implied_basis="Minneapolis Fed sd / sqrt(0.5)")


def test_c198_the_implied_comparison_is_beside_h12a_and_moves_no_verdict(tmp_path) -> None:
    """C198. DD210 items 7 to 9. `h12a_implied` takes H12a's firms, rule and tie-break, reads the
    alternatives from the implied columns and the forward from DD204's, and carries no verdict.
    Given the EWMA numbers again it reproduces H12a's count; a changed implied number moves that
    firm's count and not H12a's verdict. `load_replayed` reads the appended columns, and a file
    written before them.

    **Mutation:** one firm's implied participating forward raised beyond the forward's reach moves
    that firm and no other.
    """
    resolved = tuple(_in(i, 0.2, k=0.6, lo=0.1) for i in range(1, 7))
    ewma = [
        _out(1, 0.1, forward=0.20, bought=0.10, **{"zero-cost": 0.12, "participating": 0.15}),
        _out(2, 0.1, forward=0.19, bought=0.10, **{"zero-cost": 0.20, "participating": 0.15}),
        _out(3, 0.1, forward=0.10, bought=0.20, **{"zero-cost": 0.12, "participating": 0.15}),
        _out(4, 0.1, forward=-0.30, bought=-0.10, **{"zero-cost": -0.20, "participating": -0.15}),
        _out(5, 0.1, forward=-0.10, bought=-0.30, **{"zero-cost": -0.20, "participating": -0.15}),
        _out(6, 0.1, forward=0.05, bought=0.30, **{"zero-cost": 0.12, "participating": 0.15}),
    ]
    same = tuple(_implied(out, 0.9 if out.cohort_rank <= 4 else None) for out in ewma)
    verdict = h12a(resolved, same)
    beside = h12a_implied(resolved, same)
    assert not hasattr(beside, "verdict"), "a beside number carries no verdict"
    assert beside.basis.startswith("Minneapolis Fed")
    assert (beside.firms, beside.mapped) == (6, 4)
    assert beside.counted == (verdict.counted, verdict.counted) == (3, 3) and beside.moved == ()
    assert beside.best_by_name == verdict.best_by_name
    assert beside.median_capture_mapped[0] == beside.median_capture_mapped[1]
    assert math.isclose(beside.median_capture_mapped[0], 0.95), "firm 4 has nothing to capture"
    assert beside.median_fraction == 0.9

    moved = (_implied(ewma[0], 0.9, participating=0.25),) + same[1:]
    shifted = h12a_implied(resolved, moved)
    assert shifted.moved == (1,) and shifted.counted == (3, 2), "the mutation"
    assert h12a(resolved, moved) == verdict, "H12a reads DD204's columns only"

    row = {name: "" for name in DD202_COLUMNS + APPENDED}
    row.update(oos_end_date="2024-04-05", cohort_rank="1", cik="cik1", n="480", effectiveness="0.1", drop_reason="")
    row.update({f"vr_{name}": "0.2" for name in ("forward", "bought_option", "zero_cost_collar", "participating_forward")})
    row.update(vr_participating_forward_implied="0.25", vr_bought_option_implied="0.1", vr_zero_cost_collar_implied="0.1")
    row.update(implied_fraction="0.75", implied_basis="Minneapolis Fed sd / sqrt(0.5)", vr_ratio_forward="0.3", ratio_gap="0.04", ratio_gap_2022="0.02")
    with_columns, without = tmp_path / "with.csv", tmp_path / "without.csv"
    for path, columns in ((with_columns, DD202_COLUMNS + APPENDED), (without, DD202_COLUMNS)):
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerow(row)
    (read,) = load_replayed(with_columns)
    assert read.reduction_implied["participating forward"] == 0.25 and read.implied_fraction == 0.75
    assert read.ratio_reduction == 0.3 and read.ratio_reduction_stated is None and read.ratio_gap == 0.04
    assert read.ratio_gap_window == {"NBER_2020": None, "RATES_2022": 0.02}
    (old,) = load_replayed(without)
    assert old.reduction == read.reduction and old.implied_basis == "" and old.ratio_gap is None
    assert all(value is None for value in old.reduction_implied.values())


def test_c199_the_refused_ratio_forward_is_marked_beside_and_never_admitted() -> None:
    """C199. DD211. The ratio forward is DD193's, one protective bought and two opposite sold at the
    one strike where it costs nothing, returned without the gate so it can be marked, and never an
    alternative. At the stated exposure the gate refuses it on a rate, a currency and a crude leg.
    Its period's P&L sums to its payoff. On a firm whose value moves twice its stated exposure,
    variance reduction scores it above the forward while its P&L falls behind the forward's: what
    item 3 says variance cannot see. The worst fall, the window weeks and `ratio_beside` are the
    arithmetic item 2 states.

    **Mutation:** sized at one half, its leverage is exactly one and the gate admits it, so the
    refusal is the leverage and not the name.
    """
    assert REFUSED not in STRUCTURES
    euro = Exposure(1, "c", "currency", "EUR", 1, 2.0e9)
    debt = Exposure(2, "c", "rates", "SVENY01", -1, 5.0e10)
    crude = Exposure(3, "c", "crude", "WTI_C2", -1, 1.0e9)
    for exposure, vol in ((euro, 0.10), (debt, 0.5), (crude, 0.35)):
        legs = strike(REFUSED, exposure, 1.0, vol, 0.5, 1.0)
        bought, sold = legs
        assert (bought.side, bought.multiple, sold.side, sold.multiple) == (Side.BOUGHT, 1.0, Side.SOLD, RATIO)
        assert (bought.payoff, sold.payoff) == (exposure.protective, exposure.opposite)
        assert bought.strike == sold.strike
        assert refused(exposure, legs), exposure.instrument
        assert not refused(exposure, strike(REFUSED, exposure, 1.0, vol, 0.5, 0.5)), "the mutation"
    for name in STRUCTURES:
        assert not refused(euro, strike(name, euro, 1.0, 0.10, 0.5, 1.0)), name

    levels, days = _path(TENOR_WEEKS * 8 + 1, 5, 0.10 / math.sqrt(52.0))
    vols = np.full(len(levels), 0.10)
    ratio = structure_pnl(REFUSED, euro, levels, days, vols, 1.0)
    legs = strike(REFUSED, euro, 1.0, 0.10, 182 / 365.0, 1.0)
    spot = math.exp(levels[TENOR_WEEKS] - levels[0])
    payoff = sum(
        (1.0 if leg.side is Side.BOUGHT else -1.0)
        * leg.multiple
        * (max(spot - leg.strike, 0.0) if leg.payoff is Payoff.CALL else max(leg.strike - spot, 0.0))
        for leg in legs
    )
    assert math.isclose(ratio[:TENOR_WEEKS].sum(), payoff * euro.amount_usd, rel_tol=1e-9, abs_tol=1e-3)

    forward = structure_pnl("forward", euro, levels, days, vols, 1.0)
    exposure_pnl = euro.amount_usd * euro.sign * np.diff(levels)
    noise = np.random.default_rng(6).standard_normal(len(exposure_pnl)) * exposure_pnl.std()
    firm = 2.0 * exposure_pnl + noise
    assert ederington(firm, ratio) > ederington(firm, forward)
    assert worst_fall(ratio - forward) > 0.0

    assert worst_fall(np.array([1.0, -3.0, 2.0, -1.0, 0.5])) == 3.0
    assert worst_fall(np.array([1.0, 2.0])) == 0.0 == worst_fall(np.array([]))
    assert worst_fall(np.array([-1.0, -2.0])) == 3.0, "the peak starts at zero"

    by_name = {w.name: w.window for w in REPLAY_WINDOWS}
    assert set(GAP_WINDOWS) == set(GAP_COLUMNS) == {"NBER_2020", "RATES_2022"}
    assert all(GAP_WINDOWS[name] == by_name[name] for name in GAP_WINDOWS)
    fridays = [date(2019, 12, 27) + timedelta(days=7 * i) for i in range(160)]
    weeks = window_weeks(fridays, GAP_WINDOWS["NBER_2020"])
    assert fridays[weeks[0]] == date(2020, 2, 7) and fridays[weeks[-1] + 1] == date(2020, 4, 24)
    assert weeks == list(range(weeks[0], weeks[-1] + 1))

    vr = {"bought": 0.1, "zero-cost": 0.1, "participating": 0.1}
    ins = (_in(1, 0.2, k=1.8, lo=0.1), _in(2, 0.2, k=0.4, lo=0.1), _in(3, 0.2, k=5.0, lo=0.1), _in(4, 0.01))
    outs = (
        replace(_out(1, 0.1, forward=0.20, **vr), ratio_reduction=0.25, ratio_gap=0.08, ratio_gap_window={"NBER_2020": 0.02, "RATES_2022": 0.05}),
        replace(_out(2, 0.1, forward=0.20, **vr), ratio_reduction=0.10, ratio_gap=0.01, ratio_gap_window={"NBER_2020": None, "RATES_2022": 0.01}),
        replace(_out(3, 0.1, forward=0.20, **vr), ratio_reduction=0.15, ratio_gap=0.30, ratio_gap_window={"NBER_2020": 0.12, "RATES_2022": 0.02}),
        replace(_out(4, -0.1), ratio_gap=0.0),
    )
    result = ratio_beside(ins, outs)
    assert not hasattr(result, "verdict")
    assert (result.firms, result.largest_gap, result.largest_rank) == (4, 0.30, 3)
    assert math.isclose(result.median_gap, 0.045)
    assert result.windows["NBER_2020"][0::2] == (2, 0.12) and result.windows["NBER_2020"][3] == 3
    assert result.windows["RATES_2022"][3] == 1
    assert result.ahead_k_above_one == (1, 2) and result.ahead_k_at_most_one == (0, 1)


def test_c223_d21s_read_is_the_registers() -> None:
    """C223. §13. D21's read of 2026-09-29: the file dated as a result of the record and carrying no
    price, the counts behind H14a, H14b and H12a, the three verdicts, and `CLAIMS` holding the same.
    DD210's comparison is not performed, by name, on every row.

    **Mutation:** with two more rates-only firms' effectiveness set below half their in-sample R²,
    H14b clears 70% and passes; and with Chevron's forward set to 0.85 of its best alternative, H12a
    still passes, six of seven, because the verdict is the median's threshold.
    """
    ins = load_in_sample(IN_SAMPLE)
    outs = load_replayed(RECORD_RESULT)
    with open(RECORD_RESULT, newline="", encoding="utf-8") as handle:
        header = next(csv.reader(handle))
        dates = {line[0] for line in csv.reader(handle)}
    assert tuple(header) == DD202_COLUMNS + APPENDED and dates == {"2024-04-05"}
    assert not [c for c in header if any(word in c for word in ("price", "settle", "barrel", "market_value", "mv_t"))]
    assert len(outs) == 40

    result = h14(ins, outs)
    assert result.evaluable == 32
    assert (result.level.counted, result.level.verdict) == (32, Verdict.PASS)
    assert (result.decay.counted, result.decay.verdict) == (21, Verdict.FAIL)
    assert result.level_in_sample == 32, "H14a's in-sample shadow: decided before 2015 (DD232)"
    assert (result.resolved, result.decay_resolved, result.weak_not_decaying) == (18, 10, 11)
    assert round(result.median_in, 4) == 0.0161

    lead = h12a(ins, outs)
    assert (lead.eligible, lead.counted, lead.verdict) == (7, 7, Verdict.PASS)
    assert lead.best_by_name == {"bought option": 0, "zero-cost collar": 0, "participating forward": 7}
    assert round(lead.median_capture, 3) == 1.300

    beside = h12a_implied(ins, outs)
    assert beside.firms == 0 and beside.basis.startswith("not performed"), "DD210, not performed by name"
    assert all(out.implied_basis.startswith("not performed") for out in outs)
    ratio = ratio_beside(ins, outs)
    assert (ratio.largest_rank, round(ratio.largest_gap, 3)) == (5, 1.790), "P10: Chevron, a crude firm"
    assert ratio.ahead_k_above_one == (5, 6) and ratio.ahead_k_at_most_one == (0, 1), "P9"

    register = {c.claim_id: c.verdict for c in CLAIMS}
    assert (register["H12a"], register["H14a"], register["H14b"]) == (Verdict.PASS, Verdict.PASS, Verdict.FAIL)

    # The mutations.
    fitted = {firm.cik: firm for firm in ins}
    uncounted = [
        out for out in outs
        if out.effectiveness is not None and out.cik in fitted and fitted[out.cik].fitted
        and out.effectiveness >= 0.5 * fitted[out.cik].r2
    ]
    two = {out.cik for out in uncounted[:2]}
    moved = tuple(
        replace(out, effectiveness=0.5 * fitted[out.cik].r2 - 1e-6) if out.cik in two else out for out in outs
    )
    assert h14(ins, moved).decay.verdict is Verdict.PASS
    chevron = next(out for out in outs if out.cohort_rank == 5)
    best = max(chevron.reduction[name] for name in ALTERNATIVES)
    thinner = tuple(
        replace(out, reduction={**out.reduction, "forward": 0.85 * best}) if out.cohort_rank == 5 else out
        for out in outs
    )
    assert (h12a(ins, thinner).counted, h12a(ins, thinner).verdict) == (6, Verdict.PASS)


#: The three lines the Fed's file opened with at both reads: two sentences and a blank (DD243).
_PREAMBLE = (
    '"The data below are statistics for Market-Based Probability Densities (MPDs) generated by '
    'the Federal Reserve Bank of Minneapolis."',
    '"Data Definitions can be found in the data dictionary CSV file."',
    '""',
)
_FED_HEADER = '"market","idt","maturity_target","mu","sd"'


def test_c224_the_feds_file_after_the_read_reads_past_its_preamble_and_its_horizon() -> None:
    """C224. DD243, written 2026-09-29 after the read by the owner's decision, before any `sd` of
    the Fed's file was read. Two corrections, and only two.

    **Item 1, the preamble.** The header is the first line whose fields include `sd`. The registered
    reader still refuses the file with a preamble exactly as it did at both reads, and on a file
    with no preamble the two readers keep the same rows: DD243 adds a skip and nothing else.

    **Item 2, the horizon.** `maturity_target` is the Fed's *"time-to-expiry target for options
    selection"*, in months. DD210's σ = sd / √½ assumed six, and a shape probe found three on most
    rows, where √½ understates the annual figure by √2. So σ = sd / √(m/12) at each row's own
    target, a six-month row lands exactly where DD210 put it, and a target that is not a positive
    number refuses its row and is counted.

    **Mutation:** a file whose header has no `sd` finds no header at all, and says so.
    """
    rows = (
        "euro,2015-01-02,3,0,0.05",
        "pound,2015-01-02,6,0,0.05",
        "yen,2015-01-02,NA,0,0.05",
        "oil,2015-01-02,3,0,0.20",
        "oil,2015-01-09,6,0,0.20",
        "sp6m,2015-01-02,3,0,0.10",
        "euro,2026-01-02,3,0,0.05",
    )
    plain = "\n".join((_FED_HEADER, *rows)) + "\n"
    fed = "\n".join((*_PREAMBLE, plain))

    with pytest.raises(ImpliedUnreadable, match="0 columns whose every value is a date"):
        implied_rows(fed, OOS_END)  # the registered reader, as it refused at both reads

    read = implied_rows_after_the_read(fed, OOS_END)
    assert [(r["market"], r["date"], r["maturity_target"]) for r in read] == [
        ("euro", "2015-01-02", "3"),
        ("pound", "2015-01-02", "6"),
        ("yen", "2015-01-02", "NA"),
        ("oil", "2015-01-02", "3"),
        ("oil", "2015-01-09", "6"),
    ], "the unmapped market and the 2026 row are dropped on arrival, as DD210 item 6 drops them"
    stripped = [{k: v for k, v in r.items() if k != "maturity_target"} for r in read]
    assert stripped == implied_rows(plain, OOS_END), "on a file with no preamble, nothing else differs"
    assert implied_rows_after_the_read(plain, OOS_END) == read

    releases = implied_releases_after_the_read(read)
    assert releases.refused == 1, "the NA target"
    assert releases.volatility("JPY", date(2015, 1, 2)) is None
    assert math.isclose(releases.volatility("EUR", date(2015, 1, 2)), 0.05 / math.sqrt(3 / 12), rel_tol=1e-15)
    assert math.isclose(releases.volatility("EUR", date(2015, 1, 2)), 2 * 0.05, rel_tol=1e-15)
    six = implied_releases(stripped).volatility("GBP", date(2015, 1, 2))
    assert math.isclose(releases.volatility("GBP", date(2015, 1, 2)), six, rel_tol=1e-15), "six months: DD210's σ"
    assert math.isclose(releases.volatility("WTI_C2", date(2015, 1, 2)), 0.40, rel_tol=1e-15)
    assert math.isclose(releases.volatility("WTI_C2", date(2015, 1, 9)), 0.20 / math.sqrt(0.5), rel_tol=1e-15)
    basis = after_the_read_basis(releases)
    assert basis.startswith("after the read (DD243): Minneapolis Fed sd / sqrt(m/12)"), basis
    assert "rows refused: 1" in basis

    with pytest.raises(ImpliedUnreadable, match="no line whose fields include sd"):
        implied_rows_after_the_read(fed.replace('"sd"', '"stdev"'), OOS_END)

    d21 = _read(REPO_ROOT / "docs" / "PRECOMMIT_deskcraft_d21_hedge_backtest.md")
    section = d21.split("\n## 14.")[1]
    assert "**DD243" in section and "before any `sd`" in section


#: What D21's section 14.2 reports beside H12a after the read: (firms, mapped, counted on EWMA and
#: on the Fed's volatility, ranks moved), and the winners on the Fed's volatility.
REPORTED_BESIDE_H12A = (7, 4, (7, 7), ())
REPORTED_WINNERS = {"bought option": 0, "zero-cost collar": 0, "participating forward": 7}

#: DD243 item 5. The two files the post-read run wrote, each beside the landed file it must
#: reproduce outside the columns the Fed's volatility may move.
AFTER_THE_READ = {
    FIXTURES / "d21_implied_after_the_read_oos_20260929.csv": (
        RECORD_RESULT,
        frozenset({*(f"vr_{name.replace(' ', '_').replace('-', '_')}_implied" for name in ALTERNATIVES), "implied_fraction", "implied_basis"}),
    ),
    FIXTURES / "d22_implied_after_the_read_oos_20260929.csv": (
        FIXTURES / "d22_funding_oos_20260928.csv",
        frozenset({"option_premium", "option_worst_fall", "implied_fraction", "implied_basis"}),
    ),
}


def _csv_rows(path) -> tuple[list[str], list[dict[str, str]]]:
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def moved_outside(new: list[dict[str, str]], landed: list[dict[str, str]], beside: frozenset[str]) -> list[str]:
    """Every cell of `landed` outside `beside` that `new` does not reproduce, by row and column."""
    return [
        f"row {i} {column}"
        for i, (a, b) in enumerate(zip(new, landed, strict=True), start=1)
        for column in b
        if column not in beside and a[column] != b[column]
    ]


def test_c225_after_the_read_moves_only_what_the_feds_volatility_prices() -> None:
    """C225. DD243 items 4 to 6, D21 §14.2. The two files written after the read, by the owner's
    decision, sit beside the landed ones and never in their place. Each reproduces its landed file in
    every column the Fed's volatility cannot reach, cell for cell. Each says on every row that it was
    read after the read. What §14.2 reports beside H12a is what the D21 file gives, and the verdicts
    stand as scored.

    **Mutation:** one landed cell outside the implied columns, changed in a copy, is found.
    """
    for new, (landed, beside) in AFTER_THE_READ.items():
        new_columns, new_rows = _csv_rows(new)
        landed_columns, landed_rows = _csv_rows(landed)
        assert new_columns == landed_columns and len(new_rows) == len(landed_rows), new.name
        assert not moved_outside(new_rows, landed_rows, beside), (new.name, moved_outside(new_rows, landed_rows, beside))
        assert all(row["implied_basis"].startswith("after the read (DD243)") for row in new_rows), new.name
        assert all(not row["implied_basis"].startswith("after the read") for row in landed_rows), landed.name

        column = next(c for c in landed_columns if c not in beside and c not in ("oos_end_date", "cik"))
        altered = [dict(row) for row in new_rows]
        altered[-1][column] = altered[-1][column] + "1"
        assert moved_outside(altered, landed_rows, beside) == [f"row {len(new_rows)} {column}"], "the mutation"

    fed = h12a_implied(load_in_sample(IN_SAMPLE), load_replayed(next(iter(AFTER_THE_READ))))
    assert (fed.firms, fed.mapped, fed.counted, fed.moved) == REPORTED_BESIDE_H12A, fed
    assert fed.best_by_name == REPORTED_WINNERS, fed.best_by_name
    for claim, verdict in (("H12a", Verdict.PASS), ("H14a", Verdict.PASS), ("H14b", Verdict.FAIL)):
        assert next(c for c in CLAIMS if c.claim_id == claim).verdict is verdict, claim

    section = _read(REPO_ROOT / "docs" / "PRECOMMIT_deskcraft_d21_hedge_backtest.md").split("\n## 14.")[1]
    assert "### 14.2" in section and "after the read" in section
