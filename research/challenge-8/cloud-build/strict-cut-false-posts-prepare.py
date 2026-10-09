#!/usr/bin/env python3
"""Cloud-only exact ghost-post mutants from the frozen strictCUT positives."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

TEMPLATE_SHA = "7cb5c8a8a2541da30af188c8731ee13276c59b206e5ed58a78e909852719359e"
MUTANTS = {
    "normal-false": (
        "positive_basic", b"/*@ ens true; @*/", b"/*@ ens false; @*/"),
    "unwind-false": (
        "positive_direct_unwind",
        b"/*@ on_unwind_ens lifetime_token(?unwind_k); @*/",
        b"/*@ on_unwind_ens lifetime_token(?unwind_k) &*& false; @*/"),
}


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_capture(path: Path):
    spec = importlib.util.spec_from_file_location("strict_cut_frozen_capture", path)
    need(spec is not None and spec.loader is not None, "frozen capture unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare(proof_root: Path, controls: Path, output: Path) -> dict:
    capture = load_capture(proof_root / "research/challenge-8/overnight-lifetime/capture.py")
    template = (proof_root / "research/challenge-8/overnight-lifetime/cases.rs").read_bytes()
    need(sha(template) == TEMPLATE_SHA, "lifetime template pin changed")
    need(output.is_dir() and not (output / "source-manifest.json").exists() and
         not (output / "cases").exists(),
         "false-post evidence must be a fresh prepared Cloud directory")
    rows = {}
    for key, (case, old, new) in MUTANTS.items():
        source = capture.select_case(template, case)
        baseline = controls / "cases" / case / case
        need(source == (baseline / "verified/lib.rs").read_bytes(),
             f"{key}: positive parent source differs")
        need(source.count(old) == 1 and source.count(new) == 0,
             f"{key}: target post occurrence changed")
        at = source.index(old)
        changed = source[:at] + new + source[at + len(old):]
        original = capture.strip_ghost(source)
        need(capture.strip_ghost(changed) == original ==
             (baseline / "original/lib.rs").read_bytes(),
             f"{key}: runtime source changed")
        need(changed.replace(new, old, 1) == source,
             f"{key}: mutation is not exactly reversible")
        root = output / "cases" / key
        (root / "verified").mkdir(parents=True)
        (root / "original").mkdir()
        (root / "verified/lib.rs").write_bytes(changed)
        (root / "original/lib.rs").write_bytes(original)
        post_line = changed.count(b"\n", 0, at) + 1
        rows[key] = {
            "parent_case": case, "target_function": case,
            "parent_verified_sha256": sha(source),
            "mutant_verified_sha256": sha(changed),
            "original_sha256": sha(original),
            "old_post_utf8": old.decode(), "new_post_utf8": new.decode(),
            "old_post_count": 1, "new_post_count": 1,
            "post_line_one_based": post_line,
            "post_column_zero_based": at - (changed.rfind(b"\n", 0, at) + 1),
            "runtime_source_unchanged": True,
            "only_target_post_changed": True,
            "accepted": False,
        }
    result = {"classification": "FALSE_POST_SOURCES_PREPARED_DIAGNOSTIC_ONLY",
              "template_sha256": TEMPLATE_SHA, "cases": rows,
              "accepted": False, "actual_sort4_accepted": False}
    (output / "source-manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    for key in ("proof-root", "controls-evidence", "evidence"):
        p.add_argument("--" + key, type=Path, required=True)
    a = p.parse_args()
    prepare(a.proof_root, a.controls_evidence, a.evidence)


if __name__ == "__main__":
    main()
