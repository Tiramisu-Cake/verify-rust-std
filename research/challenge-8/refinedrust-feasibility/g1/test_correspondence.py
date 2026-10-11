"""Small synthetic service tests for the read-only G1 output classifier.

No compiler, proof runner, extractor, cloud client or network code is imported.
"""

import hashlib
import tempfile
import unittest
from pathlib import Path

from correspondence import inspect_outputs


SOURCE = Path(__file__).resolve().parents[4] / "library/core/src/slice/sort/shared/smallsort.rs"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_lines() -> dict[str, int]:
    lines = SOURCE.read_text().splitlines()
    return {
        "first_fnmut": next(i for i, s in enumerate(lines, 1) if "if !is_less(&*tail, &*sift)" in s),
        "tail_read": next(i for i, s in enumerate(lines, 1) if "let tmp = ManuallyDrop::new(tail.read())" in s),
        "gap_copy": next(i for i, s in enumerate(lines, 1) if "ptr::copy_nonoverlapping(sift, gap_guard.dst, 1)" in s),
        "late_fnmut": next(i for i, s in enumerate(lines, 1) if "if !is_less(&tmp, &*sift)" in s),
        "normal_guard_drop": next(i for i, s in enumerate(lines, 1) if "let mut gap_guard = CopyOnDrop" in s),
        "late_guard_drop": next(i for i, s in enumerate(lines, 1) if "let mut gap_guard = CopyOnDrop" in s),
    }


MIR = """fn insert_tail(_1: *mut T, _2: *mut T, _3: &mut F) -> () {
    debug tmp => _7;
    debug gap_guard => _8;
    bb0: {
        _4 = <F as FnMut>::call_mut(move _3, move _5) -> [return: bb1, unwind: cleanup bb10];
    }
    bb1: {
        _7 = ptr::read(move _2) -> [return: bb2, unwind: cleanup bb10];
    }
    bb2: {
        _9 = ptr::copy_nonoverlapping(move _6, move _8, const 1_usize) -> [return: bb3, unwind: cleanup bb10];
    }
    bb3: {
        _11 = <F as FnMut>::call_mut(move _3, move _12) -> [return: bb4, unwind: cleanup bb12];
    }
    bb4: {
        drop(_8) -> [return: bb5, unwind: cleanup bb13];
    }
    bb5: {
        return;
    }
    bb10 (cleanup): {
        resume;
    }
    bb12 (cleanup): {
        drop(_8) -> [return: bb13, unwind terminate(cleanup)];
    }
    bb13 (cleanup): {
        resume;
    }
}
"""

RADIUM = """Program Definition insert_tail_def (FnMut_loc: loc) (read_loc: loc) (copy_loc: loc) (CopyOnDrop_DropGlue_loc: loc) : function :=
  {| f_code :=
     <[ "_bb0" := CallS FnMut_loc [] [] [@{expr} ] None (Goto "_bb1") (Goto "_bb10") ]>%E $
     <[ "_bb1" := CallS read_loc [] [] [@{expr} ] None (Goto "_bb2") (Goto "_bb10") ]>%E $
     <[ "_bb2" := CallS copy_loc [] [] [@{expr} ] None (Goto "_bb3") (Goto "_bb10") ]>%E $
     <[ "_bb3" := CallS FnMut_loc [] [] [@{expr} ] None (Goto "_bb4") (Goto "_bb12") ]>%E $
     <[ "_bb4" := CallS CopyOnDrop_DropGlue_loc [] [] [@{expr} ] None (Goto "_bb5") (Goto "_bb13") ]>%E $
     <[ "_bb10" := Unwind ]>%E $
     <[ "_bb12" := CallS CopyOnDrop_DropGlue_loc [] [] [@{expr} ] None (Goto "_bb13") (UnwindTerminate) ]>%E;
     f_init := "_bb0"; |}.
Final Obligation.
  solve_fn_vars_nodup.
Qed.
"""


class CorrespondenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="g1-correspondence-synthetic-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        original = SOURCE.read_bytes()
        self.original = self.root / "smallsort.rs"
        self.annotated = self.root / "annotated.rs"
        self.stripped = self.root / "stripped.rs"
        for path in (self.original, self.annotated, self.stripped):
            path.write_bytes(original)
        self.mir = self.root / "log/mir/insert_tail.after.mir"
        self.mir.parent.mkdir(parents=True)
        self.mir.write_text(MIR)
        self.radium = self.root / "output/core/generated/generated_code_core.v"
        self.radium.parent.mkdir(parents=True)
        self.radium.write_text(RADIUM)
        lines = source_lines()
        names = {
            "first_fnmut": (0, "<F as FnMut>::call_mut", "FnMut_loc"),
            "tail_read": (1, "ptr::read", "read_loc"),
            "gap_copy": (2, "ptr::copy_nonoverlapping", "copy_loc"),
            "late_fnmut": (3, "<F as FnMut>::call_mut", "FnMut_loc"),
            "normal_guard_drop": (4, "", "CopyOnDrop_DropGlue_loc"),
            "late_guard_drop": (12, "", "CopyOnDrop_DropGlue_loc"),
        }
        self.receipt = {
            "sources": {"smallsort": {
                "original_path": str(self.original),
                "original_sha256": digest(original),
                "annotated_path": str(self.annotated),
                "annotated_sha256": digest(original),
                "stripped_path": str(self.stripped),
            }},
            "locals": {"tmp": "_7", "gap_guard": "_8"},
            "correspondence": {
                label: {
                    "function": "insert_tail", "source_line": lines[label],
                    "mir_file": str(self.mir.relative_to(self.root)), "mir_sha256": digest(MIR.encode()),
                    "mir_bb": bb, "mir_callee": callee,
                    "radium_file": str(self.radium.relative_to(self.root)), "radium_sha256": digest(RADIUM.encode()),
                    "radium_definition": "insert_tail_def", "radium_bb": bb,
                    "radium_callee_binding": binding,
                    **({"radium_unwind_bb": 10 if label == "first_fnmut" else 12} if label in ("first_fnmut", "late_fnmut") else {}),
                }
                for label, (bb, callee, binding) in names.items()
            },
        }

    def test_synthetic_control_flow_observed_but_full_admission_incomplete(self) -> None:
        result = inspect_outputs(self.root, self.receipt)
        self.assertEqual("INCONCLUSIVE", result["verdict"])
        self.assertFalse(result["admission_complete"])
        self.assertTrue(result["unproved"])
        self.assertTrue(all(c["status"] == "OBSERVED" for c in result["checks"] if c["id"].startswith("event:")))
        self.assertEqual("OBSERVED", next(c for c in result["checks"] if c["id"] == "radium_unwind_paths")["status"])

    def test_missing_map_is_inconclusive(self) -> None:
        self.receipt["correspondence"] = {}
        result = inspect_outputs(self.root, self.receipt)
        self.assertEqual("INCONCLUSIVE", result["verdict"])
        self.assertEqual(6, sum(c["id"].startswith("event:") for c in result["checks"]))

    def test_certified_ghost_strip_checks_annotated_bytes(self) -> None:
        original = self.original.read_bytes()
        anchor = b"unsafe fn insert_tail<T, F: FnMut(&T, &T) -> bool>"
        offset = original.index(anchor)
        added = b"#[rr::verify]\n"
        annotated = original[:offset] + added + original[offset:]
        self.annotated.write_bytes(annotated)
        self.receipt["sources"]["smallsort"]["annotated_sha256"] = digest(annotated)
        self.receipt["insertions"] = {"smallsort": [{
            "original_offset": offset, "annotated_offset": offset, "inserted_hex": added.hex(),
            "inserted_sha256": digest(added),
        }]}
        result = inspect_outputs(self.root, self.receipt)
        self.assertEqual("OBSERVED", next(c for c in result["checks"] if c["id"] == "source_identity")["status"])
        self.assertEqual("INCONCLUSIVE", result["verdict"])

        altered = annotated.replace(b"let mut sift = tail.sub(1);", b"let mut sift = tail.sub(2);")
        self.annotated.write_bytes(altered)
        self.receipt["sources"]["smallsort"]["annotated_sha256"] = digest(altered)
        result = inspect_outputs(self.root, self.receipt)
        self.assertEqual("STOP", next(c for c in result["checks"] if c["id"] == "source_identity")["status"])

    def test_comment_marker_does_not_count_as_mapped_call(self) -> None:
        fake = MIR.replace("_11 = <F as FnMut>::call_mut", "// <F as FnMut>::call_mut\n        _11 = unrelated")
        self.mir.write_text(fake)
        for entry in self.receipt["correspondence"].values():
            entry["mir_sha256"] = digest(fake.encode())
        result = inspect_outputs(self.root, self.receipt)
        self.assertEqual("INCONCLUSIVE", result["verdict"])
        self.assertEqual("NOT_OBSERVED", next(c for c in result["checks"] if c["id"] == "event:late_fnmut")["status"])

    def test_receipt_cannot_read_outside_selected_evidence_root(self) -> None:
        self.receipt["correspondence"]["tail_read"]["mir_file"] = "../p0/other.mir"
        self.receipt["sources"]["smallsort"]["original_path"] = str(SOURCE)
        result = inspect_outputs(self.root, self.receipt)
        self.assertEqual("INCONCLUSIVE", result["verdict"])
        self.assertEqual("INCONCLUSIVE", next(c for c in result["checks"] if c["id"] == "event:tail_read")["status"])
        self.assertEqual("INCONCLUSIVE", next(c for c in result["checks"] if c["id"] == "source_identity")["status"])

    def test_payload_drop_is_stop(self) -> None:
        bad = MIR.replace("bb5: {\n        return;", "bb5: {\n        drop(_7) -> [return: bb6, unwind: cleanup bb13];\n    }\n    bb6: {\n        return;")
        self.mir.write_text(bad)
        for entry in self.receipt["correspondence"].values():
            entry["mir_sha256"] = digest(bad.encode())
        result = inspect_outputs(self.root, self.receipt)
        self.assertEqual("STOP", result["verdict"])
        self.assertEqual("STOP", next(c for c in result["checks"] if c["id"] == "payload_drop")["status"])

    def test_panic_free_annotation_at_fnmut_is_stop(self) -> None:
        bad = RADIUM.replace("<[ \"_bb0\" := CallS FnMut_loc", "<[ \"_bb0\" := annot{ 1 }: UnwindFreeAnnot;\n      CallS FnMut_loc")
        self.radium.write_text(bad)
        for entry in self.receipt["correspondence"].values():
            entry["radium_sha256"] = digest(bad.encode())
        result = inspect_outputs(self.root, self.receipt)
        self.assertEqual("STOP", result["verdict"])
        self.assertEqual("STOP", next(c for c in result["checks"] if c["id"] == "fnmut_unwind_policy")["status"])

    def test_missing_late_cleanup_is_inconclusive(self) -> None:
        bad = MIR.replace("bb12 (cleanup): {\n        drop(_8) -> [return: bb13, unwind terminate(cleanup)];", "bb12 (cleanup): {\n        goto -> bb13;")
        self.mir.write_text(bad)
        for entry in self.receipt["correspondence"].values():
            entry["mir_sha256"] = digest(bad.encode())
        result = inspect_outputs(self.root, self.receipt)
        self.assertEqual("STOP", result["verdict"])
        self.assertEqual("STOP", next(c for c in result["checks"] if c["id"] == "late_unwind")["status"])


if __name__ == "__main__":
    unittest.main()
