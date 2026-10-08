# D17 — the exposure extractor, fixed before any exposure is read

**Status: LANDED 2026-09-27.** §14 holds the verdicts; nothing above §13 was edited.

*Written 2026-09-26, before any exposure is extracted, before any equity price is read, and before
the first out-of-sample read: `docs/OWNER_AUTHORISATION_the_first_oos_read.md` does not exist at the
commit that adds this document. Everything below is a rule with one answer. The extraction runs in
curvecast, which has egress, and deskcraft receives dated fixtures. The package lands when the
fixtures exist and its bars run, and this status line changes then and nothing above it does.*

---

## 0. What D17 does, in one paragraph

Paper 2 treats forty real US companies as hedging clients. D17 reads what each company's 2014
annual report says it is exposed to (foreign revenue, floating-rate debt, crude-linked sales or
costs), sizes the hedge a reader of that report would build, and then asks the company's own share
price how much of that hedge it actually needed. **H11** predicts the report-sized hedge is too big
for most of the cohort. **H17** predicts it is too big by a factor above two for currencies and
crude, and by less than 1.5 for rates. D22 then replays the report-sized hedge through 2020 and
2022 (the joint registration, §6.1). This document fixes how every number is read, before any is.

## 1. What it rests on

| | |
|---|---|
| D22's lock | `PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md` §6.1 (DD171–DD180). D17 restates it and does not choose against it |
| The routes | `OWNER_ADMISSION_d22_results_only_routes.md` §1 and §6: SEC filings (public domain, curvecast's D423 identity), Alpha Vantage's free weekly adjusted prices, EIA's NYMEX WTI settlements |
| The bars' shape | `AMENDMENT_A1` §2.1 (three quantities), §5.3 (interval methods), §5.4–§5.5 (power, the bar and the claim) |
| The cohort's purpose | `RESEARCH_client_solutions_layer.md` §9.2: selected mechanically, or the finding is manufactured |

> **DD181 — the owner's four answers of 2026-09-26, recorded where they bind.** (1) Exposure is
> measured on **weekly** prices plus **quarterly operating cash flow** from the filings, reported
> side by side and never pooled. (2) H11's *disclosed* exposure is **the figures tagged in the
> 10-K's XBRL**, not Item 7A's own sensitivities. (3) EIA's WTI route is **extended to D17's
> regression**. (4) Every row after 2014-12-24 is **dropped on arrival**. The questions and answers
> are verbatim in the admission's §6, which also records two things this document did afterwards
> and the owner may refuse: the window grew from two years to five (§6 below), and answer (4) is
> applied to EIA's route as well as Alpha Vantage's.

> **DD182 — a second document may carry the registered marker, and it is this one.** C158 held the
> marker to the joint registration so that no package could use it to postpone a verdict. D17's
> case is the same case: its rules must be fixed before any exposure is extracted (research §9.2),
> its extraction runs in another repository, and its measured half waits on an owner act — a free
> Alpha Vantage key, set as an environment variable. Writing the rules and the run in one commit
> would put the rules after the extraction. C158 now holds an **equality on a declared set** of two
> documents, each with its reason, so a third is a visible edit and not a quiet use.

## 2. The cohort, restated from §6.1

**Forty firms, by rule.** Nothing here is chosen; each step is §6.1's, made mechanical.

1. **Universe.** Every row of the SEC's Financial Statement Data Sets `sub.txt`, quarters 2014q1 to
   2014q4, with `form` exactly `10-K` (so no `10-K/A` and no `10-KT`), `accepted` between
   2014-01-01 and 2014-12-24 inclusive, and `sic` outside 6000–6799. A blank `sic` is not outside
   that range and is dropped, counted. A filer with two such 10-Ks keeps the later acceptance. The
   data sets carry only filings with XBRL financial data, which is §6.1's universe condition.
2. **Ordering.** `Assets` from `num.txt`: the row with that filing's `adsh`, tag `Assets`, a
   `us-gaap` version, no co-registrant, `qtrs` 0, `uom` USD, and `ddate` equal to the filing's
   `period`. Largest first; ties by CIK ascending. A filing with no such row is dropped, counted.
3. **Walk.** Down the ordering, one firm at a time, until forty survive (i) and (ii). D23's twenty
   are eligible and not privileged.
4. **Filter (i), an Item 7A quantitative disclosure** *(widened before any request, DD190, and
   re-cut before any fixture was written, DD192: §12 holds the rule that runs)*. The 10-K's primary document is converted to
   text. The span runs from the **last** match of `item 7A` followed within 200 characters by
   `quantitative` or `market risk` (the first is usually the table of contents) to the next match
   of `item 8`. If the span is under 1,000 characters and says `incorporated` and `reference`, the
   filing's EX-13 is read instead, from its first `quantitative and qualitative disclosure(s) about
   market risk`, else its first `market risk`, for 20,000 characters. It **passes** iff it holds a
   sentence with both a dollar amount (`$` and a digit, or a number followed by `million` or
   `billion`) and a shock (a number followed by `%`, `percent`, `basis point` or `bp`), or with
   `value at risk` and a dollar amount. Drops are counted by which of the three steps failed.
5. **Filter (ii), a rates read or a currency read** (§3 below, read from the filing's own XBRL
   instance, named by `sub.txt`'s `instance` field).
6. **Filter (iii) is skipped** (DD180): the admitted daily route does not reach.

A firm with no traded share (a government corporation, a subsidiary with public debt only) is not
excluded by any of these, since the filter that would have excluded it is skipped. It stays in the
cohort, gets no measured exposure, and is counted under §5's missing-data rule.

## 3. The stated exposure, and the hedge a reader of the 10-K builds

> **DD183 — "disclosed" in H11 and in §6.1 means the figures the 10-K tags, and that makes H11 and
> H17 two statistics of one ratio.** `AMENDMENT_A1` §2.1 names three quantities and calls Item 7A's
> own sensitivity *disclosed* and the tagged figures *structural*. §6.1 hedges the tagged figures —
> *"a rates read from the debt footnote or a currency read"*, *"the facts on those members,
> sign-flipped"* — and calls that hedge *"the one H11 predicts is too large"*. The owner resolved the
> clash for §6.1's reading (DD181). So both H11 and H17 compare the tagged figure with the measured
> one: **H11 is a per-firm count, H17 a median by asset class.** That is the price. Item 7A's own
> figures are reported beside, with no verdict (§7), which is where A1's disclosure-quality finding
> lives.

All facts come from the 10-K instance: unit USD, dated at the fiscal year the 10-K reports (an
instant equal to `dei:DocumentPeriodEndDate`, or a duration ending on it that is 350 to 380 days
long). A dimensional fact counts only on a context with **exactly one** explicit member, so a fact
split by segment and by country at once is never added to its own total.

> **DD184 — the naive hedge is 100% of the stated exposure, for twelve months, in D22's instrument.**
> A reader of the 10-K hedges next year's foreign revenue and next year's floating interest, which
> is also how Item 7A usually states a sensitivity. One convention for every class, so the classes
> can be compared: **the hedge covers the next twelve months of the stated flow.**

| Class | Stated exposure N (USD) | Rule | Its weekly P&L E_t | D22's instrument |
|---|---|---|---|---|
| **Currency** *c* | Revenue attributed to *c* | DD174's members (a currency axis naming *c*, or a geographical member naming a single-currency country, curvecast `373f85a`'s table). On each member, the largest-magnitude fact whose concept's local name contains `Revenue` or `Sales` and none of `Cost`, `Expense`, `Deferred`, `Unearned`, `Receivable`, `Tax`, `Percentage`, `Proceeds`, `Allowance`, `Lease`, `Return`, `Discount`, `Gain`, `Loss`. Summed over the members naming *c*; a euro-area aggregate member, if present, replaces its member states. A currency read with no such fact is a read and not a leg, counted | + N × Δ ln(USD per *c*) | Spot *c*, `panel.FX_QUOTES` orientation |
| **Rates** | Floating-rate debt, net of tagged swaps: F_net = V + max(CP, STB) + FVH − CFH | V = `LongTermDebtPercentageBearingVariableInterestAmount`; else, on a `DebtInstrumentAxis` or `LongtermDebtTypeAxis` member whose name contains `Floating`, `Variable` or `TermLoan`, the largest-magnitude of `DebtInstrumentCarryingAmount`, `LongTermDebt`, `LongTermDebtNoncurrent`, `DebtInstrumentFaceAmount`, summed over members. CP = `CommercialPaper`, STB = `ShortTermBorrowings`, the larger taken because filers tag commercial paper both inside and beside short-term borrowings. FVH = `NotionalAmountOfInterestRateFairValueHedgeDerivatives` (pay floating, which adds); CFH = `NotionalAmountOfInterestRateCashFlowHedgeDerivatives` (pay fixed, which subtracts). A rates read exists iff at least one of V, CP, STB is a nonzero fact | − F_net × Δ y₁ | `SVENY01`, the one-year GSW zero |
| **Crude** | DD176's fact, unchanged | The largest-magnitude crude-read fact for the fiscal year whose concept names revenue or sales (long crude) or a cost, expense or purchase (short crude). It admits no firm | ± N × Δ ln(WTI, contract 2), each daily return on one contract's two settles, rolled on CME's calendar (DD176) | NYMEX WTI contract 2 |

Δ y₁ is the change in the one-year zero yield as a decimal, so − F_net × Δ y₁ is the change in a
year's interest on the floating debt. **Credit is declined** (§9, X2), as §6.1 declines it for D22.

**What each rule drops, said now.** The currency rule reads revenue and nothing else, so costs in
the currency, foreign assets and the firm's own currency hedges are absent: the stated exposure is
gross. The rates rule misses a swap that is tagged only in prose, which A1 §2.2's error 3 names and
H17's rates half is there to detect, and it counts forward-starting cash-flow hedges as live. The
crude rule inherits DD176's and DD179's: a pipeline's transport revenue that names crude reads as a
crude exposure, and a refined product is hedged with crude.

## 4. The measured exposure

> **DD185 — the measured exposure is k, the variance-minimising multiple of the naive hedge.**
> Regress the firm's weekly change in market value on the stated exposure's weekly P&L:
>
> ```
> MV_T · r_t  =  a + k · E_t + e_t,        E_t = Σ_legs N_leg · s_leg · Δf_leg,t
> ```
>
> k is the share of the stated exposure the market actually priced. The hedge that minimises the
> variance of the hedged firm is **k times the naive hedge**, so *"the naive notional exceeds the
> measured notional by more than 30%"* is exactly **k < 1/1.3**, and *"structural ÷ measured"* is
> exactly **1/k**. It is Adler and Dumas's exposure, the total regression coefficient of firm value
> on the factor, with **no market return on the right**. A firm hedges its value, and the market's
> own exposure is part of that value. Jorion's market-adjusted exposure answers a different
> question and is not computed. For a single leg, k·N is Ederington's minimum-variance position in
> that leg's instrument, the quantity D21 fits.

**Two denominators, reported side by side and never pooled** (DD181, research §15.4):

| | Equity (the verdict) | Operating cash flow (beside) |
|---|---|---|
| Source | Alpha Vantage `TIME_SERIES_WEEKLY_ADJUSTED` | `NetCashProvidedByUsedInOperatingActivities` from `companyfacts`, each period's value as last filed on or before 2014-12-24 |
| Window | Weekly returns whose end date is in **(2009-12-24, 2014-12-24]**, about 261 | Fiscal quarters ending in (2009-12-24, 2014-12-24] with the same quarter a year earlier present, about 19 |
| Left side | MV_T · ln(adjusted close_t / adjusted close_{t−1}) | OCF_q − OCF_{q−4}. A quarter is its own ~91-day fact, else the difference of two year-to-date facts with the same start |
| Right side | E_t, each factor taken at the equity observation date, or the latest earlier session with a value | Σ (N_leg / 4) · s_leg · [f̄_q − f̄_{q−4}], f̄ the factor's average over the quarter's sessions |
| Minimum | **100** weekly returns | **12** year-on-year quarters |
| k's interval | Stationary bootstrap, expected block **4 weeks**, 10,000 resamples | Stationary bootstrap, expected block **4 quarters** (the year-on-year differences overlap), 10,000 resamples |

A firm listed for part of the window is measured on the part, if it clears the minimum.

> **DD186 — the window is five years, chosen on power computed from committed DEV rates and
> currencies before any equity row exists.** §6 is the table. Over two years k's standard error for
> a euro exposure one-fifth of market value is 1.02; over five it is 0.47, because both the sample
> and the currency's variance grow. The window stops at 2014-12-24 like every input (§6.1), starts
> after the 2008–2009 crisis, and is the one the 2014 filings describe best. Rates are unresolvable
> at either length, and that is §6's first finding.

> **DD187 — how a price is tied to a filer, and what arrives and what is kept.**
>
> 1. **Symbol.** `dei:TradingSymbol` in the cohort 10-K, else the SEC's current ticker map for the
>    CIK, first entry. It must appear in Alpha Vantage's `LISTING_STATUS` as of 2014-12-24, or the
>    firm has no price, counted.
> 2. **Identity.** A symbol can name another company by 2026. So the price is checked against the
>    filer's own words: `dei:EntityPublicFloat` against the adjusted close at the last weekly
>    observation on or before the float date, restated to the cover date's share basis (× raw ÷
>    adjusted close at the last observation on or before the cover date), × the cover's
>    `dei:EntityCommonStockSharesOutstanding`, summed over classes. **Pass iff the ratio is
>    in [0.35, 1.30]**: affiliates hold up to two-thirds of some firms, and eight months of price move
>    separate the two dates. A fail is no price, counted. It is never retried under another symbol.
> 3. **Market value.** MV_T = shares from the latest 10-K or 10-Q accepted on or before 2014-12-24
>    (`num.txt`, else the 10-K instance summed over classes) × the adjusted close at the last weekly
>    observation on or before 2014-12-24, restated to that filing's share basis the same way. So a
>    split between the filing and the construction date cannot move MV_T.
> 4. **Drop on arrival.** Each Alpha Vantage and EIA response is parsed in memory and **every row
>    dated after 2014-12-24 is discarded before anything is written or computed**. The raw response
>    is never cached. The cache holds the kept rows only, and a bar asserts that no cached row is
>    later than 2014-12-24. The week ending 2014-12-26 is therefore dropped too, which is §6.1's rule
>    anyway: an observation dated after the construction date.
> 5. **What leaves curvecast.** Statistics only (k, its interval, n, R², the identity ratio and a
>    drop reason), per firm and per class, never a price and never MV_T, since MV_T divided by the
>    committed share count would restate one.
>
> Alpha Vantage's adjusted close is on today's share basis, so its **levels** carry every later
> split and dividend. Only ratios within 2009–2014 and the restatements in (2) and (3) are used, and
> a later action multiplies both terms of each ratio by the same factor. No level is used alone.

## 5. The scorers

> **DD188 — the verdicts, the evaluable set, and what is reported first.**

**H11** (scored on the equity denominator; the cash-flow denominator scored by the same rule and
reported beside). A firm is **evaluable** iff it has at least one leg (§3) and an equity k (§4). It
**counts** iff **k_firm < 1/1.3**, where k_firm uses every leg the firm has. A k at or below zero
counts: the measured hedge is nothing, or the wrong way, so any naive hedge is too large. **PASS iff
at least 70% of the evaluable firms count.** Reported first, in this order: the cohort median of
k_firm with a bootstrap percentile interval over firms (10,000); the count, with its
Clopper–Pearson 95% interval; then the verdict. Beside them:

- **the missing-data bounds**: the share counting if every cohort firm without a k counted, and if
  none did, both over forty;
- **the resolved count**: firms whose own k interval lies wholly below 1/1.3, or wholly above it.

The evaluable set is not the cohort. Firms are missing because they have no traded share, fail the
identity check, have fewer than 100 returns, or were delisted or renamed so that a 2026 route no
longer serves their 2014 prices. **The second reason is
decided by what happened after the construction date**, so the evaluable set leans towards firms
that survived. That is why the bounds are reported, and why Paper 2 says it in these words.

**H17** (same denominators, same order). Per firm and class, **ratio = 1/k_class**, or +∞ if
k_class ≤ 0, with k_class from that class's legs alone. **The first half** is the median over every
(firm, class) pair with class currency or crude, and it holds iff the median is **above 2.0**. **The
second half** is the median over firms with a rates leg, and it holds iff the median is **below
1.5**. **PASS iff both hold.** Each median carries a bootstrap percentile interval over firms
(10,000, resampling firms with all their pairs). The currency and crude medians are reported
separately beside the pooled one. The register writes *"FX and commodity"* as one median, and one is
scored. **A half with fewer than five evaluable units is refused, and H17 is then `NOT_PERFORMED`.**

Seeds, block lengths and resample counts are fixed here: seed **20260926**, 10,000 resamples
everywhere, blocks as §4 says.

## 6. Power, computed before any run

*Computed 2026-09-26 from `panel_daily_dev_20260914.csv` and `panel_daily_fx_dev_20260926.csv`, both
committed DEV panels, weekly by last session. No equity row, no filing and no out-of-sample row was
read.* k̂ is taken as normal with standard error SE(k) = σ_e / (σ_x · √n) ÷ (N/MV), where σ_x is the
factor's weekly standard deviation and σ_e the firm's weekly residual volatility. σ_e is assumed,
2% and 3% weekly, because no equity return has been read. Crude's σ_x is assumed at 4.2% weekly
(30% a year), because EIA's series is not committed. P(count) is P(k̂ < 1/1.3).

| Window | σ_x, one-year yield | σ_x, euro | σ_x, renminbi |
|---|---|---|---|
| 2 years, n = 104 | **1.93 bp** | 0.962% | 0.241% |
| 5 years, n = 261 | **2.62 bp** | 1.305% | 0.227% |

Five years, σ_e = 2% weekly (3% in brackets):

| Class | N/MV | SE(k) | P(count), true k = 1/3 | P(count), true k = 1 |
|---|---|---|---|---|
| Rates | 0.05 | 94.6 (141.9) | 0.50 (0.50) | 0.50 (0.50) |
| Rates | 1.00 | 4.73 (7.10) | 0.54 (0.52) | 0.48 (0.49) |
| Euro | 0.05 | 1.90 (2.85) | 0.59 (0.56) | 0.45 (0.47) |
| Euro | 0.20 | **0.47** (0.71) | **0.82** (0.73) | **0.31** (0.37) |
| Euro | 1.00 | 0.09 (0.14) | 1.00 (1.00) | 0.01 (0.05) |
| Renminbi | 0.20 | 2.72 (4.08) | 0.56 (0.54) | 0.47 (0.48) |
| Crude | 0.05 | 0.59 (0.88) | 0.77 (0.69) | 0.35 (0.40) |
| Crude | 0.20 | 0.15 (0.22) | 1.00 (0.98) | 0.06 (0.15) |

The same euro row over two years: SE 1.02, P(count) 0.67 against 0.41. That is DD186.

**What the table says, before any number is read:**

1. **A rates exposure cannot be measured at this construction date, at any window this route
   reaches.** The one-year yield moved about two basis points a week, because it sat at the floor
   from December 2008. Every rates k is a coin flip about any threshold, so **H17's second half will
   be decided by noise**, with a probability near one half whatever the truth, and a firm whose
   only leg is rates counts towards H11 about half the time whatever the truth. This is a fact about
   2009–2014, and Paper 2 reports it as one.
2. **A currency exposure is resolved only when it is large against the firm**: about one-fifth of
   market value in a floating major. The renminbi, managed in this window, is never resolved.
3. **Crude is resolved even when small.** WTI moves most, and DD176's exposures are large.
4. **So H11's bar may fail even if its prediction is true.** Expected prevalence is a mixture of
   ~0.5 for rates-only firms and 0.6–1.0 for the rest, weighted by the cohort's mix, which is not
   known until extraction. The median k and its interval are the finding. The 70% bar is the
   pre-registered decision rule and it does not move (A1 §5.5).

The cash-flow denominator is not tabulated. Its residual variance is unknown until extraction, and
it has about nineteen year-on-year quarters against 261 weeks. A1 §5.4's warning about quarterly
false positives is reported beside it.

## 7. Item 7A's own figures, reported beside with no verdict

A1 §2.1's third quantity. Inside filter (i)'s span, the first sentence per class that carries a
shock and a dollar amount is recorded verbatim, with its shock, its amount and a measure label: a
sentence naming `interest expense`, `interest cost`, `earnings`, `income`, `revenue` or `cash
flow` is an **earnings** measure, one naming `fair value` is a **fair value** measure, and one naming
`value at risk` is **VaR**. A rates sentence is one naming `interest`, a currency sentence one naming
`currenc` or `exchange rate`, and a crude sentence one naming a word in DD176's crude pattern. Only an
earnings measure converts, to an implied exposure of amount ÷ shock, and it is reported beside §3's
figure as a ratio. The rest are counted by label. **No claim reads any of this.**

## 8. Who does what, and what deskcraft receives

curvecast runs one script, never imported by any package there, under D423's identity and cap. Its
SEC stage runs first and needs nothing but the network; its measured stage refuses to start without
an Alpha Vantage key in the environment, which is never printed or written. deskcraft receives,
under `tests/fixtures/`, all LF, all dated by the day they were drawn:

| Fixture | Rows | Licence |
|---|---|---|
| `d17_cohort_dev_<date>.csv` | every firm walked: rank, CIK, name, SIC, accession, acceptance, `Assets`, each filter's outcome and drop reason, cohort rank 1–40 | Public domain (SEC) |
| `d17_stated_dev_<date>.csv` | per cohort firm per leg: class, instrument, sign, N, source concept and member, the rule step that produced it | Public domain |
| `d17_cash_flow_dev_<date>.csv` | per cohort firm per fiscal quarter: start, end, OCF, filing date, derivation | Public domain |
| `d17_item7a_dev_<date>.csv` | per cohort firm per class: the sentence, shock, amount, label | Public domain |
| `d17_measured_dev_<date>.csv` | per cohort firm, denominator and class: k, interval, n, R², identity ratio, drop reason | Statistics from `RESULTS_ONLY` routes (DD187 item 5) |

`src/deskcraft/exposure.py` loads them, scores H11 and H17 by §5, and runs no network and no
regression it cannot see the inputs of. When the package lands, its bars will cover at least these
behaviours, numbered then:

- the cohort fixture reproduces §2's walk: forty survivors, in `Assets` order, every walked firm
  accounted for by exactly one outcome;
- every leg in the stated fixture names a rule step in §3, and none is dated after 2014-12-24;
- the measured fixture carries no column that restates a price or a market value;
- the scorers reproduce §5 on synthetic cases where the answer is known, including k ≤ 0 counting,
  +∞ ratios, the five-unit refusal and both bounds;
- curvecast's cache holds no row dated after 2014-12-24 (a curvecast bar, cited here).

## 9. Carried items, and the claims this document touches

**X2** — discharged: D17's asset classes are rates, currency and crude. Credit is declined, as §6.1
declines it for D22, because `CREDIT_VS_RATES` reaches no tradeable series (DD124) and no cohort
filter reads credit. The research memo's *"two to four"* asset classes are therefore three, and
Paper 2 says so.

**X21** — discharged: the commodity arm's windows are stated separately from DD98's, as the item's
second option asks. D17's crude regression reads 2009-12-24 to 2014-12-24 and D22's WTI arm reads
`NBER_2020` and `RATES_2022` (DD176); all of them sit inside a series that ends 2024-04-05. No result
is scored on the twenty months it does not reach, and H15, whose sample would need them, never
carries crude.

> **DD189 — D17 adds no claim and moves none.** H11 and H17 keep their wording, their predicted
> PASS and their scorer. This document fixes what they are computed on, publishes their power
> before any number exists, and says in §6 that H17's rates half cannot be resolved at this
> construction date. Whether to keep that half as registered or withdraw it before anything is read
> is **the owner's decision, and it is not taken here**. Unanswered, it is scored as written.

## 10. Predictions, scored when the package lands

| # | Prediction |
|---|---|
| P1 | The walk reaches forty survivors within the first 70 firms by `Assets` |
| P2 | Filter (i) drops at most five walked firms |
| P3 | At least 30 of the 40 carry a rates leg |
| P4 | Fewer than 20 of the 40 carry a currency leg (DD174's probe found about half at the filter, and not every read is revenue) |
| P5 | At least five of the 40 have no usable weekly price (no share, no symbol, a failed identity or fewer than 100 returns) |

## 11. What this could still get wrong

1. **The Item 7A span rule can misfire** on a filing whose headings are images or whose Item 8
   heading reads differently. It is a coarse gate on large filers, and its drops are counted.
2. **The rates rule reads F_net from four elements** and misses any floating debt tagged under an
   extension concept. H17's rates half would be the place that shows, if it had power.
3. **Revenue by country is not currency exposure.** A firm invoicing Japan in dollars has a
   Japanese revenue fact and no yen exposure. That is the gross-versus-net gap the layer exists to
   measure, so it is left in, and it biases the stated figure upward, towards H11's prediction.
4. **The evaluable set is survivor-weighted** (§5). The bounds report how much that can matter;
   they cannot remove it.
5. **A symbol that moved** can still pass the identity check if the new holder's float happens to
   land inside [0.35, 1.30] of the old filer's. It is unlikely and not impossible.

---

## 12. Sharpened before the first request

> **DD190 — three rules sharpened while the extractor was written, before any filing was fetched.**
> Each would have dropped or kept a firm for how it typesets a filing or for when a route answers,
> not for what the firm disclosed. None changes a claim, a threshold, a window or a denominator.
>
> 1. **Filter (i) reads the whole 10-K for a market-risk disclosure, not only Item 7A's span.**
>    Large filers often write Item 7A as one line pointing into MD&A (*"see 'Market Risk' in
>    Item 7"*), without the words *incorporated by reference*, so §2's rule would read a one-line
>    span and drop them. Filter (i) now **passes iff, in the primary document or its EX-13, some
>    occurrence of `market risk` is followed within 5,000 characters by a qualifying sentence**,
>    §2's test unchanged. §7's sentences are read from the Item 7A span when it runs to 1,000
>    characters, and otherwise from those windows in document order.
> 2. **The fiscal year end is the date of the 10-K's latest undimensioned `Assets` fact**, not
>    `dei:DocumentPeriodEndDate`, which some filers write as a nominal date no context carries.
> 3. **Drop on arrival reaches two SEC-side responses as well.** `companyfacts` returns every
>    filing to 2026, so each response is parsed in memory and every fact filed after 2014-12-24 is
>    discarded before anything is kept. Alpha Vantage's `LISTING_STATUS` snapshot for 2014-12-24
>    carries a `delistingDate` column that can name a later date, so that column is discarded on
>    arrival. Like the EIA case, this applies the owner's answer (DD181 item 4) to routes it did not
>    name, and it is said here so that it can be refused.

> **DD191 — the first dry run found three defects in the extractor, not in the rules, and each fix
> applies the rules' own words.** Run 2026-09-26 with `--dry` (curvecast `make_deskcraft_d17_exposure.py`):
> no fixture was written and no exposure, price or cash flow was read, but which firms passed each
> filter was printed and seen. So each fix says what it moved, and the first run's counts stay here.
>
> 1. **The ordering read segment rows as the firm's `Assets`.** The 2014 data sets carry a
>    `segments` column, and a filing's `Assets` appears once per business segment as well as once
>    consolidated. The code kept whichever row came last, so Microsoft ranked first and GE, Exxon,
>    Apple and Walmart were nowhere near the top. §2 step 2 names *"the row"*; it is the
>    consolidated one, with `segments` empty. The latest share count takes the same rule.
> 2. **A dollar amount in a table was not read as one.** §2's words are *"`$` and a digit"*. The
>    code wanted them adjacent, and a table cell reads `$ (1,242)`, so Microsoft's, Pfizer's and
>    Procter & Gamble's market-risk tables failed filter (i) on typesetting alone.
> 3. **A country named by its ISO code was not read as that country.** The 2014 filings name
>    geographical members from the XBRL country taxonomy (`country:JP`, `country:GB`), and curvecast
>    `373f85a`'s table matched spelled-out names only. DD174's words are *"a member naming a
>    single-currency country"*, and `JP` names Japan. So the same countries match by ISO code as
>    well: the table's eleven euro-area states, Japan, the United Kingdom, Canada, Switzerland,
>    mainland China (`CN`, never `HK`) and Mexico. **The currency probe's 7 of 17 (curvecast
>    `cd77bf0`) is therefore an undercount**, and DD174's *"the currency arm will be thin"* rests on
>    it. Nothing in §6.1 moves; the arm will be less thin than it said.
>
> One miss the run showed is **not** a defect: Google's commercial paper is tagged `DebtCurrent`,
> which §3's rates rule does not read, so Google has no rates read. That is the rule as written
> (§11 item 2), and it stays.
>
> The first run walked **65** firms to reach forty: filter (i) dropped **9** and filter (ii) **16**,
> over **5,022** ordered 10-K filers (1,639 dropped as financial, 100 with no `Assets` row, 65
> earlier 10-Ks from the same filer). The corrected run's counts are §2's result, reported when the
> package lands.

> **DD192 — filter (i) is re-cut to Item 305's forms, and then frozen.** The second dry run, with
> DD191's fixes, still dropped Microsoft, GE, Pfizer, Procter & Gamble, Caterpillar and Disney,
> firms whose market-risk disclosures are plainly quantitative. Two causes, both in the proxy and not
> in the disclosures: a sensitivity or VaR **table** has no sentences, so §2's *"a sentence with
> both"* never matched it, and a pointer from Item 7A often names a section headed *"risk
> management"*, never saying *"market risk"*. Item 305 allows three forms, tabular, sensitivity and
> VaR, and two of them are tables. So:
>
> 1. **An Item 7A span of 1,000 characters or more is the disclosure** and is read alone. A shorter
>    span, or none, points elsewhere, and the 5,000 characters after each `market risk` or `risk
>    management` in the 10-K and its EX-13 are read instead, each cut at the next `item 8`.
> 2. **A region passes iff it holds a dollar amount within 300 characters of a shock or of VaR.** A
>    shock is a percentage, basis points, or a price move per physical unit (*"a $1.00 per gallon
>    increase"*). VaR is *value at risk* or the abbreviation, in any case.
>
> §7's sentences are read from the regions that passed. **The rule is frozen here.** It still misses
> a shock written in words (Ford's *"one percentage point"*), and the firms it drops are named in the
> cohort fixture with their reasons. A fifth cut, aimed at the names, would be the move this repository
> exists to refuse. Every cut was blind to exposure, price and cash flow, none of which had been read,
> so none could have been aimed at H11 or H17. It was not blind to which firms passed, and that is
> why all four runs are recorded:
>
> | Run | Rule | Walked to reach forty | Dropped by (i) | Dropped by (ii) |
> |---|---|---|---|---|
> | 1 | as committed + DD190 | 65 | 9 | 16 |
> | 2 | + DD191 | 56 | 13 | 3 |
> | 3 | + DD192, VaR case-sensitive | 56 | 13 | 3 |
> | 4 | **+ DD192, frozen** | **53** | **10** | **3** |
>
> Run 4's (i) drops: Ford, Pfizer, Procter & Gamble, Duke, Caterpillar, Burlington Northern Santa Fe
> LLC, BNSF Railway, CVS, MidAmerican Energy Holdings and Anadarko. Its (ii) drops: Dow, Amgen and
> Express Scripts. Runs 1 and 2 differ from 3 and 4 mostly through DD191's ordering fix, which changed
> which forty firms the walk met first.

---

## 13. The cash-flow denominator, computed 2026-09-26 (beside, not a verdict)

*Everything above was fixed before this was computed.* curvecast `measure_deskcraft_d17_exposure.py
--cash-only` ran §4's cash-flow denominator on the SEC fixtures, the committed DEV rates and
currencies, and EIA's contract-2 WTI returns (kept to 2014-12-24; every 2014 roll date matches CME's
calendar). `d17_measured_dev_20260926.csv` holds the statistics. **Thirty-two of forty firms are
evaluable**: four have no leg and four have fewer than twelve year-on-year quarters.

| | Result on operating cash flow |
|---|---|
| H11 | **20 of 32 count, 0.625, Clopper–Pearson [0.437, 0.789]**, below the 70% rule. Median k **0.036**, firm-bootstrap [−0.707, 1.505]. Bounds over forty [0.50, 0.70]. Resolved: 11 below 1/1.3, 1 above |
| H17 first half | Median ratio **2.99** over 24 currency and crude units, [0.56, +∞]. Holds |
| H17 second half | Median ratio **0.017** over 24 rates firms, [0.005, +∞]. Holds, on exactly the noise §6 predicted: the one-year yield barely moved, so k is huge and its sign is chance |
| By class | Currency 0.43 over 13 (does not hold alone), crude +∞ over 11 |

These are the beside numbers §5 promises. The verdicts are the equity denominator's, which waits on
the owner's free Alpha Vantage key. Paper 2 reports the two side by side, and says that on cash flow
H17's rates half is decided by noise.

*Next free ids: **C179 / DD193 / X26**.*

---

## 14. The equity denominator, computed 2026-09-27: the verdicts

*Everything above was fixed before any equity price was read. curvecast
`measure_deskcraft_d17_exposure.py --stamp 20260926 --out-stamp 20260926` fetched Alpha Vantage's
weekly series over two days: 25 requests on 2026-09-26, one attempt that evening refused on the
rate and keeping nothing, and 11 requests on 2026-09-27. The fixture keeps its name. Its 92 cash
rows are byte-identical to the ones §13 reported, because every seed and block is fixed, and 92
equity rows were added beside them. Rerun the same day from the kept rows, the script made no
request and wrote the fixture again byte for byte (SHA-256 `aa7284b9…`).*

**Thirty-two of forty firms are evaluable on equity.** Four have no leg. Comcast, Google and Exelon
fail the identity check, and Time Warner has no symbol active on 2014-12-24. Google's `GOOG` now
serves the class C shares, whose history begins 2014-04-04, and §4 forbids a retry under another
symbol: that is §5's renamed firm, and it is why the bounds are reported.

| | Equity (the verdict) | Operating cash flow (§13, beside) |
|---|---|---|
| H11 | **PASS. 24 of 32 count, 0.750, Clopper–Pearson [0.566, 0.885].** Median k **−9.17**, firm-bootstrap [−173.0, −0.379]. Bounds over forty [0.60, 0.80]. Resolved: 10 below 1/1.3, 6 above | FAIL, 20 of 32, 0.625 |
| H17 first half | Median ratio **1.55** over 22 currency and crude units (18 firms), [0.154, +∞]. Does not hold | 2.99, holds |
| H17 second half | Median ratio **+∞** over 25 rates firms, [+∞, +∞]. Does not hold | 0.017, holds on noise |
| **H17** | **FAIL** | PASS |
| By class | Currency **0.130** over 12, [0.046, +∞]. Crude **+∞** over 10, [1.93, +∞], which holds alone | Currency 0.43, crude +∞ |

**H11 passes as predicted, and H17 fails against a predicted PASS.** The two denominators disagree
on both claims, and Paper 2 reports them side by side, as §4 fixed.

### 14.1 What the equity k measured

> **DD207 — the market's own exposure decides every class. Read after the run; no rule moves.**
> DD185 put no market return on the right on purpose: a firm hedges its value, and the market's
> exposure is part of that value. Between 2009 and 2014 that part dominates.
>
> 1. **Rates.** 22 of 25 rates k are negative; 6 are resolved below zero and none above. In 23 of
>    the 25 firms, share prices rose when the one-year yield rose: the 22 negative k, and NextEra,
>    whose leg is net fixed after swaps, so its positive k says the same. §6 was right that a single
>    rates k cannot be resolved (19 of 25 intervals straddle zero), and wrong about what follows
>    from it: the unresolved k share one sign, the market's, so the rates half is decided by the
>    sign of the stock–yield correlation and not by a coin flip. Its bootstrap interval is
>    [+∞, +∞].
> 2. **Currency.** 9 of 12 currency k are above one, and 7 are resolved above one. The median
>    measured exposure is about 7.7 times the stated revenue (ratio 0.130), the opposite of H17's
>    prediction. Share prices rose when the dollar fell, and that co-movement, not foreign revenue,
>    is what k measures here.
> 3. **Crude.** 6 of 10 crude k are negative, and all six are resolved. Four are producers that
>    DD176's rule reads as **short** crude, because their largest crude-named fact is a purchase or a
>    cost: ExxonMobil (`CrudeOilAndProductPurchases`), Occidental
>    (`EnvironmentalCostsOperatingExpense`, $137m, hence its k of −321), and Freeport-McMoRan and
>    Apache (a future production cost). The market prices all four long. The crude median holds
>    alone on those four reads, a misread neither §3 nor §11 named. Of the two producers read long,
>    Chevron measures **0.39**, the exposure-puzzle shape this layer was built to find, and
>    ConocoPhillips 1.91.
> 4. **H11.** Its 24 counts are 22 firms with k ≤ 0 and 2 with a positive k below 1/1.3. §5 counts
>    k ≤ 0 on purpose, but the over-hedge H11 describes, a real exposure smaller than the stated one,
>    is the second kind, and there are two. Thirteen of the 24 are firms whose only leg is rates, and
>    13 of those 14 count (item 1). On the 18 firms with a currency or crude leg, 11 count, **0.611,
>    Clopper–Pearson [0.357, 0.827]**. That is reported beside the verdict and never substituted for it.

### 14.2 A defect found after the read

> **DD208 — the extractor read co-registrants' cover facts as the filer's; no correction can move a
> verdict, so the fixture stays as run.** curvecast's `_read_dei` sums
> `EntityCommonStockSharesOutstanding` over every context on its latest date and keeps the last
> `EntityPublicFloat` it meets. A combined 10-K tags each co-registrant's cover facts in the same
> instance, so a subsidiary's shares are added to the parent's and a subsidiary's float can replace
> the parent's. The FSDS path excludes co-registrants (`coreg`); the instance path does not. It was
> found by reading the three identity failures after the verdicts were computed, and then checked
> against all forty cohort instances. No cohort firm carries a later share count, so MV_T used the
> instance count everywhere.
>
> | Firm | What the defect did | Effect |
> |---|---|---|
> | Comcast | Float taken from NBCUniversal Media's $0, not its two classes' $107.7bn | Identity ratio 0.0: **dropped by the defect** |
> | Exelon | Shares 1.155bn, adding ComEd's, PECO's and BGE's to its own 0.857bn | Dropped either way: on its own count the ratio is 2.54, because its tagged float ($59.1bn at 2013-12-31) is not a public float |
> | PG&E | Shares 722m, adding the utility's 264m | Kept; MV_T and k 1.578× too large |
> | American Electric Power | Adds five subsidiaries' shares | Kept; 1.122× |
> | Southern | Adds five subsidiaries' shares | Kept; 1.052× |
> | NextEra | Adds Florida Power & Light's 1,000 shares | None |
> | 21st Century Fox | Float of class B only | None: no leg and no symbol |
>
> **Why no verdict can move.** Scaling MV_T scales k and leaves its sign and its R² alone, and the
> three kept firms' k are all negative, so every count and every ratio stays where it is. The one
> firm the defect dropped is Comcast, whose only leg is rates. On H11, 24 of 33 is 0.727 and 25 of
> 33 is 0.758, both PASS. On H17 it adds one rates unit to a half whose median is +∞ with 22 of 25
> below zero, so that half still fails and H17 still fails. **P5 is the exception** (§14.3).
>
> Correcting the extractor now would decide one firm's inclusion after every other k had been seen.
> It cannot move a verdict, so the fixture stays as run, and whether to re-run with the correction
> and report both is **the owner's call**. Two consequences are recorded for later packages. D21's
> replay (DD202) must compute MV_T with the same function: Ederington effectiveness is scale-free
> only when the fit and the replay share MV_T. And D22's H16 reads the stated legs and operating
> cash flow, never MV_T, so the defect does not reach it; H15, which would read MV_T, is refused
> (DD180).

*Answered 2026-09-28 by DD233 (the joint registration's §12): the fixture stays as run, nothing is
re-run beside it, and `_read_dei` is not corrected before D21's replay.*

### 14.3 The predictions

| # | Prediction | Scored |
|---|---|---|
| P1 | Forty survivors within the first 70 by `Assets` | **Holds**: 53 walked (§12, run 4) |
| P2 | Filter (i) drops at most five | **Wrong**: 10 |
| P3 | At least 30 of the 40 carry a rates leg | **Wrong**: 27 |
| P4 | Fewer than 20 carry a currency leg | **Holds**: 14 |
| P5 | At least five have no usable weekly price | **Holds at exactly five, and only through DD208.** Comcast, Google and Exelon fail the identity check; Time Warner and 21st Century Fox have no symbol. Comcast is the defect's, so on a corrected extractor P5 is four, and wrong, unless Comcast's own float then fails the band. GM, HP and Deere have no leg and were never priced |

### 14.4 What this hands D21

D21's in-sample number is this fixture's equity R² (DD200). Every evaluable firm's is below 0.40:
the largest is 0.399, the median 0.016, and 23 of 32 are under 0.05. So every in-sample R² is
already below H14a's 0.5, which is the case D21's §6 said decides H14a before 2015 is read. D21
stays registered, and its out-of-sample half waits on the owner.

*Next free ids: **C195 / DD209 / X26**.*
