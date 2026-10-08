"""C139-C146. D9 -- component ES under Euler, and the four flags.

`docs/PRECOMMIT_deskcraft_d9_component_risk.md`. Euler additivity is a unit test (C139), every leg
is measured including the euro (C140), the sub-additivity exhibit is exact and the DEV search is
held as measured (C141), the thresholds are the pre-registered constants (C142), the view split
partitions (C143), a declared neutrality carries its residual (C144), a half-reachable factor is
refused for selection (C145), and the headline numbers are pinned (C146).
"""

from __future__ import annotations

import numpy as np
import pytest

from deskcraft import attribution as at
from deskcraft.book import Book, Component, Currency, Direction, Instrument, InstrumentKind, Leg, Notional
from deskcraft.factors import Factor, build_basis
from deskcraft.generator import select
from deskcraft.reference import US_CASH_BOOK
from deskcraft.sensitivity import leg_sensitivity
from deskcraft.views import REFERENCE_VIEW, REFERENCE_VIEW_TWO_TERM, Move, UnreachableFactor, View


@pytest.fixture(scope="module")
def basis():
    return build_basis()


@pytest.fixture(scope="module")
def levels() -> dict[str, float]:
    return at.levels_at()


@pytest.fixture(scope="module")
def gaussian(basis, levels):
    return at.gaussian_risk(US_CASH_BOOK, REFERENCE_VIEW, basis, levels)


@pytest.fixture(scope="module")
def historical(basis, levels):
    return at.historical_risk(US_CASH_BOOK, REFERENCE_VIEW, basis, levels)


def _outright(symbol: str, series: str, direction: Direction, amount: float) -> Leg:
    instrument = Instrument(symbol, InstrumentKind.ZERO_YIELD, Currency.USD, float(series[-2:]),
                            (Component(series, 1.0, Currency.USD),))
    return Leg(symbol.lower(), instrument, direction, Notional(amount, Currency.USD))


def test_c139_components_sum_to_the_total(basis, levels, gaussian, historical) -> None:
    """C139. DD148. Euler additivity, both measures, on the book and on a synthetic book."""
    for report in (gaussian, historical):
        total = sum(leg.component for leg in report.legs)
        assert total == pytest.approx(report.es, rel=1e-10)
    synthetic = Book(
        book_id="synthetic_three",
        as_of=at.AS_OF,
        thesis="a synthetic book for the additivity bar",
        legs=(
            _outright("S02", "SVENY02", Direction.LONG, 3e7),
            _outright("S07", "SVENY07", Direction.SHORT, 5e7),
            _outright("S30", "SVENY30", Direction.LONG, 1e7),
        ),
    )
    for fn in (at.gaussian_risk, at.historical_risk):
        report = fn(synthetic, REFERENCE_VIEW, basis, levels)
        assert sum(leg.component for leg in report.legs) == pytest.approx(report.es, rel=1e-10)


def test_c140_every_leg_is_measured_including_the_euro(levels) -> None:
    """C140. DD147, DD139. Rate legs are D4's DV01 exactly; the euro is USD per 1%, not zero."""
    for leg in US_CASH_BOOK.legs:
        exposure = at.leg_exposure(leg, levels)
        assert exposure and any(value != 0.0 for value in exposure.values()), leg.leg_id
        if leg.leg_id != "eurusd":
            expected = {c.series: c.dv01 for c in leg_sensitivity(leg, levels).components}
            assert exposure == expected
    euro = at.leg_exposure(US_CASH_BOOK.legs[3], levels)
    assert levels["DEXUSEU"] == 1.2188
    assert euro == {"DEXUSEU": pytest.approx(-914_100.0, rel=1e-12)}


def test_c141_var_fails_sub_additivity_where_es_does_not(levels) -> None:
    """C141. The exhibit: exact on the textbook pair, and nothing found on the book's legs."""
    exhibit = at.textbook_exhibit()
    assert exhibit["var_single"] == 0.0 and exhibit["var_pair"] == 100.0
    assert exhibit["var_pair"] > 2 * exhibit["var_single"], "VaR is not sub-additive here"
    assert exhibit["es_single"] == pytest.approx(80.0, rel=1e-12)
    assert exhibit["es_pair"] == pytest.approx(101.6, rel=1e-12)
    assert exhibit["es_pair"] <= 2 * exhibit["es_single"], "ES is"
    # P6, as measured: linear legs on DEV changes, eleven sub-books, two levels, no violation.
    found = at.subadditivity_search(US_CASH_BOOK, levels)
    assert found == {"VAR": [], "ES": []}


def test_c142_the_flags_are_the_preregistered_thresholds(gaussian, historical) -> None:
    """C142. DD149. The constants, and what fires on `US_CASH_BOOK` under both measures."""
    assert (at.F1_DEAD_WEIGHT, at.F2_CONCENTRATION, at.F3_OFF_THESIS, at.F4_REDUNDANCY) == (
        0.05, 0.50, 0.25, 0.9,
    )
    for report in (gaussian, historical):
        assert report.screened == 4
        assert [(f.code, f.legs) for f in report.flags] == [
            ("F1", ("us_breakeven_5y",)),
            ("F3", ("eurusd",)),
        ]
    assert max(abs(v) for v in gaussian.partial_correlations.values()) == pytest.approx(0.7273, abs=1e-4)


def test_c143_the_view_split_partitions_each_component(basis, levels, gaussian, historical) -> None:
    """C143. DD150. On + off = component for every leg; the euro has no on-thesis part at all."""
    for report in (gaussian, historical):
        for leg in report.legs:
            assert leg.on_thesis + leg.off_thesis == pytest.approx(leg.component, rel=1e-12, abs=1e-6)
        assert report.leg("eurusd").on_thesis == 0.0
        assert report.leg("eurusd").off_thesis == report.leg("eurusd").component
    two = at.gaussian_risk(US_CASH_BOOK, REFERENCE_VIEW_TWO_TERM, basis, levels)
    assert two.es == gaussian.es, "the view moves the split, never the total"
    assert two.leg("us_2y").on_thesis != gaussian.leg("us_2y").on_thesis


def test_c144_a_declared_neutrality_carries_its_residual(gaussian) -> None:
    """C144. DD151, X17. D4's 370.67 per bp arrives on the risk report; the type is unchanged."""
    (declared,) = gaussian.neutralities
    assert declared.leg_id == "us_breakeven_5y"
    assert round(declared.residual_per_bp, 2) == 370.67
    assert round(declared.residual_share, 5) == 0.01483
    with pytest.raises(ValueError, match="outright position wearing two names"):
        Instrument("MATCHED", InstrumentKind.BREAKEVEN, Currency.USD, 5.0,
                   (Component("SVENY05", 1.0, Currency.USD), Component("DFII5", -1.0151, Currency.USD)),
                   neutrality=gaussian.neutralities[0].declared)


def test_c145_a_half_reachable_factor_is_refused_for_selection(basis, levels) -> None:
    """C145. DD152, X19. Named, both factors that reach outside the pool; the reference untouched."""
    for factor in (Factor.CROSS_MARKET, Factor.CREDIT_VS_RATES):
        with pytest.raises(UnreachableFactor, match=str(factor)):
            select(View.of((factor, Move.UP)), basis, levels)
    assert select(REFERENCE_VIEW, basis, levels).leg_ids == (
        "out_sveny30_short",
        "spr_sveny10_sveny30_short",
    )


def test_c146_the_headline_numbers(basis, levels, gaussian, historical) -> None:
    """C146. As measured on DEV, 2003-01-02 onward, at the 2014-12-24 levels."""
    assert gaussian.observations == historical.observations == 2_997
    assert round(gaussian.es) == 1_946_957 and round(historical.es) == 2_279_505
    assert historical.es / gaussian.es == pytest.approx(1.1708, abs=1e-4)
    shares = {leg.leg_id: round(leg.share, 4) for leg in gaussian.legs}
    assert shares == {"us_2y": 0.1723, "us_10y": 0.3089, "us_breakeven_5y": 0.0420, "eurusd": 0.4768}
    assert max(shares, key=shares.get) == "eurusd", "the leg the source called the diversifier"

    generated = select(REFERENCE_VIEW, basis, levels).book("generated", "the headline cell")
    report = at.gaussian_risk(generated, REFERENCE_VIEW, basis, levels)
    assert [(f.code, f.legs) for f in report.flags] == [
        ("F2", ("out_sveny30_short",)),
        ("F4", ("out_sveny30_short", "spr_sveny10_sveny30_short")),
    ]
    assert round(report.partial_correlations[generated.leg_ids], 4) == -0.9536
    assert np.isfinite(report.es)
