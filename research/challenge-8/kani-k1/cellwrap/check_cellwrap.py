#!/usr/bin/env python3
"""CELLWRAP static gate. Usage: python3 -I check_cellwrap.py [OUT_JSON]. Read-only git/source checks.

Base e0fda080f5 (v6 library tree). Library delta must be exactly the new opt-in child
verify/wrap/cellwrap.rs plus the appended `#[cfg(kani_smallsort_controls)] mod cellwrap;` in wrap.rs.
Static name sets reuse poneclean/source_sets.py with the wrap modules added; native kani list is
the authority, this is a source forecast.
"""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
K1 = HERE.parent
REPO = K1.parents[2]
BASE = "e0fda080f5ea479d8f4fb801f4b42adde2b3259f"
V = "library/core/src/slice/sort/shared/smallsort/verify"
WRAP, CHILD = f"{V}/wrap.rs", f"{V}/wrap/cellwrap.rs"
PREFIX = "slice::sort::shared::smallsort::verify::wrap::cellwrap::"
ROOTS = ["cellwrap_stable_tags_n2", "cellwrap_tag_corruption_control",
         "cellwrap_wrong_comparator_control"]


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True,
                          check=True).stdout


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, K1 / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def source_sets(rev, with_child):
    ss = load(f"ss_{rev}_{with_child}", "poneclean/source_sets.py")
    ss.MODULES.append(("wrap", "wrap.rs", "ordinary"))
    if with_child:
        ss.MODULES.append(("wrap::cellwrap", "wrap/cellwrap.rs", "controls"))
    return ss.sets(rev)


def main():
    checks = []

    def check(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    changed = git("diff", "--name-status", BASE, "--", "library").split("\n")
    changed = sorted(line for line in changed if line)
    check("library delta = wrap.rs (M) + wrap/cellwrap.rs (A)",
          changed == sorted([f"M\t{WRAP}", f"A\t{CHILD}"]), changed)

    base_wrap = git("show", f"{BASE}:{WRAP}")
    wrap = (REPO / WRAP).read_text()
    check("wrap.rs = base + appended cfg-gated mod line",
          wrap == base_wrap + "\n#[cfg(kani_smallsort_controls)]\nmod cellwrap;\n")
    check("wrap.rs:61 guard literal unchanged",
          wrap.splitlines()[60] == '    kani::assert(ok, "wrap canonical comparator required");')

    child = (REPO / CHILD).read_text()
    lines = child.splitlines()
    check("cellwrap.rs lines <= 100", all(len(x) <= 100 for x in lines))
    check("no cfg inside child (module gate only)", "#[cfg" not in child)
    check("no stub / stub_verified", "stub" not in child)
    ens = [i + 1 for i, x in enumerate(lines) if x.startswith("#[kani::ensures")]
    ens_text = "#[kani::ensures(|_| old(pair_tag_count(v, probe)) == pair_tag_count(v, probe))]"
    check("exactly two one-line ensures, both the tag-count line",
          len(ens) == 2 and all(lines[i - 1] == ens_text for i in ens), ens)
    check("expect_check 'pair_tag_count(v, probe)' only in ensures/helper lines",
          [i + 1 for i, x in enumerate(lines) if "pair_tag_count(v, probe)" in x] == ens)
    check("guard literal not duplicated in child", "comparator required" not in child)
    pfc = re.findall(r"proof_for_contract\((\w+)\)\]\n#\[kani::unwind\(16\)\]\nfn (\w+)", child)
    check("PFC roots/targets", pfc == [("cellwrap_stable", ROOTS[0]),
                                       ("cellwrap_stable_tag_corruption", ROOTS[1])], pfc)
    check("plain control root", re.search(
        r"#\[kani::proof\]\n#\[kani::unwind\(16\)\]\nfn cellwrap_wrong_comparator_control", child))

    # The two wrappers differ only in name and the trailing two-line tag flip.
    def item(name):
        start = child.index(f"unsafe fn {name}(")
        attrs_start = child.rindex("\n\n", 0, start)
        body_end = child.index("\n}\n", start) + 3
        return child[attrs_start:body_end]
    pos, mut = item("cellwrap_stable"), item("cellwrap_stable_tag_corruption")
    pos_attrs = pos[pos.index("#[kani::requires"):]
    mut_attrs = mut[mut.index("#[kani::requires"):]
    flip = ("    let first = v[0].get();\n"
            "    v[0].set(TaggedKey { key: first.key, tag: first.tag ^ 1 });\n")
    check("mutant = positive wrapper + tag flip only", mut_attrs.replace(
        "cellwrap_stable_tag_corruption(", "cellwrap_stable(").replace(flip, "") == pos_attrs)

    # Comparator body = network.rs mutating_key_order body (name, type alias and cover text differ).
    net = git("show", f"{BASE}:{V}/network.rs")
    nb = net[net.index("fn mutating_key_order("):]
    nb = nb[:nb.index("\n}\n") + 3]
    cb = child[child.index("fn cellwrap_key_order("):]
    cb = cb[:cb.index("\n}\n") + 3]
    norm = (nb.replace("mutating_key_order", "cellwrap_key_order")
            .replace("TaggedKeyCell", "Cell<TaggedKey>")
            .replace('"mutating comparator changes both keys"',
                     '"cellwrap comparator changes both keys"'))
    check("comparator = network.rs mutating_key_order modulo name/alias/cover text", norm == cb)
    tk = "#[derive(Clone, Copy)]\nstruct TaggedKey {\n    key: u8,\n    tag: u8,\n}\n"
    check("TaggedKey layout = network.rs", tk in net and tk in child)

    base = source_sets(BASE, False)
    new = source_sets(None, True)
    ordinary_ref = sorted((K1 / "macsplit/ordinary-expected.txt").read_text().split())
    check("ordinary unchanged = macsplit 202", new["ordinary"] == base["ordinary"] == ordinary_ref,
          len(new["ordinary"]))
    pfc_base = sum(1 for r in base["records"] if r["cls"] == "ordinary" and r["pfc"])
    pfc_new = sum(1 for r in new["records"] if r["cls"] == "ordinary" and r["pfc"])
    check("ordinary PFC 36 unchanged", pfc_base == pfc_new == 36, pfc_new)
    plus = sorted(set(new["cfg_on"]) - set(base["cfg_on"]))
    minus = sorted(set(base["cfg_on"]) - set(new["cfg_on"]))
    check("cfg-on exact delta +3", plus == sorted(PREFIX + r for r in ROOTS) and not minus
          and len(new["cfg_on"]) == len(base["cfg_on"]) + 3, [len(base["cfg_on"]),
                                                               len(new["cfg_on"])])
    check("retired unchanged", new["retired"] == base["retired"])
    (HERE / "cfg-on-expected.txt").write_text("\n".join(new["cfg_on"]) + "\n")

    req = json.loads((HERE / "g1.request.json").read_text())
    names = [h["name"] for h in req["harnesses"]]
    check("request rows = the 3 roots in order", names == [PREFIX + r for r in ROOTS])
    check("RUN-REQUEST.json = g1.request.json",
          (K1 / "RUN-REQUEST.json").read_bytes() == (HERE / "g1.request.json").read_bytes())

    out = {"base": BASE, "ok": all(c["ok"] for c in checks),
           "passed": sum(c["ok"] for c in checks), "total": len(checks),
           "cfg_on": len(new["cfg_on"]), "ordinary": len(new["ordinary"]), "checks": checks}
    text = json.dumps(out, indent=1)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(text + "\n")
    print(json.dumps({k: out[k] for k in ("ok", "passed", "total", "ordinary", "cfg_on")}))
    for c in checks:
        if not c["ok"]:
            print("FAIL", c["check"], c["detail"])
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
