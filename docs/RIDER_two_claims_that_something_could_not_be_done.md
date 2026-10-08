# Rider — two claims that something could not be done, and one of them is false

*Raised and closed 2026-09-16, against `RIDER_C73_a_bar_that_reports_without_a_verdict.md` §3 and
`RIDER_the_register_counts_itself_in_prose.md` §5.3.*

*Asked whether the things left open should be fixed now or later, the three of them were measured
instead of re-described. Two were claims that a fix was **impossible**. Neither had ever been
tested. **One of them is false, and the counterexample shipped in the same commit that made the
claim.***

*Adds no package. The budget stands at 21. No item is opened or closed.*

---

## 0. Measured before decided

| # | Measured | Value |
|---|---|---|
| 1 | What the C73 rider §3 says about its residual | *"**Not solved, and not solvable.** A genuine clean-machine breakage that coincides with an unrelated red is still reported as an echo"* |
| 2 | What C99 actually reports in exactly that state | **`broken`**, naming only the genuine break — probed 2026-09-16, one bar red only without the siblings, one bar red both ways |
| 3 | Where the counterexample already lived | **C99b's mixed case, in the same commit `d2b06a4`**: `clean_machine_verdict({"a","b"}, {"b"}) == ("broken", ("a",))`, under the comment *"The genuine one must survive the echo"* |
| 4 | The residual that is actually there | **one node id failing both ways for two different reasons** — one bar, not two |
| 5 | Why *that* one is undecidable here | `clean_machine_verdict` receives two sets of **node ids** and nothing else. A cause is not in its domain |
| 6 | Syntactic prose tallies in `docs/`, word form (*"six closed, two standing"*) | **16** |
| 7 | Same, digit form (*"2 kept, 0 broken"*, *"97 passed, 7 skipped"*) | **69** |
| 8 | Live present-tense censuses of a mutable table among those **85** | **1** — the one C100 already reads |
| 9 | Bars that read `RIDER_C73_…md` | **0**, so annotating it moves nothing |

---

## 1. The false claim

The C73 rider closed by stating its own residual, in a paragraph headed **"Not solved, and not
solvable"**. The scenario it named is a genuine clean-machine breakage *coinciding with* an
unrelated red, and its reason was that *"every failing id fails here too and C99 cannot tell
which one would also have failed for the other reason."*

**That reason is false whenever the two failures are two different bars**, which is what
"coincides with" describes. C99 does not ask whether *some* id failed both ways; it subtracts the
sets. A bar that fails without the siblings and passes with them survives any number of unrelated
reds sitting beside it.

It was not necessary to reason about this. The state was constructed — one temporary bar reading a
sibling path that `absent_machine` rebinds, plus the register's tally corrupted so C100 goes red on
both machines — and C99 was asked:

```
AssertionError: these bars pass with the sibling repositories present and fail without them, so the
suite is not green on the only machine a reviewer has: tests/test_zz_echo_probe.py::…
assert 'broken' == 'clean'
```

**One red, named, and the both-ways failure discarded as the echo it was.** The scenario the
document calls unsolvable is solved, end to end, by code in the commit that published the claim —
and **C99b already asserts it**, four lines under a comment that says so in words.

So the defect is not in the classifier. It is that **a landed pre-registration states a limit that
its own bar refutes**, and nothing reads the document. This is the sixth instance of prose given to
no bar, and the first where the prose is not *true and unguarded* but **false and unguarded**. The
five before it drifted into being wrong as the tree moved. This one was wrong on the day it landed.

**And I repeated it**, in the closing summary that prompted this rider, as a thing deliberately not
fixed. A limitation nobody measured survived into the report of what is left to do.

### 1.1 What the residual actually is

Not two bars — **one bar, failing for two reasons at once.** Then `failed_there` and `failed_here`
are the same single-element set, the subtraction is empty, and the clean-machine break hiding
inside that bar is classified as an echo.

That one is real, and it is undecidable **at this interface** rather than in principle: the
classifier is handed node ids, and two failures of one id are indistinguishable when the only thing
carried is the id. Deciding it means carrying failure *reasons*, which is a different function with
a different domain.

---

## 2. The true claim, which stays open

`RIDER_the_register_counts_itself_in_prose.md` §5.3 said the class of stale prose counts could not
be enforced *"without teaching a parser to tell a live census from a historical statement, which is
semantics, not syntax."* That claim was also made without measuring. **Measured, it survives — and
now for a stated reason rather than an asserted one.**

The syntactic form is enumerable: 16 word-form tallies and 69 digit-form, **85 in all**. Of those,
**one** is a live census of a mutable table, and it is the one C100 already reads. The rest are
quoted gate output and past-tense statements about completed acts — *"2 kept, 0 broken"*,
*"97 passed, 7 skipped"* — which cannot drift, because the run they describe is over.

So an enumeration is constructible and **is not worth constructing**. A register of 85 prose
sentences whose only purpose is to carry one live entry would need a disposition per entry, and a
register of 85 hand-classified dispositions **is itself a census that drifts**. It would build the
sixth instance deliberately, to guard against the fifth.

The discriminator really is live-versus-historical, really is semantics, and the honest disposition
is the one X15 already has. **Verdict unchanged; the evidence behind it upgraded from assertion to
measurement.**

---

## 3. What replaces it (DD108)

**The C73 rider is annotated, not rewritten**, and C101 pins the boundary.

The wrong sentence stays on the page, struck and corrected beneath, for DD103's reason: *a claim
quietly edited inside a landed pre-registration is indistinguishable from a claim that was never
made.* The record of what was believed is part of the record.

The correction alone would be worth little — it is prose, and prose is what failed six times. So
the true residual is stated where it can be checked: **it follows from the classifier's domain.**
C101 reads `clean_machine_verdict`'s signature and holds that it takes node ids and nothing else,
so "not solvable" is derived from the interface rather than asserted about the rule. If anyone ever
widens that domain to carry failure reasons, C101 goes red and the annotation must be re-read —
which is X15's shape applied to an impossibility claim, and the first time one has had an owner.

C101 also fixes the two behaviours at the boundary: different ids are separated, identical ids are
not. The first is C99b's and is cited rather than copied; the second is the residual itself.

**No carried item is opened.** The residual is not an unowned defect — it is a measured limit with
a bar on it, which is a better disposition than a register row nobody will ever act on.

---

## 4. Predictions

| | Prediction |
|---|---|
| **P1** | Suite **108 → 109** — one bar, C101, mutations inline as C88 and C100 do |
| **P2** | **No existing bar moves.** No bar reads this rider (§0 row 9), no declaration changes, no item opens or closes — so C73, C99, C99b, C76, C88 and C100 are all unmoved |
| **P3** | Clean machine **101 → 102** passed, still **7** skipped — C101 parses this repository's own source and must not enter `EXPECTED_SKIPS` |
| **P4** | C101's mutation is red on a **widened domain**: a signature carrying failure reasons is rejected by the same check that accepts today's |
| **P5** | Gates clean; `registers.py` and `src/` out of the diff; **0** post-DEV rows |

**P3 is the one most likely to be wrong**, and the record says so out loud: A3, A4 and the A4 rider
all missed the skip count, three for three, before the last two riders held it. Two holds do not
retire a three-miss record.

---

## 5. What this could still get wrong

- **C101 reads a signature, not a proof.** It holds that causes are absent from the classifier's
  domain. It cannot hold that no *other* interface could decide the residual — that would be a
  claim about every program that could be written, which is exactly the kind of claim this rider
  exists to stop making.
- **The probe ran on a temporary bar.** It was deleted, and the state it produced is not
  reproducible from the tree as committed. C99b's mixed case is the standing evidence; the probe is
  what made me stop believing the document. Both are in the record for that reason.
- **Six instances, and the instrument was never missing.** The habit under all six is stating a
  thing without measuring it, and this rider is the first to catch it in an *impossibility* claim
  rather than a count. Two such claims were checked here. **Nothing checks the next one**, and the
  reason is the same as it was in §5.3 of the last rider: the question — *what have I just asserted
  that I could have measured?* — is still asked by hand.

---

## 6. Result

**CLOSED 2026-09-16.** Bar **C101**; decision **DD108**. Suite **108 → 109**, green. Clean machine
**102 passed, 7 skipped** — the *7* held. `ruff` 0 findings; `lint-imports` **2 kept, 0 broken**
(20 files, 55 dependencies). Bar ids **109 claimed, no duplicates, no gaps, C1 → C101**.
`registers.py` and `src/` never entered the diff — the whole change is one annotation, one bar and
this document. **0 rows dated after `DEV_END`**, held by C97's `max(dates) == DEV_END`.
**Next free: C102 / DD109.**

| | Prediction | Verdict |
|---|---|---|
| **P1** | Suite 108 → 109 | HELD exactly |
| **P2** | No existing bar moves | HELD |
| **P3** | Clean machine 101 → 102 passed, still 7 skips | **HELD — third time after three misses** |
| **P4** | C101's mutation is red on a widened domain | HELD, inline |
| **P5** | Gates clean, `registers.py` and `src/` out of the diff, 0 post-DEV rows | HELD |

### 6.1 The finding was in a document, and no bar could have found it

Five of five, and **nothing unexpected went red — for the second document running.** The reading
that flatters is that the repository is in good order. The reading that is true is sharper, and it
is the reason this rider exists:

**Every one of the six instances was in prose, and the suite was green through all six.** It was
green while the register miscounted itself for four landings; it was green the whole time the C73
rider claimed a solved problem was unsolvable. A green suite is evidence about the code and it has
now been silent six times running about the documents. **"The gates say yes" answers a question
nobody asked.**

That is why the question that opened this rider — *should these be fixed now or later* — could not
be answered by running anything. It was answered by building the state the document called
impossible and asking the bar.

### 6.2 What the two claims have in common

One impossibility claim was false and one was true, and **neither had been tested when it was
written.** The false one had its counterexample in the same commit; the true one needed nine
measurements to confirm, and the confirmation changed nothing except the standing of the claim.

The pattern is not that impossibility claims are wrong. It is that they are **cheap to write and
expensive to check**, so they are the place an unmeasured assertion survives longest — a count gets
falsified by the next landing that edits the table, and *"this cannot be done"* is falsified by
nobody, because nobody tries.

### 6.3 What this does not close

The residual named in §1.1 stays, with C101 on it. The prose-count class of §2 stays, measured and
declined. And the habit under both — asserting where measuring was available — had **no owner at
all** when §5 was written, which is this rider's own defect in this rider's own subject. §7 fixes
that.

---

## 7. A second step, decided after the run above

§5's third bullet named the habit and gave it to nobody, which is the pattern this document is
about, committed inside the document about it. So it gets a row.

**This section is post-hoc and says so.** §6's predictions were scored before it was written and
are not amended — P2 correctly says no item opened during that run.

**X16, STANDING**, owed by every future pre-commit and rider: *an impossibility is stated without
the experiment that would refute it.* Discharged the way X15 is, by an obligation on the author
that is mechanical even though the test is not — name the claim, name the cheapest experiment that
would refute it, and give its result or say it was not run.

| | Prediction, before the edit |
|---|---|
| **P6** | Suite stays at **109** — a declaration and a row, no new bar |
| **P7** | Three bars move together or the suite is red: C76's row equality, C88's body equality, and **C100's tally**, which must go *two standing* → *three standing*. This is C100's first firing in anger |
| **P8** | Clean machine stays **102 passed, 7 skipped**; gates unchanged |

### 7.1 Result — P7 missed, and the miss is the finding

**X16 opened. Suite 109, green. Clean machine 102 passed, 7 skipped. `ruff` 0; `lint-imports`
2 kept, 0 broken. Next free: C102 / DD109.**

| | Verdict |
|---|---|
| **P6** | HELD — suite stayed at 109 |
| **P7** | **MISSED, in both halves** |
| **P8** | HELD |

C76 and C88 did **not** move: the row, the body and the declaration were edited together, so
neither had anything to complain about. C100 did fire — and not on its tally, which was correct
the moment the sentence was updated. **It fired on its own mutation:**

```
assert (6, 3, 7) != (6, 3, 7)
1 failed, 107 passed, 1 skipped
```

C100's first mutation appended a synthetic row using the literal id **`X16`**, chosen yesterday on
the reasoning that it did not exist. §7 gave that id to a real item nineteen hours later, so the
synthetic row collided with the real one, the count did not move, and the mutation stopped
mutating. Its second mutation quoted the tally sentence as it read yesterday morning — *"Six
closed, two standing"* — and `str.replace` on an absent pattern returns the text unchanged, so that
one was **guaranteed to break the first time C100's subject moved**, which is the only event C100
exists to notice.

**A mutation that names a fact outside its own subject has a shelf life.** Both of C100's did, and
both named facts that this very rider was about to invalidate. They are now derived — the next
free id is computed from the register, and the reworded sentence is built from the sentence that is
actually there.

**They failed loudly, which is the only reason this is a footnote and not a seventh instance.** A
mutation that silently stops mutating leaves a bar that passes while testing nothing; these went
red on the run that broke them. That is the difference between a defect and a cost.

**First unexpected red in three documents**, and it arrived the moment this document stopped
annotating prose and touched a guarded structure — which is exactly the reading §6.1 offered for
why the previous two were quiet. Eight predictions here, seven held, and the one that failed is
worth more than the seven.

**And it reddened exactly one bar.** `1 failed, 107 passed, 1 skipped` — C99 declining a verdict
rather than becoming a second red. That is the third confirmation of `d2b06a4`, and the first that
was an accident rather than a probe built to test it.
