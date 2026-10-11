# Actual helper entry: first open obligation

Build `1d2237d7-2183-48ff-8aa9-a6c8d29fcd83`, exact proof/infra
`0a61febf105b29dcb89d6fc25ec993bdcfd17e46`, verifies the unchanged runtime
entry checks of `small_sort_general_with_scratch` to the first direct sort4
boundary. Both pre/post pointer-binding variants pass paired MIR/refinement
and stop at `verified/lib.rs(20,24-32)`: `len + 16 <= usize::MAX`.
The exact source expression is `smallsort.rs:230`, with `len` from line225.
The pointer binding changes no premise used at this earlier expression.

The helper itself has no ZST guard. Its generic native entry permits ZSTs;
`FreezeMarker` does not imply nonzero size. Native array footprint bounds
`len * size_of<T>()`, which does not bound `len` for ZST. Pinned core
`mem/mod.rs:1528–1544` and RSSpec `std/lib.rsspec:390–393` explicitly permit
ZST slice lengths through `usize::MAX`. No positive size or small length
may be supplied merely because the target direct-sort4 branch is interesting.

This is a verification obligation, not evidence of runtime UB. The exporter
uses `-Coverflow_checks=off`; the source addition may wrap for a sufficiently
large ZST slice, whereas this proof model requires its mathematical sum to
fit. Changing general arithmetic semantics is outside this session's narrow
source-bound pointer/caller scope. No abort binding was implemented because
abort is later than the demonstrated first obstruction.

Two real routes could establish a sufficient entry domain: transfer public
`T::IS_ZST` guard's nonzero continuation fact along the same actual `T`, or
prove the actual small-sort threshold/clamp and scratch-construction route.
The static chain and precise specialization obligations are in
[UPSTREAM-DOMAIN-ROUTES.md](UPSTREAM-DOMAIN-ROUTES.md). The public first-guard
Cloud diagnostic is separate: even a passing guard prefix cannot stand in
for transfer through driftsort/quicksort/Freeze dispatch/scratch construction.
Neither route is currently closed at the actual helper entry.

The isolated real pointer consumer preserves native source and opaque MU
scratch. Three assertion negatives confirm no wrong pointer, unrelated raw
authority or initialized-T ownership is obtained from the pointer/cast.
It proves no source split at the first sort4 call, no scratch writes, no
callback invocation, and no caller-to-C4 composition. Full sort4's C5/copies,
the second direct call, sort8 and full helper/caller remain separate goals.
All inherited ZST/C1/C4 and this pointer profile remain experimental/unaccepted.
