# K-1 run `valid-b-full-autoharness`: COMPLETE

- head `20ee8d6941b167f147317a43f6e71661ece727d3`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `5ef6be9e0970b550560e9d5a335f34da5bb0b48e9433dd214cb3af7295dddc05`
- run c1a782cf-ea1f-46d5-8ca5-8fd23c8abbca attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `autoharness`, runner `gcb-e2-standard-4`, whole-job work budget 270 min; per-harness settings from the checked-out workflow, harnesses in parallel 3, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: False; Kani exit 1
- whole run, including compilation: max RSS 6184352 KiB, wall 2:45:09 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- autoharness started: 1892; results: {'SUCCESS': 1890, 'FAILED': 0, 'TIMEOUT': 2, 'OUT_OF_MEMORY': 0, 'MISSING_RESULT': 0}; sum Verification Time: 17176.482 s over 1890 timed harnesses

- memory peaks PARSED: sampled every 2 s, 4820 samples, largest sampled sum of RSS 11.27 GiB at 8219 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-driver` 5.90 GiB (≤13 GiB), seen 2–9909 s, peak sample 9699 s
  - `cbmc` 4.20 GiB (≤13 GiB), seen 744–9907 s, peak sample 7699 s
  - `kani-compiler` 3.70 GiB (≤13 GiB), seen 2–399 s, peak sample 399 s
  - `goto-instrument` 1.81 GiB (≤13 GiB), seen 744–9690 s, peak sample 8279 s
  - `goto-cc` 0.18 GiB (≤13 GiB), seen 401–9123 s, peak sample 457 s
  - `kissat` 0.04 GiB (≤13 GiB), seen 2051–2399 s, peak sample 2269 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–399 s, peak sample 4 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 431–3187 s, peak sample 644 s
  - `cc1plus` 0.01 GiB (≤13 GiB), seen 471–3301 s, peak sample 3113 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–9909 s, peak sample 2 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–9910 s, peak sample 0 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 8.37 GiB at 8219 s
  - simultaneous driver RSS 5.90 GiB at 9699 s
  - simultaneous solver RSS 0.04 GiB at 2269 s
  - cbmc PID 89338: 4.20 GiB peak at 7699 s; active `T0:network::insertion_safety_u64_n20_offsets9_to12,T1:network::dispatch_safety_stable_unstable_bytes17_n32`
  - cbmc PID 90649: 4.19 GiB peak at 8226 s; active `T0:str::validations::verify::check_run_utf8_validation,T1:network::dispatch_safety_stable_unstable_bytes17_n15_16_17,T2:slice::verify::check_reverse`
  - cbmc PID 91349: 3.95 GiB peak at 8591 s; active `T0:network::dispatch_safety_stable_unstable_bytes16_n32,T1:network::dispatch_safety_stable_unstable_bytes16_n15_16_17`
  - cbmc PID 92551: 3.94 GiB peak at 8734 s; active `T0:network::dispatch_safety_stable_unstable_bytes16_n32,T1:network::dispatch_safety_stable_unstable_bytes85_n32`
  - cbmc PID 91058: 3.90 GiB peak at 8217 s; active `T0:str::validations::verify::check_run_utf8_validation,T1:network::dispatch_safety_stable_unstable_bytes85_n0_1_2_7_8`
  - cbmc PID 94035: 3.77 GiB peak at 9536 s; active `T0:network::swap_contract_four_positions_i32,T1:network::network_safety_unstable_u64_n0_to17,T2:network::network_safety_unstable_u64_n30_to32`
  - kissat PID 58028: 0.04 GiB peak at 2269 s; active `T1:num::nonzero::verify::nonzero_check_isqrt_u64_small,T2:ptr::verify::check_align_offset_5`
  - kissat PID 53324: 0.02 GiB peak at 2061 s; active ``
  - kissat PID 58020: 0.02 GiB peak at 2261 s; active `T1:num::nonzero::verify::nonzero_check_isqrt_u128_large,T2:ptr::verify::check_align_offset_5`
  - kissat PID 53170: 0.02 GiB peak at 2051 s; active ``
  - kissat PID 53432: 0.01 GiB peak at 2071 s; active ``
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| intrinsics::verify::should_succeed_i64_to_f64 | workflow | SUCCESS | 0.26177067 | 0/35 | 0 |  |
| intrinsics::verify::should_succeed_bool_to_i8 | workflow | SUCCESS | 0.11248181 | 0/35 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_isize_edge_pos | workflow | SUCCESS | 1.0039551 | 0/127 | 1 | 1/1 |
| intrinsics::verify::should_succeed_u16_to_i16 | workflow | SUCCESS | 0.1016888 | 0/35 | 0 |  |
| intrinsics::verify::should_succeed_bool_to_u8 | workflow | SUCCESS | 0.12455614 | 0/35 | 0 |  |
| intrinsics::verify::should_succeed_char_to_f32 | workflow | SUCCESS | 0.22483495 | 0/106 | 2 |  |
| intrinsics::verify::should_succeed_u64_to_f64 | workflow | SUCCESS | 0.15512276 | 0/35 | 0 |  |
| intrinsics::verify::should_succeed_f64_to_i64 | workflow | SUCCESS | 0.13450313 | 0/35 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_u32_small | workflow | SUCCESS | 0.6424005 | 0/115 | 1 | 1/1 |
| intrinsics::verify::should_succeed_i64_to_u64 | workflow | SUCCESS | 0.12228758 | 0/35 | 0 |  |
| intrinsics::verify::should_succeed_i16_to_u16 | workflow | SUCCESS | 0.11751595 | 0/35 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_i32_large_pos | workflow | SUCCESS | 0.5151791 | 0/118 | 1 | 1/1 |
| collections::vec_deque::verify::check_vecdeque_swap | workflow | SUCCESS | 11.914719 | 0/475 | 9 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_i32_edge_neg | workflow | SUCCESS | 0.6256704 | 0/130 | 1 | 1/1 |
| intrinsics::verify::should_fail_tuple_to_array | workflow | SUCCESS | 0.7152261 | 1/316 | 8 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_u128_small | workflow | SUCCESS | 2.9458375 | 0/115 | 1 | 1/1 |
| intrinsics::verify::should_succeed_tuple_to_array | workflow | SUCCESS | 0.7285829 | 0/316 | 7 |  |
| intrinsics::verify::should_fail_tuple_to_tuple | workflow | SUCCESS | 0.18349838 | 1/54 | 1 |  |
| intrinsics::verify::should_succeed_tuple_to_tuple | workflow | SUCCESS | 0.17525896 | 0/54 | 0 |  |
| intrinsics::verify::should_fail_tuple_to_struct | workflow | SUCCESS | 0.13003723 | 1/54 | 1 |  |
| intrinsics::verify::should_succeed_tuple_to_struct | workflow | SUCCESS | 0.17067234 | 0/54 | 0 |  |
| intrinsics::verify::should_fail_i8_to_bool | workflow | SUCCESS | 0.10292038 | 1/47 | 1 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_usize_small | workflow | SUCCESS | 1.0362217 | 0/115 | 1 | 1/1 |
| intrinsics::verify::should_succeed_i8_to_bool | workflow | SUCCESS | 0.11281748 | 0/47 | 0 |  |
| intrinsics::verify::should_fail_u8_to_bool | workflow | SUCCESS | 0.12330451 | 1/47 | 1 |  |
| intrinsics::verify::should_succeed_u8_to_bool | workflow | SUCCESS | 0.11958619 | 0/47 | 0 |  |
| intrinsics::verify::should_fail_i32_to_char | workflow | SUCCESS | 0.21207519 | 1/128 | 2 |  |
| intrinsics::verify::should_succeed_i32_to_char | workflow | SUCCESS | 0.2055087 | 0/128 | 1 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_i64_edge_pos | workflow | SUCCESS | 0.7915957 | 0/127 | 1 | 1/1 |
| intrinsics::verify::should_fail_f32_to_char | workflow | SUCCESS | 0.20993568 | 1/128 | 2 |  |
| intrinsics::verify::should_succeed_f32_to_char | workflow | SUCCESS | 0.23417145 | 0/128 | 1 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_isize_small | workflow | SUCCESS | 2.8529801 | 0/115 | 1 | 1/1 |
| intrinsics::verify::should_fail_u32_to_char | workflow | SUCCESS | 0.22262762 | 1/128 | 2 |  |
| intrinsics::verify::should_succeed_u32_to_char | workflow | SUCCESS | 0.20541002 | 0/128 | 1 |  |
| intrinsics::verify::transmute_unchecked_char_to_f32 | workflow | SUCCESS | 0.25535423 | 0/143 | 2 |  |
| intrinsics::verify::transmute_unchecked_f32_to_char | workflow | SUCCESS | 0.14741564 | 0/77 | 0 |  |
| intrinsics::verify::transmute_unchecked_i64_to_f64 | workflow | SUCCESS | 0.18878232 | 0/71 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_u64_edge | workflow | SUCCESS | 0.55080676 | 0/121 | 1 | 1/1 |
| intrinsics::verify::transmute_unchecked_u32_to_f32 | workflow | SUCCESS | 0.15383184 | 0/71 | 0 |  |
| intrinsics::verify::transmute_unchecked_u32_to_i32 | workflow | SUCCESS | 0.13955176 | 0/71 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_i32_edge_pos | workflow | SUCCESS | 0.55556256 | 0/127 | 1 | 1/1 |
| intrinsics::verify::transmute_unchecked_i8_to_bool | workflow | SUCCESS | 0.18315051 | 0/77 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_u128_large | workflow | SUCCESS | 1.9694602 | 0/118 | 1 | 1/1 |
| intrinsics::verify::transmute_unchecked_i32_to_u32 | workflow | SUCCESS | 0.19061546 | 0/71 | 0 |  |
| intrinsics::verify::transmute_unchecked_u32_to_char | workflow | SUCCESS | 0.19249026 | 0/77 | 0 |  |
| vec::verify::verify_swap_remove | workflow | SUCCESS | 2.848123 | 0/369 | 4 |  |
| intrinsics::verify::transmute_unchecked_bool_to_i8 | workflow | SUCCESS | 0.20148174 | 0/71 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_u128_edge | workflow | SUCCESS | 1.391529 | 0/121 | 1 | 1/1 |
| intrinsics::verify::transmute_unchecked_u64_to_i64 | workflow | SUCCESS | 0.12918264 | 0/71 | 0 |  |
| intrinsics::verify::transmute_unchecked_char_to_i32 | workflow | SUCCESS | 0.32035545 | 0/143 | 2 |  |
| intrinsics::verify::transmute_unchecked_i128_to_u128 | workflow | SUCCESS | 0.19913661 | 0/71 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_i128_edge_neg | workflow | SUCCESS | 4.236105 | 0/130 | 1 | 1/1 |
| intrinsics::verify::transmute_unchecked_u64_to_f64 | workflow | SUCCESS | 0.19018127 | 0/71 | 0 |  |
| intrinsics::verify::transmute_unchecked_i32_to_char | workflow | SUCCESS | 0.18439628 | 0/77 | 0 |  |
| intrinsics::verify::transmute_unchecked_i16_to_u16 | workflow | SUCCESS | 0.18041396 | 0/71 | 0 |  |
| intrinsics::verify::transmute_unchecked_i8_to_u8 | workflow | SUCCESS | 0.17848882 | 0/71 | 0 |  |
| intrinsics::verify::transmute_unchecked_f32_to_u32 | workflow | SUCCESS | 0.19664288 | 0/71 | 0 |  |
| intrinsics::verify::transmute_unchecked_u8_to_bool | workflow | SUCCESS | 0.14093713 | 0/77 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_i128_large_neg | workflow | SUCCESS | 2.2179153 | 0/121 | 1 | 1/1 |
| alloc::layout::verify::check_array_i32 | workflow | SUCCESS | 2.1702085 | 0/154 | 2 |  |
| intrinsics::verify::transmute_unchecked_i32_to_f32 | workflow | SUCCESS | 0.19903773 | 0/71 | 0 |  |
| intrinsics::verify::transmute_unchecked_f64_to_i64 | workflow | SUCCESS | 0.17693146 | 0/71 | 0 |  |
| intrinsics::verify::transmute_unchecked_i64_to_u64 | workflow | SUCCESS | 0.19609624 | 0/71 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_i64_large_pos | workflow | SUCCESS | 0.8052595 | 0/118 | 1 | 1/1 |
| intrinsics::verify::transmute_unchecked_char_to_u32 | workflow | SUCCESS | 0.27417284 | 0/143 | 2 |  |
| intrinsics::verify::transmute_unchecked_f64_to_u64 | workflow | SUCCESS | 0.13090262 | 0/71 | 0 |  |
| intrinsics::verify::transmute_unchecked_u16_to_i16 | workflow | SUCCESS | 0.13381054 | 0/71 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_i64_edge_neg | workflow | SUCCESS | 1.2658131 | 0/130 | 1 | 1/1 |
| intrinsics::verify::transmute_unchecked_u8_to_i8 | workflow | SUCCESS | 0.13141827 | 0/71 | 0 |  |
| intrinsics::verify::transmute_unchecked_bool_to_u8 | workflow | SUCCESS | 0.15910356 | 0/71 | 0 |  |
| intrinsics::verify::transmute_unchecked_f32_to_i32 | workflow | SUCCESS | 0.19085024 | 0/71 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_i64_large_neg | workflow | SUCCESS | 0.82847726 | 0/121 | 1 | 1/1 |
| intrinsics::verify::transmute_unchecked_u128_to_i128 | workflow | SUCCESS | 0.12869987 | 0/71 | 0 |  |
| alloc::layout::verify::check_extend_packed | workflow | SUCCESS | 3.2800934 | 0/194 | 0 |  |
| num::nonzero::verify::nonzero_check_saturating_mul_for_i8 | workflow | SUCCESS | 0.61588055 | 0/111 | 1 |  |
| num::nonzer
…[summary.md truncated at 12000 bytes; summary.json holds the bounded full record]
