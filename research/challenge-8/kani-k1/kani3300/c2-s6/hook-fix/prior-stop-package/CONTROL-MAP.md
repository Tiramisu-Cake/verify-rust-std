# C2-S6 control map — pre-edit source investigation

All outcomes below are intended or source-derived; native execution NOT_RUN.
No missing row is waived. Do not interpret candidate selection as actual MIR evidence.

| Required path | Existing binding / gap | Minimal proposed selector and oracle |
| --- | --- | --- |
| Backend hook shadow argument | Existing bodyless/extern controls do not select backend hook. Inspect marker/ABI and legal generated path. | Pending legal hook candidate; protocol Unsupported (not arbitrary FAIL); bodyful direct companion required. |
| Backend hook shadow return | c1p COMPILER-CONTROLS §7 is historical UNKNOWN, not observed repro. Candidate generated PFC/modifies UntrackedDeref. | Pending legal generated call binding; paired-transfer refusal with actual shadow return. |
| Copy same source into two argument indices | maybe-uninit-call-move/main.rs copy_call has one argument; maybe-uninit-call-pairing/main.rs uses different values. Neither covers same-place duplication. | New copy-source-arguments: explicit custom MIR Call Copy(source), Copy(source), each selected hole read; initialized/source-preservation companion. |
| Free FnDef through Fn trait, no shadow | unresolved-calls/fn-trait-pointer-{plain,seeded} explicitly takes fn pointer and reaches FnPtr; closure tests are not FnDef. | New free Fn-item selector only if actual shim/layout established; outcome source-backed, not assumed blanket Unsupported. |
| Free FnDef through Fn trait, shadow | Same gap. Avoid MaybeUninit argument tuple (UnionAsField would not discriminate). | New Fn-item shadow-return selector if actual shim/protocol established, initialized direct companion. |
| Forced coerced function pointer | unresolved-calls/fn-trait-pointer-plain.rs indirect(f: fn(u8)->u8), Fn::call(&f,(42,)). Seeded companion exists. | Reuse existing selectors and exact FnPtr Unsupported; do not duplicate. |
| Padded partial extent borrowed slice | maybe-uninit-typed-array-partial-data/main.rs is typed array transfer, not borrowed slice. part1-edges/dst-by-reference uses byte slots, not padded stride. | New padded-slice-extents borrowed partial-hole / initialized pair; actual layout asserted, prefix crosses slot boundary and final payload byte remains hole. |
| Padded partial extent raw slice | Same existing gap; raw field tests are not raw fat slice. | New raw-fat-slice partial-hole / initialized pair, actual stride and data offset witness. |
| Coalescing, nested resets, journal/scope | Reuse S2 immutable-descriptor-coalescing; S3 nested-aggregate-reset; S4 compiler units delayed_cache6/delayed_scope2 and S2 registration9. | Existing selectors/units unchanged; no mixed JSON restored. |

Detailed source bindings/counts will be recorded before final source acceptance. Missing actual call identity or non-discriminating setup requires STOP with repro.

## STOP disposition

Backend generated PFC/modifies attempts are NONDISCRIMINATING/UNKNOWN: valid pointer
shape is not a shadow return, MU shape is ill-typed. See REPRO.md. Explicit ordinary
hook and free FnDef candidates remain diagnostic-only; actual call identity/count
UNKNOWN. Copy/padded drafts moved to research and are not exported controls. No row
closed by omission and no native result claimed.
