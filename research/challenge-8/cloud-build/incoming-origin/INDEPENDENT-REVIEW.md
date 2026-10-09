# Independent origin review

Reviewer built-in explorer_extent (GPT-6 Luna), read-only review of
f55e3f8a27c5cb2fc69ad0859e87f5097d844470 against75099c95. No compiler/verifier
execution. Final6cb7b6736c4ef7978d2f3a80737952ac7148cccb changes only native tests
relative to reviewed code; implementation bytes unchanged.

Specific source-call route is removed: only trusted MIR StorageLive/StorageDead
lowering constructs the internal AST tags; Rust/ghost parsing makes ordinary
ExprStmt/CallExpr. Kernel dispatch now matches tags, ordinary reserved-name calls
use ordinary resolution/specs. Diverging MIR Call has an EncodedTerminator and
zero CFG successors, so lifecycle interception no longer creates continuation.
Raw MIR ID/span fields are audit metadata; kernel authorization depends on the
trusted pinned producer and AST constructor. The retirement audit compares serialized
internal events with decoded MIR identities and relative order. Retirement control was
updated from legacy CallExpr matching to exact raw local ID, original span,
constructor and relative order. OCaml AST serialization preserves provenance;
S-expression output omits spans and is not the provenance audit channel.

No localized conservation defect found statically. StorageDead calls existing
free_locals and removes path-local binding; Drop's existing postcondition leaves
uninitialized storage that retirement consumes without calling Drop again.
Block cleanup skips the absent binding. Fresh live address is unconstrained,
allowing reuse. Context restoration is protected by do_finally. Entry authority
still requires exact same Chunk object present; no automatic restoration.

Reviewer found invalid vf__ Rust-body native test (prefix rejected before the
target); author replaced it with ordinary C prototypes in6cb7b673. Cloud must
verify it and the Rust extern/diverging route. Static review does not establish
normal/return/unwind/branch/loop closure. Broad suite and independent integration
acceptance remain gates; passing controls are not whole-model soundness proof.

Follow-up independent read-only review of proof/infra2bf268f7: default exporter
preprocessing matches verifier rust_fe invocation. FileLoader transforms source
in memory; source-byte hashes remain checked at every stage. Provenance is
correspondence to verifier-preprocessed MIR, not raw-source MIR.

Origin-call audit limitation: its sorted event comparison establishes constructor,
raw MIR local ID and original line set; it does not establish complete CFG/event
order or every local translated-name mapping. The target call operand mapping is
checked separately. This limits audit claims; reviewer identified no remaining
source-call forgery or localized lifecycle resource defect. Fresh Cloud results
must separately qualify semantics, frontend rejection, and normal/unwind paths.

Fresh author verification after review: second Cloud six span controls matched;
native C control passes. Rust extern tests remain frontend-invalid, and the live
local normal/unwind proof is INCONCLUSIVE at a resource obligation. Reviewer
source conclusions do not close these fresh semantic gates. Origin gate OPEN;
NOT_FOR_INTEGRATION. No independent acceptance or transfer has occurred.
