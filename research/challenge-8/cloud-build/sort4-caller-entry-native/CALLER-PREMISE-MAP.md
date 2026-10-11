# First-call premise map: `small_sort_general_with_scratch`

**Static source/model map only.** This records facts and remaining proof
obligations; it does not prove a caller premise or upgrade proof status. No
compiler, verifier, proof runner, extractor, or Cloud job was run for this map.
Policy read: `WORK-POLICY.md` adopted at
`6726a08d30b37d6d0f4ae65c3d8c2861615d249a`, content revision
`c7ca8c467aecf10a4b53039372ee97714f854ee3`. The prior detailed draft is
preserved in [CALLER-PREMISE-NOTES.md](CALLER-PREMISE-NOTES.md).

## Target and status

The source is `library/core/src/slice/sort/shared/smallsort.rs`, SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`,
function `small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>`
(lines 220–293). The actual first direct helper call is line 254;
`sort4_stable`'s unsafe precondition is at lines 604–610. The current C4
record (Build `3b7431bb-4e18-4921-b690-307e4ba7f984`) is a fresh VF0 candidate
for a guarded internal four-comparator fragment. The profile remains
unaccepted; this is not an admitted caller-to-callee proof, full helper proof,
or whole-sort theorem. The legacy `native_c1_to_c4: NOT_RUN` field describes
a separate legacy driver path: the current C4 fragment runs four sequential
comparator expressions. It does not prove the actual external caller.

## First direct-call gates and resources

| Premise | Exact source/model origin | What source establishes; what remains proof-open |
|---|---|---|
| `T: FreezeMarker` | `smallsort.rs:220`; trait `shared/mod.rs:8–13`; stable impl `smallsort.rs:49–62` | Actual generic bound and dispatch. `FreezeMarker` does not imply nonzero size, `Copy`, comparator purity, no panic, or no aliasing. The generic `sort4_stable` at line 606 has no `FreezeMarker` bound. |
| ZST / nonzero | Stable public guard `stable/mod.rs:29–40`; unstable guard `unstable/mod.rs:22–35`; `std/lib.rsspec:400–403` equates `IS_ZST<T>` with `size_of<T>() == 0` | Passing either public guard entails nonzero size by source/spec inspection. That entailment has not been proved through this caller chain. A direct internal call need not have passed the public guard. |
| Length | Target `smallsort.rs:225–232`; direct branch `252–257` | `len < 2` returns; direct branch requires `len >= 8`; scratch check is `scratch.len() >= len + 16`, otherwise abort. Prove actual slice extents and preserve return/abort posts. |
| Overflow / extent | `prelude_core.rsspec:255–277` (`array_inv`, split/join); mutable-slice shape at `449–451`; translator `vf_mir_translator.ml:1310–1355` | Array invariant supplies `len * size_of<T> <= isize::MAX` and pointer bounds. For nonzero `T`, this supports the source's `len + 16` reasoning on supported `usize`; caller must establish the invariant before using it. Zero-size does not bound length. Preserve abort behavior. |
| `v` and raw pointer | `v.as_mut_ptr()` at `smallsort.rs:234`; `[T]` method body `slice/mod.rs:750–780` (identity cast at 778–780); helper precondition `smallsort.rs:604–610` | Need four initialized source cells, exact base/provenance relation and retained surrounding array/owners. RSSpec has no `[T]::as_mut_ptr` summary; address equality alone is not permission or aliasing evidence. |
| Scratch | `smallsort.rs:223,239,254`; `MaybeUninit` spec `std/lib.rsspec:442–484` (size/alignment equality 478–484) | Need four writable destination cells and preserve all other scratch as `MaybeUninit<T>`; do not infer initialized `T` ownership from the scratch slice. Restore frame on normal and unwind exits. |
| `F` callback | Signature `smallsort.rs:221–224`; five actual comparisons at 620–621, 635–636, 643 | Need live mutable callback ownership/reborrows and normal/unwind restoration. `FnMut` may mutate and panic. Four-comparator C4 fragment does not prove the fifth call or full helper. |
| Lifetimes / thread | RustBelt `reborrow_ref_mut` at `rust_belt/aliasing.rsspec:1–4`; generated Rust reference resources | Must derive and restore actual thread, lifetime, borrow, and `T/F` interpretation resources at the caller boundary. They are not supplied by a raw-pointer equality fact. |

## Route distinction

For direct sort4, target lines 252–257 require `len >= 8`. The first call uses
`(v_base, scratch_base)` at 254. The second uses
`(v_base + len/2, scratch_base + len/2)` at 255. `len >= 8` makes the source
windows `[0,4)` and `[len/2,len/2+4)` disjoint and in range, but this numerical
fact does not prove provenance, permissions, or the second-call frame after
the first call. This second actual call remains separately open.

The `size_of::<T>() <= 16 && len >= 16` arm instead calls `sort8_stable`
twice (`smallsort.rs:241–251`); sort8 itself calls sort4 twice at 665–666 and
then merges. That route is distinct and unproved by the direct-C4 fragment.
The short route at 258–263 and post-presort tail/merge/`CopyOnDrop` path at
265–291 are also outside that fragment.

Stable and unstable public sort entrypoints return for ZSTs before their
respective downstream sort paths; `std/lib.rsspec:400–403` supplies the
`IS_ZST`/size equation. The static source chain is useful for deriving a
nonzero condition, but is not fresh proof. Stable routing is in
`stable/mod.rs:29–40,77–84`, `stable/drift.rs:249–256`, and
`stable/quicksort.rs:23–28`; unstable routing is in `unstable/mod.rs:22–56`
and `unstable/quicksort.rs:29–32`. This route also needs real caller-derived
scratch, pointer, `F`, lifetime, and ownership resources. Detailed allocations,
resource shapes, and route notes are retained in `CALLER-PREMISE-NOTES.md`.

## Current experiment boundary

The authorized next experiment is a fresh minimal rebase of the
`our-slice-as-mut` patch (`f200a581`) into the current C4 typed-strip arm: first
an actual-body component, then a `T`/`MaybeUninit` real-call consumer with full
posts and wrong-pointer/missing-raw-rights negatives, followed by the
unfiltered actual caller prefix with original guards and real calls. It must
not insert an artificial ZST or nonzero premise. Overflow/abort remains an
explicit classification obligation. This plan is not evidence that any of
those obligations have passed; no external caller or whole sort theorem is
currently established.
