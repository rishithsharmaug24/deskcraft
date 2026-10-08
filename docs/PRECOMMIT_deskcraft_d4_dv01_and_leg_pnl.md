# PRE-COMMIT — D4: DV01 and leg P&L, and the wrap that is declined for three of four legs

**Written 2026-09-15, before any change to this repository.** Every number in §0 was measured
on this machine today, against deskcraft at `2e569ee`, curvecast at `7727ee2` and MEIP
untouched. Nothing below §0 has been run.

**Ids.** Decisions `DD49`–`DD58`. Bars `B49`–`B58b`, executable as `C49`–`C58b`.

**The row this package closes.** `BUILD_ORDER_D3_D16.md` §4: *"D4 | DV01 and leg P&L | Wraps
`meip.rates.cascade.par_bond_duration_convexity`. Maps a per-tenor bp shift to per-leg P&L."*
Two of those three clauses do not survive contact with the book D2 actually built, and §0 is
where that is measured rather than argued.

**A second thing rides along, by the owner's direction: the lint gate.** It is not D4 and does
not pretend to be; it is a floor curvecast has had since its own scaffold and this repository
has never had, and `pyproject.toml` has declared `ruff>=0.6` as a dev dependency since D1 with
nothing running it. `DD57`–`DD58` and `C58`/`C58b` are that work, kept in their own section so
the D4 verdict and the gate can be read apart.

---

## 0. Measured before decided

### 0.1 `meip` is not importable from this repository's interpreter, so the wrap cannot be an import

```
PRODUCTION_PYTHON -c "import meip"   ->  ModuleNotFoundError: No module named 'meip'
PRODUCTION_PYTHON -c "import curvecast" -> ModuleNotFoundError: No module named 'curvecast'
PRODUCTION_PYTHON -c "import numpy"  ->  2.4.6
```

`PRODUCTION_PYTHON` is `C:/Users/rishi/AppData/Local/Programs/Python/Python312/python.exe`,
3.12.10, which is the interpreter the suite runs on. MEIP is a `uv` project with its own
`.venv`, and the function D4 was told to wrap lives behind it.

This is not a surprise and it is not a defect: it is the same condition `window.py` met at D3a
and `reference.py` met at D2. Both answered it the same way — **restate, and check the
restatement against the upstream source at test time, skipping loudly when the sibling is not
on the machine** (C9, C14, C31). D4 inherits that answer and strengthens it, see §0.2.

### 0.2 MEIP's function can be *executed* from its own source, with no import chain

`meip/rates/cascade.py` imports numpy, pydantic, four `meip.rates` modules and two stores at
module level, so importing it is not available here and would drag a `MacroStore` into a test
process that is forbidden to read `data/meip.duckdb`. But `par_bond_duration_convexity` is
self-contained — its body reaches only `ValueError`, `range`, `sum` and arithmetic — so its
function node can be parsed out and compiled alone. Measured today, on `PRODUCTION_PYTHON`:

| call | MEIP's own bytes, executed from source |
|---|---|
| `(4.0, 2)` | `(1.886094674556213, 5.405097860719161)` |
| `(4.0, 5)` | `(4.4518223310162055, 25.012485118273787)` |
| `(4.0, 10)` | `(8.11089577935503, 80.75432318611735)` |
| `(2.0, 10)` | `(8.982585006242235, 93.99546153093414)` |

Cross-checked against the same calls run inside MEIP's own `.venv` through an ordinary import:
**identical, digit for digit**. So the wrap can be a *measurement* here rather than an
assertion — which is strictly more than C31 gets for two date constants.

### 0.3 `SVENY` is continuously compounded, and the licensor says so in the file

Lines 3–7 of `meip/data/gsw/feds200628.csv`, the file curvecast pins by SHA256 in its seal
manifest as `gsw_svensson`:

```
Series,Compounding Convention,Mnemonic(s)
Zero-coupon yield,Continuously Compounded,SVENYXX
Par yield,Coupon-Equivalent,SVENPYXX
Instantaneous forward rate,Continuously Compounded,SVENFXX
One-year forward rate,Coupon-Equivalent,SVEN1FXX
```

curvecast's own audit pre-commit had already written the same thing from the other side —
*"par-yield-equivalent; use `SVENPY`, **never** `SVENY`, which is zero-coupon"* — and
`reference.py` picks `SVENY02`, `SVENY05` and `SVENY10`. So three of the four legs in
`US_CASH_BOOK` are expressed on a **continuously compounded zero-coupon** yield.

The modified duration of a zero under continuous compounding is not an approximation and is
not a proxy. `P = exp(-yT)`, so `-(dP/dy)/P = T` **exactly**, and the convexity is `T²`
exactly. There is nothing to estimate.

### 0.4 The par proxy understates the zero legs' DV01, by up to 11.7%

Modified duration at the reference tenors, at the last DEV session on which every series
`US_CASH_BOOK` needs is published — **2014-12-24**, the 2,998th and last complete case over
`SVENY02, SVENY05, SVENY10, DFII5, DEXUSEU`:

| series | yield % | continuous zero | MEIP par proxy | understatement |
|---|---|---|---|---|
| `SVENY02` | 0.76910001039505 | 2.000000 | 1.977161 | **1.142%** |
| `SVENY05` | 1.79840004444122 | 5.000000 | 4.741165 | **5.177%** |
| `SVENY10` | 2.33540010452271 | 10.000000 | 8.826975 | **11.730%** |

MEIP's docstring is candid about what its function is for: *"A duration bucket is not a bond,
and this is a proxy for one. MEIP holds no index constituents, so the alternative was a
hand-set typical index duration."* deskcraft is not in that position. `reference.py` states
each rate leg as an exact zero at an exact tenor on a curve whose compounding convention is
published in the file's own header. **Using a proxy where the exact form is available, and
losing 11.7% of the ten-year leg's DV01 doing it, is the failure MEIP's own docstring names.**

The build-order row was written before D2 fixed these legs as GSW zeros. It is not wrong about
the tool; it is wrong about which legs the tool applies to.

### 0.5 `DFII5` is par-quoted, so the wrap is kept for it — and it is the leg that matters

`DFII5` is H.15's five-year constant maturity, inflation-indexed, *quoted on an investment
basis*. D3a's register already carries the reading: `_h15`'s evidence says H.15 *"refers its
yields to Treasury's yield curve methodology"*, and the DFII rows' fallback is
`_TREASURY_REAL` — **"Treasury Daily Par Real Yield Curve Rates"**. Par, in the register's own
words, written three days before a package needed them. The par-bond cash-flow form is the
right instrument for it, and MEIP's function is that form.

Measured: `par_bond_duration_convexity(0.5, 5)` = `(4.925866328098868, 29.31037530023239)`.

### 0.6 `US_BREAKEVEN_5Y` declares `Neutrality.DV01` and is not DV01-neutral

The leg is `+1 SVENY05, -1 DFII5` on $50m, `LONG`, and it declares `Neutrality.DV01`.
`book.py` admits that declaration because the coefficients sum to zero. On 2014-12-24:

| component | convention | modified duration | DV01 on $50m |
|---|---|---|---|
| `SVENY05` | continuous zero | 5.000000 | $25,000.00 / bp |
| `DFII5` | coupon-equivalent par | 4.925866 | $24,629.33 / bp |
| | | | **residual $370.67 / bp** |

A **parallel one-basis-point rise in both curves leaves the breakeven unchanged and moves this
leg by $370.67** — 1.483% of the nominal component. Coefficient-neutral is not DV01-neutral
when the two components are quoted on different conventions, and `book.py`'s own refusal
message has said the adjacent thing since D2: *"DV01-neutral and cash-neutral are different
positions."* D4 is the first package in this repository that can compute the difference, and
`reference.py`'s stated ground — *"Same-tenor, so the hedge basis is duration"* — assumes
same-tenor implies same-duration, which the header block in §0.3 says it does not.

**The finding is not an artefact of MEIP's annual-pay form.** §0.7 recomputes it semi-annually
and the residual is $340.34/bp, same sign, same order.

### 0.7 MEIP's par form is annual-pay; US Treasuries pay semi-annually

`par_bond_duration_convexity` builds `range(1, maturity_years + 1)` — one flow a year,
discounted annually. A Treasury pays twice a year on a semi-annual bond-equivalent yield.
Recomputed on the same session, semi-annual against MEIP's annual:

| series | annual-pay | semi-annual | difference |
|---|---|---|---|
| `SVENY02` @ 0.7691% | 1.977161 | 1.980919 | +0.1901% |
| `SVENY05` @ 1.7984% | 4.741165 | 4.761361 | +0.4260% |
| `SVENY10` @ 2.3354% | 8.826975 | 8.872234 | +0.5127% |
| `DFII5` @ 0.5000% | 4.925866 | 4.931932 | +0.1231% |

Half a basis point of duration at ten years, an eighth at the one leg that actually uses the
par branch. It is recorded and it is **not corrected** — see DD52.

### 0.8 `numpy` was predicted for D4 twice, and D4 does not need it

`pyproject.toml` line 8: *"numpy arrives with D4, when there is arithmetic to do."*
`panel.py`'s `Panel` docstring: *"Deliberately not a matrix: `numpy` arrives with D4."*

The arithmetic D4 actually has is four legs, five series and six scalar formulas. `math.fsum`
is already imported by `book.py`. numpy is installed on `PRODUCTION_PYTHON` (2.4.6) and adding
it would cost nothing at install time — and would be a dependency added because a comment
predicted it.

It is also **not free**: `ENGINE_IMPORT_ROOTS` is an *equality* (C27), so naming `numpy` there
without an engine file importing it turns the census red. The guard already enforces the
conclusion.

### 0.9 ruff: one finding in the whole tree, and nothing runs it

`ruff 0.15.22`, resolved at `C:/Users/rishi/meip/.venv/Scripts/ruff.exe` — the same binary
curvecast's `scripts/run_gates.py:839` resolves for `curvecast:ruff`. It is not installed on
`PRODUCTION_PYTHON`.

```
ruff check .          ->  Found 1 error.
tests/test_book_types.py:30  F401 unused import: `deskcraft.book.Leg`
```

Left by D5's `c57d656`. One line, in an import block of five names.

A wider selection was measured and is **not** proposed: `--select E,W,F,I,UP,B,SIM
--line-length 100` gives 25 findings — `E501` 10, `SIM300` 8, `I001` 4, `B018` 2, `F401` 1 —
most of them in test code where a yoda condition or a bare expression is deliberate. Widening
the rule set is a decision about this repository's style with 24 edits attached; it is not a
thing to do inside a package about duration.

### 0.10 The tree is green before this package

`PRODUCTION_PYTHON -m pytest -q` on `2e569ee`: **51 passed**, 0 failed, 0 skipped, 2.89s.

---

## 1. Decisions

### DD49. The convention is a property of the series, read from the licensor, and refused by default

`COMPOUNDING_OF` maps a series name to `Compounding.CONTINUOUS` or
`Compounding.COUPON_EQUIVALENT`. A series with no row **raises**; it does not fall back to
either branch.

A default here is a silent answer to the question §0.4 measures at 11.7%, and DD18 already set
this repository's rule for that shape: `fx_hedged` has no default *"because a default is a
silent answer"*. `DEXUSEU` and `GZ_SPREAD` are deliberately absent — an exchange rate has no
duration, and a credit spread's DV01 is a property of the bond portfolio it is a spread over,
not of the spread. Asking for either refuses by name.

**The table lives in `sensitivity.py`, not in `sources.py`.** D3a's register answers *where a
series comes from and what may be done with it*; adding a sixth field to `Source` would edit
D3a's shape from inside D4. C49 checks each entry against the licensor's own text instead.

### DD50. The wrap is kept for the par-quoted branch and declined for the zero-quoted branch

`modified_duration(series, ytm_pct, tenor_years)` dispatches on `COMPOUNDING_OF`:

- `CONTINUOUS` → `tenor_years`, and convexity `tenor_years ** 2`. Exact, not fitted.
- `COUPON_EQUIVALENT` → MEIP's `par_bond_duration_convexity`, **restated line for line** and
  checked against MEIP's own executed bytes by C50.

This is what "wraps `meip.rates.cascade.par_bond_duration_convexity`" can honestly mean for a
book whose rate legs are three-quarters zero-coupon. The build-order row is annotated, not
rewritten (D70).

### DD51. The restatement is checked by executing MEIP's source, not by comparing text

C50 parses `par_bond_duration_convexity` out of `cascade.py`, compiles that single function
node, runs it, and compares against deskcraft's restatement on a grid of yields and maturities
at exact equality. Skips loudly when MEIP is not on the machine, in C31's shape.

Exact equality rather than a tolerance, because the restatement is line-for-line and the
identical-IEEE-double result was measured in §0.2. A tolerance would hide a reordered `sum`.

### DD52. The annual-pay approximation is recorded and not corrected

A wrap that silently improves on what it wraps is not a wrap; it is a second implementation
with the same name, and the next reader comparing deskcraft's number with MEIP's would find a
difference no document explains. §0.7 measures the cost at +0.12% on the one leg that uses this
branch. It is stated on the function, in the pre-commit, and on the returned record.

### DD53. `RATE_SENSE_OF` is a closed four-valued table over `InstrumentKind`, and `UNPRICEABLE` is not zero

A `ZERO_YIELD` leg held `LONG` is long a **bond** and loses when its yield rises. A `BREAKEVEN`
leg held `LONG` is long a **spread** and gains when that spread widens. Those are opposite signs
on the underlying series, and nothing in D2's types says which applies.

```
PRICE        long is long the price; a rate rise is a loss   ZERO_YIELD, REAL_YIELD, FUTURE
RATE         long is long the quoted rate; a rise is a gain  BREAKEVEN, CREDIT_SPREAD,
                                                             SWAP_SPREAD, CROSS_MARKET_SPREAD,
                                                             CROSS_CURRENCY_BASIS
NONE         no first-order rate sensitivity, structurally   FX_SPOT, EQUITY_VOL
UNPRICEABLE  has rate sensitivity this repo cannot compute   OPTION, RATE_VOL
```

Total and single-valued over all twelve kinds, in `ASSET_CLASS_OF`'s shape, checked by C52.

**`UNPRICEABLE` raises and never returns 0.0.** The option leg has enormous rate sensitivity;
what it lacks is a free implied-volatility surface, which is `reference.py`'s stated reason for
carrying it unpriced. A zero would be a number, and a number is what every downstream sum will
add. `NONE` and `UNPRICEABLE` are the two facts a single zero would merge.

### DD54. The shift is stated per **series**, not per tenor

The build-order row says *"a per-tenor bp shift"*. `US_BREAKEVEN_5Y` holds two different curves
at the same tenor, so a five-year shift cannot say whether the nominal or the real curve moved
— and the difference between those two is the entire content of §0.6.

`CurveShift` is therefore a frozen mapping from **series name** to basis points.
`CurveShift.parallel(series, bp)` builds a parallel move over a named tuple of series, so a
per-tenor or per-curve shift is a convenience over the primitive rather than the primitive.

### DD55. A shift naming a series the book does not hold is refused

`book_pnl` raises when the shift carries a series no leg reaches. A mistyped series name that
silently contributes zero is a stress test that reports "no effect" for a reason that has
nothing to do with the book — the failure mode D3b's `refuse_uncommittable` exists for, one
layer up.

The reverse is **not** an error: a leg whose series the shift does not name is unshifted, which
is what a partial shift means.

### DD56. D4 is first-order, and what it drops is measured rather than omitted

Leg P&L is `Σ_series dv01_series × Δy_series_in_bp`. Convexity is computed and **returned on the
record**, and is not folded into the P&L.

A second-order term on a `RATE`-sense spread needs the spread decomposed into two separately
priced bond legs with their own notionals — which is D7b's job, not D4's. Rather than compute
it for one sense and not the other, D4 computes it for neither and reports the size of what is
dropped: on `us_10y`, a 100 bp parallel move, the first-order term is 10.0% of notional and the
½·C·Δy² term is 0.5%, **5% of the move**. C57 asserts that ratio so it cannot become invisible.

### DD57. The lint gate holds at **zero**, not at a baseline

curvecast's `classify_ruff` carries `RUFF_BASELINE` at 29 findings and fails only on growth,
because 29 predated the gate. This repository has **one**, and it is deleted in this commit, so
the gate can be the stronger form: any finding at all is red.

`[tool.ruff.lint] select = ["E4", "E7", "E9", "F"]` is pinned in `pyproject.toml` — exactly ruff
0.15.22's default selection, written down so the gate cannot move when ruff's defaults do.
curvecast does not pin its selection; that is a fact about curvecast recorded here, not a change
made there, because editing a sibling repository is not in this package's scope.

### DD58. The gate is a test, because a `scripts/` directory here could not run one

deskcraft has no gate runner and structurally cannot have curvecast's. D3a widened the boundary
scan so that a `scripts/` directory arrives under the **strict** policy — every ban, including
execution — so a `scripts/run_gates.py` here could not invoke pytest or ruff without turning
C3 red. `tests/` is the one root with `HARNESS` policy, where execution is lifted, and C5 has
spawned a child interpreter from there since D1.

So the gate is `tests/test_lint.py`. It skips loudly when ruff is absent, in C31's shape, and
`C58b` is the mutation that shows the invocation can see a finding at all — which is exactly the
defect curvecast's classifier docstring records fixing on 2026-09-11, where a ruff that never ran
reported "0 findings" and went green.

---

## 2. Bars

Each `Bn` is the claim; `Cn` is the test that executes it. All in `tests/test_sensitivity.py`
except C58/C58b, which are `tests/test_lint.py`.

| id | claim |
|---|---|
| **B49** | `COMPOUNDING_OF` agrees with the licensor's own words for both branches: the `SVENY` rows are checked against the `Compounding Convention` block parsed out of `feds200628.csv`, and the H.15 rows against `SOURCES[...]`'s recorded *Par … Yield Curve Rates* fallback. A series with no row raises. Skips loudly if the GSW file is not on this machine. |
| **B50** | deskcraft's par-bond restatement reproduces MEIP's `par_bond_duration_convexity` **exactly** — both returned values, at exact equality — over a grid of yields and maturities, with MEIP's function parsed from `cascade.py` and executed from its own bytes. Its two refusals (`maturity_years <= 0`, `y <= -1.0`) are reproduced too. Skips loudly if MEIP is absent. |
| **B51** | The zero branch is the exact form and not the proxy: `modified_duration("SVENY10", y, 10)` is `10.0` for every yield, the par proxy at the same arguments is not, and the gap at 2014-12-24's yields is the three percentages in §0.4 to 3 decimal places. |
| **B52** | `RATE_SENSE_OF` is total and single-valued over `InstrumentKind`, its image is the whole of `RateSense`, and both mutations — a kind deleted, a kind added — are caught. |
| **B53** | The four `US_CASH_BOOK` legs reproduce `SCENARIO_SIGNS` where the matrix makes a rate claim: `us_2y` and `us_10y` gain on a rate rise (both `SHORT`, `PRICE` sense), `us_breakeven_5y` gains when the nominal rises against an unchanged real. Signs only, which is all `SCENARIO_SIGNS` asserts. |
| **B54** | `eurusd` has zero rate P&L under every shift, and the zero is `RateSense.NONE` **by declaration**: mutating its kind to `OPTION` raises `Unpriceable` rather than returning 0.0, so the two facts are distinguishable. |
| **B55** | `leg_pnl(us_breakeven_5y, parallel 1 bp on SVENY05 and DFII5)` is **not** zero, equals **$370.67/bp** to the cent, and the leg declares `Neutrality.DV01`. The instrument is unchanged; the bar records the contradiction. |
| **B56** | `CurveShift` is keyed by series: a shift naming a series no leg holds raises from `book_pnl`; a shift naming only some of a leg's series is honoured as a partial move; a non-finite or non-numeric bp value raises. |
| **B57** | `book_pnl` sums to the per-leg total exactly (`math.fsum`), and the dropped second-order term on `us_10y` at 100 bp is 5.000% of the first-order term — the number DD56 states, asserted so it cannot silently grow. |
| **B58** | `ruff check .` over the repository root reports **zero** findings, with the pinned selection. Skips loudly when no ruff binary resolves. |
| **B58b** | The same invocation, pointed at a planted file with a known `F401`, reports exactly that finding — so a ruff that checked nothing cannot pass B58. |

---

## 3. Predictions, fixed before the run

| id | prediction |
|---|---|
| **P1** | All of C49–C58b pass on their first complete run. *(D3b's P8 predicted the opposite and was wrong in the flattering direction; this one is stated the other way and can be wrong in the direction that costs.)* |
| **P2** | The suite goes 51 → 62: eleven bars added, none removed. |
| **P3** | No existing bar turns red. The three edits that touch existing files are the `MODULES` census gaining one name, two annotated comments, and one deleted import — none of which any bar reads except C1/C25's census, which C27 does not cover because `sensitivity.py` adds **no new import root**. |
| **P4** | `ENGINE_IMPORT_ROOTS` is unchanged. `sensitivity.py` imports `__future__`, `collections.abc`, `dataclasses`, `enum`, `math` and `deskcraft.book` — all six roots are already in the census. |
| **P5** | `lint-imports` stays 2 kept, 0 broken. D4 adds no external import to the engine at all, so neither contract can move. |
| **P6** | The breakeven residual comes out at **$370.67/bp**, and stays within $1/bp of that under the semi-annual variant ($340.34 — *not* within $1; the prediction is that the **sign and order** hold, and the semi-annual figure is stated here so the bar cannot be tuned to it). |
| **P7** | ruff goes 1 → 0 with the single deleted import and no other edit. Pinning the selection changes nothing today, because the pinned set is today's default. |
| **P8** | The three understatement percentages in §0.4 reproduce exactly from the committed fixture — 1.142%, 5.177%, 11.730% — because the yields are read from the panel rather than restated here. |

---

## 4. What this package does not do

- **It does not re-express any leg.** The breakeven's declared `Neutrality.DV01` is measured to
  be false by 1.483% and `reference.py` is **annotated, not edited** (D70). Whether the leg
  should be DV01-matched rather than coefficient-matched is a decision for **D7b**, the leg
  generator, which has a reason to make it — the same disposition D5's DD40 reached when
  `DGS2`'s floor landed and leg 1 did not move.
- **It does not price `us_10y_call` or `us_de_10y`.** Both are in `DEFERRED_LEGS` and both stay
  there; `RateSense.UNPRICEABLE` is how the option leg refuses rather than contributing a zero.
- **It does not add numpy** (§0.8), and it does not widen the ruff selection (§0.9).
- **It does not touch MEIP.** `cascade.py` is read and its function is executed from its own
  bytes; nothing is written. The standing `meip:untouched` gate is what checks that.
- **It scores no registered claim.** No row in `CLAIMS` names `D4` as scorer, so C34 is
  unaffected — a verdict recorded here would be the fabricated result C34 exists to refuse.

## 5. What would make this wrong

- **A duration whose compounding convention is assumed rather than read.** That is the
  fabricated-parameter failure MEIP's own docstring names, and DD49's refusal-by-default is
  what stops it arriving as a plausible default.
- **A `RateSense` chosen to make `SCENARIO_SIGNS` reproduce.** The table is fixed in DD53 from
  what each instrument *is*; B53 then checks it against a matrix written at D2 and never
  consulted while DD53 was decided. If a sign disagrees, the table is reported wrong and not
  quietly flipped.
- **`UNPRICEABLE` collapsed into 0.0** by any later package summing over legs. A zero is a
  number and every sum will take it.
- **The residual in §0.6 tuned away** by re-expressing the leg inside this package, which would
  make D4 both the measurement and the response to it.
- **A lint gate that passes because nothing ran.** C58b is the whole answer to that, and it
  exists because curvecast's gate went green on exactly that failure on 2026-09-09.

---

## 6. Result

*Filled in after the run, from the run. Nothing above this line was edited afterwards.*

**Suite: 62 passed, 0 failed, 0 skipped, 4.04s.** `lint-imports`: 16 files, 32 dependencies,
**2 kept, 0 broken**. `ruff check .` with the pinned selection: **0 findings**.

### 6.1 The scorecard

| id | outcome |
|---|---|
| **P1** | **WRONG.** Two bars failed on their first complete run — C51 and C58. Both are below, and both were the bar's fault rather than the code's, which is the outcome this prediction was phrased to be able to have. |
| **P2** | **RIGHT**, exactly. 51 → 62. |
| **P3** | **RIGHT.** No pre-existing bar turned red at any point. |
| **P4** | **RIGHT.** `ENGINE_IMPORT_ROOTS` is untouched and C27 is green; `sensitivity.py` adds no root the census did not already carry. |
| **P5** | **RIGHT.** 2 kept, 0 broken. |
| **P6** | **RIGHT.** $370.67/bp, to the cent. |
| **P7** | **RIGHT**, and see 6.2 — it went 1 → 0 and then briefly 0 → 1, on a finding this package itself introduced. |
| **P8** | **RIGHT.** 1.142%, 5.177%, 11.730%, recomputed from the committed fixture. |

### 6.2 C58 failed on its first run, on a finding the gate's own commit had just written

The lint gate went red immediately, on `test_sensitivity.py:33 F401` — an unused `Direction`
imported by D4's *new* test module, written an hour after the gate. Deleted, and the gate is
green at zero.

It is worth recording rather than tidying away. The gate was proposed on the strength of one
dead import left by D5, and its very first execution found a second one written by the package
that was installing it. A floor that catches its own author on day one is the argument for the
floor, made better than the pre-commit made it.

### 6.3 C51 was wrong about where the two conventions disagree

The bar asserted that the par proxy's modified duration differs from the exact zero form at
every yield. It does not. **At `y = 0` the par bond's coupon is zero, so it *is* the
zero-coupon bond it is being compared against**, and both give exactly the maturity.
`par_bond_duration_convexity(0.0, 10)` returns `(10.0, 110.0)`.

The coincidence is duration-only, and the second number is the reason: the exact continuous
convexity at ten years is `T² = 100`, and the annual-pay form gives `T(T+1) = 110` at the same
point. The cash flows have collapsed to a single payment and the **compounding convention has
not**, so the two forms agree on the first derivative and still disagree on the second. The
bar now asserts the divergence on the five non-zero yields, and asserts the coincidence — and
the surviving convexity gap — at zero, which is strictly more than it claimed before it failed.

No code changed for either failure. Both were the bar, and the second one taught the package
something it did not know when the pre-commit was written.

### 6.4 The book, as D4 reads it

`US_CASH_BOOK` at 2014-12-24, the last DEV session on which every series it needs is
published. Yields in percent: `SVENY02` 0.76910001039505, `SVENY05` 1.79840004444122,
`SVENY10` 2.33540010452271, `DFII5` 0.5, `DEXUSEU` 1.2188.

| leg | sense | net DV01 / bp | components |
|---|---|---|---|
| `us_2y` | `PRICE` | **+40,000.00** | `SVENY02` D=2.000000, dv01 +40,000.00 |
| `us_10y` | `PRICE` | **+60,000.00** | `SVENY10` D=10.000000, dv01 +60,000.00 |
| `us_breakeven_5y` | `RATE` | **+370.67** | `SVENY05` D=5.000000, dv01 +25,000.00; `DFII5` D=4.925866, dv01 −24,629.33 |
| `eurusd` | `NONE` | **0.00** | none, by declaration |

A +25 bp parallel move on all four curves: `us_2y` +1,000,000.00, `us_10y` +1,500,000.00,
`us_breakeven_5y` +9,266.71, `eurusd` 0.00, **total +2,509,266.71**. The signs are the book's
thesis — short the front end and the ten-year against a repricing of the path — and the
breakeven's four decimal places of contribution are the residual it is not supposed to have.

Under MEIP's par proxy the same two rate legs would read +39,543.23 and +52,961.85 per basis
point, which is the 11.7% at ten years in the currency the book is actually stated in.

### 6.5 What the next package inherits

- **D7b owns two re-expressions this package declined**: whether `us_breakeven_5y` should be
  matched on duration rather than on coefficients (§0.6, C55), and whether leg 1 belongs on
  `DGS2` rather than `SVENY02` (D5's DD40, still open).
- **The par branch cannot reach the front end D5 graded.** `DGS3MO` and `DGS6MO` are 0.25 and
  0.5 years and MEIP's form takes whole years; `modified_duration` refuses them by name. The
  package that wants a short leg meets that refusal, which is the point of making it one.
- **`numpy` is still not a dependency.** D8's covariance is the first thing that needs it, and
  the census turns red until the commit that imports it records it.
- **`RateSense.UNPRICEABLE` is a refusal and must stay one.** Any later package that sums over
  legs and treats it as 0.0 has silently priced the option leg at nothing.
