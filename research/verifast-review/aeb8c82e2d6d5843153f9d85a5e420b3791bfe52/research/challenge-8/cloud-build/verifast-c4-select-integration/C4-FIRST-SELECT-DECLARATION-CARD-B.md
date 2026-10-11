# C4 first-selector local declaration admission card B

2026-10-10. Design proposal only; no declaration-admission implementation or proof run is included here.

## Evidence and diagnosis

The exact admitted input pre-AST remains SHA-256 `0ed31137cf55a2ed47ed624a6c61591e4aaf96371df3c2979fc10ce8d95bb222`. The fresh saved pre-AST at `/tmp/verifast-compose2-2669cf81-direct/allprooflogs/cases/integration/composition-fixture/actual-c4-bound-pre-ast.ml` establishes the source-local declaration sequence and types:

- declaration-list index 167 is `min`;
- index 168 is `$_171`, with `ManifestTypeExpr(..., Bool)`;
- indices 169 and 170 are `$_172` and `$_173`, each `PtrTypeExpr(..., IdentTypeExpr(..., None, "T"))`;
- indices 190–195 are six later call temporaries, separate from these first-select locals.

All four locals `min`, `$_171`, `$_172`, and `$_173` are uninitialized and not address-taken. `$_171` is the bool condition local, not a pointer argument. The refusal `SORT4-C4-BOUND: local declaration $_171` is caused by the first-select admission checking declaration-list entries 190–192 for `$_171`–`$_173`; those entries are later temporaries. This is an exact-index bookkeeping error, not a source, pre-AST, or proof failure.

## Minimal correction for review

For the first-select mode, check `min` at root index 167 and `$_171`, `$_172`, `$_173` at indices 168–170. Add exact type checks: `$_171` must have the observed manifest bool type; `$_172` and `$_173` must have the observed pointer-to-`T` type. Keep the no-initializer/not-taken checks and the separate once-only declaration checks.

Set the future-local exclusion inventory to indices 190–195 in both C4-bound modes. Those are the six suffix temporaries already removed by the original C4 prefix projection; they are not the first-selector locals. This retains the same 184-declaration inventory as the original C4 bound projection and preserves all source declarations needed for the checked first selector. Keep the existing call/type/operand/edge shape matcher and exact source/MIR/pre-AST pins unchanged.

## Invariants and limits

This is a correction to source-derived local-index admission only. It must not alter the parsed AST, runtime code, generic signature, C4 contract/posts, current owner resources, call target, CFG, unwind routes, selector export, or kernel. Any mismatch in the four names, their exact types, initializer/address state, or pinned pre-AST remains a pre-proof refusal. The tool logs the fixed inventory and AST SHA; the next fresh Cloud run must show all nine imported bodies and C4 pass before composition results are considered.

Independent review is required before implementation. No proof status follows from this bookkeeping repair; a fresh run on the changed tool is required.
