# KANI3300 G1 — independent static review

## Identity and verdict

- Baseline: `657c2b24516b967f67ce71994299d0ef328aede9`.
- Reviewed candidate: `45d0300e054345b4f6bdf89528195ee7c5dba8a5`, tree `e1babbe95cc5f1ca567fe70957986d48626d05bf`.
- Ready packet: `review-packet-ready`, packet SHA-256 `f78b9b3e8d4f8a5c89ac6c1a290dc1295f06f08aab66c1f17e583ce4dd658ae5`; spec SHA-256 `888c58ed2cd2d79cba5693d583992d1e7059583b00a77703053e49d92fa57202`.
- The worktree HEAD/tree and packet candidate/tree identities match. The candidate adds only two golden-output corrections over the previously reviewed candidate; production files and all test sources are unchanged. The bodyless extern control now expects the earlier foreign-mutation guard, and the indirect-call control expects its first applicable `function pointers` diagnostic. Each still has its own unsupported property and one-failure summary. I reviewed the production diff and declared P1 dependencies, then inspected the new G1 fixtures and `TEST-MANIFEST.json`.

**Verdict:** no blocking source-level finding remains in this bounded static review. This is not a compiler/native result, formal verification credit, or authorization to dispatch.

## Invariant review

- The shadow extent uses rustc's full union size. Arm masks and offsets are rustc-derived, field ranges are checked against that extent, and whole construction resets all bytes before applying the chosen arm's data mask. Typed transfer preservation is a separate OR-of-arm-data mask; it intersects existing state and cannot turn a false source byte true. Raw byte copies and byte writes still cover the full extent.
- Whole-union Copy/Move, arguments, returns, constants, projected field stores, ZST writes, and Repeat use distinct state updates. Move sources are cleared while preserving destination state on overlap. Argument Move clearing happens only for the matching buffer entry; return sources use saved IDs/offsets and are not dereferenced after their lifetime. Direct intrinsic `Forget` Move is covered.
- Union-held pointer bytes are checked before dereferencing the pointer, and the selected final projection is checked after address-forming pointer prefixes. Pointer-byte state remains separate from pointee state. Taking a raw address does not initialize payload.
- Structural validation covers by-value formals, return places, and call arguments before zero-size or no-op shortcuts. Nested unions, union-containing by-value containers, unsupported enum layouts, function-pointer fields, transmute paths, and unmodeled volatile/swap/select/foreign/bodyless operations fail closed. The `Forget([U; 0])` control covers the no-op/zero-size G2 boundary.
- New helpers and move state are confined to `MEM_INIT_STATE`; the diff adds no assumptions, user-check weakening, points-to changes, or verifier writes outside the marked state.
- The final manifest has 40 selectors split 20/20 across two packages, with 205 harnesses total: 154 G1 harnesses and 51 existing regression harnesses. Each G1 negative has a harness, reading, type, expected outcome, diagnostic, and source binding. Move-source negatives isolate the moved-from alias read; non-Copy `ManuallyDrop` constructor and projected-store cases have positive and negative controls. Expected goldens are consistent with the manifest counts.

## Limits

- The union preservation mask is a rustc-layout inference from the pinned typed-copy guarantee; it is not supported by a backend observation. Native execution remains necessary to establish the expected outcomes.
- Rustfmt and `git diff --check` are recorded as passing in `STATIC-CHECKS.json`. Cargo, rustc, Kani, CBMC, native CI, and Cloud builds were not run by this review; proof credit remains `NONE`.
- Inherited P1 limitation: raw-alias invalidation for non-Copy `MaybeUninit<T>` transmute Moves in either direction remains outside this direct-union change. The transmute whitelist is unchanged; this review makes no general P1 soundness claim.
