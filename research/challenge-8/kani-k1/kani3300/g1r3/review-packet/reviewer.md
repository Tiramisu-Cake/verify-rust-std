# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `02b734151ada1dd0d216b0db329776eb522d2d67`
- Candidate: `6bb067476116704763502763984b225014dce221`
- Candidate tree: `03f3d79d0317436040c3b10b0e094a88ce99092c`
- Diff SHA256: `d87cf7aa909a79db7dd266a15c79fc7ecd230e23f834d59cd50faaba26377f39`

## Defect

Negative fixtures encounter a wrapper guard before their intended moved-from reads; ManuallyDrop rejection golden property owner differs from observed helper owner.

## Applicability

Independent static delta review and all-G1 std/core-wrapper sweep. Verify claims in /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/g1r3/SWEEP.md SHA256 7764b6a06425734f092e0724e1a96788523ea63f683392aa86808534f02b8809 independently. Inspect package A3 RUN-REQUEST.json, TEST-MANIFEST.json, STATIC-CHECKS.json, APPLIED-INVENTORY-A3.json and preflight-a3.json under /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/g1r3; Rust sources at /tmp/kani3300-g1r3-rust-source and /tmp/kani3300-g1r2-rust-source, hashes in /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/g1r3/RUST-SOURCES.json SHA256 e2b1672ac9a31b71b821c006a0ad3a7f32b93a17c807f4e319f4ee431185a9ff. No compiler/native results exist for this candidate.

## Invariants
- Production must remain identical to 3d085249c9c6c49a9c2e5747e2167d629748fb70; only four mem::forget calls and one golden owner may change.
- Four moved-from u32 reads and negative golden/70 harness outcomes must remain intact; direct intrinsic path must avoid unintended G2 and preserve modeled Move invalidation.
- ManuallyDrop<U> test remains an intentional G2 rejection; only exact owner/index changes, with same reason/FAILURE/harness/summary.
- Find unintended std/core union wrapper paths across all G1 fixtures; intentional rejection fixtures remain controls.
- A3 only the two task selectors; full unchanged P1+G1 production against f046; selected source/golden/helper bytes equal candidate. B untouched. Timeout<=5 and proposal (5+30)*0.0135<=0.476; Cloud $0.

## Required controls
- No nested delegation; no cargo/rustc/Kani/CBMC, build/dispatch/Cloud, raw evidence/credentials, Kani push, external messages.
- Read-only investigation; write only /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/g1r3/REVIEW.md. Do not edit tests/production/packages.
- Report concise findings, exact candidate/spec/packet and sweep identities, static limitations; no GO or proof credit.

## Declared dependencies
- `tests/expected/uninit/g1-union-pointee-negative/main.rs` → `dependencies/0000.bin` (mode 100644, SHA256 d1f94363c8e22bc557ba1ed95af569098ff4fb3530be1245078d9e7a00b6b1d2)
- `tests/expected/uninit/g1-union-pointee-positive/main.rs` → `dependencies/0001.bin` (mode 100644, SHA256 79949e53589e9f4a7d9cc03eb589f45616293368c8f6aab87a160f53ffab9973)
- `tests/expected/uninit/g1-union-pointee-unsupported-reject_manuallydrop_union/main.rs` → `dependencies/0002.bin` (mode 100644, SHA256 e3a0d7fca86a7a015421272d1c91d59aa116d2455ebbbda7b1eb8f320a63c5f5)
- `tests/expected/uninit/g1-union-pointee-negative/expected` → `dependencies/0003.bin` (mode 100644, SHA256 2f431fb7f59942dcd747dcfaedec6fd74baf2e2ad9ca34f4ba75128afe9d9c24)
- `tests/expected/uninit/g1-union-pointee-unsupported-reject_manuallydrop_union/expected` → `dependencies/0004.bin` (mode 100644, SHA256 c666dad05d345f6b0932d7cac65bba899867479a507911a47b34fea2c37b0dfe)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0005.bin` (mode 100644, SHA256 716461812b3ff9c405bbc0bdf4c4760dd19dc9635ca5384d1ab2d67c0044fea1)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0006.bin` (mode 100644, SHA256 31eab7bff7382d187879547501690eeab5cfada36a1b72e1f182d9008968357b)
- `rust-toolchain.toml` → `dependencies/0007.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Compilation and native verification NOT_RUN. Static inspection cannot establish per-harness results or independent B1/B2 credit.

Do not execute source or evidence from this packet. Do not claim new proof credit.
