# Single-owner transfer map

| Source operation | Instrumentation | Invariant |
| --- | --- | --- |
| Call resolution / operand traversal | Existing super_terminator first, shared B1 resolver | Pending entry loads/raw/union/operand checks are retained, including on refusal |
| Select validation | Exact fallback/signature/actual count+types/result/layout guard | Unsupported before call-specific Begin/Store/Load/Move clearing |
| Caller shadow args | Existing BeginArgumentTransfer; StoreArgument for all shadow args | Same instance.ty signature, count2 for MU arms, original indices2 and3; condition excluded |
| Actual Move operands | SetRef(false) only after all Stores | Both live snapshots precede clearing either source; Copy remains live |
| Callee bb0 | LoadArgument for same shadow formals | Same signature, count and original indices as caller; former intrinsic exclusion opens only validated select |
| Selected branch assignment | Existing AssignUnion/typed storage assignment in fallback | Exactly chosen arm's true/false payload state, existing padding mask; no union of initialization states |
| Callee normal Return | Existing StoreArgument index0 | Mandatory return witness for shadow result |
| Caller normal destination | Existing LoadArgument index0 After | Replaces stale destination state on normal call return; no unwind load |
| Pointer select | Ordinary body points-to analysis | Formal arguments point directly to value referents; Return joins both arm aliases to dest; bool contributes no alias; pointees not read/blessed |

Runtime buffers/protocol representations, DFCC/private assigns and masks are unchanged. Ordinary item store emission was extracted into store_call_arguments and invoked once for both ordinary items and admitted select; nonselect shims/intrinsics retain old boundaries. Actual Rust call arguments are borrowed for analysis, operands cloned into ops, all snapshots precede any Move deinit, and no dereference/cast is introduced by the classifier.

Semantic intersections for later reviewed port: C2-S3/F6 may change shadow-domain argument selection/reset for nested aggregates around this same call helper and entry/return paths. C2-S4/F7 may change analysis body overrides/cache provenance in points-to/delayed-pass; retain this classifier/body agreement while integrating. F5 descriptors, F6 resets and F7 cache fixes were not copied into SEL1. Final-C2 reviewed port plus new freeze/gates is required.
