# C2 Gate B′ replay — ACCEPTED (run 43683557088)

2026-11-15, coordinator. Kani C2 freeze `ad499e41dd` / tree `9829702c1a`; dispatch `6376c3cb3f` (= worker15 `0d6282ad1`
minus other workflows, see COORDINATOR-DISPATCH.md). Std `70ba5befc6`, test-only overlay patch SHA-256 `af2d6e7b…`
(identical to C1 Gate B′), request SHA-256 `9723c477…`. ubuntu-24.04, 3 serial jobs. Kani 0.68.0, CBMC 6.11.0.
Every receipt: C2 source binding valid (504 files, 6 subtrees) and std test-only overlay valid after the run.

| Row | Result C2 | C1 (run 43600834435) | exit / time / max RSS |
|---|---|---|---|
| merge-raw-closure-on | **SUCCESS**, 0 of 572 failed (16 unreachable), covers 5/5 | 0 of 570 (16), 5/5 | 0 / 156 s / 2291 MiB |
| merge-profile-closure-on | **SUCCESS**, 0 of 1030 failed (68 unreachable), covers 2/2 | 0 of 1028 (68), 2/2 | 0 / 186 s / 2606 MiB |
| sort4-closure-on | **BOUNDARY**: 1 of 760 failed — only `hint::select_unpredictable::<*const u64>.unsupported_construct.1` (hint.rs:871); covers 2/3, "sort4 returns" UNREACHABLE | 1 of 758 (47), 2/3, same | 1 / 46 s / 4820 MiB |

## Check-by-check comparison with C1

Per row, every check (property name + description → status) was compared with the C1 stdout of run 43600834435.
The only difference in all three rows: two new checks, both SUCCESS —
`kani::internal::enter_contract_clause.assertion.1` ("attempt to add with overflow") and
`kani::internal::exit_contract_clause.assertion.1` ("attempt to subtract with overflow").
Origin: upstream #5093 (`2ec6953d9`, in the C2 base, not in C1) replaced `saturating_add/sub` of the contract-clause
depth with guarded arithmetic. No check lost, no status changed, unreachable counts unchanged, all covers as on C1.
In both merge rows each `unsupported_construct` property is SUCCESS (not reached), as on C1.

## Verdict

Planner criteria (TASK-KANI3300-C2-GATEB-REPLAY.md) hold: both merge rows SUCCESS with all covers, sort4 at exactly the
named `select_unpredictable` boundary with no comparator/layout/uninit/frame failures. Receipt `outcome=UNKNOWN` reviewed
here. Scope unchanged from C1: these bounded geometries/targets only; the concrete profile companion does not re-prove
the generic fn-pointer `merge_profile<P>`; sort4/swap_if_less stay blocked on `select_unpredictable` (SEL1, separate).
No proof credit or publication authorization follows.

Files: `run-43683557088/<row>/{receipt,export,runtime-identities,job-status}.json`. Stdout SHA-256 prefixes:
merge-raw `9641f1d4ccb5d10e`, merge-profile `b30497dacea65624`, sort4 `e5bacd3b53a66e55` (stdout kept in run artifacts, 14 days).
