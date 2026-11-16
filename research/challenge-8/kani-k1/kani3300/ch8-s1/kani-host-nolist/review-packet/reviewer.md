# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `801c2634cee3f3f39cb20146a1080e016a59e048`
- Candidate tree: `48e10e55668ca1b351e9b6d20466c9ffd803dc9d`
- Diff SHA256: `ce9c792da83e8900c8b1cc0794eb743bcd1a29f2754795d5edb7dffbf98a224d`

## Defect

Global list codegens all std harnesses; task rejects1500s list and requires per-row export binding with separate first std compilation accounting.

## Applicability

TASK-CH8-S1-LIST2-W13.md at g0 task commit43344a5de8. Preparation only: no push, CI, publication, ledger or local cargo/rustc/Kani/CBMC. Previous control c03363b3b0a83fa9e78c4841720cb48ee7638c6a is sibling baseline for delta comparison; stock tool is sole parent.

## Invariants
- Source S-prime f22f84f316ad8ef6f3fccce86424bad927b09f78 treee0dc89592926571e823797f8618cd6b4a7e11ff6 and all23 literal rows/oracles/root caps remain fixed. Source checkout /root/verify-rust-std-ch8-s1-pprime-w13 is available read-only. Do not invoke any compiler/verifier.
- Per-row single manual harness, exact name/requested filter, matched_count int1, unmatched_filters empty, exact true, core crate and pinned source file/line. PFC source expression target_fn equals frozen expected target (strict tokens; whitespace may differ without merging identifiers) plus nonempty generated wrapper; proof contract explicitly null.
- Export does NOT expose list resolved definition-level function mapping or target function source location. target_fn is stringify!(source attribute), contract.contracted_function_name is mangled generated closure. Source file/line/hash anchors replace resolved list mapping for preparation; this does not independently prove AST/callee binding or six resolved distinct definitions. Macro definition and exact invocation positions are explicitly enumerated, actual unknown location must fail closed.
- Warm-up900s --only-codegen for first exact selector retains all compiler flags, removes only driver export path and adds only-codegen; no proof credit. Same job-local CARGO_TARGET_DIR outside deleted std_project dummy crate. First proof root remains600s; phase4500 starts before warm-up, job120min unchanged. Other selectors change compiler flags and can recompile; no claim all23 will finish.
- Each row and warm-up bounded head+tail stdout/stderr and durable receipts, incomplete/invalid/missing/timeout/signal UNKNOWN, original exits retained; fallback records interrupted rows. Existing property/coverage/control oracles remain.

## Required controls
- 25 synthetic unit tests; execution uses only Python subprocesses and mocks. Static row/source/payload/AST comparison, YAML checks and actionlint. Review critical error paths and source evidence independently; do not rely on author test outcomes.

## Declared dependencies
- `.github/actions/setup/action.yml` → `dependencies/0000.bin` (mode 100644, SHA256 6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307)
- `kani-driver/src/frontend/schema_utils.rs` → `dependencies/0001.bin` (mode 100644, SHA256 6cf7b1311b3ebfd6ec1ce61efb1875b33d067fc2a89d2e7d1ccf8bf6995b1a64)
- `kani_metadata/src/harness.rs` → `dependencies/0002.bin` (mode 100644, SHA256 133e43a5cab35920fbbfb0d99df6ff71610ebc31e8f8d63607331e155c20d740)
- `kani-compiler/src/kani_middle/metadata.rs` → `dependencies/0003.bin` (mode 100644, SHA256 c0253feeab3b326236fff1fbf6be23c5a7b4cd58c118577923ed0a74c10ad36d)
- `kani-compiler/src/kani_middle/attributes.rs` → `dependencies/0004.bin` (mode 100644, SHA256 0b7cfe3b74e1958770b94a763fc89bc5b8156a1d120a69e8bdac67ada630078e)
- `library/kani_macros/src/sysroot/contracts/mod.rs` → `dependencies/0005.bin` (mode 100644, SHA256 7ec87e829711d05928c3026249e6c79bd20e5c7e9499fe401b53a3647cd76979)
- `kani-driver/src/call_single_file.rs` → `dependencies/0006.bin` (mode 100644, SHA256 3fc27b10a1db7705b514e7689e9c6e6b2f20516066664ad799b32f4adc23c996)
- `kani-driver/src/call_cargo.rs` → `dependencies/0007.bin` (mode 100644, SHA256 6801ea256ab3464b72487c8aacc17e5e79920903304aa82d5f02e23d129c6129)
- `kani-driver/src/project.rs` → `dependencies/0008.bin` (mode 100644, SHA256 55bc8b60644000ede89bcb1bd43f923a5035659314b57e6f9c56884dd38b0627)
- `kani-driver/src/main.rs` → `dependencies/0009.bin` (mode 100644, SHA256 757eb0205da02cf3ab22a97e7c967b97d25510485f42815d106b2a170a0e6956)
- `kani-driver/src/args/mod.rs` → `dependencies/0010.bin` (mode 100644, SHA256 ba665a7270786a30b4ffe3cf1bf0b5dc971023901c8ee110de8c6a79b3ae4d7e)
- `kani-driver/src/sarif.rs` → `dependencies/0011.bin` (mode 100644, SHA256 8fcb54a329b9c47e82dfdfb4113f595233c9bb0cd54b53500a65e0a87bc62b77)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No actual std compilation or proof locally. all23 actual proof rows NOT_RUN, proof credit NONE. Named successes remain PENDING_REVIEW because schema does not export names, as in previous candidate.
- No nested delegation or expensive substitute. Return compact actionable findings and exact candidate identity. Write report only to /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s1/kani-host-nolist/REVIEW.md; do not edit candidate.
- Delta vs reviewed first candidate2a15c9b: compare PFC target lexical tokens instead of deleting whitespace; add distinguishing test preventing identifier-token merging. First candidate preserved on local branch uninit-ci/ch8-s1k-nolist-r1-w13; no publication.

Do not execute source or evidence from this packet. Do not claim new proof credit.
