# RESULT DIRECTFOUR — direct4 PASS (direct merge_profile<StrictU8> on the MERGESTEP composed fixture, no stubs)
Runtime Claude Code, no subagents. G1 GO 88d57dea95 -> Build 37d72ac9-af24-4969-8754-e1e01ef6be88: COMPILE_ERROR (3x E0599,
trait Profile not imported in directfour.rs), row NOT_RUN, $0.1080. G2 GO 7cedb3a2a3cdc259a8c42930f64a06e9c28f121b (fix = import only)
-> Build 9a000cec-dbd7-4b81-ab81-54da258f9d83: Cloud SUCCESS, summary COMPLETE, head 7cedb3a2a3 = reviewed SHA.
Library commit 248b2725c6cd528a6d87aa5928e362dc11e74522, tree 7996f9c151be2011be23bb44d04f286ea2905810 (base 91d4d9f77a / dc7c79bb).
Request directfour-direct-merge4-baseline-20261102, SHA256 82bc61a1…85d5fb matches (same bytes G1/G2); owner k1-network.
Pin Kani9461e07af7 / nightly-2026-10-12; check-tooling vs30f77e8599 PASS (both builds); bound hashes = MERGESTEP.
measurement, controls:true, jobs1, uninit off, 600s, k1-standard4/16GiB, swap off; unwind34, unwinding assertions on.

| row network::netcomp::mergestep::directfour:: | Status | VT s | CBMC RSS KiB | Failed/total; unreachable | Covers |
|---|---|---:|---:|---|---|
| directfour_merge4_u8 | SUCCESS | 207.97597 | 894860 | 0/677;67 | 6/6 |

Gate: PASS (gate/expectation_met/measurement_ok true, Kani exit0; SUCCESS + all 6 covers + identities match). No "Stub" line in
the log; annotations PFC merge_profile + unwind(34) only: real bidirectional_merge, merge_up/down, panic_on_ord_violation.
Compiler 1781964KiB; kani-driver 359028KiB; sampled process-sum 2023140KiB; time -v max 1794836KiB; wall 289.79s; Cloud
start->finish 677.9s; dmesg OOM none_seen. 67 unreachable checks not itemized by terse log (not inspected further).
Fact: on the exact MERGESTEP composed fixture (StrictU8 probe any, source18 any [..4], scratch32 uninit +0, same register/
check_merge4 oracle, same 6 post covers) the direct PFC proves in 208s, while the composed root (adapters + stub/stub_verified
steps + ledgers) hit TIMEOUT600 (VT UNKNOWN, CBMC 2607368KiB). So the composed TIMEOUT is attributable to the composition
bundle as a whole on this fixture; which part (ledgers vs pointer/havoc/assigns of verified stubs) is NOT separated.
NOT established: composed speedup (composed VT UNKNOWN); N18/N32/merge18; other CMP/F/backing/probe; generic T/FnMut;
uninit/alias-validity/unwind; Part1/ordinary credit. Historical MERGESTEP TIMEOUT/failed gate unchanged.
Own 2/2 Builds (G2 by compile-error branch), spent$0.2700, reserved$0 (cap$1.10); project cap$88.96. No G3.
Static: ordinary200 unchanged; cfg-on404->405; pfc_order25/bad0; rustfmt/diff-check PASS. Not proofs.
Evidence: directfour/g{1,2}.{summary.md,status.json,rows.txt,cost.txt,peaks.txt,tooling.txt}, g1.error-lines.txt,
g2.checks-lines.txt, runs.json, PREBUILD.md, PREBUILD-G2.md, static-check.json. Next: STOP.
