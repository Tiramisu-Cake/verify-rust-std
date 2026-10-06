# Tracked shared reference to `ManuallyDrop<T>`

This experimental VeriFast 26.09 source patch applies to commit
`809de4596839b739dd999f9e462242c835e3af46` after the tuple-parser,
FnMut HRTB, and strict lifetime-binding-cut patches. The translator input
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml` must have SHA-256
`15a9db2fbafa0f04e74e75e5bee0dd7d941a7428906e42432e9d9687843bbcce`.
The address-taken traversal patch changes a different source file and is also
required by this research profile. The sole new source change is
[verifast-manually-drop-ref.patch](verifast-manually-drop-ref.patch), SHA-256
`5500204aadd0ea0a2996d63d064160185457b6d337782aa4300c11272ab450cc`.
Its statically applied translator has SHA-256
`f8751fab591ed98daebf446eb34800e892e72a838c7c083f643bd4efabbb0432`.

Rust's `ManuallyDrop<T>` has no destructor even when `T` does. The MIR exporter
therefore records `placeDoesNotNeedDrop=true` for the implicit `&tmp` in
`&*tmp`. Before this patch the translator's no-drop shortcut emits a bare
`AddressOf(tmp)`. The following borrow of the dereferenced shared reference
uses the existing `reborrow_ref`, which needs `ref_initialized(tmp_addr)`.
The bare address has neither that initialization predicate nor a token that
could connect it to a separately precreated reference. In hosted run
[37415731049](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37415731049),
the isolated `ManuallyDrop<i32>` fixture reaches precisely this missing
`ref_initialized<i32>(tmp_addr)` obligation after the address-taken fix.

For a shared immutable borrow of a non-reborrow place whose **raw MIR place type** is
exactly `core::mem::ManuallyDrop<T>` (or its `std::mem` spelling, with one type
argument), `track_manually_drop_shared_ref` overrides the no-drop shortcut.
The existing branch then emits `create_ref(&tmp)`, including its normal token
and initialization preconditions. The match requires the MIR place kind
`Other`, so a shared-reference reborrow remains on its existing path. Other
borrow kinds, places and types retain their prior translation. This opt-in
source profile strengthens proof obligations; it does not create a reference,
heap chunk, initialization fact, or ownership fact by itself. The prior
`tuple_address_taken` profile remains available to reproduce the failure.

The intended proof uses the existing aliasing model. After initializing
`tmp`, `precreate_ref(&tmp)` supplies a fresh reference pointer and its
`ref_precreated_token`/`ref_init_perm`; `init_ref_readonly(tmp_ref, 1/2)`
consumes a fraction of the actual local `points_to<T>` and supplies
`ref_initialized(tmp_ref)`. The translated `create_ref(&tmp)` consumes its
matching precreation token and returns that same pointer; `reborrow_ref`
then preserves the initialization predicate. After the last read,
`end_ref_readonly(tmp_ref)` restores the local storage fraction. This route
uses no `T.own` bridge or assumed equality between distinct reference
provenances. The existing translator's transparent `ManuallyDrop<T>` type
translation and identity handling of `new`/`deref` are unchanged.

Hosted acceptance must build this profile from the pinned source and exact
input hashes, rerun the eight HRTB and twelve lifetime-cut regressions, and
run isolated scalar and `ManuallyDrop<i32>` positive cases with exact read
postconditions. The `ManuallyDrop` case must include the precreation,
readonly initialization, and end lemma. Negative cases must reject a missing
precreation token, missing reference initialization, and missing source
`points_to` permission at their intended obligations; a frontend error does
not count as a negative proof. The actual unrestricted `T`/`F`, symbolic-length
`insert_tail` probe should advance beyond the `&*tmp` reference check with
identical Rust bytes. Guard ownership, its later reads and cleanup, loop
invariants, and the final range contract remain separate obligations.
All builds and verification run only on hosted Actions.
