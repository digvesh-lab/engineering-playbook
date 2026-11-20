# State file and resuming: detail

Part of the `work-flow` contract. The rules in `SKILL.md` have priority.

- File: `.agents/work-flow/runs/<slug>.md`. If the slug exists, add `-2`, `-3`.
- At the start, add `.agents/work-flow/runs/` to `.git/info/exclude`. The file is
  then never committed and does not make the working tree dirty.
- Earlier versions kept runs in `.claude/flow/` and memory in
  `.claude/work-memory/`. If an old folder exists and the new folder does
  not, tell the user and move it after a yes. Do not read the two locations.
- Each skill reads the state file first.
- **Keep the `steps:` block true.** When a step ends, write its output and
  its `steps:` line in the same edit. A step has not passed until its line
  says so.
- **Rewrite in place.** Put each new fact in the section that it belongs
  to. Replace what it makes wrong. Do not add dated sections. The phase
  log gets 1 line for each event: date, step, what happened, commit.
- **Keep it short.** Keep the file at about 200 lines or fewer. If a section
  gets long, keep the conclusion and its evidence references, and move the
  rest to `<slug>.notes.md` next to it. Skills do not read the notes file
  unless a step needs that detail.
- **If you cannot read this file or the template here**, stop and tell the
  user. Do not rebuild the template from memory. The usual cause: the host
  does not permit reads of the skill folder. The fix: add the folder that
  the skill link points to (the playbook clone) to the host's working
  directories, and read the reference files through that path.
  `install.sh` prints the setting.
- `resume <slug>`: read the state file. Check that the branch, the latest
  commit, and the pull request agree with it. If they do not, that is a hard
  stop (see Hard stops in `SKILL.md`). Write or replace the `session:` line
  with the current session; remove it if there is no id. Show the switches.
  Continue from the first step that did not pass.
- **Session id.** The id that the host gives this session. If the host has
  no id but has a scratchpad path `.../<uuid>/scratchpad`, use that uuid.
  Write the line as `session: <id>` with nothing after the id. If there is
  no id, omit the line.

## Resume without a slug

1. List `.agents/work-flow/runs/*.md`. Skip `*.notes.md`. If there is none,
   say so and stop.
2. Show 1 line for each run: slug, `task:`, `branch:`, and the first step
   that did not pass (`done` if each step passed or was skipped). Put the
   runs that are not `done` first. Sort by the date of the last phase-log
   line, newest first; break ties, or with no phase log, use the file
   modification time.
3. Ask the user to select one. Always ask, also when only 1 run exists, and
   give a `cancel` option. If the question tool of the host limits the number
   of options, show the newest runs and accept a slug typed as free text.
4. Continue as for `resume <slug>`.

`status` uses steps 1 and 2 and stops.

Template:

```
task: <1 line>
session: <session id; see "Session id" above>
ref: <issue or ticket link, if any>
issues: <each issue that this run created or uses: number, title, parent, blocked by>
type: bug | feature | refactor | performance | upgrade | tests | docs | question
observed-in: <where the problem was seen, or "n/a">
environment: local | dev | staging | production (read only) | code only
needs: <data, flags, config, services necessary to reproduce>
base: <branch that the work starts from>
branch:
switches: {recall: auto, assess: manual, explain: manual, grill: manual,
  propose: manual, build.branch: manual, build.commit: manual, test: manual,
  clean: auto, prune: auto, review: manual, ship.push: manual,
  ship.pr: manual, remember: auto, iterate: manual, tickets: manual,
  research: manual, prototype: manual}
switch-source: <default | project instruction file at <base commit> | user instruction file for all projects | the user's message>
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
delivery: single | stacked     # stacked: see "Stacked delivery" in reference/tickets.md
pieces:              # stacked only: key, branch, base, PR, issue, status, tries, rounds
steps:               # pending | passed (user) | passed (auto: <reason>) | passed (unrecorded) | redo | stopped
  recall: pending    # each passed step also records its last commit hash
  ...
## Recalled from memory
## Task summary
## Verdict and evidence
## Explanation and score
## Research (each call: question, findings with labels and links, answer, gaps)
## Requirements (goal, acceptance criteria, out of scope, open questions)
## Options and approved solution (with file list and test plan)
## Prototype (each call: question, shape, files, variants, chosen, settled)
## Check baseline
## Phase log (each attempt, also the failed attempts)
## Routing log (step part, subagent, tier, calls, each tier change and its signal)
## Test results
## Review findings and rounds
## Disagreements (the user's choice against the recommendation, and the evidence)
## Process failures (a skipped step, a wrong order, a missed hard stop)
## Open items
```
