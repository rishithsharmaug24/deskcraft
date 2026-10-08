# D2 — book and leg types

Work package **D2** of `PLAN_deskcraft.md` §7, and the first row of the D2–D16 build order
approved 2026-09-05. Deliverable: frozen dataclasses for a hypothetical book, with
`Direction` and `Notional` living **here and nowhere else**, and the §6 reference fixture
expressed in them.

Decisions **DD8–DD21** (continuing D1's `DD` sequence). Bars **B10–B22**, executable as
**C10–C22** (continuing D1's `C` sequence, which is global because a `C` number is what gets
cross-referenced from another package). Predictions **P1–P8**, local to this package as they
were in D1.

**DD16–DD20 exist because the source conversation behind §6 was read directly** (§0.6) and it
turns out to be four-fifths relative value and two-fifths cross-currency, neither of which the
first draft of these types could express. **DD21 exists because this package produced a
finding and wrote it up without its null**, and caught itself in §3.3 rather than in review.

---

## 0. Measured before decided

Measured **2026-09-05**, on the production interpreter
`C:/Users/rishi/AppData/Local/Programs/Python/Python312/python.exe` (**3.12.10**).

### 0.1 C6 cannot see either of the two string positions D2 introduces

D1's `rendered_strings` reads **module-level UPPERCASE assignments** out of the AST. D2
introduces a `Book.thesis` field, so the first rendered strings in this repo sit in
**constructor-argument** position. Measured against the shipped scanner:

| source | `rendered_strings` returns |
|---|---|
| `REFERENCE = Book(thesis="you should reduce the front leg")` | `[]` |
| `NOTE = "you should reduce the front leg"` | `[('NOTE', 'you should …')]` |
| `note = "you should reduce the front leg"` | `[]` |

So the imperative ban is live for exactly the string shape D1 had, and blind to both shapes
D2 adds. This is the same class of gap the end-to-end demonstration found in C6's *first*
version, one package later and in a different position — which is the argument for widening
the scanner rather than for adding a second one beside it.

**Docstrings must stay excluded.** `src/deskcraft/__init__.py` contains the phrase
*"you should"* once, inside its module docstring, where it names the forbidden phrases in
order to forbid them. A guard that cannot describe itself is a guard that gets deleted.

### 0.2 `frozen=True` does not make an object immutable, but it does make it honest

| probe | result |
|---|---|
| `x.xs = [2]` on a frozen dataclass | `FrozenInstanceError` |
| `x.xs.append(2)` where `xs: list` | **succeeds** — `[1, 2]` |
| `hash(x)` where `xs: list` | `TypeError: unhashable type: 'list'` |
| `hash(y)` where `xs: tuple` | succeeds |

`frozen=True` rebinds `__setattr__` and stops there; a mutable field smuggled into a frozen
dataclass is still mutable. What it *does* buy is that the instance stops being hashable,
**at any depth**, because the generated `__hash__` hashes the field tuple. So one
`hash(book)` call is a deeper immutability check than any annotation scan, and it is what B11
uses.

### 0.3 The graded universe, as it actually stands today

`curvecast/src/curvecast/pit/archive_floors.py` carries **30** series with measured archive
floors. Relevant to this repo: `DGS5`, `DGS10`, `DGS30`, `DFII5`, `DFII10`, `DFII30`,
`T10YIE`, `VIXCLS`, `BAA10Y`, `AAA10Y`, `DEXUSEU`.
`curvecast.stage3.factor_space.TENOR_GRID` carries **8** GSW zero columns —
`SVENY01/02/03/05/07/10/20/30` — sourced from the file pinned in `docs/seal_manifest.json`
(16,988 rows, 1961-06-14 → 2026-07-24, sha256 `a0ecf2cf…`).

Two consequences that decide instrument choices below:

- **`T5YIE` has no measured floor.** A 5-year breakeven is therefore not a series here; it is
  the GSW 5Y zero **minus** `DFII5`, which is what `T5YIE` is anyway. That makes it a
  *derived* instrument whose grade is the worse of two components, and DD11 exists because of
  it.
- **`DGS2` has no measured floor** (M7 of the approved plan; it is one of the four the D5
  probe will add). So the 2-year leg is expressed on the GSW `SVENY02` zero, which is pinned,
  rather than on the FRED 2-year constant maturity, which is not yet graded.

### 0.4 The §6 fixture is stated in futures, and §4 declines futures

`PLAN_deskcraft.md` §2 describes the reference structure's first leg as *"a $200m two-year
futures leg"*, and §6 lists *short 2Y, short 10Y*. The approved plan's §4 declines any futures
leg — no free PIT-grade term structure exists, and every roll-adjusted continuous series is a
vendor product or a reconstruction whose splice rule is the model.

So the fixture cannot be carried **as stated**. Either it is dropped, or it is re-expressed.
DD12 re-expresses it in cash and records what that costs, because dropping the reference book
would leave every package below without the one structure the plan is written around.

### 0.5 `IntEnum` arithmetic and `StrEnum` availability

`int(Direction.SHORT) == -1` and `Direction.SHORT * 3 == -3`: an `IntEnum` member **is** an
int, so a direction whose value is its own sign needs no lookup table and no branch.
`enum.StrEnum` is available (3.11+). Both are stdlib; D2 adds no dependency, and
`pyproject.toml`'s `dependencies = []` stays empty until D4.

### 0.6 The source of §6, read directly, says three things §6's summary drops

`PLAN_deskcraft.md` §6 compresses the reference structure to one sentence. The conversation
it came from was supplied on 2026-09-05 as four screenshots, and read against the plan it
agrees on the six legs exactly — 2-year Treasury futures short, 10-year Treasury futures
short, 5-year inflation breakevens long, EUR/USD short, 10-year Treasury call options long,
US-German 10-year spread short. Three things in it are **not** in §6 and all three bear on
the types:

1. **Every leg is motivated as a distinct component of one thesis** — policy expectations
   (leg 1), term premium (leg 2), fiscal dominance / inflation (leg 3), the relative rate
   differential (leg 4), tail convexity (leg 5), relative supply (leg 6). Four of the six are
   **relative-value structures rather than outright positions**: legs 3, 4 and 6 are
   explicitly differences, and legs 1 and 2 are a policy-vs-term-premium *decomposition* that
   only means anything as a pair. A type that stores an instrument as a single name cannot
   express any of them.
2. **Two legs cross currencies** — leg 4 outright, leg 6 as a US-versus-German spread. Whether
   leg 6 is FX-hedged decides whether it is one bet or two, and the source does not say. That
   is a decision the object has to force rather than default (DD18).
3. **A scenario interaction table**, stated as the structure's justification: *"If the Fed
   signals fewer cuts → Leg 1 wins, Leg 2 partially wins, Leg 4 partially wins. If supply
   shocks hit → Leg 2 wins, Leg 3 wins, Leg 6 wins. If inflation surprises higher → Leg 3
   wins, Leg 5 might win. If everything goes wrong → Leg 5 limits downside, other legs lose."*

The third is the useful one, because it is the only part of the source that is **checkable at
all**. Its conclusion is *"the diversification comes from the fact that different legs profit
from different aspects of the same macro thesis"*, which is close to the claim the approved
plan's **H4** pre-registers as false — H4 predicts a Roy-Vetterli effective number of bets
**below 3.0** on six legs.

So the table is carried into the repo as a **pre-registered sign matrix** (DD20), one cell per
leg per scenario, and D12's replay scores it. Structured that way it stops being a rationale
and becomes 24 cells that either reproduce or do not.

**Stated carefully, because §3.3 had to walk back a stronger version of this sentence.** The
table and H4 are *not* strict contradictories, and the table is far too coarse to settle
anything on its own: four scenarios cannot separate six legs even in principle, 42% of its
cells assert nothing, and its most dramatic column moves five of six legs the same way. What
the matrix earns is a place in the register of pre-registered claims and a scorer in D12. What
it does not earn — and what the first draft of §3.3 gave it — is standing as evidence.

That is also the honest reading of the source: it is an articulate account of *why* someone
would put these six legs together, and §6 of the plan is already right that this is what makes
it worth decomposing rather than dismissing. The decomposition is what the source does not do.

---

## 1. Decisions

### DD8. The sign of a position lives in `Direction` and is unrepresentable anywhere else

`Notional.amount` is strictly positive and finite. `Direction` is an `IntEnum` whose *value*
is the sign (`LONG = +1`, `SHORT = -1`), so `Leg.signed_amount` is one multiplication with no
branch in it.

The bug this forecloses is specific and common: a leg carrying a **negative** notional *and*
`Direction.SHORT`, which is a long position that reads as a short one in every table. Under
DD8 that book cannot be constructed — `Notional(-2e8, USD)` raises at the boundary rather than
producing a sign error 400 lines downstream inside a component-ES attribution.

Zero is refused for the same reason an empty book is (DD15): a zero-notional leg contributes
nothing and survives every subsequent filter, so it is a leg that exists only to be miscounted
in a leg count.

### DD9. Immutability is asserted by hashability, not by the `frozen=True` keyword

§0.2 measured that `frozen=True` stops rebinding and nothing else. Every container field is a
`tuple`, and B11 asserts `hash(book)` succeeds — which fails loudly if any field at any depth
is mutable. Asserting that the keyword is present would be asserting the thing that does not
hold.

### DD10. Money never crosses currencies implicitly

`Book.gross_notional` **raises** on a multi-currency book. `Book.gross_by_currency()` always
answers, as a mapping. The reference book has a EUR leg, so the raising path is the one the
fixture exercises rather than a defensive branch nothing reaches.

There is no FX rate in this repo at D2, and putting one here would be the first fitted number
in a package that has none. When a cross-currency total is genuinely needed it arrives with a
dated rate from the D3 panel and a recorded decision, not as a default argument.

### DD11. An instrument declares the series it is built from, and priceability is derived

`Instrument.components` is the tuple of series identifiers the instrument is computed from —
`("SVENY05", "DFII5")` for a 5-year breakeven, `("DEXUSEU",)` for EUR/USD.

Priceability is then a **derived** property, checked against curvecast's measured floors read
at test time (B14), not a hand-maintained list in this repo. When D5 adds the four front-end
floors, the bar notices on its own; a hardcoded list would have gone quietly stale. Same shape
as C9, which parses curvecast's boundary file rather than trusting a copy of its contents.

### DD12. The reference book is re-expressed in cash, and the difference is stated, not modelled

§0.4: the fixture is a futures structure and §4 declines futures. It is carried as DV01-matched
**cash** legs on the GSW zero curve, and each such leg records on the object that its original
expression is a future and that **financing, the delivery option and roll are not modelled**.

This is a first-order equivalence and it is stated as one. What it is *not* is a claim that the
two structures are the same book — a futures leg carries a repo rate and a cheapest-to-deliver
option that a zero-coupon cash leg does not, and any later package that reports a carry number
on this fixture has to read that field or it is reporting a number the data cannot support.

### DD13. C6's scanner is widened to every non-docstring string constant under `src/`

§0.1. D2 is the package that introduces the first rendered string outside the one position C6
can see, so D2 is where the scanner is widened rather than where a second scanner is added
beside it. Docstrings stay excluded, explicitly and for the recorded reason.

The mutation leg is the point, and it is written in the shape D1's post-mortem prescribed: it
asserts the **scanner reaches a thesis-position string in a file**, not that a regex matches a
literal.

### DD14. `deskcraft/__init__.py` re-exports nothing

`__all__` stays `[]` and callers write `from deskcraft.book import Leg`. One binding site per
name is what makes the plan's *"`Direction` and `Notional` live here and nowhere else"* a
**scannable** claim (B10) rather than a convention someone remembers. A re-exporting package
gives every type two import paths, and the scan then has to decide which one is the definition.

### DD15. A book has at least one leg and no duplicate leg id

An empty book has no risk, and every ratio below — component share, effective number of bets,
concentration — divides by zero on it. Duplicate leg ids make component attribution
non-addressable: two rows called `us_2y` in an Euler decomposition cannot be told apart by the
thing that reads them. Both are refused at construction.

Two legs on the *same instrument* are allowed, because a book legitimately holds one, and the
id is what distinguishes them.

### DD16. Components are signed, so a relative-value structure is representable at all

§0.6: four of the six reference legs are differences, not outright positions, and the plan's
D6 view language needs `SLOPE`, `CURVATURE`, `REAL_VS_NOMINAL` and `CREDIT_VS_RATES` — every
one of which is a spread. So `components` is a tuple of `Component(series, coefficient,
currency)` with a **signed** coefficient, and a ten-year steepener is
`(+1 SVENY10, -1 SVENY02)` rather than a name that happens to contain the word.

`structure` is **derived** from the component count — one is `OUTRIGHT`, two `SPREAD`, three
`BUTTERFLY`, more `BASKET` — and never declared. A declared structure is a second place the
truth lives, and the two disagree the first time someone adds a wing to a fly.

### DD17. Neutrality is declared, because it is what makes a spread a relative-value leg

A two-legged instrument with no stated neutrality is an outright position wearing two names.
What a desk asks about a curve trade first is what it is neutral to — duration, cash, vega,
beta — and the answer changes the risk entirely: a DV01-neutral 2s10s steepener and a
cash-neutral one have different level exposure and therefore different component ES.

So `Neutrality` is declared, and the law it carries is an **iff**, checked in both directions
on every multi-component instrument:

> coefficients cancel to within `1e-12` **⟺** the neutrality is not `NONE`

Forwards it catches a spread written with two `+1`s and a stated hedge — the most common way a
relative-value leg is silently a doubled outright. Backwards it catches a balanced difference
that names no basis, which matters because *DV01-neutral and cash-neutral are different
positions* and a 2s10s with the question unanswered has unstated level exposure. An `OUTRIGHT`
is separately required to be exactly one component at `+1` and to declare `NONE`.

An unbalanced multi-component instrument with `NONE` stays legal, because a genuinely weighted
basket is a real thing; what is refused is the balanced one that declines to say what it is
balanced against.

### DD18. A cross-currency instrument must state whether it is FX-hedged. There is no default

§0.6.2. An unhedged US-versus-Bund spread is **two** bets — the spread and the currency — and
an FX-hedged one is one. Every effective-number-of-bets reading downstream depends on which,
and H4 is the finding the plan says is most likely to be inconvenient and most important to
publish. So `fx_hedged` is required to be `True` or `False` whenever the components span more
than one currency, and required to be `None` when they do not. Not a default, because a
default here is a silent answer to the question that decides the headline.

### DD19. Every kind maps to exactly one asset class, and the partition is total

The user's framing is legs *across* asset classes — rates, inflation, credit, FX, volatility.
`ASSET_CLASS_OF` maps every `InstrumentKind` to exactly one, and a bar asserts the mapping is
total and that its image is exactly `AssetClass`. That is what lets D9 report component ES **by
asset class** as well as by leg, which is the cut that shows a "five asset class" structure
collapsing into two, and it is cheaper to fix the partition here than to discover a kind with
no class in the middle of D9's attribution.

### DD20. The source's scenario table is carried as a pre-registered sign matrix

§0.6.3. *"Leg 2 partially wins"* is a claim about the **sign** of a leg's P&L in a named
scenario, and a sign is falsifiable. `SCENARIO_SIGNS` holds one cell per leg per scenario over
`{+1, -1, 0}`, written before any replay, and D12 scores it against realised windows.

The distinction between "wins" and "partially wins" is deliberately **dropped**: it is a
magnitude claim and the source gives no threshold, so recording it would be inventing a bar
after the fact. The sign is what was actually asserted and the sign is what gets scored — and
the matrix's own inconsistency with the source's diversification conclusion is exactly what
H4 measures.

---

## 2. What this package does not do

- **No arithmetic.** No DV01, no covariance, no VaR, no sizing. `signed_amount` and
  `gross_by_currency` are bookkeeping, not a model. `numpy` still arrives at D4.
- **No data.** No panel, no series is read, no file is opened by `src/`. The graded-universe
  facts in §0.3 are read by a **bar**, from curvecast, at test time.
- **No fit window.** `FitWindow` and the DEV guard are D3, together with the `scripts/` scan
  hole and the TRIAL_LEDGER entry.
- **No grade on the instrument.** `components` says what an instrument is built from; what
  those components are *graded* is curvecast's answer and D3's to carry into a panel.
- **It does not touch curvecast or MEIP.** Both are read by bars and modified by nothing.

---

## 3. Verification

### 3.1 Bars

| bar | what would falsify it | executable |
|---|---|---|
| **B10** | `Direction` or `Notional` being defined in more than one place, or a near-name growing beside them. AST scan over `src/`: exactly one `ClassDef` named `Direction` and one named `Notional`, both in `book.py`, and no other class name containing `direction` or `notional` case-insensitively. **Mutation:** a synthetic module defining `class SignedNotional` is caught by the same scanner. | C10 |
| **B11** | A mutable field surviving `frozen=True` (§0.2). `hash()` succeeds on every reference object; `setattr` raises `FrozenInstanceError`; every declared container field is a `tuple`. **Mutation:** the same hashability predicate is shown to reject a frozen dataclass carrying a `list`. | C11 |
| **B12** | A sign existing anywhere but `Direction`. `Notional` refuses negative, zero, NaN and infinite amounts; `Direction` values are exactly `{+1, -1}`; `Leg.signed_amount == int(direction) * amount` on every reference leg. **Mutation:** `Notional(-2e8, USD)` raises. | C12 |
| **B13** | USD silently added to EUR. `gross_notional` raises on the multi-currency reference book; `gross_by_currency` returns one entry per currency and each total matches the legs summed by hand. | C13 |
| **B14** | The priceable / not-yet-priceable partition drifting from what is actually graded. Read **from curvecast at test time**: the 30 measured floors and the 8 GSW zero columns. Every leg of the reference book is in exactly one of the two sets; every priceable leg has all components inside that universe; every deferred leg has at least one component outside it, or a kind with no series at all; the priceable book has **≥ 4** legs, which is the approved plan's §10 NO-BUILD floor. | C14 |
| **B15** | The imperative ban staying blind to the string positions D2 introduces (§0.1). The widened scanner finds no offence in `src/`, and **catches a `Book(thesis="… you should …")`** — the assertion is that the scan reaches a string *in a file*, not that a regex matches a literal. A docstring carrying the same phrase is **not** flagged, and `__init__.py` is the live case. | C15 |
| **B16** | A book that no downstream ratio can be computed on. Zero legs raises; a duplicate leg id raises; two legs on the same instrument with distinct ids are accepted. | C16 |
| **B17** | The fixture drifting from `PLAN_deskcraft.md` §6. Six legs, the stated directions (short 2Y, short 10Y, long 5Y breakeven, short EUR/USD, long 10Y option, short US-vs-Bund 10Y), and the two rate legs carrying the recorded futures→cash re-expression of DD12 rather than silently claiming to be the original. | C17 |
| **B18** | A tenor attached to something with no tenor, or missing from something that needs one. Every kind is classified exactly once; `FX_SPOT` and `EQUITY_VOL` refuse a tenor, every other kind requires a positive finite one. **Mutation** in both directions. | C18 |
| **B19** | A relative-value leg being indistinguishable from a doubled outright (DD16, DD17). `structure` is derived from the component count and matches it on every reference instrument; an `OUTRIGHT` is exactly one component at `+1` declaring `NONE`; the neutrality **iff** holds in both directions on every multi-component instrument. **Mutation, both ways:** a two-component "spread" written with two `+1`s and a stated neutrality is rejected, *and* a balanced `+1/-1` spread declaring `NONE` is rejected. | C19 |
| **B20** | A cross-currency leg with an unanswered hedging question (DD18). Every instrument whose components span more than one currency declares `fx_hedged` as a bool; every single-currency instrument declares it `None`. **Mutation** in both directions — a cross-currency instrument omitting it, and a single-currency one asserting it. | C20 |
| **B21** | A kind with no asset class, found in the middle of an attribution (DD19). `ASSET_CLASS_OF` is total over `InstrumentKind`, single-valued, and its image is exactly the members of `AssetClass`. The reference book spans **at least four** asset classes, which is the claim the structure is sold on. | C21 |
| **B22** | The sign matrix drifting from the book, or carrying a magnitude claim the source never made (DD20). Every scenario names every leg of the reference book and no others; every cell is in `{+1, -1, 0}`; the four scenarios are the four the source states. | C22 |

### 3.2 Predictions

- **P1.** All thirteen new bars pass on the first run, and **C1 is the only pre-existing bar that
  goes red** — until `MODULES` is extended with `deskcraft.book` and `deskcraft.reference`,
  which is the friction D1 said D2 would inherit.
- **P2.** Widening the imperative scan (DD13) turns **no** existing file red. The only
  occurrence of a forbidden phrase under `src/` is in `__init__.py`'s docstring, and docstrings
  are excluded by construction.
- **P3.** The reference book is multi-currency, so `gross_notional` **raises** on it and only
  `gross_by_currency` answers. The raising path is exercised by the fixture, not by a contrived
  input.
- **P4.** Exactly **4 of the 6** reference legs are priceable from today's measured floors; C14
  finds two deferred — the option leg (no series at all) and the cross-market leg (a foreign
  curve, which is DEC-2's later package).
- **P5.** `hash()` succeeds on both books, so no mutable field survived `frozen=True`.
- **P7.** **Four** of the six reference legs are relative-value structures — derived `structure`
  is not `OUTRIGHT` — and the book spans **five** asset classes: rates, inflation, FX,
  volatility, and the cross-market spread's rates. *(If it spans four, the prediction misses
  and the reason is that the cross-market spread is rates like legs 1 and 2, which would itself
  be the first quantitative sign of what H4 predicts.)*
- **P8.** Exactly **two** instruments are cross-currency — the EUR/USD leg is single-currency
  by construction, since a spot rate is one series, so only leg 6 spans currencies and P8
  therefore predicts **one**. *(Recorded in this form deliberately: the first draft of this
  prediction said two, and writing it out corrected it before the run rather than after.)*
- **P6.** curvecast is unaffected: its sweep stays **25/25**, `EXEMPT_FIELDS` is still `{}`,
  and `git status` in both upstream repositories shows nothing from this package.

### 3.3 Result

**22 bars, all passing. One failed on the first run, and it was a finding rather than a
defect — the failure is the most interesting thing this package produced.** `pytest -q` →
**22 passed**, up from D1's 9. On the end-to-end demonstration **7 of the 22 fire**, against
5 of 9 at D1, and the two additions are the two new scanners.

#### Predictions, scored

| | outcome |
|---|---|
| **P1** all thirteen new bars pass first run; C1 the only pre-existing red | **MISSED** on the first clause — C22 failed, see below. **Hit** on the second: the census was verified to be `{deskcraft, deskcraft.book, deskcraft.reference}` against D1's `{deskcraft}`, so C1 would have been red had the census not been extended. Stated plainly, that red was *never observed* — `MODULES` was extended in the same pass that added the modules, so the claim is verified by construction rather than by watching it fail |
| **P2** widening the imperative scan turns no existing file red | **hit** — the only forbidden phrase under `src/` is `__init__.py`'s docstring occurrence of *"you should"*, and C15 asserts that file both contains it and does not trip the scan |
| **P3** `gross_notional` raises on the reference book | **hit** — the book spans `{EUR, USD}`, and `gross_notional`, `net_notional` and `gross_by_asset_class` all raise on it. The raising path is the fixture's, not a contrived input's |
| **P4** exactly 4 of 6 legs priceable | **hit** — `us_10y_call` (no series at all) and `us_de_10y` (a foreign curve) defer; the remaining four are exactly `§10`'s NO-BUILD floor |
| **P5** `hash()` succeeds on both books | **hit** — and the mutation half holds: a frozen dataclass carrying a `list` is mutated successfully and is correctly rejected by the same predicate |
| **P7** four legs are relative value; five asset classes | **MISSED, both halves.** **Two** legs are relative value, not four, and the book spans **four** asset classes, not five |
| **P8** exactly one instrument is cross-currency | **hit** — `us_de_10y` only; the EUR/USD leg is one series and therefore single-currency, which is what the prediction was rewritten to say before the run |
| **P6** curvecast unaffected | **hit, with one thing stated rather than glossed** — the sweep is **39/39, 0 failed, 1008s**, `meip:untouched` reports `unmodified`, `meip:pytest` 1410 passed, and `EXEMPT_FIELDS` is still `{}`. MEIP's tree is clean. curvecast's tree carries one **untracked** file, `docs/TODO_pit_hardening_and_power.md`, which predates this package and comes from the session that scoped D5's floor probe; nothing in D2 wrote it. Reported because "both trees clean" would have been the easier sentence and would have been false |

#### C22 failed, and what it found is the package's real output

The bar asserted that if any two legs carry **identical sign patterns across all four
scenarios**, the pair is `us_2y` / `us_10y` — two Treasury legs being one bet is the obvious
guess and it is what §5.2 leads you to expect. It is wrong twice over.

`us_2y` and `us_10y` are **not** identical: the source separates them on the supply-shock
column, giving the ten-year the win and the two-year none, which is exactly the
policy-versus-term-premium distinction the structure is built on. The source is internally
consistent there.

What *is* identical is **`us_2y` and `eurusd`**:

| leg | everything_goes_wrong | fed_signals_fewer_cuts | inflation_surprises_higher | supply_shock |
|---|---|---|---|---|
| `us_2y` | −1 | **+1** | 0 | 0 |
| `us_10y` | −1 | +1 | 0 | +1 |
| `us_breakeven_5y` | −1 | 0 | +1 | +1 |
| **`eurusd`** | −1 | **+1** | 0 | 0 |
| `us_10y_call` | **+1** | 0 | +1 | 0 |
| `us_de_10y` | −1 | 0 | 0 | +1 |

The source argues for leg 4 on the ground that *"FX is driven by different flows than
rates"*. Under its own four scenarios the short EUR/USD is **indistinguishable from the short
two-year**: both pay only on fewer cuts, both lose in the tail, both are flat elsewhere. The
diversification claim and the scenario table that is offered as its evidence do not agree, and
noticing that costs no covariance, no panel and no fit — it is visible in the argument as
stated.

**And then the null was computed, and it cut the finding down (DD21).** The first write-up
of this paragraph called the collision *"the first evidence for H4, arriving at D2 instead of
D10"*. That claim does not survive its own null and is withdrawn here rather than in review.

Four scenarios over three values is 81 possible patterns. Six legs drawn uniformly from 81
collide **17.3%** of the time by luck alone. Worse, the `everything_goes_wrong` column is `-1`
for five of the six legs, so conditional on it only three columns discriminate: 27 patterns,
five legs, **32.5%**. A one-in-three event is not evidence of anything, and reporting it as
evidence is the error this project exists to avoid committing in public.

Two things do survive, and they are different in kind:

1. **The logical point, which needs no null.** The source justifies leg 4 by saying *"FX is
   driven by different flows than rates"* — an explicit diversification claim about one named
   leg — and its own scenario table gives that leg no cell distinguishing it from leg 1. The
   argument and the evidence offered for it disagree. That is true at any significance,
   because it is a statement about the argument rather than about the world. It is also a
   **one-cell test named in advance by the source**, not a search over fifteen pairs: 6.0%
   uniform, 14.0% conditional. Still not significance, and it is reported as corroborating
   detail rather than as a result.

2. **The table is under-determined, which is the finding that carries weight.** Four scenarios
   cannot separate six legs even in principle; **42% of its cells are `0`**, meaning no claim;
   and the one column that moves almost everything moves five of six legs the same way. So the
   table cannot establish the diversification conclusion **and cannot refute it either**. What
   replaces it is D12's dated replay over thousands of days, which is the whole reason D12
   exists.

The bar now carries all of that arithmetic, so the claim ships at the strength the evidence
supports. The pair is pinned as measured and the missed guess is recorded in the assertion's
comment, per D70: the prediction is scored, not edited.

#### DD21. A pre-registered claim ships with its null, or it does not ship

Added as a consequence of the above and applied retroactively to C22. A finding of the form
*"two things turned out to be the same"* is worthless without the probability that they would
have looked the same by chance, and this package produced one and wrote it up without that
number before catching itself.

The rule: **every bar that reports a coincidence computes, in the same test, how often the
coincidence occurs under an explicit null.** Not a p-value ritual — the null has to be written
down and defensible, and here it is stated two ways because the uniform one is too generous
and the conditional one is the honest one.

This is the discipline that makes the difference between a paper that survives a desk read and
one that does not, and it cost nothing to apply: six lines of arithmetic, run before the claim
left the repo.

#### P7 missed, and the miss is the same finding from the other side

Four legs were predicted to be relative value. **Two** are — `us_breakeven_5y` and
`us_de_10y`. The reasoning that produced the four was that legs 1 and 2 "are a
policy-versus-term-premium decomposition and only mean anything as a pair", and that is true
of the *thesis* and false of the *instruments*: each is a single outright point on the zero
curve, and `structure` is derived from the components, so it reports what the leg is rather
than what it is for. Being derived is what made the miss visible; a declared structure would
have recorded the intention and hidden the fact.

Five asset classes were predicted and there are **four** — `RATES`, `INFLATION`, `FX`,
`VOLATILITY`. `CREDIT` is absent because the reference structure has no credit leg, which the
plan's §4 never claimed it did. The prediction was counting the cross-market spread as its own
class; it is `RATES`, alongside legs 1 and 2, and that is the first quantitative sign of what
H4 measures — three of six legs in one asset class.

#### The five decisions that came out of reading the source directly

`§0.6` records what the four screenshots say that `PLAN_deskcraft.md` §6's one-line summary
drops, and four of the five new decisions exist because of it: signed components (DD16) so a
difference is representable at all, declared neutrality (DD17) so a balanced spread names its
basis, forced FX-hedging (DD18) so the cross-market leg's bet count is not a default, and the
sign matrix (DD20) so the source's justification is scoreable. DD19's asset-class partition is
the reporting cut the user asked for and the one that showed `CREDIT` empty.

The neutrality law is an **iff** and both halves fire: a two-`+1` "spread" with a stated hedge
is rejected, and so is a balanced `+1/−1` spread that names no basis.

#### What was built

| | |
|---|---|
| `src/deskcraft/book.py` | `Direction`, `Notional`, `Component`, `Instrument`, `ReExpression`, `Leg`, `Book`, plus `AssetClass`, `Structure`, `Neutrality` and the three kind partitions |
| `src/deskcraft/reference.py` | The six-leg structure, `DEFERRED_LEGS`, `NOTIONAL_PROVENANCE`, `SCENARIO_SIGNS`, and `US_CASH_BOOK` derived from the six rather than written twice |
| `tests/test_book_types.py` | C10–C14, C16–C22 |
| `tests/test_deskcraft_boundary.py` | `rendered_strings` widened to every non-docstring string constant; C15 added; `MODULES` extended |

#### What D3 inherits

- **The census is three modules now**, and D3's panel types make it four. Same friction, working as intended.
- **`SCENARIO_SIGNS` is a debt with a due date.** It is scored by D12 and by nothing before it. If D12 never lands, the matrix is an unfalsified claim sitting in the repo, which is the thing this project exists not to produce.
- **`fx_hedged=True` on `us_de_10y` is a decision, not a measurement**, and it is the reading least flattering to the structure — an unhedged spread would add a currency bet that H4 would then count. D12 should run it both ways.
- **The four-leg priceable book is exactly at §10's NO-BUILD floor.** D5's front-end probe is what gives it headroom, and until then a single instrument losing its grade stops the project.
