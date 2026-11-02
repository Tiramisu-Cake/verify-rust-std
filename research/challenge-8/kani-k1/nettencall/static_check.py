"""NETTEN-CALLER source/packet checks only. Does not run a compiler or verifier."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "9835bd00dc4bf386e68e5f7885964a17d0dda240"
BASE_LIBRARY_COMMIT = "23ba8cfddbce1cf0313ab402fd6376d157a0f845"
BASE_LIBRARY_TREE = "74e42aaa191879280e8e7827c1e32a4ac65d5f18"
LEAVES_REVIEWED = "1914e42274cb2a7e574a0d6497c4a9922983a9cf"  # NETTEN-LEAVES Build f6fdbf06 source
SMALLSORT = "library/core/src/slice/sort/shared/smallsort"
GRANDPARENT = SMALLSORT + "/verify/network/netcomp.rs"
PARENT = SMALLSORT + "/verify/network/netcomp/netten.rs"
CHILD = SMALLSORT + "/verify/network/netcomp/netten/caller.rs"
TOOL_BASE = "30f77e859903df14b442ff9294d4fbbd44827f20"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]
REGISTRATION = ("\n// NETTEN-CALLER: opt-in child composing the actual N10 route from the leaves above.\n"
                "mod caller;\n")
NAMES = ["nettencall_positive_u8_n10", "nettencall_swap_binding_negative_u8_n10",
         "nettencall_insert_binding_negative_u8_n10", "nettencall_count_negative_u8_n10"]
ANNOTATION = [
    "#[kani::proof]",
    "#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter10)]",
    "#[kani::stub_verified(super::super::swap_net9)]",
    "#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter10)]",
    "#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]",
    "#[kani::unwind(25)]",
]
COVERS = {
    NAMES[0]: ["nettencall positive: returned",
               "nettencall positive: input has descending adjacent pair",
               "nettencall positive: probe hits pre10", "nettencall positive: probe misses pre10",
               "nettencall positive: pre10 has duplicate value",
               "nettencall positive: probe hits only original tail",
               "nettencall positive: all hits", "nettencall positive: tail-min input returned"],
    NAMES[1]: ["nettencall swap control: actual entry reached"],
    NAMES[2]: ["nettencall insert control: actual entry reached"],
    NAMES[3]: ["nettencall negative: returned before corruption",
               "nettencall negative: count check reached"],
}
SWAP_MARKER = "nettencall actual swap adapter binding control"
INSERT_MARKER = "nettencall actual insert adapter binding control"
COUNT_LITERAL = "nettencall negative: full-value count preserved"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()


def between(text, start, end):
    i = text.index(start)
    return text[i:text.index(end, i)]


# Only the parent registration and the new child file change; everything else equals BASE.
assert git("diff", "--name-only", BASE, "--", "library").splitlines() == [PARENT, CHILD]
assert not git("diff", BASE_LIBRARY_COMMIT, BASE, "--", "library")
assert git("rev-parse", f"{BASE}:library").strip() == BASE_LIBRARY_TREE
parent = (ROOT / PARENT).read_text()
assert parent == git("show", f"{BASE}:{PARENT}") + REGISTRATION
assert not git("diff", TOOL_BASE, "--", *LANE)

# Reuse record: both old leaves, their targets and every library dependency are byte-identical to
# the reviewed NETTEN-LEAVES source; the parent differs only by the appended registration.
assert not git("diff", LEAVES_REVIEWED, BASE, "--", "library")
assert parent == git("show", f"{LEAVES_REVIEWED}:{PARENT}") + REGISTRATION
for path in [SMALLSORT + ".rs", SMALLSORT + "/verify/merge/specfix.rs", GRANDPARENT,
             SMALLSORT + "/verify/network.rs", "library/core/src/ub_checks.rs"]:
    assert (ROOT / path).read_text() == git("show", f"{LEAVES_REVIEWED}:{path}"), path

child = (ROOT / CHILD).read_text()
assert max(map(len, child.splitlines())) <= 100
code = "\n".join(l for l in child.splitlines() if not l.lstrip().startswith("//"))
for banned in ["kani::assume", "any_where", "kani::modifies", "kani::requires", "kani::ensures",
               "proof_for_contract", "insertion_sort_shift_left", "sort9_optimal",
               "small_sort_network", "swap_if_less(", "insert_tail(", "impl<", "set_probe(kani"]:
    assert banned not in code, banned
assert child.count("#[kani::proof]") == 4 and child.count("#[kani::unwind(25)]") == 4
assert child.count("kani::stub(") == 8 and child.count("kani::stub_verified(") == 8
assert child.count("static mut") == 1
assert child.count("impl SwapBridge10<U8Cmp> for u8") == 1
assert child.count("impl InsertBridge10<U8Cmp> for u8") == 1
assert len(re.findall(r"^impl\b", code, re.M)) == 2  # only the two closed impls, no blanket

# Roots, annotations and covers; no kani::cover outside root bodies.
assert re.findall(r"^fn (nettencall_\w+)\(\)", child, re.M) == NAMES
first_root = child.index("#[kani::proof]")
assert "kani::cover" not in code[:code.index("#[kani::proof]")]
annotations, covers = {}, {}
for i, name in enumerate(NAMES):
    pos = child.index("fn " + name + "()")
    block = child[child.rfind("\n}\n", 0, pos) + 3:pos]
    annotations[name] = re.findall(r"#\[kani::[^\n]+", block)
    assert annotations[name] == ANNOTATION, (name, annotations[name])
    end = child.index("#[kani::proof]", pos) if i + 1 < len(NAMES) else len(child)
    body = child[pos:end]
    covers[name] = re.findall(r'kani::cover\([^;]*?"([^"]+)"\s*,?\s*\)', body, re.S)
    assert covers[name] == COVERS[name], (name, covers[name])
    assert body.count("kani::cover(") == len(COVERS[name])
assert sum(len(c) for c in COVERS.values()) == child.count("kani::cover(")

# Control markers sit only in their adapters, directly before the forwarded summary call.
swap_impl = between(child, "impl SwapBridge10<U8Cmp> for u8", "\n}\n")
insert_impl = between(child, "impl InsertBridge10<U8Cmp> for u8", "\n}\n")
assert child.count(SWAP_MARKER) == 1 and SWAP_MARKER in swap_impl
assert child.count(INSERT_MARKER) == 1 and INSERT_MARKER in insert_impl
assert child.count(COUNT_LITERAL) == 1
assert swap_impl.index("v == ctx.root") < swap_impl.index(SWAP_MARKER)
assert swap_impl.index("canonical(*is_less)") < swap_impl.index(SWAP_MARKER)
assert swap_impl.index(SWAP_MARKER) < swap_impl.index("swap_net9(v, a, b, *is_less, ctx.probe)")
assert swap_impl.index("swap_net9(") < swap_impl.index("swap_hits) += 1")
assert insert_impl.index("model_sorted::<StrictU8>(begin, 9)") < insert_impl.index(INSERT_MARKER)
assert insert_impl.index("model_count::<StrictU8>(begin, 10) == ctx.initial_count10") < \
    insert_impl.index(INSERT_MARKER)
assert insert_impl.index(INSERT_MARKER) < \
    insert_impl.index("insert_tail_profile::<StrictU8>(begin, tail, *is_less)")
assert insert_impl.index("insert_tail_profile::<StrictU8>(") < insert_impl.index("insert_hits) += 1")
after_insert = insert_impl[insert_impl.index("insert_hits) += 1"):]
assert "initial_tail" not in after_insert and "initial_prefix_count9" not in after_insert

# Single probe: register sets context probe and StrictU8 probe; roots never set it separately.
register = between(child, "fn register10(", "\n}\n")
assert "StrictU8::set_probe(probe);" in register and child.count("set_probe(") == 1
assert "initial_prefix_count9 + (initial_tail == probe) as usize" in register
positive = child[child.index("fn " + NAMES[0]):child.index("fn " + NAMES[1])]
assert "let mut v: [u8; 10] = kani::any();" in positive
assert "let probe: u8 = kani::any();" in positive
assert positive.index("run10(&mut v, probe, &mut cmp);") < positive.index("kani::cover(")
for name, flags in [(NAMES[1], "register10(&mut v, 0, true, false);"),
                    (NAMES[2], "register10(&mut v, 0, false, true);")]:
    i = NAMES.index(name)
    body = child[child.index("fn " + name):child.index("fn " + NAMES[i + 1])]
    assert flags in body and "let mut v = [0u8; 10];" in body
    assert body.index("kani::cover(") < body.index("small_sort(&mut v, &mut cmp)")
    assert "kani::assert" not in body and "run10" not in body
count = child[child.index("fn " + NAMES[3]):]
assert count.index("run10(") < count.index("returned before corruption") < count.index("v[9] = 1;")
assert count.index("v[9] = 1;") < count.index("count check reached") < count.index(COUNT_LITERAL)

# Actual call map from the unchanged runtime source.
rt = (ROOT / (SMALLSORT + ".rs")).read_text().splitlines()
start = next(i for i, l in enumerate(rt) if l.startswith("fn sort9_optimal<"))
end = next(i for i, l in enumerate(rt) if l.startswith("fn sort13_optimal<"))
swaps = [(i + 1, tuple(map(int, m.groups()))) for i in range(start, end)
         for m in [re.search(r"swap_if_less\(v_base, (\d+), (\d+), is_less\);", rt[i])] if m]
assert len(swaps) == 25 and all(a < 9 and b < 9 and a != b for _, (a, b) in swaps)
ins_start = next(i for i, l in enumerate(rt) if l.startswith("pub fn insertion_sort_shift_left<"))
ins_end = next(i for i in range(ins_start + 1, len(rt)) if rt[i] == "}")
inserts = [i + 1 for i in range(ins_start, ins_end) if "insert_tail(v_base, tail, is_less);" in rt[i]]
assert len(inserts) == 1
net = [i + 1 for i, l in enumerate(rt) if "sort9_optimal(region, is_less);" in l
       or "insertion_sort_shift_left(region, presorted_len, is_less);" in l]
rows = ["step\tsource_line\traw_call\tactual_args_on_backing10\tcomposed_binding"]
for k, (line, (a, b)) in enumerate(swaps, 1):
    rows.append(f"swap{k:02}\t{line}\tswap_if_less::<u8,U8Cmp>(v_base,{a},{b},is_less)\t"
                f"root+0; pair ({a},{b}) in prefix9; v[9] frame\t"
                "swap_adapter10 -> verified swap_net9 (leaf netten_swap_prefix9_backing10)")
rows.append(f"insert01\t{inserts[0]}\tinsert_tail::<u8,U8Cmp>(v_base,tail,is_less)\t"
            "begin root+0, tail root+9; sole iteration of offset9 len10\t"
            "insert_adapter10 -> verified insert_tail_profile<StrictU8> "
            "(leaf netten_insert_strict_u8_begin0_tail9)")
(HERE / "n10-call-map.tsv").write_text("\n".join(rows) + "\n")

pfc = subprocess.check_output(["python3", str(HERE.parent / "integwrapfix/pfc_order.py"),
                               str(ROOT / SMALLSORT)], text=True).strip()
assert pfc == "ordinary pfc sites 20 bad 0", pfc
grand = (ROOT / GRANDPARENT).read_text()
assert grand.index("unsafe fn swap_net9") < grand.index("mod netten;")
assert parent.index("fn netten_insert_strict_u8_begin0_tail9") < parent.index("mod caller;")

spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)
ordinary, files = inv.inventory(False)
controls, cfg_files = inv.inventory(True)
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
assert [r["name"] for r in ordinary] == sorted(expected) and len(ordinary) == 200
prefix = inv.PREFIX + "network::netcomp::netten::caller::"
old_controls = [r["name"] for r in controls if not r["name"].startswith(prefix)]
assert len(old_controls) == 397
assert [r["name"] for r in controls] == sorted(old_controls + [prefix + n for n in NAMES])
assert len(controls) == 401

request_path = HERE.parent / "RUN-REQUEST.json"
assert (HERE / "g1.request.json").read_bytes() == request_path.read_bytes()
request = json.loads(request_path.read_text())
assert request["agent"] == "k1-merge" and request["request_id"].startswith("nettencall-")
assert [r["name"] for r in request["harnesses"]] == [prefix + n for n in NAMES]
assert [r["expect"] for r in request["harnesses"]] == ["SUCCESS", "FAILED", "FAILED", "FAILED"]
assert [r.get("expect_check") for r in request["harnesses"]] == [
    None, SWAP_MARKER, INSERT_MARKER, COUNT_LITERAL]
assert request["kind"] == "measurement" and request["controls"] is True
assert request["kani_jobs"] == 1 and request["uninit_checks"] is False
assert request["harness_timeout_minutes"] == 10 and request["runner"] == "gcb-e2-standard-4"
# Each expect_check matches exactly one literal of the child (no accidental substring hit).
for needle in [SWAP_MARKER, INSERT_MARKER, COUNT_LITERAL]:
    assert len([s for s in re.findall(r'"([^"]+)"', child) if needle in s]) == 1, needle

dependencies = [SMALLSORT + ".rs", SMALLSORT + "/verify/network.rs", GRANDPARENT, PARENT, CHILD,
                SMALLSORT + "/verify/merge/specfix.rs", "library/core/src/ub_checks.rs"] + LANE[4:7]
report = dict(status="PASS", base=BASE, base_library_commit=BASE_LIBRARY_COMMIT,
              base_library_tree=BASE_LIBRARY_TREE, leaves_reviewed_source=LEAVES_REVIEWED,
              library_commit=git("log", "-1", "--format=%H", "--", "library").strip(),
              library_tree=git("rev-parse", "HEAD:library").strip(),
              ordinary_exact=200, controls_exact=401, controls_before=397, added=NAMES,
              changed_library_files=[PARENT, CHILD], parent_change="registration only",
              leaves_and_dependencies_byte_identical_to_reviewed_leaves_source=True,
              protected_tooling_unchanged=True, pfc_order=pfc, annotations=annotations,
              covers=covers, swap_edges=[[line, a, b] for line, (a, b) in swaps],
              insert_tail_call_line=inserts[0], network_call_lines=net,
              request_sha256=hashlib.sha256(request_path.read_bytes()).hexdigest(),
              dependency_sha256={p: sha((ROOT / p).read_text()) for p in dependencies},
              scope="Static source/packet checks only; compile, proof and covers NOT_RUN before GO.")
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items()
                  if k not in ["annotations", "covers", "dependency_sha256", "swap_edges"]}, indent=2))
