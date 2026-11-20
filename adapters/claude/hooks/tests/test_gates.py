import os
import unittest

from helpers import SID, TempCase, denied, git, lib, make_repo, pending_after, reason, run_text, write_run


class EditGate(TempCase):
    def setUp(self):
        super().setUp()
        self.repo = make_repo(self.tmp)
        git(self.repo, 'switch', '-q', '-c', 'feat/widget')
        self.src = os.path.join(self.repo, 'src', 'a.py')

    def edit(self, path):
        return self.pre('Edit', self.repo, file_path=path, old_string='a', new_string='b')

    def test_no_marker_no_run_allows(self):
        self.assertIsNone(self.edit(self.src))
        write_run(self.repo, 'other', run_text(session='aaaaaaaa-0000', steps=pending_after('propose')))
        self.assertIsNone(self.edit(self.src))

    def test_marker_without_run_denies(self):
        self.make_marker([self.repo])
        out = self.edit(self.src)
        self.assertTrue(denied(out))
        self.assertIn('create the state file first', reason(out).lower())
        self.assertIn(SID, reason(out))

    def test_marker_without_run_allows_agents_git_outside(self):
        self.make_marker([self.repo])
        self.assertIsNone(self.edit(os.path.join(self.repo, '.agents', 'work-flow', 'runs', 'new.md')))
        self.assertIsNone(self.edit(os.path.join(self.repo, '.git', 'info', 'exclude')))
        outside = os.path.join(self.tmp, 'notes', 'x.md')
        self.assertIsNone(self.edit(outside))

    def test_propose_open_denies(self):
        p = write_run(self.repo, 'widget', run_text(steps=pending_after('propose')))
        out = self.edit(self.src)
        self.assertTrue(denied(out))
        self.assertIn('propose has not passed', reason(out))
        self.assertIn(p, reason(out))

    def test_propose_passed_on_work_branch_allows(self):
        write_run(self.repo, 'widget', run_text(steps=pending_after('build')))
        self.assertIsNone(self.edit(self.src))
        self.assertIsNone(self.pre('Write', self.repo, file_path=self.src, content='x'))

    def test_propose_skip_allows(self):
        steps = pending_after('build')
        steps['propose'] = 'skip (question)'
        write_run(self.repo, 'widget', run_text(steps=steps))
        self.assertIsNone(self.edit(self.src))

    def test_base_branch_denies(self):
        write_run(self.repo, 'widget', run_text(steps=pending_after('build')))
        for branch in ('main', 'dev', 'master', 'develop'):
            git(self.repo, 'switch', '-q', '-C', branch)
            out = self.edit(self.src)
            self.assertTrue(denied(out), branch)
            self.assertIn(f'on base branch {branch}', reason(out))

    def test_run_base_branch_denies(self):
        write_run(self.repo, 'widget', run_text(base='origin/release (abc1234)', steps=pending_after('build')))
        git(self.repo, 'switch', '-q', '-c', 'release')
        self.assertTrue(denied(self.edit(self.src)))
        git(self.repo, 'switch', '-q', '-c', 'feat/other')
        self.assertIsNone(self.edit(self.src))

    def test_detached_head_is_not_base(self):
        write_run(self.repo, 'widget', run_text(steps=pending_after('build')))
        git(self.repo, 'switch', '-q', 'main')
        git(self.repo, 'switch', '-q', '--detach')
        self.assertIsNone(self.edit(self.src))

    def test_relative_path_and_notebook(self):
        write_run(self.repo, 'widget', run_text(steps=pending_after('propose')))
        self.assertTrue(denied(self.edit('src/a.py')))
        self.assertTrue(denied(self.pre('NotebookEdit', self.repo, notebook_path=self.repo + '/n.ipynb')))

    def test_run_in_other_repo_does_not_gate(self):
        other = make_repo(self.tmp, 'other')
        write_run(other, 'widget', run_text(steps=pending_after('propose')))
        self.make_marker([other])
        self.assertIsNone(self.edit(self.src))
        self.assertTrue(denied(self.pre('Edit', self.repo, file_path=os.path.join(other, 'x.py'))))

    def test_edit_of_run_file_adds_repo_to_marker(self):
        other = make_repo(self.tmp, 'other')
        self.make_marker([self.repo])
        self.edit(os.path.join(other, '.agents', 'work-flow', 'runs', 'w.md'))
        self.assertIn(other, self.marker()['repos'])

    def test_run_file_edit_without_marker_creates_none(self):
        self.edit(os.path.join(self.repo, '.agents', 'work-flow', 'runs', 'w.md'))
        self.assertIsNone(self.marker())


class EditGatePure(unittest.TestCase):
    def run_(self, steps, base='main'):
        return lib.Run('/r/.agents/work-flow/runs/w.md', run_text(base=base, steps=steps))

    def decide(self, path, runs, cur='feat/w', origin='main', marker=False, roots=lib.TMP_ROOTS):
        return lib.edit_decision(path, ['/r', '/tmp/r'], SID, marker, runs, lambda r: cur, lambda r: origin, roots)

    def test_tmp_allowed(self):
        runs = [lib.Run('/tmp/r/.agents/work-flow/runs/w.md', run_text(steps=pending_after('propose')))]
        self.assertIsNone(self.decide('/tmp/r/a.py', runs))
        self.assertIsNotNone(self.decide('/tmp/r/a.py', runs, roots=()))

    def test_origin_head_branch_is_base(self):
        runs = [self.run_(pending_after('build'))]
        self.assertIsNotNone(self.decide('/r/a.py', runs, cur='trunk', origin='trunk'))
        self.assertIsNone(self.decide('/r/a.py', runs, cur='trunk', origin='main'))

    def test_prefix_is_not_inside(self):
        runs = [self.run_(pending_after('propose'))]
        self.assertIsNone(self.decide('/r2/a.py', runs))
        self.assertIsNotNone(self.decide('/r/.agentsx/a', runs))
        self.assertIsNotNone(self.decide('/r/.github/w.yml', runs))

    def test_ignored_file_on_base_allowed(self):
        runs = [self.run_(pending_after('build'))]
        ign = lambda repo, path: path.startswith('/r/docs/')
        decide = lambda path: lib.edit_decision(path, ['/r'], SID, False, runs, lambda r: 'main',
                                                lambda r: 'main', (), ign)
        self.assertIsNone(decide('/r/docs/notes.md'))
        self.assertIsNotNone(decide('/r/src/a.py'))

    def test_aborted_run_does_not_gate(self):
        steps = pending_after('propose')
        steps['propose'] = 'aborted (user)'
        self.assertIsNone(self.decide('/r/a.py', [self.run_(steps)]))


class BashGate(TempCase):
    def setUp(self):
        super().setUp()
        self.repo = make_repo(self.tmp)

    def bash(self, command):
        return self.pre('Bash', self.repo, command=command)

    def test_no_marker_no_run_allows(self):
        self.assertIsNone(self.bash('git switch -c feat/x'))

    def test_marker_without_run_denies_creation_only(self):
        self.make_marker([self.repo])
        self.assertTrue(denied(self.bash('git switch -c feat/x')))
        self.assertTrue(denied(self.bash('git branch feat/x')))
        self.assertIsNone(self.bash('git branch -a'))
        self.assertIsNone(self.bash('ls'))

    def test_propose_gate(self):
        p = write_run(self.repo, 'widget', run_text(steps=pending_after('propose')))
        out = self.bash('git checkout -b feat/widget')
        self.assertTrue(denied(out))
        self.assertIn(p, reason(out))
        write_run(self.repo, 'widget', run_text(steps=pending_after('build')))
        self.assertIsNone(self.bash('git checkout -b feat/widget'))

    def test_prod_env(self):
        p = write_run(self.repo, 'widget', run_text(env='[]', steps=pending_after('build')))
        out = self.bash('set -a; . ./.env.production.local; node x.js')
        self.assertTrue(denied(out))
        self.assertIn(p, reason(out))
        self.assertIn('reads a production env file (.env.production.local)', reason(out))
        self.assertIn('Ask the user first', reason(out))
        self.assertIsNone(self.bash('git commit -m "rm .env.production"'))
        self.assertTrue(denied(self.bash('rg KEY .env.prod')))
        self.assertTrue(denied(self.bash('node --env-file=.env.production x.js')))
        self.assertIsNone(self.bash('cat .env.local .env.example'))
        write_run(self.repo, 'widget', run_text(env='[prod]', steps=pending_after('build')))
        self.assertIsNone(self.bash('cat .env.production'))

    def test_prod_without_active_run_allows(self):
        self.assertIsNone(self.bash('cat .env.production'))
        write_run(self.repo, 'widget', run_text(branch='feat/gone', steps={n: 'passed' for n in lib.ORDER}))
        self.assertIsNone(self.bash('cat .env.production'))


class ReadGrepGate(TempCase):
    def setUp(self):
        super().setUp()
        self.repo = make_repo(self.tmp)
        write_run(self.repo, 'widget', run_text(env='[local]', steps=pending_after('build')))

    def test_read(self):
        self.assertTrue(denied(self.pre('Read', self.repo, file_path=self.repo + '/.env.production')))
        self.assertTrue(denied(self.pre('Read', self.repo, file_path=self.repo + '/config/prod.env')))
        self.assertIsNone(self.pre('Read', self.repo, file_path=self.repo + '/.env.local'))
        self.assertIsNone(self.pre('Read', self.repo, file_path=self.repo + '/.env.example'))

    def test_grep(self):
        self.assertTrue(denied(self.pre('Grep', self.repo, pattern='KEY', path=self.repo + '/.env.prd')))
        self.assertIsNone(self.pre('Grep', self.repo, pattern=r'\.env\.production', path=self.repo))


if __name__ == '__main__':
    unittest.main()
