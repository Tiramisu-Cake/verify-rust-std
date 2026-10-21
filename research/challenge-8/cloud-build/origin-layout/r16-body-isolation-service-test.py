#!/usr/bin/env python3
"""Synthetic source and receipt tests for R16 body isolation; no tool execution."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


campaign = load("r16_first_callback", HERE / "first-callback.py")
old = load("r16_actual_insert_tail", HERE / "actual-insert-tail-b2.py")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class BodyIsolationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.evidence = self.root / "evidence"
        self.parent_case = self.evidence / "full_body/cases/actual_three_current_full_posts"
        (self.parent_case / "original").mkdir(parents=True)
        (self.parent_case / "verified").mkdir()
        drop_raw = old.DROP_START + b"\nfn drop(&mut self) { actual_drop();}\n\n"
        insert_raw = (old.INSERT_START + b"begin: *mut T, tail: *mut T, is_less: &mut F) { "
                      b"actual_insert();\n}\n")
        self.canonical_source = (b"synthetic pinned source\n" + drop_raw +
                                old.DROP_END[len(b"}\n\n"):] + b"\n" +
                                insert_raw + old.INSERT_END[len(b"\n}\n"):])
        source_path = self.root / "pinned-smallsort.rs"
        source_path.write_bytes(self.canonical_source)
        self.body_source = SimpleNamespace(**vars(old))
        self.body_source.SOURCE = source_path
        self.body_source.PINNED_SOURCE_SHA256 = sha(self.canonical_source)
        self.body_source.PINNED_SOURCE_BLOB = old._git_blob(self.canonical_source)
        self.body_source.PINNED_DROP_SHA256 = sha(drop_raw)
        self.body_source.PINNED_DROP_BYTES = len(drop_raw)
        self.body_source.PINNED_INSERT_SHA256 = sha(insert_raw)
        self.body_source.PINNED_INSERT_BYTES = len(insert_raw)
        self.specialized_drop = old._specialize_drop(old._extract(
            self.canonical_source, old.DROP_START, old.DROP_END, b"}\n\n"))
        self.insert_body = old._specialize_insert(old._extract(
            self.canonical_source, old.INSERT_START, old.INSERT_END, b"\n}\n"))
        self.body_original = (b"#![no_std]\nuse core::{mem::ManuallyDrop, ptr};\n\n" +
                             self.specialized_drop + b"\n" + self.insert_body)
        self.body_verified = (b"#![no_std]\nuse core::{mem::ManuallyDrop, ptr};\n\n" +
                              self.specialized_drop + b"\n" +
                              old.INSERT_CONTRACT + b"\n" + self.insert_body)
        original_suffix, verified_suffix = campaign._body_isolation_suffixes(self.body_source)
        self.parent_original = self.body_original + original_suffix
        self.parent_verified = self.body_verified + verified_suffix
        (self.parent_case / "original/lib.rs").write_bytes(self.parent_original)
        (self.parent_case / "verified/lib.rs").write_bytes(self.parent_verified)
        self.parent_record = {
            "profile": campaign.R11_PROFILE,
            "prefix": False,
            "mutation": None,
            "original_sha256": sha(self.parent_original),
            "verified_sha256": sha(self.parent_verified),
            "source_sha256": self.body_source.PINNED_SOURCE_SHA256,
            "source_git_blob": self.body_source.PINNED_SOURCE_BLOB,
            "actual_drop_sha256": self.body_source.PINNED_DROP_SHA256,
            "actual_insert_tail_sha256": self.body_source.PINNED_INSERT_SHA256,
            "actual_insert_tail_bytes": self.body_source.PINNED_INSERT_BYTES,
            "mechanically_specialized_insert_sha256": sha(self.insert_body),
            "final_posts_sha256": sha(old.INSERT_CONTRACT),
        }
        self.parent_record["profile"] = campaign.R11_PROFILE
        parent_prep = self.evidence / "full_body/preparation.json"
        parent_prep.write_text(json.dumps(self.parent_record, sort_keys=True) + "\n")
        self.parent_preparation_sha = sha(parent_prep.read_bytes())

    def tearDown(self):
        self.temporary.cleanup()

    def isolate(self):
        return campaign._prepare_body_isolation(
            self.evidence, self.parent_case, self.parent_record, self.body_source,
            self.parent_preparation_sha, True, {"admitted": True})

    class Consumer:
        def _hashes(self, case):
            return (sha((case / "original/lib.rs").read_bytes()),
                    sha((case / "verified/lib.rs").read_bytes()))

        def _stage_receipts(self, case, stages, baseline):
            return {"admitted": True, "stages": list(stages)}

    def diagnostic(self, **kwargs):
        return campaign._run_body_isolation_diagnostic(
            self.evidence, self.parent_case, self.parent_record, self.body_source,
            self.Consumer(), SimpleNamespace(r8_owned_array_allocation=False),
            campaign.R11_PROFILE,
            kwargs.pop("dispatch", lambda *a, **kw: self.successful_execution()),
            parent_preparation_sha=self.parent_preparation_sha,
            parent_source_unchanged=kwargs.pop("parent_source_unchanged", True),
            parent_stage_receipt_gate=kwargs.pop("parent_stage_receipt_gate", {"admitted": True}),
            prepare_fn=kwargs.pop("prepare_fn", None),
            source_gate_fn=kwargs.pop("source_gate_fn", None),
            classify_fn=kwargs.pop("classify_fn", None))

    def successful_execution(self, **overrides):
        result = {
            "stages": {"exporter": 0, "decode": 0, "verifast": 0, "refinement": 0},
            "stage_receipt_gate": {"admitted": True},
            "source_unchanged_at_every_stage": True,
        }
        result.update(overrides)
        return result

    def test_exact_suffix_removed_and_body_posts_preserved(self):
        case, record = self.isolate()
        self.assertEqual((case / "original/lib.rs").read_bytes(), self.body_original)
        self.assertEqual((case / "verified/lib.rs").read_bytes(), self.body_verified)
        self.assertTrue(campaign._body_isolation_source_gate(
            case, self.parent_case, self.parent_record, record, self.body_source, self.parent_preparation_sha))
        self.assertEqual(record["final_posts_sha256"], sha(old.INSERT_CONTRACT))
        self.assertIs(record["accepted"], False)
        self.assertIs(record["proof_credit"], False)

    def test_mutated_or_extended_suffix_fails_closed(self):
        self.parent_original += b"pub fn extra() {}\n"
        (self.parent_case / "original/lib.rs").write_bytes(self.parent_original)
        with self.assertRaises(ValueError):
            self.isolate()

    def test_verified_suffix_mutation_fails_closed(self):
        self.parent_verified = self.parent_verified.replace(b'begin.add(2)', b'begin.add(1)', 1)
        (self.parent_case / "verified/lib.rs").write_bytes(self.parent_verified)
        with self.assertRaises(ValueError):
            self.isolate()

    def test_source_pins_and_specialized_identity_are_required(self):
        for field, value in (
            ("source_sha256", None), ("source_git_blob", "0" * 40),
            ("actual_drop_sha256", "0" * 64), ("actual_insert_tail_sha256", "0" * 64),
            ("actual_insert_tail_bytes", "1380"), ("mechanically_specialized_insert_sha256", None),
        ):
            self.parent_record[field] = value
            with self.assertRaises(ValueError):
                self.isolate()
            self.parent_record[field] = {
                "source_sha256": self.body_source.PINNED_SOURCE_SHA256,
                "source_git_blob": self.body_source.PINNED_SOURCE_BLOB,
                "actual_drop_sha256": self.body_source.PINNED_DROP_SHA256,
                "actual_insert_tail_sha256": self.body_source.PINNED_INSERT_SHA256,
                "actual_insert_tail_bytes": self.body_source.PINNED_INSERT_BYTES,
                "mechanically_specialized_insert_sha256": sha(self.insert_body),
            }[field]
        case, record = self.isolate()
        self.parent_record["mechanically_specialized_insert_sha256"] = "5" * 64
        parent_prep = self.evidence / "full_body/preparation.json"
        parent_prep.write_text(json.dumps(self.parent_record, sort_keys=True) + "\n")
        self.parent_preparation_sha = sha(parent_prep.read_bytes())
        record["mechanically_specialized_insert_sha256"] = "5" * 64
        self.assertFalse(campaign._body_isolation_source_gate(
            case, self.parent_case, self.parent_record, record, self.body_source, self.parent_preparation_sha))

    def test_parent_and_isolated_paths_must_be_canonical(self):
        case, record = self.isolate()
        self.assertFalse(campaign._body_isolation_source_gate(
            case / ".." / "other", self.parent_case, self.parent_record, record, self.body_source, self.parent_preparation_sha))
        other_parent = self.evidence / "other-parent/cases/actual_three_current_full_posts"
        (other_parent / "original").mkdir(parents=True)
        (other_parent / "verified").mkdir()
        (other_parent / "original/lib.rs").write_bytes(self.parent_original)
        (other_parent / "verified/lib.rs").write_bytes(self.parent_verified)
        self.assertFalse(campaign._body_isolation_source_gate(
            case, other_parent, self.parent_record, record, self.body_source, self.parent_preparation_sha))

    def test_pinned_source_bytes_are_rechecked_from_the_source_file(self):
        self.body_source.SOURCE.write_bytes(self.canonical_source + b"tampered")
        with self.assertRaises(ValueError):
            campaign._pinned_actual_body_identities(self.body_source)
        with self.assertRaises(ValueError):
            self.isolate()

    def test_invented_body_is_rejected_even_with_rewritten_parent_record(self):
        self.parent_original = self.parent_original.replace(b"actual_drop", b"invented_drop", 1)
        (self.parent_case / "original/lib.rs").write_bytes(self.parent_original)
        self.parent_record["original_sha256"] = sha(self.parent_original)
        parent_prep = self.evidence / "full_body/preparation.json"
        parent_prep.write_text(json.dumps(self.parent_record, sort_keys=True) + "\n")
        self.parent_preparation_sha = sha(parent_prep.read_bytes())
        with self.assertRaises(ValueError):
            self.isolate()

    def test_isolated_preparation_receipt_must_match_in_memory_record(self):
        case, record = self.isolate()
        path = self.evidence / "body_isolation/preparation.json"
        path.write_text("{}\n")
        self.assertFalse(campaign._body_isolation_source_gate(
            case, self.parent_case, self.parent_record, record, self.body_source, self.parent_preparation_sha))

    def test_parent_source_or_posts_identity_mismatch_fails_closed(self):
        case, record = self.isolate()
        self.parent_record["final_posts_sha256"] = "0" * 64
        self.assertFalse(campaign._body_isolation_source_gate(
            case, self.parent_case, self.parent_record, record, self.body_source, self.parent_preparation_sha))

    def test_prep_failure_is_inconclusive_and_original_control_continues(self):
        class PrepError(RuntimeError):
            def __init__(self):
                super().__init__("prepare broke")
                self.returncode = 17
                self.last_snapshot = {"stage": "decode", "complete": False}
                self.snapshots = ["last-completed"]

        original_calls = []
        result = self.diagnostic(prepare_fn=lambda *args: (_ for _ in ()).throw(PrepError()))
        original_calls.append("full-body-control")
        self.assertEqual(result["classification"], "INCONCLUSIVE")
        self.assertEqual(result["phase"], "prepare")
        self.assertEqual(result["exception"]["returncode"], 17)
        self.assertEqual(result["exception"]["last_snapshot"], {"stage": "decode", "complete": False})
        self.assertEqual(result["exception"]["snapshots"], ["last-completed"])
        self.assertEqual(original_calls, ["full-body-control"])
        self.assertNotIn("stages", result["exception"])

    def test_parent_verifier_exit_one_does_not_block_receipt_admitted_body_run(self):
        def dispatch(case, args, **kwargs):
            (case / "verifast.log").write_text("Verifying function 'small_sort::insert_tail'\n")
            return self.successful_execution()

        result = self.diagnostic(
            dispatch=dispatch,
            parent_stage_receipt_gate={"admitted": True, "stages": {"verifast": 1}})
        self.assertEqual(result["classification"], "BODY_UNIT_VERIFIER_EXIT0")

    def test_parent_source_or_stage_gate_failure_skips_diagnostic(self):
        for source_unchanged, stage_gate in (
                (False, {"admitted": True}), (True, {"admitted": False})):
            calls = []
            result = self.diagnostic(
                parent_source_unchanged=source_unchanged,
                parent_stage_receipt_gate=stage_gate,
                dispatch=lambda *args, **kwargs: calls.append("dispatch"))
            self.assertEqual(result["classification"], "NOT_RUN")
            self.assertEqual(result["phase"], "parent_stage_gate")
            self.assertEqual(calls, [])

    def test_post_capture_proof_comment_and_rewritten_prep_cannot_rebind_source(self):
        captured_record = json.loads(json.dumps(self.parent_record))
        captured_prep_sha = self.parent_preparation_sha
        self.parent_verified = self.parent_verified.replace(
            b"actual_insert();", b"actual_insert(); /*@ invented proof annotation @*/", 1)
        (self.parent_case / "verified/lib.rs").write_bytes(self.parent_verified)
        self.parent_record["verified_sha256"] = sha(self.parent_verified)
        (self.evidence / "full_body/preparation.json").write_text(
            json.dumps(self.parent_record, sort_keys=True) + "\n")
        calls = []
        result = campaign._run_body_isolation_diagnostic(
            self.evidence, self.parent_case, captured_record, self.body_source,
            self.Consumer(), SimpleNamespace(r8_owned_array_allocation=False),
            campaign.R11_PROFILE, lambda *args, **kwargs: calls.append("isolated-dispatch"),
            parent_preparation_sha=captured_prep_sha,
            parent_source_unchanged=True,
            parent_stage_receipt_gate={"admitted": True, "stages": {"verifast": 1}})
        calls.append("mandatory-original-control")
        self.assertEqual(result["classification"], "INCONCLUSIVE")
        self.assertEqual(result["phase"], "prepare")
        self.assertEqual(calls, ["mandatory-original-control"])

    def test_source_gate_failure_is_not_run_and_never_dispatches(self):
        calls = []
        result = self.diagnostic(
            source_gate_fn=lambda *args: False,
            dispatch=lambda *args, **kwargs: calls.append("dispatch"))
        self.assertEqual(result["classification"], "NOT_RUN")
        self.assertEqual(calls, [])

    def test_dispatch_exception_attributes_and_snapshot_are_preserved(self):
        class DispatchError(RuntimeError):
            def __init__(self):
                super().__init__("executor stopped")
                self.exit_code = 23
                self.last_snapshot = {"completed": "exporter"}

        result = self.diagnostic(prepare_fn=lambda *args: self.isolate(),
                                 dispatch=lambda *args, **kwargs: (_ for _ in ()).throw(DispatchError()))
        self.assertEqual(result["classification"], "INCONCLUSIVE")
        self.assertEqual(result["exception"]["attributes"]["exit_code"], 23)
        self.assertEqual(result["exception"]["last_snapshot"], {"completed": "exporter"})
        self.assertNotIn("stages", result)
        self.assertNotIn("execution_status", result)

    def test_receipt_and_classification_exceptions_are_inconclusive(self):
        class ReceiptError(RuntimeError):
            def __init__(self):
                super().__init__("receipt reader failed")
                self.stage = "refinement"

        class BrokenConsumer(self.Consumer):
            def _stage_receipts(self, case, stages, baseline):
                raise ReceiptError()

        existing_case, existing_record = self.isolate()
        result = campaign._run_body_isolation_diagnostic(
            self.evidence, self.parent_case, self.parent_record, self.body_source,
            BrokenConsumer(), SimpleNamespace(r8_owned_array_allocation=False),
            campaign.R11_PROFILE, lambda *a, **kw: self.successful_execution(),
            parent_preparation_sha=self.parent_preparation_sha,
            parent_source_unchanged=True, parent_stage_receipt_gate={"admitted": True},
            prepare_fn=lambda *args: (existing_case, existing_record))
        self.assertEqual(result["classification"], "INCONCLUSIVE")
        self.assertEqual(result["receipt_exception"]["attributes"]["stage"], "refinement")

        result = self.diagnostic(prepare_fn=lambda *args: (existing_case, existing_record),
                                 classify_fn=lambda *args: (_ for _ in ()).throw(ValueError("bad result")))
        self.assertEqual(result["classification"], "INCONCLUSIVE")
        self.assertEqual(result["exception"]["type"], "ValueError")
        self.assertEqual(result["phase"], "classification")

    def test_success_is_component_only_observation(self):
        case, record = self.isolate()
        (case / "verifast.log").write_text(
            "Verifying function 'small_sort::insert_tail'\n")
        result = campaign._classify_body_isolation(
            case, self.parent_case, self.parent_record, record,
            self.successful_execution(), self.body_source, self.parent_preparation_sha)
        self.assertEqual(result["classification"], "BODY_UNIT_VERIFIER_EXIT0")
        for key in ("accepted", "proof_credit", "full_target", "b2_achieved",
                    "caller_or_prefix_gate", "independent_credit", "qualification"):
            self.assertIs(result[key], False)

    def test_verifier_error_is_inconclusive(self):
        case, record = self.isolate()
        (case / "verifast.log").write_text(
            "Verifying function 'insert_tail'\nverified/lib.rs(3,2): error: Cannot prove\n")
        result = campaign._classify_body_isolation(
            case, self.parent_case, self.parent_record, record,
            self.successful_execution(), self.body_source, self.parent_preparation_sha)
        self.assertEqual(result["classification"], "INCONCLUSIVE")

    def test_execution_exception_is_inconclusive(self):
        case, record = self.isolate()
        run = self.successful_execution(exception={'type': 'RuntimeError', 'message': 'partial'})
        result = campaign._classify_body_isolation(
            case, self.parent_case, self.parent_record, record, run, self.body_source, self.parent_preparation_sha)
        self.assertEqual(result['classification'], 'INCONCLUSIVE')
        self.assertIn('exception', result['reason'])

    def test_timeout_is_inconclusive(self):
        case, record = self.isolate()
        run = self.successful_execution(stages={
            "exporter": 0, "decode": 0, "verifast": 124, "refinement": 0})
        result = campaign._classify_body_isolation(
            case, self.parent_case, self.parent_record, record, run, self.body_source, self.parent_preparation_sha)
        self.assertEqual(result["classification"], "INCONCLUSIVE")
        self.assertIn("timed out", result["reason"])

    def test_partial_stages_are_inconclusive(self):
        case, record = self.isolate()
        run = self.successful_execution(stages={"exporter": 0, "decode": 0})
        result = campaign._classify_body_isolation(
            case, self.parent_case, self.parent_record, record, run, self.body_source, self.parent_preparation_sha)
        self.assertEqual(result["classification"], "INCONCLUSIVE")
        self.assertIn("missing", result["reason"])

    def test_explicit_not_run_is_preserved(self):
        case, record = self.isolate()
        result = campaign._classify_body_isolation(
            case, self.parent_case, self.parent_record, record,
            {"status": "NOT_RUN"}, self.body_source, self.parent_preparation_sha)
        self.assertEqual(result["classification"], "NOT_RUN")

    def test_missing_null_and_wrong_type_results_are_inconclusive(self):
        case, record = self.isolate()
        for stages in (
            None,
            {"exporter": 0, "decode": 0, "verifast": 0},
            {"exporter": 0, "decode": 0, "verifast": None, "refinement": 0},
            {"exporter": 0, "decode": 0, "verifast": "0", "refinement": 0},
        ):
            result = campaign._classify_body_isolation(
                case, self.parent_case, self.parent_record, record,
                {"stages": stages, "stage_receipt_gate": {"admitted": True},
                 "source_unchanged_at_every_stage": True}, self.body_source, self.parent_preparation_sha)
            self.assertEqual(result["classification"], "INCONCLUSIVE")

    def test_missing_or_mismatched_stage_receipt_is_inconclusive(self):
        case, record = self.isolate()
        for gate in (None, {"admitted": False}, {"admitted": "true"}):
            run = self.successful_execution(stage_receipt_gate=gate)
            result = campaign._classify_body_isolation(
                case, self.parent_case, self.parent_record, record, run, self.body_source, self.parent_preparation_sha)
            self.assertEqual(result["classification"], "INCONCLUSIVE")

    def test_source_mismatch_is_inconclusive(self):
        case, record = self.isolate()
        (self.parent_case / "original/lib.rs").write_bytes(self.parent_original + b"\n")
        result = campaign._classify_body_isolation(
            case, self.parent_case, self.parent_record, record,
            self.successful_execution(), self.body_source, self.parent_preparation_sha)
        self.assertEqual(result["classification"], "INCONCLUSIVE")
        self.assertIs(result["source_exact"], False)

    def test_target_mismatch_is_inconclusive(self):
        case, record = self.isolate()
        (case / "verifast.log").write_text("Verifying function 'CopyOnDrop::drop'\n")
        result = campaign._classify_body_isolation(
            case, self.parent_case, self.parent_record, record,
            self.successful_execution(), self.body_source, self.parent_preparation_sha)
        self.assertEqual(result["classification"], "INCONCLUSIVE")
        self.assertIn("target", result["reason"])


if __name__ == "__main__":
    unittest.main()
