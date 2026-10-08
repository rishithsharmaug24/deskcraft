# Rider — the fifth verdict: compute on it, do not ship it

*2026-09-23. Narrows **X22** and **X25**, carries **DD136**, adds bars **C122–C124**. Adds no
package, fetches nothing, reads nothing dated after `DEV_END`, and commits no new byte of anyone
else's data. The budget stands at 21.*

*Raised by the owner, against a challenge worth quoting because the answer to it is the whole
document: **"I am not planning to sell this to anyone and this is just for my personal use, so why
is it blocked?"** The answer is that most of it was not blocked, that DD118 said so six days ago,
and that nothing in the tree had been taught to agree.*

---

## 0. Measured before decided

| # | Measured | Value |
|---|---|---|
| 1 | Rows in `SOURCE_ROWS` | **23** |
| 2 | — committable today | **18** |
| 3 | — refused today | **4** — `VIXCLS`, `BAA10Y`, `AAA10Y`, `DE_ZERO_10Y` |
| 4 | — in DD118's middle disposition | **1** — `T10YIE` |
| 5 | Predicates on `Source` before this document | **2** — `committable`, `independent_fallback` |
| 6 | — of those, predicates answering *may a package read this* | **0** |
| 7 | Days between DD118 taking the decision and the type expressing it | **6** |
| 8 | Sources DD118's table names as newly readable | **3** — Japan MoF JGB, NY Fed FR 2004B, ECB/Bundesbank |
| 9 | — of those, rows in this register today | **0** |
| 10 | D19 vol inputs this document unblocks | **0** |
| 11 | Committed fixture columns naming a non-committable series | **0**, before and after |
| 12 | Suite before / after | **129 / 132** |
| 13 | Next free ids | **C125 / DD137 / X26** |

**Rows 9 and 10 are the ones to read twice.** This document builds a cell and does not fill it. The
three sources DD118 said could now be read are not in the register, and grading them is a package's
work, not a rider's. And the vol surface — the thing the owner asked about — is **not** among them:
see §3, which exists because the tempting misreading of this rider is that it is a route to Cboe.

**Row 6 is the defect.** `Source` could answer *may this byte be shipped* and could not answer *may
this number be read*. Every package that wanted the second question asked the first one, got a
stricter answer than its question deserved, and declined.

---

## 1. The decision, in one line

> **DD136.** A source carries two independent grades — what its words permit to be **copied**
> (`Licence`) and what they permit to be **computed** (`Derivation`) — and `Source.disposition`
> derives DD118's three-way sort from both. The middle cell,
> **`USABLE_NOT_COMMITTABLE`**, means the numbers may be fetched and derived from and the bytes may
> not enter git: what ships is the result and the fetch script. **C122–C124.**

---

## 2. X22 named the defect and named what closes it

X22's body is unusually specific about its own discharge:

> *"Either a `readable` predicate and a term for the no-derivatives condition, or a written argument
> that the three dispositions collapse to two."*

**This takes the first branch, and the second branch is now refuted by measurement rather than by
preference.** The three do not collapse to two, because row 4 of §0 is not empty: `T10YIE` is
graded `CITATION_REQUIRED`, is not committable, and is a series this repository already reads. It
has been sitting in the middle cell since D3a and the register had no name for where it was.

**The missing term is not "no derivatives".** X22 guessed at *modification not permitted*, and
reading A5 §3 against DD118's own table shows the shape is finer. The ESCB condition binds on
**republishing modified statistics** — a condition on the *output*, not on the computation. So the
term is `RESULTS_ONLY`: derive freely, publish the verdict, do not republish the data. That is a
permission, not a refusal, and grading it as a refusal is what cost the German curve.

`Derivation` therefore carries four terms — `PERMITTED`, `RESULTS_ONLY`, `PROHIBITED`,
`UNMEASURED` — ordered least to most restrictive, with `UNMEASURED` strictest for DD34's reason:
*a default here would hand the widest permission to the least evidence.*

### 2.1 What DD35 keeps

`Source.committable` is byte-identical in meaning: `self.licence is Licence.PUBLIC_DOMAIN`. It was
always a statement about the archive and never about the reading, and DD118 said so explicitly.
**C124 exists to hold exactly that** — that widening what may be read did not widen what may be
shipped — because that is the one way this change could go wrong, and it would go wrong silently.

The owner's challenge was right about the premise and this rider does not act on it. DD35's stated
ground is *"a fixture committed to a repository that is then sent anywhere is redistribution"*, and
it closes *"this is an engineering rule, conservative on purpose. It is not a reading of anyone's
contract."* The rule survives the challenge because **it costs almost nothing once the middle cell
exists.** Before today, DD35's conservatism was also blocking reading, which it never meant to. It
is not conservative to decline a computation in order to protect an archive; it is a category error,
and it was this one.

---

## 3. What this does not do, stated before anyone hopes otherwise

**It does not reopen the vol surface, and a reader coming to this document from the options
question should stop here rather than at §1.**

DD118's own table settles it: *"Moody's, ICE, BIS, BoJ — **still refused.** Each is stricter than
attribution in its own words, and no widening reaches them."* Cboe belongs in that list on the new
axis specifically. DD121 read Cboe's terms directly and they forbid the computation, not merely the
copy:

> *"You may not **otherwise** ... **create a derivative work (for example, a financial product,
> service or index) from, use to verify or correct other data or information**, publish ...
> distribute."*

`VIXCLS` is therefore graded `PROHIBITED` on derivation and **refused on either axis alone**. The
fifth verdict is a route to sources whose words restrict *distribution*; it is not a route to
sources whose words restrict *use*. **C123 pins this**, and the mutation it was tested against is
the honest one: regrade Cboe as derivable and the bar reports it.

Three of D19's eight inputs also remain not-found-free at any route, which is an availability fact
and is untouched by any licence decision. Row 10 of §0 is **0** and it is not a rounding.

**What it does reach**, when a package chooses to spend the budget on grading them: the Japan MoF
JGB curve back to 1974, the NY Fed's FR 2004B for X11's impact term, and the euro leg at
`RESULTS_ONLY`. All three were refused at the grade this morning for a reason that was about the
archive. None is commissioned here; DD118 was explicit that removing the licence blocker is not
commissioning the work, and that remains true.

---

## 4. The bars

**C122 — a licence and a derivation are two axes and they cannot contradict each other.**
The vocabulary exists by name rather than by position; `UNMEASURED` is the maximum on the new scale;
`Disposition` has exactly three cells; a public-domain row cannot restrict derivation, and the
constructor refuses the contradiction rather than leaving it to a reader. *Mutation:* a public-domain
row is given `PROHIBITED` and the bar reports it.

**C123 — every row is graded on both axes, and the middle cell is occupied.**
A term no row uses is a word, not a verdict. `T10YIE` is asserted into the cell by name, so that
emptying it is a visible edit. And Cboe is asserted out of it on the derivation axis specifically.
*Mutation:* `VIXCLS` is regraded as derivable and the bar reports it.

**C124 — widening what may be read did not widen what may be shipped.**
`committable` still answers `licence is PUBLIC_DOMAIN` for every row; a middle-cell row is asserted
*not* committable; and every committed fixture's header is swept against the register, with a guard
that fails if the sweep finds no fixture to look at. *Mutation:* a synthetic fixture carrying
`VIXCLS` is offered and the bar reports it.

---

## 5. Dispositions

| Item | Status | What changed |
|---|---|---|
| **X22** | **OPEN, narrowed** — owner D8 | Both halves of its stated close-path are built: `readable` exists and the missing term is named `RESULTS_ONLY`. The discharge sentence is still D8's to write at landing, per DD31 and C76 |
| **X25** | **OPEN, narrowed** — owner D8 | `VIXCLS` now carries the originator's derivation words as well as the distributor's reprint note, so the row no longer rests only on the read X25 falsified. The **licence** regrade X25 actually asks for is untouched and still owed |

**Neither closes, and that is the same correct outcome as last time.** D8 has not landed, C76 will
refuse it without `**X22** — discharged:` and `**X25** — discharged:`, and a rider that wrote those
sentences on D8's behalf would be the half-state C118 exists to refuse. What this removes is the
possibility of D8 discovering at landing that the type it needed was never built.

**One consequence was found by a bar and is recorded rather than hidden.** Inserting the new enums
moved `sources.py`, which broke **C118** — X20's body cites `sources.py:315` and `:319` and the
lines are now **424** and **428**. The citations are corrected in the register.

**It broke twice, and the second time is the one worth recording.** The first correction was made
while the code edit was fresh; then a paragraph was added to the module docstring, the lines moved
again by eight, the bar went red again, and the commit was made anyway because the suite had been
run before that last edit rather than after it. That is the entire failure mode in miniature — not
ignoring a red bar, but running the check and then doing one more thing. The fix is this commit and
the record is this paragraph. A pinned line number is a real cost of editing landed code, and the
bar charged it twice because it was owed twice.

---

## 6. The prediction, fixed before anything is graded

**P — the first source graded under DD136 will land in `REFUSED` and not in the middle cell, and
the reason will be `UNMEASURED` on the derivation axis rather than a read prohibition.** Registered
because the optimistic reading of this document is that a new cell means new data, and the boring
outcome is that grading is work and the strict default bites first. If the first new source lands
straight in the middle cell, that is a result and not a relief.

---

*Next free ids: **C125 / DD137 / X26**.*
