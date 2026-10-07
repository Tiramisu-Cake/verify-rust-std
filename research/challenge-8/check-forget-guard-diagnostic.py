#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted S7a diagnostic of the exact local guard's forget body.

This captures both exporter modes and focuses items defined in a separate
included block expression. It does not admit a caller summary or redirect forget.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


PROFILE = "experimental-source-linked-select-pointer-drop-v4"
PATCH_SHA = "c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1"
HINT_SHA = "d94ef86fbdac952fe7c9a6028536e15539b33dc188966fa4e9340fa7d94c30f8"
MEM_SHA = "1db195d24508e4eef81163672d008667765c2c121f4fa70f8752742e11106273"
MANUALLY_DROP_SHA = "17e8e41866d3eadcfdc6f1a516e4ed9dd5555e10ad725aac3b04aec7c759731b"
MAYBE_DANGLING_SHA = "1cf24b2ec36fff143f329f2ef6db5b4d47cfa798da7f30d88b554b712c8f4b53"
INCLUDE = (b'    use std::mem::ManuallyDrop;\n'
           b'    const _: () = include!("forget-items.rs");\n')
ANCHOR = b"    let true_ptr = true_val.as_mut_ptr();\n"
FORGET_SOURCE = b"pub const fn forget<T>(t: T) {\n    let _ = ManuallyDrop::new(t);\n}"
FORGET_BODY = b"{\n    let _ = ManuallyDrop::new(t);\n}"
HELPER = b"checked_forget_guard"
PROBE = b"checked_forget_guard_frame_probe"
VARIANTS = (
    "helper_positive", "frame_positive", "false_assert", "wrong_post",
    "thread_loss", "thread_duplication", "frame_loss", "frame_duplication",
    "frame_wrong_value",
)
EXPECT = {
    "helper_positive": ("helper", "body_return_leak"),
    "frame_positive": ("probe", "body_return_leak"),
    "false_assert": ("helper", "body_assertion"),
    "wrong_post": ("helper", "postcondition"),
    "thread_loss": ("helper", "leak"),
    "thread_duplication": ("helper", "postcondition"),
    "frame_loss": ("probe", "leak"),
    "frame_duplication": ("probe", "postcondition"),
    "frame_wrong_value": ("probe", "postcondition"),
}


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_certificate(repo: Path, constructor, prepare, drop_diag) -> dict:
    files = {
        "hint": repo / "library/core/src/hint.rs",
        "mem": repo / "library/core/src/mem/mod.rs",
        "manually_drop": repo / "library/core/src/mem/manually_drop.rs",
        "maybe_dangling": repo / "library/core/src/mem/maybe_dangling.rs",
    }
    expected = {"hint": HINT_SHA, "mem": MEM_SHA,
                "manually_drop": MANUALLY_DROP_SHA,
                "maybe_dangling": MAYBE_DANGLING_SHA}
    for name, path in files.items():
        require(sha(path.read_bytes()) == expected[name],
                f"pinned S7 source differs: {name}")
    hint = files["hint"].read_bytes()
    mem = files["mem"].read_bytes()
    require(mem.count(FORGET_SOURCE) == 1 and
            hint.count(b"struct DropOnPanic<T> {") == 1 and
            hint.count(b"impl<T> Drop for DropOnPanic<T> {") == 1 and
            hint.count(b"unsafe { self.inner.drop_in_place() }") == 1,
            "forget body or exact local guard/Drop source differs")
    return {"source_sha256": expected, "forget_body_sha256": sha(FORGET_BODY),
            "forget_body_exact": True,
            "local_guard_and_drop_source_pinned": True,
            "candidate_nominal_defpath": "select_unpredictable::DropOnPanic",
            "nominal_defpath_mir_confirmation": "pending full typed MIR capture",
            "runtime_actual_body_source":
                "unchanged except lexical import and one const-expression include"}


def ghost(constructor, pre: bytes, post: bytes) -> bytes:
    return constructor.ghost_block(
        b"req " + pre + b";\nens " + post + b";\non_unwind_ens false;")


def helper_file(variant: str, constructor, annotated: bool) -> bytes:
    pre = b"thread_token(?tid) &*& tid == currentThread"
    post = b"thread_token(tid)"
    if variant == "wrong_post":
        post = b"thread_token(tid) &*& false"
    elif variant == "thread_loss":
        post = b"true"
    elif variant == "thread_duplication":
        post = b"thread_token(tid) &*& thread_token(tid)"
    signature = (b"unsafe fn checked_forget_guard<Element>"
                 b"(t: DropOnPanic<*const Element>)\n")
    body = FORGET_BODY
    if variant == "false_assert" and annotated:
        body = body.replace(b"    let _ = ManuallyDrop::new(t);\n",
                            b"    let _ = ManuallyDrop::new(t);\n"
                            b"    //@ assert false;\n")
    contract = ghost(constructor, pre, post)
    scaffold = constructor.strip_ghost_annotations(contract)
    raw = (signature +
           (contract if annotated else scaffold) + body + b"\n")
    require((constructor.strip_ghost_annotations(raw) ==
             signature + scaffold + FORGET_BODY + b"\n"),
            "helper source changed beyond annotations")
    return raw


def probe_file(variant: str, constructor, annotated: bool) -> bytes:
    pre = (b"thread_token(?tid) &*& tid == currentThread &*& "
           b"*cell |-> ?value &*& *frame |-> ?flag")
    post = b"thread_token(tid) &*& *cell |-> value &*& *frame |-> flag"
    if variant == "frame_loss":
        post = b"thread_token(tid) &*& *cell |-> value"
    elif variant == "frame_duplication":
        post += b" &*& *frame |-> flag"
    elif variant == "frame_wrong_value":
        pre = (b"thread_token(?tid) &*& tid == currentThread &*& "
               b"*cell |-> ?value &*& *frame |-> false")
        post = b"thread_token(tid) &*& *cell |-> value &*& *frame |-> true"
    signature = (b"unsafe fn checked_forget_guard_frame_probe<Element>"
                 b"(cell: *mut *const Element, frame: *mut bool)\n")
    body = (b"{\n    let guard = DropOnPanic { inner: cell };\n"
            b"    unsafe { checked_forget_guard(guard); }\n}\n")
    contract = ghost(constructor, pre, post)
    scaffold = constructor.strip_ghost_annotations(contract)
    raw = signature + (contract if annotated else scaffold) + body
    require(constructor.strip_ghost_annotations(raw) ==
            signature + scaffold + body,
            "probe source changed beyond annotations")
    return raw


def items_file(variant: str, constructor, annotated: bool) -> bytes:
    """One included block expression with two items and a final unit value."""
    return (b"{\n" + helper_file(variant, constructor, annotated) +
            probe_file(variant, constructor, annotated) + b"()\n}\n")


def projected_base(evidence: Path, repo: Path, constructor,
                   prepare) -> tuple[Path, dict]:
    select = constructor.load_select_module(repo)
    prefix = evidence / "exact-select-prefix"
    select.prepare(repo / "library/core/src/hint.rs", prefix,
                   evidence / "select-prefix-integrity.json")
    extraction = json.loads((prefix / "extraction.json").read_text())
    original = (prefix / "original/lib.rs").read_bytes()
    verified = (prefix / "verified/lib.rs").read_bytes()
    insertions = (
        (b"    let false_ptr = false_val.as_mut_ptr();\n",
         prepare.PROJECTION_OPEN_GHOSTS),
        (b"        let guard = DropOnPanic { inner: guard };\n",
         prepare.PROJECTION_SPLIT_GHOST),
        (b"        drop.drop_in_place();\n",
         prepare.PROJECTION_CLOSE_GHOSTS),
    )
    for anchor, addition in insertions:
        require(verified.count(anchor) == 1, "v4 projected source anchor changed")
        verified = verified.replace(anchor, anchor + addition, 1)
    require(constructor.strip_ghost_annotations(verified) == original and
            sha(select.extract_body((repo / "library/core/src/hint.rs").read_bytes())) ==
                extraction["body_sha256"],
            "source-linked projected select changed runtime behavior")
    target = evidence / "projected-source-before-includes"
    (target / "original").mkdir(parents=True)
    (target / "verified").mkdir()
    (target / "original/lib.rs").write_bytes(original)
    (target / "verified/lib.rs").write_bytes(verified)
    return target, {"tool_profile": PROFILE,
                    "projected_original_sha256": sha(original),
                    "projected_verified_sha256": sha(verified),
                    "exact_select_body_sha256": extraction["body_sha256"],
                    "isolation": "omit unused appended component definitions; all admission routes inactive"}


def make_case(root: Path, base: Path, variant: str, fixture: dict,
              constructor) -> Path:
    require(variant in VARIANTS, "unknown S7a variant")
    case = root / variant
    shutil.copytree(base, case)
    original = (case / "original/lib.rs").read_bytes()
    verified = (case / "verified/lib.rs").read_bytes()
    require(original.count(ANCHOR) == verified.count(ANCHOR) == 1 and
            original.count(b"struct DropOnPanic<T> {") == 1 and
            verified.count(b"impl<T> Drop for DropOnPanic<T> {") == 1,
            "exact original local guard scope changed")
    (case / "original/lib.rs").write_bytes(original.replace(ANCHOR,
        INCLUDE + ANCHOR, 1))
    (case / "verified/lib.rs").write_bytes(verified.replace(ANCHOR,
        INCLUDE + ANCHOR, 1))
    for mode, annotated in (("original", False), ("verified", True)):
        (case / mode / "forget-items.rs").write_bytes(
            items_file(variant, constructor, annotated))
    original_files = {name: (case / "original" / name).read_bytes()
                      for name in ("lib.rs", "forget-items.rs")}
    verified_files = {name: (case / "verified" / name).read_bytes()
                      for name in original_files}
    require(all(constructor.strip_ghost_annotations(verified_files[name]) ==
                original_files[name] for name in original_files),
            "S7a source differs beyond ghost annotations")
    require(original_files["lib.rs"].replace(INCLUDE, b"", 1) ==
                (base / "original/lib.rs").read_bytes() and
            verified_files["lib.rs"].replace(INCLUDE, b"", 1) ==
                (base / "verified/lib.rs").read_bytes(),
            "S7a changed actual body beyond lexical import and const include")
    focus_kind, obligation = EXPECT[variant]
    focus_file = "forget-items.rs"
    focus_name = HELPER if focus_kind == "helper" else PROBE
    lines = verified_files[focus_file].splitlines()
    helper_lines = [i for i, data in enumerate(lines, 1)
                    if data.startswith(b"unsafe fn " + HELPER + b"<")]
    probe_lines = [i for i, data in enumerate(lines, 1)
                   if data.startswith(b"unsafe fn " + PROBE + b"<")]
    require(len(helper_lines) == len(probe_lines) == 1 and
            helper_lines[0] < probe_lines[0] and lines[0] == b"{" and
            lines[-2:] == [b"()", b"}"],
            "exact expression item order or unit result changed")
    line = helper_lines[0] if focus_kind == "helper" else probe_lines[0]
    end_line = next((i for i, data in enumerate(lines, 1)
                     if i > line and data == b"}"), None)
    require(end_line is not None and
            (focus_kind != "helper" or end_line < probe_lines[0]) and
            (focus_kind != "probe" or end_line < len(lines) - 1),
            "focused function closing brace changed")
    target_lines = [(i, data) for i, data in enumerate(lines, 1)
                    if line <= i <= end_line]
    assertion_line = next((i for i, data in target_lines
                           if b"//@ assert false;" in data), None)
    post_line = next((i for i, data in target_lines
                      if data.startswith(b"ens ")), None)
    error_line = (assertion_line if obligation == "body_assertion" else
                  end_line if obligation == "leak" else
                  post_line if obligation == "postcondition" else None)
    require(post_line is not None and
            (obligation == "body_return_leak" or error_line is not None),
            "expected diagnostic source position missing")
    manifest = {
        **fixture, "variant": variant, "classification": "DIAGNOSTIC_ONLY",
        "accepted_component": False, "full_select_proved": False,
        "source_insertion": {"anchor": ANCHOR.decode(),
            "exact_items": [item.decode().strip() for item in INCLUDE.splitlines()],
            "included_expression": "one block with helper, probe and final unit",
            "actual_body_unchanged_after_removing_items": True},
        "source_sha256": {mode: {name: sha((case / mode / name).read_bytes())
                            for name in original_files}
                          for mode in ("original", "verified")},
        "focus": {"file": "verified/" + focus_file, "line": line,
                  "function": focus_name.decode(), "obligation": obligation,
                  "expected_error_line": error_line,
                  "assertion_line": assertion_line, "post_line": post_line,
                  "function_end_line": end_line},
        "v4_admission_active": False,
        "source_match_not_yet_mir_certified": True,
        "satisfiable_pre_witness":
            "tid=currentThread; independent cell/frame addresses for probe",
    }
    (case / "fixture.json").write_text(json.dumps(manifest, indent=2,
        sort_keys=True) + "\n")
    return case


def run_case(case: Path, args, constructor) -> dict:
    fixture = json.loads((case / "fixture.json").read_text())
    paths = tuple(case / mode / name for mode in ("original", "verified")
                  for name in ("lib.rs", "forget-items.rs"))
    env = os.environ.copy()
    for key in ("SORT4_MAYBEUNINIT_REPO_ROOT",
                "SORT4_SELECT_INTRINSIC_REPO_ROOT", "SORT4_POINTER_DROP_REPO_ROOT"):
        env.pop(key, None)
    env["PATH"] = str(args.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    stages = {}

    def stage(label: str, argv: list[str], output: str,
              stderr: str | None = None, stdin_path: str | None = None) -> int:
        before = constructor.file_hashes(paths, case)
        if stdin_path is None:
            status = constructor.run_stage(
                argv, case, case / (label + "-resources.txt"), case / output,
                case / stderr if stderr else None, env)
        else:
            with (case / stdin_path).open("rb") as source, \
                    (case / output).open("wb") as result, \
                    (case / stderr).open("wb") as error:
                status = subprocess.run(
                    ["/usr/bin/time", "-v", "-o",
                     str(case / (label + "-resources.txt")),
                     "timeout", "--signal=TERM", "--kill-after=10s", "300s",
                     *argv], cwd=case, stdin=source, stdout=result,
                    stderr=error, check=False, env=env).returncode
        after = constructor.file_hashes(paths, case)
        stages[label] = {"argv": argv, "exit": status,
                         "source_before": before, "source_after": after,
                         "source_unchanged": before == after}
        (case / (label + "-stage.json")).write_text(json.dumps(stages[label],
            indent=2, sort_keys=True) + "\n")
        return status

    readonly = stage("readonly-export", [str(args.tool_home / "bin/vf-rust-mir-exporter"),
        "verified/lib.rs", f"--sysroot={args.compiler_sysroot}", "--edition", "2021",
        "--crate-type", "lib", "--vf-rust-mir-exporter:preprocess-readonly"],
        "readonly-mir.bin", "readonly-export.log")
    if readonly == 0:
        stage("readonly-decode", ["capnp", "decode", str(args.schema), "VfMir"],
              "readonly-mir.txt", "readonly-decode.log", "readonly-mir.bin")
    normal = stage("normal-export", [str(args.tool_home / "bin/vf-rust-mir-exporter"),
        "verified/lib.rs", f"--sysroot={args.compiler_sysroot}", "--edition", "2021"],
        "normal-mir.bin", "normal-export.log")
    if normal == 0:
        stage("normal-decode", ["capnp", "decode", str(args.schema), "VfMir"],
              "normal-mir.txt", "normal-decode.log", "normal-mir.bin")
    focus = fixture["focus"]
    argv = [str(args.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
            "-focus", f"{focus['file']}:{focus['line']}", "-verbose", "1",
            "verified/lib.rs"]
    stage("focused-verification", argv, "verifast.log")
    stage("refinement", [str(args.tool_home / "bin/refinement-checker"),
        "--rustc-args", "--edition 2021", "original/lib.rs", "verified/lib.rs"],
        "refinement.log")
    return stages


def classify(case: Path, stages: dict) -> dict:
    fixture = json.loads((case / "fixture.json").read_text())
    focus = fixture["focus"]
    log = (case / "verifast.log").read_text(errors="replace")
    errors = [line for line in log.splitlines() if ": error:" in line]
    headers = re.findall(r"Verifying function '([^']+)'", log)
    intended = [name for name in headers if name.endswith(focus["function"])]
    parent = [name for name in headers if name == "select_unpredictable"]
    marker = "Verifying function '" + intended[0] + "'" if intended else ""
    start = log.find(marker) if marker else -1
    next_header = log.find("Verifying function '", start + len(marker)) \
        if start >= 0 else -1
    target_log = log[start:next_header if next_header >= 0 else None] \
        if start >= 0 else ""
    body_seen = "Executing statement" in target_log
    return_seen = "Executing return statement" in target_log
    leak_seen = "Leak check." in target_log
    expected_hashes = {f"{mode}/{name}": digest
        for mode, files in fixture["source_sha256"].items()
        for name, digest in files.items()}
    source_ok = all(item["source_unchanged"] and
                    item["source_before"] == expected_hashes and
                    item["source_after"] == expected_hashes
                    for item in stages.values())
    frontend_ok = all(stages.get(name, {}).get("exit") == 0 for name in
        ("readonly-export", "readonly-decode", "normal-export",
         "normal-decode", "refinement"))
    error = errors[0] if len(errors) == 1 else ""
    expected_file = focus["file"]
    expected_line = focus["expected_error_line"]
    exact_location = bool(error and expected_line is not None and
        re.search(re.escape(expected_file) + r"\(" +
                  str(expected_line) + r",\d+(?:-|\))", error))
    expected = focus["obligation"]
    variant = fixture["variant"]
    predicate = {
        "false_assert": "Cannot prove false",
        "wrong_post": "Cannot prove false",
        "thread_loss": "Function leaks heap chunks: thread_token",
        "thread_duplication": "No matching heap chunks: thread_token",
        "frame_loss": "Function leaks heap chunks: points_to<bool>",
        "frame_duplication": "No matching heap chunks: points_to<bool>",
    }.get(variant)
    exact_predicate = (predicate in error if predicate else
        variant == "frame_wrong_value" and "Cannot prove" in error and
            "true" in error and "false" in error)
    positive = (expected == "body_return_leak" and
        stages["focused-verification"]["exit"] == 0 and body_seen and
        return_seen and leak_seen and not errors)
    negative = (expected != "body_return_leak" and
        stages["focused-verification"]["exit"] == 1 and body_seen and
        len(errors) == 1 and exact_location and exact_predicate and
        (expected != "leak" or (return_seen and leak_seen)))
    accepted = (source_ok and frontend_ok and len(intended) == 1 and not parent and
                (positive or negative))
    classification = (("DIAGNOSTIC_POSITIVE" if positive else
                       "INTENDED_DIAGNOSTIC_REJECTION") if accepted else
                      "INCONCLUSIVE")
    result = {"variant": fixture["variant"], "classification": classification,
              "accepted_component": False, "full_select_proved": False,
              "focus": focus, "focus_argv": stages["focused-verification"]["argv"],
              "admission_active": False,
              "source_integrity": source_ok, "frontend_complete": frontend_ok,
              "target_function_headers": intended, "parent_headers": parent,
              "body_execution_seen": body_seen, "body_return_seen": return_seen,
              "leak_check_seen": leak_seen,
              "first_error": errors[0] if errors else None,
              "error_count": len(errors),
              "error_at_exact_expected_line": exact_location,
              "error_at_exact_expected_predicate": exact_predicate,
              "normal_mir_sha256": sha((case / "normal-mir.txt").read_bytes())
                  if (case / "normal-mir.txt").exists() else None,
              "readonly_mir_sha256": sha((case / "readonly-mir.txt").read_bytes())
                  if (case / "readonly-mir.txt").exists() else None,
              "stages": stages}
    (case / "classification.json").write_text(json.dumps(result, indent=2,
        sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--compiler-sysroot")
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--construction-preflight", action="store_true")
    parser.add_argument("--preflight-manifest", type=Path)
    args = parser.parse_args()
    require(args.construction_preflight != bool(args.preflight_manifest),
            "choose construction preflight or bind a prior preflight manifest")
    if not args.construction_preflight:
        require(args.tool_home is not None and args.schema is not None and
                args.compiler_sysroot is not None,
                "full S7a diagnostic needs frozen tools, schema and compiler sysroot")
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux" and
            os.environ.get("SORT4_SELECT_PROFILE") == PROFILE,
            "S7a diagnostic requires hosted frozen v4 profile")
    for key in ("SORT4_MAYBEUNINIT_REPO_ROOT",
                "SORT4_SELECT_INTRINSIC_REPO_ROOT", "SORT4_POINTER_DROP_REPO_ROOT"):
        require(key not in os.environ, "S7a cannot activate v4 admission routes")
    repo = Path(__file__).resolve().parents[2]
    require(sha((repo / "research/challenge-8/verifast-select-pointer-drop.patch").read_bytes())
            == PATCH_SHA, "S7a semantic patch differs from accepted v4")
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    scripts = repo / "research/challenge-8"
    constructor = load(scripts / "check-maybeuninit-new-pointer.py", "s7_constructor")
    prepare = load(scripts / "prepare-select-pointer-actual.py", "s7_prepare")
    certificate = source_certificate(repo, constructor, prepare, None)
    (evidence / "source-certificate.json").write_text(json.dumps(certificate,
        indent=2, sort_keys=True) + "\n")
    base, fixture = projected_base(evidence, repo, constructor, prepare)
    cases = {}
    for variant in VARIANTS:
        case = make_case(evidence, base, variant, fixture, constructor)
        cases[variant] = json.loads((case / "fixture.json").read_text())
    if args.construction_preflight:
        manifest = {"classification": "DIAGNOSTIC_CONSTRUCTION_PREFLIGHT",
                    "accepted_component": False, "tool_profile": PROFILE,
                    "patch_sha256": PATCH_SHA, "source_certificate": certificate,
                    "variants": list(VARIANTS),
                    "source_sha256": {variant: cases[variant]["source_sha256"]
                                      for variant in VARIANTS},
                    "all_nine_source_pairs_ghost_strip_identical": True}
        (evidence / "construction-preflight.json").write_text(json.dumps(
            manifest, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"classification": manifest["classification"],
                          "constructed": len(VARIANTS)}))
        return
    preflight = json.loads(args.preflight_manifest.read_text())
    require(preflight == {
        "classification": "DIAGNOSTIC_CONSTRUCTION_PREFLIGHT",
        "accepted_component": False, "tool_profile": PROFILE,
        "patch_sha256": PATCH_SHA, "source_certificate": certificate,
        "variants": list(VARIANTS),
        "source_sha256": {variant: cases[variant]["source_sha256"]
                          for variant in VARIANTS},
        "all_nine_source_pairs_ghost_strip_identical": True},
        "S7a fresh source construction differs from hosted preflight")
    results = []
    for variant in VARIANTS:
        case = evidence / variant
        try:
            stages = run_case(case, args, constructor)
            result = classify(case, stages)
        except Exception as exc:
            case.mkdir(parents=True, exist_ok=True)
            result = {"variant": variant, "classification": "INCONCLUSIVE",
                      "accepted_component": False,
                      "error": f"{type(exc).__name__}: {exc}"}
            (case / "classification.json").write_text(json.dumps(result,
                indent=2, sort_keys=True) + "\n")
        results.append(result)
    summary = {"classification": "DIAGNOSTIC_ONLY", "accepted_component": False,
               "full_select_proved": False, "actual_redirected": False,
               "v4_admission_active": False, "tool_profile": PROFILE,
               "cases": results, "all_cases_collected": len(results) == len(VARIANTS),
               "intended_diagnostic_count": sum(item["classification"] in
                   {"DIAGNOSTIC_POSITIVE", "INTENDED_DIAGNOSTIC_REJECTION"}
                   for item in results),
               "new_trust_rule_accepted": False,
               "remaining_unproved": "entire actual parent and all nonfocused bodies"}
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2,
        sort_keys=True) + "\n")
    print(json.dumps({"classification": summary["classification"],
                      "collected": len(results),
                      "intended_diagnostics": summary["intended_diagnostic_count"]}))


if __name__ == "__main__":
    main()
