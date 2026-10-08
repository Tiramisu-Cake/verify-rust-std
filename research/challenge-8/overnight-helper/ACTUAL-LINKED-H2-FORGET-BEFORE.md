# Actual nested guard and SAFE forget: integration boundary before patch

O17 (`37717092130`, `11d888ba`) passed the independent pointer-value
post-completion lemma and entered the actual helper under a compatible post.
Its first body error was missing `MaybeUninit::<T>::new` because that source
unit lacked the separately checked S6 callee bodies. This is a linkage
setup failure, not an ownership proof result. O16 showed the truthful
qualified owner exports in both MIR modes. The O18 stock `safety_proof`
candidate retains the full pointer-value post; it has no hosted result yet.

`prepare-actual-owner-linked.py` is a source-only step. It reuses the pinned
actual std body and existing source-certified S6 constructor, as_mut_ptr and
pointer-drop methods in one unit. It inserts the truthful nominal owner
projection, stock `safety_proof` and two qualified nested Drop opens, then
checks exact executable bytes under one deterministic ghost strip. The
hosted checker captures the full NORMAL/readonly outer/nested MIR and the
frozen S6 gate rejection. No verifier rule is active through this script.

The first semantic overlay may extend only the *admission* of the existing
S6 constructor/as_mut_ptr/intrinsic/pointer-drop rules to that new exact
linked source unit. It must leave the accepted five-ghost mode unchanged.
Pin the complete verified and original source, std `hint.rs` and dependent
std source hashes, all callee bodies and contracts, the qualified local ADT
and owner declaration with source spans, every outer ghost statement and
contract (including stock `safety_proof`), and complete typed local/outer
MIR with statements, terminators, drop flags and all normal/unwind edges.
The new ghost statements alter block/local numbering, so the frozen S6
graph certificate cannot be reused by matching function names or selected
calls alone. Preserve the shared Cleanup block and every reachable
predecessor. A mismatch is an admission rejection, not a proof negative.

The next separate overlay is an **actual nested H2 mode**. The selected ADT
is `select_unpredictable::DropOnPanic<T>` with exactly one private
`inner:*mut T` field and the exported Drop DefPath
`<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop`. The owner
definition is exactly `*g.inner |-> ?payload &*& <T>.own(t,payload)`.
The source-written nested body opens its actual full borrow and this owner
before the unchanged `self.inner.drop_in_place()` call. A source-equivalent
generic pointer-drop callee must be fully proved in the **same unit** under
`thread + initialized cell + <T>.own` with normal and unwind posts
`thread + optional uninitialized cell`, then linked by exact typed FnDef,
generic substitution, receiver `Move`, source span and complete nested
MIR. H2b's selected generated Drop post must return only that optional
cell, the stock field/padding resources and thread on both outcomes. It
must not return an initialized value or manufactured `<T>.own`; ordinary
Drop bodies remain on the stock template. The local top-level H2 proof
does not establish this nested mode.

Only then may a **separate SAFE forget link** redirect the actual one-call
site to a same-unit proved exact generic unsafe forget body. The proof
requires the guard constructor to transfer the selected initialized cell
into nominal owner, the unselected cell to remain outside, the pointer
Drop to consume and return the unselected optional cell, and the selected
owner to be opened immediately before forget. Its callee contract needs
only the thread, preserving the selected cell as a frame. The call
certificate must check the actual nominal type/substitution, `Move guard`,
cleared drop flag before that move, exact std SAFE forget source, and
normal/unwind successors. A false-unwind projection is allowed only after
the same-unit callee proof and a complete CFG certificate; cleanup shared
with other predecessors remains reachable. Reclose the selected wrapper
after the call, then prove final actual `assume_init` preserves the full
selected pointer and returns the thread. No `Element` pointee permission
is introduced.

Admission controls should mutate source/ADT/owner spans, field visibility,
generic substitution, ordered ghost commands, call operand `Copy` versus
`Move`, projection, drop flag and cleanup targets. Each must reject before
proof. Resource controls should remove a selected cell, target the other
slot, duplicate cell/thread, require pointee rights, demand initialized
post-drop storage or value-own after Drop, and falsify normal/unwind posts.
Each counts only at its intended body obligation after all other setup and
callee proofs pass. Positive acceptance requires full same-unit verifier
exit zero, both MIR modes, refinement, every body return/leak, actual
nested Drop normal and unwind checks, actual helper normal and false-unwind
checks, and no disabled dead-code, validity or memory checks. Until the
complete linked source/MIR capture exists, there is no honest concrete
frontend patch for this new mode; a source-only fixture is the falsifiable
next checkpoint.
