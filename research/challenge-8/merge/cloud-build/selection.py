#!/usr/bin/env python3
"""Validate the committed merge-lane group selection without executing proofs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

SCHEMA = "smallsort-merge-selection-v1"
FULL_GROUPS = {
    "rust-profile-smoke", "G2-compatibility", "A-compatibility", "B-compatibility",
    "native-baselines", "rust-unwind-baselines", "callback-model-diagnostics",
    "tuple2-shape-admission", "tuple2-resource-diagnostics", "callback-borrow-diagnostic",
    "prepared-hrtb-diagnostics", "hrtb-admission-certificate", "callback-cleanup-diagnostics",
    "copy-model-diagnostics", "wrapping-acceptance", "pointer-bridge-diagnostic",
    "pointer-domain-bridge", "owned-array-resource-diagnostic", "scratch-option-resource-diagnostic",
    "concrete-zst-diagnostic", "experimental-rust-regression", "tuple-layout-entry-diagnostics",
    "trace-entry-tuple-diagnostics", "usize-source-admission", "usize-primitive-diagnostics",
    "stack-address-admission-diagnostics", "stack-address-role-control-preparation",
    "stack-address-role-controls", "pointer-quartet-trace-entry-negative",
    "pointer-quartet-trace-diagnostic", "actual-source-preparation", "actual-callee-applicability",
    "bidirectional-option-stages", "bidirectional-small-source-preparation",
    "bidirectional-len23-diagnostic", "pointer-modular-trace-entry-negative",
    "pointer-modular-trace-diagnostic",
}
NEW_GROUPS = {
    "actual-copy-on-drop-resource-diagnostic",
    "actual-copy-on-drop-stock-diagnostic",
    "native-source-pair-turnover-resource-diagnostic",
    "native-source-pair-turnover-stock-diagnostic",
    "source-pair-turnover-resource-diagnostic",
    "cleanup-recovery-hidden-type-diagnostic",
    "current-owner-handoff-resource-diagnostic",
    "current-owner-handoff-stock-diagnostic",
    "mir-or-join-seven-diagnostic",
    "checked-current-owner-permutation",
    "checked-current-owner-permutation-stock",
    "current-owner-memory-cell-diagnostic",
    "current-owner-memory-cell-stock-diagnostic",
    "guard-payload-own-diagnostic",
    "guard-payload-own-stock-diagnostic",
    "guard-construction-fragment-diagnostic",
    "guard-construction-fragment-stock-diagnostic",
    "guard-construction-nonprecise-v3-diagnostic",
    "guard-construction-nonprecise-v3-stock-diagnostic",
    "guard-drop-geometry-v3-diagnostic",
    "guard-drop-geometry-v3-stock-diagnostic",
    "guard-construction-fbc-v4-diagnostic",
    "guard-construction-fbc-v4-stock-diagnostic",
    "insertion-onecell-guard-diagnostic",
}
KNOWN_GROUPS = FULL_GROUPS | NEW_GROUPS
DEPENDENCIES = {
    # This diagnostic performs its own exact std-source extraction/admission.
    # Historical actual/bidirectional preparation artifacts are not consumed.
    "insertion-onecell-guard-diagnostic": {"rust-profile-smoke"},
    "guard-construction-fbc-v4-diagnostic": {"actual-source-preparation", "bidirectional-small-source-preparation", "rust-profile-smoke"},
    "guard-construction-fbc-v4-stock-diagnostic": {"actual-source-preparation", "bidirectional-small-source-preparation", "rust-profile-smoke"},
    "guard-drop-geometry-v3-diagnostic": {"actual-source-preparation", "rust-profile-smoke"},
    "guard-drop-geometry-v3-stock-diagnostic": {"actual-source-preparation", "rust-profile-smoke"},
    "actual-callee-applicability": {"actual-source-preparation"},
    "stack-address-role-controls": {"stack-address-role-control-preparation"},
    "bidirectional-len23-diagnostic": {
        "actual-source-preparation", "actual-callee-applicability",
        "bidirectional-option-stages", "bidirectional-small-source-preparation",
    },
    "hrtb-admission-certificate": {
        "callback-model-diagnostics", "prepared-hrtb-diagnostics",
    },
    "guard-construction-fragment-diagnostic": {
        "actual-source-preparation", "rust-profile-smoke",
    },
    "guard-construction-fragment-stock-diagnostic": {
        "actual-source-preparation", "rust-profile-smoke",
    },
    "guard-construction-nonprecise-v3-diagnostic": {
        "actual-source-preparation", "bidirectional-small-source-preparation",
        "rust-profile-smoke",
    },
    "guard-construction-nonprecise-v3-stock-diagnostic": {
        "actual-source-preparation", "bidirectional-small-source-preparation",
        "rust-profile-smoke",
    },
    "mir-or-join-seven-diagnostic": {
        "actual-source-preparation", "bidirectional-small-source-preparation",
    },
    "checked-current-owner-permutation": {
        "actual-source-preparation", "bidirectional-small-source-preparation",
    },
    "checked-current-owner-permutation-stock": {
        "actual-source-preparation", "bidirectional-small-source-preparation",
    },
}


def fail(message: str) -> "NoReturn":
    print(message, file=sys.stderr)
    raise SystemExit(2)


def load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        fail(f"cannot read merge selection: {error}")
    if not isinstance(value, dict) or set(value) != {
        "schema", "mode", "full_transfer", "runtime_probe", "groups"
    }:
        fail("merge selection has unknown/missing fields")
    if value["schema"] != SCHEMA:
        fail("merge selection schema mismatch")
    mode = value["mode"]
    if mode not in ("full-transfer", "targeted"):
        fail("merge selection mode must be full-transfer or targeted")
    if type(value["full_transfer"]) is not bool or value["full_transfer"] != (mode == "full-transfer"):
        fail("merge selection full_transfer flag does not match mode")
    if type(value["runtime_probe"]) is not bool:
        fail("merge selection runtime_probe must be boolean")
    groups = value["groups"]
    if (not isinstance(groups, list) or not groups or
            any(not isinstance(name, str) for name in groups) or
            groups != sorted(set(groups))):
        fail("merge selection groups must be a nonempty sorted unique string list")
    unknown = set(groups) - KNOWN_GROUPS
    if unknown:
        fail("unknown selected merge groups: " + ", ".join(sorted(unknown)))
    selected = set(groups)
    missing_smoke = {"rust-profile-smoke"} - selected
    if missing_smoke:
        fail("every selection requires rust-profile-smoke")
    for group in selected:
        missing = DEPENDENCIES.get(group, set()) - selected
        if missing:
            fail(f"selected group {group} is missing dependencies: {', '.join(sorted(missing))}")
    if mode == "full-transfer" and selected != FULL_GROUPS:
        fail("full-transfer selection must be the exact retained 37-group set")
    if mode == "full-transfer" and not value["runtime_probe"]:
        fail("full-transfer selection requires the saved runtime probe")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--selection", type=Path, required=True)
    validate.add_argument("--output", type=Path, required=True)
    contains = sub.add_parser("contains")
    contains.add_argument("--selection", type=Path, required=True)
    contains.add_argument("--sha256", required=True)
    contains.add_argument("group")
    args = parser.parse_args()
    raw = args.selection.read_bytes()
    if args.command == "contains":
        if hashlib.sha256(raw).hexdigest() != args.sha256:
            fail("merge selection changed after preflight")
        value = load(args.selection)
        if args.group == "callback-destination-frame-probe":
            return 0 if value["runtime_probe"] else 1
        if args.group not in KNOWN_GROUPS:
            fail("runner requested unknown group: " + args.group)
        return 0 if args.group in value["groups"] else 1
    value = load(args.selection)
    result = dict(value)
    result["selection_sha256"] = hashlib.sha256(raw).hexdigest()
    result["not_run_groups"] = sorted(KNOWN_GROUPS - set(value["groups"]))
    result["known_groups"] = sorted(KNOWN_GROUPS)
    result["dependencies"] = {
        name: sorted(items) for name, items in sorted(DEPENDENCIES.items())
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as error:
        print(f"merge selection validation failed: {error}", file=sys.stderr)
        sys.exit(2)
