# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `bbd75af8cafbeb7906744149aed3832636494c30`
- Candidate: `1352f9d15d08cd77a1453760a254408a18f3cfb4`
- Candidate tree: `1352d0b759cb68026168f811f4de93a5a1ac4cf4`
- Diff SHA256: `a5f0990a0b22c0a3ef6ffe737cee861397f3f606d7a55ba1f0777f71c3b9aee5`

## Defect

Prepare the assigned correctness-verification harness workarounds A/B/C and PROF-ON-02 without compiler changes or execution.

## Applicability

Continuation of the same connected semantic review: localized test restoration and payload hashes only. Verify diff contains no workflow/runner/source/oracle changes; final candidate must be covered by prior semantic packet plus this test-only delta.

## Invariants
- No compiler/runtime algorithm changes, new trust, narrower input domain, weakened oracle/check/cover, or initialized true output.
- No push, CI, ledger, local Rust/compiler/verifier or raw-artifact reading. Static Git and isolated Python synthetic tests only.
- Original 62 rows retained with the extra exact-length merge4 leaf. Fresh exact row source/property/role/cover/frame binding; zero historical admissions.

## Required controls
- Inspect all changed reachable array constructors and independent generation, including B16 raw u8 any_array override.
- Compare sort4 thin writeset to old slice frame; inspect new merge4 real-body PFC and exact consumer dependency. General merge2..32 must remain unchanged.
- Check comparator factory monomorphization for every matching leaf/consumer, volatile reads and per-call nondeterminism; reject function-item carry-forward.
- Check source coordinates and frame write binding, fresh post/covers, new leaf oracle, retained PolymorphicIter rows and NOT_RUN distinctions.
- Inspect synthetic failure paths; a binding-only function is not an acceptance decision.
- Verify baseline imported package7d90 tree equals prior d569db0c package, and complete candidate tool/compiler/library sources unchanged from SEL1.
- Check control checkout depth includes SEL1 ancestor, exact control full diff/payload guards, distinct per-lane tool/std identities/features/receipts/fallback and cross-lane refusal.
- Inspect one dispatch ON→OFF with always dependency, two sequential jobs180min each/maxactive1, per-lane caps preserved and total360 disclosed.
- Synthetic paths must retain success/error/timeout/partial/missing/null/wrong-type/NOT_RUN/source-stage-target mismatch and no historical accept carry-forward. Compare reductions in test count to verify controls are retained.

## Declared dependencies
- `ch8-prof-on-control/workflow_repo.py` → `dependencies/0000.bin` (mode 100644, SHA256 e38ce725569e5f4ec66ff2d45a786099fc5f338e16e57f33369fb4f85d4bdb66)
- `ch8-prof-on-control/check_package.py` → `dependencies/0001.bin` (mode 100644, SHA256 bae459d6cf60399b350df180337ee82b0794cb63650cb26841c3a270ca97633b)
- `ch8-prof-on-control/test_workflow_repo.py` → `dependencies/0002.bin` (mode 100644, SHA256 a27f92d52bb6d51fa228ef9e512458bac5176e8e6e1e332719ac49b36a4a1f69)
- `ch8-prof-on-control/CI-REQUEST.json` → `dependencies/0003.bin` (mode 100644, SHA256 b3714a13cff56c278fc3cac9fdc8df9efc8428e63bd48496076327001556711b)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No runtime compilation, verifier execution or proof credit; actual generated closure rendering/frame variable spelling must bind afresh.

Do not execute source or evidence from this packet. Do not claim new proof credit.
