"""The DEV factor basis: three fitted, three stated. D6, decisions DD59-DD65, bars C59-C64.

**The basis this module carries was not fitted here first, and the build-order row does not
say so.** §4's D6 row asks for a target vector *"in the DEV factor basis"* and no row in the
order fits one; `window.py` names it as one of three fitted objects and the other two are D8
and D12. What says where it comes from is older than the row -- `pyproject.toml` has recorded
since D1 that the engine's inputs are *"the objects curvecast item 28 produces"*, and that
deskcraft imports *"`curvecast.stage3.factor_space`"* by design. Item 28 is WP-R1, and it
fitted a PCA of the GSW zero curve on changes over DEV, on a grid of eight tenors that is the
first eight columns of this repository's own panel, in order.

So the arithmetic below is **curvecast's, restated** (DD59), in the shape D4 used for MEIP's
par-bond function: `_pca` is line for line, and C60 parses curvecast's own `_pca` out of
`factor_space.py`, executes it from its own bytes, and holds the two at **exact equality**.
That check is stronger here than it was at D4, because C59 first establishes that the two
repositories hold the same input bytes -- 7,044 rows, 309 blanks, zero differing fields -- so
what C60 compares is the arithmetic alone.

**numpy arrives with this module, and D4's reason for refusing it does not reach here**
(DD60). D4's arithmetic was four legs and six scalar formulas; this is a covariance and a
symmetric eigendecomposition over 6,734 x 8. A hand-rolled Jacobi rotation would agree with
LAPACK to about `1e-15`, which is exactly the objection: C50 refused a tolerance for this
shape of check, because *"a tolerance would pass a reordered summation, which is how a
restatement stops being one."* A restatement calling a different eigensolver is a second
implementation, and the bar holding it would have to be weakened to let it pass.

**A sign convention chosen for diff stability is not one that carries meaning** (DD62). The
restatement keeps curvecast's rule exactly -- normalise each eigenvector to its
largest-magnitude element -- and curvecast's comment says what that rule is for: *"an
arbitrary sign in a committed table is a diff that moves for no reason."* It is the right rule
for a committed table and it says nothing about steepening. Which end of the grid carries
PC2's largest element is a property of the sample, so a view language reading `+PC2` as a
steepener would state the opposite view on half of all samples and would do it silently.
`orient` is therefore a **separate, measured step**: each fitted factor carries a named
statistic, its measured value, and the sign that follows, so a reader can disagree with the
choice of statistic rather than with an unexplained minus.

**Three of the six terms are not on the nominal curve at all** (DD63). `REAL_VS_NOMINAL`
reaches `DFII5/10/30`, `CREDIT_VS_RATES` reaches `GZ_SPREAD` -- monthly, 323 observations --
and `CROSS_MARKET` reaches `DE_ZERO_10Y`, which is in no panel here. None is in the eight
columns the PCA is fitted on, so the eigenbasis cannot cover the grammar. They are **stated**
rather than fitted, at matched tenors, because a contrast between two curves is a definition
and calling it fitted would borrow credibility from an arithmetic that never touched it.

**Every factor is a direction of market movement, never a position that profits from one.**
That is what makes a loading an inner product with D4's signed DV01 vector, with the sign
convention applied once rather than twice: `RATE_SENSE_OF` already put the minus on a bond, so
the product of exposure and factor is P&L per basis point of that factor's move.

**The six are not orthogonal, and `FactorBasis.gram` is why that is safe** (DD64).
`REAL_VS_NOMINAL` and `CROSS_MARKET` both put weight on nominal series `LEVEL` also spans.
That overlap is true rather than untidy -- a book long nominal duration and holding no TIPS
does profit when breakevens widen because nominals sold off -- and orthogonalising would
delete a real exposure to make a table look cleaner. What it costs is that a loading here is
not a variance share, so the Gram matrix travels with the basis and C64 asserts the
off-diagonal is non-zero rather than letting a later reader assume it is not.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

import numpy as np

from deskcraft.panel import Panel, complete_cases, load_daily
from deskcraft.window import FitWindow

__all__ = [
    "CONTRAST_OF",
    "FACTOR_SERIES",
    "FITTED_FACTORS",
    "NOMINAL_SERIES",
    "ORIENTATION_OF",
    "REAL_SERIES",
    "STATED_FACTORS",
    "Factor",
    "FactorBasis",
    "NominalSpectrum",
    "Orientation",
    "UnorientedFactor",
    "build_basis",
    "fit_spectrum",
    "orient",
    "sign_changes",
]

#: curvecast's `TENOR_GRID`, restated: the whole-year members of MEIP's tenor list that GSW
#: publishes as a zero-coupon `SVENY` column. It is also `panel.DAILY_SERIES[:8]`, in order,
#: and C59 checks that the bytes behind the two are the same rather than trusting the overlap.
NOMINAL_SERIES: tuple[str, ...] = (
    "SVENY01",
    "SVENY02",
    "SVENY03",
    "SVENY05",
    "SVENY07",
    "SVENY10",
    "SVENY20",
    "SVENY30",
)

#: The TIPS real curve, at the three tenors H.15 publishes and the panel carries.
REAL_SERIES: tuple[str, ...] = ("DFII5", "DFII10", "DFII30")

#: The German ten-year zero `reference.py`'s declined cross-market leg names. Not in any panel
#: here and never to be: DD126 declines the foreign curve, and a factor may name a series no
#: data reaches because a factor is a direction and not an observation.
FOREIGN_SERIES: tuple[str, ...] = ("DE_ZERO_10Y",)

#: The credit leg, monthly, and a substitute construct (D3b, DD46).
CREDIT_SERIES: tuple[str, ...] = ("GZ_SPREAD",)

#: Every series any factor names, in a fixed order, so a vector is addressable by index.
FACTOR_SERIES: tuple[str, ...] = NOMINAL_SERIES + REAL_SERIES + CREDIT_SERIES + FOREIGN_SERIES


class Factor(StrEnum):
    """The closed grammar of §4's D6 row. Three are fitted and three are stated (DD63).

    A `Factor` is a **direction the market can move**, not a position. `LEVEL` is every
    nominal yield rising together; it is not "being long the level". The distinction is what
    lets a loading be a plain inner product with a signed DV01 vector.
    """

    #: PC1 of the nominal curve on changes. UP: every nominal yield rises.
    LEVEL = "LEVEL"
    #: PC2. UP: the long end rises against the short end -- a steepening.
    SLOPE = "SLOPE"
    #: PC3. UP: the wings rise against the belly.
    CURVATURE = "CURVATURE"
    #: Stated. UP: breakevens widen -- nominals rise against reals at matched tenors.
    REAL_VS_NOMINAL = "REAL_VS_NOMINAL"
    #: Stated. UP: credit widens against rates.
    CREDIT_VS_RATES = "CREDIT_VS_RATES"
    #: Stated. UP: the US cheapens against Germany at ten years.
    CROSS_MARKET = "CROSS_MARKET"


#: The three the PCA supplies, in eigenvalue order, mapped to the component each takes.
FITTED_FACTORS: dict[Factor, int] = {
    Factor.LEVEL: 0,
    Factor.SLOPE: 1,
    Factor.CURVATURE: 2,
}

#: The three defined rather than estimated, as signed series coefficients before normalisation
#: (DD63). Matched tenors throughout: an unmatched contrast is a duration bet wearing a
#: spread's name, which is precisely what D4 found one layer down in `US_BREAKEVEN_5Y`.
CONTRAST_OF: dict[Factor, tuple[tuple[str, float], ...]] = {
    Factor.REAL_VS_NOMINAL: (
        ("SVENY05", 1.0),
        ("SVENY10", 1.0),
        ("SVENY30", 1.0),
        ("DFII5", -1.0),
        ("DFII10", -1.0),
        ("DFII30", -1.0),
    ),
    # A spread series' own move *is* the contrast, so this one is a single unit coefficient
    # rather than a difference. Writing it as `+GZ_SPREAD - SVENY10` would subtract the rates
    # leg twice, since the Gilchrist-Zakrajsek construct is already a spread over Treasuries.
    Factor.CREDIT_VS_RATES: (("GZ_SPREAD", 1.0),),
    Factor.CROSS_MARKET: (("SVENY10", 1.0), ("DE_ZERO_10Y", -1.0)),
}

STATED_FACTORS: tuple[Factor, ...] = tuple(CONTRAST_OF)


class UnorientedFactor(ValueError):
    """A fitted factor whose orientation statistic came out at zero (DD62)."""


class _OrientationRule:
    """A named statistic over a loading vector whose sign decides which way `UP` points."""

    __slots__ = ("name", "statement", "_weights")

    def __init__(self, name: str, statement: str, weights: dict[str, float]) -> None:
        self.name = name
        self.statement = statement
        self._weights = weights

    def __call__(self, loadings: tuple[float, ...]) -> float:
        index = {series: position for position, series in enumerate(NOMINAL_SERIES)}
        return math.fsum(weight * loadings[index[series]] for series, weight in self._weights.items())


#: One rule per fitted factor (DD62). The statistic is a field on the result, so the choice is
#: arguable rather than implicit -- which is the whole difference between this and reading a
#: sign off `np.linalg.eigh`.
ORIENTATION_OF: dict[Factor, _OrientationRule] = {
    Factor.LEVEL: _OrientationRule(
        "sum of the eight loadings",
        "positive means every nominal yield rises together",
        dict.fromkeys(NOMINAL_SERIES, 1.0),
    ),
    Factor.SLOPE: _OrientationRule(
        "loading(SVENY30) - loading(SVENY01)",
        "positive means the long end rises against the short end -- a steepening",
        {"SVENY30": 1.0, "SVENY01": -1.0},
    ),
    Factor.CURVATURE: _OrientationRule(
        "loading(SVENY02) + loading(SVENY30) - 2 x loading(SVENY10)",
        "positive means the wings rise against the belly -- the 2s10s30s butterfly",
        {"SVENY02": 1.0, "SVENY30": 1.0, "SVENY10": -2.0},
    ),
}


def _pca(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Eigenvalues, eigenvectors and covariance, descending, sign-normalised.

    **A restatement of `curvecast.stage3.factor_space._pca`, line for line**, and C60 executes
    curvecast's own function out of `factor_space.py` to hold the two at exact equality rather
    than within a tolerance. It is restated rather than imported because `curvecast` is not
    importable on this repository's interpreter and `factor_space.py` reaches `pit.seal` and
    `stage3.conditioning` at module level -- the same condition `window.py` met with the DEV
    bounds and `sensitivity.py` met with MEIP's par bond, answered the same way each time.

    The sign rule is curvecast's and is kept **exactly**, comment and all, because changing it
    would break the equality C60 asserts. It is a diff-stability rule and carries no market
    meaning; `orient` is where meaning is attached, separately and with a statistic (DD62).
    """
    centred = matrix - matrix.mean(axis=0)
    covariance = np.cov(centred, rowvar=False)
    values, vectors = np.linalg.eigh(covariance)
    order = np.argsort(values)[::-1]
    values, vectors = values[order], vectors[:, order]
    for k in range(vectors.shape[1]):
        # Sign-normalise to the largest-magnitude element. An eigenvector's sign is arbitrary,
        # and an arbitrary sign in a committed table is a diff that moves for no reason.
        if vectors[int(np.argmax(np.abs(vectors[:, k]))), k] < 0:
            vectors[:, k] = -vectors[:, k]
    return values, vectors, covariance


@dataclass(frozen=True)
class NominalSpectrum:
    """A PCA of the nominal curve, carrying the sample and the basis it was fitted on.

    `basis` is a field for curvecast's D405 reason, restated: the same panel gives 83.9352%
    for PC1 on changes and 95.9424% on levels, and a spectrum that travels without saying
    which it is will eventually be quoted as the other one.
    """

    #: `"changes"` -- curvecast's pre-registered choice -- or `"levels"`, the contrast.
    basis: str
    series: tuple[str, ...]
    window: FitWindow
    #: Rows the statistics were computed from: one fewer than the complete-case panel on
    #: `"changes"`, because a difference costs the first session.
    sessions: int
    #: Complete-case rows the differences were taken over, before that loss.
    complete_sessions: int
    eigenvalues: tuple[float, ...]
    variance_shares: tuple[float, ...]
    cumulative_shares: tuple[float, ...]
    #: All eight components, each a per-series loading vector, in eigenvalue order.
    loadings: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        if self.basis not in ("changes", "levels"):
            raise ValueError(f"basis must be 'changes' or 'levels', not {self.basis!r}")

    def loading(self, component: int) -> tuple[float, ...]:
        return self.loadings[component]


def fit_spectrum(
    window: FitWindow | None = None, *, basis: str = "changes", panel: Panel | None = None
) -> NominalSpectrum:
    """Fit the nominal curve's spectrum on `window`, from this repository's committed panel.

    Defaults to the whole of DEV, which is DEC-1's pre-registered fit sample. `basis="changes"`
    is curvecast's pre-registered choice (DD61); `"levels"` is computable here so the contrast
    can be stated rather than cited.

    Differences are taken over **consecutive rows of the complete-case panel** and scaled to
    basis points, which is curvecast's treatment. The 309 holidays are dropped first, so a
    difference spanning a holiday spans it the way every difference already spans a weekend.
    """
    fit_window = FitWindow.dev() if window is None else window
    loaded = load_daily(fit_window) if panel is None else panel
    kept, _ = complete_cases(loaded, NOMINAL_SERIES)
    matrix = np.asarray(
        [[kept.column(series)[row] for series in NOMINAL_SERIES] for row in range(len(kept.dates))],
        dtype=float,
    )
    if basis == "changes":
        sample = np.diff(matrix, axis=0) * 100.0
    elif basis == "levels":
        sample = matrix
    else:
        raise ValueError(f"basis must be 'changes' or 'levels', not {basis!r}")

    values, vectors, _ = _pca(sample)
    shares = values / values.sum()
    return NominalSpectrum(
        basis=basis,
        series=NOMINAL_SERIES,
        window=fit_window,
        sessions=int(sample.shape[0]),
        complete_sessions=int(matrix.shape[0]),
        eigenvalues=tuple(float(value) for value in values),
        variance_shares=tuple(float(share) for share in shares),
        cumulative_shares=tuple(float(total) for total in np.cumsum(shares)),
        loadings=tuple(
            tuple(float(x) for x in vectors[:, k]) for k in range(vectors.shape[1])
        ),
    )


@dataclass(frozen=True, slots=True)
class Orientation:
    """Which way `UP` points for one fitted factor, and the statistic that decided it (DD62)."""

    factor: Factor
    component: int
    #: What was measured, in words, so the choice can be argued with.
    statistic: str
    #: What it means for that statistic to be positive.
    statement: str
    #: Its measured value on the fitted loadings, before any sign was applied.
    value: float
    #: `+1.0` where the fitted vector already points the stated way, `-1.0` where it is flipped.
    sign: float


def orient(spectrum: NominalSpectrum) -> dict[Factor, Orientation]:
    """Measure which way each fitted factor's `UP` points. Total over `FITTED_FACTORS`.

    A statistic of exactly zero raises rather than defaulting to `+1`: an undetermined sign is
    the one case where a default is a coin flip dressed as a convention, and DD18 set this
    repository's rule for that shape when it refused a default for `fx_hedged`.
    """
    out: dict[Factor, Orientation] = {}
    for factor, component in FITTED_FACTORS.items():
        rule = ORIENTATION_OF[factor]
        value = rule(spectrum.loading(component))
        if value == 0.0:
            raise UnorientedFactor(
                f"{factor}'s orientation statistic ({rule.name}) is exactly zero on this "
                "sample, so which way its UP points is undetermined. It is refused rather "
                "than defaulted: a sign chosen by a default here is a coin flip that every "
                "view compiled afterwards would inherit."
            )
        out[factor] = Orientation(
            factor=factor,
            component=component,
            statistic=rule.name,
            statement=rule.statement,
            value=value,
            sign=1.0 if value > 0.0 else -1.0,
        )
    return out


def sign_changes(vector: tuple[float, ...]) -> int:
    """How many times a loading vector crosses zero across the tenor grid.

    The Litterman-Scheinkman shape test: a level factor crosses none, a slope factor once and
    a curvature factor twice. C62 asserts all three, so the names `LEVEL`, `SLOPE` and
    `CURVATURE` are earned by the loadings rather than assigned by eigenvalue rank.
    """
    signs = [1 if value > 0.0 else -1 if value < 0.0 else 0 for value in vector]
    nonzero = [sign for sign in signs if sign != 0]
    return sum(1 for first, second in zip(nonzero, nonzero[1:]) if first != second)


def _unit(weights: dict[str, float]) -> tuple[float, ...]:
    vector = [weights.get(series, 0.0) for series in FACTOR_SERIES]
    norm = math.sqrt(math.fsum(value * value for value in vector))
    if norm == 0.0:
        raise ValueError("a factor direction cannot be the zero vector")
    return tuple(value / norm for value in vector)


@dataclass(frozen=True)
class FactorBasis:
    """Six named unit directions over `FACTOR_SERIES`, and the angles between them.

    **Not an orthogonal basis, and `gram` is what keeps that honest** (DD64). `LEVEL` and
    `REAL_VS_NOMINAL` both put weight on `SVENY05/10/30`, so a book's loadings here do not
    decompose its risk into shares -- they are six separate inner products, each the P&L per
    basis point of one named move. C64 asserts the off-diagonal is non-zero, because the way
    this decision turns into a defect is a later reader assuming it is not.
    """

    spectrum: NominalSpectrum
    orientations: dict[Factor, Orientation]
    series: tuple[str, ...]
    vectors: dict[Factor, tuple[float, ...]]
    #: Pairwise cosines, `Factor` by `Factor`. Symmetric, unit diagonal.
    gram: dict[Factor, dict[Factor, float]]

    def vector(self, factor: Factor) -> tuple[float, ...]:
        return self.vectors[factor]

    def weight(self, factor: Factor, series: str) -> float:
        """One factor's coefficient on one series, or `0.0` where it names none."""
        try:
            return self.vectors[factor][self.series.index(series)]
        except ValueError:
            return 0.0

    def reaches(self, factor: Factor) -> tuple[str, ...]:
        """The series this factor puts non-zero weight on."""
        vector = self.vectors[factor]
        return tuple(name for name, value in zip(self.series, vector) if value != 0.0)


def build_basis(spectrum: NominalSpectrum | None = None) -> FactorBasis:
    """The six directions: three from the spectrum, oriented; three stated (DD63).

    Fitting is the expensive half and is done once here; `views.fidelity` takes the basis
    rather than refitting, so two fidelities read against one measurement instead of two.
    """
    fitted = fit_spectrum() if spectrum is None else spectrum
    orientations = orient(fitted)

    vectors: dict[Factor, tuple[float, ...]] = {}
    for factor, orientation in orientations.items():
        loadings = fitted.loading(orientation.component)
        vectors[factor] = _unit(
            {
                series: orientation.sign * value
                for series, value in zip(NOMINAL_SERIES, loadings)
            }
        )
    for factor, contrast in CONTRAST_OF.items():
        vectors[factor] = _unit(dict(contrast))

    order = tuple(Factor)
    gram = {
        row: {
            column: math.fsum(a * b for a, b in zip(vectors[row], vectors[column]))
            for column in order
        }
        for row in order
    }
    return FactorBasis(
        spectrum=fitted,
        orientations=orientations,
        series=FACTOR_SERIES,
        vectors={factor: vectors[factor] for factor in order},
        gram=gram,
    )
