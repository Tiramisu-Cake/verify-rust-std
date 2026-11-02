"""NET18-LEAVES source/packet checks only. Does not run a compiler or verifier."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "58d464ce1ce3d3ad7e60325e3297fdf07d38db4c"
BASE_LIBRARY_TREE = "3b6d2a51dae08e52464f4b2b82f5168d8ba9977b"
VERIFY = "library/core/src/slice/sort/shared/smallsort/verify/"
PARENT = VERIFY + "network/netcomp.rs"
MODULE = VERIFY + "network/netcomp/neteighteen.rs"
TOOL_BASE = "30f77e859903df14b442ff9294d4fbbd44827f20"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]
REGISTRATION = ("\n// NET18-LEAVES geometry fixtures: opt-in child module after all targets and roots above.\n"
                "mod neteighteen;\n")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()


assert git("rev-parse", f"{BASE}:library").strip() == BASE_LIBRARY_TREE
# Library change: exactly the new file plus the trailing registration in netcomp.rs.
assert sorted(git("diff", "--name-only", BASE, "--", "library").splitlines()) == [PARENT, MODULE]
assert (ROOT / PARENT).read_text() == git("show", f"{BASE}:{PARENT}") + REGISTRATION
assert not git("diff", TOOL_BASE, "--", *LANE)
source = (ROOT / MODULE).read_text()
for banned in ["kani::assume", "kani::stub", "stub_verified", "set_probe(probe", "static mut",
               "#[kani::proof]", "#[cfg(", "pub "]:
    assert banned not in source, banned
assert source.count("kani::any_where") == 2  # Only the distinct local pair indices.
assert source.count("StrictU8::set_probe(kani::any())") == 1
assert max(map(len, source.splitlines())) <= 100

names = re.findall(r"^fn (net18_\w+)\(\)", source, re.M)
assert names == ["net18_swap_left_backing18", "net18_swap_right_backing18",
                 "net18_merge_strict_scratch32"], names
want = {
    "net18_swap_left_backing18": ["#[kani::proof_for_contract(super::swap_net9)]",
                                  "#[kani::unwind(25)]"],
    "net18_swap_right_backing18": ["#[kani::proof_for_contract(super::swap_net9)]",
                                   "#[kani::unwind(25)]"],
    "net18_merge_strict_scratch32": [
        "#[kani::proof_for_contract(super::super::super::merge::specfix::merge_profile)]",
        "#[kani::unwind(34)]"],
}
annotations = {}
bodies = {}
for name in names:
    pos = source.index("fn " + name + "()")
    block = source[source.rfind("\n}\n", 0, pos) + 3:pos]
    annotations[name] = re.findall(r"#\[kani::[^\n]+", block)
    assert annotations[name] == want[name], (name, annotations[name])
    bodies[name] = source[pos:source.index("\n}\n", pos)]
assert source.count("#[kani::") == 6
assert "swap_leaf18::<0>();" in bodies["net18_swap_left_backing18"]
assert "swap_leaf18::<9>();" in bodies["net18_swap_right_backing18"]
helper = source[source.index("fn swap_leaf18"):source.index("#[kani::proof_for_contract")]
assert "let mut v: [u8; 18] = kani::any();" in helper
assert "swap_net9(v.as_mut_ptr().add(OFF), a, b, cmp, probe)" in helper
assert "let cmp: U8Cmp = StrictU8::CMP;" in helper
assert helper.count("kani::cover(") == 7
merge = bodies["net18_merge_strict_scratch32"]
assert merge.index("StrictU8::set_probe(kani::any())") < merge.index("let src: [u8; 18] = kani::any();")
assert "MaybeUninit::<[u8; 32]>::uninit()" in merge
assert "merge_profile::<StrictU8>(&src, dst, cmp)" in merge
assert "let cmp: U8Cmp = StrictU8::CMP;" in merge
assert "from_raw_parts(dst as *const u8, 18)" in merge
assert merge.count("kani::cover(") == 6
assert "32" not in merge.replace("[u8; 32]", "").replace("scratch32", "")  # Tail never addressed.

# Existing targets/contracts are byte-identical (whole old netcomp.rs and specfix.rs unchanged).
spec_path = VERIFY + "merge/specfix.rs"
assert (ROOT / spec_path).read_text() == git("show", f"{BASE}:{spec_path}")

spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)
ordinary, files = inv.inventory(False)
controls, cfg_files = inv.inventory(True)
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
assert [r["name"] for r in ordinary] == sorted(expected) and len(ordinary) == 200
prefix = inv.PREFIX + "network::netcomp::neteighteen::"
new = sorted(r["name"] for r in controls if r["name"].startswith(prefix))
assert new == sorted(prefix + n for n in names)
assert len(controls) == 398

request = json.loads((HERE / "g1.request.json").read_text())
assert (HERE / "g1.request.json").read_bytes() == (HERE.parent / "RUN-REQUEST.json").read_bytes()
assert [r["name"] for r in request["harnesses"]] == [prefix + n for n in names]
assert all(r == {"name": r["name"], "expect": "SUCCESS"} for r in request["harnesses"])
assert request["request_id"].startswith("net18-leaves-")
assert request["kind"] == "measurement" and request["controls"] is True
assert request["kani_jobs"] == 1 and request["uninit_checks"] is False
assert request["harness_timeout_minutes"] == 10
assert request["runner"] == "gcb-e2-standard-4"

dependencies = ["library/core/src/slice/sort/shared/smallsort.rs", VERIFY + "network.rs",
                PARENT, MODULE, spec_path, "library/core/src/ub_checks.rs"] + LANE[4:7]
report = dict(status="PASS", base=BASE, base_library_tree=BASE_LIBRARY_TREE,
              library_tree=git("rev-parse", "HEAD:library").strip(),
              ordinary_exact=200, controls_exact=398, added=3, annotations=annotations,
              netcomp_rs_change="trailing child-module registration only",
              targets_contracts_runtime_tooling_unchanged=True,
              source_sha256=sha(source), request_sha256=sha((HERE / "g1.request.json").read_text()),
              dependency_sha256={p: sha((ROOT / p).read_text()) for p in dependencies},
              scope="Static source/packet checks only; compile, proof and covers NOT_RUN before GO.")
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k not in ["annotations", "dependency_sha256"]},
                 indent=2))
