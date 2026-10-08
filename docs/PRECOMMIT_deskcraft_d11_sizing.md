# D11 — sizing under the risk budget

*Written 2026-09-25, at `d5f5861`, after D10 closed. Bars and predictions fixed before the run; §9 is
written after it.*

`BUILD_ORDER_D3_D16.md` §4: *"Rockafellar–Uryasev CVaR as a linear program; Chekhlov–Uryasev–
Zabarankin CDaR. Benchmarks: 1/N, ERC, min-variance, max-diversification."* D11 scores no claim and
owes no carried item. It is the sizing D15's H5 compares against 1/N, so what it defines here is
what H5 will mean.

---

## 1. What D11 builds

`src/deskcraft/sizing.py`. A set of legs, each at a **unit** size, is given non-negative multipliers
`w` by one of six rules; the resulting book is then scaled to the budget.

| Decision | Content |
|---|---|
| **DD156 — the objective is the view, never a return** | This engine states no expected return (its boundary). The two optimising rules therefore **minimise tail risk per unit of view exposure**: subject to Σ wᵢvᵢ = 1, where vᵢ is leg i's P&L per basis point of the compiled view direction (D9's t̂), and w ≥ 0. Min-variance is the Gaussian form of the same problem. Max-diversification, ERC and 1/N take no view input and are the benchmarks. |
| **DD157 — units** | A generated leg's unit is **one dollar of gross DV01**, D7b's convention, so 1/N is equal gross DV01, as the stopping rule already treats legs. A hand-built leg's unit is its **stated notional**. |
| **DD158 — one budget, one scale** | Every sized book is scaled so its **primary** measure, Gaussian ES at 97.5% (DD146), equals `RISK_BUDGET_ES = 1,000,000` USD. The number is a unit and cancels from every comparison. Historical ES and CDaR are reported beside it at that scale. |
| **DD159 — the two linear programs** | **Rockafellar–Uryasev (2000):** minimise ζ + Σuₜ/((1−α)T) over w, ζ and u ≥ 0 with uₜ ≥ −Σᵢwᵢpᵢ,ₜ − ζ, on DEV's daily leg P&L. **Chekhlov–Uryasev–Zabarankin (2005):** the same over drawdowns, with yₜ ≥ cₜ(w), yₜ ≥ yₜ₋₁ ≥ 0 and zₜ ≥ yₜ − cₜ(w) − ζ, where cₜ is cumulative P&L. α = 0.975 for both. Solved by SciPy's HiGHS. |
| **DD160 — the benchmarks** | **1/N:** w = 1. **ERC:** Spinu's (2013) convex form, whose optimum equalises Euler contributions with every w > 0. **Min-variance** and **max-diversification** (Choueifaty–Coignard 2008): long-only quadratic programs on the leg P&L covariance. |

`scipy` joins `pyproject.toml`'s dependencies and `ENGINE_IMPORT_ROOTS`: a linear program needs a
solver, and a hand-rolled simplex would be a second implementation of a standard routine. A solver
is not a capability any of the six bans reaches.

**Scored on three sets of legs, all DEV:** D7b's headline book (two legs, unit gross DV01), the
six-leg book at a 10 bp view, and `US_CASH_BOOK` at stated notionals.

---

## 2. Carried items

**X7** — discharged: no prediction's subject is produced by its own check. **X15** — discharged:
D11 registers no threshold. **X16** — discharged: none stated.

---

## 3. Bars

| Bar | Holds |
|---|---|
| **C153** | The R-U LP's optimum equals the historical ES computed directly on its weights; the CDaR LP's equals the directly computed CDaR. |
| **C154** | Optimality: on the two-leg book, a brute-force grid over the weight ratio finds no lower CVaR per unit view than the LP. |
| **C155** | ERC's Euler contributions are equal; max-diversification's ratio exceeds 1; min-variance is no worse than any other rule on variance per unit view. |
| **C156** | DD158: every rule's book has Gaussian ES equal to the budget, and view exposure is reported per unit budget. |
| **C157** | The measured table for the three leg sets, pinned. |

`MODULES` gains `deskcraft.sizing`.

---

## 4. Predictions

| | Prediction |
|---|---|
| **P1** | C153 holds to 1e-8 relative, both programs. |
| **P2** | C154: no grid point beats the LP. |
| **P3** | On `US_CASH_BOOK`, R-U and min-variance put **zero** weight on `eurusd`, which has no view exposure and adds risk; 1/N and ERC do not. |
| **P4** | On the headline book, min-variance and R-U agree on the first leg's weight share to within **5%**: fat tails move the level, not the hedge ratio. |
| **P5** | ERC gives the higher-risk leg the smaller multiplier on every set. |
| **P6** | Suite 160 → **165**. |

---

## 5. What this could still get wrong

1. Minimising risk per unit of view is one reading of *sizing under the risk budget*. The other,
   maximising view subject to the budget, is the same problem scaled, so nothing is chosen between
   them; but a reading that sized for **return** is refused by the boundary, not by argument.
2. CDaR on a static book over 2003–2014 is dominated by the rates trend of those years. It is
   reported, and its sensitivity to the path is the reason it is not primary.
3. The historical programs see 2,997 days, of which 75 form the 97.5% tail.

---

## 9. Result

*Written after the run, 2026-09-25. Suite 160 → **165**. The two generated leg sets see all of DEV
(6,734 days, their series are the nominal zeros); `US_CASH_BOOK` sees 2003 onward (2,997).*

| | Prediction | Outcome |
|---|---|---|
| P1 | Programs equal direct arithmetic, 1e-8 | **HELD** — agreement to about 1e-13 on all three sets |
| P2 | No grid point beats the program | **HELD** — 2,001 ratios on the headline book |
| P3 | R-U and min-variance give `eurusd` zero weight | **MISSED** — 4.0% and 1.4%. The euro has no view exposure and still takes weight, because its small negative correlation with the rates legs makes a little of it a hedge |
| P4 | Min-variance and R-U within 5% on the headline book | **HELD** — 0.4411 against 0.4403 |
| P5 | ERC gives the riskiest leg the smallest weight | **HELD** on all three; the full ordering is strictly inverse on two |
| P6 | 165 | **HELD** |

| Headline book, at 1m ES | weight shares | view exposure, USD/bp | historical ES |
|---|---|---|---|
| R-U CVaR | 0.440 / 0.560 | 27,354 | 1,112,420 |
| min-variance | 0.441 / 0.559 | 27,354 | 1,112,438 |
| 1/N | 0.500 / 0.500 | 26,306 | 1,115,458 |
| ERC = max-div | 0.371 / 0.629 | 19,912 | 1,217,336 |
| CDaR | 0.407 / 0.593 | 26,173 | 1,118,677 |

**9.1 What this means for H5 before D15 exists.** On the headline book the optimiser buys **4.0%
more view per unit of budget than 1/N** (27,354 against 26,306), and the ES of the difference
between the two books is **0.28 of the budget**. They are not the same book. That is the quantity
step 4's power check needs, and it is recorded here as an input, not a verdict.

**9.2 ERC and max-diversification coincide on two legs**, as they must: with two assets both
equalise risk contributions. Their view exposure is the lowest because neither is told what the
view is.

**9.3 CDaR on a static short-duration book is the rates trend.** Yields fell through DEV, so every
short-duration book draws down by tens of millions against a one-million daily ES. Reported, never
primary, as §5 item 2 said.

*Next free ids: **C158 / DD161 / X26**.*
