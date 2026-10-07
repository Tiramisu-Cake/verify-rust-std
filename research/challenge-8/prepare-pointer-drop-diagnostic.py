#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted source-linked pointer drop method diagnostic, without a new drop rule.

Exports the exact specialization and records why the existing free drop contract
does or does not establish the intended complete-cell/no-unwind post. No outcome
of this diagnostic constitutes component acceptance.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path


METHOD_SHA = "d35858d6b1ec693d5e01b994e2d8248f73c7062c151e75e73ea635456fc82098"
GLUE_SHA = "325d69d3ce0fef9099f985febc5b712bbdb3563364648adc1396a365699987aa"
METHOD_SIGNATURE = b"pub const unsafe fn drop_in_place(self)"
METHOD_BODY = (
    b"{\n"
    b"        // SAFETY: the caller must uphold the safety contract for `drop_in_place`.\n"
    b"        unsafe { drop_in_place(self) }\n"
    b"    }"
)
LOCAL_SIGNATURE = (
    b"pub unsafe fn sort4_checked_pointer_drop<Element>(slot: *mut *const Element)"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def source_certificate(repo: Path, matrix) -> tuple[bytes, dict]:
    source = (repo / "library/core/src/ptr/mut_ptr.rs").read_bytes()
    glue = (repo / "library/core/src/ptr/mod.rs").read_bytes()
    require(matrix.sha(source) == METHOD_SHA, "pointer method source pin changed")
    require(matrix.sha(glue) == GLUE_SHA, "compiler drop-glue source pin changed")
    body = matrix.extract_braced_item(source, METHOD_SIGNATURE)
    require(body == METHOD_BODY, "pointer drop method body changed")
    require(body.count(b"drop_in_place(self)") == 1, "method call is not unique")
    specialized = body.replace(b"drop_in_place(self)", b"std::ptr::drop_in_place(slot)")
    return specialized, {
        "method_source_sha256": METHOD_SHA,
        "compiler_glue_source_sha256": GLUE_SHA,
        "method_body_sha256": matrix.sha(body),
        "specialized_body_sha256": matrix.sha(specialized),
        "specialization": "T = *const Element; receiver *mut *const Element",
        "binding_changes": ["self -> slot", "scope-bound drop_in_place -> std::ptr::drop_in_place"],
        "source_body_exact": True,
        "compiler_glue_body_proved": False,
        "new_drop_rule_active": False,
        "target_normal_post": "same complete cell value and thread; caller frame retained",
        "target_unwind_post": "false",
        "pointee_resources": "none for Element; initialized pointer cell mandatory",
    }


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
    spec = importlib.util.spec_from_file_location(
        "pointer_drop_diagnostic_matrix",
        repo / "research/challenge-8/check-maybeuninit-new-pointer.py")
    require(spec is not None and spec.loader is not None, "matrix loader missing")
    matrix = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(matrix)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    body, certificate = source_certificate(repo, matrix)
    # The stock free-drop pre contains the existing empty raw-pointer own.
    # Close its definition explicitly; no Element storage is supplied.
    body = body.replace(
        b"        unsafe { std::ptr::drop_in_place(slot) }",
        b"        //@ close raw_ptr_own::<Element>()(t, value);\n"
        b"        unsafe { std::ptr::drop_in_place(slot) }")
    contract = matrix.ghost_block(
        b"req thread_token(?t) &*& t == currentThread &*& *slot |-> ?value;\n"
        b"ens thread_token(t) &*& *slot |-> value;\n"
        b"on_unwind_ens false;")
    probe = (
        b"pub unsafe fn sort4_pointer_drop_frame_probe<Element>(slot: *mut *const Element, frame: *const u8)\n" +
        matrix.ghost_block(
            b"req thread_token(?t) &*& t == currentThread &*& *slot |-> ?value &*& [?f](*frame |-> ?frame_value);\n"
            b"ens thread_token(t) &*& *slot |-> value &*& [f](*frame |-> frame_value);\n"
            b"on_unwind_ens false;") +
        b"{ unsafe { sort4_checked_pointer_drop(slot) } }\n")
    verified = LOCAL_SIGNATURE + b"\n" + contract + body + b"\n\n" + probe
    original = matrix.strip_ghost_annotations(verified)
    (evidence / "verified").mkdir()
    (evidence / "original").mkdir()
    (evidence / "verified/lib.rs").write_bytes(verified)
    (evidence / "original/lib.rs").write_bytes(original)
    (evidence / "source-certificate.json").write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    (evidence / "fixture.json").write_text(json.dumps({
        "variant": "pointer_drop_existing",
        "original_sha256": matrix.sha(original),
        "verified_sha256": matrix.sha(verified),
        "source_certificate": certificate,
        "explicit_empty_pointer_own_closed": True,
    }, indent=2, sort_keys=True) + "\n")
    runner = matrix.run_case(evidence, args.schema, args.tool_home,
                             args.compiler_sysroot, repo, "pointer_drop_existing",
                             "diagnostic", certificate_mode=False)
    log = (evidence / "verifast.log").read_text(errors="replace")
    errors = [line for line in log.splitlines() if ": error:" in line]
    stage = runner.get("stage_integrity", {})
    summary = {
        "classification": "INCONCLUSIVE",
        "accepted_component": False,
        "full_select_proved": False,
        "tool_profile": os.environ.get("SORT4_SELECT_PROFILE"),
        "source_certificate": certificate,
        "source_exact": matrix.strip_ghost_annotations(verified) == original,
        "source_integrity": set(stage) == {"exporter", "decode", "verifast", "refinement"} and
            all(value.get("unchanged") is True for value in stage.values()),
        "method_body_entered": "Verifying function 'sort4_checked_pointer_drop'" in log,
        "method_return_seen": "Executing return statement" in log,
        "first_causal_error": errors[0] if errors else None,
        "runner_result": runner,
    }
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: summary[key] for key in (
        "classification", "method_body_entered", "first_causal_error")}))
    require(summary["source_integrity"] and
            runner.get("exporter_exit") == 0 and runner.get("decode_exit") == 0 and
            runner.get("refinement_exit") == 0, "diagnostic setup/source/refinement failure")


if __name__ == "__main__":
    main()
