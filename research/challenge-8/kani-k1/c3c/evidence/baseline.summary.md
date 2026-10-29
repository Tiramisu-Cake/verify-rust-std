# K-1 run `c3c-matched-baseline`: INCONSISTENT

- head `7b6bf1ede05d5a8369fdc0dc455b340c79a7ef03`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `85ba738f15f0d6df6ca932950ab3730894d147c38074b05c91a7ff5688fa7e0f`
- run ba81d888-90db-49c7-a04d-d6dbb9108fac attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 3, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 4125308 KiB, wall 16:27.83 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 494 samples, largest sampled sum of RSS 9.36 GiB at 620 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 3.93 GiB (≤13 GiB), seen 66–987 s, peak sample 674 s
  - `kani-compiler` 2.01 GiB (≤13 GiB), seen 2–62 s, peak sample 50 s
  - `kani-driver` 1.82 GiB (≤13 GiB), seen 2–987 s, peak sample 317 s
  - `goto-cc` 0.07 GiB (≤13 GiB), seen 64–499 s, peak sample 64 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 66–806 s, peak sample 501 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–62 s, peak sample 2 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–988 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–987 s, peak sample 2 s
  - `rust-lld` 0.00 GiB (≤13 GiB), seen 6–6 s, peak sample 6 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–987 s, peak sample 2 s
  - `collect2` 0.00 GiB (≤13 GiB), seen 6–6 s, peak sample 6 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 7.90 GiB at 620 s
  - simultaneous driver RSS 1.73 GiB at 315 s
  - cbmc PID 9827: 3.93 GiB peak at 674 s; active `T0:network::network_correctness_u64_n13,T1:network::insert_tail_contract_u64_start1,T2:merge::route_safety_all_routes_n31`
  - cbmc PID 9800: 3.67 GiB peak at 620 s; active `T0:network::network_correctness_u64_n13,T1:merge::route_safety_all_routes_n32,T2:merge::route_safety_all_routes_n31`
  - cbmc PID 9894: 2.85 GiB peak at 666 s; active `T0:network::network_correctness_u8_n16,T1:network::insert_tail_contract_u64_start1,T2:network::network_correctness_u64_n8`
  - cbmc PID 9643: 2.77 GiB peak at 208 s; active `T0:network::insert_tail_contract_u64_start6,T1:merge::merge_contract_u64_n16,T2:merge::merge_contract_u64_n15`
  - cbmc PID 9681: 2.45 GiB peak at 423 s; active `T0:network::insertion_permutation_u64_n12,T1:merge::merge_contract_u64_n16,T2:merge::merge_contract_u64_n15`
  - cbmc PID 9746: 2.26 GiB peak at 497 s; active `T0:network::insertion_permutation_u64_n12,T1:merge::route_safety_all_routes_n32,T2:merge::merge_contract_u64_n15`
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
| correct::sorted_permutation_general_stable_u8_n14 | SUCCESS | TIMEOUT | None |  | None |  |
| correct::sorted_permutation_fallback_u64_n8 | SUCCESS | SUCCESS | 52.64956 | 0/481 | 60 | 1/1 |
| assembly::safety_stable_unit_n31 | SUCCESS | SUCCESS | 43.655643 | 0/280 | 1 | 1/1 |
| assembly::safety_stable_unit_n32 | SUCCESS | SUCCESS | 50.006714 | 0/273 | 5 | 1/1 |
| assembly::safety_stable_unit_n17 | SUCCESS | SUCCESS | 12.122487 | 0/280 | 1 | 1/1 |
| assembly::safety_stable_unit_n16 | SUCCESS | SUCCESS | 4.618697 | 0/272 | 5 | 1/1 |
| assembly::safety_stable_unit_n8 | SUCCESS | SUCCESS | 2.1411476 | 0/272 | 6 | 1/1 |
| assembly::permutation_merge_u8_n4 | SUCCESS | SUCCESS | 2.333273 | 0/149 | 4 | 1/1 |
| assembly::sorted_network_prefix_u8_n10 | SUCCESS | SUCCESS | 7.047707 | 0/179 | 11 | 1/1 |
| assembly::advancement_merge_up_u8_n2 | SUCCESS | SUCCESS | 1.4394697 | 0/61 | 4 | 2/2 |

Inconsistencies:
- 10 harness block(s) started on a worker before its previous block ended under kani_jobs > 1: output may be interleaved

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` c54242159e8beaeec6ffb1d4926e7de62e7b6d5ed23a5a21fbe5c872aa2d59dc
- `research/challenge-8/kani-k1/tools/kani_k1.py` c6236af71fdc13073d63873aafc069de2bbf4b71e50659168632e0a12b6f47d0
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- 3 harnesses verified concurrently: times and memory are of the shared run, not single-harness measurements
- 60 unreachable check(s) in slice::sort::shared::smallsort::verify::correct::sorted_permutation_fallback_u64_n8
- 1 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n31
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n32
- 1 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n17
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n16
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n8
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::permutation_merge_u8_n4
- 11 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::sorted_network_prefix_u8_n10
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::advancement_merge_up_u8_n2
