"""The inverted boundary, enforced by the build. D1, bars C1-C9; later C15, C23-C24b, C25-C29.

curvecast's `tests/test_curvecast_boundary.py` bans an order by banning the **words** that
would express one -- `notional`, `direction`, `position`, `size`, `weight`, `side`, `order`
-- because its output is text and, in its own words, *"the distance between 'here is the
expected bp shift at each tenor with a credible interval' and 'here is the trade' is one
field name"*.

**That is exactly why this repo exists and exactly why its guard has to be different.**
Portfolio VaR is a function *of positions*, so no risk engine can keep curvecast's boundary;
the choice was to amend a contract that has never been amended -- `EXEMPT_FIELDS` is `{}`
and three packages renamed their own fields rather than touch it -- or to build elsewhere.
Elsewhere is here, and here `Direction` and `Notional` are the subject matter. A name scan
would either ban the subject matter or rot into a list of exceptions.

So the ban is on **capability**, in three parts (DD1). No egress: with no way out of the
process there is no order path, whatever a function is called. No execution. No credentials
-- and not "secrets via env only" but *no environment access at all*, because this repo
needs none (DD3).

One half of curvecast's boundary transfers unchanged and is ported verbatim: the imperative
phrase ban (DD4). A risk decomposition of a stated book never needs to say "you should".
Recording which half transfers is the point -- "the boundary does not transfer" left
unqualified is how the imperative ban gets dropped along with the field ban.

Every scanner here is mutation-tested in the test that uses it (DD6). A source scan shipped
without a demonstration that it fires is indistinguishable from a scan that looks for
nothing, and that is a lesson this project has already paid for once.

**Since D3a the boundary is a property of the working tree, not of two directories**
(DD22). Until then each bar chose its own roots -- egress over `src/` and `tests/`, execution
over `src/` alone -- so a `scripts/fetch.py` was scanned by none of them. Now every Python
file carries exactly one policy, decided by where it sits: **ENGINE**, all six bans, is the
default; **HARNESS**, egress and broker and the LLM edge, is granted to `tests/` by name. A
directory nobody has named arrives strict. The engine's imports are a census (C27), so
capability arriving under a name no list carries turns the build red too, and a runtime audit
hook refuses the network for the whole test process (C29).

**The `C` sequence is global across this repo** -- `PRECOMMIT_deskcraft_d2_book_types.md`
says so at its head, because a `C` number is what gets cross-referenced from another
package's document. This file holds C1-C9 from D1, **C15** added by D2 when the imperative
scan was widened, and **C23 / C23b**, the LLM-edge ban and its mutation, added by the M18
repair on 2026-09-09. That pair shipped as `C10` / `C10b` and collided with D2's C10 --
the scan asserting `Direction` and `Notional` are defined in exactly one place. The
**newer** pair moved, later the same day, because D2's C10 is cited by a closed package's
pre-commit and by `src/deskcraft/book.py`; nothing about what either bar checks changed.
**C24 / C24b** are the gate that makes that non-recurring, and they exist because the
collision proved this repo had no bar-id check at all. **C25-C29** are D3a's.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

import deskcraft

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
TESTS = REPO_ROOT / "tests"

CURVECAST = Path("C:/Users/rishi/curvecast")
MEIP = Path("C:/Users/rishi/meip")

#: Exact module census. An equality rather than a floor, following curvecast's
#: `MODEL_COUNTS`: a floor only ever notices the code shrinking, and a scan over an empty
#: set passes vacuously. Adding a module turns this red until it is recorded here with its
#: work package, and so does deleting one.
MODULES = {
    "deskcraft",
    "deskcraft.book",  # D2
    "deskcraft.reference",  # D2
    "deskcraft.window",  # D3a
    "deskcraft.registers",  # D3a
    "deskcraft.sources",  # D3a
    "deskcraft.panel",  # D3b
    "deskcraft.sensitivity",  # D4
    "deskcraft.factors",  # D6
    "deskcraft.views",  # D6
    "deskcraft.costs",  # D7a
    "deskcraft.generator",  # D7b
    "deskcraft.covariance",  # D8
    "deskcraft.attribution",  # D9
    "deskcraft.bets",  # D10
    "deskcraft.sizing",  # D11
    # D12, D14, D15: built and dry-run on DEV, registered in the joint pre-commit, not landed.
    "deskcraft.construction",  # D15
    "deskcraft.riskbacktest",  # D14
    "deskcraft.scenarios",  # D12
    "deskcraft.readers",  # the four registered readers
    "deskcraft.exposure",  # D17: registered, not landed; its scorers are built ahead of the fixtures
    "deskcraft.hedging",  # D18
    "deskcraft.effectiveness",  # D21: registered, not landed; scorers and engine ahead of both halves
    "deskcraft.funding",  # D22: registered, not landed; built to the joint registration's §6.1 and §11
    "deskcraft.reverse",  # D13
    "deskcraft.readout",  # D16: registered, not landed; Paper 1's table, tally and figures
}

#: No way out of the process. This is the load-bearing ban: an order has to leave, and
#: closing every exit is stronger than enumerating the names an exit might be given.
#: **Widened at D3a (DD27)** by the eleven after `smtplib`: each was measured escaping the D1
#: list, and `urllib3`'s root is not `urllib`. The engine is also covered by C27's census,
#: which needs no list; the harness is not, which is why the list still matters.
NETWORK_MODULES = frozenset(
    {
        "socket",
        "urllib",
        "requests",
        "httpx",
        "http",
        "aiohttp",
        "websockets",
        "smtplib",
        "ftplib",
        "imaplib",
        "nntplib",
        "poplib",
        "telnetlib",
        "xmlrpc",
        "socketserver",
        "ssl",
        "asyncio",
        "webbrowser",
        "urllib3",
    }
)

EXECUTION_MODULES = frozenset({"subprocess", "multiprocessing", "pty"})

#: `os.<attr>` forms that execute or read a secret. Checked as attribute access rather
#: than as an import, because `import os` is ordinary and `os.getenv` is not. **Completed at
#: D3a (DD27)** to the whole exec, spawn, posix_spawn, fork and startfile family: D1 listed
#: nine of them and `dir(os)` on this interpreter carries nineteen. The scan reads source,
#: so POSIX-only names are listed though Windows lacks them.
FORBIDDEN_OS_ATTRS = frozenset(
    {
        "system",
        "popen",
        "execl",
        "execle",
        "execlp",
        "execlpe",
        "execv",
        "execve",
        "execvp",
        "execvpe",
        "spawnl",
        "spawnle",
        "spawnlp",
        "spawnlpe",
        "spawnv",
        "spawnve",
        "spawnvp",
        "spawnvpe",
        "posix_spawn",
        "posix_spawnp",
        "fork",
        "forkpty",
        "startfile",
        "environ",
        "getenv",
    }
)

#: `os.<attr>` forms that read or write the environment. D1 checked `environ` and `getenv`;
#: D3a adds the bytes forms and the two writers.
ENVIRONMENT_OS_ATTRS = frozenset({"environ", "environb", "getenv", "getenvb", "putenv", "unsetenv"})

CREDENTIAL_MODULES = frozenset({"getpass", "keyring", "dotenv", "python_dotenv"})

BROKER_MODULES = frozenset(
    {
        "kiteconnect",
        "ib_insync",
        "ibapi",
        "alpaca",
        "alpaca_trade_api",
        "ccxt",
        "oandapyV20",
        "robin_stocks",
        "tda",
        "schwab",
        "fyers_apiv3",
        "upstox_client",
        "smartapi",
        "breeze_connect",
        "dhanhq",
        "binance",
    }
)

#: Ported verbatim from curvecast (DD4). Word-boundary matched, case-insensitive. The
#: bare words "long" and "short" are deliberately NOT here -- they are the curve's own
#: vocabulary, and banning them would force circumlocution about the subject matter, which
#: is how a guard trains people to route around it.
FORBIDDEN_RENDERED_PHRASES = (
    r"\bbuy\b",
    r"\bsell\b",
    r"\bgo long\b",
    r"\bgo short\b",
    r"\boverweight\b",
    r"\bunderweight\b",
    r"\ballocate\b",
    r"\brecommend(s|ed|ation)?\b",
    r"\byou should\b",
    r"\btake profit\b",
)

REQUIRED_CONTRACTS = {
    "No broker SDK, ever",
    "No egress and no execution",
}

#: The LLM edge, scanned here because import-linter cannot express it. MEIP forbids
#: `meip.lpal` from `meip.rates` because "an LLM anywhere on the curve path makes a
#: published bp shift irreproducible"; curvecast restates that on its own side.
#: Reaching either from here would arrive at the same provider SDK by going around
#: both repos' contracts, and neither upstream's linter would ever see the edge,
#: because it lives in this one. Declared as a dotted path on purpose: the ban is on
#: the subpackage, not on `meip` or `curvecast`, both of which this repo imports by
#: design -- and that is exactly the shape import-linter refuses.
LLM_EDGE_MODULES = frozenset({"meip.lpal", "curvecast.news.scoring"})

# ---------------------------------------------------------------------------
# D3a: the policy census (DD22-DD26)
# ---------------------------------------------------------------------------

#: The six bans, by name. A policy is a subset of these.
BANS = ("egress", "execution", "environment", "broker", "imperative", "llm_edge")

#: The strict policy, and the default: a file under a directory nobody named receives it.
ENGINE_BANS = frozenset(BANS)

#: What the test harness keeps. `tests/` needs a child interpreter (C5), writes to
#: `tmp_path`, and quotes the forbidden phrases in order to forbid them -- so execution,
#: environment and the imperative ban are lifted there, and only there. Egress, a broker SDK
#: and the LLM edge are never lifted anywhere.
HARNESS_BANS = frozenset({"egress", "broker", "llm_edge"})

POLICY_BANS = {"ENGINE": ENGINE_BANS, "HARNESS": HARNESS_BANS}

#: Top-level directories granted HARNESS, by name. Adding one is a line in a diff with a
#: reason beside it, which is the whole point of naming them.
HARNESS_ROOTS = frozenset({"tests"})

#: File types the scan cannot read (DD23). A notebook's cells and a shell script's commands
#: are invisible to an AST, so rather than parse them they may not exist.
UNSCANNABLE_SUFFIXES = frozenset({".ipynb", ".pyw", ".sh", ".bash", ".ps1", ".psm1", ".bat", ".cmd"})

#: The exact top-level modules ENGINE files import (DD26). An equality, like `MODULES`: a new
#: import anywhere under ENGINE policy turns C27 red until it is recorded here, in the commit
#: that needs it, with the reason in that commit's pre-commit document.
#: `csv` and `pathlib` arrive at D3b (DD48), with `deskcraft.panel`, which is the first module
#: here that opens a file. Neither is a capability the six bans reach: reading a committed
#: fixture is not egress, execution, a credential, a broker SDK, the LLM edge or an imperative.
#: The extraction that produced the file ran in curvecast, which has the egress; this reads it.
#: `numpy` arrives at D6 (DD60), with `deskcraft.factors`, which is the first module here whose
#: arithmetic is not scalar. D4 refused it and its reason does not reach that far: a restatement
#: of curvecast's `_pca` held at EXACT equality has to call the same eigensolver, and a
#: hand-rolled Jacobi rotation would agree to a tolerance -- which is what C50 refused when it
#: said a tolerance is how a restatement stops being one. Not a capability the six bans reach:
#: an eigendecomposition is not egress, execution, a credential, a broker SDK or an imperative.
#: `statistics` arrives at D9 (DD146), with `deskcraft.attribution`, for `NormalDist.inv_cdf`:
#: the inverse normal is not in numpy, and a hand-rolled one is a second implementation of a
#: standard function. A quantile is not a capability any of the six bans reaches.
#: `scipy` and `itertools` arrive at D11 (DD159, DD160), with `deskcraft.sizing`: the two
#: linear programs need a solver (HiGHS), and a hand-rolled simplex would be a second
#: implementation of a standard routine; `itertools` enumerates the supports of a small
#: long-only quadratic program exactly. Neither is a capability any of the six bans reaches.
ENGINE_IMPORT_ROOTS = frozenset(
    {
        "__future__",
        "collections",
        "csv",
        "dataclasses",
        "datetime",
        "enum",
        "itertools",
        "math",
        "numpy",
        "pathlib",
        "scipy",
        "statistics",
        "deskcraft",
    }
)


# ---------------------------------------------------------------------------
# Scanners. Shared by the real check and by its mutation, so that the mutation
# exercises the same code path rather than a plausible-looking copy of it.
# ---------------------------------------------------------------------------


def imported_roots(source: str) -> set[str]:
    """Top-level package names this source imports, by either form.

    **Relative imports are skipped (D3a, DD27).** `from .socket import helper` reaches a
    first-party module that happens to be called `socket`, and until D3a this reported
    `socket` and fired the egress ban on it. A relative import cannot reach a top-level
    module, so it is not one.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            found.add(node.module.split(".")[0])
    return found


def imported_paths(source: str) -> set[str]:
    """Full dotted module paths this source imports, by either form.

    `imported_roots` deliberately truncates to the top level, which is right for the
    capability bans -- `socket` is `socket` however it is spelled. It is wrong for the
    LLM edge, where the banned thing is a subpackage of a package this repo imports on
    purpose, so the distinction has to survive the scan.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            found.add(node.module)
    return found


def reaches(path: str, banned: str) -> bool:
    """True when `path` is `banned` or lies beneath it.

    Segment-wise, so that a future `meip.lpalette` is not caught by a ban on
    `meip.lpal`, and `meip.lpal.client` is.
    """
    return path == banned or path.startswith(banned + ".")


def os_attributes(source: str) -> set[str]:
    """`os.<attr>` accesses, and bare `from os import <attr>` names.

    **Two gaps closed at D3a (DD27), both measured.** `import os as o; o.system('x')`
    returned nothing, because the check compared the attribute's owner to the literal name
    `os`; the owner is now any name `import os` was bound to. And `from os import *` returned
    `{'*'}`, which matched no ban; a star import now reports every banned attribute, because
    it binds all of them.
    """
    tree = ast.parse(source)
    names = {"os"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {alias.asname for alias in node.names if alias.name == "os" and alias.asname}
    found: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in names
        ):
            found.add(node.attr)
        elif isinstance(node, ast.ImportFrom) and node.module == "os":
            found |= {alias.name for alias in node.names}
    if "*" in found:
        found |= FORBIDDEN_OS_ATTRS | ENVIRONMENT_OS_ATTRS
    return found


def python_files(*roots: Path) -> list[Path]:
    return sorted(path for root in roots for path in root.rglob("*.py"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def working_tree(root: Path, suffixes: frozenset[str]) -> list[Path]:
    """Every file under `root` with one of `suffixes`, as the working tree holds it (DD24).

    The working tree and not the git index, so an untracked `scripts/fetch.py` is red before
    it is committed. Two things are pruned, each for what it is rather than what it is
    called: a `.git` directory, which is a database, and any directory holding `pyvenv.cfg`,
    which is an interpreter. Git-ignored directories are walked -- `.gitignore` says what not
    to commit, not what may run unguarded here.
    """
    found: list[Path] = []
    for directory, subdirectories, files in os.walk(root):
        here = Path(directory)
        subdirectories[:] = sorted(
            name
            for name in subdirectories
            if name != ".git" and not (here / name / "pyvenv.cfg").exists()
        )
        found += [here / name for name in files if Path(name).suffix.lower() in suffixes]
    return sorted(found)


def policy_of(path: Path, root: Path) -> str:
    """ENGINE unless the file sits under a top-level directory named in `HARNESS_ROOTS`."""
    parts = path.relative_to(root).parts
    return "HARNESS" if len(parts) > 1 and parts[0] in HARNESS_ROOTS else "ENGINE"


def scanned_files(root: Path) -> dict[Path, str]:
    """Every Python file in the working tree, mapped to the one policy it carries."""
    return {path: policy_of(path, root) for path in working_tree(root, frozenset({".py"}))}


def files_under(ban: str, root: Path = REPO_ROOT) -> list[Path]:
    """The files a ban reaches: every scanned file whose policy includes it."""
    assert ban in BANS, ban
    return [path for path, policy in scanned_files(root).items() if ban in POLICY_BANS[policy]]


def engine_import_roots(root: Path) -> set[str]:
    """The top-level modules imported by every ENGINE file under `root`."""
    found: set[str] = set()
    for path, policy in scanned_files(root).items():
        if policy == "ENGINE":
            found |= imported_roots(_read(path))
    return found


def _docstring_nodes(tree: ast.AST) -> set[int]:
    """Identity of every module, class and function docstring constant.

    Excluded from the scan deliberately and for a reason that is live in this repo:
    `src/deskcraft/__init__.py` contains the phrase "you should" once, inside its own
    docstring, where it names the forbidden phrases in order to forbid them. A guard that
    cannot describe itself is a guard that gets deleted.
    """
    found: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if body and isinstance(body[0], ast.Expr):
            value = body[0].value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                found.add(id(value))
    return found


def _collect_strings(
    node: ast.AST, label: str, docstrings: set[int], out: list[tuple[str, str]]
) -> None:
    for child in ast.iter_child_nodes(node):
        here = label
        if isinstance(child, ast.Assign):
            names = [t.id for t in child.targets if isinstance(t, ast.Name)]
            if names:
                here = names[0]
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            here = child.target.id
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            here = child.name
        elif isinstance(child, ast.keyword) and child.arg:
            here = f"{label}.{child.arg}" if label else child.arg

        if (
            isinstance(child, ast.Constant)
            and isinstance(child.value, str)
            and id(child) not in docstrings
        ):
            out.append((here or "<inline>", child.value))
        _collect_strings(child, here, docstrings, out)


def rendered_strings(source: str) -> list[tuple[str, str]]:
    """(label, text) for every string constant a renderer could emit, excluding docstrings.

    **Widened at D2 (DD13), and the widening is the second repair this scanner has needed.**

    D1's version read module-level UPPERCASE assignments only. That was already the *second*
    version: the first iterated `vars(deskcraft)`, so a module sitting in `src/` that nothing
    imports was invisible to it, and the end-to-end mutation that put one there sailed through
    green while three other bars fired -- because the mutation leg exercised the *regex* and
    not the *scan*.

    D2 introduces `Book.thesis`, so this repo's first rendered strings sit in
    **constructor-argument** position, and measurement before the package was written
    confirmed the D1 scanner returns `[]` for both `Book(thesis="... you should ...")` and a
    lowercase module-level assignment. Same class of gap, one package later, in a different
    position. So the scan now reaches every string constant in the file and carries a label
    describing where it was found -- `REFERENCE_BOOK.thesis` for a keyword argument, the
    target name for an assignment, the enclosing name otherwise.

    Docstrings stay out, by identity rather than by position, and `_docstring_nodes` records
    why.
    """
    tree = ast.parse(source)
    out: list[tuple[str, str]] = []
    _collect_strings(tree, "", _docstring_nodes(tree), out)
    return out


def imperative_offences(source: str) -> list[tuple[str, str]]:
    """(label, pattern) for every rendered string that trips the imperative ban.

    Shared by C6, C15 and `offences`; until D3a C6 and C15 each carried an identical nested
    copy, which is two places for the scan to drift apart in.
    """
    return [
        (label, pattern)
        for label, text in rendered_strings(source)
        for pattern in FORBIDDEN_RENDERED_PHRASES
        if re.search(pattern, text, flags=re.IGNORECASE)
    ]


def offences(source: str) -> dict[str, list[str]]:
    """What this source does that each ban forbids, keyed by ban. Empty lists are clean.

    The one function every capability bar and its mutation read (D3a), so the census in
    C25b is proven against the same code that guards the tree.
    """
    roots = imported_roots(source)
    attributes = os_attributes(source)
    return {
        "egress": sorted(roots & NETWORK_MODULES),
        "execution": sorted((roots & EXECUTION_MODULES) | (attributes & FORBIDDEN_OS_ATTRS)),
        "environment": sorted((roots & CREDENTIAL_MODULES) | (attributes & ENVIRONMENT_OS_ATTRS)),
        "broker": sorted(roots & BROKER_MODULES),
        "imperative": [f"{label}: {pattern}" for label, pattern in imperative_offences(source)],
        "llm_edge": sorted(
            f"{path} -> {banned}"
            for path in imported_paths(source)
            for banned in LLM_EDGE_MODULES
            if reaches(path, banned)
        ),
    }


def violations(source: str, bans: frozenset[str]) -> set[str]:
    """The bans in `bans` this source breaks."""
    return {ban for ban, found in offences(source).items() if found and ban in bans}


# ---------------------------------------------------------------------------
# The scan
# ---------------------------------------------------------------------------


def test_the_package_exists_and_the_census_is_exact() -> None:
    """C1. DD1. A scan over an empty set passes vacuously; this is what stops that.

    The package is deliberately empty at D1 -- the guard has to be live before there is
    anything to guard -- so the one thing that could make every bar below meaningless is
    the scanner finding no files at all. The census is an equality, so D2 adding the book
    types turns this red until they are recorded, and a later deletion turns it red too.
    """
    assert deskcraft.__all__ == []
    found = set()
    for path in python_files(SRC):
        parts = list(path.relative_to(SRC).with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        found.add(".".join(parts))
    assert found == MODULES, f"module census disagrees: {found} vs {MODULES}"
    assert python_files(SRC), "the scanned source set is empty"
    assert len(python_files(SRC, TESTS)) >= 3


def test_there_is_no_way_out_of_the_process() -> None:
    """C2. DD1. No egress, which is the ban an order path cannot be renamed around.

    **Widened at D3a (DD22):** every file under either policy, rather than `src/` and
    `tests/` by name -- egress is lifted nowhere.

    **Mutation:** the same scanner is shown to catch a module that imports `requests`. A
    scan that finds nothing and a scan that looks for nothing are the same green.
    """
    for path in files_under("egress"):
        offending = offences(_read(path))["egress"]
        assert not offending, f"{path.name} imports {offending}"

    mutant = "import requests\n\ndef send(book):\n    requests.post('https://x', json=book)\n"
    assert imported_roots(mutant) & NETWORK_MODULES == {"requests"}
    assert offences(mutant)["egress"] == ["requests"]


def test_nothing_in_the_engine_can_execute() -> None:
    """C3. DD1. No subprocess and no `os.system`, over every ENGINE file.

    Not `tests/`: this file imports `subprocess` itself, to run C5's fresh interpreter.
    That is the test harness reaching outward, which is a different thing from the engine
    doing it -- and stating the difference is better than a scan whose scope nobody can
    explain. **Since D3a (DD22) the difference is a policy rather than a root list**, so a
    `scripts/` directory is engine, not harness.

    **Mutation:** both a `subprocess` import and a bare `os.system` call are caught.
    """
    for path in files_under("execution"):
        offending = offences(_read(path))["execution"]
        assert not offending, f"{path.name} executes: {offending}"

    assert imported_roots("import subprocess") & EXECUTION_MODULES == {"subprocess"}
    assert os_attributes("import os\nos.system('x')") & FORBIDDEN_OS_ATTRS == {"system"}


def test_no_credential_is_read_anywhere() -> None:
    """C4. DD3. Not "secrets via env only" -- no environment access at all.

    The inherited rule permits secrets through the environment. deskcraft needs no secret:
    its inputs are stated books and the objects curvecast item 28 produces. So the rule is
    tightened to a scan with no judgement in it. If a later package genuinely needs an
    environment variable it edits this test with a recorded reason, which is the
    self-correcting shape and the opposite of an exemption list. **Scans every ENGINE file
    since D3a (DD22).**

    **Mutation:** an `os.getenv("KITE_API_KEY")` and a `from os import environ` are caught.
    """
    for path in files_under("environment"):
        offending = offences(_read(path))["environment"]
        assert not offending, f"{path.name} reads the environment or a secret: {offending}"

    assert os_attributes('import os\nkey = os.getenv("KITE_API_KEY")') >= {"getenv"}
    assert os_attributes("from os import environ") == {"environ"}
    assert imported_roots("import keyring") & CREDENTIAL_MODULES == {"keyring"}


def test_no_broker_sdk_is_reached() -> None:
    """C5. DD2. Asserted about this repo, not about this machine.

    `kiteconnect` IS installed on this machine, for an unrelated repository that trades a
    live NSE book. So "no broker SDK is importable" would be a claim about the interpreter
    and would be red for reasons that have nothing to do with deskcraft. Three checks
    instead, of which the third is the one that catches a transitive arrival: not declared,
    not imported, and not in `sys.modules` after a fresh `import deskcraft`.

    **D3a removed this bar's skip of its own file.** It skipped `test_deskcraft_boundary.py`
    by name because the file *names* the brokers -- but the scan reads import statements, and
    naming a module in a string imports nothing. An exemption nothing needed is a policy with
    two members, which is the shape DD22 exists to forbid.
    """
    pyproject = tomllib.loads(_read(REPO_ROOT / "pyproject.toml"))
    declared = " ".join(
        pyproject["project"]["dependencies"]
        + [d for group in pyproject["project"]["optional-dependencies"].values() for d in group]
    ).lower()
    assert not [name for name in BROKER_MODULES if name.lower() in declared]

    for path in files_under("broker"):
        offending = offences(_read(path))["broker"]
        assert not offending, f"{path.name} imports {offending}"

    probe = (
        "import sys, json; import deskcraft; "
        f"print(json.dumps(sorted(set(sys.modules) & set({sorted(BROKER_MODULES)!r}))))"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(SRC), "SYSTEMROOT": "C:\\Windows", "PATH": ""},
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]", f"importing deskcraft pulled in {result.stdout}"


def test_the_imperative_ban_transferred_even_though_the_field_ban_did_not() -> None:
    """C6. DD4. Which half transfers is stated, because the unqualified claim loses one.

    curvecast's `FORBIDDEN_FIELD_TOKENS` cannot transfer -- `Direction` and `Notional` are
    this repo's subject matter, and that is why this repo exists. Its
    `FORBIDDEN_RENDERED_PHRASES` transfers unchanged: nothing about describing a book's risk
    requires the engine to say "you should" or "take profit". **Scans every ENGINE file
    since D3a (DD22)** -- a readout driver in `scripts/` is the likeliest first renderer
    outside `src/`.

    **Mutation, in the form the first version got wrong:** the assertion is that the
    *scanner* reaches a string in a file, not that the *regex* matches a literal. See
    `rendered_strings` for what that distinction cost.
    """
    if CURVECAST.exists():
        upstream = _read(CURVECAST / "tests" / "test_curvecast_boundary.py")
        for pattern in FORBIDDEN_RENDERED_PHRASES:
            assert pattern in upstream, f"{pattern} is not curvecast's; the port has drifted"

    for path in files_under("imperative"):
        assert not imperative_offences(_read(path)), f"{path.name} would render an imperative"

    for name, value in vars(deskcraft).items():
        if name.startswith("_") or not isinstance(value, str) or not name.isupper():
            continue
        for pattern in FORBIDDEN_RENDERED_PHRASES:
            assert not re.search(pattern, value, flags=re.IGNORECASE), (name, pattern)

    mutant = 'NOTE = "Given the decomposition above, you should reduce the front leg."\n'
    assert imperative_offences(mutant) == [("NOTE", r"\byou should\b")], (
        "the scan does not reach a module-level string in a file, which is exactly the "
        "gap the end-to-end mutation found in this bar's first version"
    )


def test_the_imperative_scan_reaches_the_positions_d2_introduced() -> None:
    """C15. DD13. The widening, mutation-tested in the shape D1's post-mortem prescribed.

    D1's bar C6 asserted the scanner catches a module-level UPPERCASE string. Measured before
    D2 was written, that same scanner returned `[]` for a `Book(thesis=...)` -- which is where
    every rendered string in this repo now lives. So the assertion here is that the scan
    **reaches a string in a file** in each of the three positions, not that a regex matches a
    literal: that distinction is what the first version of C6 got wrong, and it cost a green
    vacuous pass on an end-to-end mutation that turned four other bars red.

    The docstring leg is not decoration. `src/deskcraft/__init__.py` carries "you should" in
    its own docstring, so a widening that did not exclude docstrings would turn this repo red
    for describing its own guard.
    """
    for path in files_under("imperative"):
        assert not imperative_offences(_read(path)), f"{path.name} would render an imperative"

    constructor = (
        "from deskcraft.book import Book\n"
        'REFERENCE_BOOK = Book(thesis="Given the decomposition, you should cut the front leg")\n'
    )
    assert imperative_offences(constructor) == [("REFERENCE_BOOK.thesis", r"\byou should\b")], (
        "the scan does not reach a constructor-argument string, which is the position every "
        "rendered string in this repo occupies as of D2"
    )

    lowercase = 'note = "you should take profit here"\n'
    assert {pattern for _, pattern in imperative_offences(lowercase)} == {
        r"\byou should\b",
        r"\btake profit\b",
    }

    nested = 'REASONS = {"a": {"b": ["overweight the belly"]}}\n'
    assert imperative_offences(nested) == [("REASONS", r"\boverweight\b")]

    docstring = '"""A guard that names \'you should\' in order to forbid it."""\n'
    assert imperative_offences(docstring) == [], (
        "docstrings must stay excluded; __init__.py is the live case"
    )
    assert imperative_offences('def f():\n    """you should not fire here."""\n    return 1\n') == []

    live = _read(SRC / "deskcraft" / "__init__.py")
    assert "you should" in live, "the live docstring case has moved; this bar no longer binds"
    assert not imperative_offences(live)


def test_the_edges_are_one_way() -> None:
    """C7. DD5. `lint-imports` cannot see this direction, so it is scanned.

    import-linter reads one root package: run here it sees imports made BY deskcraft, never
    curvecast or meip importing deskcraft -- which is the direction that would make the edge
    two-way and put curvecast's sealed baselines at risk. Neither upstream may be modified
    to add a contract there, so the assertion lives on this side as a scan.

    It **skips loudly** rather than passing over an absent repository: a scan of a directory
    that does not exist finds nothing and reports success, which is this check's own worst
    failure mode.
    """
    checked = 0
    for upstream in (CURVECAST / "src", MEIP / "src"):
        if not upstream.exists():
            continue
        for path in upstream.rglob("*.py"):
            assert "deskcraft" not in imported_roots(_read(path)), (
                f"{path} imports deskcraft; the edge is two-way"
            )
            checked += 1
    if checked == 0:
        pytest.skip("neither upstream repository is on this machine; nothing was scanned")
    assert checked > 100, f"only {checked} upstream files scanned; the glob is wrong"


def test_the_llm_edge_is_scanned() -> None:
    """C23. Added 2026-09-09, and the reason it exists is the finding.

    From D1 until today this ban lived only as an import-linter contract, and
    import-linter cannot express it: a dotted external module is rejected outright and
    aborts the whole run. So the contract never returned a verdict, and neither did the
    two beside it. Grepping the repo for `lpal` on 2026-09-09 found exactly one hit, in
    a docstring. **The one contract with no AST counterpart was the one that could not
    be linted**, which left the LLM edge the only part of this boundary guarded by
    nothing at all.

    Scans every file under either policy since D3a (DD22); a test that imports the provider
    SDK reaches it exactly as a module would.
    """
    files = files_under("llm_edge")
    assert len(files) >= 4, f"only {len(files)} files scanned; the glob is wrong"
    for path in files:
        reaching = offences(_read(path))["llm_edge"]
        assert not reaching, (
            f"{path} reaches {reaching}; the upstream edge is not allowed to touch an LLM"
        )


def test_the_llm_edge_scan_would_catch_a_real_import() -> None:
    """C23b. The scan, mutated. A guard that has never fired is a guard on trust.

    Runs the same scanner over sources that do reach the edge, including one that goes
    a level deeper, and one near-miss that must NOT fire.
    """
    for source in (
        "from meip.lpal import Provider",
        "import meip.lpal",
        "import meip.lpal.client as c",
        "from curvecast.news.scoring import score",
    ):
        hits = [
            (i, bnd)
            for i in imported_paths(source)
            for bnd in LLM_EDGE_MODULES
            if reaches(i, bnd)
        ]
        assert hits, f"the scan missed {source!r}"
        assert offences(source)["llm_edge"], f"offences() missed {source!r}"

    for benign in ("from meip.rates.cascade import x", "import curvecast.stage3"):
        assert not [
            i
            for i in imported_paths(benign)
            for bnd in LLM_EDGE_MODULES
            if reaches(i, bnd)
        ], f"the scan fires on {benign!r}, which the plan requires"


def test_import_contracts_are_declared() -> None:
    """C8. DD7. Needs nothing installed, so it always binds.

    The realistic failure is not that a contract is violated -- `lint-imports` catches that
    wherever it runs -- but that one is deleted, or renamed into uselessness, by someone who
    found it inconvenient. This notices with no tooling at all, which matters because
    import-linter is absent from both interpreters on this machine.
    """
    contracts = tomllib.loads(_read(REPO_ROOT / "pyproject.toml"))["tool"]["importlinter"]
    names = {c["name"] for c in contracts["contracts"]}
    assert REQUIRED_CONTRACTS <= names, f"missing: {REQUIRED_CONTRACTS - names}"

    for contract in contracts["contracts"]:
        assert contract["type"] == "forbidden"
        assert "deskcraft" in contract["source_modules"]

    broker = next(c for c in contracts["contracts"] if c["name"] == "No broker SDK, ever")
    assert BROKER_MODULES <= set(broker["forbidden_modules"]), (
        "the contract's broker list has drifted from the one the tests scan for"
    )
    egress = next(c for c in contracts["contracts"] if c["name"] == "No egress and no execution")
    assert NETWORK_MODULES <= set(egress["forbidden_modules"])

    # Added 2026-09-09. Until today this test checked that contracts were DECLARED and
    # nothing checked that they could be EVALUATED, so three contracts sat here for nine
    # days while the gate aborted on configuration. Declaration is not enforcement.
    assert contracts.get("include_external_packages") is True, (
        "include_external_packages is required whenever a forbidden module is external, "
        "and every one of these is; without it import-linter evaluates nothing"
    )
    for contract in contracts["contracts"]:
        for module in contract["forbidden_modules"]:
            assert "." not in module, (
                f"{module!r} is a subpackage of an external package; import-linter "
                "rejects it and aborts the whole run. Bans of that shape belong in "
                "LLM_EDGE_MODULES and C23, not here"
            )

    assert LLM_EDGE_MODULES, "the LLM-edge ban has been emptied; C23 would pass vacuously"


def test_curvecast_exemptions_are_still_empty() -> None:
    """C9. The constant that made this repo necessary, watched from the repo it caused.

    curvecast's `EXEMPT_FIELDS` is `{}` and has never been anything else; three packages
    renamed their own fields rather than add an entry, and a fourth did so this week. The
    single most likely way this repo goes wrong is that its existence makes relaxing that
    constant look reasonable -- so the check lives here, pointing back, rather than only in
    the repo that would be doing the relaxing.

    Parsed rather than imported: importing curvecast's test module would need its conftest,
    its path fix and its dependencies, and a guard that needs an environment to run is a
    guard that stops running.
    """
    boundary = CURVECAST / "tests" / "test_curvecast_boundary.py"
    if not boundary.exists():
        pytest.skip("curvecast is not on this machine")

    tree = ast.parse(_read(boundary))
    found = [
        node
        for node in tree.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "EXEMPT_FIELDS"
    ]
    assert len(found) == 1, "EXEMPT_FIELDS is no longer a single module-level assignment"
    value = found[0].value
    assert isinstance(value, ast.Dict) and not value.keys, (
        "curvecast's EXEMPT_FIELDS is no longer empty. That is the boundary this repo was "
        "built to avoid amending, and it has been amended."
    )


# ---------------------------------------------------------------------------
# C24: the sequence itself
# ---------------------------------------------------------------------------


def bar_ids(path: Path) -> list[str]:
    """Every bar id a test in `path` claims, in file order.

    A bar id is the first token of a test function's docstring -- `C12.` or `C12b.` --
    which is the convention curvecast's `scripts/check_bar_coverage.py` reads and the one
    both of this repo's test modules already follow. Read by AST rather than by line, so
    a `C12.` inside prose or a comment is not mistaken for a claim.
    """
    pattern = re.compile(r"^(C\d+[a-z]?)\.")
    claims = []
    for node in ast.walk(ast.parse(_read(path))):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            match = pattern.match(ast.get_docstring(node) or "")
            if match:
                claims.append(match.group(1))
    return claims


def collect_bar_ids(root: Path) -> tuple[dict[str, Path], list[str]]:
    """Map every bar id under `root` to the module claiming it, and name every collision.

    Takes a root so both arms are reachable: a guard that can only be observed passing on
    the one directory it is pointed at is not observed at all.
    """
    claimed: dict[str, Path] = {}
    duplicates: list[str] = []
    for path in sorted(root.glob("test_*.py")):
        for bar in bar_ids(path):
            if bar in claimed:
                duplicates.append(f"{bar}: {claimed[bar].name} and {path.name}")
            else:
                claimed[bar] = path
    return claimed, duplicates


def test_no_bar_id_is_claimed_twice() -> None:
    """C24. The `C` sequence is global, and until 2026-09-09 nothing checked it.

    D2's pre-commit declares the sequence global *because a `C` number is what gets
    cross-referenced from another package's document*. On 2026-09-09 the M18 repair
    claimed `C10` in this file, which D2 already held in `test_book_types.py`, and both
    modules were green: every bar passed, the duplicate was invisible, and two documents
    then cited `C10` meaning two different scans.

    Nothing would have caught it. curvecast's `check_bar_coverage.py` -- the nearest
    upstream instrument -- takes **one** doc and **one** test module per invocation and
    asks whether each bar in the table is claimed. A duplicate across two modules is
    outside the question it asks. This asks the other question, over the whole directory.

    The full registry -- claims to their scorers, sources to their fallbacks, the package
    budget -- is D3a's. This is the one piece of it the collision made unwise to defer,
    per the standing rule that a violation is what tells you which gate to write.
    """
    claimed, duplicates = collect_bar_ids(TESTS)

    assert not duplicates, (
        "a bar id is claimed by two modules; the `C` sequence is global across this "
        "repo, so renumber the newer claim rather than letting a cross-reference become "
        "ambiguous: " + "; ".join(duplicates)
    )
    # Vacuity: an empty scan reports no duplicates for the wrong reason.
    assert len(claimed) >= 24, f"only {len(claimed)} bar ids found; the scanner is wrong"


def test_the_bar_id_scan_would_catch_a_duplicate(tmp_path: Path) -> None:
    """C24b. C24, mutated -- against a real collision and against a near-miss.

    The near-miss is the half worth stating. `C24` and `C24b` are different bars in the
    same module and must never be reported as a collision; a scanner that compared only
    the numeric part would fail this repo on its own convention.
    """
    (tmp_path / "test_alpha.py").write_text(
        'def test_one() -> None:\n    """C99. A bar."""\n', encoding="utf-8"
    )
    (tmp_path / "test_beta.py").write_text(
        'def test_two() -> None:\n    """C99. The same id, in another module."""\n',
        encoding="utf-8",
    )
    _, duplicates = collect_bar_ids(tmp_path)
    assert len(duplicates) == 1 and duplicates[0].startswith("C99:"), duplicates

    near_miss = tmp_path / "near"
    near_miss.mkdir()
    (near_miss / "test_gamma.py").write_text(
        'def test_one() -> None:\n    """C99. A bar."""\n\n\n'
        'def test_two() -> None:\n    """C99b. Its mutation, which is not the same bar."""\n',
        encoding="utf-8",
    )
    claimed, duplicates = collect_bar_ids(near_miss)
    assert not duplicates, duplicates
    assert set(claimed) == {"C99", "C99b"}


# ---------------------------------------------------------------------------
# C25-C29: D3a -- one policy per file, and what backs the lists up
# ---------------------------------------------------------------------------

#: One file carrying every capability the six bans forbid. Used by C25b; the end-to-end
#: demonstration in D3a's pre-commit places the same content in the real tree.
_EVERY_CAPABILITY = (
    "import os\n"
    "import requests\n"
    "import subprocess\n"
    "import kiteconnect\n"
    "from meip.lpal import Provider\n"
    "KEY = os.getenv('KITE_API_KEY')\n"
    "NOTE = 'Given the decomposition, you should reduce the front leg.'\n"
)


def test_every_python_file_carries_exactly_one_policy() -> None:
    """C25. B25. DD22, DD24. A file the boundary does not reach cannot exist.

    Until D3a every capability bar picked its own roots, and a `scripts/` directory would
    have been scanned by none of them. Now the policy is a function of where a file sits:
    HARNESS for the top-level `tests/` alone, ENGINE for everything else, including every
    directory nobody has thought of yet.
    """
    census = scanned_files(REPO_ROOT)
    assert census, "the walk found no Python file; it is walking the wrong place"
    assert HARNESS_ROOTS == {"tests"}, "HARNESS was granted to a second root"

    for path, policy in census.items():
        top = path.relative_to(REPO_ROOT).parts[0]
        if top == "src":
            assert policy == "ENGINE", path
        if top == "tests":
            assert policy == "HARNESS", path
        if policy == "HARNESS":
            assert top in HARNESS_ROOTS, path

    assert set(python_files(SRC)) <= set(census), "the walk misses a file C1 counts"
    for ban in BANS:
        assert files_under(ban), f"the {ban} ban reaches no file and would pass vacuously"
    assert ENGINE_BANS == frozenset(BANS) and HARNESS_BANS < ENGINE_BANS


def test_a_new_directory_arrives_strict(tmp_path: Path) -> None:
    """C25b. B25. C25, mutated through the functions the real bars read.

    Three ENGINE files in three shapes of "somewhere new" -- a `scripts/` directory, a
    `tools/` directory, and the repository root -- each fire all six bans. A HARNESS file with
    the same content fires exactly the three the harness keeps. And the two pruned directories
    are not walked: a file inside a virtual environment, and one inside `.git`.
    """
    placements = ("scripts/a.py", "tools/b.py", "c.py", "tests/d.py", "venv/lib/e.py", ".git/f.py")
    for relative in placements:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_EVERY_CAPABILITY, encoding="utf-8")
    (tmp_path / "venv" / "pyvenv.cfg").write_text("home = C:\\Python\n", encoding="utf-8")

    census = {path.relative_to(tmp_path).as_posix(): policy for path, policy in scanned_files(tmp_path).items()}
    assert census == {
        "scripts/a.py": "ENGINE",
        "tools/b.py": "ENGINE",
        "c.py": "ENGINE",
        "tests/d.py": "HARNESS",
    }, census

    engine = ("scripts/a.py", "tools/b.py", "c.py")
    for relative in engine:
        planted = _read(tmp_path / relative)
        assert violations(planted, POLICY_BANS[census[relative]]) == set(BANS), relative
    harness = _read(tmp_path / "tests" / "d.py")
    assert violations(harness, POLICY_BANS[census["tests/d.py"]]) == {"egress", "broker", "llm_edge"}

    for ban in BANS:
        reached = {path.relative_to(tmp_path).as_posix() for path in files_under(ban, tmp_path)}
        expected = set(engine) | ({"tests/d.py"} if ban in HARNESS_BANS else set())
        assert reached == expected, (ban, reached)


def test_no_file_the_scanner_cannot_read(tmp_path: Path) -> None:
    """C26. B26. DD23. A notebook or a shell script is outside the scan, so it is refused.

    The boundary reads `.py` source. A notebook's code cells are JSON strings, a PowerShell
    script's commands are not Python at all, and a guard over a set the adversary can simply
    leave is a guard over nothing. Refusing is cheaper than parsing, and reversible with a
    recorded reason.
    """
    present = working_tree(REPO_ROOT, UNSCANNABLE_SUFFIXES)
    assert not present, f"files the boundary cannot read: {present}"

    for suffix in sorted(UNSCANNABLE_SUFFIXES):
        (tmp_path / f"probe{suffix.upper() if suffix == '.ps1' else suffix}").write_text(
            "x", encoding="utf-8"
        )
    (tmp_path / "fine.py").write_text("x = 1\n", encoding="utf-8")
    found = {path.name.lower() for path in working_tree(tmp_path, UNSCANNABLE_SUFFIXES)}
    assert found == {f"probe{suffix}" for suffix in UNSCANNABLE_SUFFIXES}, found


def test_the_engine_imports_are_a_census(tmp_path: Path) -> None:
    """C27. B27. DD26. Default-deny for capability, without a list that has to name it.

    §0.3 of D3a's pre-commit measured nine real capabilities escaping the D1 name lists. The
    lists are widened (C28), and they will be short again by the next name nobody thought of.
    So the engine's imports are an equality: any import under ENGINE policy that is not
    already recorded turns this red, whatever it is called, and nothing banned may ever be
    recorded.

    **Mutation:** `urllib3`, which the D1 network list missed, and `ctypes`, which no list in
    this file names at all, both change the census.
    """
    assert engine_import_roots(REPO_ROOT) == ENGINE_IMPORT_ROOTS
    banned = NETWORK_MODULES | EXECUTION_MODULES | CREDENTIAL_MODULES | BROKER_MODULES
    assert not ENGINE_IMPORT_ROOTS & banned, ENGINE_IMPORT_ROOTS & banned

    (tmp_path / "src" / "deskcraft").mkdir(parents=True)
    (tmp_path / "src" / "deskcraft" / "book.py").write_text(
        "from dataclasses import dataclass\n", encoding="utf-8"
    )
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "a.py").write_text("import urllib3\nimport ctypes\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "t.py").write_text("import pytest\n", encoding="utf-8")

    assert engine_import_roots(tmp_path) == {"dataclasses", "urllib3", "ctypes"}
    assert "ctypes" not in banned, "the mutation needs a module no list names"


def test_the_name_lists_reach_what_d1_missed() -> None:
    """C28. B28. DD27. §0.3's nine escapes, and its one false positive, through `offences`.

    Every case below was run against the D1 scanners on 2026-09-11 before this bar existed,
    and every escape returned no hit. The relative import is the opposite defect: it fired
    the egress ban on a first-party module that happened to be called `socket`.
    """
    fires = {
        "import os as o\no.system('x')": "execution",
        "from os import *": "execution",
        "import os\nos.startfile('x')": "execution",
        "import os\nos.posix_spawn('x', [], {})": "execution",
        "import os\nos.putenv('K', 'v')": "environment",
        "import urllib3": "egress",
        "import webbrowser": "egress",
        "import ftplib": "egress",
        "from xmlrpc.client import ServerProxy": "egress",
        "from socket import create_connection": "egress",
    }
    for source, ban in fires.items():
        assert offences(source)[ban], f"{source!r} does not fire {ban}"
    assert offences("from os import *")["environment"], "a star import binds environ too"

    assert not offences("from .socket import helper")["egress"], (
        "a relative import reaches a first-party module and must not fire the egress ban"
    )

    egress = next(
        c
        for c in tomllib.loads(_read(REPO_ROOT / "pyproject.toml"))["tool"]["importlinter"][
            "contracts"
        ]
        if c["name"] == "No egress and no execution"
    )
    added = {"ftplib", "imaplib", "nntplib", "poplib", "telnetlib", "xmlrpc", "socketserver",
             "ssl", "asyncio", "webbrowser", "urllib3"}
    assert added <= NETWORK_MODULES
    assert added <= set(egress["forbidden_modules"]), "the widening did not reach the contract"


def test_the_network_is_refused_at_run_time() -> None:
    """C29. B29. DD25. The runtime layer, shown to fire and shown to be the thing firing.

    In this process the guard is installed and refuses a synthetic `socket.__new__` event.
    Then two fresh interpreters run the same line, `socket.socket()`. With the guard installed
    from `tests/egress_guard.py`, it is refused by the guard's own exception type. With only an
    observing hook, the observer sees `socket.__new__` and stops the line there -- so the event
    is real, it precedes the socket, and the treatment's refusal is the guard's rather than
    something about the machine. **No socket is created in either arm.**
    """
    import egress_guard

    assert egress_guard.installed(), "conftest.py did not install the guard"
    with pytest.raises(egress_guard.EgressRefused):
        sys.audit("socket.__new__", None, 2, 1, 0)

    treatment = (
        f"import sys; sys.path.insert(0, {str(TESTS)!r})\n"
        "import egress_guard\n"
        "egress_guard.install()\n"
        "import socket\n"
        "try:\n"
        "    socket.socket()\n"
        "except egress_guard.EgressRefused:\n"
        "    print('REFUSED')\n"
        "else:\n"
        "    print('CREATED')\n"
    )
    control = (
        "import sys\n"
        "class Seen(Exception):\n"
        "    pass\n"
        "def observe(event, args):\n"
        "    if event == 'socket.__new__':\n"
        "        raise Seen(event)\n"
        "sys.addaudithook(observe)\n"
        "import socket\n"
        "try:\n"
        "    socket.socket()\n"
        "except Seen as exc:\n"
        "    print('SEEN', exc)\n"
        "else:\n"
        "    print('CREATED')\n"
    )
    outputs = {}
    for arm, source in (("treatment", treatment), ("control", control)):
        result = subprocess.run(
            [sys.executable, "-c", source],
            cwd=REPO_ROOT,
            env={"SYSTEMROOT": "C:\\Windows", "PATH": ""},
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, (arm, result.stderr)
        outputs[arm] = result.stdout.strip()

    assert outputs["treatment"] == "REFUSED", outputs
    assert outputs["control"] == "SEEN socket.__new__", outputs
