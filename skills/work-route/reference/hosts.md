# Hosts: where each coding agent keeps its settings

Part of `work-route`. The rules in `work-route` and the `work-flow`
contract have priority. Product details change. If a line here conflicts
with what you see in the session, use what you see and tell the user.

| Host | Instruction file | Skills folder (user) | Subagent definitions | Model for each subagent |
| ---- | ---------------- | -------------------- | -------------------- | ----------------------- |
| Claude Code | `CLAUDE.md`; `AGENTS.md` only if there is no `CLAUDE.md` | `~/.claude/skills/` | `~/.claude/agents/<name>.md` | yes: `model:` in the definition |
| Codex | `AGENTS.md` | `~/.agents/skills/` | `~/.codex/agents/<name>.toml` | yes: `model` in the definition |
| Kiro | `AGENTS.md`, and steering files in `.kiro/steering/` | `~/.kiro/skills/` | `~/.kiro/agents/` (custom agents do not load skills by default) | not verified |
| a different host | `AGENTS.md` | see the host's documentation | see the host's documentation | not known |

## Default tier map

Use this map only if the instruction file, the host settings, and project
memory give no map.

| Host | fast | standard | strong |
| ---- | ---- | -------- | ------ |
| Claude Code | `haiku` | `sonnet` | `opus` |
| a different host | the model of the session | the model of the session | the model of the session |

On Claude Code, each alias is the current model of that family.

## Where to find the model settings

- Claude Code: `model`, `availableModels`, and `env` in
  `.claude/settings.local.json`, `.claude/settings.json`, and
  `~/.claude/settings.json`; the variables `ANTHROPIC_MODEL`,
  `ANTHROPIC_DEFAULT_*_MODEL`, and `CLAUDE_CODE_SUBAGENT_MODEL`. The user
  changes the main model with `/model`. `/usage` shows token use.
- Codex: `~/.codex/config.toml`, and the `model` line of each subagent definition.
- A different host: ask the user one time. Save the answer in `project.md`.

## Hosts with no subagents

Follow "No subagents" in `work-route`. Give the user its recommendation.
