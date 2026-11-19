# Switches: detail

Part of the `work-flow` contract. The rules in `SKILL.md` have priority.

## Presets

| Preset | Sets |
| ------ | ---- |
| `default` | `recall`, `clean`, `prune`, `remember` auto; the others manual |
| `manual` | all manual |
| `guided` | `recall`, `assess`, `explain`, `build.branch`, `remember` auto; the others manual |
| `auto` | all auto, but not `ship` |
| `full-auto` | all auto, with `tickets` |

`tickets` is manual in `default`, `manual`, and `guided`. It is auto in
`auto` and `full-auto`. `tickets:skip` creates no issue.

`research` is manual in `default`, `manual`, and `guided`. It is auto in
`auto` and `full-auto`. `research:skip` does no outside search.

No preset sets an `env:` switch or `propose:auto(upgrade)`.

## Limits

A limit makes an auto switch narrower. Outside the limit, the step is manual.

- size: `propose:auto(size<=small)`
- task type: `clean:auto(type=bug,docs)`
- path: `build:auto(path=src/reports/**)`
- design change: `propose:auto(upgrade)`. Without it, auto asks about each
  option that changes the design.

## Other settings

- `explain:skip`: no explanation. Record the score.
- `grill:skip`: no interview. Use the acceptance criteria from `work-assess`.
- `research:skip`: no search outside the repository. `research.budget=N`:
  the searches for each call (default 8).
- `tries=N`, `rounds=N`: the loop budgets. Defaults: 3 and 2.
- `cost=cheap | balanced | best`, and `<step>.model=<tier>`: see `work-route`.

## Priority, lowest to highest

1. the defaults in this file
2. the `work-flow-defaults:` line in the instruction file
3. the preset in the user's message
4. single switches in the user's message
5. what the user says later in the run

## Examples

- `/work-flow 123`: the default preset.
- `/work-flow 123 manual`: all manual.
- `/work-flow "add CSV export to reports" guided prune:auto`
- `/work-flow 123 full-auto propose:manual`: auto, but the user selects the solution.
- `/work-flow "bump eslint to v10" auto ship.push:auto tries=5`
- `/work-flow 123 guided env:staging env:prod`: can read staging and production logs.
- `work-flow-defaults: full-auto` in the instruction file: each run is
  `full-auto` unless the user's message says a different preset.

## What the user can answer at a question

| Answer | Effect |
| ------ | ------ |
| yes | the step passes |
| a change | if it is sound, apply it in this step and ask again; if it is weaker or wrong, follow Honesty first |
| do it anyway | do it; record it under "Disagreements" |
| back to `<step>` | go back to that step; mark each later step `redo` |
| stop | pause; keep the state and the branch; continue with `resume` |
| abort | end the run; delete and revert nothing; record the run as abandoned; say what is on the branch |

Any other answer is a change request. Silence is not a yes.
