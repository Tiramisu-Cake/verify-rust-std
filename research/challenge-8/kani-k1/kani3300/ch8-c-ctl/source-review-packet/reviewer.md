# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `872d5a43380752786415bc00d2a12ce0e930cb37`
- Candidate: `56df5b34e4946ceddd231456737e9167a10d666a`
- Candidate tree: `2952c7b664cf04d79de31f865d185362f21f7e3a`
- Diff SHA256: `6c91318d62331536eeee62e4c8a7b2084804dda5b0cbc6451eb8bdcfd83d1004`

## Defect

Implement diagnostic C controls N1/N2/L3/L4 without widening the production C claim.

## Applicability

TASK-CH8-C-CONTROLS-W14.md; isolated A1 exception source branch outside S. Design /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-c-now/CONTROLS-DESIGN.md.

## Invariants
- Only one new cfg(kani_smallsort_controls) module and its registration may change; smallsort.rs and all models remain identical to production.
- N1 PFC real bidirectional_merge with dst-only frame, immutable raw capture made before shared source, volatile write then restore followed by live input read; lawful comparator, disjoint initialized geometry.
- N2 PFC outer frame exactly v, real helper and closure, raw alias retained before reborrow; no summaries/counters/local-temporary masking frame; legal companion differs only writes.
- L3 permits separate mutable/Cell storage explicitly in outer frame; L4 executes actual MD/guard graph and legal subsequent reuse, no escaped stale reference.
- No local rustc/Cargo/Kani/CBMC, push, CI, publication, ledger or model changes. All proof states NOT_RUN; stock N2 PASS is ALIAS_GAP, no proof credit.

## Required controls
- Eight source roots; review design adherence, geometry, PFC target, references, retained effects, reachability and false-oracle risks.

## Declared dependencies
- `library/core/src/slice/sort/shared/smallsort.rs` → `dependencies/0000.bin` (mode 100644, SHA256 982449b95d4449807b55f6997f83c8cce6bb167e52a95b6e4342ab816d04ba84)
- `library/core/src/slice/sort/shared/smallsort/verify/helper_contracts.rs` → `dependencies/0001.bin` (mode 100644, SHA256 86bac48e888365eab2187756dfd8ffbce059d6cc2ce35b1d8ab7b39d788118ac)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static and synthetic only. Exact generated property IDs, write retention and cover bindings must be established from future CI, never fabricated.

Do not execute source or evidence from this packet. Do not claim new proof credit.
