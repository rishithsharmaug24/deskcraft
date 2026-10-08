"""Figures computed after the read, for Paper 1's revision. Unregistered; no verdict moves.

Rebuilds D14's P&L and sigma paths exactly as readers.run_d14 does, checks them against the
registered record, then computes:
  A. the Diebold-Mariano long-run variance settings actually used (bandwidth per comparison);
  B. H1's size from 10,000 null replications (plus a check with the registered 5,000 inner draws);
  C. the Basel traffic light on a trailing 250-day window, quarterly and daily, and the
     sensitivity of the registered non-overlapping blocks to where they start;
  D. the same battery on the sign-reversed book.

Run from the repository root:  PYTHONPATH=src python after_the_read/after_the_read_figures.py
It needs the withheld file tests/fixtures/panel_daily_admitted_oos_20260928.csv (PUBLIC_COPY.md, 1).
"""
from __future__ import annotations

import math
from collections import Counter

import numpy as np

from deskcraft import covariance as cv
from deskcraft import readers as r
from deskcraft import riskbacktest as rb
from deskcraft import sizing as sz
from deskcraft.attribution import levels_at
from deskcraft.construction import _andrews_bandwidth, _qs_kernel

LEVELS = (0.975, 0.99)
ORDER = ("SAMPLE", "LEDOIT_WOLF", "EWMA", "CRISIS")


def zone(count: int) -> str:
    return next(name for ceiling, name in rb.BASEL_ZONES if count <= ceiling)


# ---------------------------------------------------------------- the record, as run_d14 builds it
record = r.oos_panel(*r.RECORD_FILES)
surface = r.panel_surface(record)
levels = levels_at(r.REAL_AS_OF)
series, matrix = r._exposures(r.US_CASH_BOOK, levels, sz.Unit.STATED)
total = matrix.sum(axis=0)
dates, changes = surface(series)
r._after(dates, r.REAL_FIT)
pnl = changes @ total


def sigmas_for(p: np.ndarray) -> dict[str, np.ndarray]:
    def flat(cov):
        return np.full(p.size, math.sqrt(float(total @ cov @ total)))

    start = float(total @ r._variant_covariance(series, r.REAL_FIT, "EWMA") @ total)
    return {
        "SAMPLE": flat(r._variant_covariance(series, r.REAL_FIT, "SAMPLE")),
        "LEDOIT_WOLF": flat(r._variant_covariance(series, r.REAL_FIT, "LEDOIT_WOLF")),
        "EWMA": rb.ewma_sigma(p, start, cv.EWMA_LAMBDA[cv.Frequency.DAILY]),
        "CRISIS": flat(r._variant_covariance(series, r.REAL_FIT, "CRISIS")),
    }


def battery(p: np.ndarray) -> dict:
    """D14's battery in run_d14's order and with its seed, so the original book reproduces Table 3."""
    rng = np.random.default_rng(r.SEED)
    sig = sigmas_for(p)
    out = {}
    losses = {}
    for name in ORDER:
        s = sig[name]
        row = {}
        for level in LEVELS:
            var, _ = rb.gaussian_forecasts(s, level)
            row[level] = rb.christoffersen(p < -var, 1.0 - level)
        var99, _ = rb.gaussian_forecasts(s, 0.99)
        row["hits99"] = p < -var99
        row["lights"] = rb.traffic_light(row["hits99"])
        row["es"] = rb.acerbi_szekely(p, s, 0.975, rng)
        var, es = rb.gaussian_forecasts(s, 0.975)
        losses[name] = rb.fz0_loss(p, var, es, 0.975)
        row["fz0"] = float(losses[name].mean())
        out[name] = row
    for name in ORDER[1:]:
        out[name]["dm"] = rb.diebold_mariano(losses[name], losses["SAMPLE"])
    out["_losses"] = losses
    return out


orig = battery(pnl)
s = orig["SAMPLE"]
assert pnl.size == 2736
assert (s[0.975].exceptions, s[0.99].exceptions) == (58, 34)
assert abs(s[0.975].kupiec_p - 0.19116) < 5e-6 and abs(s[0.975].independence_p - 0.0013225) < 5e-8
assert abs(s["es"].z2_p - 0.5384) < 1e-9
print(f"Record reproduced: {pnl.size} days, {dates[0]} to {dates[-1]}; SAMPLE 58/34, Kupiec 0.191/0.219, Z2 p 0.538.\n")

# ---------------------------------------------------------------- A. Diebold-Mariano settings
print("A. Diebold-Mariano: FZ0 loss differences against SAMPLE, long-run variance as run")
for name in ORDER[1:]:
    d = orig["_losses"][name] - orig["_losses"]["SAMPLE"]
    x = (d - d.mean())[:, None]
    a = float(np.linalg.lstsq(x[:-1], x[1:], rcond=None)[0][0, 0])
    e = x[1:] - a * x[:-1]
    bw = _andrews_bandwidth(e)
    lags = np.arange(1, e.shape[0])
    w = _qs_kernel(lags / bw)
    big = int((np.abs(w) >= 0.01).sum())
    mean, p = orig[name]["dm"]
    # Sensitivity only: Newey-West (Bartlett) at the textbook lag floor(4 (T/100)^(2/9)), no prewhitening.
    L = int(4 * (d.size / 100) ** (2 / 9))
    g0 = float(x[:, 0] @ x[:, 0] / d.size)
    lrv = g0 + 2 * sum((1 - j / (L + 1)) * float(x[j:, 0] @ x[:-j, 0] / d.size) for j in range(1, L + 1))
    z = d.mean() / math.sqrt(lrv / d.size)
    p_nw = math.erfc(abs(z) / math.sqrt(2))
    print(f"  {name:<12} mean diff {mean:+.4f}  p {p:.2g}  | AR(1) prewhitening coef {a:+.3f}, "
          f"Andrews bandwidth {bw:.2f}, lags with QS weight >= 0.01: {big}  | NW({L}) p {p_nw:.2g}")
print()

# ---------------------------------------------------------------- B. H1's size
rng = np.random.default_rng(r.SEED)
VAR975, ES975 = rb.gaussian_forecasts(np.ones(1), 0.975)
VAR99, _ = rb.gaussian_forecasts(np.ones(1), 0.99)
VAR975, ES975, VAR99 = float(VAR975[0]), float(ES975[0]), float(VAR99[0])


def z2_stat(x: np.ndarray) -> np.ndarray:
    hits = x < -VAR975
    return np.where(hits, x / ES975, 0.0).sum(axis=-1) / (x.shape[-1] * 0.025) + 1.0


def kupiec_vec(counts: np.ndarray, n: int, rate: float) -> np.ndarray:
    return np.array([rb._kupiec_counts(n, int(k), rate) for k in counts])


def wilson(k: int, n: int) -> tuple[float, float]:
    z = 1.959964
    c = (k + z * z / 2) / (n + z * z)
    h = z * math.sqrt(k * (n - k) / n + z * z / 4) / (n + z * z)
    return c - h, c + h


print("B. H1's size (correctly specified Gaussian, constant sigma; H1 fails if any of the three p < 0.05)")
REPS, REF = 10_000, 100_000
for n in (2736, 2760):
    ref = np.concatenate([z2_stat(rng.standard_normal((2000, n))) for _ in range(REF // 2000)])
    ref.sort()
    fails = k975 = k99 = kz2 = 0
    for _ in range(REPS // 1000):
        x = rng.standard_normal((1000, n))
        p975 = kupiec_vec((x < -VAR975).sum(axis=1), n, 0.025)
        p99 = kupiec_vec((x < -VAR99).sum(axis=1), n, 0.01)
        pz2 = np.searchsorted(ref, z2_stat(x), side="right") / ref.size
        fails += int(((p975 < 0.05) | (p99 < 0.05) | (pz2 < 0.05)).sum())
        k975 += int((p975 < 0.05).sum())
        k99 += int((p99 < 0.05).sum())
        kz2 += int((pz2 < 0.05).sum())
    lo, hi = wilson(fails, REPS)
    print(f"  n = {n}: size {fails / REPS:.2%} (95% Wilson {lo:.2%} to {hi:.2%}); "
          f"components: Kupiec 97.5% {k975 / REPS:.2%}, Kupiec 99% {k99 / REPS:.2%}, Z2 {kz2 / REPS:.2%}  "
          f"[{REPS:,} replications, Z2 null from {REF:,} draws]")

# Check: the registered procedure exactly (5,000 fresh inner draws per replication), fewer replications.
CHECK = 1000
n = 2736
fails = 0
sig1 = np.ones(n)
for _ in range(CHECK):
    x = rng.standard_normal(n)
    t = rb.acerbi_szekely(x, sig1, 0.975, rng)
    p975 = rb.kupiec(x < -VAR975, 0.025)
    p99 = rb.kupiec(x < -VAR99, 0.01)
    fails += int(p975 < 0.05 or p99 < 0.05 or t.z2_p < 0.05)
lo, hi = wilson(fails, CHECK)
print(f"  check, n = 2736 with the registered 5,000 inner draws per replication: {fails / CHECK:.2%} "
      f"(95% Wilson {lo:.2%} to {hi:.2%}) over {CHECK:,} replications\n")

# ---------------------------------------------------------------- C. traffic light, trailing window
print("C. Basel traffic light at 99%, trailing 250 days")
qe = [i for i in range(249, len(dates)) if i == len(dates) - 1 or (dates[i + 1].month - 1) // 3 != (dates[i].month - 1) // 3 or dates[i + 1].year != dates[i].year]
for name in ("SAMPLE", "EWMA", "CRISIS"):
    h = orig[name]["hits99"].astype(int)
    roll = np.convolve(h, np.ones(250, dtype=int), mode="valid")  # roll[k] = days k..k+249
    zones_daily = Counter(zone(int(c)) for c in roll)
    q = [(dates[i], int(roll[i - 249])) for i in qe]
    qz = Counter(zone(c) for _, c in q)
    nongreen = [(d.isoformat(), c, zone(c)) for d, c in q if c >= 5]
    peak = int(roll.max())
    peak_end = dates[int(np.argmax(roll)) + 249]
    print(f"  {name}: {len(q)} quarter-ends; green {qz['GREEN']}, yellow {qz['YELLOW']}, red {qz['RED']}. "
          f"Daily windows: green {zones_daily['GREEN']}, yellow {zones_daily['YELLOW']}, red {zones_daily['RED']} "
          f"of {roll.size}. Peak {peak} (window ending {peak_end}).")
    if nongreen:
        print("    quarter-ends not green:", "; ".join(f"{d} {c} {z.lower()}" for d, c, z in nongreen))
    red_days = [dates[k + 249] for k in range(roll.size) if roll[k] >= 10]
    if red_days:
        print(f"    red on {len(red_days)} days, windows ending {red_days[0]} to {red_days[-1]}")
    # The registered blocks start at the first day. Every other start:
    tallies = []
    for off in range(250):
        hb = h[off:]
        zs = [zone(int(hb[k:k + 250].sum())) for k in range(0, hb.size - 249, 250)]
        tallies.append((zs.count("YELLOW"), zs.count("RED")))
    with_red = sum(1 for _, rd in tallies if rd > 0)
    ng = [y + rd for y, rd in tallies]
    print(f"    non-overlapping blocks over all 250 starting offsets: a red block in {with_red} of 250; "
          f"non-green blocks {min(ng)} to {max(ng)} (registered start: {tallies[0][0]} yellow, {tallies[0][1]} red)")
print()

# ---------------------------------------------------------------- D. the sign-reversed book
print("D. Sign-reversed book (every position's sign flipped; Gaussian VaR and ES unchanged)")
mirror = battery(-pnl)
print(f"  {'':<12}{'exc 97.5 (Kupiec p)':>21}{'exc 99 (Kupiec p)':>19}{'indep p 97.5/99':>18}"
      f"{'Z1 p':>8}{'Z2 p':>8}{'FZ0':>9}{'DM p':>10}  blocks (registered start)")
for book, res in (("original", orig), ("reversed", mirror)):
    print(f"  -- {book}")
    for name in ORDER:
        row = res[name]
        c1, c2 = row[0.975], row[0.99]
        dm = f"{row['dm'][1]:.2g}" if "dm" in row else ""
        zl = "".join(z[0] for z in row["lights"])
        print(f"  {name:<12}{c1.exceptions:>6} ({c1.kupiec_p:.3f})      {c2.exceptions:>5} ({c2.kupiec_p:.3f})   "
              f"{c1.independence_p:>7.4f}/{c2.independence_p:.3f}{row['es'].z1_p:>8.3f}{row['es'].z2_p:>8.3f}"
              f"{row['fz0']:>9.3f}{dm:>10}  {zl}")
ms = mirror["SAMPLE"]
h1 = ms[0.975].kupiec_p >= 0.05 and ms[0.99].kupiec_p >= 0.05 and ms["es"].z2_p >= 0.05
h2 = ms[0.975].independence_p >= 0.05
print(f"\n  Reversed book under the registered rules: H1 {'PASS' if h1 else 'FAIL'}, H2 {'PASS' if h2 else 'FAIL'}.")
print("  Block letters: G green, Y yellow, R red, in order from the first block.")
