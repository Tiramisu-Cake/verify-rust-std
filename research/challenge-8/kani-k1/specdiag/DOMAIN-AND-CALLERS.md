# Supported domains and caller map

Static source map at task library tree
`b10a21505be73f26be50cd0e1c0f0c5f48773f9a`. Frozen counts come from
`integ2/scope/manifest.tsv`: P1 has 197 ordinary names; P2 selects 343
`p2_candidate=yes` names. That manifest's source identity is
`c522edd42ae67c385e1ee42a1c4d1bffb611c90b`; `callers.tsv` preserves those
source path/line bindings and uses current task-tree source for the call chains.

Status terms in `callers.tsv` are inventory states: `P1-selected` means only
that a row is in the frozen P1 ordinary set; `P2-source-only` means it is a
static P2 candidate. Neither is proof credit. `OPEN/control` means a negative
or frame control, not an accepted theorem. Stub binding remains `OPEN` unless
the named target, `T`, `F`, `N`, backing allocation, active region, and an
accepted matching PFC are all established. No P2 patch is applied here.

## Recommended supported domains

Shared contract principles:

- Memory-safety claims require correctly aligned, in-bounds pointers in their
  stated allocation; valid initialized `T` values wherever the body or
  predicate forms `&T`/performs a typed read; and disjoint source/destination
  regions where copying requires it. A writable predicate alone does not
  prove initialization.
- `FnMut` allows mutation of its captured state. Any future contract must say
  whether comparator writes are forbidden or declare an external effect
  footprint disjoint from the element regions. The current `modifies` clauses
  describe element memory only; they do not specify comparator state or other
  callback effects. Do not silently infer a comparator frame from an element
  frame.
- A full-value permutation claim permits arbitrary comparison results only
  when calls do not mutate the compared elements/keys and callback effects are
  disjoint from the element storage. `Cell` key mutation breaks that claim even
  if the algorithm only moves whole values. A sortedness claim additionally
  needs a stable, pure strict weak order. Do not assume order laws for safety
  under arbitrary/mutating comparators.
- Normal-return claims exclude comparator panic/nontermination. `merge` also
  has an explicit order-violation panic path; its sortedness contract needs
  sorted halves and the lawful comparator profile.

| Target | Memory and value domain | Ensures/frame support and limits |
| --- | --- | --- |
| `swap_if_less<T,F>` | Initialized writable allocation; distinct in-bounds positions in one allocation. Arbitrary Boolean results are fine for body memory safety. Full-value permutation needs the comparator not to mutate either key/value. | Current frame is only the two positions. It does not frame captured comparator state or any other callback writes. Pair-order needs a pure/stateless lawful comparator. The first ensures records a comparator decision in the pre-state; the second ensures calls `F` again after the body through a pre-state raw pointer, so the two ensures are not a one-call frame for stateful `FnMut`. |
| `insert_tail<T,F>` | Initialized writable `[begin,tail]`, `begin < tail`, same allocation; sorted `[begin,tail)` only for the lawful profile. Arbitrary result sequences can support movement/permutation only if calls cannot mutate keys. | Element frame is `[begin,tail]`; prefix before `begin` and suffix after `tail` are outside it. The current additional ensures is equality of `probe_count` before/after, not `same`. Comparator effects outside the element frame remain unspecified. Normal return excludes panic during any repeated callback. |
| `sort4_stable<T,F>` | Four initialized source values; four writable, valid, disjoint destination slots. Any comparator result sequence is compatible with memory safety and movement of unmodified values; sortedness needs a pure strict weak order. | Current modifies target is `dst[0..4]`; source is read-only in the body. There is no comparator-state frame. Do not claim full-value permutation when a `Cell` comparator mutates keys. The representation probe does not establish a generic typed-value postcondition. |
| `bidirectional_merge<T: FreezeMarker,F>` | `2 <= N <= 32`, initialized source, writable disjoint destination of `N`, and each half sorted by a pure strict weak order for merge correctness. Arbitrary comparator results suffice only for bounded body-safety claims, not sorted output. | Modifies destination only. `FreezeMarker` constrains mutation through shared `T` references, but does not constrain `F`'s captured external state. Requires and ensures call `F` through `merge_inputs_are_sorted`/`is_sorted_unrolled`; callback state can therefore change during specification evaluation. Normal return excludes comparator panic and order-violation panic. |

## Helpers and future-contract obligations

| Finding | Requires/helpers involved | Ensures/helper involved | Change boundary and status |
| --- | --- | --- | --- |
| F03 callback count/effects | `swap_if_less` has no callback-related requires; `insert_tail.valid_sorted_tail` invokes `is_sorted`; `merge.merge_inputs_are_sorted` invokes `is_sorted_unrolled`; `sort4.valid_sort4_regions` is callback-free. | `swap_if_less` snapshots a decision with `F` and its pair-order ensures calls `F` again; `insert_tail` sortedness calls `F`; `sort4.is_sorted` and merge `is_sorted_unrolled` call `F`. | Specify one body-call sequence separately from spec observers. Add an explicit comparator effect footprint or restrict effectful callbacks. Pinned generic contract support for expressing purity/state effects is OPEN. |
| F04 initialization and geometry | `swap_if_less` checks same-allocation, `can_dereference` and `can_write` at both positions. `insert_tail.valid_sorted_tail` checks writable geometry and reads sorted prefix. `sort4.valid_sort4_regions` uses `can_write` for both source and destination plus disjointness. `merge.valid_merge_destination` checks writable destination/disjointness; sorted-half helper performs typed reads. | Typed output sortedness and probe helpers read destination after body. | `can_dereference` on pin `9461e07af7ec929f050aa4192f29363c9be07779` includes initialization and validity; `can_write` checks alignment/in-bounds. Tail initialization is not implied by `valid_sorted_tail`'s writable geometry. A boolean predicate is not automatically safe as an assumption in every context. Admission and actual read must remain distinct. |
| F05 representation oracle | `matches_value_probe<T>` reads `size_of::<T>()` bytes; `probe_count` and `_unrolled` call it for each active element. | `swap_if_less` has a distinct nested `same<U>` that snapshots/compares `size_of::<U>()` bytes; `insert_tail`, `sort4_stable`, and merge use probe-count equality. | The global probe is 128 bytes, so `T > 128` can overrun the probe in `matches_value_probe`; that fixed bound does not apply to `same`. `same` still reads representation bytes and does not make padding initialized. Replace with initialized typed-value observations only after target-specific design. |
| Frame and normal return | `modifies` currently names the element region only. Comparator callbacks may be repeated, may mutate captures, and can panic; body call counts differ by algorithm. | `swap_if_less` states pair transfer and pair order; `insert_tail` states sortedness and probe count; `sort4_stable` and merge state sortedness and probe count. | Future frame edits must define external comparator writes for each target, not just the element region. Arbitrary effects and panic need separate normal-return conditions. Status OPEN; no contract patch is made. |

Representation details are intentionally separate: the 128-byte probe bound
belongs to `matches_value_probe` only. For padded `T`, initialized fields do
not initialize padding, so `same<T>`'s byte slices and probe matching are not
generic typed equality. The `sort4`/`insert_tail`/merge probe-count ensures
cannot be promoted to universal permutation claims for padded or
interior-mutable types. For `merge`, keep `N <= 32` because its contract helpers
are unrolled only through that bound.

## Production call graph and verified-stub boundaries

- `small_sort_network` calls `swap_if_less` from its fixed networks and calls
  `insertion_sort_shift_left`, which calls `insert_tail`. For current network
  proof fixtures of `u8`/`u64`, lengths `0..=8` do not enter the 9/13-element
  compare-exchange networks; `N>=2` reaches insertion, and `N>=9` reaches
  compare-exchange. At `N>=18`, production network routing can also reach
  `bidirectional_merge`; the listed `network_correctness` fixtures stop at 17.
- Selected `network_safety_unstable_u64_*` harnesses call the real
  `UnstableSmallSortFreezeTypeImpl` route with initialized `[u64;N]` and
  `volatile_reading_less_u64` (volatile reads, arbitrary result). For `N=0..8`
  the network body uses insertion only; `N=9..12` presorts 9, `N=13..17`
  presorts 13. At `N=18..24` each half presorts 9; at `N=25` the right half
  presorts 13 while the left uses 9; for `N=26..32` both halves presort 13,
  then merge. The `N>=18` harnesses stub only the order-violation panic. They
  check normal return/safety, not permutation or sortedness.
- `small_sort_general_with_scratch` calls `sort4_stable` twice on disjoint
  four-element input/scratch regions, calls `insert_tail` on active runs, and
  calls `bidirectional_merge` into a separate scratch region. `small_sort_general`
  supplies a 48-element stack scratch view. Stable/general trait routes select
  these functions for `u8`/`u64` fixtures; the trait methods themselves have no
  contracts.
- For those `u8`/`u64` route fixtures, let `L=N/2`, `R=N-L`. The scratch
  insertion calls use `begin=scratch+0` for the left run and
  `begin=scratch+L` for the right run. The first inserted tail is index 1 when
  `N<8`, index 4 when `8<=N<16`, and index 8 when `N=16`; each run then calls
  through its last element. Merge reads initialized `scratch[0..N]` and writes
  the original `v[0..N]`. Stable route scratch is an uninitialized 48-element
  `MaybeUninit<T>` array before the algorithm writes the active prefix; general
  route scratch is the corresponding internal 48-element stack allocation.
- `small_sort_fallback` calls `insertion_sort_shift_left` and therefore
  `insert_tail`. The `sorted_permutation_fallback_*` harnesses stub
  `insert_tail`; they do not PFC it. Their target/PFC correspondence is OPEN
  unless the exact `T/F/region` is bound to a separately accepted direct PFC.
- `general_stub_harness` in `verify/correct.rs` stubs both `insert_tail` and
  `bidirectional_merge`; `sort4_stable` stays real. In `verify/merge.rs`,
  `define_general_sortedness_harness` stubs only `bidirectional_merge`; both
  `insert_tail` and `sort4_stable` stay real. These are distinct chains and are
  listed separately in `callers.tsv`. Their nearest direct PFCs may match
  `T/F/N` but use different allocations or active offsets, so the stub binding
  is still OPEN unless that exact geometry is established.
- `network_correctness_*` entries call the real unstable trait route, not a
  target contract stub. `insertion_permutation_*` calls real
  `insertion_sort_shift_left`/`insert_tail` with an arbitrary volatile-reading
  comparator and no sorted-prefix assumption. Their results do not prove the
  named PFC ensures. `N>=9` network correctness checks sortedness and relies on
  separately checked structural/network insertion properties for permutation;
  it is not a full-route permutation theorem.
- Selected `insertion_safety_u64_*` rows use initialized `[u64;N]`, choose the
  exact offsets recorded in TSV, and call the real insertion body with a
  volatile-reading comparator whose result is arbitrary. The paired
  `mutating_insertion_safety_cell_*` rows use initialized
  `[Cell<TaggedKey>;N]`; their comparator writes both keys and returns an
  arbitrary result. These are normal-return/safety checks with no sorted-prefix
  assumption and no value-permutation claim. They directly show why mutating
  key callbacks cannot inhabit the supported permutation profile.
- Selected `dispatch_safety_*` rows use `ArbitraryValue` initialized exact
  arrays, a volatile-reading arbitrary comparator, and only a
  `panic_on_ord_violation` stub. Stable routes use the general path. Unstable
  `u8` uses the network path; `[u8;16]`, `[u8;17]`, `[u8;85]`, and non-Copy
  `DropValue(u8)` use general; `[u8;86]` falls back because its 48-element
  scratch size exceeds 4096 bytes. General uses `sort4` for `N>=8`, `sort8`
  instead when `N>=16 && size_of::<T>()<=16`, insertion on active runs, and a
  merge for `N>=2`. Network uses insertion for `N>=2`, `swap_if_less` for
  `N>=9`, and merge for `N>=18`. No selected dispatch row stubs these target
  functions or PFCs them.
- `route_safety_all_routes_*` chooses among direct general `u64`, non-Copy
  `WrappedU64` unstable general, and stable `u64` general. It initializes the
  exact input array and scratch as needed, executes real sort4/insertion/merge
  bodies, and stubs only order-violation panic. It makes no value-frame claim.

`callers.tsv` has explicit rows for each manifest-selected direct PFC, negative
control, fallback/general/stable composition consumer, network correctness
consumer, insertion-permutation and insertion-safety consumer, dispatch and
route-safety consumer. It records exact fixture `T`, `F`, `N`, backing,
offsets, initialization, observed frame, actual stub chain, and the nearest
named PFC source. A source analogue is not a verified stub binding. When
target reachability or matching allocation/active region is not established,
the row says `OPEN`; no proof credit is added. `frozen_manifest_ref` is a path
relative to `library/core/src/slice/sort/shared/smallsort/verify/`; call chains
are relative to the harness name in the same row. The `reject_mutant_merge_up`
manifest entry is excluded because it targets the separate `merge_up` helper,
not `bidirectional_merge`.

## Points after G1/G2 (see RESULT-SPECDIAG.md)

- `swap_if_less` with a counting `FnMut`: under PFC the observer `calls==1` fails and
  `calls==3` is reachable (body + `old` decision + pair-order ensures); separately the
  `Cell` write is outside `modifies` (assigns failure in `mem::replace::<u8>`). A future
  contract must restrict effectful callbacks or declare their footprint; the pair-order
  ensures must not re-call `F` for stateful comparators. Plain call: exactly one call.
- Always-true `F` violates the sortedness ensures of `sort4_stable`, `insert_tail` and
  `bidirectional_merge` with all requires met: sortedness belongs to the lawful pure
  order profile only; safety/permutation claims must be stated separately for any `F`.
- `valid_sorted_tail` and `valid_sort4_regions` admit an uninitialized tail/source
  (geometry only). The actual uninitialized read is NOT_DETECTED under CI flags and the
  `-Z uninit-checks` profile reports unsupported layouts for `MaybeUninit` arrays and
  raw-pointer/union code (production `select_unpredictable`), so read-side evidence is
  UNKNOWN. Requires need an explicit initialization predicate.
- `sort4_stable` static source: `can_write` is true (geometry); the requirement is an
  artifact of the predicate, not a permission to write.
- `matches_value_probe::<[u8;129]>` reads past the 128-byte probe (helper confirmed);
  the actual contract use timed out at 3 min (UNKNOWN). `same<[u8;129]>` passes, so the
  bound applies to the probe only. Padding: same/probe binding UNKNOWN in both profiles.
- K5 generic trait contract/stub barriers stand; bounded free wrappers remain a possible
  form, not established proof credit or comparator-purity expressibility at this pin.

Source references: `smallsort.rs` annotations and production bodies;
`verify/merge.rs` representation/domain helpers and PFC/stub harnesses;
`verify/correct.rs` fallback/general consumers; `verify/network.rs` direct
swap/insertion PFCs and transitive network fixtures; `verify/assembly.rs`
plain original/mutant pairs; K5 limitations in
`/root/verify-rust-std-kani-k5/research/challenge-8/kani-k1/RESULT-K5.md`.
