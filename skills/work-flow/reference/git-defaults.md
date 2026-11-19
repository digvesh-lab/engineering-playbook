# Git defaults: detail

Part of the `work-flow` contract. The rules in `SKILL.md` have priority.

Use these only if the repository has no convention and the `git-standards`
skill is not installed (see Git standards in `SKILL.md`). They are a short
form of that skill. If the two differ, `git-standards` is correct.

- **Grammar.** `<type>(<scope>): <description>` for the issue title, the
  commit subject, and the PR title. `type` is the prefix for the task type
  (`task-types.md`). `scope` is the module. The description is imperative,
  lower case, with no full stop, 70 characters maximum for the line.
- **Branch.** `<type>/<slug>` from the base branch. The slug is lower case
  with hyphens and names the change.
- **Commit.** One logical change. The body says why, and the cause for a
  bug. It does not repeat the diff. Add no trailer that the repository or
  the user did not ask for.
- **Pull request.** Sections: Summary, Test plan, Tradeoffs. If the run has
  an issue: `Fixes #<n>` when the PR base is the default branch, else
  `Refs #<n>`.
- **Issue.** The form in `tickets.md`.

## What goes into each section of a pull request

The form can come from the repository or from `git-standards`. The content
always comes from the state file:

| Section | Content from the run |
| ------- | -------------------- |
| Summary | the task and its reference, the findings (the cause, for a bug), the approved solution |
| Test plan | the test results table, with where each item was verified; each `unverified` item |
| Tradeoffs | how to undo the change, the scores before and after, the open items, each disagreement |

If the form has no section for a row, add the row's content under the
nearest section. Do not drop it.
