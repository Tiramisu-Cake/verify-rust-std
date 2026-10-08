# Exact-nine SAFE forget owner preservation: before patch 19

The O24 nine-body source keeps the real SAFE std::mem::forget(guard)
runtime call and a truthful, closed nominal guard owner across that call.
A source ghost assertion binds its existing logical value before Rust
Move; after the call, a source ghost open refers to that same saved value.
This requires more than the stock SAFE forget summary, which consumes
T.own and returns only thread. O22 independently proved the whole exact
std runtime body in the local public unsafe checked_forget_owned<T>
adapter under thread + T.own pre, thread + the *same* T.own normal post,
and false unwind. Its owner preservation is a checked theorem, not an
axiom, but the SAFE std call to local unsafe adapter correspondence
remains a narrow trusted bridge.

This separate default-off patch is conditional on exact-nine admission
from patch17 and the pinned complete O24 unit/source/std fingerprints.
It checks the same-unit local adapter's exact source signature/body,
generic T, full three-clause owner/thread contract and original std
forget/ManuallyDrop body. The actual call must be the unique typed
std::mem::forget<qualified DropOnPanic<*const Element>> with plain
Move(_32), destination _31, normal bb15 and unwind cleanup bb24. Its
source block first writes the real drop flag _41=false and moves the
real guard _24 to _32. No projection, Copy, extra operation or different
generic substitution is admitted.

Only that actual call is translated as a call to the checked same-unit
adapter with the exact nominal type argument. Its result is projected
from fn_outcome only because the local contract has false unwind.
The emitted AST has only the normal successor for that call; original
MIR cleanup bb24 and all ten original incoming call-unwind edges are
certified before translation, and the nine other predecessor edges
remain reachable. No global cleanup pruning or dead-code suppression
occurs. Other std::mem::forget calls retain stock behavior.

The caller must supply its real closed GuardOwn resource and thread,
not a fabricated true predicate. The adapter returns exactly one
GuardOwn for the same saved value and thread; opening it then yields
the selected initialized cell and raw pointer value right, while the
unselected cell has already been dropped/reclosed. No Element pointee
right appears. The ordinary public SAFE prototype retains its stock
precondition. The local adapter is unsafe/nonconst whereas std forget
is SAFE/const: that source/typed-call correspondence is explicitly
trusted under the pinned compiler/std profile, and is not a general
SAFE forget rule.

The full nine-body verifier must prove the adapter in this same unit
and all body return/leak/dead-code obligations before any actual helper
claim. Source/typed-MIR mutants of callee body/post, nominal type,
Move/Copy, drop flag, normal/cleanup edge and shared cleanup should
reject at exact source/unit/typed gate. Resource mutants must fail at
their intended owner/thread/post obligations after call linkage.
Neither patch19 nor a green local O22 component alone proves the
actual helper; A1 assume_init remains separate.
