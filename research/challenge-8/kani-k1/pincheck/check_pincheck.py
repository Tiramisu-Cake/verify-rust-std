#!/usr/bin/env python3
"""PINCHECK static checks (no rustc/cargo/Kani/CBMC).

Reuses the TRIMPART source model (check_trimpart.py at 120e443536, loaded from git) to list proof
roots of the verify tree with the controls cfg off and on, base e470652790 against the working
tree (or --head REV). Also checks the library diff scope and that copied fixtures are unchanged.
Usage (repository root): python3 -I research/challenge-8/kani-k1/pincheck/check_pincheck.py [--head REV]
Prints a JSON report; exit 1 if any check fails.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
BASE = "e470652790"
TRIMPART = "120e443536"
VERIFY = "library/core/src/slice/sort/shared/smallsort/verify"
NEW = f"{VERIFY}/pincheck.rs"
PREFIX = "slice::sort::shared::smallsort::verify::"
NEW_ROOTS = {
    "pincheck::casefive_d1_select_read_bytes1",
    "pincheck::casefive_d2_select_read_u8",
    "pincheck::arrayfactor_f5_symbolic_indices_bytes1",
    "pincheck::pincheck_calibration_uninit_read_u8",
    "pincheck::pincheck_calibration_init_read_u8",
    "pincheck::raw_uninit_read_sensitivity",
}
# (source rev, path, first line, last line) -> must appear verbatim in pincheck.rs
COPIES = [
    ("d558b986c6", f"{VERIFY}/merge/casefive.rs", 638, 674, 0),     # D1, D2 with doc comments
    ("4da5ec554a", f"{VERIFY}/merge/specdiag.rs", 320, 328, 0),     # SPECDIAG row 17
    ("42ead2dba6", "array-select-standalone/src/lib.rs", 62, 80, 4),  # F5 body, de-indented 4
]


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args], check=True, capture_output=True,
                          text=True).stdout


def load_trimpart():
    src = git("show", f"{TRIMPART}:research/challenge-8/kani-k1/trimpart/check_trimpart.py")
    tmp = Path(tempfile.mkdtemp()) / "r/c/k/t/check_trimpart.py"  # parents[3] must exist
    tmp.parent.mkdir(parents=True)
    tmp.write_text(src)
    spec = importlib.util.spec_from_file_location("check_trimpart", tmp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.REPO = REPO
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", default=None)
    head = ap.parse_args().head
    ct = load_trimpart()
    base, cur = ct.Source(BASE), ct.Source(head)
    rep: dict = {"base": git("rev-parse", BASE).strip(), "head": head or "working tree"}
    ok = True
    b_off, b_on = set(base.roots(False)), set(base.roots(True))
    h_off, h_on = set(cur.roots(False)), set(cur.roots(True))
    rep["ordinary"] = {"base": len(b_off), "head": len(h_off), "equal": b_off == h_off}
    rep["cfg_on"] = {"base": len(b_on), "head": len(h_on), "added": sorted(h_on - b_on),
                     "removed": sorted(b_on - h_on)}
    ok &= b_off == h_off and len(h_off) == 202
    ok &= h_on - b_on == NEW_ROOTS and not (b_on - h_on) and len(b_on) == 210
    # ordinary set equals the TRIMPART expected list
    exp = {l.strip()[len(PREFIX):] for l in git("show", f"{TRIMPART}:research/challenge-8/kani-k1/trimpart/ordinary-expected.txt").splitlines() if l.strip()}
    rep["ordinary"]["equals_trimpart_expected"] = h_off == exp
    ok &= h_off == exp
    # diff scope
    diff_args = ["diff", "--name-status", BASE] + ([head] if head else []) + ["--", "library"]
    names = git(*diff_args).split("\n")
    names = [n for n in names if n]
    rep["diff_scope"] = names
    ok &= sorted(names) == sorted([f"A\t{NEW}", f"M\t{VERIFY}.rs"]) or (
        head is None and sorted(n.split("\t")[1] for n in names) == sorted([NEW, f"{VERIFY}.rs"]))
    vdiff = git(*(["diff", "-U0", BASE] + ([head] if head else []) + ["--", f"{VERIFY}.rs"]))
    added = [l[1:] for l in vdiff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in vdiff.splitlines() if l.startswith("-") and not l.startswith("---")]
    rep["verify_rs_added"] = added
    ok &= added == ["#[cfg(kani_smallsort_controls)]", "mod pincheck;"] and not removed
    text = git("show", f"{head}:{NEW}") if head else (REPO / NEW).read_text()
    copies = []
    for rev, path, a, b, dedent in COPIES:
        lines = git("show", f"{rev}:{path}").splitlines()[a - 1:b]
        block = "\n".join(l[dedent:] if l.startswith(" " * dedent) else l for l in lines)
        copies.append({"source": f"{rev}:{path}:{a}-{b}", "verbatim": block in text})
        ok &= block in text
    rep["copies"] = copies
    rep["kani_assert_messages_unique"] = len(set(m := [l.split('"')[1] for l in text.splitlines() if "kani::assert(" in l or "kani::cover(" in l and '"' in l])) == len(m)
    rep["ok"] = bool(ok)
    print(json.dumps(rep, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
