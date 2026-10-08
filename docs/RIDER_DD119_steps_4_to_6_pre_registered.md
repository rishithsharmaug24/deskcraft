# Rider — DD119 steps 4, 5 and 6, pre-registered without landing a package

*Written 2026-09-22, at `3b10d30`, after `RIDER_A5_the_six_remaining_decisions.md` cleared the
last of `AMENDMENT_A5` §9.*

`BUILD_ORDER_D3_D16.md` §7.3 sets six steps. Three have run: step 1 landed A5, step 2 produced
`AMENDMENT_A6` and then `AMENDMENT_A7`, step 3 produced `RIDER_the_vol_surface_is_licensed_not_absent.md`.
**Steps 4, 5 and 6 had not started.** This document is all three, and §0 says why it is not the
document step 4 names.

Every discharge below is written in the form D8's and D9's pre-commits will quote. Where a step
owes a **prediction**, the prediction is made here, before the run, which is the only place it is
worth anything.

---

## 0. Why this is a rider and not `PRECOMMIT_deskcraft_d8_covariance.md`

> **DD129 — a pre-commit's existence is this repository's definition of a landed package, so a
> pre-commit may not be landed ahead of its package.** DD119 steps 4 and 5 are pre-registered in
> this rider instead. When D8 and D9 land, their pre-commits carry the discharges below in the
> required form; until then the register is not told that either package exists.

**The mechanism, stated exactly.** `closed(package, docs)` is *"whether a package has landed: its
pre-commit document exists (DD31)"* — a glob for `PRECOMMIT_deskcraft_<package>_*.md`. Two bars
consume it. **C34** requires that a claim's verdict exists if and only if its scorer has closed.
**C76** requires that a landed package's pre-commit says in writing what became of every carried
item it owes.

So writing `docs/PRECOMMIT_deskcraft_d8_covariance.md` today does not *describe* a plan to build
D8 — **it asserts that D8 has been built**, to every bar that asks. No claim names D8 as its
scorer, so C34 stays green and the assertion would pass unchallenged. That is worse rather than
better: the repository would carry a false statement about its own state in the one place nothing
would contradict it, while §4's row still reads D8 as the next core package.

**And the owner's standing instruction forbids the alternative.** No part of a model scheduled for
a later segment is built ahead of its segment. D8's covariance is a later segment. Step 4 as
written therefore has no honest execution today: the pre-commit cannot land without the package,
and the package may not be built.

**What is actually owed by step 4, and what this rider delivers.** §7.1's finding is that *"there
is no separate task that folds `AMENDMENT_A5` into the plan — D8's pre-commit is the fold."* The
fold is the **content**: six discharge decisions, each taken in advance so that D8 does not decide
them while looking at its own output. That content is what makes step 4 load-bearing, and none of
it requires the file to be named `PRECOMMIT_`. It is written below, and D8's pre-commit quotes it.

**One thing is genuinely lost and it should be said.** A pre-commit fixes bars before a run. This
rider fixes **decisions and predictions** before a run; the bars that enforce them are D8's and
D9's to write, and nothing here holds them to it except C76, which fires only once those packages
land. That is a weaker guarantee than a pre-commit and it is the best available one.

---

## 1. Step 4 — D8's six discharges

DD119 orders them **X22 → X11 → X2 → X18 → X6**, X22 first because it is structural. **X25** joined
the list on 2026-09-17 and belongs immediately after X22, for the reason X25's own body gives: the
disposition `VIXCLS` should carry does not exist until X22 is closed, so the two are one edit.

### 1.1 X22 — a `readable` predicate, and no sixth `Licence` member

> **`**X22** -- discharged:`** `Source` gains a `readable` predicate expressing DD118's middle
> disposition, and a **separate** field for the derivation condition. `Licence` does not grow a
> sixth member.

X22 offers two routes and names a third possibility — that the three dispositions collapse to two.
They do not collapse: DD118's middle band is exactly the band `AMENDMENT_A7` ran in, and a rule
with a live middle band needs a predicate for it.

**The tempting fix is the wrong one, and this is the part worth pre-registering.** The obvious move
is a sixth `Licence` value for *modification not permitted*, slotted between `CITATION_REQUIRED`
and `PRE_APPROVAL_REQUIRED`. **It would corrupt the ordering.** `Licence` is an `IntEnum` whose
order is load-bearing — PUBLIC_DOMAIN 0, CITATION_REQUIRED 1, PRE_APPROVAL_REQUIRED 2,
REDISTRIBUTION_PROHIBITED 3, UNMEASURED 4 — and it orders one thing: **permission to
redistribute**. The ESCB policy is *broader* than `CITATION_REQUIRED` on redistribution and
*narrower* on derivation, which is X22's own observation. A condition that is looser on the ordered
axis and tighter on an unordered one is **not a point on the order**. Inserting it makes every
`>=` comparison in the tree mean something different depending on which row it reaches, and those
comparisons are how DD118 is enforced.

So: **two axes, named separately.** `Licence` keeps redistribution and keeps its five members.
Derivation becomes its own field with its own small vocabulary, defaulting to nothing — the
`MarketDepth` and `Financing` discipline, for the reason `Licence`'s own docstring gives, that *"a
default here would hand the widest permission to the least evidence."* `readable` then answers
DD118's middle band from both fields rather than from the enum alone.

**What it costs to get wrong in the other direction.** Today nothing in the tree stops a package
reading a `PRE_APPROVAL_REQUIRED` row, because `committable` answers a different question. DD118 is
prose, and this register's whole history is prose beside a guarded structure drifting.

### 1.2 X25 — re-grade `VIXCLS` from the originator, and restate the fallback's premise

> **`**X25** -- discharged:`** `VIXCLS` is re-graded `REDISTRIBUTION_PROHIBITED` on Cboe's own
> terms, the `notice` field records that the previous grade was the distributor's description of
> its own arrangement, and the `VIX_History.csv` fallback is withdrawn with its premise stated.

No fetch, no new series, no budget. The grade moves one step stricter — reproduction, distribution
and derivative works all require prior written consent — and the fallback was chosen on the absence
of inline terms on a page that links to binding ones.

**The general defect is the one to write down, not the row.** `fred_tag` and `notice` are both
statements *about* a licence made by somebody other than the licensor, and the type has no field
for the licensor's words. `AMENDMENT_A5`'s method is *read the words, not the tag*, and this is
that method's own file failing its own rule one level up. The X22 edit is where a field for the
licensor's words belongs, which is why these two discharge together.

### 1.3 X11 — the data half closes by decision, not by fetch

> **`**X11** -- discharged:`** The impact term takes a **caller-stated `MarketDepth` with its basis
> named** (DD128). FR 2004B is not fetched, not pinned and not committed. The financing term stays
> absent, and `DFF` is recorded as the substitution `sources.py` would grade if the term were ever
> wanted — not grading `DFF` under §3.3's SOFR sentence.

DD128 already took the route choice, so this discharge mostly records consequences.

**Three consequences, and the third is the useful one.**

1. **`total` stays refusing, and that is now a measured property rather than a gap.** D7b measured
   it across all 231 structures: `total` refuses on every one and would still refuse if FR 2004B
   and a financing rate were both graded tomorrow, because `us_2y` and `us_10y` decline `financing`
   and `roll` at D2 under DD12. `cost_per_dv01` is the permanent denominator for the stopping rule.
2. **`BIASES["absent_cost_terms"]` keeps its unquantified row and its one-sided bound.** Grading
   every absent term can only raise the leg count, and the count cannot pass six — geometric, and
   no cost model moves it. The other direction stays unbounded, and no sentence may call the count
   a bound.
3. **DD128 dissolves X11's third question rather than answering it.** X11 asks whether a weekly
   series may drive an annual number. A caller-stated depth is not a series and has no frequency,
   so **the weekly-to-annual question does not arise** on the route taken. It would return
   immediately on the pinned-fixture route, which is one more reason that route is not taken. What
   survives into §1.4 is X2's monthly-to-daily question only.

### 1.4 X2 — the frequency policy

> **DD130 — one frequency per covariance; a series is never resampled upward into a faster
> covariance.** A `FitWindow` fit at daily frequency admits daily series only. A grammar term whose
> only lawful series is monthly is fitted in a **monthly companion covariance** at the same window,
> and a view mixing the two reports both fits rather than one blended number. **Forward-filling or
> interpolating a monthly series into a daily covariance is refused by name.**
>
> **`**X2** -- discharged:`** the policy above, stated before D8 fits anything, covering
> `CREDIT_VS_RATES`'s move to monthly under DD124.

**The refusal is the decision, and it is refused on this repository's own measurement rather than
on taste.** Forward-fill a monthly series onto a daily grid and its daily changes are zero on
roughly **95%** of days. **DD122 part 3 refuses a candidate that fails to move on more than 20% of
its sample's days**, because a series that does not move cannot be told from publication
resolution, and the whole of `AMENDMENT_A7` is the demonstration of what happens when that goes
unchecked: `DGS3MO` read 0.959 of unexplained variance at 49.6% stalled, and the figure was
rounding. **A forward-filled monthly credit series would be four times deader than the deadest
series this repository has refused**, and it would enter not as a candidate but as a fitted input.
Refusing it at D8 and admitting it at DD122 would be the same statistic judged by two standards in
two files.

**Why not fit everything monthly instead.** That is the honest alternative and it is available as a
stated robustness variant, not as the primary: DEV holds 7,044 daily rows and roughly 324 months,
and an eleven-series covariance on 324 observations is estimable but thin — which is the condition
Ledoit–Wolf exists for, and D8's row already carries Ledoit–Wolf as a robustness variant. So the
monthly companion is not a new mechanism; it is the mechanism D8 was already building, pointed at a
second frequency.

**What this costs.** A view that mixes a daily term and a monthly one gets two numbers and no
single risk figure. That is a real loss of convenience and it is the correct loss: the alternative
is one number whose covariance is partly manufactured, and nothing downstream could tell which part.

**And it settles D17's half of X2 by implication rather than by decision.** X2's second question —
if credit ever enters through Moody's, the panel row is restricted — is untouched here. Under
DD118 those rows are readable and not committable, which is curvecast's WP-L1 pattern, and D17
inherits it. X2 is **discharged for D8 and carried, unchanged, for D17.**

### 1.5 X18 — what a rung means once the cost has more than one term

> **`**X18** -- discharged:`** the re-measurement X18 owes is **not owed on the route DD128 takes**,
> and the reason is recorded rather than the measurement skipped.

X18 asks D8 to re-measure D7b's eight reported cells *"once X11's data half lands and
`cost_per_dv01` returns more than a spread"*, and to say whether the leg count still flips between
1× and 2×.

**X11's data half lands as a decision that adds no term.** A caller-stated `MarketDepth` makes the
impact term computable *when a caller supplies one*; it grades nothing and adds no column. The
stopping rule runs on `cost_per_dv01`, which is the spread term, and §1.3 item 1 measured that this
is permanent for the stopping rule. **So `cost_per_dv01` still returns one term after D8, and
D7b's eight cells are unmoved.**

**What is owed instead, and D8 owes it in writing.** X18's dependency is now conditional and must be
restated rather than closed silently: *if any later package makes `cost_per_dv01` return more than
the spread term, the eight cells are re-measured before any count from them is quoted again.*
X18 measured what is at stake on a synthetic second term — the two readings select different books
at **three of twenty-eight** swept cells, differences of one leg, which is H9's subject, at 0.5×
and 2.0×. **C113 and C114 already hold the arithmetic**; what C76 needs is the sentence.

This is a discharge and not a carry, deliberately. The item asked a question about a state of the
world; the state did not arrive; recording that it did not arrive, with the trigger that would
bring it back, is an answer. Carrying it to a package with no more reason to reach it than D8 had
would be moving a debt to look diligent.

### 1.6 X6 — the orientation prediction, pre-registered before anything is fitted

> **`**X6** -- discharged:`** the three orientation statistics are run across every window D8 fits,
> each sign's stability recorded, and the prediction below is scored as written.

X6's whole value is that the prediction is made first. It is made here, at `3b10d30`, with nothing
fitted and nothing looked at beyond what D6 already published.

**What is known.** On DEV 1990–2014 all three components were already oriented semantically, and
the agreement in PC2 is thin: `PC2 at SVENY01` is −0.423283, `PC2 at SVENY30` is +0.577280, a
long-to-front magnitude ratio of **1.3638**. curvecast's rule signs the largest-magnitude element
positive. Had the front carried the larger magnitude, `+PC2` would silently have meant a
**flattening**, and every view compiled afterwards would have inherited it.

> **P — pre-registered 2026-09-22, for D8 to score.**
>
> **(a) PC1's orientation is stable in every window D8 fits.** A level component's loadings are
> the same sign across the curve by construction; there is no margin to lose.
>
> **(b) PC2's orientation flips in at least one window.** The flip condition X6 names is a
> front-end-volatile sample, and a crisis-window covariance is exactly that — D8's row commissions
> crisis windows by name. A 36.4% margin is not a large thing to overturn when the front end is
> the part of the curve the crisis moved.
>
> **(c) PC3 is not predicted, and the absence of a prediction is deliberate.** Nothing published
> states PC3's margin, so a prediction here would be a guess dressed as a hypothesis. D8 records
> the margin and the stability; the prediction column reads *"none offered"*, which is an outcome
> this repository prefers to a number nobody could have justified.

**What each outcome means, stated now so neither can be read as confirmation later.** If (b) holds,
**orientation is a property of a sample and not of the factors**, and every document that describes
the basis as oriented acquires a window qualifier — including D6's row. If (b) fails and every sign
is stable across every window, then the DEV orientation is a stronger fact than D6 claimed for it,
and **X6 closes having found the opposite of what it feared**, which is the same shape X24 closed
in and is worth exactly as much.

**What must not happen:** fitting the windows, seeing the signs, and then writing the prediction.
That is why this paragraph is dated eight days before D8 is scheduled to exist.

---

## 2. Step 5 — D9's three

DD119 says step 5 splits if the owner pulls X17 forward. **DD125 says no**, so it does not split
and all three are D9's, in one package, in the order below.

### 2.1 X17 — unchanged, and the reason is now on the record

> **`**X17** -- discharged:`** DD17 is widened at D9 and not before. The item's own body decided
> this and **DD125** took it: the first caller needing a DV01-matched structure is D9, the cost of
> deferring is low and flat, one annotated object carries the narrowness, and **C109** prevents a
> second.

Recorded here only so that D9's pre-commit has a sentence to quote and C76 has an answer. Nothing
about the item moved.

### 2.2 X19 — the refusal that does not fire, and the margin it is eating

> **`**X19** -- discharged:`** `generator.select` gains a refusal for a **half-reachable** factor,
> in the shape `views.fidelity` already uses for an unreachable one (DD65), and every
> `CROSS_MARKET` fidelity number published before it is re-stated as a number about the legs that
> actually existed.

This is the binding half of `AMENDMENT_A5` §9 row 4 and DD124 says so explicitly. The cost of
deferring is **not** flat, which is what separates it from X17.

**The exact damage.** A `CROSS_MARKET` view returns a single 10-year US leg at cosine **0.707** —
one of two series — and `book()` reports *"That is a statement about costs at this cell and not a
failure of the rule."* That sentence is true of an empty selection caused by costs and false of one
caused by missing data, **and the caller cannot tell which they have.** Until the refusal fires,
every fidelity number computed for `CROSS_MARKET` is a number about `LEVEL`, whose Gram overlap
with it is **+0.2717** — and **H3's PASS rests on a 4.991% margin** between `LEVEL` and
`REAL_VS_NOMINAL`, with `CROSS_MARKET` 10.756% behind. A statistic that silently substitutes the
leading term for the trailing one is operating inside that margin.

**D9's pre-commit owes a prediction here too**, and it is not offered in this rider: whether any
published number moves when the refusal lands is a question about D9's own output, and this
document has no basis to guess it. What is pre-registered is that the question is **asked in the
pre-commit and answered in the row**, rather than discovered afterwards.

### 2.3 X3 — the re-scoring, and why the leg set should not move

> **`**X3** -- discharged:`** D9 builds the corrected statistic for both flags, re-scores D7b's leg
> ordering under it, and reports whether the surviving leg set changed. The prediction is below.

D7b already pre-registered the re-scoring; what D9 owes is the statistic and the comparison. X3 was
widened by `AMENDMENT_A3` §7 (DD96) from F4 alone to F3 as well — F4 wants a partial contribution,
a conditional correlation, which is a different object; **F3 wants exactly the decomposition that
does not exist**, and §2 calls F3 the important one.

> **P — pre-registered 2026-09-22, for D9 to score.** **The surviving leg set does not change**, at
> the headline cell or at any rung of §3.5's ladder.
>
> The reason is structural rather than optimistic: **D7b orders by `cosine`, which claims no
> decomposition**, and C111 holds that the statistic X3 is about is never read on that path. A
> corrected `dominant_share` cannot move an ordering that never consulted the uncorrected one. If
> the set *does* move, then C111 is not holding what it is believed to hold, and that is a finding
> about a bar rather than about a leg.
>
> **Where the correction does land: F3's fidelity-versus-risk split**, which is where §2 said the
> important flag lives and where the three overlapping directions — `LEVEL·REAL_VS_NOMINAL`
> +0.4434, `LEVEL·CROSS_MARKET` +0.2717, `CURVATURE·CROSS_MARKET` −0.3005 — are double-counted
> today. The three carry **83.43%** of the book's absolute loading and sit within 11% of each
> other, so the correction is not a rounding adjustment to that split.

**What must not happen, and D6 already refused it once:** retuning `dominant_share` now, which is
rewriting a measure after seeing what it measured — D4 §5's prohibition.

---

## 3. Step 6 — the declines

Step 6 needs no build. It needs each decline written **with the measurement behind it**, which is
X16's standing demand. All three decisions are now taken; what remains is the writing, and it
belongs to the packages named.

### 3.1 X20 — DEC-2's cross-market work, declined (D16)

**The decision is DD126** and it is taken: the budget is twenty-one one-in-one-out, nothing has
been removed to pay for a foreign leg, and a deferral that never executes is a decline.

**The measurement that travels with it** is `AMENDMENT_A5` §3's: the ESCB re-use policy covers the
German curve provided the source is quoted and the statistics are not modified; Japan MoF's JGB
file is PDL 1.0, modifiable, from **1974-09-24**; `DE_ZERO_10Y` grades `CITATION_REQUIRED` with a
no-modification condition the `Licence` enum has no term for — which is §1.1's subject, so the
decline and the type fix are the same finding at two levels.

**And the decline must say what it is not.** It is **not** a licence decline: DD118 lifted that, and
A5 §3's recommendation is that the yen leg goes first on history and on derivation rights. It is a
**budget** decline. A reader who is told the leg was unavailable has been told something false.

**X20 stays OPEN until the code stops making the promise**, and **C118** now refuses the half-state
where the item is closed because the decision was taken. Six sites — `costs.py:323`,
`factors.py:107`, `reference.py:27` and `:247`, `sources.py:315` and `:319` — plus one landed
pre-commit.

### 3.2 X21 — Paper 2's commodity arm, declined (D17)

**The decision is DD127.** The measurement: the EIA states NYMEX WTI prices after **2024-04-05** are
unavailable; the out-of-sample window is 2015-01-01 → 2025-12-31 (DD98); the route covers **nine of
eleven** years and stops **twenty months** short.

**The bound travels with it and is not optional.** A5 §0 row 1 records that recall is unmeasured.
Nobody has established that no free, public-domain, window-covering WTI settlement series exists —
only that the one found stops in April 2024. **The decline says that in those words**, because a
decline that overstates its reach is the sentence a later reader will cite.

**And it reopens a struck claim rather than restoring it.** Build order §0 item 6 withdrew the
blanket futures decline for energy on this route. With the route truncated, the withdrawal is
narrower than it reads: three of its four halves hold and the coverage half does not. D17 writes
that, rather than leaving §0 item 6 to be read as though nothing had happened.

### 3.3 The blanket option decline, restated with DD121's measurement (D16)

Step 6 names X23, which **closed on 2026-09-17** under DD121. The decline it was opened to make
possible is still owed, and it is D16's.

**What changed, and it is the opposite of what step 3 expected.** §7.2 item 5 said the half-decline
rested on seven inputs nobody had read a licence for, and that closing it would make the argument a
measurement *either way it came out*. It came out against: the eight vol inputs are licensed
against derivation in the originator's own words, **three of the eight are not obtainable free at
any route found**, and DD118 refuses every route.

**So the decline is now stronger and differently shaped.** It was *"pricing a vanilla needs a
surface free data does not provide."* It becomes *"free data provides no rates vol surface, and the
index surfaces that exist are licensed against the derivation that would be required."* **A licence,
not an absence** — which matters because an absence invites a search and a licence does not.
`AMENDMENT_A7`'s §7.2 annotation already records this; what D16 owes is the decline itself, with
the count of three-of-eight and the originator's words behind it.

---

## 4. What this could still get wrong

1. **DD129 solves a naming problem and not the underlying one.** DD31 defines landing by document
   existence, which was a good rule while pre-commits and packages landed together. This rider is
   the first thing that wanted to separate them, and it works around the definition rather than
   revisiting it. If a second and third want the same separation, the definition is the defect.
2. **Nothing enforces any of this until D8 and D9 land.** C76 fires on a landed package. Every
   decision here is a promise with no bar behind it, which is the guarantee §0 admits is weaker
   than a pre-commit's.
3. **DD130's monthly companion may not survive contact with a view.** A view that mixes frequencies
   gets two risk numbers, and it is possible that every interesting `CREDIT_VS_RATES` view mixes
   frequencies — in which case the policy makes the term technically fitted and practically
   unusable, and DD124's refusal to remove the word will look like bookkeeping.
4. **DD131's two-axis design is asserted, not measured.** The claim that inserting a sixth
   `Licence` member corrupts the ordering rests on reading the comparisons in the tree, not on a
   run that shows one breaking. It is the right shape for the reason given and it has not been
   demonstrated.
5. **X18 is discharged on a conditional that could quietly become true.** If a later package adds a
   second cost term without reading this paragraph, the eight cells go stale and nothing says so.
   C113 and C114 hold the arithmetic; neither holds the obligation to re-measure.
6. **X6's prediction (b) is the one most likely to be wrong for an uninteresting reason.** If D8's
   crisis windows are short, PC2 may be unstable for sample-size reasons rather than for the
   front-end-volatility reason predicted, and the prediction would be *right for the wrong cause*.
   D8 reports the window lengths beside the signs so this is separable.
7. **X3's prediction leans entirely on C111.** If C111 holds something narrower than "the statistic
   X3 is about is never read on the ordering path", the prediction is unfounded rather than merely
   wrong. D9 checks the bar before scoring the prediction.
8. **§3 writes three declines that three unlanded packages owe.** D16 and D17 are far from the
   front of the order. Pre-registering a decline that nobody writes for a year is a decline that
   drifts, and X20 and X21 stay open precisely to carry that risk visibly.

---

## 5. Result

**DD119 steps 4, 5 and 6 are pre-registered. Nine discharges and three declines are written in the
form their packages must quote, and two predictions are fixed before anything is fitted.**

- **Step 4, D8's six** — X22 (a `readable` predicate, no sixth `Licence` member, **DD131**), X25
  (re-grade `VIXCLS` from the originator), X11 (the stated depth under DD128; the weekly question
  does not arise), X2 (**DD130**, one frequency per covariance, forward-fill refused by name), X18
  (not owed on the route taken, with the trigger that would bring it back), X6 (the orientation
  prediction, made before the fit).
- **Step 5, D9's three** — X17 unchanged under DD125, X19 the refusal that is eating H3's margin,
  X3 the re-scoring with a prediction that the leg set does not move.
- **Step 6, the declines** — X20's budget decline with A5 §3's measurement, X21's coverage decline
  with its twenty months and its unmeasured recall, and the blanket option decline restated as a
  licence rather than an absence.

**No package landed, no row of §4 moved, no code was written, and the budget is unchanged.** The
register is unchanged at nine closed, three standing, thirteen open with an owner: this document
opens nothing and closes nothing, which is correct — a discharge is owed at landing, and nothing
landed.

**Next free ids: C119 / DD132 / X26.**
