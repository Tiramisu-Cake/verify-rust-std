# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `872d5a43380752786415bc00d2a12ce0e930cb37`
- Candidate: `3f469d3ba2e94d7129e66e53ea76df883ff9c946`
- Candidate tree: `08c51f3cbe8c2e0d053001ca9ed9e5a67e3576c0`
- Diff SHA256: `723b4eb2910ecbb2096536d7cfe77d1b2a3802ba1c7e68e6ec74fe06f5bc3e46`

## Defect

S1 preparation: verification-only sorting model, named FnOnce/FnMut comparator and opt-in positive/negative checker controls for actual generic SmallSort method integration.

## Applicability

Only two new sorting_model*.rs files on std872d; exact u8/Cell<u8>/NonCopyByte with KeyLess<T>. No actual method contracts/registration changed. Worker13 integrates separately on Kani0aac.

## Invariants
- Unconditional generic facade, read-free inactive fallback, exact three active pairs, no new caller bounds.
- CAP32 owned byte snapshot, length+adjacent sortedness+full multiset post, invalid/overflow active request false.
- Stateless two-projection comparator, no runtime algorithm or signature edits.

## Required controls
- 12 opt-in roots: three N0..3 positives; inactive companion; three unsupported activation negatives; corruption companion plus order/count negatives; snapshot guards companion plus invalid-token negative. All Rust/Kani NOT_RUN.

## Declared dependencies
- `library/core/src/lib.rs` → `dependencies/0000.bin` (mode 100644, SHA256 f2145a4cf20ffdae768faabe8db8b32b67b58dd38883bb0d2bff91424dc440e1)
- `library/core/src/slice/sort/shared/smallsort/verify.rs` → `dependencies/0001.bin` (mode 100644, SHA256 221226eeb818b0120a23a24ab66c20c98aae1907252d4e57a4e1048fea3e6c25)
- `library/core/src/slice/sort/shared/smallsort.rs` → `dependencies/0002.bin` (mode 100644, SHA256 982449b95d4449807b55f6997f83c8cce6bb167e52a95b6e4342ab816d04ba84)
- `library/core/src/slice/sort/shared/mod.rs` → `dependencies/0003.bin` (mode 100644, SHA256 fa9eec2901bafba25c9c1e1684df76dbb1f86e0bbd04f18f3e67cee54dcdfcc8)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Local compilation/verifier execution forbidden. No claimed Rust/Kani qualification or six-body proof; requires combined worker13 CI.
- Independent static review requested before handoff. fn_traits and sorting cfg/module registration belong to13.
- Model is active N0..32, S1 symbolic controls N0..3; fixed N32 checker identity does not prove actual sort threshold domain.

Do not execute source or evidence from this packet. Do not claim new proof credit.
