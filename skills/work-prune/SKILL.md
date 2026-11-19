---
name: work-prune
description: Step 9 of work-flow, phase 3 of the work. Removes redundant and dead code, debug output, and unnecessary comments that the change left. Use through work-flow after the clean phase, or directly to tidy the changes on the current branch.
---

# Step 9 (phase 3): remove what is not necessary

Obeys the contract in `work-flow`. Work only on the work branch.

## Do

1. Delete what this work made dead: unused functions, imports, variables,
   redundant branches, replaced code paths, and tests for code that is gone.
2. Remove debug output, commented-out code, temporary files, and TODOs from this work.
3. Keep comments that say why. Remove comments that say what the code does.
4. Before you delete something, search the full repository for references.
   Include dynamic references: strings, reflection, config, exports,
   templates, other packages.
5. Before the commit, do items 1 and 3 of `work-test` again: the proof, and
   the tests of the callers. Run the full lint and type-check. A failure starts the fix loop. The first
   attempt is to put back the last deletion.
6. After the commit, if clean or prune changed a file, run all the checks
   one time (check 4 in `reference/checks.md` of `work-flow`). A failure
   starts the fix loop in the phase that made it.
7. Record in the state file each thing that you removed and the evidence
   that nothing used it.

Dead code that existed before this work is out of scope. List it under
"Open items".

If there is nothing to remove, say so and make no commit. That is a pass.

## End of step

Show a short diff summary. Ask: "Phase 3 is done. Commit it?"

Switch: `prune`. On auto, pass only if:

- all the checks pass against the baseline (item 6)
- each deleted thing has 0 references in the repository
- nothing that you deleted is exported or part of a public API (always ask
  before you remove a public symbol)
- only files in the scope changed

Commit message: the convention of the repository, or `chore: remove dead code (<ref>)`.

## Next

`work-review`
