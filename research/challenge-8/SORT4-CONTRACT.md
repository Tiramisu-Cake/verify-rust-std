# `sort4_stable`: proposed full contract and caller audit

Target [smallsort.rs](../../library/core/src/slice/sort/shared/smallsort.rs:610),
blob `e555fce440872898e47fd5114f32eb15401d07df`, unchanged at approval
`54485d632bfca9d69fee853bd6aa30bc330647c9`. Refined on 2026-10-06 under
[SORT4-CONTRACT-PHASE](SORT4-CONTRACT-PHASE.md). This is a research contract,
not an accepted strengthening of the public target or a generic proof. Executed
facts and their domains are recorded in [the closeout](SORT4-CONTRACT-RESULTS.md).

## Current comment, actual body and distinct premises

The current SAFETY comment says only source valid for four reads, destination
valid for four writes, result stored in dst[0..4]. It omits the non-overlap
requirement of each `copy_nonoverlapping`, initialized/reference-valid source,
and the ownership policy for copied representations and overwritten storage.
Alignment, provenance and callback borrowing also need an explicit interpretation
of “valid”. We keep the source/comment unchanged and record the precise
clarification question below.

Five comparisons precede all writes: c1=(s1,s0), c2=(s3,s2), c3=(c,a),
c4=(d,b), c5=(unknown_right,unknown_left). Four one-element copies follow at
lines653–656 in order min,lo,hi,max into d0,d1,d2,d3. The source index choices
form a permutation pi of 0..3 for all five Boolean results: c1/c2 partition the
two pairs; the four cases of c3/c4 in the real comment partition a,b,c,d;
c5 exchanges only the remaining pair. This is a static index argument, not a
new generic checked theorem. Stateful/inconsistent results do not invalidate
that index argument, but they give no sortedness guarantee.

Let S_i and D_j denote logical source/destination slots and their byte regions.
Three conditions must be separated:

- **Local copy safety:** for each j, the region of S_pi(j) at copy time is readable,
  D_j writable/aligned, and these two regions do not overlap. This is mandatory
  per actual copy, independently of ordering and preservation of old values.
- **Sequence preservation:** each not-yet-copied source representation stays equal
  to its representation at the end of c5 until its copy. A sufficient spatial
  condition is D_j disjoint from every S_pi(k) for k>j, in addition to local
  non-overlap. Full source/destination range separation implies both conditions. For arbitrary
  T, an earlier overlapping write could also invalidate a later T representation,
  so continued source validity/readability is a safety obligation. The concrete
  i32 shift only demonstrates loss of values; every i32 bit pattern is valid.
- **Original-value functionality:** callbacks preserve the relevant original
  element values and comparison keys, and compare by a fixed strict weak order.
  Then pi is a stable sorted permutation of the original occurrences. Safety
  itself has no purity/order/Copy/Freeze restriction.

Full range separation is a simple sufficient, comparator-independent contract;
it is not proved necessary for every constrained overlap pattern. Coincident
ascending ranges violate the first condition at the first copy. A destination
shifted by one cell violates the second condition despite distinct source and
destination for each individual copy. Sortedness can survive multiset loss.
Concrete observed outcomes are separate from a classification of all overlaps.

## Resource notation and sufficient unrestricted safety precondition

These predicates describe required resources, not newly assumed VeriFast axioms:

- `Storage(p,4,I,P)` describes four logical slots, initialization map I and actual
  provenance/permissions P for pointer arithmetic/access, including alignment,
  bounds and allocation liveness. `RawDst(d,I)` is writable scratch storage without
  a prior independent drop obligation; I may be all-uninitialized.
- `SrcOwn(s,V)` packages valid initialized source representations V with ONE
  logical ownership sequence, full recoverable cell resources and the resources
  needed to create/end shared borrows. Ownership includes resources reachable
  from elements; it is not just their bit patterns.
- `Shadow(p,V)` describes copied representations with storage permission but no
  independent `T.own`/right to drop. It cannot automatically yield unrestricted
  owned reads, moves, or generic shared references into that copy.
- `Cb(F,Q)` is the actual mutable callback resource with its current state and
  normal/unwind invariant Q. Q permits arbitrary legal state/interior effects.
  `Frame(H)` separates untouched storage from callback-accessible resources.

A sufficient resource-oriented precondition is
`SrcOwn(s,V0) * RawDst(d,I0) * Cb(F,Q0) * Frame(H0)`, with the full byte ranges
separated for non-ZST, four valid logical positions at both bases, and legal
pointer formation/borrowing for arbitrary valid T/F. Every callback must respect
Rust aliasing/lifetimes and return (or unwind with) a valid current T/F invariant.
Legal effects through UnsafeCell and callback-accessible state are preserved.
The destination permission must be available when copies execute; the callback
cannot invalidate allocations or outstanding permissions. Shared source borrows
must end/recover before the post requires exclusive source resources.

Destination **initialization is not required**: actual callers use MaybeUninit.
Raw copying can overwrite initialized storage, but if it contains old live
resources their disposition must be specified separately. Silently returning
those resources after overwriting their bytes is unsound. Discarding them may
leak; a leak is not automatically a demonstrated memory UB, but it cannot meet
this complete resource contract. The old i32 control has initialized Copy dst
and therefore no such independent resource obligation.

Non-Freeze is allowed; reads after callbacks observe current valid state, not
necessarily V0. Non-Copy/destructor-bearing T is allowed; duplication of bytes
never proves two independent droppable sequences. Padding may remain
uninitialized; a byte-copy specification must not require every padding byte
initialized or give those bytes a logical scalar value.

For ZST, pointer equality is compatible with empty-region non-overlap. Still
require nonnull/aligned reference-valid pointers, legal logical add operations,
and four logical ownership occurrences. Empty byte separation does not supply
independent ownership or permission to drop duplicate logical occurrences.
This is an open generic proof/model gate; no i32 result establishes ZST.

## Full normal post and ownership protocol

Let V5,Q5,H5 be the current state after the fifth successful callback. Under
sequence preservation the copies yield `D_j = representation(V5_pi(j))`; they
leave source representations V5 intact and do not invoke any destructor.
The normal post must contain exactly ONE ownership sequence, current F/Q and
frame resources, both storage permissions and no outstanding local borrow debt.
It must account for all four destination slots as initialized representations.
It must not return two `SrcOwn` predicates for the same non-Copy elements.

Two explicitly distinguished uses are possible, requiring a proved resource
transport rather than an assumed ownership bridge:

| Protocol | Normal post | Allowed subsequent ownership use |
| --- | --- | --- |
| Retain originals, scratch replicas | `SrcOwn(s,V5) * Shadow(d,pi(V5)) * Cb(F,Q5) * Frame(H5)` | Source may be used/dropped according to its recovered resources; scratch stays MaybeUninit and is never independently dropped. Generic access through scratch still needs a justified shared/relational permission protocol. |
| Move logical ownership to result | `Shadow(s,V5) * DstOwn(d,pi(V5)) * Cb(F,Q5) * Frame(H5)` | Destination may own/drop the elements; source cannot independently drop/move them until ownership is explicitly restored. Actual bytes at source are not erased by this function. |

For the generic proof proposal, the first form is the bounded target post:
it expresses the physical originals and nondropped scratch used by callers.
It deliberately does not pretend to solve the later scratch comparator/move
protocol. That relational access/ownership transport is a named remaining
callee-composition dependency. The second form can only be composed with callers
that also recover ownership on every later unwind before dropping original v;
this function provides no runtime invalidation or cleanup guard for that task.
No protocol is a second ownership sequence created by byte copying.

When claiming functional original-element preservation, add separate premises:
all callbacks preserve the elements/keys being sorted and implement the same
strict weak order throughout the call. Normal result is then sorted, an exact
permutation of original occurrences and stable for equivalent keys. Updated
callback counters/effects may be permitted if they do not alter these premises;
requiring absolutely unchanged F is stronger than necessary for functionality.
Neither a Freeze bound alone nor five arbitrary Boolean answers imply order.

## All five panic posts

For k=1..5, let `(Vk,Qk,Hk)` be the actual state after the first k-1 successful
calls and the effects of the kth panicking callback. Full unwind target:
`SrcOwn(s,Vk) * RawDst(d,I_k) * Cb(F,Qk) * Frame(Hk)` with all temporary
reference/lifetime resources recovered, allocations/permissions intact, exactly
ONE current ownership sequence and no leak/debt escaping the function.
`I_k` equals I0 except permitted callback effects; **no sort4 write** has occurred.
If callback-accessible destination/frame storage changes legally, its post uses
that current state, never falsely restores I0/H0. On actual separated scratch
call sites there is no callback access to this scratch, so its incoming state
is preserved. No sortedness, permutation of pre-call values, rollback of F or
rollback of interior mutation is promised on unwind.

| Site / actual line | Arguments | State to recover on that direct panic exit |
| --- | --- | --- |
| c1 / 626 | s1,s0 | Current resources after c1 effects, no prior comparison; original dst state modulo legal callback effects |
| c2 / 627 | s3,s2 | Effects of completed c1 plus panicking c2; includes outstanding resources from earlier sharing |
| c3 / 641 | c=s_(2+c2), a=s_c1 | Effects of c1,c2 plus c3; no output copy |
| c4 / 642 | d=s_(2+!c2), b=s_(!c1) | Effects of c1..c3 plus c4; no output copy |
| c5 / 649 | selected unknown_right,unknown_left | Effects of c1..c4 plus c5; no output copy |

All five are real possible panic sites for an unrestricted comparator. There
are no body-local destructors or guard recovery edges to execute a trailing
normal ghost helper on direct unwind. Returning only borrowed comparison debt
would not satisfy this full post. Resource/borrow recovery for these exits is
unproved; source control-flow analysis only establishes absence of body writes.

## Mapping to actual callers

Static mapping at the same std blob, not verified whole-caller composition:

| Caller/path | Actual source and scratch ranges | Why the spatial/initialization premises hold |
| --- | --- | --- |
| `small_sort_general_with_scratch`, direct sort4, lines253–255 | v[0,4)→scratch[0,4), v[h,h+4)→scratch[h,h+4), h=floor(len/2) | len>=8, h>=4; len+16 scratch check; separate mutable v/scratch borrows. Source initialized T, destination MaybeUninit storage. This branch is selected after the size<=16 && len>=16 sort8 branch is excluded. |
| `sort8_stable`, lines671–672 | v[0,4)→temp[0,4), v[4,8)→temp[4,8) | Each half has four initialized source slots; temporary scratch provided by the outer caller is distinct from v and destination. Helpers' pointer comments alone do not state this separation. |
| Outer first sort8, line243 | v[0,8), destination scratch[0,8), temp scratch[len,len+8) | len>=16 and size_of(T)<=16; three regions distinct, auxiliary scratch bound len+16. |
| Outer second sort8, lines244–249 | v[h,h+8), destination scratch[h,h+8), temp scratch[len+8,len+16) | h>=8, h+8<=len; both source and destination halves disjoint (adjacent at len16), temp regions distinct. |

`small_sort_general` creates stack MaybeUninit<[T;48]> and supplies a
MaybeUninit slice. Those scratch copies have no automatic T destructor. Incoming
initialized scratch supplied externally still has the caller's MaybeUninit
resource policy; the helper cannot assume a hidden live T owner it may discard.
`FreezeMarker` is implemented for Freeze in shared/mod.rs and bounds these
callers, including sort8, but does not imply Copy and is absent from sort4.
It makes a caller-level no-interior-mutation argument possible, not a restriction
on the public safety target.

If a second sort4 panics, earlier invocations may already have initialized some
scratch. Those replicas remain nondropped; original v is still the actual
owning/drop-eligible allocation. Within sort8, no outer destination writes have
occurred until both sort4 calls return and merge begins. Later scratch insertion,
merge, CopyOnDrop restoration and successful ownership return to v are separate
full caller obligations. They require a relational scratch-access/ownership proof;
this spatial audit does not discharge them or reuse an unproved callee summary.

## Established concrete theorem and required contract clarification

Run37459631500 proves actual-body sorted exact full-range i32 multiset and
unchanged source, plus separate complete tagged-item stable permutation;18/18
covers. Its fixed disjoint initialized buffers, concrete Copy layouts and pure
nonpanicking comparison are narrower than the resource contract above. The new
contract suite reuses the exact unchanged values harness; it adds concrete
counterexamples/witnesses, not unrestricted safety or stronger UB instrumentation.

Precise question for the owner/organizer (recorded only, not sent externally):
Does “valid for four reads/writes” in this target intend full range separation
and a single-owner nondropped-scratch protocol, or must the verification contract
cover arbitrary overlapping writable ranges satisfying that literal short
comment? The actual coincident route requires additional local non-overlap;
original-value functionality also requires cross-copy preservation. Acceptance
of a clarified sufficient research contract must precede claiming coverage of
the public challenge target. No runtime/source comment or signature is changed.
