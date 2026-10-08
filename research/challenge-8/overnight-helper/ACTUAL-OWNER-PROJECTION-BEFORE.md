# Actual helper nominal-owner projection: diagnostic source capture

This is a separate candidate from the frozen S6 five-ghost projection. Its
first job is to test whether the 26.10 exporter and parser can bind a
top-level ghost predicate for the actual function-local, qualified
`select_unpredictable::DropOnPanic<T>` to the same ADT used by the caller and
the nested destructor. A local ghost declaration inside the outer function
would not by itself establish visibility in the separately translated Drop
body. No generated source or frontend rule is accepted by this card.

The unchanged runtime source is `core::hint::select_unpredictable` at the
pinned `hint.rs` hash, instantiated only at `T = *const Element` with
unrestricted `Element`. The target pre owns the current thread. The normal
post must return the exact selected full pointer with its raw-pointer value
ownership and the thread; unwind is `false`. No permission to an `Element`
pointee is present. The candidate owner definition consumes exactly the
initialized selected local slot and the value ownership of its raw pointer:

```text
pred<T> <select_unpredictable::DropOnPanic<T>>.own(t, g) =
    *g.inner |-> ?payload &*& <T>.own(t, payload)
```

The two `MaybeUninit` opens expose distinct cells holding `true_val` and
`false_val`. After both typed pointer-select calls and guard construction,
a proof-only branch closes this owner using the selected cell. The accepted
raw-pointer own predicate has body `true`; its explicit close creates no
`Element` permission. The unselected cell remains outside the owner. The
pointer-specialized drop returns that cell unchanged; a conditional close
reconstitutes only the unselected wrapper. Immediately before unchanged
`crate::mem::forget(guard)`, open the guard owner and the empty raw-pointer
value predicate. The selected cell is then an ordinary frame for a proposed
source-equivalent, independently proved generic forget callee. After the
call, conditionally close only the selected wrapper. The final wrapper
selection and `assume_init` must preserve the original selected pointer.

The diagnostic fixture inserts only ghost declarations/statements and checks
that stripping them gives the exact original baseline bytes. It must capture
NORMAL and readonly full typed MIR, the nested ADT and Drop DefPaths, the
ordered ghost inventory, the guard drop-flag assignment before the forget
`Move`, all normal/unwind targets and the shared cleanup predecessor.
Refinement must pass. A parser rejection of the qualified local owner or an
unexpected MIR shape is a setup result, not a failed ownership proof. A
later exact-source frontend overlay needs its own admission, negative
mutations and full proof; it cannot reuse the frozen five-ghost S6 gate.

The actual SAFE `forget` still has its stock nominal-own pre and cannot be
counted as proved by this candidate. A future one-call redirect requires a
new full same-unit proof of the exact generic forget body under thread-only
pre, normal thread post and false unwind. It must certify the actual call's
typed nominal substitution, guard operand `Move`, drop flag cleared before
that move, and exact pinned SAFE and local callee bodies. If the verifier's
synthetic unwind arm becomes dead code, a narrow emitted-CFG/successor repair
may use a proved no-unwind outcome extraction while preserving every
reachable shared cleanup predecessor. No blanket cleanup pruning, disabled
dead-code check or assumed owner is allowed. The generic nested Drop body
remains a separate normal/unwind proof obligation.

## O16 compatibility finding and post-completion obligation

O16 captured the revised ghost projection after separate `open` annotations
fixed the O15 parser rejection. NORMAL/readonly export and decode, refinement
and exact ghost stripping passed. The qualified nominal owner was present in
both decoded graphs, and the outer body retained its shared cleanup. Full
verification stopped before the body at the generic function prototype check:
the specialized post's additional `raw_ptr_own::<Element>()(t,result)` leaked
against the prototype. O16 therefore proves no ownership transfer, destructor
body, or actual helper return.

The next diagnostic `--owner-post-completion` keeps the actual helper's
prototype-compatible normal post: the current thread and exact selected full
pointer equality. The full intended pointer-value post remains required. It
is packaged as a separate checked entailment lemma whose pre is exactly that
normal post and whose conclusion adds `raw_ptr_own::<Element>()(t,result)`.
The lemma body only closes this predicate. The pinned 26.10 definition is
`pred_ctor raw_ptr_own<T>()(t,v)=true`, so it creates neither memory permission
nor `Element` pointee ownership. Its proof must pass complete NORMAL/readonly
export/decode, refinement and full verification. False, duplicated-thread,
wrong-pointer and pointee-right post controls must fail at their intended
obligations. Any change to the predicate definition reopens the trust review.
The actual helper is accepted only when its complete body under the
compatible post **and** the completion lemma both pass. Until then the
`--owner-post-completion` run is diagnostic only.

## Separate O18 stock `safety_proof` experiment

The O16 leak occurred in VeriFast's *prototype implementation check*, before
the actual Rust body. The stock `rust_parser.ml` accepts a `safety_proof`
clause after `req`/`ens`/`on_unwind_ens`. Stock `verifast.ml` checks a pure
prolog, requires exactly one `call()` of the implementation under its
specified contract, then checks the epilog against the generated safe
prototype. This is already-supported proof syntax and introduces no new
frontend trust rule.

The new `--owner-safety-proof` candidate retains the full original pointer
post, including `raw_ptr_own::<Element>()(t,result)`, and inserts this exact
ghost clause before the unchanged runtime body:

```text
safety_proof {
    let r = call();
    open raw_ptr_own::<Element>()(_t, r);
}
```

The generated prototype's thread binder is `_t`; the `call()` result binds
the full pointer value as `r`. Opening the verified `raw_ptr_own` chunk
releases only a predicate whose pinned body is `true`. It neither discards
`Element` pointee rights nor modifies the returned pointer/provenance. The
expected positive is a successful prototype check, after which the ordinary
actual body may reveal a later ownership or call-linkage blocker. O16 without
this clause is the negative control: its first error is the precise
prototype leak. An omitted/wrong-pointer `open` variant must fail at the
prototype compatibility obligation, not at setup; its exact stage and
location require hosted inspection. The source fixture checks exact
ghost-strip identity, unchanged actual runtime inventory, NORMAL/readonly
typed MIR and refinement. No `assume`, `assume_correct`, trusted primitive,
or runtime-source change is admitted. A passing prototype proof alone is
not a helper proof; the nested Drop, actual SAFE forget, normal/unwind body
and leak obligations remain.

## Exact nested Drop annotation boundary

The separate `--annotate-nested-drop` source-only diagnostic inserts the
same two resource opens used by the local H2 guard proof immediately before
the existing unsafe `self.inner.drop_in_place()` inside the **actual**
function-local destructor. Its type name is the exported qualified
`select_unpredictable::DropOnPanic<T>`, not the local fixture's
`DropOnPanic<T>`:

```text
open <select_unpredictable::DropOnPanic<T>>.full_borrow_content(_t, self)();
open <select_unpredictable::DropOnPanic<T>>.own(_t, ?g);
```

The first open exposes the borrowed guard and its nominal owner; the second
exposes the owned initialized `*g.inner` cell and `<T>.own` supplied by the
caller. For the pointer specialization, `<*const Element>.own` is the
definitionally true pointer-value predicate, with no `Element` pointee
permission. The existing generic `drop_in_place<T>` summary consumes the
initialized cell and value ownership and yields an optional uninitialized
cell on both normal and unwind paths. A future exact nested-DefPath H2
template mode must return that optional cell in both generated SAFE Drop
posts. The local H2b top-level mode cannot silently apply to this nested
ADT; source/ADT/field/owner spans and full nested MIR need a separate
admission certificate. The fixture checks ghost-strip identity and complete
MIR capture before any such rule. With no nested template mode active, this
annotation is diagnostic and need not prove the Drop body.

## O17 evidence and same-unit S6 integration boundary

O17 (`37717092130`, `11d888ba`) proved the independent owner-post
completion lemma with full verifier exit zero, one lemma proof header,
NORMAL/readonly export/decode and refinement. Its four unchanged-runtime
negative post variants each failed at the intended line 11: false,
`Element` pointee permission, a second thread token, and the wrong selected
full pointer. The historical evidence retains its original diagnostic
labels; the checked classifier now recognizes those precise obligations in
future runs. This proves only the definitional pointer-value completion,
not the actual helper body.

O17's prototype-compatible actual-owner candidate passed source identity,
both MIR captures and refinement, and reached the Rust body. Its first
error was line 25, missing `std::mem::MaybeUninit::<T>::new`. This is a
linkage setup barrier: that fixture includes only the actual outer helper
and nested Drop. The accepted S6 constructor, as_mut_ptr and pointer-drop
redirects require their independently checked local callee bodies in the
same exported unit, and the S6 actual-call gate admits only the frozen five
ghost annotations. The new `prepare-actual-owner-linked.py` assembles the
exact existing S6 local source certificates and unchanged actual runtime
body, then adds the truthful owner, optional stock `safety_proof`, and
qualified nested Drop opens. Its hosted checker captures complete outer
and nested MIR and the first frozen-gate rejection. It does not enable a
semantic rule or claim a proof.

The required next overlay is a **separate opt-in exact actual admission**,
not a change to the accepted five-ghost mode. It must pin the full linked
verified source and original runtime, exact exported contracts/ghost spans,
nominal ADT/owner linkage, full local callee proofs, outer and nested typed
MIR statements/terminators/locals/drop flags, and all normal/unwind edges.
The new owner ghost inventory changes MIR block/local numbering; reusing the
frozen graph matcher by name or ignoring the extra statements would be
unsound. The constructor/as_mut_ptr/intrinsic/pointer-drop components retain
their existing semantics once that gate is earned. Only after the actual
nested SAFE Drop separately proves both generated posts may an exact
SAFE-forget-to-checked-generic-callee call link be reviewed. That link must
preserve the real `Move guard`, cleared drop flag, selected-cell frame, and
reachable shared cleanup from other predecessors.
