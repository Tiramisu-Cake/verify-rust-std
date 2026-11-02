"""U64-N13 source/packet checks only. Does not run a compiler or verifier."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "9ab925b1578b9102e3009c0ec940c5c9cc0280cb"  # U64-N9 record commit (task base)
BASE_LIB = "fddf308321046a8cd8f5526622a5e2353d79830e"
VERIFY = "library/core/src/slice/sort/shared/smallsort/verify/"
MODULE = VERIFY + "network/u64nine/uthirteen.rs"
PARENT = VERIFY + "network/u64nine.rs"
SMALLSORT = "library/core/src/slice/sort/shared/smallsort.rs"
TOOL_BASE = "30f77e859903df14b442ff9294d4fbbd44827f20"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]
REGISTRATION = "\n// U64-N13: separate exact-13 typed child; the N9 items above are unchanged.\nmod uthirteen;\n"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()


source = (ROOT / MODULE).read_text()
parent = (ROOT / PARENT).read_text()
# Library: only the new child module and its appended registration in the parent.
assert git("rev-parse", f"{BASE}:library") == git("rev-parse", f"{BASE_LIB}:library")
assert git("rev-parse", f"{BASE}:library").strip() == "d22566ab5a685df2608ddb756714e51ad288f08d"
assert sorted(git("diff", "--name-only", BASE, "--", "library").splitlines()) == [PARENT, MODULE]
assert parent == git("show", f"{BASE}:{PARENT}") + REGISTRATION
assert not git("diff", BASE, "--", "library", f":(exclude){MODULE}", f":(exclude){PARENT}")
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
# No N9 item is called or substituted; no 9/8/7 literal fixture carried over.
for n9 in ["count9_u64", "run9", "adapter_u64nine", "swap_u64_net9", "region9_u64", "register(",
           "check_context(", "CONTEXT_U64_NINE", "ContextU64Nine", "SwapBridgeU64Nine", "context()",
           "sort9", "sort25", "[u64; 9]", "[P; 9]", "v[8]"]:
    assert n9 not in source, n9
assert not re.search(r"\b(?:9|8|7)\b", source.replace("u64nine", "")), re.findall(
    r".*\b(?:9|8|7)\b.*", source)
assert source.startswith("//!") and "use super::{U64Cmp, always_true_u64, canonical};" in source

annotations = {}
names = re.findall(r"^fn (u64thirteen_\w+)\(\)", source, re.M)
assert names == ["u64thirteen_leaf_u64_n13", "u64thirteen_composed_u64_n13",
                 "u64thirteen_wrong_cmp_u64_n13", "u64thirteen_count_negative_u64_n13"], names
for name in names:
    pos = source.index("fn " + name + "()")
    block = source[source.rfind("\n}\n", 0, pos) + 3:pos]
    annotations[name] = re.findall(r"#\[kani::[^\n]+", block)
    if "leaf" in name:
        want = ["#[kani::proof_for_contract(swap_u64_net13)]", "#[kani::unwind(25)]"]
    else:
        want = ["#[kani::proof]", "#[kani::stub(swap_if_less, adapter_u64thirteen)]",
                "#[kani::stub_verified(swap_u64_net13)]", "#[kani::unwind(25)]"]
    assert annotations[name] == want, (name, annotations[name])
all_annotations = re.findall(r"#\[kani::[^\n]+", source)
assert len(all_annotations) == 6 + 2 + 3 * 4, all_annotations  # target6, leaf2, three roots x4

assert source.count("impl SwapBridgeU64Thirteen<U64Cmp> for u64") == 1
assert source.count("impl SwapBridgeU64Thirteen") == 1 and source.count("impl ") == 1
assert "old(count13_u64(v, probe)) == count13_u64(v, probe)" in source
assert "swap_u64_net13(v, a, b, *is_less, ctx.probe)" in source
assert source.count("addr_of_mut!(CONTEXT_U64_THIRTEEN)") == 1
assert source.count("addr_of_mut!(CONTEXT_U64_THIRTEEN.hits)") == 1
assert source.count("addr_of_mut!") == 2
assert source.count("#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]") == 1
assert source.index("unsafe fn swap_u64_net13") < source.index(
    "#[kani::proof_for_contract(swap_u64_net13)]")
target = source[source.index("unsafe fn swap_u64_net13"):source.index("#[kani::proof_for_contract")]
assert "let mut actual: U64Cmp = cmp;" in target and "swap_if_less(v, a, b, &mut actual)" in target
assert "CONTEXT" not in target and "context13()" not in target
contract = source[source.index("#[kani::requires(canonical(cmp))]"):source.index("unsafe fn swap_u64_net13")]
assert re.search(r"\bcmp\(", contract) is None and "CONTEXT" not in contract and "context" not in contract
leaf = source[source.index("fn u64thirteen_leaf_u64_n13"):source.index("#[derive")]
assert "context" not in leaf.lower() and "stub" not in leaf
assert "let cmp: U64Cmp = StrictU64::CMP;" in leaf and "let probe: u64 = kani::any();" in leaf
assert "let mut v: [u64; 13] = kani::any();" in leaf and "while i < 13" in leaf
adapter = source[source.index("impl SwapBridgeU64Thirteen"):source.index("// Same raw parameters")]
assert adapter.index('"u64thirteen canonical comparator required"') < adapter.index(
    "if !accepted {\n            return;") < adapter.index("swap_u64_net13(") < adapter.index(
    "CONTEXT_U64_THIRTEEN.hits) += 1") < adapter.index("count13_u64(v, ctx.probe)")
assert "StrictU64::CMP" not in adapter  # canonical value is never substituted
helpers = source[source.index("fn check_context13("):source.index("#[kani::proof]\n")]
assert "kani::cover" not in helpers
assert 'kani::assert(ctx.hits == 45, "u64thirteen N13: complete actual hit count")' in helpers
negative = source[source.index("fn u64thirteen_count_negative_u64_n13()"):]
assert "const P: u64 = 1u64 << 40;" in negative and "let mut v = [P; 13];" in negative
assert "let probe = P;" in negative
assert negative.index("run13(") < negative.index("v[12] = 1u64 << 41;")
assert negative.index("v[12] = 1u64 << 41;") < negative.index("kani::assert(is_sorted_by")
assert negative.index("kani::assert(is_sorted_by") < negative.index("corrupted count check reached")
assert negative.index("corrupted count check reached") < negative.index("full-value count preserved")
assert ((1 << 41) & 0xFFFF_FFFF) == ((1 << 40) & 0xFFFF_FFFF) and (1 << 41) > (1 << 40)
wrong = source[source.index("fn u64thirteen_wrong_cmp_u64_n13()"):source.index(
    "fn u64thirteen_count_negative")]
assert "let mut cmp: U64Cmp = always_true_u64;" in wrong and "register13(&mut v, probe);" in wrong
assert "kani::assert" not in wrong and "run13" not in wrong
assert "<u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);" in wrong
composed = source[source.index("fn u64thirteen_composed_u64_n13()"):source.index(
    "fn u64thirteen_wrong_cmp")]
assert "let mut v: [u64; 13] = kani::any();" in composed and "let probe: u64 = kani::any();" in composed
assert "let mut cmp: U64Cmp = StrictU64::CMP;" in composed
assert composed.index("run13(") < composed.index("hits == 45")

covers = {}
roots = {"u64thirteen_leaf_u64_n13": [leaf], "u64thirteen_composed_u64_n13": [adapter, composed],
         "u64thirteen_wrong_cmp_u64_n13": [wrong, adapter],
         "u64thirteen_count_negative_u64_n13": [adapter, negative]}
lit = re.compile(r'kani::cover\(\s*[^"]*?"([^"]+)"', re.S)
for name, parts in roots.items():
    covers[name] = [m for p in parts for m in lit.findall(p)]
assert [len(covers[n]) for n in names] == [7, 7, 2, 3], {n: len(c) for n, c in covers.items()}
assert len(lit.findall(source)) == 7 + 1 + 6 + 1 + 2  # leaf, adapter, B, wrong, neg
assert all(len(set(c)) == len(c) for c in covers.values())

# The 45 actual raw exchange edges of sort13_optimal in the unchanged runtime source.
runtime = (ROOT / SMALLSORT).read_text().splitlines()
start = next(i for i, l in enumerate(runtime) if l.startswith("fn sort13_optimal"))
end = next(i for i in range(start, len(runtime)) if runtime[i] == "}")
calls = [(i + 1, l.strip()) for i, l in enumerate(runtime[start:end], start)
         if "swap_if_less(" in l]
assert len(calls) == 45
tsv = (HERE / "actual-calls.tsv").read_text().splitlines()
assert len(tsv) == 46 and tsv[0].startswith("N\tordinal\tline\traw_actual_call")
for k, (row, (line, text)) in enumerate(zip(tsv[1:], calls), 1):
    f = row.split("\t")
    assert f[:4] == ["13", str(k), str(line), text], (row, line, text)
    a, b = map(int, re.fullmatch(r"swap_if_less\(v_base, (\d+), (\d+), is_less\);", text).groups())
    assert a < 13 and b < 13 and a != b
    assert f[4:] == ["adapter_u64thirteen::<u64,U64Cmp>", "swap_u64_net13",
                     "u64thirteen_leaf_u64_n13", "NOT_RUN_BEFORE_GO"]
assert sum("sort13_optimal(region, is_less);" in l for l in runtime) == 1

spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)
ordinary, files = inv.inventory(False)
controls, cfg_files = inv.inventory(True)
assert files == cfg_files and MODULE in files
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
old_names = (HERE.parent / "cleanup/cfg-on-expected.txt").read_text().splitlines()
old_names += [inv.PREFIX + "network::" + n for n in [
    "netnine_full_value_count_u8_n9", "netnine_full_value_count_u8_n9_negative",
    "netthirteen_full_value_count_u8_n13", "netthirteen_full_value_count_u8_n13_negative"]]
old_names += [inv.PREFIX + "network::netcomp::" + n for n in [
    "netcomp_leaf_u8_n9", "netcomp_direct_u8_n9", "netcomp_composed_u8_n9", "netcomp_wrong_cmp_u8_n9",
    "netcomp_count_negative_u8_n9", "netcomp_leaf_u8_n13", "netcomp_composed_u8_n13",
    "netcomp_wrong_cmp_u8_n13", "netcomp_count_negative_u8_n13"]]
old_names += [inv.PREFIX + "network::u64nine::" + n for n in [
    "u64nine_leaf_u64_n9", "u64nine_composed_u64_n9", "u64nine_wrong_cmp_u64_n9",
    "u64nine_count_negative_u64_n9"]]
assert len(old_names) == 399
assert [r["name"] for r in ordinary] == sorted(expected) and len(ordinary) == 200
prefix = inv.PREFIX + "network::u64nine::uthirteen::"
assert [r["name"] for r in controls] == sorted(old_names + [prefix + n for n in names])
assert len(controls) == 403

request = json.loads((HERE / "g1.request.json").read_text())
assert (HERE / "g1.request.json").read_bytes() == (HERE.parent / "RUN-REQUEST.json").read_bytes()
full = "slice::sort::shared::smallsort::verify::network::u64nine::uthirteen::"
assert [r["name"] for r in request["harnesses"]] == [full + n for n in names]
assert [r["expect"] for r in request["harnesses"]] == ["SUCCESS", "SUCCESS", "FAILED", "FAILED"]
assert request["agent"] == "k1-merge" and request["runner"] == "gcb-e2-standard-4"
assert request["request_id"].startswith("u64thirteen-")
assert request["kind"] == "measurement" and request["controls"] is True
assert request["kani_jobs"] == 1 and request["uninit_checks"] is False
assert request["harness_timeout_minutes"] == 10
literal_lines = {}
for row in request["harnesses"]:
    if row["expect"] == "FAILED":
        quoted = '"' + row["expect_check"] + '"'
        assert source.count(quoted) == 1, row["expect_check"]
        assert row["expect_check"].startswith("u64thirteen ")
        for other in [PARENT, VERIFY + "network/netcomp.rs", VERIFY + "network.rs"]:
            assert row["expect_check"] not in (ROOT / other).read_text()
        literal_lines[row["expect_check"]] = source[:source.index(quoted)].count("\n") + 1
        ln = literal_lines[row["expect_check"]]
        assert "kani::assert(" in "".join(source.splitlines()[ln - 3:ln])

dependencies = [SMALLSORT, VERIFY + "network.rs", PARENT, MODULE, VERIFY + "merge/specfix.rs",
                "library/core/src/ub_checks.rs"] + LANE[4:7]
report = dict(status="PASS", base=BASE, base_library_tree=git("rev-parse", f"{BASE}:library").strip(),
              library_tree=git("rev-parse", "HEAD:library").strip(),
              ordinary_exact=200, controls_exact=403, u64thirteen_added=4,
              library_change="new network/u64nine/uthirteen.rs + appended child registration only",
              runtime_and_protected_tooling_unchanged=True, annotations=annotations,
              covers_required=covers, failed_literal_lines=literal_lines, raw_exchange_edges=45,
              source_sha256=sha(source), request_sha256=sha((HERE / "g1.request.json").read_text()),
              dependency_sha256={p: sha((ROOT / p).read_text()) for p in dependencies},
              scope="Static source/packet checks only; compile, proof and covers NOT_RUN before GO.")
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items()
                  if k not in ["annotations", "dependency_sha256", "covers_required"]}, indent=2))
