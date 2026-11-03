# K-1 run `typesplit-meas-dispatch-n31-n32-route-split-20261103`: COMPLETE

- head `b595df116a8b9ea63df8f8d4cca5f1685fcf6d95`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `2f5b88dc980dcdb033d090c8dbd71110c9d8dc89bb0f3c88490897c8ab294390`
- run de53e600-f485-4f43-bb2b-5b51ef686368 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
- whole run, including compilation: max RSS 1873224 KiB, wall 25:07.44 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 753 samples, largest sampled sum of RSS 2.91 GiB at 1384 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 1.79 GiB (≤13 GiB), seen 96–1507 s, peak sample 529 s
  - `kani-driver` 1.74 GiB (≤13 GiB), seen 2–1507 s, peak sample 1384 s
  - `kani-compiler` 1.72 GiB (≤13 GiB), seen 2–88 s, peak sample 72 s
  - `goto-instrument` 0.03 GiB (≤13 GiB), seen 94–1386 s, peak sample 867 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–88 s, peak sample 2 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 90–1065 s, peak sample 614 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1507 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1507 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–1507 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1507 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1507 s, peak sample 0 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 1.79 GiB at 529 s
  - simultaneous driver RSS 1.74 GiB at 1384 s
  - cbmc PID 9379: 1.79 GiB peak at 529 s; active `T0:network::typematrix::dispatch_safety_unstable_bytes9_n32`
  - cbmc PID 9321: 1.72 GiB peak at 264 s; active `T0:network::typematrix::dispatch_safety_unstable_bytes9_n31`
  - cbmc PID 9524: 1.43 GiB peak at 1127 s; active `T0:network::typematrix::dispatch_safety_stable_bytes9_n32`
  - cbmc PID 9495: 1.42 GiB peak at 1025 s; active `T0:network::typematrix::dispatch_safety_unstable_u8u32_n32`
  - cbmc PID 9553: 1.38 GiB peak at 1234 s; active `T0:network::typematrix::dispatch_safety_stable_bytes9_n31`
  - cbmc PID 9437: 1.37 GiB peak at 837 s; active `T0:network::typematrix::dispatch_safety_stable_u8u32_n32`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| network::typematrix::dispatch_safety_stable_u8u32_n31 | SUCCESS | SUCCESS | 88.15739 | 0/368 | 9 | 2/2 |
| network::typematrix::dispatch_safety_stable_u8u32_n32 | SUCCESS | SUCCESS | 95.76844 | 0/368 | 9 | 2/2 |
| network::typematrix::dispatch_safety_unstable_u8u32_n31 | SUCCESS | SUCCESS | 110.25283 | 0/368 | 12 | 2/2 |
| network::typematrix::dispatch_safety_unstable_u8u32_n32 | SUCCESS | SUCCESS | 119.04314 | 0/368 | 12 | 2/2 |
| network::typematrix::dispatch_safety_stable_u128_n31 | SUCCESS | SUCCESS | 151.42155 | 0/368 | 9 | 2/2 |
| network::typematrix::dispatch_safety_stable_u128_n32 | SUCCESS | SUCCESS | 120.035515 | 0/368 | 9 | 2/2 |
| network::typematrix::dispatch_safety_unstable_u128_n31 | SUCCESS | SUCCESS | 77.455696 | 0/368 | 8 | 2/2 |
| network::typematrix::dispatch_safety_unstable_u128_n32 | SUCCESS | SUCCESS | 90.541306 | 0/368 | 8 | 2/2 |
| network::typematrix::dispatch_safety_stable_bytes9_n31 | SUCCESS | SUCCESS | 98.47637 | 0/368 | 9 | 2/2 |
| network::typematrix::dispatch_safety_stable_bytes9_n32 | SUCCESS | SUCCESS | 107.75439 | 0/368 | 9 | 2/2 |
| network::typematrix::dispatch_safety_unstable_bytes9_n31 | SUCCESS | SUCCESS | 145.74107 | 0/368 | 8 | 2/2 |
| network::typematrix::dispatch_safety_unstable_bytes9_n32 | SUCCESS | SUCCESS | 189.97173 | 0/368 | 8 | 2/2 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_u8u32_n31
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_u8u32_n32
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_unstable_u8u32_n31
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_unstable_u8u32_n32
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_u128_n31
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_u128_n32
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_unstable_u128_n31
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_unstable_u128_n32
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_bytes9_n31
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_stable_bytes9_n32
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_unstable_bytes9_n31
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::typematrix::dispatch_safety_unstable_bytes9_n32
