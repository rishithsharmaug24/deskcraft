# Hedging measured exposure: an end-to-end test on public filings

*Paper 2 of deskcraft, `AMENDMENT_A1` §7.2. **Rendered 2026-09-29, after D21's read, and complete.**
D17, D18, D21 and D22 have scored, and nothing awaits the out-of-sample record. The claims table is
rendered from the register by `deskcraft.readout`, and every figure is checked against the package
document that recorded it (DD241). The layer describes a company's risk and never advises on it.*

---

## Abstract

A company's annual report states what it is exposed to: debt that reprices with short rates,
revenue earned in foreign currencies, crude it purchases or produces. We read those statements
from the 2014 filings of forty large US non-financial companies, chosen by a rule fixed before any
filing was opened. We measure from weekly share prices how much of each stated exposure the market
priced, as k, the multiple of the stated exposure that a variance-minimising hedge holds. We price
the hedges a bank would offer on the stated exposure and refuse, by type, any that obliges the
company to transact more than it has. Then we hold each hedge from 2014-12-24 through the years
the fit never saw. Paper 2's register holds eight live rows, H14 having been split in two before any number existed. All eight are scored: five as predicted, two against their predictions, and one not performed, refused by name.
Disclosed exposure over-hedges measured exposure for 24 of 32 evaluable firms, as predicted, but
mostly because the market's own loadings put k at or below zero. The asset-class pattern we
predicted for the gap between stated and measured exposure does not appear. The hedge a cost
minimiser picks is a leveraged one at every volatility, and that claim could not have failed.
Held out of sample, the hedges removed almost nothing: each of the 32 removed less than half of its
firm's weekly value variance, and none had removed half even in sample. The prediction that they
would lose half their in-sample effectiveness fails, at 21 of 32 against the 70% it needed, and most
of its count is noise on firms with only a rates leg. Where a hedge could be resolved, the plain
forward kept at least 90% of the best option structure's variance reduction, on 7 of 7 firms. Both
case clients with large stated exposures saw their linear hedges draw down by more than a quarter
of trailing operating cash flow in 2020 and in 2022. ExxonMobil's drawdowns were 541.18% and 1,195.55% of it, and GE's
62.14% and 404.21%. That was close to decided before the read.

## 1. What the layer does

The exposure extractor (D17) reads each firm's Item 7A market-risk disclosure and its XBRL facts
into a **stated** exposure: floating-rate debt as a one-year rate leg, foreign revenue by currency,
crude by the barrels a filing names. It then regresses the firm's weekly value change on each
stated leg's weekly P&L over 2009–2014, and k is the result: the **measured** exposure as a multiple
of the stated one. The structure grammar (D18) prices five hedges on one exposure (a forward, a
bought option, a zero-cost collar, a participating forward and a 2:1 ratio forward) and refuses by
construction any structure whose worst case obliges more than the stated flow. The hedge backtest
(D21) holds each firm's k-sized hedge through 2015 onward and asks how much of its weekly value
variance the hedge removes. The funding path (D22) marks three case clients' full stated hedges
daily through two crises and sets the drawdown against their operating cash flow.

## 2. The claims

<!-- paper 2 claims table: rendered by deskcraft.readout.claims_table(paper_two_claims()) -->
| Claim | Statement | Scored by | Predicted | Verdict |
|---|---|---|---|---|
| H11 | A hedge sized off disclosed exposure over-hedges vs one sized off measured exposure, by > 30%, for >= 70% of the cohort | D17 | PASS | **PASS** |
| H12a | The cheap linear structure captures >= 90% of the complex one's variance reduction | D21 | PASS | **PASS** |
| H13 | Unconstrained cost minimisation selects a leverage > 1 structure the gate refuses | D18 | PASS | **PASS** |
| H14 | OOS R^2 < 0.5 and < half its in-sample value; the first clause is implied by the second | D21 | none | withdrawn: H14a, H14b |
| H14a | OOS Ederington hedge-effectiveness R^2 < 0.5, for >= 70% of the cohort | D21 | PASS | **PASS** |
| H14b | OOS Ederington R^2 < half its in-sample value, for >= 70% of the cohort | D21 | PASS | **FAIL** |
| H15 | Crisis-conditional hedge effectiveness is under half the unconditional value, for >= 60% of the cohort | D22 | PASS | **NOT_PERFORMED** |
| H16 | Peak hedge-leg mark-to-market drawdown exceeds 25% of trailing operating cash flow for >= 1 case client; an existence claim | D22 | PASS | **PASS** |
| H17 | Structural-to-measured exposure ratio has cohort median > 2.0 for FX and commodity and < 1.5 for rates | D17 | PASS | **FAIL** |
<!-- end of the rendered paper 2 claims table -->

Paper 2's register holds eight live rows, H14 having been split in two before any number existed. All eight are scored: five as predicted, two against their predictions, and one not performed, refused by name.

## 3. What is scored, and what it says

- **H11 passes, for a reason it did not name.** 24 of 32 evaluable firms carry a measured exposure
  more than 30% below the stated one, 0.750 against a bar of 70%. The median k is −9.17. Twenty-two
  of the 24 count because k is at or below zero: between 2009 and 2014 share prices rose with the
  one-year yield and with a falling dollar, and a regression with no market factor measures that
  co-movement. Only two are the over-hedge the claim describes, a real exposure smaller than the
  stated one. On the 18 firms with a currency or crude leg the share is 0.611. On operating cash
  flow in place of equity the claim fails, at 0.625.
- **H17 fails.** The claim was that the stated-to-measured ratio is large for currency and crude,
  where pass-through and operational hedging absorb exposure before it reaches returns, and small for
  rates. The currency and crude median is 1.55, not above 2.0. The rates median is infinite, because
  22 of 25 rates k are negative. Currency alone is 0.130: measured far above stated.
- **H13 passes, and could not have failed.** An unconstrained minimiser of what a quote sheet shows,
  net premium less the improvement over the forward, picks the 2:1 ratio forward for every case
  client at every volatility. By put–call parity it is the only structure on the menu that beats the
  forward at zero premium. For GE at the construction date's volatility it improves the capped rate
  by 7.43bp, $57.9m a year, by selling a floor on $155.78bn, against a bought cap costing $83.7m. The
  suitability gate refuses it because its worst case obliges twice the exposure. **The leveraged pick
  is a property of the objective, not of the market.**
- **H16 passes, as it was reported before the read.** Four of six client-windows exceed a quarter of
  trailing operating cash flow. ExxonMobil's hedge, dominated by $244.16bn of stated crude
  purchases, drew down by 541.18% of that cash flow in 2020 and 1,195.55% in 2022, and GE's by
  62.14% and 404.21%. AT&T's stated exposure is $20m, and its hedge never came near the threshold.
  An existence claim on three clients needed one, and the numbers at the construction date said it
  would come.
- **H15 is not performed.** The one admitted daily equity route serves the last 100 sessions only,
  so no daily return reaches the fit years, and the claim is refused by name rather than scored on a
  weaker proxy.

## 4. What D21 found

D21 held each firm's k from 2014-12-24 and measured Ederington effectiveness, one minus the hedged
over the unhedged variance of weekly value, over the verdict weeks 2015-01-01 to 2024-04-05: 483
weeks for each of the 32 evaluable firms. What each claim could say was fixed before the read. Every
in-sample R² was below 0.40, with a median of 0.016, and a hedge fitted on noise counts toward H14b
0.74 to 0.86 of the time with no decay at all. Under no decay, H14b was expected to reach two-fifths
to three-fifths of the cohort.

- **H14a passes, and could not have failed in practice.** All 32 of 32 held hedges removed less
  than half of their firm's weekly value variance. The best was ConocoPhillips', at 0.4075. Every
  firm was already below one half in sample, so the pass says there was no clean hedge to lose,
  never that one decayed. The median effectiveness out of sample is 0.0003, and 16 of the 32 held
  hedges added variance rather than removing it.
- **H14b fails, against its prediction, and its count is mostly noise.** It needed 70% of firms to
  lose half their in-sample effectiveness and found 21 of 32, 0.656. Thirteen of the fourteen
  rates-only firms count, as a hedge on noise would, at about three in four under no decay. On the
  18 firms whose in-sample fit clears the null, the share is 0.556. The verdict rests on the
  evaluable firms. Over all forty the bounds are 0.525 to 0.725: had all eight firms without a
  score counted, H14b would have cleared its bar.
- **H12a passes, as predicted.** Seven firms had a k the fit could resolve, and on 7 of 7 the forward kept at least
  90% of the best option structure's variance reduction. For six it removed more, and the median
  ratio is 1.300. The participating forward was the best alternative every time. At a firm's full
  stated exposure instead of its measured one, six of seven still count. Chevron, whose k is 0.39, is
  the exception: a forward on its whole stated exposure over-hedges it and adds variance.
- **What the gate kept clients from.** The 2:1 ratio forward the gate refuses scores at or above the
  forward on variance for five of the six resolved firms whose k exceeds one, because variance cannot
  see what a structure obliges. On the record's path its P&L fell behind the forward's by as much as
  1.790 per dollar of stated exposure, for Chevron, which carries crude, and by 0.75 within 2020 and
  again within 2022. It is not the price of a barrier product, which was never priced.

## 5. Limits

1. **The market's own loading decides k.** No market return sits on the right-hand side, by design:
   a firm hedges its value, and the market's exposure is part of that value. Between 2009 and 2014
   that part dominated every class, and it is why H11 passes and H17 fails.
2. **The extractor read co-registrants' cover facts as the filer's.** One firm was dropped and three
   had their market value overstated. No correction can move a verdict, so the fixture stands as
   run, and D21's replay uses the same function so that its effectiveness stays scale-free.
3. **H13 could not fail.** Its count is three of three by arithmetic, before any exposure is read.
4. **H16 was close to decided before the read.** ExxonMobil's stated crude is 5.4 times its
   operating cash flow, so its hedge crosses a quarter of it on a 4.6% move. With three clients,
   the claim can establish existence and nothing about prevalence.
5. **H14a could not fail in practice, and H14b's count is carried by noise** on the rates-only firms
   (§4). H14b's failure is near its bar and turns on the evaluable set: the eight firms without a
   score would have carried it over.
6. **H12a rests on seven firms.** Only they had a hedge the fit could resolve, so the claim is about
   the firms where a hedge exists at all, not about the cohort.
7. **Hedges are held on the Treasury curve and at spot.** Swaps and futures are carried as
   DV01-matched cash, so the swap spread, financing and the futures basis are unmodelled, and so are
   forward points and the cross-currency basis. Product exposures are hedged with crude.
8. **The Fed's implied volatility was read only after the read.** The Minneapolis Fed's file opens
   with three lines of preamble that the registered reader takes as its header, so every option in
   the verdicts is priced on EWMA volatility. By the owner's decision the comparison was run the next
   day, on a reader written after the read that also annualises each row at its own horizon: most of
   the file is three-month, where the registered conversion assumed six (DD243). Beside H12a no count
   moves, and the median capture on the four firms with a mapped leg is 1.277, against 1.327 on EWMA.
   Beside H16, ExxonMobil's option book falls by 13.208bn in 2020 and 119.753bn in 2022, against its
   linear hedge's 194.900bn and 175.363bn. Neither is out-of-sample evidence of the kind the verdicts
   are.
9. **The free equity route is weekly.** Daily returns reach only the last 100 sessions, which is why
   H15 is refused. The route's licence is personal and non-commercial.

## 6. Declines

1. **Older swap-tape data.** DTCC's public tape reaches back 366 days, to 2023-12-29, and misses both
   crisis windows. Older reports come by request under unread terms, and the request was not sent.
2. **Barriers.** A knock-in, knock-out forward is path-dependent. The 2:1 ratio forward stands in
   for it, and barriers are stressed, never priced.
3. **Sold optionality in the funding path.** D22's option legs are bought, never sold.
4. **Commodities beyond crude.** A free dated series covers crude only.
5. **The markup benchmark.** Issue price against estimated value in structured-note filings shares no
   machinery with the loop, and it is annexed with its claim, H12b.

## 7. What the layer does not do

It holds no broker SDK, no credential, no order path and no network access. It reads public filings
and public prices, reports what a stated hedge would have done, and says nothing about whether any
company should hold one.
