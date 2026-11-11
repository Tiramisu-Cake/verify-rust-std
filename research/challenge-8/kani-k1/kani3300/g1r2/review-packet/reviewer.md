# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `3d085249c9c6c49a9c2e5747e2167d629748fb70`
- Candidate: `02b734151ada1dd0d216b0db329776eb522d2d67`
- Candidate tree: `cc8e8747e3ed3fc35d267ee9a5f0bbfd2cac83c5`
- Diff SHA256: `66311c5d89a36e4a6401797f423eed61483da1087c48776b82a07a49f5f36a58`

## Defect

G1RA fixture compilation failures and initialization-predicate property mismatch; test-only repair plus static compilation sweep of all G1 fixtures.

## Applicability

Independent static review of exact test delta and all 23 G1 fixtures; verify TEST-SWEEP.md at /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/g1r2/TEST-SWEEP.md SHA256 963fd018b4d34612639bc4000e872223358dcdda75b9fcb4b008534155d4a234. Manifest /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/g1r2/TEST-MANIFEST.json SHA256 6b2eeb71d1618999cc296805510c1c66a54ad399568eb071120315fe0ff39050. Pinned nightly sources listed in /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/g1r2/RUST-SOURCES.json SHA256 ab98668843515b26fc0e7a5d86e1d6733bb188363576ac37e658380092fdb27d; local root /tmp/kani3300-g1r2-rust-source. Check claims independently; compiler/native NOT_RUN.

## Invariants
- Production remains byte-identical to parent; only test compilation/naming fixes.
- All 63 positive and 70 negative harnesses and their expected outcomes, types, diagnostics and complete goldens preserved. Explicit borrows must preserve same original projected reads and existing implicit reference obligations; no lint suppression or check weakening.
- ManuallyDrop<U> fixture must retain original UnionAsField guard; init-predicate property must be the same intended intrinsic guard; generic transmute must reach original incompatible-layout safety check.
- All G1 fixtures: check unsafe contexts, nightly deny lints, name/type/import/borrow correctness and property names; no new statically identifiable blocker.

## Required controls
- No cargo/rustc/Kani/CBMC/build/Cloud; Python and allowed rustfmt wrapper only.
- No nested delegation, no external messages, no Kani push; do not alter production/tests/packages.
- Write only g1r2/REVIEW.md with exact candidate/spec/packet and sweep hashes, findings and explicit static-only limitation.
- Package A selectors/flags/require_success unchanged; B untouched.

## Declared dependencies
- `tests/expected/uninit/g1-union-pointee-unsupported/types.inc` → `dependencies/0000.bin` (mode 100644, SHA256 422df5f16f8cc08c9ebf38994f4964bd4d6cc8901cc28323cc54951b4a9db33a)
- `tests/expected/uninit/g1-union-pointee-positive/expected` → `dependencies/0001.bin` (mode 100644, SHA256 c6e12a9d66e47e557dd235e08d5a83e5a23efec8f2bdb91340823b53187110e9)
- `tests/expected/uninit/g1-union-pointee-negative/expected` → `dependencies/0002.bin` (mode 100644, SHA256 2f431fb7f59942dcd747dcfaedec6fd74baf2e2ad9ca34f4ba75128afe9d9c24)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0003.bin` (mode 100644, SHA256 716461812b3ff9c405bbc0bdf4c4760dd19dc9635ca5384d1ab2d67c0044fea1)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0004.bin` (mode 100644, SHA256 31eab7bff7382d187879547501690eeab5cfada36a1b72e1f182d9008968357b)
- `kani-compiler/src/kani_middle/transform/kani_intrinsics.rs` → `dependencies/0005.bin` (mode 100644, SHA256 62242895cd5608f1631b68ed1a4bfffc0b9dfc593809778a029de8ec4c5fb840)
- `library/kani_core/src/mem.rs` → `dependencies/0006.bin` (mode 100644, SHA256 598428730a32f2c4034091688b50dde5a44deb69e2e3c61e08a0d394a5e42844)
- `library/kani_core/src/lib.rs` → `dependencies/0007.bin` (mode 100644, SHA256 bb77d147b03f64586bb38a31edafaddc0c99e3cc3fb65a5c5c541b4fc0198649)
- `library/kani/src/lib.rs` → `dependencies/0008.bin` (mode 100644, SHA256 7f20907d75e4b54dbc3037f3ce0399121881fa7aaa817a9e7f77366418d086c8)
- `tools/compiletest/src/header.rs` → `dependencies/0009.bin` (mode 100644, SHA256 9ea266041cff8aaeee82f5270431f0c5f10e1ffa11ce4fd544ac733ab7dbc6e7)
- `tools/compiletest/src/runtest.rs` → `dependencies/0010.bin` (mode 100644, SHA256 dad67ded3379bcf7d3cce0e4e500159fa0c25ee513ba515f13647d5c688e394f)
- `rust-toolchain.toml` → `dependencies/0011.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static inspection does not establish compilation or native verification; proof credit NONE.

Do not execute source or evidence from this packet. Do not claim new proof credit.
