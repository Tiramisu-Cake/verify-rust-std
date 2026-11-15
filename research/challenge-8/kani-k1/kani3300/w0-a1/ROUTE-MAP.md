# W0-A1 std route map (static source review)

Source package: `work/ch8-w0-a1-w15` at `65864680a145c90c583dcba7efd1d569475519fc` (full SHA and object identities are in [`std/MANIFEST.md`](std/MANIFEST.md)). The eight roots are enabled only by `cfg(kani_smallsort_controls)` and each has an exact selector under `slice::sort::shared::smallsort::verify::wave0_a1::`.

## Routes and useful covers

| Exact selector | Input and actual trait entry | Static route and raw scratch view | Output payload reads |
|---|---|---|---:|
| `stable_freeze_u64_n8` | Independent arbitrary `u64[8]`; `<u64 as StableSmallSortTypeImpl>::small_sort` | `u64: Freeze`; specialized stable entry calls general-with-scratch. Separate flat `[MaybeUninit<u64>; 48]`; `sort4_stable` on each half, insert tails, then bidirectional merge. | 8 |
| `stable_freeze_u64_n16` | Independent arbitrary `u64[16]`; same entry | Separate flat 48-element scratch; `sort8_stable` on each half, insert tails, then bidirectional merge. | 16 |
| `stable_freeze_u64_n32` | Independent arbitrary `u64[32]`; same entry | Same flat scratch and sort8→insert→merge route; scale candidate. | 32 |
| `unstable_general_nocopy_u64_n8` | Independent arbitrary transparent `A1FreezeNonCopy[8]`; `<A1FreezeNonCopy as UnstableSmallSortTypeImpl>::small_sort` | Wrapper is `repr(transparent)` around `u64`, has no `Copy` or `Drop` impl, implements `FreezeMarker` by its field. The Freeze non-Copy impl's `size_of::<T>() * 48 <= 4096` selects `small_sort_general`; private `MaybeUninit<[T; 48]>`, `sort4`→insert→merge. | 8 |
| `unstable_general_nocopy_u64_n16` | Independent arbitrary wrapper `[16]`; same entry | Private general scratch 48; `sort8`→insert→merge. | 16 |
| `unstable_general_nocopy_u64_n32` | Independent arbitrary wrapper `[32]`; same entry | Private general scratch 48; `sort8`→insert→merge; scale candidate. | 32 |
| `unstable_network_u64_n18` | Active arbitrary `u64[18]` in initialized `[u64;32]`; `<u64 as UnstableSmallSortTypeImpl>::small_sort` | `u64` is Freeze+Copy, `has_efficient_in_place_swap::<u64>()` is asserted, and `8*32 <= 4096`; network specialization creates private `MaybeUninit<[u64;32]>`. `len=18` takes merge branch: two 9-element sort9+insertion regions then merge. | 18 |
| `unstable_network_u64_n32` | Active arbitrary `u64[32]` in initialized `[u64;32]`; same entry | Same network scratch; two 16-element halves take sort13+insertion, then merge; scale candidate. | 32 |

The source binding is the trait call in each generated root. Inlining may erase a named wrapper frame in generated verification input; this source map does not claim independently inspected AST/MIR binding or proof execution. Threshold/type assertions and the listed source predicates establish the intended dispatch statically; future receipts must still show the selected root and complete required events.

Each comparator is a concrete closure, not a function pointer. It performs volatile reads of both actual arguments (the wrapper reads both `u64` payloads) and returns an unconstrained `kani::any()` boolean. No lawful-order constraint, model comparator, PFC, or `stub_verified` summary is used. Each root retains only the existing `panic_on_ord_violation` stub, replaced by the exact `cut_merge_order_violation` helper body from `verify/helper_contracts.rs`: it first covers `helper contract merge order violation reachable`, then calls `kani::assume(false)` and `unreachable!()`. This cuts the inconsistent-comparator abort path for normal-return scope and adds no input precondition. The copied helper is used in every root; no other assume/stub is added.

Every root has four regular useful covers: call-begins, comparator invocation, call-return, and readbacks-complete. The exact copied order-boundary cover in the stub is additional and conditional; its reachability is not presumed. Exact full selectors and generated source are recorded in the local std commit and in `std/overlay-from-6075.patch`. After return each active output payload receives one volatile read. Across all eight roots that is **162 active payload reads**: `8+16+32 + 8+16+32 + 18+32`. The stable and non-Copy general roots check two adjacent initialized input guards; network roots check the untouched initialized tail after the active prefix. Stable scratch is checked to be a separate allocation. No uninitialized scratch/tail is read. No sortedness, permutation, or comparator-law claim is made.

## Static geometry and unwind argument

- Stable input backing is `[u64; N+2]`, active offsets `1..N+1`, scratch is 48 `MaybeUninit<u64>` elements. `N` is exactly 8, 16, or 32; backing lengths are 10, 18, and 34. Guards are backing indices 0 and `N+1`.
- Non-Copy backing is `[A1FreezeNonCopy; N+2]`, constructed by a direct literal-expansion macro whose elements each call `kani::any()` independently. `N` is 8, 16, or 32; the same guard offsets apply. `repr(transparent)` over one `u64` gives size/alignment 8; there is no user `Copy` or `Drop` implementation.
- Network backing is `[u64;32]`, active offsets `0..N`, private implementation scratch is `MaybeUninit<[u64;32]>`; the N18 fixture checks tail offsets 18..32 and N32 has no exterior tail.
- Source loops in general sorting, insertion, network regions, merge, and fixture readbacks are bounded by these finite lengths. No recursive route is selected. The fixtures retain the repository's existing `#[kani::unwind(34)]` convention, enough as the initial static bound for loops whose maximum active extent is 32 plus loop termination. This is not runtime evidence that every generated unwinding assertion passes: future dispatch must inspect all unwinding checks and stop on any failure; no bound increase or assertion suppression is authorized by this package.

## Limits

No compiler, Cargo, rustc, Kani, CBMC, Miri, build, or CI invocation was run. Validation is limited to commit/source identity, allowed-path diff review, patch hashes, and static Rust/memory-route inspection. The exact module cannot be compiler-validated in this worker session. Route realization, output covers, and all unwinding assertions remain `NOT_RUN` until coordinator dispatch. An unknown/inlined target binding, unsupported fixture, missing cover/readback, timeout/OOM, or failed unwinding check is a named blocker, not scale evidence.
