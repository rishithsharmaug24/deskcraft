# A cost-aware multi-leg construction engine and its risk-model backtest

*Paper 1 of deskcraft, `AMENDMENT_A1` §7.2. **Rendered 2026-09-28, after the out-of-sample read, and
complete at CP-2.** Five of its nine hypotheses are verdicts of that read. The claims
table is rendered from the register by `deskcraft.readout`, and every figure is checked against the
package document that recorded it (D16, DD225–DD230). The engine describes a book's risk and never
advises on it.*

---

## Abstract

We build a cost-aware engine that turns a stated macro view into a multi-leg book of US fixed-income
and currency instruments, decomposes its risk, sizes it under an expected-shortfall budget, and
stresses it against dated history. Every fitted object, from the factor basis and the covariance to
the GARCH filter, is estimated on 1988–2014. The out-of-sample record is 2015-01-01 to 2025-12-31:
2,870 weekday sessions, of which 2,736 carry every series the tested books hold. Its power was
published before any row was read, and the owner authorised the read, not the code. Nine hypotheses
were registered with predicted verdicts, two of them predicted to fail. Paper 1's register holds twelve live rows: the nine hypotheses, two of them split in two, and `SCENARIO_SIGNS`. All twelve are scored: seven as predicted, three against their predictions, and two reported, having no prediction to meet.
The risk model's unconditional coverage holds at both 97.5% and 99% (Kupiec p 0.191 and 0.219), and
its exceptions cluster (independence p 0.0013), as predicted. Expected-shortfall sizing does not beat
equal weighting on Sharpe, as predicted, and the test could not have shown that it does. Both crisis
predictions fail. A window's own correlations moved the sizing by 65.8% of gross in 2020 and by 2.7%
in 2022. A Gaussian three-factor model understated the size of the book's P&L in 2022, by 3.3%, and
not in 2020.
The hand-built book, four priceable legs expressing one view, has an effective rank of 2.4103 under
Roy–Vetterli. Under whitening the same book scores 4.0 whatever its covariance, so one of our own
hypotheses could not fail, and we say which. The leg count is an output of a cost-aware stopping rule,
not an input: 0, 1 or 2 legs at all eight cells of the cost ladder. The grammar a view is written in
reaches at most 0.906494022 of an arbitrary view direction, at any cost and any conviction, and that
is the first of the limits we report.

## 1. What the engine does

A view is written in a closed grammar of six terms (D6), for example `LEVEL` up. The generator (D7b)
turns it into legs from an eleven-series pool of US zero-coupon and real yields. It adds a leg only
while the view it gains per unit of risk clears its cost per unit of risk, and it reports the answer at
every rung of a cost ladder rather than at one. The risk layer (D8, D9, D10) fits covariances on the
fit window. It decomposes expected shortfall at 97.5% into legs under Euler, splits each leg along the
view, and counts effective bets under three definitions that disagree. The sizing layer (D11) scales
every book to one budget, $1,000,000 of Gaussian expected shortfall, under rules that minimise tail
risk per unit of view and never against a return. The stress layer (D12, D13) replays dated windows and
asks which move of the market is the most plausible way to lose the budget. The backtests (D14, D15)
run the risk model and the construction on the eleven years the fit never saw.

## 2. The claims

<!-- claims table: rendered by deskcraft.readout.claims_table() -->
| Claim | Statement | Scored by | Predicted | Verdict |
|---|---|---|---|---|
| H1 | Risk model correctly calibrated | D14 | PASS | **PASS** |
| H2 | Exceptions independent | D14 | FAIL | **FAIL** |
| H3 | View fidelity: the book loads on the view's factor | D6 | PASS | **PASS** |
| H4 | Six-leg US book has ENB < 3.0; the book is neither US-only nor priceable, and ENB is undefined without a basis | D10 | none | withdrawn: H4a, H4b |
| H4a | US_CASH_BOOK's four priceable legs have Roy-Vetterli effective rank < 3.0 | D10 | PASS | **PASS** |
| H4b | The same book and covariance exceed 3.0 under at least one other basis of D10's ladder | D10 | PASS | **PASS** |
| H5 | ES-constrained sizing beats 1/N on Sharpe | D15 | FAIL | **FAIL** |
| H6 | Crisis correlations change sizing > 20% of gross | D12 | PASS | **FAIL** |
| H7 | 3-factor Monte Carlo understates crisis P&L | D12 | PASS | **FAIL** |
| H8 | Generated book beats hand-built on ENB; both < 3.0; the level clause cannot fail, because ENB <= the leg count and H9 predicts three or four legs | D10 | none | withdrawn: H8a, H8b |
| H8a | The generated book beats the hand-built US_CASH_BOOK on Roy-Vetterli effective rank, both in the same basis on the same covariance | D10 | PASS | **FAIL** |
| H8b | ENB divided by leg count, reported for both books in each basis of D10's ladder | D10 | none | **REPORTED** |
| H9 | Cost-aware stopping terminates below six legs | D7b | PASS | **PASS** |
| SCENARIO_SIGNS | SCENARIO_SIGNS reproduces on dated windows; under-determined, and D12 replaces it | D12 | none | **REPORTED** |
<!-- end of the rendered claims table -->

Paper 1's register holds twelve live rows: the nine hypotheses, two of them split in two, and `SCENARIO_SIGNS`. All twelve are scored: seven as predicted, three against their predictions, and two reported, having no prediction to meet.

## 3. What is scored, and what it says

- **H3 passes, thinly.** The reference book's dominant loading is `LEVEL`, at +46,989.92 dollars per
  basis point, as the view compiled from the thesis said. It leads the second term by 4.991%, and the
  terms it leads overlap: they count much of the same nominal duration through different directions.
- **H4a passes and H4b could not fail.** `US_CASH_BOOK`'s effective rank is 2.4103 under Roy–Vetterli,
  below 3.0. H4b asked for more than 3.0 under at least one other definition. The whitening rung
  returns the leg count, 4.0, for any covariance, so it passes by construction. Minimum torsion, the
  rung that can move, is 2.6567.
- **H8a is refuted.** The generated book's effective rank is 1.0898, against the hand-built book's
  2.4103. Fidelity to a one-factor view and diversification pull opposite ways, so the generator built
  what it was asked for. H8b reports rank over leg count: 0.6026 hand-built, 0.5449 generated.
- **H9 passes, and its margin belongs to the grid.** The stopping rule ends at 0, 1 or 2 legs at all
  eight cells, below the six it had to stay under. It was predicted to stop at three or four, and that
  prediction is wrong on the low side at every cell. The count flips between the 1× and 2× rungs,
  which is the pair the plan named as the trigger for calling a result a statement about costs.

The out-of-sample read, 2026-09-28, on 2,736 sessions carrying every series the tested books hold:

- **H1 passes, and the tail is fatter than the model says.** The Gaussian model on `US_CASH_BOOK`
  took 58 exceptions at 97.5% against 68.4 expected, and 34 at 99% against 27.4. Kupiec's p is 0.191
  and 0.219, and Acerbi–Székely Z2's is 0.538. A correct model fails this conjunction 11.5% of the
  time. Fewer exceptions than expected at 97.5% and more at 99% is the shape of a fat tail, and
  Acerbi–Székely Z1 rejects.
- **H2 fails, as predicted.** Christoffersen's independence p at 97.5% is 0.0013: the exceptions come
  in clusters. The Basel traffic light is yellow in the 250-session blocks opening in January 2020 and
  January 2022, and red in the block opening in January 2023. An EWMA variance scores better than the
  fixed covariance on the loss function fixed in advance, and the construction backtest's secondary
  figures use it.
- **H5 fails, as predicted, and says nothing.** ES-constrained sizing trails 1/N by 0.012 of Sharpe,
  p 0.82, against a minimum detectable difference of 0.154. Its Deflated Sharpe is 0.017. G, the view
  carried per unit of realised tail risk, favours the optimiser at +0.068 with a p of 0.0034. No claim
  is made from it: the test built for G was not registered, because its power was under one half.
- **H6 fails against its prediction.** A window's own correlations moved the constructed book's
  minimum-variance sizing by 65.8% of gross in 2020 and by 2.7% in 2022. It needed both.
- **H7 fails against its prediction.** The size of the constructed book's P&L exceeded the
  three-factor model's 97.5% quantile in 2022, by 3.3%, and reached 82% of it in 2020. It needed both.
  The book is short duration, so 2022's rising rates were a gain and 2020's falling rates a loss. The
  filtered historical simulation covered both.
- **`SCENARIO_SIGNS` is reported.** The hand-built book's legs moved −, −, −, + in 2020 and +, +, −, +
  in 2022 (the 2-year, the 10-year, the breakeven and the euro). No window is classified into the
  source's four scenarios.

Three results that no claim scored:

- **The diversifier is the largest risk.** The euro leg of `US_CASH_BOOK` is 47.7% of the book's
  expected shortfall of 1,946,957 dollars, and none of that share points along the view (D9).
- **The optimiser gets about as much view as equal weighting.** On the headline book it takes 4.0%
  more view per unit of budget than 1/N (D11), which is why H5's power at the plausible effect is
  small.
- **Reverse stress is the Euler decomposition on one covariance** (D13). The budget breach sits 2.3378
  sample sigmas out for every budget-scaled book. On other covariances it moves: `US_CASH_BOOK`'s
  budget loss is 1.5455 sigmas of the 2007–09 covariance. On the construction date the euro's P&L
  correlated 0.6056 with the rates legs', against 0.006 on the whole sample, so the diversifier was a
  second copy of the rates bet on the day the book was built.

## 4. How the read was scored

The joint registration fixed every rule before the read. **H1**: the risk model is calibrated iff
Kupiec's test holds at both 97.5% and 99% and Acerbi–Székely Z2 holds at 97.5%. Kupiec's power at 99%
against true exception rates of 1.5%, 2% and 3% was published as 0.668 / 0.991 / 1.000 at 2,760
sessions, and is 0.647 / 0.990 / 1.000 at the 2,736 the read found. A correctly specified model fails
this conjunction 11.5% of the time. **H2**: Christoffersen's independence test at 97.5%, predicted to
fail. **H5**: sizing beats 1/N on Sharpe, predicted to fail, and tested with a power of 8% at the
plausible effect, so either outcome is weak evidence. **H6 and H7** were read on the two out-of-sample
windows only, `NBER_2020` and calendar 2022. On the three DEV windows H6's change was 0.007 / 0.214 /
0.040 and H7 held in none, which is why the registration moved both off DEV. That removed in-sample
evidence against both predictions, and the record refuted both without it: over all five windows H6
holds in two and H7 in one, which the first rule, three of five, would also have scored as failing.

## 5. Limits

1. **The grammar reaches at most 0.906494022 of an arbitrary view direction**, at any cost and any
   conviction. A view the six terms cannot say is expressed at that cosine or less, and no leg in the
   pool raises it (DD138).
2. **H4b could not fail.** Its whitening rung returns the leg count for any book.
3. **H9's margin is a property of the grid.** 0, 1 or 2 legs at eight cells, under a bar of six.
4. **The generator is path-dependent.** Its headline book is a short 10-year outright, reached through
   a 30-year outright and a 10s30s spread whose 30-year DV01s cancel exactly, though the pool offered
   the 10-year as one leg. A greedy, cost-aware selection can pay more to reach a book one leg would
   have given (X26, D13).
5. **On one Gaussian covariance, reverse stress adds nothing to Euler.** Its distance to the budget is
   2.3378 for every budget-scaled book. What it adds comes from other covariances and from history.
6. **Held means frozen.** No carry, no roll-down, no FX differential. A future or a swap is carried as
   the DV01-matched cash instrument, and each leg names what that drops.
7. **Two tests are weak by design.** H1's conjunction fails a correct model 11.5% of the time, and H5
   has a power of 8% at the plausible effect. On the record H1 passed and H5 failed, and each is read
   against its number.
8. **The predictions are not information-blind.** The 2015–2025 path is public, and 2020 and 2022 are
   the windows because they happened.

## 6. Declines

1. **The cross-market leg.** The source structure's US-versus-Bund spread defers to a package that no
   row of the build order commissions. The owner declined that package: the budget is twenty-one, one
   in and one out (DD126). The foreign-curve licences it waited on were measured (`AMENDMENT_A5` §3).
   It is not built, and the six code sites that defer it are held to the register.
2. **Options and volatility.** Cboe's terms refuse derivative computation from its volatility indices
   without written consent, three of the eight inputs the options package named are not free at any
   route found, and the rates volatility indices are licensed (DD121). Paper 1 has no option leg.
3. **The credit leg.** The grammar's credit term reaches no tradeable series (DD124). The daily Moody's
   pair is admitted for results only, and the public-domain spread is monthly.
4. **A seventh grammar term.** Declined for version 1 (DD138). Its absence is limit 1.
5. **Commodities.** In Paper 2's crude arm only (DD127).

## 7. What the engine does not do

It holds no broker SDK, no credential, no order path and no network access, and a boundary test
enforces that as a capability rather than as a vocabulary. It reports risk, attribution and stress for
a stated book. It says nothing about whether to hold one.
