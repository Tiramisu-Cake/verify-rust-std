# R21 fractional-forget fingerprint helper

## Defect and applicability

The R21 owner-approved fractional-forget candidate has eight source variants,
but the existing R20 fingerprint command handles only one older repair and is
bound to the R20 phase marker. A fresh R21 Cloud-only `MODE=fingerprint`
helper is needed to run the eight exact variants through normal MIR export,
Cap'n Proto decode, and the existing mode-9 refusal fingerprint. It records
source/MIR identities and failure states; it does not run the body proof or
activate a new proof rule or certificate.

## Invariants

- Require exact Cloud provider and the reviewed R21 value in
  `SORT4_R20_CALLEE_PHASE_ID`, reject GitHub Actions,
  the old R20 final-select opt-in, and every R21 fractional-forget opt-in.
- Pin the owner-projection base verified source SHA-256
  `1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6`, the
  original source SHA-256
  `466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5`, the
  exact transform module, and the existing R20/O26 fingerprint dependencies.
- Preserve an unmodified base case and an exact copy of the original source in
  every variant case. Use the existing mode-9 refusal fingerprint with
  semantic gates disabled. Never invoke a proof stage or treat verifier exit
  status as acceptance.
- Write an incomplete checkpoint before external stages and after each stage;
  preserve original stage results, exits, snapshots, and exceptions. Missing,
  null, wrong-type, `NOT_RUN`, timeout, and source-stage mismatch remain
  explicit. Deadline shortfall leaves `complete=false` and returns nonzero.
- Always record `body_proof_run=false`, `accepted=false`, and
  `proof_credit=false`.

The helper pins the transform at SHA-256
`f7f8fdb9d9e6767741399b8716ff4d28cd388e6870e7d5d468c929a507d14fb2`, its R20
repair dependency at
`3646b05602b7dce35cd4b2ab8f74d8cfe280d65df2637ac4f6cc0a128dd7e2a3`, and its
controls dependency at
`533c3d9be5249a40b2f0ad701cfaff6e95e688ecfb5b9c024c5dd2a56dc5124d`. The
fingerprint path also pins the R20 observation helper
`83d2d0940fcb255a58b97db8d6161ec3b39660a62905f89a33f926a96d3099ba`, O26 recipe
`464eef45b08b8724eba949289eff9cd745f48d65d0031ffae5675738856d562c`, O26
refresh recipe
`2cd963cc3d28c69370260cd2154e7284e189fea953928c3fc829f2fd53766af3`, and
mode-9 capture source
`ffc3653263e86c5afa4f82440f10a2207e75ad8083bdad5f784597fe0dbaa84f`.

## Controls

Synthetic tests inject a fake transformer, exporter, capture module, and
snapshot writer. They cover a successful complete fingerprint batch, deadline
reserve, partial/missing/null/wrong-type/`NOT_RUN` records, source-stage
mismatch, exact verifier exit/argv/log targets, provider/phase/ambient-opt-in
refusals, and exception persistence and propagation. A public-entry test calls
`fingerprint()` while mocking pinned modules and checks that the full CLI
namespace survives. The bounded `audit` subcommand delegates to the pinned R20
audit, adds the incremental R21 record, and requires both audits to be
complete; missing, null, wrong-type, and partial R21 records remain explicit.
They do not invoke source preparation, actual extraction, exporter/compiler,
verifier, reconstruction, or Cloud services.
