# Bidirectional merge lengths two and three — design before implementation

This is a bounded, exact-source diagnostic for the actual `bidirectional_merge`
body. It creates a new hosted-only generator and does not modify the admitted
length-two preparer. The generated CASE must include the actual `merge_up`,
`merge_down`, `bidirectional_merge`, and `panic_on_ord_violation` bodies from
the same pinned `smallsort.rs` blob. It reuses the current source gate, exact
body extraction, callback setup, and accepted helper contracts. Ghost stripping
must reproduce every runtime body byte-for-byte. No callee is replaced by an
empty or bodyless summary.

The profile allows only `len == 2 || len == 3`; in both cases `len_div_2 == 1`,
so the real loop has one iteration while the actual even/odd branch is taken
on different paths. The target remains a bounded unsafe projection, not a
generic safe-caller or whole-sort theorem.

## Entry domain and resource contract

Require a current-thread token, `type_interp::<T/F>()`, positive `size_of<T>`
and alignment, and a source slice length of two or three. Bound the complete
source and destination spans with nonoverflowing numeric endpoints,
`isize::MAX`, object provenance limits, in-range element-pointer limits,
positive aligned bases, and disjoint source/destination byte ranges. State
checked C1 one-element pointer premises for each source/destination cell used
by the actual calls: source cells 0 and 1 and destination cell 0 are always
present; source cell 2 and destination cell 2 exist only when `len == 3`; the
reverse call uses `src + (len - 1)` and `dst + (len - 1)`. Explicit cell premises
are bounded caller obligations. Deriving them from an allocation contract
remains open.

The entry contract carries the current `T` value and `<T>.own` for source cells
0 and 1, with source cell 2 and its owner conditional on `len == 3`. It carries
writable option-valued raw chunks (`*dst |-?-> ?old`) for destination slots 0
and 1, with slot 2 conditional on `len == 3`. This matches the accepted C1
copy contract's initialization-aware destination chunk. It also carries the
current `F` value and owner. No destination `<T>.own` is introduced by the physical copies. Do
not derive source ownership from slice sharing, add a `Freeze`/purity premise,
or constrain comparator answers or legal `FnMut` state effects.

Normal completion retains current source-cell values and owners for the
selected length, retains the current `F` value and owner, and makes every
corresponding destination option `Some(_)`; it claims no ordering, permutation,
or destination owner. The three allowed unwind stages are exact:

1. If the first callback panics, all destination options equal their captured
   old options.
2. If the second callback panics, destination slot 0 is `Some(_)`; every other
   present option equals its captured old option.
3. If the final ordering guard panics, every destination option is `Some(_)`.

The named checked option relation must encode these three states by matching
option constructors and equality against each old option. It must support
arbitrary old `None` and `Some` values. The no-write state and a write that
happens to equal an already-`Some` old value can overlap as logical states;
the relation still explicitly records the exact allowed snapshots. The odd
copy itself is non-unwinding. Preserve current source owners and current `F`
owner on each unwind edge. Never summarize arbitrary partially written
destinations.

## Loop and source-layout obligations

The one-iteration `Some`-body invariant retains the complete entry geometry,
source values/owners for exactly the selected length, comparator value/owner,
all current destination option chunks, lifetime token, and stock iterator
state `start == end == 1`. Initial forward cursors are `src`, `src + 1`, and
`dst`; reverse cursors are `src`, `src + (len - 1)`, and
`dst + (len - 1)`. Preserve Range and tuple-three local frame facts for MIR
addresses 34, 35, 53, and 65, but obtain fresh role certification for this
generated annotation set before accepting those stack IDs. The unchanged odd
copy and final guard remain live/checkable under the combined length domain.

Reuse checked positive-stride/alignment lemmas from the accepted pointer
domain ghost prefix. Where a helper precondition cannot be derived from the
new valid-array geometry, keep the corresponding explicit C1 cell premise and
record allocation-to-premises derivation as open. Do not close ZST, aliasing,
unwind, dead-code, leak, or source-admission gates through assumptions or
contract weakening.

The preparer retains the existing pre-loop `size_align` annotation and packs
the new ghost calls into the three existing post-invariant annotation lines.
This keeps raw MIR local-address IDs stable; hosted role certification remains
required for the generated case.

## Hosted evidence gates

The new generated case is named `bidirectional_merge_len23`. The root-owned
workflow allowlist, exact-source admission, normal MIR pipeline, and stack-role
certification must select this exact case and source SHA. Require exporter,
decoder, VeriFast, refinement, exact ghost stripping, all four actual function
bodies, both actual callback sites, even and odd branches, guard, normal and
unwind posts, leak checking, and strict dead-code checking. In particular,
`len == 2` and `len == 3` must each reach their parity outcome; a dead odd
branch invalidates the intended diagnostic. Any call-precondition, parser,
or helper failure outside its named proof obligation is inconclusive.

The explicit cell premises establish only a bounded proof projection. A
separate caller derivation must show that real allocation, provenance, source
ownership, and destination scratch resources imply these premises before this
can support an actual safe caller. No C1/allocation bridge or generic-length
claim is made here.
