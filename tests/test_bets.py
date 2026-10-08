"""C147-C152. D10 -- the effective number of bets. `docs/PRECOMMIT_deskcraft_d10_effective_bets.md`.

The ladder restates curvecast item 28 (C147), scores H4a (C148), H4b and the reason its PASS carries
no information (C149), H8a (C150), H8b under DD153's new verdict (C151), and reports every other
cell without a verdict (C152).
"""

from __future__ import annotations

import numpy as np
import pytest

from deskcraft import bets
from deskcraft import covariance as cv
from deskcraft.attribution import levels_at
from deskcraft.factors import NOMINAL_SERIES, build_basis
from deskcraft.generator import select, selection_ladder
from deskcraft.reference import US_CASH_BOOK
from deskcraft.registers import CLAIMS, Claim, Verdict
from deskcraft.views import REFERENCE_VIEW

#: DD154: both books' series, so the comparison is on one covariance.
UNION = ("SVENY02", "SVENY10", "SVENY05", "DFII5", "DEXUSEU", "SVENY30")


@pytest.fixture(scope="module")
def basis():
    return build_basis()


@pytest.fixture(scope="module")
def generated(basis):
    return select(REFERENCE_VIEW, basis, levels_at()).book("generated_headline", "the headline cell")


def _claim(claim_id: str) -> Claim:
    return next(claim for claim in CLAIMS if claim.claim_id == claim_id)


def _with_union(book) -> tuple[str, ...]:
    """DD154's covariance widened by whatever a ladder cell's book also holds."""
    held = [c.series for leg in book.legs for c in leg.instrument.components]
    return tuple(dict.fromkeys((*UNION, *held)))


def _ladder(book, series=UNION) -> bets.Ladder:
    covariance, _ = bets.leg_covariance(book, series)
    return bets.ladder(covariance, book.leg_ids)


def test_c147_the_ladder_restates_item_28() -> None:
    """C147. On D8's DEV covariance of the eight zeros: 1.8231 / 7.9059 / 8.0000."""
    ladder = bets.ladder(cv.fit(NOMINAL_SERIES).array(), NOMINAL_SERIES)
    assert (round(ladder.roy_vetterli, 4), round(ladder.min_torsion, 4), round(ladder.whitened, 4)) == (
        1.8231, 7.9059, 8.0,
    )
    assert ladder.torsion_is_marginal, "min-torsion is the marginal variances, by identity"


def test_c148_h4a_the_hand_built_book_is_under_three_bets() -> None:
    """C148. H4a, scored PASS: Roy-Vetterli rank 2.4103 on the four legs, 75% of max is 3.0."""
    ladder = _ladder(US_CASH_BOOK)
    assert round(ladder.roy_vetterli, 4) == 2.4103 and ladder.roy_vetterli < 3.0
    # DD154 costs nothing here: the union covariance and the book's own give the same rank.
    own, _ = bets.leg_covariance(US_CASH_BOOK)
    assert bets.ladder(own, US_CASH_BOOK.leg_ids).roy_vetterli == pytest.approx(ladder.roy_vetterli, rel=1e-12)
    assert _claim("H4a").verdict is Verdict.PASS


def test_c149_h4b_passes_on_a_rung_that_cannot_move() -> None:
    """C149. H4b, scored PASS as written, and the whitening identity that makes the PASS empty.

    Whitening returns the leg count for any covariance, so "above 3.0 on at least one other rung"
    holds for every four-leg book. Min-torsion, the rung that can move, is 2.6567 -- below 3.0.
    """
    ladder = _ladder(US_CASH_BOOK)
    assert ladder.whitened == pytest.approx(4.0, rel=1e-12)
    assert round(ladder.min_torsion, 4) == 2.6567 and ladder.min_torsion < 3.0
    rng = np.random.default_rng(0)
    for n in (3, 4):
        a = rng.standard_normal((200, n)) @ rng.standard_normal((n, n))
        assert bets.ladder(np.cov(a, rowvar=False), tuple(f"x{i}" for i in range(n))).whitened == pytest.approx(n)
    assert _claim("H4b").verdict is Verdict.PASS


def test_c150_h8a_the_generated_book_does_not_beat_the_hand_built_one(generated) -> None:
    """C150. H8a, scored against its prediction, on DD154's one covariance at D7b's headline cell."""
    assert generated.leg_ids == ("out_sveny30_short", "spr_sveny10_sveny30_short")
    hand, gen = _ladder(US_CASH_BOOK), _ladder(generated)
    assert round(gen.roy_vetterli, 4) == 1.0898 and round(hand.roy_vetterli, 4) == 2.4103
    assert gen.roy_vetterli < hand.roy_vetterli
    assert _claim("H8a").predicted is Verdict.PASS and _claim("H8a").verdict is Verdict.FAIL


def test_c151_a_claim_with_no_prediction_is_reported(generated) -> None:
    """C151. DD153. REPORTED only where nothing was predicted; H8b's ratios as reported."""
    assert _claim("H8b").predicted is None and _claim("H8b").verdict is Verdict.REPORTED
    with pytest.raises(ValueError, match="DD153"):
        Claim("H99", "a predicted claim", "D10", Verdict.PASS, verdict=Verdict.REPORTED)
    with pytest.raises(ValueError, match="DD153"):
        Claim("H98", "an unpredicted claim", "D10", None, verdict=Verdict.PASS)
    assert round(_ladder(US_CASH_BOOK).per_leg, 4) == 0.6026
    assert round(_ladder(generated).per_leg, 4) == 0.5449


def test_c152_every_other_cell_reported_without_a_verdict(basis) -> None:
    """C152. DD155. The seven cells beside the headline, and a 10 bp book, as measured."""
    levels = levels_at()
    measured = {}
    for selection in selection_ladder(REFERENCE_VIEW, basis, levels).cells:
        key = (selection.cell.convention.name, selection.cell.multiplier)
        if not selection.additions:
            measured[key] = None
            continue
        book = selection.book("cell", "a ladder cell")
        measured[key] = round(_ladder(book, _with_union(book)).roy_vetterli, 4)
    assert measured == {
        ("AS_QUOTED", 0.5): 1.0898, ("AS_QUOTED", 1.0): 1.0898,
        ("AS_QUOTED", 2.0): 1.0, ("AS_QUOTED", 4.0): None,
        ("PAR_PROXY", 0.5): 1.5312, ("PAR_PROXY", 1.0): 1.0,
        ("PAR_PROXY", 2.0): 1.0, ("PAR_PROXY", 4.0): None,
    }
    ten = select(REFERENCE_VIEW, basis, levels, move_bp=10.0).book("ten_bp", "a 10 bp view")
    ladder = _ladder(ten, _with_union(ten))
    assert len(ten.legs) == 6 and round(ladder.roy_vetterli, 4) == 1.3155

    # DD154 is not a formality. The same headline book on its own two series, whose complete-case
    # sample runs from 1988 rather than 2003, ranks 1.111 instead of 1.0898.
    headline = select(REFERENCE_VIEW, basis, levels).book("headline", "the headline cell")
    own = tuple(dict.fromkeys(c.series for leg in headline.legs for c in leg.instrument.components))
    assert round(_ladder(headline, own).roy_vetterli, 4) == 1.111
