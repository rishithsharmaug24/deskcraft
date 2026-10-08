"""The fit window and the registers. D3a, bars C30-C38.

`FitWindow` makes `PLAN_deskcraft.md` §9's first failure -- a covariance fitted on the window it
is stress-tested against -- a refusal (C30), on bounds read from curvecast rather than copied
from memory (C31).

The registers hold the plan as data, and every bar here compares that data with something it
does not control: the build order's own tables (C32, C33, C35), the documents on disk (C34),
the reference book (C36), curvecast's ledger (C37), and the test functions that citations name
(C38). A register checked only against itself is a constant that equals itself.

Parsers read the markdown tables by row shape. Each one is mutated in the bar that uses it,
against a copy of the real document with one line changed, so a parser that silently stopped
matching rows would fail its own mutation rather than pass a register over an empty table.
"""

from __future__ import annotations

import ast
import dataclasses
import re
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from deskcraft.generator import CANDIDATE_SERIES, enumerate_universe
from deskcraft.reference import DEFERRED_LEGS, REFERENCE_BOOK, US_CASH_BOOK
from deskcraft.registers import (
    CLAIMS,
    NUMBERING_GAPS,
    PACKAGE_BUDGET,
    Claim,
    ClaimStatus,
    Verdict,
    claim_number,
)
from deskcraft.sources import ADMITTED, SOURCE_ROWS, SOURCES, Derivation, Licence, OriginatorClass, Source
from deskcraft.window import (
    DEV_END,
    DEV_START,
    OOS_END,
    OOS_START,
    FitWindow,
    OosWindow,
)
from test_deskcraft_boundary import CURVECAST, REPO_ROOT, TESTS, _read, working_tree
from upstream_certificate import DEV_BOUNDS

DOCS = REPO_ROOT / "docs"
BUILD_ORDER = DOCS / "BUILD_ORDER_D3_D16.md"
AMENDMENT_A4 = DOCS / "AMENDMENT_A4_the_out_of_sample_window.md"
RIDER_A4 = DOCS / "RIDER_A4_the_date_and_two_unowned_findings.md"
DEV_PANEL = REPO_ROOT / "tests" / "fixtures" / "panel_daily_dev_20260914.csv"

_ORDER_ROW = re.compile(r"^\|\s*\*\*(D\d+[a-z]?)\*\*\s*\|")


def _section(text: str, start: str, stop: str) -> str:
    begin = text.index(start)
    return text[begin : text.index(stop, begin + len(start))]


# ---------------------------------------------------------------------------
# C30-C31: the fit window
# ---------------------------------------------------------------------------


def test_the_fit_window_refuses_what_dec1_forbids() -> None:
    """C30. B30. DD28. Past DEV, before DEV, backwards, empty, and the wrong type.

    The `datetime` legs match on the message, not on the exception type alone: comparing a
    `datetime` with a `date` raises `TypeError` by itself, so a bare `pytest.raises(TypeError)`
    would pass a guard that had no type check at all. §0.5 of the pre-commit is that trap.
    """
    whole = FitWindow(DEV_START, DEV_END)
    assert FitWindow.dev() == whole
    hash(whole)
    with pytest.raises(dataclasses.FrozenInstanceError):
        whole.end = date(2020, 3, 31)  # type: ignore[misc]

    one_day = timedelta(days=1)
    with pytest.raises(ValueError, match="reaches past DEV_END"):
        FitWindow(DEV_START, DEV_END + one_day)
    with pytest.raises(ValueError, match="before DEV_START"):
        FitWindow(DEV_START - one_day, DEV_END)
    with pytest.raises(ValueError, match="run forwards"):
        FitWindow(DEV_END, DEV_END)
    with pytest.raises(ValueError, match="run forwards"):
        FitWindow(DEV_END, DEV_START)

    with pytest.raises(TypeError, match="must be a datetime.date exactly"):
        FitWindow(datetime(1990, 1, 2), DEV_END)
    with pytest.raises(TypeError, match="must be a datetime.date exactly"):
        FitWindow(DEV_START, datetime(2014, 12, 31))
    with pytest.raises(TypeError, match="must be a datetime.date exactly"):
        FitWindow("1990-01-02", DEV_END)  # type: ignore[arg-type]

    # A crisis inside DEV is fittable; that is what the crisis-window covariance variants are.
    FitWindow(date(1998, 8, 1), date(1998, 10, 31))


def test_the_dev_bounds_are_curvecasts() -> None:
    """C31. B31. DD28. Restated here, read from curvecast's source, compared.

    Parsed rather than imported, in C9's shape: deskcraft does not import curvecast yet, and
    a guard that needs an environment to run is a guard that stops running.

    **Off-machine the comparison is against the certificate** (DD69), which is a dated
    transcription of the same two lines of `seal.py`. It is not vacuous: what it catches is
    this repository's own `DEV_START` or `DEV_END` moving, and the sample `FitWindow` bounds is
    the thing DEC-1 forecloses on.
    """
    certified = {name: date(*parts) for name, parts in DEV_BOUNDS.items()}
    assert certified == {"DEV_START": DEV_START, "DEV_END": DEV_END}, certified

    seal = CURVECAST / "src" / "curvecast" / "pit" / "seal.py"
    if not seal.exists():
        return

    found: dict[str, date] = {}
    for node in ast.parse(_read(seal)).body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in {"DEV_START", "DEV_END"}
        ):
            call = node.value
            assert isinstance(call, ast.Call) and getattr(call.func, "id", None) == "date"
            found[node.targets[0].id] = date(*(arg.value for arg in call.args))
    assert found == certified, found


# ---------------------------------------------------------------------------
# C32-C34: the claims register
# ---------------------------------------------------------------------------


def claims_table(text: str) -> dict[str, dict[str, object]]:
    """`BUILD_ORDER_D3_D16.md` §5, one entry per claim row, keyed by claim id."""
    rows: dict[str, dict[str, object]] = {}
    body = _section(text, "## 5. The hypothesis register", "D3a's claims register holds")
    for line in body.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] == "#":
            continue
        raw_id, raw_scorer, prediction = cells[0], cells[2], cells[3]
        claim_id = raw_id.strip("*~ ")
        if claim_id == "—":
            claim_id = "SCENARIO_SIGNS"
        if not raw_id.startswith("~~"):
            status = ClaimStatus.ACTIVE
        elif "annex" in prediction.lower():
            status = ClaimStatus.ANNEXED
        elif "withdrawn" in prediction.lower():
            status = ClaimStatus.WITHDRAWN
        else:
            status = None
        predicted = (
            Verdict.FAIL if "FAIL" in prediction else Verdict.PASS if "PASS" in prediction else None
        )
        rows[claim_id] = {
            "scorer": raw_scorer.strip("*~ "),
            "status": status,
            "predicted": predicted,
        }
    return rows


#: The universe a §5 row says its verdict was scored against. A verdict without one is a number
#: with no denominator: `AMENDMENT_A5` §0 row 13 puts the same eleven series at 231 structures and
#: twenty at 1,350, so the pool IS the multiple-testing surface a PASS was earned over.
_SCORED_UNIVERSE = re.compile(r"(\d+)\s+candidate series\s*/\s*(\d+)\s+structures")


def scored_universes(text: str) -> set[tuple[int, int]]:
    """Every `(series, structures)` universe §5 records a verdict as having been scored at."""
    body = _section(text, "## 5. The hypothesis register", "D3a's claims register holds")
    return {(int(pool), int(count)) for pool, count in _SCORED_UNIVERSE.findall(body)}


def register_disagreements(text: str, claims: tuple[Claim, ...]) -> list[str]:
    """Every way the register and §5 differ. Empty when they agree."""
    parsed = claims_table(text)
    register = {claim.claim_id: claim for claim in claims}
    out = []
    if len(register) != len(claims):
        out.append("a claim id appears twice in the register")
    if not parsed:
        out.append("§5 parsed to no rows")
    for missing in sorted(set(register) ^ set(parsed)):
        out.append(f"{missing} is in one of the register and §5 but not the other")
    for claim_id in sorted(set(register) & set(parsed)):
        claim, row = register[claim_id], parsed[claim_id]
        if row["scorer"] != claim.scorer:
            out.append(f"{claim_id}: §5 scorer {row['scorer']} vs register {claim.scorer}")
        if row["status"] is not claim.status:
            out.append(f"{claim_id}: §5 status {row['status']} vs register {claim.status}")
        if claim.status is ClaimStatus.ACTIVE and row["predicted"] is not claim.predicted:
            out.append(f"{claim_id}: §5 predicts {row['predicted']} vs register {claim.predicted}")
    return out


def _with_line_replaced(text: str, starts: str, old: str, new: str) -> str:
    lines = text.splitlines()
    hits = [i for i, line in enumerate(lines) if line.startswith(starts)]
    assert len(hits) == 1, f"the mutation's anchor {starts!r} matched {len(hits)} lines"
    lines[hits[0]] = lines[hits[0]].replace(old, new, 1)
    return "\n".join(lines)


def _without_line(text: str, starts: str) -> str:
    lines = text.splitlines()
    kept = [line for line in lines if not line.startswith(starts)]
    assert len(kept) == len(lines) - 1, f"the mutation's anchor {starts!r} is not one line"
    return "\n".join(kept)


def test_the_claims_register_is_section_5() -> None:
    """C32. B32. DD30. The table a reader sees and the data a gate enforces are one table.

    **Mutation:** the same comparison over a copy of the build order with H3's scorer changed,
    and over one with H7's row deleted, both disagree with the register.
    """
    text = _read(BUILD_ORDER)
    assert not register_disagreements(text, CLAIMS), register_disagreements(text, CLAIMS)
    assert len(claims_table(text)) == len(CLAIMS) == 24

    rescored = _with_line_replaced(text, "| H3 |", "| D6 |", "| D8 |")
    assert any(
        "H3: §5 scorer D8" in problem for problem in register_disagreements(rescored, CLAIMS)
    )

    deleted = _without_line(text, "| H7 |")
    assert any("H7 is in one of" in problem for problem in register_disagreements(deleted, CLAIMS))


def test_the_live_candidate_universe_is_one_a_claim_was_scored_against() -> None:
    """C116. DD120, `AMENDMENT_A6` §1 clause 3. A pool that grew with no claim behind it.

    H3 and H9 are `PASS` over eleven candidate series and 231 structures. `AMENDMENT_A5` §0
    row 13 puts twenty series at 1,350 and thirty at 4,525, so the candidate pool is the
    surface those two verdicts were earned over and a verdict without it named is a number
    with no denominator. DD120 clause 3 pre-registers the rule: a verdict at a different
    universe is a NEW claim with a new id, predicted before it runs, never a re-score of one
    that was given its verdict somewhere else.

    **Deliberately not an equality against today's eleven.** C103 already holds that, and an
    equality here would force a later author to EDIT H3's historical universe instead of
    registering a claim against the new one -- which is the opposite of what clause 3 asks,
    and would turn this bar into an instrument for erasing the thing it exists to protect.
    What is asserted is weaker and is the half that matters: whatever the live pool is, some
    registered claim must have been scored against it.

    So this goes red on exactly one event -- a series admitted to `FACTOR_SERIES` or `COST_OF`
    with no claim scored at the universe it produces -- and it goes green two ways, which is
    the point: register the new claim, or do not grow the pool.

    **Mutation:** with the universes stripped out of §5, the live pool has nothing behind it.
    """
    text = _read(BUILD_ORDER)
    scored = scored_universes(text)
    assert scored, "no §5 row names the universe its verdict was scored against"

    live = (len(CANDIDATE_SERIES), len(enumerate_universe()))
    assert live in scored, (
        f"the candidate pool is now {live[0]} series / {live[1]} structures, and no claim in §5 "
        "was scored against it. `AMENDMENT_A6` DD120 clause 3: register a new claim at this "
        "universe rather than re-scoring one that earned its verdict at another."
    )

    stripped = _SCORED_UNIVERSE.sub("a universe nobody wrote down", text)
    assert live not in scored_universes(stripped)


def test_every_claim_is_scored_by_the_right_kind_of_package() -> None:
    """C33. B33. DD30, DD32. Live by core, annexed by annex, and the gaps declared.

    D23 is excluded as a scorer on purpose: it is hosted in curvecast and carries no claim
    (`AMENDMENT_A1` §3.5), and every scorer being hosted here is what lets C34 read closure
    from this repository alone.
    """
    core, annex = order_tables(_read(BUILD_ORDER))
    register = {claim.claim_id: claim for claim in CLAIMS}

    for claim in CLAIMS:
        assert claim.scorer != "D23", claim.claim_id
        if claim.status is ClaimStatus.ACTIVE:
            assert claim.scorer in core, (claim.claim_id, claim.scorer)
        elif claim.status is ClaimStatus.ANNEXED:
            assert claim.scorer in annex, (claim.claim_id, claim.scorer)
        else:
            assert claim.scorer in set(core) | set(annex), (claim.claim_id, claim.scorer)
            for successor in claim.successors:
                assert register[successor].status is ClaimStatus.ACTIVE, successor

    numbers = {claim_number(claim.claim_id) for claim in CLAIMS} - {None}
    missing = set(range(1, max(numbers) + 1)) - numbers
    assert missing == NUMBERING_GAPS == {10}, (
        f"the H sequence skips {sorted(missing)} but declares {sorted(NUMBERING_GAPS)}; a "
        "claim was removed without trace, or a gap was filled without the declaration"
    )


#: DD161. A pre-registration whose run has not happened: bars fixed, verdicts owed, the package
#: not landed. DD129's rider predicted this in its own section 4: *"If a second and third want the
#: same separation, the definition is the defect."* The joint registration of the four
#: out-of-sample readers is the second: DD133 needs it in the tree before the first read, and
#: until the read no verdict can exist, so its existence cannot mean the packages landed.
REGISTERED_MARKER = "**Status: REGISTERED, not landed.**"

#: DD161, DD199. The documents allowed to carry a registered marker, each with the reason it cannot
#: land in the same commit as its run. Held as an equality, so a third is an edit to this
#: declaration and never a quiet use of the marker to postpone a verdict. D17's entry (DD182) left
#: when D17 landed, 2026-09-27: a marker is removed by landing, never by editing this set alone.
#: D16's (DD225) left the same way on 2026-09-28, in the commit that rendered the read and tagged CP-2,
#: and the joint registration's (DD161, DD172) the same day, when D22 read under its section 14.
#: D21's (DD199), the last, left on 2026-09-29, when D21 read under its own section 13. The set is
#: empty and stays declared: a new registered document is an edit here, as every one before it was.
REGISTERED_DOCUMENTS: dict[str, str] = {}

#: The package ids a pre-commit's filename names, in order: `d7a_cost_model` names D7a, and the
#: joint `d12_d14_d15_d22_...` names all four.
_PRECOMMIT_PACKAGES = re.compile(r"^PRECOMMIT_deskcraft_((?:d\d+[a-z]?_)+)")


def packages_named(filename: str) -> tuple[str, ...]:
    """The packages a pre-commit document covers, read from its name."""
    match = _PRECOMMIT_PACKAGES.match(filename)
    if match is None:
        return ()
    return tuple("D" + token[1:] for token in match.group(1).strip("_").split("_"))


def precommits_for(package: str, docs: Path) -> list[Path]:
    """Every pre-commit document whose name covers `package`."""
    return [
        path
        for path in sorted(docs.glob("PRECOMMIT_deskcraft_*.md"))
        if package in packages_named(path.name)
    ]


#: DD172. After the read, D12, D14 and D15 land and D22 does not (DD168's option 1), so the joint
#: document needs a marker that registers some of the packages it names and lands the rest. Fixed
#: before the read, so the landing commit only edits a status line and invents no mechanism.
_PARTIAL_MARKER = re.compile(r"\*\*Status: REGISTERED, not landed, for (D\d+[a-z]?(?:, D\d+[a-z]?)*)\.\*\*")


def _status_lines(text: str) -> list[str]:
    """DD239. The lines that are a status marker and nothing else.

    DD161 says a pre-commit counts if it does not carry **the line**; the first version read any
    occurrence, and the joint registration quotes its own marker inside a sentence in §0. So a
    substring test could never have landed D12, D14 and D15, and the landing commit found it.
    """
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() == REGISTERED_MARKER or _PARTIAL_MARKER.fullmatch(line.strip())
    ]


def registered_in(text: str, package: str) -> bool:
    """Whether a pre-commit's text holds `package` registered and not landed (DD161, DD172, DD239)."""
    lines = _status_lines(text)
    if REGISTERED_MARKER in lines:
        return True
    return any(package in _PARTIAL_MARKER.fullmatch(line).group(1).split(", ") for line in lines
               if _PARTIAL_MARKER.fullmatch(line))


def closed(package: str, docs: Path) -> bool:
    """Whether a package has landed: a pre-commit covering it exists and is not merely registered.

    DD31 made existence the test; DD161 keeps it, and adds the one exception the out-of-sample
    readers need -- a document carrying `REGISTERED_MARKER` closes nothing. DD172 lets the joint
    document register only some of the packages it names.
    """
    return any(not registered_in(_read(path), package) for path in precommits_for(package, docs))


def closure_disagreements(claims: tuple[Claim, ...], docs: Path) -> list[str]:
    """Live claims whose verdict and whose scorer's closure disagree, in either direction."""
    out = []
    for claim in claims:
        if claim.status is not ClaimStatus.ACTIVE:
            continue
        landed, scored = closed(claim.scorer, docs), claim.verdict is not None
        if landed and not scored:
            out.append(f"{claim.claim_id}: {claim.scorer} has landed and the claim is unscored")
        if scored and not landed:
            out.append(f"{claim.claim_id}: a verdict with no {claim.scorer} document behind it")
    return out


def test_a_verdict_exists_if_and_only_if_its_scorer_closed(tmp_path: Path) -> None:
    """C34. B34. DD31. Unscored after landing, and scored before landing, are both refused.

    **Mutation, both ways:** a D12 document with `SCENARIO_SIGNS` unscored, and a verdict on
    H3 with no D6 document. And the glob's near miss: D1's document does not close D12.
    """
    assert not closure_disagreements(CLAIMS, DOCS), closure_disagreements(CLAIMS, DOCS)
    assert closed("D1", DOCS) and closed("D2", DOCS) and closed("D3a", DOCS)

    landed = tmp_path / "landed"
    landed.mkdir()
    (landed / "PRECOMMIT_deskcraft_d12_scenario_engine.md").write_text("x", encoding="utf-8")
    # Since the read of 2026-09-28 `SCENARIO_SIGNS` carries D12's report, so the mutation takes it
    # away rather than relying on the register to be behind: a mutation that names a fact outside
    # its own subject has a shelf life, and this one's ran out the day D12 landed.
    unscored = tuple(
        dataclasses.replace(claim, verdict=None) if claim.claim_id == "SCENARIO_SIGNS" else claim
        for claim in CLAIMS
    )
    problems = closure_disagreements(unscored, landed)
    assert any(p.startswith("SCENARIO_SIGNS: D12 has landed") for p in problems), problems

    unlanded = tmp_path / "unlanded"
    unlanded.mkdir()
    scored = tuple(
        dataclasses.replace(claim, verdict=Verdict.PASS) if claim.claim_id == "H3" else claim
        for claim in CLAIMS
    )
    problems = closure_disagreements(scored, unlanded)
    # Two entries since 2026-09-16, and the second is what the first line of this mutation is
    # for: H3 is forced to carry a verdict here, and **H9 already carries one** -- D7b's, the
    # register's second in twenty claims. Against a docs directory with nothing in it both are
    # unbacked, and a mutation that still expected one would be asserting the register had not
    # moved rather than that the check works.
    #
    # **Derived since D10 (2026-09-25).** The list was written out by hand, and it went red the
    # day D10 set four verdicts: a mutation naming facts outside its own subject has a shelf life,
    # which D7b's P8 recorded and this bar then repeated. Every scored live claim is unbacked
    # against an empty directory, so the expectation is computed from the register, and H3 --
    # the one this mutation forces -- must be among them.
    expected = [
        f"{claim.claim_id}: a verdict with no {claim.scorer} document behind it"
        for claim in scored
        if claim.status is ClaimStatus.ACTIVE and claim.verdict is not None
    ]
    assert problems == expected, problems
    assert "H3: a verdict with no D6 document behind it" in problems
    assert len(problems) >= 2, "the register has held at least two verdicts since 2026-09-16"

    near = tmp_path / "near"
    near.mkdir()
    (near / "PRECOMMIT_deskcraft_d1_scaffold.md").write_text("x", encoding="utf-8")
    assert closed("D1", near) and not closed("D12", near) and not closed("D14", near)


# ---------------------------------------------------------------------------
# C35: the package budget
# ---------------------------------------------------------------------------


def order_tables(text: str) -> tuple[list[str], list[str]]:
    """The package ids of §4's core table and §4.1's annex table, in row order."""
    def ids(body: str) -> list[str]:
        return [match.group(1) for line in body.splitlines() if (match := _ORDER_ROW.match(line))]

    return (
        ids(_section(text, "## 4. The order", "### 4.1")),
        ids(_section(text, "### 4.1", "## 5.")),
    )


def budget_disagreements(text: str, budget: int) -> list[str]:
    core, annex = order_tables(text)
    out = []
    if len(core) != budget:
        out.append(f"the core table has {len(core)} packages against a budget of {budget}")
    if set(core) & set(annex):
        out.append(f"in both core and annex: {sorted(set(core) & set(annex))}")
    if len(core) != len(set(core)) or len(annex) != len(set(annex)):
        out.append("a package id appears twice in one table")
    return out


def test_the_core_is_exactly_the_budget() -> None:
    """C35. B35. DD33. Growth and shrinkage are both visible, and neither is silent.

    **Mutation:** a 22nd core row, a missing core row, and an annex row repeating a core id
    each fail against the unedited budget.
    """
    text = _read(BUILD_ORDER)
    assert not budget_disagreements(text, PACKAGE_BUDGET), budget_disagreements(text, PACKAGE_BUDGET)
    core, annex = order_tables(text)
    assert (len(core), len(annex)) == (21, 2), (core, annex)

    last = next(line for line in text.splitlines() if line.startswith("| **D22** |"))
    grown = text.replace(last, last + "\n" + last.replace("**D22**", "**D24**", 1), 1)
    assert budget_disagreements(grown, PACKAGE_BUDGET) == [
        "the core table has 22 packages against a budget of 21"
    ]

    shrunk = _without_line(text, "| **D22** |")
    assert budget_disagreements(shrunk, PACKAGE_BUDGET) == [
        "the core table has 20 packages against a budget of 21"
    ]

    annex_row = next(line for line in text.splitlines() if line.startswith("| **D19** |"))
    doubled = text.replace(annex_row, annex_row + "\n" + annex_row.replace("**D19**", "**D14**", 1), 1)
    assert budget_disagreements(doubled, PACKAGE_BUDGET) == ["in both core and annex: ['D14']"]


# ---------------------------------------------------------------------------
# C36: the source resilience register
# ---------------------------------------------------------------------------


def _components(book: object) -> set[str]:
    return {
        component.series
        for leg in book.legs  # type: ignore[attr-defined]
        for component in leg.instrument.components
    }


def test_the_source_register_covers_the_book_and_never_weakens_a_licence() -> None:
    """C36. B36. DD34-DD36. Coverage, the stricter licence, and the two fallback iffs.

    **Mutation:** a row whose FRED tag says public domain and whose licensor's notice forbids
    redistribution is not committable -- `BAA10Y`'s shape, one step more extreme -- and the two
    fallback laws raise at construction in both directions.
    """
    assert len(SOURCES) == len(SOURCE_ROWS), "a series was written into the register twice"
    assert all(key == row.series for key, row in SOURCES.items())

    missing = _components(REFERENCE_BOOK) - set(SOURCES)
    assert not missing, f"the reference book names series the register has never seen: {missing}"
    for series in _components(US_CASH_BOOK):
        assert SOURCES[series].licence is not Licence.UNMEASURED, series

    for row in SOURCE_ROWS:
        expected = row.notice if row.fred_tag is None else max(row.fred_tag, row.notice)
        assert row.licence is expected, row.series
        # DD35's question, which every row still answers and which `sendable_free` now holds.
        # `committable` stopped being the same question on 2026-09-23 (DD137): it is now
        # public domain OR an owner admission by name, and the two came apart on purpose.
        assert row.sendable_free is (row.licence is Licence.PUBLIC_DOMAIN), row.series
        assert row.committable is (row.sendable_free or row.series in ADMITTED), row.series
        assert row.licence >= row.notice, row.series

    base = dict(
        series="X",
        originator="Licensor",
        originator_class=OriginatorClass.COMMERCIAL_VENDOR,
        publisher="A distributor",
        # DD136's new axis. A synthetic row has no words behind it, so unmeasured is the
        # only honest grade -- and it is inert here, because every case below either has a
        # non-public-domain licence or trips an earlier check.
        derivation=Derivation.UNMEASURED,
        evidence="synthetic",
    )
    stricter_notice = Source(
        **base,
        fred_tag=Licence.PUBLIC_DOMAIN,
        notice=Licence.REDISTRIBUTION_PROHIBITED,
        fallback="Another",
        fallback_originator="Someone else",
    )
    assert stricter_notice.licence is Licence.REDISTRIBUTION_PROHIBITED
    assert not stricter_notice.committable and stricter_notice.independent_fallback

    with pytest.raises(ValueError, match="absent if and only if a reason"):
        Source(**base, fred_tag=None, notice=Licence.PUBLIC_DOMAIN, fallback=None,
               fallback_originator=None)
    with pytest.raises(ValueError, match="absent if and only if a reason"):
        Source(**base, fred_tag=None, notice=Licence.PUBLIC_DOMAIN, fallback="F",
               fallback_originator="O", no_fallback_reason="but also a reason")
    with pytest.raises(ValueError, match="originator is named if and only if"):
        Source(**base, fred_tag=None, notice=Licence.PUBLIC_DOMAIN, fallback="F",
               fallback_originator=None)


# ---------------------------------------------------------------------------
# C37: the ledger entry
# ---------------------------------------------------------------------------

LEDGER_HEADING = "## Non-look entries"


def test_the_foreclosure_is_in_curvecasts_ledger() -> None:
    """C37. B37. DD37. Watched from here, because the repository it constrains gains by losing it.

    Parsed, and skips loudly when curvecast is absent, in C9's shape.
    """
    ledger = CURVECAST / "docs" / "TRIAL_LEDGER.md"
    if not ledger.exists():
        pytest.skip("curvecast is not on this machine; the ledger entry was not checked")

    text = _read(ledger)
    assert LEDGER_HEADING in text, "the non-look section is gone from curvecast's ledger"
    section = text[text.index(LEDGER_HEADING) :]
    section = section[: section.find("\n## ", 1)] if "\n## " in section[1:] else section
    rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in section.splitlines()
        if line.startswith("|") and not line.startswith("|---")
    ]
    header, entries = rows[0], rows[1:]
    ours = [dict(zip(header, row, strict=True)) for row in entries if "deskcraft" in row[1]]
    assert len(ours) == 1, f"expected one deskcraft entry, found {len(ours)}"
    entry = ours[0]
    assert entry["Looks spent"].strip("*") == "0", entry
    assert entry["Trials spent"].strip("*") == "0", entry
    assert "DEV_END" in entry["Takes effect"] and "2014-12-31" in entry["Takes effect"], entry


# ---------------------------------------------------------------------------
# C38: citations
# ---------------------------------------------------------------------------

_CITATION = re.compile(r"`(test_\w+)`\s*\((C\d+[a-z]?)\)")


def claims_by_test(tests: Path) -> dict[str, str]:
    """Test function name -> the bar id its docstring claims, across every test module."""
    found: dict[str, str] = {}
    for path in sorted(tests.glob("test_*.py")):
        for node in ast.walk(ast.parse(_read(path))):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                match = re.match(r"^(C\d+[a-z]?)\.", ast.get_docstring(node) or "")
                if match:
                    found[node.name] = match.group(1)
    return found


def citation_disagreements(root: Path, claimed: dict[str, str]) -> list[str]:
    out = []
    for path in working_tree(root, frozenset({".md", ".py", ".toml"})):
        for match in _CITATION.finditer(_read(path)):
            name, cited = match.group(1), match.group(2)
            if name not in claimed:
                out.append(f"{path.name}: cites {name} as {cited}, and no such test exists")
            elif claimed[name] != cited:
                out.append(f"{path.name}: cites {name} as {cited}; it claims {claimed[name]}")
    return out


#: The effective-number-of-bets family, and the words that name a basis for it. `AMENDMENT_A3`
#: §4: one covariance of eight GSW zeros returns 1.8231 (Roy-Vetterli), 7.9059 (min-torsion) and
#: 8.0000 (whitening), so the statistic is a property of the basis and a threshold without one
#: does not name a verdict.
_ENB_WORDS = ("enb", "effective rank", "effective number of bets")
_BASIS_WORDS = ("roy-vetterli", "min-torsion", "whitening", "basis")


def unbased_enb_claims(claims: tuple[Claim, ...]) -> list[str]:
    """Live claims naming the effective-number-of-bets family without naming a basis."""
    out = []
    for claim in claims:
        if claim.status is not ClaimStatus.ACTIVE:
            continue
        statement = claim.statement.lower()
        if any(word in statement for word in _ENB_WORDS) and not any(
            word in statement for word in _BASIS_WORDS
        ):
            out.append(claim.claim_id)
    return sorted(out)


def test_a_cited_test_carries_the_id_it_is_cited_by(tmp_path: Path) -> None:
    """C38. B38. DD38. M18a corrected three documents, and a comment still said C10.

    **Mutation:** the line `pyproject.toml` carried before this commit is reported, and so is a
    citation of a test that does not exist. The mutation's text is assembled at run time so
    that this file does not itself contain the stale citation for the real scan to find.
    """
    claimed = claims_by_test(TESTS)
    assert claimed.get("test_the_llm_edge_is_scanned") == "C23"
    assert not citation_disagreements(REPO_ROOT, claimed), citation_disagreements(REPO_ROOT, claimed)

    stale = "# The ban is therefore an AST scan, `test_the_llm_edge_is_scanned` " + "(C10) -- the same\n"
    invented = "See `test_that_does_not_exist` " + "(C1).\n"
    (tmp_path / "pyproject.toml").write_text(stale, encoding="utf-8")
    (tmp_path / "NOTES.md").write_text(invented, encoding="utf-8")
    assert citation_disagreements(tmp_path, claimed) == [
        "NOTES.md: cites test_that_does_not_exist as C1, and no such test exists",
        "pyproject.toml: cites test_the_llm_edge_is_scanned as C10; it claims C23",
    ]


def test_the_withdrawn_enb_claims_are_replaced_by_ones_the_reference_book_can_carry() -> None:
    """C93. B93, DD93, DD95. `AMENDMENT_A3` §3, §5, §6.

    §5 predicted `ENB < 3.0` for a *"six-leg US book"*, and there is no such object. The six-leg
    `REFERENCE_BOOK` is not US-only -- `eurusd` is EUR and `us_de_10y` reaches the German curve --
    and **both legs it adds over the priceable book are in `DEFERRED_LEGS`**, refused for stated
    reasons rather than pending. So the claim was scored against a covariance this repository has
    declined to build.

    The restated claims name `US_CASH_BOOK`, and this bar holds the arithmetic that makes the
    restatement honest rather than convenient: **ENB is bounded above by the leg count**, so moving
    the book from six legs to four moves the bar from 50% of maximum to **75%** -- a materially
    weaker claim, forced by the data and recorded rather than absorbed. The threshold itself does
    not move, which is §5's own standing rule.

    **Mutation:** a successor restated onto the six-leg book is reported, and so is a live claim
    still carrying the phrase the withdrawal removed.
    """
    assert len(REFERENCE_BOOK.leg_ids) == 6
    assert len(US_CASH_BOOK.leg_ids) == 4
    assert len(DEFERRED_LEGS) == 2
    assert set(DEFERRED_LEGS) == set(REFERENCE_BOOK.leg_ids) - set(US_CASH_BOOK.leg_ids)
    assert not set(DEFERRED_LEGS) & set(US_CASH_BOOK.leg_ids)

    register = {claim.claim_id: claim for claim in CLAIMS}
    for withdrawn, successors in (("H4", ("H4a", "H4b")), ("H8", ("H8a", "H8b"))):
        claim = register[withdrawn]
        assert claim.status is ClaimStatus.WITHDRAWN, withdrawn
        assert claim.successors == successors
        assert claim.verdict is None
        for successor in successors:
            assert register[successor].status is ClaimStatus.ACTIVE
            assert register[successor].scorer == claim.scorer

    # ENB <= n, so the same threshold is a different bar on a different book (`AMENDMENT_A3` §5.1).
    assert 3.0 / len(US_CASH_BOOK.leg_ids) == 0.75
    assert 3.0 / len(REFERENCE_BOOK.leg_ids) == 0.5
    #: H9 predicts the generated book terminates at three or four legs. At three, `< 3.0` is the
    #: whole range: the bar can fail only on a perfectly diversified book, which is the outcome it
    #: was written to detect the absence of.
    assert 3.0 / 3 == 1.0

    live = [claim for claim in CLAIMS if claim.status is ClaimStatus.ACTIVE]
    assert not [claim.claim_id for claim in live if "six-leg" in claim.statement.lower()]

    restated = dataclasses.replace(register["H4a"], statement="Six-leg US book has ENB < 3.0")
    assert "six-leg" in restated.statement.lower()
    assert restated.status is ClaimStatus.ACTIVE


def test_a_live_claim_on_the_effective_number_of_bets_names_its_basis() -> None:
    """C94. B94, DD94. `AMENDMENT_A3` §4.

    Meucci's effective number of bets has no portfolio-free form, and curvecast item 28 measured
    what that costs: on **one** covariance of eight GSW zeros, three mutually uncorrelated bases
    return **1.8231** (Roy-Vetterli effective rank), **7.9059** (volatility-preserving min-torsion)
    and **8.0000** (plain whitening). Min-torsion is algebraically the exp-entropy of the marginal
    variances and whitening returns `n` exactly, so two of the three carry no diversification
    information at all.

    A threshold of 3.0 admits the first and refuses the other two. So `ENB < 3.0` with no basis
    named is not a claim about a book -- it is a claim about which rung of D10's own ladder gets
    compared to the number, chosen by the package being scored. That is `COST_HURDLE` again
    (`AMENDMENT_A2` §2), and unlike the hurdle it cannot be removed by algebra: a basis must
    actually be picked, so DD94 picks it here, before D10 exists.

    **Mutation:** the register as it stood before this amendment -- H4 and H8 as written -- is run
    through the same helper, and must name both.
    """
    assert not unbased_enb_claims(CLAIMS), unbased_enb_claims(CLAIMS)

    before = tuple(
        claim
        for claim in CLAIMS
        if claim.claim_id not in {"H4", "H4a", "H4b", "H8", "H8a", "H8b"}
    ) + (
        Claim("H4", "Six-leg US book has ENB < 3.0", "D10", Verdict.PASS),
        Claim("H8", "Generated book beats hand-built on ENB; both < 3.0", "D10", Verdict.PASS),
    )
    assert unbased_enb_claims(before) == ["H4", "H8"]


def test_the_out_of_sample_window_is_fixed_and_contiguous_with_dev() -> None:
    """C96. B96, DD98, DD102. `AMENDMENT_A4` §3.1, §5.

    `FitWindow` refuses an end past `DEV_END`, so an object cannot be fitted on the years it is
    tested against. This is the other half. D12, D14, D15 and D22 all read the out-of-sample
    record and **none of them existed when it was fixed** -- a window left to the package that
    reads it is `AMENDMENT_A2`'s cost hurdle and `AMENDMENT_A3`'s effective-number-of-bets basis
    a third time, with the *sample itself* as the free parameter.

    Two properties, and the second is the one that matters:

    * **Contiguity.** `OOS_START` is exactly the day after `DEV_END`, so the two windows partition
      the record. A gap between them would be a stretch of history belonging to neither, which is
      where a window nobody pre-registered would fit.
    * **A fixed forward bound.** `OOS_END` is a constant, not a clock read. A record ending "at
      extraction" changes every time the extractor runs, which makes re-running it until the
      numbers improve a refresh rather than a violation.

    **Mutation:** every bound is pushed one day past its limit, and a `datetime` is offered where
    a `date` is required -- the last because `FitWindow` learned that a `datetime` subclass turns
    a bound into a `TypeError` by accident rather than a refusal by design.
    """
    one_day = timedelta(days=1)

    assert OOS_START == DEV_END + one_day
    assert OOS_START > DEV_END and OOS_START < OOS_END
    assert OosWindow.whole() == OosWindow(OOS_START, OOS_END)

    # Eleven complete calendar years, which is the rule DD98 applied and not a round number.
    assert OOS_START.month == 1 and OOS_START.day == 1
    assert OOS_END.month == 12 and OOS_END.day == 31
    assert OOS_END.year - OOS_START.year + 1 == 11

    with pytest.raises(ValueError, match="reaches back into DEV"):
        OosWindow(DEV_END, OOS_END)
    with pytest.raises(ValueError, match="reaches back into DEV"):
        OosWindow(DEV_END - one_day, OOS_END)
    with pytest.raises(ValueError, match="reaches past OOS_END"):
        OosWindow(OOS_START, OOS_END + one_day)
    with pytest.raises(ValueError, match="must run forwards"):
        OosWindow(OOS_END, OOS_END)
    with pytest.raises(TypeError, match="must be a datetime.date exactly"):
        OosWindow(datetime(2015, 1, 1), OOS_END)

    # And the fit window still refuses to reach into it, so neither side can borrow the other's.
    with pytest.raises(ValueError, match="reaches past DEV_END"):
        FitWindow(DEV_START, OOS_START)


def test_the_out_of_sample_panel_is_specified_and_does_not_exist_yet() -> None:
    """C97. B97, DD99, DD101, DD102. `AMENDMENT_A4` §0, §3.2, §4.

    The panel four packages read is specified and not built, and **the first read of it is
    irreversible**: DD37 takes effect at deskcraft's first row dated after `DEV_END` and
    forecloses curvecast's remaining look budget. So this bar holds two things at once -- that the
    specification still matches the module, and that **the trigger has not been pulled**.

    §4's D14 row commissions *"~2,700 OOS days"* against no stated end date. The DEV panel runs at
    a measured rate, and eleven complete years at that rate is a different number; it is
    **recomputed here** rather than copied from the document, so the annotation cannot drift from
    the panel that justified it.

    **Mutation:** a fixture carrying a post-DEV date is reported, because that is the state this
    bar exists to notice the moment it changes.
    """
    amendment = _read(AMENDMENT_A4)

    # The document and the module, held at equality (C90's shape).
    assert f"`OOS_END = {OOS_END}`" in amendment or f"OOS_END = date({OOS_END.year}, " in amendment
    assert f"{OOS_START} \u2192 {OOS_END}" in amendment

    # The session rate is measured, not asserted, and the estimate is derived from it.
    dates = _panel_dates(DEV_PANEL)
    years = {day.year for day in dates}
    rate = len(dates) / len(years)
    assert 260.0 <= rate <= 261.0, rate
    span = OOS_END.year - OOS_START.year + 1
    estimate = round(span * rate / 10) * 10
    assert estimate == 2870, estimate
    assert f"\u2248 {estimate:,}" in amendment or f"{estimate:,}" in amendment

    # D14's figure, and the gap this amendment annotates rather than rewrites.
    assert round(100.0 * (estimate - 2700) / estimate, 1) == 5.9

    # The trigger. Unpulled until the owner's authorisation existed (DD133); pulled once on
    # 2026-09-28 by DD102's commit, and only by the record's three files, none past OOS_END.
    assert max(dates) == DEV_END
    past = _fixtures_past_dev()
    if not (DOCS / "OWNER_AUTHORISATION_the_first_oos_read.md").exists():
        assert not past
    else:
        from deskcraft.readers import RECORD_FILES

        # The record's three, and each reader's result file beside them (DD240), all named _oos_.
        assert set(path.name for path in RECORD_FILES) <= set(past), past
        assert all("_oos_" in name for name in past), past
        assert all(max(_panel_dates(path)) == OOS_END for path in RECORD_FILES)
        # Every reader has read: D22's result on 2026-09-28 and D21's, the last, on 2026-09-29. A
        # further file past DEV_END is a new read, and is an edit here before it is a fixture.
        # DD243 added two on 2026-09-29, by the owner's decision: the Fed's volatility after the read,
        # each beside the landed file it reproduces outside the implied columns (C225).
        results = set(past) - {path.name for path in RECORD_FILES}
        assert results == {
            "d22_funding_oos_20260928.csv",
            "d21_replayed_oos_20260929.csv",
            "d21_implied_after_the_read_oos_20260929.csv",
            "d22_implied_after_the_read_oos_20260929.csv",
        }, results


def _panel_dates(path: Path) -> list[date]:
    """Every observation date in a committed panel fixture."""
    import csv

    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    field = next(name for name in rows[0] if "date" in name.lower())
    return [date.fromisoformat(row[field][:10]) for row in rows]


def _fixtures_past_dev() -> list[str]:
    """Committed fixtures carrying a row dated after DEV_END. Empty until the OOS panel lands."""
    out = []
    for path in sorted((REPO_ROOT / "tests" / "fixtures").glob("*.csv")):
        if max(_panel_dates(path)) > DEV_END:
            out.append(path.name)
    return out


def test_the_out_of_sample_end_follows_from_the_rule_the_amendment_states() -> None:
    """C98. B98, DD98, DD103. `RIDER_A4_the_date_and_two_unowned_findings.md` §1, §4.

    DD98's whole defence is that the window was **not chosen**: `OOS_END` is *the last complete
    calendar year at the date of specification*, and on that date the rule returns exactly one
    answer. A defence of that shape is only as good as its input, and until this bar **nothing in
    this repository read an amendment's stated date at all** -- which is how `AMENDMENT_A4` came to
    state 2026-09-15 six times while being committed at 09:44 on 2026-09-16.

    The rule is **re-implemented here rather than imported** from `window.py`. A constant checked
    against the function that produced it proves only that the function ran; a constant checked
    against an independent restatement of the rule proves the rule.

    Armed in both directions, which is the point: move `OOS_END` to 2026-12-31 without touching the
    stated date and this reddens; move the stated date into a year where the rule returns something
    else and it reddens too.

    **What it cannot do** is verify that the stated date is the date the work happened. Only the
    commit says that, and the commit does not exist when the bar is written -- so §1's correction
    closes that half and nothing else does.

    **Mutation:** the rule is run one day either side of the stated date and at the first date it
    would move, so a bar that passed by returning a constant is caught.
    """

    def last_complete_year_end(on: date) -> date:
        """`AMENDMENT_A4` DD98's rule, restated: the end of the last complete calendar year."""
        return date(on.year - 1, 12, 31)

    stated = _stated_specification_date(_read(AMENDMENT_A4))

    assert last_complete_year_end(stated) == OOS_END
    assert stated <= date.today(), f"the specification date {stated} is in the future"
    assert stated > DEV_END

    # The rule is stable across the interval in which the amendment could have been written, and
    # moves on a date this window would have to be amended to reach.
    assert last_complete_year_end(stated - timedelta(days=1)) == OOS_END
    assert last_complete_year_end(date(stated.year, 1, 1)) == OOS_END
    assert last_complete_year_end(date(stated.year + 1, 1, 1)) != OOS_END

    # The rider says what was corrected, so the correction cannot be quietly undone.
    rider = _read(RIDER_A4)
    assert "DD103" in rider
    assert str(stated) in rider and "2026-09-15" in rider


def _stated_specification_date(amendment: str) -> date:
    """The date `AMENDMENT_A4` §3.1 says DD98's rule was applied on.

    Read from the sentence that carries the defence rather than from the header, because the
    header records when the work was raised and the rule cares about when it was fixed.
    """
    match = re.search(r"The specification date is (\d{4}-\d{2}-\d{2})", amendment)
    assert match, "`AMENDMENT_A4` §3.1 no longer states the date DD98's rule was applied on"
    return date.fromisoformat(match.group(1))


def test_c158_a_registration_is_not_a_landing(tmp_path: Path) -> None:
    """C158. DD161, DD182. A pre-commit marked registered closes nothing, and only declared ones may be.

    The joint registration of the four out-of-sample readers has to exist before the first read
    (DD133), and D12's claims cannot be scored until after it. DD31's rule would read its existence
    as D12 having landed. The marker is the exception. It was held to that one document so no other
    package could use it to postpone a verdict, and DD182 admits a second, D17's, whose rules must
    precede an extraction in curvecast. The set is declared with reasons and held as an equality.

    **Mutation:** the same joint name, with and without the marker, over a scratch directory.
    """
    readers = ("D12", "D14", "D15", "D22")
    docs = tmp_path / "docs"
    docs.mkdir()
    joint = docs / "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md"
    joint.write_text("# joint\n\n" + REGISTERED_MARKER + "\n", encoding="utf-8")
    assert not any(closed(r, docs) for r in readers)
    joint.write_text("# joint\n\nlanded\n", encoding="utf-8")
    assert all(closed(r, docs) for r in readers), "the joint name must close all four readers"
    assert not closed("D1", docs) and not closed("D2", docs)
    assert packages_named("PRECOMMIT_deskcraft_d7a_cost_model.md") == ("D7a",)
    assert packages_named("RIDER_d12_anything.md") == ()

    marked = [
        p.name
        for p in sorted(DOCS.glob("PRECOMMIT_deskcraft_*.md"))
        if _status_lines(_read(p))
    ]
    assert marked == sorted(REGISTERED_DOCUMENTS), marked
    # DD172: the read of 2026-09-28 landed D12, D14 and D15 (section 13), and D22 the same day (14).
    assert [closed(r, DOCS) for r in readers] == [True, True, True, True], "all four have read"

    # DD239: a marker quoted inside a sentence is a quotation, not a status.
    quoted = "# joint\n\n**Status: LANDED.**\n\nIt would carry the line `" + REGISTERED_MARKER + "`.\n"
    joint.write_text(quoted, encoding="utf-8")
    assert all(closed(r, docs) for r in readers), "a quoted marker registered the document"

    # DD172: the landing DD168's option 1 implies. Three readers land, D22 stays registered.
    joint.write_text("# joint\n\n**Status: REGISTERED, not landed, for D22.**\n", encoding="utf-8")
    assert [closed(r, docs) for r in readers] == [True, True, True, False]
    joint.write_text("# joint\n\n**Status: REGISTERED, not landed, for D12, D22.**\n", encoding="utf-8")
    assert [closed(r, docs) for r in readers] == [False, True, True, False]
    assert not registered_in("**Status: REGISTERED, not landed, for D2.**", "D22"), "D2 is not D22"

