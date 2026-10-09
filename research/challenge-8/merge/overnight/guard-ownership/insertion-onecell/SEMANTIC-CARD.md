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

## Read-authority negative repair — before implementation/dispatch

Build2eadf304 /121f9471,359s: MD immutable i32 positive all stages0, named
read/return/leak and result7 PASS; missing-init exact aliasing.rsspec88
ref_initialized<i32>(held_ref) refusal; missing-precreate exact frontend source12
unsupported address ADMISSION_ONLY. Fixed-half read control stops at leak15,
not read16, hence INCONCLUSIVE. Five one-cell cases correctly NOT_RUN.
Existing source/new/init storage permission can be fractional for immutable
addressed tmp: init creates coef*f, not a guaranteed1/2. The failed hardcoded
leak also uses runtime p from call-outcome; do not infer a read-authority theorem.

Next narrow fixture-only hypothesis: assert/bind actual available read fraction
at held_ref and actual complementary storage fraction at &tmp; leak exactly those
existing chunks, keep ref_initialized/precreation/end bookkeeping, then execute
unchanged &*tmp-derived p read. No assumed f=1, pointer equality, resource creation
or changed runtime. No tool/profile/trusted semantic change. Removal statements
must both execute and sole failure must be missing points_to at actual *p;
preparatory assert/leak, reference, cleanup or helper failure stays INCONCLUSIVE.
All positive source and result/return/leak checks remain unchanged. PASS all MD
gates permits corrected one-cell constructor/FBC in main window; FAIL identifies
only that first resource/removal mechanism. No more control groups are added.

## Exact-fraction outcome and genuine resource exclusion — before last repair

Build12d6a399 /4a401ab2 terminalSUCCESS diagnostic,365s. Positive/init/admission
repeat intended gates; exact fractions exist and both removal statements execute.
Runtime read20 also executes successfully; refusal is later end_ref_readonly at
aliasing50 for concrete1/4 points_to, hence read-negative INCONCLUSIVE and all
one-cell NOT_RUN. The hypothesis that leak discards read authority was wrong:
frozen kernel Leak consumes the real chunk and produces it at dummy fraction.
Thus dummy read authority legitimately remains; no model unsoundness claim.

Last local fixture-only correction: close each actual fractional chunk into
existing mk_points_to/scaledp, then existing lifetime_logic borrow(k,P) consumes
P and retains full_borrow plus borrow_end_token. No Leak, no created permission,
new abstract lemma/summary or trusted semantic change. ref_initialized remains
available, and both physical fractions are kept conserved inside closed borrows,
not available to raw read until explicitly opened. Use actual pointers held_ref
and &tmp and bound fractions; runtime statements and full positive/posts unchanged.
Intended sole refusal remains missing points_to at *p, after both borrow calls.
Setup/closure/borrow/recovery failures do not count. This is the same failed
read-authority question, not another group or broader model experiment.


## Final observed boundary — MD authority / mutable FBC

Build d1bfa119 /633c0c09 proves the four isolated MD gates on the frozen
profile. Concrete i32 positive verifies entire body/result7/return/leak. Missing
init fails ref_initialized at spec88; missing read authority fails points_to
at actual read24 after both genuine storage/read fractions enter existing closed
borrows. Missing precreation fails frontend source12; admission-only. Registration
with req true does not provide initialized bytes or authority. All profile pins
match; no trusted semantic change in this session.

Corrected supported own syntax admits all five one-cell bodies. Mutable guard
physical src/dst/len/padding plus one logical owner support own40 and canonical
FBC close41/open42. after_fbc_false refuses false44 after these transitions.
Missing owner refuses own at definition14 during close40; second physical FBC
close refuses src field at definition5 during second close42. These are narrow
reached negative obligations, not unrestricted T ownership uniqueness. Positive
and after_recovery_false stop alignment46 before physical copy50. Full target
normal/unwind posts and compiler cleanup are still unchecked past this point.

Raw audit AST read gate misses specialized tail->temporary, Deref->value,
value->immutable tmp assignment chain at line34; source/MIR identities are exact.
A separate saved-data classifier replay can correct this observational mismatch
and exact predicate-definition error routing, but cannot improve the failed
positive, reach recovery or turn collector SUCCESS into accepted profile.

First remaining diagnostic obligation is deriving src alignment from real
immutable tmp/shared-derived pointer resources using existing trusted mechanisms.
points_to_limits44 and nonnull45 execute; their facts do not establish alignment.
Next fresh proof must preserve full contracts and examine all subsequently reached
bounds/separation/copy/borrow recovery/return/leak obligations. It must not assume
alignment or mint read/ownership authority. Actual first-shift/dst-update remains
subsequent source-linked work and all comparator limitations above still apply.


Audit-only final one-cell replay: [receipt](../../../../cloud-build/md-authority/REPLAY-FINAL-ONECELL.json) recomputes the exact
immutable typed load-chain AST gate and routes the sole resource error through
its declared own/FBC field line after the intended executed close. Source/MIR
admission is reused only from SHA-bound saved classifications. No proof or tool
semantics are executed/changed. `after_fbc_false`, `missing_held_owner` and
`double_physical_fbc` become **EXPECTED_REJECTION** on the final fresh Build's
already-recorded intended obligations. Positive and `after_recovery_false`
remain **INCONCLUSIVE** at alignment46; fragment_pass remains false. Five saved/
synthetic mutation controls reject mutable tmp, disconnected load, wrong source,
and absent executed own/FBC close. Raw Cloud verdicts and older failures are
retained; replay does not establish a positive or reach recovery.

## Source alignment/recovery phase — first hypothesis before fresh dispatch

MERGE-SRC-ALIGN-RECOVERY-CLOUD-2026-10-09; start15:58:54UTC, main16:58:54, absolute17:28:54; policy1fcd91ef; new3600s no carryover. Existing MD admission/reference interface, own and full posts unchanged. Runtime immutable tmp and shared-derived src unchanged.

Exact saved Buildd1bfa119 prelude_core.patched.rsspec SHA d1079bc94ceafe6595c7ce216f9c93e3436d22d849bd31bcb0cf442dd183e751 matches PROFILE. points_to_limits247–249 yields object limits only. Existing to_u8s_349–351 consumes fractional points_to_(p,v), produces same fractional byte storage, alignment at p, and v==of_u8s_(bytes). Existing from_u8s_345–347 consumes those bytes using the proved alignment and returns the exact same option value/fraction. New fully-bodied initialized_storage_alignment lemma opens points_to to some(v), performs this round trip, closes the same fractional initialized points_to. It adds no assumption/axiom/resource and retains the original value; existing T.own is framed throughout. A fresh Cloud run must check the lemma body and caller, not trust its declaration.

Storage originates in actual tail load then transparent ManuallyDrop::new/local initialization; precreation is bookkeeping only. init_ref_readonly consumes a genuine storage fraction and produces held_ref initialized storage plus complementary actual tmp storage and end debt. Saved AST has create_ref(AddressOf(tmp)) returning the precreated held_ref, then reborrow_ref identity yielding &*tmp; guard fields preserve this actual pointer through FBC. Fresh source_identity assertion tests guard.src==held_ref after open; alignment lemma consumes the real guard.src fractional points_to, so no cross-pointer alignment transfer is assumed. Pure alignment persists through later resource packaging; no geometry is supplied at entry or added to guard own.

Expected first run: lemma checked, source identity/alignment pass; then first uncovered bounds/separation/copy/recovery/cleanup/post obligation becomes visible. Exact pinned one-cell copy spec std_lib626–630 requires numeric interval disjointness separately. Current frozen prelude exposes no located generic storage→numeric-disjointness lemma; typed resources/provenance are not being treated as a proof of it. Keep separation assertion and copy contract intact. If a later geometry failure occurs, use existing allocation/local facts if available; otherwise prepare source-linked reproducer and maintainer rule, never insert an axiom.

Only fresh positive and after_recovery_false selected; MD authority inputs/profile and prior controls unchanged, their new statuses NOT_RUN with prior evidence basis kept distinct. No automatic V3b/MD repeat for a geometry-only post-FBC lemma. Recovery control counts only at its false after actual copy, reference end, complementary merge and full recovery assertion; earlier failure remains INCONCLUSIVE. Full normal/applicable unwind/return/leak checks retained. Early full PASS permits actual557/558 in main hour only; current next transition NOT_RUN.

## First fresh outcome and second hypothesis — before next dispatch

Build595a5fa7 /6fbc0f7d terminalSUCCESS,314s; archive1b199861e88383fb21f610ee59eb223df4126fa354009084aa4cc44d1dd1ec90 and external text integrity verified. The fully-bodied initialized_storage_alignment lemma reaches post/leak; it is a checked generic storage conversion component in the frozen experimental profile. Both positive and after_recovery_false remain INCONCLUSIVE at added source identity assertion56, before alignment caller57, bounds/copy/recovery; no full fragment credit.

Canonical mutable FBC(t,&guard) hides src/dst/current as existential field/own witnesses. Reopening yields valid storage/owner for current physical src, but not the old separately named held_ref equality. That is information loss, not proof that the runtime &*tmp pointer differs. Exact AST still contains create_ref→reborrow identities before packaging. Second hypothesis moves the SAME src==held_ref assertion to immediately after actual constructor, before own/FBC close; it is retained, executed and checked at the source boundary where it states the runtime chain. Alignment lemma remains AFTER own/FBC open and consumes current guard.src genuine initialized storage directly. It needs no external pointer equality and returns that exact same storage/value/fraction. Full target normal/unwind/recovery assertions remain unchanged.

Expected second run: constructor identity succeeds, post-FBC alignment call/assertion succeeds, then next genuine limits/separation/copy obligation is exposed. No new reference/ownership interface, trusted rule or runtime pointer; same targeted positive+recovery false, unchanged MD and other controls explicitly NOT_RUN. If current src resource cannot support the lemma, record first failure. If cross-allocation numeric spans block, prepare minimal source-linked rule requirement without assuming it. If geometry unexpectedly passes, next recovery may require packaging the existing end token/ref_initialized alongside source storage inside guard own and ending via current src; this candidate is DESIGN_ONLY, would require affected authority controls and must still preserve actual tmp/held post anchors.
