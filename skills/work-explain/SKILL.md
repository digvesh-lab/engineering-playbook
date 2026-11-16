---
name: work-explain
description: Step 3 of work-flow. Asks whether the user knows the part of the system that the task touches, explains it with a flowchart, a worked example, or the theory, and gives the current code a score. Use through work-flow, or directly to get an explanation and a score for a feature.
---

# Step 3: explain the system and give a score

Obeys the contract in `work-flow`. Read only.

## Do

1. If the state file has a valid area note from memory, start from it and update it.
2. On manual, ask:

   > Do you know how this part of the system works, or do I explain it first?
   > I can use a flowchart, a worked example, the theory, or a mix.

   If memory shows that the user saw this explanation before, say when. Ask
   whether the user wants all of it or only the changes.
3. Give the forms that the user selected:
   - **Flowchart**: a Mermaid diagram of the real code path, with file names on the nodes.
   - **Worked example**: follow one real input through the code, step by step.
   - **Theory**: the concept behind the design and the reason for it.
4. Always give a score from 1 to 10 for each area. Each reason must point to
   something that can be checked: a `file:line`, a missing test, a measurement.

   | Area | Score | Why |
   | --- | --- | --- |
   | Correctness | | |
   | Readability | | |
   | Test coverage | | |
   | Fit with the design | | |

5. Write the explanation and the scores to the state file. `work-review`
   compares against these scores.

## End of step

Ask: "Is that clear, or do I explain a part in more detail?" Continue until
the user says that they are ready.

Switch: `explain`.

- `explain:auto`: do not ask. Write a flowchart, a short theory note, and
  the scores to the state file. Tell the user in 1 line where they are.
- `explain:skip`: do not ask and do not explain. Record the scores.

## Later in the run

If a later step goes into a part of the system that this step did not
cover, come back to this skill for that part. On manual, ask again. On
auto, add to the state file.

## Next

`work-grill`
