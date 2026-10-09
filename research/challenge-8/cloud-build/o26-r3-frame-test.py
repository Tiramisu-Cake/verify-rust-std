#!/usr/bin/env python3
"""Cloud-only exact FRAME translator diagnostic; never grants proof acceptance."""
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
import sys
import time
from types import SimpleNamespace


ROOT = Path("research/challenge-8")
TRANSLATOR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
MANIFEST = ROOT / "overnight-assume-actual/O26-R3-FRAME-TEST.json"
FRAME_PAIR = ("SORT4_R3_FRAME_TEST_REPO_ROOT", "SORT4_R3_FRAME_TEST")
PARENT_PAIRS = (
    ("SORT4_WRAPPER_REBASE_REPO_ROOT", "SORT4_WRAPPER_REBASE_ADMISSION"),
    ("SORT4_WRAPPER_INPUT_RELATION_REPO_ROOT", "SORT4_WRAPPER_INPUT_RELATION_ADMISSION"),
    ("SORT4_R3_GHOST_SCOPE_TEST_REPO_ROOT", "SORT4_R3_GHOST_SCOPE_TEST"),
    ("SORT4_R3_RECEIVER_TEST_REPO_ROOT", "SORT4_R3_RECEIVER_TEST"),
    ("SORT4_R3_GHOST_COLUMN_TEST_REPO_ROOT", "SORT4_R3_GHOST_COLUMN_TEST"),
    ("SORT4_R3_COLUMN_NESTED_TEST_REPO_ROOT", "SORT4_R3_COLUMN_NESTED_TEST"),
)
NAMES = (
    "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new",
    "sort4_checked_as_mut_ptr", "sort4_checked_pointer_drop",
    "sort4_checked_generic_drop", "checked_transmute_neo_pointer",
    "checked_assume_init_pointer", "checked_forget_owned",
    "select_unpredictable",
    "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop",
)
ERROR = re.compile(r"(?m)^.*: error: .*|^Error:.*$|^Fatal error:.*$")
REFRESH = ROOT / "overnight-assume-actual/O26-REFRESH-PROFILE.json"
R2 = ROOT / "overnight-assume-actual/O26-WRAPPER-REBASE-PROFILE.json"
R3 = ROOT / "overnight-assume-actual/O26-WRAPPER-INPUT-RELATION-PROFILE.json"
SCOPE = ROOT / "overnight-assume-actual/O26-R3-GHOST-SCOPE-TEST.json"
RECEIVER = ROOT / "overnight-assume-actual/O26-R3-RECEIVER-TEST.json"
COLUMN = ROOT / "overnight-assume-actual/O26-R3-GHOST-COLUMN-TEST.json"
NESTED = ROOT / "overnight-assume-actual/O26-R3-COLUMN-NESTED-TEST.json"
ORIGINAL = "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5"
R3_SOURCE = "a95aff14592b167c62c53c7ed726128ee86c7c19768cfe613504cdec841f8463"
FRAME_TYPED_OUTER_GRAPH = {
    "local_count": 56,
    "block_count": 39,
    "shared_cleanup_call_predecessors": 18,
    "forget": {"block": 18, "dead_local": "_34", "destination": "_35",
        "argument": "_36", "drop_flag": "_55", "guard": "_30",
        "normal": 19, "cleanup": 38, "operand": "Move", "source_line": 208},
    "pointer_drop": {"block": 16, "argument": "_33", "destination": "_32",
        "normal": 17, "cleanup": 38},
    "assume_init": {"block": 34, "argument": "_51", "destination": "_0",
        "normal": 35, "cleanup": 38},
    "cleanup": {"resume": 36, "drop": 37, "switch": 38,
        "guard": "_30", "flag": "_55"},
    "explicit_ghost_calls": [
        [0, "_4", 1, None], [1, "_5", 2, None], [6, "_14", 7, None],
        [7, "_15", 8, None], [12, "_20", 13, None], [13, "_21", 14, None],
        [20, "_38", 21, 38], [21, "_39", 22, 38], [22, "_40", 23, 38],
        [23, "_41", 24, 38], [24, "_42", 25, 38], [25, "_43", 26, 38],
        [26, "_44", 27, 38], [27, "_45", 28, 38], [28, "_46", 29, 38],
        [29, "_47", 30, 38], [30, "_48", 31, 38], [31, "_49", 32, 38],
        [32, "_50", 33, 38],
    ],
}


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def read(path: Path) -> dict:
    need(path.is_file(), f"missing FRAME TEST input: {path}")
    value = json.loads(path.read_text())
    need(isinstance(value, dict), f"FRAME TEST JSON is not an object: {path}")
    return value


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha(path: Path) -> str:
    need(path.is_file(), f"missing FRAME TEST file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f"module unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def expected_chain(a) -> tuple[dict, list[dict]]:
    refresh, r2, r3 = (read(a.proof_root / path) for path in (REFRESH, R2, R3))
    scope, receiver, column, nested, frame = (
        read(a.proof_root / path) for path in (SCOPE, RECEIVER, COLUMN, NESTED, MANIFEST))
    manifests = {"r3": r3, "scope": scope, "receiver": receiver,
                 "column": column, "nested": nested}
    need(refresh.get("classification") == "EXPERIMENTAL_O26_REFRESH_17_20" and
         r2.get("classification") == "EXPERIMENTAL_O26_WRAPPER_REBASE_COMPONENT23_R2_NOT_ACCEPTED" and
         r3.get("classification") == "EXPERIMENTAL_O26_WRAPPER_INPUT_RELATION_COMPONENT24_NOT_ACCEPTED" and
         scope.get("classification") == "EXPERIMENTAL_O26_R3_GHOST_SCOPE_TEST_NOT_ACCEPTED" and
         receiver.get("classification") == "EXPERIMENTAL_O26_R3_RECEIVER_TEST_NOT_ACCEPTED" and
         column.get("classification") == "EXPERIMENTAL_O26_R3_GHOST_COLUMN_TEST_NOT_ACCEPTED" and
         nested.get("classification") == "EXPERIMENTAL_O26_R3_COLUMN_NESTED_TEST_NOT_ACCEPTED" and
         frame.get("classification") == "EXPERIMENTAL_O26_R3_FRAME_TEST_NOT_ACCEPTED",
         "one or more exact parent/FRAME manifests are absent or unreviewed")
    chain = [
        {"kind": "R2", "manifest": r2, "parent": refresh.get("refreshed_translator_sha256"),
         "patch": r2.get("component23_patch"), "patch_sha256": r2.get("component23_patch_sha256"),
         "result": r2.get("new_translator_sha256")},
        {"kind": "R3", "manifest": r3, "parent": r3.get("r2_translator_sha256"),
         "patch": r3.get("component24_patch"), "patch_sha256": r3.get("component24_patch_sha256"),
         "result": r3.get("new_translator_sha256")},
        {"kind": "scope", "manifest": scope, "parent": scope.get("parent_translator_sha256"),
         "patch": scope.get("test_patch"), "patch_sha256": scope.get("test_patch_sha256"),
         "result": scope.get("test_translator_sha256")},
        {"kind": "receiver", "manifest": receiver, "parent": receiver.get("parent_translator_sha256"),
         "patch": receiver.get("test_patch"), "patch_sha256": receiver.get("test_patch_sha256"),
         "result": receiver.get("test_translator_sha256")},
        {"kind": "column", "manifest": column, "parent": column.get("parent_translator_sha256"),
         "patch": column.get("test_patch"), "patch_sha256": column.get("test_patch_sha256"),
         "result": column.get("test_translator_sha256")},
        {"kind": "nested", "manifest": nested, "parent": nested.get("parent_translator_sha256"),
         "patch": nested.get("test_patch"), "patch_sha256": nested.get("test_patch_sha256"),
         "result": nested.get("test_translator_sha256")},
        {"kind": "frame", "manifest": frame, "parent": frame.get("parent_translator_sha256"),
         "patch": frame.get("test_patch"), "patch_sha256": frame.get("test_patch_sha256"),
         "result": frame.get("test_translator_sha256")},
    ]
    need(r3.get("r2_translator_sha256") == r2.get("new_translator_sha256") and
         scope.get("parent_translator_sha256") == r3.get("new_translator_sha256") and
         receiver.get("parent_translator_sha256") == scope.get("test_translator_sha256") and
         column.get("parent_translator_sha256") == receiver.get("test_translator_sha256") and
         nested.get("parent_translator_sha256") == column.get("test_translator_sha256") and
         frame.get("parent_translator_sha256") == nested.get("test_translator_sha256"),
         "R2/R3/scope/receiver/COLUMN/nested/FRAME translator chain is discontinuous")
    source = frame.get("source") or {}
    body_hashes = source.get("body_sha256")
    need(isinstance(body_hashes, list) and len(body_hashes) == 9 and
         source.get("original_sha256") == ORIGINAL and
         all(isinstance(source.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", source[key])
             for key in ("verified_sha256", "unit_sha256")) and
         nested.get("source", {}).get("verified_sha256") == R3_SOURCE and
         nested.get("source", {}).get("original_sha256") == ORIGINAL and
         str(frame.get("parent_profile", "")).endswith("O26-R3-COLUMN-NESTED-TEST.json"),
         "FRAME source or nested parent source inventory is incomplete")
    for parent_name in ("r3", "scope", "receiver", "column", "nested"):
        parent_source=manifests[parent_name].get("source",{})
        need(parent_source.get("verified_sha256")==R3_SOURCE and
             parent_source.get("original_sha256",ORIGINAL)==ORIGINAL and
             parent_source.get("unit_sha256")==manifests["r3"]["source"].get("unit_sha256"),
             parent_name+" manifest source/unit differs from shared R3 parent")
    old_bodies=manifests["r3"]["source"].get("body_sha256")
    need(isinstance(old_bodies,list) and len(old_bodies)==9 and
         all(body_hashes[i]==old_bodies[i] for i in (*range(6),8)) and
         body_hashes[6]!=old_bodies[6] and body_hashes[7]!=old_bodies[7] and
         body_hashes[8]==nested.get("source",{}).get("nested_body8_sha256"),
         "FRAME must change only unit/helper/outer and preserve exact nested body-8 identity")
    need(r2.get("production_translator_sha256") == refresh.get("refreshed_translator_sha256"),
         "R2 profile does not begin at canonical O26 refresh translator")
    for item in chain:
        need(all(isinstance(item.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", item[key])
                 for key in ("parent", "patch_sha256", "result")) and
             isinstance(item.get("patch"), str),
             f"{item['kind']} patch chain pin is incomplete")
        patch_path = a.proof_root / ROOT / item["patch"]
        need(sha(patch_path) == item["patch_sha256"], f"{item['kind']} patch bytes differ")
    need(frame.get("test_patch") and
         frame.get("opt_in") == {FRAME_PAIR[0]: "exact proof root", FRAME_PAIR[1]: "1"} and
         set(frame.get("required_parent_opt_ins", [])) >= {
             "SORT4_ACTUAL_OWNER_REPO_ROOT/ADMISSION",
             "SORT4_ACTUAL_OWNER_NINE_ADMISSION",
             "SORT4_A1_NINE_REPO_ROOT",
             "SORT4_ACTUAL_NESTED_H2_REPO_ROOT",
             "SORT4_ACTUAL_FORGET_OWN_REPO_ROOT",
             "SORT4_WRAPPER_REBASE_REPO_ROOT/ADMISSION",
             "SORT4_WRAPPER_INPUT_RELATION_REPO_ROOT/ADMISSION",
             "SORT4_R3_GHOST_SCOPE_TEST_REPO_ROOT/TEST",
             "SORT4_R3_RECEIVER_TEST_REPO_ROOT/TEST",
             "SORT4_R3_GHOST_COLUMN_TEST_REPO_ROOT/TEST",
             "SORT4_R3_COLUMN_NESTED_TEST_REPO_ROOT/TEST"} and
         frame.get("verification_accepted") is False and frame.get("accepted") is False,
         "FRAME exact opt-in or non-acceptance manifest differs")
    need(frame.get("typed_outer_graph") == FRAME_TYPED_OUTER_GRAPH,
         "FRAME typed outer CFG/helper/cleanup/ghost-call graph differs from reviewed constants")
    return {"refresh": refresh, "r2": r2, "r3": r3, "scope": scope,
            "receiver": receiver, "column": column, "nested": nested,
            "frame": frame, "source": source}, chain


def apply_chain(a, r2mod, chain, base_tool: Path) -> tuple[Path, dict, list[dict]]:
    e = a.evidence / "tool-chain"
    e.mkdir()
    candidate = a.work_root / "o26-r3-frame-test-tool"
    need(not candidate.exists() and not candidate.is_relative_to(a.evidence),
         "FRAME candidate tool must be fresh and outside evidence")
    base_snapshot = r2mod.tool_snapshot(base_tool, a.proof_root)
    need(sha(base_tool / TRANSLATOR) == chain[0]["parent"],
         "canonical O26 refresh source_home translator pin differs")
    shutil.copytree(base_tool, candidate, symlinks=True)
    pins = []
    for item in chain:
        patch = a.proof_root / ROOT / item["patch"]
        need(sha(candidate / TRANSLATOR) == item["parent"],
             item["kind"] + " patch parent translator differs")
        subprocess.run(("git", "-C", str(candidate), "apply", "--check", str(patch)), check=True)
        subprocess.run(("git", "-C", str(candidate), "apply", str(patch)), check=True)
        observed = sha(candidate / TRANSLATOR)
        need(observed == item["result"], item["kind"] + " resulting translator hash differs")
        pins.append({"kind": item["kind"], "parent_translator_sha256": item["parent"],
                     "patch": item["patch"], "patch_sha256": item["patch_sha256"],
                     "result_translator_sha256": observed})
    need(sha(candidate / TRANSLATOR) == chain[-1]["result"],
         "final FRAME translator identity differs")
    write(e / "patch-chain.json", {"steps": pins, "accepted": False})
    shutil.copy2(a.proof_root / ROOT / chain[-1]["patch"], e / "frame-test.patch")
    (candidate / "bin/verifast").unlink()
    timeout = a.deadline_epoch - int(time.time()) - 25
    need(timeout > 0, "FRAME final console build deadline")
    log_path = e / "frame-test-console-build.log"
    with log_path.open("wb") as log:
        build = subprocess.run(("make", "-C", str(candidate / "src"), "../bin/verifast",
                                "WITHOUT_LABLGTK=yes", "VERBOSE=yes"),
                               stdout=log, stderr=subprocess.STDOUT,
                               timeout=timeout, check=False)
    console_log = log_path.read_text(errors="replace")
    print("FRAME TEST FINAL CONSOLE BUILD LOG BEGIN", flush=True)
    print(console_log, end="" if console_log.endswith("\n") else "\n", flush=True)
    print("FRAME TEST FINAL CONSOLE BUILD LOG END", flush=True)
    need(build.returncode == 0 and (candidate / "bin/verifast").is_file(),
         "final FRAME console build failed")
    ldd=subprocess.run(("ldd",str(candidate/"bin/verifast")),capture_output=True,text=True,check=False)
    (e/"frame-test-console-ldd.txt").write_text(ldd.stdout+ldd.stderr)
    need(ldd.returncode==0 and "not found" not in ldd.stdout+ldd.stderr,
         "final FRAME console has unresolved dynamic libraries")
    candidate_snapshot = r2mod.tool_snapshot(candidate, a.proof_root)
    for key in ("head", "effective_rsspec_sha256", "proof_std_sha256"):
        need(candidate_snapshot[key] == base_snapshot[key], "FRAME tool changed frozen " + key)
    for field in ("critical_source_sha256", "modified_tracked_source_sha256", "binary_sha256"):
        need(set(candidate_snapshot[field]) == set(base_snapshot[field]),
             "FRAME tool changed snapshot key set: " + field)
        exception = "bin/verifast" if field == "binary_sha256" else str(TRANSLATOR)
        for key, value in base_snapshot[field].items():
            if key != exception:
                need(candidate_snapshot[field][key] == value,
                     "FRAME tool changed frozen " + field + ":" + key)
    need(candidate_snapshot["critical_source_sha256"][str(TRANSLATOR)] == chain[-1]["result"] and
         candidate_snapshot["modified_tracked_source_sha256"][str(TRANSLATOR)] == chain[-1]["result"] and
         candidate_snapshot["binary_sha256"]["bin/verifast"] !=
             base_snapshot["binary_sha256"]["bin/verifast"],
         "FRAME translator/console delta mismatch")
    write(e / "tool-identity.json", {"base": base_snapshot, "frame": candidate_snapshot,
          "console_sha256": candidate_snapshot["binary_sha256"]["bin/verifast"],
          "console_build_log_sha256": sha(log_path), "accepted": False})
    need(r2mod.tool_snapshot(base_tool, a.proof_root) == base_snapshot,
         "canonical O26 source_home changed during FRAME tool construction")
    return candidate, candidate_snapshot, pins


def run_capture(a, tool: Path, mode: str, evidence: Path) -> dict:
    need(not evidence.exists(), f"fresh {mode} capture evidence already exists")
    cmd = [sys.executable, str(a.proof_root / ROOT / "overnight-assume-actual/capture.py"),
           "--tool-home", str(tool), "--schema", str(tool / "src/rust_frontend/vf_mir/vf_mir.capnp"),
           "--compiler-sysroot", str(a.compiler_sysroot), "--evidence", str(evidence),
           "--deadline-epoch", str(a.deadline_epoch), "--fingerprint"]
    cmd.append("--wrapper-input-relation-frame" if mode == "frame" else "--wrapper-input-relation")
    timeout = a.deadline_epoch - int(time.time()) - 25
    need(timeout > 0, f"{mode} source capture deadline")
    log_path = a.evidence / f"{mode}-capture-console.log"
    with log_path.open("wb") as log:
        proc = subprocess.run(cmd, cwd=a.proof_root, stdout=log, stderr=subprocess.STDOUT,
                              timeout=timeout, check=False)
    text = log_path.read_text(errors="replace")
    print(f"FRAME {mode.upper()} CAPTURE LOG BEGIN", flush=True)
    print(text, end="" if text.endswith("\n") else "\n", flush=True)
    print(f"FRAME {mode.upper()} CAPTURE LOG END", flush=True)
    need(proc.returncode == 0, f"{mode} source capture failed: {proc.returncode}")
    summary = read(evidence / "summary.json")
    write(a.evidence / f"{mode}-capture-receipt.json", {
        "exit": proc.returncode, "summary_sha256": sha(evidence / "summary.json"),
        "console_log_sha256": sha(log_path), "source": summary.get("source"),
        "accepted": False})
    return summary


def verify_capture(summary: dict, capture_root: Path, expected: dict, mode: str,
                   observed: dict, expected_transform: dict | None = None) -> dict:
    source = summary.get("source") or {}
    case_name = source.get("case_name")
    case = capture_root / case_name if isinstance(case_name, str) else capture_root / "missing"
    source_json = case / "fixture.json"
    original_path = case / "original/lib.rs"
    verified_path = case / "verified/lib.rs"
    body_hashes = expected.get("body_sha256")
    source_record=read(source_json)
    source_ok=(summary.get("classification") == "NINE_BODY_SOURCE_MIR_CALIBRATION_ONLY" and
        summary.get("frontend_refinement_and_full_body_capture") is True and
        summary.get("source_mode") == ("wrapper-input-relation-frame-source-only" if mode == "frame"
                                        else "wrapper-input-relation-source-only") and
        isinstance(body_hashes,list) and len(body_hashes)==9 and
        source.get("verified_sha256")==expected.get("verified_sha256")==sha(verified_path) and
        source.get("original_sha256")==expected.get("original_sha256")==ORIGINAL==sha(original_path) and
        source.get("source_order")==list(NAMES) and
        source.get("ghost_strip_identity") is True and
        source.get("actual_runtime_unchanged") is True and
        source.get("verification_accepted") is False and source.get("accepted",False) is False and
        source_record.get("verified_sha256")==source.get("verified_sha256") and
        (expected_transform is None or
         (source == expected_transform and source_record == expected_transform)))
    fingerprints=(summary.get("fingerprint") or {}).get("snapshots") or {}
    expected_fingerprints={"unit":expected.get("unit_sha256"),
                           **{f"body-{i}":value for i,value in enumerate(body_hashes or [])}}
    fingerprint_ok=(set(fingerprints)==set(expected_fingerprints) and
        all(isinstance(fingerprints.get(key),dict) and
            fingerprints[key].get("file")==f"actual-nested-9-{key}.marshal" and
            sha(case/fingerprints[key]["file"])==fingerprints[key].get("sha256")==digest
            for key,digest in expected_fingerprints.items()))
    expected_mir={"normal":observed.get("normal_whole_decoded_mir_sha256"),
                  "readonly":observed.get("readonly_whole_decoded_mir_sha256")}
    full=summary.get("full_body_capture") or {}
    body_mir_pins_ok=(mode!="frame" or all(
        isinstance(observed.get(mode_name+"_body_sha256"),list) and
        len(observed[mode_name+"_body_sha256"])==9 for mode_name in ("normal","readonly")))
    bodies_ok=(set(full)=={"normal","readonly"} and
        all(isinstance(full.get(mode_name),dict) and
            full[mode_name].get("exact_body_count_and_order") is True and
            full[mode_name].get("whole_decoded_mir_sha256")==expected_mir[mode_name] and
            sha(case/f"{mode_name}-mir.txt")==expected_mir[mode_name] and
            isinstance(full[mode_name].get("bodies"),list) and len(full[mode_name]["bodies"])==9 and
            all(row.get("index")==i and row.get("defpath")==NAMES[i] and
                row.get("sha256")==sha(case/row["file"]) and
                (not isinstance(observed.get(mode_name+"_body_sha256"),list) or
                 row.get("sha256")==observed[mode_name+"_body_sha256"][i]) and
                (i!=7 or observed.get(mode_name+"_outer_body7_sha256") is None or
                 row.get("sha256")==observed.get(mode_name+"_outer_body7_sha256"))
                for i,row in enumerate(full[mode_name]["bodies"]))
            for mode_name in ("normal","readonly")) and body_mir_pins_ok)
    guard=summary.get("guard_capture") or {}; stages=guard.get("stages") or {}
    refinement=(guard.get("frontend_refinement") is True and
        all(isinstance(stages.get(key),dict) and stages[key].get("exit")==0 and
            stages[key].get("source_unchanged") is True for key in
            ("normal-export","normal-decode","readonly-export","readonly-decode","refinement")))
    fingerprint=summary.get("fingerprint") or {}
    refusal=(fingerprint.get("classification")=="INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE" and
        fingerprint.get("all_ten_snapshots") is True and fingerprint.get("body_proof_run") is False and
        isinstance(fingerprint.get("stage"),dict) and fingerprint["stage"].get("exit")==2)
    need(source_ok and fingerprint_ok and bodies_ok and refinement and refusal,
         f"fresh {mode} source/MIR/refinement/fingerprint identity incomplete")
    return {"source_pair_exact":source_ok,"ten_fingerprints_exact":fingerprint_ok,
            "full_normal_readonly_nine_body_capture":bodies_ok,
            "normal_readonly_refinement":refinement,"fingerprint_refusal_no_proof":refusal,
            "source_sha256":source.get("verified_sha256"),
            "original_sha256":source.get("original_sha256"),
            "unit_sha256":source.get("unit_sha256"),"body_sha256":body_hashes,
            "normal_mir_sha256":expected_mir["normal"],
            "readonly_mir_sha256":expected_mir["readonly"],"accepted":False}


def pair_env(a, frame_mode: str):
    all_pairs=(*PARENT_PAIRS,FRAME_PAIR)
    need(not any(os.environ.get(key) for pair in all_pairs for key in pair),
         "inherited R2/R3/FRAME opt-in pair")
    for root_key,flag_key in PARENT_PAIRS:
        os.environ[root_key]=str(a.proof_root); os.environ[flag_key]="1"
    if frame_mode in ("partial","on"):
        os.environ[FRAME_PAIR[0]]=str(a.proof_root)
    if frame_mode=="on":os.environ[FRAME_PAIR[1]]="1"


def proof_stage(a, recipe, r2mod, tool: Path, case: Path, name: str,
                expected_source: str, frame_mode: str, expected_tool: dict) -> tuple[dict,str]:
    need(not any(os.environ.get(key) for pair in (*PARENT_PAIRS,FRAME_PAIR) for key in pair),
         "parent/FRAME pair leaked between proof controls")
    pair_env(a,frame_mode)
    try:
        stage=recipe.proof_stage(a.proof_root,case,tool,
            tool/"src/rust_frontend/vf_mir/vf_mir.capnp",a.compiler_sysroot,
            a.deadline_epoch,name,"r3_frame_"+name.replace("-","_"))
    finally:
        for pair in (*PARENT_PAIRS,FRAME_PAIR):
            for key in pair:os.environ.pop(key,None)
    log_path=case/(name+".log")
    text=log_path.read_text(errors="replace") if log_path.is_file() else ""
    print("R3 FRAME FULL LOG BEGIN "+name,flush=True)
    print(text,end="" if text.endswith("\n") else "\n",flush=True)
    print("R3 FRAME FULL LOG END "+name,flush=True)
    need(stage.get("status")=="RAN" and stage.get("exit") not in (None,124,137) and
         stage.get("source_unchanged") is True and
         stage.get("source_before")==stage.get("source_after") and
         stage.get("source_before",{}).get("verified/lib.rs")==expected_source and
         stage.get("source_before",{}).get("original/lib.rs")==ORIGINAL and
         stage.get("intrinsic_gate_active") is True and stage.get("pointer_drop_gate_active") is True,
         name+" full proof stage/source/tool gate incomplete")
    write(a.evidence/(name+"-stage.json"),stage)
    write(a.evidence/(name+"-receipt.json"),{
        "exit":stage.get("exit"),"source_before":stage.get("source_before"),
        "source_after":stage.get("source_after"),"log_sha256":sha(log_path),
        "tool_snapshot":r2mod.tool_snapshot(tool,a.proof_root),
        "accepted":False})
    need(r2mod.tool_snapshot(tool,a.proof_root)==expected_tool and
         r2mod.tool_snapshot(a.production_source,a.proof_root)==a.production_snapshot,
         name+" changed candidate or canonical production tool identity")
    shutil.copy2(log_path,a.evidence/(name+".log"))
    return stage,text


def log_proof_evidence(log: str, stage: dict) -> dict:
    headers=[log.find("Verifying function '"+name+"'") for name in NAMES]
    errors=ERROR.findall(log)
    first=errors[0] if errors else None
    prefix=headers[:7]
    nested=headers[8]; outer=headers[7]
    helper_end=min((x for x in (headers[7],headers[8]) if x>headers[6]),default=len(log))
    helper_segment=log[headers[6]:helper_end] if headers[6]>=0 else ""
    outer_prototype=log.find("Function '"+NAMES[7]+"': Function prototype implementation check",nested)
    nested_boundaries=[x for x in (outer,outer_prototype) if x>nested]
    nested_end=min(nested_boundaries) if nested_boundaries else len(log)
    nested_segment=log[nested:nested_end] if nested>=0 else ""
    def counts(text):
        return {key:text.count(key) for key in ("Executing return statement","Leak check.",
            "Consuming function lifetime token","Freeing locals.")}
    helper_counts=counts(helper_segment); nested_counts=counts(nested_segment)
    helper_full=all(v==2 for v in helper_counts.values())
    nested_full=(bool(nested_boundaries) and all(v==2 for v in nested_counts.values()) and
        "verified/lib.rs(169,33-48): Verifying call" in nested_segment and
        ERROR.search(nested_segment) is None)
    prefix_order=(all(x>=0 for x in prefix) and prefix==sorted(prefix))
    order=(prefix_order and headers[6]<nested and (bool(nested_boundaries) or
        (outer<0 and outer_prototype<0 and stage.get("exit") in (1,2) and
         bool(ERROR.search(nested_segment)))))
    err_before_nested=ERROR.search(log[:nested]) is not None if nested>=0 else True
    nested_error=ERROR.search(nested_segment) if nested_segment else None
    outer_start=min((x for x in (outer,outer_prototype) if x>nested),default=-1)
    outer_segment=log[outer_start:] if outer_start>=0 else ""
    if outer_start>=0:
        outer_error=ERROR.search(outer_segment)
        first_error_in_outer=bool(outer_error and first==outer_error.group(0))
    else:
        first_error_in_outer=False
    if outer>=0:
        outer_counts=counts(log[outer:])
        outer_full=(stage.get("exit")==0 and not errors and all(v==2 for v in outer_counts.values()))
    else:
        outer_counts={}; outer_full=False
    return {"headers":headers,"prefix7_ordered":prefix_order,
        "nested_before_outer":order,"errors_before_nested":err_before_nested,
        "helper_normal_unwind_return_leak_lifetime_freelocals":helper_counts,
        "helper_full_normal_unwind_observed":helper_full,
        "nested_normal_unwind_return_leak_lifetime_freelocals":nested_counts,
        "nested_full_normal_unwind_observed":nested_full,
        "outer_header_seen":outer>=0,"outer_prototype_seen":outer_prototype>=0,
        "outer_counts":outer_counts,
        "outer_full_normal_unwind_observed":outer_full,
        "first_error":first,"first_error_in_outer":first_error_in_outer,
        "first_error_in_nested":bool(nested_error and first==nested_error.group(0)),
        "proof_exit":stage.get("exit"),"accepted":False}


def run(a) -> dict:
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER")=="cloud-build" and
         os.environ.get("LANE")=="o26-input-relation-frame-test" and
         not os.environ.get("GITHUB_ACTIONS"),"Cloud FRAME TEST lane required")
    values=expected_chain(a)
    manifests,chain=values
    frame=manifests["frame"]
    parent_source=manifests["r3"]["source"]
    base_tool=a.production_source
    baseline_result={"classification":"INCONCLUSIVE","diagnostic_complete":False,
        "target_contract_proved":False,"verification_accepted":False,"accepted":False,
        "actual_source_accepted":False,"actual_safe_forget_linked":False,
        "wrong_helper_contract_negative_complete":False,
        "wrong_typed_move_edge_negative_complete":False}
    write(a.evidence/"diagnostic-audit.json",baseline_result)
    r2mod=load("frame_tool_snapshot",a.cloud_dir/"o26-wrapper-profile.py")
    recipe=load("frame_proof_recipe",a.cloud_dir/"o26-recipe.py")
    production_snapshot=r2mod.tool_snapshot(base_tool,a.proof_root)
    a.production_snapshot=production_snapshot
    candidate,snapshot,pins=apply_chain(a,r2mod,chain,base_tool)
    # The exact fresh source capture is made after the final console is built.
    frame_capture_root=a.evidence/"frame-capture"
    old_capture_root=a.evidence/"old-r3-capture"
    frame_summary=run_capture(a,candidate,"frame",frame_capture_root)
    frame_receipt=verify_capture(frame_summary,frame_capture_root,manifests["source"],
        "frame",frame.get("observed_capture") or {},frame.get("source_transform"))
    old_summary=run_capture(a,candidate,"old-r3",old_capture_root)
    old_receipt=verify_capture(old_summary,old_capture_root,parent_source,"old-r3",
        manifests["r3"].get("observed_capture") or {})
    case_frame=frame_capture_root/frame_summary["source"]["case_name"]
    case_old=old_capture_root/old_summary["source"]["case_name"]
    need(r2mod.tool_snapshot(base_tool,a.proof_root)==production_snapshot and
         r2mod.tool_snapshot(candidate,a.proof_root)==snapshot,
         "capture stage changed canonical or final tool identity")
    stages={}
    # Historical source control: all inherited parent admissions, FRAME omitted.
    old_stage,old_log=proof_stage(a,recipe,r2mod,candidate,case_old,
        "frame-old-r3-source-default-off",R3_SOURCE,"off",snapshot)
    old_errors=ERROR.findall(old_log)
    old_outer=old_log.find("Verifying function 'select_unpredictable'")
    old_reached_240=old_stage.get("exit") in (1,2) and old_outer>=0 and bool(old_errors) and \
        "verified/lib.rs(240," in old_errors[0]
    need(old_reached_240,"FRAME-off old R3 source did not preserve outer-240 baseline")
    stages["old-r3-source-off"]={"exit":old_stage.get("exit"),"first_error":old_errors[0],
        "reached_outer_240":old_reached_240,"accepted":False}
    off_stage,off_log=proof_stage(a,recipe,r2mod,candidate,case_frame,
        "frame-source-default-off",frame_receipt["source_sha256"],"off",snapshot)
    partial_stage,partial_log=proof_stage(a,recipe,r2mod,candidate,case_frame,
        "frame-source-partial-pair",frame_receipt["source_sha256"],"partial",snapshot)
    on_stage,on_log=proof_stage(a,recipe,r2mod,candidate,case_frame,
        "frame-source-on",frame_receipt["source_sha256"],"on",snapshot)
    expected_controls=frame.get("expected_controls") or {}
    off_expected=expected_controls.get("frame_off_fatal")
    partial_expected=expected_controls.get("frame_partial_fatal")
    need(isinstance(off_expected,str) and isinstance(partial_expected,str),
         "FRAME manifest lacks exact expected source-off/partial fatal lines")
    def exact_preheader(stage,log,fatal):
        return (stage.get("exit")==2 and
            [line for line in log.splitlines() if line.startswith("Fatal error:")]==[fatal] and
            ERROR.findall(log)==[fatal] and "Verifying function '" not in log)
    off_ok=exact_preheader(off_stage,off_log,off_expected)
    partial_ok=exact_preheader(partial_stage,partial_log,partial_expected)
    need(off_ok and partial_ok,"FRAME source mismatch or partial pair missed exact preheader refusal")
    stages["frame-source-off"]={"exit":off_stage.get("exit"),"fatal":off_expected,
        "preheader_refusal":off_ok,"accepted":False}
    stages["frame-source-partial"]={"exit":partial_stage.get("exit"),"fatal":partial_expected,
        "preheader_refusal":partial_ok,"accepted":False}
    on_audit=log_proof_evidence(on_log,on_stage)
    outer_seen=on_audit["outer_header_seen"] or on_audit["outer_prototype_seen"]
    nested_actual_failure=(not outer_seen and
        on_audit["proof_exit"] in (1,2) and on_audit["first_error_in_nested"] and
        not on_audit["nested_full_normal_unwind_observed"])
    outer_actual_failure=(outer_seen and
        on_audit["nested_full_normal_unwind_observed"] and
        on_audit["proof_exit"] in (1,2) and on_audit["first_error"] is not None and
        on_audit["first_error_in_outer"])
    outer_full=(on_audit["outer_header_seen"] and
        on_audit["nested_full_normal_unwind_observed"] and
        on_audit["proof_exit"]==0 and on_audit["outer_full_normal_unwind_observed"])
    need(on_audit["prefix7_ordered"] and on_audit["nested_before_outer"] and
         not on_audit["errors_before_nested"] and
         on_audit["helper_full_normal_unwind_observed"] and
         (nested_actual_failure or outer_actual_failure or outer_full),
         "FRAME-on first causal error was not in nested/outer after seven-prefix/helper checks")
    on_audit["first_causal_error_attributed"] = bool(
        nested_actual_failure or outer_actual_failure or outer_full)
    on_audit["nested_actual_failure"] = nested_actual_failure
    on_audit["outer_actual_failure"] = outer_actual_failure
    on_audit["outer_full_normal_unwind_observed"] = outer_full
    stages["frame-source-on"]=on_audit
    need(r2mod.tool_snapshot(base_tool,a.proof_root)==production_snapshot and
         r2mod.tool_snapshot(candidate,a.proof_root)==snapshot,
         "canonical base or final FRAME tool changed during proof controls")
    complete=(frame_receipt["source_pair_exact"] and frame_receipt["ten_fingerprints_exact"] and
        frame_receipt["full_normal_readonly_nine_body_capture"] and
        frame_receipt["normal_readonly_refinement"] and old_receipt["source_pair_exact"] and
        old_receipt["ten_fingerprints_exact"] and old_receipt["full_normal_readonly_nine_body_capture"] and
        old_receipt["normal_readonly_refinement"] and old_reached_240 and off_ok and partial_ok and
        on_audit["prefix7_ordered"] and on_audit["nested_before_outer"] and
        not on_audit["errors_before_nested"] and
        on_audit["helper_full_normal_unwind_observed"] and
        on_audit["first_causal_error_attributed"])
    result_classification=("R3_FRAME_TEST_NESTED_REGRESSION_OUTER_NOT_REACHED"
        if complete and nested_actual_failure else
        "R3_FRAME_TEST_DIAGNOSTIC_COMPLETE" if complete else "INCONCLUSIVE")
    result={"classification":result_classification,
        "diagnostic_complete":complete,"source_capture_frame":frame_receipt,
        "source_capture_old_r3":old_receipt,"tool_chain":pins,
        "tool_snapshot":snapshot,"production_snapshot":production_snapshot,
        "stages":stages,"frame_on_first_error":on_audit["first_error"],
        "frame_on_nested_full_normal_unwind":on_audit["nested_full_normal_unwind_observed"],
        "frame_on_outer_full_normal_unwind":on_audit["outer_full_normal_unwind_observed"],
        "nested_actual_failure":nested_actual_failure,
        "frame_on_outer_reached":outer_seen,
        "outer_credit":False,"actual_outer_240_progress":False,
        "wrong_helper_contract_negative_complete":False,
        "wrong_typed_move_edge_negative_complete":False,
        "open_gates":["wrong helper contract/body negative not run",
            "wrong typed Move/cleanup-edge negative not run",
            "malformed source/unit/span negatives open",
            "no actual source acceptance or theorem credit"],
        "actual_source_accepted":False,"target_contract_proved":False,
        "actual_helper_proved":False,"actual_safe_forget_linked":False,
        "verification_accepted":False,"accepted":False}
    write(a.evidence/"diagnostic-audit.json",result)
    return result


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("proof-root","cloud-dir","production-source","compiler-sysroot",
                "evidence","work-root"):
        p.add_argument("--"+key,type=Path,required=True)
    p.add_argument("--deadline-epoch",type=int,required=True)
    a=p.parse_args()
    for key in ("proof_root","cloud_dir","production_source","compiler_sysroot","evidence","work_root"):
        value=getattr(a,key).resolve()
        need(value.is_relative_to(Path("/workspace")),"Cloud workspace path required")
        setattr(a,key,value)
    a.deadline_epoch=int(a.deadline_epoch)
    need(not a.evidence.exists(),"FRAME TEST evidence already exists")
    a.evidence.mkdir(parents=True)
    try:
        result=run(a)
    except Exception as exc:
        prior=read(a.evidence/"diagnostic-audit.json") if (a.evidence/"diagnostic-audit.json").is_file() else {}
        result={**(prior if isinstance(prior,dict) else {}),
            "classification":"INCONCLUSIVE","diagnostic_complete":False,
            "reason":str(exc),"actual_source_accepted":False,"target_contract_proved":False,
            "verification_accepted":False,"accepted":False}
        write(a.evidence/"diagnostic-audit.json",result)
        raise
    need(result.get("diagnostic_complete") is True and result.get("accepted") is False,
         "FRAME diagnostic controls incomplete")


if __name__ == "__main__":
    main()
