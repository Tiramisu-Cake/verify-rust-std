"""Isolated progress serialization checks using synthetic parser values only."""
from importlib.util import module_from_spec, spec_from_file_location
from dataclasses import dataclass
import ast
import json
from pathlib import Path
import shutil
import sys
import tempfile
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
        result = {'accepted': False, 'case_status': {'P1': {'status': 'INCONCLUSIVE',
                   'provenance': original_provenance}},
                  'target_observed_records': [MappingProxyType({'unit_id': 'unit-a', 'proof_credit': False})]}
        observations = {'P1': {'adapter_error': 'native refusal', 'proof_credit': False},
                        'N-binding': {'status': 'NOT_RUN', 'artifact': None},
                        'partial': {'artifacts': {'stderr': {'path': None}}},
                        'typed': PARSER.Text('retained')}
        positive = {'admission_gate': object(), 'certificate': object(),
                    'positive_cases': MappingProxyType({'P0a': {'status': 'PARTIAL'}})}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'progress.json'
            namespace = dict(result=result, observations=observations,
                             execution_events=[{'event': 'adapter_error', 'error': 'retained'}],
                             positive_progress=positive, progress_path=path,
                             _jsonable=RUNNER._jsonable, json=json)
            exec(compile(ast.Module(body=[persist], type_ignores=[]), str(HERE / 'a1-runner.py'), 'exec'), namespace)
            namespace['persist_progress']()
            emitted = json.loads(path.read_text())
        self.assertIs(result['case_status']['P1']['provenance'], original_provenance)
        self.assertIsInstance(result['target_observed_records'][0], MappingProxyType)
        self.assertEqual(emitted['case_status']['P1']['provenance'], dict(original_provenance))
        self.assertEqual(emitted['target_observed_records'], [{'unit_id': 'unit-a', 'proof_credit': False}])
        self.assertEqual(emitted['observation_details']['typed'], {'kind': 'Text', 'value': 'retained'})
        self.assertEqual(emitted['observation_details']['partial']['artifacts']['stderr'], {'path': None})
        self.assertEqual(emitted['observation_details']['N-binding'], {'status': 'NOT_RUN', 'artifact': None})
        self.assertEqual(emitted['observation_details']['P1']['adapter_error'], 'native refusal')
        self.assertNotIn('admission_gate', emitted['positive_lifecycle_progress'])
        self.assertFalse(emitted['accepted'])

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
