# D12, D14, D15, D22 — one registration for the one irreversible surface

**Status: LANDED 2026-09-28.**

*Written 2026-09-25, from `930e896`. DD134 requires the four packages that read the out-of-sample
record to be registered in one document before the first read, and DD133 requires the owner's
written authorisation, `OWNER_AUTHORISATION_the_first_oos_read.md`, before any row dated after
`DEV_END` is committed or named. This document is the registration. It is marked registered and
not landed (DD161): the four packages land only when their out-of-sample run has happened and their
verdicts exist, and until then `closed()` counts none of them.*

---

## 0. Why "registered" is a status, and what DD161 changed

This repository's rule since D3a (DD31) is that a pre-commit's existence **is** its package's
landing: C34 then demands a verdict for every claim the package scores, and C76 demands a written
answer for every carried item it owes. DD129 found the first document that wanted to be written
before its package ran, and worked around the rule; its own §4 item 1 said *"if a second and third
want the same separation, the definition is the defect."* This is the second. DD133 needs this
document in the tree **before** the first read, and D12's three claims (H6, H7, `SCENARIO_SIGNS`)
cannot be scored until after it.

> **DD161 — a pre-commit may declare itself registered and not landed.** `closed()` counts a
> pre-commit only if it does not carry the line `**Status: REGISTERED, not landed.**`, and it reads
> the packages a pre-commit covers from its filename, so this document covers all four readers
> rather than only D12. C158 holds the marker to this one document: no other package may use it to
> postpone its verdicts.
>
> **DD172 — the marker may name the packages it registers** (2026-09-26, before the read).
> `**Status: REGISTERED, not landed, for D22.**` registers the packages it lists and lands the rest
> of those the filename names. DD168's option 1 makes that the state after the read: D12, D14 and
> D15 land with their verdicts, and D22 waits under §6.1. Written now, so the landing commit edits a
> status line and invents no mechanism. C158 holds both forms to this one document.

---

## 1. The surface, and the receiving side (X13)

| | Fixed |
|---|---|
| Window | `OosWindow.whole()`: **2015-01-01 → 2025-12-31** (DD98) |
| Series | the source register as it stands (DD100): the seventeen public-domain daily series, the admitted credit pair (DD140), and the six H.10 majors (DD168, `panel_daily_fx_dev_20260926.csv`), which only D22 reads and which ride this one extraction so that D22 never needs a second |
| Vintage rule | **DD166: the latest vintage on or before `OOS_END`**, which is D3b's rule as implemented (DD43, latest vintage on or before `DEV_END`) with the record's own end. `AMENDMENT_A4` §3.4 and DD101 paraphrased D3b as *"a vintage dated on or before its own observation date"*; that is not what D3b did, and taken literally it refuses every weekly-published H.10 observation, which would leave the hand-built book with no complete row. Superseded here. The fit sample and the record are then on one value basis: each observation as revised through its own window's end. The refused tail is the observations whose earliest vintage falls after `OOS_END`, expected to be the last sessions of December 2025 for series published with a lag, named by the generator at extraction. First release against latest revision was **not measured**: it would read vintages dated after `DEV_END` |
| Extraction | curvecast's `make_deskcraft_panel.py`, in the one commit DD102 reserves, which does nothing else |
| Interface | each reader takes a **surface**, a function from a series tuple to daily changes. The real run calls `panel_surface(receive_oos(panel))`; the dry run already runs the same `panel_surface` through `dev_surface`, so the read executes reviewed code. The trigger commit adds the fixture and the one line that loads it. No module names an out-of-sample file until then, so C119 holds until the owner's authorisation exists |
| Foreclosure | the first read of a post-`DEV_END` row fires **DD37** in curvecast and spends its two remaining looks for anything a deskcraft series touches. Irreversible |

**X13** — discharged: the receiving side is the table above. On receipt, D12 checks the fixture's
dates lie inside `OosWindow.whole()`, that its grid is GSW's weekday sessions exactly, and that every
series of the register is present, before any statistic is computed: `readers.receive_oos`, which C166
runs on a synthetic panel. Vintage refusals are named by curvecast's generator at extraction.

---

## 2. What every reader is handed

Every reader is **constructed at 2014-12-24** (the last session `DEXUSEU` carries in DEV) on objects
fitted over **DEV through that date** (`readers.REAL_FIT` ends on the construction date, so no fitted
object sees the four sessions after it), frozen there, and held through the surface. C165 pins every
such object before the read. The book and the view are fixed:

- the **hand-built book** is `US_CASH_BOOK` at its stated notionals;
- the **constructed book** is D7b's headline cell for `REFERENCE_VIEW` on the DEV basis, with the
  candidate pool restricted to series observed on the construction date (**DD162**; all eleven are,
  so this changes nothing on the real run and exists for the DEV dry run, where `DFII30` does not);
- every book is scaled to `RISK_BUDGET_ES` on the **`SAMPLE`** fit covariance (DD158). D14's
  first-ranked variant scales only D15's secondary descriptives (§5.3), because it is chosen on the
  record itself;
- **"held" means frozen exposures**: constant DV01 and constant maturity on every rate leg, a frozen
  FX delta on the euro, no carry, no roll-down, no FX differential. Every P&L and every Sharpe ratio
  below is rate-change and spot P&L only, and is reported as such.

---

## 3. D14 — the risk-model backtest

`src/deskcraft/riskbacktest.py`, run by `readers.run_d14`. The book is `US_CASH_BOOK`, held.

| | Fixed |
|---|---|
| Variants | `SAMPLE` (primary), `LEDOIT_WOLF`, `EWMA` (λ 0.94, recursion walked forward on the book's P&L), `CRISIS` (the latest NBER window lying inside the fit window: 2007–09 on the real run; a variant that cannot be fitted is refused by name, never replaced), all Gaussian, all fitted on DEV |
| Tests | Kupiec and Christoffersen at 97.5% and 99%; the Basel traffic light at 99% over non-overlapping 250-day blocks; Acerbi–Székely Z1 and Z2 at 97.5%, p-values from 5,000 simulations under the model; FZ0 at 97.5% and Diebold–Mariano against the primary |
| **H1** (predicted PASS) | **PASS iff**, on the primary, Kupiec has p ≥ 0.05 at **both 97.5% and 99%**, **and** Acerbi–Székely Z2 at 97.5% has p ≥ 0.05. *(**DD163**, tightened after the DEV dry run and before any out-of-sample read: the first version tested Kupiec at 99% only, and the dry run showed it passing a model that took 35 exceptions against 69 expected at 97.5%, the level DD146 makes primary. The change moves against H1's predicted PASS, §9.)* **A correctly specified model fails this conjunction about 11.5% of the time** (the independent review's 200 null simulations), which is its size and is reported beside it |
| **H2** (predicted FAIL) | **PASS iff** Christoffersen's independence test at 97.5% has p ≥ 0.05 on the primary |
| Power, published before the run | Kupiec, exact binomial, at both levels. The record is about **2,760 sessions** once holidays leave (2,870 is grid rows). At 99% against true rates of 1.5% / 2% / 3%: **0.668 / 0.991 / 1.000** at 2,760, 0.701 / 0.994 / 1.000 at 2,870. At 97.5% against 3.75% / 5% / 7.5%: **0.967 / 1.000 / 1.000** at 2,760, 0.973 / 1.000 / 1.000 at 2,870 |
| **DD135's rule, as code** | the variant of lowest mean FZ0 **among those with a lower mean FZ0 than `SAMPLE` and a two-sided Diebold–Mariano p below 5%** (one-sided 2.5%); if none, `SAMPLE`. One answer, evaluated by `run_d14` and handed to `run_d15` as a `D14Result`, so the hand-off cannot be skipped. It scales **only D15's secondary descriptives**: H5 and the three null tests are invariant to it, because a variant rescales a book and a Sharpe ratio is scale-free (C166) |

---

## 4. D12 — the scenario engine

`src/deskcraft/scenarios.py`, run by `readers.run_d12`.

| | Fixed |
|---|---|
| Windows | `scenarios.REPLAY_WINDOWS`: NBER 1990, 2001, 2007–09 (DEV), NBER **2020-02 → 2020-04**, and calendar **2022**, which the D12 row names. Five replayed; **H6 and H7 are read on the two out-of-sample windows only (DD167)** and the three DEV windows are reported beside them |
| The replayed book | the constructed book, min-variance weights at unit gross DV01, scaled to budget |
| FHS | per-series GARCH(1,1) by Gaussian likelihood on DEV; whole-day residual vectors resampled; 5,000 paths; the start state is GARCH's unconditional variance (**DD165**), so no row between DEV's end and a window's start is needed |
| Three-factor model | the first three principal components of DEV's covariance of **the whole eight-zero curve**, Gaussian, iid, cumulative over the window's length; its quantile in closed form, the limit of its Monte Carlo. The first version took components of the book's own two series, where three components are no truncation at all (the independent review's finding 4). **What it can detect, stated:** for this book the truncation removes under 1% of variance, so H7 tests iid-Gaussian √h scaling of DEV volatility against the realised window, not factor truncation |
| **H6** (predicted PASS) | the gross change in min-variance weights when the window's own correlations replace DEV's, volatilities held at DEV's. **PASS iff above 20% in both out-of-sample windows** (DD167) |
| **H7** (predicted PASS) | **PASS iff** the realised \|cumulative P&L\| exceeds the three-factor model's 97.5% quantile of \|cumulative P&L\| in **both out-of-sample windows** (DD167) |
| **DD167, and the direction it moves** | The first version read H6 and H7 on all five windows. Three lie inside DEV, inside the sample of every fitted object, so their values were computable before the read: on the real construction, **H6's change is 0.007 / 0.214 / 0.040** (one of three above 20%) and **H7 is 0 of 3** (C165). Under the 3-of-5 rule **H7 was already a FAIL** whatever the record showed, which is not an out-of-sample verdict. Reading both on the two out-of-sample windows makes them verdicts the read can move. **This removes in-sample evidence that runs against both predictions**, the flattering direction, so the DEV figures are reported beside the verdicts and the rule taken is the strict one: both windows |
| A window that cannot be computed | refused with its reason, and counted as **not above** either bar |
| `SCENARIO_SIGNS` | **REPORTED** (DD153): `US_CASH_BOOK`'s realised leg signs in each window it reaches, printed beside the source's four-scenario table. No classification of windows into the source's scenarios, which is where the under-determination lives |

---

## 5. D15 — the construction backtest

`src/deskcraft/construction.py`, run by `readers.run_d15`.

### 5.1 The power check, planned before it was run

The owner's second open question (`IDEATION_before_the_first_oos_read.md` §3, §5) is whether D15
gains a fourth null. The measurement that settles it was run on **DEV only**, as a pseudo
out-of-sample split with the real record's length, and this plan was committed to the document
before the run.

| | Fixed before the run |
|---|---|
| Fit window | 1988-01-01 → 2003-12-31. Basis refitted on it, levels at its last session |
| Test window | 2004-01-01 → 2014-12-31: eleven calendar years, the real record's length (DD98) |
| Legs | D7b's headline cell on the refitted basis, `REFERENCE_VIEW` |
| Books | **ES-constrained** = D11's `CVAR_LP`; **1/N** across the same legs; the **single-instrument** null = the greedy's first leg alone; the **hand-built** `US_CASH_BOOK`. All at one budget, held |
| Separating statistics | weight distance (total variation of weight shares); ex-ante ES of the difference as a fraction of budget; realised P&L correlation |
| The test | Ledoit–Wolf (2008) `HACPW`, ES-constrained minus 1/N; the minimum detectable difference at 80% power, 5% two-sided |
| Plausible effect | Δ* = (view exposure per unit budget, ES-constrained ÷ 1/N − 1) × 1.0 — the gain if the view itself carried an annualised Sharpe of 1.0, a generous bound for a rates view |
| **Decision rule** | Power at Δ* **below 0.5**: no fourth null; H5 keeps its registration with its power beside it; the separating statistics are reported with no verdict; the failure grammar is fixed in advance. **0.5 or more**: H5 stands as written |

### 5.2 The result, and question 2 settled

| | DEV pseudo out-of-sample, 2004–2014, 2,752 sessions |
|---|---|
| Legs | `out_sveny30_short`, `spr_sveny03_sveny30_short` |
| Weight shares, ES-constrained / 1/N | 0.4865 / 0.5135 against 0.5 / 0.5; **distance 0.0135** |
| Ex-ante ES of the difference | **0.19** of the budget; realised correlation **0.977** |
| Sharpe, ES-constrained / 1/N | −0.196 / −0.227; difference **+0.032**, s.e. 0.068, p 0.64 |
| **Minimum detectable difference** | **0.190** |
| Δ* | 0.034 (the optimiser buys 3.4% more view per unit budget) |
| **Power at Δ*** | **0.080** |

**The rule fires. DD164 — question 2 is settled: D15 gains no fourth null.** The two books are
*not* the same book (IDEATION §3's "converge by construction" is too strong: their weights differ and
the ES of their difference is a fifth of the budget), but a Sharpe race cannot see the difference.
Detecting it needs 0.19 of annualised Sharpe, and the most the view could plausibly deliver is
0.034. A fourth null would add a trial and fix none of that. **H5 stands, registered with its power:
8%.** A FAIL of H5 is therefore the expected outcome of the test's power, and is read that way.

**H5's failure grammar, fixed now.** H5 is scored by the Ledoit–Wolf test as registered: **PASS iff**
the difference is positive with p < 0.05. Then:

| Outcome | What it means |
|---|---|
| PASS | the optimiser beat 1/N by more than 0.19 of Sharpe on eleven years. Against a power of 8% at the plausible effect, read first as luck and second as signal |
| FAIL, difference positive | the sign the construction predicts, below what the test can see. Not evidence against the optimiser |
| FAIL, difference negative with p < 0.05 | the optimiser's covariance or scenarios did not transfer to the record. A finding about the fit window, reported with D14's verdicts beside it |
| FAIL, difference negative with p ≥ 0.05 | nothing: the test's power at the plausible effect is 8% |

**The separating statistics are reported with every verdict and carry none of their own**: weight
distance, ex-ante ES of the difference, realised correlation, and realised view exposure per unit of
realised ES for both books.

### 5.3 The rest of D15, fixed

| | Fixed |
|---|---|
| Nulls | the three registered: single instrument, 1/N across the same legs, the hand-built book. **No fourth (DD164)** |
| Intervals | stationary bootstrap, mean block 21 sessions, 10,000 resamples, seed 20260925 |
| Deflated Sharpe | on **7,836 trials**: every leg evaluation D7b reported across its ladder (7,830) plus D11's six sizing rules. The trial Sharpe variance is the variance of every pool-allowed candidate leg's Sharpe, each held alone over the fit window |
| PBO | CSCV over the sizing rules' held P&L, sixteen blocks, **after merging any rule whose weight shares equal an earlier rule's within 1e-6** (on a two-leg book ERC and max-diversification coincide; the independent review's finding 9) |
| SPA | Hansen's consistent p-value, benchmark 1/N, the other distinct rules the alternatives, 2,000 resamples |
| Deflated Sharpe, named | the **ES-constrained** book's, on 7,830 evaluations of 462 distinct legs plus six rules; conservative, because evaluations are not independent trials |
| Covariance for scaling | **`SAMPLE`** for every verdict and the primary descriptives. D14's first-ranked variant for the secondary descriptives, labelled as selected on the record |

**X14** — discharged: the fourth answer, as `RIDER_X13_X14_one_surface_two_clocks.md` §3 registered
it. This document is committed before D14's first result exists, and every D15 choice D14's output
could inform is a rule with one answer: the covariance variant (§3's rule), the trial count, the
block length, the seed. Nothing in this section is left to be settled when a result is visible.

### 5.4 A risk-per-view test, planned before its power check

*Written 2026-09-26, before the check below was run, and committed on its own so the order is in
the history. The owner's calls of that day, this test among them, are **DD168** (§6).*

**Why this test and not a better return test.** H5 asks whether the sizing rule earns more; §5.2
measured that no eleven-year record can say, because the standard error of a Sharpe difference
falls with the square root of *years* and the plausible gain is a fifth of what the record can
see. D11's rules never claimed to earn more. They claim **less tail risk per unit of the view**
(DD156), and that is a second-moment statement, estimable from daily data at a precision a mean
never reaches. The claim the construction makes is testable; the claim H5 tests is not.

> **DD169 — a risk-per-view test joins D15 if, and only if, it can see the effect the construction
> predicts.** The plan below is fixed before its power is measured. If the rule fires, the claim is
> registered as **H18**; if it does not, nothing is registered and the statistic stays the
> verdict-free separating statistic §5.2 already requires.

| | Fixed before the check |
|---|---|
| Claim | **H18**: the ES-constrained book carries more view per unit of realised tail risk than 1/N across the same legs |
| Books | §5.1's **ES-constrained** (`CVAR_LP`) and **1/N**, each at the budget, held as §2 defines |
| Realised tail risk | historical ES at 97.5% of the held daily P&L, `sizing.tail_mean` (Acerbi–Tasche), on D15's one complete-case sample |
| View exposure | each book's `view_exposure` at the budget. Exposures are frozen, so realised and ex-ante view exposure are the same number |
| Statistic | **G = ln(v_ES / ES_ES) − ln(v_1/N / ES_1/N)**. Positive G: the optimiser holds more view per unit of realised tail risk. G is invariant to either book's scale, so the covariance variant cancels, as it does for H5 |
| Standard error and interval | stationary bootstrap of the paired daily P&L, §5.3's settings: mean block 21, 10,000 resamples, seed 20260925. The standard error is the resamples' standard deviation |
| **Verdict rule** | **PASS iff G > 0 and the two-sided p < 0.05**, p = 2Φ(−\|G\| / s.e.): H5's shape |
| Plausible effect | **G\* = ln(ex-ante view ratio)**: the optimiser's ex-ante advantage carried unchanged into realised risk. It needs no assumption about what the view earns, which is what made H5's bound a guess |
| Power, measured twice on DEV | **(a)** §5.1's pseudo split: fit 1988–2003, construct 2003-12-31, test 2004–2014, its own books at its own G\*. **(b)** The **real** construction's books (C165: `out_sveny30_short`, `spr_sveny10_sveny30_short`, constructed 2014-12-24, ex-ante view ratio 1.0398), at the real G\*, with the standard error measured over 2004-01-01 → 2014-12-24. That span lies inside the real books' own fit window, so G's **level** there is in-sample and is not evidence; only its dispersion is used |
| **Decision rule** | **Register H18 iff power at G\* is 0.5 or more in both (a) and (b)**, two-sided 5% (`construction.power`, the function §5.1 used). Otherwise H18 is not registered, and the reason is written in §5.5 |
| Prediction | fixed after the check and before the read, with the DEV evidence it rests on named |
| Trials | H18 adds no book and no rule, so `D15_TRIALS` does not move. It is a second test on H5's pair, and is reported as one |

### 5.5 The check, and H18 not registered

*Run 2026-09-26 after §5.4 was committed (`71ceee9`), through `run_d15` for (a) and the real
construction's own objects for (b). DEV only.*

| | (a) DEV split, 2,747 sessions 2004–2014 | (b) real books, 2,747 sessions 2004-01-05 → 2014-12-24 |
|---|---|---|
| Legs | `out_sveny30_short`, `spr_sveny03_sveny30_short` | `out_sveny30_short`, `spr_sveny10_sveny30_short` |
| G\* (ex-ante view ratio) | +0.0337 (1.0343) | +0.0391 (1.0398) |
| Standard error of G | 0.0221 | 0.0228 |
| Minimum detectable G, 80% power | 0.062 | 0.064 |
| **Power at G\*** | **0.334** | **0.404** |
| Realised G | +0.0433, p 0.0497, 95% bootstrap (+0.004, +0.089) | +0.0644, inside the books' own fit window, so not evidence |

> **DD170 — the rule does not fire, and H18 is not registered.** Power is 0.33 and 0.40 against
> 0.5. The risk test sees about four times what the Sharpe test sees, 8% becoming 33–40%, because a
> second moment is estimated from days where a mean is estimated from years. The effect it is asked
> to see, a 3–4% advantage in view per unit of tail risk, is still inside its noise: detecting it
> takes a G of 0.06. No claim id is used, `D15_TRIALS` does not move, and nothing about H5 changes.

**Two things are recorded because they are tempting.** On the DEV split the realised G is
+0.043 with p 0.0497: under H18's rule it would have **passed**. It is one draw inside DEV, the rule
was committed before it was seen, and a test with a third of its power that passes is read first as
luck, which is the reading §5.2 gives H5. And a **one-sided** test, or realised **volatility** in
place of realised ES, would raise the power. Chosen now, either would be chosen after the DEV split's
result was visible, and the second tests a different claim: `CVAR_LP` minimises tail risk, not
variance. Neither is taken.

**What stays.** G is reported with every D15 run, with no verdict: it is §5.2's separating statistic,
*realised view exposure per unit of realised ES for both books*, which `run_d15` did **not compute**
until this check. `D15Result.risk_per_view` computes it now, on its own seeded bootstrap, so no other
D15 statistic moved (C167).

**What it would take, which answers the owner's question in numbers.** Holding the real books'
dispersion and scaling by the square root of the record's length, an even chance at G\* needs about
**14 years** of daily record and 80% power about **29**. The Sharpe race needed about 340. The
out-of-sample window supplies eleven. A longer single record does not exist; **independent markets**
could supply the rest, which is what the other governments' curves are for, in a later paper and
under its own registration.

---

## 6. D22 — specified, not built

D22 needs **D17** (the exposure extractor, run in curvecast with SEC egress), **D18** and **D21**,
none of which exists. What can be fixed now is fixed:

| | Fixed |
|---|---|
| Windows | `scenarios.REPLAY_WINDOWS`, the same five as D12; verdicts on the two out-of-sample windows only (§6.1, DD171) |
| H15 (predicted PASS) | crisis-conditional hedge effectiveness under half the unconditional value, for at least 60% of the cohort, as registered |
| H16 (predicted PASS) | peak hedge-leg mark-to-market drawdown above 25% of trailing operating cash flow for at least one case client, as registered |
| The mark-to-market path | D12's replay machinery, applied to D21's hedge legs |
| Margin | stated, not measured, as the D22 row requires |

**The coupling this creates, for the owner.** DD134 put D22 in the same registration as D12, D14 and
D15. `AMENDMENT_A1` §7.2 made the engine and the hedging layer **two papers with no dependency running
backwards**, so that Paper 1 ships even if the exposure layer dies. As registered, Paper 1's first
read waits on three Paper 2 packages. The two ways out are owner decisions and this document takes
neither:

1. **Read for Paper 1 now, D22 later under this registration.** DD37 is spent at the first read
   whenever it happens, so a later D22 read costs curvecast nothing more. **But D22 is not
   choice-free**, and the first version of this paragraph said it was: D17's extraction, D18's
   structures and D21's hedge legs are unspecified, and would be built after the 2020 and 2022 P&L
   had been seen (the independent review's finding 7). Option 1 therefore makes D22's verdicts
   post-hoc unless D17, D18 and D21's choices are registered before the read.
2. **Wait** until D17, D18 and D21 exist, as DD134 reads today.

> **DD168 — the owner's calls, 2026-09-26.** Six, and none of them authorises the read: that is
> DD133's, and the owner's alone.
>
> 1. **Option 1.** Paper 1 reads without waiting for D22, and D22 reads later under this
>    registration. The price the first version of this section named is paid in full: before the
>    read, every choice of D17, D18 and D21 that D22's two verdicts depend on is fixed here (§6.1),
>    and any such choice made after the read is labelled in Paper 2 as made after 2015–2025 was seen.
> 2. **A risk-per-view test** is added to D15 if its power check fires, under §5.4's plan.
> 3. **Hedges are not rates-only.** D22's instruments are US rate legs, spot foreign exchange in the
>    H.10 majors, and options on both; options on gold and commodities too, where a lawful daily
>    price route exists, ~~and none has been found (DD127)~~ *(struck 2026-09-26: one exists for
>    crude oil, subject to the owner's admission, and DD127's reason binds H15 and not H16;
>    DD176)*. A hedge leg answers an exposure, not a
>    view, so **DD138's declined seventh grammar term is not reopened**: the currency series enter as
>    hedge instruments and risk factors, as `DEXUSEU` did under DD139, never as `CANDIDATE_SERIES`,
>    so DD120's candidate-set rule is untouched.
> 4. **Option legs are priced by a separate options library in its own repository**, not by a
>    deskcraft package. The 21-package budget does not move and D19 stays in the annex. deskcraft
>    imports the library under its import census, as it imports meip.
> 5. **The rules for every hedge leg, options included, are fixed in §6.1 before the read**, and the
>    library is built afterwards to them. Implied volatility is the one input with no known free
>    route (DD121), so §6.1 fixes an ordered list of sources, the modelled one last, rather than a
>    source.
> 6. **The H.10 majors join the panel before the read**, so the one extraction DD102 reserves carries
>    them: yen, sterling, Canadian dollar, Swiss franc, renminbi and Mexican peso, beside the euro.

### 6.1 D22's lock, fixed before the read

*Written 2026-09-26, before any row dated after `DEV_END` exists in this repository. Everything
below is a rule with one answer; D17, D18 and D21 are built later **to** it, and their pre-commits
restate it rather than choose. A choice any of them makes that this table does not fix is labelled
in Paper 2 as made after 2015–2025 was seen.*

> **DD171 — D22's verdicts depend only on choices fixed here.** The price of DD168's option 1.

| | Fixed |
|---|---|
| Construction date | **2014-12-24**, `REAL_AS_OF`. Every input is dated on or before it: a filing by its EDGAR **acceptance** date, never its period end; every price, rate, volatility and regression sample by its observation date |
| Held | Exposures frozen as §2 defines, hedge ratios **never re-estimated**. D21's row leaves rolling against held to be stated; it is stated here: held |
| Cohort | **40 firms, by rule.** Universe: every filer whose 10-K was accepted between 2014-01-01 and 2014-12-24 with XBRL financial data, SIC outside 6000–6799 (financial firms deal these risks rather than hedge them). Ordered by `Assets` at the fiscal year end that 10-K reports, largest first. Filters, in order: (i) an Item 7A quantitative market-risk disclosure; (ii) at least one exposure D22 can hedge, a rates read from the debt footnote or a currency read in one of the seven currencies; (iii) daily equity prices over the regression window from an admitted source *(skipped if none is admitted when D22 reads, DD178; skipped, because the admitted route does not reach, DD180)*. The first 40 survivors; every drop counted by reason. D23's twenty are eligible and not privileged (`AMENDMENT_A1` §3.4). A hand-picked cohort would manufacture the exposure puzzle (`RESEARCH_client_solutions_layer.md` §9.2) |
| Asset classes | **Rates and currency.** ~~Commodity is declined (DD127: the price route stops 2024-04-05).~~ **Crude oil joins H16 and the option reports, never H15, if the owner admits its price route** (DD176) *(admitted 2026-09-26, DD178)*. Credit is declined for D22: `CREDIT_VS_RATES` reaches no tradeable series (DD124). Both counted, never silently absent |
| Linear legs, rates | D7b's generator on the eleven-series pool at the construction date, the target the rates exposure vector sign-flipped, D7a's costs at the 1× rung. **A swap or a future, carried as cash** (DD175): every leg holds `ReExpression(original_kind=FUTURE, unmodelled=("financing", "delivery option", "roll", "futures-cash basis", "swap spread"))` |
| Linear legs, currency | Spot in the seven currencies (`panel.FX_QUOTES`), a frozen delta as `US_CASH_BOOK` holds the euro, each quote as H.10 publishes it. No forward points: the covered-interest construct is declined (DD117) and "held" carries no FX differential. **A forward, carried at spot** (DD175): every leg holds `ReExpression(original_kind=FUTURE, unmodelled=("forward points", "cross-currency basis"))` |
| Option legs | One **bought** European option per hedged exposure, **beside** the linear hedge and never replacing it: **six-month** tenor, **at-the-money** strike on the frozen level, notional equal to the linear leg's, struck to pay in the exposure's losing direction. Rolled every six months from the construction date, on the next session, at that day's inputs; every premium is a cash outflow on the path. **Never sold**: ~~selling optionality is what the suitability gate refuses (D18, H13)~~ *(reason corrected 2026-09-26, DD198: D18's gate refuses leverage above one, and a collar sells optionality at a leverage of exactly one, so the gate admits it. The rule stands and is D22's own; no verdict moves, and the read has not happened, so DD171's label is not owed)*. Rate options are priced on the normal model (Bachelier) on the leg's zero yield, currency options by Garman–Kohlhagen at zero rate differential, both by the separate options library (DD168 item 4) |
| Implied volatility | **An ordered list, and the first source available on the day decides.** (1) The Minneapolis Fed's option-implied distributions, six-month horizon, the latest release on or before the pricing date, **only if the owner admits the source by name** (§6.2) *(admitted 2026-09-26, DD178; mapped 2026-09-28 by D21's DD210, which this row lacked: euro, sterling, yen and crude to the Fed's `euro`, `pound`, `yen` and `oil`, σ = sd/√½, the release no more than 10 days old; every other instrument is unmapped and takes (2), counted)*. (2) Otherwise EWMA realised volatility (λ 0.94, D8's) through the pricing date, times **1.0**. Direction stated: implied trades above realised on average and leaps ahead of it in a crisis, so (2) **understates** a bought option's cost and its crisis mark-up. A weekly figure used as of a date is a pricing input, not a covariance input, so DD130's refusal does not reach it |
| Verdict windows | **`NBER_2020` and `RATES_2022`**, DD167's rule applied to D22. The three DEV windows lie before the construction date, inside every fitted object's sample, and are reported beside, never scored |
| **H15** | Scored on the **linear** hedge. Ederington effectiveness, 1 − Var(r + h·x) / Var(r), where r is the firm's daily equity log return and x the hedge's daily return per dollar of market value at construction, with h the minimum-variance ratio fitted over the **two calendar years ending 2014-12-24** and held. Unconditional: all of 2015-01-01 → 2025-12-31. Conditional: the pooled sessions of the two verdict windows. A firm counts iff conditional < ½ × unconditional; a firm whose unconditional effectiveness is ≤ 0 counts as **not** meeting it. **PASS iff at least 60% of the cohort counts**, Clopper–Pearson interval beside (`AMENDMENT_A1` §5.3). The option hedge's two numbers are reported beside, with no verdict |
| **H16** | Scored on the **linear** hedge at **100% of the disclosed exposure**, the hedge a reader of the 10-K builds and the one H11 predicts is too large. Case clients: the **first three firms of the cohort ordering**. Path: D12's replay of the frozen legs, cumulative from each verdict window's first session; peak drawdown from the running peak. Trailing operating cash flow: `NetCashProvidedByUsedInOperatingActivities` in the latest 10-K accepted before the window opens. Margin stated, not measured: **full daily variation margin, no threshold, no initial margin**, so the cash path is the mark-to-market path. **PASS iff** peak drawdown exceeds 25% of trailing operating cash flow for at least one case client in at least one verdict window. The option hedge's peak cumulative premium outflow is reported beside, with no verdict |

> **DD175 — each linear leg names the instrument it stands for and what the substitution drops.**
> A firm hedging a rate exposure uses an interest-rate swap and a desk uses a Treasury future; a
> currency exposure is hedged with a forward. None of the three has a free dated series that reaches
> the verdict windows: H.15's swap rows end 2016-10-31 and four vendor routes are paid or trial, no
> free dated Treasury-futures history was found (`AMENDMENT_A5` §5.3), and a forward built from two
> interest rates is wrong by the cross-currency basis where the basis is widest (DD117). So every
> linear leg is carried as DD12 carries the reference book's futures, first-order equivalent, with
> a `ReExpression` naming what it drops. `original_kind` is `FUTURE` for both, because
> `InstrumentKind` is closed, has no swap or forward member, and gains none: its docstring admits a
> member only where a bar downstream branches on it, and none does. The swap reading is carried by
> its own unmodelled entry, `"swap spread"`. **The dropped terms are largest in stress, which is
> what the verdict windows were chosen for**, so H15 and H16 are verdicts on hedging
> **on the Treasury curve and at spot**, and Paper 2 says so in those words. No verdict,
> prediction or scorer moves: this is a label, and D21 builds to it.

> **DD176 — D22 gains a WTI futures leg if the owner admits its price route, and the arm is thin.**
>
> 1. **A correction.** DD168 item 3 said no lawful daily commodity price route had been found, citing
>    DD127. DD127 declined Paper 2's commodity arm because EIA's NYMEX series stops **2024-04-05**,
>    twenty months short of 2015–2025. That reason binds **H15**, whose unconditional sample runs to
>    2025-12-31, and does **not** bind **H16**, which reads only `NBER_2020` and `RATES_2022`, both
>    inside the series. The sentence carried the decline over without checking the windows. DD127
>    stands for Paper 2's commodity arm, and X21 is unchanged.
> 2. **The route is not public domain**, and three documents said it was. EIA's table notes give the
>    source as *"New York Mercantile Exchange (NYMEX)"*; its daily prices page says *"Prices are
>    republished by EIA with permission as follows: [...] Prompt-Month Energy Futures from CME
>    Group"*; and its copyright policy says licensed third-party material *"may be protected"*, with
>    reproduction beyond fair use needing *"the written permission of the copyright owners"*. The
>    claim is struck in place, twice in the build order, twice in `AMENDMENT_A5` and once in
>    `RIDER_A5` §5. The route is `RESULTS_ONLY` at best, is never committed, and **needs the owner's
>    admission by name**, as Alpha Vantage and the Minneapolis Fed do (§6.2). **Not admitted, the
>    WTI arm is refused by name and counted, and nothing below applies.**
> 3. **Admitted, this is fixed now.**
>    - **The crude read** is curvecast `6f592de`'s rule, committed before its count: a fact on a
>      member, on any axis, naming crude oil or a refined petroleum product, or a fact whose concept
>      names one. Natural gas and a generic commodity-contract member are not crude reads.
>    - **It admits no firm.** Filter (ii) is unchanged; a crude read adds a leg to a firm already in
>      the cohort, so H15's cohort does not move.
>    - **The exposure** is the largest-magnitude crude-read fact for the fiscal year the 10-K reports
>      whose concept names revenue or sales (long crude) or a cost, expense or purchase (short
>      crude). A fact naming neither is counted and not used. One leg per firm, of the opposite sign.
>    - **The linear leg** is NYMEX WTI held in **contract 2**, EIA's second delivery month, and rolled
>      into the new contract 2 on the session the held one becomes contract 1, by CME's expiry
>      calendar as EIA defines contract 1. The quantity is frozen in barrels at construction, the
>      exposure's dollars over the held contract's settle on 2014-12-24, and carried through every
>      roll. Each daily return is taken on **one contract's two settles**, never across two
>      contracts, so no splice exists: build order §0 item 6's argument, now written. A non-positive
>      settle refuses that day's return and every mark that depends on it, counted, never imputed.
>      D7a's costs gain a row ~~before D21 builds~~ *before D22 builds (timing corrected 2026-09-26,
>      DD205: D21's measures are variances and price no cost; the number does not move)*, fixed
>      now: a half-spread of **one full tick**, $0.01
>      a barrel from CME's contract specification, which overstates the cost if the quoted spread is
>      one tick wide.
>    - **The option leg** follows §6.1's option row: bought, six-month, at-the-money, rolled, never
>      sold. It is priced by Black-76 with the held contract's settle as the forward. EIA publishes
>      contracts 1 to 4 only, so the six-month forward is unobserved and the held contract stands
>      in for it, which drops the curve's slope beyond contract 2. Implied volatility follows §6.1's
>      ordered list: source (1) only if the Minneapolis Fed publishes crude oil *(it does, as `oil`;
>      mapped 2026-09-28 by D21's DD210)*, otherwise EWMA of
>      the held contract's log returns times 1.0. OVX is Cboe's, and DD121 refuses it.
>    - **Where it enters.** H16's path, since the linear hedge at 100% of the disclosed exposure now
>      carries the WTI leg for a case client with a crude read, and the option comparisons beside
>      H16. **Not H15**: its unconditional sample outruns the series, and scoring one firm on a
>      shorter sample is what DD127 refuses. H15's hedge stays rates and currency, and says so.
>    - **When it is read.** At D22's own read (§10 step 5), not in Paper 1's extraction, so the one
>      extraction DD102 reserves is unchanged. EIA keeps no vintages, so DD166's rule cannot be
>      applied at the source; the series is read as published, and Paper 2 states that.
> 4. **The arm is thin.** On D23's twenty firms' 2014 instances a crude read reaches **5 of 17**
>    (curvecast `a6ea07c`, counts only, no request made), against a rule of half. All three D23
>    commodity firms with a 2014 instance read; so do one pipeline firm and one card lender. About a
>    third of the cohort, thinner than the currency arm's 8 of 17.

> **DD177 — the public swap tape does not reach the verdict windows, so the swap spread stays
> unmeasured.** US rules require every swap to be publicly reported, and DTCC's repository publishes
> that tape free. Its own user guide says the cumulative reports *"are available for 366 days from the
> current date with data available from December 29, 2023"*, that its Search tab reaches 365 days
> back, and that older reports are by request to DTCC's support desk. So the free route fails on
> reach before its licence is read: its earliest row is a year after `RATES_2022` ends. A report sent
> on request is not a published route and its terms are unread; asking for one is the owner's act,
> and it is not taken here. DD175's `"swap spread"` stays an unmodelled term.

> **DD178 — the owner admitted all three results-only routes by name, 2026-09-26.** The record is
> `OWNER_ADMISSION_d22_results_only_routes.md`. EIA's NYMEX WTI settlements, Alpha Vantage's daily
> equity prices and the Minneapolis Fed's option-implied distributions may be read and computed on,
> and none of them is ever committed. So DD176's WTI arm exists, H15 has its denominator, and §6.1's
> implied-volatility list starts at source (1). Nothing else in §6.1 moves: every rule the three
> routes feed was fixed before they were admitted.
>
> **One contradiction is closed with it.** §6.2 says a failed equity route refuses H15 by name, but
> cohort filter (iii) asks for equity prices *from an admitted source*, so with none admitted no firm
> would survive and H16 would have no cohort either. The Alpha Vantage admission lapses if the owner
> becomes employed by or affiliated with an investment firm, so the case can happen. The rule, fixed
> now: **if no equity source is admitted when D22 reads, H15 is refused by name and filter (iii) is
> skipped**, so H16's cohort is the first 40 survivors of filters (i) and (ii), every drop still
> counted by reason.

> **DD179 — a refined-product exposure is hedged with crude, and the lock says what that drops.**
> DD176's crude read counts a fact naming crude oil **or a refined petroleum product**, and its linear
> leg is WTI whatever the fact names. So a jet-fuel, diesel, gasoline or heating-oil exposure is a
> cross-hedge, and the product's spread over crude is unmodelled, as DD175's dropped terms are. It is
> a basis, like theirs, so H16's WTI arm is a verdict on hedging a product **with crude**, and
> Paper 2 says so in those words. No verdict, prediction or scorer moves: this is a label.

> **DD180 — the admitted daily route does not reach, so H15 is refused by name and filter (iii) is
> skipped.** Alpha Vantage's own documentation, read 2026-09-26: for `TIME_SERIES_DAILY`, *"compact
> returns only the latest 100 data points"* and *"The 'full' outputsize is available to premium
> keys"*; `TIME_SERIES_DAILY_ADJUSTED` is *"a premium API function"*. A free key reaches the last
> hundred sessions and nothing before them, so the two years ending 2014-12-24 are out of its reach,
> and a paid key is refused under free data only. The admission DD178 records stands. It admits a
> route that cannot deliver what §6.1 asks of it.
>
> 1. **H15 is refused by name**, as §6.2 says it is when the equity route fails, and carries
>    `NOT_PERFORMED` when D22 lands. It is **not** re-scored on weekly prices, which the free key does
>    reach (*"covering 25+ years of historical data"*): §6.1 fixes a daily return, §6.2 fixes what
>    happens when it cannot be had, and a weekly H15 would be a choice this lock did not make.
> 2. **Filter (iii) is skipped.** DD178's rule is read for what it is for: an admitted route that
>    reaches no firm's regression window empties the cohort exactly as no route would, so it counts
>    as none. The cohort is the first 40 survivors of filters (i) and (ii), every drop still counted
>    by reason.
> 3. **What the owner chose instead reaches D17 and D21, not H15.** Asked the same day, the owner
>    chose Alpha Vantage's free **weekly** adjusted prices for D17's and D21's own fits, with
>    quarterly operating cash flow from the filings as a second measure, reported beside and never
>    pooled. That is a new use of an admitted route, so it is recorded by name in the admission's
>    §6, and D17's pre-commit fixes how it is used. Nothing in §6.1 moves.

### 6.2 What D22 still needs, none of it a choice the record could inform

Each item is a licence or availability fact, read before the build. If it fails, the rule above says
what happens; nothing is re-chosen.

| Input | Where it stands, 2026-09-26 | If it fails |
|---|---|---|
| Currency-level exposure | **Probed 2026-09-26, and neither route holds** (curvecast `582d3ed`, `373f85a`, `cd77bf0`; counts only). On D23's twenty firms' 2014 10-K instances, a currency axis naming one of the seven reaches **2 of 17**, and a geographical member naming a single-currency country **7 of 17**, against a rule of half. Together, **8 of 17**, reported and not a verdict. D23's five currency firms carry no currency axis at all | Filter (ii) admits rates reads only for that firm; the drop is counted |
| Daily equity prices, H15's denominator | **Tiingo's free tier forbids persisting its data at all** (terms §1.6), so it cannot back a pinned fixture: refused. **Alpha Vantage's free licence** grants personal, non-commercial use including research, counts any passing-on to others as commercial, and counts use while **employed by or affiliated with an investment firm** as commercial. It is `RESULTS_ONLY` at best and **needs the owner's admission by name**, as DD137 admitted the credit tier, with that affiliation clause named in the admission. **Admitted by the owner 2026-09-26** (DD178), the clause named. **It does not reach**: the free key serves the last 100 sessions and full history is premium (DD180) | **H15 is refused by name.** It is never re-scored on the quarterly cash-flow denominator, which cannot see a three-month window. If the admission lapses before D22 reads, filter (iii) is skipped and H16 keeps a cohort (DD178) |
| Implied volatility, source (1) | The Minneapolis Fed permits use *"for research and informational purposes only"*; its methodology prices from Bloomberg trade data, and third-party material needs the owner's permission. So: computable for research, not redistributable, never committed, **needs the owner's admission by name**. **Admitted by the owner 2026-09-26** (DD178) | Source (2), the modelled volatility, with its stated direction |
| WTI settlements, DD176's price route | EIA's NYMEX contracts 1 to 4, daily from 1983 to **2024-04-05**, which covers both verdict windows and not H15's unconditional sample. **CME Group's prices, "republished by EIA with permission"**: not public domain, `RESULTS_ONLY` at best, never committed, **needs the owner's admission by name**. **Admitted by the owner 2026-09-26** (DD178) | **The WTI arm is refused by name**; H16 and the option reports carry rates and currency only |
| Crude-oil exposure | **Probed 2026-09-26** (curvecast `6f592de`, `a6ea07c`; counts only, no request). A crude read reaches **5 of 17**, against a rule of half. It admits no firm, so the only consequence is a thin arm | Nothing re-chosen: the arm is about a third of the cohort, stated |
| Swap rates, for DD175's swap spread | **DTCC's public tape, read 2026-09-26** (DD177): 366 days back, earliest row 2023-12-29; older reports by request only | The swap spread stays unmodelled, as DD175 already carries it |

> **DD174 — a firm's currency read is fixed now, and the currency arm will be thin.** A firm has a
> currency read in one of the seven iff its 10-K instance carries a fact on an axis whose name
> contains `Currency` with a member naming one of them, **or** a fact on a geographical axis with a
> member naming a single-currency country from curvecast `373f85a`'s table (Japan, the United
> Kingdom, Canada, Switzerland, mainland China, Mexico, a euro-area state or the euro area). A
> multi-currency region is never mapped. The exposure is the facts on those members, sign-flipped,
> into spot and bought-option legs in that currency. On D23's sample this reaches about half the
> firms, so **D22's currency legs will exist for roughly half the cohort and the rest enter on rates
> alone**, counted. A reading of Item 7A's text would reach more and is **not** added: its parser is
> D17's and its rules are not written, so adding it after the read would be a choice made after
> 2015–2025 was seen, and it is labelled so if it is.

**What this lock does not do.** It adds no claim. H15 and H16 keep their registered wording, their
predicted PASS and their scorer; the lock fixes what they are computed on. Options enter as reported
comparisons beside both, because a claim about them written now would be a prediction about a
library that does not exist yet.

---

## 7. The dry run

*Run after this document's sections 0 to 6 were written, on a DEV split: fit 1988–2003, surface
2004–2014, construction at 2003-12-31. It checks that the code runs end to end and the numbers
are sane. It is not evidence about the out-of-sample record.*

*(Results in §9.)*

---

## 8. The readiness checklist for the first out-of-sample read

The owner's third question is whether the read is authorised. It is decided against this list, and
by the owner only (DD133).

| # | Item | State |
|---|---|---|
| 1 | D12, D14, D15 built and frozen at a tagged commit | see §9 |
| 2 | D22 built, or the owner chooses option 1 of §6 | **open: owner decision** |
| 3 | This registration complete: power published, trial counts fixed, no parameter open | see §9 |
| 4 | Suite green, DEV fixtures pinned | see §9 |
| 5 | Full dry run on DEV | see §9 |
| 6 | An independent review of the dry run, units and basis in particular | see §9 |
| 7 | curvecast's trigger commit prepared and not run | not started, by design |

---

## 9. Result of the dry run

*Written after the run, 2026-09-25. DEV only: fit 1988-01-01 → 2003-12-31, constructed at
2003-12-31, surface 2004-01-01 → 2014-12-31. These numbers are about the code, not the record.*

**Built:** `scenarios.py` (D12), `riskbacktest.py` (D14), `construction.py` (D15) and the runner
`readers.py`. Bars **C158–C164**. D22 is not built (§6).

### 9.1 What the dry run caught, before any out-of-sample read

This is what the dry run was for. **Four defects, each fixed before the read**, and the independent
review (§9.4) found three blockers the dry run did not:

| # | Defect | Fix |
|---|---|---|
| 1 | The generator is not date-aware: at a 2003 construction its pool names `DFII30`, which opens 2010, and `select` crashes | **DD162**, `select(pool=...)`; the real run's pool is all eleven, so nothing published moves (C159) |
| 2 | **A look-ahead in D14's `CRISIS` variant**: it used 2007–09's covariance, which in the dry run lies *inside the test period* | the variant is the latest NBER window **inside the fit window**; 2007–09 on the real run, and refused by name in the dry run, whose 2001 window cannot see TIPS |
| 3 | **D15 paired its tests by position, not by date.** Books holding the euro and TIPS skip sessions the zero curve does not, so "the last n days" compared different days | every series is joined on shared dates. The hand-built comparison's standard error fell from 0.418 to **0.236** |
| 4 | **H1's rule could not see the level DD146 makes primary.** It tested Kupiec at 99% only, and passed a model taking **35 exceptions against 69 expected at 97.5%** | **DD163**: Kupiec at both 97.5% and 99%. The change moves against H1's predicted PASS (§3) |

And one defect in a bar, not the code: C162 called an equal-distribution SPA case "worse". SPA's
size, measured over 200 null draws, is **5.5%**, so that case fails one run in twenty. The bar now
compares against a genuinely worse set.

### 9.2 The dry-run numbers

*Re-run after the independent review's fixes; the book's P&L are now joined over the union of every
series any book holds, differenced once.*

| D14, `US_CASH_BOOK`, 2,747 sessions | 97.5% exceptions / expected | 99% | Z1 p | Z2 p |
|---|---|---|---|---|
| `SAMPLE` (primary) | 35 / 68.7 (Kupiec p 0.000) | 19 / 27.5 (p 0.085) | 0.000 | 1.000 |
| `LEDOIT_WOLF` | 35 / 68.7 | 19 / 27.5 | 0.000 | 1.000 |
| `EWMA` | 94 / 68.7 (p 0.003) | 53 / 27.5 (p 0.000) | 0.000 | 0.000 |
| `CRISIS` | refused: 2001 cannot see TIPS | | | |

- **DD135's rule evaluates to `EWMA`** and D15's secondary descriptives used it. The wiring works.
- H1's dry-run answer under DD163: **not calibrated**, the primary over-conservative, fitted on 2003
  alone because `DFII5` opens that year. H2's: independent at 97.5% (p 0.47).

| D15, 2,747 shared sessions | Sharpe difference | s.e. | p | 95% bootstrap | detectable |
|---|---|---|---|---|---|
| vs 1/N | +0.031 | 0.068 | 0.64 | (−0.087, 0.158) | 0.190 |
| vs single instrument | +0.065 | 0.212 | 0.76 | (−0.313, 0.451) | 0.594 |
| vs hand-built | −0.063 | 0.236 | 0.79 | (−0.526, 0.403) | 0.660 |

| D15 descriptives | view ratio | power at Δ* | PBO | SPA p | merged |
|---|---|---|---|---|---|
| `SAMPLE`, primary | 1.034 | 0.080 | 0.56 | 0.49 | ERC into max-diversification |
| `EWMA`, secondary, selected on the record | 0.965 | 0.081 | 0.46 | 0.42 | the same |

- Deflated Sharpe 0.0: every book lost money over 2004–2014, when yields fell on a short view.
- Under `EWMA` the optimiser buys 3.5% *less* view per unit budget than 1/N, and under `SAMPLE` 3.4%
  more. The optimiser minimises historical CVaR on the fit window; the budget is measured on a
  covariance, and which book is cheaper depends on which covariance. This is why the secondary is
  labelled and the primary is `SAMPLE`.

| D12, DEV windows (dry run) | days | realised | three-factor 97.5% | FHS 97.5% | H6 change | H7 understated |
|---|---|---|---|---|---|---|
| NBER_1990 | 184 | −5.35m | 12.9m | 14.4m | 0.350 | no |
| NBER_2001 | 187 | −6.15m | 13.0m | 14.2m | 0.460 | no |
| NBER_2007 | 394 | −7.83m | 18.9m | 21.2m | 0.107 | no |

On the **real** construction the same windows give H6 0.007 / 0.214 / 0.040 and H7 0 of 3 (C165): the
reason for DD167. `SCENARIO_SIGNS`: only 2007–09 reaches the hand-built book; the 2y, 10y and
breakeven legs lost and the euro short gained.

### 9.3 The checklist, updated

| # | Item | State |
|---|---|---|
| 1 | D12, D14, D15 built and frozen at a tagged commit | built; the real construction pinned by C165; tagged at this commit |
| 2 | D22 built, or option 1 of §6 chosen with D17, D18, D21 registered | **done**: option 1, taken by the owner (DD168), with every choice D22's verdicts depend on fixed in §6.1 (DD171). §6.2's owed inputs are not conditions for the read |
| 3 | Registration complete, no parameter open | done: power at both levels, H1's size, trials 7,836, seed, block 21, the vintage rule (DD166), the verdict windows (DD167) |
| 4 | Suite green, DEV fixtures pinned | done |
| 5 | Full dry run on DEV | done |
| 6 | Independent review | **done**, §9.4: three blockers and three majors, every one dispositioned |
| 7 | curvecast's trigger commit prepared, not run | **done**: curvecast `3112140`, rehearsed on DEV against the committed panels, guarded against running without the authorisation, not run (§10, DD173) |

### 9.4 The independent review

Run 2026-09-25 by a separate reviewer with read-only access, briefed to hunt look-ahead, unit and
basis mixing, misalignment, wrong test implementations and open parameters. **It confirmed** the
statistical machinery against the papers and measured its size under the null (Ledoit–Wolf 4.3%,
Kupiec 5.5% and 6.0%, Christoffersen 5.5%, SPA 4.3–5.0%); that the dry run reads nothing past its fit
window except the construction-date levels and the surface; that every basis-point exposure meets a
basis-point change and the euro's −914,100 USD per 1% is right in sign and size; and that EWMA's
forecast for a day uses only earlier P&L. **It found:**

| # | Severity | Finding | Disposition |
|---|---|---|---|
| 1 | BLOCKER | H7 already FAIL and H6 mostly decided by the three DEV windows under the real construction | DD167, §4: verdicts on the two out-of-sample windows, DEV values reported, the direction stated |
| 2 | BLOCKER | The vintage rule as written is unimplementable and leaves the value basis open | DD166, §1 |
| 3 | BLOCKER | The out-of-sample loader, surface and receiving checks did not exist | `panel_surface`, `receive_oos`, C166; the dry run runs the same path |
| 4 | MAJOR | The three-factor model was vacuous on a two-series book | redefined on the eight-zero curve, with what it can detect stated |
| 5 | MAJOR | Nothing frozen, nothing tagged | C165 pins the real construction; committed and tagged |
| 6 | MAJOR | The test-selected variant scaled D15's descriptives | `SAMPLE` primary, the variant secondary and labelled; H5's invariance held by C166 |
| 7 | MAJOR | D22's option 1 is not choice-free | §6 corrected |
| 8 | MINOR | The join aligned end-dates, not intervals | one union complete-case sample, differenced once |
| 9 | MINOR | Six rules collapse on a two-leg book | duplicates merged before PBO and SPA |
| 10 | MINOR | The real fit used four sessions after the construction date | `REAL_FIT` ends on 2014-12-24 |
| 11 | MINOR | H1's size and 97.5% power unpublished; 2,870 counts holidays | §3 |
| 12 | MINOR | DD135's test level and hand-off loosely stated | §3; `run_d15` takes a `D14Result` |
| 13 | MINOR | No guard that the surface starts after the fit | `_after`, C166 |
| 14 | MINOR | "Held" undefined | §2 |
| 15 | MINOR | DSR, GARCH and bandwidth conventions unlabelled | §5.3; the GARCH docstring says variance-targeted, two-step; the bandwidth's unit dependence is Ledoit–Wolf's own and moves the third decimal |
| 16 | MINOR | No rule for an uncomputable window | §4: refused, counted as not above |
| 17 | RECORD | The predictions are not information-blind: the 2015–2025 path is public, and 2020 and 2022 are named because they happened | recorded here. The protocol is clean; the word "predicted" in §5 of the build order is not blindness |

**The reviewer's verdict before the fixes was: not fit to run, the fixes cheap, none needing an
out-of-sample row.** After them: D14 and D15 are fit to run once the owner authorises; D12 is fit to run
now that H6 and H7 can be moved by the read. D22 is not built.

---

## 10. The trigger, prepared and not run

*Written 2026-09-26: checklist item 7. Nothing here has read a row dated after `DEV_END`.*

| | Prepared |
|---|---|
| Extraction | curvecast `3112140`, `scripts/make_deskcraft_oos_panel.py`. GSW's weekday grid from the sealed `feds200628.csv`; every other series one ALFRED read **as of 2025-12-31** over 2015-01-01 → 2025-12-31, which is DD166's rule taken at the source; each series' refused tail named by date; three files, as DEV has three: `panel_daily_oos_<date>.csv`, `panel_daily_admitted_oos_<date>.csv`, `panel_daily_fx_oos_<date>.csv` |
| Its guard | `--extract` refuses, **before any request**, unless `OWNER_AUTHORISATION_the_first_oos_read.md` exists here, names DD37 and carries a date no later than the day: C119's shape, read from curvecast's side, so the script cannot spend the look budget on its own. curvecast's offline tests hold the guard and its order |
| Rehearsal | `--rehearse` runs the same code on DEV as known on 2014-12-31 and compares it with the three committed DEV panels, value for value and blank for blank. It agrees except exactly the record DD173 pins. A network-flagged curvecast gate re-runs it |
| Receiving side | `readers.oos_panel(daily, admitted, fx)` takes paths, refuses a row outside the record rather than filtering it, joins the three on one grid and hands the result to `receive_oos` before any statistic can see it (C170). No module names an out-of-sample file, so C119 stays on its unauthorised branch |

> **DD173 — what the rehearsal found, and why it moves nothing registered.** The committed DEV panel
> carries the five constant-maturity series (`DGS3MO`, `DGS6MO`, `DGS1`, `DGS2`, `DGS10`) from
> **1989-01-03**, not 1988-01-04, because curvecast's `cmt_daily_dev.csv` opens there: 1,250 values
> the panel never carried. And **seven values differ**: at 2008-05-28, 2008-05-29 and 2014-01-14 the
> panel holds a first print that ALFRED shows corrected before `DEV_END` (the 2-year on 2008-05-28 is
> 2.34 there and 2.62 corrected), and at 1994-11-23 and 1998-08-28 a third decimal the as-of read
> does not carry. The rule was right and its source was incomplete. Every other series agrees value
> for value: the eight GSW zeros, the three TIPS yields, the euro, the credit pair and the six H.10
> majors. **No book or fitted object a registered verdict reads touches a `DGS` series**:
> `US_CASH_BOOK` loads on `SVENY02`, `SVENY10`, `SVENY05`, `DFII5` and `DEXUSEU`, the constructed
> book on GSW zeros, D12's three factors on the eight-zero curve. So the DEV panel is not rewritten
> before the read, no pinned number moves, and the record is extracted by the as-of route. A package
> that later fits on a `DGS` series regenerates the DEV panel through that route first. curvecast
> holds the record as an equality: a new difference fails the rehearsal, and so does one of these
> disappearing.

**The read, in order, once the owner has written the authorisation.** Each step is one act, and the
order is the one X13 fixed: the foreclosure is dated before any number is read off the panel.

1. The owner commits `docs/OWNER_AUTHORISATION_the_first_oos_read.md` (DD133): DD37, ~~the four
   readers~~ *the five readers, D21's registration by name beside this one (amended 2026-09-26, DD199:
   D21 reads the record too and registers in its own document)*, this document by name, and a date.
   C119 checks its shape and nothing else can write it.
2. In curvecast, under MEIP's interpreter: `python scripts/make_deskcraft_oos_panel.py --extract`.
   It prints each series' coverage and refused tail, and writes the three files here.
3. In curvecast, one commit: an annotation on the trial ledger's non-look entry dating DD37's firing,
   with the extraction's date and the refused tail. Nothing else rides with it.
4. Here, one commit, DD102's: the three files and the one line in `readers.py` that names them.
   Its message names DD37, the extraction date and the refusal count. No other code, bar or document
   changes in it.
5. The readers run once, on `panel_surface(oos_panel(...))`: `run_d14`, then `run_d15` with D14's
   result, then `run_d12` on `NBER_2020` and `RATES_2022`. Every verdict is scored as §3 to §5 wrote
   it. The landing commit sets this document's status to `**Status: REGISTERED, not landed, for
   D22.**` (DD172), and D12, D14 and D15 land with their verdicts. D22 reads later under §6.1.

*Next free ids: ~~C179 / DD193 / X26~~ ~~C186 / DD199 / X26~~ ~~C192 / DD207 / X26~~ ~~C195 / DD209 / X26~~
~~C195 / DD210 / X26~~ ~~C200 / DD212 / X26~~ (DD210 and DD211 in D21's §12, 2026-09-28) — see §11.*

---

## 11. D22's code, built to §6.1 and rehearsed on DEV, not run

*Written 2026-09-28, before the first out-of-sample read: `docs/OWNER_AUTHORISATION_the_first_oos_read.md`
does not exist, and no row dated after `DEV_END` has been read. Everything above is unchanged, and so
is every rule of §6.1. D17, D18 and D21 exist now, so D22 is built **to** the lock as DD171 requires.
The decisions below fix what the lock left to the code, and none of them re-chooses a rule it wrote.
D22 stays registered and not landed. Its verdicts wait on the owner's authorisation, which must name
it (DD199).*

| | Built |
|---|---|
| Module | `src/deskcraft/funding.py`: the hedge legs, their daily marks, the bought options beside them, the trailing operating cash flow, and the H15 and H16 scorers |
| The read | curvecast `scripts/measure_deskcraft_d22_funding.py`: `--rehearse` on DEV, and `--replay` only under the authorisation |
| The cost row DD205 owed | `costs.CONTRACT_COST_OF["WTI_C2"]` (DD212) |

> **DD212 — DD176's WTI cost row lands in D7a's cost model, before D22 builds, as DD205 owed it.**
>
> 1. **The row.** `ContractCost("WTI_C2")`: a half-spread of **one tick, $0.01 a barrel**, basis
>    `QUOTING_CONVENTION` (CME's contract specification), with its evidence. It is not a
>    `CostProfile` and not in `COST_OF`. A profile is basis points of par in a market with a maturity
>    bucket, and `COST_OF` partitions the committed source register (C87), which WTI is not in: it
>    is results-only.
> 2. **A roll crosses the half-spread twice**, closing the held contract and opening the new one:
>    2 × $0.01 × the frozen barrels. The entry at construction crosses it once, on 2014-12-24, before
>    every window, so it is not on H16's path.
> 3. **The 1× rung is the row as stated.** §6.1 fixes D7a's costs at the 1× rung. `funding.py` does
>    not read `COST_MULTIPLIERS`, so C102's census of ladder readers is unchanged. The only cost on
>    any window's path is the crude rolls, and their total is reported beside each drawdown, so a
>    reader can scale it to any rung.
> 4. **No market depth is graded** (X11's impact term stays ungraded). The path assumes a hedge of any
>    size is held and rolled at one tick. At the sizes §11.2 reports it could not be, so a crude
>    drawdown here is a lower bound on what carrying the position would have cost.

> **DD213 — the hedge D22 replays is D17's stated exposure: every leg, at 100%, sign-flipped and
> frozen.**
>
> 1. **Which legs.** Every row of D17's stated fixture for the firm. H16's case clients are cohort
>    ranks 1, 2 and 3: **GE** (rates, crude), **ExxonMobil** (four currencies, rates, crude) and
>    **AT&T** (rates, $20m). D18 took each client's largest leg for H13. H16 scores the hedge a reader
>    of the 10-K builds at 100% of the disclosed exposure (§6.1), so it takes all of them.
> 2. **The rates leg is D7b's.** `select` on a client's rates target returns `OUT_SVENY01` alone at
>    cosine 1 (C184; D18 §9 item 4), and C201 checks it for every case client, not only GE. Its P&L is
>    D17's convention (DD184): **−s × N × Δy**, with Δy the one-year zero's daily change as a decimal,
>    so a basis point moves a year of interest on the stated debt. DV01 is frozen and the maturity
>    constant (§2).
> 3. **A currency leg is a frozen dollar delta**: **−s × N × Δ ln(USD per unit)**. Each H.10 quote
>    is turned the right way by `panel.FX_QUOTES`. This is D9's convention, a P&L per log move, as
>    `US_CASH_BOOK` holds the euro.
> 4. **The crude leg holds Q = N ÷ the 2014-12-24 contract-2 settle barrels**, frozen through every
>    roll (DD176). Its P&L is **−s × Q × (F_t − F_{t−1}) on one contract's two settles**: contract 2
>    on both on an ordinary session. On the session after contract 1 expires, it is today's
>    contract 1 against yesterday's contract 2, which is the same contract. That session also pays
>    DD212's roll cost. **This is a price change, not a log return.** Full daily variation margin
>    settles a futures position on its price. D17 and D21 read crude as a log return because they fit
>    a dollar exposure, and D22 marks a position.
> 5. **Each leg names what it stands for and what the substitution drops** (DD175, DD179). A rates leg
>    is a swap or a Treasury future carried as the one-year zero, and drops financing, the delivery
>    option, the roll, the futures-cash basis and the swap spread. A currency leg is a forward carried
>    at spot, and drops forward points and the cross-currency basis. A crude leg is NYMEX contract 2
>    itself, and drops the product-over-crude spread where the fact names a refined product.
> 6. **A non-positive held settle** refuses each change whose two settles include it, as DD176 says.
>    **The window that contains a refused change is refused for that client, and counted as not
>    exceeding.** Leaving the change out would impute a zero move, and DD176 says never imputed.

> **DD214 — the path, and its peak drawdown.** Each leg's changes are taken on its own market's
> sessions. The hedge's P&L on a date is the sum of the changes that end on it, so a leg adds nothing
> on a day its market is shut. This is D12's replay of frozen exposures with one difference: D12
> differences the complete cases of one panel, and a crude leg is in no panel. **A change counts
> toward a window iff both of its sessions lie in the window** (DD211's rule), so the path is
> cumulated from the window's first session. **Peak drawdown** is the largest fall of that cumulative
> P&L from its running peak, the peak starting at zero: `effectiveness.worst_fall`, unchanged. The
> margin is §6.1's: full daily variation margin, no threshold, no initial margin, so this path is the
> cash path.

> **DD215 — trailing operating cash flow, by rule.**
>
> 1. **The filing.** The latest filing whose form is exactly `10-K` and whose date is **before the
>    window's first day**. It is found among the firm's `companyfacts` facts of every concept, so a
>    10-K that does not tag operating cash flow is still found and is never skipped over.
>    `companyfacts`' `filed` stands for the acceptance date: it is the date EDGAR assigns, and a
>    filing accepted after 17:30 carries the next business day.
> 2. **The fact.** In that filing, a fact whose duration is 350 to 380 days, the one with the latest
>    end: `NetCashProvidedByUsedInOperatingActivities`, the concept §6.1 names. **If the filing
>    carries no such fact, `NetCashProvidedByUsedInOperatingActivitiesContinuingOperations`**, which is
>    the same line for a filer with nothing discontinued.
> 3. **Why the second concept, and which way it moves H16.** ExxonMobil's FY2013 10-K (accession
>    0000034088-14-000012, filed 2014-02-26) tags its operating cash flow, **$44.914bn**, only under
>    the continuing-operations concept. Its `companyfacts` holds no fact under §6.1's concept from any
>    filing after 2013-02-27. Read strictly, the lock would refuse ExxonMobil, and ExxonMobil's crude
>    leg is what decides H16 (DD218). **So this reading moves H16 toward its predicted PASS, the
>    flattering direction.** It is taken because the lock names operating cash flow by its usual
>    tag, and a tag is not the quantity. The concept each client-window used is reported. Whether it
>    binds on the record is not known: it binds iff ExxonMobil's 10-Ks filed in 2019 and 2021 carry
>    only the continuing-operations concept, and no filing after 2014 has been read.
> 4. **Refusals.** No 10-K before the window, a latest 10-K carrying neither concept, or a value at or
>    below zero: the client-window is refused by name and **counted as not exceeding**, against H16's
>    prediction. An earlier 10-K is never used in place of the latest. The three DEV windows precede
>    every 10-K with XBRL data, so they are refused for this reason and reported in dollars.
> 5. **Read at D22's own read**: one `companyfacts` request per case client under curvecast's D423
>    identity, and every fact filed after 2025-12-31 is dropped on arrival. What leaves is the value,
>    its filing date, its concept and its fiscal year end.

*Answered 2026-09-28 by DD231 (§12): item 3's reading is accepted, and H16 is reported as decided
before the read.*

> **DD216 — the bought options beside, and the number reported next to H16.**
>
> 1. **One option per leg**, §6.1's: bought, European, **at the money on the day it is bought**,
>    struck to pay in the losing direction, on the linear leg's notional. Rates: Bachelier on the
>    one-year yield in percent, N × 0.01 dollars per point. Currency: Garman–Kohlhagen at zero
>    differential in moneyness, on N dollars. Crude: Black-76 in moneyness on Q × that day's
>    contract-2 settle, with DD176's contract 2 standing in for the six-month forward. **The lock's
>    "at-the-money strike on the frozen level" is read as at the money on the level of the day the
>    option is bought, that level then frozen as its strike.** The other reading, every roll struck at
>    the 2014-12-24 level, makes each premium after an adverse move mostly the intrinsic value the
>    expiring option has just paid out. The registered premium outflow would then count the same
>    dollars twice. D21's structures strike at each roll's own level (DD204), and this is that convention.
> 2. **Roll dates** are 2014-12-24 and every six calendar months from it: forwards for the record,
>    and backwards for the DEV windows reported beside it. Each roll happens on the leg's first
>    session on or after its date. An option expires at the next roll date, settles at intrinsic on
>    that session, and is replaced there. Its tenor is the calendar days to expiry over 365, and it
>    is **marked daily at model value** at that day's volatility.
> 3. **Volatility** follows §6.1's ordered list with DD210's mapping: the Fed's release no more than
>    ten days old where the leg maps, and otherwise D8's EWMA (λ 0.94, normalised weights) over every
>    daily change of the leg's factor through that day, annualised on 252 sessions. For rates the
>    factor is the yield in percent; for currencies and crude it is a log return. Crude's is contract
>    2's roll-aware log return, and the option's forward follows it, so a roll moves no option.
> 4. **The registered number** is the option hedge's peak cumulative premium outflow: the premiums
>    paid for purchases inside the window, cumulated from the window's first session. No premium is
>    negative, so the peak is the total. **`NBER_2020` holds no roll date** (the rolls fall on
>    2019-12-24 and 2020-06-24), so this number is **zero by the calendar** for every client, stated
>    before the read. `RATES_2022` holds two: the sessions on or after 2022-06-24 and 2022-12-24.
> 5. **Added beside it here: the option book's own worst fall** inside the window, its marks net of
>    premiums paid and payoffs received. The linear hedge's drawdown and the option hedge's can then
>    be read side by side. A bought option cannot lose more than was paid for it, and that bound is
>    the whole comparison. No verdict reads either number.

> **DD217 — the scorers.**
>
> 1. **H16**, over the three case clients in `NBER_2020` and `RATES_2022`. A client-window
>    **counts iff its peak drawdown exceeds 25% of its trailing operating cash flow**, and **H16
>    passes iff at least one counts**. A refused client-window counts as not exceeding, and the verdict
>    is `NOT_PERFORMED` only when all six are refused. The three DEV windows are reported beside and
>    never scored (§6.1).
> 2. **H15 is refused by name** (DD180) and carries `NOT_PERFORMED` with DD180's reason. Its rule is
>    written as a scorer anyway, `funding.h15`, on each firm's unconditional and conditional
>    effectiveness, so that what the lock fixed is executable and tested. Nothing feeds it.

> **DD218 — what H16 can show, computed before the read** (X15, X16). The numbers are §11.1's.
> H16 is an existence claim over six client-windows, and one of them is close to certain before any
> row is read. ExxonMobil's stated crude purchases are **$244.156bn**, 5.4 times its FY2013 operating
> cash flow. A 100% hedge of them crosses a quarter of that cash flow on an adverse move of
> **4.6% of the price**, from any running peak, inside either window. So **what H16 can say is
> narrower than its wording, as H13's was**: the Metallgesellschaft mechanism it names is real, and
> this cohort tests it through the size of one firm's stated exposure, not through the crisis. It is
> scored as written and not withdrawn (H4b's and H13's precedent). The paper reports §11.1's
> probabilities beside the verdict, and GE's and AT&T's results as the part of the claim the record
> can move.

> **DD219 — D22's place in the read.** At §10 step 5, after Paper 1's three readers:
> `measure_deskcraft_d22_funding.py --replay`. **It refuses before any request** unless the
> authorisation exists, names DD37 **and D22**, and carries a date no later than the day. It reads the
> one extraction's panels by path, EIA's two contracts, the Fed's file (D21's, read once and shared)
> and three `companyfacts`. It writes `d22_funding_oos_<date>.csv`, statistics only: never a price,
> never a settle, never a quantity of barrels. `funding.load_funding` reads the file and `funding.h16`
> scores it. D22 lands in the commit that records its verdicts, and this document's status line then
> drops its marker.

### 11.1 What H16 can show, and the rehearsal

*Computed 2026-09-28 from construction-date inputs only: D17's stated fixture, each client's FY2013
10-K, and EWMA volatility through 2014-12-24. Crude's volatility is a statistic of EIA's
results-only route, and no settle is written here.*

**DD218's table.** Each case client's hedge at 100% of its stated legs. Each leg's factor is a
driftless Gaussian path at its EWMA volatility on 2014-12-24: `SVENY01` 0.2693% a year, the euro
8.84%, sterling 6.17%, the Canadian dollar 6.98%, the yen 11.30%, crude **48.9%**. The legs are
independent. The window lengths are about `NBER_2020`'s 61 daily changes and `RATES_2022`'s 250.
The threshold is 25% of the FY2013 operating cash flow, the one trailing at construction:
`funding.crossing_probability`, 20,000 paths, seed 20260928.

| Case client | Stated legs, total | FY2013 cash flow | Notional ÷ cash flow | P(cross), 61 changes | P(cross), 250 changes | Six-month ATM premium, all legs |
|---|---|---|---|---|---|---|
| GE | rates, crude: $94.865bn | $28.579bn | 3.3 | 0.1169 | 0.6904 | $2.385bn, 8.3% of cash flow |
| ExxonMobil | four currencies, rates, crude: $402.707bn | $44.914bn | 9.0 | **1.0000** | **1.0000** | $36.625bn, **81.5%** of cash flow |
| AT&T | rates: $20m | $34.796bn | 0.0006 | 0 | 0 | $0.0bn |

- **ExxonMobil decides H16 before any row is read.** At crude's **lowest** EWMA volatility anywhere
  in DEV (9.87%, on 2014-07-08; the median is 29.2%), its crude leg alone crosses in **55.2%** of
  61-change paths and **98.3%** of 250-change paths (C207 holds both from committed inputs).
- **Without ExxonMobil**, H16 rests on GE, which crosses in about **0.727** of pairs of windows,
  treating the two windows as independent. That is the difference DD215 item 3's reading makes, and
  why its direction is stated.
- **AT&T cannot count.** Its stated rates exposure is $20m against a threshold of $8.7bn.
- **The option hedge beside the linear one costs four-fifths of ExxonMobil's annual cash flow every
  six months** at the construction date's volatility. A bought option's loss is bounded by its
  premium, and here the premium is itself the size of a funding event.

**The rehearsal**, curvecast `measure_deskcraft_d22_funding.py --rehearse`, on the three DEV
windows, beside and never scored. Three SEC requests on the first run, none after. The kept facts'
latest filing date is 2014-11-10. A second run, offline, printed every number the first did.

| Client, window | Legs marked | Peak drawdown | Crude rolls, cost | Option premium in window | Option book's worst fall |
|---|---|---|---|---|---|
| GE, `NBER_1990` | 2 | $7.962bn | 9, $54.35m | $1.431bn | $2.443bn |
| GE, `NBER_2001` | 2 | $2.139bn | 9, $54.35m | $0.820bn | $0.910bn |
| GE, `NBER_2007` | 2 | $18.866bn | 19, $114.74m | $13.062bn | $4.905bn |
| ExxonMobil, `NBER_1990` | **5** | $74.386bn | 9, $781.72m | $19.968bn | $62.105bn |
| ExxonMobil, `NBER_2001` | 6 | $56.978bn | 9, $781.72m | $13.043bn | $26.237bn |
| ExxonMobil, `NBER_2007` | 6 | **$464.112bn** | 19, $1,650.29m | $196.075bn | $80.100bn |
| AT&T, all three | 1 | ≤ $0.001bn | none | $0.000bn | $0.000bn |

1. **Every DEV window is refused for H16's comparison**, as DD215 item 4 says: no case client filed a
   10-K with XBRL data before 2009. The dollars are reported, and the comparison is not.
2. **The cash-flow rule reads each client's FY2013 10-K at construction exactly**: GE $28.579bn and
   AT&T $34.796bn under §6.1's concept, and ExxonMobil $44.914bn under the continuing-operations
   concept. That is DD215 item 3 happening on DEV.
3. **ExxonMobil's euro leg is not marked in 1990**, because `DEXUSEU` opens in 1999. `legs_marked` says
   so (5 of 6), rather than a silent gap.
4. **Crude rolled 360 times in 7,158 sessions** (1985–2014), twelve a year, and **no DEV change is
   refused**: contract 2 never settled at or below zero before construction.
5. **In 2007–09 ExxonMobil's 100% crude hedge fell $464bn from its peak**, about ten times its FY2013
   cash flow, as crude rose into mid-2008 and collapsed. The option book beside it fell $80bn after
   $196bn of premium. That is the mechanism H16 names, on a window the lock keeps out of the verdict.
6. **At this size the roll costs are real and the depth is not.** ExxonMobil's rolls cost about
   $87m each at one tick, and nothing graded says the market could have carried the position
   (DD212 item 4).

**Predictions, scored when D22 lands.**

| # | Prediction |
|---|---|
| D22-P1 | **H16 PASS**, as registered, with ExxonMobil counting in both verdict windows |
| D22-P2 | GE counts in `RATES_2022` (0.69 under DD218's null) |
| D22-P3 | DD215 item 3's second concept is the one read for ExxonMobil in both verdict windows: its 2019 and 2021 10-Ks tag operating cash flow as its 2014 one did |
| D22-P4 | In both verdict windows, ExxonMobil's option book falls less than its linear hedge, as in all three DEV windows |

*Next free ids: **C208 / DD220 / X26**.*

---

## 12. The owner's decisions before the read, 2026-09-28

*Written 2026-09-28, before the first out-of-sample read: `docs/OWNER_AUTHORISATION_the_first_oos_read.md`
does not exist, and no row dated after `DEV_END` has been read. Nothing above this section changes.*

Four places in the record left a decision to the owner and said what followed if it went
unanswered: D21's DD206, D17's DD208, DD215 item 3 here, and the admission's §7. They were put to
the owner as one list of recommendations, with three more items, and the owner answered the list
as a whole, recorded from the reply: *"complete all of these itrems in the way you suggested and in
the order that is most optimal and commplete it end to end"*.

| Recommendation put to the owner (summarised) | Recorded as |
|---|---|
| Accept DD215 item 3's reading of ExxonMobil's cash flow, and report H16 as decided before the read | DD231 |
| Keep H12a, H14a and H14b as written, H14a labelled as a claim that could not fail in practice | DD232 |
| Keep D17's fixture as run, and correct `_read_dei` only after the read and only for a later cohort | DD233 |
| Confirm the Minneapolis Fed's extension to D21 | DD234 |
| Record the listing that was counted when the rule said drop | DD235 |
| Do not send the request to DTCC | DD236 |
| Deposit the registration with a third party before the authorisation, the upload being the owner's | DD237 |
| The authorisation is the owner's alone, written after all of the above | unchanged: DD133, §10 step 1 |

The reply was an instruction, not an answer to each question, as the admission's §7 item 1 says of
its own. So each row is recorded as the recommendation it accepted, and **the owner is told so and
may say otherwise** until the authorisation is written. From then on nothing here moves.

> **DD231 — DD215 item 3's reading is accepted.** Where a 10-K carries no fact under §6.1's concept,
> operating cash flow is read under `NetCashProvidedByUsedInOperatingActivitiesContinuingOperations`,
> as DD215 item 3 wrote. The reading was put to the owner as the direction that flatters H16: refused,
> ExxonMobil would be refused in both verdict windows and H16 would rest on GE, at about 0.727 under
> DD218's null. Accepted, **H16 is reported as decided before the read** (DD218). ExxonMobil's hedge
> crosses a quarter of its cash flow on an adverse move of 4.6% of the price and crosses with
> probability 1.0000 in both windows. The paper reports GE's and AT&T's results as the part of the
> claim the record can move, and the concept each client-window used beside the verdict.

> **DD232 — DD206 is answered: H12a, H14a and H14b stay as registered, and so does H16.** None is
> withdrawn before the read. Each keeps its wording, its predicted PASS and its scorer (A1 §5.5, and
> the precedent of H4b and H13: a claim is not withdrawn at the package that scores it). What the
> paper states beside each verdict is fixed here, from numbers that exist before the read:
>
> 1. **H14a is reported as a claim the record could not fail in practice.** Every in-sample R² D17
>    measured is below 0.40, with a median of 0.016 and 23 of 32 under 0.05 (D17 §14.4). D21's §6 puts
>    the in-sample R² below one half with probability one at every true R² below 0.3. So a pass says
>    *there is no clean hedge*, never *the hedge decayed* (D21 §6 item 1). Paper 1 says H4b could not
>    fail for any book. H14a could fail only if firms whose hedges removed less than 0.40 of their
>    equity variance in sample removed half of it out of sample, and the label says that difference.
> 2. **H14b is reported as carried by noise on the rates-only firms.** Under no decay at all D21's §6
>    item 2 puts it at two-fifths to three-fifths of the firms. The resolved subset (DD203 item 4) is
>    reported beside it as the place where it means what it says.
> 3. **H12a** keeps DD206's reading of its missing prevalence as the median. On the resolved firms
>    it is near-complementary to H14b (D21 §6 item 4), and the paper reports that.
> 4. **H16** is DD231's.

> **DD233 — DD208 is answered: D17's fixture stays as run, and nothing is re-run beside it.** DD208
> left one question: whether to re-run the extractor with `_read_dei` corrected and report both. The
> answer is no, before the read and at it. D21's replay computes MV_T with D17's function as run,
> because Ederington effectiveness is scale-free only when the fit and the replay share MV_T
> (DD208, DD202). Correcting `_read_dei` before D21 reads would break the one property the replay rests
> on. The paper reports DD208's table as found. A corrected `_read_dei` may be written after the read,
> for a cohort drawn after it, and it is never applied to D17's fixture or to D21's replay.

> **DD234 — the Minneapolis Fed's route is extended to D21, confirmed.** The admission's §7 recorded
> the extension from an instruction and said the owner may say otherwise. The owner accepted the
> recommendation to confirm it, and with it §7 item 2's application of drop-on-arrival to the Fed's
> file. D21's DD210 runs at D21's own read on the terms of the admission's §1: never committed,
> statistics only, and every row after 2025-12-31 and every market DD210 does not map dropped before
> anything is kept.

> **DD235 — a listing was counted before it was dropped, and it moves nothing.** On 2026-09-26, while
> checking Alpha Vantage's documented example URLs for D17, curvecast's
> `measure_deskcraft_d17_exposure.py` fetched `function=LISTING_STATUS` with the public `demo` key and
> **no date**, which returns the listing as of the day asked. `truncate_listing` parsed it and its
> count, **14,483**, was printed before the text was deleted. The admission's §6 rule drops such rows
> on arrival, before anything is computed, and a count is a computation. Nothing was written or kept.
> It moves nothing. The listing holds no price and no return. D17's cohort was drawn from the dated
> call, `date=2014-12-24`. No reader reads a listing, so this was not the first read DD37 guards, and
> the non-look entry is untouched. The dated example beside it, `date=2014-07-10&state=delisted`,
> returned 429 rows.

> **DD236 — the DTCC request is not sent.** DD177 left asking DTCC's support desk for reports older
> than 366 days to the owner. It is not asked: a report sent on request is not a published route and
> its terms are unread, and the term it would measure is one DD175 already names as dropped. DD175's
> `"swap spread"` stays unmodelled, as each leg carrying it says.

> **DD237 — a dated deposit outside this machine, before the authorisation.** A registration that
> exists only in a repository on the owner's machine can be dated by nobody else. So before writing the
> authorisation the owner deposits a bundle with a third party that timestamps it: an OSF
> registration under embargo, or Zenodo. The bundle is prepared from the commit that carries this
> section:
>
> 1. **deskcraft:** `git archive` of that commit **without
>    `tests/fixtures/panel_daily_admitted_dev_20260925.csv`**, the one file carrying Moody's bytes
>    (`NOT_SENDABLE.md`, DD140). That file is pinned by its blob hash, beside `git ls-tree -r` of the
>    commit and the commit object, so every hash from each file up to the commit can still be checked.
> 2. **curvecast:** `git archive HEAD`, accepted by `scripts/check_data_rights.py --archive`
>    (WP-L1 §4).
> 3. **A manifest:** each archive's sha256, both commit objects, both tree listings, and the excluded
>    blob's hash.
>
> A copy is never a clone or a `git bundle`, because both carry history, and both repositories'
> histories carry restricted bytes. If the owner would rather send no bytes at all, the manifest alone
> is the deposit: it fixes the same commits, and the archives can be rebuilt from them later. **The
> upload is the owner's act**, as the authorisation is. No bar can see an upload, so none is claimed,
> and C119 does not require one. The authorisation may cite the deposit's identifier.

Bar **C219** holds this section: each decision, the owner's words, and a line at each of the four
places a question was asked, after the decision it answers.

*Next free ids: ~~**C220 / DD238 / X27**~~ — see §13.*

---

## 13. The read, 2026-09-28

*Written after the read. The owner's authorisation is `cf84e97` (DD133). curvecast `fc2e97f` dates
DD37's firing on its trial ledger, and the record landed at `2acbd39` (DD102). The readers ran once,
at 10:53 UTC, in §10 step 5's order: `run_d14`, then `run_d15` with D14's result, then `run_d12`.
Each verdict below is scored by the rule §3 to §5 wrote. Nothing above this section changes.*

### 13.1 The record

curvecast's `make_deskcraft_oos_panel.py --extract` ran from 10:42:37 to 10:43:09 UTC. It produced
**2,870 weekday sessions**, 2015-01-01 → 2025-12-31, with every series as ALFRED knew it on
2025-12-31 (DD166). `receive_oos` accepted the record: every date lies inside `OosWindow.whole()`,
the grid is exactly GSW's weekdays, and all 25 series are present. **31 observations were refused**
as first published after 2025-12-31: 2025-12-31 on the eight Treasury series and on `BAA10Y` and
`AAA10Y`, and 2025-12-29 to 2025-12-31 on `DEXUSEU` and each of the six H.10 majors.

D14's and D15's samples are the sessions on which every series their books hold has a value:
**2,736**, from 2015-01-05 to 2025-12-26. They end on 2025-12-26 because the refused tail takes the
euro's last three sessions. §3 published Kupiec's power at 2,760 sessions. At 2,736 it is **0.647 /
0.990 / 1.000** at 99% against true rates of 1.5% / 2% / 3%, and **0.960 / 1.000 / 1.000** at 97.5%
against 3.75% / 5% / 7.5%.

> **DD238 — a replay window of the record is its own sessions, differenced inside the window.**
> §4 replays each window *"on its own realised correlations"*. In the dry run D12 received a DEV
> window through `dev_surface`, which loads that window's rows and nothing else. The record arrives
> as one panel, so the same restriction is `readers.window_surface(panel, window)`: the sessions
> inside the window, differenced there, so that the first change is the window's second session
> less its first. It is written after the read, because the read was the first time a window's rows
> came from a panel holding more than the window. It is the only reading §4 has on such a panel,
> and it moves no rule. C220 re-runs the read through it and reproduces every number below.

### 13.2 D14 — the risk-model backtest

`US_CASH_BOOK`, held from 2014-12-24, over 2,736 sessions.

| Variant | 97.5%: exceptions / expected, Kupiec p | 99% | independence p, 97.5% / 99% | Z1 p | Z2 p | mean FZ0 |
|---|---|---|---|---|---|---|
| `SAMPLE` (primary) | 58 / 68.4, **0.191** | 34 / 27.4, **0.219** | **0.0013** / 0.073 | 0.000 | **0.538** | 14.595 |
| `LEDOIT_WOLF` | 58 / 68.4, 0.191 | 34 / 27.4, 0.219 | 0.0013 / 0.073 | 0.000 | 0.527 | 14.595 |
| `EWMA` | 70 / 68.4, 0.845 | 35 / 27.4, 0.159 | 0.142 / 0.082 | 0.000 | 0.143 | 14.384 |
| `CRISIS` (2007–09) | 18 / 68.4, 0.000 | 8 / 27.4, 0.000 | 0.005 / 0.016 | 0.021 | 1.000 | 14.787 |

> **H1 — PASS, as predicted.** On the primary, Kupiec's p is 0.191 at 97.5% and 0.219 at 99%, and
> the p of Acerbi–Székely Z2 is 0.538. All three are at or above 0.05, which is DD163's conjunction.
> Beside it, as §3 requires: a correctly specified model fails this conjunction about 11.5% of the
> time. The primary takes fewer exceptions than expected at 97.5% and more at 99%, which is the
> shape of a tail fatter than the Gaussian, and Z1 rejects at p 0.000. Neither is part of H1's rule.

> **H2 — FAIL, as predicted.** Christoffersen's independence test at 97.5% on the primary has p
> 0.0013: the exceptions cluster. At 99% the p is 0.073.

The Basel traffic light at 99% runs over ten non-overlapping blocks of 250 sessions. The primary is
green in seven of them, **yellow** in the blocks opening 2020-01-10 and 2022-01-13, and **red** in
the block from 2023-01-17 to 2024-01-16. `EWMA` is yellow in three blocks and red in none. `CRISIS`
is green in all ten, because it is too conservative by a factor of almost four.

**DD135's rule evaluates to `EWMA`.** Its mean FZ0 is 0.211 below the primary's, with a two-sided
Diebold–Mariano p of 1.5 × 10⁻⁸. `LEDOIT_WOLF` cannot be told apart from the primary (p 0.92), and
`CRISIS` is worse (p 2.7 × 10⁻⁶). So D15's secondary descriptives use `EWMA`, labelled as selected
on the record.

### 13.3 D15 — the construction backtest

The constructed book is C165's: `out_sveny30_short` and `spr_sveny10_sveny30_short`, constructed
2014-12-24 and held, over 2,736 shared sessions.

| ES-constrained against | Sharpe difference | s.e. | p | 95% bootstrap | minimum detectable |
|---|---|---|---|---|---|
| 1/N | −0.012 | 0.055 | 0.82 | (−0.102, +0.076) | 0.154 |
| single instrument | −0.014 | 0.129 | 0.91 | (−0.230, +0.208) | 0.360 |
| hand-built | +0.013 | 0.208 | 0.95 | (−0.347, +0.368) | 0.582 |

The annualised Sharpe ratios are on rate-change and spot P&L only (§2): ES-constrained **0.221**,
1/N 0.234, single instrument 0.236, hand-built 0.208. The Deflated Sharpe of the ES-constrained book
on 7,836 trials is **0.017**.

> **H5 — FAIL, as predicted, and by §5.2's grammar it says nothing.** Against 1/N the difference
> is negative with p 0.82. That is §5.2's row *"FAIL, difference negative with p ≥ 0.05"*: the
> test's power at the plausible effect was 8% on DEV, and on the record's own standard error it is
> 0.112.

The separating statistics carry no verdict. The weight distance is **0.060**, the ex-ante ES of the
difference is **0.28** of the budget, the realised correlation is **0.981** and the view ratio is
1.0398. Under `SAMPLE`, PBO is 0.69 and the SPA p is 1.00, with equal risk contribution merged into
maximum diversification (weight shares equal within 1e-6). Under `EWMA`, which was selected on the
record, the ex-ante ES of the difference is 0.12 of the budget, the view ratio 1.0417, PBO 0.63 and
the SPA p 1.00.

**G, realised view per unit of realised ES** (§5.5), carries no verdict. It is **+0.068**, with
s.e. 0.023, p 0.0034 and a 95% bootstrap interval of (+0.023, +0.113), against G\* = 0.039 at
power 0.39. **H18 was not registered** (DD170), so G is not scored. Had H18 been registered, it
would have passed, as the DEV split's G would have. §5.5 read the DEV split as a test with under
half the power it needed passing once, and the same reading holds here. G is reported, and no claim
is made from it.

### 13.4 D12 — the scenario engine

The constructed book, at min-variance weights and unit gross DV01, is replayed through the five
windows. The three DEV windows reproduce C165.

| Window | days | sizing change | realised | three-factor 97.5% | FHS 97.5% | understated |
|---|---|---|---|---|---|---|
| NBER_1990 (DEV) | 184 | 0.007 | −1.55m | 12.96m | 13.87m | no |
| NBER_2001 (DEV) | 187 | 0.214 | +0.64m | 13.06m | 13.87m | no |
| NBER_2007 (DEV) | 394 | 0.040 | −0.92m | 18.96m | 20.74m | no |
| **NBER_2020** | 61 | **0.658** | −6.11m | 7.46m | 8.02m | **no** |
| **RATES_2022** | 248 | **0.027** | +15.54m | 15.04m | 15.74m | **yes** |

> **H6 — FAIL, against the prediction.** Sizing moves 65.8% of gross under 2020's correlations and
> 2.7% under 2022's. H6 passes only if both are above 20% (DD167).

> **H7 — FAIL, against the prediction.** 2022's realised P&L is 3.3% above the three-factor
> quantile, and 2020's is 82% of it. H7 passes only if both are above (DD167). FHS, beside, covers
> both windows.

**DD167's change moved neither verdict.** Over all five windows H6 would be 2 of 5 and H7 1 of 5,
which the first version's 3-of-5 rule also scores as not passing. The strict rule was taken before
the read, in the direction that removed in-sample evidence against both predictions (§4). The
record did not need that evidence to refute them.

> **`SCENARIO_SIGNS` — reported.** `US_CASH_BOOK`'s realised leg signs in NBER_2020 are `us_2y` −,
> `us_10y` −, `us_breakeven_5y` −, `eurusd` +. In RATES_2022 they are `us_2y` +, `us_10y` +,
> `us_breakeven_5y` −, `eurusd` +. In 2007–09 they were −, −, −, +. No window is classified into
> the source's four scenarios, because that classification is where the under-determination lives
> (DD153).

### 13.5 The verdicts

| Claim | Predicted | Verdict |
|---|---|---|
| H1 | PASS | **PASS** |
| H2 | FAIL | **FAIL** |
| H5 | FAIL | **FAIL** |
| H6 | PASS | **FAIL** |
| H7 | PASS | **FAIL** |
| `SCENARIO_SIGNS` | none | **REPORTED** |

Three of the five predictions held and two did not. H2 and H5 were predicted failures, and H5's is
uninformative by construction. H1's pass carries its 11.5% size. Both misses are D12's. In 2020 the
window's correlations moved the sizing by two-thirds of gross, but the book's loss stayed inside the
Gaussian quantile. In 2022 the size of the book's P&L, a gain, since the book is short duration
and rates rose, exceeded the quantile, but the correlations barely moved the sizing. Each
prediction held in one window and needed both. *(Corrected in D16's landing commit: this
paragraph first called 2022's P&L a loss. No number moved.)*

### 13.6 What lands

> **DD239 — a status is a line of its own, not a quotation.** DD161 counts a pre-commit as
> registered if it *carries the line* that is its marker. The test that implemented DD161 looked for
> the marker's text anywhere, and §0 of this document quotes the full marker inside a sentence.
> Under that test, no status line could ever have landed D12, D14 and D15. The landing commit found
> this by reading `registered_in` before changing the status line: with the old test, `closed()`
> would still have counted none of the three. `registered_in` now
> reads only lines that are a marker and nothing else, whether full or partial (DD172). No
> registered text is edited. C158 plants a quotation beside a landed status line and holds that the
> quotation registers nothing.

- This document's status becomes `**Status: REGISTERED, not landed, for D22.**` (DD172). **D12, D14
  and D15 land with their verdicts.** D22 reads later, under §6.1 and §11.
- **X13 and X14 close.** Their discharges are in §1 and §5.3, and each became binding when its
  package landed.
- **CP-1** is tagged at this commit, with its one-page write-up,
  `docs/CP1_the_engine_runs_end_to_end.md` (`AMENDMENT_A1` §7.1).
- Bar **C220** re-runs the read and holds every verdict and the numbers each rests on. C97, C128,
  C158 and C170 move to their after-the-read branches: the trigger was pulled once, by the owner's
  authorisation, and by the record's three files only.
- The admitted credit pair now sits in two files, the DEV one and the record's, and
  `NOT_SENDABLE.md` names both.
- D16's C214 and C218 hold the paper's claims table and tally as they stood before the read. They
  go red at this commit, as D16's registration intends, and move when D16 lands on these verdicts.

*Next free ids: ~~**C221 / DD240 / X27**~~ — see §14.*

---

## 14. D22's read, 2026-09-28

*Written after D22's read, under §6.1 and §11 and against the same record. curvecast's
`measure_deskcraft_d22_funding.py --replay` read the record's rates and H.10 panels by path, EIA's
two WTI contracts and three `companyfacts`, with every fact filed after 2025-12-31 dropped on
arrival. It made three SEC requests and wrote `d22_funding_oos_20260928.csv`: statistics only, no
price, settle or barrel count (DD219). Nothing above this section changes.*

### 14.1 The two verdict windows

| Case client | Window | Peak drawdown of the hedge | Operating cash flow read (10-K filed) | Ratio | Exceeds 25% |
|---|---|---|---|---|---|
| GE | NBER_2020 | 2.639bn | 4.246bn (FY2018, 2019-02-26) | 62.14% | yes |
| GE | RATES_2022 | 14.540bn | 3.597bn (FY2020, 2021-02-12) | 404.21% | yes |
| ExxonMobil | NBER_2020 | 194.900bn | 36.014bn (FY2018, 2019-02-27) | 541.18% | yes |
| ExxonMobil | RATES_2022 | 175.363bn | 14.668bn (FY2020, 2021-02-24) | 1,195.55% | yes |
| AT&T | NBER_2020 | 0.000bn | 43.602bn (FY2018, 2019-02-20) | 0.00% | no |
| AT&T | RATES_2022 | 0.000bn | 43.130bn (FY2020, 2021-02-25) | 0.00% | no |

> **H16 — PASS, as predicted, and as reported before the read.** Four of the six client-windows
> exceed a quarter of trailing operating cash flow, where one was enough: H16 is an existence
> claim. DD231 recorded it as decided before the read, and it was. ExxonMobil's hedge alone would
> have passed it in either window. AT&T's stated exposure is $20m, which cannot cross its threshold
> at any volatility on the ladder (DD218).

> **H15 — NOT PERFORMED, refused by name (DD180).** The admitted daily equity route serves only
> the last 100 sessions, so no daily return reaches the two years ending 2014-12-24.

The bought six-month options beside the linear hedge fell less than it in every client-window
that has a leg: GE 1.984bn and 4.264bn against 2.639bn and 14.540bn, and ExxonMobil 16.258bn and
120.443bn against 194.900bn and 175.363bn. They paid for it in premium. `NBER_2020` holds no roll
date, so no premium falls inside it. In `RATES_2022` GE paid 6.627bn and ExxonMobil 96.229bn. The
three DEV windows are reported in the file beside the verdicts and are never scored. No case
client has a 10-K in `companyfacts` filed before any of them opens, so each is refused for cash
flow.

### 14.2 D22's predictions

| | Prediction | Outcome |
|---|---|---|
| D22-P1 | H16 PASS, with ExxonMobil counting in both verdict windows | **HELD**: 541.18% and 1,195.55% |
| D22-P2 | GE counts in `RATES_2022` | **HELD**: 404.21%, and in `NBER_2020` too, at 62.14% |
| D22-P3 | DD215 item 3's second concept is the one read for ExxonMobil in both verdict windows | **WRONG.** ExxonMobil's FY2018 and FY2020 10-Ks tag operating cash flow under §6.1's own concept, `NetCashProvidedByUsedInOperatingActivities`. The fallback DD231 accepted, the direction that flatters H16, was read only at the construction date, and it moved no verdict-window figure |
| D22-P4 | In both verdict windows, ExxonMobil's option book falls less than its linear hedge | **HELD**: 16.258bn against 194.900bn, and 120.443bn against 175.363bn |

### 14.3 Two numbers not performed, and two defects the read found

**DD216's implied volatility is not performed, by name.** The Minneapolis Fed's statistics file
arrived as a 2.78 MB CSV that opens with three lines of preamble, two sentences and a blank,
before its header row, `"market","idt","maturity_target","mu","sd",...`. The rule DD210 wrote
reads the first line as the header, so it found no date column. DD210 fixes that outcome: a file
the rule cannot read leaves the number not performed, and nothing falls back silently. So every
row carries the EWMA basis, and D21's DD210 comparison is not performed for the same reason. The
reader is not corrected after the read. Whether to run the comparison later, with a reader that
skips the preamble and is labelled as written after the read, is the owner's decision. It carries
no verdict either way. *(Decided 2026-09-29: run, under DD243, D21's §14, whose §14.2 reports D22's numbers beside H16 and
D22-P4 read again on them. No verdict moves.)*

> **DD240 — a result file of the record opens with the date it was read to.** D21's writer puts
> `oos_end_date` first *"so deskcraft's C119 reads the file as what it is"*. D22's did not, and
> C119 and C97 find a fixture's date by its first date-named column. On the first file they raised
> `StopIteration` rather than a verdict, which failed closed but told nobody why. `funding.COLUMNS`
> now opens with `oos_end_date`, and curvecast's writer passes the panel's end date. **D22 was run
> again on the same cached inputs**, with no SEC request, and every one of the 15 rows reproduced
> the first file cell for cell apart from the new column. C97's after-the-read branch admits the
> readers' result files beside the record's three, each named `_oos_`.

**curvecast's three guards could not be tested once the authorisation existed.** Each script's
`authorised()` took `AUTHORISATION` as a default argument, so it was bound when the module loaded.
The tests that replace it with an absent file therefore replaced nothing. They had passed only
because the real file was absent. D22's C544 went red today on exactly that. The path is now
resolved when the guard is called, in the extraction's, D21's and D22's scripts, and all three
refusal tests pass with the real authorisation present. No guard became weaker.

### 14.4 What lands

- This document's status becomes `**Status: LANDED 2026-09-28.**` All four packages it registers
  have read the record: D12, D14 and D15 in §13, and D22 here. C158's declared set loses it.
- `CLAIMS` holds **H16 PASS** and **H15 NOT_PERFORMED**. Bar **C221** holds the file, the six
  ratios, both verdicts and the register together.
- D21 reads next under its own registration. Its Alpha Vantage requests stopped at the free daily
  cap of 25, with 25 of 35 weekly series kept. The other ten are read once the cap resets, and
  nothing is written until all 35 are in.

*Next free ids: **C222 / DD241 / X27**.*
