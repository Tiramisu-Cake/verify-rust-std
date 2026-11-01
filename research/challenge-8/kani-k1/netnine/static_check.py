"""NETNINE source preservation and exact static inventory checks; no compiler/proof run."""
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "ed6e746bf8ec64043e7179be0a6eb631f106601b"
NETWORK = "library/core/src/slice/sort/shared/smallsort/verify/network.rs"
spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)

source = (ROOT / NETWORK).read_text()
base = subprocess.check_output(["git", "show", f"{BASE}:{NETWORK}"], text=True)
start = source.index("// Direct full-value count on the real unstable u8/default-< route")
end = source.index("macro_rules! network_correctness_cases", start)
added = source[start:end]
restored = source[:start] + source[end:]
restored = restored.replace(
    "    // At N >= 9, there is a structural network argument and separate leaf/suffix proofs,\n"
    "    // but no full machine-checked composition. This keeps the probe formula out of the network.\n",
    "    // At N >= 9, compose the structural network permutation with the separately checked\n"
    "    // real insertion-tail permutation. This keeps its probe formula out of the network.\n",
)
assert restored == base, "existing source changed beyond the declared comment correction"
changed = subprocess.check_output(["git", "diff", "--name-only", BASE, "--", "library"], text=True)
assert changed.splitlines() == [NETWORK], changed
assert added.count("#[cfg(kani_smallsort_controls)]") == 2
assert added.count("#[kani::proof]") == 2
assert not any(token in added for token in ("kani::assume", "kani::any_where", "kani::stub"))
assert max(map(len, source.splitlines())) <= 100
ordinary, files = inv.inventory(False)
controls, cfg_files = inv.inventory(True)
assert files == cfg_files
ordinary_names = [r["name"] for r in ordinary]
controls_names = [r["name"] for r in controls]
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
old_controls = (HERE.parent / "cleanup/cfg-on-expected.txt").read_text().splitlines()
prefix = inv.PREFIX + "network::netnine_full_value_count_u8_n9"
new = [prefix, prefix + "_negative"]
assert ordinary_names == sorted(expected) and len(ordinary_names) == 200
assert controls_names == sorted(old_controls + new) and len(controls_names) == 384
report = dict(
    status="PASS", base=BASE, existing_source_preserved_except_comment=True,
    ordinary_exact=200, controls_exact=384, controls_added=new,
    scope="Static source forecast; native compilation and proof status NOT_RUN before GO.",
    source_sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files},
    new_harnesses=[r for r in controls if r["name"] in new],
)
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "source_sha256"}, indent=2))
