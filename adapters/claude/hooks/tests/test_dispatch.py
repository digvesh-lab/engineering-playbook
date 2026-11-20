import json
import os
import subprocess
import sys
import time
import unittest

from helpers import HOOKS, SID, TempCase, guard, lib, make_repo

GUARD = os.path.join(HOOKS, 'work_flow_guard.py')


def boom(args, cwd):
    raise AssertionError(f'git called: {args}')


class Markers(TempCase):
    def setUp(self):
        super().setUp()
        self.repo = make_repo(self.tmp)
        self.clone = os.path.join(self.tmp, 'clone')
        os.makedirs(os.path.join(self.clone, 'skills', 'work-flow', 'reference'))
        os.makedirs(os.path.join(self.env['CLAUDE_HOME'], 'skills'))
        os.symlink(os.path.join(self.clone, 'skills', 'work-flow'),
                   os.path.join(self.env['CLAUDE_HOME'], 'skills', 'work-flow'))

    def settings(self, perms):
        with open(os.path.join(self.env['CLAUDE_HOME'], 'settings.json'), 'w') as fh:
            json.dump({'permissions': perms, 'env': {'SECRET': 'x'}}, fh)

    def prompt(self, text, sid=SID):
        return self.handle('UserPromptSubmit', self.repo, sid=sid, prompt=text)

    def test_prompt_creates_marker_and_context(self):
        out = self.prompt('/work-flow fix the widget')
        ctx = out['hookSpecificOutput']
        self.assertEqual(ctx['hookEventName'], 'UserPromptSubmit')
        self.assertIn(os.path.join(self.clone, 'skills', 'work-flow') + '/reference/', ctx['additionalContext'])
        self.assertIn('/add-dir', ctx['additionalContext'])
        m = self.marker()
        self.assertEqual(m['repos'], [self.repo])
        self.assertIn('started', m)

    def test_reference_path_always_injected(self):
        ref = os.path.join(self.clone, 'skills', 'work-flow') + '/reference/'
        for perms in ({}, {'blockReadsOutsideWorkingDirectories': True, 'additionalDirectories': []}):
            self.settings(perms)
            ctx = self.prompt('/work-flow x')['hookSpecificOutput']['additionalContext']
            self.assertIn(ref, ctx)
            self.assertNotIn('STOP', ctx)
            self.assertNotIn('SECRET', ctx)

    def test_status_and_other_prompts(self):
        self.assertIsNone(self.prompt('/work-flow status'))
        self.assertIsNone(self.prompt('/work-memory'))
        self.assertIsNone(self.marker())

    def test_invalid_session_writes_nothing(self):
        self.prompt('/work-flow x', sid='../../evil')
        self.assertFalse(os.path.exists(lib.marker_dir(self.env)))

    def test_skill_creates_marker_and_injects_start_text(self):
        self.assertIsNone(self.pre('Skill', self.repo, skill='work-flow', args='status'))
        self.assertIsNone(self.marker())
        out = self.pre('Skill', self.repo, skill='work-flow', args='fix x')['hookSpecificOutput']
        self.assertEqual(out['hookEventName'], 'PreToolUse')
        self.assertNotIn('permissionDecision', out)
        self.assertIn('work-flow started', out['additionalContext'])
        self.assertEqual(self.marker()['repos'], [self.repo])

    def test_marker_create_false_creates_nothing(self):
        self.assertIsNone(lib.write_marker(self.env, SID, ['/x'], create=False))
        self.assertIsNone(self.marker())
        self.assertFalse(os.path.exists(lib.marker_path(self.env, SID)))

    def test_session_end_deletes(self):
        self.prompt('/work-flow x')
        self.handle('SessionEnd', self.repo)
        self.assertIsNone(self.marker())

    def test_old_markers_pruned(self):
        os.makedirs(lib.marker_dir(self.env))
        old = lib.marker_path(self.env, 'aaaaaaaa-old')
        fresh = lib.marker_path(self.env, 'bbbbbbbb-new')
        for p in (old, fresh):
            with open(p, 'w') as fh:
                fh.write('{}')
        past = time.time() - 8 * 24 * 3600
        os.utime(old, (past, past))
        self.prompt('/work-flow x')
        self.assertFalse(os.path.exists(old))
        self.assertTrue(os.path.exists(fresh))


class FastPathAndFailOpen(TempCase):
    def test_no_marker_no_runs_skips_git(self):
        plain = os.path.join(self.tmp, 'plain')
        os.makedirs(plain)
        git = lib.Git(runner=boom)
        for data in ({'hook_event_name': 'Stop'},
                     {'hook_event_name': 'PreToolUse', 'tool_name': 'Edit',
                      'tool_input': {'file_path': plain + '/a.py'}},
                     {'hook_event_name': 'PreToolUse', 'tool_name': 'Bash',
                      'tool_input': {'command': 'git switch -c x; cat .env.production'}}):
            self.assertIsNone(guard.handle({**data, 'session_id': SID, 'cwd': plain}, self.env, git, ()))

    def run_script(self, stdin, env=None):
        return subprocess.run([sys.executable, '-I', GUARD], input=stdin, capture_output=True, text=True,
                              env={**os.environ, **self.env, **(env or {})}, timeout=10)

    def test_garbage_stdin(self):
        for stdin in ('', 'not json', '[1, 2]', '{"hook_event_name": "PreToolUse", "tool_input": 5}', 'null'):
            p = self.run_script(stdin)
            self.assertEqual((p.returncode, p.stdout, p.stderr), (0, '', ''), stdin)

    def test_script_runs_isolated(self):
        repo = make_repo(self.tmp)
        p = self.run_script(json.dumps({'hook_event_name': 'UserPromptSubmit', 'session_id': SID,
                                        'cwd': repo, 'prompt': '/work-flow x'}))
        self.assertEqual(p.returncode, 0)
        self.assertIn('additionalContext', json.loads(p.stdout)['hookSpecificOutput'])
        self.assertTrue(os.path.exists(lib.marker_path(self.env, SID)))


if __name__ == '__main__':
    unittest.main()
