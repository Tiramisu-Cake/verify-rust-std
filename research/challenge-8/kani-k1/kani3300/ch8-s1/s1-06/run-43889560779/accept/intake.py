#!/usr/bin/env python3
"""Replay offline S1-06 acceptance from pinned request and structured JSON only."""
import gzip, hashlib, json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
TASK = RUN.parent
ART = RUN / "artifacts"
CONTROL = Path("/root/kani-ch8-s1-06-intake-w13")
STD = Path("/root/verify-rust-std-ch8-s1-04-w13")
REQPATH = CONTROL / "ch8-s1-control/CI-REQUEST.json"
REQSHA = "0ff35bdc40434ac6b22b4f4b5919923ab09d849c08c9930f291c014f8b96fe7b"
STD_SHA = "5be85699b8826e3286c0bf89efb9affefac0acb5"
TOOL_SHA = "0aac16ef62da9e9d5645782d458593e5d78143ba"
CONTROL_SHA = "a14a513eb7a77297a0cc10ff6eefa7577c2c383c"
GOOD_GROUPS = {"light-model-u5", "light-corruption-u4", "activation-default-u34", "cell-u34"}

def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(p.read_bytes())
def need(ok, msg):
    if not ok: raise ValueError(msg)
def embedded(files, rel):
    x=files[rel]
    raw=x["text"].encode()
    need(len(raw)==x["bytes"] and sha(raw)==x["sha256"], "embedded member hash/size: "+rel)
    return json.loads(raw)
def source_rel(path):
    prefix="/home/runner/work/kani/kani/export/"
    need(isinstance(path,str) and path.startswith(prefix), "unexpected export path")
    return path[len(prefix):]
def git(repo,*args):
    return subprocess.check_output(["git","-C",str(repo),*args]).decode().strip()
def complete(properties):
    return all(p.get("file") and str(p.get("line"," ")).isdigit() for p in properties)

def main():
    request=read(REQPATH)
    request_sha=sha(REQPATH.read_bytes())
    need(request_sha==REQSHA, "request SHA")
    need(request["std_sha"]==STD_SHA and request["tool_sha"]==TOOL_SHA, "request pins")
    need(json.loads((RUN/"run-identity.json").read_text())["head_sha"]==CONTROL_SHA, "run head")
    need(git(CONTROL,"rev-parse","HEAD")==CONTROL_SHA and not git(CONTROL,"status","--porcelain"), "control checkout")
    need(git(STD,"rev-parse","HEAD")==STD_SHA and not git(STD,"status","--porcelain"), "source checkout")
    need(git(STD,"rev-parse",STD_SHA+"^{tree}")==request["std_tree"], "source tree")
    need(git(CONTROL,"rev-parse",TOOL_SHA+"^{tree}")==request["tool_tree"], "tool tree")
    need(len(request["execution_groups"])==14 and len(request["rows"])==35, "request dimensions")
    row_by={r["id"]:r for r in request["rows"]}
    group_for={rid:g["id"] for g in request["execution_groups"] for rid in g["row_ids"]}
    need(len(group_for)==35, "execution group row mapping")
    artifact_meta=read(RUN/"artifacts-metadata.json")
    need(len(artifact_meta["artifacts"])==14, "artifact count")
    am={a["name"].split("-1-",1)[1]:a for a in artifact_meta["artifacts"]}
    need(set(am)=={g["id"] for g in request["execution_groups"]}, "artifact group set")
    all_rows={}; groups=[]; missing_records=[]
    for gid in sorted(am):
        a=am[gid]; archive=ART/a["name"]
        integ=read(archive/"zip-integrity.json")
        need(integ["github_digest_match"] is True and "sha256:"+integ["sha256"]==a["digest"], "archive digest:"+gid)
        gz=archive/"group-evidence.json.gz"
        bundle=json.loads(gzip.decompress(gz.read_bytes()))
        need(bundle["schema"]=="ch8-s1-05-artifact-v1" and bundle["state"]=="PACKAGED", "bundle state:"+gid)
        files=bundle["files"]
        group_key=next(k for k in files if k.startswith("groups/") and k.endswith("/receipt.json") and "/compile/" not in k)
        group_rel=group_key.rsplit("/",1)[0]
        receipt=embedded(files, group_rel+"/receipt.json")
        exp=embedded(files, group_rel+"/export.json")
        rich=embedded(files, group_rel+"/properties.json")
        compile_receipt=embedded(files, group_rel+"/compile/receipt.json")
        need(receipt.get("group")==gid and receipt.get("request_sha256")==request_sha, "receipt group/request:"+gid)
        need(compile_receipt.get("request_sha256")==request_sha and compile_receipt.get("std_sha")==STD_SHA and compile_receipt.get("tool_sha")==TOOL_SHA, "compile pins:"+gid)
        need(receipt.get("source_before")==receipt.get("source_after"), "source snapshot drift:"+gid)
        need(receipt.get("source_before",{}).get("std_sha")==STD_SHA and receipt.get("source_before",{}).get("tool_sha")==TOOL_SHA, "source pins:"+gid)
        variant=receipt.get("variant"); expected_files=dict(request["changed_file_sha256"])
        if variant!="production":
            v=request["variants"][variant]; expected_files.update(v["changed_file_sha256"])
            patch_file=CONTROL/"ch8-s1-control"/v["patch"]
            need(sha(patch_file.read_bytes())==v["sha256"]==receipt.get("source_under_test",{}).get("patch_sha256"), "variant patch:"+variant)
        need(receipt.get("source_under_test",{}).get("file_sha256")==expected_files, "source-under-test files:"+gid)
        ex={h["name"]:h for h in exp.get("harnesses",[])}
        rh={h["name"]:h for h in rich.get("harnesses",[])}
        selected=set(receipt.get("selectors",[]))
        need(selected and selected.issubset(ex) and selected.issubset(rh), "selector/harness reconciliation:"+gid)
        misses=[]; inventory_by={}
        for selector in sorted(selected):
            h=ex[selector]; hp=rh[selector].get("properties",[])
            by={p.get("id"):p for p in hp if p.get("id")}
            need(len(by)==len(hp), "duplicate/missing property ids:"+selector)
            need(h.get("n_properties")==len(hp), "property count:"+selector)
            # Verify bucket partition and ID/status/class agreement even when coordinates are absent.
            checks=h["checks"]; covers=h["covers"]
            cb=("failure","unreachable","undetermined","error","unknown","other")
            vb=("satisfied","unsatisfiable","unreachable","undetermined","error","unknown","other")
            need(checks["total"]==checks["success"]+sum(len(checks[k]) for k in cb), "check partition:"+selector)
            need(covers["total"]==sum(len(covers[k]) for k in vb), "cover partition:"+selector)
            for buckets, inventory in ((cb,checks),(vb,covers)):
                for bucket in buckets:
                    for pid in inventory[bucket]:
                        p=by.get(pid); need(p and p.get("status")==bucket.upper(), "bucket property/status:"+pid)
            for p in hp:
                if not p.get("file") or not str(p.get("line","")).isdigit():
                    m={"group":gid,"selector":selector,"id":p["id"],"class":p.get("class"),"description":p.get("description"),"status":p.get("status"),"location_display":p.get("location_display"),"policy_treatment":"NOT_APPLIED"}
                    misses.append(m); missing_records.append(m)
            for u in h.get("unsupported_constructs",[]):
                p=by.get(u.get("id"))
                need(p and p.get("class")==u.get("class")=="unsupported_construct" and p.get("status")==u.get("status")=="SUCCESS" and p.get("file")==u.get("file") and str(p.get("line"))==str(u.get("line")), "unsupported link:"+str(u.get("id")))
            inventory_by[selector]=(h,hp,by,complete(hp))
        rowids=[r for r,g in group_for.items() if g==gid]
        harnesses=[]
        for rid in rowids:
            row=row_by[rid]; selector=row["selector"]
            h,hp,by,loc_complete=inventory_by[selector]
            all_rows[rid]=(gid,row,h,hp,by,loc_complete)
            harnesses.append({"row":rid,"selector":selector,"source_verdict":h.get("outcome",{}).get("verdict"),"n_properties":len(hp),"n_failed":h.get("n_failed"),"unreachable_class_success":sum(p.get("class")=="unreachable" and p.get("status")=="SUCCESS" for p in hp),"check_status_unreachable":len(h["checks"]["unreachable"]),"cover_status_unreachable":len(h["covers"]["unreachable"]),"covers_satisfied":len(h["covers"]["satisfied"]),"unsupported_constructs":len(h.get("unsupported_constructs",[])),"locations_complete":loc_complete,"missing_sites":[m["id"] for m in misses if m["selector"]==selector]})
        before=receipt.get("tool_fingerprints_before",{}).get("binaries",{})
        after=receipt.get("tool_fingerprints_after",{}).get("binaries",{})
        bin_state="MATCH" if before and after and {k:v.get("sha256") for k,v in before.items()}=={k:v.get("sha256") for k,v in after.items()} else "UNKNOWN_AFTER_RUN_STOPPED"
        groups.append({"id":gid,"artifact_id":a["id"],"artifact_name":a["name"],"archive_sha256":integ["sha256"],"request_sha256":request_sha,"receipt_state":receipt.get("state"),"inventory_locations":"COMPLETE" if not misses else "INCOMPLETE","missing_sites":misses,"source_snapshot":"MATCH","binary_fingerprint_after":bin_state,"harnesses":harnesses})

    results=[]
    for rid,row in row_by.items():
        gid,r,h,hp,by,loc_complete=all_rows[rid]
        oracle=row.get("oracle"); oracle_check="NOT_APPLICABLE"; oracle_id_record=None
        if row["expected"]=="DETECTED":
            pid=oracle["property_id"] if oracle else None; p=by.get(pid)
            failed_ids=[q.get("id") for q in h.get("failed_properties",[])]
            oracle_id_record={"expected_id":pid,"observed_failed_ids":failed_ids,"binding":"PENDING"}
            exact=bool(p and failed_ids==[pid] and p.get("status")=="FAILURE" and p.get("class")==oracle.get("class") and source_rel(p.get("file"))==oracle.get("file") and str(p.get("line"))==str(oracle.get("line")) and h.get("outcome")=={"kind":"COMPLETED","verdict":"FAILURE"})
            if exact and oracle.get("description"):
                exact=p.get("description")==oracle["description"]
            if exact and row["variant"] in request.get("variants",{}):
                variant=request["variants"][row["variant"]]
                patch=(CONTROL/"ch8-s1-control"/variant["patch"]).read_text()
                marker=oracle.get("intended_message") or row.get("failure_description") or variant.get("marker")
                exact=bool(marker and marker in patch)
            elif exact:
                f=STD/oracle["file"]
                source_lines=f.read_text().splitlines()
                n=int(oracle["line"])-1
                exact=sha(f.read_bytes())==oracle["source_sha256"] and source_lines[n:n+len(oracle["assertion_context"])]==oracle["assertion_context"]
            if exact:
                oracle_check="EXACT_ID_CLASS_STATUS_FILE_LINE_SOLE_FAILURE_SOURCE_OR_PATCH_PIN"
                oracle_id_record["binding"]=oracle_check
            else: oracle_check="MISMATCH_OR_UNRESOLVED"
        elif h.get("outcome",{}).get("verdict")=="SUCCESS" and not h.get("failed_properties"):
            oracle_check="POSITIVE_VERDICT_NO_FAILURES"
        # Source binding evidence from the exact request file and source anchors.
        sb=request.get("source_bindings",{}).get(rid); anchors=[]; required=[]; covers=[]
        if sb:
            src=STD/sb["file"]
            lines=src.read_text().splitlines()
            source_sha=sha(src.read_bytes())
            need(source_sha==sb["sha256"], "source binding SHA:"+rid)
            for loc in sb["locations"]:
                need(1<=loc["line"]<=len(lines) and lines[loc["line"]-1]==loc["source"], "source anchor:"+rid)
                anchors.append({"line":loc["line"],"source":loc["source"]})
            for msg in r.get("required_success_messages",[]):
                literal=[i+1 for i,s in enumerate(lines) if msg in s]
                calls=[]
                for n in literal:
                    start=n
                    for back in range(n,max(0,n-6),-1):
                        if "assert!" in lines[back-1]: start=back; break
                    calls.append(start)
                suffix=sb["file"].split("library/core/",1)[1]
                root_name=r["selector"].split("::")[-1]
                candidates=[p for p in by.values() if p.get("status")=="SUCCESS" and p.get("class")=="assertion" and p.get("file","").endswith(suffix) and str(p.get("line")) in {str(n) for n in calls} and root_name in p.get("id","").split(".assertion.",1)[0] and "placeholder message; Kani doesn't support message formatted at runtime" in p.get("description","")]
                bound=len(literal)==1 and len(calls)==1 and len(candidates)==1
                required.append({"message":msg,"source_lines":literal,"assertion_call_lines":calls,"property_ids":[p["id"] for p in candidates],"binding":"EXACT_UNIQUE_PLACEHOLDER_ASSERTION" if bound else "PENDING"})
            for msg in r.get("required_cover_messages",[]):
                hits=[p for p in by.values() if p.get("class")=="cover" and p.get("description")==msg]
                ok=len(hits)==1 and hits[0].get("status")=="SATISFIED" and hits[0]["id"] in h["covers"]["satisfied"]
                covers.append({"message":msg,"property_id":hits[0].get("id") if len(hits)==1 else None,"status":hits[0].get("status") if len(hits)==1 else None,"binding":"EXACT_SATISFIED_ID" if ok else "PENDING"})
        # Keep failed-group unknown separate from per-row missing coordinates.
        row_missing=[m for m in missing_records if m["group"]==gid and m["selector"]==r["selector"]]
        pending=["GROUP_INTAKE_COMPLETENESS"] if gid not in GOOD_GROUPS else []
        if row_missing: pending.append("PROPERTY_COORDINATE_COMPLETENESS")
        if any(c["binding"]!="EXACT_SATISFIED_ID" for c in covers): pending.append("REQUIRED_COVER_MESSAGE_BINDING")
        if any(q["binding"]!="EXACT_UNIQUE_PLACEHOLDER_ASSERTION" for q in required): pending.append("REQUIRED_SUCCESS_MESSAGE_BINDING")
        if oracle_check in ("MISMATCH_OR_UNRESOLVED",): pending.append("PREDECLARED_NEGATIVE_ORACLE")
        if r.get("mode")=="PFC": pending.append("FULL_QUALIFIED_TARGET_CONTRACT_WRAPPER_BINDING")
        check_unreachable=list(h["checks"]["unreachable"]); cover_unreachable=list(h["covers"]["unreachable"])
        class_unreachable_success=[p["id"] for p in hp if p.get("class")=="unreachable" and p.get("status")=="SUCCESS"]
        if check_unreachable or cover_unreachable: pending.append("UNREACHABLE_STATUS_ROLE_AND_POST_FRAME_RELATION_OBLIGATION_BINDING")
        # Missing post-run tool hashes remain a separate gate and are not caused by missing property coordinates.
        if groups[[g["id"] for g in groups].index(gid)]["binary_fingerprint_after"]!="MATCH": pending.append("BINARY_AFTER_RUN_FINGERPRINT")
        companion=None
        if r.get("companion"):
            cid=r["companion"]; ci=all_rows.get(cid)
            need(ci is not None, "companion row absent:"+rid)
            cgid,cr,ch,chp,cby,cloc=ci
            cg=next(g for g in groups if g["id"]==cgid)
            cverdict=ch.get("outcome",{}).get("verdict")
            companion={"id":cid,"group":cgid,"same_run":True,"source_verdict":cverdict,"row_locations_complete":cloc,"group_qualification":"SOURCE_OBSERVATION_ONLY" if cgid in GOOD_GROUPS else "UNKNOWN","binary_after_fingerprint":cg["binary_fingerprint_after"]}
            if cverdict!="SUCCESS": pending.append("REQUIRED_COMPANION_SOURCE_SUCCESS")
            if cgid not in GOOD_GROUPS: pending.append("REQUIRED_COMPANION_GROUP_INTAKE_COMPLETENESS")
            if not cloc: pending.append("REQUIRED_COMPANION_PROPERTY_COORDINATES")
            if cg["binary_fingerprint_after"]!="MATCH": pending.append("REQUIRED_COMPANION_BINARY_AFTER_FINGERPRINT")
        results.append({"id":rid,"group":gid,"selector":r["selector"],"expected":r["expected"],"mode":r.get("mode"),"source_reported_verdict":h.get("outcome",{}).get("verdict"),"source_observation":oracle_check,"qualification":"SOURCE_OBSERVATION_ONLY" if gid in GOOD_GROUPS else "UNKNOWN","qualification_basis":"COMPLETE_GROUP_STRUCTURED_OBSERVATION_ONLY" if gid in GOOD_GROUPS else "FAILED_GROUP_INCOMPLETE_INTAKE","oracle_binding":oracle_id_record,"row_location_complete":not row_missing,"missing_sites":row_missing,"unreachable_site_observation":{"class_unreachable_success_ids":class_unreachable_success,"class_unreachable_stock_role":"MIR_UNREACHABLE_GUARD_ASSERTION","check_status_unreachable_ids":check_unreachable,"cover_status_unreachable_ids":cover_unreachable,"role_and_obligation_binding":"PENDING" if check_unreachable or cover_unreachable else "NOT_BLOCKED_BY_CLASS_UNREACHABLE_SUCCESS"},"required_success":required,"required_covers":covers,"source_anchors":anchors,"same_run_companion":companion,"acceptance":"PENDING" if pending else "STRUCTURED_OBSERVATION_ONLY","pending_gates":sorted(set(pending)),"counterfactual_location_policy":"NOT_APPLIED","proof_credit":"NONE"})
    need(len(results)==35 and len(groups)==14, "final counts")
    incomplete=[r for r in results if not r["row_location_complete"]]
    totals={"groups":14,"groups_location_complete":sum(g["inventory_locations"]=="COMPLETE" for g in groups),"groups_location_incomplete":sum(g["inventory_locations"]!="COMPLETE" for g in groups),"rows":35,"rows_location_incomplete":len(incomplete),"rows_without_missing_site":35-len(incomplete),"missing_property_records":len(missing_records),"missing_site_ids":sorted(set(m["id"] for m in missing_records)),"missing_site_statuses":sorted(set(m["status"] for m in missing_records)),"missing_site_classes":sorted(set(m["class"] for m in missing_records)),"class_unreachable_success_properties":sum(h["unreachable_class_success"] for g in groups for h in g["harnesses"]),"check_status_unreachable_properties":sum(h["check_status_unreachable"] for g in groups for h in g["harnesses"]),"cover_status_unreachable_properties":sum(h["cover_status_unreachable"] for g in groups for h in g["harnesses"]),"exact_negative_oracle_rows":sum(x["source_observation"].startswith("EXACT_ID_CLASS_STATUS") for x in results),"positive_source_success_rows":sum(x["source_observation"]=="POSITIVE_VERDICT_NO_FAILURES" for x in results),"required_cover_bindings_exact":sum(c["binding"]=="EXACT_SATISFIED_ID" for x in results for c in x["required_covers"]),"required_success_bindings_exact":sum(q["binding"]=="EXACT_UNIQUE_PLACEHOLDER_ASSERTION" for x in results for q in x["required_success"]),"binary_after_fingerprint_groups_missing":sum(g["binary_fingerprint_after"]!="MATCH" for g in groups),"rows_qualified":0,"proof_credit":"NONE"}
    report={"schema":"ch8-s1-06-offline-acceptance-v1","run":43889560779,"qualified_acceptance":"PENDING","proof_credit":"NONE","control_sha":CONTROL_SHA,"source_sha":STD_SHA,"tool_sha":TOOL_SHA,"request_sha256":request_sha,"artifact_metadata_sha256":sha((RUN/"artifacts-metadata.json").read_bytes()),"totals":totals,"groups":groups,"rows":results,"policy":{"current_policy":"FAIL_CLOSED_LOCATION_REQUIREMENT_RETAINED","counterfactual_location_policy":"NOT_APPLIED","distinction":"class=unreachable/status=SUCCESS is a successful stock MIR-Unreachable guard assertion and is not status=UNREACHABLE; coordinates alone do not resolve post/frame/relation obligation roles, covers, wrappers, oracle, or binary-after gates."},"limits":["All classification consumes compact structured JSON members only; stdout/stderr previews and raw logs were not inspected.","The four complete groups and ten failed/incomplete groups are distinguished. Per-row missing-site count is separate from group-level completeness; all rows in failed groups remain UNKNOWN.","Exact located records support source/property observations even in incomplete rows; qualification of every row in a failed group remains UNKNOWN. No missing location is inferred from identifier, count, group order, or function name.","A same-run source verdict or exact negative oracle is a structured observation, not independent proof credit.","The full qualified target/contract-wrapper binding and post/frame/relation role analysis remain pending as applicable. Proof credit B1/B2 remains NONE; it is reported separately from qualification.","No counterfactual relaxation of the exact coordinate policy was applied; no historical receipts or ledgers changed."]}
    (HERE/"ACCEPT.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(totals,sort_keys=True))
if __name__=="__main__": main()
