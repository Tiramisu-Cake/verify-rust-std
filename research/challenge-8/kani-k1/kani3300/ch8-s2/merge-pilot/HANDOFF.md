# W11 → future integrator13: offline merge pilot READY

Task `task9856043dab21de8346b68196fa91929b96331293`, input g0
`9856043dab21de8346b68196fa91929b96331293`. Canonical pins/budget reference:
`../../s2-f4-coordination/INPUTS.json` (unchanged). This package is independent
of W13 S2batch; it neither waits for nor edits W13 source/control or frozen S1.
No source patch is applied or required for this stage.

Source commit `99e8456d200fff1299ee5756279cddb23921dc65`, tree
`b769b084f9982cbcb166229b29b6bd2bff136c51`. Tool reference
`0aac16ef62da9e9d5645782d458593e5d78143ba`, tree
`9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`. Control reference
`7c41333f9bfcfd7eb4e0ede7bd316443090c9025` remains reference only.
No tool/control execution or new acceptance inferred from these pins.

Chosen form: full simultaneous counts for all 256 byte values, guarded C5,
and pure snapshot rank strengthening for actual stale fronts/duplicate ties.
Read `INVARIANT.md`, `source-map.json`, then `validation.json`/`VALIDATION.md`.
K0–K8 remain machine-proof obligations. No actual Kani induction, PFC, S2 cost
acceptance or S3 qualification. No semantic blocker found in this offline pilot.

## Proposed API, not installed core attrs

Keep actual signature and CFG:

```rust
unsafe fn bidirectional_merge<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &[T], dst: *mut T, is_less: &mut F,
)
```

Only the closed `u8` / existing `sorting_model::KeyLess<u8>` pair gets this
semantic leaf. No generic trait bound/Copy premise is added. Proposed pure,
verification-only API (names/types below are design, not compiled Rust):

```
MergeSnapshot { values: [u8;32], len: usize }       // owned initialized snapshot
MergeGhost { low_l:i, low_r:j, high_l:a, high_r:b,
             low_written:x, high_written:y }      // arithmetic natural counters
merge_snapshot_u8(v: &[u8]) -> MergeSnapshot        // pre: 2<=len<=32
merge_pre_u8(v: &[u8], dst: *mut u8) -> bool        // halves sorted + memory gates
merge_rank(before: &MergeSnapshot, p: usize) -> usize // p<len
merge_inv_u8(before, src, dst0, ghost) -> bool       // G/F/O/E/M/A, guarded loads
merge_post_u8(before, src, dst0) -> bool            // init/order/full counts/frame
```

At actual paired heads x=y=k; after up x=k+1,y=k; after down x=y=k+1;
after odd x=h+1,y=h. Destination original pointer must survive shadowing.
Ghost counters update from the **actual** `is_l` outcomes, with no assumed
extremum choice. Inline up/down or prove their exact helper bodies with the
asymmetric pre/post before any summary substitution. A proof for only the
existing safety/frame contract does not supply this API's semantic theorem.

Proposed attrs only: guarded active-pair requires/ensures, existing exact
destination modifies footprint, loop invariant G/F/O/E/M/A and simple variant
remaining_pairs=h-k if supported/tested on the pinned tool. All predicates must
short-circuit validity/init/range checks before loads. No attributes are added
here, no assumed summaries or ord-panic stub. Rank arithmetic/witnesses must be
proved via bounded pure formulas; keep default safety checks and false-invariant,
false-decrease/havoc controls. Additional snapshot/rank formulas are ghosts over
the unchanged byte model, never a new trusted model or runtime order.

## Exact geometry needed by later callers

Offsets below are element offsets (u8 size/alignment1). For same allocation of
capacity A: `s+n<=A`, `d+n<=A`, `[s,s+n)` disjoint `[d,d+n)`; initialization
of all source slots and write permission for all destination slots are separate
preconditions. Address inequality is insufficient. The theorem should be
offset-parametric or have separately proved concrete instantiations.

| route | source region | destination region | required domain |
| --- | --- | --- | --- |
| standalone merge32 cost/reference | initialized `[u8;32]`, offset0 | separate `[MaybeUninit<u8>;32]`, offset0 | n32, sorted16/16 halves |
| general final merge | scratch `[0,N)` | separate v `[0,N)` | 2<=N<=32; caller scratch capacity>=N+16; preserve scratch and extra tail |
| sort8, first half | scratch `[N,N+8)` | same scratch `[0,8)` | N=16..32; allocation capacity>=N+16 |
| sort8, second half | scratch `[N+8,N+16)` | same scratch `[floor(N/2),floor(N/2)+8)` | N=16..32; same capacity |
| network final merge | v `[0,N)` | separate stack scratch `[0,N)` | 18<=N<=32; subsequent copy-back separate obligation |

The sort8 rows yield exactly34 distinct `(src_offset,dst_offset)` pairs at
n8: for each N=16..32, `(N,0)` and `(N+8,floor(N/2))`. All pairs are disjoint;
caller must prove initialization from its actual sort4 calls. Separate arrays
alone do not qualify these same-allocation instantiations. Python write-frame
tests check modeled slots only; they do not prove these pointer topologies.
No larger scratch or source domain is implicitly qualified.

## Validation, next integration and accounting

Reproduce the diagnostic receipt from g0 (read-only source Git objects):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/challenge-8/kani-k1/kani3300/ch8-s2/merge-pilot/test_pilot.py --source-repo /root/verify-rust-std-ch8-s1-08-w13
```

The source checker uses the pinned Git object, not mutable source HEAD; 30
line checks plus tree/blob/SHA256 detect mapping drift. This is textual binding,
not AST/MIR/callee proof binding. Future integration should review any delta
from99e and prove K0–K8 in separately authorized workflow. Independent review
belongs to that future committed candidate; no subagents were used here.

Offline cost0, dispatch0, push0; ledger/reservations unchanged. INPUTS budget
reference: item2 used9/cap14, prospective accepted S2 run10, one future workflow;
harness600s, compile900s, groupRSS12GiB with2GiB headroom, phase8100s/job10800s,
preferred serial1, measured single-root aggregate target<=6GiB. These are
references, not a reservation or dispatch GO. No timing/RSS extrapolation from
the Python run. W13's independent batch is unaffected and need not wait.
