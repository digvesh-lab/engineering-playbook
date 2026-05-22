# Agent Workflow (Wiki-First)

## Execution Order

1. Load `docs/project/index.md`.
2. Load only linked sections for the target task scope.
3. Verify repo-specific facts from source files, config, tests, and existing docs.
4. Implement the requested change.
5. Update affected wiki pages in the same branch.
6. Run `node validate-wiki-graph.js /abs/path/to/repo` when wiki pages change.
7. Run `node generate-wiki-graph.js /abs/path/to/repo` when graph output should be refreshed.
8. Run relevant checks and record evidence in the task, PR, or work log.

## Why

- Lower token usage vs full-repo reads.
- Better consistency for project-specific constraints.
- Faster onboarding for new tasks.
- Safer production changes because ownership, contracts, rollout, and rollback are explicit.

## Blocking Rule

If required docs are missing or stale enough to make the implementation risky:

- Mark the task `Blocked` or `Needs Clarification` where the task tracker supports it.
- Add a concrete note naming the missing decision, owner, or evidence.
- Stop before risky implementation.

If missing docs are not risky for the current change, update the wiki and continue.
