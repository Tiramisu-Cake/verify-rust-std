#!/usr/bin/env python3
"""Static checks of the LOOPINV package: name-set delta, ordinary/PFC, cfg gate, lane guard, request.

Read-only: runs git, the cleanup source inventory and the lane's own request validator on
`git archive` exports; never builds or verifies anything.
Usage: python3 -I check_loopinv.py [--out FILE]
"""
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
K1 = "research/challenge-8/kani-k1"
BASE = "e0fda080f5ea479d8f4fb801f4b42adde2b3259f"
TOOLING_BASE = "b1242ef7faccd9b4778d40be8967c764e439d5e4"
S = "library/core/src/slice/sort/shared/smallsort"
SMALLSORT, NETWORK, LOOPINV = f"{S}.rs", f"{S}/verify/network.rs", f"{S}/verify/network/loopinv.rs"
LIB_ALLOWED = {SMALLSORT, NETWORK, LOOPINV}
NS = "slice::sort::shared::smallsort::verify::network::loopinv::"
ROOTS = ["loopinv_copy_false_control", "loopinv_copy_true", "loopinv_insertion_u64_n2_offset1"]
GATE = "all(kani, kani_smallsort_controls)"
PROOF = re.compile(r"kani\s*::\s*proof(?:_for_contract)?\b")
PFC = re.compile(r"kani\s*::\s*proof_for_contract\b")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout


def export(rev: str, dest: Path) -> Path:
    data = subprocess.run(["git", "-C", str(ROOT), "archive", rev, "library/core/src/slice/sort"],
                          check=True, capture_output=True).stdout
    tar = dest / "x.tar"
    tar.write_bytes(data)
    with tarfile.open(tar) as t:
        t.extractall(dest, filter="data")
    return dest


def load_inventory(repo: Path):
    spec = importlib.util.spec_from_file_location("k1_source_inventory", ROOT / K1 / "cleanup/source_inventory.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    repo = repo.resolve()
    mod.REPO = repo
    mod.SOURCE_ROOT = repo / f"{S}/verify.rs"
    return mod


def pfc_names(mod, controls: bool) -> set[str]:
    """Active proof_for_contract roots: the inventory's own walk, attribute kind added."""
    out = set()
    for path, text, inherited in mod.module_sources(mod.SOURCE_ROOT):
        masked = mod.predict.mask_comments_strings(text)
        spans, macros = mod.macro_proofs(text, masked)
        outside = mod.predict.blank_spans(masked, spans)
        parts = list(path.relative_to(mod.SOURCE_ROOT.parent).with_suffix("").parts)[1:]
        prefix = mod.PREFIX + ("::".join(parts) + "::" if parts else "")
        for found in re.finditer(r"\bfn\s+([A-Za-z_]\w*)\s*(?:<|\()", outside):
            attrs = mod.attr_block(masked, found.start())
            if PFC.search(attrs) and mod.active(mod.gate_state(attrs, inherited), controls):
                out.add(prefix + found.group(1))
        for call in re.finditer(r"\b([A-Za-z_]\w*)\s*!\s*\(", outside):
            if call.group(1) not in macros:
                continue
            paren = outside.find("(", call.start(), call.end())
            close = mod.predict.matching(outside, paren, "(", ")")
            args = mod.predict.split_args(outside[paren + 1:close])
            gates0 = mod.gate_state(mod.attr_block(masked, call.start()), inherited)
            for em in macros[call.group(1)]:
                raw = args[em["index"]]
                name = re.sub(r"^(?:\s*#\[[^]]+\]\s*)+", "", raw).strip()
                gates = tuple(dict.fromkeys((*gates0, *mod.gate_state(raw, inherited), *em["gates"])))
                if PFC.search(em["attribute"]) and mod.active(gates, controls):
                    out.add(prefix + name)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    errors: list[str] = []
    report: dict = {"base": BASE, "head": git("rev-parse", "HEAD").strip()}

    changed = set(git("diff", "--name-only", BASE, "HEAD", "--", "library").split())
    report["library_files_changed"] = sorted(changed)
    if changed != LIB_ALLOWED:
        errors.append(f"library diff must be exactly {sorted(LIB_ALLOWED)}: {sorted(changed)}")

    # smallsort.rs: exactly one inserted hunk, a cfg_attr on the outer while; no deletions.
    diff = git("diff", "-U0", BASE, "HEAD", "--", SMALLSORT)
    added = [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]
    hunks = [l for l in diff.splitlines() if l.startswith("@@")]
    head_src = (ROOT / SMALLSORT).read_text()
    attr_text = "\n".join(added)
    report["smallsort_diff"] = {"hunks": len(hunks), "added": len(added), "removed": len(removed)}
    if len(hunks) != 1 or removed or not added[0].strip().startswith("#[cfg_attr(") or added[-1].strip() != ")]":
        errors.append("smallsort.rs diff must be one inserted #[cfg_attr(...)] block")
    if GATE not in attr_text:
        errors.append(f"smallsort.rs attribute must be gated on {GATE}")
    after = head_src.split(attr_text, 1)[1].lstrip("\n").splitlines()[0].strip()
    if after != "while tail != v_end {":
        errors.append(f"attribute must sit on the outer loop, found: {after!r}")
    fn_start = head_src.index("pub fn insertion_sort_shift_left")
    if not (fn_start < head_src.index(attr_text) < head_src.index("pub unsafe fn sort4_stable")):
        errors.append("attribute must be inside insertion_sort_shift_left")
    base_src = git("show", f"{BASE}:{SMALLSORT}")
    if head_src.replace(attr_text + "\n", "", 1) != base_src:
        errors.append("smallsort.rs minus the attribute differs from base")
    # Without the cfg (ordinary build) cfg_attr expands to nothing: the remaining source is base.
    report["ordinary_build_smallsort_equals_base"] = head_src.replace(attr_text + "\n", "", 1) == base_src

    net = git("diff", "-U0", BASE, "HEAD", "--", NETWORK)
    net_added = [l[1:] for l in net.splitlines() if l.startswith("+") and not l.startswith("+++")]
    net_removed = [l for l in net.splitlines() if l.startswith("-") and not l.startswith("---")]
    if net_removed or [l for l in net_added if l.strip()] != ["#[cfg(kani_smallsort_controls)]", "mod loopinv;"]:
        errors.append(f"network.rs diff must only add the gated mod loopinv: {net_added} / {net_removed}")

    with tempfile.TemporaryDirectory() as td:
        sets = {}
        for label, rev in (("base", BASE), ("head", "HEAD")):
            d = Path(td) / label
            d.mkdir()
            mod = load_inventory(export(rev, d))
            ordinary, _ = mod.inventory(controls=False)
            controls, _ = mod.inventory(controls=True)
            sets[label] = {"ordinary": {r["name"] for r in ordinary}, "controls": {r["name"] for r in controls},
                           "pfc": pfc_names(mod, False), "pfc_controls": pfc_names(mod, True)}
    b, h = sets["base"], sets["head"]
    report["counts"] = {k: {"base": len(b[k]), "head": len(h[k])} for k in b}
    report["ordinary_equal"] = b["ordinary"] == h["ordinary"]
    report["pfc_equal"] = b["pfc"] == h["pfc"]
    plus, minus = sorted(h["controls"] - b["controls"]), sorted(b["controls"] - h["controls"])
    report["controls_delta"] = {"added": plus, "removed": minus}
    sha = lambda names: hashlib.sha256("\n".join(sorted(names)).encode()).hexdigest()
    report["ordinary_sha256"] = sha(h["ordinary"])
    report["controls_sha256"] = {"base": sha(b["controls"]), "head": sha(h["controls"])}
    if not report["ordinary_equal"] or len(h["ordinary"]) != 202:
        errors.append("ordinary set must be unchanged at 202")
    # Static attribute count (wrappers included) differs from the 36 of the compiler inventory;
    # the gate here is set identity with base.
    report["pfc_sha256"] = sha(h["pfc"])
    if not report["pfc_equal"]:
        errors.append("ordinary PFC set must equal base")
    if plus != [NS + r for r in ROOTS] or minus:
        errors.append(f"controls delta must be exactly +3 loopinv roots: {plus} / {minus}")

    # The lane's stray-controls guard (gcb-k1.sh validate step), replayed on HEAD with the pathspecs
    # read from the lane script of HEAD itself (owner exception b1242ef7fa adds smallsort.rs).
    lane = git("show", f"HEAD:{K1}/tools/gcb-k1.sh")
    block = lane[lane.index("stray=$(git grep -l kani_smallsort_controls"):]
    block = block[:block.index("|| true)")]
    excludes = re.findall(r"'(:![^']+)'", block)
    report["lane_guard_excludes"] = excludes
    stray = subprocess.run(["git", "-C", str(ROOT), "grep", "-l", "kani_smallsort_controls", "HEAD", "--", "library",
                            *excludes], capture_output=True, text=True).stdout.split()
    report["lane_stray_controls_guard"] = stray
    if stray:
        errors.append(f"lane guard would reject the request: {stray}")
    # Lane files equal the reviewed tooling base (k1g.sh LANE_PATHS).
    lane_paths = [".circleci", ".github/workflows", f"{K1}/tools", f"{K1}/gcb", "scripts/run-kani.sh",
                  "tool_config/kani-version.toml", "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo",
                  "library/Cargo.toml", "library/Cargo.lock"]
    lane_diff = git("diff", "--name-only", TOOLING_BASE, "HEAD", "--", *lane_paths).split()
    report["tooling_base"] = TOOLING_BASE
    report["lane_files_differ_from_tooling_base"] = lane_diff
    if lane_diff:
        errors.append(f"lane files differ from tooling base: {lane_diff}")
    report["lane_guard_blocks_dispatch"] = bool(stray)

    spec = importlib.util.spec_from_file_location("kani_k1", ROOT / K1 / "tools/kani_k1.py")
    kani_k1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kani_k1)
    req_path = HERE / "request.json"
    req = json.loads(req_path.read_text())
    try:
        kani_k1.validate_request(req)
        report["request_valid"] = True
    except Exception as exc:  # noqa: BLE001
        report["request_valid"] = False
        errors.append(f"request invalid: {exc}")
    names = [e["name"] for e in req["harnesses"]]
    if sorted(names) != sorted(NS + r for r in ROOTS):
        errors.append("request names must be the three loopinv roots")
    run = ROOT / K1 / "RUN-REQUEST.json"
    report["run_request_matches"] = run.read_bytes() == req_path.read_bytes()
    report["request_sha256"] = hashlib.sha256(req_path.read_bytes()).hexdigest()
    report["source_sha256"] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sorted(LIB_ALLOWED)}
    report["errors"] = errors
    text = json.dumps(report, indent=1, ensure_ascii=False)
    if a.out:
        Path(a.out).write_text(text + "\n")
    print(text)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
