# Test-shape static audit — no execution

Bounded read-only Luna HIGH audit and main-agent integration review. Production
semantics did not change; this is not a renewed proof acceptance or a compiler
typecheck. No build, verifier or test ran.

Old CI failure locations bind to nested Calls, not the intended payload load.
The local visitor's new SetRef(false) itself is not the shared Unsupported
cause: check_uninit/mod.rs selects for_deinit for it, which permits full sized
Nested storage; the baseline has no such new reset and also fails. Delayed
CheckRef/SetRef(true) on a whole Nested instead uses from_ty and rejects
UnionAsField. Field-insensitive points_to::resolve_place can collapse a field
target to its aggregate. The exact old initial seed/consumed-MIR cause has not
been independently bound; removal of the old MaybeUninit helper path is a
source-based design choice, not an empirically proven causal account.

The new fixtures' explicit addresses are directly union-field *u8 addresses.
InitialTargetVisitor does not seed on AddressOf or a raw u8 dereference; its
seeds are incompatible pointer casts, copy-like destinations and raw_eq.
None of those operations is explicitly present in the new fixture code.
All MaybeUninit/as_ptr/assume_init helper use is removed. The intended result
is that the old field-insensitive whole-Nested delayed guard is not selected;
the actual reachable target set still requires CI/MIR inspection.

Local pointer instrumentation can check and set the ordinary union's u8 field
while forming its address. Therefore each saved pointer is formed only after
the seed field assignment and before the tested nested Call(s). No address is
formed after reset. The pre-call field check should succeed; later load checks
exactly *const u8. Whole source/destination reset in production still uses
for_deinit's full extent. Reinit writes *mut u8 and uses the ordinary store
setter, preserving later writes without a whole-Nested pointer.

Slot field assignment/copy is existing ordinary-union AssignUnion machinery;
top-level Slot arguments retain the paired protocol. Nested construction and
return are fieldwise. Nested is non-Copy; actual Move(source) is written in
optimized custom MIR, with live saved storage. No whole-Nested use assignment,
callee payload read, function-pointer call, dangling-pointer test or unrelated
negative is substituted. The direct payload read changes the exact description
from `u8` to `*const u8`; its expected count remains one. A local/delayed
duplicate or any extra Unsupported/frame/validity failure requires review,
not blessing the output.

Source expectations: repr(C) Nested size2/alignment1, payload and Slot.byte
offset0/extent1. Those numbers, pointer object identity, Call destination reuse,
actual Move, retained target load and empty consumer must be bound to the
actual consumed MIR before acceptance. Per-fixture object-bits12 and all normal
checks remain enabled. Rust type/borrow inspection found no evident mismatch;
rustfmt parsing is not compiler validation. Runtime/discrimination credit NONE.
