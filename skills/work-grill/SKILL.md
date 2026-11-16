---
name: work-grill
description: Step 4 of work-flow. Interviews the user about the task until the requirements are clear, writes a short spec, and updates the project glossary. Uses the borrowed grilling, domain-modeling, and to-spec methods from mattpocock/skills when they are present. Use through work-flow, or directly to question a plan before code is written.
---

# Step 4: question the requirements

Obeys the contract in `work-flow`. Do not edit code. You can write the spec
to the state file and update the glossary.

This step finds the difference between what the user said and what the user means.

## Method

Read the borrowed files in `~/.claude/skills/work-flow/borrowed/` that exist:

- `grilling.md`: the method for the interview.
- `domain-modeling.md`: the method for the glossary and the decision records.
- `to-spec.md`: the form of the spec. Write the spec to the state file. Do
  not publish it to an issue tracker unless the user asks.

The contract has priority (see Borrowed skills in `work-flow`).

If the borrowed files do not exist, use this method:

1. Read the task summary, the evidence, and the glossary.
2. Answer your own questions from the code first. Ask the user only what
   the code cannot answer.
3. Ask in rounds. In one round, ask each question that does not depend on an
   answer that you do not have. Give each question a number and your
   recommended answer. Word it so that "yes" accepts your answer. Wait for
   the answers before the next round.
4. Cover what applies:
   - who uses this, and what they do before and after
   - the behaviour for normal, empty, wrong, and large input
   - what must not change
   - data: its source, its volume, its frequency, and what a repeat does
   - errors: what the user sees, what is logged, what is tried again
   - permissions and roles
   - what is out of scope
   - how the user will know that it works
5. If a term is unclear or has 2 meanings, agree one meaning. Put it in the glossary.
6. Stop when no answer can change the design. Do not ask to appear thorough.

Do the interview in the main thread. A subagent cannot ask the user.

## Output

Write to the state file under "Requirements":

- the goal, in 1 or 2 sentences
- the acceptance criteria: a numbered list that a test can check
- what is out of scope
- open questions that the user decided to leave
- glossary terms that you added or changed

For a bug with a reproduced cause, the acceptance criteria are: the
reproduction passes, and what must stay the same.

## End of step

Show the requirements. Ask: "Are these requirements complete and correct?"

Switch: `grill`.

- `grill:auto`: do not interview. Pass only if:
  - each acceptance criterion comes from the task text or the user, not from you
  - no open question can change the design
  - the task is not high risk

  If one is not met, interview.
- `grill:skip`: do not interview. Record the acceptance criteria from `work-assess`.

If a requirement conflicts with the code or with a different requirement,
say so before you continue (see Honesty in `work-flow`).

## Next

`work-propose`
