# KANI3300 A3R — independent static review

## Identity

- Baseline: `585c93b2ff366f5723611a7ca944328ef62f40b5`
- Candidate: `c57314d4cf8aed4721c3170827827c6c9b9cd429`
- Candidate tree: `1985bfcdc80f2f864b56a8983ebc7e63652a1c55`
- Diff SHA-256: `9fc942443b52a0092bf34665fe982c6c0bd6e1dcbf9f8ee5696fb8d0ea73f879`
- Spec SHA-256: `9e7eb656d63cf1e70ae4f3da2a17d7b9bd6eaa8ce8f80fea70837cb68c3361e2`
- Review packet SHA-256 supplied with the handoff: `a13bdcde06be459caaf151a220b8d2f7ab3cb0a0ee42fca13e50f0d751e8e519`
- Packet inventory: all 26 listed file hashes match; spec and diff hashes independently match. Candidate `HEAD` and tree match the identities above; baseline commit resolves.

## Verdict: changes requested

### Finding — intrinsic exemption drops `BlackBox` shadow transfers

At `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs:509-512`, the caller guard now exempts every `InstanceKind::Intrinsic` from the paired-transfer requirement. `Intrinsic::BlackBox` is included in `can_skip_intrinsic` (around line 951), so a call with a shadow-carrying `MaybeUninit<T>` argument and result reaches the skip arm without any argument/return shadow operation. Kani's codegen explicitly implements `BlackBox` as an identity copy at `kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs:332-334`; the value transfer therefore has no corresponding shadow-witness transfer in this visitor. The source object’s tracked initialization state can be left associated with the old place while the returned value occupies the destination. This is an unmodeled shadow transfer and can cause stale or incorrect initialization classification. Add a shadow-transfer model for this identity intrinsic, or retain an unsupported diagnostic for shadow-carrying `BlackBox` calls; keep the no-effect `Forget` handling separate.

This finding is based on source semantics; no runtime manifestation was measured. Unknown intrinsics still reach the explicit `Unsupported` arm, and non-intrinsic shims/bodyless transfers remain guarded.

## Other reviewed invariants

- The changed `written` assertions retain the signature/count checks and strengthen branch checks: selected argument zero requires count zero and exactly one write; positive argument selections require positive count and exactly `argument_count` writes. Existing index, layout-size, remaining-load, selected-return, and end-of-protocol assertions remain.
- Caller snapshots precede `Call(Move)` resets; reset targets the exact moved shadow place. Copy operands and ordinary assignment paths are unchanged. The `Forget` intrinsic path still has no source reset.
- The custom MIR `Call` syntax accepts `UnwindUnreachable` in the pinned `core::intrinsics::mir` API. Kani’s driver configures `panic=abort`; fixture changes replace unwind actions and leave harnesses/assertions intact. No expected golden file is changed by this candidate.
- The patch adds no imports, locals, API signatures, or enum variants. No source-level clippy/`-D warnings` issue was identified in the changed Rust lines; this is not a compiler result.

## Limits

Static source review only. Compilation, formatting/clippy execution, Kani, CBMC, Miri, and CI were not run. The reported extra uninitialized-read regressions and their absence cannot be established without the coordinator’s authorized validation. No proof credit is claimed; Cloud spend is `$0`.
