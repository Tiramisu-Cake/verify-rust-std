# Proposed integration, without merging either direction

Add a link to this direction's STATUS from the common research index/coverage
only after review. Preserve both independent journals and budgets. Do not copy
this branch's frozen common STATUS over the live sort4 branch's checkpoint.

The eventual coverage row should have three separate columns:

| Obligation | Evidence supplied here | Required integration |
| --- | --- | --- |
| Mathematical CE sequence sorts N=9/13 | N9 full rank/identity; N13 binary/identity plus written general-order transfer (full machine rank pending) | Fixed total preorder on all preserved keys, normal comparator returns |
| Complete occurrence permutation | Accepted arbitrary-decision identity-count theorem for both networks | Actual helper realizes token swap without duplicate/drop/leak |
| Actual call schedule | Full-source hash and ordered 25/45-call certificate | Keep same source version; recertify on any source change |
| swap_if_less normal/unwind Rust posts | Specification only | FnMut effects/borrow recovery, pointer provenance/alignment/validity, read/copy/ManuallyDrop resources |
| select_unpredictable used by swap | Dependency only | Verify actual *mut Element instantiation at this source/profile, full chosen-pointer/no-unwind post |
| Public small_sort entrypoints | None | Dispatch, insertion, merge, arbitrary valid lengths and all safety obligations |

No network theorem supplies Rust UB coverage, a verifier soundness/admissibility
result, or a completed public target. Do not stub actual swap_if_less with this
unproved contract and describe the result as a verified Rust network.

## General-order transfer and machine-proof boundary

For any fixed finite input in a total preorder, partition occurrences into key
equivalence classes and enumerate the occurring classes increasingly. Map each
class to its integer position. This assigns an integer rank to every occurrence
and preserves/refects strict comparisons on all keys in this input. Because CE
only permutes occurrences and keys are fixed, no new class appears; the same
ranking applies throughout the network. Rank CE is therefore the exact key CE.

For integer ranks and arbitrary integer threshold t, define projection h_t(x)
to be false when x<=t and true when x>t. A checked local min/max lemma states
that h_t(min(a,b))=h_t(a)&&h_t(b) and
h_t(max(a,b))=h_t(a)||h_t(b). Induction over the finite exact call schedule
therefore commutes rank-network execution with Boolean-network execution.
N9 hosted proof checks every composition and the full rank application. For N13,
the local CE lemma and Boolean theorem are checked, but the complete rank unit
timed out; induction over45 calls here is a written mathematical argument.
N13b is prepared to machine-check the entire composition without assumptions.

If adjacent output ranks x,y had x>y, take t=y. Their projected outputs would
be true,false, contradicting the Boolean network's adjacent-order theorem.
Thus every adjacent output rank is nondecreasing. Transitivity of <= gives
global order for every i<j. The class-rank correspondence gives the claimed
general key-order theorem, including ties, without an integer-key or Copy type
restriction. A strict weak order transfers through its totally ordered quotient
of equivalent keys. An inconsistent/partial comparator has no such bridge.

Occurrence permutation is independent: each abstract CE merely chooses between
(A,B) and (B,A), and the checked count of any arbitrary token q is unchanged.
Universal q yields equality of multisets of complete occurrences. For unique
input IDs every ID remains exactly once; equal keys never identify distinct
occurrences. No relative-order claim for equal keys follows.

The finite-class/threshold argument is ordinary mathematical transfer, distinct
from machine verification of the ghost lemmas and from the still-open Rust
ownership bridge. Results must identify these boundaries explicitly.
