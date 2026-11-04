#!/usr/bin/env python3
"""TYPEUXVI static checks (no cargo/rustc/Kani): library delta, the appended u16 section (ArbitraryValue, const
asserts, 7 roots), cell correspondence with the seven `(u8, u32)` v7 candidates, covers, name sets, lane files,
request.

Usage: python3 -B check_typeuxvi.py OUT_JSON  (run from anywhere inside the worktree)
Writes OUT_JSON; exit 1 on any failed check.
"""

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

LIB_BASE = "b1ff545720"  # TYPESPLIT result: library = v6 + network::typematrix (22 roots)
TOOL_BASE = "e0fda080f5ea479d8f4fb801f4b42adde2b3259f"  # K-1 tooling base for check-tooling (cap $98.96)
V = "library/core/src/slice/sort/shared/smallsort/verify"
NET, MOD = f"{V}/network.rs", f"{V}/network/typematrix.rs"
PREFIX = "slice::sort::shared::smallsort::verify::network::typematrix::"
PAIR, SINGLE = "dispatch_pair_safety_cases", "dispatch_safety_cases"
# (macro, root, type, stable literal or None, lengths), in source order
NEW = [(PAIR, "dispatch_safety_stable_unstable_u16_n0_1_2_7_8", "u16", None, [0, 1, 2, 7, 8]),
       (PAIR, "dispatch_safety_stable_unstable_u16_n15_16_17", "u16", None, [15, 16, 17]),
       (SINGLE, "dispatch_safety_unstable_u16_n9_12_13_18", "u16", "false", [9, 12, 13, 18])] + \
      [(SINGLE, f"dispatch_safety_{r}_u16_n{n}", "u16", lit, [n])
       for r, lit in (("stable", "true"), ("unstable", "false")) for n in (31, 32)]
# The seven (u8, u32) v7 candidates (TYPEMATRIX 3 + TYPESPLIT 4): u16 must get the same shapes.
U8U32 = ["dispatch_safety_stable_unstable_u8u32_n0_1_2_7_8", "dispatch_safety_stable_unstable_u8u32_n15_16_17",
         "dispatch_safety_unstable_u8u32_n9_12_13_18", "dispatch_safety_stable_u8u32_n31",
         "dispatch_safety_stable_u8u32_n32", "dispatch_safety_unstable_u8u32_n31", "dispatch_safety_unstable_u8u32_n32"]
# Everything appended except comments and the root invocations, byte for byte.
EXPECTED_BODY = """const _: () = {
    use super::super::super::{
        MAX_STACK_ARRAY_SIZE, SMALL_SORT_NETWORK_SCRATCH_LEN, has_efficient_in_place_swap,
    };
    use crate::mem::{align_of, size_of};
    if cfg!(any(target_arch = "x86_64", target_arch = "aarch64")) {
        assert!(size_of::<u16>() == 2 && align_of::<u16>() == 2);
        assert!(has_efficient_in_place_swap::<u16>());
        assert!(size_of::<u16>() * SMALL_SORT_NETWORK_SCRATCH_LEN <= MAX_STACK_ARRAY_SIZE);
    }
};
impl ArbitraryValue for u16 {
    fn arbitrary_value() -> Self {
        kani::any()
    }
}
"""
LANE_PATHS = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools", "research/challenge-8/kani-k1/gcb",
              "scripts/run-kani.sh", "tool_config/kani-version.toml", "rust-toolchain.toml", ".gitmodules", ".cargo",
              "library/.cargo", "library/Cargo.toml", "library/Cargo.lock"]
FMT = "/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad"
OWN_CAP = 1.40
INV_RE = re.compile(r"^(dispatch_(?:pair_)?safety_cases)!\(\s*(\w+),\s*(\(u8, u32\)|u128|u16|\[u8; 9\]),"
                    r"\s*(?:(true|false),\s*)?\[([\d, ]+)\],?\s*\);", re.M)


def git(*args: str, text: bool = True):
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True,
                         text=True).stdout.strip()
    return subprocess.run(["git", "-C", top, *args], check=True, capture_output=True, text=text).stdout


def load_inventory(root: Path):
    """cleanup/source_inventory.py imported (its main() and report file are not used), pointed at ROOT."""
    here = root / "research/challenge-8/kani-k1/cleanup/source_inventory.py"
    spec = importlib.util.spec_from_file_location("typeuxvi_source_inventory", here)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def names_at(mod, repo: Path, controls: bool) -> list[str]:
    mod.REPO = repo
    mod.SOURCE_ROOT = repo / "library/core/src/slice/sort/shared/smallsort/verify.rs"
    items, _files = mod.inventory(controls=controls)
    return [i["name"] for i in items]


def invocations(text: str):
    return [(m, n, t, s or None, [int(x) for x in ls.split(",")]) for m, n, t, s, ls in INV_RE.findall(text)]


def cells(stable, lengths):
    """(route, len) cells a root covers: pair = both routes per length, single = its route per length."""
    routes = ["stable", "unstable"] if stable is None else ["stable" if stable == "true" else "unstable"]
    return sorted((r, n) for r in routes for n in lengths)


def covers(stable, lengths):
    """Cover labels the local macros emit (see typematrix.rs), in macro order."""
    if stable is None:
        out = [f"{r} route normal return at {n}" for n in lengths for r in ("stable", "unstable")]
        return out + ["dispatch family reached the end"]
    return [f"dispatch route returns normally at {n}" for n in lengths] + ["dispatch safety family reached the end"]


def main() -> int:
    root = Path(git("rev-parse", "--show-toplevel").strip())
    out = Path(sys.argv[1]).resolve()
    errors: list[str] = []
    res: dict = {"lib_base": git("rev-parse", LIB_BASE).strip(), "tool_base": TOOL_BASE,
                 "head": git("rev-parse", "HEAD").strip()}

    # Library: against TYPESPLIT only typematrix.rs, and only text appended after its 150 lines.
    changed = sorted(git("diff", "--name-only", LIB_BASE, "--", "library").split())
    untracked = sorted(git("ls-files", "--others", "--exclude-standard", "--", "library").split())
    res["library_changed_vs_lib_base"] = sorted(changed + untracked)
    if res["library_changed_vs_lib_base"] != [MOD]:
        errors.append(f"library delta {res['library_changed_vs_lib_base']}")
    res["library_changed_vs_tool_base"] = sorted(git("diff", "--name-only", TOOL_BASE, "--", "library").split())
    if res["library_changed_vs_tool_base"] != sorted([NET, MOD]):
        errors.append("library delta vs tooling base")
    base_text = git("show", f"{LIB_BASE}:{MOD}")
    text = (root / MOD).read_text()
    res["typematrix_rs_base_lines"] = len(base_text.splitlines())
    res["typematrix_rs_lines"] = len(text.splitlines())
    res["typematrix_rs_sha256"] = hashlib.sha256(text.encode()).hexdigest()
    res["typematrix_rs_base_blob"] = git("rev-parse", f"{LIB_BASE}:{MOD}").strip()
    if not text.startswith(base_text):
        errors.append("typematrix.rs: existing 150 lines (roots, macros, impls, const asserts) changed")
    added = text[len(base_text):]
    res["appended_lines"] = len(added.splitlines())
    for bad in ("macro_rules!", "kani::assume", "proof_for_contract", "#[", "stub_verified", "unsafe"):
        if bad in added:
            errors.append(f"forbidden token in appended part: {bad}")
    body = "".join(l + "\n" for l in INV_RE.sub("", added).splitlines()
                   if l.strip() and not l.lstrip().startswith("//"))
    res["appended_non_root_body_exact"] = body == EXPECTED_BODY
    if body != EXPECTED_BODY:
        errors.append("appended const block / impl differ from the expected text")
    long = [i + 1 for i, l in enumerate(text.splitlines()) if len(l) > 100]
    if long:
        errors.append(f"lines > 100: {long}")
    if "ArbitraryValue for u16" in base_text or len(re.findall(r"ArbitraryValue for u16\b", text)) != 1:
        errors.append("u16 impl count")

    # Roots: the old 22 unchanged, the new seven via the existing local macros.
    old = invocations(base_text)
    allr = invocations(text)
    new = allr[len(old):]
    if allr[:len(old)] != old or len(old) != 22:
        errors.append("existing invocations")
    if len(re.findall(r"^dispatch_(?:pair_)?safety_cases!\(", text, re.M)) != len(allr):
        errors.append("unparsed invocations")
    if new != NEW:
        errors.append(f"new invocations {new}")
    res["new_roots"] = [{"macro": m, "name": n, "type": t, "stable": s, "lengths": ls, "cells": cells(s, ls),
                         "covers": covers(s, ls)} for m, n, t, s, ls in new]
    res["new_covers_total"] = sum(len(r["covers"]) for r in res["new_roots"])
    if res["new_covers_total"] != 31:
        errors.append("new covers != 31")

    # Cell correspondence: root by root the u16 shapes equal the seven (u8, u32) candidates.
    by_name = {n: (m, t, s, ls) for m, n, t, s, ls in allr}
    corr = []
    for (m, n, _t, s, ls), ref in zip(NEW, U8U32):
        rm, rt, rs, rls = by_name[ref]
        same = (m, s, ls) == (rm, rs, rls) and rt == "(u8, u32)" and n.replace("u16", "u8u32") == ref
        corr.append({"u16_root": n, "u8u32_root": ref, "macro": m, "stable": s, "lengths": ls, "same_shape": same})
        if not same:
            errors.append(f"shape differs: {n} vs {ref}")
    u16_cells = [tuple(c) for r in res["new_roots"] for c in r["cells"]]
    ref_cells = [tuple(c) for ref in U8U32 for c in cells(by_name[ref][2], by_name[ref][3])]
    res["cell_correspondence"] = corr
    res["u16_cells"] = {"stable": sorted(n for r, n in u16_cells if r == "stable"),
                        "unstable": sorted(n for r, n in u16_cells if r == "unstable"),
                        "total": len(u16_cells), "distinct": len(set(u16_cells)),
                        "equal_to_u8u32_candidates": sorted(u16_cells) == sorted(ref_cells)}
    if sorted(u16_cells) != sorted(ref_cells) or len(set(u16_cells)) != len(u16_cells) or len(u16_cells) != 24:
        errors.append("u16 cells")

    # Name sets, TYPESPLIT base vs head, with the static source inventory of CLEANUP.
    inv = load_inventory(root)
    with tempfile.TemporaryDirectory() as tmp:
        arch = Path(tmp) / "base.tar"
        arch.write_bytes(git("archive", LIB_BASE, "library/core/src/slice/sort/shared/smallsort", text=False))
        with tarfile.open(arch) as t:
            t.extractall(Path(tmp) / "base", filter="data")
        base_ord = names_at(inv, Path(tmp) / "base", False)
        base_on = names_at(inv, Path(tmp) / "base", True)
    head_ord = names_at(inv, root, False)
    head_on = names_at(inv, root, True)
    res["ordinary_count"] = [len(base_ord), len(head_ord)]
    res["controls_on_count"] = [len(base_on), len(head_on)]
    res["ordinary_delta"] = sorted(set(head_ord) ^ set(base_ord))
    res["controls_on_added"] = sorted(set(head_on) - set(base_on))
    res["controls_on_removed"] = sorted(set(base_on) - set(head_on))
    if base_ord != head_ord or len(head_ord) != 202:
        errors.append("ordinary set changed or != 202")
    if res["controls_on_added"] != sorted(PREFIX + r[1] for r in NEW) or res["controls_on_removed"]:
        errors.append("controls-on delta is not exactly +7")
    # PFC 36: every other library file is byte-identical to TYPESPLIT and typematrix.rs has no proof_for_contract.
    res["pfc_delta"] = 0 if "proof_for_contract" not in text else "ERR"

    # Lane files at HEAD equal the tooling base (what `k1g.sh check-tooling BUILD e0fda080f5` compares).
    lane = git("diff", "--name-only", TOOL_BASE, "HEAD", "--", *LANE_PATHS).split()
    res["lane_files_changed_vs_tool_base"] = lane
    if lane:
        errors.append(f"lane files differ from tooling base: {lane}")

    fmt = subprocess.run([f"{FMT}/rustfmt.sh", "--check", "--edition", "2024", "--config-path",
                          f"{FMT}/fmtcfg/rustfmt.toml", str(root / MOD)], capture_output=True, text=True)
    res["rustfmt_check_rc"] = fmt.returncode
    if fmt.returncode != 0:
        errors.append("rustfmt --check")

    req = root / "research/challenge-8/kani-k1/RUN-REQUEST.json"
    pkt = root / "research/challenge-8/kani-k1/typeuxvi/request.json"
    res["request_sha256"] = hashlib.sha256(req.read_bytes()).hexdigest()
    if req.read_bytes() != pkt.read_bytes():
        errors.append("RUN-REQUEST.json != typeuxvi/request.json")
    data = json.loads(req.read_text())
    if [h["name"] for h in data["harnesses"]] != [PREFIX + r[1] for r in NEW]:
        errors.append("request harness list")
    if {h["expect"] for h in data["harnesses"]} != {"SUCCESS"} or data["kind"] != "measurement":
        errors.append("request kind/expect")
    if (data["agent"], data["runner"], data["controls"], data["kani_jobs"], data["uninit_checks"],
            data["harness_timeout_minutes"]) != ("k1-network", "gcb-e2-standard-4", True, 1, False, 10):
        errors.append("request profile")
    if not data["request_id"].startswith("typeuxvi-"):
        errors.append("request_id prefix")
    with tempfile.TemporaryDirectory() as tmp:
        v = subprocess.run(["python3", "-B", str(root / "research/challenge-8/kani-k1/tools/kani_k1.py"),
                            "validate", str(req), "--args-out", f"{tmp}/args", "--runner-out",
                            f"{tmp}/runner", "--rustflags-out", f"{tmp}/rustflags",
                            "--require-runner", "gcb-e2-standard-4", "--max-total-minutes", "720"],
                           capture_output=True, text=True)
        res["validate_rc"] = v.returncode
        if v.returncode == 0:
            res["kani_args"] = Path(f"{tmp}/args").read_text().split("\n")
            res["rustflags"] = Path(f"{tmp}/rustflags").read_text().strip()
        else:
            errors.append(f"validate: {v.stderr.strip()[:300]}")
    minutes = len(data["harnesses"]) * data["harness_timeout_minutes"] + 30
    res["envelope_minutes"], res["envelope_usd"] = minutes, round(minutes * 0.0135, 4)
    if res["envelope_usd"] > OWN_CAP:
        errors.append(f"envelope over own cap ${OWN_CAP}")

    res["status"], res["errors"] = ("PASS" if not errors else "FAIL"), errors
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(res["status"], errors)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
