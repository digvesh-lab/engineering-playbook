---
name: work-propose
description: Step 5 of work-flow. Proposes 1 to 3 solutions that fit the system design or upgrade it, and gets one approved by the user. Use through work-flow after the task is assessed, and again when a solution must be reworked.
---

# Step 5: propose solutions

Obeys the contract in `work-flow`. Read only: do not edit a file before the
user approves a solution.

## Do

1. Read the decisions and lessons from memory. You can offer a rejected
   option again only if you say that it was rejected, why, and what changed.
2. On a rework: start with what the failed attempt showed. Do not offer the
   same approach with no change.
3. If the problem is common and the code does not show how to solve it,
   call `work-research` for prior art before you design the options.
   Cite each finding that an option uses, with its label.
4. Design each option against the "Requirements" in the state file.
5. Offer 1 to 3 options. Label each:
   - **Aligned**: fits the current design. Uses existing patterns, helpers, and conventions.
   - **Upgrade**: makes the design better. Say what changes, why it is
     better, and the cost of the migration.
6. For each option give:
   - a summary
   - the exact file list, with test files
   - the risks, and what can break in other places (callers, data, public API)
   - the test plan: the proof for the task type, the edge cases, and the test
     seams (where the tests meet the code). Each acceptance criterion needs
     a test. Prefer existing seams, at the highest level, and as few as possible.
   - how to undo it after a merge
   - the size: `small` (1 or 2 files), `medium` (3 to 6), `large` (more)
7. Call `work-prototype` if the options differ in one of these:
   - the screens, the layout, or the user flow
   - a state model that is hard to judge on paper

   Use the variant that the user chose in the recommendation.
8. Measure each data rule. A rule that classifies, matches, merges, or
   skips records must be run against the data before it is an option or an
   acceptance criterion. Give the count of records it hits and the cases
   that break it. If the data cannot be read in this step, label the rule
   `unverified` and make the measurement the first build task.
9. Recommend one option. Give the reason. The recommendation is the option
   that is best for the code. It is not the smallest option or the option
   that the user named first.
10. For a `large` option, say whether it can be split. If
   `borrowed/to-tickets.md` exists in the `work-flow` folder, use its method
   for the split. Write the pieces and what blocks what to the state file.
   Publish nothing in this part.
11. Write all the options to the state file.

## End of step

Ask: "Which option? You can also change one, combine them, or suggest your own."

If the user suggests an approach, or selects an option that you did not
recommend: check it against the code. Follow Honesty in `work-flow`. If it
is as good or better, say so and use it. If it is weaker, give the evidence
and the cost, and ask one time. Do not agree first and find the problems
later. Wait for a clear decision.

Switch: `propose`.

- `propose:auto`: pass only if:
  - `risk` in the state file is `low`
  - the recommended option is Aligned
  - it adds no dependency and does not change a public API, a schema, or a
    config format, unless the task asks for that
  - it is in the size limit of the switch (default `size<=medium`)
  - it was not rejected in an earlier run
- `propose:auto(upgrade)`: pass also for a recommended Upgrade option. Only
  the user sets this. Without it, auto asks about each Upgrade option.

On auto, tell the user in 1 line which option you took and why.

## Output

Record in the state file: the approved solution, its file list, its test
plan, and its `size`.

- The file list is the scope for build, test, clean, and prune (see Scope in `work-flow`).
- `work-route` uses the size and the risk to set the model tiers.
- If the approved option changes the design, or you rejected an option for a
  reason that will stay important, write a decision record (see
  `work-memory`).

## Tickets

Do this after a solution is approved. Read `reference/tickets.md` in the
`work-flow` skill folder and follow it.

Ask: "Create a GitHub issue for this work?"

Switch: `tickets`. On auto, pass only if each auto condition in
`reference/tickets.md` is met. `tickets:skip` creates no issue.

If the approved solution is split into pieces, this run builds only the
first piece that nothing blocks. Make the file list of that piece the scope.
Tell the user which pieces stay open.

## Next

`work-build`
