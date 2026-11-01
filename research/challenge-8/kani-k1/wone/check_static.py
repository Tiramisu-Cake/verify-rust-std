#!/usr/bin/env python3
"""WONE source forecast and immutable ordinary-code checks; no compiler/proof claims."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE = "4ffdf6e267"
WRAP = "library/core/src/slice/sort/shared/smallsort/verify/wrap.rs"
CHILD = WRAP[:-3] + "/wone.rs"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    inv = load("wone_source_inventory", HERE.parent / "cleanup/source_inventory.py")
    lane = load("wone_request_validator", HERE.parent / "tools/kani_k1.py")
    ordinary, files = inv.inventory(False)
    cfg_on, _ = inv.inventory(True)
    ordinary_names = [row["name"] for row in ordinary]
    cfg_names = [row["name"] for row in cfg_on]
    old_ordinary = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
    old_cfg = (HERE.parent / "cleanup/cfg-on-expected.txt").read_text().splitlines()
    request = json.loads((HERE / "g1.request.json").read_text())
    lane.validate_request(request)
    added = [row["name"] for row in request["harnesses"]]
    new = (REPO / CHILD).read_text()
    old_wrap = subprocess.check_output(["git", "show", f"{BASE}:{WRAP}"], cwd=REPO)
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", BASE, "--", "library"], cwd=REPO, text=True
    ).splitlines()
    checks = {
        "ordinary_exact_200": len(ordinary_names) == 200 and sorted(ordinary_names) == sorted(old_ordinary),
        "cfg_on_exact_388": len(cfg_names) == 388 and sorted(cfg_names) == sorted(old_cfg + added),
        "cfg_delta_exact_six": sorted(set(cfg_names) - set(old_cfg)) == sorted(added),
        "old_wrap_byte_identical_prefix": (REPO / WRAP).read_bytes() == old_wrap
            + b"\n#[cfg(kani_smallsort_controls)]\nmod wone;\n",
        "library_diff_paths": set(changed) <= {WRAP, CHILD},
        "child_inherits_opt_in": all(
            "kani_smallsort_controls" in row["gates"]
            for row in cfg_on if row["name"] in added
        ),
        "request_matches_active": (HERE / "g1.request.json").read_bytes()
            == (HERE.parent / "RUN-REQUEST.json").read_bytes(),
        "six_rows_four_success_two_failed": [r["expect"] for r in request["harnesses"]]
            == ["SUCCESS"] * 4 + ["FAILED"] * 2,
        "measurement_flags": request["kind"] == "measurement" and request["controls"]
            and request["kani_jobs"] == 1 and not request["uninit_checks"]
            and request["harness_timeout_minutes"] == 10,
        "no_stubs": "stub" not in new,
        "length_bound_four_targets": new.count("#[kani::requires(len <= 3)]") == 4,
        "no_comparator_in_model": "cmp" not in new[new.index("fn sorted<"):new.index("// A body guard")],
        "line_width": all(len(line) <= 100 for line in new.splitlines()),
    }
    order = []
    for target in re.findall(r"#\[kani::proof_for_contract\((\w+)\)\]", new):
        before = new.index("unsafe fn " + target + "(") < new.index(
            "#[kani::proof_for_contract(" + target + ")]"
        )
        checks["target_before_pfc_" + target] = before
        order.append(target)
    checks["four_distinct_pfc_targets"] = len(set(order)) == 4
    for row in request["harnesses"][-2:]:
        checks["literal_" + row["name"].split("::")[-1]] = (
            new.count('"' + row["expect_check"] + '"') == 1
        )
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL", "base": BASE,
        "checks": checks, "ordinary_count": len(ordinary_names), "cfg_on_count": len(cfg_names),
        "ordinary_names": ordinary_names, "added_names": added, "target_order": order,
        "file_sha256": {p: hashlib.sha256((REPO / p).read_bytes()).hexdigest() for p in files},
        "request_sha256": hashlib.sha256((HERE / "g1.request.json").read_bytes()).hexdigest(),
        "scope": "Static source/name checks only; native compilation and verification NOT_RUN",
    }
    (HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("ordinary_names", "file_sha256")}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
