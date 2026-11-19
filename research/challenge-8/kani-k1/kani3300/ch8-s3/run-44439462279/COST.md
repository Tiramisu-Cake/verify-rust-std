# Cost and original cutoffs

|Root|Compile upper bound s|Native verification_time_s|Native export wall s|Whole child s|Supervisor s|Sampled PGID KiB|Censoring|
|---|---|---|---|---|---|---|---|
|checker_order_corrupt|34.109|0.046604462|0.118385466|34.224|34.483192|1965000|NONE_NATIVE_COMPLETED|
|checker_count_corrupt|32.668|0.320317378|0.387259713|33.017|33.274085|1916064|NONE_NATIVE_COMPLETED|
|sort13_weak|32.726|0.086824744|0.166426565|32.899|33.16815|1977500|NONE_NATIVE_COMPLETED|
|i_p01_b1_16|33.306|UNKNOWN_CENSORED_NO_COMPLETED_EXPORT|UNKNOWN_INCOMPLETE_EXPORT|131.465|131.738788|6361996|TERMINATED_UNFINISHED_RSS|
|m8_s32_d00_allinit|32.285|197.389008141|203.999454653|236.409|236.668174|2821848|NONE_NATIVE_COMPLETED|
|i_p16_b1_16|31.836|UNKNOWN_CENSORED_NO_COMPLETED_EXPORT|UNKNOWN_INCOMPLETE_EXPORT|126.13|126.385884|6330308|TERMINATED_UNFINISHED_RSS|
|m8_s32_d00_partial_diag|30.935|195.062798708|201.518924053|232.507|232.777067|2722124|NONE_NATIVE_COMPLETED|
|m8_s40_d16_partial_diag|32.304|198.946209131|205.648633618|238.029|238.311635|2796488|NONE_NATIVE_COMPLETED|

Compile is the observed upper bound until STOCK_INITIAL_EXPORT_OBSERVED, scope STD_PROJECT_COMPILATION_AND_LINK_UNTIL_INITIAL_EXPORT; includes observation delay, not exclusive compiler CPU. Native resources.verification_time_s and native export wall_time_s are preserved with tool scope; neither is labelled exclusive symex/backend. Whole child includes compilation, verification and shutdown; worker supervision includes its own lifecycle. No symex/backend/steps/VCC phase timing is exported. Both insertion native verification durations remain censored UNKNOWN.

Campaign 1068.751379632s. Setup receipt setup_total_seconds721.402300596; build-tool subprocess267.439s, sampled setup PGID peak1453464KiB. Native job started2026-11-19T01:46:54Z and completed2026-11-19T02:16:55Z. Exact per-step setup/checkout/Validate/tool setup/build/run/upload times are in COST.json. Step wall boundaries overlap different receipt scopes and are not summed into a backend metric.

Caps unchanged: child600s includes compile180s, slot720s (recorded worker wall limit710s; controller180s and cleanup240s are separate caps), local sampled PGID6291456KiB, outer12582912KiB plus2097152KiB headroom, campaign6900s, setup1800s, job180min, Validate18min. Neither insertion hit child/compile/slot/global wall limits. No new cap, refund, reservation or accounting action.

RSS samples are nominal50ms non-atomic PGID VmRSS, possible overshoot. These are owned invocation/process-group observations, not exact per-property/root backend memory, kernel/cgroup peaks or an atomic full process-tree sum. Component maxima grouped by comm and outer owned-PID census have different scopes and times; they are not additive or interchangeable.

## checker_order_corrupt

Compile stateCOMPLETE; cutoff `NONE`, timed_outFalse; original native exit1/signalNone; child_shutdown_verifiedTrue. Worker exit0, outer cutoffNone, limit_initiatedFalse, supervisor_errorNone, orphan survivors[]. Containment `{"verified":true,"scope":"EXCLUSIVE_SUBREAPER_PID_STARTTIME","elapsed_seconds":0.00939591900009873,"signals":[],"reaped_adopted":[],"worker_exit":0}`. Next root `checker_count_corrupt`; continued under durable seal.

Component sampled peaksKiB `{"backend":18228,"compiler":1922820,"driver":6988,"other":172344}` (non-simultaneous); outer sampled owned-PID peak1990236KiB. Phase `COMPLETED; no phase peak timestamps`; RSS at signal/kernel/tree peak UNKNOWN. Worker lifecycle diagnostic retention and omission/classification counts are in COST.json and full authentic compact; final verified containment is not inferred by ignoring those events.

## checker_count_corrupt

Compile stateCOMPLETE; cutoff `NONE`, timed_outFalse; original native exit1/signalNone; child_shutdown_verifiedTrue. Worker exit0, outer cutoffNone, limit_initiatedFalse, supervisor_errorNone, orphan survivors[]. Containment `{"verified":true,"scope":"EXCLUSIVE_SUBREAPER_PID_STARTTIME","elapsed_seconds":0.008704790000138019,"signals":[],"reaped_adopted":[],"worker_exit":0}`. Next root `sort13_weak`; continued under durable seal.

Component sampled peaksKiB `{"backend":34588,"compiler":1877624,"driver":11048,"other":160144}` (non-simultaneous); outer sampled owned-PID peak1939372KiB. Phase `COMPLETED; no phase peak timestamps`; RSS at signal/kernel/tree peak UNKNOWN. Worker lifecycle diagnostic retention and omission/classification counts are in COST.json and full authentic compact; final verified containment is not inferred by ignoring those events.

## sort13_weak

Compile stateCOMPLETE; cutoff `NONE`, timed_outFalse; original native exit1/signalNone; child_shutdown_verifiedTrue. Worker exit0, outer cutoffNone, limit_initiatedFalse, supervisor_errorNone, orphan survivors[]. Containment `{"verified":true,"scope":"EXCLUSIVE_SUBREAPER_PID_STARTTIME","elapsed_seconds":0.008483641999873726,"signals":[],"reaped_adopted":[],"worker_exit":0}`. Next root `i_p01_b1_16`; continued under durable seal.

Component sampled peaksKiB `{"backend":25184,"compiler":1938904,"driver":8288,"other":177864}` (non-simultaneous); outer sampled owned-PID peak1992332KiB. Phase `COMPLETED; no phase peak timestamps`; RSS at signal/kernel/tree peak UNKNOWN. Worker lifecycle diagnostic retention and omission/classification counts are in COST.json and full authentic compact; final verified containment is not inferred by ignoring those events.

## i_p01_b1_16

Compile stateCOMPLETE; cutoff `rss_cap`, timed_outFalse; original native exit-15/signal15; child_shutdown_verifiedTrue. Worker exit0, outer cutoffNone, limit_initiatedFalse, supervisor_errorNone, orphan survivors[]. Containment `{"verified":true,"scope":"EXCLUSIVE_SUBREAPER_PID_STARTTIME","elapsed_seconds":0.008829527999978382,"signals":[],"reaped_adopted":[{"pid":10467,"start_ticks":191718,"status":3840}],"worker_exit":0}`. Next root `m8_s32_d00_allinit`; continued under durable seal.

Component sampled peaksKiB `{"backend":6349624,"compiler":2456684,"driver":8276,"other":129364}` (non-simultaneous); outer sampled owned-PID peak6380208KiB. Phase `AFTER_STOCK_INITIAL_EXPORT; precise symex/backend subphase UNKNOWN`; RSS at signal/kernel/tree peak UNKNOWN. Worker lifecycle diagnostic retention and omission/classification counts are in COST.json and full authentic compact; final verified containment is not inferred by ignoring those events.

First-over-cap trigger sample6361996KiB >6291456KiB. Pinned runner.py646-652 updates max then breaks on the first overcap sample, so recorded maximum identifies that trigger sample; it does not identify RSS at the subsequent signal. Compile marker at33.306s precedes child stop131.465s. Nominal child budget remaining after marker566.694s is arithmetic only; it is not a backend observation or fit result.

## m8_s32_d00_allinit

Compile stateCOMPLETE; cutoff `NONE`, timed_outFalse; original native exit0/signalNone; child_shutdown_verifiedTrue. Worker exit0, outer cutoffNone, limit_initiatedFalse, supervisor_errorNone, orphan survivors[]. Containment `{"verified":true,"scope":"EXCLUSIVE_SUBREAPER_PID_STARTTIME","elapsed_seconds":0.008221147999847744,"signals":[],"reaped_adopted":[],"worker_exit":0}`. Next root `i_p16_b1_16`; continued under durable seal.

Component sampled peaksKiB `{"backend":1461948,"compiler":2524808,"driver":2728968,"other":216656}` (non-simultaneous); outer sampled owned-PID peak2814392KiB. Phase `COMPLETED; no phase peak timestamps`; RSS at signal/kernel/tree peak UNKNOWN. Worker lifecycle diagnostic retention and omission/classification counts are in COST.json and full authentic compact; final verified containment is not inferred by ignoring those events.

## i_p16_b1_16

Compile stateCOMPLETE; cutoff `rss_cap`, timed_outFalse; original native exit-15/signal15; child_shutdown_verifiedTrue. Worker exit0, outer cutoffNone, limit_initiatedFalse, supervisor_errorNone, orphan survivors[]. Containment `{"verified":true,"scope":"EXCLUSIVE_SUBREAPER_PID_STARTTIME","elapsed_seconds":0.008204836999993859,"signals":[],"reaped_adopted":[{"pid":11586,"start_ticks":228406,"status":3840}],"worker_exit":0}`. Next root `m8_s32_d00_partial_diag`; continued under durable seal.

Component sampled peaksKiB `{"backend":6305752,"compiler":2530260,"driver":8172,"other":105948}` (non-simultaneous); outer sampled owned-PID peak6348352KiB. Phase `AFTER_STOCK_INITIAL_EXPORT; precise symex/backend subphase UNKNOWN`; RSS at signal/kernel/tree peak UNKNOWN. Worker lifecycle diagnostic retention and omission/classification counts are in COST.json and full authentic compact; final verified containment is not inferred by ignoring those events.

First-over-cap trigger sample6330308KiB >6291456KiB. Pinned runner.py646-652 updates max then breaks on the first overcap sample, so recorded maximum identifies that trigger sample; it does not identify RSS at the subsequent signal. Compile marker at31.836s precedes child stop126.13s. Nominal child budget remaining after marker568.164s is arithmetic only; it is not a backend observation or fit result.

## m8_s32_d00_partial_diag

Compile stateCOMPLETE; cutoff `NONE`, timed_outFalse; original native exit0/signalNone; child_shutdown_verifiedTrue. Worker exit0, outer cutoffNone, limit_initiatedFalse, supervisor_errorNone, orphan survivors[]. Containment `{"verified":true,"scope":"EXCLUSIVE_SUBREAPER_PID_STARTTIME","elapsed_seconds":0.008746973000143043,"signals":[],"reaped_adopted":[],"worker_exit":0}`. Next root `m8_s40_d16_partial_diag`; continued under durable seal.

Component sampled peaksKiB `{"backend":1434156,"compiler":2630132,"driver":2406272,"other":142268}` (non-simultaneous); outer sampled owned-PID peak2772160KiB. Phase `COMPLETED; no phase peak timestamps`; RSS at signal/kernel/tree peak UNKNOWN. Worker lifecycle diagnostic retention and omission/classification counts are in COST.json and full authentic compact; final verified containment is not inferred by ignoring those events.

## m8_s40_d16_partial_diag

Compile stateCOMPLETE; cutoff `NONE`, timed_outFalse; original native exit0/signalNone; child_shutdown_verifiedTrue. Worker exit0, outer cutoffNone, limit_initiatedFalse, supervisor_errorNone, orphan survivors[]. Containment `{"verified":true,"scope":"EXCLUSIVE_SUBREAPER_PID_STARTTIME","elapsed_seconds":0.00878583100029573,"signals":[],"reaped_adopted":[],"worker_exit":0}`. Next root `END_OF_SELECTED_PREFIX`; continued under durable seal.

Component sampled peaksKiB `{"backend":1454988,"compiler":2511780,"driver":2615088,"other":144256}` (non-simultaneous); outer sampled owned-PID peak2816820KiB. Phase `COMPLETED; no phase peak timestamps`; RSS at signal/kernel/tree peak UNKNOWN. Worker lifecycle diagnostic retention and omission/classification counts are in COST.json and full authentic compact; final verified containment is not inferred by ignoring those events.

## Historical scope limit

Old run44416629057 insertion:112.349s/RSS6326988KiB, compile marker34.680s; old same-allocation merge600.205s/timeout, compile marker35.105s, sampled peak2558128KiB. Those exact rows and old commit are preserved in COST.json. The old insertion varied begin1..16 AND tail1..16, whereas new roots fix tail1 or16. The old merge varied nonoverlapping offsets whereas new merges fix source/destination/init geometry. These are changed problems; no matched speedup, full-domain fit600, or proof completion follows.
