#!/usr/bin/env python3
"""Small classifier-only tests on saved logs and synthetic derivatives."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location("outer_bool_auditor", Path(__file__).with_name("outer_bool_auditor.py"))
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    a = parser.parse_args()
    base = a.evidence_root / "allprooflogs/cases/integration"
    prefix = base / "regression-lifetime-negative_outer_bound_escape"
    case = base / "regressions/strict-lifetime" / auditor.TARGET
    log = prefix.with_suffix(".log").read_text()
    ast = (case / "final-current-bound-ast.ml").read_text()
    verified = (case / "verified/lib.rs").read_bytes()
    original = (case / "original/lib.rs").read_bytes()
    stage = json.loads(Path(str(prefix)+"-proof.json").read_text())
    rows = []
    result = auditor.audit(log, ast, verified, original, stage)
    assert result["classification"] == "PASS_POSITIVE_LOCAL_HRTB_CLOSURE", result
    rows.append({"case":"unchanged_saved_evidence","synthetic":False,"classification":result["classification"]})
    mutations = [
        ("registration", "CHALLENGE8_HRTB_EQ", "translator_registration_and_call"),
        ("translator_call", "CHALLENGE8_HRTB_CALL", "translator_registration_and_call"),
        ("actual_callback", auditor.CALL+": Verifying call", "actual_callback"),
        ("normal_recovery", "verified/lib.rs(108,26-27): Verifying call", "normal_resource_closure"),
        ("unwind_recovery", "verified/lib.rs(101,32-33): Verifying call", "unwind_resource_closure"),
        ("cut", "verified/lib.rs(106,9-107,1): Freeing locals.", "two_complete_paths"),
        ("normal_owner_post", "verified/lib.rs(67,12-15): Consuming assertion", "normal_resource_closure"),
        ("unwind_owner_post", "verified/lib.rs(73,12-15): Consuming assertion", "unwind_resource_closure"),
        ("normal_return", "verified/lib.rs(110,2): Executing return statement", "normal_resource_closure"),
        ("unwind_return", "verified/lib.rs(103,22-83): Executing return statement", "unwind_resource_closure"),
        ("lifetime_consumption", "verified/lib.rs(52,1-110,2): Consuming function lifetime token", "two_complete_paths"),
        ("leak", "verified/lib.rs(110,1-2): Leak check.", "two_complete_paths"),
        ("export_marker", "SORT4-CURRENT-BOUND-AST-EXPORT", "export_seal"),
        ("relocation", "STRICT-RELOCATE inner=_32", "relocation_observed"),
        ("target_header", "Verifying function 'negative_outer_bound_escape'", "target_entered_once_and_last"),
        ("completion", "0 errors found (95 statements verified)", "terminal_completion"),
    ]
    for name, token, check in mutations:
        changed = "".join(line for line in log.splitlines(keepends=True) if token not in line)
        assert changed != log, name
        st = copy.deepcopy(stage); st["log_sha256"] = auditor.sha(changed.encode())
        result = auditor.audit(changed, ast, verified, original, st)
        assert result["classification"] == "INCONCLUSIVE" and not result["checks"][check], (name,result)
        rows.append({"case":"missing_"+name,"synthetic":True,"classification":result["classification"],"target_check":check})
    for name, changed in [
        ("truncated_log",log[:log.index(auditor.CALL+": Verifying call")]),
        ("truncated_with_success_banner",log[:log.index(auditor.CALL+": Verifying call")]+log[log.rindex("0 errors found"):])]:
        st=copy.deepcopy(stage);st["log_sha256"]=auditor.sha(changed.encode())
        result=auditor.audit(changed,ast,verified,original,st)
        assert result["classification"] == "INCONCLUSIVE" and not result["checks"]["normal_resource_closure"]
        rows.append({"case":name,"synthetic":True,"classification":result["classification"]})
    for name, changed_ast in [("wrong_projection",ast.replace('"std::ops::FnOnce"','"wrong_trait"')),
                              ("missing_final_ast","")]:
        result=auditor.audit(log,changed_ast,verified,original,stage)
        assert result["classification"] == "INCONCLUSIVE" and not result["checks"]["exact_projection_before_callback"]
        rows.append({"case":name,"synthetic":True,"classification":result["classification"]})
    for name, mutate in [("nonzero_exit",lambda st:st.update(exit=1)),
                         ("stale_log_hash",lambda st:st.update(log_sha256="0"*64)),
                         ("recorded_error",lambda st:st.update(errors=["error: synthetic"]))]:
        st=copy.deepcopy(stage);mutate(st)
        result=auditor.audit(log,ast,verified,original,st)
        assert result["classification"] == "INCONCLUSIVE", name
        rows.append({"case":name,"synthetic":True,"classification":result["classification"]})
    saved={"log":log.encode(),"proof":Path(str(prefix)+"-proof.json").read_bytes(),
        "manifest":(a.evidence_root/"manifest.json").read_bytes(),
        "summary":(a.evidence_root/"summary.json").read_bytes(),
        "inventory":(a.evidence_root/"files-sha256.json").read_bytes()}
    assert auditor.saved_identity(saved)
    for name in saved:
        changed=dict(saved);changed[name]+=b" ";assert not auditor.saved_identity(changed)
        rows.append({"case":"saved_identity_tamper_"+name,"synthetic":True,"classification":"IDENTITY_REFUSED"})
    changed_log="synthetic extra line\n"+log
    st=copy.deepcopy(stage);st["log_sha256"]=auditor.sha(changed_log.encode())
    assert auditor.audit(changed_log,ast,verified,original,st)["classification"]=="PASS_POSITIVE_LOCAL_HRTB_CLOSURE"
    derivative=dict(saved);derivative["log"]=changed_log.encode()
    derivative["proof"]=json.dumps(st).encode()
    assert not auditor.saved_identity(derivative)
    rows.append({"case":"self_consistent_derivative_is_not_saved_build","synthetic":True,"classification":"IDENTITY_REFUSED"})
    report={"classification":"CLASSIFIER_TESTS_PASS","cases":rows,"count":len(rows),
        "auditor_version":auditor.VERSION,"auditor_sha256":auditor.sha(Path(auditor.__file__).read_bytes()),
        "test_sha256":auditor.sha(Path(__file__).read_bytes()),"fresh_proof":False,"proof_credit":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("CLASSIFIER_TESTS_PASS",len(rows))

if __name__ == "__main__": main()
