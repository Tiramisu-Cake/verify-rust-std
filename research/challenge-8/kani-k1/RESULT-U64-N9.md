# RESULT U64-N9 — PASS (typed u64/U64Cmp N9 leaf + actual-route composition)
Coordinator GO/source `b5e00ef1a5043056b48ddf70a4b666b565ae83bb`; one jointly submitted four-row packet, owner k1-merge.
Build `62bb5025-ed9a-4116-a868-610c993af026`; request `u64nine-n9-leaf-composition-controls-20261102`.
Request SHA256 `7a0dcbf7cc987602d0d5f309098a7f2c99adf6221b6f136ac0d76f3b2931fead` matches; library `fddf308321046a8cd8f5526622a5e2353d79830e`/tree `d22566ab5a`.
Dispatched via alias `experiment/kani-k1-usixtyfournine-20261102` (same SHA; dispatch regex forbids digits).
Pin Kani9461e07af7/nightly-2026-10-12, tooling PASS vs30f77e8; measurement/controls/jobs1/uninit off/unwind25/600s/k1-standard4.
T=u64; F=U64Cmp=fn(&u64,&u64)->bool, value StrictU64::CMP=reified strict_less::<u64> (ordinary `<`).
Full any [u64;9]/independent u64 probe, backing9/offset0; Unstable->Freeze/Copy->network->sort9(25 raw)->empty insertion.
Trace: raw swap_if_less -> adapter_u64nine -> sole u64/U64Cmp bridge -> verified swap_u64_net9 (B, controls).
Leaf has no stub/verified-stub lines; it runs the real helper and proves pair/order/full-count/frame7 itself.
Composed: hits25, root/pair/canonical/frame/per-exchange count invariant, sortedness and full-u64 count pass.

| network::u64nine:: row | Status | VT s | CBMC RSS KiB | Failed/total; unreachable | Covers |
|---|---|---:|---:|---|---|
| u64nine_leaf_u64_n9 | SUCCESS | 76.41763 | 359428 | 0/388;5 | 7/7 |
| u64nine_composed_u64_n9 | SUCCESS | 148.28758 | 1345528 | 0/588;18 | 7/7 |
| u64nine_wrong_cmp_u64_n9 | FAILED expected | 0.77463937 | UNKNOWN | 1/550;29 | 2/2 |
| u64nine_count_negative_u64_n9 | FAILED expected | 82.19006 | 1004240 | 1/570;18 | 3/3 |

Only failed literals: `u64nine canonical comparator required` (:123, inside SwapBridgeU64Nine::exchange) and
`u64nine N9 negative: full-value count preserved` (reported assertion span :235; literal line237).
Wrong-cmp reaches the actual adapter guard before summary (RSS UNKNOWN: unsampled). Count control passes hits/invariant/frame and post-corruption sortedness, reaches count-check; count(1<<40) 9->8
with v[8]=1<<41 (same low32 bits). No unrelated failed checks, TIMEOUT or OOM (dmesg none_seen).
Composed covers include high-bit probe hit (probe>255) and complete hits25. All positive covers complete.
Cloud SUCCESS; lane COMPLETE; gate=true, expectation_met=true, measurement_ok=true; Kani exit1 from expected controls.
B+leaf VT=224.70521s (price of this proof); no matching direct A64 row, so no speedup claimed.
CBMC max(B,leaf)=1345528KiB; compiler VmHWM1803192KiB; kani-driver4223032KiB; sampled process-sum4242376KiB.
Wall397.09s incl compile; Cloud833.47s. Own1/1 Build spent$0.1890, reserved$0 (reserve$0.945<=cap$2.00). u8 N9 is another typed experiment.
Static ordinary exact200/cfg-on399, PFC19/bad0, rustfmt/whitespace PASS; no ordinary proof credit or ledger rewrite.
Established: exact u64/U64Cmp/default-< N9 theorem on backing9/offset0 with independent full-u64 probe and matching
real leaf pair/frame/count invariant, machine-checked actual-route composition; opt-in research.
Open: function-item F, arbitrary T/FnMut, N13/18/32, other backings/offsets, tie stability, uninit detection,
full alias-validity/unwind scope, trait PFC; ordinary200 and Part1-v6/202 not extended.
Evidence: u64nine/g1.{summary.md,rows.txt,checks-grep.txt,peaks.txt,tooling.txt,status.json,cost.txt,dispatch.txt}; PREBUILD.md.
Next: STOP; no G2/retry or further Build. U64-N9 ЗАВЕРШЁН
