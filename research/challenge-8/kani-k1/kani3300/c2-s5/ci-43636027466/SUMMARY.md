# S5 candidate CI run 43636027466 (6d2e9ae621 + CI-only 61258e9c3d) — coordinator

fmt/build/clippy PASS; units 6/2/9; kani 24/0; expected 226 ok / 2 FAILED; ui 17/0; script 2/0; json-handler (all remaining upstream suites) 17/0.
Sensitivity step INVALID (coordinator bug): each mutated selector reported '1 ignored' — compiletest skipped it as unchanged; needs --force-rerun. Not a result about the oracles.

## replace-transfer.rs
```
error: test failed: expected output to contain the line(s):
Checking harness replace_transfer...
error: /home/runner/work/kani/kani/target/kani/bin/kani-compiler exited with status exit status: 101
warning: use of an unstable feature
 --> <crate attribute>:1:12
error: stub verified target `passthrough` does not have a corresponding `#[proof_for_contract]` harness
  --> /home/runner/work/kani/kani/tests/expected/uninit/contract-modes/replace-transfer.rs:34:1
error: aborting due to 1 previous error; 1 warning emitted
```
## replace-transfer-uninitialized.rs
```
error: test failed: expected output to contain the line(s):
Checking harness replace_transfer_uninitialized...
error: /home/runner/work/kani/kani/target/kani/bin/kani-compiler exited with status exit status: 101
warning: use of an unstable feature
 --> <crate attribute>:1:12
error: stub verified target `passthrough` does not have a corresponding `#[proof_for_contract]` harness
  --> /home/runner/work/kani/kani/tests/expected/uninit/contract-modes/replace-transfer-uninitialized.rs:34:1
error: aborting due to 1 previous error; 1 warning emitted
```
