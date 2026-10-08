# Owner admission: three results-only routes for D22

**Taken by the owner on 2026-09-26 and recorded the same day. Three routes, each by name.**

This file is the written record that the joint registration's §6.2 asks for three times, in the
words *"needs the owner's admission by name"*. It is not a licence reading, and it does not claim
to be one. It records the decision, who took it and when, what each route's own words say, and
what the decision costs.

It is a different kind of admission from `OWNER_ADMISSION_the_credit_tier.md`. That admission let
three series into **committed fixtures**, and `sources.ADMITTED` carries them. None of these three
routes is ever committed, so none of them enters `sources.ADMITTED`, and C125 still names exactly
the credit tier's three.

---

## 1. The decision

The owner was asked each question separately on 2026-09-26, and answered each one:

| Question, as put to the owner | Answer |
|---|---|
| *"Do you admit the EIA/NYMEX WTI futures prices by name (CME Group's data, republished by EIA with permission)?"* | **Admit it** |
| *"Do you admit Alpha Vantage's free daily share prices by name?"* | **Admit it** |
| *"Do you admit the Minneapolis Fed's option-implied volatilities by name?"* | **Admit it** |

> **Each of these three routes may be read at D22's read and computed on. None may be committed to
> this repository or to curvecast, and only statistics computed from them are reported.** Each
> route is admitted separately and by name. A fourth route needs a fourth decision.

## 2. The three routes, and what each one's own words say

| Route | What the words say | What the admission allows | What it does not allow |
|---|---|---|---|
| **EIA's NYMEX WTI futures, contracts 1 to 4, daily** (DD176) | EIA's daily prices page: *"Prices are republished by EIA with permission as follows: [...] Prompt-Month Energy Futures from CME Group"*. EIA's copyright policy: licensed third-party material *"may be protected"*, and reproduction beyond fair use needs *"the written permission of the copyright owners"* | DD176's WTI arm: a crude-oil leg in H16 and the option reports, for a firm with a crude read | A committed settlement price, or use in H15 (DD176 item 3) |
| **Alpha Vantage's free daily equity prices** (§6.2, H15's denominator) | Personal, non-commercial use, research included. It counts **any passing-on to others** as commercial, and it counts use **while employed by or affiliated with an investment firm** as commercial | H15's regression and cohort filter (iii) | A committed price, or passing a price on to anyone |
| **The Minneapolis Fed's option-implied distributions** (§6.1, implied volatility source (1)) | Use *"for research and informational purposes only"*. Its methodology prices from Bloomberg trade data, and third-party material needs the owner's permission | The first entry on §6.1's implied-volatility list, six-month horizon, the latest release on or before the pricing date | A committed volatility, or any use outside research |

## 3. Alpha Vantage's condition, named as §6.2 requires

**This admission lapses on the day the owner becomes employed by, or affiliated with, an investment
firm.** The licence itself makes that use commercial, and a free, non-commercial licence does not
cover it. From that day:

- no new fetch from Alpha Vantage is made, and no new computation runs on its data;
- if D22 has not yet read, Alpha Vantage is no longer admitted, and the registration's DD178 says
  what follows (H15 is refused by name, and H16's cohort is drawn without filter (iii));
- whether results already computed may still be used is **not read here**. It is a question for the
  licence at that date, and the owner answers it then.

## 4. What it costs

1. **Nothing enters git, so what the repository can send is unchanged.** `NOT_SENDABLE.md` is
   already at the root because of the credit tier, and this admission neither adds to that reason
   nor removes it.
2. **Paper 2's numbers rest on data whose owners license it for personal or research use only.**
   Paper 2 can publish the method and the statistics. It cannot publish a single price or
   volatility, so a reader cannot re-run it from the paper alone.
3. **The WTI arm stays thin.** It reaches 5 of 17 firms on D23's twenty (curvecast `a6ea07c`). It
   is crude oil only. A refined-product exposure is hedged with crude (DD179).
4. **The Alpha Vantage admission has an end date the owner may choose without meaning to.** Taking
   a job at an investment firm ends it (§3).

## 5. What this does not authorise

- **It does not authorise the first out-of-sample read.** Only
  `docs/OWNER_AUTHORISATION_the_first_oos_read.md` does that, and only the owner writes it (DD133).
  No row from any of these routes dated after `DEV_END` is read before it, and the WTI and
  implied-volatility routes are read at D22's own read (§10 step 5), as DD176 and §6.1 fix.
- **It does not grade anything in curvecast.** When D22 reads, curvecast's rights register gains a
  row for each route under its own gate, graded as §2 says.
- **It does not admit a fourth route.** Neither DTCC's older swap reports nor any other source is
  admitted here.
- **It does not change `Source.committable`, `sources.ADMITTED` or C125.**

## 6. Three later decisions on two of these routes, 2026-09-26

Alpha Vantage's free key turned out not to reach a daily history: *"compact returns only the latest
100 data points"*, and *"The 'full' outputsize is available to premium keys"*. So H15 is refused and
filter (iii) is skipped (the registration's DD180). The owner was then asked three more questions
the same day, and answered each. Each extends a route admitted in §1 to a use §2 did not list, so
each is recorded here by name, as §1 requires.

| Question, as put to the owner | Answer |
|---|---|
| *"Alpha Vantage's free key has no daily price history, only the last 100 sessions; full daily history is paid. What should Paper 2 measure each company's exposure on?"* | **Weekly + filings**: *"Use Alpha Vantage's free weekly adjusted prices for D17's and D21's fits, and each company's quarterly cash flow from its SEC filings as a second measure. The two are reported side by side and never pooled"* |
| *"D17 can only measure crude-oil exposure with WTI prices. The EIA/NYMEX route you admitted covers D22 only. Extend it to D17's 2012–2014 regression?"* | **Extend it**: *"Same terms as the admission: read and computed on, never committed."* |
| *"Alpha Vantage sends a company's whole weekly history, up to this week, in one response. So fetching 2012–2014 also delivers 2015–2026 rows, the years only your out-of-sample authorisation may open. How should that be handled?"* | **Drop on arrival**: *"Rows after 2014-12-24 are discarded in memory before anything is saved or computed. A test checks that nothing later than 2014-12-24 is stored, and D17's record says so."* |

> **Alpha Vantage's free weekly adjusted prices may be read and computed on for D17's and D21's
> fits, and EIA's NYMEX WTI settlements for D17's regression, on the terms of §1: never committed,
> only statistics reported.** Every row dated after 2014-12-24 is dropped on arrival, before
> anything is stored or computed, and is read again only at D22's own read.

Three things this section says about its own record:

1. **The second and third questions named 2012–2014**, because D17's regression window was then
   taken to be two years. D17's pre-commit fixes five, 2009-12-24 to 2014-12-24, on a power table
   computed afterwards from committed DEV rates and currencies (its §6). Every date in it is still
   before `DEV_END` and the terms do not change, so the answer is recorded as reaching D17's window,
   and **the owner is told so and may say otherwise**.
2. **The third answer is applied to EIA's route too.** EIA's history also arrives whole, to
   2024-04-05, and the owner's reason reaches it unchanged. That application is this record's, not
   the owner's, and it is said here so that it can be refused.
3. **§3's condition reaches the weekly use.** The investment-firm clause is Alpha Vantage's licence,
   not a term of one endpoint, so the day it lapses the weekly use ends with the daily one.

## 7. One later decision on the Minneapolis Fed's route, recorded 2026-09-28

§1 admitted the Minneapolis Fed's distributions for D22 alone. D21's pre-commit had left them out,
because nothing mapped the Fed's markets to D21's factors (its DD204 item 7). A recommendation put
to the owner said what it needed:

| What was put to the owner | Answer |
|---|---|
| *"Price D21's option hedges at market implied volatility, not only realised. [...] report the implied-vol version next to the verdict without changing the verdict. What it needs from you: you admitted the Minneapolis Fed data for D22 only, so you'd extend that admission to D21."* | **Extend it**, recorded from the owner's reply: *"please compelete this one by one"* |

> **The Minneapolis Fed's option-implied distributions may be read at D21's own read and computed on
> for D21's DD210, on the terms of §1: never committed, only statistics reported.** Every row dated
> after 2025-12-31, and every market DD210 does not map, is dropped on arrival, before anything is
> stored or computed.

Four things this section says about its own record:

1. **The reply was an instruction, not an answer to a question.** It asked for this recommendation
   and one other to be carried out, and this one said in terms what it needed from the owner. It is
   recorded as the extension, and **the owner is told so and may say otherwise**. Refused, D21's
   DD210 is `NOT_PERFORMED` by name and nothing else in D21 moves.
2. **Drop on arrival is this record's rule**, carried over from §6's third answer, whose reason
   reaches it unchanged: the Fed's file arrives whole, to this week. As in §6 item 2, the application
   is said here so that it can be refused.
3. **Nothing from the Fed is read before the authorisation**, not even its DEV rows, because they
   cannot be fetched without the rest. §5 applies unchanged: the file is read at D21's own read, and
   D21's DD210 is rehearsed on a table built from realised volatility instead.
4. **§3's lapse clause is Alpha Vantage's and does not reach this route.** §2's research-only terms
   do, unchanged. The other recommendation, marking D18's refused ratio forward beside H12a (D21's
   DD211), reads only routes D21 already has, so it needed no decision here.

*Confirmed 2026-09-28 by DD234 (the joint registration's §12): the extension stands, and so does
item 2's application of drop-on-arrival to the Fed's file.*
