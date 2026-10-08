"""The environment census. Carried item X1, decisions DD69-DD70 and DD72, bars C72-C73, C75.

**This is not a package.** It rides along, in the shape D4's row records for the lint gate.

**What it is for.** Distribution here is `git archive HEAD` and nothing else. A reviewer who
unpacks that archive has no curvecast, no meip, and possibly neither binary this repository's
tool gates resolve -- and before this file the suite reported green while **fourteen of
seventy-five bars had not run at all**, every one of them a bar whose whole purpose is to
compare this repository against something it does not control. The bars that went silent were
exactly the bars that make the claims checkable.

Counting them is not the fix, though, and the count turned out to be the smaller half of the
problem. Writing this census found **two more bars that lose a check off-machine without
skipping**: C6 has run `if CURVECAST.exists():` around its provenance half since D3a, and C61
has done the same since D6. Neither appears in any skip count, in any pytest output, or in any
package row. A bar that quietly does less is invisible in a way a skip is not.

So the census declares **two** conditions, not one:

    SKIPS     the bar does not run at all
    PARTIAL   the bar runs, minus the half that needs a sibling repository

and, since 2026-09-16, a third that is not a condition on the environment at all:

    SKIPS_ON_A_RED_SUITE   the bar runs everywhere and declines to report only when some
                           *other* bar is already failing

**That third kind is a finding, not an accommodation** (`RIDER_C73_a_bar_that_reports_without_a_verdict.md`
§2.3). The scanner treats `pytest.skip` as proof that a bar depends on the environment, and it was
right about every bar in this repository until C99 -- which skips because the suite is red, not
because a sibling repository is missing. A static scan can see that a bar *can* skip and never why,
so the scanner keeps saying `SKIPS` and the census says the reason; `EXPECTED_SKIPS`, which is what
a clean machine is held to, is derived from the reason and so does not gain a bar that would not
skip there.

and it is an **equality** (DD72), in the shape `ENGINE_IMPORT_ROOTS` and `MODULES` already use
here. A floor notices only shrinkage, and nothing in this repository would have noticed a
nineteenth.

**Three bars must keep skipping, and a fixture for them would be a lie** (DD70). C7, C9 and C37
watch properties of another repository that can *change* -- no upstream file importing deskcraft,
`EXEMPT_FIELDS` still `{}`, the foreclosure still in curvecast's ledger. Freezing a watched value
into a fixture is precisely what defeats a drift watch: a committed copy of `EXEMPT_FIELDS == {}`
would be green forever, including on the day curvecast amends it, which is the one event C9
exists to catch. These three are correct to skip. What was wrong is only that nothing said so.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest

import upstream_certificate
from absent_machine import (
    ABSENT,
    FAILURE_REPORT,
    REPORT,
    SUITE,
    UPSTREAM_CANDIDATE_LISTS,
    UPSTREAM_CONSTANTS,
    loaded_from,
    rebind,
)
from test_deskcraft_boundary import REPO_ROOT, TESTS, _read

SKIPS = "SKIPS"
PARTIAL = "PARTIAL"

#: Not a condition on the environment: the bar runs on every machine and declines to report a
#: verdict only while another bar is failing. See the module docstring.
SKIPS_ON_A_RED_SUITE = "SKIPS_ON_A_RED_SUITE"

#: What the static scan is able to see. It observes that a bar *can* reach `pytest.skip` and cannot
#: observe why, so a bar whose skip is not environmental is declared with its true reason and
#: normalised to `SKIPS` for the comparison in C72. The asymmetry is the honest one: the
#: scanner reports a capability, the census reports a cause.
_SCANNER_KIND = {SKIPS: SKIPS, PARTIAL: PARTIAL, SKIPS_ON_A_RED_SUITE: SKIPS}

#: Every environment-conditional bar in this repository, with the reason it is one. An equality:
#: a bar that gains a dependency on a sibling repository turns C72 red until it is recorded here,
#: in the commit that adds it, which is the same discipline `MODULES` imposes on the engine.
ENVIRONMENT_CONDITIONAL: dict[str, tuple[str, str]] = {
    # -- Kind B: live drift watches. Permanently conditional, and correctly so (DD70).
    "test_the_edges_are_one_way": (
        SKIPS,
        "C7. Watches that no upstream file imports deskcraft. A fixture would freeze the "
        "direction being watched, which is the edge going two-way unnoticed.",
    ),
    "test_curvecast_exemptions_are_still_empty": (
        SKIPS,
        "C9. Watches that curvecast's EXEMPT_FIELDS is still `{}`. A committed copy would stay "
        "green on the day it is amended, which is the single event this repository exists for.",
    ),
    "test_the_foreclosure_is_in_curvecasts_ledger": (
        SKIPS,
        "C37. Watches that the foreclosure is still in curvecast's trial ledger. The repository "
        "it constrains gains by losing it, so the watch lives here and cannot be satisfied here.",
    ),
    # -- Kind C: tool gates. Conditional on a binary, with a PATH fallback ahead of the skip.
    "test_the_tree_carries_no_ruff_finding": (
        SKIPS,
        "C58. Needs a ruff binary. `pip install ruff` restores it exactly -- the selection is "
        "pinned in pyproject.toml -- so this is a missing tool, not a missing repository.",
    ),
    "test_the_ruff_invocation_would_see_a_finding": (
        SKIPS,
        "C58b. The lint gate's mutation, through the same binary.",
    ),
    "test_the_import_contracts_are_kept_by_the_tool_that_checks_them": (
        SKIPS,
        "C74. Needs a lint-imports binary. `pip install import-linter` restores it; the "
        "contracts are this repository's own, in pyproject.toml.",
    ),
    "test_the_import_contract_run_would_see_both_failures": (
        SKIPS,
        "C74b. The import-contract mutation, through the same binary.",
    ),
    # -- Kind A: restatements. The arithmetic is this repository's; only the reference is
    #    upstream, so off-machine each compares against the certificate instead (DD69).
    "test_the_imperative_ban_transferred_even_though_the_field_ban_did_not": (
        PARTIAL,
        "C6. Found by writing this census, not by any skip count: since D3a it has checked that "
        "FORBIDDEN_RENDERED_PHRASES really are curvecast's only when curvecast is present. The "
        "imperative scan itself, which is what the bar is for, runs everywhere.",
    ),
    "test_the_priceable_partition_is_derived_from_what_is_actually_graded": (
        PARTIAL,
        "C14. The graded universe comes from the certificate off-machine; the partition it "
        "draws is asserted on every machine.",
    ),
    "test_the_dev_bounds_are_curvecasts": (
        PARTIAL,
        "C31. Compares this repository's DEV bounds against a dated transcription of "
        "curvecast's seal; the live parse is the conditional half.",
    ),
    "test_c39_the_front_end_the_steepener_needs_is_graded_upstream": (
        PARTIAL,
        "C39. Shares C14's universe. The four front-end names are asserted either way.",
    ),
    "test_c42_the_panel_is_on_curvecasts_gsw_session_grid": (
        PARTIAL,
        "C42. The session grid is certified as a digest off-machine, which a count of seven "
        "thousand strings would not be.",
    ),
    "test_c44_no_committed_value_needed_a_vintage_after_dev_ended": (
        PARTIAL,
        "C44. The vintage collapse is certified; the five refusals are asserted everywhere.",
    ),
    "test_the_compounding_convention_is_the_licensors_own_word": (
        PARTIAL,
        "C49. The licensor's words are certified; COMPOUNDING_OF, which is engine code and "
        "ships in the archive, is checked against them on every machine.",
    ),
    "test_the_par_bond_restatement_reproduces_meip_exactly": (
        PARTIAL,
        "C50. MEIP's 72 answers are certified as a digest of `repr`, so the equality stays an "
        "equality and does not become a tolerance.",
    ),
    "test_the_two_repositories_hold_the_same_gsw_bytes": (
        PARTIAL,
        "C59. The bar that decided the certificate's shape: copying curvecast's fixture would "
        "have it compare this panel against a copy of this panel.",
    ),
    "test_the_pca_restatement_reproduces_curvecasts_exactly": (
        PARTIAL,
        "C60. curvecast's eigensolver output is certified through `<f8`, so byte order is "
        "pinned rather than inherited from the host.",
    ),
    "test_c179_the_restated_values_are_optcrafts": (
        PARTIAL,
        "C179. D18's three option values are certified as a digest of optcraft's own 162 "
        "answers; the restatement is checked against it on every machine, and against optcraft "
        "itself where optcraft is present (DD196).",
    ),
    # -- Not environmental at all, and the reason the third kind exists (DD106).
    "test_a_clean_machine_runs_the_suite_green_or_says_why_it_cannot_tell": (
        SKIPS_ON_A_RED_SUITE,
        "C99. Skips when every bar that failed without the siblings fails with them too, which "
        "is a statement about the suite and not about the machine. It passes on a clean machine "
        "and so must not be in EXPECTED_SKIPS.",
    ),
    "test_the_spectrum_is_the_one_curvecast_published": (
        PARTIAL,
        "C61. Already the template for the Kind-A retrofit -- it checks committed constants "
        "rather than reaching next door -- but its effective-rank cross-check is conditional.",
    ),
}

#: What a clean machine must report. Derived rather than written twice.
EXPECTED_SKIPS = frozenset(
    name for name, (kind, _) in ENVIRONMENT_CONDITIONAL.items() if kind == SKIPS
)

UPSTREAM_NAMES = frozenset(UPSTREAM_CONSTANTS) | frozenset(UPSTREAM_CANDIDATE_LISTS)
CERTIFICATE_NAMES = frozenset(upstream_certificate.ENTRIES)


# ---------------------------------------------------------------------------
# The scanner, shared by the real check and by its mutation
# ---------------------------------------------------------------------------


def _names(node: ast.AST) -> set[str]:
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}


def _calls(node: ast.AST) -> set[str]:
    found: set[str] = set()
    for item in ast.walk(node):
        if isinstance(item, ast.Call):
            if isinstance(item.func, ast.Name):
                found.add(item.func.id)
            elif isinstance(item.func, ast.Attribute):
                found.add(item.func.attr)
    return found


def _skips(node: ast.AST) -> bool:
    return any(
        isinstance(item, ast.Call)
        and isinstance(item.func, ast.Attribute)
        and item.func.attr == "skip"
        and isinstance(item.func.value, ast.Name)
        and item.func.value.id == "pytest"
        for item in ast.walk(node)
    )


def conditional_bars(root: Path) -> dict[str, str]:
    """Every test function under `root` that depends on the environment, and how.

    Three signals, because one would not be enough. A bar is conditional if it can reach a
    `pytest.skip`, **or** it names a sibling-repository path constant, **or** it reads a
    certificate entry. The first two find the bars that existed before the certificate; the
    third finds the ones the retrofit created, which no longer skip and would otherwise have
    become invisible in a new way while fixing the old one.

    Propagated through calls, because every one of these bars reaches its dependency through a
    helper -- `graded_universe`, `_ruff`, `_run`, `_meip_par_bond`, `_curvecast_function` -- and
    a scan that only looked inside the test function's own body would find almost none of them.

    Read across the whole directory at once, not per module: `graded_universe` is defined in one
    module and used from another, which is the case a per-file scan gets wrong.
    """
    functions: dict[str, ast.FunctionDef] = {}
    for path in sorted(root.glob("test_*.py")):
        for node in ast.parse(_read(path)).body:
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = node

    skip = {name: _skips(node) for name, node in functions.items()}
    upstream = {name: bool(_names(node) & UPSTREAM_NAMES) for name, node in functions.items()}
    certified = {name: bool(_names(node) & CERTIFICATE_NAMES) for name, node in functions.items()}
    calls = {name: _calls(node) & set(functions) for name, node in functions.items()}

    changed = True
    while changed:
        changed = False
        for name in functions:
            for callee in calls[name]:
                for table in (skip, upstream, certified):
                    if table[callee] and not table[name]:
                        table[name] = True
                        changed = True

    return {
        name: (SKIPS if skip[name] else PARTIAL)
        for name in sorted(functions)
        if name.startswith("test_") and (skip[name] or upstream[name] or certified[name])
    }


# ---------------------------------------------------------------------------
# C72, C72b: the census is an equality
# ---------------------------------------------------------------------------


def test_every_environment_conditional_bar_is_declared() -> None:
    """C72. B72, DD72. An equality, so a nineteenth turns it red rather than joining silently.

    The two counts in the assertion messages are the ones this rider was built on: fourteen bars
    skipped, and eighteen are conditional. The gap is the finding -- four bars lose a check
    off-machine without skipping, and two of those four predate the retrofit that created the
    other two.
    """
    found = conditional_bars(TESTS)
    declared = {
        name: _SCANNER_KIND[kind] for name, (kind, _) in ENVIRONMENT_CONDITIONAL.items()
    }

    undeclared = sorted(set(found) - set(declared))
    assert not undeclared, (
        "these bars depend on the environment and are not in the census: "
        + ", ".join(undeclared)
        + ". Add each with its kind and its reason; a bar that reaches a sibling repository "
        "without saying so is exactly what this census exists to prevent."
    )
    stale = sorted(set(declared) - set(found))
    assert not stale, f"the census declares bars that no longer exist or no longer depend: {stale}"
    assert found == declared, {
        name: (found[name], declared[name]) for name in found if found[name] != declared[name]
    }

    assert len(EXPECTED_SKIPS) == 7, sorted(EXPECTED_SKIPS)
    assert len(found) == 20, sorted(found)
    # 19 conditional and still 7 skipping on a clean machine: C99 can skip and never does there.
    # 20 since D18: C179 reads optcraft and runs its certified half everywhere (PARTIAL).
    for kind, reason in ENVIRONMENT_CONDITIONAL.values():
        assert kind in (SKIPS, PARTIAL, SKIPS_ON_A_RED_SUITE)
        assert reason.startswith("C") and len(reason) > 40, reason


def test_the_census_scan_would_catch_a_new_conditional_bar(tmp_path: Path) -> None:
    """C72b. B72b. The scan, mutated -- all three signals, the propagation, and a near-miss.

    The near-miss is the half worth stating: a bar that touches neither a sibling repository nor
    the certificate must NOT be reported, or the census degrades into a list of every test in
    the repository and stops meaning anything.
    """
    (tmp_path / "test_new.py").write_text(
        "import pytest\n"
        "from upstream_certificate import GSW_BYTES\n"
        "\n\n"
        "def _gate():\n"
        "    pytest.skip('no sibling')\n"
        "\n\n"
        "def _reach():\n"
        "    return CURVECAST / 'x'\n"
        "\n\n"
        "def test_skips_through_a_helper():\n"
        '    """C90. Reaches a skip two calls down."""\n'
        "    _gate()\n"
        "\n\n"
        "def test_names_an_upstream_constant():\n"
        '    """C91. Reaches curvecast through a helper."""\n'
        "    assert _reach()\n"
        "\n\n"
        "def test_reads_the_certificate():\n"
        '    """C92. Runs everywhere, but its provenance half does not."""\n'
        "    assert GSW_BYTES\n"
        "\n\n"
        "def test_touches_neither():\n"
        '    """C93. The near-miss; it must not be reported."""\n'
        "    assert 1 == 1\n",
        encoding="utf-8",
    )

    assert conditional_bars(tmp_path) == {
        "test_names_an_upstream_constant": PARTIAL,
        "test_reads_the_certificate": PARTIAL,
        "test_skips_through_a_helper": SKIPS,
    }


# ---------------------------------------------------------------------------
# C73: the clean machine, for real
# ---------------------------------------------------------------------------


def test_a_clean_machine_skips_exactly_the_declared_bars(tmp_path: Path) -> None:
    """C73. B73, DD72. The census, checked against a run rather than against a reading of it.

    C72 is a static scan and could be wrong in the direction that matters: a bar may skip for a
    reason no AST can see. So this runs the suite in a child interpreter under
    `absent_machine`, which rebinds the sibling-repository constants in memory and makes
    `shutil.which` find nothing, and requires the skips it observes to **equal** the declaration.

    No file in the tree is touched, so this is safe to run from inside the suite. The census
    module itself is excluded from the child, which is also what keeps this from recursing.

    **Amended 2026-09-16 by `RIDER_C73_a_bar_that_reports_without_a_verdict.md` (DD104): this bar
    no longer reads the child's exit code.** It carried two claims -- *the suite passes without
    the siblings* and *the skips are exactly the declared ones* -- and the first ran first, so any
    unrelated red made this bar fail **without ever evaluating its own subject**, in a message
    blaming sibling repositories that had nothing to do with it. That is X8's `lint-imports`
    finding turned inward: an exit code cannot tell a verdict from no verdict.

    The skip report is written at `pytest_sessionfinish` whatever the exit status, so the census
    is available from a failing child too and is now asserted unconditionally. **The gate moved
    to C99**, which can tell breakage from an echo.
    """
    report = tmp_path / "skipped.txt"
    environment = dict(os.environ)
    environment[REPORT] = str(report)
    environment["PYTHONPATH"] = str(TESTS)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--tb=no",
            "-p",
            "absent_machine",
            "--ignore",
            str(Path(__file__).resolve()),
            str(TESTS),
        ],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    assert report.exists(), (
        "the absent-machine plugin wrote no report, so it did not load. The exit code is "
        f"deliberately not read here -- C99 owns that claim:\n{completed.stdout}"
    )

    observed = {
        line.split("::")[-1] for line in report.read_text(encoding="utf-8").splitlines() if line
    }
    assert observed == EXPECTED_SKIPS, {
        "skipped and not declared": sorted(observed - EXPECTED_SKIPS),
        "declared and did not skip": sorted(EXPECTED_SKIPS - observed),
    }


def test_the_clean_machine_finds_the_suite_by_where_it_is() -> None:
    """C226. DD245. C73's simulation, on a machine whose folders have other names.

    `absent_machine` used to rebind a module when its path contained the words `deskcraft` and
    `tests`. Every run of C73 happened under `C:/Users/rishi/deskcraft`, so the rule was always
    true and nothing checked it. Unpacked into a folder with any other name, the plugin rebound
    nothing, and five of the seven declared skips ran against the real sibling repositories and
    tools. So C73 went red on the one machine it exists to describe. This was found on 2026-09-29,
    while the public copy was being built in a staging folder, and reproduced before the fix in a
    copy named `reviewer_copy`.

    The plugin now takes the suite's directory from its own file. This bar hands `rebind` a suite
    in a folder called `reviewer_copy` and four modules. The two inside it, at two depths, must be
    rebound. One under a folder that *is* called `deskcraft/tests` but is not the suite, and one
    with no file, must be left alone. The old rule gets three of the four wrong.
    """
    assert SUITE == TESTS, (SUITE, TESTS)
    assert loaded_from(sys.modules[__name__])
    assert not loaded_from(pytest)

    anchor = Path(ABSENT.anchor)
    suite = anchor / "reviewer_copy" / "tests"
    sibling = anchor / "sibling"
    placed = {
        "inside": suite / "test_inside.py",
        "nested": suite / "fixtures" / "helper.py",
        "named_alike": anchor / "deskcraft" / "tests" / "test_named_alike.py",
        "no_file": None,
    }
    modules = {}
    for label, where in placed.items():
        module = types.ModuleType(label)
        if where is not None:
            module.__file__ = str(where)
        for name in UPSTREAM_CONSTANTS:
            setattr(module, name, sibling)
        for name in UPSTREAM_CANDIDATE_LISTS:
            setattr(module, name, (sibling / "tool.exe",))
        modules[label] = module

    rebind(modules.values(), suite)

    def holds(module: types.ModuleType, path: Path, candidates: tuple[Path, ...]) -> bool:
        return all(getattr(module, name) == path for name in UPSTREAM_CONSTANTS) and all(
            getattr(module, name) == candidates for name in UPSTREAM_CANDIDATE_LISTS
        )

    rebound = {label for label, m in modules.items() if holds(m, ABSENT, (ABSENT / "nothing",))}
    untouched = {label for label, m in modules.items() if holds(m, sibling, (sibling / "tool.exe",))}
    assert rebound == {"inside", "nested"}, rebound
    assert untouched == {"named_alike", "no_file"}, untouched


# ---------------------------------------------------------------------------
# C75: the certificate is read, all of it
# ---------------------------------------------------------------------------


def test_every_certificate_entry_is_read_by_a_bar() -> None:
    """C75. B75, DD69. An entry nobody reads is a stale claim wearing a gate's clothes.

    Two equalities. `ENTRIES` must name exactly the certificate's public values, so one cannot
    be added without being listed; and every listed entry must be referenced from some test
    module, so one cannot be left behind when the bar that needed it changes shape.
    """
    public = {
        name
        for name in vars(upstream_certificate)
        if name.isupper() and not name.startswith("_")
    } - {"GENERATED", "CURVECAST_COMMIT", "MEIP_COMMIT", "ENTRIES"}
    assert public == set(upstream_certificate.ENTRIES), {
        "in the module, not in ENTRIES": sorted(public - set(upstream_certificate.ENTRIES)),
        "in ENTRIES, not in the module": sorted(set(upstream_certificate.ENTRIES) - public),
    }

    readers: dict[str, list[str]] = {name: [] for name in upstream_certificate.ENTRIES}
    for path in sorted(TESTS.glob("test_*.py")):
        if path.name == Path(__file__).name:
            continue
        used = {node.id for node in ast.walk(ast.parse(_read(path))) if isinstance(node, ast.Name)}
        for name in readers:
            if name in used:
                readers[name].append(path.name)

    unread = sorted(name for name, found in readers.items() if not found)
    assert not unread, f"these certificate entries are read by no bar: {unread}"

    assert upstream_certificate.GENERATED == "2026-09-15"
    assert len(upstream_certificate.CURVECAST_COMMIT) >= 7
    assert len(upstream_certificate.MEIP_COMMIT) >= 7


# ---------------------------------------------------------------------------
# C99: the gate C73 used to carry, with a verdict it can actually reach
# ---------------------------------------------------------------------------


def clean_machine_verdict(
    failed_without_siblings: frozenset[str], failed_here: frozenset[str]
) -> tuple[str, tuple[str, ...]]:
    """Classify a failing clean-machine run: `clean`, `broken`, or `echo`.

    Three outcomes, and the third is why this function exists:

    * nothing failed without the siblings -- **clean**, the property holds;
    * something failed there and passes here -- **broken**, the finding C99 exists for;
    * everything that failed there fails here too -- **echo**, and there is **no verdict**. The
      suite does not pass anywhere, so the clean-machine property was not falsified by this run,
      and reporting it as falsified would blame a sibling repository that had no part in it.

    Pure, so C99b can drive all three without a broken tree to break.
    """
    if not failed_without_siblings:
        return "clean", ()
    broken = failed_without_siblings - failed_here
    if broken:
        return "broken", tuple(sorted(broken))
    return "echo", tuple(sorted(failed_without_siblings))


def fails_with_the_siblings_present(node_ids: frozenset[str]) -> frozenset[str]:
    """Which of `node_ids` also fail on this machine. Empty input runs nothing."""
    if not node_ids:
        return frozenset()
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=no", *sorted(node_ids)],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": str(TESTS)},
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    return frozenset(
        line[len("FAILED ") :].split(" ")[0]
        for line in completed.stdout.splitlines()
        if line.startswith("FAILED ")
    )


def test_a_clean_machine_runs_the_suite_green_or_says_why_it_cannot_tell(tmp_path: Path) -> None:
    """C99. B99, DD105. `RIDER_C73_a_bar_that_reports_without_a_verdict.md` §2.2.

    The gate C73 carried until today: **the suite passes on a machine with neither sibling
    repository**, which is the only machine a reviewer unpacking `git archive HEAD` has.

    It is a separate bar because it is a separate claim, and because C73 could not reach a verdict
    on its own subject while carrying this one. And it reads the child's **failing node ids**
    rather than its exit code, for the reason X8 recorded against `lint-imports`: an exit code
    cannot tell a verdict from no verdict.

    So a failing child is split. Ids that fail without the siblings and **pass** with them are
    clean-machine breakage, and are named. Ids that fail **both** ways are echoes of a suite that
    is already red -- nothing has been falsified, so this **skips** rather than failing in the
    siblings' name. Before this, `n` red bars produced `n + 1` reds and three documents in a row
    got that arithmetic wrong.

    **Mutation:** C99b drives the classifier through all three outcomes and the mixed case,
    because two of the three cannot be produced without deliberately breaking the tree.
    """
    failures = tmp_path / "failed.txt"
    environment = dict(os.environ)
    environment[REPORT] = str(tmp_path / "skipped.txt")
    environment[FAILURE_REPORT] = str(failures)
    environment["PYTHONPATH"] = str(TESTS)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--tb=no",
            "-p",
            "absent_machine",
            "--ignore",
            str(Path(__file__).resolve()),
            str(TESTS),
        ],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    assert failures.exists(), (
        "the absent-machine plugin wrote no failure report, so it did not load:\n"
        f"{completed.stdout}"
    )

    failed_there = frozenset(
        line for line in failures.read_text(encoding="utf-8").splitlines() if line
    )
    assert (completed.returncode == 0) == (not failed_there), (
        "the child's exit code and its failure report disagree, so one of them is not "
        f"describing the run: exit {completed.returncode}, {len(failed_there)} failures"
    )

    verdict, names = clean_machine_verdict(
        failed_there, fails_with_the_siblings_present(failed_there)
    )
    if verdict == "echo":
        pytest.skip(
            "no verdict: every bar that failed without the sibling repositories fails with them "
            "too, so the suite is red for a reason that has nothing to do with a reviewer's "
            "machine. Fix those and this bar speaks again: " + ", ".join(names)
        )
    assert verdict == "clean", (
        "these bars pass with the sibling repositories present and fail without them, so the "
        "suite is not green on the only machine a reviewer has: " + ", ".join(names)
    )


def test_the_clean_machine_verdict_tells_breakage_from_an_echo() -> None:
    """C99b. C99, mutated -- through all three outcomes, and the boundary between two of them.

    The classifier is the whole of C99's judgement and two of its three answers cannot be produced
    without deliberately breaking the tree, so it is driven directly.

    The case worth stating is the **mixed** one: one bar broken by the absent siblings and one bar
    red anyway. A classifier answering `echo` whenever *any* failure was shared would hide a
    genuine clean-machine break behind an unrelated red -- which is the defect this rider removed,
    re-appearing one level down.
    """
    assert clean_machine_verdict(frozenset(), frozenset()) == ("clean", ())
    assert clean_machine_verdict(frozenset(), frozenset({"a"})) == ("clean", ())

    assert clean_machine_verdict(frozenset({"a"}), frozenset()) == ("broken", ("a",))
    assert clean_machine_verdict(frozenset({"a"}), frozenset({"b"})) == ("broken", ("a",))

    assert clean_machine_verdict(frozenset({"a"}), frozenset({"a"})) == ("echo", ("a",))
    assert clean_machine_verdict(frozenset({"a", "b"}), frozenset({"a", "b"})) == (
        "echo",
        ("a", "b"),
    )

    # Mixed: `a` is genuine breakage and `b` is an echo. The genuine one must survive the echo.
    assert clean_machine_verdict(frozenset({"a", "b"}), frozenset({"b"})) == ("broken", ("a",))
#: The classifier's whole input, as C101 expects to find it. Read from the signature rather than
#: restated here, because a domain written down twice is a domain that drifts -- which is the
#: subject of the rider that added this bar.
_ID_ONLY_DOMAIN = ("frozenset[str]", "frozenset[str]")


def classifier_domain(source: str, name: str = "clean_machine_verdict") -> tuple[str, ...]:
    """The annotations of `name`'s parameters, in order, exactly as written.

    Refuses any signature that could carry an argument this tuple would not show -- `*args`,
    `**kwargs`, keyword-only or positional-only parameters, or an unannotated one. A domain that
    can be widened without changing what this returns is not a domain a bar can hold.
    """
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            args = node.args
            assert not (args.vararg or args.kwarg or args.kwonlyargs or args.posonlyargs), (
                f"`{name}` can be handed arguments its parameter list does not name, so its "
                "domain cannot be read off the signature"
            )
            assert all(item.annotation is not None for item in args.args), (
                f"`{name}` has an unannotated parameter, so what it carries is not stated"
            )
            return tuple(ast.unparse(item.annotation) for item in args.args)
    raise AssertionError(f"`{name}` is not defined in the source handed to this scanner")


def test_the_clean_machine_classifier_is_handed_node_ids_and_nothing_else() -> None:
    """C101. B101, DD108. `RIDER_two_claims_that_something_could_not_be_done.md`.

    `RIDER_C73_a_bar_that_reports_without_a_verdict.md` closed by stating a residual it called
    **"not solved, and not solvable"**: a genuine clean-machine breakage *coinciding with* an
    unrelated red, reported as an echo. **That claim is false, and it was false in the commit that
    published it.** Two different bars are separated correctly -- C99 subtracts the sets, so a
    break that passes with the siblings survives any number of unrelated reds -- and C99b's mixed
    case asserts it directly, under a comment saying so in words.

    The residual that is really there is **one bar failing both ways for two different reasons**.
    Then the two sets are the same single id, the subtraction is empty, and a clean-machine break
    hiding inside that bar is classified as an echo.

    That one is undecidable **at this interface**, and this bar is what makes "at this interface"
    a checked statement rather than a second unmeasured impossibility claim: the classifier is
    handed node ids, and a *cause* is not in its domain. Widen the domain to carry failure reasons
    and this bar goes red, which is the point -- the annotation on that rider must then be re-read,
    because the limit it records would no longer hold.

    **Mutation:** a widened signature and an unreadable one, inline. The boundary behaviours are
    fixed here too -- different ids separated, identical ids not -- the first cited from C99b
    rather than re-proved, the second being the residual itself.
    """
    domain = classifier_domain(_read(Path(__file__)))
    assert domain == _ID_ONLY_DOMAIN, {
        "the classifier now takes": domain,
        "it took": _ID_ONLY_DOMAIN,
        "why it matters": (
            "the residual recorded against C99 -- one node id failing both ways for two different "
            "reasons -- is undecidable only while a cause is absent from this domain. If it is no "
            "longer absent, re-read the correction annotated onto that rider's section 3"
        ),
    }

    assert clean_machine_verdict(frozenset({"a", "b"}), frozenset({"b"})) == ("broken", ("a",))
    assert clean_machine_verdict(frozenset({"a"}), frozenset({"a"})) == ("echo", ("a",))

    widened = (
        "def clean_machine_verdict(\n"
        "    failed_without_siblings: frozenset[str],\n"
        "    failed_here: frozenset[str],\n"
        "    reasons: dict[str, str],\n"
        ") -> tuple[str, tuple[str, ...]]:\n"
        "    return ('echo', ())\n"
    )
    assert classifier_domain(widened) != _ID_ONLY_DOMAIN, (
        "a signature carrying failure reasons read as the id-only domain, so this bar cannot see "
        "the widening it exists to catch"
    )

    with pytest.raises(AssertionError, match="does not name"):
        classifier_domain(
            "def clean_machine_verdict(*node_ids: frozenset[str]) -> tuple[str, tuple[str, ...]]:\n"
            "    return ('echo', ())\n"
        )
