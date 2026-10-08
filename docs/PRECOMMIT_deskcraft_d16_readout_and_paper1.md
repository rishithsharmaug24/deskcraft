# D16 — the readout and Paper 1, built before the read and landed after it

**Status: LANDED 2026-09-28.**

*Written 2026-09-28, after D13 landed (`dac50a5`) and before the first out-of-sample read:
`docs/OWNER_AUTHORISATION_the_first_oos_read.md` does not exist. D16 scores no claim. It reports
Paper 1's nine hypotheses as written, its limits and its declines, and five of the nine are verdicts
only the read can produce. So the readout and everything around those five are built now, and D16
lands in the commit that renders the five after the read. That commit tags CP-2 (`AMENDMENT_A1`
§7.1).*

`BUILD_ORDER_D3_D16.md` §4: *"Readout and paper. Describes, never recommends. H1–H9 scored as
written, limits, and the declines."* DD138 adds that the first limit stated is the saturated cosine
**0.906494022**. D16 owes **X20** and **X26**.

---

## 0. What D16 does, in one paragraph

Paper 1 is the engine's paper: a stated view in, a multi-leg book out, its risk decomposed and
stressed, and the risk model and the construction tested on eleven years the fit never saw. D16
writes that paper from the registers rather than from memory. The claims table is **rendered** from
`registers.CLAIMS`, so the paper cannot state a verdict the register does not hold. Every figure it
quotes is checked against the document of the package that recorded it. The limits and declines are
the ones the packages measured, each with its number. Five verdicts, H1, H2, H5, H6 and H7, and the
`SCENARIO_SIGNS` report, appear as **awaiting the read**. They are filled by re-rendering once the
joint registration's readers have run, and not by editing prose.

## 1. The rules

> **DD225 — D16 is registered and not landed, and why that is not a postponed verdict.** D16 scores
> no claim, so the registered marker postpones none of its own. It holds D16 open because
> **"Paper 1 complete and sendable" is CP-2's definition** (`AMENDMENT_A1` §7.1), and five of
> Paper 1's nine hypotheses are verdicts of the out-of-sample read. Landing D16 now would tag a
> checkpoint whose defining condition is false. C158's declared set of registered documents gains
> this one, with this reason, as DD182 added D17's. The marker leaves in the landing commit, which
> re-renders the paper after the read and does nothing else.

> **DD226 — the claims table is rendered, and the paper holds the render.** `readout.claims_table()`
> renders Paper 1's rows of `CLAIMS`: every claim whose scorer is a Paper 1 package, D3a to D16, with
> its statement, scorer, predicted verdict and verdict. A withdrawn claim shows its successors. An
> unscored claim whose scorer reads the record shows **awaiting the read**. The paper carries the
> render between two markers, and a bar holds the two equal. When the read gives CLAIMS five
> verdicts, the bar goes red until the paper is re-rendered. That is the mechanism, and nobody has
> to remember it.

> **DD227 — every figure the paper quotes is one a package recorded.** `readout.FIGURES` lists each
> number the paper states, with the document that recorded it. A bar checks that each figure appears
> in its document and in the paper. So the paper cannot quote a number its package never wrote down,
> and a figure a package later corrects turns the paper red.

> **DD228 — the limits, in this order.** Each with its measurement:
>
> 1. **The grammar reaches at most 0.906494022 of an arbitrary view direction**, at any cost and any
>    conviction (DD138). First, as DD138 requires.
> 2. **H4b could not fail**: the whitening rung returns the leg count for any book (D10).
> 3. **H9's margin is a property of the grid**: 0, 1 or 2 legs at all eight cells, against a
>    predicted 3 to 4 (D7b).
> 4. **The generator is path-dependent** (X26): its headline book is a short 10-year outright,
>    reached through two legs whose 30-year DV01s cancel exactly, though the pool offered the
>    10-year as one leg (D13 §9.2).
> 5. **On one Gaussian covariance, reverse stress is the Euler decomposition** (D13, DD221): the
>    budget breach sits 2.3378 sigmas out for every budget-scaled book.
> 6. **Held means frozen**: no carry, no roll-down, no FX differential. Futures and swaps are
>    carried as DV01-matched cash, with what that drops named on each leg (DD12, DD175).
> 7. **H1's test has a size of 11.5%** under a correctly specified model (the joint registration §3),
>    and **H5's power at the plausible effect is 8%** (DD164). A pass or a failure of either is read
>    against those numbers.
> 8. **The predictions are not information-blind**: the 2015–2025 path is public, and 2020 and 2022
>    are named because they happened (the independent review's finding 17).

> **DD229 — the declines, each with the measurement behind it.**
>
> 1. **The cross-market leg** (X20). DEC-2 deferred it to a package no row of the build order
>    commissions, and DD126 declined that package: the budget is twenty-one, one in and one out.
>    `AMENDMENT_A5` §3 measured the licences that deferral was waiting on. The US-versus-Bund leg of
>    the source's structure is therefore not built, and the six code sites that defer it say so (C118).
> 2. **Options and volatility** (X23, DD121). Cboe's terms refuse derivative computation from its
>    volatility indices without written consent, three of the eight inputs D19 named are not free at
>    any route found, and MOVE and CVOL are licensed. The blanket option decline stands for Paper 1.
>    Paper 2's bought options are priced on realised volatility or the Minneapolis Fed's
>    distributions, under the owner's admissions.
> 3. **The credit leg.** `CREDIT_VS_RATES` reaches no tradeable series (DD124). The daily Moody's
>    pair is admitted for results only (DD140), and `GZ_SPREAD` is monthly.
> 4. **A seventh grammar term** (DD138): declined for version 1. Its absence is limit 1.
> 5. **Commodities** (DD127): Paper 2's crude arm only, never Paper 1's.

> **DD230 — describes, never advises.** The rendered paper passes the boundary's
> `FORBIDDEN_RENDERED_PHRASES`, the imperative ban ported from curvecast, and a bar reads it. The
> engine's own boundary is a capability ban; this is the same rule applied to the one document the
> engine's results reach a reader through.

## 2. Carried items

**X20** — discharged: DD229 item 1 writes the cross-market leg as a decline, with DD126's reason and
`AMENDMENT_A5` §3's measurement, in the paper's declines section; C118 still holds the six code
sites to the register.

**X26** — discharged: DD228 item 4 reports it among the limits, with D13 §9.2's numbers.

**X7**: no prediction below is about a number this package produces. **X15**: DD225 says what
the marker cannot do. **X16**: DD227's figure check is the experiment that would find a quoted
number no package recorded.

## 3. Bars

| Bar | Holds |
|---|---|
| **C213** | This document's rules as written, the registered marker, and C158's declared set including this document with DD225's reason |
| **C214** | DD226: `claims_table()` renders every Paper 1 row of `CLAIMS` and no Paper 2 row; withdrawn rows name their successors; exactly H1, H2, H5, H6, H7 and `SCENARIO_SIGNS` read **awaiting the read**; the paper's block equals the render |
| **C215** | DD227: every figure appears in its source document and in the paper |
| **C216** | DD228 and DD229: the paper's limits open with 0.906494022, and every limit and decline named above is present in order |
| **C217** | DD230: no forbidden phrase in the paper or in `readout.py`'s rendered strings; a planted imperative is found |
| **C218** | The tally the abstract states is computed from `CLAIMS`, and the paper's abstract carries it |

`MODULES` gains `deskcraft.readout`.

## 4. Predictions

| | Prediction |
|---|---|
| **P1** | Of Paper 1's live rows, 6 are scored today: 4 as predicted (H3, H4a, H4b, H9), 1 against (H8a), and 1 reported without a prediction (H8b) |
| **P2** | The first full render finds at least one figure the paper quotes that its source document states differently, because figures have been copied between documents for three weeks |

## 5. What this could still get wrong

- **A rendered table is only as right as the register.** C32 holds `CLAIMS` to the build order's §5,
  and this adds nothing there.
- **Prose is not rendered.** The paper's paragraphs are written by hand, and only its table, its
  tally and its figures are held by bars. A sentence can still mislead, and a reviewer is the check
  for that.

---

## 9. Result

*Written after the first render, 2026-09-28. Suite 221 → **227**, bars C213–C218. The paper is
`docs/PAPER1_the_engine_and_its_backtest.md`.*

| | Prediction | Outcome |
|---|---|---|
| P1 | 6 of 12 live rows scored: 4 as predicted, 1 against, 1 reported | **HELD** — exactly (C218) |
| P2 | The first render finds a mis-copied figure | **WRONG, and not blind.** All nineteen figures appear in their source documents as the paper writes them. Each had been found in its document before this prediction was written, so the prediction was not blind and its failure says little: X7's case, recorded rather than removed |

**What the render shows.** Twelve live rows: H3, H4a, H4b and H9 as predicted; H8a against its
prediction; H8b reported. H1, H2, H5, H6, H7 and `SCENARIO_SIGNS` read **awaiting the read**. The
abstract carries the tally the register gives, and when the read adds five verdicts to `CLAIMS`,
C214 and C218 go red until the paper is rendered again.

**D16 lands after the read**, in the commit that re-renders the paper with D12, D14 and D15's verdicts
and the figures their results record, removes this document's marker, and tags CP-2.

*Next free ids: ~~**C219 / DD231 / X27**~~ — see §10.*

---

## 10. Landed, 2026-09-28

*Written in the landing commit, after D12, D14 and D15 landed on the out-of-sample read
(`d27331a`, tagged CP-1; the joint registration's §13).*

**The re-render.** `CLAIMS` now holds the read's five verdicts and `SCENARIO_SIGNS`' report, and
the paper's claims table is the render again. **All twelve live rows are scored: seven as
predicted, three against their predictions (H6, H7 and H8a), and two reported (H8b and
`SCENARIO_SIGNS`).** None awaits the read. This document's marker is removed, C158's declared set
loses it, and the commit is tagged **CP-2**: Paper 1 is complete (`AMENDMENT_A1` §7.1).

**What else the landing did, stated, because DD225 said the landing commit re-renders the paper
and does nothing else.** The table and the tally are the render. Beyond them:

1. **The abstract, §3 and §4 carry the read's results in prose**, each figure added to `FIGURES`
   with the joint registration's §13 as its source, so C215 checks fourteen more numbers.
2. **`tally_sentence` was wrong for a register with nothing awaiting.** Its last clause would
   have rendered *"No await the out-of-sample read."* It is now dropped when nothing awaits, and
   more than one row against a prediction is written in the plural. The counts did not change.
3. **A word was wrong in four places.** The read's §13.5, CP-1's page, the register's comment on
   H7 and two build-order cells called 2022's P&L a *loss*. The constructed book is short duration,
   so 2022's rising rates were a **gain** of 15.54m, and H7 reads the magnitude. Corrected in each
   place, with no number moved.
4. **X26 closes**: limit 4 reports it with D13's numbers. **X20 stays open**, as C118 requires
   while six code sites still defer the cross-market leg. Its decline is written in the paper.

Bars C213, C214 and C218 move to their landed branches. The marker is gone and D16 is closed.
No row awaits the read, and the six that did carry the read's verdicts. The tally is
twelve / twelve / seven / three / two / none.

*Next free ids: ~~**C221 / DD240 / X27**~~ — see §11.*

---

## 11. Paper 2, rendered the same way, 2026-09-28

> **DD241 — Paper 2 is rendered from the register as Paper 1 is.** `AMENDMENT_A1` §7.2 makes the
> hedging layer its own paper: D17, D18, D21 and D22, and hypotheses H11 to H17. It is written in
> `docs/PAPER2_hedging_measured_exposure.md` under this package's rules, because `readout.py` is
> this package's: `claims_table(paper_two_claims())` renders its table between its own two
> markers, `paper_two_tally_sentence()` states its count, and `FIGURES_TWO` names the document
> behind each number it quotes. A claim refused by name renders as **NOT_PERFORMED** and is
> counted apart from those scored as or against a prediction. `READERS` gains D21 and D22, whose
> verdicts are the out-of-sample read's. Paper 1 has no claim of theirs, so its table and tally
> do not move, and C214 and C218 hold that. Paper 2 is not a package, and the budget stays
> twenty-one.

Bar **C222** holds Paper 2 the way C214, C215 and C217 hold Paper 1: the block is the render,
the rows are exactly Paper 2's, each figure is found in its source and in the paper, and no
forbidden phrase appears. It also holds which rows await the read. Today those are D21's three,
H12a, H14a and H14b, because D21's replay stopped at Alpha Vantage's free daily cap with 25 of
its 35 weekly series kept. When D21 lands none await, and the bar's expectation follows
`closed("D21")` rather than a date. **The draft is complete except for those three rows** and
the paragraph that will say what they found.

*Next free ids: **C223 / DD242 / X27**.*
