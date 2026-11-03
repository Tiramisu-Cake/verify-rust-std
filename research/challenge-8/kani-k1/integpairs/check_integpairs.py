#!/usr/bin/env python3
"""INTEGPAIRS static pre-build check (stdlib only; no proof tools, no network).

usage: python3 -I -B check_integpairs.py STAGE REQUEST.json   (run from the repository root)

For the stage's exact rows it checks, against the committed tree only:
  * library tree id = integrated tree a45388ac…;
  * each full name occurs exactly once in parttwotree/cfg-on-expected.txt (INV2-confirmed cfg-on inventory);
  * each row is in parttwotree/proof-matrix.tsv with the same expect; FAILED rows take their literal from the
    matrix and the literal occurs as a kani::assert description at the matrix line or within its reported span;
  * the root fn exists once in its module file, with its attribute block (proof kind, stubs, unwind);
  * the request validates with the lane's own kani_k1.validate_request and its harness list equals the stage
    rows with expect/expect_check equal to the matrix.
Prints one JSON object; exit 0 iff every check passes.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
K1 = ROOT / "research/challenge-8/kani-k1"
VERIFY = ROOT / "library/core/src/slice/sort/shared/smallsort/verify"
PREFIX = "slice::sort::shared::smallsort::verify::"
TREE = "a45388ac593c809405558ea0c27599f487b17e4e"
EXPECTED = K1 / "parttwotree/cfg-on-expected.txt"
MATRIX = K1 / "parttwotree/proof-matrix.tsv"

# (row, role, pair) in request order. Roles: leaf / consumer / control / baseline.
STAGES = {
    "g1": [
        ("network::netcomp::netcomp_leaf_u8_n9", "leaf", "netcomp-u8-n9"),
        ("network::netcomp::netcomp_composed_u8_n9", "consumer", "netcomp-u8-n9"),
        ("network::netcomp::netcomp_wrong_cmp_u8_n9", "control", "netcomp-u8-n9"),
        ("network::netcomp::netcomp_count_negative_u8_n9", "control", "netcomp-u8-n9"),
        ("network::u64nine::u64nine_leaf_u64_n9", "leaf", "u64nine-u64-n9"),
        ("network::u64nine::u64nine_composed_u64_n9", "consumer", "u64nine-u64-n9"),
        ("network::u64nine::u64nine_wrong_cmp_u64_n9", "control", "u64nine-u64-n9"),
        ("network::u64nine::u64nine_count_negative_u64_n9", "control", "u64nine-u64-n9"),
    ],
}
LITERAL_RE = re.compile(r"^'(?P<lit>[^']+)' @(?P<file>[A-Za-z0-9_]+\.rs):(?P<line>\d+)(?: \(literal :(?P<lit_line>\d+)\))?$")


def module_file(row: str) -> Path:
    parts = row.split("::")[:-1]
    return VERIFY.joinpath(*parts[:-1], parts[-1] + ".rs")


def matrix_rows() -> dict[str, dict[str, str]]:
    lines = MATRIX.read_text().splitlines()
    head = lines[0].split("\t")
    out = {}
    for line in lines[1:]:
        cells = line.split("\t")
        rec = dict(zip(head, cells))
        out[rec["root (verify::)"]] = rec
    return out


def root_block(src: list[str], fn: str) -> tuple[int, list[str]] | None:
    hits = [i for i, l in enumerate(src) if re.match(rf"^fn {re.escape(fn)}\(\)", l)]
    if len(hits) != 1:
        return None
    i = hits[0]
    attrs = []
    j = i - 1
    while j >= 0 and src[j].startswith("#["):
        attrs.insert(0, src[j].strip())
        j -= 1
    return i + 1, attrs


def main() -> int:
    stage, request_path = sys.argv[1], Path(sys.argv[2])
    rows = STAGES[stage]
    problems: list[str] = []
    tree = subprocess.run(["git", "rev-parse", "HEAD:library"], capture_output=True, text=True, check=True).stdout.strip()
    if tree != TREE:
        problems.append(f"library tree {tree} != {TREE}")
    expected = EXPECTED.read_text().splitlines()
    matrix = matrix_rows()
    report = []
    for row, role, pair in rows:
        rec: dict[str, object] = {"row": row, "role": role, "pair": pair}
        full = PREFIX + row
        n = expected.count(full)
        rec["inventory_count"] = n
        if n != 1:
            problems.append(f"{row}: cfg-on-expected count {n}")
        m = matrix.get(row)
        if m is None:
            problems.append(f"{row}: not in proof-matrix.tsv")
            report.append(rec)
            continue
        rec.update(matrix_class=m["class"], expect=m["expect"], covers=m["covers"])
        path = module_file(row)
        src = path.read_text().splitlines()
        rec["file"] = str(path.relative_to(ROOT))
        blk = root_block(src, row.split("::")[-1])
        if blk is None:
            problems.append(f"{row}: root fn not found exactly once in {path.name}")
        else:
            rec["fn_line"], rec["attrs"] = blk
            unwind = [a for a in blk[1] if a.startswith("#[kani::unwind(")]
            rec["unwind"] = unwind[0][len("#[kani::unwind("):-2] if len(unwind) == 1 else None
            if rec["unwind"] is None:
                problems.append(f"{row}: no single #[kani::unwind]")
        if m["expect"] == "FAILED":
            lm = LITERAL_RE.match(m["sole failure literal"])
            if not lm or lm.group("file") != path.name:
                problems.append(f"{row}: matrix literal unparsed or other file: {m['sole failure literal']!r}")
            else:
                lit, line = lm.group("lit"), int(lm.group("line"))
                lit_line = int(lm.group("lit_line") or line)
                rec.update(expect_check=lit, reported_line=line, literal_line=lit_line)
                if f'"{lit}"' not in src[lit_line - 1]:
                    problems.append(f"{row}: literal not at {path.name}:{lit_line}")
                if "kani::assert(" not in src[line - 1]:
                    problems.append(f"{row}: no kani::assert at reported line {path.name}:{line}")
                rec["literal_occurrences_in_file"] = sum(f'"{lit}"' in l for l in src)
        elif m["sole failure literal"] != "-":
            problems.append(f"{row}: SUCCESS row has a literal in the matrix")
        report.append(rec)

    # Request: lane validator + exact row/expect equality.
    sys.path.insert(0, str(K1 / "tools"))
    import kani_k1  # noqa: E402  (the lane's own validator)
    raw = request_path.read_bytes()
    req = json.loads(raw)
    try:
        kani_k1.validate_request(req, max_total_minutes=kani_k1.MAX_TOTAL_MINUTES)
        valid = True
    except kani_k1.RequestError as exc:
        valid = False
        problems.append(f"request invalid: {exc}")
    want = []
    for rec in report:
        e = {"name": PREFIX + rec["row"], "expect": rec.get("expect")}
        if rec.get("expect") == "FAILED":
            e["expect_check"] = rec.get("expect_check")
        want.append(e)
    if req.get("harnesses") != want:
        problems.append("request harnesses != stage rows/expectations (order included)")
    profile = {k: req.get(k) for k in ("agent", "runner", "kind", "harness_timeout_minutes", "kani_jobs",
                                         "uninit_checks", "controls")}
    want_profile = {"agent": "k1-merge", "runner": "gcb-e2-standard-4", "kind": "measurement",
                    "harness_timeout_minutes": 10, "kani_jobs": 1, "uninit_checks": False, "controls": True}
    if profile != want_profile:
        problems.append(f"request profile {profile} != {want_profile}")
    if not str(req.get("request_id", "")).startswith("integpairs-"):
        problems.append("request_id must start with integpairs-")
    minutes = len(req.get("harnesses", [])) * req.get("harness_timeout_minutes", 0) + 30
    out = {
        "stage": stage,
        "ok": not problems,
        "problems": problems,
        "library_tree": tree,
        "expected_sha256": hashlib.sha256(EXPECTED.read_bytes()).hexdigest(),
        "matrix_sha256": hashlib.sha256(MATRIX.read_bytes()).hexdigest(),
        "request": str(request_path),
        "request_sha256": hashlib.sha256(raw).hexdigest(),
        "request_valid": valid,
        "reserve_minutes": minutes,
        "reserve_usd": round(minutes * 0.0135, 4),
        "rows": report,
    }
    print(json.dumps(out, indent=1))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
