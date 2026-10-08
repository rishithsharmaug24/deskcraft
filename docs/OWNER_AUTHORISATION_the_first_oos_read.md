# The owner's authorisation of the first out-of-sample read

**2026-09-28.** Typed by Claude at the owner's instruction, in the session that runs the read. The
decision is the owner's, and the owner's own words are quoted below. Everything outside the quotes
restates what the owner was told before choosing.

---

## 1. What the owner was asked, and what the owner chose

After the deposit (§3), the owner was asked this, quoted as it was put:

> "The authorisation is the point of no return. Writing it and running the read spends curvecast's
> two remaining looks for anything a deskcraft series touches, from 2015 to the present (DD37). It
> also scores D12, D14, D15, D21 and D22 once on 2015–2025, with no re-run, and freezes every §12
> decision. The repo's rule (DD133) is that you write it. How do you want it written?"

There were three options: write it themselves, not authorise yet, or have it written for them. The
owner chose the third:

> "Write it for me, quoting you"

The instruction that option refers to is the owner's message of the same day, quoted word for word:

> "Upload the deposit.
> Write deskcraft/docs/OWNER_AUTHORISATION_the_first_oos_read.md. It must name DD37, the five
> readers (D12, D14, D15, D21 and D22), both registration documents, and a date no later than the
> day you commit it. It can also cite the deposit's ID.
> Run the read following the registration's §10. Then come D22, D21's replay, landing D16 with the
> CP-2 tag, and Paper 2. please do these and complete these one by one in the most efficient order"

## 2. What is authorised

The first read of rows dated after `DEV_END` (2014-12-31), over `OosWindow.whole()`, 2015-01-01 →
2025-12-31.

- **DD37 fires.** It lives in curvecast's trial ledger, in the non-look entry D3a wrote. Once a row
  dated after `DEV_END` is read here, curvecast's two remaining looks are spent for any hypothesis
  about a series in deskcraft's source register, from 2015 to the present. **This cannot be undone.**
- **Five readers, one surface:** D12, D14, D15, D21 and D22. This one authorisation covers all five,
  as DD133 and DD199 require.
- **Two registration documents**, both in the tree at deskcraft `e8679ad`, tag
  `oos-readers-registered-20260928`:
  - `PRECOMMIT_deskcraft_d12_d14_d15_d22_registration`, which registers D12, D14, D15 and D22;
  - `PRECOMMIT_deskcraft_d21_hedge_backtest`, which registers D21.

  Both exist before this authorisation, so it cannot come ahead of what it authorises. That is
  the order DD134 and DD135 depend on.
- **Order:** the joint registration's §10, one step and one commit at a time. D22 reads under that
  document's §6.1 and §11. D21 reads under its own document's §11 and §12.
- **The decisions before the read are closed.** The joint registration's §12, DD231–DD237, said the
  owner could change them until this file was written. From this file on, none of them can change.

## 3. The deposit (DD237)

Deposited as hashes only, the third route in DD237 and the owner's choice. `MANIFEST.json`, in the
bundle at `C:\Users\rishi\prereg_deposit_20260928\`, has sha256

`753c3c004a82fb981fd5272132c0a67a3e9deb52d9f7e627385d2dee8f38f634`

That manifest fixes deskcraft `e8679ad369afe2648c3dba69a3204a00f6cb1241` and curvecast
`3045a360e1ce748dcff367a4ba798052b5badb98`: their commit objects, their full tree listings, both
archives' sha256, and the blob hash of the one file kept out of the archives. The bundle's
`verify_deposit.py` printed `OK` against it on this day.

The hash was timestamped with OpenTimestamps. It went to four calendars, and each accepted it:
`a.pool.opentimestamps.org` at 10:40:19 UTC, `b.pool.opentimestamps.org` at 10:40:21,
`a.pool.eternitywall.com` at 10:40:23 and `ots.btc.catallaxy.com` at 10:40:25. The proof,
`MANIFEST.json.ots`, is kept beside the bundle and not in this repository. When this file was
written, the proof was still waiting for its Bitcoin confirmation. `ots upgrade` completes it once
the confirmation arrives. Only the hash left the machine: no code, no data and no name.
