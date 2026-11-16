# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`
- Candidate tree: `c17af287534589256ea5db86a60763e2832a88f3`
- Diff SHA256: `0f402fda7773c10ee476a35e1380851468fc394eecbb965f5b6648aa86d4f285`

## Defect

Per-row --harness changes compiler flags and rebuilds core/alloc/std per row. User supplement replaces per-row execution by grouped invocations.

## Applicability

CH8-RUNNER-BATCH-NOTE.md at g0 82cc48368e1e3aec544975831bc9595d26f5781d supplements TASK-CH8-S1-LIST2-W13.md. Same S-prime f22f84f316,23 rows/oracles. Preparation only; no push/CI/publication/ledger/local cargo/rustc/Kani/CBMC.

## Invariants
- Candidate sole parent exact stock0aac16ef62da9e9d5645782d458593e5d78143ba; 801c263 is previous sibling control, reviewed. No tool/source changes; source S-prime f22f84f316ad8ef6f3fccce86424bad927b09f78 treee0dc89592926571e823797f8618cd6b4a7e11ff6 at /root/verify-rust-std-ch8-s1-pprime-w13 read-only.
- Group by exact variant/unwind to retain all literal flags. Five groups: production34(15),production5(3),production4(3),activation-default34(1),activation-override34(1). Exactly one verify-std invocation/group; no separate warm-up/list. Repeat --harness, exact, jobs1, harness-timeout600s, one export JSON.
- Per-row exact manual/core/source/contract/token binding and property/coverage/negative oracles retained. Group selection exact count/set, unique names, full COMPLETE export. Order of harnesses[] must not matter. Missing/invalid/duplicate/unexpected inventory UNKNOWN. Positive root may be EXPECTED despite group exit1 when another root failed as expected. Driver exit is group-only; per-root exit unavailable.
- CompileMonitor caps compile+project-link until stock initial export marker at900s inside the SAME process; initial marker is written before harness verification by main.rs/begin_export_json. It writes bounded compilation receipt on observed boundary/failure; fast COMPLETE export before cap is an upper bound. A missing/late/invalid marker is UNKNOWN, not proof. No compiler rerun.
- Group wall budget900+sum(row600); shared4500 phase separately limits actual execution. Root600 timeout is stock Kani CBMC timeout, not full instrumentation wall; no fail-fast. Phase cut can leave an INCOMPLETE marker and all rows of that group UNKNOWN. Job120min and existing payload caps retained.
- RSS group cap min(12GiB,MemAvailable-2GiB,cgroup_headroom-2GiB) determined before launch; sampled process-group peak only. Exact per-harness attribution is unavailable, so each root RSS is explicitly UNKNOWN, not claimed below6GiB. Group observations grant no automatic proof/resource credit.
- Atomic group/compile/row receipts, bounded head+tail logs. Live bounded tail flush survives missing finalization. Source/tool drift, malformed export, exit mismatch, caps and interrupted groups invalidate rows; overlay cleanup in finally. Individual TIMEOUT/invalid row cannot become PASS; other completed rows in a complete export remain individually inspectable.

## Required controls
- 28 synthetic Python unit tests (process/compile-boundary success/error/timeout/signal/launch/RSS, batch order and mixed verdicts, group+row malformed exports/bindings, source/fingerprint/overlay cleanup errors, phase limit and cgroup budget, fallback and durable live head+tail). Review source and controls independently; author outcomes are not proof.

## Declared dependencies
- `kani-driver/src/frontend/schema_utils.rs` → `dependencies/0000.bin` (mode 100644, SHA256 6cf7b1311b3ebfd6ec1ce61efb1875b33d067fc2a89d2e7d1ccf8bf6995b1a64)
- `kani-driver/src/main.rs` → `dependencies/0001.bin` (mode 100644, SHA256 757eb0205da02cf3ab22a97e7c967b97d25510485f42815d106b2a170a0e6956)
- `kani-driver/src/project.rs` → `dependencies/0002.bin` (mode 100644, SHA256 55bc8b60644000ede89bcb1bd43f923a5035659314b57e6f9c56884dd38b0627)
- `kani-driver/src/call_cargo.rs` → `dependencies/0003.bin` (mode 100644, SHA256 6801ea256ab3464b72487c8aacc17e5e79920903304aa82d5f02e23d129c6129)
- `kani-driver/src/call_single_file.rs` → `dependencies/0004.bin` (mode 100644, SHA256 3fc27b10a1db7705b514e7689e9c6e6b2f20516066664ad799b32f4adc23c996)
- `kani-driver/src/call_cbmc.rs` → `dependencies/0005.bin` (mode 100644, SHA256 a0432cfd67358b23815e1f4659623d964d2d6c1818dc78ef779b1954ca341343)
- `kani-driver/src/harness_runner.rs` → `dependencies/0006.bin` (mode 100644, SHA256 4ddabb49fcbc59990e1cce5b6d2985eae33d12724fe1efe2af2534cc4ba0f480)
- `kani-driver/src/args/mod.rs` → `dependencies/0007.bin` (mode 100644, SHA256 ba665a7270786a30b4ffe3cf1bf0b5dc971023901c8ee110de8c6a79b3ae4d7e)
- `kani-driver/src/metadata.rs` → `dependencies/0008.bin` (mode 100644, SHA256 a33e7c2d497bf44e8b8133fdc1e5a88ea976de0dea067f8da3ec48071b002bcd)
- `kani_metadata/src/harness.rs` → `dependencies/0009.bin` (mode 100644, SHA256 133e43a5cab35920fbbfb0d99df6ff71610ebc31e8f8d63607331e155c20d740)
- `kani-driver/src/sarif.rs` → `dependencies/0010.bin` (mode 100644, SHA256 8fcb54a329b9c47e82dfdfb4113f595233c9bb0cd54b53500a65e0a87bc62b77)
- `.github/actions/setup/action.yml` → `dependencies/0011.bin` (mode 100644, SHA256 6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Actual compilation/runtime/cache/memory/source-coordinate behavior is NOT_RUN. Stock export does not establish resolved target DefId/AST/MIR target binding, nor named successful assertion descriptions. Existing explicit no-list limitations remain.
- No nested delegation/model escalation; no actual compiler/verifier/full runner. Review this exact committed candidate and return compact concrete findings or approval PREPARATION_ONLY. Write only /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s1/kani-host-nolist/batch/REVIEW.md. Do not edit candidate.

Do not execute source or evidence from this packet. Do not claim new proof credit.
