#!/usr/bin/env python3
"""Cloud-only native C1-C4 and ZST gates on the Bool integration tool.

Import is inert. Source preparation is a separate command that must finish
before the console build. No path in this module copies or rebuilds the tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from types import SimpleNamespace

HERE = Path("research/challenge-8/cloud-build/verifast-native-zst-integration")
NATIVE = Path("research/challenge-8/cloud-build/sort4-native-c1-bound")
INTEGRATION = Path("research/challenge-8/cloud-build/verifast-c4-select-integration")
TARGET = "small_sort_general_with_scratch"
FALSE_LOCATIONS = {
    "normal-false": "verified/lib.rs(577,9-40): error: Assertion might not hold. (Cannot prove false.)",
    "c1-unwind-false": "verified/lib.rs(387,22-93): error: Assertion might not hold. (Cannot prove false.)",
    "c2-unwind-false": "verified/lib.rs(442,18-99): error: Assertion might not hold. (Cannot prove false.)",
    "c3-unwind-false": "verified/lib.rs(504,18-75): error: Assertion might not hold. (Cannot prove false.)",
    "c4-unwind-false": "verified/lib.rs(561,18-75): error: Assertion might not hold. (Cannot prove false.)",
}
REFUSALS = {
    "source-refusal": "NATIVE-C4-BOUND: verified source SHA256 differs",
    "extra-body": "NATIVE-C4-BOUND: isolated exact-one body, unwind/full checks required",
    "malformed": "NATIVE-C4-BOUND: malformed opt-in",
    "mixed": "NATIVE-PROFILE-COMPAT: isolated native mode excludes composition/AST/FRAME/cleanup opt-ins",
}
ZST_ERRORS = {
    "generic-pre-guard-positive-assert-no-scratch":
        "verified/lib.rs(3,41-42): error: Assertion might not hold. (Cannot prove 0 < sizeof(T_typeid).)",
    "generic-pre-guard-positive-assert-mu-scratch":
        "verified/lib.rs(4,41-42): error: Assertion might not hold. (Cannot prove 0 < sizeof(T_typeid).)",
    "reachable-concrete-zst-false":
        "verified/lib.rs(4,16-21): error: Assertion might not hold. (Cannot prove false.)",
    "zst-no-extra-permission":
        "verified/lib.rs(4,19-22): error: No matching heap chunks: points_to<std_tuple_0_>(p, _)",
}
C1_ERRORS = {
    "native-c1-bound-default-off":
        "verified/lib.rs(172,1-30): error: Strict lifetime binding has unresolved inference in entry outer type",
    "native-c1-bound-false-normal":
        "verified/lib.rs(226,9-227,1): error: Assertion might not hold. (Cannot prove false.)",
    "native-c1-bound-false-unwind":
        "verified/lib.rs(210,22-93): error: Assertion might not hold. (Cannot prove false.)",
    "native-c1-bound-source-refusal":
        'Fatal error: exception Failure("NATIVE-OPAQUE-C1-BOUND: verified source SHA256 differs")',
    "native-c1-bound-extra-body":
        'Fatal error: exception Failure("NATIVE-OPAQUE-C1-BOUND: isolated exact-one body, unwind and full checks required")',
    "native-c1-bound-malformed":
        'Fatal error: exception Failure("NATIVE-OPAQUE-C1-BOUND: malformed opt-in")',
    "native-c1-bound-mixed":
        'Fatal error: exception Failure("NATIVE-PROFILE-COMPAT: isolated native mode excludes composition/AST/FRAME/cleanup opt-ins")',
}


def need(ok, message):
    if not ok:
        raise RuntimeError("NATIVE-ZST-INTEGRATION: " + message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")


def context(a):
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") in ("verifast-native-zst-integration",
                                      "verifast-slice-binding-integration") and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud lane identity")
    for name in ("proof_root", "cloud_dir", "evidence", "manifest"):
        need(str(getattr(a, name).resolve()).startswith("/workspace/"), name + " outside workspace")
    need(os.environ.get("PROOF_SHA") == subprocess.check_output(
        ["git", "-C", str(a.proof_root), "rev-parse", "HEAD"], text=True).strip(),
        "proof commit differs")
    data = json.loads(a.manifest.read_text())
    need(data.get("classification") == "EXPERIMENTAL_C4_SELECT_INTEGRATION" and
         data.get("accepted") is False and
         data.get("native_zst_profile") == "verifast-native-zst-c3-integration-20261011-h",
         "new integration manifest identity")
    return data


def modules(a):
    driver_path = a.cloud_dir / INTEGRATION.relative_to("research/challenge-8/cloud-build") / "driver.py"
    # All imports are inert. The exact imported files are bound by the recipe.
    import importlib.util
    def load(path, name):
        spec = importlib.util.spec_from_file_location(name, path)
        need(spec is not None and spec.loader is not None, "missing module " + str(path))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    return (load(driver_path, "native_zst_integration_driver"),
            load(a.cloud_dir / "sort4-native-c1-bound/native-c4-driver.py", "native_zst_c4"),
            load(a.cloud_dir / "sort4-native-c1-bound/zst_model_gates.py", "native_zst_models"),
            load(a.cloud_dir / "sort4-native-c1-bound/ghost-strip.py", "native_zst_ghost"))


def source_prepare(a, data):
    need(not a.evidence.exists(), "native source preparation already exists")
    a.evidence.mkdir(parents=True)
    driver, native, models, ghost = modules(a)
    shim = SimpleNamespace(load=driver.module, save=save)
    fixture = a.evidence / "native-c4-positive"
    cert = native.make_source(a, shim, fixture)
    bound = json.loads((a.proof_root / NATIVE / "NATIVE-C4-BOUND-MANIFEST.json").read_text())
    need(cert["verified_sha256"] == bound["verified_source_sha256"] and
         cert["original_sha256"] == bound["original_source_sha256"],
         "native C1-C4 exact source pair")
    c1_profile = json.loads((a.proof_root / NATIVE / "profile.json").read_text())
    case_text = (a.proof_root / NATIVE / "followup-cases.rs").read_text()
    c1_rows = {}
    for name in c1_profile["followup_cases"]:
        match = re.search(r"(?ms)^// CASE_BEGIN " + re.escape(name) +
                          r"\n(.*?)^// CASE_END " + re.escape(name) + r"$", case_text)
        need(match is not None, "native C1 source block " + name)
        root = a.evidence / "native-c1" / name
        (root / "verified").mkdir(parents=True)
        (root / "original").mkdir()
        verified = match.group(1).encode()
        original = ghost.strip_ghost(verified)
        (root / "verified/lib.rs").write_bytes(verified)
        (root / "original/lib.rs").write_bytes(original)
        c1_rows[name] = {"verified_sha256": sha(root / "verified/lib.rs"),
                         "original_sha256": sha(root / "original/lib.rs")}
    positive = c1_rows["native-c1-bound-positive"]
    need(positive["verified_sha256"] == c1_profile["native_c1_bound_verified_source_sha256"] and
         positive["original_sha256"] == c1_profile["native_c1_bound_original_source_sha256"],
         "native C1 exact source pair")
    rows = {}
    for name, gate in models.GATES.items():
        root = a.evidence / "zst" / name
        (root / "verified").mkdir(parents=True)
        (root / "original").mkdir()
        verified = gate["source"].encode()
        original = ghost.strip_ghost(verified)
        (root / "verified/lib.rs").write_bytes(verified)
        (root / "original/lib.rs").write_bytes(original)
        rows[name] = {"verified_sha256": sha(root / "verified/lib.rs"),
                      "original_sha256": sha(root / "original/lib.rs"),
                      "target": gate["target"], "positive": gate["positive"]}
    for name, source in models.C_CONTROLS.items():
        ext = ".c" if name.startswith("c-") else ".cpp"
        path = a.evidence / "zst" / name / (name + ext)
        path.parent.mkdir(parents=True)
        path.write_text(source)
        rows[name] = {"source_sha256": sha(path), "positive": True,
                      "language": ext[1:]}
    save(a.evidence / "prepared.json", {
        "profile": data["native_zst_profile"], "native_source": cert,
        "native_c1_sources": c1_rows,
        "zst_controls": rows, "proof_credit": False,
        "source_prepared_before_console_build": True})


def apply(a, data):
    need(not a.evidence.exists(), "native tool apply evidence already exists")
    a.evidence.mkdir(parents=True)
    need(str(a.tool_home.resolve()).startswith("/workspace/"), "tool outside workspace")
    patches = data.get("native_zst_tool_patches")
    need(isinstance(patches, list) and len(patches) >= 1, "missing patch sequence")
    rows = []
    for patch in patches:
        need(set(patch) == {"path", "sha256", "before", "after"}, "patch schema")
        relative = Path(patch["path"])
        need(not relative.is_absolute() and ".." not in relative.parts and
             str(relative).startswith("research/challenge-8/"), "patch path")
        path = a.proof_root / relative
        need(sha(path) == patch["sha256"], "patch SHA differs: " + str(relative))
        need(isinstance(patch["before"], dict) and
             isinstance(patch["after"], dict) and patch["before"], "patch file pins")
        for name, expected in patch["before"].items():
            need(sha(a.tool_home / name) == expected, "patch base differs: " + name)
        for operation in ("check", "apply"):
            argv = ["git", "-C", str(a.tool_home), "apply"]
            if operation == "check":
                argv.append("--check")
            argv.append(str(path))
            result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, check=False)
            (a.evidence / (f"patch-{len(rows)}-{operation}.log")).write_text(result.stdout)
            need(result.returncode == 0, "patch " + operation + " failed: " + str(relative))
        for name, expected in patch["after"].items():
            need(sha(a.tool_home / name) == expected, "patch output differs: " + name)
        rows.append({"path": str(relative), "sha256": patch["sha256"],
                     "before": patch["before"], "after": patch["after"]})
    save(a.evidence / "applied.json", {"patches": rows, "proof_credit": False})


def first_error(log):
    return next((line for line in log.splitlines() if ": error:" in line or
                 line.startswith(("Fatal error:", "error:"))), None)


def support(a, driver, fixture, label, expected_mir=None, target=TARGET):
    stages = {}
    paths = {}
    for mode, extra in (("normal", []), ("readonly", ["--crate-type", "lib",
                                                       "--vf-rust-mir-exporter:preprocess-readonly"])):
        binary = a.evidence / (label + "-" + mode + "-mir.bin")
        decoded = a.evidence / (label + "-" + mode + "-mir.txt")
        stages[mode + "-export"], _ = driver.stage(a, label + "-" + mode + "-export",
            [str(a.tool_home / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
             "--sysroot=" + str(a.compiler_sysroot), "--edition", "2021", *extra],
            fixture, stdout=binary)
        need(stages[mode + "-export"]["exit"] == 0, label + " " + mode + " export")
        stages[mode + "-decode"], _ = driver.stage(a, label + "-" + mode + "-decode",
            ["capnp", "decode", str(a.tool_home / driver.SCHEMA), "VfMir"],
            fixture, stdin=binary, stdout=decoded)
        need(stages[mode + "-decode"]["exit"] == 0, label + " " + mode + " decode")
        capture = driver.module(a.proof_root / "research/challenge-8/overnight-sort4/capture.py",
                                "native_zst_capture_" + label + mode)
        _, body = capture.complete_function_record(decoded.read_text(), target)
        body_path = a.evidence / (label + "-" + mode + "-full-mir.txt")
        body_path.write_text(body)
        paths[mode] = sha(body_path)
        if expected_mir is not None:
            need(paths[mode] == expected_mir[mode], label + " full " + mode + " MIR")
    stages["refinement"], _ = driver.stage(a, label + "-refinement",
        [str(a.tool_home / "bin/refinement-checker"), "--rustc-args", "--edition 2021",
         "original/lib.rs", "verified/lib.rs"], fixture)
    need(stages["refinement"]["exit"] == 0, label + " source refinement")
    result = {"stages": stages, "full_mir_sha256": paths, "target": target,
              "verified_sha256": sha(fixture / "verified/lib.rs"),
              "original_sha256": sha(fixture / "original/lib.rs"),
              "paired_support_passed": True, "proof_credit": False}
    save(a.evidence / (label + "-support.json"), result)
    return result


def isolated_env(driver):
    """Leave only the selected native mode or global ZST rule enabled."""
    env = driver.c4_env()
    env.update({
        "SORT4_ACTUAL_AST_SCOPE_TEST": "0",
        "SORT4_ACTUAL_C4_BOUND_PREFIX_TEST": "0",
        "SORT4_ACTUAL_C4_FIRST_SELECT_TEST": "0",
        "SORT4_C4_BOUND_CONTROL": "none",
        "SORT4_C4_FIRST_SELECT_CONTROL": "none",
        "SORT4_NATIVE_C4_CAPTURE": "0",
        "SORT4_NATIVE_C4_CAPTURE_SOURCE_SHA256": "",
        "SORT4_NATIVE_C4_BOUND": "0",
        "SORT4_NATIVE_C4_BOUND_CONTROL": "none",
    })
    return env


def native_cases(a, driver, prepared, bound):
    root = a.evidence / "native-c4-bound"
    root.mkdir()
    source = prepared / "native-c4-positive"
    cert = json.loads((prepared / "native-c4-source-certificate.json").read_text())
    expected = {"normal": bound["normal_full_mir_sha256"],
                "readonly": bound["readonly_full_mir_sha256"]}
    capture = support(a, driver, source, "native-c4", expected)
    native_env = isolated_env(driver)
    native_env.update({"SORT4_STRICT_LFT_CUT": "1", "SORT4_NATIVE_C4_BOUND": "1"})
    cases = [("positive", "none", "positive")]
    cases += [(f"c{i}-unwind-false", f"c{i}_unwind_false", "false") for i in (1, 2, 3, 4)]
    cases += [("normal-false", "normal_false", "false")]
    cases += [(name, "none", kind) for name, kind in
              (("source-refusal", "source"), ("extra-body", "extra"),
               ("malformed", "malformed"), ("mixed", "mixed"), ("default-off", "off"))]
    source_bytes = (source / "verified/lib.rs").read_bytes()
    original_bytes = (source / "original/lib.rs").read_bytes()
    results = {}
    for name, control, kind in cases:
        fixture = root / name / "fixture"
        (fixture / "verified").mkdir(parents=True)
        (fixture / "original").mkdir()
        altered = source_bytes + (b"\n" if kind == "source" else
                                 b"\nfn native_c4_extra_body() {}\n" if kind == "extra" else b"")
        (fixture / "verified/lib.rs").write_bytes(altered)
        (fixture / "original/lib.rs").write_bytes(original_bytes)
        env = dict(native_env)
        env["SORT4_NATIVE_C4_BOUND"] = "0" if kind == "off" else (
            "bad" if kind == "malformed" else "1")
        env["SORT4_NATIVE_C4_BOUND_CONTROL"] = control
        if kind == "mixed":
            env["SORT4_NATIVE_C4_CAPTURE"] = "1"
            env["SORT4_NATIVE_C4_CAPTURE_SOURCE_SHA256"] = cert["verified_sha256"]
        stage, raw = driver.stage(a, "native-" + name,
            [str(a.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
             "-verbose", "4", "verified/lib.rs"], fixture, env, 240)
        pre = fixture / "native-c4-bound-pre-ast.ml"
        post = fixture / "native-c4-bound-post-ast.ml"
        row = {"exit": stage["exit"], "first_error": first_error(raw),
               "admitted": "NATIVE-C4-BOUND admitted pre_ast=" +
                   bound["pre_transform_ast_sha256"] in raw,
               "source_immutable": sha(fixture / "verified/lib.rs") ==
                   hashlib.sha256(altered).hexdigest() and
                   sha(fixture / "original/lib.rs") == cert["original_sha256"],
               "pre_ast_sha256": sha(pre) if pre.is_file() else None,
               "post_ast_sha256": sha(post) if post.is_file() else None,
               "log_sha256": stage["log_sha256"], "proof_credit": False}
        if kind == "positive":
            good = (row["exit"] == 0 and row["admitted"] and row["source_immutable"] and
                    row["pre_ast_sha256"] == bound["pre_transform_ast_sha256"] and
                    row["post_ast_sha256"] is not None)
        elif kind == "false":
            good = (row["exit"] in (1, 2) and row["admitted"] and row["source_immutable"] and
                    row["first_error"] == FALSE_LOCATIONS[name] and
                    row["pre_ast_sha256"] == bound["pre_transform_ast_sha256"])
        elif kind in ("source", "extra", "malformed", "mixed"):
            good = (row["exit"] in (1, 2) and not row["admitted"] and
                    REFUSALS[name] in raw and row["source_immutable"] and not post.is_file())
        else:
            good = (row["exit"] != 0 and not row["admitted"] and
                    row["source_immutable"] and not pre.is_file() and not post.is_file())
        row["classification"] = ("EXPECTED_OBSERVED" if good else "INCONCLUSIVE")
        save(root / name / "case-result.json", row)
        results[name] = row
    return {"source": cert, "support": capture, "cases": results,
            "all_expected_observed": all(row["classification"] == "EXPECTED_OBSERVED"
                                         for row in results.values()),
            "actual_caller_proved": False, "callable_summary": False}


def fresh_c4_controls(a, driver, data):
    """Re-execute all nine inherited C4 controls after the verifast1 change."""
    expected = data["inherited_c4_controls"]["rows"]
    need(set(expected) == set(driver.CONTROLS), "C4 control set")
    source = a.evidence.parents[1] / "source-preparation/c4-fixture"
    need(source.is_dir() and sha(source / "verified/lib.rs") == data["c4_source_sha256"],
         "C4 control source")
    root = a.evidence / "fresh-c4-controls"
    root.mkdir()
    rows = {}
    for name in driver.CONTROLS:
        fixture = root / name
        shutil.copytree(source, fixture, symlinks=True)
        env = driver.c4_env()
        env["SORT4_C4_BOUND_CONTROL"] = name
        result, raw = driver.stage(a, "fresh-c4-" + name,
            [str(a.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
             "-verbose", "2", "verified/lib.rs"], fixture, env, 240)
        first = first_error(raw)
        entry = raw.find("Verifying function 'sort4_stable'")
        good = (result["exit"] in (1, 2) and first == expected[name]["expected_vc"] and
                entry >= 0 and raw.find(first) > entry and
                sha(fixture / "verified/lib.rs") == data["c4_source_sha256"])
        rows[name] = {"classification": "EXPECTED_VC_OBSERVED" if good else "INCONCLUSIVE",
                      "exit": result["exit"], "first_error": first,
                      "expected_vc": expected[name]["expected_vc"],
                      "target_entry_before_first_error": entry >= 0 and
                          first is not None and raw.find(first) > entry,
                      "log_sha256": result["log_sha256"],
                      "raw_vc_review": "PENDING_RAW_REVIEW", "proof_credit": False}
        save(root / (name + ".json"), rows[name])
    return {"cases": rows, "all_expected_observed": all(
        row["classification"] == "EXPECTED_VC_OBSERVED" for row in rows.values())}


def native_c1_cases(a, driver, prepared):
    profile = json.loads((a.proof_root / NATIVE / "profile.json").read_text())
    root = a.evidence / "native-c1-bound"
    root.mkdir()
    positive = prepared / "native-c1/native-c1-bound-positive"
    expected = {"normal": profile["native_c1_bound_normal_full_mir_sha256"],
                "readonly": profile["native_c1_bound_readonly_full_mir_sha256"]}
    support_row = support(a, driver, positive, "native-c1", expected)
    rows = {}
    for name in profile["followup_cases"]:
        fixture = prepared / "native-c1" / name
        source_pair = (sha(fixture / "verified/lib.rs"), sha(fixture / "original/lib.rs"))
        env = isolated_env(driver)
        env["SORT4_STRICT_LFT_CUT"] = "1"
        env["SORT4_NATIVE_OPAQUE_C1_BOUND"] = "0" if name.endswith("default-off") else (
            "bad" if name.endswith("malformed") else "1")
        env["SORT4_NATIVE_OPAQUE_C1_BOUND_CONTROL"] = (
            "normal_false" if name.endswith("false-normal") else
            "unwind_false" if name.endswith("false-unwind") else "none")
        if name.endswith("mixed"):
            env["SORT4_NATIVE_C4_CAPTURE"] = "1"
        stage, raw = driver.stage(a, "native-c1-" + name,
            [str(a.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
             "-verbose", "4", "verified/lib.rs"], fixture, env, 240)
        pre = fixture / "native-c1-bound-pre-ast.ml"
        post = fixture / "native-c1-bound-post-ast.ml"
        first = first_error(raw)
        admitted = "NATIVE-OPAQUE-C1-BOUND admitted pre_ast=" in raw
        immutable = source_pair == (sha(fixture / "verified/lib.rs"),
                                    sha(fixture / "original/lib.rs"))
        if name.endswith("positive"):
            good = (stage["exit"] == 0 and admitted and immutable and
                    "0 errors found (" in raw and "Verifying function '" + TARGET + "'" in raw and
                    "Executing return statement" in raw and "Leak check." in raw and
                    pre.is_file() and sha(pre) ==
                    "18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5" and
                    post.is_file())
        else:
            good = stage["exit"] in (1, 2) and first == C1_ERRORS[name] and immutable
            if name.endswith(("false-normal", "false-unwind")):
                good = good and admitted and "Verifying function '" + TARGET + "'" in raw
            elif name.endswith("default-off"):
                good = good and not admitted and not post.is_file()
            else:
                good = good and not admitted and not post.is_file()
        rows[name] = {"classification": "EXPECTED_OBSERVED" if good else "INCONCLUSIVE",
                      "exit": stage["exit"], "first_error": first, "admitted": admitted,
                      "source_pair_sha256": source_pair, "source_immutable": immutable,
                      "pre_ast_sha256": sha(pre) if pre.is_file() else None,
                      "post_ast_sha256": sha(post) if post.is_file() else None,
                      "log_sha256": stage["log_sha256"], "raw_vc_review": "PENDING_RAW_REVIEW",
                      "proof_credit": False}
        save(root / (name + ".json"), rows[name])
    return {"support": support_row, "cases": rows,
            "all_expected_observed": all(row["classification"] == "EXPECTED_OBSERVED"
                                         for row in rows.values()),
            "actual_caller_proved": False, "callable_summary": False}


def model_cases(a, driver, models, prepared):
    root = a.evidence / "zst-model"
    root.mkdir()
    rows = {}
    for name, gate in models.GATES.items():
        fixture = prepared / "zst" / name
        before = (sha(fixture / "verified/lib.rs"), sha(fixture / "original/lib.rs"))
        supported = support(a, driver, fixture, "zst-" + name, target=gate["target"])
        stage, raw = driver.stage(a, "zst-" + name + "-verification",
            [str(a.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
             "-verbose", "2", "verified/lib.rs"], fixture, isolated_env(driver), 180)
        error = first_error(raw)
        target_seen = "Verifying function '" + gate["target"] + "'" in raw
        good = (stage["exit"] == 0 and "0 errors found (" in raw if gate["positive"] else
                stage["exit"] in (1, 2) and error == ZST_ERRORS[name])
        good = bool(good and target_seen and before ==
                    (sha(fixture / "verified/lib.rs"), sha(fixture / "original/lib.rs")))
        rows[name] = {"classification": "EXPECTED_OBSERVED" if good else "INCONCLUSIVE",
                      "exit": stage["exit"], "first_error": error,
                      "target_seen": target_seen, "support": supported,
                      "source_pair_sha256": before, "log_sha256": stage["log_sha256"]}
        save(root / (name + ".json"), rows[name])
    for name in models.C_CONTROLS:
        ext = ".c" if name.startswith("c-") else ".cpp"
        fixture = prepared / "zst" / name
        path = fixture / (name + ext)
        before = sha(path)
        stage, raw = driver.stage(a, "zst-" + name + "-verification",
            [str(a.tool_home / "bin/verifast"), "-shared", path.name],
            fixture, isolated_env(driver), 180)
        good = (stage["exit"] == 0 and "0 errors found (" in raw and
                "1 statement" in raw and first_error(raw) is None and
                sha(path) == before)
        rows[name] = {"classification": "EXPECTED_OBSERVED" if good else "INCONCLUSIVE",
                      "exit": stage["exit"], "first_error": first_error(raw),
                      "source_sha256": before, "log_sha256": stage["log_sha256"],
                      "argv": ["-shared", path.name]}
        save(root / (name + ".json"), rows[name])
    return {"cases": rows, "all_expected_observed": all(
        row["classification"] == "EXPECTED_OBSERVED" for row in rows.values())}


def run(a, data):
    need(not a.evidence.exists(), "native result evidence already exists")
    a.evidence.mkdir(parents=True)
    need(str(a.tool_home.resolve()).startswith("/workspace/"), "tool outside workspace")
    prepared = a.evidence.parents[1] / "source-preparation/native"
    prep = json.loads((prepared / "prepared.json").read_text())
    need(prep["profile"] == data["native_zst_profile"] and
         prep["source_prepared_before_console_build"] is True, "prepared source identity")
    driver, _, models, _ = modules(a)
    driver.pin(SimpleNamespace(proof_root=a.proof_root, manifest=a.manifest,
                               tool_home=a.tool_home, evidence=a.evidence))
    bound = json.loads((a.proof_root / NATIVE / "NATIVE-C4-BOUND-MANIFEST.json").read_text())
    result = {"classification": "NATIVE_ZST_DIAGNOSTIC_INCOMPLETE",
              "profile": data["native_zst_profile"],
              "proof_sha": os.environ["PROOF_SHA"], "infra_sha": os.environ["INFRA_SHA"],
              "tool_sha256": sha(a.tool_home / "bin/verifast"),
              "tool_hashes": {key: sha(a.tool_home / key) for key in data["effective_hashes"]},
              "fresh_c4_controls": "NOT_RUN", "native_c1": "NOT_RUN",
              "native": "NOT_RUN", "zst": "NOT_RUN", "proof_credit": False,
              "profile_accepted": False, "actual_caller_proved": False}
    save(a.evidence / "result.json", result)
    result["fresh_c4_controls"] = fresh_c4_controls(a, driver, data)
    save(a.evidence / "result.json", result)
    result["native_c1"] = native_c1_cases(a, driver, prepared)
    save(a.evidence / "result.json", result)
    result["native"] = native_cases(a, driver, prepared, bound)
    save(a.evidence / "result.json", result)
    result["zst"] = model_cases(a, driver, models, prepared)
    result["classification"] = ("NATIVE_ZST_EXPECTED_OBSERVED_RAW_REVIEW_REQUIRED"
        if result["fresh_c4_controls"]["all_expected_observed"] and
           result["native_c1"]["all_expected_observed"] and
           result["native"]["all_expected_observed"] and
           result["zst"]["all_expected_observed"] else "NATIVE_ZST_DIAGNOSTIC_INCOMPLETE")
    save(a.evidence / "result.json", result)
    need(result["classification"] == "NATIVE_ZST_EXPECTED_OBSERVED_RAW_REVIEW_REQUIRED",
         "one or more fresh native/ZST gates inconclusive")


def resume_c_controls(a, data):
    """Supplement first Cloud evidence with only the C/C++ shared-library gates."""
    resume = data.get("supplemental_resume")
    need(isinstance(resume, dict) and resume.get("baseline_build_id") ==
         "47ee47d9-274b-4b13-84e2-167ba88ff770" and
         resume.get("baseline_proof_sha") == "03c2f4e134473253045d716a9779cc1b8530d0bb",
         "supplemental baseline identity")
    need(not a.evidence.exists(), "supplemental evidence already exists")
    a.evidence.mkdir(parents=True)
    prepared = a.evidence.parents[1] / "source-preparation/native"
    prep_path = prepared / "prepared.json"
    need(sha(prep_path) == resume["baseline_prepared_sha256"],
         "supplemental source preparation differs from baseline")
    prep = json.loads(prep_path.read_text())
    need(prep["profile"] == data["native_zst_profile"] and
         prep["source_prepared_before_console_build"] is True,
         "supplemental source preparation status")
    driver, _, models, _ = modules(a)
    driver.pin(SimpleNamespace(proof_root=a.proof_root, manifest=a.manifest,
                               tool_home=a.tool_home, evidence=a.evidence))
    binary_sha = sha(a.tool_home / "bin/verifast")
    need(binary_sha == resume["baseline_binary_sha256"],
         "supplemental binary differs from baseline")
    effective = {key: sha(a.tool_home / key) for key in data["effective_hashes"]}
    need(effective == data["effective_hashes"], "supplemental effective tree differs")
    need(set(models.C_CONTROLS) == set(resume["c_sources_sha256"]) ==
         {"c-nonempty", "cpp-empty"}, "supplemental case set")
    rows = {}
    result = {
        "classification": "SUPPLEMENTAL_C_CONTROLS_INCOMPLETE",
        "baseline_build_id": resume["baseline_build_id"],
        "baseline_proof_sha": resume["baseline_proof_sha"],
        "baseline_manifest_sha256": resume["baseline_manifest_sha256"],
        "baseline_native_result_sha256": resume["baseline_native_result_sha256"],
        "baseline_integration_result_sha256": resume["baseline_integration_result_sha256"],
        "baseline_audit_sha256": resume["baseline_audit_sha256"],
        "baseline_prepared_sha256": resume["baseline_prepared_sha256"],
        "current_proof_sha": os.environ["PROOF_SHA"],
        "current_infra_sha": os.environ["INFRA_SHA"],
        "tool_sha256": binary_sha, "effective_hashes": effective,
        "fresh_c4_controls": "BASELINE_RESULT_REFERENCE_ONLY",
        "native_c1": "BASELINE_RESULT_REFERENCE_ONLY",
        "native_c4": "BASELINE_RESULT_REFERENCE_ONLY",
        "rust_zst_models": "BASELINE_RESULT_REFERENCE_ONLY",
        "bool_composition": "BASELINE_RESULT_REFERENCE_ONLY",
        "cases": rows, "raw_review": "PENDING_INDEPENDENT_REVIEW",
        "accepted": False, "verification_accepted": False,
        "profile_accepted": False, "proof_credit": False,
    }
    save(a.evidence / "result.json", result)
    for name in ("c-nonempty", "cpp-empty"):
        ext = ".c" if name == "c-nonempty" else ".cpp"
        fixture = prepared / "zst" / name
        path = fixture / (name + ext)
        before = sha(path)
        need(before == prep["zst_controls"][name]["source_sha256"] ==
             resume["c_sources_sha256"][name], "supplemental C source differs")
        stage, raw = driver.stage(a, "supplemental-" + name + "-verification",
            [str(a.tool_home / "bin/verifast"), "-shared", path.name],
            fixture, isolated_env(driver), 180)
        good = (stage["exit"] == 0 and "0 errors found (" in raw and
                "1 statement" in raw and first_error(raw) is None and
                sha(path) == before)
        rows[name] = {"classification": "EXPECTED_OBSERVED" if good else "INCONCLUSIVE",
                      "exit": stage["exit"], "first_error": first_error(raw),
                      "source_sha256": before, "log_sha256": stage["log_sha256"],
                      "argv": ["-shared", path.name], "proof_credit": False}
        save(a.evidence / (name + ".json"), rows[name])
        save(a.evidence / "result.json", result)
    complete = all(row["classification"] == "EXPECTED_OBSERVED" for row in rows.values())
    result["classification"] = ("SUPPLEMENTAL_C_CONTROLS_EXPECTED_OBSERVED_RAW_REVIEW_REQUIRED"
        if complete else "SUPPLEMENTAL_C_CONTROLS_INCOMPLETE")
    save(a.evidence / "result.json", result)
    save(a.evidence.parents[1] / "proof-audit.json", {
        "classification": result["classification"], "supplemental_only": True,
        "baseline_build_id": resume["baseline_build_id"],
        "supplemental_result_sha256": sha(a.evidence / "result.json"),
        "other_gates": "BASELINE_RESULT_REFERENCE_ONLY",
        "raw_review": "PENDING_INDEPENDENT_REVIEW",
        "diagnostic_complete": False, "accepted": False,
        "verification_accepted": False, "profile_accepted": False,
        "proof_credit": False})
    need(complete, "supplemental C/C++ gates inconclusive")
    need(False, "supplemental raw review pending; no automatic proof credit")


def audit(a, data):
    integration = a.evidence.parents[1] / "cases/integration/result.json"
    native = a.evidence / "result.json"
    i = json.loads(integration.read_text()) if integration.is_file() else {}
    n = json.loads(native.read_text()) if native.is_file() else {}
    complete = (a.integration_exit == 0 and a.native_exit == 0 and
                i.get("diagnostic_complete") is True and
                n.get("classification") == "NATIVE_ZST_EXPECTED_OBSERVED_RAW_REVIEW_REQUIRED" and
                n.get("profile") == data["native_zst_profile"])
    result = {"classification": "FRESH_MERGED_DIAGNOSTIC_RAW_REVIEW_REQUIRED" if complete else
              "FRESH_MERGED_DIAGNOSTIC_INCOMPLETE",
              "diagnostic_complete": bool(complete), "accepted": False,
              "verification_accepted": False, "profile_accepted": False,
              "raw_review": "PENDING_INDEPENDENT_REVIEW",
              "integration_component_inherited_c4_rows": "HISTORICAL_C3_ONLY_NO_NEW_PROFILE_CREDIT",
              "new_profile_c4_credit_source": "cases/native-zst/fresh-c4-controls",
              "fresh_c4_controls_complete": isinstance(n.get("fresh_c4_controls"), dict) and
                  n["fresh_c4_controls"].get("all_expected_observed") is True,
              "integration_exit": a.integration_exit, "native_exit": a.native_exit,
              "integration_result_sha256": sha(integration) if integration.is_file() else None,
              "native_result_sha256": sha(native) if native.is_file() else None,
              "profile": data["native_zst_profile"], "proof_credit": False,
              "actual_sort4_proved": False, "actual_caller_proved": False}
    save(a.evidence.parents[1] / "proof-audit.json", result)
    need(complete, "combined diagnostic incomplete")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("source-prepare", "apply", "run", "resume-c", "audit"))
    parser.add_argument("--proof-root", required=True, type=Path)
    parser.add_argument("--cloud-dir", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--tool-home", type=Path)
    parser.add_argument("--compiler-sysroot", type=Path)
    parser.add_argument("--deadline-epoch", type=int)
    parser.add_argument("--integration-exit", type=int)
    parser.add_argument("--native-exit", type=int)
    a = parser.parse_args()
    for key in ("proof_root", "cloud_dir", "manifest", "evidence", "tool_home",
                "compiler_sysroot"):
        if getattr(a, key) is not None:
            setattr(a, key, getattr(a, key).resolve())
    data = context(a)
    if a.mode == "source-prepare":
        source_prepare(a, data)
    elif a.mode == "apply":
        need(a.tool_home is not None, "tool path")
        apply(a, data)
    elif a.mode == "run":
        need(a.tool_home is not None and a.compiler_sysroot is not None and
             a.deadline_epoch is not None, "run inputs")
        run(a, data)
    elif a.mode == "resume-c":
        need(a.tool_home is not None and a.deadline_epoch is not None,
             "supplemental run inputs")
        resume_c_controls(a, data)
    else:
        need(a.integration_exit is not None and a.native_exit is not None,
             "component exits")
        audit(a, data)


if __name__ == "__main__":
    main()
