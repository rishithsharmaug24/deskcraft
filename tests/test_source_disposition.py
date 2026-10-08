"""C122-C124. DD118's three-way sort, expressed by the type instead of by a document.

X22 named the defect and named what closes it: *"either a `readable` predicate and a term for
the no-derivatives condition, or a written argument that the three dispositions collapse to
two."* `RIDER_the_fifth_verdict.md` takes the first branch as **DD136**. These bars hold it.

The three are deliberately different in kind. C122 holds the **type** -- that the vocabulary
exists and that the two axes cannot contradict each other. C123 holds the **register** -- that
every row is graded on both axes and that the middle cell holds exactly what it should, which
since DD137 is nothing. C124 holds the **guarantee DD35 was built for** -- that widening what may be
read did not widen what may be shipped, which is the one way this change could go wrong.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from deskcraft.sources import (
    ADMITTED,
    SOURCE_ROWS,
    Derivation,
    Disposition,
    Licence,
    Source,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def test_a_licence_and_a_derivation_are_two_axes_that_cannot_contradict() -> None:
    """C122. The vocabulary exists, is ordered, and public domain cannot forbid derivation."""
    # The term X22 said was missing, by name and not by position.
    assert Derivation.RESULTS_ONLY in Derivation
    assert Derivation.UNMEASURED == max(Derivation), (
        "unread must be strictest, for DD34's reason: a default here would hand the widest "
        "permission to the least evidence"
    )
    assert set(Disposition) == {
        Disposition.COMMITTABLE,
        Disposition.USABLE_NOT_COMMITTABLE,
        Disposition.REFUSED,
    }, "DD118 sorts three ways; a fourth cell is a decision nobody took"

    # The invariant. A public-domain row carries no condition at all, so it cannot restrict
    # derivation -- and a row that claimed both would make `disposition` incoherent.
    for row in SOURCE_ROWS:
        if row.licence is Licence.PUBLIC_DOMAIN:
            assert row.derivation is Derivation.PERMITTED, row.series
        if row.committable:
            assert row.readable, f"{row.series}: committable implies readable, or the sort lies"

    # And the constructor refuses the contradiction rather than leaving it to a reader.
    with pytest.raises(ValueError, match="cannot restrict"):
        Source(
            series="IMPOSSIBLE",
            originator="x",
            originator_class=SOURCE_ROWS[0].originator_class,
            publisher="x",
            fred_tag=None,
            notice=Licence.PUBLIC_DOMAIN,
            derivation=Derivation.PROHIBITED,
            evidence="x",
            fallback=None,
            fallback_originator=None,
            no_fallback_reason="x",
        )


def test_every_row_is_graded_on_both_axes_and_the_middle_cell_is_accounted_for() -> None:
    """C123. Every row answers the new question, and the middle cell holds what it should.

    It should hold nothing today. See the assertion below -- DD137 emptied it hours after
    DD136 built it, and a bar that asserted occupancy would now be asserting a wish.
    """
    assert SOURCE_ROWS, "an empty register would pass every assertion below"
    for row in SOURCE_ROWS:
        assert isinstance(row.derivation, Derivation), row.series
        assert isinstance(row.disposition, Disposition), row.series

    middle = [r.series for r in SOURCE_ROWS if r.disposition is Disposition.USABLE_NOT_COMMITTABLE]
    assert middle == [], (
        "**The middle cell is empty, and that is DD137's doing, not a regression.** When DD136 "
        "built the cell on the morning of 2026-09-23 it held exactly one row, `T10YIE`. The "
        "owner admitted that row to committed fixtures the same day (DD137), so it moved to "
        "COMMITTABLE and the cell emptied within hours of existing. The cell is still the "
        "mechanism -- it is what `readable` returns for a row that is graded and not admitted, "
        "and it is the route for the JGB curve, FR 2004B and the euro leg when a package pays "
        "to grade them. But it is unoccupied today and pretending otherwise would be the "
        f"exact self-flattery this register refuses. Got {middle}"
    )

    # Cboe stays refused, and on the derivation axis specifically. DD118's own table says so,
    # and the temptation this bar exists to refuse is reading the fifth verdict as a route to
    # the vol surface. It is not.
    vixcls = next(r for r in SOURCE_ROWS if r.series == "VIXCLS")
    assert vixcls.derivation is Derivation.PROHIBITED
    assert vixcls.disposition is Disposition.REFUSED
    assert not vixcls.readable


def test_widening_what_may_be_read_did_not_widen_what_may_be_shipped() -> None:
    """C124. DD35's guarantee, which DD136 kept and DD137 gave up for three named rows.

    **This bar's subject changed on the day it was written, and the change is the record.**
    C124 was built in the morning of 2026-09-23 to hold that widening what may be *read* had
    not widened what may be *shipped*. That still holds: DD136 moved nothing into a fixture.
    What moved was DD137, an owner decision the same afternoon, and it is a different act --
    a deliberate, named, written surrender of the guarantee for `T10YIE`, `BAA10Y`, `AAA10Y`.

    So the bar now holds the finer statement, which is the one that stays true: the guarantee
    is intact **except where the owner spent it by name**, and `sendable_free` still answers
    DD35's original question for every row so a future strip-and-send knows what to remove.
    """
    for row in SOURCE_ROWS:
        assert row.sendable_free == (row.licence is Licence.PUBLIC_DOMAIN), row.series
        if not row.sendable_free and row.committable:
            assert row.series in ADMITTED, (
                f"{row.series} may be committed, does not travel free, and no owner admission "
                "names it. That is the guarantee leaking rather than being spent."
            )
        if row.disposition is Disposition.USABLE_NOT_COMMITTABLE:
            assert not row.committable, (
                f"{row.series}: the middle cell exists precisely to NOT be committable"
            )

    # And the tree agrees: no committed fixture names a series this register will not commit.
    graded = {r.series: r for r in SOURCE_ROWS}
    offenders: list[str] = []
    panels = sorted(FIXTURES.glob("*.csv"))
    assert panels, "no fixture found, so the sweep below would pass by looking at nothing"
    for panel in panels:
        with panel.open(newline="", encoding="utf-8") as fh:
            header = next(csv.reader(fh), [])
        for column in header:
            row = graded.get(column.strip())
            if row is not None and not row.committable:
                offenders.append(f"{panel.name}: column {column!r} is {row.disposition}")
    assert not offenders, (
        "a fixture carries a series the register refuses to commit, which is the exact failure "
        "DD35 exists to prevent: " + "; ".join(offenders)
    )
