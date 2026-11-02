"""NETTEN-LEAVES source/packet checks only. Does not run a compiler or verifier."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "58d464ce1ce3d3ad7e60325e3297fdf07d38db4c"
BASE_LIBRARY_COMMIT = "f4d3775dc505ef26e30158cfa7e78f120cd3c30e"
SMALLSORT = "library/core/src/slice/sort/shared/smallsort"
PARENT = SMALLSORT + "/verify/network/netcomp.rs"
CHILD = SMALLSORT + "/verify/network/netcomp/netten.rs"
TOOL_BASE = "30f77e859903df14b442ff9294d4fbbd44827f20"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]
REGISTRATION = ("\n// NETTEN: opt-in child with matching u8 N10 leaves; it reuses the private items above.\n"
                "mod netten;\n")
NAMES = ["netten_swap_prefix9_backing10", "netten_insert_strict_u8_begin0_tail9"]
ANNOTATIONS = {
    NAMES[0]: ["#[kani::proof_for_contract(super::swap_net9)]", "#[kani::unwind(25)]"],
    NAMES[1]: ["#[kani::proof_for_contract(super::super::super::merge::specfix::insert_tail_profile)]",
               "#[kani::unwind(25)]"],
}
COVERS = {
    NAMES[0]: ["swap taken", "swap not taken", "first to last", "last to first", "interior pair",
               "probe hits active9", "probe misses active9", "probe hits only untouched tail"],
    NAMES[1]: ["returned", "tail becomes first", "tail stays last", "interior insertion",
               "tail ties prefix value", "output differs from input", "probe hits backing10",
               "probe misses backing10"],
}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()


# Only the parent registration and the new child file change; all else is byte-identical to BASE.
assert git("diff", "--name-only", BASE, "--", "library").splitlines() == [PARENT, CHILD]
assert not git("diff", BASE_LIBRARY_COMMIT, BASE, "--", "library")
parent = (ROOT / PARENT).read_text()
assert parent == git("show", f"{BASE}:{PARENT}") + REGISTRATION
assert not git("diff", TOOL_BASE, "--", *LANE)
child = (ROOT / CHILD).read_text()
assert max(map(len, child.splitlines())) <= 100
for banned in ["kani::assume", "kani::stub", "stub_verified", "#[kani::proof]", "kani::modifies",
               "kani::requires", "kani::ensures", "static mut", "unsafe fn"]:
    assert banned not in child, banned
assert child.count("kani::any_where") == 2  # Only the distinct prefix9 swap indices.
assert child.count("#[kani::unwind(25)]") == 2
assert child.count("unsafe {") == 2

annotations, covers = {}, {}
assert re.findall(r"^fn (netten_\w+)\(\)", child, re.M) == NAMES
for i, name in enumerate(NAMES):
    pos = child.index("fn " + name + "()")
    block = child[child.rfind("\n}\n", 0, pos) + 3:pos]
    annotations[name] = re.findall(r"#\[kani::[^\n]+", block)
    assert annotations[name] == ANNOTATIONS[name], (name, annotations[name])
    end = child.index(NAMES[i + 1]) if i + 1 < len(NAMES) else len(child)
    body = child[pos:end]
    found = re.findall(r'kani::cover\([^;]*"netten (?:swap|insert): ([^"]+)"\)', body, re.S)
    covers[name] = found
    assert found == COVERS[name], (name, found)

swap = child[child.index("fn " + NAMES[0]):child.index("fn " + NAMES[1])]
assert "let mut v: [u8; 10] = kani::any();" in swap and "let probe: u8 = kani::any();" in swap
assert "swap_net9(base.add(0), a, b, cmp, probe)" in swap
assert "let cmp: U8Cmp = StrictU8::CMP;" in swap and "[u8; 9]" not in swap
ins = child[child.index("fn " + NAMES[1]):]
assert ins.index("StrictU8::set_probe(kani::any());") < ins.index("let mut v: [u8; 10] = kani::any();")
assert "insert_tail_profile::<StrictU8>(base.add(0), base.add(9), cmp)" in ins
assert "let cmp: U8Cmp = StrictU8::CMP;" in ins
assert ins.index("let pre = v;") < ins.index("insert_tail_profile::<StrictU8>(")
assert ins.index("insert_tail_profile::<StrictU8>(") < ins.index("kani::cover(true")

# Existing targets are byte-identical: swap_net9 contract/body and insert_tail_profile in specfix.
for path in [SMALLSORT + ".rs", SMALLSORT + "/verify/merge/specfix.rs",
             SMALLSORT + "/verify/network.rs", "library/core/src/ub_checks.rs"]:
    assert (ROOT / path).read_text() == git("show", f"{BASE}:{path}"), path

pfc = subprocess.check_output(["python3", str(HERE.parent / "integwrapfix/pfc_order.py"),
                               str(ROOT / SMALLSORT)], text=True).strip()
assert pfc == "ordinary pfc sites 20 bad 0", pfc
assert parent.index("unsafe fn swap_net9") < parent.index("mod netten;")

spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)
ordinary, files = inv.inventory(False)
controls, cfg_files = inv.inventory(True)
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
assert [r["name"] for r in ordinary] == sorted(expected) and len(ordinary) == 200
prefix = inv.PREFIX + "network::netcomp::"
old_controls = [r["name"] for r in controls if not r["name"].startswith(prefix + "netten::")]
assert len(old_controls) == 395
assert [r["name"] for r in controls] == sorted(old_controls + [prefix + "netten::" + n for n in NAMES])
assert len(controls) == 397

request_path = HERE.parent / "RUN-REQUEST.json"
assert (HERE / "g1.request.json").read_bytes() == request_path.read_bytes()
request = json.loads(request_path.read_text())
assert request["agent"] == "k1-merge" and request["request_id"].startswith("netten-leaves-")
assert [r["name"] for r in request["harnesses"]] == [prefix + "netten::" + n for n in NAMES]
assert [r["expect"] for r in request["harnesses"]] == ["SUCCESS", "SUCCESS"]
assert all("expect_check" not in r for r in request["harnesses"])
assert request["kind"] == "measurement" and request["controls"] is True
assert request["kani_jobs"] == 1 and request["uninit_checks"] is False
assert request["harness_timeout_minutes"] == 10 and request["runner"] == "gcb-e2-standard-4"

dependencies = [SMALLSORT + ".rs", SMALLSORT + "/verify/network.rs", PARENT, CHILD,
                SMALLSORT + "/verify/merge/specfix.rs", "library/core/src/ub_checks.rs"] + LANE[4:7]
report = dict(status="PASS", base=BASE, base_library_commit=BASE_LIBRARY_COMMIT,
              library_commit=git("log", "-1", "--format=%H", "--", "library").strip(),
              library_tree=git("rev-parse", "HEAD:library").strip(),
              ordinary_exact=200, controls_exact=397, controls_before=395, added=NAMES,
              changed_library_files=[PARENT, CHILD], parent_change="registration only",
              runtime_targets_specfix_network_unchanged=True, protected_tooling_unchanged=True,
              pfc_order=pfc, annotations=annotations, covers=covers,
              request_sha256=hashlib.sha256(request_path.read_bytes()).hexdigest(),
              dependency_sha256={p: sha((ROOT / p).read_text()) for p in dependencies},
              scope="Static source/packet checks only; compile, proof and covers NOT_RUN before GO.")
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items()
                  if k not in ["annotations", "covers", "dependency_sha256"]}, indent=2))
