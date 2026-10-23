"""Synthetic N7 admission/configuration tests; no Cloud or proof tools."""
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
    value = json.loads((Path(__file__).parent / 'network-rr/RR-G1-PROFILE-20261024-N7.json').read_text())
    value.update(authorization_phase_id=rr_lane.PHASE, proof_credit=False,
                 independent_credit=False, profile_accepted=False)
    value['std_source']['selected_baseline'] = 'cd371e035c7e573760c43bf934d53e8118ee3e7d'
    value['image_build'].update(cold_executor=rr_lane.COLD_EXECUTOR,
        image_digest=rr_lane.REPOSITORY + '@sha256:' + 'a' * 64,
        image_receipt_sha256='b' * 64, cold_build_id='01234567-1234-1234-1234-012345678901')
    return value


class RRLaneTests(unittest.TestCase):
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

    def test_attempts_preserve_unknown_and_require_evidence_driven_changed_repair(self):
        p = profile(); cold = {'stage': 'cold-image', 'accounted': True, 'status': 'FAILURE',
                              'build_id': p['image_build']['cold_build_id'], 'infra_sha': 'old'}
        rr_lane.attempts_gate({'builds': []}, 'cold-image', 'new', p)
        for ledger in ({'builds': [dict(cold, accounted=False)]}, {'builds': [cold]},
                       {'builds': [cold, cold]}, {'builds': None}, {'builds': ['bad']},
                       {'builds': [dict(cold, status='WORKING')]},
                       {'builds': [dict(cold, stage='other')]}):
            with self.subTest(ledger=ledger), self.assertRaises(ValueError):
                rr_lane.attempts_gate(ledger, 'cold-image', 'new', p)
        repair = {'prior_build_id': cold['build_id'], 'candidate_sha': 'new', 'evidence': 'Brief fact'}
        ledger = {'builds': [cold], 'setup_repair': repair}
        rr_lane.attempts_gate(ledger, 'cold-image', 'new', p)
        with self.assertRaises(ValueError):
            rr_lane.attempts_gate(ledger, 'cold-image', 'old', p)
        with self.assertRaises(ValueError):
            rr_lane.attempts_gate(dict(ledger, builds=[dict(cold, status='SUCCESS')]), 'cold-image', 'new', p)
        with self.assertRaises(ValueError):
            rr_lane.attempts_gate({'builds': [cold]}, 'warm-g1', 'new', p)
        successful = dict(cold, status='SUCCESS')
        rr_lane.attempts_gate({'builds': [successful]}, 'warm-g1', 'new', p)
        warm = {'stage': 'warm-g1', 'accounted': True, 'status': 'SUCCESS',
                'build_id': 'warm', 'infra_sha': 'old-warm'}
        # Collector success is diagnostic only; an unrelated target failure
        # can require the one explicitly recorded warm repair.
        rr_lane.attempts_gate({'builds': [successful, warm], 'warm_repair':
            {'prior_build_id': 'warm', 'candidate_sha': 'new', 'evidence': 'unrelated core diagnostic'}},
            'warm-g1', 'new', p)

    def test_configuration_uses_digest_shape_and_stage_machine_only_for_n7(self):
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
