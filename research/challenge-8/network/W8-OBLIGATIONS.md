# W8: `small_sort_network` caller — obligation map (static, 2026-10-22)

Planning note for later Network tasks; no proof, compile or run. Source:
`smallsort.rs` blob `40939f92` (shared baseline `cd371e03`), lines 311–372;
dispatch at 156–169 (`small_sort` of the `UnstableSmallSortFreezeTypeImpl`
impl, taken when `has_efficient_in_place_swap::<T>()` and
`size_of::<T>() * 32 <= MAX_STACK_ARRAY_SIZE`). Component status per
[W7](w7/DESIGN.md) and [R4](r4/DESIGN.md): candidates, unverified.

| Lines | Step | Obligation | Component / owner |
| --- | --- | --- | --- |
| 318–321 | `len < 2` → return | trivial normal post (slice unchanged) | Network |
| 323–325 | `len > 32` → `intrinsics::abort()` | abort spec (same gate as W7) | Network, via Select layer pin |
| 327 | `MaybeUninit::<[T; 32]>::uninit()` | uninitialised stack scratch, no `T` own; layout of `[T; 32]` | Network; MaybeUninit model as in Select's accepted route |
| 329–335 | `len_div_2`, `no_merge = len < 18`, `as_mut_ptr`, `slice::from_raw_parts_mut(v_base, initial_region_len)` | in-bounds region; stock `from_raw_parts_mut` spec keeps the chunk with the caller (aliasing not enforced — record as model limit) | Network; as_mut_ptr projection (Select pin) |
| 338–347 | `sort13_optimal` if `region.len() >= 13`, else `sort9_optimal` if `>= 9`, else presorted 1 | W7 summaries (actual callees in the same crate) | Network (W7) |
| 349 | `insertion_sort_shift_left(region, presorted_len, is_less)` | actual callee proof required (no assumed summary); `offset` in `1..=len` | **Merge** (insertion / insert_tail, W2) — consume their published proof by pin |
| 351–360 | `no_merge` return; `region.as_ptr() != v_base` loop exit; second region `v_base.add(len_div_2)`, `len - len_div_2` | at most two iterations; disjoint halves; pointer comparison on provenance-equal pointers | Network |
| 362–371 | `bidirectional_merge(slice::from_raw_parts_mut(v_base, len), scratch_base, is_less)` then `ptr::copy_nonoverlapping(scratch_base, v_base, len)` | `T: FreezeMarker` premise for observation safety on comparator panic (source comment: v retains its input); scratch/v non-aliasing; scratch has `len <= 32` cells; copy-back ownership transfer | **Merge** (general merge, W5) for `bidirectional_merge`; copy-back and Freeze bridge Network |
| all | unwind | comparator panic in sort9/13 (W7 separate-cell post), insertion (Merge post), merge (v unchanged per Freeze) → whole `v` owned again, scratch dropped without `T` drops | Network composes; needs each component's unwind post |

Sorting (not safety) composes: network prefix sorted (N9/N13 math component,
fixed-order/key-preservation premises) → insertion extends to the region →
merge of two sorted halves. That functional chain is separate from the
ownership proof and must keep the premises of `networks/SWAP-CONTRACT.md`.

Cross-owner dependencies to request when W8 starts: Merge's published
`insertion_sort_shift_left` and `bidirectional_merge` proofs at the same std
blob (pin, no Network copy); Select's MaybeUninit/array and `as_mut_ptr` routes.
