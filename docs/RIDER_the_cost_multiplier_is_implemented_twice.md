# Rider — the cost multiplier is implemented twice, and the two agree only while one term is graded

*Written 2026-09-16, at `a4fe979`, after `PRECOMMIT_deskcraft_d7b_leg_generator.md`. Bars, decision
and register edits are named below **before** any of them exist, in the inherited discipline.*

D7b closed by finding that §1's cost hurdle had no units: it compared a dimensionless gain in view
fidelity against a cost quoted in basis points of yield, and `AMENDMENT_A2` §2 had fixed two members
of a family of three parameters and missed the third. This rider is that finding one level over, in
the parameter A2 *did* fix.

**`COST_MULTIPLIERS` has a scope nobody stated, and the scope is a free parameter of exactly the kind
A2 removed.** The multiplier is implemented twice in `src/`, the two implementations scale different
things, they are bit-identical today, and they select different books the moment a second cost term
is graded — which is X11, which is D8's.

---

## 0. Measured first, before anything was decided

Every row below was measured on the committed tree at `a4fe979`, on the D7a/D7b panel date
2014-12-24, before a line of this document's code existed.

| # | measurement | value |
|---|---|---|
| 1 | implementations of "the cost multiplier" in `src/` | **2** |
| 2 | call sites of `cost_per_dv01` in `src/` | 2 — `costs.cost_ladder`, `generator.select` |
| 3 | which of the two passes `multiplier=` | `costs.cost_ladder` **only** |
| 4 | where `costs.cost_per_dv01` applies the multiplier | inside the **spread term** |
| 5 | where `generator.select` applies it | outside, on the **whole cost** (`multiplier * cost`) |
| 6 | cells compared, `m × cost(1.0)` against `cost(m)` | **3,696** (462 legs × 2 conventions × 4 rungs) |
| 7 | cells where the two disagree **today** | **0 — bit-identical**, worst absolute difference `0.000e+00` |
| 8 | moving the multiplier outside the ratio: differing cells | **0 of 3,696**, bit-identical |
| 9 | a graded financing term per unit gross DV01, against the spread term, at 0.12% repo over one year | min **0.640**, median **1.536**, max **15.360** |
| 10 | cost ratio A/B at 4× with a second term equal to the spread | **3.380165** |
| 11 | identity `(m, 1.0) ≡ (1.0, 1/m)` under reading **A** (scales the total) | **holds** |
| 12 | the same identity under reading **B** (scales the spread) | **fails** |
| 13 | swept cells where A and B select **different books** | **3 of 28** |
| 14 | the three, as (second term ÷ spread, rung, A legs vs B legs) | (0.5, 2.0×) **0 vs 1**; (2.0, 0.5×) **2 vs 1**; (4.0, 0.5×) **1 vs 0** |
| 15 | `Ladder.convention_effect` under a second term, both readings | **1.132891 at every rung** — X5 is unaffected, and I predicted it would not be |
| 16 | claims by status: ACTIVE / ANNEXED / WITHDRAWN | **20 / 1 / 3** — so D7b's *"twenty active claims"* is exact |
| 17 | claims carrying a verdict | **2** — H3, H9 |
| 18 | carried items before this rider | 7 closed, 3 standing, **7 open** |
| 19 | impossibility-shaped claims D7b §5 lists as *made by that document* | **1** |
| 20 | impossibility-shaped claims that document actually makes | **2** |

Rows 7 and 8 are why this was invisible, and row 20 is why it was not caught by the machinery built
to catch it.

---

## 1. The two implementations

`costs.cost_per_dv01` takes a `multiplier` and applies it **inside the spread term**:

```python
spread = multiplier * 2.0 * instrument_half_spread(leg.instrument) * BASIS_POINT
return spread * leg.notional.amount / gross_dv01(leg, yields, convention)
```

`generator.select` never passes that parameter. It computes the cost once at the default and applies
the multiplier **to the whole cost**, at the point of comparison:

```python
(leg, unit_risk_exposure(leg, yields, convention), cost_per_dv01(leg, yields, convention))
...
ratio = gain * move_bp / (multiplier * cost)
```

Today `cost_per_dv01` returns one term, and its docstring says so in bold — *"**Spread only.** The
other three of §3.2's terms are absent"*. While the total **is** the spread, `m × (spread)` and
`(m × spread)` are the same number, and row 7 measures that they are the same number in the strict
sense: bit-identical at all 3,696 cells, not merely close.

So the tree contains two definitions of the ladder's own axis, and no measurement can currently tell
them apart.

## 2. What the scope decides, once a second term exists

Write the per-DV01 cost as `s + f`, the graded spread and anything graded later. The two readings are

- **A** — the multiplier scales the total: `m·(s + f)`
- **B** — the multiplier scales the spread: `m·s + f`

Under **A** the hurdle is `Δfidelity × move ≥ COST_HURDLE × m·(s+f)`, so only the quotient
`move / m` enters and `VIEW_MOVE_BP` stays a rung of a ladder already reported — which is the whole
of D7b's §2.3 and the reason `VIEW_MOVE_BP` is not a degree of freedom.

Under **B** it is `Δfidelity × move ≥ COST_HURDLE × (m·s + f)`, and dividing by `m` leaves
`f/m` behind. The move and the multiplier stop being one axis. Rows 11 and 12 measure exactly this,
and row 10 measures the size of it: at the top rung the two costs differ by a factor of **3.38**.

**And it is not only algebra.** Row 13 ran the real selector under both readings across a sweep of
second-term magnitudes, and the two select **different books at 3 of 28 cells** — differences of one
leg in the count, at 0.5× and 2.0×. The count is H9's subject. So the unstated scope is a parameter
that moves a scored claim's answer, which is precisely what `AMENDMENT_A2` §2 removed `COST_HURDLE`
for being.

## 3. The claim D7b made about this, and did not run

D7b's X12 discharge says, in full:

> X12's inherited obligation is also discharged: `HURDLE_HOLDING_YEARS`'s collapse onto the ladder is
> a property of a one-term cost model, and **`VIEW_MOVE_BP`'s collapse is not** — §2.3's identity
> holds whatever terms the cost has, because the move multiplies the benefit and the multiplier
> multiplies the cost. So grading X11 splits two of the three parameters back apart and leaves the
> third on the ladder. Stated here so whoever closes X11 re-measures two axes and not three.

Three things are wrong with this paragraph, and the third is the one that matters.

1. *"the multiplier multiplies the cost"* is **true of `generator.select` and false of
   `costs.cost_per_dv01`**, and the sentence names neither.
2. The claim *"holds whatever terms the cost has"* is therefore **conditional on a choice the
   document did not know it was making**. Measured: true under A, false under B (rows 11–12).
3. It is an **instruction to a future package** — *"re-measures two axes and not three"* — and D8 is
   the package that grades X11. A D8 that reaches for the parameter literally named `multiplier` on
   the cost function gets reading B, and must re-measure **three**.

**This is an X16 instance by the document that discharged X16.** X16 is STANDING and reads: *an
impossibility is stated without the experiment that would refute it, and nobody tries.* D7b's §5
tabled three inherited impossibility claims and then wrote *"And the one this document makes"* —
singular — naming only §2.4's gross-DV01 claim. It makes **two** (row 19 against row 20). The one it
missed is the one with an operational consequence for another package, and it was stated as algebra
with no experiment and no explicit *"not run"*, which is the disposition X16 requires when an
experiment is declined.

The experiment was cheap: it is §0's rows 11–14, and it took one file.

## 4. Why this is fixed here rather than carried whole

D7b declined to widen `book.py`'s DD17 invariant for X17 on the ground that it would be *"widening a
guard for a caller that does not exist"*. That reasoning is right and **does not apply here**, and
the difference is worth stating because it is the line this repository keeps having to draw.

X17 is a guard that would bind on a structure nothing in the tree builds. This is **two live
implementations that already disagree in principle**, one of which is called today by `cost_ladder`
and reported by D7a. Nothing hypothetical is involved: the disagreement is masked by the number of
graded terms, not by the absence of a caller.

So the scope is decided here, and the re-measurement that the decision implies is carried to the
package that grades the second term.

## 5. The decision — DD112: the multiplier scales the total cost

**`COST_MULTIPLIERS` scales the whole cost, not any one term of it.** Reading A.

The reason is §3.5's own purpose. The ladder exists so that a reported leg count can be checked
against the possibility that it is *"a statement about costs rather than about structure"*. That
question is about the cost, entire. A ladder that scales one term of four and holds three fixed
answers a different and much narrower question — *what if the spread were wrong* — which nothing
asked and which no document in this plan describes.

It is also the reading D7b actually ran, so choosing it leaves every published number unmoved.
Choosing B would silently restate H9's evidence.

**The decision is made structural rather than documented.** A docstring saying *"the multiplier
scales the total"* is a sign next to a hole — this repository's own phrase, from the rider that found
C73's real defect. `cost_per_dv01` is restructured so the multiplier is the **outermost factor of the
return value**:

```python
return multiplier * (spread * leg.notional.amount / gross_dv01(leg, yields, convention))
```

A term added inside is then scaled by construction, and a term added outside sits on the same line as
the multiplier where a reader and a diff both see it. Row 8 measures that this restructure is
**bit-identical** at all 3,696 cells, so no published figure moves and `EXPECTED_COST_PER_DV01`'s
frozen values are untouched.

## 6. Carried items

### **X18** — opened, carried to D8: the ladder axis must be re-measured when a second term is graded

DD112 fixes the scope; it does not do D8's arithmetic. When X11's data half lands and
`cost_per_dv01` returns more than the spread, the ladder's rungs change meaning: `COST_MULTIPLIERS`
will scale a total whose composition is new, and the reported cell-by-cell leg counts in D7b §3.1
are evidence about a one-term cost model only. D8 owes a re-measurement of the eight cells and a
statement of whether the count still flips between 1× and 2×.

Owned by **D8**, which already owns X11 and X2, because the obligation arrives with the graded term
and not before.

### **X16** — discharged: this document's own claims, with the experiments

X16 is owed by every rider. Two claims here are impossibility-shaped and both were run rather than
argued:

| claim this document makes | experiment, and its result |
|---|---|
| *"the two readings cannot be told apart today"* | **run.** 3,696 cells, `m × cost(1.0)` against `cost(m)`, **0 disagreements and bit-identical** — not "close", equal |
| *"the restructure moves no published number"* | **run.** the same 3,696 cells under the rearranged expression, **0 differing**. Bit-identity was not assumed from commutativity: float multiplication is commutative but not associative, so it was measured |

And one inherited claim was probed and **survived**: `Ladder.convention_effect`'s docstring says the
PAR_PROXY/AS_QUOTED ratio is *"the same ratio at every multiplier"*, which X5's closure rests on. I
expected a second cost term to break it under reading B and it does not (row 15) — every term of the
form `X / gross_dv01` carries the same convention ratio, so the quotient is unchanged whatever the
numerator is made of. **Recorded as a negative result**, which is the half of X16 that is easy to
skip.

### **X7** — discharged: no prediction below has a subject this run produces

§8 carries no prediction of a bar count, a suite total, or anything else this document chooses. D7b
predicted its own bar count and missed it, then recorded the violation; the correction is to not
predict it, so the bars are **stated as a plan in §7** and are not scored.

### **X15** — not owed: no claim is added

X15 binds every pre-commit that adds a claim to the register. This rider adds none and scores none.
H9's verdict is untouched and §8 predicts that it stays untouched, which is a different obligation
and is met by measurement.

### **X11** — carried to D8: unchanged in scope, sharpened in what it owes

X11 already carried the graded-second-term question to D8. X18 is not a second copy of it: X11 is
about *getting* the data, X18 is about what the **ladder** means once the data is there. They land
together and are stated apart because one can be answered without answering the other.

## 7. The bars this rider adds

Three, `C113`–`C115`, decision `DD112`. Each carries a mutation, in the inherited discipline.

| bar | subject | mutation |
|---|---|---|
| **C113** | the two readings agree today, as an **equality over all 3,696 cells** — so the moment `cost_per_dv01` returns a second term without the multiplication moving outside, this goes red | a second term added inside the ratio but outside the multiplier |
| **C114** | an **AST census**: `cost_per_dv01`'s return is `multiplier * <...>`, so the scope is structural and not a docstring | the multiplier moved back inside the spread term |
| **C115** | the divergence is **measured, not asserted**: under a second term the two readings select different books, at the three cells §0 row 14 names | the second term set to zero, where the two must agree again |

C113 is the load-bearing one and it is deliberately an equality rather than a ban, in C99's shape:
it refuses the **silence**, not the act. D8 is allowed to add a cost term. It is not allowed to add
one without this bar saying so.

## 8. Predictions

Scored in §10 by the run, not by re-reading.

| | prediction |
|---|---|
| **P1** | The restructure is bit-identical, so **no existing bar in `test_costs.py` reddens** — including C88's frozen `EXPECTED_COST_PER_DV01` anchor and D7a's `cost_ladder` bars |
| **P2** | Opening X18 reddens **exactly two** bars: C76's row/declaration equality and `test_carried_items.py`'s `DECLARED_OWED`. This is the established cost of opening an item, stated at `AMENDMENT_A4` §7 |
| **P3** | The §1 tally sentence must move from *seven open* to *eight open*, or **C100 reddens** — the bar the register-counts-itself rider added for exactly this |
| **P4** | Every one of D7b's eight reported cells reproduces **identically** after the restructure: same leg counts, same compositions, same cosines to six places. **H9 stays PASS** |
| **P5** | C114's AST bar **fails against the pre-restructure source** — it is a bar that would have caught this, and saying so requires running it against the old text |
| **P6** | No **third** implementation of a cost multiplier exists in `src/`: a census of every multiplication of a cost by a ladder rung finds the two in §1 and no others |
| **P7** | Clean machine stays at **7** skips; `ruff` 0; `lint-imports` 2 kept / 0 broken |
| **P8** | The generator's own bars do not redden: `generator.select` is untouched by this change, because it never passed the parameter that moves |

## 9. Caveats, before the run

- **The second cost term is synthetic.** §0 rows 9–14 model it as financing at a plausible repo
  rate and as a multiple of the spread. Nothing here grades a source, and the magnitudes are
  illustrative; what is *not* illustrative is rows 11–12, which are algebraic properties that hold
  at any nonzero second term.
- **Row 13's "3 of 28" is a property of the sweep, not a constant of nature.** A different range of
  second-term magnitudes gives a different count. The claim it supports is the qualitative one — the
  readings select different books — and that claim needs one divergent cell, not three.
- **DD112 chooses a reading; it does not validate either.** Whether a cost ladder should scale a
  total or a term is a modelling question this repository has never posed. A is chosen because it is
  what §3.5's stated purpose asks for and what D7b ran. If D8 finds a reason to prefer B, DD112 is
  the decision it must reverse in the open, and X18 is where that argument belongs.
- **This does not touch H9's grid defect.** X15's second instance stands exactly as D7b recorded it:
  the ladder's rungs are view magnitudes from 2 bp to 0.25 bp and six legs arrives at 10 bp. The
  scope decision changes nothing about that, and nothing here should be read as strengthening H9.

## 10. Result

**CLOSED 2026-09-16.** Bars **C113–C115**, decision **DD112**, carried item **X18** opened and owned
by D8. Suite **120 → 123**, green. Clean machine **116 passed, 7 skipped** — the *7* held. `ruff`
**0** findings; `lint-imports` **2 kept, 0 broken**. Bar ids **123 claimed over 115 numbers, no
duplicates, no gaps, C1 → C115**. **0 rows dated after `DEV_END`**. **Next free: C116 / DD113 /
X19.**

**No published number moved.** All eight of D7b's cells reproduce exactly — 2 / 2 / 1 / 0 under
AS_QUOTED at cosines 0.479700, 0.479700, 0.294118, and 2 / 1 / 1 / 0 under PAR_PROXY at 0.577770,
0.384280, 0.384280 — with the same compositions and the same evaluation counts (1,380 / 1,380 / 922
/ 462). **H9 stays PASS** and its grid defect stands exactly as X15 recorded it.

| | Verdict |
|---|---|
| **P1** | HELD — the restructure is bit-identical and **no existing bar reddened**, `EXPECTED_COST_PER_DV01` and D7a's `cost_ladder` bars included |
| **P2** | **MISSED.** Opening a carried item costs **three** reds, not two. §10.1 |
| **P3** | HELD exactly — the tally left at *seven* reddens `test_the_register_states_its_own_size_and_the_statement_is_true` and nothing else |
| **P4** | HELD — eight cells, identical in count, composition and cosine to six places |
| **P5** | HELD — C114 passes on the restructured source and **fails on the pre-2026-09-16 text**, which is kept verbatim in the test file so the claim can be run |
| **P6** | HELD — a census of `src/` finds the two implementations of §1 and **no third**; after DD112 they are one scope |
| **P7** | HELD — 7 skips, ruff 0, lint-imports 2 kept / 0 broken |
| **P8** | HELD — `generator.select` is untouched: it never passed the parameter that moved |

**Seven of eight held.** The miss is the useful one, again.

### 10.1 P2 missed, and the miss is the eighth instance of the class

P2 predicted that opening X18 would redden **exactly two** bars — the row equality and the body
equality — and cited `AMENDMENT_A4` §7 for the number. Scored by experiment, because the register
edit and the declaration edit landed in one commit and neither would have been exercised otherwise:
with X18's row and body present and `DECLARED_OWED` reverted, **three** bars fail, at whole-suite
scope and at module scope alike.

```
test_no_landed_package_left_a_carried_item_unanswered          the row equality
test_every_registered_item_has_a_body_and_there_is_only_one_register   the body equality
test_the_register_states_its_own_size_and_the_statement_is_true        the tally
```

**The number was stale and I restated it anyway — and D7b had already measured it correctly.** D7b's
own P9 scored *"HELD, and named all three"*. I reached past the package that had just measured it
for the older figure in `AMENDMENT_A4`, which was true when A4 landed and was made false by the
tally bar that arrived two documents later. That is the seventh instance's class in its cheapest
possible form: not a document nobody read, but a number I read and did not re-derive.

### 10.2 And A4's correction of that number is itself stale, with the total unchanged

`AMENDMENT_A4` §9.2 said **two**. `RIDER_A4_the_date_and_two_unowned_findings.md` §7.1 corrected it
to **three**, naming the third as `test_environment_census.py`'s clean-machine census C73, which
failed whenever the child suite failed.

Measured today at whole-suite scope, the answer is **still three — and both of its parts have
changed**:

- **C73 left the count.** Since `d2b06a4` it **skips** with *"no verdict"* on a red suite rather
  than failing. The probe above reports `3 failed, 119 passed, 1 skipped`, and the skip is C73.
- **The tally bar joined it**, because `DECLARED_OWED` is what C100 derives the expected tally from,
  so an undeclared item breaks the tally as well as the row.

So the correction's **total is right by coincidence and its stated reason is wrong**. That is worse
than a number that is simply out of date: a figure that still matches is a figure nobody re-runs.
Annotated in place at A4 §9.2 under DD103, struck and dated, rather than edited.

**The general shape, now seen three times in two days**: a count about *the machinery* — not about
the subject — stated in prose, true when written, falsified by a later landing, and never re-read
because nothing reads it. C100 fixed this for the register's own size by deriving it. Nothing
derives the cost of opening an item, and §10.4 says why that is left alone.

### 10.3 What the package found

- **`COST_MULTIPLIERS` had two implementations**, scaling different things, **bit-identical at all
  3,696 cells** while one term is graded. Not close — equal, which is why five documents passed
  over it.
- **The scope decides a leg count.** Under a second cost term the two readings select different
  books at three of twenty-eight swept cells, at 0.5× and 2.0×. The leg count is H9's subject, so
  an unstated scope is a free parameter attached to a scored claim — which is what `AMENDMENT_A2`
  §2 removed `COST_HURDLE` for being, and this is the fourth member of that family to turn up.
- **D7b's X12 discharge asserted the outcome and did not run it**, in a paragraph that is an
  instruction to D8. It is an **X16 violation by the document that discharged X16**, and §5's
  enumeration — *"the one this document makes"* — is how it survived: an undrived count of one,
  against two.
- **X5 was probed on the same suspicion and survived.** `Ladder.convention_effect` is stable under
  both readings at every rung: every term of the form `X / gross_dv01` carries the same convention
  ratio, so the quotient is unchanged whatever the numerator is made of. I expected it to break and
  it does not. Recorded because X16 asks for the result either way, and a negative is the half
  that gets dropped.

### 10.4 What this does not close

- **X18 is opened, not answered.** DD112 fixes what a rung means; the eight cells are still
  evidence about a one-term cost model, and the re-measurement is D8's.
- **The second cost term is synthetic throughout.** Nothing here grades a source, and §9's caveat
  stands: rows 9–14 model a term rather than measuring one.
- **DD112 chooses between two readings and validates neither.** If D8 finds a reason to prefer the
  spread-only scope, DD112 is a decision to reverse in the open, not a fact.
- **The cost of opening a carried item is still a number in prose.** It could be derived — a bar
  could revert a declaration in a child interpreter and count the reds — and it is deliberately not,
  because that bar would re-run the suite inside the suite for a fact no package depends on. It is
  recorded here, dated, with the measurement beside it, which is what X16 asks of a claim and all
  this one warrants.
- **H9's grid defect is untouched.** The ladder's rungs remain view magnitudes from 2 bp to 0.25 bp
  and six legs still arrives at 10 bp. Nothing in this rider should be read as strengthening H9.
