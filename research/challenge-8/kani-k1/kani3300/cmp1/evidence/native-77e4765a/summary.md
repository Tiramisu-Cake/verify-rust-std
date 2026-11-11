# K-1 run `kani3300-cmp1-20261111-02`: TOOL_ERROR

- head `66881e0c52d010af94403a9bcf6dd7775b1d7cfb`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `49fb4a6df2268219dd96b29febb4c598b1490e5bc726773760e819949851b53e`
- run 77e4765a-d82a-48c8-bf2e-cb6ae2fcdc07 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `kani-tests`, runner `gcb-e2-standard-4`, whole-job work budget 10 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit None
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: not tracked by this lane
- Kani applied tree `4c0c56b2808adb542f6e58a59f4672fdc89b439c`, patch `e216f41ca8887c85e19ba84ee56fc6581ee5b95f68ad982e111c5f1b0ca19183`, version `Kani Rust Verifier 0.68.0 (standalone); CBMC 6.11.0`
- Kani build 252 s; compiletest build 16 s
- patch diffstat: .../transform/check_uninit/delayed_ub/mod.rs       |   1 +
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
 .../uninit/compound-cmp1-padding-negative/main.rs  | 106 ++++
 .../uninit/compound-cmp1-positive/expected         |  18 +
 .../expected/uninit/compound-cmp1-positive/main.rs |  15 +
 .../compound-cmp1-projection-negative/expected     |  13 +
 .../compound-cmp1-projection-negative/main.rs      | 111 ++++
 .../uninit/compound-cmp1-zero-zst-positive/main.rs |  46 ++
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
 47 files changed, 2640 insertions(+), 179 deletions(-)


| native test | expectation | result | wall s | diagnostic |
|---|---|---|---|---|
| [expected] expected/uninit/maybe-uninit-wrap-u3-intoiter/main.rs | pass | ERROR | 12.104 |  |
| [expected] expected/uninit/compound-cmp1-positive/main.rs | pass | ERROR | 49.032 |  |
| [expected] expected/uninit/compound-cmp1-empty-negative/main.rs | pass | PASS | 3.727 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `usize` |
| [expected] expected/uninit/compound-cmp1-overwrite-negative/main.rs | pass | PASS | 7.791 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `usize` |
| [expected] expected/uninit/compound-cmp1-call-negative/main.rs | pass | PASS | 24.949 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `usize` |
| [expected] expected/uninit/compound-cmp1-projection-negative/main.rs | pass | PASS | 11.804 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `usize` |
| [expected] expected/uninit/compound-cmp1-padding-negative/main.rs | pass | ERROR | 15.468 |  |
| [expected] expected/uninit/compound-cmp1-layout-unsupported/main.rs | pass | PASS | 3.576 | Failed Checks: Kani does not support this compound storage layout. |
| [expected] expected/uninit/compound-cmp1-no-mir-unsupported/main.rs | pass | PASS | 1.319 | Failed Checks: Kani does not support shadow-carrying arguments to calls without a MIR body. |
| [expected] expected/uninit/maybe-uninit-wrap-u3-positive/main.rs | pass | PASS | 5.633 |  |
| [expected] expected/uninit/maybe-uninit-wrap-u3-padding/main.rs | pass | PASS | 0.867 | 	 - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `u8`" |
| [expected] expected/uninit/maybe-uninit-wrap-u3-source-read/main.rs | pass | PASS | 1.269 | 	 - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `u64`" |
| [expected] expected/uninit/maybe-uninit-review-positive/main.rs | pass | PASS | 9.546 |  |
| [expected] expected/uninit/maybe-uninit-review-overwrite-copy/main.rs | pass | PASS | 1.77 | 	 - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `[u8; 2]`" |
| [expected] expected/uninit/maybe-uninit-buffer-u3-frame-negative/main.rs | pass | PASS | 147.136 | Failed Checks: Check that *var_7 is assignable |
| [expected] expected/uninit/maybe-uninit-buffer-u3-no-mir-unsupported/main.rs | pass | PASS | 1.671 | 	 - Description: "Kani does not support shadow-carrying arguments to calls without a MIR body." |
| [expected] expected/uninit/maybe-uninit-buffer-u3-plain-negative/main.rs | pass | PASS | 1.721 | 	 - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `u16`" |
| [expected] expected/uninit/maybe-uninit-buffer-u3-clause-pfc-negative/main.rs | pass | PASS | 2.474 | 	 - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `u16`" |
- Native compiletest results; negative expected-mode PASS does not establish a successful Kani exit.
- [expected] expected/uninit/maybe-uninit-wrap-u3-intoiter/main.rs: requested native PASS did not pass
- [expected] expected/uninit/compound-cmp1-positive/main.rs: requested native PASS did not pass
- [expected] expected/uninit/compound-cmp1-padding-negative/main.rs: required diagnostic absent from this test's own output
- [expected] expected/uninit/compound-cmp1-padding-negative/main.rs: requested native PASS did not pass

