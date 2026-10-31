#!/usr/bin/env python3
"""SPECFIX StageA static gate: read-only git/source checks, no build or proof.

Usage: python3 -I check_specfix.py [BASE] > static-check.json
Checks that production smallsort.rs is byte-identical to BASE, that verify/ changes are limited
to the opt-in specfix module, the opt-in DropValue profile in network.rs and the
matches_value_probe guard, that no profile specification calls a callback, that every
expected-FAILED check is a unique literal and that the G1-G3 requests validate and name
existing harnesses.
"""
import json, re, subprocess, sys
from pathlib import Path

K1 = Path(__file__).resolve().parents[1]
ROOT = K1.parents[2]
BASE = sys.argv[1] if len(sys.argv) > 1 else "d8f97fb2dfda3df9384ba80ccfedc6a328d69af9"
S = "library/core/src/slice/sort/shared/smallsort"
sys.path.insert(0, str(K1 / "tools"))
import kani_k1  # noqa: E402

def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], check=True, capture_output=True, text=True).stdout

def base_file(p):
    return git("show", f"{BASE}:{p}")

def cur(p):
    return (ROOT / p).read_text()

res, ok = {}, True
def check(name, cond, detail=""):
    global ok
    res[name] = {"ok": bool(cond), "detail": detail}
    ok &= bool(cond)

# 1. Production file and every other library file outside the three verify files unchanged.
check("smallsort_rs_byte_identical", base_file(f"{S}.rs") == cur(f"{S}.rs"))
changed = [l for l in git("diff", "--name-only", BASE, "--", "library").split("\n") if l]
untracked = [l for l in git("ls-files", "--others", "--exclude-standard", "--", "library").split("\n") if l]
allowed = {f"{S}/verify/merge.rs", f"{S}/verify/network.rs", f"{S}/verify/merge/specfix.rs"}
check("library_changes_limited", set(changed + untracked) <= allowed, sorted(set(changed + untracked)))

# 2. merge.rs: removing the registration and the guard gives the base text byte for byte.
merge = cur(f"{S}/verify/merge.rs")
reg = "#[cfg(kani_smallsort_controls)]\npub(super) mod specfix;\n"
guard = ('    kani::assert(n <= PROBE_BYTES, "value probe supports at most 128 bytes per value");\n'
         "    if n > PROBE_BYTES {\n        return false;\n    }\n")
doc = ("/// Supported domain: `size_of::<T>() <= PROBE_BYTES`, checked here before the first read even\n"
       "/// when `set_value_probe` was bypassed; a larger `T` is an explicit unsupported-domain failure.\n")
safety_new = ("    // SAFETY: `p` is readable for `n` bytes and `n <= PROBE_BYTES` was checked above; every read\n")
safety_old = ("    // SAFETY: `p` is readable for `n` bytes and the probe buffer is larger than `n`; every read\n")
proj = merge
for piece in (reg, guard, doc):
    check(f"merge_rs_piece_once:{piece.splitlines()[0][:40]}", proj.count(piece) == 1)
    proj = proj.replace(piece, "", 1)
proj = proj.replace(safety_new, safety_old, 1)
check("merge_rs_projection_byte_identical", proj == base_file(f"{S}/verify/merge.rs"))
check("specfix_registration_after_specdiag",
      "#[cfg(kani_smallsort_controls)]\nmod specdiag;\n" + reg in merge)
lines = merge.split("\n")
gl = next(i for i, l in enumerate(lines) if "value probe supports at most 128" in l)
first_read = next(i for i in range(gl, len(lines)) if "read_unaligned" in lines[i] or "*a.add" in lines[i])
check("probe_guard_before_first_read", gl < first_read, {"guard_line": gl + 1, "first_read_line": first_read + 1})

# 3. network.rs: only additions, each top-level added item under cfg(kani_smallsort_controls).
net_diff = git("diff", "-U0", BASE, "--", f"{S}/verify/network.rs")
removed = [l for l in net_diff.split("\n") if l.startswith("-") and not l.startswith("---")]
added = [l[1:] for l in net_diff.split("\n") if l.startswith("+") and not l.startswith("+++")]
check("network_rs_additions_only", not removed, removed[:3])
items = [i for i, l in enumerate(added) if re.match(r"(static|fn|impl|#\[kani)", l)]
uncfg = [added[i] for i in items if not (i > 0 and (added[i - 1].startswith("#[cfg(kani_smallsort_controls)]")
                                                  or added[i - 1].startswith("#[kani")))]
check("network_rs_added_items_cfg_gated", not uncfg, uncfg)

# 4. specfix.rs: specs never call a callback; harness inventory as manifest.
sf = cur(f"{S}/verify/merge/specfix.rs")
specs = re.findall(r"#\[kani::(?:requires|ensures|modifies)\((.*?)\)\]\n(?=#|pub|unsafe|fn)", sf, re.S)
calls = [s for s in specs if re.search(r"\bcmp\s*\(|is_less\s*\(|\(\*f\)", s)]
check("profile_specs_have_no_callback_calls", specs and not calls, {"clauses": len(specs), "calling": calls})
check("specfix_no_stub_verified_of_raw_targets",
      not re.search(r"stub_verified\(crate::slice::sort::shared::smallsort::", sf))
harn = re.findall(r"#\[kani::(?:proof|proof_for_contract\([^)]*\))\][^\n]*\n(?:#\[[^\n]*\n|  [^\n]*\n|\)\]\n)*fn (\w+)", sf)
man = json.loads((K1 / "specfix/manifest.json").read_text())
want = sorted(e["name"].rsplit("::", 1)[1] for e in man["harnesses"] if "::merge::specfix::" in e["name"])
check("specfix_harnesses_equal_manifest", sorted(harn) == want, {"source": sorted(harn), "manifest": want})

# 5. Expected-FAILED literals are unique and on their own kani::assert / requires line.
src_all = {p: cur(p) for p in (f"{S}/verify/merge.rs", f"{S}/verify/merge/specfix.rs", f"{S}/verify/network.rs")}
for e in man["harnesses"]:
    if e["expect"] != "FAILED":
        continue
    hits = [(p, i + 1) for p, t in src_all.items() for i, l in enumerate(t.split("\n")) if e["expect_check"] in l
            and ("kani::assert" in l or "kani::requires" in l)]
    fn_name = e.get("expected_location_fn")
    if fn_name:
        # A shared requires text: the hit must be in the attribute block of the replaced profile.
        t = src_all[f"{S}/verify/merge/specfix.rs"].split("\n")
        decl = next(i for i, l in enumerate(t) if re.match(rf"pub\(crate\) unsafe fn {fn_name}<", l))
        j = decl - 1
        while j >= 0 and t[j].startswith(("#[", "    ", ")]", "|")):
            j -= 1
        block = [(f"{S}/verify/merge/specfix.rs", i + 1) for i in range(j + 1, decl) if e["expect_check"] in t[i]]
        check(f"expect_check_located:{e['name'].rsplit('::', 1)[1]}", len(block) == 1,
              [f"merge/specfix.rs:{n}" for _, n in block])
    else:
        check(f"expect_check_unique:{e['name'].rsplit('::', 1)[1]}", len(hits) == 1,
              [f"{p.rsplit('/', 1)[1]}:{n}" for p, n in hits])

# 6. Requests validate, match the manifest and name harnesses present in source.
g1 = json.loads((K1 / "specfix/g1.request.json").read_text())
for g in ("g1", "g2", "g3"):
    kani_k1.validate_request(json.loads((K1 / f"specfix/{g}.request.json").read_text()))
check("g1_equals_manifest", g1["harnesses"] == [{k: v for k, v in e.items() if k in ("name", "expect", "expect_check")}
                                                for e in man["harnesses"]])
alltext = "\n".join(src_all.values())
missing = [e["name"] for e in g1["harnesses"] if not re.search(rf"fn {e['name'].rsplit('::', 1)[1]}\(", alltext)]
check("g1_names_in_source", not missing, missing)
check("g1_count_le_12", len(g1["harnesses"]) <= 12, len(g1["harnesses"]))

# 7. Line widths of changed Rust files.
wide = [f"{p.rsplit('/', 1)[1]}:{i + 1}" for p, t in src_all.items() for i, l in enumerate(t.split("\n")) if len(l) > 100]
check("rust_lines_le_100", not wide, wide)

print(json.dumps({"base": BASE, "head": git("rev-parse", "HEAD").strip(), "ok": ok, "checks": res}, indent=1))
sys.exit(0 if ok else 1)
