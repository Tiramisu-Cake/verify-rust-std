# MERGE-INCOMING-SPAN-LIFETIME-CLOUD-2026-10-09 — CLOSED / NO-GO FOR INTEGRATION

Owner `merge`, branch `overnight/merge-26.10`, start 2026-10-09 18:49:50 UTC;
main deadline 19:49:50, absolute deadline 20:19:50. After main: evidence, existing
run replay, package and checkpoint only; no new implementation/hypothesis/build.
Policy revision `1fcd91eff1507fe0bd0620a23b578edb454f1c3e`.
Entry `a61cc2b6b3cc44e92c19eafaf118ac0edb93243b`; own remote fetched and equal at
entry and closeout. Preserved checkpoint `2973280748cdc4eff447404a59fda197aa8b3a78`
and previous research package commit `63b54dcd4a8367ff0e37b308c82b8bc1e3592a0e`.

## Candidate and actual lifetime boundary

Own isolated tool worktree `/root/verifast-merge-incoming-span`, branch
`merge/incoming-span-lifetime-20261009`, base
`f76012fb518703b1d98e243ac4f487f16877cfcb`, portable code commit
`75099c958eb6a6d46016babf0a845a624f77d9ab`.
Old rejected `2f61f966a4a2549cb016164e35848abd21594a6f` and
`8c1386a802ba2ff43ffdd6787eaef5e47bf068e1` are not ancestors; their broad
hoisted-declaration heap exclusion is absent. They remain NOT_FOR_INTEGRATION.

MIR StorageLive/StorageDead are translated in statement order. Address-taken
hoisted declarations defer storage production until StorageLive. StorageDead
uses existing initialized/uninitialized physical cleanup and removes the current
path's address binding; saved raw pointer values remain unconstrained. A later
StorageLive gets a new symbolic address, without global numeric freshness.
Incoming anchors require the identical physical entry Chunk object still in the
current heap and a proved positive real, non-dummy fraction; entry snapshot or
parameter spelling alone is insufficient. Verified calls cannot deallocate while
framing that live fraction. Consumption/reproduction, deallocation, or losing the
chunk disables eligibility; arbitrary callbacks do not preserve entry authority
by assumption. `tail.read` preserves the exact dereference chunk in the narrow
lowered path, even after its value is moved out. Subobjects cover only their own
eligible fixed byte extent; same-allocation aliases are not separated.

Geometry domain: fixed scalar/pointer extents only. Generic T, structs and arrays
are excluded: existing modeled sizeof positivity does not establish runtime
nonzero layout for concrete unit/ZST specialization. Full insert_tail's comparator
path and actual caller region authority are not discharged by this fragment.

Trust changes: translator lifecycle lowering and kernel allocation/death/context
bookkeeping plus pure span facts. No new bytes, fractions, initializedness,
reference tokens, T.own or copy summary. Existing validity/lifetime/leak/unwind
obligations remain. [Rationale](../cloud-build/incoming-span-lifetime/RATIONALE.md)
and [independent review](../cloud-build/incoming-span-lifetime/INDEPENDENT-REVIEW.md).

**New candidate also NOT_FOR_INTEGRATION.** Reserved lifecycle events are ordinary
CallExprs identified by spelling/shape. Independent review found an extern
prototype/diverging source-call route that may forge an event and bypass normal
function resolution. This is a code-derived potential unsoundness, NOT a tested
exploit. An unforgeable internal MIR/AST event is required. Six passing controls
cannot clear that admission gate or prove whole-model soundness.

## New exact Cloud profile and controls

Proof/infra `ca0dfad5f771fd686c5dc9a49899d79be1a1bdc2`; profile
`experimental-merge-incoming-span-lifetime-onecell-v2`, NOT_ACCEPTED.
[Exact input pins](../cloud-build/incoming-span-lifetime/PROFILE.json) and
[fresh assembled binary identity](../cloud-build/incoming-span-lifetime/CLOUD-PROFILE-BUILD.json).
Console SHA256 `9e38349aa6e74a3653f50f0d8179874b85779a1476635aa07e51316a5b0152a5`.
Exporter `b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796`;
refiner `b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28`;
Rust nightly-2026-09-25, rustc commit
`f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`, exact exporter schema/driver hashes
retained in immutable archive environment. Baseline six-profile sources, tracked
MD patch and lifecycle patch are independently hashed; stock-base assembly is
not the tested profile. No identity check was disabled.

| Control | Fresh result | Intended stage/obligation |
| --- | --- | --- |
| span_positive | PASS_CONTROL | fixed u64 new local vs positive incoming fractional frame, target and normal return/leak checks |
| span_retired_local_reuse | EXPECTED_REJECTION | Cannot prove q != saved at line30; no imposed inequality after retirement |
| span_overlap | EXPECTED_REJECTION | Both legal readonly alias reads executed (17/18), false same-allocation span assertion at20 |
| span_raw_arbitrary | EXPECTED_REJECTION | No physical incoming anchor; false span assertion at21 |
| span_lost_incoming_authority | EXPECTED_REJECTION | Entry authority leaked before allocation; false span assertion at20 |
| span_zero_extent | EXPECTED_REJECTION | Abstract sizeof(T)=0; pointer inequality at23; NOT concrete T=() layout qualification |

Every negative reached its exact assertion with exporter/decode/refinement0 and
verifier1; no frontend/setup failure counted as semantic rejection. Retirement
has actual decoded MIR tmp0 `_2` StorageDead(block2,statement7,line23) before
tmp1 `_7` StorageLive(block2,statement8,line24), and matching translated AST.
Decoded MIR SHA256 `a7f9950ebe4c888eea6d11241bf1afd99d9e76c025fcaeaff1c838eede3aba59`;
proof AST `a44d4a7b420b9a4df4fe58e84e3b94ce43d82d162dc29cd23c557bcf3447a15f`.
This eliminates the old retirement diagnostic counterexample in this control;
it does not establish all lifecycle/call/subobject paths. Authority control uses
ghost leak, not a tested real deallocator/callback. Those paths remain admission
obligations. Byte-array alternate representations and broad regression suite NOT_RUN.

## Actual source-linked tmp→tail rerun

Same runtime source/signatures; source SHA256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`.
Source/MIR/AST admission and source integrity at every stage passed anew. Positive
trace proves current guard.src == held_ref and guard.dst == tail (64/65), existing
shared-derived alignment helper call (66), source limits (67), source no-overflow
(68). Real fractions/values/ref initialization are retained, without convenient
replacement pointers or an added separation premise.

First failure at69: numeric span separation **before FBC** cannot be derived for
generic T (excluded domain). Thus FBC witness loss is not the only separation
issue. Guard geometry packaging, post-FBC separation, destination geometry at
81–86, literal-one copy87, end_ref_readonly90, complementary tmp storage,
CURRENT-owner association/transfer, cleanup and normal/unwind posts are NOT_REACHED.
Positive, after_fbc_false, after_recovery_false, missing_held_owner and
double_physical_fbc all INCONCLUSIVE for their intended later gates, each stopping
at69. Neither false control is credited. Historical candidate copy/separation and
end_ref_readonly failure are not new-profile results.

Strong supplied premises remain: thread_token(t), t == currentThread, type_interp<T>,
0 < sizeof(T) <= isize::MAX, incoming tail nonnull/aligned/object-within-limits and
nonoverflow, full *tail |-> held with its CURRENT <T>.own(t, held); caller discharge
is OPEN. These sizeof premises alone do not qualify concrete generic runtime
layout for the new geometry rule. No second owner is synthesized. Actual
557/558, Drop/glue, late comparator/full recovery and whole insertion NOT_RUN and
out of this window. Readonly quiescent protocol does not cross arbitrary comparator
interior mutability. No global impossibility or established upstream bug claimed.

## Accounting, evidence and publication

- `af5c4a35-b9f1-4e39-9775-142d236193a2`: FAILURE,369s. Frozen exporter/refiner closure passed, console build0; final source pin mismatch rejected setup. Controls/actual NOT_RUN. Corrected hashes were statically assembled from immutable six-profile baseline source evidence, then tested in second Build.
- `cae0f3cc-9ca4-4ceb-b570-ab5e26e6ce82`: SUCCESS diagnostic collector,391s. Fresh controls and actual verdicts above, profile unaccepted. Archive SHA256 `49c7cf722e561812b18e6112442c3b29b960a6e70dd2dd971075a870ad8b89b8`.

[First receipt](../cloud-build/incoming-span-lifetime/EVIDENCE-af5c4a35.json),
[second receipt](../cloud-build/incoming-span-lifetime/EVIDENCE-cae0f3cc.json).
Immutable gs://smallsort-ci-evidence-504462351565/cloud-build/<BuildID>/ archives,
upload/file inventories and external text indexes verified. Archived logs read;
external text chunks not downloaded. Fresh source/proof/infra/config/tool pins are
in receipts and archive certificates. No historical PASS used as fresh proof.

New proof: six mechanism controls + five actual cases, results above. Replay:
frozen dependency bootstrap synthetic service PASS, retirement parser service PASS,
legacy-profile refusal replay PASS, fresh six-control saved-data classifier replay
PASS. Full relocated outer-audit replay is INCONCLUSIVE because source-selection
repo topology and original absolute Cloud profile paths differ; immutable original
Cloud outer audit remains valid. No audit gate was relaxed. Broad suites, MD
regressions on new profile, marker-forgery proof, concrete unit layout NOT_RUN.

Ledger **760/3600 conservative build seconds** (create-to-finish rounded up),
2840 unused CLOSED; old2555 not carried. Both own Builds terminal and downloads
verified; active/unresolved/reservation none, ready request WITHDRAWN. Shared
coordinator remains v2/max2. No foreign reservation/process/worktree/ledger changed.

Internal review package is added under `research/verifast-review/<this checkpoint's
full commit SHA>/` on origin review/verifast, preserving prior package/history.
Its publication receipt follows in the phase PUBLICATION.json; no maintainer
receipt, transfer of active ownership, integration, acceptance or upstream PR.

One next task: **replace spelling-based lifecycle calls with unforgeable internal
MIR/AST events, then validate marker-forgery and lifetime controls in a newly
authorized Cloud phase**. Generic runtime extent bridge remains a separate open
admission question before actual tmp→tail can benefit from geometry.
