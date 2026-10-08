"""After the read, unregistered: what drove the Sample 99% exceptions in the peak trailing window
(ending 2023-03-23)? Checks the 5.2 note against SVENY02 around the SVB failure (2023-03-10).

Run from the repository root:  PYTHONPATH=src python after_the_read/march2023_check.py
It needs the withheld file tests/fixtures/panel_daily_admitted_oos_20260928.csv (PUBLIC_COPY.md, 1).
"""
import math
from datetime import date

import numpy as np

from deskcraft import readers as r, riskbacktest as rb, sizing as sz
from deskcraft.attribution import levels_at

record = r.oos_panel(*r.RECORD_FILES)
surface = r.panel_surface(record)
series, matrix = r._exposures(r.US_CASH_BOOK, levels_at(r.REAL_AS_OF), sz.Unit.STATED)
total = matrix.sum(axis=0)
dates, changes = surface(series)
pnl = changes @ total
sig = math.sqrt(float(total @ r._variant_covariance(series, r.REAL_FIT, "SAMPLE") @ total))
var99 = float(rb.gaussian_forecasts(np.full(1, sig), 0.99)[0][0])
var975 = float(rb.gaussian_forecasts(np.full(1, sig), 0.975)[0][0])
hits99 = pnl < -var99
assert pnl.size == 2736 and int(hits99.sum()) == 34 and int((pnl < -var975).sum()) == 58
print("series:", series)
print(f"Sample sigma {sig:,.0f}; 97.5% VaR {var975:,.0f}; 99% VaR {var99:,.0f}")
i02 = series.index("SVENY02")
end = dates.index(date(2023, 3, 23))
win = range(end - 249, end + 1)
print(f"\nPeak window {dates[end-249]} to {dates[end]}: {int(hits99[list(win)].sum())} exceptions at 99%")
print(" date        P&L (US$)   SVENY02 chg (bp)   P&L by position (US$)")
for k in win:
    if hits99[k]:
        contrib = changes[k] * total
        print(f" {dates[k]}  {pnl[k]:>11,.0f}  {changes[k, i02]:>+8.1f}   " +
              ", ".join(f"{s} {c:+,.0f}" for s, c in zip(series, contrib)))
by_month = {}
for k in win:
    if hits99[k]:
        by_month[(dates[k].year, dates[k].month)] = by_month.get((dates[k].year, dates[k].month), 0) + 1
print("\nexceptions in the peak window by month:", dict(sorted(by_month.items())))
# cumulative SVENY02 move over 2023-03-08 .. 2023-03-24 from daily changes
a, b = dates.index(date(2023, 3, 9)), dates.index(date(2023, 3, 24))
print(f"SVENY02 cumulative change 2023-03-09..2023-03-24 (changes from 03-08 close): {changes[a:b+1, i02].sum():+.1f} bp")
for k in range(a - 1, b + 1):
    print(f"  {dates[k]}  SVENY02 {changes[k, i02]:+6.1f} bp   P&L {pnl[k]:>11,.0f}{'  <- 99% exception' if hits99[k] else ('  <- 97.5% exception' if pnl[k] < -var975 else '')}")

# Whole record: on how many of the 34 exceptions at 99% did the 2-year yield fall, and did the euro leg lose?
iex = series.index("DEXUSEU")
idx = np.flatnonzero(hits99)
fell = int((changes[idx, i02] < 0).sum())
eur_lost = int((changes[idx, iex] * total[iex] < 0).sum())
print()
print(f"All {idx.size} exceptions at 99%: 2-year yield fell on {fell}; euro position lost on {eur_lost}.")
