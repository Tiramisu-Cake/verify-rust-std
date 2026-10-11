# select/sort4 — ZST repair session CLOSED

Owner `select-sort4`; worktree `/root/verify-rust-std-select-night`, branch
`research/night-select-sort4-cloud-2026-10-09`. Phase
`SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11` is closed; no new dispatch is authorized.
Policy read: `c7ca8c467aecf10a4b53039372ee97714f854ee3`.
Start 08:33:37 / main deadline 10:33:37 / finish-only ceiling 11:03:37 UTC.

Minimal Rust size repair passed all fresh model gates: guarded generic entry
with/without unused native MU scratch; intended pre-guard false size assertions;
legal nonzero branches; concrete ZST/nonZST/MU and array/layout cases; reachable
ZST false and missing-permission negatives; unchanged C/C++ positivity controls.
Patch changes only `src/verifast1.ml`; frozen snapshot is unchanged.

Fresh native C1: verifier exit 0, 196 statements, reachable sizezero return,
full native normal/direct-unwind/early posts and intended normal/unwind negatives.
Fresh native C1–C4 fragment: Build `3b7431bb-4e18-4921-b690-307e4ba7f984`, exact
proof=infra `8de4cda418c4772009359fbb90e7e7f34836cca0`, verifier exit 0,
485 statements. All 503 registered physical IDs executed, including ZST and
len<8 returns. Four actual comparator expressions, sequential CURRENT and
full source/tail/opaque MU/F/thread/lifetime/type normal/four direct-unwind
posts, unit/free/leak/refinement/strict/dead-code gates retained. Normal and
four unwind false assertions reject at their intended locations; admissions
remain isolated/default-off. Earlier C4 inventory failures are preserved.

Qualification: experimental/unaccepted profiles; guarded internal fragment
retains the existing `T: FreezeMarker` domain of the actual scratch caller.
Full actual sort4, unrestricted generic sort4 safety, actual caller/as_mut_ptr,
guards/overflow and selector/C5/copies remain unproved/outside this session.
The research sizezero guard is not established at the actual caller.
The earlier supplied C1→C4 PASS remains a separate result.

All six Builds terminal, accounted, fully downloaded and integrity-verified.
2526/3600 conservative Cloud seconds used; unused 1074 retired, no carry.
v2 coordinator unchanged; own reservations 0, ready request withdrawn,
unresolved IDs none. Profile dispatch disabled. No automatic next session.

[Final checkpoint](cloud-build/sort4-native-c1-bound/END-CHECKPOINT-2026-10-11-ZST-REPAIR.md),
[fresh C4 review](cloud-build/sort4-native-c1-bound/FRESH-3B7431BB-REVIEW.md),
[model review package](cloud-build/sort4-native-c1-bound/MAINTAINER-ZST-REPAIR-REVIEW.md),
[C4 review package](cloud-build/sort4-native-c1-bound/MAINTAINER-NATIVE-C4-REVIEW.md),
[ledger](cloud-build/sort4-native-c1-bound/BUDGET-ZST-REPAIR-2026-10-11.json).
Next step requires a new explicit session/budget; maintainer owns review/integration.
