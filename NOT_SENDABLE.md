# This repository is not sendable as it stands

**Written 2026-09-23 by DD137. Required to exist by bar C127 for as long as a committed file
carries an admitted series. Deleting it does not make the repository sendable; it makes C127 red.**

---

## What changed

Until 2026-09-23 every byte in this repository travelled without conditions. DD35 guaranteed it:
*only a public-domain series is committable*, enforced by `panel.refuse_uncommittable` at load
time and by bar `C43` over the committed bytes. The property that guarantee protected was that
this repository could be handed to anyone, at any time, with no question to answer.

**The owner lifted that guarantee for three named series** — `T10YIE`, `BAA10Y`, `AAA10Y` — on
the reasoning that DD35's stated premise was *"a fixture committed to a repository that is then
sent anywhere is redistribution"*, and that this repository is not being sent. DD35's own closing
sentence invited the reading: *"this is an engineering rule, conservative on purpose. It is not a
reading of anyone's contract and no row claims to be."*

The reasoning is sound and the consequence is real. **Both are recorded here rather than in
anyone's memory**, because the failure mode is not the decision — it is the decision being
forgotten by whoever ships the repository eighteen months from now.

## What this means in practice

| | Before | Now |
|---|---|---|
| Hand the repository to a person or an institution | safe, always | **not safe** without stripping |
| Push to a public remote | safe | **not safe** |
| `git archive HEAD` as a distributable copy | the whole point | **carries restricted bytes** |
| Run it, read it, compute on it, publish results from it | safe | **unchanged, still safe** |

**Git history is the part that does not undo.** Once an admitted series is committed, every clone,
bundle and archive of this repository from that commit onward carries it. Removing the file later
does not remove it from history. The only remedy is a history rewrite, which curvecast faced and
deliberately declined (D442), and which is an owner decision requiring explicit confirmation.

## Where the admitted bytes are

*Added 2026-09-25 (DD140).* **One file:** `tests/fixtures/panel_daily_admitted_dev_20260925.csv`,
carrying `BAA10Y` and `AAA10Y` and nothing else. The two older panels are public domain and
byte-identical to their 2026-09-14 extraction. `T10YIE` is admitted and is **not** carried, for
D3b's DD45 reason: a derived column beside its two inputs invites a reader to treat it as a
third source. Moody's words were read the same day and forbid copying and repackaging, not
computing (`Derivation.RESULTS_ONLY`), so the admission stands. **Every commit from the one
that added this file onward carries Moody's bytes.**

*Added 2026-09-28 (DD102).* **A second file:** `tests/fixtures/panel_daily_admitted_oos_20260928.csv`,
the same two series over the out-of-sample record, 2015-01-01 → 2025-12-31, landed by the
read's trigger commit `2acbd39`. A strip for sending is now these two files, and the deposit of
2026-09-28 was built from `e8679ad`, before the second existed.

## What is still refused, and why it is not a loose end

`VIXCLS` and the Cboe volatility complex are **not** admitted and cannot be, even by editing
`sources.ADMITTED` — `Source.__post_init__` refuses the combination and `C126` holds it. Cboe's
terms forbid *"create a derivative work ... from, use to verify or correct other data"*. That is a
restriction on the computation, not on the sending, and DD137's reasoning does not reach it. The
owner's decision was about a rule they wrote themselves; this is not one.

## How to make the repository sendable again

Two routes, both owner decisions:

1. **Strip and send.** Produce a copy with the admitted columns removed and `sources.ADMITTED`
   emptied, from a commit that predates the admission. This is what curvecast's WP-L1 pattern
   does, and the machinery does not exist here yet. Since DD140 the admitted columns live in
   one file, so the strip is that file plus `sources.ADMITTED` and `panel.load_daily_admitted`.
2. **Empty `ADMITTED` and rewrite history.** Restores the original guarantee completely and
   destroys the commit graph. Not to be done without explicit instruction.

---

*Decision: `docs/OWNER_ADMISSION_the_credit_tier.md`. Rider:
`docs/RIDER_DD137_the_credit_tier_admitted.md`. Bars: `C125`–`C127`.*
