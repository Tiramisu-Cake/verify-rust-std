# Pinned source and exact comparator schedule

Current pin (shared std baseline, re-checked statically 2026-10-22): upstream
`cd371e035c7e573760c43bf934d53e8118ee3e7d`, merged into this branch as
`722320d3056595cc5cbe780f12bc0e6f242f8014`; actual source
`library/core/src/slice/sort/shared/smallsort.rs`, Git blob
`40939f922bcb6fdc7ee0d30427fa861827043827`, entire file SHA256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`.
No runtime source or generic signature changes.

Static re-check against the previous pin (VPS: Git blobs/text only; no compile,
extraction or proof): `swap_if_less` body (now lines 380–412) is byte-identical;
`sort9_optimal`/`sort13_optimal` bodies are byte-identical, with the same 25/45
ordered literal calls, every row shifted by −6 lines. The only blob changes
(+6/−12) are `CopyMarker` attribute, `small_sort_general_with_scratch`,
`small_sort_network` (lines 311ff: `&mut *ptr::slice_from_raw_parts_mut(..)` →
`slice::from_raw_parts_mut(..)` for `region` and the merge argument) and
`sort8_stable`. The hosted 2026-10-07 gate artifacts remain bound to the
previous pin only; the new pin has no hosted/Cloud gate run yet.

Previous pin (historical): entry `bea62488b44f8c557e45e04cb4eb259b0173422f`,
blob `e555fce440872898e47fd5114f32eb15401d07df`, file SHA256
`32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`;
line numbers there were +6 relative to the table below.

Each pair (a,b) below is exactly `swap_if_less(v_base,a,b,is_less)`;
comparison operand order is **is_less(v[b],v[a])**. The model puts the smaller
key at a and larger at b. Rows preserve sequential source order; a row is only
for readability and does not authorize callback reordering/parallelism.

| Network | Actual lines | Sequential pairs |
| --- | --- | --- |
| 9 | 435–438 | (0,3), (1,7), (2,5), (4,8) |
| 9 | 439–442 | (0,7), (2,4), (3,8), (5,6) |
| 9 | 443–446 | (0,2), (1,3), (4,5), (7,8) |
| 9 | 447–449 | (1,4), (3,6), (5,7) |
| 9 | 450–453 | (0,1), (2,4), (3,5), (6,8) |
| 9 | 454–456 | (2,3), (4,5), (6,7) |
| 9 | 457–459 | (1,2), (3,4), (5,6) |
| 13 | 484–489 | (0,12), (1,10), (2,9), (3,7), (5,11), (6,8) |
| 13 | 490–494 | (1,6), (2,3), (4,11), (7,9), (8,10) |
| 13 | 495–500 | (0,4), (1,2), (3,6), (7,8), (9,10), (11,12) |
| 13 | 501–504 | (4,6), (5,9), (8,11), (10,12) |
| 13 | 505–509 | (0,5), (3,8), (4,7), (6,11), (9,10) |
| 13 | 510–514 | (0,1), (2,5), (6,9), (7,8), (10,11) |
| 13 | 515–518 | (1,3), (2,4), (5,6), (9,10) |
| 13 | 519–522 | (1,2), (3,4), (5,7), (6,8) |
| 13 | 523–526 | (2,3), (4,5), (6,7), (8,9) |
| 13 | 527–528 | (3,4), (5,6) |

sort9_optimal requires len>=9 for a normal-return theorem; sort13_optimal
requires len>=13. Shorter lengths abort before any comparison (no normal/unwind
sorting post). Each otherwise-valid &mut [T] supplies initialized in-bounds
cells and unique slice access, modulo comparator's permitted shared effects.
Every literal index lies in [0,N); each pair has distinct logical indices.
`v.as_mut_ptr()` preserves allocation/provenance. For ZST, distinct logical
indices need not have distinct numerical addresses; the Rust proof must use
logical ownership, not an assumed pointer inequality.

On normal return, only the first N logical slots are permuted by network moves.
The suffix at N..len is unchanged **by network operations**, modulo allowed
comparator effects. Under preserved whole-element snapshots the whole slice is
a permutation with fixed suffix; under preserved keys only the key multiset is
fixed while occurrence identities move. All adjacent prefix keys are ordered.
These functions do not sort an arbitrary longer suffix.

On panic at comparator k, the prior k-1 completed CE transitions remain, and
the current comparison's effectful state is restored without the kth swap.
The entire slice remains initialized with the same logical ownership tokens,
modulo valid callback effects; no sorting post or rollback to entry is promised.

Caller small_sort_network (311ff) chooses N=13 when region.len()>=13, else N=9
when >=9, then insertion_sort_shift_left(region,N,...). This static check explains
intended prefix use; it proves neither that caller nor its insertion/merge steps.

Hosted gate pins the full file bytes, rejects unrecognized body operations and
checks all 25/45 ordered literal calls before generating the ghost model.
Its artifacts record actual source lines and model steps. This is source-sequence
correspondence, not Rust memory/callback/refinement verification.
