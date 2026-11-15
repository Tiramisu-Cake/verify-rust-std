# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `872d5a43380752786415bc00d2a12ce0e930cb37`
- Candidate: `ec3ff72f0b9ba925afeeb5664b2c103d61450bbc`
- Candidate tree: `7c18e1205c4c03b815f1d900e73ae67ce5e8b976`
- Diff SHA256: `9a1d10aebe4ee6d43ff9d54d4665fe3fdaae770860f8be8804aa52aa78a289c9`

## Defect

Prepare S2 actual merge32 u8 sorted+arbitrary probe-count and CAP32 invariant pilot; zero CI/proof credit.

## Applicability

Four NEW sorting_merge*.rs only. Registration and actual loop attrs only proposals to13. Model11 dependency not integrated; P1 pending.

## Invariants
- Actual merge32 calls real bidirectional_merge with KeyLess and uninitialized disjoint output; no panic or helper stubs.
- Base/arbitrary-state step/exit cover len2..32, guarded C5, fixed-query counts, reverse wrapping sentinel, odd copy, source/output frame.
- Loop pilot calls real merge_up/down but is separate from actual core for-loop; partial correctness only, no termination/extra-UB/stability/generic-T theorem.

## Required controls
- Guarded endpoint regression, sorted/count corruptions, false invariant, false frame, simple and false decreases. All NOT_RUN.

## Declared dependencies
- `library/core/src/slice/sort/shared/smallsort.rs` → `dependencies/0000.bin` (mode 100644, SHA256 982449b95d4449807b55f6997f83c8cce6bb167e52a95b6e4342ab816d04ba84)
- `library/core/src/slice/sort/shared/smallsort/verify.rs` → `dependencies/0001.bin` (mode 100644, SHA256 221226eeb818b0120a23a24ab66c20c98aae1907252d4e57a4e1048fea3e6c25)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No local Rust toolchain or proof execution. Exact model dependency supplied separately to reviewer: w11 S1 commit3f469d3ba2e94d7129e66e53ea76df883ff9c946, sorting_model.rs.
- Actual core-loop transfer not yet implemented; no summaries consumed; monolithic probe and pilot distinct.
- Tool clean0aac. APIs/source compile and loop extraction remain NOT_RUN; future P1 and exact combined head required.

Do not execute source or evidence from this packet. Do not claim new proof credit.
