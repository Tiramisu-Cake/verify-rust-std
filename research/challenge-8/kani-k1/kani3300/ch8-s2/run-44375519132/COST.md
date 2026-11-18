# Scoped costs — source-reported observations

Seconds; `None` means UNKNOWN/not exposed, never zero. Child wall includes compilation and native verification. Worker wall additionally includes worker setup/snapshots/cleanup; compile polling bound is not exact compile duration. RSS is sampled child PGID VmRSS; component peaks are non-simultaneous, outer samples sum observed owned PIDs; neither is a strict tree/kernel/cgroup peak.

| Root | Compile state | Cargo dev reported s | Compile upper bound s | Child s | Native verification_time_s | Worker s | Child sampled KiB | Child termination |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| checker_order_corrupt | COMPLETE | 28.73 | 29.248 | 29.363 | 0.040254686 | 35.13111059999994 | 1930636 | UNKNOWN |
| checker_count_corrupt | COMPLETE | 28.56 | 28.653 | 28.998 | 0.2798136 | 34.71848949499997 | 1927340 | UNKNOWN |
| swap_pfc | COMPLETE | 29.12 | 29.546 | 45.777 | 10.680759458 | 51.50536875 | 2502640 | UNKNOWN |
| sort13_weak | COMPLETE | 30.0 | 30.095 | 30.266 | 0.084462405 | 35.97690506799995 | 1927020 | UNKNOWN |
| merge32_real | COMPLETE | 30.43 | 30.879 | 600.177 | None | 605.942332669 | 2522868 | timeout |
| sort13_assumed | COMPLETE | 28.71 | 29.164 | 600.179 | None | 605.9139254569998 | 2540336 | timeout |
| merge_count_corrupt | FAILED | None | None | 0.695 | None | 3.5610636140004317 | 912060 | external_signal |
| merge_order_corrupt | NOT_STARTED | None | None | UNKNOWN | None | UNKNOWN | UNKNOWN | NO_INVOCATION |
| summary_witness | NOT_STARTED | None | None | UNKNOWN | None | UNKNOWN | UNKNOWN | NO_INVOCATION |
| general32_assumed | NOT_STARTED | None | None | UNKNOWN | None | UNKNOWN | UNKNOWN | NO_INVOCATION |
| general32_weak | NOT_STARTED | None | None | UNKNOWN | None | UNKNOWN | UNKNOWN | NO_INVOCATION |

merge_count child0.695/912060KiB comes from compile/receipt.group_execution only; group receipt lacks final execution. Worker exit-15/supervisor_exception differs from native child exit1/interrupted_by_signal15/signal=null. Worker3.561s and campaign1372.897s are different scopes. For merge32/sort13: child600.177/600.179, original_exit-15, SIGTERM15, timed_out=true/termination=timeout, matching after snapshots and verified cleanup; next root continued. External600 includes compile180 and is **not** backend TIMEOUT600. No local RSS cutoff recorded. swap peak2502640KiB=2.3867034912109375GiB for entire singleton driver, not solver-only/per-root true peak; verification10.680759458s excludes compile and other driver work.

Bounded native metric fragments in COST.json retain exact member/pointer/preview-line: merge32 observed Symex4.1702s,148505 steps,23019 VCC→8165, equation0.193017s, SSA0.959045s; sort13 Symex7.69945s,250671 steps,22555 VCC→3124, equation0.128154s, SSA0.690125s. Multiple solver/decision-procedure Runtime values are retained individually, not summed into a full root solver phase; unfinished and omitted intervals UNKNOWN. Other roots' aggregate instrumentation/symex/solver/VCC/steps are UNKNOWN where not retained. No subtraction or general32 extrapolation.

Actual setup receipt: setup_total703.3546853065491s (includes early setup/checks), tool build child242.444s, exit0, peak1451656KiB. Native job2087s; Validate synthetic step95s; setup action352s; build step243s; campaign step1373s. These overlapping scopes are not added or relabelled as proof. Full native step timestamps/durations in COST.json.

Limits: child600s with compile180 inside, stock CBMC harness ceiling600s; slot720s = supervised worker710 + durable reserve10, controller180, cleanup240, campaign6900, outer7500, phase8100, step7560 (126min), setup1800, job180min. Serial planned order in ORDER.json. 9×720+180+240=6900; global remaining budget reserves later slots without reset. RSS local6291456KiB (6GiB), outer12582912KiB (12GiB), headroom2097152KiB (2GiB); sampled limits with possible overshoot. Aggregate stdout16777216B, stderr1048576B, export8388608B, total artifact268435456B. Compact gzip8MiB/uncompressed32MiB. Checkout depths control/source/tool7/5/2. Compile/selected/deferred distinctions and cleanup signals remain explicit in COST.json/SNAPSHOT-STOP.json. No observed global cap caused this stop.

Accounting is owner-reported reference only: ledger1085e94c8c1b6df072721c47abd8632b1600ecb2, item1 30/30, item2 11/17,total41/47. Intake has no charge/refund/reservation or ledger authority; no records changed.
