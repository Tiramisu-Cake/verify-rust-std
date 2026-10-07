#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Prepare a hosted, ghost-only MaybeUninit storage permission diagnostic.

This does not export or prove the pinned assume_init Rust body and cannot
accept that component. It isolates existing open_MaybeUninit permissions.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def load_matrix(repo: Path):
    path = repo / "research/challenge-8/check-maybeuninit-new-pointer.py"
    spec = importlib.util.spec_from_file_location("constructor", path)
    require(spec is not None and spec.loader is not None, "constructor loader missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux", "GitHub-hosted Linux required")
    repo = Path(__file__).resolve().parents[2]
    matrix = load_matrix(repo)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    cast_body = (b"    //@ std::mem::open_MaybeUninit::<*Element>(storage);\n"
                 b"    //@ assert *(storage as **Element) |-> value;\n"
                 b"    //@ std::mem::close_MaybeUninit::<*Element>(storage);")
    union_term = ("*(union_variant_ptr(storage as pointer, "
                  "typeid(std::mem::MaybeUninit<*Element>), 1) as **Element)")
    union_assert = ("assert " + union_term + " |-> ?loaded;").encode()
    cast_assert = b"assert *(storage as **Element) |-> ?loaded;"
    cases = [
        ("cast_self_open_close",
         b"*storage |-> std::mem::MaybeUninit::new(?value);",
         b"*storage |-> std::mem::MaybeUninit::new(value);",
         cast_body, None, "cast-self `*storage as **Element` cell; open/assert/close"),
        ("union_field_some",
         b"*storage |-> std::mem::MaybeUninit::new(?value);",
         b"*storage |-> std::mem::MaybeUninit::new(value);",
         b"    //@ std::mem::open_MaybeUninit::<*Element>(storage);\n    //@ " + union_assert,
         union_assert, union_term),
        ("cast_self_none",
         b"*storage |-> std::mem::MaybeUninit::new_maybe_uninit(none);",
         b"*storage |-> std::mem::MaybeUninit::new_maybe_uninit(none);",
         b"    //@ std::mem::open_MaybeUninit::<*Element>(storage);\n    //@ " + cast_assert,
         cast_assert, "*(storage as **Element)"),
        ("cast_self_unknown", b"*storage |-> ?wrapper;",
         b"*storage |-> wrapper;",
         b"    //@ std::mem::open_MaybeUninit::<*Element>(storage);\n    //@ " + cast_assert,
         cast_assert, "*(storage as **Element)"),
    ]
    results = []
    for name, cell_pre, cell_post, body, target, term in cases:
        case = evidence / name
        case.mkdir()
        framed_pre = cell_pre.rstrip().removesuffix(b";") + b" &*& *frame |-> ?frame_value;"
        # Preserve exactly the same outer cell/frame on normal return.
        post = cell_post.rstrip().removesuffix(b";") + b" &*& *frame |-> frame_value;"
        body = (body + b"\n    //@ assert *frame |-> frame_value;")
        framed_sig = (b"pub unsafe fn " + name.encode() +
                      b"<Element>(storage: *mut std::mem::MaybeUninit<*const Element>, frame: *mut u8)")
        contract = matrix.ghost_block(
            b"req thread_token(?t) &*& t == currentThread &*& " + framed_pre + b"\n"
            b"ens thread_token(t) &*& " + post + b"\n"
            b"on_unwind_ens false;")
        verified = b"#![allow(dead_code)]\n\n" + framed_sig + b"\n" + contract + b"{\n" + body + b"\n}\n"
        original = matrix.strip_ghost_annotations(verified)
        lines = verified.decode().splitlines()
        target_line = next((i for i, line in enumerate(lines, 1)
                            if target is not None and target.decode() in line), None)
        fixture = {
            "variant": name, "runtime_empty_ghost_probe": True,
            "source_linked_assume_init_body": False,
            "component_acceptance": False, "permission_bridge_added": False,
            "precondition": framed_pre.decode(), "postcondition": post.decode(),
            "target_assertion": target.decode() if target else None,
            "target_assertion_line": target_line, "target_term": term,
            "expected_stage": "positive control" if target is None else "named read-cell assertion",
        }
        for sub, content in (("original", original), ("verified", verified)):
            (case / sub).mkdir()
            (case / sub / "lib.rs").write_bytes(content)
        fixture.update({"original_sha256": matrix.sha(original),
                        "verified_sha256": matrix.sha(verified),
                        "tool_profile": os.environ.get("SORT4_SELECT_PROFILE")})
        (case / "fixture.json").write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n")
        result = matrix.run_case(case, args.schema, args.tool_home,
                                 args.compiler_sysroot, repo,
                                 "assume_init_permission_probe", "diagnostic",
                                 certificate_mode=False)
        log = (case / "verifast.log").read_text(errors="replace")
        errors = [line for line in log.splitlines() if ": error:" in line or "Fatal error:" in line]
        stages = result.get("stage_integrity", {})
        source_integrity = (set(stages) == {"exporter", "decode", "verifast", "refinement"} and
                            all(stage.get("unchanged") is True for stage in stages.values()))
        error_line = None
        if errors:
            match = re.search(r"verified/lib\.rs\((\d+),", errors[0])
            error_line = int(match.group(1)) if match else None
        proof_header = f"Verifying function '{name}'"
        error_prefix = log.split(errors[0], 1)[0] if errors else ""
        last_header = error_prefix.rfind("Verifying function '")
        failure_in_probe = last_header >= 0 and error_prefix[last_header:].startswith(proof_header)
        target_reached = (target_line is not None and error_line in
                          {target_line, target_line + 1} and failure_in_probe)
        if name == "cast_self_open_close":
            classification = "CAST_SELF_PASS" if result.get("verifast_exit") == 0 else "CAST_SELF_INCONCLUSIVE"
        elif name == "union_field_some" and result.get("verifast_exit") == 0:
            classification = "UNION_FIELD_PERMISSION_AVAILABLE"
        elif target_reached and len(errors) == 1 and re.search(
                r"verified/lib\.rs\(\d+,\d+-\d+\): error: No matching heap chunks: "
                r"points_to<\*Element>\([^\n]*union_variant_ptr_provenance", errors[0]):
            classification = "TARGETED_READ_PERMISSION_MISSING"
        else:
            classification = "INCONCLUSIVE_WRONG_STAGE_OR_OBLIGATION"
        (case / "probe-summary.json").write_text(json.dumps({
            "classification": classification,
            "proof_function_entered": proof_header in log,
            "target_error": errors[0] if errors else None,
            "target_error_source_line": error_line,
            "target_obligation_reached": target_reached,
            "source_integrity": source_integrity,
            "runner_result": result,
        }, indent=2, sort_keys=True) + "\n")
        require(source_integrity and result.get("exporter_exit") == 0 and
                result.get("decode_exit") == 0 and result.get("refinement_exit") == 0,
                f"{name}: exporter/decode/refinement/source integrity failure")
        results.append({"case": name, "classification": classification,
                        "verifast_exit": result.get("verifast_exit"),
                        "target_assertion_line": target_line,
                        "target_error_source_line": error_line,
                        "first_error": errors[0] if errors else None})
    (evidence / "matrix-summary.json").write_text(json.dumps({
        "classification": "DIAGNOSTIC_NOT_ACCEPTANCE",
        "source_linked_assume_init_body": False,
        "permission_bridge_added": False,
        "cases": results,
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps(results))


if __name__ == "__main__":
    main()
