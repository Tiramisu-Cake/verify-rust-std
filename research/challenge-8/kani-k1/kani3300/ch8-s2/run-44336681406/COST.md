# Exact cost and launch order — 44336681406/1

| Stage / metric | Observation | Scope / completeness |
|---|---|---|
| Source compile/link → initial stock export | COMPLETE; elapsed_upper_bound_seconds=35.5 | Runner monotonic polling upper bound rounded to 0.001 s; exact compile wall UNKNOWN |
| Native Cargo Finished profile | 30.49 s | Producer report; distinct boundary, not additive |
| First root symex | Runtime Symex: 488.498s | Completed native progress stage; independent root wall/clock basis unavailable |
| Program expression | 4,175,569 steps | Raw count; 4.18M is rounded |
| Slicing | 2,842,455 assignments removed | Native progress count |
| VCC generation/simplification | 376,543 → 155,645 | Obligations before/after simplification, not passed properties |
| Equation postprocess | Runtime Postprocess Equation: 25.0517s | Completed native progress stage |
| SAT/solver, encoding and other phase gaps | UNKNOWN | No phase-final receipt; do not subtract times to invent costs |
| Root total wall / verification_time_s | UNKNOWN / absent | No terminal export; not zero and not 600 s |
| Group execute elapsed | 569.735 s | Includes compilation, verification work and shutdown; not root wall |
| Whole runner phase | 574.479 s | Different envelope, not additive to group |
| Stock tool build execute | 252.891 s | Setup receipt exit0; not source proof compile |
| Setup aggregate | 400.5033736228943 s | Receipt using setup epoch; distinct from phase |
| GitHub job | 981 s | Connected started_at 15:31:51Z → completed_at 15:48:12Z; timestamp-resolution wall, includes CI/setup |

Primary probes merge32_real, sort13_assumed and general32_assumed never started. Qualification swap_pfc, constructive summary_witness and five other negative controls never started. Their per-root costs remain UNKNOWN, with shared compilation/setup costs retained. The only observed root is the negative general32_weak; no speedup or relative cost estimate for another root follows. COST.json contains all 11 rows and connected step summaries.

Root backend timeout is 600 s, compile cap 900 s, root budget sum 6600 s, group envelope 7500 s, runner phase cap 8100 s, proof workflow step 7560 s and job 180 min. The actual event is RSS interruption, timed_out=false; no root completed or reached an observed TIMEOUT600 verdict. A future TIMEOUT600 observation would be censored, but this run must retain its different RSS censoring. Validation/source/setup caps remain 600/60/1800 s.

Sampled group VmRSS maximum is 12,585,016 KiB / 1,048,576 = 12.002006530761719 GiB. The effective enforced cap was 12,582,912 KiB = 12 GiB, chosen as min(12 GiB, available minus 2 GiB reserve); recorded available memory was 15,190,664 KiB. The sampler sums VmRSS of processes with the child's PGID, reading /proc; it is neither virtual memory nor a simultaneous whole-tree census. Escaped process-group members are outside this sampler. Nominal sleep/sample period is 0.05 s; true peak and polling jitter are not measured.

Comm-class sampled maxima are backend 12,568,160 KiB (11.985931396484375 GiB), compiler 3,128,832 KiB (2.98388671875 GiB), driver 16,528 KiB (0.0157623291015625 GiB) and other 162,648 KiB (0.15511322021484375 GiB). Each is a maximum of its class sum in the PGID, collected separately; maxima are not simultaneous and must not be added. Backend includes cbmc/goto-instrument/goto-cc/goto-analyzer, not one identified backend PID. Neither backend nor group maximum is exact per-root RSS. The advertised 6 GiB root target is unmeasured and not enforced by this invocation: execute receives memory[group_cap_kib], not per_root_cap_kib.

Exact runner at d33: ch8-s1-control/runner.py:413–446 defines PGID/VmRSS/comm scope; :463–476 sends SIGTERM, waits up to 5 s, then SIGKILL if live; :537–562 sets the cap; :584–585 uses start_new_session=True; :614–652 samples and detects rss > cap; :655–690 handles kill/wait/readers/shutdown; :1064–1067 passes the group cap. PGID equals spawned child PID by construction; the actual numeric PID/PGID is not exported. Recorded parent exit -15 confirms SIGTERM termination. Whether a descendant needed SIGKILL or which individual PID caused growth remains UNKNOWN. No kernel-OOM cause is inferred.

Why general32_weak ran first:

1. Actual argv (embedded group receipt and binding metadata) selects all 11 roots in request order, beginning swap_pfc and ending general32_weak, with --exact, --jobs=1, --harness-timeout 600s, unwind34 and all three opt-in cfgs. Reconstructed argv from exact producer matches byte-for-byte.
2. Stock0aac standalone verify-std compiles std_project before verify_project (kani-driver/src/main.rs:149–156); then selects roots, writes initial INCOMPLETE export and calls check_all_harnesses (:186–198). This establishes the compile boundary, not a terminal root verdict.
3. Compiler codegen_units.rs:244–269 groups by resolved contract-use set and stub map. Its units are collected from HashMap values; metadata generation :223–233 also iterates harness_info HashMap values. Native metadata indeed has a compilation inventory order starting merge_order_corrupt, merge32_real, checker_count_corrupt, summary_witness, swap_pfc, general32_weak. That is not backend launch order. Native attributes expose ordinary/verified stub contexts; internal resolved unit IDs/order are not exported and remain UNKNOWN. No claim that JSON order controls those units.
4. Driver metadata.rs:159–168 sorts original_file ascending, then original_start_line descending; harness_runner.rs:120 applies it, :137–140 creates the pool and :140–158 dispatches each root. args/mod.rs:445–460 makes jobs1 a one-worker pool; run_until_abort :58–89 processes one harness per Rayon job. All 11 actual roots share the same original_file. Native metadata gives general32_weak line160, the highest selected line, so it is first; sort8_registration_only line171 is not selected.
5. Rich streaming parser records exactly the general32_weak start and zero properties. All observed stdout bytes were fed before the final missing-RESULTS error; source runner.py:354–399 and rich_evidence.py:96–144 establish this distinction from bounded retained head/tail. The last progress names general32_weak at assertion line163 and reports symex/postprocess. With one worker and this root still incomplete at group kill, the other ten roots are NOT_STARTED, without treating their absent measurements as zero.

The stock sorted candidate sequence is general32_weak160 → sort13_weak146 → checker_order_corrupt138 → checker_count_corrupt132 → merge_count_corrupt125 → merge_order_corrupt118 → summary_witness102 → swap_pfc74 → general32_assumed59 → sort13_assumed42 → merge32_real29. Only the first launch was observed; this is the source-sorted sequence, not an observed 11-root execution trace or a cross-configuration scheduling guarantee. SOURCE-TRACE.json preserves exact commit/file hashes and bounded numbered excerpts. Reordering JSON rows alone does not change the driver's file/descending-line sort.

Ledger 943d67bd487ea3ab33e5e77a0d0dfe8453a83532 and item2 10/14, total39/43 (item1 29/29) are owner/coordinator-reported references, not independently replayed or edited. The observed boundary confirms a backend root executed, so confirmed pre-root compilefailure0 does not apply. Earlier r0–r3 compilefail0 and r4-r1 validationtimeout0 remain historical coordinator-specific decisions; no missing-RESULTS refund or new accounting rule is inferred.
