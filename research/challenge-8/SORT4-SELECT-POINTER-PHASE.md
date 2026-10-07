# Source-linked pointer select completion phase

Owner authorization2026-10-07; entry
`cd44e1bbf115c83c84fd7d4c050b1f74be0e1d09` on challenge-8/research.
Current S6: **COMPONENT_ACCEPTED (v4); actual integration STOPPED at forget guard-own.**
[Fresh run37656621026](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37656621026), proof source
`75681fbc57bda633f59096cdc28f0c1aa61daef8`, profile
`experimental-source-linked-select-pointer-drop-v4`, patch
`c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1`.
Constructor/as_mut_ptr/typed intrinsics/narrow pointer drop matrices and14baselines
PASS freshly; S6 has2positive+11proofnegative+22source/MIR/pin negatives, all on
intended obligations. All19 independent NORMAL controls reject exactly beforeproof,
including oldreceiver26→23. Full source/typed method+actual MIR/runtime/normal-unwind
CFG correspondence preserved; diagnostic37649244205 is not a proof. Five extra
stock ghost locals/blocks and every annotation coordinate are in the design table.

Actual baseline still lacks initialized payloadcell. Stock-projected actual enters
proof after full36/19 admission and checkedmethod redirect. Both stock opens, proof
condition split, retained runtime drop at verified/lib.rs60 and both closes61/62
pass in the recorded prefix. Next blocker: verified/lib.rs63 `mem::forget(guard)`,
frozen std/lib.rsspec420:41–42 requires nominal
`<DropOnPanic<*const Element>>.own(t, guard)`, absent. No guard/forget extension;
STOP at this exact obligation. Current classifier stays INCONCLUSIVE with heuristic
kind intrinsic_select; rawlog establishes the forget guard-own failure separately.
Finalreturn/leak/fullnormal-unwind posts not reached; wholehelper/sort4 NOT PROVEN.

Checked method and ghost resource identity lemma are separate from TRUSTED compiler
raw-pointer drop glue correspondence and frozen stock frontend ghost substitution.
Existing initializedcell/fullpointervalue/thread/independentframes required, no
Element rights. Recursive free stub is not a runtime-body theorem. Runtime std,
signatures/targetcontract unchanged; broader04d67f4b/Drop/guard/forget/assume_init/
union/refiner/kernel/memory/alias/provenance stay frozen. Further semantic work
requires a separate owner decision; no additional dispatch authorized at this stop.
Budget **3954/5400 summed hosted jobseconds used;1446remain**, same budget/noreset,
noactive. Last two proof orchestration jobs:37654585346=184s,37656621026=202s.


Original broad scope below is historical where it conflicts with latest freeze.

Previous pointer-ownership phase remains CLOSED;its unused4882s do not transfer.

Target actual `library/core/src/hint.rs::select_unpredictable` at
T=*const Element, with arbitrary thin pointer values and condition, no
Element:Copy/Freeze or Element pointee resources. Prove full modeled selected
pointer equality/provenance, thread token and independent caller frame;
`on_unwind_ens false`, named body/return/leak and generated safety obligations.
All three intrinsics, guards, actual pointer-specialized Drop/drop_in_place,
forget and assume_init remain in the source-linked body. Full sort4 is out of scope.

Before semantic implementation: complete dependency map and component design
with applicability, source/body links, trusted delta, exact normal/unwind/resource
contracts, positive/negative/admission/classifier matrix. Examine existing
MaybeUninit open/close, storage/ref/borrow/pointer-cast rules first. Start with
SAFE as_mut_ptr returning *mut *const Element for both known and unknown inner;
address access must not invent initialization or Element pointee rights.

Allowlist: narrow std specifications and MIR translator rules for these exact
pointer-helper operations, including defined wrapper storage using existing
predicates/borrow rules; proof annotations, source/MIR certificate/harness/runner
and evidence packaging. Every semantic delta separately described/pinned before
implementation; constructor O4 is a required regression in each changed profile.
Existing VF26.09 base809de459/nightly2026-02-05/schema/export/refiner/prelude/kernel/
general memory/provenance/aliasing frozen. Existing accepted constructor patch
325af428 remains immutable; new profile(s) separate, never combine old layout or
historical general Drop/FnMut/copy patches. Runtime std/generic signatures unchanged.

For runtime functions use exact source-linked checked bodies. Intrinsics require
explicitly declared narrow trusted type/semantic rule, not claimed Rust-body proof.
Each component: full MIR/dataflow/source integrity/refinement, SAFE/unsafe safety
contract as appropriate, unwind/leak/reachability, wrong result/post/resource loss/
duplication and precise applicability negatives. Initialized/uninitialized remain
distinct; insufficient initialization must reject assume_init at its read/contract
obligation. Unknown/changed MIR rejects. Verify callee same source/profile before
relying on summary; success advances within this list without repeated approvals.

STOP only at necessity to change kernel/general memory/provenance/aliasing, an
uncheckable resource bridge, general unions/arbitrary Drop/FnMut/copy. Preserve
minimal reproducer, precise obligation and why existing rules are insufficient.
Unsupported name alone is no stop reason. Routine implementation/harness fixes
and integration iteration authorized; no speculative unchanged retries.

Nearest hosted run must create separate compact evidence archive<=25MiB with
adapters/logs/classifications/MIR/mutation records/profiles/hashes; no tools/libs.
Include original O4 artifact11473086721/run37601511894 compact evidence with
mapping manifest and raw acceptance-log audit. Preserve historical full archive;
no verification repetition solely for repack. Packaging tests hosted only.

All builds/verifier/executable tests on GitHub-hosted Actions only. Final update
STATUS/design/results/journal/coverage/PLAN and commit/push. Success requires entire
actual helper return and full normal/unwind posts; components reported separately.
If helper passes, map remaining sort4 obligations and next concrete phase.
No upstream PR/messages/submission. RAPx CLOSED/NO-GO;B/C NOT RUN.

Design/map: [design](SORT4-SELECT-POINTER-DESIGN.md).
Evidence/checkpoint: [results](SORT4-SELECT-POINTER-RESULTS.md),STATUS,EXPERIMENT-LOG.

2026-10-07 priority correction: semantic extensions temporarily FROZEN, budget
continues in this same phase. Finish exactsame7bb/v2 intrinsic acceptance through
hosted savedS5j replay with immutable old classifications; no build/proof execution.
S5k/128dd56 had already been dispatched: full component matrix accepted and actual
helper first blocker drop_in_place57. Separate diagnostic failures do not gate
component acceptance. Assume annotation-tail and RawPtr-refinement failures are
not the missing-resource hypothesis; refiner unchanged. Draft04d/profile and
unfinished drop/assume controls NOT RUN, saved under drafts/select-pointer-frozen.
[Results with SHA/run/artifact](SORT4-SELECT-POINTER-RESULTS.md).

S5r2 savedS5j replay accepted, no build/proof execution, same7bb/v2, exact8message
corrections only; original classifications retained. Latest requested priority
complete with first actual blocker drop_in_place57. No helper theorem or semantic
resource boundary established. Budget2398/5400 remains in this phase,3002left,
no active/queued runs. Further semantic work stays FROZEN until owner changes it.
[Replay results/artifact](SORT4-SELECT-POINTER-RESULTS.md).


2026-10-07 owner resumes ONLY S6 pointer drop from bea6248. The semantic freeze
is lifted only for payload *const Element/receiver *mut *const Element checked
method and narrow trusted compiler glue, with full initialized-cell preservation
contract. Same budget2398/5400 used,3002 remain; no reset. Full independent S6
matrix and same-profile regressions precede actual integration; STOP at inability
to derive drop pre or next actual blocker. General Drop/guard/forget/assume-init,
04d67f4b draft, union/refinement/kernel/memory/alias/provenance remain frozen.
Trust review and experiment card committed717b1b6 before implementation.

S6v1 current acceptance37642650884/source4d0e307: full2+11proof/22admissions,
explicit originalv1 proof/regression provenance retained. Actualbaseline reaches
initializedcell pre110 atdrop57. Projectedactual source/export/decode/refinement
passes but ghostsource-span gate rejects beforeproof; no resource verdict.
Narrow S6v2 exact inclusive regular ghostspan+explicit half-open parsercoord gate
pre-reviewed in0da1e0b before edits, fullfreshcomponent/regression matrices and
2independent ghostcoordinate negatives before actual. Trust/compiler/dropmodel
body/posts/memory/refiner/kernel/runtime/CFG unchanged. Budget2995/5400,2405remain,
no reset/no active atprep; ONLY this S6 continuation authorized. STOP at projected
initializedcell failure or nextactual blocker; broader freeze stays in force.
