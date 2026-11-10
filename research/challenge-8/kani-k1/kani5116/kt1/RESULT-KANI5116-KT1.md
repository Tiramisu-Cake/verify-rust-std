# RESULT-KANI5116-KT1 — ACCEPTED AS TOOLING PASS (coordinator decision)
T0: 2026-11-10T20:23:42Z; main deadline 2026-11-11T01:23:42Z, closeout 01:53:42Z.
Latest build: b85f2c4d-972a-4c05-a8ba-9052c9efdc53; Cloud FAILURE; summary TOOL_ERROR; gate false.
Approved build/tooling commit: 383fd7089550aeabac3ad92366cd7c71e2f237ee; this update changes RESULT only.
Request: kani5116-kt1-repair2-20261110-03; SHA-256 819cbf028bf6506e2a15e866a184aaba850c918df51aedb75c9f17c2a4c97e5b.
Kani pin: f046b70644e113be0df9c22c2e6ea44a65a57566; nightly-2026-10-23 unchanged.
Test-only patch SHA-256: 46c68dfd5861ebd008c32d7580caa15cee9ac9b185dec960caf57d3d342f696f.
Applied Git tree: a3822bcbbd45a864b364fc0c9fc6416cdf75da25; matches fresh local preflight, including the new fixture.
Version: Kani Rust Verifier 0.68.0 (standalone), then CBMC 6.11.0; Kani release / compiletest dev profiles.
check-tooling: PASS for pool, exact candidate lane identity, all 6 bound blobs, request/patch hashes and applied patch identity.
Schema: optional kani_patch {path,sha256}; kani-tests entries {suite,mode,file,expect,require_success,diagnostic?}; failed/expect-fail rows now include bounded output_excerpt/output_sources/diagnostic_provenance.
Evidence: k1g.sh summary/native pages 4/1 and 0/4; five requested names reported once; actual argv/cwd/binary paths/digests preserved.
Tooling changed from 9b1758ab81: tools/kani_k1.py, gcb-k1.sh, k1g.sh, test_kani_k1.py, test_gcb_native.py; no tooling change after latest GO.
Python checks: initial 102 PASS; repair 1 103 PASS; repair 2 109 PASS plus 6 targeted excerpt tests after final clipping/provenance edits.
Error paths: unsafe/missing/hash/symlink/conflicting patch; bad selectors/actual set; nonzero/timeout/kill/panic; ignored/filtered requested tests; damaged summary; foreign/console-only diagnostic; build failure; budget/deadline; upload-before-gate; old kinds; excerpt bounds/provenance/paging.

| exact native name | expectation | native / gate result | native s / wall s | key diagnostic |
|---|---|---|---|---|
| [kani] kani/FunctionContracts/generic_fn_pointer_argument.rs | pass | ok / PASS | 1.88 / 2.071 | none required |
| [kani] kani/Stubbing/stub_set_multiple_use.rs | pass | ok / PASS | 0.48 / 0.667 | none required |
| [expected] ui/function-contracts/trait_default_fn_err.rs | pass, require_success=false | ok / PASS | 0.04 / 0.215 | cannot be applied to trait function declarations without default bodies |
| [expected] expected/function-contract/generic_default_missing_required.rs | pass, require_success=false | ok / PASS | 0.05 / 0.265 | unable to find implementation of associated function `Probe::probe` for NoDefault<T, U> |
| [kani] kani/FunctionContracts/specialization_default_fn_5116.rs | fail with expected fn diagnostic | FAILED (exit 1) / ERROR | 0.06 / 0.265 | error[E0433]: cannot find `core` in the crate root |

Repro is NOT credited as EXPECTED_REPRO_FAILURE: required expected `fn` substring and matching error line are absent in all four exported source-match flags; selected_source=null.
Actual first line of own kani_stderr (.err): error[E0433]: cannot find `core` in the crate root; its tail lists E0046, E0433, E0520. The excerpt establishes the observed diagnostic; the coordinator diagnosis is recorded separately below.
Own stderr path: /workspace/src/k1-out/native-4/FunctionContracts/specialization_default_fn_5116/specialization_default_fn_5116.err; 1314 bytes; SHA-256 e7fb176060848567cf57f9aaa789c779a10997db7fe8343cf307e229120dcbf3.
Own stdout says kani-compiler exited with status 101; compiletest stdout/stderr and child .out/.err are distinct, hashed sources. Gate still reads raw .out + newline + .err only; no console/excerpt credit.
Excerpt: 19 selected source lines, 186 omitted, bounded by 60 lines / 4096 JSON bytes; diagnostic_only=true; no raw-log fallback or underlying-output reconstruction.
Build times: Kani 263 s; compiletest 16 s. Negative expected-mode native PASS does not establish successful Kani exit.
Earlier builds: c12af029-8eaf-4dfb-b03d-2ed52a8af2d6 RUNNER_ERROR (no retrospective native credit); 490e5e95-27ef-45a3-a4bb-7da768cdb8cc four PASS, repro ERROR with no actual error text exported.
Actual selected-build ledger: 3 builds, $0.3510 used, $0 reserved, within $0.80 cap (first $0.1215; repair 1 $0.1080; repair 2 $0.1215).
Accepted tooling base for KF1/KF2: 383fd7089550aeabac3ad92366cd7c71e2f237ee (coordinator acceptance; historical native statuses above remain unchanged).
Решение координатора: KT1 принят как tooling PASS, новых сборок нет; compiletest Kani по умолчанию использует edition 2015, а соседние contract-тесты задают // compile-flags: --edition 2021 (tests/kani/FunctionContracts/receiver_contracts.rs:11); поэтому compile_error! с путём ::core после parse-ошибки макроса не резолвится: E0433 маскирует expected `fn`, E0046/E0520 — те же knock-on ошибки, что в #5116; неверным было ожидание manifest, не tooling.
Repair 2 observability is demonstrated; fixture, five selectors, gate policy, production macros and library remain unchanged. No new build or fix is authorized by this RESULT.
Limitations: subset is not full upstream CI; no B2/full-proof claim; excerpts identify diagnostics, not causality; no raw logs/archives or credentials read; historical evidence unchanged.
