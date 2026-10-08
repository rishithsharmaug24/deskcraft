"""C213-C218. D16: the readout and Paper 1 (`PRECOMMIT_deskcraft_d16_readout_and_paper1.md`).

Landed 2026-09-28 on the out-of-sample read's verdicts, and tagged CP-2 (DD225). What is held is that
the paper's table is the register's, that every figure it quotes was recorded by the package that
measured it, that its limits and declines are the ones the packages found, and that it describes
and never advises.
"""

from __future__ import annotations

import re

from deskcraft import readout as r
from deskcraft.registers import CLAIMS, ClaimStatus
from test_deskcraft_boundary import FORBIDDEN_RENDERED_PHRASES, REPO_ROOT, _read, imperative_offences
from test_guards_and_registers import REGISTERED_DOCUMENTS, REGISTERED_MARKER, closed, registered_in

DOCS = REPO_ROOT / "docs"
PRECOMMIT = DOCS / "PRECOMMIT_deskcraft_d16_readout_and_paper1.md"
PAPER = DOCS / "PAPER1_the_engine_and_its_backtest.md"

FIXED = (
    "**DD225 — D16 is registered and not landed, and why that is not a postponed verdict.**",
    "**\"Paper 1 complete and sendable\" is CP-2's definition**",
    "**DD226 — the claims table is rendered, and the paper holds the render.**",
    "**DD227 — every figure the paper quotes is one a package recorded.**",
    "**DD228 — the limits, in this order.**",
    "**DD229 — the declines, each with the measurement behind it.**",
    "**DD230 — describes, never advises.**",
)

#: DD228's limits and DD229's declines, as the paper's own headings of each item open.
LIMITS = (
    "**The grammar reaches at most 0.906494022 of an arbitrary view direction**",
    "**H4b could not fail.**",
    "**H9's margin is a property of the grid.**",
    "**The generator is path-dependent.**",
    "**On one Gaussian covariance, reverse stress adds nothing to Euler.**",
    "**Held means frozen.**",
    "**Two tests are weak by design.**",
    "**The predictions are not information-blind.**",
)
DECLINES = (
    "**The cross-market leg.**",
    "**Options and volatility.**",
    "**The credit leg.**",
    "**A seventh grammar term.**",
    "**Commodities.**",
)


def _flat(text: str) -> str:
    return " ".join(line.lstrip("> ").strip() for line in text.splitlines())


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    return text[start : end if end != -1 else len(text)]


def test_c213_d16_is_registered_with_its_rules_and_its_reason() -> None:
    """C213. DD225-DD230 as written. Registered before the read, landed after it: the marker left in
    the commit that rendered the read's verdicts, C158's declared set no longer names this document,
    and D16 is closed, which is what CP-2 was tagged on.

    **Mutation:** with the marker planted back in place of the landed status, D16 is registered again.
    """
    text = _read(PRECOMMIT)
    flat = _flat(text)
    missing = [phrase for phrase in FIXED if phrase not in flat]
    assert not missing, missing
    header = text.split("\n## 0.")[0]
    assert "**Status: LANDED 2026-09-28.**" in header and REGISTERED_MARKER not in header
    assert PRECOMMIT.name not in REGISTERED_DOCUMENTS
    assert closed("D16", DOCS)
    assert "**X20** — discharged:" in text and "**X26** — discharged:" in text
    assert not registered_in(text, "D16")
    assert registered_in(text.replace("**Status: LANDED 2026-09-28.**", REGISTERED_MARKER), "D16")


def test_c214_the_papers_table_is_the_registers() -> None:
    """C214. DD226. Every Paper 1 row of `CLAIMS` and no Paper 2 row; withdrawn rows name their
    successors; no row awaits the read, and the six that did carry its verdicts; and the block between
    the paper's markers is the render, character for character.

    **Mutation:** a verdict hand-edited into the paper's table no longer equals the render.
    """
    ids = [c.claim_id for c in r.paper_one_claims()]
    assert ids == ["H1", "H2", "H3", "H4", "H4a", "H4b", "H5", "H6", "H7", "H8", "H8a", "H8b", "H9", "SCENARIO_SIGNS"]
    assert not {"H11", "H12a", "H13", "H14a", "H15", "H16", "H17"} & set(ids)
    table = r.claims_table()
    awaiting = sorted(line.split("|")[1].strip() for line in table.splitlines() if line.endswith(f"| {r.AWAITING} |"))
    assert awaiting == []
    read = {c.claim_id: c.verdict.value for c in r.paper_one_claims() if c.scorer in r.READERS}
    assert read == {"H1": "PASS", "H2": "FAIL", "H5": "FAIL", "H6": "FAIL", "H7": "FAIL", "SCENARIO_SIGNS": "REPORTED"}
    for claim in r.paper_one_claims():
        if claim.status is ClaimStatus.WITHDRAWN:
            assert f"withdrawn: {', '.join(claim.successors)}" in table

    paper = _read(PAPER).replace("\r\n", "\n")
    block = paper[paper.index(r.BLOCK_BEGIN) + len(r.BLOCK_BEGIN) : paper.index(r.BLOCK_END)].strip("\n")
    assert block == table
    edited = block.replace("| H6 | Crisis correlations change sizing > 20% of gross | D12 | PASS | **FAIL** |",
                           "| H6 | Crisis correlations change sizing > 20% of gross | D12 | PASS | **PASS** |")
    assert edited != block and edited != table


def test_c215_every_quoted_figure_was_recorded_by_its_package() -> None:
    """C215. DD227. Each of `FIGURES` appears in its source document and in the paper, whitespace
    folded, because a figure wraps across lines in both.

    **Mutation:** a figure the paper quotes one digit off is not found in its source.
    """
    paper = _flat(_read(PAPER))
    for figure in r.FIGURES:
        source = _flat(_read(DOCS / figure.source))
        assert figure.text in source, (figure.text, figure.source)
        assert figure.text in paper, (figure.text, "paper")
    assert "2.4104" not in _flat(_read(DOCS / "PRECOMMIT_deskcraft_d10_effective_bets.md"))


def test_c216_the_limits_open_with_the_saturated_cosine_and_the_declines_follow() -> None:
    """C216. DD228 and DD229. The paper's limits are DD228's eight, in order, the first being DD138's
    saturated cosine; its declines are DD229's five, in order, the first being X20's cross-market leg.

    **Mutation:** two limits swapped are reported out of order.
    """
    paper = _read(PAPER)
    limits = _flat(_section(paper, "## 5. Limits"))
    declines = _flat(_section(paper, "## 6. Declines"))

    def order(body: str, items: tuple[str, ...]) -> list[int]:
        return [body.find(item) for item in items]

    positions = order(limits, LIMITS)
    assert -1 not in positions and positions == sorted(positions), positions
    assert positions[0] == min(positions) and "0.906494022" in LIMITS[0]
    swapped = limits.replace(LIMITS[0], "@@").replace(LIMITS[1], LIMITS[0]).replace("@@", LIMITS[1])
    assert order(swapped, LIMITS) != sorted(order(swapped, LIMITS))
    positions = order(declines, DECLINES)
    assert -1 not in positions and positions == sorted(positions), positions
    assert "X26" in limits and "DD126" in declines and "DD121" in declines


def test_c217_the_paper_describes_and_never_advises() -> None:
    """C217. DD230. No phrase of the boundary's imperative ban appears in the paper or in the strings
    `readout.py` renders. The ban is the one C6 holds, read here on the document it exists for.

    **Mutation:** a planted "you should" in the paper is found, and so is one in a readout constant.
    """
    paper = _read(PAPER)

    def offences(text: str) -> list[str]:
        return [p for p in FORBIDDEN_RENDERED_PHRASES if re.search(p, text, flags=re.IGNORECASE)]

    assert not offences(paper), offences(paper)
    assert not offences(r.claims_table() + r.tally_sentence())
    assert offences(paper + "\nYou should hedge the euro.\n") == [r"\byou should\b"]
    source = _read(REPO_ROOT / "src" / "deskcraft" / "readout.py")
    assert not imperative_offences(source)
    assert imperative_offences(source + '\nNOTE = "take profit on the long end"\n')


def test_c218_the_abstract_states_the_registers_tally() -> None:
    """C218. D16 P1 held before the read: six of twelve live rows scored, four as predicted, one
    against, one reported, six awaiting. After it: all twelve scored, seven as predicted, three
    against, two reported, none awaiting. Computed from `CLAIMS`, and the paper's abstract and §2
    carry the sentence.

    **Mutation:** a thirteenth live row changes the sentence, so a stale paper would fail.
    """
    t = r.tally()
    assert (t.live, t.scored, t.as_predicted, t.against, t.reported, t.awaiting) == (12, 12, 7, 3, 2, 0)
    assert "await" not in r.tally_sentence() and "three against their predictions" in r.tally_sentence()
    paper = _flat(_read(PAPER))
    abstract = _flat(_section(_read(PAPER), "## Abstract"))
    assert r.tally_sentence() in abstract and paper.count(r.tally_sentence()) == 2
    live = [c for c in CLAIMS if c.status is ClaimStatus.ACTIVE]
    assert len([c for c in live if r._package_number(c.scorer) <= r.PAPER1_LAST_PACKAGE]) == t.live


PAPER2 = DOCS / "PAPER2_hedging_measured_exposure.md"


def test_c222_paper_two_is_rendered_from_the_register() -> None:
    """C222. DD241. Paper 2 is held as Paper 1 is: its block is the render of Paper 2's rows of
    `CLAIMS` and no other, its tally sentence is in the abstract and in section 2, every quoted figure
    is found in the document that recorded it and in the paper, and it describes and never advises.
    Until D21 lands its three rows await the read; after, none does.

    **Mutation:** a verdict hand-edited into Paper 2's block no longer equals the render, and a
    figure one digit off is not found in its source.
    """
    ids = [c.claim_id for c in r.paper_two_claims()]
    assert ids == ["H11", "H12a", "H13", "H14", "H14a", "H14b", "H15", "H16", "H17"]
    assert not set(ids) & {c.claim_id for c in r.paper_one_claims()}
    table = r.claims_table(r.paper_two_claims())
    awaiting = sorted(line.split("|")[1].strip() for line in table.splitlines() if line.endswith(f"| {r.AWAITING} |"))
    assert awaiting == ([] if closed("D21", DOCS) else ["H12a", "H14a", "H14b"])
    assert "| H15 | " in table and "**NOT_PERFORMED**" in table

    paper = _read(PAPER2).replace("\r\n", "\n")
    block = paper[paper.index(r.PAPER2_BLOCK_BEGIN) + len(r.PAPER2_BLOCK_BEGIN) : paper.index(r.PAPER2_BLOCK_END)].strip("\n")
    assert block == table
    edited = block.replace("| D17 | PASS | **FAIL** |", "| D17 | PASS | **PASS** |")
    assert edited != block and edited != table

    flat = _flat(paper)
    abstract = _flat(_section(paper, "## Abstract"))
    sentence = r.paper_two_tally_sentence()
    assert sentence in abstract and flat.count(sentence) == 2
    for figure in r.FIGURES_TWO:
        assert figure.text in _flat(_read(DOCS / figure.source)), (figure.text, figure.source)
        assert figure.text in flat, (figure.text, "paper 2")
    assert "541.19%" not in _flat(_read(DOCS / "PRECOMMIT_deskcraft_d12_d14_d15_d22_registration.md"))

    offences = [p for p in FORBIDDEN_RENDERED_PHRASES if re.search(p, paper, flags=re.IGNORECASE)]
    assert not offences, offences
