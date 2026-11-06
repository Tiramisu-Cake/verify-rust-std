# K-1 run `integcheck-g1-20261106-01`: COMPLETE

- head `d1515761df4b630bd9f51812f9f0e6f8b75ab92d`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `3c5bc03f8e54ab920f2a1f76908663a9b0a9cb0cff35b49da4760b9dbcb0d542`
- run 15e40390-276a-446c-852c-a4a4e979ca38 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 4 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 2163812 KiB, wall 7:20.54 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 221 samples, largest sampled sum of RSS 2.60 GiB at 375 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-driver` 2.06 GiB (≤13 GiB), seen 2–439 s, peak sample 377 s
  - `kani-compiler` 1.76 GiB (≤13 GiB), seen 2–66 s, peak sample 52 s
  - `cbmc` 1.48 GiB (≤13 GiB), seen 78–439 s, peak sample 323 s
  - `goto-instrument` 0.06 GiB (≤13 GiB), seen 74–427 s, peak sample 417 s
  - `goto-cc` 0.04 GiB (≤13 GiB), seen 68–413 s, peak sample 68 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 4 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–440 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–439 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–439 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–440 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–439 s, peak sample 2 s
  - simultaneous cbmc RSS 1.42 GiB at 323 s
  - simultaneous driver RSS 2.06 GiB at 377 s
  - cbmc PID 9201: 1.48 GiB peak at 323 s; active `T0:helper_contracts_wide::unstable_network_safety_u8_n32_stubbed`
  - cbmc PID 9172: 1.29 GiB peak at 248 s; active `T0:helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0`
  - cbmc PID 9049: 0.42 GiB peak at 138 s; active `T0:helper_contracts::unstable_network_safety_u8_n13_stubbed`
  - cbmc PID 9241: 0.30 GiB peak at 407 s; active `T0:helper_contracts_wide::swap_safety_u8_backing32`
  - cbmc PID 9407: 0.28 GiB peak at 435 s; active `T0:tag_permutation::reject_duplicate_network_u8_n9`
  - cbmc PID 9078: 0.27 GiB peak at 146 s; active `T0:helper_contracts::unstable_network_safety_u8_n9_stubbed`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| fixed_inputs::reject_mutant_swap_u8_n2 | FAILED | FAILED | 0.32274762 | 1/80 | 6 | 1/1 |
| merge::profiles::profile_full_value_checker_rejects_payload_change_u8 | FAILED | FAILED | 3.2644954 | 1/378 | 60 | 1/1 |
| merge::profiles::profile_wrong_f_insert_rejected_u8 | FAILED | FAILED | 0.9037732 | 1/605 | 66 | 1/1 |
| merge::profiles::profile_wrong_f_merge_rejected_u8 | FAILED | FAILED | 0.7271138 | 1/594 | 77 | 1/1 |
| merge::profiles::profile_wrong_f_sort4_rejected_u64 | FAILED | FAILED | 0.33364993 | 1/552 | 81 | 1/1 |
| merge::profiles::profile_wrong_f_swap_rejected_u8 | FAILED | FAILED | 0.17620292 | 1/247 | 10 | 1/1 |
| tag_permutation::reject_duplicate_network_u8_n9 | FAILED | FAILED | 12.712492 | 1/559 | 18 | 1/2 |
| helper_contracts::rejects_insert_tail_equal_begin_u64 | FAILED | FAILED | 0.1987489 | 1/205 | 9 | 1/3 |
| helper_contracts::rejects_merge_overlapping_dst_u64 | FAILED | FAILED | 0.5202985 | 1/235 | 15 | 1/3 |
| helper_contracts::rejects_swap_comparator_writing_outside_frame_u8 | FAILED | FAILED | 1.8903475 | 1/205 | 4 |  |
| helper_contracts::rejects_swap_outside_backing_u8 | FAILED | FAILED | 0.18649432 | 1/137 | 9 | 1/3 |
| forwarding_contracts::rejects_always_true | FAILED | FAILED | 0.5441407 | 1/588 | 37 | 3/3 |
| forwarding_contracts::rejects_payload_corruption | FAILED | FAILED | 0.8123075 | 1/345 | 18 | 1/1 |
| helper_contracts::swap_safety_u8_backing9 | SUCCESS | SUCCESS | 17.797321 | 0/219 | 4 | 6/6 |
| helper_contracts::unstable_network_safety_u8_n9_stubbed | SUCCESS | SUCCESS | 7.1729608 | 0/387 | 18 | 1/1 |
| helper_contracts::swap_safety_u8_backing13 | SUCCESS | SUCCESS | 17.776968 | 0/219 | 4 | 6/6 |
| helper_contracts::unstable_network_safety_u8_n13_stubbed | SUCCESS | SUCCESS | 13.853836 | 0/387 | 18 | 1/1 |
| helper_contracts_wide::swap_safety_u8_backing32 | SUCCESS | SUCCESS | 33.460003 | 0/234 | 4 | 9/9 |
| helper_contracts_wide::unstable_network_safety_u8_n32_stubbed | SUCCESS | SUCCESS | 122.2593 | 0/387 | 12 | 5/5 |
| helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0 | SUCCESS | SUCCESS | 94.190506 | 0/228 | 8 | 5/5 |
| helper_contracts_wide::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed | SUCCESS | SUCCESS | 7.248298 | 0/269 | 9 | 4/4 |

Failed checks of `slice::sort::shared::smallsort::verify::fixed_inputs::reject_mutant_swap_u8_n2`:
- assertion failed: v[0] <= v[1] @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/fixed_inputs.rs:25

Failed checks of `slice::sort::shared::smallsort::verify::merge::profiles::profile_full_value_checker_rejects_payload_change_u8`:
- full-value checker detects payload corruption @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs:347

Failed checks of `slice::sort::shared::smallsort::verify::merge::profiles::profile_wrong_f_insert_rejected_u8`:
- profile_canonical_comparator::<P>(cmp) @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs:273

Failed checks of `slice::sort::shared::smallsort::verify::merge::profiles::profile_wrong_f_merge_rejected_u8`:
- profile_canonical_comparator::<P>(cmp) @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs:311

Failed checks of `slice::sort::shared::smallsort::verify::merge::profiles::profile_wrong_f_sort4_rejected_u64`:
- profile_canonical_comparator::<P>(cmp) @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs:237

Failed checks of `slice::sort::shared::smallsort::verify::merge::profiles::profile_wrong_f_swap_rejected_u8`:
- profile_canonical_comparator::<P>(cmp) @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs:212

Failed checks of `slice::sort::shared::smallsort::verify::tag_permutation::reject_duplicate_network_u8_n9`:
- every input tag occurs exactly once @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/tag_permutation.rs:55

Failed checks of `slice::sort::shared::smallsort::verify::helper_contracts::rejects_insert_tail_equal_begin_u64`:
- begin < tail && insert_tail_contract_len(begin, tail) > 1 && @ /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:588

Failed checks of `slice::sort::shared::smallsort::verify::helper_contracts::rejects_merge_overlapping_dst_u64`:
- merge_contract_regions_disjoint(v.as_ptr(), dst, v.len()) @ /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:859

Failed checks of `slice::sort::shared::smallsort::verify::helper_contracts::rejects_swap_comparator_writing_outside_frame_u8`:
- Check that *var_9 is assignable @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/helper_contracts.rs:250

Failed checks of `slice::sort::shared::smallsort::verify::helper_contracts::rejects_swap_outside_backing_u8`:
- crate::ub_checks::can_dereference(v_base.wrapping_add(b_pos)) && @ /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:409

Failed checks of `slice::sort::shared::smallsort::verify::forwarding_contracts::rejects_always_true`:
- canonical comparator required @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/forwarding_contracts.rs:60

Failed checks of `slice::sort::shared::smallsort::verify::forwarding_contracts::rejects_payload_corruption`:
- full-value checker rejects payload corruption @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/forwarding_contracts.rs:270

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::fixed_inputs::reject_mutant_swap_u8_n2
- 60 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::profiles::profile_full_value_checker_rejects_payload_change_u8
- 66 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::profiles::profile_wrong_f_insert_rejected_u8
- 77 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::profiles::profile_wrong_f_merge_rejected_u8
- 81 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::profiles::profile_wrong_f_sort4_rejected_u64
- 10 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::profiles::profile_wrong_f_swap_rejected_u8
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::tag_permutation::reject_duplicate_network_u8_n9
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts::rejects_insert_tail_equal_begin_u64
- 15 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts::rejects_merge_overlapping_dst_u64
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts::rejects_swap_comparator_writing_outside_frame_u8
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts::rejects_swap_outside_backing_u8
- 37 unreachable check(s) in slice::sort::shared::smallsort::verify::forwarding_contracts::rejects_always_true
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::forwarding_contracts::rejects_payload_corruption
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts::swap_safety_u8_backing9
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts::unstable_network_safety_u8_n9_stubbed
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts::swap_safety_u8_backing13
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts::unstable_network_safety_u8_n13_stubbed
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts_wide::swap_safety_u8_backing32
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts_wide::unstable_network_safety_u8_n32_stubbed
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts_wide::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed
