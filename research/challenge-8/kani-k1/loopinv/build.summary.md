# K-1 run `loopinv-e2-diag-outer-loop-20261103`: COMPLETE

- head `b64d6f6a8657156ad4c480929a3245c56bc68b0b`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `0f084bc65dc00f70ed66ab56eaf9cce49422e0e3522cfd2165a9fa600e719492`
- run c151dc31-7bb8-4cfb-8b63-c685c65192a5 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 15751956 KiB, wall 31:24.78 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 356 samples, largest sampled sum of RSS 14.99 GiB at 1546 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 14.99 GiB (>16 GB), seen 66–1546 s, peak sample 1546 s
  - `kani-compiler` 1.57 GiB (≤13 GiB), seen 2–62 s, peak sample 48 s
  - `goto-instrument` 0.60 GiB (≤13 GiB), seen 64–1281 s, peak sample 1281 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–62 s, peak sample 54 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `kani-driver` 0.01 GiB (≤13 GiB), seen 2–1548 s, peak sample 66 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1884 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1548 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1548 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–1548 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1884 s, peak sample 2 s
  - simultaneous cbmc RSS 14.99 GiB at 1546 s
  - simultaneous driver RSS 0.01 GiB at 66 s
  - cbmc PID 9307: 14.99 GiB peak at 1546 s; active `T0:network::loopinv::loopinv_insertion_u64_n2_offset1`
  - cbmc PID 9233: 14.91 GiB peak at 242 s; active `T0:network::loopinv::loopinv_copy_false_control`
  - cbmc PID 9269: 14.81 GiB peak at 861 s; active `T0:network::loopinv::loopinv_copy_true`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| network::loopinv::loopinv_insertion_u64_n2_offset1 | SUCCESS | TIMEOUT | None |  | None |  |
| network::loopinv::loopinv_copy_true | SUCCESS | TIMEOUT | None |  | None |  |
| network::loopinv::loopinv_copy_false_control | FAILED | TIMEOUT | None |  | None |  |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 15751956 KiB exceeds the largest sampled command peak 15716288 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
