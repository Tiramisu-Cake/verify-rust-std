# Current-owner physical memory-cell permission probe

## Question and scope

This isolated fixture asks whether the pinned verifier's separation heap permits
one full points-to permission for the destination head after the existing
current-owner resource helper transfers owners, and rejects requesting two full
permissions for that same physical cell. It uses the same generic `T`, `F`,
thread token, source and destination resources, native-`usize` domain, normal
posts, and false unwind post as the checked `current_owner_transposition`
fixture. The positive case is named
`current_owner_transposition_memory_cell_positive`; the matched negative is
`current_owner_transposition_memory_cell_duplicate_negative`.

The checked helper prefix is copied intact from
`current-owner-permutation-cases.rs`, including list definitions, recursive
length and owner-transfer lemmas, the full pointer/domain predicates, and
`current_owner_transposition_resource`. In each case that helper first turns
source-owned resources plus the existing transposed destination values into
source values plus destination-owned resources. The positive body opens the
resulting destination-owned predicate and `array`, asserts exactly one full
`*dst |-> head(transposition_values(vs, i, j))` permission, then recloses both
predicates. The negative performs the same sequence and asserts two such full
permissions to the identical `dst` and identical current head value. Since
`i < j < n` and `n >= 2`, the head is a positive-stride array cell in the
non-ZST domain.

## Trust premises and soundness question

The pinned source `prelude_core.original.rsspec` defines nonempty `array<T>`
as full `*p |-> value` plus recursive `array(p + 1, ...)`, with the value list
cons matching that head. Thus opening the destination array exposes physical
head-cell permission directly. The probe relies on the verifier's separation
heap accounting for full points-to chunks at one pointer. It introduces no new
axiom, lemma, ownership bridge, `T.own` claim, or changes to the prelude or
verifier. The `foreach(..., own::<T>(t))` resources remain only the existing
transferred owner sequence; the duplicate request concerns physical memory
permission, even if `T::own` is empty or copyable.

This is a calibration of the pinned memory-permission semantics, not a new
soundness argument. A refusal at the duplicate target would support only the
specific same-cell permission uniqueness behavior exercised by this proof. A
failure before that target, at a helper, in the frontend, or at an unrelated
VC does not count as the intended negative. A successful duplicate assertion
would falsify the expected uniqueness behavior and must be investigated before
any claim is made.

## Expected stages and gates

The positive case should check every helper body and the case body, prove the
single full head permission, restore the complete destination array and owned
predicate, and satisfy the unchanged full normal post. It must also pass source,
refinement, return, leak, and dead-code gates. The negative shares the same
full preconditions and full normal/unwind posts; its sole intended failure is
the `TARGET` assertion requesting duplicate full permission for the same head
cell. The first hosted run is **CALIBRATION_ONLY**: do not classify its result
as a target negative or encode an expected diagnostic until the complete Cloud
evidence identifies the refusal stage, predicate, and target location. Both
cases must retain unchanged F framing, source bytes, payload, and unwind post.

No result here proves an actual copy, actual SmallSort behavior, a caller or
Freeze/share bridge, callback behavior, or ownership/resource transfer for a
real invocation. The fixture is a conditional ghost-resource probe only.
