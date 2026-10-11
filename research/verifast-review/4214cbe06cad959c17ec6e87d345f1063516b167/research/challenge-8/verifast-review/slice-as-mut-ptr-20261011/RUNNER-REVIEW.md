# Independent static review of the slice-binding Cloud runner

## Final targeted re-review at `8db639fa08741dcabfa2558804169a5cea27276c`

**GO for a bounded, unaccepted Cloud candidate diagnostic after the
separately ongoing payload size/identity preflight.** The two blockers in the
`d7ff687c` review below are addressed:

- `source-input.py::restore_archive` explicitly hashes the bytes inside the
  outer gzip as `payload_bytes`. This preserves the former certificate digest
  for all JSON lanes; I labels its inner packed XZ encoding separately.
  The I-only pack still restores original object bytes through the existing
  OID/type/size and committed path/tree checks. Other lane encoding paths
  remain unchanged. Static Python parsing and `bash -n` passed; the separate
  payload transport/size measurement has not yet been reviewed here.
- `runner.py::audit` now labels successful slices/native/selector/C4/
  composition as `SCOPED_COMPONENT_EVIDENCE_RAW_REVIEW_PENDING`, records
  `scoped_components_complete` and the integration's separate completion
  fields, and keeps overall `diagnostic_complete=false`. Integration exit 1
  therefore cannot be mistaken for full regression completion or model
  acceptance. Exact six slice gates, three source-admission refusals, same
  console digest and native C1/C4/ZST groups remain required. The audit
  retains typed false acceptance fields and profile I.

The historical base-tool absence of the method is not a fresh default-off
gate for the unconditional one-symbol binding. New-profile evidence requires
the six fresh slice cases, three source controls, and the listed native/Bool
matrices on the same compiled tool. No actual caller or public ZST guard
result is claimed. This review does not accept the profile or transfer old
proof credit; raw Cloud outcomes and their exact first obligations still
require independent review. No compiler, verifier, proof module import or
Cloud dispatch was run locally (`NOT_RUN`).

## Intermediate re-review at `d7ff687c0f439c8b16e8d6f7830fce5aa7238080`

**BLOCK Cloud dispatch on two remaining transport/audit defects.** The
three findings below were against `f94bcf91`; the worker's subsequent
changes address their local causes as follows:

- The final audit now checks the exact six slice cases, each gate's Boolean,
  all three source-admission refusals, the native C1/C4/ZST case groups,
  matching `bin/verifast` digest, and zero slice/native exits. It writes typed
  `accepted=false`, `verification_accepted=false`, `profile_accepted=false`
  and `diagnostic_complete`. This closes the former exit-only slice verdict
  and missing-typed-fields defects.
- Before package installation or console build, `source_prepare` imports the
  pinned C4 helper and its capture dependency; the earlier integration
  `source_prepare` imports its own helpers. This closes the identified
  post-build import availability gap. The narrowed I lane prepares six exact
  binding fixtures, not the unfiltered helper/public-guard fixtures; those
  belong to the proof-owner mission and receive no credit here.
- The packed source transport is I-lane-specific in `source-input.py`.
  `make_payload` concatenates original Git-object bytes with sorted OID
  metadata and XZ+gzip encodes them. `decode_payload` requires exact I lane,
  shared schema, bounded metadata/stream, contiguous offsets and lengths,
  then restores base64 object bytes. The existing restore path still checks
  each object's Git OID/type/size, path/mode, commit/tree closure and exact
  recipe path sets. Other lanes retain the previous gzip-JSON encoding.

**Remaining blocker 1 — restore certificate crashes for every lane.**
`source-input.py::restore_archive` now assigns only
`payload = decode_payload(compressed)`, but its certificate still computes
`hashlib.sha256(raw).hexdigest()`; `raw` is undefined in that function. The
failure occurs after repository restoration and before the Cloud entrypoint.
Define the payload bytes used for this certificate and preserve the previous
digest meaning for legacy lanes; for I, state what bytes the digest covers.
Recheck restore through a static/synthetic transport control before dispatch.

**Remaining blocker 2 — combined audit can overstate integration completion.**
`runner.py::audit` sets `integration_ok` from only three positive flags and
accepts integration exit 1. It does not require the integration result's
`diagnostic_complete`, affected regression gates or composition controls.
It can therefore write `diagnostic_complete=true` and
`FRESH_COMPONENT_EVIDENCE_RAW_REVIEW_REQUIRED` while full integration gates
failed. Either require the exact complete integration result and exit 0 for
this completion claim, or explicitly classify the result as partial component
diagnostics with full integration incomplete. Keep source/admission/negative
raw evidence and the separate unaccepted profile status.

No compiler, verifier, proof runner, proof module import or Cloud dispatch was
run in this re-review (`NOT_RUN`). The original `f94bcf91` findings below are
retained as historical review context; its ten-fixture scope was narrowed in
`d7ff687c`.

## Original review at `f94bcf91aa2633d677645ca4e90d316602c67f97`

Reviewed proof/infra head `f94bcf91aa2633d677645ca4e90d316602c67f97`,
tool candidate `b6cb276afd13107c2a90ca50acbb12ff0a992dd8`, and the
`verifast-slice-binding-integration` recipe before Cloud dispatch. **BLOCK
dispatch until the three localized issues below are corrected and statically
rechecked.** This is a runner/admission review, not a proof result; compiler,
verifier, extractor, proof module imports and Cloud dispatch were NOT_RUN.

1. `runner.py::audit` currently treats three zero process exits as a completed
   combined diagnostic. `runner.py::run` can exit zero after writing
   `all_expected_observed=false` and
   `SLICE_BINDING_FIRST_OBLIGATION_OPEN` when an intended assertion or positive
   is wrong. Require the slice result's exact six-case set, all six
   `gate_passed=true`, `all_expected_observed=true`, expected slice
   classification and source-admission refusals. Also require the integration
   result's `diagnostic_complete=true` and native result's exact complete
   classification, with matching profile/tool identity. Otherwise the final
   audit must remain incomplete, even when runners returned zero.
2. The final `proof-audit.json` written by this same `audit` lacks typed
   `accepted` and `verification_accepted` booleans and a
   `diagnostic_complete` field. The earlier `a125db66` archive was rejected
   for a missing typed `accepted` despite process exit zero. Emit explicit
   `accepted=false`, `verification_accepted=false`,
   `profile_accepted=false`, and `diagnostic_complete` computed from the
   checked gates; keep raw review and consumer proof status separate.
3. `runner.py::run` imports the C4 verification helper and the integration
   driver only after stock download, dependency installation and console
   build. Their import/dependency availability is a prerequisite for the
   recipe, so add an inert pre-expensive import/dependency check. The import
   must not execute proof work or source extraction. This is a setup gate;
   it does not replace source preparation or verification.

The rest of the source path is appropriately ordered. `run.sh` materializes
the full pinned slice source before package installation; `materialize_slice`
checks compressed SHA, bounded XZ length, raw SHA, and the committed Git blob.
The C4 input preflight similarly restores the raw patch and all 30 source
modules from compressed delivery, checks raw hashes and committed Git objects,
then runs C4, native and slice source preparation before the console build.
The slice preparation uses the pinned `source_certificate`, admits three
source-mutation refusals, and generates all ten fixtures, including the six
binding cases and the unfiltered helper/public-guard diagnostics. Local file
SHA-256 values match the manifest for slice, SmallSort, unstable public
entry, `SizedTypeProperties`, the case template and all three compressed
deliveries. This source preparation is not a verified result.

After the single combined tool build, the recipe intends fresh same-tool
canonical generic/MU cases, the native pointer consumer and three intended
negatives; native C1/C4/ZST and nine C4 controls; C/C++ controls with
`-shared`; selector nine-body proof, C4 and first-select composition, and
affected regressions. `runner.py::run` currently exercises only the six slice
cases; the unfiltered actual helper and public-guard fixtures are prepared but
not verified in this maintainer lane. That is consistent with the explicitly
separate proof-owner actual-caller mission and gives no caller/nonzero proof
credit. Historical default-off and O26 results are not fresh results on
`b6cb276` and must be marked as such. Retain all raw logs, precise first VC,
source/tool/profile pins and `profile_accepted=false` after the three fixes.
