# Actual bidirectional merge: arbitrary-length resource composition

This is a prepared design, not a verified new component. It follows the exact
repository SmallSort blob `40939f922bcb6fdc7ee0d30427fa861827043827` and the
conditional actual merge_up/down proof first established at
`5bbd2ef2613106fdc38bd8aeea930cf344390275`. The fresh Cloud transfer uses proof69adf2f624ff323b077d6b22846567b4368311fe,
Build be12e7b2-e674-49c8-bce2-d0a8c68d9c1d: actual up/down full conditional
gates pass again; bounded bidirectional2/3 is INCONCLUSIVE after VFtimeout124,
204main executions,5return/6leak. Odd-source association and a C1copy path
are reached, but the full body contract remains OPEN. Strengthened stack and
pinned panic-origin admission pass separately. Source-pair current-value turnover
and cleanup hidden-type controls are unverified isolated drafts. The source-level
destination-alias observation passed with exact helper/compiler pins; it supports
the need to derive the F footprint, not public-caller raw-alias admissibility.

## Contract and trust boundary

First generalize the existing **conditional safety component**, keeping
positive stride, valid aligned endpoint/object bounds, source/destination
numeric separation and explicit resources. Require an owned source array of
length n >= 2, an option-valued writable destination array of length n, and
current F ownership. This does not derive these resources from the actual
shared slice. The slice projection and exact unchanged runtime body must
remain separately source-linked, and its normal/unwind summary cannot be
used until that body passes every gate.

Safety permits arbitrary Boolean answers and callback effects compatible with
the stated separation resources and the admitted FnMut normal/unwind protocol.
This is not a claim about every Rust closure carrying an arbitrary raw alias to
the destination. The callback's owned/shared resources must permit its actual
effects while preserving the caller's framed destination cells. This frame
compatibility must be derived at each caller, not inferred just from the type
`FnMut(&T, &T) -> bool` or source/destination numeric separation. Normal
return preserves the current source-array owners and current F owner and
initializes every destination option. Callback unwind preserves all source
and F resources and precisely the writes already completed. Final guard
panic occurs after all destination writes, preserving those resources.
Neither outcome creates destination T ownership or restores the callback's
entry state. A destination value records the selected value at that copy;
it need not equal the value at that source index after later callbacks.

The existing W1/C1/M2/cleanup/usize/stack semantic dependencies remain explicit
and independently pinned. The following composition adds checked lemmas and
resource predicates only; it introduces no trusted array, callback, equality
or ownership axiom. Full M2/cleanup admission and exhaustive stack def-use
admission remain separate gates. ZST, arbitrary invalid destination bytes,
standalone Challenge and public callers are not covered by this first domain.

## Two loop phases

Write n = 2m + e, m >= 1, e in {0,1}. At the start of iteration k < m:

| State | Source cursor indices | Destination state |
| --- | --- | --- |
| before merge_up | a, m+k-a; m-1-k+d, n-1-d | [0,k) and [n-k,n) contain recorded copied values; other slots retain their old options |
| after merge_up, before merge_down | a+up, m+k-a+(1-up); reverse cursors unchanged | slot k additionally contains the recorded forward value |
| after merge_down | forward cursors above; m-1-(k+1)+d+down, n-1-d-down | slot n-1-k additionally contains the recorded reverse value |

Here up denotes the actual forward left-selection bit, and down the actual
reverse right-selection bit. Boolean steps are ghost witnesses of real
callee results, not predetermined comparator answers. Keep the full current
source list and owners in both phases. Extract the two distinct source cells
for one callback, frame the remainder, call the already verified actual
callee, and restore the two current returned values with the existing
two-hole array lemmas. Restore them before extracting the next pair: source
indices across the two calls may overlap. Positive stride is required for
the pointer/index association; it does not create any resource.

For merge_up, a <= k and k < m give a < m+k-a. For merge_down, its left
index is at most m-1 and its right index is at least n-1-k >= m+e. The
destination indices k and n-1-k are distinct because k < m. These pure
inequalities should be discharged through checked G2 geometry, with actual
pointer expressions linked separately to index provenance and C1 bounds.

Use either individual destination-hole extraction/restoration or the existing
two-hole scratch predicate, retaining the other slot's old option on forward
unwind and the newly copied forward value on reverse unwind. A blanket
"partial output" predicate is insufficient unless it entails these exact
stages and preserves every untouched old option. Record copied values in
separate trace lists; do not equate them with a later current source list.

At k=m, reverse source index d-1 may be -1. Only wrapping arithmetic may
leave and reenter the allocation; the two terminal wrapping increments
produce end indices d and n-d without granting read permissions. If e=1,
the ordinary address comparison chooses the middle copy source. Its address
must be associated with an existing current source cell before copying into
destination index m. Preserve both actual parity branches and the final
panic guard.

## Caller and functional dependencies

The source audit in CALLER-C1-AUDIT.md locates three callers and their
different destination initial states. It is not a resource derivation.
Resolve shared-slice read access/current ownership without an automatic
slice.share-to-T.own conversion. Copying bytes into scratch is not a proof
that a second owner exists. A subsequent ownership transfer or CopyOnDrop
restoration must account for the unique source owners and the corresponding
destination byte values.

The actual bidirectional signature already has T: FreezeMarker. A proved
bridge may justify stability of the relevant representation under shared
borrows, but cannot assume purity of F or freeze indirect pointees. The
current conditional safety summary allows current values to change; it does
not imply that copies from earlier iterations still match those values.
Establish the necessary representation/resource association explicitly
before caller ownership transfer. Functional G2/A/B composition separately
requires fixed keys, a strict weak order and faithful normal answers. None
of those ordering premises belongs in unrestricted callback safety.

An independent review exposed an explicit frame hypothesis: a comparator may
capture a raw destination pointer, write through it and then panic. Valid raw
pointer writes alone are not excluded by its Rust function type. For example,
with initialized, separate u32 source/output cells, a callback can execute
`unsafe { dst.write(9) }; panic!("frame probe")` before the merge's copy. The
destination then differs from its old option if the callback unwinds. This is
a source-level candidate counterexample to an **unqualified** exact-destination
frame claim; `callback-destination-frame-probe.rs` preserves a concrete
standalone reproducer with an unchanged copy of merge_up. Its source admission,
compilation and execution have not been run. The
conditional separation contract must show why that callback lacks the required
framed write permission, or derive a more appropriate caller-specific resource
protocol. Do not silently identify "lawful Rust callback" with "callback
satisfying this VF resource contract." Existing actual callee proofs and their
posts are preserved; this design makes their callback-resource applicability
obligation explicit rather than changing those posts.

## Required matrix and decisions

1. Checked phase frame and array extraction/restoration, arbitrary n and
   arbitrary lawful up/down choices, including overlapping source pairs
   across calls and independent frame preservation.
2. Exact callback unwind before the forward copy and before the reverse
   copy; earlier writes remain, untouched destination options remain exact.
3. Both even and odd normal paths, terminal -1/reentry, residual guard panic,
   all source/F owners and destination chunks preserved. Check actual
   callees at the same source version and keep leak/dead/unwind gates.
4. Intended resource rejections for a missing owner, duplicate source owner,
   wrong suffix-stage claim, stale copied-value/current-source equality and
   access at the reverse -1 cursor. Add a destination-alias callback frame
   probe at its write permission before treating resource-compatible callback
   effects as universal Rust callback effects. Each must reach its declared obligation;
   setup or unsupported failures remain inconclusive.
5. Fresh same-input stack declaration/call/field/address/ordered-def-use
   admission, full export/decode/refinement and combined accepted regressions.

A green isolated resource phase permits the next composition step, not an
actual-function claim. A counterexample to unchanged-value assumptions must
be retained and corrected independently of safety. GitHub dispatch currently
rejects HTTP422 (Actions disabled for the user); no local execution or new
hosted result is part of this document.

## Conditional current-owner handoff draft

`current-owner-handoff-cases.rs` isolates a two-cell resource operation. It
requires destination bytes already equal the CURRENT source pair, in identity
or swap order, then moves the existing source T.own chunks onto those destination
cells while retaining source points-to bytes without ownership. Current F/thread/
type resources frame; equal-valued pairs are allowed. It performs no runtime
copy, callback or cleanup and does not derive that equality/permutation from the
actual merge. In particular, earlier recorded copies are not current source
values after an arbitrary callback. This ghost component remains UNTESTED until
a fresh Cloud run; it is a partial ownership-transfer component, not actual caller
or unrestricted safety acceptance. Positive size/four-cell separation/object
limits are explicit; Generic/ZST and the Freeze/share bridge remain open.

Fresh read-only cleanup review retains the kernel trust gap: strict exit checks
Chunk.targs, but not predicate terms/closure captures, coefficients or sizes.
The exact frontend rejects literal hidden `<&'cmp T>.full_borrow_content`, yet
opaque T.own/F.own and every marker's provenance still need a semantic closure
argument. All surviving chunks/terms must remain typable in the outer environment;
current bounded admission/green controls do not establish this invariant. No new
kernel rule is implemented or accepted by this draft.

The same draft now includes native-usize arbitrary-n identity handoff: structural
recursion consumes each existing source owner once into the matching initialized
destination array, retaining source bytes without owners. Current lists must
already be equal; whole ranges are disjoint with explicit bounds/limits. No
provenance inequality is required. A separate stock26.10 probe of the exact
fixture will distinguish this resource component from the experimental kernel;
all cases/checked bodies and refusal gates remain required. No actual copy-count-n,
CopyOnDrop or caller/current-equality derivation is asserted.

## Fresh partial resource evidence60fdb811

Source-pair overlap and same-pair ghost components pass full stages/source/
refinement/seven bodies/21return+21leak each. Restoration uses arbitrary current
selected values, not old snapshot; pure holes preserve only nonselected values.
These empty runtime/false-unwind/i32-interface proofs do not verify callback
effects, actual arbitrary-n merge or caller. Native option<usize> replacement
draft uses explicit nonnegative bounds because ghost integer types are
mathematical; it remains Cloud untested. Dup-full-cell control and hidden-type
recovery refusal are observed calibration INCONCLUSIVE until fresh exact oracle.
Cleanup hidden positive full normal/unwind passes under experimental profile;
owner identity/swap/native-array handoff both tool profiles fail setup on missing
predicate-local source_head before all case bodies. Explicit existing-chunk
binding repair is drafted, no ownership/post change or theorem credit.
Current-owner list identity prerequisite and caller/C1/F-frame/Freeze-share/kernel
closure obligations above stay open.

## Fresh current-owner handoff evidence a3553e9e

Identity/swap/native-usize arbitrary-n identity now pass on stock26.10 AND the
six-patch experimental console with five checked bodies/six returns/six leak
checks per case/all source/refinement gates. Native array recursion handles
arbitrary mathematical n with explicit byte-span/domain bounds; it transfers
existing owners once and retains source bytes without owners. This establishes
the ghost resource operation conditional on destination already matching the
CURRENT source list. Neither the actual merge nor callback/copy-time history
derives that prerequisite here. No permission is made from address arithmetic
and no owner from slice.share. Native optional-index turnover still fails setup
on recursive-predicate punctuation; source-only two-semicolon repair needs
fresh both-tool evidence. Current F-frame/caller/C1count-n/cleanup routing/normal
permutation/generic-ZST/Freeze-share and experimental-kernel closure remain open.
