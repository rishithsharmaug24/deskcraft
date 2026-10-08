# D7b — the leg generator, and the parameter the stopping rule was missing

*Written 2026-09-16, at `eecacab`, after `RIDER_the_impossibility_claims_X16_does_not_cover.md`
closed. Bars fixed before the run, in the inherited discipline.*

`BUILD_ORDER_D3_D16.md` §4 commissions this package as *"exhaustive enumeration of the
~300-structure universe, then greedy addition under §1's cost-aware stopping rule. Reports the
evaluation count for D15's trial adjustment"*. It scores **H9** and owns **X3**, **X11** and
**X12**.

**What the measurement found before anything was decided: §1's rule has a free parameter nobody
named.** The hurdle compares a gain in view fidelity against a cost quoted in basis points of
yield, and that comparison is not dimensionless until somebody says how far the view moves.
`AMENDMENT_A2` §2 fixed `COST_HURDLE` and `HURDLE_HOLDING_YEARS` by showing each was a rung of a
ladder already reported — and did not notice that the same argument applies to a third quantity it
never mentioned, which is **the only one of the three that decides H9's verdict**.

---

## 0. Measured before decided

Every row below was measured against the committed panel at `2014-12-24`, the date D7a's bars
already use, before any line of `generator.py` existed.

| | Measured | Value |
|---|---|---|
| 1 | Series with a cost profile (`COST_OF`) | **17** |
| 2 | Series in the factor basis (`FACTOR_SERIES`) | **13** |
| 3 | **Both — the enumerable pool** | **11** |
| 4 | — priced with no factor direction | 6 — `DEXUSEU`, `DGS1`, `DGS2`, `DGS10`, `DGS3MO`, `DGS6MO` |
| 5 | — in the basis with no cost | 2 — `GZ_SPREAD`, `DE_ZERO_10Y` |
| 6 | Priced series with a computable modified duration | **14 of 17** |
| 7 | — the three that refuse | `DGS3MO`, `DGS6MO` (sub-annual), `DEXUSEU` (no rate sense) |
| 8 | **Candidate structures enumerated** | **231** — §4's row says *"~300"* |
| 9 | — outrights / spreads / butterflies | **11 / 55 / 165** |
| 10 | Candidates whose `cost_per_dv01` refuses | **0 of 231** |
| 11 | Distinct candidates including direction | **462** |
| 12 | Evaluations, headline cell (1× `AS_QUOTED`) | **1,380** |
| 13 | — §1 says *"≈1,800"*; `AMENDMENT_A2` §7 corrected it to | 1,785, then 897 or 1,194 |
| 14 | **Leg count at the eight pre-registered ladder cells** | **0, 1 or 2** |
| 15 | Leg count at a cost model of effectively zero | **6, and it does not rise** |
| 16 | Book cosine at 1× `AS_QUOTED` (2 legs) | **0.479700** |
| 17 | Book cosine at the ceiling (6 legs) | **0.906494** |
| 18 | `AnnualisedCost.total` computable on any candidate | **no** — financing has no parameter at all |
| 19 | Leg count at an assumed view move of 10 bp or more | **6** |
| 20 | Next free ids | **C103 / DD110** |

**Row 8 is the fourth plan number that does not survive being implemented.** §4's *"~300"* joins
§3.1's butterfly row, §3.2's annualisation and §3.3's *"both already graded"*. The count is a
function of the enumeration rule, and §1 states none; 231 is what the rule in §1.1 below produces
and it is reported rather than tuned toward 300.

**Row 14 against row 19 is this document's subject.** The same rule, on the same universe, at the
same hurdle, returns two legs or six depending on a quantity §1 never wrote down.

---

## 1. What D7b builds

`src/deskcraft/generator.py`, and four lines of `costs.py`.

### 1.1 The candidate universe, by a stated rule

A structure is a candidate if every series it names **has a cost profile and has a direction in the
factor basis**. That intersection is `CANDIDATE_SERIES`, derived from the two registers rather than
listed, and it is eleven series: `SVENY01/02/03/05/07/10/20/30` and `DFII5/10/30`.

The rule excludes six priced series because the basis cannot see them and two basis series because
nothing prices them, and — this is the part that matters — it excludes `DGS3MO` and `DGS6MO`
**without naming them**. D7a left this exact question open: *"the two front-end series D5 went and
graded have a half-spread and no computable duration, so they have no cost per risk — D7b meets
that at the denominator rather than at the data."* It is met at neither: they are not in
`FACTOR_SERIES`, so the pool rule drops them one step earlier, and a bar holds that this is the
reason rather than a coincidence.

Three families, each with the coefficients §3.1 already prices:

| family | coefficients | count |
|---|---|---|
| outright | `(+1)` | 11 |
| spread | `(+1, −1)` over unordered pairs | 55 |
| butterfly | `(+1, −2, +1)` over curve-ordered triples, body in the middle | 165 |

**231.** Direction is not enumerated into the universe — it is a property of the leg, not of the
instrument — so each candidate is evaluated `LONG` and `SHORT`, giving **462** distinct legs.

### 1.2 The stopping rule, as §1 states it and as it is implemented

| §1 | as implemented here | why |
|---|---|---|
| 1. risk budget as ES 97.5% | **gross DV01** | `AMENDMENT_A2` §2 pre-registered the substitution; D9 owns ES. Measured consequence in §2.4 |
| 2. highest fidelity first, then most improves the book | `ViewFidelity.cosine`, greedy | §1's own word. **Not** `dominant_share` — §2.2, and X3 |
| 3. clears a cost hurdle fixed in advance | `COST_HURDLE = 1.0` against `cost_per_dv01` | `AMENDMENT_A2` §2, DD85–DD87 |
| 4. stops when the next-best fails the hurdle | as written, and the empty case is an outcome | §3.5 |
| 5. leave-one-out for every surviving leg | `Selection.leave_one_out` | reported, never optional |
| 6. counterfactual if a count is forced | `Selection.counterfactual` | the price tag §1.6 asks for |

---

## 2. The parameter nobody fixed

### 2.1 The comparison is not dimensionless

`cost_per_dv01` is, in its own docstring, *"round-trip spread cost per unit of gross DV01, **in
basis points of yield**"* — it is the yield move that repays the round trip. The benefit side of
§1.3 is a gain in fidelity, which is dimensionless. **A dimensionless number cannot be compared
against a number in basis points**, and `COST_HURDLE = 1.0` does not repair that: it fixes the
ratio's threshold, not the ratio's units.

What closes the gap is a stated view magnitude. The addition enters when

```
    Δfidelity × VIEW_MOVE_BP   ≥   COST_HURDLE × cost_per_dv01
```

and both sides are then in basis points. In words: **the fidelity the leg buys must repay its round
trip within the move the view asserts.**

### 2.2 Which fidelity, and why this is X3's discharge

`ViewFidelity` carries two statistics. `dominant_share` is `|largest| / Σ|all six|` and its own
docstring since D6 says it decomposes nothing, because the six directions are not orthogonal — that
is **X3**, and `BUILD_ORDER` §2's annotation says *"D7b ranks legs by fidelity two packages before
D9 can fix the statistic."*

**D7b does not rank by that statistic.** It ranks by `cosine`, the inner product of the book's
exposure with the compiled target, both normalised. A cosine is an angle between two vectors and
claims no decomposition, so non-orthogonality of the basis does not touch it. X3's concern about
D7b is void, and **C111 holds it as a census** — no module under `src/` that orders candidates reads
`dominant_share` — rather than as a sentence, because a sentence is what X3 was worried about.

X3 stays **OPEN** for D9, whose F3 flag does want the decomposition that does not exist.

### 2.3 `VIEW_MOVE_BP` is the cost multiplier under another name

Only the quotient enters:

```
    Δfidelity × m / (multiplier × cost_per_dv01)
```

so the selection at multiplier `m` and move `1.0` is **the same function** as the selection at
multiplier `1.0` and move `1/m`. Measured at all four rungs, leg for leg:

| multiplier, move 1 bp | equivalently | legs |
|---|---|---|
| 0.5× | move **2.00** bp | 2 |
| 1.0× | move **1.00** bp | 2 |
| 2.0× | move **0.50** bp | 1 |
| 4.0× | move **0.25** bp | 0 |

Identical selections, not merely identical counts. **C107** asserts it.

So `VIEW_MOVE_BP` is fixed at **1.0**, and it is fixed the way `HURDLE_HOLDING_YEARS` was: by taking
the unit the denominator is already quoted in. `cost_per_dv01` is a number of basis points; one
basis point is its unit and not a calibration. Any other value is a rung of a ladder already
reported.

**And that is where the argument stops being reassuring.** Read as view magnitudes, §3.5's four
rungs span **2 bp down to 0.25 bp**. A macro view that yields rise is tens of basis points. The
ladder does not reach the region a reader would assume, and the leg count over that region is:

| assumed view move | 0.25 | 0.5 | 1 | 2 | 4 | 5 | 10 | 25 | 50 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|
| **legs** | 0 | 1 | **2** | **2** | 4 | 4 | **6** | 6 | 6 | 6 |

The four rungs cover the first four columns. H9's threshold is six, and six is reached in the
columns the ladder does not span.

**This is `AMENDMENT_A2` §2's own finding, one parameter over, missed by the document that made
it.** A2 wrote *"a threshold picked by the package it scores is not a prediction"* about
`COST_HURDLE`, fixed it before D7b's pre-commit existed, and left beside it an unnamed quantity that
moves the same verdict further. It is named here, before the run, by the package it would otherwise
advantage — which is the only order in which naming it counts for anything. **DD110.**

### 2.4 The budget cancels, and what that costs

Each selected leg is sized to carry equal gross DV01. The scale then cancels out of the cosine
entirely, so **the leg count does not depend on the level of the risk budget** — "risk budget in,
leg count out" is true of the budget's *composition* and not of its size.

That is a consequence of the substitution in §1.2 row 1, and it is worth stating plainly: **gross
DV01 is strictly additive, so it prices no diversification.** Expected shortfall is sub-additive and
would. The greedy still adds legs — because cosine is normalised by the L2 norm of the net exposure,
so a leg earns its place by *cancelling off-thesis exposure*, which is F3's subject — but the
mechanism is geometric rather than statistical until D9 lands. Pre-registered here: **when D9's
component ES replaces gross DV01, the leg count is expected to rise, and the numbers below are a
lower bound on the count rather than an estimate of it.**

---

## 3. What the measurements found

### 3.1 The count flips between rungs, which is §3.5's own stated trigger

`costs.py`'s `COST_MULTIPLIERS` docstring: *"A flip between 1× and 2× means the honest headline is
that the result is a statement about costs rather than about structure."*

| convention | mult | legs | cosine | evals | selection |
|---|---|---|---|---|---|
| `AS_QUOTED` | 0.5× | 2 | 0.479700 | 1,380 | SHORT `SVENY30`; SHORT `SVENY10/SVENY30` |
| `AS_QUOTED` | **1.0×** | **2** | **0.479700** | **1,380** | SHORT `SVENY30`; SHORT `SVENY10/SVENY30` |
| `AS_QUOTED` | **2.0×** | **1** | 0.294118 | 922 | SHORT `SVENY30` |
| `AS_QUOTED` | 4.0× | 0 | — | 462 | *(empty)* |
| `PAR_PROXY` | 0.5× | 2 | 0.577770 | 1,380 | SHORT `SVENY10`; SHORT `SVENY07/10/20` |
| `PAR_PROXY` | 1.0× | 1 | 0.384280 | 922 | SHORT `SVENY10` |
| `PAR_PROXY` | 2.0× | 1 | 0.384280 | 922 | SHORT `SVENY10` |
| `PAR_PROXY` | 4.0× | 0 | — | 462 | *(empty)* |

**The flip fires, between 1× and 2×, on the axis §3.5 named.** So the headline this package
publishes is the one §3.5 pre-wrote: **the leg count here is a statement about costs, not about
structure.**

**And the convention axis changes the composition, not only the count.** X5 closed on the ground
that the convention effect is 1.132891× — *0.1800 of a rung* — and therefore needed its own axis
because no widening of the first could separate it. That understated it. At 0.5× the two conventions
select **completely disjoint books**: `AS_QUOTED` takes the thirty-year and a 10s30s spread,
`PAR_PROXY` takes the ten-year and a 7s10s20s butterfly. A ratio of 1.13 on a cost changes *which
structures win*, because the ranking is by a quotient and the conventions do not scale all eleven
durations by the same factor. X5's number was right and its consequence was understated.

### 3.2 Six legs is a ceiling set by geometry, not by cost

Run the same rule with cost effectively zero (move 10⁸ bp):

```
  move      1e+01 bp ->  6 legs, cosine 0.906494022, next-best gain ratio -0.507
  move      1e+02 bp ->  6 legs, cosine 0.906494022, next-best gain ratio -5.07
  move      1e+04 bp ->  6 legs, cosine 0.906494022, next-best gain ratio -507
  move      1e+08 bp ->  6 legs, cosine 0.906494022, next-best gain ratio -5.07e+06
```

The count stops rising at six and the next-best gain is **negative**: no remaining candidate of the
231 raises the book's cosine at all. The greedy runs out of fidelity, not out of money.

**This bounds X11 in a direction nothing else could.** `BIASES["absent_cost_terms"]` is
`UNDERSTATES_COST` / `MORE_LEGS` and unquantified — the register's only unquantified row — and X11's
body says *"no sentence anywhere may describe the count as a bound in either direction."* It can
now, on one side: **grading every absent cost term can only raise the count, and the count cannot
exceed six.** An understatement of cost is bounded above by the free-cost answer, and the free-cost
answer is measured. The other side stays unbounded and unowned, exactly as X11 says.

### 3.3 The evaluation count D15 is owed

Three numbers, and D7b reports all three rather than choosing for D15:

- **462** — distinct candidate legs (231 structures × 2 directions). The number of *hypotheses about
  the market* this package entertains.
- **1,380** — evaluations at the headline cell: 462 + 460 + 458, three rounds, the last of which
  refuses.
- **7,830** — evaluations summed across all eight reported cells.

**D7b's reading, stated so D15 can overturn it:** the trial count is **462**. Re-scoring the same
structure under a different cost assumption is a sensitivity report, not a new hypothesis, and the
eight cells are published together precisely so that none of them is a selected result. If D15
disagrees it should use 7,830, and the difference is a factor of 16.9 in the Deflated Sharpe
deflation.

None of the three is §1's **≈1,800**, and none is `AMENDMENT_A2` §7's corrected **897 or 1,194**.
A2's correction was arithmetic on the wrong two inputs: it assumed ~300 structures (the universe is
231) and no direction search (there is one, and it doubles the round). Right method, wrong
operands — and it is the third time a number in this plan has been corrected to a second wrong
value rather than measured.

### 3.4 An empty selection is an outcome, not a crash

At 4× on both conventions the rule returns **no legs**. `Book.legs` refuses to be empty — *"every
ratio below divides by zero on it"* — so the generator does not build one. It returns a `Selection`
with an empty tuple, the reason, and the ratio of the best refused candidate.

§1 has no floor and no non-empty guarantee, and it should not be given one here: a zero-leg answer
is a true statement — *at a quarter of a basis point of assumed move, no structure in the universe
repays its spread* — and forcing a one-leg book to avoid an awkward output would be the engine
inventing a position. **What must not happen is a zero being read as a failure of the rule**, so
`Selection.refused` carries the best ratio and the candidate that produced it.

### 3.5 The generator declares the neutrality its coefficients actually have

D4 measured that `US_BREAKEVEN_5Y` declares `Neutrality.DV01` and leaves **370.67 per basis point**
on $50m, and left the re-expression to D7b: *"whether this leg is better matched on duration than on
coefficients is a decision for D7b, the leg generator, which has a reason to make it."*

**The decision is: unit coefficients, and `Neutrality.CASH`, which is true.** A `(+1, −1)` pair on
one notional buys and sells equal cash by construction; that is what cash-neutral means and it needs
no measurement to be true. It is not DV01-neutral and the generator does not say it is.

The generator's own enumeration contains the reference leg, and reproduces D4's number exactly:

```
  SPR_SVENY05_DFII5   components {'SVENY05': 25000.0, 'DFII5': -24629.33}
                      net DV01  370.67   gross  49629.33   residual/gross 0.7469%
```

**The reference book is deliberately not edited**, for D4's and D5's reason — an annotated wrong
declaration is a better record than a quiet fix. What changes is that D7b no longer *inherits* the
error: nothing it generates declares a neutrality it has not got, and **C109** holds that as a
property of the enumeration rather than of this paragraph.

**What this does not do.** DV01-matching remains unavailable as a *declared* neutrality, because
`book.py`'s DD17 invariant reads *"coefficients sum to zero"* as *"hedged against something"*. A
genuinely DV01-matched pair — coefficients `(+1, −1.0151)` — does **not** sum to zero and must
therefore declare `Neutrality.NONE`, which the constructor's own message calls *"an outright
position wearing two names"*. So the object that is DV01-neutral is forbidden from saying so, and
the object that says so is not. That is a defect in D2's invariant, it is not D7b's to change, and
it is opened as **X17** below rather than described and dropped.

---

## 4. H9, scored

> **H9 — for the reference view, the cost-aware stopping rule terminates below six legs.**
> **Predicted: PASS**, at three or four.

**Verdict: PASS.** Eight of eight pre-registered cells terminate at 0, 1 or 2 legs.

**The predicted value is wrong, on the low side, at every cell.** Three or four was reasoned from
*"three factors explain 97.9% of curve variance, so by the fourth leg there is little independent
territory left"*. The territory argument is sound and lands at exactly the right place — the free-cost
ceiling is six, and the fourth leg is where the marginal gains become small — but the cost hurdle
bites two or three legs earlier than §1 expected.

**X15's discharge, and it makes the PASS weaker than it reads.** The attainable range of the leg
count over the eight pre-registered cells is **{0, 1, 2}**; the threshold is `< 6`; the fraction of
that range admitted is **3 of 3, 100%**. *Within the grid the rule runs on, H9 could not have
failed.* Six is attainable — measured, at an assumed view move of 10 bp — but no cell of the ladder
reaches it, because the ladder's rungs are view magnitudes between 0.25 and 2 basis points.

This is the second member of the class `AMENDMENT_A3` §14.4 opened as X15, and the first found by
the package being scored rather than by an audit of it. It differs from H8's in one way that
matters: **H8's threshold could not fail for an algebraic reason** (ENB ≤ leg count) and was
withdrawn; H9's can fail, and does at 10 bp, so the claim is falsifiable and the defect is in the
**grid**, not in the claim. H9 is therefore scored rather than withdrawn, and the grid's span is
reported beside the verdict so the margin cannot be quoted without it.

**`AMENDMENT_A3` §6's annotation is honoured and does not change the verdict.** It notes that
*"six" is `REFERENCE_BOOK`'s count and two of those legs cannot be priced*, so the priceable
comparand is `US_CASH_BOOK`'s **four**. At `< 4` the verdict is still PASS at all eight cells — 0,
1 and 2 are below four — and still FAIL at a 4 bp assumed move. The annotation tightens the bar
without moving the answer, which is what it predicted it would do.

`registers.CLAIMS` gains `verdict=PASS` on H9 in this commit, which is what C34 requires of a
landing scorer.

---

## 5. The carried items

### **X3** — discharged: D7b does not rank by `dominant_share`

§2.2. The ordering statistic is `cosine`, which claims no decomposition and is unaffected by the
basis's non-orthogonality. The pre-registered re-score X3 asked for is not owed, because there is
nothing ranked by the broken statistic to re-score. **C111** holds the census so this is a property
of the tree rather than of this sentence. X3 stays **OPEN** for D9 and F3.

### **X11** — carried to D8: the code half closes here, the data half is D8's

**What closes here.** X11's own §0 row says *"`annualised_cost` has **no parameter** a financing
input could be passed to, so that term is a code gap first."* Literally true — `financing` was
refused unconditionally, with no argument that could ever supply it. This package adds
`costs.Financing`, mirroring `MarketDepth` and `Maintenance`: no default, no table, stated by the
caller. The financing term is now absent because **this repository has not graded a rate**, and no
longer because the function cannot accept one. **C110.**

**And the question underneath the item is answered.** X11 asks: *"does the stopping rule ever run on
`total`, or is `cost_per_dv01` the permanent denominator?"* Measured: **`total` refuses on all 231
candidates, and would still refuse if FR 2004B and a financing rate were both graded tomorrow**,
because `us_2y` and `us_10y` decline `financing` and `roll` at D2 under DD12. For D7b,
`cost_per_dv01` is the permanent denominator, and §3.2's four terms describe a model that does not
run whole in this repository. That is recorded rather than worked around. §3.2 above adds the bound
this buys: the `MORE_LEGS` bias is now bounded above at six.

**What is carried, and why D8.** The remaining half is three questions and none is D7b's: grading an
ADV source is an extraction, and extractions run in curvecast; substituting `DFF` for the `SOFR`
that §3.3 names is a source decision; and **FR 2004B is weekly, feeding a term reported per year**,
which X11 itself calls *"X2's class of question"*. X2 is owned by **D8**, which already owes a
frequency policy for a monthly credit series. Putting the weekly-to-annual question in the same
package as the monthly-to-daily one is the only placement that lets one policy answer both.

### **X12** — discharged: the ladder is reported, never at one rung

`selection_ladder` returns **all eight cells** and `Selection` carries the cell it was computed at,
so a count cannot be quoted without its rung. §3.1's table is the published form and it is published
whole. `COST_MULTIPLIERS` is read **only** as a comprehension iterable in `generator.py`, which is
what **C102** — written yesterday against the claim that no bar could tell sweeping from picking —
measures by AST. `generator.py` joins C102's and C92's reader censuses in this commit, both of which
are equalities, so it could not have landed silently either way.

X12's inherited obligation is also discharged: `HURDLE_HOLDING_YEARS`'s collapse onto the ladder is a
property of a one-term cost model, and **`VIEW_MOVE_BP`'s collapse is not** — §2.3's identity holds
whatever terms the cost has, because the move multiplies the benefit and ~~the multiplier multiplies
the cost. So grading X11 splits two of the three parameters back apart and leaves the third on the
ladder. Stated here so whoever closes X11 re-measures two axes and not three.~~

> **Struck and corrected 2026-09-16 by `RIDER_the_cost_multiplier_is_implemented_twice.md` (DD112),
> in place under DD103's rule.** The struck sentence is conditional on a choice this document did
> not know it was making. *"The multiplier multiplies the cost"* was true of `generator.select`,
> which applies the rung to the whole cost, and **false of `costs.cost_per_dv01`**, which applied it
> inside the spread term — and this paragraph names neither. Measured: the identity holds under the
> first reading and **fails under the second**, and the two select different books at three of
> twenty-eight swept cells once a second cost term exists. So the instruction *"re-measures two axes
> and not three"* was right for the arithmetic this package ran and wrong for the function whose
> parameter is literally called `multiplier`, which is what D8 would reach for.
>
> The scope is now fixed at **DD112** — a rung scales the **total** — so the struck instruction is
> true as written *given that decision*, and **X18** carries the re-measurement to D8. It is struck
> rather than edited because what was wrong was not the conclusion but the absence of the premise.
>
> **This is an X16 instance by the document that discharged X16**, and §5's table below is the
> reason it survived: the table enumerates *one* claim this document makes, and it makes two.

### **X7** — discharged: no prediction below has a subject this run produces

Honoured. §7 carries no prediction of a bar count stated before the bars were written — that was
`AMENDMENT_A4`'s P2 miss. The counts predicted below are of things that exist before the run: the
suite total, the census sizes, the gate outputs.

### **X15** — discharged: §4 states the range, the threshold and the fraction admitted

Range over the pre-registered grid **{0, 1, 2}**, threshold `< 6`, fraction admitted **100%**. The
discharge is what found the defect, which is the first time this item has paid for itself.

### **X16** — discharged: every inherited impossibility answered, at the point of reliance

This package **inherits** claims from `d7a`, `AMENDMENT_A2` and `CARRIED_ITEMS.md`. X16's widened
form is owed here. Three impossibility claims were relied on and each is answered rather than
repeated:

| inherited claim | disposition |
|---|---|
| `d7a` §3.5 / `Ladder` — *"no bar can stop a caller reporting one cell"* | **already refuted**, C102, yesterday. D7b is the first module the bar binds on, and it binds |
| X12 — *"no bar over a package that does not exist can catch that"* | **already refuted**, C102 |
| X11 — *"grading a source means an extraction and the extraction runs in curvecast"* | **tested, and true.** `deskcraft` has no egress by construction; there is no route by which this package could grade FR 2004B. Not an unexamined foreclosure — the boundary is the repository's first property |

And the one this document makes: **§2.4's claim that gross DV01 prices no diversification.**

> **Corrected 2026-09-16 — this document makes *two*, and the second is the one that mattered.**
> The word *"one"* is the defect: an enumeration that is not derived from anything is a census, and
> this one undercounted by exactly the claim with an operational consequence for another package
> — §5's X12 paragraph above, *"§2.3's identity holds whatever terms the cost has"*, stated as
> algebra with no experiment and no explicit *"not run"*. The experiment cost one file and refutes
> it under one of the two readings of `COST_MULTIPLIERS` then live in this tree. See
> `RIDER_the_cost_multiplier_is_implemented_twice.md` §3, and the struck paragraph above.
Experiment that would refute it: a two-leg book whose gross DV01 is less than the sum of its legs'.
`gross_dv01` is `math.fsum` over `abs(...)` per component, so it cannot be — refuted only by
changing the function, which is D9's substitution and is already pre-registered. **Stated as
algebraic rather than measured**, which X16 permits and requires the saying of.

### **X17** — carried to D9: `book.py` refuses the declaration a DV01-matched structure needs

**Raised by D7b §3.5, owned by D9.** DD17's invariant treats *coefficients summing to zero* as
*hedged against something*. A DV01-matched pair does not sum to zero and must declare
`Neutrality.NONE`; a unit-weighted pair does sum to zero and must declare a neutrality it may not
have — which is exactly the `US_BREAKEVEN_5Y` defect D4 measured at 370.67/bp, and it is structural
rather than an oversight in one instrument.

**Why D9, and not D2 or D7b.** The generator does not need it: `Neutrality.CASH` is true of every
structure it emits, so nothing it publishes is mis-declared. The first package that *needs* a
DV01-matched structure is the one that computes component risk contributions and finds a leg's risk
is not where its declaration says — **D9**, whose F1 and F2 flags read exactly that. Widening DD17
before then would be widening a guard for a caller that does not exist, which is the thing D7a's
`CostBasis` prohibition and DD74 were written to avoid.

**Cost of deferring:** low, and flat. Nothing in the tree declares a neutrality it lacks except the
one leg D4 already annotated.

---

## 6. Bars

**Ten**, `C103`–`C112`, decisions `DD110` and `DD111`. Every one carries a mutation.

> **This table said nine when it was written, and P1 is scored against the nine.** The tenth
> is `C112`, whose subject — the empty selection at 4×, reported as an outcome rather than
> forced into a one-leg book — is described in §3.4 above, written before the module existed.
> So it is not a bar chosen after seeing a result; it is a bar described and not numbered,
> and it was numbered while the tests were written. Recorded here rather than by quietly
> editing the prediction, because the count is exactly what X7 says a pre-commit must not
> predict about its own run and I predicted it anyway.

| bar | subject | mutation |
|---|---|---|
| **C103** | `CANDIDATE_SERIES` is `FACTOR_SERIES ∩ COST_OF`, an equality at 11, and the universe is 231 = 11 + 55 + 165 | a series added to either register moves the pool and the count |
| **C104** | Every candidate prices and reaches the basis; `DGS3MO`/`DGS6MO`/`DEXUSEU` are excluded **by the rule**, not by a list | force one into the pool → the enumeration refuses, naming it |
| **C105** | The ladder is eight cells and the leg count **flips** across rungs — §3.5's stated trigger, recorded as a fact about this tree | a ladder of one cell; a tree where no rung flips |
| **C106** | H9's subject: every cell below six, and the free-cost ceiling is exactly six, reached for want of fidelity | raise the move until the count touches six |
| **C107** | `VIEW_MOVE_BP` is the multiplier under another name: `(m, 1.0)` and `(1.0, 1/m)` agree **leg for leg** at all four rungs | a selection where they disagree |
| **C108** | §1.5 and §1.6: leave-one-out for every surviving leg, and the forced-count counterfactual with its price | a selection reporting a count without them |
| **C109** | Every generated relative-value structure declares `Neutrality.CASH` and has it; the D4 residual is reproduced from the generator's own enumeration | a generated structure declaring `DV01` |
| **C110** | X11's code half: `annualised_cost` accepts a `Financing` and returns that term; without one it refuses **naming X11** | the term silently zero |
| **C111** | X3: no module under `src/` that orders candidates reads `dominant_share` | a planted ranker that does |
| **C112** | An empty selection is an outcome with its refused candidate, not a crash and not a one-leg book | the non-empty cells build books, so the refusal is about emptiness |

**C102 and C92 are both equalities and both gain `deskcraft/generator.py` in this commit.** They
were written by a rider and an amendment against a package that did not exist; this is the landing
they were armed for, and the census edits are in the diff.

---

## 7. Predictions

| | Prediction |
|---|---|
| **P1** | Suite **110 → 119**. Nine bars, no sub-bars |
| **P2** | The eight ladder cells reproduce §3.1's table exactly in `src/` — same counts, same compositions, same cosines to six places |
| **P3** | `ENGINE_IMPORT_ROOTS` **does not move**. No `itertools` (index loops), no `numpy` (the arithmetic is scalar) |
| **P4** | `MODULES` gains exactly one entry; C92's and C102's censuses gain exactly one each, the same one |
| **P5** | Adding `Financing` reddens **exactly one** existing bar in `test_costs.py`, and it is an absent-terms census rather than a signature check |
| **P6** | Clean machine **103 → 112 passed**, still **7** skipped |
| **P7** | `ruff` 0; `lint-imports` 2 kept, 0 broken; 0 rows after `DEV_END` |
| **P8** | Writing H9's verdict turns nothing red — C34 is satisfied by this document landing in the same commit |
| **P9** | Opening X17 reddens **two** bars in `test_carried_items.py` — the row equality and the body equality — as `AMENDMENT_A4` §7 measured, and **C100** reddens on the tally sentence as a third |

---

## 8. What this could still get wrong

- **The enumeration rule is a choice and the count follows from it.** Curve-ordered butterflies with
  the body in the middle is one convention; wings-at-any-position would give 495. The rule is stated
  in §1.1 and its count is reported; nothing here claims 231 is *the* universe.
- **`VIEW_MOVE_BP = 1.0` is defended by a unit argument, not by a measurement.** The identity in
  §2.3 is exact, so the value is not free — but the *ladder's span* is, and §2.3 says so. A reader
  who assumes a 25 bp view gets six legs and this document does not stop them; it gives them the
  table.
- **The cosine objective is D6's statistic and inherits its sample.** The basis is fitted on DEV. X6
  — factor orientation resting on a 36.4% margin — reaches the ordering here, and it is owned by D8
  and not re-opened.
- **Equal-risk sizing is stated, not optimal.** A budget allocated to maximise aligned exposure
  would put everything in one leg, because gross DV01 is additive (§2.4). Equal risk is the
  neutral choice and it is the one that survives D9's substitution; a sizing package is D11.
- **The leg count is a lower bound in one direction and unbounded in the other**, §3.2 and X11.

---

## 9. Result

**CLOSED 2026-09-16.** Bars **C103–C112**; decisions **DD110** and **DD111**. Suite **110 → 120**,
green. Clean machine **113 passed, 7 skipped** — the *7* held. `ruff` **0** findings;
`lint-imports` **2 kept, 0 broken**. Bar ids **120 claimed over 112 numbers, no duplicates, no
gaps, C1 → C112**. **0 rows dated after `DEV_END`**, held by C97 in the green suite. **Next free:
C113 / DD112.**

**H9 is scored PASS**, the register's second verdict in twenty active claims. **X12 closed**, **X11
narrowed and carried to D8**, **X3 discharged**, **X17 opened and owned by D9**.

| | Verdict |
|---|---|
| **P1** | **MISSED.** 110 → **120**, and **ten** bars not nine — §6's note says why |
| **P2** | HELD exactly — all eight cells reproduce, compositions and cosines to six places |
| **P3** | HELD — `ENGINE_IMPORT_ROOTS` did not move. No `itertools` (index loops), no `numpy` |
| **P4** | HELD — `MODULES` +1, C92's census +1, C102's census +1, the same module in all three |
| **P5** | **MISSED**, and the miss was worth more than the prediction. §9.1 |
| **P6** | **MISSED on the count, HELD on the skips** — 103 → **113** passed, **7** skipped. P1's cause |
| **P7** | HELD — ruff 0, lint-imports 2 kept / 0 broken, 0 rows after `DEV_END` |
| **P8** | **MISSED.** Writing H9's verdict turned **C34's mutation** red. §9.2 |
| **P9** | HELD, and named all three — C88 (the body), C76 (the row and the declaration), C100 (the tally) |

**Five held, four missed.** That is the weakest prediction run of this project by a wide margin,
against 3-of-5, 7-of-8, 8-of-9, 6-of-6 and 6-of-6 in the five documents before it — and the
direction of the misses is the finding.

### 9.1 P5 missed, and found the seventh instance of prose no bar reads — the first in `tests/`

P5 predicted that adding `costs.Financing` would redden **exactly one** existing bar in
`test_costs.py`. It reddened **zero**, and zero is correct: the parameter defaults to `None` and
the default path is byte-for-byte D7a's, so every assertion about the absent terms is still true.
A prediction that a backward-compatible change breaks something was simply wrong.

**But two comments inside `C80` became false in the same move, and `C80` stayed green.**

> *"Financing is absent under every input this module accepts, on every leg. It is the term no
> caller can supply, because the missing thing is a graded series and not an argument."*

At D7a the missing thing was **both**, which is the half of X11 this package closed — so the
sentence was already describing a state one package away, and `Financing` made it plainly wrong.

> *"Built here rather than from a leg, because no leg in this repository can reach a complete set
> of four."*

A leg can, now: `C110` states all three inputs and reaches `absent == ()` on a real leg.

**This is the seventh instance of the class the tally rider opened, and the first one inside a
test file.** The six before it were all in `docs/`. A false comment inside a passing bar is the
worse place for it: a reader's whole reason for trusting a comment in a test is that the assertion
beneath it ran. Both are corrected in place — code, not a landed pre-registration, so DD103's
strike-and-annotate rule does not apply — with the date and the superseded wording kept.

**The class widens by one word.** X16 and the tally rider both scoped the problem to documents.
It is not a document problem. It is a **prose** problem, and `tests/` is full of prose that is
read as though a bar had checked it.

### 9.2 P8 missed on the distinction between a bar and its mutation

P8 predicted that writing H9's verdict would turn nothing red, because C34 requires a verdict
exactly when its scorer's document exists and both landed in one commit. **The bar's real arm did
pass, exactly as predicted.** What went red was C34's **mutation**, which asserts an exact list
against an empty docs directory:

```
E   AssertionError: ['H3: a verdict with no D6 document behind it',
                     'H9: a verdict with no D7b document behind it']
```

The mutation was written when the register had one verdict and hard-coded a list of one. It is
not wrong — it is a census, and censuses are supposed to move when their subject does — but **I
predicted about the arm and the mutation is half the bar**. Restated with the reason.

Worth keeping because of what it says about the shape of this repository: **a mutation that names
a fact outside its own subject has a shelf life** — yesterday's C100 footnote, which the previous
rider tested and called very nearly one bar. It is not one bar. C34's mutation is the second
instance in two days, it was not found by the scan that measured the first (that scan looked at
`str.replace` on document text, and this is a hard-coded list of claim ids), and it is in a
different file.

### 9.3 The misses were all about running code, which refutes the previous document's reading

`RIDER_the_impossibility_claims_X16_does_not_cover.md` §6.1 offered this, after its third 6-of-6:

> predictions about *what this repository's bars will do* keep holding, and predictions about
> *what its documents say* keep failing.

**That reading is refuted by this document.** Four predictions missed and **all four are about
what the bars would do** — a suite count, a clean-machine count, which bar an edit reddens, and
whether a verdict is free. Not one miss was about a document's prose.

The honest restatement is narrower and less comfortable: the three quiet documents were quiet
because **they changed almost nothing that runs**. This one moved 231 structures, a new module, a
new cost input, a register row and a claim verdict, and four of nine predictions failed. The
previous document's own §6.1 worried that its reading was *"worse supported"* than it looked; it
was worse supported than that.

### 9.4 What the package found that nothing predicted

- **§1's hurdle has no units**, and the parameter that supplies them was never named by the plan,
  by `AMENDMENT_A2` which fixed its two siblings, or by the three documents that read A2 after.
  It is the only one of the three that changes H9's verdict.
- **The leg count flips between 1× and 2×**, which is the pair §3.5 nominates by name. §3.5 was
  written as a precaution; it fires on the first package that runs under it.
- **The convention axis changes the composition and not only the count.** X5 closed on the ground
  that the effect is *0.1800 of a rung*, too small to find by widening the multiplier. True, and
  it understates it: at 0.5× the two conventions select **disjoint books**.
- **Six legs is a geometric ceiling**, which bounds X11's unquantified `MORE_LEGS` bias above for
  the first time — found by running the rule at a cost of zero, which nothing asked for.
- **Gross DV01 is strictly additive**, so `AMENDMENT_A2`'s substitution prices no diversification.
  The substitution was made as a change of units and it is a change of the objective's shape.

### 9.5 What this does not close

- **X11 stays OPEN**, narrowed, owned by D8. The data half is untouched and the bias is bounded on
  one side only.
- **X3 stays OPEN** for D9. D7b's discharge says the statistic is not read here, not that it works.
- **X17 is opened, not solved.** One object in the tree declares a neutrality it has not got.
- **The leg counts are a lower bound.** Under D9's expected shortfall they are expected to rise,
  pre-registered in §2.4 before D9 exists.
- **The enumeration rule is a choice**, §8. 231 is what this rule produces and is not *the*
  universe.
- **X16's discharge here is partly algebraic.** §5's claim that gross DV01 prices no
  diversification is refuted only by changing `gross_dv01`, which is D9's pre-registered
  substitution — stated as algebra rather than measured, which X16 permits and requires the
  saying of.
