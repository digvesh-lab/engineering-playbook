# Agent Workflow (Wiki-First)

## Execution Order

1. Load `docs/project/index.md`.
2. Load only linked sections for the target task scope.
3. Load changed files and immediate dependencies.
4. Implement.
5. Update affected wiki pages in same change.

## Why

- Lower token usage vs full-repo reads.
- Better consistency for project-specific constraints.
- Faster onboarding for new tasks.

## Blocking Rule

If required docs are missing/stale:

- Mark task `Blocked` or `Needs Clarification`.
- Add note in task comments.
- Stop before risky implementation.
