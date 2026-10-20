# R8 S1 matrix coverage — 2026-10-20

## Evidence identity

Build `4c176189-3bf0-4aed-abdd-a42b451c1f1f` ended with Cloud Build status **FAILURE** after **702 s** (task/coordinator status). Its package was reported by Brief as **VERIFIED_ARCHIVE_AND_INVENTORY**; the Brief separately reports runner exit `0`, evidence complete `true`, and source proof verdict **NOT_ACCEPTED_AS_REPORTED**. These are distinct reporting layers. Archive SHA-256: `c836700b5cf14530824135426fcc83b0817610fa75910ee5cc78d65f9452af4e`. Index SHA-256: `ff6deb69d99aa82fbdcc9b8e10fe8e293b5af97eaaafec33a8903978366426b1`.

The source binds authorization phase `SORT4-POST-MIGRATION-NATIVE-PROOF-2026-10-20-R8` to protocol phase `SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17`, profile SHA-256 `a4b458173313345fd92350722a7f3dca1d27e615f987451d0a73446c641ea0f9`, and infra/proof SHA `69e377ad620808b0d314f8bdc5ae8c9de7ebb8a9`. The queried `proof-audit.json` has file ID `cc20cf422e3f3828330adb99a0a55222711961bbb855f3b12dfc360c537a3e96`, SHA-256 `995548317f5a8823f66218d65211d053d11672598c53e3fe0fcb7099f217ebbe`, size 1871496 bytes, and 31 JSON root children. `/case_status` and `/cases` each report 26 children. The current R8 profile supplies those 26 expected names under `first_matrix_cases`; it does not contain an `initial_case_status` property.

All 26 named `/case_status/NAME` requests returned `exact=true`, `complete=true`, and `next_offset=null`, matched the expected file SHA, and are listed with their request IDs in the companion JSON. No pagination was needed for the individual records.

## Matrix status claims

- `NOT_RUN`: 13
- `INTENDED_CLASSIFIED`: 10
- `INCONCLUSIVE`: 3
- `matrix_gate_passed=true`: 10 rows; `false`: 16 rows.
- `proof_credit=true`: 0 rows.

The source summary says `matrix_complete=false`, `dispatch_ready=false`, `accepted=false`, `diagnostic_complete=false`, and `first_missing_stage=P0a`. P0a is `INCONCLUSIVE` with reason “focused execution attestation missing.” The root source field `first_causal_stage=verification` is preserved as a source assertion; Brief causality remains **UNKNOWN**.

## Tool and native-reference receipts

The source `tool_receipt` is classified `A1_TOOL_BUILT_UNRUN_PROOF`, reports `build_exit=0`, and `proof_credit=false`. Its final tool pins include translator `8b98050f380729625b1ec766be6764af75e65d457c6b99f28a2a38d3a3676d7c`, exporter `c29d0d4692eab84257fe61036d6e41dbc11ee3ad999005df4ffb157bb8b463ad`, schema `a7542ee05f1a9fdde34baa9ea73ddd939a2cbf2f197c0737941f9f0d957f969b`, and kernel `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.

The nested `tool_receipt.native_reference` is classified by kind `separately-built-R-only-native-reference`, reports `build_exit=0`, `c_patch_applied=false`, and `proof_credit=false`. It records translator `9391bff0376ad008798a950d76dbaac095cacbe8fd5acf5b2ea4d336a759f33f`, exporter source `c29d0d4692eab84257fe61036d6e41dbc11ee3ad999005df4ffb157bb8b463ad`, schema `a7542ee05f1a9fdde34baa9ea73ddd939a2cbf2f197c0737941f9f0d957f969b`, and R patch `9cdca995bc926efe3275319dec345f4d70a2fec7fdc95781decb4e4c2df7c9c8`. These receipts are source claims and do not establish AST/source binding, formal proof acceptance, or independent proof credit.

The full bounded fields, selector request IDs, exactness, and per-case reasons are in `A1-POST-MIGRATION-R8-S1-MATRIX-2026-10-20.json`. The reader transcript is separately retained as `A1-POST-MIGRATION-R8-S1-MATRIX-READER-OBSERVATIONS-2026-10-20.json`.
