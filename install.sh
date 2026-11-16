#!/usr/bin/env bash
# Links every skill and agent in this folder into ~/.claude. Use --uninstall to remove the links.
set -euo pipefail
src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="${CLAUDE_HOME:-$HOME/.claude}"
mkdir -p "$dest/skills" "$dest/agents"
for item in "$src"/skills/*/ "$src"/agents/*.md; do
  item="${item%/}"
  link="$dest/$(basename "$(dirname "$item")")/$(basename "$item")"
  if [[ "${1:-}" == "--uninstall" ]]; then
    [[ -L "$link" && "$(readlink "$link")" == "$item" ]] && rm "$link" && echo "removed $link"
  elif [[ -e "$link" && ! -L "$link" ]]; then
    echo "skipped $link (a real file or folder is there)" >&2
  else
    ln -sfn "$item" "$link" && echo "linked  $link"
  fi
done
