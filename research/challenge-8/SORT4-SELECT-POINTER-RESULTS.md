# Pointer select completion — results

Current S7b: **auxiliary generic body NOT ACCEPTED; actual linkage NOT ACCEPTED;
no S7 actual advancement.** [Report](SORT4-SELECT-FORGET-RESULTS.md),
[design/trust](SORT4-SELECT-FORGET-DESIGN.md), [current checkpoint](STATUS.md).
Standalone run37675513854/source `c9c59a85807da0135a8192b1912b15d510c68028`
checks the whole minimal generic unit without focus/select/macros/guard. All seven
predeclared functions execute, return and leak-check; full verifier exits1 with
sole adapter-span dead-code diagnostic. NORMAL/readonly/decode/refinement exit0;
source hashes PASS. Existing ManuallyDrop correspondence remains TRUSTED.
Separate immutable replay37676357686/processor
`dd4b0493b8411d92f61f525a3c7ef6ec0429d021` preserves all nine original classes;
new separate map has two INCONCLUSIVE positives and seven intended negatives.
Dead-code exit1 never becomes PASS. Full S7 thread/cell/frame/borrow/admission/
mutation controls and new-profile regressions remain NOT RUN; no actual redirect.
S6v4 remains accepted. Last actual run37656621026 still stops at forget63,
std/lib.rsspec420 requiring absent nominal guard-own; assume_init is not reached.
Full helper/sort4 NOT PROVEN. Latest [AST diagnostic37678089113](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37678089113),
source `a6f077a5aa89ad25df94295320cdbe18ebe4b9d9`, confirms an orphan translated
cleanup return; full VF remains exit1, with source/MIR/tool identity retained.
STOP at frozen translation/dead-code acceptance; no pruning/exemptions/model change.
Physical loc-key attribution remains an explicit diagnostic limit in the report.
Budget **4752/5400 summed hosted job seconds used; 648 remain**, no reset/no active
run. Historical budgets and instructions below do not reopen phases.

Historical S6 closeout: **COMPONENT_ACCEPTED (v4); actual integration STOPPED at forget guard-own.**
[Fresh run37656621026](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37656621026), proof source
`75681fbc57bda633f59096cdc28f0c1aa61daef8`, profile
`experimental-source-linked-select-pointer-drop-v4`, patch
`c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1`.
Constructor/as_mut_ptr/typed intrinsics/narrow pointer drop matrices and14baselines
PASS freshly; S6 has2positive+11proofnegative+22source/MIR/pin negatives, all on
intended obligations. All19 independent NORMAL controls reject exactly beforeproof,
including oldreceiver26→23. Full source/typed method+actual MIR/runtime/normal-unwind
CFG correspondence preserved; diagnostic37649244205 is not a proof. Five extra
stock ghost locals/blocks and every annotation coordinate are in the design table.

Actual baseline still lacks initialized payloadcell. Stock-projected actual enters
proof after full36/19 admission and checkedmethod redirect. Both stock opens, proof
condition split, retained runtime drop at verified/lib.rs60 and both closes61/62
pass in the recorded prefix. Next blocker: verified/lib.rs63 `mem::forget(guard)`,
frozen std/lib.rsspec420:41–42 requires nominal
`<DropOnPanic<*const Element>>.own(t, guard)`, absent. No guard/forget extension;
STOP at this exact obligation. Current classifier stays INCONCLUSIVE with heuristic
kind intrinsic_select; rawlog establishes the forget guard-own failure separately.
Finalreturn/leak/fullnormal-unwind posts not reached; wholehelper/sort4 NOT PROVEN.

Checked method and ghost resource identity lemma are separate from TRUSTED compiler
raw-pointer drop glue correspondence and frozen stock frontend ghost substitution.
Existing initializedcell/fullpointervalue/thread/independentframes required, no
Element rights. Recursive free stub is not a runtime-body theorem. Runtime std,
signatures/targetcontract unchanged; broader04d67f4b/Drop/guard/forget/assume_init/
union/refiner/kernel/memory/alias/provenance stay frozen. Further semantic work
requires a separate owner decision; no additional dispatch authorized at this stop.
Budget **3954/5400 summed hosted jobseconds used;1446remain**, same budget/noreset,
noactive. Last two proof orchestration jobs:37654585346=184s,37656621026=202s.

[Design/trust](SORT4-SELECT-POINTER-DESIGN.md), [actual resource trace](SORT4-SELECT-CALLEE.md).
Historical budgets/next instructions below are historical evidence.

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

S5i/37621093604/source `3d822b09dc6e8eeb53aea934592fd36027ade965`,
v2/7bb39a84:154s12:27:21–12:29:55UTC,total2008/5400,noactive.
BUILD/profile audit PASS; fullctor/asptr/classifiers/baselines PASS. Pointerdrop
exactmethod body now reaches stock unwind post10:15–20 `Cannot prove false`;
stock general drop permits unwind, insufficient for target (not a semantic stop).
Assume-init export/refinement fails E0658: missing transparent_unions feature.
No read-proof or admission/ghost/fullintrinsic matrix ran; canonical assume MIR
not yet obtained. S5j adds fixture crate feature and collects independent diagnostics
while retaining nonzero final status for their setup failures; matrix gates unchanged.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37621093604),
[compact11481794092](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37621093604/artifacts/11481794092),
[full11481549245](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37621093604/artifacts/11481549245).

S5j/37621751848/source `2454e860dc75c277686f3031a311501a3cd2b9e3`,
v2/7bb39a84:190s12:32:45–12:35:55UTC,total2198/5400,noactive.
Full ctor/asptr/classifiers/14 baselines PASS. Intrinsic6positive+10proofnegative
PASS, all40 admissions ran;32classifiedPASS,8 exact-fatal mismatches only.
Raw logs confirm all40 correct certificate rejection before proof, source/export/
decode/refinement/mutation integrity. These mismatches do not yet accept component.
Corrected from original S5j logs: canonical readonly source/export/decode PASS
(5locals/4BB), but refinement EXIT1: `RawPtr: not yet supported` at bb1 command4,
original25/verified33. Normal VF preprocessing separately rejects ghost close
after tail read; body NOT entered. The earlier refinement-PASS claim was wrong. GhostSome pre nested binder rejected; None/
unknown reached initialization requirement but expected error-location wrong.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37621751848),
[compact11481774726](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37621751848/artifacts/11481774726),
[full11482378240](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37621751848/artifacts/11482378240).
S5k repeats only concrete harness/classification corrections, unchanged7bb semantics.

S5k/37624082376/source `128dd5673c7796c5916017ab4afafaeea8d836b8`,
v2/7bb39a84:175s12:51:51–12:54:46UTC,total2373/5400,noactive.
Intrinsic COMPONENT_ACCEPTED:6positives/10proofnegatives/40admissions PASS,
60gate/10wrongresult/28admissionmessage classifier mutants PASS; same-profile
ctor/asptr/14Rust/C/C++ regressions PASS. Raw actual intrinsic-on source/refinement/
full31local14BB certificate/all3call translations PASS; body enters and stops at
`verified/lib.rs(57,9-29): No such function: std::ptr::mut_ptr::<impl *mut T>::drop_in_place`.
Two earlier intrinsic operations execute; later wrapper call is translated, not
proved on a reached path. Whole helper remains NOT PROVEN. This run was dispatched
before latest user steering; no additional proof repeats for replay correction.
Independent assume: removed tailghost now normalrefinement fails bb1command4
`RawPtr: not yet supported` (original25,verified33), preserving source hashes and
both equal command dumps. VF separately TodoAdtDefUnion; read body NOT entered.
Ghost castSome open/close/frame PASS; None/unknown intended initialization rejects;
unionSome `No such function: union_variant_ptr` is applicability INCONCLUSIVE,
not evidence of missing ownership. Independent failures give workflow failure
but do not block the intrinsic component or actual diagnostic stages.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37624082376),
[compact11482879763](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37624082376/artifacts/11482879763),
[full11482659442](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37624082376/artifacts/11482659442).
User freezes further semantic expansion. New04d67f4b profile and unfinished
admission/drop harnesses preserved as NOT RUN; no source-linked assume/read theorem
or ownership/provenance boundary inferred. Next replay uses immutable S5j saved
artifact and exactsame7bb profile, separately preserving old INCONCLUSIVE results.

S5r/37625744772/sourceadf1554c3bb6158f1224b7e1ed5e4e2864c7b3a8,
replayS5j frozenv2/7bb:11s13:05:07–13:05:18UTC,total2384/5400.
Archive/GitHubmetadata/3839entry SHA-size-CRC/selfchecks60+10+28 PASS.
Replay fails exact equality on first positive because script set positive_prerequisite
false for a positive, unlike original classifier's vacuously-true prior-positive
gate. No proof execution; replay acceptance NOT established. S5r2 duplicates the
original ordered gate and requires all3 saved positives before any negative;
retains exact unchanged classification equality. No broad error matching change.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37625744772),
[replay evidence11484166969](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37625744772/artifacts/11484166969).

S5r2/37626031885/replay source
`586c9ae4155a3ad0d3c50ebed2d22d9716a80b4f`:14s13:07:21–13:07:35UTC,
total2398/5400,3002 remaining,noactive/queued. **REPLAY_COMPONENT_ACCEPTED**.
Input S5j/2454e860dc75c277686f3031a311501a3cd2b9e3, frozenv2/7bb39a84:
all3839 source/current+O4 manifest entries SHA/size/CRC verified. Replayed6positive,
10proofnegative,40admission classifiers solely from saved raw evidence. Sixteen
proof classifications and32admission classifications identical; exactly8 old
exact_fatal-only mismatches now intended certificate rejects. Saved original
INCONCLUSIVE summary+all60 original classification/summary files untouched;
separate56 corrected records and replay summary. Original archive outerSHA
1a5e4957da5db048d02cb56bc518eb8afa195be5384d60f300281ed8f0f036c7 preserved byteexact.
Current classifier60gate+10wrongresult+28admissionmessage and16stage/cert checks
PASS; replay36message/stage/cert/archiveprofile mutants PASS. NoVFbuild, exporter,
refiner or proof process. No crossprofile transfer.

| S5j cases (each ptr and MU) | Mutant inspected | Exact v2 rejection and intended check |
| --- | --- | --- |
| source identity (2) | helper and its caller renamed to `_impostor` | `expected one exact SAFE helper/probe or actual body`; exact named source/body admission |
| MIR operand_order (2) | data arguments `_5`, `_6` swapped | `standalone place: _5`; second argument must be Move of exact local `_5` |
| MIR operand_source (2) | second data argument replaced by third | `standalone place: _5`; second argument's exact source local |
| MIR predecessor_source (2) | source Copy `_2` changed to `_3` | `standalone place: _2`; ordered predecessor assignment's exact source local |

All8 have exporter/decode/refinement0, source/stage/mutant integrity, exit2,
singular exact certificate fatal and no proof entry. Before replay onlyexact_fatal
wasfalse; allother gatestrue. No arbitraryerror recognition added. Remaining32
admissions and all16proof results unchanged. Sameprofile ctor/asptr/14native+Rust
baselines verified in original archived run; archived patch/source/effective tool
identities preserved, not relabeled as a new semantic profile.
[Replay run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37626031885),
[compact replay11483952705](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37626031885/artifacts/11483952705).
Replay ZIP3,851,647bytes (<25MiB), SHA256
b12419118ff31e05dccfa91bded8d6660156018754b2c098b4002ec1020c9d75;
includes original compact S5j/O4 manifest/evidence, original classifications and
separate replay results; no copied tool/library distributions.

Actual integration evidence remains S5k/128dd56/v2/7bb, linked above: full pinned
helper source/MIR/refinement passes; first proof blocker drop_in_place57.
Whole helper return/normal-unwind/leak posts NOT PROVEN. Drop/guard/forget/assume
components NOT ACCEPTED, read-resource hypothesis NOT RUN. Furthersemantic work
FROZEN; current budget retained. RAPx CLOSED/NO-GO, B/C NOT RUN; fullsort4 NOT PROVEN.

## S6 independent matrix and same-profile completion

The S6 entry is `bea6248`; only pointer drop was authorized. Full cumulative
semantic patch is `cd660fe9f470293cc16712a4a71714c8f5f6e802608cedb5b486c3d8a1d27413`,
profile `experimental-source-linked-select-pointer-drop-v1`. The frozen `04d67f4b`
draft was not applied. Exact payload is `*const Element`, receiver
`*mut *const Element`; arbitrary Sized Element, no Copy/Freeze/pointee permission.

The method's specialized non-const unsafe body and the empty ghost identity lemma
are proof targets. The compiler's raw-pointer drop-glue correspondence is a
separate trusted assumption: raw pointer destruction performs no recursive drop,
callback, read/write or pointer reconstruction. It preserves the complete modeled
value and cannot unwind. Proving the lemma does not prove that correspondence;
the recursive free lang-item placeholder is not a proved runtime body.
The rule consumes and returns the SAME initialized typed cell and thread token;
independent resources frame through unchanged separation rules. No Element rights
or ownership bridge are introduced. Full source and typed MIR gates activate the
rule only after checking type/callee/operand/result/all normal+unwind CFG operations.

[Initial S6 run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37637630477),
source `de7ed9de861eea7346301f6807e242862a68c0ab`, collected the complete independent
2-positive/11-proof-negative/22-admission matrix. Both symbolic pointer positives
passed with one or two distinct fractional frames; the unrestricted stored pointer
value includes null. All proof errors were retained, although the first classifier
incorrectly required a SAFE-prototype marker for the unsafe method and used several
inexact normalized messages/locations. Admissions: 16 intended rejections, 3 exact
reason mismatches, 3 setup failures. Those setup failures were not counted as
negative evidence. Constructor/as_mut_ptr/intrinsic complete matrices and all
14 separate Rust/C/C++ baseline controls passed in this new profile. Actual helper
was gated off pending full acceptance.

Initial run cost194s (14:33:07–14:36:21 UTC): previous2398 +194 =2592/5400,
2808remaining. [Compact artifact](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37637630477/artifacts/11490457470)
contains full raw evidence and initial classifications; inner ZIP SHA256
`34a6fba71d964a5ed74298471da4176102fdf3bc747178cadd9a69894d91b232`.
[Full artifact](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37637630477/artifacts/11490457483).

Completion source `dbb70d0ba1f36e7cf6021da319b65234cc890b18` changes classification
and admission setup only, leaving the semantic patch unchanged. It replays saved
13 proof cases and 19 valid admissions, preserves all original classification JSON
bytes and raw evidence, and executes only the three repaired admission controls.
The rebuilt profile must match all original effective tool/spec byte hashes,
compiler/schema/exporter/refiner versions, std-source hashes and patch/spec audits.
Prior component and regression proofs retain their explicit original run provenance.
Only complete composite acceptance permits the actual baseline and exact five-ghost
stock projection variants. [Completion run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37640750987).

The initial method source SHA256 is
`d35858d6b1ec693d5e01b994e2d8248f73c7062c151e75e73ea635456fc82098`;
method body `647ed1904efffba64735cc7d906321846ee11a24b30fbd7cb90ebec9945caac6`,
specialized body `8da3897f4f5c089110d1cfa15b7e246817a51b4e86dad7c654f472bbbd973d2f`;
compiler-glue source SHA256
`325d69d3ce0fef9099f985febc5b712bbdb3563364648adc1396a365699987aa`.
The full admitted method MIR has exactly three typed locals and two blocks:
`bb0: StorageLive(_2); _2=Copy(_1); drop_in_place::<*const Element>(Move(_2))`
with unit destination `_0`, normal `bb1`, unwind `Continue`;
`bb1: StorageDead(_2); Return`. Operand receiver retains its typed full pointer,
not just a numerical address. Mutations cover item identity/input/output/binding,
callee/operand/destination/result type, unwind CFG, contract and extra operations.

[First completion attempt](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37640750987)
cost144s (14:55:22–14:57:46 UTC), cumulative2736/5400,2664remain. Build and classifier
checks passed, but replay module import failed on a missing pair of parentheses
at line144. Replay/new admissions/actual were NOT RUN. This setup failure counts
neither as a proof negative nor as component acceptance. Evidence:
[compact11492611069](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37640750987/artifacts/11492611069),
[full11492226327](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37640750987/artifacts/11492226327).
Retry source `41bb6b651fd2a3eb048fa2fd234fc63812ccaa39` repairs only syntax and adds
hosted Python syntax preflight before the unchanged profile build.
[Retry run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37641538816).

Retry37641538816 cost146s (15:01:12–15:03:38 UTC), total2882/5400,2518remain.
All effective tool/spec/std bytes matched the first proof profile. All13 proof
reclassifications passed. Admission replay stopped at an in-memory tuple versus
saved JSON list comparison in `source_identity`; this was an equality-check harness
bug, not changed evidence. Three new controls and actual helper were still NOT RUN.
[Compact11492831906](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37641538816/artifacts/11492831906),
inner ZIP SHA256 `1567d176eb8bceb65890f8221dd880157a0482444b72310fa911a6a13379960c`,
[full11492801889](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37641538816/artifacts/11492801889).
The next harness repair compares JSON values and collects all independent replay
outcomes plus three new controls before the final gate; it keeps original JSON and
strict stage/message/location/resource/certificate obligations.

### Historical interim S6 checkpoint — dispatch failure later recovered

Source `4d0e3070ca93e01b7a5ccfad18ea83900bc7536b` fixes JSON tuple/list comparison
and collects every replay result/delta plus three new controls independently
before the strict final composite gate. It is published, not executed. Ordinary
push repeatedly returned remote500; Git Data API created the IDENTICAL local tree
`eca47338c16c917e735c313095fb84d10ecb1a89` and commit, then advanced the existing
branch with force=false. Remote ref/fetch confirmed4d0e307. Dispatch via workflow
ID and filename, including exact structured JSON input, repeatedly HTTP500; no
new run appears. No tool/profile/pre/post semantic change, no new hosted job cost.

| Hosted run | Source | Job seconds | Cumulative used | Remaining |
| --- | --- | ---: | ---: | ---: |
| Entry before S6 | bea6248 | — | 2398 | 3002 |
| 37637630477 | de7ed9de861eea7346301f6807e242862a68c0ab | 194 | 2592 | 2808 |
| 37640750987 | dbb70d0ba1f36e7cf6021da319b65234cc890b18 | 144 | 2736 | 2664 |
| 37641538816 | 41bb6b651fd2a3eb048fa2fd234fc63812ccaa39 | 146 | 2882 | 2518 |
| 37642650884 | 4d0e3070ca93e01b7a5ccfad18ea83900bc7536b | 113 | 2995 | 2405 |
| 37645561507 | 85ec1711700ff85c899b18b7e021f076aeddb8e6 | 173 | 3168 | 2232 |
| 37648838042 | 8f1b8f44a655fcfde1fd12106d79dbbb58917332 | 65 | 3233 | 2167 |
| 37649244205 | f6fdf5ba4c3a1bee44bdb3566ab354d1e558fe6d | 69 | 3302 | 2098 |
| 37651717720 | dfc1f1d740689de8f427ac549da558d64a4318eb | 266 | 3568 | 1832 |
| 37654585346 | f1774d54b0d3ced96724b07aba9acfecb51b1633 | 184 | 3752 | 1648 |
| 37656621026 | 75681fbc57bda633f59096cdc28f0c1aa61daef8 | 202 | 3954 | 1446 |
| 37665233357 | 2ba63774e964e2ca76b3b1639e550cb93e70769e | 133 | 4087 | 1313 |
| 37666273705 | 3a4b0e9d375e8871b541ed18e6b340cf152734be | 122 | 4209 | 1191 |
| 37667942855 | f101203bfe5e6100ee2ae60fc0cae62ef7c6149b | 99 | 4308 | 1092 |
| 37669436220 | a5ce1b5f71d2f0a2ecd1f74e44063ba079683b4d | 103 | 4411 | 989 |
| 37675513854 | c9c59a85807da0135a8192b1912b15d510c68028 | 178 | 4589 | 811 |
| 37676357686 (classifier replay) | dd4b0493b8411d92f61f525a3c7ef6ec0429d021 | 12 | 4601 | 799 |
| 37678089113 (AST diagnostic) | a6f077a5aa89ad25df94295320cdbe18ebe4b9d9 | 151 | 4752 | 648 |

Skipped jobs are excluded. At that interim checkpoint iteration484s; no reset, <=1800/job and300/proof.
First run independently collected all cases and accepted-component regressions;
second was syntax setup failure; third accepted all13 saved proof cases at the
identical effective tool/spec/std hashes but aborted admission replay at the
JSON comparison bug. Raw initial classifications, source/run/tool identifiers and
full raw logs/MIR are retained in the original artifact and the later compact
retention report. Fixed code now avoids a first-classifier abort, but its three
new controls and composite acceptance have no hosted evidence yet.

**Accepted components:** existing pointer-value model/SAFE constructor, SAFE
as_mut_ptr and two typed select intrinsic specializations. S6 method/identity
body and proof-negative obligations pass, but **S6 COMPONENT NOT YET ACCEPTED**
until all22 admission controls and composite acceptance pass. The trusted raw
pointer compiler glue is not a Rust runtime-body proof; lemma verification does
not discharge compiler correspondence.

**Actual helper result:** S6 NOT RUN. Last actual S5k result is unsupported method
at `verified/lib.rs(57,9-29)`. No new failure at initialized-cell/provenance/borrow
permissions is established. Its current candidate resources are ctor
`inner==some(a/b)`, two wrapper points-to cells, exact receiver-address equalities
from as_mut_ptr and existing reborrow-end tokens. Stock open projections should
expose payload points-to-option chunks; the remaining untested derivation is
matching their known some states and selected pointer to `*drop |-> value` while
framing the other slot/token resources. Runtime method call and normal/unwind
CFG remain; exact5ghost variant uses only existing open/close+condition split.
A failed projection or selected initialized-cell match must be recorded and
stopped, not assumed or weakened. If drop succeeds, stop at the next actual
blocker. No guard/forget/assume_init/union/refiner/kernel/memory extension.

**Exact next operational blocker:** hosted workflow dispatch HTTP500 prevents the
new3-controls/complete admission gate and consequently actual execution. It is
not an intended negative or a Rust semantic boundary. Next permitted action is
ONE exact current-SHA dispatch after Actions accepts it; monitor and inspect the
complete matrix, then actual only after acceptance. No work is promised after
this session. Current checkpoint is STATUS. Documentation is not a proof run.

### S6v1 acceptance and first actual obligation

[Completion37642650884](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37642650884)
source4d0e307:113s15:17:47–15:19:40UTC, used2995/5400,2405remain. No reset.
Full exact tool/spec/std hashes match original v1 profile. All13 proof cases and
19valid admissions replayed; NEWsource_input/MIRoutput/MIRcontract controls reject
at intended certificate obligations. COMPONENT_ACCEPTED, full35cases. Original
classifications byte-identical under replay/original; per-case correction audit
and all raw original profile entries retained. Constructor/asptr/intrinsic/14baseline
proofs are explicitly attributed to37637630477, not falsely to this completion run.
[Compact11493485379](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37642650884/artifacts/11493485379),
innerSHA256 `4da675062fa21eb2a8a26205ae3fa5bb22a953ed3aaf113bbe53f12060260426`,
[full11493285528](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37642650884/artifacts/11493285528).

Actual baseline fullsource/export/decode/refinement/method/actualcertificates and
redirects PASS. `select_unpredictable` enters and reaches retained runtime drop
call57,14–29. Method req110,55–58 fails:
`No matching heap chunks: points_to<*Element>(__result2, _)`.
This is initialized pointer-cell matching, not unsupported operation. Both wrapper
cells/knownsome states and borrow tokens remain in caller but are not projected.
The exact5ghost stock projection variant exports/decodes/refines, then fails
admission before proof `actual projection ghost source span`; no resource failure
can be inferred. New admission controls are not these setup failures.

Read-only rawMIR review confirms regular annotation high coordinate is final
character inclusive, while explicit effective-parser fields use half-open end.
S6v2 preimplementation rationale0da1e0b checks BOTH exact conventions, changes
only narrow ghost source admission, keeps rawsequence/body/runtime/CFG/posts.
New semantic admission profile needs fresh complete component/baseline proofs and
two independent coordinate mutants before the canonical projected actual proof.
The budget table above continues with run37642650884:113s,2995used,2405remaining.

### S6v2 fresh component acceptance and actual setup reassessment

[37645561507](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37645561507),
source `85ec1711700ff85c899b18b7e021f076aeddb8e6`, drop-v2/8e62e6c3:
full fresh2positive+11proofnegative+22admission matrix COMPONENT_ACCEPTED.
Complete constructor/asptr/intrinsic matrices and14baseline Rust/C/C++ controls
passed at this new profile. 173s15:38:39–15:41:32UTC,3168used2232remain.
Actual baseline keeps same initialized-cell pre110/call57 failure after full gates.
Both extra coordinate controls failed SETUP at the normal exporter invocation;
readonly mutations were successful but second invocation's canonical high differs.
They remain INCONCLUSIVE, not intended negatives. Canonical projected NOTRUN.
[Compact11493408570](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37645561507/artifacts/11493408570),
innerSHA `b160edcd347c02ffafcd94ac0258e805d488bed10a500b64cd3e632b5d8d49ae`,
[full11493098966](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37645561507/artifacts/11493098966).
Pinned exporter inserts32-byte ghostcommand in normalmode; original explicit
parser positions stayfixed. V2 incorrectly used readonly ordinaryghost geometry.

[Normal diagnostic37648838042](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37648838042),
source `8f1b8f44a655fcfde1fd12106d79dbbb58917332`: authenticates immutable v2
fixture/artifact/manifest/toolpins; duplicate error-format input fails BEFORE
compilation/export. 65s16:02:13–16:03:18UTC,3233used2167remain. Classification
DIAGNOSTIC_EXPORT_OR_DECODE_FAILED preserved; no semantic/profile change.
[Compact11496405518](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37648838042/artifacts/11496405518),
innerSHA `5d1bbb3a9e895f73d3801eda20709c86ed0141787188c7ea307e0551388bdfbf`,
[full11496575242](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37648838042/artifacts/11496575242).

[Normal diagnostic37649244205](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37649244205),
source `f6fdf5ba4c3a1bee44bdb3566ab354d1e558fe6d`: effective compiler args/
source/fixture/artifact/tool integrity PASS; export/decode0; no verifier/refiner.
69s16:05:10–16:06:19UTC,3302used2098remain. DIAGNOSTIC_EXPORT_DECODED only.
FullNORMAL actual36locals19BB andfive rawghost/regular/explicit spans retained,
with complete types/callees/operands/normal-unwind CFG. Independent review links
five zero-argument/unit placeholders to frozen stock exporter/translator behavior;
no actual resource proof follows. Exact v3 projected-only certificate cardfaef1a3
precedes code: fullfresh component/regression gates and independent actualNORMAL
admission mutants required before stockprojection proof. No generic graph rewrite
or changed execution/resource semantics; frontend correspondence trusted separately.
[Compact11495097694](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37649244205/artifacts/11495097694),
innerSHA `ead2a0c8a501becdbf0bbcf6c521d356a3457fb232f5e5a4b09793a618e2c093`,
[full11495657034](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37649244205/artifacts/11495657034).

V3 completion budget:37654585346/f1774d5,184s16:45:53–16:48:57UTC;
3752/5400used,1648remain. Compact11498401742/full11497209013. No new budget.

S6v4 final evidence37656621026:202s17:07:34–17:10:56UTC,3954used1446remain.
Fresh full component/regression matrices+19NORMAL intended controls accepted.
Projected fullsource/refinement/method+36/19 admission and redirectPASS, retained
runtime drop+stock reclose prefixPASS; next forget guard-own req420/call63 failure.
STOP, no broader changes. Rawclassification unchanged; no helper/sort4 theorem.
Compact11500295662, full11500150817, compactinner SHA256
5ed34fef59d69e3f766186952338c44a09b5016e5caa0e2b601fe0b0b184a549,
manifest5177/5177 hash/CRC/sizeverified. Effectiveconsole
799fac7491db7d43e786713ae4ff75427d7e77c227fb4f7438e433b297514cd0.
