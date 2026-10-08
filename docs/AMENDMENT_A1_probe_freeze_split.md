# Amendment A1 — the probe goes first, the plan freezes, and three bars are rewritten

Amends `BUILD_ORDER_D3_D16.md` (the running order and the hypothesis register) and
`RESEARCH_client_solutions_layer.md` §10. Written 2026-09-08, after D2 closed at `4057cd5`
and four consecutive doc-only commits landed on top of it.

**One-line summary.** The riskiest component in the plan is currently seventeenth of
twenty-two; a feasibility probe moves to first, the exposure read stops being a regression and
becomes arithmetic on disclosed units, three pre-registered bars are rewritten because one of
them is provably vacuous, and the package list is frozen with a build failure enforcing it.

**Ground rule for this amendment: it adds no net packages.** The pathology it responds to is a
plan that grew from 14 packages to 22 while the build grew by zero. An amendment that answers
that by adding four more packages is the disease wearing the cure's clothes. Net movement is
**22 core packages → 21**: one added, two moved to an annex that may not be built until the
core closes.

---

## 0. Measured before decided

Everything in this section was computed or read today, before any of §1's verdicts were
written. Reproduce with the scripts named.

| # | Finding | How |
|---|---|---|
| **M11** | **The last line of source in this repo was written 2026-09-05.** Since then: four commits, `2a11d91` / `1df27cc` / `b3878fc` / `4f98e00`, **782 inserted lines, all documentation, zero source, zero tests.** Two code packages in the repo's nine-day life; four doc commits in the three days since | `git show --stat` on each |
| **M12** | **H14's two-clause conjunction is not a conjunction. Clause (a) is implied by clause (b), unconditionally.** H14 requires OOS R² < 0.5 **and** OOS R² < ½ × in-sample R². Since in-sample R² ≤ 1 by definition, ½ × in-sample R² ≤ 0.5, so the second clause strictly implies the first. **Clause (a) can never bind.** The bar advertises a strictness it does not have | Algebra; confirmed numerically in M13, where P(both) equals P(decay clause) to three decimals in all fifteen cells |
| **M13** | **The decay clause's false-positive rate under a null of no true decay** — two independent samples, identical true R². At daily frequency (n ≥ 630 per half) it is **0.000**. At quarterly frequency it is material but not fatal: **16.2%** at true R² 0.30 and n = 30 per half, **8.0%** at n = 60, **1.1%** at true R² 0.50 and n = 60 | `scratchpad/r2_power.py`, 40,000 reps, seed 20260908 |
| **M14** | **The level clause discriminates well even on quarterly data, which is the opposite of the expected concern.** At n = 60 a firm whose true R² is 0.30 reads below 0.5 with probability **0.976**; one whose true R² is 0.70 reads below 0.5 with probability **0.006**. The 95% sampling interval for a true R² of 0.50 at n = 60 is **[0.311, 0.667]** | same |
| **M15** | **The cohort bar and the cohort claim are different statements, and the plan conflates them.** At n = 40, an outcome of exactly 28/40 — the bar's own threshold — carries an exact 95% Clopper–Pearson interval of **[0.535, 0.834]**, width 0.300. **34/40 (85%) is the smallest count whose interval excludes 0.70.** A 70% point estimate first excludes 50% at n = 25 | `scratchpad/cp.py` |
| **M16** | **Whether EDGAR's `companyfacts` API returns dimensional facts is UNVERIFIED.** Revenue by geographic area is tagged against `srt:StatementGeographicalAxis`; `companyfacts` is documented as serving reported facts and is widely observed to carry consolidated / default-dimension values. If dimensional members are absent, **the FX arm of the structural read does not exist on that endpoint** and must come from the Financial Statement Data Sets or the filing's own XBRL instance. This single unknown is why the probe goes first | not measured — deskcraft has no egress and no User-Agent has been declared. §3 makes it check P-1 |
| **M17** | Open package count is **22**: D3a, D5, D3b, D4, D6, D7a, D7b, D8, D9, D10, D11, D12, D13, D14, D15, D16, D17, D18, D19, D20, D21, D22. Closed: D1, D2 | `BUILD_ORDER_D3_D16.md` §4 |
| **M18** | **`lint-imports` has never been able to run in this repo, and one of its three contracts cannot be expressed at all.** Two faults, found today by running the gate the plan's §9 lists as mandatory before every commit. (a) `[tool.importlinter]` omits `include_external_packages`, which import-linter requires whenever a forbidden module is external — the tool exits on configuration before evaluating a single contract. (b) With that added it still refuses: *“Invalid forbidden module meip.lpal: subpackages of external packages are not valid.”* The contract forbidding `meip.lpal` and `curvecast.news.scoring` — the LLM edge — **is not expressible in import-linter's semantics** | `lint-imports` under import-linter 1.10.0, from `deskcraft/` with `PYTHONPATH=src` |

**M18 is the same defect this session closed in MEIP eight hours earlier, in a different repo.** A guard that is correct, carefully reasoned, documented at length — the contract's own comment block explains precisely which direction it covers and delegates the reverse to an AST test — and **never once invoked**. The plan's §9 has listed `lint-imports` as one of four gates that must be green before every commit since D1, and it has never produced a verdict. **A guard that is correct, tested, and never invoked is indistinguishable from no guard.** Nothing in this repo has actually been checked against the LLM edge except by the AST bars in `test_deskcraft_boundary.py`, which do run and do pass.

The fix is not a flag. Since the contract is inexpressible in import-linter, **the LLM-edge ban belongs where the repo's other capability bans already live** — as an AST bar in `test_deskcraft_boundary.py`, alongside `test_the_edges_are_one_way`, which the same comment block already uses for the reverse direction. ~~That is D3a's work and is added to D3a's deliverable rather than done here.~~

**Closed 2026-09-09, in this same commit, and deliberately as code.** Leaving a dead gate on HEAD in order to preserve a documentation commit's tidiness would have been the same trade that produced M18 in the first place. The repair is the minimum that makes the gate produce a verdict and keeps the ban enforced:

1. `include_external_packages = true` added — without it import-linter exits on configuration.
2. The third contract **withdrawn from `pyproject.toml`**, with the reasoning preserved in place. Banning the parents instead is not available: deskcraft imports `meip.rates` and `curvecast.stage3.factor_space` by design.
3. The ban re-expressed as **C23**, an AST scan over `SRC` and `TESTS` matching full dotted paths segment-wise, so `meip.lpal.client` is caught and a hypothetical `meip.lpalette` is not — plus **C23b**, which mutates it against four reaching imports and two benign ones, because a guard that has never fired is a guard on trust.
4. **C8 generalised, which is the part that matters.** It checked that contracts were *declared*; it now also checks they can be *evaluated* — asserting the flag, and refusing any forbidden module containing a dot. The specific defect cannot recur in the shape that could not run.

**Result: `lint-imports` reports 2 kept, 0 broken — the first verdict it has ever produced in this repo. pytest 22 → 24.** D3a keeps `PACKAGE_BUDGET`, `FitWindow`, the `SCRIPTS` widening and the two registers; the M18 line leaves its deliverable.

> **M18a — the repair collided with a bar id, corrected later the same day.** *(Written 2026-09-09; committed 2026-09-11, held until curvecast's gate sweep was green.)* The two bars above shipped as **`C10` / `C10b`**, and D2 already held `C10`: the AST scan asserting `Direction` and `Notional` are defined in exactly one place. Both modules were green, because every bar passed — a duplicate id is invisible to a suite that only runs tests. In a repo whose `C` sequence is declared **global** (`PRECOMMIT_deskcraft_d2_book_types.md`, §0: *a `C` number is what gets cross-referenced from another package*), that leaves two documents citing `C10` and meaning two different scans.
>
> **The newer pair moved, to `C23` / `C23b`.** Not the older one: D2's C10 is cited by a closed package's pre-commit, by `PLAN_deskcraft.md` §7 and by `src/deskcraft/book.py`'s own docstring, and renumbering a closed record to tidy an open one inverts which claim gets to be stable. Every citation of the moved pair is corrected in place — here, `BUILD_ORDER_D3_D16.md` §4, `PRECOMMIT_deskcraft_d1_scaffold.md` B8, and `PLAN_deskcraft.md` §8 — and **nothing about what either bar checks has changed.**
>
> **The collision built a register D3a had not planned, and dated it.** This repo had **no bar-id gate at all**, and curvecast's `check_bar_coverage.py` would not have caught it either: it takes one doc and one test module per invocation and asks whether each tabled bar is claimed, which a duplicate across two modules passes. **C24** now scans every `tests/test_*.py` for a repeated id and **C24b** mutates it against both a real collision and the `C24`/`C24b` near-miss. The rest of the registry — claims to scorers, sources to fallbacks, `PACKAGE_BUDGET` — stays D3a's; this is the one piece the violation made unwise to defer.

**M11 is the finding that orders the rest.** The plan is not short of thinking. It has produced
782 lines of argument in three days against zero lines of code, and every item below is weighted
by whether it moves that ratio.

**M12 is a defect of exactly the kind this project exists to find, located in its own register.**
The build order's §6 forbids "a flag threshold set after seeing which legs it fires on", and §9
of the research memo caught an n = 3 bar that could not reject. M12 is the same family one level
down: a bar whose stated conjunction overstates its strictness to a reader. It was found by
simulating the bar's power — machinery aimed at something else — which is how curvecast's last
two items found their defects too.

---

## 1. The eight items, and what each becomes

| # | Item as received | Verdict | Lands as |
|---|---|---|---|
| 1 | Read exposures structurally instead of estimating them | **Adopted, reframed** | §2 — three quantities not two; error sources named; **H17** added; "exact" withdrawn |
| 2 | Run the pilot before writing D17's pre-commit | **Adopted, with a blindness rule** | §3 — the probe may count, it may not measure, and a test enforces it |
| 3 | Move the exposure probe from 17th to near-first | **Adopted, moved further than proposed** | §4 — **D23** is first in the running order, ahead of D3a |
| 4 | Split the conjunctive hypotheses; effect size first | **Adopted, but the split is not the one proposed** | §5 — the proposed three-way split is wrong because one clause is vacuous (M12); CI methods named; two power tables added |
| 5 | Freeze the plan, one-in-one-out | **Adopted, strengthened to a build failure** | §6 — a sentence in a doc is not a constraint in this repo |
| 6 | Shippable checkpoint before D16; decouple the halves | **Adopted, as two checkpoints and two papers** | §7 — CP-1 and CP-2 are tags and write-ups, **not packages** |
| 7 | Write the paper's abstract now, with blanks | **Adopted and done, twice** | §8 — both abstracts written out in full below |
| 8 | Reduce concurrency | **Adopted, and answered specifically** | §9 — three of the four competitors are already resolved; the answer is aqrtp |

---

## 2. Item 1 — the structural read. Adopted, and reframed on three points.

The proposal: stop estimating exposure by regression and start reading it out of the filings in
units — floating-rate notional from the debt footnote, gallons of jet fuel from operating
statistics, revenue by geography from ASC 280 segment reporting.

**This is the strongest item and it is adopted.** It is also stated in a form the layer's own
§11 forbids, and three corrections are needed before it can be built.

### 2.1 There are three quantities, not two, and the third one is free

The proposal frames this as structural-versus-regression. It is better than that. Item 7A is
**management's characterisation** of the exposure — typically "a hypothetical 100 basis point
move would change interest expense by $X" — which is a model, run by the firm, on assumptions it
does not publish. The debt footnote is **arithmetic on reported units**. These are different
objects and both are public.

| Quantity | Source | What it is | Error |
|---|---|---|---|
| **Disclosed** | Reg S-K Item 305 / Item 7A tabular sensitivity | Management's model output | Unknown, unpublished assumptions |
| **Structural** | Debt footnote, operating statistics, ASC 280 segments, derivative notionals | Arithmetic on reported units | §2.2 — bounded, and enumerable |
| **Measured** | Adler–Dumas elasticity regression | Net-of-everything realised sensitivity | Sampling error, non-stationarity |

The original H11 compared **disclosed against measured**. Adding the structural quantity gives a
three-way comparison at no extra extraction cost, and **disclosed-versus-structural is itself a
finding about disclosure quality** — two numbers the same firm published in the same document,
one from its model and one from its own arithmetic. Where they disagree, the reader learns
something about Item 7A that no regression can tell them.

### 2.2 "Exactly" is withdrawn, and the four error sources are named

> *"Floating notional × duration = DV01, exactly. No regression."*

It is not exact, and asserting that it is would commit the layer's own §11 defect — an exposure
taken from a filing without measuring it — from the opposite direction and with more confidence.
Four error sources, all real and all bounded:

1. **Granularity.** The maturity schedule is annual buckets, not dated cashflows. Duration
   computed from buckets is a step approximation.
2. **Reset dates unknown.** A floating tranche's DV01 depends on time to next reset, which is
   generally not disclosed. Between a fresh reset and one a day away, the current period's DV01
   differs by its full amount.
3. **Swap overlays.** Firms routinely swap fixed to floating and back. `DerivativeNotionalAmount`
   is sometimes tagged and sometimes only described in prose. A structural read that misses the
   overlay reports the pre-hedge exposure and calls it the exposure.
4. **Definitional drift.** "Floating" spans SOFR, term SOFR, prime, and legacy LIBOR fallbacks,
   with different beta to the curve point being hedged.

Realistic accuracy is a **DV01 known to roughly ±10–20%**, not to the decimal. That is still an
enormous improvement over a coefficient whose confidence interval contains zero, and the correct
claim is that improvement — not exactness.

### 2.3 What the structural read actually does: it moves the unknown onto a bounded interval

This is the sharpest statement of the item's value, and it is not how the proposal states it.

Southwest's 1.1 billion gallons is a **gross physical quantity**. The firm's P&L exposure to jet
fuel is

```
exposure  =  gallons  ×  (1 − pass_through)  ×  (1 − hedge_ratio)
```

and both fractions are unobserved. The estimation problem does **not** disappear. What changes is
its shape:

| | Regression path | Structural path |
|---|---|---|
| Unknown | a coefficient on an unbounded real line | two fractions, each in **[0, 1]** |
| An uninformative result looks like | a CI containing zero — no information at all | a bracket **[0, gallons × price]** — the worst case is known |
| What is reportable when uninformative | nothing | the bracket, which is a real quantity |

**A bounded unknown is worth far more than an unbounded one even when neither is pinned down.**
An exposure known to lie in a stated interval can be hedged conservatively, stress-tested at both
ends, and reported honestly. A coefficient whose interval contains zero can do none of those.
This is the same move curvecast's item 29 ended on — a bracketed bound rather than a point
estimate — and the paper should say so in those terms.

### 2.4 The limit the proposal understates, and it is the important one

> *"The debt footnote gives you financial rate exposure exactly and says nothing about operating
> rate exposure."*

Correct, and the consequence is larger than the sentence suggests. **Financial rate exposure is
precisely the channel that is already trivially hedged** — issue fixed, or swap — and it is where
Bartram's ~40% "absorbed by financial hedging" lives. So the structural read is at its most
accurate on the channel that is *least* interesting for the hedging question, and silent on the
operating channel — a homebuilder's sales sensitivity to mortgage rates — that motivates the
layer.

That is a genuine risk to item 1, and it is **pre-registered rather than discovered**, which is
what H17 does.

### 2.5 New hypothesis, and the asymmetry is the claim

> **H17 — the structural-versus-measured gap is asset-class conditional.**
> The ratio (structural exposure ÷ measured exposure) has a cohort median **above 2.0 for FX and
> commodity exposures** and **below 1.5 for interest-rate exposures**.
>
> **Predicted: PASS on both halves.** FX and commodity exposure is absorbed before it reaches
> returns by pass-through (10–15%) and operational hedging (10–15%) — Bartram–Bodnar's roughly
> two-thirds — so the gross structural quantity should exceed the measured elasticity by a factor
> near three. Interest-rate exposure read from the debt footnote is **already net of financial
> hedging** when the swap overlay is tagged, so no comparable wedge should open.
>
> Scored by **D17**. Reported as a distribution with a bootstrap percentile CI (§5.3), never as a
> single ratio.

Nobody in the exposure-puzzle literature states the claim in this form; it is cheap, because both
quantities are computed anyway; and — the part that matters — **it is falsifiable in a way that
would tell us the structural read is broken.** If rates show the same factor-of-three wedge as FX,
the debt-footnote read is missing the swap overlay and §2.2's error 3 is binding. H17 is therefore
a finding and a self-diagnostic on item 1 at the same time.

### 2.6 What has to be true for any of this to exist

None of §2 is buildable if the tags are not populated. That is M16, it is unverified, and it is
the whole reason for §3 and §4.

> **M16 is no longer unverified. Measured 2026-09-09 by D23** (curvecast
> `docs/PRECOMMIT_curvecast_wpd23_exposure_probe.md` §3.3, fixture
> `tests/fixtures/exposure_probe_20260909.csv`). **`companyfacts` returns
> default-dimension values only — zero dimensional fact entries across all twenty firms.**
> The tags §2 needs are populated; the *dimensions* §2 needs are not, and those are two
> different claims that this section had folded into one. See the adjudication in §3.7.

---

## 3. Item 2 — the pilot. Adopted, with a rule the proposal does not contain.

### 3.1 An unconstrained pilot destroys the package it was meant to protect

The proposal: pull 15–20 firms, extract the structural exposures, run the regressions, count how
many are usable, then write D17's pre-commit.

**As written, this destroys D17's pre-registration.** If the pilot reports that the median
disclosed-to-measured gap came out at 3.1×, then H11's ">30%" is no longer a prediction — it is a
threshold chosen with knowledge of the answer. The same applies to H14's 0.5, H15's one-half, and
H17's 2.0. The plan's own §6 forbids "a flag threshold set after seeing which legs it fires on";
a pilot that measures effect sizes commits that at the level of the entire layer.

This is the hazard curvecast's `TRIAL_LEDGER` exists for, and it does not require an `UnsealToken`
to occur — a human reading a number is sufficient.

### 3.2 The blindness rule

> **The probe may count. The probe may not measure.**
>
> It reports how many firms have a tag, how many parse, how many yield enough observations, and
> how many survive each filter. It never reports an exposure, a ratio, a gap, an R², a
> coefficient, a t-statistic, or any function of them — not in the commit, not in the log, not on
> the terminal, not for a single firm.

Feasibility is a property of the data's **presence**. Effect size is a property of its **values**.
The probe needs only the first, so the de-risking is available without paying for it in
pre-registration — and the two are separable in code as well as in principle.

### 3.3 The rule is enforced, not promised

The probe emits exactly one artifact, with a fixed schema:

```
firm_cik, asset_class, tag_path, present(bool), parsed(bool), n_obs(int), drop_reason(str|null)
```

Its pre-commit fixes that column list, and **a test asserts the emitted frame's columns are a
subset of it.** A float-valued exposure column cannot be added without turning the gate red. That
is the shape D3a's claims register uses and the shape D2's `Neutrality` gate uses: the constraint
is a type, not a habit.

`n_obs` is a count and is permitted — it bears on power, which §5's tables need, and it is not a
function of any exposure value.

### 3.4 Size, stratification, and why the probe firms stay eligible

**20 firms, stratified five per asset class** — rates, FX, commodity, credit. Unstratified, a
20-firm draw could contain no firm disclosing a physical commodity quantity, and would therefore
say nothing about the arm the proposal's best example rests on. Stratifying a probe that reports
no effect sizes biases nothing, because there is no estimate for the stratification to bias.

**The probe firms remain eligible for D17's cohort**, and the reasoning belongs on the record
because it will be challenged: under §3.2 the probe publishes no effect size, so no information
about *values* crosses into the pre-commit. What does cross is information about *availability* —
and that is handled by deriving the cohort rule from the method rather than from the sample. The
completeness filter requires "the facts the regression needs are present", a requirement that
follows from the regression, not from which firms happened to have them. The drop count is
reported either way.

### 3.5 It is a curvecast commit, and it carries no hypothesis

deskcraft has no egress (bars C2/C4) and never will. Extraction lives in curvecast, which already
holds the FRED plumbing, the floor grading, and the `make_sealed_panel.py` precedent. The probe is
a curvecast work package emitting a feasibility report plus a dated fixture; deskcraft receives
files.

**The probe carries no hypothesis, deliberately.** D3a's claims register requires every claim to
name a scorer; it does not require every package to carry a claim. A probe with a hypothesis would
be a measurement package, and §3.1 is why it must not be one.

### 3.6 The six questions the probe must answer

| # | Question | Decides |
|---|---|---|
| **P-1** | Does `companyfacts` return dimensional facts, or only default-dimension values? If not, do the Financial Statement Data Sets (`num.txt` segments) or the filing's own XBRL instance carry them? | **Whether the FX arm of §2 exists at all.** M16 |
| **P-2** | For each asset class, which concrete tag path yields the structural quantity, and for how many of the 20 is it populated? Rates: `DebtInstrumentCarryingAmount`, `LongTermDebtMaturitiesRepaymentsOfPrincipalIn*`, `DebtInstrumentInterestRateStatedPercentage`, `DebtInstrumentBasisSpreadOnVariableRate1`, `DerivativeNotionalAmount`. Commodity: company-extension namespace tags for physical volumes | Whether §2.2's error 3 (swap overlays) is even detectable |
| **P-3** | Is the Item 7A quantitative disclosure a parseable table, or prose and images? Count parseable of 20 | Whether the **disclosed** quantity of §2.1 is obtainable |
| **P-4** | Per-firm usable observation counts, at daily-equity frequency and at quarterly-XBRL frequency | Feeds §5.4's firm-level power table directly |
| **P-5** | Starting from a dated index snapshot, what fraction survives the completeness filter? | Whether a 40-firm cohort is reachable, or whether the screen must start from 200 |
| **P-6** | SEC fair access requires a declared User-Agent carrying a name and email | **A decision for the owner, not for the build.** §10 item 0 |

**The stopping condition, fixed now, before the probe runs.** If fewer than **8 of 20** firms
yield a structural read in at least one asset class, item 1's reframe fails: D17 reverts to the
regression-only design and H17 is withdrawn from the register. That is a finding, it costs two
days, and it is worth knowing before sixteen packages are built on top of it.

### 3.7 The verdict, adjudicated 2026-09-09

> **MET. 19 of 20** against the threshold of 8 — and **14 of 20** under a stricter reading that was
> not pre-committed and is reported as a sensitivity rather than substituted for the verdict.
> **Item 1's reframe holds. D17 proceeds. H17 stays in the register.**

It cost 63 requests and about two hours, which is what §3 was for.

**But the probe returned three things that change what D17 builds, and all three cut against §2.**
A stopping condition is not the only thing a probe can tell you, and treating "MET" as the whole
result would waste the other two-thirds of what it cost.

**1. P-1 came back *no*, and §2.6 is where it lands.** `companyfacts` carries **zero** fact entries
with any key outside the default-dimension set, across all twenty firms and every element in their
payloads. Revenue by geographic area is not on that endpoint at any depth. The FX arm of §2 is not
dead — `num.txt` in the Financial Statement Data Sets carries segment columns, and the filing's own
XBRL instance carries the full dimensional context — but **D17's FX channel now needs a source
change**, which is scope §2 did not carry and §2.6 did not anticipate because it conflated *the tag
is populated* with *the tag is populated at the granularity we need*. Those are two claims. The
first is true. The second is false on this endpoint.

**2. The commodity *consumer* read does not exist at all.**
`DerivativeNonmonetaryNotionalAmountVolume` — the element that would carry physical volumes,
gallons of jet fuel, ounces of gold — returns **zero of five across the whole commodity arm**. That
is §2.1's "operating statistics → commodity units" channel, and it is the one channel of the three
with no XBRL element behind it in this sample. `DAL` is the only firm of twenty with no structural
read, and §5 of the probe's own document had named Delta specifically as the consumer side against
Newmont as the producer, on the argument that a producer-only count would not transfer. It did not
transfer.

**3. P-5 inverts P-2 on rates, and this is the finding with the widest reach.** The rates arm
scored **5 of 5** on the named firms and **1.3% of 7,714 filers** in the 2026q2 bulk dataset. The
debt-footnote elements are tagged by large filers and by almost nobody else. So §5.4's cohort
cannot be drawn from the filer universe for rates, and credit at 7.8% says the same: the
"start from 200" branch of P-5's decision is not merely preferable, it is **required** for those
two arms. The FX population figure, 72.7%, is the least informative number in the probe — it is
carried by `Revenues`, which P-1 has just established arrives with no geographic split.

**What did not change, which is worth saying because it is the part §5 got right.** The credit arm
is 5 of 5 under both readings and 7.8% of the population — exactly §5's stated position, that it
generalises to lenders rather than to firms, with the lenders duly there. And **depth is not the
constraint: 55 of 120 rows were dropped because the element was absent and only 5 for falling
below the observation minimum.** §5.4's power table was written against the risk of short
histories. The binding constraint is coverage, which is the opposite risk, and the table should be
re-read with that in mind before D17 sizes anything.

---

## 4. Item 3 — the reorder. Adopted, and moved further than proposed.

The proposal puts the probe at position 2, after D5. It goes to **position 1**, ahead of D3a.

D5 (front-end archive floors) and D3a (guards and registers) both serve the macro engine, which
per §7 is a separable deliverable that ships on its own. The probe serves the solutions layer —
the riskier half, and the one with a live unknown (M16). Nothing in the probe depends on anything
in deskcraft; it is a curvecast package emitting a fixture. There is no dependency argument for
putting it second, only habit.

**New package: D23 — the exposure feasibility probe.** Numbered last, placed first — the
convention this document already established when D5 moved ahead of D4 and kept its number.

| Position | Package | Note |
|---|---|---|
| **1** | **D23** | ***new, and first.*** The probe. Runs in curvecast. §3 |
| 2 | D3a | Guards and registers — **plus §6's package budget** |
| 3 | D5 | Front-end archive floors |
| 4 | D3b | The data panel |
| 5 | D4 | DV01 and leg P&L |
| 6 | D6 | The view language |
| 7 | D7a | The cost model |
| 8 | D7b | Leg generator |
| 9 | D8 | Covariance |
| 10 | D9 | Component ES and VaR, flags F1–F4 |
| 11 | D10 | Effective number of bets |
| 12 | D11 | Sizing under the risk budget |
| 13 | D12 | Scenario engine — **then CP-1** (§7) |
| 14 | D13 | Reverse stress |
| 15 | D14 | Risk-model backtest |
| 16 | D15 | Construction backtest |
| 17 | D16 | Readout and **Paper 1** — **then CP-2** (§7) |
| 18 | D17 | Exposure extractor — **its pre-commit is written after D23 reports** |
| 19 | D18 | Structure grammar and the suitability gate |
| 20 | D21 | End-to-end hedge backtest |
| 21 | D22 | Funding path, crisis-conditional effectiveness, and **Paper 2** |
| — | ~~D19~~, ~~D20~~ | **Annex** — out of the frozen core. §6.3 |

---

## 5. Item 4 — the bars. Adopted, but the split is not the one proposed.

### 5.1 The proposed split is wrong, because one of the clauses is vacuous

The proposal splits H14 three ways: H14a (OOS R² < 0.5), H14b (< half in-sample), H14c
(prevalence ≥ 70%). It reads the conjunction as *too demanding* — "real data will half-clear it".

**The opposite is true, and it is provable in one line.** In-sample R² ≤ 1 by definition.
Therefore ½ × in-sample R² ≤ 0.5. Therefore

```
OOS R²  <  ½ × in-sample R²    ⟹    OOS R²  <  0.5
```

**always.** The level clause is strictly implied by the decay clause and can never bind. M13
confirms it numerically: across all fifteen simulated cells, P(both clauses) equals P(decay
clause) to three decimals.

So H14 is not a demanding two-part bar. It is a one-part bar with a decorative second part that
makes it *read* as stricter than it is. In a project whose entire value proposition is bars fixed
in advance and honestly reported, a bar that overstates its own strictness to a reader is a
defect, and it must be corrected in the register rather than explained in the paper.

### 5.2 The correct split

| ID | Clause | Relationship | Predicted |
|---|---|---|---|
| **H14a** | OOS Ederington R² **< 0.5** | the weaker bar | PASS |
| **H14b** | OOS Ederington R² **< ½ × in-sample R²** | **strictly implies H14a** | PASS |

Both are scored and both prevalences reported, with the containment stated in the paper:
*H14b ⊆ H14a by construction, so the only informative comparison is the count of firms in
H14a that are not in H14b* — that is, hedges that are weak but not decaying, which is a
different diagnosis from hedges that decay.

The same audit applied to the other conjunctive bars:

| Bar | Conjunction? | Verdict |
|---|---|---|
| **H11** | ">30% over-hedge" **and** "≥70% of cohort" | **Not a defect.** An effect clause plus a prevalence clause is the correct shape — the prevalence is over firms, the effect is within a firm. Keep, and report per §5.3 |
| **H14** | two effect clauses **and** prevalence | **Defective**, per §5.1. Split into H14a / H14b |
| **H15** | one effect clause + prevalence | Sound |
| **H16** | one effect clause + "≥ 1 of 3 cases" | Sound as an existence claim, but n = 3 **cannot support a prevalence reading**. Restate explicitly as *existence*: "at least one case client exhibits this", with no implied rate |
| **H17** | two conditional medians | Sound — the two halves are over disjoint subsets (FX/commodity vs rates), so they are independent claims, not a conjunction |

### 5.3 Effect size first, bar second — with the interval methods fixed now

Adopted from the proposal, and the point is that both formats are declared **before any number
exists**, so neither is a goalpost that moved.

| Quantity | Headline statistic | Interval method, fixed now |
|---|---|---|
| Cohort prevalence (H11, H14a, H14b, H15) | k of 40, as a proportion | **Clopper–Pearson exact**, two-sided 95% |
| Per-firm effect size (R², over-hedge ratio) | point estimate | **Stationary bootstrap** (Politis–Romano), 10,000 resamples, expected block length stated in the pre-commit |
| Cohort median ratio (H17) | median across firms | **Bootstrap percentile**, 10,000 resamples over firms |
| Decay (H14b) | ratio OOS ÷ in-sample | bootstrap percentile, same |

The binary bar remains, unmoved, and remains the pre-registered decision rule. It is reported
**second**, as a footnote to the effect size, for the reason §5.5 makes concrete.

### 5.4 The firm-level power table — owed, and missing until now

The research memo's §9 published a power table for the **cohort** and thereby caught the n = 3
defect. **No equivalent table exists for the per-firm bars**, whose power depends on each firm's
own observation count. That is the same defect one level down, and the proposal's instinct that
"there is no reason to assume it only happened once" was right without identifying where.

Published here, before any run. Sampling distribution of an estimated R², 40,000 replications:

| True R² | n | 2.5% | median | 97.5% | P(estimate < 0.5) |
|---|---|---|---|---|---|
| 0.15 | 60 | 0.023 | 0.152 | 0.344 | 1.000 |
| 0.30 | 40 | 0.084 | 0.305 | 0.543 | 0.944 |
| 0.30 | 60 | 0.120 | 0.304 | 0.499 | 0.976 |
| 0.30 | 2700 | 0.271 | 0.300 | 0.329 | 1.000 |
| **0.50** | **60** | **0.311** | **0.504** | **0.667** | **0.486** |
| 0.50 | 2700 | 0.473 | 0.500 | 0.526 | 0.495 |
| 0.70 | 40 | 0.516 | 0.705 | 0.833 | 0.018 |
| 0.70 | 60 | 0.551 | 0.704 | 0.811 | 0.006 |
| 0.70 | 2700 | 0.680 | 0.700 | 0.718 | 0.000 |

**The result is reassuring and it is the opposite of what was feared.** The level bar
discriminates well even on quarterly data: at n = 60 a firm at true R² 0.30 reads below 0.5
essentially always, and one at 0.70 essentially never. Firms sitting near 0.5 are a coin flip,
but that is true of any threshold and is not a defect.

And the decay clause, under a null of **no true decay** — two independent samples with identical
true R²:

| True R² | n per half | P(OOS < ½ × IS) — false positives |
|---|---|---|
| 0.30 | 30 | **0.162** |
| 0.30 | 60 | **0.080** |
| 0.30 | 126 | 0.022 |
| 0.50 | 30 | 0.049 |
| 0.50 | 60 | 0.011 |
| 0.50 | 630 | 0.000 |
| 0.70 | 60 | 0.000 |
| any | ≥ 630 | **0.000** |

**Consequences, both recorded now:**

1. **At daily-equity frequency the decay clause is clean** — zero false positives. H14b run on
   the daily denominator is uncontaminated.
2. **At quarterly-XBRL frequency it is not clean for low-R² firms.** Up to 16% of firms with no
   true decay will appear to decay. Against a 70% prevalence bar that is not enough to manufacture
   the finding, but it is enough that **the quarterly result must be reported with this false-
   positive rate beside it**, and the two denominators must never be pooled.

### 5.5 The cohort-level interval — the bar and the claim are different statements

Exact Clopper–Pearson, n = 40:

| Outcome | Proportion | Exact 95% CI | Width | Excludes 0.70? |
|---|---|---|---|---|
| 40/40 | 1.000 | [0.912, 1.000] | 0.088 | yes |
| 36/40 | 0.900 | [0.763, 0.972] | 0.209 | yes |
| **34/40** | **0.850** | **[0.702, 0.943]** | 0.241 | **yes — the smallest count that does** |
| 32/40 | 0.800 | [0.644, 0.909] | 0.266 | no |
| **28/40** | **0.700** | **[0.535, 0.834]** | **0.300** | **no** |
| 24/40 | 0.600 | [0.433, 0.751] | 0.318 | no |

**An outcome of exactly 28/40 clears the bar and is consistent with a true prevalence anywhere
from 53% to 83%.** So "≥ 70% of the cohort" is a sound **decision rule about the sample** and is
not a **claim about the population**, and the plan currently writes it as though it were both.

Resolved as follows, and this is why §5.3 puts the effect size first:

- **The decision rule does not move.** 28/40 was pre-registered; changing it to 34/40 after
  computing the interval would be exactly the goalpost-moving the rule exists to prevent.
- **The headline becomes the interval.** The paper reports "28 of 40 firms, 95% CI [0.535,
  0.834]" and states in words that the data are consistent with a true prevalence well below the
  bar. The pre-registered pass is reported beside it, honestly, as what it is.
- Where an outcome reaches 34/40 or better, the paper may additionally state that the CI excludes
  0.70 — and that stronger sentence is available only because the threshold for it was fixed
  here, in advance.

### 5.6 The register, amended

Changes to `BUILD_ORDER_D3_D16.md` §5 (applied in the same commit as this document):

| Row | Change |
|---|---|
| H12 | **Splits.** H12a (variance-reduction ratio ≥ 90%) → scored by **D21**, stays in core. H12b (the markup half, needing the 424B2 population) → **annex with D20**. §6.3 |
| H14 | **Replaced** by H14a and H14b per §5.2 |
| H16 | Restated as an **existence** claim, not a prevalence one |
| **H17** | **New**, scored by D17, per §2.5 |

Net claims: 16 → 18 rows, of which 1 is annexed. **No new package is required to score any of
them** — H17 falls to D17, H12a to D21.

---

## 6. Item 5 — the freeze, as a build failure rather than a sentence

### 6.1 The rule

> **The package list is frozen at 21 as of 2026-09-08. No package may be added to the core until
> one is closed. A package may be moved to the annex at any time; a package may leave the annex
> only by displacing a core package.**

### 6.2 Enforced in D3a, because in this repo a rule that is only written is not a rule

The whole architecture of this project is that constraints are types and gates: the boundary
test bans capability rather than vocabulary, the claims register makes an unscored claim a build
failure, the suitability gate is an iff rather than a warning, and `FitWindow.__post_init__`
refuses a date rather than discouraging it. **A one-in-one-out rule that lives only in prose is
the one constraint in the repo held together by memory** — and by M11's evidence, memory is
exactly what failed here.

So D3a's registers gain a third:

```
PACKAGE_BUDGET = 21          # core, frozen 2026-09-08 by AMENDMENT_A1
```

with the gate failing when the count of core packages in the order table exceeds it. The register
holds the order table as data, exactly as it already holds the claims table as data, so the count
is read rather than asserted. Adding a package therefore requires **editing the budget in the same
commit**, which makes the addition visible in a diff instead of invisible in a table.

**This amendment was written to be the last doc-only commit before code, and it did not survive
its own gates.** Running the four checks §9 requires found that one of them had never run at
all (M18), so the commit carries a repair: `pyproject.toml`, and C8 / C23 / C23b in
`tests/test_deskcraft_boundary.py`. Doc and code in a single commit is the inherited discipline
anyway. The rule stands in the form that matters — **the next document written is D23's
pre-commit, and it is written against a probe that runs.**

### 6.3 The annex — D19 and D20 leave the core

Two packages are moved out. Both were argued well; neither is load-bearing for the headline that
§0 item 10 already settled — *the deliverable is the instrument portfolio, and the headline test
is the end-to-end replay*.

| Package | Why it leaves | What it costs, stated |
|---|---|---|
| **D19** — option pricing under the free vol parameterisation | Item 10 demoted pricing to fair-value-with-a-band, and the selling tier is out of scope. Brown–Toft's decision rule — forwards optimal absent quantity uncertainty, options necessary with it — is the part that matters, and **the rule can be stated and applied without pricing the option.** The engine outputs "this exposure requires convexity; a vanilla is indicated; pricing it needs a surface free data does not provide", which is a more honest deliverable than a price derived from four parameters | The commodity case study is limited to linear hedges, and the paper says so. **H13 survives**: a cost minimiser selects a 2:1 leveraged forward — leverage > 1, purely linear, no surface needed — so the KIKO mechanism is exhibitable without D19 |
| **D20** — markup benchmark against the 424B2 population | This is a paper about structured-note pricing, not about hedging. It shares no machinery with the end-to-end loop | H12 splits: **H12a** (variance reduction) stays with D21; **H12b** (markup) is annexed with the package |

**The annex is not a deletion.** The argument is preserved in `RESEARCH_client_solutions_layer.md`
§4 and §7 and can be built the moment the core closes. What it may not do is consume attention
first.

---

## 7. Item 6 — two checkpoints and two papers, neither of them a package

### 7.1 The checkpoints

Adopted, and deliberately implemented as a **git tag plus a one-page write-up produced inside the
preceding package's commit**. Making a checkpoint its own package would violate §6 and would also
be the wrong instinct: a checkpoint is a claim that existing work is presentable, not new work.

| Tag | After | What exists at that moment | What does not |
|---|---|---|---|
| **CP-1** | D12 | The engine runs end to end: a view string in, a sized multi-leg book out, stressed against dated history and a filtered-historical-simulation Monte Carlo. **H3, H4, H6, H7 scored** — 4 of 9 | H1/H2 (need D14), H5 (needs D15), H8/H9 (need D7b/D10 results in place) |
| **CP-2** | D16 | The macro engine, **validated**. H1–H9 all scored. Paper 1 complete and sendable | Everything in the solutions layer |
| **CP-3** | D21 | *(Added 2026-09-29 by the owner's decision, DD244.)* The solutions layer, **scored**. Paper 2's eight live rows all scored: five as predicted, two against, one not performed. Paper 2 complete, and every package in the frozen build order landed | Nothing in the build order |

CP-1's write-up is one page and answers one question: *if everything after this stalls, what do I
hold?* The answer at CP-1 is a working, stressed construction engine with four pre-registered
results — which is a real artifact, and currently nothing is presentable before the twenty-first
package.

### 7.2 Two papers, which is stronger than "decouple the halves"

The proposal asks for the halves to be decoupled. Formalise it: **they are two papers**, with
disjoint hypothesis sets and no shared dependency running from the second to the first.

| | Paper 1 | Paper 2 |
|---|---|---|
| Title, working | *A cost-aware multi-leg construction engine and its risk-model backtest* | *Hedging measured exposure: an end-to-end test on public filings* |
| Packages | D3a–D16 | D17, D18, D21, D22 |
| Hypotheses | H1–H9 | H11, H12a, H13, H14a, H14b, H15, H16, H17 |
| Complete at | CP-2 | end of D22 *(D21 landed last, on 2026-09-29, and **CP-3** is tagged there, DD244)* |
| Depends on the other? | **No** | Yes — it reuses D6–D12 unchanged |

**If the exposure layer dies at D23's stopping condition, Paper 1 is unaffected and still ships.**
That is the entire point of the split, and it converts the proposal's "~25% engine only, no client
layer" outcome from a failure into a planned, publishable landing.

---

## 8. Item 7 — the abstracts, with blanks, written now

The proposal calls this the cheapest test in the list and observes that people almost never run
it. Run here, twice. Blanks are `[__]`; nothing below is a result.

### 8.1 Paper 1

> We build and validate a cost-aware engine that turns a stated macro view into a multi-leg
> portfolio of US fixed-income instruments, sizes it under an expected-shortfall budget, and
> stresses it against dated historical episodes. Every fitted object — the factor basis, the
> covariance, the GARCH filter — is estimated on 1988–2014, and every test runs on 2015–2026, an
> out-of-sample window of approximately 2,700 daily observations whose power we publish before
> the first run. Nine hypotheses were pre-registered with their predicted verdicts, two of them
> predicted to fail. [__] of nine were scored as predicted. The risk model's unconditional
> coverage [was / was not] rejected (Kupiec p = [__]); its exceptions [were / were not]
> independent (Christoffersen p = [__]), and we predicted in advance that they would not be.
> Expected-shortfall-constrained sizing [beat / did not beat] equal weighting across the same legs
> (Ledoit–Wolf HACPW p = [__]), which we also predicted. A six-leg book expressing a single view
> has an effective number of bets of [__] in the PCA basis against a leg count of six; we report
> the statistic under three definitions because they disagree by a factor of [__], and the
> disagreement is itself the result. The leg count is an output of a cost-aware stopping rule
> rather than an input, and it terminated at [__]. The engine describes and never recommends, and
> a boundary test enforces that at the level of capability rather than vocabulary.

### 8.2 Paper 2

> A corporate hedge is a portfolio whose factor loading is the negative of the firm's exposure. We
> test whether that exposure can be read rather than guessed from public filings, and whether the
> resulting hedge works. For a mechanically selected cohort of 40 US public companies we compute
> three quantities: the exposure the firm **discloses** under Reg S-K Item 305, the exposure
> implied **structurally** by its own reported units — floating-rate notional, physical quantities
> consumed, revenue by geographic segment — and the exposure **measured** by an Adler–Dumas
> elasticity regression. The three disagree systematically and asymmetrically: the
> structural-to-measured ratio has median [__] for FX and commodity exposures against [__] for
> interest-rate exposures, an asymmetry we predicted in advance from the pass-through and
> operational-hedging channels. Hedges sized off disclosed exposure over-hedge those sized off
> measured exposure by more than 30% for [__] of 40 firms (exact 95% CI [[__], [__]]). Each hedge
> is then constructed **as of a date**, using only data visible at that date, and walked forward
> through [__] dated crises, four of which fall entirely outside every estimation window.
> Out-of-sample Ederington effectiveness falls to [__] of its in-sample value for [__] of 40 firms;
> computed within crisis windows it falls to [__], so the hedge decorrelates from the exposure
> precisely in the state that motivated it. For [__] of the case clients the hedge's peak
> mark-to-market drawdown exceeds 25% of trailing operating cash flow — correct on price and fatal
> on cash, which no VaR reports. We give fair value with a band and never a quote: the machinery
> for an executable price does not exist on free data, and we say so rather than approximating it.

### 8.3 What writing them revealed

Two things, neither of which was visible before the exercise:

1. **Paper 2's abstract is stronger than Paper 1's.** Paper 1 is a competent validation study;
   Paper 2 contains three claims a rates or corporate-solutions desk would actually argue with.
   The riskier half is the more valuable half — which is not an argument against the reorder, it
   is the argument *for* the probe: §4 exists to protect the better paper, not to retreat from it.
2. **Paper 2's abstract cannot be written at all without the structural quantity.** Remove §2 and
   the abstract collapses to "we ran a regression and it decayed", which is a restatement of
   Bartram. **Item 1 is what makes Paper 2 publishable**, and that raises the stakes on M16 and on
   D23's stopping condition considerably.

---

## 9. Item 8 — concurrency, answered specifically

The proposal declines to say which project to pause. It can be answered, because three of the four
were resolved by decisions already taken:

| Project | State | Attention cost | Action |
|---|---|---|---|
| **momentum** | Live with real funded capital; the automation floor and event-gated ramp landed | **Ops, not build.** It consumes attention on a schedule, not on a backlog | No change |
| **MEIP** | **Parked 2026-09-08** by owner decision at Phase 3, 10 of 14. Its one compounding-cost item — the capture archive — was fixed and automated the same day | **Zero** | No change. Do not propose resuming |
| **curvecast** | All 33 items closed; two looks unspent | **Zero as a project.** It is the host for D23's and D3b's extraction, which is deskcraft work living in curvecast's egress | No change |
| **aqrtp** | Milestone 2, blocked at sub-step 2a-0 on an unmade decision about WSL2 for vLLM | **The only genuine competitor for build attention** | **Stays parked until CP-1.** Unblocking it now would put two ground-up builds in flight simultaneously, which is the term the proposal is pricing |

So the concurrency answer is: **the field is already nearly clear, and the one live competitor is
aqrtp.** Leave it blocked until CP-1 lands. That is a smaller ask than the item implies, and it is
specific enough to act on.

---

## 10. The todo list

Ordered. Each item names the repo it happens in, the gate that must be green, and the condition
that closes it. Items 1–3 are the week the proposal describes; everything after is the frozen core.

| # | Task | Repo | Closes when |
|---|---|---|---|
| ~~**0**~~ | **DONE 2026-09-09.** `Rishith Sharma <email withheld in the public copy>`, chosen by the owner from three options with the disclosure stated, recorded as D423. **Decide the SEC User-Agent.** Fair access requires a declared name and email. This sends the owner's identity to the SEC and is therefore the owner's call, not the build's. Options: personal name + email, or an institutional address | — | A string is chosen and recorded in D23's pre-commit |
| ~~**1**~~ | **DONE 2026-09-09**, curvecast `docs/PRECOMMIT_curvecast_wpd23_exposure_probe.md`, D422-D433 / C497-C505. **Write D23's pre-commit.** §0 measured-before-decided, §1 decisions, §2 what it does not do, **§3.1 the blindness rule and the fixed output schema as a bar**, §3.2 no predictions (it carries no hypothesis), the 8-of-20 stopping condition, and the 20-firm stratified sample named in advance | curvecast | Doc committed with the run |
| ~~**2**~~ | **DONE 2026-09-09 — met in substance, NOT in the letter.** 63 requests against a cap of 250; fixture `tests/fixtures/exposure_probe_20260909.csv`, 120 rows. **`run_gates.py` did not exit 0.** 38 passed, 2 failed; both failures read `timed out after 900s` and neither is a failing test. `meip:pytest` re-ran clean alone (366.2s, 1410 passed) — it had been starved by the gate before it, because `run_one` uses `subprocess.run(timeout=)`, which on Windows kills the parent and not the process tree, so an overrunning gate keeps its grandchildren and poisons the next one. `curvecast:meip-venv-sweep` was then run to completion out-of-band on the identical command with no budget: **194 passed, 0 skipped**, which is what its `classify_no_skips` verdict grades. The harness defect is recorded against `run_gates.py` and is not repaired by this package. **Run D23.** Answer P-1 … P-5. Emit the feasibility frame and a dated fixture. **Report counts only.** One commit, doc and code together | curvecast | `python scripts/run_gates.py` **exits 0 with no gate RED**; the schema test passes; the frame lands |
| ~~**3**~~ | **DONE 2026-09-09 — MET, 19 of 20 (14 of 20 strict). Verdict in §3.7.** **Adjudicate the stopping condition.** ≥ 8 of 20 → item 1's reframe holds and H17 stays. < 8 → D17 reverts to regression-only, H17 is withdrawn, and that verdict is written into this document | deskcraft | A verdict is recorded here, either way |
| ~~**4**~~ | **DONE 2026-09-11**, `docs/PRECOMMIT_deskcraft_d3a_guards_and_registers.md`, DD22–DD38 / C25–C38. Gates, each one run: deskcraft `pytest` 41 passed, `lint-imports` 2 kept, MEIP `lint-imports` 6 kept, curvecast `run_gates.py` 40 of 40, exit 0 (ledger entry committed as curvecast `93ebdec`). **D3a — guards and registers**, plus `PACKAGE_BUDGET = 21` and the count read from the order table. `FitWindow` refusing `end > 2014-12-31`. Boundary scan widened to `SCRIPTS`. Claims register carrying §5.6's amended table as data. Source-resilience register. TRIAL_LEDGER non-look entry. ~~And M18~~ — **closed 2026-09-09 ahead of D3a**, as a repair commit, because a dead gate on HEAD is not something to carry for the sake of a tidy doc commit | deskcraft | All §9 gates green, **and each one demonstrated to run** |
| **5** | **D5** — front-end archive floors, 30 → 34 | deskcraft + curvecast | Floors probed and graded |
| **6** | **D3b** — the data panel as committed dated fixtures | deskcraft | Fixtures land; this repo still fetches nothing |
| **7** | **D4, D6, D7a, D7b** — DV01, the view language, the cost model, the leg generator | deskcraft | H3 and H9 scored |
| **8** | **D8, D9, D10, D11** — covariance, component ES with flags F1–F4, effective number of bets, CVaR/CDaR sizing | deskcraft | H4 and H8 scored |
| **9** | **D12**, then **tag CP-1** with a one-page write-up in the same commit | deskcraft | H6, H7 scored; `SCENARIO_SIGNS` scored, closing D3a's register row; tag exists |
| **10** | **D13, D14, D15** — reverse stress, risk-model backtest, construction backtest | deskcraft | H1, H2, H5 scored |
| **11** | **D16 — readout and Paper 1**, then **tag CP-2**. Fill §8.1's blanks | deskcraft | H1–H9 all scored as written; Paper 1 sendable |
| **12** | **Write D17's pre-commit** — the mechanical cohort rule, the completeness filter derived from the method, the three-way comparison of §2.1, and H11 / H17 with the CI methods of §5.3 | deskcraft | Doc committed before any exposure is extracted |
| **13** | **D17, D18** — exposure extractor and the suitability gate | deskcraft + curvecast | H11, H13, H17 scored |
| **14** | **D21, D22 — and Paper 2.** Fill §8.2's blanks | deskcraft | H12a, H14a, H14b, H15, H16 scored; Paper 2 sendable |

**Row 0, stated in full 2026-09-09, because "fair access requires it" is not a reason.**
The SEC's access policy is not authentication and grants nothing: EDGAR needs **no account,
no API key and no registration**, and the filings are public domain. What the policy asks is
that automated traffic be **declared**, in the shape its own sample gives:

```
User-Agent: Sample Company Name AdminContact@<sample company domain>.com
```

That sample is an *institution plus a role address*, which is the tell — the header is a
**contact channel, not an identity check**. The policy's own sentences say what it is for:
"To ensure everyone has equitable access to SEC EDGAR content, please use efficient
scripting", and "Any request that has been identified as part of a botnet or an automated
tool outside of the acceptable policy will be **managed to ensure fair access for all
users**." Read the second one carefully: **the fair access being protected is everyone
else's, against this probe**, and "managed" is the euphemism for throttled or blocked. A
declared UA is how a script opts into being managed *by being contacted* rather than by
having its address range black-holed when it exceeds the published 10 requests/second.

It is enforced rather than advisory: undeclared traffic receives a 403 carrying the
"Your Request Originates from an Undeclared Automated Tool" page. **D23 makes zero
successful requests without it**, which is why this is row 0 and not a footnote in row 1.

**And it is the owner's call for a reason that is not squeamishness.** The standing rule in
this build is that the owner's email identifies them and is never sent to an unrelated
service in a header, URL or payload unless they ask — and this is *literally a header
carrying a name and an email*, sent to a federal agency whose web logs are federal records
under their own retention schedule. It cannot be retracted afterwards. What is disclosed is
bounded and worth stating precisely so the decision is made on facts: **a string in an
access log, beside the CIKs requested and the time**, for the few hundred requests D23's
twenty firms need. Not tied to a filing, not published, not indexed, not visible to other
EDGAR users. The SEC verifies none of it — but a false address defeats the entire
mechanism, which is reachability, so the choice is between two honest strings and not
between disclosure and anonymity.

**Row 2 named a number until 2026-09-09, and the number was wrong.** It read "stays
25/25", copied from D1's pre-commit, which recorded curvecast's count correctly *for
2026-08-31*. curvecast closed its remaining items on 2026-09-05 and the sweep has read
**39/39** since; D2's pre-commit records that run at 1008s. So the older document
(`PLAN_deskcraft.md` §8) was current and this newer one was stale — the opposite of the
way staleness usually runs, and the reason is that this row was written by copying rather
than by reading the run.

The fix is not to write 39/39 here. `PLAN_deskcraft.md` §8 already gave the argument:
*"a gate expressed as a stale number gets read as failing and then ignored"*, and the
count will move again — D23 lands in curvecast and will itself add gates. A **forward**
bar on a run that has not happened yet cannot name a count without pre-committing to what
curvecast will contain on that day. It can name the property: **no gate RED, exit 0**,
which is what `run_gates.py` documents its exit code to mean and is what the bar was
always trying to say. A SKIP never makes a run green, so the property is not weaker than
the count — it is the count with the arbitrary part removed.

**Blocked, deliberately:** aqrtp Milestone 2 until CP-1 (§9). **Annexed, deliberately:** D19 and
D20 until the core closes (§6.3).

---

## 11. What this amendment could still get wrong

In the shape §6 of the build order uses, because an amendment that only lists other people's
errors is not doing its job.

- **The blindness rule could be honoured in the letter and broken in the head.** Nothing stops a
  human reading a raw filing during the probe and forming a view about the effect size. The schema
  test constrains the artifact, not the analyst. The mitigation is that the probe's 20 firms are
  stratified and named in advance, so any impression formed is at least not a selected one — but
  this is a genuine residual and it is recorded rather than solved.
- **The structural read could pass the probe and fail in the cohort.** Twenty firms answering
  "the tag is present" does not establish that forty will, nor that the tag means the same thing
  across industries. P-5 is the partial defence; it is not a complete one.
- **H17 could be unfalsifiable in the direction that matters.** If the rates half fails — a
  factor-of-three wedge on rates too — §2.5 reads that as "the swap overlay is being missed". But
  a genuine economic wedge on rates would produce the same signature. Distinguishing them needs
  the tagged `DerivativeNotionalAmount` coverage count from P-2, which is why that count is in the
  probe rather than discovered later.
- **The freeze could be honoured by inflating packages instead of adding them.** A budget on the
  count is not a budget on scope, and D17 in particular is now carrying a three-way comparison
  where it used to carry a two-way one. The defence is that each package still ships as one commit
  with one pre-commit doc; if a package cannot, it has grown and must split — which spends budget
  and becomes visible.
- **CP-1 could be declared and not be real.** A tag is cheap. The test is the one-page write-up
  answering *what do I hold if everything stops here*, written for a reader who has not seen the
  plan. If that page cannot be written, the checkpoint has not been reached and the tag is a lie.
- **The other gates may be in M18's condition too.** One of four was found dead by running it. The remaining three — deskcraft `pytest`, curvecast `run_gates.py`, meip `lint-imports` — were run today and do produce verdicts, so the audit is complete for this repo. It has not been done for the *contents* of those suites: a passing test that asserts nothing is the same defect one level down.
- **The most likely failure remains the one M11 measures**, and this document barely dents it.
  Eight items of analysis were requested and delivered; the ratio of argument to source went up,
  not down, in the writing of it. The commit does carry source — but only M18's repair, which
  is a gate that should have worked since D1, not a package. **Nothing here has yet advanced the
  build. §6.2 is the line to hold, and D23 running is the only thing that discharges it.**
