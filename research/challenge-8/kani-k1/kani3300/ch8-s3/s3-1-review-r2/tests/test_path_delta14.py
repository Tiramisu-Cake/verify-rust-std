"""Independent bounded service checks; native execution comes only from fixture mocks."""
import copy
import unittest
from pathlib import Path
from unittest import mock
import test_s3_paths as author
import test_s3 as fixtures
import runner as r
import s3_campaign as c
import s3_evidence as ev


class IndependentPathDelta(unittest.TestCase):
    def test_alias_retarget_after_e0_uses_original_canonical_directory(self):
        helper = author.RealPathWriterTests()
        with helper.fixture('alias') as fix:
            root, std, tool, out, req, arg, launches, commands = fix
            capture = c.snapshots.capture
            seen = []

            def boundary(std_arg, tool_arg, request, context, epoch, shutdown=None):
                self.assertEqual(tool_arg, tool)
                seen.append(epoch)
                result = capture(std_arg, tool_arg, request, context, epoch, shutdown)
                if epoch == 'E0':
                    (root / 'alias').unlink()
                    (root / 'alias').symlink_to(root / 'wrong', target_is_directory=True)
                return result

            with mock.patch.object(c.snapshots, 'capture', side_effect=boundary):
                code, terminal = helper.run_fixture(fix)
            self.assertEqual(code, 0, terminal['stop_reason'])
            self.assertEqual(seen[0], 'E0')
            self.assertEqual(len(seen), 19)
            helper.equal_captures(fix)
            helper.portable(fix)
            self.assertEqual((root / 'alias').resolve(), root / 'wrong')

    def test_same_hash_path_changes_and_required_shape_matrix(self):
        helper = author.RealPathWriterTests()
        with helper.fixture() as fix:
            self.assertEqual(helper.run_fixture(fix)[0], 0)
            root, std, tool, out, req, *_ = fix
            rid = c.p.ORDER[0]
            original = c.read(out / 'groups' / ('s3-' + rid) / 'receipt.json')
            baseline = c.read(out / 'baseline.json')
            request_hash = r.sha256(r.REQUEST_PATH)
            supervision = fixtures.supervision()
            original_bytes = (out / 'groups' / ('s3-' + rid) / 'receipt.json').read_bytes()
            count = 0
            for state in ('COMPLETE', 'FAILED', 'IN_PROGRESS', 'INTERRUPTED'):
                for stage in ('before', 'after'):
                    for name in ('kani_driver', 'kani_compiler', 'cbmc'):
                        for variant in ('other_absolute', 'relative'):
                            doc = copy.deepcopy(original)
                            doc['state'] = state
                            item = doc['tool_fingerprints_' + stage]['binaries'][name]
                            before_hash = item['sha256']
                            item['path'] = (str(root / 'wrong' / Path(item['path']).name)
                                            if variant == 'other_absolute' else Path(item['path']).name)
                            self.assertEqual(item['sha256'], before_hash)
                            with self.subTest(state=state, stage=stage, name=name, variant=variant):
                                with self.assertRaisesRegex(ev.EvidenceError, 'recorded worker binary drift'):
                                    ev.protected(doc, req, baseline, supervision, request_hash)
                            count += 1
            self.assertEqual(count, 48)
            count = 0
            for stage in ('before', 'after'):
                for field, value in (('state', 'INCOMPLETE'), ('snapshot_completed', False),
                                     ('required_hashes_present', False), ('missing_binaries', ['kani_driver']),
                                     ('error', 'EACCES'), ('binaries', None)):
                    doc = copy.deepcopy(original)
                    doc['tool_fingerprints_' + stage][field] = value
                    with self.subTest(stage=stage, field=field), self.assertRaises(ev.EvidenceError):
                        ev.protected(doc, req, baseline, supervision, request_hash)
                    count += 1
            self.assertEqual(count, 12)
            self.assertEqual((out / 'groups' / ('s3-' + rid) / 'receipt.json').read_bytes(), original_bytes)

    def test_missing_binary_at_entry_never_launches_worker(self):
        helper = author.RealPathWriterTests()
        with helper.fixture() as fix:
            (fix[2] / 'target/kani/bin/kani-driver').unlink()
            code, terminal = helper.run_fixture(fix)
            self.assertEqual(code, 1)
            self.assertIn('baseline_snapshot_incomplete', terminal['stop_reason'])
            self.assertEqual(fix[6], [])
            self.assertEqual(terminal['s3_campaign']['completed'], [])
            self.assertTrue(all(row['status'] == 'NOT_RUN' for row in terminal['rows']))


if __name__ == '__main__':
    unittest.main()
