"""Adversarial offline acceptance checks; no proof execution."""
import copy
import unittest

import replay


class FailClosedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = replay.RUN / 'evidence/cell-u34'
        cls.h = replay.read(directory / 'export.json')['harnesses'][0]
        cls.hp = next(h['properties'] for h in replay.read(directory / 'properties.json')['harnesses'] if h['name'] == cls.h['name'])
        cls.policy = replay.read(replay.BASELINE / 'LOCATION-POLICY.json')
        cls.missing = dict(cls.policy['records'][0], file=None, line=None)
        cls.snapshot = replay.read(directory / 'receipt.json')['tool_fingerprints_before']

    def test_inventory_fixture(self):
        self.assertEqual(len(replay.inventory(self.h, self.hp)), self.h['n_properties'])

    def test_missing_null_wrong_type_inventory_is_rejected(self):
        for properties in (None, {}, [], [None]):
            with self.assertRaises(ValueError):
                replay.inventory(self.h, properties)

    def test_duplicate_or_missing_property_is_rejected(self):
        for hp in (self.hp + [self.hp[0]], self.hp[:-1]):
            with self.assertRaises(ValueError):
                replay.inventory(self.h, hp)

    def test_unknown_status_cannot_hide_in_success_count(self):
        hp = copy.deepcopy(self.hp)
        hp[0]['status'] = 'NOT_RUN'
        with self.assertRaises(ValueError):
            replay.inventory(self.h, hp)

    def test_cover_class_cannot_be_relabelled_as_success(self):
        hp = copy.deepcopy(self.hp)
        next(p for p in hp if p['class'] == 'cover')['class'] = 'assertion'
        with self.assertRaises(ValueError):
            replay.inventory(self.h, hp)

    def test_failed_verdict_cannot_be_overridden_by_group_success(self):
        h = copy.deepcopy(self.h)
        h['outcome']['verdict'] = 'FAILURE'
        with self.assertRaises(ValueError):
            replay.inventory(h, self.hp)

    def test_approved_location_tuple_preserves_null_coordinates(self):
        self.assertTrue(replay.location_exception(self.missing, self.policy))
        self.assertIsNone(self.missing['file'])
        self.assertIsNone(self.missing['line'])

    def test_exception_does_not_admit_failure_or_unreachable_status(self):
        for status in ('FAILURE', 'UNREACHABLE', 'UNKNOWN', None):
            self.assertFalse(replay.location_exception(dict(self.missing, status=status), self.policy))

    def test_exception_cannot_be_extended_to_other_id_or_role(self):
        for change in ({'id': self.missing['id'] + 'x'}, {'class': 'assertion'}, {'description': 'postcondition'}, {'location_display': 'library/core/src/lib.rs:1:1'}, {'selector': 'another_harness'}, {'file': 'invented.rs'}, {'line': '0'}):
            self.assertFalse(replay.location_exception(dict(self.missing, **change), self.policy))

    def test_even_modified_allowlist_cannot_add_third_id(self):
        record = dict(self.missing, id='other.unreachable.1')
        policy = {'records': [record]}
        self.assertFalse(replay.location_exception(record, policy))

    def test_source_after_cannot_replace_missing_binary_after(self):
        for after in (None, {}, [], {'binaries': None}, {'binaries': {}, 'required_hashes_present': True}):
            self.assertEqual(replay.binary_state(self.snapshot, after), 'UNKNOWN_MISSING_REQUIRED_SNAPSHOT')

    def test_required_binary_missing_or_null_fails_closed(self):
        for value in (None, {}, {'sha256': 'a' * 64}):
            after = copy.deepcopy(self.snapshot)
            after['binaries']['kani_compiler'] = value
            self.assertEqual(replay.binary_state(self.snapshot, after), 'UNKNOWN_MISSING_REQUIRED_SNAPSHOT')

    def test_binary_drift_not_accepted(self):
        after = copy.deepcopy(self.snapshot)
        after['binaries']['cbmc']['sha256'] = '0' * 64
        self.assertEqual(replay.binary_state(self.snapshot, after), 'UNKNOWN_BINARY_DRIFT')

    def test_same_fixed_required_binary_hashes_match(self):
        self.assertEqual(replay.binary_state(self.snapshot, copy.deepcopy(self.snapshot)), 'MATCH')

    def test_activation_variants_require_group_scoped_inventory(self):
        import pfc
        request = replay.read(replay.RUN / 'CI-REQUEST.json')
        group_for = {rid: g['id'] for g in request['execution_groups'] for rid in g['row_ids']}
        counts = {}
        for rid in ('activation-default', 'activation-override', 'stable_default_activation-legal', 'stable_freeze_activation-legal'):
            row = next(r for r in request['rows'] if r['id'] == rid)
            props, _, harness, _ = pfc._property_inventory(replay.RUN, group_for[rid], row['selector'])
            self.assertEqual(len(props), harness['n_properties'])
            counts[rid] = len(props)
        self.assertEqual(counts, {'activation-default': 183, 'activation-override': 371, 'stable_default_activation-legal': 207, 'stable_freeze_activation-legal': 395})

    def test_negative_oracle_rejects_an_additional_failure(self):
        directory = replay.RUN / 'evidence/light-corruption-u4'
        request = replay.read(replay.RUN / 'CI-REQUEST.json')
        row = next(r for r in request['rows'] if r['id'] == 'order_corruption_rejected')
        harness = next(h for h in replay.read(directory / 'export.json')['harnesses'] if h['name'] == row['selector'])
        properties = next(h['properties'] for h in replay.read(directory / 'properties.json')['harnesses'] if h['name'] == row['selector'])
        by = {p['id']: p for p in properties}
        self.assertEqual(replay.negative_oracle(row, harness, by, request)['binding'], 'EXACT_PREDECLARED_SOLE_FAILURE')
        bad = copy.deepcopy(harness)
        bad['checks']['failure'].append('unrelated.assertion.1')
        with self.assertRaises(ValueError):
            replay.negative_oracle(row, bad, by, request)

    def test_core_helper_name_never_exempts_unreachable_check(self):
        import unreachable
        record = {'line': '820', 'description': 'attempt to shift left with overflow'}
        decision, _ = unreachable._site_decision('DEPENDENCY_ASSERTION', record, {}, 'library/core/src/fmt/mod.rs', 'fmt::Arguments::from_str', {})
        self.assertTrue(decision.startswith('UNKNOWN'))

    def test_pinned_source_reference_is_stable_across_instances(self):
        import pfc
        relative = 'library/core/src/slice/sort/shared/smallsort.rs'
        first = pfc._GitFile(replay.STD, replay.SOURCE_SHA, relative)
        second = pfc._GitFile(replay.STD, replay.SOURCE_SHA, relative)
        self.assertEqual(str(first), str(second))
        self.assertEqual(str(first), 'git:' + replay.SOURCE_SHA + ':' + relative)

    def test_N0_does_not_exclude_post_count_loop_on_length_one_canary(self):
        import unreachable
        path = 'library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs'
        for line in ('106', '111', '112', '113', '118'):
            record = {'line': line, 'description': 'index out of bounds: the length is less than or equal to the given index'}
            decision, _ = unreachable._site_decision('POST_PREDICATE_SAFETY_CHECK', record, {'N': 0}, path, 'active_post', {})
            self.assertEqual(decision, 'UNKNOWN_OBLIGATION_BINDING')


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.rec = replay.read(replay.RUN / 'evidence/cell-u34/receipt.json')

    def test_complete_same_invocation_snapshot(self):
        self.assertEqual(replay.snapshot_gate(self.rec), 'MATCH')

    def test_before_snapshot_cannot_be_reused_as_after(self):
        self.rec['tool_fingerprints_after'] = copy.deepcopy(self.rec['tool_fingerprints_before'])
        self.assertNotEqual(replay.snapshot_gate(self.rec), 'MATCH')

    def test_missing_null_wrong_type_completion(self):
        for value in (None, False, 1, 'true'):
            self.rec['tool_fingerprints_after']['snapshot_completed'] = value
            self.assertNotEqual(replay.snapshot_gate(self.rec), 'MATCH')

    def test_unverified_child_shutdown(self):
        for value in (None, False, 1):
            self.rec['execution']['child_shutdown_verified'] = value
            self.assertNotEqual(replay.snapshot_gate(self.rec), 'MATCH')

    def test_snapshot_errors_or_missing_error_field(self):
        for value in (None, ['IOError'], {}):
            self.rec['snapshot_errors'] = value
            self.assertNotEqual(replay.snapshot_gate(self.rec), 'MATCH')


class NativeMetadataTests(unittest.TestCase):
    def setUp(self):
        import native
        self.native = native
        self.entry = replay.read(replay.RUN / 'evidence/cell-u34/binding-metadata.json')['native_metadata'][0]

    def test_original_bytes_hash_and_json(self):
        _, checks = self.native._records(self.entry)
        self.assertTrue(checks['sha256_valid'] and checks['bytes_valid'] and checks['json_valid'])

    def test_altered_native_bytes_are_rejected(self):
        _, checks = self.native._records(dict(self.entry, text=self.entry['text'] + ' '))
        self.assertFalse(checks['sha256_valid'])

    def test_valid_digest_does_not_accept_non_object_json(self):
        for raw in ('null', '[]', '{"proof_harnesses":[null]}'):
            _, checks = self.native._records(dict(self.entry, text=raw, bytes=len(raw), sha256=replay.digest(raw.encode())))
            self.assertFalse(checks['json_valid'])

    def test_pointer_cannot_use_python_negative_or_noncanonical_index(self):
        for index in ('-1', '01', '+0', '1'):
            self.assertIsNone(self.native._pointer({'rows': ['only']}, '/rows/' + index))
        self.assertEqual(self.native._pointer({'rows': ['only']}, '/rows/0'), 'only')


if __name__ == '__main__':
    unittest.main()
