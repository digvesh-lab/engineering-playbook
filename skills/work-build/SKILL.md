---
name: work-build
description: Step 6 of work-flow, phase 1 of the work. Creates a separate branch, records the check baseline, and writes the approved solution with its proof. Use through work-flow after a solution is approved, and again when a review sends work back.
---

# Step 6 (phase 1): write the code

Obeys the contract in `work-flow`. Needs a passed propose step and an
approved solution in the state file.

## Branch (first time only)

1. Look at the working tree. Apply the hard stop for changes that this run
   did not make (see Hard stops in `work-flow`). Never stash or discard
   them unless the user says so.
2. Run `git fetch`.
3. Name the branch with the form from Git standards in `work-flow`. The
   default is `<prefix>/<slug>`. The prefix is the one for the task type in
   `reference/task-types.md`: `feat`, not `feature`; `fix`, not `bug`.
   On manual (`build.branch`), ask: "Create branch `<prefix>/<slug>` from `<base>`?"
   On auto, create it and tell the user the name. If the name exists, add `-2`.
4. Run `git switch -c <prefix>/<slug> origin/<base>`. Record the branch.
   With `delivery: stacked`, a later piece branches from the branch of the
   piece before it (see `reference/tickets.md` in `work-flow`).
5. **Baseline**: run the checks before any change. Record the results
   (see The checks in `work-flow`).
6. For a bug: confirm that it still reproduces on this branch. If it does
   not, the base has the fix. That is a hard stop.

When a loop comes back to this step, go to "Do" on the existing branch.

## Do

1. Write the proof first, where the type permits it:
   - **bug**: write the failing test. Run it. Record the failure. Then write the fix.
   - **refactor**: if tests do not cover the behaviour, write them against
     the current code and see them pass. Then change the code.
   - **feature**: write a test for each acceptance criterion with the code.
2. Write the approved solution and nothing more. Apply the lessons from memory.
3. In a review loop: fix the blocking findings one at a time. Record which
   commit answers which finding.
4. Run the checks. A failure starts the fix loop (see Loops in `work-flow`).
5. Stay in the scope. A file outside it is a hard stop (see Scope in `work-flow`).
6. If the approved solution is wrong or not possible, stop. Report what you
   found. Go to the rework loop.
7. If the repository has a changelog or docs for this area, add the entry.
8. Record in the state file: the files changed, the proof, each attempt, the results.

## Borrowed method

If `borrowed/tdd.md` (in the `work-flow` skill folder) exists, read it and use its
method for the test-first loop. The contract has priority (see Borrowed
skills in `work-flow`). If it does not exist, use the method in this skill.

The borrowed method puts tests only at agreed seams. The seams are in the
test plan of the approved solution, so the approval is the agreement. Ask
again only if you need a new seam.

## End of step

Show a short diff summary. Ask: "Phase 1 is done. Commit it?"

Switch: `build.commit`. On auto, pass only if:

- the checks pass against the baseline
- only files in the scope changed
- the proof for the task type exists and passes; for a bug, you saw the test fail before the fix

Commit as the contract says. Message: the convention of the repository, or
`<type>: <what changed> (<ref>)`.

## Next

`work-test`
