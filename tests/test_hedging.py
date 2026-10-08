"""C179-C185. D18: the menu, the gate, H13 and the grammar (`PRECOMMIT_deskcraft_d18_structures_and_gate.md`).

Every exposure here is D17's committed stated fixture or invented; nothing reads a price after the
construction date, and nothing touches the network.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from dataclasses import fields
from datetime import date
from pathlib import Path

import pytest
from upstream_certificate import OPTION_VALUES, digest

from deskcraft import hedging as h
from deskcraft.costs import DurationConvention
from deskcraft.factors import FACTOR_SERIES, build_basis
from deskcraft.generator import candidate_legs, select
from deskcraft.panel import FitWindow, load_daily
from deskcraft.registers import CLAIMS, Verdict
from deskcraft.sensitivity import CurveShift, leg_pnl
from deskcraft.views import UnreachableFactor, compile_view
from test_deskcraft_boundary import REPO_ROOT

FIXTURES = REPO_ROOT / "tests" / "fixtures"
STATED = FIXTURES / "d17_stated_dev_20260926.csv"
#: The sibling that prices deskcraft's option legs (DD168 item 4). Blanked on the simulated clean
#: machine by `absent_machine.UPSTREAM_CONSTANTS`, so the path below is derived at call time.
OPTCRAFT = REPO_ROOT.parent / "optcraft"


def _optcraft_models():
    path = OPTCRAFT / "src" / "optcraft" / "models.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("optcraft_models_for_c179", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _grid() -> list[tuple[str, bool, float, float, float, float]]:
    out = []
    for call in (True, False):
        for tau in (0.25, 1.0, 5.0):
            for vol in (0.05, 0.2, 0.8):
                for strike in (0.7, 1.0, 1.3):
                    out.append(("GK", call, 1.1, strike, tau, vol))
                    out.append(("B76", call, 1.0, strike, tau, vol))
            for vol in (0.1, 0.5, 1.0):
                for strike in (-0.5, 0.3451, 1.5):
                    out.append(("N", call, 0.3451, strike, tau, vol))
    return out


def _ours(model: str, call: bool, s: float, k: float, tau: float, vol: float) -> float:
    if model == "GK":
        return float(h.gk_value(call, s, k, tau, vol, 0.01, 0.02))
    if model == "B76":
        return float(h.black76_value(call, s, k, tau, vol, 0.01))
    return float(h.bachelier_value(call, s, k, tau, vol, 0.01))


def test_c179_the_restated_values_are_optcrafts(tmp_path: Path) -> None:
    """C179. DD196. GK, Black-76 and Bachelier values equal optcraft's exactly, calls and puts.

    Off-machine the equality is against the certificate, a digest of optcraft's own answers taken
    2026-09-26 at optcraft `ae7128f`; `repr` round-trips a float, so it stays an equality.

    **Mutation:** a Bachelier value with the discount factor applied twice leaves the certificate.
    """
    grid = _grid()
    assert len(grid) == 162
    ours = [_ours(*point) for point in grid]
    assert digest(ours) == OPTION_VALUES, "the restatement has left optcraft's certified answers"

    twice = [
        value * math.exp(-0.01 * point[4]) if point[0] == "N" else value
        for point, value in zip(grid, ours, strict=True)
    ]
    assert digest(twice) != OPTION_VALUES

    theirs = _optcraft_models()
    if theirs is None:
        return
    name = {"GK": "GARMAN_KOHLHAGEN", "B76": "BLACK76", "N": "BACHELIER"}
    answers = []
    for (model, call, s, k, tau, vol), mine in zip(grid, ours, strict=True):
        carry = 0.02 if model == "GK" else 0.0
        answer = float(theirs.price(theirs.Model[name[model]], call, s, k, tau, vol, 0.01, carry))
        assert mine == answer, f"restatement diverges at {model} call={call} s={s} k={k} tau={tau} vol={vol}"
        answers.append(answer)
    assert digest(answers) == OPTION_VALUES, "optcraft's answers have moved; regenerate the certificate"


def _long(model: str) -> h.Exposure:
    cls = {"GK": "currency", "B76": "crude", "N": "rates"}[model]
    return h.Exposure(1, "0", cls, "X", 1, 1.0e9)


def test_c180_only_selling_more_than_you_hedge_beats_the_forward() -> None:
    """C180. §3, X16's experiment. At one strike and zero premium, the protected rate beats the
    forward by (p - 1) x one sold option, above zero iff p > 1, in both families, for a firm long
    or short, at every rung of both ladders.

    **Mutation:** p = 1 is the forward itself; its improvement is zero, not above it.
    """
    for model, forward, ladder in (
        ("GK", 1.0, h.LOGNORMAL_LADDER),
        ("B76", 1.0, h.LOGNORMAL_LADDER),
        ("N", 0.3451, h.NORMAL_LADDER),
        ("N", -0.5, h.NORMAL_LADDER),
    ):
        for sign in (1, -1):
            base = _long(model)
            exposure = h.Exposure(1, "0", base.cls, "X", sign, 1.0e9)
            m, unit, a = exposure.model, h._unit(exposure.model), exposure.adverse
            for vol in ladder:
                for p in (0.5, 1.0, 2.0, 3.0):
                    k = h._solve(
                        m, forward, vol,
                        lambda k, p=p: h._value(m, exposure.protective, forward, k, vol)
                        - p * h._value(m, exposure.opposite, forward, k, vol),
                    )
                    improvement = -a * (k - forward) * unit
                    sold = h._value(m, exposure.opposite, forward, k, vol) * unit
                    assert abs(improvement - (p - 1.0) * sold) <= 1e-12, (model, sign, vol, p)
                    if p == 1.0:
                        assert abs(improvement) <= 1e-12
                    else:
                        assert (improvement > 0.0) == (p > 1.0), (model, sign, vol, p)


def _ge() -> h.Exposure:
    return h.case_exposures(h.load_stated(STATED))[0]


def test_c181_the_gate_is_a_type_and_refuses_leverage() -> None:
    """C181. DD194. Four structures construct; the ratio forward does not; a wrong declaration,
    a leg that pays the wrong way and a structure with no protection all raise.
    """
    ge = _ge()
    level, ewma = h.rates_at_construction()
    menu = {p.name: p for p in h.price_menu(ge, level, ewma)}
    for name in ("forward", "bought option", "zero-cost collar", "participating forward"):
        built = h.HedgeStructure(ge, menu[name].legs, menu[name].obligation)
        assert built.leverage <= 1.0
    with pytest.raises(h.Unsuitable, match="leverage 2.0"):
        h.HedgeStructure(ge, menu["2:1 ratio forward"].legs, 2.0)

    collar = menu["zero-cost collar"].legs
    with pytest.raises(h.Unsuitable, match="declares a worst-state obligation of 0.5"):
        h.HedgeStructure(ge, collar, 0.5)
    only_sold = (collar[1],)
    with pytest.raises(h.Unsuitable, match="hedges nothing"):
        h.HedgeStructure(ge, only_sold, 1.0)
    wrong_forward = (h.StructureLeg(h.Payoff.FORWARD, h.Side.SOLD, 1.0, level),)
    with pytest.raises(h.Unsuitable, match="hedges nothing"):
        h.HedgeStructure(ge, wrong_forward, 1.0)
    wrong_option = (h.StructureLeg(h.Payoff.PUT, h.Side.BOUGHT, 1.0, level),)
    with pytest.raises(h.Unsuitable, match="hedges nothing"):
        h.HedgeStructure(ge, wrong_option, 0.0)


def test_c182_premium_paid_and_optionality_sold_are_never_netted() -> None:
    """C182. DD195. Two fields; the collar's are both above zero with net premium zero. Only
    `headline_cost`, a property named for the objective, nets them.

    **Mutation:** a field added to `Priced` turns the equality below red until it is named.
    """
    ge = _ge()
    level, ewma = h.rates_at_construction()
    collar = next(p for p in h.price_menu(ge, level, ewma) if p.name == "zero-cost collar")
    assert collar.premium_paid > 0.0 and collar.optionality_sold > 0.0
    assert abs(collar.premium_paid - collar.optionality_sold) <= 1e-15
    assert {f.name for f in fields(h.Priced)} == {
        "name", "legs", "obligation", "premium_paid", "optionality_sold",
        "forward", "protected", "rate_improvement",
    }
    assert isinstance(h.Priced.headline_cost, property)


def test_c183_h13_passes_and_could_not_have_done_otherwise() -> None:
    """C183. H13, §3. Each case client's largest exposure, every rung: the unconstrained pick is
    the ratio forward and the gate refuses it; the constrained pick is the forward. 3 of 3.

    **Mutation:** with the ratio forward struck from the menu the unconstrained pick is the
    forward everywhere and the count is zero, which is §3's other half.
    """
    level, ewma = h.rates_at_construction()
    cases = []
    for exposure in h.case_exposures(h.load_stated(STATED)):
        forward = level if exposure.model is h.Model.BACHELIER else 1.0
        case = h.score_case(exposure, forward, h.rungs_for(exposure, ewma if exposure.cls == "rates" else None))
        assert all(r.unconstrained == "2:1 ratio forward" and r.refused for r in case.rungs)
        assert all(r.constrained == "forward" for r in case.rungs)
        cases.append(case)
    result = h.h13(tuple(cases))
    assert result.counted == 3 and result.verdict is Verdict.PASS
    assert next(c for c in CLAIMS if c.claim_id == "H13").verdict is Verdict.PASS

    for case in cases:
        forward = level if case.exposure.model is h.Model.BACHELIER else 1.0
        for vol, _ in h.rungs_for(case.exposure):
            menu = tuple(p for p in h.price_menu(case.exposure, forward, vol) if p.name != "2:1 ratio forward")
            assert h.unconstrained_pick(menu).name == "forward"


def test_c184_an_exposure_is_a_target_d7b_runs_on_unchanged() -> None:
    """C184. DD197. GE's hedge target compiles to +1 on `SVENY01`, D7b takes `OUT_SVENY01` alone
    at cosine 1, and that leg gains when `SVENY01` rises. A series outside the pool is refused.
    """
    ge = _ge()
    basis = build_basis()
    target = h.hedge_target((ge,))
    compiled = compile_view(target, basis)
    unit = [value / compiled.norm for value in compiled.vector]
    assert unit == [1.0 if series == "SVENY01" else 0.0 for series in FACTOR_SERIES]

    daily = load_daily(FitWindow.dev())
    row = daily.dates.index(date(2014, 12, 24))
    yields = {s: v for s in daily.series if (v := daily.values[s][row]) is not None}
    selection = select(target, basis, yields, convention=DurationConvention.AS_QUOTED)
    assert [a.symbol for a in selection.additions] == ["OUT_SVENY01"]
    assert math.isclose(selection.cosine, 1.0, abs_tol=1e-12)
    leg = next(leg for leg in candidate_legs() if leg.leg_id == selection.additions[0].leg_id)
    assert leg_pnl(leg, CurveShift((("SVENY01", 1.0),)), yields) > 0.0

    euro = next(e for e in h.load_stated(STATED) if e.instrument == "EUR")
    with pytest.raises(UnreachableFactor):
        h.hedge_target((euro,))


def test_c185_the_case_table_is_d17s_stated_exposure() -> None:
    """C185. §0 and P4. The three case clients' largest exposures, the construction-date inputs,
    and GE's dollar figures at the EWMA rung.
    """
    cases = h.case_exposures(h.load_stated(STATED))
    assert [(c.cohort_rank, c.cls, c.instrument, c.sign, c.amount_usd) for c in cases] == [
        (1, "rates", "SVENY01", -1, 77_890_000_000.0),
        (2, "crude", "WTI_C2", -1, 244_156_000_000.0),
        (3, "rates", "SVENY01", -1, 20_000_000.0),
    ]
    level, ewma = h.rates_at_construction()
    assert round(level, 4) == 0.3451 and round(ewma, 4) == 0.2693

    ge = cases[0]
    menu = {p.name: p for p in h.price_menu(ge, level, ewma)}
    dollars = ge.amount_usd / 1e6
    assert round(menu["bought option"].premium_paid * dollars, 1) == 83.7
    ratio = menu["2:1 ratio forward"]
    assert round(ratio.rate_improvement * dollars, 1) == 57.9
    assert round((level - ratio.protected) * 100.0, 2) == 7.43
    sold = next(leg for leg in ratio.legs if leg.side is h.Side.SOLD)
    assert sold.payoff is h.Payoff.PUT and sold.multiple * ge.amount_usd == 155_780_000_000.0
