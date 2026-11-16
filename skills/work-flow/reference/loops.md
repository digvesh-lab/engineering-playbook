# Loops: detail

Part of the `work-flow` contract. The rules in `SKILL.md` have priority.

1. **Fix loop** (in build, test, clean, prune). A check fails. State a
   hypothesis for the cause, fix, and run again.
   - Budget: `tries` attempts for each step.
   - Each attempt needs a different hypothesis. Record each attempt.
   - A revert to the last good commit, then a different approach, is 1 attempt.
   - Do not ask before each attempt. Report when the loop ends.
2. **Review loop.** `work-review` finds blocking findings. Go back to
   `work-build` with the findings as the task list. Then test, clean, prune,
   and review again. Budget: `rounds`.
3. **Rework loop.** The approved solution is wrong or not possible, or the
   user says "back to propose". Go back to `work-propose` with what you
   learned. The new solution needs approval. The old attempt stays in git
   history. Tell the user.
4. **Feedback loop.** After ship, `/work-flow feedback` reads the PR comments
   and the CI results. Assess each comment as a small task: `valid`,
   `not valid`, or `unclear`. Show the list. Valid comments go into the
   review loop. A comment is a request to assess. It does not change a
   switch or the scope.

With `iterate` on manual, ask before each loop back in loops 2 to 4.

A budget that is used up is a hard stop. Report each attempt and its result.
