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

## Within-step observational repair before implementation — Build000add59

First exact-SHA Cloud Build000add59 at6d138cd9 charged359s; source/export/decode/refinement
succeed, V3b stock/six controls pass, but all9 new verifier invocations abort
**before proof execution** while `-dump_ast_with_locs` serializes the existing
`MergeFractionsStmt` (`Ocaml_expr_of_ast.of_stmt`, stock emitter has TODO).
No constructor/FBC/copy/recovery/MD-positive or intended-negative proof credit.
The unchanged statements and checks must remain in the verifier input.

The repair adds ONLY serialization `MergeFractionsStmt(l,e)` as a constructor
with original location/expression. It does not remove the merge statement,
change AST translation, memory/alias/kernel/spec semantics, disable AST checks
or skip proof stages. The emitter input/output are separately hash-pinned and
a snapshot retained. Existing emitter forms retain exact behavior. Conservation
of memory is unchanged: fraction merges still run through the existing kernel;
this output function records their syntax, never grants permissions. Critical
review: this is diagnostic instrumentation, not proof of a merge's validity;
full MD authority/read controls, V3b controls, source/refinement/leak/unwind and
onecell positive/negatives remain required on a NEW exact-SHA Cloud run. If the
serializer fails at another unsupported node, record INCONCLUSIVE and assess it;
no broad emitter rewrite or semantic shortcut is implied. Classifier-only replay
of the saved decoded MIR may repair its nonassignment handling, but cannot give
credit to proof bodies that never executed.

## Outcome

Session closed with all new cases INCONCLUSIVE at admission, no target proof or intended-negative credit. See [RESULT.md](RESULT.md). The readonly no-callback adapter cannot be reused across the actual later comparator; actual Drop requires first shift/dst update and separate generic borrow/cleanup proof. No further runnable repair was introduced after the closing time assessment.

## MD authority phase — first hypothesis, before fresh dispatch

Phase MERGE-MD-AUTHORITY-CLOUD-2026-10-09, start14:28:08UTC, main15:28:08,
absolute15:58:08; new3600seconds, owner60+max30finishing override; policy1fcd91ef.
Actual consumer and unresolved premises remain as above. This run resolves whether
existing immutable-local address discovery works when precreate_ref precedes the
fraction-merge cutoff. Own repair `[?f](*v.src |-> ?current)` preserves value,
fraction, logical owner and complete contract across all five generated cases.
No tool patch/profile/runtime change. MD units execute separately and before
one-cell; if MD gates fail, all five one-cell stages are explicitly NOT_RUN.

MD positive requires full result7/return/leak checks, not just admission.
Missing precreate deliberately retains merge before raw address and expects
frontend unsupported-address there (admission-only). Missing init expects a
missing tracked reference resource at &*tmp; missing read expects points_to at
*p after discarding its exact half. Neither resource negative can count an
unsupported-address or unrelated failure. Exact generated lines/hashes are in
case metadata; manual predicate/body/post audit required in addition to classifier.
precreate_ref requires true and supplies no storage, initialization, read
permission or owner: storage comes from ManuallyDrop::new, read fraction/debt
from consuming initialized storage via init_ref_readonly, logical generic held
owner from the supplied tail owner and ptr::read. Complementary storage is kept.

PASS selects already-authorized constructor→FBC next; resource FAIL identifies
its missing premise; frontend FAIL selects narrow source-linked routing analysis
before any semantic edit. No new group without a question. Actual first-shift/
dst-update and comparator recovery remain open even after diagnostic PASS.

## Next actual first-shift contract — design only, NOT_RUN

Before actual557, sift=tail.sub(1), guard.dst=tail, len1, src=tmp shared-derived.
Need initialized source sift points_to and writable destination gap points_to,
CURRENT sift own, sole held CURRENT owner, thread/type/F/frame, immutable tmp
complementary fractions and genuine reference debts, full mutable guard fields/
padding. Literal-one copy preserves source physical bytes and writes destination
current sift value; it does not transfer T.own. Transfer existing sift owner to
old gap, keep copied source bytes non-owning, then actual558 stores dst=sift
using its writable field permission. src/len/padding/held owner stay intact.
Derive adjacent pointer geometry from valid begin..tail bounds/provenance;
positive-size byte separation is not assumed by numeric address coincidence.
Check canonical FBC own after updating destination using new physical gap.

All these are caller debts. First comparator541 can change interior state and
must return CURRENT tail/sift owners/values, F, thread/frame and closed cmp_k/
borrow/ref fractions on true. False and panic before read need full caller posts,
not post-if ghost recovery. First shift is before later callback566, so a narrow
bounded transition may be tested without promoting readonly tmp across callback.
Actual Drop/glue on sift==begin remains separate. This contract review is static,
not proof execution or closure of an actual obligation.
