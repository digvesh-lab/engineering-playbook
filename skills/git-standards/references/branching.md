# Branch model

Part of `git-standards`. Read this when the user asks which branch
model to use, or asks to retire a long-lived branch.

## Default: GitHub Flow

One long-lived branch, the default branch. It is always deployable. Each
other branch is short-lived.

```
main (always deployable)
 ├─ feat/<slug> ─┐
 ├─ fix/<slug>  ─┼─ PR + CI ─▶ merge to main ─▶ deploy
 └─ chore/<slug>─┘
```

1. Create the branch from the default branch.
2. Keep it for 1 or 2 days. If it grows past that, split the change.
3. Open a PR to the default branch. CI must pass before the merge.
4. Merge, deploy from the default branch, and delete the branch.

## When a different model fits

| Model | Use it when | The cost |
| ----- | ----------- | -------- |
| GitHub Flow | a small team that delivers continuously | none of note; the default |
| GitFlow (`develop`, `release/*`, `hotfix/*`) | releases are scheduled and versioned | more process; long-lived branches collect merge risk |
| Trunk-based (commits to the default branch, feature flags) | many deploys each day, with strong automated tests | needs the tests and the flags first |

If you are not sure, use GitHub Flow. Do not move to trunk-based before
the release frequency and the tests justify it.

## A long-lived integration branch that exists

If the repository's convention keeps `dev`, `develop`, or `staging`, follow
the convention. If the branch is only a habit, tell the user the risk: it
becomes the real branch, the default branch goes stale, and nobody can tell
what is deployed from the branches.

To retire it, only when the user asks:

1. Stop creating branches from it. Create them from the default branch.
2. Bring the default branch up to it in one reconciliation PR.
3. Confirm that the default branch is what is deployed. Then delete the branch.

## Data migrations

A branch that needs a manual data migration says so in the Test plan of
its PR, with the environments where the migration was already run.
