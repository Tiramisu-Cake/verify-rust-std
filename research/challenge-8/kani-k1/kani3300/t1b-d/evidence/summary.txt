# K-1 run `kani3300-t1b-a2-20261111-01`: COMPLETE

- head `bddfa044cbb4e884f9140b51c0cc0b9dfc464e58`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `73903bb3f80c34492d575d40d74a4552e4e2d9a55149e578fe05dde01d55035e`
- run cbf4045a-cf4b-4ac7-8495-dfafcf57f6fb attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 2 min, harnesses in parallel 1, uninit checks on, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1754256 KiB, wall 1:53.45 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- Kani applied tree `53927d9bc0ccbff8183aa91ffb6c29d1c8a74465`, patch `0e1dd370789a196cf7f7eadad4fe850910f83fd38cbf6e306394c6c247588298`, version `Kani Rust Verifier 0.68.0 (standalone); CBMC 6.11.0`
- Kani build 252 s; compiletest build 0 s
- patch diffstat: .../codegen_cprover_gotoc/compiler_interface.rs    |  86 ++-
 kani-compiler/src/kani_middle/codegen_order.rs     |   7 +
 kani-compiler/src/kani_middle/mod.rs               |   1 +
 kani-compiler/src/kani_middle/trace.rs             | 508 +++++++++++++++
 .../delayed_ub/initial_target_visitor.rs           |  53 +-
 .../delayed_ub/instrumentation_visitor.rs          | 102 ++-
 .../transform/check_uninit/delayed_ub/mod.rs       |  69 ++-
 .../src/kani_middle/transform/check_uninit/mod.rs  | 305 ++++++++-
 .../transform/check_uninit/ptr_uninit/mod.rs       |   3 +-
 .../check_uninit/ptr_uninit/uninit_visitor.rs      | 689 +++++++++++++++++----
 .../transform/check_uninit/relevant_instruction.rs |  68 +-
 .../transform/check_uninit/ty_layout.rs            | 343 +++++++++-
 kani-compiler/src/kani_middle/transform/mod.rs     |  93 ++-
 library/kani_core/src/mem_init.rs                  | 110 +++-
 14 files changed, 2201 insertions(+), 236 deletions(-)
- memory peaks PARSED: sampled every 2 s, 58 samples, largest sampled sum of RSS 2.23 GiB at 58 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.67 GiB (≤13 GiB), seen 2–66 s, peak sample 58 s
  - `kani-driver` 0.83 GiB (≤13 GiB), seen 2–112 s, peak sample 112 s
  - `cbmc` 0.34 GiB (≤13 GiB), seen 70–110 s, peak sample 96 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 60 s
  - `python3` 0.03 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `goto-instrument` 0.02 GiB (≤13 GiB), seen 68–112 s, peak sample 68 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–113 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–112 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–112 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–113 s, peak sample 0 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 112–112 s, peak sample 112 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–112 s, peak sample 2 s
  - simultaneous cbmc RSS 0.33 GiB at 102 s
  - simultaneous driver RSS 0.61 GiB at 112 s
  - cbmc PID 8917: 0.34 GiB peak at 96 s; active `T0:uninit_probe::small_sort_general_with_scratch_u8_n4`
  - cbmc PID 8765: 0.07 GiB peak at 70 s; active ``
  - cbmc PID 8840: 0.05 GiB peak at 76 s; active `T0:uninit_probe::cmp3_manually_drop_unsized_len`
  - cbmc PID 8865: 0.05 GiB peak at 78 s; active `T0:uninit_probe::cmp3_polymorphic_unsized_len`
  - cbmc PID 8815: 0.05 GiB peak at 74 s; active `T0:uninit_probe::cmp3_into_iter_len`
  - cbmc PID 8790: 0.04 GiB peak at 72 s; active `T0:uninit_probe::cmp3_into_iter_next`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| uninit_probe::cmp3_index_range_len | SUCCESS | FAILED | 0.20675407 | 2/28 | 0 | 1/1 |
| uninit_probe::cmp3_polymorphic_sized_len | SUCCESS | FAILED | 1.7679496 | 2/142 | 6 | 2/2 |
| uninit_probe::cmp3_polymorphic_unsized_len | SUCCESS | FAILED | 1.7076207 | 2/142 | 6 | 2/2 |
| uninit_probe::cmp3_manually_drop_unsized_len | SUCCESS | SUCCESS | 1.475718 | 0/92 | 0 | 2/2 |
| uninit_probe::cmp3_into_iter_len | SUCCESS | SUCCESS | 1.1371077 | 0/149 | 11 | 1/1 |
| uninit_probe::cmp3_into_iter_next | SUCCESS | SUCCESS | 2.8858182 | 0/254 | 12 | 3/3 |
| uninit_probe::small_sort_general_with_scratch_u8_n4 | SUCCESS | SUCCESS | 31.045666 | 0/550 | 19 | 1/1 |
| uninit_probe::pincheck_calibration_uninit_read_u8 | FAILED | FAILED | 0.52246827 | 1/30 | 0 | 3/3 |
| uninit_probe::pincheck_calibration_init_read_u8 | SUCCESS | SUCCESS | 0.5395817 | 0/31 | 0 | 3/3 |

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
- `research/challenge-8/kani-k1/tools/diagnostic_trace.py` 0fe9ba94febceb919beab22da4f29fd8057765941c9d1f23b0222234fd73b49e
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` e45ccf9a2b4fddadeb78037293468f7e537865303abf7f7ec72fbe897a270246
- `research/challenge-8/kani-k1/tools/k1g.sh` 52612fefa011f88a42bbc3f5f7c29e6b79f6de73f72a205c1592185afadf64a2
- `research/challenge-8/kani-k1/tools/kani_k1.py` 707a8ca8ddcbcfd3127598a7c4b30ccde72b3454d6e1526bbd16c4bacce4b573
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 7dca0aa5bf9467c6c4fb4323dabc12254f6372f5f01af096420583bc2b5c9ca3

Notes:
- time -v max RSS 1754256 KiB exceeds the largest sampled command peak 1750612 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- -Z uninit-checks on: not in the organizers' CI flags, evidence outside CI
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::cmp3_polymorphic_sized_len
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::cmp3_polymorphic_unsized_len
- 11 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::cmp3_into_iter_len
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::cmp3_into_iter_next
- 19 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::small_sort_general_with_scratch_u8_n4
