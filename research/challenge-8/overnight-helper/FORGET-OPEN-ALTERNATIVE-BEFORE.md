# Alternative actual `forget` route: open guard ownership at the caller

Design review only; no implementation or accepted proof. This refines
`OWNERSHIP-SPLIT-BEFORE.md` after recognizing that a function declared outside
the actual helper cannot name its function-local `DropOnPanic` type. Adding a
native helper inside the actual runtime body would violate exact-source
identity. The alternative keeps the actual Rust body and `mem::forget` call
unchanged.

## Linear resource path

After the two wrapper opens and branch split, transfer exactly the selected
initialized pointer-value cell `*S |-> p_S` into truthful nominal
`DropOnPanic<*const Element>.own(t, guard)`. The unselected cell `*D |-> p_D`
remains independent. The accepted pointer-specialized `D.drop_in_place()`
preserves that cell and cannot unwind; close only the unselected wrapper.
Immediately before the actual `mem::forget(guard)` call, ghost-open the
nominal owner **in the caller**, recovering `*S |-> p_S` once. The guard
value remains a valid Rust bit-pattern and is moved into `forget`; the opened
cell is held as an independent frame. The MIR must prove the guard drop flag
clears with that move, there is no runtime operation between open and move
that can unwind or invoke Drop, and no reachable guard destructor can run
without its owner. After the call, close the selected wrapper with the
returned frame cell. No `Element` pointee right or duplicate slot appears.

## Required callee result, not yet available

The intended redirect target is a **public, independently verified generic**
unsafe adapter with the exact new-std body
`{ let _ = ManuallyDrop::new(t); }`, generic `T`, pre current thread only,
post same thread, and false unwind. A caller holding `*S |-> p_S` and an
unrelated frame must keep both by the ordinary separation rule. This adapter
does not need to name the local guard type or receive its nominal owner.
It proves a no-destructor value move under the existing trusted
`ManuallyDrop::new` identity correspondence; it does not assert that
`DropOnPanic.own` is true or manufacture a cell.

**Current G1 evidence does not supply this callable callee theorem.** O7/O11
positive fixtures inline the exact forget body in a public frame probe;
`checked_forget_generic<T>` is absent there. Historical standalone generic
callee runs executed body, return and leak checks but failed the mandatory
dead-code gate on the synthetic unwind return before the accepted 26.10 CFG
repair. A fresh public generic callee fixture on the accepted CFG profile is
the first independent obligation. Its full NORMAL/readonly graph, source
identity, refinement, return, leak, dead-code, normal/unwind contract and
negative controls must pass before a summary can be used. A separate framed
**call** probe is needed; direct-body framing alone is insufficient.

The actual SAFE `std::mem::forget<DropOnPanic<*const Element>>` retains its
stock generic contract requiring `<T>.own`. Redirecting only this one exact
typed call to the proved unsafe adapter after caller-side owner opening is a
new trusted Rust/frontend correspondence: the pinned safe std body and the
checked adapter body perform the same ManuallyDrop move and neither runs
Drop. This is a deliberate exception to the stock SAFE call interface, so
it must be reviewed as such and fail closed on source version, guard ADT,
generic substitution, callee DefPath, operand Move, guard drop-flag order,
normal/unwind targets, and any extra operation. No global SAFE `forget<T>`
specification is weakened. The local checked adapter must be proved in the
same profile before the redirect consumes its summary.
The frontend must instantiate this generic local adapter with the decoded
actual nominal ADT type without spelling the function-local Rust type in the
adapter source; inferred type arguments and the exact `Move` operand are
separate admission checks. Failure to express that typed instantiation is a
linkage blocker, not license to rename or rehome the guard.

## CFG and admission constraints

The actual MIR retains the `forget` call's cleanup successor to the shared
cleanup block. Redirect through `FnCallOutcome` so the original call and
unwind structure remain visible. A false-unwind callee should make that edge
unreachable, while the shared cleanup block remains reachable from its other
predecessors. The historical G1 call lane failed mandatory dead-code on a
synthetic unwind return even after its body/return/leak proof. If the same
failure occurs, record the emitted AST and successor inventory; only a
source/typed-call-certified correction that reconciles **emitted** CFG with
successor inventory is admissible. Never erase the MIR cleanup target, turn
off dead-code/unwind checks, or suppress a cleanup with another reachable
predecessor. The accepted `ManuallyDrop::new` CFG repair is precedent for a
causal, narrow fix, not authorization for general call pruning.

The frozen S6 five-ghost sequence closes both wrappers before `forget`, so
it cannot serve as this ownership path. A separate exact-source overlay must
admit the ordered actions: open both wrappers; split and close guard owner
from `S`; drop `D`; close only `D`; open guard owner just before forget; call
unchanged forget; close only `S`; continue to final wrapper select and
`assume_init`. Pin exact ghost text/positions, full specialized actual source,
ADT fields and generic binding, all typed local/statement/call identities,
normal and unwind edges including the common cleanup, and readonly
refinement. Missing/duplicated/wrong-value `S` or `D` cells, a wrong selected
address, extra Element right, false post, wrong call/operand, source mutation,
and altered cleanup/drop-flag must reject at their intended obligations.
The generic nested Drop body remains an independent H2 normal/unwind proof;
the outer helper proof cannot rely on a vacuous `own=false` template.
