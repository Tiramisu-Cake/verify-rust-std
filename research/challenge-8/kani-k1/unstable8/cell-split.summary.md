# K-1 run `unstable8-cell-split-20261030`: COMPLETE

- head `2d2cdfff1fc564b9f7e3e4ab5e6a4d1f74e808cb`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `8872649de662088accb8343100836dbdb91a5878f59fbe7d7e9514c8c82779e7`
- run 93263f1d-d590-454b-a496-a3c2f479b07f attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: False; expectation met: True; measurement ok: False; Kani exit 0
- whole run, including compilation: max RSS 1653588 KiB, wall 10:45.64 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 323 samples, largest sampled sum of RSS 1.80 GiB at 56 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.58 GiB (≤13 GiB), seen 2–74 s, peak sample 56 s
  - `kani-driver` 0.44 GiB (≤13 GiB), seen 2–644 s, peak sample 315 s
  - `cbmc` 0.19 GiB (≤13 GiB), seen 78–644 s, peak sample 323 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–74 s, peak sample 64 s
  - `goto-instrument` 0.03 GiB (≤13 GiB), seen 76–315 s, peak sample 315 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–645 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–644 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–644 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–644 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–645 s, peak sample 0 s
  - simultaneous cbmc RSS 0.18 GiB at 82 s
  - simultaneous driver RSS 0.38 GiB at 644 s
  - cbmc PID 9244: 0.19 GiB peak at 323 s; active `T0:types::sorted_permutation_traits_stable_fallback_cell_u8_n8`
  - cbmc PID 9217: 0.18 GiB peak at 84 s; active `T0:types::sorted_permutation_traits_unstable_fallback_cell_u8_n8`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| types::sorted_permutation_traits_stable_fallback_cell_u8_n8 | SUCCESS | SUCCESS | 330.23926 | 0/414 | 4 | 4/5 |
| types::sorted_permutation_traits_unstable_fallback_cell_u8_n8 | SUCCESS | SUCCESS | 237.26244 | 0/414 | 4 | 4/5 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 1653588 KiB exceeds the largest sampled command peak 1653112 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::types::sorted_permutation_traits_stable_fallback_cell_u8_n8
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::types::sorted_permutation_traits_unstable_fallback_cell_u8_n8
