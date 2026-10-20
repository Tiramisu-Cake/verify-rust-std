# R8 S2 matrix coverage — 2026-10-20

## Evidence identity

Build `9d0d6547-92d3-40f7-95f8-d7696df145e5` ended **FAILURE** after 293 seconds; the coordinator reported 2,605 seconds of window remaining at that status observation. The Evidence Brief reports `VERIFIED_ARCHIVE_AND_INVENTORY`, runner exit `0`, evidence complete `true`, and source proof verdict `NOT_ACCEPTED_AS_REPORTED`. These are separate reporting layers; archive/inventory verification does not establish proof acceptance. Brief causality is **UNKNOWN**.

Archive SHA-256: `1c003941ac4c899f77ef73b6412875f3b3aad9c9e4e8821b293b827b24d0a6b2`. Index SHA-256: `a02c7afe6d6a253da75a040fd3e45c4247e5f6ee9ab453bb2942d2a32ab12fa3`. The queried `proof-audit.json` is file ID `cc20cf422e3f3828330adb99a0a55222711961bbb855f3b12dfc360c537a3e96`, SHA-256 `6e3b3d5f152b413b88fedaecf2fd9744c04ba762ba58e5c3b28bc8ff028c9e21`, size 26,586 bytes, 937 lines, and 30 root children. The source reports authorization phase `SORT4-POST-MIGRATION-NATIVE-PROOF-2026-10-20-R8`, protocol phase `SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17`, profile SHA-256 `095622fa30a55a71d3ba85fb9aa009a6a55ed2bbf196f0f5ef080f273574675e`, and infra/proof SHA `576d59771c7c90b1a25cbc104dfa641cc3f3eae5` / `576d59771c7c90b1a25cbc104dfa641cc3f3eae5`.

The `/case_status` structural pointer returned 20 child names with `next_offset=20`; the explicit continuation at offset 20 returned the final six names and no further offset. All 26 manually named `/case_status/NAME` pointers individually returned `exact=true`, `complete=true`, and `next_offset=null`, matching the expected case-name set. Each request ID and source field is retained in the companion JSON and reader transcript.

## Matrix source claims

- `NOT_RUN`: 26
- `matrix_gate_passed=true`: 0; `false`: 26
- `observed_stage` and `observed_outcome`: null for all 26
- `proof_credit=true`: 0; independent proof credit: 0
- Root source claims: `matrix_complete=false`, `dispatch_ready=false`, `accepted=false`, `diagnostic_complete=false`, `first_missing_stage=OFF`.

Each row's exact source reason is `expected input identity or run pins unavailable`; all provenance values are null. These are source-reported statuses, not an independent determination that any case was executed or accepted. The Brief separately reports `tool-reconstruction` / `adapter_error` from the source and records the first missing stage as `tool-reconstruction`; causality remains unknown from the Brief. The failure-control receipt and diagnostic details are handled separately.

All 26 rows, exact fields, request IDs, source/profile identities, and coverage metadata are in `A1-POST-MIGRATION-R8-S2-MATRIX-2026-10-20.json`. The bounded request transcript is `A1-POST-MIGRATION-R8-S2-MATRIX-READER-OBSERVATIONS-2026-10-20.json`.
