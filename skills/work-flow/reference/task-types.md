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
| question | the question, and the decision that the answer is for | an answer in which each claim has evidence (`file:line`, a command and its output, a measurement, or a link), and the unknowns | none |

A `question` is an investigation, an estimate, a review, or a comparison
that changes no code. The run ends after `work-assess` with the answer. It
makes no branch, no commit, and no pull request. `work-memory` records its
index line. If the user then asks for the change, start a new run with the
answer as its evidence.

If no type fits, use the nearest. Say which and why.

The prefix is the `type` in a branch name, a commit subject, a PR title, and
an issue title. The form of each is in Git standards in `SKILL.md`.
