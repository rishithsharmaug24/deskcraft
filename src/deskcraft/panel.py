"""The data panel, read from a committed file. D3b, decisions DD42-DD48, bars C42-C48.

**This is the first module in this repository that opens a file, and the last one that should
have to.** Everything upstream of it -- the extraction, the vintage filter, the licence
closure -- happened in curvecast, which has the egress. What arrives here is two CSVs with a
date in their names, and `scripts/make_deskcraft_panel.py` over there is what put them there.
deskcraft never fetches, and `tests/conftest.py` refuses the network for the whole test
process so that this stays a property rather than a habit.

**The grid is GSW's and the blanks are real** (DD42). The daily fixture is one row per GSW DEV
session, all 7,044 of them, 1988-01-01 to 2014-12-31. A series with no observation on a
session has an empty field, and 309 rows are blank across every GSW column because those are
federal holidays. Nothing upstream dropped them, for curvecast's D412 reason: a complete-case
file could no longer tell a reader whether a gap was a holiday or a coverage defect. So the
filtering happens **here**, in `complete_cases`, which is a separate named step that returns
how many rows it dropped instead of quietly returning a shorter panel.

**Two frequencies, two files, and no join** (DD44). `GZ_SPREAD` is monthly -- 323 observations
against 6,504 for a constant-maturity series -- and this module offers no way to put it on the
daily grid. Forward-filling it would record roughly 6,200 daily credit observations that were
never published, and a loader that made that one keyword argument away is a loader that will
be given that keyword argument.

**The refusal is shared with the bar that checks it** (DD48). `refuse_uncommittable` is called
by `load_daily` at run time and by `C43` over the committed bytes, so the guard a test
exercises is the guard the loader runs. A copy of that check written separately for the test
would be a plausible-looking second implementation, and `C47` mutates this one.

**`NA` and an empty field both parse to `None`, and that is a loss the fixture does not
share.** In the file they are different facts: `NA` is GSW's own holiday marker, and empty
means the source published no observation for that date at all. At load time a missing number
is a missing number, so both become `None` -- but the distinction survives on disk, which is
where a later reader who needs it will look.

**No arithmetic happens here.** No return, no difference, no fill. `T10YIE` is not carried and
is not constructed, although `DGS10` and `DFII10` are both columns and the subtraction is one
line: a panel that carried a derived column beside its two inputs would invite every reader to
treat it as a third source, and `REAL_VS_NOMINAL` is a term in D6's grammar, not a column here.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from deskcraft.sources import SOURCES
from deskcraft.window import FitWindow, OosWindow

__all__ = [
    "ADMITTED_FIXTURE",
    "ADMITTED_SERIES",
    "DAILY_FIXTURE",
    "DAILY_SERIES",
    "FX_FIXTURE",
    "FX_QUOTES",
    "FX_SERIES",
    "MONTHLY_FIXTURE",
    "MONTHLY_SERIES",
    "Panel",
    "UncommittableSeries",
    "complete_cases",
    "load_daily",
    "load_daily_admitted",
    "load_daily_fx",
    "load_record",
    "load_monthly",
    "refuse_uncommittable",
]

_FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures"

#: The extraction's date, not the data's. In the filename so that a second panel cannot
#: silently replace a first -- D23's `exposure_probe_20260909.csv` set the convention.
DAILY_FIXTURE = _FIXTURES / "panel_daily_dev_20260914.csv"
MONTHLY_FIXTURE = _FIXTURES / "panel_monthly_dev_20260914.csv"

#: The seventeen daily series, in the order the fixture carries them. Eight GSW zeros, five
#: constant maturities, three TIPS real yields and one exchange rate.
DAILY_SERIES: tuple[str, ...] = (
    "SVENY01",
    "SVENY02",
    "SVENY03",
    "SVENY05",
    "SVENY07",
    "SVENY10",
    "SVENY20",
    "SVENY30",
    "DGS3MO",
    "DGS6MO",
    "DGS1",
    "DGS2",
    "DGS10",
    "DFII5",
    "DFII10",
    "DFII30",
    "DEXUSEU",
)

#: The credit leg, monthly, and a substitute construct rather than a mirror (DD46).
MONTHLY_SERIES: tuple[str, ...] = ("GZ_SPREAD",)

#: The daily credit tier, in a file of its own (DD140). The owner admitted both to committed
#: fixtures by name (DD137), and Moody's words forbid passing the numbers on while saying
#: nothing against computing on them (`Derivation.RESULTS_ONLY`, read 2026-09-25). They are
#: not freely sendable, so they travel apart from the two public-domain panels above, which
#: stay byte-identical: stripping this repository for sending is one file, not a column
#: surgery. Same GSW grid, same vintage rule, extracted by the same curvecast script.
ADMITTED_FIXTURE = _FIXTURES / "panel_daily_admitted_dev_20260925.csv"
ADMITTED_SERIES: tuple[str, ...] = ("BAA10Y", "AAA10Y")

#: The H.10 majors, in a file of their own (DD168). Public domain like everything in the two
#: panels above, so licence is not what separates them: those two feed every verdict already
#: registered and pinned, and a file that is never rewritten cannot move a pinned number.
#: Same GSW grid and vintage rule, extracted by the same curvecast script from one ALFRED as-of
#: read per series, so no byte dated after `DEV_END` was ever requested.
FX_FIXTURE = _FIXTURES / "panel_daily_fx_dev_20260926.csv"
FX_SERIES: tuple[str, ...] = ("DEXJPUS", "DEXUSUK", "DEXCAUS", "DEXSZUS", "DEXCHUS", "DEXMXUS")

#: Each rate as H.10 quotes it. Only sterling is quoted like the euro, in dollars per unit of the
#: foreign currency; the other five are foreign units per dollar, so a long position in any of
#: those five gains when its rate FALLS. A hedge leg that ignores this is built backwards.
FX_QUOTES: dict[str, tuple[str, str]] = {
    "DEXUSEU": ("EUR", "USD per EUR"),
    "DEXJPUS": ("JPY", "JPY per USD"),
    "DEXUSUK": ("GBP", "USD per GBP"),
    "DEXCAUS": ("CAD", "CAD per USD"),
    "DEXSZUS": ("CHF", "CHF per USD"),
    "DEXCHUS": ("CNY", "CNY per USD"),
    "DEXMXUS": ("MXN", "MXN per USD"),
}

#: GSW's own marker for a session it published with no value. Distinct on disk from an empty
#: field, which means the source published nothing for that date at all.
_ABSENT = frozenset({"", "NA"})


class UncommittableSeries(ValueError):
    """A panel column whose licence forbids the file carrying it (DD35, DD48)."""


@dataclass(frozen=True)
class Panel:
    """Dates and series, aligned. Values are `None` where the source published nothing.

    Deliberately not a matrix: `numpy` arrives with D4, when there is arithmetic to do, and a
    panel that was already an array would invite the arithmetic to be done here.

    **ANNOTATED 2026-09-15 (D4).** numpy did not arrive with D4, and the sentence is left
    as written. The arithmetic turned out to be four legs, five series and six scalar
    formulas, so `deskcraft.sensitivity` takes a `Mapping[str, float]` of yields and this
    type was never the thing standing in its way. The second clause held up better than
    the first: `sensitivity` does the arithmetic, this module still does none, and the
    reason a panel is not an array is unchanged.
    """

    dates: tuple[date, ...]
    series: tuple[str, ...]
    values: dict[str, tuple[float | None, ...]]

    def __post_init__(self) -> None:
        if tuple(sorted(self.dates)) != self.dates:
            raise ValueError("a panel's dates must be in order")
        if len(set(self.dates)) != len(self.dates):
            raise ValueError("a panel repeats a date")
        for name in self.series:
            column = self.values.get(name)
            if column is None:
                raise ValueError(f"series {name} is named and has no column")
            if len(column) != len(self.dates):
                raise ValueError(
                    f"series {name} has {len(column)} values against {len(self.dates)} dates"
                )

    def column(self, series: str) -> tuple[float | None, ...]:
        """One series, aligned to `dates`."""
        try:
            return self.values[series]
        except KeyError:
            raise KeyError(f"{series} is not in this panel; it carries {self.series}") from None


def refuse_uncommittable(columns: tuple[str, ...]) -> None:
    """Raise unless every column is a registered, public-domain series (DD35, DD48).

    Called by `load_daily` and `load_monthly` at run time, and by `C43` over the committed
    bytes. One implementation, so the guard the bar exercises is the guard that runs -- and
    `C47` mutates this function rather than a copy of it.
    """
    unknown = [name for name in columns if name not in SOURCES]
    if unknown:
        raise UncommittableSeries(
            f"{unknown} have no row in the source register. A series with no measured licence "
            "is not committable by default; `Licence.UNMEASURED` is the strictest value, not "
            "an absent one."
        )
    refused = [name for name in columns if not SOURCES[name].committable]
    if refused:
        detail = ", ".join(f"{name} ({SOURCES[name].licence.name})" for name in refused)
        raise UncommittableSeries(
            f"a committed fixture carries {detail}. A fixture may carry a public-domain series "
            "(DD35), or one the owner has admitted by name in `sources.ADMITTED` (DD137). "
            "These are neither. Admission is a decision the owner takes in writing for a named "
            "series, not a tier and not a default -- and a series whose words forbid derivation "
            "cannot be admitted at all, because DD137's reasoning is about sending and a "
            "prohibition on the computation is not a rule about sending."
        )


def _parse(text: str) -> float | None:
    if text in _ABSENT:
        return None
    return float(text)


def _read(path: Path, expected: tuple[str, ...], window: FitWindow) -> Panel:
    if not path.exists():
        raise FileNotFoundError(
            f"{path.name} is not in tests/fixtures. It is produced by curvecast's "
            "scripts/make_deskcraft_panel.py; this repository has no egress and cannot "
            "rebuild it."
        )
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = tuple(reader.fieldnames or ())
        if not header or header[0] != "Date":
            raise ValueError(f"{path.name} does not open with a Date column")
        columns = header[1:]
        refuse_uncommittable(columns)
        if columns != expected:
            raise ValueError(f"{path.name} carries {columns}, expected {expected}")

        dates: list[date] = []
        gathered: dict[str, list[float | None]] = {name: [] for name in columns}
        for row in reader:
            year, month, day = row["Date"].split("-")
            stamp = date(int(year), int(month), int(day))
            if not window.start <= stamp <= window.end:
                continue
            dates.append(stamp)
            for name in columns:
                gathered[name].append(_parse(row[name]))

    return Panel(
        dates=tuple(dates),
        series=columns,
        values={name: tuple(values) for name, values in gathered.items()},
    )


def load_daily(window: FitWindow) -> Panel:
    """The daily panel, restricted to `window`.

    A `FitWindow` rather than two dates, so DEC-1's bound is enforced by the type before this
    function sees it: a window reaching past 2014-12-31 is refused at construction, and a
    `datetime` where a `date` belongs is refused there too rather than raising later on a
    comparison.
    """
    return _read(DAILY_FIXTURE, DAILY_SERIES, window)


def load_daily_admitted(window: FitWindow) -> Panel:
    """The daily credit tier, restricted to `window`, on the same grid as `load_daily`.

    A separate loader rather than three more columns on `load_daily`, for DD140's reason:
    what may be sent and what may only be computed on are kept in different files, and a
    caller that joins them does so where the join is visible.
    """
    return _read(ADMITTED_FIXTURE, ADMITTED_SERIES, window)


def load_daily_fx(window: FitWindow) -> Panel:
    """The H.10 majors, restricted to `window`, on the same grid as `load_daily` (DD168).

    A separate loader so that nothing registered before DD168 reads a file DD168 wrote.
    """
    return _read(FX_FIXTURE, FX_SERIES, window)


def load_record(path: Path, expected: tuple[str, ...]) -> Panel:
    """One out-of-sample file, whole, or a refusal: never a quietly filtered slice.

    Takes a path rather than naming a file, so no module here names an out-of-sample panel before
    the owner's authorisation (DD133, C119); the trigger commit adds the files and the one line
    that passes them in. Every row must lie inside `OosWindow.whole()`. `_read` skips rows outside
    its window, which is right for a fit and wrong here: a DEV row inside the record's file is a
    defect in the extraction, and dropping it would hide the defect behind a complete grid.
    """
    whole = OosWindow.whole()
    with path.open(newline="", encoding="utf-8") as handle:
        stamps = [row["Date"] for row in csv.DictReader(handle)]
    outside = [s for s in stamps if not whole.start <= date.fromisoformat(s) <= whole.end]
    if outside:
        raise ValueError(f"{path.name} carries rows outside {whole.start} -> {whole.end}: {outside[:3]}")
    return _read(path, expected, whole)


def load_monthly(window: FitWindow) -> Panel:
    """The monthly panel, restricted to `window`. Its dates are month-start labels.

    There is no `load` that returns both, and no argument that puts this one on the daily
    grid (DD44). A caller that needs them together aligns them where the alignment rule is
    visible and can be argued with.
    """
    return _read(MONTHLY_FIXTURE, MONTHLY_SERIES, window)


def complete_cases(panel: Panel, series: tuple[str, ...] | None = None) -> tuple[Panel, int]:
    """Rows where every named series has a value, and **how many rows that dropped**.

    The count is returned rather than discarded because it is the whole reason the blanks were
    kept upstream. `DFII30` opens in 2010, so asking for complete cases across all seventeen
    series silently costs twenty-two years of the sample -- and a function that returned only
    the shorter panel would let that happen without anyone writing the number down.

    `series` defaults to every column. Restricting it is the ordinary case: a covariance over
    the front end has no reason to be truncated by a series it does not use.
    """
    wanted = panel.series if series is None else series
    missing = [name for name in wanted if name not in panel.values]
    if missing:
        raise KeyError(f"{missing} are not in this panel; it carries {panel.series}")

    keep = [
        index
        for index in range(len(panel.dates))
        if all(panel.values[name][index] is not None for name in wanted)
    ]
    kept = Panel(
        dates=tuple(panel.dates[index] for index in keep),
        series=panel.series,
        values={
            name: tuple(values[index] for index in keep) for name, values in panel.values.items()
        },
    )
    return kept, len(panel.dates) - len(keep)
