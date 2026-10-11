# Caller premises for the first SmallSort `sort4_stable` call

**Static source/model map only. This document does not establish any premise or
upgrade the proof status.** No compiler, verifier, proof runner, extractor, or
Cloud job was run for this map. It uses the repository's pinned Rust source and
the current research C4 profile as context, and imports no foreign proof. Policy
read: `WORK-POLICY.md` adopted at `6726a08d30b37d6d0f4ae65c3d8c2861615d249a`,
content revision `c7ca8c467aecf10a4b53039372ee97714f854ee3`.

## Pinned source and current evidence boundary

The selected source is `library/core/src/slice/sort/shared/smallsort.rs`,
SHA-256 `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`
(working tree source commit `cd371e035c7e573760c43bf934d53e8118ee3e7d`).
Other traversed files are pinned in the same current tree: `stable/mod.rs`
`3f2b2d8543a1cb91c9352e041bed49949a31cbd4b1030ec1a82cca1304cb22d3`;
`stable/drift.rs` `5992b53abed257aa1c2dc2bb811d6a525294471e7a98d434f161d376100bf9c9`;
`stable/quicksort.rs` `4a41df6bc7c4e0a6fcb655fde9bf73ed62f3a675ca805f2f766919ce249d8f4c`;
`unstable/mod.rs` `23fa044fde8d3542f5f298654923ed2426930373259e6f71670c75b80501cf9a`;
`unstable/quicksort.rs` `68ca54463f739f9ab13b1dea1bee71533333d1a0085dac1f7e4401d500903411`;
`slice/mod.rs` `e3a45814fc07497d6e85d182d6b30782711e4b77752fa817988ec6da12e2cb6f`.
Relevant related source files are listed by path and line below. The C4 profile
pins VeriFast HEAD `f76012fb518703b1d98e243ac4f487f16877cfcb`; its recorded
`std/lib.rsspec` SHA is
`d33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf`, and
`prelude_core.rsspec` SHA is
`435146cd4632541241563ae45b146704c14f6f7cdd3b5d404837617f08bc91b8`.
The current maintainer package records Build `3b7431bb-4e18-4921-b690-307e4ba7f984`
as a fresh VF0 candidate for a guarded, four-comparator internal fragment;
the profile remains unaccepted. The fragment is not the caller-to-callee
proof of `sort4_stable`, the whole helper, or a general actual-sort theorem.
The separate legacy result field `native_c1_to_c4: NOT_RUN` refers to a
legacy driver path, not the current C4 target's four sequential comparator
expressions. It also does not imply that the external caller has been proved.

## Actual first-call branch and inputs

The first relevant body is `small_sort_general_with_scratch<T: FreezeMarker,
F: FnMut(&T, &T) -> bool>` at `smallsort.rs:220–293`:

| Source location | Actual operation / condition | Premise required at first call | Static status |
| --- | --- | --- | --- |
| 220–224 | Function signature: `v: &mut [T]`, `scratch: &mut [MaybeUninit<T>]`, `is_less: &mut F` | Existing `T: FreezeMarker`, mutable slice and callback references | Actual signature; no caller entailment established here |
| 225–232 | Read `len`; return for `len < 2`; otherwise abort if `scratch.len() < len + 16` | `len >= 2`; arithmetic for `len + 16` is defined; successful guard implies the larger scratch extent | Source check only; caller proof not recorded |
| 234–239 | `v_base = v.as_mut_ptr()`; `scratch_base = scratch.as_mut_ptr() as *mut T` | Pointer values/provenance must correspond to the live mutable slices; source cells initialized; scratch permits writes as `MaybeUninit<T>` | Actual implementation path, but the caller-boundary alias/provenance transfer has no admitted summary |
| 241–251 | `if const { size_of::<T>() <= 16 } && len >= 16`, call `sort8_stable` twice | This route does **not** call the direct `sort4_stable` expressions at lines 254–255 | Route is separate and not established by the C4 fragment |
| 252–257 | Else if `len >= 8`, call `sort4_stable(v_base, scratch_base, is_less)` then `sort4_stable(v_base.add(len_div_2), scratch_base.add(len_div_2), is_less)` | `len >= 8`; first four initialized source cells; writable scratch destination cells; correct pointer provenance; live callback capability | Caller-to-first-callee edge and second call remain unproved |
| 258–263 | Else copy one item from each half | Small-length route; not the first `sort4_stable` call | Separate path |

`sort4_stable` documents its unsafe precondition at `smallsort.rs:604–610`:
`v_base` valid for four reads, `dst` valid for four writes, with result in
`dst[0..4]`. In the direct branch, `len >= 8` makes `len_div_2 >= 4`, so the
second source window `[len_div_2, len_div_2 + 4)` is disjoint from the first
`[0, 4)` and remains within `v[0..len]`. The actual second destination is
`scratch_base + len_div_2`. The caller's `scratch.len() >= len + 16` check is
stronger than the local four-write bounds, but proving the check and pointer
identity still requires real slice-origin resources; numerical address facts
alone do not create permissions.

The direct `sort4_stable` implementation at `smallsort.rs:616–651` reads the
first two comparison pairs at lines 620–621, selects `a/b/c/d` at 622–625,
then compares the cross-pairs at 635–636 and the final unknown pair at 643. It
writes the four sorted outputs at 647–650. Thus an actual full first
`sort4_stable` invocation has **five** comparator calls, not four. C4's
recorded four-comparator fragment does not, by itself, establish the fifth
comparison, the helper entry contract, or the output copies. `FreezeMarker`
does not add `Copy`, comparator purity, no-panic, or no-alias restrictions on
`F`.

## Upstream route to a non-ZST helper call

The public stable and unstable sort entries provide the relevant source-level
nonzero chain:

- Stable `slice::sort` checks `T::IS_ZST` and returns at
  `library/core/src/slice/sort/stable/mod.rs:29–33`; `len < 2` returns at 37–40.
  For the non-`optimize_for_size`, non-16-bit configuration, lengths through 20
  use insertion sort at 77–81; larger inputs enter `driftsort_main` at 83.
- Unstable `slice::sort` checks `T::IS_ZST` and returns at
  `library/core/src/slice/sort/unstable/mod.rs:22–35`; lengths through 20 use
  insertion sort at 49–52; larger inputs enter `ipnsort` at 55.
- The pinned Rust spec defines `IS_ZST::<T>() == (size_of::<T>() == 0)` in
  `std/lib.rsspec:400–403`. Therefore, **on those public-entry paths**, passing
  the ZST test implies `size_of::<T>() != 0`. This is source/spec entailment by
  inspection only; it has not been proved through the actual caller chain in
  this work item. It does not justify the research fragment's internal size
  guard as a fact about every direct invocation.
- `FreezeMarker` is declared in `shared/mod.rs:8–13` with blanket
  `impl<T: Freeze> FreezeMarker for T`. In the stable type specialization,
  `StableSmallSortTypeImpl` selects the general implementation for
  `T: FreezeMarker` at `smallsort.rs:49–62` and sets threshold 32 at 51–52.
  The fallback implementation has threshold 16 at 30–46. This type-domain
  selection is real source behavior, not a newly added proof restriction.

For stable sorting, `driftsort_main` computes
`max_full_alloc = 8_000_000 / size_of::<T>()` at `stable/mod.rs:111–117`,
then chooses a scratch length at least `SMALL_SORT_GENERAL_SCRATCH_LEN == 48`
(`smallsort.rs:173–188`). Its stack buffer uses `AlignedStorage` at
`stable/mod.rs:119–129`; the `N / size_of::<T>()` slice conversion is at
`stable/mod.rs:148–163`. The early `IS_ZST` return precedes that division.
`drift::create_run` enters stable quicksort with
`min(T::small_sort_threshold(), len)` when eager sorting at
`stable/drift.rs:249–256`; stable quicksort invokes `T::small_sort` when its
current slice is within threshold at `stable/quicksort.rs:23–28`. These call
paths explain how a sub-slice can reach small-sort while preserving shared
scratch. They do not establish a checked ownership transfer into the target.

For unstable sorting, `ipnsort` enters `unstable/quicksort.rs`; its base case
calls `T::small_sort` when `v.len() <= T::small_sort_threshold()` at lines
29–32. `UnstableSmallSortFreezeTypeImpl` can route to
`small_sort_general(v, is_less)` when its stack-size threshold check succeeds
(`smallsort.rs:113–132`, or the `CopyMarker` specialization at 142–169).
That wrapper creates 48 uninitialized `T` slots and calls
`small_sort_general_with_scratch` at `smallsort.rs:205–218`. The public
unstable ZST guard precedes this chain. The unstable network specialization and
fallback are separate routes.

## Entry resources that must be connected

The following resource shapes are available in the pinned C4 model, but their
actual origin through the caller and method operations remains a proof
obligation:

| Resource | Available stock shape | What the first call still needs |
| --- | --- | --- |
| `v: &mut [T]` | Generated mutable-slice full-borrow content is an `array<T>(base, len, elems)` plus `foreach(elems, own<T>(thread))`. The definition is `prelude_core.rsspec:449–451`; the generated counterpart is `vf_mir_translator.ml:1310–1355`. `array_inv` at `prelude_core.rsspec:255–257` yields the `len * size_of<T> <= isize::MAX` and pointer-limit facts; `array_split` and `array_join` are at 260–277. | Establish that the actual `v_base` is this base with preserved provenance, keep source values/owners current, and split four distinct cells without losing the tail. `len >= 8` gives enough indices only after that base/range connection. |
| `scratch: &mut [MaybeUninit<T>]` | Same slice full-borrow pattern for `MaybeUninit<T>`; `MaybeUninit` size/alignment equality to `T` is specified in `std/lib.rsspec:478–484`. `open_MaybeUninit` exposes optional `T` storage at 442–456; conversion helpers are at 458–476. | Preserve all scratch cells as opaque/uninitialized-or-initialized `MaybeUninit<T>` except the four write destinations. Do not assert initialized `T` owners merely from a `MaybeUninit` slice. Restore the same scratch frame on normal and panic paths. |
| Callback `is_less: &mut F` | A mutable-reference full borrow carries current `F` ownership in the generated Rust reference contract; generic signature is `FnMut(&T,&T)->bool`. | Reborrow across each call with proper late-bound reference lifetimes, preserve `F` and thread resources, and close both normal and direct-unwind outcomes. `FnMut` permits mutation; panics remain allowed. |
| Thread/type/lifetime resources | The RustBelt model has explicit `thread_token`, full/frac borrow and lifetime tokens; `reborrow_ref_mut` is specified in `rust_belt/aliasing.rsspec:1–4`. | Demonstrate their actual caller origin and restoration. The older caller premise map flags `T/F type_interp` as unresolved; the C4 target's success cannot be reused as an automatic caller-entry lemma. |

The relevant C4 `std/lib.rsspec` includes `size_of` and `IS_ZST` equations
(395–403), `MaybeUninit` semantics (429–484), and `from_raw_parts_mut`
(784–794). The latter requires raw data permissions, non-null pointer,
alignment and byte-size bounds, and returns a slice with the same pointer and
length; its comments explicitly do not enforce aliasing and point to slice
creation as TODO. The pinned Rust RSSpec files contain `as_mut_ptr` summaries
for `Box` and `Vec`, but no `as_mut_ptr` declaration for `[T]`/`&mut [T]`.
The actual slice method in `library/core/src/slice/mod.rs:750–780` returns the
identity cast `self as *mut [T] as *mut T`. A proof must therefore establish
that exact source/body-to-model pointer relation and preserve the mutable slice
origin; it cannot borrow the `Vec::as_mut_ptr` summary or infer permissions
from pointer equality. Likewise, `array_inv` range facts and address equality
are not an aliasing/ownership theorem.

## Distinct branches and proof statuses

| Caller route | Required extension beyond first direct C4 fragment | Status in current C4 evidence |
| --- | --- | --- |
| First direct sort4 call, `v_base` → `scratch_base` (line 254) | Connect safe-slice entry to raw pointer preconditions and prove full five-comparison `sort4_stable` contract | C4's four-comparator internal fragment is fresh VF0; full first helper/caller edge is not proved |
| Second direct sort4 call, `v_base + len_div_2` → `scratch_base + len_div_2` (line 255) | Prove half-offset derivation, second four-cell source/destination windows, disjointness from first call and frame after the first call | Not proved by first-call fragment |
| `size_of<T>() <= 16 && len >= 16` path (lines 241–251) | Prove both `sort8_stable` calls; each makes nested sort4 calls at `smallsort.rs:665–666`, followed by merge at 669–673; outer path calls sort8 twice | Not proved by direct-C4 fragment |
| Short path (lines 258–263) | Copy-first-element operations, and its downstream tail/merge behavior | Separate, not established by the C4 fragment |
| After either presort branch (lines 265–291) | `insert_tail` callbacks, `CopyOnDrop`, full initialized scratch, merge, restoration on panic | Not established by the four-comparator C4 fragment |
| Caller frame / public actual caller | Driftsort/ipnsort allocation, caller branch, scratch owner, lifetimes and exact call edge | Static source chain only; no accepted connected caller proof |

The nonzero derivation is useful but not enough to choose the direct branch:
for a nonzero `T` with `size_of::<T>() <= 16` and `len >= 16`, the source
selects `sort8_stable`; direct sort4 is chosen for `len >= 8` only when that
conjunction is false. Thus the direct C4 path includes every nonzero type size
above 16 at lengths at least 8, and sizes 1–16 only for lengths 8–15. It is
incorrect to claim the direct fragment covers every actual sort call or every
non-ZST type/length pair.

## Static conclusions and open obligations

1. The public stable/unstable ZST guards provide an inspectable source-level
   nonzero fact for calls reached through those entrypoints, using the pinned
   `IS_ZST` equation. This fact is not a completed caller proof.
2. `len >= 8` on the direct branch and `scratch.len() >= len + 16` are concrete
   source checks. For nonzero `T`, a valid Rust slice has a maximum element
   count bounded by `isize::MAX / size_of::<T>()`; this makes `len + 16`
   non-overflowing on supported Rust `usize` widths. The C4 entry obligation
   still has to establish the array-size bound before using that reasoning, and
   preserve the abort path/posts.
3. The actual values and origins of `v_base`, `scratch_base`, `F`, thread
   tokens, lifetime tokens, and type interpretations must be derived from the
   caller's live slice/reference resources. The source body and stock RSSpec
   provide shapes and equations, not an admitted end-to-end aliasing proof.
4. Fresh C4 VF0 is evidence for its admitted four-comparator fragment only.
   It does not cover the fifth comparator, second direct helper call, sort8
   branch, outer run/merge logic, or upstream caller. Earlier C1-to-C4 and
   sort8-related records have their own configurations and statuses; none is
   silently composed here.

These are review targets for a future connected caller proof. This map is
static documentation and does not modify status, claims, source, specifications,
or proof artifacts.
