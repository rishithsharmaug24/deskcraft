# deskcraft: a risk engine tested once, on eleven years it had never seen

*A two-page summary. Rishith Sharma, September 2026.*

## What it is

deskcraft turns a view on interest rates, such as "US yields will rise", into a multi-leg book of
Treasury, inflation-linked and currency positions. It measures the book's risk, sizes it to a fixed
tail-risk budget, and stresses it against dated history. A second layer does the same for companies,
reading the exposures they disclose and testing the hedges a bank would offer against them.

deskcraft never trades and has no connection to a broker. It answers *"what is the risk of this
book?"* and never *"should anyone hold it?"*.

## What is unusual about it

Every model was fitted on 1988–2014 only. Before anyone looked at 2015–2025, the project wrote down
four things:

- every prediction;
- every test;
- every pass-or-fail rule;
- the statistical power of each test.

A fingerprint of all of it was submitted to an independent timestamping service (OpenTimestamps) at
10:40 UTC on 28 September 2026, and sealed in the Bitcoin blockchain at 11:33 UTC. By the author's
logs, the eleven unseen years were read exactly once, at 10:53 UTC.

Two predictions were registered as expected failures, and two tests were declared weak before the
read. Predictions that failed are reported as failures.

## Paper 1: the risk engine

The reference book was built on 24 December 2014 and held unchanged through 2,736 trading days:

- short $200m of 2-year Treasuries;
- short $60m of 10-year Treasuries;
- long $50m of 5-year inflation breakeven;
- short €75m against the dollar.

| Question | What the record said |
|---|---|
| Does the risk model count its bad days correctly? | **Yes.** At 97.5% it had 58 days beyond its limit against 68.4 expected. At 99% it had 34 against 27.4. Both counts are consistent with a correct model (p 0.19 and 0.22), and so is the expected-shortfall test (p 0.54). |
| Do its bad days arrive as a correct model's would? | **No, as predicted.** They cluster (p 0.0013), and the tail is fatter than the normal distribution assumes. The Basel traffic light turns yellow in 2020 and 2022 and red in 2023. An unregistered check made after the read reverses every position: the clustering at 97.5% is then not significant (p 0.089) and the light never turns red, so both depend on the direction of the book. |
| Does a model that adapts do better? | **Yes.** An exponentially weighted variance beats the frozen covariance on a scoring rule fixed in advance (p 1.5 × 10⁻⁸). A covariance calibrated on 2007–09, as stressed regulatory models are, was about four times too conservative: 18 bad days against 68.4 expected. |
| Where does the risk sit? | **In the diversifier.** The currency leg carries 47.7% of the book's expected shortfall, and none of that share relates to the view the book expresses. |
| Does optimised sizing beat equal weights? | **No difference could be shown** (Sharpe difference −0.012, p 0.82). This was predicted, and the test's power, published beforehand, was 8%. |
| Do crisis correlations change the sizing, and does a simple factor model understate crisis P&L? | **Each prediction held in one crisis and failed in the other.** Correlations moved the sizing by 66% of gross in 2020 and 3% in 2022. The P&L broke the model's bound in 2022, by 3.3%, and not in 2020. Both are scored as failures. |

Twelve claims were scored: seven as predicted, three against their predictions, and two reported
without a prediction. The engine's own ceiling is reported too. Its six-term view language can
express at most 90.65% of an arbitrary view direction, at any cost.

## Paper 2: hedging what companies say they are exposed to

The cohort is forty large US non-financial companies, chosen by a fixed rule from their 2014 annual
reports. The project did four things:

- read each company's disclosed exposure to interest rates, currencies and crude oil;
- measured, from share prices, how much of that exposure the market actually priced;
- priced the hedges a bank would offer against it;
- followed those hedges through 2015–2025.

The results:

- **Hedging the disclosed exposure over-hedges the measured one for 24 of 32 companies, as
  predicted, but mostly for an unflattering reason.** Share prices moved in ways that made the
  measured exposure zero or negative. The fit explains very little (median R² 0.016).
- **The predicted pattern across asset classes did not appear.**
- **A cost-minimising bank offer picks a leveraged structure every time**, and a suitability check
  refuses it. The paper says plainly that this result could not have come out otherwise.
- **Hedges sized to stated exposures can be very costly in a crisis.** ExxonMobil's crude hedge
  would have lost 541% of its operating cash flow in 2020 and 1,196% in 2022. GE's would have lost
  62% and 404%.
- **Held unchanged from 2015 to April 2024, the hedges removed almost nothing.** Each hedge was
  sized in 2014 from how the company's share price had moved, then left alone. For all 32 companies
  that could be scored, it removed less than half of the share-price risk, as predicted. That could
  hardly have failed: no hedge had worked well even in 2009–2014.
- **The prediction that the hedges would lose half their earlier effect failed.** It held for 21 of
  32 companies, where 70% was needed, and most of that count came from companies whose only stated
  exposure was interest rates, where the hedge had been fitted to noise.
- **Where a hedge did work, the plain forward did as well as the option structures.** On all seven
  such companies it kept at least 90% of what the best option structure achieved, as predicted.

## What it does not show

- **No trading edge, and no claim about returns.** deskcraft is a risk tool.
- **Held means frozen**: no carry, no roll-down, no rebalancing.
- **One market and one reference book.** A pre-registered replication on Japanese and Canadian
  government bonds over 2015–2025 is the next piece of work.
- **The predictions were not blind to history.** Everyone knows 2020 and 2022 happened. The
  author had also seen US Treasury data from these years in a separate project: a yield-curve
  forecasting model was validated on 2015–2018 and evaluated once on 2019–2026 before this
  registration. No part of that model is used here.

## How to check it

- **The code and its public-domain data** are in this repository. 203 of its 235 tests run on
  them. The other 32 need two files of Moody's credit-spread data, which Moody's licence does not
  allow anyone to redistribute (see `PUBLIC_COPY.md`).
- **The registration's fingerprint and timestamp proof** are in `prereg/`, with the commands that
  show the rules scored are byte for byte the rules registered.
- **Analyses made after the read**, unregistered, are in `after_the_read/`: the two scripts behind
  online Appendix D of Paper 1, and their output.
- **The full papers** are `docs/PAPER1_the_engine_and_its_backtest.md` and
  `docs/PAPER2_hedging_measured_exposure.md`.
