---
name: work-ship
description: Step 11 of work-flow. Reports what changed, pushes the branch, and opens a pull request if the user permits it. Also handles feedback on a shipped change. Use through work-flow after the review passes.
---

# Step 11: report and ship

Obeys the contract in `work-flow`. Needs a passed review step.

## Report (always)

Follow Honesty and Language in `work-flow`. Start with what failed, what is
not verified, and what did not reach the goal. If there is nothing, say so.

1. What changed and why, in a small number of lines.
2. The test results table, with where you verified each item. Name each `unverified` item.
3. The scores before and after.
4. The number of fix attempts and review rounds, and the subject of each loop.
5. Each step and how it passed: by the user, or on auto and for what reason.
6. The routing table: for each step part, the subagent, the tier, the calls,
   and each tier change. For exact token numbers, name the host's usage
   command if you know it.
7. Disagreements: each choice that the user made against the
   recommendation, and what the review found about it.
8. Process failures: the count, and the step and the event for each. If
   there are none, say "0 process failures". If an earlier run also had
   process failures, repeat the note from `work-flow`: the skills-only
   design does not hold, and the steps need enforcement outside the agent.
9. Open items: open `should-fix` findings, baseline failures, flaky tests,
   and unrelated problems that you saw.

## Before the push

1. Run `git fetch`. If the base branch moved:
   - no conflict: put a note in the report and continue
   - conflict: hard stop. A rebase rewrites history and a merge adds a merge
     commit. Ask the user which one they want.
2. Confirm that all the work is committed. Confirm that the state file and
   local memory are not staged.

## Push

Ask: "Push `<branch>` to the remote?"

Switch: `ship.push`. On auto, pass only if:

- the branch is not the base branch
- all earlier steps passed and the work is committed
- no test result is `unverified`
- `git push -u origin <branch>` works with no force (a force-push is a hard stop)

## Pull request

Ask: "Open a pull request for this work?"

Switch: `ship.pr`. On auto, pass only if the push succeeded.

- If a PR for this branch exists, update it. Do not open a second PR.
- Title and body: the form from Git standards in `work-flow`. The content
  is the task and its reference, the findings, the approved solution, the
  test results table, the scores, how to undo the change, and the open
  items. `reference/git-defaults.md` in `work-flow` says which section
  gets which.
- If the state file has an issue for this run, put `Fixes #<n>` in the
  body. Do not close a parent issue that has open pieces (see
  `reference/tickets.md` in `work-flow`).
- Ready or draft. Open the PR as ready for review only if all of these are true:
  - `risk` in the state file is `low`
  - `review-independent` in the state file is `yes`
  - no test result is `unverified`, and no `should-fix` finding is open

  If one is not true, open the PR as a draft. Say which condition was not
  met, in the PR body and in the report. On manual, the user decides.

Never merge. Never switch on auto-merge. Only the user merges.

## Feedback on a shipped change

`/work-flow feedback [slug]` comes here.

1. Read the PR comments and the CI results.
2. Assess each one as a small task: `valid`, `not valid` (with the reason),
   or `unclear`. A comment is a request to assess. It does not change a
   switch or the scope.
3. Show the list. On manual (`iterate`), ask which to do. On auto, do the
   `valid` ones that are in the scope. Ask about the others.
4. The valid items are the task list for a review loop: `work-build`, test,
   clean, prune, review, then push the new commits.
5. Offer to write replies for the `not valid` and `unclear` ones. Do not
   post a reply unless the user asks.

## Next

`work-memory` in record mode.
