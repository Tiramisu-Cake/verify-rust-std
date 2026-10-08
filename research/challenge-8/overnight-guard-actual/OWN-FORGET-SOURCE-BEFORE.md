# Seven-body owner-preserving forget: source-only capture before linkage

O22 independently proved the exact std-body `checked_forget_owned<T>`
unsafe adapter with `thread_token + <T>.own(tid,t)` in both pre and normal
post and `on_unwind_ens false`. Its false normal post, owner duplication,
wrong value, thread duplication, owner loss, contradictory precondition and
weakened unwind admission controls failed at intended obligations. This
theorem is about the local adapter, not the actual SAFE `forget` call.

The O21 actual owner source opens `GuardOwn` before the SAFE call, leaving
the stock SAFE `forget` precondition absent. The seven-body source-only
variant keeps `GuardOwn` closed across the unchanged
`crate::mem::forget(guard)` runtime call. It adds the exact checked adapter
as a top-level same-unit callee before the actual helper; the exact H2a
generic pointer-drop callee remains before it. A ghost assertion binds the
already owned guard value before its Rust Move. After the call, a ghost
open of the **returned same-value owner** recovers the selected initialized
slot once, then the source closes its selected `MaybeUninit` wrapper.
The full actual normal pointer-value post, false unwind post, stock
`safety_proof`, nested guard Drop opens and runtime body remain unchanged.
No `<Element>.own` or pointee right is added.

This capture checks source/ghost strip identity, the full seven-body
NORMAL/readonly MIR, separate source certificates for the actual std body,
H2a generic drop and O22 owner-preserving forget adapter, and independent
refinement. It does **not** enable a SAFE-call redirect, a nested Drop
redirect, a generated-post change or a proof summary. The new ghost
assert/open syntax must be tested by later full verification; a parser or
scope failure remains diagnostic. The seven-body source and complete MIR
need a fresh admission certificate; O21's five-body hash and future
six-body hash cannot authorize them.

Only after a full new source/MIR review may a narrow trusted
correspondence map the actual SAFE call with exact nominal
`DropOnPanic<*const Element>` type, plain `Move(_34)`, cleared drop flag,
normal and shared cleanup successors to the proved same-body adapter.
The adapter's post must return exactly the owner of the moved guard,
without creating a second owner. Normal and false-unwind behavior must
be linked to the exact actual std `forget<T>` source and
`ManuallyDrop::new` representation. The generic pointer-drop and qualified
nested Drop bodies must be proved before using their summaries. Full
return/leak/dead-code/memory/validity/refinement checks remain active.
