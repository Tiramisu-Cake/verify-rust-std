#!/usr/bin/env python3
"""WRAPMORE static gate: read-only git/source checks, no build or proof.

Usage: python3 -I check_wrapmore.py G > static-check-<G>.json  (G = g1 or g2; writes
cfg-on-expected-<G>.txt next to this file). Checks against BASE (2104e7a596, v6 library tree
d4ec476a7a): the library delta is wrap.rs (only a cfg-gated `mod more;` appended) plus the new
child wrap/more.rs; every other library file is byte-identical; no spec calls a callback or
reads scratch/uninit; ordinary names are unchanged (202) and cfg-on gains exactly the stage's
opt-in names; the expect_check literal is a single literal `kani::assert` line; the request
validates with the pinned lane checker; lane files equal frozen tooling; Rust lines <= 100.
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

STAGE = sys.argv[1]
ROOT = ss.REPO
BASE = "2104e7a596fabb058a99c8bcdf0e3f487d9a7753"
TOOLING = "30f77e859903df14b442ff9294d4fbbd44827f20"
S = "library/core/src/slice/sort/shared/smallsort"
W = ss.PREFIX + "wrap::"
M = W + "more::"
G1 = ["stable_freeze_byte_n2", "unstable_cell_n2", "rejects_always_true_more"]
G2 = [w + "_n4_backing6" for w in ("stable_cell", "unstable_byte", "freeze_noncopy",
                                   "stable_freeze_byte", "unstable_cell")]
NEW = {"g1": G1, "g2": G1 + G2}  # cumulative over BASE; the request holds only the stage rows
ROWS = {"g1": G1, "g2": G2}
PFC = {"stable_freeze_byte_n2": "stable_freeze_byte", "unstable_cell_n2": "unstable_cell"}
PFC.update({n: n[:-len("_backing6")] for n in G2})
LIB_G1 = "0bf64c1c32977c54c090cb4ef23aba40ba38c33c"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]
res, ok = {}, True


def check(name, cond, detail=""):
    global ok
    res[name] = {"ok": bool(cond), "detail": detail}
    ok &= bool(cond)


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], check=True, capture_output=True,
                          text=True).stdout


cur = lambda p: (ROOT / p).read_text()
check("base_is_full_sha", git("rev-parse", BASE).strip() == BASE)
check("base_library_tree_v6", git("rev-parse", f"{BASE}:library").strip().startswith("d4ec476a7a"))

# 1. Library delta: wrap.rs and the new child only.
changed = sorted({l for l in git("diff", "--name-only", BASE, "--", "library").split("\n") if l}
                 | {l for l in git("ls-files", "--others", "--exclude-standard", "--",
                                   "library").split("\n") if l})
check("library_changes_exactly_wrap_rs_and_more_rs",
      changed == [f"{S}/verify/wrap.rs", f"{S}/verify/wrap/more.rs"], changed)
check("more_rs_new_file", git("ls-tree", BASE, f"{S}/verify/wrap/more.rs").strip() == "")
diff = [l for l in git("diff", "-U0", BASE, "--", f"{S}/verify/wrap.rs").split("\n")
        if l and l[0] in "+-" and not l.startswith(("+++", "---"))]
check("wrap_rs_diff_is_cfg_gated_mod_more_appended",
      diff == ["+", "+#[cfg(kani_smallsort_controls)]", "+mod more;"], diff)
old_wrap = git("show", f"{BASE}:{S}/verify/wrap.rs")
check("wrap_rs_prefix_byte_identical", cur(f"{S}/verify/wrap.rs").startswith(old_wrap))

# 2. more.rs content rules.
more = cur(f"{S}/verify/wrap/more.rs")
lines = more.split("\n")
specs = re.findall(r"#\[kani::(?:requires|ensures|modifies)\((.*?)\)\]\n", more, re.S)
check("specs_have_no_callback_calls",
      specs and not any(re.search(r"\bcmp\s*\(|is_less\s*\(|_less\s*\(|always_true\s*\(", s)
                        for s in specs), len(specs))
check("ensures_never_mention_scratch",
      not any("scratch" in s for s in re.findall(r"#\[kani::ensures\((.*?)\)\]\n", more, re.S)))
helper = re.search(r"fn freeze_scratch<.*?\n}\n", more, re.S)[0]
check("scratch_spec_helper_reads_no_values",
      not re.search(r"assume_init|\.read\(|\*scratch|\[\s*\w+\s*\]", helper))
olds = re.findall(r"old\(([^()]*\([^()]*\))\)", more)
check("old_only_scalar_count",
      len(olds) == len(re.findall(r"old\(", more))
      and set(olds) <= {"pair_count(v, probe)", "span_count::<_, 4>(v, probe)"}, sorted(set(olds)))
if STAGE == "g2":
    g1_more = git("show", f"{LIB_G1}:{S}/verify/wrap/more.rs")
    body = lambda t: t[t.index("// Raw scratch keeps"):]
    check("g1_items_byte_identical_after_imports", more[len(more) - len(body(more)):].startswith(
        body(g1_more)), "only the module doc line and use lists changed")
    check("g2_spec_helpers_read_only_input_span",
          not re.search(r"scratch", re.search(r"fn span_sorted.*?\nfn stable_region_n", more,
                                               re.S)[0]))
check("no_stub_cfg_or_visibility_widening",
      not re.search(r"stub|#\[cfg|pub\b|pub\(", more))
check("rust_lines_le_100", max(map(len, lines)) <= 100, max(map(len, lines)))
lit = "wrap canonical comparator required"
tree = {p: cur(p) for p in git("ls-files", f"{S}*").split("\n") if p.endswith(".rs")}
hits = [(p, i + 1) for p, t in tree.items() for i, l in enumerate(t.split("\n")) if lit in l]
check("expect_check_literal_single_kani_assert",
      len(hits) == 1 and hits[0][0].endswith("verify/wrap.rs")
      and cur(hits[0][0]).split("\n")[hits[0][1] - 1].lstrip().startswith("kani::assert("),
      [f"{p.rsplit('/', 1)[1]}:{n}" for p, n in hits])

# 3. Proof-name sets: wrap ordinary module, wrap::more gated by the controls cfg.
m = re.search(r"^((?:#\[cfg[^\n]*\]\n)?)mod more;", cur(f"{S}/verify/wrap.rs"), re.M)
ss.MODULES.append(("wrap", "wrap.rs", "ordinary"))
ss.MODULES.append(("wrap::more", "wrap/more.rs", ss.cfg_class(m[1]) if m else "absent"))
base, now = ss.sets(BASE), ss.sets(None)
macsplit = [l for l in (K1 / "macsplit/ordinary-expected.txt").read_text().split("\n") if l]
new = {M + n for n in NEW[STAGE]}
check("base_sets_202_384", len(base["ordinary"]) == 202 and len(base["cfg_on"]) == 384
      and base["ordinary"] == macsplit)
check("ordinary_unchanged_202", now["ordinary"] == base["ordinary"], len(now["ordinary"]))
check("cfg_on_equals_base_plus_new", now["cfg_on"] == sorted(set(base["cfg_on"]) | new)
      and not (set(base["cfg_on"]) & new), {"count": len(now["cfg_on"]), "added": sorted(new)})
check("retired_unchanged", now["retired"] == base["retired"])
mrec = {r["name"]: (r["pfc"], r["stub_verified"]) for r in now["records"]
        if r["file"] == "wrap/more.rs"}
check("more_pfc_targets_and_no_stubs",
      mrec == {M + n: (PFC.get(n), []) for n in NEW[STAGE]}, mrec)
sha = lambda xs: hashlib.sha256(("\n".join(xs) + "\n").encode()).hexdigest()
(HERE / f"cfg-on-expected-{STAGE}.txt").write_text("\n".join(now["cfg_on"]) + "\n")

# 4. Request and lane.
req = json.loads((HERE / f"{STAGE}.request.json").read_text())
kani_k1.validate_request(req, 720)
check("request_flags", req["kind"] == "measurement" and req["controls"] is True
      and req["kani_jobs"] == 1 and req["uninit_checks"] is False
      and req["harness_timeout_minutes"] == 10 and req["runner"] == "gcb-e2-standard-4"
      and req["agent"] == "k1-merge" and req["request_id"].startswith("wrapmore-"))
want = [(M + n, "FAILED" if n.startswith("rejects") else "SUCCESS",
         lit if n.startswith("rejects") else None) for n in ROWS[STAGE]]
check("request_entries_exact",
      [(e["name"], e["expect"], e.get("expect_check")) for e in req["harnesses"]] == want)
check("lane_files_equal_frozen_tooling",
      git("diff", "--stat", TOOLING, "--", *LANE).strip() == ""
      and not git("status", "--porcelain", "--", *LANE).strip())

json.dump({"stage": STAGE, "base": BASE, "head": git("rev-parse", "HEAD").strip(),
           "library_tree": git("rev-parse", "HEAD:library").strip(),
           "more_rs_sha256": hashlib.sha256(more.encode()).hexdigest(),
           "ordinary": {"count": len(now["ordinary"]), "sha256": sha(now["ordinary"])},
           "cfg_on": {"count": len(now["cfg_on"]), "sha256": sha(now["cfg_on"])},
           "ok": ok, "checks": res}, sys.stdout, indent=1)
print()
sys.exit(0 if ok else 1)
