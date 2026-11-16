# The checks: detail

Part of the `work-flow` contract. The rules in `SKILL.md` have priority.

- **Commands.** Use the `checks:` block in `CLAUDE.md`. If there is none, use
  project memory. If there is none, find the commands (package scripts,
  Makefile, CI config), confirm them with the user one time, and save them
  to memory.
- **Baseline.** Run the checks on the new branch before any change. Record
  each failure as pre-existing. "The checks pass" means: no failure that is
  not in the baseline. Do not fix or hide a baseline failure. List it under
  "Open items".
- **Flaky tests.** If a test fails and then passes on a second run, record
  it as flaky. Run it 2 more times. A flaky test is not proof.
- **Order.** Run the tests for the changed files first. Run all the checks
  before each commit.
- **No weaker checks.** Do not delete, skip, or loosen a test. Do not edit a
  snapshot or a lint rule to agree with new output. The only exception is
  an approved solution that says so.
