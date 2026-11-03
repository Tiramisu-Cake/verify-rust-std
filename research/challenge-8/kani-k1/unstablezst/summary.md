# K-1 run `unstablezst-meas-zst-unstable-dispatch-aware-20261103`: COMPLETE

- head `7c8bdefd81a49209c74f354083cdbb587eb7aac6`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `0507b71351a78af507cee9fcf0fbde27b9e1fa473c6e8d9923f4262390c108dc`
- run 5228c09f-b2de-48b0-b5c9-1f7e957e6685 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: False; Kani exit 1
- whole run, including compilation: max RSS 9127364 KiB, wall 31:09.24 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 933 samples, largest sampled sum of RSS 8.73 GiB at 669 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 8.69 GiB (≤13 GiB), seen 72–1867 s, peak sample 669 s
  - `kani-compiler` 1.70 GiB (≤13 GiB), seen 2–68 s, peak sample 52 s
  - `kani-driver` 0.19 GiB (≤13 GiB), seen 2–1867 s, peak sample 1851 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–68 s, peak sample 68 s
  - `goto-instrument` 0.03 GiB (≤13 GiB), seen 1123–1354 s, peak sample 1123 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `goto-cc` 0.02 GiB (≤13 GiB), seen 70–70 s, peak sample 70 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1869 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1867 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1867 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–1867 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1869 s, peak sample 0 s
  - simultaneous cbmc RSS 8.69 GiB at 669 s
  - simultaneous driver RSS 0.19 GiB at 1851 s
  - cbmc PID 9247: 8.69 GiB peak at 669 s; active `T0:network::zstprobe::zst_unstable_dispatch_aware_n8_9_12_13_17`
  - cbmc PID 9392: 3.84 GiB peak at 1831 s; active `T0:network::zstprobe::zst_unstable_dispatch_aware_n17`
  - cbmc PID 9363: 3.83 GiB peak at 1568 s; active `T0:network::zstprobe::zst_unstable_dispatch_aware_n13`
  - cbmc PID 9276: 3.76 GiB peak at 898 s; active `T0:network::zstprobe::zst_unstable_dispatch_aware_n9`
  - cbmc PID 9334: 3.76 GiB peak at 1326 s; active `T0:network::zstprobe::zst_unstable_dispatch_aware_n12`
  - cbmc PID 9305: 3.69 GiB peak at 1101 s; active `T0:network::zstprobe::zst_unstable_dispatch_aware_n8`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| network::zstprobe::zst_unstable_dispatch_aware_n8_9_12_13_17 | SUCCESS | TIMEOUT | None |  | None |  |
| network::zstprobe::zst_unstable_dispatch_aware_n8 | SUCCESS | SUCCESS | 195.41185 | 0/358 | 18 | 2/2 |
| network::zstprobe::zst_unstable_dispatch_aware_n9 | SUCCESS | SUCCESS | 251.70735 | 0/358 | 18 | 2/2 |
| network::zstprobe::zst_unstable_dispatch_aware_n12 | SUCCESS | SUCCESS | 230.07697 | 0/358 | 18 | 2/2 |
| network::zstprobe::zst_unstable_dispatch_aware_n13 | SUCCESS | SUCCESS | 242.18927 | 0/358 | 18 | 2/2 |
| network::zstprobe::zst_unstable_dispatch_aware_n17 | SUCCESS | SUCCESS | 270.87903 | 0/358 | 18 | 2/2 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 9127364 KiB exceeds the largest sampled command peak 9117356 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::zstprobe::zst_unstable_dispatch_aware_n8
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::zstprobe::zst_unstable_dispatch_aware_n9
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::zstprobe::zst_unstable_dispatch_aware_n12
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::zstprobe::zst_unstable_dispatch_aware_n13
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::zstprobe::zst_unstable_dispatch_aware_n17
