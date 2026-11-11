# K-1 run `kani3300-t1a-uninit-20261111-01`: COMPLETE

- head `5d0679cf657683bb9beb754043dda00e48baa24c`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `0a5300eb89b52b0e26714b7ce5b749cc66239ef2630dd3e0de5eb2e7fce0156c`
- run fd4c3316-efbc-4f33-8506-e22b9f2ff3b3 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 1, uninit checks on, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1752144 KiB, wall 1:59.49 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- Kani applied tree `d356238999ab436ddc1dd7ffa845b0db214aa53e`, patch `46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`, version `Kani Rust Verifier 0.68.0 (standalone); CBMC 6.11.0`
- Kani build 257 s; compiletest build 0 s
- patch diffstat: .../delayed_ub/instrumentation_visitor.rs          |  55 +-
 .../transform/check_uninit/delayed_ub/mod.rs       |   1 +
 .../src/kani_middle/transform/check_uninit/mod.rs  | 232 ++++++-
 .../transform/check_uninit/ptr_uninit/mod.rs       |   3 +-
 .../check_uninit/ptr_uninit/uninit_visitor.rs      | 689 +++++++++++++++++----
 .../transform/check_uninit/relevant_instruction.rs |  68 +-
 .../transform/check_uninit/ty_layout.rs            | 343 +++++++++-
 library/kani_core/src/mem_init.rs                  | 110 +++-
 8 files changed, 1309 insertions(+), 192 deletions(-)
- memory peaks PARSED: sampled every 2 s, 61 samples, largest sampled sum of RSS 2.24 GiB at 54 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.62 GiB (≤13 GiB), seen 2–68 s, peak sample 60 s
  - `kani-driver` 0.83 GiB (≤13 GiB), seen 2–118 s, peak sample 118 s
  - `cbmc` 0.34 GiB (≤13 GiB), seen 72–118 s, peak sample 100 s
  - `rust-lld` 0.06 GiB (≤13 GiB), seen 2–2 s, peak sample 2 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 70–84 s, peak sample 84 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–68 s, peak sample 62 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–119 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–118 s, peak sample 2 s
  - `cc` 0.00 GiB (≤13 GiB), seen 2–2 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–118 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–118 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 0.32 GiB at 104 s
  - simultaneous driver RSS 0.60 GiB at 118 s
  - cbmc PID 8912: 0.34 GiB peak at 100 s; active `T0:uninit_probe::small_sort_general_with_scratch_u8_n4`
  - cbmc PID 8760: 0.07 GiB peak at 72 s; active ``
  - cbmc PID 8810: 0.04 GiB peak at 76 s; active `T0:uninit_probe::cmp3_into_iter_len`
  - cbmc PID 8835: 0.03 GiB peak at 78 s; active `T0:uninit_probe::cmp3_manually_drop_unsized_len`
  - cbmc PID 8785: 0.03 GiB peak at 74 s; active `T0:uninit_probe::cmp3_into_iter_next`
  - cbmc PID 8937: 0.02 GiB peak at 118 s; active `T0:uninit_probe::small_sort_general_with_scratch_u8_n4`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| uninit_probe::cmp3_index_range_len | SUCCESS | FAILED | 0.2196502 | 2/28 | 0 | 1/1 |
| uninit_probe::cmp3_polymorphic_sized_len | SUCCESS | FAILED | 1.7971622 | 2/142 | 6 | 2/2 |
| uninit_probe::cmp3_polymorphic_unsized_len | SUCCESS | FAILED | 1.9053743 | 2/142 | 6 | 2/2 |
| uninit_probe::cmp3_manually_drop_unsized_len | SUCCESS | SUCCESS | 1.7168927 | 0/92 | 0 | 2/2 |
| uninit_probe::cmp3_into_iter_len | SUCCESS | SUCCESS | 1.3087981 | 0/149 | 11 | 1/1 |
| uninit_probe::cmp3_into_iter_next | SUCCESS | SUCCESS | 3.0723398 | 0/254 | 12 | 3/3 |
| uninit_probe::small_sort_general_with_scratch_u8_n4 | SUCCESS | SUCCESS | 33.678715 | 0/550 | 19 | 1/1 |
| uninit_probe::pincheck_calibration_uninit_read_u8 | FAILED | FAILED | 0.5700313 | 1/30 | 0 | 3/3 |
| uninit_probe::pincheck_calibration_init_read_u8 | SUCCESS | SUCCESS | 0.61957896 | 0/31 | 0 | 3/3 |

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::cmp3_index_range_len`:
- Undefined Behavior: Reading from an uninitialized pointer of type `usize` @ /workspace/src/library/core/src/ops/index_range.rs:57
- Undefined Behavior: Reading from an uninitialized pointer of type `usize` @ /workspace/src/library/core/src/ops/index_range.rs:57

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::cmp3_polymorphic_sized_len`:
- Undefined Behavior: Reading from an uninitialized pointer of type `usize` @ /workspace/src/library/core/src/ops/index_range.rs:57
- Undefined Behavior: Reading from an uninitialized pointer of type `usize` @ /workspace/src/library/core/src/ops/index_range.rs:57

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::cmp3_polymorphic_unsized_len`:
- Undefined Behavior: Reading from an uninitialized pointer of type `usize` @ /workspace/src/library/core/src/ops/index_range.rs:57
- Undefined Behavior: Reading from an uninitialized pointer of type `usize` @ /workspace/src/library/core/src/ops/index_range.rs:57

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
- time -v max RSS 1752144 KiB exceeds the largest sampled command peak 1700952 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- -Z uninit-checks on: not in the organizers' CI flags, evidence outside CI
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::cmp3_polymorphic_sized_len
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::cmp3_polymorphic_unsized_len
- 11 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::cmp3_into_iter_len
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::cmp3_into_iter_next
- 19 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::small_sort_general_with_scratch_u8_n4
