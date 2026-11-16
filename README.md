# Engineering Playbook

How I work on software projects with coding agents: a set of agent skills,
and the tooling for a repository wiki. The skills name no agent product.
They run on any agent that reads the [Agent Skills](https://agentskills.io)
format.

| Part | What it is | Where |
| ---- | ---------- | ----- |
| work-flow | a chain of skills that takes a coding task from assessment to a pull request | `skills/work-*` |
| git-standards | default conventions for branches, commits, pull requests, and issues | `skills/git-standards` |
| subagents | 4 role definitions that work-flow uses when the agent supports them | `adapters/<agent>/agents/` |
| repo wiki | a template and scripts for a `docs/project/` wiki with a typed graph | repository root |

## Install

**Skills, on any agent.** Needs Node.js.

```bash
npx skills add digvesh-lab/engineering-playbook -g          # all skills, for the user
npx skills add digvesh-lab/engineering-playbook -g -a codex # one agent
```

This installs the skills only. It does not install the subagents.

**Skills and subagents, from a clone.** This links the files, so a
`git pull` updates them.

```bash
git clone https://github.com/digvesh-lab/engineering-playbook
cd engineering-playbook
./install.sh --agent claude     # or: codex, kiro
./install.sh --agent claude --uninstall
```

| Agent | Skills go to | Subagents go to |
| ----- | ------------ | --------------- |
| `claude` | `~/.claude/skills/` | `~/.claude/agents/` |
| `codex` | `~/.agents/skills/` | `~/.codex/agents/` |
| `kiro` | `~/.kiro/skills/` | not installed |

Install all the `work-*` skills together. `git-standards` works alone. Each step skill reads the
contract and the reference files in `work-flow`.

**Without subagents** the flow runs in one thread. It has no model routing
and no independent review. That is acceptable for small, low-risk work. For
medium or large work, or high-risk work, install the subagents or use an
agent that has them. If you do not, the review step asks you to continue in
a new thread, and the pull request opens as a draft.

For Codex, the installer copies the subagent files, because Codex does not
start a subagent whose definition is a symlink. Run `install.sh --agent
codex` again after an update.

## work-flow

```
/work-flow <task> [preset] [step:manual|auto ...]
/work-flow resume [slug]
/work-flow feedback [slug]
/work-flow status
/work-retro
```

The task is an issue number or URL, pasted text, or a sentence.

| # | Step | Skill | What it does |
| - | ---- | ----- | ------------ |
| 1 | recall | `work-memory` | reads the notes from earlier runs |
| 2 | assess | `work-assess` | selects the task type, checks that the work is necessary, gives a verdict with evidence |
| 3 | explain | `work-explain` | explains the part of the system and gives the current code a score |
| 4 | grill | `work-grill` | questions the requirements and writes a short spec |
| 5 | propose | `work-propose` | proposes 1 to 3 solutions; creates the GitHub issues |
| 6 | build | `work-build` | creates a branch, records the check baseline, writes the solution |
| 7 | test | `work-test` | proof for the task type, edge cases, regression, a real run |
| 8 | clean | `work-clean` | makes the new code simple with no change of behaviour |
| 9 | prune | `work-prune` | removes dead code and debug output |
| 10 | review | `work-review` | an independent review and a score against the baseline |
| 11 | ship | `work-ship` | the report, the push, the pull request |
| 12 | remember | `work-memory` | records notes for later runs |

`git-standards` holds the default conventions for branches, commits, pull
requests, and issues, with one grammar for all four. It applies only where
a repository has no convention of its own. work-flow uses it for each
branch, commit, pull request, and issue in a run. It also works alone. If it
is not installed, work-flow uses the short form in
`skills/work-flow/reference/git-defaults.md`.

Other work-flow skills: `work-route` (which model tier and which subagent does each
part), `work-retro` (finds mistakes of the workflow that repeat),
`work-borrow-update` (updates the borrowed method files).

The contract is `skills/work-flow/SKILL.md`. Each step skill obeys it.

### Switches and automation

Each step has a switch: `manual` (the step shows its result and waits) or
`auto` (the step continues if its conditions are met). A preset sets all of
them: `default`, `manual`, `guided`, `auto`, `full-auto`.

To run with no questions, put this line in the instruction file of the
project (`AGENTS.md` or `CLAUDE.md`):

```
work-flow-defaults: full-auto
```

Auto removes the question. Auto does not remove the work. These continue to
apply on `full-auto`:

- **Auto conditions.** For example, a solution is taken with no question
  only if it fits the current design, is not large, and changes no schema,
  public API, or dependency.
- **Hard stops.** A write to production, a secret, a destructive data
  change, a force-push, a merge, or a file outside the approved scope always
  stops the run and asks.
- **Ready or draft.** The pull request opens as ready only if the risk is
  low and the review was independent. If not, it opens as a draft and says why.

### Settings in the instruction file

| Key | Sets |
| --- | ---- |
| `work-flow-defaults:` | the preset and switches for each run |
| `models:` | the model for each tier: `fast`, `standard`, `strong`, `top` |
| `checks:` | the commands for tests, lint, type-check, and build |
| `environments:` | how to get to local, dev, staging, and production logs |
| `docs:` | where the glossary and the decision records are |
| `work-memory: shared` | commit the project memory |
| `playbook-repo:` | the repository that gets the issues from `work-retro` |

### Tickets

With the `tickets` switch, `work-propose` creates GitHub issues with `gh`
after a solution is approved: 1 issue for the work, or a parent issue with 1
issue for each piece when a large solution is split. The pull request has
`Fixes #<n>`. A run builds 1 piece. Each open piece is the task for a new
run. Detail: `skills/work-flow/reference/tickets.md`.

### Retro

`/work-retro` reads the records of earlier runs: process failures, failed
attempts, review rounds, disagreements, and routing. A mistake that occurs
in 2 runs or more, or 1 missed hard stop, becomes a candidate with its
evidence and one fix. You accept or reject each candidate. An accepted
candidate becomes an issue, and the fix is a normal `/work-flow` run.

A retro changes nothing itself. A mistake where the agent did not obey an
instruction gets enforcement outside the agent (a hook, a permission rule,
a CI check), not one more instruction.

### Files that a run writes

| Path | Holds | Committed |
| ---- | ----- | --------- |
| `.agents/work-flow/runs/<slug>.md` | the state of 1 run | no |
| `.agents/work-flow/memory/` | notes across runs | only with `work-memory: shared` |

### Borrowed methods

Some steps use a method file from
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT licence).
The copies are in `skills/work-flow/borrowed/`, with their source commit in
`LOCK.md`. The contract has priority over a borrowed file.
`/work-borrow-update` updates them and shows each change before it replaces a file.

## Repo wiki

A reusable wiki structure for any software repository. It does not assume a
language, framework, hosting model, delivery process, or branch model.

```bash
./bootstrap-wiki.sh /abs/path/to/target-repo
node validate-wiki-graph.js /abs/path/to/target-repo
node generate-wiki-graph.js /abs/path/to/target-repo
```

The bootstrap script writes only the files that are missing. It does not
overwrite a wiki page, so you can run it again after the playbook grows. It
also adds `docs/project/generated/` to `.gitignore`.

```text
docs/project/
  README.md  index.md
  metadata/      glossary, ownership, lifecycle
  architecture/  context, containers, components, data-flows, dependencies
  adr/           decision records
  features/      FEAT-template/ (overview, design, api, data-model, testing, rollout, runbook)
  apis/          index, endpoints/, events/
  data/          schema, migrations, contracts
  conventions/   branching, coding, constraints, review-checklist
  graph/         contract
  runbooks/      deploy, rollback, incident-template, auth-gh-switch
  incidents/     YYYY/
  changelog/     YYYY-MM.md
  logs/          YYYY-MM.md
  generated/     graph.json, graph.html
```

Rules for the wiki:

- Keep the shared templates general. Record the facts of a repository only in that repository.
- "API" includes HTTP, events, CLI commands, files, packages, jobs, and manual contracts.
- Each Markdown page under `docs/project/`, except `generated/`, has
  frontmatter with a stable `id`, a valid `type`, a valid `status`, and `relations`.
- Graph edges come from typed `relations`, not from links in the text:

```yaml
relations:
  - type: depends_on
    target: RUN-rollback
  - type: exposes
    target: API-session-create
```

- Use `relations: []` only for a page that is standalone on purpose.

`frontmatter-template.md` has the frontmatter. `agent-workflow.md` has the
order in which an agent reads and updates the wiki.

## Licence and credit

MIT. See `LICENSE`. You can use, change, and share this work. Each copy, or
substantial part of it, must keep the copyright notice and the licence text.

The work-flow contract, the step skills, `work-route`, `work-retro`, the
subagent definitions, `git-standards`, and the wiki tooling are the
work of [digvesh-lab](https://github.com/digvesh-lab).

The files in `skills/work-flow/borrowed/` are copies from
[mattpocock/skills](https://github.com/mattpocock/skills), under their own
MIT licence (`skills/work-flow/borrowed/LICENSE-mattpocock.txt`).
