#!/usr/bin/env python3
"""Extract the exact SmallSort CopyOnDrop body for a hosted VeriFast gate.

Only ghost contract comments are added. Compilation, refinement checking, and
verification belong to the GitHub-hosted runner, not this extractor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_SOURCE_SHA256 = "32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959"
EXPECTED_BLOCK_SHA256 = "caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a"
EXPECTED_BLOCK_BYTES = 364
BLOCK_START = b"struct CopyOnDrop<T> {\n"
BLOCK_END = b"}\n\nfn small_sort_network"
DROP_SIGNATURE = b"    fn drop(&mut self)"
COPY_CALL = b"            ptr::copy_nonoverlapping(self.src, self.dst, self.len);"
EXPECTED_TARGET_NAME = "<CopyOnDrop<T> as core::ops::Drop>::drop"
CRATE_PREFIX = b"#![no_std]\nuse core::ptr;\n\n"

# Keep all annotations adjacent to the original signature. Removing this
# exact byte string restores the original crate byte for byte.
CONTRACT = b"""/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    (*self).src |-> ?src &*& (*self).dst |-> ?dst &*& (*self).len |-> ?len &*&
    struct_CopyOnDrop_padding(self) &*&
    [?f]src[..len] |-> ?src_values &*& dst[..len] |-> _ &*&
    foreach(src_values, own::<T>(t));
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*&
    (*self).src |-> src &*& (*self).dst |-> dst &*& (*self).len |-> len &*&
    struct_CopyOnDrop_padding(self) &*&
    [f]src[..len] |-> src_values &*& dst[..len] |-> src_values &*&
    foreach(src_values, own::<T>(t));
@*//*@ on_unwind_ens false; @*/"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract(source: Path, output: Path, evidence: Path) -> None:
    source_bytes = source.read_bytes()
    source_hash = sha256(source_bytes)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise ValueError(f"SmallSort source SHA-256 mismatch: {source_hash}")
    if source_bytes.count(BLOCK_START) != 1 or source_bytes.count(BLOCK_END) != 1:
        raise ValueError("CopyOnDrop source anchors are not unique")
    start = source_bytes.index(BLOCK_START)
    end = source_bytes.index(BLOCK_END, start) + len(b"}\n\n")
    block = source_bytes[start:end]
    if len(block) != EXPECTED_BLOCK_BYTES or sha256(block) != EXPECTED_BLOCK_SHA256:
        raise ValueError("The exact CopyOnDrop Rust block changed")
    if block.count(DROP_SIGNATURE) != 1 or block.count(COPY_CALL) != 1:
        raise ValueError("The original Drop signature or copy call is not unique")
    original = CRATE_PREFIX + block
    verified = CRATE_PREFIX + block.replace(DROP_SIGNATURE, DROP_SIGNATURE + CONTRACT)
    if verified.count(CONTRACT) != 1 or verified.replace(CONTRACT, b"") != original:
        raise ValueError("The verified crate differs by more than ghost comments")
    target_copy_call_line = verified[: verified.index(COPY_CALL)].count(b"\n") + 1

    original_path = output / "original" / "lib.rs"
    verified_path = output / "verified" / "lib.rs"
    if (output / "original").exists() or (output / "verified").exists() or evidence.exists():
        raise FileExistsError("Refusing to overwrite extraction evidence")
    original_path.parent.mkdir(parents=True, exist_ok=True)
    verified_path.parent.mkdir(parents=True, exist_ok=True)
    original_path.write_bytes(original)
    verified_path.write_bytes(verified)
    report = {
        "selection": "verifast_copy_on_drop_gate",
        "source": str(source),
        "source_sha256": source_hash,
        "block_offset": start,
        "block_bytes": len(block),
        "block_sha256": sha256(block),
        "contract_sha256": sha256(CONTRACT),
        "expected_target_name": EXPECTED_TARGET_NAME,
        "target_copy_call_line": target_copy_call_line,
        "original": str(original_path),
        "original_sha256": sha256(original),
        "verified": str(verified_path),
        "verified_sha256": sha256(verified),
        "ghost_strip_exact_bytes": True,
        "exact_destination_values": True,
        "generic_T": True,
        "arbitrary_len": True,
        "body_source_unchanged": True,
    }
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    extract(args.source, args.output, args.evidence)


if __name__ == "__main__":
    main()
