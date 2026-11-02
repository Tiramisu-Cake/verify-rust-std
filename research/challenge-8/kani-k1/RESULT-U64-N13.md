# RESULT U64-N13 — PARTIAL (leaf13 + both controls as intended; composed B13 TIMEOUT600)
Coordinator GO/source `99b08903f9d6ef1c53fb8a3701b6766261241e50`; one jointly submitted four-row packet, owner k1-merge.
Build `f11489dc-97ed-4470-8ed1-d782ea1f8a0f`; request `u64thirteen-n13-leaf-composition-controls-20261102`.
Request SHA256 `cf8693f597c243b5e084dcc96e877084e7fa48e98e1b5977cacad57493991e67` matches; library `497077c6cd14fdbcc439807c0cdc186860cb00ce`/tree `90a3889318`.
Dispatched from the task branch (no alias). Pin Kani9461e07af7/nightly-2026-10-12, check-tooling PASS vs30f77e8;
measurement/controls/jobs1/uninit off/unwind25/600s/k1-standard4 (16GiB, swap off); flags unchanged.
T=u64; F=U64Cmp=fn(&u64,&u64)->bool, value StrictU64::CMP=reified strict_less::<u64> (default `<`).
Full any [u64;13]/independent u64 probe, backing13/offset0; Unstable->Freeze/Copy->network->sort13(45 raw)->empty insertion.
Binding (trace): raw swap_if_less -> adapter_u64thirteen -> sole u64/U64Cmp bridge -> verified swap_u64_net13. Leaf has no stub lines; it runs the real helper and proves pair/order/full-count/frame11 on its own exact backing13.

| network::u64nine::uthirteen:: row | Status | VT s | CBMC RSS KiB | Failed/total; unreachable | Covers |
|---|---|---:|---:|---|---|
| u64thirteen_leaf_u64_n13 | SUCCESS | 180.07642 | 411696 | 0/388;5 | 7/7 |
| u64thirteen_composed_u64_n13 (B13) | TIMEOUT (cap600) | UNKNOWN | 3390464 | UNKNOWN | UNKNOWN |
| u64thirteen_wrong_cmp_u64_n13 | FAILED expected | 1.02872 | UNKNOWN (one unattributed 2s cbmc sample 35584@238s) | 1/550;29 | 2/2 |
| u64thirteen_count_negative_u64_n13 | FAILED expected | 169.42989 | 2032700 | 1/570;18 | 3/3 |

Gate=false (expectation_met=false, measurement_ok=false); Kani exit1; Cloud status FAILURE; lane summary COMPLETE.
B13: "CBMC timed out" after the 600s cap (CBMC PID active240..840s); no result, check counts, or covers; not OOM (dmesg none_seen).
Only failed literals in controls: `u64thirteen canonical comparator required` (:127, inside SwapBridgeU64Thirteen::exchange)
and `u64thirteen N13 negative: full-value count preserved` (reported assertion span :238; literal line240).
Count control passes hits45/invariant/frame and post-corruption sortedness, reaches count-check; count(1<<40) 13->12 via v[12]=1<<41. Wrong-cmp reaches the actual adapter guard before summary. No unrelated failed checks in the three finished rows.
Leaf13 SUCCESS is a matching independent leaf, but without B13 SUCCESS there is NO composition credit for N13.
B13+leaf13 price is not established (B13 VT UNKNOWN, >600s at this resource); no matching A64-N13, no speedup.
CBMC max=3390464KiB (B13, at timeout window); compiler VmHWM1809864KiB; kani-driver4981392KiB; sampled process-sum6525164KiB@425s.
Wall17:08.33 incl compile; Cloud start->finish1409.05s. Own1/1 Build spent$0.3240, reserved$0 (reserve$0.945<=cap$2.00).
Global after: builds168, used$79.0395, unfinished$0. Comparisons with u64 B9 (148s) / u8 B13 (269s) are different runs/domains.
Static ordinary exact200/cfg-on403, PFC20/bad0, rustfmt/whitespace PASS; runtime/N9/netcomp unchanged; no ledger rewrite.
Established: only leaf13 theorem (pair/order/full-u64 count/frame11 of real swap on exact backing13) and the two
actual-route controls behaving as intended. NOT established: N13 whole-network sortedness/full-value permutation.
Open: B13 within600s on k1-standard4; function-item F, arbitrary T/FnMut, N18/32, other backings/offsets, tie stability,
uninit detection, full alias-validity/unwind, trait PFC; ordinary200 and Part1-v6/202 not extended.
No G2: TIMEOUT is a resource outcome, not compile error; input/probe/width/timeout/machine not changed or narrowed.
Evidence: u64thirteen/g1.{summary.md,rows.txt,checks-grep.txt,checks-lines.txt,peaks.txt,tooling.txt,status.json,cost.txt,dispatch.txt}; PREBUILD.md.
Next: STOP; no retry, no further Build; any B13 reformulation needs new coordinator staging. U64-N13 ЗАВЕРШЁН (PARTIAL)
