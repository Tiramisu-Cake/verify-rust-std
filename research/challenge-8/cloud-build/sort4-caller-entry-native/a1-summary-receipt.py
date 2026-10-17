"""Bind a checked workflow gate to a single Cloud caller invocation.

This is an inert service module. Receipts carry trusted-runner reports, not
kernel proof certificates. They cannot authenticate the truth of verifier
results; the Cloud runner must establish those results before recording them.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
from typing import Mapping

PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
TARGET = "A1-FIRST-MATRIX-THRESHOLD-INTERFACE"
HASH_FIELDS = ("verified", "original", "verifier", "exporter", "schema")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z")
FOCUS = re.compile(r"verified/lib\.rs:[1-9][0-9]*\Z")
INDEX = re.compile(r"[1-9][0-9]*\Z")


class ReceiptError(ValueError):
    pass


def _require(ok: bool, why: str) -> None:
    if not ok:
        raise ReceiptError(why)


def tool_id(hashes: Mapping[str, str]) -> str:
    return hashlib.sha256((hashes["verifier"] + ":" + hashes["exporter"] +
                           ":" + hashes["schema"]).encode("ascii")).hexdigest()


def source_pair_id(hashes: Mapping[str, str]) -> str:
    return hashlib.sha256((hashes["verified"] + ":" + hashes["original"])
                          .encode("ascii")).hexdigest()


def render_receipt(gate, *, build: str, proof: str, infra: str, profile: str,
                   hashes: Mapping[str, str], caller_focus: str) -> str:
    """Render only after exact two-impl workflow admission, with pinned bytes."""
    _require(set(hashes) == set(HASH_FIELDS), "exact receipt hash inventory required")
    _require(all(isinstance(hashes[k], str) and HEX64.fullmatch(hashes[k])
                 for k in HASH_FIELDS), "full SHA256 input hashes required")
    _require(isinstance(build, str) and bool(UUID.fullmatch(build)), "Build UUID required")
    _require(bool(HEX40.fullmatch(proof)) and bool(HEX40.fullmatch(infra)),
             "full proof and infra commit pins required")
    _require(bool(HEX64.fullmatch(profile)), "profile SHA256 required")
    _require(isinstance(caller_focus, str) and bool(FOCUS.fullmatch(caller_focus)),
             "exact certified observer focus required")
    _require(gate.common_summary_available, "both actual bodies and native conformance required")
    _require(gate._build_id == build, "summary gate belongs to another Build")
    expected_pins = {"tool_id": tool_id(hashes), "profile_id": profile,
                     "proof_id": proof, "infra_id": infra, "target_id": TARGET}
    _require(dict(gate.expected_run_pins) == expected_pins, "summary tool/run pins differ")
    identities = []
    for impl in ("default16", "freeze32"):
        record = gate.implementations[impl]
        _require(record.get("source_pair_id") == source_pair_id(hashes),
                 "actual body proof used another verified/original source pair")
        row = record["compiler_identity"]
        for field in ("compiler_impl_id", "compiler_item_id"):
            value = row[field]
            _require(isinstance(value, str) and bool(INDEX.fullmatch(value)),
                     "numeric local compiler identity required")
            identities.append(value)
    _require(len(set(identities)) == 4, "compiler impl/item identities must be distinct")
    lines = ["SMALLSORT_A1_THRESHOLD_RECEIPT_V1", "build=" + build,
             "proof=" + proof, "infra=" + infra, "profile=" + profile,
             "target=" + TARGET, "caller=a1_guard_observer", "focus=" + caller_focus]
    lines += [key + "_sha256=" + hashes[key] for key in HASH_FIELDS]
    lines += [key + "=" + value for key, value in zip(
        ("default_impl", "default_item", "freeze_impl", "freeze_item"), identities)]
    lines += ["assurance=runner-reported-both-actual-bodies-and-native-conformance"]
    result = "\n".join(lines) + "\n"
    _require(len(result.encode("ascii")) <= 2048, "bounded receipt exceeded")
    return result


def write_cloud_receipt(path: Path, gate, **pins) -> None:
    """Write once in Cloud; a stale receipt cannot be overwritten silently."""
    _require(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
             os.environ.get("SORT4_A1_PHASE_ID") == PHASE,
             "exact authorized Cloud phase required")
    _require(path.name == "a1-threshold-summary.receipt" and
             str(path.resolve()).startswith("/workspace/"), "Cloud receipt destination required")
    rendered = render_receipt(gate, **pins)
    with path.open("x", encoding="ascii") as output:
        output.write(rendered)
