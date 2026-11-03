# K-1 run `typematrix-meas-dispatch-u8u32-u128-bytes9-20261103`: COMPLETE

- head `6a14da38b8a2772474c8b6d0bd59c33356284433`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `b122e59d9848a77fdb78b33ad5336cd57d912782204a0dbb47697a6c8f3d0b5d`
- run 5b4d8db6-bb4e-4d78-b344-a8a0e8389c81 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
- whole run, including compilation: max RSS 7148656 KiB, wall 39:19.14 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 1178 samples, largest sampled sum of RSS 8.33 GiB at 876 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 6.82 GiB (≤13 GiB), seen 72–2358 s, peak sample 878 s
  - `kani-driver` 2.39 GiB (≤13 GiB), seen 2–2358 s, peak sample 601 s
  - `kani-compiler` 1.77 GiB (≤13 GiB), seen 2–66 s, peak sample 50 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 70–2278 s, peak sample 1347 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 66 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `goto-cc` 0.02 GiB (≤13 GiB), seen 68–1143 s, peak sample 1143 s
  - `cc1plus` 0.01 GiB (≤13 GiB), seen 1423–1423 s, peak sample 1423 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–2359 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–2358 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 68–1423 s, peak sample 1423 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–2359 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 6.78 GiB at 876 s
  - simultaneous driver RSS 2.25 GiB at 599 s
  - cbmc PID 9306: 6.82 GiB peak at 878 s; active `T0:network::typematrix::dispatch_safety_stable_unstable_bytes9_n31_32`
  - cbmc PID 9277: 6.56 GiB peak at 399 s; active `T0:network::typematrix::dispatch_safety_stable_unstable_u8u32_n31_32`
  - cbmc PID 9509: 6.46 GiB peak at 2103 s; active `T0:network::typematrix::dispatch_safety_stable_unstable_u128_n31_32`
  - cbmc PID 9451: 3.39 GiB peak at 1708 s; active `T0:network::typematrix::dispatch_safety_stable_unstable_bytes9_n15_16_17`
  - cbmc PID 9335: 3.34 GiB peak at 1285 s; active `T0:network::typematrix::dispatch_safety_stable_unstable_u8u32_n15_16_17`
  - cbmc PID 9422: 3.18 GiB peak at 1516 s; active `T0:network::typematrix::dispatch_safety_stable_unstable_u128_n15_16_17`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| network::typematrix::dispatch_safety_stable_unstable_u8u32_n0_1_2_7_8 | SUCCESS | SUCCESS | 26.4046 | 0/390 | 8 | 11/11 |
| network::typematrix::dispatch_safety_stable_unstable_u8u32_n15_16_17 | SUCCESS | SUCCESS | 202.66759 | 0/380 | 7 | 7/7 |
| network::typematrix::dispatch_safety_stable_unstable_u8u32_n31_32 | SUCCESS | SUCCESS | 538.2921 | 0/375 | 6 | 5/5 |
| network::typematrix::dispatch_safety_stable_unstable_u128_n0_1_2_7_8 | SUCCESS | SUCCESS | 32.567104 | 0/390 | 9 | 11/11 |
| network::typematrix::dispatch_safety_stable_unstable_u128_n15_16_17 | SUCCESS | SUCCESS | 176.3751 | 0/380 | 8 | 7/7 |
| network::typematrix::dispatch_safety_stable_unstable_u128_n31_32 | SUCCESS | SUCCESS | 452.50607 | 0/375 | 8 | 5/5 |
| network::typematrix::dispatch_safety_stable_unstable_bytes9_n0_1_2_7_8 | SUCCESS | SUCCESS | 46.786545 | 0/390 | 9 | 11/11 |
| network::typematrix::dispatch_safety_stable_unstable_bytes9_n15_16_17 | SUCCESS | SUCCESS | 187.17416 | 0/380 | 8 | 7/7 |
| network::typematrix::dispatch_safety_stable_unstable_bytes9_n31_32 | SUCCESS | SUCCESS | 532.78033 | 0/375 | 8 | 5/5 |
| network::typematrix::dispatch_safety_unstable_u8u32_n9_12_13_18 | SUCCESS | SUCCESS | 80.36163 | 0/377 | 12 | 5/5 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_unstable_u8u32_n0_1_2_7_8
- 7 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_unstable_u8u32_n15_16_17
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_unstable_u8u32_n31_32
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_unstable_u128_n0_1_2_7_8
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_unstable_u128_n15_16_17
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_unstable_u128_n31_32
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_unstable_bytes9_n0_1_2_7_8
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_unstable_bytes9_n15_16_17
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_unstable_bytes9_n31_32
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_unstable_u8u32_n9_12_13_18
