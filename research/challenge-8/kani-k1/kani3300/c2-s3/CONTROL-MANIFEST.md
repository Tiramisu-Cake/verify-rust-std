# S3 controls — provisional, NOT_RUN

Exact per-file hashes/blobs and flags are in CONTROL-MANIFEST.json and INPUTS.json.
Each file has one harness. All normal checks remain enabled; object-bits is 12
per fixture, with no global override and no cover-summary ambiguity.

| File | Intended observation |
| --- | --- |
| repeated-destination.rs | One local destination is seeded initialized, then receives two nested calls, second with a payload hole. Target read is its payload after second return. Baseline must falsely succeed. |
| moved-from-source.rs | Saved pointer into a field-assembled, live source precedes actual Call(Move(source)); target read uses that old address. Baseline must falsely succeed. |
| reinit-companion.rs | Real slot writes after destination reset and after source Move must permit legal payload readback; zero failed properties. |

The two negative goldens pin `** 1 of` plus the exact intended u8 uninitialized
read description and failed single-harness verdict. This is a provisional
one-property source oracle, not an observed count. No host/std lines or full
inventory is pinned. Actual emitted duplicates/counts are UNKNOWN. If local and
delayed checks duplicate the same read, record each source binding and the exact
count for review; do not accept arbitrary failures or auto-bless a golden.
Unsupported, frame, validity, dangling/StorageDead and unrelated read failures
cannot satisfy the intended oracle. The legal companion's own assertions check
the repaired payload values.

`Nested` is repr(C), non-Copy, with a MaybeUninit<u8> payload followed by u8 marker.
Expected extent is 2, alignment 1, payload offset 0/extent 1. These are source
layout expectations; actual consumed-MIR object/field/Call/read binding remains
UNKNOWN until coordinator execution. Custom MIR is runtime/optimized to preserve
the explicit Call destination and Move operand. Whole aggregates are assembled
and returned by fields. A saved source pointer outlives the Move but source
storage is not explicitly killed; the target is not a temporary/callee object.

Existing top-level Move/return/legal/reinit/false/Copy/MU argument-return,
pairing, normal/abort, ordinary/PFC, closure/cycle, immutable and S2 controls stay
byte-identical. The known tuple legal fixture remains a known false positive.
Any drift in its failure count needs review; it is not detection-of-UB credit.
