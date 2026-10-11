# Source-bound stable quicksort threshold diagnostic

**Design and static source review only.** `threshold-cases.rs` is a Cloud-only
diagnostic template. No compiler, extractor, verifier, or proof runner was run;
no build was dispatched. It is not an accepted profile or evidence that a
caller obligation passed.

Policy read: `WORK-POLICY.md` revision
`c7ca8c467aecf10a4b53039372ee97714f854ee3`. Session card:
`CALLER-BOUND-SESSION.md`, phase
`SORT4-CALLER-DERIVED-BOUND-CLOUD-2026-10-11`.

## Actual obligation and source binding

The actual base case is `library/core/src/slice/sort/stable/quicksort.rs`,
`quicksort`'s first loop body:

```rust
let len = v.len();
if len <= T::small_sort_threshold() {
    T::small_sort(v, scratch, is_less);
    return;
}
```

The current file SHA-256 is
`4a41df6bc7c4e0a6fcb655fde9bf73ed62f3a675ca805f2f766919ce249d8f4c`.
The generic runtime signature has no `T: FreezeMarker` bound and includes
`mut limit: u32`, `mut left_ancestor_pivot: Option<&T>`, both slices, and the
mutable callback. `quicksort-base-unconstrained` copies that signature and
base-case source statements. Its return after the non-base path marks a
diagnostic cut before pivot/partition work.

The called trait and its implementations are in
`library/core/src/slice/sort/shared/smallsort.rs` (SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`):
`StableSmallSortTypeImpl` has a blanket default implementation whose threshold
body returns `SMALL_SORT_FALLBACK_THRESHOLD` (16), followed by the
`T: FreezeMarker` specialization whose actual threshold body returns
`SMALL_SORT_GENERAL_THRESHOLD` (32). The same file defines both constants and
the selected `small_sort` body, which forwards the same `v`, `scratch`, and
`is_less` to `small_sort_general_with_scratch`. `shared/mod.rs` (SHA-256
`fa9eec2901bafba25c9c1e1684df76dbb1f86e0bbd04f18f3e67cee54dcdfcc8`) defines
`FreezeMarker` and its `T: Freeze` implementation.

The fixture copies the trait, both impls, both constants, and selected method
body so a later source certificate can check their exact source identity. It
retains the trait calls; it never substitutes `32` at the caller. The explicit
Freeze-qualified wrapper is a diagnostic qualification theorem only. It does
not alter quicksort's runtime signature, establish dispatch for unconstrained
`T`, or add Freeze to unrestricted safety claims.

## Falsifiable gates

1. **Source identity before proof:** hash the three source files above; verify
   exact trait and impl headers, actual threshold return bodies, both constant
   definitions, selected `small_sort` forwarding body, and quicksort base-case
   bytes. Any mismatch refuses admission before verification. A fixture copied
   from another revision has no credit.
2. **Selected threshold positive:** for `T: FreezeMarker`, the actual trait
   call in `selected_freeze_threshold` must establish `threshold == 32`.
   `selected_freeze_threshold_false_31` must be rejected at its `== 31`
   assertion. A failure to resolve/bind the specialized impl is a binding or
   setup failure, not the intended negative.
3. **Wrong-specialization control:** `default-specialization-admission`
   uses `Cell<u8>` as a non-Freeze type and requires the actual default body to
   establish 16. If the selected Freeze case is accidentally bound to this
   fallback (16), its positive `== 32` assertion must fail. This control does
   not make the default body a substitute for the selected theorem.
4. **Base-case transfer:** preserve the unconstrained quicksort prefix and
   separately execute the Freeze-qualified prefix. The selected path must
   retain `len <= T::small_sort_threshold()` and call
   `T::small_sort(v, scratch, is_less)` on the same slices/callback. No literal
   threshold, asserted `len <= 32`, or `len >= 8` precondition is supplied.
5. **Selected helper entry:** preserve the selected impl's same-slice transfer
   into the actual helper prefix: `len < 2` return, evaluated `len + 16`
   scratch guard and abort, native `v.as_mut_ptr()` and
   `scratch.as_mut_ptr() as *mut T`, actual const/length branch, and first
   `sort4_stable` call boundary. The helper's branch establishes `len >= 8`
   only on that branch. The selected quicksort cutoff `len <= 32` alone does
   not establish nonzero size or caller `len >= 8`.
6. **Native posts:** any proof attempt must check the complete generated normal
   and unwind posts, lifetime/type/thread resources, local-free and leak
   obligations, native `T` and opaque `MaybeUninit<T>` arrays, and the actual
   same-slice/callback transfer. The return at the first sort4 callsite is a
   diagnostic cut; no sort4 summary or later helper behavior is credited.
7. **Stage and blocker classification:** inspect paired normal/read-only MIR
   and refinement. A parser/frontend failure involving `Option`, the loop, or
   specialization is `NOT_RUN` for threshold and caller obligations. Do not
   classify it as a negative. If the method binding is unsupported, the main
   agent may consider only the already recorded, exact source-bound method
   binding review; this fixture itself does not implement or authorize a
   translator patch. Any such semantic change needs its own written trust and
   regression gate before implementation.

## Outcome-to-next-decision map

- Exact source refusal: refresh the source-bound template and pins before any
  run; no semantic result.
- Positive `== 32`, false-31 rejected at its intended assertion, default-16
  control positive, and full posts: this qualifies only the selected threshold
  body and this diagnostic base-case transfer under the reviewed profile. It
  does not prove the public ZST guard, external caller applicability, all
  quicksort behavior, sort4, or whole SmallSort.
- Binding/Option/loop/frontend/setup obstruction: record its exact stage and
  source location; no threshold or caller proof credit. Do not infer that the
  source-level trait specialization is false.
- Overflow, abort, missing resource, unwind/post, or unrelated helper failure:
  record the first actual obligation. It is not a threshold false negative.
- Intended false-31 rejection at the exact assertion: confirms the negative
  control only; it does not qualify the positive or the specialization model.

The general quicksort wrapper retains `Option<&T>` and the loop to expose native
frontend behavior. If that prevents the target obligation from being reached,
the selected threshold microcase can still isolate threshold binding, but no
caller-to-helper transfer may be inferred from it. This diagnostic does not
introduce an ownership bridge, `MU` inverse, Freeze/Copy/purity restriction on
unrestricted safety, or a whole-quicksort theorem.

## Integrated minimal probe, before execution

`threshold-probes.rs` isolates threshold only; no unrelated insertion/helper
body can block it. The trait retains its actual threshold method declaration;
only this method is retained in both impls. Runtime bodies and constants match
actual source after ghost stripping/format normalization. `threshold-body`
renames just the selected method to a free generic body to isolate its verified
summary before dispatch. Explicit contracts retain native thread and full
normal/unwind guarantees (usize validity implied by16/32); generated safe
contract refinement must also pass. No parameter/resource domain is narrowed.
The selected/default generic impl contracts strengthen only numeric posts.
A method dispatch PASS still requires review of compiler def paths, substitutions
and clauses; existing ignoring-clause WARNING prevents specialization credit.
No new binding semantics is implemented in this first probe. False31 is valid
only at its intended assertion, never at trait/admission/setup error.
