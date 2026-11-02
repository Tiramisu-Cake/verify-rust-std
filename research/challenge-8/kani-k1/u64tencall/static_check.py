"""U64-TEN-CALLER source/packet checks only. Does not run a compiler or verifier."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "f057b7e4ebebd2050861976ee8bb0ee0172703c2"  # U64-TEN-LEAVES record (task base)
BASE_LIBRARY_COMMIT = "e4c696648a5a4ff4f92dbe1ec7ed145afea25ee8"
BASE_LIBRARY_TREE = "3c600416e508b037ebdfe817f6dc93d0314c9b21"
LEAVES_REVIEWED = "9009451c82740af506708b7a2217099b57970807"  # leaves Build dd2f7e52 source
SMALLSORT = "library/core/src/slice/sort/shared/smallsort"
GRANDPARENT = SMALLSORT + "/verify/network/u64nine.rs"
PARENT = SMALLSORT + "/verify/network/u64nine/tenleaves.rs"
CHILD = SMALLSORT + "/verify/network/u64nine/tenleaves/caller.rs"
TOOL_BASE = "30f77e859903df14b442ff9294d4fbbd44827f20"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]
REGISTRATION = ("\n// U64-TEN-CALLER: opt-in child composing the actual u64 N10 route from the leaves"
                " above.\nmod caller;\n")
NAMES = ["u64tencall_positive_u64_n10", "u64tencall_swap_binding_negative_u64_n10",
         "u64tencall_insert_binding_negative_u64_n10", "u64tencall_count_negative_u64_n10"]
ANNOTATION = [
    "#[kani::proof]",
    "#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter_u64ten)]",
    "#[kani::stub_verified(super::super::swap_u64_net9)]",
    "#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter_u64ten)]",
    "#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]",
    "#[kani::unwind(25)]",
]
COVERS = {
    NAMES[0]: ["u64tencall positive: returned",
               "u64tencall positive: input has descending adjacent pair",
               "u64tencall positive: probe hits pre10", "u64tencall positive: probe misses pre10",
               "u64tencall positive: pre10 has duplicate value",
               "u64tencall positive: probe hits only original tail",
               "u64tencall positive: all hits", "u64tencall positive: tail-min input returned",
               "u64tencall positive: high-bit probe hits pre10"],
    NAMES[1]: ["u64tencall swap control: actual entry reached"],
    NAMES[2]: ["u64tencall insert control: actual entry reached"],
    NAMES[3]: ["u64tencall negative: returned before corruption",
               "u64tencall negative: count check reached"],
}
PREDICATES = {
    NAMES[0]: ["true", "descending", "hits10 > 0", "hits10 == 0", "duplicate",
               "probe == pre[9] && hits9 == 0", "ctx.swap_hits == 25 && ctx.insert_hits == 1",
               "tail_min", "probe >= (1u64 << 40) && hits10 > 0"],
    NAMES[1]: ["true"], NAMES[2]: ["true"], NAMES[3]: ["true", "true"],
}
SWAP_MARKER = "u64tencall actual swap adapter binding control"
INSERT_MARKER = "u64tencall actual insert adapter binding control"
COUNT_LITERAL = "u64tencall negative: full-value count preserved"
SWAP_IMPL = "impl SwapBridgeU64Ten<U64Cmp> for u64"
INSERT_IMPL = "impl InsertBridgeU64Ten<U64Cmp> for u64"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()


def between(text, start, end):
    i = text.index(start)
    return text[i:text.index(end, i)]


# Only the parent registration and the new child file change; everything else equals BASE.
assert git("rev-parse", f"{BASE}:library").strip() == BASE_LIBRARY_TREE
assert git("rev-parse", f"{BASE_LIBRARY_COMMIT}:library").strip() == BASE_LIBRARY_TREE
assert git("diff", "--name-only", BASE, "--", "library").splitlines() == [PARENT, CHILD]
parent = (ROOT / PARENT).read_text()
assert parent == git("show", f"{BASE}:{PARENT}") + REGISTRATION
assert not git("diff", TOOL_BASE, "--", *LANE)

# Reuse record: both leaves, their targets and every library dependency are byte-identical to the
# reviewed U64-TEN-LEAVES source; tenleaves.rs differs only by the appended registration.
assert git("rev-parse", f"{LEAVES_REVIEWED}:library").strip() == BASE_LIBRARY_TREE
assert not git("diff", LEAVES_REVIEWED, BASE, "--", "library")
assert parent == git("show", f"{LEAVES_REVIEWED}:{PARENT}") + REGISTRATION
for path in [SMALLSORT + ".rs", SMALLSORT + "/verify/merge/specfix.rs", GRANDPARENT,
             SMALLSORT + "/verify/network.rs", SMALLSORT + "/verify/merge.rs",
             "library/core/src/ub_checks.rs"]:
    assert (ROOT / path).read_text() == git("show", f"{LEAVES_REVIEWED}:{path}"), path

child = (ROOT / CHILD).read_text()
assert max(map(len, child.splitlines())) <= 100
code = "\n".join(l for l in child.splitlines() if not l.lstrip().startswith("//"))
for banned in ["kani::assume", "any_where", "kani::modifies", "kani::requires", "kani::ensures",
               "proof_for_contract", "insertion_sort_shift_left", "sort9_optimal", "sort13",
               "small_sort_network", "small_sort_general", "swap_if_less(", "insert_tail(",
               "impl<", "set_probe(kani", "CONTEXT_U64_NINE", "ContextU64Nine", "U8Cmp", "StrictU8",
               "netcomp", "LtU64", "lt_u64", ">> 1", "& 0x", "as u32", "as u8", "as u16",
               "kani::any_where"]:
    assert banned not in code, banned
for word in ["u8", "u16", "u32", "i32"]:
    assert not re.search(r"\b" + word + r"\b", code), word
assert child.count("#[kani::proof]") == 4 and child.count("#[kani::unwind(25)]") == 4
assert child.count("kani::stub(") == 8 and child.count("kani::stub_verified(") == 8
assert child.count("static mut") == 1 and "static mut CONTEXT_U64_TEN: ContextU64Ten" in child
assert child.count(SWAP_IMPL) == 1 and child.count(INSERT_IMPL) == 1
assert len(re.findall(r"^impl\b", code, re.M)) == 2  # only the two closed impls, no blanket
assert child.count("kani::any()") == 2  # positive: v and probe, both full u64

# Roots, annotations and covers; no kani::cover outside root bodies.
assert re.findall(r"^fn (u64tencall_\w+)\(\)", child, re.M) == NAMES
assert "kani::cover" not in code[:code.index("#[kani::proof]")]
annotations, covers, predicates = {}, {}, {}
for i, name in enumerate(NAMES):
    pos = child.index("fn " + name + "()")
    block = child[child.rfind("\n}\n", 0, pos) + 3:pos]
    annotations[name] = re.findall(r"#\[kani::[^\n]+", block)
    assert annotations[name] == ANNOTATION, (name, annotations[name])
    end = child.index("#[kani::proof]", pos) if i + 1 < len(NAMES) else len(child)
    body = child[pos:end]
    found = re.findall(r'kani::cover\(\s*(.*?),\s*"([^"]+)",?\s*\);', body, re.S)
    covers[name] = [m[1] for m in found]
    predicates[name] = [" ".join(m[0].split()) for m in found]
    assert covers[name] == COVERS[name], (name, covers[name])
    assert predicates[name] == PREDICATES[name], (name, predicates[name])
    assert body.count("kani::cover(") == len(COVERS[name])
assert sum(len(c) for c in COVERS.values()) == child.count("kani::cover(")

# Control markers sit only in their adapters, directly before the forwarded summary call.
swap_impl = between(child, SWAP_IMPL, "\n}\n")
insert_impl = between(child, INSERT_IMPL, "\n}\n")
assert child.count(SWAP_MARKER) == 1 and SWAP_MARKER in swap_impl
assert child.count(INSERT_MARKER) == 1 and INSERT_MARKER in insert_impl
assert child.count(COUNT_LITERAL) == 1
for guard in ["v == ctx.root", "a < 9 && b < 9 && a != b", "canonical(*is_less)",
              "backing10_u64(v)", "StrictU64::probe() == ctx.probe", "ctx.insert_hits == 0"]:
    assert swap_impl.index(guard) < swap_impl.index(SWAP_MARKER), guard
assert swap_impl.index(SWAP_MARKER) < swap_impl.index("swap_u64_net9(v, a, b, *is_less, ctx.probe)")
assert swap_impl.index("swap_u64_net9(") < swap_impl.index("swap_hits) += 1")
after_swap = swap_impl[swap_impl.index("swap_hits) += 1"):]
assert "count9_u64(v, ctx.probe) == ctx.initial_prefix_count9" in after_swap
assert "unsafe { *v.add(9) }" in after_swap and "tail == ctx.initial_tail" in after_swap
for guard in ["begin == ctx.root", "tail == begin.wrapping_add(9)", "canonical(*is_less)",
              "ctx.swap_hits == 25", "ctx.insert_hits == 0", "backing10_u64(begin)",
              "StrictU64::probe() == ctx.probe", "model_sorted::<StrictU64>(begin, 9)",
              "count9_u64(begin, ctx.probe) == ctx.initial_prefix_count9",
              "tail_value == ctx.initial_tail",
              "model_count::<StrictU64>(begin, 10) == ctx.initial_count10"]:
    assert insert_impl.index(guard) < insert_impl.index(INSERT_MARKER), guard
assert insert_impl.index(INSERT_MARKER) < \
    insert_impl.index("insert_tail_profile::<StrictU64>(begin, tail, *is_less)")
assert insert_impl.index("insert_tail_profile::<StrictU64>(") < \
    insert_impl.index("insert_hits) += 1")
after_insert = insert_impl[insert_impl.index("insert_hits) += 1"):]
assert "initial_tail" not in after_insert and "initial_prefix_count9" not in after_insert
assert "model_sorted::<StrictU64>(begin, 10)" in after_insert
assert "model_count::<StrictU64>(begin, 10) == ctx.initial_count10" in after_insert
# Ghost counters are written only by the two adapter `+= 1` lines; the context once by register.
assert child.count("addr_of_mut!(CONTEXT_U64_TEN") == 3

# Single probe: register sets context probe and StrictU64 probe; roots never set it separately.
register = between(child, "fn register_u64ten(", "\n}\n")
assert "StrictU64::set_probe(probe);" in register and child.count("set_probe(") == 1
assert "initial_prefix_count9 + (initial_tail == probe) as usize" in register
assert "addr_of_mut!(CONTEXT_U64_TEN) = ctx" in register
positive = child[child.index("fn " + NAMES[0]):child.index("fn " + NAMES[1])]
assert "let mut v: [u64; 10] = kani::any();" in positive
assert positive.index("let pre = v;") < positive.index("let probe: u64 = kani::any();")
assert "let mut cmp: U64Cmp = StrictU64::CMP;" in positive
assert positive.index("run_u64ten(&mut v, probe, &mut cmp);") < \
    positive.index("check_final_u64ten(&v, &pre, probe);") < positive.index("kani::cover(")
for name, flags in [(NAMES[1], "register_u64ten(&mut v, 0, true, false);"),
                    (NAMES[2], "register_u64ten(&mut v, 0, false, true);")]:
    i = NAMES.index(name)
    body = child[child.index("fn " + name):child.index("fn " + NAMES[i + 1])]
    assert flags in body and "let mut v = [0u64; 10];" in body
    assert body.index("kani::cover(") < body.index("small_sort(&mut v, &mut cmp)")
    assert "kani::assert" not in body and "run_u64ten" not in body
count = child[child.index("fn " + NAMES[3]):]
assert "const P: u64 = 1u64 << 40;" in count and "const Q: u64 = 1u64 << 41;" in count
assert "let mut v = [P; 10];" in count and "let probe = P;" in count
assert count.index("run_u64ten(") < count.index("check_final_u64ten(") < \
    count.index("returned before corruption") < count.index("v[9] = Q;")
assert count.index("v[9] = Q;") < count.index("sorted10_u64(&v)") < \
    count.index("count check reached") < count.index(COUNT_LITERAL)
assert (1 << 40) & 0xFFFF_FFFF == (1 << 41) & 0xFFFF_FFFF  # same low 32 bits
# One typed full-u64 count predicate in the final post and the count control.
assert child.count("count10_preserved_u64(") == 3
final = between(child, "fn check_final_u64ten(", "\n}\n")
assert "count10_preserved_u64(pre, v, probe)" in final and "sorted10_u64(v)" in final
assert "count10_preserved_u64(&pre, &v, probe)" in count

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
assert len(net) == 2
rows = ["step\tsource_line\traw_call\tactual_args_on_backing10\tcomposed_binding"]
for k, (line, (a, b)) in enumerate(swaps, 1):
    rows.append(f"swap{k:02}\t{line}\tswap_if_less::<u64,U64Cmp>(v_base,{a},{b},is_less)\t"
                f"root+0; pair ({a},{b}) in prefix9; v[9] frame\t"
                "swap_adapter_u64ten -> verified swap_u64_net9 (leaf u64ten_swap_prefix9_backing10)")
rows.append(f"insert01\t{inserts[0]}\tinsert_tail::<u64,U64Cmp>(v_base,tail,is_less)\t"
            "begin root+0, tail root+9; sole iteration of offset9 len10\t"
            "insert_adapter_u64ten -> verified insert_tail_profile<StrictU64> "
            "(leaf u64ten_insert_strict_u64_begin0_tail9)")
(HERE / "n10-call-map.tsv").write_text("\n".join(rows) + "\n")

pfc = subprocess.check_output(["python3", str(HERE.parent / "integwrapfix/pfc_order.py"),
                               str(ROOT / SMALLSORT)], text=True).strip()
assert pfc == "ordinary pfc sites 21 bad 0", pfc
grand = (ROOT / GRANDPARENT).read_text()
assert grand.index("unsafe fn swap_u64_net9") < grand.index("mod tenleaves;")
assert parent.index("fn u64ten_insert_strict_u64_begin0_tail9") < parent.index("mod caller;")
assert parent.rstrip().endswith("mod caller;")

spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)
ordinary, files = inv.inventory(False)
controls, cfg_files = inv.inventory(True)
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
assert [r["name"] for r in ordinary] == sorted(expected) and len(ordinary) == 200
prefix = inv.PREFIX + "network::u64nine::tenleaves::caller::"
old_controls = [r["name"] for r in controls if not r["name"].startswith(prefix)]
assert len(old_controls) == 401
new_names = sorted(set(r["name"] for r in controls) - set(old_controls))
assert new_names == sorted(prefix + n for n in NAMES), new_names
assert [r["name"] for r in controls] == sorted(old_controls + [prefix + n for n in NAMES])
assert len(controls) == 405

full = "slice::sort::shared::smallsort::verify::network::u64nine::tenleaves::caller::"
assert prefix == full
request_path = HERE.parent / "RUN-REQUEST.json"
requests = {g: json.loads((HERE / f"{g}.request.json").read_text()) for g in ["g1", "g2"]}
current = json.loads(request_path.read_text())
assert current in requests.values()  # RUN-REQUEST.json is byte-equal to one package below
assert any((HERE / f"{g}.request.json").read_bytes() == request_path.read_bytes()
           for g in ["g1", "g2"])
want = {"g1": ([NAMES[0]], ["SUCCESS"], [None]),
        "g2": (NAMES[1:], ["FAILED"] * 3, [SWAP_MARKER, INSERT_MARKER, COUNT_LITERAL])}
for g, request in requests.items():
    names, expects, checks = want[g]
    assert request["agent"] == "k1-network"
    assert request["request_id"].startswith("usixtyfourtencall-" + g + "-")
    assert [r["name"] for r in request["harnesses"]] == [full + n for n in names]
    assert [r["expect"] for r in request["harnesses"]] == expects
    assert [r.get("expect_check") for r in request["harnesses"]] == checks
    assert request["kind"] == "measurement" and request["controls"] is True
    assert request["kani_jobs"] == 1 and request["uninit_checks"] is False
    assert request["harness_timeout_minutes"] == 10 and request["runner"] == "gcb-e2-standard-4"
    assert set(request) == {"schema", "agent", "runner", "request_id", "kind", "purpose",
                            "harness_timeout_minutes", "kani_jobs", "uninit_checks", "controls",
                            "harnesses"}
# Each expect_check matches exactly one literal of the child (no accidental substring hit).
for needle in [SWAP_MARKER, INSERT_MARKER, COUNT_LITERAL]:
    assert len([s for s in re.findall(r'"([^"]+)"', child) if needle in s]) == 1, needle

marker_lines = {lit: next(i + 1 for i, l in enumerate(child.splitlines()) if f'"{lit}"' in l)
                for lit in [SWAP_MARKER, INSERT_MARKER, COUNT_LITERAL]}
dependencies = [SMALLSORT + ".rs", SMALLSORT + "/verify/network.rs", GRANDPARENT, PARENT, CHILD,
                SMALLSORT + "/verify/merge.rs", SMALLSORT + "/verify/merge/specfix.rs",
                "library/core/src/ub_checks.rs"] + LANE[4:7]
report = dict(status="PASS", base=BASE, base_library_commit=BASE_LIBRARY_COMMIT,
              base_library_tree=BASE_LIBRARY_TREE, leaves_reviewed_source=LEAVES_REVIEWED,
              library_commit=git("log", "-1", "--format=%H", "--", "library").strip(),
              library_tree=git("rev-parse", "HEAD:library").strip(),
              ordinary_exact=200, controls_exact=405, controls_before=401, added=new_names,
              changed_library_files=[PARENT, CHILD], parent_change="registration only",
              leaves_and_dependencies_byte_identical_to_reviewed_leaves_source=True,
              protected_tooling_unchanged=True, pfc_order=pfc, annotations=annotations,
              covers=covers, cover_predicates=predicates, marker_lines=marker_lines,
              swap_edges=[[line, a, b] for line, (a, b) in swaps],
              insert_tail_call_line=inserts[0], network_call_lines=net,
              request_sha256={g: hashlib.sha256((HERE / f"{g}.request.json").read_bytes()).hexdigest()
                              for g in ["g1", "g2"]},
              run_request_sha256=hashlib.sha256(request_path.read_bytes()).hexdigest(),
              child_sha256=sha(child),
              dependency_sha256={p: sha((ROOT / p).read_text()) for p in dependencies},
              scope="Static source/packet checks only; compile, proof and covers NOT_RUN before GO.")
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items()
                  if k not in ["annotations", "covers", "cover_predicates", "dependency_sha256",
                               "swap_edges"]}, indent=2))
