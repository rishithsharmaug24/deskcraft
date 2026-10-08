"""C125-C127. DD137 -- the credit tier admitted, and the guarantee that went with it.

DD35 protected one property: every byte here travels to anyone without a condition. The owner
lifted it for three named series on 2026-09-23, on the reasoning that DD35's own premise -- *a
repository that is then sent anywhere* -- had stopped being true. The reasoning is sound. The
consequence is that the property is gone, and a property that quietly stops holding is worse
than one that was never claimed.

So these three bars hold the shape of the lift rather than the lift itself. **C125** holds that
an admission is a written, dated, named act and not a tier. **C126** holds the one limit the
owner's reasoning cannot cross -- a prohibition on the computation is not a rule about sending,
so Cboe cannot be admitted even by editing the admission list. **C127** holds the cost in the
tree, so that whoever ships this repository in eighteen months is told by a file rather than
expected to remember a conversation.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import pytest

from deskcraft.panel import UncommittableSeries, refuse_uncommittable
from deskcraft.sources import (
    ADMITTED,
    SOURCE_ROWS,
    SOURCES,
    Admission,
    Derivation,
    Licence,
    Source,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
MARKER = ROOT / "NOT_SENDABLE.md"
ADMISSION_DOC = ROOT / "docs" / "OWNER_ADMISSION_the_credit_tier.md"

#: The three the owner took on 2026-09-23. A fourth is a fourth decision, so this bar names
#: them rather than counting them -- a count would pass silently when the list grew.
EXPECTED = ("T10YIE", "BAA10Y", "AAA10Y")


def test_an_admission_is_a_written_dated_named_act_and_not_a_tier() -> None:
    """C125. DD137. Every admitted series is in the register, in the document, with a reason."""
    assert tuple(ADMITTED) == EXPECTED, (
        "the admission list changed. That is a new owner decision, not a test to update: "
        f"expected {EXPECTED}, found {tuple(ADMITTED)}"
    )
    assert ADMISSION_DOC.exists(), (
        f"{ADMISSION_DOC.name} is the written record `sources.ADMITTED` refers to. An "
        "admission that exists only in code is the thing DD137 was careful not to be."
    )
    text = ADMISSION_DOC.read_text(encoding="utf-8")

    for series, entry in ADMITTED.items():
        assert isinstance(entry, Admission)
        assert entry.series == series, "the register is keyed by a series it does not name"
        assert entry.admitted == date(2026, 9, 23), f"{series}: the date cannot be back-filled"
        # A reason per series, not per tier. Long enough that "credit" cannot be the whole of it.
        assert len(entry.reason) > 60, f"{series}: a reason short enough to be a category"
        assert series in text, f"{series} is admitted in code and absent from the document"
        assert series in SOURCES, f"{series} is admitted and has no row in the source register"
        assert SOURCES[series].committable, f"{series} is admitted and still not committable"
        assert SOURCES[series].readable, (
            f"{series} may be committed and may not be read, which is incoherent -- committing "
            "is strictly stronger"
        )

    # The reasons are distinct. Three copies of one sentence is a tier wearing three hats.
    reasons = [e.reason for e in ADMITTED.values()]
    assert len(set(reasons)) == len(reasons), "two admissions share a reason"


def test_a_prohibition_on_computing_is_not_a_rule_about_sending() -> None:
    """C126. DD137's limit. Cboe cannot be admitted, and not because nobody tried."""
    vixcls = SOURCES["VIXCLS"]
    assert vixcls.derivation is Derivation.PROHIBITED
    assert "VIXCLS" not in ADMITTED
    assert not vixcls.committable and not vixcls.readable

    # And the refusal is structural rather than a fact about this list's current contents.
    # The mutation that matters is not "admit Cboe" -- it is an ADMITTED row whose derivation
    # is later read as prohibited, which is exactly what would happen if someone measured
    # Moody's derivation words and found them stricter than the silence assumed today. The
    # row must then refuse to construct, not quietly stay committable.
    with pytest.raises(ValueError, match="forbid derivation may not be admitted"):
        Source(
            series="BAA10Y",  # in ADMITTED
            originator="x",
            originator_class=vixcls.originator_class,
            publisher="x",
            fred_tag=None,
            notice=Licence.REDISTRIBUTION_PROHIBITED,
            derivation=Derivation.PROHIBITED,
            evidence="synthetic",
            fallback=None,
            fallback_originator=None,
            no_fallback_reason="synthetic",
        )

    # The loader refuses it too, with a message that says which rule is doing the refusing.
    with pytest.raises(UncommittableSeries, match="admitted by name"):
        refuse_uncommittable(("VIXCLS",))


def test_the_cost_of_the_lift_is_recorded_in_the_tree_and_not_in_a_memory() -> None:
    """C127. DD137. `NOT_SENDABLE.md` exists iff a committed file carries an admitted series.

    The bar is an *equivalence*, deliberately. A marker that is always present is wallpaper,
    and a marker that is absent while the condition holds is the failure this exists to catch.
    """
    panels = sorted(FIXTURES.glob("*.csv"))
    assert panels, "no fixture found, so the sweep below would pass by looking at nothing"

    carried: list[str] = []
    for panel in panels:
        with panel.open(newline="", encoding="utf-8") as fh:
            header = next(csv.reader(fh), [])
        for column in header:
            if column.strip() in ADMITTED:
                carried.append(f"{panel.name}: {column.strip()}")

    if carried:
        assert MARKER.exists(), (
            "a committed fixture carries an admitted series and NOT_SENDABLE.md is absent. "
            "The repository stopped being freely sendable and nothing in the tree says so: "
            + "; ".join(carried)
        )
        body = MARKER.read_text(encoding="utf-8")
        for series in sorted({c.split(': ')[1] for c in carried}):
            assert series in body, f"{series} is committed and the marker does not name it"
    else:
        # Today's state. The decision is taken, the columns are not in a fixture yet, and the
        # marker stands as the standing warning DD137 requires -- so its presence is correct
        # either way and only its ABSENCE-while-carried is a failure.
        assert MARKER.exists(), (
            "DD137 requires the marker to stand from the decision onward, not from the first "
            "commit of data, because the decision is what makes a future commit unremarkable"
        )

    # Whatever else is true, DD35's original question still has an answer for every row.
    for row in SOURCE_ROWS:
        assert row.sendable_free == (row.licence is Licence.PUBLIC_DOMAIN), row.series
        if row.series in ADMITTED:
            assert not row.sendable_free, (
                f"{row.series}: an admitted row that is also freely sendable means the "
                "admission was unnecessary and the two predicates have been confused"
            )


def admitted_columns_by_file(fixtures: Path) -> dict[str, list[str]]:
    """Every committed fixture that carries an admitted series, and which ones. Shared by C128
    and its mutation, so the mutation exercises the sweep rather than a copy of it."""
    found: dict[str, list[str]] = {}
    for panel in sorted(fixtures.glob("*.csv")):
        with panel.open(newline="", encoding="utf-8") as fh:
            header = [column.strip() for column in next(csv.reader(fh), [])]
        carried = [column for column in header if column in ADMITTED]
        if carried:
            found[panel.name] = carried
    return found


def test_c128_the_admitted_tier_travels_in_one_file_on_the_same_grid(tmp_path: Path) -> None:
    """C128. DD140. What may only be computed on is kept apart from what may be sent.

    DD137 admitted three series to committed fixtures. DD140 landed two of them and put them in a
    **third file**, so the two public-domain panels stay byte-identical and sendable and a strip
    for sending is one file. That is a property of where columns are, so it is swept over every
    fixture rather than asserted of the one file that is supposed to hold them. `T10YIE` is
    admitted and deliberately **not** carried (DD45), so it appears in no fixture at all.

    **Mutation:** a tree whose public-domain panel has gained `BAA10Y` is reported.
    """
    from deskcraft.panel import (
        ADMITTED_FIXTURE,
        ADMITTED_SERIES,
        DAILY_FIXTURE,
        load_daily,
        load_daily_admitted,
    )
    from deskcraft.window import DEV_END, FitWindow

    from deskcraft.readers import RECORD_FILES

    # One file per window: DEV's, and since the read of 2026-09-28 the record's (DD102). The
    # public-domain panels beside each carry none of it, and NOT_SENDABLE.md names both.
    expected = {ADMITTED_FIXTURE.name: list(ADMITTED_SERIES)}
    if RECORD_FILES[1].exists():
        expected[RECORD_FILES[1].name] = list(ADMITTED_SERIES)
    assert admitted_columns_by_file(FIXTURES) == expected
    assert all(name in MARKER.read_text(encoding="utf-8") for name in expected), "NOT_SENDABLE.md"
    assert ADMITTED_SERIES == ("BAA10Y", "AAA10Y")
    assert "T10YIE" in ADMITTED and "T10YIE" not in ADMITTED_SERIES

    dev = FitWindow.dev()
    credit, rates = load_daily_admitted(dev), load_daily(dev)
    assert credit.dates == rates.dates, "the admitted panel is not on the rates panel's grid"
    assert max(credit.dates) <= DEV_END
    coverage = {name: sum(v is not None for v in credit.column(name)) for name in ADMITTED_SERIES}
    assert coverage == {"BAA10Y": 6_753, "AAA10Y": 6_753}, coverage
    assert DAILY_FIXTURE.name != ADMITTED_FIXTURE.name

    fake = tmp_path / "fixtures"
    fake.mkdir()
    (fake / "panel_daily_dev_x.csv").write_text("Date,SVENY01,BAA10Y\n1990-01-02,1,2\n", "utf-8")
    assert admitted_columns_by_file(fake) == {"panel_daily_dev_x.csv": ["BAA10Y"]}


def test_c129_moodys_derivation_words_are_read_and_the_admission_stands() -> None:
    """C129. DD140. The one way C126 said the admission could fall was measured, and it did not.

    Moody's notice forbids copying, repackaging and redistribution without consent; none of its
    verbs is computing, so the pair grades `RESULTS_ONLY`. The derivation axis stops being silent
    for them, and what is left unread on it is a census rather than a comment: only the German
    zero, whose publisher is not chosen.
    """
    for series in ("BAA10Y", "AAA10Y"):
        row = SOURCES[series]
        assert row.derivation is Derivation.RESULTS_ONLY, series
        assert "2026-09-25" in row.evidence and "terms-of-use" in row.evidence, series
        assert row.notice is Licence.REDISTRIBUTION_PROHIBITED, "the copying grade did not move"
        assert row.committable and row.readable and not row.sendable_free, series

    unread = {row.series for row in SOURCE_ROWS if row.derivation is Derivation.UNMEASURED}
    assert unread == {"DE_ZERO_10Y"}, unread
