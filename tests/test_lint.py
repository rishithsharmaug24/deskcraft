"""The lint gate. D4, decisions DD57-DD58, bars C58-C58b.

**This is not D4.** It rides along with it by the owner's direction, because
`pyproject.toml` has declared `ruff>=0.6` as a dev dependency since D1 and nothing has ever
run it, and curvecast has had the equivalent floor since its own scaffold. It is kept in its
own module so the D4 verdict and this can be read apart.

**It holds at zero, not at a baseline** (DD57). curvecast's `classify_ruff` carries
`RUFF_BASELINE` at 29 findings and fails only on growth, because 29 predated the gate there.
This repository had **one** -- an unused `deskcraft.book.Leg` in `test_book_types.py`, left by
D5 -- and it is deleted in the same commit as this file, so the gate can be the stronger form.
Any finding at all is red.

**It is a test because a `scripts/` directory here could not run one** (DD58). D3a widened the
boundary scan so that a directory nobody has named arrives under the **strict** policy, every
ban included, so a `scripts/run_gates.py` in this repository could not invoke pytest or ruff
without turning `C3` red. `tests/` is the one root with `HARNESS` policy, where execution is
lifted; `C5` has spawned a child interpreter from here since D1.

**`C58b` exists because curvecast's gate once went green on a ruff that never ran.** Its
classifier records the date: on 2026-09-09 a restart logged the session off mid-sweep, stdout
came back empty, empty stdout defaulted to `[]`, and the gate reported *"0 findings, down from
29 -- shrink RUFF_BASELINE"*. So this pair does not merely assert a clean tree; the mutation
plants a known finding and requires the same invocation, with this repository's pinned
selection, to see it.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from test_deskcraft_boundary import MEIP, REPO_ROOT

PYPROJECT = REPO_ROOT / "pyproject.toml"

#: Where a ruff binary is looked for, in order. The first is the one curvecast's
#: `scripts/run_gates.py` resolves for `curvecast:ruff` -- the same binary, so a finding here
#: and a finding there are the same finding. It is not installed on the interpreter this suite
#: runs on, which is why there is a search rather than `python -m ruff`.
RUFF_CANDIDATES = (
    MEIP / ".venv" / "Scripts" / "ruff.exe",
    MEIP / ".venv" / "bin" / "ruff",
)


def _ruff() -> Path:
    for candidate in RUFF_CANDIDATES:
        if candidate.exists():
            return candidate
    found = shutil.which("ruff")
    if found:
        return Path(found)
    pytest.skip(
        "no ruff binary resolved; tried "
        + ", ".join(str(path) for path in RUFF_CANDIDATES)
        + " and PATH"
    )


def _check(target: Path, *, config: Path | None = None) -> list[dict]:
    """Run ruff over `target` and return its findings, refusing a run that did not check.

    ruff's exit code is the contract: 0 clean, 1 findings, anything else did not check -- 2 for
    a config or CLI error, an NTSTATUS for a process Windows would not start. And a clean
    `--output-format json` run prints `[]`, never nothing. Both are asserted here rather than
    defaulted, which is exactly the distinction curvecast's classifier had to learn.
    """
    command = [str(_ruff()), "check", str(target), "--output-format", "json"]
    if config is not None:
        command += ["--config", str(config)]
    completed = subprocess.run(
        command, cwd=REPO_ROOT, capture_output=True, text=True, timeout=300, check=False
    )
    assert completed.returncode in (0, 1), (
        f"ruff did not complete (exit {completed.returncode}); it checked nothing, and a gate "
        f"that reports no findings for that reason is worse than no gate.\n{completed.stderr}"
    )
    assert completed.stdout.strip(), "ruff printed nothing; a clean run prints `[]`"
    return json.loads(completed.stdout)


def _rendered(findings: list[dict]) -> list[str]:
    return sorted(
        f"{Path(item['filename']).name}:{item['location']['row']} {item['code']}"
        for item in findings
    )


def test_the_tree_carries_no_ruff_finding() -> None:
    """C58. B58, DD57. An equality at zero, not a baseline that can only fail on growth.

    The selection is pinned in `pyproject.toml` rather than inherited from ruff's defaults, so
    the gate cannot move when the defaults do. It is today's default selection written down,
    which is why pinning it changed nothing on the day it was pinned.
    """
    text = PYPROJECT.read_text(encoding="utf-8")
    assert "[tool.ruff.lint]" in text, "the pinned selection has left pyproject.toml"

    findings = _check(REPO_ROOT)
    assert findings == [], _rendered(findings)


def test_the_ruff_invocation_would_see_a_finding(tmp_path: Path) -> None:
    """C58b. B58b, DD58. The mutation: a planted violation, through the same invocation.

    Pointed at a file outside the tree and given this repository's config explicitly, so the
    pinned selection is what judges the plant. A guard that has never fired is a guard held on
    trust, and this one's upstream twin fired for real.
    """
    planted = tmp_path / "planted.py"
    planted.write_text("import os\n", encoding="utf-8")

    findings = _check(planted, config=PYPROJECT)
    assert _rendered(findings) == ["planted.py:1 F401"], findings

    clean = tmp_path / "clean.py"
    clean.write_text("VALUE = 1\n", encoding="utf-8")
    assert _check(clean, config=PYPROJECT) == []
