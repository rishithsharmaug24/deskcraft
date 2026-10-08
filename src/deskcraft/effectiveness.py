"""D21: hedge effectiveness in and out of sample, scored ahead of both halves (`PRECOMMIT_deskcraft_d21_hedge_backtest.md`).

Registered and not landed (DD199). The loop the build order names -- filing, exposure, structure,
replay -- is D17's k, D18's menu and gate, and a replay held from 2014-12-24. This module scores
it. It runs no regression on a price: the in-sample half is D17's measured fixture, whose R² *is*
the in-sample Ederington effectiveness (DD200), and the out-of-sample half arrives from curvecast
as statistics (DD202). What it does run is the structure engine, which needs only a factor path,
and the null simulations the pre-commit publishes before any number exists.

**Effectiveness, not R².** Ederington's measure is 1 − Var(hedged) / Var(unhedged). With the
hedge ratio fitted by least squares on the same sample it equals the regression's R², so it lies
in [0, 1]. Out of sample the ratio is held, and a held ratio can add variance: the measure can be
negative, and the register's "OOS R²" means this number.

**Two numbers beside H12a, with no verdict (§12).** DD210 marks the alternatives again at the
Minneapolis Fed's implied volatility where its markets map to D17's factors; this module reads the
Fed's file by that rule and never fetches it. DD211 marks D18's refused 2:1 ratio forward on the
same path and measures the worst fall of its P&L behind the forward's.
"""

from __future__ import annotations

import csv
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.stats import f as f_dist

from deskcraft.covariance import EWMA_LAMBDA, Frequency
from deskcraft.exposure import (
    COHORT_SIZE,
    SEED,
    clopper_pearson,
    firm_bootstrap,
    median,
)
from deskcraft.hedging import (
    COLLAR_OFFSET_SD,
    PARTICIPATION,
    RATIO,
    Exposure,
    HedgeStructure,
    Model,
    Payoff,
    Side,
    StructureLeg,
    Unsuitable,
    bachelier_value,
    black76_value,
    gk_value,
    worst_obligation,
)
from deskcraft.registers import Verdict
from deskcraft.scenarios import REPLAY_WINDOWS
from deskcraft.window import OOS_START, OosWindow

#: DD203. H14a counts a firm whose out-of-sample effectiveness is below this.
H14A_LEVEL = 0.5
#: DD203. H14b counts a firm whose out-of-sample effectiveness is below this share of in-sample.
H14B_FRACTION = 0.5
#: DD203. Both halves of H14 pass iff at least this share of the evaluable firms count.
H14_SHARE = 0.70
#: DD204. The forward captures a structure's variance reduction if it reaches this share of it.
H12A_CAPTURE = 0.9
#: DD204. H12a passes iff at least this share of its eligible firms count: the median's threshold.
H12A_SHARE = 0.5
#: DD204. Fewer eligible firms than this, and H12a is refused.
MIN_UNITS = 5
#: DD201. A firm with fewer out-of-sample weekly returns than this is not evaluable; D17's minimum.
MIN_OOS_WEEKS = 100
#: DD201. The verdict window: weeks inside [OOS_START, the last WTI settle EIA publishes], the same
#: for every firm (DD127's rule: no firm is scored on a shorter sample than another).
VERDICT_END = date(2024, 4, 5)
#: DD204. A structure is struck at an observation and settles at the 26th after it.
TENOR_WEEKS = 26
TENOR_DAYS = 182
#: DD204. Volatility: D8's daily EWMA, normalised weights, annualised on 252 sessions.
EWMA_DECAY = EWMA_LAMBDA[Frequency.DAILY]
SESSIONS = 252.0
#: The null tables' replication count, fixed with the seed before they were run.
NULL_REPS = 200_000

#: DD204. The three structures H12a compares the forward against. The 2:1 ratio forward is not
#: among them: D18's gate refuses it, and a structure no client may hold is not an alternative.
ALTERNATIVES = ("bought option", "zero-cost collar", "participating forward")
STRUCTURES = ("forward",) + ALTERNATIVES

#: DD211. D18's fifth structure, which the gate refuses at any multiple above one half. Marked beside
#: H12a on the record's path; never an alternative, and never constructed through the gate.
REFUSED = "2:1 ratio forward"
#: DD211. The two stress windows its worst fall is also read inside, and the columns that carry them.
GAP_COLUMNS = {"NBER_2020": "ratio_gap_2020", "RATES_2022": "ratio_gap_2022"}
GAP_WINDOWS: dict[str, OosWindow] = {w.name: w.window for w in REPLAY_WINDOWS if w.name in GAP_COLUMNS}

#: DD210. The Minneapolis Fed's market for each of D17's factors it publishes a distribution for.
#: Every other factor keeps DD204's EWMA, and is counted.
IMPLIED_MARKETS = {"EUR": "euro", "GBP": "pound", "JPY": "yen", "WTI_C2": "oil"}
#: DD210. The horizon the Fed's `sd` is measured over, so σ = sd / √½.
IMPLIED_HORIZON_YEARS = 0.5
#: DD210. A release more than this many days before the observation is not used (D17's tolerance).
IMPLIED_STALE_DAYS = 10
#: DD210. A mapped market whose median `sd` exceeds this is read as percent.
PERCENT_THRESHOLD = 1.0


# --------------------------------------------------------------------------------------------
# The measure, and the null the pre-commit publishes (§6)
# --------------------------------------------------------------------------------------------


def ederington(unhedged: np.ndarray, hedge: np.ndarray) -> float:
    """1 − Var(unhedged + hedge) / Var(unhedged). `hedge` is the hedge's own P&L, same units."""
    unhedged = np.asarray(unhedged, dtype=float)
    hedged = unhedged + np.asarray(hedge, dtype=float)
    base = float(np.var(unhedged))
    if base == 0.0:
        return float("nan")
    return 1.0 - float(np.var(hedged)) / base


def null_r2_threshold(n: int, level: float = 0.95) -> float:
    """The in-sample R² a regression on noise exceeds with probability 1 − `level`: the F test on
    one slope, R² = F / (F + n − 2). Above it, a firm's hedge is one the data can see (DD203)."""
    crit = float(f_dist.ppf(level, 1, n - 2))
    return crit / (crit + n - 2)


def _draw(rng: np.random.Generator, n: int, reps: int, var_x: float) -> tuple[np.ndarray, ...]:
    """Centred sufficient statistics of a sample of n normal pairs: Sxx, Sxe, See, with σ_e = 1.

    Sxx is var_x · χ²(n−1). Given Sxx, Sxe is normal with variance Sxx, and See is Sxe²/Sxx plus
    an independent χ²(n−2): the regression's decomposition, drawn directly rather than summed.
    """
    sxx = var_x * rng.chisquare(n - 1, reps)
    sxe = rng.standard_normal(reps) * np.sqrt(sxx)
    see = sxe**2 / sxx + rng.chisquare(n - 2, reps)
    return sxx, sxe, see


def null_decay(
    r2: float,
    n_in: int,
    n_out: int,
    variance_ratio: float,
    decay: float = 1.0,
    reps: int = NULL_REPS,
    seed: int = SEED,
) -> tuple[float, float, float]:
    """P(in-sample R² < ½), P(held out-of-sample effectiveness < ½), P(it is < ½ × in-sample).

    y = k·x + e in sample and y = decay·k·x + e out of it, σ_e = 1 both sides, k set so the true
    in-sample R² is `r2`, the factor's variance multiplied by `variance_ratio` out of sample. The
    hedge ratio is the in-sample least-squares slope, held. `decay` 1 is H14b's null: no true decay,
    so every firm H14b counts under it is counted by estimation noise and the factor's variance.
    """
    rng = np.random.default_rng(seed)
    k = math.sqrt(r2 / (1.0 - r2)) if r2 > 0.0 else 0.0
    sxx, sxe, see = _draw(rng, n_in, reps, 1.0)
    k_hat = k + sxe / sxx
    syy = k * k * sxx + 2.0 * k * sxe + see
    r2_in = (k * sxx + sxe) ** 2 / (sxx * syy)
    beta = decay * k
    oxx, oxe, oee = _draw(rng, n_out, reps, variance_ratio)
    oyy = beta * beta * oxx + 2.0 * beta * oxe + oee
    gap = beta - k_hat
    resid = gap * gap * oxx + 2.0 * gap * oxe + oee
    eff_out = 1.0 - resid / oyy
    return (
        float(np.mean(r2_in < H14A_LEVEL)),
        float(np.mean(eff_out < H14A_LEVEL)),
        float(np.mean(eff_out < H14B_FRACTION * r2_in)),
    )


# --------------------------------------------------------------------------------------------
# The two halves, as they arrive
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class InSample:
    """D17's equity row for a firm's whole stated exposure (class `all`): its k and R² (DD200)."""

    cohort_rank: int
    cik: str
    k: float | None
    k_lo: float | None
    k_hi: float | None
    n: int | None
    r2: float | None
    drop_reason: str

    @property
    def fitted(self) -> bool:
        return self.k is not None and self.r2 is not None

    @property
    def resolved(self) -> bool:
        """DD204: the hedge is one the in-sample data can see -- k's interval lies above zero."""
        return self.fitted and self.k_lo is not None and self.k_lo > 0.0

    @property
    def multiple(self) -> float | None:
        """DD204: the gated hedge, as a multiple of the stated exposure. D18's gate refuses
        leverage above one on the stated flow, so a least-squares k above one is cut to one."""
        return None if not self.resolved else min(self.k, 1.0)


def _float(text: str | None) -> float | None:
    return float(text) if text not in ("", None) else None


def load_in_sample(path: Path) -> tuple[InSample, ...]:
    """The equity, class-`all` rows of `d17_measured_dev_<date>.csv`, one per cohort firm."""
    with open(path, newline="", encoding="utf-8") as handle:
        return tuple(
            InSample(
                cohort_rank=int(row["cohort_rank"]),
                cik=row["cik"],
                k=_float(row["k"]),
                k_lo=_float(row["k_lo"]),
                k_hi=_float(row["k_hi"]),
                n=int(row["n"]) if row["n"] else None,
                r2=_float(row["r2"]),
                drop_reason=row["drop_reason"],
            )
            for row in csv.DictReader(handle)
            if row["denominator"] == "equity" and row["class"] == "all"
        )


@dataclass(frozen=True)
class Replayed:
    """One row of D21's out-of-sample fixture (DD202): statistics only, never a price."""

    cohort_rank: int
    cik: str
    n: int | None
    effectiveness: float | None
    eff_lo: float | None
    eff_hi: float | None
    #: Variance reduction of each structure at the gated multiple, for H12a's eligible firms.
    reduction: dict[str, float | None]
    drop_reason: str
    #: DD210, beside H12a: the three alternatives' reductions with each mapped leg's options at the
    #: Minneapolis Fed's volatility. The forward reads no volatility, so it has no second number.
    reduction_implied: dict[str, float | None] = field(default_factory=dict)
    #: DD210: of the option marks on the firm's mapped legs, the fraction the Fed priced. None where
    #: the firm has no mapped leg.
    implied_fraction: float | None = None
    #: DD210: what was read, or why nothing was. The same on every row.
    implied_basis: str = ""
    #: DD211: the refused ratio forward's reduction at the gated multiple, and at the stated exposure.
    ratio_reduction: float | None = None
    ratio_reduction_stated: float | None = None
    #: DD211: the worst fall of its P&L less the forward's, per dollar of stated exposure, over the
    #: verdict weeks and inside each of `GAP_WINDOWS` by name.
    ratio_gap: float | None = None
    ratio_gap_window: dict[str, float | None] = field(default_factory=dict)


def _column(name: str) -> str:
    return name.replace(" ", "_").replace("-", "_")


def load_replayed(path: Path) -> tuple[Replayed, ...]:
    """D21's out-of-sample fixture. Taken as a path: no module here names an out-of-sample file
    (C119), and this one is dated past `DEV_END` by its first date column, as it should be. The
    columns DD210 and DD211 append are read where present."""
    with open(path, newline="", encoding="utf-8") as handle:
        return tuple(
            Replayed(
                cohort_rank=int(row["cohort_rank"]),
                cik=row["cik"],
                n=int(row["n"]) if row["n"] else None,
                effectiveness=_float(row["effectiveness"]),
                eff_lo=_float(row["eff_lo"]),
                eff_hi=_float(row["eff_hi"]),
                reduction={name: _float(row[f"vr_{name.replace(' ', '_').replace('-', '_')}"]) for name in STRUCTURES},
                drop_reason=row["drop_reason"],
                reduction_implied={name: _float(row.get(f"vr_{_column(name)}_implied")) for name in ALTERNATIVES},
                implied_fraction=_float(row.get("implied_fraction")),
                implied_basis=row.get("implied_basis") or "",
                ratio_reduction=_float(row.get("vr_ratio_forward")),
                ratio_reduction_stated=_float(row.get("vr_ratio_forward_stated")),
                ratio_gap=_float(row.get("ratio_gap")),
                ratio_gap_window={name: _float(row.get(column)) for name, column in GAP_COLUMNS.items()},
            )
            for row in csv.DictReader(handle)
        )


def _paired(in_sample: tuple[InSample, ...], replayed: tuple[Replayed, ...]):
    by_cik = {row.cik: row for row in replayed}
    for firm in in_sample:
        yield firm, by_cik.get(firm.cik)


# --------------------------------------------------------------------------------------------
# H14a and H14b (DD203)
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Count:
    counted: int
    evaluable: int
    interval: tuple[float, float]
    verdict: Verdict

    @property
    def share(self) -> float:
        return self.counted / self.evaluable if self.evaluable else float("nan")


def _count(counted: int, evaluable: int, share: float) -> Count:
    if evaluable == 0:
        return Count(0, 0, (float("nan"), float("nan")), Verdict.NOT_PERFORMED)
    verdict = Verdict.PASS if counted / evaluable >= share else Verdict.FAIL
    return Count(counted, evaluable, clopper_pearson(counted, evaluable), verdict)


@dataclass(frozen=True)
class H14Result:
    evaluable: int
    median_out: float
    median_out_interval: tuple[float, float]
    median_in: float
    #: A1 §5.3's decay row: the cohort median of effectiveness_OOS ÷ R²_in, and its interval.
    median_ratio: float
    median_ratio_interval: tuple[float, float]
    level: Count
    decay: Count
    #: In H14a and not in H14b: weak but not decaying, the diagnosis A1 §5.2 calls informative.
    weak_not_decaying: int
    #: H14a's in-sample shadow: evaluable firms whose in-sample R² is already below ½.
    level_in_sample: int
    #: DD203: firms whose in-sample R² clears the null's 95th percentile, and how many H14b takes.
    resolved: int
    decay_resolved: int
    bounds_level: tuple[float, float]
    bounds_decay: tuple[float, float]


def _decay_ratio(out: float, r2_in: float) -> float:
    """effectiveness_OOS ÷ R²_in. An in-sample R² of exactly zero leaves only the sign."""
    if r2_in > 0.0:
        return out / r2_in
    return math.copysign(math.inf, out) if out != 0.0 else 0.0


def h14(in_sample: tuple[InSample, ...], replayed: tuple[Replayed, ...], cohort_size: int = COHORT_SIZE) -> H14Result:
    """H14a and H14b over the firms with an in-sample fit and enough out-of-sample weeks."""
    pairs = [
        (firm, out)
        for firm, out in _paired(in_sample, replayed)
        if firm.fitted and out is not None and out.effectiveness is not None and (out.n or 0) >= MIN_OOS_WEEKS
    ]
    level = [out.effectiveness < H14A_LEVEL for _, out in pairs]
    decay = [out.effectiveness < H14B_FRACTION * firm.r2 for firm, out in pairs]
    evaluable = len(pairs)
    missing = cohort_size - evaluable
    threshold = {firm.n: null_r2_threshold(firm.n) for firm, _ in pairs if firm.n}
    resolved = [(firm, d) for (firm, _), d in zip(pairs, decay) if firm.n and firm.r2 > threshold[firm.n]]
    outs = np.array([out.effectiveness for _, out in pairs])
    ins = np.array([firm.r2 for firm, _ in pairs])
    ratios = np.array([_decay_ratio(out.effectiveness, firm.r2) for firm, out in pairs])
    return H14Result(
        evaluable=evaluable,
        median_out=median(outs) if evaluable else float("nan"),
        median_out_interval=firm_bootstrap([[v] for v in outs]) if evaluable else (float("nan"), float("nan")),
        median_in=median(ins) if evaluable else float("nan"),
        median_ratio=median(ratios) if evaluable else float("nan"),
        median_ratio_interval=firm_bootstrap([[v] for v in ratios]) if evaluable else (float("nan"),) * 2,
        level=_count(sum(level), evaluable, H14_SHARE),
        decay=_count(sum(decay), evaluable, H14_SHARE),
        weak_not_decaying=sum(a and not b for a, b in zip(level, decay)),
        level_in_sample=int(np.sum(ins < H14A_LEVEL)),
        resolved=len(resolved),
        decay_resolved=sum(d for _, d in resolved),
        bounds_level=(sum(level) / cohort_size, (sum(level) + missing) / cohort_size),
        bounds_decay=(sum(decay) / cohort_size, (sum(decay) + missing) / cohort_size),
    )


# --------------------------------------------------------------------------------------------
# H12a (DD204)
# --------------------------------------------------------------------------------------------


def captures(forward: float, best: float) -> bool:
    """DD204: the forward captures ≥ 90% of the best alternative's variance reduction; and where
    no alternative reduces variance at all, it is no worse than the best of them."""
    if best > 0.0:
        return forward >= H12A_CAPTURE * best
    return forward >= best


@dataclass(frozen=True)
class H12aResult:
    eligible: int
    counted: int
    interval: tuple[float, float]
    verdict: Verdict
    #: Over eligible firms whose best alternative reduces variance: VR(forward) ÷ VR(best).
    median_capture: float
    median_capture_interval: tuple[float, float]
    #: Eligible firms where no alternative reduced variance.
    nothing_to_capture: int
    #: The alternative that won, per eligible firm, counted by name.
    best_by_name: dict[str, int]
    median_reduction: dict[str, float]


def h12a(in_sample: tuple[InSample, ...], replayed: tuple[Replayed, ...]) -> H12aResult:
    """H12a over the firms whose in-sample hedge is resolved and whose replay carries every
    structure's variance reduction."""
    rows = []
    for firm, out in _paired(in_sample, replayed):
        if not firm.resolved or out is None or (out.n or 0) < MIN_OOS_WEEKS:
            continue
        if any(out.reduction.get(name) is None for name in STRUCTURES):
            continue
        rows.append(out.reduction)
    eligible = len(rows)
    if eligible < MIN_UNITS:
        nan = float("nan")
        return H12aResult(eligible, 0, (nan, nan), Verdict.NOT_PERFORMED, nan, (nan, nan), 0, {}, {})
    counted, ratios, winners, nothing = 0, [], {name: 0 for name in ALTERNATIVES}, 0
    for vr in rows:
        name = max(ALTERNATIVES, key=lambda s: (vr[s], -ALTERNATIVES.index(s)))
        winners[name] += 1
        best = vr[name]
        counted += captures(vr["forward"], best)
        if best > 0.0:
            ratios.append(vr["forward"] / best)
        else:
            nothing += 1
    verdict = Verdict.PASS if counted / eligible >= H12A_SHARE else Verdict.FAIL
    ratio = np.array(ratios)
    return H12aResult(
        eligible=eligible,
        counted=counted,
        interval=clopper_pearson(counted, eligible),
        verdict=verdict,
        median_capture=median(ratio) if len(ratio) else float("nan"),
        median_capture_interval=firm_bootstrap([[v] for v in ratio]) if len(ratio) else (float("nan"),) * 2,
        nothing_to_capture=nothing,
        best_by_name=winners,
        median_reduction={name: median(np.array([vr[name] for vr in rows])) for name in STRUCTURES},
    )


# --------------------------------------------------------------------------------------------
# Beside H12a, with no verdict (§12: DD210, DD211)
# --------------------------------------------------------------------------------------------


def _eligible(firm: InSample, out: Replayed | None) -> bool:
    """H12a's own eligibility, repeated so that a beside number is taken on H12a's firms."""
    if not firm.resolved or out is None or (out.n or 0) < MIN_OOS_WEEKS:
        return False
    return all(out.reduction.get(name) is not None for name in STRUCTURES)


def _best(vr: dict[str, float]) -> str:
    return max(ALTERNATIVES, key=lambda s: (vr[s], -ALTERNATIVES.index(s)))


def _middle(values: list[float]) -> float:
    return median(np.array(values)) if values else float("nan")


@dataclass(frozen=True)
class ImpliedBeside:
    """DD210 item 7. H12a's comparison again, the alternatives marked at the Fed's volatility where
    a leg maps and a release is fresh. **It carries no verdict**: H12a's is `h12a`'s, on EWMA."""

    basis: str
    #: H12a's eligible firms that carry the implied reductions, and of them the ones with a mapped leg.
    firms: int
    mapped: int
    #: Firms counted on EWMA (H12a's own count on these firms) and on the Fed's volatility.
    counted: tuple[int, int]
    #: Cohort ranks whose count differs between the two.
    moved: tuple[int, ...]
    #: Over the mapped firms whose best alternative reduces variance: the median VR_forward ÷ VR_best,
    #: on EWMA and on the Fed's volatility.
    median_capture_mapped: tuple[float, float]
    #: The winning alternative on the Fed's volatility, per firm, by name.
    best_by_name: dict[str, int]
    #: The median, over the mapped firms, of the fraction of their mapped legs' marks the Fed priced.
    median_fraction: float


def h12a_implied(in_sample: tuple[InSample, ...], replayed: tuple[Replayed, ...]) -> ImpliedBeside:
    """DD210: H12a's firms, rule and tie-break, with the alternatives' reductions read from the
    implied columns and the forward's from DD204's. Scores nothing."""
    basis = next((out.implied_basis for out in replayed if out.implied_basis), "")
    counted, moved, winners = [0, 0], [], {name: 0 for name in ALTERNATIVES}
    captured: tuple[list[float], list[float]] = ([], [])
    firms, fractions = 0, []
    for firm, out in _paired(in_sample, replayed):
        if not _eligible(firm, out) or any(out.reduction_implied.get(n) is None for n in ALTERNATIVES):
            continue
        firms += 1
        implied = {"forward": out.reduction["forward"], **{n: out.reduction_implied[n] for n in ALTERNATIVES}}
        winners[_best(implied)] += 1
        flags = []
        for side, vr in enumerate((out.reduction, implied)):
            best = vr[_best(vr)]
            flags.append(captures(vr["forward"], best))
            counted[side] += flags[-1]
            if out.implied_fraction is not None and best > 0.0:
                captured[side].append(vr["forward"] / best)
        if flags[0] != flags[1]:
            moved.append(out.cohort_rank)
        if out.implied_fraction is not None:
            fractions.append(out.implied_fraction)
    return ImpliedBeside(
        basis=basis,
        firms=firms,
        mapped=len(fractions),
        counted=(counted[0], counted[1]),
        moved=tuple(moved),
        median_capture_mapped=(_middle(captured[0]), _middle(captured[1])),
        best_by_name=winners,
        median_fraction=_middle(fractions),
    )


@dataclass(frozen=True)
class RatioBeside:
    """DD211. What the refused 2:1 ratio forward did on the record, beside H12a. **No verdict.**"""

    #: Firms carrying the worst fall over the verdict weeks; its median, its largest, and whose.
    firms: int
    median_gap: float
    largest_gap: float
    largest_rank: int | None
    #: The same inside each of `GAP_WINDOWS`, by name: (firms, median, largest, rank).
    windows: dict[str, tuple[int, float, float, int | None]]
    #: H12a's eligible firms whose ratio forward reduces at least the forward's variance at the gated
    #: multiple, as (at least, of), where k exceeds one and where it does not.
    ahead_k_above_one: tuple[int, int]
    ahead_k_at_most_one: tuple[int, int]


def _gap_summary(pairs: list[tuple[int, float]]) -> tuple[int, float, float, int | None]:
    if not pairs:
        return 0, float("nan"), float("nan"), None
    rank, largest = max(pairs, key=lambda p: p[1])
    return len(pairs), _middle([gap for _, gap in pairs]), largest, rank


def ratio_beside(in_sample: tuple[InSample, ...], replayed: tuple[Replayed, ...]) -> RatioBeside:
    """DD211 items 2 and 3 over the rows that carry them. Scores nothing."""
    whole = [(out.cohort_rank, out.ratio_gap) for out in replayed if out.ratio_gap is not None and (out.n or 0) >= MIN_OOS_WEEKS]
    windows = {
        name: _gap_summary(
            [(out.cohort_rank, out.ratio_gap_window[name]) for out in replayed if out.ratio_gap_window.get(name) is not None]
        )
        for name in GAP_WINDOWS
    }
    ahead = {True: [0, 0], False: [0, 0]}
    for firm, out in _paired(in_sample, replayed):
        if not _eligible(firm, out) or out.ratio_reduction is None:
            continue
        tally = ahead[firm.k > 1.0]
        tally[0] += out.ratio_reduction >= out.reduction["forward"]
        tally[1] += 1
    firms, middle, largest, rank = _gap_summary(whole)
    return RatioBeside(
        firms=firms,
        median_gap=middle,
        largest_gap=largest,
        largest_rank=rank,
        windows=windows,
        ahead_k_above_one=(ahead[True][0], ahead[True][1]),
        ahead_k_at_most_one=(ahead[False][0], ahead[False][1]),
    )


def worst_fall(pnl: np.ndarray) -> float:
    """DD211 item 2: the largest fall of the cumulative P&L from its running peak, the peak starting
    at zero. Nonnegative; zero for a path that never falls below its best."""
    path = np.concatenate([[0.0], np.cumsum(np.asarray(pnl, dtype=float))])
    return float(np.max(np.maximum.accumulate(path) - path))


def window_weeks(days: list[date], window: OosWindow) -> list[int]:
    """DD211 item 2: the weekly returns whose two observations both lie in `window`, each by the
    index of its first observation, so the return from observation i to i + 1 is index i."""
    return [i for i, (a, b) in enumerate(zip(days, days[1:])) if window.start <= a and b <= window.end]


# --------------------------------------------------------------------------------------------
# The Minneapolis Fed's file, read by DD210's rule
# --------------------------------------------------------------------------------------------


class ImpliedUnreadable(ValueError):
    """DD210 item 5: the Fed's file cannot be read by the rule, so the sensitivity is not performed."""


def _release_day(text: str | None) -> date | None:
    """DD210 item 5: an ISO date, optionally at a zero time, or M/D/YYYY. Anything else is not one."""
    text = (text or "").strip()
    try:
        if len(text) >= 10 and text[4] == text[7] == "-" and (text[:4] + text[5:7] + text[8:10]).isdigit():
            if text[10:] in ("", " 00:00", " 00:00:00", "T00:00", "T00:00:00"):
                return date(int(text[:4]), int(text[5:7]), int(text[8:10]))
            return None
        parts = text.split("/")
        if len(parts) == 3 and all(p.isdigit() for p in parts) and len(parts[2]) == 4 and all(1 <= len(p) <= 2 for p in parts[:2]):
            return date(int(parts[2]), int(parts[0]), int(parts[1]))
    except ValueError:
        return None
    return None


def implied_rows(text: str, until: date) -> list[dict[str, str]]:
    """DD210 items 5 and 6: the mapped markets' rows dated on or before `until`, as the date in ISO,
    the market and `sd` as it arrived. Every other row is dropped here, before anything is kept.

    The date column is the one column whose every value is a date, and the market column the one
    column that carries all four mapped names; `sd` must be a column. Anything else raises
    `ImpliedUnreadable`, never a guess."""
    reader = csv.DictReader(text.splitlines())
    header = [name for name in (reader.fieldnames or []) if name]
    rows = list(reader)
    if not rows:
        raise ImpliedUnreadable("the file has no rows")
    dated = [c for c in header if all(_release_day(row.get(c)) is not None for row in rows)]
    if len(dated) != 1:
        raise ImpliedUnreadable(f"{len(dated)} columns whose every value is a date, not one")
    names = set(IMPLIED_MARKETS.values())
    marked = [c for c in header if names <= {(row.get(c) or "").strip() for row in rows}]
    if len(marked) != 1:
        raise ImpliedUnreadable(f"{len(marked)} columns carrying all four mapped markets, not one")
    if "sd" not in header:
        raise ImpliedUnreadable("no column named sd")
    (day_column,), (market_column,) = dated, marked
    out = []
    for row in rows:
        day, market = _release_day(row[day_column]), (row[market_column] or "").strip()
        if market in names and day <= until:
            out.append({"date": day.isoformat(), "market": market, "sd": (row.get("sd") or "").strip()})
    return out


@dataclass(frozen=True)
class ImpliedReleases:
    """DD210: each mapped market's releases as annualised volatility, and what reading them did."""

    #: Market name to (release days as ordinals, ascending; σ at each).
    by_market: dict[str, tuple[np.ndarray, np.ndarray]]
    #: Markets whose `sd` was read as percent (item 5).
    percent: tuple[str, ...] = ()
    #: Rows refused for an `sd` that is not finite or not positive.
    refused: int = 0

    def volatility(self, instrument: str, day: date) -> float | None:
        """Item 4: the latest release on or before `day` if it is no more than ten days old. None
        otherwise, and for an instrument the Fed's markets do not map."""
        market = IMPLIED_MARKETS.get(instrument)
        if market not in self.by_market:
            return None
        days, sigmas = self.by_market[market]
        at = int(np.searchsorted(days, day.toordinal(), side="right"))
        if at == 0 or day.toordinal() - int(days[at - 1]) > IMPLIED_STALE_DAYS:
            return None
        return float(sigmas[at - 1])

    @property
    def basis(self) -> str:
        """Item 9's one line: the conversion, any market read as percent, and the rows refused."""
        parts = ["Minneapolis Fed sd / sqrt(0.5)"]
        if self.percent:
            parts.append("read as percent: " + ", ".join(self.percent))
        if self.refused:
            parts.append(f"rows refused: {self.refused}")
        return "; ".join(parts)


def implied_releases(rows: list[dict[str, str]]) -> ImpliedReleases:
    """DD210 items 3 and 5 on the kept rows: two rows for one market and date refuse the file; an
    `sd` that is not finite or not positive refuses its row; a market whose median `sd` exceeds one
    is in percent; and σ = sd / √½."""
    seen: set[tuple[str, str]] = set()
    values: dict[str, list[tuple[int, float]]] = {}
    refused = 0
    for row in rows:
        key = (row["market"], row["date"])
        if key in seen:
            raise ImpliedUnreadable(f"{row['market']} has two rows dated {row['date']}")
        seen.add(key)
        try:
            sd = float(row["sd"])
        except ValueError:
            sd = math.nan
        if not math.isfinite(sd) or sd <= 0.0:
            refused += 1
            continue
        values.setdefault(row["market"], []).append((date.fromisoformat(row["date"]).toordinal(), sd))
    percent = tuple(sorted(m for m, pairs in values.items() if median(np.array([sd for _, sd in pairs])) > PERCENT_THRESHOLD))
    by_market = {}
    for market, pairs in values.items():
        pairs.sort()
        scale = (100.0 if market in percent else 1.0) * math.sqrt(IMPLIED_HORIZON_YEARS)
        by_market[market] = (np.array([d for d, _ in pairs]), np.array([sd / scale for _, sd in pairs]))
    return ImpliedReleases(by_market, percent, refused)


# --------------------------------------------------------------------------------------------
# The Fed's file after the read (DD243)
# --------------------------------------------------------------------------------------------

#: DD243 item 2: the horizon `implied_releases` assumes, in the months `maturity_target` counts.
IMPLIED_HORIZON_MONTHS = 6.0


def implied_rows_after_the_read(text: str, until: date) -> list[dict[str, str]]:
    """DD243 item 1, written 2026-09-29 after the read by the owner's decision. The header is the
    first line whose fields include `sd`, and every line before it is preamble and is dropped. DD210's
    rule then reads the rest unchanged, so a file with no preamble reads exactly as it would have.
    Each kept row also carries its `maturity_target` as it arrived, for item 2; the date column is
    found by DD210 item 5's own test."""
    lines = text.splitlines()
    at = next(
        (i for i, line in enumerate(lines) if "sd" in {f.strip() for f in next(csv.reader([line]), [])}),
        None,
    )
    if at is None:
        raise ImpliedUnreadable("no line whose fields include sd")
    body = "\n".join(lines[at:])
    rows = implied_rows(body, until)
    if "maturity_target" not in {f.strip() for f in next(csv.reader([lines[at]]), [])}:
        raise ImpliedUnreadable("no column named maturity_target")
    raw = list(csv.DictReader(body.splitlines()))
    header = [name for name in raw[0] if name]
    (day_column,) = [c for c in header if all(_release_day(row.get(c)) is not None for row in raw)]
    target = {
        ((row.get("market") or "").strip(), _release_day(row[day_column]).isoformat()): (
            row.get("maturity_target") or ""
        ).strip()
        for row in raw
    }
    return [{**row, "maturity_target": target.get((row["market"], row["date"]), "")} for row in rows]


def implied_releases_after_the_read(rows: list[dict[str, str]]) -> ImpliedReleases:
    """DD243 item 2. Each row's `sd` is taken to six months by its own target, sd × √(6/m), and
    DD210 items 3 and 5 then run unchanged, so σ = sd / √(m/12). A row whose target is not a
    positive number of months is refused and counted with item 5's refusals."""
    kept: list[dict[str, str]] = []
    refused = 0
    for row in rows:
        try:
            months = float(row["maturity_target"])
        except ValueError:
            months = math.nan
        if not math.isfinite(months) or months <= 0.0:
            refused += 1
            continue
        try:
            sd = float(row["sd"])
        except ValueError:
            kept.append(row)  # item 5 refuses it and counts it
            continue
        kept.append({**row, "sd": repr(sd * math.sqrt(IMPLIED_HORIZON_MONTHS / months))})
    releases = implied_releases(kept)
    return ImpliedReleases(releases.by_market, releases.percent, releases.refused + refused)


def after_the_read_basis(releases: ImpliedReleases) -> str:
    """DD243 item 5's `implied_basis`: what was read, labelled as read after the read."""
    parts = ["after the read (DD243): Minneapolis Fed sd / sqrt(m/12) at each row's maturity_target"]
    if releases.percent:
        parts.append("read as percent: " + ", ".join(releases.percent))
    if releases.refused:
        parts.append(f"rows refused: {releases.refused}")
    return "; ".join(parts)


# --------------------------------------------------------------------------------------------
# The structure engine (DD204): D18's menu, struck on a path and marked weekly
# --------------------------------------------------------------------------------------------


def ewma_volatility(changes: np.ndarray) -> float:
    """D8's zero-mean EWMA through the last change, weights normalised, annualised (DD204)."""
    changes = np.asarray(changes, dtype=float)
    ages = np.arange(len(changes) - 1, -1, -1, dtype=float)
    weights = (1.0 - EWMA_DECAY) * EWMA_DECAY**ages
    weights /= weights.sum()
    return math.sqrt(float(weights @ (changes * changes)) * SESSIONS)


def _price(model: Model, payoff: Payoff, forward: float, strike: float, tau: float, vol: float) -> float:
    if tau <= 0.0:
        if payoff is Payoff.CALL:
            return max(forward - strike, 0.0)
        return max(strike - forward, 0.0)
    call = payoff is Payoff.CALL
    if model is Model.GARMAN_KOHLHAGEN:
        return float(gk_value(call, forward, strike, tau, vol))
    if model is Model.BLACK76:
        return float(black76_value(call, forward, strike, tau, vol))
    return float(bachelier_value(call, forward, strike, tau, vol))


def _shift(model: Model, forward: float, vol: float, tau: float, sds: float) -> float:
    step = sds * vol * math.sqrt(tau)
    return forward + step if model is Model.BACHELIER else forward * math.exp(step)


def _solve(model: Model, forward: float, vol: float, tau: float, gap: Callable[[float], float]) -> float:
    return float(
        brentq(gap, _shift(model, forward, vol, tau, -20.0), _shift(model, forward, vol, tau, 20.0), xtol=1e-14, maxiter=500)
    )


def strike(name: str, exposure: Exposure, forward: float, vol: float, tau: float, multiple: float) -> tuple[StructureLeg, ...]:
    """DD193's structure on `exposure` at `tau` years, sized at `multiple` of the stated exposure,
    and put through D18's gate: a structure the gate refuses raises `Unsuitable` here.

    The one exception is `REFUSED`, DD211's 2:1 ratio forward, which is returned without the gate
    so that it can be marked beside H12a. It is never an alternative (`refused` says what the gate
    would do with it)."""
    model, protective, opposite = exposure.model, exposure.protective, exposure.opposite

    def value(payoff: Payoff, k: float) -> float:
        return _price(model, payoff, forward, k, tau, vol)

    if name == "forward":
        side = Side.BOUGHT if exposure.adverse > 0 else Side.SOLD
        legs = (StructureLeg(Payoff.FORWARD, side, multiple, forward),)
    elif name == "bought option":
        legs = (StructureLeg(protective, Side.BOUGHT, multiple, forward),)
    elif name == "zero-cost collar":
        bought = _shift(model, forward, vol, tau, exposure.adverse * COLLAR_OFFSET_SD)
        sold = _solve(model, forward, vol, tau, lambda k: value(opposite, k) - value(protective, bought))
        legs = (StructureLeg(protective, Side.BOUGHT, multiple, bought), StructureLeg(opposite, Side.SOLD, multiple, sold))
    elif name == "participating forward":
        one = _solve(model, forward, vol, tau, lambda k: value(protective, k) - PARTICIPATION * value(opposite, k))
        legs = (
            StructureLeg(protective, Side.BOUGHT, multiple, one),
            StructureLeg(opposite, Side.SOLD, PARTICIPATION * multiple, one),
        )
    elif name == REFUSED:
        one = _solve(model, forward, vol, tau, lambda k: value(protective, k) - RATIO * value(opposite, k))
        return (
            StructureLeg(protective, Side.BOUGHT, multiple, one),
            StructureLeg(opposite, Side.SOLD, RATIO * multiple, one),
        )
    else:
        raise ValueError(f"{name!r} is not a structure H12a compares")
    HedgeStructure(exposure, legs, worst_obligation(legs))
    return legs


def refused(exposure: Exposure, legs: tuple[StructureLeg, ...]) -> bool:
    """D18's gate on `legs`: whether it refuses to construct them (DD211 item 1)."""
    try:
        HedgeStructure(exposure, legs, worst_obligation(legs))
    except Unsuitable:
        return True
    return False


def _option_units(model: Model) -> float:
    """Dollars per dollar of stated exposure per unit of model value. Rates: the yield is quoted in
    percent and the stated flow is a year of interest, whatever the option's tenor. Currency and
    crude: moneyness, already a fraction of the notional."""
    return 0.01 if model is Model.BACHELIER else 1.0


def structure_pnl(
    name: str,
    exposure: Exposure,
    levels: np.ndarray,
    days: np.ndarray,
    vols: np.ndarray,
    multiple: float,
) -> np.ndarray:
    """The weekly P&L of `name`, in dollars, held on `exposure` along a path of weekly levels.

    `levels` is the factor as D17's regression reads it: the one-year yield as a decimal, or a log
    level (ln USD per unit; crude's cumulative roll-aware log return). `days` are calendar-day
    ordinals of the observations, and `vols` each observation's annualised volatility in the
    model's own units (normal, percent a year, for rates; lognormal otherwise).

    The forward is D17's linear leg: −multiple · N · sign · Δlevel, the Ederington hedge itself.
    Options are struck at the first observation and at every 26th after it, each settling at
    intrinsic on the 26th observation after its strike and marked at model value in between, with
    182 days less those elapsed as its tenor. A struck structure is worth nothing to the client at
    fair value, so buying one moves no P&L; the weekly P&L is the change in what it is worth.
    """
    levels, days, vols = (np.asarray(a, dtype=float) for a in (levels, days, vols))
    n = len(levels)
    if name == "forward":
        strike(name, exposure, float(levels[0]), float(vols[0]), TENOR_DAYS / 365.0, multiple)
        return -multiple * exposure.amount_usd * exposure.sign * np.diff(levels)
    model, units = exposure.model, _option_units(exposure.model)
    out = np.zeros(n - 1)
    start = 0
    while start < n - 1:
        end = min(start + TENOR_WEEKS, n - 1)
        if model is Model.BACHELIER:
            spot = lambda i: 100.0 * levels[i]  # noqa: E731 - the yield in percent
        else:
            base = levels[start]
            spot = lambda i, base=base: math.exp(levels[i] - base)  # noqa: E731 - moneyness
        legs = strike(name, exposure, spot(start), float(vols[start]), TENOR_DAYS / 365.0, multiple)

        def worth(i: int, legs=legs, start=start) -> float:
            tau = 0.0 if i - start >= TENOR_WEEKS else max(TENOR_DAYS - (days[i] - days[start]), 0.0) / 365.0
            total = 0.0
            for leg in legs:
                sign = 1.0 if leg.side is Side.BOUGHT else -1.0
                total += sign * leg.multiple * _price(model, leg.payoff, spot(i), leg.strike, tau, float(vols[i]))
            return total

        previous = worth(start)
        for i in range(start + 1, end + 1):
            now = worth(i)
            out[i - 1] = (now - previous) * units * exposure.amount_usd
            previous = now
        start = end
    return out


def simulate_capture(
    decay: float,
    r2: float,
    reps: int,
    seed: int = SEED,
    k: float = 0.6,
    vol: float = 0.10,
    n_in: int = 261,
    n_out: int = 482,
) -> tuple[float, float, float]:
    """H12a on synthetic firms (§6): the share whose in-sample hedge is resolved, the share of
    those the forward counts for, and the median capture ratio where one is defined.

    One currency leg on a lognormal path at `vol` a year, weekly. The firm's value moves k times
    the stated exposure's P&L in sample and `decay`·k times it out of sample, plus noise sized so
    the in-sample R² is `r2`. The hedge is the in-sample slope, cut to one by the gate, held; the
    structures are marked at the path's own volatility, so what differs between them is the
    structure and nothing else. "Resolved" is read here as the slope's normal 95% interval lying
    above zero, standing in for D17's bootstrap interval.
    """
    rng = np.random.default_rng(seed)
    exposure = Exposure(1, "synthetic", "currency", "EUR", 1, 1.0)
    weekly = vol / math.sqrt(52.0)
    noise = k * weekly * math.sqrt((1.0 - r2) / r2)
    days = np.arange(n_out + 1) * 7.0
    vols = np.full(n_out + 1, vol)
    resolved, counted, ratios = 0, 0, []
    for _ in range(reps):
        e_in = rng.standard_normal(n_in) * weekly
        y_in = k * e_in + rng.standard_normal(n_in) * noise
        xc = e_in - e_in.mean()
        slope = float(xc @ (y_in - y_in.mean()) / (xc @ xc))
        resid = y_in - y_in.mean() - slope * xc
        se = math.sqrt(float(resid @ resid) / (n_in - 2) / float(xc @ xc))
        path = np.concatenate([[0.0], np.cumsum(rng.standard_normal(n_out) * weekly)])
        y_out = decay * k * np.diff(path) + rng.standard_normal(n_out) * noise
        if slope - 1.96 * se <= 0.0:
            continue
        resolved += 1
        multiple = min(slope, 1.0)
        vr = {name: ederington(y_out, structure_pnl(name, exposure, path, days, vols, multiple)) for name in STRUCTURES}
        best = max(vr[name] for name in ALTERNATIVES)
        counted += captures(vr["forward"], best)
        if best > 0.0:
            ratios.append(vr["forward"] / best)
    return (
        resolved / reps,
        counted / resolved if resolved else float("nan"),
        median(np.array(ratios)) if ratios else float("nan"),
    )


def verdict_weeks(days: list[date]) -> list[int]:
    """DD201: indices of the weekly observations inside [OOS_START, VERDICT_END]. A return is
    scored iff both its observations are in the list, so no week straddles the construction."""
    return [i for i, day in enumerate(days) if OOS_START <= day <= VERDICT_END]
