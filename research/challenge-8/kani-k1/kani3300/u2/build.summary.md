# K-1 run `kani3300-u2-uninit-20261111-01`: COMPLETE

- head `108551d92b7754d5366ec3b59bd0b652510adcef`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `d025202d57d3c271f125ca9ae8dda40b677d2bb591cad6b43307c5222f67bcb3`
- run 6a2f4260-c343-427f-a6ef-6ed0bce50b7c attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 1, uninit checks on, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1785160 KiB, wall 1:52.63 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- Kani applied tree `b9c36ac5ed550e39d26e1d1d77000052e62a9bb4`, patch `306851ac5dd4f28a11778dfc49e878a5bb62fd7c35a2ad7ad0419053b9504467`, version `Kani Rust Verifier 0.68.0 (standalone); CBMC 6.11.0`
- Kani build 245 s; compiletest build 0 s
- patch diffstat: .../transform/check_uninit/delayed_ub/mod.rs       |   1 +
 .../src/kani_middle/transform/check_uninit/mod.rs  | 106 ++++-
 .../transform/check_uninit/ptr_uninit/mod.rs       |   3 +-
 .../check_uninit/ptr_uninit/uninit_visitor.rs      | 476 ++++++++++++++++-----
 .../transform/check_uninit/relevant_instruction.rs |  59 ++-
 .../transform/check_uninit/ty_layout.rs            |  41 +-
 library/kani_core/src/mem_init.rs                  |  12 +-
 .../uninit/maybe-uninit-assume-init/expected       |   4 +
 .../uninit/maybe-uninit-assume-init/main.rs        |  13 +
 .../uninit/maybe-uninit-initialized/expected       |   1 +
 .../uninit/maybe-uninit-initialized/main.rs        | 103 +++++
 .../uninit/maybe-uninit-partial-copy/expected      |   5 +
 .../uninit/maybe-uninit-partial-copy/main.rs       |  22 +
 .../uninit/maybe-uninit-partial-write/expected     |   5 +
 .../uninit/maybe-uninit-partial-write/main.rs      |  19 +
 .../uninit/maybe-uninit-raw-address/expected       |   5 +
 .../uninit/maybe-uninit-raw-address/main.rs        |  18 +
 .../expected/uninit/maybe-uninit-raw-read/expected |   4 +
 .../expected/uninit/maybe-uninit-raw-read/main.rs  |  16 +
 .../uninit/maybe-uninit-reset-alias/expected       |   5 +
 .../uninit/maybe-uninit-reset-alias/main.rs        |  26 ++
 .../maybe-uninit-scratch-array-unwritten/expected  |   4 +
 .../maybe-uninit-scratch-array-unwritten/main.rs   |  17 +
 .../uninit/maybe-uninit-scratch-array/expected     |   1 +
 .../uninit/maybe-uninit-scratch-array/main.rs      |  16 +
 .../uninit/maybe-uninit-slice-offset/expected      |   5 +
 .../uninit/maybe-uninit-slice-offset/main.rs       |  20 +
 .../uninit/maybe-uninit-volatile-read/expected     |   4 +
 .../uninit/maybe-uninit-volatile-read/main.rs      |  15 +
 29 files changed, 876 insertions(+), 150 deletions(-)
- memory peaks PARSED: sampled every 2 s, 58 samples, largest sampled sum of RSS 2.10 GiB at 58 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.70 GiB (≤13 GiB), seen 2–66 s, peak sample 66 s
  - `cbmc` 0.26 GiB (≤13 GiB), seen 74–112 s, peak sample 94 s
  - `kani-driver` 0.21 GiB (≤13 GiB), seen 2–112 s, peak sample 104 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 66 s
  - `goto-instrument` 0.03 GiB (≤13 GiB), seen 70–106 s, peak sample 70 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `goto-cc` 0.02 GiB (≤13 GiB), seen 68–72 s, peak sample 72 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–112 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–112 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–112 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 108–108 s, peak sample 108 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–112 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 0.26 GiB at 94 s
  - simultaneous driver RSS 0.16 GiB at 106 s
  - cbmc PID 8829: 0.26 GiB peak at 94 s; active `T0:uninit_probe::swap_contract_four_positions_u8_function_item`
  - cbmc PID 8856: 0.13 GiB peak at 98 s; active `T0:uninit_probe::permutation_merge_u8_n4`
  - cbmc PID 8925: 0.07 GiB peak at 110 s; active `T0:uninit_probe::swap_contract_four_positions_u8`
  - cbmc PID 8885: 0.05 GiB peak at 104 s; active `T0:uninit_probe::permutation_merge_u8_n4`
  - cbmc PID 8789: 0.05 GiB peak at 74 s; active ``
  - cbmc PID 9000: 0.03 GiB peak at 112 s; active `T0:uninit_probe::swap_contract_four_positions_u8`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| uninit_probe::pincheck_calibration_uninit_read_u8 | FAILED | FAILED | 0.6318553 | 1/31 | 0 | 3/3 |
| uninit_probe::pincheck_calibration_init_read_u8 | SUCCESS | SUCCESS | 0.65874434 | 0/32 | 0 | 3/3 |
| uninit_probe::raw_uninit_read_sensitivity | FAILED | FAILED | 0.34033254 | 1/57 | 7 | 3/3 |
| uninit_probe::swap_contract_four_positions_u8 | SUCCESS | FAILED | 2.0437427 | 1/438 | 32 | 2/5 |
| uninit_probe::sorted_permutation_insert_tail_u8_n2 | SUCCESS | SUCCESS | 1.5808861 | 0/178 | 4 | 1/1 |
| uninit_probe::permutation_merge_u8_n4 | SUCCESS | SUCCESS | 7.6416106 | 0/230 | 4 | 1/1 |
| uninit_probe::swap_contract_four_positions_u8_function_item | SUCCESS | FAILED | 16.066118 | 3/400 | 18 | 2/5 |
| uninit_probe::small_sort_general_with_scratch_u8_n4 | SUCCESS | FAILED | 1.9385056 | 2/507 | 60 | 0/1 |
| uninit_probe::small_sort_general_scratch_unwritten_slot_u8_n4 | FAILED | FAILED | 1.7735901 | 2/463 | 47 | 0/6 |

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::pincheck_calibration_uninit_read_u8`:
- Undefined Behavior: Reading from an uninitialized pointer of type `u8` @ /workspace/src/library/core/src/mem/mod.rs:1283

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::raw_uninit_read_sensitivity`:
- Undefined Behavior: Reading from an uninitialized pointer of type `*const u8` @ /workspace/src/library/core/src/ptr/mod.rs:2175

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::swap_contract_four_positions_u8`:
- Kani does not support memory initialization checks across calls through function pointers. For more information about planned support, see https://github.com/model-checking/kani/issues/3300. @ /workspace/src/library/core/src/ops/function.rs:166

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::swap_contract_four_positions_u8_function_item`:
- Check that *var_9 is assignable @ library/kani_core/src/mem_init.rs:382
- Kani does not support reasoning about memory initialization of intrinsic `Unimplemented { name: "select_unpredictable", issue_link: "https://github.com/model-checking/kani/issues/new/choose" }`. @ /workspace/src/library/core/src/hint.rs:871
- Check that *var_17 is assignable @ library/kani_core/src/mem_init.rs:404

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::small_sort_general_with_scratch_u8_n4`:
- Transmuting between types of incompatible layouts. @ /workspace/src/library/core/src/array/iter.rs:77
- Kani does not support this assignment to MaybeUninit storage. @ /workspace/src/library/core/src/array/iter.rs:77

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::small_sort_general_scratch_unwritten_slot_u8_n4`:
- Transmuting between types of incompatible layouts. @ /workspace/src/library/core/src/array/iter.rs:77
- Kani does not support this assignment to MaybeUninit storage. @ /workspace/src/library/core/src/array/iter.rs:77

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` d51f9c59823339dfd211e0e1226e6a372f4816d2ef6c86a68cce2676dc796215
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 60af9d2e9f2d704ed66e6201cfc990662e000d860a230967ab64ec0e20801897
- `research/challenge-8/kani-k1/tools/kani_k1.py` c199cace580a89f5ee7113aafe2d6757bf23c698d873a0b14589d9f7908a43b9
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 7dca0aa5bf9467c6c4fb4323dabc12254f6372f5f01af096420583bc2b5c9ca3

Notes:
- time -v max RSS 1785160 KiB exceeds the largest sampled command peak 1784900 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- -Z uninit-checks on: not in the organizers' CI flags, evidence outside CI
- 7 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::raw_uninit_read_sensitivity
- 32 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::swap_contract_four_positions_u8
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::sorted_permutation_insert_tail_u8_n2
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::permutation_merge_u8_n4
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::swap_contract_four_positions_u8_function_item
- 60 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::small_sort_general_with_scratch_u8_n4
- 47 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::small_sort_general_scratch_unwritten_slot_u8_n4
