# K-1 run `backing2-measurement-20261031`: COMPLETE

- head `30b8b975c574dd76a6e770c7001e2a85577dc578`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `9635d6b1c94d6ee8d931fdf45f093ddc4bfc8bf21de20d5adb10eb80202cbdd4`
- run 33e2c5fd-27ba-4cdb-89f9-474f51a3ac39 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
- whole run, including compilation: max RSS 1733780 KiB, wall 4:37.02 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 140 samples, largest sampled sum of RSS 1.67 GiB at 48 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.57 GiB (≤13 GiB), seen 2–64 s, peak sample 48 s
  - `cbmc` 0.99 GiB (≤13 GiB), seen 68–274 s, peak sample 222 s
  - `kani-driver` 0.47 GiB (≤13 GiB), seen 2–276 s, peak sample 142 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–64 s, peak sample 64 s
  - `goto-instrument` 0.02 GiB (≤13 GiB), seen 66–186 s, peak sample 186 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–276 s, peak sample 2 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–277 s, peak sample 0 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–276 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–277 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–276 s, peak sample 2 s
  - simultaneous cbmc RSS 0.92 GiB at 210 s
  - simultaneous driver RSS 0.46 GiB at 276 s
  - cbmc PID 9280: 0.99 GiB peak at 222 s; active `T0:merge::backing::general_direct_u64_n7`
  - cbmc PID 9226: 0.96 GiB peak at 96 s; active `T0:merge::backing::stable_direct_u64_n7`
  - cbmc PID 9253: 0.79 GiB peak at 168 s; active `T0:merge::backing::stable_direct_u64_n6`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::backing::general_direct_u64_n7 | SUCCESS | SUCCESS | 89.5783 | 0/407 | 65 | 1/1 |
| merge::backing::stable_direct_u64_n6 | SUCCESS | SUCCESS | 43.331528 | 0/407 | 66 | 1/1 |
| merge::backing::stable_direct_u64_n7 | SUCCESS | SUCCESS | 74.84438 | 0/407 | 65 | 1/1 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 1733780 KiB exceeds the largest sampled command peak 1642516 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 65 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::backing::general_direct_u64_n7
- 66 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::backing::stable_direct_u64_n6
- 65 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::backing::stable_direct_u64_n7
