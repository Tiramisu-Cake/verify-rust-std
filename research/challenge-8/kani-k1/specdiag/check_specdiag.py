#!/usr/bin/env python3
"""Static checks of the SPECDIAG package: requests vs manifest, source shape, scope, projection.

Read-only: runs git and the lane's own request validator; never builds or verifies anything.
Usage: python3 -I check_specdiag.py [--run-request g1|g2] [--out FILE]
"""
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
K1 = "research/challenge-8/kani-k1"
S = "library/core/src/slice/sort/shared/smallsort"
SMALLSORT, MERGE, SPECDIAG = f"{S}.rs", f"{S}/verify/merge.rs", f"{S}/verify/merge/specdiag.rs"
TASK_COMMIT = "fb022288146366e1afa2747ab75be674d79fc34b"
NS = "slice::sort::shared::smallsort::verify::merge::specdiag::"
PFC_PREFIX = "crate::slice::sort::shared::smallsort::"
MODULE_DECL = "#[cfg(kani_smallsort_controls)]\nmod specdiag;\n\n"
G2_ENTRIES = [6, 8, 10, 11, 15, 16, 17, 18]
LIB_ALLOWED = {MERGE, SPECDIAG}
RESEARCH_ALLOWED_PREFIX = f"{K1}/specdiag/"
RESEARCH_ALLOWED = {f"{K1}/RESULT-SPECDIAG.md", f"{K1}/RUN-REQUEST.json"}


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout


def git_bytes(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True).stdout


def norm(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return re.sub(r"\(\s+", "(", re.sub(r"\s+\)", ")", text))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-request", choices=["g1", "g2"])
    ap.add_argument("--out")
    a = ap.parse_args()
    errors: list[str] = []
    spec = importlib.util.spec_from_file_location("kani_k1", ROOT / K1 / "tools/kani_k1.py")
    kani_k1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kani_k1)

    manifest = json.loads((HERE / "manifest.json").read_text())
    entries = manifest["entries"]
    if [e["index"] for e in entries] != list(range(1, 21)):
        errors.append("manifest must list entries 1..20 in order")
    if [e["index"] for e in entries if e["g2"]] != G2_ENTRIES or manifest["g2"]["entries"] != G2_ENTRIES:
        errors.append(f"G2 selection must be exactly {G2_ENTRIES}")
    if manifest["g1"]["entries"] != list(range(1, 21)):
        errors.append("G1 selection must be exactly entries 1..20")

    def expected_request(sel: list[int]) -> list[dict]:
        return [{k: e[k] for k in ("name", "expect", "expect_check") if k in e} for e in entries if e["index"] in sel]

    req_sha = {}
    for tag, sel, uninit in (("g1", list(range(1, 21)), False), ("g2", G2_ENTRIES, True)):
        path = HERE / f"{tag}.request.json"
        raw = path.read_bytes()
        req_sha[tag] = hashlib.sha256(raw).hexdigest()
        req = json.loads(raw)
        try:
            kani_k1.validate_request(req, max_total_minutes=720)
        except kani_k1.RequestError as exc:
            errors.append(f"{tag}: lane validator rejects: {exc}")
        want = {"kind": "diagnostic", "runner": "gcb-e2-standard-4", "controls": True, "kani_jobs": 1,
                "uninit_checks": uninit, "harness_timeout_minutes": 3}
        for k, v in want.items():
            if req.get(k) != v:
                errors.append(f"{tag}: {k} must be {v!r}, got {req.get(k)!r}")
        if set(req) - kani_k1.REQUEST_KEYS - {"kani_jobs", "uninit_checks", "controls"}:
            errors.append(f"{tag}: unexpected request keys")
        if req["harnesses"] != expected_request(sel):
            errors.append(f"{tag}: harness list differs from manifest selection")
    envelope = {t: (len(json.loads((HERE / f"{t}.request.json").read_text())["harnesses"]) * 3 + 30)
                for t in ("g1", "g2")}
    usd = {t: round(m * 0.0135, 4) for t, m in envelope.items()}
    if envelope != {"g1": 90, "g2": 54} or round(usd["g1"] + usd["g2"], 4) > 2.0:
        errors.append(f"envelope differs from the task: {envelope} {usd}")

    src = (ROOT / SPECDIAG).read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        if len(line) > 100:
            errors.append(f"{SPECDIAG}:{i} longer than 100 columns")
        if re.search(r"\b(debug_)?assert(_eq|_ne)?!\s*\(", line):
            errors.append(f"{SPECDIAG}:{i} uses a core assert macro (placeholder description on the pin)")
        if len(re.findall(r"kani::assert\(", line)) > 1:
            errors.append(f"{SPECDIAG}:{i} more than one assertion on a source line")
    messages = re.findall(r'kani::(assert|cover)\((?:[^;]|\n)*?"(specdiag [^"]+)"', src)
    seen: dict[str, int] = {}
    for _, msg in messages:
        seen[msg] = seen.get(msg, 0) + 1
    dup = sorted(m for m, c in seen.items() if c > 1)
    if dup:
        errors.append(f"duplicate literal messages: {dup}")
    n_assert, n_cover = src.count("kani::assert("), src.count("kani::cover(")
    if len(messages) != n_assert + n_cover:
        errors.append(f"{n_assert + n_cover} assert/cover calls but {len(messages)} 'specdiag ...' literal messages")

    proofs = re.findall(r"#\[kani::(proof|proof_for_contract\(([^)]*)\))\]\n(?:#\[kani::unwind\(\d+\)\]\n)?fn (\w+)\(\)", src)
    found = {name: (kind, target) for kind, target, name in proofs}
    if len(re.findall(r"#\[kani::proof", src)) != len(proofs):
        errors.append("a proof attribute is not directly followed by its harness fn")
    names = [e["name"].removeprefix(NS) for e in entries]
    if sorted(found) != sorted(names):
        errors.append(f"harness set differs: extra {sorted(set(found) - set(names))} missing {sorted(set(names) - set(found))}")
    for e in entries:
        short = e["name"].removeprefix(NS)
        if short not in found:
            continue
        kind, target = found[short]
        if e["mode"].startswith("PFC "):
            want = PFC_PREFIX + e["mode"].split()[1]
            if not kind.startswith("proof_for_contract") or target != want:
                errors.append(f"{short}: must be proof_for_contract({want}), is {kind}")
        elif kind != "proof":
            errors.append(f"{short}: plain entry must be #[kani::proof]")
        if e["expect"] == "FAILED" and e["expect_check"].startswith("specdiag ") and e["expect_check"] not in seen:
            errors.append(f"{short}: observer expect_check is not a literal message in the source")
        if (e["expect"] == "FAILED") != ("expect_check" in e):
            errors.append(f"{short}: expect_check present iff FAILED")

    base_ss = git("show", f"{TASK_COMMIT}:{SMALLSORT}").splitlines()
    for line_no, needle in ((683, "is_sorted(dst, 4, &is_less)"), (600, "is_sorted(begin"),
                            (844, "is_sorted_unrolled(dst")):
        clause = norm(" ".join(base_ss[line_no - 1:line_no + 4]))
        if not clause.startswith("#[cfg_attr(kani, kani::ensures(") or needle not in clause:
            errors.append(f"{SMALLSORT}:{line_no} ensures clause does not contain {needle!r}")
    cand = (ROOT / MERGE).read_text().splitlines()
    if ("eq &= *a.add(i) == *b.add(i);" not in cand[69]
            or "let x = ptr::read_unaligned(a.add(8 * $j) as *const u64);" not in cand[50]):
        errors.append(f"candidate {MERGE}:70/51 are not the probe byte/word reads named in the manifest")

    changed = [l.split("\t") for l in git("diff", "--name-status", TASK_COMMIT).splitlines()]
    changed += [["A", p] for p in git("ls-files", "--others", "--exclude-standard").splitlines()]
    scope_bad = []
    for status, path in changed:
        if path.startswith("library/"):
            if path not in LIB_ALLOWED:
                scope_bad.append(path)
        elif not (path.startswith(RESEARCH_ALLOWED_PREFIX) or path in RESEARCH_ALLOWED):
            scope_bad.append(path)
        if path.startswith(f"{RESEARCH_ALLOWED_PREFIX}pin-src/"):
            scope_bad.append(path + " (pin copy must not be committed)")
    if scope_bad:
        errors.append(f"outside write scope: {scope_bad}")
    head_merge = (ROOT / MERGE).read_bytes().decode()
    base_merge = git_bytes("show", f"{TASK_COMMIT}:{MERGE}").decode()
    projected = head_merge.replace(MODULE_DECL, "", 1)
    if head_merge.count(MODULE_DECL) != 1 or projected != base_merge:
        errors.append("merge.rs minus the cfg-off module declaration is not byte-identical to the base")
    other_lib = [p for _, p in changed if p.startswith("library/") and p not in LIB_ALLOWED]
    lib_tree_base = git("rev-parse", f"{TASK_COMMIT}:library").strip()

    if a.run_request:
        run = (ROOT / K1 / "RUN-REQUEST.json").read_bytes()
        if run != (HERE / f"{a.run_request}.request.json").read_bytes():
            errors.append(f"RUN-REQUEST.json differs from {a.run_request}.request.json")

    report = {
        "status": "PASS" if not errors else "FAIL", "errors": errors,
        "task_commit": TASK_COMMIT, "base_library_tree": lib_tree_base,
        "head": git("rev-parse", "HEAD").strip(), "worktree_clean": git("status", "--porcelain") == "",
        "specdiag_rs_sha256": hashlib.sha256((ROOT / SPECDIAG).read_bytes()).hexdigest(),
        "merge_rs_sha256": hashlib.sha256((ROOT / MERGE).read_bytes()).hexdigest(),
        "request_sha256": req_sha, "envelope_minutes": envelope, "envelope_usd": usd,
        "harnesses": len(found), "kani_assert": n_assert, "kani_cover": n_cover,
        "other_library_changes": other_lib, "projection_byte_identical": projected == base_merge,
    }
    text = json.dumps(report, indent=1) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    sys.stdout.write(text)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
