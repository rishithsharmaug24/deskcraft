# Amendment A6 — the candidate-set rule, pre-registered

*2026-09-17. Carries **DD120** and one bar, **C116**. No package, no series added, no row of §4
moved, and no verdict changed.*

`BUILD_ORDER_D3_D16.md` §7.3 step 2 says why this is written now rather than later: **it is the only
step in the sequence that gets harder if deferred.** H3 and H9 are scored `PASS` against an
eleven-series, 231-structure universe. `AMENDMENT_A5` §0 row 13 puts twenty series at **1,350** and
thirty at **4,525**. Once a series has landed, any rule can be written to fit what landed, and two
already-scored claims would be resting on a universe chosen after the fact. A rule written before
the first addition is binding. The same rule written after it cannot be shown to be.

---

## 0. Measured before decided

| # | Measured | Value |
|---|---|---|
| 1 | Candidate series today — `FACTOR_SERIES ∩ COST_OF`, an equality held by **C103** | **11** |
| 2 | Structures they enumerate — 11 outrights + 55 spreads + 165 butterflies | **231** |
| 3 | Distinct legs, each structure evaluated `LONG` and `SHORT` | **462** |
| 4 | Structures at 20 / 30 / 49 series — `AMENDMENT_A5` §0 row 13 | **1,350 / 4,525 / 19,649** |
| 5 | Grammar terms, closed by **DD63**, not a function of data | **6** |
| 6 | — with no tradeable series behind them: `CREDIT_VS_RATES` / `CROSS_MARKET` | **0 of 1** / **1 of 2** |
| 7 | Priced series the basis cannot see — `COST_OF ∖ FACTOR_SERIES` | **6** |
| 8 | Basis series nothing prices — `FACTOR_SERIES ∖ COST_OF` | **2** |
| 9 | Daily-change variance **not** explained by the eight nominal zeros — DGS3MO / DFII5 / DEXUSEU | **0.686 / 0.570 / 0.971** |
| 10 | — the same statistic on two series that *are* the same bonds, the noise floor | **0.074 / 0.039** |
| 11 | Candidates measured against the **eleven-series pool** rather than against the eight zeros | **0** |

Rows 9 and 10 are `AMENDMENT_A5` §0 rows 7 and 8 restated, and row 4 is its row 13. **Row 11 is this
document's own finding**, and §2 is what follows from it.

---

## 1. DD120 — the rule

> **DD120 — the candidate-set rule.** A series enters `CANDIDATE_SERIES` only by clauses 1 **and** 2
> together, and an admission carries clauses 3 and 4 in the same commit. Being free is a necessary
> condition and never a sufficient one.

**Clause 1 — admission is to a slot the grammar has, not to a gap the data fills.** DD63 closed the
view grammar at six terms, and `AMENDMENT_A5` §7.2 measured that no amount of data grows it: data
changes *which terms have a tradeable series behind them*, which is reach and not vocabulary. So the
set of reasons a series may be admitted is finite and enumerable **today** — a term with no
tradeable series (`CREDIT_VS_RATES`, 0 of 1), a term with only a reachable half (`CROSS_MARKET`, 1
of 2), or a region of a curve that a fitted term does not reach. **A series that fills no such slot
is refused however free it is, and a series admitted names its slot in the diff.**

**Clause 2 — the direction is measured against the pool, not against the eight zeros.** The
admission statistic is the fraction of a candidate's daily-change variance left unexplained by a
least-squares projection on the daily changes of `CANDIDATE_SERIES` **as it stands at the time of
the test**, over `FitWindow.dev()`, on this repository's own panel. It must exceed ~~**0.25**~~.

> **AMENDED 2026-09-17 — DD122, `AMENDMENT_A7`.** Three parts of this clause did not survive being run. *(a)* **`over FitWindow.dev()` is not what it computes** — the projection needs every basis series on one row, so the window is set by the shortest member, and `DFII30` opening 2010-02-22 takes it to **1,217 of 7,044 rows, 17.3%**, all inside the zero lower bound. *(b)* **The fixed 0.25 is withdrawn** for a hurdle of 3.4× the worse same-bonds floor *on the test's own sample*: that floor reads **0.1905** there against the 0.074 quoted below, so 0.25 was **1.31×** it and not 3.4×. Today the hurdle is **0.648**. *(c)* **A share is not a scale** — a candidate must also leave a residual above one published increment and must have moved on more than 80% of the sample's days, because `DGS3MO` clears the share test at 0.959 with a residual of **one basis point** and no change at all on **49.6%** of these days. Clauses 1, 3 and 4 are untouched.

That threshold is a **choice reported rather than hidden**, in the form `AMENDMENT_A2` §2 demanded
of `COST_HURDLE`. What is measured is the floor beneath it: two series drawn from the same bonds
leave **0.074 / 0.039** unexplained (row 10), so anything near that level is one instrument counted
twice. **0.25 is 3.4× the worse floor reading.** A tighter number would be fitted to the candidates
already in view; a looser one would admit a re-span. Neither the multiple nor its roundness is a
measurement and nothing here claims otherwise.

**And the test is weak in a way worth stating rather than discovering.** Of the nine figures
`AMENDMENT_A5` §2 reports across its three ADD rows, **nine clear 0.25** — within the set measured
so far this test could not have refused anything, which is the defect X15 named in H9's grid. It is
not vacuous, because those nine were measured against a *different* basis. It is **unrun**. §2.

**Clause 3 — a scored verdict keeps the universe it was scored against, and names it.** H3 is `PASS`
at **11 candidate series / 231 structures**. H9 is `PASS` at the same universe, over 462 legs.
Neither is re-scored when the pool moves: a verdict at a different universe is a **new claim with a
new id, predicted before it runs**. This is the clause the document exists for, and the one that
becomes impossible to write honestly once a series has landed — at that point *"re-score H3"* and
*"register H3-prime"* are the same edit, chosen after seeing which way the number went. **C116**
holds it: §5's rows name a universe, and the live pool must be one that some registered claim was
scored against. Grow the pool without registering a claim against it and the suite is red.

**Clause 4 — an admission restates three counts in the same commit**: the pool, which **C103**
already forces as an equality; the structure count; and the leg count. D15's trial adjustment is a
function of the last of these — **462** today, **2,700** at twenty series — so a pool that grows
without the evaluation count moving with it silently weakens every claim scored by counting trials.
**The pool may not pass twenty series without a fresh pre-registration**, because twenty is where
`AMENDMENT_A5` §0 row 13's own table puts the surface at 5.8× today's, and the row after it at
19.6×. Twenty is a choice; the table it is read off was measured before this rule was written.

---

## 2. The statistic A5 ran is not the statistic clause 2 requires — **X24**

`AMENDMENT_A5` §0 row 7 measures unexplained daily-change variance **against the eight nominal
zeros**. Clause 2 requires the projection on `CANDIDATE_SERIES`, which is **eleven** and includes
`DFII5`, `DFII10` and `DFII30`. The two are not the same test, and the gap is not academic: row 7's
own headline figure for a TIPS real — **0.570 at DFII5** — is the unexplained share of a series that
**is already in the pool**. Measured the way clause 2 requires, DFII5 would score zero against
itself.

*(**CLOSED 2026-09-17 — `AMENDMENT_A7`.** The projection ran. **X24's premise is the mild half of what it found**: swapping the basis from the eight zeros to the eleven moves no nominal candidate by more than **0.002**, and only `DEXUSEU` at all (0.944 to 0.905). What the same run found instead is the window this clause silently computes over, and what that window does to the statistic -- DD122.)*

So **no candidate anywhere in this repository has been measured against the pool it would join**,
and the disposition table's three ADD rows rest on a looser test than the rule they will be judged
by. That is **X24**, owned by **D8** — the next core package, the one that owns the data half of X11
and would be the package actually adding a series. Closing it is one projection per candidate on a
panel already in the tree: no fetch, no egress, no budget.

---

## 3. What the rule says about `AMENDMENT_A5` §9 row 2, which it does not take

Row 2 asks whether wave 1 is bills, TIPS reals and spot FX — all three, or fewer. The rule does not
answer it, but it does price it, and the three arms turn out to be blocked on three different
things.

| Arm | Slot (clause 1) | Direction (clause 2) | What it is actually blocked on |
|---|---|---|---|
| **Bills** | The front of the nominal curve, which the GSW fit does not reach. §0 rows 6 and 9 are not in tension: eight zeros and thirty are the same six dimensions *inside* the fit, and the bill sector is outside it | **0.686 / 0.458** at 3m / 6m against the eight zeros; unrun against the pool | **The denominator, not the data.** `DGS3MO` and `DGS6MO` are *already* in `COST_OF`, and **C104** measured what happens: a structure built on either refuses by name at the duration. A bill has no computable duration, so admitting it to the basis produces a candidate the cost model cannot price. A duration convention is a decision no row of §4 owns |
| **TIPS reals** | `REAL_VS_NOMINAL` — **already filled**, by `DFII5/10/30` | **0.570 / 0.342 / 0.292** at 5 / 10 / 30y, against a basis that **excludes three series already in the pool** | **X24.** And this document registers the prediction in advance: measured against the eleven, the GSW TIPS zeros come in **below 0.25** at all three tenors, because they track the same real curve `DFII` already carries. If that is wrong the rule admits them, and the prediction is the thing that was falsifiable. *(**RUN 2026-09-17 — `AMENDMENT_A7` §5. The prediction is FALSE at its stated threshold.** The GSW TIPS zeros are not on this panel, so the nearest proxy the tree supports is leave-one-out on the three reals that are: the five-year real point reads **0.283** against the eleven and **0.387** on the longer sample, both above 0.25. The arm stays refused at **clause 1**, whose slot is filled and which does not depend on direction; the direction leg of this refusal is **withdrawn**.)* |
| **Spot FX** | **None.** `CROSS_MARKET` is a contrast between two *curves* at matched tenors; a spot rate is not a curve | **0.971** — the largest new direction measured anywhere in the sweep | **The grammar, which DD63 closed.** Admitting it means a seventh term, and §7.2 of the build order is the standing argument that data does not buy one |

**The rule refuses all three today, for three different reasons, and each reason names what would
change it.** That is not row 2's answer — the owner still decides whether to price a bill, to run
X24, or to reopen a closed grammar — but it converts the question from *which of these three do we
want* into *which of these three blockers is worth paying for*. The largest measured direction sits
behind the most expensive one, which is the shape of result this plan keeps finding.

---

## 4. What this could still get wrong

- **The threshold is a choice, and saying so does not make it a measurement.** 0.25 is defended by a
  ratio to a measured floor, in the way `VIEW_MOVE_BP` is defended by a unit argument. A reader who
  wants 0.15 gets a different pool, and this document gives them the floor rather than an argument.
- **Clause 1 is only as strong as the slot list, and the slot list is the grammar's.** §7.2 argues
  that the grammar does not grow with data. It does not argue that six terms are the *right*
  vocabulary, and if they are not, this rule enforces the wrong bound tightly.
- **Clause 2's projection is over DEV daily changes, so it is a calm-market statistic.** A series
  whose direction only separates in stress is refused by a test that never sees stress. That
  objection applies to everything in `AMENDMENT_A5` §0 rows 6–8 and is inherited here, not created.
- **C116 holds clause 3 and nothing holds clause 1.** A series admitted for no real slot, with a
  slot named falsely in a diff, passes every bar in this repository. The bar catches the count
  moving without a claim behind it; it cannot check that a stated reason is true.
- **Twenty is a ceiling with a table behind it and no measurement.** It bounds the surface; it does
  not say the surface is too big at twenty-one.

---

## 5. Result

**CLOSED 2026-09-17.** Decision **DD120**, bar **C116**, carried item **X24** opened and owned by
**D8**. No package added, no series added, no row of §4 moved, and **no verdict changed** — H3 and
H9 keep the `PASS` they were given, now with the universe they were given it at written beside them.
`AMENDMENT_A5` §9 row 3 is taken, and `BUILD_ORDER_D3_D16.md` §7.3 step 2 is done.

Suite **124 passed**. Next free ids **C117 / DD121 / X25**.
