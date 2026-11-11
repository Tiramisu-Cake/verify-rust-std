# K-1 run `kani3300-u3c-u1-20261111-01`: INCONSISTENT

- head `6ee847b331186ed558375ba2d350646061b6ca8a`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `cce17bc34ab85fc5467689ac48403c6340cb607ea590743e96ebad0a246b2a4d`
- run 36f4b5c4-c9fc-4f44-b9d0-537889168954 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `kani-tests`, runner `gcb-e2-standard-4`, whole-job work budget 5 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit None
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: not tracked by this lane
- Kani applied tree `8ebcafd3e90f32fe7b5586d7a0d2f3ea6ddb360e`, patch `c462f297d25297b69bdd0c99b520772a7906700c5886a0118e77ed83efbcc981`, version `Kani Rust Verifier 0.68.0 (standalone); CBMC 6.11.0`
- Kani build 260 s; compiletest build 17 s
- patch diffstat: .../transform/check_uninit/delayed_ub/mod.rs       |   1 +
 .../src/kani_middle/transform/check_uninit/mod.rs  | 106 ++++-
 .../transform/check_uninit/ptr_uninit/mod.rs       |   3 +-
 .../check_uninit/ptr_uninit/uninit_visitor.rs      | 476 ++++++++++++++++-----
 .../transform/check_uninit/relevant_instruction.rs |  59 ++-
 .../transform/check_uninit/ty_layout.rs            |  41 +-
 library/kani_core/src/mem_init.rs                  |  12 +-
 .../expected                                       |   1 +
 .../main.rs                                        |  29 ++
 .../maybe-uninit-buffer-u3b-pfc-negative/expected  |   1 +
 .../maybe-uninit-buffer-u3b-pfc-negative/main.rs   |  29 ++
 .../expected                                       |   1 +
 .../main.rs                                        |  29 ++
 .../maybe-uninit-buffer-u3b-pfc-positive/expected  |   1 +
 .../maybe-uninit-buffer-u3b-pfc-positive/main.rs   |  29 ++
 .../uninit/mu-free-u3c-pfc-no-uninit/expected      |   1 +
 .../uninit/mu-free-u3c-pfc-no-uninit/main.rs       |  17 +
 tests/expected/uninit/mu-free-u3c-pfc/expected     |   1 +
 tests/expected/uninit/mu-free-u3c-pfc/main.rs      |  17 +
 tests/expected/uninit/mu-free-u3c-plain/expected   |   1 +
 tests/expected/uninit/mu-free-u3c-plain/main.rs    |  17 +
 21 files changed, 722 insertions(+), 150 deletions(-)

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|

Inconsistencies:
- native timing missing/corrupt

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` d51f9c59823339dfd211e0e1226e6a372f4816d2ef6c86a68cce2676dc796215
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 60af9d2e9f2d704ed66e6201cfc990662e000d860a230967ab64ec0e20801897
- `research/challenge-8/kani-k1/tools/kani_k1.py` 2a1b6d7a20af9b3c0296d9dc435cb7f12585ce16e27add45f10b9902e35fee23
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 7dca0aa5bf9467c6c4fb4323dabc12254f6372f5f01af096420583bc2b5c9ca3

Notes:
- Native compiletest results; negative expected-mode PASS does not establish a successful Kani exit.
