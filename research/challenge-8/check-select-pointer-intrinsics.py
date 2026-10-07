#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted source-linked S5 checks for two exact intrinsic select types.

This accepts only the two checked local adapters, never the complete hint
select_unpredictable body or a general intrinsic T. All executable stages are
guarded for GitHub-hosted Linux Actions.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
from pathlib import Path


PROFILE = os.environ.get("SORT4_SELECT_PROFILE", "experimental-source-linked-select-pointer-intrinsics-v1")
AUTHORIZED_PROFILES = {
    "experimental-source-linked-select-pointer-intrinsics-v1",
    "experimental-source-linked-select-pointer-intrinsics-v2",
    "experimental-source-linked-select-pointer-drop-v1",
    "experimental-source-linked-select-pointer-drop-v2",
    "experimental-source-linked-select-pointer-drop-v3",
    "experimental-source-linked-select-pointer-drop-v4",
}
SOURCE_SHA256 = "ab781181f967398d514d9fd2b5f3b6aebd16c2c403f3d1a2628e0c7f1fac6ebf"
INTRINSIC_SOURCE_SIGNATURE = (
    b"pub const fn select_unpredictable<T>(b: bool, true_val: T, false_val: T) -> T"
)
INTRINSIC_SOURCE_BODY = (
    b"{\n    if b {\n        forget(false_val);\n        true_val\n"
    b"    } else {\n        forget(true_val);\n        false_val\n    }\n}"
)
BODY = b"{\n    std::intrinsics::select_unpredictable(condition, a, b)\n}"
CALL = b"std::intrinsics::select_unpredictable(condition, a, b)"
MIR_CALL = 'name = "std::intrinsics::select_unpredictable"'
PREFIX = b"#![feature(core_intrinsics)]\n#![allow(internal_features)]\n\n"
OWN_A = b"std::mem::MaybeUninit_pointer_own::<Element>()(t, a)"
OWN_B = b"std::mem::MaybeUninit_pointer_own::<Element>()(t, b)"
OWN_RESULT = b"std::mem::MaybeUninit_pointer_own::<Element>()(t, result)"
INNER = b"std::mem::MaybeUninit::inner"
KINDS = ("ptr", "mu")
POSITIVES = {
    "ptr": ("symbolic", "true", "false"),
    "mu": ("unknown", "none", "some"),
}
NEGATIVES = {
    "ptr": ("wrong_result", "false_post", "assert_false", "lost_cell", "duplicate_frame"),
    "mu": ("wrong_inner", "false_post", "assert_false", "lost_cell", "duplicate_frame"),
}
SOURCE_MUTATIONS = (
    "identity", "inputtype", "operand_order", "resulttype",
    "binding", "contract", "additional_operation",
)
MIR_MUTATIONS = (
    "fndef", "type_argument", "input_type", "operand_order", "operand_source",
    "predecessor_source", "result_local", "result_type", "extra_operation",
    "cfg_successor", "cfg_unwind",
    "hir_binding", "contract",
)
CERT_PREFIX = "SORT4-SELECT-INTRINSIC:"
CERT_MARKER = CERT_PREFIX + " full typed standalone MIR graph accepted"
REJECT_PREFIX = CERT_PREFIX + " certificate mismatch: "
WRONG_POINTER_RESULT_ERROR = re.compile(
    r"verified/lib\.rs\(\d+,\d+-\d+\): error: Cannot prove condition\. "
    r"\(Cannot prove !\(result0 = \(condition \? a : b\)\)\.\)$"
)
WRONG_WRAPPER_INNER_ERROR = re.compile(
    r"verified/lib\.rs\(\d+,\d+-\d+\): error: Cannot prove that "
    r"'std::mem::MaybeUninit::inner\(pointer_typeid\(Element_typeid\), result0\)' "
    r"is not an instance of constructor 'none'$"
)
SOURCE_REASONS = {
    "operand_order": ("helper source body changed",),
    "contract": ("helper SAFE contract/source signature",),
    "additional_operation": ("helper source body changed",),
}
MIR_REASONS = {
    "fndef": ("standalone callee identity/type",),
    "type_argument": ("standalone callee identity/type",),
    "input_type": ("standalone input types/order",),
    "operand_order": ("standalone argument operand: _4/_5/_6",
                      "standalone place: _5/_6"),
    "operand_source": ("standalone argument operand: _4/_5/_6",
                       "standalone place: _5/_6"),
    "predecessor_source": ("standalone source operand: _2/_3",
                           "standalone place: _2/_3"),
    "result_local": ("standalone place: _0",),
    "result_type": ("standalone output type",
                    "standalone local identity/type: _0"),
    "extra_operation": ("standalone first block statements",),
    "cfg_successor": ("standalone normal successor",),
    "cfg_unwind": ("standalone unwind action",),
    "hir_binding": ("debug name: a",),
    "contract": ("helper exported SAFE contract",),
}
PTR_SIGNATURE = (
    b"pub fn sort4_checked_select_ptr<Element>(condition: bool, "
    b"a: *mut *const Element, b: *mut *const Element) -> *mut *const Element"
)
MU_SIGNATURE = (
    b"pub fn sort4_checked_select_mu<Element>(condition: bool, "
    b"a: std::mem::MaybeUninit<*const Element>, "
    b"b: std::mem::MaybeUninit<*const Element>) "
    b"-> std::mem::MaybeUninit<*const Element>"
)
PTR_CONTRACT = (
    b"req thread_token(?t) &*& t == currentThread;\n"
    b"ens thread_token(t) &*& (result as pointer) == "
    b"(if condition { a as pointer } else { b as pointer });\n"
    b"on_unwind_ens false;"
)
MU_CONTRACT = (
    b"req thread_token(?t) &*& t == currentThread &*& " + OWN_A + b" &*& " + OWN_B + b";\n"
    b"ens thread_token(t) &*& " + OWN_RESULT + b" &*& "
    b"result == (if condition { a } else { b }) &*& "
    + INNER + b"(result) == (if condition { " + INNER + b"(a) } else { "
    + INNER + b"(b) });\n"
    b"on_unwind_ens false;"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_certificate(repo_root: Path, constructor) -> dict:
    path = repo_root / "library/core/src/intrinsics/mod.rs"
    source = path.read_bytes()
    require(sha(source) == SOURCE_SHA256, "intrinsic source pin changed")
    body = constructor.extract_braced_item(source, INTRINSIC_SOURCE_SIGNATURE)
    require(body == INTRINSIC_SOURCE_BODY, "intrinsic fallback body changed")
    declaration = source[source.index(INTRINSIC_SOURCE_SIGNATURE) - 145:
                         source.index(INTRINSIC_SOURCE_SIGNATURE)]
    require(b"#[rustc_intrinsic]" in declaration and
            b"#[rustc_nounwind]" in declaration and
            b"#[miri::intrinsic_fallback_is_spec]" in declaration,
            "intrinsic identity/nounwind/fallback declaration changed")
    return {
        "source_path": str(path),
        "source_sha256": sha(source),
        "source_body_sha256": sha(body),
        "source_body_exact": True,
        "two_only_exact_types": ["*mut *const Element", "MaybeUninit<*const Element>"],
        "trust_scope": "typed compiler intrinsic value rule; no Rust body proof or general T",
        "normal_value": "complete result equals condition-selected input",
        "unwind": "rustc_nounwind; checked local adapters require on_unwind_ens false",
    }


def helper_name(kind: str) -> str:
    return "sort4_checked_select_" + kind


def probe_name(kind: str, variant: str) -> str:
    return "sort4_select_" + kind + "_" + variant + "_probe"


def helper_source(kind: str, constructor) -> bytes:
    require(kind in KINDS, f"unknown specialization {kind}")
    signature = PTR_SIGNATURE if kind == "ptr" else MU_SIGNATURE
    contract = PTR_CONTRACT if kind == "ptr" else MU_CONTRACT
    return signature + b"\n" + constructor.ghost_block(contract) + BODY + b"\n"


def target_line(verified: bytes, marker: bytes) -> int | None:
    return next((i for i, line in enumerate(verified.splitlines(), 1)
                 if marker in line), None)


def caller_source(kind: str, variant: str, constructor) -> bytes:
    require(variant in POSITIVES[kind] + NEGATIVES[kind],
            f"unknown {kind} fixture variant {variant}")
    name = probe_name(kind, variant).encode()
    result_type = (b"*mut *const Element" if kind == "ptr" else
                   b"std::mem::MaybeUninit<*const Element>")
    inputs = (b"a: *mut *const Element, b: *mut *const Element" if kind == "ptr" else
              b"a: std::mem::MaybeUninit<*const Element>, "
              b"b: std::mem::MaybeUninit<*const Element>")
    choose = (b"true" if variant in {"true", "none", "wrong_inner"} else
              b"false" if variant in {"false", "some"} else b"condition")
    selected = b"a" if choose == b"true" else b"b" if choose == b"false" else \
        b"(if condition { a } else { b })"
    selected_pointer = (b"a as pointer" if choose == b"true" else
                        b"b as pointer" if choose == b"false" else
                        b"(if condition { a as pointer } else { b as pointer })")
    pre = (b"req thread_token(?t) &*& t == currentThread &*& "
           b"*cell |-> ?cell_value &*& [?f](*frame |-> ?frame_value)")
    if kind == "mu":
        pre += b" &*& " + OWN_A + b" &*& " + OWN_B
        if variant in {"none", "some", "wrong_inner"}:
            pre += b" &*& " + INNER + b"(a) == none &*& " + INNER + b"(b) == some(?p)"
    pre += b";\n"
    resources = (b"thread_token(t) &*& *cell |-> cell_value &*& "
                 b"[f](*frame |-> frame_value)")
    if kind == "ptr":
        selected_post = b"(result as pointer) == " + selected_pointer
    else:
        selected_post = OWN_RESULT + b" &*& result == " + selected
        selected_post += b" &*& " + INNER + b"(result) == " + \
            (b"none" if variant in {"none", "wrong_inner"} else
             b"some(p)" if variant == "some" else
             b"(if condition { " + INNER + b"(a) } else { " + INNER + b"(b) })")
    post = resources + b" &*& " + selected_post
    if variant == "wrong_result":
        post = resources + b" &*& (result as pointer) != " + selected_pointer
    elif variant == "wrong_inner":
        post = resources + b" &*& " + OWN_RESULT + b" &*& " + \
            INNER + b"(result) == some(?invented) &*& result == a"
    elif variant == "false_post":
        post = b"false"
    elif variant == "duplicate_frame":
        post = post + b" &*& [f](*frame |-> frame_value)"
    elif variant == "lost_cell":
        post = post.replace(b"*cell |-> cell_value &*& ", b"")
    contract = pre + b"// TARGET_POSTCONDITION\nens " + post + \
        b";\non_unwind_ens false;"
    body = b"{\n    let result = " + helper_name(kind).encode() + \
        b"(" + choose + b", a, b);\n"
    if variant == "assert_false":
        body += b"    // TARGET_ASSERTION\n    //@ assert false;\n"
    body += b"    result\n}\n"
    return (b"pub unsafe fn " + name + b"<Element>(condition: bool, " +
            inputs + b", cell: *mut u8, frame: *const u8) -> " + result_type +
            b"\n" + constructor.ghost_block(contract) + body)


def source_mutation(original: bytes, verified: bytes, mutation: str,
                    kind: str, constructor) -> tuple[bytes, bytes]:
    require(mutation in SOURCE_MUTATIONS, f"unknown source mutation {mutation}")
    def runtime(old: bytes, new: bytes) -> tuple[bytes, bytes]:
        require(original.count(old) == verified.count(old) == 1,
                f"source mutation {mutation} target is not unique")
        return original.replace(old, new, 1), verified.replace(old, new, 1)
    if mutation == "identity":
        old = helper_name(kind).encode()
        new = old + b"_impostor"
        require(original.count(old) == verified.count(old) == 2,
                "identity mutant requires one helper and one call")
        result = original.replace(old, new), verified.replace(old, new)
    elif mutation == "inputtype":
        old = b"condition: bool, a:"
        require(original.count(old) == verified.count(old) == 2,
                "input type mutant requires helper and probe")
        result = (
            original.replace(old, b"condition: &bool, a:", 1)
                .replace(CALL, b"std::intrinsics::select_unpredictable(*condition, a, b)", 1)
                .replace(b"(condition, a, b);", b"(&condition, a, b);", 1),
            verified.replace(old, b"condition: &bool, a:", 1)
                .replace(CALL, b"std::intrinsics::select_unpredictable(*condition, a, b)", 1)
                .replace(b"(condition, a, b);", b"(&condition, a, b);", 1),
        )
    elif mutation == "operand_order":
        result = runtime(CALL,
                         b"std::intrinsics::select_unpredictable(condition, b, a)")
    elif mutation == "resulttype":
        if kind == "ptr":
            result = (
                original.replace(b") -> *mut *const Element\n",
                                 b") -> *const *const Element\n", 1)
                .replace(CALL, CALL + b" as *const *const Element", 1)
                .replace(b"(condition, a, b);", b"(condition, a, b) as *mut *const Element;", 1),
                verified.replace(b") -> *mut *const Element\n",
                                 b") -> *const *const Element\n", 1)
                .replace(CALL, CALL + b" as *const *const Element", 1)
                .replace(b"(condition, a, b);", b"(condition, a, b) as *mut *const Element;", 1),
            )
        else:
            old = b") -> std::mem::MaybeUninit<*const Element>\n"
            new = b") -> Option<std::mem::MaybeUninit<*const Element>>\n"
            require(original.count(old) == verified.count(old) == 2,
                    "MU output type mutant expects helper and caller")
            result = (
                original.replace(old, new, 1).replace(CALL, b"Some(" + CALL + b")", 1)
                    .replace(b"(condition, a, b);", b"(condition, a, b).unwrap();", 1),
                verified.replace(old, new, 1).replace(CALL, b"Some(" + CALL + b")", 1)
                    .replace(b"(condition, a, b);", b"(condition, a, b).unwrap();", 1),
            )
    elif mutation == "binding":
        old = b"condition: bool, a:"
        require(original.count(old) == verified.count(old) == 2,
                "binding mutant requires helper and caller")
        result = (
            original.replace(old, b"condition: bool, left:", 1)
                .replace(CALL, b"std::intrinsics::select_unpredictable(condition, left, b)", 1),
            verified.replace(old, b"condition: bool, left:", 1)
                .replace(CALL, b"std::intrinsics::select_unpredictable(condition, left, b)", 1),
        )
    elif mutation == "contract":
        old = b"on_unwind_ens false;"
        require(verified.count(old) == 2, "expected helper and caller unwind contracts")
        result = original, verified.replace(old, b"on_unwind_ens true;", 1)
    else:
        result = runtime(b"{\n    std::intrinsics::select_unpredictable",
                         b"{\n    let _ = condition;\n    std::intrinsics::select_unpredictable")
    require(constructor.strip_ghost_annotations(result[1]) == result[0],
            "source mutation changed original/verified runtime differently")
    return result


def make_case(case_dir: Path, kind: str, variant: str, cert: dict,
              constructor, admission: str | None = None) -> None:
    helper = helper_source(kind, constructor)
    caller = caller_source(kind, variant, constructor)
    verified = PREFIX + helper + b"\n" + caller
    original = constructor.strip_ghost_annotations(verified)
    require(verified.count(CALL) == 1, "expected one checked intrinsic body")
    require(original.count(BODY) == 1, "runtime helper body is not unique")
    canonical = original, verified
    if admission is not None:
        original, verified = source_mutation(original, verified, admission,
                                              kind, constructor)
    case_dir.mkdir(parents=True, exist_ok=False)
    constructor.write_case(case_dir, original, verified, {
        **cert,
        "variant": variant,
        "specialization": kind,
        "tool_profile": PROFILE,
        "helper_name": helper_name(kind),
        "probe_name": probe_name(kind, variant),
        "target_postcondition_line": target_line(verified, b"TARGET_POSTCONDITION"),
        "target_assertion_line": target_line(verified, b"TARGET_ASSERTION"),
        "probe_return_line": target_line(verified, b"    result"),
        "source_mutation": admission,
        "canonical_original_sha256": sha(canonical[0]),
        "canonical_verified_sha256": sha(canonical[1]),
        "external_intrinsic_call_count": 1,
        "ghost_strip_exact": True,
        "full_select_proved": False,
    })
    if admission is not None:
        (case_dir / "canonical").mkdir()
        (case_dir / "canonical/original.lib.rs").write_bytes(canonical[0])
        (case_dir / "canonical/verified.lib.rs").write_bytes(canonical[1])


def function_log(log: str, name: str) -> str:
    marker = f"Verifying function '{name}'"
    start = log.find(marker)
    if start < 0:
        return ""
    end = log.find("Verifying function '", start + len(marker))
    return log[start:end if end >= 0 else None]


def strict_positive_evidence(evidence: dict[str, bool]) -> bool:
    return all(evidence.get(field) is True for field in (
        "source_exact", "stage_integrity", "frontend_refinement",
        "typed_mir_identity", "full_certificate", "modeled_typed_call",
        "safe_prototype", "helper_return_leak", "probe_return_leak",
        "verifier_success",
    ))


def strict_negative_evidence(evidence: dict[str, bool]) -> bool:
    return all(evidence.get(field) is True for field in (
        "positive_prerequisite", "source_exact", "stage_integrity",
        "frontend_refinement", "typed_mir_identity", "full_certificate",
        "modeled_typed_call", "safe_prototype", "helper_return_leak",
        "probe_entered", "one_verifier_error", "target_location",
        "target_message",
    ))


def strict_admission_evidence(evidence: dict[str, bool]) -> bool:
    return all(evidence.get(field) is True for field in (
        "source_exact", "stage_integrity", "frontend_refinement",
        "mutant_exact", "exact_fatal", "before_proof", "verifier_exit_two",
    ))


def admission_reasons(kind: str, mode: str, mutation: str) -> tuple[str, ...]:
    require(kind in KINDS and mode in {"source", "mir"},
            "unknown admission specialization/mode")
    # The v2 actual-body gate deliberately reports the exact failing place.
    # Preserve the v1 spellings for the separately pinned historical profile.
    if PROFILE != "experimental-source-linked-select-pointer-intrinsics-v1":
        if mode == "source" and mutation == "identity":
            return ("expected one exact SAFE helper/probe or actual body",)
        if mode == "mir" and mutation in {"operand_order", "operand_source"}:
            return ("standalone place: _5",)
        if mode == "mir" and mutation == "predecessor_source":
            return ("standalone place: _2",)
    if mode == "source" and mutation == "identity":
        return ("expected one exact SAFE helper and one listed probe",)
    if mode == "source" and mutation == "inputtype":
        return ("helper HIR generic count/kind",)
    if mode == "source" and mutation in {"resulttype", "binding"}:
        signature = PTR_SIGNATURE if kind == "ptr" else MU_SIGNATURE
        return ("source marker missing: " + signature.decode(),)
    return SOURCE_REASONS[mutation] if mode == "source" else MIR_REASONS[mutation]


def matches_admission_fatal(message: str, reasons: tuple[str, ...]) -> bool:
    return any(message == f'Fatal error: exception Failure("{REJECT_PREFIX}{reason}")'
               for reason in reasons)


def matches_wrong_result_error(kind: str, message: str) -> bool:
    pattern = WRONG_POINTER_RESULT_ERROR if kind == "ptr" else \
        WRONG_WRAPPER_INNER_ERROR if kind == "mu" else None
    return pattern is not None and pattern.search(message) is not None


def replace_once(source: str, old: str, new: str, mutation: str) -> str:
    require(source.count(old) == 1,
            f"{mutation}: expected one target, found {source.count(old)}")
    return source.replace(old, new, 1)


def call_arguments(call: str, constructor) -> tuple[int, int, list[str]]:
    bracket = call.index("[", call.index("args = "))
    start = bracket + 1
    depth = 1
    end = -1
    for position in range(start, len(call)):
        if call[position] == "[":
            depth += 1
        elif call[position] == "]":
            depth -= 1
            if depth == 0:
                end = position
                break
    require(end >= 0, "intrinsic argument list is unterminated")
    contents = call[start:end]
    arguments = []
    cursor = 0
    while cursor < len(contents):
        opening = contents.find("(", cursor)
        if opening < 0:
            break
        item = constructor.mir_balanced_item(contents, opening)
        arguments.append(item)
        cursor = opening + len(item)
    require(len(arguments) == 3, "expected exactly three intrinsic operands")
    return start, end, arguments


def mutate_intrinsic_mir(decoded: str, kind: str, mutation: str,
                         constructor) -> str:
    """One decoded typed MIR edit; exact shape is confirmed by hosted export."""
    require(kind in KINDS and mutation in MIR_MUTATIONS,
            "unknown direct intrinsic MIR mutation")
    marker = f'defPath = "{helper_name(kind)}"'
    require(decoded.count(marker) == 1, "checked helper MIR body is not unique")
    at = decoded.index(marker)
    lead = decoded.rfind("    ( defKind =", 0, at)
    require(lead >= 0, "checked helper MIR body opening is missing")
    opening = decoded.index("(", lead)
    body = constructor.mir_balanced_item(decoded, opening)
    tail = opening + len(body)
    call_marker = "call = ("
    require(body.count(call_marker) == 1, "helper must contain exactly one call terminator")
    call_at = body.index(call_marker) + len("call = ")
    call = constructor.mir_balanced_item(body, call_at)
    if mutation == "fndef":
        call = replace_once(call, MIR_CALL,
                            'name = "std::intrinsics::assert_inhabited"', mutation)
    elif mutation == "type_argument":
        call = replace_once(call, 'param = "Element"',
                            'param = "Mutant"', mutation)
    elif mutation in {"operand_order", "operand_source"}:
        start, end, arguments = call_arguments(call, constructor)
        if mutation == "operand_order":
            arguments[1], arguments[2] = arguments[2], arguments[1]
        else:
            second = re.search(r'name = "(_\d+)"', arguments[1])
            third = re.search(r'name = "(_\d+)"', arguments[2])
            require(second is not None and third is not None and
                    second.group(1) != third.group(1),
                    "operand source locals are not distinct")
            arguments[1] = arguments[1].replace(
                second.group(0), third.group(0), 1)
        call = (call[:start] + "\n                  " +
                ",\n                  ".join(arguments) + " " + call[end:])
    elif mutation == "result_local":
        prefix, destination = call.split("destination = (", 1)
        destination = replace_once(destination, 'name = "_0"',
                                   'name = "_1"', mutation)
        call = prefix + "destination = (" + destination
    elif mutation == "cfg_successor":
        call = replace_once(call, "target = (something = (index = 1))",
                            "target = (something = (index = 0))", mutation)
    elif mutation == "cfg_unwind":
        call = replace_once(call, "unwindAction = (unreachable = void)",
                            "unwindAction = (continue = void)", mutation)
    elif mutation == "result_type":
        output_at = body.index("      output = (") + len("      output = ")
        selected = constructor.mir_balanced_item(body, output_at)
        if kind == "ptr":
            selected = replace_once(selected, "mutability = (mut = void)",
                                    "mutability = (not = void)", mutation)
        else:
            selected = replace_once(selected, 'param = "Element"',
                                    'param = "Mutant"', mutation)
        body = body[:output_at] + selected + body[output_at + len(
            constructor.mir_balanced_item(body, output_at)):]
    elif mutation == "input_type":
        inputs_at = body.index("      inputs = [") + len("      inputs = [")
        inputs_end = body.index("      localDecls = [", inputs_at)
        inputs = body[inputs_at:inputs_end]
        old = ('param = "Element"' if kind == "mu" else
               "mutability = (mut = void)")
        new = ('param = "Mutant"' if kind == "mu" else
               "mutability = (not = void)")
        require(inputs.count(old) == 2, "input mutant expects both typed arguments")
        inputs = inputs.replace(old, new, 1)
        body = body[:inputs_at] + inputs + body[inputs_end:]
    elif mutation == "hir_binding":
        body = replace_once(body, 'name = "a"', 'name = "left"', mutation)
    elif mutation == "predecessor_source":
        body = replace_once(
            body, 'copy = (\n                        local = (name = "_2")',
            'copy = (\n                        local = (name = "_3")', mutation)
    elif mutation == "contract":
        head, contract = body.split("      contract = (", 1)
        contract, rest = contract.split("      inputs = [", 1)
        require(contract.count("thread_token") >= 2,
                "exported SAFE contract lacks req and ens thread resources")
        contract = contract.replace("thread_token", "thread_token_mutant", 1)
        body = head + "      contract = (" + contract + "      inputs = [" + rest
    elif mutation == "extra_operation":
        statements_at = body.index("statements = [") + len("statements = [")
        first = body.index("( sourceInfo = (", statements_at)
        statement = constructor.mir_balanced_item(body, first)
        body = body[:first] + statement + ",\n            " + body[first:]
    if mutation in {"fndef", "type_argument", "operand_order", "operand_source",
                    "result_local", "cfg_successor", "cfg_unwind"}:
        body = body[:call_at] + call + body[call_at + len(
            constructor.mir_balanced_item(body, call_at)):]
    require(body != decoded[opening:tail], "direct MIR mutant had no effect")
    return decoded[:opening] + body + decoded[tail:]


def make_mir_mutation_tool_home(tool_home: Path, schema: Path, repo_root: Path,
                                case_dir: Path, kind: str, mutation: str) -> Path:
    shadow = case_dir / "mutation-profile"
    binary = shadow / "bin"
    binary.mkdir(parents=True)
    source_bin = tool_home / "bin"
    for entry in source_bin.iterdir():
        if entry.name == "vf-rust-mir-exporter":
            continue
        target = binary / entry.name
        if entry.name == "verifast" and entry.is_file():
            shutil.copy2(entry, target)
        else:
            target.symlink_to(entry, target_is_directory=entry.is_dir())
    wrapper = binary / "vf-rust-mir-exporter"
    wrapper.write_text('''#!/usr/bin/env python3
import hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("sort4_select_intrinsic", @PREPARER@)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
constructor = module.load_script(Path(@CONSTRUCTOR@), "sort4_constructor_for_mir_mutant")
real = @REAL@
schema = @SCHEMA@
kind = @KIND@
mutation = @MUTATION@
record = Path(@RECORD@)
argv = sys.argv[1:]
proc = subprocess.run([real, *argv], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
sys.stderr.buffer.write(proc.stderr)
if proc.returncode:
    sys.stdout.buffer.write(proc.stdout)
    raise SystemExit(proc.returncode)
decoded = subprocess.run(["capnp", "decode", schema, "VfMir"], input=proc.stdout,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if decoded.returncode:
    sys.stderr.buffer.write(decoded.stderr)
    raise SystemExit(decoded.returncode)
try:
    canonical = decoded.stdout.decode()
    changed = module.mutate_intrinsic_mir(canonical, kind, mutation, constructor)
except Exception as exc:
    record.write_text(json.dumps({"kind": kind, "mutation": mutation,
                                  "error": str(exc)}) + "\\n")
    sys.stderr.write("SORT4-SELECT-INTRINSIC MIR mutant failed: " + str(exc) + "\\n")
    raise SystemExit(98)
encoded = subprocess.run(["capnp", "encode", schema, "VfMir"], input=changed.encode(),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if encoded.returncode:
    sys.stderr.buffer.write(encoded.stderr)
    raise SystemExit(encoded.returncode)
record.parent.mkdir(parents=True, exist_ok=True)
(record.parent / "canonical-mir.txt").write_text(canonical)
(record.parent / "mutated-mir.txt").write_text(changed)
(record.parent / "canonical-mir.bin").write_bytes(proc.stdout)
(record.parent / "mutated-mir.bin").write_bytes(encoded.stdout)
selected = next((Path(arg) for arg in argv if Path(arg).suffix == ".rs" and Path(arg).is_file()), None)
record.write_text(json.dumps({"kind": kind, "mutation": mutation, "matched": True,
    "exporter_exit": proc.returncode, "decode_exit": decoded.returncode,
    "encode_exit": encoded.returncode,
    "canonical_sha256": hashlib.sha256(proc.stdout).hexdigest(),
    "mutated_sha256": hashlib.sha256(encoded.stdout).hexdigest(),
    "selected_source_sha256": hashlib.sha256(selected.read_bytes()).hexdigest() if selected else None,
    "real_exporter_sha256": hashlib.sha256(Path(real).read_bytes()).hexdigest()},
    indent=2, sort_keys=True) + "\\n")
sys.stdout.buffer.write(encoded.stdout)
'''.replace("@PREPARER@", repr(str(repo_root / "research/challenge-8/check-select-pointer-intrinsics.py")))
   .replace("@CONSTRUCTOR@", repr(str(repo_root / "research/challenge-8/check-maybeuninit-new-pointer.py")))
   .replace("@REAL@", repr(str(source_bin / "vf-rust-mir-exporter")))
   .replace("@SCHEMA@", repr(str(schema)))
   .replace("@KIND@", repr(kind))
   .replace("@MUTATION@", repr(mutation))
   .replace("@RECORD@", repr(str(case_dir / "mutation-record.json"))))
    wrapper.chmod(0o755)
    shutil.copy2(wrapper, case_dir / "mir-exporter-wrapper.py")
    (case_dir / "mutation-profile.json").write_text(json.dumps({
        "kind": kind,
        "mutation": mutation,
        "base_console_sha256": sha((source_bin / "verifast").read_bytes()),
        "shadow_console_sha256": sha((binary / "verifast").read_bytes()),
        "real_exporter_sha256": sha((source_bin / "vf-rust-mir-exporter").read_bytes()),
        "wrapper_sha256": sha(wrapper.read_bytes()),
    }, indent=2, sort_keys=True) + "\n")
    return shadow


def classify_admission(case_dir: Path, runner: dict, kind: str, mutation: str,
                       mode: str, constructor) -> dict:
    require(mode in {"source", "mir"}, "unknown admission mode")
    verified = (case_dir / "verified/lib.rs").read_bytes()
    original = (case_dir / "original/lib.rs").read_bytes()
    fixture = json.loads((case_dir / "fixture.json").read_text())
    log = (case_dir / "verifast.log").read_text(errors="replace")
    fatal = [line for line in log.splitlines() if "Fatal error:" in line]
    reasons = admission_reasons(kind, mode, mutation)
    exact_fatal = len(fatal) == 1 and not any(": error:" in line for line in
                                                  log.splitlines()) and \
        matches_admission_fatal(fatal[0], reasons)
    stage = runner.get("stage_integrity", {})
    source_exact = constructor.strip_ghost_annotations(verified) == original
    stage_ok = set(stage) == {"exporter", "decode", "verifast", "refinement"} and \
        all(item.get("unchanged") is True for item in stage.values())
    frontend_ok = runner.get("exporter_exit") == 0 and \
        runner.get("decode_exit") == 0 and runner.get("refinement_exit") == 0
    record = None
    mutant_exact = False
    if mode == "source":
        canonical_original = (case_dir / "canonical/original.lib.rs").read_bytes()
        canonical_verified = (case_dir / "canonical/verified.lib.rs").read_bytes()
        mutant_exact = (
            sha(canonical_original) == fixture["canonical_original_sha256"] and
            sha(canonical_verified) == fixture["canonical_verified_sha256"] and
            source_mutation(canonical_original, canonical_verified,
                            mutation, kind, constructor) == (original, verified)
        )
    else:
        record_path = case_dir / "mutation-record.json"
        profile_path = case_dir / "mutation-profile.json"
        files = tuple(case_dir / name for name in (
            "canonical-mir.txt", "mutated-mir.txt",
            "canonical-mir.bin", "mutated-mir.bin"))
        if record_path.exists() and profile_path.exists() and \
                all(path.exists() for path in files):
            record = json.loads(record_path.read_text())
            profile = json.loads(profile_path.read_text())
            canonical_text = files[0].read_text()
            mutated_text = files[1].read_text()
            canonical_bin = files[2].read_bytes()
            mutated_bin = files[3].read_bytes()
            try:
                exact_text = mutate_intrinsic_mir(canonical_text, kind, mutation,
                                                  constructor) == mutated_text
            except ValueError:
                exact_text = False
            mutant_exact = (
                exact_text and record.get("kind") == kind and
                record.get("mutation") == mutation and record.get("matched") is True and
                record.get("exporter_exit") == 0 and record.get("decode_exit") == 0 and
                record.get("encode_exit") == 0 and
                record.get("canonical_sha256") == sha(canonical_bin) and
                record.get("mutated_sha256") == sha(mutated_bin) and
                canonical_bin != mutated_bin and
                record.get("selected_source_sha256") == sha(verified) and
                record.get("real_exporter_sha256") == profile.get("real_exporter_sha256") and
                profile.get("base_console_sha256") == profile.get("shadow_console_sha256") and
                profile.get("wrapper_sha256") == sha(
                    (case_dir / "mutation-profile/bin/vf-rust-mir-exporter").read_bytes())
            )
    before_proof = (CERT_MARKER not in log and
                    not re.search(r"Verifying function 'sort4_checked_select_", log) and
                    not re.search(r"Verifying function 'sort4_select_", log))
    evidence = {
        "source_exact": source_exact,
        "stage_integrity": stage_ok,
        "frontend_refinement": frontend_ok,
        "mutant_exact": mutant_exact,
        "exact_fatal": exact_fatal,
        "before_proof": bool(before_proof),
        "verifier_exit_two": runner.get("verifast_exit") == 2,
    }
    result = {
        "kind": kind,
        "mutation": mutation,
        "mode": mode,
        "classification": "INTENDED_ADMISSION_REJECTION"
            if strict_admission_evidence(evidence) else "INCONCLUSIVE",
        "accepted_component": False,
        "full_select_proved": False,
        "expected_reasons": reasons,
        "fatal": fatal,
        "admission_evidence": evidence,
        "mutation_record": record,
        "runner_result": runner,
    }
    (case_dir / "admission-classification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def classify_case(case_dir: Path, runner: dict, kind: str, variant: str,
                  constructor, prerequisite_positive: bool) -> dict:
    verified = (case_dir / "verified/lib.rs").read_bytes()
    original = (case_dir / "original/lib.rs").read_bytes()
    fixture = json.loads((case_dir / "fixture.json").read_text())
    log = (case_dir / "verifast.log").read_text(errors="replace")
    mir = (case_dir / "compiler-mir.txt").read_text(errors="replace")
    helper_log = function_log(log, helper_name(kind))
    probe_log = function_log(log, probe_name(kind, variant))
    stage = runner.get("stage_integrity", {})
    stage_ok = set(stage) == {"exporter", "decode", "verifast", "refinement"} and \
        all(item.get("unchanged") is True for item in stage.values())
    frontend_ok = runner.get("exporter_exit") == 0 and \
        runner.get("decode_exit") == 0 and runner.get("refinement_exit") == 0
    source_ok = constructor.strip_ghost_annotations(verified) == original and \
        verified != original and verified.count(BODY) == 1
    mir_ok = mir.count(f'defPath = "{helper_name(kind)}"') == 1 and \
        mir.count(f'defPath = "{probe_name(kind, variant)}"') == 1 and \
        mir.count(MIR_CALL) == 1
    full_cert = log.count(CERT_MARKER) == 1 and \
        not re.search(re.escape(REJECT_PREFIX), log)
    modeled_call = log.count(
        CERT_PREFIX + (" modeled typed pointer call 1" if kind == "ptr" else
                       " modeled typed wrapper call 1")) == 1
    safe_prototype = (
        f"Function '{helper_name(kind)}': Function prototype implementation check" in log)
    helper_return_leak = "Executing return statement" in helper_log and \
        "Leak check." in helper_log and \
        not any(": error:" in line for line in helper_log.splitlines())
    probe_return_leak = "Executing return statement" in probe_log and \
        "Leak check." in probe_log
    errors = [line for line in log.splitlines() if ": error:" in line]
    first_error = errors[0] if errors else None
    error_match = re.search(r"verified/lib\.rs\((\d+),", first_error or "")
    error_line = int(error_match.group(1)) if error_match else None
    target_line = (fixture["target_assertion_line"] if variant == "assert_false" else
                   fixture["target_postcondition_line"])
    if variant == "lost_cell":
        target_location = error_line == fixture["probe_return_line"] + 1
        target_message = bool(first_error and re.search(
            r"Function leaks heap chunks: points_to<u8>\(cell, cell_value\)$",
            first_error))
    elif variant == "assert_false":
        target_location = error_line == fixture["target_assertion_line"] + 1
        target_message = bool(first_error and re.search(
            r"Assertion might not hold\. \(Cannot prove false\.\)$", first_error))
    else:
        target_location = isinstance(target_line, int) and error_line in {
            target_line + 1, fixture["probe_return_line"]}
        pattern = {
            "false_post": r"Cannot prove condition\. \(Cannot prove false\.\)$",
            "duplicate_frame": r"No matching heap chunks: \[f\]points_to<u8>"
                r"\(frame, frame_value\)$",
        }.get(variant)
        target_message = bool(first_error and (
            matches_wrong_result_error(kind, first_error)
            if variant in {"wrong_result", "wrong_inner"} else
            pattern and re.search(pattern, first_error)))
    shared = {
        "source_exact": bool(source_ok),
        "stage_integrity": bool(stage_ok),
        "frontend_refinement": bool(frontend_ok),
        "typed_mir_identity": bool(mir_ok),
        "full_certificate": bool(full_cert),
        "modeled_typed_call": bool(modeled_call),
        "safe_prototype": bool(safe_prototype),
        "helper_return_leak": bool(helper_return_leak),
    }
    positive = {
        **shared,
        "probe_return_leak": bool(probe_return_leak),
        "verifier_success": runner.get("verifast_exit") == 0,
    }
    negative = {
        **shared,
        "positive_prerequisite": prerequisite_positive,
        "probe_entered": bool(probe_log) and bool(first_error) and first_error in probe_log,
        "one_verifier_error": runner.get("verifast_exit") == 1 and len(errors) == 1,
        "target_location": bool(target_location),
        "target_message": bool(target_message),
    }
    positive_pass = variant in POSITIVES[kind] and strict_positive_evidence(positive)
    negative_pass = variant in NEGATIVES[kind] and strict_negative_evidence(negative)
    result = {
        "kind": kind,
        "variant": variant,
        "classification": (
            "DIAGNOSTIC_POSITIVE" if positive_pass else
            "INTENDED_PROOF_REJECTION" if negative_pass else "INCONCLUSIVE"),
        "accepted_component": False,
        "full_select_proved": False,
        "tool_profile": PROFILE,
        "positive_evidence": positive,
        "negative_evidence": negative,
        "first_verifier_error": first_error,
        "first_verifier_error_line": error_line,
        "helper_entered": bool(helper_log),
        "probe_entered": bool(probe_log),
        "runner_result": runner,
    }
    (case_dir / "diagnostic-classification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def run_hosted_case(case: Path, args: argparse.Namespace, repo_root: Path,
                    constructor, tool_home: Path | None = None) -> dict:
    previous = os.environ.get("SORT4_SELECT_INTRINSIC_REPO_ROOT")
    os.environ["SORT4_SELECT_INTRINSIC_REPO_ROOT"] = str(repo_root)
    try:
        return constructor.run_case(
            case, args.schema, tool_home or args.tool_home,
            args.compiler_sysroot, repo_root,
            case.name, "diagnostic", certificate_mode=True)
    finally:
        if previous is None:
            os.environ.pop("SORT4_SELECT_INTRINSIC_REPO_ROOT", None)
        else:
            os.environ["SORT4_SELECT_INTRINSIC_REPO_ROOT"] = previous


def run_admissions(evidence: Path, cert: dict, args: argparse.Namespace,
                   repo_root: Path, constructor) -> list[dict]:
    results = []
    for kind in KINDS:
        for mutation in SOURCE_MUTATIONS:
            case = evidence / f"source_{kind}_{mutation}"
            try:
                make_case(case, kind, POSITIVES[kind][0], cert, constructor,
                          admission=mutation)
                runner = run_hosted_case(case, args, repo_root, constructor)
                result = classify_admission(case, runner, kind, mutation,
                                            "source", constructor)
            except Exception as exc:
                case.mkdir(parents=True, exist_ok=True)
                result = {"kind": kind, "mutation": mutation, "mode": "source",
                          "classification": "INCONCLUSIVE", "accepted_component": False,
                          "full_select_proved": False,
                          "harness_exception": f"{type(exc).__name__}: {exc}"}
                (case / "admission-classification.json").write_text(
                    json.dumps(result, indent=2, sort_keys=True) + "\n")
            results.append(result)
        for mutation in MIR_MUTATIONS:
            case = evidence / f"mir_{kind}_{mutation}"
            try:
                make_case(case, kind, POSITIVES[kind][0], cert, constructor)
                shadow = make_mir_mutation_tool_home(
                    args.tool_home, args.schema, repo_root, case, kind, mutation)
                runner = run_hosted_case(case, args, repo_root, constructor, shadow)
                result = classify_admission(case, runner, kind, mutation,
                                            "mir", constructor)
            except Exception as exc:
                case.mkdir(parents=True, exist_ok=True)
                result = {"kind": kind, "mutation": mutation, "mode": "mir",
                          "classification": "INCONCLUSIVE", "accepted_component": False,
                          "full_select_proved": False,
                          "harness_exception": f"{type(exc).__name__}: {exc}"}
                (case / "admission-classification.json").write_text(
                    json.dumps(result, indent=2, sort_keys=True) + "\n")
            results.append(result)
    return results


def check_intrinsics(args: argparse.Namespace) -> dict:
    if os.environ.get("GITHUB_ACTIONS") != "true" or \
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \
            os.environ.get("RUNNER_OS") != "Linux":
        raise SystemExit("intrinsic select checks require GitHub-hosted Linux Actions")
    repo_root = Path(__file__).resolve().parents[2]
    constructor = load_script(
        repo_root / "research/challenge-8/check-maybeuninit-new-pointer.py",
        "sort4_constructor_for_select_intrinsics")
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    source_cert = source_certificate(repo_root, constructor)
    (evidence / "source-certificate.json").write_text(
        json.dumps(source_cert, indent=2, sort_keys=True) + "\n")
    ctor = json.loads(args.constructor_summary.read_text())
    asptr = json.loads(args.as_mut_ptr_summary.read_text())
    classifier = json.loads(args.classifier_summary.read_text()) \
        if args.classifier_summary is not None else None
    same_run = args.constructor_summary.resolve().parents[1] == \
        args.as_mut_ptr_summary.resolve().parents[1] == evidence.parent
    prerequisites = {
        "constructor_accepted": ctor.get("constructor_acceptance") is True,
        "as_mut_ptr_accepted": asptr.get("accepted_component") is True and
            asptr.get("classification") == "COMPONENT_ACCEPTED",
        "same_run_evidence": same_run,
        "new_profile_selected": os.environ.get("SORT4_SELECT_PROFILE") == PROFILE and PROFILE in AUTHORIZED_PROFILES,
        "classifier_self_check": (
            classifier is not None and classifier.get("pass") is True and
            classifier.get("mutant_count") == 60 and
            classifier.get("message_mutant_count") == 10 and
            classifier.get("admission_message_mutant_count") == (
                4 if PROFILE == "experimental-source-linked-select-pointer-intrinsics-v1"
                else 28) and
            args.classifier_summary.resolve().parent == evidence.parent),
    }
    if not all(prerequisites.values()):
        result = {
            "classification": "INCONCLUSIVE", "accepted_component": False,
            "full_select_proved": False, "prerequisites": prerequisites,
            "cases": [], "cases_not_run": list(KINDS),
        }
        (evidence / "summary.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result
    results = []
    for kind in KINDS:
        variants = POSITIVES[kind] + NEGATIVES[kind]
        for variant in variants:
            prerequisite_positive = all(
                item["classification"] == "DIAGNOSTIC_POSITIVE"
                for item in results if item["kind"] == kind and
                item["variant"] in POSITIVES[kind])
            if variant in NEGATIVES[kind] and not prerequisite_positive:
                break
            case = evidence / f"select_{kind}_{variant}"
            make_case(case, kind, variant, source_cert, constructor)
            runner = run_hosted_case(case, args, repo_root, constructor)
            result = classify_case(case, runner, kind, variant, constructor,
                                   prerequisite_positive)
            results.append(result)
            if result["classification"] == "INCONCLUSIVE":
                break
    base_pass = (len(results) == sum(len(POSITIVES[kind]) + len(NEGATIVES[kind])
                                     for kind in KINDS) and
                 all(item["classification"] == "DIAGNOSTIC_POSITIVE"
                     for item in results if item["variant"] in POSITIVES[item["kind"]]) and
                 all(item["classification"] == "INTENDED_PROOF_REJECTION"
                     for item in results if item["variant"] in NEGATIVES[item["kind"]]))
    admissions = run_admissions(evidence, source_cert, args, repo_root, constructor) \
        if base_pass else []
    admission_pass = (len(admissions) == len(KINDS) *
                      (len(SOURCE_MUTATIONS) + len(MIR_MUTATIONS)) and
                      all(item["classification"] == "INTENDED_ADMISSION_REJECTION"
                          for item in admissions))
    accepted = bool(base_pass and admission_pass and all(prerequisites.values()))
    result = {
        "classification": "COMPONENT_ACCEPTED" if accepted else "INCONCLUSIVE",
        "accepted_component": accepted,
        "full_select_proved": False,
        "tool_profile": PROFILE,
        "feasibility_only": False,
        "prerequisites": prerequisites,
        "source_certificate": source_cert,
        "cases": results,
        "cases_not_run": [f"{kind}_{variant}" for kind in KINDS
                          for variant in POSITIVES[kind] + NEGATIVES[kind]
                          if not any(item["kind"] == kind and item["variant"] == variant
                                     for item in results)],
        "admission_cases": admissions,
        "admission_cases_not_run": [f"{kind}_{mutation}" for kind in KINDS
                                    for mutation in SOURCE_MUTATIONS + MIR_MUTATIONS
                                    if not any(item["kind"] == kind and
                                               item["mutation"] == mutation
                                               for item in admissions)],
    }
    (evidence / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-home", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--constructor-summary", type=Path, required=True)
    parser.add_argument("--as-mut-ptr-summary", type=Path, required=True)
    parser.add_argument("--classifier-summary", type=Path)
    args = parser.parse_args()
    result = check_intrinsics(args)
    print(json.dumps({"classification": result["classification"],
                      "cases_run": len(result["cases"]),
                      "evidence": str(args.evidence.resolve())}))
    if not result["accepted_component"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
