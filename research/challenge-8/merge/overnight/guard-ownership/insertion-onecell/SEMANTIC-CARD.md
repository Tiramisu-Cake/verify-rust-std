# `insert_tail` one-cell guard: bounded construction and recovery diagnostic

Prepared before implementation in `NEXT-MERGE-DROP-CALLER-CLOUD-2026-10-09`.
Read policy revision `1fcd91eff1507fe0bd0620a23b578edb454f1c3e`.
Actual source is `smallsort.rs` SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`,
blob `40939f922bcb6fdc7ee0d30427fa861827043827`.
The caller is `insert_tail`, lines 550–558: `tail.read()` creates a one-cell
logical gap, `tmp: ManuallyDrop<T>` holds the only tail owner, the exact
`let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };`
constructs the guard, and the loop later moves the gap. The actual
`CopyOnDrop::drop` copy is line 306. This experiment asks whether the *first*
quiescent gap can be packaged as a full physical guard FBC, opened with its
current one-cell owner, copied back and released using the existing model.
It does not establish the comparator, a moving gap, the actual Drop method call,
compiler glue or full `insert_tail`.

## Hypothesis and domain

The proposed conditional entry has a live writable initialized tail cell,
exactly one current `<T>.own(t,v)`, `thread_token(t)`, `type_interp<T>()`, and
valid provenance/alignment/limits. It also has the frame for other cells.
These are **supplied** in the fragment, not acquired from the first comparison:
the actual caller must prove that acquisition separately. The fragment has
generic unrestricted `T`, positive-size one-cell domain for this diagnostic,
no `Freeze`/`Copy`/purity bound, and no callback while `tmp` is held. ZST and
the later comparator's legal interior mutation remain separate obligations.
The guard points to the actual local `tmp`, and its destination is the actual
`tail`; source and destination separation and source bounds are asserted after
FBC opening, before the copy. The existing `points_to_limits` lemma is called
on the actual held source before these checks. Geometry facts are not inserted
as pure facts into guard
own. Any unproved stack provenance or separation blocks the result; it is not
assumed from a numeric address coincidence.

The narrow fragment's full normal post is the initialized writable tail cell
with the exact held value read before guard construction and exactly one owner,
thread/type/frame resources, and no
live guard/FBC/held-reference debt. The full target unwind post restores the
same form for all reachable panic edges. In the narrow no-callback fragment,
read/new/copy are intended non-unwinding only after their contracts establish
that fact. Any reachable unwind without the post is a failure, not a reason to
replace it with `false`. The diagnostic's conditional post cannot be promoted
to full `insert_tail` without first-comparison, late-comparison and actual Drop
glue proofs. Sortedness and permutation require further functional premises.
The exact held-value relation relies on this fragment having no comparator or
other legal state-mutating callback; full caller normal/unwind posts use current
values after arbitrary permitted callback effects.

## Resources and trust

`ptr::read` moves the sole logical owner into `tmp`; stale tail bytes give no
second owner. `precreate_ref(&tmp)` and `init_ref_readonly` establish the raw
`&*tmp` source share. Its complementary tmp storage fraction remains tracked.
Closing `<CopyOnDrop<T>>.own` consumes one source permission, the writable
gap, and one current T owner. Closing the generated canonical
`CopyOnDrop_full_borrow_content<T>(t,&gap_guard)()` additionally consumes the
three *actual* field chunks and padding. Open returns exactly those resources;
it cannot mint another T owner or physical field permission. The direct
recovery adapter uses literal count `1` to exercise the existing one-cell
physical copy contract; it is not the actual Drop method's dynamic `self.len`
copy or a proof of cell-to-array conversion. The copy changes destination
bytes only. Recovery must end the held
reference, merge complementary tmp storage, and place the same sole owner at
the destination. A source duplicate remains a non-owning representation.

The current merge stock/six profiles are known to omit tracked ManuallyDrop
raw-share translation. The opt-in profile may **only** rebase the previously
reviewed `verifast-manually-drop-ref.patch` to the pinned 26.10 translator:
exact `ManuallyDrop<T>` ADT, shared raw `&*tmp`, `Other` place, with real
precreate/init resources. Parser, kernel, prelude, copy model and refinement
checker stay fixed. This is a separate experimental trusted profile, not a
stock proof or acceptance of the patch. Require exact patch diff/pin review,
the positive and all missing-precreate/missing-init/read-permission tracked-MD
regressions, and existing merge/profile regression gates before interpreting
the candidate. If no exact tracked route exists, stop at INCONCLUSIVE; do not
substitute a bare address or assume an ownership bridge.

## Gates, controls and decision

Pin source/blob, exact line 550–551 bytes, exact private three-field struct and
actual Drop block; ghost stripping must reproduce both original and verified
runtime fragments. Inspect MIR and proof AST for actual `ManuallyDrop::new`,
`tail.read`, `&*tmp`, `mut` guard, `len=1`, physical FBC fields/padding/value
own, and the actual copy operation. Reject empty/False guard own, invented
owner, assumptions, leaks, omitted unwind, disabled checks, or a different
runtime copy. Positive needs full normal/eligible unwind/leak/dead/source/
refinement gates. A matched `assert false` *after* FBC/open/copy controls reach
the specified line. Missing-held-authority must fail at the first owner-demand
close; double physical FBC consumption must fail at the second close. Neither
negative earns credit for setup, frontend, helper, geometry or unrelated errors.
The matched false immediately after FBC and owner reopening checks that
mutable physical FBC packaging was reached independently of later source
geometry/copy/release. A separate matched false after full recovery tests the
longer transition.

The missing-owner control removes only entry `<T>.own`; its intended rejection
is the first ownership demand at `tail.read` if that read consumes `own`, or
at guard-own close if read is physical-only. A failure at any other line is
INCONCLUSIVE. The historical read-permission service control deliberately
uses `leak` to expose the translator's reference tracking; its result is a
tool regression only, never a target proof or permission to leak in this
fragment. Record stage, predicate and exact location for every outcome.

PASS permits testing whether the resource interface is acquired in actual
`insert_tail`; it gives no actual Drop/glue credit. Failure before FBC
identifies the next resource or semantic blocker; failure at copy/release
identifies the next proof operation. Repeated unexplained failure triggers
reassessment, not another broad patch. Self-review: the strongest risk is
conflating a share of tmp physical storage with full owner transfer. The
separate full physical FBC, current owner assertion, complementary storage
release and negative controls are intended to expose exactly that error.
