# Challenge 8: current status

Updated 2026-10-06: recorded the owner-approved
[remaining-tools screening](ALTERNATIVE-TOOLS-ASSESSMENT.md) and prepared the
[RAPx applicability phase](RAPX-APPLICABILITY-PHASE.md) for the next agent.
Documentation entry HEAD `b7416c18035c714258e2a476eebdfa1609f7f66c`, fork
`Tiramisu-Cake/verify-rust-std`, branch `challenge-8/research`.
This is the single current checkpoint; procedures in
[AGENT-RUNBOOK.md](AGENT-RUNBOOK.md), priorities in [PLAN.md](PLAN.md),
history in [EXPERIMENT-LOG.md](EXPERIMENT-LOG.md).

## Authorization and execution state

**IN PROGRESS — RAPx applicability and detector coverage, gate A.**
The owner accepted the selection of RAPx and requested documentation plus the
next agent prompt. A continuation agent may begin only the bounded
[named phase](RAPX-APPLICABILITY-PHASE.md) without repeating approval: A, ZST and
ordinary alignment; B, generic/raw-memory coverage; C, comparator effects and
normal/direct-panic behavior. Advance only after the previous gate passes.

Frozen profile: RAPx exactly 0.7.50, Rust nightly-2026-02-05; reviewed upstream
source `7d61d9377033c48a4df8954f34cc076e97a93816`. Audit the installed package;
no patch, semantic model change or upgrade. Maximum four hosted runs (one per
reached gate plus one shared technical correction), 90 minutes each including
setup, one active run at a time. Used **0/4**. Session resumed by the owner on 2026-10-06 at documentation
commit `ad54f67d655c4106762016fba47534c58601f3ec`. Working tree clean,
origin verified, research branch fast-forwarded to that commit; no queued or
in-progress Actions. Preparing isolated gate-A diagnostics; no active run.

The ZST alignment rule and unsupported-call fallback are source-level concerns,
not reproduced false passes. A critical miss or essential unsupported behavior
stops this route; even success stops at an owner decision before a full proof.
The public-contract admissibility question remains separate and unresolved.
Earlier phases stay CLOSED, including no-patch feasibility (0/2 runs used).
The patched proposal in SORT4-SAFETY-DECISION, later sorting phases and external
publication remain unauthorized. This update changes documentation only.

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

Read the screening and RAPx phase, inspect actual branch/run state, record
IN PROGRESS and the gate-A experiment card, then implement and run only that
bounded diagnostic on GitHub-hosted Actions. Follow the phase's ordered gates,
profile and budget; no local builds/tests and no automatic tool upgrade.
Write RAPX-APPLICABILITY-RESULTS.md and checkpoint NO-GO, INCONCLUSIVE or READY
FOR NEXT DECISION with exact evidence. Stop there; fixture success is not a
generic sort4 proof, and a model gap does not authorize a verifier patch.
