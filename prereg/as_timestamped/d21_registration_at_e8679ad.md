# D21 — the end-to-end hedge backtest, fixed before either half is read

**Status: REGISTERED, not landed.**

*Written 2026-09-26, at `6b3117b`, after D17's first day of extraction and before its second. Day one
wrote no fixture, so no equity return, no k and no in-sample R² exists anywhere yet. Written before
the first out-of-sample read: `docs/OWNER_AUTHORISATION_the_first_oos_read.md` does not exist at the
commit that adds this document. Everything below is a rule with one answer. The package lands when
both halves have run and its bars score them; this status line changes then and nothing above it
does.*

---

## 0. What D21 does, in one paragraph

D17 reads what each of forty companies says it is exposed to, and measures from its share price how
much of that exposure the market priced: k, the multiple of the stated exposure a variance-minimising
hedge holds. D18 prices the hedges a bank would offer on it and refuses any that obliges more than
the company has. **D21 runs the whole loop as a test.** It builds each company's hedge on
2014-12-24 from nothing later, holds it, and asks how much of the company's weekly value variance it
removed, first over the five years it was fitted on and then over the nine it never saw. **H14a**
predicts the out-of-sample hedge removes less than half the variance for most of the cohort, and
**H14b** that it removes less than half of what it removed in sample. **H12a** predicts that the
plain forward removes at least nine-tenths of what the best option structure removes. §6 says
before any number exists what each of the three can and cannot show.

## 1. What it rests on

| | |
|---|---|
| D22's lock | `PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md` §6.1 (DD171–DD180): constructed **2014-12-24**, **held**, the forty by rule. D21 restates it and does not choose against it |
| The exposure and k | `PRECOMMIT_deskcraft_d17_exposure_extractor.md` §3–§5: the stated legs, the weekly window, k (DD185), its interval, MV_T and drop-on-arrival (DD187) |
| The menu and the gate | `PRECOMMIT_deskcraft_d18_structures_and_gate.md` DD193–DD196: four admitted structures, leverage on the stated flow, the restated pricers |
| The bars' shape | `AMENDMENT_A1` §5.2 (H14's split, H14b ⊆ H14a), §5.3 (interval methods), §5.5 (the bar and the claim) |
| The route | DD180 item 3: the owner chose Alpha Vantage's free **weekly** adjusted prices for D17's and D21's fits |
| The gate on the surface | `RIDER_X13_X14_one_surface_two_clocks.md` DD133–DD135, amended for D21 by DD199 below |

## 2. The fifth reader

> **DD199 — D21 reads the out-of-sample record, so it registers before the first read, in its own
> document, and the owner's authorisation names five readers.** H14a and H14b are statements about
> 2015 onwards and cannot be scored on anything else. DD134 counted four readers — D12, D14, D15,
> D22 — because D21 had no pre-commit when the rider was written, and nothing in the tree has
> counted it since: C119 checks the authorisation for four names and C120 would refuse this
> document as a lone reader pre-commit the day D21 joined the list.
>
> DD134's reason for one document is **order** (X14): no reader's rules may be written after
> another reader's result exists. That holds here, because this document is committed before the
> authorisation. What cannot hold is *one* document. The joint registration names its packages in
> its filename, `closed()` reads them from there (DD161), and renaming it would move every bar that
> cites it. So DD134 is **amended, not repealed**:
>
> 1. D21 registers in this document, committed before the authorisation exists.
> 2. The authorisation names **five** readers and **both** registration documents by name. C119
>    checks both, so an authorisation written against four readers is refused.
> 3. C120's refusal of a lone reader pre-commit gains **one declared exception**, this document,
>    held as an equality the way C158 holds the registered documents, so a sixth is an edit and not
>    a quiet use.
> 4. D21 reads **after** Paper 1, as D22 does: its extraction is its own (§7), under the same
>    authorisation, and it reads nothing Paper 1's verdicts depend on.
>
> **This changes what the owner writes.** The joint registration's §10 step 1 said the
> authorisation names *"the four readers"*; it is annotated in place. The authorisation is still
> the owner's alone (DD133), and nothing here writes it.

## 3. The hedge, restated

| | Fixed |
|---|---|
| Construction | **2014-12-24**, every input dated on or before it (§6.1) |
| Cohort | D17's forty, by §6.1's rule. A firm with no leg (four of the forty) has no hedge and is counted, never scored |
| Held | The hedge ratio is **never re-estimated** (§6.1: *"D21's row leaves rolling against held to be stated; it is stated here: held"*). No rolling variant is computed, so none can be chosen |
| The hedge | D17's **k** on the firm's whole stated exposure (class `all`), times each leg's stated notional: **k·N_leg on every leg**, one scalar per firm. For a single leg this is Ederington's minimum-variance position in that leg's instrument (DD185) |
| Instruments | D22's lock's: `SVENY01` carried as cash, spot in the seven currencies, NYMEX WTI contract 2 on one contract's two settles, each with its `ReExpression` (DD175, DD176) |

> **DD200 — the in-sample effectiveness is D17's R², and D21 fits nothing.** Ederington's measure is
> 1 − Var(hedged) / Var(unhedged). With the hedge ratio fitted by least squares on the same sample,
> hedged = y − k̂·E and Var(y − k̂·E) = (1 − R²)·Var(y), so **the in-sample effectiveness is exactly
> the regression's R²**, which D17's measured fixture already carries per firm (`denominator`
> equity, `class` all). D21 reads it and runs no regression of its own. Out of sample, with y the
> firm's weekly value change at construction scale and E the stated exposure's weekly P&L,
>
> ```
> effectiveness_OOS  =  1 − Var(MV_T·r_t − k·E_t) / Var(MV_T·r_t)
> ```
>
> over the verdict weeks (§4), k and MV_T D17's, **held**. It is §6.1's H15 measure (*"x the
> hedge's return per dollar of market value at construction"*) on weekly returns: MV_T cancels from
> the ratio. **It can be negative**: a held ratio can add variance. The register's "OOS R²" in H14a
> and H14b means this number.

**Two objects, kept apart.** H14a and H14b score **the Ederington hedge at k**, whatever k is,
because the register's claim is about minimum-variance ratios. The loop's own hedge, the one D18's
gate admits, is **min(k, 1)** of the stated exposure: the gate refuses leverage above one on the
stated flow (DD194), and a k at or below zero is no hedge. H12a scores that one (§5). A firm whose
k exceeds one is therefore hedged at its k in H14 and at one in H12a, and both are reported.

**What D21 does not compute.** No crisis-window effectiveness: on weekly prices that would be the
weekly H15 DD180 refused by name. No cash-flow denominator: D17 measures it beside the equity one,
but its out-of-sample half would need quarterly operating cash flow for 2015–2025, and A1 §5.4
already found the decay clause's false-positive rate at quarterly frequency up to 16%. D21 reads
no cash flow after 2014.

## 4. The out-of-sample window

> **DD201 — the verdict weeks are the same for every firm and end at EIA's last WTI settle.**
>
> 1. **Weeks.** A weekly return is scored iff **both** of its observations lie in
>    **[2015-01-01, 2024-04-05]**. The start is `OOS_START`, so the window is an `OosWindow` and
>    reaches nothing in DEV. The hedge is held from 2014-12-24; the returns between the construction
>    date and the first 2015 observation are held and not scored.
> 2. **The end.** EIA's NYMEX series stops **2024-04-05** (DD127), and eleven of the thirty-six firms
>    with a leg carry crude. DD127's rule is that no firm is scored on a shorter sample than another,
>    so **every firm's verdict window ends there**, crude or not: about **482** weekly returns.
>    Beside, with no verdict: the firms without a crude leg over [2015-01-01, 2025-12-31].
> 3. **Minimum.** **100** out-of-sample weekly returns, D17's own minimum. Fewer, and the firm is
>    not evaluable, counted.
> 4. **No splice.** A weekly series whose consecutive observations sit more than **21 days** apart
>    is cut at the first such gap, and only the part before it is used. A symbol that goes quiet and
>    comes back may name a different company; D17's identity check (DD187 item 2) proved the series
>    through 2014 and proves nothing after it.
> 5. **Sources.** Equity: Alpha Vantage `TIME_SERIES_WEEKLY_ADJUSTED`, **fetched again**, because
>    D17's cache holds no row after 2014-12-24 and never will. Rates and currencies: the rows of the
>    one out-of-sample extraction (DD102; the joint registration's §10 step 2), never a second read.
>    Crude: EIA's contracts 1 and 2, as DD176 fixes, read at D21's own read. Each factor is taken at
>    the equity observation date, or the latest earlier session with a value, as D17 §4 takes it.

## 5. The scorers

> **DD203 — H14a and H14b, and what is reported before either verdict.**

A firm is **evaluable** iff it has an in-sample fit (D17's equity row for class `all` carries k and
R²) and at least 100 verdict weeks. Over the evaluable firms:

- **H14a counts** a firm iff **effectiveness_OOS < 0.5**. **H14b counts** a firm iff
  **effectiveness_OOS < ½ × R²_in**. A firm whose out-of-sample effectiveness is at or below zero
  counts toward both.
- **Each passes iff at least 70% of the evaluable firms count.** The two are scored separately and
  never combined; H14b ⊆ H14a by construction (A1 §5.1), which the scorer checks rather than
  assumes.

Reported first, in this order: the cohort median of effectiveness_OOS with a bootstrap percentile
interval over firms (10,000); the median R²_in; the cohort median of the ratio OOS ÷ in-sample, with
the same interval (A1 §5.3's decay row); each count with its Clopper–Pearson 95% interval; then the
verdicts. Each firm's effectiveness_OOS carries a **stationary-bootstrap** interval, expected block
**4 weeks**, 10,000 resamples, seed **20260926**, as D17's k does. Beside them, every one computed
and none a verdict:

1. **The missing-data bounds**: each share if every cohort firm without a score counted, and if
   none did, both over forty. The evaluable set leans towards survivors, as D17's does.
2. **Weak but not decaying**: firms in H14a and not in H14b, A1 §5.2's informative count.
3. **H14a's in-sample shadow**: evaluable firms whose **in-sample** R² is already below 0.5. If it
   clears 70% on its own, H14a's out-of-sample pass says the hedge was never clean, not that it
   degraded (§6, finding 1).
4. **The resolved subset**: firms whose R²_in exceeds the in-sample null's 95th percentile,
   R² = F / (F + n − 2) with F the 95th percentile of F(1, n − 2) — **0.0148** at n = 261 — and how
   many of them H14b counts. That is where H14b is decided by decay rather than by estimation noise
   (§6, finding 2).

> **DD204 — H12a: the loop's own hedge, D18's admitted menu, marked weekly on the verdict weeks.**
>
> 1. **Eligible.** A firm enters H12a iff its equity k's interval lies **wholly above zero** — a
>    hedge the in-sample data can see — and it has at least 100 verdict weeks. On the rest every
>    structure is a hedge on noise, and comparing them measures nothing.
> 2. **Size.** Every structure is sized at **min(k, 1)** of each leg's stated exposure: the loop's
>    hedge, the largest the gate admits (§3).
> 3. **The menu.** D18's four admitted structures: the **forward**, the **bought option** at the
>    money, the **zero-cost collar** (protective strike half a standard deviation adverse, σ√τ in the
>    model's own space, the opposite option sold at the strike that makes net premium zero), and the
>    **participating forward** (one protective bought, ½ opposite sold, one strike solved for zero
>    premium). The **2:1 ratio forward is not an alternative**: the gate refuses it, and a structure
>    no client may hold is not one it could have chosen. Every struck structure is passed through
>    `HedgeStructure`, so the loop's gate is the gate D18 built.
> 4. **Tenor and roll.** Six months, as §6.1's option legs: struck at the first verdict observation
>    and at every **26th** after it, each settling at intrinsic on the 26th observation after its
>    strike, with **182** days less those elapsed as its tenor in between.
> 5. **Marks.** Weekly, at model value: Bachelier on `SVENY01` in percent, Garman–Kohlhagen at zero
>    differential on currency moneyness, Black-76 on crude moneyness (the path is the cumulative
>    roll-aware log return, so the held contract's rolls are inside it), all by D18's restated
>    pricers (DD196). A rates option pays on a year of the stated flow, whatever its tenor, because
>    that is the exposure's unit (DD184). A structure struck at fair value moves no P&L when it is
>    bought; its weekly P&L is the change in what it is worth.
> 6. **The forward** is D17's linear leg, −min(k, 1)·N·sign·Δf, so for k ≤ 1 it is exactly H14's
>    hedge.
> 7. **Volatility: EWMA, λ 0.94, D8's normalised weights**, over every daily change of the leg's own
>    factor from 2009-12-24 through the pricing date, annualised on 252 sessions, **times 1.0**.
>    §6.1's ordered list binds D22's option legs, and its first source needs a mapping from the
>    Minneapolis Fed's published underlyings to these factors that no document has written; a
>    verdict resting on an unwritten mapping would be a choice made at the read. No direction is
>    claimed for H12a: volatility sets the collar and participating strikes and every option's delta,
>    and the variance comparison has no sign in it.
> 8. **The comparison.** Per structure, VR_s = effectiveness of the firm hedged by s. The **best
>    alternative** is the one of the three with the largest VR. A firm **counts** iff
>    **VR_forward ≥ 0.9 × VR_best** where VR_best > 0, and iff **VR_forward ≥ VR_best** where no
>    alternative reduces variance at all: with nothing to capture, the claim is that the complex one
>    does no better.
> 9. **The verdict.** The register's row carries **no prevalence clause**, and A1 §5.2's audit counts
>    a prevalence as a clause. So H12a is read as a claim about **the typical firm** and written as
>    the median's own threshold: **PASS iff at least half the eligible firms count.** Seventy per
>    cent would be a bar H12a was never given. **Fewer than five eligible firms, and H12a is
>    `NOT_PERFORMED`**, never FAIL, as D17's H17 refuses a thin half.
>
> Reported first: the median capture ratio VR_forward ÷ VR_best over the eligible firms where
> VR_best > 0, with a bootstrap percentile interval over firms; the count with its Clopper–Pearson
> interval; the firms with nothing to capture; which alternative won, by name; the median VR of each
> structure; then the verdict. Beside, with no verdict: the same comparison with every structure
> sized at **100% of the stated exposure**, D18's menu as the 10-K reader would buy it.

> **DD205 — DD176's cost row is owed by the first package that prices a WTI leg's cost, and D21
> prices none.** The lock says *"D7a's costs gain a row before D21 builds"*: a half-spread of one
> full tick, $0.01 a barrel. D21's three measures are variances, so it computes no cost on any leg,
> and a register row nothing reads would still need a place in `sources.SOURCES` (C87 holds
> `COST_OF` and `UNPRICED_SERIES` as its partition). The number was fixed in the lock and does not
> move; only its timing is corrected, to **before D22 builds**, annotated in place as DD198
> corrected a reason. The read has not happened, so DD171's label is not owed.

## 6. What the three verdicts can say, computed before any run

*Computed 2026-09-26 by `deskcraft.effectiveness.null_decay` and `simulate_capture` on synthetic
draws, 200,000 and 400 replications, seed 20260926. No equity row, no k and no out-of-sample row
was read. C187 recomputes every cell of Tables A and A2; Table C's note says how to reproduce it.*

**Table A. H14 under no true decay.** A firm whose value moves k·E + e in both halves, k set so the
in-sample R² is the row's, 261 in-sample and 482 out-of-sample weeks, σ_e the same in both. v is
the factor's out-of-sample variance over its in-sample variance, which **cannot be read before the
authorisation** and is therefore a column. Each cell is the probability the firm counts.

| True R² | P(R²_in < ½) | H14a, v = ½ | v = 1 | v = 2 | v = 4 | H14b, v = ½ | v = 1 | v = 2 | v = 4 | v = 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | **0.744** | **0.754** | **0.780** | **0.816** | **0.856** |
| 0.002 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.676 | 0.631 | 0.591 | 0.552 | 0.520 |
| 0.005 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.609 | 0.513 | 0.426 | 0.356 | 0.311 |
| 0.01 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.549 | 0.403 | 0.282 | 0.200 | 0.154 |
| 0.02 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.509 | 0.303 | 0.156 | 0.078 | 0.046 |
| 0.05 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.490 | 0.187 | 0.044 | 0.009 | 0.002 |
| 0.10 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.465 | 0.092 | 0.006 | 0.000 | 0.000 |
| 0.20 | 1.000 | 1.000 | 1.000 | 1.000 | 0.587 | 0.382 | 0.017 | 0.000 | 0.000 | 0.000 |
| 0.30 | 1.000 | 1.000 | 1.000 | 0.904 | 0.000 | 0.263 | 0.002 | 0.000 | 0.000 | 0.000 |
| 0.50 | 0.490 | 1.000 | 0.524 | 0.000 | 0.000 | 0.031 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.70 | 0.000 | 0.121 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

**Table B. Where the cohort's firms sit.** The true R² of a firm whose value moves one-for-one with
its stated exposure (k = 1), from D17 §6's factor volatilities over the window and σ_e of 2% weekly
(3% in brackets). At H11's predicted k of about a third, divide by about nine.

| N / MV | Rates | Euro | Renminbi | Crude |
|---|---|---|---|---|
| 0.05 | 0.0000 (0.0000) | 0.0011 (0.0005) | 0.0000 (0.0000) | 0.0109 (0.0049) |
| 0.20 | 0.0000 (0.0000) | 0.0167 (0.0075) | 0.0005 (0.0002) | 0.1499 (0.0727) |
| 0.60 | 0.0001 (0.0000) | 0.1329 (0.0638) | 0.0046 (0.0021) | 0.6135 (0.4137) |
| 1.00 | 0.0002 (0.0001) | 0.2986 (0.1591) | 0.0127 (0.0057) | 0.8152 (0.6622) |

**The cohort's mix**, read from D17's committed stated fixture: of the forty, **15** carry rates
alone, **8** a currency alone, **2** rates and a currency, **11** crude (7 with rates, 3 with rates
and a currency, 1 with a currency), and **4** no leg at all.

**Table C. H12a's forward against the three alternatives, on firms whose hedge is resolved.** One
currency leg at 10% a year, true k 0.6, the firm's out-of-sample exposure d × k. Each cell: the
probability a resolved firm counts, and the median capture ratio.

| True R² | Resolved | d = 1¼ | d = 1 | d = 0.85 | d = ¾ | d = 0.6 | d = ½ | d = ¼ | d = 0 |
|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.935 | 0.949 (1.21) | 0.775 (1.12) | 0.596 (1.01) | **0.495** (0.90) | 0.259 (0.61) | 0.155 (0.28) | 0.013 (−1.04) | 0.000 (−3.64) |
| 0.15 | 1.000 | 0.998 (1.22) | 0.943 (1.13) | 0.735 (1.03) | **0.547** (0.92) | 0.168 (0.60) | 0.052 (0.08) | 0.003 (−4.21) | 0.000 (−10.46) |
| 0.40 | 1.000 | 1.000 (1.22) | 0.998 (1.13) | 0.925 (1.03) | **0.573** (0.92) | 0.037 (0.59) | 0.003 (0.02) | 0.000 (−10.38) | 0.000 (—) |

*A dash: no replication had an alternative that reduced variance. `simulate_capture(d, r2, 400)`
reproduces any cell; at about 27 seconds a cell (651 for the table) it is not in the suite. On a
smaller run at a true R² of 0.15, the alternative that wins is the **participating forward** in 55 of
60 replications at d = 1 and 49 of 60 at d = ¾, and the **collar** in 31 of 60 at d = ½: the
highest-delta alternative wins until the exposure halves.*

**What the tables say, before any number is read:**

1. **H14a is decided in sample.** Every firm in Table B except one whose crude exposure is above about half
   its market value sits at a true R² below 0.3, where the in-sample R² is below one half with
   probability one. So H14a's in-sample shadow will clear 70% as surely as H14a does, and **H14a's
   pass, if it comes, says the hedge was never clean, not that it degraded.** It is the register's
   claim — *"there is no clean hedge"* — and that is all it can be.
2. **H14b is carried by noise on the rates-only firms.** A firm whose hedge explains nothing counts
   toward H14b with probability **0.74 to 0.86** with no decay at all, because an in-sample R² is
   positive by construction and a held ratio fitted on noise removes nothing out of sample. Every
   rates leg sits at a true R² near zero: the one-year yield moved about two basis points a week
   between 2009 and 2014 (D17 §6). So the fifteen rates-only firms count at about three in four
   whatever happens, and H14b's 70% then needs genuine decay among the rest. A rough mixture — the
   fifteen at 0.75–0.86, the ten currency firms at 0.3–0.6, the eleven crude firms at 0–0.2 —
   reaches **two-fifths to three-fifths** of the thirty-six under no decay. The resolved subset (DD203 item 4) is
   where H14b means what it says.
3. **H14b has power where it can see.** At a true R² of 0.05 and v = 1 it counts a firm whose
   exposure halved out of sample with probability 0.807 and one that kept it with 0.187
   (Table A2 below).
4. **On the resolved firms, H12a and H14b are near-complements.** For a firm whose effectiveness is
   small, effectiveness_OOS ≈ (2d − 1)·R²_in with d the out-of-sample exposure over the held hedge,
   so **H14b counts it iff d < ¾**. An option structure with delta δ below one captures variance
   the forward loses once the exposure falls: the forward keeps 90% of the best alternative iff
   (2d − 1) ≥ 0.9·δ(2d − δ), which at δ between ½ and ¾ is **d above 0.70 to 0.76**. Table C
   measures it: the forward's count falls through one half at d = ¾ at every R², and even with no
   decay at all a firm at R² 0.05 counts only 0.775 of the time, because its held k carries noise.
   So the register predicts PASS for two claims that, on the firms where both mean anything, sit on opposite sides of the same
   number. Both can still pass, because H14b is scored over every evaluable firm and H12a over the
   resolved ones only. **Neither prediction moves** (A1 §5.5; D18's H4b precedent: a claim is not
   withdrawn at the package that scores it). The paper reports the complement.

**Table A2. H14b's power** (v = 1): the probability a firm counts when its out-of-sample exposure is
d times the in-sample one.

| True R² | d = 1 | d = ¾ | d = ½ | d = ¼ | d = 0 |
|---|---|---|---|---|---|
| 0.02 | 0.303 | 0.510 | 0.718 | 0.871 | 0.953 |
| 0.05 | 0.187 | 0.495 | 0.807 | 0.960 | 0.996 |
| 0.10 | 0.092 | 0.481 | 0.892 | 0.994 | 1.000 |
| 0.30 | 0.002 | 0.357 | 0.987 | 1.000 | 1.000 |

## 7. What leaves curvecast, and what deskcraft receives

> **DD202 — the out-of-sample half is computed where the prices are, and only statistics leave.**
> Alpha Vantage's and EIA's rows are `RESULTS_ONLY` (DD178) and are never committed, so D21's
> out-of-sample regression arithmetic runs in curvecast, in one script never imported by any package
> there, `scripts/measure_deskcraft_d21_replay.py`. It is written and rehearsed on DEV before the
> read, as the joint registration's §10 trigger was, and not run.
>
> 1. **Its guard.** It refuses, **before any request**, unless
>    `OWNER_AUTHORISATION_the_first_oos_read.md` exists in deskcraft, names DD37 and **D21**, and
>    carries a date no later than the day. C119's shape, read from curvecast's side.
> 2. **What it reads.** D17's fixtures (cohort, stated, measured), D17's kept cache for MV_T, the
>    one out-of-sample extraction's panels, EIA's contracts 1 and 2, and Alpha Vantage's weekly
>    series again. It keeps the out-of-sample rows in curvecast's ignored data directory, never in a
>    commit.
> 3. **What leaves.** `d21_replayed_oos_<date>.csv`, one row per cohort firm: `oos_end_date` (its
>    first date column, so C119 reads the file as what it is), `cohort_rank`, `cik`, `n`,
>    `effectiveness`, `eff_lo`, `eff_hi`, `multiple`, the four `vr_*` columns at the gated multiple,
>    `effectiveness_to_2025` (blank for a crude firm), the four `vr_*_stated` columns, and
>    `drop_reason`. **Never a price, never MV_T, never a weekly series.**
> 4. **The engine.** The structure marks are `deskcraft.effectiveness.structure_pnl`, loaded by the
>    script from deskcraft's source, so the arithmetic the bars test is the arithmetic that runs.

`src/deskcraft/effectiveness.py` holds the scorers, the structure engine and the null simulations.
It takes every fixture as a path and names no out-of-sample file, so C119 stays on its unauthorised
branch until the owner writes the authorisation.

## 8. Carried items, and the claims this document touches

**X15** — discharged for D21's three claims: §6 states each one's attainable range before any run,
and says where two of them cannot fail and where two of them pull against each other. **X7** —
discharged: every prediction in §9 is about a number that does not exist when this is written.
**DD171** — D21 fixes nothing D22's two verdicts depend on beyond §6.1's own rows, which it
restates: construction date, held, cohort. DD205 moves the timing of one owed cost row and no
number.

> **DD206 — D21 adds no claim and moves none.** H12a, H14a and H14b keep their wording, their
> predicted PASS and their scorer. This document fixes what they are computed on, publishes before
> any number exists that H14a cannot see decay and that H14b is carried by noise on rates-only firms,
> and reads H12a's missing prevalence as the median. Whether to keep any of them as registered or
> withdraw it before anything is read is **the owner's decision, and it is not taken here**.
> Unanswered, each is scored as written.

*Answered 2026-09-28 by DD232 (the joint registration's §12): all three are kept as registered,
and the labels the paper states beside H14a and H14b are fixed there.*

## 9. Predictions, scored when the package lands

| # | Prediction |
|---|---|
| P1 | **H14a PASS**, and its in-sample shadow clears 70% too |
| P2 | **H14b PASS**; on the resolved subset its share is below its share on the whole evaluable set |
| P3 | **H12a PASS** (the register's prediction), on at least five eligible firms |
| P4 | The median in-sample R² over the evaluable firms is below **0.02** |
| P5 | Every rates-only firm's k interval contains zero, so none of the fifteen is H12a-eligible |
| P6 | The winning alternative in H12a is the **participating forward** for more eligible firms than either of the other two: the highest delta of the three wins unless the exposure halves (Table C's note) |

## 10. What this could still get wrong

1. **Table A assumes normal weekly returns and one σ_e in both halves.** Fat tails widen every
   sampling distribution, and a firm whose residual variance rose after 2014 loses effectiveness
   with no change in its exposure. Both push H14b towards counting. Neither moves a rule.
2. **H12a's eligibility reads D17's bootstrap interval**, and Table C stands a normal interval in for
   it. The two agree to the second decimal at 261 weeks only if the weekly returns are close to
   independent, which the four-week block exists to allow them not to be.
3. **The volatility is realised, not implied.** It understates what a bought option cost, as §6.1
   says of its own source (2). Here it moves strikes and deltas, not a premium in the measure.
4. **The window ends in April 2024 for every firm.** It carries 2022, which is what an out-of-sample
   rates test most needs, and drops twenty months that would have added no crisis.

## 11. The replay, prepared and rehearsed, not run

*Written 2026-09-27, after D17 landed (`09b6e53`) and before the first out-of-sample read:
`docs/OWNER_AUTHORISATION_the_first_oos_read.md` does not exist. Nothing here read a row dated after
`DEV_END`. Everything above is unchanged.*

| | Prepared |
|---|---|
| The replay | curvecast `51fe282`, `scripts/measure_deskcraft_d21_replay.py`, DD202's one script. It loads `structure_pnl` and D18's gate from this repository's source, and D17's routes, factors and `market_value` from D17's script, so none of them is retyped |
| Its guard | `--replay` refuses before any read or request unless the authorisation exists, names DD37 **and D21**, and carries a date no later than the day. An authorisation written for four readers is refused (curvecast C536) |
| Rehearsal | `--rehearse` replays the held hedge over **D17's own fit weeks**, from D17's kept rows, with no network and no key. There DD200 makes the effectiveness *equal* D17's R², so the rehearsal tests the replay's weeks, factor moves and MV_T together. **All 32 fitted firms reproduce R² and n; the largest gap is 1.0e-15.** Given DD208's corrected market value for PG&E alone, it fails by 9.4e-4, so it enforces DD208's rule that MV_T is D17's function on D17's inputs. The four structures are struck through D18's gate and marked on the **7** firms whose k interval lies above zero, and `h14` and `h12a` read the file. A curvecast gate, `curvecast:deskcraft-d21-rehearsal`, re-runs it |
| Receiving side | `load_replayed(path)` reads what the script writes, and the writer refuses a row that carries anything outside DD202's columns (curvecast C540). No module names an out-of-sample file, so C119 stays on its unauthorised branch |

> **DD209 — two readings the replay fixes before the read, neither able to move a verdict.**
> (1) An observation with no factor value within D17's ten days **cuts the series there**, as
> DD201 item 4's gap does: a structure cannot be marked across a missing level, and D17 skipped
> such a week rather than bridging it. The DEV weeks have none, which is why the rehearsal
> reproduces every n. (2) **The rehearsal alone** takes its volatility history from 2008-12-24,
> because its path starts where DD204 item 7's history starts; the record is marked from
> 2009-12-24 as registered.

The rehearsal's structure comparison is **in sample**, so it scores nothing. It is recorded
because it shows the machinery running on real paths. The participating forward is the best
alternative on 6 of the 7, and the forward beats it on all 7, capturing 1.12 to 1.47 times its
variance reduction: what §6's finding 4 says a held hedge must do where the exposure has not moved.

## 12. Two numbers beside the verdicts, fixed before the read

*Written 2026-09-28, before the first out-of-sample read: `docs/OWNER_AUTHORISATION_the_first_oos_read.md`
does not exist, and no row of either source below dated after `DEV_END` has been read. Everything
above is unchanged. Neither decision adds a claim or moves one. Each fixes a number reported beside
H12a with no verdict, so that neither can be chosen after the record is seen.*

> **DD210 — H12a's structures are marked a second time at the Minneapolis Fed's implied volatility,
> beside the verdict and never in it.** §10 item 3 says realised volatility understates what a bought
> option cost, and DD204 item 7 left the implied source out because its mapping to these factors was
> unwritten. The owner admitted the Fed's option-implied distributions for D22 (DD178) and extended
> the admission to D21 (`OWNER_ADMISSION_d22_results_only_routes.md` §7). This is the mapping.
>
> 1. **The source.** `mpd_stats.csv`, the Fed's market-based probabilities statistics file, fetched
>    once at D21's read with the replay's declared user agent. Its data dictionary defines `sd` as
>    the standard deviation of the distribution of the log return to the contract's horizon,
>    sqrt(Σ p(x)·(x − mu)²).
> 2. **The mapping.**
>
>    | D17's factor | The Fed's market | Model |
>    |---|---|---|
>    | `EUR` | `euro` (Euro-USD futures, CME) | Garman–Kohlhagen |
>    | `GBP` | `pound` | Garman–Kohlhagen |
>    | `JPY` | `yen` | Garman–Kohlhagen |
>    | `WTI_C2` | `oil` (WTI crude futures, CME) | Black-76 |
>
>    **`SVENY01`, `CAD`, `CHF`, `CNY` and `MXN` are not mapped and stay on EWMA**, counted. The Fed
>    publishes no distribution for the four currencies. Its rate markets are three-month LIBOR three
>    and five years forward and the five- and ten-year Treasury futures' prices; none is a one-year
>    yield, and a futures-price density becomes a yield volatility only through the
>    cheapest-to-deliver bond's duration, which the file does not carry.
> 3. **The conversion.** **σ = sd / √½**, the six-month figure annualised. The contracts behind it
>    expire five to seven months out, so the annualisation is wrong by −8.7% to +8.0%, with a sign
>    that varies by release and is not known. No correction is attempted.
> 4. **Which release.** **The latest release on or before the observation date, and no more than 10
>    days before it** (D17's tolerance, DD209). Otherwise that mark takes EWMA's figure, and is counted.
> 5. **Reading the file.** The date column is the one column whose every value is a date (ISO,
>    optionally with a zero time, or M/D/YYYY). The market column is the one column that carries all
>    four names. `sd` must be a column. If any of the three fails, or a mapped market carries two rows
>    for one date, **the sensitivity is `NOT_PERFORMED` and says why; it never falls back silently**.
>    A row whose `sd` is not finite or not positive is refused and counted. **If a mapped market's
>    median `sd` over the rows kept exceeds 1, that market's `sd` is read as percent and divided by
>    100**, and the output says so: a six-month log-return deviation above one, as a median over a
>    decade, is a unit, not a market.
> 6. **Dropped on arrival.** Rows dated after 2025-12-31 and every market not in the table are
>    discarded in memory before anything is kept. What is kept is date, market and `sd`, in
>    curvecast's ignored data directory, never committed.
> 7. **What is computed.** The three alternatives' variance reductions at the gated multiple, with
>    each mapped leg's options struck and marked at the Fed's volatility wherever item 4 finds one. The
>    forward is linear and reads no volatility, so its reduction is DD204's. **H12a's count, median
>    capture and winners are reported again on these, beside the verdict. The verdict is DD204's, on
>    EWMA, and this does not move it.**
> 8. **What it can move.** Four of the seven firms whose k lies above zero in sample: ranks 1 and 5
>    (crude), 13 (sterling and crude) and 21 (euro, sterling and yen). Ranks 18, 23 and 26 hold only
>    unmapped legs, so their numbers are EWMA's by construction.
> 9. **What leaves.** Appended after DD202's columns: `vr_bought_option_implied`,
>    `vr_zero_cost_collar_implied` and `vr_participating_forward_implied`; `implied_fraction`, the
>    fraction of the firm's option marks on mapped legs that the Fed priced; and `implied_basis`, one
>    line saying what was read (the conversion, any market read as percent, the rows refused) or why
>    nothing was. **Never a volatility.**
> 10. **Rehearsed without the file.** The file arrives whole, to this week, so it is not fetched
>     before the authorisation, even for its DEV rows. The rehearsal hands the implied path a table
>     built from EWMA itself, and it must reproduce DD204's reductions exactly. That tests the
>     plumbing and not the source.
> 11. **D22 takes the same mapping.** §6.1's list and DD176 needed it too and did not write it. It binds
>     D22's option legs from here, and both are annotated in place. No D22 verdict reads a volatility
>     (H15 and H16 score the linear hedge, and the option numbers are beside them), so DD171's label is
>     not owed.

> **DD211 — the refused 2:1 ratio forward is marked on the record's path, beside H12a, with no pass
> or fail.** H13 passed at D18 and could not fail: the gate refuses the ratio forward by
> construction. What that refusal was worth is a question about paths, and the record has two stress
> windows on it. The data are the ones D21 already reads.
>
> 1. **The structure.** DD193's: the protective option bought ×1 and the opposite sold ×**2** at the
>    one strike where it costs nothing, rolled on DD204's 26-week clock at DD204's EWMA volatility and
>    marked as the other structures are. **At 100% of the stated exposure its worst state obliges
>    twice the exposure, so D18's gate refuses it on every firm.** It is marked beside the gate and
>    never constructed through it.
> 2. **The measure: the worst fall of the gap.** At **100% of the stated exposure**, on every evaluable
>    firm: the weekly P&L of the ratio forward less the forward's, summed over the firm's legs and
>    cumulated from zero. The number is **the largest fall from a running peak that starts at zero,
>    per dollar of stated exposure** (the sum of the legs' amounts). It is taken over all the verdict
>    weeks, and within `NBER_2020` and `RATES_2022` separately, each cumulated from the window's first
>    scored week. A firm the ratio forward never trailed reports 0.
> 3. **Variance, beside it.** The ratio forward's variance reduction at the gated multiple and at the
>    stated exposure, on H12a's eligible firms. **Variance reduction cannot see the obligation.** Where
>    k exceeds one, which is six of the seven in sample, the ratio forward's extra delta hedges more
>    of a firm whose value moves more than its stated exposure, so the structure the gate refuses can
>    score above the forward. That is why item 2's measure is a loss on a path and not a variance.
> 4. **At the gated multiple, rank 5 is admitted.** Its k is 0.39, so its sold leg is 0.78 of the
>    exposure and the gate would construct it. It is reported with the others and is not singled out.
> 5. **What leaves.** Appended after DD210's columns: `vr_ratio_forward`, `vr_ratio_forward_stated`,
>    `ratio_gap`, `ratio_gap_2020` and `ratio_gap_2022`. Statistics only.
> 6. **Not a price of a knock-in or knock-out structure.** DD193's ratio forward has no barrier. This
>    measures what leverage cost on the record, and says nothing about what a barrier product would
>    have cost.
> 7. **Nothing reads it.** Paper 2 reports it as what the gate kept the client from, in 2020 and 2022,
>    and says item 6 beside it.

§11's rehearsal runs both on D17's fit weeks, where they score nothing. Handed EWMA's own table,
DD210's path reproduces every alternative's reduction to the last digit on the seven firms, prices
every mark on the four mapped ones, and moves no count. DD211's worst fall is marked on all 32
replayed firms. Its six largest belong to firms with a crude leg, the largest a quarter of the
stated exposure. The ratio forward's variance reduction is above the forward's on all six firms whose
k exceeds one and below it on rank 5, so item 3 already shows in sample. P9 and P10 are written from
these numbers, before any out-of-sample row exists.

**Predictions added 2026-09-28, scored when the package lands.**

| # | Prediction |
|---|---|
| P7 | No eligible firm's H12a count differs between EWMA and the Fed's volatility: in sample the forward's reduction was 1.12 to 1.47 times the participating forward's, the usual winner (§11), a margin a change of volatility is not expected to close |
| P8 | The Fed's releases price more than half the option marks on the mapped legs of every mapped eligible firm |
| P9 | The ratio forward's variance reduction at the gated multiple is at least the forward's on more than half the eligible firms whose k exceeds one, and below it on rank 5 if rank 5 is eligible |
| P10 | The largest `ratio_gap` over the verdict weeks belongs to a firm with a crude leg |

*Next free ids: ~~C192 / DD207 / X26~~ ~~C195 / DD210 / X26~~ **C200 / DD212 / X26** (after DD210 and DD211).*
