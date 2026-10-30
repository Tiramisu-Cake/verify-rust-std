# K-1 run `backing-matched-20261031`: COMPLETE

- head `740d22674ca200f3270fb298651302019d347828`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `ef800ff1643797b5b2ba12baa88dfad5c89e3e1292c676047d834b4b1c09bcf7`
- run b07fdcd8-fbd8-401e-9948-9e5f9e7201ad attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: True; Kani exit 1
- whole run, including compilation: max RSS 8313336 KiB, wall 14:14.82 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 428 samples, largest sampled sum of RSS 8.36 GiB at 419 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 7.93 GiB (≤13 GiB), seen 76–854 s, peak sample 463 s
  - `kani-compiler` 1.71 GiB (≤13 GiB), seen 2–68 s, peak sample 52 s
  - `kani-driver` 0.74 GiB (≤13 GiB), seen 2–854 s, peak sample 591 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 72–297 s, peak sample 74 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–68 s, peak sample 4 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 70–726 s, peak sample 726 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–855 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–854 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–854 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–855 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–854 s, peak sample 2 s
  - simultaneous cbmc RSS 7.86 GiB at 419 s
  - simultaneous driver RSS 0.70 GiB at 720 s
  - cbmc PID 9358: 7.93 GiB peak at 463 s; active `T0:merge::opt_split::stable_direct_u64_n8`
  - cbmc PID 9385: 2.43 GiB peak at 684 s; active `T0:network::backing::dispatch_safety_stable_bytes17_n32_new`
  - cbmc PID 9414: 1.64 GiB peak at 808 s; active `T0:network::backing::dispatch_safety_stable_bytes17_n32_old`
  - cbmc PID 9331: 1.51 GiB peak at 92 s; active `T0:merge::backing::stable_direct_u64_n8`
  - cbmc PID 9304: 0.14 GiB peak at 78 s; active `T0:merge::backing::stable_value_corruption_control_u64_n2`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::opt_split::stable_direct_u64_n8 | SUCCESS | SUCCESS | 292.46835 | 0/405 | 62 | 1/1 |
| merge::backing::stable_direct_u64_n8 | SUCCESS | SUCCESS | 214.31592 | 0/407 | 62 | 1/1 |
| network::backing::dispatch_safety_stable_bytes17_n32_old | SUCCESS | SUCCESS | 127.42941 | 0/378 | 10 | 1/1 |
| network::backing::dispatch_safety_stable_bytes17_n32_new | SUCCESS | SUCCESS | 134.57643 | 0/352 | 6 | 1/1 |
| merge::backing::stable_value_corruption_control_u64_n2 | FAILED | FAILED | 4.9353704 | 1/409 | 69 | 1/1 |
| merge::backing::unsorted_halves_control_u64_n4 | FAILED | FAILED | 0.6949606 | 1/472 | 122 | 1/1 |
| merge::backing::allocation_bounds_control_u64 | FAILED | FAILED | 0.07497778 | 1/16 | 3 | 1/1 |

Failed checks of `slice::sort::shared::smallsort::verify::merge::backing::stable_value_corruption_control_u64_n2`:
- This is a placeholder message; Kani doesn't support message formatted at runtime @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:846

Failed checks of `slice::sort::shared::smallsort::verify::merge::backing::unsorted_halves_control_u64_n4`:
- CopyOnDrop::<T>::merge_inputs_are_sorted(v, &is_less) @ /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:842

Failed checks of `slice::sort::shared::smallsort::verify::merge::backing::allocation_bounds_control_u64`:
- dereference failure: pointer outside object bounds @ /workspace/src/library/core/src/ptr/mod.rs:1981

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 62 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::stable_direct_u64_n8
- 62 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::backing::stable_direct_u64_n8
- 10 unreachable check(s) in slice::sort::shared::smallsort::verify::network::backing::dispatch_safety_stable_bytes17_n32_old
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::network::backing::dispatch_safety_stable_bytes17_n32_new
- 69 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::backing::stable_value_corruption_control_u64_n2
- 122 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::backing::unsorted_halves_control_u64_n4
- 3 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::backing::allocation_bounds_control_u64
