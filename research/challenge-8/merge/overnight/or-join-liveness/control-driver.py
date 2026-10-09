#!/usr/bin/env python3
"""Cloud-only admission controls for the unaccepted MIR OR join component.

This runs in a third, disposable bin copy. A short verifier run can certify
frontend admission/refusal only; it never classifies a proof as accepted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "PINNED-INPUTS.json"
WRAPPER = HERE / "control-exporter.py"
OVERLAID_PARSER = HERE.parent / "stack-address-admission.py"
PARSER_REPO_PATH = "research/challenge-8/merge/overnight/stack-address-admission.py"
MODES = ("roundtrip", "storage-live-34", "storage-live-36", "goto-38-34",
         "goto-38-36", "statement-count-34", "statement-count-36",
         "real-statement-34", "predecessor-28", "comparison-eq-33",
         "comparison-eq-35", "branch-order-33", "branch-order-35",
         "span-column-34", "span-column-36", "panic-callee", "panic-unwind")
REFUSAL = "MIR-OR-JOIN-LIVENESS: exact source/MIR/AST join admission failed"
SCHEMA_SHA = "f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469"
PARSER_SHA = "9ecce61ca3886f2b9e21bb03d35ce6312da5eb405ff35a0bb37211eb2c49e974"


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def snapshot_bin(home: Path) -> dict[str, str]:
    root = home / "bin"
    require(root.is_dir(), f"tool bin missing: {root}")
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = str(path.relative_to(root))
        if path.is_symlink():
            target = path.resolve(strict=True)
            require(target.is_file(), f"unsupported directory/tool symlink: {path}")
            result[relative] = "symlink:" + os.readlink(path) + ":sha256:" + file_sha(target)
        elif path.is_file():
            result[relative] = "sha256:" + file_sha(path)
        elif path.is_dir():
            result[relative] = "directory"
        else:
            raise ValueError(f"unsupported tool entry: {path}")
    return result


def source_snapshot(home: Path) -> dict[str, str]:
    paths = ("src/verifast.ml",
             "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
             "src/rust_frontend/vf_mir_translator/rust_parser.ml")
    return {name: file_sha(home / name) for name in paths}


def subprocess_stage(argv: list[str], cwd: Path, env: dict[str, str],
                     out: Path, err: Path, seconds: float,
                     deadline: float) -> int:
    cap = min(seconds, deadline - time.monotonic() - 4)
    require(cap >= 1, "global diagnostic work budget exhausted")
    with out.open("wb") as stdout, err.open("wb") as stderr:
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stdout,
                                stderr=stderr, start_new_session=True)
        try:
            return proc.wait(timeout=cap)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=2)
            return 124
        except BaseException:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            raise


def cert(directory: Path) -> dict:
    path = directory / "certificate.json"
    require(path.is_file(), f"wrapper certificate absent: {path}")
    data = json.loads(path.read_text())
    require(isinstance(data, dict) and data.get("classification") == "MESSAGE_CERTIFIED" and
            data.get("exact_semantic_tree_match") is True and
            data.get("official_exit") == 0,
            f"wrapper message certification failed: {path}")
    for filename, key in (("official.stdout.bin", "official_stdout_sha256"),
                          ("official.stderr", "official_stderr_sha256"),
                          ("normal-decode.txt", "normal_decoded_sha256"),
                          ("encoded-input.txt", "encoded_input_sha256"),
                          ("encoded-message.bin", "encoded_message_sha256"),
                          ("redecode.txt", "redecoded_sha256")):
        require(file_sha(directory / filename) == data.get(key),
                f"wrapper artifact hash mismatch: {filename}")
    if data.get("mode") == "roundtrip":
        require(data.get("positive_decoded_text_byte_equal") is True and
                data.get("normal_decoded_sha256") == data.get("redecoded_sha256"),
                "positive normal decoded text is not lossless")
    return data


def positive_ast(path: Path, guard: int) -> bool:
    if not path.is_file():
        return False
    data = path.read_text(errors="replace")
    found = list(re.finditer(
        r'(?m)^\s*Func \(loc "verified/lib\.rs\([^\n]+"bidirectional_merge"',
        data))
    if len(found) != 1:
        return False
    tail = data[found[0].start():]
    # Start after the complete matched header. Skipping one indentation
    # character would find this same Func and truncate its runtime body.
    header_end = found[0].end() - found[0].start()
    next_fn = re.search(r'(?m)^\s*Func \(loc ', tail[header_end:])
    if next_fn:
        tail = tail[:header_end + next_fn.start()]
    join = re.escape(f'verified/lib.rs({guard},51-{guard + 2},10)')
    panic = re.escape(f'verified/lib.rs({guard + 1},13-37)')
    return (len(re.findall(r'GotoStmt \(loc "' + join + r'", "37"\)', tail)) == 2 and
            len(re.findall(r'ExprStmt \(CallExpr \(loc "' + panic +
                           r'", "panic_on_ord_violation"', tail)) == 1)


def classify_frontend(mode: str, log: str, code: int, ast: Path,
                      guard: int, signature: int) -> tuple[str, str]:
    target_executed = any(
        signature <= int(match.group(1)) <= guard + 3
        for match in re.finditer(
            r'verified/lib\.rs\((\d+),[^\n]*Executing statement', log))
    if mode == "roundtrip":
        if positive_ast(ast, guard) and REFUSAL not in log:
            return "ADMISSION_PASS_ONLY", "target proof AST has both live Gotos and the panic body"
        return "INCONCLUSIVE", "positive target proof AST absent or frontend refused"
    if code != 1:
        return "INCONCLUSIVE", f"negative verifier exit {code} is not exact frontend refusal"
    refusal_lines = [line for line in log.splitlines() if REFUSAL in line]
    if len(refusal_lines) != 1 or not re.search(
            r'verified/lib\.rs\(' + str(signature) + r',', refusal_lines[0]):
        return "INCONCLUSIVE", "new matcher refusal/location not unique at target signature"
    errors = [line for line in log.splitlines()
              if re.search(r"\berror:", line, re.IGNORECASE)]
    if len(errors) != 1 or REFUSAL not in errors[0]:
        return "INCONCLUSIVE", "unrelated frontend or proof error accompanied refusal"
    if target_executed:
        return "INCONCLUSIVE", "target body execution preceded frontend refusal"
    return "EXPECTED_FRONTEND_REFUSAL", "exact new matcher refusal before target body"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--six-home", type=Path, required=True)
    parser.add_argument("--seven-home", type=Path, required=True)
    parser.add_argument("--seven-build-manifest", type=Path, required=True)
    parser.add_argument("--prepared-case", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--normal-mir-reference", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--sysroot", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--work-seconds", type=int, default=240)
    args = parser.parse_args()
    start = time.monotonic()
    require(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build",
            "Cloud Build provider identity required")
    require(1 <= args.work_seconds <= 240, "driver work cap must be 1..240 seconds")
    require(str(args.evidence).startswith("/workspace/") and not args.evidence.exists(),
            "fresh /workspace diagnostic evidence path required")
    evidence = args.evidence
    evidence.mkdir(parents=True)
    report: dict = {"component": "MIR-OR-JOIN-LIVENESS-CONTROLS",
                    "classification": "INCONCLUSIVE", "accepted": False,
                    "proof_accepted": False, "modes": {},
                    "work_seconds": args.work_seconds,
                    "required_modes": list(MODES), "full_shape_matrix_complete": False,
                    "source_hash_gate": {"classification": "NOT_RUN"}}
    deadline = start + args.work_seconds
    def expired(_signum, _frame):
        raise TimeoutError("global diagnostic work cap reached")
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL,
                     max(0.001, deadline - time.monotonic()))
    try:
        provider = Path(os.environ["SMALLSORT_PROVIDER_FILE"])
        check = subprocess_stage([sys.executable, str(provider)], Path("/workspace"),
                                 dict(os.environ), evidence / "provider.stdout",
                                 evidence / "provider.stderr", 8, deadline)
        require(check == 0, "Cloud provider certificate rejected")
        pin = json.loads(MANIFEST.read_text())
        build = json.loads(args.seven_build_manifest.read_text())
        preflight = json.loads(args.preflight.read_text())
        require(pin.get("admission_state") == "EXPERIMENTAL_CLOUD_TRIAL" and
                pin.get("component") == "MIR-OR-JOIN-LIVENESS",
                "production seven profile has no exact trial admission")
        require(build.get("accepted") is False and
                build.get("source_commit") == pin.get("verifast_commit") and
                build.get("component_manifest_sha256") == file_sha(MANIFEST) and
                build.get("component_patch_sha256") == pin.get("component_patch_sha256") and
                build.get("base_six_full_diff_sha256") ==
                    pin.get("baseline_applied_profile_sha256") and
                all(build.get(key) is True for key in (
                    "kernel_unchanged", "parser_unchanged", "prelude_unchanged",
                    "stdlib_unchanged", "exporter_unchanged", "refiner_unchanged")) and
                build.get("seven_console_sha256") == file_sha(args.seven_home / "bin/verifast") and
                build.get("component_translator_sha256") ==
                    file_sha(args.seven_home /
                             "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml") and
                build.get("base_six_console_sha256") == file_sha(args.six_home / "bin/verifast"),
                "seven build or six baseline identity mismatch")
        require(file_sha(args.schema) == SCHEMA_SHA,
                "normal MIR schema pin mismatch")
        proof_sha = os.environ.get("PROOF_SHA", "")
        require(re.fullmatch(r"[0-9a-f]{40}", proof_sha) is not None,
                "exact Cloud proof source commit is absent")
        repo = HERE.parents[4]
        head_status = subprocess_stage(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], repo,
            dict(os.environ), evidence / "proof-checkout-head.stdout",
            evidence / "proof-checkout-head.stderr", 5, deadline)
        require(head_status == 0 and
                (evidence / "proof-checkout-head.stdout").read_text().strip() == proof_sha,
                "Cloud proof checkout differs from exact proof SHA")
        parser_copy = evidence / "stack-address-capnp-parser.original.py"
        parser_show = subprocess_stage(
            ["git", "-C", str(repo), "show",
             f"{proof_sha}:{PARSER_REPO_PATH}"], repo,
            dict(os.environ), parser_copy,
            evidence / "parser-git-show.stderr", 10, deadline)
        require(parser_show == 0 and file_sha(parser_copy) == PARSER_SHA,
                "exact committed pre-overlay Capnp parser blob differs")
        report["parser_identity"] = {
            "proof_sha": proof_sha,
            "committed_parser_sha256": file_sha(parser_copy),
            "cloud_overlay_parser_sha256": file_sha(OVERLAID_PARSER)}
        verified = args.prepared_case / "verified/lib.rs"
        original = args.prepared_case / "original/lib.rs"
        require(file_sha(verified) == pin.get("admitted_source_sha256") ==
                preflight.get("verified_sha256") and
                file_sha(original) == preflight.get("original_sha256") and
                preflight.get("accepted") is False,
                "prepared actual source does not match exact preflight")
        signature = pin.get("admitted_signature_line")
        guard = pin.get("admitted_guard_line")
        require(type(signature) is int and type(guard) is int and 0 < signature < guard,
                "admitted source locations are absent")
        lines = verified.read_text().splitlines()
        require(lines[signature - 1].startswith(
                "unsafe fn bidirectional_merge<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(") and
                lines[guard - 1] ==
                "        if left != left_end || right != right_end {" and
                lines[guard] == "            panic_on_ord_violation();",
                "prepared target signature/guard/panic changed")
        normal_sha = file_sha(args.normal_mir_reference)
        require(args.normal_mir_reference.stat().st_size > 0,
                "production normal MIR reference absent")
        provenance_path = args.normal_mir_reference.with_name(
            "normal-exporter-provenance.json")
        provenance = json.loads(provenance_path.read_text())
        expected_normal_args = ["verified/lib.rs", "--sysroot=" + str(args.sysroot),
                                "--edition", "2021"]
        require(provenance.get("normal_preprocess") is True and
                provenance.get("source_sha256") == file_sha(verified) and
                provenance.get("mir_sha256") == normal_sha and
                isinstance(provenance.get("decoded_sha256"), str) and
                provenance.get("source_unchanged") is True and
                provenance.get("command") ==
                    [str(args.seven_home / "bin/vf-rust-mir-exporter"),
                     *expected_normal_args],
                "normal MIR reference lacks actual normal-mode provenance")
        report["normal_reference_provenance_sha256"] = file_sha(provenance_path)
        # Test the external admission boundary independently of the MIR wrapper.
        # This private harmless comment edit never reaches any exporter/refiner.
        source_gate_dir = evidence / "source-hash-gate"
        source_gate_dir.mkdir()
        changed_source = source_gate_dir / "lib.rs"
        changed_source.write_bytes(verified.read_bytes() + b"\n// source admission control\n")
        admission_command = [sys.executable, str(HERE / "admit-source.py"),
            "--manifest", str(MANIFEST), "--source", str(changed_source),
            "--baseline-translator", str(args.seven_build_manifest.parent / "translator.six.ml"),
            "--component-patch", str(HERE / "or-join-liveness.patch"),
            "--component-translator", str(args.seven_build_manifest.parent / "translator.seven.ml")]
        admission_exit = subprocess_stage(admission_command, HERE, dict(os.environ),
            source_gate_dir / "stdout", source_gate_dir / "stderr", 8, deadline)
        admission_out = (source_gate_dir / "stdout").read_text()
        admission_err = (source_gate_dir / "stderr").read_text()
        source_gate_pass = (admission_exit == 2 and admission_out == "" and
            admission_err == "MIR-OR-JOIN-LIVENESS refusal: admitted source hash mismatch\n" and
            file_sha(verified) == pin["admitted_source_sha256"])
        report["source_hash_gate"] = {
            "classification": "EXPECTED_SOURCE_HASH_REFUSAL" if source_gate_pass else "INCONCLUSIVE",
            "stage": "SOURCE_ADMISSION_BEFORE_EXPORT", "exit_code": admission_exit,
            "command": admission_command, "mutated_source_sha256": file_sha(changed_source),
            "original_source_sha256": file_sha(verified),
            "stdout_sha256": file_sha(source_gate_dir / "stdout"),
            "stderr_sha256": file_sha(source_gate_dir / "stderr"), "accepted": False}
        six_before = {"bin": snapshot_bin(args.six_home),
                      "source": source_snapshot(args.six_home)}
        seven_before = {"bin": snapshot_bin(args.seven_home),
                        "source": source_snapshot(args.seven_home)}
        (evidence / "six-tool-snapshot-before.json").write_text(
            json.dumps(six_before, indent=2, sort_keys=True) + "\n")
        (evidence / "seven-tool-snapshot-before.json").write_text(
            json.dumps(seven_before, indent=2, sort_keys=True) + "\n")
        official_sha = file_sha(args.seven_home / "bin/vf-rust-mir-exporter")
        require(official_sha == pin.get("release_exporter_sha256") and
                file_sha(args.six_home / "bin/vf-rust-mir-exporter") == official_sha,
                "unchanged official exporter pin mismatch")
        test_home = Path(os.environ["RUNNER_TEMP"]) / "challenge8-or-join-control-tools"
        require(str(test_home).startswith("/workspace/") and
                not test_home.exists() and not test_home.is_symlink() and
                test_home != args.six_home and
                test_home != args.seven_home,
                "separate diagnostic tool copy is not fresh")
        shutil.copytree(args.seven_home / "bin", test_home / "bin", symlinks=True)
        copied = snapshot_bin(test_home)
        require(copied == seven_before["bin"],
                "diagnostic copied bin differs before wrapper installation")
        (evidence / "diagnostic-tool-snapshot-before.json").write_text(
            json.dumps(copied, indent=2, sort_keys=True) + "\n")
        official_copy = test_home / "bin/vf-rust-mir-exporter.official"
        wrapper_bin = test_home / "bin/vf-rust-mir-exporter"
        require(not official_copy.exists() and wrapper_bin.is_file() and
                not wrapper_bin.is_symlink(),
                "diagnostic wrapper slot is not a fresh regular exporter copy")
        wrapper_bin.rename(official_copy)
        shutil.copy2(WRAPPER, wrapper_bin)
        wrapper_bin.chmod(0o755)
        installed = snapshot_bin(test_home)
        for name, value in seven_before["bin"].items():
            if name != "vf-rust-mir-exporter":
                require(installed.get(name) == value,
                        f"unintended diagnostic tool change: {name}")
        require(file_sha(official_copy) == official_sha and
                file_sha(wrapper_bin) == file_sha(WRAPPER),
                "official exporter/wrapper copy hash mismatch")
        (evidence / "diagnostic-tool-snapshot-installed.json").write_text(
            json.dumps(installed, indent=2, sort_keys=True) + "\n")
        report["tool_identity"] = {
            "six_bin_manifest_sha256": hashlib.sha256(
                json.dumps(six_before["bin"], sort_keys=True).encode()).hexdigest(),
            "seven_bin_manifest_sha256": hashlib.sha256(
                json.dumps(seven_before["bin"], sort_keys=True).encode()).hexdigest(),
            "diagnostic_bin_manifest_sha256": hashlib.sha256(
                json.dumps(installed, sort_keys=True).encode()).hexdigest(),
            "official_exporter_sha256": official_sha,
            "diagnostic_wrapper_sha256": file_sha(wrapper_bin),
            "seven_console_sha256": file_sha(test_home / "bin/verifast"),
            "normal_reference_sha256": normal_sha,
            "schema_sha256": file_sha(args.schema),
            "prepared_original_sha256": file_sha(original),
            "prepared_verified_sha256": file_sha(verified)}
        env_base = dict(os.environ)
        env_base.update({
            "OR_JOIN_CONTROL_EVIDENCE": str(evidence / "calls"),
            "OR_JOIN_CONTROL_SCHEMA": str(args.schema),
            "OR_JOIN_CONTROL_PARSER": str(parser_copy),
            "OR_JOIN_CONTROL_SOURCE_SHA": file_sha(verified),
            "OR_JOIN_CONTROL_NORMAL_MIR_SHA": normal_sha,
            "OR_JOIN_CONTROL_OFFICIAL_SHA": official_sha,
            "OR_JOIN_CONTROL_SYSROOT": str(args.sysroot),
            "OR_JOIN_CONTROL_GUARD_LINE": str(guard),
            "LD_LIBRARY_PATH":
                f"{args.sysroot}/lib:{test_home}/bin:/tmp/vfdeps-adf88dc/lib:" +
                os.environ.get("LD_LIBRARY_PATH", ""),
        })
        (evidence / "calls").mkdir()
        all_pass = source_gate_pass
        for mode in MODES:
            require(time.monotonic() + 15 < deadline,
                    "global work budget exhausted before next control")
            case_dir = evidence / "cases" / mode
            (case_dir / "verified").mkdir(parents=True)
            (case_dir / "original").mkdir()
            shutil.copy2(verified, case_dir / "verified/lib.rs")
            shutil.copy2(original, case_dir / "original/lib.rs")
            refinement_command = [
                str(args.seven_home / "bin/refinement-checker"),
                "--rustc-args", "--edition 2021",
                "original/lib.rs", "verified/lib.rs"]
            refinement = subprocess_stage(refinement_command, case_dir, env_base,
                case_dir / "refinement.stdout", case_dir / "refinement.stderr",
                20, deadline)
            env = dict(env_base, OR_JOIN_CONTROL_MODE=mode,
                       OR_JOIN_CONTROL_ROLE="manual")
            normal_args = expected_normal_args
            manual_command = [str(wrapper_bin), *normal_args]
            manual = subprocess_stage(manual_command, case_dir,
                                      env, case_dir / "manual-message.bin",
                                      case_dir / "manual.stderr", 55, deadline)
            row: dict = {"mode": mode, "manual_exit": manual,
                         "official_refinement_exit": refinement,
                         "official_refinement_command": refinement_command,
                         "manual_exporter_command": manual_command,
                         "classification": "INCONCLUSIVE", "accepted": False}
            report["modes"][mode] = row
            if manual != 0:
                all_pass = False
                continue
            manual_cert = cert(evidence / "calls" / mode / "manual")
            require(file_sha(case_dir / "manual-message.bin") ==
                    manual_cert["encoded_message_sha256"] and
                    manual_cert["normal_decoded_sha256"] ==
                    provenance["decoded_sha256"],
                    "manual wrapper output differs from certified message")
            env["OR_JOIN_CONTROL_ROLE"] = "frontend"
            verifier_command = [
                str(test_home / "bin/verifast"), "-rustc_args", "--edition 2021",
                "-verbose", "1", "-dump_ast_with_locs", "proof-ast.ml",
                "verified/lib.rs"]
            verifier = subprocess_stage(verifier_command, case_dir, env,
                case_dir / "verifast.stdout", case_dir / "verifast.stderr",
                10 if mode == "roundtrip" else 20, deadline)
            row["verifast_exit"] = verifier
            row["verifast_command"] = verifier_command
            call_dir = evidence / "calls" / mode / "frontend"
            if not (call_dir / "certificate.json").is_file():
                row["reason"] = "frontend did not invoke diagnostic exporter"
                all_pass = False
                continue
            front_cert = cert(call_dir)
            require(front_cert["official_stdout_sha256"] ==
                    manual_cert["official_stdout_sha256"] == normal_sha and
                    front_cert["encoded_message_sha256"] ==
                    manual_cert["encoded_message_sha256"] and
                    all(item.get("source_sha256") == file_sha(verified) and
                        item.get("official_exporter_sha256") == official_sha and
                        item.get("schema_sha256") == SCHEMA_SHA and
                        item.get("parser_sha256") == PARSER_SHA
                        for item in (manual_cert, front_cert)),
                    "manual and actual frontend MIR inputs differ")
            row.update({"manual_certificate": manual_cert,
                        "frontend_certificate": front_cert,
                        "source_unchanged":
                            file_sha(case_dir / "verified/lib.rs") == file_sha(verified) and
                            file_sha(case_dir / "original/lib.rs") == file_sha(original)})
            log = ((case_dir / "verifast.stdout").read_text(errors="replace") +
                   (case_dir / "verifast.stderr").read_text(errors="replace"))
            classification, reason = classify_frontend(
                mode, log, verifier, case_dir / "proof-ast.ml", guard, signature)
            if not row["source_unchanged"]:
                classification, reason = "INCONCLUSIVE", "source changed during diagnostic"
            if refinement != 0:
                classification, reason = "INCONCLUSIVE", "unchanged official refinement failed"
            row.update({"classification": classification, "reason": reason,
                        "proof_accepted": False,
                        "log_sha256": hashlib.sha256(log.encode()).hexdigest(),
                        "proof_ast_sha256": file_sha(case_dir / "proof-ast.ml")
                        if (case_dir / "proof-ast.ml").is_file() else None})
            if classification not in {"ADMISSION_PASS_ONLY", "EXPECTED_FRONTEND_REFUSAL"}:
                all_pass = False
        six_after = {"bin": snapshot_bin(args.six_home),
                     "source": source_snapshot(args.six_home)}
        seven_after = {"bin": snapshot_bin(args.seven_home),
                       "source": source_snapshot(args.seven_home)}
        test_after = snapshot_bin(test_home)
        (evidence / "six-tool-snapshot-after.json").write_text(
            json.dumps(six_after, indent=2, sort_keys=True) + "\n")
        (evidence / "seven-tool-snapshot-after.json").write_text(
            json.dumps(seven_after, indent=2, sort_keys=True) + "\n")
        (evidence / "diagnostic-tool-snapshot-after.json").write_text(
            json.dumps(test_after, indent=2, sort_keys=True) + "\n")
        require(six_after == six_before and seven_after == seven_before and
                test_after == installed,
                "production or diagnostic tool bytes changed during controls")
        report["tool_homes_unchanged"] = True
        report["full_shape_matrix_complete"] = bool(
            all_pass and set(report["modes"]) == set(MODES) and
            report["modes"]["roundtrip"].get("classification") == "ADMISSION_PASS_ONLY" and
            all(report["modes"][mode].get("classification") == "EXPECTED_FRONTEND_REFUSAL"
                for mode in MODES if mode != "roundtrip"))
        report["classification"] = (
            "ADMISSION_CONTROLS_OBSERVED_UNACCEPTED"
            if report["full_shape_matrix_complete"] else "INCONCLUSIVE")
    except (OSError, KeyError, ValueError, RuntimeError, TimeoutError,
            json.JSONDecodeError, subprocess.SubprocessError) as exc:
        report["refusal"] = str(exc)
        report["classification"] = "INCONCLUSIVE"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        report["elapsed_seconds"] = round(time.monotonic() - start, 3)
        report["accepted"] = False
        (evidence / "control-driver.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    try:
        main()
    except (OSError, KeyError, ValueError) as exc:
        print(f"MIR-OR-JOIN control driver setup refusal: {exc}", file=sys.stderr)
        raise SystemExit(2)
