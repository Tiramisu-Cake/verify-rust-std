# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `6269319aecfb3328a2cffe8e2779432dbc346322`
- Candidate tree: `3c0864f161e79779c6fff0b1c17e14d5e01d0771`
- Diff SHA256: `888b42d222eafe114565167463abeb89115a59e885414bc075ef23de71651638`

## Defect

Rebind OFF control to P-prime-based profiles source and exclude list/row target build directories from upload.

## Applicability

Delta of previously reviewed OFF control. All 62 rows, manifest, tool pin, checks and caps must remain identical. Candidate still has exactly one stock-tool parent.

## Invariants
- No push/CI/ledger or local cargo/rustc/Kani/CBMC; only Git/static parsing and small synthetic tests.
- Single parent equals upstream0aac16ef62da9e9d5645782d458593e5d78143ba; one workflow, repository and ref guard, attempt1; checkouts siblings/depth2.
- Exact source 9fa2f7f97760584f38738909625c064006d8a936/tree 2faa473adeb0172e0f5a5e75fa2d759b20902e6d, exact stock tool binary.
- Preserve rows, source unwind, per-row cfg, ordinary checks, all covers and expected negative oracles; no implicit proof credit or OFF-to-ON transfer.
- All caps/receipts/NOT_RUN fallbacks and preflight failure distinctions maintained.

## Required controls
- Synthetic success/error/timeout/partial/missing/null/wrong-type/NOT_RUN/source-stage-target mismatch.
- Fixed62 row ordering leaf-before-consumer and matching leaf gate.
- Workflow YAML/actionlint, runner context step env only, path normalization.

## Declared dependencies

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Preparation only; actual Rust/Kani and all proof outputs remain NOT_RUN. Generated frame property identity requires post-CI independent binding.

Do not execute source or evidence from this packet. Do not claim new proof credit.
