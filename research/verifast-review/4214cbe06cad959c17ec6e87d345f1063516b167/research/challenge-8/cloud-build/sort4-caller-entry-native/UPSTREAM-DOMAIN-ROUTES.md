# Upstream runtime domain routes (static source review)

**STATIC_ONLY.** This is a source-path inventory, not a proof of caller facts.
The nonzero derivation and numeric `len <= 32` transfer are **NOT_PROVED** in
the current native caller-entry profile. No compiler, verifier, or proof tool
was run. Source hashes below are the pinned current Rust tree used by the
caller-entry manifest.

## Stable route to the exact helper

Target: `small_sort_general_with_scratch<T: FreezeMarker, F>` in
`library/core/src/slice/sort/shared/smallsort.rs:220–293`, SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`.
The Freeze specialization at `smallsort.rs:49–62` returns
`SMALL_SORT_GENERAL_THRESHOLD` (32, defined at 176–180) and calls this helper.

A short upstream route is:

1. Public stable `slice::sort` (`stable/mod.rs:29–40`) returns for `T::IS_ZST`
   and for `len < 2`; on the ordinary configuration, lengths through 20 use
   insertion sort (`stable/mod.rs:77–84`). The file SHA is
   `3f2b2d8543a1cb91c9352e041bed49949a31cbd4b1030ec1a82cca1304cb22d3`.
2. For `len > 20`, `driftsort_main` allocates scratch and computes
   `eager_sort = len <= T::small_sort_threshold() * 2`
   (`stable/mod.rs:94–135`). For Freeze-specialized T with threshold 32,
   length 21–64 selects eager mode.
3. `drift::create_run` first attempts run detection and returns a detected run
   at `drift.rs:236–247`. If that runtime branch does not return and eager mode
   is true, it sets `eager_run_len = min(T::small_sort_threshold(), len)` and
   calls quicksort on `v[..eager_run_len]` (`drift.rs:249–256`).
   `drift.rs` SHA-256 is
   `5992b53abed257aa1c2dc2bb811d6a525294471e7a98d434f161d376100bf9c9`.
4. Stable quicksort has the actual base-case guard
   `len <= T::small_sort_threshold()` immediately before `T::small_sort`
   (`stable/quicksort.rs:23–28`); SHA-256
   `4a41df6bc7c4e0a6fcb655fde9bf73ed62f3a675ca805f2f766919ce249d8f4c`.
   The concrete Freeze impl then dispatches to
   `small_sort_general_with_scratch` (`smallsort.rs:49–62`).

Thus source execution contains a real check/clamp before this method call; for
the Freeze specialization its threshold is 32. In the direct helper, lengths
8–32 with `size_of::<T>() > 16` choose the direct `sort4_stable` branch
(`smallsort.rs:241–257`). Public stable ZSTs return before this route. This
source reasoning does not prove the path, specialization, bound, resources, or
nonzero fact in VeriFast.

## Specialization and ZST qualifications

The `len <= 32` conclusion is not a literal check: generic stable quicksort
uses `T::small_sort_threshold()`, and `driftsort` calls that associated method
on `T: StableSmallSortTypeImpl`. The value 32 follows from resolving the
specialized `T: FreezeMarker` implementation at `smallsort.rs:49–54`; a
source-bound proof must establish the actual generic dispatch/method body (or
retain the symbolic threshold). Merely observing the impl declaration does
not prove that a translated caller uses it. Calling the trait method directly
also does not run quicksort's base-case guard.

The public stable ZST guard is `stable/mod.rs:29–33`; the unstable guard is
`unstable/mod.rs:22–29` (file SHA
`23fa044fde8d3542f5f298654923ed2426930373259e6f71670c75b80501cf9a`). The
pinned equation `IS_ZST::<T>() == (size_of::<T>() == 0)` is in
`std/lib.rsspec:400–403`. Passing the public guard therefore entails nonzero
size by source/spec inspection, but **the transfer through this caller path is
NOT_PROVED**. Internal helper or trait calls do not inherit that guard.

Unstable routing is separate: `unstable/quicksort.rs:29–32` guards its trait
call, while `smallsort.rs:90–169` selects network/general/fallback behavior;
the general wrapper creates stack scratch and calls the target at
`smallsort.rs:205–218`. It must not be conflated with the stable Freeze route.

## Minimal proof obligations for a source-bound prefix

A prefix can expose runtime guards without an entry assumption, but it must
admit the actual source/typed call chain and prove the invoked specialization.
It must retain the public ZST/short-length branches, `create_run`'s run-detection
condition and eager clamp (or the later quicksort base-case branch), and the
same-version associated-threshold dispatch. It must then derive actual mutable
`v` slice cells/owners and `as_mut_ptr` identity, `MaybeUninit<T>` scratch
extent/owners, callback `F`, thread/lifetime/type resources, and all normal,
unwind, early-return and abort posts. The target's
`scratch.len() < len + 16` check at `smallsort.rs:230–232` cannot be skipped;
`len <= 32` plus a proven 48-element scratch slice is enough to discharge its
comparison, but neither premise is presently caller-proved. `driftsort_main`
requests at least `SMALL_SORT_GENERAL_SCRATCH_LEN` (`stable/mod.rs:94–135`);
stack-vs-`BufGuard` construction and slice ownership still require proof.

Current C4 caller-entry diagnostics remain experimental and unaccepted. The
fresh internal C4 fragment does not provide any upstream caller lemma or
callable summary.
