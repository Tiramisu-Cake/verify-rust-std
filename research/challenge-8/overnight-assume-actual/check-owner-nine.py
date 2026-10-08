#!/usr/bin/env python3
"""Hosted whole-unit owner integration and precise independent admission controls."""
import argparse
import hashlib
import json
import os
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("nine_owner_capture", HERE / "capture.py")
CAP = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = CAP
_spec.loader.exec_module(CAP)
MUT = CAP.load(HERE.parent / "overnight-helper" /
               "capture-actual-owner-mir-mutation.py", "nine_owner_mir_controls")
SOURCE_SHA = "8629849c2d2ddde1eeb90fadb6a151dc52e626385578f89f0d86fce842c61eb8"
ADMISSION = "SORT4-ACTUAL-OWNER-NINE: exact source and complete decoded MIR admission only"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mutate_actual_mir(decoded, mutation):
    """Change one field at the actual forget, never the source or real export."""
    start, end, body = MUT.selected_body(decoded, "select_unpredictable")
    callee = 'name = "std::mem::forget"'
    CAP.PREP.require(body.count(callee) == 1, "unique actual forget missing")
    at = body.index(callee)
    call_at = body.rfind("call = (", 0, at) + len("call = ")
    call = MUT.PREP.LINK.CONSTRUCTOR.mir_balanced_item(body, call_at)
    CAP.PREP.require(callee in call, "actual forget call record missing")
    if mutation == "forget_move_to_copy":
        lo = call.index("args = [")
        hi = call.index("destination = (", lo)
        args = call[lo:hi]
        CAP.PREP.require(args.count("move = (") == 1 and
                         'local = (name = "_34")' in args and
                         "projection = []" in args, "actual Move(_34) missing")
        args = args.replace("move = (", "copy = (", 1)
        changed = call[:lo] + args + call[hi:]
    elif mutation == "forget_cleanup_to_bb23":
        changed = MUT.replace_once(call,
            "unwindAction = (cleanup = (index = 24))",
            "unwindAction = (cleanup = (index = 23))", mutation)
    else:
        raise ValueError("unknown nine-owner MIR mutation")
    body = body[:call_at] + changed + body[call_at + len(call):]
    return decoded[:start] + body + decoded[end:]


def proof(case, args, tool):
    options = SimpleNamespace(**vars(args))
    options.tool_home = tool
    return CAP.LINK.stage(case, "full-verification", [str(tool / "bin/verifast"),
        "-rustc_args", "--edition 2021", "-verbose", "1", "verified/lib.rs"],
        options, gates=True, pointer_drop=True, cap_seconds=100)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tool-home", type=Path, required=True)
    p.add_argument("--schema", type=Path, required=True)
    p.add_argument("--compiler-sysroot", required=True)
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--deadline-epoch", type=int, required=True)
    args = p.parse_args()
    CAP.PREP.require((os.getenv("GITHUB_ACTIONS"), os.getenv("RUNNER_ENVIRONMENT"),
        os.getenv("RUNNER_OS")) == ("true", "github-hosted", "Linux"), "hosted only")
    CAP.PREP.require(not args.evidence.exists(), "refusing evidence overwrite")
    args.first_barrier = False
    args.fingerprint_probe = False
    rows = []
    for variant in ("positive", "source_owner", "source_outcome",
                    "forget_move_to_copy", "forget_cleanup_to_bb23"):
        CAP.clear_semantic_opt_ins()
        os.environ.pop("SORT4_ACTUAL_OWNER_NINE_ADMISSION", None)
        source = CAP.PREP.write_case(CAP.REPO, args.evidence / variant)
        case = args.evidence / variant / CAP.PREP.CASE_NAME
        verified = case / "verified/lib.rs"
        CAP.PREP.require(sha(verified) == SOURCE_SHA, "fresh source differs from O24")
        if variant.startswith("source_"):
            before, after = ({
                "source_owner": (b"*g.inner |-> ?payload &*& <T>.own(t, payload);",
                    b"*g.inner |-> ?payload &*& <T>.own(t, payload) &*& true;"),
                "source_outcome": (b"fn_outcome_result(outcome)",
                    b"fn_outcome_result( outcome)"),
            })[variant]
            data = verified.read_bytes()
            CAP.PREP.require(data.count(before) == 1, "source mutation anchor")
            data = data.replace(before, after, 1)
            CAP.PREP.require(CAP.PREP.SEVEN.OWNER.OWNER.strip_ghost(data) ==
                (case / "original/lib.rs").read_bytes(), "runtime source changed")
            verified.write_bytes(data)
            source["verified_sha256"] = sha(verified)
        captures = CAP.GUARD.capture_case(case, source, args)
        complete = captures["frontend_refinement"] and captures["source_unchanged"]
        os.environ["SORT4_ACTUAL_OWNER_REPO_ROOT"] = str(CAP.REPO)
        os.environ["SORT4_ACTUAL_OWNER_ADMISSION"] = "1"
        os.environ["SORT4_ACTUAL_OWNER_NINE_ADMISSION"] = "1"
        tool = args.tool_home
        mutation = None
        if not variant.startswith("source_") and variant != "positive":
            tool = MUT.make_shadow(args.tool_home, args.schema, case, variant, SOURCE_SHA)
            wrapper = tool / "bin/vf-rust-mir-exporter"
            data = wrapper.read_text().replace(
                repr(str(MUT.HERE / "capture-actual-owner-mir-mutation.py")),
                repr(str(HERE / "check-owner-nine.py")))
            wrapper.write_text(data)
            (case / "mir-exporter-wrapper.py").write_text(data)
            profile = json.loads((case / "mutation-profile.json").read_text())
            profile["wrapper_sha256"] = sha(wrapper)
            (case / "mutation-profile.json").write_text(json.dumps(profile, indent=2)+"\n")
        stage = proof(case, args, tool) if complete else {}
        log = (case / "full-verification.log").read_text(errors="replace") if stage else ""
        errors = CAP.LINK.LINK.ERR.findall(log)
        fatal = [x for x in log.splitlines() if x.startswith("Fatal error:")]
        admitted = ADMISSION in log
        intact = stage.get("source_unchanged") is True
        intended = False
        reason = None
        if variant.startswith("source_"):
            reason = "owner exact verified source SHA256"
        elif variant != "positive":
            reason = "owner complete decoded unit SHA256"
            record = case / "mutation-record.json"
            if record.exists():
                mutation = json.loads(record.read_text())
                canonical = case / "canonical-mir.txt"
                changed = case / "mutated-mir.txt"
                exact = (mutation.get("matched") is True and
                    mutation.get("canonical_sha256") == sha(case / "normal-mir.bin") and
                    mutate_actual_mir(canonical.read_text(), variant) == changed.read_text())
            else:
                exact = False
        if reason:
            expected = 'Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: certificate mismatch: ' + reason + '")'
            intended = (complete and intact and not admitted and
                stage.get("exit") == 2 and fatal == [expected] and not errors and
                (variant.startswith("source_") or exact))
        row = {"variant": variant, "frontend_refinement": complete,
            "source_integrity": intact, "admission_passed": admitted,
            "classification": ("EXACT_ADMISSION_NEGATIVE" if intended else
                "WHOLE_UNIT_PROOF_DIAGNOSTIC" if variant == "positive" and admitted else
                "INCONCLUSIVE"), "proof_exit": stage.get("exit"),
            "whole_unit_proved": variant == "positive" and stage.get("exit") == 0,
            "actual_body_started": "Verifying function 'select_unpredictable'" in log,
            "first_error": errors[0] if errors else None, "fatal": fatal,
            "mutation_record": mutation, "expected_reason": reason}
        (case / "owner-proof-summary.json").write_text(json.dumps(row,indent=2)+"\n")
        rows.append(row)
        print(json.dumps(row), flush=True)
    (args.evidence / "summary.json").write_text(json.dumps({"cases":rows,
        "profile_status":"EXPERIMENTAL", "actual_generic_helper_proved":False},indent=2)+"\n")
    if any(r["classification"] == "INCONCLUSIVE" for r in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
