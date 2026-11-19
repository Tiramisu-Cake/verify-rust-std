# r4 full standard CI — attempt 1 terminal intake

Kani CI FAILURE; Kani Format Check SUCCESS; Cargo Deny SUCCESS. All 12 expected standard job instances are present and terminal: 11 SUCCESS and perf FAILURE. Five regression platforms, docs, benchcomp, LLBC, Format/Clippy and Deny jobs succeeded at job/step level. Full standard CI is not green.

Head `b3019ab3f9c83a25cd4d870e49e49121b3327bb1`, tree `b05ea48016f1cb8f20a1e7032394e602929b6e3b`, sole parent `031fc085cd4373b5fc93a55128d5a69fdbd88df1`, push/ref `fix/stub-contracted-function`, attempt 1. Explicit `/attempts/1` run/jobs endpoints were queried through connected GitHub. Later attempts are outside this packet. Native source commit/ref metadata and local committed blobs match the reviewed tree; actual native checkout/compiler/MIR/property binding is UNKNOWN.

| Run | Job ID | Native job | Conclusion | Relevant returned steps |
| --- | --- | --- | --- | --- |
| 44516395307 | 135533377213 | documentation | SUCCESS | Install book dependencies: SUCCESS; Build Documentation: SUCCESS; Publish Documentation: SKIPPED |
| 44516395307 | 135533377569 | llbc-regression | SUCCESS | Setup Kani Dependencies: SUCCESS; Build Kani with Charon: SUCCESS; Run tests: SUCCESS |
| 44516395307 | 135533377615 | benchcomp-tests | SUCCESS | Install benchcomp dependencies: SUCCESS; Setup Kani Dependencies: SUCCESS; Build Kani using release mode: SUCCESS; Run benchcomp unit and regression tests: SUCCESS |
| 44516395307 | 135533377626 | perf | FAILURE | Setup Kani Dependencies: SUCCESS; Execute Kani performance tests: FAILURE |
| 44516395307 | 135533377710 | regression (ubuntu-22.04) | SUCCESS | Setup Kani Dependencies: SUCCESS; Execute Kani regression: SUCCESS |
| 44516395307 | 135533377711 | regression (ubuntu-24.04-arm) | SUCCESS | Setup Kani Dependencies: SUCCESS; Execute Kani regression: SUCCESS |
| 44516395307 | 135533377737 | regression (macos-15) | SUCCESS | Setup Kani Dependencies: SUCCESS; Execute Kani regression: SUCCESS |
| 44516395307 | 135533377786 | regression (ubuntu-24.04) | SUCCESS | Setup Kani Dependencies: SUCCESS; Execute Kani regression: SUCCESS |
| 44516395307 | 135533377788 | regression (macos-15-intel) | SUCCESS | Setup Kani Dependencies: SUCCESS; Execute Kani regression: SUCCESS |
| 44516395718 | 135533378422 | clippy-check | SUCCESS | Setup Kani Dependencies: SUCCESS; Install jq for parsing.: SUCCESS; Run Clippy: SUCCESS; Print Clippy Statistics: SUCCESS |
| 44516395718 | 135533379023 | format-check | SUCCESS | Execute copyright check: SUCCESS; Check C code formatting: SUCCESS; Check Python code formatting: SUCCESS |
| 44516395278 | 135533377445 | audit | SUCCESS | Run actions/checkout@v6: SUCCESS; Run EmbarkStudios/cargo-deny-action@v2: SUCCESS |

All returned steps, including skipped and null/in_progress records, are preserved in NATIVE-JOBS.json. Documentation publication was skipped. Perf setup succeeded; Execute Kani performance tests failed. Perf's Post Checkout Kani was skipped and Complete job remained in_progress with null conclusion/completed_at despite the terminal job FAILURE. The job interval is 11:36:54–12:56:55Z; the performance step interval is 11:44:42–12:12:20Z. These timestamps do not establish resource use or causality.

Runner communication/CPU-memory/s2n-quic attribution is COORDINATOR_REPORTED from the pinned coordinator report; independent cause is UNKNOWN. Check-run summary endpoints for all 12 job IDs were rejected by the connector with INVALID_ARGUMENT (not an allowed endpoint); summaries and annotations are unavailable here. No raw-log/archive/GCS or alternate transport fallback was used.

Fresh attempt-1 job identities, conclusions and every step match sealed ATTEMPT-1-NATIVE.json. Kani run updated_at differs by one second (sealed 12:56:55Z, refreshed 12:56:56Z); status/outcome and all job/step records match. Immutable input/source/review/GO/addendum manifests and published file/workflow pins were checked.

Seven source declarations remain five intended positives and two expected-mode semantic negatives. Job/step success does not directly expose individual harness/property results, exact expected failure descriptions, source checkout bytes or MIR binding. Those native details remain UNKNOWN. Source oracles and required negative semantics are recorded separately in SOURCE-ORACLES.md. Current-main failure/fixed-PASS pairing, complete named-property platform validation, full-green CI and performance speedup are not established.

Historical r3: 28cd7f0a87b4fda68df320fab7422d2491b24839: Kani44461123962 FAILURE/perf reason coordinatorreported shutdown+s2n, independentcauseUNKNOWN; fiveOSregression/docs/benchcomp/LLBC/Format/Deny SUCCESS. Historical context only, no substitution for current run or perf waiver.. That history neither substitutes for this attempt nor waives its perf failure. Coordinator reports of r2/main perf success are also historical, uncontrolled context, not a causal comparison.

All worker compiler/native execution is NOT_RUN. Source, PR drafts, external files, S4 and ledgers/accounting were untouched; counts are TRACKING_ONLY. Root verification and factual coordinator handoff follow; no rerun, source fix, review, CI, publication or accounting is triggered by this packet.
