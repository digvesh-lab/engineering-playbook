```yaml
---
id: <stable-id>
type: <allowed-type>
project: <target-repo-name>
owner: <team-or-person>
status: <allowed-status>
relations:
  - type: <allowed-relation-type>
    target: <target-id>
updated: YYYY-MM-DD
---
```

Use `relations: []` only when the page is intentionally standalone.

## Allowed `type`

- `feature`
- `adr`
- `runbook`
- `component`
- `api`
- `constraint`
- `incident`
- `log`
- `convention`

## Allowed `status`

- `draft`
- `active`
- `deprecated`
- `archived`

## ID Guidance

Use stable IDs that survive title changes:

- Project index: `PROJ-<repo-name>`
- Architecture: `ARCH-<scope>`
- Feature: `FEAT-<tracker-id-or-slug>`
- API or interface: `API-<domain-or-interface>`
- ADR: `ADR-0001`
- Runbook: `RUN-<procedure>`
- Incident: `INC-YYYY-MM-DD-<slug>`

## Allowed Relation Types

- `contains`
- `part_of`
- `depends_on`
- `documents`
- `implements`
- `exposes`
- `consumes`
- `produces`
- `uses_data`
- `owns`
- `owned_by`
- `operated_by`
- `verified_by`
- `rolled_out_by`
- `replaces`
- `supersedes`
- `conforms_to`
- `mitigates`
- `related_to`
