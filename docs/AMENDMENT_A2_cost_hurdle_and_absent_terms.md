# Amendment A2 — the cost hurdle, fixed before the package it scores, and the bias nobody registered

*Written 2026-09-15, at `f9f46fa`, immediately after D7a closed and before D7b's pre-commit exists.*

D7a found that build-order **§3 does not survive being implemented**. An audit run afterwards over
the same document found that **§1 has the same defect and nobody has implemented §1 yet**: it names
a cost hurdle "fixed in advance (§3)", and §3 fixes none. Seven findings came out of that audit.
This amendment closes them.

**It is not a plan amendment.** No package is added, no row moves, `PACKAGE_BUDGET` is untouched and
`AMENDMENT_A1` §6's freeze at twenty-one core packages stands. What it does is the one thing that
becomes impossible later: **fix a threshold before the package scored by it can see what the
threshold does.** §6's own list already makes that a build failure for D9's flags. It did not say it
for the cost hurdle, and the cost hurdle is the number H9 is.

---

## 0. Measured before decided

Five things were stated in prose during the audit. Each was then measured, and two of the five came
back different enough that the fix is not the one the audit proposed.

| What the audit said | What was measured | Where |
|---|---|---|
| "The hurdle is a number somebody has to choose" | **It is not a free parameter at all.** A hurdle multiple `h` on cost `c` decides exactly what hurdle `1.0` on cost `h × c` decides, and §3.5 already reports the count at `0.5× / 1× / 2× / 4×`. Any `h ≠ 1` is a rung of a ladder the rule already runs | §2.2 |
| "Fix the holding period too, it is a second free parameter" | **It is the same parameter.** Measured on `us_10y`: `m × annualised_cost(leg, 1.0).half_spread` equals `annualised_cost(leg, 1/m).half_spread` at every rung, to the last bit — so the ladder already spans holding periods of 2y / 1y / 0.5y / 0.25y | §2.3 |
| "The hurdle compares annualised cost against view exposure" | **There is no annualised cost to compare.** `AnnualisedCost.total` **refuses on all four legs of `US_CASH_BOOK`**, under every input a caller can state, because the financing term has no parameter to state. The hurdle can only be defined on the spread term | §2.4 |
| "H9's PASS is expected by construction — every bias runs `FEWER_LEGS`" | **Half true, and the missing half reverses it.** Every row in `BIASES` runs `OVERSTATES_COST`/`FEWER_LEGS` — and **the largest effect in the model is not in `BIASES` at all**: omitting three of §3.2's four terms *understates* cost, which gives *more* legs. The two sets oppose and neither is sized | §3 |
| *(not proposed — found while measuring)* | **`eurusd` has no cost per unit of risk under any convention or multiplier**, so §3.5's ladder evaluates on **three of the reference book's four legs**. A stopping rule ranking legs by cost per risk cannot rank the fourth at all | §2.4 |

The measurement script is not committed — there is no `scripts/` here (DD58) — but every number
above is reproducible from `costs.py` and the committed panel on `2014-12-24`, and each one is
pinned by a bar below rather than left as an assertion in this document.

---

## 1. The seven findings, and what each becomes

| # | Finding | Severity | Becomes |
|---|---|---|---|
| **1** | §1.3's cost hurdle is "fixed in advance (§3)" and §3 fixes nothing. H9 *is* the hurdle, and D7b — the package that picks it — is the package scored by it | **highest** | `COST_HURDLE = 1.0` in `costs.py`, DD85–DD87, C91, and a §6 bullet |
| **2** | X11 has a register row and no body. It is the only item of eleven with nothing written, and C76 parses §1's table only | high | §X11 written; C88 makes a bodiless item red |
| **3** | `CARRIED_ITEMS.md` §4's "what is owed today" table is stale three ways and unparseable by the bar that reads §1 | medium | §4 folded into §1 (DD88); C88 holds one register, one table |
| **4** | `net_dv01` as a cost denominator is a decision in prose. C82 covers `costs.py`'s own functions, and on an outright the trap is quiet | medium | C89, an AST bar over all of `src/` (DD89) |
| **5** | H9's prediction was calibrated against a cost model now known to be too cheap | medium | **A fifth `BIASES` row**, `UNDERSTATES_COST`/`MORE_LEGS` (DD84), and §3 below |
| **6** | §1's "≈1,800 evaluations" assumes six rounds; H9 predicts three or four | low | Annotated, with the arithmetic; held by C90 |
| **7** | C10 will fire a third time and its message names no convention | low | One line in the assertion |
| *(8)* | The build order's §3 annotations carry numbers, and nothing held them against the module that produced them | low | C90 (DD90) |

Findings 1, 2 and 6 are the same defect: **a cross-reference in the commissioning text pointing at a
number that does not exist.** §3.3's *"both already graded"* was the same, and it was found by
implementing §3.3. §1 has not been implemented by anything, which is why now — before D7b's
pre-commit is written — is when these are cheap.

---

## 2. Finding 1 — the hurdle, fixed

### 2.1 Why this one is dangerous and the other six are not

§1 reads:

> 3. Each addition must clear a **cost hurdle** fixed in advance (§3).
> 4. It **stops** when the next-best addition fails the hurdle.

and §5 registers:

> **H9 — for the reference view, the cost-aware stopping rule terminates below six legs.**
> **Predicted: PASS**, at three or four.

By §1.4 the hurdle *is* the leg count: move it up, get fewer legs; move it down, get more. H9 says
the count lands at three or four. **H9's scorer is D7b**, and D7b is the package that would choose
the hurdle — while looking at candidate structures and their costs. A threshold chosen by the
package it scores is not a prediction, and a PASS obtained that way says nothing.

`AMENDMENT_A1` §5.1 caught the same class in H14: a bar whose stated form could not do the work it
claimed, withdrawn and split rather than reported. And §6 already forbids this exact thing one flag
over:

> **A flag threshold set after seeing which legs it fires on.** F1–F4's thresholds are fixed in
> D9's pre-commit, before any book is scored.

There is no equivalent sentence for the cost hurdle. §7 adds one.

### 2.2 The hurdle is not a number anyone gets to choose

State the rule in its general form. An addition enters when

    marginal view exposure gained, per unit of risk
    ----------------------------------------------   >=   HURDLE
    cost of the addition,        per unit of risk

for some hurdle `h`. Now observe that the same decision, for every candidate and in every round, is
reached by `h = 1` against a cost scaled by `h`. Selection under `(h, c)` and selection under
`(1, h·c)` are **the same function**, not similar answers — the comparison is a single inequality
and `h` multiplies one side of it.

And §3.5 already runs the entire selection at `0.5× / 1× / 2× / 4×` the central cost, reporting the
leg count at each. So **the grid of hurdles is already being reported**, and a second scalar named
`HURDLE` would report it twice under two names, with one of the two free to be chosen late.

> **DD85.** `COST_HURDLE = 1.0`, and it is fixed here because it is not a degree of freedom. Any
> other value is a rung of §3.5's ladder that the rule already runs. A package wanting the answer at
> a hurdle of 2 reads the `2×` rung; it does not set a hurdle.

This is stronger than picking a defensible number, and it is the reason to prefer it: **there is
nothing left for D7b to pick.** The count at each of the eight cells is the output, and the headline
that §3.5 demands — *is the count stable across the grid?* — is unchanged by anything D7b decides.

The scale involved is worth stating so that "1.0" is not mistaken for a small commitment. Measured
on the committed panel at `2014-12-24`, `cost_per_dv01` over the ladder's eight cells runs from
**0.078125 bp** (`us_10y`, `0.5×`, `AS_QUOTED`) to **1.939582 bp** (`us_breakeven_5y`, `4×`,
`PAR_PROXY`) — a **24.8× range**. At the central estimate the three priceable legs already span
**3.02×** (0.156250 against 0.472251). The ladder moves the decision far more than any plausible
argument about the hurdle's value would.

### 2.3 The holding period is the same parameter, and that was measured, not assumed

§3.2 ends with the sentence that makes a holding period mandatory:

> Shorter holding period pushes the first term up without limit, which is why a cost model with no
> holding-period assumption is not a cost model.

`annualised_cost` honours it: `holding_years` has no default. So the audit's second worry was that
fixing the hurdle without fixing the holding period leaves the free parameter intact under another
name. Measured on `us_10y`, the spread term:

| multiplier `m` | `m × annualised_cost(leg, 1.0)` | `annualised_cost(leg, 1/m)` | equal |
|---|---|---|---|
| 0.5 | 4,687.50 | 4,687.50 | yes |
| 1.0 | 9,375.00 | 9,375.00 | yes |
| 2.0 | 18,750.00 | 18,750.00 | yes |
| 4.0 | 37,500.00 | 37,500.00 | yes |

Exactly, at every rung — because the term is `2 × half_spread × notional / holding_years` and the
multiplier enters linearly. **The ladder is already a holding-period ladder**, spanning 2y / 1y /
0.5y / 0.25y.

> **DD87.** `HURDLE_HOLDING_YEARS = 1.0`. It is stated because §3.2 requires a cost model to state
> one, and it is not a second free parameter for DD85's reason: the ladder spans 0.25–2 years on
> the only term that exists.

**The caveat, recorded rather than discovered later.** This identity is exact *because the spread
term is the only term that exists today*. Financing does not scale with the holding period the same
way — annualised it is constant in it — so when X11 closes, the multiplier and the holding period
stop being the same axis. **X11's closure inherits the obligation to re-measure this table**, and
§4 records it as part of what closing X11 costs.

### 2.4 What the hurdle divides by, which is settled by measurement and not by preference

The rule needs a denominator. Three candidates existed and two are already foreclosed:

1. **`AnnualisedCost.total`.** Refuses. Measured on all four legs of `US_CASH_BOOK`, with a
   `MarketDepth` and a `Maintenance` both stated — the most a caller can supply:

   | leg | present | absent |
   |---|---|---|
   | `us_2y` | `half_spread`, `impact` | `financing`, `roll` |
   | `us_10y` | `half_spread`, `impact` | `financing`, `roll` |
   | `us_breakeven_5y` | `half_spread`, `impact`, `roll` | `financing` |
   | `eurusd` | `half_spread`, `impact`, `roll` | `financing` |

   Financing is absent on every leg under every input, because `annualised_cost` has **no parameter
   that could carry it** — the branch refuses unconditionally. `us_2y` and `us_10y` lose `roll` as
   well, and not for want of data: they declare `("financing", "delivery option", "roll")`
   unmodelled at **D2, DD12**. So even if H.15 and FR 2004B were graded tomorrow, two of the four
   reference legs would still refuse two of four terms, **by their own re-expression**. That is a
   fact about X11 worth more than the data gap, and §4 carries it.

2. **`LegSensitivity.net_dv01`.** Refused at DD81 and now by C89. It is a residual: 133.89× on
   `us_breakeven_5y`, `0/0` on `eurusd`, exactly zero on a spread whose neutrality holds.

3. **Expected shortfall at 97.5%**, which §1.1 names as the risk budget's unit. It does not exist
   yet: it needs D8's covariance, and D8 has not run.

> **DD86.** The hurdle's denominator is `cost_per_dv01` — round-trip spread cost per unit of **gross**
> DV01, in basis points of yield — because it is the only cost quantity this repository can compute.
> The stopping rule's risk unit becomes **expected shortfall at 97.5% when D9 lands**, and D7b
> **pre-registers** whether the surviving leg set changes under the substitution, in the same form
> X3 already requires of it for `dominant_share`. A denominator swapped in after seeing the leg set
> is the same defect as a hurdle chosen after seeing the structures.

**And the ranking is incomplete before it starts.** `eurusd` raises `NoRateRisk` under every
convention and every multiplier: it has a half-spread and no DV01, so it has no cost per unit of
risk. §3.5's ladder therefore evaluates **three of the reference book's four legs**. A greedy rule
ranking candidates by cost per risk cannot rank an FX hedge against a Treasury at all, and D7b must
say what it does about that rather than discovering it in the loop.

---

## 3. Finding 5 — H9's PASS, and the bias that was not in the bias register

D7a's §6.6 hands D7b a leg count that is *"a lower bound"*, on the grounds that every quantified
bias in `BIASES` runs `OVERSTATES_COST` / `FEWER_LEGS`, and so does the one unquantified row. That
is true of the register. The audit's finding was that it makes H9's predicted PASS suspiciously
cheap: if every bias in the model pushes the count down, a prediction that the count is low is
half-guaranteed.

**Measuring it turned the finding around.** The four rows of `BIASES` are all conservative. The
biggest effect in the cost model is not one of them:

> **Three of §3.2's four terms are absent, and an absent cost term understates cost.** Understating
> cost lets a marginal leg clear the hurdle. That is `UNDERSTATES_COST` / `MORE_LEGS` — the opposite
> direction from every row in the register — and it was not in the register, because the register
> was populated with *calibration* biases and the omission is a *coverage* bias.

The magnitudes cannot be compared: `indicative_bid_ask` is unquantified because the Fed's own paper
declines to size it, and the omission is unquantified because two of the three missing terms have no
graded input (X11) and the third is declined at D2 on two legs. **So the sign of the net bias on the
leg count is unknown**, and any sentence claiming the count is a bound in either direction is
unsupported.

> **DD84.** The omission is a bias and goes in the register, as
> `BIASES["absent_cost_terms"]` — `UNDERSTATES_COST`, `MORE_LEGS`, magnitude `None`, carried item
> **X11**. `compounded_bias` then returns an unquantified count of **3** rather than 2, which is
> exactly what that return value exists to force: a caller cannot report the product without seeing
> how much is missing from it.

This costs four equalities in C81 — `len(BIASES) == 4`, the direction set, the effect set, the
carried-item set — every one of which was written as an equality so that this edit could not happen
quietly. They are updated in the same commit, which is the friction working.

**What this does to H9, stated before D7b runs.** H9 stays as registered and its threshold does not
move. What changes is what a PASS means, and it is written down now so that it cannot be written
down afterwards:

- A PASS **at a count stable across all eight ladder cells** is informative. It says the stopping
  point is a property of the structures, not of the cost assumption — which is the thing §3.5 was
  built to detect.
- A PASS **that holds only at some rungs** is the honest headline §3.5 already names: *the result is
  a statement about costs rather than about structure*, and it must be reported that way.
- A PASS **obtained while three of four cost terms are absent** is, in addition, a statement about a
  cost model that is missing its coverage bias's magnitude in the `MORE_LEGS` direction. D7b reports
  `compounded_bias`'s unquantified count beside the leg count, so that the two travel together.

---

## 4. Finding 2 — X11 gets a body, and it is three questions rather than one

X11 is the only item of eleven with a row in `CARRIED_ITEMS.md` §1 and nothing written beneath it.
C76 parses §1's table and nothing else, so a bodiless item passes: the register can name a debt it
never states. §X11 is written in this commit, and **C88 makes a declared item with no `## X<n>.`
section turn the suite red**, so the gap closes for every future item too.

The body splits the item three ways, and the audit's version had only the first two:

1. **Impact — a grading problem.** §3.3 names NY Fed FR 2004B and `sources.py` has no row. But the
   term is *expressible*: a caller may state a `MarketDepth`, and the measurement above shows
   `impact` becoming a number the moment one is supplied. What is missing is the grade — an
   ungraded caller-stated depth is an assumption, and `CostBasis` has no `MEASURED` member for
   exactly that reason.
2. **Financing — a code problem before it is a data problem.** `annualised_cost` has **no parameter
   that could carry a financing input**; the branch refuses unconditionally. Grading a series does
   not make the term computable. And curvecast has already measured the data half, at **D218**:
   SOFR opens in **2018**, entirely outside the DEV window that ends **2014-12-31**, so SOFR is a
   decline and not a fetch. `DFF` reaches 1954 and H.15 is licence-cleared in curvecast's
   `DATA_AVAILABILITY.md` as `PUBLIC_DOMAIN`. **The route exists and it is not the one §3.3 names.**
3. **Frequency — an unowned question.** FR 2004B is **weekly**, by §3.3's own table, feeding a term
   reported per year. Whether a weekly series may drive an annual number, and by what method, is
   X2's class of question — and **X2 explicitly scopes itself out**: *"This is a covariance
   question, not a cost question."* So nobody owns it. X11 does now.

And the fact the audit did not have: **closing X11 does not make `total` computable on the legs D7b
is likeliest to choose.** `us_2y` and `us_10y` declare `financing` and `roll` unmodelled at D2 under
DD12, which is a statement about the re-expression rather than about this repository's data. Whoever
closes X11 must say whether the stopping rule runs on `total` at all, or whether `cost_per_dv01` —
the spread term alone — is the permanent denominator and §3.2's four terms are a description of a
model that never runs whole.

**Cost of deferring:** unchanged and low for Paper 1, because DD86 fixes the denominator on the term
that exists. What must not happen is D7b reporting a leg count from a one-term cost model **without
the `MORE_LEGS` bias beside it**, which DD84 now makes mechanical.

---

## 5. Finding 3 — one register, one table

`CARRIED_ITEMS.md` §4 carried a second table, *"What is owed today, and by whom"*, listing five
items. It was stale three ways: it still showed X4 and X5 as owed after D7a discharged them, it
never gained X11, and it asserted *"None of the five has landed, so **C76 passes vacuously today**"*
after D7a landed and C76 fired for real — which D7a's own §6.5 records.

It was invisible to the bar that reads §1 because its rows have **three** cells and `_ITEM_ROW`
requires four. A register with two tables has a table that is wrong, and the second one drifts
because nothing reads it.

> **DD88.** §4 states the *form* of an answer and points at §1 for the *content*. There is one
> register and it is §1. C88 holds it: every line in the document beginning `| **X` must parse as a
> well-formed §1 row, so a second item table cannot grow back.

This is C34's lesson pointed at a register instead of a claim: the thing that keeps two documents
agreeing is not care, it is that one of them is not a copy.

---

## 6. Finding 4 — `net_dv01` may not be a divisor, and a bar says so

DD81 is recorded in a docstring, and `gross_dv01`'s docstring carries the three measured failures.
C82 checks the identity `gross == |net|` on the two outrights — and its own docstring names the
hazard: *"On an outright with one component the two readings coincide, which is why the trap is
quiet."* Nothing scanned the tree.

So a D7b unit test dividing by `net_dv01` on `us_10y` would pass, and the defect would surface on
the breakeven at 133.89× or on a working spread at a division by zero.

> **DD89.** `net_dv01` may not appear as the right operand of a division anywhere in `src/`. C89
> walks every module's AST for a `BinOp(Div)` whose divisor is an attribute named `net_dv01`, with
> a mutation proving the walk catches one. Precedent is `test_deskcraft_boundary.py`'s `os`-attribute
> scan, and the rule is the standing one: a boundary hit is fixed by renaming or restructuring, never
> by exempting.

The property `LegSensitivity.net_dv01` stays. It is the right number for the question D4 asks of it
— *what does a parallel move leave on a leg that declares neutrality* — and 370.67/bp on the
breakeven is a finding, not a bug. What is banned is one use of it.

---

## 7. Finding 6 — §1's evaluation count, and §6 gains two bullets

§1 says greedy *"touches **≈1,800 evaluations** across six rounds — a number that goes into D15's
Deflated Sharpe trial count and can be defended."* Six rounds over ~300 structures, minus the legs
already taken, is **1,785**. But H9 predicts the rule stops at three or four legs, which is
**897 or 1,194**. The commissioning text's headline number assumes exactly the thing the hypothesis
one section down predicts against.

It is low severity because D7b's row already has the count *reported* rather than assumed, so the
real number lands in the diff either way. It is worth an annotation because it is the third instance
of the same pattern and because a trial count that reaches D15 should not have two values in the
plan.

§6 gains the two bullets that would have caught findings 1 and 5:

- **A cost hurdle set after seeing which structures it stops on.** Fixed at `COST_HURDLE = 1.0` in
  `costs.py` by `AMENDMENT_A2` §2, before D7b's pre-commit exists, and not a free parameter:
  any other value is a rung of §3.5's ladder.
- **A bias register that is complete in one direction.** Every row of `BIASES` ran `FEWER_LEGS`
  while the model's largest effect — three absent cost terms — ran `MORE_LEGS` and was not a row.
  A register whose scope silently excludes the biggest term reads as a bound and is not one.

---

## 8. Finding 7 — C10's message, on the package before the third one

C10 has now fired on two consecutive packages — D6's `ViewDirection`, D7a's `BiasDirection` — and
both were answered the same way, by renaming to `...Sense` beside D4's `RateSense`. The convention
has been paid for twice and appears in nobody's error message. The assertion now names it, and names
the standing rule, so the third package meets the answer at the same moment it meets the refusal.

Not a new bar and not a new id: the check is unchanged and the mutation is unchanged. Only what it
says when it fires.

---

## 9. Finding 8 — the annotations, held against the module that produced them

D7a annotated four of §3's five subsections, and the annotations carry numbers: `$15,625.00`
against `$23,437.50`, a ratio of `4/3` on the butterfly, `13.289%`, `0.1800` of a rung. Those
numbers came out of `costs.py`. Nothing held the two together, so the module could move and the
commissioning document's correction would quietly become wrong — which is the failure mode the
annotations exist to prevent, restored one level up.

> **DD90.** C90 recomputes each annotated figure from the module and asserts the build order's text
> still states it. Document and module at equality, in the shape `MODULES` and `DECLARED_OWED`
> already use here.

---

## 10. Predictions

Written before the run, in D4's broad wording rather than a narrowed one.

| | Prediction |
|---|---|
| **P1** | Exactly one existing bar turns red, and it is C81's four equalities on `BIASES`, broken by DD84's fifth row. No other bar moves |
| **P2** | The suite goes **94 → 98**: C88, C89, C90, C91 |
| **P3** | C88 turns red on the tree as it stands *before* §X11 is written and §4 is folded, naming both, and green after |
| **P4** | C89 finds **no** existing `net_dv01` division in `src/` — the ban is prospective, and its only live evidence is its mutation |
| **P5** | `compounded_bias()`'s unquantified count goes 2 → 3 and its product is **unchanged**, because the new row has no magnitude |
| **P6** | `ENGINE_IMPORT_ROOTS` and the environment census (C72's 18, C73's 7) do not move: no new module, no new conditional bar |
| **P7** | `ruff` 0 findings, `lint-imports` 2 kept 0 broken, `meip` and `curvecast` untouched, `reference.py` untouched for the fourth package running |

Scored in §12.

---

## 11. What this amendment could still get wrong

- **`COST_HURDLE = 1.0` is an argument, not a measurement.** The algebra is exact and C91 pins it,
  but the claim that a hurdle is *redundant with* the ladder rests on the ladder being run and
  reported. If D7b reports one cell, the hurdle silently becomes a free parameter again and nothing
  here catches it. The bar that would catch it belongs in D7b's pre-commit, and this document
  cannot write it.
- **The equivalence in §2.3 is true of a one-term cost model.** When X11 closes it stops being true,
  and the person closing X11 has to notice. §4 says so; nothing enforces it.
- **DD84 records a direction and no magnitude, which is honest and unsatisfying.** Two opposing
  unquantified biases mean the net sign is unknown, and "unknown" is a worse headline than the lower
  bound D7a's §6.6 offered. It is the true one.
- **C90 pins numbers that appear in prose.** A bar asserting a substring of a document is brittle in
  the ordinary way — reformatting the table breaks it. That is the intended cost: the annotation is
  load-bearing, and a reformatting that drops the figure should be noticed.
- **Six of the seven findings were cheap because §1 has never been implemented.** That is also the
  reason to distrust the sweep: §2, §4 and §5 of the build order have not been implemented either,
  and this amendment read §1 and §3 closely because D7a had just been burned by §3. The next
  package to implement §1 or §2 should expect to find something, and should not read this document
  as evidence that the commissioning text has now been checked.

---

## 12. Result

**CLOSED 2026-09-15**, the same day the audit was run. Bars **C88–C91**, decisions **DD84–DD90**.
Suite **94 → 98**, green in 7.65s. Clean-machine acceptance **91 passed, 7 skipped** — the *7* is the
stable number and it did not move. `ruff` 0 findings on the pinned selection; `lint-imports` **2 kept,
0 broken** (20 files, 55 dependencies). `meip` and `curvecast` untouched. `reference.py` untouched,
for the fourth package running. **Next free: C92 / DD91.**

### 12.1 The scorecard

| | Prediction | Verdict |
|---|---|---|
| **P1** | Exactly one existing bar turns red, C81's equalities on `BIASES` | **HELD, and measured** |
| **P2** | The suite goes 94 → 98 | HELD exactly |
| **P3** | C88 turns red on the pre-edit register, naming both defects | **HELD, and measured** |
| **P4** | C89 finds no existing `net_dv01` division in `src/` | HELD — the ban is prospective |
| **P5** | `compounded_bias()` goes 2 → 3 unquantified, product unchanged | HELD — `(1.001232, 3)` |
| **P6** | Census unmoved: C72's 18, C73's 7, `ENGINE_IMPORT_ROOTS` | HELD |
| **P7** | Gates clean, siblings and `reference.py` untouched | HELD |

Seven of seven, which is itself worth distrusting and is addressed in §12.5.

### 12.2 P1 and P3, scored by experiment rather than asserted

Both were run rather than reasoned about, in the shape D7a used for its own P4.

**P1.** The pre-edit test file was checked out beside the new module —
`git show f9f46fa:tests/test_costs.py` — and run against it:

    tests/test_costs_p1probe.py::test_every_bias_carries_a_direction... FAILED
    assert len(BIASES) == 4
    AssertionError: assert 5 == 4

One bar, one line, and nothing else moved. The probe file was deleted after the run. That is the
equality census doing exactly the work it was written for: DD84's fifth row could not be added
quietly, and four assertions had to be edited in the same commit as the module.

**P3.** C88's two helpers were run against the register as `f9f46fa` left it:

    declared, has no body : ['X11']
    item-shaped lines     : 16 against 11 declared
      NOT a well-formed §1 row: | **X2** | D8, D17 | either lands |
      NOT a well-formed §1 row: | **X3** | D9, D7b | either lands |
      NOT a well-formed §1 row: | **X4** | D7a | D7a lands |
      NOT a well-formed §1 row: | **X5** | D7a | D7a lands |
      NOT a well-formed §1 row: | **X6** | D8 | D8 lands |

Both defects, named, by the bar, on the tree that had them — **sixteen** item-shaped lines where
eleven items are declared. That is the only kind of evidence a bar written after the fact can offer,
and it is better than the assertion it replaces.

### 12.3 What the measuring changed, and it reversed one finding

The audit delivered seven findings and expected to implement seven fixes. Two of them came back
different, and one came back **backwards**:

- **The hurdle was never a number to choose.** The audit's framing was *"pick a defensible value and
  fix it"*. The algebra says there is nothing to pick: `h` multiplies one side of a single
  inequality, and §3.5 already sweeps the other side by 0.5/1/2/4. Fixing `COST_HURDLE = 1.0` is
  therefore not a modest choice made early — it is the removal of a parameter, and it is a stronger
  answer than any number would have been. The same argument then disposed of the holding period
  without a second decision, and the disposal was **measured**, not argued: `m × cost(1.0)` equals
  `cost(1.0/m)` to the last bit at all four rungs.
- **Finding 5 reversed.** The audit said H9's PASS was *"expected by construction"* because every
  bias in the register runs `FEWER_LEGS`. That is true of the register and false of the model: the
  largest effect in the cost model is that **three of four terms are absent**, which understates
  cost and gives **more** legs, and it was not in the register at all. The register held
  *calibration* biases; the omission is a *coverage* bias, and the scope difference is why nobody
  noticed a register that was complete in one direction. The honest statement is not that the leg
  count is a lower bound — it is that **the sign of the net bias is unknown**, which is worse news
  and the true one.

Both are instances of the standing lesson: a register whose rows all agree is not evidence, and
what it excludes is where to look.

### 12.4 X11 gained a third question and lost an assumption

Writing the body found something the audit's two-way split did not have. **Closing X11 does not make
the cost model whole on the legs D7b will reach first.** `us_2y` and `us_10y` declare `financing` and
`roll` unmodelled at **D2, under DD12** — their own re-expression's refusal, not a data gap — so
grading H.15 and FR 2004B leaves two of four terms absent on both. And the financing term has **no
parameter at all**: grading a series does not make it computable, because `annualised_cost` has
nowhere to put one.

So the question underneath X11 is not *"when do we get the data"*. It is **whether §3.2's four-term
model ever runs whole, or whether `cost_per_dv01` is the permanent denominator**. DD86 fixes the
denominator on the term that exists so D7b is not blocked; X11 now owns the larger question, and the
`HURDLE_HOLDING_YEARS` identity is an obligation it inherits, because financing is constant in the
holding period and its arrival splits one axis into two.

### 12.5 What this amendment still gets wrong

- **Seven of seven predictions held, and that is a weak run, not a strong one.** Every prediction
  here was about *this* rider's own mechanics — how many bars, which one reddens, whether a count
  moves. None of them could have been surprised by the subject matter, because the subject matter is
  a document. D7a's P1 missed on something outside its own module, and that miss was worth more than
  these seven holds.
- **The hurdle is fixed and unenforced at the point that matters.** C91 pins the value and the
  identity. Nothing makes D7b *report the ladder*, and if D7b reports one cell the hurdle is a free
  parameter again under a different name. That bar belongs in D7b's pre-commit and this document
  cannot write it — which is the same structural gap §11 predicted and did not close.
- **C90 pins prose.** It asserts recomputed figures appear in a markdown document, with blockquote
  markers stripped and whitespace collapsed. Rewrapping survives; rewording does not. That is
  intended, and it will annoy someone.
- **§1 was read closely because §3 had just burned a package.** §2, §4 and §5 of the build order
  have still not been implemented by anything. This sweep is not evidence that the commissioning
  text has been checked — it is evidence that the two sections anyone looked hard at both contained
  a number that did not exist.
