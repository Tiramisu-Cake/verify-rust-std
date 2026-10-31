#!/usr/bin/env python3
"""INTEGWRAP static gate: read-only git/source checks, no build or proof.

Usage: python3 -I check_integwrap.py > static-check-prebuild.json (writes ordinary-expected.txt
and cfg-on-expected.txt next to this file). Checks: the library delta against BASE (P1-CLEAN) is
exactly verify.rs (one doc line + `mod wrap;` appended) and the new verify/wrap.rs; smallsort.rs
and every other verify module are byte-identical to BASE; wrap.rs equals WRAP-N2 `811c78777d`
except listed comment rewordings and three `cfg(kani_smallsort_controls)` lines; no spec calls a
callback; the static ordinary set is the frozen P1 197 plus the 3 wrap PFCs and the cfg-on set is
the P1-CLEAN 377 plus the 5 wrap harnesses; expect_check literals are single literal
`kani::assert` lines; requests validate with the pinned lane checker; Rust lines <= 100 columns.
"""
import hashlib, importlib.util, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
K1 = HERE.parent
spec = importlib.util.spec_from_file_location("ss", K1 / "poneclean/source_sets.py")
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)
sys.path.insert(0, str(K1 / "tools"))
import kani_k1  # noqa: E402

ROOT = ss.REPO
BASE = "f000cb484e0c64fffa04581a9d5e930ee736f703"
WRAP = "811c78777d"
S = "library/core/src/slice/sort/shared/smallsort"
PREFIX = ss.PREFIX
W = PREFIX + "wrap::"
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


check("base_is_full_sha", git("rev-parse", BASE).strip() == BASE)

# 1. Library delta limited to verify.rs + new wrap.rs; everything else byte-identical.
changed = sorted({l for l in git("diff", "--name-only", BASE, "--", "library").split("\n") if l}
                 | {l for l in git("ls-files", "--others", "--exclude-standard", "--",
                                   "library").split("\n") if l})
check("library_changes_exactly_verify_rs_and_wrap_rs",
      changed == [f"{S}/verify.rs", f"{S}/verify/wrap.rs"], changed)
check("wrap_rs_new_file", git("ls-tree", BASE, f"{S}/verify/wrap.rs").strip() == "")
check("smallsort_rs_byte_identical_to_base", git("show", f"{BASE}:{S}.rs") == cur(f"{S}.rs"))

# 2. verify.rs: one added doc line, `mod wrap;` appended, nothing removed, order unchanged.
diff = [l for l in git("diff", "-U0", BASE, "--", f"{S}/verify.rs").split("\n")
        if l and l[0] in "+-" and not l.startswith(("+++", "---"))]
check("verify_rs_diff_is_one_doc_line_and_mod_wrap",
      len(diff) == 2 and diff[0].startswith("+//! `wrap` ") and diff[1] == "+mod wrap;", diff)
mods = lambda t: re.findall(r"^(?:#\[cfg[^\n]*\]\n)?mod \w+;", t, re.M)
check("verify_rs_module_order_unchanged_wrap_appended_ordinary",
      mods(cur(f"{S}/verify.rs")) == mods(git("show", f"{BASE}:{S}/verify.rs")) + ["mod wrap;"])

# 3. wrap.rs vs WRAP-N2: code identical after removing comments and the three cfg lines.
old, new = git("show", f"{WRAP}:{S}/verify/wrap.rs"), cur(f"{S}/verify/wrap.rs")
code = lambda t: [l for l in t.split("\n") if not l.lstrip().startswith("//")
                  and l != "#[cfg(kani_smallsort_controls)]"]
check("wrap_rs_code_equals_wrap_n2_without_comments", code(old) == code(new))
cfg_items = re.findall(r"#\[cfg\(kani_smallsort_controls\)\]\n(?:#\[[^\n]*\]\n)*fn (\w+)", new)
check("wrap_rs_cfg_gated_items",
      cfg_items == ["always_true", "rejects_always_true", "rejects_payload_corruption"], cfg_items)
check("wrap_rs_no_other_cfg", new.count("#[cfg(") == 3)
check("wrap_rs_no_stub_or_research_labels",
      not re.search(r"stub_verified|WRAP-N2|SPECFIX|StageA|G1|E0502", new))

# 4. No callback call in wrap.rs specs; guard literal located once.
specs = re.findall(r"#\[kani::(?:requires|ensures|modifies)\((.*?)\)\]\n", new)
check("wrap_specs_have_no_callback_calls",
      len(specs) == 15 and not any(re.search(r"\bcmp\s*\(|is_less\s*\(|_less\s*\(", s)
                                   for s in specs), len(specs))
lines = new.split("\n")
for lit in ("wrap canonical comparator required",
            "wrap full-value checker rejects payload corruption"):
    hits = [i + 1 for i, l in enumerate(lines) if lit in l]
    check(f"expect_check_literal_kani_assert:{lit}",
          len(hits) == 1 and lines[hits[0] - 1].lstrip().startswith("kani::assert("),
          [f"wrap.rs:{n}" for n in hits])

# 5. Proof-name sets (source_sets.py extended with the wrap module, class from verify.rs).
m = re.search(r"^((?:#\[cfg[^\n]*\]\n)?)mod wrap;", cur(f"{S}/verify.rs"), re.M)
ss.MODULES.append(("wrap", "wrap.rs", ss.cfg_class(m[1]) if m else "absent"))
base, now = ss.sets(BASE), ss.sets(None)
frozen = [l for l in (K1 / "poneclean/ordinary-expected.txt").read_text().split("\n") if l]
p1_cfg = [l for l in (K1 / "poneclean/cfg-on-expected.txt").read_text().split("\n") if l]
wrap_pfc = {W + n for n in ("stable_cell_n2", "unstable_byte_n2", "freeze_noncopy_n2")}
wrap_ctl = {W + n for n in ("rejects_always_true", "rejects_payload_corruption")}
check("base_sets_equal_p1_clean_native", base["ordinary"] == frozen and base["cfg_on"] == p1_cfg,
      {"ordinary": len(base["ordinary"]), "cfg_on": len(base["cfg_on"])})
check("ordinary_equals_frozen_197_plus_3_wrap",
      len(frozen) == 197 and now["ordinary"] == sorted(set(frozen) | wrap_pfc),
      len(now["ordinary"]))
check("cfg_on_equals_p1_clean_377_plus_5_wrap",
      len(p1_cfg) == 377 and now["cfg_on"] == sorted(set(p1_cfg) | wrap_pfc | wrap_ctl),
      len(now["cfg_on"]))
check("retired_unchanged", now["retired"] == base["retired"], len(now["retired"]))
wrec = {r["name"]: r for r in now["records"] if r["file"] == "wrap.rs"}
check("wrap_pfc_targets_and_no_stubs",
      {n: (r["pfc"], r["stub_verified"]) for n, r in wrec.items()} ==
      {W + "stable_cell_n2": ("stable_cell", []), W + "unstable_byte_n2": ("unstable_byte", []),
       W + "freeze_noncopy_n2": ("freeze_noncopy", []),
       W + "rejects_always_true": (None, []), W + "rejects_payload_corruption": (None, [])})
sha = lambda xs: hashlib.sha256(("\n".join(xs) + "\n").encode()).hexdigest()
(HERE / "ordinary-expected.txt").write_text("\n".join(now["ordinary"]) + "\n")
(HERE / "cfg-on-expected.txt").write_text("\n".join(now["cfg_on"]) + "\n")

# 6. Requests.
reqs = {g: json.loads((HERE / f"{g}.request.json").read_text()) for g in ("g1", "g2")}
for g, r in reqs.items():
    kani_k1.validate_request(r)
g1, g2 = reqs["g1"], reqs["g2"]
check("g1_flags", g1["kind"] == "measurement" and g1["controls"] is True and g1["kani_jobs"] == 1
      and g1["uninit_checks"] is False and g1["harness_timeout_minutes"] == 10
      and g1["runner"] == "gcb-e2-standard-4")
check("g1_entries_exact", [(e["name"], e["expect"], e.get("expect_check")) for e in g1["harnesses"]]
      == [(W + "stable_cell_n2", "SUCCESS", None), (W + "unstable_byte_n2", "SUCCESS", None),
          (W + "freeze_noncopy_n2", "SUCCESS", None),
          (W + "rejects_always_true", "FAILED", "wrap canonical comparator required"),
          (W + "rejects_payload_corruption", "FAILED",
           "wrap full-value checker rejects payload corruption")])
check("g1_entries_equal_wrap_n2_g2_retry_request",
      g1["harnesses"] == json.loads(git("show", "73336711b0:research/challenge-8/kani-k1/wraptwo/"
                                         "g2-retry.request.json"))["harnesses"])
check("g2_inventory_flags", g2["kind"] == "inventory" and g2["controls"] is False
      and g2["inventory"] is True and g2["harnesses"] == [] and g2["harness_timeout_minutes"] == 20
      and "kani_jobs" not in g2 and "uninit_checks" not in g2)

# 7. Line widths.
wide = [f"{p.rsplit('/', 1)[1]}:{i + 1}" for p in (f"{S}/verify.rs", f"{S}/verify/wrap.rs")
        for i, l in enumerate(cur(p).split("\n")) if len(l) > 100]
check("changed_rust_lines_le_100", not wide, wide)

print(json.dumps({"base": BASE, "head": git("rev-parse", "HEAD").strip(),
                  "library_tree": git("rev-parse", "HEAD:library").strip(),
                  "ordinary": {"count": len(now["ordinary"]), "sha256": sha(now["ordinary"])},
                  "cfg_on": {"count": len(now["cfg_on"]), "sha256": sha(now["cfg_on"])},
                  "ok": ok, "checks": res}, indent=1))
sys.exit(0 if ok else 1)
