# K-1 run `c3c-memory-baseline-5m`: COMPLETE

- head `f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `96ea7fdd9acd69d06081b70e9f4dcbeae89f410452f237b13aa25fb09901a52f`
- run e358163c-9006-4ea0-a402-c12a5a009747 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 5 min, harnesses in parallel 3, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 5799796 KiB, wall 29:38.32 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 886 samples, largest sampled sum of RSS 11.02 GiB at 912 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-driver` 5.53 GiB (≤13 GiB), seen 2–1776 s, peak sample 392 s
  - `cbmc` 4.12 GiB (≤13 GiB), seen 74–1776 s, peak sample 1206 s
  - `kani-compiler` 2.01 GiB (≤13 GiB), seen 2–68 s, peak sample 56 s
  - `goto-cc` 0.07 GiB (≤13 GiB), seen 70–691 s, peak sample 691 s
  - `goto-instrument` 0.06 GiB (≤13 GiB), seen 74–1477 s, peak sample 695 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–68 s, peak sample 68 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 70–382 s, peak sample 382 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1778 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1776 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 70–382 s, peak sample 382 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1776 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 6.97 GiB at 912 s
  - simultaneous driver RSS 5.52 GiB at 390 s
  - cbmc PID 9973: 4.12 GiB peak at 1206 s; active `T0:network::network_correctness_u8_n17,T1:network::insert_tail_contract_u64_start1,T2:merge::route_safety_all_routes_n32`
  - cbmc PID 9879: 3.92 GiB peak at 914 s; active `T0:network::network_correctness_u64_n8,T1:merge::merge_contract_u64_n14,T2:merge::route_safety_all_routes_n31`
  - cbmc PID 10011: 2.85 GiB peak at 1121 s; active `T0:network::network_correctness_u8_n17,T1:network::insert_tail_contract_u64_start1,T2:network::insert_tail_contract_u64_start6`
  - cbmc PID 10078: 2.76 GiB peak at 1332 s; active `T1:network::network_correctness_u8_n16,T2:network::insert_tail_contract_u64_start6`
  - cbmc PID 9475: 2.48 GiB peak at 370 s; active `T0:network::insertion_permutation_u64_n12,T1:correct::sorted_permutation_general_stable_u8_n14,T2:merge::merge_contract_u64_n16`
  - cbmc PID 9702: 2.28 GiB peak at 671 s; active `T0:network::network_correctness_u64_n13,T1:merge::merge_contract_u64_n5,T2:merge::merge_contract_u64_n15`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::merge_contract_u64_n14 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u8_n17 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n15 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::route_safety_all_routes_n31 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::route_safety_all_routes_n32 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insert_tail_contract_u64_start6 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u8_n16 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u64_n8 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u64_n13 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n16 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insertion_permutation_u64_n12 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insert_tail_contract_u64_start1 | SUCCESS | TIMEOUT | None |  | None |  |
| correct::sorted_permutation_general_stable_u8_n14 | SUCCESS | SUCCESS | 303.7755 | 0/723 | 82 | 2/2 |
| correct::sorted_permutation_fallback_u64_n8 | SUCCESS | SUCCESS | 76.92248 | 0/481 | 60 | 1/1 |
| assembly::safety_stable_unit_n31 | SUCCESS | SUCCESS | 88.01203 | 0/280 | 1 | 1/1 |
| assembly::safety_stable_unit_n32 | SUCCESS | SUCCESS | 52.73865 | 0/273 | 5 | 1/1 |
| assembly::safety_stable_unit_n17 | SUCCESS | SUCCESS | 15.581951 | 0/280 | 1 | 1/1 |
| assembly::safety_stable_unit_n16 | SUCCESS | SUCCESS | 5.483779 | 0/272 | 5 | 1/1 |
| assembly::safety_stable_unit_n8 | SUCCESS | SUCCESS | 2.6380239 | 0/272 | 6 | 1/1 |
| assembly::permutation_merge_u8_n4 | SUCCESS | SUCCESS | 2.1580024 | 0/149 | 4 | 1/1 |
| assembly::sorted_network_prefix_u8_n10 | SUCCESS | SUCCESS | 7.468569 | 0/179 | 11 | 1/1 |
| assembly::advancement_merge_up_u8_n2 | SUCCESS | SUCCESS | 0.98005396 | 0/61 | 4 | 2/2 |
| network::network_correctness_u64_n7 | SUCCESS | SUCCESS | 108.13033 | 0/361 | 18 | 3/3 |
| network::network_correctness_u64_n9 | SUCCESS | SUCCESS | 97.63996 | 0/361 | 21 | 3/3 |
| merge::merge_contract_u64_n5 | SUCCESS | SUCCESS | 142.96727 | 0/442 | 100 | 1/1 |
| merge::general_stable_sorted_permutation_u64_n8 | SUCCESS | SUCCESS | 137.74751 | 0/638 | 97 | 2/2 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 51e80f4c3b7d6cebb3bca102293379490fa375634ef081e2530b683fe7db152f
- `research/challenge-8/kani-k1/tools/kani_k1.py` eb7c3dda5ac14badf87841b2f185690705bc7617e1c45a302eafbd0a7dced1e1
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- 3 harnesses verified concurrently: times and memory are of the shared run, not single-harness measurements
- 82 unreachable check(s) in slice::sort::shared::smallsort::verify::correct::sorted_permutation_general_stable_u8_n14
- 60 unreachable check(s) in slice::sort::shared::smallsort::verify::correct::sorted_permutation_fallback_u64_n8
- 1 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n31
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n32
- 1 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n17
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n16
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n8
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::permutation_merge_u8_n4
- 11 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::sorted_network_prefix_u8_n10
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::advancement_merge_up_u8_n2
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::network_correctness_u64_n7
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::network::network_correctness_u64_n9
- 100 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_contract_u64_n5
- 97 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n8
