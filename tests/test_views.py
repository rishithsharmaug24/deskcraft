"""D6's bars: the basis is curvecast's, the signs are measured, and the fidelity can say no.

Thirteen bars. Three of them re-derive their subject from curvecast at test time rather than
trusting a constant here -- `C59` compares the two repositories' GSW bytes field by field,
`C60` executes curvecast's own `_pca` out of `factor_space.py`, and `C61` checks the fitted
spectrum against the numbers curvecast published for item 28. They **skip loudly** when
curvecast is absent, in `C31`'s shape.

`C60` is the whole of what "the DEV factor basis" can mean in a repository that cannot import
the package which fitted it. `curvecast` is not importable on this interpreter and
`factor_space.py` reaches `pit.seal` and `stage3.conditioning` at module level, so the
function node is parsed out, compiled alone and run. **Exact equality, not a tolerance** --
`C59` has already established that the inputs are the same bytes, so anything C60 finds is an
arithmetic disagreement, and a tolerance would let a different eigensolver pass as a
restatement.

`C62` is the bar that makes the three fitted names mean something. Eigenvalue rank alone would
happily call the third component "curvature"; the Litterman-Scheinkman shape test asks the
loadings, and a level factor crosses zero no times, a slope factor once and a curvature factor
twice.

`C69` exists because a fidelity statistic that cannot fail has not tested H3. It asks the same
book for a view it does not hold and requires the answer to be no.
"""

from __future__ import annotations

import ast
import csv
import math
from datetime import date

import numpy as np
import pytest

from deskcraft.factors import (
    CONTRAST_OF,
    FACTOR_SERIES,
    FITTED_FACTORS,
    NOMINAL_SERIES,
    Factor,
    build_basis,
    fit_spectrum,
    orient,
    sign_changes,
)
from deskcraft.panel import DAILY_FIXTURE, complete_cases, load_daily
from deskcraft.reference import US_CASH_BOOK
from deskcraft.registers import CLAIMS
from deskcraft.sensitivity import book_dv01
from deskcraft.views import (
    REFERENCE_VIEW,
    REFERENCE_VIEW_TWO_TERM,
    ViewTerm,
    UnreachableFactor,
    View,
    Move,
    book_exposure,
    compile_view,
    fidelity,
)
from deskcraft.window import FitWindow

from test_deskcraft_boundary import CURVECAST, REPO_ROOT
from upstream_certificate import GSW_BYTES, PCA_OUTPUT, digest

DOCS = REPO_ROOT / "docs"

#: curvecast's item-28 fixture, and the module that fitted the basis on it.
CURVECAST_FIXTURE = CURVECAST / "tests" / "fixtures" / "gsw_zero_dev.csv"
FACTOR_SPACE = CURVECAST / "src" / "curvecast" / "stage3" / "factor_space.py"

#: The same session D4's C55 pins, for the same reason: the last DEV date on which every
#: series `US_CASH_BOOK` needs is published. Fixed in D4's pre-commit before any of this.
MEASURED_ON = date(2014, 12, 24)

#: curvecast's published item-28 figures, quoted in `factor_space.py`'s own docstring and in
#: `BUILD_ORDER_D3_D16.md` section 1. Restated here so C61 compares rather than recomputes.
CURVECAST_SPECTRUM = {
    "changes": {"pc1": 83.9352, "pc1_3": 97.9021, "sessions": 6734},
    "levels": {"pc1": 95.9424, "pc1_3": 99.9064, "sessions": 6735},
}
COMPLETE_SESSIONS = 6735


@pytest.fixture(scope="module")
def spectrum():
    return fit_spectrum()


@pytest.fixture(scope="module")
def basis(spectrum):
    return build_basis(spectrum)


@pytest.fixture(scope="module")
def yields():
    panel = load_daily(FitWindow.dev())
    row = panel.dates.index(MEASURED_ON)
    return {
        series: panel.column(series)[row]
        for series in panel.series
        if panel.column(series)[row] is not None
    }


def _curvecast_function(name: str):
    """One function out of `factor_space.py`, compiled alone and run from its own bytes.

    D4's C50 mechanism. The module reaches `pit.seal` and `stage3.conditioning` at import
    time, so importing it would put curvecast's seal machinery into this process eight
    packages before the plan wants curvecast reachable at all.
    """
    tree = ast.parse(FACTOR_SPACE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            namespace: dict[str, object] = {"np": np}
            module = ast.Module(body=[node], type_ignores=[])
            exec(compile(module, str(FACTOR_SPACE), "exec"), namespace)
            return namespace[name]
    raise AssertionError(f"{name} is no longer a module-level function of factor_space.py")


def _gsw_columns(path):
    """The eight `SVENY` fields of a GSW-shaped CSV, keyed by date and left as written."""
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            row["Date"]: tuple(row[series] for series in NOMINAL_SERIES)
            for row in csv.DictReader(handle)
        }


# ---------------------------------------------------------------------------
# C59-C61: the basis is curvecast's, on the same bytes, and the arithmetic agrees
# ---------------------------------------------------------------------------


def test_the_two_repositories_hold_the_same_gsw_bytes() -> None:
    """C59. B59. DD59. Same rows, same blanks, same fields -- so C60 compares arithmetic only.

    Not "consistent" and not "overlapping". Field for field, including which sessions the
    source published nothing on, because a basis fitted here and one fitted there are only
    comparable if the sample is the same sample.

    **Off-machine the comparison is against the certificate** (DD69), and this is the bar that
    decided the certificate's shape: a snapshot made by copying curvecast's fixture would have
    this compare deskcraft's panel against a copy of deskcraft's panel -- 7,044 rows duplicated
    to assert nothing. What is certified is a digest of THIS side, taken on a date when the
    field-for-field comparison passed.
    """
    here = _gsw_columns(DAILY_FIXTURE)
    assert len(here) == 7044
    blank_here = sum(1 for row in here.values() if any(v in ("", "NA") for v in row))
    assert blank_here == 309
    assert digest(sorted(here.items())) == GSW_BYTES, (
        "this repository's GSW columns have left the bytes curvecast was compared against"
    )

    if not CURVECAST_FIXTURE.exists():
        return

    there = _gsw_columns(CURVECAST_FIXTURE)
    assert len(there) == 7044
    assert set(here) == set(there), "the two panels cover different sessions"
    differing = [stamp for stamp in here if here[stamp] != there[stamp]]
    assert differing == [], f"{len(differing)} sessions differ, first {differing[:3]}"

    blank_there = sum(1 for row in there.values() if any(v in ("", "NA", "ND") for v in row))
    assert blank_there == 309
    assert digest(sorted(there.items())) == GSW_BYTES, (
        "curvecast's fixture has moved; the certificate is stale and must be regenerated"
    )


def test_the_pca_restatement_reproduces_curvecasts_exactly() -> None:
    """C60. B60. DD59, DD60. Curvecast's own `_pca`, run from its own bytes. Exact equality.

    Not `allclose`. D4's C50 refused a tolerance for this shape of check because a tolerance
    would pass a reordered summation; here it would pass a different eigensolver, which is the
    same failure with a larger blast radius -- every loading, every orientation and every
    fidelity below inherits it.

    Run on two matrices: the real DEV sample, and a deterministic synthetic one whose columns
    are deliberately correlated, so the comparison is not resting on one input.

    **Off-machine the equality is against the certificate** (DD69) -- a digest of curvecast's
    own outputs for both matrices, taken through `<f8` so byte order is pinned rather than
    inherited from the host. Still exact, still not `allclose`, for the reason above.
    """
    from deskcraft.factors import _pca

    panel = load_daily(FitWindow.dev())
    kept, _ = complete_cases(panel, NOMINAL_SERIES)
    real = np.asarray(
        [[kept.column(s)[i] for s in NOMINAL_SERIES] for i in range(len(kept.dates))],
        dtype=float,
    )
    generator = np.random.default_rng(20260915)
    factors = generator.standard_normal((400, 3))
    synthetic = factors @ generator.standard_normal((3, 8)) + 0.1 * generator.standard_normal(
        (400, 8)
    )

    matrices = (("changes", np.diff(real, axis=0) * 100.0), ("synthetic", synthetic))

    blobs = []
    for _, matrix in matrices:
        result = _pca(matrix)
        for position in range(3):
            blobs.append(np.asarray(result[position], dtype="<f8").tobytes())
    assert digest(blobs) == PCA_OUTPUT, "the restatement has left the certified PCA output"

    if not FACTOR_SPACE.exists():
        return

    theirs = _curvecast_function("_pca")
    for name, matrix in matrices:
        mine = _pca(matrix)
        yours = theirs(matrix)
        for position, label in enumerate(("eigenvalues", "eigenvectors", "covariance")):
            assert np.array_equal(mine[position], yours[position]), f"{name}: {label} differ"


def test_the_spectrum_is_the_one_curvecast_published(spectrum) -> None:
    """C61. B61. DD61. Item 28's numbers, reproduced from deskcraft's own committed panel.

    `factor_space.py`'s docstring states 83.9352% and 97.9021% on changes and 95.9424% on
    levels; `BUILD_ORDER_D3_D16.md` section 1 quotes the three-factor figure as the reason H9
    predicts an early stop. Reproducing them here is what makes those citations checkable
    rather than inherited.

    The effective rank is computed by **curvecast's** `effective_rank`, not restated: it is
    D10's to own, and this bar only needs it as a cross-check.
    """
    assert spectrum.basis == "changes"
    assert spectrum.series == NOMINAL_SERIES
    assert spectrum.complete_sessions == COMPLETE_SESSIONS
    assert spectrum.sessions == CURVECAST_SPECTRUM["changes"]["sessions"]
    assert spectrum.window.start == FitWindow.dev().start
    assert spectrum.window.end == FitWindow.dev().end

    assert round(spectrum.variance_shares[0] * 100.0, 4) == CURVECAST_SPECTRUM["changes"]["pc1"]
    assert round(spectrum.cumulative_shares[2] * 100.0, 4) == CURVECAST_SPECTRUM["changes"]["pc1_3"]
    assert round(math.fsum(spectrum.variance_shares), 12) == 1.0

    levels = fit_spectrum(basis="levels")
    assert levels.sessions == CURVECAST_SPECTRUM["levels"]["sessions"]
    assert round(levels.variance_shares[0] * 100.0, 4) == CURVECAST_SPECTRUM["levels"]["pc1"]
    assert round(levels.cumulative_shares[2] * 100.0, 4) == CURVECAST_SPECTRUM["levels"]["pc1_3"]

    if FACTOR_SPACE.exists():
        effective_rank = _curvecast_function("effective_rank")
        measured = effective_rank(np.asarray(spectrum.eigenvalues, dtype=float))
        assert round(float(measured), 4) == 1.8231


# ---------------------------------------------------------------------------
# C62-C64: the names are earned, the signs are measured, the basis is not orthogonal
# ---------------------------------------------------------------------------


def test_the_three_fitted_factors_have_the_shape_their_names_claim(spectrum) -> None:
    """C62. B62. DD62. Litterman-Scheinkman by shape, not by eigenvalue rank.

    A level factor moves the whole curve one way and crosses zero no times; a slope factor
    crosses once; a curvature factor twice. Rank alone would call the third component
    "curvature" whatever it looked like, which is how a basis gets named rather than measured.
    """
    expected = {Factor.LEVEL: 0, Factor.SLOPE: 1, Factor.CURVATURE: 2}
    for factor, crossings in expected.items():
        loadings = spectrum.loading(FITTED_FACTORS[factor])
        assert len(loadings) == len(NOMINAL_SERIES)
        assert sign_changes(loadings) == crossings, (
            f"{factor} has {sign_changes(loadings)} sign changes across the grid, not "
            f"{crossings}; the name is not earned by the loadings"
        )
        assert round(math.fsum(value * value for value in loadings), 12) == 1.0

    assert sign_changes((1.0, 1.0, 1.0)) == 0
    assert sign_changes((-1.0, 1.0)) == 1
    assert sign_changes((1.0, 0.0, -1.0, 1.0)) == 2, "a zero is not a crossing on its own"


def test_orientation_is_measured_and_total(spectrum) -> None:
    """C63. B63. DD62. Every fitted factor's UP has a statistic behind it, and none is zero.

    The sign here is deliberately **not** the sign `_pca` produced: curvecast's rule normalises
    to the largest-magnitude element for diff stability and says so in its own comment, and
    which end of the grid holds that element is a property of the sample. A view language that
    read `+PC2` as a steepener would be exactly backwards on half of all samples.
    """
    orientations = orient(spectrum)
    assert set(orientations) == set(FITTED_FACTORS)

    for factor, orientation in orientations.items():
        assert orientation.factor is factor
        assert orientation.component == FITTED_FACTORS[factor]
        assert orientation.value != 0.0, f"{factor}'s orientation is undetermined"
        assert orientation.sign in (1.0, -1.0)
        assert math.copysign(1.0, orientation.value) == orientation.sign
        assert orientation.statistic and orientation.statement

    # Idempotent: orienting the already-oriented basis changes nothing.
    again = orient(spectrum)
    assert {f: o.sign for f, o in again.items()} == {f: o.sign for f, o in orientations.items()}


def test_the_basis_is_six_unit_directions_and_is_not_orthogonal(basis) -> None:
    """C64. B64. DD63, DD64. Unit norm, the stated contrasts as stated, and a live off-diagonal.

    The last assertion is the one that matters. `LEVEL` and `REAL_VS_NOMINAL` both put weight
    on `SVENY05/10/30`, and that overlap is true: a book long nominal duration and holding no
    TIPS does profit when breakevens widen because nominals sold off. Asserting it is non-zero
    is what stops a later reader treating these six loadings as a decomposition.
    """
    assert set(basis.vectors) == set(Factor)
    assert basis.series == FACTOR_SERIES

    for factor in Factor:
        vector = basis.vector(factor)
        assert len(vector) == len(FACTOR_SERIES)
        assert round(math.fsum(value * value for value in vector), 12) == 1.0

    for factor, contrast in CONTRAST_OF.items():
        named = dict(contrast)
        norm = math.sqrt(math.fsum(w * w for w in named.values()))
        for series in FACTOR_SERIES:
            assert basis.weight(factor, series) == pytest.approx(
                named.get(series, 0.0) / norm, abs=1e-15
            )

    for row in Factor:
        assert basis.gram[row][row] == pytest.approx(1.0, abs=1e-12)
        for column in Factor:
            assert basis.gram[row][column] == pytest.approx(basis.gram[column][row], abs=1e-15)

    overlap = basis.gram[Factor.LEVEL][Factor.REAL_VS_NOMINAL]
    assert overlap != 0.0, "the basis is being treated as orthogonal and it is not"
    assert abs(overlap) > 1e-6, f"LEVEL . REAL_VS_NOMINAL is {overlap}, effectively orthogonal"

    # The three fitted directions ARE mutually orthogonal -- they are eigenvectors.
    assert basis.gram[Factor.LEVEL][Factor.SLOPE] == pytest.approx(0.0, abs=1e-12)
    assert basis.gram[Factor.SLOPE][Factor.CURVATURE] == pytest.approx(0.0, abs=1e-12)


# ---------------------------------------------------------------------------
# C65-C67: the grammar, and the exposure it is read against
# ---------------------------------------------------------------------------


def test_the_grammar_is_closed(basis) -> None:
    """C65. B65. DD68. A view is non-empty, well-typed, and names no factor twice."""
    assert len(tuple(Factor)) == 6
    assert {f.value for f in Factor} == {
        "LEVEL",
        "SLOPE",
        "CURVATURE",
        "REAL_VS_NOMINAL",
        "CREDIT_VS_RATES",
        "CROSS_MARKET",
    }
    assert int(Move.UP) == 1 and int(Move.DOWN) == -1

    with pytest.raises(ValueError, match="states nothing"):
        View(())
    with pytest.raises(ValueError, match="twice"):
        View.of((Factor.LEVEL, Move.UP), (Factor.LEVEL, Move.DOWN))
    with pytest.raises(TypeError, match="must be a Factor"):
        ViewTerm("LEVEL", Move.UP)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="must be a Move"):
        ViewTerm(Factor.LEVEL, 1)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="holds a"):
        View((Factor.LEVEL,))  # type: ignore[arg-type]


def test_compiling_a_view_is_the_signed_sum_of_its_terms(basis) -> None:
    """C66. B66. DD68. Direction is a sign, so DOWN is exactly the negation of UP."""
    up = compile_view(View.of((Factor.LEVEL, Move.UP)), basis)
    down = compile_view(View.of((Factor.LEVEL, Move.DOWN)), basis)
    assert up.coordinates == {Factor.LEVEL: 1.0}
    assert down.coordinates == {Factor.LEVEL: -1.0}
    for a, b in zip(up.vector, down.vector):
        assert a == -b
    assert up.norm == pytest.approx(1.0, abs=1e-12)

    two = compile_view(REFERENCE_VIEW_TWO_TERM, basis)
    slope = compile_view(View.of((Factor.SLOPE, Move.UP)), basis)
    for position in range(len(basis.series)):
        assert two.vector[position] == pytest.approx(
            up.vector[position] + slope.vector[position], abs=1e-12
        )


def test_the_exposure_vector_is_d4s_dv01_and_nothing_else(yields) -> None:
    """C67. B67. DD63. Collapsed by series, to the cent, with no second sign convention.

    `RATE_SENSE_OF` already decided whether `LONG` means long the price or long the rate, so
    this function re-signs nothing. `eurusd` contributes no series at all -- `RateSense.NONE`
    returns no components -- which is why it is absent rather than zero.
    """
    exposure = book_exposure(US_CASH_BOOK, yields)
    assert exposure == pytest.approx(
        {
            "SVENY02": 40_000.00,
            "SVENY05": 25_000.00,
            "SVENY10": 60_000.00,
            "DFII5": -24_629.33,
        },
        abs=0.005,
    )
    assert "DEXUSEU" not in exposure, "a NONE-sense leg must contribute no series, not a zero"

    per_leg = book_dv01(US_CASH_BOOK, yields)
    rebuilt: dict[str, float] = {}
    for sensitivity in per_leg.values():
        for component in sensitivity.components:
            rebuilt[component.series] = rebuilt.get(component.series, 0.0) + component.dv01
    assert exposure == rebuilt

    assert round(exposure["SVENY05"] + exposure["DFII5"], 2) == 370.67


# ---------------------------------------------------------------------------
# C68-C71: H3, and the bar that lets it fail
# ---------------------------------------------------------------------------


def test_the_reference_book_loads_on_the_reference_views_factor(basis, yields) -> None:
    """C68. B68. **H3.** DD66, DD67. The claim this package is the registered scorer of.

    The view is `(LEVEL, UP)`, compiled from `REFERENCE_THESIS` in D6's pre-commit section
    DD66 before any loading existed. `loads_on_view` is dominance **and** sign: the view's
    factor carries the largest absolute loading of the six, and that loading's sign agrees
    with the direction the view states.
    """
    assert REFERENCE_VIEW.factors == (Factor.LEVEL,)
    assert REFERENCE_VIEW.move_of(Factor.LEVEL) is Move.UP

    result = fidelity(US_CASH_BOOK, REFERENCE_VIEW, basis, yields)
    assert result.book_id == "reference_us_cash"
    assert result.dominant is Factor.LEVEL
    assert result.loadings[Factor.LEVEL] > 0.0
    assert result.loads_on_view is True
    assert 0.0 < result.dominant_share <= 1.0
    assert result.cosine > 0.0

    # The alternative compilation of the same thesis, fixed at the same time (DD66).
    two = fidelity(US_CASH_BOOK, REFERENCE_VIEW_TWO_TERM, basis, yields)
    assert two.dominant is Factor.LEVEL
    assert two.loads_on_view is True


def test_the_fidelity_statistic_can_say_no(basis, yields) -> None:
    """C69. B69. DD67. A measure that cannot fail has not tested H3.

    Two ways of saying no, and both must work: a view on a factor the book barely touches, and
    a view stating the right factor in the wrong direction. The second is the one dominance
    alone would get wrong.
    """
    curvature = fidelity(
        US_CASH_BOOK, View.of((Factor.CURVATURE, Move.UP)), basis, yields
    )
    assert curvature.dominant is not Factor.CURVATURE
    assert curvature.loads_on_view is False

    backwards = fidelity(US_CASH_BOOK, View.of((Factor.LEVEL, Move.DOWN)), basis, yields)
    assert backwards.dominant is Factor.LEVEL
    assert backwards.loads_on_view is False, "dominance without sign is the claim backwards"
    assert backwards.cosine < 0.0


def test_a_view_the_book_cannot_reach_is_refused(basis, yields) -> None:
    """C70. B70. DD65. A structural zero is refused, a partial reach is reported.

    D4's DD55, one layer up: a shift naming a series no leg holds raises there, and a view
    naming a factor no leg reaches raises here. `CREDIT_VS_RATES` reaches only `GZ_SPREAD`,
    which no leg of `US_CASH_BOOK` holds, so a fidelity of zero would be indistinguishable
    from a book measured and found to carry no credit risk.
    """
    with pytest.raises(UnreachableFactor, match="GZ_SPREAD"):
        fidelity(US_CASH_BOOK, View.of((Factor.CREDIT_VS_RATES, Move.UP)), basis, yields)

    # Partial reach is not refusal: the book holds SVENY10, one side of the cross-market pair.
    cross = fidelity(
        US_CASH_BOOK, View.of((Factor.CROSS_MARKET, Move.UP)), basis, yields
    )
    assert cross.loadings[Factor.CROSS_MARKET] != 0.0
    assert Factor.CROSS_MARKET not in cross.unreachable
    assert Factor.CREDIT_VS_RATES in cross.unreachable
    assert cross.loadings[Factor.CREDIT_VS_RATES] == 0.0


def test_h3_carries_a_verdict_and_d6_is_its_scorer() -> None:
    """C71. B71. DD31. The first verdict this register has ever held.

    `registers.py` has said since D3a that *"the first package that sets one is D6, for H3, and
    its own suite is red from the moment its pre-commit document is written until it does"*.
    C34 enforces the iff in both directions; this bar pins the row itself, so a later edit that
    cleared the verdict would fail here by name rather than only as a closure mismatch.
    """
    h3 = next(claim for claim in CLAIMS if claim.claim_id == "H3")
    assert h3.scorer == "D6"
    assert h3.verdict is not None, "D6 has landed and H3 is unscored"
    assert list(DOCS.glob("PRECOMMIT_deskcraft_d6_*.md")), "D6's pre-commit document is missing"
    assert h3.verdict == h3.predicted, (
        f"H3 was predicted {h3.predicted} and scored {h3.verdict}; that is a legitimate "
        "outcome, and this assertion is the place it has to be acknowledged rather than "
        "absorbed silently"
    )
