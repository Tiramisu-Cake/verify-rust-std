# R13 runner partial-progress snapshot design

## Observed fault

R12 S3 (`173f94ec-e862-42ce-b2c1-ae729cb079c9`) and S4 (`fbc0834a-760b-4f56-98fe-952714f36c6d`) both ended with source-reported exit 124. Their Briefs report `last completed stage=UNKNOWN`; neither supports a causal-stage claim. The bounded catalogue identifies each retained `a1-lifecycle-progress.json` as about 25.7 MB and `JSON_EXCEEDS_SCAN_LIMIT`, beyond the reader's 16 MiB structural JSON limit. The small retained `stage-progress.json` reports only `a1-off-observation` / `verification` / exit 1 and does not identify the final lifecycle stage.

The runner currently writes lifecycle progress directly to its final path. Its final `diagnostic-audit.json` is written only after the matrix loop and result assembly (apart from an explicit tool-reconstruction early return). The recovery wrapper copies only `diagnostic-audit.json` to the package proof audit. When timeout or an uncaught exception interrupts before final audit publication, the wrapper therefore has no runner snapshot to package and the outer trap creates a generic audit. Existing progress data is neither compact enough for bounded review nor safely atomically replaced.

## Design and invariants

After every completed case or observed stage, publish an atomically replaced compact snapshot to both the local progress path and `diagnostic-audit.json`. The latter is the existing wrapper's package input, so timeout and exception exits retain the last complete snapshot without changing wrapper or coordinator behavior. The normal final audit remains the authoritative complete report and replaces the partial snapshot after it is fully assembled.

The partial format contains only identity pins, compact per-case status/reason/stage facts, and explicit non-admission flags. It omits raw observation payloads, MIR/AST, logs, artifacts, and parser structures. Build, proof-source, infrastructure, profile, phase, and tool identities are copied only when available from runner records. The last stage is copied only from an explicit `stage_observed` event. `NOT_RUN` is emitted only for a matching explicit `not_run` event; missing rows remain `UNKNOWN`, and started/failed/partial rows remain `INCONCLUSIVE` with `proof_credit=false`.

Every partial snapshot is marked `partial=true` and fails closed: `accepted`, `proof_credit`, matrix admission, and diagnostic/evidence completeness are false. Missing, null, and wrong-typed optional values remain distinguishable through absent/null values and never gain a status by inference. Atomic replacement uses a same-directory temporary file and `os.replace`; no incomplete temporary file is selected by the packager.

## Validation boundary

Use isolated synthetic Python tests for successful snapshot, stage/case error, timeout-derived explicit not-run, partial observations, missing/null/wrong-type fields, atomic-write failure, and packaging when the runner exits before final audit. Tests import the runner only and do not invoke source preparation, compilation, parser, or verifier. These tests establish serialization and packaging behavior only; they do not establish any proof result or Cloud runtime timing.
