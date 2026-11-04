# K-1 run `widthuthirtytwo-g1-perm-u32n8-20261103`: COMPLETE

- head `e39f946565f3625aae0f3c525f558c88b6566e5a`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `ab2a1ab9a15626e78308b93bf04a73304c6d38d05c29c452eb5b8ad6bc66ca85`
- run 0334e611-b11c-4036-9f4b-4e58417f7bbd attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1706360 KiB, wall 14:46.61 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 444 samples, largest sampled sum of RSS 1.85 GiB at 50 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.63 GiB (≤13 GiB), seen 2–66 s, peak sample 50 s
  - `cbmc` 0.15 GiB (≤13 GiB), seen 70–886 s, peak sample 290 s
  - `kani-driver` 0.12 GiB (≤13 GiB), seen 2–886 s, peak sample 74 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 4 s
  - `kissat` 0.03 GiB (≤13 GiB), seen 70–282 s, peak sample 240 s
  - `goto-instrument` 0.03 GiB (≤13 GiB), seen 68–74 s, peak sample 74 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–886 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–886 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–886 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–886 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–886 s, peak sample 2 s
  - simultaneous cbmc RSS 0.12 GiB at 832 s
  - simultaneous driver RSS 0.10 GiB at 284 s
  - simultaneous solver RSS 0.03 GiB at 240 s
  - cbmc PID 9294: 0.15 GiB peak at 290 s; active `T0:network::widthu32::widthu32_perm_n8_default`
  - cbmc PID 9227: 0.09 GiB peak at 72 s; active `T0:network::widthu32::widthu32_perm_n8_value_loss_control`
  - cbmc PID 9261: 0.09 GiB peak at 284 s; active `T0:network::widthu32::widthu32_perm_n8_kissat`
  - kissat PID 9269: 0.03 GiB peak at 240 s; active `T0:network::widthu32::widthu32_perm_n8_kissat`
  - kissat PID 9232: 0.02 GiB peak at 70 s; active ``
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| network::widthu32::widthu32_perm_n8_default | SUCCESS | TIMEOUT | None |  | None |  |
| network::widthu32::widthu32_perm_n8_kissat | SUCCESS | SUCCESS | 210.76735 | 0/334 | 18 | 5/5 |
| network::widthu32::widthu32_perm_n8_value_loss_control | FAILED | FAILED | 5.3764286 | 1/338 | 18 | 5/5 |

Failed checks of `slice::sort::shared::smallsort::verify::network::widthu32::widthu32_perm_n8_value_loss_control`:
- widthu32 negative: full-value count after value loss @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/network/widthu32.rs:67

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 1706360 KiB exceeds the largest sampled command peak 1706020 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::widthu32::widthu32_perm_n8_kissat
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::network::widthu32::widthu32_perm_n8_value_loss_control
