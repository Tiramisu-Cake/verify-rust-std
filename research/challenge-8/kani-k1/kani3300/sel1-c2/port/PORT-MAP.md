# SEL1 net delta → final C2 port

Inputs and exact identities: `INPUTS.json`. Old coordinates refer to the result side
of `69b13711e..39a6521bf1`; new coordinates refer to source `14bc57fdb99960240c4944845a3d985c8af4dcf7`.
Complete old and new patches: `SEL1-NET.patch`, `source.patch`. No old C2 history was replayed.

| File / old hunk | New location | Port decision / retained C2 behavior |
| --- | --- | --- |
| statement.rs: remove local FnDef match near 925; predicate at 928 | Same two hunks, predicate 928 | Exact net delta; shared fallback decision, no backend result/shadow copy. |
| kani_middle/mod.rs:153–199 | Same 153–199 | Exact two helpers, core definition identity, usable body and `(bool,T,T)->T` classifier. |
| points_to_analysis.rs:373–384 | Same 373–384 | Exact intrinsic guard; existing current regular-call helper, selected-body overrides and cycle handling retained. |
| reachability.rs: remove local match near 282; predicate at 285 | Same two hunks, predicate 285 | Exact net delta, same predicate as codegen. |
| uninit_visitor.rs:19 import | 19–22 | Combine select classifier import with C2 `KaniFunction`; neither owner removed. |
| visitor:65–75 entry validation | 68–78 | Exact insertion, before entry transfer emission. |
| visitor:84 intrinsic entry exception | 87 | Only validated select may use the pre-existing entry protocol. |
| visitor:99 entry protocol call | 102 | Add tcx to shared predicate; current argument numbering/count unchanged. |
| visitor:146–205 validation + store helpers | 182–241 | Insert after intact F6 `needs_nested_call_reset` / `reset_nested_call`, rather than replacing them. |
| visitor:590–610 call admission/pairing | 626–646 | Exact select validation/type checks; current Call pattern retains `target` for F6. |
| visitor:648–650 store helper invocation | 684–686 | Once for paired calls; before intrinsic/item dispatch and before current F6 resets. |
| visitor:652–654 admitted Intrinsic arm | 688–690 | Ordinary fallback owns selected state; all other intrinsic models/refusals retained, including C2 BlackBox reset. |
| visitor:811 item/shim comment | Current item/shim comment retained | C2 “shared protocol predicate” wording already expresses the new predicate; no semantic hunk omitted. |
| visitor: old item-only stores removed after old 836 | Deletion at C2 old 781–814 / new 878 | Same extraction; current F6 reset immediately after the item/shim branch remains. |
| visitor:877–879 return predicate | 923–925 | Same tcx and validated-select extension; mandatory slot0 Store still normal Return only. |
| visitor:1254–1262 protocol + name helper | 1300–1313 | Combine SEL1 signature/helper with final C2 hook exclusion. Ordinary Item conjunction keeps `!Hook`; only exact intrinsic classifier adds a second disjunct. |
| 65 fixture files, 12 groups | Same paths | Byte-identical to 39a6521bf1, including its Nested/UnionAsField golden correction. Per-file identities: `FILES.json`. |
| No old docs hunk | rust-feature-support.md:195–204 | Narrow replacement of blanket select refusal by sized/layout/mask/fallback boundary. Other C2 limits, #5104 scope and no all-SmallSort claim retained. |

`git apply --3way` applied the first four production files and fixtures directly.
Its four conflict regions were confined to the visitor import, adjacent F6/SEL1
helpers, item/shim comment and protocol predicate. Resolution keeps both sets of
helpers, the C2 comment and the hook exclusion. No whole C2 file was replaced.

All five files introduced/changed by final F7 remain byte-identical to C2, including
DelayedUbPass and both `replace_delayed_body` writers. Every pre-existing visitor
function except the three planned entry/call/protocol functions has an identical
token body; original C2 tests and all paths outside the authorized scope are unchanged.
See `VALIDATION.json`, `COMPILE-SEAMS.md` and `REVIEW.md` for scope and limits.
