# Independent static review — SEL1 candidate

**Candidate:** `52f2ef41f9f3c81c42e1207981b0e28a9171bdf2`  
**Base:** `69b13711e60a87458200833445d47488ab466344`  
**Review packet inventory SHA256:** `d859f27caf97595951a9650d3bbd4455d8bca30d836a7607d2d10b34cf9089c9`  
**Spec SHA256:** `af5ab377421302f07dec8814d2b0446c5b4a11b3296e5b035dfc0e93594c87c5`

## Findings

No blocking static correctness findings identified in the committed semantic diff.

## Review notes

- The shared `has_intrinsic_fallback` predicate keeps codegen and reachability on the existing `!must_be_overridden && has_body` rule. The more restrictive select classifier additionally checks the exact `core::intrinsics::select_unpredictable` item, intrinsic instance kind, `(bool, T, T) -> T` signature, non-variadic call, and checked body.
- Caller and fallback entry derive shadow argument positions from the same `transfers_shadow` predicate. The caller emits paired stores, then snapshots each `Move` source as deinitialized; `Copy` operands are left live. The callee loads matching parameter positions and writes its return witness on normal return. The return-load insertion is after the call, so it does not apply on unwind.
- The fallback body remains the only owner of selected result bytes. The local visitor retains its regular operand traversal and existing intrinsic models; select payload/layout refusal occurs before select-specific transfer or move-deinit operations. Typed storage masks remain in use for `MaybeUninit` payload/padding.
- Points-to sends only the validated fallback through ordinary body analysis. That analysis connects caller arguments to body parameters and the body return to the destination, so both value arms can contribute referents without a condition edge or arm-slot address.
- Read the currently present untracked `tests/expected/uninit/select-unpredictable-*` source and expected files as separate test work, not as part of the committed candidate. They cover selected values, pointer aliases, null/dangling selection without dereference, direct `MaybeUninit` legal/hole arms, padding aliases, copy/move behavior, overwrite, the hint wrapper, and nested-layout refusal. The custom-MIR move harness explicitly passes `Move(a)` and `Move(b)` and reads both saved source addresses after the call. Static source inspection only; expected-output files are not execution evidence.

## Validation and limits

- `git diff --check` for the base-to-candidate diff: clean.
- No build, compiler, Kani, or CI execution was performed. All runtime outcomes remain **NOT_RUN**; this review grants no proof credit.
- The test sources and expected-output files are untracked in the candidate worktree and are not covered by the candidate commit digest. Their expected outputs remain unverified.

## Test-only std overlay review

**Pinned package baseline:** `01d75b8e839c751e7ab679fdaaa5fba6384983b6` (`f5bdc486d661fc1896fa077d2dbc1b357b7aba49` tree).  
**Swap closure commit:** `da47945f47c6d61e6e207a749299a74f840a01f0` (`6075e7ce17179f45642c9ffe8fe09e3ec9395726` parent).  
**Raw sort4 control commit / worktree HEAD:** `6075e7ce17179f45642c9ffe8fe09e3ec9395726` (`a7795c5a49a4f3f00b774356c0ae3fb2a89c6825` tree; parent `da47945f47c6d61e6e207a749299a74f840a01f0`).

- The baseline-to-swap diff changes only `library/core/src/slice/sort/shared/smallsort/verify/helper_contracts.rs`. `exercise_swap` now passes a noncapturing `&mut |a: &T, b: &T| arbitrary_less::<T>(a, b)` to the actual `swap_if_less`, using the direct free-function call. Its `swap_safety_u64_backing4` PFC root, real helper call, four-element initialized backing, nondeterministic in-range positions, equality allowance, outside-position frame assertions, and equality/order/normal-return covers remain in place. No helper implementation or contract changed.
- The sort4 commit adds only the `#[cfg(kani_smallsort_controls)]` module registration and `verify/replay_uninit_controls.rs`. Both controls invoke the actual `sort4_stable` on the same separate source/destination geometry; the negative leaves only source slot 1 uninitialized, while the legal case initializes all four slots. The real helper's first comparator call reads slot 1, so the intended negative read is exercised before later comparisons. These are direct body controls; the existing `sort4_safety_u64` PFC, separate output, source frame checks, output readbacks, and return cover are preserved unchanged.
- Across both commits, the only changed paths are the two verify-only files above plus the new cfg-gated verify-only control module. No production algorithm, helper contract, or runtime code changed. These controls are static preparations only; outcomes remain **NOT_RUN**.

## Final native-control source review

Reviewed the final currently present 12 untracked control groups in `/root/kani-fix-3300-sel1/tests/expected/uninit/select-unpredictable-*`: values, pointer values, both pointer-hole directions, delayed padding, MaybeUninit, copy/overwrite, hint wrapper, moves, typed padding, nested-layout refusal, and unmodeled-intrinsic refusal.

- The custom-MIR move controls now return only ordinary `u8` tuples. Their intrinsic calls use explicit `Move(a)` and `Move(b)`; separate source-A/source-B helpers each perform exactly one post-call source read, after consuming and asserting the selected result. Four constant-condition roots cover true/false crossed with source A/B. The separate Copy control passes bare places `a, b`, which the custom-MIR DSL converts to Copy operands; it reads and checks both sources and selected value.
- Named checks use the `kani::assert(condition, message)` function API; no `kani::assert!` uses remain. Expected negative controls pair a named useful SUCCESS property with one intended UB/Unsupported FAILURE, and pin the failed-property count using `** 1 of` lines. Compiletest's expected matcher checks each expected line as a substring, so this intentionally pins the count without pinning a tool-dependent total. The typed `MaybeUninit<Padded>` tests exercise both selected arms: typed fields are asserted readable, then the padding byte at offset 1 is read and expected uninitialized.
- No remaining static source/API defect identified in these final controls. The test source snapshots remain untracked and separate from the semantic candidate; their outcomes are **NOT_RUN** and expected files are not verification evidence.
- Final control source identities: `select-unpredictable-moves/main.rs` SHA256 `a84336c075dcc5046e95d0e57ac1d02068c61f29e63a67749dfb13843cbb8035`; `select-unpredictable-padding/main.rs` SHA256 `dfe19d60602084f33c4177f84a85046451bd59f5e7009bf325f3941f0cf917a4`. Corresponding expected-file SHA256 values are `61b9507c4aff0e3bd83f1b8c667bc237ef15a946e0f062c63325ce2a7e861510` and `6e8e2d25ef9f7960f1475d0f66b7e3c5a11ceb27b80abfc263382a7d9c8f2c95`.
