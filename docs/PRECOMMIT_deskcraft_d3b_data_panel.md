# PRE-COMMIT — D3b, the data panel: the first numbers this repository has ever held

**Written 2026-09-14, before any change to this repository.** Until this package lands, deskcraft
contains **no data at all**: a walk of the working tree for `*.csv` and `*.parquet` returns
nothing, there is no `tests/fixtures/` directory, and every guard D1 through D5 built has been
guarding an empty room. D3b is what puts numbers in it.

**It fetches nothing.** `PLAN_deskcraft.md` §3 gives this repository no egress, D3a made that a
property of the working tree, and `tests/conftest.py` refuses the network for the whole test
process. The extraction lives in curvecast, which has the egress and already holds every input;
what arrives here is a file. That is the whole of `BUILD_ORDER_D3_D16.md` §4's D3b row — *every
panel arrives as a file; this repo never fetches* — and this package does not soften it.

**Ids.** Decisions `DD42`–`DD48`. Bars `B42`–`B48`, executable as `C42`–`C48`.

---

## 0. Measured before decided

All of §0 was read on 2026-09-14 on this machine, against deskcraft at `c57d656`, curvecast at
`0a5510e` and MEIP at `c1e383e`. Nothing in §0 was known when the package was scoped; three of the
seven readings changed what it does.

### 0.1 This repository holds nothing, and everything downstream is waiting on it

A walk of the working tree for data-shaped files returns **zero**. `tests/fixtures/` does not
exist. The suite is **44 passed** in 1.51s.

D4 (leg P&L), D8 (covariance), D9 (component ES), D11 (sizing) and D12 (scenario replay) each need
a panel to read and none of them can begin without one. That is why D3b sits where it sits.

### 0.2 The extraction is already done, and this package found it rather than repeating it

The scoping assumption was that D3b would have to pull sixteen series from FRED and the Board.
**It does not.** Every series `SOURCE_ROWS` marks committable is already extracted, DEV-sliced and
sitting in curvecast's `tests/fixtures/`:

| series | curvecast fixture | in curvecast's git |
|---|---|---|
| `SVENY01/02/03/05/07/10/20/30` | `gsw_zero_dev.csv` | tracked |
| `DGS3MO`, `DGS6MO`, `DGS1`, `DGS2`, `DGS10` | `cmt_daily_dev.csv` | tracked |
| `DEXUSEU` | `fx_vintages_dev.csv` | tracked |
| `DFII5`, `DFII10`, `DFII30` | `block_i_vintages_dev.csv` | **not tracked** |
| `GZ_SPREAD` | `block_j_ebp_snapshot.csv` | tracked |

So D3b is a **transfer, a re-grid and a licence closure**, not a fetch. It needs no FRED key, opens
no socket, and adds no licence exposure that curvecast has not already measured. The package is
substantially smaller than its row implies, and the honest reason is that WP-R1, Block I, Block J
and the FX blocks did the work first.

### 0.3 The DFII fixture is untracked, and the reason is the rule, not the series

`block_i_vintages_dev.csv` is on disk and absent from curvecast's git. It was removed by WP-L1
(`ca90bc1`) along with twenty-one others. **`DFII5`, `DFII10` and `DFII30` are not why.** All three
are Board H.15 rows, `PUBLIC_DOMAIN` on FRED's tag and on the Board's notice alike, and
`committable` True in this repository's own register since D3a.

The fixture also carries `T10YIE` (`CITATION_REQUIRED`) and `DCOILWTICO`, and curvecast's D436/D437
takes a fixture's licence as the **maximum over the publications it derives from** — a property of
the file, not of its best column. The file is therefore not committable and three public-domain
series are inside it.

**A DFII-only extract derives from H.15 alone and is public domain.** That is not a loophole; it is
the same monotone rule read forwards. The maximum over the one publication it derives from is
`PUBLIC_DOMAIN`, and the extract's provenance is checked per column by `C43` rather than asserted
here.

### 0.4 The credit substitute's licence was called unread, and curvecast had already read it

`src/deskcraft/sources.py` names the Gilchrist–Zakrajšek spread as the fallback behind both Moody's
rows and ends that sentence: *"Its licence is the Board disclaimer's default, **not read from the
file**."*

That was true when D3a wrote it and is false today, and it was already false then.
`curvecast.pit.data_rights.PUBLICATION_ROWS` carries a `board` row whose `read_from` is
*"federalreserve.gov/disclaimer.htm; the GSW and **excess-bond-premium** files"*, licence
`PUBLIC_DOMAIN`, `read_on` **2026-09-11 — deskcraft D3a section 0.8**. The excess-bond-premium file
is named explicitly, and the reading was taken by D3a's own session.

**So the substitute is public domain by a reading, not by a default**, and the sentence saying
otherwise is annotated rather than deleted (DD46).

### 0.5 Every daily series lands exactly on the GSW session grid

Measured, not assumed. The GSW DEV slice is **7,044 rows, 1988-01-01 → 2014-12-31**, strictly
increasing, no duplicate date, with **309 rows blank across all eight zero columns** — the federal
holiday calendar, kept deliberately by curvecast's D412 because a fixture that dropped them could
no longer tell a reader whether a gap was a holiday or a coverage defect.

Against that grid, **off-grid observations across all thirteen non-GSW daily series: zero.**

| series | observations | first → last | off grid |
|---|---|---|---|
| `DGS3MO`, `DGS6MO`, `DGS1`, `DGS2`, `DGS10` | 6,504 each | 1989-01-03 → 2014-12-30 | 0 |
| `DFII5`, `DFII10` | 3,002 each | 2003-01-02 → 2014-12-30 | 0 |
| `DFII30` | 1,217 | 2010-02-22 → 2014-12-30 | 0 |
| `DEXUSEU` | 4,019 | 1999-01-04 → 2014-12-24 | 0 |

A common grid was the convenient assumption and it happens to hold. It is recorded as a
**measurement with a bar on it** (`C42`), not as a property of yield data, because
`curvecast/src/curvecast/stage3/block_k.py` already records that two Treasury session grids *"are
not identical around holidays"*.

### 0.6 Five observations are knowable only from a vintage outside DEV

`cmt_daily_dev.csv` carries 6,505 rows per series and the newest is `2014-12-31` with
`vintage_date` **2015-01-05**. Filtering on the vintage rather than the observation date drops
exactly **five rows, one per CMT series, all dated 2014-12-31**.

They are five rows out of 32,525 and they are the whole reason the filter is on the vintage.
`DEV_END` is 2014-12-31; a panel that took `obs_date` at face value would carry five numbers first
published inside VAL, into the sample `FitWindow` exists to bound. That is `PLAN_deskcraft.md` §9's
circularity in miniature, and `make_block_j_fixture.py` already names the identical trap: *"A row
is carried if it was knowable by `DEV_END`. Filtering on `obs_date` instead would admit the
December-2014 sessions whose vintages land in January 2015 — sealed knowledge, committed in the
clear, read by every test run."*

`DFII5` and `DFII10` also carry **2,801 and 2,799 superseded vintages** respectively, so the
collapse rule bites on revisions and not only on the boundary. `DFII30`, `DEXUSEU` and the five CMT
series carry one vintage per observation.

### 0.7 The credit substitute is monthly, and the daily grid would manufacture what it lacks

`GZ_SPREAD` in `block_j_ebp_snapshot.csv` is **503 monthly observations, 1973-01-01 → 2014-11-01**,
every label a month-start, one vintage each. **323 of them fall inside DEV.**

It stops at 2014-11-01 rather than 2014-12-01 because the filter upstream is on `block_j`'s
publication clamp and not on the label — the same rule as §0.6, applied by the fixture this reads.

Placed on the 7,044-row daily grid it would be blank on roughly nineteen days in twenty, and any
loader that forward-filled it would be inventing daily credit observations that were never
published. Hence DD44.

### 0.8 There are two copies of the GSW source on this machine and only one is the sealed one

`C:/Users/rishi/meip/data/gsw/feds200628.csv` is sha256 `a0ecf2cf…`, 16,616,550 bytes. That is
exactly what `curvecast/docs/seal_manifest.json` pins as `gsw_svensson`, and it is what
`make_gsw_factor_fixture.py` resolves through `curvecast.meip_edge`.

`C:/Users/rishi/workshop/data/global_fi/raw/fed_gsw/feds200628.csv` is sha256 `f961e25b…` with
16,973 data rows against the pinned file's 16,988. It is an earlier download belonging to an
unrelated repository.

**Nothing in this package reads the second one**, and it is recorded here so that a future reader
who finds two files with one name does not resolve the ambiguity by picking the nearer.

---

## 1. Decisions

### DD42. The panel is the GSW session grid, and the blanks stay

The daily fixture carries **one row per GSW DEV session, all 7,044, in order**, with an empty field
wherever a series has no observation. Nothing is forward-filled, interpolated or dropped.

This is curvecast's D412 inherited rather than re-argued: a complete-case panel would be perfectly
good data that could no longer distinguish a federal holiday from a coverage defect, and it would
silently be 3,002 rows long because `DFII5` starts in 2003. **Complete-case filtering is the
loader's job, where it is visible and reversible**, exactly as `factor_space.load_zero_panel` does
it upstream.

The consequence is a fixture that is mostly empty in its early years and says so.

### DD43. A row is carried only if it was knowable by `DEV_END`

For every series the panel takes, per observation date, the value from the **latest vintage at or
before 2014-12-31**, and no observation whose earliest vintage falls after it.

Five CMT rows fall out (§0.6). They are named in the bar rather than counted, because "five rows
were dropped" and "the five 2014-12-31 closes, published 2015-01-05, were dropped" are different
claims and only the second one says the filter worked.

`gsw_zero_dev.csv` has no realtime axis to filter on — it is a single pinned file — so its rows are
carried on observation date, and that asymmetry is stated rather than smoothed. The visible effect
is that the panel's last row, 2014-12-31, carries GSW values and five empty CMT fields.

### DD44. Daily and monthly are two files

`GZ_SPREAD` gets its own fixture at its own frequency. Folding a 323-observation monthly series
into a 7,044-row daily grid would either fill it with blanks that a later loader will be tempted to
forward-fill, or fill it with forward-filled values that were never published.

The precedent is `make_block_j_fixture.py`'s own: *"Three outputs, because this block has three
kinds of evidence and folding them into one file would hide which is which."*

### DD45. The panel carries `DGS10` and `DFII10`, and does not carry `T10YIE`

D3a left this package a specific inheritance: *"`T10YIE` arrives as `DGS10 − DFII10`, and `DGS10`
needs a register row first."* The register row is added here (DD47) and both inputs are columns of
the panel. **The subtraction is not performed.**

A data panel that carried a derived column beside the two columns it was derived from would invite
every later reader to treat it as a third source, and the arithmetic belongs to D6's grammar, where
`REAL_VS_NOMINAL` is a named term with a direction. What D3b owes is that the construction is
*possible without the copyrighted series*, and two columns is what makes it possible.

### DD46. The credit leg is `GZ_SPREAD`, by the owner's decision, with the difference stated

The owner chose substitution on 2026-09-14 over dropping the leg, over a local-only Moody's fixture
and over seeking Moody's permission. What is substituted, and what it costs, is recorded on the
register row and here:

- **monthly, not daily** — 323 DEV observations against 6,504 for a CMT series;
- **a different bond universe** — a constructed portfolio of senior unsecured bonds matched to
  Treasury securities, not Moody's seasoned Aaa/Baa index;
- **a different construction** — a credit spread whose estimated default-risk component is removed
  in the companion `ebp` column, which this package does not carry.

It is a **substitute construct, not a mirror**, which is the phrase `sources.py` already uses for
Treasury's par curve behind GSW, and no later package may describe it as a Moody's spread.

The sentence in `sources.py` saying the substitute's licence was *"not read from the file"* is
**annotated with a dated clause, not rewritten** (curvecast's D70). Deleting it would erase the one
fact worth keeping: that a licence this repository believed unmeasured had been measured by its own
previous package three days earlier, and nothing noticed until a package needed it.

### DD47. Two register rows are added, and neither is a new permission

`DGS10` is added as an H.15 row, identical in shape to the four D5 graded and to `DFII10` beside it.
It is already inside curvecast's `fred_board` publication and already carried in `cmt_daily_dev.csv`;
what it lacked was a row in this repository saying so.

`GZ_SPREAD` is added as a Board row, `PUBLIC_DOMAIN` on a reading (§0.4), and with **no fallback**.
`Source.__post_init__` requires a reason when a fallback is absent, and the honest reason is that
the only free daily alternatives are the two series it is itself the substitute for, whose licence
forbids the fixture — and that ICE BofA's option-adjusted spreads, the obvious third answer, are
the withdrawal that caused `sources.py` to exist at all.

The register goes 21 rows → 23, committable 16 → 18.

### DD48. Licence closure is a property of the committed file, checked per column

`C43` reads the header of each fixture, resolves every column against `SOURCES`, and requires
`committable` on all of them — then scans the **bytes** of both files for the four series the
register refuses, so that a restricted series could not arrive inside a value, a comment or a
column this package forgot to name.

The generator's intentions are not evidence. D3a wrote the refusal (*"D3b inherits
`Source.committable` as a refusal"*) and this is the shape that makes it one.

`csv` and `pathlib` enter `ENGINE_IMPORT_ROOTS`, and `deskcraft.panel` enters `MODULES`. Neither
import is a capability the boundary bans: the six bans are egress, execution, credentials, broker
SDKs, the LLM edge and the imperative vocabulary, and reading a committed file is none of them.
Recorded here because C27 is an equality and will be red until it is.

---

## 2. What this package does not do

1. **It fetches nothing.** No network call, no FRED key, no environment read. The inputs are files
   already on this machine, and `conftest.py` refuses the network for the whole test process.
2. **It does not modify curvecast's fixtures or MEIP.** It reads five files in curvecast and none
   in MEIP. `meip:untouched` is expected to stay green for the reason that it is never opened.
3. **It computes nothing.** No return, no difference, no covariance, no derived column. The panel
   is source values carried through as the source's own text, never reparsed and reformatted —
   `make_gsw_factor_fixture.py`'s rule, for its reason: a float round-trip is a silent
   transformation of committed evidence.
4. **It adds no leg and moves no leg.** `US_CASH_BOOK` is still the four of D5 §0.6. A panel that
   can price a credit leg is not a credit leg, and D7 is the package that builds one.
5. **It scores no hypothesis.** `CLAIMS` gains no verdict. D6 still writes the first one.
6. **It does not carry `ebp`, `est_prob`, `DGS5`, `DGS30`, `SVENY04`, or any other series the
   sources at hand would have made free.** A panel sized to what the plan's legs need is a panel a
   later reader can audit; a panel sized to what was lying around is not.
7. **It does not lift the §10 NO-BUILD floor.** Four priceable legs before, four after.
8. **It does not amend closed documents.** D3a's §0.9 says the GZ licence was not read from the
   file. That is what was believed on 2026-09-11; §0.4 records what is true now, and the register
   row carries the dated annotation.

---

## 3. Verification

### 3.1 Bars

| bar | what would falsify it | executable |
|---|---|---|
| **B42** | The panel not being on the grid it claims. The daily fixture's `Date` column is **exactly** curvecast's GSW DEV grid, parsed from `gsw_zero_dev.csv` at test time — same 7,044 dates, same order, no duplicate — and its columns are exactly the seventeen named series plus `Date`. **Skips loudly** if curvecast is absent. | C42 |
| **B43** | A restricted series reaching a committed file (DD48). Every column of both fixtures resolves to a `Source` with `committable` True; and the bytes of both files contain none of `VIXCLS`, `BAA10Y`, `AAA10Y`, `T10YIE`. | C43 |
| **B44** | A value knowable only after DEV ended (DD43). Recomputed from curvecast's vintage fixtures at test time: for every committed observation the vintage used is at or before `DEV_END`, and the five 2014-12-31 CMT closes published 2015-01-05 are **absent by name**. **Skips loudly** if curvecast is absent. | C44 |
| **B45** | A generator that silently dropped, duplicated or padded rows. Per-series non-empty counts are exactly §0.5's: 6,504 for each of the five CMT series, 3,002 for `DFII5` and `DFII10`, 1,217 for `DFII30`, 4,019 for `DEXUSEU`, 8 GSW columns over 7,044 rows with 309 blank across all of them, and 323 monthly `GZ_SPREAD` rows. | C45 |
| **B46** | The loader admitting a window it should refuse, or hiding the completeness rule. `load_daily` takes a `FitWindow` and returns only dates inside it; a bare `date` pair is refused by `FitWindow` itself; `complete_cases` is a separate, named step whose dropped-row count is returned rather than discarded. | C46 |
| **B47** | **Mutation.** A fixture carrying a non-committable series must make C43 fail. A copy of the real daily fixture with one column renamed to `BAA10Y` is run through the same checker the real bar uses, and must be rejected. | C47 |
| **B48** | The monthly panel being merged into the daily one by accident (DD44). The two fixtures are separate files; every `GZ_SPREAD` label is a month-start; no date in the monthly fixture is offered as a session of the daily grid; and the loader exposes no join. | C48 |

### 3.2 Predictions

Fixed before any file in this repository is touched, scored as written.

- **P1. The suite goes 44 → 51**, 0 failed, 0 skipped. Seven new bars, and curvecast is present on
  this machine so the two that would skip do not.
- **P2. The daily fixture is 7,044 rows and 18 columns** — `Date` plus seventeen series — with
  **309 rows blank across all eight SVENY columns**, and its last row, 2014-12-31, carries GSW
  values and five empty CMT fields.
- **P3. Per-series coverage is exactly §0.5's table**, all thirteen non-GSW daily series on grid
  with zero off-grid observations, and the monthly fixture is 323 rows.
- **P4. Licence closure holds**: all eighteen series committable, and none of the four refused
  names appears anywhere in the bytes of either file.
- **P5. Exactly five observations are dropped for vintage, one per CMT series, all 2014-12-31**,
  and `DFII5`/`DFII10` contribute 2,801 and 2,799 superseded vintages that the collapse resolves
  without dropping an observation.
- **P6. `lint-imports` reports 2 kept, 0 broken**, and MEIP's reports **6 kept, 0 broken** with
  MEIP's tree unmodified.
- **P7. curvecast's `run_gates.py` is 44 of 44, exit 0**, with `meip:untouched` green. This package
  adds a script and a document there and changes no module, so this is the property re-checked.
- **P8. At least one new bar fails on its first complete run.** D5 predicted no miss and had none,
  and recorded that as evidence its work was mechanical rather than as a record. This package is
  not mechanical: it re-grids four fixtures written under three different conventions, applies a
  vintage rule that bites on 5,600 superseded rows, and asserts a licence property over bytes.
  **The prediction is a miss, and P8 is the prediction most likely to be wrong in the direction
  that flatters this package.**

### 3.3 Result

Run 2026-09-14, production interpreter Python 3.12. Scored against §3.2 exactly as written;
nothing in §0 through §3.2 was edited after the first file was touched.

| | prediction | verdict | what was measured |
|---|---|---|---|
| **P1** | suite 44 → 51, 0 failed, 0 skipped | **hit** | `51 passed in 1.55s`. Seven bars, none skipped: curvecast is present, so C42 and C44 ran rather than skipping. |
| **P2** | 7,044 rows, 18 columns, 309 all-GSW-blank rows, last row GSW-valued with five empty CMT fields | **hit** | 7,044 rows, 18 columns, 8 GSW columns at 6,735 observations each (7,044 − 309), 309 rows blank across all eight. Last row `2014-12-31`: GSW values present, `DGS3MO`/`DGS6MO`/`DGS1`/`DGS2`/`DGS10` all empty. |
| **P3** | per-series coverage exactly §0.5's table; monthly 323 rows | **hit** | 6,504 for each of five CMT series; 3,002 / 3,002 / 1,217 for `DFII5`/`DFII10`/`DFII30`; 4,019 for `DEXUSEU`. Monthly 323 rows, `1988-01-01` → `2014-11-01`, every label a month-start. |
| **P4** | eighteen series committable, four refused names absent from the bytes | **hit** | C43 resolves every column of both fixtures to a committable `Source`; a byte scan of both files finds none of `VIXCLS`, `BAA10Y`, `AAA10Y`, `T10YIE`. |
| **P5** | five vintage drops, one per CMT series, all 2014-12-31; `DFII5`/`DFII10` contribute 2,801 and 2,799 superseded vintages resolved without losing an observation | **hit** | Re-derived from curvecast's fixtures independently of the generator: `DFII5` 5,803 in-DEV rows → 3,002 observations (2,801 superseded), `DFII10` 5,801 → 3,002 (2,799), and **zero** observations of either lost to the vintage rule. Each of the five CMT series has exactly one observation with no vintage at or before `DEV_END`, and it is `2014-12-31` in all five. |
| **P6** | deskcraft `lint-imports` 2 kept / 0 broken; MEIP 6 kept / 0 broken, tree unmodified | **hit** | As predicted, and the sweep's own `meip:untouched` gate independently reports `unmodified`. |
| **P7** | curvecast 44 of 44, exit 0, `meip:untouched` green | **hit** | `44 passed, 0 failed, 0 skipped, 1332s`, exit 0. `curvecast:pytest` 1,047 passed / 21 skipped, `curvecast:receiver-copy` 769 / 299, `curvecast:meip-venv-sweep` 194 / 0, `meip:pytest` 1,410 passed. |
| **P8** | **at least one new bar fails on its first complete run** | **MISS** | All seven of C42–C48 passed the first time they were run to completion. |

#### P8 missed, and it missed in the direction that flatters this package

That was the stated risk when it was written, so it gets the fuller account rather than a line.

The package was **not** defect-free. One real defect was found — the generator's `--check` raised
`TypeError: Path.read_text() got an unexpected keyword argument 'newline'` on its first execution.
But it was found by the **generator's own self-check**, upstream of every bar, and it was a defect
in the verifier rather than in the panel. By the time C42–C48 ran, the thing they examine had
already been checked by a different instrument. So the honest reading of P8 is not "the bars are
strong" but "the bars were handed an artefact that something else had already verified" — and the
prediction was wrong about *which* instrument would catch the first problem, not about whether
there would be one.

Three further reasons the first run was easier than §3.2 argued, all of which were knowable and
none of which were stated there:

1. **The four source fixtures are not unverified inputs.** `curvecast:fixture[block_i]`,
   `[block_j]`, `[fx_vintage]` and the GSW grid all have their own passing gates in the sweep
   above. The re-grid consumed files that were already under bars.
2. **The vintage rule was not implemented here.** `DEV_END` and the collapse-to-latest-vintage
   discipline came from curvecast, where they are already exercised. D3b applied a rule; it did
   not invent one.
3. **The only genuinely new logic — the loader — is small and has no arithmetic in it.** `panel.py`
   parses, filters on a window, and counts. DD45's refusal to carry a derived column is the
   reason there was nothing here for a bar to catch.

#### What the run measured that nothing predicted

1. **`Path.read_text(newline=)` is 3.13+, and the production interpreter is 3.12.** The generator's
   `--check` crashed on first execution. Fixed with an explicit `path.open(encoding="utf-8",
   newline="")`. This matters beyond the version: reading with newline translation **on** would
   make a CRLF/LF drift compare equal, which would defeat the only rule the LF convention exists
   to enforce. The fix is annotated in the script with that reason.
2. **`ruff` is red on deskcraft's HEAD, and was before this package.** `tests/test_book_types.py:30`
   imports `deskcraft.book.Leg` unused — F401, one finding, in a file last written by D5
   (`c57d656`) and untouched by D3b (`git status` reports it unmodified). Not fixed here: `ruff`
   is not among D5's declared gates, and M18's precedent is that a repair ships as its own commit
   rather than riding inside a package that did not cause it.
3. **This repository had no `.gitattributes`, and `core.autocrlf` is `true`.** Found by git's
   own warning at `git add` time, on the first fixtures this repository has ever held: the blob
   is stored with LF, and the next checkout would have written CRLF back. The generator's
   `--check` compares the committed bytes against a freshly rendered copy **with newline
   translation off**, so on any fresh clone it would have reported both panels stale, and the
   person who cloned would have been right to distrust it. `tests/fixtures/** text eol=lf` is
   added in this commit, matching the two lines curvecast has carried for the same reason. The
   defect was one `git add` away from shipping, and nothing in §3 would have caught it: every
   bar reads through `csv`, which accepts either ending.
4. **curvecast classifies its ruff findings; deskcraft has no ruff gate at all.** The sweep reports
   `curvecast:ruff PASS — 29 findings, all pre-existing`, i.e. a gate that permits a known
   backlog and fails on a new entry. deskcraft has no equivalent, which is why item 2 above had
   to be found by hand. Recording it as a candidate for a later package, not acting on it here.

#### What this result is weak evidence for

**C45 and the generator's `verify()` are the same numbers written twice.** The coverage counts in
`EXPECTED_COVERAGE` and the counts C45 asserts were measured once, in §0.5, and then written into
both places. C45 would therefore not catch a generator that was wrong in a way its own check was
also wrong about. It is a regression bar — it catches the fixture changing under a reader — and it
should not be read as independent confirmation that the extraction was right.

**C42 and C44 are the bars that carry weight**, because both re-derive from curvecast's fixtures at
test time rather than comparing against a constant: C42 re-parses the GSW grid and asserts
date-for-date equality, and C44 recomputes the whole vintage collapse and compares values, then
asserts the five refusals by name. The numbers in §3.3's P5 row above were likewise re-derived
from the source fixtures for this write-up, not read back from the generator.
