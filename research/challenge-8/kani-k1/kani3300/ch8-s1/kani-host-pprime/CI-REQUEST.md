# CH8 S1 P-prime, worker13

Preparation only, task item 13; g0 input `34fb6ac87607be8e27634245c68331853142ed02`.

- S′ `f22f84f316ad8ef6f3fccce86424bad927b09f78`, tree `e0dc89592926571e823797f8618cd6b4a7e11ff6`, base P′ `c5ff36ff433692140605891f646043f991db05de`.
- Control `8c8ac10d675fff41d5ec1b2684c6f673cd6bfaf2`, tree `f0a7d1d51f9d57f1c0f859f632741066a6e5c11f`, sole parent/tool `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- Local branches/worktrees and exact manifest/request SHA256 are in `CI-REQUEST.json`.
- 23 rows/oracles/caps/flags unchanged. `runner.py` changes only its STD_SHA/STD_TREE constants.
- Upload path excludes `${{ env.RECEIPT_ROOT }}/**/target/**`, including `list/target/`.
- Derived source hash for the corrected companion and payload hashes are refreshed. Historical `base_std_sha` and `model_source_sha` in the in-control request retain the original patch/model provenance; executable source binding is S′ SHA/tree.

No push, CI, ledger, publication, compiler or verifier executed. All proof rows NOT_RUN; no proof credit.
