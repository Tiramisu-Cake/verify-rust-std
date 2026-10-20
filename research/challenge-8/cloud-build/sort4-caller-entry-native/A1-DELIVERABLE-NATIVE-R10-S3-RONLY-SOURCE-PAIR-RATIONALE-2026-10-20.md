# R10 S3 rationale: R-only source-pair gate

## Defect and applicability

`collect_native_reference_baseline` validates P1's source pair using the canonical keys `verified` and `original`. After invoking the R-only console, it reconstructed the same pair with keys `verified/lib.rs` and `original/lib.rs`, compared those dictionaries directly, then indexed the path-shaped keys as if they were canonical keys. The equality therefore failed even when both source files were byte-identical. The failure message combined this impossible equality with AST existence, obscuring the actual gate.

This defect applies to every R10 P1 native-reference collection. The R10 S2 Brief catalogue confirms that the AST output was present in the archived stage; the stage record did not retain post-stage source hashes, so the precise changed-file hypothesis is unnecessary and unsupported. The source-only cause is the inconsistent key shape.

## Change and controls

Reconstruct the post-stage pair with the already-established canonical keys and their explicit fixture-relative paths. Check source-pair preservation and AST existence independently, with bounded diagnostics that identify the failed gate and report only the two SHA-256 values where applicable. Keep the exact source-pair equality requirement, native AST baseline gates, stage exit observation, and `proof_credit=False` unchanged. A nonzero console exit that emitted its AST remains an observed structural-only baseline; it is not accepted as proof.

Synthetic isolated tests exercise unchanged source plus AST (including nonzero stage exit), each source file changing independently, and missing AST. These tests validate the actual collector boundary with fake stage/helper services; they do not invoke preparation, compilation, extraction, or a verifier.
