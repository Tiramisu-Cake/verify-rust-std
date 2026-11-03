#!/usr/bin/env python3
"""UNSTABLEZST static checks (no cargo/rustc/Kani): library delta, root-1 semantic diff, name sets, request.

Usage: python3 -B check_unstablezst.py OUT_JSON  (run from anywhere inside the worktree)
Writes OUT_JSON and unstablezst/root1.diff; exit 1 on any failed check.
"""

import difflib
import hashlib
import importlib.util
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

BASE = "5fc77d446f1d17eb7be227dc1d604ba40d01477b"  # ZSTPROBE result, branch base
V = "library/core/src/slice/sort/shared/smallsort/verify"
NET, PROBE = f"{V}/network.rs", f"{V}/network/zstprobe.rs"
PREFIX = "slice::sort::shared::smallsort::verify::network::zstprobe::"
ORIG_ROOT = "slice::sort::shared::smallsort::verify::network::dispatch_safety_unstable_zst_n8_9_12_13_17"
LENGTHS = [8, 9, 12, 13, 17]
ROOTS = ["zst_unstable_dispatch_aware_n8_9_12_13_17"] + [f"zst_unstable_dispatch_aware_n{n}" for n in LENGTHS]
INSERTED = [
    "",
    "// UNSTABLEZST: `dispatch_safety_unstable_zst_n8_9_12_13_17` with `zst_aware_less` as the only",
    "// change, as one family and per length.",
    "dispatch_safety_cases!(zst_unstable_dispatch_aware_n8_9_12_13_17, (), false, [8, 9, 12, 13, 17]);",
] + [f"dispatch_safety_cases!(zst_unstable_dispatch_aware_n{n}, (), false, [{n}]);" for n in LENGTHS]
ORIG_CALL = "dispatch_safety_cases!(dispatch_safety_unstable_zst_n8_9_12_13_17, (), false, [8, 9, 12, 13, 17]);"
STUB_ORIG = "#[kani::stub(super::super::panic_on_ord_violation, assume_order_violation)]"
STUB_PROBE = "#[kani::stub(super::super::super::panic_on_ord_violation, super::assume_order_violation)]"
# Every line pair root 1 may differ in, as (original, copy), with its reason. Anything else fails.
ALLOWED = {
    ("    use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};",
     "    use super::super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};"): "module depth",
    ("        <T as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut volatile_reading_less::<T>);",
     "        <T as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut zst_aware_less::<T>);"):
        "comparator (live branch at STABLE = false)",
    ("        " + STUB_ORIG, "        " + STUB_PROBE): "module depth (same two functions)",
    (ORIG_CALL, INSERTED[3]): "root name",
}
STABLE_ORIG = ["        <T as StableSmallSortTypeImpl>::small_sort(", "            &mut v,",
               "            &mut scratch,", "            &mut volatile_reading_less::<T>,", "        );"]
STABLE_PROBE = ["        <T as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, "
                "&mut zst_aware_less::<T>);"]


def git(*args: str, text: bool = True):
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True,
                         text=True).stdout.strip()
    return subprocess.run(["git", "-C", top, *args], check=True, capture_output=True, text=text).stdout


def segment(lines: list[str], start: str, end: str) -> list[str]:
    i = lines.index(start)
    j = lines.index(end, i)
    return lines[i:j + 1]


def load_inventory(root: Path):
    """cleanup/source_inventory.py imported (its main() and report file are not used), pointed at ROOT."""
    here = root / "research/challenge-8/kani-k1/cleanup/source_inventory.py"
    spec = importlib.util.spec_from_file_location("unstablezst_source_inventory", here)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def names_at(mod, repo: Path, controls: bool) -> list[str]:
    mod.REPO = repo
    mod.SOURCE_ROOT = repo / "library/core/src/slice/sort/shared/smallsort/verify.rs"
    items, _files = mod.inventory(controls=controls)
    return [i["name"] for i in items]


def main() -> int:
    root = Path(git("rev-parse", "--show-toplevel").strip())
    out = Path(sys.argv[1]).resolve()
    errors: list[str] = []
    res: dict = {"base": BASE, "head": git("rev-parse", "HEAD").strip()}

    changed = sorted(git("diff", "--name-only", BASE, "--", "library").split())
    untracked = sorted(git("ls-files", "--others", "--exclude-standard", "--", "library").split())
    res["library_changed"] = changed + untracked
    if changed + untracked != [PROBE]:
        errors.append(f"library delta {changed + untracked}")

    base_probe = git("show", f"{BASE}:{PROBE}").splitlines()
    probe_text = (root / PROBE).read_text()
    probe = probe_text.splitlines()
    k = probe.index(INSERTED[1]) - 1
    res["zstprobe_rs_inserted_at_line"] = k + 1
    res["zstprobe_rs_inserted"] = probe[k:k + len(INSERTED)]
    if probe[k:k + len(INSERTED)] != INSERTED or probe[:k] + probe[k + len(INSERTED):] != base_probe:
        errors.append("zstprobe.rs delta is not exactly the inserted UNSTABLEZST block")
    # Placement: right after the stable `zst_stable_dispatch_aware_*` invocation.
    if probe[k - 1] != ");" or probe[k - 5] != "    zst_stable_dispatch_aware_n0_1_2_7_8_15_16_17_31_32,":
        errors.append("block not placed after zst_stable_dispatch_aware_*")
    res["zstprobe_rs_sha256"] = hashlib.sha256(probe_text.encode()).hexdigest()
    res["zstprobe_rs_base_blob"] = git("rev-parse", f"{BASE}:{PROBE}").strip()
    res["network_rs_blob"] = git("rev-parse", f"HEAD:{NET}").strip()

    # Root 1 semantic diff: helper + macro + invocation of the original vs the zstprobe copies.
    base_net = git("show", f"{BASE}:{NET}").splitlines()
    fn_start = "fn dispatch_safety_fixed<T: ArbitraryValue, const N: usize, const STABLE: bool>() {"
    orig = (segment(base_net, fn_start, "}")
            + [""] + segment(base_net, "macro_rules! dispatch_safety_cases {", "}")
            + [""] + [ORIG_CALL])
    if ORIG_CALL not in base_net or base_net[base_net.index(ORIG_CALL) - 1] != "#[cfg(kani_smallsort_controls)]":
        errors.append("original unstable ZST invocation not found with its controls gate")
    copy = (segment(probe, fn_start, "}")
            + [""] + segment(probe, "macro_rules! dispatch_safety_cases {", "}")
            + [""] + [INSERTED[3]])
    diff = list(difflib.unified_diff(orig, copy, f"base:{NET}", PROBE, lineterm="", n=1))
    (out.parent / "root1.diff").write_text("\n".join(diff) + "\n")
    sm = difflib.SequenceMatcher(a=orig, b=copy, autojunk=False)
    pairs, unexplained = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        a, b = orig[i1:i2], copy[j1:j2]
        if a == STABLE_ORIG and b == STABLE_PROBE:
            pairs.append("stable call (dead at STABLE = false): volatile_reading_less -> zst_aware_less")
        elif tag == "replace" and len(a) == len(b) and all(p in ALLOWED for p in zip(a, b)):
            pairs += [f"{ALLOWED[p]}: {p[0].strip()} -> {p[1].strip()}" for p in zip(a, b)]
        else:
            unexplained.append({"orig": a, "copy": b})
    res["root1_diff_pairs"], res["root1_unexplained"] = pairs, unexplained
    res["root1_compared_lines"] = [len(orig), len(copy)]
    if unexplained:
        errors.append("root 1 differs beyond comparator/module-depth paths/name")
    # Per-length roots: the same invocation with the length list narrowed to one entry.
    for n, line in zip(LENGTHS, INSERTED[4:]):
        if line != ORIG_CALL.replace("dispatch_safety_unstable_zst_n8_9_12_13_17",
                                     f"zst_unstable_dispatch_aware_n{n}").replace("[8, 9, 12, 13, 17]", f"[{n}]"):
            errors.append(f"per-length root {n}")
    res["covers_per_root"] = {ROOTS[0]: len(LENGTHS) + 1, **{r: 2 for r in ROOTS[1:]}}
    stubs = [l.strip() for l in probe if "#[kani::stub(" in l]
    if set(stubs) != {STUB_PROBE} or len(stubs) != 2:
        errors.append(f"stubs {stubs}")
    for bad in ("kani::assume", "proof_for_contract", "#[cfg(not"):
        if bad in probe_text:
            errors.append(f"forbidden token {bad}")
    long = [i + 1 for i, l in enumerate(probe) if len(l) > 100]
    if long:
        errors.append(f"lines > 100: {long}")

    # Name sets, base vs head, with the static source inventory of CLEANUP.
    inv = load_inventory(root)
    with tempfile.TemporaryDirectory() as tmp:
        arch = Path(tmp) / "base.tar"
        arch.write_bytes(git("archive", BASE, "library/core/src/slice/sort/shared/smallsort", text=False))
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
    if sorted(set(head_on) - set(base_on)) != sorted(PREFIX + r for r in ROOTS) or res["controls_on_removed"]:
        errors.append("controls-on delta is not exactly +6")
    if ORIG_ROOT not in head_on:
        errors.append("original unstable ZST root missing")
    # PFC: every library file but zstprobe.rs is byte-identical to BASE, and zstprobe.rs has no contract proof.
    res["pfc_delta"] = 0

    req = root / "research/challenge-8/kani-k1/RUN-REQUEST.json"
    pkt = root / "research/challenge-8/kani-k1/unstablezst/request.json"
    res["request_sha256"] = hashlib.sha256(req.read_bytes()).hexdigest()
    if req.read_bytes() != pkt.read_bytes():
        errors.append("RUN-REQUEST.json != unstablezst/request.json")
    data = json.loads(req.read_text())
    if [h["name"] for h in data["harnesses"]] != [PREFIX + n for n in ROOTS]:
        errors.append("request harness list")
    if {h["expect"] for h in data["harnesses"]} != {"SUCCESS"} or data["kind"] != "measurement":
        errors.append("request kind/expect")
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
    if res["envelope_usd"] > 1.30:
        errors.append("envelope over own cap $1.30")

    res["status"], res["errors"] = ("PASS" if not errors else "FAIL"), errors
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(res["status"], errors)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
