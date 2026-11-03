# K-1 run `panicprobe-e1-diag-6roots-20261103`: COMPLETE

- head `e147981c0a638929355fac8b9620089b0b55c24b`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `d1dccfe467d7662408718abd91f9ce51e0228075e16f56aa27f6640c090dbe6b`
- run aff12270-00bd-49e5-a680-5bab36e988eb attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1742248 KiB, wall 3:47.37 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 115 samples, largest sampled sum of RSS 1.79 GiB at 76 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.62 GiB (≤13 GiB), seen 2–100 s, peak sample 76 s
  - `kani-driver` 0.67 GiB (≤13 GiB), seen 2–226 s, peak sample 226 s
  - `cbmc` 0.48 GiB (≤13 GiB), seen 104–226 s, peak sample 214 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–100 s, peak sample 4 s
  - `goto-instrument` 0.02 GiB (≤13 GiB), seen 102–152 s, peak sample 152 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `goto-cc` 0.02 GiB (≤13 GiB), seen 124–124 s, peak sample 124 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–227 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–226 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–226 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–226 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–227 s, peak sample 2 s
  - simultaneous cbmc RSS 0.48 GiB at 214 s
  - simultaneous driver RSS 0.67 GiB at 226 s
  - cbmc PID 9333: 0.48 GiB peak at 214 s; active `T0:network::panicprobe::panic_network_u8_n18_should_panic`
  - cbmc PID 9304: 0.48 GiB peak at 176 s; active `T0:network::panicprobe::panic_network_u8_n18_plain`
  - cbmc PID 9275: 0.41 GiB peak at 144 s; active `T0:network::panicprobe::panic_general_u8_n16_should_panic`
  - cbmc PID 9248: 0.40 GiB peak at 116 s; active `T0:network::panicprobe::panic_general_u8_n16_plain`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| network::panicprobe::panic_control_plain | SUCCESS | SUCCESS | 0.044473596 | 1/2 | 0 | 1/1 |
| network::panicprobe::panic_control_ub | FAILED | FAILED | 0.06946079 | 2/8 | 0 | 1/1 |
| network::panicprobe::panic_network_u8_n18_should_panic | SUCCESS | SUCCESS | 37.001644 | 1/279 | 11 | 1/1 |
| network::panicprobe::panic_network_u8_n18_plain | FAILED | FAILED | 35.997242 | 1/279 | 11 | 1/1 |
| network::panicprobe::panic_general_u8_n16_should_panic | SUCCESS | SUCCESS | 25.993532 | 1/255 | 4 | 1/1 |
| network::panicprobe::panic_general_u8_n16_plain | FAILED | FAILED | 21.175707 | 1/255 | 4 | 1/1 |

Failed checks of `slice::sort::shared::smallsort::verify::network::panicprobe::panic_control_plain`:
- This is a placeholder message; Kani doesn't support message formatted at runtime @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/network/panicprobe.rs:37

Failed checks of `slice::sort::shared::smallsort::verify::network::panicprobe::panic_control_ub`:
- This is a placeholder message; Kani doesn't support message formatted at runtime @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/network/panicprobe.rs:48
- dereference failure: pointer outside object bounds @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/network/panicprobe.rs:54

Failed checks of `slice::sort::shared::smallsort::verify::network::panicprobe::panic_network_u8_n18_should_panic`:
- This is a placeholder message; Kani doesn't support message formatted at runtime @ /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:854

Failed checks of `slice::sort::shared::smallsort::verify::network::panicprobe::panic_network_u8_n18_plain`:
- This is a placeholder message; Kani doesn't support message formatted at runtime @ /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:854

Failed checks of `slice::sort::shared::smallsort::verify::network::panicprobe::panic_general_u8_n16_should_panic`:
- This is a placeholder message; Kani doesn't support message formatted at runtime @ /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:854

Failed checks of `slice::sort::shared::smallsort::verify::network::panicprobe::panic_general_u8_n16_plain`:
- This is a placeholder message; Kani doesn't support message formatted at runtime @ /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:854

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 1742248 KiB exceeds the largest sampled command peak 1695600 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 11 unreachable check(s) in slice::sort::shared::smallsort::verify::network::panicprobe::panic_network_u8_n18_should_panic
- 11 unreachable check(s) in slice::sort::shared::smallsort::verify::network::panicprobe::panic_network_u8_n18_plain
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::network::panicprobe::panic_general_u8_n16_should_panic
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::network::panicprobe::panic_general_u8_n16_plain
