"""Static scope and source identity checks; no local Rust or proof tools."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = "a3d731225cf5c55a7268cc0dada8e151e4c256ef"
MERGE = "library/core/src/slice/sort/shared/smallsort/verify/merge.rs"
NETWORK = "library/core/src/slice/sort/shared/smallsort/verify/network.rs"
SOURCES = {
    "OPT_G1": "73fb790ad0d78e81c5a2928651650398dbe7d673",
    "OPT_G2": "c81c10e3061e07bb83c732d81413632ada757d2c",
    "BACKING": "740d22674ca200f3270fb298651302019d347828",
}
PATHS = [
    "library", ".circleci", ".github/workflows", ".gitmodules", ".cargo",
    "research/challenge-8/kani-k1/tools", "research/challenge-8/kani-k1/gcb",
    "scripts/run-kani.sh", "tool_config/kani-version.toml", "rust-toolchain.toml",
]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def blob(sha, path):
    return git("show", f"{sha}:{path}").decode()


def function(text, name):
    start = text.index("    fn " + name)
    begin = text.index(" {", start) + 1
    depth, end = 1, begin + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


old, now = blob(BASE, MERGE), (ROOT / MERGE).read_text()
before = old.split("mod backing {", 1)[1]
after = now.split("mod backing {", 1)[1]
guard = "N == 6 || N == 7 || N == 8"
assert function(after, "stable_direct_body").replace(guard, "N == 6 || N == 8") == (
    function(before, "stable_direct_body")
)
opt = old.split("mod opt_split {", 1)[1].split("mod backing {", 1)[0]
general = function(after, "general_direct_body")
assert general == function(opt, "general_direct_body").replace(
    "N == 6 || N == 8", "N == 7"
)
restored = after.replace(general + "\n\n", "", 1)
new_names = ["general_direct_u64_n7", "stable_direct_u64_n6", "stable_direct_u64_n7"]
for name in new_names:
    route, n = name.split("_direct_u64_n")
    comment = "        // N7 merges unequal halves of length 3 and 4.\n" if n == "7" else ""
    expected = (
        f"    fn {name}() {{\n{comment}        {route}_direct_body::<{n}>();\n    }}"
    )
    assert function(after, name) == expected
    block = "    #[kani::proof]\n    #[kani::unwind(34)]\n" + expected + "\n\n"
    assert restored.count(block) == 1
    restored = restored.replace(block, "", 1)
restored = restored.replace(guard, "N == 6 || N == 8", 1)
assert now.split("mod backing {", 1)[0] + "mod backing {" + restored == old
assert max(map(len, now.splitlines())) <= 100
assert git("diff", "--name-only", BASE, "--", *PATHS).decode().splitlines() == [MERGE]

identities = {}
for label, sha in SOURCES.items():
    changes = git("diff", "--name-only", sha, BASE, "--", *PATHS).decode().splitlines()
    assert set(changes) <= {MERGE, NETWORK}, (label, changes)
    for path in changes:
        historic, baseline = blob(sha, path), blob(BASE, path)
        assert baseline.startswith(historic), (label, path)
        comment = (
            "// Matched backing pilot:" if path == MERGE
            else "// Stable-only dispatch isolates scratch shape from the unstable route."
        )
        assert baseline[len(historic):].startswith("\n" + comment), (label, path)
    identities[label] = dict(source_sha=sha, unchanged_except_appended_backing=changes)

measurement = json.loads((OUT / "measurement.request.json").read_text())
diagnostic = json.loads((OUT / "diagnostic.request.json").read_text())
prefix = "slice::sort::shared::smallsort::verify::merge::"
full_names = [
    "opt_split::general_direct_u64_n6", "backing::general_direct_u64_n7",
    "opt_split::general_direct_u64_n8", "backing::stable_direct_u64_n6",
    "backing::stable_direct_u64_n7", "backing::stable_direct_u64_n8",
]
for request, kind, jobs, names in (
    (measurement, "measurement", 1, ["backing::" + name for name in new_names]),
    (diagnostic, "diagnostic", 3, full_names),
):
    assert request["request_id"] == f"backing2-{kind}-20261031"
    assert request["kind"] == kind and request["kani_jobs"] == jobs
    assert request["agent"] == "k1-network" and request["controls"] is True
    assert request["runner"] == "gcb-e2-standard-4"
    assert request["harness_timeout_minutes"] == 10
    assert request["harnesses"] == [dict(name=prefix + n, expect="SUCCESS") for n in names]
active_request = (OUT.parent / "RUN-REQUEST.json").read_bytes()
assert active_request in [
    (OUT / f"{kind}.request.json").read_bytes() for kind in ("measurement", "diagnostic")
]
result = dict(
    base_sha=BASE, merge_rs_sha256=hashlib.sha256(now.encode()).hexdigest(),
    exact_scope_restore=True, general_matches_opt_except_const_guard=True,
    stable_matches_backing_except_const_guard=True, adapter_oracle_probe_unchanged=True,
    other_library_and_lane_files_unchanged=True, historical_sources=identities,
    requests_exact=True, active_request_id=json.loads(active_request)["request_id"],
    local_proof_tools_run=False,
    evidence_scope="Source identity only; historical PASS is not a measurement of this SHA.",
)
(OUT / "static-audit.json").write_text(json.dumps(result, indent=2) + "\n")
print("PASS: exact scope, helper/oracle/adapter/flags identities, 3/6 request entries")
