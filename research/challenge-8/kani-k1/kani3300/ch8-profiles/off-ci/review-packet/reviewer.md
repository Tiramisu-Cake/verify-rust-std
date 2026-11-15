# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `236bf75037fa4e56d0aa18f93df1d6b6965676b8`
- Candidate tree: `89e69479b1fe981a24a37ad9822646e0d490f6f7`
- Diff SHA256: `8bde55dc81e2353cbd0ff1849220052cbfdd456369bccbca2258d9359c3bb218`

## Defect

Prepare one fixed Profiles OFF CI-only batch hosted on Tiramisu-Cake/kani with exact separate std and stock tool checkouts.

## Applicability

Only .github/workflows and ch8-prof-off-control. Source manifest is the fixed62-row Profiles request at g0 ea3cec4078. No source/tool semantic patches.

## Invariants
- No push/CI/ledger or local cargo/rustc/Kani/CBMC; only Git/static parsing and small synthetic tests.
- Single parent equals upstream0aac16ef62da9e9d5645782d458593e5d78143ba; one workflow, repository and ref guard, attempt1; checkouts siblings/depth2.
- Exact source b5cf722e20f71c1f4f494ec4ad2af2970aa3bc9f/tree bd6fdf1750e589a8fa5c63bfd445553df43adb8a, exact stock tool binary.
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
