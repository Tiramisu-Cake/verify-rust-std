#!/usr/bin/env python3
"""Cloud-only source-linked R3 ghost-column and nested-order TESTs."""
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

ROOT = Path("research/challenge-8")
TRANSLATOR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
COLUMN_PAIR = ("SORT4_R3_GHOST_COLUMN_TEST_REPO_ROOT", "SORT4_R3_GHOST_COLUMN_TEST")
NESTED_PAIR = ("SORT4_R3_COLUMN_NESTED_TEST_REPO_ROOT", "SORT4_R3_COLUMN_NESTED_TEST")
SCOPE_PAIR = ("SORT4_R3_GHOST_SCOPE_TEST_REPO_ROOT", "SORT4_R3_GHOST_SCOPE_TEST")
RECEIVER_PAIR = ("SORT4_R3_RECEIVER_TEST_REPO_ROOT", "SORT4_R3_RECEIVER_TEST")
INPUT_PAIR = ("SORT4_WRAPPER_INPUT_RELATION_REPO_ROOT", "SORT4_WRAPPER_INPUT_RELATION_ADMISSION")
REBASE_PAIR = ("SORT4_WRAPPER_REBASE_REPO_ROOT", "SORT4_WRAPPER_REBASE_ADMISSION")
PARENT = "7451dee6edcd63a4151eb45816a882f51107c7f096b047762cc482b154f61fd6"
SOURCE = "a95aff14592b167c62c53c7ed726128ee86c7c19768cfe613504cdec841f8463"
ORIGINAL = "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5"
UNIT = "407acbaea262ba908ed88434231e9fce1128678840f5d929deaad71838290a92"
OUTER = "f8374652a11e36073ad6ed10ec39b0f8de62da53265dd80d2dc2c3565491cee1"
COLUMN_MARK = "R3-GHOST-COLUMN-TEST:"
RECEIVER_MARK = "R3-RECEIVER-TEST: accepted NORMAL receiver"
SCOPE_MARK = "R3-GHOST-SCOPE-TEST: retained two input lets; nested opens transferred"
HIDE_ERROR = "Declaration hides existing local variable 'saved_true_input'."
COLUMN_FATAL = 'Fatal error: exception Failure("SORT4-AS-MUT-PTR: certificate mismatch: R3 ghost-column TEST partial or invalid opt-in")'
ROUTE_FATAL = 'Fatal error: exception Failure("SORT4-AS-MUT-PTR: certificate mismatch: R3 ghost-column TEST exact one-to-one ordered route")'
CANDIDATE_FATAL = 'Fatal error: exception Failure("SORT4-AS-MUT-PTR: certificate mismatch: R3 ghost-column TEST exact two distinct AST candidates")'
NESTED_MARK = "SORT4-R3-NESTED-BEFORE-OUTER-TEST:"
NESTED_FATAL = 'Fatal error: exception Failure("SORT4-R3-NESTED-BEFORE-OUTER-TEST: certificate mismatch: exact root/test opt-in pair")'
NESTED_BAD_ORDER = 'Fatal error: exception Failure("SORT4-R3-NESTED-BEFORE-OUTER-TEST: certificate mismatch: exact qualified key inventory")'
NAMES = (
    "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new",
    "sort4_checked_as_mut_ptr", "sort4_checked_pointer_drop",
    "sort4_checked_generic_drop", "checked_transmute_neo_pointer",
    "checked_assume_init_pointer", "checked_forget_owned",
    "select_unpredictable",
    "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop",
)
ERROR = re.compile(r"(?m)^.*: error: .*|^Error:.*$|^Fatal error:.*$")
ROW = re.compile(re.escape(NESTED_MARK) +
                 r" (before|after)\[(\d+)\] body_name=(.*?) module=(.*?) fn=(.*?) type=FuncBody loc=(\S+) ast_sha256=([0-9a-f]{64})")
SUMMARY_RE = re.compile(re.escape("exact nine-body one-item permutation") +
                 r", signatures=(\d+) signatures_sha256_before=([0-9a-f]{64}) signatures_sha256_after=([0-9a-f]{64})")
SUMMARY = "exact nine-body one-item permutation"


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def inventory(text):
    rows = {"before": {}, "after": {}}
    for phase, number, body_name, module, name, loc, digest in ROW.findall(text):
        index = int(number)
        need(index in range(9) and index not in rows[phase],
             "duplicate or out-of-range AST declaration inventory")
        rows[phase][index] = (body_name, module, name, loc, digest)
    summary = SUMMARY_RE.findall(text)
    need(len(summary) == 1 and summary[0][0] == "3" and
         summary[0][1] == summary[0][2] and
         all(set(rows[k]) == set(range(9)) for k in rows) and
         [rows["before"][i][0] for i in range(9)] == list(NAMES) and
         [rows["after"][i][0] for i in range(9)] ==
         list(NAMES[:7]) + [NAMES[8], NAMES[7]] and
         sorted(rows["before"].values()) == sorted(rows["after"].values()),
         "R3 AST function/signature permutation certificate incomplete")
    return {"rows": rows, "signature_count": 3,
            "signature_ast_sha256_before": summary[0][1],
            "signature_ast_sha256_after": summary[0][2],
            "exact_one_item_multiset": True}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "R3 column module unavailable")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def build_copy(a, parent_tool, name, patch_path, expected_translator,
               parent_snapshot, mutate=None):
    tool = a.work_root / ("r3-column-" + name + "-tool")
    need(not tool.exists() and not tool.is_relative_to(a.evidence),
         name + " tool must be a fresh copy outside evidence")
    shutil.copytree(parent_tool, tool, symlinks=True)
    target = tool / TRANSLATOR
    if mutate is None:
        subprocess.run(("git", "-C", str(tool), "apply", "--check", str(patch_path)), check=True)
        subprocess.run(("git", "-C", str(tool), "apply", str(patch_path)), check=True)
        patch_hash = sha(patch_path)
    else:
        before = target.read_text()
        after = mutate(before)
        need(after != before, name + " mutation target absent")
        target.write_text(after)
        diff = subprocess.run(("diff", "-u", str(parent_tool / TRANSLATOR), str(target)),
                              capture_output=True, text=True).stdout.splitlines()
        need(len(diff) >= 3, name + " mutation diff absent")
        diff[0] = "--- a/" + str(TRANSLATOR)
        diff[1] = "+++ b/" + str(TRANSLATOR)
        mutation_patch = a.evidence / (name + ".patch")
        mutation_patch.write_text("\n".join(diff) + "\n")
        patch_hash = sha(mutation_patch)
    expected_hash = expected_translator if mutate is None else sha(target)
    need(sha(target) == expected_hash, name + " translator identity mismatch")
    (tool / "bin/verifast").unlink()
    timeout = a.deadline_epoch - int(time.time()) - 25
    need(timeout > 0, name + " build deadline")
    with (a.evidence / (name + "-console-build.log")).open("wb") as out:
        built = subprocess.run(("make", "-C", str(tool / "src"), "../bin/verifast",
                                "WITHOUT_LABLGTK=yes", "VERBOSE=yes"),
                               stdout=out, stderr=subprocess.STDOUT,
                               timeout=timeout, check=False)
    need(built.returncode == 0 and (tool / "bin/verifast").is_file(), name + " build failed")
    return tool, patch_hash


def verify_snapshot(r2, a, parent, tool, expected_translator, name):
    snap = r2.tool_snapshot(tool, a.proof_root)
    for key in ("head", "effective_rsspec_sha256", "proof_std_sha256"):
        need(snap[key] == parent[key], name + " changed " + key)
    for field in ("critical_source_sha256", "modified_tracked_source_sha256", "binary_sha256"):
        need(set(snap[field]) == set(parent[field]), name + " snapshot keys changed: " + field)
        exception = "bin/verifast" if field == "binary_sha256" else str(TRANSLATOR)
        for key, value in parent[field].items():
            if key != exception:
                need(snap[field][key] == value, name + " changed frozen " + field + ":" + key)
    need(snap["critical_source_sha256"][str(TRANSLATOR)] == expected_translator and
         snap["modified_tracked_source_sha256"][str(TRANSLATOR)] == expected_translator and
         snap["binary_sha256"]["bin/verifast"] != parent["binary_sha256"]["bin/verifast"],
         name + " translator/console delta mismatch")
    return snap


def run_stage(a, r3, case, tool, name, own_pair, mode):
    pairs = (SCOPE_PAIR, RECEIVER_PAIR, COLUMN_PAIR)
    need(not any(os.environ.get(k) for pair in (*pairs, NESTED_PAIR) for k in pair),
         "inherited R3 TEST pair")
    for pair in (SCOPE_PAIR, RECEIVER_PAIR):
        os.environ[pair[0]] = str(a.proof_root)
        os.environ[pair[1]] = "1"
    # Nested scheduler is always parented by COLUMN-on; the column controls
    # themselves set this pair only for their enabled/fault cases.
    if name.startswith("nested-"):
        os.environ[COLUMN_PAIR[0]] = str(a.proof_root)
        os.environ[COLUMN_PAIR[1]] = "1"
    if own_pair is not None:
        os.environ[own_pair[0]] = str(a.proof_root)
        if mode != "partial":
            os.environ[own_pair[1]] = "1"
    try:
        stage = r3.proof_stage(a, case, tool, name, True)
    finally:
        for pair in (*pairs, NESTED_PAIR):
            for key in pair:
                os.environ.pop(key, None)
    log = (case / (name + ".log")).read_text(errors="replace")
    return stage, log


def tool_and_stage_identity(r2, a, parent_tool, parent_snapshot, tool, name,
                            expected_translator, patch_sha):
    snap = verify_snapshot(r2, a, parent_snapshot, tool, expected_translator, name)
    write(a.evidence / (name + "-tool-identity.json"),
          {"parent": parent_snapshot, "candidate": snap,
           "patch_sha256": patch_sha, "accepted": False})
    return snap


def schedule(a, r2, r3, case, column_tool, column_snapshot, m_column, column_on_log, column_on_stage):
    e = a.evidence / "nested-scheduler"
    e.mkdir()
    manifest_path = a.proof_root / ROOT / "overnight-assume-actual/O26-R3-COLUMN-NESTED-TEST.json"
    manifest = read(manifest_path)
    patch = a.proof_root / ROOT / manifest["test_patch"]
    need(manifest["parent_translator_sha256"] == m_column["test_translator_sha256"] and
         sha(patch) == manifest["test_patch_sha256"] and
         manifest["source"]["verified_sha256"] == SOURCE and
         manifest["source"]["unit_sha256"] == UNIT and
         manifest["source"]["nested_body8_sha256"] ==
             "e0508d6cfb436bc1bcd04737ad74e37b357d17e9ec3c2a226ee961f7036eae9a",
         "nested scheduler manifest/parent/source pins differ")
    on_tool, patch_hash = build_copy(a, column_tool, "nested-on", patch,
                                    manifest["test_translator_sha256"], column_snapshot)
    on_snapshot = tool_and_stage_identity(r2, a, column_tool, column_snapshot,
                                         on_tool, "nested-on", manifest["test_translator_sha256"], patch_hash)
    bad_tool, bad_patch_hash = build_copy(a, on_tool, "nested-wrong-permutation", patch,
        manifest["test_translator_sha256"], on_snapshot,
        lambda s: s.replace("[a;b;c;d;e;f;g;nested;outer]",
                            "[a;b;c;d;e;f;g;outer;nested]", 1))
    bad_snapshot = tool_and_stage_identity(r2, a, on_tool, on_snapshot, bad_tool,
        "nested-wrong-permutation", sha(bad_tool / TRANSLATOR), bad_patch_hash)
    stages = {}
    for name, tool, snap, own_pair, mode in (
        ("nested-off", on_tool, on_snapshot, None, "off"),
        ("nested-partial", on_tool, on_snapshot, NESTED_PAIR, "partial"),
        ("nested-on", on_tool, on_snapshot, NESTED_PAIR, "on"),
        ("nested-wrong-permutation", bad_tool, bad_snapshot, NESTED_PAIR, "on"),
    ):
        stage, log = run_stage(a, r3, case, tool, name, own_pair, mode)
        need(stage.get("status") == "RAN" and stage.get("exit") not in (None,124,137) and
             stage.get("source_unchanged") is True and stage.get("source_before")==stage.get("source_after") and
             stage.get("source_before", {}).get("verified/lib.rs") == SOURCE and
             stage.get("source_before", {}).get("original/lib.rs") == ORIGINAL and
             stage.get("intrinsic_gate_active") is True and stage.get("pointer_drop_gate_active") is True,
             name + " full proof stage incomplete")
        (e / (name + ".log")).write_text(log)
        print("R3 NESTED FULL LOG BEGIN " + name, flush=True)
        print(log, end="" if log.endswith("\n") else "\n", flush=True)
        print("R3 NESTED FULL LOG END " + name, flush=True)
        write(e / (name + "-stage.json"), stage)
        fatals = [x for x in log.splitlines() if x.startswith("Fatal error:")]
        if name == "nested-off":
            need(COLUMN_MARK in log and RECEIVER_MARK in log and SCOPE_MARK in log,
                 "nested-off lost inherited parent admissions")
            first_error = next((x for x in ERROR.findall(log)), None)
            column_first_error = next((x for x in ERROR.findall(column_on_log)), None)
            outer_header = log.find("Verifying function '" + NAMES[7] + "'")
            nested_header = log.find("Verifying function '" + NAMES[8] + "'")
            need(NESTED_MARK not in log and stage.get("exit") == column_on_stage.get("exit") and
                 first_error == column_first_error and
                 (outer_header < 0 or nested_header < 0 or outer_header < nested_header),
                 "nested-off differs from COLUMN-on lexical schedule/error")
        elif name == "nested-partial":
            need(fatals == [NESTED_FATAL] and "Verifying function '" not in log,
                 "nested partial pair did not fail preheaders")
        elif name == "nested-wrong-permutation":
            need(fatals == [NESTED_BAD_ORDER] and COLUMN_MARK in log and
                 RECEIVER_MARK in log and SCOPE_MARK in log,
                 "wrong nested permutation missed exact inventory gate")
        else:
            headers = [log.find("Verifying function '" + n + "'") for n in NAMES]
            prefix_headers = headers[:7]
            nested = headers[8]
            outer = headers[7]
            need(all(x >= 0 for x in prefix_headers) and
                 prefix_headers == sorted(prefix_headers) and nested > prefix_headers[-1],
                 "nested-on did not prove seven prefix bodies then actual nested body")
            audited_inventory = inventory(log)
            expected_locs = ["18:5", "33:1", "49:1", "65:1", "82:1",
                "100:1", "121:1", "135:1", "165:9"]
            before = audited_inventory["rows"]["before"]
            after = audited_inventory["rows"]["after"]
            need(all(before[i][3].endswith(":" + expected_locs[i]) for i in range(9)) and
                 [after[i][3].split(":")[-2:] for i in range(9)] ==
                    [loc.split(":") for loc in expected_locs[:7] + [expected_locs[8], expected_locs[7]]],
                 "nested AST full source locations changed")
            nested_text = log[nested:outer] if outer > nested else log[nested:]
            counts = {k: nested_text.count(k) for k in
                      ("Executing return statement", "Leak check.",
                       "Consuming function lifetime token", "Freeing locals.")}
            nested_errors = [x for x in ERROR.findall(nested_text)]
            need(ERROR.search(log[:nested]) is None,
                 "nested proof had an unrelated prefix error before its header")
            need(outer > nested or
                 (outer < 0 and stage.get("exit") not in (None, 0) and bool(nested_errors)),
                 "nested proof ended before outer without a located nested proof error")
            result_nested_body = outer > nested and all(v == 2 for v in counts.values()) and \
                "verified/lib.rs(169,33-48): Verifying call" in nested_text and not nested_errors
            result = {"nested_body_full_normal_unwind_log_observed": result_nested_body,
                      "nested_return_leak_lifetime_freelocals_counts": counts,
                      "errors_before_nested": False,
                      "nested_first_error": nested_errors[0] if nested_errors else None,
                      "outer_header_after_nested": outer > nested,
                      "first_outer_error": (next((x for x in ERROR.findall(log[outer:])), None)
                                            if outer > nested else None),
                      "proof_exit": stage.get("exit"), "accepted": False,
                      "actual_nested_drop_credit": False, "actual_helper_proved": False,
                      "verification_accepted": False}
            write(e / "nested-body-evidence.json", result)
        stages[name] = {"exit": stage.get("exit"), "fatal": fatals,
                        "console_sha256": (bad_snapshot if name == "nested-wrong-permutation" else on_snapshot)
                            ["binary_sha256"]["bin/verifast"],
                        "console_build_log_sha256": sha(a.evidence / (
                            "nested-wrong-permutation-console-build.log"
                            if name == "nested-wrong-permutation" else
                            "nested-on-console-build.log")),
                        "log_sha256": hashlib.sha256(log.encode()).hexdigest(),
                        "accepted": False}
    need(r2.tool_snapshot(column_tool, a.proof_root) == column_snapshot and
         r2.tool_snapshot(on_tool, a.proof_root) == on_snapshot and
         r2.tool_snapshot(bad_tool, a.proof_root) == bad_snapshot,
         "nested scheduler mutated a parent/candidate tool after controls")
    return {"classification": "R3_COLUMN_NESTED_SCHEDULER_DIAGNOSTIC_COMPLETE",
            "diagnostic_complete": True, "stages": stages,
            "actual_nested_drop_full_normal_unwind_observed":
                read(e / "nested-body-evidence.json").get("nested_body_full_normal_unwind_log_observed", False)
                if (e / "nested-body-evidence.json").exists() else False,
            "actual_nested_drop_credit": False, "actual_helper_proved": False,
            "verification_accepted": False, "accepted": False,
            "open_gates": ["source/unit/body/span malformed negatives", "frontend admissibility", "outer full contract"]}


def run(a, r2, r3, case, receiver_tool, receiver_snapshot):
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") == "o26-r3-ghost-scope-test" and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud R3 column TEST lane required")
    need(not any(os.environ.get(k) for pair in
         (SCOPE_PAIR, RECEIVER_PAIR, COLUMN_PAIR, NESTED_PAIR) for k in pair),
         "inherited column/scheduler opt-in")
    e = a.evidence / "r3-ghost-column-test"
    need(not e.exists(), "column TEST evidence exists")
    e.mkdir()
    manifest = read(a.proof_root / ROOT / "overnight-assume-actual/O26-R3-GHOST-COLUMN-TEST.json")
    patch = a.proof_root / ROOT / manifest["test_patch"]
    relation = read(a.proof_root / ROOT / "overnight-assume-actual/O26-WRAPPER-INPUT-RELATION-PROFILE.json")
    capture = read(a.r3_evidence / "capture-check.json")
    production_snapshot = r2.tool_snapshot(a.r3_source, a.proof_root)
    need(manifest["classification"] == "EXPERIMENTAL_O26_R3_GHOST_COLUMN_TEST_NOT_ACCEPTED" and
         sha(patch) == manifest["test_patch_sha256"] and
         manifest["parent_translator_sha256"] == PARENT and
         relation["source"]["body_sha256"][7] == OUTER and
         manifest["source"]["outer_body_sha256"] == OUTER and
         manifest["source"]["verified_sha256"] == SOURCE and
         manifest["source"]["unit_sha256"] == UNIT and
         capture.get("all_nine_body_records_and_ten_marshal_files_hashed") is True and
         capture.get("typed_outer_mir_exact") is True and
         sha(receiver_tool / TRANSLATOR) == PARENT and
         r2.tool_snapshot(receiver_tool, a.proof_root) == receiver_snapshot,
         "column exact source/MIR/receiver parent admission absent")
    source_case = a.r3_evidence / "capture" / "nine-body-wrapper-input-relation"
    need(sha(source_case / "verified/lib.rs") == SOURCE and
         sha(source_case / "original/lib.rs") == ORIGINAL,
         "column full source case changed")
    column_tool, patch_hash = build_copy(a, receiver_tool, "on", patch,
                                         manifest["test_translator_sha256"], receiver_snapshot)
    column_snapshot = verify_snapshot(r2, a, receiver_snapshot, column_tool,
                                      manifest["test_translator_sha256"], "column-on")
    write(e / "column-on-tool-identity.json", {"parent": receiver_snapshot,
          "candidate": column_snapshot, "patch_sha256": patch_hash, "accepted": False})
    faults = (
        ("wrong-first", lambda s: s.replace('| 155, 1, 155, 32 -> "155:1", 1',
                                              '| 155, 1, 155, 32 -> "155:1", 41', 1), ROUTE_FATAL),
        ("wrong-second", lambda s: s.replace('| 155, 73, 155, 104 -> "155:73", 41',
                                               '| 155, 73, 155, 104 -> "155:73", 1', 1), ROUTE_FATAL),
        ("missing-candidate", lambda s: s.replace('| ((_, 155, _), _) -> true',
                                                     '| ((_, 155, col), _) -> col = 1', 1), CANDIDATE_FATAL),
    )
    fault_tools = {}
    for name, mutate, _ in faults:
        tool, h = build_copy(a, column_tool, name, patch,
                             manifest["test_translator_sha256"], column_snapshot, mutate)
        snap = verify_snapshot(r2, a, column_snapshot, tool, sha(tool / TRANSLATOR), name)
        write(e / (name + "-tool-identity.json"), {"parent": column_snapshot,
              "candidate": snap, "fault_patch_sha256": h, "accepted": False})
        fault_tools[name] = (tool, snap, h)
    r3 = load("column_r3_profile", a.cloud_dir / "o26-r3-profile.py")
    all_stages = {}
    on_advanced = False
    column_on_log = None
    column_on_stage = None
    for name, tool, own_mode, fault in (
        ("column-off", column_tool, "off", None),
        ("column-partial", column_tool, "partial", None),
        ("column-on", column_tool, "on", None),
        *((name, pair[0], "on", fatal) for name, pair, fatal in
          ((n, fault_tools[n], f) for n, _, f in faults)),
    ):
        own_pair = None if own_mode == "off" else COLUMN_PAIR
        mode = own_mode
        stage, log = run_stage(a, r3, case, tool, name, own_pair, mode)
        need(stage.get("status") == "RAN" and stage.get("exit") not in (None,124,137) and
             stage.get("source_unchanged") is True and stage.get("source_before")==stage.get("source_after") and
             stage.get("source_before", {}).get("verified/lib.rs") == SOURCE and
             stage.get("source_before", {}).get("original/lib.rs") == ORIGINAL and
             stage.get("intrinsic_gate_active") is True and stage.get("pointer_drop_gate_active") is True,
             name + " proof stage incomplete")
        (e / (name + ".log")).write_text(log)
        print("R3 COLUMN FULL LOG BEGIN " + name, flush=True)
        print(log, end="" if log.endswith("\n") else "\n", flush=True)
        print("R3 COLUMN FULL LOG END " + name, flush=True)
        write(e / (name + "-stage.json"), stage)
        fatals=[x for x in log.splitlines() if x.startswith("Fatal error:")]
        if name == "column-off":
            need(HIDE_ERROR in log and COLUMN_MARK not in log and
                 SCOPE_MARK in log and RECEIVER_MARK in log,
                 "column-off did not repeat exact saved_true_input hiding error")
        elif name == "column-partial":
            need(stage.get("exit") == 2 and fatals == [COLUMN_FATAL] and
                 "Verifying function '" not in log,
                 "column partial opt-in not rejected preheaders")
        elif name == "column-on":
            first_marker = COLUMN_MARK + " call 155:1 -> AST 155:1"
            second_marker = COLUMN_MARK + " call 155:73 -> AST 155:41"
            need(log.count(first_marker) == 1 and log.count(second_marker) == 1 and
                 log.index(first_marker) < log.index(second_marker) and
                 SCOPE_MARK in log and RECEIVER_MARK in log and
                 "Verifying function '" in log and HIDE_ERROR not in log,
                 "column-on mapping absent or failed to advance past line155")
            on_advanced = True
            column_on_log = log
            column_on_stage = stage
        else:
            expected_route_markers = 1 if name == "wrong-second" else 0
            need(stage.get("exit") == 2 and fatals == [fault] and SCOPE_MARK in log and
                 RECEIVER_MARK not in log and "Verifying function '" not in log and
                 log.count(COLUMN_MARK) == expected_route_markers,
                 name + " fault did not fail exact pre-receiver mapping gate")
        stage_snapshot = fault_tools[name][1] if name in fault_tools else column_snapshot
        build_log_name = name if name in fault_tools else "on"
        all_stages[name] = {"exit": stage.get("exit"), "fatal": fatals,
                            "log_sha256": hashlib.sha256(log.encode()).hexdigest(),
                            "console_sha256": stage_snapshot["binary_sha256"]["bin/verifast"],
                            "console_build_log_sha256": sha(a.evidence / (build_log_name + "-console-build.log")),
                            "patch_sha256": patch_hash if name == "column-on" else
                                (fault_tools[name][2] if name in fault_tools else None),
                            "accepted": False}
    nested_flag = os.environ.get("O26_WITH_R3_COLUMN_NESTED_TEST", "0")
    need(nested_flag in ("0", "1"), "invalid nested scheduler flag")
    nested_result = None
    if nested_flag == "1":
        need(column_on_log is not None and column_on_stage is not None,
             "nested scheduler requires completed COLUMN-on stage")
        nested_result = schedule(a, r2, r3, case, column_tool,
                                 column_snapshot, manifest, column_on_log, column_on_stage)
        need(nested_result.get("diagnostic_complete") is True and
             nested_result.get("accepted") is False,
             "requested nested scheduler controls incomplete")
    need(on_advanced and r2.tool_snapshot(receiver_tool, a.proof_root) == receiver_snapshot and
         r2.tool_snapshot(a.r3_source, a.proof_root) == production_snapshot,
         "column parent/production tool changed or positive diagnostic not advanced")
    result = {"classification": "R3_GHOST_COLUMN_TEST_DIAGNOSTIC_COMPLETE",
              "diagnostic_complete": True, "stages": all_stages,
              "nested_scheduler_test_requested": nested_flag == "1",
              "nested_scheduler_test": nested_result,
              "actual_nested_drop_full_normal_unwind_observed":
                  nested_result.get("actual_nested_drop_full_normal_unwind_observed", False)
                  if nested_result else False,
              "source_runtime_sha256": sha(source_case / "verified/lib.rs"),
              "original_source_sha256": sha(source_case / "original/lib.rs"),
              "source_unit_span_negative_gates_complete": False,
              "actual_source_accepted": False, "target_contract_proved": False,
              "verification_accepted": False, "accepted": False}
    write(e / "diagnostic-audit.json", result)
    return result
