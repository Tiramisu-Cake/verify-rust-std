# Static coverage mapping

All rows describe source expectations for the reviewed repair. Every repaired
native outcome is NOT_RUN. These are harness counts, never property quotas.

## ordinary_stub.rs — nineteen success expectations

| Harness | Retained goal |
| --- | --- |
| provider | Same-function f PFC, both requires/ensures |
| verified_control | Same f verified contract with admitted input |
| ordinary_stub | Ordinary f→safe-u8 g returns x+2 |
| ordinary_stub_outside_target_precondition | Replacement admits input8 outside f's requires |
| requires_only_provider | Requires-only PFC |
| requires_only_verified_control | Requires-only verified selection |
| ensures_only_provider | Ensures-only PFC |
| ensures_only_verified_control | Ensures-only verified result |
| multiple_targets | Both requires-only/ensures-only ordinary targets; unstubbed f unaffected |
| recursive_provider | RecursiveCheck/REENTRY source control; outside straight-line model |
| recursive_verified_control | Recursive verified replacement |
| recursive_target | Ordinary replacement of recursive original |
| generic_instances | Two type instantiations and original-precondition-independent input |
| uncontracted_target | Uncontracted original and unchanged contracted f |
| transitive_replacement | Transitive ordinary stubs resolved to g |
| replacement_provider | Separate contracted provider PFC |
| replacement_contract | Copied and direct provider Assert semantics |
| replacement_verified_contract | Provider Replace mode through copied body |
| replacement_contract_target | Changed: one caller Check and nested ordinary provider Assert |

The first eighteen source definitions are unchanged from6f and reported
verified by the coordinator for the old same-file run, with no independently
retained named native reports. The nineteenth was the reported native failure;
its repaired success remains a source expectation.

## ordinary_stub_fail.rs — two success and eleven failure expectations

| Harness | Expected semantic outcome |
| --- | --- |
| provider | Success: f's both-clause PFC |
| requires_only_provider | Success: requires-only PFC |
| replacement_overflow | Failure: g's u8 addition overflows at MAX |
| verified_precondition | Failure: f verified requires x<8 at8 |
| verified_postcondition | Failure: false caller equality after verified f(7) |
| provider_postcondition | Failure: bad_contract PFC post x+2 on identity body |
| unstubbed_postcondition | Failure: bad_contract Assert post remains active |
| unstubbed_precondition | Failure: unstubbed f Assert requires at8 |
| replacement_postcondition | Failure: ordinary bad_contract Assert post |
| replacement_provider_postcondition | Changed: caller Check identity admits1; nested ordinary identity-provider Assert ensures0 fails |
| replacement_precondition | Failure: replacement requires x<4 at4 |
| requires_only_verified_precondition | Failure: requires-only verified requires at8 |
| requires_only_verified_result | Failure: requires-only verified return remains unconstrained |

The old expected suite was NOT_RUN. All expected text remains byte-identical;
the changed negative still requires its named semantic failure and ensures0
description. No compile-error or once-guard outcome replaces it.

## Other source files — six harnesses

| Fixture/harness | Expected outcome and scope |
| --- | --- |
| ordinary_stub_no_assert.rs / ordinary_stub_original_mode | Success: copied provider Original ignores false pre/post but computes actual body |
| ordinary_stub_no_assert.rs / provider | Success: selected f Check remains active under no-assert |
| ordinary_stub_no_assert.rs / verified_control | Success: verified Replace remains active under no-assert |
| ordinary_stub_no_assert.rs / replacement_provider | should_panic: provider PFC post failure remains active under no-assert |
| ordinary_stub_issue_4591.rs / check_caller | Semantic failure: i32::MAX admitted by replacement causes actual caller +1 overflow |
| ordinary_stub_overlap.rs / overlapping_contract_target | Existing compile-error: original-target PFC+verified+ordinary overlap; separate diagnostic control |

Old no-assert native named outcomes are UNKNOWN. Old issue/overlap expected
suite outcomes are NOT_RUN. New native outcomes are NOT_RUN for every row.

## All thirteen PFC selections

| Fixture | Harness → selected function |
| --- | --- |
| ordinary_stub.rs | provider→f; requires_only_provider→requires_only; ensures_only_provider→ensures_only; recursive_provider→recursive; replacement_provider→contracted_replacement; replacement_contract_target→replacement_caller |
| ordinary_stub_fail.rs | provider→f; provider_postcondition→bad_contract; requires_only_provider→requires_only; replacement_provider_postcondition→replacement_caller |
| ordinary_stub_no_assert.rs | provider→f; replacement_provider→replacement |
| ordinary_stub_overlap.rs | overlapping_contract_target→f |

Each harness has a real direct selected call. Recursive internals and explicit
overlap are handled by their separate existing semantics/diagnostic, not
assigned a straight-line model PASS. Only the two changed caller selections
were previously provider selections. This explicit replacement of coverage
does not prove general provider-PFC alias support. Provider Check/Replace
goals remain in separate controls; the repaired composition covers Assert
inside caller Check.
