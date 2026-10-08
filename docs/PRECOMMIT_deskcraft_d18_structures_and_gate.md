# D18 — five structures on a stated exposure, the gate that refuses leverage, and a claim that cannot fail

*Written 2026-09-26, at `98246c1`, after D17's cash-flow half and before its equity half. Bars and
predictions fixed before the run; §9 is written after it.*

`BUILD_ORDER_D3_D16.md` §4: *"Extends D6's grammar from views to exposures — the hedge target is the
exposure vector sign-flipped, so D7b/D9/D11 are reused unchanged. The gate is an **iff**, in D2's
`Neutrality` shape: a structure names the exposure it hedges and its worst case, or it is
unconstructible. **Leverage ratio > 1 is a refusal, not a warning.** Premium paid and optionality
sold are reported separately and never netted. Carries **H13**."*

**What this package is for, plainly.** A company's annual report states what it is exposed to. A
bank can offer it several hedges for one exposure, and the cheapest-looking of them, measured the
way a quote sheet measures cost, is the one that leaves the company obliged to transact more than
it has. That was the KIKO disaster (Korea, 2008). D18 builds the menu, the price of each item, and
a type that cannot be constructed for a structure that obliges more than the exposure.

---

## 0. Measured before decided

- **One identity decides H13.** A zero-premium structure that buys one unit of the protective
  option and sells *p* units of the opposite option at the same strike has, by put–call parity at
  a discount factor of one, a protected rate that beats the forward by exactly **(p − 1) × the
  value of one sold option**. Checked with optcraft at three volatilities in each model family and
  at p = ½ and p = 2: equal to six places. So among one-strike zero-premium structures, **the
  only one that beats the forward is one that sells more than it hedges**, at every volatility
  above zero. §3 draws the consequence.
- **Volatility at the construction date**, EWMA with λ 0.94 and D8's normalised weights over the
  committed DEV panels through 2014-12-24: `SVENY01` at **0.3451%**, normal volatility **0.2693%**
  a year; the euro **8.84%**, the Canadian dollar **6.98%**, sterling **6.17%**, the yen **11.30%**.
  Crude has no committed series: EIA's route is results-only (DD176).
- **The case clients** are the first three firms of D17's cohort ordering, as D22's lock names them
  for H16: GE, ExxonMobil, AT&T. Their largest stated exposures (D17's stated fixture): GE, rates,
  **$77.89bn** of floating and short-term debt, losing when `SVENY01` rises; ExxonMobil, crude,
  **$244.16bn** of purchases, losing when WTI rises; AT&T, rates, **$20m**.

---

## 1. What D18 builds

`src/deskcraft/hedging.py`, and one extension of `src/deskcraft/views.py`.

| Decision | Content |
|---|---|
| **DD193 — the menu** | Five structures on one exposure, each sized at **100% of the stated exposure for one year**, D17's naive hedge. **Forward**: the linear leg at F. **Bought option**: the protective option at K = F. **Zero-cost collar**: buy the protective option half a standard deviation (σ√τ, in the model's own space) adverse of F, sell one unit of the opposite option at the strike that makes net premium zero. **Participating forward**: buy one protective, sell **½** opposite, one strike solved for zero premium. **2:1 ratio forward**: buy one protective, sell **2** opposite, one strike solved for zero premium. The ratio forward stands in for KIKO: its sold leg doubles the obligation as the knock-in did, and the knock-out is dropped, because a barrier is path-dependent and research §7 keeps those *stressable, never priceable*. Rates, dividends and forward points are zero (discount factor one), as D22's lock prices currency options at zero rate differential. |
| **DD194 — leverage, and the gate as a type** | Leverage is research §6's: **the worst-state notional the client is obliged to transact ÷ the stated exposure**. A bought option obliges nothing, a forward one, a sold option its multiple. The denominator is the **stated** flow, not D17's measured k: the obligation is to deliver currency or crude or to pay fixed, and the flow the 10-K states is what the firm will have to deliver. Sizing at 100% of the stated flow is H11's over-hedge, which D17 and D21 measure; it is not the gate's question. `HedgeStructure(exposure, legs, worst_obligation)` constructs **iff** (a) some leg pays in the exposure's losing direction, (b) the declared worst-state obligation equals the one derived from the legs, which is `Neutrality`'s shape (DD16, DD17), and (c) the derived leverage is at most 1. Otherwise it raises `Unsuitable`. There is no warning path. |
| **DD195 — the cost a minimiser sees** | The *unconstrained cost minimiser* minimises what a quote sheet shows: **net premium paid minus the improvement of the protected rate over the forward**, per unit of exposure. It never sees optionality sold. The report carries **premium paid** and **optionality sold** as two numbers and never nets them (research §6). At fair value every structure here is worth nothing to the client, so a minimiser on fair value is indifferent among them. Only a markup could break the tie, and option markups are not modelled: D7a prices linear legs. So the headline objective is the one that makes the choice, and it is the one H13 names. |
| **DD196 — prices and volatility** | optcraft's value formulas for Garman–Kohlhagen, Black-76 and Bachelier are **restated** in `hedging.py` and certified to exact equality by a bar that reads optcraft's own source. That honours DD168 item 4 the way C59 and C60 honour meip and curvecast: the engine imports no sibling. The bar is PARTIAL in the census when optcraft is absent. Currency is priced on GK at zero differential and crude on Black-76, both in moneyness (F = 1); rates on Bachelier on `SVENY01` in percent. Volatility: every case on a **ladder**, lognormal {5%, 10%, 20%, 40%, 80%} and normal {0.05, 0.10, 0.25, 0.50, 1.00}% a year, plus the **EWMA rung** where the committed panel carries the series. D22's ordered source list binds D22's option legs, not D18's cases, and §3 shows no volatility can move H13. |
| **DD197 — the grammar, from views to exposures** | `views.ExposureTerm(series, weight)`, where `weight` is the firm's P&L per unit **rise** in the series (sign × amount), and `views.HedgeTarget(exposures)`. `compile_view` compiles a hedge target to **−Σ weight × e(series)** in series space: the exposure sign-flipped. A hedge target states no factor, so its `terms` are empty and D7b's factor-reach loop has nothing to iterate. Reach is checked where the target is built instead: `hedging.hedge_target` refuses any series outside `generator.CANDIDATE_SERIES`, X19's rule applied to a series rather than a factor. `generator.py`, `attribution.py` and `sizing.py` are not edited. |
| **DD198 — a reason in D22's lock that overstated the gate** | The lock's option row says *"Never sold: selling optionality is what the suitability gate refuses (D18, H13)"*. The gate the build order specifies refuses **leverage above one**, and a collar sells optionality at a leverage of exactly one, so the gate admits it. The rule stands: D22's option legs are bought, never sold. Only the reason is corrected, in place. The out-of-sample read has not happened, so DD171's label for a choice made after 2015–2025 was seen is not owed. |

---

## 2. Carried items

**X7**: discharged; every prediction below is about a number that exists before its check.
**X15**: discharged in §3. **X16**: §3 says H13 cannot fail, and names its refuting experiment, the
identity swept over both ladders, run in C180. **DD171**: D18 fixes nothing D22's verdicts depend
on except that the gate admits a bought option (leverage zero) and that the hedge target reaches
D7b. Both follow the lock. DD198 corrects one reason in the lock and moves no rule.

---

## 3. X15 for H13, and why it cannot fail

| Claim | Quantity and range | Threshold | Admits |
|---|---|---|---|
| H13 | cases, of 3, whose unconstrained pick has leverage above one: {0, 1, 2, 3} in principle, **{3}** on this menu at every volatility above zero | at least 1 | **100% of what is attainable: it cannot fail** |

The ratio forward is the only structure on the menu whose headline cost is below zero (§0's
identity with p = 2). The forward's is zero. The bought option's is its premium. The collar's and
the participating forward's are positive, because each gives up rate to pay for its protection at
zero premium. So the minimiser picks the ratio forward on every exposure at every rung, and the
gate refuses it. The count is 3 by arithmetic, before any exposure is read.

**H13 is scored as written, not withdrawn.** It is H4b's case: withdrawing a claim at the package
that scores it would be the scorer choosing its own bars. So it is scored, with the range beside
the verdict. What the paper can say is narrower than the register's row, and more useful: **the
KIKO pick is a property of the objective, not of the market.** A minimiser that sees net premium
and rate, and not optionality sold, walks into leverage every time, at any volatility. That is
why DD195 reports optionality sold, and why the gate is a type.

**What would have made H13 falsifiable** is a menu with no structure selling more than it hedges,
or a cost that counts optionality sold. On the first, the count is 0 by the same identity. On the
second, every structure costs zero and the pick is undefined. Neither is a hypothesis about data.

---

## 4. Bars

| Bar | Holds |
|---|---|
| **C179** | DD196's restatement: GK, Black-76 and Bachelier values equal optcraft's **exactly**, calls and puts, on a grid of spots, strikes, tenors and volatilities. PARTIAL: skips when optcraft is absent. |
| **C180** | X16's experiment. For p in {½, 2}, both model families and every rung: the protected rate's improvement equals (p − 1) × one sold option to 1e-12, and is above zero iff p > 1. |
| **C181** | The gate, DD194: forward, bought option, collar and participating forward construct; the ratio forward raises `Unsuitable`; a declared obligation that disagrees with the legs raises; a structure with no leg paying in the losing direction raises. |
| **C182** | DD195: premium paid and optionality sold are two fields. The collar's are both above zero with net premium zero; no field of the report nets them. |
| **C183** | H13: for each case client, the unconstrained pick is the ratio forward at every rung, the gate refuses it, the constrained pick is the forward; the verdict is in `CLAIMS`. |
| **C184** | DD197: GE's hedge target compiles to +1 on `SVENY01` and 0 elsewhere; D7b's `select` on it at the headline cell takes `OUT_SVENY01` alone, at cosine 1, in the direction that gains when `SVENY01` rises; `hedge_target` refuses a series outside the candidate pool. |
| **C185** | The case table is read from D17's stated fixture: each client's legs, the largest by amount, and GE's dollar figures at the EWMA rung. |

`MODULES` gains `deskcraft.hedging`. The environment census gains C179 as PARTIAL.

---

## 5. Predictions

| | Prediction |
|---|---|
| **P1** | C179 is exact at every grid point. |
| **P2** | **H13 PASS**, 3 of 3, at every rung of both ladders and at the EWMA rung. By §3 this cannot fail. |
| **P3** | The gate-constrained minimiser picks **the forward** in every case at every rung. This is also arithmetic: every other admitted structure either pays premium or gives up rate. |
| **P4** | GE at the EWMA rung, no verdict: the bought cap costs about **$84m** (0.2693% × 0.399 × $77.89bn). The ratio forward's capped rate beats the forward by about **7.4bp**, about **$58m** a year, bought by selling a floor on **$155.8bn**. |
| **P5** | D7b on GE's hedge target takes one leg, `OUT_SVENY01`, at cosine 1.0. |
| **P6** | The suite gains seven bars. C32 and C34 redden until H13's verdict and the §5 row land in this commit. |

---

## 9. Result

*Written after the run, 2026-09-26. Suite 186 → **193** passed; `ruff` green.*

| | Predicted | Measured |
|---|---|---|
| **P1** | C179 exact | **Exact at all 162 grid points**, calls and puts in all three models. The certificate holds optcraft's digest at `ae7128f`. |
| **P2** | H13 PASS, 3 of 3, every rung | **PASS, 3 of 3, at all seventeen rungs**: six for GE and AT&T each (five on the ladder and the EWMA rung), five for ExxonMobil's crude, which has no committed series. |
| **P3** | The constrained pick is the forward | **The forward, at every rung, in every case.** |
| **P4** | GE: cap about $84m; ratio forward about 7.4bp, $58m, floor sold on $155.8bn | **$83.7m; 7.43bp, $57.9m a year; a floor sold on $155.78bn.** |
| **P5** | D7b takes `OUT_SVENY01` alone at cosine 1 | **As predicted**, and the leg's P&L on a one-basis-point rise in `SVENY01` is positive: the target points the way the hedge must gain. |
| **P6** | Seven bars | **Seven**, C179–C185. |

**GE's menu at the construction date** (EWMA rung, `SVENY01` 0.3451%, normal volatility 0.2693% a
year, $77.89bn of floating and short-term debt, one year):

| Structure | Leverage | Premium paid | Optionality sold | Capped rate | Rate vs forward | Headline cost | Gate |
|---|---|---|---|---|---|---|---|
| Forward (pay fixed) | 1.0 | 0 | 0 | 0.3451% | 0 | 0 | admits |
| Bought cap | 0 | $83.7m | 0 | 0.3451% | 0 | $83.7m | admits |
| Zero-cost collar | 1.0 | $41.5m | $41.5m | 0.4798% | −$104.9m | $104.9m | admits |
| Participating forward | 0.5 | $57.9m | $57.9m | 0.4194% | −$57.9m | $57.9m | admits |
| **2:1 ratio forward** | **2.0** | $115.8m | **$115.8m** | **0.2708%** | **+$57.9m** | **−$57.9m** | **refused** |

Four things the table shows that the verdict does not:

1. **The ratio forward's $57.9m is paid for with $115.8m of optionality sold**, a floor on twice
   the debt GE has. If the one-year yield falls below 0.2708%, GE pays fixed on $155.8bn against
   $77.9bn of floating debt. The excess $77.9bn is a pay-fixed swap with no debt behind it, and it
   loses as rates fall. That is the knock-in half of KIKO, without the knock-out.
2. **Every zero-premium structure sells exactly what it buys.** Net premium is zero by construction,
   which is why a quote sheet calls them free. The two columns this report never nets are the
   only place the difference between the collar ($41.5m sold) and the ratio forward ($115.8m sold)
   is visible.
3. **The gate-constrained choice is the plain forward**, Brown–Toft's answer absent quantity
   uncertainty, and the cheap linear structure H12a expects D21 to find sufficient.
4. **D7b adds nothing to a single-series exposure.** Every stated rates exposure in D17's cohort
   sits on `SVENY01`, so D22's rates linear leg is the one-year zero alone. That is the lock
   working as written, and it is worth knowing before D22 reads.

**What the gate does not see.** Leverage is measured against the stated flow (DD194). A forward
on 100% of the stated exposure has leverage one here, and it is H11's over-hedge if D17 measures
the exposure at a third of that. The gate refuses a structure that obliges more than the firm
has; whether the firm has what its 10-K says is D17's question.

*Next free ids: **C186 / DD199 / X26**.*
