# S5 independent static review — current staged candidate

Reviewed staged source in `/root/kani-fix-3300-c2-s5` at the coordinator-reported pre-deletion tree `5bdc6172c3a1ef23930be6b3ebb0a83982df7846`, including the false-Replace companion delta. No source edits, builds, compiler/verifier runs, CI, or pushes were performed. The three JSON suites remain present.

## Finding — fix contradictory per-row map text before deletion

`ORACLE-MAP.json` contains copied boilerplate that contradicts the row's own `new_exact_N`, `portable_oracles`, and candidate fixtures. At lines 1032–1033 and the following mode rows (1154, 1218, 1268, 1313, 1384), every mode is described as a cycle `Unsupported` with N=1 and as removing cycle-negative covers. That is wrong for `replace_transfer` (N=2 read failures), `replace_ordinary` / `replace_simple_check` (N=0 legal assertions and covers), and `recursive_simple_check` (N=0 bounded assertions and covers). The same shared text is on recursive check/ordinary rows but still misleadingly claims a positive companion oracle on the negative rows.

The composition rows repeat another conflicting template at lines 1455, 1534, 1624, 1708, 1794, 1919, and 2005: it says every root has two read failures and a cycle description/provenance block. This is false for all legal roots, the single immutable-hole read case has two read checks but no cycle, and only `cycle_root` needs the cycle diagnostic. These fields are part of the required per-root source/map explanation, so they should be rewritten to match each root's exact failures, useful successes, covers, and source-preservation notes before the map is treated as closed. The detailed `portable_oracles` in many rows are substantially more accurate, but do not resolve the contradictory top-level fields.

## Static checks and limits

- The staged portable fixtures appear split to one harness each, retain the stated source operations/contracts, use regular output and `--object-bits 12`, and use literal expected blocks with `SUMMARY` / exact `** N of`, status/description witnesses, verdict, and one-harness completion. I found no blank-only or regex-based goldens and no negative-root covers.
- The 21 old source case/root pointers are mapped. The full mixed-inventory equality/selector-order claim is explicitly dropped; S4 identities and the end-to-end coverage decrease are documented for coordinator acceptance.
- The updated `replace-transfer-uninitialized.rs` retains the original `input(false)` handoff and requires the post-return assertion plus the uninitialized-return cover. Its inventory hash matches the current file.
- All portable expected executions and all four native compiletest sensitivity overlays remain `NOT_RUN`; static inspection cannot establish that compiler output will match the new goldens or that the mutation overlays yield the predicted native verdict/count. Keep CI as a required acceptance step. `SENSITIVITY-MANIFEST.json` still names the base commit as `source_candidate`; update that identity to the final local source candidate/tree when it is committed.

**Disposition:** do not authorize suite deletion until the contradictory ORACLE-MAP row text is corrected. The exact-base observations support the mapped N values, but portable-candidate behavior and native sensitivity are still CI limitations.

## Follow-up review — corrected map and latest companion delta

Rechecked the corrected `ORACLE-MAP.json` against all 22 portable selectors/goldens. The stale cycle/read boilerplate is gone. I statically reconciled each row's exact summary count, Failed Checks list, required consecutive property blocks, and one-harness annotation against the candidate goldens: 22 inputs, 0 discrepancies. Per-root preservation text now matches the operations. The mixed-isolation limitation remains explicit.

One small metadata refresh remains for the latest robustness edit to `replace-transfer-uninitialized.rs`: the source now uses `let initialized: bool = kani::any(); kani::assume(!initialized);` before `input(initialized)`, avoiding a literal-false frontend constant-fold while restricting this companion to the same false partition. The row prose at `ORACLE-MAP.json:1361` still says “fixed-false” and `input(false)`; `MODE-COVER-MAP.md:21` also says “fixed-false.” Please describe this as a nondeterministic bool constrained by `kani::assume(!initialized)`. `FIXTURE-INVENTORY.json` still records the prior source hash `31a28abd…`; the current source hashes to `a3c05e39…`. Refresh that inventory hash (and any associated checksum file) after this edit. This is a metadata consistency issue, not a source-semantic blocker.

The assumed-false source keeps the original input constructor, Replace stub/helper/contracts, post-return assertion, and cover. The assertion is non-constant at source level; the assume restricts its domain to the uninitialized alternative. Its expected N=0 and cover reachability remain statically plausible, but native execution is still NOT_RUN and must be established in CI.

**Updated disposition:** the earlier map blocker is resolved. No remaining static source/map issue blocks suite deletion after refreshing the companion metadata. This does not qualify portable goldens or mutation sensitivity: all 22 native expected cases and all four compiletest sensitivity experiments remain CI acceptance requirements.
