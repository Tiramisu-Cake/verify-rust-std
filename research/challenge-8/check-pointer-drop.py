#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted, source-linked S6 check of one raw-pointer drop method specialization.

Acceptance covers the checked method adapter and the exact compiler drop-glue
rule for a stored ``*const Element``. It does not establish the whole SmallSort
helper, a general Drop implementation, or ownership of Element.
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


PROFILE = "experimental-source-linked-select-pointer-drop-v4"
HELPER = "sort4_checked_pointer_drop"
PREFIX = "SORT4-POINTER-DROP:"
FULL_MARKER = PREFIX + " full typed method MIR graph accepted"
REJECT_PREFIX = PREFIX + " certificate mismatch: "
MODELED_MARKER = PREFIX + " modeled typed pointer drop 1"
SIGNATURE = b"pub unsafe fn sort4_checked_pointer_drop<Element>(slot: *mut *const Element)"
CONTRACT = (
    b"req thread_token(?t) &*& t == currentThread &*& *slot |-> ?value;\n"
    b"ens thread_token(t) &*& *slot |-> value;\n"
    b"on_unwind_ens false;"
)
POSITIVES = ("initialized", "initialized_two_frames")
NEGATIVES = (
    "wrong_preserved", "false_post", "assert_false", "lost_cell",
    "duplicate_cell", "lost_thread", "duplicate_thread", "lost_frame",
    "duplicate_frame", "none_init", "unknown_init",
)
SOURCE_MUTATIONS = (
    "identity", "input_type", "output_type", "binding", "callee",
    "operand", "contract", "extra_operation",
)
MIR_MUTATIONS = (
    "identity", "input_type", "output_type", "binding", "callee",
    "operand", "destination", "result_type", "cfg_successor",
    "cfg_unwind", "extra_operation", "contract",
)
PIN_MUTATIONS = ("method_source_pin", "glue_source_pin")


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


def probe_name(variant: str) -> str:
    return f"sort4_pointer_drop_{variant}_probe"


def target_line(source: bytes, marker: bytes) -> int | None:
    return next((line for line, text in enumerate(source.splitlines(), 1)
                 if marker in text), None)


def helper_source(body: bytes, constructor) -> bytes:
    return SIGNATURE + b"\n" + constructor.ghost_block(CONTRACT) + body + b"\n"


def probe_source(variant: str, constructor) -> bytes:
    require(variant in POSITIVES + NEGATIVES, "unknown drop fixture")
    name = probe_name(variant).encode()
    initialized = variant not in {"none_init", "unknown_init"}
    cell = (b"*slot |-> ?value" if initialized else
            b"points_to_::<*const Element>(slot, none)" if variant == "none_init" else
            b"points_to_::<*const Element>(slot, ?state)")
    two_frames = variant == "initialized_two_frames"
    extra_pre = b" &*& [?g](*frame2 |-> ?frame2_value)" if two_frames else b""
    extra_post = b" &*& [g](*frame2 |-> frame2_value)" if two_frames else b""
    pre = (b"req thread_token(?t) &*& t == currentThread &*& " + cell +
           b" &*& [?f](*frame |-> ?frame_value)" + extra_pre + b";\n")
    resources = (b"thread_token(t) &*& " + cell.replace(b"?value", b"value")
                 .replace(b"?state", b"state") +
                 b" &*& [f](*frame |-> frame_value)" + extra_post)
    post = resources
    if variant == "wrong_preserved":
        post = (b"thread_token(t) &*& *slot |-> ?changed &*& "
                b"changed != value &*& "
                b"[f](*frame |-> frame_value)")
    elif variant == "false_post":
        post = b"false"
    elif variant == "lost_cell":
        post = b"thread_token(t) &*& [f](*frame |-> frame_value)"
    elif variant == "duplicate_cell":
        post += b" &*& *slot |-> value"
    elif variant == "lost_thread":
        post = b"*slot |-> value &*& [f](*frame |-> frame_value)"
    elif variant == "duplicate_thread":
        post += b" &*& thread_token(t)"
    elif variant == "lost_frame":
        post = b"thread_token(t) &*& *slot |-> value"
    elif variant == "duplicate_frame":
        post += b" &*& [f](*frame |-> frame_value)"
    contract = pre + b"// TARGET_POSTCONDITION\nens " + post + \
        b";\non_unwind_ens false;"
    body = b"{\n    // TARGET_CALL\n    unsafe { sort4_checked_pointer_drop(slot) };\n"
    if variant == "assert_false":
        body += b"    // TARGET_ASSERTION\n    //@ assert false;\n"
    body += b"}\n"
    return (b"pub unsafe fn " + name + b"<Element>(slot: *mut *const Element, "
            b"frame: *const u8" +
            (b", frame2: *const u16" if two_frames else b"") + b")\n" +
            constructor.ghost_block(contract) + body)


def source_mutation(original: bytes, verified: bytes, mutation: str,
                    constructor) -> tuple[bytes, bytes]:
    require(mutation in SOURCE_MUTATIONS, "unknown source mutation")
    def both(old: bytes, new: bytes) -> tuple[bytes, bytes]:
        require(original.count(old) == verified.count(old) == 1,
                f"source mutant {mutation} target not unique")
        return original.replace(old, new, 1), verified.replace(old, new, 1)
    if mutation == "identity":
        old = HELPER.encode()
        require(original.count(old) == verified.count(old) == 2,
                "identity mutant needs helper and call")
        result = original.replace(old, old + b"_impostor"), \
            verified.replace(old, old + b"_impostor")
    elif mutation == "input_type":
        old = SIGNATURE
        new = SIGNATURE.replace(b"slot: *mut *const Element",
                                b"slot: *mut *const u8")
        call = b"std::ptr::drop_in_place(slot)"
        replacement = b"std::ptr::drop_in_place(slot as *mut *const Element)"
        require(original.count(old) == verified.count(old) == 1,
                "input mutant helper signature is not unique")
        result = (original.replace(old, new, 1).replace(call, replacement, 1)
                  .replace(b"sort4_checked_pointer_drop(slot)",
                           b"sort4_checked_pointer_drop::<Element>(slot as *mut *const u8)", 1),
                  verified.replace(old, new, 1).replace(call, replacement, 1)
                  .replace(b"sort4_checked_pointer_drop(slot)",
                           b"sort4_checked_pointer_drop::<Element>(slot as *mut *const u8)", 1))
    elif mutation == "output_type":
        result = both(SIGNATURE + b"\n", SIGNATURE + b" -> ()\n")
    elif mutation == "binding":
        require(original.count(SIGNATURE) == verified.count(SIGNATURE) == 1,
                "binding mutant helper signature not unique")
        head_o, tail_o = original.split(SIGNATURE, 1)
        head_v, tail_v = verified.split(SIGNATURE, 1)
        result = (head_o + SIGNATURE.replace(b"slot", b"location") +
                  tail_o.replace(b"std::ptr::drop_in_place(slot)",
                                 b"std::ptr::drop_in_place(location)", 1),
                  head_v + SIGNATURE.replace(b"slot", b"location") +
                  tail_v.replace(b"std::ptr::drop_in_place(slot)",
                                 b"std::ptr::drop_in_place(location)", 1)
                  .replace(b"*slot |->", b"*location |->", 2))
    elif mutation == "callee":
        result = both(b"unsafe { std::ptr::drop_in_place(slot) }",
                      b"unsafe { std::ptr::read(slot); }")
    elif mutation == "operand":
        result = both(b"std::ptr::drop_in_place(slot)",
                      b"std::ptr::drop_in_place(core::ptr::null_mut::<*const Element>())")
    elif mutation == "contract":
        require(verified.count(b"on_unwind_ens false;") == 2,
                "expected helper and probe unwind contracts")
        result = original, verified.replace(b"on_unwind_ens false;",
                                            b"on_unwind_ens true;", 1)
    else:
        result = both(b"unsafe { std::ptr::drop_in_place(slot) }",
                      b"unsafe { let _ = slot; std::ptr::drop_in_place(slot) }")
    require(constructor.strip_ghost_annotations(result[1]) == result[0],
            "source mutation lost runtime equivalence")
    return result


def make_case(case: Path, variant: str, source_cert: dict, body: bytes,
              constructor, admission: str | None = None) -> None:
    helper = helper_source(body, constructor)
    caller = probe_source(variant, constructor)
    verified = helper + b"\n" + caller
    original = constructor.strip_ghost_annotations(verified)
    require(original.count(body) == 1 and
            verified.count(b"std::ptr::drop_in_place(slot)") == 1,
            "exact local method body/call is not unique")
    canonical = original, verified
    if admission is not None:
        original, verified = source_mutation(original, verified, admission,
                                              constructor)
    case.mkdir(parents=True, exist_ok=False)
    constructor.write_case(case, original, verified, {
        **source_cert,
        "variant": variant,
        "source_mutation": admission,
        "tool_profile": PROFILE,
        "helper_name": HELPER,
        "probe_name": probe_name(variant),
        "target_call_line": target_line(verified, b"TARGET_CALL"),
        "target_postcondition_line": target_line(verified, b"TARGET_POSTCONDITION"),
        "target_assertion_line": target_line(verified, b"TARGET_ASSERTION"),
        "probe_return_line": len(verified.splitlines()),
        "canonical_original_sha256": sha(canonical[0]),
        "canonical_verified_sha256": sha(canonical[1]),
        "runtime_equal_after_ghost_strip": True,
        "full_select_proved": False,
    })
    if admission is not None:
        (case / "canonical").mkdir()
        (case / "canonical/original.lib.rs").write_bytes(canonical[0])
        (case / "canonical/verified.lib.rs").write_bytes(canonical[1])


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
        "typed_mir_identity", "full_certificate", "modeled_drop_call",
        "unsafe_body_entered", "helper_return_leak", "probe_return_leak",
        "identity_lemma_return_leak", "verifier_success",
    ))


def strict_negative_evidence(evidence: dict[str, bool]) -> bool:
    return all(evidence.get(field) is True for field in (
        "positive_prerequisite", "source_exact", "stage_integrity",
        "frontend_refinement", "typed_mir_identity", "full_certificate",
        "modeled_drop_call", "unsafe_body_entered", "helper_return_leak",
        "identity_lemma_return_leak", "probe_entered", "one_verifier_error", "target_location",
        "target_message",
    ))


def strict_admission_evidence(evidence: dict[str, bool]) -> bool:
    return all(evidence.get(field) is True for field in (
        "source_exact", "stage_integrity", "frontend_refinement",
        "mutant_exact", "exact_fatal", "before_proof", "verifier_exit_two",
    ))


SOURCE_REASONS = {
    "identity": ("expected one exact unsafe method and one listed probe",),
    "input_type": ("method source marker missing", "method HIR generic identity"),
    "output_type": ("method source marker missing", "method output type",
                    "method exported SAFE contract"),
    "binding": ("method source marker missing", "method debug binding"),
    "callee": ("method source body differs from pinned source",),
    "operand": ("method source body differs from pinned source",),
    "contract": ("method exported SAFE contract",),
    "extra_operation": ("method source body differs from pinned source",),
}
MIR_REASONS = {
    "identity": ("expected one exact unsafe method and one listed probe",),
    "input_type": ("method input type",),
    "output_type": ("method output type",),
    "binding": ("method debug binding",),
    "callee": ("method free drop-glue FnDef/type",),
    "operand": ("method call operand", "method place: _2"),
    "destination": ("method place: _0",),
    "result_type": ("method result local/type: _0",),
    "cfg_successor": ("method complete CFG", "method normal successor"),
    "cfg_unwind": ("method unwind action",),
    "extra_operation": ("method ordered statements",),
    "contract": ("method exported SAFE contract",),
}
PIN_REASONS = {
    "method_source_pin": ("pinned pointer method/lang-item source changed",),
    "glue_source_pin": ("pinned pointer method/lang-item source changed",),
}


def admission_reasons(mode: str, mutation: str) -> tuple[str, ...]:
    require(mode in {"source", "mir", "pin"}, "unknown admission mode")
    reasons = {"source": SOURCE_REASONS, "mir": MIR_REASONS,
               "pin": PIN_REASONS}[mode]
    require(mutation in reasons, "unknown admission mutation")
    return reasons[mutation]


def matches_admission_fatal(message: str, reasons: tuple[str, ...]) -> bool:
    return any(message == f'Fatal error: exception Failure("{REJECT_PREFIX}{reason}")'
               for reason in reasons)


def replace_once(source: str, old: str, new: str, mutation: str) -> str:
    require(source.count(old) == 1,
            f"{mutation}: expected one MIR target; found {source.count(old)}")
    return source.replace(old, new, 1)


def helper_mir_body(decoded: str, constructor) -> tuple[int, int, str]:
    marker = f'defPath = "{HELPER}"'
    require(decoded.count(marker) == 1, "checked method MIR body is not unique")
    at = decoded.index(marker)
    lead = decoded.rfind("    ( defKind =", 0, at)
    require(lead >= 0, "checked method MIR body opening missing")
    opening = decoded.index("(", lead)
    body = constructor.mir_balanced_item(decoded, opening)
    return opening, opening + len(body), body


def mutate_pointer_drop_mir(decoded: str, mutation: str, constructor) -> str:
    """Change exactly one decoded MIR field in the exact local method body.

    The canonical graph and reason strings must be confirmed by a hosted export.
    Any unobserved shape raises and leaves admission unaccepted.
    """
    require(mutation in MIR_MUTATIONS, "unknown direct MIR mutation")
    opening, tail, body = helper_mir_body(decoded, constructor)
    if mutation == "identity":
        body = replace_once(body, f'defPath = "{HELPER}"',
                            f'defPath = "{HELPER}_impostor"', mutation)
    elif mutation in {"input_type", "output_type", "result_type"}:
        if mutation == "input_type":
            first = body.index("      inputs = [")
            last = body.index("      localDecls = [", first)
        elif mutation == "output_type":
            body = replace_once(body, "output = (kind = (tuple = []))",
                                "output = (kind = (bool = void))", mutation)
            first = last = 0
        else:
            first = body.index("      localDecls = [")
            last = body.index("      basicBlocks = [", first)
        fragment = body[first:last]
        if mutation == "input_type":
            fragment = replace_once(fragment, 'param = "Element"',
                                    'param = "Mutant"', mutation)
        elif mutation == "result_type":
            first_local = fragment.index("( mutability =")
            local = constructor.mir_balanced_item(fragment, first_local)
            require('id = (name = "_0")' in local,
                    "result-type mutant expected result local _0 first")
            changed = replace_once(local, "ty = (kind = (tuple = []))",
                                   "ty = (kind = (bool = void))", mutation)
            fragment = fragment[:first_local] + changed + fragment[first_local + len(local):]
        if mutation != "output_type":
            body = body[:first] + fragment + body[last:]
    elif mutation == "binding":
        body = replace_once(body, 'name = "slot"', 'name = "location"', mutation)
    elif mutation == "contract":
        first = body.index("      contract = (")
        last = body.index("      inputs = [", first)
        fragment = body[first:last]
        require(fragment.count("thread_token") == 2,
                "contract mutant expected pre/post thread tokens")
        fragment = fragment.replace("thread_token", "thread_token_mutant", 1)
        body = body[:first] + fragment + body[last:]
    elif mutation == "extra_operation":
        first = body.index("statements = [") + len("statements = [")
        start = body.index("( sourceInfo = (", first)
        statement = constructor.mir_balanced_item(body, start)
        body = body[:start] + statement + ",\n            " + body[start:]
    else:
        call_tag = "call = ("
        require(body.count(call_tag) == 1, "method must have one call terminator")
        start = body.index(call_tag) + len("call = ")
        call = constructor.mir_balanced_item(body, start)
        if mutation == "callee":
            call = replace_once(call, 'name = "std::ptr::drop_in_place"',
                                'name = "std::ptr::read"', mutation)
        elif mutation == "operand":
            require('args = [' in call, "method call arguments missing")
            arguments = call[call.index('args = ['):]
            source = re.search(r'name = "(_\d+)"', arguments)
            require(source is not None, "method call operand local missing")
            old = source.group(0)
            new = f'name = "_{int(source.group(1)[1:]) + 1}"'
            call = replace_once(call, old, new, mutation)
        elif mutation == "destination":
            require("destination = (" in call, "method call destination missing")
            head, destination = call.split("destination = (", 1)
            target = re.search(r'name = "(_\d+)"', destination)
            require(target is not None, "method call destination local missing")
            destination = replace_once(
                destination, target.group(0),
                f'name = "_{int(target.group(1)[1:]) + 1}"', mutation)
            call = head + "destination = (" + destination
        elif mutation == "cfg_successor":
            target = re.search(r"target = \(something = \(index = (\d+)\)\)", call)
            require(target is not None, "method normal successor missing")
            call = replace_once(call, target.group(0),
                                f"target = (something = (index = {int(target.group(1)) + 1}))",
                                mutation)
        elif mutation == "cfg_unwind":
            tag = "unwindAction = ("
            require(call.count(tag) == 1, "method unwind action missing or repeated")
            action_at = call.index(tag) + len("unwindAction = ")
            action = constructor.mir_balanced_item(call, action_at)
            require("continue =" in action,
                    "method unwind action shape unknown")
            call = call[:action_at] + "(unreachable = void)" + \
                call[action_at + len(action):]
        body = body[:start] + call + body[start + len(
            constructor.mir_balanced_item(body, start)):]
    require(body != decoded[opening:tail], "direct MIR mutation had no effect")
    return decoded[:opening] + body + decoded[tail:]


def make_mir_mutation_tool_home(tool_home: Path, schema: Path, repo_root: Path,
                                case: Path, mutation: str) -> Path:
    shadow = case / "mutation-profile"
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
spec = importlib.util.spec_from_file_location("sort4_pointer_drop", @PREPARER@)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
constructor = module.load_script(Path(@CONSTRUCTOR@), "sort4_constructor_for_drop_mutant")
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
    changed = module.mutate_pointer_drop_mir(canonical, mutation, constructor)
except Exception as exc:
    record.write_text(json.dumps({"mutation": mutation, "error": str(exc)}) + "\\n")
    sys.stderr.write("SORT4-POINTER-DROP MIR mutant failed: " + str(exc) + "\\n")
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
'''.replace("@PREPARER@", repr(str(repo_root / "research/challenge-8/check-pointer-drop.py")))
   .replace("@CONSTRUCTOR@", repr(str(repo_root / "research/challenge-8/check-maybeuninit-new-pointer.py")))
   .replace("@REAL@", repr(str(source_bin / "vf-rust-mir-exporter")))
   .replace("@SCHEMA@", repr(str(schema)))
   .replace("@MUTATION@", repr(mutation))
   .replace("@RECORD@", repr(str(case / "mutation-record.json"))))
    wrapper.chmod(0o755)
    shutil.copy2(wrapper, case / "mir-exporter-wrapper.py")
    (case / "mutation-profile.json").write_text(json.dumps({
        "mutation": mutation,
        "base_console_sha256": sha((source_bin / "verifast").read_bytes()),
        "shadow_console_sha256": sha((binary / "verifast").read_bytes()),
        "real_exporter_sha256": sha((source_bin / "vf-rust-mir-exporter").read_bytes()),
        "wrapper_sha256": sha(wrapper.read_bytes()),
    }, indent=2, sort_keys=True) + "\n")
    return shadow


def stage_evidence(runner: dict) -> tuple[bool, bool]:
    stage = runner.get("stage_integrity", {})
    integrity = set(stage) == {"exporter", "decode", "verifast", "refinement"} and \
        all(item.get("unchanged") is True for item in stage.values())
    frontend = runner.get("exporter_exit") == 0 and \
        runner.get("decode_exit") == 0 and runner.get("refinement_exit") == 0
    return bool(integrity), bool(frontend)


def pin_root(case: Path, repo_root: Path, mutation: str) -> Path:
    """Shadow only the two certified std files, with one exact pin mutant."""
    require(mutation in PIN_MUTATIONS, "unknown source pin mutant")
    shadow = case / "source-pin-root/library/core/src/ptr"
    shadow.mkdir(parents=True)
    for name in ("mut_ptr.rs", "mod.rs"):
        original = (repo_root / "library/core/src/ptr" / name).read_bytes()
        changed = original + b"\n// SORT4-POINTER-DROP source pin mutant\n" if (
            name == ("mut_ptr.rs" if mutation == "method_source_pin"
                     else "mod.rs")) else original
        (shadow / name).write_bytes(changed)
    return case / "source-pin-root"


def classify_admission(case: Path, runner: dict, mutation: str, mode: str,
                       constructor) -> dict:
    verified = (case / "verified/lib.rs").read_bytes()
    original = (case / "original/lib.rs").read_bytes()
    fixture = json.loads((case / "fixture.json").read_text())
    log = (case / "verifast.log").read_text(errors="replace")
    fatal = [line for line in log.splitlines() if "Fatal error:" in line]
    reasons = admission_reasons(mode, mutation)
    exact_fatal = len(fatal) == 1 and \
        not any(": error:" in line for line in log.splitlines()) and \
        matches_admission_fatal(fatal[0], reasons)
    integrity, frontend = stage_evidence(runner)
    source_exact = constructor.strip_ghost_annotations(verified) == original and \
        sha(original) == fixture.get("original_sha256") and \
        sha(verified) == fixture.get("verified_sha256")
    record = None
    mutant_exact = False
    if mode == "source":
        canonical_original = (case / "canonical/original.lib.rs").read_bytes()
        canonical_verified = (case / "canonical/verified.lib.rs").read_bytes()
        mutant_exact = (
            sha(canonical_original) == fixture["canonical_original_sha256"] and
            sha(canonical_verified) == fixture["canonical_verified_sha256"] and
            source_mutation(canonical_original, canonical_verified, mutation,
                            constructor) == (original, verified)
        )
    elif mode == "pin":
        root = case / "source-pin-root/library/core/src/ptr"
        selected = "mut_ptr.rs" if mutation == "method_source_pin" else "mod.rs"
        repo = Path(__file__).resolve().parents[2]
        expected = (repo / "library/core/src/ptr" / selected).read_bytes() + \
            b"\n// SORT4-POINTER-DROP source pin mutant\n"
        other = "mod.rs" if selected == "mut_ptr.rs" else "mut_ptr.rs"
        mutant_exact = (root / selected).read_bytes() == expected and \
            (root / other).read_bytes() == \
            (repo / "library/core/src/ptr" / other).read_bytes()
    else:
        record_path = case / "mutation-record.json"
        profile_path = case / "mutation-profile.json"
        files = tuple(case / name for name in (
            "canonical-mir.txt", "mutated-mir.txt",
            "canonical-mir.bin", "mutated-mir.bin"))
        if record_path.exists() and profile_path.exists() and \
                all(path.exists() for path in files):
            record = json.loads(record_path.read_text())
            profile = json.loads(profile_path.read_text())
            canonical_text, mutated_text = files[0].read_text(), files[1].read_text()
            canonical_bin, mutated_bin = files[2].read_bytes(), files[3].read_bytes()
            try:
                exact_text = mutate_pointer_drop_mir(canonical_text, mutation,
                                                     constructor) == mutated_text
            except ValueError:
                exact_text = False
            mutant_exact = (
                exact_text and record.get("mutation") == mutation and
                record.get("matched") is True and
                record.get("exporter_exit") == 0 and
                record.get("decode_exit") == 0 and
                record.get("encode_exit") == 0 and
                record.get("canonical_sha256") == sha(canonical_bin) and
                record.get("mutated_sha256") == sha(mutated_bin) and
                canonical_bin != mutated_bin and
                record.get("selected_source_sha256") == sha(verified) and
                record.get("real_exporter_sha256") == profile.get("real_exporter_sha256") and
                profile.get("base_console_sha256") == profile.get("shadow_console_sha256") and
                profile.get("wrapper_sha256") == sha(
                    (case / "mutation-profile/bin/vf-rust-mir-exporter").read_bytes())
            )
    before_proof = FULL_MARKER not in log and \
        f"Verifying function '{HELPER}'" not in log and \
        f"Verifying function '{probe_name(POSITIVES[0])}'" not in log
    evidence = {
        "source_exact": source_exact,
        "stage_integrity": integrity,
        "frontend_refinement": frontend,
        "mutant_exact": bool(mutant_exact),
        "exact_fatal": bool(exact_fatal),
        "before_proof": bool(before_proof),
        "verifier_exit_two": runner.get("verifast_exit") == 2,
    }
    result = {
        "mutation": mutation,
        "mode": mode,
        "classification": "INTENDED_ADMISSION_REJECTION"
            if strict_admission_evidence(evidence) else "INCONCLUSIVE",
        "accepted_component": False,
        "expected_reasons": reasons,
        "fatal": fatal,
        "admission_evidence": evidence,
        "mutation_record": record,
        "runner_result": runner,
    }
    (case / "admission-classification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def error_line(message: str | None) -> int | None:
    match = re.search(r"verified/lib\.rs\((\d+),", message or "")
    return int(match.group(1)) if match else None


def matches_negative_message(variant: str, message: str | None) -> bool:
    if not message:
        return False
    patterns = {
        "wrong_preserved": (
            r"verified/lib\.rs\(\d+,\d+(?:-\d+(?:,\d+)?)?\): error: "
            r"Cannot prove condition\. \(Cannot prove !\(value = value\)\.\)$",
        ),
        "false_post": (r"Cannot prove condition\. \(Cannot prove false\.\)$",),
        "assert_false": (r"Assertion might not hold\. \(Cannot prove false\.\)$",),
        "lost_cell": (
            r"Function leaks heap chunks: points_to<\*Element>\(slot, value\)$",
        ),
        "duplicate_cell": (
            r"No matching heap chunks: points_to<\*Element>\(slot, value\)$",
        ),
        "lost_thread": (r"Function leaks heap chunks: thread_token\(t\)$",),
        "duplicate_thread": (
            r"No matching heap chunks: thread_token\(t\)$",
        ),
        "lost_frame": (
            r"Function leaks heap chunks: \[f\]points_to<u8>\(frame, frame_value\)$",
        ),
        "duplicate_frame": (
            r"No matching heap chunks: \[f\]points_to<u8>\(frame, frame_value\)$",
        ),
        "none_init": (
            r"prelude_core\.rsspec\(213,53-57\): error: Cannot prove that 'none' is not an instance of constructor 'none'$",
        ),
        "unknown_init": (
            r"prelude_core\.rsspec\(213,53-57\): error: Cannot prove that 'state' is not an instance of constructor 'none'$",
        ),
    }
    return any(re.search(pattern, message) for pattern in patterns[variant])


def classify_case(case: Path, runner: dict, variant: str,
                  constructor, prerequisite_positive: bool) -> dict:
    verified = (case / "verified/lib.rs").read_bytes()
    original = (case / "original/lib.rs").read_bytes()
    fixture = json.loads((case / "fixture.json").read_text())
    log = (case / "verifast.log").read_text(errors="replace")
    mir = (case / "compiler-mir.txt").read_text(errors="replace")
    helper_log = function_log(log, HELPER)
    probe_log = function_log(log, probe_name(variant))
    lemma_log = function_log(log, "std::ptr::pointer_drop_glue_identity")
    integrity, frontend = stage_evidence(runner)
    source_exact = constructor.strip_ghost_annotations(verified) == original and \
        verified != original and \
        sha(original) == fixture.get("original_sha256") and \
        sha(verified) == fixture.get("verified_sha256")
    mir_identity = mir.count(f'defPath = "{HELPER}"') == 1 and \
        mir.count(f'defPath = "{probe_name(variant)}"') == 1 and \
        mir.count('name = "std::ptr::drop_in_place"') == 1
    full_certificate = log.count(FULL_MARKER) == 1 and REJECT_PREFIX not in log
    modeled = log.count(MODELED_MARKER) == 1
    # Unsafe methods carry a user contract and are checked by entering their
    # body. The SAFE prototype marker is deliberately absent for this method.
    unsafe_body_entered = bool(helper_log)
    helper_return = "Executing return statement" in helper_log and \
        "Leak check." in helper_log and \
        not any(": error:" in line for line in helper_log.splitlines())
    lemma_proved = "Executing return statement" in lemma_log and \
        "Leak check." in lemma_log and \
        not any(": error:" in line for line in lemma_log.splitlines())
    probe_return = "Executing return statement" in probe_log and \
        "Leak check." in probe_log
    errors = [line for line in log.splitlines() if ": error:" in line]
    first = errors[0] if errors else None
    line = error_line(first)
    if variant in {"none_init", "unknown_init"}:
        location = bool(re.search(
            rf"verified/lib\.rs\({fixture['target_call_line'] + 1},\d+(?:-\d+)?\): note: Verifying call",
            log)) and bool(first and
                "prelude_core.rsspec(213,53-57): error:" in first) and \
            "verified/lib.rs(4,55-58): note: Consuming assertion" in log
    elif variant == "assert_false":
        location = line == fixture["target_assertion_line"] + 1
    elif variant in {"lost_cell", "lost_thread", "lost_frame"}:
        location = line == fixture["probe_return_line"]
    else:
        location = line in {fixture["target_postcondition_line"] + 1,
                            fixture["probe_return_line"]}
    shared = {
        "source_exact": bool(source_exact),
        "stage_integrity": integrity,
        "frontend_refinement": frontend,
        "typed_mir_identity": bool(mir_identity),
        "full_certificate": bool(full_certificate),
        "modeled_drop_call": bool(modeled),
        "unsafe_body_entered": unsafe_body_entered,
        "helper_return_leak": bool(helper_return),
        "identity_lemma_return_leak": bool(lemma_proved),
    }
    positive_evidence = {
        **shared,
        "probe_return_leak": bool(probe_return),
        "verifier_success": runner.get("verifast_exit") == 0,
    }
    negative_evidence = {
        **shared,
        "positive_prerequisite": prerequisite_positive,
        "probe_entered": bool(probe_log) and bool(first) and first in probe_log,
        "one_verifier_error": runner.get("verifast_exit") == 1 and len(errors) == 1,
        "target_location": bool(location),
        "target_message": matches_negative_message(variant, first)
            if variant in NEGATIVES else False,
    }
    positive_pass = variant in POSITIVES and strict_positive_evidence(positive_evidence)
    negative_pass = variant in NEGATIVES and strict_negative_evidence(negative_evidence)
    result = {
        "variant": variant,
        "classification": (
            "DIAGNOSTIC_POSITIVE" if positive_pass else
            "INTENDED_PROOF_REJECTION" if negative_pass else "INCONCLUSIVE"),
        "accepted_component": False,
        "tool_profile": PROFILE,
        "positive_evidence": positive_evidence,
        "negative_evidence": negative_evidence,
        "first_verifier_error": first,
        "first_verifier_error_line": line,
        "helper_entered": bool(helper_log),
        "identity_lemma_proved": bool(lemma_proved),
        "probe_entered": bool(probe_log),
        "runner_result": runner,
    }
    (case / "diagnostic-classification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def run_hosted_case(case: Path, args: argparse.Namespace, repo_root: Path,
                    constructor, tool_home: Path | None = None,
                    drop_root: Path | None = None) -> dict:
    previous = os.environ.get("SORT4_POINTER_DROP_REPO_ROOT")
    os.environ["SORT4_POINTER_DROP_REPO_ROOT"] = str(drop_root or repo_root)
    try:
        return constructor.run_case(
            case, args.schema, tool_home or args.tool_home,
            args.compiler_sysroot, repo_root,
            case.name, "diagnostic", certificate_mode=True)
    finally:
        if previous is None:
            os.environ.pop("SORT4_POINTER_DROP_REPO_ROOT", None)
        else:
            os.environ["SORT4_POINTER_DROP_REPO_ROOT"] = previous


def run_admissions(evidence: Path, cert: dict, body: bytes,
                   args: argparse.Namespace, repo_root: Path,
                   constructor) -> list[dict]:
    results = []
    for mode, mutations in (("source", SOURCE_MUTATIONS),
                            ("mir", MIR_MUTATIONS), ("pin", PIN_MUTATIONS)):
        for mutation in mutations:
            case = evidence / f"{mode}_{mutation}"
            try:
                make_case(case, POSITIVES[0], cert, body, constructor,
                          admission=mutation if mode == "source" else None)
                tool_home = args.tool_home if mode != "mir" else \
                    make_mir_mutation_tool_home(
                        args.tool_home, args.schema, repo_root, case, mutation)
                shadow = pin_root(case, repo_root, mutation) if mode == "pin" else None
                runner = run_hosted_case(case, args, repo_root, constructor,
                                         tool_home, shadow)
                result = classify_admission(case, runner, mutation, mode, constructor)
            except Exception as exc:
                case.mkdir(parents=True, exist_ok=True)
                result = {
                    "mode": mode, "mutation": mutation,
                    "classification": "INCONCLUSIVE", "accepted_component": False,
                    "harness_exception": f"{type(exc).__name__}: {exc}",
                }
                (case / "admission-classification.json").write_text(
                    json.dumps(result, indent=2, sort_keys=True) + "\n")
            results.append(result)
    return results


def check_pointer_drop(args: argparse.Namespace) -> dict:
    if os.environ.get("GITHUB_ACTIONS") != "true" or \
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \
            os.environ.get("RUNNER_OS") != "Linux":
        raise SystemExit("pointer drop checks require GitHub-hosted Linux Actions")
    repo_root = Path(__file__).resolve().parents[2]
    constructor = load_script(
        repo_root / "research/challenge-8/check-maybeuninit-new-pointer.py",
        "sort4_constructor_for_pointer_drop")
    diagnostic = load_script(
        repo_root / "research/challenge-8/prepare-pointer-drop-diagnostic.py",
        "sort4_pointer_drop_source_certificate")
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    body, source_cert = diagnostic.source_certificate(repo_root, constructor)
    cert = {
        **source_cert,
        "new_drop_rule_active": True,
        "activation_env": "SORT4_POINTER_DROP_REPO_ROOT",
        "compiler_glue_body_proved": False,
    }
    (evidence / "source-certificate.json").write_text(
        json.dumps(cert, indent=2, sort_keys=True) + "\n")
    ctor = json.loads(args.constructor_summary.read_text())
    asptr = json.loads(args.as_mut_ptr_summary.read_text())
    intrinsic = json.loads(args.intrinsic_summary.read_text())
    classifier = json.loads(args.classifier_summary.read_text())
    same_run = all(path.resolve().parents[1] == evidence.parent for path in (
        args.constructor_summary, args.as_mut_ptr_summary, args.intrinsic_summary)) and \
        args.classifier_summary.resolve().parent == evidence.parent
    prerequisites = {
        "constructor_accepted": ctor.get("constructor_acceptance") is True,
        "constructor_tool_home_matches": isinstance(ctor.get("tool_home"), str) and
            Path(ctor["tool_home"]).resolve() == args.tool_home.resolve(),
        "as_mut_ptr_accepted": asptr.get("accepted_component") is True and
            asptr.get("classification") == "COMPONENT_ACCEPTED",
        "intrinsic_accepted": intrinsic.get("accepted_component") is True and
            intrinsic.get("classification") == "COMPONENT_ACCEPTED",
        "same_run_evidence": same_run,
        "new_profile_selected": os.environ.get("SORT4_SELECT_PROFILE") == PROFILE,
        "as_mut_ptr_same_profile": asptr.get("tool_profile") == PROFILE,
        "intrinsic_same_profile": intrinsic.get("tool_profile") == PROFILE,
        "classifier_self_check": classifier.get("pass") is True and
            classifier.get("mutant_count") == 2 * (11 + 14 + 7) and
            classifier.get("message_mutant_count") == 12 and
            classifier.get("admission_message_mutant_count") == 4 and
            args.classifier_summary.resolve().parent == evidence.parent,
    }
    if not all(prerequisites.values()):
        result = {
            "classification": "INCONCLUSIVE", "accepted_component": False,
            "full_select_proved": False, "prerequisites": prerequisites,
            "cases": [], "admission_cases": [],
        }
        (evidence / "summary.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result
    results = []
    for variant in POSITIVES + NEGATIVES:
        positive_ready = any(item["classification"] == "DIAGNOSTIC_POSITIVE"
                             for item in results)
        case = evidence / f"pointer_drop_{variant}"
        try:
            make_case(case, variant, cert, body, constructor)
            runner = run_hosted_case(case, args, repo_root, constructor)
            result = classify_case(case, runner, variant, constructor, positive_ready)
        except Exception as exc:
            case.mkdir(parents=True, exist_ok=True)
            result = {"variant": variant, "classification": "INCONCLUSIVE",
                      "accepted_component": False,
                      "harness_exception": f"{type(exc).__name__}: {exc}"}
            (case / "diagnostic-classification.json").write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n")
        results.append(result)
    base_pass = len(results) == len(POSITIVES + NEGATIVES) and \
        all(item["classification"] == "DIAGNOSTIC_POSITIVE"
            for item in results if item["variant"] in POSITIVES) and \
        all(item["classification"] == "INTENDED_PROOF_REJECTION"
            for item in results if item["variant"] in NEGATIVES)
    admissions = run_admissions(evidence, cert, body, args, repo_root, constructor)
    admission_pass = len(admissions) == len(SOURCE_MUTATIONS + MIR_MUTATIONS + PIN_MUTATIONS) and \
        all(item["classification"] == "INTENDED_ADMISSION_REJECTION"
            for item in admissions)
    accepted = bool(base_pass and admission_pass and all(prerequisites.values()))
    result = {
        "classification": "COMPONENT_ACCEPTED" if accepted else "INCONCLUSIVE",
        "accepted_component": accepted,
        "full_select_proved": False,
        "tool_profile": PROFILE,
        "feasibility_only": False,
        "prerequisites": prerequisites,
        "source_certificate": cert,
        "cases": results,
        "cases_not_run": [variant for variant in POSITIVES + NEGATIVES
                          if not any(item["variant"] == variant for item in results)],
        "admission_cases": admissions,
        "admission_cases_not_run": [f"{mode}_{mutation}"
                                    for mode, mutations in (("source", SOURCE_MUTATIONS),
                                                            ("mir", MIR_MUTATIONS),
                                                            ("pin", PIN_MUTATIONS))
                                    for mutation in mutations
                                    if not any(item["mode"] == mode and
                                               item["mutation"] == mutation
                                               for item in admissions)],
    }
    (evidence / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--constructor-summary", type=Path, required=True)
    parser.add_argument("--as-mut-ptr-summary", type=Path, required=True)
    parser.add_argument("--intrinsic-summary", type=Path, required=True)
    parser.add_argument("--classifier-summary", type=Path, required=True)
    args = parser.parse_args()
    result = check_pointer_drop(args)
    print(json.dumps({"classification": result["classification"],
                      "cases_run": len(result["cases"]),
                      "evidence": str(args.evidence.resolve())}))
    if not result["accepted_component"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
