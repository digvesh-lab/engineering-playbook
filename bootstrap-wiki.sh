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
  "$DOCS_ROOT/runbooks" \
  "$DOCS_ROOT/incidents" \
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

write_if_missing "$DOCS_ROOT/README.md" "# Project Wiki

Repo-specific engineering and operations docs.
"

write_if_missing "$DOCS_ROOT/index.md" "---
id: PROJ-$(basename "$TARGET_REPO")
type: convention
project: $(basename "$TARGET_REPO")
owner: unknown
status: active
links:
  - ARCH-context
  - CONV-constraints
  - CONV-branching
updated: $(date +%F)
---

# $(basename "$TARGET_REPO") Wiki Index

## Start Here
- architecture/context.md
- conventions/constraints.md
- conventions/branching.md
- features/README.md
"

write_if_missing "$DOCS_ROOT/architecture/context.md" "---
id: ARCH-context
type: component
project: $(basename "$TARGET_REPO")
owner: unknown
status: draft
links: []
updated: $(date +%F)
---

# Architecture Context
"

write_if_missing "$DOCS_ROOT/conventions/constraints.md" "---
id: CONV-constraints
type: constraint
project: $(basename "$TARGET_REPO")
owner: unknown
status: draft
links: []
updated: $(date +%F)
---

# Constraints
"

write_if_missing "$DOCS_ROOT/conventions/branching.md" "---
id: CONV-branching
type: convention
project: $(basename "$TARGET_REPO")
owner: unknown
status: active
links: []
updated: $(date +%F)
---

# Branching Strategy

## Branch Roles

- Default branch: <set-per-repo>
- Integration/release branches: <set-per-repo>

## Branch Naming

- Feature: <set-pattern-per-repo>
- Fix: <set-pattern-per-repo>
- Hotfix: <set-pattern-per-repo>

## Merge Policy

- PR requirement: <set-per-repo>
- Merge method: <set-per-repo>
- Review/check gates: <set-per-repo>
"

write_if_missing "$DOCS_ROOT/features/README.md" "---
id: FEAT-index
type: feature
project: $(basename "$TARGET_REPO")
owner: unknown
status: active
links: []
updated: $(date +%F)
---

# Features

One folder per feature: FEAT-<id>
"

write_if_missing "$DOCS_ROOT/features/FEAT-template/overview.md" "---
id: FEAT-template
type: feature
project: $(basename "$TARGET_REPO")
owner: unknown
status: draft
links: []
updated: $(date +%F)
---

# Feature Overview Template
"

write_if_missing "$DOCS_ROOT/adr/README.md" "# ADR Index"
write_if_missing "$DOCS_ROOT/adr/0001-wiki-first-agent-flow.md" "# ADR 0001: Wiki-first agent flow"

if [[ -f "$TARGET_REPO/.gitignore" ]]; then
  if ! grep -q '^docs/project/generated/$' "$TARGET_REPO/.gitignore"; then
    printf "\n%s\n" "docs/project/generated/" >> "$TARGET_REPO/.gitignore"
  fi
else
  printf "%s\n" "docs/project/generated/" > "$TARGET_REPO/.gitignore"
fi

echo "bootstrapped wiki at $DOCS_ROOT"
