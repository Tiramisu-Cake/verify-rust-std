# H2 generic Drop MIR inventory and exact-gate obligations

Read-only review of O7 NORMAL/readonly artifacts from run `37705052264`,
`overnight-s6/asptr-linkage/positive/{normal,readonly}-mir.txt`. This is
the actual unchanged helper source at the pinned 26.10 std, before H2 ghost
annotation or frontend extension. It is not a proof of the nested Drop body.

The ADT is `select_unpredictable::DropOnPanic`, `StructKind`, `isLocal=true`,
one restricted/private field named `inner` with type `*mut T`, one variant,
and an ordinary type parameter `T` without an added Copy/Freeze restriction.
The actual method DefPath is
`<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop`, with
`isDropFn=true` and `unsafety=safe`. Its input is `&mut DropOnPanic<T>`;
`_0` is `()`, `_1` is that mutable reference, `_2` is `*mut T`.

The complete actual method CFG has two non-cleanup blocks. Block 0 contains
`StorageLive(_2)`, then `_2 = Copy((*_1).inner)`, then a call with a
zero-sized FnDef constant
`std::ptr::mut_ptr::<impl *mut T>::drop_in_place<T>`. The sole argument is
`Move(_2)`, destination `_0`, normal target block 1, unwind action
`Continue`. Block 1 has `StorageDead(_2)` and `Return`. There are no other
operations or local cleanup blocks in this method. The outer helper's
common cleanup block 13 remains a separate obligation; method-local
`Continue` does not justify suppressing that outer cleanup.

A future exact gate must pin this full shape, field type/visibility, generic
FnDef/substitution, both successors, and the safe/drop flags. It must also
check full pinned std source plus the exact generic method and actual
nested body, then separately prove a checked local H2a method and redirect
only this typed nested call. An adapter with top-level `DropOnPanic<T>` has
a different DefPath and cannot alone certify the actual nested call.

The generated `gen_drop_contract` post currently uses the ADT field
points-to/own, padding and thread for both outcomes, and omits the
uninitialized pointee cell. Its pre invokes the full borrow content, which
contains field points-to, padding and nominal `.own`. For the exact guard
predicate, opening `.own` provides the initialized `*inner |-> payload` and
`<T>.own(t,payload)` needed by the stock generic free-drop contract. That
call returns only optional storage on both outcomes; the template extension
would add a typed `PointsTo` with dummy value for the pointee at `inner` to
both posts. This extra post must be *proved by the body* and must not be
silently added for ordinary Drop types or as a new axiom.

The accepted S6 actual-select gate currently requires the outer
`select_unpredictable` body's `ghost_decl_blocks` to be empty and its
`ghost_stmts` to equal only the reviewed MaybeUninit projection sequence.
The H2b isolated fixture does not activate that gate. A later actual-helper
fixture that inserts guard transfer statements into the outer body will need
a separately reviewed exact ghost-statement extension, with its typed MIR
graph and unchanged runtime body pinned. The nested Drop method's own
ghost opens are a separate body and do not by themselves weaken the outer
gate.
