# Actual SAFE forget: ownership at the call boundary

This design review precedes any new specification or redirect. The exact
updated std body is `forget<T>(t:T) { let _ = ManuallyDrop::new(t); }`.
The current stock SAFE specification requires `thread_token` and
`<T>.own(t,value)`, returns only the thread, and has false unwind. O20's
G1 caller proof establishes a different, independently callable local
unsafe adapter with that exact runtime body under a thread-only contract.
It does not establish actual SAFE-call correspondence or nominal guard
ownership.

The current actual-helper ghosts close the truthful
`DropOnPanic<*const Element>.own` around the selected initialized pointer
slot, preserve the unselected slot separately through pointer Drop, then
open guard ownership immediately before `crate::mem::forget(guard)`. That
last open recovers the selected cell as an independent frame, but leaves
the stock SAFE `forget` precondition `<T>.own` absent. A source-certified
redirect to G1's thread-only adapter would make this path verifier-ready,
provided the exact nominal `T`, valid initialized guard value, plain Move,
no intervening Drop, shared cleanup and source equivalence are checked.
This route is a **new trusted relaxation at one SAFE call site**; the
generic stock SAFE specification remains unchanged. The local adapter's
full no-ownership contract and no-unwind proof are checked; the claim that
the corresponding SAFE call may frame the opened cell is trusted from the
identical ManuallyDrop runtime body and absence of any pointee read/Drop.

A stronger alternative keeps the truthful guard owner *closed* through
`forget`. First verify an exact-body generic local adapter with
`req thread_token(tid) &*& <T>.own(tid,t)` and
`ens thread_token(tid) &*& <T>.own(tid,t)`, false unwind. The post returns
the same linear resource that entered; it creates no new cell and gives
the caller no second guard. This is plausible because `ManuallyDrop::new`
is an identity move and the body suppresses Drop, but the owner-preserving
contract must be **proved**, including return/leak/dead-code checks. A
separate negative must demand a duplicate `<T>.own`, false post, wrong
value and thread loss, each at its intended obligation. If the generic
contract cannot verify without changing the stock model, reject this
route; do not assume or assert retained ownership.

If it verifies, redirect only the actual typed SAFE call to that stronger
local summary under exact source and full MIR admission. The call uses the
stock SAFE precondition and gains a proved stronger post. Immediately
after the call, open the returned nominal guard owner to recover the
selected cell once, then close its `MaybeUninit` wrapper. The actual
runtime body and its `forget(guard)` call remain byte-identical. The
correspondence still needs review because a local `unsafe` adapter is used
for a SAFE std call and the adapter contract extends the stock post. The
compiler's nominal value validity, `ManuallyDrop` representation, absence
of destructor execution, and exact generic instantiation form the trust
boundary; no `Element` pointee rights are needed.

O21's actual typed call is in outer bb16: drop flag `_40` becomes false,
`_24` moves into `_34`, and `std::mem::forget` takes plain `Move(_34)` at
`T=select_unpredictable::DropOnPanic<*const Element>`. The normal target is
bb17 and unwind cleanup target bb23, shared with eight other call edges.
The owner-preserving route requires a **new exact source/MIR certificate**:
keep the existing `GuardOwn` closed across this call, then move the current
three `OPEN_OWNER` ghost steps to after the call before closing the selected
wrapper. The stronger callee must return ownership of the *same moved guard
value*, which may be referred to by a saved logical value after Rust's
`guard` local becomes unusable. Its `inner` field must still identify the
selected slot. The current O21 source/unit fingerprint cannot authorize this
rearranged ghost variant. Normal and shared cleanup successors remain in
the MIR; only a separately proved false-unwind callee can justify a narrow
normal-only call translation while other bb23 predecessors stay reachable.

The existing actual `safety_proof` stays in force: it calls the real
pointer-specialized helper under the prototype and opens only the
definitionally true `raw_ptr_own` of the returned pointer. Neither route
changes its full normal post or false-unwind post. The generic/ZST helper
remains open; the proposed instantiation is only
`DropOnPanic<*const Element>` in the pointer-specialized actual body.

The next falsifiable decision is the standalone owner-preserving generic
adapter under a public same-unit framed caller. If it passes, prefer its
linear resource path; if it fails for a semantic reason, retain the
already-proved thread-only G1 adapter and review the narrow SAFE-call
relaxation explicitly. No new frontend rule or helper claim follows from
this card alone.
