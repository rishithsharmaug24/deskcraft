"""C130-C138. D8 -- the covariance. `docs/PRECOMMIT_deskcraft_d8_covariance.md`.

The primary estimator is the object D6 already used (C130), every estimator takes a `FitWindow`
(C131), frequencies do not mix (C132), the robustness variants are what the pre-commit says they
are (C133-C135), the leg the grammar cannot say is measured (C136), X6's orientation run is held
as measured (C137), and the one source D8 regraded stays regraded (C138).
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from deskcraft import covariance as cv
from deskcraft.factors import NOMINAL_SERIES, _pca, fit_spectrum
from deskcraft.panel import load_daily
from deskcraft.sources import SOURCES, Derivation, Disposition, Licence
from deskcraft.window import FitWindow

#: `US_CASH_BOOK`'s five series: the three GSW zeros, the TIPS leg of the breakeven, and the euro.
BOOK_SERIES = ("SVENY02", "SVENY05", "SVENY10", "DFII5", "DEXUSEU")


def test_c130_the_primary_is_the_covariance_d6_already_used() -> None:
    """C130. DD141. Over the eight nominal zeros on DEV, `fit` is `factors._pca`'s matrix exactly."""
    _, sample, dropped = cv.changes(load_daily(FitWindow.dev()), NOMINAL_SERIES)
    primary = cv.fit(NOMINAL_SERIES)
    assert np.array_equal(primary.array(), _pca(sample)[2]), "a restatement at a tolerance is not one"
    assert (primary.observations, primary.dropped, dropped) == (6_734, 309, 309)
    assert primary.units == (cv.Unit.BASIS_POINTS,) * 8
    shares = fit_spectrum().cumulative_shares
    assert (round(shares[0] * 100, 4), round(shares[2] * 100, 4)) == (83.9352, 97.9021)


def test_c131_every_estimator_takes_a_fit_window() -> None:
    """C131. A raw date, a window past DEV, and a series with no unit row are refused."""
    with pytest.raises(TypeError, match="FitWindow"):
        cv.fit(NOMINAL_SERIES, date(2014, 12, 31))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="DEV_END"):
        FitWindow(date(2010, 1, 1), date(2015, 1, 2))
    with pytest.raises(cv.UnfittableSeries, match="no unit row"):
        cv.fit(("SVENY10", "DE_ZERO_10Y"))


def test_c132_one_frequency_per_covariance() -> None:
    """C132. DD130, X2. Daily refuses a monthly series by name; the monthly companion takes it."""
    with pytest.raises(cv.FrequencyRefused, match="Forward-filling"):
        cv.fit(("GZ_SPREAD", "SVENY10"))
    monthly = cv.fit_monthly(("GZ_SPREAD", "SVENY10"))
    assert monthly.frequency is cv.Frequency.MONTHLY
    assert monthly.observations == 322 and monthly.observations <= 323
    assert round(monthly.correlation("GZ_SPREAD", "SVENY10"), 4) == -0.3268


def test_c133_ledoit_wolf_is_unit_free() -> None:
    """C133. DD142. Intensity in [0, 1], variances kept, and a change of unit changes nothing else.

    **Mutation:** shrinking the raw (unstandardised) sample toward a scaled identity moves when
    one series changes unit, which is the defect DD142 was written against.
    """
    _, sample, _ = cv.changes(load_daily(FitWindow.dev()), BOOK_SERIES)
    shrunk, intensity = cv.ledoit_wolf(sample)
    assert 0.0 <= intensity <= 1.0
    centred = sample - sample.mean(axis=0)
    assert np.allclose(np.diag(shrunk), (centred**2).mean(axis=0), rtol=1e-12)

    k = np.ones(len(BOOK_SERIES))
    k[-1] = 100.0  # the euro in basis points of return instead of percent
    rescaled, intensity_k = cv.ledoit_wolf(sample * k)
    assert intensity_k == pytest.approx(intensity, rel=1e-12)
    assert np.allclose(rescaled, shrunk * np.outer(k, k), rtol=1e-10)

    def identity_target(x: np.ndarray, delta: float = 0.1) -> np.ndarray:
        s = np.cov(x - x.mean(axis=0), rowvar=False)
        return delta * np.trace(s) / s.shape[0] * np.eye(s.shape[0]) + (1 - delta) * s

    assert not np.allclose(identity_target(sample * k), identity_target(sample) * np.outer(k, k))


def test_c134_ewma_is_riskmetrics() -> None:
    """C134. DD143. Weights sum to one and decay by lambda; lambda is a constant, not a knob."""
    assert cv.EWMA_LAMBDA == {cv.Frequency.DAILY: 0.94, cv.Frequency.MONTHLY: 0.97}
    ones = np.ones((50, 1))
    assert cv._ewma(ones, 0.94)[0, 0] == pytest.approx(1.0, rel=1e-12)
    only_last = np.zeros((50, 1))
    only_last[-1, 0] = 1.0
    only_second = np.zeros((50, 1))
    only_second[-2, 0] = 1.0
    last = cv._ewma(only_last, 0.94)[0, 0]
    second = cv._ewma(only_second, 0.94)[0, 0]
    assert second / last == pytest.approx(0.94, rel=1e-12)


def test_c135_crisis_windows_are_the_nber_recessions_inside_dev() -> None:
    """C135. DD144. Three windows as dated; the book's set is refused where it is not observed."""
    assert [(c.name, c.window.start, c.window.end) for c in cv.CRISIS_WINDOWS] == [
        ("NBER_1990", date(1990, 7, 1), date(1991, 3, 31)),
        ("NBER_2001", date(2001, 3, 1), date(2001, 11, 30)),
        ("NBER_2007", date(2007, 12, 1), date(2009, 6, 30)),
    ]
    for crisis in cv.CRISIS_WINDOWS[:2]:
        with pytest.raises(cv.UnfittableSeries, match="0 jointly observed"):
            cv.fit_crisis(BOOK_SERIES, crisis)
    gfc = cv.fit_crisis(BOOK_SERIES, cv.CRISIS_WINDOWS[2])
    assert gfc.observations == 394
    # P4, as measured: the 2s10s correlation ROSE in the crisis window, against the prediction.
    dev = cv.fit(BOOK_SERIES)
    assert round(dev.correlation("SVENY02", "SVENY10"), 4) == 0.7446
    assert round(gfc.correlation("SVENY02", "SVENY10"), 4) == 0.7520


def test_c136_the_leg_the_grammar_cannot_say_is_measured() -> None:
    """C136. DD139, X22. The book's euro is in the covariance in percent; unreadable is refused."""
    book = cv.fit(BOOK_SERIES)
    assert book.units[-1] is cv.Unit.PERCENT_LOG_RETURN
    assert book.units[:-1] == (cv.Unit.BASIS_POINTS,) * 4
    assert (book.observations, book.dropped) == (2_997, 4_046)
    # P5: the euro's largest absolute correlation with the book's rate series is small.
    worst = max(abs(book.correlation("DEXUSEU", s)) for s in BOOK_SERIES[:4])
    assert round(worst, 4) == 0.1642 and worst < 0.31
    # P3: Ledoit-Wolf barely moves a sample this long.
    lw = cv.fit(BOOK_SERIES, method=cv.Method.LEDOIT_WOLF)
    assert lw.shrinkage is not None and lw.shrinkage < 0.05

    assert not SOURCES["VIXCLS"].readable
    cv.UNIT_OF["VIXCLS"] = cv.Unit.BASIS_POINTS  # give it a unit, so only readability can refuse
    try:
        with pytest.raises(cv.UnfittableSeries, match="not readable"):
            cv.fit(("SVENY10", "VIXCLS"))
    finally:
        del cv.UNIT_OF["VIXCLS"]


def test_c137_orientation_across_the_windows_d8_fits() -> None:
    """C137. X6, scored as the rider fixed it on 2026-09-22.

    (a) PC1 stable in every window: held. (b) PC2 flips in at least one: held, in NBER_1990,
    where curvecast's sign rule points +PC2 at a flattening. The window is short (184 changes),
    but NBER_2001 is as short (187) and did not flip, so length alone does not explain it. PC2
    and PC3 nearly tie there (9.65% against 8.62% of variance), which is the condition under which
    an eigenvector's orientation is least determined.
    """
    table = {(r.window, r.factor): (r.sessions, r.sign, r.crossings) for r in cv.orientation_by_window()}
    assert table == {
        ("DEV", "LEVEL"): (6_734, 1.0, 0),
        ("DEV", "SLOPE"): (6_734, 1.0, 1),
        ("DEV", "CURVATURE"): (6_734, 1.0, 2),
        ("NBER_1990", "LEVEL"): (184, 1.0, 0),
        ("NBER_1990", "SLOPE"): (184, -1.0, 1),
        ("NBER_1990", "CURVATURE"): (184, 1.0, 2),
        ("NBER_2001", "LEVEL"): (187, 1.0, 0),
        ("NBER_2001", "SLOPE"): (187, 1.0, 1),
        ("NBER_2001", "CURVATURE"): (187, 1.0, 2),
        ("NBER_2007", "LEVEL"): (394, 1.0, 0),
        ("NBER_2007", "SLOPE"): (394, 1.0, 1),
        ("NBER_2007", "CURVATURE"): (394, 1.0, 2),
    }


def test_c138_vixcls_is_graded_from_the_originator() -> None:
    """C138. X25. The notice is Cboe's words, the fallback's false premise is withdrawn."""
    row = SOURCES["VIXCLS"]
    assert row.notice is Licence.REDISTRIBUTION_PROHIBITED
    assert row.derivation is Derivation.PROHIBITED
    assert row.disposition is Disposition.REFUSED
    assert row.fallback is None and row.no_fallback_reason is not None
    assert "premise is false" in row.no_fallback_reason
