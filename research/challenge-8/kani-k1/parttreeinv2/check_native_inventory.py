#!/usr/bin/env python3
"""Validate saved bounded k1g inventory pages against the frozen request and exact set.

Copied from parttwotree/check_native_inventory.py (sha256 b1830b85...); PARTTREE-INV2 differences: expected and
added manifests are read from the pinned parttwotree/ files and their SHA-256 are asserted; set comparison is
by sorted unique names; names_sha256 is checked in the artifact's own page order.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
KANI = "9461e07af7ec929f050aa4192f29363c9be07779"
EXPECTED_SHA256 = "da9bcae231b35b1c42d2873976879c1209a688cc03bc25a3421f5fea7b578f1b"
ADDED_SHA256 = "ac8c1c4a0509480dae614c36471e32a84b6b7ae93c8b9d081a2c02d1ae474230"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def main(label):
    manifest = json.loads((HERE / "runs.json").read_text())
    run = next(row for row in manifest["builds"] if row["label"].lower() == label)
    request_bytes = (HERE / f"{label}.request.json").read_bytes()
    request = json.loads(request_bytes)
    expected_file = HERE.parent / "parttwotree/cfg-on-expected.txt"   # pinned PARTTWO-TREE manifest
    assert hashlib.sha256(expected_file.read_bytes()).hexdigest() == EXPECTED_SHA256
    added_file = HERE.parent / "parttwotree/opt-in-added-expected.txt"
    assert hashlib.sha256(added_file.read_bytes()).hexdigest() == ADDED_SHA256
    expected = expected_file.read_text().splitlines()
    identity = {"request_id": run["request_id"],
                "request_sha256": hashlib.sha256(request_bytes).hexdigest(),
                "build_id": run["uuid"], "head_sha": run["head_sha"], "kani_commit": KANI}
    assert git("show", f"{run['head_sha']}:research/challenge-8/kani-k1/RUN-REQUEST.json") == request_bytes
    assert git("rev-parse", f"{run['head_sha']}:library").decode().strip() == manifest["library_tree"]
    assert request["controls"] == run["controls"] and request["kind"] == "inventory"
    pages = sorted(HERE.glob(f"{label}.inventory-page-*.txt"),
                   key=lambda p: int(p.stem.rsplit("-", 1)[1]))
    assert pages, "no saved inventory pages"
    names, offset, bound = [], 0, None
    for page in pages:
        fields, rows = {}, []
        for line in page.read_text().splitlines():
            if line.startswith("slice::"):
                rows.append(line)
            elif "=" in line:
                key, value = line.split("=", 1)
                assert key not in fields, (page, key)
                fields[key] = value
            else:
                raise AssertionError((page, "unrecognized line", line))
        assert all(fields.get(k) == v for k, v in identity.items()), page
        assert int(fields["total"]) == run["expected_count"]
        assert int(fields["offset"]) == offset == int(page.stem.rsplit("-", 1)[1])
        assert int(fields["count"]) == len(rows) and 0 < len(rows) <= 80
        current_bound = {k: fields[k] for k in (*identity, "total", "inventory_sha256", "names_sha256")}
        if bound is None:
            bound = current_bound
        assert current_bound == bound, "page identities differ"
        names.extend(rows)
        offset += len(rows)
        next_offset = str(offset) if offset < int(fields["total"]) else "done"
        assert fields["next_offset"] == next_offset
    assert fields["next_offset"] == "done", "incomplete pagination"
    assert len(names) == run["expected_count"] == len(expected)
    assert len(set(names)) == len(names) and len(set(expected)) == len(expected)
    assert hashlib.sha256(("\n".join(names) + "\n").encode()).hexdigest() == bound["names_sha256"]
    missing, extra = sorted(set(expected) - set(names)), sorted(set(names) - set(expected))
    ordinary = set((HERE.parent / "macsplit/ordinary-expected.txt").read_text().splitlines())
    added = set(added_file.read_text().splitlines())
    split = {"native_ordinary_members": len(ordinary & set(names)), "native_added_members": len(added & set(names)),
             "ordinary_missing": sorted(ordinary - set(names)), "added_missing": sorted(added - set(names))}
    report = {"ok": not missing and not extra and not split["ordinary_missing"] and not split["added_missing"],
              **bound, **split, "library_tree": manifest["library_tree"],
              "controls": run["controls"], "expected_file": str(expected_file.relative_to(ROOT)),
              "expected_sha256": hashlib.sha256(expected_file.read_bytes()).hexdigest(),
              "pages": [p.name for p in pages], "missing": missing, "extra": extra,
              "duplicates": [], "scope": "native compilation and exact inventory; no proofs"}
    (HERE / f"{label}.inventory-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    assert len(sys.argv) == 2 and sys.argv[1] == "g1"
    raise SystemExit(main(sys.argv[1]))
