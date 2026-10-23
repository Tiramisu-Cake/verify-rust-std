"""Synthetic Git-repository tests for exact tracked symlink validation."""

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

MODULE = Path(__file__).with_name('verify_inputs.py')
spec = importlib.util.spec_from_file_location('verify_inputs_under_test', MODULE)
verify_inputs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_inputs)


def run_git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


class VerifyInputSymlinkTests(unittest.TestCase):
    def make_repo(self, target='../.agents/skills'):
        temp = tempfile.TemporaryDirectory(prefix='rr-input-link-')
        repo = Path(temp.name) / 'repo'
        repo.mkdir()
        (repo / '.claude').mkdir()
        (repo / '.agents/skills').mkdir(parents=True)
        (repo / '.agents/skills/SKILL.md').write_text('synthetic skill bytes\n')
        (repo / '.claude/skills').symlink_to(target)
        run_git(repo, 'init', '-q')
        run_git(repo, 'config', 'user.email', 'synthetic@example.invalid')
        run_git(repo, 'config', 'user.name', 'Synthetic Test')
        run_git(repo, 'add', '--', '.claude', '.agents')
        run_git(repo, 'commit', '-qm', 'synthetic fixture')
        pin = {'commit': run_git(repo, 'rev-parse', 'HEAD').decode().strip(),
               'tree': run_git(repo, 'rev-parse', 'HEAD:').decode().strip(),
               'verify_paths': [''], 'gitlinks': {}}
        return temp, repo, pin

    def bypass_status_only(self, repo, *args):
        if args and args[0] == 'status':
            return b''
        return run_git(repo, *args)

    def assert_rejected(self, repo, pin, pattern, bypass_status=False):
        implementation = (lambda _repo, *args: self.bypass_status_only(_repo, *args)) if bypass_status else None
        if implementation:
            with patch.object(verify_inputs, 'git', side_effect=implementation):
                with self.assertRaisesRegex(ValueError, pattern):
                    verify_inputs.verify_checkout(repo, pin)
        else:
            with self.assertRaisesRegex(ValueError, pattern):
                verify_inputs.verify_checkout(repo, pin)

    def test_exact_git_symlink_mode_blob_and_bytes_pass_without_dereference(self):
        temp, repo, pin = self.make_repo()
        with temp:
            entry = verify_inputs.verify_checkout(repo, pin)['byte_inventory']['.claude/skills']
            self.assertEqual(entry['mode'], '120000')
            self.assertEqual(entry['git_blob'], run_git(repo, 'rev-parse', 'HEAD:.claude/skills').decode().strip())
            self.assertEqual(entry['bytes'], len(b'../.agents/skills'))
            self.assertNotIn('sha256', entry)

    def test_escaping_symlink_target_is_rejected_lexically(self):
        temp, repo, pin = self.make_repo('../../../../outside')
        with temp:
            self.assert_rejected(repo, pin, 'escapes checkout')

    def test_tampered_symlink_target_bytes_are_rejected(self):
        temp, repo, pin = self.make_repo()
        with temp:
            link = repo / '.claude/skills'
            link.unlink()
            link.symlink_to('../.agents/changed')
            self.assert_rejected(repo, pin, 'target/blob mismatch', bypass_status=True)

    def test_missing_tracked_symlink_is_rejected(self):
        temp, repo, pin = self.make_repo()
        with temp:
            (repo / '.claude/skills').unlink()
            self.assert_rejected(repo, pin, 'pristine|missing or non-symlink', bypass_status=True)

    def test_swapped_symlink_parent_is_rejected_even_when_target_stays_inside(self):
        temp, repo, pin = self.make_repo()
        with temp:
            (repo / '.claude').rename(repo / 'claude-real')
            (repo / '.claude').symlink_to('claude-real')
            self.assert_rejected(repo, pin, 'swapped symlink parent', bypass_status=True)

    def test_regular_tracked_bytes_and_execution_mode_remain_checked(self):
        temp, repo, pin = self.make_repo()
        with temp:
            path = repo / '.agents/skills/SKILL.md'
            path.write_text('tampered bytes\n')
            self.assert_rejected(repo, pin, 'byte/mode mismatch', bypass_status=True)
            path.write_text('synthetic skill bytes\n')
            path.chmod(0o755)
            self.assert_rejected(repo, pin, 'byte/mode mismatch', bypass_status=True)

    def test_unsupported_tracked_mode_is_rejected(self):
        temp, repo, pin = self.make_repo()
        with temp:
            original = verify_inputs.git

            def unsupported(_repo, *args):
                value = self.bypass_status_only(_repo, *args)
                if args[:3] == ('ls-tree', '-r', '-z'):
                    value = value.replace(b'120000 blob ', b'100664 blob ')
                return value

            with patch.object(verify_inputs, 'git', side_effect=unsupported):
                with self.assertRaisesRegex(ValueError, 'unsupported/missing tracked source mode'):
                    verify_inputs.verify_checkout(repo, pin)


if __name__ == '__main__':
    unittest.main()
