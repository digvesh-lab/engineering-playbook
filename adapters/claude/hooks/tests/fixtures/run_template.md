task: add a widget endpoint
session: $session
ref: n/a
issues: none
type: $type
observed-in: n/a
environment: code only
needs: none
base: $base
branch: $branch
switches: {recall: auto, assess: manual, explain: manual, grill: manual,
  propose: manual, build.branch: manual, build.commit: manual, test: manual,
  clean: auto, prune: auto, review: manual, ship.push: manual,
  ship.pr: manual, remember: auto, iterate: manual, tickets: manual,
  research: manual, prototype: manual}
switch-source: default
budgets: {tries: 3, rounds: 2}
risk: low
size: small
cost: balanced
models: {fast: , standard: , strong: , top: }
main-model: m (recommended: standard; user chose: standard)
routing: not active (small)
review-independent: no
git-standards: defaults
env: $env
delivery: single
pieces:
steps:               # pending | passed (user) | passed (auto: <reason>) | passed (unrecorded) | redo | stopped
$steps
## Recalled from memory
## Task summary
## Phase log (each attempt, also the failed attempts)
$log
## Open items
