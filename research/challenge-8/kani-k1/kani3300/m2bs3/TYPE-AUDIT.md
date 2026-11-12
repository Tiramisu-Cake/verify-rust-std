# M2-B/S3 explicit source/type audit

Static source audit only; build/clippy/Kani/CBMC NOT_RUN locally. Allowed pinned rustfmt wrapper ran.

## Compiler delta

- points_to_analysis.rs imports std::collections::HashMap alongside HashSet, both used.
  StableInstance and StableBody remain aliases of rustc_public::mir::{mono::Instance, Body}.
- New field and parameter `body_overrides: &HashMap<StableInstance, StableBody>`; internal recursive
  analysis holds `&'a HashMap<StableInstance, StableBody>` alongside `&'a CallGraph` and `&'a Body<'tcx>`.
  Each recursive call passes the same shared map; no mutation/RefCell/callback or new lifetime bound.
  Public run_points_to_analysis still returns PointsToGraph<'tcx>; its ONLY call site is updated.
  Both calls to PointsToAnalysis::run pass the added map in the same parameter position.
- apply_regular_call_effect: instance is rustc_middle::ty::Instance<'tcx>; rustc_internal::stable(instance)
  is StableInstance. get(&stable_instance): Option<&StableBody>; cloned(): Option<StableBody>;
  or_else(|| stable_instance.body()): Option<StableBody>. The existing body() signature is established
  by its previous Some binding and existing resolver. internal_mir(tcx) still yields internal Body<'tcx>.
  Missing bodies retain the existing early return and local Unsupported policy.
- delayed_ub/mod.rs imports KaniAttributes and stable TerminatorKind (used). KaniAttributes::for_instance
  accepts (TyCtxt<'tcx>, stable Instance), source attributes.rs:181; fn_marker(): Option<rustc_span::Symbol>,
  source:314. is_some_and predicate takes Symbol; marker.as_str() == &str is the existing contracts.rs
  marker comparison form. Its result and both selector flags are bool.
- instances: Vec<stable Instance>, iteration item &Instance, *instance: Instance (Copy, same existing use).
  transformer.body_ref(tcx,*instance): &stable Body, source transform/mod.rs. `.ty().kind().is_closure()`
  is an existing contracts.rs expression yielding bool. body.blocks is Vec<stable BasicBlock>;
  len(): usize compared to unsuffixed 1 inferred usize, short-circuit protects index 0 (usize).
  statements.is_empty(): bool; matches! inspects the discriminant of stable TerminatorKind, no move/binding.
  clear_body at body.rs:459 creates exactly this empty one-block Unreachable shape and preserves locals.
- HashMap inference: insert(*instance, body.clone()) fixes HashMap<stable Instance, stable Body>.
  Body: Clone is already required by transformer.body and original delayed visitor body.clone().
  Borrow is shared and ends each loop iteration. Root get/cloned/unwrap_or_else returns stable Body;
  &body and &body_overrides match the new entry signature. Map is scoped to one global-pass invocation.
- No changed arithmetic, integer cast, width, sign or truncation; no usize/u64/u128 mixing.
  CBMC runtime object50/offset2 are trace data, never compiler indices or numeric constants in the patch.

## Tests

ordinary-singleton.rs is byte-identical to M2-A C03 (checked hash), including -D warnings and flags.
All its types/signatures match unchanged legal-pair.rs except omission of the separate PFC harness.
select:(MaybeUninit<u8>,MaybeUninit<u8>,bool)->MaybeUninit<u8>; byte:u8; slot:MaybeUninit<[u8;3]>;
slot.as_mut_ptr():*mut[u8;3], cast::<u8>():*mut u8, add(1/2):usize offsets, write(1/2/3):u8 values;
assume_init consumes storage and returns [u8;3]; value/out equality operands both [u8;3]; result &u8.

ensures-left/right-hole.rs use std::intrinsics::raw_eq and std::mem::MaybeUninit, both used.
Existing promoted-allocations/helper-*-hole.rs establishes identical intrinsic/reference pattern and gates.
promoted_hole:()->&'static[MaybeUninit<u8>;3]. Return expression is a promoted shared reference to a
flat array of MaybeUninit<u8>; uninit():MaybeUninit<u8>, new(7u8):MaybeUninit<u8>. Valid reference to
MU storage does not create a reference to invalid u8 data. Postcondition argument is
&&[MaybeUninit<u8>;3] (shared reference to return value); *result:&[MaybeUninit<u8>;3]. Other operand
&[MaybeUninit::new(7u8);3]:&[MaybeUninit<u8>;3], all initialized. raw_eq<T>(&T,&T)->bool with
T=[MaybeUninit<u8>;3] in both directions, under unsafe block and core_intrinsics/internal_features gates.
Three repeat count is inferred usize; no casts, signed arithmetic or range widening. Root discards the
returned reference without reading payload; only postcondition raw_eq reads the hole. Existing expected
negative pattern retained; CI must establish intended failed operand and successful lawful companion,
not just overall FAILURE. Result/lifetime/closure lowering still require compilation and retained MIR.
