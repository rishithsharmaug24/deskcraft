# PRE-COMMIT — D5, deskcraft side: the front end is graded, and the floor that was waiting for it

**Written 2026-09-12, before any change to this repository.** The measurement is curvecast's and
is already committed there at `e78d2f7` (`FLOORS` 30 → 34, `D447`–`D452`, `C519`–`C522`). This
document covers only what deskcraft does about it.

**Why there are two commits and not one.** D5 is a deskcraft package whose deliverable is four
additive rows inside curvecast's table, so the measurement, the probe changes and the bars that
hold the table live in curvecast's commit, and this repository's commit is what deskcraft owes in
return: the floor that was written to go stale, tightened; the one sentence the measurement made
false, annotated; and three bars saying what is now true. The precedent is D3a, which wrote its
ledger entry into curvecast and its guards here, in two commits with two documents.

**Ids.** Decisions `DD39`–`DD41`. Bars `B39`–`B41`, executable as `C39`–`C41`.

---

## 0. Measured before decided

All of §0 was read on 2026-09-12 on this machine, against curvecast at `e78d2f7`.

### 0.1 The floor written to go stale has gone stale, and it did not say so

`graded_universe()` in `tests/test_book_types.py` asserts `len(series) >= 30`, and its own
docstring explains why it parses curvecast at test time rather than holding a copy: *"A hardcoded
copy here would have gone stale the moment D5 probes the four front-end floors, and going stale
silently is the failure this arrangement exists to prevent."* The parse today returns **34**, and
`DGS3MO`, `DGS6MO`, `DGS1` and `DGS2` are all four in it.

**The arrangement worked and the assertion did not.** Parsing at test time meant the new rows
arrived here the moment curvecast committed them, with no edit — which is what the docstring
promised. But `>= 30` is satisfied by 34 and by 30 alike, so nothing in this repository announced
that the thing it had been waiting for had arrived. A lower bound four rows below the truth is a
guard that has already spent its margin.

### 0.2 The universe, counted both ways

`graded_universe()` returns **42**: 34 archive floors plus the 8 GSW zero columns parsed out of
`curvecast.stage3.factor_space.TENOR_GRID`. `DTB3` — the secondary-market bill rate, a real FRED
series and a plausible front-end substitute — is **not** in it, because curvecast deliberately did
not measure it (its `C521` asserts the refusal).

### 0.3 Leg 1's reason is now half false

`src/deskcraft/reference.py:90` gives two grounds for expressing the policy-expectations leg on
the GSW two-year zero rather than on the FRED two-year constant maturity: *"because `DGS2` carries
no measured archive floor **yet** and `SVENY02` is pinned"*. The first ground expired at curvecast
`e78d2f7`. The second did not.

**The two instruments are not interchangeable**, which is the part the sentence never said:
`SVENY02` is a zero yield off the pinned GSW file and `DGS2` is a par constant maturity off H.15.
Swapping them because a floor was measured would move a number while appearing to tidy a comment.

### 0.4 The four already have register rows, and all four are committable

D3a's `SOURCE_ROWS` already carries `DGS3MO`, `DGS6MO`, `DGS1` and `DGS2` as Board H.15 rows.
Read today: FRED's tag `PUBLIC_DOMAIN`, the Board's notice `PUBLIC_DOMAIN`, operative licence
`PUBLIC_DOMAIN`, `committable` **True** on all four. So the licence question curvecast's WP-L1
answered for 34 fixtures was already answered here for these four series, before they were graded.

### 0.5 Nothing in this repository is red, and that is the finding

`pytest -q` on the tree curvecast's D5 landed on: **41 passed**, 0 failed, 0 skipped. C14 is green
because `graded_universe()` returned a **superset** of what it returned yesterday, and every leg's
components were already inside the smaller set.

### 0.6 The NO-BUILD floor has not moved, and this package does not move it

`BUILD_ORDER_D3_D16.md` §1 row 1 is why D5 was pulled ahead of D4: *"Only four legs of the
reference structure are priceable from graded data, which is exactly §10's NO-BUILD floor."*
`US_CASH_BOOK` prices `us_2y`, `us_10y`, `us_breakeven_5y` and `eurusd` from `SVENY02`, `SVENY10`,
`SVENY05` + `DFII5`, and `DEXUSEU`. That is still four legs after this package, because D5 adds no
leg. **What D5 bought is headroom in the reachable universe, not a fifth priceable leg** — and the
package that spends it is D7, the leg generator.

---

## 1. Decisions

### DD39. The floor moves to the count that was measured, and stays an inequality

`len(series) >= 30` becomes `len(series) >= 34`.

It stays `>=` rather than `==` on purpose. curvecast owns that table and will add rows to it
without asking this repository; an equality here would turn a sibling's ordinary work into
deskcraft's red, and a downstream guard that cries on every upstream addition gets relaxed rather
than read. The direction this floor exists for is the other one — a row **disappearing**, or the
AST scan silently matching nothing after a refactor upstream — and against that, a floor at
today's measured truth is strictly better than one four rows beneath it.

**curvecast holds the equality and deskcraft holds the floor.** curvecast's `C519` asserts
`tuple(FLOORS) == census` over all 34 names, which is the assertion that belongs with the table's
owner. Restating it here would be a second copy of a census, which is the thing `graded_universe()`
was written to avoid.

### DD40. The leg does not move, and the expired half of its reason is annotated, not rewritten

curvecast's D5 §2.1 forbids this package moving a leg onto a newly graded series, and §0.3 is why
that is more than procedure. So `_US_2Y` stays on `SVENY02`, and the comment at `reference.py:90`
gains a dated clause recording which half of its ground expired and when.

**Annotated, never silently rewritten** (curvecast D70). Deleting the `DGS2` clause would leave a
comment that reads as though `SVENY02` had always been chosen on its merits, and would erase the
one fact a later reader needs: that the alternative became available on 2026-09-12 and was not
taken. `C40` pins the leg so that the decision cannot be made by accident later.

### DD41. What is graded is asserted by name, not by a count

`len(series) >= 34` is satisfied by any thirty-four strings. The claim this package actually makes
is about four named series, so `C39` names them — and names `DTB3`, which curvecast refused to
measure, so that the bar cannot pass because a scan started matching everything.

---

## 2. What this package does not do

1. **It does not move any leg.** Leg 1 stays on `SVENY02`. That decision belongs to D7, which
   builds the leg generator and has a reason to make it.
2. **It does not change `US_CASH_BOOK`, `DEFERRED_LEGS` or `REFERENCE_BOOK`.** No instrument, no
   notional, no direction.
3. **It measures nothing.** The floors are curvecast's measurement; this repository has no egress
   and could not re-take them if it wanted to.
4. **It does not touch curvecast or MEIP.** curvecast's four rows landed in curvecast's own commit
   at `e78d2f7`; nothing upstream changes in this one.
5. **It does not lift the §10 NO-BUILD floor.** The priceable count is still four (§0.6).
6. **It does not amend closed documents.** `PRECOMMIT_deskcraft_d2_book_types.md` says `DGS2` has
   no measured floor; that was true when it was written, and a pre-commit document is a record of
   what was believed before a run, not a live claim.

---

## 3. Verification

### 3.1 Bars

| bar | what would falsify it | executable |
|---|---|---|
| **B39** | The front end not being graded upstream, or the scan matching everything. Parsed from curvecast at test time: `DGS3MO`, `DGS6MO`, `DGS1` and `DGS2` are each in the graded universe; the floor count is **at least 34**; the GSW columns are exactly 8; `DTB3` is **absent**, so a scan that had started matching every string in the file would fail rather than pass. **Skips loudly** if curvecast is absent. | C39 |
| **B40** | A leg moving onto a newly graded series without a package deciding to (DD40). `US_CASH_BOOK.leg_ids` is exactly `('us_2y', 'us_10y', 'us_breakeven_5y', 'eurusd')`; the two-year leg's components are exactly `('SVENY02',)`; `DEFERRED_LEGS` keys are exactly `us_10y_call` and `us_de_10y`; and **no leg of `REFERENCE_BOOK` reaches any of D5's four**. The last clause is the one with teeth: C14 would stay green if leg 1 moved to `DGS2`, because `DGS2` is now graded. | C40 |
| **B41** | A series reachable by a later leg whose licence forbids the fixture that leg would need (DD41, WP-L1's rule). Every one of D5's four has a `Source` row keyed by its own series, operative licence `PUBLIC_DOMAIN` — the **maximum** of FRED's tag and the originator's notice — and `committable` True. | C41 |

### 3.2 Predictions

Fixed before any change is made to this repository, scored as written.

- **P1. The suite goes 41 → 44**, 0 failed, 0 skipped.
- **P2. Raising the floor turns no existing bar red.** C14 in particular stays green, because
  `graded_universe()` returns a superset of what it returned before, and every leg's components
  were already inside the smaller set.
- **P3. The parse is 34 floors, 8 GSW columns, universe 42**, and `DTB3` is absent from it.
- **P4. No leg moves.** `US_CASH_BOOK.leg_ids` is the four of §0.6 in that order, the two-year leg
  names exactly `('SVENY02',)`, `DEFERRED_LEGS` is exactly the two of §0.6, and no leg reaches any
  of D5's four series.
- **P5. All four register rows are `PUBLIC_DOMAIN` on tag and on notice, and committable.**
- **P6. `lint-imports` reports 2 kept, 0 broken**, and MEIP's reports **6 kept, 0 broken** with
  MEIP's tree unmodified. This package adds no import: the new module imports what
  `tests/test_book_types.py` already imports.
- **P7. curvecast's `run_gates.py` is 44 of 44, exit 0** on the tree at `e78d2f7`. This repository
  changes nothing there, so this is the property re-checked rather than a new claim — D3a's P8
  shape, and the failure mode it guards is this repo quietly reaching upstream and relaxing
  something.
- **P8. Every new bar passes on its first complete run.** Written down knowing the record it bets
  against: D1 missed this on two bars, D2 on one, and D3a predicted its own miss and hit it. This
  package predicts no miss, which makes P8 the prediction most likely to fail.

### 3.3 Result

**Three new executable bars, all passing on their first complete run; the suite goes 41 → 44, 0
failed, 0 skipped.** `lint-imports` reports **2 kept, 0 broken**; MEIP's reports **6 kept, 0
broken** and its tree is clean; curvecast's `run_gates.py` is **44 of 44, exit 0** in **872s**.
The bars and predictions above are as they stood before any file in this repository was touched
(sha256 `69547008…` of this document then); nothing in §0 through §3.2 has been edited since.

| | outcome |
|---|---|
| **P1** suite 41 → 44, 0 failed, 0 skipped | **hit** — `44 passed in 1.05s` |
| **P2** no existing bar changes verdict | **hit** — C14 green, and the 41 that passed before pass unchanged |
| **P3** 34 floors, 8 GSW columns, universe 42, `DTB3` absent | **hit** — `floors=34 gsw=8 universe=42 DTB3_in=False` |
| **P4** no leg moves | **hit** — `('us_2y', 'us_10y', 'us_breakeven_5y', 'eurusd')`, deferred `('us_10y_call', 'us_de_10y')`, the two-year leg still `('SVENY02',)`, and no leg of `REFERENCE_BOOK` reaches any of D5's four |
| **P5** all four register rows public domain and committable | **hit** — `PUBLIC_DOMAIN` on tag and notice, operative licence `PUBLIC_DOMAIN`, `committable` True, on all four |
| **P6** `lint-imports` 2 kept / 0 broken; MEIP 6 / 0, tree unmodified | **hit** — both, and `git status` in MEIP is empty |
| **P7** curvecast 44 of 44, exit 0 | **hit** — 872s, every gate green, `meip:untouched  unmodified` |
| **P8** every new bar passes on its first complete run | **hit** — C39, C40 and C41 green on the first run of the three together |

**Eight of eight, and that is the least interesting result this repository has produced.** D1
missed on two bars, D2 on one, and D3a predicted its own miss and hit it. This package predicted
no miss and had none, because almost everything it does is mechanical: the measurement was taken
elsewhere, and what is written here is four names, a floor, an annotation and three assertions
about facts already on disk. A clean sheet on eight easy predictions is not evidence of anything
beyond the predictions having been easy, and it is recorded that way rather than as a record.

#### One thing the run measured that nothing predicted

curvecast's own D5 §3.3 records its sweep at **1,611s** and says it could not attribute the 333s
by which that exceeded WP-L1's 1,278s. This sweep is the same tree plus two document edits and it
took **872s**. Per gate: `gdelt-archive` **458.2s → 18.9s**, `pytest` **437.8s → 367.9s**,
`meip-venv-sweep` **368.7s → 245.9s**, `receiver-copy` **117.4s → 82.8s**, `meip:pytest` **190.0s
→ 127.9s**. Counts are identical everywhere — 1,047 passed / 21 skipped, 769 / 299, 194, 1,410.

**So a sweep's wall time on this machine is not a comparable figure across runs, and reading one
as though it were would have been a mistake in either direction.** curvecast's §3.3 hedged
correctly by recording the number and declining to explain it; this run says why the hedge was
right. Most of the swing is one gate — `gdelt-archive` alone accounts for 439s of the 739s
difference — and no count anywhere moved, so nothing about the tree changed between them. The
cause is not diagnosed here and is not this package's to diagnose.

It matters beyond bookkeeping. `curvecast:pytest` carries a **measured 2,700s** budget, set at
`8a59cab` after a 900s budget killed a gate that had been running at 902s. On this tree that gate
has now been observed at **437.8s and 367.9s**, and on the tree three commits back at **918.9s**
over a suite 17 tests smaller. A gate whose honest observations span better than two to one is
exactly the case for a budget set from measurement with headroom rather than from a round number,
which is what `8a59cab` argued and what these two sweeps happen to demonstrate.
