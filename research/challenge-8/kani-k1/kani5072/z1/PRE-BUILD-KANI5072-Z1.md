# PRE-BUILD — KANI5072 Z1

Candidate: the full verify-rust-std commit in the final PRE-BUILD REVIEW marker. Dispatch requires coordinator GO for that exact packet.
Worktree `/root/verify-rust-std-kani5072`; branch `experiment/kani-k1-kani5072-20261111`.
Slug `kani5072`; stage `kani5072-z1`; stable owner `k1-merge`; request `kani5072-z1-main-20261111-01`.
Runtime Codex; task window main 300 + closeout 30 minutes. This packet does not open a Cloud phase or reset any T0.

## Identities

- Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, toolchain `nightly-2026-10-23`; neither changed.
- Accepted tooling base `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`. All lane/tool/workflow/config paths match that base.
- Local Kani branch `fix/volatile-zst-5072`, commit `6fba5bf9254f4954dd6dbce6ece8ef159004e905`; official origin only, no Kani push.
- Patch `kani-fix.patch`, SHA-256 `380b22438bbdd115d98aacc81f97a49cce24e9abf77fa176c32067210e8ff238`; includes all three new Rust fixtures and both new goldens.
- Request SHA-256 `adbeda538f3c142a3748b1f498c8aae6480e89b1a75e9c104866d61a1d588bdf`.
- Fresh-pin applied tree `f3791c8eb38f92bc331bf8b8c63cda0bc22b9db4` equals the local Kani commit tree.
- Exact local std contract: `library/core/src/ptr/mod.rs`, Git blob `4121d40b756291492fef9360b6e4ac2327c5d478`, lines 2083–2178.

## Static semantic gate

The pinned local `read_volatile` contract explicitly exempts ZSTs from readable-storage validity, requires alignment even at size zero, and requires a valid initialized result.
[Official Rust docs](https://doc.rust-lang.org/nightly/core/ptr/fn.read_volatile.html) agree (consulted 2026-11-11; rendered snapshot identifies 1.101.0-nightly, commit 282215592, 2026-10-04). The moving docs page is corroboration; the exact local source identity above is the pinned contract.
For an inhabited ZST, null therefore satisfies this contract: no memory is accessed and address zero is aligned. No non-null assertion is added. This conclusion concerns runtime volatile reads.
The existing alignment assertion remains before the ZST result. `Expr::init_unit` provides an existing typed zero-size initializer, with no source dereference.
The returning intrinsic path checks an uninhabited ZST before constructing a value. For a ZST intrinsic with no return target, an arm guarded by both zero size and uninhabited layout now emits the same explicit uninhabited-value SafetyCheck. Both MIR call shapes therefore reject uninhabited ZSTs with the same diagnostic; non-ZST non-returning handling remains unchanged.
Non-ZST lowering keeps the same dereference, result assignment and alignment check. No CBMC/pointer-model change or extension of non-ZST MMIO support is claimed. Existing initialization/validity instrumentation and its known limitations are unchanged.

## Production diff

One production file, +30/-2; five new test/golden files, +90/-0. No existing fixture or golden changed.
All six changed paths are under `kani-compiler/src/codegen_cprover_gotoc/` or `tests/`.

```diff
diff --git a/kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs b/kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs
index 3d87436..d32674c 100644
--- a/kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs
+++ b/kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs
@@ -88,6 +88,19 @@ pub fn codegen_never_return_intrinsic(&mut self, instance: Instance, span: Span)
                 "transmuting to uninhabited type has undefined behavior",
                 span,
             ),
+            // Reject uninhabited ZST results even when MIR has no return target.
+            "volatile_load"
+                if {
+                    let ret_ty = instance.ty().kind().fn_sig().unwrap().skip_binder().output();
+                    self.is_zst_stable(ret_ty) && self.layout_of_stable(ret_ty).is_uninhabited()
+                } =>
+            {
+                self.codegen_fatal_error(
+                    PropertyClass::SafetyCheck,
+                    "volatile load of an uninhabited type has undefined behavior",
+                    span,
+                )
+            }
             _ => self.codegen_fatal_error(
                 PropertyClass::UnsupportedConstruct,
                 &format!("Unsupported intrinsic {intrinsic}"),
@@ -1897,7 +1910,7 @@ fn codegen_intrinsic_simd_shuffle(
     /// <https://doc.rust-lang.org/std/ptr/fn.read_volatile.html>
     ///
     /// Undefined behavior if any of these conditions are violated:
-    ///  * `src` must be valid for writes (done by `--pointer-check`)
+    ///  * For non-ZSTs, `src` must be valid for reads (done by `--pointer-check`)
     ///  * `src` must be properly aligned (done by `align_check` below)
     ///
     /// TODO: Add a check for the condition:
@@ -1919,7 +1932,22 @@ fn codegen_volatile_load(
             "`src` must be properly aligned",
             loc,
         );
-        let expr = src.dereference();
+        let pointee_type = pointee_type_stable(src_typ).unwrap();
+        let expr = if self.is_zst_stable(pointee_type) {
+            // ZST reads do not access memory, but still require alignment and a valid value.
+            if self.layout_of_stable(pointee_type).is_uninhabited() {
+                let validity_check = self.codegen_assert_assume_false(
+                    PropertyClass::SafetyCheck,
+                    "volatile load of an uninhabited type has undefined behavior",
+                    loc,
+                );
+                return Stmt::block(vec![align_check, validity_check], loc);
+            }
+            let typ = self.codegen_ty_stable(pointee_type);
+            Expr::init_unit(typ, &self.symbol_table)
+        } else {
+            src.dereference()
+        };
         let res_stmt = self.codegen_expr_to_place_stable(p, expr, loc);
         Stmt::block(vec![align_check, res_stmt], loc)
     }
```

## Exact typed manifest — 8 selectors

The following is the full `manifest.json`, exactly equal to request `kani_tests`:

```json
[
  {
    "suite": "kani",
    "mode": "kani",
    "file": "Intrinsics/Volatile/load_zst.rs",
    "expect": "pass",
    "require_success": true
  },
  {
    "suite": "expected",
    "mode": "expected",
    "file": "intrinsics/volatile_load/zst_unaligned.rs",
    "expect": "pass",
    "require_success": false,
    "diagnostic": "`src` must be properly aligned"
  },
  {
    "suite": "expected",
    "mode": "expected",
    "file": "intrinsics/volatile_load/zst_uninhabited.rs",
    "expect": "pass",
    "require_success": false,
    "diagnostic": "volatile load of an uninhabited type has undefined behavior"
  },
  {
    "suite": "kani",
    "mode": "kani",
    "file": "Intrinsics/Volatile/load.rs",
    "expect": "pass",
    "require_success": true
  },
  {
    "suite": "kani",
    "mode": "kani",
    "file": "Intrinsics/Volatile/store.rs",
    "expect": "pass",
    "require_success": true
  },
  {
    "suite": "kani",
    "mode": "kani",
    "file": "Intrinsics/Volatile/unaligned.rs",
    "expect": "pass",
    "require_success": true
  },
  {
    "suite": "expected",
    "mode": "expected",
    "file": "intrinsics/volatile_load/unaligned/main.rs",
    "expect": "pass",
    "require_success": false,
    "diagnostic": "`src` must be properly aligned"
  },
  {
    "suite": "expected",
    "mode": "expected",
    "file": "intrinsics/unaligned_volatile/out_of_bounds/main.rs",
    "expect": "pass",
    "require_success": false,
    "diagnostic": "dereference failure: pointer outside object bounds"
  }
]
```

New positive fixture: six harnesses cover original `read_volatile(&())`, NonNull dangling unit, over-aligned ZST, null unit/over-aligned ZST, direct intrinsic calls, and aggregate ZST results.
New negative alignment fixture uses the direct intrinsic so the retained compiler alignment assertion is tested without a public-wrapper precondition masking it.
New negative uninhabited fixture requires the explicit uninhabited-value SafetyCheck, shared by returning and non-returning ZST lowering. Native observation of every golden and diagnostic is pending; none is recorded as observed evidence.
Existing controls: load, store, unaligned byte precision; negative aligned-volatile non-ZST misalignment; negative unaligned-volatile non-ZST bounds.
Every negative has `expect: pass`, `require_success: false` and a specific own-child-output diagnostic; its native PASS must match the expected failing check. An unexpected negative SUCCESS is a blocker.
Declared NOT_RUN: `kani/VolatileIntrinsics/main_fixme.rs` and all other `fixme_*` fixtures; full upstream CI and the remaining matrix. No ignored/fixme test is selected.

## Static validation

- Request/schema and typed manifest: PASS, 8 selectors <= 20; all positive entries require success.
- Fresh clean detached pin: unchanged runner `prepare_kani` performs `git apply --check --index`, applies the exact hashed bytes, verifies all eight fixtures and four required golden files, and produces the matching tree above.
- All new Rust fixtures have Kani SPDX/copyright and edition-2021 compile flags. Existing goldens are unchanged.
- Pinned rustfmt wrapper with clone rustfmt.toml: zero diff for the production file (edition 2024) and all three new fixtures (edition 2021).
- `git diff --check`: PASS; no changes outside the allowed directories in Kani; source clone clean after commit.
- No runner/tooling changes, so no new service error paths are introduced. No local cargo/rustc/Kani/CBMC execution.
- Independent GPT-6 Luna HIGH review: PASS for final Kani candidate `6fba5bf9254f4954dd6dbce6ece8ef159004e905`; two localized findings resolved and checked by the same reviewer. Exact spec/packet/diff identities and verdict are in `INDEPENDENT-REVIEW.md`; native tests remain pending.

## Budget and dispatch boundary

One proposed `kani-tests` Build, standard4: 5 work minutes + unchanged 30 overhead = 35 paid minutes.
At $0.0135/min, maximum reservation is **$0.4725 <= own $0.50 cap**; own actual/reserved at preparation is $0/$0. Unreserved margin $0.0275.
The runner verification cutoff is start + (5 + 24) = 29 minutes, leaving six minutes before the Cloud timeout for closeout. Per-selector timeout is 180 seconds; selectors run serially.
No slot or money is reserved by preparing this packet. Project-wide nightly cap <= $6.40 and competing owner/phase slots must be checked by the coordinator at exact-packet GO; this task does not authorize changing global caps or ledgers.
Read-only project ledger snapshot during preparation: 267 builds, $112.6545 used, $0.6750 reserved, $118.96 infrastructure cap. Adding this reservation gives $113.8020; this changing global ledger does not establish the separate nightly $6.40 allowance. No ledger was changed.
A repeat requires actual cost + its full new reservation <= $0.50 and another exact-packet GO. At the same reservation, that requires actual first-build cost <= $0.0275; no automatic retry.
After GO only: publish-source identity recheck, existing coordinator dispatch, `k1g.sh watch BUILD`, then end turn. Evidence only bounded `k1g.sh summary/native`; no raw logs, archives or credentials.
On completion check native names, own diagnostics, no ignored/TIMEOUT, patch/request/pin/applied-tree identity, unchanged tooling and own cost. Then update RESULT and PR draft, submit REVIEW REQUEST or completion marker, and stop.
