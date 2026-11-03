#!/usr/bin/env python3
"""ZSTPROBE static checks (no cargo/rustc/Kani): library delta, root-1 byte diff, name sets, request.

Usage: python3 -B check_zstprobe.py OUT_JSON  (run from anywhere inside the worktree)
Writes OUT_JSON and zstprobe/root1.diff; exit 1 on any failed check.
"""

import difflib
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = "e8e238db9d87323fa4da011a1a8b37fb76ec91c0"
BASE_LIBRARY_TREE = "d4ec476a7a001363e58f19948c188a9c2078e370"
V = "library/core/src/slice/sort/shared/smallsort/verify"
NET, PROBE = f"{V}/network.rs", f"{V}/network/zstprobe.rs"
PREFIX = "slice::sort::shared::smallsort::verify::network::zstprobe::"
ROOTS = [
    "zst_stable_dispatch_aware_n0_1_2_7_8_15_16_17_31_32",
    "zst_stable_dispatch_volatile_n2",
    "zst_read_volatile_dangling",
    "zst_read_volatile_local",
]
ADDED_NET = ["#[cfg(kani_smallsort_controls)]", "mod zstprobe;", ""]
STUB_ORIG = "#[kani::stub(super::super::panic_on_ord_violation, assume_order_violation)]"
STUB_PROBE = ("#[kani::stub(super::super::super::panic_on_ord_violation, "
              "super::assume_order_violation)]")
# Every line pair root 1 may differ in, as (original, copy). Anything else fails.
ALLOWED = {
    ("    use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};",
     "    use super::super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};"),
    ("        <T as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut volatile_reading_less::<T>);",
     "        <T as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut zst_aware_less::<T>);"),
    ("        " + STUB_ORIG, "        " + STUB_PROBE),
    ("    dispatch_safety_stable_zst_n0_1_2_7_8_15_16_17_31_32,",
     "    zst_stable_dispatch_aware_n0_1_2_7_8_15_16_17_31_32,"),
}
# rustfmt joins the stable call onto one line once the comparator name is shorter.
STABLE_ORIG = ["        <T as StableSmallSortTypeImpl>::small_sort(", "            &mut v,",
               "            &mut scratch,", "            &mut volatile_reading_less::<T>,", "        );"]
STABLE_PROBE = ["        <T as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, "
                "&mut zst_aware_less::<T>);"]


def git(*args: str) -> str:
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True,
                         text=True).stdout.strip()
    return subprocess.run(["git", "-C", top, *args], check=True, capture_output=True, text=True).stdout


def segment(lines: list[str], start: str, end: str) -> list[str]:
    i = lines.index(start)
    j = lines.index(end, i)
    return lines[i:j + 1]


def main() -> int:
    root = Path(git("rev-parse", "--show-toplevel").strip())
    out = Path(sys.argv[1]).resolve()
    errors: list[str] = []
    res: dict = {"base": BASE}

    tree = git("rev-parse", f"{BASE}:library").strip()
    if tree != BASE_LIBRARY_TREE:
        errors.append(f"base library tree {tree}")
    # Library delta of the working tree against the base (committed or not).
    changed = sorted(git("diff", "--name-only", BASE, "--", "library").split())
    untracked = sorted(git("ls-files", "--others", "--exclude-standard", "--", "library").split())
    res["library_changed"] = changed + untracked
    if sorted(changed + untracked) != sorted([NET, PROBE]):
        errors.append(f"library delta {changed + untracked}")

    base_net = git("show", f"{BASE}:{NET}").splitlines()
    head_net = (root / NET).read_text().splitlines()
    # Exactly three lines inserted (gate, mod, blank) and nothing else changed.
    k = head_net.index("mod zstprobe;")
    res["network_rs_inserted"] = head_net[k - 1:k + 2]
    if head_net[k - 1:k + 2] != ADDED_NET or head_net[:k - 1] + head_net[k + 2:] != base_net:
        errors.append("network.rs delta is not exactly the cfg-gated mod line")

    probe_text = (root / PROBE).read_text()
    probe = probe_text.splitlines()
    res["zstprobe_rs_sha256"] = hashlib.sha256(probe_text.encode()).hexdigest()
    res["network_rs_sha256"] = hashlib.sha256((root / NET).read_bytes()).hexdigest()
    res["network_rs_base_blob"] = git("rev-parse", f"{BASE}:{NET}").strip()

    # Root 1 byte diff: dispatch_safety_fixed + dispatch_safety_cases + the stable ZST invocation.
    fn_start = "fn dispatch_safety_fixed<T: ArbitraryValue, const N: usize, const STABLE: bool>() {"
    orig = (segment(base_net, fn_start, "}")
            + [""] + segment(base_net, "macro_rules! dispatch_safety_cases {", "}")
            + [""] + segment(base_net, "dispatch_safety_cases!(", ");"))
    copy = (segment(probe, fn_start, "}")
            + [""] + segment(probe, "macro_rules! dispatch_safety_cases {", "}")
            + [""] + segment(probe, "dispatch_safety_cases!(", ");"))
    # segment() stops at the first bare "}" / ");": the fn and macro end at column 0.
    diff = list(difflib.unified_diff(orig, copy, f"base:{NET}", PROBE, lineterm="", n=1))
    (out.parent / "root1.diff").write_text("\n".join(diff) + "\n")
    sm = difflib.SequenceMatcher(a=orig, b=copy, autojunk=False)
    pairs, unexplained = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        a, b = orig[i1:i2], copy[j1:j2]
        if a == STABLE_ORIG and b == STABLE_PROBE:
            pairs.append("stable call: volatile_reading_less -> zst_aware_less (rustfmt joins lines)")
        elif tag == "replace" and len(a) == len(b) and all(p in ALLOWED for p in zip(a, b)):
            pairs += [f"{x.strip()} -> {y.strip()}" for x, y in zip(a, b)]
        else:
            unexplained.append({"orig": a, "copy": b})
    res["root1_diff_pairs"], res["root1_unexplained"] = pairs, unexplained
    res["root1_compared_lines"] = [len(orig), len(copy)]
    if unexplained:
        errors.append("root 1 differs beyond comparator/module-depth paths/name")

    # Harness name set: macro invocation(s) plus #[kani::proof] fns. No contracts, no new stubs.
    names = re.findall(r"^dispatch_safety_cases!\(\n    (\w+),", probe_text, re.M)
    names += re.findall(r"^#\[kani::proof\]\n(?:#\[kani::[^\n]*\]\n)*fn (\w+)\(", probe_text, re.M)
    res["new_controls_harnesses"] = [PREFIX + n for n in names]
    if names != ROOTS:
        errors.append(f"harness names {names}")
    if "proof_for_contract" in probe_text:
        errors.append("zstprobe has proof_for_contract")
    stubs = re.findall(r"#\[kani::stub\([^\n]*\)\]", probe_text)
    res["stub_lines"] = len(stubs)
    if set(s for s in stubs) != {STUB_PROBE}:
        errors.append(f"stubs {stubs}")
    for bad in ("kani::assume", "any_where(|_|", "#[cfg(not"):
        if bad in probe_text:
            errors.append(f"forbidden token {bad}")
    long = [i + 1 for i, l in enumerate(probe) if len(l) > 100]
    if long:
        errors.append(f"lines > 100: {long}")
    # Ordinary and PFC sets: the only library change is behind kani_smallsort_controls.
    res["ordinary_delta"], res["pfc_delta"] = 0, 0
    res["controls_delta"] = len(names)

    req = root / "research/challenge-8/kani-k1/RUN-REQUEST.json"
    pkt = root / "research/challenge-8/kani-k1/zstprobe/request.json"
    res["request_sha256"] = hashlib.sha256(req.read_bytes()).hexdigest()
    if req.read_bytes() != pkt.read_bytes():
        errors.append("RUN-REQUEST.json != zstprobe/request.json")
    data = json.loads(req.read_text())
    if [h["name"] for h in data["harnesses"]] != [PREFIX + n for n in ROOTS]:
        errors.append("request harness list")
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
    if res["envelope_usd"] > 1.00:
        errors.append("envelope over own cap $1.00")

    res["status"], res["errors"] = ("PASS" if not errors else "FAIL"), errors
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(res["status"], errors)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
