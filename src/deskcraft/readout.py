"""D16: the readout. Paper 1's claims table, its tally and its figures, rendered from the registers.

`PRECOMMIT_deskcraft_d16_readout_and_paper1.md` (DD225-DD230). Landed 2026-09-28, after the
out-of-sample read, in the commit that rendered the paper on its verdicts and tagged CP-2.

**Rendered, not written** (DD226). The claims table is built from `registers.CLAIMS`, so the paper
cannot carry a verdict the register does not hold, and a verdict the read adds turns the paper red
until it is rendered again. **Every figure is recorded somewhere else first** (DD227): `FIGURES`
names the document each number came from, and a bar finds it there. Nothing here opens a file or
computes a result; the packages did that.
"""

from __future__ import annotations

from dataclasses import dataclass

from deskcraft.registers import CLAIMS, Claim, ClaimStatus, Verdict

__all__ = [
    "AWAITING",
    "BLOCK_BEGIN",
    "BLOCK_END",
    "FIGURES",
    "FIGURES_TWO",
    "PAPER1_LAST_PACKAGE",
    "PAPER2_BLOCK_BEGIN",
    "PAPER2_BLOCK_END",
    "PAPER2_PACKAGES",
    "READERS",
    "Figure",
    "Tally",
    "claims_table",
    "paper_one_claims",
    "paper_two_claims",
    "paper_two_tally_sentence",
    "tally",
    "tally_sentence",
]

#: `AMENDMENT_A1` §7.2: Paper 1 is D3a to D16, and its hypotheses are the claims those packages score.
PAPER1_LAST_PACKAGE = 16
#: The packages whose verdicts only the out-of-sample read can produce: the joint registration's
#: four and D21 (DD199). D21 and D22 joined with Paper 2's render (DD241); Paper 1 has no claim of
#: theirs, so its table and tally do not move.
READERS = frozenset({"D12", "D14", "D15", "D21", "D22"})
#: `AMENDMENT_A1` §7.2: Paper 2 is D17, D18, D21 and D22, and its hypotheses are theirs (DD241).
PAPER2_PACKAGES = frozenset({"D17", "D18", "D21", "D22"})
AWAITING = "awaiting the read"
BLOCK_BEGIN = "<!-- claims table: rendered by deskcraft.readout.claims_table() -->"
BLOCK_END = "<!-- end of the rendered claims table -->"
PAPER2_BLOCK_BEGIN = "<!-- paper 2 claims table: rendered by deskcraft.readout.claims_table(paper_two_claims()) -->"
PAPER2_BLOCK_END = "<!-- end of the rendered paper 2 claims table -->"


def _package_number(scorer: str) -> int:
    digits = "".join(ch for ch in scorer[1:] if ch.isdigit())
    return int(digits)


def paper_one_claims() -> tuple[Claim, ...]:
    """Every claim a Paper 1 package scores, in the register's order."""
    return tuple(c for c in CLAIMS if _package_number(c.scorer) <= PAPER1_LAST_PACKAGE)


def paper_two_claims() -> tuple[Claim, ...]:
    """Every claim a Paper 2 package scores, in the register's order (DD241)."""
    return tuple(c for c in CLAIMS if c.scorer in PAPER2_PACKAGES)


def _verdict(claim: Claim) -> str:
    if claim.status is ClaimStatus.WITHDRAWN:
        return "withdrawn: " + ", ".join(claim.successors)
    if claim.verdict is not None:
        return f"**{claim.verdict.value}**"
    if claim.scorer in READERS:
        return AWAITING
    return "unscored"


def _predicted(claim: Claim) -> str:
    return claim.predicted.value if claim.predicted is not None else "none"


def claims_table(claims: tuple[Claim, ...] | None = None) -> str:
    """DD226: Paper 1's rows of `CLAIMS` as a markdown table, or the rows given (DD241)."""
    lines = ["| Claim | Statement | Scored by | Predicted | Verdict |", "|---|---|---|---|---|"]
    for claim in paper_one_claims() if claims is None else claims:
        statement = claim.statement.replace("|", "/")
        lines.append(f"| {claim.claim_id} | {statement} | {claim.scorer} | {_predicted(claim)} | {_verdict(claim)} |")
    return "\n".join(lines)


@dataclass(frozen=True)
class Tally:
    """Paper 1's live rows, and what has become of each so far."""

    live: int
    scored: int
    as_predicted: int
    against: int
    reported: int
    awaiting: int
    #: Refused by name (`Verdict.NOT_PERFORMED`): scored, and neither as nor against a prediction.
    not_performed: int = 0


def tally(claims: tuple[Claim, ...] | None = None) -> Tally:
    live = [c for c in (paper_one_claims() if claims is None else claims) if c.status is ClaimStatus.ACTIVE]
    scored = [c for c in live if c.verdict is not None]
    predicted = [c for c in scored if c.predicted is not None and c.verdict is not Verdict.NOT_PERFORMED]
    return Tally(
        live=len(live),
        scored=len(scored),
        as_predicted=sum(c.verdict is c.predicted for c in predicted),
        against=sum(c.verdict is not c.predicted for c in predicted),
        reported=sum(c.verdict is Verdict.REPORTED for c in scored),
        awaiting=sum(c.verdict is None and c.scorer in READERS for c in live),
        not_performed=sum(c.verdict is Verdict.NOT_PERFORMED for c in scored),
    )


_NUMBER_WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                 "ten", "eleven", "twelve")


def _word(n: int) -> str:
    return _NUMBER_WORDS[n] if n < len(_NUMBER_WORDS) else str(n)


def tally_sentence() -> str:
    """The abstract's count, as the register stands.

    Before the read it ended *"Six await the out-of-sample read."* With nothing awaiting, that
    clause would have read *"No await"*, so it is dropped rather than rendered, and a count of
    more than one against is written in the plural. Found by the landing render.
    """
    t = tally()
    scored = f"All {_word(t.scored)}" if t.scored == t.live else _word(t.scored).capitalize()
    against = "against its prediction" if t.against == 1 else "against their predictions"
    sentence = (
        f"Paper 1's register holds {_word(t.live)} live rows: the nine hypotheses, two of them split in "
        f"two, and `SCENARIO_SIGNS`. {scored} are scored: {_word(t.as_predicted)} as predicted, "
        f"{_word(t.against)} {against}, and {_word(t.reported)} reported, having no prediction to meet."
    )
    if t.awaiting:
        sentence += f" {_word(t.awaiting).capitalize()} await the out-of-sample read."
    return sentence


def paper_two_tally_sentence() -> str:
    """Paper 2's count, as the register stands (DD241)."""
    t = tally(paper_two_claims())
    scored = f"All {_word(t.scored)}" if t.scored == t.live else _word(t.scored).capitalize()
    against = "against its prediction" if t.against == 1 else "against their predictions"
    sentence = (
        f"Paper 2's register holds {_word(t.live)} live rows, H14 having been split in two before any "
        f"number existed. {scored} are scored: {_word(t.as_predicted)} as predicted, {_word(t.against)} "
        f"{against}, and {_word(t.not_performed)} not performed, refused by name."
    )
    if t.awaiting:
        sentence += f" {_word(t.awaiting).capitalize()} await the out-of-sample read."
    return sentence


@dataclass(frozen=True)
class Figure:
    """A number the paper quotes, as the paper writes it, and the document that recorded it."""

    text: str
    source: str
    what: str


#: DD227. Each figure is checked in its source document and in the paper.
FIGURES: tuple[Figure, ...] = (
    Figure("0.906494022", "PRECOMMIT_deskcraft_d7b_leg_generator.md", "the grammar's saturated cosine (DD138)"),
    Figure("46,989.92", "PRECOMMIT_deskcraft_d6_view_language.md", "H3: the reference book's LEVEL loading per basis point"),
    Figure("4.991%", "PRECOMMIT_deskcraft_d6_view_language.md", "H3: LEVEL's lead over the second term"),
    Figure("2.4103", "PRECOMMIT_deskcraft_d10_effective_bets.md", "H4a: Roy-Vetterli effective rank of US_CASH_BOOK"),
    Figure("2.6567", "PRECOMMIT_deskcraft_d10_effective_bets.md", "H4b: the minimum-torsion rung"),
    Figure("1.0898", "PRECOMMIT_deskcraft_d10_effective_bets.md", "H8a: the generated book's effective rank"),
    Figure("0.6026", "PRECOMMIT_deskcraft_d10_effective_bets.md", "H8b: the hand-built book's rank over its leg count"),
    Figure("0.5449", "PRECOMMIT_deskcraft_d10_effective_bets.md", "H8b: the generated book's"),
    Figure("0, 1 or 2", "PRECOMMIT_deskcraft_d7b_leg_generator.md", "H9: the leg count at the eight cells"),
    Figure("47.7%", "PRECOMMIT_deskcraft_d9_component_risk.md", "the euro leg's share of US_CASH_BOOK's ES"),
    Figure("1,946,957", "PRECOMMIT_deskcraft_d9_component_risk.md", "US_CASH_BOOK's Gaussian ES at 97.5%"),
    Figure("4.0% more view per unit of budget than 1/N", "PRECOMMIT_deskcraft_d11_sizing.md", "the optimiser against 1/N"),
    Figure("2.3378", "PRECOMMIT_deskcraft_d13_reverse_stress.md", "the budget breach on the sample covariance"),
    Figure("1.5455", "PRECOMMIT_deskcraft_d13_reverse_stress.md", "US_CASH_BOOK's budget loss in 2007-09 sigmas"),
    Figure("0.6056", "PRECOMMIT_deskcraft_d13_reverse_stress.md", "the euro's correlation with the rates legs at construction"),
    Figure("0.668 / 0.991 / 1.000", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "Kupiec's power at 99%"),
    Figure("11.5%", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H1's size"),
    Figure("0.007 / 0.214 / 0.040", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H6's change in the DEV windows"),
    Figure("power of 8%", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H5's power at the plausible effect"),
    # The read, 2026-09-28: the joint registration's section 13.
    Figure("2,736", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "the sessions carrying every series the tested books hold"),
    Figure("0.647 / 0.990 / 1.000", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "Kupiec's power at 99% on those sessions"),
    Figure("0.191", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H1: Kupiec p at 97.5%"),
    Figure("0.219", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H1: Kupiec p at 99%"),
    Figure("0.538", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H1: Acerbi-Szekely Z2 p"),
    Figure("0.0013", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H2: Christoffersen independence p at 97.5%"),
    Figure("p 0.82", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H5: the Sharpe difference against 1/N"),
    Figure("0.154", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H5: the minimum detectable difference against 1/N"),
    Figure("0.017", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "the ES-constrained book's Deflated Sharpe"),
    Figure("+0.068", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "G, view per unit of realised ES, no verdict"),
    Figure("65.8%", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H6: the sizing change in NBER_2020"),
    Figure("2.7%", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H6: the sizing change in RATES_2022"),
    Figure("3.3%", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H7: RATES_2022 above the three-factor quantile"),
    Figure("82%", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H7: NBER_2020 as a share of the quantile"),
)

#: DD241. Paper 2's figures, each checked in its source document and in the paper (C222).
FIGURES_TWO: tuple[Figure, ...] = (
    Figure("24 of 32", "PRECOMMIT_deskcraft_d17_exposure_extractor.md", "H11: firms counted, of the evaluable"),
    Figure("0.750", "PRECOMMIT_deskcraft_d17_exposure_extractor.md", "H11: the share"),
    Figure("−9.17", "PRECOMMIT_deskcraft_d17_exposure_extractor.md", "H11: the median k"),
    Figure("0.611", "PRECOMMIT_deskcraft_d17_exposure_extractor.md", "H11 beside: the share on firms with a currency or crude leg"),
    Figure("0.625", "PRECOMMIT_deskcraft_d17_exposure_extractor.md", "H11 beside: the share on operating cash flow"),
    Figure("1.55", "PRECOMMIT_deskcraft_d17_exposure_extractor.md", "H17: the currency and crude median ratio"),
    Figure("22 of 25", "PRECOMMIT_deskcraft_d17_exposure_extractor.md", "H17: rates k below zero"),
    Figure("0.130", "PRECOMMIT_deskcraft_d17_exposure_extractor.md", "H17: the currency median ratio"),
    Figure("below 0.40", "PRECOMMIT_deskcraft_d17_exposure_extractor.md", "D21's in-sample R-squared, every firm"),
    Figure("0.016", "PRECOMMIT_deskcraft_d17_exposure_extractor.md", "D21's in-sample R-squared, the median"),
    Figure("7.43bp", "PRECOMMIT_deskcraft_d18_structures_and_gate.md", "H13: the ratio forward's improvement for GE"),
    Figure("$57.9m", "PRECOMMIT_deskcraft_d18_structures_and_gate.md", "H13: the same, a year"),
    Figure("$155.78bn", "PRECOMMIT_deskcraft_d18_structures_and_gate.md", "H13: the floor sold"),
    Figure("$83.7m", "PRECOMMIT_deskcraft_d18_structures_and_gate.md", "H13: GE's bought cap"),
    Figure("$244.16bn", "PRECOMMIT_deskcraft_d18_structures_and_gate.md", "ExxonMobil's stated crude purchases"),
    Figure("541.18%", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H16: ExxonMobil in NBER_2020"),
    Figure("1,195.55%", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H16: ExxonMobil in RATES_2022"),
    Figure("62.14%", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H16: GE in NBER_2020"),
    Figure("404.21%", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H16: GE in RATES_2022"),
    Figure("5.4 times", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "DD218: ExxonMobil's crude over its FY2013 cash flow"),
    Figure("4.6%", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "DD218: the move that crosses a quarter of it"),
    Figure("0.74 to 0.86", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "H14b under no decay, a hedge fitted on noise"),
    Figure("two-fifths to three-fifths", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "H14b under no decay, the cohort"),
    Figure("366 days", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "DTCC's public tape"),
    Figure("2023-12-29", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "DTCC's earliest row"),
    # D21's read, 2026-09-29: its registration's section 13.
    Figure("483", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "the verdict weeks of every evaluable firm"),
    Figure("32 of 32", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "H14a: firms counted"),
    Figure("0.4075", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "H14a: the largest effectiveness, ConocoPhillips"),
    Figure("0.0003", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "the median effectiveness out of sample"),
    Figure("16 of the 32", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "held hedges that added variance"),
    Figure("21 of 32", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "H14b: firms counted"),
    Figure("0.656", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "H14b: the share"),
    Figure("Thirteen of the fourteen", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "H14b: rates-only firms counted"),
    Figure("0.556", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "H14b: the share on the resolved subset"),
    Figure("0.525 to 0.725", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "H14b: the missing-data bounds over forty"),
    Figure("7 of 7", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "H12a: eligible firms counted"),
    Figure("1.300", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "H12a: the median capture"),
    Figure("1.790", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "DD211: the ratio forward's worst fall, Chevron"),
    # After the read, 2026-09-29 (DD243): D21's registration, section 14.2, and D22's linear figures.
    Figure("1.277", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "beside H12a: median capture, mapped firms, the Fed's volatility"),
    Figure("1.327", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "beside H12a: the same four firms on EWMA"),
    Figure("13.208bn", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "beside H16: ExxonMobil's option fall, NBER_2020"),
    Figure("119.753bn", "PRECOMMIT_deskcraft_d21_hedge_backtest.md", "beside H16: ExxonMobil's option fall, RATES_2022"),
    Figure("194.900bn", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H16: ExxonMobil's linear drawdown, NBER_2020"),
    Figure("175.363bn", "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md", "H16: ExxonMobil's linear drawdown, RATES_2022"),
)
