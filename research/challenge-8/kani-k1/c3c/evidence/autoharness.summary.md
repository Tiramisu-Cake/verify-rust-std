# K-1 run `c3c-full-autoharness`: PARTIAL

- head `2cc4a5871bf6da42d23137208247c0cf8dacb44c`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `103ae1340f20eeec91024eb5a1c4bb3a6df67f7455582a3e6012c480a67f79cc`
- run be070a8b-f0ca-4d6c-8f86-f8aff7915cbd attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `autoharness`, runner `gcb-e2-standard-4`, per-harness timeout 270 min, harnesses in parallel 3, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: False; Kani exit 124
- whole run, including compilation: max RSS None KiB, wall None (UNPARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- autoharness started: 1959; results: {'SUCCESS': 1951, 'FAILED': 0, 'TIMEOUT': 5, 'OUT_OF_MEMORY': 0, 'MISSING_RESULT': 3}; sum Verification Time: 25773.944 s over 1951 timed harnesses

- memory peaks PARSED: sampled every 2 s, 7197 samples, largest sampled sum of RSS 13.54 GiB at 10754 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-driver` 8.06 GiB (≤13 GiB), seen 2–14453 s, peak sample 12331 s
  - `cbmc` 4.34 GiB (≤13 GiB), seen 1164–14454 s, peak sample 10708 s
  - `kani-compiler` 3.74 GiB (≤13 GiB), seen 4–682 s, peak sample 672 s
  - `goto-instrument` 1.81 GiB (≤13 GiB), seen 1162–14342 s, peak sample 4821 s
  - `goto-cc` 0.18 GiB (≤13 GiB), seen 684–14416 s, peak sample 883 s
  - `kissat` 0.04 GiB (≤13 GiB), seen 2079–2594 s, peak sample 2089 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 4–682 s, peak sample 142 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cc1plus` 0.01 GiB (≤13 GiB), seen 703–11248 s, peak sample 1629 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 686–9887 s, peak sample 4259 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–14454 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–14453 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 8.38 GiB at 10754 s
  - simultaneous driver RSS 8.06 GiB at 12331 s
  - simultaneous solver RSS 0.03 GiB at 2085 s
  - cbmc PID 111150: 4.34 GiB peak at 10708 s; active `T0:correct::contract_insert_tail_u8_scratch,T1:network::insertion_safety_u64_n17_offsets5_to8,T2:network::insert_tail_contract_u64_start13`
  - cbmc PID 112521: 3.94 GiB peak at 11855 s; active `T0:correct::sorted_permutation_fallback_u64_n16,T1:network::mutating_insertion_safety_cell_n6_to10,T2:network::insertion_permutation_u64_n12`
  - cbmc PID 113897: 3.88 GiB peak at 14250 s; active `T0:correct::sorted_permutation_fallback_u8_n13,T1:network::dispatch_safety_stable_unstable_bytes16_n32,T2:network::network_correctness_u8_n14`
  - cbmc PID 113492: 3.69 GiB peak at 13620 s; active `T0:correct::sorted_permutation_fallback_u8_n15,T1:network::dispatch_safety_stable_unstable_bytes16_n31,T2:network::network_correctness_u8_n17`
  - cbmc PID 113167: 3.62 GiB peak at 12891 s; active `T0:correct::sorted_permutation_fallback_u8_n16,T1:network::insertion_safety_u64_n11_to12,T2:network::swap_contract_bytes86_n2`
  - cbmc PID 112629: 3.51 GiB peak at 12090 s; active `T0:correct::sorted_permutation_fallback_u64_n16,T1:network::mutating_insertion_safety_cell_n14,T2:network::insertion_permutation_u64_n12`
  - kissat PID 62787: 0.04 GiB peak at 2089 s; active ``
  - kissat PID 62777: 0.03 GiB peak at 2079 s; active ``
  - kissat PID 68249: 0.02 GiB peak at 2590 s; active `T0:ffi::c_str::verify::check_bytes,T1:ptr::mut_ptr::verify::check_mut_add_usize,T2:num::verify::carrying_mul_u64_mid_edge`
  - kissat PID 68071: 0.01 GiB peak at 2580 s; active `T0:ffi::c_str::verify::check_to_str`
  - kissat PID 67763: 0.01 GiB peak at 2564 s; active `T0:ffi::c_str::verify::check_to_str`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| num::nonzero::verify::nonzero_check_clamp_for_u128 | workflow | SUCCESS | 2.0145748 | 0/122 | 1 | 1/1 |
| collections::vec_deque::verify::check_vecdeque_swap | workflow | SUCCESS | 15.305007 | 0/475 | 9 |  |
| num::nonzero::verify::nonzero_check_clamp_for_32 | workflow | SUCCESS | 0.8153682 | 0/122 | 1 | 1/1 |
| num::nonzero::verify::nonzero_check_clamp_for_u64 | workflow | SUCCESS | 1.4484385 | 0/122 | 1 | 1/1 |
| num::nonzero::verify::nonzero_check_min_for_i128 | workflow | SUCCESS | 0.24296509 | 0/64 | 1 |  |
| num::nonzero::verify::nonzero_check_min_for_u128 | workflow | SUCCESS | 0.15516031 | 0/64 | 1 |  |
| num::nonzero::verify::nonzero_check_min_for_u32 | workflow | SUCCESS | 0.17693739 | 0/64 | 1 |  |
| num::nonzero::verify::nonzero_check_min_for_i16 | workflow | SUCCESS | 0.13906929 | 0/64 | 1 |  |
| num::nonzero::verify::nonzero_check_min_for_u64 | workflow | SUCCESS | 0.39282298 | 0/64 | 1 |  |
| num::nonzero::verify::nonzero_check_min_for_i8 | workflow | SUCCESS | 0.09542059 | 0/64 | 1 |  |
| num::nonzero::verify::nonzero_check_min_for_i32 | workflow | SUCCESS | 0.1701585 | 0/64 | 1 |  |
| num::nonzero::verify::nonzero_check_min_for_i64 | workflow | SUCCESS | 0.6495147 | 0/64 | 1 |  |
| num::nonzero::verify::nonzero_check_min_for_u8 | workflow | SUCCESS | 0.14069742 | 0/64 | 1 |  |
| num::nonzero::verify::nonzero_check_min_for_usize | workflow | SUCCESS | 0.31902966 | 0/64 | 1 |  |
| num::nonzero::verify::nonzero_check_min_for_isize | workflow | SUCCESS | 0.53345734 | 0/64 | 1 |  |
| num::nonzero::verify::nonzero_check_min_for_u16 | workflow | SUCCESS | 0.1592588 | 0/64 | 1 |  |
| num::nonzero::verify::nonzero_check_max_for_i16 | workflow | SUCCESS | 0.1335779 | 0/76 | 1 |  |
| num::nonzero::verify::nonzero_check_max_for_i128 | workflow | SUCCESS | 0.16684978 | 0/76 | 1 |  |
| num::nonzero::verify::nonzero_check_max_for_u64 | workflow | SUCCESS | 0.5541131 | 0/76 | 1 |  |
| num::nonzero::verify::nonzero_check_max_for_usize | workflow | SUCCESS | 0.56180364 | 0/76 | 1 |  |
| num::nonzero::verify::nonzero_check_max_for_i8 | workflow | SUCCESS | 0.09470414 | 0/76 | 1 |  |
| num::nonzero::verify::nonzero_check_max_for_u128 | workflow | SUCCESS | 0.16673721 | 0/76 | 1 |  |
| num::nonzero::verify::nonzero_check_max_for_i32 | workflow | SUCCESS | 0.15598802 | 0/76 | 1 |  |
| num::nonzero::verify::nonzero_check_max_for_u32 | workflow | SUCCESS | 0.18131226 | 0/76 | 1 |  |
| num::nonzero::verify::nonzero_check_max_for_u8 | workflow | SUCCESS | 0.14878863 | 0/76 | 1 |  |
| num::nonzero::verify::nonzero_check_max_for_u16 | workflow | SUCCESS | 0.18216583 | 0/76 | 1 |  |
| vec::verify::verify_swap_remove | workflow | SUCCESS | 3.9828706 | 0/369 | 4 |  |
| num::nonzero::verify::nonzero_check_max_for_isize | workflow | SUCCESS | 0.18323953 | 0/76 | 1 |  |
| num::nonzero::verify::nonzero_check_max_for_i64 | workflow | SUCCESS | 0.13563792 | 0/76 | 1 |  |
| num::nonzero::verify::nonzero_check_cmp_for_u8 | workflow | SUCCESS | 0.18739066 | 0/101 | 1 |  |
| num::nonzero::verify::nonzero_check_cmp_for_usize | workflow | SUCCESS | 0.30771664 | 0/101 | 1 |  |
| num::nonzero::verify::nonzero_check_cmp_for_i16 | workflow | SUCCESS | 0.15638696 | 0/101 | 1 |  |
| num::nonzero::verify::nonzero_check_cmp_for_i64 | workflow | SUCCESS | 0.36439207 | 0/101 | 1 |  |
| num::nonzero::verify::nonzero_check_cmp_for_u128 | workflow | SUCCESS | 0.70948684 | 0/101 | 1 |  |
| num::nonzero::verify::nonzero_check_cmp_for_u64 | workflow | SUCCESS | 0.21091717 | 0/101 | 1 |  |
| num::nonzero::verify::nonzero_check_cmp_for_u16 | workflow | SUCCESS | 0.13895828 | 0/101 | 1 |  |
| num::nonzero::verify::nonzero_check_cmp_for_isize | workflow | SUCCESS | 0.3270141 | 0/101 | 1 |  |
| num::nonzero::verify::nonzero_check_cmp_for_i128 | workflow | SUCCESS | 0.43264806 | 0/101 | 1 |  |
| num::nonzero::verify::nonzero_check_cmp_for_u32 | workflow | SUCCESS | 0.3331847 | 0/101 | 1 |  |
| num::nonzero::verify::nonzero_check_cmp_for_i32 | workflow | SUCCESS | 0.27558464 | 0/101 | 1 |  |
| num::nonzero::verify::nonzero_check_cmp_for_i8 | workflow | SUCCESS | 0.16823213 | 0/101 | 1 |  |
| num::nonzero::verify::nonzero_check_from_mut_u64 | workflow | SUCCESS | 0.06994217 | 0/21 | 0 |  |
| num::nonzero::verify::nonzero_check_from_mut_u32 | workflow | SUCCESS | 0.064312465 | 0/21 | 0 |  |
| num::nonzero::verify::nonzero_check_from_mut_i16 | workflow | SUCCESS | 0.080032244 | 0/21 | 0 |  |
| num::nonzero::verify::nonzero_check_from_mut_u16 | workflow | SUCCESS | 0.078247346 | 0/21 | 0 |  |
| num::nonzero::verify::nonzero_check_from_mut_u128 | workflow | SUCCESS | 0.090336375 | 0/21 | 0 |  |
| num::nonzero::verify::nonzero_check_from_mut_i64 | workflow | SUCCESS | 0.06764808 | 0/21 | 0 |  |
| num::nonzero::verify::nonzero_check_from_mut_i128 | workflow | SUCCESS | 0.072263464 | 0/21 | 0 |  |
| num::nonzero::verify::nonzero_check_from_mut_isize | workflow | SUCCESS | 0.072462246 | 0/21 | 0 |  |
| num::nonzero::verify::nonzero_check_from_mut_i8 | workflow | SUCCESS | 0.06948857 | 0/21 | 0 |  |
| num::nonzero::verify::nonzero_check_from_mut_usize | workflow | SUCCESS | 0.06791472 | 0/21 | 0 |  |
| num::nonzero::verify::nonzero_check_from_mut_u8 | workflow | SUCCESS | 0.06419616 | 0/21 | 0 |  |
| num::nonzero::verify::nonzero_check_from_mut_i32 | workflow | SUCCESS | 0.064252876 | 0/21 | 0 |  |
| num::nonzero::verify::nonzero_check_from_mut_unchecked_usize | workflow | SUCCESS | 0.5352889 | 0/102 | 1 |  |
| alloc::layout::verify::check_array_i32 | workflow | SUCCESS | 3.6152937 | 0/154 | 2 |  |
| num::nonzero::verify::nonzero_check_from_mut_unchecked_i8 | workflow | SUCCESS | 0.37846115 | 0/102 | 1 |  |
| num::nonzero::verify::nonzero_check_from_mut_unchecked_isize | workflow | SUCCESS | 0.47892788 | 0/102 | 1 |  |
| num::nonzero::verify::nonzero_check_from_mut_unchecked_i128 | workflow | SUCCESS | 0.3187708 | 0/102 | 1 |  |
| num::nonzero::verify::nonzero_check_from_mut_unchecked_u32 | workflow | SUCCESS | 0.37989685 | 0/102 | 1 |  |
| num::nonzero::verify::nonzero_check_from_mut_unchecked_i32 | workflow | SUCCESS | 0.4218095 | 0/102 | 1 |  |
| num::nonzero::verify::nonzero_check_from_mut_unchecked_i16 | workflow | SUCCESS | 0.3312329 | 0/102 | 1 |  |
| num::nonzero::verify::nonzero_check_from_mut_unchecked_i64 | workflow | SUCCESS | 0.31526774 | 0/102 | 1 |  |
| num::nonzero::verify::nonzero_check_from_mut_unchecked_u16 | workflow | SUCCESS | 0.30612606 | 0/102 | 1 |  |
| num::nonzero::verify::nonzero_check_from_mut_unchecked_u64 | workflow | SUCCESS | 0.30209023 | 0/102 | 1 |  |
| num::nonzero::verify::nonzero_check_from_mut_unchecked_u8 | workflow | SUCCESS | 0.29711917 | 0/102 | 1 |  |
| num::nonzero::verify::nonzero_check_from_mut_unchecked_u128 | workflow | SUCCESS | 0.31419834 | 0/102 | 1 |  |
| alloc::layout::verify::check_extend_packed | workflow | SUCCESS | 3.5375018 | 0/194 | 0 |  |
| num::nonzero::verify::nonzero_check_new_for_i128 | workflow | SUCCESS | 2.3298306 | 0/224 | 3 |  |
| mem::verify::check_swap_adt_no_drop | workflow | SUCCESS | 1.5078743 | 0/382 | 5 |  |
| num::nonzero::verify::nonzero_check_new_for_u64 | workflow | SUCCESS | 1.2676163 | 0/224 | 3 |  |
| num::nonzero::verify::nonzero_check_new_for_i8 | workflow | SUCCESS | 0.58079976 | 0/224 | 3 |  |
| alloc::layout::verify::check_repeat_packed | workflow | SUCCESS | 3.9648514 | 0/197 | 0 |  |
| num::nonzero::verify::nonzero_check_new_for_u32 | workflow | SUCCESS | 0.8692055 | 0/224 | 3 |  |
| num::nonzero::verify::nonzero_check_new_for_u128 | workflow | SUCCESS | 2.1651018 | 0/224 | 3 |  |
| num::nonzero::verify::nonzero_check_new_for_u8 | workflow | SUCCESS | 0.5811779 | 0/224 | 3 |  |
| alloc::layout::verify::check_extend | workflow | SUCCESS | 11.91847 | 0/248 | 0 |  |
| num::nonzero::verify::nonzero_check_new_for_i64 | workflow | SUCCES
…[summary.md truncated at 12000 bytes; summary.json holds the bounded full record]
