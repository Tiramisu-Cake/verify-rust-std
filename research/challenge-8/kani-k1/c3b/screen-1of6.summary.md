# K-1 run `c3b-screen-1of6`: COMPLETE

- head `afea78b3476bdce3b36b7e2e31fad116c129a497`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `7fd31bb7b7efb3b239b8eb82ca2770678a168fc7bf7c90be4cb97e706531a310`
- run 45a0dd0c-8f94-49d1-932b-ba5759453cac attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 2 min, harnesses in parallel 1, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 2951128 KiB, wall 1:00:52 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 1823 samples, largest sampled sum of RSS 4.50 GiB at 1672 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `cbmc` 2.81 GiB (≤13 GiB), seen 86–3651 s, peak sample 1674 s
  - `kani-compiler` 2.17 GiB (≤13 GiB), seen 2–64 s, peak sample 56 s
  - `kani-driver` 1.88 GiB (≤13 GiB), seen 0–3651 s, peak sample 204 s
  - `kissat` 0.60 GiB (≤13 GiB), seen 164–3631 s, peak sample 1692 s
  - `goto-instrument` 0.09 GiB (≤13 GiB), seen 204–3643 s, peak sample 1692 s
  - `goto-cc` 0.08 GiB (≤13 GiB), seen 66–3510 s, peak sample 82 s
  - `cargo` 0.04 GiB (≤13 GiB), seen 0–64 s, peak sample 2 s
  - `cc1plus` 0.01 GiB (≤13 GiB), seen 80–80 s, peak sample 80 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–3652 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 0–3651 s, peak sample 0 s
  - `time` 0.00 GiB (≤13 GiB), seen 0–3651 s, peak sample 0 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 80–80 s, peak sample 80 s
  - …only the 12 largest commands listed

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| assembly::advancement_merge_up_u8_n2 | SUCCESS | SUCCESS | 0.5466266 | 0/61 | 4 | 2/2 |
| assembly::safety_stable_unit_n31 | SUCCESS | SUCCESS | 42.729424 | 0/280 | 1 | 1/1 |
| assembly::sorted_permutation_swap_u8_n2 | SUCCESS | SUCCESS | 0.35209543 | 0/84 | 4 | 1/1 |
| correct::sorted_permutation_fallback_u64_n13 | SUCCESS | TIMEOUT | None |  | None |  |
| correct::sorted_permutation_fallback_u8_n10 | SUCCESS | SUCCESS | 72.00929 | 0/474 | 60 |  |
| correct::sorted_permutation_fallback_u8_n16 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::drop_fallback_drop_count_n8 | SUCCESS | SUCCESS | 5.651393 | 0/457 | 17 |  |
| merge::drop_general_drop_count_n4 | SUCCESS | SUCCESS | 4.67928 | 0/457 | 9 |  |
| merge::fallback_sorted_permutation_u8_n8 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::fallback_sorted_permutation_u8_u64_n5 | SUCCESS | SUCCESS | 13.74874 | 0/422 | 124 |  |
| merge::general_stable_sorted_permutation_u64_n11 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_stable_sorted_permutation_u64_n5 | SUCCESS | SUCCESS | 19.919996 | 0/638 | 105 |  |
| merge::general_stable_sorted_permutation_u8_n1 | SUCCESS | SUCCESS | 0.8264573 | 0/631 | 130 |  |
| merge::general_stable_sorted_permutation_u8_n2 | SUCCESS | SUCCESS | 5.6079593 | 0/631 | 113 |  |
| merge::general_stable_sorted_permutation_u8_n8 | SUCCESS | SUCCESS | 37.90254 | 0/631 | 99 |  |
| merge::merge_contract_u64_n14 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n7 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u8_n13 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u8_n6 | SUCCESS | SUCCESS | 104.969864 | 0/435 | 100 |  |
| merge::route_safety_all_routes_n12 | SUCCESS | SUCCESS | 43.099483 | 0/637 | 11 |  |
| merge::route_safety_all_routes_n18 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::route_safety_all_routes_n23 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::route_safety_all_routes_n29 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::route_safety_all_routes_n5 | SUCCESS | SUCCESS | 10.35313 | 0/637 | 15 |  |
| merge::sort4_arbitrary_comparator_u64_n4 | SUCCESS | SUCCESS | 5.2004414 | 0/164 | 36 |  |
| network::dispatch_safety_stable_bytes16_n15 | SUCCESS | SUCCESS | 22.08222 | 0/384 | 10 |  |
| network::dispatch_safety_stable_u8_n0_1_2_7_8 | SUCCESS | SUCCESS | 11.056504 | 0/396 | 10 |  |
| network::dispatch_safety_stable_unstable_bytes17_n0_1_2_7_8 | SUCCESS | SUCCESS | 43.326138 | 0/406 | 9 |  |
| network::dispatch_safety_stable_unstable_bytes85_n32 | SUCCESS | TIMEOUT | None |  | None |  |
| network::dispatch_safety_unstable_bytes16_n16 | SUCCESS | SUCCESS | 23.780426 | 0/384 | 8 |  |
| network::dispatch_safety_unstable_u8_n18_31_32 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insert_tail_contract_u64_start14 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insert_tail_contract_u64_start1_tail14 | SUCCESS | SUCCESS | 43.93239 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail5 | SUCCESS | SUCCESS | 15.755873 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start2_tail11 | SUCCESS | SUCCESS | 35.381985 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start2_tail3 | SUCCESS | SUCCESS | 11.97194 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start2_tail9 | SUCCESS | SUCCESS | 25.3694 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start3_tail15 | SUCCESS | SUCCESS | 48.590073 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start3_tail8 | SUCCESS | SUCCESS | 19.252886 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start4_tail14 | SUCCESS | SUCCESS | 41.00312 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start4_tail8 | SUCCESS | SUCCESS | 19.066017 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start9 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insertion_permutation_u8_n10 | SUCCESS | SUCCESS | 2.541774 | 0/114 | 4 |  |
| network::insertion_safety_u64_n13 | SUCCESS | SUCCESS | 52.79456 | 0/95 | 4 |  |
| network::insertion_safety_u64_n16_offsets13_to16 | SUCCESS | SUCCESS | 9.636608 | 0/90 | 4 |  |
| network::insertion_safety_u64_n17_offsets1_to4 | SUCCESS | SUCCESS | 54.93125 | 0/90 | 4 |  |
| network::insertion_safety_u64_n18_offsets5_to8 | SUCCESS | SUCCESS | 44.69607 | 0/90 | 4 |  |
| network::insertion_safety_u64_n19_offsets9_to12 | SUCCESS | SUCCESS | 35.375706 | 0/90 | 4 |  |
| network::insertion_safety_u64_n20_offsets9_to12 | SUCCESS | SUCCESS | 44.611515 | 0/90 | 4 |  |
| network::mutating_insertion_safety_cell_n14 | SUCCESS | SUCCESS | 96.876656 | 0/186 | 4 |  |
| network::mutating_insertion_safety_cell_n16_offsets1_to4 | SUCCESS | SUCCESS | 50.610203 | 0/181 | 4 |  |
| network::mutating_insertion_safety_cell_n17_offsets5_to8 | SUCCESS | SUCCESS | 48.289173 | 0/181 | 4 |  |
| network::mutating_insertion_safety_cell_n18_offsets9_to12 | SUCCESS | SUCCESS | 41.589222 | 0/181 | 4 |  |
| network::mutating_insertion_safety_cell_n1_to5 | SUCCESS | SUCCESS | 9.299325 | 0/222 | 4 |  |
| network::mutating_insertion_safety_cell_n6_to10 | SUCCESS | SUCCESS | 88.65562 | 0/222 | 4 |  |
| network::mutating_route_safety_cell_n5_to8 | SUCCESS | SUCCESS | 15.4655485 | 0/189 | 4 |  |
| network::network_correctness_u64_n13 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u64_n8 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u8_n13 | SUCCESS | SUCCESS | 34.639957 | 0/361 | 21 |  |
| network::network_correctness_u8_n5 | SUCCESS | SUCCESS | 2.4878461 | 0/361 | 18 |  |
| network::network_safety_unstable_u64_n18_to21 | SUCCESS | SUCCESS | 116.86221 | 0/312 | 12 |  |
| network::swap_contract_bytes17_n2 | SUCCESS | SUCCESS | 12.367815 | 0/396 | 5 |  |
| network::swap_contract_four_positions_u64 | SUCCESS | SUCCESS | 8.732835 | 0/347 | 5 |  |
| network::swap_contract_u64_n2 | SUCCESS | SUCCESS | 6.952778 | 0/404 | 5 |  |
| network::swap_contract_u8_n2 | SUCCESS | SUCCESS | 4.812334 | 0/404 | 5 |  |

Tooling SHA-256 at the run commit:
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 9d8fea987d2f76f61f830ba0d5beebc03211c0ed2e1076b03c1332905bf0096f
- `research/challenge-8/kani-k1/tools/kani_k1.py` e732269a43cd6f15f68df13d1e28fb8ab593a7e135094113eec2c33522515ed0
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::advancement_merge_up_u8_n2
- 1 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n31
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::sorted_permutation_swap_u8_n2
- 60 unreachable check(s) in slice::sort::shared::smallsort::verify::correct::sorted_permutation_fallback_u8_n10
- 17 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::drop_fallback_drop_count_n8
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::drop_general_drop_count_n4
- 124 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::fallback_sorted_permutation_u8_u64_n5
- 105 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n5
- 130 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n1
- 113 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n2
- 99 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n8
- 100 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_contract_u8_n6
- 11 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_all_routes_n12
- 15 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_all_routes_n5
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::sort4_arbitrary_comparator_u64_n4
- 10 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_bytes16_n15
- 10 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_u8_n0_1_2_7_8
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_unstable_bytes17_n0_1_2_7_8
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_unstable_bytes16_n16
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail14
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail5
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start2_tail11
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start2_tail3
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start2_tail9
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start3_tail15
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start3_tail8
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start4_tail14
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start4_tail8
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insertion_permutation_u8_n10
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insertion_safety_
…[summary.md truncated at 12000 bytes; summary.json holds the bounded full record]
