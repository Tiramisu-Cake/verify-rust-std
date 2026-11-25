"""Check the pinned REV2 S13 source binding and its extracted Boolean network."""

import re
import subprocess
import sys
from pathlib import Path


SMALLSORT = "library/core/src/slice/sort/shared/smallsort.rs"
VERIFY = SMALLSORT.removesuffix(".rs") + "/verify"
STD = "217b8efaa6c9c0d6e5d44f77e98d74bd5493360a"
BINDING = "32c2857f4b7137601de54ea42a02610c8fd29ed9"
FIX3 = "32129c149a15fb1b60a7314e738f3cb466d076e5"
COMMON = {
    SMALLSORT: "0b77c3dbb3b767ba35281a2a686aa477ff1344c5",
    "library/core/src/slice/mod.rs": "13f6a07ec8422a835375372b5c1cb67a6898673d",
    "library/core/src/slice/raw.rs": "154c5356d99ee7edcb395e2c364a8e2ac22a9375",
    "library/core/src/slice/index.rs": "522603c574bad1c7181e2cca597dd9326e26500d",
    f"{VERIFY}/cal1_model.rs": "236394dcfb1ff571ee6f816391f7b2e00cc9e630",
    f"{VERIFY}/cal1_q_merge_model.rs": "d3c2a137f7332d79e7ce8596a517fd8b5f2dbe19",
    f"{VERIFY}/rev2_provider_cost.rs": "c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de",
}
FIXTURES = {
    (BINDING, f"{VERIFY}/rev2_s13_binding.rs"): "8718e67a68f473a6e7367d168a34410f40d324eb",
    (STD, f"{VERIFY}/rev2_s13_geometries.rs"): "c403b343270752fb03fc087a101b55d8dc20a7ab",
}


def require(condition, message):
    if not condition:
        sys.exit(f"Re-audit required: {message}")


def code(source):
    return " ".join(re.sub(r"(?m)^\s*//[^\n]*", "", source).split())


def main(worktree):
    def git(*args):
        return subprocess.check_output(("git", "-C", worktree, *args), text=True).strip()

    require(
        git("show", "-s", "--format=%T %P", STD)
        == f"ff2563b5867b8327b95db909262ddf80e3ed9c03 {BINDING}"
        and git("show", "-s", "--format=%T %P", BINDING)
        == f"0e682cfceaed5d33d3d3374b5dc97da5012bba93 {FIX3}"
        and git("rev-parse", f"{FIX3}^{{tree}}") == "1b0cc32c571b370178e64f2b8c79773d2ce27051",
        "Std/FIX3 commit chain or tree",
    )
    for path, blob in COMMON.items():
        for revision in (FIX3, BINDING, STD):
            require(git("rev-parse", f"{revision}:{path}") == blob, f"{revision}:{path}")
        require(git("hash-object", "--no-filters", path) == blob, f"worktree {path}")
    for (revision, path), blob in FIXTURES.items():
        require(git("rev-parse", f"{revision}:{path}") == blob, f"{revision}:{path}")

    source = Path(worktree, SMALLSORT).read_text()
    network = code(source.split("fn small_sort_network<", 1)[1].split("\n}\n", 1)[0])
    require(
        "const SMALL_SORT_NETWORK_THRESHOLD: usize = 32; "
        "const SMALL_SORT_NETWORK_SCRATCH_LEN: usize = SMALL_SORT_NETWORK_THRESHOLD;" in code(source)
        and "let len = v.len(); if len < 2 { return; } "
        "if len > SMALL_SORT_NETWORK_SCRATCH_LEN { intrinsics::abort_immediate(); }" in network
        and "let len_div_2 = len / 2; let no_merge = len < 18; "
        "let v_base = v.as_mut_ptr(); let initial_region_len = if no_merge { len } else { len_div_2 }; "
        "let mut region = unsafe { slice::from_raw_parts_mut(v_base, initial_region_len) }; "
        "loop { let presorted_len = if region.len() >= 13 { sort13_optimal(region, is_less); 13 }"
        in network
        and "insertion_sort_shift_left(region, presorted_len, is_less); "
        "if no_merge { return; } if region.as_ptr() != v_base { break; } "
        "unsafe { region = slice::from_raw_parts_mut(v_base.add(len_div_2), len - len_div_2) };"
        in network,
        "actual N32 split, sort13 dispatch, or insertion boundary",
    )

    signature = "fn sort13_optimal<T, F>(v: &mut [T], is_less: &mut F)"
    sort13 = code(source.split(signature, 1)[1].split("\n}\n", 1)[0] + "\n}")
    call = r"swap_if_less\(v_base, (\d+), (\d+), is_less\);"
    require(
        re.fullmatch(
            r"where F: FnMut\(&T, &T\) -> bool, \{ "
            r"if v\.len\(\) < 13 \{ intrinsics::abort_immediate\(\); \} "
            r"let v_base = v\.as_mut_ptr\(\); unsafe \{ "
            rf"(?:{call} ){{45}}\}} \}}",
            sort13,
        ),
        "sort13 guard, base pointer, call arguments or control flow",
    )
    pairs = [(int(a), int(b)) for a, b in re.findall(call, sort13)]
    leaf = git("show", f"{FIX3}:{VERIFY}/rev2_provider_cost.rs")
    schedule = leaf.split("const SWAP_PAIRS:", 1)[1].split("];", 1)[0]
    require(
        pairs == [(int(a), int(b)) for a, b in re.findall(r"\((\d+), (\d+)\)", schedule)]
        and len(pairs) == 45
        and all(0 <= a < b < 13 for a, b in pairs),
        "ordered calls or FIX3 selector domain",
    )

    low_bits = (1 << 13) - 1
    for mask in range(low_bits + 1):
        bits = [(mask >> i) & 1 for i in range(13)]
        for a, b in pairs:
            bits[a], bits[b] = bits[a] & bits[b], bits[a] | bits[b]
        observed = sum(bit << i for i, bit in enumerate(bits))
        expected = low_bits ^ (low_bits >> mask.bit_count())
        require(observed == expected, f"extracted Boolean network on mask {mask}")
    print("Pinned source and anchor fixtures match; actual N32 split 16+16; 45 ordered FIX3 calls")
    print("Extracted Boolean network: 8192/8192 masks match sorted popcount")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"Usage: {sys.argv[0]} STD_WORKTREE")
    main(sys.argv[1])
