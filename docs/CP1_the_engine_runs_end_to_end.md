# CP-1 — the engine runs end to end

*Tagged 2026-09-28 at the commit that lands D12, D14 and D15 (`AMENDMENT_A1` §7.1). One page, and
one question: if everything after this stalls, what is held?*

## What exists

deskcraft is a paper-only risk engine for multi-leg interest-rate books. It never trades and holds
no broker connection. Given a macro view written in a closed grammar of six terms (the level of the
curve, its slope, its curvature, real against nominal, credit against rates, one market against
another), it does five things:

1. **Compiles the view** onto factors fitted on 1988–2014 only.
2. **Generates a book**: a greedy, cost-aware search over outrights and spreads, reporting how much
   of the view the book can reach. At any cost it reaches at most **90.65%** of an arbitrary view
   direction. That is the grammar's saturated cosine, 0.906494022, and the engine's headline limit.
3. **Sizes the book** under one tail-risk budget. The optimising rules are linear programs that
   minimise tail loss per unit of view, never against a forecast return.
4. **Attributes the risk** by Euler components and counts the effective number of independent bets.
5. **Stresses the book** against dated history and a filtered historical simulation.

The risk model and the construction were then tested **once**, on 2015–2025. That record was
fixed, and every rule scoring it written down, before anyone read a row of it. The owner authorised
the read in a written document that quotes the owner's instruction. The registration's fingerprint
was timestamped outside this machine first.

## What was scored

| Claim | Result |
|---|---|
| H3, the book loads on the view's factor | PASS |
| H4a, the reference book is under three effective bets | PASS, 2.4103 |
| H4b, it exceeds three under another basis | PASS, and it could not have failed |
| H6, crisis correlations move sizing by more than 20% of gross, in 2020 and in 2022 | **FAIL**: 66% in 2020, 3% in 2022 |
| H7, a Gaussian three-factor model understates the size of the crisis P&L, in 2020 and in 2022 | **FAIL**: exceeded in 2022 by 3%, not in 2020 |
| H1, the risk model is calibrated out of sample | PASS, with an 11.5% chance of failing even if correct |
| H2, its exceptions are independent | FAIL, as predicted: they cluster |
| H5, the optimiser beats equal weights on Sharpe | FAIL, as predicted, and the test had 8–11% power |

CP-1 was defined as H3, H4, H6 and H7 scored. H1, H2 and H5 landed in the same commit, because D14
and D15 read the record in the same step as D12. H8a (the generated book diversifies better than
the hand-built one) was refuted earlier, and H9 (cost-aware stopping) passed on a grid where it
could not have failed.

## What it shows

- **The Gaussian risk model counts its exceptions correctly over eleven unseen years, and gets
  their timing wrong.** The exceptions arrive in clusters, and the tail is fatter than the model
  says. A variance model that adapts (EWMA) scores better by the scoring rule fixed in advance.
- **Optimised sizing does not beat equal weights on Sharpe**, and no eleven-year record could have
  shown that it does. The difference it makes is to tail risk per unit of view. The test built for
  that claim was not registered, because its power was below one half.
- **The two crisis predictions each held in one window and failed in the other.** In 2020
  correlations moved the sizing by two-thirds of gross, and the book's loss stayed inside the
  Gaussian bound. In 2022 the size of its P&L broke the bound, and correlations hardly moved the
  sizing. The book is short duration, so 2022's rising rates were a gain, of 15.54m.

## What is not here

- **Paper 1** itself: the readout, D16, lands next and closes at CP-2.
- **The hedging layer**, Paper 2. The exposure extractor (D17) and the structure gate (D18) have
  landed. The hedge backtest (D21) and the funding path (D22) read the same record next.
- **Any claim about returns on capital.** The engine answers what the risk of a book is, and never
  whether to hold it.
