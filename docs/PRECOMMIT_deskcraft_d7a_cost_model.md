# PRE-COMMIT — D7a: the cost model, and the one term of four that graded data reaches

*Written 2026-09-15, at `694b374`, before any of this package's code existed.*

**Package D7a**, `docs/BUILD_ORDER_D3_D16.md` §4. Its row reads: *"§3. ~20 instrument profiles,
compositional structure costs, four cost terms, the four-point sensitivity ladder, and §3.4's
bias recorded on the object."* Decisions **DD74–DD83**, bars **C77–C87**.

It discharges carried items **X4** and **X5**, which `docs/CARRIED_ITEMS.md` assigned to this
package, and opens one: **X11**, which it cannot close and D7b can.

**The headline, measured before the module was written.** The build order names four cost terms.
Of the four, **exactly one — the spread term — is computable for every leg of `US_CASH_BOOK`
from what this repository has graded.** Two of the other three were declared unmodelled on two of
the four legs at **D2**, by `ReExpression(unmodelled=("financing", "delivery option", "roll"))`,
which nobody at D2 was writing as a statement about a cost model. The same two have no graded
input here in any case: `sources.py` carries no row for repo, SOFR or GC, and none for the NY Fed
primary-dealer volumes §3.3 names as the impact term's source. Two independent reasons, written
three packages apart, agree on which terms this package cannot compute.

---

## 0. Measured before decided

Ten readings. Four of them changed a decision, and two of them contradict a sentence in the
document that commissioned this package.

### 0.1 Two of the four cost terms were declared unmodelled at D2, on two of the four legs

`reference.py`'s `_FUTURES_TO_CASH` has carried this since D2, on legs 1 and 2:

    ReExpression(original_kind=InstrumentKind.FUTURE,
                 unmodelled=("financing", "delivery option", "roll"))

§3.2's four terms are `half_spread`, `impact`, `financing`, `roll`. Intersecting the two:

| leg | `unmodelled` | overlaps the cost terms |
|---|---|---|
| `us_2y` | financing, delivery option, roll | **financing, roll** |
| `us_10y` | financing, delivery option, roll | **financing, roll** |
| `us_breakeven_5y` | — | — |
| `eurusd` | — | — |

DD12 wrote that field to say *"any later package reporting a carry number on such a leg has to
read it or it is reporting a number the data does not support."* D7a is that later package, and
the field is read rather than re-decided (DD80). Two of the four terms are refused on half the
book by a declaration made three packages before there was a cost model to refuse them for.

### 0.2 Two of the four cost terms have no graded input in this repository at all

§3.3 names the inputs. Checked against `sources.py`, which has 23 rows:

| §3.3's input | source named | row in `sources.py`? |
|---|---|---|
| Bid-ask, on-the-run vs off-the-run | NY Fed and Board staff research | cited, not a series — fine |
| TIPS liquidity penalty | FRBSF wp2017-10 | cited, not a series — fine |
| Average daily volume, by maturity bucket | NY Fed FR 2004B | **none** |
| Repo / financing | *"Fed H.15 and SOFR, both already graded"* | **none** |

**The words "both already graded" are false.** H.15 is graded *for yields* — `DGS3MO` through
`DGS10` and the three `DFII` rows — and neither H.15's overnight rates nor SOFR has a row here,
nor a column in the committed panel. Nothing in this repository can compute a financing drag, and
nothing can compute an impact term, because neither input exists.

This is not closable by D7a. Grading a source means an extraction, and the extraction runs in
curvecast, which has the egress. It becomes **X11**, owned by D7b, which is the package that
needs the numbers.

### 0.3 Cost per risk divides by duration only if the spread is carried in price — and it must be

Two units are available for a half-spread, and the choice is not cosmetic.

    carried in PRICE:  cost = half_spread_price * 1e-4 * notional
                       DV01 = duration * notional * 1e-4
                       cost / DV01 = half_spread_price / duration

    carried in YIELD:  cost = half_spread_yield * DV01
                       cost / DV01 = half_spread_yield

**Under the second, duration cancels exactly and X4's bias vanishes from the arithmetic while
remaining in reality.** A model carrying its spreads in yield would be internally consistent,
would report a cost per unit of risk that no convention choice could move, and would be wrong.

The question has a determinate answer and it is not a preference: **a dealer quotes a Treasury in
32nds of a point, which is price.** So the spread is carried in price (DD75), the duration does
not cancel, and the convention arm X5 asks for has something to move.

### 0.4 X4's bias is 13.289% in the ratio, not the 11.730% it is in the denominator

X4 states the defect as *"`SVENY10` DV01 understated 11.730%, and cost-per-risk divides by it."*
Understating a denominator by *x* overstates the ratio by *x/(1−x)*, not by *x*. Recomputed from
the committed panel on 2014-12-24:

| series | true duration | par proxy | duration understated | **cost per DV01 overstated** |
|---|---|---|---|---|
| `SVENY02` | 2.000000 | 1.977161 | 1.142% | **1.155%** |
| `SVENY05` | 5.000000 | 4.741165 | 5.177% | **5.459%** |
| `SVENY10` | 10.000000 | 8.826975 | 11.730% | **13.289%** |

The figure that goes on the bias object is **13.289%**, because that is the number the thing the
bias is about — a reported cost per unit of risk — is wrong by.

### 0.5 X5 says two conservative biases point the same way. There are three

X5's two are §3.4's bid-ask overstatement (unquantified, from the Board's 2025 paper) and X4's
convention bias. D4's **DD52** left a third as a magnitude with no direction: *"MEIP's par form is
annual-pay and US Treasuries pay semi-annually. Measured at +0.12% of duration on `DFII5`."*

D4's §0.7 table gives semi-annual **minus** annual-pay, so the annual-pay branch this repository
actually runs **understates** `DFII5`'s duration:

    DFII5 @ 0.5000%   annual-pay 4.925866   semi-annual 4.931932   annual-pay low by 0.1231%
    -> DV01 understated  ->  cost per DV01 OVERstated by 0.1232%  ->  stops earlier  ->  fewer legs

Same direction as the other two. So the answer D7a gives X5 is not the reassuring one: the
compounding concern is **worse** than the register stated, by a third term — though that third
term is two orders of magnitude smaller than the second, which is itself the reason to carry
magnitudes on the objects rather than a count of biases in prose.

### 0.6 `net_dv01` is a residual, and dividing cost by it overstates cost per risk 133.89-fold

D4's `LegSensitivity.net_dv01` reads two ways on purpose: a leg's DV01 on an outright, and the
**residual** a parallel move leaves on a leg declaring a neutrality. For a cost-per-risk
denominator the second reading is a trap. Measured on `US_CASH_BOOK`:

| leg | gross DV01 | net DV01 | gross ÷ net |
|---|---|---|---|
| `us_2y` | 40,000.00 | 40,000.00 | 1.0000 |
| `us_10y` | 60,000.00 | 60,000.00 | 1.0000 |
| `us_breakeven_5y` | 49,629.33 | 370.67 | **133.8915** |
| `eurusd` | 0.00 | 0.00 | **0 ÷ 0** |

You pay the spread on every component you trade, so the risk that spread buys is the components'
risk and not what is left after they offset. On a spread whose declared neutrality actually held,
the net is **zero** and cost per risk is infinite — a structure priced as infinitely expensive for
being well hedged. The denominator is gross DV01 (DD81), and the FX leg, which has no rate sense
at all, is refused rather than returned as infinity.

### 0.7 §3.2's four terms are not all annualised, and §3.2 contradicts §3.1

Two defects in the commissioning formula, both found by trying to implement it.

**(a) The label says annualised and two terms are not.** Written against the correct form:

    financing:  written  financing_drag * holding_years   correct  financing_drag
    impact:     written  impact(...)                      correct  2 * impact(...) / holding_years

| holding years | financing written ÷ correct | impact written ÷ correct |
|---|---|---|
| 0.25 | 0.25× | 0.125× |
| 1.00 | **1.00×** | 0.500× |
| 4.00 | 4.00× | 2.000× |

The financing term is right at exactly one holding period — one year — which is the most likely
reason the error survived being read. The impact term is right at two years and at no other.

**(b) `half_spread × n_components` contradicts §3.1, and §3.1 is the correct one.** §3.1's own
table already prices the breakeven as *"1 × nominal + 1 × TIPS"*, which is a sum over components
with **different** per-component spreads. §3.2's single `half_spread × n_components` is that sum
only when every component costs the same, and the reference book's leg 3 is exactly the case where
they do not. On the stated $50m, with the TIPS profile at twice the nominal:

    section 3.2   nominal half-spread x 2 components  =  15,625.00
    compositional nominal + TIPS                      =  23,437.50   -- section 3.2 low by 50.0%

The build-order formula is **annotated, not rewritten** — D4's precedent for the same situation.

### 0.8 The front end D5 graded has no computable duration, so it has no cost per risk

`modified_duration` refuses `DGS3MO` and `DGS6MO`: the par-bond branch takes whole years, which is
MEIP's signature restated rather than widened (DD52). Every other series carrying a D4 convention
has one. So the two front-end names **D5 went and graded** can be given a half-spread and cannot
be given a cost per unit of risk, and D7b looking for a short leg meets that at the denominator
rather than at the data. Recorded by name (C86) rather than left to be discovered.

### 0.9 The convention arm is 0.18 of a ladder rung, which is why X5 asks for an arm

X5's remedy is a **convention arm** on §3.5's ladder rather than a wider ladder, and the numbers
say why. §3.5's rungs are 0.5× / 1× / 2× / 4× — a factor of two apart, one unit apart in log₂.
The convention effect at ten years is 1.132891×, which is **0.1800 of a rung**.

A ladder detects a *flip between rungs*. An effect of 0.18 of a rung cannot produce one at any
multiplier, so no widening or narrowing of the cost ladder separates the convention's contribution
from the cost multiplier's. It needs its own axis (DD82).

### 0.10 The tree is green before this package

`694b374`, production interpreter, nothing modified:

    83 passed in 6.20s

ruff and both import contracts run inside that, as bars, since `0e19ecd`.

---

## 1. Decisions

### DD74. `CostBasis` has no member meaning "measured"

§6 of the build order lists *"a cost number reported as a measurement"* among the things that
would make the whole plan wrong, and §3.5 says it in the other direction: *"The cost numbers are
calibrated assumptions from public sources, never measurements, and no package may describe them
otherwise."*

A rule stated twice in prose is the kind of rule this repository mechanises. `CostBasis` has three
members — `QUOTING_CONVENTION`, `PUBLISHED_RESEARCH`, `STATED_ASSUMPTION` — and **no fourth**. A
measurement is not a value this type can hold, so a profile claiming to be one does not fail a
check; it fails to be constructible. That is `Direction`'s move at D2: the bug is not caught, it is
made unrepresentable.

Every profile carries a `basis` and an `evidence` string, in `Source`'s shape, so what a number is
and where it came from travel with the number rather than with this document.

### DD75. A half-spread is carried in **price**, as an exact dyadic fraction of one 32nd of a point

§0.3: carrying it in yield makes the duration cancel and X4's bias disappear from the arithmetic
while remaining real. Price it is.

The values are the quoting increment rather than invented decimals. One 32nd of a point is
3.125 bp of par, and every entry in the table is `1/4`, `1/2` or `1` of that:

| bucket | increment | full spread | **half-spread** |
|---|---|---|---|
| 0–2y, 2–3y | ¼ of a 32nd | 0.78125 bp | **0.390625 bp** |
| 3–6y, 6–7y, 7–11y | ½ of a 32nd | 1.5625 bp | **0.78125 bp** |
| 11y+ | one 32nd | 3.125 bp | **1.5625 bp** |

C77 asserts the dyadic property, so a future hand cannot quietly replace a convention with a
fitted decimal: `0.42` is not a fraction of a 32nd and turns the bar red.

### DD76. A profile is derived from **(market, maturity bucket)**, never written per series

`SVENY10` and `DGS10` are the same bond at the same point on the curve, quoted two ways. D4's
tables are keyed by series because the *compounding convention* genuinely differs by series; a
*cost* does not — a dealer quotes the note, not the curve fit. Writing two rows would be two
places for one truth to live, and they would drift.

So `COST_OF` is built by a function of market and bucket, and the buckets are the NY Fed FR 2004B
buckets §3.3 already names: 0–2, 2–3, 3–6, 6–7, 7–11, 11+. C77 asserts `SVENY10` and `DGS10` agree,
which is a law rather than a coincidence.

### DD77. Cost is compositional, and **even** in the coefficient's sign

§3.1 is right and §3.2 is wrong where they disagree (§0.7b). A structure's cost is
`Σ_components half_spread(series) × |coefficient|`, and the absolute value is load-bearing: you pay
the spread whichever way you trade. DV01 is **odd** in the coefficient and cost is **even**, which
is the whole reason a spread can be risk-neutral and cost twice an outright.

The build-order formula is annotated and not rewritten, as D4 annotated its own row.

### DD78. The four terms are annualised consistently, and the two §3.2 mis-annualises are corrected

    annualised = ( 2*half_spread + 2*impact ) / holding_years      entry and exit, spread over the hold
               + financing_drag                                    already per year
               + roll_cost * rolls_per_year                        already per year

The ratios §0.7a measures are recorded on the module so a reader comparing this against the build
order finds the difference explained rather than merely present.

### DD79. A term whose input is not graded here is `None`, never `0.0`, and `total` refuses

Two of the four (§0.2). A zero is a number and every sum downstream adds it, which is D4's DD53
reasoning for `UNPRICEABLE` not being zero, applied to a term instead of a leg. `AnnualisedCost`
carries four optional terms and a `total` that raises, naming every absent term and its reason.

A caller who has an ADV figure may state it. There is no default and no table, because a default
would be this repository inventing the number §3.3 said would come from the NY Fed.

### DD80. A term the leg's own `ReExpression` declares unmodelled is refused **on that leg**

Read from `leg.re_expressed.unmodelled` (§0.1), not from a list here. A list here would be a second
place the truth lives and would not follow a leg whose re-expression changes.

### DD81. The risk denominator is **gross** DV01, and a leg with no rate sense has none

§0.6. `net_dv01` is a residual on any leg declaring a neutrality — 133.89× on the breakeven leg,
and zero on a spread whose neutrality holds. `cost_per_dv01` refuses a leg whose `RateSense` is
`NONE` by name rather than returning infinity, because `eurusd` is in the reference book and an
infinity propagates into every total that adds it.

**The general denominator is not this package's.** The stopping rule's risk budget is expected
shortfall at 97.5% and component ES under Euler is D9. D7a supplies the numerator and a rates-only
denominator, and says so.

### DD82. The ladder has **two** axes: four cost multipliers × two duration conventions

§3.5 mandates 0.5× / 1× / 2× / 4×. X5 adds the convention arm, and §0.9 is why it has to be an
arm rather than more rungs: 0.18 of a rung cannot produce a flip between rungs at any multiplier.
`DurationConvention` has two members — `AS_QUOTED`, which is D4's decision per series, and
`PAR_PROXY`, which is MEIP's proxy everywhere — so the eight cells report the convention's
contribution separately from the cost multiplier's rather than blended into it.

### DD83. A bias is an object with a **direction**, and an unquantified magnitude is `None`

X4's stated closure condition: *"on the cost object rather than in prose, in the same shape §3.4
already uses for the bid-ask bias."* `Bias` carries the source, the direction as a signed enum, the
magnitude as `float | None`, and what it does to the leg count.

`None` is the Board paper's bid-ask bias, which *"does not quantify the magnitude."* It is not
`0.0`, for DD79's reason. `compounded_bias` returns the product over the quantified entries **and
the count of the entries it could not include**, so the compounded figure is never a single number
that hides an arm — which is precisely the failure X5 describes.

---

## 2. Bars

| bar | what it holds |
|---|---|
| **C77** | Every half-spread is an exact dyadic fraction of one 32nd of a point, and the table is derived from (market, bucket): `SVENY10` and `DGS10` agree, and so do `SVENY02` and `DGS2` |
| **C78** | `CostBasis` has no member meaning measured, and every profile carries a basis and non-empty evidence |
| **C79** | Cost is compositional and even in the coefficient's sign; the breakeven leg prices at the component sum, and §3.2's `n_components` form is low by 50.0% |
| **C80** | A term with no graded input is `None` and `total` refuses, naming every absent term |
| **C81** | A term the leg's `ReExpression` declares unmodelled is refused on that leg, read from the leg |
| **C82** | Cost per risk uses gross DV01; `us_breakeven_5y`'s gross ÷ net is 133.8915, and a leg with no rate sense is refused rather than returned as infinity |
| **C83** | Converted to yield, every TIPS profile respects the FRBSF paper's *"under a basis point"* bound |
| **C84** | The ladder is four multipliers × two conventions, and the convention arm moves `us_10y`'s cost per DV01 by 13.289% |
| **C85** | Every bias carries a direction; an unquantified magnitude is `None`; `compounded_bias` reports the count it could not include |
| **C86** | The series with no computable duration are exactly `DGS3MO` and `DGS6MO`, and cost per risk refuses them by name |
| **C87** | Every graded series either has a cost profile or a refusal reason, and the two sets partition `SOURCES` exactly |

---

## 3. Predictions, fixed before the run

**P1. No existing bar turns red.** D4's wording deliberately, rather than D6's narrowed form: D6
scoped P3 to one module and the surprise landed outside it.

**P2. `ENGINE_IMPORT_ROOTS` does not change.** The arithmetic is scalar — a sum over at most two
components — so `math`, `dataclasses`, `enum`, `collections.abc` and `__future__` cover it, and all
five are already in the census. numpy is not needed and will not be added.

**P3. The environment census does not move.** No bar here names a sibling repository path or reads
a certificate entry, so C72 still finds **18** conditional bars and C73 still **7** skips on a clean
machine.

**P4. C76 turns red on the run that has this document and not yet the discharge lines.** This
document makes `closed("D7a", docs)` true, and X4 and X5 are OPEN and owned by D7a. The register
gate written yesterday fires on its author's own next package, which is the first time it has had a
subject at all. Predicted as **red on the first run, green after §7 is written**, in the shape C34
went red at D6 and stayed red across two runs.

**P5. The spread term is the only one of four computable for all four legs of `US_CASH_BOOK`.**
Financing and roll are refused on `us_2y` and `us_10y` by D2's `ReExpression` and on every leg by
the absence of a graded repo series; impact is refused everywhere for want of an ADV. Predicted:
**one of four**.

**P6. The profile count lands at 17 priced and 6 refused, against the row's "≈20".** Stated because
the rider that closed X1 left exactly this habit behind — *"if writing a census, predict its size
before writing it"* — after nothing predicted that census would find eighteen bars, so eighteen
arrived as a discovery rather than as a scored miss.

**P7. The suite goes 83 → 94.** Eleven bars, C77–C87.

---

## 4. What this package does not do

- **It does not run the selection.** Greedy addition, the cost hurdle, leave-one-out and the
  counterfactual leg count are §1's stopping rule and belong to **D7b**, which scores H9. D7a
  scores no registered claim.
- **It does not supply the risk denominator the stopping rule uses.** That is component expected
  shortfall at 97.5% under Euler, which is **D9**. Cost per gross DV01 is a rates-only stand-in and
  is labelled as one.
- **It does not resize or re-express any leg.** `reference.py` is untouched, for the third package
  running: D4 declined the DV01 match and named D7b, D5 declined the `DGS2` substitution and named
  D7, and D7a declines both again. A package that both measures a book and rewrites it produces a
  measurement nothing can be checked against.
- **It does not grade a source.** X11 is opened, not closed. Grading needs an extraction and the
  extraction runs in curvecast.
- **It does not quote a price.** §6: *"A structure quoted as a price… output that reads as
  executable is a defect."* Every number here is a cost band input to a selection, and `CostBasis`
  is what keeps it from being read as anything else.

---

## 5. What would make this wrong

- **A cost number presented as a measurement.** DD74 makes it unrepresentable; if a later package
  widens `CostBasis`, that is the failure and the widening is the diff to look at.
- **A half-spread that is not a fraction of a quoting increment.** A fitted decimal here would be a
  calibration wearing a convention's clothes. C77 is the guard and it is an equality.
- **The ladder reported at one cell.** §3.5 exists because a point estimate of a cost is a claim
  nobody can support. ~~A caller taking the 1× `AS_QUOTED` cell and reporting it alone has defeated
  the whole apparatus, and no bar can stop that — it is a reading discipline, recorded here.~~

  > **Corrected 2026-09-16 (DD109), in the open rather than by editing.** The last clause is false.
  > The sentence's own word is **caller**, and a caller is what an AST scanner reaches — this
  > repository was already banning `net_dv01` as a divisor that way on the day this was written.
  > **C102** now holds the disposition of every module that reads the ladder, as an equality, and
  > it fires on exactly the selector described here. What is true, and all that was ever true, is
  > that no bar reaches a *reader* who quotes one cell out of a report; the claim was made about
  > callers and declined the guard that covers them. See
  > `RIDER_the_impossibility_claims_X16_does_not_cover.md` §2.1.
- **The compounded bias read as a single number.** `compounded_bias` returns the count of terms it
  could not include for exactly this reason; a caller dropping that half has restated X5 as a
  reassurance.
- **Gross DV01 mistaken for the risk budget.** It is a denominator of convenience for a rates leg.
  The stopping rule runs on expected shortfall and D9 supplies it.
- **X11 quietly not being answered.** C76 now makes that a red suite rather than a silence, which
  is the only reason opening a new item is a responsible thing to do.

---

## 6. Result

**CLOSED 2026-09-15.** `src/deskcraft/costs.py`, `tests/test_costs.py`, bars **C77–C87**, decisions
**DD74–DD83**. Suite **83 → 94**, green in 6.88s. Clean-machine acceptance **87 passed, 7 skipped**,
re-measured rather than arithmetic. `ruff` 0 findings on the pinned selection; `lint-imports` 2 kept,
0 broken. `meip` and `curvecast` untouched. `reference.py` untouched, for the third package running.

### 6.1 The scorecard

| | Prediction | Verdict |
|---|---|---|
| **P1** | No existing bar turns red | **MISS** — C10 fired on `BiasDirection` |
| **P2** | `ENGINE_IMPORT_ROOTS` does not change | HELD — the diff adds one line, to `MODULES` |
| **P3** | Census does not move: C72 still 18, C73 still 7 | HELD |
| **P4** | C76 turns red on the run that has this doc without §7 | **HELD, and measured** |
| **P5** | One of four terms is computable on all four legs | HELD — the spread term, exactly |
| **P6** | 17 priced and 6 refused, against the row's "≈20" | HELD exactly |
| **P7** | The suite goes 83 → 94 | HELD exactly |

Six of seven. The one that missed is the one D4's wording exists to catch, and it caught the same
thing it caught at D6.

### 6.2 P1 missed, on the same bar and for the same reason as D6

D2's **C10** — *no near-name may grow beside `Direction` or `Notional`* — refused this package's
first draft:

    AssertionError: a near-name grew beside the real one: ['BiasDirection']

Renamed to **`BiasSense`**, echoing D4's `RateSense`. **Never exempted**, which is the standing rule:
a boundary hit is fixed by renaming the symbol. This is the **second consecutive package** C10 has
caught — D6's `ViewDirection`, now D7a's `BiasDirection` — and the repetition is the finding, not the
fix. A bar that fires on two packages in a row against two different authors of the same idea is
holding a real naming pressure, not a stylistic one: when a package needs to say *which way something
points*, the word it reaches for first is `Direction`, and `Direction` is already spoken for. A third
package writing a `...Direction` should expect the same red and should not be surprised by it.

P1 was stated in **D4's broad wording deliberately**, after D6 narrowed its equivalent to one module
and the surprise landed outside it. The broad wording is what made this a scored miss rather than an
unnoticed rename.

### 6.3 What nothing predicted: §3.1's butterfly row

§0.7 caught `half_spread × n_components` contradicting §3.1 and stated the arithmetic on the
breakeven. It never looked **one table up**, at the row that introduced the same defect:

| Structure | Components | Cost | measured |
|---|---|---|---|
| 2s5s10s butterfly | 3 | 3 × | **4 ×** |

A 2s5s10s is `(+1, -2, +1)`. Three components, **four units of notional**, and a dealer charges the
spread on every unit crossed, not on every distinct name. `BUTTERFLY_RATIO = 4/3`, held by C79.

This was found while writing C79's mutation — and only because two *other* refusals forced the
mutation to be rewritten twice:

1. `Instrument("FLIPPED", …)` was refused by `book.py`: *"has coefficients that cancel but declares
   no neutrality"* — **DD17**, firing on a test fixture rather than on a leg.
2. `Instrument("DOUBLED", components=(Component("SVENY10", 2.0),))` was refused because **DD8**
   requires an `OUTRIGHT`'s single coefficient to be 1.0; size lives in `Notional`.

Rewriting the mutation as §3.1's own butterfly is what put a `(+1, -2, +1)` next to a table saying
`3 ×`. **The defect was found by machinery aimed at something else** — which is curvecast's standing
lesson from items 28 and 29, arriving here unprompted. A package's own bars passing is not evidence
that the package is right.

The build order's §3.1 is **annotated, not rewritten**, and so are §3.2, §3.3 and §3.5. Four of five
subsections of the commissioning document now carry a correction; the headline sentence of §3.1
survives all of them, moving from *"two to three times an outright"* to two to four, in the same
direction.

### 6.4 A defect in this package's own module, found by a bug in its own test

C84's first draft called `annualised_cost(_leg(leg_id), 1.0, Maintenance(4.0))`, passing a
`Maintenance` positionally into the `depth` parameter. **The module accepted it silently** and
returned an answer. The test bug was mine; the module's willingness to take a `Maintenance` where a
`MarketDepth` belongs was a real gap, and fixing only the call would have left it. Both were fixed:
the call is keyword-form, and `annualised_cost` now `isinstance`-checks `depth` and `maintenance`.

Recorded because the temptation was to fix the test and move on, and because this is the second thing
in this package a test found in the code rather than in itself.

### 6.5 P4, scored by experiment rather than asserted

C76 was written yesterday by the rider that closed X1 and X8, and it **passed vacuously** — no
package owing an open item had landed. This document landing makes `closed("D7a", docs)` true, so the
gate finally had a subject.

Rather than assert the prediction, it was run: §7 was trimmed off this document, `test_carried_items.py`
was run, and C76 went red naming both items in the declared form —

    X4: D7a has landed and its pre-commit does not say what became of it.
        Write `**X4** -- discharged:` or `**X4** -- carried to <D>:`

— then §7 was restored and it went green. **The gate fires on its author's own next package**, which
is the only kind of evidence a gate written against a vacuous subject can offer.

It cost a second red, one register away, exactly as designed: closing X4 and X5 in
`docs/CARRIED_ITEMS.md` broke `DECLARED_OWED`, because the declaration is an **equality** and not a
floor. Two documents and one declaration had to agree before the suite went green — the same friction
C34 produced at D6, and the reason it is worth having.

### 6.6 What D7b inherits

- **X11**, opened here. Two of the four cost terms have no graded input in this repository, and §3.3
  claims one of them does. Grading needs an extraction and the extraction runs in curvecast.
- **X3**, which it already shared with D9.
- **`us_breakeven_5y` declares `Neutrality.DV01` and does not have it** — D4 measured 370.67/bp on
  $50m and named D7b for the re-expression. D7a has now measured the *cost* consequence of the same
  defect: dividing cost by `net_dv01` would overstate that leg's cost per risk **133.89-fold**. The
  re-expression is still D7b's, and now two packages have declined it for the same reason.
- **A short leg with no cost per risk.** `DGS3MO` and `DGS6MO` — the two series **D5 went and
  graded** — have a half-spread and no computable modified duration, so a stopping rule looking for a
  cheap front-end leg meets the refusal at the denominator rather than at the data (C86).
- **A leg count that is a lower bound.** Every quantified bias in `BIASES` runs `OVERSTATES_COST` /
  `FEWER_LEGS`, and the one unquantified bias — the Fed Board's own, which its paper declines to
  size — runs the same way. Whatever count D7b reports, the true count is that or higher.

### 6.7 What this package still gets wrong

- **`SEASONING_PENALTY` is a range carried as a tuple and never collapsed**, so nothing downstream
  can multiply by it without choosing an end. That is deliberate (§3.4's *"never reported at a point
  estimate"*), and it means D7b must decide something D7a refused to decide.
- **`compounded_bias` multiplies quantified biases as if they were independent.** They are not
  obviously independent — the par-proxy and annual-pay biases both come from the same MEIP
  approximation — and the product is reported beside the count rather than as a corrected number for
  exactly that reason. A defensible composition needs the covariance, which is D8's.
- **Nothing here is measured, and `CostBasis` is the only thing enforcing it.** C78 holds that the
  enum has no `MEASURED` member. It cannot stop a profile being given a wrong number under an honest
  basis, and no bar can.

---

## 7. Carried items

**X4** — discharged: the bias is on the cost object, with its direction, as `BIASES["par_proxy_duration"]`. Its
magnitude is stated as **13.289%** — the amount a reported *cost per unit of risk* is overstated by
— and not as X4's own 11.730%, which is the amount the *denominator* is understated by; §0.4 has the
arithmetic. Direction `OVERSTATES_COST`, consequence `FEWER_LEGS`, so the leg count D7b produces
under the par-proxy arm is a **lower bound** on the leg count the quoted convention produces. The
bias is **live only under `DurationConvention.PAR_PROXY`**: D4 already declined that proxy for the
three continuously-compounded legs, so the default arm carries none of it, and DD82's second ladder
axis is what makes the difference visible instead of assumed.

**X5** — discharged: §3.5's ladder gains a second axis, `DurationConvention`, so the eight cells
report the convention's contribution separately from the cost multiplier's. §0.9 is why it had to be
an axis and not more rungs — the convention effect is 0.1800 of a rung and cannot produce a flip
between rungs at any multiplier. The item's own count is **corrected upward rather than reassured**:
X5 says two conservative biases point the same way, and §0.5 finds a third in D4's DD52, which left
the annual-pay approximation as a magnitude with no direction. All three are in `BIASES` with
directions, and `compounded_bias` reports the product of the quantified ones beside the count of the
unquantified ones, which is one — the Board's bid-ask bias, which its own paper does not quantify.

**X11** — carried to D7b: opened by this package and not closable by it. §3.3 names two inputs —
NY Fed FR 2004B primary-dealer volumes for the impact term, and repo/SOFR for the financing term —
and says of the second *"both already graded"*, which §0.2 measures as false. Neither has a row in
`sources.py` nor a column in the committed panel, so two of the four cost terms have no input here
and `AnnualisedCost` reports them as absent rather than zero (DD79). Grading a source means an
extraction and the extraction runs in curvecast, which holds the egress. D7b owns it because D7b is
the package that needs the numbers to run the selection at all.
