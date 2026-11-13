import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
NAMES = ('athena', 'heimdall', 'hermes', 'iris', 'nemesis', 'odin', 'saga', 'themis', 'thor')


class PreviewTests(unittest.TestCase):
    def test_claude_dry_run_previews_nine_without_writes(self):
        script = ROOT / 'install.sh'
        self.assertTrue(script.is_file(), 'Installer CLI install.sh is missing')
        with tempfile.TemporaryDirectory(dir='/tmp/opencode') as temp:
            home = Path(temp) / 'home with spaces'
            home.mkdir()
            env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home / '.config'), XDG_STATE_HOME=str(home / '.local/state'))
            for key in list(env):
                if key.startswith('GIT_'):
                    del env[key]
            env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null', GIT_TERMINAL_PROMPT='0')
            result = subprocess.run(['bash', str(script), '--runtime', 'claude', '--dry-run'], env=env, cwd=temp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name in NAMES:
                self.assertIn(name + '.md', result.stdout)
            self.assertEqual(list(home.iterdir()), [])


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir='/tmp/opencode')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.home = self.base / 'home with spaces'
        self.home.mkdir()
        self.repo = self.base / 'checkout'
        self.repo.mkdir()
        shutil.copy2(ROOT / 'install.sh', self.repo / 'install.sh')
        shutil.copytree(ROOT / 'agents', self.repo / 'agents')
        shutil.copytree(ROOT / 'skills', self.repo / 'skills')
        shutil.copytree(ROOT / 'templates', self.repo / 'templates')
        self.env = dict(os.environ, HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / '.config'),
                        XDG_STATE_HOME=str(self.home / '.local/state'), GIT_CONFIG_NOSYSTEM='1',
                        GIT_CONFIG_GLOBAL='/dev/null', GIT_TERMINAL_PROMPT='0', LC_ALL='C')
        for key in list(self.env):
            if key.startswith('GIT_') and key not in ('GIT_CONFIG_NOSYSTEM', 'GIT_CONFIG_GLOBAL', 'GIT_TERMINAL_PROMPT'):
                del self.env[key]
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('add', 'install.sh', 'agents', 'skills', 'templates')
        self.git('commit', '-qm', 'fixture')

    def git(self, *args, check=True):
        return subprocess.run(['git', '-C', str(self.repo), *args], env=self.env,
                              capture_output=True, text=True, check=check)

    def run_installer(self, *args, env=None, script=None, limit=False):
        cmd = ['bash', str(script or self.repo / 'install.sh'), *args]
        if limit:
            cmd = ['bash', '-c', 'ulimit -c 0; ulimit -f 1; exec "$@"', 'limit', *cmd]
        return subprocess.run(cmd, cwd=self.base, env=env or self.env, capture_output=True, text=True)

    def destination(self, runtime, name='athena'):
        prefix = '.claude/agents' if runtime == 'claude' else '.config/opencode/agents'
        return self.home / prefix / (name + '.md')

    def snapshot(self):
        return sorted((str(p.relative_to(self.home)), 'link:' + os.readlink(p) if p.is_symlink()
                       else 'dir' if p.is_dir() else p.read_bytes()) for p in self.home.rglob('*'))

    def apply(self, runtime='claude', *args):
        return self.run_installer('--runtime', runtime, '--apply', *args)

    def assert_failed_unchanged(self, result, before):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_claude_skills_only_copies_two_files(self):
        result = self.run_installer('--runtime', 'claude', '--components', 'skills', '--apply')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        files = sorted(p.relative_to(self.home).as_posix() for p in self.home.rglob('*') if p.is_file())
        self.assertEqual(files, ['.claude/skills/retro/SKILL.md', '.claude/skills/review/SKILL.md'])
        for name in ('retro', 'review'):
            self.assertEqual((self.home / '.claude/skills' / name / 'SKILL.md').read_bytes(),
                             (self.repo / 'skills' / name / 'SKILL.md').read_bytes())

    def test_checkout_path_ending_in_newline_preserves_git_provenance(self):
        renamed = self.base / 'checkout\n'
        self.repo.rename(renamed)
        self.repo = renamed
        revision = self.git('rev-parse', 'HEAD').stdout.strip()
        before = self.snapshot()
        preview = self.run_installer('--runtime', 'both', '--components', 'all', '--dry-run')
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertIn('Source revision: ' + revision + ' (clean)', preview.stdout)
        self.assertEqual(self.snapshot(), before)
        result = self.run_installer('--runtime', 'both', '--components', 'all', '--apply')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Source revision: ' + revision + ' (clean)', result.stdout)
        expected = {}
        for runtime in ('claude', 'opencode'):
            for name in NAMES:
                expected[self.destination(runtime, name)] = self.repo / 'agents' / runtime / (name + '.md')
            prefix = '.claude' if runtime == 'claude' else '.config/opencode'
            for name in ('review', 'retro'):
                expected[self.home / prefix / 'skills' / name / 'SKILL.md'] = self.repo / 'skills' / name / 'SKILL.md'
        expected[self.home / '.local/share/pantheon/templates/pull-request.md'] = self.repo / 'templates/pull-request.md'
        self.assertEqual({p for p in self.home.rglob('*') if p.is_file()}, set(expected))
        for destination, source in expected.items():
            self.assertFalse(destination.is_symlink())
            self.assertEqual(destination.read_bytes(), source.read_bytes())

    def test_checkout_paths_with_multiple_or_inner_newlines(self):
        for name in ('checkout with spaces\n\n', 'checkout\ninner'):
            with self.subTest(name=name):
                renamed = self.base / name
                self.repo.rename(renamed); self.repo = renamed
                revision = self.git('rev-parse', 'HEAD').stdout.strip()
                preview = self.run_installer('--runtime', 'claude', '--components', 'template')
                self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
                self.assertIn('Source revision: ' + revision + ' (clean)', preview.stdout)
                self.assertEqual(self.snapshot(), [])
                result = self.run_installer('--runtime', 'claude', '--components', 'template', '--apply')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('Source revision: ' + revision + ' (clean)', result.stdout)
                self.assertEqual((self.home / '.local/share/pantheon/templates/pull-request.md').read_bytes(),
                                 (self.repo / 'templates/pull-request.md').read_bytes())
                shutil.rmtree(self.home); self.home.mkdir()

    def test_components_selection_and_independent_copies(self):
        for runtime, selection, counts in (
                ('opencode', 'skills', (0, 2, 0)), ('both', 'skills', (0, 4, 0)),
                ('claude', 'template', (0, 0, 1)), ('both', 'template', (0, 0, 1)),
                ('claude', 'template,agents', (9, 0, 1)),
                ('both', 'skills,template', (0, 4, 1)),
                ('claude', 'skills,agents', (9, 2, 0)), ('both', 'all', (18, 4, 1))):
            with self.subTest(runtime=runtime, selection=selection):
                result = self.run_installer('--runtime', runtime, '--components', selection, '--apply')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                files = [p for p in self.home.rglob('*') if p.is_file()]
                self.assertEqual(sum('/agents/' in p.as_posix() for p in files), counts[0])
                self.assertEqual(sum('/skills/' in p.as_posix() for p in files), counts[1])
                self.assertEqual(sum(p.name == 'pull-request.md' for p in files), counts[2])
                for p in files:
                    self.assertFalse(p.is_symlink())
                    if '/skills/' in p.as_posix():
                        self.assertEqual(p.read_bytes(), (self.repo / 'skills' / p.parent.name / 'SKILL.md').read_bytes())
                    if p.name == 'pull-request.md':
                        self.assertEqual(p.read_bytes(), (self.repo / 'templates/pull-request.md').read_bytes())
                shutil.rmtree(self.home); self.home.mkdir()
        result = self.run_installer('--runtime', 'both', '--components', 'skills,template', '--apply')
        self.assertEqual(result.returncode, 0, result.stderr)
        dest = self.home / '.claude/skills/review/SKILL.md'
        template_dest = self.home / '.local/share/pantheon/templates/pull-request.md'
        skill_bytes, template_bytes = dest.read_bytes(), template_dest.read_bytes()
        (self.repo / 'skills/review/SKILL.md').write_bytes(b'changed')
        (self.repo / 'templates/pull-request.md').write_bytes(b'changed')
        self.assertEqual(dest.read_bytes(), skill_bytes)
        self.assertEqual(template_dest.read_bytes(), template_bytes)

    def test_components_invalid_arguments_never_write(self):
        for value in ('', ',agents', 'agents,', 'agents,,skills', 'agents,agents',
                      'all,skills', 'all,all', 'unknown', '*', 'skills, template'):
            with self.subTest(value=value):
                self.assert_failed_unchanged(self.run_installer('--runtime', 'both', '--components', value, '--apply'), [])
        for args in (('--runtime', 'claude', '--components'),
                     ('--runtime', 'claude', '--components', 'skills', '--components', 'skills'),
                     ('--runtime', 'claude', '--runtime', 'both'),
                     ('--runtime', '', '--runtime', 'claude'),
                     ('--runtime', 'claude', '--apply', '--apply'),
                     ('--runtime', 'claude', '--dry-run', '--dry-run'),
                     ('--runtime', 'claude', '--apply', '--backup', '--backup'),
                     ('--runtime', 'claude', '--components', 'template', '--backup'),
                     ('--runtime', 'claude', '--components', 'skills', '--apply', '--dry-run'),
                     ('--components', 'template', '--apply')):
            with self.subTest(args=args):
                self.assert_failed_unchanged(self.run_installer(*args), [])

    def test_component_preview_and_noop_leave_contents_and_timestamps(self):
        for args in (('--runtime', 'both', '--components', 'all'),
                     ('--runtime', 'opencode', '--components', 'skills,template', '--dry-run')):
            result = self.run_installer(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.snapshot(), [])
        self.assertEqual(self.run_installer('--runtime', 'both', '--components', 'all', '--apply').returncode, 0)
        paths = [self.home, *self.home.rglob('*')]
        before = self.snapshot()
        times = {p: p.stat().st_mtime_ns for p in paths}
        for args in (('--runtime', 'both', '--components', 'all'),
                     ('--runtime', 'both', '--components', 'skills,template', '--dry-run'),
                     ('--runtime', 'both', '--components', 'all', '--apply', '--backup')):
            result = self.run_installer(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.snapshot(), before)
            self.assertEqual({p: p.stat().st_mtime_ns for p in paths}, times)
        self.assertFalse((self.home / '.local/state/pantheon/backups').exists())

    def test_component_late_conflict_blocks_all_and_backups_are_distinct(self):
        targets = [self.home / '.claude/skills/review/SKILL.md',
                   self.home / '.config/opencode/skills/review/SKILL.md',
                   self.home / '.local/share/pantheon/templates/pull-request.md']
        targets[-1].parent.mkdir(parents=True); targets[-1].write_bytes(b'late conflict')
        before = self.snapshot()
        self.assert_failed_unchanged(self.run_installer('--runtime', 'both', '--components', 'all', '--apply'), before)
        self.assertFalse(self.destination('claude').exists())
        for i, target in enumerate(targets):
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(('old' + str(i)).encode())
        before = self.snapshot()
        self.assert_failed_unchanged(self.run_installer('--runtime', 'both', '--components', 'all', '--apply'), before)
        self.assertFalse(self.destination('claude').exists())
        for run in range(2):
            if run:
                for i, target in enumerate(targets): target.write_bytes(('old' + str(i)).encode())
            result = self.run_installer('--runtime', 'both', '--components', 'all', '--apply', '--backup')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        root = self.home / '.local/state/pantheon/backups'
        backups = sorted(root.glob('install.*'))
        self.assertEqual(len(backups), 2)
        for directory in backups:
            for relative, expected in (('skills/claude/review/SKILL.md', b'old0'),
                                       ('skills/opencode/review/SKILL.md', b'old1'),
                                       ('template/pull-request.md', b'old2')):
                file = directory / relative
                self.assertEqual(file.read_bytes(), expected)
                self.assertEqual(file.stat().st_mode & 0o777, 0o600)
                self.assertEqual(file.parent.stat().st_mode & 0o777, 0o700)
            self.assertEqual(directory.stat().st_mode & 0o777, 0o700)

    def test_components_custom_xdg_depends_on_actual_opencode_destinations(self):
        env = dict(self.env, XDG_CONFIG_HOME=str(self.base / 'custom'))
        for runtime in ('opencode', 'both'):
            result = self.run_installer('--runtime', runtime, '--components', 'template', '--apply', env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len([p for p in self.home.rglob('*') if p.is_file()]), 1)
            self.assertFalse((self.home / '.config').exists())
            shutil.rmtree(self.home); self.home.mkdir()
            for selection in ('agents', 'skills', 'all'):
                self.assert_failed_unchanged(self.run_installer('--runtime', runtime, '--components', selection,
                                                                '--apply', env=env), [])
            self.assert_failed_unchanged(self.run_installer('--runtime', runtime, '--apply', env=env), [])
        result = self.run_installer('--runtime', 'claude', '--components', 'all', '--apply', env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.base / 'custom').exists())

    def test_new_sources_provenance_and_untracked_extras(self):
        for relative, component in (('skills/review/SKILL.md', 'skills'),
                                    ('templates/pull-request.md', 'template')):
            with self.subTest(relative=relative):
                path = self.repo / relative
                original = path.read_bytes()
                path.write_bytes(b'dirty')
                self.assert_failed_unchanged(self.run_installer('--runtime', 'claude', '--components', component, '--apply'), [])
                path.write_bytes(original)
                self.git('rm', '-q', '--cached', relative); self.git('commit', '-qm', 'untrack source')
                self.assert_failed_unchanged(self.run_installer('--runtime', 'claude', '--components', component, '--apply'), [])
                self.git('add', relative); self.git('commit', '-qm', 'restore source')
        unselected = self.repo / 'templates/pull-request.md'
        original = unselected.read_bytes(); unselected.write_bytes(b'dirty unselected')
        self.assert_failed_unchanged(self.run_installer('--runtime', 'claude', '--components', 'skills', '--apply'), [])
        unselected.write_bytes(original)
        (self.repo / 'skills/extra').mkdir()
        (self.repo / 'skills/extra/SKILL.md').write_bytes(b'extra')
        result = self.run_installer('--runtime', 'both', '--components', 'skills', '--apply')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.home / '.claude/skills/extra').exists())

    def test_new_component_unsafe_paths_and_missing_source_block_preflight(self):
        source = self.repo / 'skills/retro/SKILL.md'
        original = source.read_bytes(); source.unlink()
        self.assert_failed_unchanged(self.run_installer('--runtime', 'both', '--components', 'all', '--dry-run'), [])
        source.symlink_to(self.repo / 'skills/review/SKILL.md')
        self.assert_failed_unchanged(self.run_installer('--runtime', 'both', '--components', 'all', '--dry-run'), [])
        source.unlink(); source.write_bytes(original)
        template = self.repo / 'templates/pull-request.md'
        original = template.read_bytes(); template.unlink()
        self.assert_failed_unchanged(self.run_installer('--runtime', 'both', '--components', 'all', '--dry-run'), [])
        template.symlink_to(self.repo / 'skills/review/SKILL.md')
        self.assert_failed_unchanged(self.run_installer('--runtime', 'both', '--components', 'all', '--dry-run'), [])
        template.unlink(); template.write_bytes(original)
        directory = self.repo / 'skills/retro'; directory.rename(self.repo / 'skills/saved')
        directory.symlink_to(self.repo / 'skills/saved', target_is_directory=True)
        self.assert_failed_unchanged(self.run_installer('--runtime', 'both', '--components', 'all', '--dry-run'), [])
        directory.unlink(); (self.repo / 'skills/saved').rename(directory)
        outside = self.base / 'outside'; outside.mkdir()
        nested = self.home / '.config/opencode/skills/review'
        nested.parent.mkdir(parents=True); nested.symlink_to(outside, target_is_directory=True)
        before = self.snapshot()
        self.assert_failed_unchanged(self.run_installer('--runtime', 'both', '--components', 'all', '--apply'), before)
        self.assertEqual(list(outside.iterdir()), [])
        nested.unlink()
        local = self.home / '.local'; local.symlink_to(outside, target_is_directory=True)
        before = self.snapshot()
        self.assert_failed_unchanged(self.run_installer('--runtime', 'both', '--components', 'all', '--apply'), before)
        self.assertEqual(list(outside.iterdir()), [])

    def test_new_components_newline_home_and_unsafe_backup(self):
        self.home = self.base / 'skills\nhome with spaces'; self.home.mkdir()
        env = dict(self.env, HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / '.config'))
        result = self.run_installer('--runtime', 'both', '--components', 'skills,template', '--apply', env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len([p for p in self.home.rglob('*') if p.is_file()]), 5)
        target = self.home / '.claude/skills/review/SKILL.md'; target.write_bytes(b'old')
        outside = self.base / 'backup-outside'; outside.mkdir()
        state = self.home / '.local/state'; state.symlink_to(outside, target_is_directory=True)
        before = self.snapshot()
        self.assert_failed_unchanged(self.run_installer('--runtime', 'both', '--components', 'skills,template',
                                                       '--apply', '--backup', env=env), before)
        self.assertEqual(list(outside.iterdir()), [])

    def test_new_components_io_failure_reports_partial_progress(self):
        first = self.home / '.claude/skills/review/SKILL.md'
        first.parent.mkdir(parents=True)
        first.write_bytes((self.repo / 'skills/review/SKILL.md').read_bytes())
        second = self.home / '.claude/skills/retro/SKILL.md'
        second.parent.mkdir(parents=True); second.write_bytes(b'old')
        result = self.run_installer('--runtime', 'claude', '--components', 'skills,template',
                                    '--apply', '--backup', limit=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('completed: 1', result.stderr)
        self.assertIn('completed: skills/claude/review/SKILL.md', result.stderr)
        self.assertIn('pending: skills/claude/retro/SKILL.md', result.stderr)
        self.assertIn('pending: template/pull-request.md', result.stderr)
        backups = list((self.home / '.local/state/pantheon/backups').glob('*/skills/claude/retro/SKILL.md'))
        self.assertEqual([p.read_bytes() for p in backups], [b'old'])
        self.assertEqual(second.read_bytes(), b'old')
        self.assertNotIn('Apply complete', result.stdout)

    def test_selection_copies_exactly_selected_agents_and_is_independent(self):
        for runtime in ('claude', 'opencode', 'both'):
            with self.subTest(runtime=runtime):
                result = self.apply(runtime)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(self.git('rev-parse', 'HEAD').stdout.strip(), result.stdout)
                for selected in ('claude', 'opencode'):
                    expected = runtime in (selected, 'both')
                    for name in NAMES:
                        dst = self.destination(selected, name)
                        self.assertEqual(dst.exists(), expected)
                        if expected:
                            self.assertEqual(dst.read_bytes(), (self.repo / 'agents' / selected / (name + '.md')).read_bytes())
                    if expected:
                        self.assertEqual(len(list(self.destination(selected).parent.iterdir())), 9)
                shutil.rmtree(self.home)
                self.home.mkdir()
        self.assertEqual(self.apply().returncode, 0)
        source = self.repo / 'agents/claude/athena.md'
        old = self.destination('claude').read_bytes()
        source.write_bytes(b'changed after installation')
        self.assertEqual(self.destination('claude').read_bytes(), old)

    def test_bad_arguments_and_preview_do_not_write(self):
        for args in ((), ('--runtime', 'bad'), ('--runtime',), ('--runtime', 'claude', '--backup'),
                     ('--runtime', 'both', '--apply', '--dry-run'), ('--unknown',)):
            with self.subTest(args=args):
                self.assert_failed_unchanged(self.run_installer(*args), [])
        for runtime in ('claude', 'opencode', 'both'):
            result = self.run_installer('--runtime', runtime)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.snapshot(), [])

    def test_relative_executable_invocation_from_checkout(self):
        result = subprocess.run(['./install.sh', '--runtime', 'claude', '--dry-run'], cwd=self.repo,
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.snapshot(), [])

    def test_late_conflict_blocks_both_and_identical_noop(self):
        dst = self.destination('opencode', 'thor')
        dst.parent.mkdir(parents=True)
        dst.write_bytes(b'conflict')
        before = self.snapshot()
        preview = self.run_installer('--runtime', 'both', '--dry-run')
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assert_failed_unchanged(self.apply('both'), before)
        self.assertFalse(self.destination('claude').exists())
        dst.unlink()
        self.assertEqual(self.apply('both').returncode, 0)
        before = self.snapshot()
        result = self.apply('both', '--backup')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_backups_are_unique_private_and_exact(self):
        dst = self.destination('claude')
        dst.parent.mkdir(parents=True)
        backup_root = self.home / '.local/state/pantheon/backups'
        for content in (b'old one', b'old two'):
            dst.write_bytes(content)
            result = self.apply('claude', '--backup')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(dst.read_bytes(), (self.repo / 'agents/claude/athena.md').read_bytes())
        backups = list(backup_root.glob('*/claude/athena.md'))
        self.assertEqual(len(backups), 2)
        self.assertEqual({p.read_bytes() for p in backups}, {b'old one', b'old two'})
        for p in backups:
            self.assertEqual(p.stat().st_mode & 0o777, 0o600)
            self.assertEqual(p.parent.stat().st_mode & 0o777, 0o700)
            self.assertEqual(p.parent.parent.stat().st_mode & 0o777, 0o700)

    def test_unsafe_sources_destinations_and_backup_components_block(self):
        source = self.repo / 'agents/opencode/thor.md'
        for kind in ('missing', 'directory', 'symlink', 'source_ancestor'):
            with self.subTest(kind=kind):
                if kind == 'source_ancestor':
                    folder = source.parent
                    folder.rename(folder.with_name('saved'))
                    folder.symlink_to(folder.with_name('saved'), target_is_directory=True)
                else:
                    saved = source.read_bytes()
                    source.unlink()
                    if kind == 'directory': source.mkdir()
                    if kind == 'symlink': source.symlink_to(self.repo / 'agents/claude/thor.md')
                before = self.snapshot()
                self.assert_failed_unchanged(self.run_installer('--runtime', 'both', '--dry-run'), before)
                before = self.snapshot()
                self.assert_failed_unchanged(self.apply('both', '--backup'), before)
                if kind == 'source_ancestor':
                    folder.unlink(); folder.with_name('saved').rename(folder)
                else:
                    if kind == 'directory': source.rmdir()
                    if kind == 'symlink': source.unlink()
                    source.write_bytes(saved)
        dst = self.destination('opencode', 'thor')
        dst.parent.mkdir(parents=True)
        for kind in ('symlink', 'directory'):
            if kind == 'symlink': dst.symlink_to(self.repo / 'agents/claude/thor.md')
            else: dst.mkdir()
            before = self.snapshot()
            self.assert_failed_unchanged(self.apply('both'), before)
            if kind == 'symlink': dst.unlink()
            else: dst.rmdir()
        shutil.rmtree(self.home / '.config')
        (self.home / '.config').symlink_to(self.base, target_is_directory=True)
        before = self.snapshot()
        self.assert_failed_unchanged(self.apply('both'), before)
        (self.home / '.config').unlink()
        (self.home / '.local').symlink_to(self.base, target_is_directory=True)
        before = self.snapshot()
        self.assert_failed_unchanged(self.apply('claude', '--backup'), before)

    def test_newline_home_cannot_hide_symlink_in_destination_or_backup(self):
        for kind in ('claude', 'opencode', 'backup'):
            with self.subTest(kind=kind):
                self.home = self.base / ('home\n' + kind)
                self.home.mkdir()
                outside = self.base / ('outside-' + kind)
                outside.mkdir()
                env = dict(self.env, HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / '.config'),
                           XDG_STATE_HOME=str(self.home / '.local/state'))
                if kind == 'backup':
                    dst = self.destination('claude')
                    dst.parent.mkdir(parents=True)
                    dst.write_bytes(b'previous content')
                    link = self.home / '.local'
                    args = ('--runtime', 'claude', '--apply', '--backup')
                else:
                    link = self.home / ('.claude' if kind == 'claude' else '.config')
                    args = ('--runtime', kind, '--apply')
                link.symlink_to(outside, target_is_directory=True)
                before = self.snapshot()
                result = self.run_installer(*args, env=env)
                escaped = list(outside.rglob('*'))
                self.assertEqual(escaped, [],
                                 f'{kind}: writes escaped into sandbox outside HOME; exit={result.returncode}')
                self.assert_failed_unchanged(result, before)

    def test_newline_home_without_symlinks_supports_install_and_backup(self):
        self.home = self.base / 'safe\nhome with spaces'
        self.home.mkdir()
        env = dict(self.env, HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / '.config'),
                   XDG_STATE_HOME=str(self.home / '.local/state'))
        result = self.run_installer('--runtime', 'both', '--apply', env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        for runtime in ('claude', 'opencode'):
            self.assertEqual(self.destination(runtime).read_bytes(),
                             (self.repo / 'agents' / runtime / 'athena.md').read_bytes())
        self.destination('claude').write_bytes(b'old bytes')
        result = self.run_installer('--runtime', 'claude', '--apply', '--backup', env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        backups = list((self.home / '.local/state/pantheon/backups').glob('*/claude/athena.md'))
        self.assertEqual([p.read_bytes() for p in backups], [b'old bytes'])

    def test_git_provenance_and_untracked_extras(self):
        source = self.repo / 'agents/claude/athena.md'
        source.write_bytes(b'dirty')
        self.assert_failed_unchanged(self.apply(), [])
        preview = self.run_installer('--runtime', 'claude')
        self.assertEqual(preview.returncode, 0); self.assertIn('dirty', preview.stdout)
        self.git('add', 'agents/claude/athena.md')
        self.assert_failed_unchanged(self.apply(), [])
        self.git('reset', '--hard', '-q', 'HEAD')
        self.git('rm', '-q', '--cached', 'agents/claude/athena.md')
        self.git('commit', '-qm', 'untrack source')
        self.assert_failed_unchanged(self.apply(), [])
        self.git('add', 'agents/claude/athena.md')
        self.git('commit', '-qm', 'restore source')
        self.git('rm', '-q', '--cached', 'install.sh')
        self.git('commit', '-qm', 'untrack script')
        self.assert_failed_unchanged(self.apply(), [])
        self.git('add', 'install.sh'); self.git('commit', '-qm', 'restore script')
        (self.repo / 'agents/claude/extra.md').write_bytes(b'extra')
        self.assertEqual(self.apply().returncode, 0)
        self.assertFalse(self.destination('claude', 'extra').exists())

    def test_hidden_tracked_changes_block_apply_without_altering_index_flags(self):
        path = 'agents/opencode/thor.md'  # Not selected by the Claude-only install.
        source = self.repo / path
        for flag in ('assume-unchanged', 'skip-worktree'):
            with self.subTest(flag=flag):
                original = source.read_bytes()
                self.git('update-index', '--' + flag, '--', path)
                source.write_bytes(b'hidden tracked modification')
                try:
                    self.assertEqual(self.git('diff', '--quiet', 'HEAD', '--', check=False).returncode, 0)
                    flag_before = self.git('ls-files', '-v', '--', path).stdout
                    index_before = (self.repo / '.git/index').read_bytes()
                    result = self.apply('claude')
                    flag_after = self.git('ls-files', '-v', '--', path).stdout
                    self.assertEqual(flag_after, flag_before)
                    self.assertEqual((self.repo / '.git/index').read_bytes(), index_before)
                    self.assert_failed_unchanged(result, [])
                finally:
                    self.git('update-index', '--no-' + flag, '--', path)
                    source.write_bytes(original)
                    shutil.rmtree(self.home)
                    self.home.mkdir()

    def test_flags_block_even_identical_bytes_with_special_tracked_filename(self):
        path = 'tracked\nname with spaces.md'
        (self.repo / path).write_bytes(b'unchanged')
        self.git('add', '--', path)
        self.git('commit', '-qm', 'special filename')
        self.assertEqual(self.apply('claude').returncode, 0)
        shutil.rmtree(self.home)
        self.home.mkdir()
        for flag in ('assume-unchanged', 'skip-worktree'):
            with self.subTest(flag=flag):
                self.git('update-index', '--' + flag, '--', path)
                before = (self.repo / '.git/index').read_bytes()
                try:
                    preview = self.run_installer('--runtime', 'claude', '--dry-run')
                    self.assertEqual(preview.returncode, 0, preview.stderr)
                    self.assertIn('unknown', preview.stdout)
                    self.assert_failed_unchanged(self.apply('claude'), [])
                    self.assertEqual((self.repo / '.git/index').read_bytes(), before)
                finally:
                    self.git('update-index', '--no-' + flag, '--', path)
                    shutil.rmtree(self.home)
                    self.home.mkdir()

    def test_missing_git_metadata_parent_repo_and_no_git(self):
        path = self.base / 'bin'; path.mkdir()
        for name in ('bash', 'dirname', 'cmp'):
            (path / name).symlink_to(shutil.which(name))
        env = dict(self.env, PATH=str(path))
        self.assert_failed_unchanged(self.run_installer('--runtime', 'claude', '--apply', env=env), [])
        preview = self.run_installer('--runtime', 'claude', env=env)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertIn('unknown', preview.stdout)
        shutil.rmtree(self.repo / '.git')
        self.assert_failed_unchanged(self.apply(), [])
        self.git('init', '-q')
        self.assert_failed_unchanged(self.apply(), [])
        shutil.rmtree(self.repo / '.git')
        subprocess.run(['git', 'init', '-q', str(self.base)], env=self.env, check=True)
        subprocess.run(['git', '-C', str(self.base), '-c', 'user.name=Fixture', '-c',
                        'user.email=fixture@example.invalid', 'commit', '--allow-empty', '-qm', 'parent'],
                       env=self.env, check=True)
        self.assert_failed_unchanged(self.apply(), [])

    def test_custom_xdg_and_fixed_backup_root(self):
        env = dict(self.env, XDG_CONFIG_HOME=str(self.base / 'custom'), XDG_STATE_HOME=str(self.base / 'other-state'))
        for runtime in ('opencode', 'both'):
            self.assert_failed_unchanged(self.run_installer('--runtime', runtime, '--apply', env=env), [])
        dst = self.destination('claude'); dst.parent.mkdir(parents=True); dst.write_bytes(b'old')
        result = self.run_installer('--runtime', 'claude', '--apply', '--backup', env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list((self.home / '.local/state/pantheon/backups').glob('*/claude/athena.md'))), 1)
        self.assertFalse((self.base / 'other-state').exists())

    def test_real_io_failure_reports_partial_progress_and_backup(self):
        first = self.destination('claude', 'athena'); first.parent.mkdir(parents=True)
        first.write_bytes((self.repo / 'agents/claude/athena.md').read_bytes())
        second = self.destination('claude', 'heimdall'); second.write_bytes(b'old')
        result = self.run_installer('--runtime', 'claude', '--apply', '--backup', limit=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('completed: 1', result.stderr)
        self.assertIn('completed: claude/athena.md', result.stderr)
        self.assertIn('pending: claude/thor.md', result.stderr)
        self.assertIn('claude/heimdall.md', result.stderr)
        backups = list((self.home / '.local/state/pantheon/backups').glob('*/claude/heimdall.md'))
        self.assertEqual([p.read_bytes() for p in backups], [b'old'])
        self.assertEqual(second.read_bytes(), b'old')
        self.assertNotIn('Apply complete', result.stdout)


if __name__ == '__main__':
    unittest.main()
