"""D17: H11 and H17, scored from the measured fixture curvecast sends (`PRECOMMIT_deskcraft_d17_exposure_extractor.md`).

Registered and not landed (DD182). The scorers are built ahead of the fixtures, to §5's rules, and
every number they need arrives as a statistic: k per firm, per denominator and per class, with its
interval. This module runs no regression, because the prices the regressions ran on may never be
committed here (DD187 item 5), and it opens nothing but the fixture it is given.

k is the variance-minimising multiple of the naive hedge (DD185). So H11's *"the naive notional
exceeds the measured notional by more than 30%"* is k < 1/1.3, and H17's *"structural ÷ measured"*
is 1/k, read as +∞ when k ≤ 0: the measured hedge is nothing, or the wrong way.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.stats import beta

from deskcraft.registers import Verdict

#: §5. A firm counts toward H11 iff its k is below this.
OVERHEDGE = 1 / 1.3
#: §5. H11 passes iff at least this share of the evaluable firms count.
H11_SHARE = 0.70
#: §5. H17's two halves: currency and crude above, rates below.
H17_ABOVE = 2.0
H17_BELOW = 1.5
#: §5. A half with fewer evaluable units than this is refused.
MIN_UNITS = 5
#: §5. The cohort is forty firms (§2), which the missing-data bounds are taken over.
COHORT_SIZE = 40
RESAMPLES = 10_000
SEED = 20260926

EQUITY = "equity"
CASH = "cash"
ALL = "all"
FIRST_HALF = ("currency", "crude")
SECOND_HALF = ("rates",)


@dataclass(frozen=True)
class Measured:
    """One row of `d17_measured_dev_<date>.csv`: a firm, a denominator, a class and its k."""

    cohort_rank: int
    cik: str
    denominator: str
    cls: str
    k: float | None
    k_lo: float | None
    k_hi: float | None
    n: int | None
    drop_reason: str


def _float(text: str) -> float | None:
    return float(text) if text not in ("", None) else None


def load_measured(path: Path) -> tuple[Measured, ...]:
    with open(path, newline="", encoding="utf-8") as handle:
        return tuple(
            Measured(
                cohort_rank=int(row["cohort_rank"]),
                cik=row["cik"],
                denominator=row["denominator"],
                cls=row["class"],
                k=_float(row["k"]),
                k_lo=_float(row["k_lo"]),
                k_hi=_float(row["k_hi"]),
                n=int(row["n"]) if row["n"] else None,
                drop_reason=row["drop_reason"],
            )
            for row in csv.DictReader(handle)
        )


def ratio(k: float) -> float:
    """Structural ÷ measured, DD185: 1/k, and +∞ when the measured hedge is nothing or backwards."""
    return math.inf if k <= 0 else 1.0 / k


def clopper_pearson(count: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """The exact two-sided interval `AMENDMENT_A1` §5.3 fixes for a prevalence."""
    tail = (1.0 - level) / 2.0
    lo = 0.0 if count == 0 else float(beta.ppf(tail, count, n - count + 1))
    hi = 1.0 if count == n else float(beta.ppf(1.0 - tail, count + 1, n - count))
    return lo, hi


def median(values: np.ndarray) -> float:
    """The middle value, or the mean of the middle two. +∞ is a value like any other here."""
    ordered = np.sort(values)
    n = len(ordered)
    if n % 2:
        return float(ordered[n // 2])
    a, b = ordered[n // 2 - 1], ordered[n // 2]
    return float("inf") if math.isinf(a) or math.isinf(b) else float((a + b) / 2.0)


def firm_bootstrap(groups: list[list[float]], seed: int = SEED) -> tuple[float, float]:
    """A bootstrap percentile interval for the median, resampling firms with all their units (§5)."""
    rng = np.random.default_rng(seed)
    medians = np.empty(RESAMPLES)
    for b in range(RESAMPLES):
        picks = rng.integers(len(groups), size=len(groups))
        medians[b] = median(np.array([v for i in picks for v in groups[i]]))
    lo, hi = np.percentile(medians, [2.5, 97.5], method="inverted_cdf")
    return float(lo), float(hi)


@dataclass(frozen=True)
class H11Result:
    denominator: str
    evaluable: int
    counted: int
    share: float | None
    share_interval: tuple[float, float] | None
    median_k: float | None
    median_interval: tuple[float, float] | None
    bound_low: float
    bound_high: float
    resolved_below: int
    resolved_above: int
    verdict: Verdict


def h11(rows: tuple[Measured, ...], denominator: str = EQUITY, cohort_size: int = COHORT_SIZE) -> H11Result:
    """§5's H11 on one denominator: the median k first, the count with its interval, the verdict."""
    firms = [r for r in rows if r.denominator == denominator and r.cls == ALL and r.k is not None]
    n = len(firms)
    counted = sum(1 for r in firms if r.k < OVERHEDGE)
    missing = cohort_size - n
    bound_low, bound_high = counted / cohort_size, (counted + missing) / cohort_size
    below = sum(1 for r in firms if r.k_hi is not None and r.k_hi < OVERHEDGE)
    above = sum(1 for r in firms if r.k_lo is not None and r.k_lo > OVERHEDGE)
    if n == 0:
        return H11Result(denominator, 0, 0, None, None, None, None, bound_low, bound_high, 0, 0, Verdict.NOT_PERFORMED)
    ks = np.array([r.k for r in firms])
    share = counted / n
    return H11Result(
        denominator=denominator,
        evaluable=n,
        counted=counted,
        share=share,
        share_interval=clopper_pearson(counted, n),
        median_k=median(ks),
        median_interval=firm_bootstrap([[k] for k in ks]),
        bound_low=bound_low,
        bound_high=bound_high,
        resolved_below=below,
        resolved_above=above,
        verdict=Verdict.PASS if share >= H11_SHARE else Verdict.FAIL,
    )


@dataclass(frozen=True)
class Half:
    units: int
    firms: int
    median_ratio: float | None
    interval: tuple[float, float] | None
    holds: bool | None


@dataclass(frozen=True)
class H17Result:
    denominator: str
    first: Half
    second: Half
    by_class: dict[str, Half]
    verdict: Verdict


def _half(rows: list[Measured], classes: tuple[str, ...], holds_if) -> Half:
    groups: dict[str, list[float]] = {}
    for r in rows:
        if r.cls in classes and r.k is not None:
            groups.setdefault(r.cik, []).append(ratio(r.k))
    units = sum(len(g) for g in groups.values())
    if units < MIN_UNITS:
        return Half(units, len(groups), None, None, None)
    values = np.array([v for g in groups.values() for v in g])
    m = median(values)
    return Half(units, len(groups), m, firm_bootstrap(list(groups.values())), holds_if(m))


def h17(rows: tuple[Measured, ...], denominator: str = EQUITY) -> H17Result:
    """§5's H17 on one denominator. PASS iff both halves hold; a refused half refuses the claim."""
    mine = [r for r in rows if r.denominator == denominator]
    first = _half(mine, FIRST_HALF, lambda m: m > H17_ABOVE)
    second = _half(mine, SECOND_HALF, lambda m: m < H17_BELOW)
    by_class = {
        cls: _half(mine, (cls,), lambda m: m > H17_ABOVE if cls in FIRST_HALF else m < H17_BELOW)
        for cls in FIRST_HALF + SECOND_HALF
    }
    if first.holds is None or second.holds is None:
        verdict = Verdict.NOT_PERFORMED
    else:
        verdict = Verdict.PASS if (first.holds and second.holds) else Verdict.FAIL
    return H17Result(denominator, first, second, by_class, verdict)
