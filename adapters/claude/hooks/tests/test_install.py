import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

from helpers import HOOKS  # noqa: F401  (puts the hooks folder on sys.path)

import install_hooks as ih

OTHER = {'matcher': 'Bash', 'hooks': [{'type': 'command', 'command': 'python3 /h/use-rg.py'}]}
OLD = {'hooks': [{'type': 'command', 'command': 'python3 /home/u/.claude/hooks/work-flow-steps-check.py'},
                 {'type': 'command', 'command': 'notify-send done'}]}


class Installer(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.spath = os.path.join(self.tmp, 'claude', 'settings.json')
        self.gpath = ih.guard_path()

    def write(self, data):
        os.makedirs(os.path.dirname(self.spath), exist_ok=True)
        with open(self.spath, 'w') as fh:
            json.dump(data, fh)

    def read(self):
        with open(self.spath) as fh:
            return json.load(fh)

    def run_(self, fn):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            fn(self.spath, self.gpath)
        return buf.getvalue()

    def tagged(self, data):
        return [(e, g.get('matcher')) for e, gs in data.get('hooks', {}).items() for g in gs
                for h in g['hooks'] if self.gpath in h['command']]

    def test_creates_missing_settings(self):
        self.run_(ih.install)
        data = self.read()
        self.assertEqual(sorted(self.tagged(data), key=str), sorted(ih.EVENTS, key=str))
        h = data['hooks']['Stop'][0]['hooks'][0]
        self.assertEqual(h, {'type': 'command', 'command': f'python3 -I {self.gpath}', 'timeout': 5})
        self.assertNotIn('matcher', data['hooks']['Stop'][0])
        self.assertFalse(os.path.exists(self.spath + '.bak'))

    def test_preserves_other_keys_and_is_idempotent(self):
        original = {'permissions': {'allow': ['Bash(ls)']}, 'model': 'x', 'hooks': {'PreToolUse': [OTHER]}}
        self.write(original)
        self.run_(ih.install)
        first = self.read()
        with open(self.spath + '.bak') as fh:
            self.assertEqual(json.load(fh), original)
        self.run_(ih.install)
        self.assertEqual(self.read(), first)
        self.assertEqual(first['permissions'], original['permissions'])
        self.assertEqual(first['model'], 'x')
        self.assertEqual(first['hooks']['PreToolUse'][0], OTHER)
        self.assertEqual(len(self.tagged(first)), len(ih.EVENTS))

    def test_replaces_old_stop_hook(self):
        self.write({'hooks': {'Stop': [OLD]}})
        out = self.run_(ih.install)
        self.assertIn('replaced old Stop hook', out)
        stop = self.read()['hooks']['Stop']
        commands = [h['command'] for g in stop for h in g['hooks']]
        self.assertNotIn('python3 /home/u/.claude/hooks/work-flow-steps-check.py', commands)
        self.assertIn('notify-send done', commands)

    def test_uninstall_removes_tagged_only(self):
        self.write({'hooks': {'PreToolUse': [OTHER]}, 'model': 'x'})
        self.run_(ih.install)
        self.run_(ih.uninstall)
        self.assertEqual(self.read(), {'hooks': {'PreToolUse': [OTHER]}, 'model': 'x'})
        self.write({'model': 'x'})
        self.run_(ih.install)
        self.run_(ih.uninstall)
        self.assertEqual(self.read(), {'model': 'x'})

    def test_uninstall_without_settings(self):
        self.run_(ih.uninstall)
        self.assertFalse(os.path.exists(self.spath))

    def test_symlinked_settings_stays_link(self):
        real = os.path.join(self.tmp, 'dotfiles.json')
        with open(real, 'w') as fh:
            json.dump({'model': 'x'}, fh)
        os.makedirs(os.path.dirname(self.spath))
        os.symlink(real, self.spath)
        self.run_(ih.install)
        self.assertTrue(os.path.islink(self.spath))
        self.assertTrue(self.tagged(self.read()))

    def test_invalid_json_is_left_alone(self):
        os.makedirs(os.path.dirname(self.spath))
        with open(self.spath, 'w') as fh:
            fh.write('{"token": "s3cret",')
        err = io.StringIO()
        with mock.patch.dict(os.environ, {'CLAUDE_HOME': os.path.dirname(self.spath)}), \
                contextlib.redirect_stderr(err):
            self.assertEqual(ih.main(['x', 'install']), 1)
        self.assertNotIn('s3cret', err.getvalue())
        with open(self.spath) as fh:
            self.assertEqual(fh.read(), '{"token": "s3cret",')

    def test_main_usage(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(ih.main(['x']), 2)


if __name__ == '__main__':
    unittest.main()
