"""Dated certificates of what each upstream comparison found, and of nothing else.

**This is not a copy of curvecast or of meip** (DD69). Nine bars in this suite re-derive a
value here and compare it against one read next door, and all nine went silent on a machine
without the sibling repositories -- which is to say the bars that make this repository's claims
checkable were exactly the bars a reviewer could not run. The obvious repair is to commit the
upstream values. For most of these that would be wrong, and for one it would be circular:

C59 asserts that deskcraft's committed panel and curvecast's fixture are **the same bytes**. A
snapshot made by copying curvecast's fixture would have C59 compare deskcraft's panel against a
copy of deskcraft's panel -- 7,044 rows duplicated in order to assert nothing.

So each entry below records **this repository's side** of a comparison, on a date, with the
upstream commit it agreed with named. The claim an entry makes is:

    on 2026-09-15, with curvecast at 7727ee2 and meip at c1e383e, deskcraft's side of this
    comparison reduced to this value, and the comparison passed.

Off-machine, a bar re-derives its own side and checks it against the certificate. That catches
every drift on the side `git archive HEAD` actually contains.

**What a certificate cannot catch, said plainly:** upstream moving afterwards. That is not a gap
this file could close -- a reviewer holding only the archive cannot see curvecast either. Watching
upstream for change is C7, C9 and C37's job, those three are permanently conditional on purpose
(DD70), and freezing their subject into a fixture is precisely what would defeat them.

Regeneration is by hand, because a `scripts/` directory here is unconstructible (DD58). Each
bar's provenance half is what says the certificate has gone stale, and it says so loudly.
"""

from __future__ import annotations

import hashlib

#: The day every value below was measured, and the sibling commits it was measured against.
#: Named rather than implied: a certificate with no date is a constant with no provenance.
GENERATED = "2026-09-15"
CURVECAST_COMMIT = "7727ee2"
MEIP_COMMIT = "c1e383e"


def digest(*parts: object) -> str:
    """A stable hash of `repr`, shared by the certificate and by every bar that reads it.

    Shared rather than copied on purpose. A bar and its certificate computing a hash two
    slightly different ways is the failure that would make every entry here unfalsifiable, and
    it is the kind of difference that survives review because both sides look right.

    `repr` round-trips a float exactly in CPython, so a digest over floats is an equality and
    not a tolerance -- which is what C50 and C60 need, for the reason D4's C50 gives: a
    tolerance would pass a reordered summation, and a reordered summation is how a restatement
    stops being one.
    """
    accumulator = hashlib.sha256()
    for part in parts:
        accumulator.update(repr(part).encode("utf-8"))
        accumulator.update(b"\x00")
    return accumulator.hexdigest()


# ---------------------------------------------------------------------------
# Literals -- small enough to read, so they are readable rather than hashed
# ---------------------------------------------------------------------------

#: C14, C39. Series with a measured archive floor, plus the pinned GSW zero columns: 34 + 8.
#: curvecast's D5 took FLOORS from 30 to 34 at `e78d2f7`, and `graded_universe()` returned the
#: four new rows with no edit here. That is the arrangement working, and it is also the reason
#: this tuple is checked against the live parse whenever curvecast is present: a hardcoded copy
#: that nothing compares is a copy that goes stale silently.
GRADED_UNIVERSE = (
    "AAA10Y",
    "BAA10Y",
    "CORESTICKM158SFRBATL",
    "CORESTICKM159SFRBATL",
    "CPIAUCSL",
    "CPILFESL",
    "DCOILWTICO",
    "DEXUSEU",
    "DFII10",
    "DFII30",
    "DFII5",
    "DGS1",
    "DGS10",
    "DGS2",
    "DGS30",
    "DGS3MO",
    "DGS5",
    "DGS6MO",
    "DTWEXB",
    "DTWEXBGS",
    "GASREGW",
    "MEDCPIM158SFRBCLE",
    "SVENY01",
    "SVENY02",
    "SVENY03",
    "SVENY05",
    "SVENY07",
    "SVENY10",
    "SVENY20",
    "SVENY30",
    "T10YIE",
    "THREEFY10",
    "THREEFY2",
    "THREEFY5",
    "THREEFYTP10",
    "THREEFYTP2",
    "THREEFYTP5",
    "TREAST",
    "TRMMEANCPIM158SFRBCLE",
    "VIXCLS",
    "WSHOBL",
    "WSHONBNL",
)

#: C31. curvecast's `pit/seal.py`, transcribed on the date above. The first generator run used
#: 1990-01-02 from memory, which turned VINTAGE_COLLAPSE red before any of this was committed --
#: the certificate catching an error in its own making, which is the strongest evidence
#: available that it is not decorative.
DEV_BOUNDS = {"DEV_START": (1988, 1, 1), "DEV_END": (2014, 12, 31)}

#: C49. The Board's own words, three lines above the data in `feds200628.csv`. All four
#: `XX` rows are kept, not only the two the package turns on: the pair that is NOT read is what
#: shows the header block was parsed rather than the answer written down.
GSW_CONVENTIONS = {
    "SVENYXX": "Continuously Compounded",
    "SVENPYXX": "Coupon-Equivalent",
    "SVENFXX": "Continuously Compounded",
    "SVEN1FXX": "Coupon-Equivalent",
}

# ---------------------------------------------------------------------------
# Digests -- too large to read, so they are hashed rather than duplicated
# ---------------------------------------------------------------------------

#: C42. The 7,044 GSW DEV session dates, in order, as curvecast publishes them.
SESSION_GRID = "32c976e7afd259a63b522a982a9a555eec5008ccf665eea3c8fbf15b60726e20"

#: C59. Every `SVENY` field of every session, keyed by date and left exactly as written --
#: blanks included, because a basis fitted here and one fitted there are comparable only if the
#: sample is the same sample, and which sessions published nothing is part of the sample.
GSW_BYTES = "17987f5b6e2cf5640039e6ec73c8e2f0a7841df542ed9c96105853ccfcbdfa20"

#: C44. The DEV_END-vintage collapse of curvecast's three vintage files, over the nine series
#: this panel carries. The five rows the filter refuses are named in `test_data_panel.py` and
#: are deliberately NOT repeated here: "five rows were dropped" and "these five rows were
#: dropped" are different claims, and the module that makes the second already makes it.
VINTAGE_COLLAPSE = "d941cc47478055e3832c816e897cd4659562c850728a96e5740ee15f67978866"

#: C50. MEIP's `par_bond_duration_convexity` over the 72-point grid, both returned values.
PAR_BOND_GRID = "9fab8367c1bb4972784d5478e44ebab9def6c1d7dd61ea42480db7438c053125"

#: C60. curvecast's `_pca`, run from its own bytes, over both matrices C60 uses -- the real DEV
#: sample and the seeded synthetic one -- eigenvalues, eigenvectors and covariance for each.
#: Hashed through `<f8` so byte order is pinned rather than inherited from the host.
PCA_OUTPUT = "c7c6892dde719f567acb8b6cc9af6563cafced348b03e214c5771212fe53793c"

#: C179. optcraft's `price` over C179's 162-point grid, Garman-Kohlhagen, Black-76 and Bachelier,
#: calls and puts. Measured 2026-09-26 against optcraft `ae7128f`; `GENERATED` above is the date
#: of the entries before this one, none of which depended on optcraft.
OPTION_VALUES = "1f8d92352d50e2f614210bcc9038d2f4c1f5d32162101a2f0ee6636e51b0c46c"

#: Every entry a bar is expected to read. C75 holds this at equality against the module's own
#: public names, so an entry that stops being read cannot sit here looking like a guarantee.
ENTRIES = (
    "GRADED_UNIVERSE",
    "DEV_BOUNDS",
    "GSW_CONVENTIONS",
    "SESSION_GRID",
    "GSW_BYTES",
    "VINTAGE_COLLAPSE",
    "PAR_BOND_GRID",
    "PCA_OUTPUT",
    "OPTION_VALUES",
)
