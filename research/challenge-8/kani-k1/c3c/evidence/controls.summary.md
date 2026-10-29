# K-1 run `c3c-controls-cover-audit`: COMPLETE

- head `34c3cf02580266542d2122707bc4d955527d0641`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `1020fcce12cccc0806f5d02aa56c5f96d392e556acd9b366219592f7b57bdaeb`
- run 0b2482ba-6db6-4125-8aa1-2503a7a8ccf4 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 3, uninit checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 6419416 KiB, wall 6:32.83 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 197 samples, largest sampled sum of RSS 6.76 GiB at 213 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-driver` 6.12 GiB (≤13 GiB), seen 2–392 s, peak sample 392 s
  - `kani-compiler` 1.79 GiB (≤13 GiB), seen 2–64 s, peak sample 52 s
  - `cbmc` 1.35 GiB (≤13 GiB), seen 70–386 s, peak sample 96 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 68–263 s, peak sample 215 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 66–324 s, peak sample 66 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–64 s, peak sample 2 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–393 s, peak sample 393 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–392 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–393 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–392 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–392 s, peak sample 2 s
  - simultaneous cbmc RSS 3.25 GiB at 201 s
  - simultaneous driver RSS 6.12 GiB at 392 s
  - cbmc PID 9335: 1.35 GiB peak at 96 s; active `T0:correct::sorted_permutation_general_u8_n14,T1:correct::contract_insert_tail_u8_prefix,T2:network::insert_tail_contract_u64_start1_tail2`
  - cbmc PID 9381: 1.22 GiB peak at 326 s; active `T0:correct::sorted_permutation_general_u8_n14`
  - cbmc PID 9314: 1.21 GiB peak at 140 s; active `T0:correct::sorted_permutation_stable_u8_n14,T1:correct::contract_insert_tail_u8_prefix,T2:merge::merge_contract_u64_n5`
  - cbmc PID 9354: 0.80 GiB peak at 201 s; active `T0:correct::sorted_permutation_general_u8_n14,T1:correct::contract_insert_tail_u8_prefix,T2:merge::merge_contract_u64_n5`
  - cbmc PID 9475: 0.69 GiB peak at 291 s; active `T0:correct::sorted_permutation_general_u8_n14,T1:correct::sorted_permutation_fallback_u64_n8,T2:network::dispatch_safety_stable_bytes16_n15`
  - cbmc PID 9546: 0.56 GiB peak at 324 s; active `T0:correct::sorted_permutation_general_u8_n14,T1:merge::general_stable_sorted_permutation_u64_n2,T2:network::dispatch_safety_stable_bytes16_n15`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| correct::sorted_permutation_fallback_u64_n8 | SUCCESS | SUCCESS | 68.44929 | 0/481 | 60 | 1/1 |
| correct::contract_insert_tail_u8_prefix | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n5 | SUCCESS | SUCCESS | 146.94041 | 0/442 | 100 | 1/1 |
| merge::general_stable_sorted_permutation_u64_n2 | SUCCESS | SUCCESS | 8.338895 | 0/638 | 111 | 2/2 |
| network::swap_contract_u8_n2 | SUCCESS | SUCCESS | 29.244923 | 0/404 | 5 | 5/5 |
| network::insert_tail_contract_u64_start1_tail2 | SUCCESS | SUCCESS | 16.972382 | 0/415 | 36 | 3/3 |
| network::dispatch_safety_stable_bytes16_n15 | SUCCESS | SUCCESS | 37.462524 | 0/384 | 10 | 1/1 |
| network::mutating_route_permutation_cell_n2 | SUCCESS | SUCCESS | 7.562522 | 0/214 | 4 | 7/7 |
| correct::sorted_permutation_general_u8_n14 | SUCCESS | SUCCESS | 175.81065 | 0/723 | 82 | 1/2 |
| correct::sorted_permutation_stable_u8_n14 | SUCCESS | SUCCESS | 144.35138 | 0/723 | 82 | 1/2 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 51e80f4c3b7d6cebb3bca102293379490fa375634ef081e2530b683fe7db152f
- `research/challenge-8/kani-k1/tools/kani_k1.py` eb7c3dda5ac14badf87841b2f185690705bc7617e1c45a302eafbd0a7dced1e1
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 3 harnesses verified concurrently: times and memory are of the shared run, not single-harness measurements
- 60 unreachable check(s) in slice::sort::shared::smallsort::verify::correct::sorted_permutation_fallback_u64_n8
- 100 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_contract_u64_n5
- 111 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n2
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::network::swap_contract_u8_n2
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail2
- 10 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_bytes16_n15
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::network::mutating_route_permutation_cell_n2
- 82 unreachable check(s) in slice::sort::shared::smallsort::verify::correct::sorted_permutation_general_u8_n14
- 82 unreachable check(s) in slice::sort::shared::smallsort::verify::correct::sorted_permutation_stable_u8_n14
