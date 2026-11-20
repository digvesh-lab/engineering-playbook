#!/usr/bin/env python3
"""Add or remove the work-flow guard hooks in ${CLAUDE_HOME:-~/.claude}/settings.json. Usage: install_hooks.py install|uninstall"""
import json
import os
import shlex
import shutil
import sys

EVENTS = [('UserPromptSubmit', None), ('PreToolUse', 'Skill'), ('PreToolUse', 'Edit|Write|NotebookEdit'),
          ('PreToolUse', 'Bash'), ('PreToolUse', 'Read|Grep'), ('Stop', None), ('SessionEnd', None)]
OLD_HOOK = 'work-flow-steps-check.py'
TIMEOUT = 5


def guard_path():
    return os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'work_flow_guard.py'))


def settings_path(env=os.environ):
    home = env.get('CLAUDE_HOME') or os.path.join(os.path.expanduser('~'), '.claude')
    return os.path.join(home, 'settings.json')


def load(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f'{path} is not a JSON object')
    return data


def save(path, data):
    target = os.path.realpath(path)  # keep a symlinked settings.json a symlink
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = target + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=2)
        fh.write('\n')
    if os.path.exists(target):
        shutil.copymode(target, tmp)
    os.replace(tmp, target)


def strip(data, match):
    """Remove each hook command for which match(command) is true; return the removed commands."""
    removed = []
    hooks = data.get('hooks')
    if not isinstance(hooks, dict):
        return removed
    for event in list(hooks):
        groups = hooks[event]
        if not isinstance(groups, list):
            continue
        kept_groups = []
        for g in groups:
            items = g.get('hooks') if isinstance(g, dict) else None
            if not isinstance(items, list):
                kept_groups.append(g)
                continue
            kept = []
            for h in items:
                cmd = h.get('command') if isinstance(h, dict) else None
                if isinstance(cmd, str) and match(cmd):
                    removed.append((event, cmd))
                else:
                    kept.append(h)
            if kept or not items:
                kept_groups.append({**g, 'hooks': kept})
        if kept_groups:
            hooks[event] = kept_groups
        else:
            del hooks[event]
    if not hooks:
        del data['hooks']
    return removed


def entries(path):
    cmd = f'python3 -I {shlex.quote(path)}'
    out = []
    for event, matcher in EVENTS:
        group = {'hooks': [{'type': 'command', 'command': cmd, 'timeout': TIMEOUT}]}
        if matcher:
            group = {'matcher': matcher, **group}
        out.append((event, group))
    return out


def install(spath, gpath):
    data = load(spath)
    if os.path.exists(spath):
        shutil.copy2(os.path.realpath(spath), spath + '.bak')
        print(f'backup  {spath}.bak')
    strip(data, lambda c: gpath in c)
    for event, cmd in strip(data, lambda c: OLD_HOOK in c):
        print(f'replaced old {event} hook {cmd}')
    hooks = data.setdefault('hooks', {})
    for event, group in entries(gpath):
        hooks.setdefault(event, []).append(group)
    save(spath, data)
    print(f'installed work-flow guard hooks in {spath}')


def uninstall(spath, gpath):
    if not os.path.exists(spath):
        return
    data = load(spath)
    if strip(data, lambda c: gpath in c):
        save(spath, data)
        print(f'removed work-flow guard hooks from {spath}')


def main(argv):
    if len(argv) != 2 or argv[1] not in ('install', 'uninstall'):
        print('usage: install_hooks.py install|uninstall', file=sys.stderr)
        return 2
    spath, gpath = settings_path(), guard_path()
    try:
        (install if argv[1] == 'install' else uninstall)(spath, gpath)
    except (OSError, ValueError) as e:
        print(f'work-flow hooks not changed: {type(e).__name__} in {spath}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
