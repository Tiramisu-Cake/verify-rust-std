# `sort4_stable` positive-size memory-pre diagnostic — review before hosted run

## Witnessed obligation and falsifiable hypothesis

O11 (`37709227889`) exported and decoded the exact generic `sort4_stable` MIR,
refined the ghost-stripped pair, and failed in VeriFast at the first actual
comparator expression:

```text
Pointer may be out of bounds (Cannot prove pointer_within_limits(ptr_add_(v_base, 1, T_typeid)).)
```

The minimal hypothesis is that the historical checked
`interior_pointer_limits<T>` lemma, applied to the actual initialized
`v_base[..4]` resource with `count = 4` and `index = 1`, discharges that
concrete bounds obligation. Its body is copied byte-for-byte from
`extract-verifast-insertion.py`; it derives the address fact from the array,
`points_to_limits`, `array_inv`, and multiplication lemmas. The call is a ghost
line immediately before the unchanged `v_base.add(1)` comparator expression.
No pointer value, permission, or result is assumed.

The fixture deliberately uses a positive-size domain, `0 < size_of::<T>()`,
with arbitrary sized `T` and `F: FnMut(&T, &T) -> bool`. It requires no `Copy`,
`Freeze`, comparator-purity, or ordering premise. The source precondition owns
four initialized input cells and one `<T>.own` per cell. `array_<T>(dst, 4, ..)`
models four optional destination cells; separating conjunction with the input
array supplies the distinct storage needed by the raw copies for this
positive-size diagnostic. Generic/ZST behavior remains explicitly open.

## Intended posts and active diagnostic posts

The intended complete normal safety post is current initialized
`v_base[..4]`, one `<T>.own` for every current source value, initialized
`dst[..4]`, and current thread/type/comparator resources. Destination bytes do
not grant a second `<T>.own` sequence. The intended unwind post returns current
source values/owners, current thread/type/comparator resources, and the
unchanged optional destination state: every comparator runs before the first
copy, so a comparator panic occurs before destination writes. Neither intended
post claims a sortedness relation; that remains a separate SWO proof.

The active fixture posts are intentionally diagnostic and weaker: normal and
unwind return the current initialized source with one owner per element, the
current optional destination array, and current comparator/thread/type
resources. The active normal post does not claim that the four destination
slots became initialized. The fixture is always classified
`MEMORY_PRE_DIAGNOSTIC_NOT_A_SORT4_PROOF`, including a verifier exit of zero.
The capture records both complete intended posts and active partial posts
separately. It does not install a fictional borrow-debt chunk: no
`precreate_ref`, borrow token, or `ref_initialized` resource is introduced by
this first bounds-only step. If reference formation next requires such a
protocol, the next reviewed fixture must account for its exact normal and
unwind debts rather than hide them in a guard or assume bridge.

## Trust boundary and controls

The only new logical fact is the checked historical lemma above. It depends on
the pinned VeriFast array/pointer model and arithmetic lemmas; no new primitive,
axiom, parser, translator, exporter, refinement, or memory-model change is
introduced. The first actual function and its generic signature are extracted
from the pinned source. The injected lemma, contract, and bound call are all
ghost text; ghost stripping must reconstruct the exact prior source pair.
The one-token comparator-alter control must still be rejected by the source
certificate.

The opt-in `capture.py --memory-pre` mode runs the same full normal and readonly
MIR export/decode, complete graph inventory, full VeriFast log, source hashes,
and refinement check as the earlier capture-only mode. The default mode stays
unchanged. Setup/export/decode/refinement failures are inconclusive. The result
can only establish that the new lemma advances the observed first bounds
obligation; later borrow, callback, helper, pointer-copy, initialization,
unwind, and output-order obligations remain separate. No local executable
check or verifier run is part of this change.

## Self-review

The array lemma cannot prove a bound for an arbitrary index: the call fixes
`count = 4` and `index = 1`, within its checked preconditions. The source
certificate guards the actual expression, and the unmodified runtime bytes
are checked after removing the inserted ghost line and contract. The optional
destination predicate makes no assumption that prior `T` values are initialized
or owned and does not assign destination ownership. The positive-size premise
avoids treating zero-width aliasing as disjoint storage; that excludes the
generic/ZST target and is recorded as such. The diagnostic post cannot be used
as acceptance of the actual std contract.
