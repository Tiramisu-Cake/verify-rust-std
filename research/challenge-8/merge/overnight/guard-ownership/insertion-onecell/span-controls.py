#!/usr/bin/env python3
"""Run and classify the dedicated allocation-span soundness controls."""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "span-controls.rs"
CASES = {
    "span_positive": "positive local versus incoming fractional frame",
    "span_overlap": "overlapping aliases",
    "span_raw_arbitrary": "arbitrary incoming raw address",
    "span_zero_extent": "zero-sized read has no positive extent",
    "span_retired_local_reuse": "retired local address is not globally fresh",
}


def prepare(evidence: Path) -> dict:
    source = SOURCE.read_bytes()
    head = source.split(b"// CASE_BEGIN ", 1)[0]
    result = {}
    for function, marker in CASES.items():
        begin = b"// CASE_BEGIN " + function.encode() + b"\n"
        end = b"// CASE_END " + function.encode()
        if source.count(begin) != 1 or source.count(end) != 1:
            raise RuntimeError(f"expected unique case delimiters for {function}")
        body = source.split(begin, 1)[1].split(end, 1)[0]
        unit = head + body
        declaration = b"pub unsafe fn " + function.encode()
        if unit.count(declaration) != 1 or unit.count(b"pub unsafe fn ") != 1:
            raise RuntimeError(f"fixture {function} is not isolated")
        lines = unit.decode().splitlines()
        matches = [i + 1 for i, line in enumerate(lines) if "TARGET: " + marker in line]
        if len(matches) != 1:
            raise RuntimeError(f"expected unique target marker for {function}")
        case = evidence / function
        for tree in ("original", "verified"):
            (case / tree).mkdir(parents=True, exist_ok=True)
            (case / tree / "lib.rs").write_bytes(unit)
        read_lines = []
        if function == "span_overlap":
            for needle in (b"    let first = unsafe { *p };\n",
                           b"    let second = unsafe { *q };\n"):
                if unit.count(needle) != 1:
                    raise RuntimeError("overlap read marker changed")
                read_lines.append(unit[:unit.index(needle)].count(b"\n") + 1)
        result[function] = {"target_line": matches[0], "target": {"line": matches[0]},
                            "read_lines": read_lines,
                            "expected_stages": {"exporter": 0, "decode": 0,
                                                 "refinement": 0,
                                                 "verifast": 0 if function == "span_positive" else 1},
                            "source_sha256": __import__("hashlib").sha256(unit).hexdigest()}
    return result


def classify(function: str, case: Path, meta: dict, execution: dict) -> dict:
    stages = execution["stages"]
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    errors = re.findall(r"^.*\berror:.*$", log, re.M | re.I)
    line_pattern = rf"verified/lib\.rs\({meta['target_line']},\d+(?:-\d+(?:,\d+)?)?\): error:"
    exact_target = len(errors) == 1 and re.search(line_pattern, errors[0]) is not None
    target_executed = re.search(
        rf"verified/lib\.rs\({meta['target_line']},\d+(?:-\d+(?:,\d+)?)?\): "
        r"(?:note: )?Executing statement", log) is not None
    reads_executed = all(re.search(
        rf"verified/lib\.rs\({line},\d+(?:-\d+(?:,\d+)?)?\): "
        r"(?:note: )?Executing statement", log) is not None
        for line in meta.get("read_lines", []))
    pipeline_ok = (execution.get("source_unchanged_at_every_stage") is True and
                   all(stages.get(stage) == code for stage, code in
                       meta["expected_stages"].items()))
    if function == "span_positive":
        passed = (pipeline_ok and stages.get("verifast") == 0 and not errors and
                  target_executed and "Leak check." in log and "0 errors found" in log and
                  "Executing return statement" in log)
        classification = "PASS_CONTROL" if passed else "INCONCLUSIVE"
    else:
        intended = (exact_target and "Cannot prove" in errors[0] and
                    (function != "span_overlap" or reads_executed))
        classification = "EXPECTED_REJECTION" if pipeline_ok and stages.get("verifast") == 1 and intended else "INCONCLUSIVE"
    result = {**execution, "case": function, **meta, "errors": errors,
              "target_executed": target_executed,
              "reads_executed": reads_executed,
              "classification": classification, "accepted": False,
              "meaning": "allocation-span soundness control only"}
    (case / "classification.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def run(evidence: Path, args, env: dict, execute_case) -> dict:
    metadata = prepare(evidence / "span-controls")
    results = {}
    for function in CASES:
        case = evidence / "span-controls" / function
        results[function] = classify(function, case, metadata[function], execute_case(case, args, env))
    aggregate = {"profile": args.profile, "accepted": False,
                 "controls": {name: row["classification"] for name, row in results.items()},
                 "case_details": {name: {"source_sha256": row["source_sha256"],
                                          "target_line": row["target_line"],
                                          "expected_stages": row["expected_stages"],
                                          "read_lines": row["read_lines"],
                                          "classification": row["classification"]}
                                  for name, row in results.items()},
                 "case_artifacts": {name: {"directory": f"span-controls/{name}",
                                           "log": f"span-controls/{name}/verifast.log",
                                           "classification": f"span-controls/{name}/classification.json"}
                                   for name in results},
                 "all_matched": all(row["classification"] in {"PASS_CONTROL", "EXPECTED_REJECTION"}
                                    for row in results.values()),
                 "evidence_class": "diagnostic only; not proof or consumer acceptance"}
    (evidence / "span-results.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    return aggregate
