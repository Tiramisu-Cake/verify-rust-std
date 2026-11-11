# K-1 run `kani3300-u3b-20261111-02`: TOOL_ERROR

- head `a3e082da37f65095f85ebf998170775d7b75db9c`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `f839b593b08b53953a408528e8833d54be50dc9abff281c27291e18c09b46f4a`
- run 9f964706-4b89-4340-a1ee-022aa23ecbe9 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `kani-tests`, runner `gcb-e2-standard-4`, whole-job work budget 10 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit None
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: not tracked by this lane
- Kani applied tree `4de67d7ead14bdc4060d2b08060e7ee7651625bb`, patch `d9417e68ec3ee9c8c27bb8e7ac829e2af712c4d124ac59078416ab34feebd85c`, version `Kani Rust Verifier 0.68.0 (standalone); CBMC 6.11.0`
- Kani build 248 s; compiletest build 17 s
- patch diffstat: .../transform/check_uninit/delayed_ub/mod.rs       |   1 +
 .../src/kani_middle/transform/check_uninit/mod.rs  | 106 +++-
 .../transform/check_uninit/ptr_uninit/mod.rs       |   3 +-
 .../check_uninit/ptr_uninit/uninit_visitor.rs      | 533 ++++++++++++++++-----
 .../transform/check_uninit/relevant_instruction.rs |  59 ++-
 .../transform/check_uninit/ty_layout.rs            |  41 +-
 library/kani_core/src/mem_init.rs                  | 110 +++--
 .../maybe-uninit-buffer-u3-frame-negative/expected |   9 +
 .../maybe-uninit-buffer-u3-frame-negative/main.rs  |  31 ++
 .../maybe-uninit-buffer-u3-plain-negative/expected |   4 +
 .../maybe-uninit-buffer-u3-plain-negative/main.rs  |  23 +
 .../expected                                       |   2 +
 .../main.rs                                        |  29 ++
 .../maybe-uninit-buffer-u3b-pfc-negative/expected  |   3 +
 .../maybe-uninit-buffer-u3b-pfc-negative/main.rs   |  29 ++
 .../expected                                       |   2 +
 .../main.rs                                        |  29 ++
 .../maybe-uninit-buffer-u3b-pfc-positive/expected  |   2 +
 .../maybe-uninit-buffer-u3b-pfc-positive/main.rs   |  29 ++
 .../maybe-uninit-review-overwrite-copy/expected    |   4 +
 .../maybe-uninit-review-overwrite-copy/main.rs     |  15 +
 .../uninit/maybe-uninit-review-positive/expected   |   1 +
 .../uninit/maybe-uninit-review-positive/main.rs    | 100 ++++
 .../uninit/maybe-uninit-wrap-u3-positive/expected  |   1 +
 .../uninit/maybe-uninit-wrap-u3-positive/main.rs   |  71 +++
 25 files changed, 1059 insertions(+), 178 deletions(-)


| native test | expectation | result | wall s | diagnostic |
|---|---|---|---|---|
| [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-positive/main.rs | pass | ERROR | 50.284 |  |
| [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-positive-no-uninit/main.rs | pass | PASS | 5.4 |  |
| [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-negative/main.rs | pass | ERROR | 51.35 |  |
| [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-negative-no-uninit/main.rs | pass | PASS | 5.107 |  |
| [expected] expected/uninit/maybe-uninit-buffer-u3-frame-negative/main.rs | pass | PASS | 124.419 | Failed Checks: Check that *var_7 is assignable |
| [expected] expected/uninit/maybe-uninit-wrap-u3-positive/main.rs | pass | PASS | 6.037 |  |
| [expected] expected/uninit/maybe-uninit-buffer-u3-plain-negative/main.rs | pass | PASS | 1.62 | 	 - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `u16`" |
| [expected] expected/uninit/maybe-uninit-review-positive/main.rs | pass | PASS | 9.85 |  |
| [expected] expected/uninit/maybe-uninit-review-overwrite-copy/main.rs | pass | PASS | 1.771 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `[u8; 2]` |
- Native compiletest results; negative expected-mode PASS does not establish a successful Kani exit.
- [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-positive/main.rs: requested native PASS did not pass
- [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-negative/main.rs: required diagnostic absent from this test's own output
- [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-negative/main.rs: requested native PASS did not pass
