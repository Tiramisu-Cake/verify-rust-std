# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `c5ff36ff433692140605891f646043f991db05de`
- Candidate: `f22f84f316ad8ef6f3fccce86424bad927b09f78`
- Candidate tree: `e0dc89592926571e823797f8618cd6b4a7e11ff6`
- Diff SHA256: `66cbefb6e3a54acf9db5a364b43b5298bfa54d3cd8cc070bf8a935706a80d315`

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
- `library/core/src/slice/sort/shared/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 fa9eec2901bafba25c9c1e1684df76dbb1f86e0bbd04f18f3e67cee54dcdfcc8)
- `scripts/run-kani.sh` → `dependencies/0001.bin` (mode 100755, SHA256 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1)
- `rust-toolchain.toml` → `dependencies/0002.bin` (mode 100644, SHA256 689c159497e53389671511fa85e200533c2a892488346620ccaae0a34ad45618)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No Rust/Kani compilation or proof run; all 23 rows NOT_RUN and no proof credit.
- Do not run build/list/run or actual compiler/exporter; mocked synthetic service tests allowed.
- No nested delegation. Return compact findings, validation and preparation-only decision.

Do not execute source or evidence from this packet. Do not claim new proof credit.
