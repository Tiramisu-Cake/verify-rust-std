# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `5fd713a200aea3ba85edcc341f48a0a20331fce2`
- Candidate: `613c188313e34e51e6a69d2c62bbd6ded2511819`
- Candidate tree: `c37ec4b9e9a8e795d144dc48cbb72b44b8fbf78b`
- Diff SHA256: `f32ff4358900069b57015cb15d006d8106496e15764d50ab3849545d66d23107`

## Defect

Review delta fixing the initial reviewer P2: restore early zero-layout return in copy_init_state_single before pointer handling.

## Applicability

Continuation by the same reviewer. Inspect the three-line production delta; preserve conclusions for the previously reviewed candidate and explicitly record both identities. Original review in REVIEW-INITIAL.md and original packet review-packet.

## Invariants
- Typed assignment, constants, bodyful arguments and normal returns preserve source initializedness at D(T); padding destination becomes uninitialized. A false source data byte stays false.
- Raw copy/copy_nonoverlapping retain full rustc extent, padding and partial data. Flat arrays repeat D(T) at rustc stride, N>1; flat slices use slot layout.
- Unsupported layouts reject before applying any mask. Preserve existing support limits; A2 offset/layout repair, A3 call-pairing, B1 resolver work are outside A1.
- Keep nondeterministic single-byte witness coverage, overlap and overwrite semantics; capture return identities while live. No weakened existing fixture/check/contract.
- Check model ABI vs generated calls and pinned rustc_public signatures; unused/import/borrow/type concerns under -D warnings. Inspect new regression fixtures and exact failure intent.

## Required controls
- No nested delegation. No builds, dispatch, Cloud, cargo/rustc/Kani/CBMC/Miri, Actions/PR/issues/comments, raw evidence or credentials, network mutations or Kani push.
- No production/test edits. Write only a concise REVIEW.md in this A1 research directory, with exact reviewed candidate and packet identities, concrete findings, and static limitations.
- All new harness outcomes are expectations pending coordinator CI; do not claim measured proof or GO.

## Declared dependencies
- `library/kani_core/src/mem_init.rs` → `dependencies/0000.bin` (mode 100644, SHA256 9ff043b57ff6aed633815bc35a185c7cdf1a94d24356c95bb74679438081c0ce)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Compilation, MIR/Miri inspection and native verification NOT_RUN by task authorization; existing A2/A3/B1 blockers remain separate.

Do not execute source or evidence from this packet. Do not claim new proof credit.
