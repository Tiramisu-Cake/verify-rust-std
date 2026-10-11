# Merge len1 qualification and caller composition — ACTIVE

Session start `2026-10-10T22:36:57Z`, main cutoff `2026-10-11T00:36:57Z`,
finishing cutoff `01:06:57Z`. Hour status delivered `23:35:59Z`; continuation
without waiting. No new experiments/Builds after main cutoff and no automatic
next session. Previous closed checkpoint is preserved in
[archive/FINAL-CHECKPOINT-GUARD-LEN1-20261010.md](archive/FINAL-CHECKPOINT-GUARD-LEN1-20261010.md).

Own project `/root/verify-rust-std-merge-origin`, branch
`merge/incoming-origin-20261009`; initial `92470c3a2292f299207a017f2b7d0a8edfe54974`.
Own tool `/root/verifast-merge-incoming-span`, branch
`merge/incoming-span-lifetime-20261009`; tool unchanged
`df6b3fbfcf4192d6b442d13e35dafe8477a3fe6f`. Later changes preserved.
Policy revision `c7ca8c467aecf10a4b53039372ee97714f854ee3` read; v2 coordinator,
stable owner `merge`, maximum one own and two global queued/running/unresolved.
No foreign worktree/pins/accounts/selector edits, std runtime changes, disk
cleanup, Actions, baseline or upstream publication. Disk checked before evidence
preparation (3.4GiB initially; 3.1GiB during caller preparation).

## Saved regressions

[LEN1-SAVED-REGRESSIONS-20261011.json](LEN1-SAVED-REGRESSIONS-20261011.json)
records replay of saved Build `c6e247a9-20b0-477d-8d5c-b8e9da795542`,
proof `20548c2798115ba6f1ac0d7632aeddc11ea0e8a3`, archive
`ed26546a6d4efbdd4f850b6ed5cb9fa6de18f34d8d27424853d9887d7466c5c3`.
Corrected source-anchor selector reaches `missing_source_quarter`'s mandatory
contract obligation at `verified/lib.rs(52,5-6)`:
`No matching heap chunks: [1/4]array<u64>(src, 1, cons(_, nil))`.
This selector has no relation to `select_unpredictable`.
Direct and nonempty canonical positives admit on saved evidence.
Synthetic service expectation now follows the implemented exact CURRENT effect
body gate: matching name/location alone cannot admit an emp/emp body.
Wrong binder, arbitrary body, duplicate/missing definitions and other unsupported
applications remain refused. Service tests are **PASS_SERVICE_ONLY**;
historical Cloud **INCONCLUSIVE** remains unchanged. Replay is not a new proof.

## New duplication negative and qualified len1 campaign

Historical `duplicate_effect_close` is retained as **UNEXPECTED_ACCEPTANCE /
BAD_NEGATIVE_ORACLE**: the second close could unfold and refold the first chunk.
New `duplicate_effect_simultaneous` has one close, followed by a structured AST
Sep requiring two identical full effects for the same payload. The harness has
one original resource set and no extra ownership. Fresh first close produces
one effect at line105; only the second predicate fails at line106 columns76–98:
`No matching heap chunks: CopyOnDrop_drop_effect(_t, src, dst, len)`.
The nearby nonempty canonical positive constructs and uses one effect, while
the direct body positive verifies the summary's implementation in the same
campaign. Setup/admission/signature failures are not duplication evidence.

Fresh Build `1396ff47-bc4f-4b77-99ea-cf1a4b1c457a`, exact proof=infra
`d491b9378886be6925f5095803818bfb73b692fe`, archive
`56169df42aef94641b2dd56b86576eda2f5853a50f0ba8de268896a09df81a6f`:
full compiler and mandatory normal/unwind smokes **FRESH_PASS**. All12 fixtures
run; direct/canonical positives have fresh proof. Initial diagnostic classifier
expected source aliases rather than the admitted generated symbolic bindings;
raw Build **FAILURE / INCONCLUSIVE** is preserved. Saved classifier correction
pins exact second-predicate location, generated binding names and first-chunk
production; all12 expected classifications now match. Wrong column, wrong
predicate and missing first production remain refused in saved mutations.
[LEN1-QUALIFICATION-20261011.json](LEN1-QUALIFICATION-20261011.json) binds every
saved input hash and classifier version. Verdict:
**QUALIFIED_LEN1_COMPONENT_FRESH_PROOF_PLUS_SAVED_ADMISSION**, for internal
review only. This is neither another proof run nor profile acceptance.

## Caller derivation and composition

First caller Build `c226905b-2b8c-49ef-b795-c6818874bef2`, proof=infra
`7f4d59d10f1396636b84145e3c26cc6d990ade3a`, archive
`aadd6d3d6fa642c9f93f19a6f75cc460a3e1095d6c33b5b248fc4ba08731c164`, is
**INCONCLUSIVE_PREPARATION**. All3 source/MIR/AST gates admit; verifier refuses
unsafe free-function safety_proof without a prototype before copy/call, while
refinement separately refuses local RawPtr. No composition or intended-negative
credit. Exact first causes in
[CALLER-ATTEMPTS-20261011.json](CALLER-ATTEMPTS-20261011.json).

Corrected adapter `7c7e24655c7bdf6e6b00df995da6c8152e315ddc` removes unsupported
safety_proof and closes the CURRENT effect by an inline ghost statement after
actual dynamic-length copy. The caller first derives canonical own/FBC resources
from actual `tail.read()` and `CopyOnDrop { src: &*tmp, dst: tail, len: 1 }`.
Field halves, padding and source quarter are conserved through FBC; live
allocation geometry supplies guard separation, constructor supplies length and
field identities. Existing close_points_to folds the initialized guard before
`&mut gap_guard as *mut CopyOnDrop`; open_points_to exposes returned fields and
padding with ref_mut_end_token. Helper entry consumes those physical resources,
normal post returns them plus CURRENT effect, and end_ref_mut returns the guard
allocation before effect recovery/end_ref_readonly/end_lifetime/full normal
posts. There is no assumed pointer-origin equality or supplied body input.
Corrected adapter **NOT_RUN until terminal fresh evidence**.

Source mapping: pinned std read/constructor550–551, Drop copy306; u64 helper
substitutes `self.field` with `(*guard).field` only and retains dynamic len.
MIR gates bind unique helper/caller and copy/call source lines, live debug
bindings and exact three-field guard aggregate. AST gates bind nonempty own,
generated FBC, defined exact CURRENT effect and real call; helper effect close
and return/leak evidence are pinned to their function source lines. Manual
specialization is **not compiler-produced Drop/glue** or whole insert_tail.

## Supplied premises and open boundaries

Caller entry still supplies initialized tail storage/held u64 ownership,
thread token, type interpretation, u64 positive size/alignment, object limits,
isize/no-overflow bounds. Lifetime resources originate in existing reference
operations. Constructor/body entry facts are derived only if fresh composition
closes: source/destination identities, len1, source quarter/destination gap,
CURRENT owner, payload geometry/separation, physical guard fields/padding and
borrow return token. Actual Drop receiver `ref_origin(self)==self` applicability
remains **OPEN**; the raw helper does not establish that method precondition.

Actual compiler Drop/glue **NOT_IMPLEMENTED**. Panic/unwind cleanup
**NOT_PROVED / NOT_EXERCISED** in the normal fragment. Generic/ZST, comparator,
whole insert_tail and arbitrary n **NOT_RUN / OUT_OF_SCOPE**. Existing full
caller normal/unwind posts are preserved; helper on_unwind_ens false does not
prove panic cleanup. Guard21/span6 previous Build
`b1da6f8e-7569-4070-b86d-857bce812c13` remains **PREVIOUS_FRESH_PASS**, unchanged
profile **NOT_RERUN**. Both mandatory normal/unwind smoke regressions are
retained in each current Cloud lane.

## Complete effective tool and dependencies

Profile `experimental-merge-qualified-guard-onecell-v1`, SHA256
`0b8cf55b0e7b5a1d0e0595b1483726459cb1d2f40264311e2014d3580ad189b8`;
**NOT_ACCEPTED / NOT_FOR_INTEGRATION**. Effective base
`f76012fb518703b1d98e243ac4f487f16877cfcb` plus ordered ten patches:
wrapping, callback, copy, cleanup, usize, stack-address, tracked-MD,
allocation-span, unit-layout, guard-layout. [EFFECTIVE-SOURCE.json](EFFECTIVE-SOURCE.json)
records all patch hashes and twelve trusted effective file hashes. Component
SHA alone is insufficient. Guard patch
`16476ac7e615831bfd49cec3efdcefd1d76eab1a57f2df47b97f43fb8d6a1d74`, exporter
`f80da46a4e5dd7dc89888d0392a29ff5fee1f096c85845c1f33517f46c93526b`, schema
`bac5f307bb74f0e98efeebfe67649639666ec4a9e38c3cb8bcb60a3259fe31f9`.
Pinned Rust nightly2026-09-25/compiler
`f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`, x86_64-unknown-linux-gnu;
VFdeps archive `8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580`,
OCaml4.14.0, Capnp0.10.4, decoder
`2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2`, Dune binary
`2fb09b0245e247ee2501fdce01a18a8665bdc03d0a5fe90b8e0e18867261000a`.
Numeric Dune version was not captured. No trust patch was changed this session.

## Accounting and continuation

[BUDGET.json](BUDGET.json) is authoritative: 3600 fresh seconds create→finish,
including failures, no carryover. Two terminal/accounted builds so far:444+405
=849 seconds; 2751 remain before pending corrected submission. All archive,
index, inventory and pinned config/source integrity checks completed for these
builds. Pending submission must be reconciled before any duplicate or new Build.

Saved replay (in own worktree; saved archive unpacked outside Git):

```bash
python3 -B research/challenge-8/cloud-build/origin-layout/saved-len1-replay.py \
 /tmp/merge-len1-fresh-1396ff47/saved/allprooflogs/checked-minimal-bridge/onecell-drop-interface \
 --build-id 1396ff47-bc4f-4b77-99ea-cf1a4b1c457a \
 --proof-sha d491b9378886be6925f5095803818bfb73b692fe \
 --archive-sha256 56169df42aef94641b2dd56b86576eda2f5853a50f0ba8de268896a09df81a6f
python3 -B research/challenge-8/cloud-build/origin-layout/onecell-interface-admission-service-test.py
python3 -B research/challenge-8/cloud-build/origin-layout/len1-runner-service-test.py
```

Cloud reconciliation uses the existing client only:

```bash
python3 -B research/challenge-8/cloud-build/control.py \
 --phase-id MERGE-LEN1-COMPOSITION-CLOUD-2026-10-11 --owner merge \
 --ledger /root/verify-rust-std-merge-origin/research/challenge-8/cloud-build/origin-layout/BUDGET.json \
 --state-dir /tmp/merge-len1-composition-20261011 status
```

At closure record terminal Builds, exact spend/retired balance, withdraw own
request/reservation and preserve any unresolved ID/token with next action.
