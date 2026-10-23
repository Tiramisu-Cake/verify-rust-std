"""Synthetic N8 admission/configuration tests; no Cloud or proof tools."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rr_lane
import control


def profile():
    value = json.loads((Path(__file__).parent / 'network-rr/RR-G1-PROFILE-20261024-N8.json').read_text())
    value.update(authorization_phase_id=rr_lane.PHASE, proof_credit=False,
                 independent_credit=False, profile_accepted=False)
    value['std_source']['selected_baseline'] = 'cd371e035c7e573760c43bf934d53e8118ee3e7d'
    value['image_build'].update(cold_executor=rr_lane.COLD_EXECUTOR,
        machine_type_cold='E2_HIGHCPU_8', machine_type_warm='E2_STANDARD_2',
        image_digest=rr_lane.REPOSITORY + '@sha256:' + 'a' * 64,
        image_receipt_sha256='b' * 64, cold_build_id='01234567-1234-1234-1234-012345678901')
    return value


class RRLaneTests(unittest.TestCase):
    def test_cold_setup_repair_may_reduce_machine_without_shortening_timeout(self):
        p = profile()
        p['image_build']['machine_type_cold'] = 'E2_STANDARD_2'
        self.assertEqual(rr_lane.machine_type(p, 'cold-image'), 'E2_STANDARD_2')
        self.assertEqual(rr_lane.profile_gate(p, 'cold-image', 1740), rr_lane.COLD_EXECUTOR)
        for stage, key, value in [('cold-image', 'machine_type_cold', 'E2_HIGHCPU_32'),
                                  ('cold-image', 'machine_type_cold', None),
                                  ('warm-g1', 'machine_type_warm', 'E2_HIGHCPU_8')]:
            bad = copy.deepcopy(p); bad['image_build'][key] = value
            with self.subTest(stage=stage, value=value), self.assertRaises(ValueError):
                rr_lane.profile_gate(bad, stage, rr_lane.TIMEOUTS[stage])

    def test_exact_stage_images_and_timeouts(self):
        p = profile()
        self.assertEqual(rr_lane.profile_gate(p, 'cold-image', 1740), rr_lane.COLD_EXECUTOR)
        self.assertEqual(rr_lane.profile_gate(p, 'warm-g1', 1200), p['image_build']['image_digest'])
        for stage, seconds in [('cold-image', 1739), ('warm-g1', 1199), ('NOT_RUN', 1200),
                               (None, 1740), ('warm-g1', True)]:
            with self.subTest(stage=stage, seconds=seconds), self.assertRaises(ValueError):
                rr_lane.profile_gate(p, stage, seconds)

    def test_partial_null_missing_wrong_type_and_foreign_identity_refused(self):
        for key, bad in [('image_digest', None), ('image_digest', 'tag:latest'),
                         ('image_digest', 'foreign@sha256:' + 'a' * 64),
                         ('image_receipt_sha256', None), ('cold_build_id', []),
                         ('cold_executor', control.SDK)]:
            p = profile(); p['image_build'][key] = bad
            with self.subTest(key=key, bad=bad), self.assertRaises(ValueError):
                rr_lane.profile_gate(p, 'warm-g1', 1200)
        for section, key, bad in [('tool', 'patched', True), ('tool', 'source_commit', '0' * 40),
                                 ('std_source', 'selected_baseline', '0' * 40),
                                 ('compiler', 'channel', 'other')]:
            p = profile(); p[section][key] = bad
            with self.subTest(section=section, key=key), self.assertRaises(ValueError):
                rr_lane.profile_gate(p, 'cold-image', 1740)
        for bad in (None, [], 'profile', {'image_build': None}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                rr_lane.profile_gate(bad, 'warm-g1', 1200)

    def cold_fixture(self, *, state='STARTED', status='FAILURE', build_id=None, source='old'):
        p = profile()
        build = {'stage': 'cold-image', 'accounted': True, 'status': status,
                 'build_id': build_id or p['image_build']['cold_build_id'], 'infra_sha': source}
        if state == 'NOT_STARTED':
            build.update(status='EXPIRED', execution_seconds=0)
            evidence = {'kind': 'BUILD_METADATA_ZERO_EXECUTION'}
        else:
            evidence = {'kind': 'EVIDENCE_BRIEF', 'exact': True, 'archive_sha256': 'a' * 64,
                        'index_sha256': 'b' * 64, 'file_sha256': 'c' * 64,
                        'file_id': 'synthetic-file', 'selector': {'start': 1, 'end': 1}}
        record = {'build_id': build['build_id'], 'source_commit': source,
                  'stage': 'cold-image', 'state': state, 'evidence': evidence}
        return build, record

    def test_infrastructure_failures_have_no_submit_count_limit(self):
        builds, records = [], {}
        for i in range(5):
            build, record = self.cold_fixture(state='NOT_STARTED', build_id='infra-' + str(i))
            builds.append(build); records[build['build_id']] = record
        ledger = {'builds': builds, 'cold_start_observations': records, 'setup_repair': {
            'prior_build_id': builds[-1]['build_id'], 'candidate_sha': 'new', 'evidence': 'changed setup'}}
        rr_lane.attempts_gate(ledger, 'cold-image', 'new', profile())
        with self.assertRaises(ValueError):
            rr_lane.attempts_gate(ledger, 'cold-image', 'old', profile())
        bad = copy.deepcopy(ledger); bad['builds'][-1]['execution_seconds'] = 1
        with self.assertRaisesRegex(ValueError, 'mismatches metadata'):
            rr_lane.attempts_gate(bad, 'cold-image', 'new', profile())

    def test_actual_starts_require_bound_brief_and_preserve_limit(self):
        cold, record = self.cold_fixture()
        ledger = {'builds': [cold], 'cold_start_observations': {cold['build_id']: record},
                  'cold_repair': {'prior_build_id': cold['build_id'], 'candidate_sha': 'new',
                                  'evidence': 'actual Dockerfile failure'}}
        rr_lane.attempts_gate(ledger, 'cold-image', 'new', profile())
        for key, value in [('source_commit', 'foreign'), ('stage', 'warm-g1'),
                           ('evidence', None), ('state', None)]:
            bad = copy.deepcopy(ledger); bad['cold_start_observations'][cold['build_id']][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                rr_lane.attempts_gate(bad, 'cold-image', 'new', profile())
        bad = copy.deepcopy(ledger)
        bad['cold_start_observations'][cold['build_id']]['evidence']['file_sha256'] = None
        with self.assertRaises(ValueError):
            rr_lane.attempts_gate(bad, 'cold-image', 'new', profile())
        second, second_record = self.cold_fixture(build_id='second-start', source='second')
        ledger['builds'].append(second); ledger['cold_start_observations']['second-start'] = second_record
        with self.assertRaisesRegex(ValueError, 'actual Dockerfile-start limit'):
            rr_lane.attempts_gate(ledger, 'cold-image', 'new', profile())

    def test_unknown_start_is_an_evidence_gate_not_exhaustion(self):
        cold, record = self.cold_fixture(state='UNKNOWN')
        ledger = {'builds': [cold], 'cold_start_observations': {cold['build_id']: record}}
        with self.assertRaisesRegex(ValueError, 'UNKNOWN.*not attempt exhaustion'):
            rr_lane.attempts_gate(ledger, 'cold-image', 'new', profile())
        for bad in ({'builds': [dict(cold, accounted=False)]}, {'builds': [cold]},
                    {'builds': None}, {'builds': ['bad']},
                    {'builds': [dict(cold, status='WORKING')]}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                rr_lane.attempts_gate(bad, 'cold-image', 'new', profile())

    def test_warm_requires_successful_started_cold_and_keeps_two_attempt_limit(self):
        cold, record = self.cold_fixture(status='SUCCESS')
        ledger = {'builds': [cold], 'cold_start_observations': {cold['build_id']: record}}
        rr_lane.attempts_gate(ledger, 'warm-g1', 'new', profile())
        with self.assertRaises(ValueError):
            rr_lane.attempts_gate(ledger, 'cold-image', 'new', profile())
        unknown = copy.deepcopy(ledger); unknown['cold_start_observations'][cold['build_id']]['state'] = 'UNKNOWN'
        with self.assertRaisesRegex(ValueError, 'Brief-confirmed Dockerfile start'):
            rr_lane.attempts_gate(unknown, 'warm-g1', 'new', profile())
        warm = {'stage': 'warm-g1', 'accounted': True, 'status': 'SUCCESS',
                'build_id': 'warm', 'infra_sha': 'old-warm'}
        ledger['builds'].append(warm)
        ledger['warm_repair'] = {'prior_build_id': 'warm', 'candidate_sha': 'new',
                                 'evidence': 'unrelated core diagnostic'}
        rr_lane.attempts_gate(ledger, 'warm-g1', 'new', profile())
        ledger['builds'].append(dict(warm, build_id='warm2', infra_sha='warm2'))
        with self.assertRaisesRegex(ValueError, 'warm attempt limit'):
            rr_lane.attempts_gate(ledger, 'warm-g1', 'new', profile())

    def test_configuration_uses_digest_shape_and_stage_machine_only_for_n8(self):
        p = profile(); raw = (json.dumps(p) + '\n').encode()
        record = dict(control.NETWORK_PHASES[rr_lane.PHASE], profile_sha256=control.digest(raw))
        for stage, timeout, machine in [('cold-image', 1740, 'E2_HIGHCPU_8'),
                                        ('warm-g1', 1200, 'E2_STANDARD_2')]:
            with self.subTest(stage=stage), mock.patch.dict(control.NETWORK_PHASES, {rr_lane.PHASE: record}), \
                 mock.patch.object(control.subprocess, 'check_output', return_value=raw), \
                 mock.patch.object(control, 'network_env', return_value=[]):
                cfg = control.config('a' * 40, 'a' * 40, rr_lane.LANE, timeout, 'synthetic',
                    source_payload=b'synthetic source', phase_id=rr_lane.PHASE, stage=stage)
            image = rr_lane.profile_gate(p, stage, timeout)
            self.assertEqual(cfg['steps'][0]['name'], image)
            self.assertEqual(cfg['options']['machineType'], machine)
            self.assertEqual(cfg['options']['diskSizeGb'], 100)
            self.assertEqual(cfg['timeout'], str(timeout) + 's')
            self.assertEqual(cfg['queueTtl'], '60s')
            for step in cfg['steps'][:2]:
                self.assertIn('PROOF_IMAGE=' + image, step['env'])
            body = cfg['steps'][0]['args'][1]
            self.assertEqual('apt-get' in body, stage == 'cold-image')
            self.assertIn('network_setup_run pinned-source-restore', body)
            self.assertTrue(all(len(arg.encode()) <= 10000 for s in cfg['steps'] for arg in s.get('args', [])))

    def test_other_lanes_keep_their_old_envelope(self):
        with self.assertRaises(ValueError):
            control.network_time_budget(1740)
        self.assertEqual(rr_lane.time_budget(1740, 'cold-image')['package_reserve'], 240)
        with mock.patch.object(control, 'network_env', return_value=[]):
            cfg = control.config('a' * 40, 'a' * 40, 'network-n13', 795, 'synthetic',
                                 phase_id=control.NETWORK_N4_PHASE, stage='exact')
        self.assertEqual(cfg['steps'][0]['name'], control.UBUNTU)
        self.assertEqual(cfg['options'], {'machineType': 'E2_STANDARD_2', 'logging': 'CLOUD_LOGGING_ONLY'})


if __name__ == '__main__':
    unittest.main()
