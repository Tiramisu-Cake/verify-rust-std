# Concrete CopyOnDrop compiler glue: bounded implementation contract

**Status: NOT_IMPLEMENTED / NOT_PROVED / NOT_FOR_INTEGRATION.** Merge owns the
tool and proof work. This note is a static implementation boundary, not a new
phase, permission, proof result, or transfer to the VeriFast maintainer. It
uses the accepted policy revision `c7ca8c467aecf10a4b53039372ee97714f854ee3`
and the active experiment card `GLUE-NEXT-EXPERIMENT-20261011.md`. The existing
selected-drop profile `803abaa5` and observation profiles remain experimental.

## Compiler facts and first prerequisite

The first pinned x86_64/nightly-2026-09-25 observation in Build `854d9fb5`
shows `Shim(DropGlue(core::ptr::drop_glue, Some(CopyOnDrop)))` with the sole
concrete argument `CopyOnDrop`. Its generated MIR has input `_1: &mut
CopyOnDrop`, `_2 = copy _1`, one trait `Drop::drop(move _2)` call with normal
target `bb1` and `unwind continue`, then `bb1: return`. It has no `Rvalue::Ref`,
borrow-end or `StorageDead`. The raw trait-call `FnDef` does **not** itself name
the local destructor. The observed `FnDef` arguments contain a late-bound
region; the ordinary exporter currently rejects them at `no_bound_vars()`.
These are observations of one generated body, not proof of its call binding.

The next observation must resolve that exact call, with its exact type arguments,
to the same local `CopyOnDrop::drop` DefId/hash and checked source body in the
same compiler invocation. A subsequent attempt in Build `96248554` compiled
the observer but stopped during extraction when its late query tried to steal
an already stolen selected-method MIR body. Repair query order or cache the
needed identity before stealing; preserve the raw binder and generated MIR.
Until the resolved instance is observed and matched, do not implement the
semantic lowering below. An API/pipeline failure is setup evidence, not an
intended negative.

## Smallest tool boundary after the prerequisite passes

1. Append a tagged generated-instance descriptor to existing Cap'n Proto
   `Body`, and an exact reference to it on `DropData`, keeping existing field
   ordinals. Bind `InstanceKind::DropGlue`, concrete guard type and arguments,
   glue DefId/path/hash, selected local destructor DefId/path/hash, caller place
   type, compiler/target, and the one normal/unwind CFG. Generic glue DefPathHash
   alone is insufficient because multiple concrete instances share it. Require
   exactly one matching generated body and one matching checked local method in
   each exported unit; reject mismatches, duplicates, projection, replace, or
   unsupported fields. The only admitted guard has two raw-pointer fields and
   `usize`, concrete `u64`, x86_64, and caller-derived `len == 1`.
2. Export the actual `instance_mir` through reused MIR local-declaration and
   basic-block encoders. Do not pass it through HIR-dependent `encode_body`:
   that code expects a local HIR DefId, `fn_sig`, generics, body/contract spans
   and annotations. Pre-collect the unique instance before `fill_bodies` and
   before any query ordering that steals the selected method. Give its `Body`
   a private deterministic name derived from the structural instance and
   `generated` tag, MIR-derived `&mut CopyOnDrop -> ()` signature, no generic or
   ghost declarations, and a real compiler span only for diagnostics. A narrow
   generated-body-only `FnDef` encoder may erase the observed bound region for
   typed export, while retaining raw binder and resolved callee identity as
   admission evidence. No global `FnDef`/region rule changes.
3. Translate the tagged body as a **private checked function**, reusing the
   ordinary MIR block translator. Its formal `_1` is named `self`, matching
   the selected method's parsed explicit strong contract. Reuse that contract's
   `req`, full normal `ens`, and literal `on_unwind_ens false`; omit only the
   method-specific canonical `safety_proof` clause on the private glue body.
   The method's own canonical safety proof remains independently checked. This
   is a verified implementation contract, never a declaration without body or
   an assumed/generic `drop_in_place` summary. Bind the generated trait call
   to the *observed resolved local instance* before making the AST call; the
   general trait specializer's ignored predicates or path name alone cannot
   justify the binding. Preserve the generated call's normal target and
   `unwind continue` in `fn_outcome` translation. Only a compiler-synthetic
   empty Resume continuation may receive synthetic location treatment; real
   source dead-code reporting remains active.
4. At the caller's qualified MIR `Drop`, keep the already tested physical
   guard packing and linear receiver protocol: `close_points_to(g)`,
   `create_ref_mut(g)` producing receiver `r` plus exact `ref_mut_end_token(r,g)`,
   call the checked private glue body with `r`, then on permitted outcome
   `close_points_to(r)`, `end_ref_mut(r)`, `open_points_to(g)` before caller
   `StorageDead(g)`. The generated MIR itself creates no reference or end token;
   do not insert one there. The external source quarter, destination gap,
   CURRENT owner, `type_interp`, thread token, geometry and readonly end/lifetime
   resources come from the existing caller ledger. No origin fixedpoint,
   full-borrow/FBC, or end-token premise is added at caller entry.
5. Update the **official** refiner's generated-Body path: original and verified
   must each contain exactly one structurally corresponding tagged body; always
   run `check_body_refines_body`, bypassing the ordinary source-snippet equality
   shortcut. A missing private verified body is a failure, even though ordinary
   restricted HIR bodies may be omitted. Do not add the generated core span to
   the source checked-range list. Because the existing refiner does not inspect
   call/drop unwind edges, add a separate exact two-block structural gate for
   all generated locals, types, statements, rvalues, call operand/arguments,
   substitutions, normal and unwind actions, and return. Normalize only source
   spans and separately bound cross-crate identifiers; bind hashes **within**
   each export rather than requiring equal raw DefPathHash across crates.
   Build and pin the changed official refiner binary in Cloud on the new
   experimental profile; old binary `b049` remains historical evidence.

## Acceptance and refusal

Required fresh Cloud gates on the exact new profile: source/verified source
SHA, compiler/target and concrete layout; raw generated Instance and resolved
callee identity; complete original/verified export and official refinement;
strict normal/unwind structural comparison; AST private body and exact selected
method call; same-unit checked actual method with dynamic `self.len` and its
canonical safety compatibility; caller one created/consumed mutable token;
full CURRENT/source/destination/owner/thread/field/padding normal post,
return/free/leak; pre/post-call nonvacuity; source dead-code negative; mandatory
normal and unwind smokes. Retain negatives withholding usable guard frame or
source quarter, wrong/missing instance or selected body, wrong/omitted
borrow-end, duplicate full effect, and repeated destructor, each at its
intended obligation. A setup, export, decode, unsupported-call or unrelated
failure is not an intended negative. The original caller's comparator-panic
cleanup remains a separate obligation even if this bounded normal glue passes.

Any need for a general alias/kernel/model rule, generic `T`/ZST support, a
weakened unwind/post/resource check, or source-generated helper in place of
the compiler body is outside this contract and requires a new owner decision.


Parent integration note (2026-10-11): observer v3 Builda6ee2fbe compiled but extraction failed by re-querying stolen method MIR. Observer v4/tool54407e62 reads exact DefId from already-owned source MIR, explicitly labels mir_drops_elaborated_and_const_checked and keeps resolved concrete substitutions separate. No instantiated-method MIR claim; selected source body still checked in the same unit by existing campaign. Implementation remains NOT_IMPLEMENTED pending fresh binding observation. Parent owns subsequent glue/receiver/end/cleanup; this note does not transfer development to maintainer.

Addressed future controls must mutate only candidate-specific receiver finish after checked glue: omitted end keeps created token and cannot recover physical g before StorageDead/free/leak; wrong end uses a distinct receiver and must fail on the exact linear ref_mut_end_token before physical restoration; post-retirement replay must ask for a second full normal effect using the same initial resources after their unique receiver/storage retirement (no freshly supplied tokens or receiver premises). Compiler setup or unrelated dead code failures are not these ownership negatives. Each control requires its own source/MIR/AST predicate/location and same-profile positive baseline; until implemented and matched in Cloud all three remain NOT_RUN.

Final observation v4 Build2d88c92f-e721-4cfe-9eee-4c0aa1846903/dc42741245002c010c4e27554003a7ba4e28d1bf FAILURE349s, create15:57:37.912198503Z/start15:57:38.611801784Z/finish16:03:26.686660Z. Full archive59a5e1881da1a1596a18501e2a1a6bbc7b63d370cac7a205389ff3778facd894 plus config/source/inventory/index/allchunks integrity verified. Exportercompile E0425 atsrc/lib.rs2820: exported_bodies undefined in encode_terminator_kind; new owned-body argument reached encode_body but was not threaded through basicblock/terminator helper chain. Decoder/translator/console/extraction/observation/consumerproof NOT_RUN onv4. Static hashes/closure passed, compiler validity did not; no credit transfer and no semantic change implemented. Candidate54407e62 is a preserved non-buildable draft, not ready for maintainer integration.

Session CLOSED after main. All5Cloud Builds terminal/accounted/downloadverified:377+456+531+477+349=2190/3600;1410unusedretired/no carryover, prior314retiredunchanged. Ownactive/reservations/unresolvednone, ownturnrequestwithdrawn, peerstate untouched. Originalv4selectedprofile and historical manifests/verdicts/failures/suppliedpremises preserved. Observationalprofilev2 has freshboundedcomponent PASS and42actualrawglue observations; resolvedcallee binding still unavailable, generatedglueproof NOT_RUN. Newend/retirementcontrols and reachableactualcallerpaniccleanup NOT_RUN. Development remains merge, maintainer compatibilityreview only. No automaticnewsession/newexperiment orprofileacceptance.

Next within-scope action after explicitnewsession/budget: thread exporter-owned body view through full encoder callchain (or exact immutable EncCtx view), statically trace each argument's scope before Cloudcompile under separatelypinned newobserverprofile; require resolvedcallee==adt.destructor and exact captured sourcebody before taggedactualglue implementation. Then body-v1 officialrefiner/strictCFG and receiver/end gates, then sourcebound latepaniccleanup. No generalkernel/memory/alias/genericT/ZST expansion.

Binding v5 Build12a54039/d74a50c8 SUCCESS511s/fullarchiveb283c431 integrityverified incl allchunks. Exporter/decoder/translator/console exits0; selected7/helper4+normalunwindsmokes freshv5PASS_COMPONENT_DIAGNOSTIC. All42 rawobservations wholeInstance equality true for Item(adt.destructor.did) args[], exactcapturedowner Runtime(PostCleanup), glueRuntime(Optimized). Capturedsourcebody not instantiated; concreteargs separate. Generatedglue stillNOT_RUN. Budget511used/3089remaining.

## Body-v1 exact implementation gate after confirmed binding

Prerequisite is now observed onv5, not a glueproof. Tagged descriptor appended atBody27 plus capturedowner hash/phase28/29 and DropData generatedkey8. Descriptor binds actualShim DropGlue concreteguard args, rawtraitbinder, exactresolvedItem args[], sameunitmethod DefPathHash/capturedsourcehash/phase, receiver type, normalbb1/unwindContinue. Unique privatekey __vf_generated_drop_glue; non-generic concreteu64 localguard only. Main owns exporter; delegated translator and officialrefiner have disjointfiles and this exactcontract. No borrowedmethod MIR requery. Rawtrait typedexport boundregion erasure only inside structurally admittedgeneratedcontext; rawbinder retained. Strong parsedmethod req/fullnormalens/on_unwindfalse reused only as checkedprivateglue contract; canonical safetyproof stays on actualmethod and omitted onglue. No inventedMIRRef/StorageDead.

Officialrefiner requires unique generatedpair, exact2block4localcopy-call-return shape plus normal/unwind, sameunitmethodhash+capturebinding, and always check_body_refines_body; no snippetshortcut/generatedcheckedspan. Refiner rebuiltCloud withsource/binaryreceipt onbody-v1, oldbinarypin historical. Callerlinearcreate/end remainsexistingresourceproducer; no suppliedpremise or permissionfromaddress. Affectedgates freshselected/helper+mandatorysmokes, source/verifiedextraction/refinement/privateAST actualmethod dynamicself.len/CURRENT/fullposts/returnfreeleak, required missingpermissions/nonvacuity/duplication/end/retirement/deadcode controls. NewprofileNOT_ACCEPTED. Unsupportedshape/refiner/API/setup refusal doesnot countnegative. Kernel/memory/alias/genericT/ZST expansion remainsoutside.

Static controls review after body-v1 pin (NOT_IMPLEMENTED/NOT_RUN): exactgeneratedcaller finish closesreceiverpoints, end_ref_mut(receiver), opensphysicalguard; sharednormal/unwindarm. Omittedend removesonlyendcall and mustrefusephysicalreopen withlivecreatedtoken afteractualgluereturn. Wrongend mustrefuseexactref_mut_end_token at end_ref_mut(address), withoutnewreceiver/token orpermissionfromaddress; othermissingpreconditions remainINCONCLUSIVE. Retirementreplay mustcallsameprivatecheckedglue usingstalesyntheticreceiver onlyafteractualguardStorageDead/free_locals andfirstcall/end/physicalrestore, preservingoneactualnormalMIRDrop/refinement andwithoutrecreatedreceiver/restored/suppliedresources. Ifpostretirementinsertionnotisolatable, keepNOT_RUN. These are candidate-specific diagnostic lowering variants requiringnewexactprofile pin andfreshpositive; noautomaticcreditsfrombody-v1. Actualcleanup stillseparate.

Body-v1 Cloud build b48cd6eb-033b-430f-b4a4-90fbbcbcabe8 startedfromf6b62c0e04f84b21096257f4ac4bf5e7cb6ee6b8 afterfullinput transport correction. Tool/profile semantics unchangedfromdbbba0d3/8b79e83c. No terminalbuild/refinement/proofclaim untilfullverifiedevidence.

## Current prepared candidate and next gate

The body-v2 exporter, decoder, translator and console compiled in Cloud; the official refiner build stopped because two existing synthetic Drop records lacked fields from the expanded schema. The [V2 receipt](GLUE-BODY-V2-RESULT-20261011.json) preserves that setup failure. No extraction, refinement or generated-glue proof ran.

Body-v3, tool `853fd1e2edb309101df83b93c65572a0d8d0d189`, only supplies empty qualification fields and false flags in those two existing synthetic Drop records. Its profile is `77852588b0f177eb4c7d4e4a65626f6a3648f78768da08b82458c3650e14a2a2`. The full patch/source/runner replay passes static checks; V3 has not been built in Cloud. The exporter, decoder, translator and console sources are unchanged from the compiled V2 candidate.

Next experiment requires a fresh authorized session and budget. Hypothesis: these schema defaults restore the official refiner build while preserving ordinary synthetic Drop behavior. The domain and target contract remain the exact nongeneric concrete-u64 source specialization: dynamic self.len, CURRENT, complete normal resource posts, false method unwind post, full caller outcomes, return/free/leak, and strict original/verified generated CFG including unwind. Expected first positive gate is refiner-build exit 0 with exact source/binary receipts; then actual generated body and checked selected method must pass extraction/refinement/proof. A compiler/setup failure is not an intended negative. A structural or binding mismatch requires inspection of its exact descriptor/CFG; a need for general kernel/memory/alias or generic T/ZST support requires the owner's scope decision.

After actual glue PASS, qualify the exact caller-created receiver and linear end token, with all required missing-permission, nonvacuity, duplication, end/retirement and real dead-code controls on that same profile. Only then proceed to actual late-panic cleanup with the multi-cell witness. Session accounting and closure are in [FINAL-CHECKPOINT](FINAL-CHECKPOINT.md) and [BUDGET](BUDGET.json). No profile acceptance, integration or external publication is authorized.

Body-v3 Buildaa12856c/8091ec47 FAILURE408s; archive7c8af4a808aa2d23251fe5ee0e8f83ca207c72b409b929031749caae70600dd0 fullintegrity verified. Exporter/decoder/translator/console0; officialrefiner1 atmain.ml174 ambiguous local.id inferredbasic_block_id vsplace.local local_decl_id. No rebuiltrefiner executable/receipt, extraction/refinement/proof NOT_RUN; no intendednegative. Body-v3 profile/patch retained.

Narrowbody-v4 tool117cc1d2d271cc4d8e6b86551228e55859725568/profile794bd56d0337ac8813ce7935703e6a368b0606b8c06b8868498ec7dfbcfcf926 adds explicitschema-derived recordtypes withinnewgeneratedhelpers; predicates/CFG/unwind/normalposts/lifetime/kernel unchanged. Same sharedlabel ambiguity motivates annotations inlocal/layout/spanmap lambdas; no newadmission. NewCloudcompile gate required. Serviceclassifier fix requires independentglueheader/copiedreceiver/call/return/leak; positives do not inheritselectedmarkers. NextCloudrun also savesoriginalMIRanddecodedCFG besidetheverifiedpair withsupplementalstages, officialrefiner remainsresponsibleforownsourcecomparison. InputsfrompreviousBuild untouched; oldclassifications/logspreserved.
