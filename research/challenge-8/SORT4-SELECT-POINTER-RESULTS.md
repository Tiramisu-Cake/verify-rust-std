# Pointer select completion — results

2026-10-07 IN PROGRESS;entrycd44e1bbf115c83c84fd7d4c050b1f74be0e1d09.
Current budget1854/5400 summed hosted job seconds, no active run. Intrinsics pending;
whole helper NOT PROVEN. Existing O4 constructor experimental acceptance retained.
[Phase](SORT4-SELECT-POINTER-PHASE.md),[design/map](SORT4-SELECT-POINTER-DESIGN.md).
RAPx CLOSED/NO-GO;B/C NOT RUN;fullsort4 outside phase.

S1/37607108528/sourcef19f077457da722e326f88df362b0d14731987e0,
profile325af428 unchanged: source/export/decode/refinement PASS, then SAFE prototype
leaks full_borrow at1beforebody;contract adaptation mismatch,notsemantic boundary.
108/5400jobseconds,noactive. Compactartifact11474994216,ZIP1050469bytes,
O4770+current73 included;manifest843/843SHA/CRC/sizematches.
[Compact evidence](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37607108528/artifacts/11474994216),
[run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37607108528).
S2tests actualelidedreceiver IN/OUT wrappercell/value transport at unchangedprofile;
component/fullhelper acceptance pending.

S2/37608166705/sourcea20e64856822850c76e13ad7bc0d1248af0676a0,
unchanged325af428:3 SAFE/body/frame/state positives PASS;4intendedproofnegatives
PASS,lostcell actualtargetleak reached atfinal32 butclassifiermismatch=>INCONCLUSIVE.
No newcomponentaccepted; this confirms existingelidedreceiver protocol feasibility.
130jobseconds,total238/5400,noactive. [Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37608166705),
[compact11476196005](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37608166705/artifacts/11476196005),
ZIP1221330bytes current227+O4770. S3fullcriterion/design9e02c4f,implementationpending.

S3/37610022772, source489416d21b52858b124638d88180378ef2b4b8d0,
profileexperimental-source-linked-select-pointer-as-mut-ptr-v1/patch e9b4d025,
177hosted jobseconds (10:50:21–10:53:18UTC); spend415/5400, noactive.
Full constructor regressions16source/proof+9MIR and14baseline controls PASS;
constructorclassifier5groups and selectclassifier58gate mutants PASS.
3active-rule SAFE/body/frame/state positives PASS,5intended proofnegatives PASS.
Invent_initialized reaches intendedpost24:180–184 and rejects none→some:
`Cannot prove that 'std::mem::MaybeUninit::inner(pointer_typeid(Element_typeid), value)' is not an instance of constructor 'none'`.
Classifierwrongmessage kept INCONCLUSIVE;17admission controls NOT RUN, component
UNACCEPTED, actualintegration NOT RUN. S4fixexactmessage+4message-mutants, nosemantic
change; fullmatrix then actualbody with checkedconstructor+asptr ifaccepted.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37610022772),
[compact11477915575](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37610022772/artifacts/11477915575),
[full11477880702](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37610022772/artifacts/11477880702).

S4/37610819914/source6f5d28502767cef9a730549eba2b9784f084c961,
samee9b4d025profile,205jobseconds (10:57:32–11:00:57UTC),total620/5400.
All3positive+6proofnegative+8sourceadmission+7MIRadmission controls PASS;
MIR contract mutation failed in harness BEFORE export finished: expectedoneown
occurrence but exact SAFEpre/post containstwo. This is INCONCLUSIVE, not intended
negative; MIRcontract/additionalop andactualintegration NOT RUN. Fullctor and
14baselines/classifiers PASS. Compact11477701950,full11477662208,
[run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37610819914).
S4b changesexactone preannotation afterasserting2pre/postoccurrences, keeps
expectedcertificate reason/stage strict. No semanticdelta; finish2admissions,
then actualintegration ifaccepted. Hostedcompact read in memory after local
diskfilled; historical/full archives preserved, onlyredundantlocalcopiesremoved.

S4b/37611745252/source7c14ab64372d75928c4a000bb43dad83761c5bb4,
unchangede9b4d025;247jobseconds11:05:39–11:09:46UTC,total867/5400.
Asmut SAFE/body/state/frame COMPONENT_ACCEPTED:3positive,6proofnegatives,8source,
9MIR,fullctorregression/baselines/classifier+4message controls PASS. Allcontrols
reachedtargetchecks, including exact MIRcontract andextra-operation certificate.
Actualcombinedunit RUN, bothlocalcallee typedcertificates PASS,2ctorredirects
seen; firstexternalasptrredirect rejectedbeforebody becauseeffective type
substitutions include stock-synthetic erased lifetime. Underlying rawFnDef sole
pointertype+latebound1 confirmed in MIR, correctiondesigncommitted7fc98da before
implementation. Actualfinalpost/borrow/resourceprotocol stillNOTPROVEN.
[Compact11477673504](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37611745252/artifacts/11477673504),
[full11477848970](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37611745252/artifacts/11477848970),
[run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37611745252).
S5new8e838ad1profile includesexactlifetimecorrection +typedcompilerintrinsic
selection rule/checkedownershiptransfer, currentlyUNACCEPTED feasibilityonly.

S5/37612975447/sourcef7543ce101907249614dcfbf427bef8f223e87d7,
profile07930fff:97s11:16:39–11:18:16UTC,total964/5400, BUILD FAILED.
OCaml module localbodystring shadowed BodyRd.t parameter at8783; noproof/MIR
matrices executed. Namefixe5663903 changesno semantics.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37612975447),
compact11479045470/full11479215424 preservebuildlog/profile/O4.
Laterfullarchivesexclude disposablemutation-profile tool/librarycopies, retain
wrapper source outsidethatdirectory andalllogs/MIR/profiles/hashes. Historical
fullO4 andearlier fullarchives remainunchanged; compactevidencealreadyexcludedtools.

S5a/37613525435/source6b6d033b5729a6a8d72597838523570a3d8afc65/e5663903,
138s11:21:32–11:23:50UTC,total1102/5400. Newprofilefullctor+asptrmatrices
and60intrinsicclassifiermutants PASS (earlierdesigncard's62countwasincorrect).
Actualbothtypedgates/2redirectseachPASS, SAFEhelper entered; firstPROOF failure
Incorrectnumbertypeargs atasptr38. ExactlocalVFsignatureincludesinferredlifetime
generic, sourceRustsignatureunchanged; correction6f705b9 reviewedbeforeimpl.
Bothintrinsicfeasibilityunits export/decode/refinement/integrity PASS butcandidate
4locals graphrejects actual7locals beforeproof. NOT accepted intrinsic/helper.
[Compact11479611306](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37613525435/artifacts/11479611306),
[full11479026615](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37613525435/artifacts/11479026615),
[run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37613525435).
S5b2cd1a04a exactcanonical7locals/BBgraph +inferredlifetime redirect, full
intrinsicacceptance3+3positive/5+5proof/40admission/60classifiercriteria implemented.
Firstunknownwrongresultdiagnostic failsclosed untilrawprooferrorobserved;
noacceptancebeforeallgates, noactualintrinsicruleintegrationbeforeaccepted.

S5b/37615266238, source `2fb924f02061a00a6e0204ed90145ef8c8f1e912`,
patch `2cd1a04a35e58f5337e392cc5e27899ac7de20ad5d821f47045438e0348c732b`,
150s (11:36:56–11:39:26 UTC), total1252/5400, no active run.
Six intrinsic positives PASS: pointer symbolic/true/false, wrapper unknown/none/some,
SAFE compatibility, checked body/ownership lemma, full modeled result/inner,
thread/frame/no-unwind/leak. Exact source/full typed MIR/refinement gates PASS.
Two negative cases reach normal post26 but message mismatch remains INCONCLUSIVE:
`Cannot prove condition. (Cannot prove !(result0 = (condition ? a : b)).)` and
`Cannot prove that 'std::mem::MaybeUninit::inner(pointer_typeid(Element_typeid), result0)' is not an instance of constructor 'none'`.
Eight other proof negatives and40 admission controls NOT RUN. No intrinsic
component acceptance. Constructor/as_mut_ptr complete regressions, baselines and
60 intrinsic classifier mutants PASS. Actual body now passes both as_mut_ptr
calls; first remaining unsupported intrinsic is at49:21–92 with rule disabled.
Full helper NOT PROVEN; guard/drop/forget/assume_init not yet proved.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37615266238),
[compact11478479176](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37615266238/artifacts/11478479176),
[full11478894018](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37615266238/artifacts/11478894018).
S5c pins only these exact diagnostics plus10 message mutants; identical semantic
profile, full matrix required. Full actual certificate remains disabled pending
separate typed graph implementation and complete component acceptance.

S5c/37616835826/source `6a9ddc9fa3c228f244010483bd7840521b3edce7`,
unchanged2cd1a04a:100s11:50:40–11:52:20UTC,total1352/5400, noactive.
All6positive and10proofnegative PASS at intended value/inner/assert/post/leak/
frame obligations. Classifier60+10 PASS. Sourceidentity admission PASS; source
inputtype rejection reaches exact HIR generic count/kind beforeproof, but expected
source-marker reason differs =>INCONCLUSIVE. Remaining38admissions NOT RUN.
Intrinsic component NOT ACCEPTED; actual unchanged firstintrinsic49, helperNOTPROVEN.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37616835826),
[compact11480431752](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37616835826/artifacts/11480431752),
[full11480376847](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37616835826/artifacts/11480376847).
S5d exact HIR reason+4 diagnostic mutants and all40 independent admission results;
full acceptance remains all-or-nothing. Separately export/probe exact unsafe pointer
method body with stock free-drop contract, no drop semantic change (design1caf569).

S5d/37617734037/source `d08fa8ad86b6b735ea6a4ec2474da372d6d4ce78`,
same2cd1a04a:147s11:58:36–12:01:03UTC,total1499/5400,noactive.
Ctor/asptr full regressions/baselines/classifiers PASS. Exact pointer method
source/export/decode/refinement PASS; stock free-drop requires the defined empty
pointer-own chunk, which was not explicitly closed, so method proof fails at
std/lib.rsspec612 before no-unwind/return. Harness then reads missing fixture.json;
this local implementation error aborts stage. Intrinsic matrix/admissions NOT RUN.
No new component accepted and no semantic boundary inferred from these failures.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37617734037),
[compact11480588490](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37617734037/artifacts/11480588490),
[full11480018683](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37617734037/artifacts/11480018683).
S5e new v2/1c9637f certifies full actual graph; fixes diagnostic fixture and
closes stock raw_ptr_own without Element resources. Canonical assume_init export
remains diagnostic with narrow field-address translation inactive. Full intrinsic
matrix and same-profile regressions required before intrinsic-on actual proof.

S5e/37618952909/source `bd4a63dde50f410d0ef670cc494bb9795811f42c`,
v2/1c9637f:90s12:09:01–12:10:31UTC,total1589/5400, noactive.
BUILD FAIL: generated ScalarInt.size_get is OCaml int, Uint8.to_int expectsuint8.
No component/diagnostic export or proof ran. Packaging safety/current+O4 PASS.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37618952909),
[compact11480883970](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37618952909/artifacts/11480883970),
[full11480619259](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37618952909/artifacts/11480619259).
S5f removes conversion only, patch9181630f, exactsame v2 acceptance criteria.

S5f/37619547036/source `08e16f3fa003be4baf6e3a04df1c240ce4d6167d`,
9181630f:43s12:14:11–12:14:54UTC,total1632/5400,noactive.
SETUP FAIL: strict canonical applied.patch audit catches stale new blob hash
from textual patch API fix. No build/proof/MIR. S5g regenerates git diff from
cleanVF809 two-file worktree; only blob/index header changes, hashec841d1c.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37619547036),
[compact11481671010](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37619547036/artifacts/11481671010),
[full11481451361](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37619547036/artifacts/11481451361).

S5g/37619961051/source `53f4d9459df5557d528b01ccba6cb695984113c2`,
ec841d1c:93s12:17:44–12:19:17UTC,total1725/5400,noactive.
Canonical patch audit PASS; BUILD FAIL8978: unannotated guard_type parameter
cannot resolve decoded record kind. No MIR/proof. S5h adds D.ty annotation only.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37619961051),
[compact11482375375](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37619961051/artifacts/11482375375),
[full11482115571](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37619961051/artifacts/11482115571).

S5h/37620410162/source `634de56a65ca6d6757a5ab195b042d957cade153`,
73f0904f:129s12:21:34–12:23:43UTC,total1854/5400,noactive.
BUILD FAIL9197: D.decode_uint128 returns decoded record, notStdint.uint128.
S5i uses existing CapnpAux reader conversion; numericAPIs reviewed, nosemanticdelta.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37620410162),
[compact11482281192](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37620410162/artifacts/11482281192),
[full11482311201](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37620410162/artifacts/11482311201).
Four separate kernel/storage ghost-only diagnostics added; no source-linked
assume_init/body acceptance inferred from them, unknownerrors remainINCONCLUSIVE.
