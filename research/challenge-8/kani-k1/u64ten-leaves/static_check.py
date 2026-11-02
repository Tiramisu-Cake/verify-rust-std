"""U64-TEN-LEAVES source/packet checks only. Does not run a compiler or verifier."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "9ab925b1578b9102e3009c0ec940c5c9cc0280cb"  # U64-N9 record commit (task base)
BASE_LIBRARY_COMMIT = "fddf308321046a8cd8f5526622a5e2353d79830e"
BASE_LIBRARY_TREE = "d22566ab5a685df2608ddb756714e51ad288f08d"
SMALLSORT = "library/core/src/slice/sort/shared/smallsort"
PARENT = SMALLSORT + "/verify/network/u64nine.rs"
CHILD = SMALLSORT + "/verify/network/u64nine/tenleaves.rs"
TOOL_BASE = "30f77e859903df14b442ff9294d4fbbd44827f20"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]
REGISTRATION = ("\n// U64-TEN-LEAVES: opt-in child with matching u64 N10 leaves; it reuses the private items"
                " above.\nmod tenleaves;\n")
NAMES = ["u64ten_swap_prefix9_backing10", "u64ten_insert_strict_u64_begin0_tail9"]
ANNOTATIONS = {
    NAMES[0]: ["#[kani::proof_for_contract(super::swap_u64_net9)]", "#[kani::unwind(25)]"],
    NAMES[1]: ["#[kani::proof_for_contract(super::super::super::merge::specfix::insert_tail_profile)]",
               "#[kani::unwind(25)]"],
}
COVERS = {
    NAMES[0]: ["swap taken", "swap not taken", "first to last", "last to first", "interior pair",
               "probe hits active9", "probe misses active9", "probe hits only untouched tail",
               "high-bit probe hits backing10"],
    NAMES[1]: ["returned", "tail becomes first", "tail stays last", "interior insertion",
               "tail ties prefix value", "output differs from input", "probe hits backing10",
               "probe misses backing10", "high-bit probe hits backing10"],
}
# Exact cover predicates (whitespace-normalized source text), in order.
PREDICATES = {
    NAMES[0]: ["taken", "!taken", "a == 0 && b == 8", "a == 8 && b == 0",
               "a > 0 && a < 8 && b > 0 && b < 8", "active_hits > 0", "active_hits == 0",
               "probe == pre[9] && active_hits == 0", "probe >= (1u64 << 40) && whole_hits > 0"],
    NAMES[1]: ["true", "pre[9] < pre[0]", "pre[8] <= pre[9]", "pre[0] < pre[9] && pre[9] < pre[8]",
               "pre[9] == pre[4]", "!prefix_unchanged(&v, &pre, 0)", "hits > 0", "hits == 0",
               "probe >= (1u64 << 40) && hits > 0"],
}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()


# Only the parent registration and the new child file change; all else is byte-identical to BASE.
assert git("rev-parse", f"{BASE}:library").strip() == BASE_LIBRARY_TREE
assert git("rev-parse", f"{BASE_LIBRARY_COMMIT}:library").strip() == BASE_LIBRARY_TREE
assert git("diff", "--name-only", BASE, "--", "library").splitlines() == [PARENT, CHILD]
parent = (ROOT / PARENT).read_text()
assert parent == git("show", f"{BASE}:{PARENT}") + REGISTRATION
assert not git("diff", TOOL_BASE, "--", *LANE)
child = (ROOT / CHILD).read_text()
assert max(map(len, child.splitlines())) <= 100
for banned in ["kani::assume", "kani::stub", "stub_verified", "#[kani::proof]", "kani::modifies",
               "kani::requires", "kani::ensures", "static mut", "unsafe fn", "impl ", "trait ",
               "any_where(|&i| i < 9 && i != a && ", "[u64; 9]", "[u64; 12]"]:
    assert banned not in child, banned
# No narrowing of payload or probe; no u8 domain items; no LtU64 (x >> 1).
for banned in ["u8", "u16", "u32", " as ", "U8Cmp", "StrictU8", "netcomp", "LtU64", "lt_u64", ">> 1"]:
    assert banned not in child, banned
assert child.count("kani::any_where") == 2  # Only the distinct prefix9 swap indices.
assert child.count("kani::any()") == 4  # swap: v, probe; insert: probe, v.
assert child.count("#[kani::unwind(25)]") == 2
assert child.count("unsafe {") == 2

annotations, covers, predicates = {}, {}, {}
assert re.findall(r"^fn (u64ten_\w+)\(\)", child, re.M) == NAMES
for i, name in enumerate(NAMES):
    pos = child.index("fn " + name + "()")
    block = child[child.rfind("\n}\n", 0, pos) + 3:pos]
    annotations[name] = re.findall(r"#\[kani::[^\n]+", block)
    assert annotations[name] == ANNOTATIONS[name], (name, annotations[name])
    end = child.index(NAMES[i + 1]) if i + 1 < len(NAMES) else len(child)
    body = child[pos:end]
    found = re.findall(r'kani::cover\(\s*(.*?),\s*"u64ten (?:swap|insert): ([^"]+)",?\s*\);',
                       body, re.S)
    covers[name] = [m[1] for m in found]
    predicates[name] = [" ".join(m[0].split()) for m in found]
    assert covers[name] == COVERS[name], (name, covers[name])
    assert predicates[name] == PREDICATES[name], (name, predicates[name])
    assert body.count("kani::cover(") == 9
    call = "swap_u64_net9(" if i == 0 else "insert_tail_profile::<StrictU64>("
    assert body.index(call) < body.index("kani::cover("), name  # all covers after the target

swap = child[child.index("fn " + NAMES[0]):child.index("fn " + NAMES[1])]
assert "let mut v: [u64; 10] = kani::any();" in swap and "let probe: u64 = kani::any();" in swap
assert swap.index("let pre = v;") < swap.index("let probe: u64 = kani::any();")
assert "unsafe { swap_u64_net9(base.add(0), a, b, cmp, probe) };" in swap
assert "let cmp: U64Cmp = StrictU64::CMP;" in swap
assert "kani::assert(v[9] == pre[9]," in swap and "while i < 10 {" in swap
assert "count_matching_values(&pre[..9], &probe) == count_matching_values(&v[..9], &probe)" in swap
assert "count_matching_values(&pre, &probe) == count_matching_values(&v, &probe)" in swap
ins = child[child.index("fn " + NAMES[1]):]
assert ins.index("StrictU64::set_probe(kani::any());") < ins.index("let probe = StrictU64::probe();")
assert ins.index("let probe = StrictU64::probe();") < ins.index("let mut v: [u64; 10] = kani::any();")
assert ins.index("let mut v: [u64; 10] = kani::any();") < ins.index("let pre = v;")
assert "unsafe { insert_tail_profile::<StrictU64>(base.add(0), base.add(9), cmp) };" in ins
assert "let cmp: U64Cmp = StrictU64::CMP;" in ins
assert ins.index("let pre = v;") < ins.index("insert_tail_profile::<StrictU64>(")
assert "kani::assert(sorted10_u64(&v)," in ins
assert "kani::assert(StrictU64::probe() == probe," in ins

# Existing targets are byte-identical: swap_u64_net9 contract/body and insert_tail_profile in specfix.
for path in [SMALLSORT + ".rs", SMALLSORT + "/verify/merge/specfix.rs",
             SMALLSORT + "/verify/network.rs", "library/core/src/ub_checks.rs"]:
    assert (ROOT / path).read_text() == git("show", f"{BASE}:{path}"), path
assert parent.index("unsafe fn swap_u64_net9") < parent.index("mod tenleaves;")
assert parent.rstrip().endswith("mod tenleaves;")

pfc = subprocess.check_output(["python3", str(HERE.parent / "integwrapfix/pfc_order.py"),
                               str(ROOT / SMALLSORT)], text=True).strip()
assert pfc == "ordinary pfc sites 21 bad 0", pfc

spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)
ordinary, files = inv.inventory(False)
controls, cfg_files = inv.inventory(True)
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
assert [r["name"] for r in ordinary] == sorted(expected) and len(ordinary) == 200
prefix = inv.PREFIX + "network::u64nine::tenleaves::"
old_controls = [r["name"] for r in controls if not r["name"].startswith(prefix)]
assert len(old_controls) == 399
new_names = sorted(set(r["name"] for r in controls) - set(old_controls))
assert new_names == sorted(prefix + n for n in NAMES), new_names
assert [r["name"] for r in controls] == sorted(old_controls + [prefix + n for n in NAMES])
assert len(controls) == 401

request_path = HERE.parent / "RUN-REQUEST.json"
assert (HERE / "g1.request.json").read_bytes() == request_path.read_bytes()
request = json.loads(request_path.read_text())
full = "slice::sort::shared::smallsort::verify::network::u64nine::tenleaves::"
assert request["agent"] == "k1-network" and request["request_id"].startswith("usixtyfourten-")
assert [r["name"] for r in request["harnesses"]] == [full + n for n in NAMES]
assert [r["expect"] for r in request["harnesses"]] == ["SUCCESS", "SUCCESS"]
assert all("expect_check" not in r for r in request["harnesses"])
assert request["kind"] == "measurement" and request["controls"] is True
assert request["kani_jobs"] == 1 and request["uninit_checks"] is False
assert request["harness_timeout_minutes"] == 10 and request["runner"] == "gcb-e2-standard-4"

dependencies = [SMALLSORT + ".rs", SMALLSORT + "/verify/network.rs", PARENT, CHILD,
                SMALLSORT + "/verify/merge/specfix.rs", "library/core/src/ub_checks.rs"] + LANE[4:7]
report = dict(status="PASS", base=BASE, base_library_commit=BASE_LIBRARY_COMMIT,
              base_library_tree=BASE_LIBRARY_TREE,
              library_commit=git("log", "-1", "--format=%H", "--", "library").strip(),
              library_tree=git("rev-parse", "HEAD:library").strip(),
              ordinary_exact=200, controls_exact=401, controls_before=399, added=new_names,
              changed_library_files=[PARENT, CHILD], parent_change="registration only",
              runtime_targets_specfix_network_unchanged=True, protected_tooling_unchanged=True,
              pfc_order=pfc, annotations=annotations, covers=covers, cover_predicates=predicates,
              request_sha256=hashlib.sha256(request_path.read_bytes()).hexdigest(),
              child_sha256=sha(child),
              dependency_sha256={p: sha((ROOT / p).read_text()) for p in dependencies},
              scope="Static source/packet checks only; compile, proof and covers NOT_RUN before GO.")
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items()
                  if k not in ["annotations", "covers", "cover_predicates", "dependency_sha256"]},
                 indent=2))
