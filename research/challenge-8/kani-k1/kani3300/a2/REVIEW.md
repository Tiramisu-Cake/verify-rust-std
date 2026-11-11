# KANI3300 A2 static review

- Reviewed semantic candidate (before test-only follow-ups): `b8c0d00ac3ab00eefaa22396274af4e9d2b15450`, tree `84d000bffab31216aa31cef40befdf266f047d3f`
- Baseline: `613c188313e34e51e6a69d2c62bbd6ded2511819`
- Semantic patch packet: candidate `1dc99da6bf3c6387d8f69d9a44ffa8a8e0419139`, tree `b5ae9ea9b93eb0c7f030d969151d472b8e01c73d`, packet SHA `7b1afb2109c5831d781bff631d013eea65f9500f5bd786d1f6b982640bffde7a`, diff SHA256 `59dbfca578144032457af4f9150d11891082b4b5b483c0c67f3a96d5b5b04bf4`, spec SHA256 `8a4b71411d628ad908bc34199eed17431d19135f3f22ed0981ca2e6665d85807`
- Golden correction delta: baseline `1dc99da6bf3c6387d8f69d9a44ffa8a8e0419139`, candidate `b8c0d00ac3ab00eefaa22396274af4e9d2b15450`, packet SHA `5acbce315f2a4ab71be39d5b0dd93321212d221ada9e5088b8e84f03f3d90b88`, diff SHA256 `353f1e0a14a5ba54aa528725455d72dfd9f783c045e5c06f659ced0046231f83`, spec SHA256 `2f67e0dbd98fca2fff51d728775fcc84914e4719dbf6988c8e8ab381b8b1c3a4`

## Findings and assessment

The initial semantic packet's added expected files used `Test:` labels, inconsistent with the pinned `harness_runner.rs`, which emits `Checking harness NAME...`. The final delta fixes the six new goldens to the runner's header and retains diagnostics, failure expectations, and totals. No remaining static finding in the reviewed scope.

The source changes appear consistent with A2: `RigidTy::Pat` forwards the existing offset; nested enum variant masks are compared in enum-local coordinates and the chosen mask receives the enclosing offset once; unequal masks remain Unsupported. The nested wide-pointer Pat fixtures use nonzero member offset. The padding fixture's MaybeUninit transfer is handled through `for_typed_storage`; `build_assign_union` applies the computed payload mask, so initialized source padding is cleared on transfer and the byte-1 read distinguishes the corrected offset from the old reset-to-zero behavior. Same-layout and differing-padding enum fixtures cover positive and Unsupported outcomes. The reverse array transmute guard covers equal-length `[MaybeUninit<T>; N] -> [T; N]`, distinct from the existing forward storage conversion. `RawEq` is no longer skipped and is explicitly Unsupported because it reads all bytes through references.

**Verdict: static review passes for semantic candidate `b8c0d00` and the final fixture-only candidate `3dc0227`.** No obvious source-level type/import/borrow/unused issue was found. No formatting wrapper, compiler, clippy, Kani, MIR/layout measurement, or coordinator CI was run; compilation and runtime outcomes remain unverified. A1 remains a dependency, not newly proved. No proof credit or GO is claimed.

## Test-only follow-up

- Final candidate: `3dc0227cee87d85bed32678a2209353ebdb9d2fa`, tree `6e32e075432994b45a180c7da27750ba7de0526a`
- Follow-up baseline: `b8c0d00ac3ab00eefaa22396274af4e9d2b15450`
- Scope: only `maybe-uninit-array-reverse-unsupported/main.rs` and `nested-enum-same-padding/main.rs` changed.

The reverse-array fixture now asserts scalar elements individually, avoiding a second `raw_eq` diagnostic after the explicit transmute guard. The positive nested enum fixture compares its 16 prefix bytes in a fixed loop with unwind 17, avoiding array `PartialEq` while retaining the byte and enum-payload assertions. No concrete issue found in this delta.

**Compatibility scope:** the blanket `RawEq` Unsupported boundary also rejects standard-library bytewise array equality when `-Z uninit-checks` is enabled, including equality on initialized arrays. Existing suites that reach this intrinsic require coordinator accounting; this review makes no overall full-regression PASS claim. Static-only limitations above still apply.

- Immutable follow-up fixture packet SHA: `eb4e011665faa193c6c9299600f28328aaa84ff1b0ae78a94acbcd2031ae3fde`
- Follow-up diff SHA256: `3cef18e7bfc9ce4306ba5f5e84d3c912f53c5699c92f4ea6d3c1cc917805dbfd`
- Follow-up spec SHA256: `7a7ef9e6544f3011d86c8975d5c88cff72f2f45f39b75827f95fe78846350477`

The raw_eq restriction is an intentional A2 support boundary for this stage, not a claim that all std array equality remains supported under `-Z uninit-checks`. A concrete existing caller is `tests/expected/uninit/maybe-uninit-transmute/main.rs::exact_usize_array_copy`, whose final whole-array `assert_eq!` may reach array `PartialEq`'s raw_eq specialization; its historical expected success is unchanged and is not asserted to pass here. Coordinator accounting must keep such compatibility failures distinct from the new A2 layout controls. This review does not claim an overall full-regression PASS.
