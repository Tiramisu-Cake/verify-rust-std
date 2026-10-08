# H2 generic pointer-drop and nominal guard: pre-implementation review

2026-10-08; std `cd371e035c7e573760c43bf934d53e8118ee3e7d`,
VF26.10 `f76012fb518703b1d98e243ac4f487f16877cfcb`. The new H2
components are experimental and separate from accepted S6. The target is
the unchanged nested generic `<select_unpredictable::DropOnPanic<T> as
Drop>::drop` in `library/core/src/hint.rs`, not merely the pointer-specialized
outer call. No host-side compiler or verifier execution is authorized.

## Actual problem and proposed semantics

The nested Drop body copies `self.inner: *mut T` and calls the *method*
`std::ptr::mut_ptr::<impl *mut T>::drop_in_place<T>`. O7 full MIR records a
distinct generic body with that typed FnDef; the S6 rule handles only
`*mut *const Element` and returns an initialized pointer cell with no unwind.
Neither property holds for arbitrary `T`. The source of the generic method
has exactly `unsafe { drop_in_place(self) }`; the stock free-function spec
requires `thread_token(t) &*& *slot |-> value &*& <T>.own(t,value)` and
returns `thread_token(t) &*& *slot |-> _` on **normal and unwind**.

Component H2a should verify a source-equivalent unsafe generic method
adapter with a `T: Sized` instantiation, matching the actual nested guard's
implicit sized `T`. Its complete contract is that stock free-function
transition, with `type_interp::<T>()` framed. No `Element` pointee right,
no value-preservation post, no false-unwind claim, and no generic change to
the free drop-glue axiom are involved. Exact std method and free-glue source
hashes, local runtime-body equality, and typed MIR shape are admission
conditions before a call redirect can use H2a.

Component H2b needs a **truthful** nominal
`<DropOnPanic<T>>.own(t,g)`: the actual selected initialized cell at
`g.inner`, including `<T>.own(t,payload)`. The cell is transferred from its
original wrapper at guard construction; the other wrapper stays separate.
The actual generic destructor opens this owner and passes it to H2a. A real
caller must construct this owner from an initialized cell and the Drop body
must reach return/leak check; an impossible precondition is unacceptable.

The stock generated SAFE Drop template pre contains the guard field,
padding, thread and nominal owner. Its post returns field/padding/thread but
omits the target now left uninitialized by drop. A narrowly gated extension
to `gen_drop_contract` should add `*g.inner |-> _` to **both** outcomes for
this exact nominal ADT, after source/typed-MIR certification. Ordinary Drop
types retain their stock template. The extension must not assume that Drop
succeeds or erase cleanup, dead-code, leak, validity or refinement checks.

## Trust boundary and causal gates

The method copy's correspondence to the std method is trusted at the
source/MIR interface, bounded by whole-file SHA, exact body, typed callee,
argument, destination and both CFG outcomes. Its body and caller contracts
must be proved, not asserted as a ghost axiom. The compiler's free
`drop_glue` remains the existing trusted primitive with the stock generic
resource contract; it is not strengthened to initialized storage or no
unwind. The new generated Drop post is a trusted frontend contract-shape
rule; acceptance requires the actual generic Rust body to prove that post
nonvacuously and every ordinary Drop control to remain unchanged.

Before writing a redirect or template patch, capture complete NORMAL and
readonly MIR for the generic source-equivalent method and actual nested Drop
on the combined O10 profile. The first capture is a diagnostic. A source
mutation must reject before method proof once the exact gate exists. The
method matrix then needs positive generic transition/frame cases and
negative missing owner, duplicate/lost/wrong slot, false normal post,
false unwind post, wrong receiver, source body, typed callee/operand/CFG,
plus a separately verified ordinary Drop regression. The guard matrix needs
the actual body, a constructed real-owner witness, missing/duplicate/wrong
target, normal and unwind optional-state obligations, and full source/MIR
and refinement gates. No negative counts if setup or an unrelated body fails.

## Self-review before first implementation

The first artifact in this directory is only a source-certified hosted
capture driver for H2a. It does not activate a new frontend rule and labels
all results diagnostic. It uses both MIR export modes, full VeriFast and
refinement, records untouched original/verified source hashes, and isolates
the generic method from the actual helper. If its compiled graph or free
contract resolution differs, the next semantic patch must be redesigned
from that evidence. The H2b source predicate and template extension remain
unimplemented until actual generic graph and parser binding are captured.

## H2b isolated SAFE-body capture review

The next diagnostic copies the exact private-field `DropOnPanic<T>` struct
and the exact generic `Drop::drop` runtime body from the pinned actual helper
into an isolated module. Its exported DefPath is **not** the actual nested
DefPath; the certificate records this limit. This removes unrelated outer
constructor/intrinsic failures while exposing the same field type, generic
call and SAFE generated Drop prototype. A top-level predicate gives the
guard the real initialized target cell and its `T.own`; the only body edit is
ghost opening of full-borrow content and that nominal owner. Ghost stripping
must recover the exact source-certified Drop body bytes.

An unsafe constructor with pre `*slot |-> v &*& <T>.own(t,v)` returns the
guard owner after explicitly closing it; no destructor can run before return.
Its positive fixture also instantiates `T=u32` and transfers a concrete
initialized `u32` slot cell from the caller into that owner. This makes
nonvacuity observable without returning a pointer to a dead local stack slot.
Missing-cell and wrong-target variants must fail at that close, not at a
setup error. An independent ordinary public-field Drop control checks that
the stock generated template still verifies without a nominal extension.
The H2b capture does not redirect the generic method; an unresolved method
or target-post leak is expected causal evidence. Full NORMAL/readonly MIR,
refinement and source integrity run even when full verification stops.

## O11 capture and parser-only amendment

O11 run `37709227889` completed both MIR export modes, decoding and
refinement for every H2a/H2b case. H2a's source-equivalent generic method
and frame probe fully verified; missing owner and false normal/unwind posts
failed at their intended proof obligations. These are **local method**
results only; no actual generic method redirect occurred. The isolated
ordinary public-field Drop control fully verified on the same profile.

All three H2b owner variants stopped before body verification at a parser
error on the **second** `open` statement within one inline `/*@...@*/`
block. O11 gives no owner-construction or generic SAFE Drop proof result.
The fixture now emits two adjacent single-statement ghost blocks. Both are
removed without changing a byte of the pinned Drop runtime body; no
predicate, method contract, normal/unwind post, verifier rule or target
classification has changed. A fresh hosted run must confirm the parser
accepts this exact encoding before any semantic extension is judged.
