#!/usr/bin/env python3
"""Check skills against the playbook rules. Usage: check.py <skills folder> [skill ...]"""
import re
import sys
from pathlib import Path

PRODUCTS = r"\b(Claude|Codex|Gemini|Antigravity|Cursor|Copilot|Opus|Sonnet|Haiku|GPT-?\d*)\b"
MAX_LINES = 200
MAX_WORDS = 25


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fields = dict(re.findall(r"^([\w-]+):\s*(.*)$", m.group(1), re.M))
    return fields, text[m.end():]


def long_sentences(body):
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    body = re.sub(r"`[^`]*`", "X", body)
    body = re.sub(r"\n[ \t]+(?=[^\s-])", " ", body)
    for line in body.splitlines():
        if line.startswith(("|", "#")):
            continue
        for s in re.split(r"(?<=[.!?:])\s+", line.lstrip("-* 0123456789.")):
            if len(s.split()) > MAX_WORDS:
                yield s


def check(folder):
    errors, warnings = [], []
    f = folder / "SKILL.md"
    if not f.exists():
        return ["no SKILL.md"], []
    text = f.read_text()
    fields, body = frontmatter(text)
    if fields is None:
        return ["no frontmatter"], []
    if fields.get("name") != folder.name:
        errors.append(f"name '{fields.get('name')}' is not the folder name")
    extra = set(fields) - {"name", "description", "disable-model-invocation"}
    if extra:
        errors.append(f"frontmatter has extra fields: {sorted(extra)}")
    desc = fields.get("description", "")
    user_only = fields.get("disable-model-invocation") == "true"
    if not desc:
        errors.append("no description")
    elif not user_only and not re.search(r"\b(Use|Read by)\b", desc):
        errors.append("description has no trigger ('Use ...' or 'Read by ...')")
    if folder.name.startswith("work-") and folder.name != "work-flow" and not user_only:
        if not re.search(r"^Obeys the contract in `work-flow`\.", body, re.M):
            errors.append("no 'Obeys the contract in `work-flow`.' line")
    if re.search(PRODUCTS, body):
        errors.append(f"names an agent product or model: {sorted(set(re.findall(PRODUCTS, body)))}")
    for link in re.findall(r"\]\(([^)#:]+)\)", body):
        if not (folder / link).exists():
            errors.append(f"broken link: {link}")
    lines = text.count("\n")
    if lines > MAX_LINES:
        warnings.append(f"{lines} lines; move detail to reference/")
    for s in long_sentences(body):
        warnings.append(f"{len(s.split())} words: {s[:90]}")
    return errors, warnings


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "skills")
    names = sys.argv[2:] or sorted(p.name for p in root.iterdir() if p.is_dir())
    failed = 0
    for name in names:
        errors, warnings = check(root / name)
        for e in errors:
            print(f"ERROR {name}: {e}")
        for w in warnings:
            print(f"warn  {name}: {w}")
        failed += bool(errors)
    print(f"{len(names)} skills, {failed} with errors")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
