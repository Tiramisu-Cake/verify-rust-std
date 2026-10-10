# Merge guard qualification / len1 session — CLOSED

Session start **2026-10-10T19:26:15Z**; main cutoff **21:26:15Z**;
absolute finishing cutoff **21:56:15Z**. Hour update delivered at20:26 UTC.
All Builds are terminal/accounted; final evidence review completed before the
absolute cutoff. No new Build or
experiment after main; no automatic next session. This checkpoint replaces the
previous closed compile-session checkpoint, retained in
[archive/FINAL-CHECKPOINT-COMPILE-20261010.md](archive/FINAL-CHECKPOINT-COMPILE-20261010.md).

Assigned project `/root/verify-rust-std-merge-origin`, branch
`merge/incoming-origin-20261009`; initial HEAD
`0f770c2236d0e1a66000e003bc77d08586d1b931`. Git-dir/index:
`/root/verify-rust-std/.git/worktrees/verify-rust-std-merge-origin[/index]`.
Assigned tool `/root/verifast-merge-incoming-span`, branch
`merge/incoming-span-lifetime-20261009`; initial tool
`e16352c4f015059ea4158be7d3205275080ce880`, current tool
`df6b3fbfcf4192d6b442d13e35dafe8477a3fe6f`; git-dir/index:
`/root/verifast/.git/worktrees/verifast-merge-incoming-span[/index]`.
Later own changes preserved. Third-agent selector patches, foreign worktrees,
pins, ledgers and maintainer integration excluded. Runtime std and final
contracts/refinement/dead-code/unwind/leak checks conserved. No Actions or
upstream publication. Policy `c7ca8c467aecf10a4b53039372ee97714f854ee3`, adoption
`1b9e3df3182d13e5adf7d2e5d04afcfbc1851f14`, ACK
`aec832ab25ba65a5ddc643ca325f8d8ea8b2b612` retained.

## Fresh guard theorem

Build **b1da6f8e-7569-4070-b86d-857bce812c13**, proof=infra
**7995fccfee6c0e29621c2cffcca94161c7e05729**, passed the full candidate build,
mandatory smokes and all21 bounded controls. Archive SHA256
`a47f1958ffa4a08b9d7147059fab95e21a65aebc35c3802cc3009ef8d7f2e1dc`
and all text chunks integrity verified. `qualified_live_guard` proves extent
at76, actual storage alignment80, separation81, preservation through the
precise half-FBC frame100, bounded copy and CURRENT recovery, complete normal
posts, return131 and zero leak errors. **FRESH_PASS_CONTROL**, component only;
combined profile **NOT_ACCEPTED**, integration **NOT_FOR_INTEGRATION**.

Extent and alignment originate from the pinned compiler's `layout_of` for the
same local DefId, exact full HIR Item source span, concrete nongeneric guard
instance, DefPathHash and x86_64/pointer64 target. Schema/decoder/translator
retain these qualifications; model binds the exact generated StructType's
`sizeof`, `alignof`, field sizes and offset functions used by storage and
pointer geometry. The observed instance has size24, alignment8 and offsets
0,8,16. These are qualified facts for this instance, not guessed constants or
an axiom attached only to a textual name. Physical storage alignment uses the
existing typed-byte conversion lemma. Its returned aggregate is opened with
existing `open_points_to`, retaining its coefficient and saved field values.

Separation originates at actual validated MIR `StorageLive` allocation events
for the guard and tracked tmp. Hidden receipts bind the allocated pointer in
the same lexical scope; only simultaneously live supported positive extents
qualify. Entry comparisons require original surviving physical chunks with a
positive non-dummy fraction; references carry the same pointer geometry.
`StorageDead` and physical/lexical cleanup retire receipts. Guard fields and
padding stay physical resources. FBC preserves the established pure relation;
it creates no allocation, ownership, permission or lost authority. Different
names, addresses and retained chunks alone are insufficient.

Semantic negatives are fresh intended refusals: overlap/zero claims atTARGET82,
missing StorageLive/resources atTARGET10 after qualified extent, and four
unqualified layout cases (wrong constness, renamed source, generic and ZST)
at their size assertion. ILP32 is a separately recorded frontend target
admission refusal, **not** a semantic negative. Full mutable canonical FBC
construction followed by false reaches its exact entry assertion; this is
entry-only evidence, not mutable callee/caller/CURRENT recovery credit.

No supplied guard-size or root/source separation added. Bounded constructor
fixture still supplies valid tail physical storage, thread/type interpretation
and u64 ownership, payload extent/alignment/limits/no-overflow and relevant
lifetime resources; len1 comes from the actual constructor. Standalone len1
body/interface takes explicit fields/padding, source quarter at CURRENT,
destination gap, len1 and payload geometry/separation. Caller derivation of
those premises remains a separate obligation. Supported domain is concrete
u64/x86_64, the exactly qualified guard and supported scalar/pointer live
storage. Generic/ZST/arrays, comparator/user-Drop and whole insert_tail remain
unsupported or open. Historical count-n contract is not proved by removing
premises from a separate len1 helper.

## Preparation repairs and retained failures

Saved282324ae replay reproduced post-FBC insertion splitting manifest ghost
fragment4. The sole exact fragment was updated to include the assertion,
then exact ghost removal recovered the original runtime bytes. Four prepared
fixtures and causal mutations passed; no hash allowlist/admission widening.
Fresh builds reached exporter and proof, closing this preparation blocker.

Build2caa4a93 reached extent76 but qualified metadata was absent: exporter
`tcx.def_span` covered only the header. Reproducer and independent addressed
review preceded the same-DefId full HIR Item span repair, tooldf6b3fbf. No
other type/target/source/layout guard changed. Buildc766f676 freshly compiled
and proved extent/alignment, then lacked the field frame at separation80.
Annotation-only `open_points_to` restored the returned initialized aggregate's
same coefficient/value fields and padding; independent review GO preceded
b1da6f8e full guard theorem. All failures and exact source/MIR/AST are retained.

The first len1 Build ce59352c failed before compiler/export/proof: the provider
still expected the old exact `run.sh` base hash after adding len1 mode. The
actual refusal was reproduced using the real18 pinned input files; sole exact
pin updated to `cc8327ec962bccc3a71129f7296b72517152a9d457799ad369aab4b66303c9e9`.
All18 real provider transforms prepared, independent review GO. Prior fixture
and syntax preflights did not cover that outer gate; the new preflight does.
Neither this replay nor ce59352c provides len1 proof credit.

## Len1 started step — fresh raw proof, incomplete campaign

Final Build **c6e247a9-20b0-477d-8d5c-b8e9da795542** created
**2026-10-10T21:23:00.891539584Z**, proof=infra
**20548c2798115ba6f1ac0d7632aeddc11ea0e8a3**, unchanged tool/profile. Campaign
`len1-minimal-v1` contains12 exact cases; original runtime body keeps self.len.
Source-linked mechanical u64 specialization is not compiler-produced
monomorphic Drop MIR or an actual destructor caller. The nonempty canonical
own/FBC proposal passes resources through a checked body call into a same-file
defined CURRENT effect; `own=false` compatibility is vacuous and never counted.
Initial effect AST body and sole no-effect leak classifier failed closed until
this raw evidence grounded their precise shape and diagnostic. Pure source/ghost
preparation and isolated saved/synthetic service checks passed; Fresh raw direct and canonical positives have exporter/decode/refinement/verifier
exit0, actual copy/normal return/leak, no dead-code records. Independent resource
review confirms nonempty canonical own -> generated FBC fields/padding -> checked
call -> same defined CURRENT effect, normal generated field/padding/effect post;
unwind field/padding post is unchanged. Standalone generated canonical pre still
supplies ref_origin(self)==self; this is not actual caller origin construction.
No user-authored Assume/Leak occurs in the checked proof/effect; a preexisting
generated end_ref_padding helper has a false assumption stub outside this trace
and is not called. Original global AST assumptions are not claimed absent.

Raw classification remains INCONCLUSIVE: MIR classifier used nonexistent
provider local_name API; effect declaration/definition location check was wrong,
and exact effect-body gate intentionally failed closed. Saved-data classifier replay now binds the positive source/MIR/AST gates and
reports DIRECT_STRONG_PRE_BODY_PASS_CONDITIONAL and
CANONICAL_ONECELL_EFFECT_INTERFACE_PASS_FRAGMENT_ONLY. This supplements the
fresh proof at exact20548c27; the closing classifier/documentation commit is
not a new proof run. All trusted tool/profile/source fixtures remain unchanged.
The complete campaign still fails its exact expected-classification map.
Malformed effect signature and missing definition reject at the intended
verifier qualification gate. No-effect control reaches the exact sole residual
type_interp + sourcequarter array + destination array prototype leak.

`duplicate_effect_close` unexpectedly verifies. Its second close auto-opens the
first effect chunk and refolds the same resources; it does not demand two
simultaneous effects. Independent review confirms this is a bad duplication
oracle, not evidence of resource creation. Preserve its unexpected result and
all_matched=false; no classifier fix may make this a successful negative.
A future negative must require two full effects simultaneously. The current
12-case campaign is incomplete even if individual positive admission closes.
Actual caller/glue/panic are not implemented by this campaign.

| Obligation | Verdict at current checkpoint |
| --- | --- |
| Candidate exporter/decoder/translator/full verifier build | FRESH_PASS c766f676 and b1da6f8e |
| Final fixture preparation | FRESH_PASS guard; len1 provider replay PASS_PREPARATION_ONLY |
| Qualified guard extent/alignment/separation and half-FBC preservation | FRESH_PASS_CONTROL b1da6f8e |
| Addressed guard/span/recovery negatives | FRESH intended matched rejections b1da6f8e |
| Retained-six and exact-combined normal/unwind smoke | FRESH_PASS b1da6f8e |
| Six span controls | FRESH matched6/6 b1da6f8e |
| Bounded CURRENT copy/recovery full normal posts/return/leak | FRESH_PASS_FRAGMENT_ONLY b1da6f8e |
| Historical specialized strong-pre Drop body | Retained conditional PASS on historical profile |
| New len1 strong-pre body | FRESH_PROOF + SAVED_ADMISSION_REPLAY: DIRECT_STRONG_PRE_BODY_PASS_CONDITIONAL |
| Nonvacuous canonical interface | FRESH_PROOF + SAVED_ADMISSION_REPLAY: PASS_FRAGMENT_ONLY; nonempty own/FBC/call/effect |
| Actual one-cell mutable caller composition | NOT_RUN |
| Actual compiler Drop/glue | NOT_IMPLEMENTED, out of scope |
| Actual panic/unwind cleanup | NOT_EXERCISED, out of scope |
| Whole combined profile / maintainer integration | NOT_ACCEPTED / NOT_FOR_INTEGRATION |

## Exact candidate and dependencies

Tool component **df6b3fbfcf4192d6b442d13e35dafe8477a3fe6f**; effective Cloud
source base **f76012fb518703b1d98e243ac4f487f16877cfcb** plus10 ordered patches:
wrapping, callback, copy, cleanup, usize-multiple, stack-address, tracked-MD,
allocation-span, unit-layout, guard-layout. [EFFECTIVE-SOURCE.json](EFFECTIVE-SOURCE.json)
records every patch and all12 effective trusted file hashes; component alone
is not the full composed profile. Profile
`experimental-merge-qualified-guard-onecell-v1`, SHA256
**0b8cf55b0e7b5a1d0e0595b1483726459cb1d2f40264311e2014d3580ad189b8**;
guard patch **16476ac7e615831bfd49cec3efdcefd1d76eab1a57f2df47b97f43fb8d6a1d74**.
Exporter `f80da46a4e5dd7dc89888d0392a29ff5fee1f096c85845c1f33517f46c93526b`;
schema `bac5f307bb74f0e98efeebfe67649639666ec4a9e38c3cb8bcb60a3259fe31f9`.
No foreign selector patch is included.

Pinned Rust nightly2026-09-25, compiler
`f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`, x86_64-unknown-linux-gnu;
real VFdeps archive `8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580`,
OCaml4.14.0, Capnp0.10.4, decoder
`2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2`, Dune binary SHA256
`2fb09b0245e247ee2501fdce01a18a8665bdc03d0a5fe90b8e0e18867261000a`.
Numeric Dune version was not captured. Existing reproducible build retained;
no new cache mechanism or assumed cross-build binary identity. No separate
compile-only series after the previously confirmed build.

VPS21:23 UTC: RAM1967MiB,288MiB available; swap3915MiB used/0free;
disk59MiB free; load26.45/28.72/30.29. No compatible local OCaml/Dune; local
compile **NOT_RUN**, elapsed/peak RSS **NOT_MEASURED**. No installs, heavy
local compilation, swap changes or foreign process/data changes. Only own
verified duplicate evidence files were removed after archive/file checks;
raw archives, indices, receipts and actual worktrees remain.

## Build accounting and reproduction

New phase `MERGE-GUARD-LEN1-CLOUD-2026-10-10`, ownermerge,3600 create-to-finish
Cloud seconds including failures. v2/max2 coordinator unchanged; at most one
own queued/running/unresolved Build. Prior1595s account closed separately;
2005 retired, no carryover. [BUDGET.json](BUDGET.json) contains exact timestamps,
source/config/archive hashes and dispatch tokens.

| Build ID | Exact proof=infra | Result | Seconds |
| --- | --- | --- | ---: |
| 2caa4a93-f9e2-4f1f-8f2f-63b230ffed7c | 345138358cafa6568525008a5fa592ba54696698 | FAILURE: qualifier |455|
| c766f676-41e1-47d2-969c-339716c73789 | 29771d654854c6fdd05f7dcfc32a1936fce6ac37 | FAILURE: physical field frame |451|
| b1da6f8e-7569-4070-b86d-857bce812c13 | 7995fccfee6c0e29621c2cffcca94161c7e05729 | SUCCESS: guard component |476|
| ce59352c-dadc-4cd6-971b-c9f56331dfd9 | 46accba0c36492e34403296ae32f81e400939965 | FAILURE before compiler/proof |85|
| c6e247a9-20b0-477d-8d5c-b8e9da795542 | 20548c2798115ba6f1ac0d7632aeddc11ea0e8a3 | FAILURE: diagnostic admission incomplete |491|

All five Builds terminal/accounted, archives integrity verified. **CLOSED1958/3600s**,
**1642 unused retired**, no carryover. Final archive
`ed26546a6d4efbdd4f850b6ed5cb9fa6de18f34d8d27424853d9887d7466c5c3`;
index integrity verified, text chunks were not downloaded for the last Build
(its complete raw archive contains the source/MIR/AST/logs). Final config
`5a43feb5c0a1c8af092bf17dbc375c4420ccac459e8019513ad183949910d1e4`, source input
`a8ee3ad5737a4218506ab679d82d7529fd407d274b3a3fdc85b8bd35d00a6951`, token
`dispatch-5676aec5f7bd4b5eb399a376e3d78924`. Own active/reservations are empty; ready request withdrawn through the client.
No unresolved ID/token. Coordinator v2/max2 and foreign accounts unchanged.
No new session will start automatically.

Replay saved preparation only (no proof tools):

```bash
python3 -B research/challenge-8/cloud-build/origin-layout/guard-fixture-preparation-service-test.py \
  --archive /tmp/merge-bridge-evidence-282324ae/evidence.tar.gz --output NEW_OWN_REPLAY_DIR
python3 -B research/challenge-8/cloud-build/origin-layout/source-replay.py \
  --git-source /root/verifast-merge-incoming-span --output NEW_OWN_TEXT_REPLAY_DIR
```

Guard reproduction uses exact7995fccf (`bridge-minimal`); corrected len1 uses
exact20548c27 (`len1-minimal`). Dispatch only under a newly authorized account
and window after closure:

```bash
python3 -B research/challenge-8/cloud-build/control.py \
  --phase-id NEW_AUTHORIZED_PHASE --owner merge \
  --ledger /root/verify-rust-std-merge-origin/research/challenge-8/cloud-build/origin-layout/BUDGET.json \
  --state-dir NEW_OWN_STATE submit --infra-sha FULL_PUBLISHED_SHA \
  --proof-sha FULL_PUBLISHED_SHA --lane merge --source-mode pinned-objects --timeout 1200
```

Actual current command used phaseMERGE-GUARD-LEN1-CLOUD-2026-10-10,
state-dir/tmp/merge-guard-len1-20261010, exact20548c27 for both SHAs, timeout1200.
Full exporter/decoder/translator/verifier build and source hashes precede
minimal target checks, then mandatory smokes; real pinned dependencies retained.
Next action in a newly authorized window: replace the duplicate-close oracle
with an assertion requiring two simultaneous full effects, preserving the
source/body/interface positives and intended resource negatives. Then construct
actual one-cell caller FBC/own/len1/payload/CURRENT and origin premises from
the real constructor and live allocations; perform an actual resource-transfer
composition run. Readonly half-FBC guard and standalone canonical proof do not
already compose. Actual Drop/glue and panic cleanup remain separate and were
not added. Preserve raw c6e247a9 INCONCLUSIVE, saved classification receipts and
the exact unexpected control rather than rerunning it unchanged.

Final saved-evidence admission details and code identities are retained with
the raw receipt and addressed independent review; actual caller composition
remains NOT_RUN. No new source fixture or proof tool ran locally or after main.

## Final saved admission limits

[LEN1-SAVED-ADMISSION-REPLAY-20261010.json](LEN1-SAVED-ADMISSION-REPLAY-20261010.json)
records the real12-case import-only replay and classifier identity. Individual
direct/canonical positives admit; original Cloud aggregate is not rewritten.
Duplicateclose remains UNEXPECTED_ACCEPTANCE. Missing-source-quarter remains
INCONCLUSIVE: the contract-line selector correction was made after its replay
and was NOT_REPLAYED. The existing synthetic service test failed on a stale
expectation that the now-grounded real effect gate refuses; it was not changed
or claimed PASS. The classifier delta is retained for completion, not accepted
as a fully regressed candidate. Next permitted step is saved replay of that
selector and precise update/replay of the stale service expectation, then a
new reviewed simultaneous-full-effect negative in a new authorized Cloud
window. No new source proof or tool-profile credit from closing commit.
