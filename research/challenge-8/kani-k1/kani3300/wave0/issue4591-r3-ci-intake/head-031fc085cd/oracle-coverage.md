# Named source-oracle coverage

Exact source head `031fc085cd4373b5fc93a55128d5a69fdbd88df1`; reviewed tree `2ff34bc99ec3fe63579202c196f0ca288e318919`. Oracle SHA256 `a0ea77ec172fb21f23238c21af6b18712de71b5ddc1a2bdb3b6759fa30b694de` at author5162af47e12611de4102ba20b0135b17c1d79d7d; independent static review19079d13154e3b814a3abeca9d9b38f0188b731d APPROVE.

All38 declaration/attribute locations match. The workflow calls stock kani-regression.sh; its15-suite loop includes kani/kani and expected/expected. The compiletest collector recursively discovers the five .rs files; expected-mode output matches unchanged .expected fragments. This is static discovery. The native API exposes successful enclosing regression steps on five OS instances; it exposes no individual suite, file, harness or property result. Every current named outcome below is UNKNOWN, not NOT_RUN.

| Source file | Source harnesses | Native named outcomes |
| --- | --- | --- |
| tests/expected/function-contract/ordinary_stub_fail.rs | 13 | UNKNOWN |
| tests/expected/function-contract/ordinary_stub_issue_4591.rs | 1 | UNKNOWN |
| tests/expected/function-contract/ordinary_stub_overlap.rs | 1 | UNKNOWN |
| tests/kani/FunctionContracts/ordinary_stub.rs | 19 | UNKNOWN |
| tests/kani/FunctionContracts/ordinary_stub_no_assert.rs | 4 | UNKNOWN |

| File / harness (attribute line) | Reviewed source expectation |
| --- | --- |
| ordinary_stub_fail.rs / provider (15) | VERIFICATION_SUCCESS |
| ordinary_stub_fail.rs / replacement_overflow (20) | VERIFICATION_FAILURE |
| ordinary_stub_fail.rs / verified_precondition (26) | VERIFICATION_FAILURE |
| ordinary_stub_fail.rs / verified_postcondition (32) | VERIFICATION_FAILURE |
| ordinary_stub_fail.rs / provider_postcondition (43) | VERIFICATION_FAILURE |
| ordinary_stub_fail.rs / unstubbed_postcondition (48) | VERIFICATION_FAILURE |
| ordinary_stub_fail.rs / unstubbed_precondition (54) | VERIFICATION_FAILURE |
| ordinary_stub_fail.rs / replacement_postcondition (60) | VERIFICATION_FAILURE |
| ordinary_stub_fail.rs / replacement_provider_postcondition (77) | VERIFICATION_FAILURE |
| ordinary_stub_fail.rs / replacement_precondition (88) | VERIFICATION_FAILURE |
| ordinary_stub_fail.rs / requires_only_provider (99) | VERIFICATION_SUCCESS |
| ordinary_stub_fail.rs / requires_only_verified_precondition (104) | VERIFICATION_FAILURE |
| ordinary_stub_fail.rs / requires_only_verified_result (110) | VERIFICATION_FAILURE |
| ordinary_stub_issue_4591.rs / check_caller (22) | VERIFICATION_FAILURE_CALLER_OVERFLOW |
| ordinary_stub_overlap.rs / overlapping_contract_target (17) | COMPILE_ERROR_ORIGINAL_CONTRACT_CLOSURE |
| ordinary_stub.rs / provider (17) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / verified_control (22) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / ordinary_stub (30) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / ordinary_stub_outside_target_precondition (38) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / requires_only_provider (54) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / requires_only_verified_control (59) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / ensures_only_provider (65) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / ensures_only_verified_control (70) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / multiple_targets (76) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / recursive_provider (92) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / recursive_verified_control (97) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / recursive_target (103) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / generic_instances (119) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / uncontracted_target (131) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / transitive_replacement (138) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / replacement_provider (152) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / replacement_contract (157) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / replacement_verified_contract (164) | VERIFICATION_SUCCESS |
| ordinary_stub.rs / replacement_contract_target (177) | VERIFICATION_SUCCESS |
| ordinary_stub_no_assert.rs / ordinary_stub_original_mode (17) | VERIFICATION_SUCCESS |
| ordinary_stub_no_assert.rs / provider (23) | VERIFICATION_SUCCESS |
| ordinary_stub_no_assert.rs / verified_control (28) | VERIFICATION_SUCCESS |
| ordinary_stub_no_assert.rs / replacement_provider (34) | EXPECTED_PANIC_POSTCONDITION |

Contract coverage includes requires-only, ensures-only and both clauses; safeu8 plain and contracted replacements; same-function PFC/stub_verified; recursion, generic instances, transitive stubs, multiple targets and uncontracted targets. Negative safety/pre/post controls and no-assert Original behavior are retained. Source details and historical6f assurance are separate fields per row in oracle-coverage.json.

Positive replacement_contract_target selects replacement_caller Check and calls it once. The caller and nested contracted_replacement require x<16 and ensure result=x+3. All admitted u8 inputs produce3..18 without overflow, including8..15 outside the original target precondition. Nested provider Assert is a static mode prediction.

Negative replacement_provider_postcondition also selects replacement_caller once. Input1 returns1; the caller identity post passes, while discriminating_replacement ensures0 fails in nested Assert. The unchanged golden requires the ensures0 failure description, named harness failure and2success/11failure/13total harness summary. Actual native named/property evidence is UNKNOWN. These counts describe harness expectations, not property quotas.

The repair replaces the old sequential provider-PFC direct+copied pattern. No universal mixed-alias provider-PFC coverage is claimed. Separate replacement_provider and replacement_verified_contract preserve provider Check and Replace controls. Explicit original-target PFC+verified+ordinary overlap remains an unchanged compile-error control with no semantic proof credit.

Verbatim check_caller for issue4591 permits replacement i32::MAX: compilation should succeed, then caller +1 should yield an overflow counterexample. Current compile/property detail is UNKNOWN. Its expected failure is not a fake verifier PASS.

To strengthen named claims, the bounded evidence would need exact-head structured harness outcomes and discriminating property diagnostics, including successful compilation for the reproducer and positive/negative caller-PFC cases, plus source/binary/input identities. None is exposed by the permitted metadata/check summaries. This is an evidence limit, not authorization to run CI or obtain raw logs.
