"""NETTHIRTEEN exact source preservation and static inventory; no compiler/proof run."""
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "b47dc20eba5ae095f44dc26ca1df81df3fbf8c2d"
NETWORK = "library/core/src/slice/sort/shared/smallsort/verify/network.rs"
spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)

source = (ROOT / NETWORK).read_text()
base = subprocess.check_output(["git", "show", f"{BASE}:{NETWORK}"], text=True)
start = source.index("// N13 uses sort13_optimal, then insertion with the full prefix13 and no merge.")
end = source.index("macro_rules! network_correctness_cases", start)
added = source[start:end]
assert source[:start] + source[end:] == base, "existing network source changed"
changed = subprocess.check_output(["git", "diff", "--name-only", BASE, "--", "library"], text=True)
assert changed.splitlines() == [NETWORK], changed
assert added.count("#[cfg(kani_smallsort_controls)]") == 2
assert added.count("#[kani::proof]") == 2
assert added.count("#[kani::unwind(25)]") == 2
assert not any(token in added for token in ("kani::assume", "kani::any_where", "kani::stub"))
assert max(map(len, source.splitlines())) <= 100
ordinary, files = inv.inventory(False)
controls, cfg_files = inv.inventory(True)
assert files == cfg_files
ordinary_names = [r["name"] for r in ordinary]
controls_names = [r["name"] for r in controls]
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
old_controls = (HERE.parent / "cleanup/cfg-on-expected.txt").read_text().splitlines()
old_prefix = inv.PREFIX + "network::netnine_full_value_count_u8_n9"
new_prefix = inv.PREFIX + "network::netthirteen_full_value_count_u8_n13"
new = [new_prefix, new_prefix + "_negative"]
assert ordinary_names == sorted(expected) and len(ordinary_names) == 200
assert controls_names == sorted(old_controls + [old_prefix, old_prefix + "_negative"] + new)
assert len(controls_names) == 386
request = json.loads((HERE / "g1.request.json").read_text())
assert (HERE / "g1.request.json").read_bytes() == (HERE.parent / "RUN-REQUEST.json").read_bytes()
assert [r["name"] for r in request["harnesses"]] == new
assert request["controls"] and request["kani_jobs"] == 1 and not request["uninit_checks"]
assert request["harness_timeout_minutes"] == 10 and request["kind"] == "measurement"
literal = '"netthirteen negative: full-value count preserved"'
assert source.count(literal) == 1
assert request["harnesses"][1]["expect_check"] == literal.strip('"')
positive, negative = added.split("// Narrow count-oracle control:")
assert positive.count("kani::cover(") == 4 and negative.count("kani::cover(") == 2
assert negative.index("v[12] = 1;") < negative.index("kani::assert(is_sorted_by")
assert negative.index("kani::assert(is_sorted_by") < negative.index("corrupted count check reached")
assert negative.index("corrupted count check reached") < negative.index(literal)
report = dict(
    status="PASS", base=BASE, existing_library_source_preserved=True,
    ordinary_exact=200, controls_exact=386, controls_added=new,
    scope="Static source forecast; native compilation and proof status NOT_RUN before GO.",
    request_sha256=hashlib.sha256((HERE / "g1.request.json").read_bytes()).hexdigest(),
    source_sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files},
    new_harnesses=[r for r in controls if r["name"] in new],
)
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "source_sha256"}, indent=2))
