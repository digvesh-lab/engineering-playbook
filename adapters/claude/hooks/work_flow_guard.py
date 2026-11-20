#!/usr/bin/env python3
"""Claude Code hook entry for the work-flow guard. Reads the hook JSON on stdin; fails open on any error."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # -I drops the script dir from sys.path

import work_flow_lib as lib  # noqa: E402

GATED_EDIT = ('Edit', 'Write', 'NotebookEdit')


def _abs(path, cwd):
    path = os.path.expanduser(path)
    return os.path.realpath(path if os.path.isabs(path) else os.path.join(cwd, path))


def _existing_parent(path):
    cur = os.path.dirname(path)
    while cur and not os.path.isdir(cur) and os.path.dirname(cur) != cur:
        cur = os.path.dirname(cur)
    return cur


def _has_runs_folder(dirs):
    for d in dirs:
        cur = d
        while cur:
            if os.path.isdir(os.path.join(cur, '.agents', 'work-flow', 'runs')):
                return True
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
    return False


class Context:
    def __init__(self, data, env, git, extra_dirs=()):
        self.data, self.env, self.git = data, env, git
        self.sid = lib.valid_session(data.get('session_id'))
        self.cwd = os.path.realpath(data.get('cwd') or os.getcwd())
        self.additional, self.block_reads = lib.read_permissions(env)
        self.marker = lib.read_marker(env, self.sid) if self.sid else None
        self.extra_dirs = [d for d in extra_dirs if d]
        self._repos = self._runs = None

    def marker_repos(self):
        return [r for r in (self.marker or {}).get('repos') or [] if isinstance(r, str)]

    def quick_skip(self):
        if self.marker is not None:
            return False
        return not _has_runs_folder([self.cwd, *self.extra_dirs, *self.additional])

    def repos(self):
        if self._repos is None:
            out = []
            for d in [self.cwd, *self.extra_dirs, *self.additional]:
                top = self.git.toplevel(d)
                if not top and os.path.isdir(os.path.join(d, '.agents', 'work-flow', 'runs')):
                    top = d
                if top and top not in out:
                    out.append(top)
            for r in self.marker_repos():
                r = os.path.realpath(r)
                if os.path.isdir(r) and r not in out:
                    out.append(r)
            self._repos = out
        return self._repos

    def session_runs(self):
        if self._runs is None:
            self._runs = [] if not self.sid else [
                r for repo in self.repos() for r in lib.load_runs(repo) if lib.names_session(r.text, self.sid)]
        return self._runs

    def active(self):
        return lib.choose_active(self.session_runs(), self.git.branch)


def _deny(reason):
    return {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
                                   'permissionDecisionReason': reason}}


def _start_marker(ctx):
    if ctx.sid:
        top = ctx.git.toplevel(ctx.cwd)
        lib.write_marker(ctx.env, ctx.sid, [top] if top else [])


def _note_run_file(ctx, path):
    m = lib.RUN_FILE_RE.match(path)
    if m and ctx.sid and ctx.marker is not None:
        ctx.marker = lib.write_marker(ctx.env, ctx.sid, [m.group(1)], create=False)


def on_prompt(ctx):
    if not lib.prompt_starts_work_flow(ctx.data.get('prompt')):
        return None
    _start_marker(ctx)
    skill_real = os.path.realpath(os.path.join(lib.claude_home(ctx.env), 'skills', 'work-flow'))
    parts = [lib.start_context(skill_real)]
    warn = lib.read_block_warning(ctx.block_reads, ctx.cwd, ctx.additional, skill_real)
    if warn:
        parts.append(warn)
    return {'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': ' '.join(parts)}}


def on_pre_tool(ctx, allow_roots):
    tool = ctx.data.get('tool_name')
    ti = ctx.data.get('tool_input') or {}
    if tool == 'Skill':
        if lib.skill_starts_work_flow(ti):
            _start_marker(ctx)
        return None
    if tool in GATED_EDIT:
        raw = ti.get('file_path') or ti.get('notebook_path')
        if not raw:
            return None
        path = _abs(raw, ctx.cwd)
        _note_run_file(ctx, path)
        ctx.extra_dirs = [_existing_parent(path)]
        if ctx.quick_skip():
            return None
        reason = lib.edit_decision(path, ctx.repos(), ctx.sid, ctx.marker is not None, ctx.session_runs(),
                                   ctx.git.branch, ctx.git.origin_head, allow_roots,
                                   lambda repo, p: lib.run_git(['check-ignore', '-q', p], repo) is not None)
        return _deny(reason) if reason else None
    if tool == 'Bash':
        cmd = ti.get('command') or ''
        if not (lib.creates_branch(cmd) or lib.prod_match(cmd)) or ctx.quick_skip():
            return None
        active = ctx.active()
        reason = (lib.branch_decision(cmd, ctx.sid, ctx.marker is not None, ctx.session_runs(), active)
                  or lib.prod_decision([cmd], active))
        return _deny(reason) if reason else None
    if tool in ('Read', 'Grep'):
        texts = [ti.get(k) for k in ('file_path', 'path') if isinstance(ti.get(k), str)]
        if not any(lib.prod_match(t) for t in texts) or ctx.quick_skip():
            return None
        reason = lib.prod_decision(texts, ctx.active())
        return _deny(reason) if reason else None
    return None


def on_stop(ctx):
    if not ctx.sid or ctx.quick_skip():
        return None
    issues = []
    for run in ctx.session_runs():
        issues += [f'{os.path.basename(run.path)}: {p}' for p in lib.stop_problems(run, ctx.git, lib.read_text)]
    if not issues:
        return None
    msg = lib.stop_message(issues)
    if ctx.data.get('stop_hook_active'):
        return {'systemMessage': msg}
    return {'decision': 'block', 'reason': msg}


def handle(data, env, git=None, allow_roots=lib.TMP_ROOTS):
    if not isinstance(data, dict):
        return None
    ctx = Context(data, env, git or lib.Git())
    event = data.get('hook_event_name')
    if event == 'UserPromptSubmit':
        return on_prompt(ctx)
    if event == 'PreToolUse':
        return on_pre_tool(ctx, allow_roots)
    if event == 'Stop':
        return on_stop(ctx)
    if event == 'SessionEnd':
        if ctx.sid:
            lib.delete_marker(env, ctx.sid)
    return None


def main():
    try:
        out = handle(json.loads(sys.stdin.read()), os.environ)
        if out:
            sys.stdout.write(json.dumps(out))
    except Exception:  # noqa: BLE001 - a guard must never break the session
        pass
    sys.exit(0)


if __name__ == '__main__':
    main()
