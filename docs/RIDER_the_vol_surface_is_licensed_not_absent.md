# Rider — the vol surface is licensed, not absent

*2026-09-17. Closes **X23**, opens **X25**, carries **DD121**. No package, no bar, no code, no row
of §4 moved, no series added. Step 3 of **DD119**.*

`BUILD_ORDER_D3_D16.md` §7.3 step 3 is *"grade D19's seven ungraded vol inputs"*, and its cost
estimate was **a licence read per input, no fetch and no budget**. That is what was done, on
2026-09-17, and it took the answer somewhere the item did not anticipate: **the decline D19 half-
reversed is restored in full, and the reason it is restored is better than the reason it was
originally taken.**

---

## 0. Measured before decided

| # | Measured | Value |
|---|---|---|
| 1 | Vol inputs D19's §4.1 row names | **8** |
| 2 | — downloadable at the page `RESEARCH_client_solutions_layer.md` §7 cites as verifying them free | **5** |
| 3 | — not on that page at all: `VIX3M`, `VIX6M`, `SKEW` | **3** |
| 4 | Licence words on that page itself | **none** — an accuracy disclaimer and two footer links |
| 5 | Grade of the five, read from Cboe's own terms | **`REDISTRIBUTION_PROHIBITED`** |
| 6 | Grade `sources.py` carries for `VIXCLS`, read from FRED's note | **`PRE_APPROVAL_REQUIRED`** |
| 7 | Of `RESEARCH` §7's four free parameters — level, term structure, skew, vol-of-vol — how many survive | **0 of 4** |
| 8 | Routes that refuse: Cboe direct **and** FRED | **2 of 2** |

---

## 1. What the pages say

**The page the plan relied on states no terms.** `cboe.com/tradable-products/vix/vix-historical-data`
carries an accuracy disclaimer — *"Cboe Volatility Index data is compiled for the convenience of
site visitors and is furnished without responsibility for accuracy"* — and nothing about use. It
links to **Use of Content** and **Terms & Conditions**, which is where the words are. `sources.py`'s
`VIXCLS` fallback already recorded half of this: *"its page states no redistribution terms, so it
mends the distributor and not the licence."* **That reading is now measured and its premise is
wrong.** The page states none *inline*; it links to terms that state a great many.

**Use of Content**, read 2026-09-17:

> *"In order to use any Cboe logo, data, photo/image or other content contained in Cboe websites
> (collectively "Cboe Content"), you must receive approval in advance from Cboe."*
>
> *"If Cboe approves your request, such approval will be contingent upon your execution of a
> license agreement. You are not approved to use Cboe Content until a license agreement has been
> signed by both you and Cboe."*

**Terms & Conditions**, read 2026-09-17. The grant:

> *"view, print and download one copy of the Materials for your personal non-commercial use in
> connection with products and services offered by Cboe, provided that you maintain all copyright,
> trademark and other notices contained on the Materials."*

And the refusal, which names this repository's intended use by example:

> *"You may not otherwise copy, reproduce, alter, store either in hard copy or in an electronic
> retrieval system, license, transmit, display, broadcast, **create a derivative work (for example,
> a financial product, service or index) from, use to verify or correct other data or
> information**, publish, rent, sublicense, distribute, or otherwise use in whole or in part in any
> other manner the Materials without Cboe's prior written consent."*

`RESEARCH_client_solutions_layer.md` §7 proposed *"a stated parametric surface"* fitted to these
four parameters. A stated parametric surface fitted to Cboe index values is a derivative work
**of the kind the clause gives as its own example**. This is not an edge reading.

---

## 2. Three of the eight are not free in the first place

The count matters as much as the licence, and it is the half nobody checked. Of D19's eight, the
cited page offers **five** — `VIX`, `VVIX`, `VIX9D`, `OVX`, `GVZ` — alongside `VXAPL`, `VXAZN`,
`VXEEM` and the retired `VXO`. **`VIX3M`, `VIX6M` and `SKEW` are not on it.** They have index
dashboards; their history is directed to **Cboe DataShop**, which is a paid product, and to the
Global Indices Feed, which is a licensed feed.

So the plan's own rule — free data only, no purchases — refuses three of the eight **before the
licence question is reached**. And those three are not a fringe: `VIX3M` and `VIX6M` are the entire
**term structure**, and `SKEW` is the entire **skew**. `RESEARCH` §7 named four free parameters as
enough for a stated surface — level, term structure, skew, vol-of-vol. Two of the four are not
obtainable, and the two that are (`VIX`, `VVIX`) are licensed against derivation. **Nought of four.**

---

## 3. DD121 — the option decline is restored, and its reason changes

> **DD121.** D19's vol inputs grade `REDISTRIBUTION_PROHIBITED` at the originator and no better
> than `PRE_APPROVAL_REQUIRED` at FRED. Both are stricter than `CITATION_REQUIRED`, so **DD118
> refuses them at every route**: not committable, not readable-and-pinned, not derived from. The
> blanket decline on option pricing stands in full. **The half-reversal at §4.1's D19 row is
> withdrawn as a matter of licence, and the row is annotated rather than moved — D19 stays
> annexed and §4.1's displacement rule is untouched.**

**Both routes refuse, which is what makes this robust.** Cboe direct lands at
`REDISTRIBUTION_PROHIBITED` on the words above. FRED lands at `PRE_APPROVAL_REQUIRED` — the grade
`sources.py` already carries for `VIXCLS`, because FRED's note asserts Cboe's copyright and says
FRED reprints *with permission*, which grants nothing downstream. The two routes differ by one
step of the enum and agree on the disposition, so the conclusion does not depend on which reading
of Cboe's terms a reader prefers.

**The decline is better than it was.** It used to say *there is no free implied-vol surface*, which
was measured for Treasuries on `VXTYN` and then over-generalised, and `RESEARCH` §7 was right to
object to it. What it says now is exact: **the equity and commodity surface is visible at no charge
and licensed against exactly the use this engine would make of it, and half its parameters are
behind a paid shop.** That is a decline with its search behind it, which is X16's demand.

**And it is the conflation X23 was opened to catch, found in the document that opened it.**
`AMENDMENT_A5` §5.2 says *"those are free"* — true of price and false of licence, in a repository
whose whole free-data argument is that those are different questions. `RESEARCH` §7's *"Verified
free today"* is the same word doing the same two jobs.

---

## 4. X25 — a landed graded row is wrong

`sources.py`'s `VIXCLS` row grades the **distributor's note** rather than the **originator's terms**
and lands one step milder than the words support: `notice=PRE_APPROVAL_REQUIRED`, where Cboe's own
terms forbid reproduction and derivation without prior written consent. Its `fallback` then points
at Cboe's page on the premise that the page *"states no redistribution terms"* — measured above and
false as a description of the route, because the page's terms are one link away and they bind.

That is the same defect `AMENDMENT_A5` exists to correct — **read the words, not the tag** — one
level up, in the file A5's method was applied to. **X25**, owned by **D8**: the next package that
grades a source, and already the owner of **X22**, the missing predicate that would let a row say
*refused* at all. Changing a graded row is a code change and belongs to a package, so nothing here
edits `sources.py`.

---

## 5. What this could still get wrong

- **A terms-of-use page is a contract, and an index value is a fact.** US copyright does not
  protect facts, and a thin compilation claim over a published index level is arguable. The grade
  here is read **from the words**, which is what `Licence` documents itself as doing, and the words
  bind by contract whether or not the underlying numbers are copyrightable. A reader who thinks
  the clause unenforceable gets a different answer and does not get it from this repository.
- **"Materials" is defined by Cboe's site, not by this document.** The read above treats the
  downloadable historical CSVs as Materials because they are downloaded from the site and because
  Use of Content names *data* explicitly. That is the conservative reading and it is stated as one.
- **The three absences are absences from one page.** `VIX3M`, `VIX6M` and `SKEW` may exist free at
  some route nobody here has found. Recall is unmeasured in exactly the way `AMENDMENT_A5` §0
  row 1 says it is, and this rider inherits that bound rather than escaping it.
- **Nothing here was fetched as data.** Four pages were read for their words on 2026-09-17. No
  series was downloaded, nothing entered the tree, and no `.csv` exists as a result of this rider.

---

## 6. Result

**X23 CLOSED**, by measurement, with the outcome its own body registered as one of the two that
would close it: *"one of them does not [grade], and the decline D16 reports finally carries the
search X16 asks for."* **X25 opened**, owned by **D8**. **DD121** taken. §1's tally moves to
**eight closed, three standing, fourteen open with an owner**.

No bar was added — this rider changes no structure, and the bar that would matter is the predicate
**X22** already names. Suite **124 passed**, unchanged. Next free ids **C117 / DD122 / X26**.

D16 still writes the decline. That is step 6 of DD119 and it is unchanged by this: what changed is
that the decline now has a number and four quotations behind it instead of an assumption.
