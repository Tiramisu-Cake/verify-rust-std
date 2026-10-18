# Select/sort4 OCaml buildability session

Task select-sort4-ocaml-buildability-2026-10-18-r1, direct owner invocation of
CURRENT-TASK.md. InitialHEAD/remotee3837f4110f8713d00ba2e0f4bb7284b578831ae.
Owner select-sort4, assigned research/night-select-sort4-cloud-2026-10-09.
T0 2026-10-18T18:59:16Z/main20:59:16Z/absolute21:29:16Z.
WORK-POLICY at e3837f41 plus existing owner Evidence Brief policy2026-10-17 read;
eight unrelated owner policy/docs edits preserved and excluded from commits.

Sequential within-scope code fixes/Builds authorized until main deadline, not a
one-Build or960/3600s cap. New phase SORT4-A1-OCAML-BUILDABILITY-2026-10-18-R1.
Own ledger BUDGET-A1-BUILDABILITY-2026-10-18.json uses existing numeric registration:
technical18960s=150*60wall9000+9000rounding headroom+960final reservation. This
represents the time authorization, not an extension; hard main/absolute cutoffs,
max900s per Build and one occupied/unresolved own Build remain enforced. No carry.
Existing coordinator protocol unchanged; phase admission additionally enforces
owner's max2 project occupied slots under existing coordinator lock, including
untracked live Builds. Original reservations/unresolved/accounting code unchanged.
Old405/960+555retired,433/960+527retired and all old ledgers remain byte-preserved.

## Baseline evidence refresh

[New ordinary Brief for7987e81f](A1-BUILDABILITY-BASELINE-BRIEF-7987E81F-2026-10-18.md)
adds actual D.rvalue / expected string at translator6884. This expected-type
information no longer needs admin access. Original Brief/checkpoint observations
remain historical, not overwritten.102/102 records captured, no omissions, but
orderNOT_ESTABLISHED,last stageUNKNOWN. console-buildexit0 is an individual record,
not proof of new R-only reference success. Combined R-onlyexit2;26source-reported
NOT_RUN; no formal credit. Integrity remains distinct from proof acceptance.

## R1 hypothesis, domain and outcome decisions

Minimal expected-type annotations repair record-label/constructor disambiguation:
`check_type scope (ty : D.ty)` and ADT lambda `(arg : D.generic_arg)`.
Schema Ty.kind:TyKind; GenericArg.kind:GenericArgKind; Adt.substs:List(GenericArg).
Callers supply D.decode_ty, ref.ty, Slice/Tuple members and GenericArgKind.Type.
Unannotated qualified kind can select the latest same-labelled string field;
D.Ref is also an overloaded rvalue constructor. Annotation selects intended schema
types without changing any arm, refusal, traversal, region or binder identity.

Reviewed all R-added OCaml: normalize_required_ty already types D.ty and returns
D.ty; normalize_required_arg already types D.generic_arg and local generic_arg_kind.
Clauses are decoded by D.decode_clause and match unambiguous clause constructors;
record/collection fields otherwise have typed producers and consumers. No blanket
refactor or other speculative annotation. Two old unused_mut removals retained.
Preservation is source evidence, not successful compilation.

Actual obligations/domain/posts remain original R/C/G/26-row experiment in
A1-RCG-SEMANTIC-GATES-2026-10-17.md: common threshold post16<=result<=32 for actual
default/Freeze bodies/conformance, unrestricted generic T, original comparator F,
three borrows/HRTB/FnMut/Output=bool, full native normal/unwind/safe contracts.
No supplied length bound, Copy/Freeze/nonzero/no-panic restriction, runtime/std,
compiler/decoder/dependency/schema/exporter/kernel/prelude/refiner/G change.
P1 remains complete interface mapping; N-false31 requires own pair bodies,
conformance,receipt issuance and caller assertion order. No old receipt substitute.

R1 source-only base→43pre-R→new fullR→unchangedC application PASS; exact source maps
in A1-BUILDABILITY-R1-SOURCE-CHECK-2026-10-18.json. New R differs by exactly two
annotations from preceding R. Frozen semantics/schema/exporter/R-before unchanged.
6 isolated synthetic service checks validate exact new account, arbitrary sequential
Build count admission,900s limit,main cutoff and original-protocol env. No local
compiler,decoder generator,extraction,refiner,verifier or proof runner executed.
Luna HIGH review and committed closure/config preflight required before submit.

Each full Build: fresh R-only exporter/console and own receipt,final C,unchanged26.
Compiler failure→Brief diagnosis and next justified compile-only fix in scope;
verification/admission error requiring semantics/contract changes→owner question,
no expansion. Reporting gap→audit request only,no unchanged rerun for bypass.
Positive complete evidence→record bounds/fullproof distinction; A1/A2 not automatic.

## R1 committed release

Candidate proof/infra`ff7fbd1daa9b89f74ec79c313ad27f6bd80f5b53`; Luna HIGH GO, full committedclosure/configPASS.
[R1 release](A1-BUILDABILITY-R1-RELEASE-2026-10-18.json),
[review](A1-BUILDABILITY-R1-REVIEW-2026-10-18.md).
{"commit": "ff7fbd1daa9b89f74ec79c313ad27f6bd80f5b53", "config_arg_bounds": "PASS", "dispatch": "NOT_ATTEMPTED", "exact_restore": "PASS", "formal_credit": false, "phase_profile_environment": "PASS", "restored_paths": {"infra": 33, "proof": 107}, "shared_objects": 160, "source_payload_bytes": 505400, "source_sha256": "ea4cbff90b19db1f5651bc16b4d0a721fec0445bac2c838670a83c68c19eda07", "source_substitutions": 169}

## R1 submit

Published8e896966f8208bb32d96718acdc4566cbbbbfe29 before submit;
Build92524a3d-fec8-4e74-a902-271f791e8bb7,token
dispatch-746a521760aa46988240b2a0c0059716;config
85b7b631a7a52c2d602f56305aa5f6bd1a5714d95611dc62b425c98514393f6e.
Full R-only→C→unchanged26;900timeout+60reserve;terminal evidence pending.

## R1 terminal and R2 build-assembly hypothesis

R1 Build92524a3d-fec8-4e74-a902-271f791e8bb7 FAILURE,415charged/414execution.
Brief names R-only reference stage exit0 and final schema/exporter/console stage
exit0. This establishes successful named combined build stages, not proof. Own
fresh reference receipt is required between them by pinned flow, but receipt
contents/hash not independently exposed in Brief. R1 compile blockers no longer
block these stages.108/108 stage records; stage order/last stage still UNKNOWN.
P0a normal-export/readonly-export/refinementexit1,unclosed delimiteroriginal/lib.rs156.
No per-row verdict inventory in Brief; P0a setupfailure observed,other casesUNKNOWN.
A1/A2 open,no formalcredit; no NOT_RUN inferred from absent records.

Static constructor inspection shows `_observer` combines function-opening signature
with loop/if-opening guard prefix, then suffix literals with only2closingbraces.
Both P0c and N-false31 need a third final function delimiter before original P1
caller. `_p1_caller` has correct balance because full guard alreadyclosesif.
R2 repairs just these2literal delimiters, as minimum related build-assembly syntax
fix authorized by task section2. No assertion,cut,pre/post,negative,target,caller,
std runtime,G/C semantic change. No local fixture/source extraction execution.
R/C fullpatch bytes unchangedR1; new helper/profile/source identities required.
Hypothesis: compiler accepts both constructed observer declarations, then runs
unchanged source-support/AST/proof gates. Further in-scope compileerror→continue;
semantic/admission error→separate owner decision; reporting gap→audit not rerun.

## R2 committed release

Candidate proof/infra`28cd86597b07e6c2726cf1c391cfdfbd28997a98`; Luna HIGH GO, full committedclosure/configPASS.
[R2 release](A1-BUILDABILITY-R2-RELEASE-2026-10-18.json),
[review](A1-BUILDABILITY-R2-REVIEW-2026-10-18.md).
{"commit": "28cd86597b07e6c2726cf1c391cfdfbd28997a98", "config_arg_bounds": "PASS", "dispatch": "NOT_ATTEMPTED", "exact_restore": "PASS", "formal_credit": false, "phase_profile_environment": "PASS", "restored_paths": {"infra": 33, "proof": 107}, "shared_objects": 160, "source_payload_bytes": 505755, "source_sha256": "f5e75e6817eae9b607ccd9dab2facb32f4f40473a68f0e54d6cea09a20da5006", "source_substitutions": 170}

## R2 submit

Publishedda099c42a791a78572ee78b3b7c6f5f127b05aed before submit;
Buildae9fd22f-a143-4a4f-9d7c-2911ec1ad042,token
dispatch-c4940b8f3076485ebddf602872bcd205;config
06fe4403335574cef498ae2576a4067a16dc35fd1941867e0cbad412989242a4.
FullR-only→C→26,900s timeout,sameauthorizedsession,415accounted+960reserve.

## R2 terminal and R3 header hypothesis

Buildae9fd22f-a143-4a4f-9d7c-2911ec1ad042FAILURE,401charged;session816s.
Brief names both R-only andfinal-Cbuildsexit0. P0asupportfailsnormal/readonly/refinement1.
Refinement diagnosticunknownfeatureinternal_features atoriginal/lib.rs1:53,
logsha a2701cdb50651f0c9ab18aaa6e98ab33b861f6fc9c0d2f56460981f69ab0faa9,line21.
No per-rowverdicts exposed; otheroutcomesUNKNOWN,notNOT_RUN. Noformalcredit.

Staticfixture rootheader mistakenlylists internal_features as a languagefeature.
R3 removes onlythat unsupportedtoken,retainsfreeze/min_specialization/rustc_attrs/
core_intrinsics andexistingwarningspolicy. Noallow-lint,check,deps/compiler/version,
runtime,std,contract,G/C/domain/lifecyclechange. This is minimumbuild-headerfix.
R/CbyteidenticalR1;43pre-R/R/Csource-onlyreconstructionPASS. Nofixtureconstruction,
sourceextractionorcompilationlocally. Hypothesiscompilerpassesheaderthenunchanged
fullmatrixcontinues;runtime/admissionsemanticblockerrequiresownerdecision.
