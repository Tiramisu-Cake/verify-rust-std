#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted, source-linked diagnostic for the pointer as_mut_ptr storage cast.

The helper is safe and uses an elided mutable-reference lifetime, as the real
method does. Its callers are unsafe proof probes. These are deliberately partial
diagnostics, not a method summary or a full select_unpredictable proof.
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


MAYBE_UNINIT_SHA256 = "1230d267542337ee2842c29d8227cf8a58fe75c53a2a70efaee3922c4e8e25c0"
SOURCE_SIGNATURE = b"pub const fn as_mut_ptr(&mut self) -> *mut T"
SOURCE_BODY = (
    b"{\n"
    b"        // `MaybeUninit` and `ManuallyDrop` are both `repr(transparent)` so we can cast the pointer.\n"
    b"        self as *mut _ as *mut T\n"
    b"    }"
)
HELPER_NAME = "sort4_checked_as_mut_ptr"
VARIANTS = (
    "unknown", "none", "some", "wrong_result", "false_post",
    "assert_false", "duplicate_frame", "lost_cell", "invent_initialized",
)
POSITIVES = {"unknown", "none", "some"}
NEGATIVES = set(VARIANTS) - POSITIVES
MIR_MUTATIONS = (
    "operand", "return", "casttype", "outputtype", "inputtype",
    "identity", "binding", "contract", "additional_operation",
)
SOURCE_MUTATIONS = (
    "operand", "return", "casttype", "inputtype", "identity",
    "binding", "contract", "additional_operation",
)
CERT_MARKER = "SORT4-AS-MUT-PTR: full typed body MIR graph accepted"
POINTER_OWN = b"std::mem::MaybeUninit_pointer_own::<Element>()(t, value)"
PROFILE = os.environ.get("SORT4_SELECT_PROFILE", "experimental-s6-26.10-v1")
INVENT_INITIALIZED_ERROR = re.compile(
    r"verified/lib\.rs\(\d+,\d+(?:-\d+(?:,\d+)?)?\): error: "
    r"Cannot prove that 'std::mem::MaybeUninit::inner"
    r"\(pointer_typeid\(Element_typeid\), value\)' "
    r"is not an instance of constructor 'none'$"
)
LOCAL_SIGNATURE = (
    "pub fn sort4_checked_as_mut_ptr<Element>(storage: &mut "
    "std::mem::MaybeUninit<*const Element>) -> *mut *const Element"
)
SOURCE_REASONS = {
    "operand": "local body differs from exact source specialization",
    "return": "local body differs from exact source specialization",
    "casttype": "local body differs from exact source specialization",
    "inputtype": "source marker missing: " + LOCAL_SIGNATURE,
    "identity": "expected one local checked body",
    "binding": "source marker missing: " + LOCAL_SIGNATURE,
    "contract": "local SAFE contract/source signature changed",
    "additional_operation": "local body differs from exact source specialization",
}
MIR_REASONS = {
    "operand": "place/projection: _3",
    "return": "place/projection: _0",
    "casttype": "pointer cast kind/target type",
    "outputtype": "result type",
    "inputtype": "receiver type or elided lifetime",
    "identity": "expected one local checked body",
    "binding": "debug binding count/name",
    "contract": "exported SAFE contract annotation",
    "additional_operation": "statement count/order",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def matches_invent_initialized_error(message: str) -> bool:
    return INVENT_INITIALIZED_ERROR.search(message) is not None


def load_matrix(repo_root: Path):
    path = repo_root / "research/challenge-8/overnight-s6/check-maybeuninit-new-pointer.py"
    spec = importlib.util.spec_from_file_location("sort4_constructor_matrix", path)
    require(spec is not None and spec.loader is not None, "constructor matrix loader unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_certificate(repo_root: Path, matrix) -> tuple[bytes, dict]:
    path = repo_root / "library/core/src/mem/maybe_uninit.rs"
    source = path.read_bytes()
    require(sha(source) == MAYBE_UNINIT_SHA256, "MaybeUninit source pin changed")
    body = matrix.extract_braced_item(source, SOURCE_SIGNATURE)
    require(body == SOURCE_BODY, "as_mut_ptr expression or comment changed")
    require(body.count(b"self") == 1 and body.count(b"*mut T") == 1,
            "expected exactly one receiver identifier and one target cast")
    # A free function cannot name its parameter `self`. This is the only body
    # substitution; T is instantiated as *const Element in the resulting cast.
    specialized = body.replace(b"self", b"storage").replace(
        b"*mut T", b"*mut *const Element")
    require(specialized.count(b"storage as *mut _ as *mut *const Element") == 1,
            "specialized body no longer contains the exact source expression")
    return specialized, {
        "source_path": str(path),
        "source_sha256": sha(source),
        "source_signature": SOURCE_SIGNATURE.decode(),
        "source_body_sha256": sha(body),
        "source_body_exact": True,
        "body_substitutions": [
            "sole receiver identifier self -> storage (free-function syntax)",
            "sole type occurrence T -> *const Element (pointer specialization)",
        ],
        "specialized_body_sha256": sha(specialized),
        "adapter_limit": "ordinary non-const safe function; the generic const method is not proved",
        "target_obligation": (
            "result preserves the complete modeled storage pointer, wrapper cell, "
            "defined pointer-value ownership and unrelated frame; thread preserved "
            "and no unwind"
        ),
        "initialization_domain": "unknown/none/some ghost states; the cast does not read the value",
        "ownership_limit": (
            "certificate_mode=True with the accepted pointer-own definition; "
            "callers supply and receive the same defined pointer-value resource. "
            "This does not establish storage ownership at actual select call sites"
        ),
    }


def probe_name(variant: str) -> str:
    return "sort4_as_mut_ptr_" + variant + "_probe"


def target_line(verified: bytes, marker: bytes) -> int | None:
    return next((index for index, line in enumerate(verified.splitlines(), 1)
                 if marker in line), None)


def source_mutation(original: bytes, verified: bytes, mutation: str,
                    matrix) -> tuple[bytes, bytes]:
    """Apply one compilable fixture mutation; the repository std stays pinned."""
    require(mutation in SOURCE_MUTATIONS, f"unknown source mutation: {mutation}")

    def replace_runtime(old: bytes, new: bytes) -> tuple[bytes, bytes]:
        require(original.count(old) == 1 and verified.count(old) == 1,
                f"source {mutation} must have one runtime target")
        return original.replace(old, new, 1), verified.replace(old, new, 1)

    expression = b"storage as *mut _ as *mut *const Element"
    if mutation == "operand":
        result = replace_runtime(expression,
                                 b"(&mut *storage) as *mut _ as *mut *const Element")
    elif mutation == "return":
        result = replace_runtime(expression, b"std::ptr::null_mut()")
    elif mutation == "casttype":
        result = replace_runtime(expression,
                                 b"storage as *mut _ as *mut u8 as *mut *const Element")
    elif mutation == "inputtype":
        require(original.count(b"*const Element") >= 4,
                "input type mutation lost pointer specialization")
        result = (original.replace(b"*const Element", b"*mut Element"),
                  verified.replace(b"*const Element", b"*mut Element"))
    elif mutation == "identity":
        result = (original.replace(HELPER_NAME.encode(),
                                   (HELPER_NAME + "_impostor").encode()),
                  verified.replace(HELPER_NAME.encode(),
                                   (HELPER_NAME + "_impostor").encode()))
    elif mutation == "binding":
        original_helper, original_probe = original.split(b"pub unsafe fn ", 1)
        verified_helper, verified_probe = verified.split(b"pub unsafe fn ", 1)
        require(b"storage" in original_helper and b"storage" in verified_helper,
                "binding mutation has no helper receiver")
        result = (original_helper.replace(b"storage", b"cell") +
                  b"pub unsafe fn " + original_probe,
                  verified_helper.replace(b"storage", b"cell") +
                  b"pub unsafe fn " + verified_probe)
    elif mutation == "contract":
        old = b"(result as pointer) == (storage as pointer);"
        require(verified.count(old) == 2, "contract mutation expects helper and probe posts")
        result = original, verified.replace(old,
            b"(result as pointer) != (storage as pointer);", 1)
    else:
        result = replace_runtime(
            b"{\n        // `MaybeUninit`",
            b"{\n        let _ = storage as *mut _;\n        // `MaybeUninit`")
    require(result != (original, verified), "source mutation had no effect")
    require(matrix.strip_ghost_annotations(result[1]) == result[0],
            "source mutant changed original/verified runtime differently")
    return result


def make_case(case_dir: Path, specialized: bytes, certificate: dict,
              matrix, variant: str, admission: str | None = None) -> None:
    require(variant in VARIANTS, f"unknown as_mut_ptr diagnostic variant: {variant}")
    # Keep the cast body unannotated. Contracts are the only difference between
    # original and verified files; the helper is checked through its own body.
    contract = (
        b"req thread_token(?t) &*& t == currentThread &*& "
        b"*storage |-> ?value &*& " + POINTER_OWN + b";\n"
        b"ens thread_token(t) &*& *storage |-> value &*& "
        + POINTER_OWN + b" &*& "
        b"(result as pointer) == (storage as pointer);\n"
        b"on_unwind_ens false;"
    )
    helper = (
        b"pub fn " + HELPER_NAME.encode() +
        b"<Element>(storage: &mut std::mem::MaybeUninit<*const Element>) "
        b"-> *mut *const Element\n" + matrix.ghost_block(contract) +
        specialized + b"\n"
    )
    state = {
        "unknown": b"",
        "none": b" &*& std::mem::MaybeUninit::inner(value) == none",
        "some": b" &*& std::mem::MaybeUninit::inner(value) == some(?p)",
        "invent_initialized": b" &*& std::mem::MaybeUninit::inner(value) == none",
    }.get(variant, b"")
    state_post = {
        "unknown": b"",
        "none": b" &*& std::mem::MaybeUninit::inner(value) == none",
        "some": b" &*& std::mem::MaybeUninit::inner(value) == some(p)",
    }.get(variant, b"")
    resources = (
        b"thread_token(t) &*& *storage |-> value &*& "
        + POINTER_OWN + b" &*& "
        b"[f](*frame |-> frame_value)"
    )
    pre = (
        b"req thread_token(?t) &*& t == currentThread &*& "
        b"*storage |-> ?value &*& "
        + POINTER_OWN + b" &*& "
        b"[?f](*frame |-> ?frame_value)" + state + b";\n"
    )
    post = resources + state_post + b" &*& (result as pointer) == (storage as pointer)"
    if variant == "wrong_result":
        post = resources + b" &*& (result as pointer) != (storage as pointer)"
    elif variant == "false_post":
        post = b"false"
    elif variant == "duplicate_frame":
        post = resources + b" &*& [f](*frame |-> frame_value) &*& " \
            b"(result as pointer) == (storage as pointer)"
    elif variant == "lost_cell":
        post = (
            b"thread_token(t) &*& "
            + POINTER_OWN + b" &*& "
            b"[f](*frame |-> frame_value) &*& "
            b"(result as pointer) == (storage as pointer)"
        )
    elif variant == "invent_initialized":
        post = resources + b" &*& std::mem::MaybeUninit::inner(value) == some(?invented) " \
            b"&*& (result as pointer) == (storage as pointer)"
    probe_contract = pre + b"// TARGET_POSTCONDITION\nens " + post + b";\n" + \
        b"on_unwind_ens false;"
    probe_body = b"{\n    let result = " + HELPER_NAME.encode() + b"(storage);\n"
    if variant == "assert_false":
        probe_body += b"    // TARGET_ASSERTION\n    //@ assert false;\n"
    probe_body += b"    result\n}\n"
    probe = (
        b"pub unsafe fn " + probe_name(variant).encode() +
        b"<Element>(storage: &mut std::mem::MaybeUninit<*const Element>, "
        b"frame: *const u8) -> *mut *const Element\n" +
        matrix.ghost_block(probe_contract) + probe_body
    )
    verified = helper + b"\n" + probe
    original = matrix.strip_ghost_annotations(verified)
    require(original.count(specialized) == 1, "source body is not unique in fixture")
    require(original.count(HELPER_NAME.encode()) == 2, "expected one body and one caller")
    canonical = (original, verified)
    if admission is not None:
        original, verified = source_mutation(original, verified, admission, matrix)
    require(matrix.strip_ghost_annotations(verified) == original,
            "ghost stripping changed executable Rust")
    case_dir.mkdir(parents=True, exist_ok=False)
    matrix.write_case(case_dir, original, verified, {
        **certificate,
        "variant": variant,
        "probe_name": probe_name(variant),
        "target_postcondition_line": target_line(verified, b"TARGET_POSTCONDITION"),
        "target_assertion_line": target_line(verified, b"TARGET_ASSERTION"),
        "probe_signature_line": target_line(verified, b"pub unsafe fn " + probe_name(variant).encode()),
        "probe_return_line": target_line(verified, b"    result"),
        "expected_stage": "verifier",
        "expected_predicate": {
            "wrong_result": "modeled result pointer inequality",
            "false_post": "false normal postcondition",
            "assert_false": "false assertion after checked helper call",
            "duplicate_frame": "second fractional frame cell",
            "lost_cell": "unreturned storage points-to chunk at leak check",
            "invent_initialized": "invalid none-to-some initialization claim",
        }.get(variant, "pointer equality, wrapper cell/own and fractional frame"),
        "expected_location": (
            "named probe assertion" if variant == "assert_false" else
            "named probe leak check" if variant == "lost_cell" else
            "named probe normal postcondition"),
        "expected_class": "DIAGNOSTIC_POSITIVE" if variant in POSITIVES else
            "INTENDED_PROOF_REJECTION",
        "local_function_path_suffix": HELPER_NAME,
        "expected_external_call_count": 0,
        "ghost_stripped_equal": True,
        "intentionally_partial": False,
        "source_linked_checked_body_redirect": True,
        "source_admission_mutation": admission,
        "canonical_original_sha256": sha(canonical[0]),
        "canonical_verified_sha256": sha(canonical[1]),
    })
    if admission is not None:
        canonical_dir = case_dir / "canonical"
        canonical_dir.mkdir()
        (canonical_dir / "original.lib.rs").write_bytes(canonical[0])
        (canonical_dir / "verified.lib.rs").write_bytes(canonical[1])


def function_log(log: str, name: str) -> str:
    marker = f"Verifying function '{name}'"
    start = log.find(marker)
    end = log.find("Verifying function '", start + len(marker)) if start >= 0 else -1
    return log[start:end if end >= 0 else None] if start >= 0 else ""


def strict_positive_evidence(evidence: dict[str, bool]) -> bool:
    return all(evidence.get(key) is True for key in (
        "source_exact", "stage_integrity", "frontend_refinement", "typed_mir_identity",
        "certificate_marker", "safe_prototype", "helper_body_return_leak",
        "probe_body_return_leak", "verifier_success",
    ))


def strict_negative_evidence(evidence: dict[str, bool]) -> bool:
    return all(evidence.get(key) is True for key in (
        "positive_prerequisite", "source_exact", "stage_integrity",
        "frontend_refinement", "typed_mir_identity", "certificate_marker",
        "safe_prototype", "helper_body_return_leak", "named_probe_entered",
        "single_verifier_error", "target_location", "target_message",
        "leak_return_location",
    ))


def strict_admission_evidence(evidence: dict[str, bool]) -> bool:
    return all(evidence.get(key) is True for key in (
        "source_exact", "stage_integrity", "frontend_refinement",
        "mutant_exact", "exact_fatal", "before_proof", "verifier_exit_two",
    ))


def replace_once(source: str, old: str, new: str, label: str) -> str:
    require(source.count(old) == 1,
            f"{label}: expected one MIR target, found {source.count(old)}")
    return source.replace(old, new, 1)


def mutate_as_mut_ptr_mir(decoded: str, mutation: str, matrix) -> str:
    """Mutate only the helper's decoded typed MIR, retaining the real source."""
    require(mutation in MIR_MUTATIONS, f"unknown direct MIR mutation: {mutation}")
    marker = f'defPath = "{HELPER_NAME}"'
    require(decoded.count(marker) == 1, "helper MIR body identity is not unique")
    at = decoded.index(marker)
    lead = decoded.rfind("    ( defKind =", 0, at)
    require(lead >= 0, "helper MIR body opening is missing")
    opening = decoded.index("(", lead)
    body = matrix.mir_balanced_item(decoded, opening)
    tail = opening + len(body)
    if mutation == "operand":
        body = replace_once(body,
            'copy = (\n                        local = (name = "_3")',
            'copy = (\n                        local = (name = "_1")', mutation)
    elif mutation == "return":
        body = replace_once(body,
            'lhsPlace = (\n                    local = (name = "_0")',
            'lhsPlace = (\n                    local = (name = "_2")', mutation)
    elif mutation == "casttype":
        body = replace_once(body, "kind = (ptrToPtr = void)",
                            "kind = (pointerCoercion = void)", mutation)
    elif mutation == "outputtype":
        head, output = body.split("      output = (", 1)
        changed = replace_once(output,
            "mutability = (mut = void) ) ) ),",
            "mutability = (not = void) ) ) ),", mutation)
        body = head + "      output = (" + changed
    elif mutation == "inputtype":
        head, inputs = body.split("      inputs = [", 1)
        before_locals, rest = inputs.split("      localDecls = [", 1)
        before_locals = replace_once(before_locals,
            "mutability = (mut = void) ) ) ) ],",
            "mutability = (not = void) ) ) ) ],", mutation)
        body = head + "      inputs = [" + before_locals + "      localDecls = [" + rest
    elif mutation == "identity":
        body = replace_once(body, marker,
                            f'defPath = "{HELPER_NAME}_impostor"', mutation)
    elif mutation == "binding":
        body = replace_once(body, 'name = "storage"',
                            'name = "other"', mutation)
    elif mutation == "contract":
        head, annotations = body.split("      contract = (", 1)
        contract, rest = annotations.split("      inputs = [", 1)
        require(contract.count("MaybeUninit_pointer_own") == 2,
                "contract mutation expects exactly pre/post ownership occurrences")
        contract = contract.replace("MaybeUninit_pointer_own",
                                    "MaybeUninit_pointer_own_mutant", 1)
        body = head + "      contract = (" + contract + "      inputs = [" + rest
    elif mutation == "additional_operation":
        at_stmts = body.index("          statements = [")
        first = body.index("( sourceInfo = (", at_stmts)
        stmt = matrix.mir_balanced_item(body, first)
        body = body[:first] + stmt + ",\n            " + body[first:]
    require(body != decoded[opening:tail], "MIR mutation had no effect")
    return decoded[:opening] + body + decoded[tail:]


def make_mir_mutation_tool_home(tool_home: Path, schema: Path, repo_root: Path,
                                case_dir: Path, mutation: str) -> Path:
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
spec = importlib.util.spec_from_file_location("sort4_select_pointer", @PREPARER@)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
matrix = module.load_matrix(Path(@ROOT@))
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
decoded = subprocess.run(["capnp", "decode", schema, "VfMir"], input=proc.stdout,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if decoded.returncode:
    sys.stderr.buffer.write(decoded.stderr)
    raise SystemExit(decoded.returncode)
try:
    canonical = decoded.stdout.decode()
    changed = module.mutate_as_mut_ptr_mir(canonical, mutation, matrix)
except Exception as exc:
    record.write_text(json.dumps({"mutation": mutation, "error": str(exc)}) + "\\n")
    sys.stderr.write("SORT4-AS-MUT-PTR MIR mutant failed: " + str(exc) + "\\n")
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
record.write_text(json.dumps({"mutation": mutation, "matched": True,
    "exporter_exit": proc.returncode, "decode_exit": decoded.returncode,
    "encode_exit": encoded.returncode,
    "canonical_sha256": hashlib.sha256(proc.stdout).hexdigest(),
    "mutated_sha256": hashlib.sha256(encoded.stdout).hexdigest(),
    "selected_source_sha256": hashlib.sha256(selected.read_bytes()).hexdigest() if selected else None,
    "real_exporter_sha256": hashlib.sha256(Path(real).read_bytes()).hexdigest()},
    indent=2, sort_keys=True) + "\\n")
sys.stdout.buffer.write(encoded.stdout)
'''.replace("@PREPARER@", repr(str(repo_root / "research/challenge-8/overnight-s6/check-select-pointer.py")))
   .replace("@ROOT@", repr(str(repo_root)))
   .replace("@REAL@", repr(str(source_bin / "vf-rust-mir-exporter")))
   .replace("@SCHEMA@", repr(str(schema)))
   .replace("@MUTATION@", repr(mutation))
   .replace("@RECORD@", repr(str(case_dir / "mutation-record.json"))))
    wrapper.chmod(0o755)
    shutil.copy2(wrapper, case_dir / "mir-exporter-wrapper.py")
    (case_dir / "mutation-profile.json").write_text(json.dumps({
        "mutation": mutation,
        "base_console_sha256": sha((source_bin / "verifast").read_bytes()),
        "shadow_console_sha256": sha((binary / "verifast").read_bytes()),
        "real_exporter_sha256": sha((source_bin / "vf-rust-mir-exporter").read_bytes()),
        "wrapper_sha256": sha(wrapper.read_bytes()),
    }, indent=2, sort_keys=True) + "\n")
    return shadow


def admission_classification(case_dir: Path, runner_result: dict,
                             kind: str, mutation: str, matrix) -> dict:
    fixture = json.loads((case_dir / "fixture.json").read_text())
    original = (case_dir / "original/lib.rs").read_bytes()
    verified = (case_dir / "verified/lib.rs").read_bytes()
    log = (case_dir / "verifast.log").read_text(errors="replace")
    reasons = SOURCE_REASONS if kind == "source" else MIR_REASONS
    reason = reasons[mutation]
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    exact_fatal = fatal == [
        f'Fatal error: exception Failure("SORT4-AS-MUT-PTR: certificate mismatch: {reason}")'
    ]
    stage = runner_result.get("stage_integrity", {})
    frontend = (
        runner_result.get("exporter_exit") == 0 and
        runner_result.get("decode_exit") == 0 and
        runner_result.get("refinement_exit") == 0 and
        set(stage) == {"exporter", "decode", "verifast", "refinement"} and
        all(value.get("unchanged") is True for value in stage.values()) and
        matrix.strip_ghost_annotations(verified) == original and
        not re.search(r"Verifying function 'sort4_checked_as_mut_ptr'", log) and
        not re.search(r"Verifying function 'sort4_as_mut_ptr_", log) and
        CERT_MARKER not in log
    )
    source_exact = False
    mir_exact = False
    mutation_record = None
    if kind == "source":
        canonical_original = (case_dir / "canonical/original.lib.rs").read_bytes()
        canonical_verified = (case_dir / "canonical/verified.lib.rs").read_bytes()
        source_exact = (
            sha(canonical_original) == fixture["canonical_original_sha256"] and
            sha(canonical_verified) == fixture["canonical_verified_sha256"] and
            source_mutation(canonical_original, canonical_verified, mutation, matrix) ==
            (original, verified)
        )
    else:
        profile_path = case_dir / "mutation-profile.json"
        record_path = case_dir / "mutation-record.json"
        mir_files = tuple(case_dir / name for name in (
            "canonical-mir.txt", "mutated-mir.txt",
            "canonical-mir.bin", "mutated-mir.bin"))
        if profile_path.exists() and record_path.exists() and \
                all(path.exists() for path in mir_files):
            profile = json.loads(profile_path.read_text())
            mutation_record = json.loads(record_path.read_text())
            canonical_text = (case_dir / "canonical-mir.txt").read_text()
            mutated_text = (case_dir / "mutated-mir.txt").read_text()
            canonical_bin = (case_dir / "canonical-mir.bin").read_bytes()
            mutated_bin = (case_dir / "mutated-mir.bin").read_bytes()
            mir_exact = (
                mutation_record.get("matched") is True and
                mutation_record.get("mutation") == mutation and
                mutation_record.get("exporter_exit") == 0 and
                mutation_record.get("decode_exit") == 0 and
                mutation_record.get("encode_exit") == 0 and
                mutation_record.get("canonical_sha256") == sha(canonical_bin) and
                mutation_record.get("mutated_sha256") == sha(mutated_bin) and
                canonical_bin != mutated_bin and
                mutation_record.get("selected_source_sha256") == sha(verified) and
                mutation_record.get("real_exporter_sha256") == profile.get("real_exporter_sha256") and
                profile.get("base_console_sha256") == profile.get("shadow_console_sha256") and
                profile.get("wrapper_sha256") == sha(
                    (case_dir / "mutation-profile/bin/vf-rust-mir-exporter").read_bytes()) and
                mutate_as_mut_ptr_mir(canonical_text, mutation, matrix) == mutated_text
            )
    admission_evidence = {
        "source_exact": matrix.strip_ghost_annotations(verified) == original,
        "stage_integrity": set(stage) == {"exporter", "decode", "verifast", "refinement"} and
            all(value.get("unchanged") is True for value in stage.values()),
        "frontend_refinement": runner_result.get("exporter_exit") == 0 and
            runner_result.get("decode_exit") == 0 and runner_result.get("refinement_exit") == 0,
        "mutant_exact": source_exact if kind == "source" else mir_exact,
        "exact_fatal": exact_fatal,
        "before_proof": not re.search(r"Verifying function 'sort4_checked_as_mut_ptr'", log) and
            not re.search(r"Verifying function 'sort4_as_mut_ptr_", log) and CERT_MARKER not in log,
        "verifier_exit_two": runner_result.get("verifast_exit") == 2,
    }
    passed = strict_admission_evidence(admission_evidence)
    result = {
        "kind": kind,
        "mutation": mutation,
        "classification": "INTENDED_ADMISSION_REJECTION" if passed else "INCONCLUSIVE",
        "expected_stage": "verifier certificate before proof",
        "expected_predicate": reason,
        "exact_fatal": exact_fatal,
        "frontend_and_refinement_pass": frontend,
        "source_mutation_exact": source_exact,
        "mir_mutation_exact": mir_exact,
        "mutation_record": mutation_record,
        "accepted_component": False,
        "admission_evidence": admission_evidence,
        "runner_result": runner_result,
    }
    (case_dir / "admission-classification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def run_admission_matrix(evidence: Path, specialized: bytes, certificate: dict,
                         matrix, args: argparse.Namespace, repo_root: Path) -> list[dict]:
    results = []
    for mutation in SOURCE_MUTATIONS:
        case_dir = evidence / ("source_" + mutation)
        make_case(case_dir, specialized, certificate, matrix, "unknown", admission=mutation)
        runner_result = matrix.run_case(
            case_dir, args.schema, args.tool_home, args.compiler_sysroot, repo_root,
            "source_" + mutation, "diagnostic", certificate_mode=True)
        result = admission_classification(case_dir, runner_result,
                                          "source", mutation, matrix)
        results.append(result)
        if result["classification"] != "INTENDED_ADMISSION_REJECTION":
            return results
    for mutation in MIR_MUTATIONS:
        case_dir = evidence / ("mir_" + mutation)
        make_case(case_dir, specialized, certificate, matrix, "unknown")
        shadow = make_mir_mutation_tool_home(args.tool_home, args.schema,
                                            repo_root, case_dir, mutation)
        runner_result = matrix.run_case(
            case_dir, args.schema, shadow, args.compiler_sysroot, repo_root,
            "mir_" + mutation, "diagnostic", certificate_mode=True)
        result = admission_classification(case_dir, runner_result,
                                          "mir", mutation, matrix)
        results.append(result)
        if result["classification"] != "INTENDED_ADMISSION_REJECTION":
            return results
    return results


def classify(case_dir: Path, runner_result: dict, certificate: dict,
             variant: str, prerequisite_positive: bool) -> dict:
    mir = (case_dir / "compiler-mir.txt").read_text(errors="replace")
    log = (case_dir / "verifast.log").read_text(errors="replace")
    verified = (case_dir / "verified/lib.rs").read_bytes()
    original = (case_dir / "original/lib.rs").read_bytes()
    fixture = json.loads((case_dir / "fixture.json").read_text())
    helper_log = function_log(log, HELPER_NAME)
    probe_log = function_log(log, probe_name(variant))
    stripped = re.sub(rb"/\*@.*?@\*/", b"", verified, flags=re.S)
    stripped = re.sub(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)", b"", stripped)
    stage_integrity = runner_result.get("stage_integrity", {})
    integrity = set(stage_integrity) == {"exporter", "decode", "verifast", "refinement"} and \
        all(item.get("unchanged") is True for item in stage_integrity.values())
    source_exact = certificate["source_body_exact"] and verified != original and \
        original == stripped
    frontend_refinement = runner_result.get("exporter_exit") == 0 and \
        runner_result.get("decode_exit") == 0 and \
        runner_result.get("refinement_exit") == 0
    typed_mir_identity = mir.count(f'defPath = "{HELPER_NAME}"') == 1 and \
        mir.count(f'defPath = "{probe_name(variant)}"') == 1
    frontend_ok = source_exact and frontend_refinement and integrity and typed_mir_identity
    certificate_seen = log.count(CERT_MARKER) == 1 and \
        log.count("SORT4-AS-MUT-PTR: certified SAFE local body " + HELPER_NAME) == 1
    helper_checked = (
        frontend_ok and certificate_seen and
        f"Function '{HELPER_NAME}': Function prototype implementation check" in log and
        "Executing return statement" in helper_log and "Leak check." in helper_log and
        not any(": error:" in line for line in helper_log.splitlines())
    )
    errors = [line for line in log.splitlines() if ": error:" in line]
    first_error = errors[0] if errors else None
    error_line_match = re.search(r"verified/lib\.rs\((\d+),", first_error or "")
    error_line = int(error_line_match.group(1)) if error_line_match else None
    entered_probe = bool(probe_log)
    marker_line = fixture["target_assertion_line"] if variant == "assert_false" else \
        fixture["target_postcondition_line"]
    if variant == "lost_cell":
        target_location = error_line == fixture["probe_return_line"] + 1
        target_message = bool(first_error and re.search(
            r"Function leaks heap chunks: points_to<std::mem::MaybeUninit<\*Element>>"
            r"\(storage, value\)$", first_error))
    else:
        target_location = isinstance(marker_line, int) and error_line in {
            marker_line + 1, fixture["probe_return_line"]}
        expected = {
            "wrong_result": r"Cannot prove condition\. \(Cannot prove !\(result0 = storage\)\.\)$",
            "false_post": r"Cannot prove condition\. \(Cannot prove false\.\)$",
            "assert_false": r"Assertion might not hold\. \(Cannot prove false\.\)$",
            "duplicate_frame":
                r"No matching heap chunks: \[f\]points_to<u8>\(frame, frame_value\)$",
        }.get(variant)
        target_message = bool(first_error and (
            matches_invent_initialized_error(first_error)
            if variant == "invent_initialized" else
            expected and re.search(expected, first_error)))
    if variant == "assert_false":
        target_location = isinstance(fixture["target_assertion_line"], int) and \
            error_line == fixture["target_assertion_line"] + 1
    shared_evidence = {
        "source_exact": bool(source_exact),
        "stage_integrity": bool(integrity),
        "frontend_refinement": bool(frontend_refinement),
        "typed_mir_identity": bool(typed_mir_identity),
        "certificate_marker": bool(certificate_seen),
        "safe_prototype":
            f"Function '{HELPER_NAME}': Function prototype implementation check" in log,
        "helper_body_return_leak":
            "Executing return statement" in helper_log and "Leak check." in helper_log and
            not any(": error:" in line for line in helper_log.splitlines()),
    }
    positive_evidence = {
        **shared_evidence,
        "probe_body_return_leak": entered_probe and
            "Executing return statement" in probe_log and "Leak check." in probe_log,
        "verifier_success": runner_result.get("verifast_exit") == 0,
    }
    negative_evidence = {
        **shared_evidence,
        "positive_prerequisite": prerequisite_positive,
        "named_probe_entered": entered_probe and first_error is not None and
            first_error in probe_log,
        "single_verifier_error": runner_result.get("verifast_exit") == 1 and len(errors) == 1,
        "target_location": bool(target_location),
        "target_message": bool(target_message),
        "leak_return_location": variant != "lost_cell" or
            error_line == fixture["probe_return_line"] + 1,
    }
    positive_pass = variant in POSITIVES and strict_positive_evidence(positive_evidence)
    intended_negative = variant in NEGATIVES and strict_negative_evidence(negative_evidence)
    result = {
        "classification": (
            "DIAGNOSTIC_POSITIVE" if positive_pass else
            "INTENDED_PROOF_REJECTION" if intended_negative else "INCONCLUSIVE"
        ),
        "accepted_component": False,
        "full_select_proved": False,
        "tool_profile": PROFILE,
        "source_certificate": certificate,
        "runner_result": runner_result,
        "full_helper_mir_identity_count": mir.count(f'defPath = "{HELPER_NAME}"'),
        "full_probe_mir_identity_count": mir.count(f'defPath = "{probe_name(variant)}"'),
        "helper_entered": bool(helper_log),
        "helper_checked": helper_checked,
        "full_typed_as_mut_ptr_certificate_seen": certificate_seen,
        "helper_return_seen": "Executing return statement" in helper_log,
        "helper_leak_check_seen": "Leak check." in helper_log,
        "frame_probe_entered": entered_probe,
        "frame_probe_return_seen": "Executing return statement" in probe_log,
        "frame_probe_leak_check_seen": "Leak check." in probe_log,
        "first_verifier_error": first_error,
        "first_verifier_error_line": error_line,
        "intended_negative_location": target_location if variant in NEGATIVES else None,
        "intended_negative_message": target_message if variant in NEGATIVES else None,
        "positive_prerequisite_passed": prerequisite_positive,
        "stage_source_integrity": integrity,
        "positive_evidence": positive_evidence,
        "negative_evidence": negative_evidence,
    }
    (case_dir / "diagnostic-classification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def check_select(args: argparse.Namespace) -> dict:
    if os.environ.get("GITHUB_ACTIONS") != "true" or \
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \
            os.environ.get("RUNNER_OS") != "Linux":
        raise SystemExit("as_mut_ptr diagnostic requires GitHub-hosted Linux Actions")
    repo_root = Path(__file__).resolve().parents[3]
    matrix = load_matrix(repo_root)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    specialized, certificate = source_certificate(repo_root, matrix)
    (evidence / "source-certificate.json").write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    constructor = json.loads(args.constructor_summary.read_text())
    classifier = json.loads(args.classifier_summary.read_text())
    prerequisites = {
        "constructor_acceptance": constructor.get("constructor_acceptance") is True,
        "classifier_self_check": classifier.get("pass") is True,
        "classifier_mutants": classifier.get("mutant_count") == 58,
    }
    if not all(prerequisites.values()):
        summary = {
            "classification": "INCONCLUSIVE",
            "accepted_component": False,
            "full_select_proved": False,
            "tool_profile": PROFILE,
            "prerequisites": prerequisites,
            "cases": [],
            "admission_cases": [],
        }
        (evidence / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        return summary
    results = []
    for variant in VARIANTS:
        prerequisite_positive = bool(results) and all(
            item["classification"] == "DIAGNOSTIC_POSITIVE" for item in results
            if item["variant"] in POSITIVES)
        if variant in NEGATIVES and not prerequisite_positive:
            break
        case_dir = evidence / ("as_mut_ptr_" + variant)
        make_case(case_dir, specialized, certificate, matrix, variant)
        runner_result = matrix.run_case(
            case_dir, args.schema, args.tool_home, args.compiler_sysroot, repo_root,
            "as_mut_ptr_" + variant, "diagnostic", certificate_mode=True)
        result = classify(case_dir, runner_result, certificate, variant,
                          prerequisite_positive)
        result["variant"] = variant
        results.append(result)
        if variant in POSITIVES and result["classification"] != "DIAGNOSTIC_POSITIVE":
            break
    base_pass = (
        len(results) == len(VARIANTS) and
        all(item["classification"] == "DIAGNOSTIC_POSITIVE" for item in results
            if item["variant"] in POSITIVES) and
        all(item["classification"] == "INTENDED_PROOF_REJECTION" for item in results
            if item["variant"] in NEGATIVES)
    )
    admission = run_admission_matrix(evidence, specialized, certificate, matrix,
                                     args, repo_root) if base_pass else []
    admission_pass = len(admission) == len(SOURCE_MUTATIONS) + len(MIR_MUTATIONS) and \
        all(item["classification"] == "INTENDED_ADMISSION_REJECTION" for item in admission)
    summary = {
        "classification": "COMPONENT_ACCEPTED" if base_pass and admission_pass else "INCONCLUSIVE",
        "accepted_component": bool(base_pass and admission_pass),
        "full_select_proved": False,
        "tool_profile": PROFILE,
        "prerequisites": prerequisites,
        "source_certificate": certificate,
        "cases": results,
        "cases_not_run": list(VARIANTS[len(results):]),
        "admission_cases": admission,
        "admission_cases_not_run": [
            "source_" + item for item in SOURCE_MUTATIONS
        ][sum(item["kind"] == "source" for item in admission):] + [
            "mir_" + item for item in MIR_MUTATIONS
        ][sum(item["kind"] == "mir" for item in admission):],
    }
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-home", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--constructor-summary", type=Path, required=True)
    parser.add_argument("--classifier-summary", type=Path, required=True)
    args = parser.parse_args()
    result = check_select(args)
    print(json.dumps({"classification": result["classification"],
                      "evidence": str(args.evidence.resolve())}))
    if not result["accepted_component"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
