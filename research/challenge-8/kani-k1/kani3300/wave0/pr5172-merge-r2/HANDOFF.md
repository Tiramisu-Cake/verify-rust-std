# HANDOFF — PR #5172 merge r2

2026-11-20 (Europe/Moscow). Coordinator task, one stage. Complete; stop with HANDOFF.

## Final identities

- Kani worktree: `/root/kani-pr5172-copilot-w15`.
- Branch: `fix/pr5172-copilot-20261119` (retained throughout).
- Clean input HEAD: `be926954f97d39628227c51a27fd702ea5eb0c98` (code fix `cea872ac973f98daef320e056987b6d5365d9e8b` plus comment cleanup).
- Fetched PR head: `d91aeeea94a8a4a697f9416fafbe6cf0f8816801`.
- Fetched current main: `fca73e13186782e62d286ef89c43d2fcc4bb3a51`.
- Final HEAD / new merge commit: `7e53bc65394dd1af675545c428ca2ff29e7a6a27`.
- Final tree: `46f343ba308f8d5922ce6d101ead94d96f24be35`.
- First parent: `be926954f97d39628227c51a27fd702ea5eb0c98`.
- Second parent: `d91aeeea94a8a4a697f9416fafbe6cf0f8816801`.
- Author and committer: `Tiramisu-Cake <igkharin@gmail.com>`.
- Exact message: `Merge branch 'fix/kani-uninit-unresolved-call-v3' into fix/kani-uninit-unresolved-call-v3`.
- Exactly one new Kani commit created. No rebase, history rewrite, skip-ci marker, or second merge commit.

Fetch command (read-only remote operation):

```sh
git fetch https://github.com/model-checking/kani.git \
  refs/pull/5172/head:refs/remotes/pr5172-review/head \
  refs/heads/main:refs/remotes/pr5172-review/main
```

Both fetched identities exactly matched the requested revisions. The PR head has parents `ac0304a8bfde3002ef0411ae0e73f94ce0cd7878` and `36bfc54d0694c382bca052f3c6d77819ba1f2279`. Current main has sole parent `36bfc54d0694c382bca052f3c6d77819ba1f2279`.

## Exact conflict report and main decision

1. Preflight `git merge-tree --write-tree be926954f97d39628227c51a27fd702ea5eb0c98 d91aeeea94a8a4a697f9416fafbe6cf0f8816801` returned exit 0 and only tree `46f343ba308f8d5922ce6d101ead94d96f24be35`.
2. Actual `git merge --no-ff` of the fetched PR head succeeded using `ort`. **No conflicts, unmerged paths, or manual resolutions.** Its committed tree equals the preflight tree. No source edits were made during this stage.
3. `git merge-tree --write-tree HEAD refs/remotes/pr5172-review/main`, at final HEAD `7e53bc65394dd1af675545c428ca2ff29e7a6a27`, returned **exit 0** and only hypothetical tree `0954c429de190c35f1c72112611ad1e6711f6b12`. No conflict messages or staged conflict entries were emitted. Merge base: `36bfc54d0694c382bca052f3c6d77819ba1f2279`.
4. Therefore, per the owner's conditional instruction, **current main was not merged**. The hypothetical tree is not the final tree. #5192 is still absent from the final branch.

#5192 changes trait-object pointee checks, reference/raw-pointer unsizing, vtable initialization, and Box-pointer recognition, including additions in the shared `ptr_uninit/uninit_visitor.rs`. #5172 guards unsupported calls (including virtual dispatch) and shim shadow-state transfers; our follow-up reuses the checked callee body and bounds recursive type traversal with a visited set. The textual merge is clean; this is not a claim of semantic or runtime compatibility for their future combination. No combined implementation was committed, no conflict resolution selected one side over the other, and no semantic redesign was attempted.

## Nightly API review

`rust-toolchain.toml` in final HEAD and fetched main selects `nightly-2026-11-19`. The input selected `nightly-2026-11-18`. The PR-head merge includes Kani's toolchain adaptation commit `62e6f800a2138bdc85ce57a379e7007583803a91` (#5201).

Read the dated distribution manifests directly, without installing or executing a toolchain:

| Manifest | rustc version | rustc source commit |
|---|---|---|
| <https://static.rust-lang.org/dist/2026-11-18/channel-rust-nightly.toml> | `1.102.0-nightly (59cbdee2e 2026-11-17)` | `59cbdee2e7b3ee50e44b460561c43c9e3023d9f0` |
| <https://static.rust-lang.org/dist/2026-11-19/channel-rust-nightly.toml> | `1.102.0-nightly (65ce8611f 2026-11-18)` | `65ce8611fed3142053320be6996ef00e9992671f` |

Used the GitHub connector to inspect the [exact Rust comparison](https://github.com/rust-lang/rust/compare/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0...65ce8611fed3142053320be6996ef00e9992671f) and read targeted files at both source commits. The comparison reports 127 commits and returns 300 file entries; that file list is capped and is not an exhaustive whole-Rust audit. Source comparisons below used the actual contents of the specified files at both exact commits.

Confirmed changes and applicability:

| API/source change between the dated rustc revisions | Result for #5172 and our follow-up |
|---|---|
| `rustc_attr_ir/src/attr.rs`: `Attribute::Tool(Box<AttrItem>)` becomes `Attribute::Tool { item, opts }`. | No direct use in the six PR compiler files. #5201's four adaptations in Kani `kani_middle/attributes.rs` are retained. |
| `rustc_middle/src/ty/intrinsic.rs`: `IntrinsicDef::name: Symbol` becomes `Intrinsic::{Rustc(Symbol), Backend { llvm }}`; `TyCtxt::is_intrinsic` becomes `is_rustc_intrinsic`. | No direct use of these changed rustc APIs in the six PR compiler files. #5201's `Intrinsic::Rustc(sym::simd_bitmask)` adaptation is retained. |
| `rustc_public_bridge/src/context/impls.rs`: `intrinsic_name` now matches both `Intrinsic` variants and returns the selected symbol as a string. | The bridge preserves the name interface consumed through Kani's `Intrinsic::from_instance`; that helper uses rustc-public `Instance::intrinsic_name()`. No source adaptation required here. |
| `rustc_abi/src/lib.rs`: `TargetDataLayout::{i1_align,i8_align}` removed; I8 alignment is `Align::ONE`. | No use of either field in the six PR compiler files. #5201's LLBC replacement using `Integer::I8.align(target_data)` is retained. |
| `rustc_middle/src/ty/{context,sty}.rs` and `rustc_type_ir/src/flags.rs`: type interning and flag computation reorganized; `ty_kind.rs`/`sty.rs` add `fn_sig_abi` and `fn_sig_safety`. | No use of the changed construction/flag APIs or added helpers in the PR files. The follow-up reads type kinds and fields; it does not construct internal types. The `Pat`/ADT/closure match shapes used by the helper are not changed by the inspected diffs. |
| `rustc_middle/src/mir/query.rs`: coroutine layout gains `pack`; `queries.rs` gains crate-source flags query. | No direct uses of these changed APIs in the PR files. |

Direct, byte-for-byte comparisons also found these Rust source files identical between the two nightly commits:

- `compiler/rustc_public/src/mir/mono.rs`: instance kinds, `Instance::resolve`, `body`, `has_body`, `is_foreign_item`, and `intrinsic_name` declarations remain unchanged.
- `compiler/rustc_middle/src/ty/instance.rs`: internal instance representation/resolution source unchanged.
- `compiler/rustc_public/src/rustc_internal/mod.rs`: stable/internal conversion source unchanged.
- `compiler/rustc_public/src/ty.rs` and its implementation files `ty/def.rs`, `ty/tys.rs`: public type definitions/helpers unchanged.

Read and compared the other targeted source files listed in the table, as well as `rustc_middle/src/ty/{mod,util}.rs`. In those inspected diffs, no signature change was found for `FieldDef::ty(tcx, args)`, `skip_normalization`, or the existing closure upvar path used by our recursive helper. The follow-up's call is `field.ty(tcx, *args).skip_normalization()` and its visited set keys are internal `Ty`; no source change was needed.

### Required grep

Scanned the complete contents of **all six compiler files changed by #5172**, determined by `git diff --name-only 36bfc54d06 HEAD -- kani-compiler`:

```text
kani-compiler/src/kani_middle/points_to/mod.rs
kani-compiler/src/kani_middle/points_to/points_to_analysis.rs
kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs
kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs
kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs
kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs
```

`rg -n` with this pattern returned exit 1, no matches (expected no-match, not an execution error):

```regex
Attribute::Tool|IntrinsicDef|\bis_intrinsic\b|\bis_rustc_intrinsic\b|\bi1_align\b|\bi8_align\b|\bmk_ty_from_kind\b|\bintern_ty\b|FlagComputation|PackCoroutineLayout|used_crate_source_flags|fn_sig_abi|fn_sig_safety
```

A second grep traced the adjacent paths: `Intrinsic::from_instance` at `points_to_analysis.rs:205`, `uninit_visitor.rs:308`, and `initial_target_visitor.rs:113`; `resolve_call` at `points_to_analysis.rs:350`; stable-body conversion at `points_to_analysis.rs:454`; `field.ty(...).skip_normalization()` at `uninit_visitor.rs:792`; `TyKind::Pat` at line 796; closure upvars at line 797. Reviewed the helper and bridge implementations these call sites depend on.

### Risk assessment

No concrete nightly API incompatibility was found in this targeted static review. This is **not compilation, regression, or proof acceptance**. The earlier tested fix was based on the previous nightly; this merged candidate has not been tested on nightly-2026-11-19. In particular, MIR body conversion and generated shim behavior, new backend-specific intrinsics, and interactions with the other newly inherited main changes remain runtime/test risks. The resolver still explicitly rejects rustc-public `LlvmIntrinsic` and virtual instances; no support for newly introduced intrinsic behavior was guessed or added. #5192's future combination remains untested even though Git merges it textually without conflict.

## Preservation and allowed validation

- `git diff --check d91aeeea94 HEAD` passed.
- Final-vs-PR changed-file list is exactly our four input follow-up files; no other delta remains relative to the fetched PR head.
- For each of those four files, the complete `git diff ac0304a8bf be926954f97 -- FILE` is byte-for-byte identical to `git diff d91aeeea94 7e53bc65394d -- FILE`, including patch coordinates and blob IDs. Our code fix and comment cleanup were preserved exactly.
- The committed merge tree equals its preflight merge-tree result.
- Kani worktree is clean after the merge.
- No cargo, rustc, Kani, CBMC, builds, tests, push, CI dispatch, or remote writes were performed. Git hooks were disabled per command for local commits to preserve that boundary. No toolchain installation occurred.
- Research worktree was initially clean at `7e0d1cb77534e53a6e90338f8e97213385ef85f7`. An unrelated untracked `research/challenge-8/kani-k1/kani3300/wave0/pr5159-followup-main/` appeared during the stage; it was left untouched and is excluded from this HANDOFF commit.
- This document is committed separately in `/root/verify-rust-std-kani3300-g0` with `[skip ci]`, as `Tiramisu-Cake <igkharin@gmail.com>`. Its commit SHA is reported in the final coordinator response.

## Final HEAD vs fetched PR head, limited to our files

The full exact patch follows. It is 39 insertions and 40 deletions in four files.

```diff
diff --git a/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs b/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs
index 3a53ecb88f3cba00e8af9dcdd32c71a5b4041573..e49da2d961e35f48554aba49eeadd75f6aae1a3d 100644
--- a/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs
+++ b/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs
@@ -193,7 +193,7 @@ fn apply_primary_terminator_effect(
     ) {
         if let TerminatorKind::Call { func, args, destination, .. } = &terminator.kind {
             // Instrumentation stops execution at unsupported calls before their effects occur.
-            let Ok(instance) =
+            let Ok((instance, body)) =
                 resolve_call(self.tcx, rustc_internal::stable(func.ty(self.body, self.tcx)))
             else {
                 return;
@@ -327,7 +327,8 @@ fn apply_primary_terminator_effect(
                         }
                     } else {
                         // Otherwise, handle this as a regular function call.
-                        self.apply_regular_call_effect(state, instance, args, destination);
+                        let Some(body) = body else { return };
+                        self.apply_regular_call_effect(state, instance, body, args, destination);
                     }
                 }
             }
@@ -344,10 +345,12 @@ fn apply_call_return_effect(
     }
 }
 
-/// Resolve calls whose effects the uninitialized-memory passes can follow.
-/// The local visitor emits unsupported-call checks and guards memory initialization state
-/// transfers through compiler-generated shims.
-pub fn resolve_call(tcx: TyCtxt, func_ty: StableTy) -> Result<StableInstance, String> {
+/// Resolve a supported direct callee and return its checked MIR body.
+/// Intrinsics and foreign items return no body.
+pub fn resolve_call(
+    tcx: TyCtxt,
+    func_ty: StableTy,
+) -> Result<(StableInstance, Option<StableBody>), String> {
     let StableTyKind::RigidTy(StableRigidTy::FnDef(def, args)) = func_ty.kind() else {
         return Err(unsupported_call_reason("calls through function pointers"));
     };
@@ -355,13 +358,13 @@ pub fn resolve_call(tcx: TyCtxt, func_ty: StableTy) -> Result<StableInstance, St
         format!("Kani could not resolve function item `{func_ty:?}` for memory initialization checks: {err:?}.")
     })?;
     let reason = match instance.kind {
-        StableInstanceKind::Intrinsic => return Ok(instance),
-        StableInstanceKind::Item if instance.is_foreign_item() => return Ok(instance),
+        StableInstanceKind::Intrinsic => return Ok((instance, None)),
+        StableInstanceKind::Item if instance.is_foreign_item() => return Ok((instance, None)),
         StableInstanceKind::Item | StableInstanceKind::Shim => {
             // Check MIR availability for the instance, including compiler-generated shims,
             // and report explicit tail calls before converting user code to stable MIR.
-            if crate::kani_middle::checked_body(tcx, instance).is_some() {
-                return Ok(instance);
+            if let Some(body) = crate::kani_middle::checked_body(tcx, instance) {
+                return Ok((instance, Some(body)));
             }
             format!("calls to bodyless {:?} instances", instance.kind)
         }
@@ -443,19 +446,12 @@ fn apply_regular_call_effect(
         &self,
         state: &mut PointsToGraph<'tcx>,
         instance: Instance<'tcx>,
+        body: StableBody,
         args: &[Spanned<Operand<'tcx>>],
         destination: &Place<'tcx>,
     ) {
         // Here we simply call another function, so need to retrieve internal body for it.
-        let new_body = {
-            let stable_instance = rustc_internal::stable(instance);
-            // Preserve accumulated edges when the callee's body is unavailable.
-            let Some(stable_body) = crate::kani_middle::checked_body(self.tcx, stable_instance)
-            else {
-                return;
-            };
-            stable_body.internal_mir(self.tcx)
-        };
+        let new_body = body.internal_mir(self.tcx);
 
         // In order to be efficient, create a new graph for the function call analysis, which only
         // contains arguments and statics and anything transitively reachable from them.
diff --git a/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs b/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs
index 6d5e6940e20aa46e421fb2ed7682c7e90454e7b3..baf4236745560360113099012f05c4234220ab6c 100644
--- a/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs
+++ b/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs
@@ -129,7 +129,6 @@ fn visit_terminator(&mut self, term: &Terminator, location: Location) {
 /// The instance a call operand refers to, if it is a function item rather than a function pointer.
 fn try_resolve_instance(locals: &[LocalDecl], func: &Operand) -> Option<Instance> {
     match func.ty(locals).unwrap().kind() {
-        // Successfully resolved instances can identify intrinsics that create analysis targets.
         TyKind::RigidTy(RigidTy::FnDef(def, args)) => Instance::resolve(def, &args).ok(),
         _ => None,
     }
diff --git a/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs b/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs
index 9bc70819031b79835540b90eff1c2317abf27d1d..5d26dc5fad2afec1c7bc866163cc9183617d4f5f 100644
--- a/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs
+++ b/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs
@@ -103,8 +103,7 @@ fn visit_terminator(&mut self, term: &Terminator, location: Location) {
         } else {
             unreachable!()
         }
-        // The local uninitialized-memory visitor checks call operands and emits unsupported-call
-        // checks independently of the analysis targets collected here.
+        // The local visitor checks call operands and reports unsupported calls.
         self.super_terminator(term, location);
         // Push the current target from the terminator onto the list.
         self.targets.push(self.current_target.clone());
diff --git a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs b/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs
index 1f45e5c32680540a63ee6f803ae5b048fd79f96d..fb91a51d7fa6ea5abd8ea8823e2aa47d7890532a 100644
--- a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs
+++ b/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs
@@ -28,6 +28,7 @@
     },
     ty::{AdtKind, ConstantKind, RigidTy, Ty, TyConstKind, TyKind},
 };
+use std::collections::HashSet;
 
 pub struct CheckUninitVisitor<'tcx> {
     tcx: TyCtxt<'tcx>,
@@ -283,8 +284,7 @@ fn visit_terminator(&mut self, term: &Terminator, location: Location) {
                     Ok(instance) => instance,
                     Err(reason) => {
                         self.push_target(MemoryInitOp::Unsupported { reason });
-                        // Keep entry loads and operations collected while visiting the call.
-                        // The common terminator epilogue publishes the collected target.
+                        // Publish entry loads and operand checks through the terminator epilogue.
                         break 'call;
                     }
                 };
@@ -411,8 +411,8 @@ fn visit_terminator(&mut self, term: &Terminator, location: Location) {
                         }
                     }
                     InstanceKind::Item | InstanceKind::Shim => {
-                        // The resolver accepts MIR bodies and foreign items. Foreign items use
-                        // the models below; other calls transfer union argument and return state.
+                        // Model foreign allocation calls here. Calls with MIR bodies store
+                        // initialization state for union arguments.
                         if instance.is_foreign_item() {
                             match instance.name().as_str() {
                                 "alloc::alloc::__rust_alloc" | "alloc::alloc::__rust_realloc" => {
@@ -764,31 +764,37 @@ fn try_remove_topmost_deref(place: &Place) -> Option<Place> {
     }
 }
 
-/// Try retrieving instance for the given function operand.
+/// Resolve a call operand and discard the checked body.
 fn try_resolve_instance(
     tcx: TyCtxt,
     locals: &[LocalDecl],
     func: &Operand,
 ) -> Result<Instance, String> {
-    resolve_call(tcx, func.ty(locals).unwrap())
+    resolve_call(tcx, func.ty(locals).unwrap()).map(|(instance, _)| instance)
 }
 
-/// Check whether a type may carry memory initialization state through a compiler-generated shim.
-/// Inspect unions and nested by-value storage; references and pointers carry addresses.
-/// Treat unknown types conservatively as carrying memory initialization state.
+/// Check for unions or unclassified types in a shim's by-value storage.
+/// Follow aggregate fields and captures; stop at pointers and references.
 fn shim_type_may_carry_shadow(tcx: TyCtxt<'_>, ty: Ty) -> bool {
-    fn inspect<'tcx>(tcx: TyCtxt<'tcx>, ty: rustc_middle::ty::Ty<'tcx>) -> bool {
+    fn inspect<'tcx>(
+        tcx: TyCtxt<'tcx>,
+        ty: rustc_middle::ty::Ty<'tcx>,
+        visited: &mut HashSet<rustc_middle::ty::Ty<'tcx>>,
+    ) -> bool {
         use rustc_middle::ty::TyKind;
+        if !visited.insert(ty) {
+            return false;
+        }
         match ty.kind() {
             TyKind::Adt(def, args) => {
                 def.is_union()
-                    || def
-                        .all_fields()
-                        .any(|field| inspect(tcx, field.ty(tcx, args).skip_normalization()))
+                    || def.all_fields().any(|field| {
+                        inspect(tcx, field.ty(tcx, *args).skip_normalization(), visited)
+                    })
             }
-            TyKind::Tuple(fields) => fields.iter().any(|field| inspect(tcx, field)),
-            TyKind::Array(element, _) | TyKind::Pat(element, _) => inspect(tcx, *element),
-            TyKind::Closure(_, args) => inspect(tcx, args.as_closure().tupled_upvars_ty()),
+            TyKind::Tuple(fields) => fields.iter().any(|field| inspect(tcx, field, visited)),
+            TyKind::Array(element, _) | TyKind::Pat(element, _) => inspect(tcx, *element, visited),
+            TyKind::Closure(_, args) => inspect(tcx, args.as_closure().tupled_upvars_ty(), visited),
             TyKind::Bool
             | TyKind::Char
             | TyKind::Int(_)
@@ -802,10 +808,9 @@ fn inspect<'tcx>(tcx: TyCtxt<'tcx>, ty: rustc_middle::ty::Ty<'tcx>) -> bool {
             _ => true,
         }
     }
-    inspect(tcx, rustc_internal::internal(tcx, ty))
+    inspect(tcx, rustc_internal::internal(tcx, ty), &mut HashSet::new())
 }
 
-/// Describe an unsupported call encountered during memory initialization checks.
 fn unsupported_call_reason(kind: &str) -> String {
     format!(
         "Kani does not support memory initialization checks across {kind}. For more information about planned support, see https://github.com/model-checking/kani/issues/3300."
```

**HANDOFF — stop here.** Publication and further validation require a later stage.
