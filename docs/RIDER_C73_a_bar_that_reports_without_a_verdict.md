# Rider — C73 reports a verdict it never reached, and the echo was the symptom

*Raised and closed 2026-09-16, against `tests/test_environment_census.py` (C73) and
`RIDER_A4_the_date_and_two_unowned_findings.md` §7.1.*

*The A4 rider closed by annotating C73's docstring with a warning to human readers: **"a red here is
usually an echo … before predicting how many bars a change reddens, add this one."** That is a sign
posted next to a hole. Asked whether the hole was filled, the answer was no — so this fills it, and
the sign comes down.*

*Adds no package. The budget stands at 21.*

---

## 0. Measured before decided

| # | Measured | Value |
|---|---|---|
| 1 | Which of C73's two assertions fires when an unrelated bar is red | **`assert completed.returncode == 0`** — the gate, not the census |
| 2 | Whether C73's declared subject is evaluated when that fires | **No.** The census line is never reached |
| 3 | What the red says | *"the suite does not pass on a machine with neither sibling repository, which is the only machine a reviewer has"* — **the siblings are irrelevant to the actual cause** |
| 4 | Whether the skip report exists in a failing child | **Yes** — the plugin writes it at `pytest_sessionfinish`, whatever the exit status |
| 5 | Reds produced by removing one register declaration | **3** — two real, one echo |
| 6 | Prior instance of this exact defect in this repo | **X8**, against `lint-imports` — *"Exit code alone cannot tell a verdict from no verdict"* |

---

## 1. The defect, which is not the echo

C73 is named `test_a_clean_machine_skips_exactly_the_declared_bars` and its docstring says its
subject is the skip census. It carries **two** assertions:

```python
assert completed.returncode == 0, "the suite does not pass on a machine with neither sibling …"
assert observed == EXPECTED_SKIPS, {...}
```

The first is a **gate** — *the suite passes without the siblings*. The second is the **census** — the
bar's declared subject. They are different claims, and the first runs first.

So when any unrelated bar is red: C73 fails on the gate, **the census never executes**, and the
message blames the absent sibling repositories for a failure that has nothing to do with them.
A reader seeing that red learns something false, and learns nothing about whether the skip census
still holds.

**This is X8's finding, indoors.** X8 recorded — *"found while closing X8"*, and it is the one row
in §4 of the carried-items register that was never proposed by anyone — that **a refused
`lint-imports` configuration exits `1` exactly as a broken contract does**, so *"exit code alone
cannot tell a verdict from no verdict"*. The fix there was to stop reading the exit code and read
the `Contracts:` line instead (`test_import_contract.py`). **C73 then did to its own child exactly
what `lint-imports` had done to us** — and it was written after the lesson, by the same hand, in the
same week.

**The echo was never the disease.** A whole-suite gate *must* notice a red suite; that part is
correct and cannot be designed away. What is wrong is that a bar with no verdict reports a verdict,
in someone else's name.

---

## 2. What replaces it (DD104, DD105)

**Split the two claims, and let each one reach a verdict.**

### 2.1 C73 keeps the census, and always evaluates it (DD104)

The skip report is written at `pytest_sessionfinish` regardless of exit status (measurement 4), so
the observed skips are available whether or not the child passed. C73 now reads them and asserts the
equality **unconditionally**. Its verdict is about its own subject, always.

### 2.2 C99 takes the gate, and distinguishes breakage from an echo (DD105)

The child now also reports its **failing** node ids. When the child fails, C99 re-runs exactly those
ids **on this machine, without the plugin**, and splits them:

| Failing on the clean machine | Failing here too | Verdict |
|---|---|---|
| none | — | **PASS** — the suite passes without the siblings |
| some | **no** | **FAIL** — genuine clean-machine breakage, and the ids are named |
| some | **yes**, all of them | **NO VERDICT** — skipped, naming them as echoes |

The third row is the whole point, and it is X8's disposition applied to ourselves: **a bar that
cannot evaluate its subject says so instead of failing in its subject's name.** The suite is already
red; the clean-machine property has not been falsified, because the suite does not pass anywhere.

**Cost is zero in the green case** — the re-run happens only when the child has already failed.

### 2.3 The census believed a skip was always environmental (DD106)

**Unpredicted, and found by the first application.** Adding C99 turned **C72** red: the
environment census treats reaching `pytest.skip` as proof that a bar depends on a sibling
repository, and C99 skips because *the suite is red*. Declaring it `SKIPS` would have put it in
`EXPECTED_SKIPS` — asserting that a clean machine must skip it, which is false, since on a clean
green machine it passes.

The signal was right about every bar in this repository until this one, which is precisely why it
was never examined. **A static scan can see that a bar *can* skip and can never see why.** So the
census gains a third kind, `SKIPS_ON_A_RED_SUITE`, and the comparison in C72 normalises it back to
`SKIPS` before meeting the scanner: **the scanner reports a capability, the census reports a
cause**, and `EXPECTED_SKIPS` — the thing a clean machine is actually held to — is derived from the
cause. Nineteen conditional bars now, still **seven** skipping off-machine.

---

## 3. What this does and does not solve

**Solved.** The misdiagnosis: a red that blamed the sibling repositories for an unrelated failure.
The silent census: C73's declared subject now always gets a verdict. And the arithmetic that three
documents kept getting wrong — **`n` failing bars now produce `n` reds**, because the echo becomes a
skip rather than a third red.

~~**Not solved, and not solvable.** A genuine clean-machine breakage that coincides with an
unrelated red is still reported as an echo, because every failing id fails here too and C99 cannot
tell which one would also have failed for the *other* reason. That is a strictly smaller hole than
the one it replaces and it is stated rather than papered over.~~

> **Corrected 2026-09-16 (DD108), in the open rather than by editing**, because a claim quietly
> revised inside a landed pre-registration is indistinguishable from one that was never made.
> **The paragraph above is false, and it was false on the day it landed.**
>
> Two *different* bars — one broken by the absent siblings, one red anyway — are separated
> correctly. C99 subtracts the sets, so a genuine break survives any number of unrelated reds
> beside it. **C99b asserts exactly this, in this same commit**, four lines under a comment that
> says *"The genuine one must survive the echo"*; and the state was built and put to the real bar,
> which answered `broken`, naming only the genuine break.
>
> The residual is **one bar failing both ways for two different reasons** — one bar, not two. It
> is undecidable at this interface because `clean_machine_verdict` is handed node ids and a cause
> is not among them, which **C101** now holds by reading the signature: the limit is derived from
> the domain instead of asserted in prose. See
> `RIDER_two_claims_that_something_could_not_be_done.md`.

**The sign comes down.** C73's docstring told the reader to remember to add the echo. With the echo
gone the instruction would be wrong, so it is replaced by what is now true. **A warning in a
docstring was the wrong instrument, and leaving it in place after fixing the hole would have been
the same mistake twice.**

---

## 4. Predictions

| | Prediction |
|---|---|
| **P1** | Suite 105 → **107** — C99 and its mutation C99b, counted against the bars actually written |
| **P2** | Removing one register declaration now reddens **exactly 2**, with C99 **skipped**, where today it reddens 3 |
| **P3** | Clean-machine goes 98 → **100** passed and stays at **7** skips — C99 passes there and C99b is not environment-conditional |
| **P4** | `EXPECTED_SKIPS` is unmoved: C99's skip is conditional on a red suite and the tree is green |
| **P5** | Gates clean; `registers.py` out of the diff; **0** post-DEV rows |

**P2 is the one that matters** — it is the claim that the hole is actually filled — and it is scored
by running the probe, not by argument. **P3's skip count is the one most likely to be wrong**, on
the A3/A4/rider record: three predictions about this machinery, three misses.

---

## 5. What this could still get wrong

- **C99 re-runs failing node ids in a third process**, so a bar that fails only when run alongside
  its neighbours — shared state, ordering — would be classified as clean-machine breakage when it is
  really an interaction. No such bar is known here, and the suite is stateless by construction, but
  the classification rests on that.
- **A skip is easy to stop reading.** C99's no-verdict case is honest and it is also quiet; if the
  suite were left red for a long time, the clean-machine property would go unchecked without anyone
  noticing. The mitigation is that the property is only unchecked while something else is already
  red, which is not a state this repository tolerates.
- **This makes the red count predictable and does not make me predict it.** The three misses across
  A3, A4 and the A4 rider were not caused by the echo being hard to reason about; they were caused
  by predicting before measuring. Removing the trap removes this instance, not the habit.

---

## 6. Result

**CLOSED 2026-09-16.** Bars **C99**, **C99b**; decisions **DD104–DD106**. Suite **105 → 107**,
green. Clean-machine **100 passed, 7 skipped** — the *7* held. `ruff` 0 findings; `lint-imports`
**2 kept, 0 broken**. Bar ids **107 claimed, no duplicates, no gaps, C1 → C99**. `registers.py`
never entered the diff; `src/` untouched entirely. **0 rows dated after `DEV_END`.**
**Next free: C100 / DD107.**

| | Prediction | Verdict |
|---|---|---|
| **P1** | Suite 105 → 107 | HELD exactly |
| **P2** | One declaration removed reddens **2**, C99 skipped, where it was 3 | **HELD — measured** |
| **P3** | Clean-machine 98 → 100 passed, still 7 skips | HELD |
| **P4** | `EXPECTED_SKIPS` unmoved | HELD |
| **P5** | Gates clean, `registers.py` out of the diff, 0 post-DEV rows | HELD |

**Five of five — and §4 said why that is the weak kind of run.** Every prediction was about this
rider's own mechanics. The one that mattered, P2, is the one that was scored by running the probe:

```
2 failed, 104 passed, 1 skipped
SKIPPED  no verdict: every bar that failed without the sibling repositories fails with
         them too, so the suite is red for a reason that has nothing to do with a
         reviewer's machine. Fix those and this bar speaks again: ...
```

**Three reds became two, and the third now explains itself.**

### 6.1 What the predictions did not anticipate

**C72 went red on the first application**, and none of the five predictions saw it coming. That red
is §2.3 — the census had encoded *"a bar that can skip depends on the environment"*, true of every
bar written before C99 and false of C99. It is a better finding than anything §4 predicted, and it
arrived the way the useful ones keep arriving in this repository: **a guard aimed at something else
refused the change.**

It is also the fourth consecutive time a prediction missed the *mechanism* while the *counts* came
out right. The counts held here only because C72's red was fixed before the final run — which is
what a prediction written before the work always gets to do, and worth naming rather than banking.

### 6.2 The answer to the question that prompted this

The A4 rider closed by annotating C73's docstring: *"before predicting how many bars a change
reddens, add this one."* **That was a sign next to a hole, and it was the same instrument this
repository has now failed with four times** — A2's *"this document cannot write it"*, A3's unowned
class, A4 §8's unowned bullet, and a docstring warning. Prose naming a defect is not a fix.

The hole is filled: C73 reaches a verdict on its own subject in every run, C99 owns the gate and
can tell breakage from an echo, and **`n` failing bars now produce `n` reds**. The sign has been
taken down, because with the echo gone the instruction it gave would be wrong — and leaving it
there would have been the same mistake a fifth time.

**What is not fixed** is the habit that made all four necessary: predicting before measuring. This
rider removed one trap. It did not make me measure first, and §5 said so before the run rather than
after.
