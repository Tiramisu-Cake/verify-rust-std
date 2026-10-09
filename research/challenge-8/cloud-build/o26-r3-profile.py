#!/usr/bin/env python3
"""Cloud-only R3 source/graph admission and proof staging; never acceptance."""
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


ROOT = Path("research/challenge-8")
PROFILE = ROOT / "overnight-assume-actual/O26-WRAPPER-INPUT-RELATION-PROFILE.json"
TRANSLATOR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
PATCH = "overnight-assume-actual/verifast-o26-wrapper-input-relation-profile-26.10.patch"
PAIR = ("SORT4_WRAPPER_INPUT_RELATION_REPO_ROOT",
        "SORT4_WRAPPER_INPUT_RELATION_ADMISSION")
CASE = "nine-body-wrapper-input-relation"
R3_SOURCE = "a95aff14592b167c62c53c7ed726128ee86c7c19768cfe613504cdec841f8463"
R3_UNIT = "407acbaea262ba908ed88434231e9fce1128678840f5d929deaad71838290a92"
R3_BODY7 = "f8374652a11e36073ad6ed10ec39b0f8de62da53265dd80d2dc2c3565491cee1"
MIR_SHA = {
    "normal": "5b241f4f51d9ba7e72dd4d24cf295a95a8f64d7750867821dc70dac982609509",
    "readonly": "c5fe3880640143c2805697f8fb4c46f380fc62eb01f3344ee1ec606e7aadf121",
}
ORIGINAL = "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5"
NAMES = (
    "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new",
    "sort4_checked_as_mut_ptr", "sort4_checked_pointer_drop",
    "sort4_checked_generic_drop", "checked_transmute_neo_pointer",
    "checked_assume_init_pointer", "checked_forget_owned",
    "select_unpredictable",
    "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop",
)
GHOST_CALLS = (
    (0, "_4", 1, None), (1, "_5", 2, None),
    (6, "_14", 7, None), (7, "_15", 8, None),
    (12, "_20", 13, None), (13, "_21", 14, None),
    *((index, f"_{index + 18}", index + 1, 43) for index in range(25, 33)),
    *((index, f"_{index + 18}", index + 1, 43) for index in range(33, 38)),
)
SITE = {
    "forget": {"block": 20, "guard_source_local": "_30",
               "move_argument_local": "_38", "destination_local": "_37",
               "normal_block": 21, "cleanup_block": 43,
               "negative_cleanup_block": 42},
    "assume_init": {"block": 39, "move_argument_local": "_56",
                    "destination_local": "_0", "normal_block": 40,
                    "cleanup_block": 43},
}
CALLEE = {"forget": "std::mem::forget",
          "assume_init": "std::mem::MaybeUninit::<T>::assume_init"}
FATAL_R2_SOURCE = ('Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: '
                   'certificate mismatch: owner exact verified source SHA256")')


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
    need(spec is not None and spec.loader is not None, f"module unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def r2_module(a):
    return load("o26_r3_r2_profile", a.cloud_dir / "o26-wrapper-profile.py")


def manifest(a) -> dict:
    m = read(a.proof_root / PROFILE)
    s = m.get("source", {})
    need(m.get("classification") ==
         "EXPERIMENTAL_O26_WRAPPER_INPUT_RELATION_COMPONENT24_NOT_ACCEPTED" and
         m.get("component24_patch") == PATCH and
         m.get("verification_accepted") is False and
         m.get("kernel_modified") is False and
         m.get("opt_in") == {
             "SORT4_WRAPPER_REBASE_REPO_ROOT": "exact proof root",
             "SORT4_WRAPPER_REBASE_ADMISSION": "1",
             PAIR[0]: "exact proof root", PAIR[1]: "1"},
         "R3 manifest/profile identity differs")
    need(s.get("verified_sha256") == R3_SOURCE and
         s.get("original_sha256") == ORIGINAL and
         s.get("unit_sha256") == R3_UNIT and
         isinstance(s.get("body_sha256"), list) and
         len(s["body_sha256"]) == 9 and
         s["body_sha256"][7] == R3_BODY7,
         "R3 fresh source/unit/nine-body pins differ")
    observed = m.get("observed_capture", {})
    need(m.get("observed_cloud_build_id") ==
         "93da48d0-d720-4179-8d2c-d8b7495703bf" and
         m.get("observed_cloud_archive_sha256") ==
         "e5c4a3a4feecf49ae6ae02ec65ef0a595ca7db815954847afe5a3b423291ec7a" and
         observed.get("classification") == "SOURCE_MIR_CAPTURE_ONLY" and
         observed.get("normal_whole_decoded_mir_sha256") == MIR_SHA["normal"] and
         observed.get("readonly_whole_decoded_mir_sha256") == MIR_SHA["readonly"] and
         observed.get("decoded_body_count") == 9 and
         observed.get("fingerprint_snapshot_count") == 10 and
         observed.get("actual_proof_run") is False,
         "R3 manifest observed capture differs from reviewed archive")
    r2 = r2_module(a).profile(a.proof_root)
    need(all(s["body_sha256"][i] == r2["source"]["body_sha256"][i]
             for i in range(9) if i != 7) and
         s["verified_sha256"] != r2["source"]["verified_sha256"] and
         s["unit_sha256"] != r2["source"]["unit_sha256"],
         "R3 changed a non-outer body or reused R2 source/unit")
    for value in (m.get("component24_patch_sha256"),
                  m.get("new_translator_sha256")):
        need(isinstance(value, str) and
             re.fullmatch(r"[0-9a-f]{64}", value) is not None,
             "R3 patch/translator SHA not observed")
    need(sha(a.proof_root / ROOT / PATCH) == m["component24_patch_sha256"],
         "R3 patch bytes changed")
    return m


def tool_identity(a, m: dict) -> dict:
    r2 = r2_module(a)
    before = r2.tool_snapshot(a.r2_source, a.proof_root)
    after = r2.tool_snapshot(a.r3_source, a.proof_root)
    recorded = read(a.evidence / "r2-tool-before.json")
    need(before == recorded and before["head"] == after["head"] ==
         "f76012fb518703b1d98e243ac4f487f16877cfcb",
         "R2 tool changed or R3 base head differs")
    need(before["effective_rsspec_sha256"] ==
         after["effective_rsspec_sha256"] and
         before["proof_std_sha256"] == after["proof_std_sha256"],
         "R3 changed effective specs or proof std")
    for key in ("critical_source_sha256", "modified_tracked_source_sha256"):
        need(set(before[key]) == set(after[key]) and
             all(before[key][name] == after[key][name]
                 for name in before[key] if name != str(TRANSLATOR)),
             f"R3 changed tracked source outside translator: {key}")
    need(all(before["binary_sha256"][name] == after["binary_sha256"][name]
             for name in before["binary_sha256"] if name != "bin/verifast") and
         before["binary_sha256"]["bin/verifast"] !=
         after["binary_sha256"]["bin/verifast"] and
         before["critical_source_sha256"][str(TRANSLATOR)] ==
         r2.profile(a.proof_root)["new_translator_sha256"] and
         after["critical_source_sha256"][str(TRANSLATOR)] ==
         m["new_translator_sha256"],
         "R3 console/translator or stock binaries differ")
    patch_text = (a.proof_root / ROOT / PATCH).read_text()
    need([line for line in patch_text.splitlines()
          if line.startswith(("--- ", "+++ "))] ==
         ["--- a/" + str(TRANSLATOR), "+++ b/" + str(TRANSLATOR)],
         "R3 patch scope differs from translator only")
    return {"r2": before, "r3": after,
            "only_translator_and_console_changed": True,
            "kernel_parser_schema_specs_exporter_refiner_unchanged": True,
            "accepted": False}


def outer_parts(decoded: str, a):
    mut = load("o26_r3_mir_selector", a.proof_root / ROOT /
               "overnight-helper/capture-actual-owner-mir-mutation.py")
    start, end, body = mut.selected_body(decoded, "select_unpredictable")
    local_at = body.index("localDecls = [")
    block_at = body.index("basicBlocks = [", local_at)
    block_end = body.index("\n      span = (", block_at)
    locals_text = body[local_at:block_at]
    blocks = body[block_at:block_end]
    names = set(re.findall(r'name = "(_\d+)"', locals_text))
    ids = [int(n) for n in re.findall(r'\( id = \(index = (\d+)\),', blocks)]
    need(names == {f"_{n}" for n in range(61)} and ids == list(range(44)),
         "R3 outer local/block inventory differs")
    return mut, start, end, body, block_at, block_end, blocks


def block_at(blocks: str, index: int, mut) -> str:
    marker = f"( id = (index = {index}),"
    need(blocks.count(marker) == 1, f"R3 block {index} not unique")
    at = blocks.index(marker)
    return mut.PREP.LINK.CONSTRUCTOR.mir_balanced_item(blocks,
                                                        blocks.index("(", at))


def call_at(decoded: str, a, kind: str):
    mut, start, end, body, lo, hi, blocks = outer_parts(decoded, a)
    site = SITE[kind]
    block = block_at(blocks, site["block"], mut)
    need(block.count(f'name = "{CALLEE[kind]}"') == 1,
         f"R3 {kind} callee differs")
    callee_at = block.index(f'name = "{CALLEE[kind]}"')
    open_at = block.rfind("call = (", 0, callee_at)
    need(open_at >= 0, f"R3 {kind} call absent")
    open_at += len("call = ")
    call = mut.PREP.LINK.CONSTRUCTOR.mir_balanced_item(block, open_at)
    arg_lo = call.index("args = [")
    arg_hi = call.index("destination = (", arg_lo)
    args = call[arg_lo:arg_hi]
    need(args.count("move = (") == 1 and args.count("copy = (") == 0 and
         args.count(f'local = (name = "{site["move_argument_local"]}")') == 1 and
         f'local = (name = "{site["destination_local"]}")' in call[arg_hi:] and
         f'target = (something = (index = {site["normal_block"]}))' in call and
         f'unwindAction = (cleanup = (index = {site["cleanup_block"]}))' in call,
         f"R3 {kind} Move/destination/normal/unwind differs")
    return mut, start, end, body, lo, hi, blocks, block, open_at, call, arg_lo, arg_hi


def outer_graph(decoded: str, a, m: dict) -> dict:
    mut, _, _, body, _, _, blocks = outer_parts(decoded, a)
    need(len(GHOST_CALLS) == 19,
         "R3 exact nineteen added/rebase ghost-call sites differ")
    for index, dest, normal, cleanup in GHOST_CALLS:
        block = block_at(blocks, index, mut)
        need(block.count('name = "VeriFast_ghost_command"') == 1 and
             "args = []" in block and
             f'local = (name = "{dest}")' in block and
             f'target = (something = (index = {normal}))' in block and
             (f'unwindAction = (cleanup = (index = {cleanup}))' in block
              if cleanup is not None else
              "unwindAction = (continue = void)" in block),
             f"R3 ghost call {index} differs")
    for kind in SITE:
        call_at(decoded, a, kind)
    need('local = (name = "_34")' in block_at(blocks, 17, mut) and
         'name = "std::ptr::mut_ptr::<impl *mut T>::drop_in_place"' in
         block_at(blocks, 17, mut) and
         'local = (name = "_30")' in block_at(blocks, 42, mut),
         "R3 pointer-drop or cleanup guard differs")
    resume, drop, switch = (block_at(blocks, n, mut) for n in (41, 42, 43))
    need("unwindResume = void" in resume and
         'local = (name = "_30")' in drop and
         "target = (index = 41)" in drop and
         'local = (name = "_60")' in switch and
         "targets = [(index = 41), (index = 42)]" in switch,
         "R3 unwind resume/drop/switch chain differs")
    need(blocks.count("unwindAction = (cleanup = (index = 43))") == 23,
         "R3 shared cleanup predecessor count differs")
    graph = {"local_count": 61, "block_count": 44,
             "ghost_calls": [{"block": b, "destination_local": d,
                              "normal_block": n,
                              **({"cleanup_block": c} if c is not None
                                 else {"unwind": "Continue"})}
                             for b, d, n, c in GHOST_CALLS],
             "forget": SITE["forget"], "assume_init": SITE["assume_init"],
             "pointer_drop_receiver_local": "_34",
             "pointer_drop": {"block": 17, "source_local": "_26",
                              "move_argument_local": "_34",
                              "destination_local": "_33",
                              "normal_block": 18, "cleanup_block": 43},
             "unwind_chain": {"resume_block": 41, "drop_block": 42,
                              "switch_block": 43, "switch_local": "_60",
                              "switch_targets": [41, 42]},
             "shared_cleanup_predecessor_count": 23}
    declared = m.get("typed_outer_mir", {})
    need(all(declared.get(k) == value for k, value in graph.items()),
         "R3 typed graph manifest differs from exact decoded graph")
    return graph


def mutate_outer_mir(decoded: str, mutation: str, a) -> str:
    kind = ("assume_init" if mutation == "outer_assume_init_move_to_copy"
            else "forget")
    need(mutation in ("outer_assume_init_move_to_copy",
                      "forget_move_to_copy", "forget_cleanup_to_wrong_block"),
         "unknown R3 MIR mutation")
    (mut, start, end, body, lo, hi, blocks, block, call_at_index,
     call, arg_lo, arg_hi) = call_at(decoded, a, kind)
    if mutation.endswith("move_to_copy"):
        prior = call[arg_lo:arg_hi]
        changed = prior.replace("move = (", "copy = (", 1)
        need(changed != prior and
             changed.replace("copy = (", "move = (", 1) == prior,
             "R3 Move/Copy mutation not reversible")
        new_call = call[:arg_lo] + changed + call[arg_hi:]
    else:
        before = f'unwindAction = (cleanup = (index = {SITE["forget"]["cleanup_block"]}))'
        after = f'unwindAction = (cleanup = (index = {SITE["forget"]["negative_cleanup_block"]}))'
        need(call.count(before) == 1, "R3 forget cleanup edge not unique")
        new_call = call.replace(before, after, 1)
        need(new_call.replace(after, before, 1) == call,
             "R3 cleanup mutation not reversible")
    new_block = block[:call_at_index] + new_call + block[call_at_index + len(call):]
    marker = f'( id = (index = {SITE[kind]["block"]}),'
    at = blocks.index(marker)
    new_blocks = blocks[:at] + new_block + blocks[at + len(block):]
    new_body = body[:lo] + new_blocks + body[hi:]
    result = decoded[:start] + new_body + decoded[end:]
    need(result != decoded, "R3 MIR mutation had no effect")
    return result


def capture_check(a, m: dict) -> dict:
    summary = read(a.evidence / "capture/summary.json")
    case = a.evidence / "capture" / CASE
    source = summary.get("source", {})
    need(summary.get("classification") ==
         "NINE_BODY_SOURCE_MIR_CALIBRATION_ONLY" and
         summary.get("source_mode") == "wrapper-input-relation-source-only" and
         summary.get("frontend_refinement_and_full_body_capture") is True and
         source.get("verified_sha256") == R3_SOURCE ==
         sha(case / "verified/lib.rs") and
         source.get("original_sha256") == ORIGINAL ==
         sha(case / "original/lib.rs") and
         source.get("ghost_strip_identity") is True and
         source.get("actual_runtime_unchanged") is True and
         source.get("verified_source_reversible_three_input_relation_insertions") is True and
         len(source.get("inserted_ghost_comments", [])) == 9,
         "R3 source pair or nine-ghost source certificate differs")
    guard = summary.get("guard_capture", {})
    stages = guard.get("stages", {})
    need(guard.get("frontend_refinement") is True and
         guard.get("source_unchanged") is True and
         all(stages.get(key, {}).get("exit") == 0 and
             stages[key].get("source_unchanged") is True
             for key in ("normal-export", "normal-decode", "readonly-export",
                         "readonly-decode", "refinement")),
         "R3 NORMAL/readonly/refinement support incomplete")
    body_records = summary.get("full_body_capture", {})
    for mode in MIR_SHA:
        data = case / f"{mode}-mir.txt"
        row = body_records.get(mode, {})
        need(sha(data) == MIR_SHA[mode] == row.get("whole_decoded_mir_sha256") and
             row.get("classification") == "COMPLETE_NINE_BODY_CAPTURE_ONLY" and
             row.get("exact_body_count_and_order") is True and
             len(row.get("bodies", [])) == 9,
             f"R3 complete {mode} decoded MIR differs")
        for i, item in enumerate(row["bodies"]):
            path = case / item["file"]
            need(item.get("index") == i and item.get("defpath") == NAMES[i] and
                 item.get("file") == f"{mode}-body-{i}-full-mir.txt" and
                 path.stat().st_size == item.get("bytes") and
                 sha(path) == item.get("sha256"),
                 f"R3 {mode} body {i} file/inventory differs")
        need(row["bodies"][7]["sha256"] ==
             m["observed_capture"][f"{mode}_outer_body7_sha256"],
             f"R3 observed {mode} outer body-7 bytes differ")
    fp = summary.get("fingerprint", {})
    rows = fp.get("snapshots", {})
    expected = {"unit": R3_UNIT,
                **{f"body-{i}": value
                   for i, value in enumerate(m["source"]["body_sha256"])}}
    need(fp.get("classification") ==
         "INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE" and
         fp.get("all_ten_snapshots") is True and
         set(rows) == set(expected), "R3 fingerprint snapshot inventory differs")
    for label, expected_sha in expected.items():
        row = rows[label]
        path = case / row["file"]
        need(row.get("file") == f"actual-nested-9-{label}.marshal" and
             row.get("bytes", 0) > 0 and
             path.stat().st_size == row["bytes"] and
             sha(path) == row.get("sha256") == expected_sha,
             f"R3 {label} Marshal bytes differ")
    graph = outer_graph((case / "normal-mir.txt").read_text(), a, m)
    result = {"classification": "R3_SOURCE_MIR_GRAPH_PINNED_DIAGNOSTIC",
              "source_sha256": R3_SOURCE, "original_sha256": ORIGINAL,
              "unit_sha256": R3_UNIT, "normal_readonly_refinement_complete": True,
              "all_nine_body_records_and_ten_marshal_files_hashed": True,
              "typed_outer_mir_exact": True, "typed_graph": graph,
              "accepted": False, "verification_accepted": False}
    write(a.evidence / "capture-check.json", result)
    return result


def proof_stage(a, case: Path, tool: Path, name: str, admitted: bool) -> dict:
    r2 = r2_module(a)
    need(not any(os.environ.get(key) for key in (*r2.PAIR, *PAIR)),
         "inherited R2/R3 opt-in forbidden")
    if admitted:
        os.environ[PAIR[0]] = str(a.proof_root)
        os.environ[PAIR[1]] = "1"
    try:
        return r2.proof_stage(a, case, tool, name, "r3_" + name, True)
    finally:
        for key in PAIR:
            os.environ.pop(key, None)


def proofs(a, m: dict) -> dict:
    need(read(a.evidence / "capture-check.json").get("classification") ==
         "R3_SOURCE_MIR_GRAPH_PINNED_DIAGNOSTIC", "R3 capture absent")
    case = a.evidence / "capture" / CASE
    off = proof_stage(a, case, a.r3_source, "r2-old-certificate-refusal", False)
    write(a.evidence / "r2-old-certificate-stage.json", off)
    off_log = (case / "r2-old-certificate-refusal.log").read_text(errors="replace")
    fatals = [line for line in off_log.splitlines()
              if line.startswith("Fatal error:")]
    need(off.get("status") == "RAN" and off.get("exit") == 2 and
         off.get("source_unchanged") is True and
         fatals == [FATAL_R2_SOURCE] and
         "Verifying function '" not in off_log,
         "old R2 certificate did not reject R3 source at exact source pin")
    positive = proof_stage(a, case, a.r3_source, "r3-positive", True)
    write(a.evidence / "r3-positive-stage.json", positive)
    log = (case / "r3-positive.log").read_text(errors="replace")
    prefix = [log.find("Verifying function '" + name + "'") for name in NAMES[:7]]
    outer = log.find("Verifying function 'select_unpredictable'")
    nested = log.find("Verifying function '" + NAMES[8] + "'")
    result = {"classification": "R3_POSITIVE_DIAGNOSTIC_REVIEW_REQUIRED",
              "stage": positive, "seven_prefix_headers_in_order":
              all(p >= 0 for p in prefix) and prefix == sorted(prefix),
              "outer_header_after_prefix": outer > max(prefix),
              "nested_header_before_outer": nested >= 0 and nested < outer,
              "full_proof_exit": positive.get("exit"),
              "full_proof_exit_zero": positive.get("exit") == 0,
              "actual_nested_drop_verified_before_outer": False,
              "accepted": False, "verification_accepted": False}
    write(a.evidence / "proof-summary.json", result)
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("preflight", "r2-snapshot", "tool-identity",
                                    "capture-check", "proofs", "final-identity"))
    for name in ("proof-root", "cloud-dir", "production-source",
                 "production-patch", "stock-home", "r2-source", "r3-source",
                 "compiler-sysroot", "evidence"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--deadline-epoch", type=int, required=True)
    a = p.parse_args()
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         not os.environ.get("GITHUB_ACTIONS"), "identified Cloud Build required")
    a.schema = a.r3_source / "src/rust_frontend/vf_mir/vf_mir.capnp"
    m = manifest(a)
    if a.mode == "preflight":
        write(a.evidence / "profile-manifest.json", m)
    elif a.mode == "r2-snapshot":
        write(a.evidence / "r2-tool-before.json",
              r2_module(a).tool_snapshot(a.r2_source, a.proof_root))
    elif a.mode == "tool-identity":
        write(a.evidence / "tool-identity.json", tool_identity(a, m))
    elif a.mode == "final-identity":
        current = tool_identity(a, m)
        need(current == read(a.evidence / "tool-identity.json"),
             "R2/R3 tool changed during proof or controls")
        write(a.evidence / "tool-identity-after.json", current)
    elif a.mode == "capture-check":
        capture_check(a, m)
    else:
        proofs(a, m)


if __name__ == "__main__":
    main()
