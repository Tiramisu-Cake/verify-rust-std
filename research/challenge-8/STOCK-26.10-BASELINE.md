# STOCK-26.10-BASELINE — BEFORE card

2026-10-08. Owner explicitly resumes this named phase after Git synchronization.
Own branch `research/stock-26.10-baseline`, parent
`a06cfb9d9dd95cf5a8875bd5d2f9bd85df47fadd`; included upstream/std
`cd371e035c7e573760c43bf934d53e8118ee3e7d`. Sync/source branches and main stay fixed.
Separate ceiling **1800 GitHub-hosted job seconds**, including setup and artifacts.
Old account **5306/5400, 94 remaining** is untouched; S7c **UNACCEPTED**.

## Obligation, hypothesis and frozen profile

Actual obligation advanced: `core::mem::forget<T>` at mem/mod.rs193–195,
exact body `{ let _ = ManuallyDrop::new(t); }`. It is unchanged textually from the
old experiment. This tests a minimal unsafe generic adapter with the previous
explicit contract, not a safe generic-forget summary or actual guard linkage.

Hypothesis: unmodified release26.10 supports isolated scalar/raw-pointer bodies
through export/decode/refinement/full proof; on the new compiler/std, the exact
forget adapter either passes the complete gate or reveals a fresh, diagnosable
failure. The old physical residual key52 and old CFG remedy are not presumed.

Profile `stock-26.10-baseline-v1`: VF source/tag26.10
`f76012fb518703b1d98e243ac4f487f16877cfcb`, release archive SHA256
`5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd`,
Rust nightly-2026-09-25, target x86_64-unknown-linux-gnu, Ubuntu22.04 hosted.
Effective patches **NONE**. Stock exporter, integrated decoder/translator and
refiner come from the same release; decoder wire schema comes from the exact
source pin, SHA256 `f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469`.
The release/source provenance is trusted; source components and actual binaries,
all effective stock specifications, rustc commit/sysroot are recorded on runner.
Stock specs are compared bytewise to the exact VF source. No console rebuild.

The fixture body is extracted textually from repository std; external std calls
are exported using the nightly sysroot crate metadata. This is not a build/export
of repository std. Runner records repository and rust-src hashes and their actual
agreement/difference, so this limitation cannot be hidden behind the nightly label.
Repository mem SHA256 `b86a596a58dcb21a45e8b29b33327ca8c7bde708aa6fca158d4366e51403daf2`;
ManuallyDrop `f9cce798828cc852c00feeea9a6218c225b68d92727a5edbddc7c08a731a4f25`;
SmallSort `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`.

## Complete fixture contracts and controls

All clauses are in separate block annotations, ghost-stripped original source is
retained, and hashes are checked before/after every stage. `tid == currentThread`
is part of every precondition below. All `T` are unrestricted sized Rust types;
no Freeze/Copy/purity additions. Full normal/unwind contracts:

| Fixture | Domain and precondition | Normal post | Unwind post / expected obligation |
| --- | --- | --- | --- |
| u32_positive, stock_u32(x) = x | all u32 x; thread_token(tid) | same thread token, result == x | false; full verifier exit0/body/return/leak/dead-code |
| raw_positive, stock_raw(p) = *p | valid initialized u32 slot, full `*p |-> v`, thread token, pointer provenance/permissions carried by the resource | same slot/value and token, result == v | false; full verifier exit0/body/return/leak/dead-code |
| u32_false_post / raw_false_post | same respective pre and body | same resources & false instead of result equality | false; intended `Cannot prove false` at normal ens line6 |
| u32_contradictory_pre | u32 pre & false, same nonempty body | original full normal post | false; expected mandatory dead-code rejection for skipped stock_u32 body, no early frontend failure |
| forget_positive | arbitrary T by value; thread_token(tid) | same token | false; exact generic body, full gate or first blocker |
| forget_false_post | same T/pre/body | same token & false | false; intended `Cannot prove false` at ens line9 |
| forget_contradictory_pre | same T/pre & false/body | same token | false; intended dead-code rejection for skipped adapter body |
| potentially_panicking(b) | all bool b, token; panic if b | same token | same token; actual callee body checked before caller in same unit |
| ordinary_unwind | bool b, token; calls checked callee | same token | same token; actual normal/unwind ReturnStmt paths must execute |
| false_unwind | same caller domain/body | same token | false; intended `Cannot prove false` at caller unwind line23 |
| shared_cleanup<T> | bool b, arbitrary T, token; MD::new then checked potentially-panicking call | same token | same token; verify actual cleanup predecessors and both AST returns |

First scalar/raw fixtures run before forget. All eleven are isolated units; no S6
predicates/helpers are inserted. Failures do not prevent independent later units.
Each unit records NORMAL export/decode, readonly export/decode, full verifier and
refinement independently. AST-with-locs is captured by the stock console; there
is no separate standalone translator binary stage. Full proof means actual timed
body headers and body/return/leak traces, exact ordered stock-prelude functions
u32_sync/u32_share_mono/init_ref_readonly_points_to_shared plus target functions,
no focus, exit0, no dead code. Unwind positives also require observed actual AST
unwind/normal returns, not just full exit0. The old strict classifier is unchanged;
its raw classification is saved. Contradictory-pre tests have a separate explicit
mapping requiring exact body span, no target body execution, exit1 and frontend0;
they are deliberately unreachable controls, never positive proofs.

## Outcome decisions and dispatch bound

- Setup/export/decode/refinement or unrelated proof failure: record first causal
  stage, fix only a concrete harness issue; this is not an intended negative.
- Full scalar/pointer positive and intended controls: stock chain operational in
  that domain only. Continue exact adapter/independent unwind controls.
- Adapter dead code: inspect new complete MIR, AST, stock source/console diagnostic.
  State structural inference separately from physical-loc attribution. No tracing
  patch or semantic CFG change is authorized in this phase.
- Missing S6 rules: source-based migration plan, not adding predicates here.
- Semantic rejection repeats: no identical re-run. A new run needs a new
  falsifiable hypothesis or exact harness repair, plus budget and artifact reserve.

First dispatch uses existing workflow API selection
`proof=verifast_maybeuninit_new_pointer`, `forget_guard_stage=forget_generic_ast`,
`budget_minutes=30`, routed only on our new branch to job `stock-2610`.
Research trigger remains **workflow_dispatch only**. Other historical jobs skip;
a skipped job is not verification. Exact source SHA is resolved after commit and
remote equality before dispatch. Job ceiling10min=600s; inner deadline540s leaves
60s for artifacts/cancellation, fixture deadline530s. First run has1800s available;
remaining budget must be recalculated from actual job started_at/completed_at.
No actual-call redirect, ownership guard, assume_init, pointer-drop/memory/unwind
model extension or patch transfer. Deliverable is stock evidence + transfer plan.
