---
name: work-route
description: Orchestration rules for work-flow. Finds the models that the session can use, recommends the model for the main thread, selects the model tier (fast, standard, strong) and the subagent for each part of a step, and keeps token use low. Read by work-flow at the start of each run, or directly when the user asks which model to use for coding work.
---

# Orchestration and model choice

Obeys the contract in `work-flow`. The contract says what to do. This skill
says who does it, on which model, and with how much context.

## Goals, in this order

1. **Good work.** The user must not need to come back with a complaint.
2. **Cheap work.** Use the smallest model and the least context that reaches goal 1.

Cost never makes a quality rule weaker. Do not skip a check, a test, a
review, or a hard stop to save tokens. A cheap model that fails costs more
than a strong model that succeeds. Select the cheapest tier that will
probably succeed.

## Tiers

The rules use tier names. No rule names a model.

| Tier | Meaning |
| ---- | ------- |
| `fast` | the smallest, cheapest model |
| `standard` | the general coding model |
| `strong` | the strongest model in normal use |
| `top` | a model above `strong`, if the account has one |

## Find the models (at the start of each run)

Do not use your own knowledge of model names. It can be out of date.

1. State the model of this session. If you do not know it, say "unknown".
2. Read the configuration and keep what you find. A host settings file can
   hold secrets (tokens, keys, server credentials). Never print or read a
   whole settings file. Search it for the model keys only, for example
   `grep -nE '^(model|model_reasoning_effort)\b' <file>`:
   - the `models:` map in the instruction file
   - the host's own model settings and environment variables (the table in
     `reference/hosts.md` (in the `work-route` skill folder) says where they are for each host)
   - the model line of each `flow-` subagent definition
   - the model map in `project.md`, with its date
3. If nothing gives a map, use the default map of the host from
   `reference/hosts.md`. If the host is not in the file, all tiers are the
   model of this session, and routing by model is not active.
4. A session cannot list the models of the account. If the map is not clear,
   or the memory entry is older than 30 days, ask one time: "Which models
   can this account use? Tell me the fast, the standard, and the strong
   one." Save the answer with the date.
5. Show the map in 1 line: `models: fast=<model> · standard=<model> · strong=<model> · top=none`.
6. If a subagent call fails because a model is not available: remove the
   model from the map and tell the user. Use the next tier up. If there is
   none, use the next tier down, say that the quality floor is lower, and
   ask whether to continue. Record the result in memory.

A `models:` map in the instruction file has priority over steps 2 to 5:

```
models:
  fast: <alias or model id>
  standard: <alias or model id>
  strong: <alias or model id>
  top: <alias or model id; optional>
```

## The model for the main thread

The main thread is the orchestrator. It reads the returns, decides whether
an auto step passes, decides when to escalate, and applies Honesty. A
stronger main model makes these decisions better and costs more on each turn.

You cannot change the main model. Only the user can, with the host's
model command (see `reference/hosts.md`).
Recommend one time at the start:

| Situation | Recommended main model |
| --------- | ---------------------- |
| `cost=cheap` | `standard` |
| `cost=balanced`; small, low risk, most steps manual | `standard` |
| `cost=balanced`; large or high risk | `strong` |
| `cost=balanced`; most steps auto | `strong` (no person checks each step) |
| `cost=best` | `strong`, or `top` if the map has it |
| no subagents in this session | the highest tier that a step of this task needs |

Use this form. Recommend up and down:

> You run on `<model>`. For this task I recommend `<model>`, because `<reason>`.
> The cost is `<higher | lower>` token use on each turn. Switch the model
> with `<the host's model command>`, or reply `continue`.

- Give the reason from this task: size, risk, and the number of auto steps.
- If the current model is correct, say nothing.
- Recommend again after `work-propose` sets the size, only if the recommendation changed.
- If the user declines, do not ask again in this run. Record the choice.

## Roles

The orchestrator reads the state file, selects the route, sends briefs,
asks the user the step questions, and makes the commits. It does not read
large files or long tool output.

| Subagent | Default tier | Can edit | Used for |
| -------- | ------------ | -------- | -------- |
| `flow-scout` | fast | no | search, read, list references, run the checks and summarise, git status, reports |
| `flow-worker` | standard | yes | write code and tests, simplify, remove dead code, fix failures |
| `flow-architect` | strong | no | difficult causes, solution design, rework |
| `flow-reviewer` | strong | no | the independent review and the score |

The `model:` line in a subagent file is the default alias. Pass the model
from the map with each call. You can pass a different tier for one call.

## Tier for each step

`size` and `risk` come from the state file. Before `work-propose` sets the
size, use `medium`.

| Step | Part | small, low risk | medium | large or high risk |
| ---- | ---- | --------------- | ------ | ------------------ |
| recall | read and check memory | fast | fast | fast |
| assess | find files, read history, reproduce | fast | fast | fast |
| assess | decide the cause and the verdict | standard | standard | strong |
| explain | use a valid area note again | fast | fast | fast |
| explain | write a new explanation and score | standard | standard | standard |
| grill | read the code to answer its own questions | fast | fast | fast |
| grill | the interview | main thread | main thread | main thread |
| research | search, read, summarise (a subagent with web tools, else main thread) | fast | fast | fast |
| research | label the findings, write the answer | standard | standard | standard |
| prototype | write the flowchart, the variants, or the demo | standard | standard | standard |
| propose | design the options | standard | strong | strong |
| build | a `mechanical` slice (see Build slices) | standard | standard | standard |
| build | a `judgment` slice | standard | strong | strong |
| test | list edge cases, write tests | standard | standard | standard |
| test | run all the checks, summarise failures (each step that runs them) | fast | fast | fast |
| clean | simplify | standard | standard | standard |
| prune | find references | fast | fast | fast |
| prune | delete and check again | fast | standard | standard |
| review | review and score | standard | strong | strong |
| ship | report, push, PR body | fast | fast | fast |
| remember | write draft memory entries | fast | fast | fast |

## Build slices

High risk raises the tier of the decisions (verdict, design, review). It
does not put all of the build on `strong`. Before the build, split the
approved file list into slices and label each in the state file:

- `mechanical`: the approved design leaves no decision. Wiring, modules,
  DTOs, schemas, controllers and delegates, docs, and tests for behaviour
  that the test plan names.
- `judgment`: a new rule or algorithm, logic that writes or deletes data,
  concurrency or retries, a prompt change, or a slice where the design
  left a question open. If you are not sure, label it `judgment`.

A `mechanical` slice that returns `needs-decision`, fails its tests 2
times, or gets a blocking finding goes up 1 tier (see Change of tier).

## Checks go to the scout

The main thread runs only the tests for the files of the current edit. A
run of all the checks (all tests, lint, build, coverage) goes to
`flow-scout`, which returns the totals against the baseline and the
failures only. This is not optional and token rule 7 does not apply to it.
The totals are tool output, so the `fast` floor below does not apply; a
failure that the scout explains is confirmed before it changes a verdict.

Two floors apply to each row:

- The reviewer is never on a lower tier than the tier that built the code.
- A `fast` result is never the only evidence for a verdict, a deleted
  function, or "no references found". A `standard` or `strong` agent confirms it.

## Risk

A task is high risk if it touches one of these:

- authentication, authorisation, sessions, secrets, cryptography
- money: payments, billing, pricing, tax
- data: schema changes, migrations, deletes, bulk updates
- concurrency, locks, queues, retries, caches
- a public API, a shared library, or code with many callers
- an area that memory marks as fragile or as the location of a repeated bug

`work-assess` records `risk: low | high` and the reason. If you are not sure, record `high`.

## Change of tier

Start on the tier in the table. Change the tier only on a signal.

Go up 1 tier when:

- an attempt failed and you have no new hypothesis
- 2 attempts on the same tier failed
- a review found a blocking finding in code from that tier
- an agent says that it is not sure, or returns `needs-decision` on a technical point
- a scout result conflicts with other evidence

Go down 1 tier only for mechanical work in a later round. Never move the
reviewer down. Record each change and its signal in the state file. Do not
go up because a task feels important. Do not stay on a tier that fails.

## Cost settings

| Setting | Effect |
| ------- | ------ |
| `cost=balanced` (default) | the table |
| `cost=cheap` | each `strong` cell in the small and medium columns becomes `standard`; the floors and the high-risk column do not change |
| `cost=best` | the assess verdict, propose, build, and review use `strong` for each size; scouts stay on `fast` |

- One step: `build.model=strong`, `review.model=standard`. This has priority over the table.
- If a user setting puts a high-risk part below the table's tier, follow
  Honesty: say the risk, ask one time, then do what the user decides.
- With `cost=best`, or when `strong` failed on a high-risk part, use `top` if the map has it.

## Token rules

1. **Send a brief.** Do not send the conversation. The brief names the state-file sections to read.
2. **The state file is the memory.** Detail goes into the state file. Keep only the summary.
3. **Short returns.** A subagent returns a maximum of 200 words and a list of `file:line` references.
4. **Summarise tool output.** The scout returns failures only: test name, message, first relevant stack line.
5. **Read narrowly.** Search first. Then read only the ranges that match.
6. **Use memory first.** A valid area note, a known command, or a past decision replaces a new investigation.
7. **Do small work inline.** If a part needs fewer than about 3 file reads and no long output, do it in the main thread.
8. **Read in parallel. Write in series.** Scouts can run in parallel. Only 1 agent edits the branch at a time.
9. **One job in one brief.**
10. **Cheap check first.** Run the tests for the changed files, then all the checks before a commit.
11. **New thread between steps.** On a long run, tell the user that `/work-flow resume` in a new thread keeps the context small.
12. **Effort follows tier.** Scouts: low. Workers: medium. Architect and reviewer: high.

## The brief

```
Role: <flow-scout | flow-worker | flow-architect | flow-reviewer>
Step: <step>, part: <part>
Read first: <absolute path of the step skill file>, section <name>
State file: .agents/work-flow/runs/<slug>.md, sections: <list>
Job: <one job, as an instruction>
Scope: <files it can read; files it can change>
Do not: commit, push, ask the user, change switches, go out of the scope
Return: <the fields>, maximum 200 words, with file:line references.
        Write detail to the state file under <section>.
        Say what is verified and what is not verified.
        If a decision is necessary, return `needs-decision` and the question.
```

The orchestrator knows the path of each skill file that it loaded. Put that
path in the brief. A subagent does not know where the skills are installed.

Rules for each subagent:

- It does not ask the user. It does not pass a step. Only the orchestrator does.
- It follows Honesty. "I did not find it" is a valid return.
- It does not start other subagents.

## No subagents

Some hosts do not run subagents, or do not let a subagent use its own
model. The `flow-` subagent definitions can also be missing: an installer
that installs only skills does not install them.

1. Say one time, at the start of the run:

   > This session has no `flow-` subagents. The run continues in one
   > thread. Two things are weaker: no model routing, and no independent
   > review. Recommendation: for `small`, `low` risk work, continue. For
   > `medium` or `large` work, or `high` risk work, install the subagents
   > (`install.sh --agent <host>` in the playbook repository) or use a host
   > that has subagents. If you continue here, the review step asks for a
   > new thread.

2. Record `routing: not active (<reason>)` in the state file.
3. Do the steps in the main thread.
4. Before each step, name the tier from the table: "Next step: propose.
   Recommended model: `<model>`. Switch the model and reply `continue`, or
   reply `continue`." If the current model is correct, say nothing.
5. The review follows "Who reviews" in `work-review`: in the same thread
   only for `small`, `low` risk work; in a new thread for other work.
6. `ship` on auto opens a draft PR when the review was not independent (see
   `work-ship`).
7. Obey each token rule that does not need a subagent.

## Records

- State file: for each step part, the subagent, the tier, the number of
  calls, and each tier change with its signal. Work done inline gets a
  line too: `inline (<reason>)`. A step does not pass while its routing
  line is missing.
- `work-ship` report: a table of the same. Exact token numbers are in the
  host's usage report.
- `lessons.md`: where a tier failed or was more than necessary, by area and
  task type. Memory can raise a start tier freely. It can lower one only
  after 2 runs that succeeded on the lower tier.
