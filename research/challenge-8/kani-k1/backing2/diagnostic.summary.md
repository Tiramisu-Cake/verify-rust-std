# K-1 run `backing2-diagnostic-20261031`: COMPLETE

- head `e2e3fec798e6c5dfb2afbf992a08f8ca0959876f`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `e817ba1dff4e6afea1296c15fe956120bc76a95b8936581bdebdd33e694deec8`
- run 86b9e456-a7c0-4b43-93bd-ace1816100d0 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 3, uninit checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 1812320 KiB, wall 8:22.72 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 252 samples, largest sampled sum of RSS 3.66 GiB at 285 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.73 GiB (≤13 GiB), seen 2–64 s, peak sample 50 s
  - `kani-driver` 1.58 GiB (≤13 GiB), seen 2–502 s, peak sample 502 s
  - `cbmc` 1.51 GiB (≤13 GiB), seen 70–500 s, peak sample 291 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 68–273 s, peak sample 273 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–64 s, peak sample 56 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `goto-cc` 0.01 GiB (≤13 GiB), seen 66–271 s, peak sample 271 s
  - `cc1plus` 0.01 GiB (≤13 GiB), seen 66–66 s, peak sample 66 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–502 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–502 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–502 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 66–66 s, peak sample 66 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 3.15 GiB at 98 s
  - simultaneous driver RSS 1.58 GiB at 502 s
  - cbmc PID 9385: 1.51 GiB peak at 291 s; active `T1:merge::opt_split::general_direct_u64_n8`
  - cbmc PID 9304: 1.51 GiB peak at 80 s; active `T0:merge::backing::stable_direct_u64_n8,T1:merge::opt_split::general_direct_u64_n8`
  - cbmc PID 9299: 0.97 GiB peak at 114 s; active `T0:merge::backing::stable_direct_u64_n8,T1:merge::backing::general_direct_u64_n7,T2:merge::backing::stable_direct_u64_n7`
  - cbmc PID 9294: 0.96 GiB peak at 114 s; active `T0:merge::backing::stable_direct_u64_n8,T1:merge::backing::general_direct_u64_n7,T2:merge::backing::stable_direct_u64_n7`
  - cbmc PID 9358: 0.83 GiB peak at 229 s; active `T0:merge::backing::stable_direct_u64_n8,T1:merge::opt_split::general_direct_u64_n6,T2:merge::backing::stable_direct_u64_n6`
  - cbmc PID 9353: 0.75 GiB peak at 253 s; active `T0:merge::backing::stable_direct_u64_n8,T1:merge::opt_split::general_direct_u64_n8,T2:merge::backing::stable_direct_u64_n6`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::opt_split::general_direct_u64_n6 | SUCCESS | SUCCESS | 81.49289 | 0/407 | 66 | 1/1 |
| merge::backing::general_direct_u64_n7 | SUCCESS | SUCCESS | 118.67463 | 0/407 | 65 | 1/1 |
| merge::opt_split::general_direct_u64_n8 | SUCCESS | SUCCESS | 228.36633 | 0/407 | 62 | 1/1 |
| merge::backing::stable_direct_u64_n6 | SUCCESS | SUCCESS | 97.234764 | 0/407 | 66 | 1/1 |
| merge::backing::stable_direct_u64_n7 | SUCCESS | SUCCESS | 118.90441 | 0/407 | 65 | 1/1 |
| merge::backing::stable_direct_u64_n8 | SUCCESS | SUCCESS | 239.84729 | 0/407 | 62 | 1/1 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 1812320 KiB exceeds the largest sampled command peak 1810696 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 3 harnesses verified concurrently: times and memory are of the shared run, not single-harness measurements
- 66 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::general_direct_u64_n6
- 65 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::backing::general_direct_u64_n7
- 62 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::general_direct_u64_n8
- 66 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::backing::stable_direct_u64_n6
- 65 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::backing::stable_direct_u64_n7
- 62 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::backing::stable_direct_u64_n8
