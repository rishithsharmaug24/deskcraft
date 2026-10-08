"""C153-C157. D11 -- sizing under the risk budget. `docs/PRECOMMIT_deskcraft_d11_sizing.md`.

The two linear programs agree with direct arithmetic (C153) and with a brute-force search (C154),
the benchmarks do what their names say (C155), every book is at one budget on one measure (C156),
and the measured table is pinned (C157).
"""

from __future__ import annotations

import numpy as np
import pytest

from deskcraft import sizing as sz
from deskcraft.attribution import levels_at
from deskcraft.factors import build_basis
from deskcraft.generator import select
from deskcraft.reference import US_CASH_BOOK
from deskcraft.views import REFERENCE_VIEW


@pytest.fixture(scope="module")
def sets() -> dict[str, sz.LegSet]:
    basis, levels = build_basis(), levels_at()
    headline = select(REFERENCE_VIEW, basis, levels).book("headline", "the headline cell")
    ten = select(REFERENCE_VIEW, basis, levels, move_bp=10.0).book("ten_bp", "a 10 bp view")
    return {
        "headline": sz.leg_set(headline, REFERENCE_VIEW, basis, sz.Unit.GROSS_DV01, levels),
        "ten_bp": sz.leg_set(ten, REFERENCE_VIEW, basis, sz.Unit.GROSS_DV01, levels),
        "us_cash": sz.leg_set(US_CASH_BOOK, REFERENCE_VIEW, basis, sz.Unit.STATED, levels),
    }


@pytest.fixture(scope="module")
def books(sets) -> dict[str, dict[sz.Rule, sz.SizedBook]]:
    return {name: sz.size_all(legs) for name, legs in sets.items()}


def test_c153_the_programs_agree_with_direct_arithmetic(sets) -> None:
    """C153. DD159. Each program's optimum is its objective recomputed on its own weights."""
    for legs in sets.values():
        w, value = sz._cvar_lp(legs, sz.ALPHA)
        assert value == pytest.approx(sz.tail_mean(-(legs.pnl @ w)), rel=1e-8)
        assert legs.view @ w == pytest.approx(1.0, rel=1e-9) and (w >= -1e-12).all()
        w, value = sz._cdar_lp(legs, sz.ALPHA)
        assert value == pytest.approx(sz.tail_mean(sz.drawdowns(legs.pnl @ w)), rel=1e-8)
    # The Acerbi-Tasche form, which is what the program minimises: 2,997 x 2.5% is 74.925.
    losses = np.arange(1.0, 101.0)
    assert sz.tail_mean(losses, 0.975) == pytest.approx((100 + 99 + 0.5 * 98) / 2.5)


def test_c154_no_grid_point_beats_the_program(sets) -> None:
    """C154. On the two-leg book, CVaR per unit view over a fine grid of the weight ratio."""
    legs = sets["headline"]
    _, optimum = sz._cvar_lp(legs, sz.ALPHA)
    best = np.inf
    for share in np.linspace(0.0, 1.0, 2001):
        w = np.array([share, 1.0 - share])
        exposure = float(legs.view @ w)
        if exposure <= 0.0:
            continue
        best = min(best, sz.tail_mean(-(legs.pnl @ (w / exposure))))
    assert optimum <= best + 1e-9
    assert best - optimum < 1e-3 * optimum, "the grid is fine enough to land near the optimum"


def test_c155_the_benchmarks_do_what_their_names_say(sets, books) -> None:
    """C155. DD160. ERC equalises; max-diversification's ratio exceeds 1; min-variance is least.

    P5: ERC gives the most volatile leg the smallest weight, on every set.
    """
    for name, legs in sets.items():
        erc = books[name][sz.Rule.EQUAL_RISK_CONTRIBUTION]
        assert np.allclose(erc.shares, 1.0 / len(legs.leg_ids), atol=1e-8), name
        vol = np.sqrt(np.diag(legs.covariance))
        assert int(np.argmax(vol)) == int(np.argmin(erc.weights)), name

        md = np.array(books[name][sz.Rule.MAX_DIVERSIFICATION].weights)
        ratio = float(md @ vol) / float(np.sqrt(md @ legs.covariance @ md))
        assert ratio > 1.0, name

        def variance_per_view(book: sz.SizedBook) -> float:
            w = np.array(book.weights) / book.view_exposure
            return float(w @ legs.covariance @ w)

        floor = variance_per_view(books[name][sz.Rule.MIN_VARIANCE])
        for rule, book in books[name].items():
            if book.view_exposure > 0.0:
                assert floor <= variance_per_view(book) * (1 + 1e-9), (name, rule)


def test_c156_one_budget_one_measure(books) -> None:
    """C156. DD158. Every book's Gaussian ES is the budget; nothing else is held equal."""
    for per_rule in books.values():
        for book in per_rule.values():
            assert book.gaussian_es == pytest.approx(sz.RISK_BUDGET_ES, rel=1e-12)
            assert sum(book.shares) == pytest.approx(1.0, rel=1e-10)


def test_c157_the_measured_table(sets, books) -> None:
    """C157. Weight shares and view exposure per unit budget, as measured on DEV."""
    shares = {
        (name, rule.name): tuple(round(x, 4) for x in book.weight_shares)
        for name, per_rule in books.items()
        for rule, book in per_rule.items()
    }
    assert shares[("headline", "CVAR_LP")] == (0.4403, 0.5597)
    assert shares[("headline", "MIN_VARIANCE")] == (0.4411, 0.5589)
    assert shares[("headline", "ONE_OVER_N")] == (0.5, 0.5)
    assert shares[("headline", "EQUAL_RISK_CONTRIBUTION")] == (0.3707, 0.6293)
    # P3 missed: the euro has no view exposure and still takes weight, because its small negative
    # correlation with the rates legs makes a little of it a hedge.
    assert shares[("us_cash", "CVAR_LP")] == (0.1766, 0.0722, 0.7113, 0.0399)
    assert shares[("us_cash", "MIN_VARIANCE")] == (0.2787, 0.073, 0.6346, 0.0137)
    views = {name: round(books[name][sz.Rule.CVAR_LP].view_exposure) for name in books}
    assert views == {"headline": 27_354, "ten_bp": 28_314, "us_cash": 37_230}
    ru, flat = books["headline"][sz.Rule.CVAR_LP], books["headline"][sz.Rule.ONE_OVER_N]
    assert round(sz.tracking_error(ru, flat, sets["headline"]), 4) == 0.2821
    assert sets["headline"].pnl.shape == (6_734, 2) and sets["us_cash"].pnl.shape == (2_997, 4)
