"""D5's bars on the deskcraft side: the front end is graded, and no leg moved onto it.

The measurement is curvecast's, committed there at `e78d2f7` with its own bars over the table.
What is here is what this repository owes in return, and none of it re-measures anything.

`test_book_types.py`'s `graded_universe()` already parses curvecast at test time, and C14 already
derives the priceable partition from it. Neither says **which** series are graded, and a count
cannot: `len(series) >= 34` is satisfied by any thirty-four strings. So C39 names the four, and
names one curvecast refused to measure so the bar cannot pass by the scan matching everything.

C40 is the bar with the least obvious teeth and the most need for them. C14 would stay green if
leg 1 were re-expressed on `DGS2` tomorrow, because `DGS2` is now inside the graded universe --
the guard that was watching for exactly that stopped watching the moment the measurement landed.
"""

from __future__ import annotations

from deskcraft.reference import DEFERRED_LEGS, REFERENCE_BOOK, US_CASH_BOOK
from deskcraft.sources import SOURCES, Licence

from test_book_types import graded_universe

#: The four curvecast's D5 measured. Written out here rather than derived, because this is the
#: claim being made and a claim derived from its own subject asserts nothing.
FRONT_END = ("DGS3MO", "DGS6MO", "DGS1", "DGS2")

#: A real FRED series, a plausible front-end substitute, and deliberately not measured upstream
#: (curvecast's `C521` asserts the refusal). That makes it a live control rather than a nonsense
#: string: if the scan started matching everything in the file, this is what would catch it.
NOT_GRADED = "DTB3"


def test_c39_the_front_end_the_steepener_needs_is_graded_upstream() -> None:
    """C39. B39, DD41. Four named series, not a count of thirty-four.

    The approved plan's M7 recorded that thirty series carried measured archive floors and that
    the four a steepener's short leg needs did not. This is the assertion that M7 is closed, and
    it is the only place in this repository that says so by name.

    Off-machine the universe comes from the certificate (DD69); the four names are asserted
    either way, which is the claim M7 closed.
    """
    universe = graded_universe()

    missing = [series for series in FRONT_END if series not in universe]
    assert not missing, f"D5 measured these upstream and they are not in the universe: {missing}"

    assert NOT_GRADED not in universe, (
        f"{NOT_GRADED} is in the graded universe and curvecast never measured it. Either the "
        "table gained a row nobody here knows about, or the AST scan has started matching "
        "strings that are not series ids -- and the second would make this bar pass vacuously"
    )

    floors = {name for name in universe if not name.startswith("SVENY")}
    assert len(floors) >= 34, f"only {len(floors)} archive floors; D5 left the table at 34"


def test_c40_no_leg_moved_onto_the_newly_graded_series() -> None:
    """C40. B40, DD40. A measurement landing is not a decision to re-express a leg.

    curvecast's D5 §2.1 forbids that package moving a leg, and this is where the refusal becomes
    executable rather than written down. **C14 cannot carry it**: C14 asks that every priceable
    leg's components lie inside the graded universe, and `DGS2` is now inside it, so leg 1 moving
    from `SVENY02` to `DGS2` would leave C14 green.

    The two are not interchangeable -- `SVENY02` is a zero yield off the pinned GSW file, `DGS2`
    a par constant maturity off H.15 -- so the substitution would move a number while looking
    like tidying. D7, the leg generator, is where that decision belongs and where this pin is
    expected to be revisited.
    """
    assert US_CASH_BOOK.leg_ids == ("us_2y", "us_10y", "us_breakeven_5y", "eurusd")
    assert tuple(DEFERRED_LEGS) == ("us_10y_call", "us_de_10y")

    two_year = REFERENCE_BOOK.leg("us_2y").instrument
    assert two_year.symbol == "US_ZERO_2Y"
    assert tuple(two_year.series) == ("SVENY02",)

    for leg in REFERENCE_BOOK.legs:
        reached = set(leg.instrument.series) & set(FRONT_END)
        assert not reached, (
            f"{leg.leg_id} reaches {sorted(reached)}, which D5 graded on 2026-09-12. A leg moving "
            "onto a series because a measurement landed is a decision for the package that "
            "builds legs, and it is not this one"
        )


def test_c41_every_series_d5_graded_is_public_domain_and_committable() -> None:
    """C41. B41, DD41. What a later leg would need is legal before that leg exists.

    D3a's register already carried these four, and the rule upstream (WP-L1) is that a fixture is
    committable **iff** its licence is public domain. A graded series whose licence forbade the
    fixture would be headroom that cannot be spent, so the two halves are checked together.
    """
    for series in FRONT_END:
        row = SOURCES[series]
        assert row.series == series
        assert row.fred_tag is Licence.PUBLIC_DOMAIN
        assert row.notice is Licence.PUBLIC_DOMAIN
        assert row.licence is Licence.PUBLIC_DOMAIN, (
            f"{series}'s operative licence is {row.licence.name}. The operative licence is the "
            "maximum of the tag and the notice, and a restricted one makes this headroom unusable"
        )
        assert row.committable
