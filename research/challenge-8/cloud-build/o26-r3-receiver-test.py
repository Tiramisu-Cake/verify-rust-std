#!/usr/bin/env python3
"""Cloud-only nested R3 receiver TEST; diagnostic with no theorem credit."""
import hashlib
import json
import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

PATCH_REL = Path("research/challenge-8/overnight-assume-actual/verifast-r3-receiver-TEST.patch")
PAIR = ("SORT4_R3_RECEIVER_TEST_REPO_ROOT", "SORT4_R3_RECEIVER_TEST")
SCOPE_PAIR = ("SORT4_R3_GHOST_SCOPE_TEST_REPO_ROOT", "SORT4_R3_GHOST_SCOPE_TEST")
MARKER = "R3-RECEIVER-TEST: accepted NORMAL receiver"
SCOPE_MARKER = "R3-GHOST-SCOPE-TEST: retained two input lets; nested opens transferred"
FATAL = 'Fatal error: exception Failure("SORT4-AS-MUT-PTR: certificate mismatch: actual external receiver operand/binding")'
TRANSLATOR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def run(a, r3, r2, case, scope_tool, scope_snapshot):
    """Run nested controls after the scope helper has completed its on control."""
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") == "o26-r3-ghost-scope-test" and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud R3 receiver TEST lane required")
    need(not any(os.environ.get(k) for k in (*SCOPE_PAIR, *PAIR)),
         "inherited scope/receiver TEST opt-in")
    e = a.evidence / "r3-receiver-test"
    need(not e.exists(), "receiver TEST evidence already exists")
    e.mkdir()
    result = {"classification": "INCONCLUSIVE", "diagnostic_complete": False,
              "actual_source_accepted": False, "target_contract_proved": False,
              "verification_accepted": False, "accepted": False,
              "malformed_place_admissibility_complete": False}
    m = read(a.proof_root / "research/challenge-8/overnight-assume-actual/O26-R3-RECEIVER-TEST.json")
    patch = a.proof_root / PATCH_REL
    need(m["classification"] == "EXPERIMENTAL_O26_R3_RECEIVER_TEST_NOT_ACCEPTED" and
         sha(patch) == m["test_patch_sha256"] and
         m["parent_translator_sha256"] == "ed8ee5ed8a7f8abb7d9c7cee3a978059b55c0a02e34f908170a80d6cc3ed4102" and
         m["source"] == {"verified_sha256": "a95aff14592b167c62c53c7ed726128ee86c7c19768cfe613504cdec841f8463",
                         "unit_sha256": "407acbaea262ba908ed88434231e9fce1128678840f5d929deaad71838290a92"},
         "receiver manifest/patch/source pins differ")
    need(sha(scope_tool / TRANSLATOR) == m["parent_translator_sha256"],
         "completed scope tool is not the exact receiver patch parent")
    parent_snapshot = r2.tool_snapshot(a.r3_source, a.proof_root)
    need(r2.tool_snapshot(scope_tool, a.proof_root) == scope_snapshot,
         "scope tool changed after its completed controls")
    configs = [("on", None), ("wrong-first", "_11"), ("wrong-second", "_13")]
    all_stages = {}
    receiver_on_tool = None
    receiver_on_snapshot = None
    for name, wrong in configs:
        tool = a.work_root / ("r3-receiver-" + name + "-tool")
        need(not tool.exists() and not tool.is_relative_to(e), "receiver tool copy must be fresh/outside evidence")
        shutil.copytree(scope_tool, tool, symlinks=True)
        if name == "on":
            subprocess.run(("git", "-C", str(tool), "apply", "--check", str(patch)), check=True)
            subprocess.run(("git", "-C", str(tool), "apply", str(patch)), check=True)
            expected_hash = m["test_translator_sha256"]
            patch_hash = sha(patch)
        else:
            source = (a.work_root / "r3-receiver-on-tool" / TRANSLATOR).read_text()
            mutant = source.replace(f'if receiver_test_requested then "{wrong}"',
                                    f'if receiver_test_requested then "_WRONG_{wrong}"', 1)
            need(mutant != source, name + " mutation target missing")
            target = tool / TRANSLATOR
            target.write_text(mutant)
            negpatch = e / (name + ".patch")
            diff = subprocess.run(("diff", "-u", str(a.work_root / "r3-receiver-on-tool" / TRANSLATOR), str(target)),
                                  capture_output=True, text=True).stdout.splitlines()
            diff[0] = "--- a/" + str(TRANSLATOR)
            diff[1] = "+++ b/" + str(TRANSLATOR)
            negpatch.write_text("\n".join(diff) + "\n")
            expected_hash = sha(target)
            patch_hash = sha(negpatch)
        need(sha(tool / TRANSLATOR) == expected_hash, name + " translator hash mismatch")
        (tool / "bin/verifast").unlink()
        timeout = a.deadline_epoch - int(time.time()) - 25
        need(timeout > 0, "receiver TEST build deadline")
        with (e / (name + "-console-build.log")).open("wb") as log:
            build = subprocess.run(("make", "-C", str(tool / "src"), "../bin/verifast",
                                    "WITHOUT_LABLGTK=yes", "VERBOSE=yes"),
                                   stdout=log, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        need(build.returncode == 0 and (tool / "bin/verifast").is_file(), name + " console build failed")
        snapshot = r2.tool_snapshot(tool, a.proof_root)
        for field in ("head", "effective_rsspec_sha256", "proof_std_sha256"):
            need(snapshot[field] == scope_snapshot[field], name + " changed frozen " + field)
        for field in ("critical_source_sha256", "modified_tracked_source_sha256"):
            need(set(snapshot[field]) == set(scope_snapshot[field]),
                 name + " source snapshot key set changed")
            for key, value in scope_snapshot[field].items():
                if key != str(TRANSLATOR):
                    need(snapshot[field][key] == value,
                         name + " changed non-translator source " + key)
        need(set(snapshot["binary_sha256"]) == set(scope_snapshot["binary_sha256"]),
             name + " binary snapshot key set changed")
        for key, value in scope_snapshot["binary_sha256"].items():
            if key != "bin/verifast":
                need(snapshot["binary_sha256"][key] == value,
                     name + " changed binary " + key)
        need(snapshot["critical_source_sha256"][str(TRANSLATOR)] == expected_hash and
             snapshot["binary_sha256"]["bin/verifast"] != scope_snapshot["binary_sha256"]["bin/verifast"],
             name + " translator/console snapshot mismatch")
        write(e / (name + "-tool-identity.json"), {"parent": scope_snapshot,
              "candidate": snapshot, "patch_sha256": patch_hash, "accepted": False})
        if name == "on":
            receiver_on_tool, receiver_on_snapshot = tool, snapshot
        if name == "on":
            modes = [("off", False), ("partial", "partial"), ("on", True)]
        else:
            modes = [("negative", True)]
        for mode, admitted in modes:
            need(not any(os.environ.get(k) for k in (*SCOPE_PAIR, *PAIR)),
                 "scope/receiver TEST opt-in leaked")
            os.environ[SCOPE_PAIR[0]] = str(a.proof_root)
            os.environ[SCOPE_PAIR[1]] = "1"
            if mode == "partial":
                os.environ[PAIR[0]] = str(a.proof_root)
            elif mode == "on" or mode == "negative":
                os.environ[PAIR[0]] = str(a.proof_root)
                os.environ[PAIR[1]] = "1"
            try:
                stage_name = "r3-receiver-" + name + ("-" + mode if name == "on" else "")
                stage = r3.proof_stage(a, case, tool, stage_name, True)
            finally:
                for key in (*SCOPE_PAIR, *PAIR):
                    os.environ.pop(key, None)
            logname = "r3-receiver-" + name + ("-" + mode if name == "on" else "")
            log = (case / (logname + ".log")).read_text(errors="replace")
            print("R3 RECEIVER FULL LOG BEGIN " + logname, flush=True)
            print(log, end="" if log.endswith("\n") else "\n", flush=True)
            print("R3 RECEIVER FULL LOG END " + logname, flush=True)
            write(e / (logname + "-stage.json"), stage)
            (e / (logname + ".log")).write_text(log)
            need(stage.get("status") == "RAN" and
                 stage.get("exit") not in (None, 124, 137) and
                 stage.get("source_unchanged") is True and
                 stage.get("source_before") == stage.get("source_after") and
                 stage.get("source_before", {}).get("verified/lib.rs") == m["source"]["verified_sha256"] and
                 stage.get("source_before", {}).get("original/lib.rs") == "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5" and
                 stage.get("intrinsic_gate_active") is True and stage.get("pointer_drop_gate_active") is True,
                 logname + " full proof stage incomplete")
            fatals = [line for line in log.splitlines() if line.startswith("Fatal error:")]
            need(SCOPE_MARKER in log, logname + " did not retain exact scope admission")
            if name == "on" and mode == "off":
                need(stage.get("exit") == 2 and fatals == [FATAL] and MARKER not in log and
                     "Verifying function '" not in log, "receiver off control missed frozen refusal")
            elif name == "on" and mode == "partial":
                expected = 'Fatal error: exception Failure("SORT4-AS-MUT-PTR: certificate mismatch: R3 receiver TEST partial or invalid opt-in")'
                need(stage.get("exit") == 2 and fatals == [expected] and MARKER not in log and
                     "Verifying function '" not in log, "receiver partial pair not rejected")
            elif name == "on" and mode == "on":
                need(log.count(MARKER + " _11") == 1 and log.count(MARKER + " _13") == 1 and
                     log.index(MARKER + " _11") < log.index(MARKER + " _13"),
                     "receiver-on did not emit both exact markers")
                result.update({"receiver_on_full_exit": stage.get("exit"),
                               "receiver_on_first_error": next((x for x in log.splitlines() if ": error: " in x or x.startswith("Fatal error:") or x.startswith("Error:")), None)})
            else:
                need(stage.get("exit") == 2 and fatals == [FATAL] and
                     log.count(MARKER + " _11") == (1 if wrong == "_13" else 0) and
                     MARKER + " _13" not in log,
                     name + " negative did not fail at exact intended receiver predicate")
            all_stages[logname] = {"exit": stage.get("exit"), "fatal": fatals,
                                   "patch_sha256": patch_hash,
                                   "log_sha256": hashlib.sha256(log.encode()).hexdigest(),
                                   "console_sha256": snapshot["binary_sha256"]["bin/verifast"],
                                   "console_build_log_sha256": sha(e / (name + "-console-build.log")),
                                   "accepted": False}
    need(r2.tool_snapshot(a.r3_source, a.proof_root) == parent_snapshot and
         r2.tool_snapshot(scope_tool, a.proof_root) == scope_snapshot,
         "receiver TEST mutated production or parent scope tool")
    column_flag = os.environ.get("O26_WITH_R3_GHOST_COLUMN_TEST", "0")
    nested_flag = os.environ.get("O26_WITH_R3_COLUMN_NESTED_TEST", "0")
    need(column_flag in ("0", "1") and nested_flag in ("0", "1") and
         (nested_flag == "0" or column_flag == "1"),
         "invalid/missing parent ghost-column/nested runner flag")
    column_result = None
    if column_flag == "1":
        column_helper = importlib.util.spec_from_file_location(
            "r3_ghost_column_diagnostic", a.cloud_dir / "o26-r3-ghost-column-test.py")
        need(column_helper is not None and column_helper.loader is not None,
             "ghost-column helper unavailable")
        column_module = importlib.util.module_from_spec(column_helper)
        import sys
        sys.modules[column_helper.name] = column_module
        column_helper.loader.exec_module(column_module)
        column_result = column_module.run(a, r2, r3, case, receiver_on_tool,
                                          receiver_on_snapshot)
        need(column_result.get("diagnostic_complete") is True and
             column_result.get("accepted") is False and
             column_result.get("verification_accepted") is False,
             "requested ghost-column TEST controls incomplete")
    result.update({"classification": "R3_RECEIVER_TEST_DIAGNOSTIC_COMPLETE",
                   "diagnostic_complete": True, "exact_scope_parent": True,
                   "ghost_column_test_requested": column_flag == "1",
                   "ghost_column_test": column_result,
                   "nested_scheduler_test_requested": nested_flag == "1",
                   "nested_scheduler_test": (column_result.get("nested_scheduler_test")
                       if column_result else None),
                   "default_off_refusal": True, "partial_pair_refusal": True,
                   "receiver_on_markers": True, "wrong_first_receiver_negative": True,
                   "wrong_second_receiver_negative": True, "malformed_place_admissibility_complete": False,
                   "stages": all_stages, "accepted": False, "verification_accepted": False,
                   "actual_source_accepted": False, "target_contract_proved": False})
    write(e / "diagnostic-audit.json", result)
    return result
