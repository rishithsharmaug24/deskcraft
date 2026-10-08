"""Where every series comes from, what its licence says, and what replaces it. D3a, DD34-DD36, bar C36.

**Extended at D3b (DD47) by two rows, neither of them a new permission.** `DGS10` is an H.15
row identical in shape to the four D5 graded; it was always inside curvecast's public-domain
publication and always carried in its CMT fixture, and what it lacked was a row here saying
so. It is one of the two inputs `T10YIE` is constructed from, which is why D3a left it as this
package's inheritance. `GZ_SPREAD` is the credit leg the owner chose on 2026-09-14 in place of
the two Moody's rows, whose licence forbids the fixture: a substitute construct, monthly, on a
different bond universe, and public domain by a reading rather than by a default.

**Why this exists.** A free source did not theoretically go bad -- one went bad in April 2026.
FRED's ICE BofA option-adjusted spreads now carry *"only ... 3 years of observations"*, and on
2026-09-11 `BAMLC0A0CM` reported `observation_start = 2023-09-12`. The series was withdrawn by
its **licensor** through its **distributor**, and nothing upstream of the consumer could see it
coming. So every series this repo will read carries a row saying who computes it, who
publishes it, what its licence says, and what would replace it.

**The licence is the stricter of two statements, and they disagree** (DD34). FRED tags
`BAA10Y` *copyrighted: citation required*; the Moody's notice in the same series' notes forbids
copying, reproduction and redistribution without prior written consent. A register that
recorded the tag would record the weaker statement about the same bytes. `Licence` is ordered
and a row answers with the maximum of the two, the way curvecast's `worst_of` answers for a
grade: contamination is monotone. `UNMEASURED` is the strictest value, not an absent one.

**Only a public-domain series is committable** (DD35). Citation-required copyright is not a
licence to redistribute, and a fixture committed to a repository that is then sent anywhere is
redistribution. D3b inherits `Source.committable` as a refusal. It is an engineering rule and
conservative on purpose; no row here is a reading of anyone's contract.

**A licence answers what may be copied and not what may be computed** (DD136, extending DD118).
Those are two questions and `Licence` is one ordered scale, so for six days DD118's rule -- *read
yes, commit no* -- lived in a document while every package that wanted to read a row asked
`committable` instead and got a stricter answer than its question deserved. `Derivation` is the
second axis and `Source.disposition` derives DD118's three cells from both. The middle one,
`USABLE_NOT_COMMITTABLE`, was occupied before it had a name: `T10YIE` has been in it since D3a.
`committable` is unchanged in meaning, and C124 holds that it stayed unchanged.

**A fallback names its originator, so a mirror is not mistaken for a second source** (DD36).
Treasury.gov behind `DGS10` protects against FRED or the Board withdrawing the series -- which
is what happened to ICE's -- and not against Treasury changing its method, because H.15's
constant-maturity yields *are* Treasury's. `independent_fallback` is derived as *the
originators differ*, and most rows here are honest about being the other kind.

Measured 2026-09-11: FRED's `cc` tag group through the API, the series notes, the Federal
Reserve Board's disclaimer, and data.gov's licence field for Treasury's curves. The document
that records the readings is `docs/PRECOMMIT_deskcraft_d3a_guards_and_registers.md` §0.8-§0.9.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import IntEnum, StrEnum

__all__ = [
    "ADMITTED",
    "SOURCES",
    "SOURCE_ROWS",
    "Admission",
    "Derivation",
    "Disposition",
    "Licence",
    "OriginatorClass",
    "Source",
]


class Licence(IntEnum):
    """What a statement about a series permits, ordered from least to most restrictive.

    Classified from the words, not from their typography:

    - `PUBLIC_DOMAIN` -- dedicated to the public domain, or copying and distribution permitted
      without permission. Citation may be requested.
    - `CITATION_REQUIRED` -- copyright asserted, reuse with attribution.
    - `PRE_APPROVAL_REQUIRED` -- copyright asserted, reuse by permission. A notice that says the
      distributor reprints *with permission* grants nothing further downstream, and lands here.
    - `REDISTRIBUTION_PROHIBITED` -- the words forbid reproduction or redistribution without
      consent.
    - `UNMEASURED` -- nobody has read the words. Strictest, because a default here would hand
      the widest permission to the least evidence.
    """

    PUBLIC_DOMAIN = 0
    CITATION_REQUIRED = 1
    PRE_APPROVAL_REQUIRED = 2
    REDISTRIBUTION_PROHIBITED = 3
    UNMEASURED = 4


class Derivation(IntEnum):
    """What a statement permits a reader to **compute** from the numbers.

    `Licence` answers what may be copied. That is a different question from what may be
    derived, and conflating the two is what **X22** named: a licence can be broader than
    `CITATION_REQUIRED` on redistribution and narrower on derivation, and one ordered scale
    cannot hold both halves. Graded from the words, like `Licence`, and strictest-when-unread
    for the same reason (DD34).

    - `PERMITTED` -- the words permit use and derivation, or the series is public domain and
      carries no condition at all.
    - `RESULTS_ONLY` -- derivation is permitted and republishing the *modified data* is not.
      Statistics, coefficients and verdicts travel; a derived series does not. The ESCB re-use
      policy is this shape, and it is the term A5 s3 stated in prose beside a row that could
      not hold it.
    - `PROHIBITED` -- the words forbid creating a derivative work at all. Cboe's terms are
      this shape, read at DD121: *"create a derivative work (for example, a financial product,
      service or index) from, use to verify or correct other data or information"*.
    - `UNMEASURED` -- nobody has read the derivation words. Strictest, not absent.
    """

    PERMITTED = 0
    RESULTS_ONLY = 1
    PROHIBITED = 2
    UNMEASURED = 3


class Disposition(StrEnum):
    """DD118's three-way sort of a graded source, which DD136 makes a property of the row.

    - `COMMITTABLE` -- public-domain bytes. A fixture may carry them and `git archive HEAD`
      may send them anywhere. DD35, unchanged and for its original reason.
    - `USABLE_NOT_COMMITTABLE` -- the numbers may be fetched, read and derived from; the bytes
      may not enter git. What ships is the result and the fetch script, not the panel. This is
      the cell DD118 opened and DD136 builds.
    - `REFUSED` -- the row may not be touched at all.
    """

    COMMITTABLE = "COMMITTABLE"
    USABLE_NOT_COMMITTABLE = "USABLE_NOT_COMMITTABLE"
    REFUSED = "REFUSED"


class OriginatorClass(StrEnum):
    """Who computes the number, coarsely. The ICE precedent is a commercial licensor."""

    PUBLIC_SECTOR = "PUBLIC_SECTOR"
    EXCHANGE = "EXCHANGE"
    COMMERCIAL_VENDOR = "COMMERCIAL_VENDOR"


@dataclass(frozen=True)
class Admission:
    """One series the owner has admitted to committed fixtures by name (DD137).

    An admission is **not** a licence reading and claims nothing about what the licence
    permits. It records that the owner, who owns the consequence, decided that a rule written
    for a repository that would be **sent to an institution** should not bind a repository
    that is not being sent. DD35's own text invited exactly that reading: *"this is an
    engineering rule, conservative on purpose. It is not a reading of anyone's contract."*

    Every field is load-bearing. `admitted` dates the decision so it cannot be back-filled.
    `reason` states why **this series** rather than the tier it belongs to, so the list cannot
    grow by category -- a fourth series is a fourth decision, not an extension of this one.

    The consequence is recorded in the tree, not in anyone's memory: `C127` requires
    `NOT_SENDABLE.md` to exist whenever an admitted series is in a committed file.
    """

    series: str
    admitted: date
    reason: str


#: Series the owner admitted on 2026-09-23; the written record is
#: `docs/OWNER_ADMISSION_the_credit_tier.md`. Three, by name.
#:
#: **Nothing whose words forbid derivation may appear here.** `Source.__post_init__` refuses
#: that combination, so this list cannot reach Cboe even by editing this list -- which is the
#: point, because Cboe's restriction is on the computation and not on the sending, and the
#: owner's reasoning above does not reach it.
ADMITTED: dict[str, Admission] = {
    a.series: a
    for a in (
        Admission(
            series="T10YIE",
            admitted=date(2026, 9, 23),
            reason=(
                "FRED's own citation-required tag over arithmetic on two public-domain series, "
                "with no third-party notice behind it. The weakest of the three claims, and the "
                "one that already had a committable construction, so admitting it costs least"
            ),
        ),
        Admission(
            series="BAA10Y",
            admitted=date(2026, 9, 23),
            reason=(
                "Moody's forbids copying, reproduction and redistribution without consent and "
                "says nothing about private computation. The whole of that prohibition governs "
                "an act this repository has stopped performing. This is the daily credit leg "
                "A5 measured CREDIT_VS_RATES at 0 of 1 tradeable series without"
            ),
        ),
        Admission(
            series="AAA10Y",
            admitted=date(2026, 9, 23),
            reason="The investment-grade pair to BAA10Y, on the same notice and the same reading",
        ),
    )
}


@dataclass(frozen=True)
class Source:
    """One series: its originator, its publisher, its licence, and its fallback."""

    series: str
    #: Who computes the number.
    originator: str
    originator_class: OriginatorClass
    #: Where the number is read today, which is not always its originator.
    publisher: str
    #: FRED's copyright category as read from the API, or `None` for a series FRED does not carry.
    fred_tag: Licence | None
    #: The licensor's own published words, classified.
    notice: Licence
    #: What those words permit a reader to compute, which `notice` does not answer (DD136).
    derivation: Derivation
    evidence: str
    fallback: str | None
    fallback_originator: str | None
    no_fallback_reason: str | None = None

    def __post_init__(self) -> None:
        if (self.fallback is None) != (self.no_fallback_reason is not None):
            raise ValueError(
                f"{self.series}: a fallback is absent if and only if a reason is given"
            )
        if (self.fallback is None) != (self.fallback_originator is None):
            raise ValueError(
                f"{self.series}: a fallback originator is named if and only if a fallback is"
            )
        if self.fred_tag is Licence.UNMEASURED:
            raise ValueError(
                f"{self.series}: a FRED tag is either read or absent; absent is None"
            )
        if self.licence is Licence.PUBLIC_DOMAIN and self.derivation is not Derivation.PERMITTED:
            raise ValueError(
                f"{self.series}: public domain carries no condition, so it cannot restrict "
                f"derivation; got {self.derivation.name}"
            )
        if self.series in ADMITTED and self.derivation is Derivation.PROHIBITED:
            raise ValueError(
                f"{self.series}: a series whose words forbid derivation may not be admitted "
                "(DD137). The owner's reasoning is that a rule about sending does not bind a "
                "repository that is not sent; a prohibition on the computation is not a rule "
                "about sending and that reasoning does not reach it."
            )

    @property
    def licence(self) -> Licence:
        """The operative licence: the stricter of FRED's tag and the licensor's words."""
        if self.fred_tag is None:
            return self.notice
        return max(self.fred_tag, self.notice)

    @property
    def admitted(self) -> Admission | None:
        """The owner's named admission of this series to committed fixtures, or `None` (DD137)."""
        return ADMITTED.get(self.series)

    @property
    def committable(self) -> bool:
        """Whether a fixture may carry this series (DD35, widened by DD137).

        Two ways, and the second is a decision rather than a reading. Public domain qualifies
        for DD35's original reason: those bytes travel without conditions, to anyone, forever.
        An **admitted** series qualifies because the owner decided on 2026-09-23 that DD35's
        stated premise -- *a repository that is then sent anywhere* -- had stopped being true
        of this repository, and DD35's own closing sentence says it is an engineering rule and
        not a reading of anyone's contract.

        **The two are not equivalent and the code must not pretend they are.** `sendable_free`
        below is the property DD35 actually protected, and it still answers for every row.
        """
        return self.licence is Licence.PUBLIC_DOMAIN or self.series in ADMITTED

    @property
    def sendable_free(self) -> bool:
        """Whether this series' bytes travel to anyone without a condition (DD35's guarantee).

        Before DD137 this was the same question as `committable` and the repository had one
        predicate for both. They have come apart, so they are two predicates: a fixture may
        now carry a row that is committable and not freely sendable, and **that is exactly
        what makes this repository no longer archivable by default.** C127 holds the
        consequence in the tree.
        """
        return self.licence is Licence.PUBLIC_DOMAIN

    @property
    def readable(self) -> bool:
        """Whether a package may fetch this series and derive from it (DD118, DD136).

        Two conditions, one per axis, because the axes are independent. The licence must grant
        use on attribution or better, which is DD118's own wording. And the words must not
        forbid derivation: `RESULTS_ONLY` passes because this repository publishes results and
        does not republish data, which is precisely the distinction DD118 relies on; and
        `UNMEASURED` fails for DD34's reason, since a default here would hand the widest
        permission to the least evidence.

        **An admitted series is readable whatever its licence axis says** (DD137). Reading is
        strictly weaker than committing, so a row the owner admitted to a committed file and
        the code then refused to read would be incoherent -- and `Derivation.PROHIBITED` is
        still refused, because `__post_init__` will not let such a row be admitted at all.
        `BAA10Y` reaches here by admission and not by grade, and the grade is unchanged.
        """
        if self.series in ADMITTED:
            return True
        return (
            self.licence <= Licence.CITATION_REQUIRED
            and self.derivation <= Derivation.RESULTS_ONLY
        )

    @property
    def disposition(self) -> Disposition:
        """DD118's three-way sort, derived rather than asserted (DD136, X22).

        `committable` implies `readable` by the invariant in `__post_init__`, so the order of
        these tests is a statement about strength and not a tie-break.
        """
        if self.committable:
            return Disposition.COMMITTABLE
        if self.readable:
            return Disposition.USABLE_NOT_COMMITTABLE
        return Disposition.REFUSED

    @property
    def independent_fallback(self) -> bool:
        """Whether the fallback survives the originator, not merely the distributor."""
        return self.fallback_originator is not None and self.fallback_originator != self.originator


_BOARD = "Board of Governors of the Federal Reserve System"
_TREASURY = "U.S. Department of the Treasury"
_ST_LOUIS = "Federal Reserve Bank of St. Louis"
_CBOE = "Cboe (Chicago Board Options Exchange)"
_MOODYS = "Moody's Investors Service"

_FRED_API = "FRED API series/tags `cc` group and series notes, read 2026-09-11"
_BOARD_DISCLAIMER = (
    "federalreserve.gov/disclaimer.htm, read 2026-09-11: public domain unless otherwise "
    "indicated, citation to the Board requested"
)
_TREASURY_NOMINAL = (
    "Treasury Daily Par Yield Curve Rates; data.gov licence CC0 1.0, read 2026-09-11"
)
_TREASURY_REAL = (
    "Treasury Daily Par Real Yield Curve Rates; CC0 per data.gov, read 2026-09-11 from a "
    "search result rather than the dataset page"
)


def _gsw(tenor: str) -> Source:
    return Source(
        series=f"SVENY{tenor}",
        originator=_BOARD,
        originator_class=OriginatorClass.PUBLIC_SECTOR,
        publisher="Board website, feds200628.csv, as pinned in curvecast's seal manifest",
        fred_tag=None,
        notice=Licence.PUBLIC_DOMAIN,
        derivation=Derivation.PERMITTED,
        evidence=_BOARD_DISCLAIMER,
        fallback=(
            f"{_TREASURY_NOMINAL}, bootstrapped to zero rates. A par curve on a different "
            "spline is a different object, so this is a substitute construct, not a mirror"
        ),
        fallback_originator=_TREASURY,
    )


def _h15(series: str, fallback: str) -> Source:
    return Source(
        series=series,
        originator=_TREASURY,
        originator_class=OriginatorClass.PUBLIC_SECTOR,
        publisher="Board H.15 Selected Interest Rates, via FRED",
        fred_tag=Licence.PUBLIC_DOMAIN,
        notice=Licence.PUBLIC_DOMAIN,
        derivation=Derivation.PERMITTED,
        evidence=f"{_FRED_API}; H.15 refers its yields to Treasury's yield curve methodology",
        fallback=fallback,
        fallback_originator=_TREASURY,
    )


def _moodys_spread(series: str, grade: str) -> Source:
    return Source(
        series=series,
        originator=_MOODYS,
        originator_class=OriginatorClass.COMMERCIAL_VENDOR,
        publisher=(
            f"FRED; the spread of Moody's Seasoned {grade} yield over the 10-year constant "
            "maturity, computed by the Federal Reserve Bank of St. Louis"
        ),
        fred_tag=Licence.CITATION_REQUIRED,
        notice=Licence.REDISTRIBUTION_PROHIBITED,
        # Read 2026-09-25 (DD140), graded from the words and not from their silence. FRED's
        # notes carry Moody's notice verbatim: the information "MAY NOT BE COPIED OR OTHERWISE
        # REPRODUCED, REPACKAGED, FURTHER TRANSMITTED, TRANSFERRED, DISSEMINATED, REDISTRIBUTED
        # OR RESOLD, OR STORED FOR SUBSEQUENT USE FOR ANY SUCH PURPOSE". Every verb passes the
        # numbers on; "repackaged" reaches a derived series published as data, and nothing
        # reaches computing a result from them. That is RESULTS_ONLY, the ESCB shape. Moody's
        # own site terms do forbid "create derivatives of", for material taken from its sites --
        # a route this register never uses, recorded in `evidence` so it stays closed.
        derivation=Derivation.RESULTS_ONLY,
        evidence=(
            f"{_FRED_API}; the notes carry Moody's notice forbidding copying, reproduction and "
            "redistribution without prior written consent, stricter than the tag. Derivation "
            "read 2026-09-25 from the same notes: the prohibited acts are copying, "
            "repackaging and redistribution, none of them computation (RESULTS_ONLY). "
            "moodys.com/web/en/us/legal/terms-of-use.html forbids 'modify, create derivatives "
            "of ... repackage' for material on Moody's own sites, so that route is refused"
        ),
        fallback=(
            "The Gilchrist-Zakrajsek credit spread in the Board's excess-bond-premium file: "
            "monthly, a different bond universe and a different construction, so a substitute "
            "construct. Its licence is the Board disclaimer's default, not read from the file"
            " -- ANNOTATED 2026-09-14 (D3b, DD46): the last clause was false when it was "
            "written. curvecast's `pit.data_rights` board publication names the "
            "excess-bond-premium file explicitly, grades it PUBLIC_DOMAIN, and records the "
            "reading as taken on 2026-09-11 by this repository's own D3a session. The licence "
            "was measured three days before a package needed it and nothing noticed. The "
            "substitute was taken at D3b; it has its own GZ_SPREAD row below"
        ),
        fallback_originator=_BOARD,
    )


SOURCE_ROWS: tuple[Source, ...] = (
    *(_gsw(tenor) for tenor in ("01", "02", "03", "05", "07", "10", "20", "30")),
    *(
        _h15(series, f"{_TREASURY_REAL}, read at the same tenor")
        for series in ("DFII5", "DFII10", "DFII30")
    ),
    *(
        # `DGS10` added at D3b (DD47). D3a left it as this package's inheritance -- "T10YIE
        # arrives as DGS10 - DFII10, and DGS10 needs a register row first" -- and the panel
        # carries both inputs and not the copyrighted series they would construct.
        _h15(series, f"{_TREASURY_NOMINAL}, read at the same tenor")
        for series in ("DGS3MO", "DGS6MO", "DGS1", "DGS2", "DGS10")
    ),
    Source(
        series="DEXUSEU",
        originator=_BOARD,
        originator_class=OriginatorClass.PUBLIC_SECTOR,
        publisher="Board H.10 Foreign Exchange Rates, via FRED",
        fred_tag=Licence.PUBLIC_DOMAIN,
        notice=Licence.PUBLIC_DOMAIN,
        derivation=Derivation.PERMITTED,
        evidence=f"{_FRED_API}; {_BOARD_DISCLAIMER}",
        fallback=(
            "The Board's own H.10 release through its Data Download Program. Same originator: "
            "survives FRED dropping the series, not the Board discontinuing it"
        ),
        fallback_originator=_BOARD,
    ),
    # DD168, 2026-09-26: the H.10 majors, hedge instruments and risk factors as `DEXUSEU` is
    # (DD139), never grammar candidates (DD120, DD138). Graded on their own tags, read the day
    # they were added, not by analogy: all six carry exactly the tags `DEXUSEU` carries.
    *(
        Source(
            series=series,
            originator=_BOARD,
            originator_class=OriginatorClass.PUBLIC_SECTOR,
            publisher="Board H.10 Foreign Exchange Rates, via FRED",
            fred_tag=Licence.PUBLIC_DOMAIN,
            notice=Licence.PUBLIC_DOMAIN,
            derivation=Derivation.PERMITTED,
            evidence=(
                "FRED API series/tags, read 2026-09-26: `cc` 'public domain: citation "
                f"requested', source `frb`, release `h10`, the tags DEXUSEU carries; {_BOARD_DISCLAIMER}"
            ),
            fallback=(
                "The Board's own H.10 release through its Data Download Program. Same originator: "
                "survives FRED dropping the series, not the Board discontinuing it"
            ),
            fallback_originator=_BOARD,
        )
        for series in ("DEXJPUS", "DEXUSUK", "DEXCAUS", "DEXSZUS", "DEXCHUS", "DEXMXUS")
    ),
    Source(
        series="T10YIE",
        originator=_ST_LOUIS,
        originator_class=OriginatorClass.PUBLIC_SECTOR,
        publisher="FRED, computed by the Federal Reserve Bank of St. Louis from DGS10 and DFII10",
        fred_tag=Licence.CITATION_REQUIRED,
        notice=Licence.CITATION_REQUIRED,
        # The only row in this register that lands in DD118's middle cell. FRED's own tag
        # asserts copyright and grants reuse with attribution; there is no third-party notice
        # behind it to read a derivation condition out of, and the copyright is on the
        # arithmetic, not on a restriction against doing arithmetic.
        derivation=Derivation.PERMITTED,
        evidence=(
            f"{_FRED_API}; no third-party notice. Arithmetic on two public-domain series "
            "carries a copyrighted tag"
        ),
        fallback=(
            "DGS10 minus DFII10, both public domain. curvecast D166 already prefers the "
            "construction on vintage coverage, 2,307 own-vintage DEV rows against 233"
        ),
        fallback_originator=_TREASURY,
    ),
    Source(
        series="VIXCLS",
        originator=_CBOE,
        originator_class=OriginatorClass.EXCHANGE,
        publisher="FRED, reprinted with Cboe's permission",
        fred_tag=Licence.CITATION_REQUIRED,
        # Regraded at D8 (X25) from the originator's words, where it had been graded from the
        # distributor's note. Cboe's terms require prior written consent for reproduction,
        # distribution and derivative works alike, which is REDISTRIBUTION_PROHIBITED.
        notice=Licence.REDISTRIBUTION_PROHIBITED,
        # Read at DD121 from Cboe's own terms, not from FRED's reprint note: "You may not
        # otherwise ... create a derivative work (for example, a financial product, service or
        # index) from, use to verify or correct other data or information". Refused on either
        # axis alone, and since D8 each axis says so from the originator's words.
        derivation=Derivation.PROHIBITED,
        evidence=(
            f"{_FRED_API}; the notes assert Cboe's copyright and that FRED reprints with "
            "permission, which grants nothing further downstream. Cboe's own terms, read at "
            "DD121, require written consent to reproduce, distribute or derive"
        ),
        fallback=None,
        fallback_originator=None,
        no_fallback_reason=(
            "Withdrawn at D8 (X25). The fallback was Cboe's own VIX_History.csv, chosen "
            "because its page states no redistribution terms. That premise is false: the page "
            "states none inline and links to Cboe's Use of Content and Terms & Conditions, "
            "which bind and forbid derivation. A fallback on the same originator's terms "
            "mends nothing, and any other copy of VIX is Cboe's number under the same terms"
        ),
    ),
    _moodys_spread("BAA10Y", "Baa"),
    _moodys_spread("AAA10Y", "Aaa"),
    Source(
        series="GZ_SPREAD",
        originator=_BOARD,
        originator_class=OriginatorClass.PUBLIC_SECTOR,
        publisher=(
            "The Board's excess-bond-premium file, published with the Gilchrist-Zakrajsek "
            "FEDS Note and read through curvecast's Block J snapshot, publication-clamped"
        ),
        fred_tag=None,
        notice=Licence.PUBLIC_DOMAIN,
        derivation=Derivation.PERMITTED,
        evidence=(
            "curvecast's `pit.data_rights` board publication, whose `read_from` names "
            "federalreserve.gov/disclaimer.htm and the excess-bond-premium file explicitly, "
            "read 2026-09-11 in this repository's D3a session 0.8. Read from the file's own "
            "publisher, not assumed from the disclaimer's default"
        ),
        fallback=None,
        fallback_originator=None,
        no_fallback_reason=(
            "There is no free daily alternative left to name. This row IS the fallback behind "
            "BAA10Y and AAA10Y, whose licence forbids the fixture, so naming them here would "
            "close a circle rather than open a route -- and ICE BofA's option-adjusted "
            "spreads, the obvious third answer, are the withdrawal this register was built to "
            "record. A credit spread on a fourth bond universe has not been measured, and a "
            "package that needs one measures it before it reads a row of it"
        ),
    ),
    Source(
        series="DE_ZERO_10Y",
        originator="A German zero curve; Deutsche Bundesbank is the candidate, not yet measured",
        originator_class=OriginatorClass.PUBLIC_SECTOR,
        publisher="Not chosen",
        fred_tag=None,
        notice=Licence.UNMEASURED,
        # A5 s3 reads the ESCB policy as RESULTS_ONLY in shape, but this row's publisher is
        # not chosen, so no words have been read for THIS source and the grade stays unmeasured.
        derivation=Derivation.UNMEASURED,
        evidence="None. Its only leg is declined (DD126)",
        fallback=None,
        fallback_originator=None,
        no_fallback_reason=(
            "Declined with the cross-market leg (DD126). No package reads it, so no publisher is "
            "chosen and no licence is read for one"
        ),
    ),
)

#: The register keyed by series. C36 asserts no series was written twice.
SOURCES: dict[str, Source] = {row.series: row for row in SOURCE_ROWS}
