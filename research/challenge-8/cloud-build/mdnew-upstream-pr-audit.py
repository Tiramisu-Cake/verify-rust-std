#!/usr/bin/env python3
"""Fail-closed audit of native mysh registration and Rust-suite evidence."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path

BASE = "f76012fb518703b1d98e243ac4f487f16877cfcb"
CANDIDATE = "da4beb61a6c2dd0e80fe4a74c5c230f3adac7cab"
TREE = "50481095a79cb8f517fb61c0a4aa5d026b591b91"
REF = "refs/heads/upstream/manuallydrop-new-successors"
BUNDLE = "10f0afdc4457e919929eebd7333f57944d76e1fce5da4a04ee2914f659d7c189"
REGISTRATION_SHA256 = "a9a3482ec4f748f76cdae5630b9dda657acac174e3b57ef4b6b16eab987a8b2c"
REGISTRATION_BLOB = "d06dfeebedc8ff76aa63e31a99ba57f695e99903"
UNCHANGED_TRANSLATOR_SHA256 = "a15a743c4106891e2fde892e26dd3ab2ab87adca04c12b333e6000c4c063509f"
STOCK = "5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd"
DEPS = "8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580"
RUSTC = "f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f"
FIXTURES = {
    "forget": ("2a6f0d16bd29cc9ea6c10e3b63e6b94000249d72e94d64f99d45cefb277ce1f7", "0cb379e42fe6bd821d5e0d6dd750097b682565d9"),
    "shared_cleanup": ("e3f91c8a2e0dfa9a1c281350b59318b5553847b1940add46d44061662d456d33", "45c97e151bb09a8ec737acfd412777b1cca3e402"),
    "false_normal_post": ("23a1360b673fe6ece1f8903e69aae104f9e8dadfc34061d09062a993f6071f0d", "0ede897d6f2b76e785dd5245d82c4ac808bf636f"),
    "shared_false_unwind": ("24c003dcb4f99c8bec2240dc3a61d5747f8c96b27b518686a0dbe32aef1158db", "221c061f2ea3290d4424376b03f26b401890a636"),
    "dead_code_pre": ("b1317808274abeca09fc9b5b4e9079c7426822347205970217123993e0af70c2", "a54649df69fde7cdfb6d523a128aed296e61dbba"),
}
REGISTRATION = [
    "cd manuallydrop_new_cfg", "verifast forget.rs", "verifast shared_cleanup.rs",
    "verifast -allow_should_fail false_normal_post.rs",
    "verifast -allow_should_fail shared_false_unwind.rs",
    "! verifast dead_code_pre.rs", "cd ..",
]
TRACES = {
    "verifast forget.rs": "PASS: verifast forget.rs",
    "verifast shared_cleanup.rs": "PASS: verifast shared_cleanup.rs",
    "verifast -allow_should_fail false_normal_post.rs": "PASS: verifast -allow_should_fail false_normal_post.rs",
    "verifast -allow_should_fail shared_false_unwind.rs": "PASS: verifast -allow_should_fail shared_false_unwind.rs",
    "! verifast dead_code_pre.rs": "PASS: ! verifast dead_code_pre.rs",
}
DEAD = re.compile(r"dead_code_pre\.rs\(1,1-7,2\): dead code")

class AuditFailure(Exception):
    def __init__(self, message: str, kind: str = "EARLY_OR_WRONG_DIAGNOSTIC"):
        super().__init__(message); self.kind = kind

def need(ok: bool, message: str, kind: str = "EARLY_OR_WRONG_DIAGNOSTIC") -> None:
    if not ok: raise AuditFailure(message, kind)

def read(path: Path) -> bytes:
    need(path.is_file(), f"missing evidence: {path}", "MISSING_EVIDENCE")
    return path.read_bytes()

def sha(path: Path) -> str: return hashlib.sha256(read(path)).hexdigest()

def json_file(path: Path) -> dict:
    try: value=json.loads(read(path))
    except (json.JSONDecodeError,UnicodeDecodeError) as ex:
        raise AuditFailure(f"invalid evidence JSON {path}: {ex}","INCOMPLETE_EVIDENCE") from ex
    need(isinstance(value,dict),f"expected object in {path}","INCOMPLETE_EVIDENCE")
    return value

def git(repo: Path, *args: str) -> str:
    try: return subprocess.check_output(["git","-C",str(repo),*args],text=True,stderr=subprocess.PIPE).strip()
    except (OSError,subprocess.CalledProcessError) as ex:
        raise AuditFailure(f"cannot verify pinned Git source: {ex}","INCOMPLETE_EVIDENCE") from ex

def verify_trace(log: str, code: int) -> dict:
    if code in (124,137,-9): raise AuditFailure(f"native registration timed out (exit {code})","TIMEOUT")
    need(code == 0,f"native mysh registration exited {code}")
    blocks={}
    for command in TRACES:
        suffix=re.escape(command)
        start=re.search(r"(?m)^Starting process \d+: (?:[^\n]*\$ )?"+suffix+r"$",log)
        after=log[start.end():] if start else ""
        passes=list(re.finditer(r"(?m)^PASS: (?:[^\n]*\$ )?"+suffix+r" \(",after))
        need(len(passes)==1,f"missing or duplicate mysh trace for {command}","INCOMPLETE_EVIDENCE")
        finish_match=passes[0]
        finish=(start.end()+finish_match.start()) if start and finish_match else -1
        need(start is not None and finish>=0,f"mysh trace for {command} has no command boundary","INCOMPLETE_EVIDENCE")
        blocks[command]=log[start.end():finish]
    for command in ("verifast forget.rs","verifast shared_cleanup.rs"):
        need(re.search(r"0 errors found \(\d+ statements verified\)",blocks[command]) is not None,
             f"{command} lacks VeriFast's complete success summary","INCOMPLETE_EVIDENCE")
    need(DEAD.search(blocks["! verifast dead_code_pre.rs"]) is not None,
         "dead_code_pre negative control lacks the exact whole-function dead-code diagnostic")
    need("-ignore_unwind_paths" not in log and "-allow_dead_code" not in log,
         "native selected block used a forbidden checker-disabling option")
    return {"mysh_commands":len(TRACES),"dead_code_diagnostic":True}

def verify_provenance(tool: Path, all_logs: Path, native: dict) -> dict:
    identities=json_file(all_logs/"identities.json")
    receipt=json_file(all_logs/"restore-receipt.json")
    runtime=json_file(all_logs/"runtime-components.json")
    certificate=json_file(all_logs.parent/"source-input-certificate.json")
    manifest_path=all_logs/"tool-input/manifest"; bundle_path=all_logs/"tool-input/bundle"
    manifest=json.loads(read(manifest_path))
    infra=identities.get("infra_sha"); proof=identities.get("proof_sha")
    need(isinstance(infra,str) and re.fullmatch(r"[0-9a-f]{40}",infra) and proof==infra,
         "infra/proof delivery identities differ","INCOMPLETE_EVIDENCE")
    need(receipt.get("classification")=="RESTORED_GIT_INPUT" and
         receipt.get("base_commit")==BASE and receipt.get("candidate_commit")==CANDIDATE and
         receipt.get("candidate_tree")==TREE and receipt.get("candidate_ref")==REF and
         receipt.get("bundle_sha256")==BUNDLE and receipt.get("manifest_sha256")==sha(manifest_path) and
         receipt.get("infra_sha")==infra and receipt.get("proof_sha")==proof and
         receipt.get("git_identity_preserved") is True,
         "restore receipt does not bind exact upstream candidate")
    need(certificate.get("lane")=="verifast-mdnew-upstream-pr" and
         certificate.get("infra",{}).get("commit")==certificate.get("infra",{}).get("head")==infra and
         certificate.get("proof",{}).get("commit")==certificate.get("proof",{}).get("head")==proof and
         certificate.get("infra",{}).get("root_tree")==identities.get("infra_tree") and
         certificate.get("proof",{}).get("root_tree")==identities.get("proof_tree") and
         certificate.get("archive_sha256")==identities.get("source_input_archive_sha256"),
         "source-input certificate does not bind exact infra/proof trees")
    need(sha(bundle_path)==BUNDLE and manifest.get("candidate_commit")==CANDIDATE and
         manifest.get("candidate_tree")==TREE and manifest.get("candidate_ref")==REF and
         manifest.get("bundle_sha256")==BUNDLE,
         "tool delivery manifest/bundle pins differ")
    need(git(tool,"rev-parse","HEAD")==CANDIDATE and git(tool,"rev-parse","HEAD^{tree}")==TREE,
         "candidate checkout identity differs")
    need(runtime.get("baseline_source_sha")==BASE and runtime.get("candidate_source_sha")==CANDIDATE and
         runtime.get("candidate_tree")==TREE and runtime.get("stock_distribution_sha256")==STOCK and
         runtime.get("vfdeps_archive_sha256")==DEPS and f"commit-hash: {RUSTC}" in runtime.get("rustc_verbose","") and
         re.fullmatch(r"[0-9a-f]{64}",runtime.get("console_binary_sha256",{}).get("candidate","")) is not None,
         "source-built candidate runtime does not match pinned toolchain")
    proof_paths=certificate.get("proof",{}).get("restored_paths",[])
    for rel, expected in ((f"research/challenge-8/verifast-input/{CANDIDATE}/bundle",BUNDLE),
                          (f"research/challenge-8/verifast-input/{CANDIDATE}/manifest",sha(manifest_path))):
        matches=[x for x in proof_paths if x.get("path")==rel]
        need(len(matches)==1 and matches[0].get("sha256")==expected,
             f"source certificate lacks exact restored proof input {rel}","INCOMPLETE_EVIDENCE")
    infra_root=Path(__file__).resolve().parents[3]
    infra_paths=certificate.get("infra",{}).get("restored_paths",[])
    for rel in ("research/challenge-8/cloud-build/run-verifast-mdnew-cfg.sh",
                "research/challenge-8/cloud-build/run-verifast-mdnew-upstream-pr.sh",
                "research/challenge-8/cloud-build/restore-verifast-pr-input.py",
                "research/challenge-8/cloud-build/mdnew-upstream-pr-audit.py",
                "research/challenge-8/cloud-build/test-verifast-mdnew-upstream-pr.py",
                "research/challenge-8/cloud-build/verifast-upstream-pr-phase-test.py",
                "research/challenge-8/cloud-build/recipes/verifast-mdnew-upstream-pr.json"):
        matches=[x for x in infra_paths if x.get("path")==rel]
        need(len(matches)==1 and matches[0].get("sha256")==sha(infra_root/rel),
             f"source certificate lacks exact infra input {rel}","INCOMPLETE_EVIDENCE")
    need(manifest.get("purpose")=="mdnew-cfg-cloud-delivery" and manifest.get("base_commit")==BASE and
         manifest.get("candidate_commit")==CANDIDATE and manifest.get("candidate_tree")==TREE,
         "candidate manifest differs from authorized delivery")
    selected=manifest.get("selected_files",{})
    expected_paths={"src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
      "tests/rust/purely_unsafe/manuallydrop_new_cfg/README.md",
      "tests/rust/purely_unsafe/manuallydrop_new_cfg/dead_code_pre.rs",
      "tests/rust/purely_unsafe/manuallydrop_new_cfg/false_normal_post.rs",
      "tests/rust/purely_unsafe/manuallydrop_new_cfg/forget.rs",
      "tests/rust/purely_unsafe/manuallydrop_new_cfg/shared_cleanup.rs",
      "tests/rust/purely_unsafe/manuallydrop_new_cfg/shared_false_unwind.rs",
      "tests/rust/testsuite.mysh"}
    need(set(selected)==expected_paths,"candidate source manifest allowlist differs","INCOMPLETE_EVIDENCE")
    translator="src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
    need(selected.get(translator,{}).get("sha256")==UNCHANGED_TRANSLATOR_SHA256,
         "translator bytes differ from the already validated 8f candidate","INCOMPLETE_EVIDENCE")
    for name,(expected,blob) in FIXTURES.items():
        rel=f"tests/rust/purely_unsafe/manuallydrop_new_cfg/{name}.rs"
        actual=sha(tool/rel)
        need(actual==expected==native.get("fixtures",{}).get(name,{}).get("sha256") and
             git(tool,"rev-parse",f"{CANDIDATE}:{rel}")==blob==native["fixtures"][name].get("git_blob"),
             f"{name} fixture bytes/Git blob differ from frozen source")
        need(manifest.get("fixtures",{}).get(rel,{}).get("sha256")==expected and
             manifest.get("fixtures",{}).get(rel,{}).get("git_blob")==blob,
             f"{name} fixture differs from exact delivery manifest","INCOMPLETE_EVIDENCE")
    reg="tests/rust/testsuite.mysh"
    need(sha(tool/reg)==native.get("registration_sha256") and
         git(tool,"rev-parse",f"{CANDIDATE}:{reg}")==native.get("registration_git_blob"),
         "native test registration does not match pinned source")
    return {"infra_sha":infra,"proof_sha":proof,"candidate":CANDIDATE,"tree":TREE,
            "bundle_sha256":BUNDLE,"manifest_sha256":sha(manifest_path),
            "source_certificate_sha256":sha(all_logs.parent/"source-input-certificate.json"),
            "candidate_console_sha256":runtime["console_binary_sha256"]["candidate"]}

def verify_stage(root: Path, record: dict, key: str, allowed: tuple[int,...]=(0,)) -> str:
    item=record.get(key,{})
    need(item.get("path") and item.get("path")==Path(item["path"]).name,
         f"{key} log path is absent or unsafe","INCOMPLETE_EVIDENCE")
    path=root/item["path"]; data=read(path)
    need(hashlib.sha256(data).hexdigest()==item.get("sha256"),f"{key} log digest mismatch","INCOMPLETE_EVIDENCE")
    code=item.get("exit_status")
    exit_path=item.get("exit_status_path"); resource_path=item.get("resources_path")
    need(exit_path==Path(exit_path).name and resource_path==Path(resource_path).name,
         f"{key} exit/resource receipt path is unsafe","INCOMPLETE_EVIDENCE")
    exit_file=root/exit_path; resource_file=root/resource_path
    try: recorded=int(read(exit_file).decode().strip())
    except (UnicodeDecodeError,ValueError) as ex:
        raise AuditFailure(f"{key} exit receipt is malformed","INCOMPLETE_EVIDENCE") from ex
    resources=read(resource_file)
    need(hashlib.sha256(resources).hexdigest()==item.get("resources_sha256"),
         f"{key} resource receipt digest mismatch","INCOMPLETE_EVIDENCE")
    need(recorded==code,f"{key} manifest and exit receipt disagree","INCOMPLETE_EVIDENCE")
    if code in (124,137,-9):
        if key=="make_test_run": return "TIMEOUT"
        raise AuditFailure(f"{key} timed out (exit {code})","TIMEOUT")
    need(code in allowed,f"{stem} exited {code}")
    return "PASS" if code==0 else "NOT_RUN"

def audit(tool: Path, all_logs: Path) -> dict:
    tool=tool.resolve(); all_logs=all_logs.resolve(); native=json_file(all_logs/"native-input.json")
    need(native.get("selected_commands")==REGISTRATION,"selected commands differ from native registration allowlist","INCOMPLETE_EVIDENCE")
    script=read(all_logs/"selected-manuallydrop-registration.mysh")
    need(hashlib.sha256(script).hexdigest()==native.get("selected_script_sha256"),"selected mysh script digest differs","INCOMPLETE_EVIDENCE")
    text=script.decode()
    need([line.strip() for line in text.splitlines() if line.strip()]==["cd purely_unsafe"]+REGISTRATION+["cd .."],
         "selected mysh input is not the exact native registration block","INCOMPLETE_EVIDENCE")
    need("-ignore_unwind_paths" not in text and "-allow_dead_code" not in text,
         "selected script disables a required check")
    log=read(all_logs/"native-registration.log").decode(errors="replace")
    trace=verify_trace(log,native.get("registration_run",{}).get("exit_status"))
    need(verify_stage(all_logs,native,"registration_run")=="PASS","native registration did not pass")
    rust_status=verify_stage(all_logs,native,"rust_suite_run")
    need(rust_status=="PASS","full native tests/rust/testsuite.mysh did not pass")
    make_status=verify_stage(all_logs,native,"make_test_run",(0,124,125,137))
    if make_status=="TIMEOUT":
        make_label="NOT_RUN_TIMEOUT"
    elif make_status=="NOT_RUN":
        note=read(all_logs/native["make_test_run"]["path"]).decode(errors="replace")
        need(note.startswith("NOT_RUN:"),"make test has no explicit NOT_RUN reason","INCOMPLETE_EVIDENCE")
        make_label="NOT_RUN_BUDGET"
    else: make_label="PASS"
    provenance=verify_provenance(tool,all_logs,native)
    case_records=native.get("case_evidence",{})
    need(set(case_records)==set(FIXTURES),"native per-fixture evidence set is incomplete","INCOMPLETE_EVIDENCE")
    whole_log=read(all_logs/"native-registration.log")
    for name,(expected,blob) in FIXTURES.items():
        case_dir=all_logs/"cases/manuallydrop-native"/name
        record=json_file(case_dir/"case.json")
        source=read(case_dir/"source.rs"); trace=read(case_dir/"native-mysh-trace.log")
        native_record=case_records[name]
        need(record==native_record and hashlib.sha256(source).hexdigest()==expected==native_record.get("source_sha256") and
             native_record.get("git_blob")==blob and hashlib.sha256(trace).hexdigest()==native_record.get("trace_sha256") and
             trace in whole_log,f"{name} preserved native case evidence does not match the full mysh trace",
             "INCOMPLETE_EVIDENCE")
        if name=="dead_code_pre":
            need(DEAD.search(trace.decode(errors="replace")) is not None,
                 "preserved dead_code_pre trace lacks the exact diagnostic")
    need(native.get("registration_sha256")==REGISTRATION_SHA256 and
         native.get("registration_git_blob")==REGISTRATION_BLOB,
         "registration source differs from the pinned native test block")
    need(read(all_logs/"cases/manuallydrop-native/selected-registration.mysh")==script and
         json_file(all_logs/"cases/manuallydrop-native/manifest.json")==native,
         "preserved native registration script/manifest differs from executed inputs","INCOMPLETE_EVIDENCE")
    return {"classification":"UPSTREAM_NATIVE_REGISTRATION_AND_RUST_SUITE_PASS","accepted":True,
            "provenance":provenance,"selected_registration":trace,
            "full_rust_testsuite":"PASS","make_test":make_label,
            "scope":"native selected registration and full tests/rust suite; broader make test status shown separately"}

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("candidate_tool",type=Path); p.add_argument("evidence",type=Path); p.add_argument("--output",type=Path)
    a=p.parse_args()
    try: result=audit(a.candidate_tool,a.evidence); code=0
    except AuditFailure as ex: result={"classification":"INCONCLUSIVE","accepted":False,"failure_kind":ex.kind,"reason":str(ex)}; code=2
    except (OSError,KeyError,TypeError,ValueError,subprocess.SubprocessError) as ex: result={"classification":"INCONCLUSIVE","accepted":False,"failure_kind":"INCOMPLETE_EVIDENCE","reason":str(ex)}; code=2
    payload=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(payload)
    print(payload,end=""); return code
if __name__=="__main__": raise SystemExit(main())
