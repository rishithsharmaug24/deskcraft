# D3a — guards and registers

Work package **D3a** of `docs/BUILD_ORDER_D3_D16.md` §4, second in the running order after
D23. Deliverable, as the row states it: `FitWindow` refusing `end > 2014-12-31`; the boundary
scan widened before a `scripts/` directory can exist; the **claims register**; the **source
resilience register**; the TRIAL_LEDGER non-look entry; and `PACKAGE_BUDGET = 21`, read from
§4's table and failing the build.

Decisions **DD22–DD38**, continuing D2's `DD` sequence. Bars **B25–B38**, executable as
**C25–C38** plus **C25b**, continuing the global `C` sequence past C24b. Predictions
**P1–P9**, local to this package.

**The scope of the widening was put to the owner rather than assumed,** because it is the one
decision here that could not be recovered from the plan: does a future `scripts/` directory
inherit the whole ban — no egress, no execution, no environment — or only the egress half?
The recommendation was the whole ban; on 2026-09-11 the owner accepted it on the condition
that it is the correct thing to do institutionally. DD22 records the reasoning on that test,
and §2 records the limit that reasoning has.

---

## 0. Measured before decided

Measured **2026-09-11**, on the production interpreter
`C:/Users/rishi/AppData/Local/Programs/Python/Python312/python.exe` (**3.12.10**, pytest
9.1.1), against deskcraft `ef08144`, curvecast `9153ff7` and MEIP `c1e383e`.

### 0.1 The boundary is a property of two directories, and each bar picked its own two

`tests/test_deskcraft_boundary.py` hardcodes a root set per bar:

| bar | ban | scans |
|---|---|---|
| C2 | egress | `src/`, `tests/` |
| C3 | execution | `src/` |
| C4 | environment and credentials | `src/` |
| C5 | broker SDK | `src/`, `tests/` |
| C6, C15 | imperative phrases | `src/` |
| C23 | the LLM edge | `src/`, `tests/` |

So a file at `scripts/fetch.py`, `tools/x.py` or `./setup.py` is scanned by **none** of the
seven, which is the approved plan's M10. There is no rule deciding which root a bar scans; the
split between the two sets happens to be *engine versus harness*, and C3's docstring is the
only place that says so.

### 0.2 The working tree, censused

Six `.py` files, in exactly two top-level roots: `src/` (3) and `tests/` (3). **Zero**
notebooks, `.pyw`, shell, PowerShell or batch files. No `pyvenv.cfg` anywhere, so no
virtual environment sits inside the tree. The engine imports, by root:
`__future__`, `collections`, `dataclasses`, `datetime`, `enum`, `math`, `deskcraft` — **seven
roots, all standard library or first-party.**

### 0.3 The name lists miss nine forms, and misfire on a tenth

Run against the shipped scanners, each of these is a real capability and each returns no
hit:

| source | scanner returns | bans hit |
|---|---|---|
| `import os as o; o.system('x')` | `[]` | none — **the alias is invisible** |
| `from os import *` | `['*']` | none |
| `os.startfile('x')` | `['startfile']` | none |
| `os.posix_spawn(...)` | `['posix_spawn']` | none |
| `os.putenv('K', 'v')` | `['putenv']` | none |
| `import urllib3` | `['urllib3']` | none — its root is not `urllib` |
| `import webbrowser` | `['webbrowser']` | none |
| `import ftplib` | `['ftplib']` | none |
| `from xmlrpc.client import ServerProxy` | `['xmlrpc']` | none |

And one false positive: `from .socket import helper` — a **relative** import of a
first-party module — reports `socket` and fires the egress ban. `dir(os)` on this interpreter
carries 19 exec/spawn/env names; `FORBIDDEN_OS_ATTRS` lists 9.

**This is the argument for §1's DD25 more than for longer lists.** Every list above can be
extended, and every extension is another list that is short by some name not yet thought of.

### 0.4 A runtime refusal is available with no banned import, and the suite is already clean under it

`sys.addaudithook` needs only `sys`. Measured in child interpreters:

- `socket.socket()` raises exactly one audit event, **`socket.__new__`**, before the object
  exists; a hook raising on it refuses the socket.
- `socket.create_connection(("example.invalid", 80))` raises **`socket.getaddrinfo`** first,
  so a refusal lands before DNS is attempted.
- **The whole current suite, 26 tests, run under an observing hook, raises zero network
  events** and passes in 1.03s.

An audit hook sees what an AST scan cannot — `importlib`, a library that opens a URL, a name
not on any list — but only on code the process **executes**, and only in the process that
installed it. A child interpreter does not inherit it.

### 0.5 `datetime` is a `date`, and a guard that compares it is refusing by accident

`issubclass(datetime, date)` is `True`, so `isinstance(datetime(2015, 1, 1), date)` passes a
type check written against `date`. Comparing the two then raises
`TypeError: can't compare datetime.datetime to datetime.date`. curvecast's
`FactorSpace.__post_init__` compares `sample_end > SEAL_BOUNDARY` and would therefore refuse
a `datetime` — by `TypeError`, not by the `ValueError` its message was written for. A guard
that refuses the right input for the wrong reason is one refactor away from accepting it.

### 0.6 curvecast's windows, read from source

`curvecast/src/curvecast/pit/seal.py`: `DEV_START = date(1988, 1, 1)`,
`DEV_END = date(2014, 12, 31)`, `VAL_END = date(2018, 12, 31)`, `SEAL_BOUNDARY = VAL_END`.
DEC-1 of the approved plan fits every object on **1988-01-01 → 2014-12-31**, "matching
curvecast's DEV exactly" — which is `DEV_START`/`DEV_END`, not `FactorSpace`'s seal boundary.

### 0.7 The two tables the registers read

`BUILD_ORDER_D3_D16.md` §4 parses to **21 core rows** — D23, D3a, D5, D3b, D4, D6, D7a,
D7b, D8, D9, D10, D11, D12, D13, D14, D15, D16, D17, D18, D21, D22 — and §4.1 to **2 annex
rows**, D19 and D20; no overlap, no repeat. §5 parses to **20 claim rows**: 18 live, H12b
struck as annexed, H14 struck as withdrawn.

*(Corrected 2026-09-11, before the first run and after the bars were fixed. This sentence
first read "18 claim rows: 16 live". The parse output it cites printed twenty rows; the 18
was `AMENDMENT_A1` §5.6's own count — "Net claims: 16 → 18 rows" — carried over instead of
counted, and it excludes the unnumbered `SCENARIO_SIGNS` row and the two struck rows
differently. Found while writing C32's row-count assertion. No bar or prediction cited the
number.)*

**There is no H10, and there never has been.** `git log -S"H10" --all` returns **zero
commits** — no document in this repository's history has ever contained the string. The
sequence runs H1–H9, then an unnumbered row for `SCENARIO_SIGNS`, then H11. The gap sits
exactly where the unnumbered row sits, which is the likeliest explanation and is not recorded
anywhere.

### 0.8 Licences, measured two ways, and the two ways disagree

FRED's copyright category (`cc` tag group) read through the API, the licensor's notice read
from the series notes, and the publisher of record's own policy page, all on 2026-09-11. The
page reads and the API reads agree on every tag.

| series | FRED `cc` tag | licensor's own words | observations |
|---|---|---|---|
| `DGS3MO` `DGS6MO` `DGS1` `DGS2` `DGS10` | public domain: citation requested | — (Board H.15) | 1962/1976/1981 → 2026-09-09 |
| `DFII5` `DFII10` `DFII30` | public domain: citation requested | — (Board H.15) | 2003/2010 → 2026-09-09 |
| `DEXUSEU` | public domain: citation requested | — (Board H.10) | 1999-01-04 → 2026-09-04 |
| `T10YIE` | **copyrighted: citation required** | none; computed by FRB St. Louis from `DGS10` and `DFII10` | 2003-01-02 → |
| `VIXCLS` | copyrighted: citation required | *"Copyright, 2016, Chicago Board Options Exchange, Inc. Reprinted with permission."* | 1990-01-02 → |
| `BAA10Y` `AAA10Y` | **copyrighted: citation required** | Moody's: *"MAY NOT BE COPIED OR OTHERWISE REPRODUCED, REPACKAGED, FURTHER TRANSMITTED, TRANSFERRED, DISSEMINATED, REDISTRIBUTED OR RESOLD … WITHOUT MOODY'S PRIOR WRITTEN CONSENT."* | 1986/1983 → |
| `BAMLC0A0CM` *(not in this universe; the precedent)* | copyrighted: pre-approval required | ICE: *"Reproduction of this data in any form is prohibited except with the prior written permission of ICE Data Indices."* and *"Starting in April 2026, this series will only include 3 years of observations."* | **2023-09-12** → 2026-09-10 |
| GSW `SVENY*` (`feds200628.csv`, not on FRED) | — | Board: *"Unless otherwise indicated, information on Board's website is in the public domain and may be copied and distributed without permission. Please cite to the Board as the source of the information."* | the file curvecast pins |

Four findings, each of which changes something built here:

1. **The ICE truncation is confirmed, not remembered.** BUILD_ORDER §0 item 4 recorded it on
   2026-09-05; the API now reports `observation_start = 2023-09-12`, three years back from
   today to the week.
2. **FRED's tag is not the licence.** For `BAA10Y` and `AAA10Y` the tag says *citation
   required* and the licensor's notice forbids reproduction and redistribution outright. A
   register that recorded the tag would record the weaker of two statements about the same
   bytes.
3. **Arithmetic changes the tag.** `T10YIE` is `DGS10 − DFII10`, two public-domain series,
   and carries *copyrighted: citation required*. curvecast's D166 had already declined to
   ingest it for a different reason — the construction covers the same 3,002 DEV dates with
   2,307 own-vintage rows against 233. The licence points the same way.
4. **curvecast already commits restricted rows.** `tests/fixtures/block_j_vintages_dev.csv`
   carries **7,253** `BAA10Y`, **8,000** `AAA10Y` and **6,298** `VIXCLS` rows, and
   `vix_daily_dev.csv` another **6,298** `VIXCLS`. Neither curvecast, deskcraft nor MEIP has a
   git remote, so nothing has been redistributed. **A copy sent to anyone would carry them.**

### 0.9 The fallbacks exist, and most share an originator

- **Treasury's Daily Par Yield Curve Rates** — data.gov lists publisher *Office of Debt
  Management* and licence **CC0 1.0**. The **Par Real Yield Curve** carries the same CC0
  licence (read from a data.gov search result, not from the dataset page itself).
- **H.15's constant-maturity yields are Treasury's numbers.** FRED's `DFII5` notes refer the
  reader to *"the Treasury Yield Curve Methodology"*, and FRB St. Louis has read its spread
  inputs *"directly from the U.S. Treasury Department"* since 2019-06-21. So Treasury.gov is a
  second **publisher** for `DGS*` and `DFII*`, not a second **originator**.
- **Cboe publishes `VIX_History.csv`**, *"VIX Index data for 1990 to present (Updated
  Daily)"*; the page carries a no-warranty statement and no redistribution terms.
- The nominal-yield-curve page is *"Last Update: November 05, 2019"* while the file it serves
  runs to 2026-07-24 — the page date is not the data date.

### 0.10 M18a's "every citation is corrected" missed one

`pyproject.toml:104` still names `test_the_llm_edge_is_scanned` and gives it the id **C10**, in
a parenthesis straight after the name. That test claims **C23**. A scan for the form
*backticked test name, then a parenthesised id* over every `.md`, `.py` and `.toml` file finds
**two** citations in the repository, and this is the one that is wrong. *(This paragraph avoids
writing the stale citation in that form, so that quoting a defect does not reproduce it for
C38 to find.)* M18a named the
three documents it corrected; the fourth place that cited the pair was a comment, and no gate
reads comments. curvecast met the same defect on 2026-08-26 (`8f77d68`): *a gate that checks
every bar is claimed cannot check that a claim points at the right test.*

---

## 1. Decisions

### DD22. Every Python file carries exactly one policy, and the strict one is the default

The owner's decision, on the recommendation below. Two policies:

- **ENGINE** — egress, execution, environment and credentials, broker SDK, imperative
  phrases, the LLM edge. All six.
- **HARNESS** — egress, broker SDK, the LLM edge. Granted to the top-level `tests/` directory
  **by name**, and to nothing else.

A file's policy is decided by where it sits, before anything about its contents is read. A
directory nobody has named arrives ENGINE. The seven bars stop choosing roots and ask the
census which files a ban reaches.

Why the whole ban and not the egress half, on the institutional test the owner set:

1. **Egress without execution is not an egress ban.** `subprocess.run(["curl", …])` leaves
   the process without importing a network module. A repository that allows execution allows
   egress by one level of indirection, and a guard that can be stepped around that way is a
   guard in name.
2. **Nothing planned needs more.** D23, D3b and D17 fetch in curvecast, which has the egress,
   the floor grading and `make_sealed_panel.py`'s precedent. deskcraft receives files.
3. **Loosening later is cheap and tightening later is costly.** C4 already says a package that
   needs an environment variable *edits the test with a recorded reason*. Tightening after a
   `scripts/` directory exists means auditing everything it already did — M10 again.
4. **It keeps DD1 true of the repository, not of two directories.** The paper can say *no
   code in this repository can reach the network, start a process or read the environment*,
   and have a bar behind every word.

What it costs, and it is stated because a reader will ask: **no process orchestration in
deskcraft** — no gate runner, no PDF build, no worker pool. What needs a child process lives
in `tests/`, as C5 already does, or in curvecast.

This is how a risk function separates data acquisition from computation: the component that
computes the risk number cannot fetch, so every number it produces is traceable to an input
someone committed. That is the property a model validator audits first.

### DD23. A file the scanner cannot read may not exist

`.ipynb`, `.pyw`, `.sh`, `.bash`, `.ps1`, `.psm1`, `.bat`, `.cmd` are refused anywhere in the
working tree. The scan reads `.py` source; a notebook's cells and a shell script's commands
are invisible to it, and a guard over a set the adversary can leave is a guard over nothing.
Refusing is simpler than parsing and is cheap to reverse with a recorded reason.

### DD24. The working tree is scanned, not the git index

A new, untracked `scripts/fetch.py` must turn the build red **before** it is committed, and a
scan of `git ls-files` would not see it until afterwards. Two things are excluded, both by
what they are rather than by name: `.git/`, which is a database, and any directory holding a
`pyvenv.cfg`, which is an interpreter. Git-ignored directories such as `scratch/` and `build/`
**are** scanned — `.gitignore` is a list of what not to commit, not a list of what may run
unguarded in this tree.

### DD25. A runtime refusal beside the static one, and its reach stated exactly

`tests/egress_guard.py` defines an audit hook refusing the network events of §0.4, and
`tests/conftest.py` installs it for the whole test process. It needs only `sys`, so it trips
no ban. It covers what the AST scan cannot — `importlib`, library URL reads, names absent from
every list — **on every code path a test executes, including engine code a test calls.**

What it does not cover, stated here so it is not discovered: code no test executes; any child
process, which does not inherit the hook; and execution itself, which the harness keeps
because C5 needs a fresh interpreter. Execution is therefore a proxy route out of the harness,
and §2 says so.

### DD26. The engine's imports are a census, not a deny-list

`ENGINE_IMPORT_ROOTS` is the **exact** set of top-level modules that ENGINE files import —
an equality, following `MODULES` — and it is asserted **disjoint** from every banned list. A
new import anywhere under ENGINE policy turns the build red until it is recorded. That is
default-deny applied to capability itself: `urllib3`, `webbrowser`, `importlib` and every
module §0.3 did not think of arrive refused, without a list having to name them.

An equality rather than an allow-list for the same reason `MODULES` is one: an allow-list only
grows, and a list of what was once imported becomes a list of what may be imported. It needs
no upstream grant ahead of time either — `numpy` and `meip` are recorded by D4 in the commit
that first imports them, where the diff shows it.

### DD27. The name lists are widened anyway, because the harness has no census

The harness imports `pytest`, `subprocess`, `tomllib` and whatever a test needs, so a census
there would be churn. It keeps the deny-lists, and they are widened to close §0.3:

- `NETWORK_MODULES` gains `ftplib`, `imaplib`, `nntplib`, `poplib`, `telnetlib`, `xmlrpc`,
  `socketserver`, `ssl`, `asyncio`, `webbrowser`, `urllib3` — mirrored into the import-linter
  contract, which C8 requires.
- The os scan resolves **aliases** (`import os as o`) and treats `from os import *` as
  reaching every banned attribute. The execution family is completed to the `exec*`,
  `spawn*`, `posix_spawn*`, `fork*` and `startfile` names; environment gains `environb`,
  `getenvb`, `putenv`, `unsetenv`. The scan reads source, so POSIX-only names are listed
  though this interpreter lacks them.
- **Relative imports are first-party** and no longer reported as top-level roots, which
  removes §0.3's false positive.

### DD28. `FitWindow` is a type, and it refuses on the axis it was written for

`FitWindow(start, end)`, frozen, both fields **exactly** `date` — `datetime` refused by
`TypeError` on purpose (§0.5), not by accident. It refuses `start < DEV_START`,
`end > DEV_END` and `start >= end`. `DEV_START` and `DEV_END` are restated in
`deskcraft.window` and **checked against curvecast's source at test time**, parsed rather than
imported, in C9's shape: deskcraft does not import curvecast yet, and a guard that needs an
environment to run stops running.

The start bound is refused as well as the end, because DEC-1 fixes the fit sample *exactly*
and D14's out-of-sample claim compares objects fitted on one sample. A package that needs a
pre-1988 fit edits the bound with a recorded reason.

### DD29. `FitWindow` governs estimators, and a replay window is a different type

D12 computes **realised correlations on the 2020 window**, which `PLAN_deskcraft.md` §9
requires — using full-sample correlations to stress a crisis is circular. That is a
measurement *of* the scenario, not a fitted object used out of sample, and it must not be
blocked by this guard or smuggled past it. So: an object whose output is used to forecast or
size out of sample takes a `FitWindow`; a replay window is D12's own type, carries its own
guard, and never feeds an estimator. Stated now, because the first package to meet the
distinction is eight packages away.

### DD30. The claims register is data, and its agreement with §5 is a bar

`deskcraft.registers.CLAIMS` holds §5's table: id, statement, scorer, predicted verdict,
status, and — for a withdrawn claim — its successors. A bar parses §5 and compares ids,
scorers, statuses and predictions, so the document a reader sees and the data a gate enforces
cannot drift. The statement text is not compared: markdown emphasis is presentation.

Every live claim's scorer must be a **core** package, an annexed claim's an **annex** package,
and every scorer must be hosted **here** — which is what lets closure be read from this
repository alone. D23 carries no claim, deliberately (`AMENDMENT_A1` §3.5).

### DD31. A verdict is recorded if and only if its scorer has closed, and closure is derived

The build order's words are *"the gate fails if a claim has no scorer, or if the scorer has
landed and the claim is unscored."* That is half of an iff. The other half — a verdict
recorded for a claim whose scorer has **not** landed — is a fabricated result, and it is the
more dangerous half. Both are refused, in D2's `Neutrality` shape.

A package is closed when `docs/PRECOMMIT_deskcraft_<id>_*.md` exists. Derived, not declared:
one commit carries a package's document and its code, so the document existing on a commit is
the package landing. The consequence is intended friction: **the scorer's own suite is red
from the moment its pre-commit document is written until its verdicts are recorded**, which
is what makes an unscored claim a build failure rather than a promise.

### DD32. The gap in the numbering is recorded, not renumbered

§0.7. `H10` is declared a gap in `NUMBERING_GAPS`, and a bar asserts the numbered ids are
contiguous **except** for declared gaps — so a claim deleted from both the register and §5 in
one commit still turns the build red. Renumbering H11–H17 down would move eight ids already
cited by `AMENDMENT_A1`, `RESEARCH_client_solutions_layer.md` and both abstracts, for the same
reason M18a moved the newer pair and not the older: a closed record's ids are the stable ones.
`SCENARIO_SIGNS` keeps its name and no number.

### DD33. `PACKAGE_BUDGET` is an equality, which is stricter than the amendment

`AMENDMENT_A1` §6.2 says the gate fails *"when the count of core packages in the order table
exceeds it."* This package asserts **equality**, and the difference is a scope failure the
amendment's form cannot see: **a package deleted from the core without being moved to the
annex** — the readout, the backtest nobody wants to run — passes a ceiling silently. Moving a
package to the annex remains allowed at any time; under equality it costs one edited constant,
which is the visibility §6.2 was asking for in the other direction. Annex and core are
asserted disjoint, and no id may appear twice.

Closed packages stay in the table and in the count. One-in-one-out's *earned* condition — that
a package closed before one was added — is a fact about history and is not checked (§2).

### DD34. The source register records the licensor's words, and the operative licence is the stricter

§0.8 finding 2. `Licence` is ordered — `PUBLIC_DOMAIN` < `CITATION_REQUIRED` <
`PRE_APPROVAL_REQUIRED` < `REDISTRIBUTION_PROHIBITED` < `UNMEASURED` — and each row records
FRED's tag and the notice separately. The licence a row answers with is the **maximum** of the
two. Contamination is monotone here as it is in curvecast's `worst_of`: there is no operation
on two statements about the same bytes that makes either one weaker.

`UNMEASURED` is the strictest value, not a missing one, for `UnknownSeries`' reason: a
default here hands the strongest permission to the weakest evidence.

### DD35. Only a public-domain series is committable

`Source.committable` is derived: `licence is PUBLIC_DOMAIN`. Citation-required copyright is
not a licence to redistribute, and a fixture committed to a repository sent to an institution
is redistribution. **D3b inherits this as a refusal**: a fixture carrying a non-committable
series does not land. By §0.8 that excludes `VIXCLS`, `BAA10Y`, `AAA10Y` and `T10YIE` — the
last with a construction that is committable and that curvecast's D166 already prefers.

This is an engineering rule, conservative on purpose. It is not a reading of anyone's contract
and no row claims to be.

### DD36. A fallback names its originator, so a mirror is not mistaken for a second source

Each row names its originator — who computes the number — and its publisher — where it is read
today. A fallback names its own originator, and `independent_fallback` is derived as *the
originators differ*. §0.9 is why: Treasury.gov behind `DGS10` protects against FRED or the
Board withdrawing the series, which is exactly what ICE did through FRED, and it does not
protect against Treasury changing its method, because they are the same number.

Two laws, both iffs, refused at construction: **a fallback is absent iff a reason is given**,
and **a fallback originator is named iff a fallback is**.

The universe is DEC-2's US series, D5's four front-end series, and every component of
`REFERENCE_BOOK`. A bar makes the book's components a subset, so a leg cannot name a series
the register has never seen. Every series `US_CASH_BOOK` prices from must carry a measured
licence; a series reachable only through a deferred leg may be `UNMEASURED`.

### DD37. The foreclosure is written into curvecast's ledger before the first post-DEV row is read

DEC-1 reads 2015 → present, and curvecast's seal cannot see a sibling repository doing it. So
the non-look entry is written **now**, in `curvecast/docs/TRIAL_LEDGER.md`, taking effect at
deskcraft's first read of a row dated after `DEV_END` — none has occurred; deskcraft holds no
data file. It spends no look and no trial: no `UnsealToken`, no curvecast hypothesis, nothing
imported from `curvecast.evaluation`.

What it forecloses is wider than the plan's *"anything curve-shaped"*, and deliberately so:
**any curvecast hypothesis about a series in deskcraft's source register over 2015 →
present**, since deskcraft will read `DEXUSEU`, `VIXCLS` and the credit spreads as well as the
curve. The wider scope is the less flattering one to curvecast's remaining budget, which is the
direction a ledger should err in. `make_sealed_panel.py` says *"Extraction is not an unseal"*,
and that is true; the entry records the rest of it — what a person has read cannot be unread.

A bar here parses the ledger for the entry, so it cannot be removed quietly from the repository
that would benefit from removing it.

### DD38. Citations of a test by name carry the id that test claims

§0.10. Every `` `test_name` (Cnn) `` in a `.md`, `.py` or `.toml` file must name the id the test
claims. `pyproject.toml:104` is corrected to C23 in this commit, and the bar is watched failing
on it first.

---

## 2. What this package does not do

- **It is not a sandbox.** The boundary is a static scan plus an in-process audit hook on
  test-executed paths. There is no OS-level network isolation, no container and no CI runner.
  An institutional deployment would add a network-denied runner; this repository has none,
  and the paper says *enforced by static analysis and an in-process runtime check*, never
  *isolated*.
- **It does not stop deliberate evasion.** `getattr(os, name)`, `exec` of a string,
  `__import__`, `ctypes` and a `-c` string handed to a child interpreter all defeat an AST scan.
  The engine's import census refuses `importlib` and `ctypes` until recorded; the harness has
  no census, and a test that starts a process can leave through it.
- **No data, no panel, no estimator.** `FitWindow` has no consumer yet; the guard that *every
  estimator takes a `FitWindow`* is D8's, where the first estimator lands. `src/` still opens
  no file — closure and parity are read by bars, not by the registers.
- **It does not repair curvecast's committed rows** (§0.8 finding 4). curvecast is modified
  here by one ledger entry and the pending hash in its handoff, and by nothing else.
- **It does not interpret a licence.** Rows classify the words a licensor published, on a
  date, with the URL. Committability is a conservative engineering rule.
- **It does not check that a package was earned.** The budget makes an addition or a removal
  visible; whether one package closed before another was added is history, and unchecked.
- **It does not check a multi-clause bar for implication** (`BUILD_ORDER` §6). That audit stays
  manual and is recorded as such.

**Known residuals for the paper's limits, in one place:**

| residual | why it stays |
|---|---|
| A harness process can leave through execution | C5 needs a fresh interpreter; the hook is per-process and a child does not inherit it |
| A name list is finite | The engine is covered by the census (DD26); the harness is not |
| Code no test executes is invisible to the runtime hook | The hook sees execution, not source |
| Dynamic attribute and import forms | No static scan resolves them |
| An `UNMEASURED` licence on a deferred leg's series | Measured when DEC-2's cross-market package opens |
| Fallback licences are not all measured on the file itself | `VIX_History.csv` and the Board's EBP/GZ file are named from their pages, not their terms |

---

## 3. Verification

### 3.1 Bars

| bar | what would falsify it | executable |
|---|---|---|
| **B25** | A Python file the boundary does not reach, or one reached by two policies. Walking the working tree (DD24), every `.py` file receives exactly one of ENGINE or HARNESS; HARNESS is held by the top-level `tests/` alone; the census today is `{src: ENGINE, tests: HARNESS}`; every one of the six bans reaches a non-empty set. **Mutation (C25b), through the same functions, in `tmp_path`:** a `scripts/a.py`, a `tools/b.py` and a top-level `c.py`, each carrying every banned capability, fire **all six** bans; a `tests/d.py` carrying the same fires **exactly** egress, broker and LLM edge; a file inside a directory holding `pyvenv.cfg`, and one inside `.git/`, are not scanned. | C25, C25b |
| **B26** | A file the scanner cannot read (DD23). Zero `.ipynb`, `.pyw`, `.sh`, `.bash`, `.ps1`, `.psm1`, `.bat`, `.cmd` in the working tree outside the DD24 exclusions. **Mutation:** each suffix planted in `tmp_path` is reported, and a `.py` beside them is not. | C26 |
| **B27** | Capability arriving in the engine under a name no list carries (DD26). The top-level modules imported by ENGINE files equal `ENGINE_IMPORT_ROOTS` exactly, and that set is disjoint from the network, execution, credential and broker lists. **Mutation:** a `scripts/a.py` importing `urllib3` — which §0.3 measured the network list missing — changes the census. | C27 |
| **B28** | §0.3's nine escapes and its false positive (DD27). Through the shipped scanners: `import os as o; o.system`, `from os import *`, `os.startfile`, `os.posix_spawn`, `os.putenv` fire; `urllib3`, `webbrowser`, `ftplib`, `xmlrpc.client` fire; `from .socket import helper` does **not**, and `from socket import create_connection` does. The widened network list is inside the import-linter contract. | C28 |
| **B29** | Egress at run time by a route the scan cannot see (DD25). In this process, `sys.audit("socket.__new__", …)` is refused by the guard's own exception type. **Treatment and control, each in a fresh interpreter:** with the guard installed from `tests/egress_guard.py`, a real `socket.socket()` is refused by that exception; with only an observing hook, the same line is seen to raise `socket.__new__` — so the event is real, it fires before any socket exists, and the refusal is the guard's. **No socket is created in either arm.** | C29 |
| **B30** | A fit reaching past DEV, or starting before it (DD28). `FitWindow` refuses `end` one day past `DEV_END`, `start` one day before `DEV_START`, `start == end`, `start > end`, a `datetime` in either field **with `TypeError`**, and a string; it accepts `(DEV_START, DEV_END)` exactly; it is hashable, and assigning a field raises `FrozenInstanceError`. | C30 |
| **B31** | deskcraft's DEV drifting from curvecast's. `DEV_START` and `DEV_END` equal the values assigned in `curvecast/src/curvecast/pit/seal.py`, read by AST. **Skips loudly** if curvecast is absent. | C31 |
| **B32** | The register and §5 disagreeing (DD30). Parsed from `BUILD_ORDER_D3_D16.md` §5: the same ids, the same scorer per id, struck-through exactly on the non-live rows, annexed and withdrawn told apart by the row's own word, and the same predicted verdict on every live row. **Mutation:** the parser over a copy of §5 with one scorer changed, and over one with a row removed, both disagree with the register. | C32 |
| **B33** | A claim scored by nothing, or by the wrong thing (DD30, DD32). Every live claim's scorer is a core package, every annexed claim's an annex package, no scorer is D23; a withdrawn claim names successors that exist and are live; the numbered ids are contiguous except for `NUMBERING_GAPS`, which is exactly `{10}`. | C33 |
| **B34** | An unscored claim whose scorer landed, or a verdict whose scorer did not (DD31). Over `docs/`: every live claim has a verdict **iff** its scorer's pre-commit document exists. **Mutation, both ways, in `tmp_path`:** a `PRECOMMIT_deskcraft_d12_x.md` with `SCENARIO_SIGNS` unscored is refused, and a verdict on H3 with no D6 document is refused. D1 is not mistaken for D12 by the glob. | C34 |
| **B35** | The core growing, or shrinking, silently (DD33). The core rows of §4 number exactly `PACKAGE_BUDGET`; the annex rows are disjoint from them; no id appears twice. **Mutation:** a table with a 22nd core row, one with 20, and one whose annex repeats a core id each fail. | C35 |
| **B36** | A series a book names that the register has never seen, or a licence weaker than its evidence (DD34–DD36). Every component series of `REFERENCE_BOOK` has a row; each row's key is its series; every series `US_CASH_BOOK` prices from has a licence other than `UNMEASURED`; the licence is the maximum of tag and notice; `committable` holds exactly on `PUBLIC_DOMAIN`. **Mutation:** a row with a public-domain tag and a no-redistribution notice is not committable; a missing fallback with no reason, and a fallback originator with no fallback, both raise at construction. | C36 |
| **B37** | The foreclosure being removed from the repository it constrains (DD37). curvecast's `TRIAL_LEDGER.md` carries the deskcraft non-look entry with **0** looks spent and the `DEV_END` trigger. **Skips loudly** if curvecast is absent. | C37 |
| **B38** | A test cited under the wrong id (DD38). Every `` `test_name` (Cnn) `` in a `.md`, `.py` or `.toml` file in this repository names the id that test claims, and every test so cited exists. **Mutation:** the line `pyproject.toml:104` carried before this commit is reported. | C38 |

### 3.2 Predictions

- **P1. No existing bar changes verdict.** The policy census reproduces §0.1's roots exactly for
  every ban on today's tree, so C1–C24b — 26 tests — pass unchanged through the refactor.
- **P2. C38 is red on the tree as it stands**, on exactly one citation, `pyproject.toml:104`, and
  green once it is corrected. Watched, not inferred — C1's red at D2 was never observed, and this
  one will be.
- **P3. D3a adds no import root.** `deskcraft.window`, `deskcraft.registers` and
  `deskcraft.sources` import only from §0.2's seven, so `ENGINE_IMPORT_ROOTS` ships as exactly
  those seven.
- **P4. The runtime guard fires on no existing test**, as §0.4 measured with an observing hook,
  and the child treatment is refused by the guard's own exception type.
- **P5. Every new bar passes on its first complete run except C38** (P2). *(Both previous
  packages missed their first-run prediction, D1 on two bars and D2 on one, so this is the
  prediction most likely to miss and it is written down anyway.)*
- **P4a. The treatment child is refused by the guard's own type, and the control child's
  observer sees `socket.__new__`** — the order §0.4 measured, confirmed inside the bar rather
  than carried over from the measurement.
- **P6. `lint-imports` still reports 2 kept, 0 broken** with eleven more forbidden modules in the
  egress contract. It could fail: import-linter may refuse a standard-library name it cannot
  resolve, which is how M18's gate died.
- **P7. The end-to-end demonstration fires exactly eight bars.** One file, `scripts/probe.py`,
  placed in the real tree and carrying `requests`, `subprocess`, `os.getenv`, `kiteconnect`,
  `meip.lpal` and *"you should"*, turns **C2, C3, C4, C5, C6, C15, C23 and C27** red — and no
  others; C25 stays green, because `scripts/` receiving ENGINE is the census working. A
  `scratch.ipynb` placed alone turns **C26** red. Removing both returns every bar to green.
- **P8. curvecast's `run_gates.py` exits 0 with no gate RED** on the tree carrying the ledger
  entry — the property, not a count (`AMENDMENT_A1` §10 row 2).
- **P9. Upstream stays untouched except where stated.** curvecast's diff is the ledger entry and
  its handoff row only; MEIP's tree is clean; `EXEMPT_FIELDS` is still `{}`.

### 3.3 Result

**15 new executable bars, all passing; the suite goes 26 → 41 tests, 0 failed, 0 skipped.**
`lint-imports` reports **2 kept, 0 broken** with eleven more forbidden modules; MEIP's reports
**6 kept, 0 broken**; curvecast's `run_gates.py` **40 of 40, exit 0**. The bars and predictions above are as
they stood at 20:01:47 (sha256 `4fb28e46…` of this file then); one §0 sentence was corrected
after that and before the first run, annotated in place at §0.7.

#### Three runs, and the first one measured the wrong tree

| run | tree | result | red |
|---|---|---|---|
| 1 | **incomplete**: the contract widening had not applied and the ledger entry was not yet written | 37 passed, 4 failed | C8 and C28 on the contract; C37 on the ledger; **C38 on `pyproject.toml`'s citation** |
| 2 | complete, with the stale citation still in place | 40 passed, 1 failed | **C38 only, on that one citation** |
| 3 | citation corrected | **41 passed** | none |

Run 1 happened because the edit widening `pyproject.toml`'s contract and the suite that
verifies it were issued in one batch; the edit was refused — the file had not been read in
that session — and the suite ran anyway, against a tree without it. Every red in run 1 was
traced to its cause before anything else was touched, and each was the expected one. **The
lesson is procedural and cheap: never issue an edit and the run that verifies it together.**
It is recorded because a run on the wrong tree that happens to go green is indistinguishable,
afterwards, from a verification.

#### Predictions, scored

| | outcome |
|---|---|
| **P1** no existing bar changes verdict | **hit** — measured directly, not inferred from green: for each of the six bans the census's file set is **identical** to §0.1's root set on today's tree (11/11 egress, broker and LLM edge; 6/6 execution, environment and imperative). C1–C24b pass in runs 2 and 3. C8 was red in run 1 only, on the unapplied contract edit — the incomplete tree, not the refactor |
| **P2** C38 red on exactly one citation, then green | **hit, watched twice** — runs 1 and 2 each report exactly `pyproject.toml: cites test_the_llm_edge_is_scanned as C10; it claims C23`; run 3 is green |
| **P3** D3a adds no import root | **hit, with a disclosure.** `ENGINE_IMPORT_ROOTS` ships as §0.2's seven and C27 passes on them. But `deskcraft.registers` was first written importing `re`, and was changed to string methods **before any run and after this prediction existed** — so the prediction held partly because of an implementation choice made knowing it. The choice stands on its own (a four-comparison id check does not need the regex engine in the census), and the sequence is stated so a reader can weigh it |
| **P4** the runtime guard fires on no existing test | **hit** — 41 pass under it, and a refusal inside any test would have raised |
| **P4a** treatment refused by the guard's type; control sees `socket.__new__` | **hit** — `REFUSED` and `SEEN socket.__new__`, and no socket was created in either child |
| **P5** every new bar passes on its first complete run except C38 | **hit on run 2**, the first run on the complete tree. Run 1 had four reds on an incomplete one; it is in the table above, so a reader who counts it as the first run can score this a miss |
| **P6** `lint-imports` still 2 kept, 0 broken | **hit** — "Analyzed 12 files, 19 dependencies", both contracts KEPT. import-linter accepted all eleven standard-library names |
| **P7** the end-to-end demonstration fires exactly eight bars | **hit, both halves.** `scripts/probe.py` in the real tree turned **exactly C2, C3, C4, C5, C6, C15, C23 and C27** red — 8 failed, 33 passed — and C25 stayed green. `scratch.ipynb` alone turned **exactly C26** red. With both removed, 41 passed |
| **P8** curvecast's sweep exits 0 with no gate RED | **hit** — `exit=0`, **40 passed, 0 failed, 0 skipped** in 2038s, on `9153ff7` plus the two ledger docs (the tree committed as curvecast `93ebdec`). Scored on the property; the count is recorded because it was read off the run. `curvecast:pytest` 1030 passed, 21 skipped in 918.9s; `meip:pytest` 1410 passed; `curvecast:ruff` 29 findings, all pre-existing |
| **P9** upstream untouched except where stated | **hit** — at the sweep, curvecast's `git status` was `docs/TRIAL_LEDGER.md` and `docs/HANDOFF_curvecast.md` and nothing else of D3a's (the owner's untracked `docs/TODO_pit_hardening_and_power.md` predates this package and was not added); `meip:untouched` printed *unmodified* and MEIP's tree is clean at `c1e383e`; `EXEMPT_FIELDS` is `{}` under C9, green in all three runs. **One disclosure:** the handoff row's *"Verified 40 of 40"* sentence was written after the sweep, since it reports it; no curvecast gate parses that file — its four mentions in curvecast's Python are two docstrings and two comments |

#### What measurement found that the plan did not

1. **FRED's copyright tag understates the licence on the credit spreads.** §0.8 finding 2, and
   the reason `Source.licence` is a maximum and not a field. A register built from the API
   alone would have marked `BAA10Y` citation-required and let D3b commit it.
2. **curvecast already commits the restricted rows** — 7,253 `BAA10Y`, 8,000 `AAA10Y` and
   12,596 `VIXCLS` across two fixtures. Nothing has left this machine, because no repository
   here has a remote. **Before any copy of curvecast leaves it, the owner decides** what those
   fixtures become; D3a records it in curvecast's handoff and changes nothing there.
3. **Arithmetic acquires a copyright.** `T10YIE` is two public-domain series subtracted and is
   tagged copyrighted. The register's fallback — the subtraction itself — is committable, and
   curvecast's D166 had already preferred it on vintage coverage, for an unrelated reason.
4. **Most fallbacks share an originator.** Of 21 rows, **11** have a fallback from a different
   originator, **9** have one from the same originator — a second publisher of Treasury's or the
   Board's own number — and **1** has none. The register protects against a distributor
   withdrawing a series, which is what happened with ICE; for nine rows it does not protect
   against the originator stopping, and it says so per row.
5. **H10 never existed** (§0.7), and the register now declares the gap rather than leaving a
   reader to wonder whether a claim was deleted.
6. **M18a's "every citation corrected" was false in one place** (§0.10), in a comment no gate
   read — the second time in this project a renumbering's tidy-up missed a copy, after curvecast
   `8f77d68`. C38 reads comments.
7. **This document transcribed a count instead of taking it** (§0.7: "18 claim rows" from the
   amendment's arithmetic, against a parse output printing 20). Caught by writing the bar that
   counts them — the same defect `AMENDMENT_A1` §10 recorded when a gate count was *copied
   rather than read off the run*.

**One pre-existing finding, not D3a's:** ruff's default rules report `F401` — `Leg` imported and
unused — at `tests/test_book_types.py:30`. That file is unchanged by this package and the finding
reproduces at `ef08144`; it is left for the package that next touches D2's tests.

#### What was built

| | |
|---|---|
| `src/deskcraft/window.py` | `DEV_START`, `DEV_END`, `FitWindow` |
| `src/deskcraft/registers.py` | `PACKAGE_BUDGET`, `Claim`, `ClaimStatus`, `Verdict`, `CLAIMS` (20 rows), `NUMBERING_GAPS` |
| `src/deskcraft/sources.py` | `Licence`, `OriginatorClass`, `Source`, `SOURCE_ROWS` (21 rows), `SOURCES` |
| `src/deskcraft/__init__.py` | docstring only: the ban is now a property of the working tree |
| `tests/test_deskcraft_boundary.py` | the policy census; one `offences` function every capability bar and its mutation read; the lists widened; aliases, star imports and relative imports handled; C5's self-skip removed; `MODULES` extended; **C25, C25b, C26–C29** |
| `tests/test_guards_and_registers.py` | **C30–C38** |
| `tests/egress_guard.py`, `tests/conftest.py` | the runtime refusal, installed for the whole test process |
| `pyproject.toml` | eleven modules added to the egress contract; the stale id corrected, with the reason beside it |
| curvecast `docs/TRIAL_LEDGER.md` | the non-look section and its one row — committed in curvecast as `93ebdec` |
| curvecast `docs/HANDOFF_curvecast.md` | `9153ff7` filled in; a row for the ledger entry and the licence finding — same commit |

#### What the next packages inherit

- **D5** — the four front-end series already have register rows, licence-measured public domain,
  each with a same-originator fallback. D5 adds their floors; the register is ready for them.
- **D3b** — `Source.committable` is a **refusal**: no fixture carrying `VIXCLS`, `BAA10Y`, `AAA10Y`
  or `T10YIE`. `T10YIE` arrives as `DGS10 − DFII10`, and `DGS10` needs a register row first.
- **D4** — the engine's import census: `numpy` and `meip` are recorded in `ENGINE_IMPORT_ROOTS`
  by the commit that first imports them, with the reason in that commit's pre-commit.
- **D6** — **the first verdict.** D6's suite is red from the moment its pre-commit document is
  written until H3's verdict is recorded in `CLAIMS` (DD31). That is the register working.
- **D8** — the guard that *every estimator takes a `FitWindow`*, over the first real estimator.
- **D12** — its own replay-window type (DD29), and `SCENARIO_SIGNS`, H6 and H7's verdicts.
- **The owner** — the decision on curvecast's committed Moody's and Cboe rows before any copy of
  that repository is sent anywhere.
