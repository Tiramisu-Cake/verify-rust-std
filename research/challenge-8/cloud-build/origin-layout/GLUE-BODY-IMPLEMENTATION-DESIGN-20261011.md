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
