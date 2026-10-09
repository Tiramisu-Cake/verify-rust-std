# O26 wrapper-owner rebase candidate

## Problem and hypothesis

The complete Cloud proof reaches the final `select_unpredictable` wrapper call,
then fails at `std/lib.rsspec:462`: the checked selector requires
`MaybeUninit_pointer_own<Element>(t, MaybeUninit::new(payload))` for its current
first argument. The constructor and `as_mut_ptr` summaries retain ownership
indexed by an earlier, opaque wrapper value. `close_MaybeUninit` reconstructs a
canonical `MaybeUninit::new(payload)` storage value, while the constructor
contract states only `inner(result) == some(pointer)`, not wrapper equality.
This identity mismatch is an inference from the first error and contracts;
Cloud proof must test it. The outer pointer-drop callee's verified post
preserves the pointer cell value, so this candidate does not rely on treating
the dropped unselected storage as newly initialized.

## Source-only ghost rule

Immediately before opening the two existing `MaybeUninit` storage cells, bind
both old wrapper values to their existing cell and indexed ownership chunks.
After the existing branch-specific storage closes, bind both current wrapper
values. Consume **both** old indexed chunks by opening their defined predicate
and, in the `some(pointer)` branch, opening `raw_ptr_own<Element>(t,pointer)`.
The latter predicate is `true` in the pinned prelude. Call the already proved
`close_MaybeUninit_pointer_own` lemma once for each current wrapper. This
reindexes empty pointer-value ownership to the actual stored values; it grants
no pointee permission, creates no cell, assumes no wrapper equality and adds
no verifier rule. Both sides are handled symmetrically, independent of the
condition. If either old chunk, current cell, or new lemma call cannot be
proved, the candidate fails at that obligation.

The actual std runtime, algorithms, generic signatures, thread token, result
selection, `raw_ptr_own` normal post, false unwind post, guard/forget/drop
logic, leak/dead-code checks, validity and refinement remain unchanged. This
is still the pointer-specialized outer obligation `T = *const Element` with
unrestricted implicit-Sized `Element`, not a generic std theorem. The generic
nested Drop body remains a separate required proof.

## Cloud evidence and refusal rule

Prepare this as an opt-in new source case; the canonical source remains intact.
Require byte-identical ghost-stripped original source and exactly two inserted
ghost blocks at pinned boundaries. Capture fresh NORMAL and readonly complete
MIR, refinement, decoded nine-body records and ten Marshal snapshots before
any certificate refresh. The expected changed records are outer body 7 and
the unit; the other eight must match the canonical snapshot byte for byte.
Compare the actual changed graph, ghost metadata and ordering rather than
assuming this prediction. Old exact-source certificates must refuse the new
source; that refusal is admission evidence only. A refreshed experimental
profile needs new source/unit/body-7 pins, component 17 and A1 component 20
controls, all seven callee proofs before outer, nested Drop, full normal/unwind
and resource checks. Setup, source mismatch and helper failures are
INCONCLUSIVE, never intended ownership negatives or proof acceptance.
