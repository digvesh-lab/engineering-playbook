# State file and resuming: detail

Part of the `work-flow` contract. The rules in `SKILL.md` have priority.

- File: `.agents/work-flow/runs/<slug>.md`. If the slug exists, add `-2`, `-3`.
- At the start, add `.agents/work-flow/runs/` to `.git/info/exclude`. The file is
  then never committed and does not make the working tree dirty.
- Earlier versions kept runs in `.claude/flow/` and memory in
  `.claude/work-memory/`. If an old folder exists and the new folder does
  not, tell the user and move it after a yes. Do not read the two locations.
- Each skill reads the state file first.
- `resume`: read the state file. Check that the branch and the latest commit
  agree with it. If they do not, that is a hard stop. Show the switches.
  Continue from the first step that did not pass.

Template:

```
task: <1 line>
ref: <issue or ticket link, if any>
issues: <each issue that this run created or uses: number, title, parent, blocked by>
type: bug | feature | refactor | performance | upgrade | tests | docs
observed-in: <where the problem was seen, or "n/a">
environment: local | dev | staging | production (read only) | code only
needs: <data, flags, config, services necessary to reproduce>
base: <branch that the work starts from>
branch:
switches: {recall: auto, assess: manual, explain: manual, grill: manual,
  propose: manual, build.branch: manual, build.commit: manual, test: manual,
  clean: auto, prune: auto, review: manual, ship.push: manual,
  ship.pr: manual, remember: auto, iterate: manual, tickets: manual,
  research: manual}
switch-source: <default | instruction file at <base commit> | the user's message>
budgets: {tries: 3, rounds: 2}
risk: low | high (<reason>)
size: small | medium | large      # from work-propose; medium until then
cost: balanced
models: {fast: , standard: , strong: , top: }
main-model: <model of this session> (recommended: <tier>; user chose: <...>)
routing: active | not active (<reason>)
review-independent: yes (subagent | new thread) | no
git-standards: repository convention | git-standards skill | defaults
env: []
steps:               # pending | passed (user) | passed (auto: <reason>) | redo | stopped
  recall: pending    # each passed step also records its last commit hash
  ...
## Recalled from memory
## Task summary
## Verdict and evidence
## Explanation and score
## Research (each call: question, findings with labels and links, answer, gaps)
## Requirements (goal, acceptance criteria, out of scope, open questions)
## Options and approved solution (with file list and test plan)
## Check baseline
## Phase log (each attempt, also the failed attempts)
## Routing log (step part, subagent, tier, calls, each tier change and its signal)
## Test results
## Review findings and rounds
## Disagreements (the user's choice against the recommendation, and the evidence)
## Process failures (a skipped step, a wrong order, a missed hard stop)
## Open items
```
