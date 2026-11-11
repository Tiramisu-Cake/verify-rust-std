# K-1 run `kani3300-cmp2-20261111-01`: TOOL_ERROR

- head `6f50f1fbc4a95ca21444ee9ac6f101034081cd43`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `27cdfcdf089af8dc025a90ec98e3e189701758ba4fe64f1d77ccd1dfc42421c5`
- run a13d3781-287d-4229-88d6-6b3dd1a74879 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `kani-tests`, runner `gcb-e2-standard-4`, whole-job work budget 10 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit None
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: not tracked by this lane
- Kani applied tree `e6870add67f2b1602f60ef3a623cf08139831265`, patch `17db5a0db394c5c5db8f7182fb61866df656747b17e160ead4034e03a14dbc0a`, version `Kani Rust Verifier 0.68.0 (standalone); CBMC 6.11.0`
- Kani build 236 s; compiletest build 16 s
- patch diffstat: .../delayed_ub/instrumentation_visitor.rs          |  55 +-
 .../transform/check_uninit/delayed_ub/mod.rs       |   1 +
 .../src/kani_middle/transform/check_uninit/mod.rs  | 232 ++++++-
 .../transform/check_uninit/ptr_uninit/mod.rs       |   3 +-
 .../check_uninit/ptr_uninit/uninit_visitor.rs      | 689 +++++++++++++++++----
 .../transform/check_uninit/relevant_instruction.rs |  68 +-
 .../transform/check_uninit/ty_layout.rs            | 343 +++++++++-
 library/kani_core/src/mem_init.rs                  | 110 +++-
 .../uninit/compound-cmp1-call-negative/expected    |  25 +
 .../uninit/compound-cmp1-call-negative/main.rs     | 131 ++++
 .../uninit/compound-cmp1-call-positive/main.rs     |  74 +++
 .../uninit/compound-cmp1-drop-positive/main.rs     |  59 ++
 .../uninit/compound-cmp1-empty-negative/expected   |   7 +
 .../uninit/compound-cmp1-empty-negative/main.rs    |  37 ++
 .../uninit/compound-cmp1-fields-positive/main.rs   | 106 ++++
 .../compound-cmp1-layout-unsupported/expected      |  15 +
 .../compound-cmp1-layout-unsupported/main.rs       |  88 +++
 .../compound-cmp1-no-mir-unsupported/expected      |   4 +
 .../compound-cmp1-no-mir-unsupported/main.rs       |  23 +
 .../compound-cmp1-overwrite-negative/expected      |  10 +
 .../compound-cmp1-overwrite-negative/main.rs       |  56 ++
 .../uninit/compound-cmp1-padding-negative/expected |  15 +
 .../uninit/compound-cmp1-padding-negative/main.rs  | 108 ++++
 .../uninit/compound-cmp1-positive/expected         |  18 +
 .../expected/uninit/compound-cmp1-positive/main.rs |  15 +
 .../compound-cmp1-projection-negative/expected     |  13 +
 .../compound-cmp1-projection-negative/main.rs      | 111 ++++
 .../uninit/compound-cmp1-zero-zst-positive/main.rs |  46 ++
 .../compound-cmp2-argument-negative/expected       |  10 +
 .../uninit/compound-cmp2-argument-negative/main.rs |  40 ++
 .../uninit/compound-cmp2-positive/aggregate.rs     |  16 +
 .../uninit/compound-cmp2-positive/expected         |   7 +
 .../expected/uninit/compound-cmp2-positive/main.rs |  10 +
 .../uninit/compound-cmp2-positive/manually_drop.rs |  16 +
 .../compound-cmp2-positive/ordinary_argument.rs    |  19 +
 .../compound-cmp2-positive/pointer_argument.rs     |  13 +
 .../uninit/compound-cmp2-positive/unsize.rs        |  16 +
 .../expected                                       |   4 +
 .../main.rs                                        |  30 +
 .../maybe-uninit-buffer-u3-frame-negative/expected |   9 +
 .../maybe-uninit-buffer-u3-frame-negative/main.rs  |  31 +
 .../expected                                       |   4 +
 .../main.rs                                        |  17 +
 .../maybe-uninit-buffer-u3-plain-negative/expected |   4 +
 .../maybe-uninit-buffer-u3-plain-negative/main.rs  |  23 +
 .../maybe-uninit-review-overwrite-copy/expected    |   4 +
 .../maybe-uninit-review-overwrite-copy/main.rs     |  15 +
 .../uninit/maybe-uninit-review-positive/expected   |   1 +
 .../uninit/maybe-uninit-review-positive/main.rs    | 100 +++
 .../uninit/maybe-uninit-wrap-u3-intoiter/expected  |   2 +
 .../uninit/maybe-uninit-wrap-u3-intoiter/main.rs   |  44 ++
 .../uninit/maybe-uninit-wrap-u3-padding/expected   |   4 +
 .../uninit/maybe-uninit-wrap-u3-padding/main.rs    |  21 +
 .../uninit/maybe-uninit-wrap-u3-positive/expected  |   1 +
 .../uninit/maybe-uninit-wrap-u3-positive/main.rs   |  71 +++
 .../maybe-uninit-wrap-u3-source-read/expected      |   4 +
 .../maybe-uninit-wrap-u3-source-read/main.rs       |  25 +
 57 files changed, 2831 insertions(+), 192 deletions(-)


| native test | expectation | result | wall s | diagnostic |
|---|---|---|---|---|
| [expected] expected/uninit/maybe-uninit-wrap-u3-intoiter/main.rs | pass | ERROR | 11.737 |  |
| [expected] expected/uninit/compound-cmp1-positive/main.rs | pass | ERROR | 47.165 |  |
| [expected] expected/uninit/compound-cmp1-empty-negative/main.rs | pass | PASS | 3.475 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `usize` |
| [expected] expected/uninit/compound-cmp1-overwrite-negative/main.rs | pass | PASS | 7.588 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `usize` |
| [expected] expected/uninit/compound-cmp1-call-negative/main.rs | pass | PASS | 23.538 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `usize` |
| [expected] expected/uninit/compound-cmp1-projection-negative/main.rs | pass | PASS | 11.049 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `usize` |
| [expected] expected/uninit/compound-cmp1-padding-negative/main.rs | pass | ERROR | 14.56 |  |
| [expected] expected/uninit/compound-cmp1-layout-unsupported/main.rs | pass | PASS | 3.374 | Failed Checks: Kani does not support this compound storage layout. |
| [expected] expected/uninit/compound-cmp1-no-mir-unsupported/main.rs | pass | PASS | 1.268 | Failed Checks: Kani does not support shadow-carrying arguments to calls without a MIR body. |
| [expected] expected/uninit/maybe-uninit-wrap-u3-positive/main.rs | pass | PASS | 5.331 |  |
| [expected] expected/uninit/maybe-uninit-wrap-u3-padding/main.rs | pass | PASS | 0.867 | 	 - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `u8`" |
| [expected] expected/uninit/maybe-uninit-wrap-u3-source-read/main.rs | pass | PASS | 1.218 | 	 - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `u64`" |
| [expected] expected/uninit/maybe-uninit-review-positive/main.rs | pass | PASS | 9.143 |  |
| [expected] expected/uninit/maybe-uninit-review-overwrite-copy/main.rs | pass | PASS | 1.67 | 	 - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `[u8; 2]`" |
| [expected] expected/uninit/maybe-uninit-buffer-u3-frame-negative/main.rs | pass | PASS | 129.091 | Failed Checks: Check that *var_7 is assignable |
| [expected] expected/uninit/maybe-uninit-buffer-u3-no-mir-unsupported/main.rs | pass | PASS | 0.972 | 	 - Description: "Kani does not support shadow-carrying arguments to calls without a MIR body." |
| [expected] expected/uninit/maybe-uninit-buffer-u3-plain-negative/main.rs | pass | PASS | 1.619 | 	 - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `u16`" |
| [expected] expected/uninit/maybe-uninit-buffer-u3-clause-pfc-negative/main.rs | pass | PASS | 2.171 | 	 - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `u16`" |
| [expected] expected/uninit/compound-cmp2-positive/main.rs | pass | PASS | 9.293 |  |
| [expected] expected/uninit/compound-cmp2-argument-negative/main.rs | pass | PASS | 2.973 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u32` |
- Native compiletest results; negative expected-mode PASS does not establish a successful Kani exit.
- [expected] expected/uninit/maybe-uninit-wrap-u3-intoiter/main.rs: requested native PASS did not pass
- [expected] expected/uninit/compound-cmp1-positive/main.rs: requested native PASS did not pass
- [expected] expected/uninit/compound-cmp1-padding-negative/main.rs: required diagnostic absent from this test's own output
- [expected] expected/uninit/compound-cmp1-padding-negative/main.rs: requested native PASS did not pass
