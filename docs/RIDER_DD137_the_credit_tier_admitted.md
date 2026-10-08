# Rider — the credit tier admitted, and the guarantee that was spent to do it

*2026-09-23, the same day as DD136 and hours after it. Carries **DD137**, adds bars **C125–C127**,
narrows nothing and closes nothing. Adds no package, fetches nothing, reads nothing dated after
`DEV_END`. The budget stands at 21.*

*Raised by the owner, who asked whether the reasons given against lifting DD35 were the only
reasons. **They were not**, four more were found on the check, and the owner took the narrower of
the two decisions that were then available.*

---

## 0. Measured before decided

| # | Measured | Value |
|---|---|---|
| 1 | Commits in this repository that have ever touched `tests/fixtures/` | **1** |
| 2 | — of those, commits carrying a non-public-domain column | **0** |
| 3 | Rows in `SOURCE_ROWS` | **23** |
| 4 | — committable before / after | **18 / 21** |
| 5 | — freely sendable before / after | **18 / 18** |
| 6 | Series admitted | **3** — `T10YIE`, `BAA10Y`, `AAA10Y` |
| 7 | — of those, requiring a new fetch anywhere | **0** — all three are already in curvecast's `block_i_vintages_dev.csv` |
| 8 | Series in the middle cell DD136 built this morning | **1 → 0** |
| 9 | Existing bars that went red on the change | **5** |
| 10 | — of those, red because a guarantee was genuinely surrendered | **3** — C36, C47, C124 |
| 11 | — red for a mechanical reason (pinned line numbers) | **1** — C118 |
| 12 | `CREDIT_VS_RATES` tradeable series before | **0 of 1** (A5) |
| 13 | D19 vol inputs this document unblocks | **0** |
| 14 | Suite before / after | **132 / 135** |
| 15 | Next free ids | **C128 / DD138 / X26** |

**Rows 1 and 2 are the price.** This repository's history was clean — one fixture commit, no
restricted column, ever. That is a property a repository has once. Row 5 says it has not been spent
yet, because no admitted column is in a fixture; the decision is taken and the data has not moved.

**Row 8 is the one nobody would have predicted.** DD136 built the `USABLE_NOT_COMMITTABLE` cell in
the morning and it held exactly one row. DD137 admitted that row in the afternoon and the cell
emptied. The cell is not wasted — it is what `readable` returns for a graded, unadmitted row, and
it is the route for the JGB curve, FR 2004B and the euro leg — but **it is unoccupied today and
C123 now asserts that it is**, because a bar asserting occupancy would be asserting a wish.

**Row 13 is unchanged from this morning and will not move.** See §3.

---

## 1. The decision, in one line

> **DD137.** `Source.committable` is *public domain* **or** *named in `sources.ADMITTED`*. An
> admission is an owner decision for one series, written and dated in
> `docs/OWNER_ADMISSION_the_credit_tier.md`, never a tier and never a default. A series whose
> words forbid **derivation** may not be admitted at all. DD35's original question survives as
> `Source.sendable_free`, and `NOT_SENDABLE.md` records in the tree that its answer has stopped
> being *yes* everywhere. **C125–C127.**

---

## 2. The check the owner asked for, and what it found

The owner's condition was explicit: *"check thoroughly if the reasons mentioned here are the only
reasons and if so I want to go ahead."* **The condition was not met.** Four reasons had not been
given, and one of them falsified the description of the option itself.

| # | Found | Consequence |
|---|---|---|
| 1 | **deskcraft has no egress.** Bar `C2`; `conftest.py` refuses the network for the whole suite; `panel.py` says so in its own `FileNotFoundError` | "deskcraft can download and commit anything" was **false**. The fetch is curvecast's |
| 2 | **curvecast does the stripping and has a stricter, separately-motivated regime.** `make_deskcraft_panel.py` carries `REFUSED_SERIES`; WP-L1 took 22 fixtures out of git; D442 makes `git archive HEAD` the only copy because 13 commits carry restricted blobs | Lifting DD35 alone changes nothing. And curvecast's rules rest on third-party permissions never granted — *personal use* does not dissolve them |
| 3 | **It does not undo.** Rows 1–2 of §0 | The clean history is spent at the first commit of an admitted column, and the only remedy is a rewrite that curvecast itself declined |
| 4 | **"Personal use" does not reach Cboe, and Cboe was the point.** Its terms forbid *creating a derivative work from* the data | The option's premise — *a sharing risk, not a lawsuit risk* — is sound for the citation-required and redistribution-prohibited tiers and **unsound for the tier the owner wanted** |

A fifth, smaller: `MOVE` is an ICE index not freely downloadable, blocked by *free data only, no
purchases* rather than by any licence. It was named in the option's description and was never
available.

**The owner took the narrower decision on that basis.** That sequence is the reason this document
exists as a rider rather than as an edit: the decision changed shape between being offered and
being taken, and a register that records only the outcome loses the part that was informative.

---

## 3. What DD137 does not reach, and why it is a limit rather than an omission

`VIXCLS` and the Cboe complex **cannot** be admitted. Not *are not* — cannot:
`Source.__post_init__` raises if a row in `ADMITTED` is graded `Derivation.PROHIBITED`, and
**C126** mutation-tests that refusal against the mutation that would actually happen.

The argument is one line and it is worth stating plainly because it is the whole boundary of the
owner's reasoning: **DD137 says a rule about sending does not bind a repository that is not sent.
Cboe's restriction is not a rule about sending.** It governs the computation — *"create a
derivative work ... from, use to verify or correct other data"* — and a decision about distribution
has nothing to say about it. The owner's argument is good and it stops here.

**C126's mutation is deliberately not "someone admits Cboe."** That is the obvious edit and it is
not the likely one. The likely one is that somebody measures Moody's derivation words — currently
`UNMEASURED`, because the notice governs copying and is silent — finds them stricter than the
silence assumed today, and regrades `BAA10Y`. An admitted row that turns out to forbid derivation
must refuse to construct, not quietly stay committable. That is what C126 tests.

---

## 4. What went red, and the difference between the two kinds

Five bars. **Three were red because a guarantee was genuinely surrendered, and those are the ones
worth reading:**

- **C36** asserted `committable is (licence is PUBLIC_DOMAIN)`. It now asserts that of
  `sendable_free`, and asserts `committable` is that *or* an admission. The old line was not wrong;
  it was a statement about a property that no longer exists in that form.
- **C47** refused `BAA10Y` and `T10YIE` by name. Those were two of its three refusals. They are
  asserted to **pass** now, at the same site — not deleted, because a deleted refusal leaves a gap
  where a guarantee used to be and nothing marks it. Its subject is `VIXCLS` now.
- **C124** was written this morning to hold that DD136 had not widened what may be shipped. It
  still holds that. DD137 widened it, deliberately, and C124 now holds the finer statement: the
  guarantee is intact **except where the owner spent it by name**.

**One was mechanical.** C118 pins `sources.py` line numbers through X20's body; the new register
moved them from 424/428 to **534/538**. Third time today. Corrected.

**One was a consequence nobody predicted:** C123, above, row 8.

---

## 5. The bars

**C125 — an admission is a written, dated, named act and not a tier.**
The three are asserted by name rather than counted, because a count passes silently when the list
grows. Each carries the decision date, a reason long enough not to be a category, a row in the
source register, and a mention in the admission document. The reasons must be distinct — three
copies of one sentence is a tier wearing three hats. *Mutation:* the list is the assertion; a
fourth series fails it, which is correct, because a fourth series is a fourth decision.

**C126 — a prohibition on computing is not a rule about sending.**
`VIXCLS` is `PROHIBITED`, unadmitted, uncommittable and unreadable; and an admitted row regraded to
`PROHIBITED` raises at construction. *Mutation:* `BAA10Y` is constructed with prohibited derivation
and the bar reports it; the loader is checked too, so the refusal is the one that runs.

**C127 — the cost is recorded in the tree, not in a memory.**
`NOT_SENDABLE.md` must exist, and must name every admitted series that is actually in a committed
fixture. The bar is written as an equivalence with both branches live: today no fixture carries an
admitted column, and the marker is still required, because the decision is what makes a future
commit unremarkable. Also asserts that no admitted row is *also* freely sendable — that would mean
the admission was unnecessary and the two predicates had been confused.

---

## 6. Dispositions

No item opens, closes or narrows. **X22 and X25 are untouched** and still D8's; DD137 widened
`committable`, which is not the predicate either of them is about.

**What is now owed and has no item, stated rather than opened.** The columns are not in a fixture.
Putting them there is a change to **curvecast's** `make_deskcraft_panel.py` — removing three names
from its `REFUSED_SERIES` and regenerating the panel — and it lands in a different repository with
its own gate. It is not opened as an X item here because **X items are owed by deskcraft packages**
and this one is not deskcraft's to discharge. The next package that needs a daily credit leg
commissions it.

*(**Discharged 2026-09-25, DD140.** The owner asked for Moody's derivation words to be read
before the columns moved, because C126's mutation names the one way the admission could fall:
a row regraded `PROHIBITED`. It was not. The notice forbids copying, repackaging and
redistribution and says nothing against computing, so the grade is `RESULTS_ONLY` and the
admission stands. Moody's **site** terms do forbid *"create derivatives of"*, for material
taken from its sites, and that route is recorded as refused in the row's `evidence`. curvecast's
`make_deskcraft_panel.py` now writes a **third** file, `panel_daily_admitted_dev_20260925.csv`,
carrying `BAA10Y` and `AAA10Y` and nothing else: 6,753 DEV sessions each, zero vintage refusals
inside DEV, on the GSW grid. The two public-domain panels are byte-identical. `T10YIE` is
admitted and **not carried**, for D3b's DD45 reason, which is about design and not licence.
`REFUSED_SERIES` was not edited, as the paragraph above expected: it still guards the two
sendable panels, and the third file has its own allow-list. C128 and C129 hold the split.)*

---

## 7. The prediction, fixed before the columns move

**P — the first thing to go wrong with DD137 will not be a licence problem. It will be that
somebody sends the repository anyway**, because `NOT_SENDABLE.md` is a file and files are read by
people who are looking for them. Registered because the compensating control chosen here is
documentary, and the honest prior is that documentary controls fail in exactly one direction. If
eighteen months pass and the marker has done its job, that is a result and not a relief — and the
route that would actually make it safe, a strip-and-send built in curvecast's WP-L1 shape, is
named in `NOT_SENDABLE.md` §"How to make the repository sendable again" and does not exist yet.

---

*Next free ids: **C128 / DD138 / X26**.*
