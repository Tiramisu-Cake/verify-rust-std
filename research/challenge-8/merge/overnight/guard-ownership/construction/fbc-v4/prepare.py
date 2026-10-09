#!/usr/bin/env python3
"""Prepare the isolated exact-constructor canonical FBC roundtrip V4."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "guard_constructor_v3b_preparation_for_fbc", HERE.parent / "nonprecise-v3/prepare.py")
if spec is None or spec.loader is None:
    raise RuntimeError("pinned V3b constructor preparer unavailable")
V3 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = V3
spec.loader.exec_module(V3)
P, B, V2 = V3.P, V3.B, V3.V2
PROFILE = "copy-on-drop-source-construction-canonical-fbc-fragment-v4"
OWN = V3.OWN
CONSTRUCTOR_CONTRACT = V3.CONSTRUCTOR_CONTRACT
FBC_CLOSE = b"        //@ close CopyOnDrop_full_borrow_content::<T>(t, &drop_guard)();\n"
FBC_OPEN = b"        //@ open CopyOnDrop_full_borrow_content::<T>(t, &drop_guard)();\n"
ROUNDTRIP = V3.ROUNDTRIP.replace(
    b"        //@ close <CopyOnDrop<T>>.own(t, drop_guard);\n",
    b"        //@ close <CopyOnDrop<T>>.own(t, drop_guard);\n" + FBC_CLOSE + FBC_OPEN,
    1)
if ROUNDTRIP == V3.ROUNDTRIP or ROUNDTRIP.count(FBC_CLOSE) != 1 or \
        ROUNDTRIP.count(FBC_OPEN) != 1:
    raise RuntimeError("V4 FBC insertion must add exactly one close/open pair")


def sha(data: bytes) -> str:
    return P.sha(data)


def extract(source: Path, output: Path, report_path: Path) -> dict:
    # Reuse V3b's exact source/struct/entry/normal/unwind extraction and then
    # add only the two ghost FBC statements before the existing own reopen.
    report = V3.extract(source, output, report_path)
    if (report["profile"] != V3.PROFILE or
            report["exact_own_sha256"] != sha(OWN) or
            report["constructor_contract_sha256"] != sha(CONSTRUCTOR_CONTRACT) or
            report["roundtrip_sha256"] != sha(V3.ROUNDTRIP)):
        raise RuntimeError("V3b source/own/contract roundtrip identity differs")
    for name, row in report["cases"].items():
        case = output / name
        verified_path = case / "verified/lib.rs"
        original = (case / "original/lib.rs").read_bytes()
        prior = verified_path.read_bytes()
        if prior.count(V3.ROUNDTRIP) != 1:
            raise RuntimeError(f"{name}: V3b roundtrip not unique")
        verified = prior.replace(V3.ROUNDTRIP, ROUNDTRIP, 1)
        stripped = (verified.replace(OWN, b"", 1)
                    .replace(CONSTRUCTOR_CONTRACT, b"", 1)
                    .replace(ROUNDTRIP, b"", 1))
        if name == "first_body_false":
            stripped = stripped.replace(V3.CONSTRUCTOR_FALSE, b"", 1)
            row["intended_failure"]["line"] = V3.line_at(verified, V3.CONSTRUCTOR_FALSE)
        if stripped != original:
            raise RuntimeError(f"{name}: FBC roundtrip changed runtime source")
        verified_path.write_bytes(verified)
        row["verified_sha256"] = sha(verified)
        row["fbc_close_line"] = V3.line_at(verified, FBC_CLOSE)
        row["fbc_open_line"] = V3.line_at(verified, FBC_OPEN)
        row["fbc_roundtrip_sha256"] = sha(ROUNDTRIP)
        row["runtime_source_identical_after_ghost_strip"] = True
    report.update({"profile": PROFILE,
                   "parent_v3b_profile": V3.PROFILE,
                   "parent_v3b_roundtrip_sha256": sha(V3.ROUNDTRIP),
                   "roundtrip_sha256": sha(ROUNDTRIP),
                   "fbc_close_sha256": sha(FBC_CLOSE),
                   "fbc_open_sha256": sha(FBC_OPEN),
                   "fbc_roundtrip_sha256": sha(ROUNDTRIP),
                   "canonical_fbc_packaging_only": True,
                   "no_drop_impl_in_fragment": True,
                   "accepted": False})
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    extract(args.source, args.output, args.report)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit(f"V4 canonical FBC preparation refused: {error}")
