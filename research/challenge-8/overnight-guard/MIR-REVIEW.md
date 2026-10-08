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

## O11 generic method capture

Run `37709227889`, H2a positive case, exported the same two-block
shape in NORMAL and readonly. Local `sort4_checked_generic_drop<T>` has
one input `*mut T`, `_0:()`, `_1:*mut T`, `_2:*mut T`, `unsafe=true`,
`isDropFn=false`, a single `Sized<T>` clause and no extra ghost statements.
Block 0 has `StorageLive(_2)`, `_2=Copy(_1)` and a zero-sized FnDef
`std::ptr::drop_in_place<T>` call with `Move(_2)`, destination `_0`,
normal target 1 and unwind `Continue`. Block 1 has `StorageDead(_2)` and
`Return`; both blocks are non-cleanup. This is source-certified to the
std method body after only `self→slot` and free-call qualification.

Full VF exit 0 includes return and leak checks for the generic method and
frame probe on normal **and unwind**. Three isolated controls fail at
their target obligations: missing `<T>.own` at the free-drop call, false
normal post, and false unwind post. All had NORMAL/readonly MIR, refinement
and source-integrity success. These establish H2a's *local* adapter proof,
not a redirect from the actual nested Drop method. Its future gate must
pin the full local graph above and the actual nested graph above, and
must keep their distinct DefPaths explicit.

## O12 nominal guard capture

Run `37710354025` removed the O11 parser obstruction. The source-equivalent
local guard constructor proves its return and leak check from a real
`*slot |-> value` and `<T>.own(t,value)`. The concrete `u32` witness then
failed at the constructor's generic `<T>.own` pre: the stock `u32_own`
predicate has body `true` but still requires an explicit `close` to produce
its predicate chunk. The O13 fixture adds only that ghost close. In the
missing-cell and wrong-target controls, the close of guard owner reaches
the predicate's `*g.inner |-> ?payload` assertion and fails there, with
the constructor and close statement in the trace. Ordinary Drop remains
full-verifier exit 0. No local SAFE guard Drop body proof was reached in
the positive case, and none is claimed for O12.

The annotated local guard method now has exactly five locals: `_0:()`,
`_1:&mut DropOnPanic<T>`, two unit ghost destinations `_2`/`_3`, and
`_4:*mut T`. Its four non-cleanup blocks are: (0) `StorageLive(_2)` and
zero-sized `VeriFast_ghost_command` for full-borrow open, normal target 1,
unwind `Continue`; (1) `StorageDead(_2)`, `StorageLive(_3)` and the second
ghost-command for nominal owner open, normal target 2, unwind `Continue`;
(2) `StorageDead(_3)`, `StorageLive(_4)`, `_4=Copy((*_1).inner)` with the
typed `inner:*mut T` field projection, then zero-sized generic FnDef
`std::ptr::mut_ptr::<impl *mut T>::drop_in_place<T>`, `Move(_4)`, `_0`
destination, normal target 3 and unwind `Continue`; (3)
`StorageDead(_4)`, Return. NORMAL and readonly inventories agree. Both
ghost statements appear separately in `ghostStmts`; generated template
must retain both normal and unwind obligations. This is the **top-level
adapter DefPath** `<DropOnPanic<T> as std::ops::Drop>::drop`, distinct from
the nested actual std DefPath.
