# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `bf8170b28afb682f8dd55a94199caa247736d8fa`
- Candidate: `15ede35f3f6809e79a869d33482f7fc6034464f5`
- Candidate tree: `e00857811a1e9b0d1c1f6f4deb78adb9bdbc52e0`
- Diff SHA256: `029325b7288870ae1c8daa5a6b703179eb07b2d317451d858b563ee6bd464bf3`

## Defect

F6 hypothesis: nested aggregate Call destinations and actual Move sources retain stale true initialization shadow beyond the existing whole-assignment guard. Neither discriminating runtime pair has run.

## Applicability

Only C2-S3: not transfers_shadow and exact existing PointeeInfo UnionAsField; direct/accepted Item, Shim, foreign/hook calls and BlackBox; full sized extent SetRef(false).

## Invariants
- Existing top-level union/MU/flat-array/slice paired protocol, all snapshots before any source reset, return0 and pending B1 checks preserved.
- Source reset Before actual Call Move, destination reset only After normal target; no Copy/function-operand reset.
- Forget/no-effect exclusions and resolver/early Unsupported unchanged; no new recursive model or blanket guard.
- Full sized storage reset includes padding, no pointee/neighbor reset; later writes survive.
- Runtime, immutable F5, DFCC, delayed-body cache F7, SEL1, composition roots/checker/allowlist and existing fixtures unchanged.

## Required controls
- New repeated-destination and moved-from-source single-harness negatives; baseline exact base plus test-only patch must false-SUCCESS, candidate intended u8 read failure. All execution and exact property counts NOT_RUN/UNKNOWN.
- New reinit companion expected legal; custom MIR field construction/returns; repr(C) extent assumptions need actual consumed-MIR binding.
- Existing top-level move-return, call-pairing, normal-abort, ordinary/PFC, closure, cycle, immutable suites remain byte-identical.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 1371e9059e45cff62f8be3d5323cc866ce74a4e67a6f3e69bf98372462bd3853)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0001.bin` (mode 100644, SHA256 e888310d3f46c1bdbfc39a091ddeebd29c9173694da25db0132f654cbf775d37)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs` → `dependencies/0002.bin` (mode 100644, SHA256 53064d8de9417f1c2ffb33675a5679767a4e6e14052f0dfff233e38739408217)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0003.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)
- `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs` → `dependencies/0004.bin` (mode 100644, SHA256 82ce460dd51984ca62f8f9bafb4043597ae8e90c75fa4fdce0d0091681b9c2ad)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs` → `dependencies/0005.bin` (mode 100644, SHA256 6008f3aec05e33bde86720d1a4d2c71009d89390b368101d79a4d8c24afa9c3d)
- `kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs` → `dependencies/0006.bin` (mode 100644, SHA256 ad73c82580f8f9ba3528ce9b6b371c6a4f717443e31a86b1fad6bad0a2c80d64)
- `library/kani_core/src/lib.rs` → `dependencies/0007.bin` (mode 100644, SHA256 fd4936db12f998df2419b9e6240f9171643f8287654840596ea2db40cfd76bc0)
- `docs/src/reference/experimental/contracts.md` → `dependencies/0008.bin` (mode 100644, SHA256 086a178a276615522c364c306c4e7184907351809c3b9aa73aa1ea9577f208e1)
- `tests/expected/uninit/part1-composition/move-return-top-level.rs` → `dependencies/0009.bin` (mode 100644, SHA256 83d33f5c707bee9a063bab2c88e1aa1bc174c062a6785695d00a0b1b92760f48)
- `tests/expected/uninit/part1-composition/move-return-reinit.rs` → `dependencies/0010.bin` (mode 100644, SHA256 df3b5073df2c89991d25eaf48a4fa68fc06878b87b21d5adf643ede6514ffe2b)
- `tests/expected/uninit/part1-composition/move-return-reinit.expected` → `dependencies/0011.bin` (mode 100644, SHA256 1d82430f1f5fab7c8e0b0cfc64fe4119cf325f51dcd86ab6aa152462f7591a35)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No compiler/build/test/verifier/push/CI permitted. Static review only; no proof credit.
- Goldens provisional: one intended u8 payload failure per negative; actual duplicates/counts need reached-read execution. Unsupported or baseline failure cannot discriminate.
- Docs narrowing deferred. Known composition FAIL remains S5 debt; source coverage alone does not establish model execution.

Do not execute source or evidence from this packet. Do not claim new proof credit.
