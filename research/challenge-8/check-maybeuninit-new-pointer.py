#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Prepare and check the narrowly certified MaybeUninit constructor profile.

All compilation, MIR export/decode, VeriFast, and refinement work is guarded
for GitHub-hosted Linux Actions. This script only prepares disposable fixtures;
it never edits repository Rust sources.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


HINT_SHA256 = "d94ef86fbdac952fe7c9a6028536e15539b33dc188966fa4e9340fa7d94c30f8"
HINT_BLOB = "fe59166363b9cc049c0d48f4349f4dc9c0e458b8"
MAYBE_UNINIT_SHA256 = "7d588bf99e1bd7293b4b9c40fd71a6d5ed71ec6945920b166fc0c90547785702"
MANUALLY_DROP_SHA256 = "17e8e41866d3eadcfdc6f1a516e4ed9dd5555e10ad725aac3b04aec7c759731b"
MAYBE_DANGLING_SHA256 = "1cf24b2ec36fff143f329f2ef6db5b4d47cfa798da7f30d88b554b712c8f4b53"

SELECT_SCRIPT = "prepare-and-check-sort4-select.py"
CERT_MODULE = "sort4_certified_maybeuninit"
CERT_FUNCTION = "sort4_checked_maybeuninit_new"
CERT_FUNCTION_PATH = f"{CERT_MODULE}::{CERT_FUNCTION}"
CERT_DIAGNOSTIC = "SORT4-MAYBEUNINIT:"
RUST_SOURCE_NEW_CALL = b"MaybeUninit::new("
MIR_EXTERNAL_NEW = b"std::mem::MaybeUninit::<T>::new"
UNION_SIGNATURE = b"pub union MaybeUninit<T>"
NEW_SIGNATURE = b"pub const fn new(val: T) -> MaybeUninit<T>"
EXPECTED_NEW_BODY = b"{\n        MaybeUninit { value: ManuallyDrop::new(val) }\n    }"
INTRINSIC_SELECT = b"crate::intrinsics::select_unpredictable("


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def strict_proof_negative(evidence: dict[str, bool]) -> bool:
    """Accept a negative only after the named proof obligation was reached."""
    required = (
        "proof_expected", "integrity_and_frontend_ok", "verifier_failed",
        "target_obligation", "intended_message", "no_applicability_rejection",
        "named_probe_entered", "error_in_named_probe", "constructor_body_checked",
        "external_call_count_exact", "redirect_count_exact",
    )
    return all(evidence.get(key) is True for key in required)


def extract_braced_item(source: bytes, signature: bytes) -> bytes:
    require(source.count(signature) == 1,
            f"expected one source item signature: {signature.decode('ascii')}")
    start = source.index(signature)
    opening = source.find(b"{", start + len(signature))
    require(opening >= 0, "source item has no opening brace")
    depth = 0
    state = "code"
    block_depth = 0
    i = opening
    while i < len(source):
        byte = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else 0
        if state == "line":
            if byte == 10:
                state = "code"
        elif state == "block":
            if byte == 47 and nxt == 42:
                block_depth += 1
                i += 1
            elif byte == 42 and nxt == 47:
                block_depth -= 1
                i += 1
                if block_depth == 0:
                    state = "code"
        elif state == "string":
            if byte == 92:
                i += 1
            elif byte == 34:
                state = "code"
        elif state == "char":
            if byte == 92:
                i += 1
            elif byte == 39:
                state = "code"
        elif byte == 47 and nxt == 47:
            state = "line"
            i += 1
        elif byte == 47 and nxt == 42:
            state = "block"
            block_depth = 1
            i += 1
        elif byte == 34:
            state = "string"
        elif byte == 39:
            closing = source.find(b"'", i + 1, min(len(source), i + 10))
            if closing >= 0:
                state = "char"
        elif byte == 123:
            depth += 1
        elif byte == 125:
            depth -= 1
            if depth == 0:
                return source[opening:i + 1]
        i += 1
    raise ValueError("unterminated source item")


def load_select_module(repo_root: Path):
    path = repo_root / "research/challenge-8" / SELECT_SCRIPT
    spec = importlib.util.spec_from_file_location("sort4_select_prepare", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the existing select fixture preparer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def certify_repository_sources(repo_root: Path) -> dict:
    paths = {
        "hint": repo_root / "library/core/src/hint.rs",
        "maybe_uninit": repo_root / "library/core/src/mem/maybe_uninit.rs",
        "manually_drop": repo_root / "library/core/src/mem/manually_drop.rs",
        "maybe_dangling": repo_root / "library/core/src/mem/maybe_dangling.rs",
    }
    contents = {key: path.read_bytes() for key, path in paths.items()}
    expected = {
        "hint": HINT_SHA256,
        "maybe_uninit": MAYBE_UNINIT_SHA256,
        "manually_drop": MANUALLY_DROP_SHA256,
        "maybe_dangling": MAYBE_DANGLING_SHA256,
    }
    actual = {key: sha(value) for key, value in contents.items()}
    for key in expected:
        require(actual[key] == expected[key],
                f"pinned {key} source SHA-256 mismatch: {actual[key]}")
    hint_blob = subprocess.check_output(
        ["git", "-C", str(repo_root), "hash-object", str(paths["hint"])],
        text=True,
    ).strip()
    require(hint_blob == HINT_BLOB, f"pinned hint.rs blob mismatch: {hint_blob}")

    hint_body = load_select_module(repo_root).extract_body(contents["hint"])
    require(hint_body.count(INTRINSIC_SELECT) == 3,
            "pinned select body must retain exactly three intrinsics")
    require(hint_body.count(RUST_SOURCE_NEW_CALL) == 2,
            "pinned select body must retain exactly two MaybeUninit::new calls")

    union = extract_braced_item(contents["maybe_uninit"], UNION_SIGNATURE)
    new_body = extract_braced_item(contents["maybe_uninit"], NEW_SIGNATURE)
    require(union == b"{\n    uninit: (),\n    value: ManuallyDrop<T>,\n}",
            "pinned MaybeUninit union field definition changed")
    require(new_body == EXPECTED_NEW_BODY,
            "pinned MaybeUninit::new body changed")
    return {
        "repository_root": str(repo_root),
        "files": {
            key: {"path": str(paths[key]), "sha256": actual[key]}
            for key in paths
        },
        "hint_git_blob": hint_blob,
        "hint_body_sha256": sha(hint_body),
        "hint_intrinsic_call_count": hint_body.count(INTRINSIC_SELECT),
        "hint_external_maybeuninit_new_call_count": hint_body.count(RUST_SOURCE_NEW_CALL),
        "external_mir_constructor_def_path": MIR_EXTERNAL_NEW.decode("ascii"),
        "union_item_sha256": sha(union),
        "constructor_body_sha256": sha(new_body),
        "constructor_body_exact": True,
        "union_fields_exact": True,
        "manuallydrop_and_maybedangling_source_pinned": True,
        "exported_def_id_limitation": (
            "MIR exporter serializes def_path_str only; this source/MIR certificate "
            "is an explicit local-copy applicability link, not DefId equality"
        ),
    }


def ghost_block(contract: bytes) -> bytes:
    clauses = []
    current = []
    pending_comments = []
    for line in contract.splitlines():
        stripped = line.strip()
        if stripped.startswith((b"req ", b"ens ", b"on_unwind_ens ")):
            if current:
                clauses.append(current)
            current = pending_comments + [line]
            pending_comments = []
        elif stripped.startswith(b"// TARGET_"):
            pending_comments.append(line)
        elif current:
            current.append(line)
        elif stripped:
            pending_comments.append(line)
    if current:
        clauses.append(current)
    require(not pending_comments, "ghost marker/comment is not attached to a contract clause")
    require(bool(clauses), "empty ghost contract")
    return b"\n" + b"\n".join(
        b"/*@\n" + b"\n".join(clause) + b"\n@*/" for clause in clauses
    ) + b"\n"


def enable_crate_feature(source: bytes, feature: bytes) -> bytes:
    line = b"#![feature(" + feature + b")]"
    lines = source.splitlines(keepends=True)
    if any(existing.rstrip(b"\r\n") == line for existing in lines[:16]):
        return source
    insert_at = 0
    for index, existing in enumerate(lines):
        if existing.startswith(b"#!["):
            insert_at = index + 1
        else:
            break
    lines.insert(insert_at, line + b"\n")
    return b"".join(lines)


def strip_ghost_annotations(data: bytes) -> bytes:
    data = re.sub(rb"/\*@.*?@\*/", b"", data, flags=re.S)
    return re.sub(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)", b"", data)


def constructor_source(cert: dict, variant: str = "positive") -> tuple[bytes, bytes, dict]:
    maybe_source = (Path(cert["files"]["maybe_uninit"]["path"])).read_bytes()
    union = extract_braced_item(maybe_source, UNION_SIGNATURE)
    fields = union[1:-1]
    body = extract_braced_item(maybe_source, NEW_SIGNATURE)
    require(body == EXPECTED_NEW_BODY, "constructor body no longer matches pinned expression")

    # The source's manual Copy impl is not part of this constructor proof;
    # pointer instantiation is Copy without adding a local Clone body.
    union_attrs = b"#[repr(transparent)]\n"
    local_union = union_attrs + b"pub union MaybeUninit<T> " + union + b"\n"
    helper_contract = (
        b"req thread_token(?t) &*& t == currentThread;\n"
        b"ens thread_token(t) &*& "
        b"std::mem::MaybeUninit::inner(result) == some(val) &*& "
        b"std::mem::MaybeUninit_pointer_own::<Element>()(t, result);\n"
        b"on_unwind_ens false;"
    )
    signature = (
        b"pub fn " + CERT_FUNCTION.encode() +
        b"<Element>(val: *const Element) -> MaybeUninit<*const Element>"
    )
    helper_annotation = ghost_block(helper_contract)
    helper_body = body
    if variant == "wrong_active_field":
        helper_body = b"{\n        MaybeUninit { uninit: () }\n    }"
    elif variant in {"wrong_value", "wrong_operand"}:
        helper_body = b"{\n        MaybeUninit { value: ManuallyDrop::new(std::ptr::null::<Element>()) }\n    }"
    elif variant == "wrong_return":
        helper_body = (
            b"{\n        let wrapped = MaybeUninit { value: ManuallyDrop::new(val) };\n"
            b"        wrapped\n    }"
        )
    elif variant == "extra_operation":
        helper_body = (
            b"{\n        std::hint::black_box(val);\n"
            b"        MaybeUninit { value: ManuallyDrop::new(val) }\n    }"
        )

    local_module = (
        b"mod " + CERT_MODULE.encode() + b" {\n"
        b"    use std::mem::ManuallyDrop;\n"
        + local_union
        + b"\n    " + signature + helper_annotation + b"    " + helper_body + b"\n"
        b"}\n"
    )

    # The value being wrapped is deliberately unconstrained as a pointee: no
    # predicate mentions *val.  The two unrelated cells exercise framing.
    probe_contract = (
        b"req thread_token(?t) &*& t == currentThread &*& "
        b"[?f](*frame |-> ?frame_value) &*& *other |-> ?other_value;\n"
        b"ens thread_token(t) &*& [f](*frame |-> frame_value) &*& "
        b"*other |-> other_value &*& result == val;\n"
        b"on_unwind_ens false;"
    )
    probe_assert = (
        b"    //@ assert std::mem::MaybeUninit::inner(wrapped) == some(val);\n"
        b"    //@ open std::mem::MaybeUninit_pointer_own::<Element>()(t, wrapped);\n"
        b"    //@ open raw_ptr_own::<Element>()(t, val);\n"
        b"    //@ close std::mem::MaybeUninit_pointer_own::<Element>()(t, "
        b"std::mem::MaybeUninit::new_maybe_uninit(none));\n"
        b"    //@ open std::mem::MaybeUninit_pointer_own::<Element>()(t, "
        b"std::mem::MaybeUninit::new_maybe_uninit(none));\n"
        b"    // TARGET_FRAME_ASSERTION\n"
        b"    //@ assert [f](*frame |-> frame_value) &*& *other |-> other_value;\n"
    )
    probe_signature = (
        b"pub fn sort4_checked_maybeuninit_frame_probe<Element>(\n"
        b"    val: *const Element, frame: *const u8, other: *mut i32,\n"
        b") -> *const Element\n"
    )
    if variant == "wrong_inner_post":
        probe_signature = (
            b"pub fn sort4_checked_maybeuninit_wrong_value_probe<Element>(\n"
            b"    val: *const Element, wrong: *const Element,\n"
            b"    frame: *const u8, other: *mut i32,\n"
            b") -> *const Element\n"
        )
        probe_contract = (
            b"req thread_token(?t) &*& t == currentThread &*& "
            b"(val as pointer) != (wrong as pointer) &*& "
            b"[?f](*frame |-> ?frame_value) &*& *other |-> ?other_value;\n"
            b"ens thread_token(t) &*& [f](*frame |-> frame_value) &*& "
            b"*other |-> other_value &*& result == val;\n"
            b"on_unwind_ens false;"
        )
        probe_assert = (
            b"    // TARGET_ASSERTION\n"
            b"    //@ assert std::mem::MaybeUninit::inner(wrapped) == some(wrong);\n"
            b"    //@ assert [f](*frame |-> frame_value) &*& *other |-> other_value;\n"
        )
    elif variant == "false_assert":
        probe_assert = (
            b"    // TARGET_ASSERTION\n"
            b"    //@ assert false;\n"
            b"    //@ assert [f](*frame |-> frame_value) &*& *other |-> other_value;\n"
        )
    elif variant == "false_uninit":
        probe_assert = (
            b"    // TARGET_ASSERTION\n"
            b"    //@ assert std::mem::MaybeUninit::inner(wrapped) == none;\n"
            b"    //@ assert [f](*frame |-> frame_value) &*& *other |-> other_value;\n"
        )
    elif variant == "resource_duplication":
        probe_assert = (
            b"    //@ assert std::mem::MaybeUninit::inner(wrapped) == some(val);\n"
            b"    // TARGET_ASSERTION\n"
            b"    //@ assert [f](*frame |-> frame_value) &*& "
            b"[f](*frame |-> frame_value);\n"
        )
    elif variant == "false_postcondition":
        probe_signature = (
            b"pub unsafe fn sort4_checked_maybeuninit_false_post_probe<Element>(\n"
            b"    val: *const Element, wrong: *const Element,\n"
            b"    frame: *const u8, other: *mut i32,\n"
            b") -> *const Element\n"
        )
        probe_contract = (
            b"req thread_token(?t) &*& t == currentThread &*& "
            b"(val as pointer) != (wrong as pointer) &*& "
            b"[?f](*frame |-> ?frame_value) &*& *other |-> ?other_value;\n"
            b"// TARGET_POSTCONDITION\n"
            b"ens thread_token(t) &*& [f](*frame |-> frame_value) &*& "
            b"*other |-> other_value &*& result == wrong;\n"
            b"on_unwind_ens false;"
        )
        probe_assert = (
            b"    //@ assert std::mem::MaybeUninit::inner(wrapped) == some(val);\n"
            b"    // TARGET_RETURN\n"
        )
    probe_signature = probe_signature.replace(b"pub fn ", b"pub unsafe fn ", 1)
    probe = (
        probe_signature
        + ghost_block(probe_contract)
        + b"{\n"
        b"    let wrapped = std::mem::MaybeUninit::new(val);\n"
        + probe_assert
        + b"    val\n"
        b"}\n"
    )
    if variant == "renamed_function":
        local_module = local_module.replace(
            CERT_FUNCTION.encode(), b"sort4_checked_maybeuninit_new_impostor", 1)
        probe = probe.replace(CERT_FUNCTION.encode(),
                              b"sort4_checked_maybeuninit_new_impostor")
    elif variant == "nonpointer_input":
        local_module = local_module.replace(
            b"<Element>(val: *const Element) -> MaybeUninit<*const Element>",
            b"<Element>(val: Element) -> MaybeUninit<Element>", 1)
    elif variant == "extra_union_field":
        local_module = local_module.replace(
            b"#[repr(transparent)]", b"#[repr(C)]", 1)
        local_module = local_module.replace(
            b"    value: ManuallyDrop<T>,\n", b"    value: ManuallyDrop<T>,\n    extra: u8,\n", 1)
    elif variant == "wrong_binding":
        probe = probe.replace(
            b"std::mem::MaybeUninit::new(val)",
            b"sort4_certified_maybeuninit::sort4_checked_maybeuninit_new(val)", 1)

    if variant == "nonpointer_identity":
        identity = (
            b"pub fn sort4_nonpointer_identity(\n"
            b"    input: std::mem::MaybeUninit<i32>,\n"
            b") -> std::mem::MaybeUninit<i32>\n"
            + ghost_block(
                b"req thread_token(?t) &*& t == currentThread;\n"
                b"ens thread_token(t);\n"
                b"on_unwind_ens false;"
            )
            + b"{\n    input\n}\n"
        )
        probe += b"\n" + identity

    prefix = b"#![feature(transparent_unions)]\n" + local_module + b"\n" + probe
    original_prefix = strip_ghost_annotations(prefix)
    verified_prefix = prefix
    require(strip_ghost_annotations(verified_prefix) == original_prefix,
            "constructor fixture changes runtime source beyond its declared variant")
    fixture_union = extract_braced_item(local_module, UNION_SIGNATURE)
    metadata = {
        "variant": variant,
        "local_function_path_suffix": CERT_FUNCTION_PATH,
        "expected_external_call_count": 1,
        "expected_union_fields": ["uninit: ()", "value: ManuallyDrop<T>"],
        "constructor_runtime_body_sha256": sha(body),
        "fixture_body_sha256": sha(helper_body),
        "fixture_union_fields_sha256": sha(fixture_union[1:-1]),
        "ghost_stripped_equal": True,
        "target_assertion_line": next((i for i, line in enumerate(verified_prefix.splitlines(), 1)
                                        if b"TARGET_ASSERTION" in line), None),
        "target_postcondition_line": next((i for i, line in enumerate(verified_prefix.splitlines(), 1)
                                           if b"TARGET_POSTCONDITION" in line), None),
        "target_return_line": next((i for i, line in enumerate(verified_prefix.splitlines(), 1)
                                     if b"TARGET_RETURN" in line), None),
    }
    return original_prefix, verified_prefix, metadata


def write_case(case_dir: Path, original: bytes, verified: bytes, metadata: dict) -> None:
    stripped = strip_ghost_annotations(verified)
    require(stripped == original,
            f"{case_dir.name}: original/verified runtime sources differ after ghost stripping")
    (case_dir / "original").mkdir(parents=True, exist_ok=False)
    (case_dir / "verified").mkdir()
    (case_dir / "original/lib.rs").write_bytes(original)
    (case_dir / "verified/lib.rs").write_bytes(verified)
    metadata["original_sha256"] = sha(original)
    metadata["verified_sha256"] = sha(verified)
    metadata["fixture_runtime_equal_after_ghost_strip"] = stripped == original
    (case_dir / "fixture.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


def file_hashes(paths: tuple[Path, ...], root: Path) -> dict[str, str]:
    return {str(path.relative_to(root)): sha(path.read_bytes()) for path in paths}


MIR_MUTATIONS = (
    "operand", "return", "active_field", "type", "identity", "extra_operation",
)

SOURCE_APPLICABILITY_REASONS = {
    "wrong_active_field": ("local constructor runtime body differs from repository", "source_certificate"),
    "wrong_operand": ("local constructor runtime body differs from repository", "source_certificate"),
    "wrong_return": ("local constructor runtime body differs from repository", "source_certificate"),
    "extra_operation": ("local constructor runtime body differs from repository", "source_certificate"),
    "renamed_function": ("constructor source marker missing", "source_certificate"),
    "wrong_binding": ("checked body shape or external call count differs", "redirect_count"),
    "nonpointer_input": ("constructor source marker missing", "source_certificate"),
    "extra_union_field": ("local union fields differ from repository", "source_certificate"),
}

MIR_APPLICABILITY_REASONS = {
    "operand": ("constructor operand: _1", "full_graph"),
    "return": ("constructor place: _0", "full_graph"),
    "active_field": ("constructor union identity/type/active field", "full_graph"),
    "type": ("checked constructor input is not *const Element", "typed_certificate"),
    "identity": ("expected exactly one checked constructor body", "typed_certificate"),
    "extra_operation": ("constructor first block statements", "full_graph"),
}


def replace_once(source: str, old: str, new: str, label: str) -> str:
    require(source.count(old) == 1,
            f"{label}: expected exactly one MIR mutation target, found {source.count(old)}")
    return source.replace(old, new, 1)


def mir_balanced_item(source: str, start: int) -> str:
    require(source[start] == "(", "MIR item must begin with a parenthesis")
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(source)):
        char = source[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise ValueError("MIR item has no closing parenthesis")


def mutate_constructor_mir(decoded: str, mutation: str) -> str:
    """Change one raw MIR fact after export; the Rust source remains pinned."""
    require(mutation in MIR_MUTATIONS, f"unknown MIR mutation: {mutation}")
    marker = f'defPath = "{CERT_FUNCTION_PATH}"'
    require(decoded.count(marker) == 1, "constructor MIR body identity is not unique")
    start = decoded.index(marker)
    end = decoded.index("      impSpan = (", start)
    body = decoded[start:end]
    if mutation == "operand":
        body = replace_once(body,
            'use = (\n                      copy = (\n                        local = (name = "_1")',
            'use = (\n                      copy = (\n                        local = (name = "_3")', mutation)
    elif mutation == "return":
        body = replace_once(body,
            'lhsPlace = (\n                    local = (name = "_0")',
            'lhsPlace = (\n                    local = (name = "_3")', mutation)
    elif mutation == "active_field":
        body = replace_once(body, "unionActiveField = 1", "unionActiveField = 0", mutation)
    elif mutation == "type":
        input_end = body.index("      localDecls = [")
        inputs = body[:input_end]
        inputs = replace_once(inputs, "mutability = (not = void)",
                              "mutability = (mut = void)", mutation)
        body = inputs + body[input_end:]
    elif mutation == "identity":
        body = replace_once(body, marker,
            f'defPath = "{CERT_FUNCTION_PATH}_impostor"', mutation)
    else:
        statements = body.index("          statements = [")
        first = body.index("( sourceInfo = (", statements)
        item = mir_balanced_item(body, first)
        body = body[:first] + item + ",\n            " + body[first:]
    mutated = decoded[:start] + body + decoded[end:]
    require(mutated != decoded, "MIR mutation had no effect")
    return mutated


def make_mir_mutation_tool_home(tool_home: Path, schema: Path, repo_root: Path,
                                case_dir: Path, mutation: str) -> Path:
    """Wrap only the exporter in a disposable per-control copy of the profile."""
    shadow = case_dir / "mutation-profile"
    binary_dir = shadow / "bin"
    binary_dir.mkdir(parents=True)
    source_bin = tool_home / "bin"
    for entry in source_bin.iterdir():
        if entry.name == "vf-rust-mir-exporter":
            continue
        target = binary_dir / entry.name
        if entry.name == "verifast" and entry.is_file():
            shutil.copy2(entry, target)
        else:
            target.symlink_to(entry, target_is_directory=entry.is_dir())
    wrapper = binary_dir / "vf-rust-mir-exporter"
    wrapper.write_text('''#!/usr/bin/env python3
import hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("sort4_constructor_matrix", @PREPARER@)
matrix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(matrix)
real = @REAL@
schema = @SCHEMA@
mutation = @MUTATION@
record = Path(@RECORD@)
argv = sys.argv[1:]
proc = subprocess.run([real, *argv], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
sys.stderr.buffer.write(proc.stderr)
if proc.returncode:
    sys.stdout.buffer.write(proc.stdout)
    raise SystemExit(proc.returncode)
selected = any(Path(arg).suffix == ".rs" and Path(arg).is_file() and
               matrix.CERT_FUNCTION.encode() in Path(arg).read_bytes() for arg in argv)
if not selected:
    sys.stdout.buffer.write(proc.stdout)
    raise SystemExit(0)
decoded = subprocess.run(["capnp", "decode", schema, "VfMir"], input=proc.stdout,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if decoded.returncode:
    sys.stderr.buffer.write(decoded.stderr)
    raise SystemExit(decoded.returncode)
try:
    original = decoded.stdout.decode()
    changed = matrix.mutate_constructor_mir(original, mutation)
except Exception as exc:
    record.write_text(json.dumps({"mutation": mutation, "error": str(exc)}) + "\\n")
    sys.stderr.write("SORT4-MAYBEUNINIT MIR mutant failed: " + str(exc) + "\\n")
    raise SystemExit(98)
encoded = subprocess.run(["capnp", "encode", schema, "VfMir"], input=changed.encode(),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if encoded.returncode:
    sys.stderr.buffer.write(encoded.stderr)
    raise SystemExit(encoded.returncode)
record.parent.mkdir(parents=True, exist_ok=True)
(record.parent / "canonical-mir.txt").write_text(original)
(record.parent / "mutated-mir.txt").write_text(changed)
record.write_text(json.dumps({"mutation": mutation, "matched": True,
    "exporter_exit": proc.returncode,
    "canonical_sha256": hashlib.sha256(proc.stdout).hexdigest(),
    "mutated_sha256": hashlib.sha256(encoded.stdout).hexdigest(),
    "selected_source_sha256": next(hashlib.sha256(Path(arg).read_bytes()).hexdigest()
        for arg in argv if Path(arg).suffix == ".rs" and Path(arg).is_file()),
    "real_exporter_sha256": hashlib.sha256(Path(real).read_bytes()).hexdigest(),
    "decode_exit": 0, "encode_exit": 0}, indent=2) + "\\n")
(record.parent / "canonical-mir.bin").write_bytes(proc.stdout)
(record.parent / "mutated-mir.bin").write_bytes(encoded.stdout)
sys.stdout.buffer.write(encoded.stdout)
'''.replace("@PREPARER@", repr(str(repo_root / "research/challenge-8/check-maybeuninit-new-pointer.py")))
   .replace("@REAL@", repr(str(source_bin / "vf-rust-mir-exporter")))
   .replace("@SCHEMA@", repr(str(schema)))
   .replace("@MUTATION@", repr(mutation))
   .replace("@RECORD@", repr(str(case_dir / "mutation-record.json"))))
    wrapper.chmod(0o755)
    (case_dir / "mutation-profile.json").write_text(json.dumps({
        "mutation": mutation,
        "base_console_sha256": sha((source_bin / "verifast").read_bytes()),
        "shadow_console_sha256": sha((binary_dir / "verifast").read_bytes()),
        "real_exporter_sha256": sha((source_bin / "vf-rust-mir-exporter").read_bytes()),
        "wrapper_sha256": sha(wrapper.read_bytes()),
    }, indent=2, sort_keys=True) + "\n")
    return shadow


def run_stage(argv: list[str | Path], cwd: Path, resource_path: Path,
              stdout_path: Path, stderr_path: Path | None = None,
              env: dict[str, str] | None = None) -> int:
    stderr_path = stdout_path if stderr_path is None else stderr_path
    with stdout_path.open("wb") as stdout:
        stderr = subprocess.STDOUT if stderr_path == stdout_path else stderr_path.open("wb")
        try:
            completed = subprocess.run(
                ["/usr/bin/time", "-v", "-o", str(resource_path),
                 "timeout", "--signal=TERM", "--kill-after=10s", "300s",
                 *map(str, argv)],
                cwd=cwd, stdout=stdout, stderr=stderr, check=False, env=env,
            )
            return completed.returncode
        except OSError as exc:
            stderr_path.write_text(f"could not start stage: {exc}\n")
            return 127
        finally:
            if stderr_path != stdout_path and hasattr(stderr, "close"):
                stderr.close()


def run_case(case_dir: Path, schema: Path, tool_home: Path, sysroot: str,
             repo_root: Path, mode: str, expect: str,
             certificate_mode: bool = True) -> dict:
    original = case_dir / "original/lib.rs"
    verified = case_dir / "verified/lib.rs"
    paths = (original, verified)
    base_env = os.environ.copy()
    base_env["PATH"] = str(tool_home / "bin") + os.pathsep + base_env.get("PATH", "")
    if certificate_mode:
        base_env["SORT4_MAYBEUNINIT_REPO_ROOT"] = str(repo_root)
    else:
        base_env.pop("SORT4_MAYBEUNINIT_REPO_ROOT", None)
    stage_integrity = {}

    def audited(stage: str, argv: list[str | Path], stdout: Path,
                resources: Path, stderr: Path | None = None) -> int:
        before = file_hashes(paths, case_dir)
        status = run_stage(argv, case_dir, resources, stdout, stderr, base_env)
        after = file_hashes(paths, case_dir)
        stage_integrity[stage] = {"before": before, "after": after, "unchanged": before == after}
        (case_dir / f"source-integrity-{stage}.json").write_text(
            json.dumps(stage_integrity[stage], indent=2, sort_keys=True) + "\n")
        (case_dir / f"{stage}-exit-code.txt").write_text(f"{status}\n")
        return status

    exporter = audited("exporter", [
        tool_home / "bin/vf-rust-mir-exporter", "verified/lib.rs",
        f"--sysroot={sysroot}", "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly",
    ], case_dir / "compiler-mir.bin", case_dir / "exporter-resources.txt",
       case_dir / "exporter.log")
    if exporter == 0:
        before = file_hashes(paths, case_dir)
        with (case_dir / "compiler-mir.bin").open("rb") as source, \
                (case_dir / "compiler-mir.txt").open("wb") as decoded, \
                (case_dir / "capnp-decode.log").open("wb") as errors:
            try:
                proc = subprocess.run([
                    "/usr/bin/time", "-v", "-o", str(case_dir / "decode-resources.txt"),
                    "timeout", "--signal=TERM", "--kill-after=10s", "300s",
                    "capnp", "decode", str(schema), "VfMir",
                ], stdin=source, stdout=decoded, stderr=errors, check=False,
                    cwd=case_dir, env=base_env)
                decode = proc.returncode
            except OSError as exc:
                errors.write(f"could not start decoder: {exc}\n".encode())
                decode = 127
        after = file_hashes(paths, case_dir)
        stage_integrity["decode"] = {"before": before, "after": after, "unchanged": before == after}
    else:
        decode = 125
        (case_dir / "compiler-mir.txt").write_bytes(b"")
        (case_dir / "capnp-decode.log").write_text("not run because MIR export failed\n")
        (case_dir / "decode-resources.txt").write_text("stage not run\n")
        stage_integrity["decode"] = {"unchanged": True, "status": "not_run_export_failed"}
    (case_dir / "decode-exit-code.txt").write_text(f"{decode}\n")

    if exporter == 0 and decode == 0:
        vf = audited("verifast", [
            tool_home / "bin/verifast", "-rustc_args", "--edition 2021",
            "-verbose", "1", "verified/lib.rs",
        ], case_dir / "verifast.log", case_dir / "verifast-resources.txt")
    else:
        vf = 125
        (case_dir / "verifast.log").write_text("not run because export/decode failed\n")
        (case_dir / "verifast-resources.txt").write_text("stage not run\n")
        stage_integrity["verifast"] = {"unchanged": True, "status": "not_run_export_or_decode_failed"}

    refinement = audited("refinement", [
        tool_home / "bin/refinement-checker", "--rustc-args", "--edition 2021",
        "original/lib.rs", "verified/lib.rs",
    ], case_dir / "refinement.log", case_dir / "refinement-resources.txt")
    log = (case_dir / "verifast.log").read_text(errors="replace")
    headers = re.findall(
        r"^\s*\d+(?:\.\d+)?s: verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): "
        r"Verifying function '([^']+)'$", log, re.M)
    errors = [line for line in log.splitlines() if ": error:" in line]
    diagnostic_seen = CERT_DIAGNOSTIC in log
    applicability_diagnostic_seen = bool(re.search(
        r"SORT4-MAYBEUNINIT: (?:certificate mismatch|unsupported certified union shape)", log))
    certified_body_seen = "certified local body" in log
    translated_body_seen = "checked local body translated (inner=1, aggregate=1" in log
    full_mir_graph_seen = "SORT4-MAYBEUNINIT: full typed constructor MIR graph accepted" in log
    sources_unchanged = all(x.get("unchanged", False) for x in stage_integrity.values())
    base_ok = exporter == 0 and decode == 0 and refinement == 0 and sources_unchanged
    helper_headers = sum(name.endswith(CERT_FUNCTION) for _, name in headers)
    probe_headers = sum(name.endswith("sort4_checked_maybeuninit_frame_probe") for _, name in headers)
    fixture = json.loads((case_dir / "fixture.json").read_text())
    variant = fixture.get("variant")
    expected_probe = {
        "stock_false_control": "stock_false_control",
        "wrong_inner_post": "sort4_checked_maybeuninit_wrong_value_probe",
        "false_postcondition": "sort4_checked_maybeuninit_false_post_probe",
    }.get(variant, "sort4_checked_maybeuninit_frame_probe")
    expected_probe_headers = sum(name.endswith(expected_probe) for _, name in headers)
    error_offset = log.find(errors[0]) if errors else -1
    functions_before_error = re.findall(r"Verifying function '([^']+)'", log[:error_offset]) \
        if error_offset >= 0 else []
    failure_in_expected_probe = bool(functions_before_error) and \
        functions_before_error[-1].endswith(expected_probe)
    helper_header_marker = f"Verifying function '{CERT_FUNCTION_PATH}'"
    helper_body_start = log.find(helper_header_marker)
    next_function = log.find("Verifying function '", helper_body_start + len(helper_header_marker)) \
        if helper_body_start >= 0 else -1
    helper_body_log = log[helper_body_start:next_function if next_function >= 0 else None] \
        if helper_body_start >= 0 else ""
    helper_prototype_checked = (
        f"Function '{CERT_FUNCTION_PATH}': Function prototype implementation check" in log
    )
    helper_return_checked = "Executing return statement" in helper_body_log
    helper_leak_checked = "Leak check." in helper_body_log
    ownership_lemma_marker = "Verifying function 'std::mem::close_MaybeUninit_pointer_own'"
    own_start = log.find(ownership_lemma_marker)
    own_end = log.find("Verifying function '", own_start + len(ownership_lemma_marker)) if own_start >= 0 else -1
    ownership_lemma_log = log[own_start:own_end if own_end >= 0 else None] if own_start >= 0 else ""
    ownership_lemma_checked = own_start >= 0 and "Executing return statement" in ownership_lemma_log and "Leak check." in ownership_lemma_log

    identity_name = "sort4_nonpointer_identity"
    identity_headers = sum(name.endswith(identity_name) for _, name in headers)
    identity_header_marker = f"Verifying function '{identity_name}'"
    identity_start = log.find(identity_header_marker)
    identity_next = log.find("Verifying function '", identity_start + len(identity_header_marker)) \
        if identity_start >= 0 else -1
    identity_body_log = log[identity_start:identity_next if identity_next >= 0 else None] \
        if identity_start >= 0 else ""
    identity_return_checked = "Executing return statement" in identity_body_log
    identity_leak_checked = "Leak check." in identity_body_log
    verified_source = verified.read_bytes()
    safe_constructor_contract = (
        b"pub fn " + CERT_FUNCTION.encode() + b"<Element>" in verified_source and
        b"pub unsafe fn " + CERT_FUNCTION.encode() not in verified_source and
        b"req thread_token(?t) &*& t == currentThread;" in verified_source and
        b"std::mem::MaybeUninit::inner(result) == some(val) &*& " in verified_source and
        b"on_unwind_ens false;" in verified_source
    )
    pointer_option_paths_exercised = (
        b"open std::mem::MaybeUninit_pointer_own::<Element>()(t, wrapped);" in verified_source
        and b"new_maybe_uninit(none));" in verified_source
        and b"*val |->" not in verified_source
    )
    decoded_mir = (case_dir / "compiler-mir.txt").read_text(errors="replace")
    external_call_count_mir = decoded_mir.count(f'name = "{MIR_EXTERNAL_NEW.decode()}"')
    redirect_count = log.count("redirected checked external pointer call")
    error_lines = []
    for entry in errors:
        match = re.search(r"verified/lib\.rs\((\d+),", entry)
        if match:
            error_lines.append(int(match.group(1)))
    target_assertion_line = fixture.get("target_assertion_line")
    execution_lines = [int(match.group(1)) for entry in log.splitlines()
                       if (match := re.search(
                           r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): "
                           r"(?:note: )?(?:Executing statement|Executing return statement|Verifying call)$", entry))]
    targeted_error = (
        isinstance(target_assertion_line, int) and len(errors) == 1 and
        error_lines == [target_assertion_line + 1] and
        target_assertion_line + 1 in execution_lines
    )
    false_variant = variant in {"false_assert", "stock_false_control"}
    resource_variant = variant == "resource_duplication"
    false_post_variant = variant == "false_postcondition"
    intended_false_message = (
        expect != "proof_negative" or not errors or
        ("Cannot prove false" in errors[0] if false_variant else
         "No matching heap" in errors[0] if resource_variant else
         "Cannot prove" in errors[0] if false_post_variant else
         "Assertion might not hold" in errors[0])
    )
    constructor_probe = variant not in {
        "stock_false_control", "stock_pointer_frame"
    }
    expected_constructor_calls = 1 if constructor_probe else 0
    target_obligation = targeted_error
    if false_post_variant:
        target_postcondition = fixture.get("target_postcondition_line")
        target_return = fixture.get("target_return_line")
        target_obligation = (
            isinstance(target_postcondition, int) and len(errors) == 1 and
            error_lines == [target_postcondition + 1] and
            isinstance(target_return, int) and target_return + 1 in execution_lines
        )
    proof_negative_evidence = {
        "proof_expected": expect == "proof_negative",
        "integrity_and_frontend_ok": base_ok,
        "verifier_failed": vf == 1,
        "target_obligation": target_obligation,
        "intended_message": intended_false_message,
        "no_applicability_rejection": not applicability_diagnostic_seen,
        "named_probe_entered": expected_probe_headers == 1,
        "error_in_named_probe": failure_in_expected_probe,
        "constructor_body_checked": not constructor_probe or (
            helper_headers == 1 and helper_prototype_checked and
            helper_return_checked and helper_leak_checked and full_mir_graph_seen and ownership_lemma_checked),
        "external_call_count_exact": external_call_count_mir == expected_constructor_calls,
        "redirect_count_exact": redirect_count == expected_constructor_calls,
    }
    expected_proof_failure = strict_proof_negative(proof_negative_evidence)
    mutation_record = None
    if expect == "mir_applicability_reject":
        record_path = case_dir / "mutation-record.json"
        if record_path.exists():
            mutation_record = json.loads(record_path.read_text())
    mutation_name = fixture.get("mir_mutation")
    mutation_profile_path = case_dir / "mutation-profile.json"
    mutation_profile = json.loads(mutation_profile_path.read_text()) \
        if mutation_profile_path.exists() else None
    mutation_text_exact = False
    if mutation_name in MIR_MUTATIONS and (case_dir / "canonical-mir.txt").exists() \
            and (case_dir / "mutated-mir.txt").exists():
        try:
            mutation_text_exact = mutate_constructor_mir(
                (case_dir / "canonical-mir.txt").read_text(), mutation_name
            ) == (case_dir / "mutated-mir.txt").read_text()
        except ValueError:
            pass
    mutation_ready = (
        isinstance(mutation_record, dict) and mutation_record.get("matched") is True
        and mutation_record.get("mutation") == mutation_name
        and mutation_record.get("exporter_exit") == 0
        and mutation_record.get("decode_exit") == 0
        and mutation_record.get("encode_exit") == 0
        and mutation_record.get("canonical_sha256") != mutation_record.get("mutated_sha256")
        and isinstance(mutation_profile, dict)
        and mutation_profile.get("base_console_sha256") == mutation_profile.get("shadow_console_sha256")
        and mutation_record.get("real_exporter_sha256") == mutation_profile.get("real_exporter_sha256")
        and mutation_record.get("selected_source_sha256") == sha(verified_source)
        and (case_dir / "canonical-mir.bin").exists()
        and (case_dir / "mutated-mir.bin").exists()
        and mutation_record.get("canonical_sha256") == sha((case_dir / "canonical-mir.bin").read_bytes())
        and mutation_record.get("mutated_sha256") == sha((case_dir / "mutated-mir.bin").read_bytes())
        and mutation_text_exact
    )
    applicability_reason = (
        MIR_APPLICABILITY_REASONS.get(mutation_name)
        if expect == "mir_applicability_reject" else
        SOURCE_APPLICABILITY_REASONS.get(variant)
    )
    expected_applicability_reason_seen = (
        applicability_reason is not None and
        f"SORT4-MAYBEUNINIT: certificate mismatch: {applicability_reason[0]}" in log
    )
    if expect in {"positive", "specialization_positive"}:
        outcome = "PASS" if (
            base_ok and vf == 0 and helper_headers == 1 and probe_headers == 1
            and certified_body_seen and translated_body_seen and full_mir_graph_seen
            and safe_constructor_contract and helper_prototype_checked and ownership_lemma_checked
            and helper_return_checked and helper_leak_checked
            and pointer_option_paths_exercised
            and external_call_count_mir == 1 and redirect_count == 1
            and (expect != "specialization_positive" or
                 (identity_headers == 1 and identity_return_checked and identity_leak_checked))
        ) else "INCONCLUSIVE"
    elif expect == "control_positive":
        control_headers = sum(name.endswith("stock_pointer_frame") for _, name in headers)
        outcome = "PASS" if base_ok and vf == 0 and control_headers == 1 else "INCONCLUSIVE"
    elif expect == "proof_negative":
        outcome = "EXPECTED_PROOF_FAILURE" if expected_proof_failure else "INCONCLUSIVE"
    elif expect == "applicability_reject":
        outcome = "EXPECTED_APPLICABILITY_REJECT" if (
            exporter == 0 and decode == 0 and refinement == 0 and vf == 1
            and sources_unchanged and applicability_diagnostic_seen
            and expected_applicability_reason_seen
            and helper_headers == 0 and expected_probe_headers == 0
        ) else "INCONCLUSIVE"
    elif expect == "mir_applicability_reject":
        outcome = "EXPECTED_MIR_APPLICABILITY_REJECT" if (
            base_ok and vf == 1 and mutation_ready and applicability_diagnostic_seen
            and expected_applicability_reason_seen
            and helper_headers == 0 and expected_probe_headers == 0
        ) else "INCONCLUSIVE"
    elif expect == "actual_callee":
        actual_headers = sum(name == "select_unpredictable" for _, name in headers)
        log_bundle = "\n".join(
            (case_dir / name).read_text(errors="replace")
            for name in ("exporter.log", "verifast.log") if (case_dir / name).exists())
        redirect_count = log_bundle.count("redirected checked external pointer call")
        redirect_evidence = redirect_count == 2 and \
            "checked local body translated (inner=1, aggregate=1, redirected=2" in log_bundle
        outcome = "CALLEE_PASS" if (
            base_ok and vf == 0 and actual_headers == 1 and redirect_evidence
            and helper_headers == 1 and certified_body_seen and translated_body_seen
            and external_call_count_mir == 2
        ) else "CALLEE_INCONCLUSIVE"
    else:
        outcome = "INCONCLUSIVE"
    result = {
        "case": case_dir.name,
        "mode": mode,
        "expected_class": expect,
        "outcome": outcome,
        "exporter_exit": exporter,
        "decode_exit": decode,
        "verifast_exit": vf,
        "refinement_exit": refinement,
        "verified_function_headers": headers,
        "certifier_diagnostic_seen": diagnostic_seen,
        "certifier_applicability_rejection_seen": applicability_diagnostic_seen,
        "certified_local_body_evidence": certified_body_seen,
        "checked_local_body_translation_evidence": translated_body_seen,
        "full_typed_constructor_mir_graph_seen": full_mir_graph_seen,
        "expected_applicability_reason": applicability_reason,
        "expected_applicability_reason_seen": expected_applicability_reason_seen,
        "safe_constructor_contract": safe_constructor_contract,
        "checked_constructor_prototype_implementation": helper_prototype_checked,
        "checked_constructor_return": helper_return_checked,
        "defined_ownership_introduction_body_checked": ownership_lemma_checked,
        "checked_constructor_leak_check": helper_leak_checked,
        "pointer_option_paths_exercised": pointer_option_paths_exercised,
        "nonpointer_identity_header_count": identity_headers,
        "nonpointer_identity_return": identity_return_checked,
        "nonpointer_identity_leak_check": identity_leak_checked,
        "failure_in_expected_probe": failure_in_expected_probe,
        "proof_negative_evidence": proof_negative_evidence,
        "targeted_negative_error": targeted_error,
        "first_verifast_error": errors[0] if errors else None,
        "checked_constructor_header_count": helper_headers,
        "frame_probe_header_count": probe_headers,
        "external_maybeuninit_new_defpath_count_in_mir": external_call_count_mir,
        "checked_external_pointer_redirect_count": redirect_count,
        "source_unchanged_at_every_stage": sources_unchanged,
        "stage_integrity": stage_integrity,
        "mir_mutation_record": mutation_record,
        "mir_mutation_ready": mutation_ready,
        "mir_mutation_text_exact": mutation_text_exact,
    }
    (case_dir / "classification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


CONSTRUCTOR_CASES = [
    ("constructor_positive", "positive", "positive"),
    ("nonpointer_identity", "nonpointer_identity", "specialization_positive"),
    ("wrong_inner_post", "wrong_inner_post", "proof_negative"),
    ("false_uninit", "false_uninit", "proof_negative"),
    ("false_assert", "false_assert", "proof_negative"),
    ("false_postcondition", "false_postcondition", "proof_negative"),
    ("resource_duplication", "resource_duplication", "proof_negative"),
    ("wrong_active_field", "wrong_active_field", "applicability_reject"),
    ("wrong_operand", "wrong_operand", "applicability_reject"),
    ("wrong_return", "wrong_return", "applicability_reject"),
    ("extra_operation", "extra_operation", "applicability_reject"),
    ("renamed_function", "renamed_function", "applicability_reject"),
    ("wrong_binding", "wrong_binding", "applicability_reject"),
    ("nonpointer_input", "nonpointer_input", "applicability_reject"),
    ("extra_union_field", "extra_union_field", "applicability_reject"),
]


def prepare_constructor_case(evidence: Path, cert: dict,
                             name: str, variant: str) -> Path:
    original_prefix, verified_prefix, metadata = constructor_source(cert, variant)
    case_dir = evidence / name
    case_dir.mkdir(parents=True, exist_ok=False)
    write_case(case_dir, original_prefix, verified_prefix, metadata)
    return case_dir


def prepare_mir_mutation_case(evidence: Path, cert: dict,
                              mutation: str) -> Path:
    name = f"mir_{mutation}"
    case_dir = prepare_constructor_case(evidence, cert, name, "positive")
    fixture = json.loads((case_dir / "fixture.json").read_text())
    fixture["variant"] = name
    fixture["mir_mutation"] = mutation
    (case_dir / "fixture.json").write_text(json.dumps(
        fixture, indent=2, sort_keys=True) + "\n")
    return case_dir


def prepare_stock_false_control(evidence: Path) -> Path:
    case_dir = evidence / "stock_false_control"
    verified = (
        b"pub fn stock_false_control()\n" +
        ghost_block(b"req true;\nens true;\non_unwind_ens false;") +
        b"{\n    // TARGET_ASSERTION\n    //@ assert false;\n}\n"
    )
    original = strip_ghost_annotations(verified)
    metadata = {
        "variant": "stock_false_control",
        "target_assertion_line": next(
            i for i, line in enumerate(verified.splitlines(), 1)
            if b"TARGET_ASSERTION" in line),
        "local_function_path_suffix": "stock_false_control",
        "expected_external_call_count": 0,
    }
    case_dir.mkdir(parents=True, exist_ok=False)
    write_case(case_dir, original, verified, metadata)
    return case_dir


def prepare_stock_pointer_frame(evidence: Path) -> Path:
    case_dir = evidence / "stock_pointer_frame"
    verified = (
        b"pub unsafe fn stock_pointer_frame(p: *const u8, other: *mut u8) -> u8\n" +
        ghost_block(
            b"req thread_token(?t) &*& t == currentThread &*& "
            b"[?f](*p |-> ?pv) &*& *other |-> ?ov;\n"
            b"ens thread_token(t) &*& [f](*p |-> pv) &*& *other |-> ov &*& result == pv;\n"
            b"on_unwind_ens false;"
        ) +
        b"{\n    unsafe { *p }\n}\n"
    )
    original = strip_ghost_annotations(verified)
    metadata = {"variant": "stock_pointer_frame", "expected_external_call_count": 0}
    case_dir.mkdir(parents=True, exist_ok=False)
    write_case(case_dir, original, verified, metadata)
    return case_dir


def run_native_controls(evidence: Path, repo_root: Path,
                        stock_home: Path, tool_home: Path) -> dict:
    fixtures = (
        ("c_nonempty", repo_root / "research/challenge-8/rust-fieldless-layout-controls/positive_c_nonempty.c"),
        ("cpp_empty", repo_root / "research/challenge-8/rust-fieldless-layout-controls/positive_cpp_empty.cpp"),
        ("existing_rust_generic_struct", tool_home / "tests/rust/purely_unsafe/generic_structs.rs"),
        ("existing_c_struct", tool_home / "tests/chars__of_struct.c"),
        ("existing_cpp_constructor", tool_home / "tests/cxx/constructors.cpp"),
    )
    results = {}
    for profile, home in (("stock", stock_home), ("patched", tool_home)):
        for name, fixture in fixtures:
            case_dir = evidence / "native-controls" / profile / name
            case_dir.mkdir(parents=True, exist_ok=False)
            before = sha(fixture.read_bytes())
            flags = ["-rustc_args", "--edition 2021"] if fixture.suffix == ".rs" else ["-c"]
            status = run_stage(
                [home / "bin/verifast", *flags, "-verbose", "1", fixture],
                repo_root, case_dir / "resources.txt", case_dir / "verifast.log",
            )
            after = sha(fixture.read_bytes())
            outcome = "PASS" if status == 0 and before == after else "INCONCLUSIVE"
            result = {"outcome": outcome, "verifast_exit": status,
                      "source_sha256_before": before, "source_sha256_after": after,
                      "source_unchanged": before == after, "tool_home": str(home.resolve())}
            (case_dir / "classification.json").write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n")
            results[f"{profile}_{name}"] = result
    return results


def make_actual_callee_case(evidence: Path, repo_root: Path,
                            cert: dict) -> Path:
    select = load_select_module(repo_root)
    target = evidence / "actual_select_after_constructor"
    target.mkdir(parents=True, exist_ok=False)
    prepared = target / "prepared"
    prepared.mkdir()
    select_case = prepared / "actual_select_pointer"
    select.prepare(repo_root / "library/core/src/hint.rs", select_case,
                   prepared / "extraction-integrity.json")
    original_prefix, verified_prefix, metadata = constructor_source(cert, "positive")
    frame_probe_marker = b"pub unsafe fn sort4_checked_maybeuninit_frame_probe"
    original_module = original_prefix.split(frame_probe_marker, 1)[0]
    verified_module = verified_prefix.split(frame_probe_marker, 1)[0]
    crate_feature = b"#![feature(transparent_unions)]\n"
    require(original_module.startswith(crate_feature) and verified_module.startswith(crate_feature),
            "constructor fixture lost its transparent_unions crate feature")
    original_module = original_module[len(crate_feature):]
    verified_module = verified_module[len(crate_feature):]
    # Keep the actual select body and its two standard constructor calls byte-identical.
    for variant_name, module_prefix in (("original", original_module),
                                        ("verified", verified_module)):
        path = select_case / variant_name / "lib.rs"
        data = enable_crate_feature(path.read_bytes(), b"transparent_unions")
        path.write_bytes(data + b"\n" + module_prefix)
    original = select_case / "original/lib.rs"
    verified = select_case / "verified/lib.rs"
    require(verified.read_bytes().count(RUST_SOURCE_NEW_CALL) == 2,
            "actual select adapter must retain both external constructor calls")
    select_meta = json.loads((select_case / "extraction.json").read_text())
    metadata.update({
        "actual_select_original_sha256_before_helper": select_meta["original_sha256"],
        "actual_select_verified_sha256_before_helper": select_meta["verified_sha256"],
        "external_constructor_call_count": verified.read_bytes().count(RUST_SOURCE_NEW_CALL),
        "actual_select_body_sha256": select_meta["body_sha256"],
        "helper_source_sha256": sha(verified_module),
        "transparent_unions_feature_enabled": True,
        "verified_ghost_strip_exact": strip_ghost_annotations(verified.read_bytes())
            == original.read_bytes(),
    })
    (target / "fixture.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    # run_case expects the original and verified at the case root.
    final = evidence / "actual_select_after_constructor_run"
    final.mkdir()
    (final / "original").mkdir()
    (final / "verified").mkdir()
    (final / "original/lib.rs").write_bytes(original.read_bytes())
    (final / "verified/lib.rs").write_bytes(verified.read_bytes())
    (final / "fixture.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return final


def quarantine_false_assert_success(evidence: Path, case_name: str,
                                    result: dict) -> None:
    if case_name not in {"stock_false_control", "patched_false_control", "false_assert"}:
        return
    if result.get("verifast_exit") != 0:
        return
    record = {
        "status": "PROFILE_QUARANTINED",
        "reason": "a deliberately false assertion unexpectedly verified",
        "case": case_name,
        "verifast_exit": result.get("verifast_exit"),
        "classification": result,
        "profile_must_not_be_used": True,
        "remaining_constructor_cases": "NOT_RUN",
        "actual_callee": "NOT_RUN",
    }
    (evidence / "FALSE-ASSERT-PROFILE-QUARANTINED.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    raise SystemExit(
        f"profile quarantined: false assertion unexpectedly verified in {case_name}")


def main() -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true" or \
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \
            os.environ.get("RUNNER_OS") != "Linux":
        raise SystemExit("MaybeUninit constructor checks require GitHub-hosted Linux Actions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-home", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument(
        "--feasibility-only", action="store_true",
        help="run the constructor positive as a partial diagnostic; never accept the profile",
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    source_cert = certify_repository_sources(repo_root)
    (evidence / "source-certificate.json").write_text(
        json.dumps(source_cert, indent=2, sort_keys=True) + "\n")

    stock_control = prepare_stock_false_control(evidence)
    stock_false_result = run_case(stock_control, args.schema, args.stock_home,
                                  args.compiler_sysroot, repo_root,
                                  "stock_false_control", "proof_negative",
                                  certificate_mode=False)
    quarantine_false_assert_success(evidence, "stock_false_control", stock_false_result)
    patched_false_dir = evidence / "patched_false_control"
    patched_false_dir.mkdir(parents=True, exist_ok=False)
    verified_false = (stock_control / "verified/lib.rs").read_bytes()
    original_false = (stock_control / "original/lib.rs").read_bytes()
    write_case(patched_false_dir, original_false, verified_false,
               json.loads((stock_control / "fixture.json").read_text()))
    patched_false_result = run_case(patched_false_dir, args.schema, args.tool_home,
                                    args.compiler_sysroot, repo_root,
                                    "patched_false_control", "proof_negative",
                                    certificate_mode=False)
    quarantine_false_assert_success(evidence, "patched_false_control", patched_false_result)

    stock_frame_dir = prepare_stock_pointer_frame(evidence)
    stock_frame_result = run_case(stock_frame_dir, args.schema, args.stock_home,
                                  args.compiler_sysroot, repo_root,
                                  "stock_pointer_frame", "control_positive",
                                  certificate_mode=False)
    patched_frame_dir = evidence / "patched_pointer_frame"
    patched_frame_dir.mkdir(parents=True, exist_ok=False)
    write_case(patched_frame_dir,
               (stock_frame_dir / "original/lib.rs").read_bytes(),
               (stock_frame_dir / "verified/lib.rs").read_bytes(),
               json.loads((stock_frame_dir / "fixture.json").read_text()))
    patched_frame_result = run_case(patched_frame_dir, args.schema, args.tool_home,
                                    args.compiler_sysroot, repo_root,
                                    "patched_pointer_frame", "control_positive",
                                    certificate_mode=False)
    native_results = run_native_controls(evidence, repo_root, args.stock_home, args.tool_home)
    baseline_results = {
        "stock_false_control": stock_false_result,
        "patched_false_control": patched_false_result,
        "stock_pointer_frame": stock_frame_result,
        "patched_pointer_frame": patched_frame_result,
        "native_controls": native_results,
    }
    baselines_ok = (
        stock_false_result["outcome"] == "EXPECTED_PROOF_FAILURE" and
        patched_false_result["outcome"] == "EXPECTED_PROOF_FAILURE" and
        stock_frame_result["outcome"] == "PASS" and
        patched_frame_result["outcome"] == "PASS" and
        all(item["outcome"] == "PASS" for item in native_results.values())
    )
    if not baselines_ok:
        (evidence / "summary.json").write_text(json.dumps({
            "constructor_acceptance": False,
            "constructor_cases": [],
            "constructor_cases_not_run": len(CONSTRUCTOR_CASES),
            "baselines": baseline_results,
            "actual_callee_status": "NOT_RUN",
        }, indent=2, sort_keys=True) + "\n")
        raise SystemExit("stock/patched pointer, false-assertion, or C/C++ baseline did not pass")

    results = []
    first_name, first_variant, first_expectation = CONSTRUCTOR_CASES[0]
    positive_dir = prepare_constructor_case(evidence, source_cert, first_name, first_variant)
    results.append(run_case(positive_dir, args.schema, args.tool_home,
                            args.compiler_sysroot, repo_root,
                            "constructor", first_expectation))
    if args.feasibility_only:
        feasibility_pass = results[0]["outcome"] == "PASS"
        (evidence / "constructor-negatives-not-run.json").write_text(json.dumps({
            "status": "NOT_RUN",
            "reason": "C4 feasibility-only mode; no acceptance matrix or full MIR gate",
            "remaining_cases": [name for name, _, _ in CONSTRUCTOR_CASES[1:]],
        }, indent=2, sort_keys=True) + "\n")
        (evidence / "actual-callee-not-run.json").write_text(json.dumps({
            "status": "NOT_RUN",
            "reason": "C4 feasibility-only mode does not authorize callee acceptance",
        }, indent=2, sort_keys=True) + "\n")
        summary = {
            "profile_status": "UNACCEPTED",
            "feasibility_only": True,
            "feasibility_result": "PASS" if feasibility_pass else "INCONCLUSIVE",
            "constructor_acceptance": False,
            "baselines": baseline_results,
            "constructor_cases": results,
            "constructor_cases_not_run": len(CONSTRUCTOR_CASES) - len(results),
            "remaining_constructor_cases": [name for name, _, _ in CONSTRUCTOR_CASES[1:]],
            "actual_callee_status": "NOT_RUN",
            "source_certificate": source_cert,
            "tool_home": str(args.tool_home.resolve()),
            "stock_home": str(args.stock_home.resolve()),
            "compiler_sysroot": args.compiler_sysroot,
            "schema": str(args.schema.resolve()),
        }
        (evidence / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print(json.dumps({
            "profile_status": "UNACCEPTED",
            "feasibility_result": summary["feasibility_result"],
            "actual_callee_status": "NOT_RUN",
        }, sort_keys=True))
        if not feasibility_pass:
            raise SystemExit(1)
        return
    if results[0]["outcome"] == "PASS":
        for case_name, variant, expectation in CONSTRUCTOR_CASES[1:]:
            case_dir = prepare_constructor_case(evidence, source_cert, case_name, variant)
            case_result = run_case(case_dir, args.schema, args.tool_home,
                                   args.compiler_sysroot, repo_root,
                                   "constructor", expectation)
            results.append(case_result)
            quarantine_false_assert_success(evidence, case_name, case_result)
    else:
        (evidence / "constructor-negatives-not-run.json").write_text(json.dumps({
            "status": "NOT_RUN",
            "reason": "constructor positive did not pass; proof and applicability controls are gated",
            "remaining_cases": [name for name, _, _ in CONSTRUCTOR_CASES[1:]],
        }, indent=2, sort_keys=True) + "\n")

    expected_outcome = {
        "positive": "PASS",
        "specialization_positive": "PASS",
        "proof_negative": "EXPECTED_PROOF_FAILURE",
        "applicability_reject": "EXPECTED_APPLICABILITY_REJECT",
    }
    source_matrix_pass = (
        len(results) == len(CONSTRUCTOR_CASES) and
        all(result["outcome"] == expected_outcome[expectation]
            for result, (_, _, expectation) in zip(results, CONSTRUCTOR_CASES))
    )
    mir_results = []
    if source_matrix_pass:
        for mutation in MIR_MUTATIONS:
            case_dir = prepare_mir_mutation_case(evidence, source_cert, mutation)
            shadow_home = make_mir_mutation_tool_home(
                args.tool_home, args.schema, repo_root, case_dir, mutation)
            mir_results.append(run_case(
                case_dir, args.schema, shadow_home, args.compiler_sysroot,
                repo_root, "mir_mutation", "mir_applicability_reject"))
    else:
        (evidence / "mir-mutants-not-run.json").write_text(json.dumps({
            "status": "NOT_RUN",
            "reason": "source/proof matrix did not pass",
            "remaining_cases": list(MIR_MUTATIONS),
        }, indent=2, sort_keys=True) + "\n")
    constructor_acceptance = (
        source_matrix_pass and len(mir_results) == len(MIR_MUTATIONS) and
        all(item["outcome"] == "EXPECTED_MIR_APPLICABILITY_REJECT"
            for item in mir_results)
    )
    final_callee = None
    if constructor_acceptance:
        callee_case = make_actual_callee_case(evidence, repo_root, source_cert)
        final_callee = run_case(callee_case, args.schema, args.tool_home,
                                args.compiler_sysroot, repo_root,
                                "actual_callee", "actual_callee")
    else:
        (evidence / "actual-callee-not-run.json").write_text(json.dumps({
            "status": "NOT_RUN",
            "reason": "full constructor acceptance matrix did not pass",
        }, indent=2, sort_keys=True) + "\n")

    summary = {
        "constructor_acceptance": constructor_acceptance,
        "baselines": baseline_results,
        "constructor_cases": results,
        "constructor_cases_not_run": len(CONSTRUCTOR_CASES) - len(results),
        "mir_mutation_cases": mir_results,
        "mir_mutation_cases_not_run": len(MIR_MUTATIONS) - len(mir_results),
        "actual_callee": final_callee,
        "actual_callee_status": (
            final_callee["outcome"] if final_callee else "NOT_RUN"
        ),
        "tool_home": str(args.tool_home.resolve()),
        "stock_home": str(args.stock_home.resolve()),
        "compiler_sysroot": args.compiler_sysroot,
        "schema": str(args.schema.resolve()),
        "source_certificate": source_cert,
    }
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "constructor_acceptance": constructor_acceptance,
        "actual_callee_status": summary["actual_callee_status"],
        "cases": {item["case"]: item["outcome"] for item in results},
    }, sort_keys=True))
    if not constructor_acceptance:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
