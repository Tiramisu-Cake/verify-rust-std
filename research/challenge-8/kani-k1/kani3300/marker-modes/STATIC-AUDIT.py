#!/usr/bin/env python3
"""Static scope/manifest audit. Does not run any compiler, Kani or the CI runner."""
import ast
import hashlib
import json
from pathlib import Path


def main():
    directory = Path(__file__).resolve().parent
    inputs = json.loads((directory / "INPUTS.json").read_text())
    manifest = json.loads((directory / "TEST-MANIFEST.json").read_text())
    source = Path(inputs["source_repo"])
    suite = source / "tests/json-handler/uninit-contract-mode-boundaries"
    checks = []

    def check(name, condition):
        checks.append({"name": name, "pass": bool(condition)})

    for name, expected in inputs["source_files"].items():
        check("unchanged base source: " + name,
              hashlib.sha256((source / name).read_bytes()).hexdigest() == expected)
    for name, expected in inputs["changed_source_file_sha256"].items():
        check("prepared source fingerprint: " + name,
              hashlib.sha256((source / name).read_bytes()).hexdigest() == expected)
    check("source write scope",
          all(name == "docs/src/reference/experimental/contracts.md"
              or name.startswith("tests/json-handler/uninit-contract-mode-boundaries/")
              for name in inputs["source_changed_files"]))
    for name in ("observe.py", "run.py", "test_observe.py"):
        ast.parse((suite / name).read_text(), filename=name)
        check("Python syntax: " + name, True)
    declared = json.loads((suite / "roots.json").read_text())
    check("exact six proposed roots", manifest["root_count"] == declared["root_count"] == 6
          and len(manifest["roots"]) == len(declared["roots"]) == 6)
    check("same root order/names",
          [r["harness"] for r in manifest["roots"]] == [r["harness"] for r in declared["roots"]])
    check("all verifier results/bindings remain pending",
          all(r["execution_status"] == "NOT_RUN" and r["binding_status"] == "BINDING_PENDING"
              and r["observed_outcome"] is None and r["failures"] is None
              for r in manifest["roots"]))
    check("boundary verdicts not invented",
          all(r["expected_boundary_outcome"] is None and r["expected_boundary_failure_set"] is None
              for r in manifest["roots"]))
    check("CI roots/caps unapproved", manifest["approved_root_count"] is None
          and manifest["approved_caps"] is None and not manifest["ci_dispatch_authorized"])
    check("no mode qualification", not manifest["mode_qualification"])
    for root in declared["roots"]:
        text = (suite / root["file"]).read_text()
        check("source harness: " + root["harness"], "fn " + root["harness"] + "()" in text)
        check("valid new/uninit source: " + root["harness"],
              "MaybeUninit::new(42)" in text and "MaybeUninit::uninit()" in text)
    recursive = (suite / "recursive.rs").read_text()
    check("real recursive edge", "recursive_transfer(relay(value), initialized, depth - 1)" in recursive)
    check("SimpleCheck companion unrolls bounded step", "relay(relay(value))" in recursive
          and "bounded_transfer(relay(value)" not in recursive)
    docs = (source / "docs/src/reference/experimental/contracts.md").read_text()
    check("public limitation and deferral linked", "Part1 support does not currently cover" in docs
          and "diagnostic for missing private initialization state is deferred" in docs
          and "REQUIRED-STATE.md" in docs)
    check("result at most 35 lines",
          len((directory / "RESULT-MARKER-MODES-PREP.md").read_text().splitlines()) <= 35)
    report = dict(kind="static scope/manifest audit; not Rust/compiler/verifier acceptance",
                  status="PASS" if all(c["pass"] for c in checks) else "FAIL",
                  source_head=inputs["source_head"], checks=checks,
                  synthetic_python_tests=dict(count=13, status="PASS", invocation="test_observe.py"),
                  scratchpad_rustfmt=inputs["rustfmt"], compiler="NOT_RUN", verifier="NOT_RUN")
    (directory / "STATIC-CHECKS.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f'{report["status"]}: {len(checks)} static scope/manifest checks; compiler/verifier NOT_RUN')
    return int(report["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
