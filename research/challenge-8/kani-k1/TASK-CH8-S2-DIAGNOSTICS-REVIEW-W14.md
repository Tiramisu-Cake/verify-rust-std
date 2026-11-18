# W14 — S2 static diagnosis / runner diagnostics delta review

PREPARED_NOT_ISSUED. Coordinator supplies exact committed author pins and selects
one scope per turn. Review first READY without waiting for the other; if active,
queue the second, never reset active work. Fresh/current model+Fast, no subagents.
Correctness verification, not security work. STOP only real blocker, not volume.

Contracts: TASK-CH8-S2-R1-STATIC-DIAG-W13.md and TASK-CH8-RUSTC-DIAGNOSTICS-W11.md.
Old source9fd/control2ec/package0a4cef/reviewe40/run44284869572 are immutable;
historical rustc diagnostic/cause UNKNOWN. No new compiler/toolchain audit.

Scope A, static report13: independently check concrete contract/cfg/name/type
claims at frozen source/tool pins, including old(), requires/modifies/ensures,
merge_contract_regions_disjoint, sorting_s2_span and13line registration call.
Check strength/provenance: source-local established vs hypothesis vs absent runtime
diagnostic; proposed repairs NOT_APPLIED. No source edits, no invented error text.
Output `kani3300/ch8-s2/r1-static-diagnostic-review/`.

Scope B, runner delta11: exact control parent/tree/diff/hash bindings, independent
preview-independent stdout/stderr error retention and context, chunk/ANSI/EOF,
explicit partial/resource exhaustion, normal/failure/fallback/packing boundaries,
meaningful long-middle regression and affected service error controls. Preserve
all native outcomes/proof/selection/source/tool/resource caps; no unsafe complete
claim or raw/unbounded artifact. Runtime production NOT_RUN. Check baseline-vs-new
test distinguishes the original loss; run only necessary Python/static checks.
Output `kani3300/ch8-s2/runner-diagnostics-r2-review/`.

For each output: REVIEW.md/json, validation/provenance/hashes, findings with original
owner13 or11, HANDOFF, APPROVE/CHANGES_REQUIRED with limits. Local findings return
original owner via coordinator; immutable new repair and same reviewer delta review,
preserve old outputs. No author implementation edits by reviewer. Both approvals
lead to coordinator handoff only; compile cause and future runtime stay separate.

No CI/rerun/cancel/push/PR/compiler/verifier/full runner/source/ledger/reservation/
budget changes. R1 charge/repeat owner decision, no presumed next run number.
Paths from `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.
Exact ownpaths commit --only, `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>.
Final `READY <full g0 SHA> <scope> <verdict>`.
