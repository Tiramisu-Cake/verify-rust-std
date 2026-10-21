# R14 independent review — 2026-10-21

**Result: GO for the reviewed source-only R14 candidate.** Review is limited to static and synthetic checks. It establishes neither Cloud execution results nor proof credit.

The P1 consumer follows the current producer schema and keeps the two native-reference comparisons separate: common prototype versus the independent R-only baseline, and each current compiler-bound implementation versus its own original. It rejects stale/extra schema, non-literal gate values, incomplete compiler identities, malformed hashes/maps, changed native/header observations, and mismatched run pins. Run identity correctly uses 64-hex tool/profile SHA-256 values and 40-hex Git commit pins for proof/infra. Raw P1 source hashes are tied to the compiler inventory's source ID and generated-source hash; synthetic negative coverage includes a coordinated raw-pair/gate-hash mutation. Interface rows remain structural-only with body count zero and no proof/conformance credit.

The producer-consumer fixture now supplies the raw source-pair hashes before constructing the R-only baseline receipt. It verifies the captured pair and passes that unchanged baseline through the real AST producer, avoiding post-extraction mutation that would not model the runtime receipt binding.

R-only capture admits a terminal integer exit only. Exit 0 requires no error diagnostic; exit 1 is accepted only for the unique exact duplicate-prototype diagnostic at the unique source declaration. The collector verifies the stage-log hash, source-pair stability, and the precise source bytes used to anchor that diagnostic. The v2 receipt binds the stage, log, AST, R-only tool/translator/profile, source pair, and Build. Full AST parsing and compiler item/span checks still gate structural extraction. Timeouts, other exits, missing or mismatched logs/AST, stale destinations, source mutation, malformed receipts, stage exceptions, and truncated AST remain fail-closed. The accepted R-only capture is explicitly structural-only.

The R14 profile/entry/runner and lane route preserve the existing A1 protocol and R13 historical route. The seven-row mini-preflight must complete before canonical R14 target/full-matrix continuation; its result cannot substitute for P1 or matrix admission. The recipe includes the current R14 profile and adapters while retaining the existing R13 implementation chain. The compressed-archive cap is checked against the complete `.tar.gz` before upload; an over-cap archive is left intact, gets a compact size/limit diagnostic, and fails through the existing packaging-error path, whose bounded primary error preserves the measured size.

## Exact reviewed files

SHA-256 values identify the reviewed snapshot:

- `a1-matrix-classifier.py` — `a486599a43d16a62cba9100e913587c3ef997dafc6f885011fec73b7f40b42ed`
- `test_a1_p1_producer_classifier.py` — `1244120dd43a79b2fb04b2bc034d6abb55d73925deb3e658dda6ffbbc27daa47`
- `A1-R14-P1-SCHEMA-DESIGN-2026-10-21.md` — `5adf21fa52acf440b3cce1d14c13b0036392fc0325a95664726c0066e8e829bb`
- `a1-runner.py` — `0d9682f9125f667250e250af9f3a47c0ff95af9ccf6ff86d08523acf033524a3`
- `a1-ast-gates.py` — `c3089e41380b5ec2fb71c03126c23e537dfbb740de3bb5b9695567b0ec579c44`
- `test_a1_r10_r_only_source_pair.py` — `ea3aaceaf6001d7d384545bfbfaeb8189f22e38a810e171298c4b2cef2aaae52`
- `test_a1_ast_gates.py` — `933a7a9d39f6157fd553719b67186da463f4da2c7fd2caba595753faa4195b2e`
- `test_a1_r14_dependencies.py` — `a3fbd4c58c24653ed60904cc26b5ea9c7f20d1222e04c3692ed809532bccaff3`
- `test_a1_r14_registration.py` — `d9a326b56a7ec3671483fff0837386f511919cdc4db61242a0dd7561da2bba34`
- `A1-NATIVE-MATRIX-R14-PROFILE-2026-10-21.json` — `87849fdd9de677683f8c6bf738efb3d95c02ca71e5d6bb25508019908f058fbb`
- `a1-entry-r14.py` — `e690e0037d3078e14c4528006aa5d4999fa676d82633ec99035eff4450a68a79`
- `a1-runner-r14.py` — `2ef451df66774cf62925c474f50619679e3a0a27cd19e8dfa9ef0de1bddde10c`
- `run-sort4-c1-current-recovery.sh` — `00117b432987d02d45974c3d2e25b1aa8ebd281941047d0ad3726dd6b6ac3281`
- `control.py` — `328cd9c6d73dbd8c3f05e434a6029f8fb9176003db3d2ff417c5cb6ddebfaf25`
- `recipes/o26-sort4-c1-current-recovery.json` — `ba51eff19c9e117cc602383f39cfda1af327cadc8c37fdf521c4faa8b3f866ab`
- `package-evidence.py` — `6cff687d994b02ee8a1ce2adedf2be660aca17c7ee239ded5f740527c7c94781`
- `test-package-archive-limit.py` — `536153feb9094dc5989fa00b9028065dadab7243bf5a4024c218ea7ff695b3b8`
- `test-package-upload-diagnostics.py` — `286281a281136cfb4c263dd23751cfeedebe94cd9847ab97063410b2bb7aa5db`

## Validation

- `python -m unittest test_a1_ast_gates test_a1_p1_producer_classifier test_a1_matrix_classifier test_a1_r10_r_only_source_pair` — 70 passed after the final fixture update.
- `python -m unittest test_a1_r14_dependencies test_a1_r14_registration` — 7 passed.
- `python -m unittest test-package-archive-limit test-package-upload-diagnostics` — 9 passed.

No local compiler, exporter, decoder, refiner, verifier, preparer, or Cloud Build was run as part of this review.
