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
import re
import shutil
import subprocess
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
CERT_PREFIX = "SORT4-ASSUME-INIT:"
REJECT_PREFIX = CERT_PREFIX + " certificate mismatch: "
SOURCE_MUTATIONS = ("identity", "body", "type")
MIR_MUTATIONS = ("field", "operand", "return", "type", "extra_operation")


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


def mutate_source(original: bytes, verified: bytes, mutation: str,
                  matrix) -> tuple[bytes, bytes, str]:
    """Source-side certificate controls with aligned runtime source files."""
    if mutation == "identity":
        old = b"sort4_checked_assume_init"
        require(original.count(old) == verified.count(old) == 1,
                "identity mutation target is not unique")
        new = old + b"_impostor"
        reason = "expected exactly one unsafe local adapter body"
    elif mutation == "body":
        old, new = b"storage.value", b"storage.uninit"
        require(original.count(old) == verified.count(old) == 1,
                "body mutation target is not unique")
        reason = "assume-init annotated body/source-copy mismatch"
    elif mutation == "type":
        old, new = b"-> *const Element", b"-> *mut Element"
        cast_old, cast_new = b"cast::<*const Element>()", b"cast::<*mut Element>()"
        require(original.count(old) == verified.count(old) == 1 and
                original.count(cast_old) == verified.count(cast_old) == 1,
                "type mutation target is not unique")
        original = original.replace(cast_old, cast_new, 1)
        verified = verified.replace(cast_old, cast_new, 1)
        reason = "assume-init unsafe contract/source signature"
    else:
        raise ValueError(f"unknown assume-init source mutation {mutation}")
    original = original.replace(old, new, 1)
    verified = verified.replace(old, new, 1)
    require(matrix.strip_ghost_annotations(verified) == original,
            "source mutant differs after ghost stripping")
    return original, verified, reason


def mutate_assume_mir(decoded: str, mutation: str, constructor) -> tuple[str, str]:
    """Mutate one typed MIR fact; the source bytes remain unchanged."""
    require(mutation in MIR_MUTATIONS, f"unknown assume-init MIR mutation {mutation}")
    marker = f'defPath = "{HELPER}"'
    require(decoded.count(marker) == 1, "assume-init MIR identity is not unique")
    start = decoded.index(marker)
    lead = decoded.rfind("    ( defKind =", 0, start)
    require(lead >= 0, "assume-init MIR body opener missing")
    opening = decoded.index("(", lead)
    body = constructor.mir_balanced_item(decoded, opening)
    end = opening + len(body)
    replace = constructor.replace_once
    if mutation == "field":
        body = replace(body, "index = 1,", "index = 0,", mutation)
        reason = "assume-init active union field/type"
    elif mutation == "operand":
        body = replace(body,
            'args = [\n                  ( move = (\n                      local = (name = "_4")',
            'args = [\n                  ( move = (\n                      local = (name = "_3")', mutation)
        reason = "assume-init call operand: _4"
    elif mutation == "return":
        body = replace(body,
            'destination = (\n                  local = (name = "_0")',
            'destination = (\n                  local = (name = "_1")', mutation)
        reason = "assume-init place: _0"
    elif mutation == "type":
        inputs_at = body.index("      inputs = [") + len("      inputs = [")
        inputs_end = body.index("      localDecls = [", inputs_at)
        inputs = body[inputs_at:inputs_end]
        inputs = replace(inputs, 'param = "Element"', 'param = "Mutant"', mutation)
        body = body[:inputs_at] + inputs + body[inputs_end:]
        reason = "assume-init input type/arity"
    else:
        statements = body.index("          statements = [")
        first = body.index("( sourceInfo = (", statements)
        item = constructor.mir_balanced_item(body, first)
        body = body[:first] + item + ",\n            " + body[first:]
        reason = "assume-init address ordered statements"
    require(body != decoded[opening:end], "MIR mutation had no effect")
    return decoded[:opening] + body + decoded[end:], reason


def make_mir_tool_home(tool_home: Path, schema: Path, repo: Path,
                       case: Path, mutation: str, matrix) -> Path:
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
spec = importlib.util.spec_from_file_location("assume_diag", @SCRIPT@)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
ctor_spec = importlib.util.spec_from_file_location("assume_ctor", @CTOR@)
ctor = importlib.util.module_from_spec(ctor_spec); ctor_spec.loader.exec_module(ctor)
real, schema, mutation, record = @REAL@, @SCHEMA@, @MUTATION@, Path(@RECORD@)
proc = subprocess.run([real, *sys.argv[1:]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
sys.stderr.buffer.write(proc.stderr)
if proc.returncode: sys.stdout.buffer.write(proc.stdout); raise SystemExit(proc.returncode)
dec = subprocess.run(["capnp", "decode", schema, "VfMir"], input=proc.stdout,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if dec.returncode: sys.stderr.buffer.write(dec.stderr); raise SystemExit(dec.returncode)
try:
    canonical = dec.stdout.decode(); changed, reason = module.mutate_assume_mir(canonical, mutation, ctor)
except Exception as exc:
    record.write_text(json.dumps({"mutation": mutation, "error": str(exc)}) + "\\n")
    sys.stderr.write("ASSUME-INIT MIR mutation failed: " + str(exc) + "\\n"); raise SystemExit(98)
enc = subprocess.run(["capnp", "encode", schema, "VfMir"], input=changed.encode(),
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if enc.returncode: sys.stderr.buffer.write(enc.stderr); raise SystemExit(enc.returncode)
record.parent.mkdir(parents=True, exist_ok=True)
(record.parent / "canonical-mir.txt").write_text(canonical)
(record.parent / "mutated-mir.txt").write_text(changed)
(record.parent / "canonical-mir.bin").write_bytes(proc.stdout)
(record.parent / "mutated-mir.bin").write_bytes(enc.stdout)
selected = next((Path(x) for x in sys.argv[1:] if x.endswith(".rs") and Path(x).is_file()), None)
record.write_text(json.dumps({"mutation": mutation, "reason": reason, "matched": True,
 "exporter_exit": proc.returncode, "decode_exit": dec.returncode, "encode_exit": enc.returncode,
 "canonical_sha256": hashlib.sha256(proc.stdout).hexdigest(),
 "mutated_sha256": hashlib.sha256(enc.stdout).hexdigest(),
 "selected_source_sha256": hashlib.sha256(selected.read_bytes()).hexdigest() if selected else None,
 "real_exporter_sha256": hashlib.sha256(Path(real).read_bytes()).hexdigest()},
 indent=2, sort_keys=True) + "\\n")
sys.stdout.buffer.write(enc.stdout)
'''.replace("@SCRIPT@", repr(str(Path(__file__).resolve())))
       .replace("@CTOR@", repr(str(repo / "research/challenge-8/check-maybeuninit-new-pointer.py")))
       .replace("@REAL@", repr(str(source_bin / "vf-rust-mir-exporter")))
       .replace("@SCHEMA@", repr(str(schema)))
       .replace("@MUTATION@", repr(mutation))
       .replace("@RECORD@", repr(str(case / "mutation-record.json"))))
    wrapper.chmod(0o755)
    shutil.copy2(wrapper, case / "mir-exporter-wrapper.py")
    (case / "mutation-profile.json").write_text(json.dumps({
        "mutation": mutation,
        "base_console_sha256": matrix.sha((source_bin / "verifast").read_bytes()),
        "shadow_console_sha256": matrix.sha((binary / "verifast").read_bytes()),
        "real_exporter_sha256": matrix.sha((source_bin / "vf-rust-mir-exporter").read_bytes()),
        "wrapper_sha256": matrix.sha(wrapper.read_bytes()),
    }, indent=2, sort_keys=True) + "\n")
    return shadow


def run_admission(case: Path, original: bytes, verified: bytes, metadata: dict,
                  mutation: str, mode: str, expected: tuple[str, ...], args,
                  repo: Path, matrix, constructor) -> dict:
    if mode == "source":
        original, verified, reason = mutate_source(original, verified, mutation, constructor)
        expected = (reason,)
        constructor.write_case(case, original, verified, {
            **metadata, "variant": f"assume_init_source_{mutation}",
            "admission_mode": "source", "admission_mutation": mutation,
        })
        tool_home = args.tool_home
    else:
        constructor.write_case(case, original, verified, {
            **metadata, "variant": f"assume_init_mir_{mutation}",
            "admission_mode": "mir", "admission_mutation": mutation,
        })
        tool_home = make_mir_tool_home(args.tool_home, args.schema, repo, case,
                                       mutation, matrix)
    runner = constructor.run_case(case, args.schema, tool_home,
                                  args.compiler_sysroot, repo,
                                  f"assume_init_{mode}_{mutation}",
                                  "diagnostic", certificate_mode=False)
    log = (case / "verifast.log").read_text(errors="replace")
    fatals = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    fatal_ok = len(fatals) == 1 and fatals[0] in {
        f'Fatal error: exception Failure("{REJECT_PREFIX}{why}")' for why in expected
    } and not any(": error:" in line for line in log.splitlines())
    stage = runner.get("stage_integrity", {})
    stage_ok = set(stage) == {"exporter", "decode", "verifast", "refinement"} and all(
        x.get("unchanged") is True for x in stage.values())
    frontend_ok = runner.get("exporter_exit") == 0 and runner.get("decode_exit") == 0 and \
        runner.get("refinement_exit") == 0
    mutant_ok = False
    record = None
    if mode == "source":
        mutant_ok = constructor.strip_ghost_annotations(verified) == original
    else:
        record_path = case / "mutation-record.json"
        if record_path.exists():
            record = json.loads(record_path.read_text())
            files = [case / n for n in ("canonical-mir.txt", "mutated-mir.txt",
                                         "canonical-mir.bin", "mutated-mir.bin")]
            profile_path = case / "mutation-profile.json"
            if all(x.exists() for x in files) and profile_path.exists():
                profile = json.loads(profile_path.read_text())
                canonical_bin, mutated_bin = files[2].read_bytes(), files[3].read_bytes()
                try:
                    exact = mutate_assume_mir(files[0].read_text(), mutation,
                                              constructor)[0] == files[1].read_text()
                except (ValueError, KeyError):
                    exact = False
                mutant_ok = exact and record.get("matched") is True and \
                    record.get("mutation") == mutation and \
                    record.get("exporter_exit") == record.get("decode_exit") == \
                    record.get("encode_exit") == 0 and \
                    record.get("canonical_sha256") == matrix.sha(canonical_bin) and \
                    record.get("mutated_sha256") == matrix.sha(mutated_bin) and \
                    canonical_bin != mutated_bin and \
                    record.get("selected_source_sha256") == matrix.sha(verified) and \
                    profile.get("base_console_sha256") == profile.get("shadow_console_sha256") and \
                    profile.get("wrapper_sha256") == matrix.sha(
                        (case / "mutation-profile/bin/vf-rust-mir-exporter").read_bytes())
    no_proof = "SORT4-ASSUME-INIT: full typed method MIR graph accepted" not in log and \
        f"Verifying function '{HELPER}'" not in log
    classification = "INTENDED_ADMISSION_REJECTION" if all((
        fatal_ok, stage_ok, frontend_ok, mutant_ok, no_proof,
        runner.get("verifast_exit") == 2)) else "INCONCLUSIVE"
    result = {
        "classification": classification, "accepted_component": False,
        "mode": mode, "mutation": mutation, "expected_reasons": expected,
        "fatal": fatals, "stage_integrity_ok": stage_ok,
        "frontend_refinement_ok": frontend_ok, "mutant_integrity_ok": mutant_ok,
        "before_proof": no_proof, "runner_result": runner,
        "mutation_record": record,
    }
    (case / "admission-classification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def classify_positive(log: str, runner: dict) -> dict:
    markers = (
        "SORT4-ASSUME-INIT: certified source-linked unsafe body",
        "SORT4-ASSUME-INIT: full typed method MIR graph accepted",
        "SORT4-ASSUME-INIT: modeled full union field address",
        "SORT4-ASSUME-INIT: modeled typed pointer read",
    )
    error_lines = [line for line in log.splitlines() if ": error:" in line]
    last_fn = re.findall(r"Verifying function '([^']+)'", log)
    read_source_note = "Executing call" in log and "read" in log and HELPER in log
    causal = bool(error_lines) and last_fn and last_fn[-1] == HELPER and \
        all(marker in log for marker in markers) and read_source_note and \
        "union_variant_ptr" in log and "No matching heap chunk" in log
    source_ok = set(runner.get("stage_integrity", {})) == {
        "exporter", "decode", "verifast", "refinement"} and all(
            x.get("unchanged") is True for x in runner.get("stage_integrity", {}).values())
    return {
        "classification": "TARGETED_READ_PERMISSION_DIAGNOSTIC" if causal and source_ok
            else "INCONCLUSIVE",
        "accepted_component": False, "full_select_proved": False,
        "source_integrity": source_ok,
        "source_linked_body_and_graph_markers": all(m in log for m in markers),
        "last_function": last_fn[-1] if last_fn else None,
        "read_source_note": read_source_note,
        "exact_union_chunk_failure": "union_variant_ptr" in log and
            "No matching heap chunk" in log,
        "first_error": error_lines[0] if error_lines else None,
    }


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
    errors = [line for line in log.splitlines() if ": error:" in line or "Fatal error:" in line or line.startswith(("error:", "error["))]
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
