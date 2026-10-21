#!/usr/bin/env python3
"""Synthetic parser/classifier and fail-closed boundary tests; no tool stages."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "r11_storage_placement", HERE / "r11-storage-placement-controls.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PlacementControlTests(unittest.TestCase):
    def setUp(self):
        self.target = 277
        self.identity = {"cloud_build_id": "b-uuid", "proof_sha": "a" * 40,
                         "profile": m.PROFILE, "case": "synthetic"}

    def log(self, *, positive=False, line=None, diagnostic=None, cut=True, produced=True):
        line = self.target if line is None else line
        rows = []
        if cut:
            rows.append(f"R11_INVARIANT_CUT kind=source_bound at=verified/lib.rs({line},8-31,1)")
        if produced:
            rows.append(f"R11_EXEC kind=label_invariant phase=body gate=produced at=verified/lib.rs({line},8-31,1)")
        rows.append(f"verified/lib.rs({line},8): Executing statement")
        if diagnostic:
            rows.append(f"verified/lib.rs({line},8-31,1): error: {diagnostic}")
        return "\n".join(rows)

    def mir_fixture(self):
        return '''bodies = [
 (defPath = "crate::insert_tail", clauses = [],
  localDecls = [
   (id = (name = "_0"), ty = (kind = (tuple = []))),
   (id = (name = "_7"), ty = (kind = (tuple = []))),
   (id = (name = "_8"), ty = (kind = (uInt = (u64 = void)))),
   (id = (name = "_9"), ty = (kind = (tuple = [])))
  ],
  basicBlocks = [
   (id = (index = 0), statements = [
    (sourceInfo = (span = (regular = (lo = (line = 277), hi = (line = 277)))),
     kind = (storageLive = (name = "_7"))),
    (sourceInfo = (span = (regular = (lo = (line = 277), hi = (line = 277)))),
     kind = (nop = void))
   ], terminator = (sourceInfo = (span = (regular = (lo = (line = 277), hi = (line = 277)))),
    kind = (call = (func = (constant = (function = "VeriFast_ghost_command")),
     args = [], destination = (local = (name = "_7")),
     target = (something = (index = 1)), unwindAction = (cleanup = (index = 158)))))),
   (id = (index = 1), statements = [
    (sourceInfo = (span = (regular = (lo = (line = 277), hi = (line = 277)))),
     kind = (storageDead = (name = "_7")))
   ], terminator = (sourceInfo = (span = (regular = (lo = (line = 278), hi = (line = 278)))),
    kind = (return = void)))
  ])
]'''

    def test_positive_diagnostic_requires_cut_and_body_production(self):
        gate = {"admitted": True}
        good = m._classify("positive_replay", {"exit_code": 1,
            "log": self.log(positive=True, diagnostic="later unrelated resource refusal")},
            self.target, positive=True, stage_gate=gate)
        self.assertTrue(good["matched"])
        self.assertFalse(good["proof_credit"])
        for log in (self.log(cut=False), self.log(produced=False), self.log(line=278)):
            row = m._classify("positive_replay", {"exit_code": 0, "log": log},
                              self.target, positive=True, stage_gate=gate)
            self.assertFalse(row["matched"])

    def test_negative_requires_exact_target_binding_refusal_and_no_receipts(self):
        gate = {"admitted": True}
        right = m._classify("missing_live", {"exit_code": 1,
            "log": self.log(diagnostic=m.DIAGNOSTIC, cut=False, produced=False)},
            self.target, positive=False, stage_gate=gate)
        self.assertTrue(right["matched"])
        self.assertFalse(right["accepted"])
        wrong = [
            {"exit_code": 1, "log": "random error"},
            {"exit_code": 1, "log": self.log(line=278, diagnostic=m.DIAGNOSTIC,
                                                  cut=False, produced=False)},
            {"exit_code": 2, "log": self.log(diagnostic=m.DIAGNOSTIC,
                                                  cut=False, produced=False)},
            {"exit_code": 1, "log": self.log(diagnostic=m.DIAGNOSTIC)},
            {"exit_code": 124, "log": self.log(diagnostic=m.DIAGNOSTIC,
                                                    cut=False, produced=False)},
        ]
        for outcome in wrong:
            self.assertFalse(m._classify("missing_live", outcome, self.target,
                positive=False, stage_gate=gate)["matched"])

    def test_stage_gate_requires_real_current_identity_and_receipt_sha(self):
        with tempfile.TemporaryDirectory() as temporary:
            case = Path(temporary)
            row = {"stage": "verifast", "exit_code": 1,
                   "source_before": {"original/lib.rs": "a", "verified/lib.rs": "b",
                                     "small_sort_source": "c"},
                   "source_after": {"original/lib.rs": "a", "verified/lib.rs": "b",
                                    "small_sort_source": "c"}, "source_unchanged": True,
                   "r11_run_identity": self.identity}
            path = case / "verifast-stage.json"
            def check():
                receipt_sha = m._sha(path.read_bytes())
                return m._stage_gate(case, {"exit_code": 1, "stage_receipt_sha256": receipt_sha},
                    row["source_before"], self.identity, self.identity)
            path.write_text(json.dumps(row))
            self.assertTrue(check()["admitted"])
            bad = dict(row, r11_run_identity={**self.identity, "cloud_build_id": "stale"})
            path.write_text(json.dumps(bad))
            self.assertFalse(check()["admitted"])
            path.unlink()
            self.assertFalse(m._stage_gate(case, {}, {}, self.identity,
                                           self.identity)["admitted"])

    def test_saved_native_inputs_need_current_exporter_decode_artifact_receipts(self):
        with tempfile.TemporaryDirectory() as temporary:
            case = Path(temporary)
            original, verified = b"orig", b"verified"
            raw, decoded = b"fresh-native-mir", b"decoded-native-mir"
            (case / "compiler-mir.bin").write_bytes(raw)
            (case / "decode.out").write_bytes(decoded)
            sources = {"original/lib.rs": m._sha(original),
                       "verified/lib.rs": m._sha(verified),
                       "small_sort_source": "c" * 64}
            identity = {"cloud_build_id": "12345678-1234-5678-1234-567812345678",
                        "proof_sha": "a" * 40, "source_sha256": sources["small_sort_source"],
                        "profile": m.PROFILE, "profile_sha256": "d" * 64,
                        "tool_commit": "f" * 40, "tool_sha256": {name: "e" * 64 for name in m.TOOLS},
                        "provider": {"provider": "cloud-build", "build_id":
                            "12345678-1234-5678-1234-567812345678", "project": "p", "region": "r"}}
            exporter = {"stage": "exporter", "exit_code": 0, "source_before": sources,
                        "source_after": sources, "source_unchanged": True,
                        "r11_run_identity": identity, "output_path": "compiler-mir.bin",
                        "output_sha256": m._sha(raw), "output_size": len(raw)}
            decoder = {"stage": "decode", "exit_code": 0, "source_before": sources,
                       "source_after": sources, "source_unchanged": True,
                       "r11_run_identity": identity, "input_path": "compiler-mir.bin",
                       "input_sha256": m._sha(raw), "output_path": "decode.out",
                       "output_sha256": m._sha(decoded), "output_size": len(decoded)}
            (case / "exporter-stage.json").write_text(json.dumps(exporter))
            (case / "decode-stage.json").write_text(json.dumps(decoder))
            self.assertTrue(m._current_native_input_gate(case, raw, decoded,
                (original, verified), identity)["admitted"])

            bad_rows = [
                dict(decoder, r11_run_identity={**identity, "cloud_build_id": "stale"}),
                dict(decoder, input_sha256="0" * 64),
                dict(decoder, output_sha256="1" * 64),
                dict(decoder, source_unchanged=False),
                dict(decoder, exit_code=124),
            ]
            for bad in bad_rows:
                (case / "decode-stage.json").write_text(json.dumps(bad))
                self.assertFalse(m._current_native_input_gate(case, raw, decoded,
                    (original, verified), identity)["admitted"])
            for malformed in (None, "wrong-type", {"stage": "decode"}):
                (case / "decode-stage.json").write_text(json.dumps(malformed))
                self.assertFalse(m._current_native_input_gate(case, raw, decoded,
                    (original, verified), identity)["admitted"])
            (case / "decode-stage.json").unlink()
            self.assertFalse(m._current_native_input_gate(case, raw, decoded,
                (original, verified), identity)["admitted"])

    def test_current_tuple_rejects_stale_build_proof_profile_and_tools(self):
        import hashlib
        class Args:
            profile = m.PROFILE
            tool_home = None
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = root / "profile.json"
            profile.write_text(json.dumps({"profile": m.PROFILE, "accepted": False,
                                           "effective_tool_commit": "f" * 40}))
            args = Args()
            args.tool_home = root / "tools"
            (args.tool_home / "bin").mkdir(parents=True)
            hashes = {}
            for name in m.TOOLS:
                path = args.tool_home / "bin" / name
                path.write_bytes(name.encode())
                hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            env = {"SMALLSORT_MERGE_PROFILE": str(profile),
                   "CLOUD_BUILD_ID": "12345678-1234-5678-1234-567812345678",
                   "CLOUD_BUILD_PROJECT_ID": "project", "CLOUD_BUILD_REGION": "region",
                   "PROOF_SHA": "a" * 40}
            tuple_data = {"cloud_build_id": env["CLOUD_BUILD_ID"], "proof_sha": "a" * 40,
                          "source_sha256": "b" * 64, "profile": m.PROFILE,
                          "accepted": False,
                          "profile_sha256": m._file_sha(profile), "tool_commit": "f" * 40,
                          "tool_sha256": hashes,
                          "provider": {"provider": "cloud-build",
                              "build_id": env["CLOUD_BUILD_ID"], "project": "project",
                              "region": "region"}}
            binding = m._profile_binding(args, env)
            self.assertEqual(m._run_identity(tuple_data, args, env, binding)["cloud_build_id"],
                             env["CLOUD_BUILD_ID"])
            raw_receipt = {key: value for key, value in tuple_data.items()
                           if key not in {"cloud_build_id", "profile_sha256", "tool_commit"}}
            raw_identity = m._run_identity(raw_receipt, args, env, binding)
            self.assertEqual(raw_identity["cloud_build_id"], env["CLOUD_BUILD_ID"])
            self.assertEqual(raw_identity["profile_sha256"], m._file_sha(profile))
            with self.assertRaises(ValueError):
                m._run_identity({key: value for key, value in raw_receipt.items()
                                 if key != "source_sha256"}, args, env, binding)
            alias_receipt = {**raw_receipt, "effective_tool_commit": "f" * 40,
                             "executable_hashes": hashes}
            alias_receipt.pop("tool_commit", None)
            alias_receipt.pop("tool_sha256", None)
            self.assertEqual(m._run_identity(alias_receipt, args, env, binding), raw_identity)
            mutations = [
                {**tuple_data, "cloud_build_id": "87654321-4321-8765-4321-876543218765"},
                {**tuple_data, "proof_sha": "c" * 40},
                {**tuple_data, "profile_sha256": "d" * 64},
                {**tuple_data, "tool_sha256": {**hashes, "verifast": "e" * 64}},
                {**tuple_data, "profile": "legacy-profile"},
                {**tuple_data, "tool_commit": "0" * 40},
            ]
            for bad in mutations:
                with self.assertRaises(ValueError):
                    m._run_identity(bad, args, env, binding)
            (args.tool_home / "bin" / "verifast").write_bytes(b"replaced")
            with self.assertRaises(ValueError):
                m._run_identity(tuple_data, args, env, binding)

    def test_mutation_plan_fails_closed_on_missing_or_ambiguous_source_anchor(self):
        with self.assertRaises(ValueError):
            m._mutation_plan("", b"fn insert_tail() {}\n")
        with self.assertRaises(ValueError):
            m._target_line(m.INVARIANT + b"\n" + m.INVARIANT)

    def test_safe_mutants_edit_only_uniquely_bound_native_records(self):
        decoded = self.mir_fixture()
        source = b"\n" * 276 + b"    //@ inv thread_token(t);\n"
        plan = m._mutation_plan(decoded, source)
        self.assertEqual(plan["source_line"], self.target)
        self.assertEqual(plan["temp_local"], "_7")
        self.assertEqual(plan["native_edges"]["target"], "(something = (index = 1))")
        self.assertEqual(plan["native_edges"]["unwindAction"],
                         "(cleanup = (index = 158))")
        wrong_dead = m._mutate_decoded(decoded, "wrong_dead_local", plan)
        self.assertIn('storageDead = (name = "_0")', wrong_dead)
        self.assertIn('target = (something = (index = 1))', wrong_dead)
        self.assertIn('unwindAction = (cleanup = (index = 158))', wrong_dead)
        for name in ("missing_live", "missing_dead", "wrong_dead_local",
                     "duplicate_live", "target_span_mismatch",
                     "ordinary_non_unit_destination"):
            mutant = m._mutate_decoded(decoded, name, plan)
            self.assertNotEqual(mutant, decoded, name)
        with self.assertRaisesRegex(ValueError, "no reviewed unique typed"):
            m._mutate_decoded(decoded, "extra_address_taken_use", plan)
        flat = decoded.replace("(something = (index = 1))", "(something = 1)")
        with self.assertRaises(ValueError):
            m._mutation_plan(flat, source)

    def test_cut_parser_accepts_exact_inv_at_but_rejects_ambiguous_fields(self):
        line = self.target
        good = f"R11_INVARIANT_CUT kind=source_bound inv_at=verified/lib.rs({line},8-31,1)"
        self.assertEqual(len(m._parse_cut(good, line)), 1)
        wrong = f"R11_INVARIANT_CUT kind=source_bound inv_at=verified/lib.rs({line + 1},8-31,1)"
        self.assertEqual(m._parse_cut(wrong, line), [])
        wrong_inv_at_with_line_fallback = (
            f"R11_INVARIANT_CUT kind=source_bound inv_at=verified/lib.rs({line + 1},8-31,1) line={line}")
        self.assertEqual(m._parse_cut(wrong_inv_at_with_line_fallback, line), [])
        duplicate = f"R11_INVARIANT_CUT kind=source_bound inv_at=verified/lib.rs({line},8) inv_at=verified/lib.rs({line + 1},8)"
        self.assertEqual(m._parse_cut(duplicate, line), [])

    def test_incomplete_and_wrong_type_outcomes_never_match(self):
        for outcome in (None, "wrong-type", {}, {"exit_code": None, "log": ""},
                        {"exit_code": 124, "log": self.log()}):
            row = m._classify("positive_replay", outcome, self.target,
                              positive=True, stage_gate={"admitted": True})
            self.assertFalse(row["matched"])

    def test_refusal_predicate_location_and_timeout_are_not_wildcards(self):
        gate = {"admitted": True}
        cases = [
            (1, self.log(diagnostic="R11 unrelated invariant diagnostic for another predicate",
                         cut=False, produced=False), True),
            (1, self.log(line=278, diagnostic=m.DIAGNOSTIC, cut=False, produced=False), True),
            (124, self.log(diagnostic=m.DIAGNOSTIC, cut=False, produced=False), True),
            (1, self.log(diagnostic=m.DIAGNOSTIC, cut=False, produced=False), False),
        ]
        for code, log, admitted in cases:
            row = m._classify("wrong_dead_local", {"exit_code": code, "log": log},
                              self.target, positive=False,
                              stage_gate={"admitted": admitted})
            self.assertFalse(row["matched"])


if __name__ == "__main__":
    unittest.main()
