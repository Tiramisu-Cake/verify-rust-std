# K-1 run `unstable8-gate-20261030`: COMPLETE

- head `5ff343a759b87c3927f7f3f90981d15f30e9e946`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `62bb6f2abab22983459e9493cea361a0513429968a82d2570da57cb9a0d80560`
- run 64a70b50-30b2-4d26-b25b-7ed1463b4851 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: False; Kani exit 1
- whole run, including compilation: max RSS 1782584 KiB, wall 14:31.36 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 436 samples, largest sampled sum of RSS 1.93 GiB at 52 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.70 GiB (≤13 GiB), seen 2–68 s, peak sample 52 s
  - `kani-driver` 0.80 GiB (≤13 GiB), seen 2–870 s, peak sample 270 s
  - `cbmc` 0.46 GiB (≤13 GiB), seen 72–870 s, peak sample 84 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–68 s, peak sample 4 s
  - `goto-instrument` 0.02 GiB (≤13 GiB), seen 70–270 s, peak sample 270 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–871 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–870 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–870 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–870 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–871 s, peak sample 0 s
  - simultaneous cbmc RSS 0.40 GiB at 82 s
  - simultaneous driver RSS 0.58 GiB at 270 s
  - cbmc PID 9288: 0.46 GiB peak at 84 s; active `T0:types::sorted_permutation_traits_general_drop_u8_n8`
  - cbmc PID 9315: 0.30 GiB peak at 280 s; active `T0:types::sorted_permutation_traits_fallback_cell_u8_n8`
  - cbmc PID 9232: 0.07 GiB peak at 72 s; active ``
  - cbmc PID 9261: 0.04 GiB peak at 74 s; active `T0:types::reject_logical_permutation_drop_n2`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| types::sorted_permutation_traits_general_drop_u8_n8 | SUCCESS | SUCCESS | 194.44167 | 0/580 | 6 | 5/5 |
| types::sorted_permutation_traits_fallback_cell_u8_n8 | SUCCESS | TIMEOUT | None |  | None |  |
| types::reject_logical_permutation_drop_n2 | FAILED | FAILED | 1.9809694 | 1/390 | 8 | 0/1 |
| types::reject_logical_sortedness_cell_n2 | FAILED | FAILED | 0.561533 | 1/227 | 5 | 0/1 |

Failed checks of `slice::sort::shared::smallsort::verify::types::reject_logical_permutation_drop_n2`:
- assertion failed: count(input, probe) == count(output, probe) @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/types.rs:58

Failed checks of `slice::sort::shared::smallsort::verify::types::reject_logical_sortedness_cell_n2`:
- assertion failed: output[i - 1] <= output[i] @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/types.rs:56

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 1782584 KiB exceeds the largest sampled command peak 1782088 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::types::sorted_permutation_traits_general_drop_u8_n8
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::types::reject_logical_permutation_drop_n2
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::types::reject_logical_sortedness_cell_n2
