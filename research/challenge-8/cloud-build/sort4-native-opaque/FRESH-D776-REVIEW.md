# Fresh d776: pointer PASS; precise strict entry and overflow dependencies

Build d77612a5-5620-47a7-819d-3fa499cd15c0, proof=infra
86e38e3a74cca49b2be8e12aa101bdd797d4a917, collectorSUCCESS/run0,
verification_accepted=false. create20:10:35.683686674UTC,
start20:10:36.429204801UTC, finish20:16:19.470822UTC; charged344seconds.
Session total759/3600. Canonical archive/config/source/inventory/upload/text-index
integrity verified: archivee467a5f23dcc9718b010eb16d78d1a4112c94f1ddffd2649244d2b8b0096e9d3.
[D776 artifact index](D776-ARTIFACT-INDEX.json) pins selected raw files; their bytes
also compared against the canonical archive before review. Direct duplicate
archive removed only after equal hashes; canonical evidence retained.

## Pointer implementation-expression component — fresh VF0/90

Sourcec89a920a546cc05acc0a9b3489e9a906a5c125395a3e5614edfcfbcc1f424a1c,
originalf132be6333ff6e16aa57ef47ebf45a7c45f98b6ba7a97f5fb7edba67e07d106f.
Paired normal/readonly MIR+refinement0, full ASTac332b537474a87325afdd1add0baaa2f3677731d3bdafd3d31a0430cb5b38ae,
verification0/90. Runtime slice-to-thin-pointer casts are exact method
implementation expressions (receiver renamed); len<2 return and len/2 are
included. Ghost source4 split/rejoin derives permission and T owners from native
source; scratch casts preserve pointer values while existing MU storage/owners
stay intact. Numeric pointer equality supplies no T ownership for scratch.
Raw log closes full automatic native normal post, unit return, local-free and
leak on each reached branch. No comparator or direct-unwind edge. Native
references and all lengths/ZST remain admitted in this expression component.
Actual external v.as_mut_ptr()/scratch.as_mut_ptr() method-call binding is absent.

## Native C1 candidate — fresh pre-callback strict-entry refusal

Source7ebcf7cd435c31b3f4669ac6f31a62fd45fcb2c7fa03500bdfbc44ccaca01742;
ghoststrip7c35a7e01915233308d113b081f26784c4ad5aaf6f7049dc209d126e3eb326a1.
Paired MIR+refinement0, normal8e9adcccd136d3c1ee4dc1e7bd929c3cd60883f497178eab24da40f60754dee4,
readonlybde6d797d56e0e11e9837fc922f6def819c6931d1349f42c5b36d4570e2001aa.
Actual candidate function entered; native source/MU/F resources and first-four
split/interior limits/start lifetime reached. VF1 at172:1–30:
`Strict lifetime binding has unresolved inference in entry outer type`.
Kernel freeze_strict_type in src/verifast.ml2545 rejects unresolved type
inference in any entry outer type before entering cmp. Callback body, direct
unwind, CURRENT recovery, full candidate posts/return/leak remain NOT_RUN.
This is not the intended callback unwind negative or a connected C1 proof.
No strict-cut check disabled, no alias/general type rule patched.

Full-package AST diagnostic separately exits2 with Ocaml_expr_of_ast.of_body_ss
TODO; no artifact. Serializer of_stmt has TODO for MergeFractionsStmt, which
appears in the GLOBAL recover_pair lemma; the new capture-only path serializes
only the original native declaration and may avoid that independent serializer
failure. This hypothesis needs fresh Cloud capture. Sole actual comparator MIR
call std::ops::FnMut::call_mut, lateBoundGenericParamCount1, span210:21–92;
source marker194, cut212. New source-specific capture-only profile is DRAFT,
not an accepted binding or a new lifetime/kernel rule.

## Minimal usize add — checked runtime route captured, verifier stops earlier

Same pinned rustc compiler SHA7033431126d84f3dfbedf1c28518cd043887aefaac0db2dec211ef331a95471b;
source601fe289c804513c48dd5a432a083920fd2f9bd6f3d6fa1be1b7850961dc5283.
Direct --emit=mir -C overflow-checks=on -C panic=unwind -C opt-level=0
-Z mir-opt-level=0 exit0, MIRb529e8c4d717a76f883833f75abd8b241bc5fc0eb9f133039011ef247512c48a.
Exact bb0 computes `_4 = AddWithOverflow(copy _3, const16_usize)`, asserts
`!_4.1` with successbb1 and `unwind continue`; bb1 assigns `_4.0` then returns
unit with StorageDead. Overflow takes a safe panic/unwind route, not runtime
unsafety. There is no caller len bound or ignored panic in this reproducer.

Frozen vf_mir_exporter lib.rs69 unconditionally appends
`-Coverflow_checks=off`; sourceSHA11f1e10bb8e52a4950611f874b1123c11e2c87cbb1378c3f5060992f74425f00.
Its normal/readonly full MIR instead has binaryOp/add and NO Assert; both
SHAa917ed828acb3b28ef766a6ba38e1afc7d9627cc2bdc967172a68797b1aac9a4.
Translated ordinary Add first refuses at3:17–25, cannot prove
len+16<=18446744073709551615. Thus checked operation and panic contract are
not reached in the frozen proof pipeline. General exporter/checked-operation
support belongs to VeriFast agent; no proof credit or general patch here.

## Scope retained

Prior opaque interface1ba7 VF0/73 and earlyreturnVF0/81 remain separate fresh
results, not repeated. Prior actual C1→C4 d5/a518 VF0/370 normal/all4CURRENT
unwinds/fullprefixposts/unit/leak remain prior PASS. Native→actualC1 and
native→actualC4 NOT_PROVED. Full actualcaller, guards/call edge, external pointer
methods, positive-size selection/ZST and laterC5/select/copy remain OPEN.
