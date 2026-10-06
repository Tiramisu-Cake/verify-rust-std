# `sort4_stable`: RAPx / VeriFast / Kani composition assessment

Night-phase update: [N2/37547890530](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37547890530),
source3f5c9e3126a6db0599f1b989f03146e143342d04, completes full acceptance/audit
at unchanged exact d4a12525 fieldless profile (matrix/refinement/integrity/negative/
native gates all pass). The earlier prototype INCONCLUSIVE below is historical.
This removes its processing/native-fixture acceptance blocker; it supplies no
typed reference/copy/raw-scratch/callback/whole-sort4 resource bridge. Independent
stock logical/callee/range components are authorized by SORT4-NIGHT-PHASE;
their actual results are separate from this layout acceptance.

[Pure index component](SORT4-INDEX-LEMMA.md) N4/37548475221/sourcefa74d92 now
checks the exact formulas for all5 independent Boolean answers with bounds and
exact permutation. Intended duplicate-index assertion fails; saved replay fixes
processing separately. This closes the logical selection theorem only. Exact
pointer-valued callee,provenance,resources and application to real copies remain open.

Current update: [stock run37540829027/source968c073](SORT4-ALIGNMENT-RESULTS.md#stock-generic-baseline-and-experimental-fieldless-layout--2026-10-07)
now establishes both generic geometry cases with VF0, integrity/refinement/dead-code
checks intact. Prior dead-code failures below are historical. The separately
approved fieldless-only experimental Rust layout prototype closes at6/6,653s:
[run37544574703/sourcee472aa2](SORT4-ALIGNMENT-RESULTS.md#fieldless-layout-prototype-closeout)
verifies original Z0/8/const-mutadd and generic calls Z/u64 in one experimental
unit/model. Metadata processing and new native fixtures leave full acceptance
INCONCLUSIVE. No stock-to-patched theorem transfer is assumed and no contradictory
stock Z instance is imported. Generic geometry does not establish typed ownership,
callback or copy safety. RAPx NO-GO and B/C NOT RUN unchanged;
no full generic sort4 composition follows.


2026-10-06, documentation-only owner request; entry synchronized to
`eda527922ec96468a804e3a62fbc1ca96f23691d`. This assessment uses the
[adopted contract](SORT4-CONTRACT.md), not a new contract or tool profile.
No implementation, build, executable check or workflow dispatch accompanies it.
Subsequent H_align scopes are recorded in [results](SORT4-ALIGNMENT-RESULTS.md).
Initial37529855468, syntax-only37532204465 and bounded37535499783 remain historical
with unaltered raw evidence. The separately authorized generic completion used
37537448952/source16aaf1b and37537868053/source519a370,2/2 NEW runs,85s summed jobs.
Checked order splits now discharge i==0 and the original residual post, but dead-
code rejection of impossible guard assertions keeps the whole generic gate
INCONCLUSIVE. Layout review complete, no tool patch. No automatic copy UB or full
sort4 proof gained. STATUS is current; STOP at run limit, no active experiment.

## Decision

A division of proof obligations is legitimate in principle. There is no rule
that one verifier must establish the entire contract. **The present results do
not yet compose into a generic sort4 theorem.** A defensible prospective route
keeps VeriFast responsible for current resources, legal callback effects and
all five panic posts, and admits RAPx facts only individually after their scope,
dependencies and source correspondence are established. Existing Kani theorems
remain concrete functional results, not universal assumptions of either tool.

**RAPx 0.7.50 / nightly-2026-02-05 gate A remains CLOSED / NO-GO for ZST
alignment. B/C remain NOT RUN.** Restricting RAPx's role does not reverse A or
resume those gates. Currently RAPx contributes detector diagnostics, not a
proved actual-sort4 component. Prospective use for selected non-ZST arithmetic,
bounds or non-overlap facts requires a separate decision and evidence; those
facts are not reliable automatically because the observed bug was in Align.
ZST remains in the overall target domain and needs independent coverage.

There is an independent alignment argument worth a narrow check: every actual
source/destination pointer is its aligned base plus an index 0..3 in units of T;
size(T) is a multiple of align(T), including size(T)=0. This can establish
alignment preservation without trusting RAPx's ZST rule. It cannot establish
reference validity, ownership, callback recovery or automatic operation checks.
The gate below tested that distinction; current results discharge generic path
posts but fail the whole-unit dead-code gate, and concrete ZST model compatibility
remains absent. Neither incomplete gate is imported as a premise.

## Obligation ledger

Tool assignments below are prospective responsibility, not established coverage.
“Independent” means no other tool's verdict is assumed; actual callee proofs and
the common-domain interpretation are still required. The evidence links identify
recorded profiles and runs, rather than treating green Actions jobs as proofs.

| Exact obligation under the adopted contract | Tool / proposed owner | Existing confirmation | Missing check | Dependency on another tool's result |
| --- | --- | --- | --- | --- |
| Same actual sort4 body, signatures, c1..c5, four copies and actual callees | Each tool plus source/refinement audits | Kani actual-body injection/audits in [37459631500](SORT4-RESULTS.md); std blob e555fce; hint blob fe59166. RAPx A analyzes synthetic calls to toolchain core, not repository sort4 | Exact RAPx target extraction/selection and dependency audit; VF sort4 MIR/export/refinement; actual helper/primitive correspondence | No verdict transfer. Same source identity is a prerequisite, not a theorem from another model |
| Full Separated4 byte ranges, source/reference-valid initialization, writable raw dst, bounds/liveness/provenance; no old dst owner silently lost | VF resource/caller proof; RAPx only candidate for isolated geometric predicates | [Caller audit](SORT4-CONTRACT.md#mapping-to-actual-callers); Kani separate initialized arrays; RAPx A valid ZST/u64 controls only | Machine-checked caller preconditions including scratch subranges, same-allocation disjoint ranges, ZST logical slots and raw dst; generic pointer permissions | Caller proof establishes premises first. RAPx ValidPtr does not imply VF Storage/SrcOwn/RawDst or Rust shared-reference validity |
| Nonnull/aligned pointers for all ten reference arguments and eight copy endpoints, including aligned ZST with equal addresses | Independent VF geometry and operation/resource proof; RAPx ZST Align excluded from proof evidence | Concrete Kani checks; RAPx [A/replay](RAPX-APPLICABILITY-RESULTS.md): two ZST SOUND_MISS; u64 intended Align failures with other Failed/Unknown. VF H_align helpers/bounds and four path posts now discharge, but dead-code gate leaves whole-unit INCONCLUSIVE | Complete whole-unit generic gate with dead-code checks; faithful concrete ZST size/alignment model; then source-exact pointer routing and automatic reference/copy enforcement, all layouts | Base alignment comes from adopted Storage and caller proof, never RAPx SOUND. Selection provenance must be established separately |
| Concrete original repr(align8) Z has size0/align8 and typed .add(i) retains base, i<=3 | Independently faithful Rust layout component; current VF model inadequate | [H_align trace/release review](SORT4-ALIGNMENT-MODEL-BOUNDARY.md):26.09 and26.10/master drop repr alignment, assert0<size(Z); layout/add fail. Bounded compiler-backed repair reviewed, not implemented | Reviewed minimum Rust-only layout facts/bounds correction; Kani concrete Z candidate has no full-domain interface, then exact concrete calibration/operation proof | No import of size0/align8 as trusted assumptions. Generic arithmetic, RAPx ZST SOUND and Kani concrete proofs cannot validate contradictory VF encoding |
| Checked generic step divisibility and const/mut offsets0..3 retain alignment under original byte/provenance resources | Unchanged VF checked ghost proofs | [Run37537868053](SORT4-ALIGNMENT-RESULTS.md): helpers/local bounds and all four path posts/leak checks finish; residual i==0 checked, VF1 due dead code; intended negatives2/2 | Reachable ghost proof structure and accepted whole-unit0 with dead-code checks intact; faithful concrete layout correspondence | Existing specs supply local premises; no RAPx/Kani verdict assumed. Branch/lemma proof is not the missing universal post |
| Generic tuple arguments and compiler's HRTB FnOnce::Output=bool for actual FnMut(&T,&T) calls | VF if used for callbacks | [No-patch matrix](SORT4-NO-PATCH-ASSESSMENT.md#compact-obstacle-matrix): actual insertion call failures; historical tuple/HRTB advancement, not sort4 proof | Checked tuple ownership and exported bound-region equality for actual sort4; no assumed equality/tuple bridge | RAPx Boolean results and Kani concrete closures cannot supply these VF resources or type derivations |
| Each normal callback may change F and legal interior/reachable state; safety has no order/purity/Copy/Freeze premise | VF effect-aware call/resource proof | VF FnMut contract returns current F; normal [two-cell recovery](verifast-borrow-recovery.md) is checked without callback. Kani sort4 comparator is pure/nonpanicking | Arbitrary-F effect/resource protocol, source validity after legal effects, repeated sharing, recoverable current frame and dst state | RAPx gate C NOT RUN; no assumed unchanged state or unproved callback summary imported |
| On each c1..c5 panic recover current SrcOwn, RawDst, F/frame and all local borrow resources, with one owner and no sort4 write | VF or equivalent independently adequate resource model | Actual control flow puts comparisons before copies; normal recovery controls pass; historical strict-cut unwind returned debt, not full post | Source-exact recovery on every direct Continue edge, including prior callbacks' effects and live sharing; actual helper callee proof | Independent of RAPx normal checkpoints and Kani pure closures. Absence of writes does not itself recover resources |
| Actual select_unpredictable pointer instantiation gives the condition-selected pointer, preserves its provenance/permission, and has no extra applicable panic | VF actual-callee proof or another independently justified same-source proof | [hint.rs](../../library/core/src/hint.rs:836) audited; Kani exercises actual helper in concrete domains | Prove actual pointer callee/intrinsics, then route each selected pointer's resources; no assumed if replacement | RAPx builtin's numeric disjunction is insufficient for exact selection or selected provenance; Kani theorem is concrete |
| Four selected indices form one permutation for arbitrary five Boolean answers; copies use current V5 | VF checked generic index/resource lemma; Kani may provide separate finite diagnostic | Static 32-answer index argument in contract; Kani concrete ordered comparisons | Checked source-linked index theorem, exact selection correspondence and resource routing | No reliance on sortedness to prove safety/permutation; RAPx's independent selection disjunctions lose joint permutation constraints |
| Each copy is non-overlapping and within readable source/writable dst; earlier writes preserve later sources | VF independent resource/byte proof; RAPx candidate for selected geometry only | Kani [37466906281](SORT4-CONTRACT-RESULTS.md) distinguishes coincident UB from shifted multiset loss; full separation statically sufficient | Generic four-copy proof, all pointer paths, permission/provenance and consistent byte interpretation. RAPx B NOT RUN | Separated4 is caller-established. RAPx NonOverlap alone neither establishes across-copy preservation nor satisfies VF typed copy preconditions |
| Raw possibly-uninitialized dst becomes four valid copied representations; uninitialized padding is allowed; invalid scalar/reachable values are not produced | VF initialization/representation proof; RAPx only after separate B-like applicability decision | VF baseline typed copy requires initialized dst; historical Drop used initialized dst. Kani stronger validity profile has unsupported CopyNonOverlapping | Actual raw-copy/callee proof with optional initialization, padding and generic value validity, including inhabited/destructor-bearing ZST | Kani i32/tagged results cannot supply generic validity. RAPx B NOT RUN and Init/ValidPtr are not accepted representation transport |
| Immutable bytes are never illegally mutated; UnsafeCell effects remain legal | VF permission/alias proof; RAPx candidate only with measured property coverage | [Kani detector gap](ub-checks.md): immutable write/read9 passed; no target-wide check | Independently justified write permissions for raw copies and all callback-accessible state; paired intended detector controls if RAPx used | No inference from Kani default pass or RAPx SOUND; this category remains open separately |
| Normal SrcOwn(s,V5) + Shadow(dst,pi(V5)), both storages, current F/frame, exactly one ownership sequence, no local debt | VF relational ownership proof | [Adopted protocol](SORT4-CONTRACT.md#full-normal-post-and-ownership-protocol); historical checked recovery/Drop are conditional, different domains | Generic four-slot shadow representation, logical ZST occurrences, no duplicate drop rights; full five-call + four-copy composition | Byte equality or RAPx copying does not imply T.own, Shadow or a permission transfer. No imported ownership bridge |
| Conditional sorted exact original-occurrence permutation and stability under fixed strict weak order and key/value preservation | Existing concrete Kani; VF checked abstract order proof or an independently justified parametric theorem for generic extension | Kani values 0/267 failed,12 covers; tagged 0/233 failed,6 covers, [37459631500](SORT4-RESULTS.md) | Generic order theorem for exact network and tie rules; proof of abstraction if reusing Kani via ranks; strict weak order/effect premises separate from safety | No universal lift from i32 keys or fixed IDs without a proved simulation. Memory safety remains independently required before interpreting outputs |
| Reuse sort4 in sort8/general scratch callers and later merge/drop/move paths | VF/equivalent caller composition, later scope | Static len>=8/16 audit; scratch nondropped by MaybeUninit | Actual caller establishes entire precondition, then relational scratch access/ownership and all later unwind transport | Requires a proved actual sort4 summary first; does not feed an assumed scratch summary back into sort4 |

## Common source and domain, without a model shortcut

Target sort4 is smallsort.rs:612–658, blob
`e555fce440872898e47fd5114f32eb15401d07df`; actual selection helper is hint.rs,
blob `fe59166363b9cc049c0d48f4349f4dc9c0e458b8`. The source files were rechecked
at entry. Kani pin is `152c6a8c875d9886a67e229247b4826d6105ccfd` on
nightly-2026-02-05. Official VF26.09 is
`809de4596839b739dd999f9e462242c835e3af46` with the same nightly; released
26.10 source comparison is context only, with its different nightly-2026-09-25
and no target export/refinement run. RAPx 0.7.50 is audited package/VCS
`7d61d9377033c48a4df8954f34cc076e97a93816` on nightly-2026-02-05.
Shared compiler date does not make MIR, intrinsic or memory models identical.

For every component, bind target, architecture/layout, selected body/callees,
flags, normal/unwind paths and actual property locations. In particular,
RAPx's A fixtures use toolchain core: unchanged repository ptr annotations alone
do not make their proof a repository primitive or sort4 proof. A future callee
summary needs the actual matching callee verified before reuse. VF ghost-only
annotations need source/refinement correspondence; semantic AST/MIR rewrites are
not authorized by calling them proof-only. No common proof certificate or checked
RAPx-to-VF import has been demonstrated.

Composition need not import certificates or prove everything twice. Independently
checked theorems can be conjoined if each denotes the same real executions on D
and its premises are independently established. For that argument, document each
model's interpretation of addresses/provenance, valid typed values, byte padding,
effects and unwind states, and the particular facts it preserves. A common
numeric inequality may need only arithmetic/source correspondence; returning
VF T.own needs much more. An assumed reflection map or trusted bodyless imported
summary is a new trust requirement, not a consequence of using approved tools.
The current evidence lacks that source/domain correspondence for a RAPx component
and the required VF generic theorem, so the conjunction is not yet available.

Let D be the adopted safety domain: arbitrary valid sized T and legal F,
initialized reference-valid four-slot source, raw writable four-slot scratch,
Separated4, legal provenance/permissions and effect-aware current resources.
It includes non-Copy, non-Freeze, padding, all valid layouts and all five panics.
For ZST, byte separation is vacuous even at equal addresses, but base alignment,
reference validity and four logical ownership occurrences remain. A same-address
logical occurrence is not a new spatial ownership chunk for free. Legal callback
leaks/replacement do not require resurrection of consumed resources.

Kani's D_K is a strict subdomain: two concrete Copy layouts, fixed separate
initialized arrays and pure nonpanicking key comparison. Its functional theorem
can be retained on D_K, but cannot fill D minus D_K. Ordering applies on D_F,
the subdomain of D with fixed strict weak order and relevant key/value preservation;
it never constrains the safety theorem. A prospective RAPx role on size(T)>0 is
a component subdomain, not exclusion of ZST from D: an independent component
must prove the corresponding obligation for size(T)=0, and the exhaustive domain
split and shared premises must be justified. No present RAPx generic theorem
establishes even that non-ZST component.

The new H_align audit strengthens the source/model compatibility requirement:
same Rust bytes and successful refinement do not imply a faithful layout model.
The original empty repr(align8) Z exports with empty fields/isReprC=false and no
alignment metadata, while VF's concrete struct model imposes positive size.
Thus the concrete ZST obligations cannot currently be transported to that model.
Four path posts and the checked stride lemma do not validate this
instantiation, and assuming actual size0 against the positive-size axiom would
make proof reasoning inconsistent. No circular resource/layout premise is added.
The model boundary is a specific reason this present no-patch joint route remains
inapplicable as a full contract proof, even with RAPx restricted to diagnostics.
ZST remains in D; RAPx A remains NO-GO, B/C NOT RUN, Kani D_K unchanged.

## Restricting RAPx and excluding circular assumptions

The diagnosed Align shortcut occurs in pinned
[memory.rs:25–46](https://github.com/safer-rust/RAPx/blob/7d61d9377033c48a4df8954f34cc076e97a93816/rapx/src/verify/property_checker/memory.rs).
Further source review for this assessment observes that zst_guard also appears
in Allocated and Init checks; their applicability has not been tested by B.
This is dependency-audit motivation, not a claim that those checks have the same
demonstrated bug. Whole-case SOUND and the 43 proved records cannot be used as
an independent general memory-safety theorem.

Pinned [call.rs:239–296](https://github.com/safer-rust/RAPx/blob/7d61d9377033c48a4df8954f34cc076e97a93816/rapx/src/verify/vm/call.rs)
models select_unpredictable with a fresh result equal to either argument, without
linking the choice to condition, and attaches the first available argument
provenance. The disjunction can overapproximate numeric choices, useful for a
range bound if independently justified; it loses the correlated choices needed
for permutation/order. Its provenance attachment cannot be presumed valid when
the numeric result selects the other pointer. That is a static applicability
concern, not a newly executed detector counterexample. Likewise `_cleanup` in
exec_call alone is not an executed proof of missing unwind coverage; C is NOT RUN.

RAPx may therefore remain a diagnostic cross-check now. To use a future narrow
fact, inventory its generated checkpoints and premises, path/effect coverage,
fast rules and shared VM facts; retain Unknown/unsupported/missing evidence.
Independently establish any aligned-base or effect invariant on which it depends.
If that fact ultimately depends on the unproved Align rule, discarded callback
effects or unsound provenance transport, quarantine it with the affected chain.
A control for one property is evidence for that property/domain, not general
tool soundness. Prefer independent overlapping proofs to a trusted import.

The allowed dependency order is: caller-established D and source mapping;
independent layout/primitive and callback/resource proofs; checked selected-index
and copy composition; normal/five-unwind safety; conditional functionality; later
caller use. Kani's existing concrete facts sit alongside this chain. None supplies
unproved generic premises. No component may assume its own target conclusion.
Specifically: do not assume generic sort4 safety to justify RAPx pointers and then
use RAPx to prove that safety; do not assume Shadow as the result of copying;
do not use unproved caller scratch transport to justify sort4's ownership post;
do not infer provenance from equal addresses or sorting from five fresh Booleans.

## VeriFast capabilities: necessary versus optional changes

These are requirements of the proposed VF role, not authorization or a proven
minimal patch set. [Historical evidence](SORT4-NO-PATCH-ASSESSMENT.md) establishes
some blockers on analogous actual insertion calls; complete sort4 was NOT RUN.

| Capability | Necessary for this VF role | What changes are or are not justified |
| --- | --- | --- |
| Owned (&T,&T) argument and exported HRTB Output=bool | Yes, if VF verifies actual arbitrary FnMut calls | Reviewed official26.09/26.10 lack the demonstrated route. Checked tuple representation and correctly scoped projection handling, or another demonstrated source-exact mechanism, are needed; the historical tuple/HRTB patches are candidates, not automatically admissible or sufficient |
| Full current normal and direct-panic resource recovery | Yes, at all five exits | Ordinary normal recovery is demonstrated. Direct Continue skips trailing helper; new explicit checked recovery routing or another demonstrated mechanism is needed for this architecture. Strict-cut's borrowed-debt post is insufficient. A kernel change is not established as intrinsically necessary; an unreviewed frontend continuation is still a trust change |
| Arbitrary legal callback effects and one-owner/Shadow accounting | Yes | Requires checked proof protocols/lemmas and source applicability; RAPx cannot remove it. Evidence does not show that extending the alias kernel is unavoidable, nor that existing callback specification alone provides all needed current resources |
| Raw-copy initialization, padding and full representation post | Yes if VF proves copy/resources; a separately validated other-tool component could change the implementation allocation | Existing typed copy spec requires initialized dst. Need actual raw-callee/byte proof or separately reviewed adequate specification; no optional-to-initialized coercion. A VF prelude change is conditional, not justified merely by RAPx NonOverlap/ValidPtr. VF's old typed call remains blocked without a checked interface |
| Actual pointer selection helper and five-call composition | Yes as proof dependencies | A checked helper/intrinsic proof and resource/index lemmas may suffice; adding a trusted builtin or runtime if rewrite is not automatically necessary or authorized |
| Independent layout/alignment proof | Yes to cover the RAPx gap | H_align now discharges helper/bounds and all four generic path posts; whole-unit dead-code gate still fails. Concrete original Z requires faithful size/repr alignment encoding: current positive-size axiom contradicts Rust ZST and exporter loses repr alignment. If VF owns this calibration, reviewed layout-model correction is necessary; another independent component is possible. No implementation authorized. Automatic reference/copy enforcement still unproved; no evidence requires a generic alignment-kernel extension or historical insertion patch chain |
| Minimum closed Rust struct layout repair | Recommended future route, not implemented | Compiler-backed size/ABIalign for closed nongeneric Sized repr(Rust)/repr(C) structs with optionalalign, shared source/typeid/target linkage, Rust-only >=0 bound, field-rule compatibility. [Review/regression plan](SORT4-ALIGNMENT-MODEL-BOUNDARY.md) names exporter/schema/bindings/AST/translator/engine and trust edge. >=0 alone supplies no exact0/8. Generic ADT exact layout and other forms remain separate scope; current abstract generic function proof needs no semantic patch for index arithmetic |
| Independent Kani layout component | Concrete diagnostic candidate; no evidenced full-domain replacement | Kani0.67.0/nightly2026-02-05 could calibrate exact original Z/.add at same source/target. No existing Z run, arbitrary-T quantification, exhaustive domain split or checked ownership/provenance interface. Keep concrete Z entirely out of incompatible VF units; cannot import0/8 into positive-size context |
| Old address-taken/ManuallyDrop/local Drop/declaration-order/projection-name patch chain | No demonstrated need in sort4's own body | Do not import insertion patches. The actual selection helper contains MaybeUninit/DropOnPanic; if its pointer instantiation needs frontend support, establish that separately rather than assuming all helper cleanup patches necessary |

There is no currently established complete no-patch composition, and no basis to
declare all VF changes unnecessary. Conversely, requiring the entire historical
insertion chain before investigating this division would be unjustified. Tool
semantic changes require their own rationale, trust review and regression gate
before implementation; this assessment implements none.

## One next bounded check — proposed, NOT RUN

**Historical proposal at the documentation-only assessment checkpoint.** Its
hypothesis/scope below are retained. The subsequent three separately authorized
scopes/runs are recorded in [results](SORT4-ALIGNMENT-RESULTS.md); latest continuation
is CLOSED at the concrete ZST model boundary. This proposal grants no new dispatch.

**Hypothesis H_align:** unchanged official VF26.09 can check a source-linked,
generic alignment-preservation lemma for `base.add(i)` at every i in 0..3,
including size(T)=0 and align(T)>1, using aligned Storage bases and the existing
size_align lemma, without Copy/Freeze or a new trusted assumption. This is new
because it isolates the gap after assigning ZST alignment independently of RAPx;
it does not repeat c1 or retry RAPx A. The source basis is pinned
[prelude_core.rsspec size_align](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/bin/rust/prelude_core.rsspec#L51-L53)
and the actual .add offsets, not a green ZST verdict.

Proposed future scope: one hosted manual diagnostic, at most90min including
setup, official26.09/nightly-2026-02-05, no patches, no RAPx/Kani rerun and no
B/C. No run is authorized by this proposal. Preparation would freeze the exact
artifact/hash/profile and experiment card before code or dispatch. Use arbitrary
valid sized T, legal aligned bases/provenance with four positions, i in0..3 and
normal pointer arithmetic. Positive alignment, legal offsets and absence of
address/offset overflow must follow the pinned layout model and Storage/caller
premises, not fresh assumptions hiding .add UB. Check the actual .add expression's representation;
prove size/align arithmetic rather than postulating an unconstrained numeric
pointer equals a permission-bearing Rust pointer.

The full eventual target remains the contract's SrcOwn + Shadow normal post and
all five current-state SrcOwn + RawDst panic posts. This diagnostic is deliberately
only geometry: normal aligned result with original storage/resource frame;
no callback, source/dst writes, ownership creation or permitted unwind. Generic
coverage cannot be replaced by several concrete positive layouts.

Include an aligned size0/align8 control and two false alignment-conclusion controls
for byte-offset1 source/destination from aligned bases. Those negatives omit the
claimed result's alignment premise and must fail at the lemma's alignment
conclusion, not setup, parsing or an unrelated resource assertion. No impossible
typed cell at a misaligned address may be assumed. They test the proposed lemma,
**not an automatic UB detector**. No independent manual assertion is presented
as a repair of RAPx's detector. Verify full output/refinement and isolate controls.

Also audit the boundary to automatic target operation checks within this same
gate's report. VF's pinned typed copy contract
[std/lib.rsspec:545–549](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/bin/rust/std/lib.rsspec#L545-L549)
does not explicitly state alignment. Determine whether its resource predicates
and frontend actually enforce the needed fact, including ZST; do not assume
points_to implies every Rust pointer condition. The geometry theorem must later
be connected to each real reference/copy operation without suppressing checks.
If an aligned/misaligned raw-operation pair is expressible with the other
resources intact under this unchanged profile, inspect rejection at the actual
alignment/permission obligation. Earlier failure to construct those resources
is not intended alignment detection. If no such obligation is enforceable,
report the model boundary rather than manufacturing it with a manual assertion.
This audit is not a new primitive proof or a repair of the raw-dst gap.

Decision map: a checked generic lemma plus intended false-post rejections supports
independent alignment preservation, conditional on proved selected-pointer
routing/callers. It permits only a later composition decision. Missing automatic
enforcement remains an explicit additional obligation even if arithmetic passes.
Export/resource/layout failure is INCONCLUSIVE for H_align; an unexpectedly
proved false conclusion is NO-GO for that VF profile/model route. A required
semantic extension triggers STOP for separate review, never an automatic patch.
No result of this small gate closes generic sort4 safety or reopens RAPx B/C.

## Checkpoint

Conditional acyclic composition remains incomplete. The generic completion runs
now discharge every residual index/alignment/resource post, but final37537868053
fails the unchanged dead-code gate on three impossible guard-body assertions.
Whole-unit generic status INCONCLUSIVE; no accepted theorem is transported.
Previous raw outcomes/logs/JSONs and the existing Kani concrete domain remain intact.

Concrete original Z still fails faithful calibration. Source review at official
26.09 and26.10/current master confirms positive Rust struct size and lost repr
alignment. Recommend minimum compiler-backed Rust size/ABIalign facts through the
export/schema/AST/translation/engine path, with a Rust-only >=0 bound, same typeid /
target/source linkage, ordinary-struct compatibility and future positive/negative
regressions. Generic functions remain symbolic; generic ADT exact layout is a
separate scope. No tool patch or patch test is implemented here.

Kani0.67.0 is a concrete Z calibration candidate, not an already evidenced layout
component for every valid Rust T. Without exhaustive domain mapping and an independent
permission/resource interface that avoids VF's contradictory concrete Z encoding,
that route cannot replace the full component. The layout review/regression design
adds no theorem and does not license numeric facts as ownership assumptions.
Selected pointers, callback effects, all five panic posts, raw-copy validity and
resources, automatic UB and full sort4 remain open. Historical insertion/FnMut/Drop
patches have no new justification from this scoped layout work.

Latest phase CLOSED at2/2 NEW runs,85s total jobs/setup, no active experiment.
Generic proof needs a separately verified ghost-structure repair that retains all
checks. Future layout implementation requires the documented trust review and
acceptance gates, not an automatic continuation. RAPx CLOSED / NO-GO; B/C NOT RUN;
ZST retained; no external issue/PR/message or third run.
