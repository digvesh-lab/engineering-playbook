#!/usr/bin/env bash
set -euo pipefail

TARGET_REPO="${1:-}"
if [[ -z "$TARGET_REPO" ]]; then
  echo "usage: $0 /abs/path/to/repo" >&2
  exit 2
fi

if [[ ! -d "$TARGET_REPO/.git" ]]; then
  echo "error: target is not a git repo: $TARGET_REPO" >&2
  exit 2
fi

TARGET_REPO="$(cd "$TARGET_REPO" && pwd)"
REPO_NAME="$(basename "$TARGET_REPO")"
TODAY="$(date +%F)"
DOCS_ROOT="$TARGET_REPO/docs/project"

mkdir -p \
  "$DOCS_ROOT/metadata" \
  "$DOCS_ROOT/architecture" \
  "$DOCS_ROOT/adr" \
  "$DOCS_ROOT/features/FEAT-template" \
  "$DOCS_ROOT/apis/endpoints" \
  "$DOCS_ROOT/apis/events" \
  "$DOCS_ROOT/data" \
  "$DOCS_ROOT/conventions" \
  "$DOCS_ROOT/graph" \
  "$DOCS_ROOT/runbooks" \
  "$DOCS_ROOT/incidents/YYYY" \
  "$DOCS_ROOT/changelog" \
  "$DOCS_ROOT/logs" \
  "$DOCS_ROOT/generated"

write_if_missing() {
  local path="$1"
  local content="$2"
  if [[ ! -f "$path" ]]; then
    printf "%s\n" "$content" > "$path"
  fi
}

frontmatter() {
  local id="$1"
  local type="$2"
  local status="${3:-draft}"
  cat <<FM
---
id: $id
type: $type
project: $REPO_NAME
owner: unknown
status: $status
relations: []
updated: $TODAY
---
FM
}

frontmatter_with_relations() {
  local id="$1"
  local type="$2"
  local status="$3"
  local relations="$4"
  cat <<FM
---
id: $id
type: $type
project: $REPO_NAME
owner: unknown
status: $status
relations:
$relations
updated: $TODAY
---
FM
}

write_if_missing "$DOCS_ROOT/README.md" "$(frontmatter_with_relations "PROJ-readme" "convention" "active" "  - type: documents
    target: PROJ-$REPO_NAME")
# Project Wiki

Repo-specific engineering and operations documentation generated from the shared engineering playbook.

## Principles

- Keep pages factual and current with implementation changes.
- Use placeholders only where a repo-specific owner must make a decision.
- Do not encode language, framework, hosting, or branch-model assumptions in shared templates.
- Keep generated artifacts under \`docs/project/generated/\`.

## Start

- Read \`index.md\` for the navigation map.
- Update affected pages in the same change as code or process changes.
"

write_if_missing "$DOCS_ROOT/index.md" "$(frontmatter_with_relations "PROJ-$REPO_NAME" "convention" "active" "  - type: contains
    target: META-glossary
  - type: contains
    target: META-ownership
  - type: contains
    target: META-lifecycle
  - type: contains
    target: ARCH-context
  - type: contains
    target: ARCH-containers
  - type: contains
    target: ARCH-components
  - type: contains
    target: ARCH-data-flows
  - type: contains
    target: ARCH-dependencies
  - type: contains
    target: ADR-index
  - type: contains
    target: FEAT-index
  - type: contains
    target: API-index
  - type: contains
    target: DATA-schema
  - type: contains
    target: CONV-review-checklist
  - type: contains
    target: GRAPH-contract
  - type: contains
    target: RUN-deploy
  - type: contains
    target: RUN-rollback
  - type: documents
    target: PROJ-readme")
# $REPO_NAME Wiki Index

## Project Metadata

- [Glossary](metadata/glossary.md)
- [Ownership](metadata/ownership.md)
- [Lifecycle](metadata/lifecycle.md)

## Architecture

- [Context](architecture/context.md)
- [Containers](architecture/containers.md)
- [Components](architecture/components.md)
- [Data Flows](architecture/data-flows.md)
- [Dependencies](architecture/dependencies.md)

## Delivery

- [Features](features/README.md)
- [ADRs](adr/README.md)
- [APIs and Interfaces](apis/index.md)
- [Data](data/schema.md)
- [Conventions](conventions/review-checklist.md)
- [Graph Contract](graph/contract.md)

## Operations

- [Deploy](runbooks/deploy.md)
- [Rollback](runbooks/rollback.md)
- [Incidents](incidents/)
- [Changelog](changelog/)
- [Work Logs](logs/)
"

write_if_missing "$DOCS_ROOT/metadata/glossary.md" "$(frontmatter "META-glossary" "convention")
# Glossary

Define repo-specific terms, acronyms, business concepts, and technical labels.

| Term | Meaning | Source |
| --- | --- | --- |
| TBD | Define before relying on this term in implementation docs. | TBD |
"

write_if_missing "$DOCS_ROOT/metadata/ownership.md" "$(frontmatter "META-ownership" "convention")
# Ownership

Document accountable humans, teams, systems, and escalation paths.

## Repository Owner

- Owner: TBD
- Backup: TBD
- Reviewers: TBD

## Operational Contacts

| Area | Primary | Backup | Escalation |
| --- | --- | --- | --- |
| Code | TBD | TBD | TBD |
| Runtime | TBD | TBD | TBD |
| Data | TBD | TBD | TBD |
| Security | TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/metadata/lifecycle.md" "$(frontmatter "META-lifecycle" "convention")
# Lifecycle

State the repo lifecycle without assuming a release model.

## Current Stage

- Stage: TBD
- Supported environments: TBD
- Release cadence: TBD
- Deprecation policy: TBD

## Readiness Criteria

- Build and validation checks are documented.
- Ownership and escalation are documented.
- Deploy and rollback procedures are documented where applicable.
- External contracts and data responsibilities are documented where applicable.
"

write_if_missing "$DOCS_ROOT/architecture/context.md" "$(frontmatter "ARCH-context" "component")
# Architecture Context

Explain what this repo is responsible for and what it explicitly does not own.

## Responsibilities

- TBD

## Non-Responsibilities

- TBD

## External Actors

| Actor/System | Relationship | Contract Location |
| --- | --- | --- |
| TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/architecture/containers.md" "$(frontmatter "ARCH-containers" "component")
# Containers

Describe deployable or independently operated units. For libraries or docs-only repos, list published packages or consumed entry points instead.

| Unit | Purpose | Runtime/Host | Owner |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/architecture/components.md" "$(frontmatter "ARCH-components" "component")
# Components

Document major internal modules, boundaries, and invariants.

| Component | Responsibility | Depends On | Notes |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/architecture/data-flows.md" "$(frontmatter "ARCH-data-flows" "component")
# Data Flows

Document movement of data, control messages, files, or human workflow state.

| Flow | Source | Destination | Trigger | Failure Handling |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/architecture/dependencies.md" "$(frontmatter "ARCH-dependencies" "component")
# Dependencies

List external services, packages, platforms, credentials, and operational assumptions.

| Dependency | Type | Required For | Failure Mode | Owner |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/adr/README.md" "$(frontmatter_with_relations "ADR-index" "adr" "active" "  - type: contains
    target: ADR-0001")
# ADR Index

Architecture Decision Records capture durable technical decisions.

## Naming

Use \`NNNN-short-title.md\` with a monotonically increasing number.

## Records

- [0001 Wiki-First Documentation](0001-wiki-first-documentation.md)
"

write_if_missing "$DOCS_ROOT/adr/0001-wiki-first-documentation.md" "$(frontmatter_with_relations "ADR-0001" "adr" "active" "  - type: documents
    target: PROJ-$REPO_NAME
  - type: documents
    target: GRAPH-contract")
# ADR 0001: Wiki-First Documentation

## Status

Accepted

## Context

Agents and humans need a small, repo-local source of truth before making implementation changes.

## Decision

Maintain \`docs/project/\` as the canonical project wiki. Every implementation or process change updates the affected wiki page in the same branch.

## Consequences

- Project context can be loaded selectively instead of reading the full repository.
- Stale or missing documentation is treated as a delivery risk.
- Generated or volatile outputs stay under \`docs/project/generated/\`.
"

write_if_missing "$DOCS_ROOT/features/README.md" "$(frontmatter_with_relations "FEAT-index" "feature" "active" "  - type: contains
    target: FEAT-template")
# Features

One folder per feature or capability. Use IDs from the team's task tracker when available, otherwise use a stable short slug.

## Template

Copy \`FEAT-template/\` and replace placeholders.

## Feature List

| Feature | Status | Owner | Notes |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/features/FEAT-template/overview.md" "$(frontmatter_with_relations "FEAT-template" "feature" "draft" "  - type: contains
    target: FEAT-template-design
  - type: exposes
    target: FEAT-template-api
  - type: uses_data
    target: FEAT-template-data
  - type: verified_by
    target: FEAT-template-testing
  - type: rolled_out_by
    target: FEAT-template-rollout
  - type: operated_by
    target: FEAT-template-runbook")
# Feature Overview

## Problem

TBD

## Users / Actors

TBD

## Scope

### In Scope

- TBD

### Out of Scope

- TBD

## Success Criteria

- TBD
"

write_if_missing "$DOCS_ROOT/features/FEAT-template/design.md" "$(frontmatter_with_relations "FEAT-template-design" "feature" "draft" "  - type: part_of
    target: FEAT-template")
# Feature Design

## Approach

TBD

## Alternatives Considered

| Option | Decision | Reason |
| --- | --- | --- |
| TBD | TBD | TBD |

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/features/FEAT-template/api.md" "$(frontmatter_with_relations "FEAT-template-api" "api" "draft" "  - type: part_of
    target: FEAT-template
  - type: conforms_to
    target: API-index")
# Feature Interfaces

Document any public API, CLI, event, file, UI, job, or operational interface affected by this feature.

| Interface | Type | Contract | Compatibility Notes |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/features/FEAT-template/data-model.md" "$(frontmatter_with_relations "FEAT-template-data" "component" "draft" "  - type: part_of
    target: FEAT-template
  - type: conforms_to
    target: DATA-schema")
# Feature Data Model

## Data Owned

TBD

## Data Read

TBD

## Migration / Backfill

TBD

## Retention / Privacy

TBD
"

write_if_missing "$DOCS_ROOT/features/FEAT-template/testing.md" "$(frontmatter_with_relations "FEAT-template-testing" "convention" "draft" "  - type: part_of
    target: FEAT-template
  - type: conforms_to
    target: CONV-review-checklist")
# Feature Testing

## Required Checks

| Check | Command / Method | Required Result |
| --- | --- | --- |
| TBD | TBD | TBD |

## Manual Review

TBD
"

write_if_missing "$DOCS_ROOT/features/FEAT-template/rollout.md" "$(frontmatter_with_relations "FEAT-template-rollout" "runbook" "draft" "  - type: part_of
    target: FEAT-template
  - type: depends_on
    target: RUN-deploy
  - type: depends_on
    target: RUN-rollback")
# Feature Rollout

## Release Plan

TBD

## Compatibility

TBD

## Monitoring

TBD

## Rollback Trigger

TBD
"

write_if_missing "$DOCS_ROOT/features/FEAT-template/runbook.md" "$(frontmatter_with_relations "FEAT-template-runbook" "runbook" "draft" "  - type: part_of
    target: FEAT-template")
# Feature Runbook

## Normal Operation

TBD

## Failure Modes

| Symptom | Likely Cause | Action |
| --- | --- | --- |
| TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/apis/index.md" "$(frontmatter_with_relations "API-index" "api" "active" "  - type: contains
    target: API-template
  - type: contains
    target: EVENT-template")
# APIs and Interfaces

Use this section for any externally consumed interface: HTTP, GraphQL, RPC, events, CLI, files, packages, scheduled jobs, dashboards, or manual workflow contracts.

## Endpoint / Command / File Interfaces

- See \`endpoints/\`.

## Event Interfaces

- See \`events/\`.

## Compatibility Policy

- Breaking-change definition: TBD
- Versioning strategy: TBD
- Deprecation notice period: TBD
"

write_if_missing "$DOCS_ROOT/apis/endpoints/template.md" "$(frontmatter_with_relations "API-template" "api" "draft" "  - type: part_of
    target: API-index")
# Interface Template

## Summary

TBD

## Consumers

TBD

## Contract

TBD

## Errors / Failure Modes

TBD

## Compatibility Notes

TBD
"

write_if_missing "$DOCS_ROOT/apis/events/template.md" "$(frontmatter_with_relations "EVENT-template" "api" "draft" "  - type: part_of
    target: API-index")
# Event Template

## Producer

TBD

## Consumers

TBD

## Payload

TBD

## Delivery Semantics

TBD

## Replay / Recovery

TBD
"

write_if_missing "$DOCS_ROOT/data/schema.md" "$(frontmatter_with_relations "DATA-schema" "component" "draft" "  - type: contains
    target: DATA-migrations
  - type: contains
    target: DATA-contracts")
# Data Schema

Document durable data structures, storage locations, files, indexes, or external records.

| Entity | Location | Owner | Notes |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/data/migrations.md" "$(frontmatter_with_relations "DATA-migrations" "runbook" "draft" "  - type: part_of
    target: DATA-schema
  - type: depends_on
    target: RUN-rollback")
# Migrations

Document schema, contract, data, file, or state transitions.

| Migration | Trigger | Rollback | Verification |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/data/contracts.md" "$(frontmatter_with_relations "DATA-contracts" "api" "draft" "  - type: part_of
    target: DATA-schema
  - type: conforms_to
    target: API-index")
# Data Contracts

Document inbound and outbound data guarantees.

| Contract | Producer | Consumer | Compatibility Rule |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/conventions/branching.md" "$(frontmatter "CONV-branching" "convention")
# Branching Strategy

This page must be filled per repo. Do not inherit branch assumptions from the shared playbook.

## Branch Roles

- Default branch: TBD
- Integration branches: TBD
- Release branches: TBD
- Protected branches: TBD

## Branch Naming

- Feature: TBD
- Fix: TBD
- Documentation: TBD
- Hotfix: TBD

## Merge Policy

- PR requirement: TBD
- Merge method: TBD
- Required checks: TBD
- Review requirements: TBD
"

write_if_missing "$DOCS_ROOT/conventions/coding.md" "$(frontmatter "CONV-coding" "convention")
# Coding Conventions

Document repo-local conventions only after verifying the actual codebase.

## Source Layout

TBD

## Naming

TBD

## Error Handling

TBD

## Observability

TBD

## Security

TBD
"

write_if_missing "$DOCS_ROOT/conventions/constraints.md" "$(frontmatter "CONV-constraints" "constraint")
# Constraints

Record non-negotiable technical, product, compliance, operational, or compatibility constraints.

| Constraint | Reason | Source | Review Date |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/conventions/review-checklist.md" "$(frontmatter "CONV-review-checklist" "convention" "active")
# Review Checklist

Use this checklist for any change before marking work ready for review.

- Wiki pages affected by the change are updated.
- Public interfaces and data contracts are documented if changed.
- Tests or verification evidence match the risk of the change.
- Rollout and rollback notes exist for operational changes.
- Secrets, credentials, and local-only artifacts are not committed.
- Backward compatibility impact is explicit.
"

write_if_missing "$DOCS_ROOT/graph/contract.md" "$(frontmatter_with_relations "GRAPH-contract" "convention" "active" "  - type: documents
    target: PROJ-$REPO_NAME")
# Graph Contract

This wiki is graph-ready when every Markdown page under \`docs/project/\` has valid frontmatter and all relationships are expressed through \`relations\`.

## Required Frontmatter

\`\`\`yaml
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
\`\`\`

Use \`relations: []\` only when a page is intentionally standalone.

## Allowed Node Types

- feature
- adr
- runbook
- component
- api
- constraint
- incident
- log
- convention

## Allowed Status Values

- draft
- active
- deprecated
- archived

## Allowed Relation Types

- contains
- part_of
- depends_on
- documents
- implements
- exposes
- consumes
- produces
- uses_data
- owns
- owned_by
- operated_by
- verified_by
- rolled_out_by
- replaces
- supersedes
- conforms_to
- mitigates
- related_to

## Validation Rules

- Every Markdown file below \`docs/project/\`, except files below \`docs/project/generated/\`, must have frontmatter.
- Every page must have a unique \`id\`.
- Every \`type\`, \`status\`, and relation \`type\` must be allowed by this contract.
- Every relation target must resolve to another page ID in the wiki.
- Generated files must be written to \`docs/project/generated/\`.

## Graph Output

\`generate-wiki-graph.js\` emits:

- \`docs/project/generated/graph.json\`
- \`docs/project/generated/graph.html\`

The JSON shape is:

\`\`\`json
{
  \"nodes\": [
    {
      \"id\": \"ARCH-context\",
      \"type\": \"component\",
      \"path\": \"docs/project/architecture/context.md\",
      \"title\": \"Architecture Context\",
      \"status\": \"draft\"
    }
  ],
  \"edges\": [
    {
      \"source\": \"PROJ-example\",
      \"target\": \"ARCH-context\",
      \"type\": \"contains\"
    }
  ]
}
\`\`\`
"

write_if_missing "$DOCS_ROOT/runbooks/deploy.md" "$(frontmatter "RUN-deploy" "runbook")
# Deploy Runbook

Document the deployment path for this repo. If the repo is not deployed, state how it is published, consumed, or released.

## Prerequisites

TBD

## Procedure

1. TBD

## Verification

TBD

## Owners

TBD
"

write_if_missing "$DOCS_ROOT/runbooks/rollback.md" "$(frontmatter "RUN-rollback" "runbook")
# Rollback Runbook

Document how to reverse a bad release, contract change, migration, publication, or operational update.

## Triggers

TBD

## Procedure

1. TBD

## Verification

TBD

## Communication

TBD
"

write_if_missing "$DOCS_ROOT/runbooks/incident-template.md" "$(frontmatter "RUN-incident-template" "runbook")
# Incident Runbook Template

## Symptoms

TBD

## Triage

TBD

## Mitigation

TBD

## Escalation

TBD

## Follow-Up

TBD
"

write_if_missing "$DOCS_ROOT/runbooks/auth-gh-switch.md" "$(frontmatter "RUN-auth-gh-switch" "runbook")
# GitHub Account Switch Runbook

Use only when the repo workflow requires a specific GitHub identity.

## Procedure

1. Confirm the expected GitHub username from the task or project metadata.
2. Run \`gh auth switch -u <username>\`.
3. Run \`gh auth status\` and verify the active account.
4. Set repo-local git identity if required by project policy.

## Notes

Do not change global git identity for a repo-specific task unless explicitly required.
"

write_if_missing "$DOCS_ROOT/incidents/YYYY/YYYY-MM-DD-incident-template.md" "$(frontmatter "INC-template" "incident")
# Incident Template

## Summary

TBD

## Timeline

| Time | Event |
| --- | --- |
| TBD | TBD |

## Impact

TBD

## Root Cause

TBD

## Actions

| Action | Owner | Status |
| --- | --- | --- |
| TBD | TBD | TBD |
"

write_if_missing "$DOCS_ROOT/changelog/YYYY-MM.md" "$(frontmatter "CHANGELOG-template" "log")
# Changelog YYYY-MM

## Added

- TBD

## Changed

- TBD

## Fixed

- TBD

## Removed

- TBD
"

write_if_missing "$DOCS_ROOT/logs/YYYY-MM.md" "$(frontmatter "LOG-template" "log")
# Work Log YYYY-MM

Use for concise implementation notes, verification evidence, and decisions that do not need a full ADR.

| Date | Change | Evidence | Follow-Up |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |
"

if [[ -f "$TARGET_REPO/.gitignore" ]]; then
  if ! grep -q '^docs/project/generated/$' "$TARGET_REPO/.gitignore"; then
    printf "\n%s\n" "docs/project/generated/" >> "$TARGET_REPO/.gitignore"
  fi
else
  printf "%s\n" "docs/project/generated/" > "$TARGET_REPO/.gitignore"
fi

echo "bootstrapped wiki at $DOCS_ROOT"
