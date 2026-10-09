# Caller C1/F frame obligations

This is a source-linked obligation map, not a caller proof or an accepted
summary. It isolates the `small_sort_general_with_scratch` path that constructs
`CopyOnDrop` and calls `bidirectional_merge`; the other two call sites have
different destination storage and are outside this transition sketch. Source
references are to [`smallsort.rs`](/root/verify-rust-std/library/core/src/slice/sort/shared/smallsort.rs:220)
in the repository checkout (the call-site audit records the inspected commit
and blob in [CALLER-C1-AUDIT.md](CALLER-C1-AUDIT.md)).

At entry, `v: &mut [T]` and `scratch: &mut [MaybeUninit<T>]` are exclusive slice
arguments (`smallsort.rs:220–224`). The function fills both scratch halves,
extends their sorted prefixes through every element, then constructs
`CopyOnDrop { src: scratch_base, dst: v_base, len }` and calls the merge
(`:265–290`). The guard copies all `len` elements from scratch back to `v` if
unwinding drops it (`:295–307`); after a normal merge, `mem::forget` suppresses
that restoration (`:286–291`). These source facts identify the state changes
to derive; they do not establish their VeriFast resource interpretation.

The required resource transitions are separate obligations:

1. **Caller handoff into the merge.** Derive valid, aligned, disjoint source
   and destination extents, initialized current bytes, the complete C1
   destination-option state, and current `F` ownership. The values copied into
   scratch must be related to the values and unique `<T>.own` resources from
   `v`; represent the scratch contents as the current source permutation with
   each existing owner exactly once. Bitwise copying bytes does not create a
   second owner. The stock prelude gives `&mut [T]` ownership through
   `full_borrow(k, <[T]>.full_borrow_content(...))`, whose body is `array(...)`
   plus `foreach(..., own::<T>(t))` ([pinned prelude](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/bin/rust/prelude_core.rsspec#L444), lines 444–451); it defines slice sharing separately as `array_share` over per-element `<T>.share` (same file, lines 429–442).
   No `share -> own` conversion is available or assumed.
2. **Conditional merge transfer.** The checked merge body must consume the
   current source owners once and transfer them to initialized destination
   cells on normal return, while preserving the current `F` owner and full
   target posts. This is an OPEN future arbitrary-n resource post: the present
   bounded len2/3 contract retains source owners and proves initialized destination
   options; it does not claim destination ownership or this caller composition. A copied destination value records the value at that copy;
   later callbacks may affect callback state or separately owned indirect
   targets. The destination must not acquire a duplicate `T.own` merely because
   its bytes match a source cell.
3. **Normal caller exit.** Once `mem::forget(drop_guard)` runs, prove that the
   destination owns the returned current permutation exactly once, that
   scratch's duplicate bytes are represented without a second owner, and that
   the caller receives the current `F` state. This is the merge normal post
   composed with the caller's own post, not an inference from `forget`.
4. **Unwind caller exit.** If the merge unwinds, `CopyOnDrop::drop` copies the
   entire initialized scratch range back to `v` (`:301–307`). Prove that the
   exact current scratch bytes are restored to `v`, each original owner is
   restored there exactly once, scratch is left without a duplicate owner, and
   the current `F` state and required unwind posts are preserved. This includes
   callback panic and the merge's final panic guard. Do not substitute the
   source's entry snapshot for values recorded at each actual copy.

The public `&mut` arguments and the private `v_base`/stack scratch allocation
are useful source facts for deriving the caller's allocation and separation
premises. They do not prove C1's pointer endpoints, positive stride, object
limits, or per-cell write chunks in the frozen model; those remain explicit
proof obligations. An address captured by `F` is only a numeric/address
association. It does not grant `F` permission to write the target, nor does
`FnMut(&T, &T) -> bool` alone establish a callback frame. The prepared
`callback-destination-frame-probe.rs` uses a standalone copied helper and an
unsafe raw write before panic; it demonstrates why address equality alone is
insufficient, but is not a counterexample through a public safe caller and
does not prove that such a callback is admissible under this caller's actual
borrow/provenance state. Derive active `&mut` alias admissibility and the
callback's resource footprint from the public caller separately; keep the
conditional helper contract conditional on its stated resources.

`FreezeMarker` is a local marker blanket-implemented for `T: Freeze`
([`mod.rs`](../../../../library/core/src/slice/sort/shared/mod.rs:8));
the merge itself has that bound and documents its stale temporary comparator
inputs ([`smallsort.rs`](../../../../library/core/src/slice/sort/shared/smallsort.rs):742–754).
This is not yet a VeriFast lifetime loan, current-value ownership bridge,
callback purity fact, or immutability guarantee through pointer fields.
`MaybeUninit` specs represent elements as `option<T>` and provide typed/untyped
conversion lemmas ([pinned std spec](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/bin/rust/std/lib.rsspec#L429), lines 429–483);
they do not justify turning arbitrary initialized-invalid bytes into valid
`T`. Generic and ZST cases need their own domain arguments; no byte-separation
or Freeze-to-loan conversion is implicit.

Finally, unrestricted safety keeps comparator answers arbitrary and preserves
current values/resources under the proved frame. Sorted-half, immutable-key,
strict-weak-order, and faithful-normal-answer premises belong to the separate
functional sorting proof. They must not be smuggled into the C1/F caller
contract to obtain an easier resource or callback argument.

## Fresh guard protocol evidence —54a22b0d

The direct generic `CopyOnDrop::drop` body is checked under the explicit strong
resource contract: count-n initialized source bytes with EXISTING T owners,
writeable destination bytes, valid/disjoint spans and guardfields, full normal
post and unwindfalse. Actualruntime1return1leak and source/copy operands are
separately checked. This does not establish its use through ordinary drop glue.

Freshpositive proofAST line100 has `TypePredDef` for CopyOnDrop's generated
`own` with bodyFalse, from the frozen frontend rule for a struct with no public
fields (translator.original.ml6692–6696; verifiedsource4–8 allfieldsprivate).
The prototype implementation proof is ASTFunc field7; actualruntime is field10.
PositiveVF log141–144 explicitly checks that prototype and executes the two
`open` annotations81/82 before the actual runtimebody proof. This establishes
`prototype safety_proof executed, vacuous own=false`, independently of the
strong actualbody result. Existing `compatibility_path_status=NOT_ESTABLISHED`
continues to denote `generic destructor/caller applicability not established`.

Frozen `drop_in_place<T>` stdlib597–600 needs a real `<T>.own` chunk. The
generated False guardinterpretation cannot provide a nonfalse owned CopyOnDrop
value to that route. Before caller composition: separately justify a nonvacuous
guard resourceinterpretation, source-linked construction and current source/
destination/ownerpool handoff, then actual normal forget and unwind glue.
No interpretation/constructor/kernel change is introduced by this evidence note.
It must preserve currentvalues, provenance and coefficient/term/size lineage,
and transfer every owner exactly once on both normal/unwind exits.
The arbitrary-index transposition component now checked in this same Build
helps only when the needed CURRENT destinationvalue relation has already been
proved; it supplies neither initializedbytes from arithmetic nor callbackframe
nor this guard/genericdrop applicability bridge.
