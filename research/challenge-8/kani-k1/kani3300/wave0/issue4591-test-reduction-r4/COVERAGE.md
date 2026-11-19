# Exact seven-harness source coverage

All outcomes below are source intentions. Compile, expansion, Kani/CBMC, compiletest, native formatting and full standard CI are NOT_RUN on this candidate. Static checks give no native or independent proof credit.

P = tests/kani/FunctionContracts/ordinary_stub.rs; N = tests/kani/FunctionContracts/ordinary_stub_no_assert.rs; F = tests/expected/function-contract/ordinary_stub_fail.rs; I = tests/expected/function-contract/ordinary_stub_issue_4591.rs.

| File / exact harness | Distinct source obligation | Intended native oracle |
| --- | --- | --- |
| P / ordinary_stub | Exact reviewed A: f/requires_only/ensures_only to g, recursion-tagged target, generic u8/u16/equal input, uncontracted → requires_only → g, untouched contracted_replacement. Nine straight-line assertions. | PASS; results 10/10/10/10/2/4/5/10/11. |
| P / replacement_provider | Byte-exact selected provider Check and required verified-provider companion; one contracted_replacement(any()) call, provider requires x<16. | PASS; actual x+3 satisfies post on admitted inputs. |
| P / replacement_verified_contract | Byte-exact ordinary f to selected provider with stub_verified(contracted_replacement); f(8) uses provider Replace post. | PASS; result 11. |
| P / replacement_contract_target | Byte-exact caller-PFC with ordinary f to provider; caller requires x<16, one caller(any()) call, nested provider Assert. | PASS; actual result x+3. |
| N / ordinary_stub_original_mode | Byte-exact harness and file-wide --no-assert-contracts; replacement requires x<4 and now honestly ensures x+2. | PASS; concrete f(8)==10. |
| F / replacement_provider_postcondition | Exact reviewed B: caller-PFC, f to identity provider with requires x<4 / ensures result==0, arbitrary u8 x<=4, one caller(x). | One verification failure; both provider descriptions, VERIFICATION FAILED, exact named summary and 0/1/1 totals. |
| I / check_caller | Byte-exact issue4591 source and expected: ordinary nonnegative i32 replacement can return MAX; actual caller adds one. | One verification failure; caller.assertion overflow and named 0/1/1 summary. |

Original declarations: 38. Final declarations: 7 in four Rust files, plus two companion expected files. The overlap Rust/expected pair is deleted. Every other removal/merge follows the 38 named dispositions in committed review2ed6/COVERAGE-EDITS.md; no replacement harness or diagnostic golden was added.

For F, x=0 satisfies provider pre/post; admitted x=1 fails provider post; x=4 fails provider pre. The replacement and caller identity post perform no arithmetic, and caller result==x remains true on every returning path. This is source reasoning; future native verification must establish actual assertion reachability, mode selection and both exact failures. Compile errors, unreachable checks, coverage errors, single-top-level-call errors or caller-post failures cannot satisfy this oracle. Since F contains exactly one harness, its two failure fragments cannot come from different harnesses.

The two assertion groups each use two trailing backslashes to require three adjacent output lines. The three summary fragments are separate substring requirements. Expected-mode regression success means matching the intended failing verification output; the positive kani files require successful process exits. This behavior was read in unchanged compiletest sources, not executed. No filters, ignore/fixme markers or should_panic controls remain in these four files.
