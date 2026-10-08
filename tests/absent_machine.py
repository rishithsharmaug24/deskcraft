"""Simulate a reviewer's machine: no curvecast, no meip, no resolved binaries.

A pytest plugin, loaded with `-p absent_machine`. It rebinds the module-level sibling-repository
path constants after collection, so every bar takes its own absent branch, and it makes
`shutil.which` find nothing so the tool gates cannot resolve either. **No file in the tree is
touched and no environment variable is set** -- the simulation lives entirely in the child
process's memory, which is why it is safe to run from inside the suite.

This file exists because the instrument mattered more than the number. The count it produced --
fourteen of seventy-five bars silent, eighteen per cent of the suite -- was not reproducible
from a description, and a measurement nobody else can repeat is an assertion. C73 runs it.

Distribution here is `git archive HEAD` and nothing else, so a reviewer unpacking the archive
has neither sibling repository. Before this plugin the suite reported green while the bars that
make this repository's claims checkable had not run at all.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

#: The module-level constants that name a sibling repository, and the two candidate lists that
#: name a binary inside one. Declared here rather than in the census so that the simulation and
#: the bar that checks it read the same list -- two lists that must agree is a third thing to
#: keep in step, and it is always the copy that drifts.
UPSTREAM_CONSTANTS = (
    "CURVECAST",
    "MEIP",
    "CURVECAST_FIXTURE",
    "FACTOR_SPACE",
    "GSW_SOURCE",
    "CASCADE",
    "OPTCRAFT",
)

#: Candidate lists: a tuple of paths, replaced by a tuple of one path that cannot exist.
#:
#: **`INTERPRETER_CANDIDATES` added 2026-09-22 by DD132**, and it is worth saying why rather than
#: just adding it. The constant above warns that a second list which must agree is a third thing
#: to keep in step and that it is always the copy that drifts. DD132 gave the import-contract
#: gate a fallback route to the same tool -- a third list -- and this list did not know about it,
#: so on the simulated clean machine the two bars reached the real sibling interpreter and ran
#: where the census declares they skip. **C73 caught it in the same sweep that introduced it**,
#: which is the whole reason this runs against a child process instead of a reading of one.
UPSTREAM_CANDIDATE_LISTS = ("RUFF_CANDIDATES", "LINT_IMPORTS_CANDIDATES", "INTERPRETER_CANDIDATES")

#: Somewhere no repository is, on any machine this could run on.
ABSENT = Path("C:/__absent__") if sys.platform == "win32" else Path("/__absent__")

#: The suite's own directory, found from where this file is and not from what any folder is
#: called. **Added 2026-09-29 by DD245.** The plugin used to rebind a module when its path
#: contained the words `deskcraft` and `tests`, which is a statement about the author's disk. A
#: reviewer who unpacked the archive into a folder with any other name got a simulation that
#: rebound nothing, so every bar reached the real siblings and C73 went red on the one machine it
#: exists to describe. The same test also matched any path with both words in it that was not
#: this suite.
SUITE = Path(__file__).resolve().parent

#: When set, the node id of every skipped test is written here at the end of the session, one
#: per line. Parsing `-rs` output would give a file and a line number; a node id is what the
#: census declares, and comparing the thing declared to the thing observed is the point.
REPORT = "DESKCRAFT_ABSENT_REPORT"

#: When set, the node id of every *failing* test is written here the same way. Added 2026-09-16
#: by `RIDER_C73_a_bar_that_reports_without_a_verdict.md` (DD105): C73 read the child's exit code
#: and so could not tell "the suite is broken without the siblings" from "two unrelated bars are
#: red", which is X8's `lint-imports` finding turned inward. **A node id can be re-run; an exit
#: code cannot be asked a second question.**
FAILURE_REPORT = "DESKCRAFT_ABSENT_FAILURES"

_skipped: list[str] = []
_failed: list[str] = []


def loaded_from(module, suite: Path = SUITE) -> bool:
    """Whether `module` was loaded from a file inside `suite`, at any depth."""
    filename = getattr(module, "__file__", None)
    if not filename:
        return False
    try:
        return Path(filename).resolve().is_relative_to(suite)
    except (OSError, ValueError):
        return False


def rebind(modules, suite: Path = SUITE) -> None:
    """Point every sibling-repository constant in the suite's own modules at `ABSENT`."""
    for module in modules:
        if not loaded_from(module, suite):
            continue
        for name in UPSTREAM_CONSTANTS:
            if hasattr(module, name):
                setattr(module, name, ABSENT)
        for name in UPSTREAM_CANDIDATE_LISTS:
            if hasattr(module, name):
                setattr(module, name, (ABSENT / "nothing",))


def pytest_collection_finish(session):
    rebind(list(sys.modules.values()))
    shutil.which = lambda *args, **kwargs: None


def pytest_runtest_logreport(report):
    if report.skipped and report.when in ("setup", "call"):
        _skipped.append(report.nodeid)
    if report.failed:
        _failed.append(report.nodeid)


def pytest_sessionfinish(session, exitstatus):
    for variable, collected in ((REPORT, _skipped), (FAILURE_REPORT, _failed)):
        destination = os.environ.get(variable)
        if destination:
            Path(destination).write_text("\n".join(sorted(set(collected))), encoding="utf-8")
