# Owner admission — the credit tier, admitted to committed fixtures

**Taken by the owner 2026-09-23. Recorded the same day. Three series, by name.**

This file is the written record `sources.ADMITTED` refers to and `C125` requires to exist. It is
not a licence reading and it does not claim one. It records a decision, who took it, when, on what
reasoning, and what it costs.

---

## 1. The decision

> **`T10YIE`, `BAA10Y` and `AAA10Y` may be carried by a committed fixture in this repository.**
> Each is admitted individually and by name. A fourth series is a fourth decision.

## 2. The reasoning the owner gave

The owner's challenge, verbatim, on 2026-09-23:

> *"I am not planning to sell this to anyone and this is just for my personal use so why is there
> a licensing problem this is like a personal project so licensing issues should not be a concern
> so why is it blocked for Deskcraft"*

**The challenge was correct about DD35's premise, and DD35 says so itself.** Its ground is that
*"a fixture committed to a repository that is then sent anywhere is redistribution"*, and it closes:

> *"This is an engineering rule, conservative on purpose. It is not a reading of anyone's contract
> and no row claims to be."*

The premise is a property of a goal, not of the law: it holds while the repository is going to be
sent to an institution, and not otherwise. The owner decided the repository is not being sent, so
the premise does not hold, so the rule it supports does not bind these three rows.

**The decision was taken after the alternatives were measured, not instead of measuring them.** The
owner was shown, before deciding: that deskcraft has no egress and the fetch lives in curvecast;
that curvecast's own regime is stricter and separately motivated by third-party permissions that
were never granted; that git history does not undo; that `MOVE` is not free at any route and is
blocked by *"free data only, no purchases"* rather than by any licence; and that the Cboe complex
is blocked by a restriction on the computation which this reasoning does not reach. The narrower
admission was chosen over deleting DD35 outright **on that basis**.

## 3. The three, and why each separately

| Series | Licence | What the words actually forbid | Why admitted |
|---|---|---|---|
| `T10YIE` | `CITATION_REQUIRED` | FRED's own tag; copying with attribution. No third-party notice behind it | The weakest claim of the three, over arithmetic on two public-domain series. It already had a committable construction (`DGS10 − DFII10`), so admitting it costs least and tests whether the rest were worth it |
| `BAA10Y` | `REDISTRIBUTION_PROHIBITED` | Moody's: copying, reproduction, redistribution without prior written consent. **Silent on private computation** | The whole of that prohibition governs an act this repository has stopped performing. This is the daily credit leg that `AMENDMENT_A5` measured `CREDIT_VS_RATES` at **0 of 1** tradeable series without |
| `AAA10Y` | `REDISTRIBUTION_PROHIBITED` | The same notice | The investment-grade pair to `BAA10Y`, on the same reading. Admitting one without the other would give a spread with no benchmark |

## 4. What is refused and stays refused

`VIXCLS` and the Cboe volatility complex are **not** admitted, and the code will not let them be:
`Source.__post_init__` raises if an admitted series is graded `Derivation.PROHIBITED`, and `C126`
mutation-tests that refusal.

Cboe's terms, read at DD121 from the originator rather than the distributor:

> *"You may not **otherwise** ... **create a derivative work (for example, a financial product,
> service or index) from, use to verify or correct other data or information**, publish ...
> distribute."*

**That restricts the computation, not the sending.** The owner's reasoning in §2 is that a rule
about sending does not bind a repository that is not sent. It is a good argument and it has nothing
to say here, because the act in question is not sending. This is recorded as a *limit* on the
decision rather than as a separate refusal, so that a later reader does not mistake the limit for
an oversight.

Three of D19's eight vol inputs also remain not-found-free at any route — an availability fact,
untouched by any decision in this file.

## 5. What it costs, stated by the person who chose it

1. **The repository is no longer sendable as it stands.** `NOT_SENDABLE.md` is at the root and
   `C127` keeps it there.
2. **It is irreversible in the direction that matters.** Before today, one commit had ever touched
   `tests/fixtures/` and it carried **zero** restricted columns — the history was clean. Once an
   admitted series is committed, every clone and archive from that commit carries it, and only a
   history rewrite removes it.
3. **The credential goal is narrowed, not dead.** Results and method still travel; the panel does
   not. That is the middle path DD136 built and it remains available for everything here.

## 6. What this does not authorise

- It does not admit a fourth series. Each admission is its own decision with its own row.
- It does not commission the fixture rebuild. The columns are not in any committed file yet; a
  package that needs them asks curvecast's extractor to stop stripping them, which is a change in
  a different repository with its own gate.
- It does not change `Source.sendable_free`, which still answers DD35's original question for every
  row and is how a future strip-and-send would know what to remove.
