# #5172 fixup — итоговый diff

- Worktree: `/root/kani-5172-fixup-w11`
- Ветка: `fix/kani-uninit-unresolved-call-v3-fixup-w11`
- Исходная база #5172: `6fe484b30043b3696b5f1ccc4bea0e42891ad012`
- Первая правка: `cb0efdbe5bba20635561e5c663cd9f6c3c767578`
- Итоговый коммит: `5d5035f5afcaf90902772bf68f56bae253ac2f99`, новый коммит поверх первой правки, без amend.
- Автор обоих коммитов: `Tiramisu-Cake <igkharin@gmail.com>`.

Итоговая дельта `6fe484b300..5d5035f5afcaf90902772bf68f56bae253ac2f99` содержит только:

- `checked_body(tcx, instance)` в `resolve_call` и передачу `tcx` из points-to анализа и локального visitor. Это перенос соответствующей части PR-01 `d82752c8bc878398e672bffaa631ca6a28430acc` по указанию в `kani_middle/mod.rs`.
- Вычитанные комментарии в четырёх compiler-файлах и 18 исходниках тестов. Включены четыре комментария тестов, ранее исправленные PR-01.

Все строки диагностики восстановлены из #5172: общий шаблон `Kani does not support memory initialization checks across {kind}. For more information about planned support, see …/3300`, ошибка `Kani could not resolve function item …`, `calls to bodyless … instances`, `calls to LlvmIntrinsic instances` и `shadow transfers through Shim instances`. Все `.expected` и `delayed-ub-unsupported-call/expected` совпадают с исходной базой побайтно и отсутствуют в итоговом diff.

Статические проверки: PASS. `git diff --check 6fe484b300 HEAD` прошёл. Проверены все 22 файла итогового diff: после удаления комментариев и нормализации пробелов/завершающих запятых код совпадает с базой плюс точечный перенос `checked_body`/`tcx`; все строковые литералы четырёх compiler-файлов совпадают с базой. Код, флаги, assertions тестов и ожидаемые результаты сохранены. История содержит два последовательных коммита поверх исходной базы.

Компиляция и runtime-тесты не запускались; push, CI, публикации и ledger не выполнялись. COMMENT.md содержит точный текст владельца и строку раскрытия; это черновик, он не публиковался.

Статистика итогового diff:

```text
 .../kani_middle/points_to/points_to_analysis.rs    | 20 +++++++-------
 .../delayed_ub/initial_target_visitor.rs           |  2 +-
 .../delayed_ub/instrumentation_visitor.rs          |  4 +--
 .../check_uninit/ptr_uninit/uninit_visitor.rs      | 32 ++++++++++++----------
 .../uninit/unresolved-calls/direct-seeded.rs       |  2 +-
 .../unresolved-calls/entry-initialized-plain.rs    |  4 +--
 .../unresolved-calls/entry-initialized-seeded.rs   |  6 ++--
 .../uninit/unresolved-calls/entry-partial-plain.rs |  4 +--
 .../unresolved-calls/entry-partial-seeded.rs       |  6 ++--
 .../unresolved-calls/erased-pointer-plain.rs       |  2 +-
 .../unresolved-calls/erased-pointer-seeded.rs      |  4 +--
 .../uninit/unresolved-calls/fn-pointer-seeded.rs   |  2 +-
 .../unresolved-calls/fn-trait-pointer-plain.rs     |  3 +-
 .../unresolved-calls/fn-trait-pointer-seeded.rs    |  5 ++--
 .../unresolved-calls/generated-positive-plain.rs   |  3 +-
 .../unresolved-calls/generated-positive-seeded.rs  |  5 ++--
 .../unresolved-calls/global-escaped-plain.rs       |  2 +-
 .../unresolved-calls/global-escaped-seeded.rs      |  4 +--
 .../uninit/unresolved-calls/pending-ops-plain.rs   |  5 ++--
 .../uninit/unresolved-calls/pending-ops-seeded.rs  |  7 ++---
 .../uninit/unresolved-calls/virtual-seeded.rs      |  2 +-
 .../unresolved-calls/wrapped-pointer-seeded.rs     |  2 +-
 22 files changed, 62 insertions(+), 64 deletions(-)
```

Полный итоговый diff `6fe484b300..5d5035f5afcaf90902772bf68f56bae253ac2f99` (`git diff --unified=0`):

```diff
diff --git a/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs b/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs
index d74f11eb1..3a53ecb88 100644
--- a/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs
+++ b/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs
@@ -195,3 +195,3 @@ fn apply_primary_terminator_effect(
-            // Calls the analysis cannot follow add no edges here: the instrumentation guards each
-            // of them with an unsupported check, which stops execution before the call.
-            let Ok(instance) = resolve_call(rustc_internal::stable(func.ty(self.body, self.tcx)))
+            // Instrumentation stops execution at unsupported calls before their effects occur.
+            let Ok(instance) =
+                resolve_call(self.tcx, rustc_internal::stable(func.ty(self.body, self.tcx)))
@@ -348,3 +348,3 @@ fn apply_call_return_effect(
-/// The local visitor owns the diagnostic on every rejected path, even without delayed-UB seeds.
-/// MIR-backed shims may be analyzed; their shadow-transfer boundary is guarded locally.
-pub fn resolve_call(func_ty: StableTy) -> Result<StableInstance, String> {
+/// The local visitor emits unsupported-call checks and guards memory initialization state
+/// transfers through compiler-generated shims.
+pub fn resolve_call(tcx: TyCtxt, func_ty: StableTy) -> Result<StableInstance, String> {
@@ -361,3 +361,3 @@ pub fn resolve_call(func_ty: StableTy) -> Result<StableInstance, String> {
-            // Query actual MIR availability, including empty compiler-generated shims.
-            // has_body alone describes the definition rather than the generated instance.
-            if instance.body().is_some() {
+            // Check MIR availability for the instance, including compiler-generated shims,
+            // and report explicit tail calls before converting user code to stable MIR.
+            if crate::kani_middle::checked_body(tcx, instance).is_some() {
@@ -452 +452 @@ fn apply_regular_call_effect(
-            // Unsupported callees leave previously accumulated edges intact.
+            // Preserve accumulated edges when the callee's body is unavailable.
diff --git a/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs b/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs
index b585f7237..6d5e6940e 100644
--- a/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs
+++ b/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs
@@ -132 +132 @@ fn try_resolve_instance(locals: &[LocalDecl], func: &Operand) -> Option<Instance
-        // A failed resolution cannot identify an intrinsic seed.
+        // Successfully resolved instances can identify intrinsics that create analysis targets.
diff --git a/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs b/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs
index 7909418cb..9bc708190 100644
--- a/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs
+++ b/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs
@@ -106,2 +106,2 @@ fn visit_terminator(&mut self, term: &Terminator, location: Location) {
-        // The local uninitialized-memory visitor owns unsupported-call checks. It runs
-        // even without delayed-UB targets, and preserves checks on the call's operands.
+        // The local uninitialized-memory visitor checks call operands and emits unsupported-call
+        // checks independently of the analysis targets collected here.
diff --git a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs b/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs
index 121d61dbd..fef7aa83a 100644
--- a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs
+++ b/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs
@@ -69,2 +69,2 @@ fn find_all(mut self, body: &MutableBody) -> Vec<InitRelevantInstruction> {
-                // RustCall and other generated ABIs do not establish the legacy union
-                // slot pairing. Guard entry before any fallback LoadArgument can bless it.
+                // Guard shim entry when parameters or the return value may carry
+                // memory initialization state, before loading union arguments.
@@ -282 +282 @@ fn visit_terminator(&mut self, term: &Terminator, location: Location) {
-                let instance = match try_resolve_instance(&self.locals, func) {
+                let instance = match try_resolve_instance(self.tcx, &self.locals, func) {
@@ -287 +287 @@ fn visit_terminator(&mut self, term: &Terminator, location: Location) {
-                        // The common terminator epilogue must publish this target, even on error.
+                        // The common terminator epilogue publishes the collected target.
@@ -291,2 +291,2 @@ fn visit_terminator(&mut self, term: &Terminator, location: Location) {
-                // Inspect the source operands and destination before any StoreArgument.
-                // Tuple wrapping must not hide a union behind an unproved generated ABI.
+                // Check arguments and the destination for memory initialization state,
+                // including unions inside tuples, before storing argument state.
@@ -409,2 +409,2 @@ fn visit_terminator(&mut self, term: &Terminator, location: Location) {
-                        // The resolver checked actual instance body availability, with foreign
-                        // models retained. Non-shadow shims follow the ordinary MIR path.
+                        // The resolver accepts MIR bodies and foreign items. Foreign items use
+                        // the models below; other calls transfer union argument and return state.
@@ -763,2 +763,6 @@ fn try_remove_topmost_deref(place: &Place) -> Option<Place> {
-fn try_resolve_instance(locals: &[LocalDecl], func: &Operand) -> Result<Instance, String> {
-    resolve_call(func.ty(locals).unwrap())
+fn try_resolve_instance(
+    tcx: TyCtxt,
+    locals: &[LocalDecl],
+    func: &Operand,
+) -> Result<Instance, String> {
+    resolve_call(tcx, func.ty(locals).unwrap())
@@ -767,3 +771,3 @@ fn try_resolve_instance(locals: &[LocalDecl], func: &Operand) -> Result<Instance
-/// Conservative admission guard for generated ABIs, not an expansion of the shadow model.
-/// Inspect only by-value storage: references and pointers do not transfer their pointee shadow.
-/// Unknown storage is rejected rather than treated as an empty tuple or ordinary bytes.
+/// Check whether a type may carry memory initialization state through a compiler-generated shim.
+/// Inspect unions and nested by-value storage; references and pointers carry addresses.
+/// Treat unknown types conservatively as carrying memory initialization state.
@@ -799 +803 @@ fn inspect<'tcx>(tcx: TyCtxt<'tcx>, ty: rustc_middle::ty::Ty<'tcx>) -> bool {
-/// Describe a call whose memory effects cannot be tracked by the uninitialized-memory passes.
+/// Describe an unsupported call encountered during memory initialization checks.
diff --git a/tests/expected/uninit/unresolved-calls/direct-seeded.rs b/tests/expected/uninit/unresolved-calls/direct-seeded.rs
index 70ae032c0..8b0d53f5d 100644
--- a/tests/expected/uninit/unresolved-calls/direct-seeded.rs
+++ b/tests/expected/uninit/unresolved-calls/direct-seeded.rs
@@ -11 +11 @@ fn direct(value: u8) -> u8 {
-// A copy intrinsic creates a delayed-UB analysis target without introducing UB.
+// The copy intrinsic initializes the destination and creates an analysis target.
diff --git a/tests/expected/uninit/unresolved-calls/entry-initialized-plain.rs b/tests/expected/uninit/unresolved-calls/entry-initialized-plain.rs
index 63accc842..ffb8d69ed 100644
--- a/tests/expected/uninit/unresolved-calls/entry-initialized-plain.rs
+++ b/tests/expected/uninit/unresolved-calls/entry-initialized-plain.rs
@@ -18,2 +18,2 @@ fn identity(value: u32) -> u32 {
-// No statements in bb0: LoadArgument and the union-field Check share the
-// unresolved Call's target. The initialized control requires the load to survive.
+// The call is the first instruction in the entry block. Loading the initialized union
+// parameter's memory initialization state allows the argument check to succeed.
diff --git a/tests/expected/uninit/unresolved-calls/entry-initialized-seeded.rs b/tests/expected/uninit/unresolved-calls/entry-initialized-seeded.rs
index f3bb16388..d20b6b18a 100644
--- a/tests/expected/uninit/unresolved-calls/entry-initialized-seeded.rs
+++ b/tests/expected/uninit/unresolved-calls/entry-initialized-seeded.rs
@@ -18,2 +18,2 @@ fn identity(value: u32) -> u32 {
-// No statements in bb0: LoadArgument and the union-field Check share the
-// unresolved Call's target. The initialized control requires the load to survive.
+// The call is the first instruction in the entry block. Loading the initialized union
+// parameter's memory initialization state allows the argument check to succeed.
@@ -29 +29 @@ unsafe fn indirect(value: Word, f: fn(u32) -> u32) -> u32 {
-// A copy intrinsic creates a delayed-UB analysis target without introducing UB.
+// The copy intrinsic initializes the destination and creates an analysis target.
diff --git a/tests/expected/uninit/unresolved-calls/entry-partial-plain.rs b/tests/expected/uninit/unresolved-calls/entry-partial-plain.rs
index 416ffd275..14dcc843c 100644
--- a/tests/expected/uninit/unresolved-calls/entry-partial-plain.rs
+++ b/tests/expected/uninit/unresolved-calls/entry-partial-plain.rs
@@ -19,2 +19,2 @@ fn identity(value: u32) -> u32 {
-// No statements in bb0: preserve the entry LoadArgument and the Check
-// collected from the union field used as the call argument.
+// The call is the first instruction in the entry block. Loading the union parameter's
+// memory initialization state precedes checking the union field used as an argument.
diff --git a/tests/expected/uninit/unresolved-calls/entry-partial-seeded.rs b/tests/expected/uninit/unresolved-calls/entry-partial-seeded.rs
index 2d7acde7e..bff214ede 100644
--- a/tests/expected/uninit/unresolved-calls/entry-partial-seeded.rs
+++ b/tests/expected/uninit/unresolved-calls/entry-partial-seeded.rs
@@ -19,2 +19,2 @@ fn identity(value: u32) -> u32 {
-// No statements in bb0: preserve the entry LoadArgument and the Check
-// collected from the union field used as the call argument.
+// The call is the first instruction in the entry block. Loading the union parameter's
+// memory initialization state precedes checking the union field used as an argument.
@@ -30 +30 @@ unsafe fn indirect(value: Word, f: fn(u32) -> u32) -> u32 {
-// A copy intrinsic creates a delayed-UB analysis target without introducing UB.
+// The copy intrinsic initializes the destination and creates an analysis target.
diff --git a/tests/expected/uninit/unresolved-calls/erased-pointer-plain.rs b/tests/expected/uninit/unresolved-calls/erased-pointer-plain.rs
index a704098b4..5d0dc55cc 100644
--- a/tests/expected/uninit/unresolved-calls/erased-pointer-plain.rs
+++ b/tests/expected/uninit/unresolved-calls/erased-pointer-plain.rs
@@ -20 +20 @@ fn check() {
-    // c_void and u8 have the same one-byte data layout; erasure itself adds no seed.
+    // The raw-pointer cast erases the pointee type while preserving its address.
diff --git a/tests/expected/uninit/unresolved-calls/erased-pointer-seeded.rs b/tests/expected/uninit/unresolved-calls/erased-pointer-seeded.rs
index 35261d078..3f4f913a5 100644
--- a/tests/expected/uninit/unresolved-calls/erased-pointer-seeded.rs
+++ b/tests/expected/uninit/unresolved-calls/erased-pointer-seeded.rs
@@ -17 +17 @@ fn indirect(f: fn(*mut c_void), pointer: *mut c_void) {
-// A copy intrinsic creates a delayed-UB analysis target without introducing UB.
+// The copy intrinsic initializes the destination and creates an analysis target.
@@ -30 +30 @@ fn check() {
-    // c_void and u8 have the same one-byte data layout; erasure itself adds no seed.
+    // The raw-pointer cast erases the pointee type while preserving its address.
diff --git a/tests/expected/uninit/unresolved-calls/fn-pointer-seeded.rs b/tests/expected/uninit/unresolved-calls/fn-pointer-seeded.rs
index 844037d99..0d606c30c 100644
--- a/tests/expected/uninit/unresolved-calls/fn-pointer-seeded.rs
+++ b/tests/expected/uninit/unresolved-calls/fn-pointer-seeded.rs
@@ -15 +15 @@ fn identity(value: u8) -> u8 {
-// A copy intrinsic creates a delayed-UB analysis target without introducing UB.
+// The copy intrinsic initializes the destination and creates an analysis target.
diff --git a/tests/expected/uninit/unresolved-calls/fn-trait-pointer-plain.rs b/tests/expected/uninit/unresolved-calls/fn-trait-pointer-plain.rs
index da67d225c..a3ace5b7b 100644
--- a/tests/expected/uninit/unresolved-calls/fn-trait-pointer-plain.rs
+++ b/tests/expected/uninit/unresolved-calls/fn-trait-pointer-plain.rs
@@ -14,2 +14 @@ fn indirect(f: fn(u8) -> u8) -> u8 {
-    // Fn-trait invocation of a function pointer reaches the FnPtr boundary.
-    // This is not coverage of a bodyless or direct-shadow Shim guard.
+    // Calling this function pointer through the Fn trait reaches an indirect call.
diff --git a/tests/expected/uninit/unresolved-calls/fn-trait-pointer-seeded.rs b/tests/expected/uninit/unresolved-calls/fn-trait-pointer-seeded.rs
index dee00b651..721d1e31f 100644
--- a/tests/expected/uninit/unresolved-calls/fn-trait-pointer-seeded.rs
+++ b/tests/expected/uninit/unresolved-calls/fn-trait-pointer-seeded.rs
@@ -14,2 +14 @@ fn indirect(f: fn(u8) -> u8) -> u8 {
-    // Fn-trait invocation of a function pointer reaches the FnPtr boundary.
-    // This is not coverage of a bodyless or direct-shadow Shim guard.
+    // Calling this function pointer through the Fn trait reaches an indirect call.
@@ -19 +18 @@ fn indirect(f: fn(u8) -> u8) -> u8 {
-// A copy intrinsic creates a delayed-UB analysis target without introducing UB.
+// The copy intrinsic initializes the destination and creates an analysis target.
diff --git a/tests/expected/uninit/unresolved-calls/generated-positive-plain.rs b/tests/expected/uninit/unresolved-calls/generated-positive-plain.rs
index f7b5f74eb..81fe807d8 100644
--- a/tests/expected/uninit/unresolved-calls/generated-positive-plain.rs
+++ b/tests/expected/uninit/unresolved-calls/generated-positive-plain.rs
@@ -12,2 +12 @@ fn identity(value: u8) -> u8 {
-// A non-shadow function-item Fn-trait call is a positive generated-body probe.
-// Actual instance kind/body and property reachability require pinned CI MIR binding.
+// The function item is passed through the generic Fn-trait call below.
diff --git a/tests/expected/uninit/unresolved-calls/generated-positive-seeded.rs b/tests/expected/uninit/unresolved-calls/generated-positive-seeded.rs
index fa75e3f4b..e3d0f81af 100644
--- a/tests/expected/uninit/unresolved-calls/generated-positive-seeded.rs
+++ b/tests/expected/uninit/unresolved-calls/generated-positive-seeded.rs
@@ -12,2 +12 @@ fn identity(value: u8) -> u8 {
-// A non-shadow function-item Fn-trait call is a positive generated-body probe.
-// Actual instance kind/body and property reachability require pinned CI MIR binding.
+// The function item is passed through the generic Fn-trait call below.
@@ -26 +25 @@ fn drop(&mut self) {
-// A copy intrinsic creates a delayed-UB analysis target without introducing UB.
+// The copy intrinsic initializes the destination and creates an analysis target.
diff --git a/tests/expected/uninit/unresolved-calls/global-escaped-plain.rs b/tests/expected/uninit/unresolved-calls/global-escaped-plain.rs
index e94bd9e45..94b890dcc 100644
--- a/tests/expected/uninit/unresolved-calls/global-escaped-plain.rs
+++ b/tests/expected/uninit/unresolved-calls/global-escaped-plain.rs
@@ -14 +14 @@ fn indirect(f: fn()) {
-    // There is no pointer argument or return value to gate instrumentation on.
+    // The callee accesses memory through a global pointer.
diff --git a/tests/expected/uninit/unresolved-calls/global-escaped-seeded.rs b/tests/expected/uninit/unresolved-calls/global-escaped-seeded.rs
index 976a97864..9ade469d6 100644
--- a/tests/expected/uninit/unresolved-calls/global-escaped-seeded.rs
+++ b/tests/expected/uninit/unresolved-calls/global-escaped-seeded.rs
@@ -14 +14 @@ fn indirect(f: fn()) {
-    // There is no pointer argument or return value to gate instrumentation on.
+    // The callee accesses memory through a global pointer.
@@ -18 +18 @@ fn indirect(f: fn()) {
-// A copy intrinsic creates a delayed-UB analysis target without introducing UB.
+// The copy intrinsic initializes the destination and creates an analysis target.
diff --git a/tests/expected/uninit/unresolved-calls/pending-ops-plain.rs b/tests/expected/uninit/unresolved-calls/pending-ops-plain.rs
index 2cba767a5..072d3a7cb 100644
--- a/tests/expected/uninit/unresolved-calls/pending-ops-plain.rs
+++ b/tests/expected/uninit/unresolved-calls/pending-ops-plain.rs
@@ -15,2 +15 @@ fn identity(value: u8) -> u8 {
-// The dereference is an operand of the Call terminator, so super_terminator
-// collects its Check before resolution fails. It must precede Unsupported.
+// Check the dereferenced call argument before reporting the unsupported function-pointer call.
@@ -28 +27 @@ fn check() {
-    // Raw byte storage avoids the unsupported raw-pointer/union interaction.
+    // Allocate two bytes and initialize the first byte.
diff --git a/tests/expected/uninit/unresolved-calls/pending-ops-seeded.rs b/tests/expected/uninit/unresolved-calls/pending-ops-seeded.rs
index 0157cfe34..8a3f32544 100644
--- a/tests/expected/uninit/unresolved-calls/pending-ops-seeded.rs
+++ b/tests/expected/uninit/unresolved-calls/pending-ops-seeded.rs
@@ -15,2 +15 @@ fn identity(value: u8) -> u8 {
-// The dereference is an operand of the Call terminator, so super_terminator
-// collects its Check before resolution fails. It must precede Unsupported.
+// Check the dereferenced call argument before reporting the unsupported function-pointer call.
@@ -26 +25 @@ unsafe fn indirect(f: fn(u8) -> u8, pointer: *const u8) -> u8 {
-// A copy intrinsic creates a delayed-UB analysis target without introducing UB.
+// The copy intrinsic initializes the destination and creates an analysis target.
@@ -38 +37 @@ fn check() {
-    // Raw byte storage avoids the unsupported raw-pointer/union interaction.
+    // Allocate two bytes and initialize the first byte.
diff --git a/tests/expected/uninit/unresolved-calls/virtual-seeded.rs b/tests/expected/uninit/unresolved-calls/virtual-seeded.rs
index be2b16bb0..a8f4a7246 100644
--- a/tests/expected/uninit/unresolved-calls/virtual-seeded.rs
+++ b/tests/expected/uninit/unresolved-calls/virtual-seeded.rs
@@ -21 +21 @@ fn indirect(writer: &dyn Writer, pointer: *mut u8) {
-// A copy intrinsic creates a delayed-UB analysis target without introducing UB.
+// The copy intrinsic initializes the destination and creates an analysis target.
diff --git a/tests/expected/uninit/unresolved-calls/wrapped-pointer-seeded.rs b/tests/expected/uninit/unresolved-calls/wrapped-pointer-seeded.rs
index d461fcb50..384afcb62 100644
--- a/tests/expected/uninit/unresolved-calls/wrapped-pointer-seeded.rs
+++ b/tests/expected/uninit/unresolved-calls/wrapped-pointer-seeded.rs
@@ -19 +19 @@ fn indirect(f: fn(Wrapped), wrapper: Wrapped) {
-// A copy intrinsic creates a delayed-UB analysis target without introducing UB.
+// The copy intrinsic initializes the destination and creates an analysis target.
```
