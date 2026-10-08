# Actual pointer helper: one selected-slot transfer through the guard

Design before a new semantic overlay. The O12 five-ghost projected run is a
diagnostic of the old resource prefix. It cannot establish truthful nominal
guard ownership: those five ghosts close **both** `MaybeUninit` wrapper cells
before `forget`, leaving no selected slot cell to place in `DropOnPanic.own`.
No patch or proof for this protocol is accepted by this note.

The target is the unchanged `core::hint::select_unpredictable` body with
`T = *const Element`, unrestricted `Element`, token-only pre, same token plus
complete selected pointer normal post and `on_unwind_ens false`. The two local
wrapper slots are distinct; `true_ptr` and `false_ptr` carry their addresses,
not pointee rights. `*true_ptr |-> p_true` and `*false_ptr |-> p_false` denote
initialized **pointer values**. There is never a permission for `*p_true` or
`*p_false` as an `Element` cell.

Let `S = condition ? true_ptr : false_ptr` and
`D = condition ? false_ptr : true_ptr`. After source-certified
`open_MaybeUninit` on both wrappers, the resource is one cell at `S` and one
at `D`, each carrying its original full pointer value, plus the established
wrapper value-ownership facts. The two typed intrinsic calls prove the exact
`guard.inner = S`, `drop = D`, and `S != D` relationship branchwise. A
proof-only split on `condition` must then **consume** the `S` cell into a
satisfiable nominal predicate, schematically

```
DropOnPanic<T>.own(t, guard) =
    *guard.inner |-> ?payload &*& <T>.own(t, payload)
```

for `T=*const Element`. The raw-pointer `<T>.own` is the accepted value-only
ownership and supplies no `Element` right. The `D` cell stays separate.
The source ghost action must close the actual nested nominal predicate from
the selected cell; an assertion that the predicate is `true` or a duplicate
`S` cell is inadmissible. A concrete `u32` owner witness and the actual
generic Drop body are separate H2 obligations under the generated SAFE Drop
contract. The source syntax/binding of this nested predicate remains to be
captured on hosted MIR before implementation.

At the call `D.drop_in_place()`, the pointer-specialized checked method
consumes and returns only the `D` cell with its **same** full pointer value,
and cannot unwind. The guard predicate frames the `S` cell. Close only the
unselected wrapper immediately after this call. The selected wrapper stays
open while its cell is inside guard ownership. The normal resource state is

```
thread_token(t) * DropOnPanic.own(t, guard) *
    initialized_MaybeUninit_cell(D, p_D) * wrapper_value_ownership
```

The exact typed `mem::forget(guard)` call must consume the guard value and
its nominal own, execute the unchanged body `let _ = ManuallyDrop::new(t);`
without running `Drop`, and return **exactly once** the initialized `S` cell
with `p_S`, the token and the independent `D` wrapper frame. A local
source-equivalent adapter can make the transfer visible by ghost-opening the
guard predicate in its body before the ManuallyDrop identity operation; the
body proof must discharge its full normal/no-unwind post and leak/dead-code
checks. This relies on a reviewed, source/MIR-pinned correspondence that
moving a guard into ManuallyDrop suppresses its destructor and does not read
the pointed-to slot. The stock generic SAFE `forget<T>` contract remains
unchanged. Redirect only the one actual typed call after the local adapter is
proved in the same source profile. Preserve its MIR normal and cleanup
successors; a false-unwind callee must make the cleanup branch unreachable by
proof, not by deleting the shared cleanup block.

After that transfer, close the **selected** wrapper using the returned cell.
Now both wrapper cells and their original full pointer values exist again.
The third typed intrinsic chooses the original selected wrapper; the
pointer-only `assume_init` chain consumes an initialized wrapper and yields
the same complete pointer, token and no `Element` rights. The rejected
alternative is closing both wrappers before `forget` and then pretending
the guard also owns `S`.

The generated generic guard Drop template still has to verify its actual
body on normal and unwind paths. H2a needs the generic pointer-drop method
with its genuine possibly-unwinding contract; H2b needs the truthful nominal
owner and post exposing the now-uninitialized target slot. Those results do
not by themselves prove the outer helper, but they prevent a vacuous
`own=false` destructor from being counted as safety evidence. In the outer
pointer-specialized helper, the only live-guard call is the no-unwind `D`
drop. Later `forget` and `assume_init` must be source-linked no-unwind; the
guard drop flag is cleared before the forget move. The full MIR cleanup
inventory, including the shared predecessor, remains admitted and inspected.

Any new ghost/source admission must be a separate overlay after fresh O12
prefix evidence. Pin whole std source, exact specialized helper runtime body,
ADT field/privacy/generic binding, ordered ghost strings and coordinates,
complete NORMAL/readonly typed MIR and all cleanup edges. Reject wrong
selected address, missing/duplicated `S` cell, loss/change of either full
pointer value or thread, unselected frame loss, altered forget callee/operand,
drop-flag order, extra operation, and false normal/unwind posts at their
intended source, admission or proof obligation. Keep refinement, validity,
memory, unwind, leak and dead-code checks enabled. The old five-ghost S6
certificate stays frozen and remains only an independently measured prefix.
