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
