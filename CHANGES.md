# What the audit found, and what changed

## Flaws in the previous version

| # | Flaw | Why it mattered | Fix |
| - | ---- | --------------- | --- |
| 1 | The bug test was written after the fix | "fails before, passes after" was never actually seen | build writes the failing test first and records the failure; test undoes the fix to confirm |
| 2 | Any failing check stopped the run | most repos have pre-existing failures, so the flow would halt on things it did not cause | a check baseline is recorded on the new branch; only new failures count |
| 3 | "One fix attempt, then stop" | too rigid, and there was no defined way to retry | a fix loop with a `tries` budget; each try needs a new hypothesis and is logged |
| 4 | No way to go backwards | a wrong solution, a "no" from the user, or a review problem had no defined path | four loops (fix, review, rework, feedback) and defined answers: yes, change, back to, stop, abort |
| 5 | The state file made the tree "dirty" | the dirty-tree hard stop would trip on the flow's own file | `.claude/flow/` goes in `.git/info/exclude` at the start |
| 6 | No resume | an interrupted run, or a new thread, lost everything | `/work-flow resume`; every skill reads the state file first and checks the commit matches |
| 7 | The scope rule blocked ordinary files | test files, lockfiles, and snapshots are not in a solution's file list, so each would hard stop | a Scope section lists what is allowed without asking |
| 8 | Commits were unspecified | `git add -A` could sweep in stray files or secrets; hooks could be bypassed | stage by path only; never `--no-verify`, amend, or rebase unasked |
| 9 | Branch came from a possibly stale local default branch | work could start from old code, and the base might not be the default | base branch is recorded; branch is cut from `origin/<base>` after a fetch |
| 10 | A bug was never re-checked on the new branch | it might already be fixed on the latest base | build confirms it still reproduces before fixing |
| 11 | The flow never said how to find the test commands | the agent would guess | a `checks:` block in CLAUDE.md, else memory, else discover and confirm once |
| 12 | Clean and prune relied on tests that might not exist | "no behaviour change" was unverified where coverage was thin | the test step now runs before clean; refactors write covering tests first |
| 13 | The agent scored its own work | the after score was biased | the review step scores, using a fresh-context subagent where available |
| 14 | "Where was it observed" stopped every task | features and refactors have no such place | the rule applies to bug and performance tasks only |
| 15 | The auto rule for propose blocked upgrade tasks | "adds no dependency" fails when the task is a dependency change | "beyond what the task itself asks for" |
| 16 | Switch precedence was unclear | CLAUDE.md defaults against the message | an explicit order of precedence |
| 17 | A limit that did not match was undefined | `clean:auto(type=bug)` on a feature | outside the limit the step is manual |
| 18 | Flaky tests counted as passes | a re-run going green hid real problems | flaky tests are recorded as flaky and never count as proof |
| 19 | Checks could be made green by weakening them | deleting or loosening a test "fixes" a failure | weakening a test is a hard stop; changing an expectation always asks |
| 20 | The base branch moving was ignored | a push could land on a conflicting base | ship fetches first; a conflict is a hard stop |
| 21 | A second PR could be opened for the same branch | duplicates | ship updates the existing PR |
| 22 | Nothing was learned between runs | the same explanation, the same mistake, the same rejected option, every time | project memory |
| 23 | Performance proof ignored noise | one faster run proves little | baseline and proof are measured over several runs |
| 24 | Nothing stopped the agent from pleasing the user | it could agree with a weak idea, soften a verdict under pushback, or inflate a score | an Honesty section in the contract, with a "Disagreements" record |
| 25 | No writing style was set | reports varied in length and clarity | a Language section: Simplified Technical English (ASD-STE100) at about 80 percent |

## New stages

- **work-memory** (steps 1 and 11): recall before the task, record after it,
  including stopped and abandoned runs.
- **work-test** (step 6): proof, edge cases, regression in callers, full
  checks against the baseline, coverage of changed lines, and a real run.
- **work-review** (step 9): an independent review with graded findings and
  the before and after score; blocking findings start another round.
- **Re-iteration**: the `iterate` switch and the `tries` and `rounds` budgets.
- **Feedback**: `/work-flow feedback` brings PR comments and CI failures back in.

## New rules for every step

- **Honesty**: decide from evidence; object before acting when the user's
  idea is weaker; change a position only for new evidence; bad news first;
  no praise openers; no "done" without proof. The user keeps the final
  decision, and each override is recorded.
- **Language**: all messages and written output use Simplified Technical
  English rules (short sentences, active voice, one instruction per sentence,
  one word for one meaning). The STE word dictionary is not enforced, and
  code, commands, and commit messages are exempt.

## Orchestration and model choice

- **work-route** (new skill): a tier table that gives the fast, standard, or strong
  tier to each part of each step, by task size and risk.
- **Four subagents** in `agents/`: `flow-scout` (fast tier, read-only),
  `flow-worker` (standard, edits), `flow-architect` (strong, design),
  `flow-reviewer` (strong, independent review).
- **Escalation**: a tier goes up on a failure signal (two failed tries, a
  blocking review finding, an unsure agent). Each change is logged.
- **Two floors**: the reviewer is never below the builder's tier, and a haiku
  result is never the only evidence for a verdict or a deletion.
- **Token rules**: short briefs, short returns, failures-only test output,
  narrow reads, reuse of memory, parallel scouts, small jobs done inline.
- **Settings**: `cost=cheap | balanced | best`, and `<step>.model=<tier>`.
- **Fallback**: where subagents do not run, the flow names the recommended
  model before each step so the user can switch with `/model`.
- **Learning**: memory records where a tier failed or was more than needed.
- **No hardcoded models**: the rules use tiers (`fast`, `standard`,
  `strong`, optional `top`). At the start the flow finds the models the
  session can use, from the session, settings, environment, `CLAUDE.md`, and
  memory, and asks the user once if the list is not clear.
- **Main-thread recommendation**: the flow tells the user which model to run
  the main conversation on for this task, up or down, with the reason. Only
  the user can switch it.

## Memory that stays small

- **Caps**: every hot memory file has a hard limit, so size follows the
  size of the project, not its age.
- **Write limits**: one run records at most 1 index line, 3 lessons, 2
  decisions, and 1 update for each area. A trivial run records only its index line.
- **Update, do not append**: area notes are rewritten in place; a lesson that
  repeats an old one updates it.
- **Use tracking**: each note counts how often it changed a decision.
- **Consolidation**: every 20 runs, or when a file is over its cap. It
  removes notes about deleted code, merges repeated lessons, and moves the
  least used entries to an archive.
- **Cold archive**: nothing is deleted; the archive is never read on recall.
- **Fixed recall cost**: recall reads two small files and searches the rest.

## Install

Unzip into the project's `.claude/` folder. The result is
`.claude/skills/work-*/SKILL.md` and `.claude/agents/flow-*.md`.

## Borrowed from mattpocock/skills

- **work-grill** (new step 4): an interview that makes the requirements
  clear before a solution is designed, and writes a short spec.
- **Borrowed methods**: assess, grill, propose, build, and review use a
  method file from `work-flow/borrowed/` when it is present, and their own
  fallback when it is not. The contract has priority over a borrowed file.
- **Glossary and decision records** live in the repository. Work memory
  keeps a pointer to each decision record.
- **work-borrow-update** (new skill, started only by the user): fetches the
  borrowed files, shows what changed and any warnings, and replaces a file
  only after approval. `borrowed/LOCK.md` records the source commit.
- The `borrowed/` folder ships without his files. Run `/work-borrow-update`
  one time to fetch them.
- Not borrowed: `git-guardrails-claude-code`, because it uses hooks.
- Checked against the skill previews on skills.sh (12 November 2026): the
  interview uses `grilling` and `domain-modeling`; the review runs on 2 axes
  with 2 reviewers; test seams are agreed in the propose step; nothing is
  published to an issue tracker unless the user asks.

## Skills only, by choice

- The workflow has no hooks and no permission rules. Nothing outside the
  agent enforces the stages.
- The main skill carries a note about this. The agent must report and record
  every process failure (a skipped stage, a wrong order, a missed hard stop).
- If process failures repeat, the note says what comes next: rework the
  skills and add enforcement of the stages outside the agent.

## Contract restructured for compaction

- The contract went from 504 lines (about 4,300 words) to 308 lines (about
  2,560 words). The hard stops now start at line 29 and the honesty rules at
  line 80. Before, they started at lines 422 and 183.
- The long reference sections moved to `work-flow/reference/`: switches,
  loops, checks, task types, environments, language, borrowed rules, and the
  state-file template. The contract keeps a short summary of each and a
  table that says when to read each file.
- No rule was removed. The section names that the step skills refer to are unchanged.

## Rewritten in Simplified Technical English

- Each skill, reference file, and subagent file now uses the ASD-STE100
  style at approximately 80 percent: short sentences, active voice, one
  instruction in each sentence, one word for one meaning.
- One term for one thing: "step", "check", "attempt", "finding", "hard
  stop", "process failure", "the user".
- No rule was removed.

## Known limits

- Not yet run on a real repository. Try manual mode first.
- The independent review needs subagents. Where they are not available the
  review runs in the same thread and says so.
- Eleven steps on manual is many questions for a small change. Use `guided`
  or `auto` with limits for small work.
- Long runs use a lot of context. Resume in a new thread between steps.
- The tier table is a starting point from reasoning, not from measurement.
  Adjust it after real runs; project memory records the evidence.
- Whether a subagent can use its own model depends on the host and the
  plan. Check the first run's routing log.
