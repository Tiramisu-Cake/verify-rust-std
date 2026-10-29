# K-1 run `c3b-priority-repair-1`: COMPLETE

- head `b30c50d03c9d0fd8dc8f442742e8ee2754fc1a21`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `346be33ea1f2be93b9484695d3abdd1490c8c0772648a7cbbcdfd939d2cc1497`
- run 031fa8c0-d86b-49e9-a19e-67b4cd420725 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 2 min, harnesses in parallel 1, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 3156524 KiB, wall 22:47.38 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 683 samples, largest sampled sum of RSS 4.93 GiB at 1110 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `cbmc` 3.01 GiB (≤13 GiB), seen 72–1365 s, peak sample 1112 s
  - `kani-driver` 2.53 GiB (≤13 GiB), seen 0–1365 s, peak sample 1034 s
  - `kani-compiler` 1.81 GiB (≤13 GiB), seen 2–62 s, peak sample 50 s
  - `kissat` 0.50 GiB (≤13 GiB), seen 98–1361 s, peak sample 1245 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 70–1217 s, peak sample 70 s
  - `goto-cc` 0.04 GiB (≤13 GiB), seen 64–312 s, peak sample 66 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 0–62 s, peak sample 2 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1367 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 0–1365 s, peak sample 0 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 312–312 s, peak sample 312 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1367 s, peak sample 0 s
  - `time` 0.00 GiB (≤13 GiB), seen 0–1365 s, peak sample 0 s
  - …only the 12 largest commands listed

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| correct::sorted_permutation_general_u8_n14 | SUCCESS | TIMEOUT | None |  | None |  |
| correct::sorted_permutation_general_u8_n15 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_sorted_permutation_u64_n11 | SUCCESS | SUCCESS | 105.34339 | 0/638 | 91 |  |
| merge::general_sorted_permutation_u64_n12 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_sorted_permutation_u64_n16 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_sorted_permutation_u8_n12 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_sorted_permutation_u8_n13 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_sorted_permutation_u8_n16 | SUCCESS | SUCCESS | 124.20711 | 0/631 | 76 |  |
| merge::merge_contract_u64_n16 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insert_tail_contract_u64_start1_tail16 | SUCCESS | SUCCESS | 53.698334 | 0/415 | 36 |  |
| network::network_correctness_u64_n14 | SUCCESS | TIMEOUT | None |  | None |  |
| network::dispatch_safety_stable_bytes17_n17 | SUCCESS | SUCCESS | 28.309837 | 0/384 | 10 |  |

Tooling SHA-256 at the run commit:
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 513850c0e01369cb2b27eba83704fd85e93737e20b49080d9cb7c2ff07b8b78b
- `research/challenge-8/kani-k1/tools/kani_k1.py` e732269a43cd6f15f68df13d1e28fb8ab593a7e135094113eec2c33522515ed0
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- 91 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_sorted_permutation_u64_n11
- 76 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_sorted_permutation_u8_n16
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail16
- 10 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_bytes17_n17
