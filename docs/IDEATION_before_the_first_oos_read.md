# Ideation — the three levers, before the surface is touched

*2026-09-23, after `RIDER_DD137_the_credit_tier_admitted.md`. **This document decides nothing.**
It carries no `DD`, adds no `C`, opens and closes no `X`, adds no package, fetches nothing, and
reads no row dated after `DEV_END`. The budget stands at 21 and the next free ids are still
**C128 / DD138 / X26**.*

*Raised by the owner, who asked to ideate on improving the odds **before** D15 or any
out-of-sample surface is run. **C119** makes that notification machine-enforced and `DD133` puts
the owner in the loop; `DD134` requires D12, D14, D15 and D22 to be registered in **one**
pre-commit before the first read. This is the thinking that is owed **before** that pre-commit is
written — not the pre-commit, and not a substitute for it.*

---

## 0. Measured before argued

Every number below is read from the tree, not computed here.

| # | Measured | Value | Where |
|---|---|---|---|
| 1 | Grammar terms, closed by `DD63`, not a function of data | **6** | `AMENDMENT_A6` §0 row 5 |
| 2 | Leg count at view moves 0.25 / 0.5 / 1 / 2 bp | **0 / 1 / 2 / 2** | `PRECOMMIT_d7b` §3.2 |
| 3 | Leg count at 4 / 5 / **10** / 25 / 50 / 100 bp | 4 / 4 / **6** / 6 / 6 / 6 | same |
| 4 | Leg count at **10⁸ bp** | **6** | same, §3.2 trace |
| 5 | Book cosine at 10 bp and at 10⁸ bp | **0.906494022**, identical | same |
| 6 | Next-best gain ratio once six legs are held | **negative** at every magnitude | same |
| 7 | Factor space: PC1 / ~~PC1+PC2~~ PC1–3 / **effective rank** | 83.9352% / 97.9021% / **1.8231** | `BUILD_ORDER` D6 row *(label corrected 2026-09-25 by D8: 97.9021% is three components, as D6's pre-commit says; PC1+PC2 is 94.2347%)* |
| 8 | Of the six grammar terms, how many are **fitted** | **3** — the other three are *stated* at matched tenors | same |
| 9 | `LEVEL`'s margin over `REAL_VS_NOMINAL` / `CROSS_MARKET` | **4.991%** / 10.756% | same |
| 10 | Gram overlap among those three | **0.4434** and **0.2717** | same |
| 11 | `US_CASH_BOOK` legs / Roy–Vetterli effective rank | 4 / **< 3.0** (H4a PASS) | `AMENDMENT_A3` §262 |
| 12 | `DEXUSEU` daily-change variance unexplained by the eight zeros | **0.905** against a 0.648 hurdle | `RIDER_A5` §1 |
| 13 | — as published increments, and share of days it moves | **73.7 increments**; **99.0%** | same |
| 14 | `DGS3MO` / `DGS6MO` share of days **unchanged** | **49.6%** / **51.2%** | same |
| 15 | Candidate pool after `DD123` | **11 series, 231 structures, 462 legs** | `C103` |
| 16 | H5's pre-registered verdict | **FAIL** | `registers.py` |

**Row 5 is the one that reorganises the other fifteen.** The book's directional fidelity saturates
at **0.906494022** and does not move when the assumed view magnitude is raised by seven orders of
magnitude. That ceiling is a property of the vocabulary. **No cost model, no data admission and no
sizing rule can reach it.**

---

## 1. Lever 1 — is H9's 0–2 legs a cost-model artifact or a real vocabulary limit?

**Both, at different magnitudes, and the register already says so in a comment nobody has had to
read out loud yet.** `registers.py`'s note on H9: *"The margin is a property of the grid and not of
the structure."*

**The 0–2 is an artifact.** §3.5's ladder spans view moves of **2 bp down to 0.25 bp**. A macro
view that yields rise is tens of basis points. D7b named this itself, before its own run, as
**DD110** — *"the ladder does not reach the region a reader would assume"*. At a realistic 10 bp
the count is **6**. So the headline "0–2 legs" is a statement about an unrealistically small grid,
and nothing should be concluded from it about the engine's vocabulary.

**The 6 is real, and it is not about money.** Row 4: at **10⁸ bp** — a view of a million percent,
where cost is arithmetically irrelevant — the count is **still 6**, the cosine is **still
0.906494022**, and the next-best gain is **negative**. *No remaining candidate of the 231 raises
the book's cosine at all.* The greedy runs out of **fidelity**, not out of money.

> **So the answer is: the vocabulary limit is real, it is exactly quantified, and it is
> `0.906494022`.** The engine can express at most 90.65% of an arbitrary view direction, with at
> most six legs, at any cost and any conviction. That is the number to put in front of a reader,
> not the leg count — a leg count is a budget artifact and a saturated cosine is a structural one.

**And it bounds X11 on one side**, which D7b already recorded: grading every absent cost term can
only raise the count, and the count cannot exceed six.

**What I would put to the owner.** The engine's honest headline is not *"it picks 0–2 legs"* but
*"it spans 90.6% of view space and the last 9.4% is unreachable by construction."* The second is a
more useful sentence for a desk, it is falsifiable, and it is already measured.

---

## 2. Lever 2 — do A5's three ADD sources lift the leg count?

**No, and the reason is now sharper than when the question was framed. They cannot, in principle,
because the leg count is bounded by the grammar and not by the data.**

The question is also **already decided**: `DD123`, taken **2026-09-22**, admitted none of the
three. That decision stands and is not reopened here. But the three refusals are of different
kinds, and only one of them is load-bearing for what comes next.

| Source | Refused on | Would it lift the count? |
|---|---|---|
| **Bills** (4wk–1y) | **Measurement.** Unchanged on **49.6% / 51.2%** of days; the whole residual is **1.004 bp** against a **1 bp** published increment | **No.** *"The most attractive candidate by the old statistic is the deadest series on the panel."* Refused twice over, correctly |
| **TIPS real curve** | **Clause 1** — the slot is already filled by `DFII5/10/30` | **No.** A second occupant of a filled slot adds no direction |
| **Spot FX** (H.10) | **Clause 1 — the grammar has no sentence for it.** `DD63` closed the grammar at six terms and none is an exchange rate | **Not without a seventh term.** And it is *the* new direction: **0.905** against a 0.648 hurdle, **73.7 increments**, moves **99.0%** of days |

**The FX refusal is the interesting one and `RIDER_A5` says so in those words.** It is refused for
a reason that has nothing to do with licence, cost, quality or availability. It is *"genuinely new
information by every test this repository has"* and it is declined because **there is no slot**.

**Now put that beside §1 and beside row 7.** The six-term grammar compiles into a factor space of
**effective rank 1.8231**. Only **three** of the six terms are fitted at all; the other three are
*stated* at matched tenors. And of the fitted three, `BUILD_ORDER`'s own D6 row says they are
*"substantially the same nominal duration position counted through overlapping directions"* —
`LEVEL` leading `REAL_VS_NOMINAL` by **4.991%**, gram overlap **0.4434** and **0.2717**.

> **So the vocabulary is nominally six and effectively under two.** The engine saturates at cosine
> 0.9065 because most of its six named directions are the same direction wearing different names.
> **The one measured direction that is genuinely orthogonal to the curve is the one the grammar
> cannot say.**

**What I would put to the owner, as the single highest-value open question in the project.**
Not *"admit more data"* — DD123 answered that and answered it right. The question is:

> **Is a seventh grammar term worth a decision?** It is the only change that can move
> `0.906494022`. `BUILD_ORDER` §7.2 is the standing argument that *data does not buy a grammar
> term*, and that argument is sound — but it answers *"should data buy one?"*, not *"should
> anything?"* Those are different questions and only the first has been asked.

**I am not proposing it and it is not mine to propose.** A grammar change is a `DD63` reopening,
it invalidates C103's pool figures, it changes 231 structures to a different number, and it would
land against a frozen 21-package budget. It is a large decision. **But it is the only lever on the
number that actually binds, and it should be declined deliberately rather than by default.**

---

## 3. Lever 3 — should D15's nulls be chosen to be informative when it fails?

**Yes, and on the numbers above the current three are at risk of failing uninformatively.**

D15 runs against three pre-registered nulls: the **single-instrument expression**, **1/N across
the same legs**, and the **hand-built book** (`US_CASH_BOOK`, four legs — `DD93` corrected
"six-leg", which names no priceable object). **H5 is pre-registered `FAIL`**: *ES-constrained
sizing beats 1/N on Sharpe* is predicted not to hold.

**The problem is not that H5 is predicted to fail. It is that we can already say why it will.**

1/N and an ES-constrained optimiser differ only to the extent the legs differ. Row 7 says the
factor space has effective rank **1.8231**; row 11 says the hand-built book's four legs have
Roy–Vetterli effective rank **< 3.0**; row 10 says the fitted terms overlap at gram **0.4434**.
**Across legs that collinear, 1/N and any sizing rule converge by construction.** A `FAIL` would
then be re-measuring collinearity that D6 and D10 have already measured — and pre-registering the
prediction does not rescue it, because a test whose failure mechanism is known in advance is not
discriminating between hypotheses. It is confirming an arithmetic identity on an irreversible
surface.

**That is the argument for choosing the nulls to be informative under failure, and it is exactly
the owner's instinct.** Three concrete directions, offered as material for `DD134`'s single
pre-commit and not as a specification:

- **A null that is not collinear with the book.** The three current nulls are all drawn from the
  same 462 legs. A null the book cannot mimic — a duration-matched single instrument, or a
  deliberately mis-specified book — makes a `FAIL` say *which* of sizing and selection failed.
  Against the present set, a `FAIL` cannot separate them.
- **Report the separating statistic beside the verdict.** If 1/N and the optimiser converge, the
  informative number is *how far apart the weight vectors were*, not which Sharpe was higher.
  A near-zero weight distance turns an uninformative `FAIL` into a clean measured statement:
  *the optimiser had nothing to optimise over.* That is publishable; a lost Sharpe race is not.
- **Fix the failure grammar in advance.** `DD135` already requires every D15 choice D14 could
  inform to be a constant or a rule with one answer. The natural extension, and it costs nothing:
  **pre-register what each possible failure would mean** before the read, so no outcome can be
  narrated after the fact. `RIDER_C73` is the precedent — a bar that reports without a verdict.

**One caution on this lever, against my own suggestion.** Adding a null adds a comparison, and D15
counts trials for Deflated Sharpe and PBO. A fourth null is not free; it moves the DSR threshold
against every other claim in the package. **D7b reported three evaluation counts rather than
choosing for D15** precisely so this decision stays where it belongs. If a null is added, the
trial count must move with it in the same document, before the run.

---

## 4. What the three levers turn out to be

They are one constraint seen from three sides.

> **`DD63`'s six-term grammar, whose factor space has effective rank 1.8231, is the binding
> constraint on this engine — not cost, not licence, not data, and not sizing.**

- **Lever 1** measures it: cosine saturates at **0.906494022** and the last 9.4% is unreachable.
- **Lever 2** hits it from outside: the one genuinely new direction free data offers is refused
  because there is no slot, and no admission can create one.
- **Lever 3** is downstream of it: D15's nulls converge because the legs are collinear, and the
  legs are collinear because three of six terms are the same duration position renamed.

**And it reaches the owner's derivatives question directly.** The engine declines option pricing
under `DD121` on a licence argument, and that argument is sound and separate. But there is a
second reason, structural, that no licence change would fix: **`ViewFidelity.cosine` is a
directional statistic on the six-factor space. Convexity is not a direction.** A vanilla leg would
not raise the cosine by anything, because the metric cannot see what it buys. So the engine's
designed output — *"this exposure requires convexity; a vanilla is indicated; pricing it needs a
surface free data does not provide"* — is doing more work than it appears to: it is the engine
correctly reporting a deficiency **its own objective function is blind to.** Worth stating
explicitly somewhere, because a reader will otherwise assume the cosine already accounts for it.

---

## 5. What this document does not do

It takes no decision, and three of the questions above are the owner's alone: whether a seventh
grammar term is worth a `DD63` reopening, whether D15 gains a fourth null and pays the trial cost,
and whether the first out-of-sample read is authorised at all.

*(**Annotated 2026-09-25.** The first is answered: **declined for version 1**, `DD138`, with the
ceiling carried as the engine's headline limit (`BUILD_ORDER_D3_D16.md` §7.6). `DD139` adds the
half this document did not separate: the currency series the grammar cannot say is still a risk
D8 must measure, because `US_CASH_BOOK` holds it. The second and third stay open.)*

*(**Annotated again 2026-09-25.** The second is answered: **no fourth null (DD164)**, measured rather
argued. On a DEV pseudo out-of-sample split of the real record's length the optimiser and 1/N are
not the same book, but a Sharpe race needs 0.19 of annualised Sharpe to see their difference and the
most the view could plausibly give is 0.034: power 8%. H5 keeps its registration with its power
beside it. The third stays open, and the checklist it is decided against is §9.3 of
`PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md`.)*

**Nothing here touches the out-of-sample surface.** `docs/OWNER_AUTHORISATION_the_first_oos_read.md`
does not exist, no post-`DEV_END` row is read, named or committed, `C119` is not tripped, and
**curvecast's remaining two looks are unspent**. `DD134`'s single pre-commit for D12, D14, D15 and
D22 is still unwritten, and this document is input to it rather than any part of it.

*Next free ids, unchanged: **C128 / DD138 / X26**.*
