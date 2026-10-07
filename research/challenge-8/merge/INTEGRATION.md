# Geometry contract and future actual Rust transfer

## Authorized nonzero stock component

[POINTER-DESIGN](POINTER-DESIGN.md) separates audited public caller ZST exclusion
from standalone generic Challenge obligations. The new fixtures project only
exact add/sub/wrapping and comparison operators; they require explicit nonzero
layout/byte/provenance limits. Checked Rust ghost G2 local formulas are independent
bodies, not imported C axioms. Complete Rust trace, wrapping terminal associations,
resources/copies/FnMut/unwind and actual merge refinement remain OPEN until their
own gates complete. Current executable results are recorded in RESULTS/STATUS.

Geometry preconditions: n>=2; arithmetic n=2m+e,m>=1,e in{0,1}; two original
source halves in one logical source domain[0,n); destination domain[0,n).
For standalone merge_down, ordinary destination decrement additionally needs
D>=1 in the chosen destination allocation; mere validity for the current write
does not justify dst.sub(1). The bidirectional caller discharges this stronger
arithmetic helper precondition. Forward add permits the one-past boundary n.
Comparison results are arbitrary independent Booleans whenever calls return.
No sortedness, total order/SWO, key preservation or comparator purity is needed
for index bounds. A panic stops before the remaining operations; geometry for
normally returning prefixes supplies no Rust unwind/resource proof.

Sorting would separately require sorted halves, a fixed consistent order on
preserved keys and faithful normally returning comparator, together with actual
copy/ownership realization. These requirements must never enter geometry's
unrestricted comparison domain. No actual Rust merge functionality or safety claim.

Required transfer obligations:

- Map every logical cursor/event to the exact source pointer operation and its
  sequencing, including both reference creations before comparator, copy before
  advances, wrapping_sub intermediates, wrapping_add endpoints and final checks.
- Preserve allocation provenance, alignment/validity and same-allocation byte
  addressability; establish ordinary add/sub no overflow/isize/allocation limits
  using actual layout/usize bounds, rather than mathematical integer arithmetic.
- Justify wrapping arithmetic outside allocation and return before any dereference;
  an index -1 is a symbolic displacement, not a legal pointer read.
- Prove source initialization/read permissions, destination writable permissions,
  disjoint copy byte ranges, comparator effects/borrow recovery and frame resources.
  Actual T:FreezeMarker bound stays as in pinned Rust; no new Copy/Freeze restriction.
- Handle ZST explicitly: zero-sized pointer equality/order need not distinguish
  indices; residual geometry permits either choice. Scalar guard/count equivalence
  is not automatically the actual pointer guard for ZST. Ownership semantics remain
  separate even when zero bytes move.
- Restore/retain appropriate ownership under duplicate/outdated temporary copies,
  arbitrary bad comparisons and panic/unwind; final guard is AFTER writes.

No common main-direction STATUS/PLAN/coverage changes, no tool patch or branch
merge. This component does not cover public SmallSort UB categories or prove
Rust pointer accesses/copy/FnMut/initialization/unwind safe.

Pinned pointer definitions for transfer review: const_ptr.rs wrapping_add1164
and wrapping_sub1243 preserve attached provenance and permit leaving/re-entering
an allocation before dereference; mut_ptr.rs ordinary sub requires the nonzero
byte range to stay in one allocation and count*size fit isize. These source
documents explain the intended bridge, not a verified permission/overflow lemma.
Math n may be unbounded; transfer additionally constrains actual n to usize,
relates slice allocation/layout limits to every offset and handles zero-sized
byte displacement separately. No numeric-address rewrite supplies provenance.

## Accepted occurrence output model

Goal A now proves guard-conditional ID permutation, destination coverage and
exact chronological trace/output correspondence for arbitrary comparison and
residual answers. See RESULTS for accepted SHA/run. IDs are original input
positions, one per occurrence; they are independent of keys and of allocation
addresses. Signed potential permits temporary duplicates and crossed intervals;
final scalar guard after copies is essential. A negative without it gives[0,0]
from[0,1]. This result does not supply ownership for those temporary copies or
panic paths. Scalar/pointer guard realization must be proved separately,
particularly for ZST whose distinct logical indices may share addresses.

Functional B premises are one immutable pullback SWO relation on these
occurrenceIDs, both original halves sorted by it, every normallyreturning exact
comparator answer matching rel(rightID,leftID), and odd choice matching logical
left<left_end. Such key/order/fidelity premises belong only to functional B;
they are absent from the accepted unrestricted geometry and Goal A. Constructive
rank correspondence must be checked before any B rank theorem is applied.

## Accepted stable functional composition

Goal B is now accepted at4e546ec150cf655681516be727aa1a79f525fc56/run37681190236.
Its finite fixed SWO is a pure pullback relation on original occurrence IDs,
constructed domain0..n-1. General predecessor-count bridge bodies are rechecked
unchanged; original-half sortedness and every source comparator answer derive
rank premises, with sorted/stable output projected back to the same relation.
No assumed embedding or unchecked reference merge. Forward ties select left,
reverse ties select right; residual scalar h=endA<endD derives final guard.
All full A output/coverage/trace/count posts are retained under these B premises.

Future Rust transfer must additionally realize the ID-to-value association,
preserve immutable keys through all comparator effects and copies, justify
faithful normal comparison summaries (or stop at a conditional functional result),
and connect actual calls to the two read pairs/selected source IDs and scalar
residual. Its normal sorted/stable result requires actual final pointer guards
to agree with the scalar equalities or a separately proved ZST treatment.
Destination initialization and one owner per live T require permission/ownership
proofs for copy_nonoverlapping, not just mathematical ID counts. Arbitrary bad
comparisons may copy duplicate IDs before panic; A proves no Rust unwind cleanup.

These sorting assumptions are absent from G2 and guard-conditional A. The
mathematical phase is complete; actual Rust/functionality/safety and public
Challenge admission remain open. No runtime, signature or trust model change.
