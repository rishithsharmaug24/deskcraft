# Tooling — the four gates, and the exact software that runs them

*Recorded 2026-09-15, at `740f97a`. Closes carried item X9 in `docs/CARRIED_ITEMS.md`.*

Two of this repository's four gates run from binaries that live in **another repository's virtual
environment**, and MEIP is under a standing rule that it must never be modified. Nothing recorded
where those binaries came from or what version produced the numbers in the package rows. This file
does, so the gate is rebuildable by someone who has only `git archive HEAD`.

---

## 1. The four gates

| gate | what it holds | how it is invoked | enforced by a bar? |
|---|---|---|---|
| **pytest** | Every bar C1 onward | `python -m pytest -q` from the repository root | it *is* the suite |
| **ruff** | Zero findings — an equality at zero, not a baseline | a test resolves the binary and runs it as a subprocess | **yes** |
| **import-linter** | The two import contracts | a test resolves the binary and runs it as a subprocess | **yes — C74/C74b, added 2026-09-15** |
| **the absent-machine census** | That an environment-conditional bar is declared rather than silent | a test rebinds the sibling paths and re-runs the suite in a child | **yes — C72/C72b/C73, added 2026-09-15** |

**All four now run on every `pytest` invocation.** Gates three and four were the two carried
items this file was written to record, X8 and X1, and both closed on 2026-09-15 by the rider in
`RIDER_environment_census_and_import_contract.md`. The original text of this section — *"gate
three does not run unless a person runs it; gate four is not built"* — is kept in the register's
§X1 and §X8 rather than deleted, because what those two gates found when they were finally run is
the reason to keep writing them.

---

## 2. Exact versions, measured today

| component | version | where |
|---|---|---|
| **Production interpreter** | `Python 3.12.10 (tags/v3.12.10:0cc8128, Apr 8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)]` | `C:/Users/rishi/AppData/Local/Programs/Python/Python312/python.exe` |
| **pytest** | 9.1.1 | on the production interpreter |
| **numpy** | 2.4.6 | on the production interpreter; arrived at D6 |
| **ruff** | 0.15.22 | `C:/Users/rishi/meip/.venv/Scripts/ruff.exe` |
| **import-linter** | 1.10.0 | `C:/Users/rishi/meip/.venv/Scripts/lint-imports.exe`, on a 3.12.10 venv |

The suite runs on the **production interpreter**, not on a virtual environment. There is no
`.venv` in this repository and none is wanted: `tests/conftest.py` puts `src/` on the path, which
is how imports work here, and that is a deliberate property rather than an accident of setup.

---

## 3. Why the binaries live next door, and what happens when they do not

**ruff is resolved through a candidate list, and the list ends in `PATH`.** The lint gate looks in
MEIP's venv first — deliberately, because that is the same binary curvecast's own gate runner
resolves, so a finding here and a finding there are the same finding — then falls back to
`shutil.which("ruff")`. It is not installed on the interpreter the suite runs on, which is why
there is a search rather than `python -m ruff`.

**So ruff is not in fact a single point of failure.** Any `pip install ruff` on any interpreter
restores the gate, and restores it *exactly*, because the rule selection is pinned in
`[tool.ruff.lint]` in `pyproject.toml` rather than inherited from ruff's defaults. The gate cannot
move when ruff's defaults move. Pinning it changed nothing on the day it was pinned, which is the
point.

If no ruff resolves at all, the two lint bars **skip**. They are two of the fourteen counted in
carried item X1.

**import-linter now has both** (2026-09-15). C74 resolves it through the same candidate list
ending in `PATH`, so the tool is no more a single point of failure than ruff is.

**And it needed a different mutation than ruff's.** ruff's exit code is the contract — 0 clean, 1
findings, anything else did not check. `lint-imports` exits **1 for a refused configuration as
well as for a broken contract**, so the exit code cannot distinguish a verdict from no verdict.
What distinguishes them is whether a `Contracts: N kept, M broken.` line was printed at all. C74b
plants both failures; see the register's §X8.

---

## 4. The import contract, and its exact invocation

Run from the repository root:

    PYTHONPATH=C:/Users/rishi/deskcraft/src \
      C:/Users/rishi/meip/.venv/Scripts/lint-imports.exe --config pyproject.toml

Output as of `740f97a`:

    Analyzed 19 files, 47 dependencies.

    No broker SDK, ever            KEPT
    No egress and no execution     KEPT

    Contracts: 2 kept, 0 broken.

`PYTHONPATH` is required because import-linter imports the package to build its graph and there is
no installed distribution. The contracts themselves are written at D1, in `[tool.importlinter]`,
**before any code existed that could violate them** — a contract added afterwards is a contract
written to fit whatever was built.

**Never run `uv sync` against MEIP's environment.** MEIP must not be modified; these binaries are
read, borrowed and nothing else. Use `uv run --no-sync` if a MEIP-side invocation is ever needed.

---

## 5. Why there is no `scripts/` directory

This repository cannot have one, and that is enforced rather than preferred.

D3a widened the boundary scan so that a directory nobody has named arrives under the **strict**
policy — every ban included: egress, execution, environment, broker SDK, imperative naming, LLM
edge. A `scripts/run_gates.py` here could therefore not invoke pytest or ruff without turning the
execution ban red. `tests/` is the one root carrying the **harness** policy, where execution is
lifted, and a bar has spawned a child interpreter from there since D1.

**That is why the lint gate is a test.** It is not a stylistic choice: a gate runner in this
repository is unconstructible, so any gate that must execute something lives in `tests/` or is
run by hand. Both remaining gaps in §1 follow from that constraint, and both resolve the same way —
as bars in `tests/`, not as a script.

---

## 6. Rebuilding the toolchain from scratch

For someone who has the archive and neither sibling repository:

1. **Interpreter.** CPython 3.12.10, 64-bit. Any 3.12.x should work; 3.12.10 is what produced
   every number in the package rows.
2. **Suite dependencies.** `pytest` 9.1.1 and `numpy` 2.4.6. The dev extras in `pyproject.toml`
   declare the floors; the versions above are the exact ones measured.
3. **ruff.** `pip install ruff==0.15.22`. Once it is on `PATH` the lint gate resolves it through
   the fallback and runs with this repository's pinned selection. A newer ruff is safe for the
   same reason — the selection is pinned — but the finding count is only guaranteed reproducible
   at 0.15.22.
4. **import-linter.** `pip install import-linter==1.10.0`, then §4's invocation with `PYTHONPATH`
   pointing at this repository's `src/`.
5. **Expect exactly seven skips.** Without curvecast and meip on disk the suite reports
   **87 passed, 7 skipped** rather than 94 passed — three live drift watches that cannot be
   satisfied off-machine by construction, and four tool gates that `pip install ruff
   import-linter` restores. **The seven is the stable number here, not the 87:** the passed count
   moves with every package (81 → 83 at the register gate, 83 → 94 at D7a) and the skip count has
   not moved since it was declared, because a package whose bars touch no sibling repository adds
   nothing conditional. Any other skip count is a bug: C72 declares the seven and C73 re-runs the
   suite under a simulated clean machine to check them. Before 2026-09-15 this line read
   *"61 passed, 14 skipped"* and nothing held it.

---

## 7. What this file could get wrong

- **Nothing verifies the version table.** §2's versions are recorded, not asserted by a bar. A
  toolchain upgrade would leave this file stale and nothing would go red. Mechanising it is cheap
  — a bar could compare the resolved binary's `--version` against a recorded constant — but it
  has not been done, and claiming it here would be worse than recording the gap. The *gates*
  themselves are now all four asserted; it is only this file's account of which binary ran them
  that is still prose.
- **The paths are this machine's.** `C:/Users/rishi/...` is where the siblings live here. A
  reviewer's rebuild goes through §6 and the `PATH` fallback instead, and never needs them.
- **"2 kept, 0 broken" in §4 was a hand-run, and so was every occurrence of that phrase in every
  package row up to D6.** That was X8, and it was the reason this file existed at all. C74 has now
  run it and returned the same answer, so the rows were right — they were just not evidence. Rows
  written from here quote a number a bar produced.
