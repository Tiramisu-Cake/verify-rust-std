# HANDOFF — PR #5172 approved comment cleanup

2026-11-20 (Europe/Moscow). Coordinator task, one stage. Complete; stop with HANDOFF.

## Revision boundary and commits

- Kani worktree: `/root/kani-pr5172-copilot-w15`.
- Branch: `fix/pr5172-copilot-20261119`.
- Verified clean input HEAD: `cea872ac973f98daef320e056987b6d5365d9e8b`.
- New Kani commit: `be926954f97d39628227c51a27fd702ea5eb0c98`; its sole parent is the input HEAD. Exactly one commit added.
- Author and committer: `Tiramisu-Cake <igkharin@gmail.com>`.
- Exact commit message: `Tighten comments in unresolved-call handling`.
- The Kani commit contains neither a skip-ci marker nor a Co-Authored-By trailer.
- Kani worktree is clean after the commit.
- Research worktree: `/root/verify-rust-std-kani3300-g0`; clean input HEAD `16b5608bf91a469099866ae6677a4f859c19b0c9`. This HANDOFF is committed separately with `[skip ci]`; its commit SHA is reported in the coordinator response.

## Scope completed

Applied exactly the owner-approved source HANDOFF at `../pr5172-slop-r2/HANDOFF.md`: section (a), all six section (d) edits, and the adapter doc replacement `/// Resolve a call operand and discard the checked body.`. No replacements from sections (b) or (c), no helper removal, and no additional source edits.

Four Rust files changed: 9 insertions and 16 deletions, all full-line comments or documentation. The complete committed diff follows below.

## Validation

- Reconstructed the expected committed files from the input commit using the eight original line ranges and the exact replacement blocks in the source HANDOFF; all four files match exactly.
- Compared each input/committed file after removing only full lines whose first non-whitespace characters are `//` (including `///`). The remaining bytes, including whitespace and all code, are identical in every file. This establishes the requested unchanged code-token check without invoking a compiler or lexer. Independently checked every added/deleted line is a full-line comment/doc line.
- SHA-256 values below are identical before and after stripping those comment lines. Paths are relative to `kani-compiler/src/kani_middle/`.

| File | SHA-256 of comment-stripped bytes (both revisions) |
|---|---|
| `points_to/points_to_analysis.rs` | `b9cc741ca52d3a6f5f2d2d34eef8b9769f883e9c340cf60c4d2da7456556ff43` |
| `transform/check_uninit/ptr_uninit/uninit_visitor.rs` | `cfd6929581d5a5bf366436cc5d54e1baa9a422ea924c76a3aadf905f7d342c62` |
| `transform/check_uninit/delayed_ub/initial_target_visitor.rs` | `d728522d89a0bacf028eceb42e9f7557b4ba2c11e4d28e94b69881a0ce3e81e7` |
| `transform/check_uninit/delayed_ub/instrumentation_visitor.rs` | `98e607924cd9da05e820cbad2e2fd6eca829ac421dee88c5260a22ea0f8cbdd9` |

- All nine added lines are at most 100 characters including indentation; measured maximum: 98. Replacement indentation matches each original block.
- `git diff --check cea872ac973f98daef320e056987b6d5365d9e8b be926954f97d39628227c51a27fd702ea5eb0c98` passed.
- `rustfmt.toml` is unchanged and has no `wrap_comments` setting. Code, whitespace outside replaced comment lines, and comment indentation are preserved. Formatting was assessed statically; rustfmt acceptance was not executed or claimed.
- No cargo, rustc, rustfmt, Kani, CBMC, build, tests, push, CI dispatch, or remote mutation was performed. Git commit hooks were disabled for these local commits to preserve that execution boundary.

## Full committed Kani diff

```diff
diff --git a/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs b/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs
index 9c61b22c05557ba2e6739657042db757818977f3..e49da2d961e35f48554aba49eeadd75f6aae1a3d 100644
--- a/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs
+++ b/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs
@@ -345,10 +345,8 @@ fn apply_call_return_effect(
     }
 }
 
-/// Resolve calls whose effects the uninitialized-memory passes can follow.
-/// The local visitor emits unsupported-call checks and guards memory initialization state
-/// transfers through compiler-generated shims.
-/// Returns the checked body for reuse, except for intrinsics and foreign items.
+/// Resolve a supported direct callee and return its checked MIR body.
+/// Intrinsics and foreign items return no body.
 pub fn resolve_call(
     tcx: TyCtxt,
     func_ty: StableTy,
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
index 5b02c666289ff81a9532aeb4fed18451f8c63ff5..fb91a51d7fa6ea5abd8ea8823e2aa47d7890532a 100644
--- a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs
+++ b/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs
@@ -284,8 +284,7 @@ fn visit_terminator(&mut self, term: &Terminator, location: Location) {
                     Ok(instance) => instance,
                     Err(reason) => {
                         self.push_target(MemoryInitOp::Unsupported { reason });
-                        // Keep entry loads and operations collected while visiting the call.
-                        // The common terminator epilogue publishes the collected target.
+                        // Publish entry loads and operand checks through the terminator epilogue.
                         break 'call;
                     }
                 };
@@ -412,8 +411,8 @@ fn visit_terminator(&mut self, term: &Terminator, location: Location) {
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
@@ -765,7 +764,7 @@ fn try_remove_topmost_deref(place: &Place) -> Option<Place> {
     }
 }
 
-/// Try retrieving instance for the given function operand.
+/// Resolve a call operand and discard the checked body.
 fn try_resolve_instance(
     tcx: TyCtxt,
     locals: &[LocalDecl],
@@ -774,9 +773,8 @@ fn try_resolve_instance(
     resolve_call(tcx, func.ty(locals).unwrap()).map(|(instance, _)| instance)
 }
 
-/// Check whether a type may carry memory initialization state through a compiler-generated shim.
-/// Inspect unions and nested by-value storage; references and pointers carry addresses.
-/// Treat unknown types conservatively as carrying memory initialization state.
+/// Check for unions or unclassified types in a shim's by-value storage.
+/// Follow aggregate fields and captures; stop at pointers and references.
 fn shim_type_may_carry_shadow(tcx: TyCtxt<'_>, ty: Ty) -> bool {
     fn inspect<'tcx>(
         tcx: TyCtxt<'tcx>,
@@ -813,7 +811,6 @@ fn inspect<'tcx>(
     inspect(tcx, rustc_internal::internal(tcx, ty), &mut HashSet::new())
 }
 
-/// Describe an unsupported call encountered during memory initialization checks.
 fn unsupported_call_reason(kind: &str) -> String {
     format!(
         "Kani does not support memory initialization checks across {kind}. For more information about planned support, see https://github.com/model-checking/kani/issues/3300."
```

**HANDOFF — stop here.** Publication and any later validation remain outside this stage.
