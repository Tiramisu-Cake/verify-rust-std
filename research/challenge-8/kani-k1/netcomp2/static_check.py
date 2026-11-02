"""NETCOMP2 source/packet checks only. Does not run a compiler or verifier."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "b57bf76f69"
G1 = "0944189023c0c53620ed74a45bb2d2efef4c53cd"
MODULE = "library/core/src/slice/sort/shared/smallsort/verify/network/netcomp.rs"
TOOL_BASE = "30f77e859903df14b442ff9294d4fbbd44827f20"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()


source = (ROOT / MODULE).read_text()
old = git("show", f"{G1}:{MODULE}")
old_cover = '    kani::cover(ctx.hits == 25, "netcomp N9: all actual exchanges intercepted");\n'
new_cover = '    kani::cover(context9().hits == 25, "netcomp N9: all actual exchanges intercepted");\n'
old_fixed = old.replace(old_cover, "").replace("    positive9(true);\n}",
                                             "    positive9(true);\n" + new_cover + "}")
separator = "\n// N13 is a separate exact backing, target, leaf and context; N9 dependencies stay intact.\n\n"
assert source.split(separator)[0] == old_fixed
assert git("diff", "--name-only", BASE, "--", "library").splitlines() == [MODULE]
assert not git("diff", TOOL_BASE, "--", *LANE)
assert not git("diff", G1, "--", "library", f":(exclude){MODULE}")
assert "kani::assume" not in source
assert source.count("kani::any_where") == 4  # Only distinct leaf pair indices.
assert source.count("#[kani::unwind(25)]") == 9
assert max(map(len, source.splitlines())) <= 100

annotations = {}
names = re.findall(r"^fn (netcomp_\w+)\(\)", source, re.M)
assert len(names) == 9
for name in names:
    pos = source.index("fn " + name + "()")
    block = source[source.rfind("\n}\n", 0, pos) + 3:pos]
    annotations[name] = re.findall(r"#\[kani::[^\n]+", block)
    n = name.rsplit("_n", 1)[1]
    if "leaf" in name:
        want = [f"#[kani::proof_for_contract(swap_net{n})]", "#[kani::unwind(25)]"]
    elif "direct" in name:
        want = ["#[kani::proof]", "#[kani::unwind(25)]"]
    else:
        want = ["#[kani::proof]", f"#[kani::stub(swap_if_less, adapter{n})]",
                f"#[kani::stub_verified(swap_net{n})]", "#[kani::unwind(25)]"]
    assert annotations[name] == want, (name, annotations[name])

for n, hits in [(9, 25), (13, 45)]:
    assert source.count(f"impl SwapBridge{n}<U8Cmp> for u8") == 1
    assert source.count(f"impl SwapBridge{n}") == 1
    assert f"old(count{n}(v, probe)) == count{n}(v, probe)" in source
    assert f"swap_net{n}(v, a, b, *is_less, ctx.probe)" in source
    assert source.count(f"addr_of_mut!(CONTEXT{n})") == 1
    assert source.count(f"addr_of_mut!(CONTEXT{n}.hits)") == 1
    assert source.index(f"unsafe fn swap_net{n}") < source.index(f"#[kani::proof_for_contract(swap_net{n})]")
    helper = source[source.index(f"fn check_context{n}("):source.index(f"fn run{n}(")]
    assert "kani::cover" not in helper
    assert f'kani::assert(ctx.hits == {hits}, "netcomp N{n}: complete actual hit count")' in helper
    negative = source[source.index(f"fn netcomp_count_negative_u8_n{n}()"):]
    assert negative.index(f"v[{n-1}] = 1") < negative.index("kani::assert(is_sorted_by")
    assert negative.index("kani::assert(is_sorted_by") < negative.index("corrupted count check reached")
    assert negative.index("corrupted count check reached") < negative.index("full-value count preserved")
assert source.count("#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]") == 2

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
assert [r["name"] for r in ordinary] == sorted(expected) and len(ordinary) == 200
prefix = inv.PREFIX + "network::netcomp::"
assert [r["name"] for r in controls] == sorted(old_names + [prefix + n for n in names])
assert len(controls) == 395

request = json.loads((HERE / "g1.request.json").read_text())
assert (HERE / "g1.request.json").read_bytes() == (HERE.parent / "RUN-REQUEST.json").read_bytes()
selected = ["netcomp_direct_u8_n9", "netcomp_composed_u8_n9", "netcomp_count_negative_u8_n9",
            "netcomp_leaf_u8_n13", "netcomp_composed_u8_n13", "netcomp_wrong_cmp_u8_n13",
            "netcomp_count_negative_u8_n13"]
assert [r["name"] for r in request["harnesses"]] == [prefix + n for n in selected]
assert [r["expect"] for r in request["harnesses"]] == ["SUCCESS", "SUCCESS", "FAILED", "SUCCESS",
                                                        "SUCCESS", "FAILED", "FAILED"]
assert request["request_id"].startswith("netcomp2-")
assert request["kind"] == "measurement" and request["controls"]
assert request["kani_jobs"] == 1 and not request["uninit_checks"]
assert request["harness_timeout_minutes"] == 10
for row in request["harnesses"]:
    if row["expect"] == "FAILED":
        assert '"' + row["expect_check"] + '"' in source

dependencies = ["library/core/src/slice/sort/shared/smallsort.rs",
                "library/core/src/slice/sort/shared/smallsort/verify/network.rs",
                "library/core/src/slice/sort/shared/smallsort/verify/merge/specfix.rs",
                "library/core/src/ub_checks.rs"] + LANE[4:7]
report = dict(status="PASS", base=git("rev-parse", BASE).strip(), reused_source=G1,
              ordinary_exact=200, controls_exact=395, n13_added=4,
              n9_prefix_exact_except_requested_cover_move=True,
              all_other_library_bytes_preserved_from_g1=True,
              runtime_and_protected_tooling_unchanged=True, annotations=annotations,
              source_sha256=sha(source), request_sha256=sha((HERE / "g1.request.json").read_text()),
              dependency_sha256={p: sha((ROOT / p).read_text()) for p in dependencies},
              scope="Static source/packet checks only; compile, proof and covers NOT_RUN before GO.")
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k not in ["annotations", "dependency_sha256"]}, indent=2))
