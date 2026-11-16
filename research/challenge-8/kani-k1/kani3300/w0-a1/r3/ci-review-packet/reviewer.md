# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `bf81a1f14f9468c5b25d3ee33f7dafbf2bca131e`
- Candidate: `e3e9f138b77d81ae7f75d3a6ec910e9c27eb3a8e`
- Candidate tree: `483b25c43c2a4c44f8107b33cdd764b027cc6d1f`
- Diff SHA256: `b1c764533787a2b05c095190393c7c73b035bb02b3cb6fd324cede11fc45a1c0`

## Defect

Compile diagnostics were removed by upload bounding; std rows repeated core compilation failure; standalone5151 fixtures lack edition2021.

## Applicability

R3 preparation only. Single serial eight-row SEL1 job and two5151 fixtures on both frozen source pins; std312ff625 dependency.

## Invariants
- Frozen Kani source/compiler/runtime and all eight A1 verification profiles unchanged. No proof credit from wrapper exits.
- Keep original exits/signals/exceptions and incomplete evidence; no retry; N32 first; source-stage-target identities checked.
- Stream32MiB, metadata16MiB, upload256MiB, group timeout600s and frozenRSS reserve preserved; intended target dirs excluded.
- Preserve all issue fixture source bytes; edition2021 scoped identically to both5151 cases and both pins.
- No push, CI, ledger or local Rust/compiler/verifier execution.

## Required controls
- 24 isolated Python synthetic service tests passed: success/error/signal/timeout/partial/missing/null/wrong-type/source drift/NOT_RUN and excerpt/upload cases.
- Offline workflow/request/std patch checker: shell syntax, inlinePython AST,4 negative workflow mutations, unchanged R1 row specs.

## Declared dependencies
- `scripts/ch8-w0-a1/replay_origin.py` → `dependencies/0000.bin` (mode 100644, SHA256 aa5d3484421c8266ff2aebfeafabc395740133b4625c28e345b5c7fcfbb78ec0)
- `scripts/ch8-w0-a1/native/issue-5151-empty-drop.rs` → `dependencies/0001.bin` (mode 100644, SHA256 5f21884535ffd4fedcf28056257f568bd5d52b95fd00ed059a4576ad5a1c2bb4)
- `scripts/ch8-w0-a1/native/issue-5151-initialized-slot-companion.rs` → `dependencies/0002.bin` (mode 100644, SHA256 b9583a302214a90d61778cc4e7ce28d6b337d63b4d53d0ff54c13460da2adc1c)
- `scripts/ch8-w0-a1/native/MANIFEST.json` → `dependencies/0003.bin` (mode 100644, SHA256 aa0e4cbde9973ac4c8ba727dd6349a0c63b97febf870685049f963cf58309a4a)
- `scripts/ch8-w0-a1/baseline-source-binding.json` → `dependencies/0004.bin` (mode 100644, SHA256 d3de2bc1fa15080475d125bb7325bbab26d061ccc4a9f40ecf43916516bc49aa)
- `scripts/ch8-w0-a1/sel1-source-binding.json` → `dependencies/0005.bin` (mode 100644, SHA256 d4ed00227c03cd59c759c2551064d362c03b7a2f356cd13bf24ac16dbe59630b)
- `kani-driver/src/call_cargo.rs` → `dependencies/0006.bin` (mode 100644, SHA256 6801ea256ab3464b72487c8aacc17e5e79920903304aa82d5f02e23d129c6129)
- `kani-driver/src/call_single_file.rs` → `dependencies/0007.bin` (mode 100644, SHA256 3fc27b10a1db7705b514e7689e9c6e6b2f20516066664ad799b32f4adc23c996)
- `kani-driver/src/util.rs` → `dependencies/0008.bin` (mode 100644, SHA256 9b0e3df2d1dda2ca2616dadef9925c5ace0ec01cc0504d8df35fa4ab6c7de000)
- `kani-driver/src/project.rs` → `dependencies/0009.bin` (mode 100644, SHA256 55bc8b60644000ede89bcb1bd43f923a5035659314b57e6f9c56884dd38b0627)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- R1 first8652 diagnostics unavailable. Static bad import fix does not establish entire error cause.
- No actual compile/verifier/CI result.230 runner-min is a proposed coordinator envelope, no budget authorization.

Do not execute source or evidence from this packet. Do not claim new proof credit.
