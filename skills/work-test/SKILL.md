---
name: work-test
description: Step 7 of work-flow. Tests the change after it is built: the proof for the task type, edge cases, regression in callers, all the checks against the baseline, and a real run on the environment where the problem was seen. Use through work-flow after the build phase, or directly to test the changes on the current branch.
---

# Step 7: test the change

Obeys the contract in `work-flow`. Work on the work branch. You can add and
change test files. Change product code only to fix a defect that this step finds.

The build step proved that the change works one time. This step looks for
the cases where it fails.

## Do

1. **Proof.** Run the proof for the task type again. Confirm that it tests
   the real behaviour and not a mock. For a bug, remove the fix, confirm
   that the test fails, and put the fix back.
2. **Edge cases.** List the cases that the change can get wrong. For each
   one, test it or say why it does not apply:
   - empty, null, missing, zero, negative, very large
   - boundaries (first, last, off by one), duplicates, order
   - invalid input and each error path that the change added
   - permissions and roles; the data of a different user or tenant
   - concurrency, retries, a second run
   - time: timezones, daylight saving, expiry
   - old data, old clients, old config
3. **Regression.** Find the callers of each changed function, type,
   endpoint, or schema. Run their tests. If a caller has no test and the
   change can affect it, add a test or report it.
4. **All checks.** Run all the checks. Compare with the baseline. Record flaky tests as flaky.
5. **Coverage.** If the project has a coverage tool, report the coverage of
   the changed lines. Each changed line with no cover gets a test or a reason.
6. **Real run.** Run the software and use the change on the environment in the state file:
   - bug: do the original reproduction steps and show that the problem is gone
   - feature: go through each acceptance criterion
   - performance: do the baseline measurement again, the same number of times

   If you cannot run it, write the exact steps for the user. Mark the item
   `unverified` until the user reports the result.
7. **For some types.**
   - upgrade: check the deprecation warnings and each breaking change
   - schema or data change: test the migration forward, and backward if one exists
   - public API change: check each known consumer
8. A failure is a defect: start the fix loop (see Loops in `work-flow`). If
   the defect shows that the approved solution is wrong, go to the rework loop.
9. Write to the state file under "Test results": what you ran, where, the
   results, the edge-case list with decisions, and each `unverified` item.

Do not make a test weaker to make it pass. Always ask before you change
what an existing test expects.

## End of step

Show this table. Ask: "Here are the test results. Commit the added tests and continue?"

| Check | Result | Where |
| ----- | ------ | ----- |
| Proof for the task type | | |
| Edge cases (tested / not applicable / open) | | |
| Regression in callers | | |
| All checks against the baseline | | |
| Coverage of changed lines | | |
| Real run | | |

Switch: `test`. On auto, pass only if:

- the checks pass against the baseline, with no new flaky test
- the proof exists, passes, and fails without the change
- each edge case has a test or a reason
- no existing test was made weaker, skipped, or given a different expectation
- you did the real run; an `unverified` item makes this step ask

Commit message: the convention of the repository, or `test: cover <area> (<ref>)`.

## After later phases

`work-clean` and `work-prune` change the code after this step. Each one
does items 1, 3, and 4 again before its commit. `work-review` does item 6
again if one of them changed something.

## Next

`work-clean`
