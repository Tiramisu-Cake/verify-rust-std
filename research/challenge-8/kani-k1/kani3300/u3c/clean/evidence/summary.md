# K-1 run `kani3300-u3c-clean-20261111-01`: TOOL_ERROR

- head `08438b07d1a6dd646cd8c8b7f638ec509229b7e7`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `d8d4a877878ea44f2986be5f541d7a7ffa1eb500ea363a50718c236dc392c7bd`
- run 87c1def4-07d7-4233-84ea-5b01eda765a2 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `kani-tests`, runner `gcb-e2-standard-4`, whole-job work budget 5 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit None
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: not tracked by this lane
- Kani applied tree `97f86904b400e81c9b269cdafa957750ef741eea`, patch `8a1df0a7eeb4b449f280d521e2a563d9cb57f0936bcc29a65fb88ad2161a1dda`, version `Kani Rust Verifier 0.68.0 (standalone); CBMC 6.11.0`
- Kani build 269 s; compiletest build 18 s
- patch diffstat: .../expected                                       |  1 +
 .../main.rs                                        | 29 ++++++++++++++++++++++
 .../maybe-uninit-buffer-u3b-pfc-negative/expected  |  1 +
 .../maybe-uninit-buffer-u3b-pfc-negative/main.rs   | 29 ++++++++++++++++++++++
 .../expected                                       |  1 +
 .../main.rs                                        | 29 ++++++++++++++++++++++
 .../maybe-uninit-buffer-u3b-pfc-positive/expected  |  1 +
 .../maybe-uninit-buffer-u3b-pfc-positive/main.rs   | 29 ++++++++++++++++++++++
 .../uninit/mu-free-u3c-pfc-no-uninit/expected      |  1 +
 .../uninit/mu-free-u3c-pfc-no-uninit/main.rs       | 17 +++++++++++++
 tests/expected/uninit/mu-free-u3c-pfc/expected     |  1 +
 tests/expected/uninit/mu-free-u3c-pfc/main.rs      | 17 +++++++++++++
 tests/expected/uninit/mu-free-u3c-plain/expected   |  1 +
 tests/expected/uninit/mu-free-u3c-plain/main.rs    | 17 +++++++++++++
 14 files changed, 174 insertions(+)


| native test | expectation | result | wall s | diagnostic |
|---|---|---|---|---|
| [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-positive/main.rs | pass | ERROR | 162.497 |  |
| [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-positive-no-uninit/main.rs | pass | PASS | 3.237 | VERIFICATION:- SUCCESSFUL |
| [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-negative/main.rs | pass | PASS | 124.869 | VERIFICATION:- FAILED |
| [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-negative-no-uninit/main.rs | pass | PASS | 1.069 | VERIFICATION:- SUCCESSFUL |
| [expected] expected/uninit/mu-free-u3c-pfc/main.rs | pass | PASS | 1.471 | VERIFICATION:- SUCCESSFUL |
| [expected] expected/uninit/mu-free-u3c-pfc-no-uninit/main.rs | pass | PASS | 1.069 | VERIFICATION:- SUCCESSFUL |
| [expected] expected/uninit/mu-free-u3c-plain/main.rs | pass | PASS | 0.767 | VERIFICATION:- SUCCESSFUL |
- Native compiletest results; negative expected-mode PASS does not establish a successful Kani exit.
- [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-positive/main.rs: timeout/kill/build failure/runner panic is not a native result
- [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-positive/main.rs: required diagnostic absent from this test's own output
- [expected] expected/uninit/maybe-uninit-buffer-u3b-pfc-positive/main.rs: requested native PASS did not pass
