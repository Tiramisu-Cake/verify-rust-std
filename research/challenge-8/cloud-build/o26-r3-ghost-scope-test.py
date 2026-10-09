#!/usr/bin/env python3
"""Cloud-only isolated R3 ghost-scope TEST and full-log diagnostic."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

TRANSLATOR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
PAIR = ("SORT4_R3_GHOST_SCOPE_TEST_REPO_ROOT", "SORT4_R3_GHOST_SCOPE_TEST")
MARKER = "R3-GHOST-SCOPE-TEST: retained two input lets; nested opens transferred"
OLD = "actual outer/nested ghost scope inventory"
PARTIAL = "R3 ghost-scope TEST partial or invalid opt-in"


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "R3 module missing")
    item = importlib.util.module_from_spec(spec)
    sys.modules[name] = item
    spec.loader.exec_module(item)
    return item


def run_proof(a, r3, case, tool, name, mode):
    need(not any(os.environ.get(key) for key in PAIR), "inherited scope opt-in")
    if mode in ("partial", "on"):
        os.environ[PAIR[0]] = str(a.proof_root)
    if mode == "on":
        os.environ[PAIR[1]] = "1"
    try:
        stage = r3.proof_stage(a, case, tool, name, True)
    finally:
        for key in PAIR:
            os.environ.pop(key, None)
    log = (case / (name + ".log")).read_text(errors="replace")
    print("R3 GHOST SCOPE FULL LOG BEGIN " + name, flush=True)
    print(log, end="" if log.endswith("\n") else "\n", flush=True)
    print("R3 GHOST SCOPE FULL LOG END " + name, flush=True)
    write(a.evidence / (name + "-stage.json"), stage)
    need(stage.get("status") == "RAN" and
         stage.get("exit") not in (None, 124, 137) and
         stage.get("source_unchanged") is True and
         stage.get("source_before") == stage.get("source_after") and
         stage.get("intrinsic_gate_active") is True and
         stage.get("pointer_drop_gate_active") is True,
         name + ": full source/profile proof stage incomplete")
    return stage, log


def snapshots_equal_except_console_translator(before, after, changed):
    need(before["head"] == after["head"] and
         before["effective_rsspec_sha256"] == after["effective_rsspec_sha256"] and
         before["proof_std_sha256"] == after["proof_std_sha256"],
         "R3 scope TEST kernel/spec/source identity differs")
    for field, exception in (("critical_source_sha256", str(TRANSLATOR)),
                             ("modified_tracked_source_sha256", str(TRANSLATOR)),
                             ("binary_sha256", "bin/verifast")):
        need(set(before[field]) == set(after[field]) and
             all(before[field][key] == after[field][key]
                 for key in before[field] if key != exception),
             "R3 scope TEST changed another tracked source or binary")
    need(after["critical_source_sha256"][str(TRANSLATOR)] == changed and
         after["modified_tracked_source_sha256"][str(TRANSLATOR)] == changed and
         before["binary_sha256"]["bin/verifast"] !=
         after["binary_sha256"]["bin/verifast"],
         "R3 scope TEST translator/console delta differs")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("r3-source", "r3-evidence", "compiler-sysroot", "evidence",
                "proof-root", "work-root", "cloud-dir", "deadline-epoch"):
        p.add_argument("--" + key, required=True)
    a = p.parse_args()
    for key in ("r3_source", "r3_evidence", "compiler_sysroot", "evidence",
                "proof_root", "work_root", "cloud_dir"):
        value = Path(getattr(a, key)).resolve()
        need(value.is_relative_to(Path("/workspace")), "Cloud workspace path required")
        setattr(a, key, value)
    a.deadline_epoch = int(a.deadline_epoch)
    a.schema = a.r3_source / "src/rust_frontend/vf_mir/vf_mir.capnp"
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") == "o26-r3-ghost-scope-test" and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud R3 TEST lane required")
    need(not a.evidence.exists(), "R3 TEST evidence already exists")
    a.evidence.mkdir(parents=True)
    result = {"classification": "INCONCLUSIVE", "diagnostic_complete": False,
              "accepted": False, "verification_accepted": False,
              "actual_nested_drop_credit": False, "actual_helper_proved": False}
    try:
        proof = a.proof_root / "research/challenge-8/overnight-assume-actual"
        m = read(proof / "O26-R3-GHOST-SCOPE-TEST.json")
        parent = read(proof / "O26-WRAPPER-INPUT-RELATION-PROFILE.json")
        patch = proof / "verifast-r3-ghost-scope-TEST.patch"
        need(m.get("classification") ==
             "EXPERIMENTAL_O26_R3_GHOST_SCOPE_TEST_NOT_ACCEPTED" and
             m["test_patch_sha256"] == sha(patch) and
             m["source"]["verified_sha256"] == parent["source"]["verified_sha256"] and
             m["source"]["unit_sha256"] == parent["source"]["unit_sha256"],
             "R3 scope TEST manifest/patch/source pins differ")
        r3 = module("r3_scope_profile", a.cloud_dir / "o26-r3-profile.py")
        r2 = module("r3_scope_snapshot", a.cloud_dir / "o26-wrapper-profile.py")
        original = read(a.r3_evidence / "capture-check.json")
        a.evidence, scope_evidence = a.r3_evidence, a.evidence
        checked = r3.capture_check(a, parent)
        a.evidence = scope_evidence
        need(checked == original and
             checked.get("all_nine_body_records_and_ten_marshal_files_hashed") is True and
             checked.get("typed_outer_mir_exact") is True,
             "R3 source/MIR/refinement capture differs")
        case = a.r3_evidence / "capture" / r3.CASE
        before = r2.tool_snapshot(a.r3_source, a.proof_root)
        need(sha(a.r3_source / TRANSLATOR) == m["parent_translator_sha256"],
             "R3 parent translator changed")
        test = a.work_root / "r3-ghost-scope-test-tool"
        need(not test.exists() and not test.is_relative_to(a.evidence.parents[2]),
             "R3 TEST tool must be fresh and outside evidence")
        shutil.copytree(a.r3_source, test, symlinks=True)
        subprocess.run(("git", "-C", str(test), "apply", "--check", str(patch)), check=True)
        subprocess.run(("git", "-C", str(test), "apply", str(patch)), check=True)
        need(sha(test / TRANSLATOR) == m["test_translator_sha256"],
             "R3 TEST translator hash differs")
        (test / "bin/verifast").unlink()
        timeout = a.deadline_epoch - int(time.time()) - 25
        need(timeout > 0, "R3 TEST build deadline")
        with (a.evidence / "test-console-build.log").open("wb") as log:
            build = subprocess.run(("make", "-C", str(test / "src"),
                "../bin/verifast", "WITHOUT_LABLGTK=yes", "VERBOSE=yes"),
                stdout=log, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        need(build.returncode == 0 and (test / "bin/verifast").is_file(),
             "R3 TEST console build failed")
        after = r2.tool_snapshot(test, a.proof_root)
        need(r2.tool_snapshot(a.r3_source, a.proof_root) == before,
             "R3 production tool changed")
        snapshots_equal_except_console_translator(before, after,
            m["test_translator_sha256"])
        write(a.evidence / "tool-identity.json", {"production": before,
             "test": after, "patch_sha256": sha(patch), "accepted": False})
        off, off_log = run_proof(a, r3, case, test, "r3-ghost-scope-off", "off")
        need(off["exit"] == 2 and
             re.findall(r"(?m)^Fatal error:.*$",off_log)==[
                 'Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: certificate mismatch: ' + OLD + '")'] and
             "Verifying function '" not in off_log and MARKER not in off_log,
             "default-off did not retain old scope inventory refusal")
        partial, partial_log = run_proof(a, r3, case, test,
                                        "r3-ghost-scope-partial", "partial")
        need(partial["exit"] == 2 and
             re.findall(r"(?m)^Fatal error:.*$",partial_log)==[
                 'Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: certificate mismatch: ' + PARTIAL + '")'] and
             "Verifying function '" not in partial_log and
             MARKER not in partial_log, "partial TEST pair was not rejected")
        on, on_log = run_proof(a, r3, case, test, "r3-ghost-scope-on", "on")
        need(on_log.count(MARKER)==1 and OLD not in on_log,
             "enabled TEST did not reach reviewed scope transfer")
        need(r2.tool_snapshot(a.r3_source, a.proof_root) == before and
             r2.tool_snapshot(test, a.proof_root) == after,
             "R3 TEST source/tool changed during proof controls")
        result.update({"classification": "R3_GHOST_SCOPE_TEST_DIAGNOSTIC_COMPLETE",
                       "diagnostic_complete": True,
                       "r3_capture_rechecked": True, "tool_identity_rechecked": True,
                       "default_off_refusal": True, "partial_pair_refusal": True,
                       "enabled_scope_marker": True, "enabled_full_exit": on["exit"],
                       "enabled_full_exit_zero": on["exit"] == 0,
                       "first_enabled_error": next((line for line in on_log.splitlines()
                           if re.search(r": error: |^Fatal error:", line)), None)})
    except Exception as exc:
        result["reason"] = str(exc)
    write(a.evidence / "diagnostic-audit.json", result)
    if not result["diagnostic_complete"]:
        raise SystemExit("R3 ghost-scope TEST inconclusive: " + result["reason"])


if __name__ == "__main__":
    main()
