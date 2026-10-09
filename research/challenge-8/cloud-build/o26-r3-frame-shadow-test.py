#!/usr/bin/env python3
"""Cloud-only exact FRAME-shadow diagnostic; never grants proof acceptance."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path("research/challenge-8")
SHADOW_MANIFEST = ROOT / "overnight-assume-actual/O26-R3-FRAME-SHADOW-TEST.json"
FRAME_MANIFEST = ROOT / "overnight-assume-actual/O26-R3-FRAME-TEST.json"
FRAME_PAIR = ("SORT4_R3_FRAME_TEST_REPO_ROOT", "SORT4_R3_FRAME_TEST")
SHADOW_PAIR = ("SORT4_R3_FRAME_SHADOW_TEST_REPO_ROOT", "SORT4_R3_FRAME_SHADOW_TEST")
ORIGINAL = "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5"
FRAME_SOURCE = "8543e99940897e3289f9f57fe3edc30fa4cffbba713b68aab36eb49d3faac816"
R3_SOURCE = "a95aff14592b167c62c53c7ed726128ee86c7c19768cfe613504cdec841f8463"
OLD_FRAME_ERROR = ("verified/lib.rs(231,49-57): error: Type mismatch. Actual: *Element. "
                   "Expected: std::mem::MaybeUninit<?>.")
SHADOW_OFF_FATAL = 'Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: certificate mismatch: owner exact verified source SHA256")'
SHADOW_PARTIAL_FATAL = 'Fatal error: exception Failure("SORT4-R3-FRAME-SHADOW-TEST: certificate mismatch: exact root/test opt-in pair")'
ERROR = re.compile(r"(?m)^.*: error: .*|^Error:.*$|^Fatal error:.*$")
NAMES = (
    "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new",
    "sort4_checked_as_mut_ptr", "sort4_checked_pointer_drop",
    "sort4_checked_generic_drop", "checked_transmute_neo_pointer",
    "checked_assume_init_pointer", "checked_forget_owned",
    "select_unpredictable",
    "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop",
)


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def read(path: Path) -> dict:
    need(path.is_file(), f"missing FRAME-shadow input: {path}")
    value = json.loads(path.read_text())
    need(isinstance(value, dict), f"FRAME-shadow JSON is not an object: {path}")
    return value


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha(path: Path) -> str:
    need(path.is_file(), f"missing file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_helper(a):
    path = a.cloud_dir / "o26-r3-frame-test.py"
    spec = importlib.util.spec_from_file_location("frame_test_shared", path)
    need(spec is not None and spec.loader is not None, "FRAME helper unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def shadow_chain(a, shared):
    manifests, chain = shared.expected_chain(a)
    profile = read(a.proof_root / SHADOW_MANIFEST)
    base = manifests["frame"]
    need(profile.get("classification") == "EXPERIMENTAL_O26_R3_FRAME_SHADOW_TEST_NOT_ACCEPTED" and
         profile.get("accepted") is False and profile.get("verification_accepted") is False and
         profile.get("parent_profile", "").endswith("O26-R3-FRAME-TEST.json") and
         profile.get("parent_translator_sha256") == base.get("test_translator_sha256") and
         profile.get("typed_outer_graph") == base.get("typed_outer_graph") and
         profile.get("runtime_spec_kernel_parser_exporter_refiner_modified") is False and
         profile.get("actual_helper_proved") is False and
         profile.get("actual_nested_drop_proved_in_this_profile") is False and
         profile.get("opt_in") == {SHADOW_PAIR[0]: "exact proof root", SHADOW_PAIR[1]: "1"} and
         set(profile.get("required_parent_opt_ins", [])) >=
             set(base.get("required_parent_opt_ins", [])) | {FRAME_PAIR[0] + "/TEST"},
         "FRAME-shadow manifest parent/tool/source/opt-in contract differs")
    source = profile.get("source") or {}
    transform = profile.get("source_transform") or {}
    observed = profile.get("observed_capture") or {}
    frame_source = base.get("source") or {}
    shadow_bodies = source.get("body_sha256") or []
    frame_bodies = frame_source.get("body_sha256") or []
    mir_relation = all(isinstance(observed.get(mode+"_body_sha256"), list) and
        len(observed[mode+"_body_sha256"]) == 9 and
        all(isinstance(h, str) and re.fullmatch(r"[0-9a-f]{64}", h)
            for h in observed[mode+"_body_sha256"] + [observed.get(mode+"_whole_decoded_mir_sha256")]) and
        all((observed[mode+"_body_sha256"][i] == base["observed_capture"][mode+"_body_sha256"][i])
            for i in (*range(7), 8)) and
        observed[mode+"_body_sha256"][7] != base["observed_capture"][mode+"_body_sha256"][7]
        for mode in ("normal", "readonly"))
    need(transform.get("parent_verified_sha256") == FRAME_SOURCE and
         transform.get("original_sha256") == ORIGINAL and
         source.get("original_sha256") == ORIGINAL and
         all(isinstance(source.get(k), str) and re.fullmatch(r"[0-9a-f]{64}", source[k])
             for k in ("verified_sha256", "unit_sha256")) and
         all(isinstance(h, str) and re.fullmatch(r"[0-9a-f]{64}", h) for h in shadow_bodies) and
         source.get("verified_sha256") != FRAME_SOURCE and
         source.get("unit_sha256") != frame_source.get("unit_sha256") and
         len(shadow_bodies) == len(frame_bodies) == 9 and
         all(shadow_bodies[i] == frame_bodies[i] for i in (*range(7), 8)) and
         shadow_bodies[7] != frame_bodies[7] and mir_relation and
         transform.get("source_order") == list(shared.NAMES) and
         source.get("verified_sha256") == transform.get("verified_sha256") and
         transform.get("case_name") == "nine-body-wrapper-input-relation-frame-shadow" and
         transform.get("shadow_internal_names") == {"true_val":"true_val_1","false_val":"false_val_1"} and
         transform.get("changed_late_comment_names") == [
             "conditional_wrapper_matches_input","shadow_false_wrapper_matches_input",
             "shadow_true_wrapper_matches_input"] and
         transform.get("verified_source_reversible_three_late_comment_substitutions") is True and
         transform.get("actual_runtime_unchanged") is True and transform.get("ghost_strip_identity") is True and
         transform.get("accepted") is False and transform.get("verification_accepted") is False and
         len(source.get("body_sha256", [])) == 9 and
         isinstance(observed.get("normal_body_sha256"), list) and
         isinstance(observed.get("readonly_body_sha256"), list) and
         len(observed["normal_body_sha256"]) == len(observed["readonly_body_sha256"]) == 9,
         "FRAME-shadow exact source or full nine-body MIR pins are incomplete")
    item = {"kind": "frame-shadow", "manifest": profile,
        "parent": profile.get("parent_translator_sha256"),
        "patch": profile.get("test_patch"), "patch_sha256": profile.get("test_patch_sha256"),
        "result": profile.get("test_translator_sha256")}
    need(all(isinstance(item.get(k), str) and re.fullmatch(r"[0-9a-f]{64}", item[k])
             for k in ("parent", "patch_sha256", "result")) and isinstance(item.get("patch"), str) and
         profile.get("expected_controls", {}).get("frame_off_fatal") == SHADOW_OFF_FATAL and
         profile.get("expected_controls", {}).get("frame_partial_fatal") == SHADOW_PARTIAL_FATAL,
         "FRAME-shadow patch/result/control pins are incomplete")
    need(sha(a.proof_root / ROOT / item["patch"]) == item["patch_sha256"],
         "FRAME-shadow patch bytes differ from the manifest pin")
    chain.append(item)
    return manifests, profile, chain


def capture_shadow(a, tool: Path, evidence: Path):
    need(not evidence.exists(), "fresh shadow capture evidence already exists")
    cmd = [sys.executable, str(a.proof_root / ROOT / "overnight-assume-actual/capture.py"),
        "--tool-home", str(tool), "--schema", str(tool / "src/rust_frontend/vf_mir/vf_mir.capnp"),
        "--compiler-sysroot", str(a.compiler_sysroot), "--evidence", str(evidence),
        "--deadline-epoch", str(a.deadline_epoch), "--fingerprint",
        "--wrapper-input-relation-frame-shadow"]
    timeout = a.deadline_epoch - int(time.time()) - 25
    need(timeout > 0, "FRAME-shadow source capture deadline")
    log_path = a.evidence / "frame-shadow-capture-console.log"
    with log_path.open("wb") as log:
        proc = subprocess.run(cmd, cwd=a.proof_root, stdout=log, stderr=subprocess.STDOUT,
                              timeout=timeout, check=False)
    text = log_path.read_text(errors="replace")
    print("FRAME SHADOW SOURCE CAPTURE LOG BEGIN", flush=True)
    print(text, end="" if text.endswith("\n") else "\n", flush=True)
    print("FRAME SHADOW SOURCE CAPTURE LOG END", flush=True)
    need(proc.returncode == 0, f"FRAME-shadow source capture failed: {proc.returncode}")
    summary = read(evidence / "summary.json")
    write(a.evidence / "frame-shadow-capture-receipt.json", {
        "exit": proc.returncode, "summary_sha256": sha(evidence / "summary.json"),
        "console_log_sha256": sha(log_path), "source": summary.get("source"), "accepted": False})
    return summary


def verify_shadow_capture(summary: dict, root: Path, profile: dict):
    expected = profile["source"]
    observed = profile["observed_capture"]
    source = summary.get("source") or {}
    case = root / "nine-body-wrapper-input-relation-frame-shadow"
    transform = profile.get("source_transform") or {}
    full = summary.get("full_body_capture") or {}
    snapshots = (summary.get("fingerprint") or {}).get("snapshots") or {}
    source_pair = (summary.get("classification") == "NINE_BODY_SOURCE_MIR_CALIBRATION_ONLY" and
        summary.get("source_mode") == "wrapper-input-relation-frame-shadow-source-only" and
        summary.get("frontend_refinement_and_full_body_capture") is True and
        source == transform and source.get("verified_sha256") == expected.get("verified_sha256") and
        source.get("parent_verified_sha256") == FRAME_SOURCE and
        source.get("original_sha256") == ORIGINAL and sha(case / "verified/lib.rs") == source.get("verified_sha256") and
        sha(case / "original/lib.rs") == ORIGINAL and source.get("actual_runtime_unchanged") is True and
        source.get("ghost_strip_identity") is True and source.get("verification_accepted") is False and
        source.get("accepted") is False)
    labels={"unit", *(f"body-{i}" for i in range(9))}
    expected_fingerprints={"unit":expected.get("unit_sha256"),
        **{f"body-{i}": value for i,value in enumerate(expected.get("body_sha256", []))}}
    fingerprints=(set(snapshots)==labels and set(expected_fingerprints)==labels and
        all((case / snapshots[label]["file"]).is_file() and
            snapshots[label]["file"] == f"actual-nested-9-{label}.marshal" and
            sha(case / snapshots[label]["file"]) == snapshots[label].get("sha256") == expected_fingerprints[label]
            for label in labels))
    bodies=(set(full)=={"normal", "readonly"} and all(
        full[mode].get("exact_body_count_and_order") is True and
        full[mode].get("whole_decoded_mir_sha256") == observed.get(mode+"_whole_decoded_mir_sha256") and
        sha(case / f"{mode}-mir.txt") == observed.get(mode+"_whole_decoded_mir_sha256") and
        len(full[mode].get("bodies", [])) == 9 and
        all(row.get("index")==i and row.get("defpath")==NAMES[i] and
            row.get("sha256")==sha(case / row["file"]) and
            row.get("sha256")==observed[mode+"_body_sha256"][i]
            for i,row in enumerate(full[mode]["bodies"])) for mode in ("normal", "readonly")))
    guard=summary.get("guard_capture") or {}; stages=guard.get("stages") or {}
    refinement=(guard.get("frontend_refinement") is True and all(
        stages.get(name, {}).get("exit")==0 and stages[name].get("source_unchanged") is True
        for name in ("normal-export", "normal-decode", "readonly-export", "readonly-decode", "refinement")))
    fingerprint=summary.get("fingerprint") or {}
    refusal=(fingerprint.get("classification")=="INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE" and
        fingerprint.get("all_ten_snapshots") is True and fingerprint.get("body_proof_run") is False and
        fingerprint.get("stage", {}).get("exit")==2)
    need(source_pair and fingerprints and bodies and refinement and refusal,
         "fresh FRAME-shadow source/MIR/refinement/fingerprint identity incomplete")
    return {"source_pair_exact":source_pair,"ten_fingerprints_exact":fingerprints,
        "full_normal_readonly_nine_body_capture":bodies,"normal_readonly_refinement":refinement,
        "fingerprint_refusal_no_proof":refusal,"source_sha256":source.get("verified_sha256"),
        "original_sha256":source.get("original_sha256"),"unit_sha256":source.get("unit_sha256"),
        "body_sha256":expected.get("body_sha256"),"accepted":False}


def exact_preheader(stage, log, fatal):
    return (stage.get("exit")==2 and
        [line for line in log.splitlines() if line.startswith("Fatal error:")]==[fatal] and
        ERROR.findall(log)==[fatal] and "Verifying function '" not in log)


def run(a):
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER")=="cloud-build" and
         os.environ.get("LANE")=="o26-input-relation-frame-shadow-test" and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud FRAME-shadow TEST lane required")
    shared=load_helper(a)
    manifests, profile, chain=shadow_chain(a,shared)
    old_parent_pairs=shared.PARENT_PAIRS
    need(not any(os.environ.get(key) for pair in (*old_parent_pairs,FRAME_PAIR,SHADOW_PAIR)
                 for key in pair), "inherited R2/R3/FRAME/shadow opt-in pair")
    out={"classification":"INCONCLUSIVE","diagnostic_complete":False,
        "verification_accepted":False,"accepted":False,"target_contract_proved":False,
        "actual_source_accepted":False,"actual_helper_proved":False,"actual_safe_forget_linked":False}
    write(a.evidence / "diagnostic-audit.json",out)
    tool_snapshot=shared.load("frame_shadow_tool_snapshot",a.cloud_dir/"o26-wrapper-profile.py")
    recipe=shared.load("frame_shadow_proof_recipe",a.cloud_dir/"o26-recipe.py")
    a.production_snapshot=tool_snapshot.tool_snapshot(a.production_source,a.proof_root)
    candidate,snapshot,pins=shared.apply_chain(a,tool_snapshot,chain,a.production_source)
    (a.evidence/"frame-test.patch").rename(a.evidence/"frame-shadow-test.patch")
    # Fresh captures bind the exact old FRAME source and changed shadow source to this final tool.
    old_capture_root=a.evidence/"old-frame-capture"
    old_summary=shared.run_capture(a,candidate,"frame",old_capture_root)
    old_receipt=shared.verify_capture(old_summary,old_capture_root,manifests["frame"]["source"],
        "frame",manifests["frame"].get("observed_capture") or {},manifests["frame"].get("source_transform"))
    shadow_capture_root=a.evidence/"shadow-capture"
    shadow_summary=capture_shadow(a,candidate,shadow_capture_root)
    shadow_receipt=verify_shadow_capture(shadow_summary,shadow_capture_root,profile)
    old_case=old_capture_root/old_summary["source"]["case_name"]
    shadow_case=shadow_capture_root/shadow_summary["source"]["case_name"]
    stages={}

    # Baseline: old FRAME source still reaches the recorded type mismatch at 231.
    shared.FRAME_PAIR=FRAME_PAIR
    shared.PARENT_PAIRS=old_parent_pairs
    baseline,baseline_log=shared.proof_stage(a,recipe,tool_snapshot,candidate,old_case,
        "old-frame-shadow-off-baseline",FRAME_SOURCE,"on",snapshot)
    baseline_audit=shared.log_proof_evidence(baseline_log,baseline)
    baseline_errors=ERROR.findall(baseline_log)
    baseline_outer=baseline_log.find("Verifying function 'select_unpredictable'")
    baseline_error=baseline_log.find(OLD_FRAME_ERROR)
    baseline_ok=(baseline.get("exit")==1 and baseline_errors==[OLD_FRAME_ERROR] and
        baseline_outer>=0 and baseline_error>baseline_outer and
        baseline_audit["prefix7_ordered"] and baseline_audit["helper_full_normal_unwind_observed"] and
        baseline_audit["outer_header_seen"] and baseline_audit["first_error_in_outer"] and
        old_receipt["source_pair_exact"])
    need(baseline_ok,"old FRAME source did not preserve exact line-231 baseline")
    stages["old-frame-source-shadow-off"]={"exit":baseline.get("exit"),
        "first_error":baseline_errors[0],"reached_line_231":baseline_ok,
        "prefix7_ordered":baseline_audit["prefix7_ordered"],
        "helper_full_normal_unwind_observed":baseline_audit["helper_full_normal_unwind_observed"],
        "first_error_in_outer":baseline_audit["first_error_in_outer"],
        "intended_theorem_negative":False,"accepted":False}

    # Shadow controls inherit all R2/R3/COLUMN/nested parents and the FRAME pair.
    shared.FRAME_PAIR=SHADOW_PAIR
    shared.PARENT_PAIRS=(*old_parent_pairs,FRAME_PAIR)
    off,off_log=shared.proof_stage(a,recipe,tool_snapshot,candidate,shadow_case,
        "frame-shadow-source-off",shadow_receipt["source_sha256"],"off",snapshot)
    partial,partial_log=shared.proof_stage(a,recipe,tool_snapshot,candidate,shadow_case,
        "frame-shadow-source-partial",shadow_receipt["source_sha256"],"partial",snapshot)
    on,on_log=shared.proof_stage(a,recipe,tool_snapshot,candidate,shadow_case,
        "frame-shadow-source-on",shadow_receipt["source_sha256"],"on",snapshot)
    expected=profile.get("expected_controls") or {}
    off_fatal=expected.get("frame_off_fatal")
    partial_fatal=expected.get("frame_partial_fatal")
    need(isinstance(off_fatal,str) and isinstance(partial_fatal,str),
         "FRAME-shadow exact off/partial fatal pins are missing")
    off_ok=exact_preheader(off,off_log,off_fatal)
    partial_ok=exact_preheader(partial,partial_log,partial_fatal)
    need(off_ok and partial_ok,"FRAME-shadow source-off/partial missed exact preheader refusal")
    on_audit=shared.log_proof_evidence(on_log,on)
    outer_seen=on_audit["outer_header_seen"] or on_audit["outer_prototype_seen"]
    error_span=re.search(r"verified/lib.rs\((\d+),", on_audit["first_error"] or "")
    beyond_late=(on_audit["proof_exit"]==0 or
        (error_span is not None and int(error_span.group(1))>233))
    on_audit["past_three_late_wrapper_assertions"]=beyond_late
    outer_failure=(outer_seen and on_audit["nested_full_normal_unwind_observed"] and
        on_audit["proof_exit"] in (1,2) and on_audit["first_error"] is not None and
        on_audit["first_error_in_outer"])
    outer_full=(on_audit["outer_header_seen"] and on_audit["nested_full_normal_unwind_observed"] and
        on_audit["proof_exit"]==0 and on_audit["outer_full_normal_unwind_observed"])
    on_ok=(beyond_late and on_audit["prefix7_ordered"] and on_audit["nested_before_outer"] and
        not on_audit["errors_before_nested"] and on_audit["helper_full_normal_unwind_observed"] and
        on_audit["nested_full_normal_unwind_observed"] and outer_seen and
        (outer_failure or outer_full))
    need(on_ok,"FRAME-shadow-on failed before the intended helper/nested/outer proof diagnostic")
    on_audit["outer_actual_failure"]=outer_failure
    on_audit["outer_full_normal_unwind_observed"]=outer_full
    stages["frame-shadow-source-off"]={"exit":off.get("exit"),"fatal":off_fatal,
        "preheader_refusal":off_ok,"accepted":False}
    stages["frame-shadow-source-partial"]={"exit":partial.get("exit"),"fatal":partial_fatal,
        "preheader_refusal":partial_ok,"accepted":False}
    stages["frame-shadow-source-on"]=on_audit
    need(tool_snapshot.tool_snapshot(a.production_source,a.proof_root)==a.production_snapshot and
         tool_snapshot.tool_snapshot(candidate,a.proof_root)==snapshot,
         "canonical production or candidate tool changed during FRAME-shadow controls")
    complete=(old_receipt["source_pair_exact"] and old_receipt["ten_fingerprints_exact"] and
        old_receipt["full_normal_readonly_nine_body_capture"] and old_receipt["normal_readonly_refinement"] and
        shadow_receipt["source_pair_exact"] and shadow_receipt["ten_fingerprints_exact"] and
        shadow_receipt["full_normal_readonly_nine_body_capture"] and shadow_receipt["normal_readonly_refinement"] and
        baseline_ok and off_ok and partial_ok and on_ok)
    classification="R3_FRAME_SHADOW_DIAGNOSTIC_COMPLETE" if complete else "INCONCLUSIVE"
    out={"classification":classification,"diagnostic_complete":complete,
        "source_capture_old_frame":old_receipt,"source_capture_frame_shadow":shadow_receipt,
        "tool_chain":pins,"tool_snapshot":snapshot,"production_snapshot":a.production_snapshot,
        "stages":stages,"frame_shadow_on_first_error":on_audit.get("first_error"),
        "old_frame_line231_baseline_is_not_an_intended_theorem_negative":True,
        "nested_actual_failure":False,"frame_shadow_outer_reached":outer_seen,
        "frame_shadow_outer_full_normal_unwind_observed":outer_full,
        "outer_credit":False,"actual_outer_240_progress":False,
        "wrong_shadow_binding_negative_complete":False,
        "open_gates":["wrong shadow binding/name/source/unit/span controls not run",
            "wrong Move/edge and branch/false-post controls not run",
            "no actual source acceptance or theorem credit"],
        "actual_source_accepted":False,"target_contract_proved":False,
        "actual_helper_proved":False,"actual_safe_forget_linked":False,
        "verification_accepted":False,"accepted":False}
    write(a.evidence/"diagnostic-audit.json",out)
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("proof-root","cloud-dir","production-source","compiler-sysroot","evidence","work-root"):
        p.add_argument("--"+key,type=Path,required=True)
    p.add_argument("--deadline-epoch",type=int,required=True)
    a=p.parse_args()
    for key in ("proof_root","cloud_dir","production_source","compiler_sysroot","evidence","work_root"):
        value=getattr(a,key).resolve()
        need(value.is_relative_to(Path("/workspace")),"Cloud workspace path required")
        setattr(a,key,value)
    a.deadline_epoch=int(a.deadline_epoch)
    need(os.environ.get("LANE")=="o26-input-relation-frame-shadow-test" and not a.evidence.exists(),
         "fresh FRAME-shadow TEST lane/evidence required")
    a.evidence.mkdir(parents=True)
    try:
        result=run(a)
    except Exception as exc:
        prior=read(a.evidence/"diagnostic-audit.json") if (a.evidence/"diagnostic-audit.json").is_file() else {}
        out={**(prior if isinstance(prior,dict) else {}),"classification":"INCONCLUSIVE",
            "diagnostic_complete":False,"reason":str(exc),"target_contract_proved":False,
            "verification_accepted":False,"accepted":False}
        write(a.evidence/"diagnostic-audit.json",out)
        raise
    need(result.get("diagnostic_complete") is True and result.get("accepted") is False,
         "FRAME-shadow diagnostic controls incomplete")


if __name__=="__main__":main()
