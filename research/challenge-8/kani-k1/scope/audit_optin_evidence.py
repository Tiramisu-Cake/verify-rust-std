#!/usr/bin/env python3
"""Reconcile extended-positive names with bounded PASS evidence and source drift.

This is a bounded source-level transfer audit, not a proof rerun. It intentionally
reads only committed Rust blobs and compact P-6/C3a/C3c summaries and row tables.
The helper closure is identifier-based and does not expand Rust macros as a compiler does.
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from collections import defaultdict
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
P6 = "6cfc76cb211d088aebaff8a449bcac953e97f942"
C3A_PASS = "8003d40abe12b3cfdc48729f060fd0a3214e6be6"
HEAD = "9be5499c459e3157be0d86dc366b2eccd1e911c8"
LIB = "library/core/src/slice/sort/shared/smallsort/verify"
EXTENDED = BASE / "extended-positive.txt"
SCOPE = BASE / "scope.tsv"
C3C_ROWS = ROOT / "research/challenge-8/kani-k1/c3c/evidence"
C3A_REPORT = BASE / "RESULT-C3A-source.md"
OUT = BASE / "optin-evidence.tsv"
SUMMARY = BASE / "optin-evidence-summary.md"


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def blob(rev: str, path: str) -> str | None:
    p = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                       text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return p.stdout if p.returncode == 0 else None


def source_parser():
    sys.path.insert(0, str(BASE))
    import source_items
    return source_items


SI = source_parser()


def git_paths(rev: str) -> list[str]:
    nested = git("ls-tree", "-r", "--name-only", rev, "--", LIB).splitlines()
    root_module = LIB + ".rs"
    return sorted(set(nested + ([root_module] if blob(rev, root_module) is not None else [])))


def clean_rust(text: str) -> str:
    """Remove comments and cfg attributes while retaining literals and code."""
    out, i, state, depth = [], 0, "code", 0
    while i < len(text):
        c, n = text[i], text[i + 1] if i + 1 < len(text) else ""
        if state == "code":
            if c == '"': state = "string"; out.append(c); i += 1
            elif c == "/" and n == "/": state = "line"; out.extend("  "); i += 2
            elif c == "/" and n == "*": state = "block"; depth = 1; out.extend("  "); i += 2
            else: out.append(c); i += 1
        elif state == "string":
            out.append(c); i += 1
            if c == "\\" and i < len(text): out.append(text[i]); i += 1
            elif c == '"': state = "code"
        elif state == "line":
            if c == "\n": out.append(c); state = "code"
            else: out.append(" ")
            i += 1
        else:
            if c == "/" and n == "*": depth += 1; out.extend("  "); i += 2
            elif c == "*" and n == "/": depth -= 1; out.extend("  "); i += 2; state = "code" if depth == 0 else "block"
            else: out.append("\n" if c == "\n" else " "); i += 1
    text = "".join(out)
    text = re.sub(r"(?m)^\s*#\[cfg\s*\(.*?\)\]\s*\n?", "", text)
    return text


def item_key(item: dict, raw: str) -> tuple[str, str]:
    if item["kind"] == "call":
        m = re.match(r"\s*(\w+)\s*!\s*\(\s*(\w+)", raw)
        if m: return "call", m[1] + ":" + m[2]
    return item["kind"], item["name"]


def other_symbols(body: str) -> list[str]:
    text = clean_rust(body)
    m = re.match(r"\s*(?:(?:pub)(?:\([^)]*\))?\s+)*(?:unsafe\s+|default\s+)*(const|static|type|struct|enum|union|trait)\s+(\w+)", text)
    if m:
        return [m[2]]
    if re.match(r"\s*(?:unsafe\s+)?impl\b", text):
        head = text.split("{", 1)[0]
        # Link a trait implementation to both its trait and self type. This lets
        # method bodies inside the impl participate when either name is called.
        m = re.search(r"\b([A-Z][A-Za-z0-9_]*)\s+for\s+([A-Z][A-Za-z0-9_]*)", head)
        if m: return [m[1], m[2]]
        m = re.search(r"\bimpl\s*(?:<[^>]*>\s*)?([A-Z][A-Za-z0-9_]*)", head)
        if m: return [m[1]]
    return []


def indexed_source(rev: str):
    """Load top-level definitions and import paths from the verification tree."""
    nodes, defs, imports = {}, defaultdict(list), defaultdict(list)
    texts = {}
    for path in git_paths(rev):
        raw = blob(rev, path)
        if raw is None: continue
        texts[path] = raw
        for it in SI.items(raw):
            body = raw[it["content"]:it["end"]]
            key = (path, *item_key(it, body))
            nodes[key] = (raw, it, body)
            if it["kind"] in ("fn", "macro"):
                attrs = clean_rust(raw[it["start"]:it["content"]])
                if it["kind"] == "fn" and re.search(r"kani\s*::\s*proof(?:_for_contract)?\b", attrs):
                    continue
                defs[it["name"]].append(key)
            elif it["kind"] == "other":
                for symbol in other_symbols(body):
                    defs[symbol].append(key)
            elif it["kind"] == "use":
                imports[path].extend(SI.imports(it["body"]))
    return nodes, defs, imports, texts


IDENT_RE = re.compile(r"\b[A-Za-z_]\w*")


def refs(body: str) -> set[str]:
    clean = clean_rust(body)
    result = set()
    for match in IDENT_RE.finditer(clean):
        name, pos = match[0], match.end()
        while pos < len(clean) and clean[pos].isspace(): pos += 1
        if clean.startswith("!", pos):
            pos += 1
            while pos < len(clean) and clean[pos].isspace(): pos += 1
        elif clean.startswith("::", pos):
            pos += 2
            while pos < len(clean) and clean[pos].isspace(): pos += 1
            if pos >= len(clean) or clean[pos] != "<":
                continue
            depth, pos = 1, pos + 1
            while pos < len(clean) and depth:
                if clean[pos] == "<": depth += 1
                elif clean[pos] == ">": depth -= 1
                pos += 1
            if depth: continue
            while pos < len(clean) and clean[pos].isspace(): pos += 1
        if pos < len(clean) and clean[pos] == "(": result.add(name)
    return result


def local_import_targets(path: str, imports: list[str]) -> dict[str, set[str]]:
    result = defaultdict(set)
    for entry in imports:
        imported, _, alias = entry.partition(" as ")
        leaf = alias or imported.rsplit("::", 1)[-1]
        # Only imports from sibling verification modules are resolved here.
        match = re.search(r"(?:^|::)(correct|merge|network|assembly|comparators|smoke|types|mutations)::(\w+)$", imported)
        if match:
            result[leaf].add((LIB + "/" + match[1] + ".rs", match[2]))
    return result


def find_harness(name: str, indexed) -> tuple[str, tuple[str, dict, str]] | None:
    nodes, _, _, _ = indexed
    short = name.rsplit("::", 1)[-1]
    for key, value in nodes.items():
        raw, it, body = value
        if it["kind"] == "call" and re.search(r"\b" + re.escape(short) + r"\b", body):
            return key[0], value
        if it["kind"] == "fn" and it["name"] == short:
            return key[0], value
    return None


def closure(harness: tuple[str, tuple[str, dict, str]] | None, indexed) -> set[tuple[str, str, str]]:
    if harness is None: return set()
    nodes, defs, imports, _ = indexed
    path, value = harness
    raw, it, body = value
    start = (path, *item_key(it, body))
    visited, queue = set(), [start]
    while queue:
        key = queue.pop()
        if key in visited or key not in nodes: continue
        visited.add(key)
        source, item, text = nodes[key]
        import_map = local_import_targets(key[0], imports.get(key[0], []))
        ref_names = refs(text)
        tokens = {m[0] for m in IDENT_RE.finditer(clean_rust(text))}
        clean_body = clean_rust(text)
        for ref in ref_names | tokens:
            candidates = defs.get(ref, [])
            same_file = [c for c in candidates if c[0] == key[0]]
            if same_file: queue.extend(same_file)
            for target_path, target_name in import_map.get(ref, set()):
                queue.extend(c for c in defs.get(target_name, []) if c[0] == target_path)
            # Resolve a qualified sibling-module call even when it is not imported.
            if not same_file and ref not in import_map:
                for candidate in candidates:
                    module = candidate[0].rsplit("/", 1)[-1].removesuffix(".rs")
                    if (candidate[0] == LIB + ".rs" and candidate[1] == "macro"):
                        # macro_rules! in verify.rs is lexically visible to child modules.
                        queue.append(candidate)
                    if re.search(r"\b(?:super|self)::(?:\w+::)*" + re.escape(module) + r"::" + re.escape(ref) + r"\b", clean_body):
                        queue.append(candidate)
    return visited


def source_audit(name: str, rev: str, cache: dict) -> tuple[bool, str]:
    """Compare this harness and its statically called verification helpers only."""
    key = (rev, HEAD)
    if key not in cache:
        cache[key] = (indexed_source(rev), indexed_source(HEAD))
    old, new = cache[key]
    old_h, new_h = find_harness(name, old), find_harness(name, new)
    if old_h is None or new_h is None:
        return False, "harness source item absent at evidence SHA or target"
    old_closure, new_closure = closure(old_h, old), closure(new_h, new)
    if old_closure != new_closure:
        missing = len(old_closure ^ new_closure)
        return False, f"helper dependency set changed ({missing} source items)"
    old_nodes, _, old_imports, _ = old
    new_nodes, _, new_imports, _ = new
    for node in old_closure:
        if node not in old_nodes or node not in new_nodes:
            return False, f"called helper added/removed: {node[1]}:{node[2]}"
        old_raw, old_item, old_body = old_nodes[node]
        new_raw, new_item, new_body = new_nodes[node]
        old_attrs = clean_rust(old_raw[old_item["start"]:old_item["content"]])
        new_attrs = clean_rust(new_raw[new_item["start"]:new_item["content"]])
        if old_attrs != new_attrs:
            return False, f"harness/helper attributes changed: {node[1]}:{node[2]}"
        if clean_rust(old_body) != clean_rust(new_body):
            return False, f"harness/helper body changed: {node[1]}:{node[2]}"
        if sorted(old_imports.get(node[0], [])) != sorted(new_imports.get(node[0], [])):
            return False, f"imported names changed in {node[1]}"
    # Production files are unchanged across this revision and target; prove that
    # all library changes are within verify/ before accepting the source transfer.
    changed = git("diff", "--name-only", rev, HEAD, "--", "library").splitlines()
    if any(not p.startswith(LIB) for p in changed):
        return False, "production/library code changed outside verify/"
    return True, "harness body and resolved helper bodies unchanged"


def main() -> None:
    head = git("rev-parse", HEAD).strip()
    if head != HEAD:
        raise SystemExit(f"expected worktree target {HEAD}, got {head}")
    scope = {r["name"]: r for r in csv.DictReader(SCOPE.open(), delimiter="\t")}
    p6_names = {n for n, r in scope.items() if r.get("proof_sha") == P6}
    # Load only compact GCB result fragments and their matching status metadata.
    # Distinct runs are ordered by finishTime; within a run, later row fragments
    # supersede earlier snapshots for the same harness.
    gcb_passes = defaultdict(list)
    status_files = sorted(C3C_ROWS.glob("*.status.json"))
    for status_path in status_files:
        stem = status_path.name.removesuffix(".status.json")
        status = json.loads(status_path.read_text())
        run_rows = {}
        for rows_path in sorted(C3C_ROWS.glob(stem + ".*.rows.tsv")):
            for line in rows_path.read_text().splitlines():
                if not line.startswith("slice::sort::shared::smallsort::"):
                    continue
                cols = line.split("\t")
                run_rows[cols[0]] = (cols[1], rows_path.name)
        for harness, (result, rows_name) in run_rows.items():
            if result != "SUCCESS":
                continue
            finished = status.get("finishTime", "")
            sha = status.get("source_sha", "")
            build_id = status.get("id", "")
            if not sha or not build_id or not finished:
                continue
            source = f"GCB C3c {stem}; build {build_id}; finished {finished}; {rows_name}"
            gcb_passes[harness].append((finished, sha, source))
    for entries in gcb_passes.values():
        entries.sort(key=lambda row: row[0], reverse=True)
    # Exact C3a positive PASS evidence in RESULT-C3A: the grouped Drop case.
    c3a_name = "slice::sort::shared::smallsort::verify::types::sorted_permutation_traits_general_drop_u8_n7_to9"
    c3a_pass = c3a_name in EXTENDED.read_text().splitlines()
    c3a_pass &= "SUCCESS | 349.6911" in C3A_REPORT.read_text()
    source_cache = {}
    rows = []
    for name in (n.strip() for n in EXTENDED.read_text().splitlines() if n.strip()):
        candidates = [(sha, source) for _, sha, source in gcb_passes.get(name, [])]
        if name == c3a_name and c3a_pass:
            candidates.append((C3A_PASS, "RESULT-C3A; build 2f10637a; exact grouped Drop N7..9"))
        if name in p6_names:
            candidates.append((P6, "P-6 Actions run 40748125754; 8/8 partitions"))
        latest_sha, latest_source = candidates[0] if candidates else ("NO_EVIDENCE", "NO_EVIDENCE")
        selected_sha, selected_source = "NO_EVIDENCE", "NO_EVIDENCE"
        transfer, why = "NO_EVIDENCE", "no exact PASS result in bounded P-6/C3A/C3C sources"
        rejected = []
        for sha, source in candidates:
            ok, note = source_audit(name, sha, source_cache)
            if ok:
                selected_sha, selected_source = sha, source
                transfer = "PASS"
                why = ("; ".join(rejected) + "; " if rejected else "") + note
                break
            rejected.append(f"{source.split(';')[0]} not transferable: {note}")
        historical = "PASS" if candidates else "NO_EVIDENCE"
        if candidates and transfer == "NO_EVIDENCE":
            why = "no suitable source identity; " + "; ".join(rejected)
        rows.append({"harness": name, "historical_result": historical,
                     "last_historical_sha": latest_sha, "last_historical_source": latest_source,
                     "selected_sha": selected_sha, "selected_source": selected_source,
                     "transfer": transfer, "audit_note": why})
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    counts = Counter(r["historical_result"] for r in rows)
    transfers = Counter(r["transfer"] for r in rows)
    sources = Counter(r["selected_source"].split(";")[0] for r in rows if r["transfer"] == "PASS")
    latest_sources = Counter(r["last_historical_source"].split(";")[0]
                             for r in rows if r["historical_result"] == "PASS")
    text = ["# Opt-in evidence audit", "", f"Target library SHA: `{HEAD}`.",
            f"Evidence scope: {len(rows)} extended-positive harnesses; historical PASS {counts['PASS']}, no exact PASS evidence {counts['NO_EVIDENCE']}.",
            f"Transfer result after per-harness source audit: PASS {transfers['PASS']}, NO_EVIDENCE {transfers['NO_EVIDENCE']}.",
            "", "This is a source-level transfer audit, not a new Kani run. Each harness source item and its identifier-resolved verification helper call closure are compared independently; this bounded Python analysis does not expand macros as rustc does. cfg attributes, comments, and import regrouping are normalized. Production/library files outside verify/ are also checked for changes.",
            "", "Selected transferable PASS evidence source counts:"]
    text += [f"- {src}: {count}" for src, count in sources.items()]
    text += ["", "Latest historical PASS source counts:"]
    text += [f"- {src}: {count}" for src, count in latest_sources.items()]
    text += ["", "All bounded GCB `*.rows.tsv` fragments were reconciled with their matching `*.status.json` source SHA, finish time, and build ID; rows are considered newest-first. GCB evidence is selected only when that harness's source and helper closure match the target; otherwise the audit falls back to an earlier suitable PASS such as P-6. Rows without a suitable matching PASS remain NO_EVIDENCE; timeout, missing result, neighboring length, and negative control are not PASS.",
             "", "Reproduce with `python3 research/challenge-8/kani-k1/scope/audit_optin_evidence.py`."]
    SUMMARY.write_text("\n".join(text) + "\n")
    print(f"{OUT}: historical PASS {counts['PASS']}, no evidence {counts['NO_EVIDENCE']}; transferable {transfers['PASS']}")


if __name__ == "__main__":
    main()
