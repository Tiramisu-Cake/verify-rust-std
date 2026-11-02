# RESULT NETCOMP2 — PASS (exact N9 calibration and N13 composition gate)
Historical NETCOMP G1 remains PARTIAL (A9 covers4/5); its38.2% was observation under a failed measurement gate.
Coordinator GO/source: `bd5d2bf059e720e5bc59c7d1bc433f743ba65ec4`; one jointly submitted seven-row packet.
Build `44af7732-80e7-4cc3-b3ec-26f5af0d2d40`; request `netcomp2-n9-cover-n13-pair-frame-count-20261102`.
Request SHA256 `69646d5b669310254328a92ea9d35d7d0b2a99c0708cd94f4605e04422723311` matches.
Library commit `f4d3775dc505ef26e30158cfa7e78f120cd3c30e`; tree `3b6d2a51dae08e52464f4b2b82f5168d8ba9977b`.
Pin Kani9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12; source/request/pool/tooling identity PASS.
measurement, controls:true, jobs1, uninit off, unwind25/unwinding assertions,600s/row, k1-standard4/16GiB, swap off.
T=u8; F=U8Cmp=fn(&u8,&u8)->bool, value StrictU8::CMP=reified strict_less::<u8>; not prior function-item F.
Unrestricted full inputs/independent u8 probe; exact initialized backing9/13, offset0, pair-only summary writes.
Actual Unstable -> Freeze/Copy -> sort9/13 -> empty insertion suffix, no merge; runtime source unchanged.
B trace prints raw swap_if_less->adapter9/13 plus verified swap_net9/13; hits25/45, root/pair/frame/canonical/invariant pass.
New leaf13 has no substitutions and proves actual helper pair/order/full-count/frame on its own exact backing13.
Reused historical leaf9 SUCCESS7/7 and wrong-cmp9 intended FAILED2/2: G1 build b3e257d1-eaf9-4323-a8f1-f4648798cbd9,
source0944189023c0c53620ed74a45bb2d2efef4c53cd; dependency bytes/pin/flags preserved (netcomp2/reuse-dependencies.md).

| network::netcomp:: row | Status | VT s | CBMC RSS KiB | Failed/total; unreachable | Covers |
|---|---|---:|---:|---|---|
| netcomp_direct_u8_n9 (A9) | SUCCESS | 242.8685 | 275236 | 0/383;22 | 4/4 |
| netcomp_composed_u8_n9 (B9) | SUCCESS | 93.435 | 989648 | 0/588;18 | 6/6 |
| netcomp_count_negative_u8_n9 | FAILED expected | 59.137207 | 945832 | 1/569;18 | 3/3 |
| netcomp_leaf_u8_n13 | SUCCESS | 52.948425 | 334712 | 0/388;5 | 7/7 |
| netcomp_composed_u8_n13 (B13) | SUCCESS | 268.8405 | 2156824 | 0/588;18 | 6/6 |
| netcomp_wrong_cmp_u8_n13 | FAILED expected | 0.54970115 | UNKNOWN | 1/550;29 | 2/2 |
| netcomp_count_negative_u8_n13 | FAILED expected | 138.28883 | 1907928 | 1/569;18 | 3/3 |

Only failed literals: `netcomp N9 negative: full-value count preserved` (:242), `netcomp canonical comparator required` (:354),
and `netcomp N13 negative: full-value count preserved` (:459), netcomp.rs reported assertion spans; literal lines244/354/461.
Count controls pass hits/invariant/frame before v[8/12]=1, then pass sortedness and reach count-check; count(0)9->8/13->12.
Wrong-cmp reaches the actual B13 adapter guard before summary; RSS UNKNOWN because this short CBMC process was not sampled.
No unrelated failed checks, timeout or OOM. All positive covers complete; historical rows are not rows of this new Build.
Cloud SUCCESS; lane COMPLETE; expectation_met=true, measurement_ok=true, gate=true; Kani exit1 from expected controls.
Current VT: B9_new93.435s vs A9_new242.8685s; B alone61.53% less, excluding leaf cost.
Mixed-run estimate B9_new+leaf9_old=143.109446s,41.08% less than A9_new; NOT same-build measurement.
Jobs1 CBMC max(B9_new,leaf9_old)=989648KiB vs A9_new275236KiB (~3.596x); no memory improvement.
N13 B+leaf=321.788925s, CBMC max(B13,leaf13)=2156824KiB; composition fits600s/row, speedup unestablished without matching direct F.
Compiler VmHWM1806972KiB; kani-driver8209712KiB; sampled process-sum8130224KiB; command wall929.76s incl compilation.
Cloud start->finish1275.949353s; own1/1 Build, spent$0.2970, reserved$0; initial reserve$1.350 <=stage cap$1.40, project cap$88.96.
Static ordinary exact200/cfg-on395; PFC18/bad0, rustfmt/whitespace PASS; no new ordinary proof credit or historical ledger changes.
Established: machine-checked actual-route composition for the stated exact N9/N13 u8/U8Cmp domain and full-value count oracle.
Open: old function-item F, arbitrary T/FnMut/backings/offsets/N18, tie stability, init detection/full alias-validity/unwind, trait-PFC/Part1/v6.
Evidence: netcomp2/g1.{summary.md,rows.txt,checks-lines.txt,peaks.txt,tooling.txt,status.json,cost.txt,assessment.json}; PREBUILD.md/reuse-dependencies.md.
Evidence Brief HTTP404 recorded in g1.brief.txt; task-specific bounded K-1 reports used, no archive-integrity/independent-reader credit inferred.
Next: STOP; old NETCOMP G2 not resumed, no retry or further Build. NETCOMP2 ЗАВЕРШЁН
