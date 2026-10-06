#!/usr/bin/env python3
"""Add a transparent tuple-2 ownership model to a disposable Actions install.

The pinned VeriFast binary is unchanged. This deliberately changes its bundled
Rust spec only for the explicitly selected tuple_overlay experiment.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path


BASE_SHA256 = "d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5"
ANCHOR = (
    "pred<T1, T2> <(T1, T2)>.share(k, t, l) = "
    "<T1>.share(k, t, &(*l).0) &*& <T2>.share(k, t, &(*l).1);\n"
)
MODEL_INSERT = """pred_ctor challenge8_tuple2_own<T1, T2>()(t: thread_id_t, v: (T1, T2)) =
    <T1>.own(t, v.0) &*& <T2>.own(t, v.1);

type_pred_def for<T1, T2> <(T1, T2)>.own = challenge8_tuple2_own::<T1, T2>;

"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: patch-verifast-tuple-model.py PRELUDE_RSSPEC EVIDENCE_DIR")
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted"
        or os.environ.get("RUNNER_OS") != "Linux"
        or os.environ.get("VFVERSION") != "26.09"
    ):
        raise SystemExit("tuple model overlay runs only on pinned GitHub-hosted Linux Actions")

    prelude = Path(sys.argv[1])
    evidence = Path(sys.argv[2])
    source = prelude.read_bytes()
    source_sha = sha256(source)
    if source_sha != BASE_SHA256:
        raise SystemExit(
            f"bundled prelude differs from pinned tag 26.09: {source_sha}; expected {BASE_SHA256}"
        )
    anchor = ANCHOR.encode("utf-8")
    insertion = MODEL_INSERT.encode("utf-8")
    if source.count(anchor) != 1 or insertion in source:
        raise SystemExit("tuple model anchor is missing, duplicated, or already patched")
    patched = source.replace(anchor, insertion + anchor, 1)
    if patched.count(insertion) != 1 or patched.replace(insertion, b"", 1) != source:
        raise SystemExit("tuple model patch does not round-trip exactly")

    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "prelude-original.rsspec").write_bytes(source)
    (evidence / "prelude-tuple-overlay.rsspec").write_bytes(patched)
    (evidence / "model-overlay.json").write_text(
        json.dumps(
            {
                "model": "transparent tuple-2 field ownership",
                "tool_version": os.environ["VFVERSION"],
                "installed_spec": str(prelude),
                "original_sha256": source_sha,
                "patched_sha256": sha256(patched),
                "insertion_sha256": sha256(insertion),
                "insertion_bytes": len(insertion),
                "exact_round_trip": True,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    prelude.write_bytes(patched)
    if prelude.read_bytes() != patched:
        raise SystemExit("installed prelude does not match recorded overlay")
    print(f"Applied tuple-2 model overlay: {source_sha} -> {sha256(patched)}")
    print(f"Insertion SHA-256: {sha256(insertion)}")


if __name__ == "__main__":
    main()
