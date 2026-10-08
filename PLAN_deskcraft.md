# deskcraft — a paper-only macro risk engine

> **Status:** scoped 2026-08-31; **D1 closed 2026-08-31**, **D2 closed 2026-09-05**,
> **D3a closed 2026-09-11**.
> The scaffold, the inverted boundary test and the book types are in and green — **22 bars**,
> `docs/PRECOMMIT_deskcraft_d1_scaffold.md` and `docs/PRECOMMIT_deskcraft_d2_book_types.md`.
> D3a added the guards and registers — one policy per Python file with the strict one as the
> default, a runtime network refusal under test, `FitWindow`, the claims and source registers
> and the package budget — in `docs/PRECOMMIT_deskcraft_d3a_guards_and_registers.md`; the suite
> is **41 tests**.
> **curvecast item 28 closed 2026-09-05, so the block on the factor covariance and the
> scenario library is lifted.**
>
> **§7 below is superseded.** A larger build order was approved on 2026-09-05 and runs
> **D2–D16**: it keeps every package here and inserts the data panel, the view language, the
> leg generator, the ES/CDaR sizing step and the two validation packages that are the actual
> product. The mapping from old row to new is given there. §1–§6 and §9 are unchanged and
> still govern.
> **Sibling to:** `c:\Users\rishi\curvecast` (consumed one-way, as a library) and
> `c:\Users\rishi\meip` (consumed one-way, never modified).

---

## 1. Why this repo exists, and why it is not curvecast

curvecast's constitution ends its output at explanation and forecast: *"No trade
recommendations, signals, target weights, or position sizes. Ever. Anywhere."* That is not a
style preference — it is machine-enforced by `tests/test_curvecast_boundary.py`, which
introspects every pydantic model and refuses a field whose name contains any of
`notional`, `direction`, `position`, `size`, `weight`, `allocation`, `leverage`, `side`,
`order`, `signal`, `trade`. `EXEMPT_FIELDS` is `{}` and has never been non-empty; on three
separate occasions a package renamed its own field rather than add an exemption.

A risk engine cannot be written under that rule. Portfolio VaR is a function *of positions*.
There is no version of component VaR that does not carry a notional. So the choice was
between amending a contract that has never been amended, or building the risk engine
somewhere else. **This is somewhere else.**

curvecast is not modified by this repo. The import edge is one-way and outbound only.

---

## 2. What this is, stated honestly, before any of the interesting parts

**This is a craft artifact. It is not a trading system, and it is not capable of becoming
one.** Three separate facts make that true, and none of them is a matter of effort:

1. **The strategy question was already tested and answered NO.** The RATES-X power audit ran
   138 configurations across seven candidate families on GSW data before building anything.
   Nothing cleared the bars. Curve RV died on costs (best gross Sharpe 0.72, net −1.59;
   breakeven multiple never reaches 1.0× against a 2.0× bar). Per-CUSIP RV is real and
   smaller than the cost of touching it — ~10 bp of amplitude against a ~60 bp round trip.
   Duration timing ties the passive ladder in the US and is negative in India on measured
   spreads.
2. **The regulatory wall is independent of the statistical one.** RBI's *Rupee Interest Rate
   Derivatives* Master Direction (11 Dec 2025) §5.4(i) makes retail INR IRD hedging-only, and
   §5.2(ii)'s reclassification route needs ₹500 cr net worth. LRS prohibits remittance of
   margin to overseas exchanges, which closes UST futures and closes shorting abroad.
3. **The worked example is an institutional book.** A $200m two-year futures leg is not a
   retail position by three orders of magnitude. Sizing it is an exercise in understanding how
   a desk thinks, not a plan.

So the deliverable is *fluency*: the ability to take a macro thesis, express it as a
multi-leg structure, decompose that structure's risk correctly, stress it against dated
history, and say which leg is actually carrying the bet. That is a demonstrable skill and it
is the thing this repo produces evidence of.

**What this repo will never contain:** broker credentials, an order path, a live market
connection, a scheduler, or any function whose return value is intended to be executed.
Paper only, and the absence of an execution path is structural rather than promised.

---

## 3. The boundary this repo keeps

curvecast's boundary does not transfer — `Direction` and `Notional` are the subject matter
here. A different and narrower one applies:

| Allowed | Forbidden |
|---|---|
| Hypothetical books with notionals and directions | Any broker SDK, API key, or credential |
| Component / marginal VaR, risk contributions | Any function that places, stages, or schedules an order |
| Correlation and factor decomposition | Any live or streaming market connection |
| Dated historical scenario replay | Any claim of realised or expected return on capital |
| Sizing *arithmetic* on a stated book | A recommendation to hold the book it sizes |

The distinction that does the work: **this repo answers "what is the risk of this book?" and
never "should you hold it?"** A risk decomposition of a hypothetical structure is a statement
about arithmetic. It becomes advice only when someone asserts the structure is worth holding,
and that assertion is not this repo's output.

Inherited unchanged from curvecast: free data only; secrets via env only; never commit
`.env`, `data/`, or `*.duckdb`; never circumvent an anti-bot control; tests never touch the
network; one commit per work package with the pre-commit doc written first.

---

## 4. What it consumes, and from where

Nothing here re-implements what already exists. Three dependencies, all one-way:

- **`meip.rates.cascade.par_bond_duration_convexity`** — DV01 and convexity per leg. This is
  already the correct transform and the plan's relation 7 says so; the "expected P&L per 10 bp"
  column of any leg table is this function, not a fresh derivation.
- **`meip.rates.simulate.tenor_shifts`** — maps a shock scenario to a curve shift. The
  scenario library feeds this rather than a new simulator.
- **curvecast item 28 (WP-R1)** — the factor covariance, the PCA basis, and the dated
  scenario library. **This is the shared spine.** deskcraft applies those objects to a book;
  curvecast computes them about the curve. The split is exactly the boundary: the covariance
  is a fact about the world, the book is a hypothesis about what to hold.

deskcraft therefore cannot start in earnest before curvecast item 28. It can start its own
scaffolding and its VaR arithmetic on a synthetic covariance, and swap in the real one.

---

## 5. Methodology, with the citations that fix it

### 5.1 Risk decomposition — Euler, not intuition

Parametric VaR is homogeneous of degree one in the position vector, so by Euler's theorem the
sum of position × marginal VaR equals total VaR exactly, with **no residual**. That is the
whole reason component VaR is the right object and ad-hoc "percent of notional" attributions
are not.

- **Marginal VaR** — the partial derivative of portfolio VaR with respect to one position.
  "How much more risk does one more dollar here add?"
- **Component VaR** = position × marginal VaR. Additive, sums to the total.
- **Euler allocation** — Tasche, *Capital Allocation to Business Units and Sub-Portfolios: the
  Euler Principle* (arXiv 0708.2542).

This is what answers *"no single factor dominates"* precisely. The naïve reading of a six-leg
table is that risk is spread across six things. The component-VaR reading routinely shows one
leg carrying most of it.

### 5.2 Diversification — effective number of bets, not leg count

The premise is Litterman & Scheinkman, *Common Factors Affecting Bond Returns* (Journal of Fixed Income 1, 1991, 54–61): three factors — level, slope, curvature — explain **>96%** of the variation in US Treasury returns. Everything below follows from that number being large.

- Meucci, *Managing Diversification* (SSRN 1358533) — the diversification distribution and
  the **effective number of bets**, defined as the exponential entropy of the risk
  contributions of *uncorrelated* factors.
- Meucci, Santangelo & Deguest, *Risk Budgeting and Diversification Based on Optimized
  Uncorrelated Factors* (SSRN 2276632) — **minimum-torsion bets**, which fix the main defect
  of the PCA version: principal components are statistically uncorrelated but need not
  correspond to anything an investor recognises, whereas minimum-torsion factors stay close to
  the original assets while being uncorrelated.

**The expected finding, pre-registered here so it cannot be claimed as a discovery later:**
a curve-heavy multi-leg structure has an effective number of bets **substantially below its
leg count**, because the first three principal components of the zero curve explain the
overwhelming majority of variance in changes. Legs that are separately motivated — a
front-end policy leg, a long-end supply leg, a cross-country spread leg — are largely the
same two bets wearing different names.

### 5.3 Stress — dated replay first, hypotheticals second and labelled

Industry practice combines three kinds, and the failure mode of each is known:

- **Historical replay** — 1994, 1998 LTCM, 2008, 2013 taper, 2020, 2022. Cheap, defensible,
  and its limit is that it assumes the next crisis resembles a previous one. 2020 had no
  precedent in *speed*; 2008's credit contagion is invisible to a 1987-style equity shock.
- **Stylised shocks** — parallel ±100 bp, steepener, flattener, twist.
- **Hypotheticals** — allowed, but **labelled as hypothetical on the object**, because a
  hypothetical calibrated after seeing the book is an argument rather than a test.

**The load-bearing warning, and the one the six-leg example most needs:** *pair-correlation
assumptions must be stressed, because legs that look independent collapse into one in a
shock.* A structure whose diversification rests on a normal-times correlation matrix is
undiversified precisely when it matters. Every scenario must therefore be run with **realised
crisis-window correlations**, not the full-sample matrix.

### 5.4 Reverse stress testing

Rather than "what does 2008 do to this book?", ask **"what is the smallest, most plausible
joint move that breaches the loss tolerance?"** This finds the structure's actual weak axis,
which is frequently not the one the thesis is about. Regulator-standard (Basel, PRA) and
under-used outside banks.

---

## 6. The worked example

The reference fixture is a six-leg US-rates/FX/vol structure expressing a "fewer cuts than
priced, plus fiscal-driven term-premium repricing" thesis: short 2Y, short 10Y, long 5Y
breakevens, short EUR/USD, long 10Y calls, short US-vs-Bund 10Y spread.

It is a good fixture precisely because it is **articulate and plausible**, which is what makes
its risk structure worth decomposing rather than dismissing. Three things the engine should be
able to say about it, none of which are visible from the leg table:

1. **Legs 1, 2 and 6 are not three bets.** All three are US curve exposure; under a PCA of
   changes they load mostly on level and slope. The effective number of bets for the whole
   structure will land well below six.
2. **The leg 1 / leg 2 distinction is relation 18, and it is not cleanly measurable.** The
   structure separates "policy expectations" (leg 1) from "term premium repricing" (leg 2).
   curvecast item 17 measured that no free PIT-clean expectations/term-premium decomposition
   exists before 2016 — Kim–Wright is a re-estimated model graded **P3** below its 2016
   archive floor, with **6,099 of 6,099** DEV-era observations differing from today's vintage.
   **So this structure's central distinction cannot be backtested PIT-cleanly before 2016.**
   That is a real limit on the thesis, discovered independently of it.
3. **Leg 5 is doing something different in kind.** Options are the only leg with convex payoff;
   in a linear VaR framework its risk is understated by construction. It needs its own
   treatment (delta-gamma at minimum), and a scenario grid rather than a covariance.

---

## 7. Build order

Each is a work package under the inherited discipline: pre-commit doc first, bars fixed before
the run, one commit.

| # | Package | Depends on | Deliverable |
|---|---|---|---|
| **D1** | Repo scaffold + the boundary test | — | **CLOSED 2026-08-31.** `pyproject.toml` with three import contracts, an empty `deskcraft` package so the guard is live before there is anything to guard, and the *inverted* boundary test — **9 bars, C1–C9**. The ban is on **capability**, not vocabulary (DD1): no egress, no execution, no credential read, and no broker SDK reached — asserted about this repo rather than about this machine, since `kiteconnect` is installed here for an unrelated one. Half of curvecast's boundary ports verbatim (the imperative phrases) and half cannot port at all (the field tokens), and which half is which is recorded (DD4). See `docs/PRECOMMIT_deskcraft_d1_scaffold.md` |
| **D2** | Book and leg types | D1 | **CLOSED 2026-09-05.** Frozen dataclasses; `Direction`/`Notional` live here and nowhere else, asserted by a scan (C10). Immutability is checked by **hashability**, because `frozen=True` does not stop a mutable field (DD9). Components are **signed**, so relative value is representable at all, and `structure` is derived from them rather than declared (DD16); a balanced spread must name its neutrality basis and an unbalanced one must not (DD17, an iff); a cross-currency instrument must state `fx_hedged`, with no default (DD18). Every kind maps to exactly one `AssetClass` (DD19). The §6 structure is carried in full, re-expressed from futures to cash with what that drops recorded on the object (DD12), and its source's scenario table is pre-registered as a **sign matrix** for D12 to score (DD20) — which already shows the short EUR/USD leg carrying a sign pattern identical to the short 2Y, by the structure's own reasoning. **13 bars, C10–C22.** See `docs/PRECOMMIT_deskcraft_d2_book_types.md` |
| **D3** | DV01 / convexity per leg | D2 | Wraps `meip.rates.cascade.par_bond_duration_convexity`. Reproduces the fixture's "P&L per 10 bp" column from first principles, or explains the difference |
| **D4** | Covariance + component VaR | D3, curvecast 28 | Marginal and component VaR under Euler; the additivity identity is a **unit test**, not a claim |
| **D5** | Effective number of bets | D4 | PCA and minimum-torsion versions; report **both**, since they disagree and the disagreement is informative |
| **D6** | Scenario replay | D4, curvecast 28 | Dated historical windows with **crisis-window correlations**, never full-sample |
| **D7** | Reverse stress | D6 | Smallest plausible breach of a stated loss tolerance |
| **D8** | The readout | D5, D6, D7 | One page describing a book's risk. **Describes; never recommends** |

**On the initialisation, and why it is not D1.** `git init` was done ahead of D1 and kept
separate from it. It carries no bar — D1's bar is the *inverted boundary test passing*, and an
empty git directory gates nothing. What it buys is that this spec, which curvecast item 28 is
now scoped against, stops being a single unversioned file with no history and no recovery; and
that the inherited rule *never commit `.env`, `data/`, or `*.duckdb`* has something enforcing
it from the first commit rather than from whenever code first lands. **D1 remains OPEN.**

**On sequencing.** Nothing here is a prerequisite for curvecast's sealed run, and D4 and D6
cannot start before curvecast item 28 delivers the factor covariance and the scenario library.
D1–D3 are blocked on nothing; what holds them is priority, since curvecast item 27 is the
terminal gate and this repo is off that critical path. A scheduling decision, recorded so it
is not later mistaken for a blocker.

*(Updated 2026-08-31. This note previously said starting D1 would compete with curvecast
item 18 for attention. Item 18 closed the same day at `aa0f61c`, so it no longer would, and
D1 was built. The original reasoning is left visible rather than deleted: the argument was
about scheduling and the schedule changed, which is a different thing from the argument
having been wrong.)*

---

## 8. Gates

```bash
pytest -q                                   # incl. the inverted boundary test
lint-imports                                # 2 kept, 0 broken. Needs PYTHONPATH=src and an
                                            # interpreter carrying import-linter. The LLM-edge
                                            # ban is NOT here: import-linter cannot express a
                                            # dotted external module, so it is C23 in
                                            # tests/test_deskcraft_boundary.py.
                                            # Corrected 2026-09-09 -- this gate had never once
                                            # produced a verdict. See AMENDMENT_A1 M18.
cd c:/Users/rishi/curvecast && python scripts/run_gates.py   # must stay 39/39 green
cd c:/Users/rishi/meip && uv run --no-sync lint-imports      # 6 kept, 0 broken
```

curvecast's own gates are part of deskcraft's gate set, because the one failure mode that
matters most here is this repo quietly reaching back into curvecast and relaxing something.
`EXEMPT_FIELDS` staying `{}` is the specific thing to watch — and since D1 it is watched
**from here**, by `test_curvecast_exemptions_are_still_empty` (C9), which parses curvecast's
boundary file rather than importing it. The check belongs on this side: the repo most likely
to make relaxing that constant look reasonable is the one whose existence it caused.

*(The count read 23/23 when this plan was written and 25/25 after D1 corrected it. curvecast
closed its remaining items on 2026-09-05 — all 33 are now shut — and the sweep is **39/39,
0 failed, in 1008s**, with `meip:untouched` reporting `unmodified`. Corrected again as part of
D2, for the reason D1 gave: a gate expressed as a stale number gets read as failing and then
ignored. The number will keep moving, which is the argument for reading it off the run rather
than off this file.)*

---

## 9. What would make this repo wrong

Recorded now, so it is not rationalised later:

- **If it ever produces a number someone acts on.** The engine sizes hypotheticals. The moment
  a readout is used to place a trade, every disclaimer in §2 has failed and the RATES-X
  138-trial ledger applies to whatever claim is being made.
- **If the covariance is fitted on the window it is stress-tested against.** Crisis-window
  correlations must come from the crisis window; using full-sample correlations to "stress"
  a crisis is circular.
- **If leg 5's convexity is handled linearly** and the tail is reported as if it were
  understood.
- **If the effective-number-of-bets result is quietly dropped** because it is unflattering to
  a structure someone likes. It is the most likely finding to be inconvenient and the most
  important one to publish.
