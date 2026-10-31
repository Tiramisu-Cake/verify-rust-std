#!/usr/bin/env python3
"""Static source/request audit only; does not compile or run a proof tool."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = "6a6a03e9535ee9204881687d29e884bb695be662"
SOURCE = "0560a33adbbd8b058c05370108357dcf09c265b8"
CAP_BASE = "6945f187208040e2d911e0797ef525668bdd46f8"
ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "research/challenge-8/kani-k1/geom16"
PARENT = "library/core/src/slice/sort/shared/smallsort/verify/merge.rs"
CHILD = "library/core/src/slice/sort/shared/smallsort/verify/merge/geom16.rs"
SUFFIX = b"\n#[cfg(kani_smallsort_controls)]\nmod geom16;\n"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha(data):
    return hashlib.sha256(data).hexdigest()


old = git("show", f"{BASE}:{PARENT}")
parent = (ROOT / PARENT).read_bytes()
child = (ROOT / CHILD).read_text()
assert parent == old + SUFFIX
assert parent == git("show", f"{SOURCE}:{PARENT}")
assert child.encode() == git("show", f"{SOURCE}:{CHILD}")
changed = git("diff", "--name-only", BASE, SOURCE, "--", "library").decode().splitlines()
assert sorted(changed) == sorted([PARENT, CHILD])
lanes = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
         "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh",
         "tool_config/kani-version.toml", "rust-toolchain.toml", ".gitmodules",
         ".cargo", "library/.cargo", "library/Cargo.toml", "library/Cargo.lock"]
assert not git("diff", "--name-only", CAP_BASE, "HEAD", "--", *lanes)
assert not git("diff", "--name-only", SOURCE, "--", "library")
assert '9461e07af7ec929f050aa4192f29363c9be07779' in (
    ROOT / "tool_config/kani-version.toml").read_text()
assert 'nightly-2026-10-12' in (ROOT / "rust-toolchain.toml").read_text()
assert "CAP_USD=88.96" in (ROOT / lanes[2] / "k1g.sh").read_text()
assert child.count("#[kani::unwind(34)]") == 8
assert child.count("#[kani::proof_for_contract(") == 3
assert child.count("#[kani::proof]") == 5
assert child.count("kani::assume(") == 2
assert "stub" not in child and "assume_init" not in child
assert child.count("[MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN]") == 5
assert max(map(len, child.splitlines())) <= 100

requests = [json.loads((OUT / f"{g}.request.json").read_text()) for g in ("g1", "g2")]
assert (ROOT / "research/challenge-8/kani-k1/RUN-REQUEST.json").read_bytes() == (
    OUT / "g1.request.json").read_bytes()
names = [h["name"] for r in requests for h in r["harnesses"]]
functions = re.findall(r"^fn (\w+)\(\)", child, re.M)
assert sorted(n.split("::")[-1] for n in names) == sorted(functions)
assert len(set(names)) == 8
for request in requests:
    assert request["controls"] and not request["uninit_checks"]
    assert request["kani_jobs"] == 1 and request["harness_timeout_minutes"] == 10
    for h in request["harnesses"]:
        if h["expect"] == "FAILED":
            assert child.count('"' + h["expect_check"] + '"') == 1

report = {
    "kind": "STATIC_ONLY_NO_COMPILATION_OR_PROOF_CREDIT",
    "base_sha": BASE, "source_sha": SOURCE, "cap_base_sha": CAP_BASE,
    "library_tree": git("rev-parse", f"{SOURCE}:library").decode().strip(),
    "library_changed_paths": changed,
    "old_parent_sha256": sha(old), "ordinary_parent_projection_sha256": sha(parent[:-len(SUFFIX)]),
    "new_child_sha256": sha(child.encode()),
    "old_parent_items_and_dependencies_byte_identical": True,
    "all_other_library_files_byte_identical": True,
    "ordinary_projection": "EOF cfg-off module absent; parent projection byte-identical",
    "registrations": "geom16 only at EOF; top region unchanged; independent specdiag insertion",
    "tooling_cap_pin_toolchain_unchanged_since_cap_base": True,
    "line_width_max": max(map(len, child.splitlines())),
    "assert_literal_lines": {literal: next(i for i, line in enumerate(child.splitlines(), 1)
                                         if '"' + literal + '"' in line)
        for literal in ["GEOM16_SORTED", "GEOM16_FULL_VALUE_COUNT",
                        "GEOM16_SOURCE_FRAME", "GEOM16_LEFT_HALF_FRAME"]},
    "exact_names": names,
    "requests_sha256": {g: sha((OUT / f"{g}.request.json").read_bytes()) for g in ("g1", "g2")},
    "result": "PASS",
}
(OUT / "source-audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: report[k] for k in ["result", "source_sha", "library_tree",
                                       "line_width_max", "assert_literal_lines"]}, indent=2))
