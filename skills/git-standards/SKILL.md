---
name: git-standards
description: Default conventions for git branches, commit messages, pull requests, and issues, with one grammar for all four. Use before you create a branch, write a commit, open a pull request, or file an issue, and when the user asks to standardize one of these in a repository.
---

# Git standards

Defaults for a repository that has no convention of its own.

This skill works alone. `work-flow` also uses it, when it is installed, for
the form of each branch, commit, pull request, and issue in a run.

## Which rules apply

1. Look for the repository's own convention: `CONTRIBUTING.md`, a PR or
   issue template in `.github/`, a commit-lint config, the instruction file
   (`AGENTS.md` or `CLAUDE.md`), and the last 20 commit subjects.
2. If the repository has one, follow it. Do not propose a change to it
   unless the user asks.
3. If it has none, or covers only part, use this skill for the rest.

## One grammar

An issue title, a branch, a commit subject, and a PR title for the same
change use the same words:

```
<type>(<scope>): <description>
```

- `type`: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `ci`, `style`.
- `scope`: the module or feature, with the name that the repository uses
  for it. Leave it out only if the change has no single module.
- `description`: imperative mood, lower case, no full stop, 70 characters
  maximum for the full line. Write "reject expired tokens", not "rejected"
  or "rejects".

## Branch

- Start from the default branch. Name it `<type>/<slug>`:
  `fix/token-expiry-comparison`, not `fix/bug`.
- `<slug>`: lower case, hyphens, specific to the change.
- One branch for one change and one PR. Do not use an old branch again for
  different work.
- Do not create a branch from a long-lived integration branch (`dev`,
  `develop`, `staging`) unless the repository's convention says so.
- A hotfix is a `fix/<slug>` branch. It has no special type.

The choice of branch model, and how to retire an integration branch:
`references/branching.md`. Read it only when the user asks about the model.

## Commit

```
<type>(<scope>): <description>

<body: why the change is necessary, and the cause for a bug>

<footer: BREAKING CHANGE: ..., or Fixes #<n>>
```

- One logical change in one commit. If the body needs "also", make 2 commits.
- The body gives the reason and the user-facing effect. It does not repeat the diff.
- The body is optional for a change that the subject explains fully.
- Stage files by path. Do not commit build output, caches, or scratch files.
- For a bug that existed for a long time, name the commit that introduced
  it, if you know it.
- Add no trailer that the repository or the user did not ask for.

## Pull request

- Title: the grammar above.
- Body: the template in `references/templates.md`. It has Summary, Test
  plan, and Tradeoffs.
- Summary: what changed and why, 1 bullet for each logical change. For a
  bug, give the symptom and the cause.
- Test plan: the exact steps or commands. Mark an item `[x]` only if you
  did it in this PR. Never write "tested locally".
- Name each thing that the diff does not show and the change needs: a data
  migration (and where it was run), a config or environment change, a
  deploy order.
- Put `Fixes #<n>` in the body so that the merge closes the issue. GitHub
  closes it only on a merge into the default branch. For a different base,
  write `Refs #<n>` and close the issue at the release.

## Issue

- Title: the grammar above.
- Body: the template in `references/templates.md`. It has Summary, Repro,
  Root cause, and Notes.
- One issue for one report. If the report has more than 1 cause, list each
  as a `- [ ]` item in the same issue. Make separate issues only if the
  fixes ship separately.
- Give a reproduction: a link, exact steps, or example input. For a data
  bug, give expected and actual, as a table if there is more than 1 example.
- Use labels that exist in the repository. Do not create a label.
- After the issue is filed, put each new finding in a comment. Edit the
  body only if the summary itself is wrong.
- Fill in "Root cause" when you know it.
- Close the issue through the PR, not by hand.
