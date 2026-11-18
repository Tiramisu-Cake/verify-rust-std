# Regression expectations and evidence boundary

All new test executions on both main and the fixed candidate are **NOT_RUN**.
The expectations below come from source semantics and upstream test conventions.
They are review inputs, not verifier results. Counts in `.expected` files count
explicit harness declarations/outcomes; there are no property-count quotas.

| Test | Main expectation | Candidate expectation |
| --- | --- | --- |
| `tests/kani/FunctionContracts/ordinary_stub.rs` | Missing original contract closure on a reachable ordinary target; suite fails | All 19 harnesses verify |
| `tests/kani/FunctionContracts/ordinary_stub_no_assert.rs` | Missing original closure in Original mode | Ordinary replacement verifies; original PFC/verified controls retain their modes; the bad replacement's PFC is an expected panic |
| `tests/expected/function-contract/ordinary_stub_fail.rs` | Compilation error prevents the required semantic result inventory | Two providers verify, eleven named failure controls report verification failures and the pinned property descriptions appear |
| `tests/expected/function-contract/ordinary_stub_issue_4591.rs` | Missing `__kani_recursion_check_abs_val` | Compilation reaches verification; caller addition has a failing overflow property and `check_caller` fails verification |
| `tests/expected/function-contract/ordinary_stub_overlap.rs` | Missing original `f` contract closure | Same unsupported explicit-contract-target overlap diagnostic retained |

## Positive and negative semantics

The dependency-free f/g fixture keeps `requires(x < 8)`, `ensures(result ==
x + 1)`, the original `x + 1` body and the `x + 2` replacement. PFC and verified
controls exercise that same original `f`; ordinary stubbing asserts `x + 2`.
A separate ordinary harness uses `x == 8`: the safe replacement is admitted
outside the original precondition, and its result violates the original
postcondition. Requires-only and ensures-only targets use the same
distinguishable replacement; each also has PFC/verified controls. The
requires-only verified negative result check demonstrates nondeterministic
return abstraction without an ensures clause, and its precondition still
fails for `x == 8`.

The positive test covers a recursive target's ordinary replacement, recursive
PFC/verified controls, two concrete instantiations of a generic ordinary target,
an uncontracted target, multiple targets, an unstubbed contracted call in a
stubbed harness, transitive replacement, a contracted provider, a provider used
as `stub_verified`, and a provider selected by PFC while called through an
ordinary target.

The negative test pins named failed harnesses for replacement arithmetic
overflow, original verified precondition and postcondition expectations,
incorrect PFC, an unstubbed original precondition/postcondition in a harness
with ordinary mappings, replacement precondition/postcondition and the
provider-target PFC postcondition. The expected output requires actual
verification results and descriptions, so a missing-closure compilation error
cannot satisfy it. In `--no-assert-contracts` mode, a contracted replacement
runs its original body, while PFC and verified modes remain active.

The explicit same-target overlap test combines PFC, verified and ordinary
stubbing for `f`. Its error is intentionally unchanged. The source guard also
preserves verified-only overlap; this combined compile-error test supplies no
independent execution result for that separate configuration.

## Verbatim issue #4591

The Rust reproducer after the license/flag/comment header is byte-identical to
the issue's code block. In particular, `stub_abs_val` admits every nonnegative
`i32`, including `i32::MAX`, and `caller` adds one. The fixed expectation is an
overflow counterexample, not a successful proof. The original `abs_val` body
also has negation overflow at `i32::MIN`, but an active ordinary stub bypasses
that body; the required counterexample property is the caller's addition.

## Previously observed main evidence

Immutable intake:
`../stub-contract-confirm-intake/run-44380273557/RESULT.md`, intake commit
`75de8b41bcdfcd202d066e3d5cfaf514f681f9e9`, author g0 package
`5bb7ec9a01099148242421b0eb837c496e209c66`. Native run
44380273557/attempt1 had successful setup and stock compiler build. Its
ordinary invocation exited 1 with:

```text
Failed to find contract closure `__kani_recursion_check_f` in function `stub_contract_confirm::f`
```

Provider and verified controls each exited 0 with a native
`VERIFICATION:- SUCCESSFUL` marker. The retained intake's producer and
owner-policy classifications remain **INCONCLUSIVE**, including their
unretained export/count and unreachable-property limitations. Neither the
intake nor its historical records are changed or upgraded to a stricter PASS.
This observation supports the defect signature for that fixture; it supplies
no fixed-candidate result and no main execution result for the newly added
upstream tests. The old clear-error approach is superseded, and the old issue
draft is a duplicate of #4591; both statuses are recorded only in this package.
