# Rider to A4 — the date the rule was applied on, and two findings nobody owns

*Raised 2026-09-16, against `docs/AMENDMENT_A4_the_out_of_sample_window.md`, `AMENDMENT_A3` §14.4
and `docs/CARRIED_ITEMS.md`.*

*A4 landed nine minutes into the wrong day and said so six times; and two named defects — one in A3,
one in A4's own §8 — were written into prose and given to nobody. **Neither of those is a new
discovery. Both are recorded in documents that are already committed.** What was missing is the
thing this repository has an instrument for: a row with an owner.*

*Adds no package. Fixes no result. The budget stands at 21.*

---

## 0. Measured before decided

| # | Measured | Value |
|---|---|---|
| 1 | `AMENDMENT_A4`'s stated date vs the commit that landed it | **2026-09-15** stated / **2026-09-16 09:44** committed |
| 2 | A2 and A3, same comparison | **both match** — A4 is the only one that does not |
| 3 | A4-authored date stamps carrying the wrong day | **6** — the document ×3, `window.py` ×1, the build order ×2 |
| 4 | DD98's rule applied at 2026-09-15 / at 2026-09-16 | **2025-12-31 / 2025-12-31** — identical |
| 5 | First date on which the rule would return something else | **2027-01-01** |
| 6 | Bars reading an amendment's own stated date | **0** |
| 7 | Findings named in a committed document and carried by no register row | **2** — A3 §14.4 bullet 1, A4 §8 bullet 1 |

---

## 1. The date DD98's rule was applied on, which is not the date A4 states

DD98's whole defence is that **the window was not chosen**:

> *"Chosen by a rule, not by taste: **the last complete calendar year at the date of
> specification.** Today is 2026-09-15, so the rule yields exactly one answer and there was nothing
> to pick."*

A rule with a date for an input is only as good as the date. A4 was drafted late on 2026-09-15 and
**committed at 09:44 on 2026-09-16** — the session crossed midnight between the drafting and the
close — so the document, the module comment and both build-order annotations state a day that is not
the day the pre-registration landed. **Six stamps, and A2 and A3 both match their commits**, so this
is A4's alone and not a house convention.

**The window does not move, and that is measured rather than argued.** The rule returns
**2025-12-31** at 2026-09-15 and **2025-12-31** at 2026-09-16; the first date on which it returns
anything else is **2027-01-01**. `OOS_END` is therefore invariant across the whole interval in which
this amendment could plausibly be said to have been written.

**So why correct it at all?** Because the defence is *"the rule yields exactly one answer given the
date"*, and a reader checking that sentence checks it against the date printed beside it. A
pre-registration whose stated input is wrong is weaker than one whose stated input is right, even
when the output is the same — and this project's entire method is that the inputs are checkable.

**DD103.** The stamps are corrected to **raised 2026-09-15, closed 2026-09-16**, which is what
happened. The correction is recorded here rather than made silently, because a date quietly edited
inside a landed pre-registration is indistinguishable from a date chosen after the fact — which is
the exact suspicion DD98 exists to foreclose.

**And nothing would have caught it.** Zero bars read an amendment's stated date. §4 closes that for
the one date that is load-bearing.

---

## 2. X14 — A4 §8 named a defect in the ordering of two packages and gave it to nobody

A4 §8, first bullet, in full:

> *"**D14 and D15 run on the same eleven years, and D14 goes first.** Whatever D14 reports is known
> when D15's pre-commit is written, so D15's 'out-of-sample' is out-of-sample for the *model* and
> not for the *analyst*. The look budget exists for this and this amendment does not touch it — but
> fixing the window does not fix the ordering, and nothing here should be read as though it did. **A
> holdout split would address it; inventing one is not this document's to do.**"*

Every clause of that is right, including the last. **What follows from it is a row**, and A4 did not
write one. A defect that is named, correctly reasoned about, declared out of scope and then left in
a §8 bullet is owned by nobody, and `C76` — the bar that makes a landing package answer for open
items — cannot see it. D15 can land without ever addressing it.

This is the same shape as **A2 §12.5**, which named the unenforced cost hurdle and said *"this
document cannot write it"*; A3 found that wrong and wrote C92 and X12. **A4 §9.2 criticised exactly
this habit in its own predictions and then committed it in its own §8.**

> **X14.** D14 and D15 score the same eleven years and D14 runs first, so D15's sample is
> out-of-sample for the model and not for the analyst. — owned by **D15**.

**What it does not claim.** It does not claim D15 is invalid, and it does not invent a holdout —
A4 was right that inventing one is not an amendment's job. It claims that **D15's pre-commit must
say, in advance, what it is doing about the fact that D14's result is already known** — split the
window, restrict D15 to a statistic D14 does not report, or state plainly that the exposure is
accepted and bounded. Any of the three is an answer. Silence is not, and silence is what the current
register permits.

---

## 3. X15 — A3 said the class was still open, and then the class had no row either

A3 §14.4, first bullet:

> *"**The class of defect A1 §5.1 found is still open.** C94 makes an ENB claim name its basis. No
> bar asks whether any *other* pre-registered threshold is implied by another row. H14 and H8 are
> two instances in a register of 24, both found by hand, both after the fact."*

Verified today: `C94` holds the effective-number-of-bets family and nothing else, and no row of the
carried-items register mentions the class. **Two instances found by hand in one register, an
explicit statement that nothing holds the general case, and no owner.**

The defect is worth restating precisely, because it is not "a threshold was wrong". It is that
**H8's threshold could not fail**: ENB is bounded above by the leg count, H9 predicts the stopping
rule terminates at three or four legs, so `< 3.0` covers 100% of the attainable range at three. The
bar was satisfied by every possible book except the perfectly diversified one — the outcome it was
written to detect the absence of. Neither clause is wrong on its own; the vacuity lives in the
*interaction*, mediated by a bound (`ENB ≤ n`) stated in neither row and scored by two different
packages.

> **X15.** A threshold is pre-registered without the attainable range of the quantity it cuts, so a
> bar that cannot fail is invisible until someone reads two rows together. — **STANDING**, owed by
> every pre-commit that adds a claim.

**Why STANDING and not owned by a package.** There is no general mechanical test: catching it
requires knowing each quantity's attainable range, which is semantics and not syntax. What *is*
mechanical is the obligation on the author — **state the range, then the threshold, then what
fraction of the range the threshold admits.** H8 would not have survived that sentence being
written. This is X7's shape exactly (a standing rule for every future pre-commit), and it is filed
the same way.

---

## 4. What is enforced in code

**C98** makes DD98's defence executable. It applies the rule — *last complete calendar year at the
date of specification* — to the date the amendment states, and requires the result to equal
`OOS_END`; and it requires the stated date not to lie in the future.

The bar is armed in both directions, which is the point:

* move `OOS_END` to 2026-12-31 without touching the stated date, and it reddens;
* move the stated date into a year where the rule returns something else, and it reddens.

So `OOS_END` is now held to its own stated derivation rather than to a sentence claiming one. The
rule is deliberately re-implemented in the bar rather than imported from `window.py`: a constant
checked against a function that produced it proves only that the function was run, while a constant
checked against an independent restatement of the rule proves the rule.

**What C98 cannot do** is verify that the stated date is the date the work happened — only the
commit can say that, and the commit does not exist when the bar is written. That gap is closed by
§1's correction and by nothing else, which is worth saying plainly.

---

## 5. Predictions

| | Prediction |
|---|---|
| **P1** | The suite goes 104 → 105 — **one** bar, C98, and I have counted the bars before writing this |
| **P2** | Opening **two** register items reddens the same **two** bars measured in A4 §9.2 — the row equality and the body equality — and nothing else |
| **P3** | The six date corrections redden **nothing**, because measurement 6 found no bar reads an amendment's date |
| **P4** | Clean-machine stays at **7** skips; `registers.py` stays out of the diff |
| **P5** | Gates clean; siblings untouched; **0** post-DEV rows still |

**P2 and P3 are the ones with content**, and both are cheap to score: P2 by pulling the declarations
and running the module, P3 by reverting the stamps and running the suite. **A4 §9.2's lesson was
that naming a failure mode is not a defence against it, so both are measured before this document is
closed rather than reasoned about after.**

---

## 6. What this could still get wrong

- **X14 is filed against D15 and the exposure is not only D15's.** D12, D14, D15 and D22 all read
  the same eleven years in sequence, so every package after the first inherits some version of the
  problem. X14 names the sharpest instance — two packages, same sample, adjacent — and a general
  rule about sequential reads of one sample is a bigger question than this rider should answer.
  **If D15's answer turns out to generalise, X14 is where the widening gets recorded.**
- **X15 asks for a sentence, and a sentence is not a bar.** An author who writes *"the range is
  [1, 4] and the threshold admits 100% of it"* and then registers the threshold anyway has
  satisfied X15 and learned nothing. It converts an invisible defect into a visible one, which is
  the most a standing item can do; it does not prevent it.
- **Correcting a date inside a landed pre-registration is a move that deserves suspicion**, which is
  why it is recorded here with the measurement showing the window is invariant. If the rule's output
  had moved, the honest act would have been to keep the original date and its original answer — and
  that is worth stating precisely because it did not happen here.
- **This rider fixes A4's bookkeeping and does not revisit A4's decision.** The window, the series
  list, the vintage rule and the DD37 trigger all stand exactly as written.

---

## 7. Result

**CLOSED 2026-09-16.** Bar **C98**, decision **DD103**, items **X14** and **X15**. Suite
**104 → 105**, green. Clean-machine **98 passed, 7 skipped** — the *7* held. `ruff` 0 findings;
`lint-imports` **2 kept, 0 broken**. Bar ids **105 claimed, no duplicates, no gaps, C1 → C98**.
`registers.py` never entered the diff; `meip` clean and `curvecast` HEAD unmoved at `7727ee2`;
`reference.py` untouched. **0 rows dated after `DEV_END`.** **Next free: C99 / DD104.**

| | Prediction | Verdict |
|---|---|---|
| **P1** | Suite 104 → 105, one bar, counted first | HELD exactly |
| **P2** | Opening two items reddens the **two** bars A4 §9.2 measured | **MISSED** — it reddens **three** |
| **P3** | The date corrections redden nothing | **MISSED as worded, held in substance** |
| **P4** | 7 skips; `registers.py` out of the diff | HELD |
| **P5** | Gates clean, siblings untouched, 0 post-DEV rows | HELD |

**Three of five, and P2's miss is the one worth the rider.**

### 7.1 P2: the third red is the clean-machine census, and this is the third time

Measured by pulling X14 and X15 out of `DECLARED_OWED` and `DECLARED_STANDING` and running the
**whole suite**: **three** bars fail, not two — the register-row equality (:179), the body equality
(:284), and **`test_environment_census.py::test_a_clean_machine_skips_exactly_the_declared_bars`**
(C73), which runs the suite in a child interpreter and fails whenever the child does.

**And A4 §9.2 is wrong by the same one.** Its probe was run as
`pytest -q tests/test_carried_items.py` — **module-scoped** — so it could not observe a bar in
another module and reported *"two bars fail"* as though that were the whole-suite answer. Re-run
here at full scope with only X13's declaration pulled: **three failures, the same three.** §7.3
records the correction at the source.

So the fact, now measured three separate times: **in this repository a red is never one red.** C73
re-runs everything in a child, so any failure anywhere produces at least two. A3's P1 discovered
it and called the echo *"unpredicted"*; A4 §9.2 then measured at a scope that hid it; this rider
predicted two having written the lesson into its own §5. **Three encounters, three failures to carry
it forward** — which is a fact about how I hold context between documents, not about the guard. It
is annotated onto C73 itself now, where it will be read by whoever next predicts a red.

### 7.2 P3: nothing pre-existing read the date, which was the claim worth making

Measured by reverting the six stamps and running the suite: **two** bars redden — **C98**, which is
the bar this rider added *to* read the date, and C73's echo of it. **No bar written before today
touches an amendment's stated date**, which is exactly what measurement 6 said and exactly why §1
could not have been caught by the suite.

So the substance held and the wording did not: *"redden nothing"* was written about the tree as it
stood before C98, and by the time it was scored the tree had C98 in it. **A prediction has to name
the tree it is about**, and this one did not.

### 7.3 What this corrects in A4

- **§9.2's count.** *"two bars fail"* → **three**, at whole-suite scope. The claim was true of the
  command that was run and false of the sentence it was written into.
- **Six date stamps.** Corrected to *raised 2026-09-15, closed 2026-09-16*, with DD98's rule shown
  to return **2025-12-31** at both dates, so `OOS_END` is unmoved.
- **§8 bullet 1** is now **X14**, owned by D15, instead of a bullet owned by nobody.

**What it does not touch:** the window, the series list, the vintage rule, the DD37 trigger, and
every verdict A4 recorded. This is bookkeeping on a decision that stands.

### 7.4 The pattern across A2, A3, A4 and this rider

Four documents, and the same defect in each: **something is named correctly in prose and then not
given to anyone.** A2 named the unenforced hurdle and said it could not write the bar; A3 wrote the
bar and named a class it then left unowned; A4 named an ordering defect in §8 and left it there,
while criticising exactly that habit in §9.2. This rider closes two of those and is itself only
worth having because the register — a row, an owner, a status — is the instrument prose keeps
failing to reach for.

**The predictions have now missed in the same direction four times running**: A3's P1, A4's P1 and
P2, this rider's P2 and P3. Every miss is about **the machinery I am editing** rather than about the
finance. That is the honest summary of what these four documents have established about their own
author.
