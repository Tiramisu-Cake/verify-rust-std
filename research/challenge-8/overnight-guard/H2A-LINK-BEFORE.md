# H2a generic method linkage: prepatch admission card

O11 run `37709227889` proved the source-equivalent unsafe generic local
adapter and framed probe on both normal/unwind paths with full verifier
exit 0; missing owner and false normal/unwind post controls failed at
their exact obligations. This is a local proof, not an actual call summary.

## Actual obligation and hypothesis

The actual SAFE nested Drop body calls
`std::ptr::mut_ptr::<impl *mut T>::drop_in_place<T>` on a copied `inner`
raw pointer. The S6 pointer-specialized method redirect is inapplicable:
generic `T` can run arbitrary destructors and unwind. The hypothesis is
that the local O11 helper, whose body is the exact std method body after
receiver renaming and qualification of the free function, can serve as a
checked summary for this one generic typed call. Its pre consumes a real
initialized target cell plus `<T>.own`; normal and unwind return only
optional storage and thread. O11's local capture framed
`type_interp::<T>()`, but stock SAFE Drop pre does not supply that token
and stock free drop does not require it. The candidate removes that
gratuitous conjunct and must reprove its local method before redirect.
The actual Drop body must still prove those
resources exist from the truthful nominal guard owner.

## Exact admission and trust

The redirect must be off by default and enabled only after the same
fixture contains the exact local generic method signature/body/complete
contract, verified source spans and complete NORMAL typed MIR graph:
`_2=Copy(_1)`, free `std::ptr::drop_in_place<T>` FnDef, Move `_2`,
destination `_0`, normal bb1, unwind Continue, then StorageDead/Return.
Both std `mut_ptr.rs` and `ptr/mod.rs` whole files and exact method/free
glue bodies remain pinned. The target must be the source-certified SAFE
Drop body with exact private-field guard ADT, one generic `T`, typed
FnDef/substitution, copied `inner`, normal/unwind successors and all
ghost-command blocks. A standalone top-level guard DefPath and the
actual nested DefPath need separate mode certificates. No name-only
redirect, global generic method summary, false unwind, assumed owner,
runtime source edit or deleted cleanup is admissible.

The trust boundary is the equivalence of the compiler's std method and
checked local adapter under the pinned source/typed MIR certificate. The
free drop-glue primitive remains the existing stock contract. The
adapter's proof is checked by ordinary VeriFast return/leak paths; the
SAFE Drop body is also separately checked. The redirect is not itself a
lemma proving the outer helper and cannot manufacture a target cell.

## Controls and expected decisions

With the redirect alone, the local source-equivalent guard Drop should
advance past the missing method and fail at the stock generated Drop
post's leftover optional-cell leak. That is the causal basis for the
separate nominal template extension. If it fails earlier on the owner
open or method pre, repair the resource protocol first. Source mutations
to local method body, guard body/field, call operand, target type or
contracts must reject before proof. Typed MIR mutations to FnDef,
substs, local mapping, added operation, destination, normal/unwind edge
or ghost-command inventory must reject at the exact certificate. Missing
cell and wrong target must fail at owner construction, not be counted as
method-link negatives. Ordinary Drop and the accepted S6 pointer-only
matrix must remain unchanged under the candidate console. The eventual
actual nested mode must retain the outer shared cleanup and exact runtime
body and get a distinct hosted run. O11/O12 diagnostics do not imply this
redirect has been accepted.

## O13 evidence and first isolated H2a candidate

O13 run `37711416854` retained the O12 four-block annotated guard graph.
Its standalone H2b positive was blocked before the constructor by a parser
restriction on `close <u32>.own(t,value)`; direct stock `close u32_own` is a
new, unverified fixture amendment. The linked H2a fixture omits this
independent concrete witness while keeping the generic owner constructor,
exact guard ADT, owner predicate and exact generic SAFE Drop runtime body.
O13 missing-cell and wrong-target owner controls fail at the intended
`points_to<T>` assertion, and ordinary Drop proves under the same profile.

The first H2a patch is **local DefPath only**. Activation requires
`SORT4_GUARD_REPO_ROOT` and a same-unit source/MIR certificate. It pins
whole-file MD5 values for `mut_ptr.rs`, `ptr/mod.rs` and `hint.rs`, the
exact std method body, checked local method contract and body, exact
standalone guard body and private field, the sole exported owner predicate
with its source coordinates, relevant source spans, and both complete
typed method/guard graphs. Its redirect targets only
`<DropOnPanic<T> as std::ops::Drop>::drop`; the actual nested DefPath is
excluded. Method-operand and guard-operand source mutants must reject in
the certificate before proof, with the exact reason recorded. A positive
cannot be accepted from a gate print alone: the local checked generic
method must prove return/leak, the guard body must reach the method and
eventually prove its normal and unwind posts, and the independent nominal
template component must be reviewed separately. The stock SAFE Drop pre
does not include `type_interp::<T>()`; the candidate method no longer
requires it. A hosted rerun must prove its body and the missing-owner and
false-post controls on this revised contract. No actual Rust helper proof
is claimed here.
