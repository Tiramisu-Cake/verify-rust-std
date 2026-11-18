# W11 — preserve rustc error blocks independently of previews

ISSUED by coordinator, bounded offline implementation. Correctness verification,
not security work. Fresh/current model+Fast; no subagents. STOP only real blocker,
not volume/context. No cargo/rustc/Kani/CBMC/full runner or CI.

Owner reports run44284869572 compileFAILED27.6s/zero roots despite cfg gate PASS:
`Found 1 compilation errors`; actual error was in omitted stdout middle16235bytes,
absent from compact artifact and job log. Historical cause stays UNKNOWN. Repair
future diagnostics retention, not compilation semantics or the std source.

Baseline control2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8/treeb04ce6fd7a2c937bf72fcda7a262eef65a9f45bb,
parent9e14e033f9ee31522b571c127609dcdff76d230b. Existing read-only worktree
`/root/kani-ch8-s2-cfg-r1-w13`, runner `ch8-s1-control/runner.py`; also inspect
check_package.py, pack_evidence.py and test_runner/test_s2/error/fallback paths.
Package0a4cef493f858d0e91d3ebccfbbab0b8d32d0119 under
`/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s2/batch-r1/`.
Create isolated `/root/kani-ch8-s2-diagnostics-w11`; preserve baseline worktree.
New immutable control candidate must retain required parent9e14, e.g. apply frozen
r1 candidate patch onto9e14 then narrow delta. No CI branch/trigger/publication.

Capture every rustc textual `error[...]:` / `error:` block from actual stdout and
stderr with useful source/note/help context, regardless of whether it is in the
head/tail preview. Streaming/chunk-boundary/ANSI handling must not lose headers.
Keep stream provenance/offsets and diagnostic completeness/omission/resource fields.
Retain full required error blocks while respecting existing hard output/resource
caps; if cap/abnormal EOF makes full retention impossible, emit explicit incomplete
diagnostics and dropped counts/bytes/reason, never silent truncation or complete=true.
Do not promise all diagnostics when the producer itself omitted them. Successful
streams with no errors are distinct from spawn/timeout/output-cap partial results.

Receipt and compact group-evidence must include the new fields through normal,
compile-failed, timeout/output-cap and fallback/packing paths. Raw log exports or
unbounded dumps are outside scope. Preserve all source/tool/cfg/argv/selection,
11roots/20covers/6negative oracles, errors/native exits/shutdown/resource caps,
fallback controls and all proof outcomes. New fields are diagnostics, no proof
credit. Std9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6 and stock0aac remain unchanged.
Only necessary derived payload hashes/manifest bindings may change; no new budgets.

Offline regression tests must put errors in a long stream's omitted middle and
show old capture loses/new retains them, with multiple blocks, stderr, multiline
source/note context, ANSI/split headers/UTF8, errors near EOF and explicit cap or
termination incompleteness. Test normal/failure/fallback packing and existing
affected service error paths. Python fixture child processes/unit tests allowed;
no compiler or full runner. Use targeted existing tests, no broad unrelated suite.

Write g0 only `kani3300/ch8-s2/runner-diagnostics-r2/`: exact control SHA/tree/parent,
delta/full candidate patches, changed-file hashes, CI/request binding updates if
necessary, VALIDATION/test command/results, MANIFEST and HANDOFF. Paths from g0
`research/challenge-8/kani-k1/`. Preserve old packages/candidates/evidence/ledger.
W13 owns separate static source diagnosis; do not edit source or its output.
Reviewer14 receives exact committed delta. Runtime/CI retention in production NOT_RUN.

No CI/rerun/cancel/push/PR/ledger/reservation/budget/labels/publication. Item1 28/28,
item2 provisional10/14,total38/42; charge/retry owner-only. Exact ownpaths commit
--only, `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>. Final
`READY <full g0 SHA> <control SHA/tree> <targeted validation result>`.
