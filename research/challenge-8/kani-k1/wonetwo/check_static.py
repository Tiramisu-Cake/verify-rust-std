#!/usr/bin/env python3
"""Static source/name forecast for the fixed-N2 WONE proofs; no proof claims."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE = "305cce3cf11dd9181ca773175bca5804c982f0eb"
WRAP = "library/core/src/slice/sort/shared/smallsort/verify/wrap.rs"
CHILD = "library/core/src/slice/sort/shared/smallsort/verify/wrap/wone.rs"
PREFIX = "slice::sort::shared::smallsort::verify::wrap::wone::"
NEW_NAMES = [
    PREFIX + "unstable_byte_n2",
    PREFIX + "freeze_noncopy_n2",
    PREFIX + "stable_byte_n2",
]
TARGETS = {
    "unstable_byte_n2": "unstable_byte_len",
    "freeze_noncopy_n2": "freeze_noncopy_len",
    "stable_byte_n2": "stable_byte_len",
}


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def item_body(source: str, name: str, masked: str) -> str:
    """Return a simple Rust function body using the inventory parser's brace matcher."""
    found = re.search(r"\bfn\s+" + re.escape(name) + r"\s*\([^)]*\)[^{]*\{", masked)
    if not found:
        raise ValueError(f"missing function {name}")
    opening = masked.find("{", found.start(), found.end())
    closing = predict.matching(masked, opening, "{", "}")
    return source[opening + 1:closing]


def main() -> int:
    global predict
    inv = load("wonetwo_source_inventory", HERE.parent / "cleanup/source_inventory.py")
    lane = load("wonetwo_request_validator", HERE.parent / "tools/kani_k1.py")
    predict = load("wonetwo_predict_inventory", HERE.parent / "c3b/predict_inventory.py")

    ordinary, files = inv.inventory(False)
    cfg_on, _ = inv.inventory(True)
    ordinary_names = [row["name"] for row in ordinary]
    cfg_names = [row["name"] for row in cfg_on]
    old_ordinary = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
    old_cfg = (HERE.parent / "cleanup/cfg-on-expected.txt").read_text().splitlines()
    old_wone_request = json.loads((HERE.parent / "wone/g1.request.json").read_text())
    old_wone_names = [row["name"] for row in old_wone_request["harnesses"]]
    old_n3_request = json.loads((HERE.parent / "wonediag/g1.request.json").read_text())
    old_wone_names += [row["name"] for row in old_n3_request["harnesses"]]
    request_path = HERE / "g1.request.json"
    request = json.loads(request_path.read_text())
    lane.validate_request(request)
    added = [row["name"] for row in request["harnesses"]]
    source_path = REPO / CHILD
    source = source_path.read_text()
    masked = predict.mask_comments_strings(source)

    old_child = subprocess.check_output(["git", "show", f"{BASE}:{CHILD}"], cwd=REPO)
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", BASE, "--", "library"], cwd=REPO, text=True
    ).splitlines()
    addition = source[len(old_child):]
    addition_masked = masked[len(old_child):]
    pfc_pairs = re.findall(
        r"#\s*\[\s*kani\s*::\s*proof_for_contract\s*\(\s*(\w+)\s*\)\s*\]"
        r"\s*(?:#\s*\[[^]]*\]\s*)*fn\s+(\w+)\b",
        addition_masked,
    )
    actual_targets = {fn: target for target, fn in pfc_pairs}
    exact_added = added == NEW_NAMES
    checks = {
        "ordinary_exact_200": len(ordinary_names) == 200 and sorted(ordinary_names) == sorted(old_ordinary),
        "cfg_on_exact_394": len(cfg_names) == 394 and sorted(cfg_names)
            == sorted(old_cfg + old_wone_names + NEW_NAMES),
        "cfg_delta_exact_three": sorted(set(cfg_names) - set(old_cfg + old_wone_names))
            == sorted(NEW_NAMES),
        "old_wone_including_n3_byte_identical_prefix": source_path.read_bytes().startswith(old_child),
        "library_diff_only_wone_child": changed == [CHILD],
        "wrap_module_file_unchanged": (REPO / WRAP).read_bytes()
            == subprocess.check_output(["git", "show", f"{BASE}:{WRAP}"], cwd=REPO),
        "exact_three_requested_names": exact_added,
        "new_harnesses_in_wone_module": all(
            row["source"] == CHILD and "kani_smallsort_controls" in row["gates"]
            for row in cfg_on if row["name"] in NEW_NAMES
        ),
        "request_matches_active": request_path.read_bytes()
            == (HERE.parent / "RUN-REQUEST.json").read_bytes(),
        "three_success_rows_only": [r["expect"] for r in request["harnesses"]] == ["SUCCESS"] * 3,
        "measurement_flags": request["kind"] == "measurement" and request["controls"] is True
            and request["kani_jobs"] == 1 and request["uninit_checks"] is False
            and request["harness_timeout_minutes"] == 10
            and request["runner"] == "gcb-e2-standard-4",
        "request_id_wonetwo_prefix": request["request_id"].startswith("wonetwo-"),
        "rust_line_width_at_most_100": all(len(line) <= 100 for line in source.splitlines()),
        "no_old_length_dispatch_in_additions": "with_backing!" not in addition
            and "input_covers(" not in addition
            and re.search(r"\b(?:match|len)\b", addition_masked) is None,
        "seven_n2_cover_goals": source.count('"wonetwo N2 ') == 7,
        "no_stub_or_assumption_in_additions": "stub" not in source[len(old_child):].lower()
            and "kani::assume" not in source[len(old_child):],
    }

    body_targets = {}
    for pfc, target in TARGETS.items():
        body = item_body(source, pfc, masked)
        body_masked = item_body(masked, pfc, masked)
        pfc_pos = masked.find("fn " + pfc)
        target_match = re.search(r"\bunsafe\s+fn\s+" + target + r"\s*\(", masked)
        checks["target_before_" + pfc] = target_match is not None and target_match.start() < pfc_pos
        checks["unwind16_" + pfc] = "#[kani::unwind(16)]" in masked[max(0, pfc_pos - 120):pfc_pos]
        checks["literal2_" + pfc] = re.search(r"\b" + target + r"\([^;]*?,\s*2\s*,", body_masked) is not None
        checks["backing4_offset1_" + pfc] = "[left, a, b, right]" in body_masked \
            and "wrapping_add(1)" in body_masked
        checks["unrestricted_input_" + pfc] = "kani::any()" in body_masked \
            and "let probe: u8 = kani::any()" in body_masked
        checks["covers_and_frame_" + pfc] = "input_frame(&v, left, right)" in body_masked \
            and "input_covers_n2(a, b, probe)" in body_masked
        checks["no_stub_assumption_backing_macro_" + pfc] = all(
            token not in body.lower() for token in ("stub", "kani::assume", "with_backing!")
        )
        body_targets[pfc] = target
    checks["exact_three_pfc_targets"] = actual_targets == TARGETS

    helper = item_body(source, "input_covers_n2", masked)
    helper_masked = item_body(masked, "input_covers_n2", masked)
    expected_cover_terms = [
        "N2 returns", "N2 reversed keys return", "N2 increasing keys return",
        "N2 tied distinct values", "N2 duplicate full values",
        "N2 independent probe hits input", "N2 independent probe misses input",
    ]
    checks["separate_uncontracted_n2_cover_helper"] = "#[kani::proof" not in masked[
        max(0, masked.find("fn input_covers_n2") - 100):masked.find("fn input_covers_n2")
    ]
    checks["all_seven_cover_kinds"] = all(term in helper for term in expected_cover_terms) \
        and helper.count("kani::cover(") == 7
    checks["helper_has_no_length_dispatch"] = "input_covers(" not in helper_masked

    stable_masked = item_body(masked, "stable_byte_n2", masked)
    checks["stable_byte_full_scratch48"] = "[MaybeUninit::uninit(); 48]" in stable_masked \
        and "&mut scratch" in stable_masked
    checks["stable_byte_not_prefix_scratch"] = "scratch[.." not in stable_masked

    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "base": BASE,
        "checks": checks,
        "ordinary_count": len(ordinary_names),
        "cfg_on_count": len(cfg_names),
        "added_names": added,
        "target_order": body_targets,
        "file_sha256": {p: hashlib.sha256((REPO / p).read_bytes()).hexdigest() for p in files},
        "request_sha256": hashlib.sha256(request_path.read_bytes()).hexdigest(),
        "scope": "Static source/name forecast only; compilation and verification NOT_RUN",
    }
    (HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
