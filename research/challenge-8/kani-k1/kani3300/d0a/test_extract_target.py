import json
import tempfile
import unittest
from pathlib import Path

from extract_target import PROPERTY, SPEC_EQ, fragment, read_bounded, summarize


LOC = {"file": "/sysroot/library/core/src/array/equality.rs", "line": "157", "function": SPEC_EQ}
ROOT = "array_value_as_used_by_merge_output"
EQ = "std::array::equality::<impl std::cmp::PartialEq for [u8; 4]>::eq"


def result():
    def call(name, typ="function-call"):
        return {"stepType": typ, "function": {"displayName": name}}
    def assign(lhs, data):
        return {"stepType": "assignment", "lhs": lhs, "value": {"data": data}}
    trace = [{"stepType": "location-only"}, call("__CPROVER_initialize"),
             call("__CPROVER_initialize", "function-return"), call(ROOT)]
    trace += [assign("MEM_INIT_STATE." + k, v) for k, v in
              [("tracked_object_id", "9ul"), ("tracked_offset", "0ul"), ("value", "FALSE")]]
    trace += [call(EQ), call(SPEC_EQ)]
    for data in ["TRUE", "FALSE"]:
        trace += [call("kani::mem_init::MemoryInitializationState::get::<4>"),
                  assign("var_0", data), call("kani::mem_init::MemoryInitializationState::get::<4>", "function-return")]
    trace += [{"stepType": "failure", "property": PROPERTY + "2", "sourceLocation": LOC}]
    return {"description": "uninit", "property": PROPERTY + "2", "sourceLocation": dict(LOC),
            "status": "FAILURE", "trace": trace}


def encoded(obj):
    return json.dumps([{"result": [obj]}], indent=2).encode()


class ExtractTests(unittest.TestCase):
    def test_complete_fragment_inside_truncated_outer_capture(self):
        data = encoded(result())[:-4]
        found = fragment(data, "2")
        self.assertEqual(found["state"], "COMPLETE_RESULT_FRAGMENT")
        self.assertEqual(summarize(found["object"])["last_state_writes"]["value"]["value"]["data"], "FALSE")

    def test_partial_property_is_not_recovered(self):
        self.assertEqual(fragment(encoded(result())[:-100], "2")["state"], "PARTIAL")

    def test_missing_and_nested_headers(self):
        self.assertEqual(fragment(b'[]', "2")["state"], "UNAVAILABLE")
        nested = b'            {\n              "description": "x",\n              "property": ' + json.dumps(PROPERTY + "2").encode() + b'}'
        self.assertEqual(fragment(nested, "2")["state"], "UNAVAILABLE")

    def test_duplicate_property_headers_are_ambiguous(self):
        self.assertEqual(fragment(encoded(result()) * 2, "2")["state"], "UNAVAILABLE")

    def test_utf8_cap_after_complete_fragment(self):
        self.assertEqual(fragment(encoded(result()) + b'\n\xe2', "2")["state"], "COMPLETE_RESULT_FRAGMENT")

    def test_source_stage_target_and_status_mismatch(self):
        for field, value in [("property", PROPERTY + "1"), ("status", "SUCCESS")]:
            obj = result(); obj[field] = value
            with self.assertRaises(ValueError): summarize(obj)
        for field, value in [("file", "other.rs"), ("line", "158"), ("function", "other")]:
            obj = result(); obj["sourceLocation"][field] = value
            with self.assertRaises(ValueError): summarize(obj)

    def test_missing_null_wrong_type_empty_trace(self):
        for value in [None, {}, [], [None]]:
            obj = result(); obj["trace"] = value
            with self.assertRaises(ValueError): summarize(obj)
        obj = result(); del obj["trace"]
        with self.assertRaises(ValueError): summarize(obj)

    def test_partial_endpoint_and_wrong_open_stack(self):
        obj = result(); obj["trace"].pop()
        with self.assertRaises(ValueError): summarize(obj)
        obj = result(); obj["trace"].insert(-1, {"stepType": "function-call", "function": {"displayName": "unexpected"}})
        with self.assertRaises(ValueError): summarize(obj)

    def test_whole_state_write_invalidates_field_last_claim(self):
        obj = result(); obj["trace"].insert(-1, {"stepType": "assignment", "lhs": "MEM_INIT_STATE", "value": {"name": "struct"}})
        with self.assertRaises(ValueError): summarize(obj)

    def test_bounded_read(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture"; path.write_bytes(b"12345")
            self.assertEqual(read_bounded(path, 5), b"12345")
            with self.assertRaises(ValueError): read_bounded(path, 4)


if __name__ == "__main__":
    unittest.main()
