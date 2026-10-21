"""Isolated R15 actual-body service tests; synthetic inputs only, no extraction or verifier."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "a1_actual_body_service_under_test", HERE / "a1-actual-body.py")
BODY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BODY)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FakeGhost:
    @staticmethod
    def strip_ghost(source: bytes) -> bytes:
        return source


class FakeGates:
    def __init__(self, name="synthetic-body", focus=2, end=5):
        self.name = name
        self.focus = focus
        self.end = end

    def functions(self, _ast_text):
        return [{"name": self.name, "kind": "definition",
                 "fields": [("start", self.focus)] + [None] * 9 + ["body"]}]

    def _source_span(self, token):
        line = token[1] if isinstance(token, tuple) else 2
        return (("verified/lib.rs", line, 0), ("verified/lib.rs", line, 9))

    def node(self, _node, tag, arity):
        if tag == "Some" and arity == 1:
            return ("body",)
        if tag == "tuple" and arity == 2:
            return ("tuple-head", ("end", self.end))
        raise AssertionError((tag, arity))

    @staticmethod
    def digest(text):
        return sha(text.encode())


class FakeGrammar:
    def __init__(self, hashes):
        self.hashes = hashes

    def _tool_hashes(self, _tool):
        return self.hashes


class FakeC4:
    def __init__(self, *, support=True, stage_error=False, make_ast=True,
                 mutate_source=False, mutate_tool=None, lemma_exit=0):
        self.support = support
        self.stage_error = stage_error
        self.make_ast = make_ast
        self.mutate_source = mutate_source
        self.mutate_tool = mutate_tool
        self.lemma_exit = lemma_exit
        self.stage_calls = 0
        self.stage_names = []

    def source_support(self, _a, _tool, fixture, _stage_root, _env, *, target):
        self.fixture = fixture
        return ({"source_support": "TERMINAL"},
                {"paired_support_passed": self.support, "target": target})

    def stage(self, _a, stage_root, _name, command, _env, _timeout, *, cwd):
        self.stage_calls += 1
        self.stage_names.append(_name)
        if self.stage_error:
            raise RuntimeError("synthetic stage failure")
        log = b"synthetic verifier completed\n"
        (stage_root / (_name + ".log")).write_bytes(log)
        if self.make_ast:
            ast_path = Path(command[command.index("-dump_ast_with_locs") + 1])
            ast_path.write_text("synthetic AST text")
        if self.mutate_source:
            (cwd / "verified/lib.rs").write_bytes(b"changed after source-pair stage")
        if self.mutate_tool is not None:
            self.mutate_tool()
        exit_code = self.lemma_exit if _name == "lemma-verification" else 0
        return {"classification": "TERMINAL", "exit": exit_code,
                "log_sha256": sha(log)}


class ActualBodyClassifierTests(unittest.TestCase):
    def setUp(self):
        self.log = b"verifier output\n"
        self.stage = {"classification": "TERMINAL", "exit": 0,
                      "log_sha256": sha(self.log)}
        self.selection = {"classification": "SOURCE_BOUND_FULL_BODY_INTERVAL", "name": "sort4_stable", "body_count_from_intervals": 1}

    def classify(self, **overrides):
        values = {"selection": self.selection, "paired": True, "immutable": True}
        values.update(overrides)
        return BODY.classify(self.stage, self.log, **values)

    def test_nonterminal_missing_and_boolean_exit_are_inconclusive(self):
        for stage in (None, {}, {"classification": "RUNNING", "exit": 0,
                                  "log_sha256": sha(self.log)},
                      {"classification": "TERMINAL", "exit": True,
                       "log_sha256": sha(self.log)}):
            with self.subTest(stage=stage):
                result = BODY.classify(stage, self.log, selection=self.selection,
                                       paired=True, immutable=True)
                self.assertFalse(result["passed"])
                self.assertFalse(result["proof_credit"])
                self.assertEqual(result["status"], "INCONCLUSIVE")

    def test_missing_or_changed_log_is_inconclusive(self):
        for log in (None, b"different log"):
            with self.subTest(log=log):
                result = BODY.classify(self.stage, log, selection=self.selection,
                                       paired=True, immutable=True)
                self.assertFalse(result["passed"])
                self.assertEqual(result["status"], "INCONCLUSIVE")

    def test_pair_immutability_and_missing_selection_gates_block_pass(self):
        for selection, paired, immutable in (
                (self.selection, False, True),
                (self.selection, True, False),
                (None, True, True)):
            with self.subTest(selection=selection, paired=paired, immutable=immutable):
                result = BODY.classify(self.stage, self.log, selection=selection,
                                       paired=paired, immutable=immutable)
                self.assertFalse(result["passed"])
                self.assertFalse(result["proof_credit"])

    def test_wrong_body_selection_must_not_pass(self):
        result = BODY.classify(self.stage, self.log,
            selection={"name": "unrelated_helper", "body_count_from_intervals": 1},
            paired=True, immutable=True)
        self.assertFalse(result["passed"])
        self.assertEqual(result["status"], "INCONCLUSIVE")

    def test_zero_exit_is_unqualified_and_never_yields_receipt_credit(self):
        result = self.classify()
        self.assertTrue(result["passed"])
        self.assertEqual(result["status"], "SOURCE_REPORTED_BODY_CHECKED_UNQUALIFIED")
        self.assertFalse(result["proof_credit"])
        self.assertFalse(result["summary_eligible"])
        self.assertNotIn("receipt", result)

    def test_negative_resource_controls_remain_unclassified(self):
        result = self.classify(negative="synthetic-negative")
        self.assertFalse(result["passed"])
        self.assertFalse(result["proof_credit"])
        self.assertFalse(result["summary_eligible"])
        self.assertEqual(result["status"], "RESOURCE_CONTROL_OBSERVED_UNCLASSIFIED")


class ActualBodyServiceTests(unittest.TestCase):
    def make_case(self, name="synthetic-body"):
        verified = b"// synthetic verified Rust pair\n"
        original = b"// synthetic original Rust pair\n"
        meta = {"name": name, "focus_line": 2, "end_line": 5}
        return name, verified, original, meta

    def run_case(self, temp, c4, *, grammar=None, gates=None):
        root = Path(temp)
        return BODY.run_case(None, c4, Path("/synthetic/tool"), {}, root,
            self.make_case(), gates or FakeGates(),
            grammar or FakeGrammar({"verifier": "old-tool"}),
            {"tool_hashes": {"verifier": "old-tool"}})

    def test_zero_exit_after_exact_synthetic_body_selection_is_unqualified(self):
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_case(temp, FakeC4())
        self.assertIn("body_selection", result)
        self.assertTrue(result["passed"])
        self.assertEqual(result["status"], "SOURCE_REPORTED_BODY_CHECKED_UNQUALIFIED")
        self.assertFalse(result["proof_credit"])
        self.assertFalse(result["summary_eligible"])

    def test_stage_exception_is_recorded_and_remains_inconclusive(self):
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_case(temp, FakeC4(stage_error=True))
        self.assertIn("synthetic stage failure", result["error"])
        self.assertFalse(result["passed"])
        self.assertFalse(result["proof_credit"])

    def test_missing_ast_prevents_body_selection_and_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_case(temp, FakeC4(make_ast=False))
        self.assertNotIn("body_selection", result)
        self.assertFalse(result["passed"])
        self.assertEqual(result["status"], "INCONCLUSIVE")

    def test_failed_source_pair_suppresses_dependent_verifier(self):
        c4 = FakeC4(support=False)
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_case(temp, c4)
        self.assertEqual(result["status"], "SOURCE_PAIR_PREREQUISITE_FAILED")
        self.assertEqual(c4.stage_calls, 0)
        self.assertNotIn("verification", result)
        self.assertFalse(result["passed"])

    def test_failed_required_lemma_suppresses_actual_body_verification(self):
        c4 = FakeC4(lemma_exit=1)
        base = self.make_case()
        meta = dict(base[3], required_lemmas=[{
            "name": "copy_lemma", "focus_line": 3, "end_line": 6}])
        case = (base[0], base[1], base[2], meta)
        with tempfile.TemporaryDirectory() as temp:
            result = BODY.run_case(None, c4, Path("/synthetic/tool"), {}, Path(temp),
                case, FakeGates(name="copy_lemma", focus=3, end=6),
                FakeGrammar({"verifier": "old-tool"}),
                {"tool_hashes": {"verifier": "old-tool"}})
        self.assertEqual(result["status"], "CHECKED_LEMMA_PREREQUISITE_FAILED")
        self.assertIn("actual body explicitly NOT_RUN", result["reason"])
        self.assertEqual(c4.stage_names, ["lemma-verification"])
        self.assertNotIn("body-verification", c4.stage_names)
        self.assertNotIn("verification", result)
        self.assertFalse(result["passed"])
        self.assertFalse(result["proof_credit"])

    def test_changed_source_pair_is_not_passed(self):
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_case(temp, FakeC4(mutate_source=True))
        self.assertFalse(result["source_pair_immutable"])
        self.assertFalse(result["passed"])

    def test_changed_tool_identity_is_not_passed(self):
        grammar = FakeGrammar({"verifier": "old-tool"})
        c4 = FakeC4(mutate_tool=lambda: setattr(grammar, "hashes", {"verifier": "new-tool"}))
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_case(temp, c4, grammar=grammar)
        self.assertFalse(result["tool_immutable"])
        self.assertFalse(result["passed"])

    def test_component_cases_are_built_from_small_synthetic_markers(self):
        source = (b"// synthetic component prefix\n" +
            b"// CASE_BEGIN copy-a\nunsafe fn copy_a<T>() {}\n// CASE_END copy-a\n" +
            b"// CASE_BEGIN copy-b\nunsafe fn copy_b<T>() {}\n// CASE_END copy-b\n" +
            b"// CASE_BEGIN copy-c\nunsafe fn copy_c<T>() {}\n// CASE_END copy-c\n" +
            b"// CASE_BEGIN copy-d\nunsafe fn copy_d<T>() {}\n// CASE_END copy-d\n")
        cases = BODY.component_cases(source, FakeGhost())
        self.assertEqual([case[0] for case in cases],
                         ["copy-a", "copy-b", "copy-c", "copy-d"])
        for _name, verified, original, meta in cases:
            self.assertTrue(verified.startswith(b"// synthetic component prefix"))
            self.assertEqual(FakeGhost.strip_ghost(verified), original)
            self.assertFalse(meta["proof_credit"])
            self.assertFalse(meta["summary_eligible"])


if __name__ == "__main__":
    unittest.main()
