# Borrowed skills: detail

Part of the `work-flow` contract. The rules in `SKILL.md` have priority.

Source: https://github.com/mattpocock/skills (MIT licence). The copies are
in `borrowed/`. `borrowed/LOCK.md` lists them and the source commit of each.

| Step | Borrowed file | Used for |
| ---- | ------------- | -------- |
| work-assess | `diagnosing-bugs.md` | the reproduction and the search for a cause |
| work-grill | `grilling.md`, `domain-modeling.md`, `to-spec.md` | the interview, the glossary and decision records, the spec |
| work-propose | `to-tickets.md` | the split of large work and the form of a ticket |
| work-prototype | `prototype.md` (with `prototype/UI.md`, `prototype/LOGIC.md`) | the UI variants and the logic demo |
| work-retro | `retro.md` | the categories of improvement |
| work-build | `tdd.md` | the test-first loop |
| work-review | `code-review.md` | the review |

Rules:

- A borrowed file gives the method for one step. It does not change the
  order of the steps, the switches, the scope, or the hard stops.
- If a borrowed file conflicts with the contract, the contract has priority.
  This includes: approval before an edit, a question before a commit or a
  push, Honesty, and Language. Tell the user. Record it under "Process failures".
- If a borrowed file calls a different skill by name: read the copy in
  `borrowed/` if there is one. If there is none, do not run it. Say that
  the dependency is missing.
- If a borrowed file says to publish to an issue tracker, add labels, or run
  `/setup-matt-pocock-skills`: do not. Write the spec, the tickets, and the
  findings to the state file. The `tickets` switch is the only path to the
  issue tracker. It publishes at the end of `work-propose`, after a
  solution is approved, with the rules in `tickets.md`. A spec or a ticket
  is never published during `work-grill`.
- If a borrowed file says to write ticket files under `.scratch/`: do not.
  Write the tickets to the state file.
- If a borrowed file says to write `GLOSSARY.md` or a decision record
  immediately: that is an edit. Show the entry and get approval first,
  unless the switch of the step is `auto`. Record each entry in the state file.
- If a borrowed file says to continue when the user does not answer: do not,
  unless the switch of the step is `auto`.
- If a borrowed file says to call a server, run a script, or read an issue
  tracker: use only the environments that are switched on, and only read.
  The hard stops apply. Keep a copy of a script template out of the tracked files.
- If a borrowed file links to a supporting file, the copy is in
  `borrowed/<name>/`, with the same relative path.
- If a borrowed file says to ask the user a question, and the switch is
  `auto`: use the answer from the approved solution or the requirements, and
  record it. If they give no answer, ask.
- If a borrowed file says to start subagents: only the orchestrator starts
  them. Use the `flow-` subagents and the tiers from `work-route`.
- If a borrowed file is not there, the step uses its own method. Say so in
  1 line and record it in the state file.
- Do not edit a borrowed file. Only `/work-borrow-update` changes it. Only
  the user starts that skill.
