# Select R22 response to Network P2 (`select_unpredictable` at `*mut T`)

Decision date: 2026-10-23. Pin this file by its full Select Git commit and SHA-256 together with the adjacent `P2-INTERFACE.json`. It grants Network no Cloud lane, no summary and no proof credit. It supersedes the P2 paragraph of `../select-callee-r21/NETWORK-SELECT-RESPONSE.md` only by making the publication interface exact; P1/P3 there are unchanged.

## Status: NOT_PUBLISHED

No checked `select_unpredictable` callee is published at any instantiation. The `*const Element` fractional route started from the approved candidate `288fa7cd`. In R22 it gained a parser fix, a ghost `merge_fractions` repair and fresh pins (proof candidate `dbaf41e6`). Its latest proof Build `7e23e945` still fails the positive at the function-end leak check, so its control targets are not pinned and nothing is accepted. A `*mut` source-only fixture writer exists (`overnight-helper/prepare-actual-helper-capture-mut.py`), but no `*mut` source evidence, MIR or translator certificate exists. Network's R4 generator must keep `select_spec is None` until `P2-INTERFACE.json` at a later pinned Select commit reports `"status": "PUBLISHED"`.

## What Select will publish (the exact post shape)

The published unit will be the actual std body of `select_unpredictable<T>` (exact pinned `library/core/src/hint.rs` source, unchanged runtime body and generic signature), instantiated in the fixture at `T = *mut Element` where `Element` is an unrestricted generic type parameter. The contract text is the existing pointer fixture contract with only the pointer kind changed:

```rust
pub fn select_unpredictable<Element>(condition: bool, true_val: *mut Element, false_val: *mut Element) -> *mut Element
/*@
req thread_token(?t) &*& t == currentThread;
@*/
/*@
ens thread_token(t) &*& (result as pointer) ==
    (if condition { true_val as pointer } else { false_val as pointer });
@*/
/*@
on_unwind_ens false;
@*/
```

This is the conditional result equality plus `on_unwind_ens false` that Network requested, written in the pointer-cast form of the existing const fixture contract, whose verification is still pending. Select does not publish the textual variant `ens if condition { result == true_val } else { result == false_val }`; a Network caller must either consume the exact text above or derive its own form by a checked lemma in its own proof. No equivalence between the two forms is asserted here.

The claim will cover only this raw-pointer instantiation with generic `Element`. It is not a generic-`T` summary, does not cover `T` with a panicking `Drop`, and establishes no ownership of the pointees (the resource argument is `raw_ptr_own`, which owns no pointee cell).

## Publication criteria (all required)

1. Accepted `*const Element` callee: checked positive and complete normal/unwind/nested-Drop, ownership, leak/refinement and same-site omission controls with pinned diagnostic targets, independently reviewed.
2. A separate `*mut Element` route: fresh exact original/verified source pair with ghost-strip identity, fresh MIR/unit/body/snapshot pins, and mutable-specific translator certificates under a closed opt-in. Const certifiers (`pointer_element`, `const_ptr`, `Sort4SelectIntrinsic` signatures and peers) stay const-only; nothing is inferred from the const PASS.
3. Same-version checked positive and the complete matrix for the `*mut` unit, plus refusal controls for const/mut substitution, wrong pointer depth, wrong select operand/branch result and changed source/signature/cleanup.
4. Independent review GO; `P2-INTERFACE.json` updated in a new commit with the exact Build IDs, Brief file/index identities, contract-text SHA-256, unit/source pins and tool/profile identities.

## What Network may do now

Keep P2 as a pending dependency. Network may write its consumer against the contract text above but must gate it on `status == "PUBLISHED"` and on the exact `contract_text_sha256` in a later interface record, never on this NOT_PUBLISHED one. No unchecked spec, address-only bridge, guard-own exemption or Copy/Freeze premise is authorized.
