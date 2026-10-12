#!/usr/bin/env python3
"""Cloud-only I prerequisite assembly and input-bound C0-C2 evidence.

Import is inert. No historical verdict is carried to this tool. Negative rows
remain unaccepted until their first diagnostic is reviewed at the intended gate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import lzma
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

HERE = Path("research/challenge-8/cloud-build/verifast-i-glue-prereqs")
PROFILE = "experimental-i-glue-prereqs-u64-v1"
SCHEMA = "src/rust_frontend/vf_mir/vf_mir.capnp"

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

def need(value, message):
    if not value:
        raise RuntimeError("I-GLUE-PREREQS: " + message)

def context(a):
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") == "verifast-i-glue-prereqs" and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud-only lane")
    for name in ("proof_root", "manifest", "evidence"):
        need(str(getattr(a, name).resolve()).startswith("/workspace/"), name)
    need(subprocess.check_output(["git", "-C", str(a.proof_root), "rev-parse", "HEAD"],
                                 text=True).strip() == os.environ["PROOF_SHA"], "proof SHA")
    data = json.loads(a.manifest.read_text())
    need(data["schema"] == "i-glue-prereqs-tool-v1" and data["profile"] == PROFILE and
         data["profile_accepted"] is False and data["tool_head"], "prepared tool manifest")
    return data

def inputs(a, data):
    package = a.proof_root / HERE
    need(sha(package / "i-base.patch.xz") == data["i_base_patch_xz_sha256"], "I delivery")
    need(sha(package / "tool.patch.xz") == data["additive_patch_xz_sha256"], "additive compressed delivery")
    raw = lzma.decompress((package / "tool.patch.xz").read_bytes())
    need(len(raw) == data["additive_patch_raw_bytes"] and hashlib.sha256(raw).hexdigest() == data["additive_patch_sha256"], "additive raw delivery")
    rows = json.loads((package / "fixture-admission.json").read_text())["source_fixtures"]
    for row in rows:
        for kind in ("original", "verified"):
            need(sha(package / row["path"] / kind / "lib.rs") == row[kind + "_sha256"],
                 "fixture SHA: " + row["id"] + "/" + kind)
    save(a.evidence / "input-closure.json", {"manifest_sha256": sha(a.manifest),
         "fixture_manifest_sha256": sha(package / "fixture-admission.json"),
         "source_pairs": rows, "profile": PROFILE, "compiler": data["compiler_commit"],
         "source_preparation_or_compilation": False, "proof_credit": False})

def apply(a, data):
    inputs(a, data)
    package = a.proof_root / HERE
    need(subprocess.check_output(["git", "-C", str(a.tool_home), "rev-parse", "HEAD"],
                                 text=True).strip() == data["stock_base"], "stock source commit")
    raw = lzma.decompress((package / "i-base.patch.xz").read_bytes())
    need(hashlib.sha256(raw).hexdigest() == data["i_base_patch_sha256"], "I raw patch")
    base_patch = a.evidence / "i-base.patch"
    base_patch.write_bytes(raw)
    additive_patch = a.evidence / "additive-tool.patch"
    additive_patch.write_bytes(lzma.decompress((package / "tool.patch.xz").read_bytes()))
    for patch, label, expected in ((base_patch, "I-base", data["i_effective_hashes"]),
                                    (additive_patch, "additive", data["effective_hashes"])):
        for flags in (["--check"], []):
            result = subprocess.run(["git", "-C", str(a.tool_home), "apply", *flags, str(patch)],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (a.evidence / (label + ("-check" if flags else "-apply") + ".log")).write_bytes(result.stdout)
            need(result.returncode == 0, label + " apply")
        actual = {name: sha(a.tool_home / name) for name in expected}
        need(actual == expected, label + " effective source pins")
        save(a.evidence / (label + "-source-pins.json"), actual)
    # The disposable source index provides an independent full-tree check,
    # rather than treating the manifest's tool_head as a label.
    subprocess.run(["git", "-C", str(a.tool_home), "add", "-u"], check=True)
    observed_tree = subprocess.check_output(["git", "-C", str(a.tool_home), "write-tree"],
                                             text=True).strip()
    need(observed_tree == data["tool_tree"], "assembled full source tree differs from tool head")
    save(a.evidence / "assembled-tree.json", {"actual_tree": observed_tree,
         "expected_tree": data["tool_tree"], "tool_head": data["tool_head"],
         "source_reconstructed_from_exact_patches": True})

def pin(a, data):
    actual = {name: sha(a.tool_home / name) for name in data["effective_hashes"]}
    need(actual == data["effective_hashes"], "source/spec changed after assembly")
    binaries = {name: sha(a.tool_home / "bin" / name) for name in
                ("verifast", "vf-rust-mir-exporter", "refinement-checker", "vf-cxx-ast-exporter", "libz3.so")}
    save(a.evidence / "effective-tool.json", {"tool_head": data["tool_head"],
         "i_base": data["i_base"], "stock_base": data["stock_base"],
         "manifest_sha256": sha(a.manifest), "source_hashes": actual, "binaries": binaries,
         "profile": PROFILE, "profile_accepted": False})

def stage(a, case, name, argv, env, cap=120, input_path=None, output_path=None):
    seconds = min(cap, a.deadline_epoch - int(time.time()) - 25)
    need(seconds > 0, "deadline before " + name)
    clean = {k: v for k, v in os.environ.items()
             if not k.startswith(("SORT4_", "SMALLSORT_I_GLUE", "SMALLSORT_ACTUAL_GLUE", "SMALLSORT_SELECTED_DROP"))}
    clean.update(env)
    log = case / (name + ".log")
    resources = case / (name + "-resources.txt")
    with log.open("wb") as stream:
        inp = input_path.open("rb") if input_path else subprocess.DEVNULL
        out = output_path.open("wb") if output_path else stream
        try:
            code = subprocess.run(["/usr/bin/time", "-v", "-o", str(resources),
                "timeout", "--signal=TERM", "--kill-after=10s", str(seconds) + "s", *argv],
                cwd=case, env={**clean, "PWD": str(case)}, stdin=inp,
                stdout=out, stderr=stream).returncode
        finally:
            if input_path: inp.close()
            if output_path: out.close()
    text = log.read_text(errors="replace")
    row = {"exit": code, "argv": argv, "cwd": str(case), "environment": env,
           "log_sha256": sha(log), "output_sha256": sha(output_path) if output_path else None,
           "first_diagnostic": next((line for line in text.splitlines()
               if re.search(r"error:|^Error:|^Fatal error:", line)), None), "proof_credit": False}
    save(case / (name + "-stage.json"), row)
    return row, text

def proof(a, case, env):
    src = case / "verified/lib.rs"
    before = sha(src)
    row, log = stage(a, case, "verifier", [str(a.tool_home / "bin/verifast"),
         "-rustc_args", "--edition 2021", "-dump_ast_with_locs", str(case / "proof-ast.ml"),
         "-dump_per_line_stmt_exec_counts", "-verbose", "2", "verified/lib.rs"], env)
    need(sha(src) == before, "verifier changed input source")
    row.update({"headers": re.findall(r"Verifying function '([^']+)'", log),
         "body_executions": len(re.findall(r"Executing", log)),
         "return_seen": "Executing return statement" in log,
         "leak_check_seen": "Leak check." in log,
         "dead_code": re.findall(r"(?m)^.*: dead code$", log),
         "zero_errors": "0 errors found (" in log,
         "target_line": next((i for i, line in enumerate(src.read_text().splitlines(), 1)
                                if "TARGET: C2 diagnostic" in line), None),
         "ast_sha256": sha(case / "proof-ast.ml") if (case / "proof-ast.ml").exists() else None})
    save(case / "proof-evidence.json", row)
    return row

def capture(a, case, env):
    result = {}
    for kind in ("original", "verified"):
        binary = case / (kind + "-mir.bin")
        decoded = case / (kind + "-mir.txt")
        row, _ = stage(a, case, kind + "-export", [str(a.tool_home / "bin/vf-rust-mir-exporter"),
             kind + "/lib.rs", "--sysroot=" + str(a.compiler_sysroot), "--edition", "2021"], env,
             output_path=binary)
        result[kind + "-export"] = row
        if row["exit"] != 0: return result, False
        row, _ = stage(a, case, kind + "-decode", ["capnp", "decode", str(a.tool_home / SCHEMA), "VfMir"],
                       env, input_path=binary, output_path=decoded)
        result[kind + "-decode"] = row
        if row["exit"] != 0: return result, False
    row, _ = stage(a, case, "official-refinement", [str(a.tool_home / "bin/refinement-checker"),
         "--rustc-args", "--edition 2021", "original/lib.rs", "verified/lib.rs"], env)
    result["official-refinement"] = row
    return result, row["exit"] == 0

def run(a, data):
    pin(a, data)
    package = a.proof_root / HERE
    fixture_data = json.loads((package / "fixture-admission.json").read_text())
    root = a.evidence / "cases"
    root.mkdir()
    c0 = {}
    baseline = root / "profile-off"
    (baseline / "verified").mkdir(parents=True)
    (baseline / "verified/lib.rs").write_text("#![no_std]\npub fn scalar(x: u64) -> u64 { x }\n")
    c0["profile-off"] = proof(a, baseline, {})
    positive_path = package / "cases/prefix-positive"
    setting_cases = (("invalid-zero", {"SMALLSORT_I_GLUE_PREREQS": "0"}),
                      ("invalid-empty", {"SMALLSORT_I_GLUE_PREREQS": ""}),
                      ("partial-layout-control", {"SMALLSORT_I_GLUE_LAYOUT_MUTANT": "foreign-source"}),
                      ("partial-binding-control", {"SMALLSORT_I_GLUE_BINDING_MUTANT": "wrong-mir-id"}),
                      ("mixed-native", {"SMALLSORT_I_GLUE_PREREQS": PROFILE,
                                         "SORT4_NATIVE_C4_BOUND": "1"}),
                      ("mixed-native-capture", {"SMALLSORT_I_GLUE_PREREQS": PROFILE,
                                                 "SORT4_NATIVE_C4_CAPTURE": "1"}),
                      ("mixed-opaque-c1", {"SMALLSORT_I_GLUE_PREREQS": PROFILE,
                                            "SORT4_NATIVE_OPAQUE_C1_BOUND": "1"}),
                      ("mixed-opaque-capture", {"SMALLSORT_I_GLUE_PREREQS": PROFILE,
                                                 "SORT4_NATIVE_OPAQUE_C1_CAPTURE": "1"}),
                      ("mixed-selector", {"SMALLSORT_I_GLUE_PREREQS": PROFILE,
                                           "SORT4_ACTUAL_C4_FIRST_SELECT_TEST": "1"}),
                      ("mixed-glue-zero-presence", {"SMALLSORT_I_GLUE_PREREQS": PROFILE,
                                                    "SMALLSORT_ACTUAL_GLUE_BODY": "0"}),
                      ("mixed-glue", {"SMALLSORT_I_GLUE_PREREQS": PROFILE,
                                       "SMALLSORT_ACTUAL_GLUE_BODY": "1"}))
    for name, env in setting_cases:
        case = root / name
        shutil.copytree(positive_path, case)
        c0[name] = proof(a, case, env)
    def settings_gate(name, row):
        marker = ("Invalid SMALLSORT_I_GLUE_PREREQS profile" if name.startswith("invalid-")
                  else "mutation controls require the exact prerequisites profile" if name.startswith("partial-")
                  else "cannot be mixed with native, selector, or generated-glue settings")
        # The exact first refusal must be the settings gate, not any early error.
        return row["exit"] != 0 and marker in (row.get("first_diagnostic") or "")
    c0_ok = (c0["profile-off"]["exit"] == 0 and c0["profile-off"]["zero_errors"] and
             all(settings_gate(name, c0[name]) for name, _ in setting_cases))
    save(a.evidence / "c0-settings.json", {"rows": c0, "provisional_settings_closure": c0_ok,
         "raw_review_required": True, "proof_credit": False})
    rows = {}
    admission_controls = {}
    for name in ("foreign-source", "foreign-compiler", "foreign-target", "foreign-width",
                 "foreign-type", "foreign-layout", "foreign-align", "foreign-offset",
                 "foreign-field-size", "foreign-field-shape", "duplicate"):
        case = root / ("layout-" + name)
        shutil.copytree(positive_path, case)
        row = proof(a, case, {"SMALLSORT_I_GLUE_PREREQS": PROFILE,
                             "SMALLSORT_I_GLUE_LAYOUT_MUTANT": name})
        row.update({"source_sha256": sha(case / "verified/lib.rs"),
                    "intended_gate": "actual qualified layout validation before model facts",
                    "classification": "ADMISSION_REFUSAL_PENDING_GATE_REVIEW",
                    "intended_negative_credit": False})
        admission_controls["layout-" + name] = row
    for name in ("wrong-mir-id", "wrong-translated-local"):
        case = root / ("binding-" + name)
        shutil.copytree(positive_path, case)
        row = proof(a, case, {"SMALLSORT_I_GLUE_PREREQS": PROFILE,
                             "SMALLSORT_I_GLUE_BINDING_MUTANT": name})
        row.update({"source_sha256": sha(case / "verified/lib.rs"),
                    "intended_gate": "actual independent MIR declaration/event inventory",
                    "classification": "ADMISSION_REFUSAL_PENDING_GATE_REVIEW",
                    "intended_negative_credit": False})
        admission_controls["binding-" + name] = row
    save(a.evidence / "admission-controls.json", admission_controls)
    for fixture in fixture_data["source_fixtures"]:
        case = root / Path(fixture["path"]).name
        shutil.copytree(package / fixture["path"], case)
        env = {"SMALLSORT_I_GLUE_PREREQS": PROFILE}
        captures, closed = capture(a, case, env)
        result = {"fixture": fixture, "source_pair": {k: sha(case / k / "lib.rs")
                    for k in ("original", "verified")}, "capture": captures,
                  "source_refinement_closed": closed, "classification": "SETUP_OR_ADMISSION_REFUSAL",
                  "intended_gate": fixture.get("expected_gate", fixture.get("expected")),
                  "intended_negative_credit": False}
        if closed:
            result["proof"] = proof(a, case, env)
            observed = result["proof"]
            result["classification"] = ("POSITIVE_RAW_PASS_PENDING_REVIEW" if observed["exit"] == 0 and
                observed["zero_errors"] and not observed["dead_code"] else "PROOF_REFUSAL_PENDING_GATE_REVIEW")
        save(case / "result.json", result)
        rows[fixture["id"]] = result
    positive = rows.get("c2-prefix-positive", {})
    gate_ok = positive.get("classification") == "POSITIVE_RAW_PASS_PENDING_REVIEW"
    result = {"classification": "C0_C2_RAW_EVIDENCE_PENDING_REVIEW", "settings_closed": c0_ok,
              "c2_positive_raw_pass": gate_ok, "rows": rows,
              "admission_controls": admission_controls, "raw_review_required": True,
              "profile_accepted": False, "verification_accepted": False,
              "C3": "NOT_RUN_DEFERRED_BY_USER", "C4_C7": "NOT_RUN_PENDING_C0_C2", "accepted": False}
    save(a.evidence / "result.json", result)
    save(a.evidence.parents[1] / "proof-audit.json", result)
    need(c0_ok and gate_ok, "C0/C2 gate incomplete; do not proceed to affected I gates")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("inputs", "apply", "pin", "run", "checkpoint"))
    parser.add_argument("--proof-root", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path)
    parser.add_argument("--compiler-sysroot", type=Path)
    parser.add_argument("--deadline-epoch", type=int)
    parser.add_argument("--stage")
    parser.add_argument("--exit-code", type=int)
    a = parser.parse_args()
    if a.mode == "checkpoint":
        save(a.evidence / "execution-checkpoint.json", {"stage": a.stage, "exit": a.exit_code,
             "raw_result_present": (a.evidence / "result.json").exists(), "profile_accepted": False})
        return
    data = context(a)
    {"inputs": inputs, "apply": apply, "pin": pin, "run": run}[a.mode](a, data)

if __name__ == "__main__":
    main()
