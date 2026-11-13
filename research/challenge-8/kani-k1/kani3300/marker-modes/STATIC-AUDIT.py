#!/usr/bin/env python3
"""Audit this STOP handoff's source fingerprints and declarations, not Kani behavior."""
import hashlib
import json
from pathlib import Path


def main():
    directory = Path(__file__).resolve().parent
    inputs = json.loads((directory / "INPUTS.json").read_text())
    manifest = json.loads((directory / "TEST-MANIFEST.json").read_text())
    source = Path(inputs["source_repo"])
    checks = []

    def check(name, condition):
        checks.append({"name": name, "pass": bool(condition)})

    for name, expected in inputs["source_files"].items():
        check("source fingerprint: " + name,
              hashlib.sha256((source / name).read_bytes()).hexdigest() == expected)

    compiler = source / "kani-compiler/src"
    contract = (compiler / "codegen_cprover_gotoc/codegen/contract.rs").read_text()
    transform = (compiler / "kani_middle/transform/mod.rs").read_text()
    resolution = (compiler / "kani_middle/points_to/points_to_analysis.rs").read_text()
    interface = (compiler / "codegen_cprover_gotoc/compiler_interface.rs").read_text()
    reachability = (compiler / "kani_middle/reachability.rs").read_text()
    check("unchanged lookup fallback anchor", ".unwrap_or_default()" in contract)
    check("body cache is not an effect map anchor",
          "cache: HashMap<Instance, TransformationResult>" in transform)
    check("function-pointer resolution rejection anchor",
          'unsupported_call_reason("calls through function pointers")' in resolution)
    check("reachability includes address-taken functions anchor",
          "PointerCoercion::ReifyFnPointer" in reachability)
    check("immutable finalization follows contract attachment anchor",
          interface.index("gcx.handle_check_contract") <
          interface.index("gcx.finalize_immutable_allocations()"))
    check("no implementation claimed",
          inputs["source_commit"] is None and inputs["source_changed_files"] == []
          and not manifest["compiler_units_implemented"])
    check("all specified scenarios explicitly not executed",
          all(case["execution_status"] == "NOT_RUN"
              and case["fixture_status"] == "NOT_PREPARED_STOP"
              for case in manifest["lookup_and_fact_scenarios"]
              + manifest["integration_candidates"]))
    check("mode/root bindings pending",
          all(root["binding_status"] == "BINDING_PENDING"
              and root["completed_outcome"] is None and root["failures"] is None
              for root in manifest["integration_candidates"]))
    check("unknown scenarios retained",
          {case["id"] for case in manifest["lookup_and_fact_scenarios"]
           if case.get("required_state") == "UNKNOWN"}
          == {"unknown-absent", "unknown-binding"})
    check("CI remains unapproved",
          manifest["ci_approved_root_count"] is None and not manifest["verifier_acceptance"])
    check("result within required 35 lines",
          len((directory / "RESULT-MARKER-MODES-PREP.md").read_text().splitlines()) <= 35)
    report = {
        "kind": "static STOP handoff audit; not production resolver/unit/verifier tests",
        "status": "PASS" if all(item["pass"] for item in checks) else "FAIL",
        "source_head": inputs["source_head"],
        "checks": checks,
        "compiler_units": "NOT_RUN",
        "verifier": "NOT_RUN",
    }
    (directory / "STATIC-CHECKS.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f'{report["status"]}: {len(checks)} static handoff checks; compiler/verifier NOT_RUN')
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
