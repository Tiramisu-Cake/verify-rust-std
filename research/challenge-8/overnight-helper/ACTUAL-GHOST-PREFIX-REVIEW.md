# Actual pointer helper: initialized-slot ghost prefix, 26.10

Design/review checkpoint before a fresh hosted projected run. The obligation is
the unchanged `core::hint::select_unpredictable` body, specialized to
`T = *const Element` with unrestricted `Element`. The target precondition owns
the current thread only. Its normal post returns the selected complete pointer
and the same thread; its unwind post is `false`. No `Element` pointee permission
is assumed or created. This note does not claim the complete helper verified.

## Observed blocker and the smallest existing preparation

O10, run `37707814634`, reaches the actual call `drop.drop_in_place()` at
`verified/lib.rs:112` and fails at the checked method's initialized-cell
precondition `*slot |-> ?value` (`verified/lib.rs:50`). The first error is
`No matching heap chunks: points_to<*Element>(__result2, _)`. The wrapper
slots exist, but their `MaybeUninit` storage has not been projected to
initialized raw-pointer cells. The checked drop method's post preserves the
**same pointer value** at the slot, thread, and no-unwind; its accepted
pointer-specialized glue does not require or grant a pointee cell.

The exact existing S6 projection sequence is the minimal candidate:

```rust
let false_ptr = false_val.as_mut_ptr();
//@ std::mem::open_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);
//@ std::mem::open_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);
// ... unchanged two pointer-select calls and guard construction ...
let guard = DropOnPanic { inner: guard };
//@ if (condition) { } else { }
drop.drop_in_place();
//@ std::mem::close_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);
//@ std::mem::close_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);
```

The opens convert each initialized wrapper cell into an initialized
`*const Element` **value** cell at the corresponding local slot. The two
pointer intrinsics choose opposite slot addresses without producing a new
cell. The proof-only branch split identifies the unselected slot passed to
drop while framing the selected cell. The pointer drop preserves its cell's
value, so both closes reconstruct the original initialized wrappers; no
replacement or arbitrary value is invented. This explains the normal path
through the next operation without a guard-own assumption. The separate
guard destructor and all retained cleanup predecessors remain obligations;
neither a split nor the no-unwind pointer-drop rule may simply erase them.

`prepare-select-pointer-actual.py` already creates this exact projection
variant, checks unique insertion anchors and ghost-stripped runtime identity.
Frozen S6 `Sort4SelectIntrinsic.projection_ghosts` contains these exact five
strings. Its opt-in projected admission pins the original `hint.rs` bytes,
the specialized signature and unchanged body apart from these insertions,
ghost order/coordinates, 36 typed locals, all 19 blocks, calls, operands,
normal/unwind successors and the shared cleanup. Reuse this gate and source
preparer on the 26.10 combined profile; no additional frontend overlay is
justified for these five ghosts. The source/extractor-to-model correspondence
and the accepted pointer-only drop rule remain explicit trust boundaries.

Historical S6v4 run `37656621026` proved this prefix through both closes and
then failed at the ordinary `std::mem::forget` precondition for private
`DropOnPanic.own`. That result belongs to the older profile only; it predicts
the next 26.10 blocker but cannot certify the new combined profile.

## Fresh gate and interpretation

Run only the canonical projected variant first, under the exact current
profile and pinned source. Require source identity, NORMAL/readonly
export/decode, full projected MIR admission, refinement, and full VeriFast
trace. Expected first proof advance is the checked pointer-drop precondition
passing and both wrapper closes executing. If the next error is nominal
guard-own at actual `forget`, classify as a truthful **partial helper** result,
not a pass. A source/admission mismatch is setup inconclusive; do not count it
as a resource failure. Existing S6 negative source/MIR mutants remain its
admission controls. A fresh semantic profile requires component and baseline
regressions at a meaningful checkpoint.

If further ghost commands are needed for `forget`, guard cleanup or final
`assume_init`, first define their resource invariant, source anchors, exact
normal/unwind behavior and trust boundary in a separate BEFORE review. Admit
only a new exact ordered sequence and its full typed MIR (including every
cleanup predecessor) in a **separate** patch. Do not alter the frozen S6
certificate or assert `DropOnPanic.own = true`. In particular, the normal
continuation must retain its selected initialized slot through a no-destructor
`forget` operation; any reachable destructor needs a separately proved
recoverable slot protocol. The H2 guard/drop path is under independent review.
