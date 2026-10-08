# Amendment A3 — the three sections nobody had read, and a bar I said could not be written

*Raised 2026-09-15, the same day `AMENDMENT_A2` closed, against
`docs/BUILD_ORDER_D3_D16.md` §2, §4 and §5.*

*A2 §12.5 left two things open and called one of them unwritable. It was wrong about that, and
right to be suspicious of the other.*

*Annotates the build order and the hypothesis register. Rewrites neither. D4's precedent.*

---

## 0. Measured before decided

Every number below was measured before any of §2–§9 was written, and each is reproduced by a bar.

| # | Measured | Value |
|---|---|---|
| 1 | `REFERENCE_BOOK.leg_ids` | **6** — and two of them, `eurusd` and `us_de_10y`, name a market that is not the US |
| 2 | `DEFERRED_LEGS` | **2** — `us_10y_call` (no free vol surface), `us_de_10y` (DEC-2) |
| 3 | `US_CASH_BOOK.leg_ids` | **4** — the priceable book, and the one D4 through D16 actually measure |
| 4 | Effective number of bets, one covariance of 8 GSW zeros, three uncorrelated bases (curvecast item 28) | **1.8231** (Roy–Vetterli), **7.9059** (min-torsion), **8.0000** (whitening) |
| 5 | `SCENARIO_SIGNS`: leg pairs with identical signs in all four scenarios | **1 of 15** — `us_2y` ≡ `eurusd`, both `(+1, 0, 0, −1)` |
| 6 | Clopper–Pearson 95% interval at 28/40 | **[0.5347, 0.8344]** → **[0.535, 0.834]** at three decimals |
| 7 | Modules under `src/` reading `COST_HURDLE` | **1** — `costs.py`, which also reads `COST_MULTIPLIERS` |
| 8 | Committed fixtures reaching past `DEV_END` | **0 of 2** — both are `*_dev_*`, 1988-01-01 → 2014-12-31 |
| 9 | Source-register entries; of D19's ~~nine~~ **eight** named vol inputs | **23**; **1** (`VIXCLS`) | *(corrected 2026-09-17, §9)*

---

## 1. The findings

A2 §12.5 closed with two open statements. This amendment takes both, and the second one opened
five more.

| # | Finding | Where | Severity | What it becomes |
|---|---|---|---|---|
| **1** | The cost hurdle is fixed and unenforced, and A2 said the bar could not be written here. **It can.** | A2 §12.5 | **High** | **C92** + **X12**, DD91–DD92 |
| **2** | **H8's level bar cannot fail.** ENB ≤ the leg count, and H9 predicts 3–4 legs | §5, and §5 again | **High** | H8 withdrawn as written, DD95 |
| **3** | **H4 and H8 name a "six-leg US book" that does not exist and could not be priced if it did** | §5 | **High** | Restated on `US_CASH_BOOK`, DD93 |
| **4** | **ENB < 3.0 is not a claim about a book. It is a claim about a basis** | §5 | **High** | Basis named in advance, DD94, **C94** |
| **5** | X3 is routed to **F4**; §2 calls **F3** the important flag and it breaks the same way | §2 | Medium | X3 widened, DD96 |
| **6** | No row commissions the post-DEV panel that D12, D14, D15 and D22 all need | §4 | Medium | Annotated, DD97 |
| **7** | D19 names ~~nine~~ **eight** vol inputs; the register grades one | §0 item 7, §4.1 | Low | Annotated |

**Findings 2, 3 and 4 are all H4 and H8.** Two rows of the hypothesis register carry three
independent defects between them, and the register has been read at every package since D1.

### 1.1 What the shape of these is

A2 found that §1 and §3 each contained *a cross-reference pointing at a number that does not
exist*. §5 contains that too — finding 3 is exactly it. But findings 2 and 4 are a second shape,
and it is the one A2's own headline was about:

> **A pre-registered threshold that is not determined until the package that scores it makes a
> free choice.**

`COST_HURDLE` was that. `ENB < 3.0` is that. In both cases the number reads as a fact about the
world and is a fact about a convention, and in both cases the package that would choose the
convention is the package the claim is scored by. A2 removed the first by algebra. This one
cannot be removed by algebra — a basis must actually be picked — so it is picked **here**, before
D10 exists, which is the whole of what "pre-registered" is supposed to mean.

---

## 2. Finding 1 — the bar A2 said could not be written

### 2.1 What A2 claimed

> **The hurdle is fixed and unenforced at the point that matters.** C91 pins the value and the
> identity. Nothing makes D7b *report the ladder*, and if D7b reports one cell the hurdle is a
> free parameter again under a different name. That bar belongs in D7b's pre-commit and **this
> document cannot write it**.

The last clause is false, and it is false in a way this repository has already demonstrated
twice. `C76` is a bar written by one package that turns red when a *later* package lands without
discharging an obligation. `C34` is a bar that was red from the moment D6's document landed until
D6 set a verdict. Neither needed the later package to exist. A bar that arms now and binds later
is the ordinary construction here, and A2 reached for "belongs in D7b's pre-commit" without
trying it.

### 2.2 The bar (C92, DD91)

The failure mode is precise: a selector reads `COST_HURDLE` and compares one cost against it,
never touching `COST_MULTIPLIERS`. The hurdle is then a free parameter again, because the ladder
that made `1.0` non-arbitrary is not reported.

**C92 walks every module under `src/` and requires that a module referencing `COST_HURDLE` also
references `COST_MULTIPLIERS`.** The reader census is an equality — today it is exactly
`costs.py`, which defines both — so the bar is *armed and true*, not vacuously passing. The day
D7b imports the hurdle alone, the suite turns red before the pre-commit is written.

**What this bar does not do, stated.** It proves a module *mentions* the ladder, never that it
*sweeps* it. A selector could import `COST_MULTIPLIERS` and evaluate one element. That residue is
not closeable by a bar over a package that does not exist, and it is what X12 is for.

### 2.3 X12 (DD92)

> **X12.** The hurdle is `1.0` only because the ladder is reported. Nothing yet requires D7b to
> report it. — owned by **D7b**.

`C76` already refuses to let a package land without writing `**X12** — discharged:` or
`**X12** — carried to <D>:`. So D7b cannot land silently on this, which is the enforcement A2
wanted and routed to a document that does not exist yet.

**Note the division of labour.** C92 is mechanical and catches the crude failure. X12 is
procedural and catches the subtle one. Neither alone is enough, and A2 had neither.

---

## 3. Finding 3 — the six-leg US book is not a book

§5's H4 reads:

> **H4** | Six-leg US book has ENB < 3.0 | D10 | PASS

There are two books in `reference.py` and **the phrase names neither**:

| | Legs | US-only? | Priceable? |
|---|---|---|---|
| `REFERENCE_BOOK` | **6** | **No** — `eurusd` is EUR, `us_de_10y` reaches the German curve | **No** — two legs are in `DEFERRED_LEGS` |
| `US_CASH_BOOK` | **4** | Yes | Yes — this is the book D4–D16 measure |

`DEFERRED_LEGS` is not a todo list. `us_10y_call` is deferred because **no free implied-volatility
surface exists**, and `reference.py` says in terms that a Black-76 leg fed from realised
volatility "would produce risk numbers that are artefacts of the input". `us_de_10y` is deferred
to DEC-2 with its own pre-commit and its own graded panel. **An ENB over the six-leg book requires
a covariance over two legs that this repository has refused to price, on the record, for stated
reasons.** H4 as written is not merely wrong about a count; it is scored against an object whose
construction the repository has already declined.

This propagates. §5's H8 compares the generated book against "hand-built", and §4's **D15** row
names its third pre-registered null as "**the hand-built six-leg book**". All three inherit it.

**DD93. The hand-built book is `US_CASH_BOOK`, at four legs**, everywhere the register and the
order say "six-leg". It is the only hand-built book that can be priced, and `reference.py` has
said so since D2: *"the four legs that free graded data reaches today … this is the book D4
through D16 actually measure"*.

**What that costs, stated rather than absorbed.** See §4.2 — it makes H4 a materially weaker
claim, and weakening a claim quietly is the thing this repository exists to not do.

---

## 4. Finding 4 — `ENB < 3.0` names a basis, and no basis is named

### 4.1 The measurement that already exists

curvecast item 28 measured Meucci's effective number of bets on **one** covariance of **eight**
GSW zeros, in three mutually uncorrelated bases:

    Roy-Vetterli effective rank (PCA)   1.8231  of 8
    volatility-preserving min-torsion   7.9059  of 8
    plain whitening                     8.0000  of 8

and recorded the conclusion in its own words: *"Three uncorrelated bases of one covariance, three
answers: **the statistic is a property of the basis choice**, and 7.9059 alone would say the curve
is well diversified, the opposite of what the covariance says."* The min-torsion figure is
*algebraically* the exp-entropy of the marginal variances — it carries no diversification
information at all, and item 28 proved that by closed form, by an SLSQP search over all 64
entries, and against the per-tenor vols.

**A threshold of 3.0 admits the first number and refuses the other two.** So on one covariance,
H4's verdict is PASS, FAIL and FAIL depending on a choice nobody has made.

### 4.2 And §4's own D10 row commissions all three

> **D10** | Effective number of bets | **All three of the ladder, each with its basis named.** Carries H4 and H8

The order knows. The hypothesis register does not. D10 is commissioned to produce three numbers
and H4 predicts PASS against one threshold, which means **H4's verdict is decided by which of
D10's three outputs gets compared to 3.0** — and D10 is the package that chooses. This is
`COST_HURDLE` again: a threshold that reads as a fact and resolves to a convention, with the
choosing done by the party being scored.

**DD94. The basis is Roy–Vetterli effective rank, fixed here, before D10 exists.** Two reasons,
both stated in advance:

1. It is the only one of the three that carries diversification information. Min-torsion is the
   marginal variances by an identity item 28 proved; whitening returns `n` exactly. A statistic
   that is constant by construction cannot score a claim about a book.
2. It is the one this repository has already restated at exact equality — D6's C60 executes
   curvecast's own `_pca` and reproduces 83.9352 / 97.9021 / effective rank 1.8231.

**D10 still reports all three.** The ladder is the deliverable; what is fixed is which rung H4 and
H8 are *scored on*. This is the `COST_MULTIPLIERS` construction exactly — report the sweep, fix
the cell the claim is read off.

**C94** requires every ACTIVE claim in `CLAIMS` whose statement names the effective-number-of-bets
family to name its basis. Today that is H4a, H4b and H8a; before this amendment it was nothing,
and H4 and H8 both failed it.

---

## 5. Finding 2 — H8's level bar cannot fail, and this is the headline

### 5.1 The arithmetic

The effective number of bets is the exponential of the entropy of the diversification
distribution over `n` bets. Entropy is maximised at the uniform distribution, so

> **1 ≤ ENB ≤ n**, with the upper bound attained only when every bet contributes equally.

Item 28 confirms the bound empirically: plain whitening of an 8-asset covariance returns
**exactly 8.0000**.

Now read two rows of the same register together:

| | Claim | Scorer |
|---|---|---|
| **H8** | Generated book beats hand-built on ENB; **both < 3.0** | D10 |
| **H9** | Cost-aware stopping terminates below six legs — **predicted PASS, at 3–4** | D7b |

If H9 passes as predicted, the generated book has **3 or 4 legs**. Then:

| Generated legs | ENB range | "< 3.0" is | Can it fail? |
|---|---|---|---|
| **3** | [1.000, **3.000**] | **100.0% of maximum** | **Only if the book is perfectly diversified** |
| **4** | [1.000, 4.000] | 75.0% of maximum | Rarely |

**At three legs the bar is satisfied by every book except the maximally diversified one.** H8's
level clause was written to detect a book whose legs are secretly one bet. It can only fail on the
book that is the exact opposite of that. **The clause does not merely fail to bind — its failure
condition is the outcome it was written to celebrate.**

### 5.2 Why nobody saw it

This is precisely the defect `AMENDMENT_A1` §5.1 found in H14 — *"the conjunction is vacuous: in
sample R² ≤ 1, so the decay clause strictly implies the level clause and the level clause can
never bind"* — and H14 was caught because both clauses sat **in one row**. Here the two halves sit
**four rows apart**, are scored by **different packages** (D10 and D7b), and the implication runs
through a bound (`ENB ≤ n`) that is stated in neither row. A1 fixed the instance and not the
class.

**DD95. H8's level clause is withdrawn as vacuous, and is not replaced by a different number.**
Choosing a threshold now — 2.0, or ENB/n < 0.6 — would be inventing a bar after noticing the
defect, which is what §5's own closing rule forbids and what D6 refused to do to `dominant_share`.
The informative quantity, **ENB ÷ leg count for both books**, is therefore reported by D10 **with
no threshold and no prediction**. That is not a dodge: the register already carries exactly this
disposition for `SCENARIO_SIGNS` — *"no prediction; the matrix is under-determined"* — and a
measurement with no bar is worth more than a bar that cannot fail.

### 5.3 What survives, and it is the half worth having

The **comparison** clause does not have this problem. "Generated beats hand-built" is a ranking of
two books computed in one basis on one covariance, and nothing about `ENB ≤ n` makes it automatic
— the two books have different leg counts, which is exactly why the comparison must be made on a
ratio and reported as a ranking. It becomes **H8a**, and it carries the content H8 was written
for.

---

## 6. The restatement (§5's table, and `registers.py`)

In the shape `AMENDMENT_A1` §5.1 set for H14: withdraw as written, name successors, move no
pre-registered threshold. `Claim` already carries `ClaimStatus.WITHDRAWN` and `successors`, so
this needs no new machinery — the register was built for it.

| # | Claim | Scored by | Predicted |
|---|---|---|---|
| ~~H4~~ | ~~Six-leg US book has ENB < 3.0~~ | ~~D10~~ | **Withdrawn as written.** The six-leg book is not US-only and two of its legs are in `DEFERRED_LEGS`; and `ENB` is undefined without a basis. §3, §4 |
| **H4a** | `US_CASH_BOOK`'s four priceable legs have **Roy–Vetterli effective rank < 3.0** | D10 | PASS — **and weaker than H4 read.** At n = 4 the bar is 75% of maximum where at n = 6 it was 50% |
| **H4b** | The **same book, same covariance**, exceeds 3.0 under at least one other basis of D10's ladder | D10 | PASS — the basis-dependence, made falsifiable on this book rather than asserted from curvecast's |
| ~~H8~~ | ~~Generated book beats hand-built on ENB; both < 3.0~~ | ~~D10~~ | **Withdrawn as written.** The level clause cannot fail against H9's own prediction. §5 |
| **H8a** | The generated book beats the hand-built `US_CASH_BOOK` on **Roy–Vetterli effective rank**, both in the same basis on the same covariance | D10 | PASS — the comparison, which `ENB ≤ n` does not make automatic |
| **H8b** | **ENB ÷ leg count**, reported for both books | D10 | *no prediction; the level bar is withdrawn as vacuous and deliberately not replaced (DD95)* |

**H4b is the one that can be surprised.** It predicts PASS on the strength of a measurement taken
on a different book — eight GSW zeros, not four cash legs — and a four-leg book of highly
correlated duration positions could plausibly come in under 3.0 in all three bases, which would
falsify it. Every prediction A2 made was about A2's own mechanics; this one is not.

**H9 is left alone.** Its "below six legs" inherits §3's phantom — the priceable comparand is four
— and A2 already annotated its 3–4. Reopening it here would be a third amendment touching one row,
and the note in §11 is enough. **Flagged, not fixed.**

---

## 7. Finding 5 — X3 is routed to the wrong flag (DD96)

X3 is open and owned, and it says:

> D9 owns the corrected statistic, under **§2's F4 flag** — a partial contribution rather than a
> raw pairwise correlation.

But §2 says this about **F3**:

> **The important one.** A leg can pass F1 (plenty of risk) and pass F2 (not dominant) and still be
> pure downside, because the risk it adds points somewhere the view does not. **Only the
> fidelity-versus-risk split exposes it.**

The fidelity side of that split *is* `dominant_share`, and `views.py` has said since D6 that it
**does not split anything**:

> `dominant_share` is not a variance decomposition. The six directions are not orthogonal
> (`factors.FactorBasis.gram`), so the loadings do not partition anything.

So the non-orthogonality bites F3 harder than F4 — F4 wants a conditional correlation, which is a
different object, while F3 wants exactly the decomposition that does not exist — and **X3 names
only F4.** The flag §2 calls "the important one" is the flag the carried item does not mention.

**DD96 widens X3 rather than opening an entry**, on the precedent of curvecast's D414 and D421,
where both items ended by widening a guard instead of adding one. X3's body now names F3 as the
flag that depends on the split most directly, and D7b's pre-registered re-score covers it.

---

## 8. Finding 6 — the panel four packages need, that no row commissions (DD97)

`D3b` delivered **two fixtures, both DEV**: 1988-01-01 → 2014-12-31. **This repository holds no
row dated after `DEV_END`.** Now read four rows of §4:

- **D12** — "Dated replay on full history **including 2020 and 2022**"
- **D14** — "**~2,700 OOS days**"
- **D15** — the construction backtest
- **D22** — "conditional on **D12's dated crisis windows**"

`window.py` is explicit that this is intended, not forbidden: *"Every out-of-sample test in this
repo runs on the years after `DEV_END`"*, and DEC-1 *reads 2015 → present*. **The OOS period is
authorised.** What is missing is that **no row in §4 commissions the panel that covers it**, and
D3b's row — the one that would — scopes itself to DEV and closed.

This matters more than an ordinary gap because of **DD37**, which is already written into
curvecast's ledger:

> the non-look entry is written **now** … **taking effect at deskcraft's first read of a row dated
> after `DEV_END`** — none has occurred; deskcraft holds no data file … what a person has read
> cannot be unread.

So the first package that reaches for the OOS panel fires an **irreversible** foreclosure in a
sibling repository — of *curvecast's* remaining budget, not deskcraft's — and the order contains
no row at which that is anyone's decision. **DD97 annotates §4 rather than inventing a package**:
the budget is frozen at 21 and adding a row is the owner's, not an amendment's. What the
annotation fixes is that the trigger is named, at the row that will pull it (D12, running first of
the four), so it is taken deliberately.

**~2,700 is checkable and consistent.** 2015-01-01 → present at ≈252 sessions a year is ≈2,950, so
"~2,700 OOS days" describes an OOS panel ending in **2025**, not one ending today. Whoever builds
it should state the end date rather than inherit a figure written against a different one.

---

## 9. Finding 7 — eight vol inputs, one graded

§0 item 7 and §4.1's D19 row name **VIX, VIX9D, VIX3M, VIX6M, SKEW, VVIX, OVX, GVZ** — ~~nine~~ **eight**
inputs across level, term, skew and vol-of-vol. The source register grades **one**: `VIXCLS`, and
it carries the Cboe reprint permission and a named fallback.

This is §3.3's shape exactly — *"Fed H.15 and SOFR, both already graded"*, which was false — and it
is the third instance. **D19 is annexed, so nothing is blocked**, and the severity is low for that
reason alone. But the annex row is the *argument for un-annexing*, and ~~eight of its nine~~ **seven of its eight** inputs
have never been through a licence read. **Annotated, and not opened as a carried item**: an
annexed package's data gap is not owed by any core package, and X7 already forbids raising an item
whose subject a future run produces.

### Corrected 2026-09-17, while `BUILD_ORDER_D3_D16.md` §7.2 was being written

**This finding miscounted in its own sentence.** The list it prints — `VIX`, `VIX9D`, `VIX3M`,
`VIX6M`, `SKEW`, `VVIX`, `OVX`, `GVZ` — is **eight** names, and the same sentence calls it nine.
This document's own §0 row 9, §1's finding row 7 and this section's heading all carried the larger
number. The graded count of **one** was right and is unchanged, so the ratio is **seven of eight**, not eight of nine.

**Where the ninth came from, which is the part worth keeping.**
`RESEARCH_client_solutions_layer.md` §7 lists **nine** free vol series, and the ninth is
**`VXEEM`** — EM equity implied vol — which §4.1's D19 row dropped when it was written. This
finding took its **count** from the research layer and its **names** from the build order, and the
two lists differ by exactly that one series. That is this finding's own subject arriving one level
up: **a number stated beside a list that does not support it.** Nobody re-read the list against the
number. It stood in **seven places here** — §0 row 9, §1's finding row 7, this section's heading,
its list sentence, its ratio, §10's taxonomy and §11 item 3 — and in **two later documents**:
§4.1's D19 annotation, which §11 of this document prescribed, and `AMENDMENT_A5` §5.2.

**Nothing downstream moves.** The severity was low because D19 is annexed and it stays low; the
graded count, the licence facts and the argument are untouched. What changed on 2026-09-17 is that
the gap is no longer only annotated: `AMENDMENT_A5` §5.2 established that every one of those inputs
is equity or commodity vol and therefore **free** — without reading any of their licences — so the
half-decline is now a claim with no record behind it, and it is opened as **X23**, owned by **D16**.
The reason this finding gave for *not* opening an item — *"an annexed package's data gap is not
owed by any core package"* — is answered by giving it to the core package that reports the declines
rather than to the annexed one that would consume them.

---

## 10. What verified

Two claims in these sections were checkable arithmetically. **Both are exactly right**, and
saying so is the point of checking rather than auditing.

- **§2's F4 example.** *"This is the `us_2y` / `eurusd` case, visible in the source's own scenario
  table."* Measured: of the **15** leg pairs in `SCENARIO_SIGNS`, **exactly one** carries identical
  signs across all four scenarios, and it is `us_2y` ≡ `eurusd`, both `(+1, 0, 0, −1)`. The claim
  is not approximately right; it is the unique instance, and both legs are in the priceable book so
  D9 can actually score it.
- **§5's interval.** *"an outcome of exactly 28/40 clears the ≥ 70% bar while carrying a 95%
  interval of [0.535, 0.834]"*. Exact Clopper–Pearson gives **[0.5347, 0.8344]**, which is
  [0.535, 0.834] at three decimals. Both endpoints, correct as written.

**So the pattern is not "every section contains a wrong number."** It is narrower and more useful:
**the arithmetic in this plan is reliable, and the cross-references and the thresholds are not.**
Every defect A2 and A3 have found is one of two kinds — a pointer to something that does not exist
(§3.3, §5's six-leg book, D19's ~~eight~~ **seven** ungraded series), or a number that is not
determined until someone chooses (§1.3's hurdle, §5's ENB). Nobody has yet found an arithmetic
error in this document.

*(Annotated 2026-09-17, with §9's correction.* **There is a third kind, and it was in §9 while this
paragraph was being written.** A count stated beside a list that does not support it is neither a
pointer to something absent nor a number awaiting a choice: the eight names were all real, and
nine was fully determined — it was simply not how many of them there were. The closing sentence
survives **on its letter**, because no arithmetic was performed and none of what was performed is
wrong; counting is what it does not cover. The ungraded figure in the list above is corrected with
it. And *"this document"* reads either way — as the plan, which is what §10 audits, or as this
amendment, which is where the miscount was.*)

---

## 11. The annotations

Annotate, never rewrite — D4's precedent, and A2's.

1. **§2**, after the flag table: F3's split is the one X3 bites, and X3 named only F4.
2. **§4**, at **D12**: the OOS panel does not exist, no row commissions it, and the first read of
   one fires DD37 in curvecast. At **D15**: its third null is `US_CASH_BOOK`, four legs.
3. **§4.1**, at **D19**: one of ~~nine~~ **eight** inputs is graded. *(The annotation this line
   asked for was written on 2026-09-15 and took the wrong count into the plan with it; corrected
   at §9 above, and at the row itself, on 2026-09-17.)*
4. **§5**, at the table: H4 and H8 withdrawn as written, successors named, and the note that H4a is
   a **weaker** bar than H4 read — 75% of maximum against 50%.
5. **§5**, at **H9**: "below six legs" names the unpriceable book; the priceable comparand is four.

---

## 12. Predictions

Scored in §14. P1 and P2 are to be run, not argued — A2's §12.2 shape.

| | Prediction |
|---|---|
| **P1** | Exactly two existing bars turn red on the register change: the `CLAIMS` census and the claims/build-order cross-check |
| **P2** | C94 run against the **pre-edit** register names exactly H4 and H8 as the claims failing to name a basis |
| **P3** | C92 passes vacuously-but-armed today: exactly one module reads `COST_HURDLE`, and it reads `COST_MULTIPLIERS` |
| **P4** | The suite goes 98 → 102 |
| **P5** | `PACKAGE_BUDGET` is untouched at 21, and no row is added to §4 |
| **P6** | Gates clean; `meip`, `curvecast` and `reference.py` untouched |

**P6 names `reference.py` deliberately.** Three of this amendment's findings are *about* that
file's contents, and the temptation to edit it — to add a six-leg US book, or to un-defer a leg —
is exactly the pressure D4 refused when it found `Neutrality.DV01` false by 370.67/bp. The
measurements are right; the document that misdescribes them is what changes.

---

## 13. What this amendment could still get wrong

- **DD94 picks a basis, and picking is a choice this amendment makes on D10's behalf.** The
  argument in §4.2 is that two of the three rungs are constant by construction, which is a fact,
  not a preference — but it is still a selection made by the party writing the amendment rather
  than by the party running the package, and the honest mitigation is that it is made **before the
  book's covariance exists**, not that it is made by someone disinterested.
- **H8b reports a ratio with no bar, and a measurement with no bar is easy to not report.** X7
  forbids a carried item whose subject a future run produces, so there is no item holding it. C94
  requires the claim to name a basis; nothing requires D10 to publish the ratio. This is the same
  residue §2.2 leaves on the hurdle, and it is the same answer: the pre-commit, not the bar.
- **The six-leg book may be the right object and the deferral the wrong one.** If a free vol
  surface appears, `us_10y_call` becomes priceable and H4a's four legs are the wrong count again.
  DD93 fixes the book by name (`US_CASH_BOOK`), not by number, so the restatement follows the
  deferral rather than freezing a count — but §5's *threshold* is a count, and it would then be a
  50%-of-maximum bar again without anyone deciding to make it one.
- **§2 is still the least-tested section.** F1 and F2 were read and nothing was found, but they are
  definitions scored by a package (D9) that does not exist, and "nothing found" in a section with
  no executable content is the weakest kind of pass. **F1's own rationale names financing** —
  *"is paying spread and financing"* — which X11 records as absent from the cost model entirely.
  That is noted and not opened: D9 computes F1 from component ES, not from cost, so the phrase is
  rationale rather than arithmetic. If D9 ever computes F1 from a cost, X11 blocks it.
- **Three sections were read once, by one reader, in one sitting.** §1 and §3 each took a package's
  worth of implementation pressure before their defects surfaced. §2, §4 and §5 have had an
  afternoon. The four findings above are what one careful read produces; they are not a
  certificate.

---

## 14. Result

**CLOSED 2026-09-15**, the same day it was raised and the same day `AMENDMENT_A2` closed. Bars
**C92–C95**, decisions **DD91–DD97**. Suite **98 → 102**, green in 7.77s. Clean-machine acceptance
**95 passed, 7 skipped** — the *7* is the stable number and did not move, so all four new bars are
environment-independent. `ruff` 0 findings on the pinned selection; `lint-imports` **2 kept, 0
broken**. `meip`, `curvecast` and **`reference.py`** untouched. `PACKAGE_BUDGET` untouched at 21 and
no row added to §4. **Next free: C96 / DD98.**

### 14.1 The scorecard

| | Prediction | Verdict |
|---|---|---|
| **P1** | Exactly two existing bars turn red: the `CLAIMS` census and the claims/§5 cross-check | **MISSED, and measured** |
| **P2** | C94 against the pre-edit register names exactly H4 and H8 | **HELD, and measured** |
| **P3** | C92 passes armed: one module reads `COST_HURDLE`, and it reads `COST_MULTIPLIERS` | HELD — `deskcraft/costs.py`, alone |
| **P4** | The suite goes 98 → 102 | HELD exactly |
| **P5** | `PACKAGE_BUDGET` untouched at 21, no row added to §4 | HELD |
| **P6** | Gates clean; `meip`, `curvecast`, `reference.py` untouched | HELD |

**Five of six, and the miss is the useful one** — which is the opposite of A2, where seven of seven
held and §12.5 had to record that as a weak run.

### 14.2 P1 missed, and what it got wrong

The register change was run against the **pre-edit** §5 — `git show a4cd7b5:docs/BUILD_ORDER_D3_D16.md`
restored under the new `registers.py`:

    FAILED tests/test_guards_and_registers.py::test_the_claims_register_is_section_5
    FAILED tests/test_environment_census.py::test_a_clean_machine_skips_exactly_the_declared_bars
    2 failed, 100 passed

    assert not ['H4a is in one of the register and §5 but not the other',
                'H4b is in one of the register and §5 but not the other',
                ... 'H4: §5 status ACTIVE vs register WITHDRAWN',
                    'H8: §5 status ACTIVE vs register WITHDRAWN']

P1 named **two bars** — "the `CLAIMS` census and the claims/§5 cross-check". They are **one bar**:
C32 carries both the cross-check and the `len(CLAIMS) == 20` equality, so it reddens once and
reports both defects together. The second failure is the clean-machine census, which runs the suite
in a subprocess and is an **echo** of the first, not an independent finding — and it was not
predicted.

The count coincidentally matched at two. The substance did not. **A prediction about which bars
fire is a prediction about the shape of the guard, and I did not know the shape of a guard I was
editing** — which is exactly the error §13's last bullet warns about at a different scale.

### 14.3 What the measuring changed

Two of the seven findings came out different from the audit that opened them:

- **Finding 1 reversed A2's own conclusion.** A2 §12.5 said the bar "belongs in D7b's pre-commit
  and this document cannot write it". It took one look at `C76` to see that was wrong. **An
  amendment that names a gap and declares it unclosable should be read as a claim to check, not a
  result** — and the cost of not checking it was that `COST_HURDLE` sat unenforced for a day with a
  document saying that was unavoidable.
- **Finding 2 was not in the audit at all.** The plan was to check §5's cross-references, in §3.3's
  shape. H4's phantom book is that shape and was found that way. **H8's vacuity is not** — it is an
  interaction between two rows scored by two different packages, mediated by a bound (`ENB ≤ n`)
  stated in neither, and it only appeared because §3's measurement of *leg counts* was in front of
  me while reading §5's *thresholds*. `AMENDMENT_A1` §5.1 found the identical defect in H14 and
  fixed the instance rather than the class; C94 now holds the class for the ENB family, and nothing
  holds it for the register generally.

### 14.4 What this did not close

- **The class of defect A1 §5.1 found is still open.** C94 makes an ENB claim name its basis. No bar
  asks whether any *other* pre-registered threshold is implied by another row. H14 and H8 are two
  instances in a register of 24, both found by hand, both after the fact.
- **§2 is still the least-tested section**, for the reason §13 gives: it has no executable content,
  so a careful read that finds nothing is nearly worthless. F1 and F2 got one.
- **The post-DEV panel is named and not built** (§8). DD97 annotates the trigger at D12 and
  deliberately does not add a package, because the budget is frozen and that is the owner's call.
  **This is the one finding here that needs a decision from outside this document.**
