# D9 — component ES under Euler, and the four flags

*Written 2026-09-25, at `e41b0c3`, after D8 closed. Thresholds, bars and predictions are fixed here
before any book is scored. §9 is written after the run.*

`BUILD_ORDER_D3_D16.md` §4: *"ES 97.5% primary. Euler additivity is a unit test. Exhibit VaR
violating sub-additivity where ES does not. §2's four flags with thresholds pre-registered here."*
D9 scores no claim. It owes **X3**, **X17** and **X19**, pre-registered in
`RIDER_DD119_steps_4_to_6_pre_registered.md` §2.

---

## 0. Measured before decided

At the as-of date D7a and D7b already use, 2014-12-24, from the committed DEV panel:

| Leg | Exposure |
|---|---|
| `us_2y`, short $200m `SVENY02` | +40,000.00 USD per bp |
| `us_10y`, short $60m `SVENY10` | +60,000.00 USD per bp |
| `us_breakeven_5y`, long $50m | +25,000.00 on `SVENY05`, −24,629.33 on `DFII5` |
| `eurusd`, short €75m, `DEXUSEU` = 1.2188 | **−914,100 USD per 1% rise in EUR/USD** |

The fourth row is the one D4's `book_dv01` cannot produce: `FX_SPOT` has rate sense `NONE`, so it
returns no components. DD139 is why D9 produces it.

---

## 1. What D9 builds

`src/deskcraft/attribution.py`.

| Decision | Content |
|---|---|
| **DD146 — the measure** | **ES at 97.5%, Gaussian, on D8's primary sample covariance**, over DEV, is the primary figure: σ = √(e′Σe), ES = σ·φ(z)/(1−α), with z = Φ⁻¹(0.975). Historical simulation over the same DEV changes is reported beside it, never instead. VaR at 97.5% and 99% is reported for comparison. Zero mean, daily horizon. |
| **DD147 — exposure** | A rate leg's exposure is D4's signed DV01 per series, unchanged. An FX leg's is **direction × notional × Sₐₛ₋ₒ𝒻 × 0.01**, USD per 1% log-move (first order, matching D8's `PERCENT_LOG_RETURN`). P&L is in USD. A book holding an unpriceable leg is refused whole, as `sensitivity` already does. |
| **DD148 — Euler** | A leg's component is eᵢ′Σe/σ scaled to the measure; under historical simulation it is the leg's mean loss over the tail scenarios the book's ES averages. Both sum to the total exactly, by homogeneity. |
| **DD149 — F1–F4 thresholds** | **F1 dead weight:** \|component\| < **5%** of book ES. **F2 concentration:** component > **50%**, which is "most" read literally. **F3 off-thesis:** the leg's off-thesis component ≥ **25%** of book ES. **F4 redundancy:** \|partial correlation\| of two legs' P&L, given every other leg, ≥ **0.9**. Reported with the count of legs screened. |
| **DD150 — F3's split** | A leg's exposure is split along the **compiled view target** t̂ (`views.compile_view`, unit-normalised): on-thesis (eᵢ·t̂)t̂, off-thesis the remainder. Euler is linear, so the leg's component splits the same way and the pieces sum to the whole. The covariance is fitted over the union of the book's series and the series t̂ reaches. The geometry is `cosine`'s, which claims no decomposition of the six grammar terms, so the Gram overlaps X3 names never enter. |
| **DD151 — X17** | A declared `DV01` neutrality is **measured, not widened**. `book.py` holds types and no yields, so it cannot compute a duration. Its syntactic invariant stays: it catches a spread written with two `+1`s. Every risk report carries each declared-neutral leg's measured parallel residual. |
| **DD152 — X19** | `generator.select` refuses a view naming a factor whose reach is not wholly inside `CANDIDATE_SERIES`, by name, raising `views.UnreachableFactor`. |

The sub-additivity exhibit is two-part: a **search** over every pair and sub-book of the scored book
under DEV historical simulation at 97.5% and 99%, and the **textbook construction** (two independent
bonds, each defaulting with probability 2% for a loss of 100), computed exactly and labelled synthetic.

---

## 2. Carried items

**X17** — discharged: DD151. The type keeps its syntactic invariant, and the measured residual rides on
the risk report. `US_BREAKEVEN_5Y`'s declared `DV01` is reported with its residual at every scoring.

**X19** — discharged: DD152. The one published `CROSS_MARKET` selection number, cosine **0.707**
(`AMENDMENT_A5` §0 row 10), is restated where it was published: a single US ten-year leg against a
contrast whose German half no candidate reaches. It was a number about `LEVEL`'s overlap, not about
the cross-market term.

**X3** — discharged: the corrected statistic is DD150's split for F3 and a partial correlation for F4;
neither reads `dominant_share`. D7b's ordering is re-scored by re-running all eight cells after
D9's changes.

**X7** — discharged: no prediction's subject is produced by its own verification. **X15** —
discharged: §3 states each threshold's range. **X16** — discharged: none stated.

---

## 3. X15, for the four thresholds

A component share ranges over (−∞, +∞): a hedge contributes negatively and one leg can exceed the
book. F1 admits the band (−5%, +5%). F2 admits (50%, ∞). F3 admits [25%, ∞) of off-thesis share.
F4 admits partial correlations in [0.9, 1] ∪ [−1, −0.9], 10% of the range of each sign. None of
these is a claim; a flag firing is reported with the number of legs screened.

---

## 4. Bars

| Bar | Holds |
|---|---|
| **C139** | DD148: components sum to the total, Gaussian and historical, on `US_CASH_BOOK` and on a synthetic book. |
| **C140** | DD147: rate exposures equal D4's DV01s exactly; `eurusd` is −914,100 USD per 1%; every one of the four legs carries non-zero risk. |
| **C141** | The exhibit: the textbook pair gives VaR(a+b) = 100 > 0 = VaR(a)+VaR(b) and ES 101.6 ≤ 160; the DEV search's count is held as measured. |
| **C142** | DD149: the thresholds are the constants above; the flags on `US_CASH_BOOK` are held as measured. |
| **C143** | DD150: on + off = component for every leg; `eurusd`'s on-thesis part is exactly zero. |
| **C144** | DD151/X17: the breakeven's residual is 370.67 per bp and 1.483%; `book.py`'s invariant is unchanged. |
| **C145** | DD152/X19: `select` refuses `CROSS_MARKET` and `CREDIT_VS_RATES` by name; the reference view is untouched. |
| **C146** | The headline numbers for `US_CASH_BOOK` and the generated headline book, as measured. |

`MODULES` gains `deskcraft.attribution`. `ENGINE_IMPORT_ROOTS` gains **`statistics`**, for
`NormalDist.inv_cdf`: the inverse normal is not in numpy, and a hand-rolled one is a second
implementation of a standard function. Not a capability any of the six bans reaches.

---

## 5. Predictions

| | Prediction |
|---|---|
| **P1** | Euler holds to 1e-10 relative, both methods. |
| **P2** | **`eurusd` is the largest contributor to `US_CASH_BOOK`'s ES**, above 40%. The leg the source called the diversifier carries the most risk. |
| **P3** | F3 fires on `eurusd`: its whole component is off-thesis, because a `LEVEL UP` view has no FX direction. |
| **P4** | F4 fires on no pair: the 2y and 10y shorts correlate 0.74 raw and less given the others. |
| **P5** | Historical ES exceeds Gaussian ES for the book, by a factor between 1.0 and 1.5. |
| **P6** | The DEV search finds **no** VaR sub-additivity violation: linear legs on near-elliptical changes. |
| **P7** | X3: the surviving leg set is unchanged at all eight cells (C105 stays green unedited). |
| **P8** | X19's refusal moves no bar's pinned number. |
| **P9** | Suite 146 → **154** (eight bars). The only existing bars this commit must edit are C1's module census and C27's import census. |

---

## 5a. What this could still get wrong

1. The Gaussian primary is thin-tailed by construction; P5 exists to measure by how much.
2. The FX delta is first order. A 10% move in EUR/USD misstates P&L by about 5% of the move.
3. F3's split depends on the view. Under `REFERENCE_VIEW_TWO_TERM` the on-thesis direction moves, and
   both are reported so the choice cannot be made after seeing which flags fire.

---

## 9. Result

*Written after the run, 2026-09-25. Suite 146 → **154**, 0 failed; `ruff` 0 and `lint-imports`
2 kept / 0 broken from their bars. `US_CASH_BOOK`, DEV 2003-01-02 → 2014-12-24, 2,997 changes.*

| | Prediction | Outcome |
|---|---|---|
| P1 | Euler to 1e-10, both measures | **HELD** — sums are exact to the float |
| P2 | `eurusd` the largest contributor, above 40% | **HELD** — **47.7%** Gaussian, 44.2% historical |
| P3 | F3 fires on `eurusd` | **HELD** — its whole component is off-thesis, 47.7% of book ES |
| P4 | F4 fires on no pair | **HELD** — largest partial is 2y/10y at 0.727 |
| P5 | Historical ES / Gaussian ES in (1.0, 1.5) | **HELD** — 2,279,505 / 1,946,957 = **1.171** |
| P6 | No VaR sub-additivity violation on the book | **HELD** — 0 of 11 sub-books (2⁴ − 1 − 4) × 2 levels |
| P7 | X3: leg sets unchanged at all eight cells | **HELD** — C105 green, unedited |
| P8 | X19 moves no pinned number | **HELD** |
| P9 | 154, only C1 and C27 edited | **HELD** |

| `US_CASH_BOOK`, reference view | component ES | share | on-thesis | off-thesis |
|---|---|---|---|---|
| `us_2y` | 335,463 | 17.2% | 345,256 | −9,793 |
| `us_10y` | 601,342 | 30.9% | 579,366 | 21,976 |
| `us_breakeven_5y` | 81,843 | **4.2%** (F1) | 256,130 | −174,286 |
| `eurusd` | 928,308 | **47.7%** | 0 | 928,308 (F3) |
| **book** | **1,946,957** (Gaussian ES 97.5%) | | | |

**9.1 The diversifier is the risk.** The source justified `eurusd` as the leg that profits from a
different aspect of the thesis. Measured, it is the largest single risk in the book and none of it
points along the view. DD139 put the euro into D8's covariance because a DV01-only figure would have
carried it at zero. Without it the book's ES is 1,403,920 against 1,946,957, **understated by
27.9%**, and the leg that contributes most would not appear at all. (The two figures agree: the euro
is nearly uncorrelated with the rates legs, so its 47.7% share is close to its share of variance,
and ES scales with the square root of variance: 1 − √(1 − 0.477) ≈ 27.7%.) F2 did not fire, at 47.7% against 50%.

**9.2 The breakeven is dead weight, and that is the hedge working.** Its on-thesis part (+256k) and
off-thesis part (−174k) nearly cancel: the nominal leg adds level risk and the real leg hedges most
of it back. What is left is 4.2% of the book, with D4's 370.67/bp residual riding beside it (C144).

**9.3 Found and not predicted: the generated headline book is one bet.** At D7b's headline cell the
book is a short 30-year outright plus a short 10s30s spread. The spread contributes **−111%** of ES,
a hedge, and the outright **211%** (F2). Their P&Ls correlate at **−0.954** (F4). The greedy took the
spread to cancel the outright's off-level exposure, so the two legs are one position. This is F3's
mechanism, recorded by D7b's own docstring ("a leg earns its place by cancelling off-thesis
exposure"), now measured in risk rather than in angle.

*Next free ids: **C147 / DD153 / X26**.*
