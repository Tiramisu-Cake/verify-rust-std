# CH8 S1 P-prime paired candidate review

**Decision: PREPARATION_ONLY — ready for the next authorized handoff; no proof credit.**

## Reviewed identities

- Source candidate `f22f84f316ad8ef6f3fccce86424bad927b09f78` (tree `e0dc89592926571e823797f8618cd6b4a7e11ff6`), baseline P-prime `c5ff36ff433692140605891f646043f991db05de`; prior source `75a4d1ea6eb60c63c27c1b18e662740d93bafb08`.
- Control candidate `8c8ac10d675fff41d5ec1b2684c6f673cd6bfaf2` (tree `f0a7d1d51f9d57f1c0f859f632741066a6e5c11f`), parent tool `0aac16ef62da9e9d5645782d458593e5d78143ba`; prior control `36db70978a16144624abf94d480a593dae684451`.
- Source review spec SHA-256 `908e6f0263b09a82c93bb2b4d8f0cf2d16bbb1a802d5ae5ba999ca2f810f4831`; packet SHA-256 `e4ec3197dccf5a8acf34c6dc875bf5c15322e0e3b9784743403b6b925a0f5e9f`.
- Control review spec SHA-256 `9d7ab67acaacdf26fad3ee43eb6534f68db90fde4ec63536954486230a41d54a`; packet SHA-256 `a6d6a6a315e229f299b144d28305a58315142443ef531df843c2b29765e35e60`.

## Findings

- Both packets pass `smallsort-session review check` against the requested candidate and spec identities.
- Source candidate is the P-prime rebase with the pin resolved to tool `0aac`; its only post-rebase source correction is removal of the extra `>` in `sorting_entry_controls.rs`. Read the complete S1 source diff and the model, smoke, and control companions; found no similar punctuation/syntax typo. `check_source.py` reports six actual method bodies byte-identical to P-prime after removing 19 verification attributes. The six S1 entry roots and two activation companions remain registered behind the opt-in cfgs. The `DETECTED` false-assertion controls are intentional negative controls per the request matrix.
- Control delta versus prior control is limited to `STD_SHA`/`STD_TREE`, the matching request and payload/source hashes, and workflow upload exclusion of `**/target/**`. The runner has only the two standard-library identity constants changed. Static checks confirm both activation patches and result hashes, source/control identities, and byte-identical 23 literal rows (SHA-256 `4a392837eed3ee6e8b67812ed3c7d22001796efe9d98d6aa02d8ef165d6f9856`).
- No candidate edits or unexplained semantic differences found in the paired package.

## Validation and limits

- `smallsort-session review check`: source and control packets valid.
- `check_source.py`: `PASS_STATIC_ONLY`; runtime bodies identical; 6 methods, 6 PFC smoke roots, 2 activation companions.
- `check_rebase.py`: `PASS_STATIC_ONLY`; 23 rows unchanged; runner delta and upload exclusion as specified; activation patch/hash checks pass.
- No cargo/rustc/Kani/CBMC, build/list/run, CI, push, ledger, or raw evidence was used. Compilation and proof outcomes remain unestablished; all 23 rows are **NOT_RUN**, with **no proof credit**.
