# Rider — the six decisions `AMENDMENT_A5` §9 left with the owner

*Taken 2026-09-22, at `8b7e5dc`, after `AMENDMENT_A7` ran the admission test.*

`AMENDMENT_A5` §9 listed eight decisions and took none of them. Two have since been taken by
documents that had to take them in order to say anything at all: **row 1** by DD118 (read yes,
commit no) and **row 3** by DD120 and then DD122 (the candidate-set rule, and the amendment that
followed running it). **Six were still open this morning.** This rider takes all six.

**It is a rider and not an amendment**, under the standing rule that a new amendment is warranted
only when the problem could change a verdict. None of the six changes a verdict. Four of them are
refusals to change anything, one moves a grammar term's frequency without moving its meaning, and
one states a number the cost model already accepts from its caller. What they change is the
register: after this document, **no row of `AMENDMENT_A5` §9 is waiting on the owner.**

Each decision below carries the measurement it turns on. Where the measurement was made elsewhere
it is cited rather than restated, and where it is new it is beneath the decision.

---

## 0. The six rows, and the one fact each turns on

| §9 row | Decision | The fact it turns on | Taken as |
|---|---|---|---|
| 2 | Wave 1 — bills, TIPS reals, spot FX, all three or fewer? | After DD122 all three are refused, and **not one of them by preference** | **DD123** |
| 4 | The two broken words | One is closed by licence and one by a missing refusal — different defects, different packages | **DD124** |
| 5 | Is X17 pulled forward? | The first caller that needs it is D9, and there is no second one | **DD125** |
| 6 | Who owns DEC-2's cross-market work | The budget is frozen at twenty-one one-in-one-out and nothing has been removed | **DD126** |
| 7 | Paper 2's commodity arm | The series covers nine of eleven out-of-sample years | **DD127** |
| 8 | FR 2004B — a depth, or the share-alike into the archive | `costs.py` already accepts a caller-stated `MarketDepth` | **DD128** |

Six decisions, and **five of them decline to do something**. That is worth saying plainly at the
top rather than letting it emerge: this rider is mostly a record of work not commissioned. The
justification for each is a measurement, and §8 lists what each one would take to reopen.

---

## 1. DD123 — wave 1 is empty, and it is empty on measurement

> **DD123 — no series is admitted in wave 1. The candidate pool stays at eleven, the universe at
> 231 structures and 462 legs.** Bills, TIPS reals and spot FX are each refused, and each is
> refused by a rule that was written before the candidate was measured. `AMENDMENT_A5` §9 row 2 is
> closed. This decision admits nothing and therefore restates nothing under DD120 clause 4.

**Bills — refused twice, and the second refusal is the informative one.** `DGS3MO` and `DGS6MO`
were already outside the pool by the pool rule, held by **C104**: a structure naming either refuses
by name at the duration. That refusal was structural and a reader could reasonably have asked
whether it was merely conservative. `AMENDMENT_A7` answered it on the panel. On clause 2's actual
sample `DGS3MO` leaves **0.959** of its daily-change variance unexplained — which under the old
fixed `0.25` would have made bills the single most attractive thing in the free universe — and the
whole of that residual is **1.004 bp** against a published increment of **1 bp**, on a series that
does not change at all on **49.6%** of those days. `DGS6MO` reads 0.920 and **51.2%**. DD122 part 3
refuses both outright. **The most attractive candidate by the old statistic is the deadest series on
the panel**, and that is now a measurement rather than a judgement.

**TIPS reals — refused at clause 1, and the direction leg of the old refusal is withdrawn.** The
grammar slot a real-yield series would fill is already filled, by `DFII5`, `DFII10` and `DFII30`.
Clause 1 does not consult direction, so the refusal does not depend on the statistic — which is
fortunate, because `AMENDMENT_A6` §3's registered prediction that the GSW TIPS zeros would read
below 0.25 is **false** at the nearest proxy the tree supports (0.283 on the eleven, 0.387 on the
longer sample; `AMENDMENT_A7` §5). That section already names the discomfort and does not repeat
it here. **This decision rests on clause 1 alone.**

**Spot FX — refused at clause 1, and it is the interesting refusal.** `DEXUSEU` is the one series
on this panel that passes the amended direction test: **0.905** against a hurdle of 0.648, a
residual of 0.00737 against a published increment of 0.0001 — **73.7 increments**, not one — and it
moves on **99.0%** of the sample's days. It is genuinely new information by every test this
repository has. It is refused because **the grammar has no sentence for it.** DD63 closed the
grammar at six terms; none of the six is an exchange rate; admission under DD120 is admission *to a
slot*, and there is no slot. Adding one is a grammar change and a grammar change is not a data
decision.

**So wave 1 shrinks to nothing by three different rules, and none of them is preference.** That is
the outcome X24's body registered as its own closing condition, and it is now also §9 row 2's
answer. The pool figures are unchanged and are restated here only because a reader arriving at this
row will want them: **eleven series, 231 structures, 462 legs** — 11 outrights, 55 spreads, 165
butterflies, each long and short. Held by **C103**.

---

## 2. DD124 — neither broken word is removed; one moves frequency and one waits on a refusal

> **DD124 — `CREDIT_VS_RATES` moves to monthly and `CROSS_MARKET` keeps its word. Neither term is
> removed from the grammar.** The execution of the move belongs to **D8** under **X2**'s frequency
> policy, and the yen leg is **not** commissioned by this decision. `AMENDMENT_A5` §9 row 4 is
> closed. The binding half of the second word is **X19**, which is D9's.

`AMENDMENT_A5` §9 row 4 offered three moves on two words and the two words turn out to have nothing
in common but their symptom. Taking them separately is most of the decision.

**`CREDIT_VS_RATES` is closed by licence, and monthly is not a compromise — it is the only lawful
shape.** DD116 measured this: there is no daily credit series anyone may redistribute, Moody's
forbids reproduction outright and ICE restricts to internal use, and **no widening of DD35 reaches
either** because both are stricter than attribution. What is free and public domain is monthly:
Treasury's HQM curve from 1984, and the Board's excess-bond-premium file that already carries
`GZ_SPREAD` — which is `PUBLIC_DOMAIN` and is **already in `panel_monthly_dev_20260914.csv`**. So
the move costs no fetch, no licence decision and no new source. What it costs is a frequency
policy, because a grammar with one monthly term and five daily ones has to say what a view means
when it mixes them. **That policy is X2's, and X2 is D8's.** This decision settles the *direction*
and leaves the mechanism where the register already put it.

**Removal was the live alternative and it is refused on the same ground that DD120 refuses
additions.** Removing a term is as much a change to a closed grammar as adding one. DD63 closed it
at six; `AMENDMENT_A1` §6 freezes the package budget one-in-one-out; the discipline that makes the
grammar worth anything is that it does not move when the data is inconvenient. A term that reaches
monthly data is not a term that reaches nothing.

**`CROSS_MARKET` is a different defect wearing the same symptom, and the yen leg is not the fix.**
Before DD118 the yen leg was blocked by licence; DD118 lifted that (the Japan MoF file is PDL 1.0
and modifiable, from 1974-09-24). After DD120 and DD122, adding it is no longer a licence question
at all — it is **an ordinary admission**: a fetch, a grade, a joint-sample measurement against the
pool, and a restatement of the three counts under clause 4. That is package work and it is D8's
when D8 runs. **This decision does not commission it**, for the reason DD126 gives below: the
budget is frozen and nothing has been removed to pay for it.

**What actually binds today is X19, and it is worth being exact about the cost.** `views.fidelity`
raises `UnreachableFactor` for a factor no leg reaches (DD65). `generator.select` has **no
equivalent refusal for a half-reachable one**. So a `CROSS_MARKET` view returns a single 10-year US
leg at cosine **0.707**, with a Gram overlap `LEVEL·CROSS_MARKET` of **+0.2717**, and `book()`
reports a sentence about costs that is true of an empty selection caused by costs and false of one
caused by missing data. **Until that refusal fires, every fidelity number computed for
`CROSS_MARKET` is a number about `LEVEL`** — and H3's PASS rests on a **4.991%** margin between
those two. That is the half of row 4 that can change a claim, it is already an item with an owner,
and this decision changes neither.

---

## 3. DD125 — X17 is not pulled forward

> **DD125 — X17 stays where it is, with D9.** DD17 is not widened ahead of a caller.
> `AMENDMENT_A5` §9 row 5 is closed. The item's status, owner and body are unchanged; only the
> question of pulling it forward is answered.

X17's own body decides this row, which is the cleanest outcome a §9 row can have. The first caller
that needs a DV01-matched structure is **D9**. There is no earlier one. Widening DD17 before a
caller exists is **widening a guard for nobody** — the anti-pattern DD74 was written against and
the one D7a's `CostBasis` prohibition enforces one level down.

**The cost of deferring is measured and it is flat.** One annotated object carries the narrowness,
and **C109** prevents a second appearing. The cost does not grow with time, which is the property
that makes deferral safe here and does not make it safe for X19 (whose cost is a live margin) or
for X20 (whose cost is a promise the code keeps making).

**And pulling it forward would not buy the thing it looks like it buys.** The coefficient axis —
the PCA-weighted butterfly weighting that is the one cheap expansion path left — needs the
generator to emit non-unit coefficients as well. Widening DD17 alone delivers half a mechanism to
no caller. Both halves land in D9 or neither does.

---

## 4. DD126 — DEC-2 is not commissioned; the deferral becomes a decline

> **DD126 — no package is commissioned for DEC-2's cross-market work, and D16 reports it as a
> decline** with `AMENDMENT_A5` §3's measurement behind it, in the row that already promises
> *"H1–H9 scored as written, limits, and the declines."* `AMENDMENT_A5` §9 row 6 is closed.
> **X20 stays OPEN**, and this decision says exactly why.

The budget is **twenty-one core packages, one-in-one-out**, frozen by `AMENDMENT_A1` §6 and checked
as an equality by **C35**. Nine have landed. Commissioning DEC-2's package means removing one of
the twelve that have not, and no candidate for removal has been proposed, measured or defended.
X20's own body put this correctly: what was unowned was never the measurement — A5 §3 made that —
**it was the decision**. This is the decision, and it is no.

**A deferral that never executes is a decline, and it should be written as one.** The reader of the
paper is currently told a direction was deferred when it was declined. D16's second half is
reporting the declines; this is one, and it arrives with its measurement already made: the ESCB
re-use policy covers the German curve provided the source is quoted and the statistics are not
modified; Japan MoF's JGB file is PDL 1.0, modifiable, from 1974-09-24; `DE_ZERO_10Y` grades
`CITATION_REQUIRED` with a no-modification condition the `Licence` enum has no term for (DD114 —
which is X22's subject, and X22 is D8's).

**X20 does not close here, and that is the point of C118.** Six sites in `src/deskcraft` still
promise a package that will not exist — `costs.py:323`, `factors.py:107`, `reference.py:27` and
`:247`, `sources.py:315` and `:319` — plus one landed pre-commit. Rewriting those sentences is a
**code change**, and a code change belongs to a package, not to a rider. Until the code stops
saying *"DEC-2's later package"*, the repository is still making the promise this decision
withdrew. **A decline taken in a document while the code keeps the deferral is the same defect one
level up from the one X20 was opened for**, and §7's bar exists so that it cannot be closed in that
state.

---

## 5. DD127 — Paper 2's commodity arm is declined, and the decline carries its search

> **DD127 — Paper 2's commodity arm is declined.** The decline is reported by **D17** with the
> coverage measurement and the bound on what was searched. `AMENDMENT_A5` §9 row 7 is closed.
> **X21 stays open** until D17 lands and writes it.

Build order §0 item 6 withdrew the blanket futures decline for energy on the ground that the EIA
publishes NYMEX WTI contracts 1–4 daily, free, public domain, individually dated, from 1983. ~~Three
of those four halves hold.~~ Two of those four halves hold *(public domain struck 2026-09-26, DD176)*. **The coverage half does not**: the EIA states prices after
**2024-04-05** are unavailable. The out-of-sample window is 2015-01-01 → 2025-12-31 (DD98). So the
route that dissolved the splice objection reaches **nine of eleven** out-of-sample years and stops
**twenty months short** of the window it would be scored on.

**Twenty months is not a rounding error on an eleven-year window, and the arm cannot be scored
honestly on a truncated one.** Scoring it on 2015–2024 and reporting it beside claims scored on
2015–2025 is the shape this repository refuses everywhere else: a verdict that keeps the sample it
was scored at, or it is not a verdict.

**Two things travel with the decline and neither is optional.** First, **its search** — A5 §0
row 17 records what was looked at, so the decline is a measured refusal and not a shrug. Second,
**its bound**: A5 §0 row 1 is explicit that recall is unmeasured. Nobody has established that no
free, public-domain, window-covering WTI settlement series exists; what has been established is
that the one this repository found stops in April 2024. **The decline says that, in those words.**
A decline that overstates its own reach is worse than no decline, because it is the sentence a
later reader will cite.

---

## 6. DD128 — state the depth; FR 2004B's bytes stay out of the archive

> **DD128 — the impact term is closed by a caller-stated `MarketDepth` with its basis named. FR
> 2004B is not committed.** `AMENDMENT_A5` §9 row 8 is closed. This decision creates no item and no
> out-of-git dependency.

FR 2004B's terms are **attribution with a share-alike clause**: a redistributor must pass on *"the
same permissions, conditions, and restrictions."* Distribution here is **`git archive HEAD` and
nothing else** — so committing FR 2004B's bytes would attach those conditions to **every archive
this repository ever sends**, in perpetuity, for a single depth number in a cost model. That is a
decision about the distribution channel and the price is wildly out of proportion to the input.

**The route that works today needs nothing.** `costs.py` already accepts a caller-stated
`MarketDepth` and refuses only in its absence. A stated depth with its basis named closes X11's
impact half at the cost of one documented number. It requires no fetch, no fixture out of git under
DD118's middle band, no licence grade, and — importantly — **no predicate the type system lacks**,
which is precisely what X22 says is missing and what would otherwise have to be built first.

**What this does not do.** It does not grade FR 2004B, and it does not close X11. X11's data half
reads *"grade FR 2004B and H.15 and the cost model is whole"*; A5 §6.3 already struck that as
stated, because grading FR 2004B converts an ungraded input into a graded uncommittable one rather
than closing anything. H.15 is untouched by this decision. **X11 stays open with D8**, and its
impact half now has a route rather than a blocker.

---

## 7. C118 — the decline cannot be written while the code keeps the promise

**The bar.** `test_carried_items.py::test_c118_the_dec2_deferral_is_counted_where_it_is_made`.

DD126 declines DEC-2's package in a document. Six sentences in `src/deskcraft` still tell a reader
that a later package will do the work. Those two states are not compatible, and the register's own
history says which way the drift runs: a claim in prose beside a guarded structure is the thing
`RIDER_the_register_counts_itself_in_prose.md` exists as standing evidence about.

**What it holds, as an equality against the tree.** Exactly **six** `DEC-2` references live in
`src/deskcraft`, across exactly **four** files — `costs.py`, `factors.py`, `reference.py`,
`sources.py` — and that count and that file set are what **X20**'s body states. And **X20 is
OPEN**: the bar refuses a tree in which the item has been closed while the code still defers.

**How it goes red, which is the only interesting part of a green bar.**

- **X20 closed with the code unchanged** — the state DD126 makes tempting, since the decision is
  taken and the item looks answered. Red.
- **A site added or removed without the register moving** — a seventh deferral, or a fifth file, or
  five sites after a partial rewrite. Red, naming the difference.
- **A new deferral to a package that no row commissions, with no item at all** — the defect X20 was
  opened for, reappearing under a different name. Red at the count.

**How it goes green, and it is green two ways.** Rewrite the six sentences and close X20 in the
same commit, or leave both alone. What it refuses is exactly the half-state.

**What it is not.** It is not a general detector of unowned deferrals — it knows one deferral by
name. **C76** is the bar that walks every open row to an owning package and demands a written
discharge when that package lands; this one holds a single promise's arithmetic between a document
and a tree. The two are complementary in the way C116 and C117 are: C76 asks whether an item has an
owner, C118 asks whether the code still contradicts what the owner decided.

---

## 8. What this could still get wrong

Six decisions, and each is reopenable on evidence. Naming the evidence is cheaper now than
reconstructing it later.

1. **DD123 rests on DD122's part 3 thresholds** — one published increment, and 20% of days
   unchanged. Those are `AMENDMENT_A7`'s numbers and its §8 already lists what is soft about them.
   If part 3 moves, bills' refusal falls back to C104 alone, which is structural and survives.
2. **`DEXUSEU` passes everything except the grammar.** This rider refuses it on a slot, not on a
   measurement, and a reader may reasonably think a six-term grammar that cannot express a genuinely
   independent risk is the thing that should move. It is the strongest case against DD63 that this
   repository has produced, and it is made here rather than buried.
3. **DD124 splits one row into two defects and may be splitting it too cleanly.** If the frequency
   policy X2 produces turns out to make a monthly term unusable inside a daily grammar, then
   *removal* becomes live again — and this decision will have made it harder by putting the term's
   survival on record first.
4. **DD125 assumes D9 is the first caller.** That is read off the build order as it stands. A
   package reordering that puts a DV01-matched structure before D9 invalidates the reasoning, not
   just the timing.
5. **DD126 declines on a budget that nothing has tried to pay for.** No removal candidate was
   proposed. It is possible the right answer was to remove a package and buy the foreign leg, and
   nobody ran that comparison. This decision is a refusal to spend, not a demonstration that the
   spend is bad.
6. **DD127's bound is the honest part and also the weak part.** Recall is unmeasured. The decline
   says so, but a decline whose own document admits it may have missed a source is a decline a
   later reader can reopen with one link.
7. **DD128 states a number instead of sourcing one.** A caller-stated depth is a defensible input
   and a weaker one than a measured file. What makes it acceptable is that the alternative attaches
   share-alike conditions to every archive — not that the number is good.
8. **C118 pins a count that a legitimate refactor moves.** Renaming a helper or splitting a module
   changes the file set with no change in meaning, and the bar will go red for a reason that is not
   a defect. That is the intended trade: it is cheap to restate and expensive to drift.

---

## 9. Result

**Six decisions taken. `AMENDMENT_A5` §9 has no row left with the owner.**

Five of the six decline to commission work, and each declines on a measurement: a pool rule and a
quantisation floor (DD123), a licence that no widening reaches (DD124), a caller that does not yet
exist (DD125), a frozen budget nothing has paid into (DD126), twenty missing months (DD127). The
sixth states a number the cost model was already built to accept (DD128).

**Nothing is added to the pool, the grammar, the budget or the archive.** The candidate universe
stays at eleven series, 231 structures and 462 legs. The grammar stays at six terms. The package
budget stays at twenty-one, one-in-one-out, nine landed. `git archive HEAD` picks up no new
conditions.

**Two items are deliberately left open by decisions that could have closed them.** X20, because the
code still promises what DD126 withdrew, and C118 now refuses the half-state. X21, because D17 has
not landed to write the decline DD127 takes. Both are debts with owners and dates, which is what
this register is for.

**Next free ids: C119 / DD129 / X26.**
