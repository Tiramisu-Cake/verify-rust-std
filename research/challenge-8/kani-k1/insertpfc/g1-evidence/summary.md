# K-1 run `insertpfc-g1-20261107-01`: COMPLETE

- head `db5d23de550329235552a2691e69378c148c3f42`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `7812dc811e6d978d054ff2ccd09f693a69c0f5e79c6c9d8b66b527dbd63924de`
- run 4da67e0b-a086-459c-8287-f3ae365566dc attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 5 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 5102236 KiB, wall 4:01.79 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 122 samples, largest sampled sum of RSS 4.91 GiB at 140 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 4.87 GiB (≤13 GiB), seen 76–240 s, peak sample 136 s
  - `kani-compiler` 1.79 GiB (≤13 GiB), seen 2–64 s, peak sample 50 s
  - `kani-driver` 0.18 GiB (≤13 GiB), seen 2–240 s, peak sample 240 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 70–222 s, peak sample 210 s
  - `goto-cc` 0.04 GiB (≤13 GiB), seen 66–220 s, peak sample 220 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–64 s, peak sample 56 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–242 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–240 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 204–204 s, peak sample 204 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–242 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–240 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 4.86 GiB at 128 s
  - simultaneous driver RSS 0.18 GiB at 240 s
  - cbmc PID 8935: 4.87 GiB peak at 136 s; active `T0:helper_contracts::insertion_safety_u64_len3`
  - cbmc PID 8973: 4.76 GiB peak at 194 s; active `T0:helper_contracts::insertion_safety_u64_len2`
  - cbmc PID 9168: 0.28 GiB peak at 238 s; active `T0:tag_permutation::reject_duplicate_network_u8_n9`
  - cbmc PID 8843: 0.12 GiB peak at 76 s; active ``
  - cbmc PID 9139: 0.10 GiB peak at 218 s; active `T0:merge::profiles::profile_full_value_checker_rejects_payload_change_u8`
  - cbmc PID 9056: 0.04 GiB peak at 206 s; active ``
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| helper_contracts::insertion_safety_u64_len2 | SUCCESS | SUCCESS | 55.339634 | 0/164 | 4 | 6/6 |
| helper_contracts::insertion_safety_u64_len3 | SUCCESS | SUCCESS | 63.423126 | 0/164 | 4 | 6/6 |
| fixed_inputs::reject_mutant_swap_u8_n2 | FAILED | FAILED | 0.32335067 | 1/80 | 6 | 1/1 |
| merge::profiles::profile_full_value_checker_rejects_payload_change_u8 | FAILED | FAILED | 8.109631 | 1/378 | 60 | 1/1 |
| merge::profiles::profile_wrong_f_insert_rejected_u8 | FAILED | FAILED | 0.8300799 | 1/605 | 66 | 1/1 |
| merge::profiles::profile_wrong_f_merge_rejected_u8 | FAILED | FAILED | 0.7044573 | 1/594 | 77 | 1/1 |
| merge::profiles::profile_wrong_f_sort4_rejected_u64 | FAILED | FAILED | 0.31860116 | 1/552 | 81 | 1/1 |
| merge::profiles::profile_wrong_f_swap_rejected_u8 | FAILED | FAILED | 0.16503914 | 1/247 | 10 | 1/1 |
| tag_permutation::reject_duplicate_network_u8_n9 | FAILED | FAILED | 17.974674 | 1/559 | 18 | 1/2 |
| helper_contracts::rejects_insert_tail_equal_begin_u64 | FAILED | FAILED | 0.18817593 | 1/205 | 9 | 1/3 |
| helper_contracts::rejects_merge_overlapping_dst_u64 | FAILED | FAILED | 0.49925742 | 1/235 | 15 | 1/3 |
| helper_contracts::rejects_swap_comparator_writing_outside_frame_u8 | FAILED | FAILED | 1.7502549 | 1/205 | 4 |  |
| helper_contracts::rejects_swap_outside_backing_u8 | FAILED | FAILED | 0.17222455 | 1/137 | 9 | 1/3 |
| forwarding_contracts::rejects_always_true | FAILED | FAILED | 0.5235468 | 1/588 | 37 | 3/3 |
| forwarding_contracts::rejects_payload_corruption | FAILED | FAILED | 0.6987619 | 1/345 | 18 | 1/1 |

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
- Check that *var_9 is assignable @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/helper_contracts.rs:276

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
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts::insertion_safety_u64_len2
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::helper_contracts::insertion_safety_u64_len3
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
