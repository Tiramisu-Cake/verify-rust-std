# Independent semantic review: exact slice `as_mut_ptr` binding

2026-10-11, before maintainer implementation. **Conditional GO for candidate
integration** of patch SHA-256
`f200a5812149bb2278ded1d1ccb27a104b3dec3c03c5e40c79e30409d0d06916`
from proof commit `64922e1e5978b7204a6664e33a9f202aa6eea920` onto clean
VeriFast `46181aff379a5d4231cc51814cfe3732bda21c03`. This is a semantic
review of the delta, not acceptance of the combined tool profile or any
proof result. `git apply --check` succeeds against that tool head; no tool
file was edited for this review.

## Rule and source correspondence

The patch changes only the match arm in
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`: the existing exact
`std::slice::<impl [T]>::as_ptr` lowering also matches exact compiler symbol
`std::slice::<impl [T]>::as_mut_ptr`. The arm requires the translated
substitutions to have shape `[GenArgType T; _]` and exactly one translated
argument. It returns `FnCallResult (CastExpr (*T, arg))`, using the original
typed cast path and no heap/resource statement. `FnCallResult` assigns the
pointer directly; it introduces no callee contract or unwind branch. Other
method symbols retain their former regular-call path. The pattern failure on
a different arity is a rejection/error, not a permissive fallback.

The pinned `library/core/src/slice/mod.rs` SHA-256 is
`e3a45814fc07497d6e85d182d6b30782711e4b77752fa817988ec6da12e2cb6f`.
At line 778, `pub const fn as_mut_ptr(&mut self) -> *mut T` contains precisely
`self as *mut [T] as *mut T`; its `rustc_as_ptr` and `rustc_no_writable`
attributes are present. The patch models that value projection for the
source version, including `&mut [MaybeUninit<T>] -> *mut MaybeUninit<T>`.
The later scratch `as *mut T` is a separate existing MIR cast. In
`src/verifast1.ml`'s Rust pointer-cast typecheck, unsized-to-sized conversion
uses `strip_pointer_metadata` when sizedness is known; otherwise the generic
cast uses `ptr_cast`. Both functions in `bin/rust/prelude_core.rsspec` retain
pointer provenance and address, with target-appropriate metadata. They do
not create heap chunks. Existing slice full-borrow content relates the same
thin pointer to `array<T>` and `foreach own<T>`; those resources must already
come from the mutable slice reference and be restored by the caller.

**Trust boundary:** the translator arm itself checks the exact symbol and
translated arities, but does not inspect the source body, check the full MIR
signature/receiver mutability, or restrict the second substitution beyond
its presence. It relies on well-typed compiler MIR and the runner's exact
source/method hash, paired normal/read-only MIR and refinement admission.
Those runner checks are external to the translator, so the bare tool change
must not be advertised as a version-independent implementation of every
future `[T]::as_mut_ptr` body. A changed source or MIR shape requires fresh
admission/review before qualification. This is a limitation of the candidate,
not a blocker for the pinned, source-admitted experiment.

## Resource and path assessment

The new result is a raw pointer value only. It grants no pointee ownership,
writable permission, initialized `T` view of `MaybeUninit<T>`, lifetime token,
new provenance, disjointness, or alias fact. The receiver's mutable-reference
borrow and full source/scratch frames remain obligations of the existing
native Rust reference model. The source body cannot unwind; no kernel, ZST
size, RSSpec, posts, CURRENT, or native C3 isolation change is present in this
patch. The pointer value can be used later only when separate heap and
validity obligations are discharged. The method's `*mut T` return type alone
does not justify a write or read.

Pinned SmallSort SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`
retains `len < 2`, then the `scratch.len() < len + 16` abort check, then
`v.as_mut_ptr()` and `scratch.as_mut_ptr() as *mut T`, before the original
sort8/direct-sort4 conditions. The internal helper has no ZST guard;
`FreezeMarker` alone does not exclude ZST. No nonzero or selected-path fact
may be supplied by this binding. Source/abort/normal/unwind, callback and
borrow frames remain caller obligations.

## Evidence and affected gates

The exact proof review package and `FINAL-BASE-RESULT-MANIFEST.json` at commit
`64922e1e` distinguish pre-binding translator
`66e266d3a36517d8c552b34ab17357b7b5d11192095e47672504533611c76124`
from post-binding translator
`21ca026ae3279ef7da9a8a482b5355fab4c39250dec553854509b1f8923f52c4`.
The archived Cloud profile has a different translator from tool `46181aff`;
its results cannot qualify this integrated head. The later raw reviews report
isolated generic/MU and consumer positives, plus intended wrong-pointer,
missing-raw-rights and forbidden MU-initialized-`T` negatives. Default-off,
source-mutation and malformed-phase refusals are admission results, not
verifier negatives. Their archived `verification_accepted` and profile
acceptance remain false. The first archived build's malformed audit and
pre-MIR syntax failure confer no caller result.

Fresh combined-tool gates should cover exact source/hash and method shape,
normal/read-only MIR and refinement; canonical generic/MU native-reference
cases; a consumer with the real `as_mut_ptr` call and separate scratch cast;
the three intended negatives; source/phase mutations; and default-off exact
method rejection. Recheck the affected native C1/C4 and existing Bool C3
isolation/compatibility gates on the combined SHA. Inherited ZST/C1/C4
semantics need their own independent review and applicable regression record;
this note reviews only the new binding. Preserve C/C++ controls where the
combined profile's existing gates require them. Record full source/tool/
profile IDs and classify candidate, regression, consumer acceptance and
upstream acceptance separately.

The actual unfiltered helper prefixes in the later raw builds stop before
either pointer call, at `smallsort.rs:230` / `verified/lib.rs(20,24-32)`:
`len + 16 <= usize::MAX` is unproved. Public ZST continuation positives stop
on unresolved ghost `size_of`; the reachable ZST-branch negative alone does
not transfer a nonzero premise to this helper. Thus there is no actual caller
pointer/alias credit, callable summary, C4 composition or full sort4 proof.
These are proof-owner tasks, not reasons to expand this one-symbol tool delta.

**Decision:** integrate as an isolated candidate if the exact source
admission and fresh combined-tool gates above remain mandatory. Block profile
acceptance, consumer pin adoption and proof-credit transfer until their
separate obligations and reviews are satisfied. No local build, verifier,
proof extraction or Cloud dispatch was run for this review (`NOT_RUN`).
