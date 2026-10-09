# O26 shadow-binding source capture (blocked diagnostic)

## Problem and rule

The 93da48d0 Cloud capture fixed the input-relation candidate source at
`a95aff14592b167c62c53c7ed726128ee86c7c19768cfe613504cdec841f8463`.
The three late assertions referring to Rust's shadowed `true_val` and
`false_val` may need the exporter names `true_val_1` and `false_val_1`.
This is a falsifiable source-annotation hypothesis, not a new proof rule.
The R3 proof outcome must identify the actual failure before this case is
activated.

The blocked preparer starts with the exact captured nine-body input-relation
source pair and substitutes only those three late ghost comments. Its reviewed
JSON gate must pin the parent source SHA and agree on both NORMAL and readonly
internal names. The two input bindings, two payload assertions and two current
wrapper assertions remain unchanged: nine individual ghost commands in three
regions. The three substitutions must reverse byte-for-byte to the parent;
ghost stripping must yield the exact original runtime source. The actual
function order and three intrinsic calls, one `forget`, and one `assume_init`
stay fixed. No source runtime, signature, postcondition, ownership resource,
parser, translator, spec, kernel, memory model, exporter or refiner changes.

## Capture and refusal

The separate Cloud lane is default-off and source-only. It requires paired
NORMAL and readonly MIR, refinement, nine complete decoded bodies, and ten
independently hashed Marshal snapshots. The eight bodies outside the outer
function must match the reviewed 93da48d0 capture exactly. The fingerprint
probe's explicit no-proof-rule refusal is a collector result only; it is not
an owner-17 or equality negative. A mismatch, setup error, incomplete dump,
or premature proof claim is inconclusive. No verifier certificate admits the
new source; component 17, A1, callee proof, normal/unwind resources and
mutation controls remain required before any future profile can be accepted.
`verification_accepted` remains false.

The draft JSON deliberately says `BLOCKED_AWAITING_FRESH_INPUT_RELATION_CAPTURE`.
Only the root reviewer may replace it after the actual R3 failure and exact
fresh source/MIR evidence are reviewed. The Cloud lane refuses while blocked.
