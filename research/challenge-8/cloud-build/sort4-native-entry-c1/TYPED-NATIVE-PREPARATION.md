# Typed native source-frame preparation

Status: prepared as a Cloud-only isolated diagnostic; no typed proof result is
claimed here. The three source blocks are carried as individual `.gh` files so
each transported input remains reviewable and fixture-isolated.

The positive keeps the actual `small_sort_general_with_scratch<T, F>` signature
and the existing native-entry copied operations and generated full contract.
Inside the artificial `len >= 8` ghost boundary, it calls the stock
`produce_type_interp::<T/F>()`, obtains the complete source slice and `F` cell
plus thread resources, splits only the first four source elements, and calls
`c1_source_typed_identity`. That separately checked identity lemma requires and
returns exactly the two type interpretations together with source4 ownership,
the current-thread token, the comparator cell, and `F.own`. The diagnostic then
joins/restores the complete source frame and leaks both stock type chunks.

This tests logical chunk availability after explicit stock production. It does
not claim that native heap ownership entails either chunk. All `T`, including
ZSTs, and all vector/scratch lengths remain admitted by the exact native
signature contract. The case adds no scratch access, pointer arithmetic, size
condition, destination premise, source mutation, or runtime branch.

The missing-T and missing-F fixtures are byte-for-byte the positive block with
only the matching producer line removed. Both still call the checked helper and
retain the later leak statements. They are candidates for negative controls;
the collector intentionally leaves them uncredited until a fresh Cloud log
shows one exact missing `type_interp<T>` or `type_interp<F>` callee precondition,
with helper verification complete before native entry. Setup/admission errors,
an earlier helper failure, or a different first obligation remain
inconclusive.

Positive resource credit requires the existing candidate controls, complete
normal and readonly native-entry MIR/refinement gates, exact source-operation
mapping, artificial-boundary and execution trace mapping, captured automatic
normal/unwind AST posts, one native proof entry, helper verification before
native entry, execution of both producers/helper/both leaks, exit zero, no
errors, and the full leak check. A passing positive would establish only the
additional typed source-frame subset in this standalone native resource
diagnostic. It proves neither actual caller control flow nor sort4 execution,
source-to-destination transfer, a callable summary, or composition into C1.

The existing seven cases retain their source-block bytes and generated Rust
fragments. The caller-entry recipe adds only the three `.gh` inputs required to
transport these cases. No verifier/compiler/proof execution was run locally;
the new inputs require the designated Cloud lane before any negative is
classified.
