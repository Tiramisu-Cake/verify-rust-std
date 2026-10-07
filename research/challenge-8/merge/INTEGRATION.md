# Geometry contract and future actual Rust transfer

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
unrestricted comparison domain. No full merge functionality or safety claim.

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

Functional B premises will be one immutable pullback SWO relation on these
occurrenceIDs, both original halves sorted by it, every normallyreturning exact
comparator answer matching rel(rightID,leftID), and odd choice matching logical
left<left_end. Such key/order/fidelity premises belong only to functional B;
they are absent from the accepted unrestricted geometry and Goal A. Constructive
rank correspondence must be checked before any B rank theorem is applied.
