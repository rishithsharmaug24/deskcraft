# Amendment A5 — what free data actually reaches, and the words it does not fix

*Raised and closed 2026-09-17, against `docs/BUILD_ORDER_D3_D16.md` §0 item 6 and §3.3,
`AMENDMENT_A3` §9, `CARRIED_ITEMS.md` X11, and `src/deskcraft/sources.py`'s `DE_ZERO_10Y` row.*

*The owner paused the D8 → D9 → D12 list to ask whether the vocabulary is too small, then asked the
harder version of the question: **for every direction this repository has declined, is the refusal a
licence, a price, or a gap nobody searched?** This document answers it source by source.*

*Adds no package. Fetches nothing. Changes no code. Opens no carried item. The budget stands at 21.*

---

## 0. Measured before decided

| # | Measured | Value |
|---|---|---|
| 1 | Sources read for **their own licence words**, not a summary of them | **22** |
| 2 | — dedicating to the public domain, committable under DD35 today | **5** |
| 3 | — granting redistribution on attribution, refused by DD35 | **6** |
| 4 | — stricter than attribution (non-commercial, pre-approval, or no redistribution) | **5** |
| 5 | — with no free source at any licence | **6** |
| 6 | Components for 99.99% of daily change variance, 8 GSW zeros / 30 GSW zeros | **6 / 6** |
| 7 | Daily-change variance **not** explained by the eight zeros — DGS3MO / DFII5 / DEXUSEU | **0.686 / 0.570 / 0.971** *(**ANNOTATED 2026-09-17 — `AMENDMENT_A7` §6.** The first two reproduce exactly on **level** changes; the third only on **log** changes, where level changes give 0.9731. The row states one statistic computed two ways. Nothing turns on it — both readings clear every hurdle — so it is a correction and not an item.)* |
| 8 | — the same statistic on two series that *are* the same bonds (DGS2 / DGS10), the noise floor | **0.074 / 0.039** |
| 9 | `CREDIT_VS_RATES` grammar terms with a tradeable series behind them | **0 of 1** |
| 10 | `CROSS_MARKET` series reachable; cosine of the book `select` returns | **1 of 2**; **0.707** *(restated 2026-09-25 by D9, X19: a lone US ten-year leg against a contrast whose German half no candidate reaches; a number about `LEVEL`'s overlap. `select` now refuses the view, DD152)* |
| 11 | Leakage into `LEVEL` of a `SLOPE UP` book, at 1bp / 10bp | **+0.416 / +0.241** |
| 12 | Gram overlap `LEVEL·REAL_VS_NOMINAL`, baked into the contrast's definition | **+0.4434** |
| 13 | Structures at 11 / 20 / 30 / 49 candidate series | **231 / 1,350 / 4,525 / 19,649** |
| 14 | Free daily JGB history at Japan MoF, first row | **1974-09-24** |
| 15 | Free daily euro-area curve at the ECB, first row | **2004-09-06** |
| 16 | Last free H.15 USD swap row | **2016-10-31** |
| 17 | Last EIA NYMEX futures row, against an OOS window ending 2025-12-31 | **2024-04-05** |
| 18 | Next free ids | **C116 / DD113 / X19** |

**Row 1 is a list of what was looked for, not a census.** There is no register of free rate data to
sweep, so recall here is unmeasured in exactly the way
`RIDER_the_impossibility_claims_X16_does_not_cover.md` §0 row 10 measured the corpus sweep's recall
and found it at one half. Nothing below says the search was complete. What each DECLINE below
carries is the search that supports it, which is X16's discharge and the only thing this document
can honestly offer.

**Rows 6 and 8 are why "more tenors" was never the answer.** The GSW curve is a six-parameter
Svensson fit, so eight zeros and thirty zeros are the same six dimensions; and two series drawn from
the same bonds leave 4–7% unexplained, which is the floor everything in row 7 must clear to count as
a direction rather than as noise.

---

## 1. The decision, in one line

> **Three additions are free, public domain and committable today — bills, the TIPS real curve, and
> H.10 spot FX. Every other direction this repository wants is owned by someone, and the question is
> no longer where to look but whether DD35 admits an explicit grant. Credit at daily frequency is
> the one direction no decision reaches.**

---

## 2. The disposition table

Four verdicts, fixed here as **DD113**:

- **ADD** — free, public domain, committable under DD35 as it stands.
- **GRANTED** — free and explicitly redistributable, on attribution. Refused by DD35 today;
  reachable by an owner decision, not by more searching.
- **CONSTRUCT** — not published, but derivable from what is already committable. Costs a package,
  and the construction's own error is stated before it is built.
- **DECLINE** — no free source, or a licence stricter than attribution. **Each carries the search.**

| Direction | Source read | Verdict | The words, or the search |
|---|---|---|---|
| **Bills, 4wk–1y** | H.15 secondary-market bill rows | **ADD** | Board disclaimer; FRED tag public domain. **0.686 / 0.458** new direction at 3m / 6m |
| **TIPS real curve** | Board GSW TIPS file `feds200805` | **ADD** | Same Board publisher as the nominal file already committed. Real and breakeven zeros 2–20y, forwards, 5y5y, daily from 1999. **0.570 / 0.342 / 0.292** at 5 / 10 / 30y. Never published below 2y; a 1999–2002 liquidity premium is in the levels |
| **Spot FX** | H.10, 23 pairs + three dollar indexes | **ADD** | Public domain at the tag and at the Board. **0.971** — the largest new direction measured anywhere |
| **Energy futures** | EIA NYMEX WTI contracts 1–4 | **ADD, and broken** | ~~Public domain~~ *(struck 2026-09-26, DD176: CME Group's prices, republished by EIA with permission)*, individually dated, from 1983 — **and the series now stops 2024-04-05**, inside the OOS window. §7.2 |
| **US–yen leg** | Japan MoF JGB daily | **GRANTED** | Public Data License 1.0, which Digital Agency states is compatible with CC BY 4.0: commercial use permitted, source cited, **modification permitted** if the edit is declared. Daily 1Y–40Y from **1974-09-24** |
| **US–euro leg** | ECB / Bundesbank, under the ESCB re-use policy | **GRANTED, with a second lock** | *"All publicly available ESCB statistics may be reused free of charge on the condition that the source is quoted and that the statistics (including metadata) **are not modified**."* §3 |
| **UK leg, incl. the only free OIS curve found** | Bank of England yield curves | **GRANTED** | UK Open Government Licence v3.0 |
| **Canada** | Bank of Canada zero curves | **GRANTED** | Attribution, and changes must be stated |
| **Impact-cost ADV** | NY Fed FR 2004B | **GRANTED, and it changes X11** | *"you must include any copyright notice… If you distribute the Content, you must make the Content available with the same permissions, conditions, and restrictions set forth in these Terms."* §7.3 |
| **Policy rates, 40+ banks to 1945** | BIS CBPOL | **DECLINE** | *"users may download, display, print out, photocopy or redistribute any BIS Material **for non-commercial purposes**"*. Narrower than attribution, so no widening of DD35 reaches it |
| **Japan, at the central bank** | Bank of Japan | **DECLINE** | *"the source, the Bank of Japan, should be explicitly credited"*, and commercial reproduction needs prior permission. Use MoF, which is the same curve on better terms |
| **German 10y via FRED** | `IRLTLT01DEM156N` | **DECLINE** | OECD-sourced, FRED-tagged **copyrighted**, and **monthly**. Closes the "just take it off FRED" route |
| **Daily credit — Moody's** | FRED `DBAA` / `DAAA` | **DECLINE** | *"MOODY'S INFORMATION MAY NOT BE COPIED OR OTHERWISE REPRODUCED, REPACKAGED, FURTHER TRANSMITTED, TRANSFERRED, DISSEMINATED, REDISTRIBUTED OR RESOLD… WITHOUT MOODY'S PRIOR WRITTEN CONSENT"* |
| **Daily credit — ICE BofA OAS** | FRED `BAMLC0A0CM` | **DECLINE** | *"provided for your internal use only and you are not authorized or permitted to publish, distribute or otherwise furnish [data] to any third-party"* |
| **USD swaps** | H.15, then four vendor routes | **DECLINE** | H.15 carried ICE swap rates to **2016-10-31** and nothing free replaced them. Eris, BlueGamma, Pensford, Tradition are all vendor or trial |
| **Implied rate vol** | MOVE (ICE), CVOL (CME) | **DECLINE** | Both licensed. The free copies on aggregator sites are unlicensed redistribution, which is not a source. §5.2 |
| **Treasury futures** | searched, no free dated history | **DECLINE** | D2's cash re-expression already covers the exposure |
| **FX forward points** | BoE FX pages; forward-margin archive | **DECLINE, reason upgraded** | BoE publishes FX under LSEG terms **excluded from the OGL**; only a 2006–2011 forward-margins archive exists. And the constructible version is wrong — §5.1 |
| **Inflation swaps** | searched | **DECLINE** | Commercial only (Tradition, S&P, LSEG). No central bank publishes a daily curve |
| **CDS** | searched | **DECLINE** | ISDA and BIS publish **aggregate, semi-annual**. The daily aggregator sites are scrapes, not licensed sources |

**DD113 fixes the taxonomy and nothing else.** A verdict in this table is a reading of published
words; it is not legal advice, and §8 says what that leaves open.

---

## 3. The euro leg is the hard one and the yen leg is the easy one — the reverse of what was assumed

`sources.py` carries a row for `DE_ZERO_10Y` whose licence is `UNMEASURED` and whose evidence reads
*"None. Its only leg is deferred under DEC-2"*, with a `no_fallback_reason` promising that
*"DEC-2's later package measures the source and its licence before any row of it is read."* **That
package does not exist** (§7.1). This section is the measurement it was going to make.

**The German curve is redistributable and not modifiable.** The Bundesbank publishes the daily
German zero curve from 1997-08-01 and, as an ESCB member, publishes it under the ESCB re-use policy:
free of charge, commercial use included, **provided the source is quoted and the statistics
including metadata are not modified.** The attribution half is the familiar DD35 question. The
second half is new and it is the binding one, because **a deskcraft panel is a modification** —
resampled to a session grid, differenced to basis points, and fitted into loadings. Whether a
principal-component analysis of differences is a *modification of the statistics* or a *result
derived from them* is a question this document cannot settle and does not pretend to; what it can
say is that the risk sits on the **committed bytes**, not on the published numbers, and that
curvecast's WP-L1 pattern was built for exactly that shape: keep the fixture out of git, pin it by
CRLF-folded sha256, and let `git archive HEAD` carry only what may travel.

**The Japanese curve is redistributable and modifiable.** Japan MoF publishes JGB rates under Public
Data License 1.0, which Digital Agency states is compatible with CC BY 4.0 — commercial use
permitted, source cited, and **editing permitted provided the edit is declared**. The file is daily,
1Y through 40Y, Gregorian dates, first row **1974-09-24**.

**So the ordering reverses**, and this is **DD115**:

| | Euro | Yen |
|---|---|---|
| History covering DEV (1988→2014) | **2004-09-06 onward** — 62% of the window | **1974-09-24 onward** — all of it |
| Redistribution | Granted | Granted |
| Derivative works | **Not granted** | Granted, with the edit declared |
| Central-bank alternative | — | BoJ, and it is **worse** (§2) |

> **The first cross-market leg is the yen leg.** It is not a preference: it is the only one of the
> two whose licence permits the thing this repository does to data, and the only one whose history
> covers the window the hypotheses are scored on.

This does not close `DE_ZERO_10Y`. It supplies the row's missing evidence and its licence grade —
`CITATION_REQUIRED`, with a no-modification condition the `Licence` enum has no term for — and
**leaves the edit to the package that reads it**, because changing a graded row is a package's work
and this document builds nothing. **DD114** is that grade, recorded and not yet applied.

---

## 4. Credit cannot be fixed by adding data, and that is now measured rather than assumed

The owner's question was the right one to ask of every refusal: *why refuse instead of adding the
data?* For `CREDIT_VS_RATES` the answer is that **there is no daily credit series anyone may
redistribute**, and the two obvious candidates say so in their own words (§2). Both are **stricter
than attribution** — Moody's forbids reproduction outright, ICE restricts to internal use — so
unlike the euro and yen legs, **no widening of DD35 reaches them.** An owner decision about
attribution licences changes the cross-market words; it does not change this one.

What is left that is free and public domain is **monthly**: Treasury's HQM corporate spot curve from
1984, and the Board's excess-bond-premium file already carrying `GZ_SPREAD`. `sources.py`'s own
`no_fallback_reason` under `GZ_SPREAD` already said ICE BofA was *"the withdrawal this register was
built to record"*; this amendment confirms that reading at the source and adds Moody's beside it.

**DD116.** *A daily `CREDIT_VS_RATES` term is closed by licence, not by search. The monthly curve is
not the convenient shape for Paper 2 — it is the only lawful one.* The grammar term keeps its zero
tradeable series until a package either (a) moves it to monthly and says so where a reader will see
it, or (b) removes it. Leaving a six-term grammar in which one term silently reaches nothing is the
shape `views.fidelity` already refuses for an unreachable factor, and §6.2 is the same defect one
level over.

---

## 5. Three declines whose reason changes

### 5.1 FX forwards — the constructible version is wrong where it matters

The refusal was recorded as *"no free forward points exist, so FX-hedged legs would misstate
carry."* The first clause is confirmed: the only free run found is a Bank of England forward-margins
archive covering **2006–2011**, and BoE's live FX pages carry LSEG terms explicitly excluded from
the OGL.

But a forward is **constructible** under covered interest parity from H.10 spot (public domain) and
two money-market rates, and the US leg of that is H.15 (public domain). So the honest refusal is not
"no data". It is two-part, and **DD117** fixes it:

1. The foreign leg re-imports §3's licence question, because no free **public-domain** foreign
   deposit rate was found.
2. **The construction fails on measurement before it fails on licence.** Post-2008 cross-currency
   basis means a CIP-implied forward misprices the hedge by the basis — and the basis is widest in
   exactly the dated windows D12 replays. A constructed forward would be most wrong in 2008 and
   2020, which is where a scenario engine is read.

That is a decline this document is willing to defend, and it is a different sentence from the one
that was there.

### 5.2 Implied vol — two different questions were being answered as one

`AMENDMENT_A3` §9 found D19 naming ~~nine~~ **eight** vol inputs with **one** graded. That finding stands and is
not this one, and its count was corrected on 2026-09-17 — it printed eight names and called them nine,
having taken the count from `RESEARCH_client_solutions_layer.md` §7, which lists nine because it
includes `VXEEM`. This paragraph repeated the error unchecked. The distinction this document adds:
**D19's eight are equity and commodity vol** — VIX, VIX9D, VIX3M, VIX6M, SKEW, VVIX, OVX,
GVZ — and those are free. **Rates** implied vol is the
one that is not: MOVE is ICE's, CVOL is CME's, and both are licensed. A reader who takes A3 §9 as
saying "vol data is a grading problem" will be wrong about the only vol surface this repository's
own instruments would need.

**And this section makes a claim it did not measure.** *"Those are free"* is asserted here on the
strength of Cboe's publication practice, and **seven of the eight have never been through a licence
read** — this document's twenty-two-source sweep was rates, FX and credit and did not reach them.
So the half-decline D19 carries is stated without the record X16 asks for. Opened 2026-09-17 as
**X23**, owned by **D16**, and sequenced at `BUILD_ORDER_D3_D16.md` §7.3 step 3: a licence read per
input, no fetch and no package.

*(**Read the same day** — `RIDER_the_vol_surface_is_licensed_not_absent.md`, **DD121**, which closes X23.* **~~Those are free~~ — the word
was doing two jobs and this document is the one that says they are different.** *Free of charge, yes.
Free to derive from, no: Cboe's terms refuse derivative works without prior written consent and name *"a
financial product, service or index"* as the example, so the grade is **`REDISTRIBUTION_PROHIBITED`** and
**DD118 refuses it** — at FRED too, one step milder and still refused. And three of the eight are not
obtainable free at any route found. The blanket option decline is restored in full.)*

### 5.3 Swaps and Treasury futures — unchanged, now with the search behind them

Both declines stand as written. What they lacked was the record X16 asks for, and §2 supplies it:
H.15's swap rows end **2016-10-31**; four vendor routes were checked and all are paid or trial; no
free dated Treasury-futures history was found. D2's cash re-expression covers the futures exposure
and always did.

---

## 6. What needs no new data at all

### 6.1 PCA-weighted butterflies — a correction

**This was stated wrongly.** Earlier in this session PCA-weighted flies were listed as needing D8's
covariance. They do not. `factors.NominalSpectrum.loadings` already carries the DEV
principal-component loadings over the eight GSW zeros — restated at exact equality from curvecast
item 28 at D6, held by C60 — so **level- and slope-neutral fly weights are computable today**, from
objects this repository already holds.

What genuinely needs D8 is a **regression**-weighted fly, which needs a covariance estimate. And
what needs D9 is **declaring** the resulting neutrality, which is **X17** — a DV01-matched structure
cannot today say what it is neutral to. So the blocker on this direction is a carried item and a
generator that emits only unit coefficients `(+1)`, `(+1,−1)`, `(+1,−2,+1)`; it was never data.

### 6.2 The half-reachable factor, and the refusal that does not fire

`views.fidelity` raises `UnreachableFactor` for a factor no leg reaches (DD65). `generator.select`
has **no equivalent refusal for a half-reachable one** — so a `CROSS_MARKET` view returns a single
10-year US leg at cosine **0.707** and a `book()` that reports *"That is a statement about costs at
this cell and not a failure of the rule."* That sentence is true of an empty selection caused by
costs and false of one caused by missing data, and the caller cannot tell which they have.

This is code, it is small, and it belongs to whichever package next touches `generator.select`.
**Opened as X19**, owned by D9.

### 6.3 The impact term — a stated depth, not a graded file

X11's data half reads, in the register's own words, *"grade FR 2004B and H.15 and the cost model is
whole."* §2 measures FR 2004B's terms and they are **attribution with a share-alike clause** —
distributing the content obliges the distributor to pass the same conditions on. Under DD35 that is
not committable, so **grading it does not close the half**; it converts an ungraded input into a
graded uncommittable one. Meanwhile `costs.py` already accepts a caller-stated `MarketDepth` and
refuses only in its absence. **The route that works today is a stated depth with its basis named.**

---

## 7. Three defects with no owner

### 7.1 DEC-2 defers to a package that does not exist

Six code sites and one pre-commit defer the cross-market leg and its licence read to *"DEC-2's later
package"* — `costs.py:323`, `factors.py:107`, `reference.py:27` and `:247`, `sources.py:315` and
`:319`, and `PRECOMMIT_deskcraft_d3a_guards_and_registers.md:451`, which defers *"an `UNMEASURED`
licence on a deferred leg's series"* to it. **No row of `BUILD_ORDER_D3_D16.md` §4 commissions it.**
A deferral to a package that will never open is a decline with no decision behind it, and it is the
same shape `AMENDMENT_A4` §2 found when the OOS panel had a specification and no row. §3 measures
the licence that deferral was holding; what it cannot do is create the owner.

### 7.2 §0 item 6 rests on a series that stopped inside the OOS window

Build order §0 item 6 withdraws the blanket futures decline for energy, on the ground that *"the EIA
publishes NYMEX WTI contracts 1–4, daily settlement, free, public domain, from 1983 — individually
dated."* ~~The public-domain and individually-dated halves hold.~~ The individually-dated half holds *(the public-domain half struck 2026-09-26, DD176)*. **The coverage half does not: the EIA
page now states prices after 2024-04-05 are unavailable.** The OOS window is 2015-01-01 →
2025-12-31 (DD98), so the route that dissolved the splice objection now covers **nine of eleven**
OOS years and stops twenty months short. Paper 2's commodity arm is scoped against a series that no
longer reaches the window it would be scored on.

### 7.3 FR 2004B's share-alike clause reaches the archive, not just the file

Covered at §6.3 as a defect in X11's stated discharge. The second half is a distribution question
nobody has asked: NY Fed's terms require a redistributor to pass on *"the same permissions,
conditions, and restrictions"*. Since **distribution here is `git archive HEAD` and nothing else**,
committing FR 2004B bytes would attach those conditions to every archive this repository ever sends.
That is a decision about the distribution channel, not about a column.

---

## 8. What this could still get wrong

- **The ESCB no-modification clause is read, not adjudicated.** Whether a PCA on differenced data
  modifies *the statistics* is the question §3 turns on, and this document states it as a risk
  rather than resolving it. If the answer is "no", the euro leg is exactly as easy as the yen leg
  and §3's ordering is wrong for the right reason.
- **PDL 1.0's CC BY compatibility is asserted by its publisher**, on Digital Agency's own page. The
  licence text was not read clause by clause.
- **Row 1 has unmeasured recall.** Twenty-two sources is what was looked for, not what exists.
- **Four of the DECLINE rows rest on searches re-run after a session limit.** The first attempts
  returned nothing at all, and the verdicts rest entirely on the later run.
- **Every decision here is prose.** DD113–DD117 carry no bar. A decision without a bar is a sentence
  in a document, which is the thing this repository keeps discovering about its own prose, and §9
  names what would hold each.

---

## 9. What the owner still decides

Nothing below is taken by this document.

*(**CLOSED 2026-09-22 — `RIDER_A5_the_six_remaining_decisions.md`.** All eight rows are now taken: row 1 by DD118 and row 3 by DD120/DD122, both by documents that had to decide in order to say anything, and the remaining six by the rider above as **DD123–DD128**. Five of those six decline to commission work, each on a measurement. **No row of this section is waiting on the owner.**)*

| | Decision | Turns on |
|---|---|---|
| 1 | ~~**Does DD35 admit an explicit grant?**~~ **TAKEN 2026-09-17 — DD118, §11.** Read yes, commit no | The **GRANTED** column of §2 is live; §11 says what it does and does not change |
| 2 | ~~**Wave 1: bills, TIPS reals, spot FX — all three, or fewer?**~~ **TAKEN 2026-09-22 — DD123, `RIDER_A5_the_six_remaining_decisions.md`.** None. The pool stays at eleven. Bills are refused twice over (C104, and DD122 part 3 at 49.6% and 51.2% of days unchanged), TIPS reals and spot FX at clause 1 for a slot that is filled and a slot that does not exist | §0 rows 7 and 13. Eleven series is 231 structures; twenty is 1,350 |
| 3 | ~~**A candidate-set rule, pre-registered, before any series is added**~~ **TAKEN 2026-09-17 — DD120, `AMENDMENT_A6`.** Admission is to a grammar slot, the direction is measured against the pool rather than against the eight zeros, and a verdict keeps the universe it was scored at | Row 13 is combinatorial, and H3 and H9 must stay scored on the vocabulary they were scored on. **And this document's own row 7 is not that statistic** — **X24** |
| 4 | ~~**The two broken words**~~ **TAKEN 2026-09-22 — DD124, `RIDER_A5_the_six_remaining_decisions.md`.** Neither is removed. `CREDIT_VS_RATES` moves to monthly, executed by D8 under X2's frequency policy; `CROSS_MARKET` keeps its word and the yen leg is not commissioned — after DD120 it is an ordinary admission. The binding half is **X19**, which is D9's | §4 and §6.2 |
| 5 | ~~**Is X17 pulled forward?**~~ **TAKEN 2026-09-22 — DD125, `RIDER_A5_the_six_remaining_decisions.md`.** No. The first caller is D9 and there is no earlier one; widening DD17 now is widening a guard for nobody, and it would deliver half a mechanism anyway — the coefficient axis also needs the generator to emit non-unit coefficients | D9 owns it today |
| 6 | ~~**Who owns DEC-2's cross-market work**, now that no row does~~ **TAKEN 2026-09-22 — DD126, `RIDER_A5_the_six_remaining_decisions.md`.** Nobody. The budget is frozen at twenty-one one-in-one-out and nothing has been removed to pay for it, so the deferral becomes a decline and D16 reports it with §3's measurement. **X20 stays OPEN** — six code sites still promise the package, and **C118** refuses the half-state | §7.1 |
| 7 | ~~**Paper 2's commodity arm**, against a series that stops 2024-04-05~~ **TAKEN 2026-09-22 — DD127, `RIDER_A5_the_six_remaining_decisions.md`.** Declined. Nine of eleven out-of-sample years, twenty months short. D17 writes it, carrying both §0 row 17's search and §0 row 1's bound that recall is unmeasured. **X21 stays open** until D17 lands | §7.2 |
| 8 | ~~**FR 2004B: state a depth, or take the share-alike into the archive**~~ **TAKEN 2026-09-22 — DD128, `RIDER_A5_the_six_remaining_decisions.md`.** State the depth. `costs.py` already accepts a caller-stated `MarketDepth`; committing the bytes would attach share-alike conditions to every `git archive HEAD` this repository ever sends, for one number. X11 stays open and its impact half now has a route | §6.3, §7.3 |

**The three ownerless defects are now owned.** They were going to be left here as proposals, on the
reasoning that opening an item reddens three bars and belongs to a package. That was the wrong call
and it is reversed: a defect named only in prose is the failure mode this register exists to
prevent, and `RIDER_the_register_counts_itself_in_prose.md` is standing evidence that prose beside a
guarded structure drifts. **X19** (the missing refusal) to **D9**, **X20** (DEC-2's unowned
deferral) to **D16**, **X21** (the EIA truncation) to **D17** — §1's tally moves from eight open to
eleven and the declaration census in `tests/test_carried_items.py` moves with it. Next free id is
**X22**.

**Two build-order claims were false rather than incomplete, and both are struck in place** rather than
only described here: §0 item 6's coverage half (§7.2) and §3.3's *"Public domain"* on FR 2004B (§6.3),
which also narrows **X11**. The declines at §2 and §5 need no structural change — what they lacked
was the search behind them, and that is what this document is.

---

## 10. Result

**CLOSED 2026-09-17.** Decisions **DD113–DD117**, no bars, no code, ~~no carried item opened~~, no
package added. Suite **123 passed**, unchanged, run after this document landed — because a document
that turns a bar red is a document that changed something it said it did not. ~~Next free ids are still
**C116 / DD118 / X19**.~~

*Corrected the same day and left struck rather than rewritten, because the order in which this went
wrong is the useful part.* **Five carried items were opened before the day ended.** **X19**, **X20**
and **X21** by §9, once the owner reversed the decision to leave the three ownerless defects as
proposals; **X22** by §11's DD118, which sorts a graded source three ways where the type expresses
one; and **X23** against **this document's own §5.2**, by `BUILD_ORDER_D3_D16.md` §7.2 — *"those are
free"* is a licence claim and no licence was read. The suite is still **123 passed**: no bar was added,
only the three register bars' data moved. §1 of the register now reads **thirteen open**, and next
free ids are **C116 / DD120 / X24**.

| | What was asked | What was found |
|---|---|---|
| **US–euro** | Why refuse instead of adding it? | Redistributable, **not modifiable**. The lock is the second clause, not DD35 |
| **US–yen** | Same | Redistributable **and** modifiable, from 1974. The easier leg, and it was assumed to be the harder one |
| **FX view words** | Same | Constructible under CIP, and the construction is most wrong in the windows D12 replays |
| **Monthly credit** | Same | Not a preference. Both daily alternatives forbid redistribution in their own words, and no licence decision reaches them |
| **PCA flies** | Same | **They need no data and no D8.** D6's loadings already hold them; X17 gates the claim |
| **Swaps, implied rate vol, futures** | Same | No free source. Now with the search recorded, which is what X16 asks and what these declines lacked |

---

## 11. DD118 — the licence rule, decided

*Taken by the owner 2026-09-17, against §9 row 1.*

> **A source whose licence grants use or redistribution on attribution — `CITATION_REQUIRED` or
> better — may be graded, read and derived from. Only `PUBLIC_DOMAIN` bytes may be committed.
> Everything between the two lives as a fixture pinned by CRLF-folded sha256 and kept out of git,
> which is curvecast's WP-L1 pattern, so `git archive HEAD` continues to carry only bytes that
> travel without conditions.**

**What does not change, and it is most of the code.** `Source.committable` still returns
`self.licence is Licence.PUBLIC_DOMAIN`, unchanged and for its original reason: that predicate was
always about the archive and never about the reading. DD35's guarantee is untouched — every byte
this repository can send anyone remains unconditioned, which was the property the rule existed to
protect and the one a craft artifact is judged on.

**What changes is what a package may do with a graded row it may not commit.**

| | This morning | Under DD118 |
|---|---|---|
| **Japan MoF JGB**, daily 1Y–40Y from 1974-09-24 | refused at the grade | read, derived, pinned. `CROSS_MARKET` becomes a true word, and X19's refusal becomes a guard rather than a wall |
| **NY Fed FR 2004B** | refused at the grade | read. X11's impact term can have a measured ADV, and the share-alike clause never fires, because nothing is distributed |
| **ECB / Bundesbank** | refused at the grade | readable, **and still the harder leg** — §3's no-modification condition binds on *republishing modified statistics*, which DD118 does not do, but the conservative reading is that derived results may travel and the statistics may not |
| **Moody's, ICE, BIS, BoJ** | refused | **still refused.** Each is stricter than attribution in its own words, and no widening reaches them (§4) |

**And the rule creates a defect on arrival.** It sorts every graded source into **three**
dispositions — committable, readable-and-pinned, refused — and `sources.py` can express **one**.
There is no `readable` predicate, and `Licence`'s five terms include none that says *modification
not permitted*, which is the condition the German curve actually carries. **X22**, owned by D8,
because D8 is the next package that grades a source and therefore the first that must act on the
distinction.

**What this does not settle.** Which foreign leg gets built, and in which package, is a budget
question and remains open at §9 row 6 — DD118 removes the licence blocker and does not commission
the work. The recommendation that follows from §3 is unchanged: **yen before euro**, on history and
on derivation rights, and a decision to build neither is still available.
