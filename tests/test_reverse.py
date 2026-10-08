"""C208-C212. D13: reverse stress (`PRECOMMIT_deskcraft_d13_reverse_stress.md`).

DEV only: the committed panels and the two books the joint registration §2 names, at 2014-12-24. The
closed form is held against D9's Euler decomposition, which DD221 says it is on one covariance, and
against brute force on synthetic cases whose answer is known.
"""

from __future__ import annotations

import math
from datetime import date, timedelta

import numpy as np
import pytest

from deskcraft import covariance as cv
from deskcraft import reverse as r
from deskcraft.attribution import gaussian_risk
from deskcraft.registers import CLAIMS
from deskcraft.views import REFERENCE_VIEW
from deskcraft.window import FitWindow
from test_deskcraft_boundary import REPO_ROOT, _read

PRECOMMIT = REPO_ROOT / "docs" / "PRECOMMIT_deskcraft_d13_reverse_stress.md"

FIXED = (
    "**DD220 — the stated loss is the budget, in one session.**",
    "**L = $1,000,000 lost in one session**",
    "Δ*  =  −L · Σe / (e′Σe),        distance  d  =  L / √(e′Σe)",
    "**D9's Euler share, exactly**",
    "d = φ(z)/(1 − α) = **2.3378** at α = 97.5%",
    "**DD222 — the same breach on the other covariances.**",
    "**d_C = L / √(e′Σ_C e)**",
    "**its distance under `SAMPLE`**",
    "**D9's series set**",
    "**Every distance and every scenario is taken over the series the book holds**",
    "**The cosine is taken in `SAMPLE`'s own metric**",
    "**DD223 — the breaches that happened.**",
    "**their count** against the Gaussian expectation T·(1 − Φ(2.3378))",
    "**the most plausible of them**",
    "**DD224 — `US_CASH_BOOK`'s euro is kept.**",
)


def _flat(text: str) -> str:
    return " ".join(line.lstrip("> ").strip() for line in text.splitlines())


@pytest.fixture(scope="module")
def books():
    basis, levels, (cash, constructed) = r.the_two_books()
    return basis, levels, {"cash": r.run_d13(cash, basis, levels), "constructed": r.run_d13(constructed, basis, levels)}


def test_c208_d13s_rules_are_written_before_its_numbers() -> None:
    """C208. DD220-DD224 and the predictions, as the pre-commit spells them; D13 scores no claim.

    **Mutation:** the sentence fixing the cosine's metric removed is reported.
    """
    text = _flat(_read(PRECOMMIT))
    missing = [phrase for phrase in FIXED if phrase not in text]
    assert not missing, missing
    metric = "**The cosine is taken in `SAMPLE`'s own metric**"
    assert [p for p in FIXED if p not in text.replace(metric, "")] == [metric]
    for prediction in ("P1", "P2", "P3", "P4", "P5", "P6", "P7"):
        assert f"| **{prediction}** |" in _read(PRECOMMIT), prediction
    assert not [c for c in CLAIMS if c.scorer == "D13"]
    assert round(r.ES_SCALE, 4) == 2.3378


def test_c209_the_closed_form_is_the_nearest_breach_and_on_one_covariance_it_is_d9(books) -> None:
    """C209. DD221. On a synthetic covariance Δ* loses exactly L at distance L/√(e′Σe), and no other
    move losing L is nearer. On both real books, on `SAMPLE`: the distance is φ(z)/(1 − α), and the
    per-leg shares and the on-thesis share are D9's Gaussian report's, to 1e-12.

    **Mutation:** a scenario along e rather than Σe loses L and is further away.
    """
    rng = np.random.default_rng(13)
    a = rng.standard_normal((4, 4))
    sigma = a @ a.T + 0.5 * np.eye(4)
    e = np.array([3.0, -1.0, 2.0, 0.5])
    scenario, distance = r.most_plausible(e, sigma, 7.0)
    assert math.isclose(-(e @ scenario), 7.0, rel_tol=1e-12)
    assert math.isclose(r.mahalanobis(scenario, sigma), distance, rel_tol=1e-12)
    assert math.isclose(distance, 7.0 / math.sqrt(e @ sigma @ e), rel_tol=1e-12)
    for _ in range(200):
        direction = rng.standard_normal(4)
        if e @ direction >= 0.0:
            direction = -direction
        other = direction * 7.0 / -(e @ direction)
        assert r.mahalanobis(other, sigma) >= distance - 1e-12
    along_e = -7.0 * e / (e @ e)
    assert r.mahalanobis(along_e, sigma) > distance

    basis, levels, results = books
    for name, result in results.items():
        breach = result.on("SAMPLE")
        assert math.isclose(breach.distance, r.ES_SCALE, rel_tol=1e-12), name
        assert breach.alignment == pytest.approx(1.0, abs=1e-12)
        assert math.isclose(sum(breach.leg_shares.values()), 1.0, rel_tol=1e-12)
        assert math.isclose(sum(breach.series_shares.values()), 1.0, rel_tol=1e-12)
    cash = results["cash"]
    from deskcraft.reference import US_CASH_BOOK

    report = gaussian_risk(US_CASH_BOOK, REFERENCE_VIEW, basis, levels, window=r.REAL_FIT)
    for leg in report.legs:
        assert math.isclose(cash.on("SAMPLE").leg_shares[leg.leg_id], leg.share, rel_tol=1e-12), leg.leg_id
    assert math.isclose(cash.on("SAMPLE").on_thesis, sum(leg.on_thesis for leg in report.legs) / report.es, rel_tol=1e-12)


def test_c210_every_covariance_the_series_reach_is_reported_and_the_rest_refused(books) -> None:
    """C210. DD222. `US_CASH_BOOK` holds TIPS and the euro, so D8's 1990 and 2001 windows are refused
    by name and 2007-09 is reported; the constructed book, on GSW zeros alone, reaches all three. No
    scenario on another covariance is nearer to `SAMPLE` than `SAMPLE`'s own, and every scenario loses
    exactly L.

    **Mutation:** a covariance whose variances are all doubled moves the distance by 1/√2 and leaves
    the scenario's direction, so its cosine with `SAMPLE`'s is 1.
    """
    _, _, results = books
    cash, constructed = results["cash"], results["constructed"]
    names = ("SAMPLE", "LEDOIT_WOLF", "EWMA", "NBER_1990", "NBER_2001", "NBER_2007")
    assert [b.covariance for b in cash.breaches] == list(names)
    assert [b.covariance for b in constructed.breaches] == list(names)
    assert [b.covariance for b in cash.breaches if b.refused] == ["NBER_1990", "NBER_2001"]
    assert not [b.covariance for b in constructed.breaches if b.refused]
    for result in (cash, constructed):
        e = result.book.exposure[result.book.block()]
        for breach in result.breaches:
            if breach.refused:
                assert "cannot identify" in breach.refused
                continue
            move = np.array([breach.scenario[s] for s in result.book.held])
            assert math.isclose(-(e @ move), r.LOSS, rel_tol=1e-10), breach.covariance
            assert breach.sample_distance >= r.ES_SCALE - 1e-9, breach.covariance
            assert -1.0 - 1e-12 <= breach.alignment <= 1.0 + 1e-12

    sample = cv.fit(cash.book.series, r.REAL_FIT).array()
    scenario, distance = r.most_plausible(cash.book.exposure, sample)
    wider, far = r.most_plausible(cash.book.exposure, 2.0 * sample)
    assert math.isclose(far, distance / math.sqrt(2.0), rel_tol=1e-12)
    held = cash.book.block()
    assert math.isclose(r.sample_cosine(scenario[held], wider[held], sample[np.ix_(held, held)]), 1.0, rel_tol=1e-12)


def test_c211_the_breaches_that_happened_are_counted_and_the_nearest_is_found(monkeypatch) -> None:
    """C211. DD223 on a synthetic panel whose answer is known: two series, four sessions, a book that
    loses on both. The breaches are the sessions losing at least L; the nearest is the one of least
    `SAMPLE` distance, which is not the largest loss; and the Gaussian expectation is T·(1 − Φ(2.3378)).

    **Mutation:** the budget raised above every loss leaves no breach and no nearest session.
    """
    days = tuple(date(2010, 1, 4) + timedelta(days=i) for i in range(4))
    changes = np.array([[-10.0, 0.0], [0.0, -10.0], [-30.0, -30.0], [1.0, 1.0]])
    sigma = np.array([[100.0, 0.0], [0.0, 25.0]])
    book = r.Exposed("toy", ("A", "B"), ("A", "B"), ("a", "b"), np.array([[1.0, 0.0], [0.0, 1.0]]), np.array([1.0, 0.0]))
    monkeypatch.setattr(r.cv, "daily_changes", lambda series, window: (days, changes, 0))
    monkeypatch.setattr(r, "LOSS", 10.0)
    found = r.historical(book, FitWindow.dev(), sigma)
    assert (found.sessions, found.breaches) == (4, 3)
    assert found.nearest == days[0] and math.isclose(found.nearest_distance, 1.0)
    assert found.nearest_move == {"A": -10.0, "B": 0.0}
    assert math.isclose(found.expected, 4 * (1.0 - 0.990300), rel_tol=1e-3)
    monkeypatch.setattr(r, "LOSS", 1e6)
    none = r.historical(book, FitWindow.dev(), sigma)
    assert (none.breaches, none.nearest) == (0, None)


def test_c212_the_run_on_dev_is_section_9s(books) -> None:
    """C212. §9's tables, recomputed: the distances, the scenarios' shares and cosines, and history,
    for both books. And §9.1's and §9.2's two findings: the euro's P&L correlates with the rates legs'
    at 0.006 on `SAMPLE` and 0.61 on the construction date's EWMA, and the constructed book's two
    30-year DV01s cancel exactly, leaving the 10-year alone.

    **Mutation:** P3's prediction, the construction date's EWMA above 2.3378, is false on the run.
    """
    _, _, results = books
    cash, constructed = results["cash"], results["constructed"]
    got = {b.covariance: (round(b.distance, 4), round(b.alignment, 4)) for b in cash.breaches if not b.refused}
    assert got == {
        "SAMPLE": (2.3378, 1.0),
        "LEDOIT_WOLF": (2.3397, 1.0),
        "EWMA": (2.2938, 0.9272),
        "NBER_2007": (1.5455, 0.9746),
    }
    assert not cash.on("EWMA").distance > r.ES_SCALE, "P3 was wrong, and §9 says so"
    shares = {name: round(cash.on(name).leg_shares["eurusd"], 4) for name in got}
    assert shares == {"SAMPLE": 0.4768, "LEDOIT_WOLF": 0.4769, "EWMA": 0.5467, "NBER_2007": 0.4241}
    assert all(max(cash.on(name).leg_shares, key=cash.on(name).leg_shares.get) == "eurusd" for name in got)
    history = cash.history
    assert (history.sessions, history.breaches, round(history.expected, 1)) == (2997, 50, 29.1)
    assert (history.nearest, round(history.nearest_distance, 4)) == (date(2004, 5, 17), 2.3799)

    sample = cv.fit(cash.book.series, r.REAL_FIT).array()
    ewma = cv.fit(cash.book.series, r.REAL_FIT, cv.Method.EWMA).array()
    rates, euro = cash.book.matrix[:3].sum(axis=0), cash.book.matrix[3]
    corr = [float(rates @ s @ euro) / math.sqrt(float(rates @ s @ rates) * float(euro @ s @ euro)) for s in (sample, ewma)]
    assert [round(c, 4) for c in corr] == [0.0057, 0.6056]

    exposure = dict(zip(constructed.book.series, constructed.book.exposure))
    assert exposure["SVENY30"] == 0.0 and round(exposure["SVENY10"], 2) == 70856.22
    assert constructed.book.matrix[0][constructed.book.series.index("SVENY30")] == -constructed.book.matrix[1][
        constructed.book.series.index("SVENY30")
    ]
    got = {b.covariance: round(b.distance, 4) for b in constructed.breaches}
    assert got == {"SAMPLE": 2.3378, "LEDOIT_WOLF": 2.338, "EWMA": 2.7704, "NBER_1990": 2.1761,
                   "NBER_2001": 2.2304, "NBER_2007": 1.5071}
    assert {round(b.scenario["SVENY10"], 3) for b in constructed.breaches} == {-14.113}
    history = constructed.history
    assert (history.sessions, history.breaches, round(history.expected, 1), history.nearest) == (
        6730, 85, 65.3, date(1996, 10, 29)
    )
