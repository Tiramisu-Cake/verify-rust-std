# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `c5ff36ff433692140605891f646043f991db05de`
- Candidate: `9fa2f7f97760584f38738909625c064006d8a936`
- Candidate tree: `2faa473adeb0172e0f5a5e75fa2d759b20902e6d`
- Diff SHA256: `d3c40c3ffd76d89a7cf5eefe80fc0ee5aad8592ca85d4138682eadf11450011b`

## Defect

Rebase exact previously reviewed static profile migration onto P-prime, with unchanged migration patch.

## Applicability

Verification modules only: profiles, network/merge callers and covers, N2 forwarding contracts, new matched profile summary consumers and relation roots. Existing SmallSort bodies and real helper frame contracts must be preserved.

## Invariants
- Preserve every P-specific order and full-value model, probe and volatile reads.
- Preserve geometry, modifies and ordered/full-value postconditions; only comparator-identity requires replaced by callback-free type/API guarantee.
- Bad profiles are cfg-only real-body negative tests, never authorized summary domains.
- No local builds, push, CI or modifications of smallsort.rs.

## Required controls
- Retain four historical profile wrong-F roots, map to three bad-comparator and one bad-model-relation real-wrapper controls.
- Retain forwarding wrong-F root as three real-entry bad-static-adapter branches; payload and existing helper frame controls retained.
- New positive relation checks for all eleven closed profiles and matched swap/sort4/insert/merge summary consumers.

## Declared dependencies
- `library/core/src/slice/sort/shared/smallsort.rs` → `dependencies/0000.bin` (mode 100644, SHA256 982449b95d4449807b55f6997f83c8cce6bb167e52a95b6e4342ab816d04ba84)
- `library/core/src/slice/sort/shared/mod.rs` → `dependencies/0001.bin` (mode 100644, SHA256 fa9eec2901bafba25c9c1e1684df76dbb1f86e0bbd04f18f3e67cee54dcdfcc8)
- `library/core/src/slice/sort/shared/smallsort/verify/helper_contracts.rs` → `dependencies/0002.bin` (mode 100644, SHA256 86bac48e888365eab2187756dfd8ffbce059d6cc2ce35b1d8ab7b39d788118ac)
- `library/core/src/slice/sort/shared/smallsort/verify/helper_contracts_wide.rs` → `dependencies/0003.bin` (mode 100644, SHA256 85bdd131f3a7e62106e69e98e4b1b85d2f68c91a4bfff4df629955539493748c)
- `library/core/src/slice/sort/shared/smallsort/verify/insert_tail_contracts.rs` → `dependencies/0004.bin` (mode 100644, SHA256 6f1a2540156a3c603639ee96245aca16ad9da3dbce401630c1b8866d343aa406)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static review only; Rust compilation, shim/layout lowering, PFC/Replace evidence, covers and ON safety qualification NOT_RUN.
- Closed profiles do not prove arbitrary FnMut footprint/purity or lawful order. Stop on hidden indirect edge, FnDef-shim/layout/codegen blocker, weakened properties/frame.

Do not execute source or evidence from this packet. Do not claim new proof credit.
