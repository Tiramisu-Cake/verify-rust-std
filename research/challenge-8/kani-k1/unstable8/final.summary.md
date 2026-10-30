# K-1 run `unstable8-final-20261030`: COMPLETE

- head `b177a4bd5d46ae30edf1d75379ff7c43a7f19720`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `13e673f339fef7f5908421701e55f4f1e61df2a539513bcf7919a870d1741022`
- run 2fbe4ddc-a6c0-4cd9-8056-12c7c828b7f8 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: False; Kani exit 1
- whole run, including compilation: max RSS 1722424 KiB, wall 18:16.09 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 548 samples, largest sampled sum of RSS 1.82 GiB at 48 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.64 GiB (≤13 GiB), seen 2–62 s, peak sample 48 s
  - `cbmc` 0.50 GiB (≤13 GiB), seen 66–1095 s, peak sample 505 s
  - `kani-driver` 0.46 GiB (≤13 GiB), seen 2–1095 s, peak sample 495 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–62 s, peak sample 62 s
  - `goto-instrument` 0.03 GiB (≤13 GiB), seen 64–495 s, peak sample 495 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1096 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1095 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1095 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–1095 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1096 s, peak sample 0 s
  - simultaneous cbmc RSS 0.49 GiB at 503 s
  - simultaneous driver RSS 0.44 GiB at 287 s
  - cbmc PID 9278: 0.50 GiB peak at 505 s; active `T0:types::sorted_permutation_traits_general_drop_u8_n9`
  - cbmc PID 9224: 0.19 GiB peak at 70 s; active `T0:types::sorted_permutation_traits_stable_fallback_cell_u8_n8`
  - cbmc PID 9251: 0.18 GiB peak at 295 s; active `T0:types::sorted_permutation_traits_unstable_fallback_cell_u8_n8`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| types::sorted_permutation_traits_stable_fallback_cell_u8_n8 | SUCCESS | SUCCESS | 222.42752 | 0/414 | 4 | 4/4 |
| types::sorted_permutation_traits_unstable_fallback_cell_u8_n8 | SUCCESS | SUCCESS | 206.487 | 0/414 | 4 | 4/4 |
| types::sorted_permutation_traits_general_drop_u8_n9 | SUCCESS | TIMEOUT | None |  | None |  |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::types::sorted_permutation_traits_stable_fallback_cell_u8_n8
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::types::sorted_permutation_traits_unstable_fallback_cell_u8_n8
