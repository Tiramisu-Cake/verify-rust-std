> R24 supersedes the historical decision below: the active [P2 interface](P2-INTERFACE.json) is now `PUBLISHED` under the exact scoped experimental profile. See [R24 qualification](../select-callee-r24/P2-MUT-QUALIFIED-PROFILE.json) and [independent review](../select-callee-r24/R24-p2-publication-review.json). Independent proof credit remains zero; caller linkage remains a consumer obligation.

# Select R23 response to Network P2 (`select_unpredictable` at `*mut T`)

Decision date: 2026-10-23. Pin this file and the adjacent `P2-INTERFACE.json` by their full Select Git commit and SHA-256. This response grants no Network Cloud lane, no summary, and no proof credit. It carries forward the exact planned contract from R22; it does not publish that contract.

## Status: NOT_PUBLISHED

No checked `select_unpredictable` callee is published at any instantiation. The const fractional fingerprint Build `739f982d-078a-4ff5-9860-aabef75dc027` completed with exact source observations and strict eight-row pin validation. That is source-observation/fingerprint evidence, not proof: parser-input binding is not established and `body_proof_run` is false. Its Evidence Brief identities are recorded in `P2-INTERFACE.json`.

Proof Build `e25a96d4-25c0-416f-a55c-debb87baacb1` first exposed a stale cleanup-coordinate certificate. The reviewed coordinate overlay was compiled in `cf8405cc-d421-4e7a-a9cb-3fcb8b74b1c9` (source `0b2b5adc41ac803e3d72213a531d3105b2f8caaf`); this run reached the outer normal return and leak-check event, then exited 1 with dead-code reports. The terminal cause remains unresolved, and this does not establish callee acceptance or leak clearance. Seven negative diagnostics were observed on their intended obligations, without target acceptance. Exact bounded identities are in `S3-POSITIVE-TRACE-OBSERVATIONS.json`, `S3-CONTROL-OBSERVATIONS.json`, and the adjacent interface.

The mutable source-only chain at commit `17142eb2eba8e62a757e90552dffc592f79cec4e` received independent GO review in `R23-mut-delta-review.json` (SHA-256 `b567f95542d3fa0f95ecce84ba35ac7fa5199485c4b42a319201afed513c1b7a`). It remains inactive and has no actual mutable source capture, typed MIR/source binding, or mutable translator admission. Its source records explicitly leave proof NOT_RUN, publication NOT_PUBLISHED, and credit zero. The review ran 24 synthetic tests; the main run reports 30, with one additional helper test reported afterward (31 total). None of these counts is a proof result.

Network's generator must keep `select_spec is None` until a later pinned interface has `"status": "PUBLISHED"` and records the completed publication criteria below.

## Planned contract and exact bounds

The only planned claim is for the unchanged actual std runtime body and generic signature of `select_unpredictable<T>`, instantiated in the fixture at `T = *mut Element`, where `Element` remains an unrestricted generic type parameter. The contract text is the existing pointer fixture contract with only the pointer kind changed:

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

This is the conditional result equality plus `on_unwind_ens false`, in the pointer-cast form. Select does not publish the textual variant `ens if condition { result == true_val } else { result == false_val }`; Network may derive that form only through its own checked lemma. No equivalence is claimed here.

The scope is this raw-pointer instantiation with generic `Element`. It is not a generic-`T` summary, does not cover a `T` with a panicking `Drop`, and establishes no ownership of pointees. The resource argument is `raw_ptr_own`, which owns no pointee cell. The source-only mutable candidate and the const fingerprint do not establish this contract.

## Publication criteria (all required)

1. A valid accepted callee proof with the intended source/certificate binding and complete normal, unwind, nested-Drop, ownership, leak, refinement, and same-site omission controls. The current const proof exits on dead-code reports after the return/leak-check event; it does not satisfy this criterion.
2. A separate mutable route with fresh exact original/verified source, ghost-strip identity, complete source/unit/body/snapshot pins, and mutable-specific translator certificates under a closed opt-in. Const certificates and const PASS results cannot be reused as mutable evidence.
3. A same-version checked mutable positive and the complete compatible matrix, including refusal controls for const/mut substitution, wrong pointer depth, wrong select operand/branch result, and changed source, signature, or cleanup.
4. Independent review GO on the exact proof/matrix candidate and a new pinned interface commit containing actual Build IDs, Brief file/index identities, contract SHA-256, source/unit/body pins, and tool/profile identities.

Until all four criteria are met, keep this interface `NOT_PUBLISHED`, keep Network `select_spec` unset, and award zero proof credit. Network may use the planned text for design only, gated on a future `PUBLISHED` interface and its exact `contract_text_sha256`; no unchecked spec, address-only bridge, guard-own exemption, or Copy/Freeze premise is authorized.
