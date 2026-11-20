#!/usr/bin/env bash
# Links the skills, and installs the subagent definitions of one host, into the user's home.
# Codex does not start a subagent whose definition is a symlink, so those files are copied.
# Usage: install.sh [--agent claude|codex|kiro|agy] [--fast-model NAME] [--strong-model NAME] [--no-hooks] [--uninstall]
# claude: also adds the work-flow guard hooks to ~/.claude/settings.json (backup: settings.json.bak).
# --no-hooks skips that; --uninstall removes them.
# --fast-model and --strong-model (codex, agy): the model for the scout, and for the architect and
# reviewer. Without them each subagent uses the model of the session. No model name is kept in
# this repository, because model names change.
set -euo pipefail
src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
agent=claude
uninstall=0
copy_agents=0
hooks=1
fast_model=""
strong_model=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) agent="${2:?--agent needs a name}"; shift 2 ;;
    --fast-model) fast_model="${2:?--fast-model needs a name}"; shift 2 ;;
    --strong-model) strong_model="${2:?--strong-model needs a name}"; shift 2 ;;
    --no-hooks) hooks=0; shift ;;
    --uninstall) uninstall=1; shift ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

case "$agent" in
  claude) skills_dest="${CLAUDE_HOME:-$HOME/.claude}/skills"; agents_dest="${CLAUDE_HOME:-$HOME/.claude}/agents" ;;
  codex)  skills_dest="$HOME/.agents/skills";                 agents_dest="${CODEX_HOME:-$HOME/.codex}/agents"; copy_agents=1 ;;
  kiro)   skills_dest="$HOME/.kiro/skills";                   agents_dest="" ;;
  agy)    skills_dest="$HOME/.agents/skills";                 agents_dest="${AGY_CONFIG_DIR:-$HOME/.gemini/config}/agents"; copy_agents=1 ;;
  *) echo "unknown agent: $agent (use claude, codex, kiro, or agy)" >&2; exit 2 ;;
esac

link() { # link <source> <destination folder>
  local item="${1%/}" link
  link="$2/$(basename "$item")"
  if [[ $uninstall -eq 1 ]]; then
    if [[ -L "$link" && "$(readlink "$link")" == "$item" ]]; then rm "$link"; echo "removed $link"; fi
  elif [[ -e "$link" && ! -L "$link" ]]; then
    echo "skipped $link (a real file or folder is there)" >&2
  else
    mkdir -p "$2"; ln -sfn "$item" "$link"; echo "linked  $link"
  fi
}

copy() { # copy <source file> <destination folder>
  local item="$1" dest
  dest="$2/$(basename "$item")"
  if [[ $uninstall -eq 1 ]]; then
    if [[ -L "$dest" ]] || { [[ -f "$dest" ]] && cmp -s <(grep -vE '^(model = |model: )' "$dest") "$item"; }; then rm "$dest"; echo "removed $dest"
    elif [[ -e "$dest" ]]; then echo "kept    $dest (it differs from this repository)" >&2; fi
  else
    local model=""
    case "$(basename "$item")" in
      flow-scout.*) model="$fast_model" ;;
      flow-architect.*|flow-reviewer.*) model="$strong_model" ;;
    esac
    mkdir -p "$2"; rm -f "$dest"
    if [[ -n "$model" ]]; then
      if [[ ! "$model" =~ ^[A-Za-z0-9._:/-]+$ ]]; then echo "invalid model name: $model" >&2; exit 2; fi
      if [[ "$dest" == *.md ]]; then
        awk -v m="$model" '{print} /^name: /{print "model: " m}' "$item" > "$dest"
      else
        awk -v m="$model" '{print} /^name = /{print "model = \"" m "\""}' "$item" > "$dest"
      fi
      echo "copied  $dest (model: $model)"
    else
      cp "$item" "$dest"; echo "copied  $dest"
    fi
  fi
}

for item in "$src"/skills/*/; do link "$item" "$skills_dest"; done

if [[ -n "$agents_dest" && -d "$src/adapters/$agent/agents" ]]; then
  for item in "$src/adapters/$agent/agents"/*; do
    if [[ $copy_agents -eq 1 ]]; then copy "$item" "$agents_dest"; else link "$item" "$agents_dest"; fi
  done
  if [[ $copy_agents -eq 1 && $uninstall -eq 0 ]]; then
    echo "note: the $agent subagent files are copies. Run this command again after an update." >&2
  fi
elif [[ $uninstall -eq 0 ]]; then
  echo "note: no subagent definitions for $agent. work-flow runs in one thread:" >&2
  echo "      no model routing, and the review of medium or large work needs a new thread." >&2
fi

if [[ "$agent" == claude ]]; then
  hook_installer="$src/adapters/claude/hooks/install_hooks.py"
  if [[ $uninstall -eq 1 ]]; then
    if command -v python3 >/dev/null; then python3 -I "$hook_installer" uninstall; fi
  elif [[ $hooks -eq 1 ]]; then
    if command -v python3 >/dev/null; then python3 -I "$hook_installer" install
    else echo "note: python3 not found; the work-flow guard hooks were not installed." >&2; fi
  fi
fi

if [[ "$agent" == claude && $uninstall -eq 0 ]]; then
  echo "note: the skills read their reference/ files at run time. If the host blocks those reads," >&2
  echo "      add the clone to permissions.additionalDirectories in ~/.claude/settings.json:" >&2
  echo "      \"$src\" (the realpath of ~/.claude/skills/work-flow is inside it)," >&2
  echo "      and read the reference files through the clone path." >&2
fi
