"""Synthetic-only tests for the inactive R21 Brief fingerprint projection."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
PROJECTION_PATH = HERE / "project_r21_fingerprint_brief.py"
PROOF_PATH = HERE.parent / "cloud-build" / "select-callee-r21-fractional-proof.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


p = load(PROJECTION_PATH, "synthetic_r21_projection")
proof = load(PROOF_PATH, "synthetic_r21_proof_consumer")

BUILD = "synthetic-build"
FILE = "synthetic-file"
FILE_SHA = "a" * 64
INDEX_SHA = "b" * 64
ARCHIVE_SHA = "c" * 64


def h(n: int) -> str:
    return f"{n:064x}"


def make_record() -> dict:
    variants = {}
    defaults = {name: h(i + 1) for i, name in enumerate(p.SNAPSHOTS)}
    original = h(100)
    base_verified = h(101)

    def snapshots(seed: int):
        return {name: {"file": f"actual-nested-9-{name}.marshal",
                       "bytes": 400 + index, "sha256": digest}
                for index, (name, digest) in enumerate(defaults.items())}

    def fingerprint(seed: int):
        pair = {"original/lib.rs": original, "verified/lib.rs": h(seed)}
        return {
            "classification": "INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE",
            "expected_refusal_seen": True, "all_ten_snapshots": True,
            "body_proof_run": False,
            "stage": {
                "status": "RAN", "exit": 2, "source_unchanged": True,
                "source_before": pair, "source_after": pair,
                "intrinsic_gate_active": False, "pointer_drop_gate_active": False,
                "stdout": "nine-body-fingerprint-refusal.log",
                "stderr": "nine-body-fingerprint-refusal.log",
                # These fields are intentionally large and outside classifier input.
                "argv": ["irrelevant"] * 80,
                "diagnostic_blob": {f"unused-{i}": "x" * 200 for i in range(80)},
            },
            "snapshots": snapshots(seed),
            "unconsumed_fingerprint_detail": ["large"] * 100,
        }

    location_fp = fingerprint(102)
    location = {
        "reproduces_pinned": True, "source_intact_after_stages": True,
        "fingerprint_check": {"complete": True,
                              "snapshots_match_default_pins": True,
                              "unconsumed": "large" * 100},
        "fingerprint": location_fp,
        "unused_location_diagnostics": ["large"] * 100,
    }
    for index, variant in enumerate(p.VARIANTS):
        variants[variant] = {
            "status": "COMPLETE", "source_intact_after_stages": True,
            "original_preserved": True, "original_sha256": original,
            "verified_sha256": h(200 + index),
            "normal_mir_check": {"complete": True,
                                 "payload": {f"unused-{i}": i for i in range(100)}},
            "fingerprint_check": {"complete": True,
                                  "snapshots_match_default_pins": True,
                                  "classification": "unused"},
            "fingerprint": fingerprint(200 + index),
            "unused_variant_payload": {f"unused-{i}": [i] * 20 for i in range(100)},
        }
    return {
        "schema": "r21-fractional-forget-fingerprint-v1", "mode": "fingerprint",
        "classification": "SYNTHETIC", "complete": True, "accepted": False,
        "proof_credit": False, "body_proof_run": False,
        "base_source": {"original_sha256": original,
                        "verified_sha256": base_verified,
                        "unused_file": "ignored"},
        "snapshot_pins": defaults, "variant_order": list(p.VARIANTS),
        "location_control": location, "variants": variants,
        "unused_root_noise": {f"noise-{i}": [i] * 50 for i in range(100)},
    }


def ptr_tokens(pointer: str):
    if pointer == "":
        return []
    return [x.replace("~1", "/").replace("~0", "~") for x in pointer[1:].split("/")]


def get_node(root, pointer):
    node = root
    for token in ptr_tokens(pointer):
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node


def full_recursive_request_count(value):
    """Count pages for the former strategy: recurse into every container."""
    if isinstance(value, dict):
        count = max(1, (len(value) + 19) // 20)
        return count + sum(full_recursive_request_count(child)
                           for child in value.values()
                           if isinstance(child, (dict, list)))
    if isinstance(value, list):
        count = max(1, (len(value) + 19) // 20)
        return count + sum(full_recursive_request_count(child)
                           for child in value
                           if isinstance(child, (dict, list)))
    return 0


def kind(value):
    if isinstance(value, dict): return "object"
    if isinstance(value, list): return "array"
    if value is None: return "null"
    if type(value) is bool: return "boolean"
    if type(value) is int: return "integer"
    if isinstance(value, str): return "string"
    raise AssertionError(type(value))


class SyntheticBrief:
    def __init__(self, root):
        self.root = root
        self.calls = []

    def __call__(self, pointer, offset=None, value_start=None):
        self.calls.append((pointer, offset, value_start))
        if "/unused_" in pointer or pointer.endswith("/argv") or "diagnostic_blob" in pointer:
            raise AssertionError("projection traversed an intentionally omitted subtree")
        node = get_node(self.root, pointer)
        if isinstance(node, dict):
            items = list(node.items())
            start = 0 if offset is None else offset
            page = items[start:start + 20]
            results = []
            for key, value in page:
                child_pointer = (pointer + "/" if pointer else "/") + str(key).replace("~", "~0").replace("/", "~1")
                row = {"pointer": child_pointer, "kind": kind(value), "exact": True}
                if isinstance(value, (dict, list)):
                    row["child_count"] = len(value)
                else:
                    row["value"] = value
                results.append(row)
            total = len(items)
            next_offset = start + len(page) if start + len(page) < total else None
            selected_kind, child_count = "object", total
        elif isinstance(node, list):
            start = 0 if offset is None else offset
            page = list(enumerate(node))[start:start + 20]
            results = []
            for index, value in page:
                row = {"pointer": f"{pointer}/{index}", "kind": kind(value), "exact": True}
                if isinstance(value, (dict, list)):
                    row["child_count"] = len(value)
                else:
                    row["value"] = value
                results.append(row)
            next_offset = start + len(page) if start + len(page) < len(node) else None
            selected_kind, child_count = "array", len(node)
        else:
            results = [{"pointer": pointer, "kind": kind(node), "value": node,
                        "exact": True, "complete": True}]
            next_offset, selected_kind, child_count = None, kind(node), 0
        request = {"pointer": pointer, "file_id": FILE,
                   "expected_sha256": FILE_SHA}
        if offset is not None: request["offset"] = offset
        if value_start is not None: request["value_start"] = value_start
        return {
            "schema": "smallsort-targeted-observation-v2", "status": "OK",
            "exact": True, "complete": next_offset is None,
            "selected_kind": selected_kind, "child_count": child_count,
            "offset": 0 if offset is None else offset, "next_offset": next_offset,
            "build_id": BUILD, "file_id": FILE, "file_path": "synthetic.json",
            "file_sha256": FILE_SHA, "index_sha256": INDEX_SHA,
            "archive_sha256": ARCHIVE_SHA,
            "request_id": f"request-{len(self.calls)}",
            "request": request,
            "coverage": {"synthetic": True}, "results": results,
        }


class ProjectionTests(unittest.TestCase):
    def projector(self, root=None):
        service = SyntheticBrief(make_record() if root is None else root)
        return p.Projector(service, build_id=BUILD, file_id=FILE,
                           expected_sha256=FILE_SHA), service

    def test_projection_passes_unchanged_strict_classifier_and_skips_noise(self):
        projector, service = self.projector()
        bundle = projector.run()
        pins = proof.fingerprint_to_pins(bundle["projected_record"])
        self.assertIs(proof.validate_pins(pins), pins)
        self.assertEqual(bundle["receipt"]["identity"], {
            "build_id": BUILD, "file_id": FILE, "file_path": "synthetic.json",
            "file_sha256": FILE_SHA, "index_sha256": INDEX_SHA,
            "archive_sha256": ARCHIVE_SHA,
        })
        self.assertEqual(bundle["receipt"]["coverage"], {"coverage": {"synthetic": True}})
        self.assertLess(len(service.calls), 200)
        self.assertLess(len(service.calls), full_recursive_request_count(make_record()))
        self.assertFalse(any("unused" in pointer for pointer, _, _ in service.calls))
        self.assertIn("stage argv", " ".join(bundle["receipt"]["omitted_fields"]))

    def test_missing_record_field_fails_projection_and_classifier(self):
        tree = make_record()
        del tree["variants"]["positive"]["normal_mir_check"]["complete"]
        projector, _ = self.projector(tree)
        with self.assertRaises(p.ProjectionError):
            projector.run()

        record = self.projector()[0].run()["projected_record"]
        del record["variants"]["positive"]["normal_mir_check"]
        with self.assertRaises(RuntimeError):
            proof.fingerprint_to_pins(record)

    def test_wrong_type_inexact_error_and_identity_drift_refuse(self):
        wrong = make_record()
        wrong["variants"]["positive"]["fingerprint"]["body_proof_run"] = 0
        with self.assertRaises(p.ProjectionError):
            self.projector(wrong)[0].run()

        projector, service = self.projector()
        original_call = service.__call__
        def inexact(pointer, offset=None, value_start=None):
            d = original_call(pointer, offset, value_start)
            if pointer == "": d["exact"] = False
            return d
        projector.call = inexact
        with self.assertRaises(p.ProjectionError):
            projector.run()

        projector, service = self.projector()
        original_call = service.__call__
        calls = 0
        def drifting(pointer, offset=None, value_start=None):
            nonlocal calls
            calls += 1
            d = original_call(pointer, offset, value_start)
            if calls == 2: d["index_sha256"] = "d" * 64
            return d
        projector.call = drifting
        with self.assertRaises(p.ProjectionError):
            projector.run()

    def test_unexpected_request_selector_fields_refuse(self):
        for extra in ({"offset": 0}, {"value_start": 0}, {"selector": "lines"}):
            with self.subTest(extra=extra):
                projector, service = self.projector()
                original_call = service.__call__
                def unexpected(pointer, offset=None, value_start=None, *, extra=extra):
                    d = original_call(pointer, offset, value_start)
                    if pointer == "":
                        d["request"].update(extra)
                    return d
                projector.call = unexpected
                with self.assertRaises(p.ProjectionError):
                    projector.run()

    def test_server_offset_only_pagination_and_error_refusal(self):
        projector, service = self.projector()
        # Root has >20 direct children; the second selector must use the
        # exact server-supplied continuation offset.
        tree = make_record()
        tree.update({f"extra-{i}": i for i in range(30)})
        projector, service = self.projector(tree)
        bundle = projector.run()
        self.assertIsInstance(bundle["projected_record"], dict)
        root_calls = [offset for pointer, offset, _ in service.calls if pointer == ""]
        self.assertEqual(root_calls, [None, 20, 40])

        projector, service = self.projector()
        original_call = service.__call__
        def error(pointer, offset=None, value_start=None):
            d = original_call(pointer, offset, value_start)
            if pointer == "": d["status"] = "ERROR"
            return d
        projector.call = error
        with self.assertRaises(p.ProjectionError):
            projector.run()

    def test_server_value_start_is_followed_and_unfinished_string_is_refused(self):
        projector, service = self.projector()
        original_call = service.__call__
        stage_pointer = "/variants/positive/fingerprint/stage"
        stdout_pointer = stage_pointer + "/stdout"
        suffix = "nine-body-fingerprint-refusal.log"[9:]

        def partial_then_complete(pointer, offset=None, value_start=None):
            d = original_call(pointer, offset, value_start)
            if pointer == stage_pointer:
                for row in d["results"]:
                    if row["pointer"] == stdout_pointer:
                        row["value"] = "nine-body"
                        row["next_value_start"] = 9
            elif pointer == stdout_pointer and value_start == 9:
                d["results"] = [{"pointer": pointer, "kind": "string", "value": suffix,
                                 "exact": True, "complete": True}]
                d["request"]["value_start"] = 9
            return d

        projector.call = partial_then_complete
        projected = projector.run()["projected_record"]
        self.assertEqual(projected["variants"]["positive"]["fingerprint"]["stage"]["stdout"],
                         "nine-body-fingerprint-refusal.log")
        self.assertTrue(any(value_start == 9 for _, _, value_start in service.calls))

        projector, service = self.projector()
        original_call = service.__call__
        def truncated_without_continuation(pointer, offset=None, value_start=None):
            d = original_call(pointer, offset, value_start)
            if pointer == stage_pointer:
                for row in d["results"]:
                    if row["pointer"] == stdout_pointer:
                        row["value"] = "nine-body"
                        row["complete"] = False
            return d
        projector.call = truncated_without_continuation
        with self.assertRaises(p.ProjectionError):
            projector.run()


if __name__ == "__main__":
    unittest.main()
