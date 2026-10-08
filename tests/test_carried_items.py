"""The carried-items register, made executable. Decision DD73, bars C76-C76b.

**This is not a package.** It rides along, in the shape D4's row records for the lint gate.

**Why it exists.** `docs/CARRIED_ITEMS.md` names ten weaknesses and gives each an owning
package. Its own §3 said the thing that made this bar necessary: *"If an owning package closes
without discharging its item, that is a silent failure this file does not catch — nothing parses
it."* A register nothing parses is a list of good intentions, and every item still open
changes a number the work will report, so losing one is not cosmetic.

This is C34's logic pointed at a second document. C34 holds that a claim's verdict exists if and
only if its scorer has landed, reading closure from a `PRECOMMIT_deskcraft_<package>_*.md`
document existing. Here: **if the package owing a carried item has landed, its pre-commit must
say what became of that item.**

**Deferral stays available, and that is deliberate.** A package may find that an item genuinely
belongs later. What it may not do is pass over it in silence, so there are exactly two ways to
answer, both written into the owning pre-commit:

    **X4** -- discharged: <what was done about it>
    **X4** -- carried to D9: <why it belongs there instead>

A carry is followed. The target inherits the debt, must be a real package in the build order,
and owes the same answer when it lands -- so an item can be moved but not dropped, and the
moving is in a diff.

**It passed vacuously when it was written, and no longer does.** At DD73 no pre-commit existed
for D7a, D7b, D8, D9 or D17, so nothing was owed an answer -- exactly the condition this
repository objects to elsewhere, which is why the guard against it was C76's equality on what
the register says and C76b's mutation. **D7a landed on 2026-09-15 owing X4 and X5**, and the
real arm now judges a live document: the pre-commit's §7 carries both discharges, and the run
that had the doc without them turned this red naming both items (D7a's P4, scored by
experiment rather than asserted). C76b stays, because the cases it covers -- a bare mention, a
followed carry, a bad target, a cycle -- are still not reachable from the tree as it stands.
"""

from __future__ import annotations

import re
from pathlib import Path

from test_deskcraft_boundary import REPO_ROOT, _read
from test_guards_and_registers import BUILD_ORDER, closed, order_tables, precommits_for

#: `RIDER_A5_the_six_remaining_decisions.md` §7, DD126. The package source, walked by C118.
#: Not `REPO_ROOT / "src"` -- the bar is about what the shipped package promises a reader, and a
#: script or a fixture mentioning DEC-2 is not a promise the library makes.
PACKAGE = REPO_ROOT / "src" / "deskcraft"

#: A site X20's body cites. `costs.py:323` names its file; `:247` continues the last one named,
#: which is the form the body already uses for `reference.py` and `sources.py`.
_SITE = re.compile(r"`(?:(\w+\.py))?:(\d+)`")


DOCS = REPO_ROOT / "docs"
REGISTER = DOCS / "CARRIED_ITEMS.md"

#: A row of §1's register: id, item, owner, status.
_ITEM_ROW = re.compile(r"^\|\s*\*\*(X\d+)\*\*\s*\|(.*?)\|(.*?)\|(.*?)\|\s*$")

#: A package id anywhere in an owner cell. `D7a §3.5` and `D8 (free rider)` both name one.
_PACKAGE = re.compile(r"\bD\d+[a-z]?\b")

#: The two answers a pre-commit may give. Declared as a form rather than looked for loosely: a
#: document that merely *mentions* X4 has not said what became of it, and "X4 is not addressed
#: here" would satisfy a search for the id.
_DISCHARGE = re.compile(
    r"\*\*(X\d+)\*\*\s*(?:—|--)\s*(?:(discharged)|carried to (D\d+[a-z]?))\b"
)

#: What §1 says today, as the expected result of parsing it. Not a copy of the register: it is
#: the census `MODULES` and `ENGINE_IMPORT_ROOTS` already are here, so an owner column edited
#: without a reason turns this red rather than passing quietly.
#: Empty since 2026-09-29 (DD242). X2 and X21 were discharged in writing by D17's §9 when it landed,
#: and C76 accepted both then; §1 had not moved their status. X20 closed with its six code sentences
#: rewritten in the same commit, which is the one way C118 lets it close.
DECLARED_OWED: dict[str, frozenset[str]] = {}
#: X12 joined on 2026-09-16: `generator.selection_ladder` returns a whole `Selection` at
#: every one of the eight cells, so a leg count cannot travel without the rung it came from.
#: The item mattered: the count **flips between 1x and 2x**, the pair §3.5 itself nominates.
#: D8 closed five on 2026-09-25: X6 (orientation run), X11 and X18 (DD128's route adds no cost
#: term), X22 (every estimator acts on `readable`), X25 (`VIXCLS` regraded from Cboe's words).
#: D9 closed three on 2026-09-25: X3 (F3 splits along the compiled view, F4 is a partial
#: correlation, neither reads the non-orthogonal share), X17 (a declared DV01 neutrality is
#: measured on the risk report, the syntactic invariant kept), X19 (select refuses a factor
#: whose reach leaves the candidate pool).
#: The read closed two on 2026-09-28: X13 (D12 landed on the record the owner authorised) and X14
#: (D15's rules preceded D14's first result, and landed with it handed over by rule). D16 closed
#: X26 the same day, reporting it as Paper 1's fourth limit.
#: DD242 closed the last three on 2026-09-29: X2 (D8's frequency policy, then D17 declined credit
#: by name), X21 (D17 stated crude's windows apart from DD98's), and X20 (D16 wrote the decline
#: into Paper 1, and the six sentences in `src/deskcraft` now state it).
DECLARED_CLOSED = frozenset(
    {
        "X1", "X2", "X3", "X4", "X5", "X6", "X8", "X9", "X10", "X11", "X12",
        "X13", "X14", "X17", "X18", "X19", "X20", "X21", "X22", "X23", "X24", "X25", "X26",
    }
)
#: X7, X15 and X16 are obligations on every future pre-commit rather than debts a package pays off.
#: X15 is `AMENDMENT_A3` §14.4's open class: H14 and H8 were both bars that could not fail, and
#: both were found by hand, so the standing rule is that a threshold arrives with the attainable
#: range of the quantity it cuts and the fraction of that range it admits.
#: X16 is the same shape one level up, raised by `RIDER_two_claims_that_something_could_not_be_
#: done.md`: two documents declared a residual unfixable, neither claim had been tested, and one
#: of the two was false in the commit that published it. A claim of impossibility arrives with
#: the experiment that would refute it, and that experiment's result or an explicit "not run".
DECLARED_STANDING = frozenset({"X7", "X15", "X16"})
DECLARED_ITEMS = frozenset(DECLARED_OWED) | DECLARED_CLOSED | DECLARED_STANDING


#: A body section for an item: `## X11. <anything>`. The register's closed items append an
#: em-dash marker to the heading, so the id is matched up to its full stop and no further.
_ITEM_BODY = re.compile(r"^##\s+(X\d+)\.\s+\S", re.MULTILINE)

#: Any line that opens with a bolded item id, whether or not it is a well-formed §1 row. What
#: this catches is the shape §4 carried until 2026-09-15: a *second* table of items, with three
#: cells instead of four, invisible to `_ITEM_ROW` and therefore free to go stale.
_ITEM_LINE = re.compile(r"^\|\s*\*\*(X\d+)\*\*")


def body_sections(text: str) -> set[str]:
    """Every item that has a `## X<n>.` section of its own."""
    return set(_ITEM_BODY.findall(text))


def item_lines(text: str) -> list[str]:
    """Every line opening with a bolded item id. §1's rows, and anything shaped like them."""
    return [line for line in text.splitlines() if _ITEM_LINE.match(line)]


def register_items(text: str) -> dict[str, tuple[frozenset[str], str]]:
    """Every register row, as `id -> (owning packages, status)`.

    The owner cell is prose -- `D8 (policy), D17 (the four-class claim)`, `rider, landed`,
    `every future pre-commit` -- so packages are extracted from it rather than assumed to be
    the whole cell. A cell naming none is owned by something that is not a package, and those
    are the items this bar cannot help with.
    """
    found: dict[str, tuple[frozenset[str], str]] = {}
    for line in text.splitlines():
        match = _ITEM_ROW.match(line)
        if match:
            found[match.group(1)] = (
                frozenset(_PACKAGE.findall(match.group(3))),
                match.group(4).strip(),
            )
    return found


def answers(docs: Path, package: str) -> dict[str, tuple[str, str | None]]:
    """What `package`'s pre-commit documents say became of each carried item."""
    given: dict[str, tuple[str, str | None]] = {}
    for path in precommits_for(package, docs):
        for item, discharged, carried in _DISCHARGE.findall(_read(path)):
            given[item] = ("discharged", None) if discharged else ("carried", carried)
    return given


def discharge_disagreements(
    items: dict[str, tuple[frozenset[str], str]], docs: Path, packages: frozenset[str]
) -> list[str]:
    """Every open item a landed package owes an answer for and has not given one.

    Carries are followed to a fixed point rather than taken at face value, because "carried to
    D9" written in a D8 document that landed after D9 would move a debt into the past. The
    target must be a real package, and it owes the same answer when it lands.
    """
    out: list[str] = []
    queue = [
        (item, package)
        for item, (owners, status) in sorted(items.items())
        if "OPEN" in status
        for package in sorted(owners)
    ]
    seen: set[tuple[str, str]] = set()

    while queue:
        item, package = queue.pop(0)
        if (item, package) in seen:
            continue
        seen.add((item, package))

        if package not in packages:
            out.append(f"{item}: owed by {package}, which is not a package in the build order")
            continue
        if not closed(package, docs):
            continue

        given = answers(docs, package).get(item)
        if given is None:
            out.append(
                f"{item}: {package} has landed and its pre-commit does not say what became "
                f"of it. Write `**{item}** -- discharged:` or `**{item}** -- carried to <D>:`"
            )
        elif given[0] == "carried":
            queue.append((item, given[1]))
    return out



def test_c118_the_dec2_deferral_is_counted_where_it_is_made() -> None:
    """C118. DD126, `RIDER_A5_the_six_remaining_decisions.md` §7. A decline the code contradicts.

    DD126 declines DEC-2's package: the budget is twenty-one one-in-one-out, nothing has been
    removed to pay for a foreign leg, and a deferral that never executes is a decline. That
    decision is taken in a document. **Six sentences in `src/deskcraft` still tell a reader that
    a later package will do the work**, and those two states are not compatible.

    The tempting half-state is the one this bar exists for: DD126 is taken, X20 therefore looks
    answered, and closing it costs one line while rewriting six sentences costs a package. Close
    it in that state and the repository declines in prose while promising in code -- the defect
    X20 was opened for, one level up.

    So the bar holds an equality rather than a count: every `DEC-2` site in the package is cited
    by X20's body at its own file and line, and no site is cited that does not exist. X20 must be
    OPEN. Green two ways -- rewrite the six and close the item in one commit, or leave both --
    and red only on the half-state, on a seventh deferral nobody registered, or on a site that
    moved without the register moving.

    It is deliberately narrow. C76 is the bar that walks every open row to an owning package and
    demands a written discharge; this one knows a single promise by name and holds its arithmetic
    between a document and a tree.

    **Closed 2026-09-29 (DD242), the first of the two green states.** The six sentences were
    rewritten to state DD126's decline and X20 closed in the same commit. The body keeps its six
    citations as the record of what was rewritten, and the tree must now hold no `DEC-2` at all.

    **Mutations:** a `DEC-2` sentence reappearing after the close, and the reverse half-state -- the
    code rewritten and the item left open. While X20 was open, a renumbered citation was the one.
    """
    text = _read(REGISTER)
    body = text.split("## X20.")[1].split("\n## X")[0]

    cited: set[tuple[str, int]] = set()
    current = ""
    for name, line in _SITE.findall(body):
        current = name or current
        assert current, "X20's body cites a line before naming a file"
        cited.add((current, int(line)))

    found = {
        (path.name, number)
        for path in sorted(PACKAGE.glob("*.py"))
        for number, line in enumerate(_read(path).splitlines(), start=1)
        if "DEC-2" in line
    }
    status = register_items(text)["X20"][1]

    assert not dec2_disagreements(status, found, cited), dec2_disagreements(status, found, cited)

    if "CLOSED" in status:
        reappeared = {sorted(cited)[0]}
        assert dec2_disagreements(status, reappeared, cited), "a DEC-2 sentence came back unseen"
        reopened = status.replace("CLOSED", "OPEN")
        assert dec2_disagreements(reopened, found, cited), "the item reopened over rewritten code"
    else:
        moved = {(n, k + 1) if n == "costs.py" else (n, k) for n, k in cited}
        assert dec2_disagreements(status, moved, cited), "the mutation moved nothing"


def dec2_disagreements(
    status: str, found: set[tuple[str, int]], cited: set[tuple[str, int]]
) -> list[str]:
    """C118's two green states, and what each refuses. Open: the tree's `DEC-2` sites equal the six
    X20's body cites. Closed: the tree holds none, and the body still records the six it rewrote."""
    out: list[str] = []
    if len(cited) != 6 or len({name for name, _ in cited}) != 4:
        out.append(f"X20's body cites {len(cited)} sites; it records six in four files")
    if "CLOSED" in status:
        out += [
            f"X20 is closed and `src/deskcraft/{name}:{number}` still defers to DEC-2"
            for name, number in sorted(found)
        ]
        return out
    if "OPEN" not in status:
        return out + [f"X20 reads {status!r}, which is neither OPEN nor CLOSED"]
    if found != cited:
        out.append(
            f"the package defers to DEC-2 at {sorted(found - cited)}; X20's body cites "
            f"{sorted(cited - found)} and the tree does not. DD126 declined the package, and the "
            "register says where the code still promises it"
        )
    return out


def test_no_landed_package_left_a_carried_item_unanswered() -> None:
    """C76. B76, DD73. The register's own §3 said nothing parsed it. Now something does.

    Four equalities before the check itself, written when the check passed vacuously -- no
    pre-commit existed for any of the five owing packages -- because a guard whose subject is
    empty is a guard that reports success for the wrong reason. The equalities are what would
    notice an item being deleted, reassigned, or marked closed without one, and they are what
    D7a had to move: X4 and X5 out of OPEN, X11 in, on the same run as the register.
    """
    items = register_items(_read(REGISTER))
    assert set(items) == DECLARED_ITEMS, {
        "in the register, not declared": sorted(set(items) - DECLARED_ITEMS),
        "declared, not in the register": sorted(DECLARED_ITEMS - set(items)),
    }

    owed = {item: owners for item, (owners, status) in items.items() if "OPEN" in status}
    assert owed == DECLARED_OWED, owed
    assert {i for i, (_, s) in items.items() if s.startswith("**CLOSED")} == DECLARED_CLOSED
    assert {i for i, (_, s) in items.items() if "STANDING" in s} == DECLARED_STANDING

    for item in DECLARED_CLOSED:
        assert "—" in items[item][1], f"{item} is closed and does not say what closed it"

    core, annex = order_tables(_read(BUILD_ORDER))
    packages = frozenset(core) | frozenset(annex)
    assert len(packages) == 23, sorted(packages)

    assert not discharge_disagreements(items, DOCS, packages), discharge_disagreements(
        items, DOCS, packages
    )


def test_the_discharge_check_would_catch_a_package_that_landed_in_silence(tmp_path: Path) -> None:
    """C76b. B76b. The check, mutated -- silence, both answers, a followed carry, a bad target.

    This is where C76 is observed firing, because the real arm has nothing to judge yet. Every
    case runs through `discharge_disagreements`, not through a copy of it.
    """
    items = {
        "X4": (frozenset({"D7a"}), "**OPEN**"),
        "X6": (frozenset({"D8"}), "**OPEN**"),
        "X9": (frozenset({"D7a"}), "**CLOSED** — docs/TOOLING.md"),
    }
    packages = frozenset({"D7a", "D7b", "D8", "D9"})
    docs = tmp_path / "docs"
    docs.mkdir()

    # Nothing has landed: nothing is owed, and a closed item is never chased.
    assert discharge_disagreements(items, docs, packages) == []

    # D7a lands and says nothing about X4.
    landed = docs / "PRECOMMIT_deskcraft_d7a_cost_model.md"
    landed.write_text("# D7a\n\nA package about costs.\n", encoding="utf-8")
    assert discharge_disagreements(items, docs, packages) == [
        "X4: D7a has landed and its pre-commit does not say what became of it. Write "
        "`**X4** -- discharged:` or `**X4** -- carried to <D>:`"
    ]

    # Mentioning the id is not answering for it.
    landed.write_text("# D7a\n\nX4 is interesting and is not addressed here.\n", encoding="utf-8")
    assert len(discharge_disagreements(items, docs, packages)) == 1

    # Discharged, in the declared form.
    landed.write_text("# D7a\n\n**X4** -- discharged: stated as a bias with its direction.\n", encoding="utf-8")
    assert discharge_disagreements(items, docs, packages) == []

    # Carried, and followed: D9 has not landed, so nothing is owed yet.
    landed.write_text("# D7a\n\n**X4** -- carried to D9: the corrected statistic is D9's.\n", encoding="utf-8")
    assert discharge_disagreements(items, docs, packages) == []

    # D9 lands in silence, and inherits the debt rather than dropping it.
    (docs / "PRECOMMIT_deskcraft_d9_attribution.md").write_text("# D9\n", encoding="utf-8")
    assert discharge_disagreements(items, docs, packages) == [
        "X4: D9 has landed and its pre-commit does not say what became of it. Write "
        "`**X4** -- discharged:` or `**X4** -- carried to <D>:`"
    ]

    # A carry to something that is not a package in the build order.
    landed.write_text("# D7a\n\n**X4** -- carried to D99: somewhere that does not exist.\n", encoding="utf-8")
    assert discharge_disagreements(items, docs, packages) == [
        "X4: owed by D99, which is not a package in the build order"
    ]

    # A cycle terminates rather than hanging: D7a carries to D7b, D7b carries back.
    landed.write_text("# D7a\n\n**X4** -- carried to D7b: not here.\n", encoding="utf-8")
    (docs / "PRECOMMIT_deskcraft_d7b_legs.md").write_text(
        "# D7b\n\n**X4** -- carried to D7a: nor here.\n", encoding="utf-8"
    )
    assert discharge_disagreements(items, docs, packages) == []


def test_every_registered_item_has_a_body_and_there_is_only_one_register() -> None:
    """C88. B88, DD88. `AMENDMENT_A2` §4-§5. C76 parses §1's table and nothing else.

    **Two ways a register can be wrong that C76 cannot see**, both found by an audit on
    2026-09-15 rather than by a bar, which is why they are a bar now:

    1. **An item with a row and no body.** X11 was opened by D7a and given a §1 row, an owner and
       a status -- and nothing beneath it: no defect statement, no measurement, no what-closes-it,
       no cost of deferring. It was the only item of eleven in that state and C76 passed, because
       a row is all C76 reads. A register that can name a debt without stating it is a list of
       ids.
    2. **A second table of items.** §4 carried one -- *"What is owed today, and by whom"* -- and by
       the time anyone read it, it was stale three ways: X4 and X5 still shown as owed after D7a
       discharged them, no X11, and a sentence saying C76 *"passes vacuously today"* after C76 had
       fired for real. It drifted precisely because nothing read it: three cells where `_ITEM_ROW`
       wants four, so the parser walked past it. The fix is not to update it -- it is that there is
       one register and §4 points at it (C34's lesson, aimed at a register instead of a claim).

    **Mutation:** both cases are run against the real functions, on `git`-shaped text rather than
    on a paraphrase -- a document with a body removed, and one with a three-cell row added back.
    """
    text = _read(REGISTER)

    bodies = body_sections(text)
    assert bodies == DECLARED_ITEMS, {
        "has a body, not declared": sorted(bodies - DECLARED_ITEMS),
        "declared, has no body": sorted(DECLARED_ITEMS - bodies),
    }

    rows = item_lines(text)
    assert len(rows) == len(DECLARED_ITEMS), rows
    unparsed = [line for line in rows if not _ITEM_ROW.match(line)]
    assert not unparsed, (
        "a line opens with an item id and is not a well-formed §1 row, which is how §4's "
        f"owed-table went stale unseen: {unparsed}"
    )

    # The mutations, through the same two functions rather than a copy of them.
    without_body = text.replace("## X11. Two of the four", "## Two of the four", 1)
    assert "X11" not in body_sections(without_body)

    second_table = text + "\n| **X2** | D8, D17 | either lands |\n"
    regrown = [line for line in item_lines(second_table) if not _ITEM_ROW.match(line)]
    assert regrown == ["| **X2** | D8, D17 | either lands |"], regrown


# ---------------------------------------------------------------------------
# C100: the register's statement about itself
# ---------------------------------------------------------------------------

#: The one sentence in which the register states its own size. Word-numbers, because the sentence
#: is written for a reader first and a parser second. Anchored to the whole form rather than to
#: three loose numbers: a document that merely contains the word "seven" has not stated a tally.
_TALLY = re.compile(r"^([\w-]+) closed, ([\w-]+) standing, ([\w-]+) open with an owner\.", re.MULTILINE)

#: Enough to count this register twice over. A number beyond the table's reach is a number the
#: register cannot currently state, and `stated_tally` says so rather than guessing. Extended past
#: twenty on 2026-09-29 (DD242), when the closed count reached twenty-three: hyphenated, as written.
_UNITS = (
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen".split()
)
_WORD_NUMBERS = {word: value for value, word in enumerate(_UNITS)} | {
    (tens if unit == 0 else f"{tens}-{_UNITS[unit]}"): 10 * (2 + i) + unit
    for i, tens in enumerate(("twenty", "thirty", "forty"))
    for unit in range(10)
}

#: How a status cell is classified. Checked for ambiguity at use, not assumed: `CLOSED by
#: verification` and `OPEN, narrowed` both carry trailing prose, and a cell matching two of these
#: would be counted twice without anyone noticing.
_STATUSES = ("CLOSED", "STANDING", "OPEN")


def stated_tally(text: str) -> tuple[int, int, int]:
    """`(closed, standing, open)` as §1's summary sentence states them."""
    match = _TALLY.search(text)
    assert match, (
        "`CARRIED_ITEMS.md` §1 no longer states its own size in the form C100 reads. The "
        "sentence is `<word> closed, <word> standing, <word> open with an owner.` and it sits "
        "directly beneath the register table. Reword it and this bar stops being able to check "
        "it -- which is the state the register was in for four landings."
    )
    words = [word.lower() for word in match.groups()]
    unknown = [word for word in words if word not in _WORD_NUMBERS]
    assert not unknown, f"the tally uses a number this bar cannot read: {unknown}"
    closed_count, standing_count, open_count = (_WORD_NUMBERS[word] for word in words)
    return closed_count, standing_count, open_count


def counted_tally(text: str) -> tuple[int, int, int]:
    """`(closed, standing, open)` as §1's table actually reads, row by row."""
    counts = dict.fromkeys(_STATUSES, 0)
    for item, (_, status) in sorted(register_items(text).items()):
        matched = [name for name in _STATUSES if name in status]
        assert len(matched) == 1, (
            f"{item}'s status cell matches {matched or 'no'} status word, so the register cannot "
            f"be counted: {status!r}"
        )
        counts[matched[0]] += 1
    return counts["CLOSED"], counts["STANDING"], counts["OPEN"]


def test_the_register_states_its_own_size_and_the_statement_is_true() -> None:
    """C100. B100, DD107. `RIDER_the_register_counts_itself_in_prose.md`.

    **The register was guarded everywhere except in what it says about itself.** Three equality
    censuses fix the declarations, C76 walks every row to an owner, C88 demands a body under every
    row and refuses a second table -- and then §1 summarises itself in one sentence that no bar
    had ever read. It was last true at `f9f46fa`. Four landings then edited the table and left the
    sentence alone, three of them adding an open item, and by today it was wrong in two of its
    three numbers while every row beneath it was correct.

    **The claim that matters never failed**: no item was ever unowned. What drifted was the census
    *beside* the census -- the line a reader reaches for first, and the only one written for a
    human rather than for a parser. That is the fifth time in this repository that prose named
    something true and was given to no bar, and the first time the prose was about the guarded
    structure it sits under.

    So the disposition is C98's, which is the one that worked: **re-derive the quantity from the
    source and compare it to the stated words**, rather than correcting the words (true this
    afternoon, stale at D7b) or deleting them (a register that cannot state its own size is a
    worse register).

    **Mutation:** the historical failure itself, in both directions -- a table that grows while
    the sentence stands still, and a sentence edited while the table stands still.
    """
    text = _read(REGISTER)

    assert stated_tally(text) == counted_tally(text), {
        "§1's sentence says": stated_tally(text),
        "§1's table reads": counted_tally(text),
        "order": "(closed, standing, open)",
    }
    assert counted_tally(text) == (
        len(DECLARED_CLOSED),
        len(DECLARED_STANDING),
        len(DECLARED_OWED),
    ), "the table and the declarations disagree, which is C88's subject and not this bar's"

    assert len(_TALLY.findall(text)) == 1, (
        "the register states its size twice, and two statements of one number disagree "
        "eventually -- which is why the paragraph beneath §1 stopped restating it"
    )

    # The mutations. Both are what actually happened between `f9f46fa` and today, and both now
    # **derive** what they perturb rather than naming it. Until 2026-09-16 the first borrowed the
    # literal id `X16` on the reasoning that it did not exist, and the second quoted the tally
    # wording as it stood that morning. `RIDER_two_claims_that_something_could_not_be_done.md`
    # then opened X16 and the tally moved to *three standing*: the added row collided with a real
    # one and stopped adding anything, and the quoted wording stopped matching. Both went red,
    # which is correct and is the only reason this is a footnote -- **a mutation that names a
    # fact outside its own subject has a shelf life**, and that is this bar's subject one level
    # down. Neither hard-codes anything now.
    unused = f"X{max(int(item[1:]) for item in register_items(text)) + 1}"
    grown = text + f"\n| **{unused}** | opened by a later package | D99 | **OPEN** |\n"
    assert counted_tally(grown) != stated_tally(grown), (
        "a row was added and the tally did not move, and this bar did not notice"
    )

    sentence = _TALLY.search(text)
    assert sentence, "no tally sentence, which the first assertion in this bar should have said"
    closed_word = sentence.group(1)
    wrong = "Nine" if closed_word.lower() != "nine" else "Eight"
    reworded = text.replace(
        sentence.group(0), sentence.group(0).replace(closed_word, wrong, 1), 1
    )
    assert stated_tally(reworded) != counted_tally(reworded)
