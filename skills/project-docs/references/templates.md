# Templates

Part of `project-docs`. Remove each line that has nothing true to say.

## docs/README.md

```markdown
# <system name>

<What it does and for whom, in 2 or 3 sentences.>

## Run it
- Install: `<command>`
- Start: `<command>`
- Test: `<command>`
- Configuration: `<file or the list of required variables, no values>`

## Where things are
- `<folder>`: <what lives there>

## More
- [Architecture](architecture.md) · [Runbooks](runbooks.md) · [Glossary](glossary.md) · [Decisions](decisions/)
```

## docs/architecture.md

```markdown
# Architecture

## Main parts
- **<part>** (`<path>`): <its one job>

## Data flow
<input> → <part> → <part> → <store or output>

## External systems
- **<system>**: <what it is used for> (`<where the client code is>`)

## Limits that shape the design
- <a constraint and its consequence>
```

## docs/decisions/NNNN-<slug>.md

```markdown
# NNNN: <decision in one line>

Date: YYYY-MM-DD · Replaces: <NNNN or none>

## Context
<The problem and the constraint, in a few sentences.>

## Decision
<What was chosen.>

## Rejected
- <option>: <why not>

## Consequences
- <what is now easier, and what is now harder>
```

## docs/runbooks.md

```markdown
# Runbooks

## Deploy
1. `<command>`: <what it does>

## Roll back
1. `<command>`

## Incident
1. Where to look first: `<logs or dashboard command>`
2. Who to tell: <role>
```

## docs/glossary.md

```markdown
# Glossary

- **<term>**: <its one meaning>. Not: <a meaning it does not have>.
```
