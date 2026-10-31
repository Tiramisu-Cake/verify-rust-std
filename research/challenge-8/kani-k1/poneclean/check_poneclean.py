#!/usr/bin/env python3
"""P1-CLEAN static gate: read-only git/source checks, no build or proof.

Usage: python3 -I check_poneclean.py > static-check.json (writes ordinary-expected.txt,
cfg-on-expected.txt and PFC-MAP.tsv next to this file). Checks: smallsort.rs differs from BASE
only by deleted annotations/their comments and the unused `kani` import (runtime bodies and
signatures byte-identical, no `kani::` left); library changes are limited to the verify files;
no specification attribute calls a callback; no active proof or stub targets a raw helper;
the static ordinary set equals the frozen P1 197 names; the cfg-on set equals BASE minus
DEACTIVATED.tsv plus the new opt-in harnesses; every P1 PFC targets the expected profile/tag;
expect_check literals are located; requests validate; changed Rust lines are <= 100 columns.
"""
import csv, importlib.util, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
K1 = HERE.parent
spec = importlib.util.spec_from_file_location("ss", HERE / "source_sets.py")
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)
sys.path.insert(0, str(K1 / "tools"))
import kani_k1  # noqa: E402

ROOT = ss.REPO
BASE = "6f3a2629615cc7184b840d3c21aaea54b129267e"
S = "library/core/src/slice/sort/shared/smallsort"
PREFIX = ss.PREFIX
res, ok = {}, True


def check(name, cond, detail=""):
    global ok
    res[name] = {"ok": bool(cond), "detail": detail}
    ok &= bool(cond)


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], check=True, capture_output=True,
                          text=True).stdout


def cur(p):
    return (ROOT / p).read_text()


# 1. smallsort.rs: only annotation blocks, their `// Contract:` comments and the import go.
base_rs, cur_rs = git("show", f"{BASE}:{S}.rs"), cur(f"{S}.rs")
lines = base_rs.split("\n")
keep, i = [], 0
while i < len(lines):
    line = lines[i]
    if line.startswith("#[cfg_attr(kani, kani::"):
        depth = 0
        while True:
            depth += lines[i].count("[") - lines[i].count("]")
            depth += lines[i].count("(") - lines[i].count(")")
            i += 1
            if depth <= 0:
                break
        continue
    if line.startswith("// Contract:"):
        while lines[i].startswith("//") and not lines[i].startswith("///"):
            i += 1
        continue
    if line.startswith("// The pair is ordered on return.") or line.startswith(
            "// is valid only for stateless comparators"):
        i += 1
        continue
    keep.append(line)
    i += 1
proj = "\n".join(keep)
proj = proj.replace("// Bounded SmallSort verification; contracts and harnesses are isolated from "
                    "ordinary Rust builds.\n#[cfg(kani)]\nuse crate::kani;\n",
                    "// Bounded SmallSort verification; harnesses are isolated from ordinary Rust "
                    "builds.\n")
check("smallsort_rs_equals_annotation_free_projection_of_base", proj == cur_rs)
check("smallsort_rs_has_no_kani_contracts", "kani::" not in cur_rs)
added = [l for l in git("diff", "-U0", BASE, "--", f"{S}.rs").split("\n")
         if l.startswith("+") and not l.startswith("+++")]
check("smallsort_rs_only_added_line_is_tail_comment",
      added == ["+// Bounded SmallSort verification; harnesses are isolated from ordinary Rust builds."],
      added)
for fn in ("swap_if_less", "insert_tail", "sort4_stable", "bidirectional_merge"):
    sig = lambda t: re.search(rf"\n((?:pub )?unsafe fn {fn}<[^{{]*)\{{", t)[1]
    check(f"signature_identical:{fn}", sig(base_rs) == sig(cur_rs))

# 2. Library changes limited.
changed = [l for l in git("diff", "--name-only", BASE, "--", "library").split("\n") if l]
untracked = [l for l in git("ls-files", "--others", "--exclude-standard", "--", "library").split("\n") if l]
allowed = {f"{S}.rs"} | {f"{S}/verify{x}" for x in
                         (".rs", "/merge.rs", "/network.rs", "/correct.rs", "/merge/specfix.rs",
                          "/merge/specdiag.rs")}
check("library_changes_limited", set(changed + untracked) <= allowed, sorted(set(changed + untracked)))
check("verify_rs_module_order_unchanged",
      re.findall(r"^(?:#\[cfg[^\n]*\]\n)?mod \w+;", git("show", f"{BASE}:{S}/verify.rs"), re.M)
      == re.findall(r"^(?:#\[cfg[^\n]*\]\n)?mod \w+;", cur(f"{S}/verify.rs"), re.M))

# 3. No callback call in any specification attribute under verify/ and smallsort.rs.
spec_re = re.compile(r"#\[(?:cfg_attr\(kani, )?kani::(?:requires|ensures|modifies)\((.*?)\)\]\n"
                     r"(?=\s*(?:#|pub|unsafe|fn))", re.S)
calls, nspec = [], 0
for p in [f"{S}.rs"] + [str(x.relative_to(ROOT)) for x in (ROOT / S / "verify").rglob("*.rs")]:
    for m in spec_re.finditer(cur(p)):
        nspec += 1
        if re.search(r"\bcmp\s*\(|is_less\s*\(|\(\*f\)|call_comparator|\bf\s*\(", m[1]):
            calls.append(p)
check("specs_have_no_callback_calls", nspec > 0 and not calls, {"clauses": nspec, "calling": calls})
check("no_callback_spec_helpers_left",
      not re.search(r"fn (call_comparator|is_sorted_unrolled|valid_sorted_tail|merge_inputs_are_sorted)\b",
                    cur(f"{S}/verify/merge.rs")))

# 4. Proof-name sets.
base, now = ss.sets(BASE), ss.sets(None)
frozen = sorted({l.strip() for l in (K1 / "specfix/g2.inventory.txt").read_text().split("\n")
                 if l.startswith(PREFIX)})
check("frozen_p1_count_197", len(frozen) == 197)
check("static_ordinary_equals_frozen_p1", now["ordinary"] == frozen,
      {"missing": sorted(set(frozen) - set(now["ordinary"])),
       "extra": sorted(set(now["ordinary"]) - set(frozen))})
raw = re.compile(r"(?:^|::)(swap_if_less|sort4_stable|insert_tail|bidirectional_merge)$")
active_raw = [r["name"] for r in now["records"] if r["cls"] != "retired" and (
    (r["pfc"] and raw.search(r["pfc"])) or any(raw.search(x) for x in r["stub_verified"]))]
check("no_active_raw_contract_proof_or_stub", not active_raw, active_raw)
ordinary_stubs = [r["name"] for r in now["records"] if r["cls"] == "ordinary" and r["stub_verified"]]
check("no_ordinary_stub_verified", not ordinary_stubs, ordinary_stubs)
deact = list(csv.DictReader(open(HERE / "DEACTIVATED.tsv"), delimiter="\t"))
gone = {PREFIX + d["name"] for d in deact}
new = {PREFIX + "merge::specfix::" + n for n in (
    "specfix_wrong_f_swap_rejected_u8", "specfix_wrong_f_sort4_rejected_u64",
    "specfix_wrong_f_insert_rejected_u8", "specfix_wrong_f_merge_rejected_u8",
    "specfix_case5_typed_swap_bytes17", "specfix_case5_typed_swap_bytes128",
    "specfix_case5_typed_swap_bytes129")}
check("cfg_on_equals_base_minus_deactivated_plus_new",
      set(now["cfg_on"]) == (set(base["cfg_on"]) - gone) | new,
      {"count": len(now["cfg_on"]), "base": len(base["cfg_on"]), "deactivated": len(gone)})
check("new_harnesses_are_opt_in", not (new & set(now["ordinary"])))
(HERE / "ordinary-expected.txt").write_text("\n".join(now["ordinary"]) + "\n")
(HERE / "cfg-on-expected.txt").write_text("\n".join(now["cfg_on"]) + "\n")

# 5. P1 PFC -> profile/tag map (32) and the 4 former stub consumers.
transfer = list(csv.DictReader(open(K1 / "specfix/TRANSFER.tsv"), delimiter="\t"))
p1_pfc = sorted(r["harness"] for r in transfer if r["P1_member"] == "yes" and r["consumer_kind"] == "PFC")
p1_stub = sorted(r["harness"] for r in transfer if r["P1_member"] == "yes" and r["consumer_kind"] == "stub_verified")
rec = {r["name"].rsplit("::", 1)[1]: r for r in now["records"] if r["cls"] != "retired"}
TAG = {"merge_contract_u64": "LtU64", "merge_contract_u8": "LtU8", "merge_scratch48_contract_u8": "LtU8",
       "sort4_contract_u64": "Sort4ReadU64", "sort4_contract_bytes16": "Sort4ReadB16",
       "insert_tail_contract_u64": "LtU64", "contract_insert_tail_u8": "LtU8",
       "swap_contract_bytes16": "KeyB16", "swap_contract_bytes17": "KeyB17",
       "swap_contract_cell_i32": "CellI32", "swap_contract_drop_u8": "DropU8",
       "swap_contract_four_positions_i32": "LtI32", "swap_contract_four_positions_u64": "LtU64",
       "swap_contract_four_positions_u8": "LtU8", "swap_contract_u64": "StrictU64",
       "swap_contract_u8": "StrictU8"}
srcs = {f: cur(f"{S}/verify/{f}") for f in ("merge.rs", "network.rs", "correct.rs")}
rows, bad = [], []
for h in p1_pfc:
    r = rec.get(h)
    tag = next(v for k, v in sorted(TAG.items(), key=lambda kv: -len(kv[0])) if h.startswith(k))
    fam = r and r["pfc"].rsplit("::", 1)[1]
    text = srcs[r["file"]] if r else ""
    # The tag must appear in the instantiation or direct body naming this harness.
    m = re.search(rf"(?s)(?:\b{h}\b.*?\);|fn {h}\(\)\s*\{{.*?\n\}})", text)
    found = bool(m and re.search(rf"\b{tag}\b", m[0]))
    if r and r.get("macro") == "insert_tail_start1_group_case":
        # The group macro's shared body fixes the tag; check that body once.
        body = re.search(r"(?s)fn insert_tail_group_value<.*?\n\}", text)[0]
        found = "insert_tail_profile::<LtU64>(" in body and "LtU64::CMP" in body
    if not (r and r["cls"] == "ordinary" and fam.endswith("_profile") and found):
        bad.append(h)
    rows.append([h, r["name"].split("verify::")[1].rsplit("::", 1)[0] if r else "?", fam, tag,
                 f"{r['file']}:{r['line']}" if r else "?"])
check("p1_pfc_count_32", len(p1_pfc) == 32, len(p1_pfc))
check("p1_pfc_all_profile_targets_with_tag", not bad, bad)
stub_bad = [h for h in p1_stub if h not in rec or rec[h]["stub_verified"] or rec[h]["cls"] != "ordinary"]
check("p1_former_stub_consumers_real_body", len(p1_stub) == 4 and not stub_bad, stub_bad)
with open(HERE / "PFC-MAP.tsv", "w") as f:
    f.write("harness\tmodule\tprofile\ttag\tsource\n")
    for row in rows:
        f.write("\t".join(row) + "\n")
    for h in p1_stub:
        f.write(f"{h}\tmerge\treal body (stub_verified removed)\t-\t{rec[h]['file']}:{rec[h]['line']}\n")

# 6. expect_check literals and request validation.
sf = cur(f"{S}/verify/merge/specfix.rs").split("\n")
for prof in ("swap_profile", "sort4_profile", "insert_tail_profile", "merge_profile"):
    decl = next(i for i, l in enumerate(sf) if re.match(rf"pub\(crate\) unsafe fn {prof}<", l))
    j = decl - 1
    while j >= 0 and sf[j].startswith(("#[", "    ", ")]", "|")):
        j -= 1
    hits = [i + 1 for i in range(j + 1, decl) if "specfix_canonical_comparator" in sf[i]]
    check(f"guard_requires_located:{prof}", len(hits) == 1, [f"merge/specfix.rs:{n}" for n in hits])
reqs = {g: json.loads((HERE / f"{g}.request.json").read_text()) for g in ("g1", "g2", "g3")}
for g, r in reqs.items():
    kani_k1.validate_request(r)
g1 = reqs["g1"]
check("g1_entries_13_to_14", 13 <= len(g1["harnesses"]) <= 14, len(g1["harnesses"]))
check("g1_names_in_cfg_on", all(e["name"] in now["cfg_on"] for e in g1["harnesses"]))
check("g1_flags", g1["kind"] == "measurement" and g1["controls"] and g1["kani_jobs"] == 1
      and g1["uninit_checks"] is False and g1["harness_timeout_minutes"] == 10)
check("g2_g3_inventory_flags", reqs["g2"]["controls"] is False and reqs["g3"]["controls"] is True
      and reqs["g2"]["harness_timeout_minutes"] == 20 and reqs["g3"]["harness_timeout_minutes"] == 30)

# 7. Line widths of changed Rust files.
wide = []
for p in sorted(allowed - {f"{S}.rs"}):
    for i, l in enumerate(cur(p).split("\n")):
        if len(l) > 100:
            wide.append(f"{p.rsplit('/', 1)[1]}:{i + 1}")
check("verify_rust_lines_le_100", not wide, wide)

print(json.dumps({"base": BASE, "head": git("rev-parse", "HEAD").strip(), "ok": ok, "checks": res}, indent=1))
sys.exit(0 if ok else 1)
