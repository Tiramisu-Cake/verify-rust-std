# Observed cost and phase boundaries

[github-jobs.json](github-jobs.json) retains connected metadata timestamps. Validate21:52:34–21:55:03Z; source check21:55:08–21:55:13Z; tool setup21:55:13–21:56:32Z; tool build21:56:32–22:01:43Z; roots step22:01:43–22:02:24Z on2026-11-18. All setup/check/build steps succeed; roots step fails. Job21:52:30–22:02:29Z. Timestamp precision is seconds.

| Observation | Value | Exact scope |
|---|---:|---|
| Build receipt execution |310.365s|setup/receipt.json /elapsed_seconds; original exit0 |
| Aggregate setup clock |550.7530262470245s|includes validation/checkout/setup/build; not compiler time |
| Campaign roots phase |41.2439071s|controller + worker, not native verification time |
| Worker supervision |40.77790262199994s|worker process and lifecycle envelope |
| Driver execution |40.437s|compile + native execution; original exit1 |
| Compile marker upper bound |40.32s|STOCK_INITIAL_EXPORT_OBSERVED, state COMPLETE; not precise compiler CPU/wall time |
| Native harness start |monotonic612.61318214|observed stock stdout header; campaign start571.717808659 |
| Native export wall_time_s |0.129903507s|native export scope |
| Native verification_time_s |0.045636733s|export harness resources, source-reported |
| Driver sampled PGID RSS |1927052KiB|non-atomic VmRSS at0.05s samples |
| Outer owned-process sampled RSS |1950184KiB|polled observed owned PIDs |
| Cleanup |0.011897822000037195s|verified exclusive subreaper/PID/start-time; no signals |

Worker exit0, driver exit1, signal null, timeout false, cutoff null, supervisor_error null, orphan survivors[]. Child shutdown and outer containment are verified. The GlobalFailure is raised in controller result validation **after** the completed worker returned, not a worker kill or a native timeout. Lifecycle enumeration ENOENT and cleanup ECHILD diagnostics remain preserved in the compact member; they are not the recorded stop reason. No source/worker snapshot error is present.

Backend/symex separate time, steps and VCC are UNKNOWN_NOT_EXPORTED. Component RSS maxima are separately sampled and not simultaneous; true peak kernel/tree/cgroup RSS is UNKNOWN. Later eight selected rows are NOT_RUN, not charged inferred compile or verification time; deferred eight NOT_SELECTED. No matched historical timing pair established.

Caps unchanged: compile180s inside child600s, slot720s (supervision limit710s observed), local6GiB sampled, outer12GiB/reserve2GiB, campaign6900s, Validate18min, setup1800s, job180min. [COST.json](COST.json) records exact values, pointer-bearing compile boundary and all metadata steps.
