# Agnostic Repo Wiki Playbook

This repo provides a reusable, production-readiness wiki structure for any software repository. It is intentionally neutral: it does not assume a programming language, framework, runtime, hosting model, API style, delivery process, or branch model.

## Design Rules

- Keep shared templates generic; record repo-specific facts only in the target repo.
- Use placeholders where an owner must make a local decision.
- Treat APIs broadly: HTTP, events, CLI commands, files, packages, jobs, dashboards, and manual workflow contracts all count.
- Treat operations broadly: deploy, publish, rollback, migration, incident response, and support procedures all count.
- Express graph edges through typed frontmatter `relations`; do not rely on prose links for graph generation.
- Keep generated or volatile outputs under `docs/project/generated/`.

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
    0001-wiki-first-documentation.md

  features/
    README.md
    FEAT-template/
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
      template.md
    events/
      template.md

  data/
    schema.md
    migrations.md
    contracts.md

  conventions/
    branching.md
    coding.md
    constraints.md
    review-checklist.md

  graph/
    contract.md

  runbooks/
    deploy.md
    rollback.md
    incident-template.md
    auth-gh-switch.md

  incidents/
    YYYY/
      YYYY-MM-DD-incident-template.md

  changelog/
    YYYY-MM.md

  logs/
    YYYY-MM.md

  generated/
    graph.json
    graph.html
```

## Bootstrap Command

```bash
./bootstrap-wiki.sh /abs/path/to/target-repo
node validate-wiki-graph.js /abs/path/to/target-repo
node generate-wiki-graph.js /abs/path/to/target-repo
```

The bootstrap script writes missing files only. It does not overwrite existing wiki pages, so teams can safely re-run it after the playbook expands.

## Graph Contract

Every Markdown page under `docs/project/`, except files under `docs/project/generated/`, must include frontmatter with a stable `id`, valid `type`, valid `status`, and `relations`.

Use typed relations for machine-readable edges:

```yaml
relations:
  - type: depends_on
    target: RUN-rollback
  - type: exposes
    target: API-session-create
```

Use `relations: []` only for pages that are intentionally standalone.

## Git Ignore

Target repos should ignore generated wiki artifacts:

```gitignore
docs/project/generated/
```

The bootstrap script adds this entry when missing.
