# D10 — the effective number of bets, on three rungs, each with its basis named

*Written 2026-09-25, at `58db0c4`, after D9 closed. Bars and predictions fixed before the run; §9 is
written after it.*

`BUILD_ORDER_D3_D16.md` §4: *"All three of the ladder, each with its basis named. Carries H4 and
H8."* H4 and H8 were withdrawn and split by `AMENDMENT_A3` (DD93–DD95), so D10 scores **H4a, H4b,
H8a and H8b**. It owes no carried item.

---

## 0. Measured before decided

- The ladder is curvecast item 28's, restated: **Roy–Vetterli** effective rank (exp-entropy of the
  covariance's eigenvalue shares), **volatility-preserving minimum torsion** (whose factor variances
  are the marginal variances, by identity), and **plain whitening** (every factor variance 1). On
  eight GSW zeros over DEV item 28 reports **1.8231 / 7.9059 / 8.0000**.
- **Whitening returns the leg count exactly, whatever the covariance.** For a four-leg book that is
  4.0. `AMENDMENT_A3` §4.1 says so, and §6 then calls H4b *"the one that can be surprised"*. It
  cannot: H4b asks for > 3.0 under **at least one** other rung, and the whitening rung is 4.0 by
  construction. Found here before the run; see §3.
- D9 measured the generated headline book's two legs at a correlation of **−0.954**.

---

## 1. What D10 builds

`src/deskcraft/bets.py`: `effective_rank` (restated from curvecast), the three-rung ladder on any
covariance, and a book's **leg P&L covariance** E Σ Eᵀ, where E is D9's exposure matrix and Σ is
D8's primary.

| Decision | Content |
|---|---|
| **DD153 — a claim with no prediction is scored by being reported** | `Verdict.REPORTED` joins the enum. It is the only verdict a claim registered with `predicted=None` may carry, and a claim with a prediction may never carry it. H8b takes it; `SCENARIO_SIGNS` will at D12. PASS on a report would read as a prediction coming true. |
| **DD154 — one covariance for a comparison** | Where two books are compared (H8a), Σ is D8's primary over the **union** of both books' series, and each book's leg covariance is derived from it. The same sample, so the ranking cannot come from two different samples. |
| **DD155 — which generated book** | H8a is read off **D7b's headline cell**, 1× under `AS_QUOTED` at `VIEW_MOVE_BP = 1.0`, which D7b named its headline before D10 existed. The other seven cells and a 10 bp book are reported beside it with no verdict. |

---

## 2. Carried items

**X7** — discharged: every prediction below is about a number that exists before its verification.
**X15** — discharged in §3. **X16** — discharged: §3's statement that H4b cannot fail arrives with
its experiment, the whitening identity, run in C149.

---

## 3. X15 for the four claims, and the one that cannot fail

| Claim | Quantity and range | Threshold | Admits |
|---|---|---|---|
| H4a | Roy–Vetterli rank of a 4×4 covariance, [1, 4] | < 3.0 | two thirds of the range, 75% of its maximum |
| H4b | the largest of the two non-PCA rungs, [1, 4]; **the whitening rung is exactly 4** | > 3.0 | **100%: it cannot fail** |
| H8a | a ranking of two ranks | none | — |
| H8b | a ratio, reported | none | — |

**H4b is scored as written, not withdrawn.** It is withdrawn-shaped (DD95's shape), but withdrawing a
claim at the package that scores it would be the scorer choosing its own bars. H9's precedent is
the one that applies: scored, with the range beside the verdict. D10 also reports what H4b was
written to ask. **Min-torsion is the rung that can move**, and it is reported with its own
comparison to 3.0 and no verdict.

---

## 4. Bars

| Bar | Holds |
|---|---|
| **C147** | The restatement: on D8's DEV covariance of the eight zeros, the ladder is 1.8231 / 7.9059 / 8.0000 to four places, and min-torsion's factor variances equal the marginal variances. |
| **C148** | H4a: the `US_CASH_BOOK` ladder as measured, and its verdict in `CLAIMS`. |
| **C149** | H4b: whitening equals the leg count for any book (a synthetic 3-leg and the 4-leg), so the PASS carries no information; min-torsion as measured. |
| **C150** | H8a: both books on DD154's one covariance, D7b's headline cell, and the verdict. |
| **C151** | DD153: `REPORTED` only on a claim with no prediction; H8b's ratios reported. |
| **C152** | The rest of the ladder: every cell's rank and the 10 bp book, without a verdict. |

`MODULES` gains `deskcraft.bets`.

---

## 5. Predictions

| | Prediction |
|---|---|
| **P1** | C147 reproduces item 28 to four places. |
| **P2** | **H4a PASS**, as the register predicts: the book's rank is about 2.4, because the euro and the rates block are two roughly equal and uncorrelated bets and the breakeven is small. |
| **P3** | **H4b PASS, but only on the whitening rung.** Min-torsion is below 3.0, because the euro and the 10-year dominate the marginal variances. |
| **P4** | **H8a does not hold, against the register's PASS.** The generated headline book's rank is below 1.5, because D9 measured its two legs as one bet. |
| **P5** | Suite 154 → **160**. C32 and C34 redden until the §5 rows and the verdicts land in this commit. |

---

## 9. Result

*Written after the run, 2026-09-25. Suite 154 → **160**; `ruff` and `lint-imports` green from their
bars. One covariance throughout (DD154): D8's primary over the union of both books' series,
2003-01-02 → 2014-12-24, 2,997 changes.*

| | Prediction | Outcome |
|---|---|---|
| P1 | Item 28 reproduced to four places | **HELD** — 1.8231 / 7.9059 / 8.0000, torsion = marginal |
| P2 | H4a PASS, about 2.4 | **HELD** — **2.4103** |
| P3 | H4b PASS only on whitening; min-torsion under 3.0 | **HELD** — whitening 4.0, min-torsion **2.6567** |
| P4 | H8a does not hold; generated rank under 1.5 | **HELD** — **1.0898** against 2.4103: **refuted** |
| P5 | 160, with C32 and C34 red until the verdicts land | **HALF** — 160 held. C32 never reddened. C34 did, but on its **mutation arm**, a hand-written list of unbacked verdicts that D10's four made stale; now derived from the register. C152 also reddened, on my test fitting each cell on its own series rather than DD154's |

| Claim | Verdict | Number |
|---|---|---|
| H4a | **PASS** | Roy–Vetterli 2.4103 < 3.0 |
| H4b | **PASS**, vacuously | whitening 4.0 by construction; min-torsion 2.6567 |
| H8a | **refuted** (`FAIL` in `CLAIMS`) | generated 1.0898 < hand-built 2.4103 |
| H8b | **REPORTED** | 0.6026 hand-built, 0.5449 generated |

**9.1 H8a asked the generator to do the opposite of its job.** The reference view is one term,
`LEVEL UP`. A book with high fidelity to a one-factor view *should* be one bet; the greedy adds a leg
by cancelling off-view exposure, which D9 measured as a −0.954 correlation between the two legs.
Diversification and fidelity to a narrow view pull opposite ways, and H8a predicted the generator
would win on the axis it was never optimising. Even at a realistic 10 bp magnitude, where the book
has six legs, its rank is 1.3155. **This is the one claim so far the register predicted wrongly on
the finance.**

**9.2 H4b is the fourth claim this plan registered that could not fail.** H14's conjunction (A1),
H8's level clause (A3), H9's grid (D7b), and now H4b's disjunction over a rung that returns the leg
count by construction. A3 stated the identity in §4.1 and, two sections later, called H4b the claim
that "can be surprised". Scored as written, with the range in §3, so no bar is invented at scoring.

**9.3 The sample moves the rank.** The same headline book on its own two series, whose complete-case
sample starts in 1988 rather than 2003, ranks 1.111 instead of 1.0898. C152 holds both. A comparison
of two books is only a comparison on one covariance.

*Next free ids: **C153 / DD156 / X26**.*
