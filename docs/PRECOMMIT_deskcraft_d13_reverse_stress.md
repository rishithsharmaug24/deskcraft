# D13 — reverse stress: the smallest plausible move that breaches a stated loss

*Written 2026-09-28, after D22's code (joint registration §11) and before any number below §8 is
computed. Rules, bars and predictions are fixed here; §9 is written after the run. D13 reads DEV
only, scores no claim and owes no carried item, so it lands with its run.*

`BUILD_ORDER_D3_D16.md` §4: *"Reverse stress. Smallest plausible joint move breaching a stated loss
tolerance."* `PLAN_deskcraft.md` §5.4: *"Rather than 'what does 2008 do to this book?', ask 'what is
the smallest, most plausible joint move that breaches the loss tolerance?' This finds the
structure's actual weak axis, which is frequently not the one the thesis is about."*

---

## 0. What D13 does, in one paragraph

A risk budget says how much a book may lose. D13 turns the question round: of every move of the
market that would lose that much in one day, which is the most likely, and what does it look like?
Under a Gaussian model the answer has a closed form, and §2 shows before any run that on one
covariance it is **D9's Euler decomposition under another name**. So D13's content is what the
closed form cannot give: the same breach under D8's other covariances (the construction date's
EWMA, Ledoit–Wolf, the crisis windows), and the breaches that actually happened in DEV. Does the
weak axis move when the covariance does, and does history breach the budget where the model says
it will?

## 1. What it rests on

| | |
|---|---|
| Covariances | D8, `covariance.fit` and `fit_crisis`: `SAMPLE` primary, `LEDOIT_WOLF`, `EWMA` (λ 0.94, its estimate at the fit window's end), and the NBER windows inside DEV, each refused by name where the book's series do not reach it |
| Exposures | D9, `attribution.leg_exposure`: a rate leg's signed DV01 per basis point, an FX leg's USD P&L per 1% log move, in the units D8's covariance carries |
| The budget | D11, `sizing.RISK_BUDGET_ES` = $1,000,000, Gaussian ES at 97.5%, and the joint registration §2's rule (DD158): **every book is scaled to the budget on the `SAMPLE` covariance** |
| The books and window | The joint registration §2: `US_CASH_BOOK` and the constructed headline book (D7b's cell for `REFERENCE_VIEW`), both at **2014-12-24** on `readers.REAL_FIT`, 1988-01-01 → 2014-12-24 |
| The view | `views.REFERENCE_VIEW`, `LEVEL` up, compiled on the fit window's basis (D9's DD150 split) |

## 2. The rules

> **DD220 — the stated loss is the budget, in one session.** Each book is scaled so that its
> Gaussian ES at 97.5% on `SAMPLE` over the fit window is `RISK_BUDGET_ES`, and **L = $1,000,000
> lost in one session**. The budget is the only loss this repository has stated for a book, and the
> daily horizon is D9's and D14's. No second tolerance and no second horizon is computed, so none
> can be chosen.

> **DD221 — the most plausible breach, and why on one covariance it is D9.** With exposure e (USD
> per unit move of each series) and covariance Σ of daily changes, the loss of a move Δ is −e·Δ.
> The move of smallest Mahalanobis distance √(Δ′Σ⁻¹Δ) that loses L is
>
> ```
> Δ*  =  −L · Σe / (e′Σe),        distance  d  =  L / √(e′Σe)
> ```
>
> (Lagrange, one line: minimise Δ′Σ⁻¹Δ subject to e·Δ = −L). Three consequences, stated before any
> run:
>
> 1. **The loss Δ* puts on series i is L·eᵢ(Σe)ᵢ / (e′Σe)**, so its share is eᵢ(Σe)ᵢ / (e′Σe):
>    **D9's Euler share, exactly**, series by series and so leg by leg. On one Gaussian covariance,
>    reverse stress finds the weak axis D9 already reports.
> 2. **On `SAMPLE`, d is the same for every book**: the book is scaled so that
>    √(e′Σe)·φ(z)/(1 − α) = L, so d = φ(z)/(1 − α) = **2.3378** at α = 97.5%. The budget loss is
>    2.34 sample sigmas by construction.
> 3. **The on-thesis share of the breach is D9's on-thesis share** (DD150), because both are the
>    same linear split of the same vector.
>
> C209 holds all three to 1e-12, which is X16's refuting experiment: a share differing from D9's
> would show the closed form wrong. What D13 adds is DD222 and DD223.

> **DD222 — the same breach on the other covariances.** For each of `LEDOIT_WOLF`, `EWMA` and every
> NBER window inside DEV that the book's series reach, the scaled book's exposure is held and Σ is
> replaced. Reported for each: **d_C = L / √(e′Σ_C e)**, the budget loss in that covariance's own
> sigmas; the scenario Δ*_C, series by series; **its distance under `SAMPLE`**, √(Δ*_C′Σ_S⁻¹Δ*_C),
> which is at least 2.3378 by the optimality of Δ*_S, and says how implausible the crisis-shaped
> breach looks to the model the budget was set on; the per-series shares; the on-thesis share; and
> **the cosine between Δ*_C and Δ*_S**, which says whether the weak axis moved. A window the book's
> series cannot see is refused by name (D8 refuses 1990 and 2001 for a book holding TIPS or the
> euro) and never replaced.
>
> **Which series, stated.** Every covariance is fitted over **D9's series set**: the union of the
> book's series and those the view reaches (DD150). So `SAMPLE` is D9's matrix exactly, and
> Ledoit–Wolf, whose shrinkage depends on the whole set, is fitted on the same one. **Every distance
> and every scenario is taken over the series the book holds**, on the covariance's block for them.
> The closed form's distance is the same in either space, because e is zero off the held series. The
> view's other series enter only the on-thesis share, as in D9. **The cosine is taken in `SAMPLE`'s
> own metric**, Δ₁′Σ_S⁻¹Δ₂ over the product of the two distances. A plain cosine over basis points
> and a percent would move with the choice of unit, and this one cannot.

> **DD223 — the breaches that happened.** Over the fit window's daily changes, the sessions on which
> the scaled book lost at least L. Reported: **their count** against the Gaussian expectation
> T·(1 − Φ(2.3378)); and **the most plausible of them**, the breach of smallest distance under
> `SAMPLE`, with its date, its distance and its move series by series. The changes are the ones
> `SAMPLE` was fitted on, so this is in sample, and says only whether the Gaussian model's tail
> matches the data it was fitted to. D14 is the out-of-sample test.

> **DD224 — `US_CASH_BOOK`'s euro is kept.** DD139 put `DEXUSEU` in D8's covariance because a
> DV01-only figure carries the euro leg at zero, and D9 measured it at 47.7% of the book's ES. A
> reverse stress without it would find a rates-only weak axis for a book whose largest risk is not
> rates. The constructed book holds only GSW zeros.

## 3. Carried items, and what this touches

D13 owes no item in `CARRIED_ITEMS.md`. **X7**: every prediction below is about a number that does
not exist yet. **X15**: §2 states the attainable range: d on `SAMPLE` is a constant, the shares on
`SAMPLE` are D9's, and a cosine lies in [−1, 1]. **X16**: DD221's identity is held by a bar, and the
experiment that would refute it is that bar. D13 scores no claim, so C34 asks nothing of it.

## 4. Bars

| Bar | Holds |
|---|---|
| **C208** | This document's rules as written: DD220–DD224 and the predictions table, and D13 has no claim in `CLAIMS` |
| **C209** | DD221: on a synthetic covariance and on both real books, Δ* loses exactly L, has distance L/√(e′Σe), no move losing L is nearer (checked against random directions), and the per-series and per-leg shares equal D9's Euler shares, and the on-thesis share D9's, to 1e-12. On `SAMPLE` d = φ(z)/(1 − α) for both books |
| **C210** | DD222: every covariance a book's series reach is reported, every other is refused by name; each scenario's `SAMPLE` distance is at least the `SAMPLE` scenario's; a cosine of the `SAMPLE` scenario with itself is 1 |
| **C211** | DD223: the breach count and the most plausible breach on a synthetic panel whose answer is known; the reported breach loses at least L and none of the other breaches is nearer under `SAMPLE` |
| **C212** | The run on DEV reproduces §9's table |

`MODULES` gains `deskcraft.reverse`.

## 5. Predictions

| | Prediction |
|---|---|
| **P1** | DD221 holds: d = 2.3378 on `SAMPLE` for both books, and the shares are D9's to 1e-12. *An identity, recorded so that its bar is scored like the others* |
| **P2** | On the `NBER_2007` covariance, `US_CASH_BOOK`'s budget loss is **fewer than 2.3378** crisis sigmas: the crisis covariance is wider than DEV's average |
| **P3** | On the construction date's `EWMA`, `US_CASH_BOOK`'s budget loss is **more than 2.3378** sigmas: late 2014 was calmer than 2003–2014's average for this book |
| **P4** | **The euro carries the largest share** of `US_CASH_BOOK`'s breach on every covariance that reaches it |
| **P5** | `US_CASH_BOOK`'s `NBER_2007` scenario has a cosine **above 0.9** with its `SAMPLE` scenario: the weak axis does not move much for a book whose risk is one currency and one curve |
| **P6** | The count of DEV sessions on which `US_CASH_BOOK` lost at least L **exceeds the Gaussian expectation**: D9 measured historical ES at 1.171 times Gaussian, so the tail is fatter than the model's |
| **P7** | The constructed book's `SAMPLE` breach moves **every zero it holds the same way**: it breaches on level, the axis of its own thesis |

## 6. What this could still get wrong

- **The Gaussian closed form is the model's own answer.** A reverse stress under the model the budget
  was set on cannot find a weak axis the model does not already see; DD221 says so. DD222 and DD223
  are the parts that can surprise, and DD223 is in sample.
- **"Plausible" is Mahalanobis distance under one covariance.** A crisis-shaped breach is scored by
  the sample model's distance, which is the question a desk asks of its own model. It is not a
  probability of the crisis.
- **Crisis windows are short.** `NBER_2007` is about 390 sessions; a five-series covariance over it
  is estimable, and a shorter window would not be. D8's refusals stand.

---

## 9. Result

*Written after the run, 2026-09-28. Both books scaled to the budget on `SAMPLE` over `REAL_FIT`;
`US_CASH_BOOK`'s changes run 2003-01-02 → 2014-12-24 (2,997, because `DFII5` opens in 2003), and the
constructed book's 1988 → 2014-12-24 (6,730). Bars C208–C212.*

| | Prediction | Outcome |
|---|---|---|
| P1 | DD221's identity | **HELD** — d = 2.3378 on `SAMPLE` for both books; leg shares and on-thesis share equal D9's to 1e-12 (C209) |
| P2 | `NBER_2007` below 2.3378 | **HELD** — **1.5455** |
| P3 | Construction-date `EWMA` above 2.3378 | **WRONG** — **2.2938**. Right about volatility and wrong about the book: §9.1 |
| P4 | The euro the largest share everywhere | **HELD** — 47.7% `SAMPLE`, 47.7% Ledoit–Wolf, **54.7% `EWMA`**, 42.4% `NBER_2007` |
| P5 | `NBER_2007` cosine above 0.9 | **HELD** — 0.9746 |
| P6 | More historical breaches than Gaussian | **HELD** — **50** against 29.1 |
| P7 | The constructed book breaches on level | **HELD, and vacuously**: §9.2 |

**`US_CASH_BOOK`, the budget lost in one session.** The scenario is series by series, in basis points
and in percent for the euro:

| Covariance | d, own sigmas | d under `SAMPLE` | Cosine with `SAMPLE` | `SVENY02` | `SVENY05` | `SVENY10` | `DFII5` | `DEXUSEU` | Euro's share | On-thesis |
|---|---|---|---|---|---|---|---|---|---|---|
| `SAMPLE` | 2.3378 | 2.3378 | 1 | −8.39 | −10.47 | −10.02 | −7.30 | +1.02% | 47.7% | 60.7% |
| `LEDOIT_WOLF` | 2.3397 | 2.3378 | 1.0000 | −8.38 | −10.46 | −10.02 | −7.30 | +1.02% | 47.7% | 60.6% |
| `EWMA`, 2014-12-24 | **2.2938** | 2.5214 | **0.9272** | −6.26 | −9.84 | −9.79 | −8.19 | +1.17% | **54.7%** | 54.7% |
| `NBER_1990`, `NBER_2001` | refused: `DFII5` and `DEXUSEU` cannot be seen | | | | | | | | | |
| `NBER_2007` | **1.5455** | 2.3988 | 0.9746 | −9.78 | −11.09 | −10.30 | −6.72 | +0.90% | 42.4% | 65.4% |

**History.** The scaled book lost at least $1m on **50** of 2,997 sessions, against **29.1** a Gaussian
model expects. **The most plausible of them is 2004-05-17**, at 2.3799 sample sigmas, only 0.04
further out than the closed form: 2y −8.31bp, 5y −9.66bp, 10y −9.05bp, `DFII5` −8.00bp, the euro
+1.13%. The breach closest to the model's is the model's scenario, observed once. The count says the
tail is fatter than the model's, which D9's historical-to-Gaussian ES of 1.171 already implied.

**The constructed book.**

| Covariance | d | d under `SAMPLE` | Cosine | `SVENY30` | `SVENY10` | On-thesis |
|---|---|---|---|---|---|---|
| `SAMPLE` | 2.3378 | 2.3378 | 1 | −9.93 | −14.11 | 90.8% |
| `LEDOIT_WOLF` | 2.3380 | 2.3378 | 1.0000 | −9.93 | −14.11 | 90.8% |
| `EWMA`, 2014-12-24 | **2.7704** | 2.3832 | 0.9810 | −11.78 | −14.11 | 83.1% |
| `NBER_1990` | 2.1761 | 2.3566 | 0.9920 | −8.74 | −14.11 | 79.1% |
| `NBER_2001` | 2.2304 | 2.3563 | 0.9921 | −8.75 | −14.11 | 102.2% |
| `NBER_2007` | **1.5071** | 2.3378 | 1.0000 | −9.88 | −14.11 | 92.5% |

History: **85** breaches of 6,730 sessions against 65.3 expected; the nearest is 1996-10-29 at 2.3815.

### 9.1 The diversifier stopped diversifying on the construction date (P3)

P3 said late 2014 was calmer than 2003–2014 for this book, and for every leg it was. On the
construction date's EWMA the three rates legs together move $224,844 a day against $308,559 on
`SAMPLE`, and the euro leg $261,381 against $294,480. **What moved was the correlation between them**:
the rates legs' P&L and the euro leg's correlate at **0.0057** on `SAMPLE` and **0.6056** on the
construction date's EWMA. The 10-year yield and the euro correlate at −0.016 and −0.587. In late 2014
US yields rose as the euro fell, and the book is short both, so its two halves gained and lost
together. The book's daily deviation rose from $427,752 to $435,953, and the budget loss moved from
2.34 to 2.29 sigmas. **The euro was 47.7% of the book's risk on the average covariance and 54.7% on
the day the book was built.** It was sold as the leg that profits from a different side of the
thesis, and on that day it was a second copy of the rates bet. D9 found it was the largest risk and
all off-thesis. D13 finds that when it was bought, it was not even a separate one.

### 9.2 The generator's headline book holds no 30-year risk (P7)

The constructed book is D7b's short 30-year outright plus a short 10s30s spread. Their 30-year DV01s
are **212,568.67 and −212,568.67 dollars per basis point at budget scale, and they cancel exactly**.
The book's whole exposure is **$70,856 per basis point on `SVENY10`**. D9 §9.3 called it one bet, from
a −0.954 correlation between the two legs. It is one series. P7's "same way" held only because the
30-year's move in the scenario is its correlation with the 10-year, not a risk the book carries.
Every covariance therefore gives the same 10-year move, −14.11bp, which is the budget over the DV01,
and only the 30-year's correlated response changes.

**The pool offered that exposure as one leg.** `out_sveny10_short` is among D7b's 462 candidate legs.
The cost-aware greedy took the 30-year first, whose half-spread per unit of risk is lower. It then
took the spread to cancel what the 30-year carries off the view. It arrived at the 10-year outright
through two legs, trading the 30-year twice for a 30-year exposure the book does not keep. H9 counts
legs and is unmoved by this. What it shows is that a greedy, cost-aware selection can pay more to
reach a book one leg would have given. That is a limit of D7b's method, which D16 reports: **X26**,
opened here.

### 9.3 What reverse stress added

On one covariance it added nothing, as DD221 said. On others it found two things D9 could not: the
weak axis **does** move for `US_CASH_BOOK` on the construction date (cosine 0.93, the euro's share up
seven points), because the book's two bets merged, and the budget loss is **1.51 to 1.55 crisis sigmas**
for both books in 2007–09 against 2.34 on average. History agrees with the model's shape and not its
frequency: its most plausible breach sits 0.04 sigmas from the closed form's, and it breaches 1.7
times as often as the model says (50 against 29.1).

One thing the suite caught on the first full run: C111's census (X3) reads any name `cosine` in the
package, because that is `ViewFidelity`'s statistic. The scenario's field is named `alignment`,
renamed rather than exempted, as D6's `ViewDirection` was.

*Next free ids: **C213 / DD225 / X27**.*
