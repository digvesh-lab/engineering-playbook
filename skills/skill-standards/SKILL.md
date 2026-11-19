---
name: skill-standards
description: The rules for writing a skill in this playbook - the kind of skill, the frontmatter, the description, the body, the language, the borrowed methods, and the wiring into work-flow - with a check script. Use when you create, change, split, or review a skill of this playbook.
---

# Write a skill for this playbook

A skill here is an instruction file for the agent. Write it so that the
agent takes the same path on each run.

## Before you write

1. Write the job of the skill in 1 sentence. If an existing skill does this
   job, change that skill.
2. Search skills.sh for a skill that does the job (`work-research` can do
   this). If one fits and its licence is compatible, borrow its method (see
   "Borrowed methods"). Write only what the borrowed method does not cover.
3. Select the kind:

| Kind | Example | First sentence of the description | Ends with |
| ---- | ------- | --------------------------------- | --------- |
| step of work-flow | `work-test` | "Step N of work-flow." | `## End of step`, `## Next` |
| on-call helper | `work-research` | "<Name> helper for work-flow." | `## End of the call`, `## Next` |
| user-only tool | `work-borrow-update` | a 1-line summary for the user | its last step |
| standalone standard | `git-standards` | what the standard covers | its last rule |

## Frontmatter

- `name`: the folder name, in kebab-case. A work-flow skill starts with `work-`.
- `description`: the job, then the triggers.
- `disable-model-invocation: true`: only for a skill that only the user starts.
  Then the description is a 1-line summary for the user.
- No other fields.

## Description

The agent reads each description at each turn. Each word costs context.

- Put the role first: "Step 5 of work-flow.", "Research helper for work-flow."
- Say what the skill does in 1 or 2 sentences.
- End with the triggers: "Use through work-flow when ...", "Use when ...",
  "Use directly with /<name> <argument>.". Write 1 trigger for each case.
  Do not write synonyms of the same case.

## Body

- Start a work-flow skill with "Obeys the contract in `work-flow`." Then
  say what it can write. Example: "Read only: change no code. Write only to
  the state file."
- Write steps as a numbered list. End each step on a condition that shows
  when it is done.
- Put each rule in 1 place. Point to the contract, `reference/`, or a
  borrowed file. Do not copy their text.
- Say what to do. Use "do not" only for a hard limit, and give the
  correct action with it.
- Keep `SKILL.md` at 200 lines or fewer. Move detail that only some cases
  need to `reference/<topic>.md`. Add a line that says when to read it.
- Name no agent product and no model. Say "the host" and the model tier
  (fast, standard, strong). Hosts and models are in `work-route`.
- Name no client, project, or private path. Use generic examples.
- Write in the style of `work-flow/reference/language.md`: about 80 percent
  ASD-STE100. Code, commands, and file names stay exact.

## Borrowed methods

- Get a borrowed method only with `/work-borrow-update add <name>`. Only the
  user starts it. The copy goes to `work-flow/borrowed/`, with a row in
  `LOCK.md` and a row in `work-flow/reference/borrowed-rules.md`.
- Do not edit a borrowed file. In the skill, list each borrowed rule that
  the contract overrides, and give the rule that applies.
- Name the borrowed file in the skill. Say what to do if it is not there.

For the general method of writing for agents (context pointers, steps and
completion criteria, when to split, pruning), read
`work-flow/borrowed/writing-for-agents.md`. If it is not there, use the
rules in this file only.

## Wiring

A new skill is not complete until each place that lists skills names it.

- **Step of work-flow**:
  - the chain table, the description, and the step table in `work-flow/SKILL.md`
  - the step table in `README.md`
  - the presets in `work-flow/reference/switches.md`
  - the switches line and a section in `work-flow/reference/state-file.md`
  - a row in the tier table of `work-route`
  - the "Next" section of the step before it
- **On-call helper**:
  - a `-` row and a note in the chain table of `work-flow/SKILL.md`, and its `:skip` switch
  - the presets in `switches.md`
  - the switches line and a section in `state-file.md`
  - a row in `work-route`
  - the step of the skill that calls it
  - "Other work-flow skills" in `README.md`
- **User-only tool**: "Other work-flow skills" in `README.md`.
- **Standalone standard**: a row in the first table of `README.md`, and its own section.

`install.sh` links each folder in `skills/`. After you add a folder, run
`install.sh` again for each host. Or link the folder by hand.

## Check

Run the check script from the root of the playbook:

```bash
python3 skills/skill-standards/scripts/check.py skills <name>
```

- An `ERROR` is a broken rule. Fix it before you finish.
- A `warn` is a long file or a long sentence. Fix it, or say why it stays.
- The script does not check the wiring. Search for the name of a similar
  skill (`rg -n work-research skills README.md`) and confirm each place.

The skill is complete when the check has no `ERROR` and the wiring list is done.
