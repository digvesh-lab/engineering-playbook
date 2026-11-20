import os
import shutil
import string
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOKS = os.path.dirname(HERE)
FIX = os.path.join(HERE, 'fixtures')
sys.path.insert(0, HOOKS)

import work_flow_lib as lib  # noqa: E402
import work_flow_guard as guard  # noqa: E402

SID = '9049caa9-495d-4470-b63e-756c73744835'
GIT_ENV = {**os.environ, 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1',
           'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@t', 'GIT_COMMITTER_NAME': 't',
           'GIT_COMMITTER_EMAIL': 't@t'}


def fixture(name):
    with open(os.path.join(FIX, name), encoding='utf-8') as fh:
        return fh.read()


def states(**override):
    out = {n: 'passed (auto: ok) @ abc1234' for n in lib.ORDER}
    out.update(override)
    return {k: v for k, v in out.items() if v is not None}


def pending_after(step):
    i = lib.ORDER.index(step)
    return {n: ('passed (auto: ok)' if j < i else 'pending') for j, n in enumerate(lib.ORDER)}


def run_text(session=SID, base='origin/main (c43c046)', branch='feat/widget', env='[]', steps=None,
             type='feature', log=''):
    steps = states() if steps is None else steps
    block = '\n'.join(f'  {k}: {v}' for k, v in steps.items())
    return string.Template(fixture('run_template.md')).substitute(
        session=session, base=base, branch=branch, env=env, steps=block, type=type, log=log)


def git(cwd, *args):
    return subprocess.run(['git', '-C', cwd, *args], check=True, capture_output=True, text=True,
                          env=GIT_ENV).stdout.strip()


def make_repo(root, name='repo'):
    path = os.path.join(root, name)
    os.makedirs(path)
    git(path, 'init', '-q', '-b', 'main')
    commit(path, 'init')
    return os.path.realpath(path)


def commit(repo, msg):
    with open(os.path.join(repo, 'f.txt'), 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')
    git(repo, 'add', 'f.txt')
    git(repo, 'commit', '-q', '-m', msg)
    return git(repo, 'rev-parse', 'HEAD')


def write_run(repo, slug, text):
    d = os.path.join(repo, '.agents', 'work-flow', 'runs')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, slug + '.md')
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(text)
    return p


def write_index(repo, text):
    d = os.path.join(repo, '.agents', 'work-flow', 'memory')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'index.md'), 'w', encoding='utf-8') as fh:
        fh.write(text)


class TempCase(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.env = {'CLAUDE_HOME': os.path.join(self.tmp, 'claude'),
                    'XDG_STATE_HOME': os.path.join(self.tmp, 'state')}
        os.makedirs(self.env['CLAUDE_HOME'])

    def handle(self, event, cwd, sid=SID, **fields):
        data = {'hook_event_name': event, 'session_id': sid, 'cwd': cwd, **fields}
        return guard.handle(data, self.env, lib.Git(), allow_roots=())

    def pre(self, tool, cwd, **tool_input):
        return self.handle('PreToolUse', cwd, tool_name=tool, tool_input=tool_input)

    def make_marker(self, repos=()):
        lib.write_marker(self.env, SID, list(repos))

    def marker(self):
        return lib.read_marker(self.env, SID)


def denied(out):
    return bool(out) and out['hookSpecificOutput']['permissionDecision'] == 'deny'


def reason(out):
    return out['hookSpecificOutput']['permissionDecisionReason']
