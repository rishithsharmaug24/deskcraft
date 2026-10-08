"""The gate on the one irreversible surface. `RIDER_X13_X14_one_surface_two_clocks.md`, C119-C121.

Four packages -- D12, D14, D15 and D22 -- read the out-of-sample record, and the first read of a
row dated after `DEV_END` fires DD37 in curvecast permanently. C96 fixes the window, C97 asserts
the trigger is unpulled, C98 derives the forward bound from its own rule. What none of the three
holds is **who pulls it** and **in what order the four are written**, which is X13 and X14.

Every bar here is deliberately **two-branched**, with the live branch being the one that runs
today. A bar whose body only begins to exist once a gate opens is X15's defect moved into time:
it cannot fail while it matters, and by the time it can fail the thing it was guarding is spent.

Each mutation builds its own tree under `tmp_path` rather than perturbing a literal, because the
detectors here are the whole bar -- a detector that silently stopped matching would otherwise pass
over an empty directory and report green.
"""

from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path

from deskcraft.window import DEV_END
from test_deskcraft_boundary import REPO_ROOT, _read

DOCS = REPO_ROOT / "docs"
FIXTURES = REPO_ROOT / "tests" / "fixtures"
PACKAGE = REPO_ROOT / "src" / "deskcraft"

#: DD133's gate. Absent by design -- the rider that specifies it may not also grant it.
AUTHORISATION = DOCS / "OWNER_AUTHORISATION_the_first_oos_read.md"

#: DD134's one document for one surface.
JOINT = "PRECOMMIT_deskcraft_d12_d14_d15_d22"

#: The four packages the joint document registers. X13's body names exactly these.
JOINT_READERS = ("D12", "D14", "D15", "D22")

#: DD199. The readers registered outside the joint document, each before the first read, with the
#: reason. Held as an equality in C191, so a sixth is an edit here and never a quiet use of the
#: exception DD134's amendment made.
SEPARATE = {
    "PRECOMMIT_deskcraft_d21_hedge_backtest.md": (
        "DD199: D21's H14a and H14b are statements about 2015 onwards, and D21 had no pre-commit "
        "when DD134 counted four. The joint document's filename is what `closed()` reads, so it "
        "cannot take a fifth package without moving every bar that cites it"
    ),
}

#: Every package that reads the record: the joint document's four and DD199's fifth.
READERS = ("D12", "D14", "D15", "D21", "D22")

#: A committed panel's filename carries its coverage and then its extraction vintage --
#: `panel_daily_dev_20260914.csv`. The vintage is when curvecast extracted it and says nothing
#: about which rows are inside; only the coverage token does. Comparing a vintage with `DEV_END`
#: is a category error, and it was one until this bar was first run.
_CSV_LITERAL = re.compile(r'"([A-Za-z0-9_.-]+\.csv)"')


def _panel_max(path: Path) -> date:
    """The latest observation date in a committed panel fixture."""
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    field = next(name for name in rows[0] if "date" in name.lower())
    return max(date.fromisoformat(row[field][:10]) for row in rows)


def fixtures_past_dev(fixtures: Path) -> list[str]:
    """Committed fixtures carrying a row dated after `DEV_END`. Empty until the gate opens."""
    return sorted(p.name for p in fixtures.glob("*.csv") if _panel_max(p) > DEV_END)


def modules_reaching_past_dev(package: Path, fixtures: Path) -> list[str]:
    """Package modules naming a panel that reaches past `DEV_END`, in either arrival order.

    The fixture and the code that loads it need not land together. If the CSV comes first, its
    rows are checked. If the module comes first -- a loader written against a filename curvecast
    has not delivered yet -- there are no rows to check, and the only evidence is the coverage
    token in the name it was given.
    """
    out = []
    for path in sorted(package.glob("*.py")):
        for name in _CSV_LITERAL.findall(_read(path)):
            target = fixtures / name
            if target.exists():
                if _panel_max(target) > DEV_END:
                    out.append(f"{path.name}: {name} carries rows past {DEV_END}")
            elif "oos" in name.lower():
                out.append(f"{path.name}: {name} names an out-of-sample panel")
    return out


def lone_reader_precommits(docs: Path) -> list[str]:
    """Pre-commits naming a reader on its own, outside the joint document and DD199's set."""
    out = []
    for path in sorted(docs.glob("PRECOMMIT_*.md")):
        if path.name.startswith(JOINT) or path.name in SEPARATE:
            continue
        stem = path.name.lower()
        if any(f"_d{reader[1:]}_" in stem or f"_d{reader[1:]}." in stem for reader in READERS):
            out.append(path.name)
    return out


def authorisation_problems(text: str) -> list[str]:
    """What an authorisation's text lacks, per DD133 and DD199: DD37, every reader, both
    registration documents by name, and a date that is not in the future."""
    out = []
    if "DD37" not in text:
        out.append("the assent does not name the decision it spends (DD37)")
    missing = [reader for reader in READERS if reader not in text]
    if missing:
        out.append(
            f"readers not named: {missing}. One surface, one authorisation -- naming a subset would "
            "let the other packages read on an assent that was never given for them (DD133, DD199)"
        )
    for document in (JOINT, *SEPARATE):
        if document.removesuffix(".md") not in text:
            out.append(
                f"{document} is not named, so the authorisation could have been granted before "
                "there was anything registered to grant it against (DD134, DD199)"
            )
    stamps = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if not stamps:
        out.append("the assent carries no date, so nothing next door can be dated against it")
    elif date.fromisoformat(stamps[0]) > date.today():
        out.append("the authorisation is post-dated")
    return out


def test_the_first_out_of_sample_read_is_the_owners_to_authorise(tmp_path: Path) -> None:
    """C119. DD133. `RIDER_X13_X14_one_surface_two_clocks.md` §2.

    X13 states the asymmetry: the cost of deferring is *"zero today and unbounded at the moment of
    the first read"*, because DD37 forecloses curvecast's remaining look budget the instant a row
    dated after `DEV_END` is read here, and *"what a person has read cannot be unread."*

    C97 already asserts the trigger is unpulled, so the day it is pulled it is *"pulled by a red
    bar and a deliberate edit"*. **That is a tripwire and not a gate.** A red bar is an argument
    with a test and a deliberate edit is available to whoever finds the test inconvenient, so the
    sequence C97 permits is: the fixture lands, this bar goes red, somebody edits the expectation
    because the fixture is obviously meant to be there, and a look budget in another repository is
    spent by a commit whose message is about a test. Nothing required the **owner** to decide.

    So this bar is green **two ways** and red only in between. With no authorisation, nothing
    post-DEV may be committed and no module may name a panel that reaches past `DEV_END`. With
    one, it must be well-formed: DD37 named, all four readers named, a date that is not in the
    future, and the joint pre-commit asserted to exist -- so an authorisation cannot precede the
    registration it is supposed to be authorising.

    **Mutation:** a tree is built carrying a post-DEV fixture and a loader naming an out-of-sample
    panel that has not arrived, and both halves are reported.
    """
    fixtures = fixtures_past_dev(FIXTURES)
    modules = modules_reaching_past_dev(PACKAGE, FIXTURES)

    if not AUTHORISATION.exists():
        assert not fixtures and not modules, {
            "fixtures dated past DEV_END": fixtures,
            "modules naming a panel past DEV_END": modules,
            "DD133": "the out-of-sample record has been reached without an owner authorisation. "
            f"Write {AUTHORISATION.name} first -- DD37 is irreversible and is spent in curvecast, "
            "not here, so this repository cannot give the budget back.",
        }
    else:
        problems = authorisation_problems(_read(AUTHORISATION))
        assert not problems, problems

    # The mutation, in both arrival orders.
    fake_fixtures = tmp_path / "fixtures"
    fake_fixtures.mkdir()
    (fake_fixtures / "panel_daily_oos_20260923.csv").write_text(
        "date,value\n2015-01-02,1.0\n", encoding="utf-8"
    )
    assert fixtures_past_dev(fake_fixtures) == ["panel_daily_oos_20260923.csv"]

    fake_package = tmp_path / "package"
    fake_package.mkdir()
    (fake_package / "loader.py").write_text(
        'OOS = _FIXTURES / "panel_daily_oos_20271231.csv"\n', encoding="utf-8"
    )
    assert modules_reaching_past_dev(fake_package, fake_fixtures) == [
        "loader.py: panel_daily_oos_20271231.csv names an out-of-sample panel"
    ]

    # And the detector still passes the real DEV panels, whose vintage is post-DEV and whose rows
    # are not -- the category error this bar was written with and corrected on its first run.
    assert modules_reaching_past_dev(PACKAGE, FIXTURES) == modules


def test_four_readers_of_one_surface_are_registered_together_or_not_at_all(tmp_path: Path) -> None:
    """C120. DD134. `RIDER_X13_X14_one_surface_two_clocks.md` §4.

    X13 and X14 were raised by different documents against different packages and read as
    unrelated -- one about a look budget next door, one about an analyst's memory. They are the
    same defect: **sequence around a single shared surface**. One joint pre-registration, written
    before the first read, is simultaneously what makes the read deliberate and what removes the
    knowledge carried forward from the package that read it first.

    **The failure mode this refuses is not skipping the joint document.** It is writing D12's
    pre-commit first because D12 runs first, which is entirely reasonable locally and sets the
    order four packages before anyone notices that the order was the thing at stake. So while the
    joint document is absent, a pre-commit naming one reader alone is refused; when it exists, it
    must name all four and cite the decisions it rests on.

    **Mutation:** a directory carrying a lone D14 pre-commit beside the nine that legitimately
    exist is reported, and the joint document is shown not to trip it.
    """
    joint = sorted(DOCS.glob(f"{JOINT}*.md"))
    lone = lone_reader_precommits(DOCS)

    if not joint:
        assert not lone, {
            "pre-commits naming one reader alone": lone,
            "DD134": "D12, D14, D15 and D22 read one irreversible surface, so they are "
            f"pre-registered in one document named {JOINT}*.md -- writing them in sequence is "
            "what X14 is about, and by the time D15 is written the order is already set",
        }
    else:
        assert len(joint) == 1, [p.name for p in joint]
        text = _read(joint[0])
        missing = [reader for reader in JOINT_READERS if reader not in text]
        assert not missing, {"readers absent from the joint pre-commit": missing}
        for decision in ("DD133", "DD134", "DD135"):
            assert decision in text, f"the joint pre-commit does not cite {decision}"

    # The mutation: the shape it exists to catch, and the shape it must let through.
    fake = tmp_path / "docs"
    fake.mkdir()
    (fake / "PRECOMMIT_deskcraft_d7a_cost_model.md").write_text("x", encoding="utf-8")
    (fake / f"{JOINT}_20260923.md").write_text("x", encoding="utf-8")
    assert lone_reader_precommits(fake) == []

    (fake / "PRECOMMIT_deskcraft_d14_battery.md").write_text("x", encoding="utf-8")
    assert lone_reader_precommits(fake) == ["PRECOMMIT_deskcraft_d14_battery.md"]


def test_every_d15_choice_d14_could_inform_is_a_constant_or_a_rule() -> None:
    """C121. DD135. `RIDER_X13_X14_one_surface_two_clocks.md` §3.

    X14's sentence -- *"no amount of pre-registration by D15 changes what its author has already
    read"* -- is exactly right and carries a presupposition worth reading twice: **has already
    read.** It is true of a pre-commit written after D14 runs and vacuous for one written before.
    All three answers X14 enumerates accept the writing order and repair the damage downstream.
    The fourth inverts the writing order without inverting the running order, and costs neither
    sample nor evidence.

    The objection that makes it real is that D15 needs a covariance and which one is defensible is
    what D14 reports. **DD98's device dissolves it**: `OOS_END` was fixed without being chosen, by
    a rule returning exactly one answer. So D15 names *"whichever variant D14 ranks first on
    Fissler-Ziegel loss under Diebold-Mariano"* -- a function of an output that does not exist
    yet. A rule evaluated afterwards is not a choice made afterwards.

    This bar holds the shape in two places: the register must offer **four** answers rather than
    three, so the option cannot quietly disappear; and once the joint pre-commit exists it must
    carry X14's discharge and leave no parameter to be settled when the result is visible.

    **Mutation:** the pending-decision detector is exercised on text of the shape it exists to
    catch and on the register's own body, so a detector that had stopped matching fails here
    rather than passing over a document it no longer reads.
    """
    register = _read(REPO_ROOT / "docs" / "CARRIED_ITEMS.md")
    body = register.split("## X14.")[1].split("\n## X15.")[0]

    answers = re.findall(r"^\* \*\*", body, re.M)
    assert len(answers) == 4, (
        f"X14's body offers {len(answers)} acceptable answers, not four. The fourth -- invert the "
        "writing order, so D15's specification is committed before D14's first result exists -- "
        "costs neither sample nor evidence and is the only one that removes the exposure rather "
        "than bounding it. It is registered by "
        "`RIDER_X13_X14_one_surface_two_clocks.md` §3 and must stay visible in the item itself."
    )
    assert "writing order" in body, "the fourth answer is counted but not named"

    joint = sorted(DOCS.glob(f"{JOINT}*.md"))
    if joint:
        text = _read(joint[0])
        assert "**X14** — discharged:" in text or "**X14** - discharged:" in text, (
            "the joint pre-commit does not discharge X14. C76 will refuse D15's landing without "
            "it, and by then the choice has been made by default."
        )
        section = text.split("frozen")[1] if "frozen" in text else text
        pending = sorted({match.group(0) for match in _PENDING.finditer(section)})
        assert not pending, {
            "parameters left to be settled when the result is visible": pending,
            "DD135": "a D15 choice D14's output could inform is a constant or a rule with one "
            "answer. A third category is the defect.",
        }

    # The mutation: the detector must fire on the shape, and stay quiet on the register.
    for phrase in ("the covariance is TBD", "to be decided once D14 reports", "whichever looks best"):
        assert _PENDING.search(phrase), f"the pending-decision detector no longer reads {phrase!r}"
    assert not _PENDING.search(body), "X14's body already reads as a deferred decision"


#: DD135's refusal. A parameter left to be settled when the result is visible is the whole defect,
#: and it announces itself in prose long before it shows up in a number.
_PENDING = re.compile(
    r"\b(to be (decided|determined|chosen|selected)|TBD|TBC|once we (see|know)|"
    r"decide (later|at the time)|whichever looks|as appropriate)\b",
    re.IGNORECASE,
)


def test_c169_d22s_lock_is_written_before_the_read() -> None:
    """C169. DD168, DD171, DD175, DD176, DD177, DD178, DD179. The price of reading Paper 1 before D22 exists, paid in the document.

    The owner took option 1: Paper 1 reads now and D22 reads later under the same registration.
    That is honest only if every choice D22's two verdicts depend on is fixed before any row after
    `DEV_END` is read. So while the authorisation is absent, the lock must be in the joint document
    and must fix the construction date, the cohort rule, the hedge legs including the option legs,
    the implied-volatility order and the verdict windows. With the authorisation present the same
    must hold, since a lock that disappeared after the read would be a lock that was never there.

    **Mutation:** the same check over a copy of the section with the construction date removed.
    """
    text = _read(sorted(DOCS.glob(f"{JOINT}*.md"))[0])
    start = text.find("### 6.1 D22's lock, fixed before the read")
    assert start >= 0, "DD168's option 1 without its price: D22 would be post-hoc"
    section = text[start : text.find("\n## 7.", start)]

    def missing(body: str) -> list[str]:
        required = (
            "DD171",
            "**2014-12-24**",
            "**40 firms, by rule.**",
            "**Rates and currency.**",
            "**bought**",
            "**six-month**",
            "**at-the-money**",
            "**Never sold**",
            "**An ordered list, and the first source available on the day decides.**",
            "**`NBER_2020` and `RATES_2022`**",
            "**PASS iff at least 60% of the cohort counts**",
            "**full daily variation margin, no threshold, no initial margin**",
            "**H15 is refused by name.**",
            "**A swap or a future, carried as cash**",
            "**A forward, carried at spot**",
            "\"futures-cash basis\", \"swap spread\"",
            "**on the Treasury curve and at spot**",
            "**Crude oil joins H16 and the option reports, never H15, if the owner admits its price route**",
            "WTI arm is refused by name and counted, and nothing below applies.**",
            "**one contract's two settles**",
            "DD177",
            "**if no equity source is admitted when D22 reads, H15 is refused by name and filter (iii) is",
            "hedging a product **with crude**",
        )
        return [phrase for phrase in required if phrase not in body]

    assert not missing(section), missing(section)
    assert missing(section.replace("**2014-12-24**", "2014-12-24")) == ["**2014-12-24**"]


def test_c171_the_three_results_only_routes_are_admitted_in_writing() -> None:
    """C171. DD178. D22's three results-only routes are admitted by a written, dated, named record.

    §6.2 asks three times for the owner's admission by name, and DD178 says it was given. That holds
    only while the record exists, names each route, names the condition §6.2 required (Alpha
    Vantage's investment-firm clause) and keeps every route out of git. The routes never enter
    `sources.ADMITTED`, which is for committed fixtures and which C125 pins at the credit tier's three.

    **Mutation:** the same check over the record with the affiliation clause removed.
    """
    record = DOCS / "OWNER_ADMISSION_d22_results_only_routes.md"
    assert record.exists(), "DD178 cites an admission that is not written down"
    registration = _read(sorted(DOCS.glob(f"{JOINT}*.md"))[0])
    assert record.name in registration, "DD178 must name the record it rests on"

    clause = (
        "**This admission lapses on the day the owner becomes employed by, or affiliated with, an "
        "investment"
    )

    def missing(body: str) -> list[str]:
        required = (
            "**Taken by the owner on 2026-09-26",
            "**EIA's NYMEX WTI futures, contracts 1 to 4, daily**",
            "**Alpha Vantage's free daily equity prices**",
            "**The Minneapolis Fed's option-implied distributions**",
            clause,
            "None may be committed",
            "**It does not authorise the first out-of-sample read.**",
        )
        return [phrase for phrase in required if phrase not in body]

    text = _read(record)
    assert not missing(text), missing(text)
    assert missing(text.replace(clause, "")) == [clause]


def test_c172_the_daily_route_does_not_reach_and_the_owner_chose_weekly() -> None:
    """C172. DD180, DD181. The admitted daily route fails on reach, and what replaced it is written.

    Alpha Vantage's free key serves the latest hundred sessions and nothing earlier, so §6.2's own
    rule refuses H15 by name and DD178's rule, read for what it is for, skips filter (iii). The owner
    then admitted weekly prices for D17's and D21's fits, extended the WTI route to D17 and ruled
    that every later row is dropped on arrival. Each is a new use of an admitted route, so each must
    be in the admission record verbatim, and the registration must say H15 is not re-scored weekly.

    **Mutation:** the same check over the registration with the refusal of a weekly H15 removed, and
    over the admission with the drop-on-arrival rule removed.
    """
    registration = _read(sorted(DOCS.glob(f"{JOINT}*.md"))[0])
    admission = _read(DOCS / "OWNER_ADMISSION_d22_results_only_routes.md")
    weekly_refused = "It is **not** re-scored on weekly prices"
    dropped = "Every row dated after 2014-12-24 is dropped on arrival"

    def missing(reg: str, adm: str) -> list[str]:
        needed = {
            "DD180 in the registration": "**DD180 — the admitted daily route does not reach" in reg,
            "H15 refused": "1. **H15 is refused by name**" in reg,
            "no weekly H15": weekly_refused in reg,
            "filter (iii) skipped": "2. **Filter (iii) is skipped.**" in reg,
            "the admission's section 6": "## 6. Three later decisions on two of these routes, 2026-09-26" in adm,
            "weekly + filings": "| **Weekly + filings**:" in adm,
            "WTI extended": "| **Extend it**:" in adm,
            "drop on arrival": dropped in adm,
            "the window change owned": "**the owner is told so and may say otherwise**" in adm,
        }
        return [name for name, ok in needed.items() if not ok]

    assert not missing(registration, admission), missing(registration, admission)
    assert missing(registration.replace(weekly_refused, ""), admission) == ["no weekly H15"]
    assert missing(registration, admission.replace(dropped, "")) == ["drop on arrival"]


def test_c191_the_fifth_reader_is_registered_before_the_read_and_named_by_the_assent(tmp_path: Path) -> None:
    """C191. DD199. D21 reads the record too, so it is registered before the first read and the
    owner's authorisation names five readers and both registration documents.

    DD134 counted four readers because D21 had no pre-commit when the rider was written, and nothing
    counted it afterwards: C119 checked four names, and C120 would have refused D21's document as a
    lone reader pre-commit the day it joined the list. The amendment keeps DD134's reason -- order,
    every reader's rules fixed before anyone's result -- and drops only the single document, which
    the joint registration's filename cannot stretch to. The exception is declared, with its reason,
    and held here as an equality.

    **Mutation:** an assent written against four readers and the joint document alone is refused,
    naming D21 and D21's document; one naming all five and both documents is accepted; and a second
    reader document outside the declared set is reported by C120's detector.
    """
    import test_guards_and_registers as registers

    declared = sorted(SEPARATE)
    reader_documents = sorted(
        path.name
        for path in DOCS.glob("PRECOMMIT_*.md")
        if not path.name.startswith(JOINT)
        and any(f"_d{reader[1:]}_" in path.name.lower() for reader in READERS)
    )
    assert reader_documents == declared, reader_documents
    assert sorted(READERS) == sorted(JOINT_READERS + tuple(p for name in SEPARATE for p in registers.packages_named(name)))
    for name in declared:
        text = _read(DOCS / name)
        for decision in ("DD133", "DD134", "DD199"):
            assert decision in text, f"{name} does not cite {decision}"
        if not AUTHORISATION.exists():
            assert registers.REGISTERED_MARKER in text, f"{name} lost its marker before the read"
        else:
            # Landed on its own read, 2026-09-29 (its section 13), under the authorisation that
            # named it; the rules above that section are C186's to hold.
            status = registers._status_lines(text)
            assert status == [] and "**Status: LANDED 2026-09-29.**" in text, status
            assert all(registers.closed(p, DOCS) for p in registers.packages_named(name))

    joint = _read(sorted(DOCS.glob(f"{JOINT}*.md"))[0])
    step_one = joint[joint.index("1. The owner commits `docs/OWNER_AUTHORISATION_the_first_oos_read.md`") :][:600]
    assert "DD199" in step_one and "five readers" in step_one, "§10 still asks the owner for four"
    rider = " ".join(line.lstrip("> ").strip() for line in _read(DOCS / "RIDER_X13_X14_one_surface_two_clocks.md").splitlines())
    assert "amended 2026-09-26 by DD199" in rider, "DD134 reads as though four were all there are"

    four = "DD37. D12, D14, D15, D22. PRECOMMIT_deskcraft_d12_d14_d15_d22_registration. 2026-09-26."
    problems = authorisation_problems(four)
    assert len(problems) == 2 and "D21" in problems[0] and "d21_hedge_backtest" in problems[1], problems
    five = four.replace("D22.", "D21, D22.") + " PRECOMMIT_deskcraft_d21_hedge_backtest."
    assert authorisation_problems(five) == []
    assert authorisation_problems(five.replace("2026-09-26", "2999-01-01")) == ["the authorisation is post-dated"]

    fake = tmp_path / "docs"
    fake.mkdir()
    for name in declared + ["PRECOMMIT_deskcraft_d21_second_thoughts.md"]:
        (fake / name).write_text("x", encoding="utf-8")
    assert lone_reader_precommits(fake) == ["PRECOMMIT_deskcraft_d21_second_thoughts.md"]


def test_c219_the_owners_decisions_before_the_read_are_written_where_each_was_asked() -> None:
    """C219. DD231-DD237. The owner's answers of 2026-09-28, in the registration's §12, and a line
    at each of the four places a question was asked.

    DD206, DD208, DD215 item 3 and the admission's §7 each left a decision to the owner and said what
    followed if it went unanswered. An answer written only in §12 would leave those four places
    reading as still open, so each carries a line after it naming the decision that answered it. The
    owner's reply was an instruction to carry out a list of recommendations, so §12 quotes it and says
    the owner may still say otherwise.

    **Mutation:** the same check with DD233's statement removed from §12, and with the line after
    D17's DD208 removed.
    """
    registration = _read(sorted(DOCS.glob(f"{JOINT}*.md"))[0])
    start = registration.find("## 12. The owner's decisions before the read, 2026-09-28")
    assert start >= 0, "the owner's answers of 2026-09-28 are not in the registration"
    section = registration[start:]

    statements = (
        "**DD231 — DD215 item 3's reading is accepted.**",
        "**H16 is reported as decided before the read**",
        "**DD232 — DD206 is answered: H12a, H14a and H14b stay as registered, and so does H16.**",
        "**H14a is reported as a claim the record could not fail in practice.**",
        "**H14b is reported as carried by noise on the rates-only firms.**",
        "**DD233 — DD208 is answered: D17's fixture stays as run, and nothing is re-run beside it.**",
        "**DD234 — the Minneapolis Fed's route is extended to D21, confirmed.**",
        "**DD235 — a listing was counted before it was dropped, and it moves nothing.**",
        "**DD236 — the DTCC request is not sent.**",
        "**DD237 — a dated deposit outside this machine, before the authorisation.**",
        "`tests/fixtures/panel_daily_admitted_dev_20260925.csv`**",
        "**The\n> upload is the owner's act**",
        "*\"complete all of these itrems in the way you suggested and in\nthe order that is most optimal "
        "and commplete it end to end\"*",
        "**the owner is told so and\nmay say otherwise**",
    )
    #: Each place a question was asked: where the question is, and the line that answers it.
    sites = {
        "D21's DD206": ("PRECOMMIT_deskcraft_d21_hedge_backtest.md", "> **DD206 —", "*Answered 2026-09-28 by DD232"),
        "D17's DD208": ("PRECOMMIT_deskcraft_d17_exposure_extractor.md", "> **DD208 —", "*Answered 2026-09-28 by DD233"),
        "DD215": (None, "> **DD215 —", "*Answered 2026-09-28 by DD231"),
        "the admission's §7": (
            "OWNER_ADMISSION_d22_results_only_routes.md",
            "## 7. One later decision on the Minneapolis Fed's route",
            "*Confirmed 2026-09-28 by DD234",
        ),
    }
    texts = {site: registration[:start] if name is None else _read(DOCS / name) for site, (name, _, _) in sites.items()}

    def missing(body: str, texts: dict[str, str]) -> list[str]:
        gaps = [phrase for phrase in statements if phrase not in body]
        for site, (_, question, answer) in sites.items():
            asked, answered = texts[site].find(question), texts[site].find(answer)
            if not 0 <= asked < answered:
                gaps.append(site)
        return gaps

    assert not missing(section, texts), missing(section, texts)
    assert missing(section.replace(statements[5], ""), texts) == [statements[5]]
    cut = dict(texts)
    cut["D17's DD208"] = cut["D17's DD208"].replace(sites["D17's DD208"][2], "")
    assert missing(section, cut) == ["D17's DD208"]
