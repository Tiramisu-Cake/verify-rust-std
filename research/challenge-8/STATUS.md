# Challenge 8: current status

Updated 2026-10-07: **bounded H_align no-patch continuation CLOSED at a
concrete ZST model boundary**. Used1/3 NEW manual hosted runs and38/5400 job-seconds
including preparation, verification, saved-evidence replay and upload. No active
experiment; unused slots are retired at this stop boundary. Fork
`Tiramisu-Cake/verify-rust-std`, branch `challenge-8/research`.
This is the single current checkpoint; procedures in [AGENT-RUNBOOK.md](AGENT-RUNBOOK.md),
plan in [PLAN.md](PLAN.md), history in [EXPERIMENT-LOG.md](EXPERIMENT-LOG.md).

## Authorization and execution state — CLOSED

Owner authorized classifier repair, checked generic const/mut proof development
and original ZST layout trace on unchanged official VF26.09/nightly2026-02-05,
from clean matching f1c0774b3a8662ca4e9d838a4a1ad06f7f625e55. Max3 NEW runs /
90min jobs including setup; no local executable checks, model/spec/kernel patches,
new axioms, outer-contract weakening or runtime/type replacement.
[Card](SORT4-ALIGNMENT-PHASE.md), [results](SORT4-ALIGNMENT-RESULTS.md).

NEW [run37535499783](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37535499783),
source/head_sha ea635ea152f9ff3a491b57b7b6a9df84dc99a4be, remote matched,
verifast_sort4_alignment/30; job21:40:14–21:40:52Z on2026-10-06, FAILURE,38s.
All six exports/decodes/refinements/source-integrity checks pass; VF1 each.
Both generic helpers now complete with explicit nonnegative local req. Existing
array__inv/provenance/layout/size_align facts discharge local bounds and every
reached helper call; .add succeeds. i=1,2,3 paths finish full posts/leak checks;
residual no-helper path fails final returned-pointer alignment post line23.
Whole generic const/mut theorem remains INCONCLUSIVE, no complete no-unwind post.

Original Z layout remains INCONCLUSIVE at size==0 line20 (align8 not reached);
Z add at pointer_within_limits line21. [Pinned-source trace](SORT4-ALIGNMENT-MODEL-BOUNDARY.md)
finds missing repr alignment metadata and incompatible positive struct-size axiom.
A faithful no-patch concrete ZST proof cannot close against that axiom. This is
the phase stop condition; no further fix/run, unused2 slots not carried forward.
ZST remains in target domain. No model correction implemented.

Both byte-offset controls are EXPECTED_FALSE_POST_FAILURE at intended line25
modulus8 assertions after legal .add/cast. Hosted classifier replay/tests PASS:
initial37529855468 six parse errors remain INCONCLUSIVE;37532204465 four positives
INCONCLUSIVE and two negatives reclassified separately as intended failures.
Original logs/JSON/ZIPs and historical outcomes preserved, tree hashes unchanged;
3 test groups and30 fail-closed mutations pass. Artifact11446132505/full logs
inspected. These controls establish neither automatic copy UB nor full sort4 safety.

RAPx0.7.50 remains CLOSED / NO-GO for ZST alignment; automatic RAPx replay CLOSED /
NO-GO; B/C NOT RUN. No other RAPx property is accepted automatically. Kani unchanged.
Generic composition still unavailable. STOP; documentation/commit/push closeout only.
Any later proof diagnostic or layout-model work requires a new decision.

## Historical syntax-only H_align run — CLOSED / INCONCLUSIVE

**CLOSED / INCONCLUSIVE — syntax-only continuation.** Owner explicitly authorized
only report-b1ae937 annotation correction and exactly one additional NEW hosted
H_align run90min including runner preparation. Entry clean matching local/remote
b1ae937f901ad34aeef8bcdbd98997abd1fd1969; origin/branch correct, no active run.
Two signature semicolons removed and six contract blocks split; static checked-
example/payload/ghost-strip audit passed. All six archived originals byte-identical
to historical fixtures. Runner/driver/workflow/std/pins/flags/posts/classifier unchanged.
Correction9474453f231eb600e1ec35d571c8ac4f70fa7138 pushed/remote confirmed;
NEW run37532204465 head_sha matched, created2026-10-06T21:12:28Z, job
21:12:33–21:13:15Z FAILURE (42s), replay SKIPPED. Official VF26.09/
nightly2026-02-05 identities/audits pass. Budget1/1 additional runs used.

All six exports/decodes/refinements and source-integrity checks pass; VF1 each.
First substantive blocker: div_rem_nonneg(address,alignment), prelude64,
Cannot prove 0<=address in both checked generic helpers (caller/.add not reached).
ZST layout stops at size==0 assertion line20; align8 not reached. ZST add stops
at pointer_within_limits obligation line21. Both negatives reach byte add/cast
and reject marked assertion line25; manual intended-negative evidence only.
Automatic all-six INCONCLUSIVE/raw header counts0 retained: parser omits the
source-span prefix present in actual timed function headers. Manual named header
counts1 for each helper and each concrete caller; no classifier repair or raw
JSON overwrite. No positive post proved or full-sort4 theorem gained.
[Results](SORT4-ALIGNMENT-RESULTS.md), [closed scope](SORT4-ALIGNMENT-PHASE.md).
No proof/tool/runner correction or further run after result. No active run;
STOP regardless of outcome; documentation commit/push only. RAPx CLOSED / NO-GO,
B/C NOT RUN; new proof correction/run needs a new owner decision.

## Historical initial H_align run — CLOSED / INCONCLUSIVE

**CLOSED / INCONCLUSIVE — one-run H_align phase.** Owner explicitly resumed
from clean matching HEAD98c0f4f53eca6467a1e0ead8f0260f96b7d53dbc. Prepared/pushed
source17ad1f48b1eb97f806e03a97b7bf64b24f8ac50b, remote matched, no other active
run. Budget1/1 NEW hosted runs used,90min including setup. Run37529855468
created20:53:28UTC, verification job20:53:33–20:54:10UTC FAILURE; selection
verifast_sort4_alignment/90. Official VF26.09 archive/schema/source audits pass;
all six exports/decodes/refinements and source-integrity checks pass.

Generic helpers stop at ghost body `{` line10; other cases stop at `ens` lines
12/13/14. All verifier exits1 before caller/helper headers or pointer operations;
negative alignment assertions at isolated line23 NOT REACHED. Two fixture syntax
mistakes: semicolon terminates ghost lemma declaration before its body; Rust
contract req/ens/unwind clauses need separate annotation ranges. This is our
preparation failure, not H_align refutation or a semantic VeriFast finding.
[Closeout/proposed exact correction](SORT4-ALIGNMENT-RESULTS.md),
[phase](SORT4-ALIGNMENT-PHASE.md). Correction NOT APPLIED / NOT VERIFIED;
no proof/runner/tool changes after this result. Saved logs/artifact inspected;
geometry, ZST layout and automatic-operation coverage remain unestablished.
RAPx A/replay stay NO-GO; B/C NOT RUN. No active run or new proof draft.

## Historical joint-route documentation — CLOSED

**CLOSED — joint-route analysis/documentation only.** Owner requested the
obligation-to-tool/evidence/gap/dependency matrix, compatibility analysis,
independent treatment of the ZST alignment gap and necessary/optional VF changes,
then documentation commit/push. Clean entry local43bc758; origin research head
was newer documentation eda527922ec96468a804e3a62fbc1ca96f23691d. Fetched,
inspected and fast-forwarded before analysis. Correct fork/branch; no queued or
active runs in entry listing. Latest research evidence remains replay37513897141;
latest unrelated run37518141083 is completed SKIPPED.

[Assessment](SORT4-COMPOSITION-ASSESSMENT.md): VF/equivalent resource proof must
cover current callback effects, normal ownership and all five panic exits;
RAPx presently supplies diagnostics only, with no proved actual-sort4 component.
Selected future RAPx low-level facts need independent property/dependency/model
qualification. Known Align bug does not establish reliability of other checks.
ZST remains in the target; RAPx0.7.50 gate A/replay stay CLOSED / NO-GO; B/C
NOT RUN. Kani concrete functionality remains unchanged, without a generic lift.

One proposed independent no-patch VF26.09 alignment-preservation gate is
**NOT RUN / NOT AUTHORIZED**: generic legal .add offsets0..3, including size0 /
align>1, checked base/size premises and intended false-post controls. Geometry
alone is not automatic operation coverage; actual reference/copy alignment
enforcement and selected provenance remain explicit gates. Tuple/HRTB, full
direct-unwind recovery and raw-copy/resource capabilities remain necessary for
the proposed VF role; the entire old insertion patch chain is not required by
current evidence. No changes to std/contract/proofs/verifiers/runners/workflows,
no builds/executable checks/dispatch or external messages. No active run/draft.

## Historical explicit-domain decision — CLOSED

**CLOSED — documentation decision complete; adopted domain recorded.**
From head `43bc758625157febb496804f346b7433f1a21d5a`, the owner chose an explicit
sufficient contract following authoritative C precedents. The
[adopted domain](SORT4-CONTRACT.md#adopted-domain-and-caller-obligations) requires
full source/output byte-range separation, with the existing reference/storage,
callback and resource obligations. ZST byte separation is vacuous; pointer
equality remains allowed and alignment/logical ownership remain required.
Every composed caller must prove the precondition; the existing caller audit
is not a machine-checked composition proof. No Copy/Freeze/purity/no-panic
restriction is added to safety; ordering premises remain separate.

[Authority assessment](C-VERIFICATION-ARTIFACTS.md#authority-and-separation-precedents)
confirms P1's peer-reviewed VMCAI publication and distinguishes Fraunhofer's
reference artifacts and the VeriFast example. They support the specification
method, not minimality, Rust proof results or committee approval. Project
contract choice is settled; external acceptance remains unconfirmed. The
earlier unsent question is retained as history, not the next required action.

Only documentation/source reading, static review and this docs commit/ref
update were in scope. No std/proof/tool/workflow changes or external messages.
The latest ten Actions runs at entry were completed; the latest research run
remains replay37513897141. Previous experiment/replay budgets stay closed.

## Historical admissibility review — CLOSED

**CLOSED — bounded documentation-only sort4 admissibility review.**
Owner resumed from expected/actual HEAD
`826d74b45546f9ce1319e2cd4cac8b6d42a2f41f` for source/primary-source reading,
documentation, commit and push only. Entry tree clean; origin is the named fork,
local/remote research heads match; no active or queued Actions. Latest unrelated
run37518141083 is main's scheduled Subtree Update, completed SKIPPED.
No Actions dispatch, compilation, executable checks, verifier/proof-code changes
or external messages/publication. Reviewed the full research contract's premises
and distinguished caller-established conditions from accepted challenge scope.
Previous experiment and replay budgets are closed; unused slots grant no authority.
[Review and unsent question](SORT4-ADMISSIBILITY-REVIEW.md): local per-copy
non-overlap/reference validity follow actual operations; full range separation
is sufficient and caller-established, not proved necessary or organizer-accepted.
Raw scratch and retained-originals ownership match audited routes; full exclusive
resources/Shadow/no proof debt are our accounting protocol, not all mandatory UB
conditions. Legal callback effects and all five panic exits stay in safety scope.
Official issue56 answer discusses insufficient safety comments and functional
primitive-order proofs, but inspected sources do not resolve this sort4 domain.
No new proof coverage; no std/contract/proof/verifier/workflow change.

Historical runner limitation documented in the review: run-rapx-applicability.sh
calls classifier tests without required --evidence-dir; the corrected processor
is fixed to six original-source cases. Not repaired/run; any separately resumed
runner needs a fresh preparation/interface review. Saved-data NO-GO remains valid.

## Historical automatic replay — CLOSED / NO-GO

**CLOSED — automatic processing reproduced gate-A NO-GO.**
Owner explicitly authorizes classifier/tests/docs and a minimal manual hosted
replay mode from expected/actual HEAD3e628c6a2d1197c069abf46fba33b3453c2de57f.
Entry tree clean, correct fork/branch/local/remote HEAD, no newer/unrelated changes
or active Actions. Budget1/2 NEW replay runs, at most30min each, one active.
Input fixed to run37508888778/source929ea803ffff1c4f534716cc8c37bbbfa06a5960,
artifact11434810024/archive SHA256
d9c5300fd4ac5c6267a8516e33ff4a8ba713795dc9e393e6eff3d8f2a71edf38.
Archive downloaded read-only and SHA verified locally; no local executable tests.
Preserve original logs/JSON/manual result; new outputs identify processor SHA.
Authentic paired-log replay and corrupted variants ran hosted. No RAPx
installation/build/verification, B/C, semantic changes or new sort4 proof.
Completed [run37513897141](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37513897141),
exact processor1c0b5171375c1198ef0e94b6a26d5e3a13cf1a15, replay/30min,
job18:46:45–18:46:57UTC SUCCESS; verification/bootstrap job SKIPPED.
Hosted tests9/9 groups PASS, all six pairs parsed. Two PROVED_VALID, two ZST
SOUND_MISS, two INTENDED_ALIGN_DETECTION_WITH_OTHER_UNPROVED (other Failed/
Unknown retained). Aggregate commands_succeeded=true, evidence_parsed=true,
gate_outcome=NO-GO;43 Proved/3 Failed/2 Unknown. Original JSONs preserved
byte-identically under historical output. New artifact11436755991 identifies
both original source/artifact and corrected processor SHA; full hashes/results
in [report](RAPX-APPLICABILITY-RESULTS.md).
STOP at1/2 replay runs; no active run or unfinished proof draft. Documentation
closeout only, no further dispatch/B/C/semantic tool change/new verification.

## Historical semantic continuation — CLOSED / NO-GO

**CLOSED — NO-GO for stock RAPx 0.7.50 / nightly-2026-02-05, gate A.**
The owner explicitly resumed at `1fc89566800f8152d218de7f9a757f665626f220`.
Entry tree clean, local and remote HEAD match, origin points to the fork, no
queued/in-progress Actions. No newer or unrelated changes at entry.
Separate budget: **2/4 NEW hosted runs**, at most 90 minutes each including
setup, one active run at a time. Ordinary runner/setup/classifier repairs were
authorized autonomously within this budget; the prior one-correction limit was
superseded for this completed continuation. Historical two runs remain below,
outside the new budget.

Mandatory checksum-metadata dependency removed; archive/VCS/version/lock and
full installed-source identity audit PASS. Contract printing separated from
actual verification, which omits debug-contracts. Negative fixtures never ran
as ordinary programs; only the layout binary executed on hosted Actions.
Completed
[run37508216376](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37508216376),
exact source `cbbbb430d0091191141819843b3c8b476d0ff9f6`, created18:02:30UTC,
A/90min, FAILURE at classifier synthetic-log test11/12; full source identity
audit PASS, layout/preparation/all six A controls NOT RUN.
Synthetic row deletions corrected without changing the classifier. Completed
[run37508888778](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37508888778),
source `929ea803ffff1c4f534716cc8c37bbbfa06a5960`, A/90min, job18:07:43–18:10:57UTC.
Commands SUCCESS; classifier tests12/12, all six actual functions analyzed,
one copy checkpoint/path and eight primitive records each (48 total).
Both ZST negatives get SOUND and violated Align(src/dst) ProvedByRule despite
retained byte-offset1 and hosted size0/align8. Valid ZST/u64 controls SOUND;
u64 negatives fail intended Align but retain distinct ValidPtr Unknowns.
Exact paired contracts/DefIds/checkpoints/properties and optimized MIR manually
audited. This is a reproduced critical detector miss, not a std runtime bug.

Automatic classifier remains fail-closed/unmapped for all six actual logs:
real renderer omits crate prefix, prints std::ptr callee, and expands ValidPtr
to eight checks. Synthetic tests did not validate those forms. Raw JSONs are
preserved, not promoted to successes; report distinguishes manual verdicts.
No further classifier/tool change or dispatch after the confirmed miss.

STOP: substantive A result obtained at2/4 NEW runs; no active run or proof draft.
B/C NOT RUN and remain unauthorized; unused budget does not reopen the route.
Report/log/coverage/index updated. Any future parser replay, verifier change or
different route requires a separate decision. No RAPx patch/upgrade, std change,
contract weakening, full-sort4 proof or external publication authorized.

## Historical preceding session — CLOSED / INCONCLUSIVE

**CLOSED — INCONCLUSIVE, gate A stopped at setup. No active run.**
Owner resumed from documentation `ad54f67d655c4106762016fba47534c58601f3ec`.
Tree clean at entry, origin/branch verified; no unrelated changes or active runs.
Six isolated alignment fixtures and manual workflow selection are committed.
All compilation/executable diagnostics used GitHub-hosted Actions only.

Frozen profile RAPx '=0.7.50' --locked / nightly-2026-02-05 retained.
Package archive SHA/VCS match reviewed 7d61d937; second run verifies both
executable versions and captures binary hashes. Hosted installed-source
comparison did NOT complete; do not claim full profile audit or detector result.

- [run37492790456](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37492790456),
  source `b55ae850d1cef67ddbcd02d8d97b4763c9c4a9f1`, A/90min, FAILURE,
  16:04:37–16:08:18 UTC: runner incorrectly queries direct driver version via
  argv instead of RAPXFLAGS; setup exit 2 after successful package install.
- [run37493697524](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37493697524),
  source `772def3ce7e5e3585ac0c9a909f97afbcdb9a821`, A/90min, FAILURE,
  16:11:22–16:18:02 UTC: single shared correction fixed version query; runner
  then requires absent Cargo registry `.cargo-checksum.json`, setup exit 1.
  No installed-source comparison, layout, preparation, MIR or fixture analysis.

Used **2/4**, planned A plus shared technical correction. Remaining planned
B/C slots cannot be repurposed as further A retries. All six A controls, B/C,
SOUND/UNSOUND/Unknown obligations and generic coverage: **NOT RUN**.
Full logs/artifacts inspected; two preparation failures preserved. ZST
alignment shortcut remains a source-level concern, not a reproduced miss.
No verifier/contract/std semantic change or downgrade/upgrade was made.
Direct branch dispatch worked; no default-branch update was needed.

Stop at the phase boundary. A further narrow preparation-and-A retry needs a
new owner decision; proposal in the results, not applied. Full sort4 proof,
verifier development, later phases and external publication remain unauthorized.
At that checkpoint, contract admissibility was unresolved; the later owner
decision above adopts an explicit research domain. Earlier phases stay CLOSED.
No active run, uncommitted proof draft or new proof claim.

## Completed no-patch review

Official26.10 release `f76012fb518703b1d98e243ac4f487f16877cfcb`, Linux artifact
SHA256 `5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd`
(release API digest), nightly-2026-09-25. Source comparison with pinned26.09
`809de4596839b739dd999f9e462242c835e3af46` confirms opaque tuple2 ownership,
HRTB empty-bound filter, immediate Continue unwinding return and initialized-typed
dst copy precondition persist. New trait-name canonicalization and mutable-slice
contract generation do not close those obligations. Exact target export/refinement
on26.10 NOT RUN; no claim of incompatibility or generic sort4 failure.

Normal recover_pair technique remains useful but lacks FnMut/direct panic.
Kani is the one detailed integrated alternative: exact-body concrete evidence,
monomorphized type/callback domain and measured UB instrumentation gaps; no
unrestricted safety route established. Full matrix, immutable sources, profiles,
observed/inferred/unknown distinctions and no-run rationale are in the assessment.
No conclusion that every no-patch route is impossible. Generic coverage unchanged.

That closeout recommended a contract/admissibility review. The subsequent owner
decision selects the separate RAPx applicability task above; it does not answer
the contract question or select verifier development. Latest proof run remains
37466906281 below; the screening and READY checkpoint add no verification result.

## Completed contract diagnostics and architecture review

[Closeout and hashes](SORT4-CONTRACT-RESULTS.md), [full research contract](SORT4-CONTRACT.md),
[selected architecture/gate](SORT4-SAFETY-DECISION.md).
Final [run37466906281](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37466906281)
SUCCESS, proof source `7f96aa2f3262cf209ff3dcafd06e355e5590885b`,
`sort4_contract_diagnostics`/90min,12:56:09–13:06:10UTC:

- Unchanged values control0/267failed,12/12covers.
- Coincident [0,1,2,3]: raw1, ONLY actual memcpy src/dst overlap at ptr/mod.rs555:14;
  first0→0 copy is UB boundary, no output claim after it.
- Shifted [0,4)→[1,5): raw1, ONLY explicit original-multiset assertion at
  injected smallsort.rs1192:9; default memory/trace/sorted checks pass/unreachable.
- Independent witness0/130failed,1/1cover: dst[0,0,0,0] from snapshot[0,1,2,3].
  Individually disjoint copies overwrite later sources; NOT an UB finding.
- All4 classifications and44 malformed/nonmatching rejection cases pass.
  Source/pin/byte audits pass; std blob remains e555fce440872898e47fd5114f32eb15401d07df.

Prior37464581019 failed at harness memcmp unwind6 before shifted posts;
37465676476 reached the intended multiset assertion but classifier rejected
Kani's formatted-panic placeholder. Both failures preserved; element-wise
comparison and static kani::assert label corrected them without weakening posts
or checks. Each correction got a NEW source/run. Final suite363.05s; job601s,
common preparation227s; all3 jobs1424s, no budget bottleneck. Default pinned
Kani152c6a8c/Rustnightly-2026-02-05 profile unchanged; stronger UB checks NOT RUN.

Contract now specifies local copy vs cross-copy preservation, raw initialized/
uninitialized scratch and prior resources, one ownership sequence, current
callback effects and all5 panic posts; maps real len>=8/16 separated callers.
This is static proposed contract/caller analysis, not generic proof or accepted
public contract strengthening. Existing values/tagged functionality preserved.

Historical architecture proposal: separately reviewed explicit normal/direct-Continue
recovery with a checked helper; first bounded c1-only full-normal/full-unwind mechanism gate.
Historical tuple/HRTB/strict-cut capabilities are dependencies, not sufficient:
strict-cut earlier unwind returns debt and changes kernel+translator. New recovery
routing is missing. Whole-sort4 also needs uninitialized-dst copy semantics,
actual selection helper proof, five-call sharing, ZST/provenance/padding and
scratch-access/ownership transport. No patch changed/applied or VF run performed.

## Completed sort4 functional phase

[SORT4-PHASE.md](SORT4-PHASE.md) remains closed. Its results are retained in
[the closeout](SORT4-RESULTS.md), [contract/caller audit](SORT4-CONTRACT.md)
and [generic-safety assessment](SORT4-SAFETY-DECISION.md).
The actual std blob stays `e555fce440872898e47fd5114f32eb15401d07df`.
Harness/runner source is `1bc9cb718efc07315082334cded2d2362ecbbde1`;
[run 37459631500](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37459631500)
completed SUCCESS (sort4_functional/90min; 11:55:16–11:59:55 UTC).
Values: 0/267 failed, 12/12 covers; tagged stability: 0/233 failed, 6/6 covers.
Full logs/artifacts/source/tool hashes were inspected. Workflow-only exposure
was 26a43be on research / 3d8c8c0 on main.

Both actual-body functional theorems are established for their concrete
types, separate initialized buffers and pure nonpanicking comparison.
Generic safety remains open. The phase found no new falsifiable route through
unchanged VeriFast and ran no generic diagnostic; that was a static feasibility
decision, not an executed generic failure. The completed contract follow-up above records the overlap observations and
explicit ownership/architecture proposal without proving generic safety.

## Earlier insertion/ManuallyDrop phase remains closed

The ManuallyDrop/insert_tail feasibility phase reached NO-GO for integration.
The subsequent sort4 phases preserve that stop. Neither the completed
functional proof nor the new contract phase reopens insertion callback
integration, patch expansion or full insertion work.

The actual conditional `recover_single` body verifies through return and
leak-check (16 records), and five independent baseline controls pass. Both
ManuallyDrop callers still stop before the reference/helper call: immutable
tmp offers half storage where full borrow construction needs a whole cell.
Original RawPtr refinement failure and the draft's unproved child-pointer
permission bridge remain. The missing-init negative was not reached.
Source-exact first false return and direct panic recovery remain unestablished.
See the [preserved closeout and historical profile](PREPARED-PHASE-2026-10-06.md).

## Established milestones — not Challenge 8 completion

| Evidence | What passed | Boundary |
| --- | --- | --- |
| [37383583285](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37383583285) / Kani | Two actual swap harnesses, 5/5 covers | Four i32 cells, fixed positions 1/2; not generic safety |
| [37389298278](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37389298278) / Kani | Insertion adapter, research summary caller and direct actual outer function, 15/15 covers | Lengths/offsets 1..4, sorted prefix, unwind 6; not arbitrary-length modular proof |
| [37459631500](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37459631500) / Kani | Actual sort4 sorted exact i32 multiset and separate tagged-item stability;18/18 covers | Complete four-element arity, full i32 range; fixed disjoint buffers, pure nonpanicking `<`, concrete Copy layouts; generic safety open |
| [37401540878](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37401540878) / unchanged VeriFast 26.09 | Actual unrestricted generic size helper, exact size_of(T)<=8 on LP64 | Isolated function; dispatch callers/full-core integration open |
| [37419989766](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37419989766) / experimental patched VeriFast | Actual generic CopyOnDrop::drop body, exact destination and ONE ownership sequence | Conditional source/destination resources, arbitrary valid len; not insertion |
| [37435525052](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37435525052) / experimental patched VeriFast | Actual Drop plus two one-cell callers (normal and FnMut() normal/unwind); 25 controls and 7 intended negatives | Local cleanup gate completed; not held &T provenance or actual insert_tail |
| [37437514808](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37437514808) / unchanged VeriFast 26.09 | i32 and unrestricted T two-cell sharing/recovery, checked helper/callers, full current cells/T.own; 3 intended negatives | Natural Rust block, normal path only; no callback, panic, ManuallyDrop or std insertion |

Only the size helper has an isolated generic proof among the seven required
safety targets. The other six and all three sorting contracts remain incomplete.
See [coverage](coverage.md); do not equate a microfixture or patched-tool success
with whole-function proof, verifier soundness or upstream acceptance.

## Previous recovery evidence and preserved draft

- Diagnostic [37448257248](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37448257248),
  source f0f417ce9913f53a90591c89593b31b359b87032, minimal profile/90min:
  completed/failure. Actual recover_single body passes; five baseline controls
  pass. Both MD callers fail full borrow construction with missing points_to<T>
  at tmp_addr before reference/helper call. Positive refinement still rejects
  original RawPtr. All seven exports/decodes, six refinements, exact source/tool
  audits pass. No full lifecycle or intended missing-init negative established.
- Unchanged-release baseline
  [37448682524](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37448682524),
  same source, verifast_borrow_recovery/90min: completed/success; both positives,
  three intended negatives, all five refinement/export/decode checks pass.
- Historical37441463201 remains evidence of the prior common-helper failure.
  Its new helper failure is superseded, its caller/pointer gate was never green.

[DRAFT-MD-RECOVERY-2026-10-06.patch](DRAFT-MD-RECOVERY-2026-10-06.patch) remains
UNAPPLIED and UNVERIFIED. Review rejected its absolute/relative fraction mixup
and unsupported permission transfer to a saved shared-reference-derived pointer.
Only independently designed access packaging was implemented. See experiment
log for exact costs, hashes, diagnostics and case counts.

## Next permitted action and stop boundary

Phase closed at the concrete ZST model boundary after1/3 NEW runs,38s summed jobs.
No active experiment, no further implementation/dispatch. Recommended next decision:
review minimum faithful Rust ZST size/repr-alignment encoding and its trust/admissibility
requirements versus another independent layout component. An unchanged-tool residual
index proof diagnostic is separately proposed NOT RUN / NOT AUTHORIZED in the results.
No patch, new axiom, ZST exclusion, B/C, full sort4 or external publication authorized.
