# S1 actual-body map (verification NOT_RUN)

All rows: independent symbolic bytes in initialized backing3, symbolic N in 0..3,
active interior span [1..1+N] of backing5 with initialized canaries at both sides.
All attrs are on implementation bodies, gated by all(kani,kani_smallsort_sorting).
PFC mode selects the exact qualified trait method below, with F=KeyLess<T>.

| Planned selector suffix | Exact target | Type | Threshold | Body/route at N0..3 |
|---|---|---|---|---|
| stable_default_cell | <Cell<u8> as StableSmallSortTypeImpl>::small_sort | Cell<u8> | 16 | Stable default; insertion, empty scratch |
| stable_freeze_u8 | <u8 as StableSmallSortTypeImpl>::small_sort | u8 | 32 | Stable Freeze; general |
| unstable_default_cell | <Cell<u8> as UnstableSmallSortTypeImpl>::small_sort | Cell<u8> | 16 | Unstable default; fallback insertion |
| unstable_freeze_u8 | <u8 as UnstableSmallSortTypeImpl>::small_sort | u8 | 32 | Unstable Freeze forwarding to Copy body |
| freeze_default_noncopy | <NonCopyByte as UnstableSmallSortFreezeTypeImpl>::small_sort | NonCopyByte | 32 | Freeze default; general (1*48<=4096) |
| freeze_copy_u8 | <u8 as UnstableSmallSortFreezeTypeImpl>::small_sort | u8 | 32 | Freeze Copy; network (1*32<=4096), early insertion |

Requires is v.len() <= <T as THIS trait>::small_sort_threshold() on each body.
Stable Freeze adds v.len()<2 || scratch.len()>=v.len()+16. Stable default ignores
scratch. No requirement that MU scratch holds initialized T. Smoke uses separate
flat allocation, legal scratch length 0 for N<2 and N+16 for N>=2. No claims for
arbitrary scratch allocations/offsets from this fixture.

unstable/quicksort.rs checks len<=threshold immediately before the trait call;
stable/quicksort.rs also checks len<=T::small_sort_threshold() immediately
before the call, with the matching Stable trait. This map
is source inspection, not verification of callers. S1 does not cover network
merge N>=18, general sort4/sort8, all branches, length32, or arbitrary T/F.
