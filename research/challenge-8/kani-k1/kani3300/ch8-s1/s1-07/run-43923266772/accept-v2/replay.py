#!/usr/bin/env python3
"""Integrity replay for the stop marker; does not accept or classify evidence."""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent
d=json.loads((D/"ACCEPT.json").read_text())
for name, expected in d["read_inputs"].items():
 p=Path(name)
 actual=hashlib.sha256(p.read_bytes()).hexdigest()
 if actual != expected: raise SystemExit(f"INPUT_SHA_MISMATCH {name}: {actual}")
assert d["state"] == "STOP_INCOMPLETE"
assert not d["claims"]["historical_receipt_modified"]
print("STOP_INCOMPLETE: input identities match; no acceptance inferred")
