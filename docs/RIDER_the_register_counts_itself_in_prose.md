# Rider — the register states its own size in the one line nothing reads

*Raised and closed 2026-09-16, against `docs/CARRIED_ITEMS.md` §1 and the two bars that guard it.*

*Asked whether everything was addressed and closed, the four gates said yes: suite 107 green,
clean machine 100/7, `ruff` 0, `lint-imports` 2 kept 0 broken, tree clean. So the question was put
to the registers instead, and the carried-items register — the document whose entire purpose is to
guarantee that no defect is unowned — **is wrong about how many defects it is carrying.***

*Adds no package. The budget stands at 21. No item is opened or closed.*

---

## 0. Measured before decided

| # | Measured | Value |
|---|---|---|
| 1 | What §1's table says today | **6 closed, 2 standing, 7 open** |
| 2 | What the sentence directly beneath it says | *"Six closed, one standing, four open with an owner"* — **wrong in two of three**, and the same paragraph restates the open count a third time |
| 3 | Last landing at which that sentence was true | **`f9f46fa`** (D7a) |
| 4 | Landings since that edited the table and left the sentence alone | **4** — `a4cd7b5`, `49398d1`, `118259a`, `423780a`; three of the four added an open item |
| 5 | Bars that read §1's table | **2** — C76 (rows → owners → discharges) and C88 (rows ↔ bodies, one register only) |
| 6 | Bars that read the sentence that counts those rows | **0** |
| 7 | Other present-tense prose tallies of a mutable table in `docs/` | **0.** Four other word-counts exist (`A1` §"Eight items", `A3` §"Two rows", the build order's "Two rows", `RESEARCH` §"Four rows") and every one is **past tense about a completed act**, so none of them can drift |
| 8 | Whether the register's load-bearing claim is also wrong | **No.** *"No item is unowned"* still holds at fifteen items |

---

## 1. The defect

The register is guarded carefully and in the right places. `DECLARED_OWED`, `DECLARED_CLOSED` and
`DECLARED_STANDING` are equality censuses; C76 walks every row to an owner and demands a landed
package discharge it in writing; C88 demands a body under every row and refuses a second table.
Fifteen rows, fifteen bodies, three declarations, two bars.

**And then the register states its own size in a sentence, and that sentence is the one line in
the file nothing reads.** It has been wrong since `49398d1`, four landings ago.

The failure is precise, and smaller than it first looks: **the claim that matters held.** No item
was ever unowned; every one of X12, X13, X14 and X15 arrived with a row, an owner, a status and a
body, and both bars passed honestly every time. What drifted is the *census beside the census* —
the human-readable summary that a reader reaches for first and that no machine has ever checked.

**This is the fifth instance of the pattern the C73 rider named**, and the sharpest, because this
time the unread prose is *about the guarded structure it sits under*:

| | Prose that named something true and was given to no bar |
|---|---|
| A2 | *"this document cannot write it"* |
| A3 | §14.4's open class, left unowned |
| A4 | §8's ordering defect, written as a bullet where a row was needed |
| A4 rider | a warning annotated onto C73's docstring |
| **here** | **the register's own tally of itself** |

Four documents diagnosed that habit. Three of those four then edited this table and walked past
the sentence underneath it.

---

## 2. What replaces it (DD107)

**The sentence stays, and C100 reads it.**

Two fixes were available and both are worse. *Correcting the numbers* is the instrument that has
now failed five times — it would be true this afternoon and stale at D7b. *Deleting the numbers*
removes the drift by removing the information, and a register that cannot tell a reader its own
size in one line is a worse register.

So this takes C98's disposition, which is the one that worked: **re-derive the quantity from the
source and compare it to the stated words.** C100 parses §1's table, counts the three statuses,
and asserts the sentence says what the table says. The tally stops being decoration and becomes a
claim that is scored on every run.

**One number, in one place.** The same paragraph restated the open count a second time (*"the four
that remain"*), so a single edit could leave the two disagreeing. That clause loses its number and
keeps its meaning: there is now exactly one place in the register where its size is written down,
and a bar is pointed at it.

---

## 3. Predictions

| | Prediction |
|---|---|
| **P1** | Suite **107 → 108** — one bar, C100, with its mutation inline as C88 does |
| **P2** | Corrupting the tally sentence reddens **exactly 1**, not 2 |
| **P3** | Clean machine **100 → 101** passed, still **7** skipped — C100 reads a file in this repo and needs no sibling |
| **P4** | All three declarations unmoved: no item opens or closes, so `DECLARED_OWED`, `DECLARED_CLOSED` and `DECLARED_STANDING` are untouched, and C76/C88 do not move |
| **P5** | Gates clean; `registers.py` and `src/` out of the diff; **0** post-DEV rows |

**P2 is the one worth running**, and it is not really a prediction about C100. Until yesterday a
single broken bar produced *two* reds here, because C73 re-ran the whole suite in a child and
failed on its exit code. `d2b06a4` was supposed to end that. **This is the first change landed
since, so P2 is the first independent test of whether that fix actually made the red count
predictable** — and it is scored by running the probe, not by argument.

---

## 4. What this could still get wrong

- **C100 reads one sentence by pattern.** Reword the sentence and the bar goes red with a parse
  failure that looks like a defect and is not one. The failure message therefore states the form
  it needs, so the fix is obvious to whoever hits it. This is the cost of reading prose at all,
  and it is the same cost C98 accepted to read A4's date.
- **It guards this tally, not the class.** Measurement 7 says no other present-tense count of a
  mutable table exists in `docs/` today. That is a fact about today and not a guarantee, and no
  bar enforces it — writing one would mean teaching a parser to tell a live census from a
  historical statement, which is semantics, not syntax. Filed as the honest limit rather than
  papered over: **this closes an instance, and the class is X15's shape.**
- **Five instances, and the instrument was available for all five.** The register has existed
  since `740f97a`. Nothing prevented any of the four documents from adding a row or a bar; what
  was missing was the habit of asking, at the end of a landing, what in the repository now states
  something that the landing made false. That question is still asked by hand.

---

## 5. Result

**CLOSED 2026-09-16.** Bar **C100**; decision **DD107**. Suite **107 → 108**, green. Clean machine
**101 passed, 7 skipped** — the *7* held. `ruff` 0 findings; `lint-imports` **2 kept, 0 broken**.
Bar ids **108 claimed, no duplicates, no gaps, C1 → C100**. `registers.py` never entered the diff
and `src/` was untouched entirely — the whole change is two files and one new document.
**0 rows dated after `DEV_END`.** **Next free: C101 / DD108.**

| | Prediction | Verdict |
|---|---|---|
| **P1** | Suite 107 → 108 | HELD exactly |
| **P2** | Corrupting the tally reddens **exactly 1**, not 2 | **HELD — measured** |
| **P3** | Clean machine 100 → 101 passed, still 7 skips | HELD |
| **P4** | All three declarations unmoved; C76 and C88 do not move | HELD |
| **P5** | Gates clean, `registers.py` and `src/` out of the diff, 0 post-DEV rows | HELD |

### 5.1 P2, which was a claim about yesterday's rider and not about this one

```
1 failed, 106 passed, 1 skipped
FAILED tests/test_carried_items.py::test_the_register_states_its_own_size_and_the_statement_is_true
```

**One red, and C99 skipped rather than becoming a second.** Before `d2b06a4` this probe would have
returned two failures — C100 and C73's echo — and the second would have blamed two absent sibling
repositories for a wrong number in a markdown table.

That matters more than C100 does. `d2b06a4` claimed to make the red count predictable, and it
scored that claim with a probe it wrote itself, on the tree it had just changed. **This is the
first change landed since, so it is the first time the claim was tested by something that was not
trying to prove it.** It held.

### 5.2 Five of five, and what that is worth

The fifth consecutive document to score every prediction it made, and §3 said in advance why that
is the weak kind of run. **P2 is the only one of the twenty-five predictions across these five
documents that was scored against a claim made by a *different* document.** That is a better class
of evidence than the other twenty-four and it is still machinery: not one prediction in five
documents has been about the finance these packages exist to produce.

**Nothing unexpected went red**, which breaks a run of four. Two readings are available and the
honest one is the smaller: this rider changed one sentence and added one bar, and a change that
size has little surface to surprise anyone. Four documents in a row turned up a finding they did
not predict because each of them touched machinery that several bars watched at once. This one
did not, so the absence of a surprise is evidence about the size of the change and not about the
state of the repository.

### 5.3 What this does not close

The instance is closed and **the class is not.** Measurement 7 found no other present-tense count
of a mutable table in `docs/` — today. Nothing enforces that, and nothing could without teaching a
parser to tell a live census from a historical statement, which is semantics. It sits in X15's
shape: an obligation on the author, discharged by asking at the end of every landing **what in
this repository now states something this landing made false.**

That question was available for all five instances. The register has existed since `740f97a`, C76
has parsed it since `694b374`, and nothing prevented any of the four intervening documents from
adding six words to a sentence they had just made wrong. **What was missing was never the
instrument.**
