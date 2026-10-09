"""Cloud controls for the exact slice as_mut_ptr MIR translator name."""
from __future__ import annotations
import hashlib, json, os, re, subprocess, time
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _function(source: str, name: str) -> str:
    match = re.search(r"(?m)^fn " + re.escape(name) + r"<[^\n]*\{", source)
    if not match:
        raise RuntimeError("missing control function " + name)
    opening = source.find("{", match.start())
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{": depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[match.start():index + 1] + "\n"
    raise RuntimeError("unterminated control function " + name)


def _stage(root: Path, name: str, argv: list[str], env: dict[str, str], deadline: int) -> dict:
    remaining = deadline - int(time.time())
    if remaining <= 0:
        return {"state": "NOT_RUN", "exit": None, "reason": "deadline elapsed"}
    timeout = min(180, remaining)
    output = root / (name + ".log")
    start = int(time.time())
    with output.open("wb") as stream:
        result = subprocess.run(["timeout", "--signal=TERM", "--kill-after=10s",
                                 str(timeout) + "s", *argv], cwd=root, env=env,
                                stdout=stream, stderr=subprocess.STDOUT, check=False)
    return {"state": "TERMINAL", "exit": result.returncode,
            "elapsed_seconds": int(time.time()) - start, "argv": argv,
            "log": output.name, "log_sha256": sha(output)}


def run_controls(a, env: dict[str, str]) -> dict:
    if env.get('SMALLSORT_EXECUTION_PROVIDER') != 'cloud-build' or env.get('LANE') != 'o26-sort4-caller-entry' or env.get('GITHUB_ACTIONS'):
        raise RuntimeError('slice projection controls are Cloud-only in the exact caller-entry lane')
    root = a.evidence / "slice-projection-controls"
    root.mkdir(parents=True, exist_ok=False)
    source_path = a.proof_root / "research/challenge-8/caller-entry/slice-projection-controls.rs"
    source = source_path.read_text()
    core = a.proof_root / "library/core/src/slice/mod.rs"
    core_text = core.read_text()
    needle = "pub const fn as_mut_ptr(&mut self) -> *mut T {\n        self as *mut [T] as *mut T\n    }"
    source_ok = core_text.count(needle) == 1
    source_certificate = {"path": "library/core/src/slice/mod.rs", "sha256": sha(core),
                         "method_body_exact": source_ok,
                         "method_body": needle if source_ok else None,
                         "controls_source_sha256": sha(source_path)}
    record(root / "source-certificate.json", source_certificate)
    tool = a.production_source / "bin/verifast"
    cases = {
        "slice-positive": (_function(source, "slice_projection"), True, None),
        "maybe-uninit-positive": (_function(source, "maybe_uninit_projection"), True, None),
        "wrong-equality-negative": (_function(source, "wrong_pointer_projection"), False, "Assertion might not hold."),
        "rawdst-ownership-negative": (_function(source, "unrelated_raw_destination"), False, "No matching heap chunks"),
    }
    results = {}
    for name, (body, positive, expected) in cases.items():
        case = root / name
        case.mkdir()
        fixture = "use core::mem::MaybeUninit;\n" + body
        original = re.sub(r"(?m)^\s*//@.*(?:\n|$)", "", fixture)
        for rel, content in (("original/lib.rs", original), ("verified/lib.rs", fixture)):
            path = case / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        source_pair_ok = original == re.sub(r"(?m)^\s*//@.*(?:\n|$)", "", fixture)
        source_certificate["ghost_stripped_pairs"]=source_certificate.get("ghost_stripped_pairs", {})
        source_certificate["ghost_stripped_pairs"][name]={"original_sha256":sha(case/"original/lib.rs"),"verified_sha256":sha(case/"verified/lib.rs"),"source_pair_ok":source_pair_ok}
        stages = {}
        stages["refinement"] = _stage(case, "refinement", [str(a.production_source/"bin/refinement-checker"),
            "--rustc-args", "--edition 2021", "original/lib.rs", "verified/lib.rs"], env,
            a.deadline_epoch)
        vf_log = case / "verification.log"
        stages["verification"] = _stage(case, "verification", [str(tool),
            "-rustc_args", "--edition 2021", "-verbose", "2", "verified/lib.rs"], env,
            a.deadline_epoch)
        log = (case / "verification.log").read_text(errors="replace") if vf_log.exists() else ""
        function_name = {"slice-positive":"slice_projection", "maybe-uninit-positive":"maybe_uninit_projection",
                         "wrong-equality-negative":"wrong_pointer_projection", "rawdst-ownership-negative":"unrelated_raw_destination"}[name]
        entry_matches = list(re.finditer(r"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^\n]*\): Verifying function ['\"]" + re.escape(function_name) + r"(?:<|['\"])", log))
        own_log = log[entry_matches[0].start():] if len(entry_matches) == 1 else ""
        entries = re.findall(r"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\((\d+),[^\n]*\): Executing statement", own_log)
        errors = [line for line in own_log.splitlines() if ": error:" in line or line.startswith("Fatal error:")]
        no_errors = "0 errors found" in own_log and stages["verification"].get("exit") == 0
        leak = "Leak check." in own_log
        target_line = next((i for i, line in enumerate(fixture.splitlines(), 1) if "CONTROL_TARGET_ASSERT" in line), None)
        first_error_line = None
        if errors:
            location = re.search(r"verified/lib\.rs\((\d+),", errors[0])
            first_error_line = int(location.group(1)) if location else None
        projection_line = next((i for i, line in enumerate(fixture.splitlines(), 1)
                                if "CONTROL_PROJECTION_CALL" in line), None)
        target_executed = target_line in [int(value) for value in entries] if target_line else False
        projection_executed = projection_line in [int(value) for value in entries] if projection_line else False
        failure_after_projection = (first_error_line == target_line and
                                    projection_line is not None and
                                    first_error_line > projection_line and
                                    projection_executed)
        expected_match = (expected in errors[0] if errors and expected == "Assertion might not hold."
                          else bool(errors and any(token in errors[0] for token in
                               ("No matching heap chunks",))))
        intended = (stages["verification"].get("exit") == 1 and len(errors) == 1 and
                    expected_match and len(entry_matches) == 1 and failure_after_projection) if not positive else False
        passed = (stages["refinement"].get("exit") == 0 and source_pair_ok and
                  (no_errors and leak and target_executed if positive else intended))
        result = {"classification": "PASS" if passed else "NOT_CONFIRMED",
                  "expected": "VF0/full native post/leak" if positive else expected,
                  "verification_exit": stages["verification"].get("exit"),
                  "first_error": errors[0] if errors else None,
                  "first_error_source_line": first_error_line,
                  "projection_source_line": projection_line,
                  "failure_after_projection": failure_after_projection,
                  "proof_entries": len(entry_matches), "target_line": target_line,
                  "target_assert_executed": target_executed, "projection_executed": projection_executed,
                  "full_native_post_and_leak": bool(positive and no_errors and leak),
                  "intended_negative": intended, "source_pair_ok": source_pair_ok, "stages": stages,
                  "verification_log_sha256": sha(vf_log) if vf_log.exists() else None}
        record(case / "case-result.json", result)
        results[name] = result
    record(root / "source-certificate.json", source_certificate)
    positive_ok = all(results[n]["classification"] == "PASS" for n in ("slice-positive", "maybe-uninit-positive"))
    negative_ok = all(results[n]["intended_negative"] for n in ("wrong-equality-negative", "rawdst-ownership-negative"))
    result = {"all_intended": bool(source_ok and positive_ok and negative_ok),
              "source_certificate": source_certificate, "positive_completion": positive_ok,
              "negative_obligations_reached": negative_ok, "cases": results,
              "profile_acceptance": False, "ownership_axioms_added": False,
              "patch_sha256": "f200a5812149bb2278ded1d1ccb27a104b3dec3c03c5e40c79e30409d0d06916"}
    record(root / "controls-result.json", result)
    return result
