#!/usr/bin/env bash
# Links the skills, and installs the subagent definitions of one host, into the user's home.
# Codex does not start a subagent whose definition is a symlink, so those files are copied.
# Usage: install.sh [--agent claude|codex|kiro] [--uninstall]
set -euo pipefail
src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
agent=claude
uninstall=0
copy_agents=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) agent="${2:?--agent needs a name}"; shift 2 ;;
    --uninstall) uninstall=1; shift ;;
    -h|--help) sed -n '2,3p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

case "$agent" in
  claude) skills_dest="${CLAUDE_HOME:-$HOME/.claude}/skills"; agents_dest="${CLAUDE_HOME:-$HOME/.claude}/agents" ;;
  codex)  skills_dest="$HOME/.agents/skills";                 agents_dest="${CODEX_HOME:-$HOME/.codex}/agents"; copy_agents=1 ;;
  kiro)   skills_dest="$HOME/.kiro/skills";                   agents_dest="" ;;
  *) echo "unknown agent: $agent (use claude, codex, or kiro)" >&2; exit 2 ;;
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
    if [[ -L "$dest" ]] || { [[ -f "$dest" ]] && cmp -s "$item" "$dest"; }; then rm "$dest"; echo "removed $dest"
    elif [[ -e "$dest" ]]; then echo "kept    $dest (it differs from this repository)" >&2; fi
  else
    mkdir -p "$2"; rm -f "$dest"; cp "$item" "$dest"; echo "copied  $dest"
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
