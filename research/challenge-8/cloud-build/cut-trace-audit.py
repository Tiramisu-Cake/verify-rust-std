#!/usr/bin/env python3
"""Fail-closed source and outcome audit for one unaccepted CUT TRACE diagnostic."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

TRACKED = ("src/verifast.ml", "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
           "src/rust_frontend/vf_mir_translator/rust_parser.ml",
           "src/rust_frontend/vf_mir/vf_mir.capnp")
BINARIES = ("bin/verifast", "bin/vf-rust-mir-exporter", "bin/refinement-checker",
            "bin/vf-cxx-ast-exporter", "bin/libz3.so")
TRACE_INSERT = (b'            if Sys.getenv_opt "SORT4_STRICT_LFT_TRACE" = Some "1" then\r\n'
                b'              Printf.eprintf "STRICT-CUT-ENTRY name=%s type=%s\\n%!"\r\n'
                b'                name (string_of_type tp);\r\n')
TRACE_ANCHOR = b'          List.map (fun (name, tp) ->\r\n'
CUT_PATHS = {"src/verifast.ml", "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"}
EXPECTED_ERROR = "verified/lib.rs(84,9-38): Strict lifetime binding has unresolved inference in entry outer type"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(*args: str) -> bytes:
    return subprocess.check_output(args)


def specs(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): sha(p.read_bytes())
            for p in sorted((root / "bin/rust").rglob("*.rsspec"))}


def snapshot(root: Path) -> dict:
    need(run("git", "-C", str(root), "rev-parse", "HEAD").strip().decode() ==
         "f76012fb518703b1d98e243ac4f487f16877cfcb", "VeriFast source pin changed")
    return {
        "head": "f76012fb518703b1d98e243ac4f487f16877cfcb",
        "tracked": {p: sha((root / p).read_bytes()) for p in TRACKED},
        "binaries": {p: sha((root / p).read_bytes()) for p in BINARIES},
        "specs": specs(root),
        "diff_sha256": sha(run("git", "-C", str(root), "diff", "--binary", "HEAD")),
        "modified_files": run("git", "-C", str(root), "diff", "--name-only", "HEAD").decode().splitlines(),
    }


def compare(prod: Path, cut: Path, stock: Path, before_trace: Path,
            baseline: dict) -> dict:
    need(snapshot(prod) == baseline, "production source, specifications or binaries changed")
    need(run("git", "-C", str(cut), "rev-parse", "HEAD").strip().decode() == baseline["head"],
         "isolated source HEAD differs")
    before = before_trace.read_bytes()
    after = (cut / "src/verifast.ml").read_bytes()
    need(before.count(TRACE_ANCHOR) >= 1, "CUT entry anchor absent")
    # The reviewed patch adds these exact three lines at its unique freeze site.
    expected = before.replace(
        TRACE_ANCHOR + b'            name, freeze_strict_type l "entry outer type" [] tp)',
        TRACE_ANCHOR + TRACE_INSERT + b'            name, freeze_strict_type l "entry outer type" [] tp)', 1)
    need(expected != before and after == expected, "TRACE changed more than three print lines")
    need((cut / TRACKED[1]).read_bytes() != (prod / TRACKED[1]).read_bytes(),
         "strict CUT translator delta absent")
    for rel in TRACKED[2:]:
        need((cut / rel).read_bytes() == (prod / rel).read_bytes(), f"unexpected source delta: {rel}")
    need(specs(cut) == baseline["specs"], "specification inventory or bytes changed")
    for rel in BINARIES[1:]:
        need((cut / rel).read_bytes() == (prod / rel).read_bytes(), f"tool binary changed: {rel}")
        need((cut / rel).read_bytes() == (stock / rel).read_bytes(), f"tool binary differs from stock: {rel}")
    modified = set(run("git", "-C", str(cut), "diff", "--name-only", "HEAD").decode().splitlines())
    need(modified == set(baseline["modified_files"]) | CUT_PATHS,
         f"isolated source file inventory changed: {sorted(modified)}")
    return {"production_unchanged": True, "trace_only_print_delta": True,
            "cut_modified_files": sorted(modified), "specs_equal": True,
            "exporter_refiner_schema_equal": True,
            "production_console_sha256": baseline["binaries"]["bin/verifast"],
            "trace_console_sha256": sha((cut / "bin/verifast").read_bytes()),
            "cut_before_trace_verifast_sha256": sha(before),
            "trace_verifast_sha256": sha(after), "accepted": False}


def classify(capture: Path, raw_exit: int, source_audit: dict) -> dict:
    result_path = capture / "positive_f_bound/result.json"
    log_path = capture / "positive_f_bound/full-verification.log"
    result = json.loads(result_path.read_text()) if result_path.is_file() else {}
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    stages = result.get("stages", {})
    required = ("normal-export", "normal-decode", "readonly-export",
                "readonly-decode", "refinement")
    support = all(stages.get(s, {}).get("exit") == 0 for s in required)
    first_errors = [line for line in log.splitlines()
                    if ": error:" in line or line.startswith("Fatal error:") or
                    "Strict lifetime binding has unresolved inference in entry outer type" in line]
    trace_lines = [line for line in log.splitlines() if "STRICT-CUT-ENTRY" in line]
    traced = [re.search(r"STRICT-CUT-ENTRY name=(\S+) type=(.+)$", line)
              for line in trace_lines]
    header = result.get("target_headers") == 1 and "Verifying function 'callback_positive'" in log
    body = result.get("decoded_body_inventory_ok") is True
    original = result.get("source_strip_identity") is True
    error_pattern = (r"verified/lib\.rs\(84,9-38\): (?:error: )?"
                     r"Strict lifetime binding has unresolved inference in entry outer type")
    exact_error = (len(first_errors) == 1 and re.search(error_pattern, first_errors[0]) is not None and
                   stages.get("full-verification", {}).get("exit") in (1, 2))
    reported = result.get("full_error_lines", [])
    exact_error = exact_error and (not reported or reported == first_errors)
    matched = (raw_exit != 0 and support and header and body and original and
               exact_error and trace_lines and all(traced) and source_audit["production_unchanged"])
    return {"classification": "CUT_TRACE_ENTRY_DIAGNOSTIC_MATCH" if matched else "INCONCLUSIVE",
            "accepted": False, "actual_sort4_proved": False,
            "raw_capture_exit": raw_exit, "stage_exits": {k: v.get("exit") for k, v in stages.items()},
            "full_error_lines": first_errors, "expected_error": EXPECTED_ERROR,
            "target_headers": result.get("target_headers"),
            "decoded_body_inventory": result.get("decoded_body_inventory"),
            "source_hashes": result.get("source_hashes"),
            "trace_entries": [{"name": m.group(1), "type": m.group(2)} for m in traced if m],
            "last_trace_entry": ({"name": traced[-1].group(1), "type": traced[-1].group(2)}
                                 if traced and traced[-1] else None),
            "checks": {"support": support, "header": header, "body": body,
                       "original_strip": original, "exact_first_error": exact_error,
                       "trace_present": bool(trace_lines), "trace_format": all(traced)},
            "source_audit": source_audit}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("snapshot", "compare", "classify"))
    p.add_argument("--production-source", type=Path, required=True)
    p.add_argument("--snapshot", type=Path)
    p.add_argument("--cut-source", type=Path)
    p.add_argument("--stock-home", type=Path)
    p.add_argument("--before-trace", type=Path)
    p.add_argument("--capture", type=Path)
    p.add_argument("--raw-exit", type=int)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.mode == "snapshot":
        data = snapshot(a.production_source)
    else:
        need(all((a.snapshot, a.cut_source, a.stock_home, a.before_trace)), "missing comparison inputs")
        data = compare(a.production_source, a.cut_source, a.stock_home, a.before_trace,
                       json.loads(a.snapshot.read_text()))
        if a.mode == "classify":
            need(a.capture is not None and a.raw_exit is not None, "missing capture result")
            data = classify(a.capture, a.raw_exit, data)
    a.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    if a.mode == "classify" and data["classification"] != "CUT_TRACE_ENTRY_DIAGNOSTIC_MATCH":
        raise SystemExit("CUT TRACE is inconclusive")


if __name__ == "__main__":
    main()
