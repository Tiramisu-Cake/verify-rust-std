# C2-S3 preparation result

READY `86428e9313a8a697482bfd092de61a735a716961`

Candidate tree `146049f153dd5410d8be7a812b071147c64c2cd0`, isolated clone
`/root/kani-fix-3300-c2-s3`, branch `fix/kani-3300-c2-s3`, exact base
`bf8170b28afb682f8dd55a94199caa247736d8fa`. Clean source worktree.

The assigned destination initially did not exist. It was cloned locally from
the clean S2 source and switched to the exact base. No reset/stash, modification
of existing clones, build, push or CI was performed.

## Changes and identities

- `a328d1d897bf7382c154530db1de7c3687bc5480`: initial test-only controls.
- `15ede35f3f6809e79a869d33482f7fc6034464f5`: nested Call reset source repair.
- `86428e9313a8a697482bfd092de61a735a716961`: test-only review correction,
  eliminating unrelated callee marker reads. Earlier test-only tree is
  superseded; use the final baseline package below.

All source commits use author and committer Tiramisu-Cake
<igkharin@gmail.com> through git -c. Only visitor, necessary for_deinit size
guard and new nested-aggregate-reset fixtures changed. No runtime/immutable/
DFCC/cache/SEL1/composition changes; S4/S5/F8 were not started.

Source repair uses exact existing UnionAsField classification outside supported
shadow carriers. It resets actual Move sources after all supported snapshots,
before Call; resets exact destinations only on normal continuation. It covers
accepted Item/Shim/foreign/hook routes plus black_box, and preserves Forget,
existing no-effect exclusions and early resolver/Unsupported paths. No new
aggregate transfer protocol or blanket Unsupported was introduced.

## Separate final baseline package

Apply `baseline-tests.patch` only to exact base bf8170b28.
SHA256 `b7e778b38db68d4b31a6dcaa47c1c32b08fa40915d3435d08148c845c1679673`.
Expected tree `623062b0c7d9c9dda7a1edd52d8cb86d7c33bcc1`, also recorded in
expected-baseline-tree.txt. It contains six new fixture/oracle files and no
production repair. Sources/goldens/flags are byte-identical to the candidate.
Temporary-index apply/check and exact tree/blob comparison passed; applying
source-repair.patch on that test-only tree reproduces the candidate tree.

## Validation and limits

Allowed rustfmt wrapper and committed `git diff --check` passed. Static
Rust type/borrow/extent/order review is in REVIEW.md; this is not compiler
typechecking. Git patch/tree/blob/hash and JSON/one-harness/flag checks passed.

Local cargo/rustc/Kani/CBMC/Miri/builds, all baseline/candidate executions,
fmt suite/build/clippy, full Quick, actual consumed MIR/offset/object identity,
reached-read proof, exact emitted property/duplicate counts and composition
outcome on this candidate are NOT_RUN/UNKNOWN. Negative goldens provisionally
request one intended u8 read failure; no empirical discrimination is claimed.
The coordinator request records each required binding and stop condition.

F6 remains source-established hypothesis with an unexecuted candidate repair.
No reproduction, accepted fix, new B1/B2 proof or independent proof credit.
contracts.md is unchanged: docs narrowing waits for both discriminating
baseline/candidate pairs and complete source coverage review. Known tuple
legal stays a known false positive. Existing known composition FAIL remains
narrowly deferred S5 debt, not an all-PASS Quick or a waiver for new drift.

Research is uncommitted only under kani3300/c2-s3 in g0 at entry
959f03d10eae173389511132aa4675c7fc5aafb1. Concurrent/unrelated SEL1 research
changes were not touched or staged. No publication/dispatch/CI/Cloud spend.
