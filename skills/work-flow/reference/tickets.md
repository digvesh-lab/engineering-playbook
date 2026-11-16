# Tickets: detail

Part of the `work-flow` contract. The rules in `SKILL.md` have priority.

The `tickets` switch creates GitHub issues for the work with the `gh`
command. GitHub is the only tracker. `work-propose` does this after a
solution is approved. No other step publishes.

## What to create

| Situation | Create |
| --------- | ------ |
| The task came from an issue (`ref` in the state file) | nothing; use that issue |
| The task has no issue, and the solution is 1 piece | 1 issue |
| The task has no issue, and the solution is split | 1 parent issue, and 1 issue for each piece |
| The task came from an issue, and the solution is split | 1 issue for each piece, under that issue |

Create the issues in dependency order: an issue that blocks is created
before the issue that it blocks. Record each issue in the state file under
`issues:` immediately after `gh` returns its number.

## The form of an issue

Use the form from Git standards in `SKILL.md`: the repository's issue
template or written format, then the issue form of the `git-standards`
skill with the "Acceptance criteria" section below added, then this form.

- Title: `<type>(<scope>): <description>`, the same grammar as the commit
  prefix for the task type.
- Body:

```
## Summary
What must work, from the user's side. 1 to 3 sentences.

## Acceptance criteria
- [ ] <each criterion from "Requirements" that this issue covers>

## Blocked by
- #<n>, or "None"

## Notes
Out of scope, risks, and how to undo the change.
```

- A bug issue also has `## Repro` and `## Root cause`, from "Verdict and evidence".
- A parent issue lists its pieces as a checklist of issue numbers.
- Do not put a file path or a code snippet in an issue, unless it records a decision.
- Never put a secret, a credential, personal data, customer data, or raw
  logs in an issue. An issue cannot be deleted.

## Links

- Read `gh issue create --help` one time in a run. Newer versions have
  `--parent <n>` and `--blocked-by <n,n>`.
- Parent and child: use `--parent`. If the installed `gh` does not have it,
  write `Parent: #<n>` in the body of the child.
- Blocked by: use `--blocked-by`, and leave the "Blocked by" section out.
  If the installed `gh` does not have it, write the numbers in the section.
- Labels: add a label only if it exists in the repository
  (`gh label list`). If a label is missing, do not create it. Create the
  issue with no label and report it.

## Auto conditions

On `tickets:auto`, create the issues with no question only if:

- `gh auth status` succeeds
- the repository has issues switched on
  (`gh repo view --json hasIssuesEnabled`)
- the repository for the issue is the repository that the pull request will target
- the state file has no number under `issues:` for this piece
- `gh issue list --search "<title words>" --state open` shows no issue for the same work

If one is not met, and it is not a hard stop, ask.

## Hard stops

- `gh` is not installed, or is not logged in.
- Issues are switched off for the repository.
- The repository for the issue is not the repository that the pull request
  will target (a fork).
- An open issue is found for the same work, and the task did not name it.

A missing label is not a hard stop.

## A split and the scope

If the solution is split into pieces:

- This run builds only the first piece that nothing blocks. Its file list is the scope.
- The pull request closes only the issue of that piece.
- Tell the user the numbers of the open pieces. Each one is the task for a new run.

## Later in the run

- `work-ship`: the pull request body has `Fixes #<n>` for the issue of this
  run. It never closes a parent issue that has open pieces.
- Rework or resume: do not create an issue again. Edit the issue that the
  state file names (`gh issue edit`).
- Stop or abort: add 1 comment to each issue that the run created. Say that
  the work stopped and where the branch is. Do not close the issue.
