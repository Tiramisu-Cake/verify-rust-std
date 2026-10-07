# Source-linked pointer select completion phase

Owner authorization2026-10-07; entry
`cd44e1bbf115c83c84fd7d4c050b1f74be0e1d09` on challenge-8/research.
**IN PROGRESS.** New5400summed hosted-job-second budget,<=1800/job,
<=300/individual proof,one active relevant workflow_dispatch. Spend2398/5400;3002remain,noactive.
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
