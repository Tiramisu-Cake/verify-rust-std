"""Isolated progress serialization checks using synthetic parser values only."""
from importlib.util import module_from_spec, spec_from_file_location
from dataclasses import dataclass
import ast
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
from unittest import mock
from types import MappingProxyType
import unittest


HERE = Path(__file__).parent


def load_module(path: Path, name: str):
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("test module could not be loaded")
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# a1-runner imports only standard-library modules at module scope and declares
# its execution entry under __main__; importing it does not prepare or run proof.
RUNNER = load_module(HERE / "a1-runner.py", "test_a1_progress_runner")
PARSER = load_module(HERE / "a1-synthetic-inputs.py", "independent_parser_module")


@dataclass(frozen=True)
class Text:
    value: str


@dataclass(frozen=True)
class Record:
    fields: tuple


class ProgressJsonTests(unittest.TestCase):
    def test_nested_immutable_parser_nodes_preserve_kind_order_and_text(self):
        nodes = PARSER.Record((
            ("duplicate", PARSER.Text("same")),
            ("duplicate", PARSER.Atom("same")),
            ("number", PARSER.Number("0x00Af")),
            ("nested", PARSER.ListValue((
                PARSER.Number("-0x0"), PARSER.Text(""), None,
            ))),
        ))
        inventory = MappingProxyType({
            "inventory": MappingProxyType({"types": (nodes,)}),
            "empty": None,
        })

        encoded = RUNNER._jsonable(inventory)
        self.assertEqual(encoded, {
            "inventory": {"types": [{
                "kind": "Record",
                "fields": [
                    ["duplicate", {"kind": "Text", "value": "same"}],
                    ["duplicate", {"kind": "Atom", "value": "same"}],
                    ["number", {"kind": "Number", "value": "0x00Af"}],
                    ["nested", {"kind": "ListValue", "values": [
                        {"kind": "Number", "value": "-0x0"},
                        {"kind": "Text", "value": ""}, None,
                    ]}],
                ],
            }]},
            "empty": None,
        })
        self.assertEqual(json.loads(json.dumps(encoded)), encoded)
        self.assertNotEqual(encoded["inventory"]["types"][0]["fields"][0][1],
                            encoded["inventory"]["types"][0]["fields"][1][1])

    def test_partial_error_not_run_and_artifact_shapes_are_preserved(self):
        progress = MappingProxyType({
            "error": {"status": "INCONCLUSIVE", "reason": "collector error",
                      "proof_credit": False},
            "not_run": {"status": "NOT_RUN", "observed_stage": None,
                        "artifact": None, "proof_credit": False},
            "partial": {"status": "PARTIAL", "artifacts": {
                "stdout": {"path": None}, "stderr": {},
            }},
            "missing": {"status": "ERROR", "artifact": {}},
            "absent": {"status": "NOT_RUN"},
            "null": None,
        })

        encoded = RUNNER._jsonable(progress)
        self.assertEqual(encoded, {
            "error": {"status": "INCONCLUSIVE", "reason": "collector error",
                      "proof_credit": False},
            "not_run": {"status": "NOT_RUN", "observed_stage": None,
                        "artifact": None, "proof_credit": False},
            "partial": {"status": "PARTIAL", "artifacts": {
                "stdout": {"path": None}, "stderr": {},
            }},
            "missing": {"status": "ERROR", "artifact": {}},
            "absent": {"status": "NOT_RUN"},
            "null": None,
        })
        self.assertNotIn("path", encoded["absent"])
        self.assertNotIn("path", encoded["missing"]["artifact"])
        self.assertIsNone(encoded["partial"]["artifacts"]["stdout"]["path"])
        self.assertIsNone(encoded["null"])

    def test_actual_progress_boundary_preserves_mappingproxy_and_partial_records(self):
        tree = ast.parse((HERE / 'a1-runner.py').read_text())
        run = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'run')
        persist = next(node for node in run.body if isinstance(node, ast.FunctionDef) and node.name == 'persist_progress')
        original_provenance = MappingProxyType({'source_id': 'source-a', 'proof_credit': False})
        result = {'accepted': False, 'phase_id': 'phase-a', 'authorization_phase_id': 'auth-a',
                  'build_id': 'build-a', 'proof_sha': 'a' * 40, 'infra_sha': 'b' * 40,
                  'profile_sha256': 'c' * 64,
                  'case_status': {'P1': {'status': 'INCONCLUSIVE',
                   'provenance': original_provenance}}}
        observations = {'P1': {'adapter_error': 'native refusal', 'proof_credit': False},
                        'N-binding': {'status': 'NOT_RUN', 'artifact': None},
                        'N-clause-redirect': {'artifacts': {'stderr': {'path': None}}},
                        'OFF': PARSER.Text('retained')}
        events = [{'case_id': 'P1', 'event': 'adapter_error', 'error': 'native refusal'},
                  {'case_id': 'N-binding', 'event': 'not_run', 'reason': 'deadline'},
                  {'case_id': 'N-clause-redirect', 'event': 'started'},
                  {'case_id': 'P1', 'event': 'stage_observed', 'stage': 'P1-verification'}]
        positive = {'admission_gate': object(), 'certificate': object(),
                    'positive_cases': MappingProxyType({'P0a': {'status': 'PARTIAL'}})}
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            progress_path = directory / 'progress.json'
            audit_path = directory / 'diagnostic-audit.json'
            namespace = dict(result=result, observations=observations,
                             execution_events=events, positive_progress=positive,
                             progress_path=progress_path, partial_audit_path=audit_path,
                             _partial_progress_snapshot=RUNNER._partial_progress_snapshot,
                             _atomic_json_write=RUNNER._atomic_json_write)
            exec(compile(ast.Module(body=[persist], type_ignores=[]), str(HERE / 'a1-runner.py'), 'exec'), namespace)
            namespace['persist_progress']()
            emitted = json.loads(progress_path.read_text())
            packaged = json.loads(audit_path.read_text())
        self.assertIs(result['case_status']['P1']['provenance'], original_provenance)
        self.assertEqual(emitted, packaged)
        self.assertEqual(emitted['case_status']['P1']['status'], 'INCONCLUSIVE')
        self.assertEqual(emitted['case_status']['N-binding'], {
            'status': 'NOT_RUN', 'proof_credit': False, 'reason': 'deadline'})
        self.assertEqual(emitted['case_status']['N-clause-redirect']['status'], 'INCONCLUSIVE')
        self.assertEqual(emitted['case_status']['OFF']['status'], 'UNKNOWN')
        self.assertEqual(emitted['last_observed_stage'], 'P1-verification')
        self.assertEqual(emitted['build_id'], 'build-a')
        self.assertFalse(emitted['accepted'])
        self.assertFalse(emitted['matrix_complete'])
        self.assertFalse(emitted['proof_credit'])
        self.assertTrue(emitted['partial'])
        self.assertNotIn('observation_details', emitted)
        self.assertNotIn('positive_lifecycle_progress', emitted)
        self.assertFalse(emitted['accepted'])

    def test_partial_snapshot_records_completed_error_timeout_and_unknown_rows(self):
        result = {'phase_id': 'phase', 'authorization_phase_id': 'auth',
                  'build_id': 'build', 'proof_sha': 'd' * 40, 'infra_sha': 'e' * 40,
                  'profile_sha256': 'f' * 64, 'case_status': {
                      'P0a': {'status': 'INTENDED_CLASSIFIED', 'observed_stage': 'verification'},
                      'P0b': {'status': 'NOT_RUN', 'reason': 'placeholder'}}}
        observations = {
            'P0a': {'source_id': 'source-a', 'unit_id': 'unit-a',
                    'raw': {'large': 'must-not-be-copied'}},
            'P0b': None,
            'P0c': {'adapter_error': 'synthetic exception'},
            'P1': {'source_id': 17, 'unit_id': None},
        }
        events = [
            {'case_id': 'P0a', 'event': 'started'},
            {'case_id': 'P0a', 'event': 'completed'},
            {'case_id': 'P0a', 'event': 'stage_observed', 'stage': 'P0a-verification'},
            {'case_id': 'P0b', 'event': 'not_run', 'reason': 'deadline budget'},
            {'case_id': 'P0c', 'event': 'adapter_error', 'error': 'synthetic exception'},
            {'case_id': 'P1', 'event': 'started'},
        ]
        snapshot = RUNNER._partial_progress_snapshot(result, observations, events, {})
        self.assertEqual(snapshot['case_status']['P0a']['status'], 'INTENDED_CLASSIFIED')
        self.assertEqual(snapshot['case_status']['P0a']['source_identity'], {
            'source_id': 'source-a', 'unit_id': 'unit-a'})
        self.assertEqual(snapshot['case_status']['P0b']['status'], 'NOT_RUN')
        self.assertEqual(snapshot['case_status']['P0b']['reason'], 'deadline budget')
        self.assertEqual(snapshot['case_status']['P0c']['status'], 'INCONCLUSIVE')
        self.assertEqual(snapshot['case_status']['P0c']['reason'], 'synthetic exception')
        self.assertEqual(snapshot['case_status']['P1']['status'], 'INCONCLUSIVE')
        self.assertNotIn('source_identity', snapshot['case_status']['P1'])
        self.assertEqual(snapshot['case_status']['OFF']['status'], 'UNKNOWN')
        self.assertEqual(snapshot['last_observed_stage'], 'P0a-verification')
        self.assertEqual(snapshot['profile_sha256'], 'f' * 64)
        self.assertNotIn('large', json.dumps(snapshot))
        self.assertIsNone(snapshot['proof_verdict'])

    def test_r13_final_report_keeps_lossless_observation_pointer_serialization(self):
        observation = {'classification': 'INCONCLUSIVE', 'source_id': 'source-a'}
        value = {'authorization_phase_id': RUNNER.R13_AUTHORIZATION_PHASE,
                 'observation_details': {'P1': observation},
                 'observed_rows': [{'case_id': 'P1', 'observation': dict(observation)}]}
        serialized = RUNNER._report_value_for_disk(value, RUNNER.R13_AUTHORIZATION_PHASE)
        self.assertEqual(serialized['observed_rows'][0]['observation_ref'], {
            'schema': 'a1-observation-ref-v1', 'json_pointer': '/observation_details/P1'})
        self.assertNotIn('observation', serialized['observed_rows'][0])
        self.assertFalse(serialized['report_serialization']['proof_credit'])

    def test_r13_can_load_the_same_pinned_ghost_grammar_preflight(self):
        with tempfile.TemporaryDirectory() as temporary:
            helper = Path(temporary) / RUNNER.HERE / RUNNER.R12_GHOST_GRAMMAR_HELPER
            helper.parent.mkdir(parents=True)
            helper.write_text('PREFLIGHT_HELPER_LOADED = True\n')
            profile = {
                'authorization_phase_id': RUNNER.R13_AUTHORIZATION_PHASE,
                'ghost_grammar_preflight_enabled': True,
                'a1_ghost_grammar_sha256': hashlib.sha256(helper.read_bytes()).hexdigest(),
            }
            loaded = RUNNER.load_r12_ghost_grammar(Path(temporary), profile)
            self.assertTrue(loaded.PREFLIGHT_HELPER_LOADED)

    def test_atomic_json_write_leaves_existing_target_on_replace_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'audit.json'
            target.write_text('{"old":true}\n')
            with mock.patch.object(RUNNER.os, 'replace', side_effect=OSError('replace failed')):
                with self.assertRaisesRegex(OSError, 'replace failed'):
                    RUNNER._atomic_json_write(target, {'new': True})
            self.assertEqual(json.loads(target.read_text()), {'old': True})
            self.assertEqual(list(Path(temporary).glob('.audit.json.*.tmp')), [])

    def test_unknown_objects_and_wrong_parser_shapes_still_fail(self):
        class Unknown:
            def __repr__(self):
                raise AssertionError("repr must never be used as serialization")

        @dataclass(frozen=True)
        class SpoofText:
            value: str

        SpoofText.__name__ = "Text"
        SpoofText.__module__ = "unregistered_parser_spoof"

        for value in (Unknown(), PARSER.Text(7), PARSER.Number(15),
                      Text("foreign"), Record((("field", Text("foreign")),)),
                      SpoofText("spoofed")):
            with self.subTest(value_type=type(value).__name__), self.assertRaises(TypeError):
                RUNNER._jsonable(value)

    def test_identical_parser_source_in_another_checkout_is_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "proof" / "a1-synthetic-inputs.py"
            copied.parent.mkdir()
            shutil.copyfile(HERE / "a1-synthetic-inputs.py", copied)
            proof_parser = load_module(copied, "separate_proof_parser_module")
            value = proof_parser.Record((
                ("owner", proof_parser.Text("StableSmallSortTypeImpl")),
                ("number", proof_parser.Number("0x10")),
            ))
            self.assertEqual(RUNNER._jsonable(value), {
                "kind": "Record",
                "fields": [
                    ["owner", {"kind": "Text", "value": "StableSmallSortTypeImpl"}],
                    ["number", {"kind": "Number", "value": "0x10"}],
                ],
            })

            altered = copied.with_name("altered") / "a1-synthetic-inputs.py"
            altered.parent.mkdir()
            shutil.copyfile(copied, altered)
            altered.write_bytes(altered.read_bytes() + b"\n# different source bytes\n")
            impostor = load_module(altered, "different_proof_parser_module")
            with self.assertRaises(TypeError):
                RUNNER._jsonable(impostor.Text("same class name, other source"))


if __name__ == "__main__":
    unittest.main()
