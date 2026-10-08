"""The effective number of bets, on three rungs. D10, decisions DD153-DD155, bars C147-C152.

**The statistic is a property of the basis**, which is curvecast item 28's finding and
`AMENDMENT_A3` DD94's reason for naming one. So every number here travels inside a `Ladder` that
carries all three rungs:

- **Roy-Vetterli** effective rank: the exp-entropy of the covariance's eigenvalue shares. The only
  rung that moves because the covariance's off-diagonal moved, and the one H4a and H8a are read on.
- **Volatility-preserving minimum torsion** (Meucci-Santangelo-Deguest): its factor variances
  are the marginal variances by an algebraic identity, so it is a statistic of the diagonal.
- **Plain whitening**: every factor variance is 1, so it returns the leg count exactly. It is
  the ladder's endpoint, and it is why H4b cannot fail.

A **book** enters as its leg P&L covariance, `E S E'`: D9's exposure matrix around D8's primary
covariance. Each leg is one asset of weight one, so the ladder is about the legs as held.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from deskcraft.attribution import leg_exposure, levels_at
from deskcraft.book import Book
from deskcraft.covariance import fit
from deskcraft.window import FitWindow

__all__ = [
    "Ladder",
    "effective_rank",
    "ladder",
    "leg_covariance",
    "min_torsion_variances",
]


def effective_rank(variances: np.ndarray) -> float:
    """Exponential entropy of a variance-share distribution -- Roy and Vetterli (2007).

    **A restatement of `curvecast.stage3.factor_space.effective_rank`**, line for line.
    """
    shares = np.asarray(variances, dtype=float)
    if shares.ndim != 1 or shares.size == 0:
        raise ValueError("effective_rank needs a non-empty one-dimensional array")
    if (shares < 0).any():
        raise ValueError("a variance share cannot be negative")
    total = shares.sum()
    if total <= 0:
        raise ValueError("effective_rank of an all-zero variance distribution is undefined")
    positive = shares[shares > 0] / total
    return float(np.exp(-(positive * np.log(positive)).sum()))


def _symmetric_inverse_sqrt(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    if (values <= 0).any():
        raise ValueError("the matrix is not positive definite")
    return vectors @ np.diag(1.0 / np.sqrt(values)) @ vectors.T


def min_torsion_variances(covariance: np.ndarray) -> tuple[np.ndarray, float]:
    """Factor variances under the volatility-preserving torsion, and the largest off-diagonal.

    The closed form item 28 uses: `diag(sd) @ inv(sqrtm(C)) @ diag(1 / sd)`, `C` the correlation.
    """
    deviations = np.sqrt(np.diag(covariance))
    correlation = covariance / np.outer(deviations, deviations)
    torsion = np.diag(deviations) @ _symmetric_inverse_sqrt(correlation) @ np.diag(1.0 / deviations)
    rotated = torsion @ covariance @ torsion.T
    off = float(np.abs(rotated - np.diag(np.diag(rotated))).max())
    return np.diag(rotated).copy(), off


@dataclass(frozen=True, slots=True)
class Ladder:
    """The three rungs on one covariance, with the basis of each named by its field."""

    names: tuple[str, ...]
    roy_vetterli: float
    min_torsion: float
    whitened: float
    #: Whether min-torsion's factor variances equal the marginal variances (item 28's identity).
    torsion_is_marginal: bool

    @property
    def count(self) -> int:
        return len(self.names)

    @property
    def per_leg(self) -> float:
        """H8b's statistic: Roy-Vetterli rank divided by the count."""
        return self.roy_vetterli / self.count


def ladder(covariance: np.ndarray, names: tuple[str, ...]) -> Ladder:
    """All three rungs on `covariance`, whose rows are `names`."""
    matrix = np.asarray(covariance, dtype=float)
    if matrix.shape != (len(names), len(names)):
        raise ValueError(f"a {matrix.shape} covariance cannot carry {len(names)} names")
    values = np.linalg.eigvalsh(matrix)
    torsion, _ = min_torsion_variances(matrix)
    whitening = _symmetric_inverse_sqrt(matrix)
    whitened = np.diag(whitening @ matrix @ whitening.T)
    return Ladder(
        names=names,
        roy_vetterli=effective_rank(np.clip(values, 0.0, None)),
        min_torsion=effective_rank(torsion),
        whitened=effective_rank(whitened),
        torsion_is_marginal=bool(np.allclose(torsion, np.diag(matrix), rtol=1e-9, atol=0.0)),
    )


def leg_covariance(
    book: Book,
    series: tuple[str, ...] | None = None,
    window: FitWindow | None = None,
) -> tuple[np.ndarray, tuple[str, ...]]:
    """The book's leg P&L covariance `E S E'`, and the series `S` was fitted over.

    `series` defaults to the book's own. Passing a wider set is DD154: two books compared on one
    covariance fitted over the union of their series.
    """
    levels = levels_at()
    exposures = [leg_exposure(leg, levels) for leg in book.legs]
    held = tuple(dict.fromkeys(s for e in exposures for s in e))
    universe = held if series is None else series
    missing = [s for s in held if s not in universe]
    if missing:
        raise ValueError(f"{book.book_id} holds {missing}, which the given series set omits")
    matrix = np.array([[e.get(s, 0.0) for s in universe] for e in exposures])
    sigma = fit(universe, window).array()
    return matrix @ sigma @ matrix.T, universe
