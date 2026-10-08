# Build order D3–D16, with the cost model and the risk-contribution flags

Supersedes `PLAN_deskcraft.md` §7's D1–D8. Written 2026-09-05, after D2 closed at `4057cd5`.
D1 and D2 are shut; everything below is open.

This document is the to-do list. Each row becomes one work package under the inherited
discipline — pre-commit doc first with bars fixed **before** the run, then one commit carrying
doc and code together.

---

## 0. What changed since the order was approved, and why

Five things from work done on 2026-09-05, then five more on 2026-09-08, a hardening
amendment on top of those, and a twelfth on 2026-09-17 after the free-data sweep — all from
measurement rather than from a change of mind.

| # | Change | Cause |
|---|---|---|
| 1 | **D5 moves ahead of D4** | Only four legs of the reference structure are priceable from graded data, which is exactly §10's NO-BUILD floor. One series losing its grade stops the project. D5's front-end probe is the only thing that buys headroom, so it goes first. |
| 2 | **D3 splits into D3a and D3b** | D3 had grown to five jobs. The guards and the two registers are load-bearing and small; the data panel is neither. |
| 3 | **A claims register, at D3a** | `SCENARIO_SIGNS` is a pre-registered claim with no scorer until D12. An unfalsified claim sitting in a repo is what this project exists not to produce, so the register makes it a **build failure** rather than a promise. |
| 4 | **A source resilience register, at D3a** | Measured on 2026-09-05: FRED's ICE BofA credit spreads were truncated to 3 years of observations in April 2026 and prohibit reproduction. A free source did not theoretically go bad — one went bad five months ago. |
| 5 | **A cost model, as D7a, before the leg generator** | The stopping rule is cost-aware or it is arbitrary, and RATES-X already established that costs are decisive in exactly this domain: curve relative value at **gross Sharpe 0.72, net −1.59**. |
| 6 | **The blanket futures decline is withdrawn for energy** | It rested on continuous roll-adjusted series baking in an unauditable splice rule. Measured 2026-09-06: the **EIA publishes NYMEX WTI contracts 1–4, daily settlement, free, ~~public domain~~, from 1983** — *individually dated*, so the splice objection dissolves because the roll rule becomes ours to write and state. Treasury futures **stay declined**; no free dated history was found, and D2's cash re-expression already covers them. *(Annotated 2026-09-17 by `AMENDMENT_A5` §7.2, DD113.* **The coverage half has expired.** The EIA page now states prices after **2024-04-05** are not available, so the series reaches **nine of the eleven** OOS years DD98 fixes (2015-01-01 → 2025-12-31) and stops roughly twenty months short of the window a commodity result would be scored on. ~~Public-domain and individually-dated both hold~~ Individually-dated holds, and the splice argument is untouched — what has gone is reach. **X21**, owned by D17.*) *(Struck 2026-09-26, DD176:* **not public domain.** *EIA republishes these prices from CME Group "with permission", and its own policy says licensed third-party material may be protected, so the route needs the owner's admission by name.)* |
| 7 | **The blanket option decline is withdrawn in half, as D19** | `VXTYN` was measured dead (2014-11-14 → 2020-05-15), and that measurement was over-generalised. Free vol **levels, term structure, skew and vol-of-vol** do exist — VIX from 1990, VIX9D/3M/6M, SKEW, VVIX, OVX, GVZ. Four parameters are not a surface, but they support a **stated parameterisation with a sensitivity ladder**. Vanillas become priceable; path-dependent exotics stay stressable-not-quotable. |
| 8 | **A client-solutions layer, as D17–D21** | `docs/RESEARCH_client_solutions_layer.md`. A hedge is a book whose factor loading is the client's exposure vector sign-flipped, so D6–D12 are reused unchanged and only the exposure extractor and the suitability gate are new. It is engineerable **because the exposure is a public document**: Reg S-K Item 7A market-risk disclosure and XBRL company facts on EDGAR, free, keyless, public domain, full-text searchable to 2001. Scope is a **40-firm measurement cohort** with **three hand-built case studies drawn from inside it**, across **four asset classes** (rates, FX, commodity, credit). |
| 9 | **The scope bound is widened and the objective is restated** | Two defects found 2026-09-08 by taking the solutions layer seriously. **(a)** The three-client bound made its own hypotheses unfalsifiable: an exact binomial sign test on n = 3 **cannot reject at 5% even under a unanimous result** (best achievable two-sided p = **0.2500**; n = 6 is the floor for the test to be capable of rejecting, n = 40 the first value with power 0.703 against a 70%-prevalence effect). The cohort is therefore 40 for the measurement packages, with the hand-built case tier held at three. **(b)** *Maximum coverage is the wrong objective.* It is the KIKO objective: coverage is only raisable without premium by selling optionality, so coverage-maximisation and the leverage ≤ 1 refusal are in direct conflict, and FSS says full coverage is not optimal regardless. Coverage becomes a **reported output with its denominator named**; the maximand is measured residual-risk reduction per unit of modelled cost. Adds **H15** and **H16** |
| 10 | **Coverage is an input, the tiers are reprioritised, and the end-to-end backtest is the deliverable** | Settled by the user 2026-09-08, and the first half is a better answer than item 9's. **(a)** *Coverage is a stated target, not a maximand* — the client says how much of the exposure they want neutralised, fully or partly, and the engine returns the best portfolio for **that** target. This keeps the whole of item 9(b)'s argument (the engine still never raises coverage on its own, so it never reaches for sold optionality) while removing the awkwardness of a hedging tool that argues against hedging. It is the same shape as §1's stopping rule: **budget in, structure out.** **(b)** Pricing is demoted to *fair value with a band* — a live quote was never the product. **(c)** The selling tier is **out of scope**, not a limitation: the deliverable is the instrument portfolio, not the pitch. **(d)** The headline test becomes the full loop — public filing → exposure → structure → replay against real crises — which makes D21/D22 the centre of the layer rather than its validation appendix. |
| 11 | **The probe goes first, the plan freezes, and three bars are rewritten** | `AMENDMENT_A1_probe_freeze_split.md`, 2026-09-08. **(a)** The exposure is read *structurally* — arithmetic on disclosed units — alongside the disclosed and the measured quantity, giving a **three-way** comparison and adding **H17**; the read is not exact and its four error sources are named. **(b)** A feasibility probe, **D23**, moves to **first in the running order** under a **blindness rule**: it may count, it may not measure, because a pilot that reports effect sizes destroys D17's pre-registration. **(c)** **H14's conjunction is provably vacuous** — since in-sample R² ≤ 1, the decay clause strictly implies the level clause, so the bar advertises a strictness it does not have. Split into H14a/H14b. **(d)** Two power tables that were owed and missing: firm-level R² sampling, and the exact Clopper–Pearson interval on cohort prevalence, where **28/40 clears the ≥ 70% bar with a 95% CI of [0.535, 0.834]**. **(e)** The package list is **frozen at 21** and the budget is a build failure, not a sentence; D19 and D20 move to an annex. **(f)** Two checkpoints and **two papers**, so the engine ships even if the exposure layer dies. |
| 12 | **The free-data sweep lands, the licence rule is decided, and the integration order is fixed** | `AMENDMENT_A5_what_free_data_reaches.md`, 2026-09-17. **Twenty-two sources read for their own licence words** rather than for a tag: five public-domain, six granting redistribution on attribution, five stricter than attribution, six with no free source at any licence. **DD118** then decides the rule the sweep exposed — *read yes, commit no* — which opens the yen leg and FR 2004B to **reading** while `git archive HEAD` continues to carry only unconditioned bytes. Four carried items opened (**X19**–**X22**), **two claims in this document struck in place** (§0 item 6's coverage half, §3.3's *"Public domain"* on FR 2004B), and a fifth opened here against §4.1's D19 row (**X23**). **What to build next is not derivable from any of that, so it is decided rather than implied: §7, DD119.** No package added, no row of §4 moved, nothing un-annexed — `AMENDMENT_A1` §6 is untouched. |

---

## 1. The stopping rule, settled

**Risk budget in, leg count out.** There is no leg-count input and no cap.

1. A **risk budget** is stated as expected shortfall at 97.5% — the Basel FRTB measure, and the one a modern risk function actually runs.
2. Legs are added **greedily**: the structure with the highest fidelity to the view enters first, then whichever addition most improves the book, one at a time.
3. Each addition must clear a **cost hurdle** fixed in advance (§3).
4. It **stops** when the next-best addition fails the hurdle.
5. **Leave-one-out is reported for every surviving leg**, so each leg's place is defended by a number rather than by the fact that it was added.
6. If a fixed count is wanted for presentation, the **counterfactual is reported**: what forcing the extra leg cost in view-exposure per unit of risk. The count becomes a presentation choice with a price tag rather than a hidden assumption.

Greedy rather than exhaustive, and the reason is statistical. Choosing 6 from ~300 structures is
~10¹² combinations, and searching that for the best-looking book is overfitting at industrial
scale. Greedy touches **≈1,800 evaluations** across six rounds — a number that goes into D15's
Deflated Sharpe trial count and can be defended.

**Pre-registered, before anything runs:**

> **H9 — for the reference view, the cost-aware stopping rule terminates below six legs.**
> **Predicted: PASS**, at three or four. Three factors explain 97.9% of curve variance, so by the
> fourth leg there is little independent territory left, and the cost hurdle bites before the
> geometry does.

> **H8 — a generated book for the same view has a higher effective number of bets than the
> hand-built six-leg book, and both are still below 3.0.**
> **Predicted: PASS on both halves.** The second half matters more: it says the machine helps a
> little and the binding constraint is the market, not the construction.

> **Annotated 2026-09-15 by `AMENDMENT_A2`, not rewritten.** Two numbers this section names do not
> exist, and one of them is the hypothesis one section down.
>
> **The hurdle in point 3 was never fixed.** *"Fixed in advance (§3)"* — and §3's five subsections
> fix no hurdle value anywhere; its only quantity is §3.1's *relative* multiple, which is a
> statement about what a structure costs, not a threshold anything can be compared against. By
> point 4 the hurdle **is** the leg count, and §5's **H9** is a prediction about that count scored
> by **D7b** — the package that would otherwise choose the hurdle, while looking at the structures
> it stops on. §6 forbids exactly this for D9's flag thresholds and said nothing here.
>
> It is fixed now, before D7b's pre-commit exists: **`costs.COST_HURDLE = 1.0`**, with
> `HURDLE_HOLDING_YEARS = 1.0`, held by C91. And it is 1.0 because it is **not a free parameter** —
> selecting at hurdle `h` against cost `c` is the same function as selecting at `1.0` against
> `h × c`, and §3.5 already runs the whole selection at `0.5× / 1× / 2× / 4×`. Any other value is a
> rung of a ladder the rule already reports. The denominator is `cost_per_dv01`, because
> `AnnualisedCost.total` refuses on all four legs of the reference book (DD86); the expected-shortfall
> unit point 1 names arrives with D9, and D7b pre-registers the substitution. `AMENDMENT_A2` §2.
>
> **"≈1,800 evaluations" assumes six rounds, which is what H9 predicts against.** Six rounds over
> ~300 structures, minus the legs already taken, is **1,785**. At H9's predicted three or four legs
> it is **897 or 1,194**. The figure above is the count at a cap the rule does not have, and D15's
> trial count should take the number D7b reports rather than this one. Low severity — D7b's row
> already reports the count — and recorded because a plan should not carry two values for a number
> that reaches a Deflated Sharpe.

---

## 2. The four risk-contribution flags

Every leg in a finished book is screened on four pathologies. Two are the standard multi-PM
risk-committee questions; the third is the one this project's machinery is unusually good at
finding and is the most common in practice; the fourth is the one the reference structure
already fails on its own reasoning.

| # | Flag | What it means | Why it is a defect |
|---|---|---|---|
| **F1** | **Dead weight** — contributes almost no risk | The leg is on, is paying spread and financing, and moves nothing | Pure cost. It is not in the book in any sense that matters, and it consumes attention and operational risk |
| **F2** | **Concentration** — contributes most of the risk | One leg is the book and the others are decoration | The stated diversification is false, and the drawdown profile is a single position's |
| **F3** | **Off-thesis risk** — contributes real risk, but not to the view | The leg is taking risk in a direction that was never asked for | **The important one.** A leg can pass F1 (plenty of risk) and pass F2 (not dominant) and still be pure downside, because the risk it adds points somewhere the view does not. Only the fidelity-versus-risk split exposes it |
| **F4** | **Redundancy** — contributes risk and view, but nothing another leg does not already give | Two legs, one bet | This is the `us_2y` / `eurusd` case, visible in the source's own scenario table |

F1 and F2 are computed from component expected shortfall under Euler (D9). F3 needs the view's
factor direction (D6) alongside it. F4 needs the correlation of leg P&L, conditional on the
other legs — a partial contribution, not a raw pairwise correlation, because raw correlation
between two legs expressing the same thesis is high **by construction** and says nothing.

**Thresholds are pre-registered in D9's doc before any book is scored**, and are reported with
the count of legs screened, so a flag firing cannot be presented as a discovery.

> *Annotated 2026-09-15 by `AMENDMENT_A3` §7, not rewritten.*
>
> **F3's split is the one X3 bites, and X3 names only F4.** This section calls F3 *"the important one"* and says *"only the fidelity-versus-risk split exposes it"* — and the fidelity side of that split is `dominant_share`, which `views.py` has recorded since D6 as **not a variance decomposition**: *"the six directions are not orthogonal (`factors.FactorBasis.gram`), so the loadings do not partition anything."* The Gram entries are `LEVEL·REAL_VS_NOMINAL` +0.4434, `LEVEL·CROSS_MARKET` +0.2717, `CURVATURE·CROSS_MARKET` −0.3005. F4 wants a *conditional correlation*, which is a different object and is D9's to build; **F3 wants exactly the decomposition that does not exist**, which is why X3 bites it harder and why X3's body now names it. D7b ranks legs by fidelity **two packages before** D9 can fix the statistic.
>
> **F4's example verifies exactly.** *"The `us_2y` / `eurusd` case, visible in the source's own scenario table"* — of the **15** leg pairs in `SCENARIO_SIGNS`, **exactly one** carries identical signs across all four scenarios, and it is that pair, both `(+1, 0, 0, −1)`. Not approximately right: the unique instance, and both legs are priceable, so D9 can score it.
>
> **F1's rationale names a cost term the engine does not have.** *"Is paying spread and financing"* — financing is one of the two terms X11 records as **absent**. D9 computes F1 from component ES and not from cost, so this is rationale and not arithmetic; **if F1 is ever computed from a cost, X11 blocks it.**

---

## 3. The cost model

### 3.1 Costs are compositional, which is the whole point

Not 300 independent estimates. **≈20 instrument cost profiles**, and a structure's cost is the
sum over its components:

| Structure | Components | Cost |
|---|---|---|
| Outright 10Y | 1 | 1 × |
| 2s10s steepener | 2 | 2 × |
| 2s5s10s butterfly | 3 | 3 × |
| 5Y breakeven | 2 (nominal + real) | 1 × nominal + 1 × TIPS |
| US-vs-Bund 10Y, FX-hedged | 3 (UST, Bund, FX hedge) | 3 × |

**A relative-value structure costs two to three times an outright to establish and the same to
unwind, so it must clear a two-to-three-times higher hurdle.** That single fact is the most
likely reason the stopping rule terminates early, and it is the mechanism behind RATES-X's
finding that curve RV dies net of costs.

> **Annotated 2026-09-15 by D7a, not rewritten.** Two rows of this table count the wrong thing,
> and the table is right about the other three.
>
> **The butterfly row is low by a third.** A 2s5s10s is `(+1, -2, +1)` — three *components* but
> **four units of notional**, and a dealer charges the spread on every unit crossed, not on every
> distinct name. Cost is `4 ×`, not the `3 ×` written. `costs.instrument_half_spread` sums
> `|coefficient| × half_spread` and C79 holds the ratio at exactly `4/3`. Found while writing
> C79's mutation, and **nothing in D7a's §3 predicted it** — the pre-commit had caught the same
> defect one table down in §3.2 and did not think to look back up at the row that introduced it.
>
> **The breakeven row is the one row that is already correct**, and is the reason §3.2 is wrong:
> *"1 × nominal + 1 × TIPS"* is a sum over components with **different** per-component spreads,
> which is the compositional form, not a component count. See the note under §3.2.
>
> The headline sentence above survives both corrections — it moves from "two to three times" to
> two to four, in the same direction.

### 3.2 The four cost terms

```
annualised cost  =  2 × half_spread × n_components / holding_years     entry and exit
                 +  impact(order_size, ADV)                            square-root law
                 +  financing_drag × holding_years                     repo vs coupon
                 +  roll_cost × rolls_per_year                         on-the-run decay
```

Shorter holding period pushes the first term up without limit, which is why a cost model with
no holding-period assumption is not a cost model.

> **Annotated 2026-09-15 by D7a, not rewritten** — D4's precedent for an upstream formula that an
> implementing package finds does not hold. What executes is `costs.annualised_cost`; the block
> above is kept as written so the correction is visible as a difference. Three defects, all found
> by trying to implement it, all recorded in that package's §0.7 with the arithmetic:
>
> 1. **The label says annualised and two of the four terms are not.** `financing_drag ×
>    holding_years` is a *total*, not a rate — annualised, it is `financing_drag`, and the written
>    form is correct only at exactly one year, which is the most likely reason it survived being
>    read. `impact(...)` is a one-off entry cost undivided by the holding period, and it is paid
>    **twice**, on entry and exit: annualised it is `2 × impact / holding_years`, which agrees with
>    the written form only at two years.
> 2. **`half_spread × n_components` contradicts §3.1's own breakeven row**, and §3.1 is the correct
>    one. A single scalar spread times a component count is the compositional sum only when every
>    component costs the same; on `us_breakeven_5y`, with TIPS at twice the nominal, it is **low by
>    50%** ($15,625.00 against $23,437.50 on $50m). And on §3.1's butterfly it is low by a further
>    third, because it counts names rather than units of notional.
> 3. **Two of the four terms have no graded input in this repository at all.** §3.3 names NY Fed
>    FR 2004B for the impact term, and `sources.py` has no row for it; §3.3 says of the financing
>    term *"Fed H.15 and SOFR, both already graded"*, and **neither is in the source register**.
>    D7a computes the two that are computable, records the other two as **absent rather than zero**
>    (a zero is a number and every sum downstream adds it), and makes `AnnualisedCost.total`
>    **refuse** — naming the missing terms — rather than return a sum of two things labelled four.
>    That is carried item **X11**, owned by D7b.

### 3.3 Where each input comes from, all free and all publisher-of-record

| Input | Source | Notes |
|---|---|---|
| Average daily volume, by maturity bucket | [NY Fed Primary Dealer Statistics](https://www.newyorkfed.org/markets/counterparties/primary-dealers-statistics) (FR 2004B) | **Free, from 1998-01-28**, weekly, buckets 0–2 / 2–3 / 3–6 / 6–7 / 7–11 / 11+ years **and a separate TIPS bucket**. ~~Public domain.~~ Feeds the impact term. *(**"Public domain" struck 2026-09-17** by `AMENDMENT_A5` §2 and §6.3, DD113.* NY Fed's terms of use retain copyright and require a redistributor to pass on *"the same permissions, conditions, and restrictions"* — attribution with a share-alike clause, which is `CITATION_REQUIRED` and **not** `PUBLIC_DOMAIN`. Under **DD35** the fixture is refused, so grading this series does not close **X11**'s data half; a caller-stated `MarketDepth` does.*) |
| Bid-ask, on-the-run vs off-the-run | NY Fed and Federal Reserve Board staff research | Published research, cited rather than scraped |
| TIPS liquidity penalty | [FRBSF, *Is There an On-the-Run Premium in TIPS?*](https://www.frbsf.org/wp-content/uploads/wp2017-10.pdf) | Seasoned TIPS bid-ask runs **30–100% higher** than on-the-run, though the paper notes the absolute magnitude is under a basis point |
| Repo / financing | Fed H.15 and SOFR, both already graded | GC assumed; specialness is a **stated assumption, not a measurement** |

> **Annotated 2026-09-15 by D7a.** *"Both already graded"* is **false**, and was false when it was
> written. `sources.py` has **no row for either** — no H.15 series and no SOFR series — and no row
> for FR 2004B either, so **the two rows this table gives for the impact and financing terms name
> nothing this repository holds.** The two rows above them are real: the bid-ask row is published
> research cited rather than scraped, exactly as it says, and the FRBSF row is a paper whose own
> absolute bound D7a carries as a bar (C83). The gap is **X11**, owned by D7b; D7a refuses the two
> terms by name rather than defaulting them, because a default is a silent answer (DD18).

### 3.4 The caveat that decides how the model is used

The Federal Reserve Board's own 2025 work — [*Trading Costs vs. Indicative Liquidity in the
Off-the-Run Treasury Market*](https://www.federalreserve.gov/econres/feds/trading-costs-vs-indicative-liquidity-in-the-off-the-run-treasury-market.htm)
— finds that indicative bid-ask spreads are a **biased** measure and *"systematically overstate
trading costs of more seasoned Treasuries"*, with the bias larger for larger orders. It does not
quantify the magnitude.

Two consequences, both recorded rather than worked around:

1. Using bid-ask as the cost is **conservative** — it stops the rule *earlier*, giving *fewer*
   legs. That is the less flattering direction, which is the right direction for a bias to run.
2. It is still a bias, and a leg killed by an overstated cost is a leg killed wrongly. So the
   model is never reported at a point estimate.

### 3.5 Sensitivity is mandatory, not optional

The whole selection runs at **0.5× / 1× / 2× / 4×** the central cost estimate, and the leg count
at each is reported beside the result. If the count is stable across that range, the cost
assumption is not driving the answer. If it flips between 1× and 2×, the honest headline is that
**the result is a statement about costs rather than about structure**, and it says so.

**This is a paper engine and nothing is executed.** The cost numbers are calibrated assumptions
from public sources, never measurements, and no package may describe them otherwise.

> **Annotated 2026-09-15 by D7a — the ladder has a second axis now.** `CARRIED_ITEMS.md`'s **X5**
> held that the 0.5×/1×/2×/4× multipliers vary the *level* of the cost estimate and cannot reach a
> bias that is not a level, so a bias with a stated direction and no magnitude has nowhere to
> appear. Measured: the par-proxy duration convention moves cost per DV01 by **13.289%** on
> `us_10y`, which is **0.18 of a single rung** of this ladder — widening the multipliers could
> never have separated it. `costs.cost_ladder` therefore runs the full grid of **4 multipliers ×
> 2 `DurationConvention` values**, and C84 holds the arm at that fraction. X5 is closed by the
> arm, not by the multipliers.
>
> The prohibition in the paragraph above is now mechanical: `CostBasis` has **no `MEASURED`
> member** (DD74), so a cost profile in this engine cannot be recorded as a measurement, and C78
> holds that the enum stays that way.

---

## 4. The order

Rows are in **running order**, not numeric order — the convention set when D5 moved ahead
of D4 and kept its number. Frozen at **21 core packages** by `AMENDMENT_A1` §6; the two
annexed packages are below the table and may not be built until the core closes.

| # | Package | Deliverable |
|---|---|---|
| **D23** | **Exposure feasibility probe** ***(new, and first)*** | **CLOSED 2026-09-09** — run in curvecast under `docs/PRECOMMIT_curvecast_wpd23_exposure_probe.md` (D422–D433 / C497–C505) and adjudicated here at `e286e62`: the stopping condition is **MET, 19 of 20 (14 of 20 strict)**, fixture `tests/fixtures/exposure_probe_20260909.csv`, 120 rows, 63 requests against a cap of 250. H17 stands and D17 is not reverted to regression-only. *(Marker added 2026-09-14 by D3b. The row had been closed in `AMENDMENT_A1` §7 and in the adjudication commit since 2026-09-09 and said so nowhere in this table — which is the failure mode C34 exists to prevent one register away, and this table is the other one.)* *As scoped:* Runs in **curvecast**, which has the egress; deskcraft receives a dated fixture. Answers P-1 … P-5 of `AMENDMENT_A1` §3.6 — above all **whether EDGAR `companyfacts` returns dimensional facts at all**, on which the whole FX arm of the structural read depends. **20 firms, stratified five per asset class.** Under the **blindness rule** it emits one frame with a fixed schema and **reports counts only** — never an exposure, ratio, R² or coefficient — and a test asserts the schema so a float column cannot be added. **Carries no hypothesis, deliberately.** Stopping condition fixed in advance: fewer than **8 of 20** firms yielding a structural read withdraws H17 and reverts D17 to regression-only |
| **D3a** | Guards and registers | **CLOSED 2026-09-11** — `docs/PRECOMMIT_deskcraft_d3a_guards_and_registers.md`, bars C25–C38. Delivered as scoped below, and three things beyond it, each from measurement: the ban reaches every Python file by policy rather than by a root list, with the strict policy the default (the owner's decision); the engine's imports are a census, and a runtime audit hook refuses the network under test; and the source register records the licensor's words over FRED's tag, which disagree for the credit spreads. `PACKAGE_BUDGET` is checked as an equality, stricter than §6.2 of the amendment. *As scoped:* `FitWindow` refusing `end > 2014-12-31`. Widen the boundary scan to `SCRIPTS` before a `scripts/` directory can exist. **Claims register** — every pre-registered claim names the package that scores it; the gate fails if a claim has no scorer, or if the scorer has landed and the claim is unscored. **Source resilience register** — publisher, publisher class, licence, and a named fallback per series. TRIAL_LEDGER non-look entry. **`PACKAGE_BUDGET = 21`, read from §4's table, failing the build when the core exceeds it.** ~~And the M18 repair~~ — **done 2026-09-09, ahead of this package.** `lint-imports` had never run: the config omitted `include_external_packages`, and beneath that the `meip.lpal` contract is inexpressible and aborted every run. The LLM-edge ban is now **C23** (AST, dotted paths, segment-wise) with **C23b** mutating it, and **C8 now asserts the gate can be evaluated, not merely that contracts are declared**. `lint-imports`: 2 kept, 0 broken. ~~Bar-id uniqueness~~ — **also done 2026-09-09**: that repair shipped its pair as `C10`, which D2 already held, so **C24 / C24b** now fail the build on any `C` id claimed by two modules (`AMENDMENT_A1` M18a). A renumber with no guard is a fix that can silently regress, and this package is at least one away. **The claims register, the source-resilience register and `PACKAGE_BUDGET` are untouched and remain D3a's.** |
| **D5** | Front-end archive floors ***(moved up)*** | **CLOSED 2026-09-12** — measured in curvecast at `e78d2f7` (`FLOORS` 30 → 34, `D447`–`D452`, `C519`–`C522`) and answered here by `docs/PRECOMMIT_deskcraft_d5_front_end_floors.md`, bars C39–C41. All four of `DGS3MO`, `DGS6MO`, `DGS1` and `DGS2` open on ALFRED's 2005-06-28 epoch — the date `DGS5`, `DGS10` and `DGS30` have carried since they were measured eleven months earlier — and are **P0 from the floor, P1 before it**, so a steepener's short leg now carries the long leg's provenance. That is M7 closed. *As scoped:* the probe, the four rows, and Treasury.gov's par curve as the cross-check, which agrees on **174 of 174** shared 2026 sessions and is a cross-check rather than a committed panel or a test (a bar that needs the network is not a bar). *Beyond it, from measurement:* the documented measurement method no longer executes — the full-range read hits FRED's 2,000-vintage cap — and was replaced by an adaptive window walk; and comparing FRED's value **strings** counted reprints as revisions, which moved `DGS1` 7 → 6 and `DGS2` 5 → 4. **The claim in this row as written was too strong and is corrected rather than deleted:** it does not lift the leg universe off §10's NO-BUILD floor, because D5 adds no leg and the priceable count is still four. What it lifted is the **reachable** universe, 30 → 34, and the package that spends it is D7. |
| **D3b** | The data panel | **CLOSED 2026-09-14** — `docs/PRECOMMIT_deskcraft_d3b_data_panel.md`, bars C42–C48. Two dated fixtures land: `panel_daily_dev_20260914.csv`, 7,044 GSW sessions × 17 series over 1988-01-01 → 2014-12-31, and `panel_monthly_dev_20260914.csv`, 323 credit observations. Generated by curvecast's `scripts/make_deskcraft_panel.py`; **this repository still fetches nothing.** *As scoped:* committed dated fixtures, extraction staying in curvecast. *Beyond it, from measurement:* the extraction was **already done** — every committable series was sitting in curvecast's own fixtures, so D3b is a transfer, a re-grid and a licence closure and not a fetch; **five constant-maturity observations were refused** because their only vintage is 2015-01-05, so a panel taking `obs_date` at face value would have carried post-DEV knowledge in through a fixture nobody suspected; and the Gilchrist–Zakrajšek substitute's licence, which `sources.py` recorded as *not read from the file*, had been read by D3a itself three days earlier and nothing noticed until a package needed it. **The credit leg is `GZ_SPREAD` by the owner's decision of 2026-09-14** — monthly, a different bond universe, a substitute construct that no later package may describe as a Moody's spread. `DGS10` and `GZ_SPREAD` join the source register (16 committable → 18); `T10YIE` is **not** carried although both of its inputs are columns. |
| **D4** | DV01 and leg P&L | **CLOSED 2026-09-15** -- `docs/PRECOMMIT_deskcraft_d4_dv01_and_leg_pnl.md`, bars C49-C57 (and C58/C58b, the lint gate, which rides along and is not D4). *As scoped:* `src/deskcraft/sensitivity.py` maps a stated bp shift to per-leg DV01 and P&L over `US_CASH_BOOK`. *Not as scoped, and measured:* **the wrap holds for one leg of four.** The Board's own header block in `feds200628.csv` says `SVENYXX` is *Continuously Compounded* zero-coupon, so three of the four legs have a modified duration of exactly their maturity and nothing to approximate; MEIP's par-bond proxy -- written for a repository that *holds no index constituents* -- understates `SVENY10`'s DV01 by **11.730%**. It is kept for `DFII5`, which is genuinely par-quoted, and C50 executes MEIP's own bytes out of `cascade.py` to hold the restatement at exact equality. **The shift is keyed by series, not by tenor** (DD54): `US_BREAKEVEN_5Y` holds two curves at five years and a per-tenor shift cannot name which moved. *Beyond it, from measurement:* that leg declares `Neutrality.DV01` and **does not have it** -- its two components are quoted on different conventions, so a parallel move leaves **370.67 per basis point** on $50m. `reference.py` is annotated and not edited; the re-expression is D7b's. `numpy` was predicted for this package by `pyproject.toml` and `panel.py` and was **not** added, because the arithmetic is scalar and `ENGINE_IMPORT_ROOTS` is an equality. D4 scores no registered claim |
| **D6** | The view language | **CLOSED 2026-09-15** — `docs/PRECOMMIT_deskcraft_d6_view_language.md`, bars C59–C71. *As scoped:* `src/deskcraft/views.py` carries the closed six-term grammar, each term with a `Move`, compiling to a target vector; `src/deskcraft/factors.py` carries the basis it compiles into. **H3 is scored `PASS`** — the first verdict `CLAIMS` has ever held, and C34 was red from the moment this document landed until it was set. *Not as scoped, and measured:* **the DEV factor basis was never this package's to fit, and this row is where that went missing.** No row in this table fits one, though `window.py` names it among three fitted objects — but `pyproject.toml` has recorded since D1 that the engine's inputs are *"the objects curvecast item 28 produces"* and that deskcraft reaches `curvecast.stage3.factor_space` by design. Item 28 fitted it, on changes, on DEV, over the eight GSW zeros that are this repository's own panel columns. So the arithmetic is **restated, not refitted**: C59 establishes the two repositories hold the same GSW bytes (7,044 rows, 309 blanks, **0 differing fields**) and C60 executes curvecast's own `_pca` to hold the restatement at **exact equality**, reproducing 83.9352% / 97.9021% / effective rank 1.8231. **Only three of the six terms are fitted** — `REAL_VS_NOMINAL`, `CREDIT_VS_RATES` and `CROSS_MARKET` reach curves the eigenbasis does not span, and are **stated** at matched tenors rather than estimated. *Beyond it, from measurement:* **curvecast's eigenvector sign rule is for diff stability and carries no market meaning**, so orientation is a separate measured step (DD62) — and the prediction that it would flip a component was **wrong**: all three were already oriented, on a **36.4% margin** in PC2 that a different sample could reorder into a silent flattener. **H3's PASS is thin.** `LEVEL` leads at +46,989.92/bp but by only **4.991%** over `REAL_VS_NOMINAL` and 10.756% over `CROSS_MARKET`, and all three are substantially the same nominal duration position counted through overlapping directions (`gram` 0.4434 and 0.2717) — recorded, with the statistic **not** retuned, and F4's partial-contribution form left to D9. `numpy` arrives here rather than at D8 (DD60), because a restatement held at exact equality has to call the same eigensolver. And D2's `C10` caught the grammar's first-draft `ViewDirection` as a near-name of `Direction` and was right to: renamed to `Move`, never exempted *(Annotated 2026-09-25 by D8, X6: **the orientation is DEV's, not the factors'.** On the 1990 recession sample curvecast's sign rule points `+PC2` at a flattening (C137). Every oriented reading of this basis is a statement about the DEV sample.)* |
| **D7a** | **The cost model** ***(new)*** | **CLOSED 2026-09-15** — `docs/PRECOMMIT_deskcraft_d7a_cost_model.md`, bars C77–C87. *As scoped:* `src/deskcraft/costs.py` carries **17 instrument cost profiles** against the row's *"~20"* and **6 refusals**, compositional structure costs, the four terms, §3.5's ladder, and §3.4's bias on the object rather than in prose. *Not as scoped, and measured:* **§3 does not survive being implemented, and four of its five subsections are annotated above rather than rewritten.** §3.2's formula is not annualised in two of four terms — `financing_drag × holding_years` is a total, right only at one year; `impact(…)` is undivided and paid twice, right only at two — and its `half_spread × n_components` contradicts §3.1's own breakeven row, running **50% low** on `us_breakeven_5y`. §3.1's **butterfly row is low by a third**: `(+1, -2, +1)` is four units of notional across three components and a dealer charges per unit crossed, which **nothing predicted** — the pre-commit had found the identical defect one table down and never looked back up at the row that introduced it. **§3.3's *"Fed H.15 and SOFR, both already graded"* is false**: neither is in `sources.py`, nor is FR 2004B, so **two of the four cost terms have no graded input in this repository at all.** They are recorded **absent rather than zero** and `AnnualisedCost.total` **refuses**, naming them — opened as **X11**, owned by D7b, the first carried item raised by a package rather than by an audit. *Beyond it, from measurement:* **cost per risk divides by gross DV01, never by D4's `net_dv01`** (DD81) — that field is a residual, and on `us_breakeven_5y` it overstates cost per risk **133.89-fold**, on `eurusd` it is 0÷0, and on a spread whose declared neutrality actually held it would price a well-hedged structure as infinitely expensive; the FX leg is refused by name. **X4 is closed by stating D4's 11.730% understatement as a bias with a direction, at 13.289%** — the figure is the ratio's, not the denominator's, and C85 holds the identity `x/(1−x)` rather than storing two constants. **X5 is closed by a second ladder axis, and by correcting its count upward: there are three conservative biases, not two** — D4's DD52 annual-pay approximation understates `DFII5`'s duration, so it overstates cost per DV01 by 0.1232%, the same direction as the other two. `CostBasis` has **no `MEASURED` member** (DD74), so §3.5's closing prohibition is now mechanical. And the two front-end series **D5 went and graded**, `DGS3MO` and `DGS6MO`, have a half-spread and **no computable duration**, so they have no cost per risk — D7b meets that at the denominator rather than at the data. `ENGINE_IMPORT_ROOTS` did not move and `numpy` is not reached: the arithmetic is scalar. D2's `C10` caught this package's first-draft `BiasDirection` as a near-name of `Direction`, the **second consecutive package** it has caught — renamed to `BiasSense`, never exempted. D7a scores no registered claim |
| **D7b** | Leg generator | **CLOSED 2026-09-16** — `docs/PRECOMMIT_deskcraft_d7b_leg_generator.md`, bars C103–C112. *As scoped:* `src/deskcraft/generator.py` enumerates the universe, runs §1's greedy addition under the cost hurdle at every cell of §3.5's ladder, and reports leave-one-out per surviving leg and the forced-count counterfactual. *Not as scoped, and measured:* **§1's hurdle has a free parameter nobody named, and it is the only one of three that moves H9's verdict.** The comparison sets a dimensionless gain in fidelity against `cost_per_dv01`, which is *in basis points of yield*; `COST_HURDLE = 1.0` fixes the threshold and not the units, so the rule is undefined until a view magnitude is stated. `VIEW_MOVE_BP = 1.0` is fixed here by `AMENDMENT_A2` §2's own argument — only `move / multiplier` enters, so the selection at multiplier `m` and move `1.0` is **identical leg for leg** to the selection at `1.0` and `1/m`, measured at all four rungs (C107) — which makes it a rung of a ladder already reported and not a degree of freedom. **And the collapse is not reassuring:** read as view magnitudes, §3.5's four rungs span **2 bp down to 0.25 bp**, while a macro view that yields rise is tens of basis points, and at 10 bp the count is **six**. The universe is **231** (11 outrights, 55 spreads, 165 butterflies over the eleven series that have both a cost profile and a factor direction), not the row's *"~300"*; the evaluation count D15 is owed is **462** distinct legs, **1,380** at the headline cell and **7,830** across the eight reported cells — none of them §1's *"≈1,800"* nor `AMENDMENT_A2` §7's corrected *"897 or 1,194"*, which was right arithmetic on two wrong operands. **The leg count flips between 1× and 2×**, which is the pair §3.5 nominates, so the headline is the one §3.5 pre-wrote: the count is a statement about costs rather than about structure — and the *convention* axis changes the **composition**, not only the count, which is more than X5 claimed for it. *Beyond it, from measurement:* **six legs is a ceiling set by geometry, not by cost** — at a cost model of effectively zero the greedy stops at six because no remaining structure raises the book's cosine, which **bounds X11's `MORE_LEGS` bias above** for the first time. **Gross DV01 is strictly additive, so `AMENDMENT_A2`'s substitution prices no diversification**; the counts are a lower bound on the count under D9's expected shortfall. At 4× the rule takes **nothing**, and an empty selection is reported as an outcome with its refused candidate rather than forced into a one-leg book. **X12 closed** (the ladder is reported whole), **X11 narrowed and carried to D8** (`costs.Financing` closes the code half; the weekly-to-annual question follows X2), **X3 discharged** — the ordering is `cosine`, which claims no decomposition, so the statistic X3 is about is never read (C111) — and **X17 opened**, owned by D9. `ENGINE_IMPORT_ROOTS` did not move. D7b scores **H9: PASS** *(annotated 2026-09-16 by `RIDER_the_cost_multiplier_is_implemented_twice.md`, DD112: `COST_MULTIPLIERS` had* **two implementations** *— `cost_per_dv01` scaled the spread term and `generator.select` scaled the whole cost — bit-identical at all 3,696 cells while the spread is the only graded term, and divergent once it is not. The rung is fixed to scale the* **total**, *which is the reading this row reports, so* **every figure above is unmoved and all eight cells reproduce exactly**. *The re-measurement owed when X11's second term lands is carried as* **X18**, *owned by D8.)* |
| **D8** | Covariance | **CLOSED 2026-09-25** — `docs/PRECOMMIT_deskcraft_d8_covariance.md`, bars C130–C138, DD141–DD145. `src/deskcraft/covariance.py`: the sample covariance is primary and is **exactly** the matrix D6's PCA used (C130); Ledoit–Wolf to constant correlation **on standardised changes**, because on raw mixed units the unit chooses the intensity (DD142); RiskMetrics EWMA; the three NBER recessions inside DEV as crisis windows (DD144); a monthly companion that samples daily series down and never up (DD130, DD145). `DEXUSEU` is in the book's covariance in percent (DD139). **The book's five series have a crisis covariance in one window only, 2007–09**; 1990 and 2001 are refused by name. **X6 found what it feared: PC2's orientation flips in the 1990 window.** P4 missed: 2s10s correlation rose in 2007–09 (0.752 against 0.745). Six items answered, five closed. *As scoped:* Sample primary; Ledoit–Wolf, EWMA and crisis-window variants as robustness. All take a `FitWindow`. *(Annotated 2026-09-17 by §7.1 below, DD119.* **This row owns five of the register's thirteen open carried items — the largest discharge load any package has carried into its pre-commit**: **X2**'s frequency-policy half, **X6**, **X11**'s data half, **X18**, and **X22**. Three of the five moved on 2026-09-17 and all three moved *towards* this package rather than away from it — **X22** was opened by DD118 because the rule sorts a graded source three ways and `sources.py` expresses one; **X11** was narrowed twice and now offers two routes rather than one, a pinned FR 2004B fixture or the stated `MarketDepth` already in `costs.py`; and **X2**'s daily-credit half was measured at `AMENDMENT_A5` §4 and found to be a licence wall rather than a preference, so the frequency policy is a decision and not a fetch. **C76 will require this package's pre-commit to say in writing what became of each of the five.** There is therefore no separate task that folds `AMENDMENT_A5` into the plan — this row is where it lands, and it is the next core package.*) *(**Scope widened 2026-09-25 by DD139, §7.6.** The covariance carries `DEXUSEU` as a **risk factor**, because `US_CASH_BOOK` holds `eurusd` and a DV01-only covariance would carry one of its four legs at zero. This is not a grammar term: DD138 declines that, and `generator.py` still drops `DEXUSEU` from the candidate pool.)* |
| **D9** | Component ES and VaR under Euler, **and flags F1–F4** | **CLOSED 2026-09-25** — `docs/PRECOMMIT_deskcraft_d9_component_risk.md`, bars C139–C146, DD146–DD152. `src/deskcraft/attribution.py`: Gaussian ES 97.5% on D8's sample covariance is primary, historical simulation beside it; Euler components sum exactly under both. **`eurusd` is `US_CASH_BOOK`'s largest risk, 47.7% of ES, and all of it is off-thesis for the reference view** (F3); the breakeven is dead weight at 4.2% (F1). Historical ES is 1.17× Gaussian. VaR fails sub-additivity on the textbook pair and on none of the book's eleven sub-books. **The generated headline book is one bet**: its two legs correlate at −0.954 given nothing else, so F2 and F4 fire. X3, X17, X19 closed. *As scoped:* ES 97.5% primary. Euler additivity is a unit test. Exhibit VaR violating sub-additivity where ES does not. §2's four flags with thresholds pre-registered here |
| **D10** | Effective number of bets | **CLOSED 2026-09-25** — `docs/PRECOMMIT_deskcraft_d10_effective_bets.md`, bars C147–C152, DD153–DD155. `src/deskcraft/bets.py` restates item 28's ladder exactly (1.8231 / 7.9059 / 8.0000 on the eight zeros) and applies it to a book's leg P&L covariance. **H4a PASS** (2.4103), **H4b PASS vacuously** (whitening is the leg count for any covariance; min-torsion is 2.6567), **H8a refuted** (generated 1.0898 against 2.4103), **H8b reported** under a new verdict, `REPORTED`, for claims registered without a prediction. *As scoped:* All three of the ladder, each with its basis named. Carries H4 and H8 |
| **D11** | Sizing under the risk budget | **CLOSED 2026-09-25** — `docs/PRECOMMIT_deskcraft_d11_sizing.md`, bars C153–C157, DD156–DD160. `src/deskcraft/sizing.py`: the optimising rules minimise tail risk **per unit of view exposure**, never against a return (DD156), and every book is scaled to one Gaussian-ES budget (DD158). R-U CVaR and CDaR are HiGHS linear programs and agree with direct arithmetic to 1e-13; ERC, min-variance, max-diversification and 1/N are the benchmarks. On the headline book the optimiser buys 4.0% more view per unit budget than 1/N, and the ES of their difference is 0.28 of the budget. *As scoped:* Rockafellar–Uryasev CVaR as a linear program; Chekhlov–Uryasev–Zabarankin CDaR. Benchmarks: 1/N, ERC, min-variance, max-diversification |
| **D12** | Scenario engine | Dated replay on full history including 2020 and 2022, each window on **its own** realised correlations. Filtered historical simulation with hand-rolled GARCH(1,1). **Scores `SCENARIO_SIGNS`**, which is what closes D3a's claims-register row. *(**CLOSED 2026-09-28** — landed on the out-of-sample read, `PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md` §13, bar C220. **H6 and H7 refuted**: sizing moved 65.8% of gross under 2020's correlations and 2.7% under 2022's, and the size of 2022's P&L, a gain for the short-duration book, exceeded the three-factor quantile by 3.3% while 2020's stayed at 82% of it. `SCENARIO_SIGNS` reported. CP-1 tagged, `docs/CP1_the_engine_runs_end_to_end.md`.)* *(Annotated 2026-09-15 by `AMENDMENT_A3` §8.* **The panel this row replays does not exist, and no row commissions it.** D3b delivered two fixtures, **both DEV** (1988-01-01 → 2014-12-31); this repository holds **no row dated after `DEV_END`**. The OOS period is *authorised* — `window.py` says every out-of-sample test here runs after `DEV_END`, and DEC-1 reads 2015 → present — but D12, D14, D15 and D22 all need a panel nobody is commissioned to build. **And the first read of a post-DEV row fires DD37 in curvecast**, irreversibly: the non-look entry takes effect at *"deskcraft's first read of a row dated after `DEV_END`"*, and *"what a person has read cannot be unread."* It forecloses **curvecast's** remaining budget, not deskcraft's. D12 runs first of the four, so the trigger is named here. **No package is added — the budget is frozen at 21 and that is the owner's call, not an amendment's.**) *(Superseded in part 2026-09-16 by `AMENDMENT_A4` §2.* **The sentence immediately above is wrong, and the correction is recorded rather than the sentence removed.** This was never a budget decision: D23, D3b and D17 all say extraction runs in curvecast and deskcraft receives a dated fixture, so the OOS panel is D3b's deliverable at a different date range and **costs no package at all**. What was missing was a *specification*, and A4 supplies it: the window is **2015-01-01 → 2025-12-31** (DD98), fixed by the rule *last complete calendar year at the date of specification* and enforced by `window.OosWindow` rather than by prose; series limited to the existing source register (DD100); D3b's vintage rule inherited verbatim (DD101). The DD37 trigger stands exactly as named above and **gets a commit of its own that does nothing else** (DD102). Receiving and validating the fixture is **X13**, owned by this row.) *(**GATED 2026-09-23** by `RIDER_X13_X14_one_surface_two_clocks.md`, **DD133-DD135**, **C119-C121**. This row reads the out-of-sample record. It may not be pre-registered on its own -- D12, D14, D15 and D22 share one irreversible surface and are registered in **one** document, `PRECOMMIT_deskcraft_d12_d14_d15_d22_*.md`, before the first read; and no post-`DEV_END` row may be committed or named until `docs/OWNER_AUTHORISATION_the_first_oos_read.md` exists. The owner pulls this trigger, not the package that happens to be next.)* |
| **D13** | Reverse stress | **CLOSED 2026-09-28** — `docs/PRECOMMIT_deskcraft_d13_reverse_stress.md`, bars C208–C212, DD220–DD224. `src/deskcraft/reverse.py`: the budget lost in one session, on DEV. **On one Gaussian covariance reverse stress is D9's Euler decomposition** (DD221): the breach sits 2.3378 sigmas out for every book and its shares are D9's, held to 1e-12. What it adds is the same breach on other covariances and in history. `US_CASH_BOOK`'s budget loss is 1.55 crisis sigmas in 2007–09. On the construction date's EWMA it is 2.29, not the 2.34+ P3 predicted, because the euro's P&L correlated 0.61 with the rates legs', against 0.006 on average: the diversifier became a second copy of the rates bet. History breaches 50 times against 29.1 expected. **The constructed headline book holds no 30-year risk**: its two legs' 30-year DV01s cancel exactly and leave a 10-year outright the pool offered as one leg (X26, to D16). *As scoped:* Smallest plausible joint move breaching a stated loss tolerance |
| **D14** | **Risk-model backtest** | Kupiec, Christoffersen, Acerbi–Székely Z1/Z2, Fissler–Ziegel via Diebold–Mariano, Basel traffic light. ~2,700 OOS days. *(**CLOSED 2026-09-28** — landed on the out-of-sample read, `PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md` §13, bar C220. **H1 PASS** (Kupiec p 0.191 at 97.5% and 0.219 at 99%, Z2 p 0.538) and **H2 not independent, as predicted** (p 0.0013), over 2,736 sessions. DD135's rule selected `EWMA`.)* Power table published in the pre-commit, before the run. *(Annotated 2026-09-16 by `AMENDMENT_A4` §3.2 (DD99).* **“~2,700 OOS days” was written against no stated end date, and it is 5.9% low against the window A4 fixes.** The out-of-sample record is **2015-01-01 → 2025-12-31** (DD98), eleven complete calendar years; the DEV panel runs at a measured **260.89 sessions a year** — min 260, median 261, max 262, no holiday gaps — so eleven years is **≈ 2,870** sessions. 2,700 would end the window around **April 2025**, which is not a calendar boundary and corresponds to no rule. **≈ 2,870 is an estimate and is labelled one**: the true count lands with the fixture, and this row's power table is computed on the count the fixture carries, not on either figure written here.) *(**GATED 2026-09-23** by `RIDER_X13_X14_one_surface_two_clocks.md`, **DD133-DD135**, **C119-C121**. This row reads the out-of-sample record. It may not be pre-registered on its own -- D12, D14, D15 and D22 share one irreversible surface and are registered in **one** document, `PRECOMMIT_deskcraft_d12_d14_d15_d22_*.md`, before the first read; and no post-`DEV_END` row may be committed or named until `docs/OWNER_AUTHORISATION_the_first_oos_read.md` exists. The owner pulls this trigger, not the package that happens to be next.)* |
| **D15** | **Construction backtest** | Against three pre-registered nulls: the single-instrument expression, 1/N across the same legs, **and the hand-built book**. *(Annotated 2026-09-15 by `AMENDMENT_A3` §3, DD93: this read **six-leg**, which names no priceable object — the hand-built book is `US_CASH_BOOK`, at **four** legs.)* Ledoit–Wolf HACPW, stationary bootstrap, Deflated Sharpe on the counted trials, PBO via CSCV, Hansen SPA *(**CLOSED 2026-09-28** — landed on the out-of-sample read, `PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md` §13, bar C220. **H5 as predicted**: −0.012 of Sharpe against 1/N at p 0.82, uninformative by §5.2's grammar. Deflated Sharpe 0.017.)* *(Question 2 settled by DD164: no fourth null; H5's power at the plausible effect is 8%.)* *(A risk-per-view test was planned and power-checked 2026-09-26, DD169 and DD170: power 0.33 and 0.40 against 0.5, so **no H18**; the statistic is reported with every run, without a verdict.)* *(**GATED 2026-09-23** by `RIDER_X13_X14_one_surface_two_clocks.md`, **DD133-DD135**, **C119-C121**. This row reads the out-of-sample record. It may not be pre-registered on its own -- D12, D14, D15 and D22 share one irreversible surface and are registered in **one** document, `PRECOMMIT_deskcraft_d12_d14_d15_d22_*.md`, before the first read; and no post-`DEV_END` row may be committed or named until `docs/OWNER_AUTHORISATION_the_first_oos_read.md` exists. The owner pulls this trigger, not the package that happens to be next. **X14's fourth answer applies here**: this row's specification is committed **before D14's first result exists**, and every parameter D14's output could inform is a constant or a rule with one answer -- never a value to be chosen on sight.)* |
| **D16** | Readout and paper | Describes, never recommends. H1–H9 scored as written, limits, and the declines *(DD138, §7.6: the first limit stated is the saturated cosine **0.906494022**, the share of an arbitrary view direction the six-term grammar can reach at any cost, reported in place of H9's leg count as the engine's headline limit.)* *(**CLOSED 2026-09-28** — landed on the read's verdicts and tagged **CP-2**; Paper 1 complete: twelve live rows scored, seven as predicted, three against, two reported (§10 of its pre-commit). Registered earlier that day as `docs/PRECOMMIT_deskcraft_d16_readout_and_paper1.md`, DD225–DD230, bars C213–C218. `src/deskcraft/readout.py` renders Paper 1's claims table and tally from `CLAIMS`, and `docs/PAPER1_the_engine_and_its_backtest.md` holds the render, with every quoted figure checked against the document that recorded it. Five hypotheses and `SCENARIO_SIGNS` read **awaiting the read**, and D16 lands, tagging CP-2, in the commit that re-renders them after it (DD225). X20 and X26 are written into the paper's declines and limits.)* |
| **D17** | **Exposure extractor** ***(new)*** | Reads a real US public company's own filings — Item 7A market-risk disclosure and XBRL company facts — into a **stated** exposure vector, and estimates the **measured** exposure by Adler–Dumas elasticity regression. Reports the gap. Run over a **40-firm cohort selected by a mechanical rule fixed in this package's pre-commit** — dated index snapshot, filing-completeness filter, deterministic ordering, drop count reported — because a hand-picked cohort would reproduce the exposure-puzzle literature by construction. Extraction stays in curvecast; deskcraft receives a dated fixture. Carries **H11** *(**REGISTERED 2026-09-26, not landed**: `PRECOMMIT_deskcraft_d17_exposure_extractor.md`, DD181–DD189, C173. Every rule is fixed before any exposure is read. The owner's calls (DD181): weekly prices plus quarterly operating cash flow, *disclosed* means the figures the 10-K tags, the WTI route reaches D17, and later rows are dropped on arrival. Measured exposure is k, the variance-minimising multiple of the naive hedge, over five years of weekly returns ending 2014-12-24. Its power was published before any run (§6 there), and **a rates exposure cannot be resolved at this construction date**. The measured half waits on the owner's free Alpha Vantage key.)* *(**LANDED 2026-09-27**: §14 there, DD207–DD208, C192–C194. Thirty-two of forty firms measured on equity. **H11 PASS** (24 of 32, 0.750) and **H17 FAIL** (currency and crude median 1.55, rates median +∞), the cash-flow denominator the reverse on both. The market's own rate and dollar loadings decide every class (DD207): 22 of H11's 24 counts are a k at or below zero, and only two are the over-hedge the claim describes. A co-registrant defect in curvecast's extractor was found after the read and shown unable to move either verdict (DD208); whether to correct it is the owner's.)* |
| **D18** | **Structure grammar and the suitability gate** ***(new)*** | Extends D6's grammar from views to exposures — the hedge target is the exposure vector sign-flipped, so D7b/D9/D11 are reused unchanged. The gate is an **iff**, in D2's `Neutrality` shape: a structure names the exposure it hedges and its worst case, or it is unconstructible. **Leverage ratio > 1 is a refusal, not a warning.** Premium paid and optionality sold are reported separately and never netted. Carries **H13** *(**LANDED 2026-09-26**: `PRECOMMIT_deskcraft_d18_structures_and_gate.md`, DD193–DD198, C179–C185. Five structures on a stated exposure, priced by optcraft's formulas restated and certified (DD196). The gate is `hedging.HedgeStructure`, which cannot be constructed above leverage one, measured on the stated flow (DD194). A stated rates exposure compiles to a hedge target that D7b's generator runs on unedited (DD197). H13 scored.)* |
| **D21** | **End-to-end hedge backtest** ***(new)*** | The full loop, and the layer's headline. Filing → exposure → structure → replay. **Constructed as of a date**: the exposure regression, the hedge ratio and the structure choice use only data available at the construction date, then the book is held and walked forward. A hedge built today and tested on 2008 is a demonstration, not a test — this is the same discipline `FitWindow` already enforces on the covariance. Rolling vs held re-estimation is stated, not chosen after seeing which wins. Ederington effectiveness in-sample vs out-of-sample across the D17 cohort. Carries **H14** *(**REGISTERED 2026-09-26**, `PRECOMMIT_deskcraft_d21_hedge_backtest.md`, DD199–DD206, C186–C191: held, D17's k on every leg, in-sample effectiveness is D17's R² (DD200), verdict weeks 2015-01-01 → 2024-04-05 for every firm (DD201); H12a on the gated hedge against D18's three admitted alternatives (DD204). **The fifth reader of the out-of-sample record** (DD199), so it is GATED as D22's row is and the owner's authorisation names five readers. §6 says before any run that H14a is decided in sample and that H14b is carried by noise on the rates-only firms.)* *(**CLOSED 2026-09-29** — read on the record, its §13, bar C223. **H12a PASS**: the forward keeps at least 90% of the best admitted alternative's variance reduction on all seven eligible firms, median capture 1.300, the participating forward the best alternative on all seven. **H14a PASS**, 32 of 32, a claim the record could not fail in practice. **H14b FAIL**, 21 of 32 (0.656) against the 70% it needed, carried by noise on the rates-only firms (13 of 14 count); 10 of 18 on the resolved subset. DD210's implied volatility not performed, by name, as D22's was. P2 and P5 were wrong.)* |
| **D22** | **Funding path and crisis-conditional effectiveness** ***(new)*** | The two things VaR structurally missed. **(a)** Hedge effectiveness recomputed *conditional on* D12's dated crisis windows and reported beside the unconditional number — an R² of 0.8 that falls to 0.3 in 2008 and 2020 is a hedge that works when it is not needed. **(b)** Peak cumulative mark-to-market drawdown on the hedge leg over the replay windows, against the firm's trailing operating cash flow from XBRL. The **mark-to-market path is data**; the margin assumption is **stated, not measured**, because CSA and IM terms are not public. Carries **H15** and **H16** *(**SPECIFIED, NOT BUILT, 2026-09-25**: registered in the joint document, which cannot build it — it needs D17, D18 and D21. Whether Paper 1 reads before D22 exists is an owner decision, §6 there.)* *(**Option 1 taken by the owner 2026-09-26, DD168.** D22 reads after Paper 1 under a lock written before the read, §6.1 there (DD171): constructed 2014-12-24 and held, a 40-firm cohort by rule, rates and currency legs with bought six-month options beside them, verdicts on `NBER_2020` and `RATES_2022`. The options are priced by a separate library, so this row's budget does not move.)* *(**BUILT 2026-09-28, not run** — the joint registration §11, **DD212–DD219**, bars **C200–C207**: `src/deskcraft/funding.py`, and curvecast's `measure_deskcraft_d22_funding.py`, rehearsed on the three DEV windows. DD205's WTI cost row lands in D7a's model as `costs.CONTRACT_COST_OF`. H15 stays refused by name (DD180). **H16 is close to decided before the read** (DD218): ExxonMobil's stated crude purchases are 5.4 times its FY2013 operating cash flow, so a 100% hedge crosses a quarter of that cash flow on a 4.6% adverse move, and it crosses in every simulated path at the construction date's volatility. In DEV's 2007–09 window the same hedge fell $464bn from its peak.)* *(**CLOSED 2026-09-28** — read on the record, the joint registration §14, bar C221. **H16 PASS**: four of six client-windows exceed a quarter of trailing operating cash flow, ExxonMobil at 541% and 1,196%, GE at 62% and 404%, AT&T at 0%. **H15 not performed**, refused by name (DD180). D22-P3 was wrong: ExxonMobil's verdict-window 10-Ks tag §6.1's own concept, so DD231's fallback moved nothing there.)* *(**GATED 2026-09-23** by `RIDER_X13_X14_one_surface_two_clocks.md`, **DD133-DD135**, **C119-C121**. This row reads the out-of-sample record. It may not be pre-registered on its own -- D12, D14, D15 and D22 share one irreversible surface and are registered in **one** document, `PRECOMMIT_deskcraft_d12_d14_d15_d22_*.md`, before the first read; and no post-`DEV_END` row may be committed or named until `docs/OWNER_AUTHORISATION_the_first_oos_read.md` exists. The owner pulls this trigger, not the package that happens to be next.)* |

### 4.1 The annex — argued, out of the frozen core

Moved out by `AMENDMENT_A1` §6.3. Neither is load-bearing for the headline that §0
item 10 settled — the deliverable is the instrument portfolio and the test is the
end-to-end replay. **The argument is preserved; what it may not do is consume attention
first.** A package leaves the annex only by displacing a core package.

| # | Package | Deliverable | What annexing costs, stated |
|---|---|---|---|
| **D19** | **Option pricing under the free vol parameterisation** ***(new)*** | Level (VIX, OVX, GVZ), term (VIX9D/3M/6M), skew (SKEW), vol-of-vol (VVIX). Vanillas priced under a declared parameterisation with a mandatory sensitivity ladder; path-dependent exotics **stressed, never quoted**. Reverses the blanket option decline for the half free data supports | Brown–Toft's rule — forwards optimal absent quantity uncertainty, options necessary with it — **is still stated and applied**; only the pricing goes. The engine outputs “this exposure requires convexity; a vanilla is indicated; pricing it needs a surface free data does not provide”. The commodity case study is limited to linear hedges and the paper says so. **H13 survives**: a cost minimiser selects a 2:1 leveraged forward, which is leverage > 1 with no surface needed. *(Annotated 2026-09-15 by `AMENDMENT_A3` §9.* **This row names nine vol inputs and the source register grades one** — `VIXCLS`, with Cboe's reprint permission and a named fallback. `VIX9D`, `VIX3M`, `VIX6M`, `SKEW`, `VVIX`, `OVX` and `GVZ` have never been through a licence read. Same shape as §3.3's *"both already graded"*, and the third instance. **Low severity only because D19 is annexed** — but this row is the argument for un-annexing it, and eight-ninths of its inputs are ungraded.*) *(Annotated again 2026-09-17 by `AMENDMENT_A5` §5.2 and by §7.2 below.* **A3 §9's gap is now measured on one side and still unread on the other, and the asymmetry is the finding.** A5 §5.2 establishes that **every input this row names is equity or commodity vol, and those are free**; the implied vol that is not free is **rates** vol — MOVE is ICE's and CVOL is CME's — which is the only vol surface this repository's own instruments would ever need. So the ungraded inputs are asserted free by a document that **never read their licences**: A5's twenty-two-source sweep was rates, FX and credit and did not reach them. The half-decline this row takes is therefore stated without the record X16 asks for. **X23**, owned by **D16**, which is the row that reports the declines. Grading them **does not un-annex this row** and §4.1's displacement rule is untouched — what it buys is that the displacement argument stops being a preference and becomes a measurement. **And the count in the annotation above is wrong, found while writing this one**: the list A3 §9 prints is `VIX`, `VIX9D`, `VIX3M`, `VIX6M`, `SKEW`, `VVIX`, `OVX`, `GVZ` — **eight** names called nine in the same sentence, so the ratio is **seven of eight** ungraded, not eight of nine. The ninth is real but not here: `RESEARCH_client_solutions_layer.md` §7 lists nine free vol series and the extra one is **`VXEEM`**, which this row dropped when it was written — A3 took its count from the research layer and its names from this table. Corrected at A3 §9 rather than struck here, and the severity is unmoved either way.*) *(**Annotated 2026-09-17, `RIDER_the_vol_surface_is_licensed_not_absent.md`, DD121, closing X23.** **X23 ran and the half-reversal does not survive it.** Cboe's terms refuse, without prior written consent, to *"create a derivative work (for example, a financial product, service or index) from"* these values — the clause's own example is what this row would build. Grade **`REDISTRIBUTION_PROHIBITED`** at the originator and `PRE_APPROVAL_REQUIRED` at FRED, and **DD118 refuses both**. Three of the eight — `VIX3M`, `VIX6M`, `SKEW` — are not free at any route found, which removes the term structure and the skew. The blanket option decline is restored in full, with a better reason than it was first taken for. **This row is annotated and not moved**: it stays annexed, §4.1's displacement rule is untouched, and D16 writes the decline at step 6.*) |
| **D20** | **Markup benchmark** ***(new)*** | The 424B2 population: issue price vs disclosed estimated initial value, comparator set fixed by structure type and tenor **before** any structure is proposed. Scored against Henderson–Pearson, SLCG and Deng et al. Carries **H12** | A paper about structured-note pricing, not about hedging; it shares no machinery with the end-to-end loop. **H12 splits** — H12a (variance reduction) stays with D21, H12b (the markup half) is annexed with the package |

---

## 5. The hypothesis register

| # | Claim | Scored by | Predicted |
|---|---|---|---|
| H1 | Risk model correctly calibrated | D14 | PASS **SCORED 2026-09-28 by D14 — PASS**, on 2,736 out-of-sample sessions: Kupiec p 0.191 at 97.5% and 0.219 at 99%, Acerbi–Székely Z2 p 0.538. A correctly specified model misses this conjunction about 11.5% of the time |
| H2 | Exceptions independent | D14 | **FAIL** **SCORED 2026-09-28 by D14 — FAIL, as predicted**: Christoffersen independence p 0.0013 at 97.5%. The exceptions cluster |
| H3 | View fidelity: the book loads on the view's factor | D6 | PASS — **scored at 11 candidate series / 231 structures** (`AMENDMENT_A6` §1 clause 3, DD120). A verdict at a different universe is a new claim id, never a re-score |
| ~~H4~~ | ~~Six-leg US book has ENB < 3.0~~ | ~~D10~~ | **Withdrawn as written** (`AMENDMENT_A3` §3, §4, DD93–DD94). Two independent defects. The "six-leg US book" names neither object in `reference.py`: `REFERENCE_BOOK` has six legs but `eurusd` and `us_de_10y` are not US, and **both of the two legs it adds are in `DEFERRED_LEGS`** — an ENB over it needs a covariance over two legs this repository has refused to price, for stated reasons. And **`ENB` is undefined without a basis**: one covariance of 8 GSW zeros gives **1.8231** (Roy–Vetterli), **7.9059** (min-torsion) and **8.0000** (whitening), so `< 3.0` admits the first and refuses the other two. Split into H4a/H4b |
| **H4a** | `US_CASH_BOOK`'s four priceable legs have **Roy–Vetterli effective rank** < 3.0 | D10 | PASS — **and a weaker bar than H4 read.** ENB ≤ the leg count, so at n = 4 this is **75% of maximum** where at n = 6 it was 50%. The threshold does not move; what moved is the book, and only because the six-leg one cannot be priced. **SCORED 2026-09-25 by D10 — PASS**, at **2.4103** on the four legs' P&L covariance |
| **H4b** | The **same book and covariance** exceed 3.0 under at least one other basis of D10's ladder | D10 | PASS — the basis-dependence made falsifiable **on this book**, rather than asserted from curvecast's eight zeros. A four-leg book of overlapping duration positions could come in under 3.0 in all three, which would falsify it. **SCORED 2026-09-25 by D10 — PASS, and it could not have been otherwise**: whitening returns the leg count, 4.0, for any covariance, so "at least one other basis" always holds. The sentence above is wrong by `AMENDMENT_A3` §4.1's own identity. The rung that can move, min-torsion, is **2.6567**, under 3.0 (D10 §3) |
| H5 | ES-constrained sizing beats 1/N on Sharpe | D15 | **FAIL** **SCORED 2026-09-28 by D15 — FAIL, as predicted**: −0.012 against 1/N, p 0.82. Uninformative by the registration's §5.2: power at the plausible effect was 8% on DEV and is 0.112 on the record |
| H6 | Crisis correlations change sizing > 20% of gross | D12 | PASS **Scored 2026-09-28 by D12: refuted.** 65.8% of gross under NBER_2020's correlations and 2.7% under RATES_2022's; both were needed (DD167) |
| H7 | 3-factor Monte Carlo understates crisis P&L | D12 | PASS **Scored 2026-09-28 by D12: refuted.** the size of RATES_2022's P&L, a gain for the short-duration book, is 3.3% above the three-factor 97.5% quantile and NBER_2020's is 82% of it; both were needed (DD167) |
| ~~H8~~ | ~~Generated book beats hand-built on ENB; both < 3.0~~ | ~~D10~~ | **Withdrawn as written** (`AMENDMENT_A3` §5, DD95). **The level clause cannot fail.** ENB ≤ the leg count, and **H9 predicts the generated book terminates at 3–4 legs** — so at three legs `< 3.0` is **100% of maximum**, satisfied by every book except the perfectly diversified one. Its failure condition is the outcome it was written to celebrate. This is `AMENDMENT_A1` §5.1's H14 defect with the two clauses **four rows apart and scored by different packages**. Split into H8a/H8b |
| **H8a** | The generated book beats the hand-built `US_CASH_BOOK` on **Roy–Vetterli effective rank**, both in the same basis on the same covariance | D10 | PASS — the comparison, which `ENB ≤ n` does **not** make automatic, and the half H8 was written for. **Scored 2026-09-25 by D10: refuted.** The generated headline book ranks **1.0898** against the hand-built book's **2.4103** on one covariance; the six-leg book at a 10 bp view ranks 1.3155 on the same covariance. A book built for fidelity to a one-factor view is one bet by design |
| **H8b** | **ENB ÷ leg count**, reported for both books in each basis of D10's ladder | D10 | *no prediction. The level bar is vacuous and is deliberately **not replaced** by a different number — that would be inventing a bar after noticing the defect. The `SCENARIO_SIGNS` disposition, for the same reason* **Reported 2026-09-25 by D10** (`Verdict.REPORTED`, DD153): **0.6026** hand-built, **0.5449** generated, Roy–Vetterli |
| **H9** | Cost-aware stopping terminates below six legs | D7b | **SCORED 2026-09-16 — PASS**, at **0, 1 or 2**, so the predicted 3–4 is wrong on the low side at every one of the eight pre-registered cells. **X15's discharge makes the pass weaker than it reads:** the attainable range over that grid is `{0, 1, 2}`, the threshold is `< 6`, and the fraction admitted is **100%** — *within the grid the rule runs on, H9 could not have failed*. It is scored rather than withdrawn because it **is** falsifiable: at an assumed view move of 10 bp the count is exactly **six**, and six is a geometric ceiling no cost model can pass. The defect is in the grid, whose rungs are view magnitudes between 0.25 bp and 2 bp. §6's annotation below is honoured and does not move the verdict: at `< 4`, the priceable comparand, all eight cells still pass. *(Annotated 2026-09-15 by `AMENDMENT_A3` §6, not restated.* **"Six" is `REFERENCE_BOOK`'s count, and two of those legs cannot be priced** — the priceable comparand is `US_CASH_BOOK`'s **four**, so the bar is weaker than it reads. `AMENDMENT_A2` §7 already annotated the 3–4 into 897 or 1,194 evaluations. Flagged and left, because a third amendment touching one row is worse than the annotation.*) **Scored at 11 candidate series / 231 structures**, over 462 legs — `AMENDMENT_A6` §1 clause 3, DD120 |
| — | `SCENARIO_SIGNS` reproduces on dated windows | D12 | *no prediction; the matrix is under-determined and D12 replaces it* **Reported 2026-09-28 by D12** (`Verdict.REPORTED`): `US_CASH_BOOK`'s leg signs are −, −, −, + in NBER_2020 and +, +, −, + in RATES_2022 (2y, 10y, breakeven, euro), with no window classified into the source's scenarios |
| **H11** | A hedge sized off *disclosed* exposure over-hedges vs one sized off *measured* exposure, by > 30%, for ≥ 70% of the cohort | D17 | PASS **SCORED 2026-09-27 by D17 — PASS**, 24 of 32, 0.750, Clopper–Pearson [0.566, 0.885], median k −9.17. It passes mostly on k ≤ 0 (22 of the 24), the market's own loading on the one-year yield and the dollar, not a stated exposure larger than a real one (D17 §14, DD207). On cash flow, beside, it does not hold: 0.625 |
| **H12a** | The cheap linear structure captures ≥ 90% of the complex one's variance reduction | D21 | PASS. **SCORED 2026-09-29 by D21 — PASS**, 7 of 7 eligible firms, median capture 1.300 (D21 §13) |
| ~~H12b~~ | ~~The markup gap against the 424B2 population~~ | ~~D20~~ | **annexed with D20**, §4.1 |
| **H13** | Unconstrained cost minimisation selects a leverage > 1 structure the gate must refuse | D18 | PASS — the KIKO mechanism, and it should fire. **SCORED 2026-09-26 by D18 — PASS**, 3 of 3 case clients at every rung of both volatility ladders, **and it could not have been otherwise**: put–call parity makes the 2:1 ratio forward the only structure on D18's menu that beats the forward at zero premium, at any volatility above zero (D18 §3, X15). The pick belongs to the objective, not to the market: a minimiser that sees net premium and rate, and not optionality sold, walks into leverage every time. The gate-constrained pick is the plain forward in every case |
| ~~H14~~ | ~~OOS R² < 0.5 **and** < half its in-sample value~~ | ~~D21~~ | **Withdrawn as written.** The conjunction is vacuous: in-sample R² ≤ 1, so the decay clause strictly implies the level clause and the level clause can never bind. `AMENDMENT_A1` §5.1 |
| **H14a** | OOS Ederington hedge-effectiveness R² **< 0.5**, for ≥ 70% of the cohort | D21 | PASS — the weaker bar. **SCORED 2026-09-29 by D21 — PASS**, 32 of 32, and a claim the record could not fail in practice: every firm was already below 0.5 in sample (DD232) |
| **H14b** | OOS Ederington R² **< ½ × its in-sample value**, for ≥ 70% of the cohort | D21 | PASS — **the finding that matters most.** H14b ⊆ H14a by construction, so the informative count is firms in H14a that are *not* in H14b: weak but not decaying. **Scored 2026-09-29 by D21: refuted.** 21 of 32 (0.656), where 70% was needed. It is carried by noise on the rates-only firms, 13 of 14 of which count (DD232); on the resolved subset it takes 10 of 18. Weak but not decaying: 11 |
| **H15** | Crisis-conditional hedge effectiveness is under half the unconditional value, for ≥ 60% of the cohort | D22 | PASS — the hedge fails on the state that motivated it. **Scored 2026-09-28 by D22: not performed**, refused by name (DD180): the admitted daily equity route serves the last 100 sessions only |
| **H16** | Peak hedge-leg mark-to-market drawdown exceeds 25% of trailing operating cash flow for ≥ 1 case client. **An existence claim** — n = 3 cannot support a prevalence reading and none is implied | D22 | PASS — the Metallgesellschaft mechanism. **SCORED 2026-09-28 by D22 — PASS**, four of six client-windows: ExxonMobil 541% and 1,196% of trailing operating cash flow, GE 62% and 404%, AT&T 0% (the joint registration §14) |
| **H17** | The structural-versus-measured gap is **asset-class conditional**: the ratio (structural ÷ measured) has cohort median **> 2.0 for FX and commodity** and **< 1.5 for rates** | D17 | PASS on both halves — pass-through and operational hedging absorb roughly two-thirds of FX and commodity exposure before it reaches returns, while a debt footnote read is already net of financial hedging. **Also a self-diagnostic**: a factor-of-three wedge on rates means the swap overlay is being missed **Scored 2026-09-27 by D17: refuted.** Currency and crude pooled: median 1.55, not above 2.0; rates: median +∞, not below 1.5, because 22 of 25 rates k are negative. Currency alone is 0.130, measured far *above* stated, and crude holds alone only because the rule reads four producers as short (D17 §14, DD207). On cash flow, beside: PASS, the rates half on noise |

D3a's claims register holds this table as data. A row with no scorer fails the build.

**Interval methods are fixed here, before any number exists** (`AMENDMENT_A1` §5.3):
cohort prevalence by **exact Clopper–Pearson**, per-firm effect sizes by **stationary
bootstrap** (Politis–Romano, 10,000 resamples), cohort medians by **bootstrap percentile**.
**The effect size with its interval is the headline and the binary bar is reported beneath
it** — because at n = 40 an outcome of exactly 28/40 clears the ≥ 70% bar while
carrying a 95% interval of [0.535, 0.834]. The bar is a decision rule about the sample; it is
not a claim about the population, and the paper must not write it as though it were both.
The pre-registered thresholds do **not** move.

---

## 6. What would still make this wrong

Inherited from `PLAN_deskcraft.md` §9, plus what today added:

- Any covariance fitted on the window it is stress-tested against.
- The effective-number-of-bets result being dropped because it is unflattering.
- **A cost number reported as a measurement.** It is a calibrated assumption from public
  sources, and §3.5's sensitivity ladder is what keeps that visible.
- **A flag threshold set after seeing which legs it fires on.** F1–F4's thresholds are fixed in
  D9's pre-commit, before any book is scored.
- **A claim in the register with no scorer**, which D3a makes a build failure rather than a
  matter of anyone remembering.

Added 2026-09-08 with the solutions layer (`docs/RESEARCH_client_solutions_layer.md`):

- **A structure quoted as a price.** Free data yields a fair value and a cost band. A *bid*
  needs a dealer's curves, CVA/FVA/KVA and the client's credit. Output that reads as executable
  is a defect.
- **An exposure taken from a filing without measuring it** — the H11 error, committed by the
  tool built to detect it.
- **A suitability gate that warns instead of refusing.** A warning is a thing a salesperson
  clicks through.
- **A cohort selected, filtered or trimmed after seeing what it produces.** The selection rule is fixed in D17's pre-commit and the drop count is reported; a cohort chosen to reproduce the exposure puzzle would reproduce it.
- **The three-case tier creeping.** The cohort widened on a power calculation; the case tier did not, because each case is hand-built and hand-defended. Growing it silently is
  the same scope failure the original bound was written to prevent.
- **Coverage reported without its denominator**, or presented as the thing being maximised. Coverage against *disclosed* exposure is the H11 error restated as a headline number.

Added 2026-09-08 by `AMENDMENT_A1`:

- **A bar whose stated conjunction overstates its own strictness.** H14 required OOS R² < 0.5 *and* < half in-sample, when the second clause implies the first unconditionally. Every multi-clause bar in the register is now checked for implication before it is registered, not after it is reported.
- **A pilot that measures.** A feasibility probe reporting any effect size — a gap, an R², a coefficient — converts every downstream threshold from a prediction into a number chosen with knowledge of the answer. The blindness rule and its schema test are what keep the de-risking free.
- **A prevalence bar reported as a population claim.** §5 now names the interval method and puts the effect size first.
- **A package added without spending the budget.** `PACKAGE_BUDGET` is read from this table by D3a's register; adding a row without editing the budget in the same commit turns the gate red.
- **A checkpoint tagged that is not real.** CP-1's test is the one-page write-up answering *what do I hold if everything stops here*, written for a reader who has not seen the plan. If that page cannot be written, the checkpoint has not been reached.
- **A gate listed in §9 that cannot produce a verdict.** `lint-imports` was listed as mandatory before every commit from D1 and has never run: a missing `include_external_packages`, and beneath it a contract import-linter cannot express. Every gate named in §9 must be demonstrated to run, not merely declared.

Added 2026-09-15 by `AMENDMENT_A2`, after D7a found §3 does not survive being implemented and an
audit found §1 has the same defect:

- **A cost hurdle set after seeing which structures it stops on.** §1.3 named one, §3 fixed none, and
  §1.4 makes the hurdle identical to the leg count H9 predicts — with H9 scored by the package that
  would have chosen it. Fixed now at `costs.COST_HURDLE = 1.0`, before D7b's pre-commit exists, and
  not a free parameter: any other value is a rung of §3.5's ladder. This is the F1–F4 bullet above,
  which was written for D9's flags and not for the threshold that decides H9.
- **A bias register that is complete in one direction.** Every row of `costs.BIASES` ran
  `OVERSTATES_COST` / `FEWER_LEGS`, which read together say a leg count is a lower bound — while the
  cost model's largest effect, three of §3.2's four terms being absent, runs `UNDERSTATES_COST` /
  `MORE_LEGS` and was not a row. A register whose scope silently excludes the biggest term reads as
  a bound and is not one (DD84).
- **A commissioning cross-reference pointing at a number that does not exist.** §3.3's *"both already
  graded"*, §1.3's hurdle and §1's *"≈1,800 evaluations"* are three instances, and the first was found
  only by implementing it. Every *"fixed in §n"* in this document is a claim about §n, and claiming it
  does not make it so.

---

## 7. The sequence, and the two findings that set it

*Added 2026-09-17, at the owner's instruction that the integration be recorded in the plan rather
than left in a conversation. Carries **DD119** and nothing else — no bar, no code, no package, no
row moved.*

`AMENDMENT_A5` measured what free data reaches. **DD118** decided what may be read against what may
be committed. Neither says **what to build next**, and it does not follow from either: A5 opened
four carried items, struck two claims in this document, and left **seven** owner decisions standing
at its §9. So the order below is decided rather than implied — an order arrived at by reasoning and
then left unwritten is precisely the failure mode `CARRIED_ITEMS.md` exists to prevent, and
`RIDER_the_register_counts_itself_in_prose.md` is standing evidence that it happens here.

> **DD119 — the integration order.** The steps at §7.3 run in the order written, and the order is
> load-bearing rather than tidy: each step either makes a later one cheaper, or becomes impossible
> to do honestly once a later one has run. Where a step is blocked on a decision this document may
> not take, `AMENDMENT_A5` §9's row is named and the step stops there rather than guessing.
> **Nothing in this section adds a package, moves a row of §4, or un-annexes anything.**

### 7.1 A5 did not scatter work across the order — it loaded D8

The sweep reads like a document about *data*, and the instinct it invites is to look for a new place
to put the work. There is no new place. Walking the register's thirteen open items to their owners
puts most of them on the **next core package**.

| Open items | Owner | Which |
|---|---|---|
| **5 of 13** | **D8** *(next)* | **X2** (the frequency-policy half), **X6**, **X11** (the data half), **X18**, **X22** |
| **3 of 13** | **D9** | **X3** (the fix half), **X17**, **X19** |
| **2 of 13** | **D16** | **X20**, **X23** |
| 1 each | D12, D15, D17 | **X13**, **X14**, **X21** — and D17 also holds **X2**'s four-class half |

*X2 has two owners and is counted under each; the thirteen distinct items are X2, X3, X6, X11, X13,
X14, X17, X18, X19, X20, X21, X22, X23.*

*(**ANNOTATED 2026-09-17.** The table above is left as written and its arithmetic has moved twice
since. X23 closed (DD121), X24 opened and closed (DD120, DD122), X25 opened. The register now
stands at **thirteen open**, and D8's share is **6 of 13** — X2, X6, X11, X18, X22, X25. §7.1's
finding is unchanged and its margin is unchanged: the free-data sweep and the three amendments
that followed it loaded the next core package rather than scattering work across the order.)*

**Three of D8's five moved on 2026-09-17, and all three moved towards it.** X22 was *opened* by
DD118, because the rule sorts a graded source three ways and `sources.py` expresses one. X11 was
*narrowed twice* and now has two routes rather than one. X2's daily-credit half was *measured* at
A5 §4 and found to be a licence wall rather than a preference, which turns the frequency policy
from a fetch into a decision. **The free-data sweep raised D8's pre-commit load; it did not lower
it.**

And C76 makes that binding rather than advisory: once D8 lands, its pre-commit must say in writing
what became of each of the five, or the suite is red. **There is no separate task that folds A5
into the plan. D8's pre-commit is the fold**, and D9's is most of the rest — the two of them are
named on eight of the thirteen.

### 7.2 The convexity question — what is already expressible, and the one measurement left

Recorded here because it was asked and answered outside the repository, and an answer that lives
only in a conversation is worth nothing to the next reader.

**1. The vocabulary does not grow, and no amount of data grows it.** DD63 closed the grammar at six
terms — three fitted (`LEVEL`, `SLOPE`, `CURVATURE`), three stated (`REAL_VS_NOMINAL`,
`CREDIT_VS_RATES`, `CROSS_MARKET`) — and `factors.py` carries the reason in its own
words, at its module docstring: the three are stated *"because a contrast between two curves is a
definition and calling it fitted would borrow credibility from an arithmetic that never touched
it."* They are stated **permanently and by design**, not for want of a series. Adding TIPS reals, bills or a yen leg changes **which of the six have a
tradeable series behind them** — reach, not vocabulary size. A5 §9 row 2 is a decision about reach.

**2. Curve convexity is already expressible. Payoff convexity is not.** `CURVATURE` is one of the
three *fitted* terms, the butterfly is its discrete second difference, and **165 of D7b's 231
structures are butterflies**. What the engine cannot express is a convex *payoff* — asymmetric P&L
in the underlying — because that needs an option, an option needs a surface, and §5.2 of A5
measures that free data provides no **rates** vol surface at any licence. The two are different
objects and were being asked as one question.

**3. Futures would buy leverage, not convexity.** A future is linear in its underlying; it changes
funding and not shape. The one free dated exception measured is the EIA's NYMEX WTI contracts 1–4 —
~~public domain~~ *(struck 2026-09-26, DD176: CME Group's prices, republished with permission)*, individually dated, from 1983 — which buys a commodity **term-structure** direction
and stops **2024-04-05**, inside the window it would be scored on (**X21**, §0 item 6).

**4. The cheap axis is coefficients, not series, and it is gated on a carried item rather than on
data.** A5 §6.1 corrects an earlier claim: PCA-weighted butterflies need **no new data and no D8**,
because `factors.NominalSpectrum.loadings` already carries D6's DEV loadings, restated at exact
equality and held by C60. What blocks the direction is that the generator emits unit coefficients
only — `(+1)`, `(+1,−1)`, `(+1,−2,+1)` — and that **X17** means a DV01-matched structure cannot
*declare* the neutrality it has. A unit-coefficient fly is a curve-shape view, not a neutral
convexity harvest, and A5 §0 row 11 measures why that matters: a `SLOPE UP` book leaks **+0.416 /
+0.241** into `LEVEL` at 1bp / 10bp. **So the expansion with the best ratio of expressive power to
cost needs no series at all — and it runs through D9, not through a data decision.**

**5. Which leaves exactly one measurement outstanding, and it is cheap.** §4.1's D19 row is the
plan's existing slot for this question, and its stated output already *is* the answer above: *this
exposure requires convexity; a vanilla is indicated; pricing it needs a surface free data does not
provide.* But that half-decline now rests on **seven inputs nobody has read a licence for** — eight named,
one graded — which A5 §5.2 asserts are free without having read them. Closing it is a licence read per input — no
fetch, no egress, no package, no budget, the same method A5 ran over twenty-two sources in a day.
**X23**, owned by D16. Until it runs, un-annexing D19 is a preference; after it, the argument is a
measurement either way it comes out.

*(**Run 2026-09-17**, `RIDER_the_vol_surface_is_licensed_not_absent.md`, **DD121**.* **It came out against.** *The eight are licensed against derivation in the originator's own words, three of them are not obtainable free at any route found, and DD118 refuses every route — so item 2 above is now exact rather than provisional: payoff convexity is not expressible, and the reason is a licence rather than a missing surface. The one measurement §7.2 said was outstanding is no longer outstanding, and the cheap axis at item 4 — coefficients through D9 — is the whole of what is left.)*

### 7.3 The sequence

| # | Step | Why here and not later |
|---|---|---|
| 1 | **Land what is on disk.** `AMENDMENT_A5` is untracked and §1 of the register already cites it; the suite is green with thirteen open | Every step below cites a document that is not yet in the tree, and the register's state is currently the working tree's rather than the repository's |
| 2 | **The candidate-set rule, pre-registered, before any series is added** — A5 §9 row 3 | **The only step that gets harder if deferred.** H3 and H9 are scored **PASS** against an eleven-series, 231-structure universe; A5 §0 row 13 puts twenty series at **1,350** and thirty at **4,525**. Once a series has landed, any rule can be written to fit what landed, which is selection after the fact on two already-scored claims. It is an amendment, not a package, and **no row of §4 owns it** — which is why it is named here. *(**DONE 2026-09-17**: `AMENDMENT_A6`, **DD120**, bar **C116**, and **X24** opened against `AMENDMENT_A5`'s own admission statistic. The rule refuses all three of §9 row 2's arms today, for three different reasons — a duration the cost model cannot compute, a slot already filled, and a seventh grammar term DD63 closed — and names what would change each. Row 2 stays the owner's. **X24 closed 2026-09-17 by `AMENDMENT_A7`**: the projection ran, the basis swap the item named is worth **≤0.002** to every nominal candidate, and the window clause 2 silently computes over turned out to be **17.3% of the panel** — on which `DGS3MO` does not move at all on half its days and its whole unexplained residual is one basis point. **DD122** amends clause 2 in three parts and **C117** holds the sample count as an equality.)* |
| 3 | **Grade D19's seven ungraded vol inputs** — **X23**, §7.2 item 5 | A licence read, no fetch, no package, no budget: the cheapest measurement remaining anywhere in the plan. It is also the only one that converts the convexity verdict from a recommendation into a record, and it is independent of steps 4–6, so it can run beside them. *(**DONE 2026-09-17**, `RIDER_the_vol_surface_is_licensed_not_absent.md`, **DD121**. The conversion happened and it went the other way: `REDISTRIBUTION_PROHIBITED` at the originator, refused by DD118 at both routes, and three of the eight not free at all. **X23 closed, X25 opened** against `sources.py`'s `VIXCLS` grade.)* |
| 4 | **D8's pre-commit, carrying five discharges**, in the order **X22 → X11 → X2 → X18 → X6** | X22 first because it is structural — everything D8 does with a graded source runs through a predicate that cannot yet express DD118's three dispositions. X11's route choice (a pinned FR 2004B fixture, or the stated `MarketDepth` already in `costs.py`) is **A5 §9 row 8** and is the owner's; the recommendation carried into the pre-commit is **state the depth**, because it costs nothing, adds no out-of-git dependency, and needs no predicate the type system lacks — which is exactly what X22 says is missing. X6 rides free. *(**PRE-REGISTERED 2026-09-22**, `RIDER_DD119_steps_4_to_6_pre_registered.md` §1, **DD129–DD131**. The step's content is written and the document is a rider rather than a pre-commit, because `closed()` reads landing from `PRECOMMIT_deskcraft_<package>_*.md` existing (DD31), so landing D8's pre-commit today would assert to C34 and C76 that D8 has been built. **Six discharges, not five** — X25 joined the list on 2026-09-17 and sits beside X22, since the disposition `VIXCLS` should carry does not exist until X22 closes. X11 takes DD128's stated depth, which also dissolves the weekly-to-annual question rather than answering it; **DD130** sets one frequency per covariance and refuses forward-filling by name, on DD122 part 3's own logic; **DD131** gives X22 a `readable` predicate and a second axis rather than a sixth `Licence` member, which would corrupt an ordering that means one thing; X18 is discharged as not owed on the route taken, with its trigger recorded; and **X6's orientation prediction is fixed before anything is fitted** — PC1 stable, **PC2 predicted to flip in at least one crisis window**, PC3 not predicted.)* |
| 5 | **D9** — **X17**, **X19**, **X3** | This is where a neutrality claim becomes available at all, so it gates §7.2 item 4's coefficient axis as well as its own three items. **A5 §9 row 5** asks whether X17 is pulled forward ahead of the rest; if the owner says yes, this step splits and the X17 half moves between steps 3 and 4. *(**PRE-REGISTERED 2026-09-22**, `RIDER_DD119_steps_4_to_6_pre_registered.md` §2. **The owner said no — DD125**, so the step does not split and all three stay in D9. X17 is unchanged; **X19 is the item with a cost that is not flat**, because until `generator.select` refuses a half-reached factor every `CROSS_MARKET` fidelity number is a number about `LEVEL`, inside the 4.991% margin H3's PASS rests on; and **X3 carries a prediction that the surviving leg set does not move**, since D7b orders by `cosine` and C111 holds that the statistic X3 is about is never read on that path — the correction lands in F3's fidelity-versus-risk split instead.)* |
| 6 | **The declines, each stated with the measurement behind it** — **X20** (D16), **X21** (D17), **X23** (D16) | These need no build. They need the decline written with its number, which is X16's standing demand. **A5 §9 rows 4, 6 and 7** are the owner's, and none of them is answered here. *(**ANSWERED 2026-09-22** by `RIDER_A5_the_six_remaining_decisions.md` — rows 4, 6 and 7 are **DD124**, **DD126** and **DD127** — and the three declines are written out at `RIDER_DD119_steps_4_to_6_pre_registered.md` §3. X23 closed under DD121, so the third decline is the **blanket option decline**, which DD121 made stronger and differently shaped: not an absent surface but a **licensed** one, with three of the eight inputs not obtainable free at any route found. X20 and X21 stay open — the first because six code sites still promise DEC-2's package and **C118** refuses the half-state, the second until D17 lands to write it.)* |

### 7.4 What this sequence forbids

- **No series is added before step 2.** Adding one re-scores H3 and H9 on a vocabulary they were
  not scored on, and no rule written afterwards can be shown not to have been fitted to it.
- **No read of a row dated after `DEV_END` as a side effect of anything above.** The first such
  read fires DD37 in **curvecast**, irreversibly, and forecloses *its* remaining budget rather than
  this repository's. X13 is D12's, and DD102 gives the trigger a commit that does nothing else.
- **D19 stays annexed.** Step 3 produces evidence for a displacement argument; it does not make
  one. §4.1's rule is unchanged: a package leaves the annex only by displacing a core package.
- **The budget does not move.** Twenty-one core, one-in-one-out, `AMENDMENT_A1` §6, checked as an
  equality by C35.

### 7.5 What this does not make complete

A5 says it about itself, and the sentence is the honest bound on everything above: *Row 1 is a list
of what was looked for, not a census. There is no register of free rate data to sweep, so recall
here is unmeasured.* Twenty-two sources is a **floor**, not a total, and the same will be true of
the seven licences step 3 reads.

Steps 2–6 make this document consistent with what was found. They do not make the search complete,
and nothing available would — which is why **X16 is standing** rather than closed, and why every
decline in this plan is asked to carry its search rather than only its conclusion.

### 7.6 Two owner decisions, 2026-09-25

*One entry each: neither moves a verdict, so neither is a document.*

> **DD138 — the seventh grammar term is declined for version 1.** `IDEATION_before_the_first_oos_read.md`
> §2 asked it: `DEXUSEU` is the one measured direction orthogonal to the curve (0.905 unexplained
> against a 0.648 hurdle) and `DD63`'s grammar has no slot for it. `DD63` is not reopened while
> D8–D22 are unbuilt. The ceiling that leaves is a **stated limitation**: the engine reaches at most
> **0.906494022** of an arbitrary view direction at any cost and any conviction, and D16 reports
> that as the engine's headline limit in place of H9's leg count. Two reasons. A term admitted
> because it raises the engine's own fidelity statistic is fitting the metric. And a grammar change
> moves C103's pool (11 series, 231 structures, 462 legs), the universe H3 and H9 were scored at
> (DD120 clause 3). **Revisit after CP-2**, as a version-2 question arriving under a new claim id,
> never as a re-score.

> **DD139 — what a view can say and what the engine measures are separate questions, and the
> second must be complete.** DD138 limits the first. `US_CASH_BOOK`, the book D9, D10 and D15
> score, holds four legs and one is `eurusd`, short €75m of `DEXUSEU`. `sensitivity.RATE_SENSE_OF`
> gives `FX_SPOT` the sense `NONE`, so a DV01-only risk figure carries that leg at zero, which is
> the omission `_priced_legs` refuses in words. **D8's covariance carries `DEXUSEU` as a risk
> factor and D9 maps an FX leg onto it.** The grammar still has no FX term and the candidate pool
> still excludes it. `DEXUSEU` is public domain (H.10) and already a panel column, so this is scope,
> not data. `us_10y_call` and `us_de_10y` stay deferred and `REFERENCE_BOOK` stays refused whole.

*Next free ids: **C128 / DD140 / X26**.*
