# K-1 run `direct-b-remaining`: COMPLETE

- head `0335a90e393b566617ec9be870682517dc3d7c62`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `c2081954bad62bb7b5637075238eb26ea8a68a88ee7bf7e0921b393ce0060975`
- run 7bda9e5a-266a-41c2-89d5-c0606da6befe attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
- whole run, including compilation: max RSS 6585000 KiB, wall 21:06.57 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 633 samples, largest sampled sum of RSS 6.55 GiB at 353 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 6.28 GiB (≤13 GiB), seen 66–1265 s, peak sample 310 s
  - `kani-compiler` 1.79 GiB (≤13 GiB), seen 2–58 s, peak sample 46 s
  - `kani-driver` 1.21 GiB (≤13 GiB), seen 2–1265 s, peak sample 1171 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 64–1117 s, peak sample 1065 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–58 s, peak sample 2 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 60–1171 s, peak sample 60 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1265 s, peak sample 2 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1266 s, peak sample 0 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1265 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 64–1173 s, peak sample 1173 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1266 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 6.22 GiB at 353 s
  - simultaneous driver RSS 1.18 GiB at 1265 s
  - cbmc PID 9326: 6.28 GiB peak at 310 s; active `T0:merge::general_stable_direct_u64_n7`
  - cbmc PID 9353: 6.03 GiB peak at 701 s; active `T0:merge::general_stable_direct_u64_n6`
  - cbmc PID 9299: 4.49 GiB peak at 168 s; active `T0:merge::general_stable_direct_u64_n5`
  - cbmc PID 9542: 0.97 GiB peak at 1189 s; active `T0:merge::general_stable_sorted_permutation_u64_n8`
  - cbmc PID 9515: 0.61 GiB peak at 1131 s; active `T0:merge::general_stable_sorted_permutation_u8_n9`
  - cbmc PID 9434: 0.56 GiB peak at 890 s; active `T0:merge::general_stable_direct_u8_n8`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::general_stable_direct_u64_n5 | SUCCESS | SUCCESS | 89.78859 | 0/407 | 67 | 2/2 |
| merge::general_stable_direct_u64_n6 | SUCCESS | SUCCESS | 235.455 | 0/407 | 66 | 2/2 |
| merge::general_stable_direct_u64_n7 | SUCCESS | SUCCESS | 382.71622 | 0/407 | 65 | 2/2 |
| merge::general_stable_direct_u8_n5 | SUCCESS | SUCCESS | 27.549227 | 0/400 | 69 | 2/2 |
| merge::general_stable_direct_u8_n6 | SUCCESS | SUCCESS | 22.382229 | 0/400 | 68 | 2/2 |
| merge::general_stable_direct_u8_n7 | SUCCESS | SUCCESS | 48.825714 | 0/400 | 67 | 2/2 |
| merge::general_stable_direct_u8_n8 | SUCCESS | SUCCESS | 142.44217 | 0/400 | 64 | 2/2 |
| merge::general_stable_sorted_permutation_u64_n8 | SUCCESS | SUCCESS | 93.25507 | 0/638 | 97 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n9 | SUCCESS | SUCCESS | 53.54981 | 0/631 | 97 | 2/2 |
| merge::general_stable_sorted_permutation_u64_n6 | SUCCESS | SUCCESS | 38.43796 | 0/638 | 103 | 2/2 |
| merge::general_stable_sorted_permutation_u64_n7 | SUCCESS | SUCCESS | 49.328888 | 0/638 | 101 | 2/2 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- 67 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u64_n5
- 66 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u64_n6
- 65 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u64_n7
- 69 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u8_n5
- 68 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u8_n6
- 67 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u8_n7
- 64 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u8_n8
- 97 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n8
- 97 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n9
- 103 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n6
- 101 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n7
