#!/usr/bin/env python3
"""Read-only WRAP-N2 source/request gate. No compilation or proof acceptance is inferred."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

K1 = Path(__file__).resolve().parents[1]
ROOT = K1.parents[2]
BASE = "6f3a2629615cc7184b840d3c21aaea54b129267e"
S = "library/core/src/slice/sort/shared/smallsort"
sys.path.insert(0, str(K1 / "tools"))
import kani_k1


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


checks = {}


def check(name, ok, detail=None):
    checks[name] = {"ok": bool(ok), "detail": detail}


def read(path):
    return (ROOT / path).read_text()


reg = "#[cfg(kani_smallsort_controls)]\nmod wrap;\n"
verify = read(S + "/verify.rs")
baseline = subprocess.check_output(["git", "-C", str(ROOT), "show", BASE + ":" + S + "/verify.rs"])
check("single_cfg_registration_at_end", verify.count(reg) == 1 and verify.endswith(reg))
check("ordinary_verify_projection_byte_identical", verify.removesuffix(reg).encode() == baseline)
changed = git("diff", "--name-only", BASE, "--", "library").splitlines()
untracked = git("ls-files", "--others", "--exclude-standard", "--", "library").splitlines()
check("library_scope_only_wrap_and_registration",
      set(changed + untracked) == {S + "/verify.rs", S + "/verify/wrap.rs"}, changed + untracked)
lane = [".circleci", ".github/workflows", "scripts/run-kani.sh", "rust-toolchain.toml",
        "tool_config/kani-version.toml", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", ".gitmodules", ".cargo", "library/.cargo",
        "library/Cargo.toml", "library/Cargo.lock"]
check("lane_and_pin_unchanged", not git("diff", "--name-only", BASE, "--", *lane))
src = read(S + "/verify/wrap.rs")
check("no_stubs_or_assumes_or_shared_statics",
      not re.search(r"kani::(?:stub|stub_verified|assume)\b|\bstatic\s|merge::specfix", src))
check("exact_three_pfc_targets", re.findall(r"#\[kani::proof_for_contract\((\w+)\)\]", src)
      == ["stable_cell", "unstable_byte", "freeze_noncopy"])
check("five_total_harnesses", src.count("#[kani::proof]") == 2
      and src.count("#[kani::proof_for_contract(") == 3)
check("unwinding_assertions_retained", src.count("#[kani::unwind(16)]") == 5
      and "unwinding-assertions" not in src)
specs = re.findall(r"#\[kani::(?:requires|modifies|ensures)\((.*?)\)\]", src, re.S)
check("fifteen_clauses_no_callback_calls", len(specs) == 15 and not any(
      re.search(r"\b(?:cmp|is_less|cell_less|byte_less|noncopy_less)\s*\(", s) for s in specs))
check("scalar_old_count_same_probe", src.count("old(pair_count(v, probe)) == pair_count(v, probe)") == 3)
check("input_only_frames", src.count("#[kani::modifies(ptr::slice_from_raw_parts_mut(v, 2))]") == 3)
check("full_value_count_not_key_count", "(v[0].model() == probe) as usize" in src
      and "(v[1].model() == probe) as usize" in src)
check("all_expected_trait_entries", all(t in src for t in [
      "<Cell<u8> as StableSmallSortTypeImpl>::small_sort(v, scratch, &mut is_less)",
      "<u8 as UnstableSmallSortTypeImpl>::small_sort(v, &mut is_less)",
      "<NonCopyU8 as UnstableSmallSortFreezeTypeImpl>::small_sort(v, &mut is_less)"]))
check("noncopy_local_transparent_no_copy_or_drop", "#[repr(transparent)]\nstruct NonCopyU8(u8);" in src
      and not re.search(r"impl.*(?:Copy|Drop).*for NonCopyU8|#\[derive", src))
check("rust_width_le_100", all(len(line) <= 100 for line in src.splitlines()))
manifest = json.loads((K1 / "wraptwo/manifest.json").read_text())
for name in ["g1", "g2-retry", "inventory-ordinary"]:
    request = json.loads((K1 / f"wraptwo/{name}.request.json").read_text())
    kani_k1.validate_request(request)
    check(name + "_valid", True)
    if request["kind"] == "measurement":
        check(name + "_exact_rows", request["harnesses"] == manifest["harnesses"])
        check(name + "_settings", request.get("controls") is True
              and request.get("kani_jobs") == 1 and request.get("uninit_checks") is False
              and request["harness_timeout_minutes"] == 10)
for row in manifest["harnesses"]:
    name = row["name"].rsplit("::", 1)[1]
    check("harness_present:" + name, bool(re.search(rf"fn {name}\(\)", src)))
    if row["expect"] == "FAILED":
        hits = [i + 1 for i, line in enumerate(src.splitlines())
                if '"' + row["expect_check"] + '"' in line and "kani::assert" in line]
        check("unique_literal:" + name, len(hits) == 1, {"source_lines": hits})
check("run_request_equals_g2", (K1 / "RUN-REQUEST.json").read_bytes()
      == (K1 / "wraptwo/g2-retry.request.json").read_bytes())
check("raw_pair_interface_constructs_exact_n2",
      src.count("let v = unsafe { slice::from_raw_parts_mut(v, 2) };") == 3
      and all(re.search(rf"unsafe fn {name}\([^)]*v: \*mut", src, re.S)
              for name in ["stable_cell", "unstable_byte", "freeze_noncopy"]))
check("stable_retains_scratch_exclusivity", "#[kani::requires(stable_region(v, scratch))]" in src
      and "d as usize >= 2" in src and "d.unsigned_abs() >= scratch.len()" in src)
ok = all(c["ok"] for c in checks.values())
print(json.dumps({"base": BASE, "head": git("rev-parse", "HEAD"), "ok": ok,
                  "scope": "lexical source/request checks only; compile and proofs NOT_RUN",
                  "wrap_sha256": hashlib.sha256(src.encode()).hexdigest(), "checks": checks}, indent=1))
sys.exit(0 if ok else 1)
