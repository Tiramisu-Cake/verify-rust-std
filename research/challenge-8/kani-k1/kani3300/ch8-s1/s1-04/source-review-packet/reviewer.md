# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `f22f84f316ad8ef6f3fccce86424bad927b09f78`
- Candidate: `5be85699b8826e3286c0bf89efb9affefac0acb5`
- Candidate tree: `a9caaa953d579641ecc6a4b84b5c16fa1d23563b`
- Diff SHA256: `f135f71cc9ece1675ac5fb19a4e16cfe2b3ef9d4f50daab26f3a490dbf2f2c60`

## Defect

Four symbolic N0..3 S1 smoke roots timeout at600s; split exact-N experiment for scheduling and qualification.

## Applicability

Only bounded verification fixtures under verify/. Runtime and existing symbolic roots preserved.

## Invariants
- arbitrary bytes and KeyLess unchanged; exact PFC target
- same scratch geometry canaries independent post unwind34
- union N0/1/2/3 with all11 meaningful covers before replacement acceptance

## Required controls
- Original roots retained; fixed-N covers by applicability; no proof execution authorized.

## Declared dependencies
- `library/core/src/slice/sort/shared/smallsort.rs` → `dependencies/0000.bin` (mode 100644, SHA256 45ae77ad0bb2a74cfab1aa53d5e1c48311f0b483c94eb52d96d97f680bd39651)
- `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs` → `dependencies/0001.bin` (mode 100644, SHA256 a04f72d0a4f8c42fadc6639ead77e215dc46264096e8e998903bfe1be9ca0a18)
- `library/core/src/slice/sort/shared/smallsort/verify/sorting_entry_controls.rs` → `dependencies/0002.bin` (mode 100644, SHA256 7cb487628b9e93a086c09fc59cfc54aaeb12e12a3f917f67009f378e722d29ff)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static review only; no local Rust/Kani/CBMC permitted; runner/control integration follows separately in same review.

Do not execute source or evidence from this packet. Do not claim new proof credit.
