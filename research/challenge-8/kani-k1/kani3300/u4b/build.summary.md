# K-1 run `kani3300-u4b-uninit-20261111-01`: COMPLETE

- head `d3e56afbf577da0d94e82406d10e9b77c2492900`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `53a2f3ac1453787fd74f190d838352f9a819676619c66f456c6dad8c197bd1ff`
- run 6d1690f4-c07e-4af9-a858-d97534c4db29 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 1, uninit checks on, valid-value checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1861528 KiB, wall 3:22.43 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- Kani applied tree `d356238999ab436ddc1dd7ffa845b0db214aa53e`, patch `46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`, version `Kani Rust Verifier 0.68.0 (standalone); CBMC 6.11.0`
- Kani build 259 s; compiletest build 0 s
- patch diffstat: .../delayed_ub/instrumentation_visitor.rs          |  55 +-
 .../transform/check_uninit/delayed_ub/mod.rs       |   1 +
 .../src/kani_middle/transform/check_uninit/mod.rs  | 232 ++++++-
 .../transform/check_uninit/ptr_uninit/mod.rs       |   3 +-
 .../check_uninit/ptr_uninit/uninit_visitor.rs      | 689 +++++++++++++++++----
 .../transform/check_uninit/relevant_instruction.rs |  68 +-
 .../transform/check_uninit/ty_layout.rs            | 343 +++++++++-
 library/kani_core/src/mem_init.rs                  | 110 +++-
 8 files changed, 1309 insertions(+), 192 deletions(-)
- memory peaks PARSED: sampled every 2 s, 102 samples, largest sampled sum of RSS 2.24 GiB at 66 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.77 GiB (≤13 GiB), seen 2–72 s, peak sample 72 s
  - `kani-driver` 0.76 GiB (≤13 GiB), seen 2–200 s, peak sample 200 s
  - `cbmc` 0.36 GiB (≤13 GiB), seen 76–198 s, peak sample 180 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 74–74 s, peak sample 74 s
  - `goto-instrument` 0.03 GiB (≤13 GiB), seen 108–138 s, peak sample 138 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–72 s, peak sample 4 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–202 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–200 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–202 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–200 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–200 s, peak sample 2 s
  - simultaneous cbmc RSS 0.36 GiB at 180 s
  - simultaneous driver RSS 0.76 GiB at 200 s
  - cbmc PID 8780: 0.36 GiB peak at 180 s; active `T0:uninit_probe::small_sort_general_with_scratch_u8_n4`
  - cbmc PID 8726: 0.30 GiB peak at 100 s; active `T0:uninit_probe::small_sort_general_scratch_unwritten_slot_only_u8_n4`
  - cbmc PID 8753: 0.28 GiB peak at 130 s; active `T0:uninit_probe::small_sort_general_scratch_written_slot_u8_n4`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| uninit_probe::small_sort_general_scratch_written_slot_u8_n4 | SUCCESS | SUCCESS | 27.29353 | 0/492 | 19 | 3/3 |
| uninit_probe::small_sort_general_scratch_unwritten_slot_only_u8_n4 | FAILED | FAILED | 31.642582 | 2/503 | 19 | 4/4 |
| uninit_probe::small_sort_general_with_scratch_u8_n4 | SUCCESS | SUCCESS | 62.98066 | 0/572 | 19 | 1/1 |
| uninit_probe::pincheck_calibration_uninit_read_u8 | FAILED | FAILED | 0.67755663 | 1/30 | 0 | 3/3 |

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::small_sort_general_scratch_unwritten_slot_only_u8_n4`:
- Undefined Behavior: Reading from an uninitialized pointer of type `*const u8` @ /workspace/src/library/core/src/ptr/mod.rs:1769
- Undefined Behavior: Reading from an uninitialized pointer of type `u8` @ /workspace/src/library/core/src/ptr/mod.rs:1769

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::pincheck_calibration_uninit_read_u8`:
- Undefined Behavior: Reading from an uninitialized pointer of type `u8` @ /workspace/src/library/core/src/mem/mod.rs:1283

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` d51f9c59823339dfd211e0e1226e6a372f4816d2ef6c86a68cce2676dc796215
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 60af9d2e9f2d704ed66e6201cfc990662e000d860a230967ab64ec0e20801897
- `research/challenge-8/kani-k1/tools/kani_k1.py` 2a1b6d7a20af9b3c0296d9dc435cb7f12585ce16e27add45f10b9902e35fee23
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 7dca0aa5bf9467c6c4fb4323dabc12254f6372f5f01af096420583bc2b5c9ca3

Notes:
- time -v max RSS 1861528 KiB exceeds the largest sampled command peak 1861200 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- -Z uninit-checks on: not in the organizers' CI flags, evidence outside CI
- 19 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::small_sort_general_scratch_written_slot_u8_n4
- 19 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::small_sort_general_scratch_unwritten_slot_only_u8_n4
- 19 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::small_sort_general_with_scratch_u8_n4

