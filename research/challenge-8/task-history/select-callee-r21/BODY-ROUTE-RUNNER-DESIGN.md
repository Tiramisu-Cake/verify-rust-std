# R21 actual-body transport lane

## Defect and applicability

The R20 callee lane intentionally ends at the nine-body `select_unpredictable`
diagnostic and has no actual sort4 body transport. Reusing its lane/phase would
admit a different action under historical identity. R21 needs an isolated body
lane that builds the frozen O26 base (`vf_mir_translator.ml` SHA-256
`0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a`), then
calls the separately pinned R21 entry adapter. The branch-selected translator
patch belongs to the callee certificate refresh and is deliberately absent:
the body reconstructor starts from the unrefreshed O26 base.

## Invariants

- Require lane `o26-sort4-body-r21`, phase marker
  `SORT4_R21_BODY_PHASE_ID=SORT4-ACTUAL-SELECT-2026-10-23-R21`, Cloud provider,
  exact proof/infra checkout heads, fresh profile SHA, and the R21 profile's
  separate R17 backend protocol identities.
- Refuse GitHub Actions, legacy recovery/callee opt-ins, ambient A1 summary or
  admission markers, and any profile or dependency pin mismatch.
- Preserve the R20 O26 setup pins, source/tool/schema/compiler/dependency
  identities, initial console build at base `0862e635…`, stock-binary
  preservation hashes, and Cloud provider checks.
- Keep `allprooflogs` exclusive and create it before evidence writes. Preserve
  the first failing stage and original runner exit/exception in the final
  audit. A successful process exit never implies proof acceptance.
- The audit always reports `accepted=false` and `proof_credit=false`; missing,
  null, wrong-type, partial, and explicit `NOT_RUN` body diagnostics remain
  distinguishable.

## Controls

The route audit has small isolated tests for success-shaped diagnostics,
nonzero/error and timeout exits, missing/null/wrong-type/partial/`NOT_RUN`
diagnostics, and profile/source/route mismatches. These are transport and
classification controls only. Shell syntax and an early wrong-environment
refusal are checked without running setup, extraction, compilation, export,
reconstruction, verification, or Cloud services.
