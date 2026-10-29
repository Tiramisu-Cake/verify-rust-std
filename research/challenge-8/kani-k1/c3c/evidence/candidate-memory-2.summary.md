# K-1 run `c3c-memory-candidate-2of2`: COMPLETE

- head `eefb512a3fe8e30c31645eb63141f2a5179e39d8`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `125d998e4eac820973d7efd4affda68b66db62b8ff440c807cbf7c8e1dc4146b`
- run 4722df9d-7a70-46d1-b761-deef420bb1f2 attempt None, image Ubuntu 24.04.5 LTS 4 CPU AMD EPYC 7B12, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 5 min, harnesses in parallel 3, uninit checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 5661708 KiB, wall 8:44.83 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 263 samples, largest sampled sum of RSS 6.41 GiB at 427 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-driver` 5.40 GiB (≤13 GiB), seen 2–523 s, peak sample 429 s
  - `kani-compiler` 1.78 GiB (≤13 GiB), seen 2–48 s, peak sample 38 s
  - `cbmc` 1.23 GiB (≤13 GiB), seen 52–523 s, peak sample 385 s
  - `goto-cc` 0.05 GiB (≤13 GiB), seen 50–186 s, peak sample 50 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 52–469 s, peak sample 52 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–48 s, peak sample 2 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–525 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–523 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–523 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–523 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–525 s, peak sample 0 s
  - simultaneous cbmc RSS 2.66 GiB at 96 s
  - simultaneous driver RSS 5.40 GiB at 429 s
  - cbmc PID 10052: 1.23 GiB peak at 385 s; active `T1:correct::sorted_permutation_general_u8_n14`
  - cbmc PID 9863: 1.22 GiB peak at 252 s; active `T1:correct::sorted_permutation_stable_u8_n14`
  - cbmc PID 9472: 1.10 GiB peak at 96 s; active `T0:merge::merge_contract_u64_n5,T1:assembly::safety_stable_unit_n32,T2:network::insert_tail_contract_u64_start1_tail16`
  - cbmc PID 9564: 1.07 GiB peak at 142 s; active `T1:assembly::safety_stable_unit_n31,T2:network::insert_tail_contract_u64_start1_tail8`
  - cbmc PID 10106: 0.97 GiB peak at 481 s; active `T1:merge::general_stable_sorted_permutation_u64_n8`
  - cbmc PID 9435: 0.92 GiB peak at 68 s; active `T0:merge::merge_contract_u64_n5,T1:assembly::safety_stable_unit_n32,T2:network::insert_tail_contract_u64_start1_tail16`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| network::insert_tail_contract_u64_start1_tail8 | SUCCESS | SUCCESS | 19.046303 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail9 | SUCCESS | SUCCESS | 19.914776 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail10 | SUCCESS | SUCCESS | 16.998772 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail11 | SUCCESS | SUCCESS | 24.420643 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail12 | SUCCESS | SUCCESS | 22.62196 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail13 | SUCCESS | SUCCESS | 31.436855 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail14 | SUCCESS | SUCCESS | 36.369545 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail15 | SUCCESS | SUCCESS | 45.161785 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail16 | SUCCESS | SUCCESS | 47.67078 | 0/415 | 36 |  |
| correct::sorted_permutation_general_u8_n14 | SUCCESS | SUCCESS | 112.16317 | 0/723 | 82 |  |
| correct::sorted_permutation_stable_u8_n14 | SUCCESS | SUCCESS | 142.25116 | 0/723 | 82 |  |
| correct::sorted_permutation_fallback_u64_n8 | SUCCESS | SUCCESS | 37.113495 | 0/481 | 60 |  |
| assembly::safety_stable_unit_n31 | SUCCESS | SUCCESS | 44.01439 | 0/280 | 1 | 1/1 |
| assembly::safety_stable_unit_n32 | SUCCESS | SUCCESS | 43.670624 | 0/273 | 5 | 1/1 |
| assembly::safety_stable_unit_n17 | SUCCESS | SUCCESS | 11.882472 | 0/280 | 1 | 1/1 |
| assembly::safety_stable_unit_n16 | SUCCESS | SUCCESS | 4.675986 | 0/272 | 5 | 1/1 |
| assembly::safety_stable_unit_n8 | SUCCESS | SUCCESS | 2.4828973 | 0/272 | 6 | 1/1 |
| assembly::permutation_merge_u8_n4 | SUCCESS | SUCCESS | 1.6419815 | 0/149 | 4 | 1/1 |
| assembly::sorted_network_prefix_u8_n10 | SUCCESS | SUCCESS | 4.562046 | 0/179 | 11 | 1/1 |
| assembly::advancement_merge_up_u8_n2 | SUCCESS | SUCCESS | 0.6380137 | 0/61 | 4 | 2/2 |
| network::network_correctness_u64_n7 | SUCCESS | SUCCESS | 58.325016 | 0/361 | 18 |  |
| network::network_correctness_u64_n9 | SUCCESS | SUCCESS | 30.822624 | 0/361 | 21 |  |
| merge::merge_contract_u64_n5 | SUCCESS | SUCCESS | 56.915627 | 0/442 | 100 |  |
| merge::general_stable_sorted_permutation_u64_n8 | SUCCESS | SUCCESS | 54.63317 | 0/638 | 97 |  |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 51e80f4c3b7d6cebb3bca102293379490fa375634ef081e2530b683fe7db152f
- `research/challenge-8/kani-k1/tools/kani_k1.py` eb7c3dda5ac14badf87841b2f185690705bc7617e1c45a302eafbd0a7dced1e1
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- 3 harnesses verified concurrently: times and memory are of the shared run, not single-harness measurements
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail8
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail9
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail10
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail11
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail12
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail13
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail14
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail15
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail16
- 82 unreachable check(s) in slice::sort::shared::smallsort::verify::correct::sorted_permutation_general_u8_n14
- 82 unreachable check(s) in slice::sort::shared::smallsort::verify::correct::sorted_permutation_stable_u8_n14
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
