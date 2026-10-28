# K-1 run `c3b-light60-before`: COMPLETE

- head `19e2db1ba9d3d07d7c36ae4f85d20fa9f0ad1c98`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `2c2bd20f4eeaee82d247b427402c4d8cc201d6c696af105335d56001994747c0`
- run 02bacd6a-52d0-4c9e-ad76-7fe1edb81f4c attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 1 min, harnesses in parallel 1, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 2249408 KiB, wall 39:23.66 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 1180 samples, largest sampled sum of RSS 2.81 GiB at 62 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `kani-compiler` 2.15 GiB (≤13 GiB), seen 2–72 s, peak sample 66 s
  - `cbmc` 1.50 GiB (≤13 GiB), seen 108–2362 s, peak sample 1245 s
  - `kani-driver` 1.20 GiB (≤13 GiB), seen 0–2362 s, peak sample 637 s
  - `goto-instrument` 0.09 GiB (≤13 GiB), seen 170–2348 s, peak sample 1608 s
  - `goto-cc` 0.08 GiB (≤13 GiB), seen 74–2067 s, peak sample 78 s
  - `cargo` 0.04 GiB (≤13 GiB), seen 0–72 s, peak sample 2 s
  - `cc1plus` 0.01 GiB (≤13 GiB), seen 108–1381 s, peak sample 1381 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 1052–1052 s, peak sample 1052 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 0–2362 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–2363 s, peak sample 0 s
  - `time` 0.00 GiB (≤13 GiB), seen 0–2362 s, peak sample 0 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 108–2326 s, peak sample 1052 s
  - …only the 12 largest commands listed

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::general_stable_sorted_permutation_u8_n0 | SUCCESS | SUCCESS | 0.5919301 | 0/631 | 136 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n1 | SUCCESS | SUCCESS | 1.005435 | 0/631 | 130 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n2 | SUCCESS | SUCCESS | 6.437617 | 0/631 | 113 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n3 | SUCCESS | SUCCESS | 8.87728 | 0/631 | 111 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n4 | SUCCESS | SUCCESS | 12.607441 | 0/631 | 109 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n5 | SUCCESS | SUCCESS | 19.662964 | 0/631 | 107 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n6 | SUCCESS | SUCCESS | 25.547316 | 0/631 | 105 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n7 | SUCCESS | SUCCESS | 32.526134 | 0/631 | 103 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n8 | SUCCESS | SUCCESS | 45.675148 | 0/631 | 99 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n9 | SUCCESS | SUCCESS | 54.265476 | 0/631 | 97 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n10 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_stable_sorted_permutation_u64_n0 | SUCCESS | SUCCESS | 0.7758282 | 0/638 | 136 | 2/2 |
| merge::general_stable_sorted_permutation_u64_n1 | SUCCESS | SUCCESS | 1.1261864 | 0/638 | 128 | 2/2 |
| merge::general_stable_sorted_permutation_u64_n2 | SUCCESS | SUCCESS | 14.832575 | 0/638 | 111 | 2/2 |
| merge::general_stable_sorted_permutation_u64_n3 | SUCCESS | SUCCESS | 11.16591 | 0/638 | 109 | 2/2 |
| merge::general_stable_sorted_permutation_u64_n4 | SUCCESS | SUCCESS | 20.750416 | 0/638 | 107 | 2/2 |
| merge::general_stable_sorted_permutation_u64_n5 | SUCCESS | SUCCESS | 27.716154 | 0/638 | 105 | 2/2 |
| merge::general_stable_sorted_permutation_u64_n6 | SUCCESS | SUCCESS | 50.351532 | 0/638 | 103 | 2/2 |
| merge::general_stable_sorted_permutation_u64_n7 | SUCCESS | SUCCESS | 53.06692 | 0/638 | 101 | 2/2 |
| merge::general_stable_sorted_permutation_u64_n8 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_stable_sorted_permutation_u64_n9 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_stable_sorted_permutation_u64_n10 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::route_safety_all_routes_n2 | SUCCESS | SUCCESS | 5.5674095 | 0/637 | 15 | 4/4 |
| merge::route_safety_all_routes_n3 | SUCCESS | SUCCESS | 8.019685 | 0/637 | 15 | 4/4 |
| merge::route_safety_all_routes_n4 | SUCCESS | SUCCESS | 11.296252 | 0/637 | 15 | 4/4 |
| merge::route_safety_all_routes_n5 | SUCCESS | SUCCESS | 14.6763935 | 0/637 | 15 | 4/4 |
| merge::route_safety_all_routes_n6 | SUCCESS | SUCCESS | 17.020596 | 0/637 | 15 | 4/4 |
| merge::route_safety_all_routes_n7 | SUCCESS | SUCCESS | 19.833998 | 0/637 | 15 | 4/4 |
| merge::route_safety_all_routes_n8 | SUCCESS | SUCCESS | 33.26801 | 0/637 | 11 | 4/4 |
| merge::route_safety_all_routes_n9 | SUCCESS | SUCCESS | 33.67864 | 0/637 | 11 | 4/4 |
| merge::route_safety_all_routes_n10 | SUCCESS | SUCCESS | 41.035515 | 0/637 | 11 | 4/4 |
| network::network_correctness_u8_n5 | SUCCESS | SUCCESS | 3.2974148 | 0/361 | 18 | 3/3 |
| network::network_correctness_u8_n6 | SUCCESS | SUCCESS | 9.475988 | 0/361 | 18 | 3/3 |
| network::network_correctness_u8_n7 | SUCCESS | SUCCESS | 48.903805 | 0/361 | 18 | 3/3 |
| network::network_correctness_u8_n8 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u8_n9 | SUCCESS | SUCCESS | 20.084612 | 0/361 | 21 | 3/3 |
| network::network_correctness_u8_n10 | SUCCESS | SUCCESS | 31.794748 | 0/361 | 21 | 3/3 |
| network::network_correctness_u64_n5 | SUCCESS | SUCCESS | 9.578666 | 0/361 | 18 | 3/3 |
| network::network_correctness_u64_n6 | SUCCESS | SUCCESS | 40.00333 | 0/361 | 18 | 3/3 |
| network::network_correctness_u64_n7 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u64_n8 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u64_n9 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u64_n10 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u8_n5 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u8_n6 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u8_n7 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u8_n8 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u8_n9 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u8_n10 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n5 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n6 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n7 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n8 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n9 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n10 | SUCCESS | TIMEOUT | None |  | None |  |
| network::swap_contract_four_positions_u8 | SUCCESS | SUCCESS | 13.225633 | 0/347 | 5 | 5/5 |
| network::swap_contract_four_positions_u64 | SUCCESS | SUCCESS | 19.836906 | 0/347 | 5 | 5/5 |
| network::swap_contract_u8_n2 | SUCCESS | SUCCESS | 18.453575 | 0/404 | 5 | 5/5 |
| network::swap_contract_u64_n2 | SUCCESS | SUCCESS | 21.017473 | 0/404 | 5 | 5/5 |
| assembly::sorted_permutation_swap_u8_n2 | SUCCESS | SUCCESS | 0.43579283 | 0/84 | 4 | 1/1 |

Tooling SHA-256 at the run commit:
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` fb8663df29332899c81c1865583facc5394e6941c484027d896e2cadc0beda04
- `research/challenge-8/kani-k1/tools/kani_k1.py` 1ac896f51b7d1ed1c07a29e8010ffea29ea1c74f2b6e0ece2de10123e1ebf2ef
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- 136 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n0
- 130 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n1
- 113 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n2
- 111 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n3
- 109 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n4
- 107 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n5
- 105 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n6
- 103 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n7
- 99 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n8
- 97 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n9
- 136 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n0
- 128 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n1
- 111 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n2
- 109 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n3
- 107 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n4
- 105 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n5
- 103 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n6
- 101 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n7
- 15 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_all_routes_n2
- 15 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_all_routes_n3
- 15 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_all_routes_n4
- 15 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_all_routes_n5
- 15 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_all_routes_n6
- 15 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_all_routes_n7
- 11 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_all_routes_n8
- 11 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_all_routes_n9
- 11 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_all_routes_n10
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::network_correctness_u8_n5
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::network_correctness_u8_n6
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::network_correctness_u8_n7
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::network::network_correctness_u8_n9
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::network::network_correctness_u8_n10
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::network_correctness_u64_n5
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::network_correctness_u64_n6
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::network::swap_contract_four_positions_u8
- 5 unreachable check(s) in slice::sort::shared::smallsort
…[summary.md truncated at 12000 bytes; summary.json holds the bounded full record]
