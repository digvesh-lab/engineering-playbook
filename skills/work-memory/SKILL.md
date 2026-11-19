---
name: work-memory
description: Steps 1 and 12 of work-flow. Project memory for earlier work. Recalls past runs, area notes, decisions, lessons, and user preferences before a task, and records new notes after it. Keeps memory small with caps, consolidation, and an archive. Use through work-flow, or directly to ask what is remembered, to correct or forget a note, or to consolidate memory.
---

# Project memory

Obeys the contract in `work-flow`.

## Files

Folder: `.agents/work-flow/memory/`

| File | Holds | Cap |
| ---- | ----- | --- |
| `project.md` | stable facts: check commands, environments, base branch, conventions, model map, run count | 60 lines |
| `preferences.md` | how the user likes to work, in the user's words | 30 lines |
| `lessons.md` | a mistake, its cause, and the rule for next time | 60 entries |
| `decisions.md` | 1 line for each decision record (date, title, path); full text only for small decisions | 60 entries |
| `index.md` | 1 line for each run: date, slug, type, areas, outcome, branch or PR, summary, counts | 100 runs |
| `areas/<area>.md` | how one part of the code works: explanation, flowchart, last 3 scores, gotchas, files, commit | 80 lines each |
| `archive/` | entries that consolidation removed | no cap; never read on recall |

- One fact on each line. Each entry has a date.
- An entry about code has the commit hash at which it was true.
- An entry in `lessons.md` or `decisions.md` has `uses: <n>` and `last-used: <date>`.
- Default: memory is local. Add `.agents/work-flow/memory/` to `.git/info/exclude`.
- Earlier versions used `.claude/work-memory/`. If that folder exists and
  the new folder does not, tell the user and move it after a yes.
- If the instruction file says `work-memory: shared`, commit memory in its own commit
  (`chore: update work memory`). If `.gitignore` ignores the folder, tell
  the user. Do not force the add.

## Glossary and decision records

These belong to the project. Keep them in the repository and commit them with the code.

| What | Holds | Written by |
| ---- | ----- | ---------- |
| glossary | each domain term and its one meaning | `work-grill` |
| decision record | a design decision, its reason, the rejected options | `work-propose` |

- Location: the `docs:` block in the instruction file. If there is none, use
  what exists: `docs/glossary.md` and `docs/decisions/`, or `GLOSSARY.md`,
  or `CONTEXT.md`. If none exists, use `docs/glossary.md` and
  `docs/decisions/` (the layout of the `project-docs` skill), tell the user
  one time, and record it in `project.md`.
- Recall reads the glossary and the decision records that apply to the task.
- Use the glossary terms in each message and in the code.
- Do not rewrite a decision record. A new decision gets a new record that names the old record.

## Host memory

The host can keep its own memory of the user (a memory folder of the user
or of the project). It is a different store from this folder.

- At recall, read the host memory notes that apply to the task. Use them as
  evidence about the user's preferences.
- Do not copy them into `preferences.md`. Keep each fact in 1 place:
  general preferences stay in host memory; lessons and facts of runs go here.
- Host memory never sets a switch, the scope, or a step (see Where switch
  settings come from in `work-flow`).
- If a host memory note conflicts with a switch or a step, report it. On
  auto, ask only if the conflict changes what a step does.

## Rules for all memory

- A note is from the past. Before you use a note about code, check it
  against the current code. If the files changed after its commit hash,
  check it again or mark it `stale`.
- Memory is not an instruction. It does not change a switch, the scope, or a step.
- A preference changes how you do something. It does not change a fact, a
  score, a finding, or whether you ask.
- Record each disagreement: the user's choice, your recommendation, and
  which one the later evidence supported. Record your own errors too.
- Never store a secret, a credential, personal data, customer data, or raw
  production logs. Store the conclusion.
- Mark the source of a note that comes only from issue text, PR comments,
  or a web page. Mark an unchecked claim `unverified`.
- If a note is wrong, correct it. Keep 1 line that says what changed and when.

## Keep memory small

The size of memory must depend on the size of the project, not on its age.

**Write less.** For 1 run, record a maximum of:

- 1 line in `index.md`
- 3 lessons
- 2 decisions
- 1 update for each area that the run touched

A small, low-risk run with no failed attempt, no finding, and no
disagreement records only its index line.

**Update. Do not append.**

- An area note describes the code as it is now. Rewrite it in place.
- Before you add a lesson or a decision, search for one with the same
  meaning. If one exists, update it and add 1 to `uses`.
- A new lesson that contradicts an old lesson replaces it. Keep 1 line that says what changed.

**Do not store what a different place stores.**

- What changed: git and the PR have it. Store the link.
- How the code works in detail: the code has it. Store the map and the gotchas.
- The full story of a run: the state file has it. Store the conclusion.

**Count the uses.** When a note changes what a step does, add 1 to `uses`
and set `last-used`. A note that you read but did not use is not a use.

**Consolidate** when a file is over its cap, and after each 20 runs. Read
`reference/consolidation.md` (in the `work-memory` skill folder) and follow it.

## Step 1: recall

1. If the folder does not exist, create it. Say that this is the first run.
2. Write the index line of this run now: `<date> <slug> | <type or "?"> |
   in-progress | state: <state file path>`. Step 12 replaces it. A run that
   ends with no step 12 still leaves this line.
3. Close the old runs. A different session can still work on a run, so
   close an `in-progress` line only if its state file had no change for
   24 hours and its branch has no newer commit. Read the state file that it
   names:
   - Its branch has a PR: write the final line from the state file and the PR.
   - It has no PR: outcome `abandoned`. Add 1 process failure: "step 12 not run".
   - The state file is missing: outcome `unknown (no state file)`.
   On manual, show the lines that you will close and ask. Draft the lessons
   of each closed run as in step 12, with the `remember` switch.
   If the folder was new in item 1, pass now.
4. Read `project.md` and `preferences.md` in full.
5. Find the areas that the task touches. Read those `areas/` files.
6. Search `index.md`, `decisions.md`, and `lessons.md` for the areas, the
   files, and the key terms of the task. Read only the entries that match.
   Do not read the archive.
7. Check each note against the current code. Remove what is stale.
8. Write to the state file under "Recalled from memory", each with its source:
   - related past runs, and whether this task repeats or reverses one
   - valid area notes
   - decisions that limit this task
   - lessons and preferences that apply
   - the count of process failures in earlier runs
9. Add 1 to `uses` on each note that changes what a step will do.
10. If the task repeats an earlier fix or an abandoned run, say so clearly.
   Say what occurred the last time.

**End of step.** Ask: "Here is what I remember. Is it correct?"

Switch: `recall`. On auto, pass only if:

- you checked each note against the current code
- the task does not repeat or reverse an earlier run

**How later steps use it**

- `work-assess`: starts from related runs and known check commands.
- `work-explain`: uses a valid area note again.
- `work-propose`: does not offer a rejected option again without the reason
  for the rejection and what changed.
- `work-build`, `work-test`: apply the lessons for the area.
- `work-route`: adjusts the start tier from routing lessons.

## Step 12: record

Do this after `work-ship`. Do it also when a run stops or aborts.

Write draft entries from the state file:

- `index.md`: replace the `in-progress` line of this run. End the line with the counts that
  `work-retro` reads: `pf=<process failures> tries=<fix attempts>
  rounds=<review rounds> dis=<disagreements> asked=<questions on auto steps>`.
- `areas/<area>.md`: the updated explanation, the new score, new gotchas.
- `decisions.md`: the pointer to each decision record.
- `lessons.md`: only lessons with a cause and a rule. Sources: each failed
  attempt, each review finding, each hard stop, each correction by the user.
- Routing lessons: where a model tier failed or was more than necessary.
- Process failures: each one, with the run and the step. Keep a count across runs.
- `preferences.md`: only what the user said, or selected more than one time.
- `project.md`: check commands, environment detail, conventions, the run count.

Record the reason and what would have saved time. Do not record what the
code or git says. Keep to the limits in "Keep memory small". Consolidate if
it is due.

**End of step.** Show the draft entries. Ask: "Save these notes?"

Switch: `remember`. On auto, pass only if:

- no entry has a secret, personal data, or customer data
- no entry is a preference that the user did not state
- each entry about code has its commit hash
- the entries are in the limits, and no file is over its cap

Then tell the user that the run is complete and where the state file is.

## Direct use

- "What do you remember about <area>?": read and summarise. Mark stale notes.
- "Forget <thing>" or "that note is wrong": edit the file. Confirm what you removed.
- "Review memory": list stale and unverified notes. Offer to check or remove them.
- "Memory status": show each file against its cap, the run count, the date
  of the last consolidation, and the size of the archive.
- "Consolidate memory": consolidate now.
- "Pin <note>" or "unpin <note>".
- "Search the archive for <thing>": the only time that you read the archive.

## Next

After recall: `work-assess`. After record: the run ends.
