# Consolidation: detail

Part of `work-memory`. The rules in its `SKILL.md` and the `work-flow`
contract have priority.

**Consolidate** when a file is over its cap, and after each 20 runs:

1. Remove notes about code that does not exist now.
2. Remove notes that were `stale` or `unverified` for more than 90 days.
3. Merge lessons with the same cause into 1 rule. Add their `uses`.
4. Move a lesson that is now a fixed project rule to `project.md`, or
   suggest it for the instruction file.
5. If a file is still over its cap, remove the entries with the lowest
   `uses` and the oldest `last-used` first.
6. Move index lines older than the last 100 runs to `archive/index-<year>.md`.

Rules for consolidation:

- Move each removed entry to `archive/<file>-<year>.md`. Do not delete it.
- Never remove an entry with `pin`. Only the user sets `pin`. Only the user removes a preference.
- Follow the `remember` switch. On manual, show what you will merge and move,
  and ask. On auto, do it and report the counts in 1 line.
- Use the `standard` tier to merge lessons, not the `fast` tier.
- If a merge loses a detail that prevented a real failure, keep the detail.
