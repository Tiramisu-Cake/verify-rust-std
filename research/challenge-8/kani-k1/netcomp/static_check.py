"""NETCOMP G1 source preservation, exact static inventory and packet checks; no compiler run."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "a76671d5c4"
NETWORK = "library/core/src/slice/sort/shared/smallsort/verify/network.rs"
MODULE = NETWORK[:-3] + "/netcomp.rs"
RUNTIME = "library/core/src/slice/sort/shared/smallsort.rs"
TOOL_BASE = "30f77e859903df14b442ff9294d4fbbd44827f20"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)
source = (ROOT / MODULE).read_text()
network = (ROOT / NETWORK).read_text()
registration = "#[cfg(kani_smallsort_controls)]\nmod netcomp;\n\n"
assert network.count(registration) == 1
assert network.replace(registration, "") == git("show", f"{BASE}:{NETWORK}")
changed = git("diff", "--name-only", BASE, "--", "library").splitlines()
assert changed == sorted([NETWORK, MODULE]), changed
assert not git("diff", TOOL_BASE, "--", *LANE)
assert not git("diff", BASE, "--", RUNTIME)
assert "9461e07af7ec929f050aa4192f29363c9be07779" in (ROOT / LANE[5]).read_text()
assert 'channel = "nightly-2026-10-12"' in (ROOT / "rust-toolchain.toml").read_text()
assert "kani::assume" not in source
assert source.count("kani::any_where") == 2  # Leaf pair indices only.
assert source.count("impl SwapBridge9<U8Cmp> for u8") == 1
assert source.count("impl SwapBridge9") == 1
assert source.count("#[kani::modifies(") == 1
assert "#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]" in source
assert "old(count9(v, probe)) == count9(v, probe)" in source
assert "old(pair_models::<StrictU8>(v, a, b))" in source
assert "swap_net9(v, a, b, *is_less, ctx.probe)" in source
assert source.count("addr_of_mut!(CONTEXT9)") == 1
assert source.count("addr_of_mut!(CONTEXT9.hits)") == 1
assert source.index("if !accepted") < source.index("swap_net9(v, a, b, *is_less, ctx.probe)")
assert source.index("unsafe fn swap_net9") < source.index("#[kani::proof_for_contract(swap_net9)]")
assert source.count("#[kani::unwind(25)]") == 5
assert max(map(len, source.splitlines())) <= 100

ordinary, files = inv.inventory(False)
controls, cfg_files = inv.inventory(True)
assert files == cfg_files
ordinary_names = [r["name"] for r in ordinary]
control_names = [r["name"] for r in controls]
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
old = (HERE.parent / "cleanup/cfg-on-expected.txt").read_text().splitlines()
old += [inv.PREFIX + "network::" + n for n in [
    "netnine_full_value_count_u8_n9", "netnine_full_value_count_u8_n9_negative",
    "netthirteen_full_value_count_u8_n13", "netthirteen_full_value_count_u8_n13_negative"]]
names = ["netcomp_leaf_u8_n9", "netcomp_direct_u8_n9", "netcomp_composed_u8_n9",
         "netcomp_wrong_cmp_u8_n9", "netcomp_count_negative_u8_n9"]
new = [inv.PREFIX + "network::netcomp::" + n for n in names]
assert ordinary_names == sorted(expected) and len(ordinary_names) == 200
assert control_names == sorted(old + new) and len(control_names) == 391

request = json.loads((HERE / "g1.request.json").read_text())
assert (HERE / "g1.request.json").read_bytes() == (HERE.parent / "RUN-REQUEST.json").read_bytes()
assert [r["name"] for r in request["harnesses"]] == new
assert [r["expect"] for r in request["harnesses"]] == ["SUCCESS"] * 3 + ["FAILED"] * 2
assert request["kind"] == "measurement" and request["controls"]
assert request["kani_jobs"] == 1 and not request["uninit_checks"]
assert request["harness_timeout_minutes"] == 10
for row in request["harnesses"][3:]:
    assert source.count('"' + row["expect_check"] + '"') == 1
negative = source[source.index("fn netcomp_count_negative_u8_n9"):]
assert negative.index("v[8] = 1") < negative.index("kani::assert(is_sorted_by")
assert negative.index("kani::assert(is_sorted_by") < negative.index("corrupted count check reached")
assert negative.index("corrupted count check reached") < negative.index("full-value count preserved")

annotations = {}
for name in names:
    pos = source.index("fn " + name + "()")
    block = source[source.rfind("\n}\n", 0, pos) + 3:pos]
    annotations[name] = re.findall(r"#\[kani::[^\n]+", block)
    assert "#[kani::unwind(25)]" in annotations[name]
assert not any("stub" in a for n in names[:2] for a in annotations[n])
for name in names[2:]:
    assert annotations[name] == ["#[kani::proof]", "#[kani::stub(swap_if_less, adapter9)]",
                                 "#[kani::stub_verified(swap_net9)]", "#[kani::unwind(25)]"]

report = dict(status="PASS", base=git("rev-parse", BASE).strip(),
              ordinary_exact=200, controls_exact=391, controls_added=new,
              existing_network_bytes_preserved=True, runtime_and_protected_tooling_unchanged=True,
              target_precedes_pfc=True, pfc_module_gate="inherited kani_smallsort_controls",
              request_sha256=digest(HERE / "g1.request.json"),
              source_sha256={p: digest(ROOT / p) for p in [NETWORK, MODULE, RUNTIME]},
              annotations=annotations,
              scope="Static source/packet checks only; compile, proof and covers NOT_RUN before GO.")
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "annotations"}, indent=2))
