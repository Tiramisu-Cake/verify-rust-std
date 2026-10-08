#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted source-only diagnostic for actual select's truthful guard owner.

This prepares an exact-runtime ghost candidate; it installs no frontend rule
and claims no proof of the actual helper, generic forget, or nested Drop.
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
OWNER_PRED = (
    b"/*@\npred<T> <select_unpredictable::DropOnPanic<T>>.own(t, g) =\n"
    b"    *g.inner |-> ?payload &*& <T>.own(t, payload);\n@*/\n"
)
OPEN_WRAPPERS = (
    b"    /*@ std::mem::open_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>); @*/\n"
    b"    /*@ std::mem::open_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>); @*/\n"
    b"    /*@ assert *true_ptr |-> ?true_payload; @*/\n"
    b"    /*@ assert *false_ptr |-> ?false_payload; @*/\n"
)
CLOSE_OWNER = (
    b"        /*@ if (condition) {\n"
    b"                 close raw_ptr_own::<Element>()(t, true_payload);\n"
    b"                 close <select_unpredictable::DropOnPanic<*Element>>.own(t, guard);\n"
    b"             } else {\n"
    b"                 close raw_ptr_own::<Element>()(t, false_payload);\n"
    b"                 close <select_unpredictable::DropOnPanic<*Element>>.own(t, guard);\n"
    b"             } @*/\n"
)
CLOSE_UNSELECTED = (
    b"        /*@ if (condition) {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);\n"
    b"             } else {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);\n"
    b"             } @*/\n"
)
OPEN_OWNER = (
    b"        /*@ open <select_unpredictable::DropOnPanic<*Element>>.own(t, guard); @*/\n"
    b"        /*@ assert *guard.inner |-> ?selected_payload; @*/\n"
    b"        /*@ open raw_ptr_own::<Element>()(t, selected_payload); @*/\n"
)
CLOSE_SELECTED = (
    b"        /*@ if (condition) {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);\n"
    b"             } else {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);\n"
    b"             } @*/\n"
)
INSERTIONS = (
    (b"    let false_ptr = false_val.as_mut_ptr();\n", OPEN_WRAPPERS),
    (b"        let guard = DropOnPanic { inner: guard };\n", CLOSE_OWNER),
    (b"        drop.drop_in_place();\n", CLOSE_UNSELECTED + OPEN_OWNER),
    (b"        crate::mem::forget(guard);\n", CLOSE_SELECTED),
)


def load_actual():
    path = HERE / "prepare-actual-helper-capture.py"
    spec = importlib.util.spec_from_file_location("overnight_actual_owner_base", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("actual helper source preparer unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ACTUAL = load_actual()


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def strip_ghost(source: bytes) -> bytes:
    source = re.sub(rb"(?m)^[ \t]*/\*@.*?@\*/(?:\r?\n)?", b"", source,
                    flags=re.S)
    return re.sub(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)", b"", source)


def candidate(base_verified: bytes, base_original: bytes,
              owner_post_completion: bool = False) -> bytes:
    verified = base_verified
    normal_post = (b"    (if condition { true_val as pointer } else { false_val as pointer });")
    require(verified.count(normal_post) == 1, "normal pointer post changed")
    if not owner_post_completion:
        # Historical O16 diagnostic: this stronger implementation post is
        # rejected by the generic std prototype before any body proof.
        after = (b"    (if condition { true_val as pointer } else { false_val as pointer }) "
                 b"&*& raw_ptr_own::<Element>()(t, result);")
        verified = verified.replace(normal_post, after, 1)
    for anchor, ghost in INSERTIONS:
        require(verified.count(anchor) == 1,
                f"actual owner insertion anchor ambiguous: {anchor.decode()}")
        verified = verified.replace(anchor, anchor + ghost, 1)
    require(verified.endswith(b"}\n") and verified.count(OWNER_PRED) == 0,
            "actual helper final source boundary changed")
    verified += OWNER_PRED
    require(strip_ghost(verified) == base_original,
            "ghost projection changed actual runtime bytes")
    require(verified.count(b"crate::mem::forget(guard);") == 1 and
            verified.count(b"unsafe { self.inner.drop_in_place() }") == 1 and
            verified.count(b"crate::intrinsics::select_unpredictable(") == 3,
            "actual call/destructor inventory changed")
    return verified


def write_case(repo: Path, out: Path,
               owner_post_completion: bool = False) -> dict:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux",
            "actual owner fixture requires GitHub-hosted Linux")
    require(not out.exists(), f"refusing to overwrite {out}")
    base = out / "baseline"
    base_record = ACTUAL.write_fixture(repo, base)
    base_verified = (base / "verified/lib.rs").read_bytes()
    base_original = (base / "original/lib.rs").read_bytes()
    verified = candidate(base_verified, base_original,
                         owner_post_completion=owner_post_completion)
    case = out / "owner-projection"
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_bytes(base_original)
    (case / "verified/lib.rs").write_bytes(verified)
    record = {
        "classification": "SOURCE_AND_MIR_CAPTURE_ONLY",
        "actual_helper_proved": False,
        "actual_nested_drop_proved": False,
        "actual_safe_forget_linked": False,
        "owner_post_completion": owner_post_completion,
        "actual_normal_post": "prototype-compatible thread plus exact full selected pointer",
        "full_pointer_value_post_status": (
            "requires separately checked completion lemma; no actual helper proof"
            if owner_post_completion else "O16 prototype-incompatible diagnostic"),
        "target_specialization": "T = *const Element; Element unrestricted",
        "source_certificate": base_record["source_certificate"],
        "original_sha256": ACTUAL.digest(base_original),
        "verified_sha256": ACTUAL.digest(verified),
        "baseline_original_sha256": base_record["original_sha256"],
        "ghost_strip_identity": True,
        "qualified_nominal_owner": OWNER_PRED.decode(),
        "ordered_ghost_blocks": [OPEN_WRAPPERS.decode(), CLOSE_OWNER.decode(),
                                 CLOSE_UNSELECTED.decode(), OPEN_OWNER.decode(),
                                 CLOSE_SELECTED.decode()],
        "expected_call_inventory": {
            "pointer_select": 2, "wrapper_select": 1,
            "pointer_drop": 1, "safe_forget": 1, "assume_init": 1},
    }
    (case / "fixture.json").write_text(json.dumps(record, indent=2,
                                                  sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--owner-post-completion", action="store_true",
                        help="keep prototype-compatible post; require separate checked lemma")
    args = parser.parse_args()
    print(json.dumps(write_case(args.repo, args.out,
                                owner_post_completion=args.owner_post_completion),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
