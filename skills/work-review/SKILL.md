---
name: work-review
description: Step 10 of work-flow. Reviews the completed change independently, gives it a score against the baseline, and sends blocking problems back to the build step for a new round. Use through work-flow after the 3 work phases, or directly to review the changes on the current branch.
---

# Step 10: review

Obeys the contract in `work-flow`. Read only: this step finds problems.
`work-build` fixes them in the next round.

## Who reviews

The agent that wrote the code does not review it. Use the `flow-reviewer`
subagent, on the tier from `work-route`. The reviewer is never on a lower
tier than the builder. Give it only:

- the task summary and the "Requirements"
- the approved solution and its file list
- the diff: `git diff <base>...<branch>`
- the baseline scores and their reasons, with their source

Do not give it the build conversation or the phase log.

If the state file has no baseline scores (for example `explain:skip`), the
reviewer gives the Before scores for the code on the base, with the rubric
of `work-explain`. Record their source as `reviewer@<base commit>`.

If no subagent is available:

- `small` size and `low` risk: review in this thread from the git diff
  only. Record `review-independent: no`. Say so in the report.
- `medium` or `large` size, or `high` risk: do not review in the thread
  that built the code. Tell the user: "This change needs an independent
  review. Start a new thread and run `/work-flow resume <slug>`." A review
  in a new thread reads only the state file sections and the diff that a
  reviewer gets. Record `review-independent: yes (new thread)`.

With a subagent, record `review-independent: yes (subagent)`.

## Borrowed method

If `borrowed/code-review.md` (in the `work-flow` skill folder) exists, use its
method. The contract has priority (see Borrowed skills in `work-flow`). If
it does not exist, use the method in this skill.

The borrowed method reviews the diff from a fixed point on 2 axes, each
with its own reviewer: does the code follow the repository's standards, and
does it do what the spec says.

- The fixed point is the `base` in the state file.
- The spec is the "Requirements" in the state file.
- The orchestrator starts 2 `flow-reviewer` calls in parallel, one for each
  axis. A reviewer does not start other subagents.
- The orchestrator puts the 2 results into one list of findings.

The checklist, the grades, and the score table in this skill always apply.

## Check

1. **Task.** Check each acceptance criterion or reproduction step against the diff.
2. **Scope.** Find what the task did not need, and what it needed that is missing.
3. **Correctness.** Logic errors, unhandled errors, edge cases with no test.
4. **Security.** Input handling, injection, authorisation on new paths,
   secrets or personal data in code or logs.
5. **Safety.** Data migrations, backward compatibility, behaviour on failure, how to undo.
6. **Performance.** New loops over data, queries in loops, work on a hot path.
7. **Tests.** Do they test behaviour? Do they fail if the code is wrong? Was one made weaker?
8. **Fit.** Agrees with the approved solution and the design. No duplicate
   helper. Consistent names and style.
9. **What is left.** Debug output, dead code, old comments.

If clean or prune changed something, do the real run from `work-test` (item 6) again.

## Findings

Each finding has a `file:line`, what is wrong, why it is important, and a grade:

- `blocking`: wrong, unsafe, or does not do the task. Must be fixed.
- `should-fix`: a real weakness. Fix it now, or list it under "Open items" with a reason.
- `note`: no action is necessary.

A finding with no evidence is `unverified`. It is never `blocking`.

## Score

Give a score for the same 4 areas as `work-explain`, against the same things:

| Area | Before | After | Why |
| --- | --- | --- | --- |
| Correctness | | | |
| Readability | | | |
| Test coverage | | | |
| Fit with the design | | | |

- Give the score for the code as it is, not for the effort. A score can stay
  the same or go down.
- A score that went down is a `blocking` finding, unless the approved
  solution accepted that cost.
- Do not raise a score, lower a grade, or drop a finding to end the loop.
- Do not invent a finding. If the change is good, say so in 1 sentence.
- If the user disputes a finding, change it only for new evidence (see
  Honesty in `work-flow`).
- Review each choice under "Disagreements" as you review other code.

## Return form

Each reviewer returns only this form. Use only these words for the grades.

```
findings:
  - <blocking | should-fix | note | unverified> <file:line> - <what is wrong> - <why it is important>
counts: blocking=<n> should-fix=<n> note=<n> unverified=<n>
scores:            # the 4 areas, 1 to 10
  correctness: <before> -> <after> - <why>
  readability: <before> -> <after> - <why>
  test-coverage: <before> -> <after> - <why>
  fit: <before> -> <after> - <why>
before-source: <explain step | reviewer@<base commit>>
```

- The orchestrator sets the verdict from the counts. The reviewer does not
  select it.
- If a return is in a different form (other grade words, 1 total score),
  send it back one time with this form. If the second return is also in a
  different form, the review is `unverified`. It is never `pass`. Ask the user.
- With 2 axes, put the 2 returns into 1 list and 1 score table. For each
  area, use the lower score.

## Verdict and the loop

- `pass`: `blocking=0`, and no score went down that the approved solution did not accept.
- `changes needed`: 1 blocking finding or more, or a score that went down.

On `changes needed`:

1. Record the findings and the round number.
2. On manual (`iterate`), ask: "The review found <n> blocking problems. Go
   back and fix them?" On auto, go back.
3. Mark build, test, clean, prune, and review as `redo`. Run `work-build`
   with the blocking findings as its task list.
4. The next review checks each earlier finding, then reviews the new diff.

Stop the loop and ask the user when:

- the `rounds` budget is used up (hard stop)
- a finding comes back after it was "fixed"
- a round has more blocking findings than the round before
- the findings show that the approved solution is wrong (go to the rework loop)

## End of step

Show the findings, the score table, and the verdict. Ask: "Here is the
review. Do you accept it?"

Switch: `review`. On auto, pass only if:

- the verdict is `pass`
- each `should-fix` is fixed or is under "Open items" with a reason
- no score went down
- `review-independent` is `yes`; a review in the thread that built the code
  makes this step ask

## Next

`work-ship`
