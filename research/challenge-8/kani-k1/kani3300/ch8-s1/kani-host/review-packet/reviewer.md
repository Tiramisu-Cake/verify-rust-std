# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `36db70978a16144624abf94d480a593dae684451`
- Candidate tree: `f3d36d51f58bf7937f6f8778260e3e2816996b48`
- Diff SHA256: `3b511493c98306b16b90c190d0edce3d3ab373df61b58df060e0374dacf43b02`

## Defect

Prepare the same CH8 S1 batch on Kani host after absent std-fork Actions runs; preparation only.

## Applicability

One CI-only single-parent control; host migration from std control f88bf3f0ea0ef1f87ca01ba5da11b57be574adf1. Original control is available in /root/verify-rust-std-ch8-s1-w13 Git object store. Task /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/TASK-CH8-S1K-HOST-W13.md.

## Invariants
- Only .github/workflows and ch8-s1-control changed; stock workflows removed; single workflow push uninit-ci/ch8-s1k-* on Tiramisu-Cake/kani.
- runner.py, test_runner.py, activation patches and all request non-host fields including rows/oracles/caps must match original control exactly.
- Exact production std75a4 and stock tool0aac checkouts with sibling layout, paths normalized from cwd, runner.* step env only; no local tool execution.

## Required controls
- New host repository/ref/single parent/path inventory/payload/only-workflow checks; YAML sensitivity tests; original runner error paths.
- Independent review must check workflow and host binding changes and exact immutable batch equality.

## Declared dependencies
- `.github/actions/setup/action.yml` → `dependencies/0000.bin` (mode 100644, SHA256 6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No push, CI, publication or ledger operations authorized; no local cargo/rustc/Kani/CBMC; no raw evidence logs.
- Review author must not execute build subcommand; synthetic mocked build wrapper tests are allowed.
- No proof credit; actual 23 rows remain NOT_RUN.

Do not execute source or evidence from this packet. Do not claim new proof credit.
