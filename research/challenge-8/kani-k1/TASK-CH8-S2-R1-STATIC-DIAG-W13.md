# W13 — S2 r1 static compile-diagnosis

ISSUED by coordinator after owner report 13:35. Correctness verification, not
security work. Fresh/current model+Fast, no subagents. STOP only for a real blocker,
not volume/context. No compiler, cargo, rustc, Kani/CBMC or full runner.
Paths relative to `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.

Observed input (coordinator/ledger report, not recovered rustc diagnostic):
run44284869572/attempt1 compile FAILED27.6s, cfg gate passed, zero roots,
`Found 1 compilation errors`; stdout preview omitted16235bytes. Exact diagnostic
is absent from artifact/job log; historical cause remains UNKNOWN from evidence.
Ledger outcome40a3b47eb8. R0 run44264952389 uncharged; r1 accounting/repeat owner-only.

Exact r1 package0a4cef493f858d0e91d3ebccfbbab0b8d32d0119,
source9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6/tree64d96010b0b4b896322e26d700c253f834ba9fd6,
control2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8/treeb04ce6fd7a2c937bf72fcda7a262eef65a9f45bb,
triggerbdedeae662cf6f03dc7593638d263dec21d0a135/parent9e14e033f9ee31522b571c127609dcdff76d230b,
stock tool0aac16ef62da9e9d5645782d458593e5d78143ba. Reviewe40ac8e8dd APPROVE was
static cfg registration lookup, not successful compilation.
Use source worktree `/root/verify-rust-std-ch8-s2-cfg-r1-w13` read-only.
Only r1 source delta versus97ac is13lines sort8_registration_only at
sorting_s2_batch.rs:165+, #[proof_for_contract(sort8_stable)].

Trace actual effective cfg for all11 roots, emphasizing sorting+controls+s2_assumed:
sort8_stable requires/modifies/ensures, old() captures, pointer/value types and
closure capture/return shape; merge_contract_regions_disjoint definitions/imports;
sorting_s2_span module/functions and their cfg availability; registration harness
call arguments/types and contract-macro references in stock tool. Compare provider
and consumer cfgs and 97ac/r1 delta. Reuse CFG-PFC-MAP and ROOT-BINDINGS, but don't
mistake name registration for contract body/type/name-resolution validation.

Return source-local evidence with exact commit:path:line/hash, active/inactive
declarations and a compact dependency/cfg table. Rank concrete hypotheses and
separate established static defect from expected diagnostic and UNKNOWN historical
runtime cause. Missing diagnostic cannot be reconstructed as observed evidence.
Give minimal proposed repair as text/diff NOT_APPLIED and the exact future retained
diagnostic/compile result that would distinguish hypotheses. No source/control edits
or new source candidate, no weakening summaries/contracts or new proof credit.

Write only `kani3300/ch8-s2/r1-static-diagnostic/`: REPORT.md/json, source/cfg map,
PROVENANCE/MANIFEST, HANDOFF.md. Compact, no broad new audit/test suite; read-only
Python/static checks if useful. W11 independently owns runner capture changes in
another worktree/output; do not edit its files. Reviewer14 receives exact committed
report when ready. Old candidates/reviews/postrun/ledger immutable.

No CI/rerun/cancel/push/PR/ledger/reservation/budget or compiler/verifier/full runner.
Item1 28/28,item2 provisional10/14,total38/42; r1 charge owner decision, no assumed
next attempt/accounting. Exact ownpaths commit --only, `[skip ci]`, author
Tiramisu-Cake <igkharin@gmail.com>. Final `READY <full g0 SHA> <static finding summary>`.
