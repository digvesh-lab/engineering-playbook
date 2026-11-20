import unittest

from helpers import SID, fixture, lib, run_text, states


class ParseFields(unittest.TestCase):
    def test_base(self):
        self.assertEqual(lib.parse_base('origin/main (c43c046)'), 'main')
        self.assertEqual(lib.parse_base('dev (origin/dev acb7121)'), 'dev')
        self.assertEqual(lib.parse_base('origin/dev 3d47c1e (memory: PRs go into dev)'), 'dev')
        self.assertEqual(lib.parse_base('feat/parent'), 'feat/parent')
        self.assertIsNone(lib.parse_base(''))
        self.assertIsNone(lib.parse_base(None))

    def test_branch(self):
        self.assertEqual(lib.parse_branch('fix/auditor-data-noise (from dev)'), 'fix/auditor-data-noise')
        self.assertEqual(lib.parse_branch('feat/widget'), 'feat/widget')
        self.assertIsNone(lib.parse_branch('none (assessment only)'))
        self.assertIsNone(lib.parse_branch('not created (x is open as PR #480; do not reuse)'))
        self.assertIsNone(lib.parse_branch(''))
        self.assertIsNone(lib.parse_branch('-x'))

    def test_env(self):
        self.assertEqual(lib.parse_env('[]'), [])
        self.assertEqual(lib.parse_env('[prod]'), ['prod'])
        self.assertEqual(lib.parse_env('[local, Production]'), ['local', 'production'])
        self.assertEqual(lib.parse_env(None), [])

    def test_run_from_template(self):
        r = lib.Run('/r/.agents/work-flow/runs/widget.md', run_text(steps=states(build='pending')))
        self.assertEqual(r.repo, '/r')
        self.assertEqual(r.slug, 'widget')
        self.assertEqual(r.base, 'main')
        self.assertEqual(r.branch, 'feat/widget')
        self.assertEqual(r.env, [])
        self.assertTrue(r.has_steps)
        self.assertEqual(list(r.steps), lib.ORDER)
        self.assertEqual(r.steps['build'], 'pending')
        self.assertEqual(r.steps['recall'], 'passed')
        self.assertNotIn('build.branch', r.steps)  # switches: line is not the steps block

    def test_steps_block_ends_at_heading(self):
        text = 'steps:\n  recall: passed\n## Notes\n  assess: passed\n'
        self.assertEqual(lib.steps_of(text), ({'recall': 'passed'}, True))

    def test_single_line_steps(self):
        r = lib.Run('/r/.agents/work-flow/runs/q.md', fixture('run_singleline.md'))
        self.assertEqual(r.steps, {'recall': 'passed', 'assess': 'passed', 'explain': 'pending', 'grill': 'skip'})
        self.assertEqual(r.base, 'dev')
        self.assertIsNone(r.branch)
        self.assertEqual(r.env, ['prod'])
        self.assertEqual(r.type, 'question')

    def test_no_steps_block(self):
        self.assertEqual(lib.steps_of('task: x\nbranch: y\n'), ({}, False))


class Session(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(lib.valid_session(SID), SID)
        self.assertEqual(lib.valid_session('ABCDEF01'), 'ABCDEF01')

    def test_invalid(self):
        for bad in ('../../etc/passwd', 'abc', 'g' * 10, 'a' * 65, '', None, 123, SID + '/x'):
            self.assertIsNone(lib.valid_session(bad), bad)

    def test_names_session(self):
        self.assertTrue(lib.names_session(run_text(), SID))
        self.assertTrue(lib.names_session(f'session: {SID}   \n', SID))
        self.assertFalse(lib.names_session(f'session: {SID} (old)\n', SID))
        self.assertFalse(lib.names_session(run_text(session='aaaaaaaa-bbbb'), SID))
        self.assertFalse(lib.names_session(run_text(), None))


class ActiveRun(unittest.TestCase):
    def mk(self, repo, slug, mtime, branch='feat/a', steps=None):
        return lib.Run(f'{repo}/.agents/work-flow/runs/{slug}.md',
                       run_text(branch=branch, steps=steps or states(build='pending')), mtime)

    def test_branch_match_wins_over_newer(self):
        a = self.mk('/r', 'a', 1, branch='feat/a')
        b = self.mk('/r', 'b', 9, branch='feat/b')
        self.assertIs(lib.choose_active([a, b], lambda repo: 'feat/a'), a)

    def test_newest_open_without_match(self):
        a = self.mk('/r', 'a', 1)
        b = self.mk('/r', 'b', 9)
        done = self.mk('/r', 'c', 20, steps=states())
        self.assertIs(lib.choose_active([a, b, done], lambda repo: 'other'), b)

    def test_none_and_aborted(self):
        done = self.mk('/r', 'c', 20, steps=states())
        self.assertIsNone(lib.choose_active([done], lambda repo: 'other'))
        aborted = self.mk('/r', 'x', 30, branch='feat/x', steps=states(build='aborted (user)', test='pending'))
        self.assertIsNone(lib.choose_active([aborted], lambda repo: 'feat/x'))


class StartSignals(unittest.TestCase):
    def test_prompt(self):
        for p in ('/work-flow fix the bug', '  /work-flow', '/work-flow\nmore', '/work-flow resume x'):
            self.assertTrue(lib.prompt_starts_work_flow(p), p)
        for p in ('/work-flow status', '/work-flow-progress', '/work-memory', 'run /work-flow', '', None):
            self.assertFalse(lib.prompt_starts_work_flow(p), p)

    def test_skill(self):
        self.assertTrue(lib.skill_starts_work_flow({'skill': 'work-flow', 'args': 'fix x'}))
        self.assertTrue(lib.skill_starts_work_flow({'skill': 'work-flow'}))
        self.assertFalse(lib.skill_starts_work_flow({'skill': 'work-flow', 'args': 'status'}))
        self.assertFalse(lib.skill_starts_work_flow({'skill': 'work-memory', 'args': 'x'}))
        self.assertFalse(lib.skill_starts_work_flow({'skill': 'x:work-flow'}))
        self.assertFalse(lib.skill_starts_work_flow('work-flow'))

    def test_read_block_warning(self):
        msg = lib.read_block_warning('/clone/skills/work-flow')
        self.assertIn('/clone/skills/work-flow/reference/', msg)
        self.assertIn('/add-dir', msg)
        self.assertNotIn('STOP', msg)

    def test_index_slug_is_run_token(self):
        idx = '- 2026-11-20 other | fix | api | PR #1 | done | fix/auditor-data-noise\n'
        self.assertFalse(lib.index_has_final_line(idx, 'fix/auditor-data-noise'))
        self.assertTrue(lib.index_has_final_line(idx, 'other'))
        self.assertFalse(lib.index_has_final_line('- 2026-11-20 x | in-progress |\n', 'y'))


class ProdMatch(unittest.TestCase):
    def test_hits(self):
        for t in ('cat .env.production.local', '.env.prod', 'src/.env.prd', 'x/.env.prod-backup',
                  'prod.env', 'cp production.env /x'):
            self.assertTrue(lib.prod_match(t), t)

    def test_misses(self):
        for t in ('.env.local', '.env.example', '.env', '.env.products', 'reproduction.env', 'npm run prod', ''):
            self.assertIsNone(lib.prod_match(t), t)

    def test_search_commands_skipped(self):
        for t in ('git commit -m "drop .env.production"', 'rg .env.prod src', 'grep -r prod.env .',
                  'git log -S.env.production', 'ls && git show x:.env.prod'):
            self.assertIsNone(lib.prod_match(t), t)
        for t in ('cat .env.production', 'source .env.prod', 'node --env-file=.env.production x.js',
                  'git log; cat .env.prod'):
            self.assertTrue(lib.prod_match(t), t)


class BranchCreation(unittest.TestCase):
    def test_creates(self):
        for c in ('git switch -c feat/x', 'git switch -C feat/x', 'git switch --create feat/x origin/main',
                  'git checkout -b feat/x', 'git checkout -B feat/x', 'git worktree add -b feat/x ../wt',
                  'git branch feat/x', 'git -C /r branch feat/x main', 'cd /r && git checkout -b x',
                  'git status; git switch -c y', 'GIT_TRACE=0 git checkout -b z'):
            self.assertTrue(lib.creates_branch(c), c)

    def test_list_forms(self):
        for c in ('git branch', 'git branch -a', 'git branch -r', 'git branch -d feat/x', 'git branch -D feat/x',
                  'git branch --show-current', 'git branch -v', 'git branch -vv', "git branch --list 'feat/*'",
                  'git branch --merged main', 'git switch main', 'git checkout main', 'git checkout -- f.txt',
                  'git worktree add ../wt main', 'echo git checkout -b x', 'git log --branches'):
            self.assertFalse(lib.creates_branch(c), c)


if __name__ == '__main__':
    unittest.main()
