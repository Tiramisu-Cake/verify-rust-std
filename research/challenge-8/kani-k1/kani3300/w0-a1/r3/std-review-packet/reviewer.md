# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `65864680a145c90c583dcba7efd1d569475519fc`
- Candidate: `312ff625b9b3338281d899cca47d72c24d5a2539`
- Candidate tree: `44bf49c77a2f5157bc051002dfd8b162f36bc649`
- Diff SHA256: `cabd49c95c77060144ae1de964d5d8d3d252d29c9e12d521d3031d24f4c793b6`

## Defect

A1 child module imports the smallsort traits from verify, which only declares child modules.

## Applicability

cfg(kani_smallsort_controls), frozen std70ba plus accepted SEL1+A1 overlay.

## Invariants
- Only the name-resolution path changes. Preserve every body, assertion, cover, stub, domain, layout and unwind bound.
- No claims that this explains all8652 errors or proves compilation.

## Required controls
- Static module scope lookup and exact one-line source diff.
- No local Rust/Kani execution or CI; future coordinator firstN32 compile retains bounded diagnostics.

## Declared dependencies
- `library/core/src/slice/sort/shared/smallsort.rs` → `dependencies/0000.bin` (mode 100644, SHA256 bc8f2cd12c03ac2c4a1be231bb14d7fefef269ed0fd571e35993e6d0467c7fb0)
- `library/core/src/slice/sort/shared/smallsort/verify.rs` → `dependencies/0001.bin` (mode 100644, SHA256 f7741fde76545b53c98742149c2081c3ef6de8c7f004fe4522473cd64a611f1c)
- `library/core/src/slice/sort/shared/mod.rs` → `dependencies/0002.bin` (mode 100644, SHA256 fa9eec2901bafba25c9c1e1684df76dbb1f86e0bbd04f18f3e67cee54dcdfcc8)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static preparation only; first R1 diagnostics lost. No compile/proof credit.

Do not execute source or evidence from this packet. Do not claim new proof credit.
