# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `c9b3a0a5ddd0103d7ecdcbb0cd42d7683cbb11a2`
- Candidate tree: `959f15e8da123fe623c2e1185dbc7a963652b68b`
- Diff SHA256: `9cb0ad489b3bee1a376ce918a93571e2a6bbe8fa15c30fd54f030516c6c4fb7f`

## Defect

Prepare bounded CI-only valid-value235 ordinary-root census without changing compiler/std. Review runner outcome integrity and GitHub Actions readiness.

## Applicability

Challenge8 item1 laneB step1; one future coordinator dispatch; no push/CI now.

## Invariants
- Exact std872d and pristine Kani0aac, all235 roots and historic shard membership retained.
- Organizer semantic flags plus valid-value-checks; exporter is diagnostic transport.
- No cfg-on/autoharness; unknown/timeouts/mismatched identities cannot become PASS.

## Required controls
- Offline synthetic tests success/error/timeouts/RSS/output/missing/null/wrong-type/NOT_RUN/source-stage-target mismatch.
- Static YAML/actionlint; no actual compiler invoked.

## Declared dependencies

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No execution evidence; only CI packaging.
- Ubuntu-only, per-root bounded scheduling; no cross-OS cost/proof qualification.

Do not execute source or evidence from this packet. Do not claim new proof credit.
