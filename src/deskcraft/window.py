"""The window every fitted object is estimated on. D3a, decisions DD28-DD29, bars C30-C31.

The approved plan's DEC-1 fits on DEV and replays on all history: every object whose output
is used out of sample -- the covariance, the factor basis, the GARCH filter, a shrinkage
intensity -- is estimated on **1988-01-01 -> 2014-12-31**, and the backtests run on
2015 -> present. `PLAN_deskcraft.md` §9 names the one way that design fails: *the covariance
fitted on the window it is stress-tested against.* This module is what makes that a refusal
rather than a discipline.

**The bounds are curvecast's, restated and checked rather than imported.** `DEV_START` and
`DEV_END` are the values `curvecast.pit.seal` assigns, and C31 reads that file at test time
and compares. Importing it would put curvecast on this package's import path eight packages
before the plan needs it, and a copy nothing checks is a copy that drifts.

**Both fields must be exactly `datetime.date`** (DD28). `datetime` is a subclass of `date`, so
an `isinstance` check admits it, and comparing it with a `date` then raises `TypeError`. A
guard written against `date` that receives a `datetime` is therefore refusing by accident,
and one refactor away from accepting. The refusal here is deliberate and has its own message.

**The start is bounded as well as the end.** DEC-1 fixes the fit sample exactly, and the
risk-model backtest compares objects fitted on one sample; a covariance fitted from 1970 is
not a leak, but it is not the object the backtest was pre-registered against.

**What this does not govern** (DD29). A dated replay measures realised correlations *on* the
2020 window, because stressing a crisis with full-sample correlations is circular. That is a
statistic of the scenario, not a fitted object used out of sample; it belongs to D12's own
window type, and it never feeds an estimator. This type is for estimators.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

__all__ = ["DEV_END", "DEV_START", "FitWindow", "OOS_END", "OOS_START", "OosWindow"]

#: First day of curvecast's DEV split, `curvecast.pit.seal.DEV_START`. Checked by C31.
DEV_START = date(1988, 1, 1)

#: Last day of curvecast's DEV split, `curvecast.pit.seal.DEV_END`. Checked by C31.
DEV_END = date(2014, 12, 31)

#: First day of the out-of-sample record (`AMENDMENT_A4` §3.1, DD98). Contiguous with `DEV_END`
#: by construction -- the day after it -- so DEV and OOS partition the record with no gap a
#: package could quietly fit a window into. C96 holds the contiguity.
OOS_START = date(2015, 1, 1)

#: Last day of the out-of-sample record (DD98). **Fixed before the panel that covers it exists**,
#: by a rule rather than by taste: the last *complete* calendar year at the date of specification,
#: 2026-09-16. The rule yields exactly one answer, so there was nothing to pick -- and it
#: returns the same answer on 2026-09-15, the day the amendment was drafted; the first date it
#: would return anything else is 2027-01-01. **C98 holds this constant to that rule**, applied to
#: the date the amendment states, so the derivation is checked rather than asserted.
#:
#: **This is a constant and not a clock read, and that is the point.** A window ending "at
#: extraction" would change every time the extractor runs, which makes re-running it until the
#: numbers improve a refresh rather than a violation. Extending it is a code change, an amendment
#: and a red bar -- see `AMENDMENT_A4` §3.1's extension rule, which also forbids merging any
#: extension into a headline already published.
OOS_END = date(2025, 12, 31)


@dataclass(frozen=True)
class FitWindow:
    """A closed interval of dates inside DEV, which an estimator takes instead of raw dates."""

    start: date
    end: date

    def __post_init__(self) -> None:
        for name in ("start", "end"):
            value = getattr(self, name)
            if type(value) is not date:
                raise TypeError(
                    f"FitWindow.{name} must be a datetime.date exactly, not "
                    f"{type(value).__name__}. A datetime is a date subclass that raises on "
                    "comparison with a date, so admitting one would make the bound below a "
                    "TypeError by accident rather than a refusal by design."
                )
        if self.start < DEV_START:
            raise ValueError(
                f"a fit starting {self.start} begins before DEV_START {DEV_START}. DEC-1 fixes "
                "the fit sample exactly, and the backtest is pre-registered against objects "
                "fitted on that sample."
            )
        if self.end > DEV_END:
            raise ValueError(
                f"a fit ending {self.end} reaches past DEV_END {DEV_END}. Every out-of-sample "
                "test in this repo runs on the years after DEV_END, so a fit reaching into them "
                "is the circularity PLAN_deskcraft.md §9 names, and it is refused here rather "
                "than reported later."
            )
        if self.start >= self.end:
            raise ValueError(
                f"a fit window must run forwards: start {self.start} is not before end "
                f"{self.end}."
            )

    @classmethod
    def dev(cls) -> FitWindow:
        """The whole DEV split, which is DEC-1's pre-registered fit sample."""
        return cls(DEV_START, DEV_END)


@dataclass(frozen=True)
class OosWindow:
    """A closed interval of dates inside the out-of-sample record (`AMENDMENT_A4` §5).

    `FitWindow` refuses an end past `DEV_END`, so a covariance cannot be fitted on the years it
    is tested against. This is the other half: it refuses a window that reaches *back* into the
    fit sample, and one that reaches *forward* past the end fixed in advance.

    **Why the forward bound is a type and not a sentence.** D12, D14, D15, D21 and D22 all read
    this record (D21 since DD199), and none of them existed when the window was fixed. A window left to the package that
    reads it is the defect `AMENDMENT_A2` found in the cost hurdle and `AMENDMENT_A3` found in
    the effective-number-of-bets basis, with the sample itself as the free parameter. Extending
    the out-of-sample record is therefore a code change, an amendment and a red bar rather than a
    keyword argument.
    """

    start: date
    end: date

    def __post_init__(self) -> None:
        for name in ("start", "end"):
            value = getattr(self, name)
            if type(value) is not date:
                raise TypeError(
                    f"OosWindow.{name} must be a datetime.date exactly, not "
                    f"{type(value).__name__}. A datetime is a date subclass that raises on "
                    "comparison with a date, so admitting one would make the bounds below a "
                    "TypeError by accident rather than a refusal by design."
                )
        if self.start <= DEV_END:
            raise ValueError(
                f"an out-of-sample window starting {self.start} reaches back into DEV, which "
                f"ends {DEV_END}. Every object this record scores was fitted on DEV, so a test "
                "window overlapping it is the circularity PLAN_deskcraft.md §9 names."
            )
        if self.start < OOS_START:
            raise ValueError(
                f"an out-of-sample window starting {self.start} begins before OOS_START "
                f"{OOS_START}."
            )
        if self.end > OOS_END:
            raise ValueError(
                f"an out-of-sample window ending {self.end} reaches past OOS_END {OOS_END}. "
                "The out-of-sample record is fixed in advance (`AMENDMENT_A4` DD98) and is "
                "extended only at a complete calendar-year boundary, by amendment, and reported "
                "as a separate window -- never merged into a headline already published."
            )
        if self.start >= self.end:
            raise ValueError(
                f"an out-of-sample window must run forwards: start {self.start} is not before "
                f"end {self.end}."
            )

    @classmethod
    def whole(cls) -> OosWindow:
        """The whole pre-registered out-of-sample record: eleven complete calendar years."""
        return cls(OOS_START, OOS_END)
