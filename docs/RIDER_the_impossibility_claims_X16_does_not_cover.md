# Rider — the claims that were already on the page when the rule arrived

*Raised and closed 2026-09-16, against `RIDER_two_claims_that_something_could_not_be_done.md` §7,
`PRECOMMIT_deskcraft_d7a_cost_model.md` §3.5, and `CARRIED_ITEMS.md` X12.*

X16 landed nineteen hours ago and says an impossibility arrives with the experiment that would
refute it. It is owed by **every pre-commit and rider** — which is to say, by documents written
after it. Asked whether anything else needed addressing, the honest first move was to point the new
rule at the corpus it does not cover.

**Two more false claims. Both refuted by probes that took minutes. One of them is refuted three
paragraphs above itself, in the register that opened X16.**

---

## 0. Measured before decided

| | Measured | Value |
|---|---|---|
| 1 | Mutations declared in the suite | **22** |
| 2 | First literal scan — test strings appearing verbatim in `docs/` | **722**, useless |
| 3 | Raw `str.replace` on document text | **4 sites** |
| 4 | — of those, anchor-checked by a helper that asserts a unique match | **2** |
| 5 | — of those, derived rather than named (C100, fixed yesterday) | **1** |
| 6 | — of those, an unguarded literal quoting a document's prose | **1** (C88) |
| 7 | C88's anchor made stale, suite run | **`1 failed, 107 passed, 1 skipped`** |
| 8 | Impossibility-phrasing grep, outside the two documents about it | **11 hits** |
| 9 | — of those, a foreclosure declining a fix | **0** |
| 10 | Known instances that grep fails to find | **1 of 2** |
| 11 | Foreclosure-phrasing grep | **15 hits**, 3 new candidates |
| 12 | Candidates probed | **3** |
| 13 | — false | **2** |
| 14 | — true | **1** |
| 15 | Next free ids | **C102 / DD109** |

**Row 2 is the tally grep's mistake made again.** 722 counts `us_10y`, `Direction` and `book.py` —
symbol names that appear in documents because the documents discuss the code. Renaming any of them
reddens the bar from the code side, so none of them is the shape being looked for. Narrowed to
perturbations of document *prose*, the answer is row 3's four.

**Row 10 is the measurement that matters most in this table.** The grep in row 8 does not find
`RIDER_the_register_counts_itself_in_prose.md` §5.3 — *"without teaching a parser … semantics, not
syntax"* — which is one of the two claims already known to be of this kind. A scan that misses half
of a known sample is not a census, and nothing below is presented as one.

---

## 1. The footnote, tested

Yesterday's rider called C100's failure a footnote: **a mutation that names a fact outside its own
subject has a shelf life.** It did not measure whether that was one bar or a class.

It is very nearly one bar. Of four raw replacements on document text, two run through
`_with_line_replaced` / `_without_line`, which **assert their anchor matched exactly one line** —
the fix pattern, already applied, before the lesson that named it. One is C100, derived yesterday.

That leaves **C88**, which anchors on `"## X11. Two of the four"` — a heading in a document C88 does
not own, belonging to an item owned by D7b, the next package. So the state was built: X11's heading
reworded the way a closing package plausibly would.

```
>       assert "X11" not in body_sections(without_body)
E       assert 'X11' not in {'X1', 'X10', 'X11', 'X12', 'X13', 'X14', ...}
FAILED tests/test_carried_items.py::test_every_registered_item_has_a_body_and_there_is_only_one_register
1 failed, 107 passed, 1 skipped
```

**Loud.** The no-op leaves X11 in the bodies, and the assertion is a negative over a set the
unmutated document satisfies — so a stale anchor cannot pass. The class is closed by measurement
rather than by the word *footnote*, and **no change is made**.

> **A fourth confirmation of `d2b06a4`, again by accident.** `1 failed, 107 passed, 1 skipped` — one
> red bar produced one red, with C99 declining a verdict rather than becoming a second. That is now
> three accidents and one probe.

---

## 2. X16 is prospective, and the corpus predates it

X16's discharge reads *"for each claim of impossibility **it makes**"*. Every foreclosure already on
the page when X16 landed is outside it. Two greps and a read found three testable candidates.

### 2.1 `d7a` §3.5 — "no bar can stop that"

> **The ladder reported at one cell.** §3.5 exists because a point estimate of a cost is a claim
> nobody can support. A caller taking the 1× `AS_QUOTED` cell and reporting it alone has defeated
> the whole apparatus, and **no bar can stop that** — it is a reading discipline, recorded here.

The same claim is on the `Ladder` class itself: *"which no bar can stop, and which is why it is
written on the object a reader holds."*

**The repository already bans `net_dv01` as a divisor by AST**, so the technique was not novel and
was available on the day the sentence was written. A thirty-line probe:

```
=== real source: src/deskcraft/costs.py ===   flagged: none
=== planted single-cell reporter ===          flagged: ['headline_cost']
=== the real ratio (two cells) ===            flagged: none
```

**False.** It fires on the defect and stays quiet on `convention_effect`, which reads two cells to
build a ratio. The sentence's own word is **caller**, and callers in this repository are exactly
what an AST bar reaches. Note that the two statements of the claim do not even agree with each
other about whose discipline it is — the document says *caller*, the docstring says *reader*.

### 2.2 `CARRIED_ITEMS.md` X12 — "no bar over a package that does not exist can catch that"

> **What C92 cannot do, and is this item.** It proves a module *mentions* the ladder, never that it
> *sweeps* it. A selector may import `COST_MULTIPLIERS` and evaluate one element, and **no bar over
> a package that does not exist can catch that.**

**Three paragraphs above, the same item says the opposite**, and names its own evidence:

> **That was wrong**, and `C76` and `C34` are both standing proof of it: a bar written by one
> package can arm now and bind when a later one lands.

X12 was raised to correct `AMENDMENT_A2` for saying *"this document cannot write it"* — and then
closed with a smaller copy of the sentence it was correcting. Probed at exactly the shape the
sentence describes:

```
real costs.py                  mentions=2 sweeps=1 subscripts=[]                    -> SWEEPS
planted selector (subscript)   mentions=1 sweeps=0 subscripts=['COST_MULTIPLIERS[1]'] -> PICKS A RUNG
planted selector (sweeps)      mentions=1 sweeps=1 subscripts=[]                    -> SWEEPS
```

**False**, by the technique X12 itself calls standing proof.

### 2.3 `d7a` §3.6 — "It cannot stop a profile being given a wrong number under an honest basis"

**True, and it stays.** No bar can check a number against a reality it has no independent access
to; that is the oracle problem and not a missing scanner. Recorded so that the ratio below has a
denominator with something in it.

### 2.4 What the rate is not

Three probed, two false. **That is not a base rate**, and saying so is this rider declining to
repeat yesterday's sentence — *"so the rate is one in two, on a sample of two"* — which reads like a
measurement and was not one. The denominator is unmeasured because recognising a foreclosure in
prose is the semantics problem that kept the prose-count class open, and row 10 shows the grep
missing half of a known sample. **Three claims were tested because three were found; nothing here
says how many there are.**

---

## 3. What replaces them (DD109)

**C102** holds the disposition of every module that reads the ladder, as an equality census.

**Why a census and not a ban.** X12's stated discharge explicitly permits D7b to report at one
rung *"if D7b instead argues that one rung is the right one, that is a decision and it is fixed in
advance in D7b's own document"*. A bar that forbids single-rung reads would overrule a discharge the
register grants. So C102 does not forbid; it **names**. Today exactly one module reads the ladder
and it sweeps. The day a module picks a rung, the census is no longer an equality and the suite is
red until the author either sweeps or writes the rung and its reason into the census — which is
precisely the decision X12 asks to be fixed in advance.

That is C99's shape one level over: do not refuse the act, refuse the *silence*.

**What this does to X12.** It stays **OPEN** and owned by D7b. The half that said no bar could
catch a single-rung read is struck and corrected; the half that asks D7b to *report* the ladder is a
positive obligation a scanner cannot impose, and C76 already holds it.

---

## 4. Predictions

| | Prediction |
|---|---|
| **P1** | Suite **109 → 110**. One bar, both halves inline |
| **P2** | C102 is red on both planted shapes and green on the tree as it stands |
| **P3** | No existing bar moves. X12 stays OPEN, the tally is untouched, no module is added |
| **P4** | Clean machine **102 → 103 passed**, still **7** skipped |
| **P5** | `ruff` 0; `lint-imports` 2 kept, 0 broken; 0 rows after `DEV_END` |
| **P6** | **`src/` enters the diff**, for the first time in four documents — the `Ladder` docstring carries the false claim and cannot keep it |

---

## 5. What this could still get wrong

- **The census could be read as closing X12.** It does not. It closes one sentence inside X12.
- **C102 counts sweeping syntactically.** A module that writes `for m in COST_MULTIPLIERS: break`
  sweeps by the scanner and not in fact. That is a narrower hole than the one it replaces and it is
  stated here rather than discovered later — which is X16's discharge, owed by this document too.
- **The corpus sweep has unmeasured recall**, §0 row 10. Nothing here claims the corpus is clean.

---

## 6. Result

**CLOSED 2026-09-16.** Bar **C102**; decision **DD109**. Suite **109 → 110**, green. Clean machine
**103 passed, 7 skipped** — the *7* held. `ruff` 0 findings; `lint-imports` **2 kept, 0 broken**.
Bar ids **110 claimed, no duplicates, no gaps, C1 → C102**. **0 rows dated after `DEV_END`**, held
by C97 in the green suite. **Next free: C103 / DD110.**

| | Verdict |
|---|---|
| **P1** | HELD exactly — 109 → 110 |
| **P2** | HELD — the scanner separates all four planted shapes, so the census is armed and not vacuous |
| **P3** | HELD — X12 still OPEN, the tally untouched, no module added |
| **P4** | HELD — 102 → 103 passed, 7 skipped |
| **P5** | HELD |
| **P6** | HELD — `src/` in the diff, deliberately |

### 6.1 Six of six is a weak run, and this one is weaker than it looks

Nothing unexpected went red, for the third document running — and this time the work did touch
guarded structures: `src/`, the register, and a landed pre-commit. Yesterday's rider offered the
reading that the quiet ones were quiet because they only annotated prose. **That reading is now
worse supported.** The honest version is narrower: predictions about *what this repository's bars
will do* keep holding, and predictions about *what its documents say* keep failing. Every
falsification in the last four documents — six instances of unguarded prose, and now two false
impossibility claims — came from reading, not from running.

### 6.2 Where the two false claims came from

Both were written at the moment a document stopped building and started explaining why it had
stopped. `d7a` §3.5 is in a list of *misreadings this package invites*; X12's is in the paragraph
naming what the item is **for**. **The sentence that says why a thing was not done is the least
examined sentence in a pre-commit**, because it is the one that closes a section rather than
opening one.

X12's is the sharper of the two: it was raised to correct `AMENDMENT_A2` for writing *"this
document cannot write it"*, and it closed by writing a smaller copy of that sentence three
paragraphs below its own refutation. **A rule can be stated and violated inside one item.**

### 6.3 What this does not close

- **X12 stays OPEN**, owned by D7b. One sentence in it is struck; the item is not.
- **The corpus is not swept.** §0 row 10 measures the only available scan missing half of a known
  sample. What is owed is now stated at the point of reliance — X16's widening — rather than as a
  census nobody could keep.
- **C102 counts sweeping syntactically**, §5. A `for ... : break` sweeps by the scanner and not in
  fact. Stated, not discovered later.
- **The habit is unchanged.** Two documents in two days have found that the thing they declared
  impossible was not. The rule now exists in two places and has been applied once.
