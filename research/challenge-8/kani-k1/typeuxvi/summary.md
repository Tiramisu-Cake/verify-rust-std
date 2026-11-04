# K-1 run `typeuxvi-meas-dispatch-u16-20261104`: COMPLETE

- head `edd7e20803f592b881f2300ab9a54e2ca2229b3f`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `8d2d6de9e47438e7940539171ea16a2d87d3ffe6bb172122df572b306ab9da9a`
- run 79fa3fcd-d5ba-453b-ad9f-1585453f80b4 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
- whole run, including compilation: max RSS 3301616 KiB, wall 9:40.10 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 291 samples, largest sampled sum of RSS 3.36 GiB at 206 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 3.15 GiB (≤13 GiB), seen 64–579 s, peak sample 164 s
  - `kani-compiler` 1.74 GiB (≤13 GiB), seen 2–58 s, peak sample 46 s
  - `kani-driver` 1.57 GiB (≤13 GiB), seen 2–579 s, peak sample 579 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 62–501 s, peak sample 210 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–58 s, peak sample 50 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 60–60 s, peak sample 60 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–580 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–579 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–579 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–579 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–580 s, peak sample 0 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 3.15 GiB at 164 s
  - simultaneous driver RSS 1.57 GiB at 579 s
  - cbmc PID 9257: 3.15 GiB peak at 164 s; active `T0:network::typematrix::dispatch_safety_stable_unstable_u16_n15_16_17`
  - cbmc PID 9315: 1.50 GiB peak at 274 s; active `T0:network::typematrix::dispatch_safety_unstable_u16_n9_12_13_18`
  - cbmc PID 9344: 1.34 GiB peak at 348 s; active `T0:network::typematrix::dispatch_safety_unstable_u16_n32`
  - cbmc PID 9431: 1.31 GiB peak at 549 s; active `T0:network::typematrix::dispatch_safety_unstable_u16_n31`
  - cbmc PID 9402: 1.25 GiB peak at 479 s; active `T0:network::typematrix::dispatch_safety_stable_u16_n32`
  - cbmc PID 9373: 1.20 GiB peak at 416 s; active `T0:network::typematrix::dispatch_safety_stable_u16_n31`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| network::typematrix::dispatch_safety_stable_unstable_u16_n0_1_2_7_8 | SUCCESS | SUCCESS | 19.711946 | 0/390 | 8 | 11/11 |
| network::typematrix::dispatch_safety_stable_unstable_u16_n15_16_17 | SUCCESS | SUCCESS | 147.63992 | 0/380 | 7 | 7/7 |
| network::typematrix::dispatch_safety_unstable_u16_n9_12_13_18 | SUCCESS | SUCCESS | 62.3632 | 0/377 | 12 | 5/5 |
| network::typematrix::dispatch_safety_stable_u16_n31 | SUCCESS | SUCCESS | 57.45501 | 0/368 | 9 | 2/2 |
| network::typematrix::dispatch_safety_stable_u16_n32 | SUCCESS | SUCCESS | 60.66503 | 0/368 | 9 | 2/2 |
| network::typematrix::dispatch_safety_unstable_u16_n31 | SUCCESS | SUCCESS | 78.72693 | 0/368 | 12 | 2/2 |
| network::typematrix::dispatch_safety_unstable_u16_n32 | SUCCESS | SUCCESS | 84.97608 | 0/368 | 12 | 2/2 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_unstable_u16_n0_1_2_7_8
- 7 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_unstable_u16_n15_16_17
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_unstable_u16_n9_12_13_18
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_u16_n31
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_u16_n32
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_unstable_u16_n31
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_unstable_u16_n32
