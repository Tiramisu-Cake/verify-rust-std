# A u8 N5–8 consumer audit (source only)

- Frozen base: `e0ff82577dc58950621dadc9c141d88a5821987f`; library tree
  `c522edd42ae67c385e1ee42a1c4d1bffb611c90b`. Scope references: `integ2/scope/p1-ordinary.txt`,
  `p2-ordinary.txt`, and `manifest.tsv`. All coordinates below are at this frozen base.
- P1/P2 graph entries include `general_stable_direct_u8_n5..n8`,
  `merge_contract_u8_n5..n8`, `network_correctness_u8_n5..n7` (N8 is P2-only),
  `dispatch_safety_stable_u8...` and unstable N8 dispatch, plus fallback u8/u64 N5..8.
- **Covered in source:** direct general harness (`verify/merge.rs:848–875,907–928,972–978`) chooses stable/general
  route, uses full-domain arbitrary u8 values and `lt_u8`, then checks sortedness and full-value
  probe multiplicity. No stub: runtime merge body is real. **UNKNOWN:** proof acceptance.
- **Covered in source:** stable `u8: FreezeMarker`, N5–8 enter `small_sort_general_with_scratch`
  (`smallsort.rs:49–62,220–290`): scratch length must be >= N+16; source v and scratch are
  separate allocations. N5–7 copy one item from each half, insert remaining tails; N8 calls
  `sort4_stable(v, scratch)` and `sort4_stable(v+4, scratch+4)`, then final merge.
- **Covered in source:** `sort8_stable` (`smallsort.rs:736–754`) has two sort4 calls at source offsets
  0/4 into scratch offsets 0/4, then `bidirectional_merge(scratch[0..8], dst)`. Its callers
  are at `small_sort_general_with_scratch:243–248` only when len>=16; merge source and dst are
  shifted regions of the same scratch allocation (offset gap len or len/2+8, hence disjoint).
  No N8 call is shown: callee shape only, not an N5–8 runtime consumer. **UNKNOWN:** proof acceptance.
- **Covered in source:** N8 direct general route has the two-sort4 + merge sequence above. sort4 contract
  (`smallsort.rs:680–694`) requires writable 4-element source and destination and disjoint
  regions; merge contract (`:837–849`) requires writable/disjoint destination and sorted halves.
  For disjoint regions within one allocation, `regions_are_disjoint` accepts sufficient offset
  (`verify/merge.rs:190–218`); **Gap:** source checks do not independently prove caller binding.
- **Covered in source:** P1/P2 standalone `merge_contract_u8_n5..8`
  (`verify/merge.rs:254–267,1235–1242`) declare PFC checks for exact N, initialized `[u8;N]`
  source, separate MaybeUninit dst; PFC supplies callee requires. T=u8/F=lt_u8/N=5..8 resolved.
  **Gap:** caller sorted halves/pointer binding. **UNKNOWN:** proof acceptance.
- **Covered in source:** P2 `merge_scratch48_contract_u8_n5..8` (`:1145–1199`) use prefix N of 48-element stable
  or general scratch plus separate initialized dst; only prefix N is initialized. This matches
  standalone scratch geometry. **Gap:** no runtime caller binding. **UNKNOWN:** proof acceptance.
- **Covered in source:** direct merge fixture (`:254–267`) uses exact-array source + separate dst; scratch48
  fixture (`:1145–1169`) has prefix N + separate dst. Both differ from runtime's shifted source
  and destination subregions in the same original allocation for some general merge routes.
- **Covered in source (contract claims):** sort4 modifies dst[0..4] and ensures sortedness/probe
  count (`smallsort.rs:680–694`); merge requires initialized source/sorted halves and declares dst
  frame. Runtime initializes scratch prefix before merge (`:265–290`). **UNKNOWN:** independent
  frame proof or caller init/contract composition.
- **Covered in source:** P1/P2 fallback property N5–8 (`verify/merge.rs:1222–1233,1296–1316`)
  calls `small_sort_fallback` with real `insert_tail`, no stub. **UNKNOWN:** proof acceptance.
- **Covered in source:** `network_correctness_u8_n5..7` ordinary; N8 cfg-controls/P2
  (`verify/network.rs:930–997`). They use unstable dispatch and check sortedness/counts at N<9;
  no stable sort4/merge edge. Stable/unstable dispatch N8 checks safety/normal return only
  (`verify/network.rs:254–284,310–314`), with `panic_on_ord_violation -> assume_order_violation`.
- **Gap:** PFC fixtures are separate from actual caller AST/MIR argument binding, same-allocation shifted disjointness,
  initialized-prefix provenance, or composition of verified callee contracts into caller credit.
  **UNKNOWN:** acceptance/evidence status for all PFC claims; no standalone credit inferred.
  Direct B proof is not a replacement for the A callee theorem; source annotation/manifest claims
  are not proof credit. No A u8 N5–8 typed-oracle credit is inferred by this read-only audit.
