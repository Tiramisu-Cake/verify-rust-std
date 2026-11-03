#!/usr/bin/env python3
"""TYPEMATRIX static checks (no cargo/rustc/Kani): library delta, macro semantic diff, roots, name sets, request.

Usage: python3 -B check_typematrix.py OUT_JSON  (run from anywhere inside the worktree)
Writes OUT_JSON and typematrix/macros.diff next to it; exit 1 on any failed check.
"""

import difflib
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

BASE = "e8e238db9d87323fa4da011a1a8b37fb76ec91c0"  # v6 library tree + K-1 tooling + cap 93.96
V = "library/core/src/slice/sort/shared/smallsort/verify"
NET, MOD = f"{V}/network.rs", f"{V}/network/typematrix.rs"
PREFIX = "slice::sort::shared::smallsort::verify::network::typematrix::"
NET_INSERT = ["#[cfg(kani_smallsort_controls)]", "mod typematrix;", ""]
NET_INSERT_AFTER = ["use crate::kani;", "use crate::mem::size_of;", ""]
STUB_ORIG = "        #[kani::stub(super::super::panic_on_ord_violation, assume_order_violation)]"
STUB_COPY = ("        #[kani::stub(super::super::super::panic_on_ord_violation, "
             "super::assume_order_violation)]")
GROUPS = {"n0_1_2_7_8": [0, 1, 2, 7, 8], "n15_16_17": [15, 16, 17], "n31_32": [31, 32]}
TYPES = {"u8u32": "(u8, u32)", "u128": "u128", "bytes9": "[u8; 9]"}
# (root, macro, type, stable literal or None for the pair macro, lengths)
ROOTS = [(f"dispatch_safety_stable_unstable_{t}_{g}", "dispatch_pair_safety_cases", ty, None, ns)
         for t, ty in TYPES.items() for g, ns in GROUPS.items()]
ROOTS.append(("dispatch_safety_unstable_u8u32_n9_12_13_18", "dispatch_safety_cases", "(u8, u32)", "false",
              [9, 12, 13, 18]))


def git(*args: str, text: bool = True):
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True,
                         text=True).stdout.strip()
    return subprocess.run(["git", "-C", top, *args], check=True, capture_output=True, text=text).stdout


def macro(lines: list[str], name: str) -> list[str]:
    start = f"macro_rules! {name} {{"
    i = lines.index(start)
    return lines[i:lines.index("}", i) + 1]


def load_inventory(root: Path):
    """cleanup/source_inventory.py imported (its main() and report file are not used), pointed at ROOT."""
    here = root / "research/challenge-8/kani-k1/cleanup/source_inventory.py"
    spec = importlib.util.spec_from_file_location("typematrix_source_inventory", here)
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
    res["library_changed"] = sorted(changed + untracked)
    if res["library_changed"] != sorted([NET, MOD]):
        errors.append(f"library delta {res['library_changed']}")

    # network.rs: base + exactly the gated `mod typematrix;` after the `use` block.
    base_net = git("show", f"{BASE}:{NET}").splitlines()
    net = (root / NET).read_text().splitlines()
    k = net.index(NET_INSERT[1]) - 1
    res["network_rs_inserted_at_line"] = k + 1
    if net[k:k + 3] != NET_INSERT or net[:k] + net[k + 3:] != base_net or net[k - 3:k] != NET_INSERT_AFTER:
        errors.append("network.rs delta is not exactly the gated mod line after the use block")

    text = (root / MOD).read_text()
    mod = text.splitlines()
    res["typematrix_rs_sha256"] = hashlib.sha256(text.encode()).hexdigest()
    res["typematrix_rs_lines"] = len(mod)
    res["network_rs_sha256"] = hashlib.sha256((root / NET).read_bytes()).hexdigest()
    res["network_rs_base_blob"] = git("rev-parse", f"{BASE}:{NET}").strip()

    # Semantic diff: both copied macros against the parent's; only the stub line may differ.
    orig = macro(base_net, "dispatch_safety_cases") + [""] + macro(base_net, "dispatch_pair_safety_cases")
    copy = macro(mod, "dispatch_safety_cases") + [""] + macro(mod, "dispatch_pair_safety_cases")
    diff = list(difflib.unified_diff(orig, copy, f"base:{NET}", MOD, lineterm="", n=1))
    (out.parent / "macros.diff").write_text("\n".join(diff) + "\n")
    sm = difflib.SequenceMatcher(a=orig, b=copy, autojunk=False)
    pairs, unexplained = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        a, b = orig[i1:i2], copy[j1:j2]
        if a == [STUB_ORIG] and b == [STUB_COPY]:
            pairs.append("stub paths one module deeper (same two functions)")
        else:
            unexplained.append({"orig": a, "copy": b})
    res["macro_diff_pairs"], res["macro_unexplained"] = pairs, unexplained
    res["macro_compared_lines"] = [len(orig), len(copy)]
    if unexplained or len(pairs) != 2:
        errors.append("copied macros differ beyond the two stub lines")
    pair_doc = "/// Selects stable or unstable dispatch for each listed fixed array length and covers both routes."
    if mod[mod.index("macro_rules! dispatch_pair_safety_cases {") - 1] != pair_doc:
        errors.append("pair macro doc line")
    # The body is the parent's: neither the helper nor the comparator is copied.
    for bad in ("fn dispatch_safety_fixed", "fn volatile_reading_less", "kani::assume", "proof_for_contract",
                "#[cfg(", "stub_verified", "#[kani::solver"):
        if bad in text:
            errors.append(f"forbidden token {bad}")
    if "use super::{ArbitraryValue, dispatch_safety_fixed};" not in mod:
        errors.append("parent helper import")
    stubs = [l for l in mod if "#[kani::stub(" in l]
    if stubs != [STUB_COPY, STUB_COPY]:
        errors.append(f"stubs {stubs}")
    if [l.strip() for l in mod if "#[kani::unwind(" in l] != ["#[kani::unwind(65)]"] * 2:
        errors.append("unwind")
    long = [i + 1 for i, l in enumerate(mod) if len(l) > 100]
    if long:
        errors.append(f"lines > 100: {long}")

    # Invocations: exactly the ten roots, in order, with their type/stable/lengths; covers from the macros.
    calls = re.findall(r"^(dispatch_(?:pair_)?safety_cases)!\(\s*(\w+),\s*(\(u8, u32\)|u128|\[u8; 9\]),"
                       r"\s*(?:(true|false),\s*)?\[([\d, ]+)\]\s*\);", text, re.M)
    got = [(n, m, t, s or None, [int(x) for x in ls.split(",")]) for m, n, t, s, ls in calls]
    res["roots"] = [{"name": n, "macro": m, "type": t, "stable": s, "lengths": ls,
                     "covers": (2 * len(ls) + 1) if s is None else len(ls) + 1} for n, m, t, s, ls in got]
    if got != ROOTS:
        errors.append(f"root invocations {got}")
    if len(re.findall(r"^dispatch_(?:pair_)?safety_cases!\(", text, re.M)) != len(ROOTS):
        errors.append("unparsed invocations")
    res["covers_total"] = sum(r["covers"] for r in res["roots"])

    # ArbitraryValue: full any for the tuple fields and u128; no impl for [u8; 9] (parent's [u8; M]).
    impls = re.findall(r"^impl ArbitraryValue for (.+) \{\n    fn arbitrary_value\(\) -> Self \{\n        (.+)\n",
                       text, re.M)
    res["arbitrary_impls"] = impls
    if impls != [("(u8, u32)", "(kani::any(), kani::any())"), ("u128", "kani::any()")]:
        errors.append(f"ArbitraryValue impls {impls}")
    if "impl<const M: usize> ArbitraryValue for [u8; M] {" not in base_net:
        errors.append("parent [u8; M] impl missing")
    asserts = [l.strip() for l in mod if l.strip().startswith("assert!(")]
    res["const_asserts"] = asserts
    if len(asserts) != 9 or "    if cfg!(any(target_arch = \"x86_64\", target_arch = \"aarch64\")) {" not in mod:
        errors.append("target-specific const assertions")

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
    if res["controls_on_added"] != sorted(PREFIX + r[0] for r in ROOTS) or res["controls_on_removed"]:
        errors.append("controls-on delta is not exactly +10")
    # PFC: network.rs gains only the gated mod line, every other file is byte-identical, typematrix.rs has none.
    res["pfc_delta"] = 0

    req = root / "research/challenge-8/kani-k1/RUN-REQUEST.json"
    pkt = root / "research/challenge-8/kani-k1/typematrix/request.json"
    res["request_sha256"] = hashlib.sha256(req.read_bytes()).hexdigest()
    if req.read_bytes() != pkt.read_bytes():
        errors.append("RUN-REQUEST.json != typematrix/request.json")
    data = json.loads(req.read_text())
    if [h["name"] for h in data["harnesses"]] != [PREFIX + r[0] for r in ROOTS]:
        errors.append("request harness list")
    if {h["expect"] for h in data["harnesses"]} != {"SUCCESS"} or data["kind"] != "measurement":
        errors.append("request kind/expect")
    if (data["agent"], data["runner"], data["controls"], data["kani_jobs"], data["uninit_checks"],
            data["harness_timeout_minutes"]) != ("k1-merge", "gcb-e2-standard-4", True, 1, False, 10):
        errors.append("request profile")
    if not data["request_id"].startswith("typematrix-"):
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
    if res["envelope_usd"] > 1.80:
        errors.append("envelope over own cap $1.80")

    res["status"], res["errors"] = ("PASS" if not errors else "FAIL"), errors
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(res["status"], errors)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
