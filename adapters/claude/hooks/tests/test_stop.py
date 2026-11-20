import os
import unittest

from helpers import SID, TempCase, commit, fixture, git, lib, make_repo, run_text, states, write_index, write_run


class StopProblems(TempCase):
    def setUp(self):
        super().setUp()
        self.repo = make_repo(self.tmp)

    def problems(self, text, slug='widget'):
        p = write_run(self.repo, slug, text)
        return lib.stop_problems(lib.Run(p, text, repo=self.repo), lib.Git(), lib.read_text)

    def feature_branch(self):
        git(self.repo, 'switch', '-q', '-c', 'feat/widget')
        return commit(self.repo, 'work')

    def test_no_steps_block(self):
        self.assertEqual(self.problems('task: x\nsession: %s\nbranch:\n' % SID), ['no steps: block'])

    def test_missing_steps_reported_once_past_assess(self):
        text = run_text(branch='', steps={'recall': 'passed', 'assess': 'passed', 'explain': 'pending'})
        out = self.problems(text)
        self.assertEqual(len(out), 1)
        self.assertIn('lacks grill, propose', out[0])

    def test_missing_steps_tolerated_early_question_or_aborted(self):
        early = run_text(branch='', steps={'recall': 'passed', 'assess': 'pending'})
        self.assertEqual(self.problems(early), [])
        question = run_text(branch='', type='question', steps={'recall': 'passed', 'explain': 'passed'})
        self.assertEqual(self.problems(question), [])
        aborted = run_text(branch='', steps={'recall': 'passed', 'propose': 'aborted (user)'})
        self.assertEqual(self.problems(aborted), [])

    def test_missing_steps_when_branch_set(self):
        out = self.problems(run_text(branch='feat/nope', steps={'recall': 'passed'}))
        self.assertTrue(any('lacks assess' in p for p in out))

    def test_order(self):
        out = self.problems(run_text(branch='', steps=states(test='pending', ship='pending', remember='pending')))
        self.assertEqual(out, ['clean is passed but earlier step test is still pending',
                               'prune is passed but earlier step test is still pending',
                               'review is passed but earlier step test is still pending'])

    def test_commit_not_recorded(self):
        head = self.feature_branch()
        steps = states(ship='pending', remember='pending')
        out = self.problems(run_text(steps=steps))
        self.assertEqual(out, [f'commit {head[:7]} on feat/widget is not recorded'])

    def test_commit_recorded_by_prefix(self):
        head = self.feature_branch()
        steps = states(ship='pending', remember='pending')
        self.assertEqual(self.problems(run_text(steps=steps, log=f'- 2026-11-20 build {head[:7]}')), [])
        self.assertEqual(self.problems(run_text(steps=steps, log=f'- build {head[:12]}')), [])
        wrong = ('0' if head[0] != '0' else '1') + head[1:7]
        self.assertTrue(self.problems(run_text(steps=steps, log=f'- build {wrong}')))

    def test_commit_check_skipped(self):
        steps = states(ship='pending', remember='pending')
        git(self.repo, 'branch', 'feat/widget')
        self.assertEqual(self.problems(run_text(steps=steps)), [], 'no commits beyond base')
        self.assertEqual(self.problems(run_text(branch='feat/absent', steps=steps)), [], 'branch absent')
        self.assertEqual(self.problems(run_text(branch='none (assessment only)', steps=steps)), [])

    def test_step12(self):
        msg = 'step 12 not run'
        steps = states(remember='pending')
        self.assertTrue(any(msg in p for p in self.problems(run_text(branch='', steps=steps))), 'no index')
        write_index(self.repo, fixture('index.md'))
        self.assertTrue(any(msg in p for p in self.problems(run_text(branch='', steps=steps))),
                        'in-progress line and widget-2 line do not count')
        self.assertEqual(self.problems(run_text(branch='', steps=steps), slug='widget-2'), [])
        write_index(self.repo, fixture('index.md') + '- 2026-11-21 widget | feature | api | PR #3 | done\n')
        self.assertEqual(self.problems(run_text(branch='', steps=steps)), [])

    def test_step12_not_checked_before_ship(self):
        self.assertEqual(self.problems(run_text(branch='', steps=states(ship='pending', remember='pending'))), [])


class StopEvent(TempCase):
    def setUp(self):
        super().setUp()
        self.repo = make_repo(self.tmp)

    def test_block_then_system_message(self):
        write_run(self.repo, 'widget', run_text(branch='', steps=states(test='pending', ship='pending',
                                                                          remember='pending')))
        out = self.handle('Stop', self.repo)
        self.assertEqual(out['decision'], 'block')
        self.assertIn('widget.md: clean is passed', out['reason'])
        out = self.handle('Stop', self.repo, stop_hook_active=True)
        self.assertEqual(set(out), {'systemMessage'})

    def test_other_session_and_notes_ignored(self):
        bad = run_text(session='aaaaaaaa-0000', branch='', steps=states(test='pending'))
        write_run(self.repo, 'other', bad)
        write_run(self.repo, 'widget.notes', run_text(branch='', steps=states(test='pending')))
        self.assertIsNone(self.handle('Stop', self.repo))

    def test_clean_run_passes(self):
        write_run(self.repo, 'widget', run_text(branch='', steps=states(ship='pending', remember='pending')))
        self.assertIsNone(self.handle('Stop', self.repo))

    def test_runs_in_marker_repo(self):
        other = make_repo(self.tmp, 'other')
        write_run(other, 'widget', run_text(branch='', steps=states(test='pending', ship='pending',
                                                                     remember='pending')))
        cwd = os.path.join(self.tmp, 'plain')
        os.makedirs(cwd)
        self.assertIsNone(self.handle('Stop', cwd))
        self.make_marker([other])
        self.assertEqual(self.handle('Stop', cwd)['decision'], 'block')


if __name__ == '__main__':
    unittest.main()
