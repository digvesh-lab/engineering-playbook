# Task types

Part of the `work-flow` contract. The rules in `SKILL.md` have priority.

| Type | Evidence that the work is necessary | Proof that the work is done | Prefix |
| ---- | ----------------------------------- | --------------------------- | ------ |
| bug | reproduced; cause at `file:line` | a test that failed before the fix and passes after | `fix` |
| feature | it does not exist; the user gave acceptance criteria | a test for each acceptance criterion | `feat` |
| refactor | a concrete problem; tests cover the behaviour (if not, add them first) | those tests pass with no change | `refactor` |
| performance | a baseline from 3 runs or more | the same measurement, better by more than the variation between runs | `perf` |
| upgrade | the current and target versions; the breaking changes | the checks pass on the new version | `chore` |
| tests | the gap in coverage | new tests pass, and fail when you break the code | `test` |
| docs | what is missing or wrong | the docs agree with the code | `docs` |

If no type fits, use the nearest. Say which and why.

The prefix is the `type` in a branch name, a commit subject, a PR title, and
an issue title. The form of each is in Git standards in `SKILL.md`.
