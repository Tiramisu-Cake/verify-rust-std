#!/usr/bin/env python3
"""Static consistency checker for the SmallSort audit package (audit-2026-11-03).

Python standard library + local Git only. No network, no cargo/rustc/Kani, no proofs.
Run from a clone of https://github.com/Tiramisu-Cake/verify-rust-std that has fetched all
branches (see README.md, "Reproducing the static checks"):

    python3 -B research/challenge-8/audit-2026-11-03/check_audit_report.py

What it checks (all lexical or Git-object level):
  * TSV schemas, unique keys and the declared counts of each harness set;
  * name-set equality of the harness table against the published expected-name files;
  * that every commit/tree identifier exists locally, has the declared object type, and that
    each declared library tree equals `git rev-parse <commit>:library`;
  * that every `path:line` declaration exists at its pinned commit (and, for harness rows, that the
    line contains the harness identifier as a token);
  * that every GitHub blob/tree URL in the package uses a full 40-hex commit (no branch names) and
    that the path/line exists at that commit;
  * relative links inside the package, absence of local filesystem paths, and listed known statuses.

It does NOT establish AST/MIR binding, callee identity, proof results, CI results or public
availability of URLs (the last one is a separate online check described in README.md).
"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG_FILES = ["README.md", "snapshots.tsv", "harnesses.tsv", "claims.tsv", "findings.tsv", "resources.tsv",
             "check_audit_report.py"]
VERIFY = "library/core/src/slice/sort/shared/smallsort/verify/"
PREFIX = "slice::sort::shared::smallsort::verify::"
FORK = "https://github.com/Tiramisu-Cake/verify-rust-std"
UPSTREAM = "https://github.com/model-checking/verify-rust-std"

# Target pins of the report (not the documentation HEAD).
P1_V6 = ("d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097", "d4ec476a7a001363e58f19948c188a9c2078e370")
INTEGRATED = ("2756f0e2a6ae0956fdb427574eda39b5b9a76e64", "a45388ac593c809405558ea0c27599f487b17e4e")
SPLIT31_LIB = ("b2a13747dae7458dd825f78a1d32e2ffed0b568b", "05eb97eaef01dc4015e659d46256b2d910750d58")
U64_LIB = ("a6010df7b451da55d4227ad5960b0c93992f10f0", "514c6f841cf2af3b27f6d9aa8f27c86e24c562af")
PART2_FAST = ("2104e7a596fabb058a99c8bcdf0e3f487d9a7753", "d4ec476a7a001363e58f19948c188a9c2078e370")
# Published expected-name files (commit, path).
ORDINARY_EXPECTED = ("4f4034527d3e3a26e4cd94e12ba6922e2b5e80e4", "research/challenge-8/kani-k1/macsplit/ordinary-expected.txt")
CFGON_EXPECTED = ("28d79f25282c448e83a399aa42826db895816d1b", "research/challenge-8/kani-k1/parttwotree/cfg-on-expected.txt")
ADDED_EXPECTED = ("28d79f25282c448e83a399aa42826db895816d1b", "research/challenge-8/kani-k1/parttwotree/opt-in-added-expected.txt")
PFC_INVENTORY = ("94ae47268d3957e1077c43313c82dabcaf606855", "research/challenge-8/kani-k1/domains/pfc-inventory.tsv")
SNAPSHOT_COMMIT = {"P1-V6": P1_V6[0], "INTEGRATED": INTEGRATED[0], "SPLIT31": SPLIT31_LIB[0],
                   "U64-TEN-CALLER": U64_LIB[0], "PART2-FAST": PART2_FAST[0]}

HEADERS = {
    "snapshots.tsv": ["snapshot", "role", "commit", "library_tree", "source_url", "evidence_url", "inventory_status",
                      "proof_status", "ci_status", "note"],
    "harnesses.tsv": ["snapshot", "name", "cfg", "class", "expected", "family", "domain", "source", "result_ref", "note"],
    "claims.tsv": ["claim_id", "snapshot_or_lineage", "library_commit", "library_tree", "kind", "property", "T", "F", "CMP",
                   "domain", "route", "leaf", "consumer", "status", "assurance", "build", "result_url", "code", "note"],
    "findings.tsv": ["id", "neutral_issue", "baseline_status_v4", "baseline_link_v4", "current_status_p1_v6",
                     "research_status_other_trees", "current_links", "remaining_scope"],
    "resources.tsv": ["source", "row", "build", "profile", "vt_s", "vt_status", "cbmc_rss", "driver_rss", "compiler_rss",
                      "process_sum_rss", "unit", "note"],
}
EXPECTED_COUNTS = {
    ("P1-V6", "ordinary"): 202,
    ("P1-V6", "controls"): 182,
    ("INTEGRATED", "controls"): 54,
    ("SPLIT31", "controls"): 3,
    ("U64-TEN-CALLER", "controls"): 4,
    ("PART2-FAST", "controls"): 8,
}
EXPECTED_CLASSES = {
    ("P1-V6", "ordinary-pfc"): 36, ("P1-V6", "ordinary-plain"): 166,
    ("P1-V6", "positive-candidate"): 131, ("P1-V6", "intended-negative"): 34,
    ("P1-V6", "diagnostic"): 10, ("P1-V6", "service-positive"): 7,
}
FINDING_IDS = [f"F{i:02d}" for i in range(1, 12)] + ["A1", "A2", "A3", "A4"]
KNOWN_STATUS = {  # (table, key, field) -> required substring
    ("snapshots.tsv", "INTEGRATED", "proof_status"): "NOT_RUN",
    ("snapshots.tsv", "INV2-RESULT", "inventory_status"): "438",
    ("snapshots.tsv", "INV2-RESULT", "proof_status"): "NOT_RUN",
    ("snapshots.tsv", "PARTTWO-TREE-RESULT", "inventory_status"): "NOT OBTAINED",
    ("snapshots.tsv", "U64-TEN-CALLER", "proof_status"): "PARTIAL",
    ("claims.tsv", "INTEG-MATRIX", "status"): "NOT_RUN",
    ("claims.tsv", "INV2", "assurance"): "no proof credit",
    ("claims.tsv", "U1", "status"): "UNKNOWN",
    ("claims.tsv", "CASE5", "assurance"): "OPEN",
    ("claims.tsv", "N10", "assurance"): "cross-Build",
    ("claims.tsv", "N22c", "assurance"): "cross-Build",
    ("findings.tsv", "A4", "current_status_p1_v6"): "not a proof obligation",
}

errors: list[str] = []
notes: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def git(*args: str, check: bool = True) -> str:
    r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout if r.returncode == 0 else ""


def obj_type(oid: str) -> str:
    return git("cat-file", "-t", oid, check=False).strip()


_blob_cache: dict[tuple[str, str], list[str] | None] = {}


def blob_lines(commit: str, path: str) -> list[str] | None:
    key = (commit, path)
    if key not in _blob_cache:
        r = subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{path}"], capture_output=True)
        _blob_cache[key] = r.stdout.decode("utf-8", "replace").split("\n") if r.returncode == 0 else None
    return _blob_cache[key]


def path_kind(commit: str, path: str) -> str:
    return git("cat-file", "-t", f"{commit}:{path}", check=False).strip()


def read_tsv(name: str) -> list[dict[str, str]]:
    with open(HERE / name, newline="") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    if not rows or rows[0] != HEADERS[name]:
        err(f"{name}: header mismatch: {rows[0] if rows else None}")
        return []
    out = []
    for i, r in enumerate(rows[1:], 2):
        if len(r) != len(HEADERS[name]):
            err(f"{name}:{i}: {len(r)} fields, expected {len(HEADERS[name])}")
            continue
        out.append(dict(zip(HEADERS[name], r)))
    return out


def check_commit_tree(where: str, commit: str, tree: str) -> None:
    if obj_type(commit) != "commit":
        err(f"{where}: {commit} is not a local commit object (type {obj_type(commit) or 'missing'})")
        return
    if tree:
        if obj_type(tree) != "tree":
            err(f"{where}: {tree} is not a tree object")
        actual = git("rev-parse", f"{commit}:library", check=False).strip()
        if actual != tree:
            err(f"{where}: library tree of {commit} is {actual}, declared {tree}")


URL_RE = re.compile(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/[^\s)<>\"'|`]+")


def check_url(where: str, url: str, counters: Counter) -> None:
    url = url.rstrip(".,;")
    m = re.match(r"https://github\.com/([^/]+/[^/]+)/(blob|tree)/([^/#]+)/?([^#]*)(?:#L(\d+)(?:-L(\d+))?)?$", url)
    if not m:
        if re.match(r"https://github\.com/[^/]+/[^/]+/(blob|tree)/", url):
            err(f"{where}: unparsable source URL {url}")
        counters["external_unchecked"] += 1
        return
    repo, kind, ref, path, l1, l2 = m.groups()
    if repo not in ("Tiramisu-Cake/verify-rust-std", "model-checking/verify-rust-std"):
        counters["external_unchecked"] += 1
        return
    if not re.fullmatch(r"[0-9a-f]{40}", ref):
        err(f"{where}: URL ref is not a full commit SHA: {url}")
        return
    if obj_type(ref) != "commit":
        err(f"{where}: URL commit {ref} not present locally as a commit (tree IDs are not valid in blob URLs)")
        return
    counters["pinned_urls"] += 1
    if path:
        k = path_kind(ref, path)
        if kind == "blob" and k != "blob":
            err(f"{where}: {path} is not a file at {ref[:12]}")
            return
        if kind == "tree" and k not in ("tree", "blob"):
            err(f"{where}: {path} missing at {ref[:12]}")
            return
        if l1:
            lines = blob_lines(ref, path) or []
            hi = int(l2 or l1)
            if not (1 <= int(l1) <= hi <= len(lines)):
                err(f"{where}: line {l1}{'-' + l2 if l2 else ''} outside {path}@{ref[:12]} ({len(lines)} lines)")
            else:
                counters["line_anchored_urls"] += 1


def name_set(commit: str, path: str) -> list[str]:
    lines = blob_lines(commit, path)
    if lines is None:
        err(f"expected-name file {path}@{commit[:12]} not found")
        return []
    return [l.strip() for l in lines if l.strip()]


def main() -> int:
    counters: Counter = Counter()
    for f in PKG_FILES:
        if not (HERE / f).is_file():
            err(f"package file missing: {f}")
    tables = {n: read_tsv(n) for n in HEADERS}

    # --- documentation HEAD vs target pins -------------------------------------------------
    head = git("rev-parse", "HEAD").strip()
    head_lib = git("rev-parse", "HEAD:library", check=False).strip()
    notes.append(f"docs HEAD {head}, its library tree {head_lib or 'n/a'}")
    if head_lib == INTEGRATED[1]:
        notes.append("docs HEAD library tree = INTEGRATED research candidate (not the Part 1 v6 tree); expected")
    elif head_lib == P1_V6[1]:
        notes.append("docs HEAD library tree = Part 1 v6 tree")
    else:
        notes.append("docs HEAD library tree differs from both target pins; targets are checked by commit, not HEAD")
    for where, (c, t) in {"P1-V6": P1_V6, "INTEGRATED": INTEGRATED, "SPLIT31": SPLIT31_LIB,
                          "U64-TEN-CALLER": U64_LIB, "PART2-FAST": PART2_FAST}.items():
        check_commit_tree(f"pin {where}", c, t)

    # --- snapshots ---------------------------------------------------------------------------
    snaps = tables["snapshots.tsv"]
    ids = [s["snapshot"] for s in snaps]
    for k, v in Counter(ids).items():
        if v > 1:
            err(f"snapshots.tsv: duplicate snapshot {k}")
    for s in snaps:
        tree = s["library_tree"] if s["snapshot"] not in ("UPSTREAM-BASE",) else ""
        check_commit_tree(f"snapshots.tsv {s['snapshot']}", s["commit"], tree)
    counters["snapshots"] = len(snaps)

    # --- harnesses ---------------------------------------------------------------------------
    hs = tables["harnesses.tsv"]
    keys = Counter((h["snapshot"], h["name"]) for h in hs)
    for k, v in keys.items():
        if v > 1:
            err(f"harnesses.tsv: duplicate row {k}")
    cnt = Counter((h["snapshot"], h["cfg"]) for h in hs)
    for k, want in EXPECTED_COUNTS.items():
        if cnt.get(k, 0) != want:
            err(f"harnesses.tsv: {k} has {cnt.get(k, 0)} rows, expected {want}")
    cls = Counter((h["snapshot"], h["class"]) for h in hs)
    for k, want in EXPECTED_CLASSES.items():
        if cls.get(k, 0) != want:
            err(f"harnesses.tsv: class {k} has {cls.get(k, 0)}, expected {want}")
    integ_groups = Counter(h["class"].split(" ")[0] for h in hs if h["snapshot"] == "INTEGRATED")
    if dict(integ_groups) != {"A-success-gate": 27, "B-expected-failed": 17, "C-open-or-diagnostic": 10}:
        err(f"harnesses.tsv: INTEGRATED groups {dict(integ_groups)} != A27/B17/C10 (+ ordinary leaf = A28)")
    full = lambda h: h["name"].replace("verify::", PREFIX, 1)
    v6_ord = sorted(full(h) for h in hs if h["snapshot"] == "P1-V6" and h["cfg"] == "ordinary")
    v6_all = sorted(full(h) for h in hs if h["snapshot"] == "P1-V6")
    integ = sorted(full(h) for h in hs if h["snapshot"] == "INTEGRATED")
    if v6_ord != sorted(name_set(*ORDINARY_EXPECTED)):
        err("harnesses.tsv: P1-V6 ordinary names != published ordinary-expected (202)")
    if sorted(v6_all + integ) != sorted(name_set(*CFGON_EXPECTED)):
        err("harnesses.tsv: P1-V6 (384) + INTEGRATED (54) names != published cfg-on-expected (438)")
    if integ != sorted(name_set(*ADDED_EXPECTED)):
        err("harnesses.tsv: INTEGRATED names != published opt-in-added-expected (54)")
    # PFC rows of P1-V6 vs the public PFC inventory (ordinary entries only)
    inv = blob_lines(*PFC_INVENTORY) or []
    inv_rows = [l.split("\t") for l in inv[1:] if l.strip()]
    inv_ord = {r[0] for r in inv_rows if len(r) > 5 and r[5].strip() == "ordinary"}
    if len(inv_ord) != 36:
        err(f"domains/pfc-inventory.tsv: {len(inv_ord)} ordinary entries, expected 36")
    pfc_names = {h["name"].split("::")[-1] for h in hs if h["snapshot"] == "P1-V6" and h["class"] == "ordinary-pfc"}
    inv_short = {n.split("::")[-1] for n in inv_ord}
    if inv_short and inv_short != pfc_names:
        err(f"harnesses.tsv: ordinary PFC names differ from domains/pfc-inventory.tsv ({len(pfc_names)} vs {len(inv_short)})")
    it_pfc = sum(1 for h in hs if h["snapshot"] == "P1-V6" and h["class"] == "ordinary-pfc"
                 and "insert_tail" in h["name"])
    if it_pfc != 5:
        err(f"harnesses.tsv: ordinary insert_tail PFC rows {it_pfc}, expected 5")
    # source declarations
    for h in hs:
        commit = SNAPSHOT_COMMIT[h["snapshot"]]
        path, _, line = h["source"].rpartition(":")
        if not path.startswith(VERIFY) or not line.isdigit():
            err(f"harnesses.tsv: bad source {h['source']}")
            continue
        lines = blob_lines(commit, path)
        if lines is None or not (1 <= int(line) <= len(lines)):
            err(f"harnesses.tsv: {h['name']}: {h['source']} not present at {commit[:12]}")
            continue
        tok = h["name"].split("::")[-1]
        if not re.search(r"\b" + re.escape(tok) + r"\b", lines[int(line) - 1]):
            err(f"harnesses.tsv: {h['name']}: identifier not on {h['source']}@{commit[:12]}")
        else:
            counters["harness_lines_lexically_bound"] += 1
    counters["harness_rows"] = len(hs)

    # --- claims ------------------------------------------------------------------------------
    cl = tables["claims.tsv"]
    for k, v in Counter(c["claim_id"] for c in cl).items():
        if v > 1:
            err(f"claims.tsv: duplicate claim {k}")
    for c in cl:
        check_commit_tree(f"claims.tsv {c['claim_id']}", c["library_commit"], c["library_tree"])
        for loc in c["code"].split():
            if loc == "-" or loc.startswith("https://"):
                continue
            path, _, line = loc.rpartition(":")
            p = path if path.startswith("library/") else VERIFY + path
            lines = blob_lines(c["library_commit"], p)
            if lines is None or not line.isdigit() or not (1 <= int(line) <= len(lines)):
                err(f"claims.tsv {c['claim_id']}: {loc} not present at {c['library_commit'][:12]}")
            else:
                counters["claim_code_lines"] += 1
        if c["leaf"] not in ("-", "") and "Build" not in c["leaf"] and c["assurance"].startswith("bounded composition"):
            err(f"claims.tsv {c['claim_id']}: composition without stated leaf Build provenance")
        if "composition" in c["assurance"] and "same Build" not in c["assurance"] and "cross-Build" not in c["assurance"]:
            err(f"claims.tsv {c['claim_id']}: composition assurance must say same Build or cross-Build")
    counters["claims"] = len(cl)

    # --- findings ----------------------------------------------------------------------------
    fi = tables["findings.tsv"]
    if [f["id"] for f in fi] != FINDING_IDS:
        err(f"findings.tsv: ids {[f['id'] for f in fi]} != {FINDING_IDS}")
    counters["findings"] = len(fi)

    # --- resources ---------------------------------------------------------------------------
    rs = tables["resources.tsv"]
    for r in rs:
        if "timeout" in r["vt_status"].lower() and r["vt_status"].upper().startswith("SUCCESS"):
            err(f"resources.tsv: timeout row marked SUCCESS: {r['row']}")
        if r["vt_status"].lower().startswith("timeout") and "cap" not in r["vt_status"].lower():
            err(f"resources.tsv: timeout must be labelled as a cap, not a VT: {r['row']}")
        if r["vt_s"] == "":
            err(f"resources.tsv: empty VT field (use UNKNOWN): {r['row']}")
    counters["resource_rows"] = len(rs)

    # --- known statuses ----------------------------------------------------------------------
    idx = {"snapshots.tsv": ("snapshot", snaps), "claims.tsv": ("claim_id", cl), "findings.tsv": ("id", fi)}
    for (table, key, field), want in KNOWN_STATUS.items():
        kf, rows = idx[table]
        row = next((r for r in rows if r[kf] == key), None)
        if row is None or want not in row[field]:
            err(f"{table} {key}.{field}: expected to contain {want!r}")
        else:
            counters["known_statuses"] += 1
    fast = next((s for s in snaps if s["snapshot"] == "PART2-FAST"), None)
    fast_result = path_kind(PART2_FAST[0], "research/challenge-8/kani-k1/RESULT-PART2-FAST.md")
    if fast and fast_result != "blob" and "PENDING" not in fast["proof_status"]:
        err("snapshots.tsv PART2-FAST: no RESULT at the recorded commit, status must be PENDING")
    if fast and fast_result == "blob" and ("PENDING" in fast["proof_status"] or "8/8" not in fast["proof_status"]):
        err("snapshots.tsv PART2-FAST: RESULT is published at the recorded commit; status must state its 8/8 outcome")
    if fast and fast_result == "blob" and any("PENDING" in h["result_ref"] for h in hs if h["snapshot"] == "PART2-FAST"):
        err("harnesses.tsv PART2-FAST: rows still PENDING although the RESULT is published")

    # --- URLs, relative links, private paths -------------------------------------------------
    for f in PKG_FILES:
        p = HERE / f
        if not p.is_file():
            continue
        text = p.read_text()
        if f != "check_audit_report.py":
            if re.search(r"(?<![\w.])/(root|tmp|home)/", text):
                err(f"{f}: contains a local filesystem path")
            for url in URL_RE.findall(text):
                check_url(f, url, counters)
        if f == "README.md":
            for m in re.finditer(r"\]\(([^)]+)\)", text):
                target = m.group(1)
                if target.startswith(("http://", "https://", "#")):
                    continue
                if not (HERE / target.split("#")[0]).exists():
                    err(f"README.md: relative link {target} does not resolve inside the package")
                else:
                    counters["relative_links"] += 1

    print("check_audit_report.py: static checks only (lexical / Git object level); no AST/MIR binding, no proof, no CI result.")
    for n in notes:
        print("note:", n)
    for k in sorted(counters):
        print(f"{k}: {counters[k]}")
    if errors:
        print(f"FAIL: {len(errors)} problem(s)")
        for e in errors:
            print("  -", e)
        return 1
    print("PASS")
    return 0


def repo_root() -> Path:
    r = subprocess.run(["git", "-C", str(HERE), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("not inside a Git checkout")
    return Path(r.stdout.strip())


REPO = repo_root()
if __name__ == "__main__":
    sys.exit(main())
