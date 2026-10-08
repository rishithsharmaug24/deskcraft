# D1 — repo scaffold and the inverted boundary test

Work package **D1** of `PLAN_deskcraft.md` §7. Deliverable: `pyproject.toml`, and the
**inverted** boundary test — *assert no broker SDK is importable, no credential is read, no
order path exists*. Bar: the test must **pass, and be shown to fail** when the thing it
forbids is present. Decisions **DD1–DD7**, bars **B1–B9** (executable as **C1–C9**),
predictions **P1–P5**.

Decisions are numbered `DD` because §7 already uses `D1…D8` for the work packages
themselves, and two numbering schemes sharing a letter is how a cross-reference stops
meaning anything.

`git init` was done on 2026-08-31 as a record-keeping commit (`2c8618f`) and deliberately
kept separate from this package: it carried no bar, and an empty git directory gates
nothing. **This** package is D1. Its bar is the boundary test passing and failing on
command.

---

## 0. Measured before decided

Measured **2026-08-31**.

### 0.1 The environment

`pytest` is present on the production interpreter
(`C:/Users/rishi/AppData/Local/Programs/Python/Python312/python.exe`), which is what
curvecast's gates already run on. `import-linter` is **absent from both** that interpreter
and MEIP's `.venv` — the same state curvecast is in, and the reason its contract check is
split into a declaration test that always binds and a runner that skips.

### 0.2 A broker SDK is installed on this machine, and that decides the test's shape

The workshop repository trades a live NSE book and has `kiteconnect` available to it. So an
assertion of the form *"no broker SDK is importable in this interpreter"* would be a
statement about the **machine**, not about **deskcraft**, and it would be red for reasons
that have nothing to do with this repo. What is checkable, and what is actually meant, is
that **deskcraft does not reach one**: it is not a declared dependency, it is not imported
by any module here, and importing `deskcraft` pulls none into `sys.modules`.

### 0.3 curvecast's boundary is lexical, and lexical will not work here

`tests/test_curvecast_boundary.py` bans field names carrying `notional`, `direction`,
`position`, `size`, `weight`, `side`, `order`. §3 of the plan is explicit that this does not
transfer: **`Direction` and `Notional` are the subject matter here**, which is the whole
reason this repo exists rather than an entry in `EXEMPT_FIELDS`.

So the vocabulary that curvecast forbids is the vocabulary deskcraft is *for*, and a
name-based guard would either ban the subject matter or degenerate into a list of
exceptions. §1 chooses a structural guard instead.

### 0.4 What of curvecast's boundary does transfer, checked rather than assumed

One half does, unchanged: `FORBIDDEN_RENDERED_PHRASES` — `buy`, `sell`, `go long`,
`go short`, `overweight`, `underweight`, `allocate`, `recommend*`, `you should`,
`take profit`. None of those is subject matter here. A risk decomposition of a stated book
never needs to say *"you should"*, and §3's working distinction — *this repo answers "what
is the risk of this book?", never "should you hold it?"* — is exactly what that list
enforces. It is ported verbatim.

### 0.5 The reverse import edge cannot be seen by a linter here

`lint-imports` reads one root package. Run in this repo it sees imports **made by**
deskcraft; it cannot see `curvecast` or `meip` importing deskcraft, which is the direction
that would make the edge two-way and put curvecast's sealed baselines at risk. curvecast
documents exactly this limitation about its own MEIP edge and answers it with an AST scan
(`tests/test_meip_edge.py::test_the_edge_is_one_way`). The same answer is taken here, over
both upstream repositories.

### 0.6 curvecast's gate count is 23 in this plan and is now 25

§8 of `PLAN_deskcraft.md` names *"must stay 23/23 green"*. curvecast's item 18 closed on
2026-08-31 and added two gates, so the correct figure is **25/25**. Corrected in §8 as part
of this package, because a gate expressed as a stale number is a gate that gets read as
failing and then ignored.

---

## 1. Decisions

### DD1. The boundary is structural, not lexical, and that inversion is the package

curvecast bans an order by banning the **words** that would express one, because its output
is text and a directive is one field name away. Here the output is **arithmetic on
positions**, the forbidden words are the permitted subject matter (§0.3), and a name scan
would be the *"policy enforced by whoever remembers it"* that curvecast's own boundary
docstring warns against.

So the ban is on **capability**, in three parts, each of which makes an order impossible
regardless of what anything is called:

1. **No egress.** `deskcraft` may not import `socket`, `urllib`, `requests`, `httpx`,
   `http`, `aiohttp`, `websockets` or `smtplib`. With no network there is no order path,
   whatever a function is named.
2. **No execution.** No `subprocess`, no `os.system`, no `os.exec*`.
3. **No credentials.** No `os.environ`, `os.getenv`, `getpass`, `keyring` or `dotenv`.

### DD2. No broker SDK, asserted about this repo rather than about this machine

A broker SDK is installed here for an unrelated repository (§0.2), so the checkable claim is
that deskcraft does not reach one: absent from the declared dependencies, absent from every
import in `src/` and `tests/`, and absent from `sys.modules` after `import deskcraft` in a
fresh interpreter. The last of the three is the one that would catch a transitive arrival.

### DD3. Reading no environment variable at all is stronger than reading secrets from env, and it is what this repo needs

The inherited rule is *secrets via env only*. deskcraft needs no secret: it consumes MEIP
functions and curvecast objects, and its inputs are stated books. So the rule is tightened
to **no environment access whatsoever**, which is a scan with no judgement in it. If a later
package genuinely needs one, it edits this test with a recorded reason — the same
self-correcting shape as curvecast's `MODEL_COUNTS`, and the opposite of an exemption list.

### DD4. Half of curvecast's boundary is ported verbatim, and which half is stated

`FORBIDDEN_RENDERED_PHRASES` transfers unchanged (§0.4); `FORBIDDEN_FIELD_TOKENS` does not
transfer at all. Both halves are recorded, because *"the boundary does not transfer"* left
unqualified is how the imperative ban would have been dropped along with the field ban.

### DD5. The one-way edge is asserted by scanning upstream, not by trusting a linter

`lint-imports` cannot see the reverse direction (§0.5). An AST scan over `curvecast/src` and
`meip/src` asserts neither imports `deskcraft`. It **skips** if a repository is not on this
machine rather than passing vacuously — a scan over a directory that does not exist finds
nothing and reports success, which is the failure mode the check exists to prevent.

### DD6. Every guard is mutation-tested in the test that uses it

Item 13's rule, inherited: a source-scanning guard shipped without a demonstration that it
fires is indistinguishable from a scan that looks for nothing. Each of the three structural
bans and the imperative scan carries a variant that is shown to be caught.

### DD7. The contract check is split, because import-linter is not installed

`test_import_contracts_are_declared` parses `pyproject.toml` and needs no tooling, so it
always binds and catches the realistic failure — a contract deleted or renamed into
uselessness. `test_import_linter_holds_the_contracts` runs the tool and skips when it is
absent, which on both interpreters it is (§0.1). curvecast's reasoning, adopted rather than
re-derived: a single skipping test would mean the contracts were guarded by nothing.

---

## 2. What this package does not do

- **No book, no leg, no `Direction`, no `Notional`.** Those are D2. This package deliberately
  ships an empty `deskcraft` package with a docstring, so that the guard is live *before*
  there is anything to guard — curvecast's WP-0 reasoning about `news/scoring.py`, which is
  the only ordering under which a guard can be trusted.
- **No arithmetic.** No VaR, no DV01, no covariance.
- **It does not touch curvecast or MEIP.** Both are read by the edge scan and modified by
  nothing.

---

## 3. Verification

### 3.1 Bars

| bar | what would falsify it | executable |
|---|---|---|
| **B1** | The package importing nothing today and therefore passing vacuously. `deskcraft` imports cleanly, the scanned source set is non-empty, and the module census is an **equality**, so both adding and deleting a module turn it red. | C1 |
| **B2** | Egress arriving by any route. AST scan over `src/` and `tests/`: none of the eight network modules is imported. **Mutation:** a synthetic module importing `requests` is shown to be caught by the same scanner. | C2 |
| **B3** | Execution arriving. No `subprocess`, `os.system` or `os.exec*` in `src/`. **Mutation:** a synthetic `subprocess` import is caught. | C3 |
| **B4** | A credential read. No `os.environ`, `os.getenv`, `getpass`, `keyring` or `dotenv` anywhere in `src/`, as attribute access as well as import. **Mutation:** a synthetic `os.getenv("KITE_API_KEY")` is caught. | C4 |
| **B5** | A broker SDK reached transitively. None of the broker names is a declared dependency, none is imported in `src/` or `tests/`, and a **fresh interpreter** that does `import deskcraft` has none in `sys.modules`. The subprocess leg skips only if the interpreter cannot be resolved. | C5 |
| **B6** | The half of curvecast's boundary that does transfer being dropped with the half that does not. The imperative phrase list is present, matches curvecast's, and no rendered string in `deskcraft` trips it. **Mutation:** a string containing *"you should"* is caught. | C6 |
| **B7** | The edge going two-way unnoticed. An AST scan over `curvecast/src` and `meip/src` finds no `import deskcraft`. **Skips** — loudly — if a repository is absent, rather than passing over an empty directory. | C7 |
| **B8** | A contract deleted or renamed into uselessness. `pyproject.toml` declares the three contracts by name, each `type = "forbidden"`, each with `deskcraft` among its sources, and every module a contract names exists. **Annotated 2026-09-09, not rewritten:** B8 checked that three contracts were *declared*, and nothing checked that any could be *evaluated*. One of the three -- the LLM edge -- names `meip.lpal`, a subpackage of an external package, which import-linter rejects outright and which aborts the entire run, taking the other two with it. The config also omitted `include_external_packages`, required whenever a forbidden module is external. So this gate returned **no verdict at all** between D1 and 2026-09-09, and the LLM edge -- the only one of the three with no AST counterpart -- was guarded by nothing. The ban is now C23 (shipped as C10, renumbered the same day off a collision with D2's C10 — `AMENDMENT_A1` M18a); C8 additionally asserts the flag and refuses any forbidden module carrying a dot. `AMENDMENT_A1` M18. | C8 |
| **B9** | `EXEMPT_FIELDS` acquiring a first entry next door. curvecast's boundary constant is read from its own file and asserted empty, from here, because the thing most likely to be relaxed by this repo's existence is the constant that made this repo necessary. Skips if curvecast is absent. | C9 |

### 3.2 Predictions

- **P1.** Every bar B1–B9 passes on the first run. *(Ranges over the executable bars C1–C9,
  not over this table.)*
- **P2.** All four mutation legs (C2, C3, C4, C6) catch their variant.
- **P3.** C5's subprocess leg runs rather than skips, and finds zero broker modules in
  `sys.modules`.
- **P4.** C7 and C9 run rather than skip — both upstream repositories are on this machine at
  the paths the plan names.
- **P5.** curvecast is unaffected: its own gate sweep stays **25/25** with `EXEMPT_FIELDS`
  still `{}`, and `git status` in both upstream repositories shows nothing from this package.

### 3.3 Result

**9 bars, all passing. Two failed on the first run and a third was found broken by the
end-to-end demonstration; all three were defects in the bars, not findings about the
code.** `pytest -q` → **9 passed**. curvecast's own sweep is **25/25** with
`EXEMPT_FIELDS` still `{}`, and neither upstream repository has a change from this package.

#### Predictions, scored

| | outcome |
|---|---|
| **P1** every bar passes first run | **MISSED** — C1 and C5 failed; see below |
| **P2** all four mutation legs catch their variant | **hit**, after C6 was repaired — and the repair is the finding |
| **P3** C5's subprocess leg runs and finds zero broker modules | **hit** — `[]`, exit 0 |
| **P4** C7 and C9 run rather than skip | **hit** — **198** upstream files scanned (39 curvecast + 159 MEIP), none importing `deskcraft`; `EXEMPT_FIELDS` parsed and empty |
| **P5** curvecast unaffected | **hit** — 25/25, both upstream trees clean of anything from here |

#### The two first-run failures, and why neither is a finding

- **C1** built its census from `path.stem`, so `__init__.py` contributed the literal
  `__init__` and the equality compared `{"deskcraft", "__init__"}` against `{"deskcraft"}`.
  Repaired to derive the **importable module name** from the path relative to `src/`, which
  is the thing the census is actually about.
- **C5** interpolated `sorted(BROKER_MODULES)` into the probe source, producing
  `set(sys.modules) & [...]` — a `TypeError` inside the subprocess. The bar was asserting
  `returncode == 0` and so failed loudly rather than silently, which is the only reason it
  was not a green vacuous pass.

Both are ordinary defects. Neither changed a decision.

#### C6 was broken, and the end-to-end demonstration is what found it

The bar in §3.1 requires the test to **pass, and be shown to fail**. Running that
demonstration — one module dropped into `src/` importing `requests` and `subprocess`,
reading `os.getenv("KITE_API_KEY")` and carrying the string *"you should reduce the front
leg"* — turned **four** bars red. **C6 was not one of them.**

Its first version iterated `vars(deskcraft)`, so it saw only the top-level package's own
namespace: a module sitting in `src/` that nothing imports was invisible to it. And its
mutation leg had not caught that, because the leg exercised the **regex** against a literal
rather than the **scan** against a file — so it demonstrated that the pattern matches, which
was never in doubt, and not that the scanner reaches.

That is item 13's rule missed on its first application in this repo: *a source-scanning
guard is mutation-tested in the same test that uses it*, and a mutation that does not go
through the scanner is not a mutation of the guard. `rendered_strings` now reads
module-level assignments from the **AST** of every file under `src/`, which also covers
files nothing imports — the exact case that escaped. On the repeated demonstration **five**
of nine bars fire, C6 among them, and all nine are green again once the probe is removed.

**Recorded rather than repaired quietly** (curvecast's D70, inherited): the gap is described
in `rendered_strings`' own docstring, where the next person to touch the scanner will read
it, and the bar table above is unedited.

#### What was built

| | |
|---|---|
| `pyproject.toml` | Package metadata, empty runtime dependencies, and three import contracts written before any code could violate them |
| `src/deskcraft/__init__.py` | The package, deliberately empty, so the guard is live before there is anything to guard |
| `tests/conftest.py` | The `src/` path stopgap, carried with curvecast's caveat |
| `tests/test_deskcraft_boundary.py` | C1–C9: the inverted boundary, its four mutations, the one-way edge scan, the contract declaration check, and the watch on curvecast's `EXEMPT_FIELDS` |

#### What D2 inherits

- **The census is an equality.** Adding the book types turns C1 red until they are recorded
  with their work package. That is the intended friction, not a bug to route around.
- **`Direction` and `Notional` live in D2 and nowhere else** (§7). Nothing in the boundary
  test forbids them here — that is the whole inversion — so the discipline that keeps them
  in one module is the plan, and D2's own bars have to carry it.
- **C4 forbids all environment access**, not merely secrets. A later package that genuinely
  needs a variable edits the bar with a recorded reason; it does not add an exemption.
