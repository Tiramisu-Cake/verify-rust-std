# K-1 run `c3c-matched-candidate-retry1`: INCONSISTENT

- head `66a7ad1fae733121cde66cc6dcf2e0ebf8b2122f`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `59f3d9b919ce9f7941fa8efdc8efe5bd0225ac20b7f15ed0769c322f7ebae56a`
- run fa7d2d00-8470-40e3-be55-c96f0eaa76dc attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 3, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 5263720 KiB, wall 19:39.31 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 589 samples, largest sampled sum of RSS 8.09 GiB at 523 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-driver` 5.02 GiB (≤13 GiB), seen 2–1178 s, peak sample 533 s
  - `cbmc` 2.46 GiB (≤13 GiB), seen 74–1178 s, peak sample 253 s
  - `kani-compiler` 1.98 GiB (≤13 GiB), seen 2–64 s, peak sample 54 s
  - `goto-instrument` 0.08 GiB (≤13 GiB), seen 72–995 s, peak sample 443 s
  - `goto-cc` 0.05 GiB (≤13 GiB), seen 66–997 s, peak sample 543 s
  - `rust-lld` 0.04 GiB (≤13 GiB), seen 2–2 s, peak sample 2 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–64 s, peak sample 2 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 263–263 s, peak sample 263 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1179 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1178 s, peak sample 2 s
  - `cc` 0.00 GiB (≤13 GiB), seen 2–2 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 4.12 GiB at 180 s
  - simultaneous driver RSS 5.02 GiB at 533 s
  - cbmc PID 9633: 2.46 GiB peak at 253 s; active `T0:correct::sorted_permutation_general_u8_n14,T1:network::insert_tail_contract_u64_start1_tail9,T2:merge::merge_contract_u64_n16`
  - cbmc PID 10047: 2.24 GiB peak at 435 s; active `T0:correct::sorted_permutation_stable_u8_n14,T2:merge::merge_contract_u64_n15`
  - cbmc PID 10669: 2.16 GiB peak at 778 s; active `T0:merge::merge_contract_u64_n14,T1:network::insertion_permutation_u64_n12,T2:merge::route_safety_stable_u64_n32`
  - cbmc PID 10387: 1.32 GiB peak at 503 s; active `T0:correct::sorted_permutation_fallback_u64_n8,T1:network::insert_tail_contract_u64_start1_tail12,T2:merge::route_safety_noncopy_u64_n32`
  - cbmc PID 11186: 1.31 GiB peak at 1101 s; active `T0:network::network_correctness_u8_n17,T1:network::network_correctness_u64_n13,T2:network::network_correctness_u64_n8`
  - cbmc PID 10517: 1.29 GiB peak at 604 s; active `T0:merge::merge_contract_u64_n14,T2:merge::route_safety_noncopy_u64_n31`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::merge_contract_u64_n14 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u8_n17 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n15 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::route_safety_general_u64_n31 | SUCCESS | SUCCESS | 97.77425 | 0/280 | 5 |  |
| merge::route_safety_noncopy_u64_n31 | SUCCESS | SUCCESS | 87.66127 | 0/527 | 9 |  |
| merge::route_safety_stable_u64_n31 | SUCCESS | SUCCESS | 80.26621 | 0/278 | 5 |  |
| merge::route_safety_general_u64_n32 | SUCCESS | SUCCESS | 65.54604 | 0/280 | 5 |  |
| merge::route_safety_noncopy_u64_n32 | SUCCESS | SUCCESS | 98.430695 | 0/527 | 9 |  |
| merge::route_safety_stable_u64_n32 | SUCCESS | SUCCESS | 89.98477 | 0/278 | 5 |  |
| network::insert_tail_contract_u64_start6_tail7 | SUCCESS | SUCCESS | 8.822884 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail8 | SUCCESS | SUCCESS | 11.926526 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail9 | SUCCESS | SUCCESS | 13.811169 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail10 | SUCCESS | SUCCESS | 14.320616 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail11 | SUCCESS | SUCCESS | 20.519001 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail12 | SUCCESS | SUCCESS | 22.50792 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail13 | SUCCESS | SUCCESS | 21.26445 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail14 | SUCCESS | SUCCESS | 20.307783 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail15 | SUCCESS | SUCCESS | 30.924984 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail16 | SUCCESS | SUCCESS | 33.86554 | 0/415 | 36 |  |
| network::network_correctness_u8_n16 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u64_n8 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u64_n13 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n16 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insertion_permutation_u64_n12 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insert_tail_contract_u64_start1_tail2 | SUCCESS | SUCCESS | 10.989818 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail3 | SUCCESS | SUCCESS | 8.37065 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail4 | SUCCESS | SUCCESS | 15.431039 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail5 | SUCCESS | SUCCESS | 11.343843 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail6 | SUCCESS | SUCCESS | 14.445677 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail7 | SUCCESS | SUCCESS | 15.674913 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail8 | SUCCESS | SUCCESS | 24.809826 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail9 | SUCCESS | SUCCESS | 41.088985 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail10 | SUCCESS | SUCCESS | 32.437077 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail11 | SUCCESS | SUCCESS | 38.493557 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail12 | SUCCESS | SUCCESS | 31.003319 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail13 | SUCCESS | SUCCESS | 40.716125 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail14 | SUCCESS | SUCCESS | 60.109516 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail15 | SUCCESS | SUCCESS | 58.873955 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail16 | SUCCESS | SUCCESS | 65.039536 | 0/415 | 36 |  |
| correct::sorted_permutation_general_u8_n14 | SUCCESS | SUCCESS | 176.50821 | 0/723 | 82 |  |
| correct::sorted_permutation_stable_u8_n14 | SUCCESS | SUCCESS | 153.7859 | 0/723 | 82 |  |
| correct::sorted_permutation_fallback_u64_n8 | SUCCESS | SUCCESS | 58.47473 | 0/481 | 60 |  |
| assembly::safety_stable_unit_n31 | SUCCESS | SUCCESS | 56.66656 | 0/280 | 1 | 1/1 |
| assembly::safety_stable_unit_n32 | SUCCESS | SUCCESS | 36.039997 | 0/273 | 5 | 1/1 |
| assembly::safety_stable_unit_n17 | SUCCESS | SUCCESS | 12.196939 | 0/280 | 1 | 1/1 |
| assembly::safety_stable_unit_n16 | SUCCESS | SUCCESS | 4.5938807 | 0/272 | 5 | 1/1 |
| assembly::safety_stable_unit_n8 | SUCCESS | SUCCESS | 2.9362347 | 0/272 | 6 | 1/1 |
| assembly::permutation_merge_u8_n4 | SUCCESS | SUCCESS | 1.6602936 | 0/149 | 4 | 1/1 |
| assembly::sorted_network_prefix_u8_n10 | SUCCESS | SUCCESS | 5.3128037 | 0/179 | 11 | 1/1 |
| assembly::advancement_merge_up_u8_n2 | SUCCESS | SUCCESS | 0.63795656 | 0/61 | 4 | 2/2 |

Inconsistencies:
- 5 harness block(s) started on a worker before its previous block ended under kani_jobs > 1: output may be interleaved

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` c54242159e8beaeec6ffb1d4926e7de62e7b6d5ed23a5a21fbe5c872aa2d59dc
- `research/challenge-8/kani-k1/tools/kani_k1.py` c6236af71fdc13073d63873aafc069de2bbf4b71e50659168632e0a12b6f47d0
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- 3 harnesses verified concurrently: times and memory are of the shared run, not single-harness measurements
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_general_u64_n31
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_noncopy_u64_n31
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_stable_u64_n31
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_general_u64_n32
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_noncopy_u64_n32
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_stable_u64_n32
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail7
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail8
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail9
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail10
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail11
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail12
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail13
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail14
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail15
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail16
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail2
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail3
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail4
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail5
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail6
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail7
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail8
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail9
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail10
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail11
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail12
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail13
- 36 unreachable check(s) in slice::sort::s
…[summary.md truncated at 12000 bytes; summary.json holds the bounded full record]
