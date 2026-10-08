# Rider — one irreversible surface, two clocks, and the order things are written in

*2026-09-23. Narrows **X13** and **X14**, carries **DD133–DD135**, adds bars **C119–C121**. Adds no
package, fetches nothing, reads nothing dated after `DEV_END`. The budget stands at 21.*

*Raised by the owner against a health read of the whole repository, which put the two items side by
side and asked for both to be accounted for before anything touches the out-of-sample record.*

**No item closes here, and that is the correct outcome.** A discharge is owed at landing (DD31,
C76) and neither D12 nor D15 has landed. What this document does instead is the thing that is
actually available today: it makes both defects **unreachable** rather than merely owned, by fixing
in advance the two decisions that were going to be taken by whoever happened to be at the keyboard
on the day the fixture arrived. X20 is the precedent and C118 is its shape — a decision may be
taken in a document while the item stays open, and a bar refuses the half-state in between.

---

## 0. Measured before decided

| # | Measured | Value |
|---|---|---|
| 1 | Packages that read the out-of-sample record | **4** — D12, D14, D15, D22 |
| 2 | Of those, pre-commits on disk today | **0 of 4** |
| 3 | Committed fixtures carrying a row dated after `DEV_END` | **0** |
| 4 | Maximum date in the committed daily panel | **2014-12-31** — exactly `DEV_END` |
| 5 | Bars holding the out-of-sample surface before this document | **3** — C96, C97, C98 |
| 6 | — of those, bars that require a *person* to assent before the trigger is pulled | **0** |
| 7 | Acceptable answers `X14` enumerates for D15 | **3** |
| 8 | — of the three, how many cost sample / how many cost evidence | **1 / 1** |
| 9 | Sessions the out-of-sample record is estimated to carry | **≈ 2,870** |
| 10 | X13's cost of deferring, today / at the first read | **zero / unbounded** |
| 11 | X14's cost of deferring, today / when D15's pre-commit is written | **zero / total** |
| 12 | Packages landed | **9 of 21** |
| 13 | Suite before this document | **126 passed** |
| 14 | Next free ids | **C122 / DD136 / X26** |

**Rows 10 and 11 are why this document exists and why it exists now.** Both costs are zero today
and both become unpayable at a moment that has not happened yet — and rows 2 and 3 say that neither
moment has happened. Every earlier week of this project, acting on these two items would have been
premature. This is the last week in which it is possible.

**Row 6 is the defect nobody had named.** C97 asserts the trigger has not been pulled, so the day
it is pulled it is *"pulled by a red bar and a deliberate edit"*. That is a good tripwire and it is
not a gate: a red bar is an argument with a test, and a deliberate edit is available to anyone who
finds the test inconvenient. Nothing in the repository required the **owner** to be the one who
decided.

---

## 1. The decisions, in three lines

> **DD133.** The first read of a post-`DEV_END` row is the owner's to authorise, in writing, in a
> file that does not exist yet. Until it exists, no fixture may carry such a row and no module may
> name one. **C119.**
>
> **DD134.** The four packages that read one irreversible surface are pre-registered in **one**
> document, before the first read, not in four documents in sequence. **C120.** *(amended 2026-09-26
> by DD199, `PRECOMMIT_deskcraft_d21_hedge_backtest.md` §2: D21 reads the surface too and had no
> pre-commit when this was written. It registers in its own declared document before the first read,
> so the order this decision protects holds; the authorisation names five readers and both documents.
> C191.)*
>
> **DD135.** D15's dependence on D14 is expressed as a **rule evaluated afterwards**, never as a
> **value chosen afterwards**, and every D15 choice D14's output could inform is enumerated and
> frozen before D14 runs. **C121.**

---

## 2. X13 — the tripwire had no owner on it

X13's own body states the asymmetry exactly: *"zero today and unbounded at the moment of the first
read"*. DD37 takes effect at deskcraft's first row dated after `DEV_END` and forecloses curvecast's
remaining look budget for any curvecast hypothesis about a series in this source register over
2015 → present, and *"what a person has read cannot be unread."*

C97 holds that the trigger is unpulled. What it cannot hold is **who pulls it**. The bar reads the
tree; the tree does not record consent. So the sequence C97 permits today is: a fixture lands, a bar
goes red, someone edits the bar's expectation because the fixture is obviously meant to be there,
and a look budget in another repository is spent by a commit whose message is about a test.

**DD133 puts a person in that loop.** `docs/OWNER_AUTHORISATION_the_first_oos_read.md` must exist,
and must carry the assent sentence, before a post-DEV row may be committed or named. The file is
deliberately *absent* from this commit: this document may not grant the authorisation it specifies,
because a document that both writes the gate and walks through it is not a gate.

**What the assent must say**, and why each clause is there:

| Clause | Why |
|---|---|
| Names **DD37** and states the foreclosure is in curvecast's ledger and irreversible | So the assent cannot be given by someone who has not been told what it costs |
| Names **all four** reading packages | So it is one authorisation for one surface, not four granted separately — which is DD134's subject |
| Carries a **date** | So C119 can check it is not post-dated, and so the ledger entry next door can be dated against it |
| States that the **joint pre-commit exists** | So the authorisation cannot precede the registration, which is the ordering DD134 and DD135 both rest on |

**What DD133 is not.** It is not a second opinion on whether the read should happen; X13 already
settles that (*"all four packages are core and all four need the panel — so the only question was
ever when"*). It is a requirement that the *when* is chosen by the person who owns the budget being
spent, on a day they picked, rather than inherited from the order in which files arrived.

---

## 3. X14 — the defect is in the writing order, not in the reading order

X14: D14 and D15 score the same eleven years, D14 runs first, so *"D15's sample is out-of-sample for
the model and in-sample for the analyst, and no amount of pre-registration by D15 changes what its
author has already read."*

That sentence is exactly right, and it carries a presupposition worth reading twice: **"has already
read."** It is true of a D15 pre-commit written after D14 runs. It is vacuous for one written
before. X14's three acceptable answers all assume the writing order is fixed and try to repair the
damage downstream — split the sample, restrict the statistic, or bound the exposure. None of them
questions the assumption that produced the damage.

**So there is a fourth answer, and it is strictly stronger than the three.**

> **Invert the writing order without inverting the running order.** D14 still runs first, because
> D15 needs a risk model that has been validated. But D15's specification is committed to git
> **before D14's first result exists**, so there is nothing carried forward to fit to — not bounded,
> not restricted, *absent*. And git records the order, so the claim is checkable rather than a
> statement about somebody's memory.

| Answer | Costs sample | Costs evidence | Removes the exposure | Checkable |
|---|---|---|---|---|
| Split the window | **yes** — ~5 years each, against a generator that stops at 0–2 legs | no | yes | yes |
| Restrict D15's statistic | no | **yes** — the interesting comparisons are the ones D14 touches | partly | weakly |
| Accept and bound | no | **yes** — D15's verdict is scored as the weaker evidence it then is | no, by construction | no |
| **Invert the writing order** | **no** | **no** | **yes** | **yes — git ancestry** |

### 3.1 The objection that makes it real

The fourth answer is only available if D15's pre-commit *can* be written without D14's result. The
honest objection is that it cannot: D15 needs a covariance to size with, and which covariance is
defensible is precisely what D14 reports.

**The device that dissolves this is already this repository's own.** DD98 fixed `OOS_END` without
choosing it, by stating a *rule* that returns exactly one answer — *the last complete calendar year
at the date of specification*. The same move works here:

> D15 does not name a covariance. It names **"whichever variant D14 ranks first on Fissler–Ziegel
> loss under Diebold–Mariano, ties broken by the pre-stated order"** — a function of D14's output,
> fixed before the output exists.

A rule evaluated afterwards is not a choice made afterwards. That is **DD135**, and it generalises:
every D15 parameter D14's output could inform must be, in the joint pre-commit, either a
**constant** or a **rule with one answer**. A third category — a value to be decided when we see —
is the defect, and C121 refuses a pre-commit that leaves one.

### 3.2 What the fourth answer does not claim

It does not claim D15's author is uninformed. They have read A5, A7, H9's result and every landed
package, and they should have. X14 is not about general knowledge; it is about **D14's output
specifically**, and that object does not exist. The fix is exact because the defect was exact.

It also does not repeal the three. A joint pre-commit may take the fourth answer *and* restrict the
statistic, and should say so. What it may not do is take none of them, which is what the register
calls silence and permits today.

---

## 4. Why both items get one instrument

X13 and X14 were raised by different documents, owned by different packages, and read as unrelated:
one is about a look budget next door, the other about an analyst's memory. **They have the same
fix**, and noticing that is most of this document's content.

Both are defects of **sequence around a single shared surface**. X13 says four packages read it and
the first read is irreversible. X14 says four packages read it in an order, and the order leaks. A
joint pre-registration — one document, four packages, committed before the first read — is
simultaneously the thing that makes the read deliberate (X13) and the thing that removes the
carried-forward knowledge (X14). Two riders would have written the same requirement twice and let
it drift, which is DD107's subject.

**DD134** therefore commissions one document, `PRECOMMIT_deskcraft_d12_d14_d15_d22_*.md`, and
**C120** refuses a lone pre-commit for any of the four. That refusal is the load-bearing half: the
natural failure mode is not skipping the joint document, it is writing D12's pre-commit first
because D12 runs first, and discovering at D15 that the order was set four packages ago.

---

## 5. The bars

**C119 — the first out-of-sample read is the owner's, and the tree cannot take it alone.**
Green two ways: authorisation absent **and** nothing post-DEV anywhere; or authorisation present,
well-formed and dated. Red on the half-state — a post-DEV fixture, or a module naming one, while no
one has assented. *Mutation:* a synthetic post-DEV fixture is offered against an absent
authorisation, and the bar reports it.

**C120 — four readers of one surface are registered together or not at all.**
While the joint pre-commit is absent, no pre-commit naming D12, D14, D15 or D22 alone may exist;
when it is present it must name all four and cite DD133–DD135. *Mutation:* a lone D14 pre-commit is
reported.

**C121 — every D15 choice D14 could inform is a constant or a rule, never a pending decision.**
Holds the fourth answer's shape: X14's body must list **four** answers rather than three, and once
the joint pre-commit exists it must carry X14's discharge naming one of them and must leave no
deferred-decision phrasing in D15's frozen-parameter section. *Mutation:* a pending-decision phrase
is injected and the bar reports it.

All three are **conditional bars with a live branch today**: each has real work to do while the
authorisation is absent, so none is a test that only begins to exist later. X15 is the standing item
that asks for exactly this — a threshold whose attainable range is unstated is a bar that cannot
fail, and a bar that only runs after the gate opens is the same defect in time.

---

## 6. Dispositions

| Item | Status | What changed |
|---|---|---|
| **X13** | **OPEN, narrowed** — owner D12 | The trigger now needs a named authorisation, not just a red bar. C119. Discharge still owed at D12's landing |
| **X14** | **OPEN, narrowed** — owner D15 | A fourth acceptable answer is registered and is the one recommended; D15 still chooses, in writing, at its landing. C121 |

Neither closes. **C76 will still refuse to let D12 land without `**X13** — discharged:` and D15
without `**X14** — discharged:`**, and this document deliberately does not pre-empt either
sentence. What it removes is the possibility of those sentences being written by someone who has
already spent what they were supposed to be deciding about.

---

## 7. The prediction, fixed before anything is fitted

**P — the joint pre-commit will find at least one D15 parameter that cannot be written as a
constant or as a rule, and the discovery will be made while writing the document rather than while
running it.** Registered here so that if every parameter falls out cleanly, that is a result and not
a relief — and if it does not, the parameter is named before anyone knows which way it would have
gone. This is X7's shape and it is satisfiable: the subject is the *document*, not the run.

---

*Next free ids: **C122 / DD136 / X26**.*
