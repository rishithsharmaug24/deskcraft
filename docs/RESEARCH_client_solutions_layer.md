# The client-solutions layer: turning an institution's exposures into a structure

Research memo, 2026-09-08. Written **before** any package is scoped, so the design is argued
from measured facts and cited literature rather than from what turns out to be convenient.

The question: a salesperson on a dealer's corporate-solutions desk hears a client describe its
business, works out where the client is actually exposed, and proposes a structure — swap,
option, forward, note, or a combination — that addresses it. **Can that be engineered, and how
much of it is real rather than roleplay?**

Short answer: **three of the five stages are engineerable on free public data, one is
partly engineerable, and one is not engineerable at all.** The value is concentrated in the
part nobody automates, and the failure mode is pretending the last stage exists.

---

## 0. The finding that decides the whole design

**This is the same machine as the macro engine, with the target vector supplied by a balance
sheet instead of an opinion.**

| | Macro path (D6–D11) | Solutions path |
|---|---|---|
| Input | a view — "long the long end" | an exposure — "we borrow floating, sell in EUR" |
| Target | factor loading the book should have | factor loading the book should have, **sign-flipped** |
| Then | leg generator, cost model, sizing, ES, ENB, stress | *identical* |

A hedge is a book whose factor loading is the negative of the client's exposure vector. So
D6's view language, D7a's cost model, D7b's leg generator, D9's component ES and flags, D11's
CVaR sizing and D12's stress engine are **reused unchanged**. What is genuinely new is only:

1. **an exposure extractor** — turning a business into a vector, and
2. **a suitability gate** — refusing structures that cannot state what they hedge.

That is two or three packages, not a second project. It is also the strongest argument that the
existing architecture was right: if the same pipeline serves a macro PM and a corporate
treasurer, the abstraction is at the correct altitude.

---

## 1. Why corporates hedge — and why it constrains the structure

This is not decoration; it determines which structure is correct, so it has to be in the model.

[Froot, Scharfstein & Stein (1993)](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1993.tb05123.x)
is the governing result. Hedging creates value **only** because external finance costs more
than internal funds, so the point is to have cash in the states where you want to invest. The
consequence people skip: **the optimal hedge is not "eliminate variance."** It is to match cash
availability to investment opportunity. If the client's investment opportunities *rise* when
oil falls, a full oil hedge is over-hedging.

[Giambona, Graham, Harvey & Bodnar (2018)](https://people.duke.edu/~charvey/Research/Published_Papers/P134_The_theory_and_.pdf),
surveying 1,100+ risk managers, found what firms actually do: ~90% hedge to increase expected
cash flow, 70–80% to smooth earnings or meet shareholder expectations, and — the fact that
matters most here — **operational hedging is more common than financial hedging in every risk
category except FX**. A machine that proposes a derivative for every exposure is modelling a
minority of real risk management.

**Instrument choice follows from the shape of the exposure, not from taste.**
[Brown & Toft (2002)](https://www.ssrn.com/abstract=286733) derive it: with price risk alone,
**forwards are optimal**. Add quantity/production uncertainty and the exposure becomes convex,
so **options become necessary**, and customised exotics only beat vanillas when
price–quantity correlation is large and quantity risk exceeds price risk. This gives a
**decision rule the engine can implement**, and a rule that refuses complexity by default —
which is the opposite of a sales desk's incentive and therefore worth encoding.

---

## 2. The exposure need not be role-played — it is a public document

This is the finding that makes the layer institutional rather than a simulation.

**US public companies are required to publish their market-risk exposures.** Reg S-K Item 305 /
[Item 7A](https://corporate.target.com/investors/annual/2022-annual-report/10-k-report/10-k-part-ii/item-7a-quantitative-and-qualitative-disclosures-about-market-risk)
mandates *Quantitative and Qualitative Disclosures About Market Risk* — a tabular sensitivity
analysis, a sensitivity-shock disclosure, or a VaR, covering interest rate, FX, commodity and
equity price risk. Firms also file XBRL-tagged financials, and structured-note issuers file
term sheets.

All of it is free, keyless and public domain:

| Source | What it gives | Coverage |
|---|---|---|
| [EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) — submissions, companyconcept, **companyfacts**, **frames** | XBRL financials: debt, revenue by segment, currency exposure | *"These APIs do not require any authentication or API keys to access."* |
| EDGAR full-text search (`efts.sec.gov`) | Item 7A text, hedging policy, **424B2 term sheets** | **2001 → present** |
| Fair-access policy | 10 req/s, declared User-Agent with name and email | no key, no licence bar |

So a "client" can be a **real named company**, its stated exposure is a **citable public
document**, and the machine's inferred exposure can be **scored against what the company itself
disclosed**. That converts the discovery conversation from roleplay into measurement.

Constraint that must be honoured: deskcraft has **no egress** (boundary bars C2/C4). Extraction
stays in curvecast and arrives here as a committed dated fixture — the `make_sealed_panel.py`
pattern, unchanged.

---

## 3. The trap, and the best test in the whole layer

Here is where a naive build goes wrong, and it is measurable.

[Bartram & Bodnar's exposure puzzle](https://mpra.ub.uni-muenchen.de/6482/1/Exposure_Puzzle_SSRN.pdf)
and [Bartram, Brown & Minton (2010)](https://www.sciencedirect.com/science/article/abs/pii/S0304405X09002062):
firms' **measured** exposure to FX is far smaller than their **disclosed** operational exposure,
because three channels absorb it before any derivative is written —

- **pass-through** — 10–15% of exposure,
- **operational hedging** — 10–15%,
- **financial hedging**, mostly foreign-currency debt rather than FX derivatives — **~40%**.

Roughly **two-thirds of stated exposure is already absorbed**. A machine that reads "60% of
revenue is in euros" and hedges 60% of revenue **systematically over-hedges** — and an
over-hedge is not a conservative error, it is an unhedged speculative position in the opposite
direction.

This yields the layer's sharpest pre-registered test, and one a working desk would actually
want: **measure the gap** between the exposure a firm *states* and the exposure recoverable
from its returns via the [Adler–Dumas (1984) elasticity regression](https://www.sciencedirect.com/science/article/abs/pii/S0022199605000346),
and report the residual, which is the only part a derivative should address.

---

## 4. What the structure costs, benchmarked against a measured population

The second thing no sell-side tool does, for an obvious reason.

Since ~2012 SEC-registered structured notes must disclose an **"estimated initial value" below
the issue price** — the issuer's own model value, with the gap attributable to the issuer's
internal funding rate and hedging charges. Those disclosures sit in **424B2 filings on EDGAR**,
free and full-text searchable to 2001. The academic priors to score against are well
established:

| Study | Sample | Markup over fair value |
|---|---|---|
| [Henderson & Pearson (2011)](https://www.sciencedirect.com/science/article/abs/pii/S0304405X10002953) | 64 SPARQS issues | **~8%**; expected return slightly **below zero** |
| [SLCG — reverse convertibles](https://www.slcg.com/pdf/workingpapers/Valuation%20of%20Structured%20Products.pdf) | 530+ notes, 2001–2010 | 3.5–6.7% |
| SLCG — absolute-return barrier notes | 214 notes, 2006–2009 | ~4.5% |
| [Deng, Mallett & McCann — autocallables](https://www.slcg.com/files/research-papers/modeling-autocallable-structured-products.pdf) | — | ~4.74% average overpricing |

[Célérier & Vallée (QJE 2017)](https://academic.oup.com/qje/article-abstract/132/3/1469/3057435)
supply the mechanism: complexity is **not** incidental — it is used to advertise a headline
rate, and it correlates with markup. That is a testable proposition on the 424B2 population,
and it gives the engine a defensible default: **quote the cheapest structure that achieves the
stated hedge objective, and report what the complex alternative would have cost.**

---

## 5. The suitability gate, as a type rather than a warning

Two regimes govern the job directly, and both are encodable as refusals.

**US — [CFTC 17 CFR 23.434](https://www.ecfr.gov/current/title-17/chapter-I/part-23/subpart-H/section-23.434), institutional suitability.**
A swap dealer recommending a swap must have reasonable diligence to understand its risks
(*general* suitability) and a reasonable basis to believe it suits the counterparty (*specific*
suitability), including the counterparty's **ability to absorb potential losses**. The safe
harbour requires, in writing, that the counterparty exercises independent judgement and that the
dealer discloses it is **acting as a counterparty and not advising**.

**EU — [MiFID II product governance](https://www.esma.europa.eu/sites/default/files/library/esma35-43-620_guidelines_on_mifid_ii_product_governance_requirements_0.pdf).**
Manufacturers must identify a target market per product; ESMA's guidance is explicit that for
very complex, risky products a comprehensive assessment **may yield no compatible target market
at all**. A structure with no target market is a structure that should not exist.

**And for accounting reality — [IFRS 9](https://www.ifrs.org/-/media/project/fi-hedge-accounting/draft-requirements/published-documents/draft-hedge-accounting.pdf).**
Hedge accounting requires an *economic relationship* between hedged item and instrument, that
credit risk does not dominate it, and that the **hedge ratio used for accounting equals the one
used for risk management**. A treasurer who loses hedge accounting gets P&L volatility — often
the very thing they were hedging to avoid. So *"does this qualify?"* is a first-class output,
not a footnote.

Two structural notes worth making:

- **The repo's existing imperative ban is already the safe-harbour posture.** C6 forbids
  rendered imperatives, so the readout describes and never recommends — which is precisely what
  23.434(b)(3) requires a dealer to disclose in writing. The constraint that was adopted for
  craft reasons turns out to be the regulatory one.
- **The gate should have the shape D2 gave `Neutrality`: an iff.** A structure must name the
  exposure it hedges and its worst case, or it is untypeable — not warned about, *unconstructible*.

---

## 6. The failure cases, operationalised into computable refusals

These are the disasters the layer exists to not reproduce, each reduced to a number.

**KIKO — Korea, 2008.** Knock-in/knock-out FX options sold to exporters as zero-cost hedges;
**571 SMEs lost $2bn+**, many bankrupted, and Korea's FSS eventually directed banks to
compensate 15–41% for mis-selling. The pathology is exact and computable: the **knock-out killed
the hedge precisely when it was needed**, while the **knock-in doubled the obligation**. So:

> **Leverage ratio** = worst-state notional the client is obliged to transact ÷ notional of the
> actual underlying exposure. KIKO's was ≥ 2. **A structure with leverage > 1 is not a hedge**,
> and the engine refuses to call it one.

**Metallgesellschaft, 1993 — ~$1.06bn.** A stack-and-roll of short-dated futures against
long-dated delivery obligations. The [Culp–Miller](https://www.mit.edu/~jparsons/publications/Maturity%20Structure%20of%20a%20Hedge%20Matters,%20Jnl%20Applied%20Corp%20Fin%201995.pdf)
defence treated basis risk as minor; the maturity-structure critique showed it was not. So:

> **Maturity mismatch and funding are reported separately from price exposure.** A hedge that is
> right on price and wrong on *when* is the canonical way to be right and insolvent.

**Lehman minibonds, 2008.** Credit-linked notes whose embedded swap was guaranteed by Lehman.
Retail investors bought a product whose protection evaporated with the issuer. So:

> **Issuer/counterparty credit is a leg, not a caveat** — and it is *wrong-way* whenever the
> hedge pays out in the states where the dealer is weakest.

**"Zero cost" is the tell.** Zero-cost collars and structured forwards are zero-cost because the
client **sells** optionality. Every one of the 2008 corporate blow-ups had this shape. The
engine therefore reports **premium paid and optionality sold as two separate numbers, never
netted to zero.**

---

## 7. Options and volatility — better than previously declined

The blanket "no free implied-vol surface" decline was measured for Treasuries (`VXTYN` ran
2014-11-14 → 2020-05-15 and was discontinued) and then over-generalised. Verified free today at
[Cboe historical data](https://www.cboe.com/tradable-products/vix/vix-historical-data):

| Series | What it gives | History |
|---|---|---|
| **VIX** | ATM-ish 30-day equity index vol | **1990 →** |
| VIX9D / VIX3M / VIX6M | **term structure** | shorter |
| VVIX | **vol of vol** | 2007 → |
| SKEW | risk-neutral third moment, [BKM-style](https://acfr.aut.ac.nz/__data/assets/pdf_file/0008/328931/Pakorn-Bakshi,-Kapadia,-and-Madan-2003-Risk-Neutral-Moment-Estimators.pdf) | to be probed |
| **OVX / GVZ** | **crude oil** and **gold** implied vol | 2007 → |
| VXEEM | EM equity implied vol | — |
| [EIA WTI contracts 1–4](https://www.eia.gov/dnav/pet/PET_PRI_FUT_S1_D.htm) | dated futures curve, public domain | **1983 →** |

Four free parameters — **level, term structure, skew, vol-of-vol** — are not a surface, but they
are enough for a **stated parametric surface** whose approximation error is reported on the
sensitivity ladder, exactly as cost is. So:

- **Vanilla options: priceable** under a declared parameterisation, with the ladder mandatory.
- **Path-dependent exotics (autocallables, KIKOs): stressable, not priceable.** They can be
  shown to a client as *what it does to you*, never quoted as *what it is worth*.

That is a real reversal of the earlier decline, and it is the honest half — the half that stays
declined is the half where free data genuinely runs out.

*(**Annotated 2026-09-17 by `RIDER_the_vol_surface_is_licensed_not_absent.md`, DD121 — X23's close.***
***The reversal does not survive a licence read, and "verified free today" is why.*** *What was verified
was that the numbers are visible at no charge. Cboe's Terms & Conditions permit downloading **one
copy for personal non-commercial use** and refuse, without prior written consent, to* **"create a
derivative work (for example, a financial product, service or index) from"** *them — and a stated
parametric surface fitted to these parameters is the clause's own example. Grade* **`REDISTRIBUTION_PROHIBITED`**, *refused by DD118 at this route and at FRED.*

*And the table above over-counts what the linked page carries. It offers* **five** *of these —
VIX, VVIX, VIX9D, OVX, GVZ.* ***VIX3M, VIX6M and SKEW are not on it***, *and their history is directed
to Cboe DataShop, which is paid. So of the four free parameters this section names — level, term
structure, skew, vol-of-vol —* **two are not obtainable and the other two are licensed against the
use proposed.** *The blanket decline is restored, with the better reason this section was right to
demand.)*

---

## 8. What cannot be engineered, stated plainly

Recorded in the shape §4 of the plan uses, because an institution will look for exactly this
list and its absence is what makes a pitch read as naive.

| Not engineerable | Why |
|---|---|
| **The relationship** | The most valuable input — what the CFO is actually worried about, what the board will approve — is private and often unstated. Item 7A tells you the exposure, never the anxiety. |
| **Axe and inventory** | Where the desk *wants* risk determines the price a client gets. Never public. |
| **Executable pricing** | Needs the dealer's own curves plus CVA/FVA/KVA and the client's credit. Free data gives a *fair value*, not a *bid*. |
| **CSA, initial margin, credit terms** | Bilateral and private, and they frequently dominate the economics. |
| **Whether the client tells the truth** | Firms understate exposures they have not hedged. |

And the one that must be said out loud: **a salesperson is paid partly to sell.** A system that
optimises for the client — quoting the cheapest structure that meets the objective and refusing
leveraged "zero-cost" packages — models the job **as it should be**, not as it is. That is a
defensible choice and probably the only one worth publishing. But it is a choice, it will be
noticed, and it belongs in the paper rather than in a footnote.

---

## 9. Scope — revised 2026-09-08 on a power calculation, not a preference

The original bound was three named companies and two asset classes. It was wrong, and the
reason is arithmetic rather than judgement.

**An exact binomial sign test on n = 3 cannot reject at 5% even if all three firms show the
effect.** The most extreme achievable two-sided p is **0.2500**. H11 and H14 as originally
written were therefore *vacuous, not weak* — constructed so that they could not fail. That is
precisely the defect the build order's own power table exists to catch, committed here by the
document that wrote that table.

Computed before the scope was set, sign test at p0 = 0.5, two-sided 5%:

| n | best achievable p | power if 70% of firms show it | if 75% | if 80% |
|---|---|---|---|---|
| 3 | 0.2500 — **cannot reject** | — | — | — |
| 5 | 0.0625 — **cannot reject** | — | — | — |
| 6 | 0.0312 — requires unanimity | 0.118 | 0.178 | 0.262 |
| 15 | 0.0000 | 0.297 | 0.461 | 0.648 |
| 20 | 0.0000 | 0.416 | 0.617 | 0.804 |
| 30 | 0.0000 | 0.589 | 0.803 | 0.939 |
| **40** | 0.0000 | **0.703** | **0.897** | **0.981** |

**n = 6 is the floor for the test to be capable of rejecting at all. n = 40 is the first value
where a 70%-prevalence effect is more likely than not to be detected.**

### 9.1 Two tiers, which move independently

The widening is disciplined by cost, because the two halves of this layer have wildly different
marginal costs per client.

| Tier | Scope | Packages | Why this size |
|---|---|---|---|
| **Measurement cohort** | **n = 40** US public companies | D17, D21, D22 | Same extractor, same regression, keyless public-domain API. The marginal cost of the 40th firm is approximately the cost of the 4th. Statistical claims need a distribution, not three anecdotes |
| **Case studies** | **3** named companies | D18, D19, D20 | Each structure is hand-built and hand-defended. Three is enough to show the framework generalises; twenty is a different project |

**Asset classes go from two to four** — rates, FX, commodity, and credit — because credit
(`BAA10Y`, `AAA10Y`) and commodity (EIA dated WTI, per §0 item 6 of the build order) are already
graded in the existing leg universe. This costs nothing new and it is what lets the cohort
screen select on exposure type rather than on availability.

### 9.2 The cohort must be selected mechanically, or the finding is manufactured

A hand-picked cohort would reproduce the exposure-puzzle literature by construction. The
selection rule is fixed in **D17's pre-commit, before any exposure is extracted**: a dated index
membership snapshot, a filing-completeness filter (a 10-K with an Item 7A quantitative
disclosure and the XBRL facts the regression needs), and a deterministic ordering. Firms that
drop out do so on a stated rule and the drop count is reported.

The three case studies are then drawn **from within the cohort**, named in advance, so the deep
work cannot be a different sample from the statistical work.

---

## 10. Pre-registered hypotheses, predictions fixed before any run

> **Superseded in part, 2026-09-08, by `AMENDMENT_A1_probe_freeze_split.md`.** The register
> in `BUILD_ORDER_D3_D16.md` §5 is the single source of truth; this table is kept for the
> reasoning behind each bar. Four rows changed and the reasons are worth reading rather than
> just applying:
>
> - **H14 was withdrawn as written.** Its two clauses are not independent: in-sample R² is
>   at most 1, so “OOS R² < ½ × in-sample” strictly implies “OOS R² < 0.5”.
>   The level clause can never bind, and the bar therefore advertised a strictness it did not
>   have. Split into **H14a** (level) and **H14b** (decay), with H14b ⊆ H14a stated.
> - **H12 splits.** H12a (variance reduction) moves to D21; H12b (the 424B2 markup half) is
>   annexed with D20.
> - **H16 is an existence claim**, not a prevalence one. n = 3 cannot carry a rate.
> - **H17 is new** — the structural-versus-measured gap is asset-class conditional. §3's
>   pass-through and operational-hedging channels are FX- and commodity-specific, so a debt
>   footnote read — already net of financial hedging — should show no comparable wedge.
>
> And the bars are now reported effect-size-first with named interval methods, because at
> n = 40 an outcome of exactly 28/40 clears the “≥ 70% of the cohort” bar while
> carrying an exact 95% interval of **[0.535, 0.834]**. The bar is a decision rule about the
> sample, not a claim about the population.

| # | Claim | Bar | Predicted |
|---|---|---|---|
| **H11** | A hedge sized off *disclosed* exposure over-hedges relative to one sized off *measured* exposure | Naive notional exceeds Adler–Dumas residual notional by **> 30%** for **≥ 70% of the cohort** | **PASS** — Bartram–Bodnar say ~⅔ is pre-absorbed |
| **H12** | The cheap linear structure captures most of the benefit of the complex one | Forward/swap achieves **≥ 90%** of the variance reduction of the best structured alternative, at lower modelled cost | **PASS** |
| **H13** | Cost minimisation alone selects a structure the suitability gate must refuse | The unconstrained cost-minimiser selects a leverage > 1 "zero-cost" structure in **≥ 1 of 3** cases | **PASS** — this is the KIKO mechanism, and it should fire |
| **H14** | There is no clean hedge. Minimum-variance hedge ratios degrade badly out of sample | Out-of-sample [Ederington](https://onlinelibrary.wiley.com/doi/10.1002/fut.3990120207) hedge-effectiveness R² **< 0.5**, and **< half** its in-sample value, for **≥ 70% of the cohort** | **PASS** — and this is the finding that matters most |
| **H15** | The hedge decorrelates from the exposure exactly when it is needed | Ederington R² computed *within* the five dated crisis windows is **< half** its full-sample value for **≥ 60% of the cohort** | **PASS** — i.e. the hedge fails conditionally on the state that motivated it |
| **H16** | A hedge can be correct on price and fatal on cash | Peak cumulative mark-to-market drawdown on the hedge leg, over the replay windows, exceeds **25% of the firm's trailing annual operating cash flow** for ≥ 1 of the 3 case clients | **PASS** — the Metallgesellschaft mechanism, and VaR cannot see it |

**H14 is the point of the whole layer.** Every pitch book in this business shows a hedge that
works. The measured claim that the hedge *decays*, with a number attached and the decay
pre-registered before it was computed, is worth more than any structure the engine proposes —
and it is the same result the observable→instrument work predicts from the other direction.

---

## 11. What would make this wrong

- **A structure quoted as a price.** Free data yields a fair value and a cost band; a *bid*
  requires a dealer's book. Any output that reads as executable is a defect.
- **An exposure taken from a filing without measuring it.** That is the H11 error, committed by
  the tool built to detect it.
- **A markup benchmark drawn from the products the engine likes.** The 424B2 comparator set is
  defined by structure type and tenor **before** any structure is proposed.
- **A suitability gate that warns instead of refusing.** A warning is a thing a salesperson
  clicks through. D2 settled this shape already: it is an iff, or it is decoration.
- **Three demonstrations becoming twenty.** §9 is a scope bound, and abandoning it silently is
  the most likely way this project fails to ship.

---

## 12. The engineering claim, and where the prediction actually hides

This layer was proposed on the reasoning that hedging requires no forecast: the target is given
by the client, so finding the instrument combination that meets it is optimisation rather than
prediction, and should therefore yield to pure engineering.

**That reasoning is right about the first moment and wrong about the second, and the distinction
decides what this layer may honestly claim.**

What is genuinely absent is real, and it is the reason this layer is more tractable than a
directional model: **no view on the level of anything is required.** Nothing here needs rates to
rise, the dollar to fall, or a spread to tighten. The objective is well-posed, and under an ES
constraint it is convex - a linear program (D11), not a search. In that specific sense the claim
holds and the engineering is the work.

But three estimates sit underneath it, and each is a forecast whether or not it is called one:

1. **The exposure is an estimate, not a datum.** The disclosed number is management's
   characterisation; the usable number is an Adler-Dumas regression coefficient with a standard
   error and no guarantee of stationarity. Hedging off it assumes the sensitivity measured
   in-sample persists over the hedge horizon. That is a prediction - and section 3 says it is
   systematically biased before it is even unstable.
2. **The hedge ratio is a covariance forecast.** Ederington's h* = rho*(sigma_S/sigma_F) is
   fitted on history and applied forward. Every hedge ratio in existence is a claim that a
   second moment will hold.
3. **Basis risk is constitutive, not residual.** If an instrument matched the exposure exactly
   there would be no problem to solve. The problem exists *because* it does not match, and that
   gap is stochastic. No amount of engineering removes it; engineering only chooses which basis
   you are exposed to.

So the correct statement is that **hedging replaces a first-moment forecast with a second-moment
forecast.** That is a genuine and large improvement - variances and correlations are far more
persistent than returns - which is why the intuition is directionally right. It is not zero, and
**H14 is the pre-registered measurement of how far from zero it is.**

---

## 13. Why maximum coverage is the wrong objective

The natural objective is: hedge as much of the exposure as possible, leave as little uncovered
as possible. It is also the objective that produced KIKO, and it fails on three independent
grounds.

1. **Theory says full coverage is not optimal.** Froot-Scharfstein-Stein: hedging creates value
   by matching internal cash to investment opportunity, not by minimising variance. Past the
   point where cash covers the investment programme, the marginal hedge buys nothing and pays
   the spread. Giambona et al.'s 1,100 risk managers say the same thing in practice.
2. **Coverage is measured against the wrong denominator.** Section 3: roughly two-thirds of
   stated exposure is pre-absorbed. Hedging 100% of the *stated* exposure is roughly 300% of the
   *measured* one - a large speculative position wearing the word "prudent".
3. **Coverage is cheap to buy, and that is precisely the danger.** The only way to raise coverage
   without paying premium is to sell optionality. Every structure in section 6 has that shape.
   **Coverage-maximisation and leverage-minimisation are in direct conflict**, and any system
   that maximises the first will walk into the second's boundary and find KIKO waiting there.

**Coverage is therefore an output that is always reported, and never a target that is
maximised.** The objective the engine actually optimises is:

> **Maximise measured residual-risk reduction per unit of modelled cost, subject to
> leverage <= 1, a floor on crisis-conditional effectiveness (H15), and a funding-path
> constraint (H16).**

Coverage appears in the readout as a number with its denominator named - *measured* residual
exposure, never disclosed exposure - beside what it cost and what was sold to obtain it.

---

## 14. The crisis question - what VaR missed, and what replaces it

The concern that a hedge leaves correlated risk uncovered, and that this is the failure mode
where VaR did not work, is correct and is the sharpest constraint on the design. Four distinct
mechanisms hide under it, and they need four different answers.

**1. Correlations move, and VaR was fitted on the calm ones.** Answered by machinery that already
exists in this project rather than bolted on for this layer: **ES at 97.5%, not VaR** (D9 - and
the sub-additivity exhibit is a bar, because VaR can report a diversified hedge as riskier than
its parts and thereby argue against hedging at all); **each crisis window on its own realised
correlations, never full-sample** (D12a, already `PLAN_deskcraft` section 9); and **filtered
historical simulation, not Gaussian** (D12b - measured kurtosis on this data is 4.96-15.12, so
Gaussian is refuted rather than merely doubted).

**2. The hedge decorrelates from the exposure exactly when it is needed.** This is the specific
corporate version, and it is *not* covered by the above, because it concerns the relationship
between the hedge and the thing hedged rather than the distribution of either. It becomes
**H15**: hedge effectiveness computed *conditional on* the crisis windows, reported beside the
unconditional number. An unconditional R-squared of 0.8 that falls to 0.3 in 2008 and 2020 is
not a hedge that works with a caveat - it is a hedge that works when it is not needed.

**3. Funding - the mechanism VaR structurally cannot see.** Metallgesellschaft was *right on
price*. It died on the cash path: the hedge leg's mark-to-market moved against it long before
the offsetting physical exposure paid, and the firm could not fund the interval. VaR is a P&L
measure and has no representation of *when* cash moves. **H16** measures peak cumulative
mark-to-market drawdown on the hedge leg against the firm's own trailing operating cash flow,
taken from XBRL. Honest limit, per section 8: the actual margin call depends on CSA and IM terms
that are not public, so what is computed is the **mark-to-market path**, which is data, under a
**stated** margin assumption, which is not.

**4. Wrong-way counterparty risk.** Covered by section 6: issuer credit is a leg, and it is
wrong-way whenever the hedge pays out in the states where the dealer is weakest.

**What none of this delivers is a safe hedge.** It delivers a hedge whose failure mode is stated
in advance, measured, and reported with the residual named. That is the difference between this
and a pitch book, and it is the entire deliverable.

---

## 15. The end-to-end backtest — what it can and cannot reach

The headline test is the whole loop: read a real company's filings, build the best structure the
engine can, and replay it over real history to see whether it would in fact have neutralised
what it was built to neutralise. It is the right headline. Four things decide how strong it is.

### 15.1 The construction date is what makes it a test

**A hedge built today and replayed on 2008 is a demonstration, not a test.** We know 2008
happened; we know which instruments would have paid. The exposure regression, the hedge ratio
and the structure choice must therefore use **only data available at the construction date**,
after which the book is held and walked forward into a future it could not see. This is exactly
the discipline `FitWindow` already enforces on the covariance, extended to the hedge itself.
Whether ratios are held or re-estimated on a stated schedule is declared in advance, never
chosen after seeing which one wins.

### 15.2 Which crises are actually reachable

Roughly eleven, and they are a genuinely rich set:

**1987** · **1994 bond massacre** · **1998 LTCM/Russia** · **2000–02** · **2008** ·
**2011 euro / US downgrade** · **2013 taper** · **2015–16 China and oil** · **2020 COVID** ·
**2022 inflation shock** · **2023 SVB**

Four of those — **2015–16, 2020, 2022, 2023** — fall entirely outside the DEV fit window ending
2014-12-31, so they are **genuinely out-of-sample** for anything fitted, including a hedge ratio.
That is the strongest part of the whole design: two rate shocks, a pandemic and a bank run, none
of which any fitted object has seen.

**The Great Depression is declined, and not for data-quality reasons.** The instruments do not
exist. The GSW curve begins **1961-06-14**; the modern FX market post-dates the 1971 breakdown of
Bretton Woods; the interest-rate swap market dates from 1981. There is no structured hedge
portfolio to build for 1929 because nothing in it had been invented. Stating this is better than
producing a 1929 number from reconstructed proxies, which would be a statement about the
reconstruction.

### 15.3 Monte Carlo is a supplement, and replay is primary

Simulation is worth building and is already planned (D12b, filtered historical simulation rather
than Gaussian, since measured kurtosis of 4.96–15.12 refutes Gaussian outright). But it must not
be the headline, for a reason this project has already pre-registered as **H7**: a simulation
whose correlations are fitted on history **understates realised crisis losses**, because the
correlations themselves move in a crisis. Measured on this data, three factors reproduce only
82–92% of realised crisis curve shifts — and *worst on the mildest* episode.

So the ordering is: **dated replay is the evidence; simulation fills the gaps between the eleven
crises that actually happened**, and the gap between the two is itself reported, because that gap
is the honest size of the model risk.

### 15.4 "Did it work" needs a denominator, and there are two

The firm's internal cash flows are not public, so effectiveness is measured against two
observable proxies with opposite strengths, and both are reported:

| Denominator | Frequency | Strength | Weakness |
|---|---|---|---|
| **Equity returns** | Daily | Thousands of observations; supports real statistics | The share price is not the cash flow; it embeds everything else the firm does |
| **Reported operating income / cash flow** (XBRL) | Quarterly | It is the actual thing a CFO is hedging | ~40–80 observations per firm; low power, and accounting smoothing blurs it |

Neither alone is convincing. **Agreement between them is the finding**; disagreement is
informative and is reported rather than resolved by picking the flattering one.

### 15.5 What the product then is

An instrument portfolio that neutralises a **stated fraction** of a **measured** exposure, priced
at fair value with a cost band, with its residual named, its behaviour in eleven historical
crises shown, its cash path shown, and its out-of-sample decay measured. That is a complete
institutional deliverable. It is not a tradeable quote, and it does not need to be.
