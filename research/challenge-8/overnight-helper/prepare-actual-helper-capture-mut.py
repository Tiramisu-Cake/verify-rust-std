#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""P2 source route: the exact actual helper fixture at ``T = *mut Element``.

This is a separate fixture writer; the reviewed ``*const Element`` preparer is
loaded by its pinned SHA-256 and never modified. Only the three fixture
signature types change; the std runtime body, its source certificate and the
contract text are reused byte-for-byte. It grants no translator admission,
helper proof or summary: mutable-pointer gates and pins are separate work.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


CONST_PREPARER_SHA256 = "2c5ce72fb643c96f3e9cf57eda0e8f206b584a9a060ee6398c4e2ff1aeb3e7be"
CONST_SIGNATURE = (
    b"pub fn select_unpredictable<Element>(\n"
    b"    condition: bool,\n    true_val: *const Element,\n"
    b"    false_val: *const Element,\n) -> *const Element\n"
)
MUT_SIGNATURE = (
    b"pub fn select_unpredictable<Element>(\n"
    b"    condition: bool,\n    true_val: *mut Element,\n"
    b"    false_val: *mut Element,\n) -> *mut Element\n"
)
SPECIALIZATION = "T = *mut Element; Element unrestricted"


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_const():
    path = Path(__file__).with_name("prepare-actual-helper-capture.py")
    require(path.is_file() and digest(path.read_bytes()) == CONST_PREPARER_SHA256,
            "pinned const helper preparer differs")
    spec = importlib.util.spec_from_file_location("p2_const_helper_capture", path)
    require(spec is not None and spec.loader is not None,
            "const helper preparer spec unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_pair(repo: Path) -> tuple[bytes, bytes, dict]:
    """Return the mutable original/verified pair and its certificate."""
    const = load_const()
    body, source = const.source_certificate(repo)
    # The const pair comes from the reviewed writer itself, so the mutable
    # pair differs from it only in the three signature types.
    with tempfile.TemporaryDirectory() as scratch:
        const_record = const.write_fixture(repo, Path(scratch) / "const")
        const_verified = (Path(scratch) / "const/verified/lib.rs").read_bytes()
    require(digest(const_verified) == const_record["verified_sha256"],
            "const fixture record differs from its bytes")
    contract_start = const_verified.index(b"/*@\nreq ")
    contract = const_verified[contract_start:const_verified.index(body)]
    require(const_verified.count(CONST_SIGNATURE) == 1 and
            body.count(b"*const") == 0 and
            body.count(b"*mut") == body.count(b"inner: *mut T,") == 1,
            "const fixture signature or generic runtime body changed")
    verified = const_verified.replace(CONST_SIGNATURE, MUT_SIGNATURE, 1)
    original = const.strip_ghost(verified)
    require(const.strip_ghost(const_verified).replace(
        CONST_SIGNATURE, MUT_SIGNATURE, 1) == original,
            "mutable pair differs from const pair outside the signature")
    require(original.count(body) == verified.count(body) == 1 and
            original.count(b"crate::mem::forget(guard);") == 1 and
            original.count(b"*const") == 0 and original.count(b"*mut Element") == 3,
            "actual mutable source pair changed")
    record = {
        "source_certificate": dict(source, target_specialization=SPECIALIZATION),
        "const_preparer_sha256": CONST_PREPARER_SHA256,
        "const_verified_sha256": digest(const_verified),
        "original_sha256": digest(original),
        "verified_sha256": digest(verified),
        "ghost_strip_identity": const.strip_ghost(verified) == original,
        "contract_text_sha256": digest(contract),
        "capture_only": True,
        "translator_admission": "NOT_IMPLEMENTED",
        "helper_proof_status": "NOT_RUN",
    }
    require(record["ghost_strip_identity"], "ghost stripping changed runtime body")
    return original, verified, record


def write_fixture(repo: Path, out: Path) -> dict:
    original, verified, record = build_pair(repo)
    require(not out.exists(), f"refusing to overwrite {out}")
    (out / "original").mkdir(parents=True)
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    (out / "fixture.json").write_text(json.dumps(record, indent=2,
                                                  sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_fixture(args.repo, args.out), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
