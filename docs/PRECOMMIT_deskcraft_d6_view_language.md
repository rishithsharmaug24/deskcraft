# PRE-COMMIT — D6: the view language, and the factor basis that was never this package's to fit

**Written 2026-09-15, before any change to this repository.** Every number in §0 was measured
on this machine today, against deskcraft at `a610fa4` (clean tree, 62 passed), curvecast at
`7727ee2` and MEIP untouched. Nothing below §0 has been run.

**Ids.** Decisions `DD59`–`DD68`. Bars `B59`–`B71`, executable as `C59`–`C71`.

**The row this package closes.** `BUILD_ORDER_D3_D16.md` §4: *"D6 | The view language | Closed
grammar — `LEVEL`, `SLOPE`, `CURVATURE`, `REAL_VS_NOMINAL`, `CREDIT_VS_RATES`, `CROSS_MARKET`,
each with a direction. Compiles to a target vector in the DEV factor basis. Carries H3."*

**This package scores a registered claim, and it is the first one that does.** `CLAIMS` names
D6 as the scorer of **H3 — "view fidelity: the book loads on the view's factor", predicted
PASS**. `registers.py` has said since D3a that *"the first package that sets one is D6, for H3,
and its own suite is red from the moment its pre-commit document is written until it does."*
C34 reads closure from this document's existence, so writing this file turns the suite red on
purpose, and only the commit that records H3's verdict turns it green again. D4 could decline
to grade because no row named it. This package has no such exit, and the prediction was fixed
in `CLAIMS` eight packages ago and cannot be revised now.

---

## 0. Measured before decided

### 0.1 The "DEV factor basis" is not missing, and it was never D6's to fit

The row names an object no module in this repository builds. There is no factor module in
`src/deskcraft/`; the eight files are `book`, `panel`, `reference`, `registers`, `sensitivity`,
`sources`, `window` and `__init__`. `window.py` names the factor basis as one of three fitted
objects — *"the covariance, the factor basis, the GARCH filter"* — and of those, the covariance
is D8 and the GARCH filter is D12. No row in §4 fits the factor basis. Searching the build
order for `PCA`, `principal component` or `Litterman` returns nothing.

That reads like a gap in the order. It is not. Two places in this repository already say where
the basis comes from, and both predate the row:

- `pyproject.toml`, D1, on why `dependencies` is empty: *"The engine's inputs are stated books
  and **the objects curvecast item 28 produces**."*
- `pyproject.toml`, D1, on the withdrawn import contract: *"deskcraft imports `meip.rates`
  (D4's duration and convexity) and **`curvecast.stage3.factor_space`** (D10's effective rank)
  by design."*

curvecast item 28 is WP-R1, and `src/curvecast/stage3/factor_space.py` is 627 lines of it. It
fits a PCA of the GSW zero curve **on changes, on DEV**, over a tenor grid of eight — and that
grid is `SVENY01, 02, 03, 05, 07, 10, 20, 30`, which is the first eight columns of
`panel_daily_dev_20260914.csv`, in order. The basis exists, it is fitted on this repository's
own window, and the row's silence about where it comes from is the whole of what made it look
absent.

### 0.2 deskcraft's committed panel and curvecast's fixture are the same GSW bytes

Measured today, comparing `tests/fixtures/panel_daily_dev_20260914.csv`'s eight `SVENY` columns
against curvecast's `tests/fixtures/gsw_zero_dev.csv`:

    rows                   7,044   both
    date sets equal        True
    rows differing             0   of 7,044 shared
    blank rows               309   both

Not merely consistent — identical, field for field, including which sessions are blank. D3b's
panel and curvecast's item-28 fixture were cut from the same source file, so a basis fitted here
and a basis fitted there are fitted on one sample, and any disagreement between them is an
arithmetic disagreement rather than a data one.

### 0.3 curvecast's PCA runs from its own bytes and reproduces its published spectrum

`factor_space.py` reaches `numpy`, `curvecast.pit.seal` and `curvecast.stage3.conditioning` at
module level, and curvecast is not importable on `PRODUCTION_PYTHON`. So the D4 mechanism was
tried: parse the single function node out of the source, `compile` it alone, `exec` it. Both
`_pca` and `effective_rank` execute with nothing in their namespace but `numpy`.

Run on deskcraft's own committed panel, complete-cased over the eight `SVENY` columns:

    complete-case sessions    6,735          (7,044 - 309)
    differences               6,734

    basis "changes"    PC1  83.9352%    PC1-3  97.9021%    effective rank  1.8231
    basis "levels"     PC1  95.9424%    PC1-3  99.9064%    effective rank  1.2000

Every one of those figures is curvecast's own published number, from `factor_space.py`'s
docstring and from `BUILD_ORDER_D3_D16.md` §1's *"three factors explain 97.9% of curve
variance"*. 6,735 is the count curvecast's `load_zero_panel` docstring states. This is a
cross-check against a measurement made elsewhere, on the same data, by other code — not a
result of this package.

**Nothing above reads a loading.** The orientation of PC2 and PC3 has deliberately not been
looked at, because §3 predicts it.

### 0.4 curvecast's sign rule is a diff-stability rule, and it carries no meaning

`_pca` ends:

    for k in range(vectors.shape[1]):
        # Sign-normalise to the largest-magnitude element. An eigenvector's sign is arbitrary,
        # and an arbitrary sign in a committed table is a diff that moves for no reason.
        if vectors[int(np.argmax(np.abs(vectors[:, k]))), k] < 0:
            vectors[:, k] = -vectors[:, k]

The comment says exactly what the rule is for: a committed table whose signs do not move
between runs. It is the right rule for that, and it is not a rule about *steepening*. Nothing
in it makes `+PC2` mean the long end rising against the short end rather than the reverse; the
largest-magnitude element of a slope factor can sit at either end of the grid, and which end it
sits at is a property of the sample.

A view language that took `+PC2` to be a steepener because the number is positive would be
stating the opposite view on half of all possible samples, and would do it silently. This is
the single most dangerous thing in this package, and DD62 is the answer to it.

### 0.5 Three of the six grammar terms are not on the nominal curve at all

`LEVEL`, `SLOPE` and `CURVATURE` are the classical factors of a single nominal curve and the
PCA produces them. `REAL_VS_NOMINAL`, `CREDIT_VS_RATES` and `CROSS_MARKET` are contrasts
*between* curves: the first reaches `DFII5/10/30`, the second `GZ_SPREAD`, the third
`DE_ZERO_10Y`. None of those is in the eight-column grid the PCA is fitted on, and two of them
are not even on the daily grid — `GZ_SPREAD` is monthly (323 observations against 6,504) and
`DE_ZERO_10Y` is not in the panel at all.

So "the DEV factor basis" cannot be the eight-tenor eigenbasis and cover the grammar. The
grammar spans six directions and the fit supplies three of them. DD63 states the other three
rather than fitting them, which is the honest shape: a contrast between two curves is a
definition, not an eigenvector, and calling it fitted would borrow credibility from an
arithmetic that never touched it.

### 0.6 What the book's exposure actually is, from D4's own module

`book_dv01(US_CASH_BOOK, ...)` on 2014-12-24, the date D4's C55 pins:

| leg | sense | net DV01 |
|---|---|---|
| `us_2y` | PRICE | **+40,000.00** |
| `us_10y` | PRICE | **+60,000.00** |
| `us_breakeven_5y` | RATE | **+370.67** |
| `eurusd` | NONE | 0.00, with no components |

Collapsed to series, which is the form a factor loading needs:

    SVENY02     +40,000.00
    SVENY05     +25,000.00
    SVENY10     +60,000.00
    DFII5       -24,629.33
    ----------------------
    total      +100,370.67

Three facts follow and all three matter below. The three nominal exposures **carry the same
sign**, which is what a level position looks like. The ten-year carries **more DV01 than the
two-year** despite a notional a third the size, so the book is not flat along the curve. And
the only non-nominal exposure in the whole book is `DFII5`, which exists because leg 3's
declared DV01 neutrality does not hold — D4's finding, arriving here as the book's entire
`REAL_VS_NOMINAL` coordinate.

### 0.7 `numpy` is needed, for a reason D4's refusal does not cover

D4 refused numpy and gave the reason in its §0.8: *"a dependency added because a comment
predicted one"*, with arithmetic that was four legs, five series and six scalar formulas. That
reason does not reach here. This package's arithmetic is a covariance and a symmetric
eigendecomposition over 6,734 × 8.

It could be hand-rolled. Jacobi rotation on an 8×8 symmetric matrix is forty lines and would
agree with LAPACK to about `1e-15`. That is precisely the objection: it would agree *to a
tolerance*, and D4's C50 refused a tolerance for exactly this shape of check — *"a tolerance
would pass a reordered summation, which is how a restatement stops being one."* A restatement
of curvecast's `_pca` that called a different eigensolver would not be a restatement. It would
be a second implementation, and the bar holding the two together would have to be weakened to
let it pass.

`numpy` 2.4.6 is importable on `PRODUCTION_PYTHON`. `ENGINE_IMPORT_ROOTS` is an equality, so it
is named there in the same commit that imports it, and `pyproject.toml`'s D1 comment — already
annotated once by D4 — is annotated again rather than rewritten (D70).

### 0.8 The tree is green before this package

`a610fa4`, `git status --porcelain` empty, **62 passed, 0 failed, 0 skipped in 4.17s**.
`lint-imports` 2 kept, 0 broken. `ruff check .` 0 findings.

---

## 1. Decisions

### DD59. The basis is curvecast's, restated here and checked against its bytes

Not fitted afresh as an independent object, and not received as a fixture of numbers. Three
options were available and the third is taken:

- **Import it.** Unavailable: curvecast is not importable on this interpreter, and putting it
  on the import path would drag `pit.seal` and `stage3.conditioning` into a test process eight
  packages before the plan wants curvecast reachable at all.
- **Receive a committed fixture of loadings.** Available — D3b's shape — and worse. A fixture
  of eight eigenvectors is a table nobody downstream can re-derive, and deskcraft already holds
  the input bytes, so the fixture would be a second copy of something this repository can
  compute.
- **Restate the fit, and check the restatement by executing curvecast's own function** (taken).
  D4's C50 shape, and stronger here than it was there, because §0.2 establishes that the two
  repositories hold the same input bytes — so the comparison is over the arithmetic alone.

### DD60. `numpy` arrives at D6

Per §0.7. The reason is not that a comment predicted it: the reason is that a restatement
checked at exact equality has to call the same eigensolver, and hand-rolling one would force
the bar down to a tolerance. Named in `ENGINE_IMPORT_ROOTS`, declared in `pyproject.toml`, and
both of D1's predictions about it are annotated rather than deleted.

### DD61. Fitted on **changes**, in basis points, complete-case — and the basis travels

curvecast's D405 pre-registered changes over levels and the contrast is large: 83.9352% for PC1
on changes against 95.9424% on levels, from one panel. `FactorBasis.basis` carries the string
for curvecast's reason — *"a spectrum that travels without saying which it is will eventually
be quoted as the other one"* — and both are computable here.

### DD62. Sign normalisation and semantic orientation are two different steps

The basis keeps curvecast's largest-magnitude rule exactly, so the eigenvectors here and there
are the same vectors. **Orientation is separate, measured, and recorded on its own object.**
Each of the three fitted factors carries a stated statistic whose sign decides which way its
"UP" points:

    LEVEL       sum of the eight loadings                        > 0  =>  all yields rise
    SLOPE       loading(SVENY30) - loading(SVENY01)              > 0  =>  steepening
    CURVATURE   loading(SVENY02) + loading(SVENY30)
                                  - 2 x loading(SVENY10)         > 0  =>  wings up vs belly

The statistic and its measured value are both fields, so a reader can disagree with the choice
of statistic rather than with an unexplained sign. A statistic that comes out at zero is a
refusal, not a coin flip.

### DD63. Six directions of **market movement** in series space; three fitted, three stated

Every factor is a unit vector over named series, and every factor means *a way the market
moves*, never *a position that profits*. That makes a loading an inner product with D4's signed
DV01 vector, and the product is P&L per basis point of that factor's move, with no sign
convention applied twice.

    LEVEL, SLOPE, CURVATURE   PC1, PC2, PC3 over the eight SVENY series, oriented per DD62
    REAL_VS_NOMINAL           +1 on SVENY05/10/30, -1 on DFII5/10/30, normalised.
                              UP = breakevens widen.
    CREDIT_VS_RATES           +1 on GZ_SPREAD. UP = credit widens against rates.
                              A spread series' own move *is* the contrast.
    CROSS_MARKET              +1 on SVENY10, -1 on DE_ZERO_10Y, normalised.
                              UP = the US cheapens against Germany.

The contrasts are stated at **matched tenors** because an unmatched contrast is a duration bet
wearing a spread's name — which is D4's finding about leg 3, one layer up.

### DD64. The six are **not** orthogonal, and the Gram matrix travels with them

`REAL_VS_NOMINAL` and `CROSS_MARKET` both put positive weight on nominal series that `LEVEL`
also spans. That overlap is not an error to be removed: a book that is long nominal duration
and holds no TIPS genuinely does profit when breakevens widen because nominals sold off, and a
US-only book genuinely does load on a US-versus-Germany move, because it holds one side of it.
Orthogonalising would delete a true exposure to make a table tidier.

What it does mean is that a loading in this basis cannot be read as a variance share. So the
**Gram matrix of the six factors is computed and carried on the basis object**, and the bar
asserts the off-diagonal is non-zero — because a basis silently believed orthogonal is the way
this decision turns into a defect.

### DD65. A view naming a factor the book structurally cannot reach is refused

D4's DD55 shape, restated: a `CurveShift` naming a series no leg holds raises, *"because a
mistyped mnemonic that silently contributes nothing is a stress test reporting 'no effect' for
a reason that has nothing to do with the book."* A view has the same failure available. Asking
`US_CASH_BOOK` for its `CREDIT_VS_RATES` fidelity must raise, because no leg reaches
`GZ_SPREAD` and a reported fidelity of zero would be indistinguishable from a measured absence
of credit risk.

**Partial reach is not refusal.** `US_CASH_BOOK` holds `SVENY10` and therefore reaches half of
`CROSS_MARKET`; that loading is real and is reported.

### DD66. The reference view is `(LEVEL, UP)`, compiled from the thesis before the run

`REFERENCE_THESIS` is *"Fewer policy cuts than priced, plus a fiscal-driven repricing of the
term premium."* `reference.py` glosses leg 1 as *"the policy-expectations component: if the
path prices fewer cuts, the two-year yield rises"* and leg 2 as *"the term-premium component"*.
Both clauses raise yields; the thesis names two **drivers** and does not say which end moves
further.

So the compilation is one term, `(LEVEL, UP)`. Adding `(SLOPE, UP)` would be an inference about
relative magnitudes that the thesis text does not make, and it would be an inference made by
the package that is about to be graded on whether the book matches it.

**The two-term variant is stated here anyway**, `(LEVEL, UP) + (SLOPE, UP)`, and is reported
beside the one-term reading in §6 — fixed now so it cannot be produced afterwards as whichever
of the two came out better.

### DD67. H3 is operationalised as dominance plus sign, and the magnitude is reported beside it

*"The book loads on the view's factor"* is qualitative and this package has to make it
checkable. `loads_on_view` is true when **the view's factor carries the largest absolute
loading of the six, and that loading's sign agrees with the view's stated direction.** Both
halves are needed: dominance alone would pass a book positioned for exactly the opposite view.

Reported beside it, never instead of it: all six signed loadings, the dominant share
`|largest| / sum of |all six|`, and the cosine between the book's exposure vector and the
compiled target. The share is **not** a variance decomposition and says so, per DD64.

### DD68. `ViewDirection`'s value is its sign

D2's `Direction` pattern, for D2's reason: `UP = 1`, `DOWN = -1`, so compiling a directed term
is one multiplication with no lookup table, and there is exactly one representation of a
downward view rather than two that can disagree.

---

## 2. Bars

Each `Bn` is the claim; `Cn` is the test that executes it. All in `tests/test_views.py`.

| id | claim |
|---|---|
| **B59** | deskcraft's committed panel and curvecast's `gsw_zero_dev.csv` carry the same GSW bytes: 7,044 rows each, equal date sets, **0 differing rows** over the eight `SVENY` columns, 309 blank in both. Skips loudly if curvecast is not on this machine. |
| **B60** | deskcraft's `_pca` restatement reproduces curvecast's **exactly** — eigenvalues, eigenvectors and covariance, at exact equality, not a tolerance — with curvecast's function parsed out of `factor_space.py` and executed from its own bytes. Skips loudly if curvecast is absent. |
| **B61** | The fitted basis reproduces curvecast's published spectrum to 4 dp: on changes, PC1 **83.9352%**, PC1–3 **97.9021%**, effective rank **1.8231**, over **6,734** differences from **6,735** complete-case sessions; on levels, PC1 **95.9424%**. |
| **B62** | PC1, PC2 and PC3 have the Litterman–Scheinkman *shape*: **0, 1 and 2 sign changes** respectively across the tenor grid, so the names are earned by the loadings rather than assigned by rank. |
| **B63** | The orientation map is total over the three fitted factors; each statistic is non-zero, so no sign is undetermined; and orienting an already-oriented basis is idempotent. |
| **B64** | All six factor vectors are unit-norm; the three stated contrasts are exactly the series and coefficients DD63 names; the Gram matrix is symmetric with unit diagonal; and `LEVEL · REAL_VS_NOMINAL` is **non-zero**, so DD64's overlap is asserted rather than assumed away. |
| **B65** | `View` refuses an empty view, the same factor twice, a non-`ViewFactor` term and a non-`ViewDirection` direction. |
| **B66** | `(LEVEL, UP)` and `(LEVEL, DOWN)` compile to exactly opposite target vectors, and a two-term view compiles to the signed sum of its terms. |
| **B67** | The book's exposure vector is D4's `book_dv01` collapsed by series and nothing else: `SVENY02 +40,000.00`, `SVENY05 +25,000.00`, `SVENY10 +60,000.00`, `DFII5 -24,629.33`, to the cent, with `eurusd` contributing no series at all. |
| **B68** | **H3.** `fidelity(US_CASH_BOOK, (LEVEL, UP))` reports `LEVEL` as the dominant factor with a positive loading, so `loads_on_view` is true. |
| **B69** | The statistic is capable of saying no: `fidelity(US_CASH_BOOK, (CURVATURE, UP))` reports `loads_on_view` **false**. A fidelity measure that cannot fail on this book has not tested H3. |
| **B70** | `fidelity(US_CASH_BOOK, (CREDIT_VS_RATES, UP))` **raises** (DD65), naming `GZ_SPREAD`; and `CROSS_MARKET` does **not** raise, because the book holds `SVENY10`. |
| **B71** | `CLAIMS`'s `H3` row carries a `Verdict`, and C34 is green — the first verdict this register has ever held. |

---

## 3. Predictions, fixed before the run

| id | prediction |
|---|---|
| **P1** | All of C59–C71 pass on their first complete run. *(D4's P1 said this and was wrong twice. Stated the same way again, for the same reason: it can be wrong in the direction that costs.)* |
| **P2** | The suite goes 62 → 75: thirteen bars added, none removed. |
| **P3** | `ENGINE_IMPORT_ROOTS` gains exactly one root, `numpy`, and `MODULES` gains exactly two, `deskcraft.factors` and `deskcraft.views`. Nothing else in the boundary test moves. |
| **P4** | `lint-imports` stays **2 kept, 0 broken**. `numpy` is in neither forbidden list, and no engine module reaches a banned root. |
| **P5** | **PC1 needs no flip and at least one of PC2/PC3 does.** curvecast's largest-magnitude rule puts PC1's biggest loading positive and a level factor's loadings share a sign, so DD62's sum statistic comes out positive already. PC2 and PC3 have no such guarantee, and I predict **exactly one** of the two is flipped by DD62. *(This is the prediction §0.4 was written to make possible, and it is the one I would least like to be wrong about.)* |
| **P6** | **H3 passes.** All three nominal exposures carry the same sign and PC1 is 83.9352% of the variance, so the level loading takes the sum of `+40,000`, `+25,000` and `+60,000` while slope takes only the difference pattern. Dominance should not be close. |
| **P7** | **H3 passing is weak evidence, and the run will show why.** The `LEVEL` loading exceeds the `SLOPE` loading by more than 3×, and the two-term variant of DD66 **also** reports `LEVEL` dominant — meaning the book would have passed H3 under either compilation of the thesis, which is a property of PC1's share rather than of the book's fidelity. If this is right, H3's PASS is recorded as a PASS and annotated as a weak one. |
| **P8** | `REAL_VS_NOMINAL` is the **second** largest absolute loading of the six, ahead of `SLOPE` and `CROSS_MARKET`, because it is the only factor the `-24,629.33` on `DFII5` reaches with full weight — so D4's residual, which was a defect one layer down, is a real coordinate of this book one layer up. |

---

## 4. What this package does not do

- **It does not fit a basis of its own.** DD59. The arithmetic is curvecast's, restated, and
  C60 holds the two at exact equality against curvecast's own bytes.
- **It does not re-express any leg, and it does not size one.** The `DFII5` coordinate exists
  because leg 3's declared `Neutrality.DV01` is false by 370.67/bp. That is measured again here
  from a second direction and `reference.py` stays annotated rather than edited (D70). The
  re-expression is still **D7b's**.
- **It does not choose the view after seeing the loadings.** DD66 fixes the reference view from
  the thesis text, and states the two-term variant in advance so neither can be presented later
  as the one that was meant.
- **It does not generate legs, cost anything, or rank structures.** The fidelity statistic is
  what D7b's greedy addition will maximise and what D9's F3 flag will read; neither is built
  here.
- **It does not touch MEIP or write to curvecast.** `factor_space.py` is read and one function
  is executed from its own bytes. The standing `meip:untouched` gate covers the first.
- **It does not claim the six factors are orthogonal, or that the dominant share is a variance
  decomposition.** DD64, and B64 asserts the overlap rather than hiding it.

## 5. What would make this wrong

- **A view language that reads `+PC2` as a steepener.** §0.4. curvecast's sign rule is for diff
  stability and carries no market meaning, and this is the failure that would be silent,
  plausible, and exactly backwards on half of all samples. DD62 and C63 are the whole answer.
- **A fidelity statistic that cannot fail.** If every view over this book returned
  `loads_on_view = True`, H3's PASS would be an artifact of the measure. C69 is the bar that
  makes the statistic capable of a no, and P7 is the prediction that says what the PASS is
  worth even when it is honest.
- **H3 scored against a view chosen to make it pass.** DD66 forecloses it by fixing the
  compilation from the thesis text, in this document, before any loading is computed.
- **A dominant share read as a variance share.** DD64. The six directions are not orthogonal
  and the number does not decompose anything.
- **A verdict recorded for a claim this package did not actually score**, or a verdict withheld
  after this document lands. C34 refuses both, and this is the first package where either is
  possible.

---

## 6. Result

*Filled in after the run, from the run. Nothing above this line was edited afterwards.*

**Suite: 75 passed, 0 failed, 0 skipped, 4.29s.** `lint-imports`: 19 files, 47 dependencies,
**2 kept, 0 broken**. `ruff check .` with the pinned selection: **0 findings**.

### 6.1 The scorecard

| id | outcome |
|---|---|
| **P1** | **WRONG**, twice over. `C10` — a D2 bar, not one of D6's — turned red on the first run, and is §6.2. And `C71` could not have passed on a run that precedes the verdict it asserts, which is a defect in how P1 was phrased rather than in the bar: the verdict has to come *from* a run, so "all of C59–C71 pass on their first complete run" was never satisfiable as written. Recorded rather than reworded. |
| **P2** | **RIGHT**, exactly. 62 → 75. |
| **P3** | **RIGHT as written, and narrower than it should have been.** `ENGINE_IMPORT_ROOTS` gained exactly `numpy`; `MODULES` gained exactly `deskcraft.factors` and `deskcraft.views`; nothing else in the boundary test moved. But D4's P3 said *"no existing bar turns red"* and this one only claimed the boundary test would not move — so C10 firing is outside what P3 promised, which is the wrong place for a prediction's edge to be. |
| **P4** | **RIGHT.** 2 kept, 0 broken, over 19 files and 47 dependencies (16 and 32 at D4). |
| **P5** | **WRONG.** §6.3. I predicted PC1 would need no flip and **exactly one** of PC2/PC3 would. Measured: **all three were kept**, zero flips. The reasoning that produced the prediction was sound and the conclusion was wrong, and §6.3 is why that does not rescue DD62 — it sharpens it. |
| **P6** | **RIGHT.** H3 passes. `LEVEL` dominant at **+46,989.92** per basis point, positive, `loads_on_view` true. |
| **P7** | **RIGHT on both stated halves, and it measured the wrong weakness.** `|LEVEL| / |SLOPE|` is **7.854**, comfortably past the predicted 3×, and the two-term variant also reports `LEVEL` dominant and true. But the margin that actually decides H3 is not the one over `SLOPE` — it is the one over `REAL_VS_NOMINAL`, and that is **4.991%**. §6.4. |
| **P8** | **RIGHT**, including the reason. `REAL_VS_NOMINAL` is the second largest absolute loading, ahead of `CROSS_MARKET`, `CURVATURE` and `SLOPE`. It is reached by the `-24,629.33` on `DFII5` that exists only because leg 3's declared DV01 neutrality is false. |

### 6.2 C10 fired on the first run, and the fix was a rename

The grammar's direction type was written as `ViewDirection`. `C10` — D2's bar asserting that
`Direction` and `Notional` are defined in `book.py` and nowhere else — caught it as a
**near-name**, which is a scan it carries for a stated reason: *"a near-name growing beside the
real one is how 'one binding site' stops being true without anything being renamed."*

It was right, and the case is stronger than the scan could know. `Direction` and
`ViewDirection` would have been an `IntEnum` whose value is a sign, twice, with opposite
subjects — one the sign of a **position**, the other the sign of a **market move** — and
nothing in either name says which. That is the most confusable arrangement the two concepts
could have been given.

Fixed by **renaming the symbol, never by exempting it**, which is the rule carried from
curvecast where `EXEMPT_FIELDS` is `{}` and four packages renamed their own fields rather than
add the first entry. `Move` / `ViewTerm`, and the field is `move`. No bar was weakened and
`C10` is untouched.

The observation worth keeping: **the bar that caught this was written at D2 for a different
purpose and had never fired.** D3b's lesson — *"a package's own bars passing is not evidence
that the package is right"* — with its converse, that an old bar firing on new work is the
cheapest correction available.

### 6.3 P5 was wrong, and the reason makes DD62 more load-bearing rather than less

All three fitted factors came out already pointing the stated way, so curvecast's
largest-magnitude rule and DD62's semantic statistics agreed on every one:

| factor | statistic | value | outcome |
|---|---|---|---|
| `LEVEL` | sum of the eight loadings | **+2.79868** | kept |
| `SLOPE` | `l(SVENY30) - l(SVENY01)` | **+1.00056** | kept |
| `CURVATURE` | `l(SVENY02) + l(SVENY30) - 2 l(SVENY10)` | **+1.76816** | kept |

A reader could take that as evidence DD62 was unnecessary machinery. It is the opposite, and
the margin says so. curvecast's rule signs `PC2` by whichever element is largest in magnitude,
and on this sample those two candidates are the ends of the grid:

    PC2 at SVENY01   -0.423283
    PC2 at SVENY30   +0.577280      |long| / |front| = 1.3638

**The agreement rests on a 36.4% margin between two numbers that a different sample could
reorder.** Had the front end carried the larger magnitude — which is what a sample dominated
by front-end volatility produces — curvecast's rule would have signed `PC2` to make the
*front* element positive, and `+PC2` would have silently meant a **flattening**. Every view
compiled afterwards, every fidelity, and H3 itself would have inherited that, and no test in
this repository other than C63 would have noticed.

So the honest reading is: the prediction was wrong, the two rules coincide on this sample, and
the coincidence is a property of the sample and not of either rule. That is exactly the
condition under which a guard looks redundant and is not.

### 6.4 H3 is PASS, and it is a thin PASS

`US_CASH_BOOK` against `(LEVEL, UP)`, on 2014-12-24, per basis point of each factor's move:

| factor | loading | share of total |
|---|---|---|
| **`LEVEL`** | **+46,989.92** | **29.22%** ← dominant |
| `REAL_VS_NOMINAL` | +44,755.99 | 27.83% |
| `CROSS_MARKET` | +42,426.41 | 26.38% |
| `CURVATURE` | −20,665.78 | 12.85% |
| `SLOPE` | −5,983.22 | 3.72% |
| `CREDIT_VS_RATES` | 0.00 | 0.00% — **structural**, and flagged as such |

`loads_on_view` is **true**: `LEVEL` is dominant and positive, which is the direction the view
states. **H3 = PASS, as `CLAIMS` predicted eight packages ago.** The verdict is recorded.

**What the number is worth.** P7 predicted the PASS would be weak and named the wrong reason.
`LEVEL` beats `SLOPE` by 7.854×, as predicted — but `SLOPE` is not the runner-up. `LEVEL`
beats `REAL_VS_NOMINAL` by **2,233.93 per basis point, which is 4.991%**, and beats
`CROSS_MARKET` by 10.756%. The top three carry **83.43%** of the total absolute loading between
them and sit within 11% of each other.

**And all three are substantially the same position, counted three times.** That is DD64's
non-orthogonality arriving with numbers on it:

    LEVEL . REAL_VS_NOMINAL   +0.4434
    LEVEL . CROSS_MARKET      +0.2717
    CURVATURE . CROSS_MARKET  -0.3005

`CROSS_MARKET`'s loading is **exactly** `60,000 / sqrt(2) = 42,426.4069` — the ten-year nominal
leg and nothing else, because the book holds one side of the pair and `DE_ZERO_10Y` is zero. It
is arithmetically correct and it is not a cross-market bet; it is the US half of one.
`REAL_VS_NOMINAL` is `(25,000 + 60,000 + 24,629.33) / sqrt(6)`, and the third term is positive
because a long breakeven does profit when breakevens widen — also correct, and also driven
mostly by nominal duration the other two factors already counted.

So `dominant_share` is doing less work on this book than its name suggests, which DD64 said in
advance it might and C64 asserted rather than hid. **The statistic is not changed in response.**
DD67 fixed it before the run, and rewriting it now to separate the overlap would be tuning a
measure after seeing what it measured — the failure D4's §5 named when it refused to re-express
leg 3 inside the package that found the residual.

**The package that owns the fix is named rather than improvised.** §2's F4 flag already states
the general form of this problem for legs: *"a partial contribution, not a raw pairwise
correlation, because raw correlation between two legs expressing the same thesis is high by
construction and says nothing."* The same argument applies one level up, to factors, and F4 is
**D9**'s. D10 carries the adjacent question, since curvecast's item 28 found the effective
number of bets is portfolio-free only in the PCA basis — which is the same fact about
non-orthogonal bases, met from the other side.

### 6.5 What the next package inherits

- **The basis is fitted and checkable, and it is curvecast's.** `factors.build_basis()` returns
  six named directions; C60 holds the arithmetic at exact equality against curvecast's own
  bytes and C59 establishes the inputs are the same bytes. Anything downstream that wants the
  DEV factor basis takes it from here rather than refitting.
- **`Move` is the direction type and `Direction` is still `book.py`'s alone.** C10 enforces
  that, and D18 — which extends this grammar from views to exposures — inherits the
  distinction already made rather than having to discover it.
- **A fidelity over non-orthogonal factors over-attributes, by measured amounts.** §6.4. **D9**
  owns the partial-contribution form under F4, and **D10** the basis-dependence question. A
  package that quotes `dominant_share` as a decomposition is quoting it wrong, and the Gram
  matrix travels on the object so that it can be checked rather than assumed.
- **`CREDIT_VS_RATES` is unreachable by this book and refuses rather than returning zero**
  (DD65). `GZ_SPREAD` is monthly and no leg holds it. The first package that wants a credit leg
  meets that refusal, which is the point of making it one — D4 left `DGS3MO`/`DGS6MO` behind
  the same kind of wall.
- **The reference view is one term and the alternative is on the record.** `REFERENCE_VIEW` and
  `REFERENCE_VIEW_TWO_TERM` both live in `views.py`, fixed in DD66 before any loading existed.
  D7b maximises fidelity to a view; which view it is handed is now a stated object rather than
  an argument.
- **`numpy` is a dependency now** (DD60), so D8's covariance no longer has to bring it. The
  census records it and D1's two predictions about it are annotated, not rewritten.
