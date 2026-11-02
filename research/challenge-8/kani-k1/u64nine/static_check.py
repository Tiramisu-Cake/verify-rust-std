"""U64-N9 source/packet checks only. Does not run a compiler or verifier."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "58d464ce1ce3d3ad7e60325e3297fdf07d38db4c"  # NETCOMP2 record commit (task base)
BASE_LIB = "f4d3775dc505ef26e30158cfa7e78f120cd3c30e"
VERIFY = "library/core/src/slice/sort/shared/smallsort/verify/"
MODULE = VERIFY + "network/u64nine.rs"
NETWORK = VERIFY + "network.rs"
TOOL_BASE = "30f77e859903df14b442ff9294d4fbbd44827f20"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]
REGISTRATION = "\n#[cfg(kani_smallsort_controls)]\nmod u64nine;\n"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()


source = (ROOT / MODULE).read_text()
network = (ROOT / NETWORK).read_text()
# Library: only the new module and the appended cfg-gated registration.
assert git("rev-parse", f"{BASE}:library") == git("rev-parse", f"{BASE_LIB}:library")
assert sorted(git("diff", "--name-only", BASE, "--", "library").splitlines()) == [NETWORK, MODULE]
assert network == git("show", f"{BASE}:{NETWORK}") + REGISTRATION
assert not git("diff", BASE, "--", "library", f":(exclude){MODULE}", f":(exclude){NETWORK}")
assert not git("diff", TOOL_BASE, "--", *LANE)
assert "kani::assume" not in source and "kani::stub(" not in source.split("#[derive")[0]
assert source.count("kani::any_where") == 2  # Only distinct leaf pair indices.
assert source.count("#[kani::unwind(25)]") == 4
assert max(map(len, source.splitlines())) <= 100
# No u8/u32 narrowing of payload/probe; the only u8 mention is the widening cover constant.
assert "as u8" not in source and "as u32" not in source and "u32" not in source
assert source.count("u8::") == 1 and "probe > u8::MAX as u64" in source
assert "U8Cmp" not in source and "StrictU8" not in source and "netcomp" not in source
assert "LtU64" not in source

annotations = {}
names = re.findall(r"^fn (u64nine_\w+)\(\)", source, re.M)
assert names == ["u64nine_leaf_u64_n9", "u64nine_composed_u64_n9", "u64nine_wrong_cmp_u64_n9",
                 "u64nine_count_negative_u64_n9"], names
for name in names:
    pos = source.index("fn " + name + "()")
    block = source[source.rfind("\n}\n", 0, pos) + 3:pos]
    annotations[name] = re.findall(r"#\[kani::[^\n]+", block)
    if "leaf" in name:
        want = ["#[kani::proof_for_contract(swap_u64_net9)]", "#[kani::unwind(25)]"]
    else:
        want = ["#[kani::proof]", "#[kani::stub(swap_if_less, adapter_u64nine)]",
                "#[kani::stub_verified(swap_u64_net9)]", "#[kani::unwind(25)]"]
    assert annotations[name] == want, (name, annotations[name])

assert source.count("impl SwapBridgeU64Nine<U64Cmp> for u64") == 1
assert source.count("impl SwapBridgeU64Nine") == 1 and source.count("impl ") == 1
assert source.count("type U64Cmp = fn(&u64, &u64) -> bool;") == 1
assert "old(count9_u64(v, probe)) == count9_u64(v, probe)" in source
assert "swap_u64_net9(v, a, b, *is_less, ctx.probe)" in source
assert source.count("addr_of_mut!(CONTEXT_U64_NINE)") == 1
assert source.count("addr_of_mut!(CONTEXT_U64_NINE.hits)") == 1
assert source.count("#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]") == 1
assert source.index("unsafe fn swap_u64_net9") < source.index(
    "#[kani::proof_for_contract(swap_u64_net9)]")
target = source[source.index("unsafe fn swap_u64_net9"):source.index("#[kani::proof_for_contract")]
assert "let mut actual: U64Cmp = cmp;" in target and "swap_if_less(v, a, b, &mut actual)" in target
assert "CONTEXT" not in target and "context()" not in target
leaf = source[source.index("fn u64nine_leaf_u64_n9"):source.index("#[derive")]
assert "context" not in leaf.lower() and "stub" not in leaf
assert "let cmp: U64Cmp = StrictU64::CMP;" in leaf and "let probe: u64 = kani::any();" in leaf
helpers = source[source.index("fn check_context("):source.index("#[kani::proof]\n")]
assert "kani::cover" not in helpers
assert 'kani::assert(ctx.hits == 25, "u64nine N9: complete actual hit count")' in helpers
negative = source[source.index("fn u64nine_count_negative_u64_n9()"):]
assert "const P: u64 = 1u64 << 40;" in negative and "let mut v = [P; 9];" in negative
assert negative.index("run9(") < negative.index("v[8] = 1u64 << 41;")
assert negative.index("v[8] = 1u64 << 41;") < negative.index("kani::assert(is_sorted_by")
assert negative.index("kani::assert(is_sorted_by") < negative.index("corrupted count check reached")
assert negative.index("corrupted count check reached") < negative.index("full-value count preserved")
assert ((1 << 41) & 0xFFFF_FFFF) == ((1 << 40) & 0xFFFF_FFFF) and (1 << 41) > (1 << 40)
wrong = source[source.index("fn u64nine_wrong_cmp_u64_n9()"):source.index("fn u64nine_count_negative")]
assert "let mut cmp: U64Cmp = always_true_u64;" in wrong and "register(&mut v, probe);" in wrong
assert "kani::assert" not in wrong and "run9" not in wrong

covers = {}
roots = {"u64nine_leaf_u64_n9": [leaf], "u64nine_composed_u64_n9": [], "u64nine_wrong_cmp_u64_n9": [],
         "u64nine_count_negative_u64_n9": []}
adapter = source[source.index("impl SwapBridgeU64Nine"):source.index("// Same raw parameters")]
composed = source[source.index("fn u64nine_composed_u64_n9()"):source.index("fn always_true_u64")]
roots["u64nine_composed_u64_n9"] = [adapter, composed]
roots["u64nine_wrong_cmp_u64_n9"] = [wrong, adapter]
roots["u64nine_count_negative_u64_n9"] = [adapter, negative]
lit = re.compile(r'kani::cover\(\s*[^"]*?"([^"]+)"', re.S)
for name, parts in roots.items():
    covers[name] = [m for p in parts for m in lit.findall(p)]
assert [len(covers[n]) for n in names] == [7, 7, 2, 3], {n: len(c) for n, c in covers.items()}
assert sum(len(lit.findall(source)) for _ in [0]) == 7 + 1 + 6 + 1 + 2  # leaf, adapter, B, wrong, neg

spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)
ordinary, files = inv.inventory(False)
controls, cfg_files = inv.inventory(True)
assert files == cfg_files
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
old_names = (HERE.parent / "cleanup/cfg-on-expected.txt").read_text().splitlines()
old_names += [inv.PREFIX + "network::" + n for n in [
    "netnine_full_value_count_u8_n9", "netnine_full_value_count_u8_n9_negative",
    "netthirteen_full_value_count_u8_n13", "netthirteen_full_value_count_u8_n13_negative"]]
old_names += [inv.PREFIX + "network::netcomp::" + n for n in [
    "netcomp_leaf_u8_n9", "netcomp_direct_u8_n9", "netcomp_composed_u8_n9", "netcomp_wrong_cmp_u8_n9",
    "netcomp_count_negative_u8_n9", "netcomp_leaf_u8_n13", "netcomp_composed_u8_n13",
    "netcomp_wrong_cmp_u8_n13", "netcomp_count_negative_u8_n13"]]
assert len(old_names) == 395
assert [r["name"] for r in ordinary] == sorted(expected) and len(ordinary) == 200
prefix = inv.PREFIX + "network::u64nine::"
assert [r["name"] for r in controls] == sorted(old_names + [prefix + n for n in names])
assert len(controls) == 399

request = json.loads((HERE / "g1.request.json").read_text())
assert (HERE / "g1.request.json").read_bytes() == (HERE.parent / "RUN-REQUEST.json").read_bytes()
full = "slice::sort::shared::smallsort::verify::network::u64nine::"
assert [r["name"] for r in request["harnesses"]] == [full + n for n in names]
assert [r["expect"] for r in request["harnesses"]] == ["SUCCESS", "SUCCESS", "FAILED", "FAILED"]
assert request["agent"] == "k1-merge" and request["runner"] == "gcb-e2-standard-4"
assert request["request_id"].startswith("u64nine-")
assert request["kind"] == "measurement" and request["controls"] is True
assert request["kani_jobs"] == 1 and request["uninit_checks"] is False
assert request["harness_timeout_minutes"] == 10
literal_lines = {}
for row in request["harnesses"]:
    if row["expect"] == "FAILED":
        quoted = '"' + row["expect_check"] + '"'
        assert source.count(quoted) == 1, row["expect_check"]
        literal_lines[row["expect_check"]] = source[:source.index(quoted)].count("\n") + 1
        ln = literal_lines[row["expect_check"]]
        assert "kani::assert(" in "".join(source.splitlines()[ln - 3:ln])

dependencies = ["library/core/src/slice/sort/shared/smallsort.rs", NETWORK, MODULE,
                VERIFY + "merge/specfix.rs", "library/core/src/ub_checks.rs"] + LANE[4:7]
report = dict(status="PASS", base=BASE, base_library_tree=git("rev-parse", f"{BASE}:library").strip(),
              library_tree=git("rev-parse", "HEAD:library").strip(),
              ordinary_exact=200, controls_exact=399, u64nine_added=4,
              library_change="new network/u64nine.rs + appended cfg-gated mod registration only",
              runtime_and_protected_tooling_unchanged=True, annotations=annotations,
              covers_required=covers, failed_literal_lines=literal_lines,
              source_sha256=sha(source), request_sha256=sha((HERE / "g1.request.json").read_text()),
              dependency_sha256={p: sha((ROOT / p).read_text()) for p in dependencies},
              scope="Static source/packet checks only; compile, proof and covers NOT_RUN before GO.")
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items()
                  if k not in ["annotations", "dependency_sha256", "covers_required"]}, indent=2))
