#!/usr/bin/env python3
"""PARTTWO-TREE static checks: source map, v6 preservation, expected root manifest.

Read-only Git/source analysis. No cargo/rustc/Kani. The name sets are a source-level forecast
(cleanup/source_inventory.py parser); native membership is established only by the inventory Build.
Run from anywhere: python3 -B research/challenge-8/kani-k1/parttwotree/check_parttwotree.py
"""
from __future__ import annotations

import difflib
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
K1 = HERE.parent
LIB = "library/core/src/slice/sort/shared/smallsort"
VER = f"{LIB}/verify"
PREFIX = "slice::sort::shared::smallsort::verify::"

V6_COMMIT = "d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097"
V6_TREE = "d4ec476a7a001363e58f19948c188a9c2078e370"
BRANCH_BASE = "4f4034527d3e3a26e4cd94e12ba6922e2b5e80e4"   # MACSPLIT head, coordinator clarification
MACSPLIT_REPORT = "71d18696613bdd6b00648a0d7b44d1cd3c6da940"
V5_LIB = "dd0f293f00c032d9fc69b74419a304dbb92d1108"          # base of L-W and L-N
V4_LIB = "9dcf313fb4"                                         # base of L-M (pre-CLEANUP)

# Frozen inputs from the task table (report tip, library commit).
LINES = {
    "bridge": dict(report="8cbb26750012c51d99266fa9fbe342519345649d",
                   library="77cb4c97733d24c1f03f11dc803a2a7676bfc4d5",
                   prerequisites=["b07dc219a27af35e9832335c129bb8759926b7ca"]),
    "wone": dict(report="b21be6cd8639ba779b9badea989abe3a3e4a2c91",
                 library="4231462d124b8c69bfaa55dd0eb956717308f1be",
                 prerequisites=["e4f1df6a348fe67277250f84e5a6aa83638a7892",
                                "af8b0db75a78f737772c8fe86ed7d5cdff109e11"]),
    "netten": dict(report="61cfba69c3dac0b87324d2845c1164e08222d0a6",
                   library="2ebda13e1445186f53a12b69a4419aafe4f17e1b",
                   prerequisites=["f4d3775dc505ef26e30158cfa7e78f120cd3c30e",
                                  "23ba8cfddbce1cf0313ab402fd6376d157a0f845"]),
    "u64": dict(report="4b9d56c46d1be97ba981610fb0dea77e0c864f66",
                library="497077c6cd14fdbcc439807c0cdc186860cb00ce",
                prerequisites=["9ab925b1578b9102e3009c0ec940c5c9cc0280cb",
                               "fddf308321046a8cd8f5526622a5e2353d79830e"]),
    "n18": dict(report="e3a778017a0e057b34d6ea910fcca9d21f7dc3a3",
                library="248b2725c6cd528a6d87aa5928e362dc11e74522",
                prerequisites=["7d8b21728b1ccb632d67374918bd13d2c45de116",
                               "97a252bea7ee68720b097ecf83d014e0b87d5f20",
                               "4eb7e81259f843da6517a8de97c68e23b584eb76",
                               "91d4d9f77a5a6e7f27b151839e6ac42114523a89",
                               "813a03db4a0ae11fbe8e00418b17556ae5171758"]),
}
NETCOMP_BASE = "f4d3775dc505ef26e30158cfa7e78f120cd3c30e"     # NETCOMP2 library, common to L-N

# New files: byte-identical copies of the pinned source blob.
COPIED = {
    f"{VER}/bridge.rs": "bridge",
    f"{VER}/wrap/wone.rs": "wone",
    f"{VER}/network/netcomp/netten.rs": "netten",
    f"{VER}/network/netcomp/netten/caller.rs": "netten",
    f"{VER}/network/netcomp/neteighteen.rs": "n18",
    f"{VER}/network/netcomp/mergestep.rs": "n18",
    f"{VER}/network/netcomp/mergestep/directfour.rs": "n18",
    f"{VER}/network/u64nine.rs": "u64",
    f"{VER}/network/u64nine/uthirteen.rs": "u64",
}
NETCOMP = f"{VER}/network/netcomp.rs"
NETTEN_BLOCK = ("\n// NETTEN: opt-in child with matching u8 N10 leaves; it reuses the private items above.\n"
                "mod netten;\n")
N18_BLOCK = ("\n// NET18-LEAVES geometry fixtures: opt-in child module after all targets and roots above.\n"
             "mod neteighteen;\n"
             "\n// MERGESTEP step summaries and actual merge4 calibration: opt-in child module after all above.\n"
             "mod mergestep;\n")
# Parent edits relative to v6: exactly these inserted lines, nothing removed.
PARENT_EDITS = {
    f"{LIB}/verify.rs": ["", "#[cfg(kani_smallsort_controls)]", "mod bridge;"],
    f"{VER}/network.rs": ["", "#[cfg(kani_smallsort_controls)]", "mod netcomp;",
                          "", "#[cfg(kani_smallsort_controls)]", "mod u64nine;"],
    f"{VER}/wrap.rs": ["", "#[cfg(kani_smallsort_controls)]", "mod wone;"],
}
TRANSFERRED_MODULES = ("bridge::", "wrap::wone::", "network::netcomp::", "network::u64nine::")
RETIRED = ("network::dispatch_safety_stable_unstable_bytes17_n32",
           "network::insert_tail_contract_u64_start1_tail13_to16")
V6_SPLIT = ("network::dispatch_safety_stable_bytes17_n32", "network::dispatch_safety_unstable_bytes17_n32",
            "network::insert_tail_contract_u64_start1_tail13_to14",
            "network::insert_tail_contract_u64_start1_tail15_to16")
# Lineage roots intentionally not transferred (outside the task's file scope; see SOURCE-MAP.md).
NOT_TRANSFERRED = ("network::netnine_full_value_count_u8_n9", "network::netnine_full_value_count_u8_n9_negative",
                   "network::netthirteen_full_value_count_u8_n13",
                   "network::netthirteen_full_value_count_u8_n13_negative")

spec = importlib.util.spec_from_file_location("k1_source_inventory", K1 / "cleanup/source_inventory.py")
si = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(si)


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(REPO), *args])


def blob(commit: str, path: str) -> bytes:
    return git("show", f"{commit}:{path}")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rev(spec_: str) -> str:
    return git("rev-parse", spec_).decode().strip()


def export(commit: str, dest: Path) -> Path:
    data = git("archive", "--format=tar", commit, LIB, f"{LIB}.rs")
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(dest, filter="data")
    return dest


ATTR_PATTERNS = {
    "proof_for_contract": re.compile(r"proof_for_contract\s*\(\s*([^)]*?)\s*\)"),
    "unwind": re.compile(r"kani\s*::\s*unwind\s*\(\s*([^)]*?)\s*\)"),
    "stub": re.compile(r"kani\s*::\s*stub\s*\(\s*([^)]*?)\s*\)"),
    "stub_verified": re.compile(r"kani\s*::\s*stub_verified\s*\(\s*([^)]*?)\s*\)"),
    "solver": re.compile(r"kani\s*::\s*solver\s*\(\s*([^)]*?)\s*\)"),
    "should_panic": re.compile(r"kani\s*::\s*should_panic"),
}


def annotations(attrs: str) -> dict:
    flat = re.sub(r"\s+", " ", attrs)
    out = {}
    for key, pattern in ATTR_PATTERNS.items():
        found = [m.group(1) if m.groups() else True for m in pattern.finditer(flat)]
        if found:
            out[key] = found
    out["kind"] = "pfc" if "proof_for_contract" in out else "plain"
    return out


INNER_CONTROLS = re.compile(r"\A\s*(?:#!\[[^]]*\]\s*)*#!\[\s*cfg\s*\(\s*kani_smallsort_controls\s*\)\s*\]")


def macro_emitter_attrs(path: Path, text: str, inherited) -> dict[str, str]:
    """Name -> attribute text of the emitter that produced it (cleanup parser, per emitter)."""
    masked = si.predict.mask_comments_strings(text)
    spans, macros = si.macro_proofs(text, masked)
    outside = si.predict.blank_spans(masked, spans)
    out = {}
    for call in re.finditer(r"\b([A-Za-z_]\w*)\s*!\s*\(", outside):
        if call.group(1) not in macros:
            continue
        paren = outside.find("(", call.start(), call.end())
        args = si.predict.split_args(outside[paren + 1:si.predict.matching(outside, paren, "(", ")")])
        for emitter in macros[call.group(1)]:
            arg = re.sub(r"^(?:\s*#\[[^]]+\]\s*)+", "", args[emitter["index"]]).strip()
            # cleanup's emitter text runs from the arm's `=>`; keep only the block adjacent to `fn`.
            out.setdefault(arg, si.attr_block(emitter["attribute"], len(emitter["attribute"])))
    return out


def inventory(root: Path, controls: bool) -> list[dict]:
    """Same traversal/gates as cleanup/source_inventory.py, plus annotations of each root."""
    si.REPO = root
    si.SOURCE_ROOT = root / f"{LIB}/verify.rs"
    result = []
    seen = set()
    for path, text, inherited in si.module_sources(si.SOURCE_ROOT):
        if path in seen:
            continue
        seen.add(path)
        rel = path.relative_to(root).as_posix()
        masked = si.predict.mask_comments_strings(text)
        inner = bool(INNER_CONTROLS.match(masked))
        if inner and "kani_smallsort_controls" not in inherited:
            # Inner `#![cfg(kani_smallsort_controls)]` gates the whole file (L-M bridge.rs on its lineage).
            inherited = (*inherited, "kani_smallsort_controls")
        emitted = macro_emitter_attrs(path, text, inherited)
        for item in si.records(path, text, inherited):
            if not si.active(item["gates"], controls):
                continue
            parts = list(path.relative_to(si.SOURCE_ROOT.parent).with_suffix("").parts)
            if parts and parts[0] == "verify":
                parts = parts[1:]
            module = "::".join(parts)
            name = PREFIX + (module + "::" if module else "") + item["name"]
            if item["origin"] == "direct":
                found = re.search(r"\bfn\s+" + re.escape(item["name"]) + r"\s*[<(]", masked)
                attrs = si.attr_block(masked, found.start())
                ann = annotations(attrs)
            else:
                ann = annotations(emitted[item["name"]])
                ann["macro_template"] = True
            result.append(dict(name=name, source=rel, line=item["line"], origin=item["origin"],
                               gates=list(item["gates"]), inherited_gates=list(inherited),
                               inner_cfg=inner, **ann))
    names = [r["name"] for r in result]
    dup = [n for n, c in Counter(names).items() if c > 1]
    if dup:
        raise ValueError(f"duplicate names {dup[:5]}")
    return sorted(result, key=lambda r: r["name"])


def inserted_only(old: str, new: str) -> tuple[bool, list[str]]:
    a, b = old.splitlines(), new.splitlines()
    inserted, ok = [], True
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        if tag != "insert":
            ok = False
        inserted.extend(b[j1:j2])
    return ok, inserted


def main() -> int:
    checks: dict[str, object] = {}
    fail: list[str] = []

    def need(key: str, value: bool, detail=None):
        checks[key] = {"pass": bool(value), **({"detail": detail} if detail is not None else {})}
        if not value:
            fail.append(key)

    head = rev("HEAD")
    lib_status = git("status", "--porcelain", "--", "library").decode()
    use_worktree = bool(lib_status.strip())
    # Identities.
    need("v6_tree", rev(f"{V6_COMMIT}:library") == V6_TREE)
    need("branch_base_tree_equals_v6", rev(f"{BRANCH_BASE}:library") == V6_TREE)
    need("macsplit_report_tree_equals_v6", rev(f"{MACSPLIT_REPORT}:library") == V6_TREE)
    need("branch_base_is_ancestor", subprocess.call(
        ["git", "-C", str(REPO), "merge-base", "--is-ancestor", BRANCH_BASE, "HEAD"]) == 0)
    identities = {}
    for line, d in LINES.items():
        objs = [d["report"], d["library"], *d["prerequisites"]]
        ok = all(git("cat-file", "-t", o).decode().strip() == "commit" for o in objs)
        ok &= subprocess.call(["git", "-C", str(REPO), "merge-base", "--is-ancestor",
                               d["library"], d["report"]]) == 0
        for p in d["prerequisites"]:
            ok &= subprocess.call(["git", "-C", str(REPO), "merge-base", "--is-ancestor", p, d["report"]]) == 0
        identities[line] = dict(report=d["report"], library=d["library"], library_tree=rev(f"{d['library']}:library"),
                                prerequisites={p: rev(f"{p}:library") for p in d["prerequisites"]})
        need(f"identity_{line}", ok)
    need("v5_base_tree", rev(f"{V5_LIB}:library") == "cbe69760c8166d49acf1171c46185dfa3d58b270")
    need("lineN_common_base", all(subprocess.call(["git", "-C", str(REPO), "merge-base", "--is-ancestor",
                                                   NETCOMP_BASE, LINES[k]["library"]]) == 0
                                  for k in ("netten", "u64", "n18")))

    def current(path: str) -> bytes:
        return (REPO / path).read_bytes() if use_worktree else blob("HEAD", path)

    # Source map: byte-identical new files.
    files = {}
    for path, line in COPIED.items():
        src = blob(LINES[line]["library"], path)
        cur = current(path)
        files[path] = dict(source_commit=LINES[line]["library"], source_path=path, sha256=sha(cur),
                           source_sha256=sha(src), relation="byte-identical")
        need(f"copy:{path}", src == cur)
    # netcomp.rs = NETCOMP2 base + NETTEN registration + NET18/MERGESTEP registrations.
    base = blob(NETCOMP_BASE, NETCOMP).decode()
    cur = current(NETCOMP).decode()
    files[NETCOMP] = dict(source_commit=NETCOMP_BASE, sha256=sha(cur.encode()), relation=(
        "NETCOMP2 blob + netten registration (2ebda13e14) + neteighteen/mergestep registrations (248b2725c6)"))
    need("netcomp_composition", cur == base + NETTEN_BLOCK + N18_BLOCK
         and blob(LINES["netten"]["library"], NETCOMP).decode() == base + NETTEN_BLOCK
         and blob(LINES["n18"]["library"], NETCOMP).decode() == base + N18_BLOCK
         and blob(LINES["u64"]["library"], NETCOMP).decode() == base)
    # Parent edits: insertion only, exactly the registrations.
    parents = {}
    for path, lines in PARENT_EDITS.items():
        old = blob(V6_COMMIT, path).decode()
        ok, inserted = inserted_only(old, current(path).decode())
        parents[path] = dict(v6_sha256=sha(old.encode()), sha256=sha(current(path)), inserted=inserted)
        need(f"parent_insert_only:{path}", ok and inserted == lines, inserted)
    # Library-wide preservation: only the 13 paths differ from v6.
    diff_args = ["diff", "--name-status", V6_COMMIT] + ([] if use_worktree else ["HEAD"]) + ["--", "library"]
    changed = sorted(git(*diff_args).decode().split("\n"))
    changed = [c for c in changed if c]
    untracked = [l[3:] for l in lib_status.splitlines() if l.startswith("??")]
    expected_changed = sorted([f"M\t{p}" for p in PARENT_EDITS] + [f"A\t{p}" for p in [*COPIED, NETCOMP]])
    actual_changed = sorted(changed + [f"A\t{p}" for p in untracked if not p.endswith("/")])
    need("library_changed_paths_exact", actual_changed == expected_changed, actual_changed)
    need("runtime_smallsort_rs_unchanged", current(f"{LIB}.rs") == blob(V6_COMMIT, f"{LIB}.rs"))
    # Shared dependencies of transferred files: same bytes as on each source lineage, except L-M,
    # whose merge.rs/specfix.rs differ from v6 exactly by the CLEANUP commit (cfg(any()) removals).
    deps = [f"{LIB}.rs", f"{VER}/merge.rs", f"{VER}/merge/specfix.rs", f"{VER}/types.rs", f"{VER}/comparators.rs"]
    dep_rel = {}
    for line, d in LINES.items():
        same = [p_ for p_ in deps if blob(d["library"], p_) == current(p_)]
        dep_rel[line] = dict(identical=same, differing=[p_ for p_ in deps if p_ not in same])
        if line != "bridge":
            need(f"deps_identical_{line}", len(same) == len(deps), dep_rel[line]["differing"])
    cleanup = "dd0f293f00c032d9fc69b74419a304dbb92d1108"
    lm = [f"{VER}/merge.rs", f"{VER}/merge/specfix.rs"]
    need("deps_bridge_differ_only_by_cleanup",
         dep_rel["bridge"]["differing"] == lm
         and all(blob(LINES["bridge"]["library"], p_) == blob(V4_LIB, p_) == blob(f"{cleanup}^", p_)
                 and blob(cleanup, p_) == blob(V6_COMMIT, p_) == current(p_) for p_ in lm))
    for line in ("wone",):
        old_wrap = blob(LINES[line]["library"], f"{VER}/wrap.rs")
        need("wrap_rs_equals_wone_lineage", old_wrap == current(f"{VER}/wrap.rs"))

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        if use_worktree:
            cand_root = REPO
        else:
            cand_root = export("HEAD", tmp / "head")
        cand_ord = inventory(cand_root, False)
        cand_on = inventory(cand_root, True)
        v6_root = export(V6_COMMIT, tmp / "v6")
        v6_ord = inventory(v6_root, False)
        v6_on = inventory(v6_root, True)
        lineage = {}
        for line, d in LINES.items():
            root = export(d["library"], tmp / line)
            lo, lc = inventory(root, False), inventory(root, True)
            mods = {"bridge": ("bridge::",), "wone": ("wrap::wone::",),
                    "netten": ("network::netcomp::",), "u64": ("network::netcomp::", "network::u64nine::"),
                    "n18": ("network::netcomp::",)}[line]
            sel = [r for r in lc if r["name"][len(PREFIX):].startswith(mods)]
            lineage[line] = dict(total_cfg_on=len(lc), ordinary=len(lo), transferred=[r["name"] for r in sel],
                                 transferred_in_ordinary=[r["name"] for r in lo
                                                          if r["name"][len(PREFIX):].startswith(mods)],
                                 annotations={r["name"]: {k: r.get(k) for k in
                                                          ("kind", "proof_for_contract", "unwind", "stub",
                                                           "stub_verified")} for r in sel},
                                 not_transferred=sorted(set(r["name"] for r in lc) - set(r["name"] for r in sel)
                                                        - set(r["name"] for r in inventory(
                                                            export({"bridge": V4_LIB}.get(line, V5_LIB),
                                                                   tmp / f"{line}-base"), True))))
            need(f"lineage_{line}_transferred_opt_in_only", not lineage[line]["transferred_in_ordinary"])

    names = lambda rows: [r["name"] for r in rows]  # noqa: E731
    ord_names, on_names = names(cand_ord), names(cand_on)
    macsplit = (K1 / "macsplit/ordinary-expected.txt").read_text().splitlines()
    pages = [l for l in (K1 / "macsplit/g1.inventory-pages.txt").read_text().splitlines() if l.startswith("slice::")]
    page_sha = sha(("\n".join(pages) + "\n").encode())
    need("macsplit_native_pages_equal_expected", sorted(pages) == sorted(macsplit) and len(pages) == 202
         and page_sha == "b721d93c7a7eec362fd3fad0327e6e2ed0a866020851251632a7d0761c2bc904")
    need("ordinary_equals_macsplit_native_202", sorted(ord_names) == sorted(macsplit) and len(ord_names) == 202)
    need("ordinary_equals_v6_static", sorted(ord_names) == sorted(names(v6_ord)))
    v6_by = {r["name"]: r for r in v6_on}
    cand_by = {r["name"]: r for r in cand_on}
    # Line numbers in network.rs shift by the inserted registration; all other metadata must match.
    same_ann = all({k: v for k, v in cand_by[n].items() if k != "line"}
                   == {k: v for k, v in v6_by[n].items() if k != "line"} for n in names(v6_on))
    need("v6_roots_unchanged_metadata", same_ann)
    pfc_ord = [r for r in cand_ord if r["kind"] == "pfc"]
    insert_tail = [r for r in pfc_ord if "insert_tail" in r["name"][len(PREFIX):]]
    need("ordinary_pfc_36", len(pfc_ord) == 36, len(pfc_ord))
    need("ordinary_insert_tail_pfc_5", len(insert_tail) == 5, [r["name"][len(PREFIX):] for r in insert_tail])
    need("v6_split_names_present", all(PREFIX + n in ord_names for n in V6_SPLIT))
    need("retired_absent", not any(PREFIX + n in on_names for n in RETIRED)
         and not any("::correct::" in n for n in on_names)
         and not any(PREFIX + n in on_names for n in NOT_TRANSFERRED))
    union = set(names(v6_on))
    for d in lineage.values():
        union |= set(d["transferred"])
    need("cfg_on_equals_union", set(on_names) == union and len(on_names) == len(union))
    added = sorted(set(on_names) - set(names(v6_on)))
    need("added_all_in_transferred_modules", all(n[len(PREFIX):].startswith(TRANSFERRED_MODULES) for n in added))
    need("added_all_controls_gated", all("kani_smallsort_controls" in cand_by[n]["gates"] for n in added))
    lineage_ann_ok = all(
        {k: cand_by[n].get(k) for k in ("kind", "proof_for_contract", "unwind", "stub", "stub_verified")} == ann
        for d in lineage.values() for n, ann in d["annotations"].items())
    need("transferred_annotations_equal_lineage", lineage_ann_ok)
    nt = sorted(set(sum((d["not_transferred"] for d in lineage.values()), [])))
    need("not_transferred_exactly_netnine_netthirteen", nt == sorted(PREFIX + n for n in NOT_TRANSFERRED), nt)

    on_text = "".join(n + "\n" for n in on_names)
    add_text = "".join(n + "\n" for n in added)
    (HERE / "cfg-on-expected.txt").write_text(on_text)
    (HERE / "opt-in-added-expected.txt").write_text(add_text)
    with (HERE / "roots-manifest.tsv").open("w") as out:
        out.write("name\tset\tkind\ttarget\tunwind\tstub\tstub_verified\tsource:line\torigin\tgates\tcfg_provenance\n")
        for r in cand_on:
            short = r["name"][len(PREFIX):]
            sset = "ordinary" if r["name"] in set(ord_names) else "opt-in"
            prov = ("module registration" + (" + inner #![cfg]" if r["inner_cfg"] else "")
                    if "kani_smallsort_controls" in r["inherited_gates"]
                    else "item/macro cfg" if "kani_smallsort_controls" in r["gates"] else "none")
            out.write("\t".join([short, sset, r["kind"], ";".join(r.get("proof_for_contract", [])),
                                 ";".join(r.get("unwind", [])), ";".join(r.get("stub", [])),
                                 ";".join(r.get("stub_verified", [])), f"{r['source'][len(VER) + 1:]}:{r['line']}",
                                 r["origin"] + (" (macro template attrs)" if r.get("macro_template") else ""),
                                 ",".join(r["gates"]) or "-", prov]) + "\n")
    report = dict(
        status="PASS" if not fail else "FAIL", failed=fail, head=head, worktree_mode=use_worktree,
        identities=dict(v6=V6_COMMIT, v6_tree=V6_TREE, branch_base=BRANCH_BASE, macsplit_report=MACSPLIT_REPORT,
                        lines=identities),
        counts=dict(ordinary=len(ord_names), ordinary_pfc=len(pfc_ord), ordinary_plain=len(ord_names) - len(pfc_ord),
                    cfg_on=len(on_names), v6_cfg_on=len(v6_on), added_opt_in=len(added),
                    added_pfc=sum(cand_by[n]["kind"] == "pfc" for n in added),
                    added_plain=sum(cand_by[n]["kind"] == "plain" for n in added)),
        hashes=dict(cfg_on_expected_sha256=sha(on_text.encode()), added_sha256=sha(add_text.encode()),
                    ordinary_names_sha256=sha(("\n".join(sorted(ord_names)) + "\n").encode()),
                    macsplit_expected_sha256=sha((K1 / "macsplit/ordinary-expected.txt").read_bytes()),
                    macsplit_pages_names_sha256=page_sha),
        files=files, parent_edits=parents, dependencies=dep_rel, lineages={k: {kk: vv for kk, vv in v.items() if kk != "annotations"}
                                                       for k, v in lineage.items()},
        checks=checks,
        limitation="Static source forecast; compiler/Kani membership only from the native inventory Build.",
    )
    (HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(dict(status=report["status"], failed=fail, counts=report["counts"], hashes=report["hashes"]),
                     indent=2))
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
