#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted proof of the pointer-value post omitted only for prototype compatibility.

This lemma has no relation to an Element pointee.  The target actual helper
still needs a separate full body proof under its unchanged pointer equality.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
VARIANTS = ("positive", "false_post", "pointee_rights",
            "thread_duplication", "wrong_pointer")
PRED_SOURCE = Path("bin/rust/rust_belt/general.rsspec")
PRED_DEFINITION = b"pred_ctor raw_ptr_own<T>()(t: thread_id_t, v: *T;) = true;"
TYPE_DEFINITION = b"type_pred_def for <T> <*T>.own = raw_ptr_own::<T>;"
SOURCE_PREFIX = b"#![allow(dead_code)]\n\n/*@\n"
LEMMA = (b"lem complete_selected_pointer_own<Element>(\n"
         b"    t: thread_id_t, condition: bool,\n"
         b"    true_val: *Element, false_val: *Element, result: *Element)\n"
         b"    req thread_token(t) &*& (result as pointer) ==\n"
         b"        (if condition { true_val as pointer } else { false_val as pointer });\n"
         b"    ens thread_token(t) &*& (result as pointer) ==\n"
         b"        (if condition { true_val as pointer } else { false_val as pointer }) &*&\n"
         b"        raw_ptr_own::<Element>()(t, result);\n"
         b"{\n"
         b"    close raw_ptr_own::<Element>()(t, result);\n"
         b"}\n")
SOURCE_SUFFIX = (
    b"@*/\n\npub fn completion_fixture_anchor()\n"
    b"/*@\nreq thread_token(?t) &*& t == currentThread;\n@*/\n"
    b"/*@\nens thread_token(t);\n@*/\n"
    b"/*@\non_unwind_ens false;\n@*/\n"
    b"{}\n"
)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


HELPER = load(HERE / "check-helper.py", "owner_completion_runner")
OWNER = load(HERE / "prepare-actual-owner-projection.py",
             "owner_completion_source")


def source_pair(variant: str) -> tuple[bytes, bytes]:
    HELPER.require(variant in VARIANTS, "unknown owner completion variant")
    lemma = LEMMA
    post = (b"        raw_ptr_own::<Element>()(t, result);")
    if variant == "false_post":
        lemma = lemma.replace(post, post[:-1] + b" &*& false;")
    elif variant == "pointee_rights":
        lemma = lemma.replace(post, post[:-1] + b" &*& *result |-> _;")
    elif variant == "thread_duplication":
        lemma = lemma.replace(post,
                              post[:-1] + b" &*& thread_token(t);")
    elif variant == "wrong_pointer":
        # A result equal to the selected value need not equal the other one.
        lemma = lemma.replace(post, post[:-1] + b" &*& (result as pointer) == "
                              b"(if condition { false_val as pointer } else "
                              b"{ true_val as pointer });")
    verified = SOURCE_PREFIX + lemma + SOURCE_SUFFIX
    original = OWNER.strip_ghost(verified)
    HELPER.require(OWNER.strip_ghost(verified) == original and
                   verified.count(b"close raw_ptr_own::<Element>()(t, result);") == 1,
                   "completion source/definitional close changed")
    return original, verified


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--variant", choices=VARIANTS, default="positive")
    args = parser.parse_args()
    HELPER.require((os.environ.get("GITHUB_ACTIONS"),
                    os.environ.get("RUNNER_ENVIRONMENT"),
                    os.environ.get("RUNNER_OS")) ==
                   ("true", "github-hosted", "Linux"),
                   "owner completion proof requires GitHub-hosted Linux")
    args.evidence = args.evidence.resolve()
    HELPER.require(not args.evidence.exists(), "refusing to overwrite evidence")
    definition = (args.tool_home / PRED_SOURCE).read_bytes()
    HELPER.require(definition.count(PRED_DEFINITION) == 1 and
                   definition.count(TYPE_DEFINITION) == 1,
                   "raw pointer value-own definition/binding changed")
    original, verified = source_pair(args.variant)
    case = args.evidence
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_bytes(original)
    (case / "verified/lib.rs").write_bytes(verified)
    os.environ.pop("SORT4_ACTUAL_OWNER_REPO_ROOT", None)
    os.environ.pop("SORT4_ACTUAL_FORGET_REPO_ROOT", None)
    os.environ.pop("SORT4_G1_CALL_REPO_ROOT", None)
    stages = HELPER.run_case(case, args, prove=True)
    log = (case / "full-verification.log").read_text(errors="replace") if (
        case / "full-verification.log").is_file() else ""
    errors = HELPER.error_info(log)
    frontend = all(stages.get(key, {}).get("exit") == 0 for key in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    proof = stages.get("full-verification", {}).get("exit")
    lemma_headers = len(re.findall(
        r"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^)]*\): "
        r"Verifying function 'complete_selected_pointer_own'", log))
    unchanged = all(stage.get("source_unchanged") is True for stage
                    in stages.values() if stage.get("status") == "RAN")
    classification = "INCONCLUSIVE"
    if args.variant == "positive" and frontend and proof == 0 and \
            not errors and lemma_headers == 1 and unchanged:
        classification = "EXPERIMENTAL_OWNER_POST_COMPLETION_PROVED"
    elif args.variant != "positive" and frontend and proof == 1 and \
            lemma_headers == 1 and unchanged and len(errors) == 1:
        # O17 (37717092130) established these exact normal-post obligations.
        # Historical O17 labels remain in its immutable evidence; only future
        # classifications use this stricter, reviewed predicate/location map.
        expected = {
            "false_post": "Cannot prove condition. (Cannot prove false.)",
            "pointee_rights":
                "No matching heap chunks: points_to_<Element>(result, _)",
            "thread_duplication":
                "No matching heap chunks: thread_token(t)",
            "wrong_pointer": "Cannot prove condition. (Cannot prove result = "
                             "(condition ? false_val : true_val).)",
        }
        error = errors[0]
        if error["file"] == "verified/lib.rs" and error["line"] == "11" and \
                error["message"] == expected[args.variant]:
            classification = "INTENDED_OWNER_COMPLETION_POST_NEGATIVE"
    result = {
        "classification": classification, "variant": args.variant,
        "actual_helper_proved": False,
        "full_pointer_value_post_derived":
            classification == "EXPERIMENTAL_OWNER_POST_COMPLETION_PROVED",
        "actual_body_and_lemma_composed": False,
        "raw_pointer_own_definition": PRED_DEFINITION.decode(),
        "raw_pointer_type_binding": TYPE_DEFINITION.decode(),
        "raw_pointer_own_source": str(PRED_SOURCE),
        "original_sha256": HELPER.digest(original),
        "verified_sha256": HELPER.digest(verified),
        "source_integrity": OWNER.strip_ghost(verified) == original,
        "source_unchanged_across_stages": unchanged,
        "lemma_verification_headers": lemma_headers,
        "frontend_refinement": frontend, "full_verifier_exit": proof,
        "first_error": errors[0] if errors else None, "stages": stages,
    }
    (case / "summary.json").write_text(json.dumps(
        result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"variant": args.variant,
                      "classification": classification,
                      "first_error": result["first_error"]}), flush=True)


if __name__ == "__main__":
    main()
