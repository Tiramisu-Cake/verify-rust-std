# Independent S1-04 review

**Decision: ACCEPT_STATIC_WITH_LIMITATIONS**

Reviewed exact committed inputs:

- Source candidate `5be85699b8826e3286c0bf89efb9affefac0acb5`, baseline `f22f84f316ad8ef6f3fccce86424bad927b09f78`, tree `a9caaa953d579641ecc6a4b84b5c16fa1d23563b`; source packet diff SHA256 `f135f71cc9ece1675ac5fb19a4e16cfe2b3ef9d4f50daab26f3a490dbf2f2c60`.
- Control candidate `5fd538730869103cb7108cd823f58b1dac924960`, baseline `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`, tree `81ded40ddd99579cbe06efd74e19b1bf5801803a`; final control packet diff SHA256 `6d1ecf3739233823b5e8577be6048ab53893f17cfcedd2fcb17d04dd93b5be53`.

## Findings

- The source split is limited to verification fixtures. The exact-N roots keep the original PFC targets, type/comparator substitutions, arbitrary byte inputs, backing/canary geometry, stable scratch sizing, caller-postcondition checks, and unwind 34. The original symbolic roots remain. The per-N covers reconstruct the required 11-cover union; no partial union is treated as replacement acceptance.
- Control request pins the source/tool identities and inventories 35 rows in 14 disjoint groups across the four ordered workflow stages. Runner selection is an explicit subset of the full partition. Source is verified before overlay; lossless porcelain parsing and cleanup preserve the primary failure while marking drift or incomplete execution UNKNOWN. Negative oracles bind exact property ID, export file, line, and class; activation false-ensures controls remain unbound and cannot qualify as detections.
- The initially identified fallback gap is fixed: fallback now preserves the prior terminal snapshot and synthesizes a pinned, selected-group terminal envelope with UNKNOWN row outcomes when execution has no valid final envelope. Added setup-failure/mid-run tests verify the artifact is collectable and remains no-credit.
- The initially identified max-parallel-2 estimate is corrected: eight two-root heavy groups yield 19,240s at parallelism two and 42,680s total. The selected max-parallel-1 envelope remains 71,540s. This is conservative planning arithmetic, not a measured completion-time guarantee.
- Final control delta only clarifies the control-parent diagnostic and reports `control_parent` separately from `tool_sha`; the request payload hash matches the updated file. No behavior or review finding changes.
- `git diff --check` was clean for the source candidate. Synthetic control suite: 35 tests passed (`test_runner.py`, `test_package.py`, `test_s104.py`). No Rust compiler, Kani, CBMC, CI, push, or dispatch was run.

## Limitations

This is static/source-and-control review only. The exact-N proof rows and activation controls remain NOT_RUN. Named success/cover binding, false-ensures wrapper IDs, exception-role qualification, and runtime cost of the split remain pending. This review grants no proof credit, qualified acceptance, or dispatch authorization.
