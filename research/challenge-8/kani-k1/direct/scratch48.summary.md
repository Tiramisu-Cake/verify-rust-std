# K-1 run `direct-a-scratch48`: COMPLETE

- head `258208d0e5c6d54d637e9a9cfff3cbc39883fce0`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `3d4ddc2908cacee6d7a7b6ee5efc24ff0fffbf44b54ded6793a794abb8b4adef`
- run a72ff727-f085-46cd-96a6-dff28f421d6b attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: True; Kani exit 1
- whole run, including compilation: max RSS 9241468 KiB, wall 35:43.49 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 1070 samples, largest sampled sum of RSS 9.19 GiB at 750 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 8.81 GiB (≤13 GiB), seen 70–2142 s, peak sample 750 s
  - `kani-compiler` 1.72 GiB (≤13 GiB), seen 2–64 s, peak sample 50 s
  - `kani-driver` 0.92 GiB (≤13 GiB), seen 2–2142 s, peak sample 1345 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 72–1905 s, peak sample 812 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 66–1674 s, peak sample 66 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–64 s, peak sample 64 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–2143 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–2142 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–2142 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–2143 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–2142 s, peak sample 2 s
  - simultaneous cbmc RSS 8.74 GiB at 750 s
  - simultaneous driver RSS 0.88 GiB at 1540 s
  - cbmc PID 9356: 8.81 GiB peak at 750 s; active `T0:merge::merge_scratch48_contract_u64_n8`
  - cbmc PID 9394: 7.02 GiB peak at 1065 s; active `T0:merge::merge_scratch48_contract_u64_n7`
  - cbmc PID 9318: 6.58 GiB peak at 311 s; active `T0:merge::merge_scratch48_contract_u64_n6`
  - cbmc PID 9622: 4.66 GiB peak at 2065 s; active `T0:merge::merge_scratch48_contract_u64_n5`
  - cbmc PID 9432: 1.28 GiB peak at 1323 s; active `T0:merge::merge_scratch48_contract_u8_n9`
  - cbmc PID 9470: 1.21 GiB peak at 1522 s; active `T0:merge::merge_scratch48_contract_u8_n8`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::merge_scratch48_contract_u64_n5 | SUCCESS | SUCCESS | 208.6917 | 0/447 | 101 | 2/2 |
| merge::merge_scratch48_contract_u64_n6 | SUCCESS | SUCCESS | 310.3914 | 0/447 | 99 | 2/2 |
| merge::merge_scratch48_contract_u64_n7 | SUCCESS | SUCCESS | 338.99643 | 0/447 | 97 | 2/2 |
| merge::merge_scratch48_contract_u64_n8 | SUCCESS | SUCCESS | 417.82526 | 0/447 | 95 | 2/2 |
| merge::merge_scratch48_contract_u8_n5 | SUCCESS | SUCCESS | 84.004974 | 0/440 | 103 | 2/2 |
| merge::merge_scratch48_contract_u8_n6 | SUCCESS | SUCCESS | 124.35181 | 0/440 | 101 | 2/2 |
| merge::merge_scratch48_contract_u8_n7 | SUCCESS | SUCCESS | 131.9174 | 0/440 | 99 | 2/2 |
| merge::merge_scratch48_contract_u8_n8 | SUCCESS | SUCCESS | 193.20743 | 0/440 | 97 | 2/2 |
| merge::merge_scratch48_contract_u8_n9 | SUCCESS | SUCCESS | 187.80992 | 0/440 | 95 | 2/2 |
| merge::general_stable_direct_value_corruption_control_u64_n2 | FAILED | FAILED | 27.591068 | 1/407 | 70 |  |
| merge::merge_scratch48_unsorted_halves_control_u64_n4 | FAILED | FAILED | 0.5098025 | 1/470 | 122 | 1/1 |

Failed checks of `slice::sort::shared::smallsort::verify::merge::general_stable_direct_value_corruption_control_u64_n2`:
- direct output preserves full-value counts @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:952

Failed checks of `slice::sort::shared::smallsort::verify::merge::merge_scratch48_unsorted_halves_control_u64_n4`:
- CopyOnDrop::<T>::merge_inputs_are_sorted(v, &is_less) @ /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:842

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 101 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u64_n5
- 99 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u64_n6
- 97 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u64_n7
- 95 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u64_n8
- 103 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u8_n5
- 101 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u8_n6
- 99 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u8_n7
- 97 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u8_n8
- 95 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u8_n9
- 70 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_value_corruption_control_u64_n2
- 122 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_scratch48_unsorted_halves_control_u64_n4
