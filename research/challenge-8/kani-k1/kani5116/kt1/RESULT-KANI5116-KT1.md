# RESULT-KANI5116-KT1 — calibration 1 failed; repair pending GO
T0: 2026-11-10T20:23:42Z; main deadline 2026-11-11T01:23:42Z, closeout 01:53:42Z.
Build: c12af029-8eaf-4dfb-b03d-2ed52a8af2d6; Cloud FAILURE; structured summary RUNNER_ERROR; gate false.
Approved candidate: 17f6ca9848954819273097f810c16caba6a0be5e.
Kani pin: f046b70644e113be0df9c22c2e6ea44a65a57566; nightly-2026-10-23 unchanged.
Test-only patch SHA-256: 46c68dfd5861ebd008c32d7580caa15cee9ac9b185dec960caf57d3d342f696f.
Applied tree: not established by this run's exported summary; local preflight expectation a3822bcbbd45a864b364fc0c9fc6416cdf75da25.
Request SHA-256: 7f6dc49b2a3e89d534bae4ac1b66b48d8094ef233775af651c2075a44017792b; candidate request/patch hashes match.
check-tooling: pool, candidate lane identity and all 6 bound blobs PASS; overall FAIL because applied identity is absent.
Native evidence read: k1g.sh native returned 'no structured native report'; no per-test result can be credited.
Source/code finding: pinned version.rs prints Kani plus CBMC on separate lines; runner wrongly required one line.
Historical field bytes were not exported, so this explains a code defect, not an independently recovered historical version value.
Schema: optional kani_patch {path,sha256}; kani-tests uses typed {suite,mode,file,expect,require_success,diagnostic?} entries.
Tooling files: tools/kani_k1.py, gcb-k1.sh, k1g.sh, test_kani_k1.py, test_gcb_native.py.
Python checks: initial 102 PASS; repair 103 PASS, including real multiline-version service coverage and fail-closed diagnostic paging.
| test | expectation | result | time | diagnostic |
|---|---|---|---|---|
| kani/FunctionContracts/generic_fn_pointer_argument.rs | native PASS | NOT_ESTABLISHED | unavailable | unavailable |
| kani/Stubbing/stub_set_multiple_use.rs | native PASS | NOT_ESTABLISHED | unavailable | unavailable |
| ui/function-contracts/trait_default_fn_err.rs | native PASS | NOT_ESTABLISHED | unavailable | unavailable |
| expected/function-contract/generic_default_missing_required.rs | native PASS | NOT_ESTABLISHED | unavailable | unavailable |
| kani/FunctionContracts/specialization_default_fn_5116.rs | expected fn repro failure | NOT_ESTABLISHED | unavailable | unavailable |
Kani/compiletest build times: unavailable in exported summary; build_outcome=success is source-reported, not per-test evidence.
Actual selected-build ledger: 1 build, $0.1215 used, $0 reserved (9 rounded billed minutes at lane rate).
Repair request: kani5116-kt1-repair1-20261110-02; unchanged selectors/patch/pin/tree expectation; whole-job 20 min, paid timeout 50 min.
Repair reservation: $0.6750; cumulative used + proposed reserve $0.7965 <= $0.80; dispatch requires new exact-SHA GO.
New accepted tooling base for KF1/KF2: NONE; KT1 acceptance is not achieved.
Limitations: no raw logs/archives read; no reconstruction of lost native results; subset is not full upstream CI.
