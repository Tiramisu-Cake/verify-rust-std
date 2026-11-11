# KANI3300 G1R2 — static test compilation sweep
Scope: all 23 G1 fixtures (154 harnesses), shared types.inc, all goldens; compiler/native NOT_RUN; Cloud $0, proof credit NONE.
Candidate `02b734151ada1dd0d216b0db329776eb522d2d67`; parent/unchanged production `3d085249c9c6c49a9c2e5747e2167d629748fb70`.
Paths below are relative to Kani; fixture prefix is `tests/expected/uninit/g1-union-pointee-`.
`rust-toolchain.toml:6`: nightly-2026-10-23; exact Rust commit 7189d39d9ce936881b8132c6addeaf3e295cd455; source identities in RUST-SOURCES.json.
`positive/main.rs:3`, `negative/main.rs:3`, all 21 rejection main.rs:3: edition 2021, unchanged; explicit unsafe blocks also satisfy unsafe_op_in_unsafe_fn for the two tail helpers.
`tools/compiletest/src/header.rs:56`, `runtest.rs:359`: fixture compile-flags forwarded as RUSTFLAGS; all G1 files/includes have no deny/forbid or -D flags; warnings remain nonfatal.
`positive/main.rs:565,580`, `negative/main.rs:665,680`: union holder.ptr reads now explicitly unsafe; subsequent raw copies and delayed local reads unchanged.
`positive/main.rs:59,64,71–685`, `negative/main.rs:65,70,77–794`: reviewed raw dereferences, union reads, pointer arithmetic/copy/write and intrinsic calls; unsafe operations remain in explicit blocks; union construction and field assignment distinguished from reads.
Nightly `compiler/rustc_lint/src/autorefs.rs:61,102–114,154–160`: Deny; lint peels fields/indexing to raw dereference, including overloaded ManuallyDrop::deref, so aggregate fixtures also needed repair.
`positive/main.rs:331–368,386,406,416,673,683`: 15 formerly implicit ManuallyDrop borrows now explicit; same scalar/tuple/array projection and assertions.
`negative/main.rs:338,347,359,371,392,405,452,466`: 8 formerly implicit ManuallyDrop borrows now explicit; same padding addresses, sub(1), and byte reads.
`unsupported-reject_manuallydrop_union/main.rs:13`: (&*p).wide makes the existing wrapper borrow explicit; no lint allow or pointer cast bypass.
Same wrapper guard: `ptr_uninit/uninit_visitor.rs:513–521` under `kani-compiler/src/kani_middle/transform/check_uninit/`; assignment of ManuallyDrop<U> still passes through PointeeInfo::from_ty.
`ty_layout.rs:262–271` in that directory: recurse into ManuallyDrop<U> with allow_union=false → UnionAsField(U); diagnostic and golden unchanged.
`unsupported-reject_union_transmute/main.rs:8–12`: local repr(C, align(8)) TransmuteU { bytes:[u8;5], word:u32 }; size rounds to 8, matching [u64;1], so no E0422/E0512; shared helper unchanged.
`unsupported-reject_union_transmute/main.rs:16–17`: original construction/transmute retained; `ptr_uninit/uninit_visitor.rs:1015–1028` rejects ordinary union transmute as TriviallyUnsafe; same safety_check golden.
`unsupported/types.inc:4–68`: names/imports, Copy members/derives, union field restrictions, foreign declarations and signatures checked; includes resolve for all 21 selectors; TransmuteU supplied only in its own fixture.
`positive/main.rs:17–56,132–141,612–642`, `negative/main.rs:17–61,149–158,720–731`: types, moves/borrows, array lengths/index bounds, thin/fat pointers, scalar inference and align(8) backing checked; no new blocker found statically.
`unsupported-reject_{select_unpredictable,typed_swap,forget_union_array}/main.rs:5–15`, `negative/main.rs:5,777–794`: feature(core_intrinsics) present; pinned core signatures select_unpredictable<T>, typed_swap_nonoverlapping<T>(*mut T,*mut T), forget<T>(T) match.
Nightly deny checks: dangerous_implicit_autorefs fixed without allows; invalid_reference_casting has no shared-reference-to-mutable write; no fabricated invalid/null values, constant arithmetic overflow, unconditional out-of-bounds/panic, or duplicate/conflicting attrs found.
Unused imports/types/fields in shared helper, unused assignment and unnecessary unsafe around safe intrinsics remain warnings; no deny(warnings), deny(unused) or CI flag introduced.
`unsupported-reject_init_predicate/main.rs:12` → `library/kani_core/src/mem.rs:73–79` can_dereference → `:254–258` assert_is_initialized → `:246–250` marked is_initialized intrinsic.
`kani-compiler/src/kani_middle/transform/kani_intrinsics.rs:207–210,359–370`: that intrinsic body inserts Unsupported for PointeeLayout::Union with the exact intended reason; this is the original initialization-predicate guard, not a different rejection.
`library/kani/src/lib.rs:63` expands kani_core::kani_lib!(kani); the intrinsic's expanded definition explains the reported library location and owner `kani::mem::is_initialized::<U>`.
Only golden change: `unsupported-reject_init_predicate/expected:1` now exact `kani::mem::is_initialized::<U>.unsupported_construct.1`; FAILURE, reason, named harness and 0/1/1 summary retained (G1RA observed identity; no new run claimed).
All other rejection property names/classes checked against source guard placement: caller guards remain harness-owned; four existing diagnostic-only goldens retain exact reason + named failure/summary; no additional naming mismatch identified statically.
Positive 63 and negative 70 harness names/order, expected outcomes/types/diagnostics and both complete goldens unchanged; negative golden still binds each of 70 named safety_check failures and reading types.
Manifest changes limited to candidate/source hashes, bodies at repaired lines and the one predicate property binding; all package B entries and fixtures unchanged.
Permitted rustfmt wrapper --check --edition 2024 (formatting only) with repository config/skip_children passed for all 24 Rust/include files; git diff --check passed.
Validation is source inspection, formatting and static inventory only; compilation, nightly lint execution, MIR lowering and actual property outcomes await separate GO.
