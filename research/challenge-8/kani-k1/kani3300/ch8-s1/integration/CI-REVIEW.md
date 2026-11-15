# Frozen S1 CI package review

## Decision: GO for coordinator review/pre-dispatch preparation

Static review only; no workflow, Kani, build, or proof was run. The reviewed
production export is std `75a4d1ea6eb60c63c27c1b18e662740d93bafb08`, tree
`6d1b90bc11440762c9b65889fc538ba3071b0d9d`; stock Kani is
`0aac16ef62da9e9d5645782d458593e5d78143ba`, tree
`9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`. The refreshed CI-only overlay is
tree `e9137511d22abf8993ecc8708dd8c5c527aaac53`, patch SHA256
`debff93371d9b69962cdf6b3e96f2aa78939786d5e4d90bed8d226d6c023fb21`, and
request SHA256 `b186c533712383d485cf85419eb4999fd19fe93391d7d178b6fd2db7840cc066`.
Local file hashes match the overlay/request declarations, including workflow
`04f30dcf7f3bbdbcba377993b6f1f91e5526a3d481e4dfca1fb98b1584e8c869`, checker
`ca84de9934b89eba4ad4dcee89498616c86e1ec6280e5b86ecd8a28466ab8ad9`, runner
`b4a6541f11aa9ea0990a4bd9c1939b1cae4fddd9e6248fbc20e59db3d406f786`, and
tests `99332ebca71669c53fc66463399231d1abeb0b1f6960ca6fe1096ae1347fe675`.

Static checks passed for the reviewed package:

- Workflow triggers only on `push` to `uninit-ci/ch8-s1-*`, and the job is
  guarded to the named upstream repository and push event. It has read-only
  contents permission, one Ubuntu 24.04 job, serial matrix, and a 120-minute
  job cap. Every step now has an explicit timeout. The setup epoch starts at
  the first step; pre-build step caps total 28 minutes and `check_package.py`
  limits the build to the remainder of the absolute 30-minute setup window.
  The verifier/list step is capped at 75 minutes; fallback and upload reserve
  15 minutes.
- Checkout depth is at least two, credentials are not persisted, and the
  control/export/tool checkouts are siblings. The control overlay alone removes
  ordinary workflows; the source export and stock tool remain pinned intact.
  Source/tree/changed-file identities are checked before and after rows.
- The exact argv preserves the requested `-Z` ordering before `--cbmc-args`,
  `--no-assert-contracts`, object bits 12, sorting/control cfgs, stock tool pin,
  and default solver/check settings. The runner binds schema 0.1.0, exact root
  selection, PFC mode/target metadata, checks/covers completeness, tool identity,
  and caps; timeout, signal, output/RSS cap, unsupported output, or source drift
  yields UNKNOWN/STOP. Negative rows retain original exit/signal and require
  the named failed property. Receipts keep proof credit pending review.
- The request contains 23 rows, all NOT_RUN: six distinct production PFC smoke
  selectors, 12 model controls, two legal attachment companions, two isolated
  false-ensures variants, and one ordinary bridge. The activation patches each
  change only one intended ensures clause and are hash-bound, applied separately,
  and reverted. Full 600-second row caps are retained; the runner starts a row
  only when its whole cap plus cleanup margin fits the remaining 75-minute phase.
  Planned work is 2,760 seconds plus the separately estimated list time; this
  is not a runtime guarantee. Group RSS is sampled at 50ms and documented as a
  sampled bound, not an exact kernel high-water measurement.
- Successful check names are unavailable in stock export 0.1. The runner
  therefore reports counts and an explicit `REVIEW_REQUIRED` source-assertion
  binding instead of inventing successful property IDs. This and the actual
  `contract_binding` output must be reviewed before assigning any P1 credit.

## Review gates before any later proof credit

The PFC binding now matches the stock compiler schema. Kani 0aac's
`kani_middle::metadata::gen_contracts_metadata` stores the crate-relative
pretty target name in `ProofForContract.target_fn`
([metadata.rs:82-95, 147-155](/root/kani-upstream-ch8-s1/kani-compiler/src/kani_middle/metadata.rs:82)). Separately,
`AssignsContract.contracted_function_name` is `modify.mangled_name()` for the
generated modifies/check wrapper ([contract.rs:32-52](/root/kani-upstream-ch8-s1/kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs:32)).
The runner requires `ProofForContract.target_fn` to equal the exact list
contract target, requires a nonempty `contracted_function_name`, and records
the latter separately with `contract_wrapper_correlation: PENDING_REVIEW`.
That correctly avoids comparing a mangled wrapper name to a pretty function
name. These fields and the successful source-assertion binding remain for
human review; list/export names are still NOT_RUN.

The control preflight now verifies that `rev-list --parents -n1 HEAD` contains
exactly the control SHA and pinned production SHA, in addition to changed-path
and payload checks. The YAML checker is intentionally local-only; the workflow
payload is hash-bound and was checked statically here. No unresolved package
blocker remains in the reviewed scope.

The parent agent reports six targeted package/export tests passed after the
schema correction; this reviewer did not run them. Dispatch count, cost, proof
credit, P1 acceptance, and final selection remain with the coordinator/reviewer.
No dispatch or Cloud spend was performed here.
