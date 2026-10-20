# R9 session — native interface proof registration

Session: `select-native-interface-proof-autonomous-2026-10-20-r9`; owner
`select-sort4`; branch `research/night-select-sort4-cloud-2026-10-09`.
Authorization is the explicit `CURRENT-TASK.md` assignment. T0 is
`2026-10-20T17:07:04Z`, main deadline `2026-10-20T19:07:04Z`, absolute
deadline `2026-10-20T19:37:04Z`; ceiling 3600 Cloud seconds, used 0, carry 0.
Lane: `o26-sort4-c1-current-recovery`; phase:
`SORT4-NATIVE-INTERFACE-PROOF-2026-10-20-R9`; timeout ceiling 900 seconds.

## Defect, applicability, and rationale

R8 is closed and its phase, profile, deadline, and ledger must remain historical.
The R9 assignment authorizes a fresh 3600-second window and a new phase. Current
transport and consumers accept only explicitly registered phases; reusing R8
would bind the run to expired authorization and would not establish R9 identity.
The R8 transport/entry/adapter/focus-helper/core-consumer/recipe pattern is the
applicable registration model. Register R9 as a distinct exact profile and
dependent closure while retaining existing guards, source-core byte identities,
environment equality, protocol checks, accepted=false rejection, focus/dead-code
controls, and baseline→overlay→C source transitions.

The candidate source repair `8e46fbf4c603e9a0133d3024ce22e73958d73542`
qualifies four accesses as `Ast.sized` while preserving predicates and control
flow. It is applicable to the prior R-only compile failure, but actual
compilation, extraction, and verification remain NOT_RUN. R9 registration does
not change proof semantics, runtime std, tool semantics, native contracts,
equality/refinement criteria, or proof credit.

## Distinguishing controls

Run only synthetic/static registration and service tests locally: exact R9
success plus wrong/unknown/old/missing/null/bad-type/hash/path/environment,
protocol/core mutation negatives, and runner success/error/NOT_RUN/partial
preservation. Check dependent pins and complete recipe closure against committed
files and hashes. Do not import the real proof core in isolated activation tests.
Independent review of the current diff/dependencies and the existing Cloud
preflight remain mandatory before any coordinator submission. These controls
establish registration integrity only, not source applicability or proof.

## Checkpoint

At activation, proofs remain at the R8 baseline: 0 formally closed obligations
and 0 independent B1/B2 credit. Actual candidate compilation and verifier are
NOT_RUN. Registration work, any later Build charge, and proof progress are to be
reported separately. Historical R8 ledger and releases remain untouched.


S1 candidate `c73930175ade6efffc82c6f70a5e2d803fdc872d`: independent GPT-6 Luna HIGH GO against be82ac4, no current registration/dependency findings. Synthetic checks: activation8/dispatch7/profile9/action3/progress4/focus7 PASS. Initial exact payload rejected unsorted recipe proof_paths before dispatch; canonical sort fixed and reviewed. Exact committed Git closure PASS:37infra/114proof/171shared objects,529005bytes,186config substitutions,sourceSHA185835f290f28cfd66a7cc0ee01f6fe9a1a2c678ff24930373e4b9701e014ddd. Profile ffdcf3f410055c4cf63ccd264d52dd3dd7a2df54383342ecdb9c833c097ad104. Two known gitmodulesMissing stderr observations with restore exit0; selected bytes/HEADs checked, no full-repository fsck claim. Mathematical source/compiler/std/tool/patch/core/matrix identities equal to R8 corrected candidate; actual compilation/target NOT_RUN until Cloud. Timeout900/envelope960 planned within fresh3600.

S1 accepted Build `2f7b5d56-f9b6-44d1-a1fd-89f7b79870a4` on exact proof=infra `c73930175ade6efffc82c6f70a5e2d803fdc872d`, config3fef71ed3106d66f15c29011b6db2c8a6e6e4207f1d2c6e8407529ffb79674d9, token dispatch-b5414610b74f470db8fba299ae233d1a. Published remote head96268a88d85c3f9b0b5574ad0e2847703e88d106 includes exact candidate; coordinator admission passed. Mixed setup/proof hypothesis: qualified Ast.sized compiles both R-only/finalC and enables compiler-bound native P1/equality controls. Timeout900/envelope960, fresh used0, ownactive1; no duplicate.

S1 terminal FAILURE905s; total905/3600spent2695remaining/ownactive0. Brief VERIFIED_ARCHIVE_AND_INVENTORY, outerevidencecomplete true, source runexit124. Exact26 source progress:11INTENDED_CLASSIFIED/2INCONCLUSIVE/12NOT_RUN/1OBSERVED(R7), not final matrix acceptance; noformalcredit. P0a/P0b source NATIVE_INTENDED_PASS body+conformance currentidentities. P1 R-only frontend error compiler item body is not unique; independent caller binding normal/readonly semantic mismatch. Ownfalse31 body stage events verifier0, no receipt/callerassertion. S1-EVIDENCE/MATRIX and bounded Reader responses retain exact coordinates/index/archive/requestIDs. JSON25MiB structural limit addressed with scoped text windows; transient auth timeout retry succeeded/no rawfallback. S2 narrow body=Some selection candidate, binder actual representation investigation ongoing.

S2 runtime candidate `38ad79803c5e55bc12c3d848cdbf1ba3a889b39a`: independent Luna HIGH GO native Some-body selector and mismatch-only diagnostic/dependent profile. Exact equality and fail-closed zero/multiple definitions preserved; cause of caller mismatch still unknown. R-only894bfe9032a19caef1370a563be1c8c9ea09a06bcdf51061f5b1d60b60c37c0a→unchangedC d69dd8c87093ebdce275c61b718d339b4425da6a6d97ebd866e36c1724d680dd; profile2f68c4916325ccc132bb67b8e1f764a87c643a18cd3634733d01903cd9749581; helper2db4ada728e2d076500a1f92777ed1519068dac996e81db3840fc29c6a8bd771. Source-map5/profile9/callbinding22 PASS; test-only309808b9 addresses reviewer early-mismatch gap using leaf-onlydepth80case, production unchanged and whole3000bytecontract retained. Exact Git closure37infra114proof171objects530326bytes187substitutions/source37599a30185b9bf58d69fd54a00f506082744ef0328f9aa80291a8c3cd905af3 PASS. Known2gitmodulesMissingstderr/restoreexit0/selectedclosureverified/notfullfsck. Timeout900/envelope960 fits2695remaining. Nextmixedproof target nativeP1 plus exact failingpair diagnostics, no speculative comparator weakening.

S2 accepted Build `62675952-19c6-483b-8770-28992e68b640` through coordinator on proof=infra `38ad79803c5e55bc12c3d848cdbf1ba3a889b39a`, configa98fe7adbb40d5c7db56e49e856b3d9a6e559902e3d5aa94cefb2668af8c1514, tokendispatch-ad9e82993a4841c5a5f1f2536595e678; publishedremoteHEAD60d750c377701e1e135e9f50e983b81a23a66d5d verified. Timeout900/envelope960/prior905spent2695remaining, ownactive1. Native actualcompiler-bound definition selection and P1 target are distinct new hypothesis; unchanged strict caller equality gains only bounded faildiagnostic. Actualresultpending/noformalcredit.

S2 terminalFAILURE863s, total1768/3600spent1832remaining/ownactive0. Brief VERIFIED_ARCHIVE_AND_INVENTORY/source run0/outerdeliverycomplete. Canonicalaudit2606668bytes/original32254654bytes; sourceaccepted/evidencecomplete/matrixcompletefalse. Exact26source12classified2inconclusive12notrun; noformalcredit. NativeR-only actualnew894bfecompiledexit0 butsamebodyisnotuniqueerror persists; Someonlyhypothesisnotresolved. Exactbindingdiagnostic callerquicksortcaseP1/callsargument_region_roles tuple slot2 IDs differs; normal3bf1...readonlyd57c... matchesactualbaseline. Main fullP1 syntheticreproducer failsbeforetwo-line tuple recursion andpassesafter; observeralphacase preserved,22testsPASS/LunaHIGHGO. S3 independentlyusefulactualbindingregression plusboundednativecandidatecount/locationdiagnostic; sourceclasscollisionnotguessed. Hourprogress1768spent0formalcredit, remaining1832 and main19:07:04 unchanged. S1 individuallymeasuredRonly97.11s/finalC11.13s, nofullsetup/proofdurationinferred.

S3 candidate `a8bc59bef4bb494d5ad3ebd44f482c1264315d0f`: independent Luna HIGH GO tuple-preserving alpha recursion plus bounded lazy native candidate diagnostic and all dependent pins. ActualS2 diagnostic confirms fields/inputhashes; nativecollisioncauseunestablished/selectorunchanged. R-onlyff9c4f7217bbca25975bb94a08df1ee705d506a248a06ad2da504adb25ff4889→unchangedCdad5857cdc204cbd93e9311c0cea91b1016485194324dbe000c3f3bdd59f0848; helper0e6d606bf434cee9973d2eb0c687e5942bd900e92f18976f5687c933cb2d6e74/profilef4168cd79a0259511df69ed1648425ce04dac2b973dddbd29b3e0caea221fc9a. Source-map5/profile9/binder22PASS; observer/P1alpha cases preserved and real mismatch negatives retained. Exact Git closure37infra114proof171objects531023bytes187substitutions/sourcea80b1e0af9e1bdd95bd2665805a105eaa6b749fdaec2fbca8dd4c56f06058c97PASS. Known2gitmodulesMissingstderr/restoreexit0/notfullfsck. Timeout900/envelope960 fits1832remaining; proof/actualbinding notcredited before Cloud.

S3 accepted Build `0b3c2c0a-4b3f-4df6-8e58-8de4d346b08a` through coordinator on proof=infra `a8bc59bef4bb494d5ad3ebd44f482c1264315d0f`, config1ea6aeaaec3496e1a57d2759395ff20412588caed31f45a987491c72d662e189, tokendispatch-8d36826d9a2144ba9b59ddaeab84a0ad. PublishedremoteHEADcb413f8168b00f8caf29e912a35756ea6b6b1e4c verified. Timeout900/envelope960/prior1768spent1832remaining/ownactive1. MixedactualP1callerbinding/independentcontrols + boundednativecollisiondiagnostic; notunchangednativefailure retry. Actualresultpending/proofcredit0.

S3 terminal FAILURE647s (finish18:23:33.184323Z), total2415/3600spent1185remaining/ownactive0. Public metadata executeSUCCESS/package-uploadFAILUREexit1/verdictFAILUREexit2. Brief and package-upload-error catalogue both HTTP404: Reader report or query route unavailable. Exact missing sizes/primary_error requested from owner; no raw audit or fallback. All26 actual results UNKNOWN, not inferred NOT_RUN; tuple acceptance/native diagnostics unknown, formalcredit0. S4 lossless R9-only row-pointer serialization addresses source-proven duplicate observations while retaining full observation_details/nonmatrix records; S3 cause remains UNKNOWN.

S4 independent Luna HIGH GO for lossless report view and dependent core/profile pins. Serialization8/profile9/progress4/activation8/dispatch7/action3/lifecycle4/context4 PASS; reviewer independently serialization8/profile9/progress4. Retained observation_details is canonical within report; row observation_ref points to it, nested Reader queries must follow pointer. Cloud preflight unchanged; actual source claims and packaging pending.

S4 candidate56e85571952e5b895f0bad465903e2dd0688b11a exact Git closure PASS:37infra114proof171objects531833bytes187substitutions; source6d64efc2952e18926e413cb8bdb385dc9b11b694e49084ea4e2f3c0fd1b0bd3c. Known2gitmodulesMissing stderr, restoreexit0, selected byte comparisonPASS/notfullfsck. Corea45c9c74b8f63354f6342a3f00e317e2eca980a44fe4a2715fc2e242d88ba555/profile75a2bc314f5267dbfaa4dfffd10b3edd5ac8bb40e5ce0645547ca9e495ca8f8c. IndependentLunaHIGHGO, timeout900/reserve960 fits1185remaining.
