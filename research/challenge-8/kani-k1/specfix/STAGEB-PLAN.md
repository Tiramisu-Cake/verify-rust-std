# SPECFIX StageB plan (next session) — atomic F03 transfer

StageA (this session) ships checked profiles only opt-in; ordinary annotations and all 197/343
consumers keep the old generic contracts. StageB is one atomic patch; nothing below is applied.

## Why StageA

- No local compiler: an unverified rewrite of ~78 PFCs and ~59 stub consumers would be
  reviewed blind and could break the 197 ordinary set with no retry slot left.
- The stub chain `kani::stub(raw, adapter)` + `stub_verified(profile)` with extra adapter
  bounds, and the fn-pointer guard, are unestablished on pin `9461e07af7`; G1 row 10 tests them.
- The source tree must stay fixed for G1–G3.

## Changes StageB must make together

1. **Profile key = (T, comparator)**, not T alone. Current fixtures use two orders per type:
   `lt_u8`/`lt_u64`/`lt_i32` (key `x >> 1`) and `strict_less::<u8|u64>` (full order), plus
   `array_key_less::<16|17|85|86>`, `lt_b16`/`lt_b85`, `cell_value_less`, `drop_value_less`.
   Replace `Profile for T` by zero-sized tag types `impl Profile for Tag { type Elem; .. }`;
   adapters then need `ElemProfile` (T → its unique stub-consumer tag; all stub consumers use
   `lt_*`). DropValue/TaggedKey tags stay in their owner modules.
2. **smallsort.rs**: remove every clause that calls `F` or assumes order laws:
   swap `old(.. is_less ..)` decision + post-state pair-order ensures; insert_tail
   sorted-prefix requires and sorted ensures; sort4 sorted ensures; merge sorted-halves
   requires and sorted ensures. Probe-count ensures also go: a key-mutating `Cell` or a
   callback writing through a captured pointer breaks them for arbitrary `F`. Keep
   geometry/init (`can_dereference` source/region, `can_write` destination, disjointness,
   `2 <= N <= 32`) and the element `modifies`, or drop generic contracts entirely if a
   frame-only PFC has no consumer. No new generic clause may mention `F`.
3. **PFCs** (77 rows + 8 omissions, `consumer_kind=PFC` in `TRANSFER.tsv`): keep each name,
   retarget `proof_for_contract` to the family profile with its tag; convert the fixture F item
   to the canonical fn pointer (new instance, same math, same reads). Domains, N/offsets,
   frame asserts and covers unchanged. Each needs a fresh run; old PASS does not transfer.
4. **Stub consumers** (59 rows, `consumer_kind=stub_verified`): add
   `kani::stub(raw target, <family>_adapter)` and `stub_verified(<family>_profile)`; the
   fixture passes `&mut (Tag::CMP)`. Write insert_tail/swap adapters like `merge_adapter`.
   Negative requires controls retarget to the profile requires (sorted halves/prefix,
   same-index) with `expect_check` = the profile clause; add one always-true negative per
   adapter. Fallback/general chains keep the OPEN locality transfer; do not mask it.
5. **Real-body rows** (214): unchanged; arbitrary/mutating safety stays real-body. The byte
   probe stays for them with the StageA guard; profile harnesses use typed model counts with
   the u64/u8 bridge (G1 row 9 case 6) where they share a composition oracle.
6. **Gates**: static check that smallsort.rs runtime bodies/signatures are byte-identical and no
   generic clause contains a callback call; ordinary inventory exact 197; cfg-on inventory;
   targeted G1 of every changed adapter family and one PFC per (family, tag); full CI by the
   coordinator.

## Preconditions from this session's G1

Row 10 SUCCESS-path asserts plus a single guard failure at `merge_profile` requires is the
evidence that the adapter chain and the fn-pointer guard work on the pin. If row 10 fails to
compile or fails elsewhere, StageB must use real-body consumers (fresh time) instead of stubs.
