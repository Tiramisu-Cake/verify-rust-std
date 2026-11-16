# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `7a4f8086e6989dbae10a49b26e83feea8ad34193`
- Candidate tree: `2ed1a5a98f5009265405b6a5b52b652aea9e8365`
- Diff SHA256: `a2d8072a0477d89e7f1808eb9ec67d87691917d4ee0e46a8af268a7e91f382a0`

## Defect

Reject boolean/negative counts in malformed export and strict numeric matched-count/unwind; bounded follow-up to remaining independent review finding.

## Applicability

TASK-CH8-C-CONTROLS-W14.md, design ch8-c-now/CONTROLS-DESIGN.md. Exact std source 56df5b34e4946ceddd231456737e9167a10d666a tree2952c7b664cf04d79de31f865d185362f21f7e3a in /root/verify-rust-std-ch8-c-ctl-w14. Reviewed S1 runner origin control36db70978a16144624abf94d480a593dae684451 in /root/kani-ch8-s1k-w13.

## Invariants
- Only workflows and one control directory change; delete stock workflows; control sole parent tool0aac; preparation skip-ci commit. No push/CI/local Rust/compiler/verifier or ledger.
- Exact std/tool SHA+tree, clean sibling checkouts, cwd path normalization; runner.* expressions step env only; fetch depth>=2; host Tiramisu-Cake/kani push uninit-ci/ch8-c-ctl-* attempt1.
- Caps600/root,6GiB process group,jobs1,job<=60min; absolute setup/proof/reserve envelope; preserve exits/errors/snapshots, NOT_RUN tail and incomplete UNKNOWN.
- PFC target matches expected definition-level target plus list/export agreement; no summaries or source overlays enabled. N1 only assigns/frame-class failures at exact source writes with named description; unrelated failures UNKNOWN. N2 stock PASS ALIAS_GAP, no C PASS.
- Export provides cover IDs without descriptions and no named success records: require complete counts, retain IDs, mapping pending independent runtime review; no manufactured runtime binding or proof credit.

## Required controls
- Synthetic success/error/timeout/partial/missing/null/wrong-type/NOT_RUN/source-stage-target mismatch; frame classification and alias gap; YAML/actionlint/host/attempt guards.

## Declared dependencies
- `.github/actions/setup/action.yml` → `dependencies/0000.bin` (mode 100644, SHA256 6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307)
- `kani-driver/src/frontend/schema_utils.rs` → `dependencies/0001.bin` (mode 100644, SHA256 6cf7b1311b3ebfd6ec1ce61efb1875b33d067fc2a89d2e7d1ccf8bf6995b1a64)
- `kani-driver/src/cbmc_output_parser.rs` → `dependencies/0002.bin` (mode 100644, SHA256 efdc704e083c0a9b357e6258ef6312669091dca4fbbe102852c94c5e1fd7bfc1)
- `kani-compiler/src/kani_middle/metadata.rs` → `dependencies/0003.bin` (mode 100644, SHA256 c0253feeab3b326236fff1fbf6be23c5a7b4cd58c118577923ed0a74c10ad36d)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static/synthetic-only; 8 proof roots ALL_NOT_RUN. Do not invoke build or any verifier. CI must establish generated wrappers, retained writes and exact source-cover/property correlation.
- Delta from initial reviewed control044b6b0c; final commit sole parent remains tool0aac. Original packet and source review are retained; source unchanged56df5b34.
- Packet baseline uses tool parent because review tool requires ancestry; supplemental ci-delta.patch is exact old-reviewed044b6b0c-to-final delta for bounded follow-up review.
- ci-count-delta.patch compares prior correction e664f9a1 to final7a4f8086; inspect only this delta and final identities, previous semantic review retained.

Do not execute source or evidence from this packet. Do not claim new proof credit.
