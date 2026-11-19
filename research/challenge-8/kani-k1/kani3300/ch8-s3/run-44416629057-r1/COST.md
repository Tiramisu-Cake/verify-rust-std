# Cost and censoring

| Root | Compile upper bound s | Native verification s | Child elapsed s | Sampled PGID max KiB | Termination |
|---|---:|---:|---:|---:|---|
| checker_order_corrupt | 34.621 | 0.047798802 | 34.801 | 1926164 | completed |
| checker_count_corrupt | 35.267 | 0.366425888 | 35.763 | 1946768 | completed |
| s3_swap_u8_geometry | 34.816 | 27.29707652 | 62.995 | 1932796 | completed |
| s3_sort4_u8_separate | 36.017 | 78.983176885 | 120.782 | 2566336 | completed |
| s3_sort4_u8_same_alloc | 36.942 | 212.237510446 | 254.769 | 2297976 | completed |
| s3_insert_tail_u8_rel16 | 34.680 | UNKNOWN | 112.349 | 6326988 | rss_cap |
| s3_merge8_u8_separate | 34.998 | 150.963607091 | 191.767 | 2572460 | completed |
| s3_merge8_u8_same_alloc | 35.105 | UNKNOWN | 600.205 | 2558128 | timeout |
| sort13_weak | 34.782 | 0.103120149 | 35.027 | 1924228 | completed |


Campaign elapsed1454.135514967s; all nine launched serially and all nine sealed. Native job22:59:00–23:31:25Z on2026-11-18. Validate149s, source identity5s, tool setup68s, once-only tool build259s, roots step1455s (second-resolution GitHub metadata). Setup and build succeeded; roots step failed. Campaign SELECTED_PARTIAL/native workflow failure is separate from each root verdict.

Compile values are upper bounds for STD_PROJECT_COMPILATION_AND_LINK_UNTIL_INITIAL_EXPORT, not compiler CPU and not exact exclusive compilation. Native verification values are stock per-harness resources. Symex/backend phase times/steps/VCC and per-root component RSS are UNKNOWN_NOT_EXPORTED. No whole-child or censored duration is labeled native verification time. No matched speedup claim.

insert_tail: execution.termination_reason=rss_cap, timed_out=false,112.349s; original exit-15/signal15, verified child shutdown, worker exit0 and containment verified; next merge8separate ran. Local sampled PGID max6326988KiB exceeds cap6291456KiB (overshoot35532KiB); outer sampled peak6344420KiB is below12582912KiB. Exact runner loop samples RSS, updates maximum, then breaks on the first value above cap; thus6326988KiB is the reconstructed triggering RSS sample. RSS at subsequent SIGTERM/kill and precise phase are UNKNOWN. Compilation boundary was already observed at34.680s; backend component sampled max6312480KiB is a non-simultaneous component peak, not an independently timed kill-phase measurement.

merge8same: execution.termination_reason=timeout, timed_out=true,600.205s; original exit-15/signal15, verified child shutdown, worker exit0 and containment verified; sort13weak ran next. This is whole-child600s including the35.105s compile upper bound, not CBMC verification600s. PGID sampled peak2558128KiB; RSS at trigger/kill UNKNOWN. No local RSS breach, supervisor cutoff, slot720 cutoff or outer/global stop is recorded. The compile180s subcap was not the trigger for either leaf. Supervised worker limit710s plus publication reserve10s fits slot720s. Neither campaign6900/outer7500 nor phase8100/global caps fired.

All containment/cleanup records and original exits are preserved in COST.json. Polling is non-atomic PGID VmRSS (0.05s); component peaks are by comm and non-simultaneous; outer census is another sampling scope. None is a true kernel/cgroup/tree peak. Unfinished verification durations are censored and cannot be recovered by subtracting compile from elapsed. 600 minus compile upper bound is envelope arithmetic only, not a phase duration.
