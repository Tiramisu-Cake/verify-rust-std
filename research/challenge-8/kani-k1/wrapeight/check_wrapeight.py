#!/usr/bin/env python3
"""WRAPEIGHT static gate: read-only git/source checks, no build or proof.

Usage: python3 -I check_wrapeight.py > static-check.json  (writes cfg-on-expected.txt and
semantic-diff.txt next to this file). Checks against BASE (e8e238db9d, v6 library tree
d4ec476a7a + tooling + cap 93.96): the first library commits are the two WRAPMORE
cherry-picks (library tree 7cdb7ee5eb = WRAPMORE G2); the WRAPEIGHT commit only appends to
verify/wrap/more.rs; no spec calls a callback; ordinary names (202) and ordinary PFC (36) are
unchanged, cfg-on is 392 after WRAPMORE and 396 now with the exact four new names; the
request validates with the pinned lane checker; lane files equal BASE; Rust lines <= 100.
"""
import difflib, hashlib, importlib.util, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
K1 = HERE.parent
spec = importlib.util.spec_from_file_location("ss", K1 / "poneclean/source_sets.py")
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)
sys.path.insert(0, str(K1 / "tools"))
import kani_k1  # noqa: E402

ROOT = ss.REPO
BASE = "e8e238db9d87323fa4da011a1a8b37fb76ec91c0"
OLD_TOOLING = "30f77e859903df14b442ff9294d4fbbd44827f20"
WRAPMORE = ["0bf64c1c32977c54c090cb4ef23aba40ba38c33c", "716e094b615484c1e0f1fac3e6f87299f14a0c49"]
WRAPMORE_TREE = "7cdb7ee5eb8343ee943c9b79b2a4ecdb04fa60b8"
S = "library/core/src/slice/sort/shared/smallsort"
MORE = f"{S}/verify/wrap/more.rs"
M = ss.PREFIX + "wrap::more::"
NEW = {"stable_cell_n8_backing10": "stable_cell_n8", "unstable_cell_n8_backing10": "unstable_cell_n8",
       "unstable_byte_n8_backing10": "unstable_byte_n8", "unstable_byte_n9_backing11": "unstable_byte_n9"}
N4 = {"stable_cell_n8": "stable_cell_n4", "unstable_cell_n8": "unstable_cell_n4",
      "unstable_byte_n8": "unstable_byte_n4", "unstable_byte_n9": "unstable_byte_n4"}
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

# 1. History: BASE -> task commit -> two WRAPMORE cherry-picks -> one WRAPEIGHT library commit.
lib_commits = [c for c in git("rev-list", "--reverse", f"{BASE}..HEAD", "--", "library").split()]
check("library_commits_are_two_cherry_picks_plus_one", len(lib_commits) == 3, lib_commits)
picks, own = lib_commits[:2], lib_commits[2] if len(lib_commits) == 3 else None
patch_id = lambda c: subprocess.run(["git", "-C", str(ROOT), "patch-id", "--stable"], input=git(
    "show", c), capture_output=True, text=True, check=True).stdout.split()[0]
check("cherry_picks_patch_identical_to_wrapmore",
      [patch_id(c) for c in picks] == [patch_id(c) for c in WRAPMORE], picks)
check("after_picks_library_tree_is_wrapmore_g2",
      git("rev-parse", f"{picks[1]}:library").strip() == WRAPMORE_TREE)
check("picks_touch_only_wrap_rs_and_more_rs",
      sorted({f for c in picks for f in git("show", "--name-only", "--format=", c).split()})
      == [f"{S}/verify/wrap.rs", MORE])
check("own_commit_touches_only_more_rs",
      own and git("show", "--name-only", "--format=", own).split() == [MORE])
changed = sorted({l for l in git("diff", "--name-only", BASE, "--").split("\n") if l}
                 | {l for l in git("ls-files", "--others", "--exclude-standard").split("\n") if l})
check("non_library_changes_are_research_only",
      all(p.startswith("research/challenge-8/kani-k1/") and not p.startswith(
          ("research/challenge-8/kani-k1/tools", "research/challenge-8/kani-k1/gcb"))
          for p in changed if not p.startswith("library/")), changed)
check("library_changes_exactly_wrap_rs_and_more_rs",
      [p for p in changed if p.startswith("library/")] == [f"{S}/verify/wrap.rs", MORE])

# 2. more.rs: WRAPMORE prefix byte-identical, wrap.rs equal to WRAPMORE.
more = cur(MORE)
wm_more = git("show", f"{WRAPMORE[1]}:{MORE}")
check("more_rs_prefix_is_wrapmore_byte_identical", more.startswith(wm_more))
check("wrap_rs_equals_wrapmore", cur(f"{S}/verify/wrap.rs")
      == git("show", f"{WRAPMORE[1]}:{S}/verify/wrap.rs"))
added = more[len(wm_more):]
lines = more.split("\n")
specs = re.findall(r"#\[kani::(?:requires|ensures|modifies)\((.*?)\)\]\n", added, re.S)
check("new_specs_have_no_callback_calls",
      len(specs) == 20 and not any(re.search(r"\bcmp\s*\(|is_less\s*\(|_less\s*\(", s)
                                   for s in specs), len(specs))
olds = re.findall(r"old\(([^()]*\([^()]*\))\)", added)
check("old_only_scalar_count",
      len(olds) == len(re.findall(r"old\(", added)) == 4
      and set(olds) == {"span_count::<_, 8>(v, probe)", "span_count::<_, 9>(v, probe)"},
      sorted(set(olds)))
check("no_stub_cfg_or_visibility_widening", not re.search(r"stub|#\[cfg|pub\b|pub\(", more))
check("rust_lines_le_100", max(map(len, lines)) <= 100, max(map(len, lines)))
check("unwind_16_on_every_new_root",
      len(re.findall(r"#\[kani::proof_for_contract\(\w+\)\]\n#\[kani::unwind\(16\)\]\n", added))
      == 4)

# 3. Semantic diff of each new wrapper/root against its *_n4 / *_n4_backing6 original.
def item(text, name):
    m = re.search(rf"\n((?://[^\n]*\n)*(?:#\[[^\n]*\n|    [^\n]*\n|\)\]\n)*(?:unsafe )?fn {name}\("
                  rf".*?\n}}\n)", text, re.S)
    return m[1]

out = []
for root, wrapper in NEW.items():
    n4 = N4[wrapper]
    for old, new in ((n4, wrapper), (n4 + "_backing6", root)):
        out += difflib.unified_diff(item(more, old).splitlines(), item(more, new).splitlines(),
                                    f"{old}", f"{new}", n=0, lineterm="")
(HERE / "semantic-diff.txt").write_text("\n".join(out) + "\n")

# 4. Proof-name sets: wrap ordinary, wrap::more gated by the controls cfg.
ss.MODULES.append(("wrap", "wrap.rs", "ordinary"))


def sets(rev):
    m = re.search(r"^((?:#\[cfg[^\n]*\]\n)?)mod more;", ss.text_at("wrap.rs", rev), re.M)
    mods = list(ss.MODULES)
    ss.MODULES.append(("wrap::more", "wrap/more.rs", ss.cfg_class(m[1]) if m else "absent"))
    try:
        return ss.sets(rev)
    finally:
        ss.MODULES[:] = mods


opfc = lambda s: sorted(r["name"] for r in s["records"] if r["cls"] == "ordinary" and r["pfc"])
cpfc = lambda s: sorted(r["name"] for r in s["records"]
                        if r["cls"] in ("ordinary", "controls") and r["pfc"])
base, mid, now = sets(BASE), sets(picks[1]), sets(None)
macsplit = [l for l in (K1 / "macsplit/ordinary-expected.txt").read_text().split("\n") if l]
new = {M + n for n in NEW}
check("base_sets_202_384", len(base["ordinary"]) == 202 and len(base["cfg_on"]) == 384
      and base["ordinary"] == macsplit)
check("ordinary_unchanged_202", now["ordinary"] == base["ordinary"] == mid["ordinary"])
check("ordinary_pfc_unchanged_36", len(opfc(base)) == 36 and opfc(now) == opfc(base))
check("cfg_on_392_after_wrapmore", len(mid["cfg_on"]) == 392)
check("cfg_on_equals_wrapmore_plus_four", now["cfg_on"] == sorted(set(mid["cfg_on"]) | new)
      and not (set(mid["cfg_on"]) & new) and len(now["cfg_on"]) == 396, sorted(new))
check("retired_unchanged", now["retired"] == base["retired"] == [])
check("cfg_on_pfc_38_45_49", [len(cpfc(s)) for s in (base, mid, now)] == [38, 45, 49],
      {"opt_in_pfc": [len(cpfc(s)) - len(opfc(s)) for s in (base, mid, now)]})
mrec = {r["name"]: (r["pfc"], r["stub_verified"]) for r in now["records"]
        if r["file"] == "wrap/more.rs" and r["name"] in new}
check("new_pfc_targets_and_no_stubs", mrec == {M + n: (w, []) for n, w in NEW.items()}, mrec)
sha = lambda xs: hashlib.sha256(("\n".join(xs) + "\n").encode()).hexdigest()
(HERE / "cfg-on-expected.txt").write_text("\n".join(now["cfg_on"]) + "\n")

# 5. Request and lane.
req = json.loads((HERE / "g1.request.json").read_text())
kani_k1.validate_request(req, 720)
check("run_request_equals_packet_request",
      (K1 / "RUN-REQUEST.json").read_text() == (HERE / "g1.request.json").read_text())
check("request_flags", req["kind"] == "measurement" and req["controls"] is True
      and req["kani_jobs"] == 1 and req["uninit_checks"] is False
      and req["harness_timeout_minutes"] == 10 and req["runner"] == "gcb-e2-standard-4"
      and req["agent"] == "k1-merge" and req["request_id"].startswith("wrapeight-"))
check("request_entries_exact",
      [(e["name"], e["expect"], e.get("expect_check")) for e in req["harnesses"]]
      == [(M + n, "SUCCESS", None) for n in NEW])
check("lane_files_equal_base",
      git("diff", "--stat", BASE, "--", *LANE).strip() == ""
      and not git("status", "--porcelain", "--", *LANE).strip())
check("lane_delta_vs_30f77e85_is_k1g_cap_only",
      git("diff", "--name-only", OLD_TOOLING, BASE, "--", *LANE).split()
      == ["research/challenge-8/kani-k1/tools/k1g.sh"])

json.dump({"base": BASE, "head": git("rev-parse", "HEAD").strip(),
           "library_tree": git("rev-parse", "HEAD:library").strip(),
           "more_rs_sha256": hashlib.sha256(more.encode()).hexdigest(),
           "ordinary": {"count": len(now["ordinary"]), "sha256": sha(now["ordinary"])},
           "ordinary_pfc": len(opfc(now)),
           "cfg_on": {"count": len(now["cfg_on"]), "sha256": sha(now["cfg_on"])},
           "cfg_on_pfc": len(cpfc(now)), "opt_in_pfc": len(cpfc(now)) - len(opfc(now)),
           "ok": ok, "checks": res}, sys.stdout, indent=1)
print()
sys.exit(0 if ok else 1)
