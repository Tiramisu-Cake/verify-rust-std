# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `8c8ac10d675fff41d5ec1b2684c6f673cd6bfaf2`
- Candidate tree: `f0a7d1d51f9d57f1c0f859f632741066a6e5c11f`
- Diff SHA256: `3d6454e345fe0d522311a3d6fbdf13ff4fdaff3222a09202dedbda5f04292f62`

## Defect

CH8 S1 P-prime rebase: 872d/0aac nightly mismatch and extra generic closing angle in override companion; exclude target build directories from artifact upload.

## Applicability

TASK-CH8-PPRIME-REBASE.md item 13; preparation only; no push/CI/ledger or local compiler/verifier. Old source75a4 and control36db available in local Git stores for exact comparison.

## Invariants
- S-prime is cherry-pick of 1313f7c329 and 75a4d1ea6e on c5ff36ff433692140605891f646043f991db05de, pin resolved to tool0aac; only additional source change removes one extra > at sorting_entry_controls.rs:32. Read full source diff for similar syntax errors.
- Runtime algorithms/bodies/signatures/thresholds unchanged relative to P-prime. All old 23 rows/oracles/caps/flags/activation patches unchanged.
- Control is single child of tool0aac; relative to old36db only std SHA/tree bindings, mechanically derived source/payload hashes and workflow target upload exclusion may differ. runner.py differs only STD_SHA/STD_TREE constants. Historical base_std_sha/model_source_sha retained as provenance.

## Required controls
- Static source runtime-body comparison; exact old/new source delta; literal rows equality; workflow exclusion matches list/target and nested target paths; synthetic runner/error paths, actionlint, source and control identity checks.

## Declared dependencies
- `.github/actions/setup/action.yml` → `dependencies/0000.bin` (mode 100644, SHA256 6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No Rust/Kani compilation or proof run; all 23 rows NOT_RUN and no proof credit.
- Do not run build/list/run or actual compiler/exporter; mocked synthetic service tests allowed.
- No nested delegation. Return compact findings, validation and preparation-only decision.

Do not execute source or evidence from this packet. Do not claim new proof credit.
