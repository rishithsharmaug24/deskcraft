"""The import-contract gate. Carried item X8, decision DD71, bars C74-C74b.

**This is not a package.** It rides along, in the shape D4's row records for the lint gate --
*"C58/C58b, the lint gate, which rides along and is not D4."*

**Why it exists.** Every package row since D1 quotes `lint-imports` output; D6's says *"19
files, 47 dependencies, 2 kept, 0 broken."* Until this file, **no test in this repository ran
it.** One boundary bar reads the contracts out of `[tool.importlinter]` and asserts things about
their shape, and C7 scans the direction the tool structurally cannot see -- but the tool itself
was a hand-run, and every "0 broken" in every row was a number a human typed.

That is worse than a skip. A skip appears in pytest's output; a gate that is never invoked
leaves no evidence at all. And this one guards the boundary the whole premise rests on: no
egress, no execution, no broker SDK, and no edge running backwards into curvecast or meip.

**The finding that shaped the bar.** `lint-imports` exits **1** both when a contract is broken
and when the configuration is refused before anything is evaluated. Exit code alone therefore
cannot tell a real verdict from no verdict -- which is exactly the failure this repository has
already had: a dotted external module sat in `[tool.importlinter]` from D1 until 2026-09-09,
aborted every run, and took the two expressible contracts down with it, so the gate returned no
verdict on anything for nine days.

So the load-bearing assertion here is not the exit code. It is that the summary line **exists**:
a configuration abort prints no `Contracts: N kept, M broken.` at all, and a parser that defaults
a missing count to zero reports a clean gate for a gate that did not run. C58b was written after
curvecast's ruff gate went green on a ruff that never ran; this is the same lesson, found again
in a second tool, and C74b plants both failures rather than only the interesting one.

**DD132, 2026-09-22 -- what the gate resolves.** `lint-imports.exe` is a pip-generated
console script: an unsigned, per-venv launcher stub that does nothing but call
`importlinter.cli:lint_imports_command`. Application Control refuses *it* -- Code Integrity
3077 names `meip/.venv/Scripts/lint-imports.exe` -- while allowing both
the interpreter sitting beside it and the `importlinter` library that interpreter imports.
The stub still **exists**, so a resolver that selects on existence hands `subprocess.run` a
file it cannot start, and the `OSError` lands before any assertion runs. Both bars then go
red for an environment reason, and the boundary above goes back to being a number a human
typed -- the state X8 was opened to end, reached the long way round.

So resolution asks the binding question, which is not *does a launcher exist* but **can this
tool be run at all**: each candidate is probed with `--help`, and the first one that starts
and answers is used. The interpreter plus the declared entry point is the same tool, the
same version and the same configuration; only the launcher differs. What the fallback must
never become is a `pytest.skip` -- a gate that reports nothing while looking like it
reported something is precisely the C58b failure, and finding it a third time would not
make it a new one. The skip survives for one case only, the case it was written for: no
route to the tool at all.
"""

from __future__ import annotations

import functools
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from test_deskcraft_boundary import MEIP, REPO_ROOT

PYPROJECT = REPO_ROOT / "pyproject.toml"
SRC = REPO_ROOT / "src"

#: Where a `lint-imports` binary is looked for, in order, then `PATH`. Same arrangement as the
#: lint gate's `RUFF_CANDIDATES` and for the same reason: it is not installed on the interpreter
#: this suite runs on. **Unlike ruff, this tool has no pinned selection** -- the contracts are
#: the selection, and they live in this repository's own `pyproject.toml`, so the gate cannot
#: drift with the tool's defaults either.
LINT_IMPORTS_CANDIDATES = (
    MEIP / ".venv" / "Scripts" / "lint-imports.exe",
    MEIP / ".venv" / "bin" / "lint-imports",
)

#: The same tool reached without its launcher, tried after the launchers and before the skip.
#: See DD132 in the module docstring: the console script is what Application Control refuses,
#: not the interpreter beside it and not the library that interpreter imports.
INTERPRETER_CANDIDATES = (
    MEIP / ".venv" / "Scripts" / "python.exe",
    MEIP / ".venv" / "bin" / "python",
)

#: `import_linter-1.10.0.dist-info/entry_points.txt` verbatim:
#: `lint-imports = importlinter.cli:lint_imports_command`. Quoting the console script's own
#: declaration is what makes the fallback the same tool rather than a second opinion about it.
ENTRY_POINT = "from importlinter.cli import lint_imports_command; lint_imports_command()"

#: An equality, not a floor. Two contracts are declared and both must be kept; a third arriving
#: unnoticed, or one of these two quietly leaving, is the thing a floor would not see.
EXPECTED_KEPT = 2
EXPECTED_BROKEN = 0

#: The contracts by name, so that "2 kept" cannot be satisfied by two different contracts.
EXPECTED_CONTRACTS = ("No broker SDK, ever", "No egress and no execution")

#: A floor, deliberately: the engine grows, and D6's row recorded 19 files and 47 dependencies.
#: What this catches is the graph collapsing -- a `PYTHONPATH` that resolves nothing analyses
#: almost nothing and keeps every contract vacuously.
MINIMUM_FILES = 15

_SUMMARY = re.compile(r"Contracts:\s+(\d+)\s+kept,\s+(\d+)\s+broken\.")
_ANALYSED = re.compile(r"Analyzed\s+(\d+)\s+files,\s+(\d+)\s+dependencies\.")


def _candidates() -> list[tuple[str, ...]]:
    """Every argv that might be this tool, launchers first and the entry point last."""
    argvs = [(str(path),) for path in LINT_IMPORTS_CANDIDATES if path.exists()]
    found = shutil.which("lint-imports")
    if found:
        argvs.append((found,))
    argvs += [
        (str(path), "-c", ENTRY_POINT) for path in INTERPRETER_CANDIDATES if path.exists()
    ]
    return argvs


@functools.lru_cache(maxsize=1)
def _resolved() -> tuple[str, ...] | None:
    """The first candidate that actually starts and answers, or `None` if there is no route.

    The probe is `--help`, which is the cheapest question that distinguishes the three states
    this has to tell apart: a launcher that cannot be started at all (`OSError`, which is the
    Application Control case), something that starts but is not this tool, and the tool. It is
    deliberately not a contract run -- resolution must not be able to produce a verdict, or a
    verdict could come from resolution.
    """
    for argv in _candidates():
        try:
            probe = subprocess.run(
                [*argv, "--help"],
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
        except OSError:
            continue
        if probe.returncode == 0 and "--config" in probe.stdout:
            return argv
    return None


def _lint_imports() -> tuple[str, ...]:
    argv = _resolved()
    if argv is None:
        pytest.skip(
            "no lint-imports run resolved; tried "
            + ", ".join(str(path) for path in LINT_IMPORTS_CANDIDATES)
            + ", PATH, and the entry point on "
            + ", ".join(str(path) for path in INTERPRETER_CANDIDATES)
        )
    return argv


def _run(config: Path) -> tuple[int, str]:
    """Run the contracts under `config` and return the exit code and stdout.

    `PYTHONPATH` is required because import-linter imports the package to build its graph and
    there is no installed distribution here. Passed through the environment rather than assumed:
    a run that cannot import `deskcraft` analyses nothing and keeps every contract for the worst
    possible reason.
    """
    environment = dict(os.environ, PYTHONPATH=str(SRC))
    completed = subprocess.run(
        [*_lint_imports(), "--config", str(config)],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    assert completed.returncode in (0, 1), (
        f"lint-imports did not complete (exit {completed.returncode}); it evaluated nothing, "
        f"and a gate that reports no broken contract for that reason is worse than no gate.\n"
        f"{completed.stderr}"
    )
    assert completed.stdout.strip(), "lint-imports printed nothing at all"
    return completed.returncode, completed.stdout


def _summary(output: str) -> tuple[int, int] | None:
    """`(kept, broken)`, or `None` when the tool printed no verdict.

    `None` is the case that matters and the reason this returns an option rather than a pair of
    zeros. A configuration abort prints no summary line, and a caller that reads a missing count
    as zero broken reports a clean gate for a gate that never ran.
    """
    match = _SUMMARY.search(output)
    return (int(match.group(1)), int(match.group(2))) if match else None


def test_the_import_contracts_are_kept_by_the_tool_that_checks_them() -> None:
    """C74. B74, DD71. X8: the first time any bar has run this gate.

    Every "2 kept, 0 broken" in every package row since D1 was hand-typed until this ran. The
    counts are held at equality and the contracts are matched by name, because "two kept" is
    satisfied by any two contracts, including two that were never meant to be here.
    """
    code, output = _run(PYPROJECT)

    summary = _summary(output)
    assert summary is not None, (
        "lint-imports printed no `Contracts:` line. It exits 1 for a refused configuration as "
        "well as for a broken contract, so this -- not the exit code -- is what distinguishes "
        "a verdict from no verdict:\n" + output
    )
    assert summary == (EXPECTED_KEPT, EXPECTED_BROKEN), output
    assert code == 0, f"exit {code} with a clean summary; the two disagree\n{output}"

    for name in EXPECTED_CONTRACTS:
        assert f"{name} KEPT" in output, f"{name!r} is not reported kept\n{output}"

    analysed = _ANALYSED.search(output)
    assert analysed is not None, f"lint-imports reported no graph size\n{output}"
    files, dependencies = int(analysed.group(1)), int(analysed.group(2))
    assert files >= MINIMUM_FILES, (
        f"only {files} files analysed; the graph has collapsed and every contract is being "
        f"kept vacuously"
    )
    assert dependencies > files, f"{dependencies} dependencies over {files} files\n{output}"


def test_the_import_contract_run_would_see_both_failures(tmp_path: Path) -> None:
    """C74b. B74b, DD71. The mutation, planted twice -- a break, and a run that never happened.

    A guard that has never fired is a guard held on trust, and both of this one's failures have
    fired for real: curvecast's ruff gate went green on a ruff that never ran (2026-09-09), and
    this repository's own third contract aborted every run for nine days.

    The second plant is the one worth the file. It reproduces that exact configuration -- a
    dotted external module -- and requires it to be distinguishable from a clean run *despite
    sharing an exit code with a broken contract*.
    """
    broken = tmp_path / "broken.toml"
    broken.write_text(
        "[tool.importlinter]\n"
        'root_package = "deskcraft"\n'
        "include_external_packages = true\n"
        "\n"
        "[[tool.importlinter.contracts]]\n"
        'name = "A module the engine genuinely imports"\n'
        'type = "forbidden"\n'
        'source_modules = ["deskcraft"]\n'
        'forbidden_modules = ["math"]\n',
        encoding="utf-8",
    )
    code, output = _run(broken)
    assert code == 1
    assert _summary(output) == (0, 1), output
    assert "deskcraft is not allowed to import math" in output, output

    aborted = tmp_path / "aborted.toml"
    aborted.write_text(
        "[tool.importlinter]\n"
        'root_package = "deskcraft"\n'
        "include_external_packages = true\n"
        "\n"
        "[[tool.importlinter.contracts]]\n"
        'name = "The shape that returned no verdict for nine days"\n'
        'type = "forbidden"\n'
        'source_modules = ["deskcraft"]\n'
        'forbidden_modules = ["meip' + '.lpal"]\n',
        encoding="utf-8",
    )
    code, output = _run(aborted)
    assert code == 1, "a refused configuration exits 1, exactly as a broken contract does"
    assert _summary(output) is None, (
        "a refused configuration printed a `Contracts:` summary; the distinction this bar "
        "rests on has gone\n" + output
    )
    assert "not valid" in output, output
