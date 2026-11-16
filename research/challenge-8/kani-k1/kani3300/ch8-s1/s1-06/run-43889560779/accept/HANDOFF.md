# Handoff — S1-06 run 43889560779

Offline acceptance replay completed in `accept/`; result remains **PENDING**, proof credit **NONE**.

- Identity: control `a14a513eb7a77297a0cc10ff6eefa7577c2c383c`, std `5be85699b8826e3286c0bf89efb9affefac0acb5`, tool `0aac16ef62da9e9d5645782d458593e5d78143ba`, request SHA-256 `0ff35bdc40434ac6b22b4f4b5919923ab09d849c08c9930f291c014f8b96fe7b`.
- 4/14 groups (9 rows) have complete locations and source observations only; 10/14 failed/incomplete groups have 18 missing records in 18 rows. All 26 rows in failed groups qualify as `UNKNOWN`, including the eight individually complete rows within `light-controls-u34`.
- Exact observations: 8/8 declared negative oracles; 113/113 required covers SAT-bound; 13/127 required success messages uniquely bound. Positive source verdicts: 27/35.
- Separate remaining gates: 18 rows lack a property coordinate; all 26 rows in failed groups retain group-completeness `UNKNOWN` and `binary_after=UNKNOWN_AFTER_RUN_STOPPED`; unreachable-status role/post/frame/relation applicability pending on 31 rows; full target/contract-wrapper binding pending on 22 rows; remaining required-success bindings and companion gates retained per row. No counterfactual coordinate policy applied.

`accept/intake.py` replays from structured JSON only. It verifies artifact digest metadata, pinned request/source/tool identities, embedded member hashes, property ID/status partitions, source bindings, negative oracles, required covers/messages, and unsupported-construct links. No stdout/stderr preview, raw log, local verifier, CI, push, publication, or ledger action was used.

Main integration owns the final run-level `RESULT.md`, `collected.json`, commit, and any coordinator policy choice.
