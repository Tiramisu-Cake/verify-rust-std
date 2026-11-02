#!/usr/bin/env python3
"""PART2-SPLIT31 static source-inventory delta: base MACSPLIT vs candidate (source-level forecast only).

Reuses cleanup/source_inventory.py without running its main (which writes cleanup/ files).
Usage: static_check.py BASE_SMALLSORT_DIR_ROOT OUT_JSON
BASE_SMALLSORT_DIR_ROOT is a directory holding a `git archive` of the base library smallsort tree
(laid out as library/core/src/slice/sort/shared/smallsort...).
"""
import importlib.util, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("si", HERE.parent / "cleanup/source_inventory.py")
si = importlib.util.module_from_spec(spec); spec.loader.exec_module(si)
REL = "library/core/src/slice/sort/shared/smallsort/verify.rs"
P = si.PREFIX + "network::"
NEW = {P + "dispatch_safety_stable_bytes17_n31", P + "dispatch_safety_unstable_bytes17_n31"}


def inv(repo: Path, controls: bool):
    si.REPO, si.SOURCE_ROOT = repo, repo / REL
    items, _ = si.inventory(controls)
    return {i["name"]: i for i in items}


def main():
    base_repo, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    cand_repo = HERE.parents[3]
    r = {}
    for controls, label in ((False, "ordinary"), (True, "cfg_on")):
        b, c = inv(base_repo, controls), inv(cand_repo, controls)
        r[label] = dict(base=len(b), candidate=len(c), added=sorted(set(c) - set(b)),
                        removed=sorted(set(b) - set(c)))
    ordinary = set(inv(cand_repo, False))
    exp = set((HERE.parent / "macsplit/ordinary-expected.txt").read_text().split())
    r["ordinary_vs_macsplit_native_reference"] = dict(
        expected=len(exp), set_equal=ordinary == exp, missing=sorted(exp - ordinary), extra=sorted(ordinary - exp))
    cand_on = inv(cand_repo, True)
    r["new_roots"] = {n: dict(source=cand_on[n]["source"], line=cand_on[n]["line"], gates=cand_on[n]["gates"])
                      for n in sorted(NEW)}
    r["pass"] = (r["ordinary"]["added"] == [] and r["ordinary"]["removed"] == []
                 and set(r["cfg_on"]["added"]) == NEW and r["cfg_on"]["removed"] == []
                 and r["cfg_on"]["candidate"] == r["cfg_on"]["base"] + 2
                 and r["ordinary_vs_macsplit_native_reference"]["set_equal"]
                 and all(v["gates"] == ["kani_smallsort_controls"] for v in r["new_roots"].values()))
    out.write_text(json.dumps(r, indent=2) + "\n")
    print(json.dumps({k: (v if k in ("pass",) else {kk: vv for kk, vv in v.items() if kk in ("base", "candidate", "added", "removed", "set_equal", "expected")} if isinstance(v, dict) and k != "new_roots" else v) for k, v in r.items()}, indent=1))
    return 0 if r["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
