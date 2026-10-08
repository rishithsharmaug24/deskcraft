"""The plan, held as data. D3a, decisions DD30-DD33, bars C32-C35.

Two registers live here, and both exist because a rule that lives only in prose is the one
constraint in this repo held together by memory.

**The claims register.** `CLAIMS` is `docs/BUILD_ORDER_D3_D16.md` §5 as data: every
pre-registered claim, the package that scores it, the verdict it predicted, and its status.
It is checked from four directions, none of which is a matter of anyone remembering:

- it agrees with §5, parsed, so the table a reader sees and the rows a gate enforces cannot
  drift (C32);
- every live claim is scored by a core package, every annexed one by an annex package, and a
  withdrawn claim names what replaced it (C33);
- **a verdict is recorded if and only if its scorer has closed** (C34). The build order asked
  for half of that -- *the gate fails if the scorer has landed and the claim is unscored* --
  and the other half, a verdict for a claim whose scorer has not landed, is a fabricated
  result. Closure is read from the scorer's pre-commit document existing, never declared here;
- the numbered ids are contiguous except for the gaps `NUMBERING_GAPS` declares (C33), so a
  claim cannot be deleted from both places in one commit and leave no trace.

`verdict` is `None` on every row today. The first package that sets one is D6, for H3, and its
own suite is red from the moment its pre-commit document is written until it does. That
friction is the register working.

**ANNOTATED 2026-09-15 (D6).** It worked exactly as written. `PRECOMMIT_deskcraft_d6_view_language.md`
landed first and C34 went red on the words *"H3: D6 has landed and the claim is unscored"*; the
suite stayed red across two runs, through a rename C10 forced, until the verdict below was set
from the measurement rather than from the prediction. **H3 is `PASS`, as §5 predicted** -- the
reference book's dominant loading is `LEVEL`, positive, against a view compiled from the thesis
text before any loading existed. The sentence above is left standing rather than corrected to
the past tense: it is the only remaining record of what this register felt like before it held
a verdict, and D6's §6.4 records how thin the PASS is (a 5.0% margin over the second factor).

**The package budget.** `PACKAGE_BUDGET` is the size of the frozen core, read against §4's
order table by C35 as an **equality** (DD33) -- stricter than `AMENDMENT_A1` §6.2's *exceeds*,
because a package that leaves the core without going to the annex is a scope change exactly as
silent as one that joins it.

Nothing in this module opens a file. The parsing, the closure check and the parity check are
bars; what is here is what they check against.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

__all__ = [
    "CLAIMS",
    "NUMBERING_GAPS",
    "PACKAGE_BUDGET",
    "Claim",
    "ClaimStatus",
    "Verdict",
    "claim_number",
]

#: Core packages in `BUILD_ORDER_D3_D16.md` §4, frozen 2026-09-08 by `AMENDMENT_A1` §6.
#: An equality, not a ceiling (DD33). Adding a package, or moving one to the annex, edits this
#: constant in the same commit -- which is the point: the change is a line in a diff.
PACKAGE_BUDGET = 21

#: Numbers in the H sequence that no claim has ever held. `H10` appears in no document in
#: this repository's history -- `git log -S"H10" --all` returns nothing -- and the gap sits
#: where the unnumbered `SCENARIO_SIGNS` row sits. Recorded rather than renumbered (DD32):
#: H11-H17 are already cited by the amendment, the research memo and both abstracts.
NUMBERING_GAPS = frozenset({10})


def _number_and_suffix(identifier: str, prefix: str) -> int | None:
    """`H12a` -> 12 for prefix `H`; `D7b` -> 7 for prefix `D`; anything else -> None.

    String methods rather than a regular expression, so this module adds no import root to
    the engine's census (C27) for a check that is four comparisons long.
    """
    if not identifier.startswith(prefix):
        return None
    body = identifier[len(prefix) :]
    if body and body[-1].isalpha() and body[-1].islower():
        body = body[:-1]
    return int(body) if body.isascii() and body.isdigit() else None


class ClaimStatus(StrEnum):
    """Whether a claim is still scored, and if not, why not."""

    #: Scored by a core package.
    ACTIVE = "ACTIVE"
    #: Moved out of the frozen core with the package that scores it; may be built only after
    #: the core closes (`AMENDMENT_A1` §6.3).
    ANNEXED = "ANNEXED"
    #: Replaced as written. Carries its successors, so the replacement is traceable.
    WITHDRAWN = "WITHDRAWN"


class Verdict(StrEnum):
    """A scored outcome. `NOT_PERFORMED` is curvecast's H0-D precedent: refused, and reported.

    `REPORTED` arrived at D10 (DD153). A claim registered with no prediction and no bar -- H8b,
    and `SCENARIO_SIGNS` -- is scored by being reported. PASS would read as a prediction coming
    true, and there was none. It is the only verdict such a claim may carry, and a claim with a
    prediction may never carry it.
    """

    PASS = "PASS"
    FAIL = "FAIL"
    NOT_PERFORMED = "NOT_PERFORMED"
    REPORTED = "REPORTED"


def claim_number(claim_id: str) -> int | None:
    """The numeric part of an `H` id, or `None` for a named claim like `SCENARIO_SIGNS`."""
    return _number_and_suffix(claim_id, "H")


@dataclass(frozen=True)
class Claim:
    """One pre-registered claim, the package that scores it, and what was predicted."""

    claim_id: str
    statement: str
    scorer: str
    #: What the register predicted before any run. `None` where §5 records no prediction.
    predicted: Verdict | None
    status: ClaimStatus = ClaimStatus.ACTIVE
    #: For a withdrawn claim, the ids that replaced it.
    successors: tuple[str, ...] = ()
    #: Set by the scorer's own commit, and by nothing else (C34).
    verdict: Verdict | None = None

    def __post_init__(self) -> None:
        if claim_number(self.claim_id) is None and not self.claim_id.isupper():
            raise ValueError(f"{self.claim_id!r} is neither an H id nor a named claim")
        if _number_and_suffix(self.scorer, "D") is None:
            raise ValueError(f"{self.claim_id}: scorer {self.scorer!r} is not a package id")
        if self.predicted is Verdict.NOT_PERFORMED:
            raise ValueError(f"{self.claim_id}: a refusal is an outcome, not a prediction")
        if (self.status is ClaimStatus.WITHDRAWN) != bool(self.successors):
            raise ValueError(
                f"{self.claim_id}: a claim names successors if and only if it is withdrawn"
            )
        if self.status is not ClaimStatus.ACTIVE and self.verdict is not None:
            raise ValueError(f"{self.claim_id}: only a live claim can carry a verdict")
        if self.predicted is Verdict.REPORTED:
            raise ValueError(f"{self.claim_id}: a report is an outcome, not a prediction")
        if self.verdict is not None and (self.verdict is Verdict.REPORTED) != (self.predicted is None):
            raise ValueError(
                f"{self.claim_id}: REPORTED is the verdict of a claim with no prediction, and only "
                "of one (DD153)"
            )


_PASS, _FAIL = Verdict.PASS, Verdict.FAIL

CLAIMS: tuple[Claim, ...] = (
    #: Scored by D14 2026-09-28 on the out-of-sample read: Kupiec p 0.191 at 97.5% and 0.219 at
    #: 99%, Acerbi-Szekely Z2 p 0.538, over 2,736 sessions. A correctly specified model misses
    #: this conjunction about 11.5% of the time, which is reported beside it.
    Claim("H1", "Risk model correctly calibrated", "D14", _PASS, verdict=_PASS),
    #: Scored by D14 2026-09-28, as predicted: Christoffersen independence p 0.0013 at 97.5%.
    Claim("H2", "Exceptions independent", "D14", _FAIL, verdict=_FAIL),
    Claim(
        "H3",
        "View fidelity: the book loads on the view's factor",
        "D6",
        _PASS,
        verdict=_PASS,
    ),
    Claim(
        "H4",
        "Six-leg US book has ENB < 3.0; the book is neither US-only nor priceable, and ENB "
        "is undefined without a basis",
        "D10",
        None,
        status=ClaimStatus.WITHDRAWN,
        successors=("H4a", "H4b"),
    ),
    #: Scored by D10 2026-09-25: Roy-Vetterli rank 2.4103 on the four legs' P&L covariance.
    Claim(
        "H4a",
        "US_CASH_BOOK's four priceable legs have Roy-Vetterli effective rank < 3.0",
        "D10",
        _PASS,
        verdict=_PASS,
    ),
    #: Scored by D10 2026-09-25, and it could not have failed: the whitening rung returns the
    #: leg count, 4.0, for any covariance. Min-torsion, the rung that can move, is 2.6567.
    Claim(
        "H4b",
        "The same book and covariance exceed 3.0 under at least one other basis of D10's ladder",
        "D10",
        _PASS,
        verdict=_PASS,
    ),
    #: Scored by D15 2026-09-28, as predicted and uninformative: -0.012 against 1/N at p 0.82,
    #: with power 0.112 at the plausible effect on the record's own standard error.
    Claim("H5", "ES-constrained sizing beats 1/N on Sharpe", "D15", _FAIL, verdict=_FAIL),
    #: Scored by D12 2026-09-28 against its prediction: 0.658 of gross under NBER_2020's
    #: correlations and 0.027 under RATES_2022's, where both had to exceed 0.20 (DD167).
    Claim("H6", "Crisis correlations change sizing > 20% of gross", "D12", _PASS, verdict=_FAIL),
    #: Scored by D12 2026-09-28 against its prediction: the size of RATES_2022's P&L, a gain for a
    #: short-duration book, is 3.3% above the three-factor quantile and NBER_2020's is 82% of it,
    #: where both had to exceed it (DD167).
    Claim("H7", "3-factor Monte Carlo understates crisis P&L", "D12", _PASS, verdict=_FAIL),
    Claim(
        "H8",
        "Generated book beats hand-built on ENB; both < 3.0; the level clause cannot fail, "
        "because ENB <= the leg count and H9 predicts three or four legs",
        "D10",
        None,
        status=ClaimStatus.WITHDRAWN,
        successors=("H8a", "H8b"),
    ),
    #: Scored by D10 2026-09-25 against its prediction: the generated headline book ranks 1.0898
    #: against the hand-built book's 2.4103 on one covariance. Fidelity to a one-factor view and
    #: diversification pull opposite ways, so the generator built what it was asked for.
    Claim(
        "H8a",
        "The generated book beats the hand-built US_CASH_BOOK on Roy-Vetterli effective rank, "
        "both in the same basis on the same covariance",
        "D10",
        _PASS,
        verdict=_FAIL,
    ),
    #: Reported by D10 2026-09-25 (DD153): 0.6026 hand-built, 0.5449 generated, Roy-Vetterli.
    Claim(
        "H8b",
        "ENB divided by leg count, reported for both books in each basis of D10's ladder",
        "D10",
        None,
        verdict=Verdict.REPORTED,
    ),
    #: Scored by D7b 2026-09-16. PASS at all eight cells of §3.5's ladder -- 0, 1 or 2 legs --
    #: and the predicted 3-4 is wrong on the low side at every one of them. The margin is a
    #: property of the grid and not of the structure: the ladder's four rungs are view
    #: magnitudes between a quarter of a basis point and two, and at ten the count is six, which
    #: is the threshold. Six is also a ceiling no cost model can pass, because the greedy runs
    #: out of fidelity there rather than out of money. X15 discharged in the pre-commit's §4.
    Claim(
        "H9",
        "Cost-aware stopping terminates below six legs",
        "D7b",
        _PASS,
        verdict=_PASS,
    ),
    #: Reported by D12 2026-09-28 (DD153): US_CASH_BOOK's leg signs are -, -, -, + in NBER_2020
    #: and +, +, -, + in RATES_2022 (2y, 10y, breakeven, euro), with no window classified.
    Claim(
        "SCENARIO_SIGNS",
        "SCENARIO_SIGNS reproduces on dated windows; under-determined, and D12 replaces it",
        "D12",
        None,
        verdict=Verdict.REPORTED,
    ),
    #: Scored by D17 2026-09-27 on equity: 24 of 32, 0.750, Clopper-Pearson [0.566, 0.885]. Median k
    #: -9.17. Twenty-two of the 24 count because k <= 0, the market's own rate and dollar loadings
    #: (DD207); on the 18 firms with a currency or crude leg it is 11 of 18. Cash flow, beside: FAIL.
    Claim(
        "H11",
        "A hedge sized off disclosed exposure over-hedges vs one sized off measured exposure, "
        "by > 30%, for >= 70% of the cohort",
        "D17",
        _PASS,
        verdict=_PASS,
    ),
    #: Scored by D21 2026-09-29, as predicted: the forward keeps at least 90% of the best admitted
    #: alternative's variance reduction on all seven eligible firms, median capture 1.300.
    Claim(
        "H12a",
        "The cheap linear structure captures >= 90% of the complex one's variance reduction",
        "D21",
        _PASS,
        verdict=_PASS,
    ),
    Claim(
        "H12b",
        "The markup gap against the 424B2 population",
        "D20",
        None,
        status=ClaimStatus.ANNEXED,
    ),
    #: Scored by D18 2026-09-26: 3 of 3 case clients, at every rung of both volatility ladders.
    #: It could not have been otherwise, and D18's §3 said so before the run: put-call parity makes
    #: the ratio forward the only structure on the menu that beats the forward at zero premium, at
    #: any volatility. What it shows is that the KIKO pick belongs to the objective, not the market.
    Claim(
        "H13",
        "Unconstrained cost minimisation selects a leverage > 1 structure the gate refuses",
        "D18",
        _PASS,
        verdict=_PASS,
    ),
    Claim(
        "H14",
        "OOS R^2 < 0.5 and < half its in-sample value; the first clause is implied by the second",
        "D21",
        None,
        status=ClaimStatus.WITHDRAWN,
        successors=("H14a", "H14b"),
    ),
    #: Scored by D21 2026-09-29, as predicted and a claim the record could not fail in practice
    #: (DD232): 32 of 32 evaluable firms, every one already below 0.5 in sample.
    Claim(
        "H14a",
        "OOS Ederington hedge-effectiveness R^2 < 0.5, for >= 70% of the cohort",
        "D21",
        _PASS,
        verdict=_PASS,
    ),
    #: Scored by D21 2026-09-29 against its prediction, and carried by noise on the rates-only firms
    #: (DD232): 21 of 32, 0.656, where 0.70 was needed. 13 of the 14 rates-only firms count; on the
    #: resolved subset, 10 of 18.
    Claim(
        "H14b",
        "OOS Ederington R^2 < half its in-sample value, for >= 70% of the cohort",
        "D21",
        _PASS,
        verdict=_FAIL,
    ),
    #: Not performed, scored by D22 2026-09-28 and refused by name (DD180): the admitted daily
    #: equity route serves the last 100 sessions only, so no return reaches the fit years.
    Claim(
        "H15",
        "Crisis-conditional hedge effectiveness is under half the unconditional value, "
        "for >= 60% of the cohort",
        "D22",
        _PASS,
        verdict=Verdict.NOT_PERFORMED,
    ),
    #: Scored by D22 2026-09-28, as predicted and as reported before the read (DD231): four of six
    #: client-windows exceed 25%. ExxonMobil 541% and 1,196%, GE 62% and 404%, AT&T 0%.
    Claim(
        "H16",
        "Peak hedge-leg mark-to-market drawdown exceeds 25% of trailing operating cash flow "
        "for >= 1 case client; an existence claim",
        "D22",
        _PASS,
        verdict=_PASS,
    ),
    #: Scored by D17 2026-09-27 on equity, against its prediction: the currency and crude median is
    #: 1.55, and the rates median is +inf because 22 of 25 rates k are negative, so neither half
    #: holds. Currency alone is 0.130, measured far above stated (DD207). Cash flow, beside: PASS.
    Claim(
        "H17",
        "Structural-to-measured exposure ratio has cohort median > 2.0 for FX and commodity "
        "and < 1.5 for rates",
        "D17",
        _PASS,
        verdict=_FAIL,
    ),
)
