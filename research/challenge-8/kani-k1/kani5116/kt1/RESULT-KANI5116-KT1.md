# RESULT-KANI5116-KT1 — NOT ACCEPTED; repair 2 pending exact-candidate GO
T0: 2026-11-10T20:23:42Z; main deadline 2026-11-11T01:23:42Z, closeout 01:53:42Z.
Latest completed build: 490e5e95-27ef-45a3-a4bb-7da768cdb8cc; Cloud FAILURE; summary TOOL_ERROR; gate false.
Latest built tooling commit: da417533949ff982103a53ed8385784e88d7c80e; repair 2 has not run.
Request: kani5116-kt1-repair1-20261110-02; SHA-256 da203fd87a4d229763d234ea66694102718b7ccf4e6f297e938e4cff21e7c559.
Kani pin: f046b70644e113be0df9c22c2e6ea44a65a57566; nightly-2026-10-23 unchanged.
Test-only patch SHA-256: 46c68dfd5861ebd008c32d7580caa15cee9ac9b185dec960caf57d3d342f696f.
Applied Git tree: a3822bcbbd45a864b364fc0c9fc6416cdf75da25; matches fresh local preflight, including the new fixture.
Version stdout: Kani Rust Verifier 0.68.0 (standalone), then CBMC 6.11.0; Kani profile release, compiletest profile dev.
check-tooling: PASS for pool, exact candidate lane identity, all 6 bound blobs, request/patch hashes and applied patch identity.
Schema: optional kani_patch {path,sha256}; kani-tests entries {suite,mode,file,expect,require_success,diagnostic?}.
Native argv/cwd/binary paths and release digests: structured report, read with k1g.sh native pages 0/4 and 4/1 (next_offset=null).
Tooling files changed from 9b1758ab81: tools/kani_k1.py, gcb-k1.sh, k1g.sh, test_kani_k1.py, test_gcb_native.py.
Python checks: initial 102 PASS; repair 1 103 PASS; repair 2 preparation 109 PASS plus 6 targeted excerpt tests after final clipping/provenance edits; no repair 2 build yet.
Error paths covered: unsafe/missing/hash/symlink/conflicting patch; bad/duplicate/empty/unknown selectors; wrong actual set; nonzero/timeout/kill/panic; ignored/filtered requested tests; damaged summary; foreign diagnostic; build failures; budget/deadline; upload-before-gate; old kinds.

| exact native name | expectation | native / gate result | native s / wall s | key diagnostic |
|---|---|---|---|---|
| [kani] kani/FunctionContracts/generic_fn_pointer_argument.rs | pass | ok / PASS | 2.06 / 2.273 | none required |
| [kani] kani/Stubbing/stub_set_multiple_use.rs | pass | ok / PASS | 0.51 / 0.717 | none required |
| [expected] ui/function-contracts/trait_default_fn_err.rs | pass, require_success=false | ok / PASS | 0.04 / 0.215 | cannot be applied to trait function declarations without default bodies |
| [expected] expected/function-contract/generic_default_missing_required.rs | pass, require_success=false | ok / PASS | 0.06 / 0.266 | unable to find implementation of associated function `Probe::probe` for NoDefault<T, U> |
| [kani] kani/FunctionContracts/specialization_default_fn_5116.rs | fail with expected fn diagnostic | FAILED (exit 1) / ERROR | 0.06 / 0.266 | required diagnostic absent from this test's own output |

Repro is NOT credited as EXPECTED_REPRO_FAILURE: runner did not find the required expected `fn` substring or the matching compiler-error line in its own output.
The report exports diagnostic=null and the two gate errors, but no alternative underlying error text; the reason for the different failure is not established. No raw-log fallback.
Final build times: Kani 276 s; compiletest 18 s. Five requested native names are reported once; negative expected-mode PASS does not establish Kani exit success.
First build c12af029-8eaf-4dfb-b03d-2ed52a8af2d6 at 17f6ca9848954819273097f810c16caba6a0be5e: RUNNER_ERROR; no native results exported; no retrospective test credit.
First build exposed the one-line-version bug; repair accepts bounded multiline stdout and preserves failed structured artifacts without granting credit.
Actual selected-build ledger: 2 builds, $0.2295 used, $0 reserved, within $0.80 cap (first $0.1215; final $0.1080).
New accepted tooling base for KF1/KF2: NONE; four neighbours PASS, but KT1 calibration acceptance is not achieved.
Coordinator reopened KT1 for tooling-only repair 2: bounded own-output excerpts/provenance; fixture, five selectors, production macros and library unchanged.
Repair 2 request kani5116-kt1-repair2-20261110-03: whole-job 12 min + existing overhead 30 = paid timeout 42 min; reserve $0.5670.
Used $0.2295 + proposed reserve $0.5670 = $0.7965 <= $0.80; dispatch requires fresh exact-candidate GO, with original T0/deadlines unchanged.
Limitations: subset is not full upstream CI; no B2/full-proof claim; no raw logs/archives or credentials read; first-run evidence not reconstructed.
