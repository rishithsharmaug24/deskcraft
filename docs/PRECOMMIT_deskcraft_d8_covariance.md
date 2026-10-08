# D8 — the covariance, and the leg the grammar cannot say

*Written 2026-09-25, at `ab92a46`, after DD140 landed the credit tier. Bars and predictions are fixed
here before any covariance is fitted. §9 is written after the run.*

`BUILD_ORDER_D3_D16.md` §4 commissions: *"Sample primary; Ledoit–Wolf, EWMA and crisis-window
variants as robustness. All take a `FitWindow`."* DD139 widened it: the covariance carries `DEXUSEU`
as a **risk factor**, because `US_CASH_BOOK` holds `eurusd`. D8 scores no claim. It owes six carried
items (X2, X6, X11, X18, X22, X25), pre-registered in `RIDER_DD119_steps_4_to_6_pre_registered.md` §1.

---

## 0. Measured before decided

Inputs only; nothing below is a fitted number.

| | Measured | Value |
|---|---|---|
| 1 | DEV sessions / complete across the eight nominal zeros | 7,044 / **6,735** |
| 2 | Complete across `US_CASH_BOOK`'s five series (`SVENY02`, `SVENY05`, `SVENY10`, `DFII5`, `DEXUSEU`) | **2,998**, first 2003-01-02 |
| 3 | Series that bind row 2 | `DFII5` opens 2003-01-02; `DEXUSEU` opens 1999-01-04 and ends 2014-12-24 |
| 4 | NBER recessions inside DEV | 1990-07 → 1991-03, 2001-03 → 2001-11, 2007-12 → 2009-06 |
| 5 | — complete sessions, nominal eight | 185 / 188 / 395 |
| 6 | — complete sessions, the book's five | **0 / 0 / 395** |
| 7 | `GZ_SPREAD` | 323 month-start labels, 1988-01 → 2014-11, in percent |
| 8 | `BAA10Y`, `AAA10Y` (DD140) | 6,753 sessions each, daily, same grid |

Row 6 is the consequence to state first: **the book's crisis variant exists in exactly one window.**
A covariance over a series set the window does not observe is refused by name, never shortened.

---

## 1. What D8 builds

`src/deskcraft/covariance.py`. One result type, `Covariance`: series, unit per series, method,
frequency, the `FitWindow`, observations, rows dropped for completeness, the shrinkage intensity
where one exists, and the matrix as nested tuples (hashable, DD9). Every estimator takes a
`FitWindow` and a series tuple; none takes raw dates.

| Decision | Content |
|---|---|
| **DD141 — units** | A yield or spread moves in **basis points**: 100 × the change in its published percent. `DEXUSEU` moves in **percent log-return**: 100 × ln(Sₜ/Sₜ₋₁). A series with no unit row is refused by name (DD49's shape). Changes are taken over **consecutive complete-case rows** of the requested set, which is `factors.fit_spectrum`'s treatment, so a holiday is spanned the way a weekend is. |
| **DD142 — Ledoit–Wolf target** | **Constant correlation** (Ledoit & Wolf 2004, *Honey, I Shrunk the Sample Covariance Matrix*), not the scaled identity, **computed on standardised changes and rescaled**. The units are mixed (bp and percent). An identity target makes the result depend on the unit; so does the intensity itself on raw data, because their loss is a Frobenius norm and the high-variance unit dominates it (found while implementing, before any fit). On standardised changes the target keeps each variance, shrinks correlations toward their mean, and the whole estimator is scale-equivariant. Intensity is their closed form, clipped to [0, 1], on the 1/T second moment their derivation uses. |
| **DD143 — EWMA** | RiskMetrics (1996): λ = **0.94** daily, **0.97** monthly, zero mean, weights normalised over the finite sample, as of the window's last observation. Constants, not tuned. |
| **DD144 — crisis windows** | The **NBER recessions dated inside DEV**, from the first day of the peak month to the last day of the trough month (row 4). A published chronology with one answer, so no window is picked by what it shows. Each is a `FitWindow`. |
| **DD145 — the monthly companion** (DD130's mechanism) | A daily series enters a monthly covariance at its **last observed session of each month**, labelled with that month's start, the label `GZ_SPREAD` carries. Downsampling is lawful; upsampling is refused. Month-average sampling is named and not taken: it smooths the daily series and a monthly credit observation does not smooth back. |

The **sample** covariance is primary. The variants are robustness and are never substituted because
they look better; that sentence is BUILD_ORDER §6's first bullet, applied here.

---

## 2. Carried items

**X22** — discharged: the branch taken is the first, a `readable` predicate and a second axis
(`Derivation`), built by DD136. D8 is the first package to **act** on it: every estimator refuses a
series whose `Source.readable` is false, by name. `Licence` did not gain a sixth member (DD131).

**X25** — discharged: `VIXCLS`'s `notice` is regraded `REDISTRIBUTION_PROHIBITED` from Cboe's own
terms (reproduction, distribution and derivative works all need prior written consent). The
`VIX_History.csv` fallback is withdrawn, with the premise it rested on stated as false: its page
states no terms inline and links to terms that bind. The row's disposition stays `REFUSED`, now on
both axes independently.

**X11** — discharged: the impact term takes a caller-stated `MarketDepth` with its basis named
(DD128). FR 2004B is not fetched, pinned or committed. The financing term stays absent, and `DFF` is
recorded as the series `sources.py` would grade if the term were ever wanted. `total` keeps refusing
on all 231 structures. The weekly-to-annual question does not arise, because a stated depth has no
frequency.

**X2** — discharged: **DD130**, one frequency per covariance. A daily fit refuses a monthly series by
name, naming forward-filling as the refused act. `GZ_SPREAD` is fitted in the monthly companion
(DD145). DD140 changed the premise the item was written on: daily Moody's credit is now committed,
in its own file, so a daily credit risk factor is available to the daily covariance and needs no
resampling. `CREDIT_VS_RATES`'s stated contrast stays `GZ_SPREAD` (DD124); D8 does not edit the
grammar (DD138). X2's four-class half stays with D17, unchanged.

**X18** — discharged: not owed on the route taken. X11's data half landed as a decision that adds
no cost term, so `cost_per_dv01` still returns the spread term alone and D7b's eight cells are
unmoved. **Trigger:** if any later package makes `cost_per_dv01` return more than the spread term,
the eight cells are re-measured before any count from them is quoted again. C113 and C114 hold the
arithmetic meanwhile.

**X6** — discharged: the three orientation statistics are run on each of the four windows D8 fits
(DEV and the three NBER windows), signs recorded with window lengths, and the rider's prediction is
scored in §9 as written:
(a) PC1 stable in every window; (b) **PC2 flips in at least one window**; (c) PC3, none offered.

**X7** — discharged: every prediction in §4 is about a quantity that exists before or independent
of its own verification. **X15** — discharged: D8 registers no threshold. **X16** — discharged: §6
states one impossibility (the book has no crisis covariance in 1990 or 2001) with the experiment
that settles it: row 6 above, measured.

---

## 3. Bars

| Bar | Holds |
|---|---|
| **C130** | DD141 + restatement: the DEV sample covariance over the eight nominal zeros is **exactly** the covariance `factors._pca` computes on the same sample, and its eigen-shares reproduce 83.9352% / 97.9021%. D8's primary is the object D6 already used. |
| **C131** | Every estimator takes a `FitWindow`: a raw `date`, a window past DEV, and a series with no unit row are refused. |
| **C132** | DD130/X2: a daily fit naming `GZ_SPREAD` refuses and names forward-filling; the monthly companion fits `GZ_SPREAD` with daily series at month-end (DD145), with at most 323 observations. |
| **C133** | DD142: the LW intensity lies in [0, 1], the target keeps the sample variances, and rescaling one series by k rescales its row and column by k with the intensity unchanged. **Mutation:** an identity-target shrinkage fails the same equivariance. |
| **C134** | DD143: EWMA weights sum to one, decay by λ per session, and λ is 0.94 daily / 0.97 monthly. |
| **C135** | DD144: the crisis windows are the three NBER recessions as dated; the book's five-series set is refused by name in the 1990 and 2001 windows and fitted in 2007–09. |
| **C136** | DD139 + X22: `US_CASH_BOOK`'s five series fit on DEV with `DEXUSEU` in **percent**, and an unreadable series (`VIXCLS`) is refused by the readable predicate, by name. |
| **C137** | X6: the orientation table over the four windows, as measured, with window lengths. |
| **C138** | X25: `VIXCLS` notice is `REDISTRIBUTION_PROHIBITED`, the fallback no longer rests on a page "stating no terms", and the disposition is `REFUSED`. |

`MODULES` gains `deskcraft.covariance`. `ENGINE_IMPORT_ROOTS` is unchanged (`numpy` arrived at D6).

---

## 4. Predictions

| | Prediction |
|---|---|
| **P1** | C130 holds at exact equality, not a tolerance. |
| **P2** | X6 as the rider fixed it: (a) PC1 stable in all four windows; (b) PC2's sign flips in at least one. |
| **P3** | The LW intensity for the book's five series on DEV is **below 0.05**: T/N ≈ 600. |
| **P4** | In the 2007–09 window the correlation of daily changes between `SVENY02` and `SVENY10` is **lower** than on DEV: the front end was driven by policy and the long end by flight to quality. |
| **P5** | `DEXUSEU`'s largest absolute correlation with any of the book's four rate series on DEV is **below 0.31**, the ceiling A7's 0.905 unexplained share implies for one regressor. |
| **P6** | Suite 137 → **146** (nine bars), and one existing bar reddens on the way: C118, because the `VIXCLS` edit moves `sources.py`'s `DEC-2` lines. |

---

## 5. What this could still get wrong

1. Daily bp changes in yields and percent log-returns in FX are **different units in one matrix**.
   Every consumer multiplies by an exposure in matching units, and D9 owns that mapping; a consumer
   reading a variance without its unit reads a number off by a factor of the exchange rate.
2. The crisis variant for the book is **one window**. A statement about "crisis correlations" for
   `US_CASH_BOOK` from DEV is a statement about 2007–09, and D12 is where other crises are replayed.
3. `DEXUSEU` ends 2014-12-24 in the panel, so the book's DEV sample ends five sessions early.

---

## 6. Impossibility stated

The book's five series have **no** complete session in the 1990 or 2001 NBER windows (TIPS open
2003, the euro 1999). Experiment: row 6 of §0, run. Nothing is refused that could have been fitted.

---

## 9. Result

*Written after the run, 2026-09-25. Suite 137 → **146**, 0 failed. `ruff` 0 and `lint-imports`
2 kept / 0 broken, both from their bars.*

| | Prediction | Outcome |
|---|---|---|
| P1 | C130 exact | **HELD** — `np.array_equal`, 6,734 changes, 309 rows dropped |
| P2 | (a) PC1 stable; (b) PC2 flips somewhere | **HELD, both** — PC2 flips in NBER_1990 only |
| P3 | LW intensity < 0.05 on the book's five | **HELD** — 0.0023 at T/N = 599 |
| P4 | 2s10s correlation lower in 2007–09 | **MISSED** — 0.752 in the crisis against 0.745 on DEV |
| P5 | Euro's largest correlation with the book's rates < 0.31 | **HELD** — 0.164, with `DFII5`, negative |
| P6 | 146, and C118 reddens | **HELD** — scored by experiment: the old citation restored gives `1 failed, 144 passed, 1 skipped`, C118 alone |

**9.1 X6 found what it feared.** In the 1990 recession sample PC2's front loading is +0.504 against
−0.326 at thirty years, so curvecast's sign rule points `+PC2` at a **flattening**. The rider's own
worry (§4 item 6) was that a flip in a short window would be right for the wrong cause. NBER_2001 is
as short (187 changes against 184) and did not flip, so length alone does not explain it. What does
distinguish 1990 is that PC2 and PC3 nearly tie (9.65% against 8.62% of variance), and a near-tie is
when an eigenvector's orientation is least determined. Either way the conclusion the rider fixed in
advance follows: **orientation is a property of the sample**, and D6's row carries the qualifier.

**9.2 A defect in this document, caught before the run.** DD142 as first written claimed the
constant-correlation target made Ledoit–Wolf scale-equivariant. It does not: their intensity
minimises a Frobenius loss, which on raw mixed units is dominated by whichever series has the larger
variance in its unit. Found while implementing, corrected before any fit, and C133 now holds the
equivariance with a mutation showing the naive form fails it.

**9.3 P4 missed in the direction that matters to D12.** The front end and the long end moved
*more* together in 2007–09, not less. H6 (D12) predicts crisis correlations change sizing by more
than 20% of gross; on this pair the change is small and in the concentrating direction.

**9.4 Found beside the work.** `IDEATION_before_the_first_oos_read.md` row 7 labelled 97.9021% as
PC1+PC2; it is PC1–3, as D6's pre-commit says (PC1+PC2 is 94.2347%). Corrected in place. And the
admitted daily credit tier is usable by the daily covariance with no resampling: `BAA10Y` against
`SVENY10` correlates at −0.51 on 6,732 changes, mechanically, since it is a spread over that yield.

*Next free ids: **C139 / DD146 / X26**.*
