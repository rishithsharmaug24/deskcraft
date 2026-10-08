# About this copy

This repository is the public copy of a private one. It was rebuilt on 29 September 2026 from the
private repository's files at commit `caea01f`, **not from its history**, and it differs from them
in exactly three ways. `caea01f` is one commit after `8baeada` (tagged `CP-3`, Paper 2 complete) and
changes only the test harness: the plugin that simulates a reviewer's machine now works in a
folder of any name (DD245, bar C226).

## 1. Two data files are withheld

| File | git blob | Carries |
|---|---|---|
| `tests/fixtures/panel_daily_admitted_dev_20260925.csv` | `2450638629981c0548c9dbebd73c5124ae78fcce` | Moody's `BAA10Y` and `AAA10Y`, 1988–2014 |
| `tests/fixtures/panel_daily_admitted_oos_20260928.csv` | `23b17c90a4e12ab2aa6dc181d9c00a94774173d9` | the same two series, 2015–2025 |

Moody's terms forbid copying and redistributing these series, though not computing on them.
`NOT_SENDABLE.md` records the decision that admitted them to the private repository and why that
repository cannot be sent as it stands. Every other data file here is public domain or is a
statistic computed from a licensed source, never a price. The source register is
`src/deskcraft/sources.py`.

**What that costs.** 203 of the 235 tests pass without the two files. The other 32 stop at a missing
file, because the engine's covariance loads the credit panel beside the rates panel:

| Test file | Tests that need the withheld files |
|---|---|
| `tests/test_attribution.py` | 8 |
| `tests/test_readers.py` | 8, including the one that re-runs the out-of-sample read |
| `tests/test_bets.py` | 5 |
| `tests/test_sizing.py` | 5 |
| `tests/test_reverse.py` | 3 |
| `tests/test_admission.py`, `tests/test_guards_and_registers.py`, `tests/test_environment_census.py` | 1 each |

The environment census reports these 32 as bars that "pass with the sibling repositories present".
They pass with the two files present. The code is unchanged, so a reader who obtains the series
from FRED under Moody's terms can rebuild the two files. `git hash-object` then checks a rebuild
against the blob hashes above. The scripts that built them belong to a sibling repository that is
not public.

## 2. One email address is withheld

One line of `docs/AMENDMENT_A1_probe_freeze_split.md` recorded the contact string sent to the SEC
with each EDGAR request. Its email address is replaced with `<email withheld in the public copy>`.
No other file changed.

## 3. Four things are added

`README.md` (the two-page summary), this file, `prereg/`, and `after_the_read/`.

`after_the_read/` was added on 8 October 2026. It holds the two scripts behind online Appendix D of
Paper 1, and their output. Both were computed after the evaluation and were not registered, and
no verdict depends on them. They are not in `caea01f`; they import its engine. Each differs from
the version that produced its output only in its import lines and a note on how to run it: the
line that put the private repository's `src/` on the import path is gone. Run them from the
repository root with `PYTHONPATH=src`. Both need the withheld out-of-sample file in section 1,
because the record's loader joins it to the rates panel, though no figure uses its two series. Run in
this form against the private repository on 8 October 2026, both reproduced their saved output
exactly, apart from line endings.

## Checking the pre-registration yourself

Every rule, prediction and power figure was fixed before the out-of-sample years were read. The
steps below let anyone check that without trusting the author.

1. **The timestamp.** `prereg/MANIFEST.json.ots` is an OpenTimestamps proof for
   `prereg/MANIFEST.json`. With the OpenTimestamps client, run `ots verify prereg/MANIFEST.json.ots`.
   The proof was upgraded on 29 September 2026 and verifies against the Bitcoin blockchain alone.
   Three calendars anchored it, in blocks **968986**, 968987 and 968991. The earliest was mined at
   **11:33:39 UTC on 28 September 2026**. Two times need keeping apart:
   - **What the blockchain proves.** The manifest existed by 11:33:39 UTC. That is 51 minutes after
     the out-of-sample extraction began at 10:42:37 UTC, so the blockchain alone does not place the
     registration before the read.
   - **What places it before the read.** The author's records: the calendars answered the submission
     between 10:40:19 and 10:40:25 UTC, and the extraction and the read were logged at 10:42 and
     10:53 UTC. The calendars keep no signed time a reader can check, so for those 51 minutes the
     order rests on the author's logs, not on the blockchain. The proof as the calendars first
     returned it is `prereg/MANIFEST.json.ots.pending`.
2. **The manifest.** `sha256sum prereg/MANIFEST.json` prints
   `753c3c004a82fb981fd5272132c0a67a3e9deb52d9f7e627385d2dee8f38f634`. The manifest names the
   registered commit, `e8679ad369afe2648c3dba69a3204a00f6cb1241`, and holds the sha256 of that
   commit's complete file listing.
3. **The listing.** `sha256sum prereg/deskcraft_ls-tree.txt` prints
   `781b2a38c8ff21f45a5ebff4f752135c9924303c5f20715a30249509aded7fc6`, the manifest's entry. The
   listing gives the git blob hash of every file in the registered commit.
4. **The rules.** Two documents held every out-of-sample rule, and `prereg/as_timestamped/` holds
   each as it was at the registered commit:
   - `git hash-object prereg/as_timestamped/joint_registration_at_e8679ad.md` prints `9db7235a…`,
     the listing's entry for `docs/PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md`.
   - `git hash-object prereg/as_timestamped/d21_registration_at_e8679ad.md` prints `f976b1e5…`,
     the listing's entry for `docs/PRECOMMIT_deskcraft_d21_hedge_backtest.md`.
5. **What changed after the read.** Diff each timestamped document against its current version in
   `docs/`. In each, two lines changed: the status line, and the closing list of the next free
   identifiers. Everything else added after the read is new sections that record it, 13 and 14 in
   each. D21's section 14 is a comparison the registered rules could not perform. The owner decided
   to run it after the read, and every figure in it is labelled that way. No verdict depends on it.

The same check works for any other file in the listing whose contents have not changed since the
registered commit.
