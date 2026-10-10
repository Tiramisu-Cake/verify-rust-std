#!/usr/bin/env python3
"""Cloud-only C1+C2 bound-prefix gate after the fresh C2 discovery prerequisite.

Call ``run_bound`` from the existing c1-current-recovery Cloud runner only
after its own positive C1 gate and mandatory-refused C2 discovery pass. This
module is inert on import; it never dispatches a Build.
"""
from __future__ import annotations

import hashlib
import bisect
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any


HERE = Path("research/challenge-8/cloud-build/sort4-c2-bound-prefix")
TRANSLATOR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
KERNEL = Path("src/verifast.ml")
CONTROLS = (
    "c2-normal-missing-close", "c2-unwind-missing-close",
    "c2-normal-omit-join", "c2-unwind-omit-join", "normal-false-post",
    "c1-unwind-false-assert", "c2-unwind-false-assert",
)
FUTURE_NORMAL = {
    **{n: 241 for n in range(98, 104)},
    **{n: 242 for n in range(105, 111)},
    **{n: 249 for n in range(134, 140)},
}
FUTURE_READONLY = {
    **{n: 254 for n in range(98, 102)},
    **{n: 255 for n in range(102, 106)},
    **{n: 256 for n in range(106, 110)},
}


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError(reason)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def stage(a, name: str, command: list[str], cwd: Path, env: dict[str, str],
          cap: int = 180) -> tuple[int, str]:
    seconds = min(cap, a.deadline_epoch - int(time.time()) - 30)
    need(seconds > 0, f"deadline before C2 bound stage {name}")
    output = a.evidence / f"c2-bound-{name}.log"
    resources = a.evidence / f"c2-bound-{name}-resources.txt"
    with output.open("wb") as log:
        code = subprocess.run(
            ["/usr/bin/time", "-v", "-o", str(resources),
             "timeout", "--signal=TERM", "--kill-after=10s",
             f"{seconds}s", *command],
            cwd=cwd, env={**env, "PWD": str(cwd)}, stdin=subprocess.DEVNULL,
            stdout=log, stderr=subprocess.STDOUT, check=False).returncode
    raw = output.read_text(errors="replace")
    record(a.evidence / f"c2-bound-{name}-stage.json", {
        "argv": command, "cwd": str(cwd), "exit": code,
        "timeout_seconds": seconds, "log_sha256": sha(output),
        "resources": str(resources.relative_to(a.evidence)),
        "proof_credit": False})
    return code, raw


def target_entries(log: str, name: str) -> list[int]:
    pattern = re.compile(r"(?m)^\s*\d+(?:\.\d+)?s: .*: Verifying function '" +
                         re.escape(name) + r"'")
    return [m.start() for m in pattern.finditer(log)]


def audit_future_storage(full_mir: Path, expected: dict[int, int],
                         mode: str, absent: tuple[int, ...] = ()) -> dict[str, Any]:
    """Inspect pinned saved MIR text; never invoke a compiler or extractor."""
    body_text = full_mir.read_text()
    need(body_text.count("basicBlocks = [") == 1,
         f"{mode}: complete MIR block container changed")
    body = body_text.split("basicBlocks = [", 1)[1]
    block_pattern = re.compile(r"(?m)^        \( id = \(index = (\d+)\),")
    blocks = list(block_pattern.finditer(body))
    normal = mode.startswith("normal")
    expected_blocks = 82 if normal else 28
    expected_calls = [23, 53, 62, 63, 70] if normal else [1, 4, 9, 10, 17]
    need([int(m.group(1)) for m in blocks] == list(range(expected_blocks)),
         f"{mode}: complete MIR basic-block inventory changed")
    block_starts = [m.start() for m in blocks]
    block_texts = [body[blocks[i].start():
                        blocks[i + 1].start() if i + 1 < len(blocks) else len(body)]
                   for i in range(len(blocks))]
    successors = [list(map(int, re.findall(
        r"target = \(something = \(index = (\d+)\)\)", block)))
                  for block in block_texts]
    need(all(edges == ([n + 1] if n + 1 < expected_blocks else [])
             for n, edges in enumerate(successors)) and
         all("isCleanup = false" in block for block in block_texts) and
         sum(block.count("unwindAction = (continue = void)")
             for block in block_texts) == expected_blocks - 1,
         f"{mode}: exact linear noncleanup/Continue edge graph changed")
    calls = [n for n, block in enumerate(block_texts)
             if "std::ops::FnMut::call_mut" in block]
    need(calls == expected_calls,
         f"{mode}: exact five comparator call blocks changed")
    first_lives: dict[str, dict[str, int]] = {}
    for n, line in expected.items():
        name = f"_{n}"
        occurrence = re.search(
            rf'(?:local|storageLive|storageDead) = \(name = "{name}"\)', body)
        need(occurrence is not None and
             occurrence.group(0) == f'storageLive = (name = "{name}")' and
             bisect.bisect_right(block_starts, occurrence.start()) - 1 > calls[1],
             f"{mode}: {name} used or live before the C2 boundary")
        preceding = re.findall(r"line = (\d+)",
                               body[max(0, occurrence.start() - 350):
                                    occurrence.start()])
        need(preceding and int(preceding[-1]) == line,
             f"{mode}: {name} first StorageLive source span changed")
        first_lives[name] = {
            "line": line,
            "block": bisect.bisect_right(block_starts, occurrence.start()) - 1,
            "second_call_block": calls[1],
            "after_second_call": True}
    for n in absent:
        need(not re.search(
            rf'(?:local|storageLive|storageDead) = \(name = "_{n}"\)', body),
            f"{mode}: unexpected later local _{n}")
    return {"mode": mode, "full_mir_sha256": sha(full_mir),
            "fnmut_calls": len(calls), "future_first_storage_live": first_lives,
            "later_locals_absent": list(absent),
            "basic_block_count": expected_blocks,
            "normal_edges_linear_noncleanup_continue": True,
            "proof_credit": False}


def audit_saved_input_mutants(a, profile: dict[str, Any]) -> dict[str, Any]:
    """Exercise the exact saved-data admission gates, without proof execution."""
    out = a.evidence / "c2-bound-input-mutants"
    need(not out.exists(), "C2 input-mutant evidence exists")
    out.mkdir()
    original_mir = (a.evidence / "c2-normal-sort4-full-mir.txt").read_text()
    anchor = 'storageLive = (name = "_98")'
    need(original_mir.count(anchor) == 1, "MIR mutant anchor changed")
    mir_mutant = out / "normal-full-mir-mutant.txt"
    mir_mutant.write_text(original_mir.replace(
        anchor, 'storageDead = (name = "_98")', 1))
    mir_hash_refused = sha(mir_mutant) != profile["normal_full_mir_sha256"]
    try:
        audit_future_storage(mir_mutant, FUTURE_NORMAL, "normal-mutant")
    except RuntimeError:
        mir_shape_refused = True
    else:
        mir_shape_refused = False
    original_ast = (a.evidence / "actual-c2-unbound-scaffold-ast.ml").read_text()
    ast_anchor = '"std::ops::FnMut::call_mut"'
    need(original_ast.count(ast_anchor) == 5, "pre-AST mutant anchor changed")
    ast_mutant = out / "pre-ast-mutant.ml"
    ast_mutant.write_text(original_ast.replace(
        ast_anchor, '"unexpected::FnMut::call_mut"', 1))
    ast_hash_refused = sha(ast_mutant) != profile["pre_ast_text_sha256"]
    result = {"normal_mir_hash_refused": mir_hash_refused,
              "normal_mir_storage_shape_refused": mir_shape_refused,
              "pre_ast_hash_refused": ast_hash_refused,
              "classification": "SAVED_INPUT_ADMISSION_REFUSALS_ONLY",
              "proof_credit": False}
    record(a.evidence / "c2-bound-input-mutants.json", result)
    need(all((mir_hash_refused, mir_shape_refused, ast_hash_refused)),
         "C2 bound saved input mutant was admitted")
    return result


def run_bound(a, fixture: Path, c2_tool: Path, env: dict[str, str],
              c1_result: dict[str, Any], c2_result: dict[str, Any],
              snapshot_fn) -> dict[str, Any]:
    """Run only within the already allocated Cloud C1 owner/ledger budget."""
    need(env.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         env.get("LANE") == "o26-sort4-c1-current-recovery" and
         not env.get("GITHUB_ACTIONS"), "C2 bound requires Cloud C1 lane")
    c1 = c1_result.get("bounded_prefix", {}).get("positive", {})
    need(c1.get("classification") == "PREFIX_ONLY_BOUNDED_C1_THEOREM" and
         c1.get("bounded_full_vf0_normal_unwind_post_return_leak") is True,
         "fresh C1 complete prefix gate is absent")
    need(c2_result.get("classification") == "C2_UNBOUND_SCAFFOLD_ONLY_NOT_PROOF" and
         c2_result.get("source_hash_mutant_intended") is True and
         c2_result.get("default_off_c1_prefix_regression", {}).get("classification") ==
             "C2_PATCH_DEFAULT_OFF_C1_PREFIX_REPLAY_PASSED",
         "fresh C2 discovery/refusal prerequisite is absent")
    inv = c2_result.get("diagnostic", {}).get("ast_inventory", {})
    runtime = inv.get("runtime_inventory", {})
    need(inv.get("status") ==
             "CONFIRMED_C2_UNBOUND_SCAFFOLD_RUNTIME_INVENTORY" and
         runtime.get("status") == "C2_RUNTIME_INVENTORY_PRESERVED" and
         [runtime.get("fnmut_count"), runtime.get("selector_count"),
          runtime.get("copy_count")] == [5, 8, 4] and
         runtime.get("c2_fnmut_at_expected_source_line") ==
             [[223, "std::ops::FnMut::call_mut"]],
         "complete five-call/eight-selector/four-copy input certificate absent")

    profile_path = a.proof_root / HERE / "profile.json"
    patch_path = a.proof_root / HERE / "verifast-c2-bound-prefix-TEST.patch"
    profile = json.loads(profile_path.read_text())
    need(profile["classification"] ==
         "EXPERIMENTAL_SOURCE_LINKED_C1_C2_BOUND_PREFIX_NOT_YET_RUN" and
         profile["profile_accepted"] is False and
         profile["default_off_unchanged"] is True and
         profile["unbound_discovery_mandatory_refusal_unchanged"] is True and
         profile["actual_sort4_callable_summary"] is False,
         "C2 bound profile classification changed")
    need(sha(patch_path) == profile["patch_sha256"] and
         sha(c2_tool / TRANSLATOR) == profile["base_translator_sha256"],
         "C2 bound delta/base translator differs")
    need([row for row in patch_path.read_text().splitlines()
          if row.startswith(("--- ", "+++ "))] ==
         [f"--- a/{TRANSLATOR}", f"+++ b/{TRANSLATOR}"],
         "C2 bound patch changes non-translator files")
    source = a.evidence / "c2-discovery-fixture"
    need(source.is_dir(), "fresh C2 discovery source fixture absent")
    need(sha(source / "verified/lib.rs") == profile["annotated_source_sha256"] and
         sha(source / "original/lib.rs") == profile["ghost_stripped_runtime_sha256"] and
         sha(a.evidence / "c2-normal-sort4-full-mir.txt") ==
         profile["normal_full_mir_sha256"] and
         sha(a.evidence / "c2-readonly-sort4-full-mir.txt") ==
         profile["readonly_full_mir_sha256"] and
         sha(a.evidence / "actual-c2-unbound-scaffold-ast.ml") ==
         profile["pre_ast_text_sha256"],
         "fresh source/MIR/pre-AST identity differs from reviewed A5DE")
    future_audit = {
        "normal": audit_future_storage(
            a.evidence / "c2-normal-sort4-full-mir.txt", FUTURE_NORMAL, "normal"),
        "readonly": audit_future_storage(
            a.evidence / "c2-readonly-sort4-full-mir.txt", FUTURE_READONLY,
            "readonly", (110, *range(134, 140))),
        "bounded_ast_future_declarations": 0,
        "allocation_placement_admissibility": "PENDING_INDEPENDENT_AUDIT",
    }
    record(a.evidence / "c2-bound-future-storage-audit.json", future_audit)
    input_mutants = audit_saved_input_mutants(a, profile)
    before = snapshot_fn(a, c2_tool)
    code, _ = stage(a, "patch-check", ["git", "-C", str(c2_tool), "apply",
                                     "--check", str(patch_path)], c2_tool, env, 60)
    need(code == 0, "C2 bound patch does not apply to isolated C2 tool")
    code, _ = stage(a, "patch-apply", ["git", "-C", str(c2_tool), "apply",
                                     str(patch_path)], c2_tool, env, 60)
    need(code == 0 and sha(c2_tool / TRANSLATOR) ==
         profile["patched_translator_sha256"], "C2 bound patch identity differs")
    need(sha(c2_tool / KERNEL) == before["critical"][str(KERNEL)],
         "C2 bound patch changed kernel")
    deps = a.work_root / "vfdeps-adf88dc"
    active = env.copy()
    active["PATH"] = str(deps / "bin") + os.pathsep + active.get("PATH", "")
    active["LD_LIBRARY_PATH"] = ":".join(
        [str(a.compiler_sysroot / "lib"), str(c2_tool / "bin"),
         str(deps / "lib"), active.get("LD_LIBRARY_PATH", "")])
    active["CAPNP_INC_DIR"] = str(deps / "include")
    active["RUSTUP_TOOLCHAIN"] = "nightly-2026-09-25"
    code, _ = stage(a, "console-build",
                    ["make", "-C", str(c2_tool / "src"), "../bin/verifast",
                     "WITHOUT_LABLGTK=yes", "VERBOSE=yes"], c2_tool, active, 900)
    need(code == 0 and sha(c2_tool / TRANSLATOR) ==
         profile["patched_translator_sha256"], "C2 bound console build failed")
    after = snapshot_fn(a, c2_tool)
    need(after["head"] == before["head"] and
         after["critical"][str(KERNEL)] == before["critical"][str(KERNEL)] and
         after["effective_rsspec"] == before["effective_rsspec"] and
         after["proof_std"] == before["proof_std"] and
         all(after["critical"][key] == value for key, value in
             before["critical"].items() if key != str(TRANSLATOR)) and
         all(after["binaries"][key] == value for key, value in
             before["binaries"].items() if key != "bin/verifast"),
         "C2 bound build changed frozen tool inputs")
    record(a.evidence / "c2-bound-tool-snapshot.json", after)

    bound_env = active.copy()
    bound_env.update({
        "SORT4_ACTUAL_AST_SCOPE_TEST": "1",
        "SORT4_ACTUAL_C1_PREFIX_TEST": "0",
        "SORT4_ACTUAL_C2_DISCOVERY_TEST": "0",
        "SORT4_ACTUAL_C2_BOUND_PREFIX_TEST": "1",
        "SORT4_C1_PREFIX_CONTROL": "none",
        "SORT4_C1_OUTPUT_EQ": "0",
        "SORT4_STRICT_LFT_CUT": "1",
        "SORT4_C2_DISCOVERY": "0",
    })
    for key in ("SORT4_C1_DEBT_CONTROL", "SORT4_HRTB_OUTPUT",
                "SORT4_HRTB_OUTPUT_TARGETS", "SORT4_CALLBACK_UNWIND",
                "SORT4_STRICT_LFT_TRACE", "SORT4_STRICT_LFT_RELOCATE"):
        bound_env.pop(key, None)
    verifier = [str(c2_tool / "bin/verifast"), "-rustc_args", "--edition 2021",
                "-verbose", "2", "verified/lib.rs"]

    # The new opt-in must leave both predecessor profiles intact.
    c1_probe = a.evidence / "c2-bound-default-off-c1-fixture"
    need(not c1_probe.exists(), "C2 bound default-off C1 fixture exists")
    shutil.copytree(fixture, c1_probe, symlinks=True)
    off_post = c1_probe / "actual-c1-prefix-post-ast.ml"
    off_post.unlink(missing_ok=True)
    off_env = bound_env.copy()
    off_env.update({"SORT4_ACTUAL_C2_BOUND_PREFIX_TEST": "0",
                    "SORT4_ACTUAL_C1_PREFIX_TEST": "1",
                    "SORT4_C1_OUTPUT_EQ": "1"})
    off_code, off_log = stage(a, "default-off-c1", verifier, c1_probe,
                              off_env, 600)
    off_entries = target_entries(off_log, "sort4_stable")
    off_target = off_log[off_entries[0]:] if len(off_entries) == 1 else ""
    off_ok = (off_code == 0 and "0 errors found (" in off_log and
              "SORT4-ACTUAL-C1-PREFIX-ONLY admitted " in off_log and
              len(off_entries) == 1 and "Executing return statement" in off_target and
              "Leak check." in off_target and
              off_post.is_file() and
              sha(c1_probe / "verified/lib.rs") ==
                  "fddb6f1a0a90948042c99fd1037b7e939586c9e7b9e46a63367a7d876e04ccc9")
    record(a.evidence / "c2-bound-default-off-c1.json", {
        "classification": "PASS" if off_ok else "INCONCLUSIVE",
        "exit": off_code, "post_ast_sha256": sha(off_post) if off_post.is_file() else None,
        "log_sha256": sha(a.evidence / "c2-bound-default-off-c1.log"),
        "proof_credit": "C1 regression only"})
    need(off_ok, "C2 bound default-off C1 regression failed")

    unbound = a.evidence / "c2-bound-unbound-refusal-fixture"
    need(not unbound.exists(), "C2 bound unbound-refusal fixture exists")
    shutil.copytree(source, unbound, symlinks=True)
    unbound_ast = unbound / "actual-c2-unbound-scaffold-ast.ml"
    unbound_ast.unlink(missing_ok=True)
    unbound_env = bound_env.copy()
    unbound_env.update({"SORT4_ACTUAL_C2_BOUND_PREFIX_TEST": "0",
                        "SORT4_ACTUAL_C2_DISCOVERY_TEST": "1"})
    refusal_code, refusal_log = stage(a, "unbound-refusal", verifier,
                                      unbound, unbound_env, 180)
    refusal_marker = "SORT4-C2-DISCOVERY: UNBOUND_C2_LIFETIME_NOT_PROOF scaffold_AST_emitted"
    refusal_ok = (refusal_code in (1, 2) and
                  refusal_log.count(refusal_marker) == 1 and
                  not target_entries(refusal_log, "sort4_stable") and
                  unbound_ast.is_file() and
                  sha(unbound_ast) == profile["pre_ast_text_sha256"])
    record(a.evidence / "c2-bound-unbound-refusal.json", {
        "classification": "PASS" if refusal_ok else "INCONCLUSIVE",
        "exit": refusal_code,
        "scaffold_ast_sha256": sha(unbound_ast) if unbound_ast.is_file() else None,
        "log_sha256": sha(a.evidence / "c2-bound-unbound-refusal.log"),
        "proof_credit": False})
    need(refusal_ok, "C2 bound changed mandatory unbound refusal")

    positive = a.evidence / "c2-bound-positive-fixture"
    need(not positive.exists(), "C2 positive fixture exists")
    shutil.copytree(source, positive, symlinks=True)
    (positive / "actual-c2-bound-pre-ast.ml").unlink(missing_ok=True)
    (positive / "actual-c2-bound-post-ast.ml").unlink(missing_ok=True)
    bound_env["SORT4_C2_BOUND_CONTROL"] = "none"
    code, log = stage(a, "positive", verifier, positive, bound_env, 600)
    pre = positive / "actual-c2-bound-pre-ast.ml"
    post = positive / "actual-c2-bound-post-ast.ml"
    errors = [row for row in log.splitlines()
              if ": error:" in row or row.startswith("Fatal error:")]
    dead = [row for row in log.splitlines() if re.search(r"\): dead code$", row)]
    target = target_entries(log, "sort4_stable")
    helper = {name: target_entries(log, name)
              for name in ("recover_pair", "join_four_owned_cells")}
    target_segment = log[target[0]:] if len(target) == 1 else ""
    post_text = post.read_text(errors="replace") if post.is_file() else ""
    positive_ok = (code == 0 and not errors and not dead and
                   "0 errors found (" in log and len(target) == 1 and
                   all(len(v) == 1 and v[0] < target[0] for v in helper.values()) and
                   "Executing return statement" in target_segment and
                   "Leak check." in target_segment and
                   pre.is_file() and sha(pre) == profile["pre_ast_text_sha256"] and
                   post.is_file() and
                   post_text.count('"std::ops::FnMut::call_mut"') == 2 and
                   post_text.count('"#register_type_projection_equality"') == 2 and
                   all(f'"$_{n}"' not in post_text for n in FUTURE_NORMAL) and
                   "__vf_sort4_C2_UNBOUND_LIFETIME_DECL_PLACEHOLDER" not in post_text and
                   log.count("SORT4-C2-BOUND admitted ") == 1 and
                   "c1_2_call_siblings=1" in log and
                   "future_decl_full_input=18 future_decl_bounded=0" in log and
                   sha(positive / "verified/lib.rs") == profile["annotated_source_sha256"] and
                   sha(positive / "original/lib.rs") == profile["ghost_stripped_runtime_sha256"])
    result: dict[str, Any] = {
        "classification": "C1_C2_BOUND_PREFIX_VF0" if positive_ok else
                          "C1_C2_BOUND_PREFIX_INCONCLUSIVE",
        "positive_exit": code, "positive_ok": positive_ok,
        "positive_errors": errors, "dead_code": dead,
        "same_unit_helper_entries_before_target":
            {key: len(value) == 1 and len(target) == 1 and value[0] < target[0]
             for key, value in helper.items()},
        "target_entry_count": len(target),
        "target_return_seen": "Executing return statement" in target_segment,
        "target_leak_seen": "Leak check." in target_segment,
        "pre_ast_sha256": sha(pre) if pre.is_file() else None,
        "post_ast_sha256": sha(post) if post.is_file() else None,
        "tool_translator_sha256": sha(c2_tool / TRANSLATOR),
        "proof_scope": "bounded two comparison prefix only, full raw posts",
        "accepted": False, "bounded_theorem_admitted": False,
        "actual_sort4_proved": False, "callable_summary": False,
        "allocation_placement_admissibility": "PENDING_INDEPENDENT_AUDIT",
        "future_storage_audit": future_audit,
        "saved_input_mutant_controls": input_mutants,
        "negative_control_causality": "PENDING_FIRST_VC_REVIEW",
        "controls": {},
    }
    record(a.evidence / "c2-bound-result.json", result)
    if not positive_ok:
        return result

    # Each negative gets a fresh fixture and its own exact intended failure.
    # A verifier exit at setup/frontend or another helper is inconclusive.
    for control in CONTROLS:
        case = a.evidence / ("c2-bound-control-" + control)
        need(not case.exists(), f"C2 control fixture exists: {control}")
        shutil.copytree(source, case, symlinks=True)
        local_env = bound_env.copy()
        local_env["SORT4_C2_BOUND_CONTROL"] = control
        exit_code, raw = stage(a, "control-" + control, verifier, case,
                               local_env, 180)
        target_seen = len(target_entries(raw, "sort4_stable")) == 1
        case_errors = [row for row in raw.splitlines()
                       if ": error:" in row or row.startswith("Fatal error:")]
        expected = (exit_code != 0 and target_seen and len(case_errors) >= 1 and
                    "SORT4-C2-BOUND admitted " in raw and
                    ("Assertion might not hold" in raw if "false-assert" in control
                     else True))
        result["controls"][control] = {
            "exit": exit_code, "target_entry": target_seen,
            "first_error": case_errors[0] if case_errors else None,
            "intended_failure_candidate": expected,
            "stage_not_setup": "SORT4-C2-BOUND admitted " in raw,
            "causal_obligation_review": "PENDING_RAW_LOG_REVIEW",
        }
        record(a.evidence / "c2-bound-result.json", result)

    mutant = a.evidence / "c2-bound-source-mutant"
    need(not mutant.exists(), "C2 bound mutant fixture exists")
    shutil.copytree(source, mutant, symlinks=True)
    original_source = (mutant / "verified/lib.rs").read_bytes()
    needle = b"v_base.add(3), &*v_base.add(2)"
    need(original_source.count(needle) == 1, "C2 operand mutation anchor differs")
    (mutant / "verified/lib.rs").write_bytes(
        original_source.replace(needle, b"v_base.add(2), &*v_base.add(3)", 1))
    mutant_code, mutant_log = stage(a, "source-mutant", verifier, mutant,
                                    bound_env, 180)
    mutant_ok = (mutant_code in (1, 2) and
                 mutant_log.count("SORT4-C2-BOUND: verified source SHA256 differs") == 1 and
                 not target_entries(mutant_log, "sort4_stable") and
                 not (mutant / "actual-c2-bound-post-ast.ml").exists())
    result["source_mutant"] = {
        "intended_refusal": mutant_ok, "exit": mutant_code,
        "mutated_source_sha256": sha(mutant / "verified/lib.rs"),
        "log_sha256": sha(a.evidence / "c2-bound-source-mutant.log")}
    record(a.evidence / "c2-bound-result.json", result)
    return result
