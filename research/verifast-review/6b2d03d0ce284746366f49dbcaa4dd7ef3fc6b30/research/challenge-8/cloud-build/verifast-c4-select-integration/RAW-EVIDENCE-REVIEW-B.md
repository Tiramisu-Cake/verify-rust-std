# Build f7da71e8 raw-evidence review — 2026-10-10

Read-only independent review of the fresh B2 archive. This review classifies
the attempted run; it does not grant proof or intended-negative credit.

## Outcome

The build is a setup/integration failure before any verifier proof stage. The
archive reports `run_exit_code: 1`, `diagnostic_complete: false`, and
`verification_accepted: false`. `cases/integration/result.json` classifies the
failure as `SETUP_OR_EXECUTION_FAILURE`, `failed_stage: integration`, and
`intended_negative: false`. The proof audit also records no accepted result and
no intended-negative credit.

Input preflight, compiler setup, console build, and effective tool pin all
completed with exit code 0. The effective translator hash is
`e8ce100375f0befe1bdce4eaec9380c7949dd34488c28f47b89108bc43ec19da`; the
kernel hash remains `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
The source-preparation stack then failed while importing the FRAME-shadow
fixture: `driver.run -> prepare -> shadow.write_case -> FRAME -> R2 -> prepare.py
-> prepare-actual-nested-drop.py -> prepare-actual-owner-linked.py` attempted to
load the omitted
`research/challenge-8/overnight-linkage/check-intrinsic-drop-linkage.py` and
raised `FileNotFoundError`. No selector capture/proof, C4 proof, composition
proof, regression gate, or raw VC was produced. The B2 archive therefore says
nothing about the AST transport certificate or semantic gates.

This run also disproves the prior static-unreachability assessment for the
pruned source-module rows: the loader chain executes at module import time,
before `write_case` reaches its source-only preparation body. The full original
30-row source pack must be restored for this lane, or replaced by a separately
reviewed complete import closure. A rerun is required after the delivery fix;
this failure cannot be repaired retroactively.

## Compressed-input delivery review

The narrow two-file compression approach is acceptable with the following
checks before any future Cloud submission:

- Keep only the fixed compressed paths `tool-c4.patch.xz` and
  `source-modules.json.xz` in the exact recipe transport. Do not transport the
  corresponding raw files as well.
- Before ordinary preflight, materialize only the allowlisted raw destinations
  `tool-c4.patch` and `source-modules.json`. Check each compressed SHA against
  the pinned manifest, bound decompression to the exact declared raw size (and
  reject truncation or trailing data), then check raw SHA and Git blob OID and
  mode against `HEAD:path` before writing. Reject pre-existing destinations,
  symlinks, and path traversal. Record a data-only receipt and let existing
  patch/source-pack checks run on the reconstructed bytes.
- Pin the compressed files and recipe through the exact submitted commits.
  Do not use a network fetch, alter the transport-part cap, or relax raw
  manifest pins.

The local inert-data check found the compressed `tool-c4.patch` payload
decompresses to its pinned 481,162-byte raw file, and its Git object mode is
`100644`. The restored 30-row source pack also has the prior pinned raw
size/hash, but the current checked-out `HEAD` still has the 23-row tree; its
Git-OID check must be against the newly committed 30-row candidate, not the
stale 835f6cb tree. No compiler, extractor, verifier, Rust, Cargo, or proof
execution was run locally.
