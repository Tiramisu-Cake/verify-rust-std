# K-1 run `opt-split-n8-20261030`: COMPLETE

- head `c81c10e3061e07bb83c732d81413632ada757d2c`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `4320d011a37a848ee2d661a2a546738680ecd45eb4454af88555b3c5ee3d4a11`
- run 0e44427c-18bd-4de4-95b2-e8730abec632 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
- whole run, including compilation: max RSS 8419228 KiB, wall 19:13.36 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 577 samples, largest sampled sum of RSS 8.39 GiB at 585 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 8.03 GiB (≤13 GiB), seen 74–1151 s, peak sample 623 s
  - `kani-compiler` 1.56 GiB (≤13 GiB), seen 2–66 s, peak sample 50 s
  - `kani-driver` 0.75 GiB (≤13 GiB), seen 2–1153 s, peak sample 1153 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 70–649 s, peak sample 649 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 66 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `goto-cc` 0.01 GiB (≤13 GiB), seen 68–68 s, peak sample 68 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1153 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1153 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–1153 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1153 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1153 s, peak sample 2 s
  - simultaneous cbmc RSS 7.99 GiB at 585 s
  - simultaneous driver RSS 0.75 GiB at 1153 s
  - cbmc PID 9281: 8.03 GiB peak at 623 s; active `T0:merge::opt_split::stable_contract_u64_n8`
  - cbmc PID 9308: 7.93 GiB peak at 802 s; active `T0:merge::opt_split::stable_direct_u64_n8`
  - cbmc PID 9243: 1.86 GiB peak at 238 s; active `T0:merge::opt_split::general_contract_u64_n8`
  - cbmc PID 9335: 1.51 GiB peak at 962 s; active `T0:merge::opt_split::general_direct_u64_n8`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::opt_split::general_direct_u64_n8 | SUCCESS | SUCCESS | 203.0456 | 0/407 | 62 | 1/1 |
| merge::opt_split::stable_direct_u64_n8 | SUCCESS | SUCCESS | 298.92392 | 0/405 | 62 | 1/1 |
| merge::opt_split::general_contract_u64_n8 | SUCCESS | SUCCESS | 221.69978 | 0/447 | 95 | 1/1 |
| merge::opt_split::stable_contract_u64_n8 | SUCCESS | SUCCESS | 349.38107 | 0/447 | 95 | 1/1 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 62 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::general_direct_u64_n8
- 62 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::stable_direct_u64_n8
- 95 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::general_contract_u64_n8
- 95 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::stable_contract_u64_n8
