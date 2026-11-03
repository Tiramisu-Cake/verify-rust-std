#!/usr/bin/env python3
"""PANICPROBE static checks (no cargo/rustc/Kani): library delta, root attributes, name sets, request.

Usage: python3 -B check_panicprobe.py OUT_JSON  (run from anywhere inside the worktree)
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

BASE = "e8e238db9d87323fa4da011a1a8b37fb76ec91c0"  # cap 93.96, v6 library tree + K-1 tooling
V = "library/core/src/slice/sort/shared/smallsort/verify"
NET, PROBE = f"{V}/network.rs", f"{V}/network/panicprobe.rs"
PREFIX = "slice::sort::shared::smallsort::verify::network::panicprobe::"
# root -> (should_panic, expect, expect_check or None)
ROOTS = {
    "panic_control_plain": (True, "SUCCESS", None),
    "panic_control_ub": (True, "FAILED", "pointer outside object bounds"),
    "panic_network_u8_n18_should_panic": (True, "SUCCESS", None),
    "panic_network_u8_n18_plain": (False, "FAILED", "does not correctly implement a total order"),
    "panic_general_u8_n16_should_panic": (True, "SUCCESS", None),
    "panic_general_u8_n16_plain": (False, "FAILED", "does not correctly implement a total order"),
}
BODY = {"panic_network_u8_n18_should_panic": "network_u8_n18();",
        "panic_network_u8_n18_plain": "network_u8_n18();",
        "panic_general_u8_n16_should_panic": "general_u8_n16();",
        "panic_general_u8_n16_plain": "general_u8_n16();"}
NET_INSERT = ["", "#[cfg(kani_smallsort_controls)]", "mod panicprobe;"]


def git(*args: str, text: bool = True):
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True,
                         text=True).stdout.strip()
    return subprocess.run(["git", "-C", top, *args], check=True, capture_output=True, text=text).stdout


def load_inventory(root: Path):
    here = root / "research/challenge-8/kani-k1/cleanup/source_inventory.py"
    spec = importlib.util.spec_from_file_location("panicprobe_source_inventory", here)
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
    res["library_changed"] = sorted(set(changed + untracked))
    if res["library_changed"] != sorted([NET, PROBE]):
        errors.append(f"library delta {res['library_changed']}")

    base_net = git("show", f"{BASE}:{NET}").splitlines()
    net = (root / NET).read_text().splitlines()
    k = net.index("mod panicprobe;") - 2
    res["network_rs_inserted_at_line"] = k + 1
    if net[k:k + 3] != NET_INSERT or net[:k] + net[k + 3:] != base_net:
        errors.append("network.rs delta is not exactly the gated `mod panicprobe;`")
    res["network_rs_base_blob"] = git("rev-parse", f"{BASE}:{NET}").strip()
    res["network_rs_sha256"] = hashlib.sha256((root / NET).read_bytes()).hexdigest()

    text = (root / PROBE).read_text()
    lines = text.splitlines()
    res["panicprobe_rs_sha256"] = hashlib.sha256(text.encode()).hexdigest()
    # Each root: attribute lines directly above `fn name() {`, and its body.
    found = {}
    for i, line in enumerate(lines):
        m = re.fullmatch(r"fn (\w+)\(\) \{", line)
        if not m or m.group(1) not in ROOTS:
            continue
        j = i
        while j > 0 and lines[j - 1].startswith("#["):
            j -= 1
        attrs = lines[j:i]
        end = lines.index("}", i)
        found[m.group(1)] = {"line": i + 1, "attrs": attrs, "body": [l.strip() for l in lines[i + 1:end]]}
    res["roots"] = found
    if sorted(found) != sorted(ROOTS):
        errors.append(f"roots found {sorted(found)}")
    for name, (sp, _e, _c) in ROOTS.items():
        want = ["#[kani::proof]"] + (["#[kani::should_panic]"] if sp else []) + ["#[kani::unwind(65)]"]
        if found.get(name, {}).get("attrs") != want:
            errors.append(f"{name} attributes {found.get(name, {}).get('attrs')}")
        if name in BODY and found.get(name, {}).get("body") != [BODY[name]]:
            errors.append(f"{name} body")
    for bad in ("kani::stub", "kani::assume", "proof_for_contract", "#[cfg", "volatile", "unwrap"):
        if bad in text:
            errors.append(f"forbidden token {bad}")
    res["kani_proof_count"] = text.count("#[kani::proof]")
    res["covers"] = [l.strip() for l in lines if "kani::cover(" in l]
    if res["kani_proof_count"] != 6 or len(res["covers"]) != 4:
        errors.append("proof/cover count")
    long = [i + 1 for i, l in enumerate(lines) if len(l) > 100]
    if long:
        errors.append(f"lines > 100: {long}")

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
    if res["controls_on_added"] != sorted(PREFIX + r for r in ROOTS) or res["controls_on_removed"]:
        errors.append("controls-on delta is not exactly +6")
    # PFC 36: network.rs gains only a gated module declaration and panicprobe.rs has no contract proof.
    res["pfc_delta"] = 0

    req = root / "research/challenge-8/kani-k1/RUN-REQUEST.json"
    pkt = root / "research/challenge-8/kani-k1/panicprobe/request.json"
    if pkt.exists():
        res["request_sha256"] = hashlib.sha256(pkt.read_bytes()).hexdigest()
        if not req.exists() or req.read_bytes() != pkt.read_bytes():
            errors.append("RUN-REQUEST.json != panicprobe/request.json")
        data = json.loads(pkt.read_text())
        want = [{"name": PREFIX + n, "expect": e, **({"expect_check": c} if c else {})}
                for n, (_s, e, c) in ROOTS.items()]
        if data["harnesses"] != want:
            errors.append("request harness list/expectations")
        prof = {k: data.get(k) for k in ("kind", "runner", "controls", "kani_jobs", "uninit_checks",
                                         "harness_timeout_minutes", "agent")}
        res["request_profile"] = prof
        if prof != {"kind": "diagnostic", "runner": "gcb-e2-standard-4", "controls": True, "kani_jobs": 1,
                    "uninit_checks": False, "harness_timeout_minutes": 10, "agent": "k1-network"}:
            errors.append("request profile")
        with tempfile.TemporaryDirectory() as tmp:
            v = subprocess.run(["python3", "-B", str(root / "research/challenge-8/kani-k1/tools/kani_k1.py"),
                                "validate", str(pkt), "--args-out", f"{tmp}/args", "--runner-out",
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
    else:
        errors.append("panicprobe/request.json missing")

    res["status"], res["errors"] = ("PASS" if not errors else "FAIL"), errors
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(res["status"], errors)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
