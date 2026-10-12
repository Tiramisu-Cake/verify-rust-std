# Select/sort4 session #2 — CLOSED / mandatory A1–A2 review

Stable owner `select-sort4`, own worktree `/root/verify-rust-std-select-night`, branch
`research/night-select-sort4-cloud-2026-10-09`. Mission: full actual sort4 with
applicability to real callers, then sort8 with verified merge. Session #1 ended
`8b6545094fea0ea25079bda51505d7f990ef2d1a`; this is session #2, not a reset by
phase/patch/Build naming. No third session on this interface is authorized.

Policy `6e1a8e59c56669abe5e6ec2013478e45ed2cc267`; docs adoption
`e92176fd7dd3fa369506281eb1ce76b2dd40d1b0`
(ACK on existing session1 card). Coordinator v3 installed adoption
`3bd466e367d6b458b2d5c8c29eb4cdd24d1e3d12`, schema3/max3; no transition/state reset.
Session start 2026-10-11T21:49:02Z, main deadline23:49:02Z, finish-only absolute
2026-10-12T00:19:02Z. New3600s account; prior2079s retired, no carry.

A1 **NOT ACHIEVED**; A2 **NOT ACHIEVED**. Compiler/source admission and checked
mode-local correspondence advanced. Actual caller/helper/native consumer proof
has not advanced through the first verifier interface check. PROGRESS-REVIEW
assessment remains unchanged. Experimental profile remains unaccepted.

Domain: Freeze-qualified diagnostic T and unrestricted FnMut(&T,&T)->bool F;
wrapper retains actual base guard/operands, selected method and original helper
prefix, with explicit diagnostic cuts before later paths. Both original impls
are retained in compiler query. Freeze caller selects specialized pair; Cell
caller selects blanket pair; unrestricted generic query returns None for both.
None does not authorize an Instance or a selected-method summary at original
unrestricted quicksort. No Freeze bound was added to original runtime signature.

Mismatch repair: positive and false31 normal call locals17/18/19; source-array
normal21/22/23; readonly root16/17/18; all selected method→helper5/6/7. Origins
v/scratch/is_less remain root1/2/5 and method1/2/3. Full clauses/binders/substs,
move-empty-projection shape, unique direct mutable reborrow and exact source/callee
checked before mode maps are compared semantically. Raw maps retained. Cloud
intermediate Ast.Var observations confirmed normal separately for every case.
Source-MD5-specific strict translator operands and exact three AST edges preserved.
Saved-data MIR/AST/classifier replay has zero proof credit; old verdicts preserved.

First causal blocker (Build132d, exact proof=infra3490c28761fc21ac9af82a4b7350545992a48df4):
`verified/lib.rs(13,8-18): error: Duplicate type parameter ''_'.`
Positive AST SHA024e1ffea9f64a0318adc8056f9e17cd694225a5332bb7b450aa71f93f071b61;
verification log SHA0e7f189e5225f363a657f9bacc9e755350c413122d0fdcc2aa1b68232ef2b02e.
Trait small_sort Func declares Self plus three identical '_ parameters, omits F,
and its reference types instead use separate '__35/36/37. Dump and verification
report the same first error before any selected user function is verified.
Full source/MIR/refinement support passed; full AST exists. Threshold prototype
and definition are separate records; parser correction audits both, never removes
prototype or verifier checks. Seven final-profile regression controls executed:
canonical T/MU, pointer positive and threshold body positive VF0 candidates;
wrong-pointer/raw-rights/initialized-T-cast negatives at intended obligations.
Their evidence is isolated from actual caller progress.

Bound transfer, len+16 overflow, reachable abort, helper pointer operations and
first sort4 resources remain NOT_PROVED/NOT_REACHED. Normal/unwind generated posts
are audited for presence/resources; they are not proved by this run. Native
C1–C4 normal plus four direct-unwind exits are NOT_RUN from actual caller.
Remaining supplied premises belong to the historical isolated C1–C4 diagnostic:
positive sizeof(T), four initialized source owners and optional-T destination
rights. None has been derived for actual helper. The opaque MaybeUninit frame
cannot become initialized T or array_<T> by cast/address equality. No root bound,
nonzero or research size guard supplied; unchanged public guard not repeated.

Review required before next authorization: existing compiler API cannot select
an impl for unrestricted T; more captures on that API will not fix None. A concrete
alternative is a checked common trait-item contract (threshold<=32, guarded len
bound, full native normal/unwind resources), proven against both actual impls.
Exact pinned translator translate_trait_required_fn explicitly rejects specs on
safe trait required functions and builds only Self/lifetime params, so this needs
separate interface/trust approval and conformance controls, not only annotations.
A first bounded experiment after review could audit/repair exact original trait
method F + three lifetime binder identities, preserving input regions, clauses,
source inventory and generated posts; negative controls must mutate binder reuse,
F omission, wrong region/source and duplicate body. Expected cost one 600–900s
Cloud budget reservation (recent complete Builds407–435s are baselines, not a
promise). Risk: binder/trait contract/impl conformance semantics and subsequently
stricter selected pre vs native safe trait prototype; no kernel/layout scope.
Excluded fix: delete trait/prototype, ignore duplicate binder, strengthen original
caller with Freeze/nonzero, or assume selected summary. A general contract route
must verify both bodies and generic call, not rely on selection observation.

A2 additionally requires a resource-compatible native consumer: existing C4 takes
positive sizeof(T) and array_<T> destination, while helper scratch is opaque MU
and len8–15 reaches sort4 even for ZST. Proposed separately reviewed alternative
is a C4 prefix contract preserving current opaque MU scratch on all normal/direct
unwind exits, with actual source owners/permissions; never import an unproved MU
adapter. Public IS_ZST→sizeof remains open. Full C5/copies/secondcall/sort8 remain
outside achieved results.

Closed at 2026-10-11T23:48:10.935492+00:00 after all four terminal Builds were accounted and
all archives/config/source identities/inventory/text chunks verified. New budget
1686/3600 conservative seconds used,1914 retired, remaining0. Prior2079 retired
unchanged. Own active/unresolved Builds,reservations,ready request: none.
Coordinator still schema3/max3. Runnable manifest disabled/session_closed=true.
No new experiment begun in finish-only window.

Final Build077360e8-b6d7-4d79-a101-dd4792ea328f (416s, collector SUCCESS): all
three selected cases export/decode/refinement/admission/post AST complete;
diagnostic and verification exit1 at the SAME duplicate trait parameter line13.
No selected user function verified. Both semantic negatives correctly inconclusive,
not intended negatives. Full normal/unwind resource posts present in every case;
exactly three selected edges. Exact prepatch-post equality remains RAW_REVIEW_REQUIRED,
not a proved preservation theorem. Seven final-profile regressions passed their gates.
Translator/kernel/modified sources/RSSpec and console same as Build132d.
Archive f9c37561d7760dffe9b4e512389fe317214d4fc4f39129c5f1309209a1bc5ace.

| Build | exact proof = infra SHA | conservative seconds |
|---|---|---:|
| 5bd2b7c3-ec17-45aa-a60e-7bdda819233c | 83b1d4451910902a8d6ef931a05e32b8d46e3624 | 435 |
| b8779246-8ef6-4a9e-922d-27e8747a8089 | ce1b9c19d9f865698aa9fcf1eb1f2e0cee5120b2 | 407 |
| 132d75f9-61ae-4bfa-9f63-ac7fbc0e56a1 | 3490c28761fc21ac9af82a4b7350545992a48df4 | 428 |
| 077360e8-b6d7-4d79-a101-dd4792ea328f | 8763e495475505b247e1a354ec805bd5ab4b4558 | 416 |

Final translator e484d9f95202c876957a5d5ab349c6a40bc04dbcf813db4b373819402d807e64;
console d980e027c1eb32c6c17dca99a172c34a4b7ea72ba205b70833bf985df4668c25;
verifier source f76012fb518703b1d98e243ac4f487f16877cfcb;
rustc f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f,nightly-2026-09-25.
Actual smallsort SHA85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1.
Full source/proof/infra/config/tool/ordered experimental profile identities,
stages/posts and old session are preserved in
[SESSION-RESULT-MANIFEST](SESSION-RESULT-MANIFEST.json) and
[closed account](BUDGET-BINDING-PREFIX-SESSION2-2026-10-12.json).

Next permitted action: maintainer/owner A1–A2 review of the concrete trait/binder
and modular-contract alternative; separate decision before any generic/trusted
rule implementation or third proof session. This checkpoint is not phase
approval, experimental profile acceptance, or authorization to continue builds.

## 2026-10-12 — owner-assigned approach review, Cloud budget 0

This append records a documentation/design window, not proof session #3. Initial
checkpoint `a22282dac3765c7d9948e6edfb0ae74102a4280b`; no newer changes reset.
T0 `00:18:36Z`, main deadline `01:18:36Z`, finish-only absolute `01:48:36Z`.
ACK policy `6e1a8e59c56669abe5e6ec2013478e45ed2cc267` already in adopted docs
`e92176fd7dd3fa369506281eb1ce76b2dd40d1b0`; confirmed without repeat transfer.
Read AGENTS/WORK-POLICY/ADOPTION/PROGRESS-REVIEW and latest checkpoint/manifest;
own branch/worktree clean initially, HEAD exactly supplied. Origin fetched;
GitHub Actions read-only list returned no runs. No workflow or Cloud dispatch.

Decision package:
[common trait interface](A1-TRAIT-CONTRACT-REVIEW-2026-10-12.md),
[exact pinned source/trust boundary](A1-TRANSLATOR-REVIEW-2026-10-12.md),
[source-derived fixture plan UNRUN](A1-FIXTURES-UNRUN-2026-10-12.md).
Recommended common threshold16..32, native bounded-base-case small_sort theorem
with full CURRENT normal/unwind resources against both actual impls. Original
generic guard derives n<=32, arithmetic n+16<=48; no selected Instance, supplied
bound, Freeze/nonzero or MU→T bridge. Literal old A1 selected-Instance criterion
needs owner's route decision; no administrative relabelling as ACHIEVED.

Concrete additional scope fact: pinned RequiredFn schema lacks method generics
and clauses; exporter uses printable lifetime names independently of input Ty
regions. Minimal candidate spans required-item exporter/schema/decoder plus
translator, not a lifetime rename. Existing prototype generation needs exact
generic Self/F/impl identity and full normal/unwind conformance gates; the
clause-ignoring specialization path cannot justify unrestricted trait dispatch.
Final translator e484d9...d807e64 independently hashed at own saved
`/tmp/selected-branch-align-check/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`;
f760 source read by Git object, no checkout/change to maintainer worktree.

First proposed experiment is threshold/interface-only: both actual threshold
body proofs, original generic threshold call/guard arithmetic and full retained
small_sort signature/source shape. Full small_sort summary remains UNPROVED and
unavailable; full caller/helper gate additionally needs actual insertion/helper
dependencies. All planned fixtures UNRUN. One proposed Build:900s timeout,
960s conservative reservation from a NEW separately granted account; none
reserved here. Maintainer reviews/integrates; select-sort4 owns patch development
after authorization. No kernel/layout/alias expansion proposed.

A2 candidate C1–C4 prefix preserves exact native MU scratch frame normal and all
four direct-unwind paths, without unused typed destination rights. Existing
nonzero source split/reborrow applicability still lacks ZST proof; len8–15
includes ZST. This does not prove impossible ZST support, only the current gap.
Full C5/copies/secondcall/sort8 still OPEN. A1/A2 NOT ACHIEVED, 15% unchanged;
all old Build verdicts and experimental profile status preserved. Previous
budgets remain CLOSED/retired, no new account/coordinator state changed.

VPS artifact assessment: this window created only the three tracked design docs
and these status/log/checkpoint edits, no new /tmp evidence/tool output. Existing
own scratch assessed; no active process using the removed directories observed.
Removed six unused reproducible translator-only scratch directories:
`/tmp/select-session2-translator-check`, `...-capture-stop`, `...-observe`,
`/tmp/selected-branch-check`, `...-work`, `/tmp/select-binding-prefix-suffix-check`.
Each held exactly one source ML file and no symlinks/results; combined 4,978,821
bytes. Necessary exact base/final translator copies, all raw/read Build evidence,
unique logs/archives and own Git history retained. Other owners/worktrees/caches,
coordinator and shared state untouched.

Next permitted step: review this concrete package; a separately named owner
scope/trust decision, implementation window and Cloud budget are needed before
R/C/G implementation or Build. This checkpoint authorizes none of them.

Design review completed `2026-10-12T00:42:16Z`, within main window. Compact
read-only explorer review integrated: actual AST/common-trait no-redirect gate
and forced clause-ignoring redirect negative; P0 arithmetic explicitly caller
lemma, not reached helper; zero-arg threshold native envelope distinguished from
small_sort resources. Source hashes and exact final translator locations checked.
Static relative Markdown targets/fenced blocks and `git diff --check` pass;
no executable proof tests needed for docs-only changes. Cloud spent0, no active
new run/draft tool implementation. Package ready for separate owner decision.

