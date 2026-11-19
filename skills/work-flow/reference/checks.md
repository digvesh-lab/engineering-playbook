# The checks: detail

Part of the `work-flow` contract. The rules in `SKILL.md` have priority.

- **Commands.** Use the `checks:` block in the instruction file. If there is none, use
  project memory. If there is none, find the commands (package scripts,
  Makefile, CI config), confirm them with the user one time, and save them
  to memory.
- **Baseline.** Run the checks on the new branch before any change. Record
  each failure as pre-existing. "The checks pass" means: no failure that is
  not in the baseline. Do not fix or hide a baseline failure. List it under
  "Open items".
- **Flaky tests.** If a test fails and then passes on a second run, record
  it as flaky. Run it 2 more times. A flaky test is not proof.
- **Order.** Run the tests for the changed files first.
- **When to run all the checks.** At these 4 points of a round:
  1. the baseline, before any change
  2. before the `work-build` commit
  3. in `work-test` (item 4)
  4. after `work-prune`, before `work-review`, if clean or prune changed a file

  Before their commits, `work-clean` and `work-prune` run the tests of the
  changed files and of their callers, and the full lint and type-check.
  Lint and type-check are cheap and find breaks outside the callers. If
  check 4 fails, start the fix loop in the phase that made the failure.
  The first attempt is to undo its last change. Each review round runs
  checks 2 to 4 again.
- **No weaker checks.** Do not delete, skip, or loosen a test. Do not edit a
  snapshot or a lint rule to agree with new output. The only exception is
  an approved solution that says so.
