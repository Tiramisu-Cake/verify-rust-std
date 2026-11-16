# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `cdd3c6d04112cc1b1e1a80a850389236647bc849`
- Candidate tree: `c6f0606358d088a82129b70d2f1bd081de9e5e7e`
- Diff SHA256: `afcc473d53a8e671f6f801260205032a855ad87b596ff8b41ef566f60cfaf72e`

## Defect

Apply coordinator TASK-CH8-PPRIME-REBASE.md point14: C source controls on P-prime, update CI source pins, exclude generated target build directories from evidence upload.

## Applicability

Supplement to TASK-CH8-C-CONTROLS-W14.md. Source /root/verify-rust-std-ch8-c-ctl-w14-pprime candidate d073585946093071b696eada41b8c8cac18362a7 treee8e9fa63b59ff886077e938d40cffe7ce8c12d42, parent P-primec5ff36ff433692140605891f646043f991db05de tree1302063846873aa300f8bac64fe09e8a3ed1280f. Prior reviewed control7a4f8086e6989dbae10a49b26e83feea8ad34193 in /root/kani-ch8-c-ctl-w14; old source56df5b34e4946ceddd231456737e9167a10d666a.

## Invariants
- Source changes relative to P-prime only control module and verify.rs registration; byte-identical roots and production smallsort/helper bodies relative to prior reviewed candidate. No model/algorithm edit.
- Control sole parent upstream tool0aac; changes only workflows and ch8-c-control; stock workflows removed; skip-ci, no push/CI/ledger/local compiler.
- Only runner source SHA/tree constants change; rows/oracles/caps/flags remain identical. Same target/export/error-path guards, six PFC and two ordinary roots, NOT_RUN and no proof credit.
- Fallback excludes build directories named target before artifact-size accounting and preserves adjacent original evidence/receipts; cleanup failures retain original exception. Upload glob independently excludes **/target/**.
- Local synthetic19 tests/YAML/actionlint only; source compilation is NOT_RUN. Coordinator compilation claims are supplied context, not independently requalified proof.

## Required controls
- Source identity/parent checks; diff old-to-new rows/flags/caps/body. Synthetic target pruning before cap, sibling evidence preservation, cleanup OSError propagation, YAML sensitivity to missing upload exclusion; existing runner service error paths.

## Declared dependencies
- `.github/actions/setup/action.yml` → `dependencies/0000.bin` (mode 100644, SHA256 6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Prior reviews retained in g0 ch8-c-ctl/REVIEW.md and packets. New pprime-control-delta.patch records old control7a4 to candidatecdd3; full packet baseline tool for ancestry constraint. No formal proof or CI compilation in this stage.

Do not execute source or evidence from this packet. Do not claim new proof credit.
