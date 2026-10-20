# R8 activation rationale

R7 window expired; CURRENT-TASK now explicitly authorizes a separate R8 session with 3600 Cloud seconds. T0=2026-10-20T14:28:47Z, main=16:28:47Z, absolute=16:58:47Z. No carry from R7, no historical ledger changes.

Defect/applicability: R7 authorization guards intentionally reject unknown phases/profile paths. R8 therefore needs an exact branch-local phase/profile/entry/adapter/recipe binding and the same registration in every transported focus-helper consumer. Preserve canonical paths, profile SHA/decoded object equality, environment equality, protocol/accepted=false checks and immutable source-core hash. Add only the explicitly authorized R8 pair; preserve R6/R7 mappings. Runtime std, compiler/tools/R2/C, native contracts/equality, normal/unwind checks and all26 semantic inputs remain those of R7 S2/S3.

Controls: isolated activation stub (never actual core import), exact current profile through pure validator, wrong/unknown/old/missing/null/hash/path/environment/protocol/core mutation negatives; source closure, immutable semantic inputs comparison; independent Luna HIGH review before submit. Existing early Cloud preflight -> actual target -> reachable dependent controls. S3 audit canonicalization rationale is separate and source-supported, not an established cause of S2. Success of transport or setup has no proof credit.
