#!/usr/bin/env python3
"""Independent R3 owner, A1 and SAFE-forget negatives in disposable Cloud copies."""
from __future__ import annotations

import argparse
import difflib
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
OWNER_MARK = "SORT4-ACTUAL-OWNER-NINE: exact source and complete decoded MIR admission only"
A1_MARK = "SORT4-A1-NINE: exact source, typed local pair and outer cleanup call admitted"
FORGET_MARK = "SORT4-ACTUAL-FORGET-OWN: exact nine-body SAFE call/owner callee admitted"
FATAL_OWNER_SOURCE = ('Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: '
                      'certificate mismatch: owner exact verified source SHA256")')
FATAL_OWNER_UNIT = ('Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: '
                    'certificate mismatch: owner complete decoded unit SHA256")')
FATAL_A1 = ('Fatal error: exception Failure("SORT4-A1-NINE: certificate mismatch: '
            'outer assume_init must move selected wrapper")')
FATAL_FORGET = ('Fatal error: exception Failure("SORT4-ACTUAL-FORGET-OWN: '
                'certificate mismatch: forget argument plain Move")')
VERIFIER_ERROR = re.compile(r"(?m)^.*: error: |^Fatal error:")
SOURCE_MUTATIONS = {
    "source_owner": (b"*g.inner |-> ?payload &*& <T>.own(t, payload);",
                     b"*g.inner |-> ?payload &*& <T>.own(t, payload) &*& true;"),
    "source_outcome": (b"fn_outcome_result(outcome)",
                       b"fn_outcome_result( outcome)"),
}
OWNER_MIR_MUTATIONS = ("forget_move_to_copy", "forget_cleanup_to_wrong_block")


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f"module absent: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def modules(a):
    profile = load("o26_r3_controls_profile", a.cloud_dir / "o26-r3-profile.py")
    cap = load("o26_r3_controls_capture", a.proof_root / ROOT /
               "overnight-assume-actual/capture.py")
    prep = load("o26_r3_controls_prepare", a.proof_root / ROOT /
                "overnight-assume-actual/prepare-wrapper-input-relation.py")
    mut = load("o26_r3_controls_shadow", a.proof_root / ROOT /
               "overnight-helper/capture-actual-owner-mir-mutation.py")
    r2 = load("o26_r3_controls_r2", a.cloud_dir / "o26-wrapper-profile.py")
    return profile, cap, prep, mut, r2


def mutate_actual_mir(decoded: str, mutation: str) -> str:
    proof = os.environ.get("R3_TEST_PROOF_ROOT")
    cloud = os.environ.get("R3_TEST_CLOUD_DIR")
    need(proof is not None and cloud is not None,
         "R3 shadow exporter roots absent")
    profile = load("o26_r3_controls_shadow_profile",
                   Path(cloud) / "o26-r3-profile.py")
    return profile.mutate_outer_mir(decoded, mutation,
                                    SimpleNamespace(proof_root=Path(proof)))


def fresh_case(a, prep, cap, profile, key: str):
    out = a.evidence / "controls" / key / "source"
    out.parent.mkdir(parents=True)
    source = prep.write_case(a.proof_root, out)
    case = out / prep.CASE_NAME
    need(source["verified_sha256"] == profile.R3_SOURCE ==
         sha(case / "verified/lib.rs") and
         source["original_sha256"] == profile.ORIGINAL ==
         sha(case / "original/lib.rs"),
         f"{key}: fresh R3 source pair changed")
    return source, case


def support(a, cap, profile, case: Path, source: dict,
            compare_positive: bool) -> dict:
    args = SimpleNamespace(tool_home=a.r3_source,
                           schema=a.r3_source /
                           "src/rust_frontend/vf_mir/vf_mir.capnp",
                           compiler_sysroot=str(a.compiler_sysroot),
                           deadline_epoch=a.deadline_epoch,
                           first_barrier=False, fingerprint_probe=False)
    cap.clear_semantic_opt_ins()
    result = cap.GUARD.capture_case(case, source, args)
    stages = result["stages"]
    need(result.get("frontend_refinement") is True and
         result.get("source_unchanged") is True and
         all(stages[k].get("exit") == 0 and
             stages[k].get("source_unchanged") is True
             for k in ("normal-export", "normal-decode", "readonly-export",
                       "readonly-decode", "refinement")),
         "R3 mutant export/decode/refinement failed")
    if compare_positive:
        positive = a.evidence / "capture" / profile.CASE
        need(all(sha(case / f"{mode}-mir.bin") ==
                 sha(positive / f"{mode}-mir.bin")
                 for mode in ("normal", "readonly")),
             "R3 unchanged-source mutant MIR differs from positive")
    return result


def shadow(a, mut, profile, case: Path, tool: Path,
           mutation: str) -> Path:
    selected = mut.make_shadow(tool,
             tool / "src/rust_frontend/vf_mir/vf_mir.capnp",
             case, mutation, profile.R3_SOURCE)
    wrapper = selected / "bin/vf-rust-mir-exporter"
    old = repr(str(mut.HERE / "capture-actual-owner-mir-mutation.py"))
    data = wrapper.read_text()
    need(data.count(old) == 1, "R3 shadow import anchor differs")
    data = data.replace(old, repr(str(Path(__file__).resolve())), 1)
    wrapper.write_text(data)
    wrapper.chmod(0o755)
    (case / "mir-exporter-wrapper.py").write_text(data)
    row = read(case / "mutation-profile.json")
    row.update({"wrapper_sha256": sha(wrapper), "mutation": mutation,
                "test_only": True})
    write(case / "mutation-profile.json", row)
    return selected


def proof(a, profile, case: Path, tool: Path, name: str):
    args = SimpleNamespace(proof_root=a.proof_root, cloud_dir=a.cloud_dir,
                           r3_source=a.r3_source,
                           compiler_sysroot=a.compiler_sysroot,
                           deadline_epoch=a.deadline_epoch,
                           schema=tool /
                           "src/rust_frontend/vf_mir/vf_mir.capnp")
    return profile.proof_stage(args, case, tool, name, True)


def mutation_identity(a, profile, case: Path, mutation: str,
                      tool: Path, positive: Path) -> dict:
    record = read(case / "mutation-record.json")
    metadata = read(case / "mutation-profile.json")
    canonical = case / "canonical-mir.txt"
    mutated = case / "mutated-mir.txt"
    need(record.get("matched") is True and
         record.get("mutation") == mutation and
         record.get("selected_source_sha256") == profile.R3_SOURCE and
         all(record.get(k) == 0 for k in
             ("exporter_exit", "decode_exit", "encode_exit")) and
         record.get("canonical_sha256") ==
         sha(case / "canonical-mir.bin") ==
         sha(positive / "normal-mir.bin") and
         record.get("mutated_sha256") == sha(case / "mutated-mir.bin") and
         profile.mutate_outer_mir(canonical.read_text(), mutation, a) ==
         mutated.read_text() and
         metadata.get("wrapper_sha256") ==
         sha(case / "mir-exporter-wrapper.py") ==
         sha(tool / "bin/vf-rust-mir-exporter") and
         metadata.get("base_console_sha256") ==
         metadata.get("shadow_console_sha256") and
         metadata.get("real_exporter_sha256") ==
         record.get("real_exporter_sha256"),
         f"R3 {mutation} did not change exactly one reviewed MIR field")
    return {"mutation": mutation,
            "canonical_mir_sha256": record["canonical_sha256"],
            "mutated_mir_sha256": record["mutated_sha256"],
            "wrapper_sha256": metadata["wrapper_sha256"],
            "real_exporter_sha256": record["real_exporter_sha256"]}


def fatal_lines(log: str) -> list[str]:
    return [line for line in log.splitlines()
            if line.startswith("Fatal error:")]


def owner_controls(a, profile, cap, prep, mut) -> list[dict]:
    rows = []
    positive = a.evidence / "capture" / profile.CASE
    for key in (*SOURCE_MUTATIONS, *OWNER_MIR_MUTATIONS):
        selected, case = fresh_case(a, prep, cap, profile, "owner17-" + key)
        if key in SOURCE_MUTATIONS:
            before, after = SOURCE_MUTATIONS[key]
            verified = case / "verified/lib.rs"
            data = verified.read_bytes()
            need(data.count(before) == 1 and data.count(after) == 0,
                 f"R3 {key} mutation anchor differs")
            verified.write_bytes(data.replace(before, after, 1))
            need(verified.read_bytes().replace(after, before, 1) == data and
                 prep.R2.BASE.SEVEN.OWNER.OWNER.strip_ghost(
                     verified.read_bytes()) ==
                 (case / "original/lib.rs").read_bytes(),
                 f"R3 {key} mutation changed runtime")
            selected["verified_sha256"] = sha(verified)
        support(a, cap, profile, case, selected,
                compare_positive=key not in SOURCE_MUTATIONS)
        tool = a.r3_source
        if key in OWNER_MIR_MUTATIONS:
            tool = shadow(a, mut, profile, case, tool, key)
        stage = proof(a, profile, case, tool, "r3-owner-" + key)
        write(case / "proof-stage.json", stage)
        log = (case / ("r3-owner-" + key + ".log")).read_text(errors="replace")
        intended = (stage.get("status") == "RAN" and stage.get("exit") == 2 and
                    stage.get("source_unchanged") is True and
                    stage.get("source_before") == stage.get("source_after") and
                    stage.get("intrinsic_gate_active") is True and
                    stage.get("pointer_drop_gate_active") is True and
                    fatal_lines(log) == [FATAL_OWNER_SOURCE if
                                         key in SOURCE_MUTATIONS else
                                         FATAL_OWNER_UNIT] and
                    "Verifying function '" not in log and
                    OWNER_MARK not in log and A1_MARK not in log and
                    FORGET_MARK not in log)
        identity = None
        if key in OWNER_MIR_MUTATIONS:
            identity = mutation_identity(a, profile, case, key, tool, positive)
        row = {"variant": key, "intended_component17_refusal": intended,
               "source_sha256": selected["verified_sha256"],
               "stage": stage, "mutation_identity": identity,
               "full_support_record": sha(case / "summary.json")
               if (case / "summary.json").is_file() else None,
               "accepted": False}
        write(case / "control-result.json", row)
        need(intended, f"R3 {key} refused at wrong obligation")
        rows.append(row)
    return rows


def mutated_snapshots(a, cap, profile, case: Path, source: dict,
                      shadow_tool: Path, mutation: str,
                      positive: Path) -> dict:
    args = SimpleNamespace(tool_home=shadow_tool,
                           schema=a.r3_source /
                           "src/rust_frontend/vf_mir/vf_mir.capnp",
                           compiler_sysroot=str(a.compiler_sysroot),
                           deadline_epoch=a.deadline_epoch,
                           first_barrier=False, fingerprint_probe=False)
    fp = cap.refusal_fingerprint(case, source, args)
    rows = fp.get("snapshots", {})
    need(fp.get("classification") ==
         "INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE" and
         fp.get("all_ten_snapshots") is True and
         set(rows) == {"unit", *(f"body-{i}" for i in range(9))},
         f"R3 {mutation} fingerprint incomplete")
    recorded = read(a.evidence / "profile-manifest.json")["source"]
    for label, row in rows.items():
        path = case / row["file"]
        expected = (recorded["unit_sha256"] if label == "unit" else
                    recorded["body_sha256"][int(label[5:])])
        need(path.stat().st_size == row["bytes"] and
             sha(path) == row["sha256"] and
             ((row["sha256"] != expected) if label in ("unit", "body-7")
              else (row["sha256"] == expected)),
             f"R3 {mutation} changed wrong Marshal body: {label}")
    mutation_identity(a, profile, case, mutation, shadow_tool, positive)
    return fp


def test_tool(a, profile, r2, case: Path, rows: dict, mutation: str) -> tuple[Path, dict]:
    control_root = case.parent.parent
    test = control_root / "test-tool"
    need(not test.exists(), f"R3 {mutation} TEST tool already exists")
    before = r2.tool_snapshot(a.r3_source, a.proof_root)
    shutil.copytree(a.r3_source, test, symlinks=True)
    source = (a.r3_source / TRANSLATOR).read_text()
    old = read(a.evidence / "profile-manifest.json")["source"]
    replacements = ((old["unit_sha256"], rows["unit"]["sha256"]),
                    (old["body_sha256"][7], rows["body-7"]["sha256"]))
    changed = source
    for old_hash, new_hash in replacements:
        need(changed.count(old_hash) == 1 and old_hash != new_hash and
             new_hash not in changed,
             f"R3 {mutation} owner-only hash delta not unique")
        changed = changed.replace(old_hash, new_hash, 1)
    restored = changed
    for old_hash, new_hash in replacements:
        restored = restored.replace(new_hash, old_hash, 1)
    need(restored == source, "R3 TEST hash delta not reversible")
    (test / TRANSLATOR).write_text(changed)
    patch = "".join(difflib.unified_diff(source.splitlines(keepends=True),
                     changed.splitlines(keepends=True),
                     fromfile="a/" + str(TRANSLATOR),
                     tofile="b/" + str(TRANSLATOR)))
    (control_root / "test-owner-hash-delta.patch").write_text(patch)
    need(patch.count("@@") == 4, "R3 TEST delta is not exactly two hunks")
    (test / "bin/verifast").unlink()
    deadline = int(a.deadline_epoch - time.time()) - 25
    need(deadline > 0, "R3 TEST console build deadline")
    with (control_root / "test-console-build.log").open("wb") as log:
        result = subprocess.run(("make", "-C", str(test / "src"),
                                 "../bin/verifast", "WITHOUT_LABLGTK=yes",
                                 "VERBOSE=yes"), stdout=log,
                                stderr=subprocess.STDOUT,
                                timeout=deadline, check=False)
    need(result.returncode == 0 and (test / "bin/verifast").is_file(),
         "R3 TEST console build failed")
    after = r2.tool_snapshot(test, a.proof_root)
    need(r2.tool_snapshot(a.r3_source, a.proof_root) == before and
         before["head"] == after["head"] and
         before["effective_rsspec_sha256"] ==
         after["effective_rsspec_sha256"] and
         before["proof_std_sha256"] == after["proof_std_sha256"] and
         all(before["critical_source_sha256"][k] ==
             after["critical_source_sha256"][k]
             for k in before["critical_source_sha256"]
             if k != str(TRANSLATOR)) and
         set(before["modified_tracked_source_sha256"]) ==
         set(after["modified_tracked_source_sha256"]) and
         all(before["modified_tracked_source_sha256"][k] ==
             after["modified_tracked_source_sha256"][k]
             for k in before["modified_tracked_source_sha256"]
             if k != str(TRANSLATOR)) and
         all(before["binary_sha256"][k] == after["binary_sha256"][k]
             for k in before["binary_sha256"] if k != "bin/verifast") and
         after["critical_source_sha256"][str(TRANSLATOR)] ==
         hashlib.sha256(changed.encode()).hexdigest() and
         after["modified_tracked_source_sha256"][str(TRANSLATOR)] ==
         hashlib.sha256(changed.encode()).hexdigest() and
         before["binary_sha256"]["bin/verifast"] !=
         after["binary_sha256"]["bin/verifast"],
         "R3 TEST changed kernel/spec/source/binaries beyond two owner pins")
    identity = {"classification": "R3_TEST_OWNER_HASH_DELTA_ONLY",
                "mutation": mutation, "production_snapshot": before,
                "test_snapshot": after,
                "patch_sha256": sha(control_root / "test-owner-hash-delta.patch"),
                "test_only": True, "accepted": False}
    write(control_root / "test-tool-identity.json", identity)
    return test, identity


def downstream_control(a, profile, cap, prep, mut, r2,
                       mutation: str, expected: str) -> dict:
    source, case = fresh_case(a, prep, cap, profile, mutation)
    positive = a.evidence / "capture" / profile.CASE
    support(a, cap, profile, case, source, compare_positive=True)
    prod_shadow = shadow(a, mut, profile, case, a.r3_source, mutation)
    owner = proof(a, profile, case, prod_shadow,
                  "r3-" + mutation + "-owner-refusal")
    owner_log = (case / ("r3-" + mutation + "-owner-refusal.log")).read_text(
        errors="replace")
    need(owner.get("status") == "RAN" and owner.get("exit") == 2 and
         owner.get("source_unchanged") is True and
         fatal_lines(owner_log) == [FATAL_OWNER_UNIT] and
         "Verifying function '" not in owner_log,
         f"R3 {mutation} did not first hit owner unit pin")
    fp = mutated_snapshots(a, cap, profile, case, source, prod_shadow,
                           mutation, positive)
    test, identity = test_tool(a, profile, r2, case, fp["snapshots"], mutation)
    test_case = case.parent.parent / "test-case"
    test_case.mkdir()
    for kind in ("verified", "original"):
        (test_case / kind).mkdir()
        shutil.copy2(case / kind / "lib.rs", test_case / kind / "lib.rs")
    test_shadow = shadow(a, mut, profile, test_case, test, mutation)
    stage = proof(a, profile, test_case, test_shadow,
                  "r3-" + mutation + "-target-refusal")
    log = (test_case / ("r3-" + mutation + "-target-refusal.log")).read_text(
        errors="replace")
    mutation_record = mutation_identity(a, profile, test_case, mutation,
                                        test_shadow, positive)
    intended = (stage.get("status") == "RAN" and stage.get("exit") == 2 and
                stage.get("source_unchanged") is True and
                stage.get("source_before") == stage.get("source_after") and
                stage.get("intrinsic_gate_active") is True and
                stage.get("pointer_drop_gate_active") is True and
                fatal_lines(log) == [expected] and
                OWNER_MARK in log and "Verifying function '" not in log and
                (A1_MARK not in log if mutation == "forget_move_to_copy"
                 else FORGET_MARK in log))
    result = {"classification": (
                  "R3_A1_MOVE_COPY_NEGATIVE" if mutation.startswith("outer_")
                  else "R3_SAFE_FORGET_MOVE_COPY_NEGATIVE")
              if intended else "INCONCLUSIVE",
              "intended_refusal": intended, "mutation": mutation,
              "stage": stage, "owner_first_refusal": owner,
              "mutation_identity": mutation_record,
              "test_tool_identity": identity,
              "verification_accepted": False, "accepted": False}
    write(case.parent.parent / "test-result.json", result)
    need(intended, f"R3 {mutation} refused at wrong A1/SAFE-forget gate")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("proof-root", "cloud-dir", "r3-source",
                 "compiler-sysroot", "evidence"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--deadline-epoch", type=int, required=True)
    a = p.parse_args()
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud Build required")
    need(read(a.evidence / "capture-check.json").get("classification") ==
         "R3_SOURCE_MIR_GRAPH_PINNED_DIAGNOSTIC", "R3 capture absent")
    profile, cap, prep, mut, r2 = modules(a)
    positive = read(a.evidence / "r3-positive-stage.json")
    log = (a.evidence / "capture" / profile.CASE /
           "r3-positive.log").read_text(errors="replace")
    need(positive.get("status") == "RAN" and
         positive.get("exit") not in (None, 124, 137) and
         positive.get("source_unchanged") is True and
         OWNER_MARK in log and A1_MARK in log and FORGET_MARK in log,
         "R3 production admission did not reach owner/A1/SAFE-forget gates")
    baseline = r2.tool_snapshot(a.r3_source, a.proof_root)
    os.environ["R3_TEST_PROOF_ROOT"] = str(a.proof_root)
    os.environ["R3_TEST_CLOUD_DIR"] = str(a.cloud_dir)
    try:
        owner = owner_controls(a, profile, cap, prep, mut)
        a1 = downstream_control(a, profile, cap, prep, mut, r2,
                                "outer_assume_init_move_to_copy", FATAL_A1)
        forget = downstream_control(a, profile, cap, prep, mut, r2,
                                    "forget_move_to_copy", FATAL_FORGET)
    finally:
        os.environ.pop("R3_TEST_PROOF_ROOT", None)
        os.environ.pop("R3_TEST_CLOUD_DIR", None)
    need(r2.tool_snapshot(a.r3_source, a.proof_root) == baseline,
         "R3 production tool changed during negatives")
    result = {"classification": "R3_CHANGED_COMPONENT_NEGATIVES_COMPLETE",
              "owner17": owner, "a1": a1, "safe_forget": forget,
              "production_tool_unchanged": True,
              "verification_accepted": False, "accepted": False}
    write(a.evidence / "controls-summary.json", result)


if __name__ == "__main__":
    main()
