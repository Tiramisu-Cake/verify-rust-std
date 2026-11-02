"""MERGESTEP source/packet checks only. Does not run a compiler or verifier."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "e547e6dca1"  # TASK-MERGESTEP staging commit on NET18-LEAVES 7d8b21728b.
BASE_LIBRARY_TREE = "1fa41b3a5f101ee3981787f71588bfc22e2aae5b"
VERIFY = "library/core/src/slice/sort/shared/smallsort/verify/"
PARENT = VERIFY + "network/netcomp.rs"
MODULE = VERIFY + "network/netcomp/mergestep.rs"
TOOL_BASE = "30f77e859903df14b442ff9294d4fbbd44827f20"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]
REGISTRATION = ("\n// MERGESTEP step summaries and actual merge4 calibration: opt-in child module after"
                " all above.\nmod mergestep;\n")
PREFIX_MOD = "network::netcomp::mergestep::"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()


assert git("rev-parse", f"{BASE}:library").strip() == BASE_LIBRARY_TREE
# Library change: exactly the new file plus the trailing registration in netcomp.rs.
assert sorted(git("diff", "--name-only", BASE, "--", "library").splitlines()) == [PARENT, MODULE]
assert (ROOT / PARENT).read_text() == git("show", f"{BASE}:{PARENT}") + REGISTRATION
assert not git("diff", TOOL_BASE, "--", *LANE)
for unchanged in ["library/core/src/slice/sort/shared/smallsort.rs", VERIFY + "network.rs",
                  VERIFY + "merge/specfix.rs", VERIFY + "network/netcomp/neteighteen.rs"]:
    assert (ROOT / unchanged).read_text() == git("show", f"{BASE}:{unchanged}"), unchanged
source = (ROOT / MODULE).read_text()
for banned in ["kani::assume", "#[cfg(", "pub ", "pub(", "stub(panic_on_ord_violation",
               "stub(bidirectional_merge", "stub(merge_profile", "addr_of_mut!(STEP_CONTEXT."]:
    assert banned not in source, banned
assert max(map(len, source.splitlines())) <= 100
# Context is written only by `register`, outside every target; adapters only read it.
assert source.count("addr_of_mut!(STEP_CONTEXT)") == 1
reg = source[source.index("fn register("):source.index("fn index_in(")]
assert "addr_of_mut!(STEP_CONTEXT)" in reg
assert source.count("set_probe(") == 2  # positive any(); controls 0, both before the merge call.

names = re.findall(r"^fn (mergestep_\w+)\(\)", source, re.M)
assert names == ["mergestep_up_leaf_u8", "mergestep_down_leaf_u8", "mergestep_composed_merge4_u8",
                 "mergestep_up_binding_negative_u8", "mergestep_down_binding_negative_u8",
                 "mergestep_count_negative_u8"], names
SUBST = ["#[kani::stub(merge_up, up_adapter)]", "#[kani::stub(merge_down, down_adapter)]",
         "#[kani::stub_verified(up_step_u8)]", "#[kani::stub_verified(down_step_u8)]"]
want = {
    "mergestep_up_leaf_u8": ["#[kani::proof_for_contract(up_step_u8)]", "#[kani::unwind(34)]"],
    "mergestep_down_leaf_u8": ["#[kani::proof_for_contract(down_step_u8)]",
                               "#[kani::unwind(34)]"],
    "mergestep_composed_merge4_u8": [
        "#[kani::proof_for_contract(super::super::super::merge::specfix::merge_profile)]",
        *SUBST, "#[kani::unwind(34)]"],
    "mergestep_up_binding_negative_u8": ["#[kani::proof]", *SUBST, "#[kani::unwind(34)]"],
    "mergestep_down_binding_negative_u8": ["#[kani::proof]", *SUBST, "#[kani::unwind(34)]"],
    "mergestep_count_negative_u8": ["#[kani::proof]", *SUBST, "#[kani::unwind(34)]"],
}
annotations, bodies = {}, {}
for name in names:
    pos = source.index("fn " + name + "()")
    block = source[source.rfind("\n}\n", 0, pos) + 3:pos]
    annotations[name] = re.findall(r"#\[kani::[^\n]+", block)
    assert annotations[name] == want[name], (name, annotations[name])
    bodies[name] = source[pos:source.index("\n}\n", pos)]
# Contract attributes: 2 targets x 5, plus the root annotations above.
assert source.count("#[kani::") == 10 + sum(len(v) for v in want.values())
# Targets precede their PFCs; each forwarder calls the real raw helper with the received cmp.
assert source.index("unsafe fn up_step_u8") < source.index("fn mergestep_up_leaf_u8")
assert source.index("unsafe fn down_step_u8") < source.index("fn mergestep_down_leaf_u8")
assert "merge_up(left, right, dst, &mut actual)" in source
assert "merge_down(left, right, dst, &mut actual)" in source
assert source.count("let mut actual: U8Cmp = cmp;") == 2
# Adapters pass the received comparator, never the canonical constant, to the verified step.
assert "up_step_u8(l, r, d, cmp)" in source and "down_step_u8(l, r, d, cmp)" in source
assert source.count("let cmp = *is_less;") == 2
for literal in ["mergestep actual up adapter binding control",
                "mergestep actual down adapter binding control",
                "mergestep calibration negative: full-value count preserved"]:
    assert source.count('"' + literal + '"') == 1, literal
# Decoders: explicit bool->usize, wrapping arithmetic only.
assert "l.wrapping_add(take_left as usize), r.wrapping_add((!take_left) as usize)" in source
assert "l.wrapping_sub(take_left as usize), r.wrapping_sub((!take_left) as usize)" in source
for leaf in ["mergestep_up_leaf_u8", "mergestep_down_leaf_u8"]:
    body = bodies[leaf]
    assert "let src: [u8; 18] = kani::any();" in body
    assert "MaybeUninit::<[u8; 32]>::uninit()" in body and "let cmp: U8Cmp = StrictU8::CMP;" in body
covers = {n: re.findall(r'kani::cover\([^"]*"([^"]+)"', bodies[n]) for n in names}
assert len(covers["mergestep_up_leaf_u8"]) == 11 and len(covers["mergestep_down_leaf_u8"]) == 12
assert len(covers["mergestep_composed_merge4_u8"]) == 6
merge = bodies["mergestep_composed_merge4_u8"]
assert merge.index("StrictU8::set_probe(kani::any())") < merge.index("register(")
assert merge.index("register(") < merge.index("merge_profile::<StrictU8>(&src[..ACTIVE4], dst, cmp)")
count = bodies["mergestep_count_negative_u8"]
assert count.index("check_merge4(") < count.index("*dst.add(3) = 1")

# Existing ordinary set and cfg-on composition.
spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)
ordinary, files = inv.inventory(False)
controls, cfg_files = inv.inventory(True)
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
assert [r["name"] for r in ordinary] == sorted(expected) and len(ordinary) == 200
prefix = inv.PREFIX + PREFIX_MOD
new = sorted(r["name"] for r in controls if r["name"].startswith(prefix))
assert new == sorted(prefix + n for n in names)
assert len(controls) == 404

request = json.loads((HERE / "g1.request.json").read_text())
assert (HERE / "g1.request.json").read_bytes() == (HERE.parent / "RUN-REQUEST.json").read_bytes()
assert [r["name"] for r in request["harnesses"]] == [prefix + n for n in names]
expect = ["SUCCESS"] * 3 + ["FAILED"] * 3
assert [r["expect"] for r in request["harnesses"]] == expect
assert [r.get("expect_check") for r in request["harnesses"][3:]] == [
    "mergestep actual up adapter binding control", "mergestep actual down adapter binding control",
    "mergestep calibration negative: full-value count preserved"]
assert request["request_id"].startswith("mergestep-") and request["agent"] == "k1-network"
assert request["kind"] == "measurement" and request["controls"] is True
assert request["kani_jobs"] == 1 and request["uninit_checks"] is False
assert request["harness_timeout_minutes"] == 10
assert request["runner"] == "gcb-e2-standard-4"

dependencies = ["library/core/src/slice/sort/shared/smallsort.rs", VERIFY + "network.rs",
                PARENT, MODULE, VERIFY + "merge/specfix.rs", "library/core/src/ub_checks.rs"] + LANE[4:7]
report = dict(status="PASS", base=git("rev-parse", BASE).strip(), base_library_tree=BASE_LIBRARY_TREE,
              library_tree=git("rev-parse", "HEAD:library").strip(),
              ordinary_exact=200, controls_exact=404, added=6, annotations=annotations, covers=covers,
              netcomp_rs_change="trailing child-module registration only",
              runtime_specfix_network_neteighteen_tooling_unchanged=True,
              source_sha256=sha(source), request_sha256=sha((HERE / "g1.request.json").read_text()),
              dependency_sha256={p: sha((ROOT / p).read_text()) for p in dependencies},
              scope="Static source/packet checks only; compile, proof and covers NOT_RUN before GO.")
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items()
                  if k not in ["annotations", "dependency_sha256", "covers"]}, indent=2))
