# Templates

Part of `engineering-standards`. Copy a template, fill it, and delete each
line that does not apply.

## Commit

```
fix(auth): reject expired refresh tokens on session renewal

The renewal endpoint compared the token expiry as a string, not as a
date, so an expired token could sort as later and be accepted. A refresh
token issued before the last deploy could renew a session with no limit.

Fixes #123
```

Short form, when the subject says it all:

```
fix(api): return 404 instead of 500 for a missing resource
```

## Pull request

A repository can keep this as `.github/PULL_REQUEST_TEMPLATE.md`.

```markdown
## Summary
- <what changed and why, 1 bullet for each logical change>
- <for a bug: the symptom and the cause>
- <what the diff does not show: migration, config, deploy order, follow-up>

## Test plan
- [ ] <exact steps or commands, and what they showed>

## Tradeoffs
- <what this change costs, what it does not solve, and the option that was not taken>

Fixes #<n>
```

Example:

```markdown
## Summary
- Stop session renewal from accepting expired refresh tokens
- Cause: `isTokenExpired()` compared `expiresAt` as a string, so a date
  that sorted later as text was treated as not expired
- No data migration; existing sessions expire normally

## Test plan
- [x] Reproduced with a token whose expiry sorted wrongly as a string;
      renewal was accepted before the fix
- [x] Added a unit test for the date comparison
- [x] Renewal rejects an expired token after the fix

## Tradeoffs
- Tokens issued in the old format are parsed on each renewal, which adds
  one parse; a backfill of stored tokens was not done

Fixes #123
```

## Issue

```markdown
## Summary
- <the symptom or the request, 1 bullet for each>
- [ ] <each separate cause, when there is more than 1>

## Repro
- <a link, exact steps, or example input>
- <expected and actual; a table when there is more than 1 example>

## Root cause
- TBD until it is diagnosed

## Notes
- <related issues and PRs, earlier work, what is not obvious>
```
