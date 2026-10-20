# R11 P0c checked-cleanup candidate review

## Decision

**GO for the bounded Cloud hypothesis only.** The candidate is suitable to test
the existing checked `core::mem::drop` route on the generated diagnostic body.
This is not a conclusion that the call discharges the local ownership, and it
does not close P0c or permit proof credit.

## Review findings

`_observer` retains the pinned quicksort signature and guard bytes up to the
original `small_sort` call. The P0c suffix places the checked `drop` after the
threshold assertions and immediately before each of the two diagnostic early
returns. The corresponding N-false31 observer follows the same pattern. The
P1 caller preserves its full signature and guard/call prefix; its separately
labeled cleanup appears only in the synthetic tail after that prefix. No source
quicksort return, model rule, guard, or ownership premise is changed.

The construction test checks both P0c/N-false31 exits, assertion ordering,
source-prefix preservation, the absence of a fabricated `None` assignment,
and the P1 diagnostic-tail boundary. It establishes generated source shape
only. It cannot establish compiler lowering or ownership behavior.

The unresolved risk is material and correctly stated in the design:
`Option<&T>` is `Copy`, so the by-value `drop(left_ancestor_pivot)` may consume
only a copied argument while leaving the original local's `Option_own` chunk
live. The existing checked `drop` contract and active `proof_std`/MIR lowering
must decide this in Cloud. A failure keeps P0c open. The test must retain both
`None` and `Some(&T)` cases, all normal/unwind/abort posts, exact source-pair
and compiler bindings, and the comparator/guard obligations. Do not add a
`None` premise, a `mem::forget` escape, or an `end_ref` step without its exact
place/lifetime tokens.

## Evidence limits

R10's bounded P0c source observation reports a leak in the generated
`a1_guard_observer` body at `verified/lib.rs(139,1-2)`. It does not show a runtime
leak in actual quicksort. The design correctly separates source applicability
from the open Copy/MIR question and keeps all claims below proof credit until
Cloud produces the needed verification and exact-pair receipts.
