# Challenge 8 agent runbook

## Mission and working context

Build our own automated proof of the actual Rust SmallSort implementation.
The owner's mathematical background supports precise specifications; explanations
and progress reports should be in Russian. The existing small experiments are
scaffolding for an eventual submission that meets the full challenge.

- Fork: https://github.com/Tiramisu-Cake/verify-rust-std
- Working branch: challenge-8/research
- Upstream: model-checking/verify-rust-std; tracking issue #56.
- Requirements: doc/src/challenges/0008-smallsort.md and doc/src/general-rules.md.
- Target: library/core/src/slice/sort/shared/smallsort.rs.
- Workflow: .github/workflows/smallsort-research.yml, named SmallSort research.
- Kani pin: tool_config/kani-version.toml; currently
  152c6a8c875d9886a67e229247b4826d6105ccfd (Kani 0.67.0).

Read root AGENTS.md. Its prohibition on server-side builds and verification is
the owner's explicit instruction, not an optional performance recommendation.

## Handoff status — 2026-10-06, Europe/Moscow

Read [the consolidated handoff](HANDOFF-2026-10-06.md) first for established
scope, unresolved obligations, research misdirections and fresh-review priorities.
Older status blocks below preserve historical evidence; their next-action text
does not supersede the current stopped status or the consolidated handoff.

**Resumed at the owner's request — 2026-10-06.** Start-of-session research
HEAD and origin both `301845b167672bb710fe59150f636301ff391dcc`; no active
Actions run, latest completed run remains37423762729. Git/GitHub access works.
Complete the all-path resource ledger/trust-boundary review, then dispatch
the narrowly corrected local-cleanup diagnostic on a new pushed source SHA.
Normal/unwind ownership recovery and the unrestricted generic borrow pilot
remain the next architecture gate; a passing cleanup diagnostic alone does
not establish insertion or authorize further kernel extensions.

**Latest completed run:** [37431775757](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37431775757),
source `197d5a1efdaa1d42e7a69df1a811dbe3ba82648d`, localcaller90min.
Full logs/artifacts inspected. Pinned26.09/prelude/exporter/refiner/pairedZ3,
strict patch/output and four-file audits pass. Console build0/19.00s,
RSS426,608KiB; binary4b56ad0190f36fc8af4da8eb038207d12bff547bbc714368621ffbb8cfcde1d9.
All8HRTB/12scope/5reference regressions pass1.75/2.34/1.36s; compiler/decode0
for all25. Direct actualDrop body0/.13s, refinement0/.10s; exact364byte
source/hash/ghost-strip/MIR audits, named1/copy1 pass. First caller cleanup_one
export/decode0, same-unit Drop named1/copy1/5 copy statements, caller named1;
VF1/.13s after post/free-locals/leak trace ends with whole-function dead code
at38-49 (no error: line), refinement0/.09s. Overall1,runner1:23.62,
RSS626,532KiB, setup dominates. Other8 fixtures NOT executed. No covers/loop
bounds in this deductive gate. No successful whole caller/cleanup gate claimed.
No active run. Next diagnose reachability/CFG bookkeeping without suppressing
dead-code checks, then NEW exact-SHA gate if a justified narrow fix is found.

All-path ledger and architecture review completed in
[INSERTION-RESOURCE-LEDGER.md](INSERTION-RESOURCE-LEDGER.md). Exact saved MIR
has first comparison direct unwind; late comparison cleanup Drop then immediate
UnwindResume. Full first-panic and held-storage recovery remain independent
gates. Nested substs match now explicitly delimited; outer non-ADT fallback
preserved. Patch `e7512da5f6baa2b3fd1af3b01dde01742f6d0028aa0edf68b3f73e01209215bf`,
translator `cfea51db27ba60fd59d8cb9f0a1db3399dcb76106d219127ceb7f50e974c1caa`.
Static pinned-chain apply/hash, diff-check and bash-n pass; runtime std and all
25 regressions/body/9 caller fixtures unchanged. Next NEW exact-SHA
verifast_local_drop_caller_gate90min, then minimal generic borrow/recovery pilot.

**Read-only reassessment — 2026-10-06:** local/remote research HEAD was
`e0ef921e4058404b4944aff4335f79123ed53e61`; latest run and stopped status
confirmed on GitHub. Read [the revised plan](REASSESSMENT-2026-10-06.md) for
the current continuation order: complete the resource ledger and architecture/
trust-boundary review before further semantic verifier changes. The existing
nested-match repair/full local-cleanup gate remains a diagnostic after resumption;
it does not by itself justify the full insertion approach. No new proof code or
Actions experiment in this review. Size-helper37401540878 used the pinned release
binary; generic insertion/Drop used the experimental source-derived chain.

The owner requested a separate durable record for future VeriFast work:
[upstream contribution candidates](VERIFAST-UPSTREAM-CANDIDATES.md).
The first candidate is the independent address-taking traversal fix; the note
records evidence gaps and prerequisites for moving each patch into a separate
project. This documentation task does not resume experiments or publish a PR.

**Latest corrected local-cleanup regression failure:** [37423762729](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37423762729),
source `b3da9a5ef53b8001e63ce511ba27ae8efce67343`, local_drop_caller_gate90min.
Full logs/artifacts inspected. Patchbc13ff90/translator03bf4a5c,
source/tool/prelude/dependency/four-file and pairedZ3 audits pass. Console build
0/19.14s,RSS426,676KiB; binary
b603f7f3ac0963892f88dad3bdafe446707ce04e845b3054c7b087a1480a184e.
First2/8 HRTB cases have intended finite rejections; third hrtb_no_output has
export/decode0 but VF2 with uncaught Pattern matching failed at translator7729
in local_drop_call. Export/decode0 for all3 visited fixtures. Suite1/.69s,
RSS85,400KiB; remaining5HRTB, all12scope/all5reference, extraction, actualDrop/
callers/refinement NOT executed. Overall1,runner1:15.12,RSS646,784KiB,
setupdominates; no new destructor or cleanup proof.
Cause confirmed by source and build Warning11: final `| _ -> None` at7878
is parsed as a redundant branch of nested `match substs`, leaving outer
`match ty.kind` non-exhaustive for non-ADT generic F Drop. No fix applied yet.
Next after resumption: explicitly delimit nested substs match with begin/end,
preserve the outer non-ADT generic fallback, update strict patch/output hashes,
static review, then NEW exactSHA gate with unchanged all25/body/caller checks.

**Latest local-cleanup setup failure:** [37423344712](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37423344712),
source `3a020357cfe5cb6e01eaaf1ef3575dd0abeea00b`,
`verifast_local_drop_caller_gate`,90min, profile `tuple_local_drop`.
Full logs/artifacts inspected. Source/tool/prelude/patch input/output pins,
exact4-source-file audit and dependency/decoder setup pass. Source patch
f8f259e944478c5d23829a2d294def4c79087fb6886df559d9e91ed4146a8739
changes only translator after f8751fab; checked applied result
910a2b79a0761e359a76ac0502251cacc5183b075c556078018be3590ea679b5.
Console build2/12.73s,RSS426,848KiB: translator7740 item.def_id is an unbound
record field because the lookup lambda lacks D.trait_impl_item annotation.
No derived runtime/Z3 audit, regressions, extraction, compiler MIR, actual body,
caller proof or refinement executed. Overall2,runner1:07.68,RSS646,360KiB,
allsetup. No active run. Prepared one-line explicit record-type correction;
static application on pinned f8751fab passes. New patch
bc13ff90cbdc4a937200fb6b20efa2dbb9ceaea0a92d0e428c1fd5b47cc3a65a,
translator03bf4a5c460c1babbd79c80dff7d1c4fc02d21add286498df9bd81fe47796213.
No contract/domain/resource/check change; strict builder/runner pins updated.
Root/Sol review and independent Astra source review found no remaining concrete
blocker after exact late-self lifetime instantiation; projected places retain
the generic baseline as an explicit non-goal. The same-unit actual annotated
method consumes its concrete checked precondition; no own/token/chunk synthesis
or erasure. Method outcomes and Drop unwind CFG successors are preserved.
Luna integration prepares checks for all25 regressions, same-source actualDrop
proof, fractional onecell rawsource/dst normal and FnMut() normal/unwind caller
proofs, and7 negative permission/ownership/unannotated/brokenbody/unsupported
fixtures. The new caller fixtures have not been reached on Actions.
Gate review fixes strict error/header/cleanup/MIR counters and source hash
readback; root and independent Astra review complete. Static AST/YAML/bash-n/
diff checks pass. Fixture pin73cda1789bfb1ab3c1a3ec7a5a85a5ba305019579d5f716b59015f34d8538e30.
Defaultmain exposes the selection by workflow-only commit
5556b0bb2464697190a5467d5ce863402cf989d9; no research code merged there.
Next push corrected research source, dispatch NEW exactSHA localcaller90min and
inspect build/all25/body/caller/negative outcomes; do not rerun the old source.
Actual held_ref release and insertion loop remain open. A possible specialized
onecell actualDrop contract can call existing end_ref_readonly after copy and
merge a supplied complementary origin fraction BEFORE tmpfree; needs separate
checked body/callers. Current actualinsert normal/unwind COMPARISON_DEBT_POST
is a partial diagnostic and unsuitable for a completed normal exit after cut.

**Completed generic destructor body gate:** [37419989766](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37419989766),
source `19e74b59f9f2235c26b208cc3c9a96149e3d6cb5`, copy_on_drop_gate90min.
Full logs/artifacts inspected. Same26.09 source/tool/prelude/pairedZ3/4-file
pins and exact364byte source/ghost/hash/MIR audits pass. Build0/27.85s,
RSS426,932KiB; binary380b990b68b1adf1ec37f5221ee8b1db6d2cf622af435489b1fd57bdf873a410.
All8HRTB guards0/1.73s,12scope cases0/2.30s and5references0/1.37s pass,
everycompiler/decode0. ActualDrop compilerexport/decode0, onebody/onecopy.
Compatibility safety_proof opens ORIGINAL private own=False; afterward ACTUAL
Drop body enters separately, one exact named target and one copy call at32
with5execution records. Exact destination values and ONE foreach(T.own)
normalpost, functiontoken cleanup and leakcheck pass. VF0/.14s,RSS85,732KiB;
refiner0/.10s,RSS84,508KiB;0errors/45total statements INCLUDE generatedsupport,
not45callee statements. ContractSHAd7a090ed7ee9611434d889d7aa84f9e99d4987d9bd33889625c83c985a961e7f.
Originalcrate e9b48887; verifiedcrate793e2fc6; genericT/arbitraryvalidlen,
fractional initializedsrc/fullinitializeddst, no Copy/Freeze/nonZST restriction.
Overall0,runner1:29.65,RSS646,180KiB,setupdominates. No active run.
Directmethod contract is proved; compiler-generated cleanup reuse, heldref
release on normal/panic, loop invariants and fullinsertion remain open.
Next restricted same-unit annotatedDrop lowering with checked exactADT/generic/
impl/field identity, normal/unwind CFG and ordinary storage accounting. Sol
and Astra reviewed architecture; require caller source/dst/ONE Town resources,
never synthesize own, erase tokens or treat defaultown=False as body evidence.
See verifast-drop-diagnostic.md for acceptance and heldref release ordering.

**Latest completed Drop compatibility diagnostic:** [37419467454](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37419467454),
source `e119de8ca9f53685d673f012e1d024e35df14181`, copy_on_drop_gate90min.
Full logs/artifacts inspected. Same source/tool/pairedZ3/originalprelude/4-file
pins and ghost-byte/hash audit pass. Build0/16.44s,RSS426,804KiB; binary
380b990b68b1adf1ec37f5221ee8b1db6d2cf622af435489b1fd57bdf873a410.
All8HRTB0/1.35s,12scope0/1.79s and5reference0/1.09s pass. ExactDrop compiler
export/decode0, one body defPath/one copy call, source hash roundtrip pass.
Refinement0/.07s,RSS84,360KiB. VF1/.10s,RSS85,728KiB BEFORE substantivebody:
function prototype implementation check cannot supply explicit type_interp<T>.
NamedactualDrop0/copyexecution0; generated support lemma records are not a
callee proof. Overall1,runner1:19.97,RSS586,840KiB,setupdominates. No active run.
Prepared explicit safety_proof opens generatedfullBorrow and its ORIGINAL
private own=False to discharge unreachable defaultcaller; concrete req/ens
and mandatory actualbody/copy-line checking unchanged. No assume/new own or
resource removal. Root reviewed delta and staticAST/diff pass. Next NEW hosted
gate source; a successful compatibility check alone is insufficient.

**Latest completed destructor gate setup:** [37419199218](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37419199218),
source `16aa63f8e05e3b38b9e10b5bfa8030cb04149421`, copy_on_drop_gate90min.
Full logs/artifacts inspected. Same pinned26.09 source and4-source-file audit,
pairedZ3/exporter/refiner/originalprelude pass. Build0/18.89s,RSS426,292KiB;
binary380b990b68b1adf1ec37f5221ee8b1db6d2cf622af435489b1fd57bdf873a410.
All8HRTB0/1.71s,12scope0/2.32s and5reference0/1.35s pass; compiler/decode0
for every fixture. Exact364byte genericDrop extraction/ghost-strip/hash audits
pass, contractSHAf98226d6bed50c546c9299823727c5cf8b20cbcb8550f71f29126a1bd206c203.
ActualDrop compilerexport/decode0 and original/verified/std hash roundtrip pass.
MIR has one body defPath plus one trait item defId referencing the same method;
runner's bare name grep incorrectly counts2 and stops. No actualDrop verifier
or refinement executed; no callee proof. Overall1,runner1:21.00,RSS647,204KiB,
setupdominates. No active run. Prepared narrow counter correction: count exact
body defPath, not trait item defId; unchanged contract/source/tools/domain.
Next push and dispatch NEW copy_on_drop_gate90min; inspect actual method proof.

**Latest completed held-reference and first-shift run:** [37417173472](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37417173472),
source `3eb19991b1d8c2312d9feae535b02068335f5162`, manually_drop_ref90min.
Full logs/artifacts inspected. Same26.09/tool/prelude pins, pairedZ3,
exact4sourcefiles, ghost-byte/sourcehash/compilerMIR audits pass. Patch5500204a
on translator15a9 yields f8751fab; consolebuild0/18.86s,RSS426,436KiB;
binaryc76b4255ec5d5d55c011dc2dede8f4e862f80fef7a342980acb23c5c7398161f.
All8HRTB guards0/1.73s and12scope cases0/2.31s pass. All5trackedreference
fixtures pass0/1.37s: scalar exact7 (18records), ManuallyDrop exact7 (30records),
and three intended negative missingprecreate/init/readpermission errors;
everycompiler/decode0. Actual unrestrictedT/F,n>=2: firstFnMutBool/synthetic
unwind and strictcut/recovery pass; tail.read147, heldref148-149, actualguard
creation150, firstcopy_nonoverlapping156 and dst=sift157 pass. On sift==begin159
path compiler cleanup169 needs opaque CopyOnDrop.own at std/lib.rsspec567.
Secondcomparison165, furtherloop/cleanup/restoredrange/fullfunction remain
unproved; initialfalse-comparison return not claimed checked. Named2 includes
errorcontext duplicate,248execution/return records. VF1/.25s,RSS92,704KiB;
refiner0/.15s,RSS91,704KiB;overall1,runner1:22.47,RSS642,920KiB,setupdominates.
No active run. Preparing NEW verifast_copy_on_drop_gate90min: same experimental
sourcebuild tuple_manually_drop_ref and8+12+5fixtures, then exact364byte
CopyOnDrop block with ghost-only directDrop contract on unchangedRustsignature.
GenericT/arbitrarylen, initialized fractional source/full destination, exact
normalcopyvalues and ONE logicalforeach ownershipsequence returned. Sol owns
extractor/spec/doc; Luna owns hostedrunner/manualworkflow choice. No newown
model or cleanup-specializer in this initial gate. Root reviewed contract,
byte audit and log acceptance; static AST/YAML/bash-n/diff checks pass.
Default main exposes manual choice by workflow-only commit9467dd9614af4933ba4634e74e40a60e2cd0594f.
Next push and resolve NEW hosted run at its exact source SHA.
Private localstruct defaultown is False; it cannot simplybeclosed.
Method contract alone must not be treated as replacement for generic compiler
drop_in_place summary; cleanup reuse/restoredrange remain open.
Runtime std hash/domain unchanged; no T/F restriction or assumed own bridge.

**Latest completed address-prepass regression run:** [37415731049](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37415731049),
source `17e96da0c56bd51c587c6023bbedf72bec588583`,address_taken90min.
Full logs/artifacts inspected. Samepins/pairedZ3/ghost-byte/sourcehash/MIRaudit,
exact4sourcefiles check pass. Patch2c44ad1c aftercutbd95733e builds0/18.79s,
RSS426,804KiB; binary1e59705130b70b0b934a980702de1148f5e5b7c265638b449f184b871710740d.
All8HRTB0/1.71s and12scope0/2.30s pass. Scalar address-after-merge fixture
verifies0,oneactualbody18records; ManuallyDrop fixture compiler/decode0 and
passesoldaddresserror but reborrow_ref requires ref_initialized<i32>(tmp_addr).
Suite1/.77s; negativefixture/actualtarget/refiner not reached. named2 includes
errorcontext duplicate, not2verifiedfunctions. Overall1,runner1:20.05,
RSS625,540KiB,setupdominates. No active run; sourceowner investigates sound
reference initialization/ignore-ref-creation path without runtimeedits/checkdisable.
Defaultmainworkflowonly2f0a73b; newprofile reproducer remains.
Prepared next selection verifast_insert_tail_manually_drop_ref/profile
tuple_manually_drop_ref,90min. Narrow translatorpatch5500204a on preceding
translator15a9 tracks immutableShared/Other rawManuallyDrop<T> through
existingcreate_ref; no kernel/aliasmodelaxiom. Existingprecreate_ref and
init_ref_readonly prove actualguardreference fromtmpstorage, with accesskept
untilguardlastread (loop/cleanupdebtunproved). New5physicalfixtures require
positive scalar/ManuallyDrop read proofs; missingprecreate/init/readpermission
mustfailatintendedcontracts. SAME8HRTB+12scope first, exactRust/T/Fdomain.
Root reviewed sourcepatch/integration; NEWhostedrunpending.
Default main exposes selection by workflow-only5b4f35c.

**Latest completed actual borrowing/read milestone:** [37414755368](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37414755368),
source `dc0a359d94f0a79fe41f400d79571199690aca7d`,lft_cut90min.
Full logs/artifacts inspected. Same26.09/tool/prelude pins, pairedZ3,
ghost-byte/sourcehash/MIRaudit pass. Reviewedpatchbd95733e builds0/19.17s,
RSS426,624KiB; binaryd26c815ef4c2d6fe27b4a0580daa52fc4708083b1d581f057b8b46a7621e24e9.
All8HRTB guards0/1.78s and12scope cases0/2.31s, compiler/decode0 each.
ActualfirstFnMut bool and syntheticunwind exitpost/leakcheck pass. Normal
accessclose134-137, strictcut140, FULLtoken141, endLife142, bothborrowEnd/
openFull143-146 and actualtail.read/ManuallyDropnew147 pass. Firstnewfailure
CopyOnDrop.src &*tmp148: Taking the address of this expression is not supported.
No guard/loop/restoredrange/fullfunction proof; actualfalse-comparison return
not claimed checked. VF1/.21s,RSS92,716KiB;refiner0/.15s,RSS91,820KiB;
overall1,runner1:20.89,RSS626,948KiB,setupdominates. No active run.
CompilerMIR/source investigation found stmt_mark_addr_taken stops at
MergeFractionsStmt without cont locals. Prepared one-line continuation patch
2c44ad1cdb218b82d8f82c714841fdeab2b76b356474ec146e2a780289acdf4a
on rawverify_expr SHAaf5f7399; no newManuallyDrop model/ownershipaxiom.
Next NEW selection verifast_insert_tail_address_taken, profiletuple_address_taken,
budget90: same8+12cases plus3address fixtures, unchangedexactRust/T/Fdomain.
Priorcutprofile retained. Builder strictfour-source-file audit and sourcehashes.
Default main exposes manual choice by workflow-only2f0a73b.

**Latest completed strict exit diagnostic:** [37413756431](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37413756431),
source `6209eb7dc5dc306a7fef09a17b84f61051aa2bac`,lft_cut90min.
Full logs/artifacts inspected. Diagnostic-only patche17492b5 builds0/22.55s,
RSS426,536KiB, same pins/prelude/exporter/refiner/source/pairedZ3/MIRaudit.
Binary81e4dbe4d20801252505a4bf6e56686cc333b3aad5419ff1c3d76321f75eea15;
all8HRTB guards pass0/1.48s and all12scope cases0/1.89s, compiler/decode0 each.
Actual firstFnMut unwind rejects points_to<F> (bound metadata only), because
outerF carries localHRTB equality in BoundedGhostTypeParam metadata. VF1/.16s,
RSS92,716KiB;refiner0/.12s,RSS91,828KiB;overall1,runner1:22.12,
RSS643,832KiB,setupdominates. No active run; actualnormalcut/move
not reached. Next narrow outerparameter boundmetadata rebase to entrycontext
at strictexit, preserving heap/typeidentity/tokens and truecmp-escape rejection;
Sol owns patch, Astra independently reviews before hosted run.
Prepared patch bd95733ec743be3ff343f653a2d8c49339315d3085c9faf1da4d096748fdf77c
rebases only outer namedparameter metadata to exact entrybounds, keeping all
heap predicates/fractions/terms. Strict gate after free_locals onnormal/return/
goto still rejects actualcmp types. Captured outervariable/entrytable aliases
contaminated by cmp failclosed beforeoutside and aftersuccessfulwholeblock.
Root reviewed delta; Astra found no concrete blocker after localized fixes.
Next NEW hosted source run, same8+12cases and actualunrestrictedT/F probe.

**Latest completed actual strict-scope probe:** [37413224006](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37413224006),
source `5181cb3c003954d3adbf824aef71d8c141bfa835`,lft_cut90min.
Full logs/artifacts inspected. Same26.09 pins/pairedZ3/ghost-byte/sourcehash/
compilerMIR audits pass; patch76c3f6db builds0/13.99s,RSS426,784KiB,
same e1037db742e3b038796a0fe92d2b6606cb208d24c72315c6088a77061028a571.
All8HRTB guards pass0/1.13s and all12scope cases pass0/1.55s: 2positive
proofs/basic+earlyreturn and10negative intended errors, everyexport/decode0.
Actual comparator preconditions/bool pass; its synthetic unwind return125
hits strict block end140: lifetime-scoped heap chunk still live. No exitpost/
normalcut/fulltoken/recoveredcells/move proof yet. VF1/.15s,RSS92,708KiB;
refiner0/.10s,RSS91,816KiB;overall1,runner1:10.88,RSS658,248KiB,setupdominates.
No active run. Next identify offending predicate/typeargs at strict exit,
check local cleanup ordering versus real escaped borrow resources. Preserve
rejection and unrestricted T/F domain. Prepared diagnostic-only patch
e17492b5a1d3ec636c4181578e35d2f21427be1be6b23eec43984576aa8df62f
prints first offending predicate/typeargs and direct-vs-bound-only origin;
root reviewed delta, heap/rejection behavior unchanged. Next hosted source run.

**Latest completed scope-regression run:** [37412915463](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37412915463),
source `81f235e8856fde9208f387bb0b9ec9b6b1492abf`,lft_cut90min.
Full logs/artifacts inspected. Patch76c3f6db builds0/26.80s,RSS426,932KiB;
binary e1037db742e3b038796a0fe92d2b6606cb208d24c72315c6088a77061028a571.
Pins/pairedZ3/sourcehash/actualMIR audit pass. All8HRTB guard cases pass0/1.76s.
Scope suite: 2positive proofs (basic17 bodyrecords,earlyreturn24) and7intended
negative failures pass; every attempted case exporter/decode0. Case10 stops
on fixture error No such function: payload before borrow, NOT intended ownership
failure; final2cases/actualtargetVF/refiner not reached. Suite1/1.97s;
overall1,runner1:30.14,RSS641,168KiB,setupdominated. No active run.
Next make payload a precise pred_ctor and close its applied predicate;
rerun all8+12cases at NEW source, unchanged semantic patch/domain.

**Latest completed HRTB guards + actual access closure:**
[37410979109](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37410979109),
source `3184c40f4a00745712bdce4a28ccdc76f352562c`,fnmut_hrtb90min.
Full logs/artifacts fetched. Same pinned26.09 source/release exporter/refiner,
parser+HRTBtracepatchd90,originalprelude,pairedZ3/sourcehash/MIRaudit pass.
Sourcebuild0/15.42s,RSS426,676KiB;binary7142413b68a4c9e9e17e5afaea566c2cd3d2615633b84ce612db9bfe03d7bbcb.
All8real-compiler/translator guard cases pass0,1.49s,RSS85,532KiB:
each compiler/decode0 and actual translatedcallcount match; expectedownershipVF1
is separated from marker1/0. Bool,u8,noOutput,wrongF,wrongT,unequalLfts,
secondunannotatedcall andbodyisolation. These are matcher tests, not8calleeproofs.
Actual insert_tail FnMut Output=bool and syntheticunwind exit/leakcheck pass;
normal bothref_initialized_ closes+matchingclose_frac_borrow calls pass,
merge/halfTokenassert139 pass. End_lifetime140 needsFULL token and fails
lifetime_token(cmp_k), confirming remaining lexicalreservation. No move/guard/
loop/fullrangeproof or covers. VF1/.17s,RSS92,728KiB;refiner0/.12s,
RSS91,696KiB;overall1,runner1:04.76,RSS646,280KiB,setupdominated.
No active run. Default main exposes manual choice by workflow-only591f251.
**Latest strict-scope source-build failure:**
[37412281007](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37412281007),
source `7b349f115e75ebcd030bb0788f0e8184b42fc112`,lft_cut90min.
Full logs/artifacts fetched. Rawkernel/translatorbeforecut pins and all3source
file checks pass, extraction/ghost audit0. OCaml translator3774 scoped_ids bb
inferred debug_info fromsharedidlabel; nochildrenfield; consolebuild2/12.19s,
RSS426,180KiB. No compiler MIR/guardtests/actualVF/refiner executed.
Overall2,runner1:16.46,RSS644,292KiB,allsetup. No active run.
Prepared explicit Mir.basic_block annotations onnewscoped_ids/Hashtblcallbacks;
next NEW source run with unchangedsemanticchecks/domain; no localcompile.
This is a separate experimental
strict early binding-scope cut, preserving runtime Rust/tuple_hrtb reproducer.
Source patch implemented by Sol and independently reviewed by Astra; concrete
static blockers fixed. Current patchSHA76c3f6dbc54183997a40d91c8a178a3b751a6771c8a42e79bb9cacbbe04c89e8
includes explicit basic-block annotations and the fail-closed guard for unexpected AST exceptions; actualRustunwind
uses wrappedreturn/goto. Root checked delta/signature; no AST/lifetime axiom.
Builder strictly checks rawkernel5968a05e and precedingtranslator ef88c9c0,
onlyparser/translator/kernel modified. Source + original/patchedmodels recorded.
Beforeactualproof, rerun8HRTB guardcases plus12isolatedscopefixtures (2positive,
10negative), compilerexport/decode0 required; failurestopsactualprobe.
Positivecut recoversfullToken, semanticendlife, bothborrow_end andfullcontent
openings beforeactualread. Negativetypedchunk includes['cmp,T], typeid/type
postcut, wrong/duplicate/outside markers, accessleftopen/doubletoken/end.
CFG ingress and conditional path shapes still require hostedrealMIR validation.
No repeatedrerunofoldsource, no localbuild/test. All builds/
regressions/actualproof only on hostedActions. No full token assumption.

**Latest completed HRTB instance experiment:**
[37409198258](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37409198258),
source `e7ac80db4016bf6cf41b40920e3af11dcfb30470`,
`verifast_insert_tail_fnmut_hrtb`,90min. Full logs/artifacts fetched.
Tuple/HRTB source patches, raw parser/translator/prelude pins, paired Z3 ldd,
readonly compiler capture/hash roundtrip and ghost-byte audit pass.
Console build0/15.01s,RSS426,676KiB. Derived binary SHA256
0fd865ddb9a8211a828c2b452e6b2758ece63f094594577d9faf672f4b441d66;
HRTB patch SHA c35c4b438563f5a9da0f79c658ac7450ca429c91ed91207f6caa1ee267d09758.
Actual FnMut call preconditions, Output=bool result type and synthetic unwind
exit assertion/leakcheck pass. First new error at actual tail.read verified134:
No matching heap chunks [_]points_to<T>(tail0,_). Comparison borrows still own
both cells. No restored range, successful move, guard or loop proof yet.
VF1/.17s,RSS92,704KiB;refiner0/.12s,RSS91,704KiB;overall1,
runner1:03.07,RSS645,516KiB,setup dominated. No covers/fullfunctionproof.
Trace counter2 includes error-context duplicate,193 execution/return records;
never accepted as two verified functions. No active run.
**Latest regression setup failure:**
[37410021241](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37410021241),
source `ca6ed8d91a0d369ad76a20a519a3cb053f2bd0cf`,fnmut_hrtb90min.
Full logs/artifacts fetched. Trace patch builds0/14.88s,RSS426,420KiB,
binary7142413b68a4c9e9e17e5afaea566c2cd3d2615633b84ce612db9bfe03d7bbcb;
pairedZ3/MIR/sourcehash passes. Positivefixture exporter/decode0,oneactualMIRcall,
thenVFparseerror on INACTIVEcfg function req atline22 beforeanycalltranslation.
Suite1,no casespassed/noactualinsertionVF/refinerreached. Overall1,
runner1:10.86,RSS620,492KiB,setupdominated. **Latest isolated regression run:**
[37410552459](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37410552459),
source `905fd9d0b3fa84a187b932c47bbad5bbe52402bc`,fnmut_hrtb90min.
Full evidence fetched. Sourcebuild0/25.76s,RSS426,720KiB,same7142413binary;
pairedZ3 and real-target MIR/sourcehash pass. Two casespass(Boolean/u8):
compiler/decode0,one real MIR+translatedcall each,ownershipVF1,registrations1/0.
No-output MIR has zero Projection predicates but local variable FnOnce::Output
alias. Runner's broad search misclassified alias as equality; suite stops1
before case3 VF. No actual insertion VF/refiner. Overall1,
runner1:24.32,RSS646,648KiB,setupdominated. The completed run above checks projectionTerm records rather than arbitrary alias
mentions, keeping zero actual predicate requirement and all8cases unchanged.
Uncommitted tuple_lft_cut integration is staged separately from this rerun;
source feature being implemented/reviewed, not part of current evidence.
Current semantic HRTB patch plus diagnostic traces (hash in verifast-fnmut-hrtb.md).
Eight real compiler/exporter/translator guard regressions precede actual proof;
compiler/decode must be0, calls must genuinely translate, expected verifier1
is classified separately from registration count. Failed suite stops actualprobe.
On actual normal true-comparison path, close both ref_initialized_ fractions,
close their matching accesses, merge/assert half-token, then end_lifetime.
This probes full-token recovery; req/posts and exact runtime Rust are preserved.
Existing declaration-scope route audited/exhausted: boundaries are the existing
Rust block braces, not arbitrary early markers. Separate sound early-binding
end design is under review; no new kernel feature implemented yet.
No assumed ownership bridge, new T/F restriction or runtime Rust edits.
Default main manual routing exposed by workflow-only commit29442c6.
See verifast-fnmut-hrtb.md and verifast-lifetime-diagnostic.md.

**Latest compiler projection capture:**
[37408278446](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37408278446),
source `d34616e2b0652be92ec5130737977ae0a7c8834e`,tuple_parser90min.
Full logs/artifacts fetched. Readonly exporter0/.03s,capnp decode0/.01s,
inputhash roundtrip0. MIR binary193,920bytes SHA395d1301cf8e9759ef0004b70e155818e36024467202e1f0ee933262c0410311;
text447,324bytes SHAf1217c6e036aa2954e66449df678224e2dc6cf39870ef2f97337d89cb4b0ec3a.
Actual insert_tail projection core::ops::FnOnce::Output for F,
tuple(&'__23 T,&'__24 T),RHSBool,boundRegions'__23/'__24;
FnMut trait sameargs. Call core::ops::FnMut::call_mut MIR selfF,
tupleRefsErased,lateBoundGenericParamCount1. Ghost overrides F,tupleCmp,cmp.
Pinnedtranslator dropsnonemptyboundregions; not an absentRusttypebound.
Sourcebuild0/14.16s,pairedZ3assert0;normalVF reproducesOutput/bool typeerror1
.15s,RSS92,708KiB;refiner0/.10s,RSS91,568KiB;overall1,
runner1:05.79,RSS584,844KiB,setupdominated. No fullfunction/covers.
No active run. Next reviewed source-only HRTB instantiation at actual call,
strict compiler-origin projection/region/non-lifetime type match,booleanRHS,
canonicalstd/coretrait. Existing precise type-projection registration only;
no new F bound/assume/opaquelemma/kernelfeature. Patch prepared by Sol and independently reviewed by Sol; compile pending.
New experiment selection verifast_insert_tail_fnmut_hrtb will preserve current
tuple_parser reproducer, same input domain and explicit comparison-resourceposts.

**Latest capture attempt:** [37407937980](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37407937980),
source `a627dec2fbdf76479c219a2edcc6de1225b4cfbc`,tuple_parser90min.
Full evidence fetched. Sourcebuild/pairedZ30 and ghost byte audit pass;
source hashes unchanged before/after diagnostic. Direct exporter127 because
LD used target-libdir instead of compilerdriver sysroot/lib; compiler MIR/decode
and actual verifier/refiner not reached. Overall127,runner1:21.70,RSS624,152KiB,
all setup/capture failure. No active run. Next mirror rust_fe.ml107-120 exact
sysroot/lib driver path, recorddriverhash, dispatch NEW source, inspect actual
rustc HRTB Projection before finalizing a translator-only instance patch.

**Latest run:** [37407173581](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37407173581),
source `ff413cfbee73e42c576eee96bdc461b80ca76255`,tuple_parser90min.
Full evidence fetched. Same tuple-only source/binary/prelude pins; sourcebuild0
19.14s. Paired source-bin Z3 ldd/assert passes; binary hash08431fb2 as below.
Input req/Rust bytes unchanged; normal/unwind post explicitly returns all
comparison borrow resources, without normalization or full-range restoration.
First exit resource consumption+leakcheck pass, then normal-call return is
abstract <F as FnOnce<tuple2<&'cmp T,&'cmp T>>>::Output,expectedbool,atline125.
Source FnMut(&T,&T)->bool bound must be propagated/instantiated for substituted
lifetimes; no extra F restriction, pure/comparator stub or assumed bool lemma.
VF1,.22s,RSS92,712KiB;refiner0,.15s,RSS91,704KiB;overall1,
runner1:15.93,RSS643,776KiB,setupdominated. No covers/fullfunctionproof.
Pinned translator4793-4801 drops rustc Projection predicates
with nonempty bound_regions; original FnMut bound is higher-ranked Output=bool.
Next capture actual compiler MIR binary+capnp text using unchanged release
exporter with readonly preprocessing, audited unchanged source, then inspect
actual bound-region names/projection before a narrowly justified frontend fix.
No new F restriction/assume/opaque bool lemma; all capture runs on Actions.

**Previous actual parser diagnostic:**
[37406214235](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37406214235),
source `45487efb5c9fda8ed4aa32d848dd179d946eb83c`,tuple_parser90min.
Full evidence fetched. Console artifact/source patch build0,18.51s;
prelude unchanged, exact ghost-byte/refinement0. New derived binary
08431fb200f070b5a4c37f9dd267108f337729d2ab6a53ae1ca9f7d512fec594;
paired Z3 hash1837668dc531d14b3a4fffc0b690b77929d29c41868f98a89686f5ff64da95ea.
Tuple own constructor, both actual references and FnMut preconditions pass.
First failure is comparator unwind continuation: call-position return103
(translator UnwindAction::Continue), empty default on_unwind_ens consumes
none, leakcheck reports half token, open refInit/close tokens, borrowEnd tokens,
F/thread/prefix resources. Neither normalreturn104 nor tail.read reached.
VF1,.22s,RSS92,680KiB;refiner0,.14s,RSS91,828KiB;overall1,
runner1:15.64,RSS645,520KiB,setup dominated;no covers/fullfunctionproof.
The latest run above adds exact transparent normal/unwind
comparison-resource postconditions: all tokens/fractions/borrowEnd/prefix/F/
thread/type_interp/foreach fragments returned, no wildcard/leak/assumption.
Same input domain and Rust. Explicit borrowing obligations remain unnormalized;
this is a partial exit diagnostic, not restoredrange or finalshiftcontract.
Dispatch NEW source and inspect exit-resource matching/next normal tail.read.
Runtime ldd capture originally preceded parent's paired-Z3 LD export;
next helper captures/asserts the actual paired resolution before execution.
Baseline pins unchanged; source-derived tool remains experimental.

**Latest source-build run:** [37405631794](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37405631794),
source `5dcf5348447174f3a9a8c23cce3bad80d70188ca`,tuple_parser90min.
Full evidence fetched. Pinned deps/decoder3.93s and patched OCaml console
compilation pass; broad make target then regenerates C STDLIB manifests and
fails unrelated bitops.c18 precondition x<pow_nat(2,N32),overall2.
No insertion verifier/refiner execution, no proof/covers. Buildstage1:18.67,
runner2:22.22,RSS642,736KiB,all setup. The active run above compiles only
../bin/verifast artifact target; pinned all-.rs frontend skips C manifest
link phase, uses source rust prelude. Do not reuse/fabricate C manifests.
Then dispatch NEW source commit and inspect actual insertion proof.

**Latest completed run:** [37405435682](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37405435682),
source `3d68d61ba5e8a95dfa67677a4cea294fb337b309`,tuple_parser90min.
Full logs/artifacts fetched. Source/parser/prelude pins, patch application and
exact ghost-byte extraction pass. Official VFDeps archive hash matches, but
wrong xz extraction flag rejects its bzip2 content. No decoder/console build,
verifier or refiner execution; no target proof/covers. Overall2,runner22.60s,
RSS629,004KiB, all setup. Next run above uses upstream tar -j flag at a NEW source commit; inspect
the build and proof obligation.
A reviewed tuple2-only parser patch is committed;
Actions source-build integration is ready and independently reviewed. Default main exposes the
new manual selection by workflow-only commit `569ff40`. Ubuntu22.04 for this
selection only; other profiles retain Ubuntu24.04. Baseline verifier/tool pins
and std runtime are unchanged.

Source base VeriFast26.09 `809de4596839b739dd999f9e462242c835e3af46`;
original parser SHA f7f2c2bf573be09d8ce5dcd640ddca0e1437a8f18464facc9621ac287a5082e8,
unmodified prelude SHA d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5.
Only console artifact `make ../bin/verifast`, pinned VFDeps25.01/vfdeps-adf88dc archive and
capnpc-ocaml-decoder revision2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2;
release exporter/refiner reused, source console/Z3/resources kept together.
One overall Actions budget includes setup/build/proof. No local build or install.
See verifast-tuple-parser.md; source-derived binary is experimental, not the
unchanged release binary or an accepted full Challenge8 solution.

**Confirmed tuple model blocker:** latest finished run
[37402802085](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37402802085),
source `c0742d522d83264003b7872444b402ef12a80c97`,tuple_overlay90min.
Strict original model hash and patch roundtrip passed; unchanged binaries;
VF rejects duplicate tuple2 own alias before any target execution.
Runtimebyte/refinement0,VF1(.09s),refiner.11s,runner14.17s,RSS527,852KiB.
Independent source reviews confirm rust_parser.ml:1139-1149 creates an opaque
bodyless own fixpoint plus alias for every RSSPEC struct. Same-name predicate
or fixpoint completion and external-file alias cannot supply a transparent
body. Stop naming/placement retries and do not add an unproved tuple2 bridge.
The reviewed source patch replaces only canonical tuple2 own by a transparent
field-own constructor, retaining exactly one alias and all other struct models.

**Completed generic target:**
[37401540878](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37401540878),
source `9fb8940437be22b316c45a3b23f9ece325944aae`,verifast_swap_size90min.
Actual has_efficient_in_place_swap<T>,unrestricted T,req true,result exactly
size_of<T><=8,LP64. Exact body/ghost-byte audit/refinement0,VF0;
one named target,four body execution/return records,0errors.
VF.10s/refiner.07s,runner12.70s,RSS585,516KiB. No covers/loopbounds.
Other six targets/callers/fullcore integration remain open.

**Generic insertion progress:** exact-source unrestricted T/F,n>=2 probe
37417173472 passes first FnMut Boolean/partial synthetic unwind, strict lifetime
cut/cell recovery, tail.read, held-reference/guard creation and first copy/dst
update, then fails generic compiler Drop. This is a prefix of a failing function
proof; secondcomparison and completed early/normal/unwind exits remain open.
The direct actualDrop body is separately proved37419989766, but automatic
cleanup reuse fails the new profile's regression37423762729 before callers.
Heldref release, resource-accurate exit posts, generic loop and outer remain open.
No Rust blocks/signatures may be changed to shorten the ghost lifetime.
See verifast-probe.md, verifast-lifetime-diagnostic.md and
verifast-drop-diagnostic.md.

**Bounded milestones:** actual swap bootstrap5/5covers37383583285 at
34d008324e10a66bf59de705acd609d9509e7c36. Insertion adapter contract,
summary-based research caller and direct std outer function all pass15/15covers
37389298278 at ec5556cf37fc31af4b25d27476c88f5fbc8e77c9,unwind6/assertionspass.
Verification22.868813+5.359691+16.718891s,runner5:38.03,RSS1,944,792KiB.
Four-cell i32 functional domains are not arbitrary-length/generic proofs.

**Pinned Kani blockers:** actual insertion UB run37396688760 at
43f133c72fcd4f3dffe033582aa96aa2500bf860 has7/7covers,no undetermined,
sole1/469failure unsupported copy_nonoverlapping validity check.
Verification3.1836462s,runner3:54.96,RSS1,821,596KiB.
Observed immutable-write control37397720683 at
75799de75efab17d9c386deea6c49047db16cb60 unexpectedly verifies0/205 and1/1cover
after write9/volatile-read/assert9;positive4/4covers. Detector gap, suitefails.
Outer-invariant37390973809 emits missing-argument nondeterministic substitutions
and endsSIGTERM143 before finalproperties/covers. No warned proof may be accepted.
Frozen-pointer rewrite prepared, needs GOTO call/formal evidence on Actions.
See ub-checks.md and outer-invariant-diagnostic.md; preserve all checks/copies.

Full completed logs/artifacts fetched and summarized in README/topic notes;
artifacts expire7days. Runtime std source SHA256 remains
32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959.

## Repository map and verifier details

- smoke.rs: two original swap_if_less bootstrap proofs.
- insertion-4.rs: actual insert_tail behind a monomorphic proof-only adapter;
  a caller using verified summaries; a separate direct proof of the actual
  insertion_sort_shift_left.
- insertion-contract.md: specification, assumptions and proposed invariants.
- run-smoke.sh and run-insertion.sh: Actions entrypoints; do not execute locally.
- insertion-safety-4.rs and inject-outer-invariant.py: actual outer-loop safety prototype.
- outer-invariant.md and coverage.md: prototype scope and challenge obligations.
- extract-verifast-insertion.py, run-verifast-probe.sh and verifast-probe.md:
  exact-source approved-tool feasibility probe, no completed proof yet.
- README.md in this directory: experiment scope and run log.

The insertion order is prove_tail_contract_4, prove_composition_4,
prove_direct_insertion_4. The runner stops on the first failure; the summarized
caller must not be accepted if the callee failed. The direct stage is a separate
check, not a modular proof of the real outer loop.
The domain is arbitrary i32 values in a four-element backing array, symbolic
valid lengths/offsets, and unwind 6. Values include duplicates and extremes.

The pinned std integration uses kani::cover(condition, message), not cover!.
scripts/run-kani.sh already enables function/loop contracts and related unstable
features. Check API syntax against the PINNED Kani source before inventing flags
or annotations; if compilation is needed, create an Actions experiment.
The workflow caches Cargo downloads, not the complete verifier build. Cold
build time counts toward the chosen budget. Artifacts expire after seven days.

## Start or resume a session

Inspect git status, current branch and remotes. Fetch the fork and use
challenge-8/research without overwriting user changes. In a clean clone, a
typical setup is:

~~~bash
git status --short
git remote -v
git fetch origin
git switch challenge-8/research
git pull --ff-only origin challenge-8/research
gh auth status
~~~

If the branch does not exist locally, create it tracking the fork's remote branch.
If origin is not the fork, use the actual fork remote; do not blindly change it.
Check authentication for git push AND workflow dispatch. Never print tokens.
If gh is unavailable or unauthorized, use an already authorized equivalent
GitHub API client if available; otherwise request only the missing setup.
Do not substitute server-side verification.

## Autonomous edit → push → dispatch → inspect loop

The examples below use GitHub CLI. Consult installed gh help if an option differs.
Official references:
https://cli.github.com/manual/gh_workflow_run
https://cli.github.com/manual/gh_run_list
https://cli.github.com/manual/gh_run_view
https://cli.github.com/manual/gh_run_download

1. Choose one concrete proof obligation from the plan. State its domain,
   preconditions, expected properties and what will remain unproved.
2. Make the smallest useful implementation. Locally inspect the diff and use
   only permitted static checks (for example git diff --check or bash -n).
   Never execute the proof runners on this server.
3. Commit only the intended files and push normally to the fork's research branch.
   Verify its remote SHA matches git rev-parse HEAD. Do not dispatch unpushed code.
   After confirming origin is the fork and you are on the research branch:

~~~bash
git push origin HEAD:refs/heads/challenge-8/research
git rev-parse HEAD
git ls-remote origin refs/heads/challenge-8/research
~~~
4. Inspect existing research runs before dispatching. Resume monitoring a relevant
   active run instead of duplicating it. Record the pre-dispatch time/run IDs.
5. Dispatch explicitly against the fork and branch:

~~~bash
gh workflow run smallsort-research.yml \
  --repo Tiramisu-Cake/verify-rust-std \
  --ref challenge-8/research \
  -f proof=insertion_all_4 \
  -f budget_minutes=90
~~~

Available insertion selections are insertion_all_4, insertion_contracts_4,
insertion_direct_4 and insertion_outer_invariant_4. The choice all means the two BOOTSTRAP harnesses, not every
research proof. Other bootstrap choices select the individual harnesses.

6. Capture the returned URL if the installed CLI supplies one. Otherwise query
   runs and select the newly created run matching the branch, event and expected
   full headSha. Do not blindly take the latest run from the repository:

~~~bash
gh run list --repo Tiramisu-Cake/verify-rust-std \
  --workflow smallsort-research.yml --branch challenge-8/research \
  --event workflow_dispatch --limit 20 \
  --json databaseId,url,headSha,headBranch,status,conclusion,createdAt
~~~

   If listing is delayed, poll again; do not immediately dispatch a duplicate.
   If multiple candidates exist, compare the pre-dispatch list/time and run
   metadata/logged selection before accepting any evidence. Save the exact run ID,
   URL, SHA, selection and budget in the checkpoint. Do not push further proof
   changes on this branch until the intended dispatch has resolved to its SHA.

7. Poll the specific run roughly once per minute until completed. Use short
   waits so progress updates remain possible; do not end the turn just because
   the job is building or queued. Read-only polling runs locally, verification
   runs entirely on GitHub:

~~~bash
gh run view "$run_id" --repo Tiramisu-Cake/verify-rust-std \
  --json databaseId,url,headSha,headBranch,status,conclusion,jobs
~~~

8. After completion fetch the full log and artifacts, even on success:

~~~bash
gh run view "$run_id" --repo Tiramisu-Cake/verify-rust-std --log
gh run download "$run_id" --repo Tiramisu-Cake/verify-rust-std \
  --dir "/tmp/challenge8-evidence-$run_id"
~~~

   run_id above is the ID you verified, not a placeholder to execute literally.
   Do not commit downloaded archives, injected source or large logs. Keep a
   compact, committed result record before artifacts expire; save essential
   diagnostics and source/tool identifiers there.

9. Check the artifact environment/source SHA, expected selection, all requested
   harnesses, verification outcome, all covers, unwind assertions and exit code.
   A green badge alone is insufficient. Distinguish compilation failure,
   verifier failure, unreachable covers, timeout/OOM and infrastructure failure.
10. On failure, diagnose the first causal error and make an evidence-based fix.
    Preserve proof obligations. Push and dispatch a NEW run after source changes;
    gh run rerun on the old run would verify its original commit.
    On success, record the precise proven scope and advance to the next plan item.
    Do not ask the user to launch or inspect the next run.

Default budget is 90 minutes, with choices 30/60/90/120. A justified retry at 120
is authorized when the log shows the budget was the bottleneck. Repeated timeout
or unchanged failure calls for a different experiment or better contracts, not
blind reruns. Keep --jobs 1 for these initial experiments. Never switch to a
self-hosted runner or chargeable external compute as a workaround.
Documentation-only commits do not require a cold verification build.

Keep workflow_dispatch as the only trigger for the research workflow. For a new
experiment, update its runner and workflow choices explicitly. GitHub requires
the dispatchable workflow to exist on the default branch. If a default-branch
workflow update is necessary, commit only that reviewed workflow change there;
do not merge all research results into main merely to expose a new choice.

## Original plan after the bounded insertion run

The bounded three-stage milestone below is already completed37389298278.
Use the consolidated handoff for the current continuation sequence; do not
restart completed bounded stages as if they were still pending.

1. Resolve compilation and verify all three insertion stages. Record contract,
   modular caller and direct outcomes separately, including verification costs.
2. Develop a reusable contract and loop invariants for actual insert_tail and
   insertion_sort_shift_left, without changing runtime behavior/signatures.
   Track the sorted processed prefix, conserved multiset, untouched suffix,
   pointer bounds, logical gap, held value and CopyOnDrop restoration.
   Prototype one obligation per experiment using the pinned tool's supported
   annotations. If the tool blocks a generic contract, document a minimal
   Actions reproducer and evaluate an approved alternative or hybrid approach.
3. Test modular reuse on an actual std caller. The current three-call research
   harness is only a composition experiment, not std's pointer loop.
4. Expand domain/type coverage and separate safety harnesses from functional
   ones. Bounded lengths up to 16 are optional performance milestones;
   arbitrary valid lengths remain the requirement. Develop merge specifications
   after establishing the insertion approach.
5. Cover sort4_stable and the other SmallSort primitives, then the three trait
   implementations. Maintain a coverage table for the seven safety targets,
   three sorting contracts, specialization paths, generic types/ownership,
   comparator panic/unwind behavior and each required UB category.
6. Address length-32 scalability and uninitialized-read detection explicitly.
   Measure the supported checks rather than assuming default Kani checks cover
   every required UB. Compare approved tools on concrete blockers.
7. Prepare an automated, reviewable candidate acceptable to upstream CI. Clearly
   document assumptions and remaining gaps. Ask the owner before upstream
   publication or bounty submission.

## Durable progress record

After each meaningful result, update this runbook's handoff/next action and the
README run log in a small commit, then push it. Record:
- Full checked source SHA, run ID/URL and selection/budget.
- Tool pin and exact domain/preconditions, checked properties and enabled checks.
- Harness/cover outcomes and failure diagnosis; time/memory with build time
  distinguished from verification time.
- Whether a result is a real implementation proof or a caller using a verified
  summary, and the source/version supporting that summary.
- The next concrete experiment, any blocker and any active run to resume.

Never infer that a later documentation commit was verified by an older run.
If the session must stop, checkpoint this information before stopping. Autonomous
polling continues only while an agent session is active; this file is not a daemon.

## Historical alternate-tool diagnostic

This section records the initial alternate-tool choice, now superseded by the
generic source-derived profiles and current handoff. It is not a pending run.
The Kani outer run was incomplete with instrumentation warnings. The initial
`verifast_insert_tail_probe` (90 minutes) used the approved repository pin
VeriFast 26.09 and nightly-2026-02-05, exact source extraction, ghost-only copy
and refinement-checker. The diagnostic contract is `req true; ens true;` on
actual insert_tail; it intentionally lacks ownership and is expected to fail.
Never label a frontend result or a skipped target as a proof. No ignore-unwind,
allow-assume or assume_correct flags. See verifast-probe.md.
The manual choice/routing is exposed by default-branch workflow commit `4e32d41`;
research source must be pushed before dispatch, and only one experiment active.
Kani loop invariants alone do not enlarge the four-cell harness allocation;
this probe investigates a mathematical arbitrary-length ownership model.
