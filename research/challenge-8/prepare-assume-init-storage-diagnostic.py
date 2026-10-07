#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted exact-source assume_init export and storage-read diagnostic.

No extraction summary or permission bridge is used. Export/certificate failures
are inconclusive. Acceptance of this component is never inferred here.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path


SOURCE_SHA = "7d588bf99e1bd7293b4b9c40fd71a6d5ed71ec6945920b166fc0c90547785702"
SOURCE_SIGNATURE = b"pub const unsafe fn assume_init(self) -> T"
SOURCE_BODY = (
    b"{\n"
    b"        // SAFETY: the caller must guarantee that `self` is initialized.\n"
    b"        // This also means that `self` must be a `value` variant.\n"
    b"        unsafe {\n"
    b"            intrinsics::assert_inhabited::<T>();\n"
    b"            // We do this via a raw ptr read instead of `ManuallyDrop::into_inner` so that there's\n"
    b"            // no trace of `ManuallyDrop` in Miri's error messages here.\n"
    b"            (&raw const self.value).cast::<T>().read()\n"
    b"        }\n    }"
)
HELPER = "sort4_certified_maybeuninit::sort4_checked_assume_init"
SIGNATURE = (
    b"pub unsafe fn sort4_checked_assume_init<Element>(storage: MaybeUninit<*const Element>) -> *const Element"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def source_certificate(repo: Path, matrix) -> tuple[bytes, bytes, dict]:
    source = (repo / "library/core/src/mem/maybe_uninit.rs").read_bytes()
    require(matrix.sha(source) == SOURCE_SHA, "MaybeUninit source changed")
    body = matrix.extract_braced_item(source, SOURCE_SIGNATURE)
    require(body == SOURCE_BODY, "assume_init exact source body changed")
    union = matrix.extract_braced_item(source, matrix.UNION_SIGNATURE)
    specialized = body.replace(b"self.value", b"storage.value").replace(b"::<T>", b"::<*const Element>")
    require(specialized.count(b"(&raw const storage.value)") == 1 and
            specialized.count(b"::<*const Element>") == 2, "specialization flow changed")
    return union, specialized, {
        "source_sha256": SOURCE_SHA,
        "source_signature": SOURCE_SIGNATURE.decode(),
        "source_body_sha256": matrix.sha(body),
        "specialized_body_sha256": matrix.sha(specialized),
        "union_item_sha256": matrix.sha(union),
        "substitutions": ["self -> storage", "T -> *const Element"],
        "source_body_exact": True,
        "runtime_signature_limit": "ordinary unsafe pointer adapter; generic const method not proved",
        "storage_route": "existing open_MaybeUninit, full union-variant pointer, ordinary read",
        "resource_bridge_added": False,
    }


def make_source(repo: Path, matrix) -> tuple[bytes, bytes, dict]:
    union, body, certificate = source_certificate(repo, matrix)
    # Ghost statements leave the runtime source body byte-exact after stripping.
    annotated = body.replace(
        b"        unsafe {", b"        //@ open std::mem::MaybeUninit_pointer_own::<Element>()(t, storage);\n"
        b"        //@ std::mem::open_MaybeUninit::<*Element>(&storage);\n        unsafe {", 1)
    annotated = annotated.replace(
        b".read()\n", b".read()\n            //@ std::mem::close_MaybeUninit::<*Element>(&storage);\n", 1)
    require(matrix.strip_ghost_annotations(annotated) == body, "annotation changes runtime body")
    contract = matrix.ghost_block(
        b"req thread_token(?t) &*& t == currentThread &*& "
        b"std::mem::MaybeUninit::inner(storage) == some(?value) &*& "
        b"std::mem::MaybeUninit_pointer_own::<Element>()(t, storage);\n"
        b"ens thread_token(t) &*& result == value &*& raw_ptr_own::<Element>()(t, result);\n"
        b"on_unwind_ens false;")
    verified = (
        b"#![feature(core_intrinsics, transparent_unions)]\n#![allow(internal_features)]\n\n"
        b"mod sort4_certified_maybeuninit {\n"
        b"    use std::mem::ManuallyDrop;\n    use std::intrinsics;\n"
        b"#[repr(transparent)]\npub union MaybeUninit<T> " + union + b"\n\n    " +
        SIGNATURE + b"\n" + contract + annotated + b"\n}\n")
    return matrix.strip_ghost_annotations(verified), verified, certificate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--activate", action="store_true")
    args = parser.parse_args()
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux", "GitHub-hosted Linux required")
    repo = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location(
        "assume_init_diagnostic_matrix", repo / "research/challenge-8/check-maybeuninit-new-pointer.py")
    require(spec is not None and spec.loader is not None, "matrix loader missing")
    matrix = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(matrix)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    original, verified, certificate = make_source(repo, matrix)
    for name, content in (("original", original), ("verified", verified)):
        (evidence / name).mkdir()
        (evidence / name / "lib.rs").write_bytes(content)
    fixture = {
        "variant": "assume_init_storage_diagnostic",
        "tool_profile": os.environ.get("SORT4_SELECT_PROFILE"),
        "original_sha256": matrix.sha(original),
        "verified_sha256": matrix.sha(verified),
        "source_certificate": certificate,
        "permission_bridge_added": False,
    }
    (evidence / "fixture.json").write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n")
    if args.activate:
        os.environ["SORT4_ASSUME_INIT_REPO_ROOT"] = str(repo)
    runner = matrix.run_case(evidence, args.schema, args.tool_home,
                            args.compiler_sysroot, repo, "assume_init_storage",
                            "diagnostic", certificate_mode=False)
    log = (evidence / "verifast.log").read_text(errors="replace")
    errors = [line for line in log.splitlines() if ": error:" in line or "Fatal error:" in line]
    stage = runner.get("stage_integrity", {})
    summary = {
        "classification": "INCONCLUSIVE", "accepted_component": False,
        "full_select_proved": False, "fixture": fixture,
        "body_entered": f"Verifying function '{HELPER}'" in log,
        "first_causal_error": errors[0] if errors else None,
        "target_read_permission_reached": False,
        "source_integrity": set(stage) == {"exporter", "decode", "verifast", "refinement"} and
            all(value.get("unchanged") is True for value in stage.values()),
        "runner_result": runner,
    }
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: summary[key] for key in (
        "classification", "body_entered", "first_causal_error")}))
    require(summary["source_integrity"] and runner.get("exporter_exit") == 0 and
            runner.get("decode_exit") == 0 and runner.get("refinement_exit") == 0,
            "diagnostic source/export/decode/refinement failure")


if __name__ == "__main__":
    main()
