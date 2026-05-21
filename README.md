# Repo Wiki Structure (Review Copy)

This folder is a reviewable blueprint for per-repo documentation.

## Target Structure

```text
docs/project/
  README.md
  index.md

  metadata/
    glossary.md
    ownership.md
    lifecycle.md

  architecture/
    context.md
    containers.md
    components.md
    data-flows.md
    dependencies.md

  adr/
    README.md
    0001-*.md

  features/
    README.md
    FEAT-<id>/
      overview.md
      design.md
      api.md
      data-model.md
      testing.md
      rollout.md
      runbook.md

  apis/
    index.md
    endpoints/
      <domain>-<action>.md
    events/
      <event-name>.md

  data/
    schema.md
    migrations.md
    contracts.md

  conventions/
    branching.md
    coding.md
    constraints.md
    review-checklist.md

  runbooks/
    deploy.md
    rollback.md
    incident-<topic>.md
    auth-gh-switch.md

  incidents/
    YYYY/
      YYYY-MM-DD-<incident-id>.md

  changelog/
    YYYY-MM.md

  logs/
    YYYY-MM.md

  generated/
```

## Git Ignore

```gitignore
docs/project/generated/
```

## Bootstrap Command

```bash
./bootstrap-wiki.sh /abs/path/to/target-repo
```
