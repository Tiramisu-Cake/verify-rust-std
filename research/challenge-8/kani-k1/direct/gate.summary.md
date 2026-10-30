# K-1 run `direct-b-gate`: COMPLETE

- head `5265f374dd0b4b7363a327cca98299f06bb83e9f`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `83a3da3f0dc0a88f776e7ec5045a2490ea98a9840028bbcc1a97ebc9f9427ec6`
- run f00d0543-ba0b-4e4c-9622-59531f85cba3 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: False; Kani exit 1
- whole run, including compilation: max RSS 9454264 KiB, wall 24:55.86 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 747 samples, largest sampled sum of RSS 9.18 GiB at 367 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 9.02 GiB (≤13 GiB), seen 74–1494 s, peak sample 403 s
  - `kani-compiler` 1.73 GiB (≤13 GiB), seen 2–66 s, peak sample 52 s
  - `kani-driver` 0.31 GiB (≤13 GiB), seen 2–1494 s, peak sample 248 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 72–1468 s, peak sample 72 s
  - `goto-cc` 0.04 GiB (≤13 GiB), seen 68–1466 s, peak sample 70 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 2 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1495 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1494 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1494 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1495 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–1494 s, peak sample 2 s
  - simultaneous cbmc RSS 8.94 GiB at 367 s
  - simultaneous driver RSS 0.29 GiB at 1494 s
  - cbmc PID 9374: 9.02 GiB peak at 403 s; active `T0:merge::general_stable_direct_u64_n8`
  - cbmc PID 9347: 3.92 GiB peak at 234 s; active `T0:merge::general_stable_direct_u64_n4`
  - cbmc PID 9293: 1.69 GiB peak at 112 s; active `T0:merge::general_stable_direct_u64_n3`
  - cbmc PID 9266: 1.20 GiB peak at 86 s; active `T0:merge::general_stable_direct_value_corruption_control_u64_n2`
  - cbmc PID 9320: 1.16 GiB peak at 140 s; active `T0:merge::general_stable_direct_u64_n2`
  - cbmc PID 9455: 0.60 GiB peak at 876 s; active `T0:merge::general_stable_direct_u8_n9`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::general_stable_direct_u64_n2 | SUCCESS | SUCCESS | 21.03172 | 0/407 | 70 | 2/2 |
| merge::general_stable_direct_u64_n3 | SUCCESS | SUCCESS | 31.137829 | 0/407 | 69 | 2/2 |
| merge::general_stable_direct_u64_n4 | SUCCESS | SUCCESS | 99.82221 | 0/407 | 68 | 2/2 |
| merge::general_stable_direct_u8_n2 | SUCCESS | SUCCESS | 4.3761625 | 0/400 | 72 | 2/2 |
| merge::general_stable_direct_u8_n3 | SUCCESS | SUCCESS | 7.2661877 | 0/400 | 71 | 2/2 |
| merge::general_stable_direct_u8_n4 | SUCCESS | SUCCESS | 26.389982 | 0/400 | 70 | 2/2 |
| merge::general_stable_direct_u64_n8 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_stable_direct_u8_n9 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_stable_direct_value_corruption_control_u64_n2 | FAILED | FAILED | 19.0811 | 1/409 | 69 |  |

Failed checks of `slice::sort::shared::smallsort::verify::merge::general_stable_direct_value_corruption_control_u64_n2`:
- This is a placeholder message; Kani doesn't support message formatted at runtime @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:846

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 70 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u64_n2
- 69 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u64_n3
- 68 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u64_n4
- 72 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u8_n2
- 71 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u8_n3
- 70 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u8_n4
- 69 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_value_corruption_control_u64_n2
