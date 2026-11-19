---
name: work-prototype
description: Prototype helper for work-flow. Shows the solution options before the user selects one: a Mermaid flowchart of the user flow, HTML UI variants to compare, or a clickable demo of a state model. Use through work-propose when the options differ in what the user sees. Use directly with /work-prototype <question>.
---

# Prototype the options

Obeys the contract in `work-flow`. Change no code of the project. Write only
to the state file and to the prototype folder of the run.

This is not a numbered step. `work-propose` calls it after it designs the
options and before it recommends one. The user can also call it directly:
`/work-prototype <question>`.

## When to prototype

Prototype only when the options differ in a way that the user must see to
judge. The triggers:

- the options give different screens, layouts, or user flows
- a state model or a rule has cases that are hard to judge on paper
- the user asks for options to see, or for inspiration

Do not prototype when the options differ only in the code. Do not
prototype when a design, a ticket, or an existing pattern sets the UI.

## Pick the shape

Write the question in 1 sentence. The question decides the shape:

| Question | Shape |
| -------- | ----- |
| "Which path does the user take?" | flowchart |
| "What should this look like?" | UI variants |
| "Does this logic or state model feel right?" | logic demo |

A UI task often needs the flowchart and the variants.

## Flowchart

Write a Mermaid flowchart in the state file under "Prototype":

- a rectangle for each screen, a diamond for each decision, a label on each
  arrow for the user action
- include the error, empty, loading, and no-permission paths
- 1 chart for each option if the flows differ; 1 chart if they are the same

## UI variants and logic demo

Use the method in `borrowed/prototype.md` of the `work-flow` folder, with
its supporting files in `borrowed/prototype/` (`UI.md` and `LOGIC.md`). If
the file is not there, say so in 1 line and use the rules below only.

These rules have priority over the borrowed file:

- **Standalone files only.** Each prototype is 1 self-contained HTML file in
  `.agents/work-flow/runs/<slug>.prototype/`. It opens with a double-click,
  with no server, no install, and no CDN. Do not add a route, a component,
  or a script to the project. Do not edit `package.json`.
- **Native look.** Copy the colours, fonts, and spacing of the real screen
  into the file. Copy its header and navigation too. Each variant must
  look like a part of the product.
- **Fake data only.** Use realistic but invented names and numbers. Never
  copy rows from a database or a log into a prototype.
- **Real variants.** Default 3, at most 5. Each variant differs on 1 named
  axis: layout, density, information hierarchy, interaction model, or flow.
  Write the axis in the variant's label. If possible, make 1 variant for
  each option of `work-propose`.
- **No commit, no branch, no issue.** Ignore these borrowed rules:
  - commit the prototype to a branch
  - put a link on an issue
  - move a variant into the real code

  Git ignores the folder, as it ignores the state file.
- In-app variants (the borrowed "sub-shape A") are not part of this skill.
  If the user wants one, it becomes a build task of the approved solution.

## Output

Write to the state file under "Prototype". Add 1 block for each call:

```
question:
asked-by: work-propose | user
shape: flowchart | ui variants | logic demo
files: <each path, and how to open it>
variants: <key - axis - the option it shows>
chosen: <key, combination, or "none yet"> (<user | agent, not seen by the user>)
settled: <what the choice decided, in 1 or 2 sentences>
```

## End of the call

Switch: `prototype`.

- On manual: give the paths and ask "Which variant? You can also combine them."
- On auto, continue only if each condition is met:
  - you recorded the question and the shape
  - each variant names its axis
  - each file opens offline
  - you wrote nothing outside the prototype folder and the state file

  If each condition is met, recommend 1 variant. Record it as `agent, not
  seen by the user`. The `propose` switch decides the option.
- `prototype:skip`: make no prototype. Where a trigger applied, record
  "prototype skipped" in the state file.

When the run ends, the folder stays with the state file. Delete it only if
the user asks.

## Next

Return to `work-propose`. The chosen variant and what it settled become part
of the recommended option.
