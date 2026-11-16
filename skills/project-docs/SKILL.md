---
name: project-docs
description: A minimal docs folder for a software repository, for agents and people - what the system is, its architecture on one page, decisions, runbooks, and a glossary. Use when a repository has no docs or too many, when the user asks to create, shorten, or audit project docs, and after a change to a decision, a run step, or a domain term.
---

# Project docs

Write down only what the code cannot tell you. The code, and a code graph
made from it, say what exists and what calls what. Docs say why, how to
operate the system, and what the terms mean.

## The folder

```
docs/
  README.md        what the system is, how to run it, where things are
  architecture.md  one page: the main parts, the data flow, the external systems
  decisions/       one short file for each decision; never rewritten
  runbooks.md      deploy, rollback, and incident steps
  glossary.md      each domain term and its one meaning
```

Nothing else, unless the user asks. Templates: `references/templates.md`.

## Rules

- **If the repository has docs in a different layout, use that layout.**
  Do not move or delete existing docs unless the user asks.
- **One page stays one page.** `README.md` and `architecture.md` have a
  limit of about 100 lines each. If a page grows past it, cut it. Do not
  split it into more pages.
- **Do not copy the code.** No list of endpoints, routes, tables, fields,
  files, or functions. Point to the place in the code:
  `src/auth/` or `package.json` scripts.
- **Each fact has a source.** Give the path or the command that proves it.
  If you cannot verify a fact, leave it out.
- **A decision record is never rewritten.** A new decision gets a new file
  that names the old one.
- **No placeholder text.** A section with nothing true to say is removed.

## When to update

Update the docs in the same branch as the change, and only if the change
does one of these:

| The change | Update |
| ---------- | ------ |
| adds, removes, or replaces a main part or an external system | `architecture.md` |
| takes a design decision, or reverses one | a new file in `decisions/` |
| changes how to run, deploy, roll back, or configure | `README.md` or `runbooks.md` |
| adds a domain term, or changes its meaning | `glossary.md` |

A bug fix, a refactor inside one part, a new endpoint, or a new field
needs no docs change.

## Structure comes from the code, not from docs

To find what exists, what depends on what, and what a change touches, read
the code. A code graph makes this cheap. Recommended:
[graphify](https://github.com/Graphify-Labs/graphify), which builds the graph
from the code with no model cost and updates it after each change. If the
repository has a graph, query it before you search or read files. If it
has none, search and read the code. Keep generated graph output out of git.

## Create the docs

1. Read what exists: the README, the instruction file (`AGENTS.md` or
   `CLAUDE.md`), the manifest and its scripts, the CI config, the deploy
   config, and the top-level folders.
2. Write the 4 files from the templates, from verified facts only.
3. Create `decisions/` only when there is a first decision to record. Do
   not invent past decisions. Ask the user for the ones that matter.
4. Show the user what you could not verify, as a short list of questions.

## Shorten docs that are too long

Only when the user asks. For each page: keep what is why, how to operate,
or a term; delete what repeats the code; move the rest into the 5 items.
Show the list of pages to delete before you delete one.
