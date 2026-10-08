# O10 callback argument ownership transition — review before fixture edit

## Witnessed boundary

O10 (`37707814634`) passed the generic tuple-2 close/open/non-Copy-reference fixtures. The unchanged callback then reached the actual `FnMut::call_mut` at `callback_positive:88` after normal and readonly export/decode and refinement all passed, but stock `FnMut::call_mut` rejected `Args.own` for

```text
std_tuple_2_(&'cmp T, &'cmp T)
```

with actual value `mk_std_tuple_2_(fn_outcome_result(outcome0), fn_outcome_result(outcome2))`. The false-post callback failed at the same earlier obligation, so it is not an intended postcondition negative and tells us nothing about the result projection. This does not justify HRTB transfer.

The captured MIR confirms that immediately before the call it constructs the two reference values from `&*left` and `&*right`, aggregates them into a two-field tuple, and passes that tuple as the second `FnMut::call_mut` argument. The fixture already runs `init_ref_share` for both generated reference locations and retains their `ref_initialized`/borrow-debt resources. It does not call the stock checked `close_ref_own` bridge to package each pointee share as `<&'cmp T>.own`, nor explicitly close the tuple's newly structural `.own` predicate before the call. The parser transfer supplies a checked tuple constructor definition; it does not automatically create field-own resources from a reference's pointee share.

## Proposed fixture-only semantics

After both `init_ref_share` operations, call the existing stock `close_ref_own::<'cmp, T>` once for each exact reference value in both the positive and false-post fixtures. This consumes the corresponding `<T>.share('cmp, t, ref_value)` resource and returns the stock `<&'cmp T>.own(t, ref_value)` resource while preserving the thread token. Then close `<(&'cmp T, &'cmp T)>.own(t, (left_ref, right_ref))` using the reviewed exact tuple-2 field-own body. These transitions package permissions already created from the actual borrow; they do not mint `T.own`, a pointer, a reference, or a new share permission. Keep the actual comparator call expression, generic bounds, normal post and unwind post unchanged. Both fixtures must keep the same ownership setup so the false-post case tests its intended postcondition only.

The exact ref-value equality from `precreate_ref` to the source borrow temporaries remains a compiler/frontend correspondence obligation. The MIR's aggregate operands and call substitutions are the available source-bound checks. If ghost lowering cannot connect those values, treat that as a new frontend/resource boundary; do not replace it with an assumption or a synthetic tuple.

## Trust and resource boundary

`close_ref_own` is the pre-existing Rust-Belt specification bridge in the pinned stock `rust_belt/general.rsspec`: it converts an already-held shared pointee permission to the ownership predicate for that reference value. It is not a new axiom or helper body. The new tuple predicate remains ordinary generated and checked predicate code from the narrowly guarded parser patch. No kernel, prelude, translator, exporter, refiner, actual FnMut contract, or runtime source change is proposed here.

The callback may mutate legal interior state, so only current post-state permissions are preserved. On normal return the fixture retains its existing checked `recover_pair` route. On direct unwind, `FnMut::call_mut` consumes `Args.own` and returns current `F.own`, while the fixture's explicit borrow debt remains; the full target unwind post remains unchanged and must still be proved. A failure there is a later distinct blocker, not a reason to weaken the contract.

## Checks and decisions

- Rebuild the same pinned cumulative profile and keep the source/profile certificate, normal/readonly export/decode, full verifier, refinement, leak, and dead-code checks active.
- Require the callback positive to pass the actual `Args.own` precondition and report the next actual body obligation, or pass the full unchanged contract. Record the exact first new error.
- Before classifying either case, require both decoded normal and readonly MIR to show each source input flowing through its borrow local into the two-field `FnMut::Args` aggregate consumed by the exact `FnMut::call_mut`. The audit extracts balanced target-body, block, statement, tuple, and operand records, follows the actual locals structurally, and checks input locals `_1`/`_2` against the source parameter spans; it does not pin temporary-local numbers. `precreate_ref` correspondence remains within the compiler/frontend trust boundary.
- Require `callback_false_post` to fail specifically at its `false` normal post only after the actual call is discharged; otherwise classify it as inconclusive.
- Preserve exact source pair identity after ghost stripping, and verify the two actual tuple operands still correspond to the borrow references in captured MIR.
- If the next error is the `FnOnce::Output = bool` projection, that is the first evidence for a separate narrow HRTB component. If it is normal/unwind source recovery, classify that independently. Do not implement HRTB or alter the stock contract in this transfer.

## Self-review

The proposed step can only consume permissions that the checked `init_ref_share` path produced, because `close_ref_own` has those permissions in its precondition and no postcondition that creates `T.own`. The tuple close is checked against exactly two field resources. This preserves the distinction between actual reference ownership, pointee ownership, and source-cell borrow debt. The primary residual risk is that the ghost locations are not syntactically identical to the actual MIR reference temporaries; the full hosted proof and MIR capture must expose that mismatch rather than permit a handwritten equality. The transfer is limited to the diagnostic fixture and is not evidence of actual `sort4_stable` acceptance.
