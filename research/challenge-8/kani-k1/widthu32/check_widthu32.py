#!/usr/bin/env python3
"""WIDTHU32 static checks (no cargo/rustc/Kani): library delta, body diff vs PERMSOLVER, name sets, request.

Usage: python3 -B check_widthu32.py OUT_JSON  (run from anywhere inside the worktree)
Writes OUT_JSON and widthu32/body.diff next to it; exit 1 on any failed check.
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

BASE = "e0fda080f5ea479d8f4fb801f4b42adde2b3259f"   # branch base (v6 tree + K-1 tooling + cap 98.96)
PERMSOLVER = "a13389358a2bf617891a90fbccae343feeb2a613"  # PERMSOLVER result commit
V = "library/core/src/slice/sort/shared/smallsort/verify"
NET, NEW = f"{V}/network.rs", f"{V}/network/widthu32.rs"
SOLVER = f"{V}/network/posts/perm/solver.rs"
PREFIX = "slice::sort::shared::smallsort::verify::network::widthu32::"
ROOTS = ["widthu32_perm_n8_default", "widthu32_perm_n8_kissat", "widthu32_perm_n8_value_loss_control"]
APPENDED = "\n#[cfg(kani_smallsort_controls)]\nmod widthu32;\n"
ORIG = "perm_arbitrary_kissat_u64_n8"
CTRL_LIT = "widthu32 negative: full-value count after value loss"
NEW_COVERS = [
    "kani::cover(\nsuper::count_matching_values(&pre, &probe) > 0,\n\"widthu32: probe occurs in input\",\n);",
    "kani::cover(\nsuper::count_matching_values(&pre, &probe) == 0,\n\"widthu32: probe absent from input\",\n);",
]


def git(*args: str, text: bool = True):
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True,
                         text=True).stdout.strip()
    return subprocess.run(["git", "-C", top, *args], check=True, capture_output=True, text=text).stdout


def item(text: str, name: str) -> str:
    """Attributes + fn item `name` (from the blank line before it to its closing brace)."""
    i = text.index("fn " + name + "()")
    s = text.rfind("\n\n", 0, i) + 2
    depth, j = 0, text.index("{", i)
    for k in range(j, len(text)):
        depth += text[k] == "{"
        depth -= text[k] == "}"
        if depth == 0:
            return text[s:k + 1]
    raise ValueError(name)


def norm(s: str, subs) -> list[str]:
    """Whitespace-normalized statements, one per line (rustfmt wraps differ with path length)."""
    for a, b in subs:
        s = s.replace(a, b)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\(\s", "(", s)
    s = re.sub(r",\s\)", ")", s)
    s = re.sub(r"\] (?=#\[|fn )", "]\n", s)
    return s.replace("; ", ";\n").replace("{ ", "{\n").splitlines()


def load_inventory(root: Path):
    here = root / "research/challenge-8/kani-k1/cleanup/source_inventory.py"
    spec = importlib.util.spec_from_file_location("widthu32_source_inventory", here)
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
    res: dict = {"base": BASE, "permsolver": PERMSOLVER, "head": git("rev-parse", "HEAD").strip()}

    changed = sorted(git("diff", "--name-only", BASE, "--", "library").split())
    untracked = sorted(git("ls-files", "--others", "--exclude-standard", "--", "library").split())
    res["library_changed"] = sorted(changed + untracked)
    if res["library_changed"] != sorted([NET, NEW]):
        errors.append(f"library delta {res['library_changed']}")
    base_net = git("show", f"{BASE}:{NET}")
    net = (root / NET).read_text()
    if net != base_net + APPENDED:
        errors.append("network.rs delta is not exactly the appended opt-in `mod widthu32;`")
    res["network_rs_base_blob"] = git("rev-parse", f"{BASE}:{NET}").strip()
    res["network_rs_sha256"] = hashlib.sha256(net.encode()).hexdigest()
    new = (root / NEW).read_text()
    res["widthu32_rs_sha256"] = hashlib.sha256(new.encode()).hexdigest()
    res["widthu32_rs_bytes"] = len(new.encode())

    # Body diff: each root vs PERMSOLVER perm_arbitrary_kissat_u64_n8, paths and type mapped.
    orig_text = git("show", f"{PERMSOLVER}:{SOLVER}")
    res["permsolver_solver_rs_blob"] = git("rev-parse", f"{PERMSOLVER}:{SOLVER}").strip()
    orig = norm(item(orig_text, ORIG), [("super::super::super::", "super::")])
    # Expected statement sequence per root: the original with u64 -> u32 (the only u64 tokens are the
    # type), the root name, the per-root allowed change, and the two probe covers appended. Exact match.
    base_seq = [l.replace("u64", "u32") for l in orig]
    report = []
    for r in ROOTS:
        copy = norm(item(new, r), [])
        exp = list(base_seq)
        exp[exp.index("fn " + ORIG.replace("u64", "u32") + "() {")] = "fn " + r + "() {"
        if r == "widthu32_perm_n8_default":
            exp.remove("#[kani::solver(kissat)]")
        if r == "widthu32_perm_n8_value_loss_control":
            k = exp.index("<u32 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);")
            exp.insert(k + 1, "v[0] = v[1];")
            exp[k + 2] = exp[k + 2].replace('"partposts: full-value count preserved"', f'"{CTRL_LIT}"')
        end = len(exp) - 1
        exp[end:end] = norm("\n".join(NEW_COVERS), [])
        report += list(difflib.unified_diff(orig, copy, f"permsolver:{ORIG}", f"widthu32:{r}",
                                            lineterm="", n=0)) + [""]
        if copy != exp:
            errors.append(f"{r}: statement sequence != PERMSOLVER body (u32) + allowed change + 2 covers")
            res.setdefault("mismatch", {})[r] = list(difflib.unified_diff(exp, copy, lineterm="", n=0))
    (out.parent / "body.diff").write_text("\n".join(report))
    res["u64_tokens_in_widthu32"] = new.count("u64")
    if "u64" in new.replace("perm_arbitrary_kissat_u64_n8", "").replace("u64 N8", ""):
        errors.append("u64 left in widthu32.rs")
    res["covers_per_root"] = {r: item(new, r).count("kani::cover(") for r in ROOTS}
    if set(res["covers_per_root"].values()) != {5}:
        errors.append("covers per root != 5")
    lits = re.findall(r'"([^"]*)"', new)
    if CTRL_LIT not in lits or lits.count(CTRL_LIT) != 1 or any(CTRL_LIT in l for l in lits if l != CTRL_LIT):
        errors.append("control literal not unique")
    for bad in ("kani::assume", "proof_for_contract", "any_where", "#[cfg(", "kani::stub"):
        if bad in new:
            errors.append(f"forbidden token {bad}")
    long = [i + 1 for i, l in enumerate(new.splitlines()) if len(l) > 100]
    if long:
        errors.append(f"lines > 100: {long}")
    res["root_lines"] = {r: new[:new.index("fn " + r + "()")].count("\n") + 1 for r in ROOTS}

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
    res["ordinary_sorted_sha256"] = hashlib.sha256("\n".join(sorted(head_ord)).encode()).hexdigest()
    res["controls_on_count"] = [len(base_on), len(head_on)]
    res["controls_on_added"] = sorted(set(head_on) - set(base_on))
    res["controls_on_removed"] = sorted(set(base_on) - set(head_on))
    if base_ord != head_ord or len(head_ord) != 202:
        errors.append("ordinary set changed or != 202")
    if res["controls_on_added"] != sorted(PREFIX + r for r in ROOTS) or res["controls_on_removed"]:
        errors.append("controls-on delta is not exactly +3")
    # PFC: network.rs only gains the mod line; widthu32.rs has no contract proof (checked above).
    res["pfc_delta"] = 0

    req = root / "research/challenge-8/kani-k1/RUN-REQUEST.json"
    pkt = root / "research/challenge-8/kani-k1/widthu32/request.json"
    res["request_sha256"] = hashlib.sha256(req.read_bytes()).hexdigest()
    if req.read_bytes() != pkt.read_bytes():
        errors.append("RUN-REQUEST.json != widthu32/request.json")
    data = json.loads(req.read_text())
    if [h["name"] for h in data["harnesses"]] != [PREFIX + n for n in ROOTS]:
        errors.append("request harness list")
    if [h["expect"] for h in data["harnesses"]] != ["SUCCESS", "SUCCESS", "FAILED"] \
            or data["harnesses"][2].get("expect_check") != CTRL_LIT or data["kind"] != "diagnostic" \
            or data["agent"] != "k1-network" or not data["request_id"].startswith("widthuthirtytwo-"):
        errors.append("request kind/agent/expect")
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
    if res["envelope_usd"] > 0.810 + 1e-9:
        errors.append("envelope over reserve $0.810")

    res["status"], res["errors"] = ("PASS" if not errors else "FAIL"), errors
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(res["status"], errors)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
