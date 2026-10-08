"""The risk-model backtest's machinery. D14, registered in the joint pre-commit (DD134).

A risk model issues a VaR and an ES for tomorrow; the record says what happened. Every test here is
the published form:

- **Kupiec (1995)** proportion of failures, and **Christoffersen (1998)** independence and
  conditional coverage, on the exception sequence.
- The **Basel traffic light** at 99% over non-overlapping 250-day blocks.
- **Acerbi and Szekely (2014)** Z1 (ES given an exception) and Z2 (unconditional), with p-values
  simulated under the model the forecasts came from.
- **Fissler-Ziegel** consistency through the **FZ0** loss of Patton, Ziegel and Chen (2019), and
  **Diebold-Mariano** on its differences between two models.
- **Kupiec's power**, exact binomial, so the verdict is published beside what the test can see.

Losses are positive numbers throughout: a VaR of 1.2m means a loss larger than 1.2m is an exception.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np
from scipy import stats

from deskcraft.construction import _hac_prewhitened

__all__ = [
    "BASEL_ZONES",
    "Coverage",
    "EsTest",
    "acerbi_szekely",
    "christoffersen",
    "diebold_mariano",
    "ewma_sigma",
    "fz0_loss",
    "gaussian_forecasts",
    "kupiec",
    "kupiec_power",
    "traffic_light",
]

_NORMAL = NormalDist()

#: Basel's zones for 99% VaR over 250 days: green up to 4 exceptions, yellow 5-9, red 10 or more.
BASEL_ZONES = ((4, "GREEN"), (9, "YELLOW"), (250, "RED"))


def gaussian_forecasts(sigma: np.ndarray, level: float) -> tuple[np.ndarray, np.ndarray]:
    """Zero-mean Gaussian VaR and ES at `level`, as positive losses, from a daily sigma path."""
    z = _NORMAL.inv_cdf(level)
    es_scale = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi) / (1.0 - level)
    s = np.asarray(sigma, dtype=float)
    return z * s, es_scale * s


def ewma_sigma(pnl: np.ndarray, start_variance: float, decay: float = 0.94) -> np.ndarray:
    """The EWMA recursion walked forward: tomorrow's variance from today's P&L, nothing later."""
    out = np.empty(pnl.size)
    variance = start_variance
    for t, x in enumerate(pnl):
        out[t] = math.sqrt(variance)
        variance = decay * variance + (1.0 - decay) * x * x
    return out


@dataclass(frozen=True, slots=True)
class Coverage:
    observations: int
    exceptions: int
    expected: float
    kupiec_p: float
    independence_p: float
    conditional_p: float


def kupiec(hits: np.ndarray, rate: float) -> float:
    """Proportion-of-failures likelihood ratio, chi-squared(1) p-value."""
    h = np.asarray(hits, dtype=bool)
    return _kupiec_counts(h.size, int(h.sum()), rate)


def _kupiec_counts(t: int, x: int, rate: float) -> float:
    pi = x / t

    def ll(p: float) -> float:
        a = (t - x) * math.log(1.0 - p) if x < t else 0.0
        b = x * math.log(p) if x > 0 else 0.0
        return a + b

    lr = -2.0 * (ll(rate) - (ll(pi) if 0.0 < pi < 1.0 else 0.0))
    return float(stats.chi2.sf(max(lr, 0.0), 1))


def christoffersen(hits: np.ndarray, rate: float) -> Coverage:
    """Independence of exceptions (first-order Markov) and conditional coverage."""
    h = np.asarray(hits, dtype=int)
    prev, curr = h[:-1], h[1:]
    n00 = int(((prev == 0) & (curr == 0)).sum())
    n01 = int(((prev == 0) & (curr == 1)).sum())
    n10 = int(((prev == 1) & (curr == 0)).sum())
    n11 = int(((prev == 1) & (curr == 1)).sum())

    def term(n: int, p: float) -> float:
        return n * math.log(p) if n > 0 else 0.0

    p01 = n01 / (n00 + n01) if n00 + n01 else 0.0
    p11 = n11 / (n10 + n11) if n10 + n11 else 0.0
    p1 = (n01 + n11) / (n00 + n01 + n10 + n11)
    restricted = term(n00 + n10, 1.0 - p1) + term(n01 + n11, p1)
    unrestricted = term(n00, 1.0 - p01) + term(n01, p01) + term(n10, 1.0 - p11) + term(n11, p11)
    lr_ind = max(-2.0 * (restricted - unrestricted), 0.0)
    uc_p = kupiec(h, rate)
    lr_uc = float(stats.chi2.isf(uc_p, 1)) if uc_p > 0 else float("inf")
    return Coverage(
        observations=int(h.size),
        exceptions=int(h.sum()),
        expected=rate * h.size,
        kupiec_p=uc_p,
        independence_p=float(stats.chi2.sf(lr_ind, 1)),
        conditional_p=float(stats.chi2.sf(lr_uc + lr_ind, 2)),
    )


def traffic_light(hits: np.ndarray) -> tuple[str, ...]:
    """The Basel zone of each complete, non-overlapping 250-day block of 99% exceptions."""
    h = np.asarray(hits, dtype=bool)
    zones = []
    for start in range(0, h.size - 249, 250):
        count = int(h[start : start + 250].sum())
        zones.append(next(name for ceiling, name in BASEL_ZONES if count <= ceiling))
    return tuple(zones)


@dataclass(frozen=True, slots=True)
class EsTest:
    z1: float
    z1_p: float
    z2: float
    z2_p: float


def _z_statistics(x: np.ndarray, var: np.ndarray, es: np.ndarray, tail: float) -> tuple[np.ndarray, np.ndarray]:
    """Z1 and Z2 along the last axis of `x` (P&L), with VaR and ES as positive losses."""
    hits = x < -var
    count = hits.sum(axis=-1)
    weighted = np.where(hits, x / es, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        z1 = np.where(count > 0, weighted.sum(axis=-1) / np.maximum(count, 1) + 1.0, 0.0)
    z2 = weighted.sum(axis=-1) / (x.shape[-1] * tail) + 1.0
    return z1, z2


def acerbi_szekely(
    pnl: np.ndarray,
    sigma: np.ndarray,
    level: float,
    rng: np.random.Generator,
    simulations: int = 5000,
) -> EsTest:
    """Z1 and Z2 under a zero-mean Gaussian model with daily sigma `sigma`; one-sided p-values.

    A negative Z says the realised tail was worse than the model's ES. The p-value is the share of
    simulated Z below the realised one, the simulations drawn from the model itself.
    """
    var, es = gaussian_forecasts(sigma, level)
    tail = 1.0 - level
    z1, z2 = _z_statistics(np.asarray(pnl, dtype=float), var, es, tail)
    sims1, sims2 = [], []
    for start in range(0, simulations, 500):
        draw = rng.standard_normal((min(500, simulations - start), sigma.size)) * sigma
        a, b = _z_statistics(draw, var, es, tail)
        sims1.append(a)
        sims2.append(b)
    s1, s2 = np.concatenate(sims1), np.concatenate(sims2)
    return EsTest(float(z1), float((s1 <= z1).mean()), float(z2), float((s2 <= z2).mean()))


def fz0_loss(pnl: np.ndarray, var: np.ndarray, es: np.ndarray, level: float) -> np.ndarray:
    """Patton-Ziegel-Chen FZ0, daily, with VaR and ES as positive losses (so v = -VaR, e = -ES)."""
    y = np.asarray(pnl, dtype=float)
    v, e = -np.asarray(var, dtype=float), -np.asarray(es, dtype=float)
    tail = 1.0 - level
    hit = (y <= v).astype(float)
    return -hit * (v - y) / (tail * e) + v / e + np.log(-e) - 1.0


def diebold_mariano(loss_a: np.ndarray, loss_b: np.ndarray) -> tuple[float, float]:
    """Mean loss difference a - b and its two-sided p-value, HAC standard error."""
    d = np.asarray(loss_a, dtype=float) - np.asarray(loss_b, dtype=float)
    se = math.sqrt(float(_hac_prewhitened(d[:, None])[0, 0]) / d.size)
    z = d.mean() / se
    return float(d.mean()), float(2.0 * (1.0 - _NORMAL.cdf(abs(z))))


def kupiec_power(observations: int, rate: float, true_rate: float, alpha: float = 0.05) -> float:
    """Exact binomial power of Kupiec's test at level `alpha` against `true_rate`."""
    counts = np.array(
        [x for x in range(observations + 1) if _kupiec_counts(observations, x, rate) < alpha]
    )
    return float(stats.binom.pmf(counts, observations, true_rate).sum()) if counts.size else 0.0
