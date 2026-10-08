# Amendment A7 — the admission test ran, and the window it runs on is 17% of DEV

*2026-09-17. Closes **X24**, carries **DD122**, adds bar **C117**. Amends **DD120** clause 2. No
package, no series added, no row of §4 moved. Discharges the item `AMENDMENT_A6` §2 opened against
itself.*

`AMENDMENT_A6` pre-registered a candidate-set rule and, in the same document, opened **X24** against
its own clause 2: the admission statistic had never been run against the pool it admits into. This
document runs it. It took four projections to answer the question as asked and about thirty to find
out that the question was not the load-bearing one.

**The short version.** X24's premise — that projecting on eleven series rather than eight is a
materially different test — is **measured and is false** for every nominal candidate, worth at most
**0.002**. What is worth a great deal is something X24 did not name: the complete-case rule clause 2
inherits silently selects **1,217 of 7,044 rows**, all of them inside the zero lower bound, and on
that window the statistic cannot tell a new direction from a series that has stopped moving. On
clause 2's own sample **half of `DGS3MO`'s days show no change at all**, and its entire unexplained
residual is **one basis point** — the smallest number FRED publishes for it.

---

## 0. Measured before decided

| # | Measured | Value |
|---|---|---|
| 1 | Rows in the DEV daily panel | **7,044** |
| 2 | — on which all **eight** GSW nominal zeros are jointly observed | 6,735 |
| 3 | — on which all **eleven** of `CANDIDATE_SERIES` are jointly observed | **1,217** |
| 4 | — that figure as a share of the panel | **17.3%** |
| 5 | Span of the eleven-series joint sample (`DFII30` opens it) | **2010-02-22 … 2014-12-30** |
| 6 | `AMENDMENT_A5` §0 row 7 reproduced against the eight zeros — DGS3MO / DFII5 | **0.686 / 0.570** — exact |
| 7 | `AMENDMENT_A5` §0 row 8 reproduced — DGS2 / DGS10, the same-bonds floor | **0.074 / 0.039** — exact |
| 8 | The same floor **re-measured on clause 2's own sample** | **0.1905 / 0.0191** |
| 9 | `0.25` as a multiple of the worse floor: on A5's sample / on clause 2's sample | **3.4× / 1.31×** |
| 10 | Largest change from swapping the basis from eight zeros to the eleven, five nominal candidates, same rows | **0.002** |
| 11 | The same swap for `DEXUSEU` | 0.944 → **0.905** |
| 12 | `DGS3MO` under clause 2 as written | **0.959** |
| 13 | — its residual standard deviation, against a published increment of 1.0 bp | **1.004 bp** |
| 14 | — its share of sample days with **no change at all** | **49.6%** |
| 15 | Residual left by rounding a pool member to 1 bp **inside its own basis** — pure quantisation | **0.390 – 0.416 bp** |
| 16 | — the analytic value that floor should take, `tick / √6` | **0.408 bp** |
| 17 | Unexplained *share* produced by that quantisation alone | up to **0.078** |
| 18 | Candidates on this panel passing all three parts of the amended rule | **1 of 6** — `DEXUSEU` |
| 19 | — and its slot under clause 1 | **none** |
| 20 | Next free ids | **C118 / DD123 / X26** |

---

## 1. X24's premise is measured, and it is not where the problem was

X24 said clause 2 requires a projection on `CANDIDATE_SERIES` while every figure in the repository
was measured against the eight nominal zeros, and that the two are not the same test. They are not
the same test. On the same rows, they are very nearly the same **number**.

| Candidate | on 8 zeros | on the 11 | change |
|---|---|---|---|
| `DGS3MO` | 0.959 | 0.959 | 0.000 |
| `DGS6MO` | 0.922 | 0.920 | −0.002 |
| `DGS1` | 0.681 | 0.680 | −0.001 |
| `DGS2` | 0.191 | 0.190 | −0.001 |
| `DGS10` | 0.019 | 0.019 | 0.000 |
| `DEXUSEU` | 0.944 | 0.905 | **−0.039** |

Adding `DFII5/10/30` to the basis moves no nominal candidate by more than **0.002**, because the
three real series are themselves close to spanned by the nominal curve over this window. The one
series it moves is the one that is not a curve at all.

**So X24 was worth opening and it comes out the mild way.** The gap it named is real, it is
measured, and it changes no disposition. That is a result, and recording it is the whole point of
opening items that might be nothing. What it is not is a licence to stop reading — because the same
run put a much larger number on the table.

---

## 2. The complete-case rule chooses the window, and it chose the worst one available

Clause 2 says the projection runs *"over `FitWindow.dev()`"*. That is not what it computes. The
statistic needs every basis series and the candidate present on the same row, and
`panel.complete_cases` supplies exactly that — which means **the window is set by the shortest
member of the pool**. `DFII30` opens **2010-02-22**. So a rule whose stated window is twenty-seven
years runs on **1,217 rows, 17.3% of the panel**, every one of them after the funds rate reached
zero.

Hold the basis fixed at the eight zeros and change only the rows:

| Candidate | long sample (n = 6,483) | clause 2's sample (n = 1,216) |
|---|---|---|
| `DGS3MO` | 0.686 | **0.959** |
| `DGS6MO` | 0.458 | **0.922** |
| `DGS1` | 0.224 | **0.681** |
| `DGS2` — *the floor* | **0.074** | **0.191** |
| `DGS10` — *the floor* | **0.039** | **0.019** |

**The floor moves with everything else, and that is what breaks the threshold.** `AMENDMENT_A6`
justified `0.25` as *"3.4× the worse floor reading"*, reading 0.074 off `AMENDMENT_A5` §0 row 8 —
which was measured on the long sample. On the sample clause 2 actually computes over, the worse
floor reading is **0.1905**, and `0.25` is **1.31×** it. The number survived; its justification did
not travel with it.

---

## 3. What the statistic is actually measuring at the front of the curve

The share of variance a projection leaves unexplained is **scale-free**. It asks what fraction of a
series' movement is its own, and it has no opinion about whether the series moved. That is fine when
everything in view moves. Over 2010–2014 the front of the nominal curve did not.

| Series | sd of daily change, long | sd, clause 2's sample | days with **no change** |
|---|---|---|---|
| `DGS3MO` | 5.315 bp | **1.025 bp** | **49.6%** |
| `DGS6MO` | 4.652 bp | **0.969 bp** | **51.2%** |
| `DGS1` | 4.886 bp | 1.114 bp | 44.2% |
| `DGS2` | 5.919 bp | 2.575 bp | 30.4% |
| `DGS10` | 6.009 bp | 5.414 bp | 6.4% |
| *pool members, same rows* | — | 1.4 – 5.8 bp | **0.1 – 9.7%** |

`DGS3MO` is published to two decimal places in percent, so its smallest expressible move is
**1 bp**. On clause 2's sample it does not move at all on half its days, its whole daily standard
deviation is **1.025 bp**, and the residual the pool cannot explain is **1.004 bp**. There is no
direction in that number. There is one tick.

**The quantisation floor, measured rather than argued.** Take a series that *is* a member of the
basis — where the true unexplained share is exactly zero — round its level to 1 bp, and project the
rounded series back on the pool:

| Rounded pool member | unexplained share | residual sd |
|---|---|---|
| `SVENY01` | 0.078 | 0.409 bp |
| `SVENY02` | 0.022 | 0.390 bp |
| `SVENY05` | 0.006 | 0.395 bp |
| `SVENY10` | 0.005 | 0.411 bp |
| `SVENY30` | 0.005 | 0.416 bp |

Rounding alone produces a residual of about **0.41 bp** and an unexplained share of up to **0.078**,
from a series that is perfectly explained before it is rounded. The measured figure lands on
`tick / √6 = 0.408` — two independent rounding errors of a uniform tick, differenced — which is why
this is a floor and not a coincidence of one sample.

**So the ranking the statistic produces at the front of the curve is upside down.** `DGS3MO` has the
largest share in the sweep (0.959) and a residual of one tick. `DGS2` has a share of 0.190 — under
even the old threshold — and the **largest** nominal residual measured (1.124 bp). Share ranks how
much of a dead series is unexplained. It does not rank whether anything is there.

---

## 4. DD122 — the rule, amended in three places

> **DD122 — the admission statistic carries its sample, its hurdle is relative, and a stalled series
> is refused.** `AMENDMENT_A6` DD120 clause 2 is amended in three parts and is otherwise unchanged.
> Clauses 1, 3 and 4 are untouched.
>
> **Part 1 — the figure is void without its sample.** An admission reports the number of differences
> the projection ran on, the first and last date, and the rows `complete_cases` dropped. Clause 2's
> phrase *"over `FitWindow.dev()`"* is **withdrawn as a description of what is computed**: the test
> runs over the joint sample of the pool and the candidate, which is set by the shortest member.
> Today that is **1,217 rows, 2010-02-22 … 2014-12-30, 17.3% of the panel**.
>
> **Part 2 — the hurdle is a multiple of the floor on the test's own sample, not a fixed number.**
> A candidate must leave more than **3.4× the worse same-bonds floor**, both measured on the rows the
> test ran on, the floor being `DGS2` and `DGS10` projected on the same basis — `AMENDMENT_A5` §0
> row 8's pair. The multiple is `AMENDMENT_A6`'s reported choice and is **inherited unchanged**; the
> floor is the measurement. Today: floor **0.1905**, hurdle **0.648**. The fixed `0.25` is withdrawn.
>
> **Part 3 — a share is not a scale.** An admission additionally reports the residual standard
> deviation in the units the series is published in, that series' smallest published increment, and
> the share of sample days on which the series did not change. A candidate is **refused** if its
> residual is below one published increment, or if it did not change on more than **20%** of the
> sample's days. Measured beneath both: quantisation alone yields **0.41 bp** of residual and
> **0.078** of share (§3), and the pool's own members stall on **0.1 – 9.7%** of these days against
> the nominal candidates' **30.4 – 51.2%**.

**Note the direction: this makes the rule stricter, and it makes it stricter by a lot.** The hurdle
goes from 0.25 to 0.648 on today's pool, and two refusal grounds are added that did not exist. A
candidate landing at 0.40 would have been admitted under DD120 as written and is refused now. That
is not a tidying edit.

### 4.1 The full table, under the amended rule

| Candidate | share | vs 0.648 | residual | ticks | stall | **verdict** |
|---|---|---|---|---|---|---|
| `DGS3MO` | 0.959 | ok | 1.004 bp | 1.00 | **49.6%** | **REFUSE** — stalled |
| `DGS6MO` | 0.920 | ok | 0.929 bp | **0.93** | **51.2%** | **REFUSE** — scale and stall |
| `DGS1` | 0.680 | ok | 0.919 bp | **0.92** | **44.2%** | **REFUSE** — scale and stall |
| `DGS2` | 0.190 | **no** | 1.124 bp | 1.12 | **30.4%** | **REFUSE** — share and stall |
| `DGS10` | 0.019 | **no** | 0.748 bp | **0.75** | 6.4% | **REFUSE** — share and scale |
| `DEXUSEU` | 0.905 | ok | 0.00737 | **73.7** | 1.0% | **ADMIT** on direction |

**One candidate on this panel passes the direction test, and clause 1 refuses it for having nowhere
to go.** `CROSS_MARKET` is a contrast between two curves at matched tenors and a spot rate is not a
curve; admitting `DEXUSEU` needs a seventh grammar term, which **DD63** closed. That is the same
answer `AMENDMENT_A6` §3 gave, now with the direction half measured instead of asserted, and it is
worth stating in its sharpest form: **the only series this repository's own panel says is genuinely
new is the one its grammar has no sentence for.**

**No current pool member would be evicted by part 3**, which is the coherence check the thresholds
have to pass: the worst stall among the eleven is `DFII30` at 9.7%, against a 20% bar.

---

## 5. `AMENDMENT_A6` §3's registered prediction — wrong number, surviving verdict

A6 §3 registered this, before the run:

> *"measured against the eleven, the GSW TIPS zeros come in **below 0.25** at all three tenors,
> because they track the same real curve `DFII` already carries. If that is wrong the rule admits
> them, and the prediction is the thing that was falsifiable."*

**The GSW TIPS zeros are not on this repository's panel, so the prediction as written cannot be run
here, and this document does not claim to have run it.** What is available is the nearest proxy the
tree supports: leave each real series out of the pool and project it on the other ten — the question
*does a real tenor, given everything else, carry its own direction?*

| | vs the other ten (n = 1,216) | on the long sample, `DFII30` dropped from the basis (n = 3,001) |
|---|---|---|
| `DFII5` | **0.283** | **0.387** |
| `DFII10` | 0.101 | 0.232 |
| `DFII30` | 0.107 | — |

**At its stated threshold the prediction is false.** It said below 0.25 at all three tenors; the
five-year real point reads **0.283** on the eleven and **0.387** on the longer sample. The real
curve is not one dimension, and its front carries something neither the nominals nor the longer
reals do.

**The verdict it supported nonetheless survives, and the reason is uncomfortable enough to write
down plainly.** Under the hurdle this document corrects to — 0.648 — all three tenors are refused.
So a prediction that failed against the number its own document chose is rescued by that document's
number being wrong. **That is precisely the shape clause 3 exists to forbid**, and the only honest
defences are these, offered for the reader to reject:

- The hurdle was re-derived from the `DGS2`/`DGS10` floor, which involves no real series and could
  not have been steered by `DFII5`'s reading.
- It moves the threshold **up**, refusing more candidates, including ones a plan wanting reach would
  rather have admitted.
- It changes **no disposition** in `AMENDMENT_A5` §9 row 2. The TIPS-reals arm is refused at
  **clause 1** — the `REAL_VS_NOMINAL` slot is filled by `DFII5/10/30` — which is independent of
  direction and would refuse it at any threshold.

**What is withdrawn is the second leg of that refusal, not the refusal.** A6 §3's row said the arm
was blocked on X24 and predicted the direction test would refuse it too. At the closest available
proxy, the direction test does not refuse it at the threshold A6 named. The arm now stands on one
reason, and the prediction is struck rather than quietly restated.

---

## 6. A one-line defect in `AMENDMENT_A5` §0 row 7

Row 7 reports **0.686 / 0.570 / 0.971** for `DGS3MO` / `DFII5` / `DEXUSEU`. The first two reproduce
exactly on **level** changes. The third reproduces only on **log** changes — 0.9711 — where level
changes give 0.9731. The row states one statistic computed two ways.

It is annotated at A5 rather than rewritten, and it is not an item: both readings sit far above any
hurdle this document names, so nothing turns on which was meant. It is recorded because a row that
silently mixes conventions is how a later reader gets a figure they cannot reproduce, and this
repository has that failure mode on its register twice already.

---

## 7. C117 — the pool states how much of DEV it is jointly observed on

DD120 clause 4 already makes an admission restate the pool, the structure count and the leg count.
It forgot the count that turned out to matter most: **the sample the admission test runs on.** A
series added to the pool whose history is short does not merely add a column — it shortens the
window every future admission is judged on, silently, through `complete_cases`, and the figure that
would reveal it appears nowhere.

**C117** holds that number as an equality against the tree: the rows on which every member of
`CANDIDATE_SERIES` is simultaneously observed, and the panel's total, must equal the figures stated
in §0 rows 1 and 3 above. Add a short series and the joint sample shrinks, the stated figure is
wrong, and the suite is red until someone writes the new one down — at which point clause 4's diff
carries it and a reader can see what the admission cost.

It goes red on exactly one event and green two ways, which is the property C116 was built for as
well: restate the sample, or do not shorten it.

**C117 is not a general detector of a pool that grew, and it should not be read as one.** Measured:
admitting `DEXUSEU` takes the joint sample to 1,213 rows and C117 goes red; admitting `DGS3MO`,
which is fully observed across this span, leaves it at 1,217 and C117 stays green. The bar that
catches the pool changing **at all** is **C116**, which requires a claim scored at the new universe.
The two are complementary and neither substitutes for the other: C116 asks what the pool costs a
verdict, C117 asks what it costs the test.

---

## 8. What this could still get wrong

- **The leave-one-out proxy is not the GSW TIPS zeros.** A series already in the pool is not the
  same object as a candidate; the proxy answers *is a fourth real tenor spanned* and not *is this
  particular fourth real tenor spanned*. §5's verdict is the strongest thing the tree supports and
  it is weaker than a measurement of the actual candidate.
- **Part 3's two numbers were chosen after seeing the candidates.** One published increment and 20%
  of days are round numbers picked inside measured gaps — 0.75–1.12 ticks against a 0.41 bp
  quantisation floor, and 9.7% against 30.4% — and any choice inside either gap gives today's
  answers. That is a reason the choice is *insensitive*, not a reason it is disinterested. They bind
  **prospectively**, before any series has landed, and today's three refusals do not rest on them.
- **3.4× is inherited, not re-derived.** Re-choosing the multiple after seeing these numbers is the
  defect clause 3 names, so A6's figure is kept even though nothing about this run recommends it
  over any other.
- **The zero-lower-bound reading is an explanation, not a measurement.** What is measured is that
  the floor rises, the front-end series stall, and the residual equals one tick. *Why* the front of
  the curve was pinned from 2010 is well known and is not established here.
- **The floor is two series.** `DGS2` and `DGS10` are what A5 §0 row 8 measured. `DGS1` is arguably a
  third reading of the same relationship and reads **0.680** on clause 2's sample — which, had it
  been chosen as the floor, would put the hurdle above 2.0 and refuse everything. The pair is
  inherited rather than re-chosen, for the reason in the third bullet, and this is the largest
  single soft spot in the amended rule.
- **Nothing was fetched.** Every figure comes from `tests/fixtures/panel_daily_dev_20260914.csv`,
  through `deskcraft.panel`, on the interpreter `docs/TOOLING.md` names. No egress, no new file, no
  series added.

---

## 9. Result

**X24 CLOSED** by measurement, with the outcome its body registered as one of the two that would
close it: a candidate either clears the hurdle against the eleven or it does not, and *"wave 1
shrinks by an argument rather than by a preference."* It shrank to nothing, and the argument is §4.1.

**DD122** taken. **C117** added. `AMENDMENT_A6` clause 2 amended in three parts; clauses 1, 3 and 4
untouched. `AMENDMENT_A5` §0 row 7 annotated. §1's tally moves to **nine closed, three standing,
thirteen open with an owner** — and D8's discharge list drops from seven items to six.

Next free ids **C118 / DD123 / X26**.
