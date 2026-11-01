#!/usr/bin/env python3
"""Read-only prebuild source/request checks; no compilation or proof claim."""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
K1 = HERE.parent
ROOT = K1.parents[2]
BASE = "2d1d17ca773d97f899006a4c5f84d120e63d4af3"
S = "library/core/src/slice/sort/shared/smallsort"
BRIDGE = f"{S}/verify/bridge.rs"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


ss = load("source_sets", K1 / "poneclean/source_sets.py")
ss.MODULES += [("wrap", "wrap.rs", "ordinary"), ("bridge", "bridge.rs", "controls")]
old, now = ss.sets(BASE), ss.sets()
src = (ROOT / BRIDGE).read_text()
base_src = git("show", f"{BASE}:{BRIDGE}")
marker = "// A and B share the actual Stable entry"
prior, added = src.split(marker)
prior = prior.replace(
    "//! Exact-N3 smoke and actual Stable u8 N9:", "//! Exact-N3 feasibility smoke:", 1
).replace(
    "use crate::slice::sort::shared::smallsort::{\n"
    "    SMALL_SORT_GENERAL_SCRATCH_LEN, StableSmallSortTypeImpl, bidirectional_merge,\n};",
    "use crate::slice::sort::shared::smallsort::bidirectional_merge;", 1
)
req = json.loads((K1 / "RUN-REQUEST.json").read_text())
lane = load("kani_k1", K1 / "tools/kani_k1.py")
lane.validate_request(req)
prefix = ss.PREFIX + "bridge::"
names = [prefix + name for name in (
    "bridgenine_direct_u8_n9", "bridgenine_caller_u8_n9", "bridgenine_payload_flip_u8_n9"
)]
leaf = ss.PREFIX + "merge::merge_scratch48_contract_u8_n9"
rows = [r for r in now["records"] if r["name"] in names + [leaf]]
changed = set(git("diff", "--name-only", BASE, "--", "library").splitlines())
changed |= set(git("ls-files", "--others", "--exclude-standard", "--", "library").splitlines())
caller, harnesses = added.split("#[kani::proof]", 1)
direct = harnesses.split("#[kani::proof]", 1)[0]
checks = {
    "library_only_opt_in_bridge": changed == {BRIDGE}
    and "#![cfg(kani_smallsort_controls)]" in src,
    "old_bridge_behavior_unchanged": prior.rstrip() == base_src.rstrip(),
    "ordinary_exact_base_and_frozen_200": now["ordinary"] == old["ordinary"]
    == sorted((K1 / "integwrapfix/ordinary-expected.txt").read_text().splitlines())
    and len(now["ordinary"]) == 200,
    "cfg_on_delta_exact_three": set(now["cfg_on"]) - set(old["cfg_on"]) == set(names)
    and set(old["cfg_on"]) <= set(now["cfg_on"]),
    "leaf_existing_independent_pfc": len(rows) == 4
    and next(r for r in rows if r["name"] == leaf)["pfc"] == "specfix::merge_profile"
    and not next(r for r in rows if r["name"] == leaf)["stub_verified"],
    "request_exact_order_and_copy": [r["name"] for r in req["harnesses"]]
    == [names[0], names[1], leaf, names[2]]
    and req == json.loads((HERE / "g1.request.json").read_text()),
    "request_envelope": req["request_id"].startswith("bridgenine-")
    and req["kind"] == "measurement" and req["controls"] is True
    and req["runner"] == "gcb-e2-standard-4" and req["kani_jobs"] == 1
    and req["uninit_checks"] is False and req["harness_timeout_minutes"] == 10,
    "negative_literal_count_check_only": [r["expect"] for r in req["harnesses"]]
    == ["SUCCESS", "SUCCESS", "SUCCESS", "FAILED"]
    and req["harnesses"][3]["expect_check"]
    == "bridgenine output preserves full-value probe count"
    and '"bridgenine output preserves full-value probe count"' in caller,
    "actual_stable_api_and_scratch":
    "<u8 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut is_less)" in caller
    and "[MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN]" in caller,
    "same_explicit_fn_pointer": "let mut is_less: fn(&u8, &u8) -> bool = LtU8::CMP;" in caller
    and harnesses.count("bridgenine_stable_caller(v, false);") == 2,
    "independent_shared_probe_ab": harnesses.count("LtU8::set_probe(kani::any());") == 2
    and "set_probe" not in caller,
    "no_caller_assumes_panic_cut_or_other_profiles": "kani::assume" not in added
    and "panic_on_ord_violation" not in added and "Sort4Read" not in added,
    "a_no_stubs_b_and_control_merge_only": "stub" not in direct
    and added.count("#[kani::stub(bidirectional_merge, adapter)]") == 2
    and added.count("#[kani::stub_verified(merge_profile)]") == 2
    and added.count("#[kani::stub(") == 2,
    "oracle_model_only": caller.count("kani::assert(") == 2
    and "model_sorted::<LtU8>(v.as_ptr(), 9)" in caller
    and "count_before == model_count::<LtU8>(v.as_ptr(), 9)" in caller
    and "is_less(" not in caller,
    "payload_flip_after_return_fixed_witness": caller.index("small_sort(")
    < caller.index("v[0] ^= 1;") < caller.index("kani::assert(")
    and "LtU8::set_probe(p);" in harnesses
    and "bridgenine_stable_caller([p; 9], true);" in harnesses,
    "covers_before_oracle": caller.count("kani::cover(true,") == 2
    and caller.rindex("kani::cover(") < caller.index("kani::assert("),
    "line_width": all(len(line) <= 100 for line in src.splitlines()),
}
out = {
    "ok": all(checks.values()), "base": BASE, "checks": checks,
    "ordinary_count": len(now["ordinary"]),
    "ordinary_names_sha256": hashlib.sha256(
        ("\n".join(now["ordinary"]) + "\n").encode()).hexdigest(),
    "cfg_on_before": len(old["cfg_on"]), "cfg_on_after": len(now["cfg_on"]),
    "rows": rows,
    "request_sha256": hashlib.sha256((K1 / "RUN-REQUEST.json").read_bytes()).hexdigest(),
    "reserve_usd": (4 * 10 + 30) * 0.0135,
    "limitation": "Static source/request checks only; compile/proofs/native inventory NOT_RUN",
}
print(json.dumps(out, indent=2))
sys.exit(0 if out["ok"] else 1)
