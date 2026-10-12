# B2: actual `insert_tail` three-cell causal diagnostic

**Status: PREPARED, NOT RUN, NO PROOF CREDIT.** Policy revision read:
`6e1a8e59c56669abe5e6ec2013478e45ed2cc267`. Authorized session №2
starts 2026-10-11 21:36:26 UTC, main cutoff 23:36:26 UTC and finish-only cutoff
2026-10-12 00:06:26 UTC. B1 qualification and transport repair precede B2. This
card does not dispatch a Build or transfer a B1 result to B2.

The actual obligation is SmallSort's `insert_tail` at lines 536–570; its
consumer is the insertion loop in `insertion_sort_shift_left` at line 596 and
the two scratch-half loops in `small_sort_general_with_scratch` at line 274.
The Cloud fixture pins full original `insert_tail` and `CopyOnDrop` blocks from
SmallSort blob `40939f922bcb6fdc7ee0d30427fa861827043827` and source SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`.
Static read/hash of the current assigned source confirms the exact Drop block
SHA-256 `caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a`
(364 bytes, lines 295–310) and full insertion block SHA-256
`9bc00f3913373e5879769b9970d66b1a56ada05a10205d51cafdf6533ecc2f29`
(1380 bytes, lines 536–571). The hosted preparation rejects a hash, byte
count or ordered runtime-anchor mismatch before executing any proof stage.
It mechanically substitutes `T=u64` in every runtime statement and the guard
type while retaining generic `F`, `FnMut` calls, `self.len`, and both normal and
cleanup Drop edges. Paired original/verified inputs differ by checked proof
annotations only; ghost stripping must reproduce every runtime byte. This is a
concrete specialization diagnostic, not generic `insert_tail` verification.

`b2_three_from_local` creates `[10_u64, 20, 5]` in its own stack allocation,
derives `begin` and `tail=begin+2`, and passes its genuine `&mut F`. Its sole
external resource precondition is the canonical `&mut F` comparator state
`*is_less |-> f0 &*& <F>.own(t,f0)`, with thread/type resources. This is the
caller's legitimate input obligation, not a guard/receiver premise; a later
actual outer caller must establish this `F` borrow and get its current state
back on both outcomes. The actual callee's precondition is its three initialized cells,
one current `<u64>.own` for each, and the comparator state; the wrapper must
establish it from the local initializer. No receiver, guard FBC, origin,
borrow-end token, current-gap premise, or source/destination permission is
supplied to either function. The complete target normal **and** unwind posts
restore all three initialized cells with one owner per current value, current
`F` state, thread/type resources and caller frame. They do not claim that a
callback preserves entry values. The wrapper's normal/unwind F post and leak
check must also pass; a final proof requires checking the array at its call
boundary and local cleanup, not merely a green callee.

For the intended witness, the first callback may return true. `tail.read()`
moves the sole logical owner of `5` into `tmp`, leaving a logical gap at index
2. `copy_nonoverlapping(sift, gap_guard.dst, 1)` copies `20` into that gap;
the actual assignment `gap_guard.dst=sift` moves the logical gap to index 1.
The late `is_less(&tmp,&*sift)` can then unwind. Before the real cleanup
`Drop`, both callback reference loans and current `F` state must be recovered;
the checked generated glue/selected method copies the **current** held value
into the updated gap. The normal second-false path fills index 1; second-true
shifts `10` and fills index 0. The first comparison's early false return and
direct panic must also satisfy the full posts, without a guard. No sorting or
snapshot/permutation claim is made from arbitrary callback answers/effects.

## Falsifiable first experiment

The new `actual-insert-tail-b2.py` is an inert hosted `execute_case` hook. On
the exact experimental profile `experimental-merge-actual-glue-body-v8`, which
is **not accepted for integration**, a
single case prepares the full bodies and posts, runs exporter/decode/official
refinement/VeriFast through the existing merge lane, stores source and stage
receipts, and records the first exact error. It never classifies an early
setup, frontend, resource, dead-code, or refinement failure as an intended
negative or proof success. The first predicted causal refusal is the actual
`tail.sub(1)` at SmallSort line 540: a three-cell array resource may still
need an explicit checked interior `pointer_within_limits` derivation. This
matches an older generic-source observation and is a hypothesis for the new
concrete profile, not transferred proof evidence. If that bound is discharged,
the next expected refusal is the first comparator's genuine reference loans
at line 541; later refusals would identify moving-gap or cleanup resources. A late-Call refusal would identify the next
needed lowering rule. The current script deliberately adds **no** callback
marker: the existing marker protocol is inapplicable to this exact CFG. A
full positive needs reached first/late calls, two shifts or justified loop
invariant, normal and late-panic cleanup, actual selected Drop/glue body,
all full posts, return/free/leak/dead-code, and an exact paired MIR/AST and
source-refinement certificate.

Prior MIR evidence in `INSERTION-RESOURCE-LEDGER.md` is dated and must be
re-observed for this input. It maps first callback `bb1` to direct Continue;
late callback `bb13` to cleanup `bb20`, which Drops the guard and reaches
`bb21` UnwindResume. The existing cleanup translator admits only a single
generic-`T` two-source `FnMut` call with `UnwindAction::Continue` and a strict
ghost marker sequence. Its global synthetic unwind epilogue would skip the
real guard Drop if applied to the late Call. Thus the fixture currently can
provide a causal failure, **not** a logically complete proof annotation.
The required next semantic card must qualify this exact late Cleanup edge,
return both temporary reference loans and current `F` before guard Drop,
preserve the real cleanup successor and original UnwindResume, and prove
normal/cleanup current resources without creating a second owner. The first
comparison needs its separate full-return recovery. This is within the
owner's narrow exporter/lowering/refiner/receiver-Drop authority only after
its own before-implementation card and regression design; kernel, memory,
alias, generic `T`, ZST and source runtime changes remain outside scope.

The official refinement checker currently follows only normal targets of
`Call` and `Drop` (`refinement_checker.ml` near 2595 and 2607, both TODOs).
Before any B2 panic proof claim, the qualified actual caller must compare
original and verified unwind action and cleanup graph, with mutations that
remove or redirect the late Call cleanup and guard Drop rejected at the exact
refinement obligation. Ordinary normal/unwind smoke does not close this.

Expected controls after the first causal result: a reached false assertion
after the first `dst` update; missing callback loan fraction/token at its
real close/end predicate; missing moving-gap destination permission at the
actual selected Drop precondition; and late cleanup-edge mutants at official
refinement. Each needs its own exact stage, predicate and location oracle
calibrated from raw Cloud evidence. Until then every control is NOT_RUN and
the v8/B2 profile remains NOT_ACCEPTED/NOT_FOR_INTEGRATION. A full source,
proof, or tool change requires a fresh exact-SHA Build; saved replay changes
only classification of unchanged artifacts.

## Session №3: first two shared-reference resources (authorized 2026-10-12)

T0 **2026-10-12T00:19:22Z**; main **01:19:22Z**, absolute **01:49:22Z**. Last30min only finish started step/evidence/account/checkpoint. Exactlyone newBuild, timeout<=900s plus60s queue, separate960Cloud seconds. Stableownermerge/reviewedmergelane, installedv3/max3/oneperowner unchanged. Policy6e1a8e59c56669abe5e6ec2013478e45ed2cc267 and adoptionACK1e65f562994220a909ccf97903c36cb054576b76 confirmed. Profile/tool remain exactly v8/a158398e336edce9817f62a55733a3470a986d7b/profileSHA0e67b038f940a9892dcb840747fbcc340532a31649979601af545acc41a0c68b, EXPERIMENTAL/NOT_ACCEPTED/NOT_FOR_INTEGRATION. Previousunused1564retired; no carryover.

**Falsifiable hypothesis:** both first references (`sift=begin+1`, `tail=begin+2`) can derive precreation **and** initialized/shared access from the original three-cell array and its sole owners using the existing full-borrow/lifetime/share interface. This supersedes the old conditional pointer-bounds-first prediction for Build7f45c598: tail.sub(1) already executed there. No comparator restrictions or receiver/FBC/origin/end-token/gap/ownership entry assumptions added. Domain remains concreteu64/threecells/genericF; full original body and full normal/unwind target posts retained verbatim. All current cell owners, F/thread/type and caller frame must survive/reassemble.

Concrete applicability review: historical `extract-verifast-insertion.py` RANGE_COMPARE_PREP is specialized at n=3,T=u64; its old diagnostic posts are not copied. Split two singleton cells and corresponding foreach owners, close FBC, borrow/share, precreate and init_ref_share both references, open genuine tracked initialization access fractions and package actual reference tuple. On normal false-return and true-continuation attempt close both accesses, end lexical lifetime/full borrows and rejoin array/owners before actual subsequent runtime. Full first Continue-unwind restoration remains an explicit target; no new callback or cleanup semantics/markers are implemented. Exactu64FnMut HRTB registration was0; if loans pass and call admission/recovery fails, preserve that first causal blocker and stop. Call→cleanup Drop→Resume remains separately open; refiner0/nodes give no qualification.

**Controls/oracles:** preserve the existing same-campaign B1 positive, six proof negatives, ten official admission (originalnine plus wrongkeybinding), four receiver/end/retirement controls, helperfour, mandatory retainedsix and exactcombined ordinarynormal/unwind regressions. Existing predicates/locations remain encoded in their source-bound classifiers. A negative counts only at its exact configured stage/obligation, never setup/unsupported/dead-code substitution. First actual target positive must pass both create_ref requirements then genuine first FnMut call, and restore both normal/firstContinue-unwind resources; statementreach alone is insufficient. No new B2 cleanupnegative is claimed before its prerequisite execution.

**Outcome mapping:** fullfirstcallback normal/unwind recovery→partialprogress only, report next causal obligation in completebody; create_ref refusal→hypothesis not discharged, exact resourceerror retained; HRTB/callback/cleanupsemanticfrontier→reproducibleblocker with frozenprofile, no semantics expansion; setup/refinementfailure→INCONCLUSIVE, no resourcecredit. AfteroneBuild inspect fullarchive/inventories/receipts/rawlogs, then closewindow; any classifiercorrection savedreplay only, preserving oldverdict. B2 requires full PROGRESS-REVIEW criterion and index15% staysunchanged.

**Pre-dispatch identities:** actualSmallSort full85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1/blob40939f922bcb6fdc7ee0d30427fa861827043827, Dropcaff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a, fullinsert9bc00f3913373e5879769b9970d66b1a56ada05a10205d51cafdf6533ecc2f29. Baseline exactsource/ghoststrip/MIR/AST are saved from Build7f45c598/proof=infra958afc34558419a37626b04b57610e220e7f4c03; identities below are historical, not newproof. Fresh verifiedsource/ghoststrip and MIR/AST identities must be retained by the Cloud stage receipts before interpretation; compiling/extraction locally is forbidden.

```json
{
  "original/lib.rs": "d5a1f33a06115a3a23918afe054191227ca29d990fb199147d23ec4f6531bc26",
  "verified/lib.rs": "3ccf7783833f937889c04d549c70d0369a610bc4114760392ff89239144cbdef",
  "original-compiler-mir.bin": "65956454c89b1d0fccece0ff018372adfab75d50d08030bcb59632d3977d675f",
  "compiler-mir.bin": "14dc2bdc3d85c41d644375e722e084e862cd2e8607282070039a97783183f997",
  "original-decode.out": "564bc866378c3b15ea18ff68edfb665c1658defe25503eda2d9025cd00a14286",
  "decode.out": "e20974bdb8b8082a0960ebd2accdd0c3fe285d19484c219e45c30fd01badef2d",
  "proof-ast.ml": "4af36e7ee577a499533fac7ba643b17985c517e843e88f14dc4e7ab2fe6aed76",
  "verifast.log": "ea10c38c633c98386e64d93cc88816092cecf2e4f7ce6edaabec75ca02487ca7"
}
```

Fresh planned byte identities (static insertion into unchanged saved baseline; no local extraction/compiler/proof execution):

```json
{
  "check": "SAVED_BYTE_STATIC_ONLY_NOT_PROOF_NOT_EXTRACTION",
  "verified_sha256": "7501d1b03a53252929e1776c36acc33587c3cf6f60ee9c90e532ed3f55d31fc9",
  "unchanged_prior_verified_sha256": "3ccf7783833f937889c04d549c70d0369a610bc4114760392ff89239144cbdef",
  "new_annotations_strip_to_prior_verified": true,
  "annotation_sha256": "0778ce459efa5f057063c2bda3605d5218fbb875aa389cf0da56ca8b0e6ec2e1",
  "normal_unwind_post_sha256": "778eeee10b9fa0a1fa66194f0035cffb5c40916189216c38275b5c43b9093d49",
  "source_script_sha256": "97d05c5ee21d607ad7d99f0d6c07b398eca71c2f0a7940c9fab543320ee2ec41"
}
```

## Session №3 closed — shared-reference prefix advanced, full callback recovery blocked

T0 2026-10-12T00:19:22Z; main01:19:22Z, absolute01:49:22Z. Build finished00:48:04Z within originalwindow. Completion resumed08:38:07Z under latestowner20min allowance through08:58:07Z; no newproof/experiment/Build afterresumption. Closedaccount 2026-10-12T08:49:31.967055Z. Original deadlines/identities remain preserved. Policy6e1a8e59c56669abe5e6ec2013478e45ed2cc267, existingadoption1e65f562994220a909ccf97903c36cb054576b76 ACK confirmed.

**Reference blocker removed for both actual references.** From originalthree-cell array/foreachowners, proof derives two fullborrows/shares, both precreationtokens and both genuine ref_initialized accessfractions. Fresh trace executes all annotations then both actual&*tail/&*sift calls and firstactualFnMut at verified/lib.rs(185,13-77). This proves the reached prefix only; lifetime/borrow/resource roundtrip is not proved. No receiver/FBC/origin/end-token/gap premises or comparatorrestriction was added; completebody and fullnormal/unwindposts remain.

**First subsequent causal blocker:** `verified/lib.rs(130,16-19): No matching heap chunks: array<u64>(begin, 3, _)` in full `on_unwind_ens`. Firstactualcall's AST unwindbranch goes directly to `ReturnStmt(unwinding)` with no callbackloan/lifetime recovery. Neither earlynormal-return recovery186–208 nor normalcontinuation211–233 executed; unwind restoration failed and currentF/thread/type/frame/fullpost credit is absent. Bothcallbacklogs retain `MERGE_HRTB_CALL registered=0 … eligible_bounds=0`; callreached underfallback does notqualify concreteu64HRTB output. No newcallback/cleanupsemantics implemented. Latecallback256/read240/guard241/updatedgap248 notexecuted. Officialrefiner0 doesnotqualify Call→cleanupDrop→Resume; MIR/AST unwind gates remainunadmitted.

**B1 regression PASS in its previous boundednormal domain**, with freshfivecompilerstages0; actualcaller→generatedglue→checkedcanonicalDrop, fullCURRENTnormal/return/free/leak; sixproofnegatives, tenadmission, fourreceiver/end/retirement, compatibility/helpers/mandatoryretainedsix/exactcombinedordinarynormalunwind gatesmatched. Necessary65rawlogs read in full. Originalmissingkey earliercardinality refusal retained; wrongkeybinding matches intendedbindingstage. No transfer to unrestricted std or profileacceptance. **B2 NOTACHIEVED** byfullPROGRESS-REVIEW criterion; index15% unchanged.

Build **30bce9a0-29e8-4535-9060-ee6d9df2dccc**, rawFAILURE, proof=infra **9e15014b5c62f94eb797e044d1f4ca9bd8cb74f1**. Tool **a158398e336edce9817f62a55733a3470a986d7b**, profile **0e67b038f940a9892dcb840747fbcc340532a31649979601af545acc41a0c68b**, EXPERIMENTAL/NOT_ACCEPTED/NOT_FOR_INTEGRATION unchanged. Originalsource d5a1f33a06115a3a23918afe054191227ca29d990fb199147d23ec4f6531bc26 / verified7501d1b03a53252929e1776c36acc33587c3cf6f60ee9c90e532ed3f55d31fc9; ghoststrip exact, fullposts hash778eeee10b9fa0a1fa66194f0035cffb5c40916189216c38275b5c43b9093d49. Artifactidentities and source/stagereceipts in [compactresult](SHARED-REF-SESSION3-RESULT.json). Log2bd6af00d485cba410ab51542fae7f80c99d6cd202d5fd6d4b1bc8f1ac48bce9; archive8adafda11fba216005943f9aa5709ae7b3ce55c97e74a900f34105a956b3e98b. Fullarchive/inventory/config/source-input/uploadreceipt/index/alltextchunks integrityverified; previousverdicts unchanged, noclassifier replay or secondBuild.

Account CLOSED **543/960 seconds**, **417 unused retired**, previous1564 retired/no carryover. OneBuild terminal/accounted/downloadverified. Ownactive/reservation/unresolved/request none afterinstalledclient reconciliation/withdrawal; coordinatorv3/max3 unchanged, no manualforeignmutations. Source/toolworktrees preserved; onlyownprojectbranchpublication. NoActions/merge/upstream/externalmessages. Newsessionnotautomaticallyopened. Nextrequiresseparateownerdecision onconcreteu64HRTB and firstContinue-unwind callbackresource recovery; iftrustedsemantics needed, separatecard/profile/admissionregression beforeimplementation.
