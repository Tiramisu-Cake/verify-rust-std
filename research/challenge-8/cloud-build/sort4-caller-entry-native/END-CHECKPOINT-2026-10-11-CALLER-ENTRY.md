# Actual caller entry session checkpoint — CLOSED

Owner `select-sort4`, worktree `/root/verify-rust-std-select-night`, branch
`research/night-select-sort4-cloud-2026-10-09`. Initial checkpoint
`0f673c4f05b5c04f0704244e93f929c78611e0fa`; fetched origin, initial clean
worktree/HEAD/branch/remotes checked; no foreign worktree edits.
Policy full revision `c7ca8c467aecf10a4b53039372ee97714f854ee3`, adoption
`6726a08d30b37d6d0f4ae65c3d8c2861615d249a`.
Phase `SORT4-ACTUAL-CALLER-ENTRY-CLOUD-2026-10-11`, new 3600-second account,
start13:54:02/main15:54:02/finish-only16:24:02 UTC. Existing lane
`o26-sort4-c1-current-recovery`, Cloud `smallsort-ci/global`, v2 coordinator,
at most two project Builds/one owner-ledger retained. No local proof execution.

## Proven component and actual helper boundary

The one-symbol [pointer patch](../../caller-entry/verifast-slice-as-mut-ptr.patch)
adds exact `[T]::as_mut_ptr` to the existing typed slice pointer-cast arm;
SHA `f200a5812149bb2278ded1d1ccb27a104b3dec3c03c5e40c79e30409d0d06916`.
Canonical source/method bytes and full profiles are pinned. The change supplies
no ownership, initialized T cells, alias/provenance or lifetime authority.
Frozen ZST/C1/C4 snapshots and runtime std/generic signatures remain unchanged.
Rationale and trust/gates were written before implementation; tool build and
application occurred only in isolated Cloud checkouts.

Fresh canonical T/MU bodies and real pointer consumer with actual scratch
MU-to-T pointer cast verify with full native resources/posts, refinement,
strict lifetime, unit/free/leak and physical execution checks. Wrong-pointer,
unrelated raw authority and initialized-T-from-MU assertions fail at intended
locations. Source mutations, malformed phase and default-off binding controls
are separate admissions, not semantic proof negatives.

Both unfiltered actual `small_sort_general_with_scratch` prefix variants pass
paired MIR/refinement, then stop at `smallsort.rs:230`, mapped to
`verified/lib.rs(20,24-32)`: `len + 16 <= usize::MAX`. Abort and pointer calls
are later and not reached. Native ZST footprint gives no count bound; helper
has no ZST guard. Exporter overflow checks are off; this is a proof/model VC,
not evidence of runtime UB. No artificial guard, nonzero entry assumption,
general arithmetic repair or abort alias was introduced.

## Public guard and composition

Third Build `d352b4a6`'s exact stable public guard fixtures stop at generic T
resolution in copied BufGuard before guard; no positive/negative credit.
Fourth Build `00e90a4b-b7ed-4b92-8b07-bbf168dbc820`, proof=infra
`4871e8a6b47d9f863d42df802233496a051a7242`, checks actual
`unstable::sort<T,F>` first `T::IS_ZST` guard, cut before len/likely.
The reachable ZST-branch `assert false` rejects at lib.rs(10,20-25), with
paired support/refinement. Positive and false-zero continuation assertions
both stop at lib.rs(12,28-29), `No such function: size_of`; no nonzero positive
or continuation-negative credit. Rust use aliases are not ghost name aliases.
The next proof-only notation candidate is the established fully qualified
`std::mem::size_of::<T>()`, with updated classifier tokens/template pin and a
fresh run; it was not implemented after the main deadline. Public cases use
pre-binding translator66e266d3; pointer consumers use post-binding21ca026a.
No combined caller proof or guard-fact transfer is claimed.

Even a successful public guard component proves neither the intervening
call chain nor nonzero/length/resource transfer into the helper. The static
[premise map](CALLER-PREMISE-MAP.md) and
[routes](UPSTREAM-DOMAIN-ROUTES.md) keep Freeze specialization, lengths/overflow,
source, opaque scratch, callback and lifetime obligations separate.
Actual caller-to-C4 composition is NOT_RUN because entry bridge remains open.
Earlier native C1/C4 guarded-fragment PASS is historical and not transferred
to this changed caller/binding. Full five-comparison sort4/C5/copies, second
direct call, sort8, tail/merge and full actual caller contract remain open.
Research sizezero-return is not a proved actual caller check or generic sort4
ZST safety. Profiles remain experimental/unaccepted; maintainer owns review
and integration, while this mission remains owned by select-sort4.

## Evidence/account state

First Build `a125db66` (46ffa84f): 394sec, terminal FAILURE; components VF0,
prefix syntax error and untyped collector audit, no caller semantic result.
Second `1d2237d7` (0a61febf): 374sec, collector SUCCESS; reviewed pointer
gates and helper overflow. Third `d352b4a6` (3ed89d79): 389sec, collector
SUCCESS; same helper/pointer results, public stable fixture frontend failure.
First three standard downloads and all raw inventories/text chunks verified.
Fourth `00e90a4b` (4871e8a6): 432sec, collector SUCCESS, standard delivery and
all raw inventories/text chunks verified. Archive
`2c3e5c6870d51c605221f875abf87d7d21e7ef814b53614d2f84fefde7782760`.
The target proof audit retains accepted=false/verification_accepted=false;
collector success is not caller/guard proof PASS.

Exact proof/infra SHA, config/payload hashes, preflight manifests, raw archive
hashes and commands are preserved in [EXPERIMENT-LOG](../../EXPERIMENT-LOG.md),
fresh review files and [ledger](BUDGET-2026-10-11.json). Raw archives are retained
under each exact Build ID in
`gs://smallsort-ci-evidence-504462351565/cloud-build/`; downloads/extractions are
under `/tmp/caller-entry-<id>-read` and `/tmp/caller-entry-<id>-raw`.
[Review package](REVIEW-PACKAGE.md) contains candidate patch/rationale, complete
base/result manifests, commands and open model/tool/source trust obligations.
[Recorded commands and evidence](REPRODUCTION.md) give all four exact runs.

Account CLOSED at2026-10-11T15:57:57.997385Z. Four terminal Builds, all
accounted/download verified:394+374+389+432=1589/3600 conservative seconds.
Unused2011 retired, no carry. Own active/unresolved Builds/reservations none;
ready request withdrawn through client; schema2/max2 independently checked.
Cloud profile disabled. After15:54:02 only the already-begun Build's evidence,
accounting/review/checkpoint completed. No pending implementation draft;
review-ready candidate has explicitly recorded failing fixture obligations. No merge, upstream publication or external messages.
No automatic next session. The first next obligation is genuine caller-derived
entry domain transfer, not an assumed nonzero premise or MU ownership inverse.
