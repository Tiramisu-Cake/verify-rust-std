# K-1 run `kani3300-u0-uninit-20261111-01`: COMPLETE

- head `69b3b92fc9965e3e35af4eeff80d02c650745285`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `0dbce45f0859d38e56817b53e1861e4d028853418f6826caa73293adfb966056`
- run 51f228c7-615f-4027-8bae-d68fb293e132 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 1, uninit checks on, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1769104 KiB, wall 1:28.94 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 46 samples, largest sampled sum of RSS 2.23 GiB at 60 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.69 GiB (≤13 GiB), seen 2–68 s, peak sample 62 s
  - `cbmc` 0.46 GiB (≤13 GiB), seen 76–88 s, peak sample 78 s
  - `kani-driver` 0.07 GiB (≤13 GiB), seen 2–88 s, peak sample 84 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–68 s, peak sample 4 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `goto-instrument` 0.02 GiB (≤13 GiB), seen 70–84 s, peak sample 84 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 70–70 s, peak sample 70 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–89 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–88 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–88 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 70–70 s, peak sample 70 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–89 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 0.46 GiB at 78 s
  - simultaneous driver RSS 0.07 GiB at 84 s
  - cbmc PID 8762: 0.46 GiB peak at 78 s; active `T0:uninit_probe::swap_contract_four_positions_u8_function_item`
  - cbmc PID 8858: 0.07 GiB peak at 86 s; active ``
  - cbmc PID 8818: 0.05 GiB peak at 82 s; active `T0:uninit_probe::permutation_merge_u8_n4`
  - cbmc PID 8908: 0.03 GiB peak at 88 s; active `T0:uninit_probe::swap_contract_four_positions_u8`
  - cbmc PID 8789: 0.03 GiB peak at 80 s; active `T0:uninit_probe::swap_contract_four_positions_u8_function_item`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| uninit_probe::pincheck_calibration_uninit_read_u8 | FAILED | FAILED | 0.38240585 | 1/31 | 3 | 3/3 |
| uninit_probe::pincheck_calibration_init_read_u8 | SUCCESS | FAILED | 0.49518698 | 1/32 | 0 | 3/3 |
| uninit_probe::raw_uninit_read_sensitivity | FAILED | FAILED | 0.10888922 | 1/47 | 13 | 0/3 |
| uninit_probe::swap_contract_four_positions_u8 | SUCCESS | FAILED | 1.9651716 | 1/454 | 32 | 2/5 |
| uninit_probe::sorted_permutation_insert_tail_u8_n2 | SUCCESS | SUCCESS | 1.4840374 | 0/181 | 4 | 1/1 |
| uninit_probe::permutation_merge_u8_n4 | SUCCESS | FAILED | 0.26872548 | 1/243 | 42 | 0/1 |
| uninit_probe::swap_contract_four_positions_u8_function_item | SUCCESS | FAILED | 4.6925774 | 1/416 | 24 | 2/5 |
| uninit_probe::small_sort_general_with_scratch_u8_n4 | SUCCESS | FAILED | 0.40498284 | 1/515 | 73 | 0/1 |

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::pincheck_calibration_uninit_read_u8`:
- Transmuting between types of incompatible layouts. @ /workspace/src/library/core/src/mem/mod.rs:1283

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::pincheck_calibration_init_read_u8`:
- Transmuting between types of incompatible layouts. @ /workspace/src/library/core/src/mem/mod.rs:1283

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::raw_uninit_read_sensitivity`:
- Interaction between raw pointers and unions is not yet supported. @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/uninit_probe.rs:47

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::swap_contract_four_positions_u8`:
- Kani does not support memory initialization checks across calls through function pointers. For more information about planned support, see https://github.com/model-checking/kani/issues/3300. @ /workspace/src/library/core/src/ops/function.rs:166

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::permutation_merge_u8_n4`:
- Interaction between raw pointers and unions is not yet supported. @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/uninit_probe.rs:117

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::swap_contract_four_positions_u8_function_item`:
- Interaction between raw pointers and unions is not yet supported. @ /workspace/src/library/core/src/hint.rs:844

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::small_sort_general_with_scratch_u8_n4`:
- Checking memory initialization of type [mem::maybe_uninit::MaybeUninit<u8>; 20] is not supported. Cannot determine layout for a type that contains union of type mem::maybe_uninit::MaybeUninit<u8> as a field. @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/uninit_probe.rs:177

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` d51f9c59823339dfd211e0e1226e6a372f4816d2ef6c86a68cce2676dc796215
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 60af9d2e9f2d704ed66e6201cfc990662e000d860a230967ab64ec0e20801897
- `research/challenge-8/kani-k1/tools/kani_k1.py` c199cace580a89f5ee7113aafe2d6757bf23c698d873a0b14589d9f7908a43b9
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 7dca0aa5bf9467c6c4fb4323dabc12254f6372f5f01af096420583bc2b5c9ca3

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- -Z uninit-checks on: not in the organizers' CI flags, evidence outside CI
- 3 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::pincheck_calibration_uninit_read_u8
- 13 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::raw_uninit_read_sensitivity
- 32 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::swap_contract_four_positions_u8
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::sorted_permutation_insert_tail_u8_n2
- 42 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::permutation_merge_u8_n4
- 24 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::swap_contract_four_positions_u8_function_item
- 73 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::small_sort_general_with_scratch_u8_n4
