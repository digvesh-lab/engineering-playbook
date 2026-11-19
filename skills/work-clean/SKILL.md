---
name: work-clean
description: Step 8 of work-flow, phase 2 of the work. Makes the new code clean and simple with no change to its behaviour. Use through work-flow after the test step, or directly to simplify the changes on the current branch.
---

# Step 8 (phase 2): make it clean and simple

Obeys the contract in `work-flow`. Work only on the work branch and only on
code that this run changed.

## Do

1. Do not change behaviour. The tests from `work-test` must pass before and
   after. Do not change them.
2. Simplify the logic. Use better names. Remove nesting.
3. Use an existing helper where a new one does the same thing.
4. Follow the style of the code around it and the conventions in memory.
5. Work in small steps. Run the tests for the changed files after each step.
6. Before the commit, do items 1 and 3 of `work-test` again: the proof, and
   the tests of the callers. Run the full lint and type-check. A failure starts the fix loop. The first
   attempt is to undo the last change. All the checks run after
   `work-prune` (see `reference/checks.md` in `work-flow`).
7. Record in the state file what you simplified.

If nothing needs a change, say so and make no commit. That is a pass.

## End of step

Show a short diff summary. Ask: "Phase 2 is done. Commit it?"

Switch: `clean`. On auto, pass only if:

- the proof, the tests of the callers, the lint, and the type-check pass
- no test file changed in this phase
- only files in the scope changed
- no public name, signature, or output changed

Commit message: the convention of the repository, or `refactor: simplify <area> (<ref>)`.

## Next

`work-prune`
