# KANI3300 A2R static review

## Reviewed identities

- Semantic packet: baseline `3dc0227cee87d85bed32678a2209353ebdb9d2fa`; candidate `85fc5cd2ca770cdc5ae1bb514c27b6da7b6d9b18`; tree `d178157e35b45f84afd17b86027e667716c17344`; diff SHA256 `b1145bb4737be6381226349344a6a3fb87c83f756f04dc7f363252b01671cedd`; spec SHA256 `ff55a22d10fccb7d8f84d8403f37aae19283969b20a555af0c7f27c5de392648`.
- Golden-only follow-up: baseline `85fc5cd2ca770cdc5ae1bb514c27b6da7b6d9b18`; candidate `b207847932da34ac19886c1337f5b69ace0b0843`; tree `3cdfc7e4ee0551211554f40968d391e3d404e27d`; diff SHA256 `0e185648814b3c9f3dfd2accea2cef4b9d0b059bedb833ea057ce28c8d148327`; spec SHA256 `1cdc3f65e1a08d4fd2ead1133086fdf04b24620c11763e909e7b4ab23ff08a28`.
- Task contract spec SHA256: `ff55a22d10fccb7d8f84d8403f37aae19283969b20a555af0c7f27c5de392648`.

## Findings and assessment

No blocking static correctness finding in the reviewed A2R delta. `RawEq` is recognized at its intrinsic call; both reference operands are selected independently. For each, the code obtains the pointee layout size, constructs `[u8; size]`, and emits `CheckAs`. The existing `CheckAs` path casts the operand address to a pointer to that byte array and derives the memory-init mask from the array type, so its mask covers every byte, including padding and `MaybeUninit` storage. A zero-sized pointee yields a zero-byte check. The ordinary initialized-array equality path therefore receives checks rather than an unconditional Unsupported result.

Initial-target tracking adds both raw_eq operands, allowing the existing delayed-UB points-to/shadow flow to account for earlier writes to those pointees. The changed source does not alter Pat offsets or enum variant-local layout comparison. Existing `maybe-uninit-transmute`, `maybe-uninit-initialized`, and `maybe-uninit-partial-copy` source/golden files are unchanged; their expected-file SHA256 values match the declared dependency snapshots.

The replacement fixture statically covers initialized `[u8; 3]` arrays, initialized scalar and `MaybeUninit` storage, a single uninitialized byte in each operand position, uninitialized struct padding, and a zero-sized type. Its one-byte holes are explicit `MaybeUninit::uninit()` assignments. The padding case uses a 12-byte `Padded` value. Pinned rustc `InstSimplify::simplify_raw_eq` transmutes operands to an integer only when `Integer::from_size(layout.size)` succeeds; that explains the prior size-8 fixture's transmute instrumentation errors. The revised 12-byte fixture avoids that integer-size rewrite, so those prior diagnostics point to fixture/rustc simplification rather than a defect in the A2R raw_eq byte check.

The golden follow-up adds the three exact `Verification failed for - <harness>` summary lines. This is useful because `compiletest`'s `contains_lines` matches expected lines independently unless a trailing backslash requests adjacency, and the runner sorts same-file harnesses by descending source line. The new lines bind the failed count to the intended left-byte, padding, and right-byte harnesses without relying on output ordering. The expected summary remains 4 successes, 3 failures, 7 total.

Static API review found the referenced `Ty::try_new_array`, `Ty::unsigned_ty`, `Ty::layout`, `Layout::shape`, and size `bytes()` APIs in the pinned `/tmp/kani3300-g1r-api` files; imports, operand borrowing, and type flow are consistent by inspection. I verified all 11 API source SHA256 hashes against `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/g1r/API-SOURCES.json`. No obvious unused import/code or clippy/`-D warnings` issue is apparent. No compiler or clippy run was performed.

## Static verdict and limits

**Static review: PASS, with no blocking findings.** The golden follow-up is test-only and preserves the intended diagnostics and counts. This is source and fixture reasoning only: all build, clippy, Kani, CBMC, Miri, and runtime outcomes remain **NOT_RUN**. No proof credit is granted or inferred.
