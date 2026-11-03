# K-1 run `zstprobe-diag-zst-dispatch-volatile-20261103`: COMPLETE

- head `debceddebaaa100eec0dda1a4e0c0cae85d6b09e`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `6a1d2d15b8524ebc99e405b9d4e25d8b0972b672e66991c9697629d6ab3dad09`
- run 8922abbc-a604-46ce-adee-fa919ada629b attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 3465072 KiB, wall 4:24.37 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 133 samples, largest sampled sum of RSS 3.45 GiB at 248 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 3.30 GiB (≤13 GiB), seen 70–262 s, peak sample 226 s
  - `kani-compiler` 1.66 GiB (≤13 GiB), seen 2–64 s, peak sample 50 s
  - `kani-driver` 0.71 GiB (≤13 GiB), seen 2–262 s, peak sample 248 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–64 s, peak sample 64 s
  - `goto-instrument` 0.02 GiB (≤13 GiB), seen 66–66 s, peak sample 66 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `goto-cc` 0.02 GiB (≤13 GiB), seen 68–68 s, peak sample 68 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–264 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–262 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–262 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–262 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–264 s, peak sample 0 s
  - simultaneous cbmc RSS 3.30 GiB at 226 s
  - simultaneous driver RSS 0.71 GiB at 248 s
  - cbmc PID 9312: 3.30 GiB peak at 226 s; active `T0:network::zstprobe::zst_stable_dispatch_aware_n0_1_2_7_8_15_16_17_31_32`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| network::zstprobe::zst_stable_dispatch_aware_n0_1_2_7_8_15_16_17_31_32 | SUCCESS | SUCCESS | 194.84787 | 0/391 | 5 | 11/11 |
| network::zstprobe::zst_stable_dispatch_volatile_n2 | SUCCESS | FAILED | 1.2114006 | 4/356 | 12 | 2/2 |
| network::zstprobe::zst_read_volatile_dangling | SUCCESS | FAILED | 0.065541565 | 5/32 | 2 | 1/1 |
| network::zstprobe::zst_read_volatile_local | SUCCESS | FAILED | 0.055160776 | 4/16 | 2 | 1/1 |

Failed checks of `slice::sort::shared::smallsort::verify::network::zstprobe::zst_stable_dispatch_volatile_n2`:
- dereference failure: pointer NULL @ no location
- dereference failure: pointer invalid @ no location
- dereference failure: pointer outside object bounds @ no location
- dereference failure: invalid integer address @ no location

Failed checks of `slice::sort::shared::smallsort::verify::network::zstprobe::zst_read_volatile_dangling`:
- dereference failure: pointer NULL @ no location
- dereference failure: deallocated dynamic object @ no location
- dereference failure: dead object @ no location
- dereference failure: pointer outside object bounds @ no location
- dereference failure: invalid integer address @ no location

Failed checks of `slice::sort::shared::smallsort::verify::network::zstprobe::zst_read_volatile_local`:
- dereference failure: pointer NULL @ no location
- dereference failure: pointer invalid @ no location
- dereference failure: pointer outside object bounds @ no location
- dereference failure: invalid integer address @ no location

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::network::zstprobe::zst_stable_dispatch_aware_n0_1_2_7_8_15_16_17_31_32
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::network::zstprobe::zst_stable_dispatch_volatile_n2
- 2 unreachable check(s) in slice::sort::shared::smallsort::verify::network::zstprobe::zst_read_volatile_dangling
- 2 unreachable check(s) in slice::sort::shared::smallsort::verify::network::zstprobe::zst_read_volatile_local
