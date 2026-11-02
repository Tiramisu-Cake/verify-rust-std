# RESULT NETCOMP — PARTIAL (G1 coverage/measurement gate false)
G1 only; coordinator GO/source `0944189023c0c53620ed74a45bb2d2efef4c53cd`.
Build `b3e257d1-eaf9-4323-a8f1-f4648798cbd9`; request `netcomp-g1-n9-pair-frame-count-20261102`.
Request SHA256 `e7afc8c7cb631569289b751c103892302c736191f28153e95216f24c41dc312a` matches.
Library commit `47ed440a23641545fba1eedd279a0ebabe6edf02`; tree `f9fa2945d6fd31f042b66926aad098f906f4abca`.
Pin Kani9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12; tooling/pool identity PASS.
T=u8, F=U8Cmp=fn(&u8,&u8)->bool, value StrictU8::CMP (reified strict_less::<u8>).
Exact initialized backing9/offset0, full arbitrary input and independent arbitrary u8 probe in positives.
Real Unstable -> Freeze/Copy -> sort9 -> empty insertion suffix, no merge; raw helper unchanged.
B: raw swap_if_less -> adapter9 -> sole u8/U8Cmp bridge -> verified swap_net9; independent leaf has no stubs.
Trace: B prints both substitutions; hits25/root/pair/ctx frame/canonical/invariant checks pass; guard control binds same adapter.
measurement, controls:true, jobs1, uninit off, unwind25/unwinding assertions, 600s/row, k1-standard4/16GiB, swap off.

| network::netcomp:: row | Status | VT s | CBMC RSS KiB | Failed/total; unreachable | Covers |
|---|---|---:|---:|---|---|
| netcomp_leaf_u8_n9 | SUCCESS | 49.674446 | 314920 | 0/388;5 | 7/7 |
| netcomp_direct_u8_n9 (A9) | SUCCESS | 260.72028 | 275776 | 0/383;22 | 4/5 (1 unreachable) |
| netcomp_composed_u8_n9 (B9) | SUCCESS | 111.43491 | 988628 | 0/588;18 | 6/6 |
| netcomp_wrong_cmp_u8_n9 | FAILED expected | 0.5270568 | UNKNOWN | 1/550;29 | 2/2 |
| netcomp_count_negative_u8_n9 | FAILED expected | 67.798065 | 971680 | 1/569;18 | 4/4 |

Wrong-cmp sole failure: `netcomp canonical comparator required`, netcomp.rs:122, actual entry/adapter reached.
Count-control sole failure: `netcomp N9 negative: full-value count preserved`, netcomp.rs:242.
Canonical B first passes hits/invariant/frame, then v[8]=1 keeps order and changes count(0)9->8; both witness covers reached.
No unrelated failed checks, timeout or OOM; wrong-cmp RSS UNKNOWN because its short CBMC run was not sampled.
Cloud Build FAILURE; lane COMPLETE, expectation_met=true, measurement_ok=false, gate=false; Kani exit1 expected.
G1 is NOT PASS: A9 leaves one cover unreachable. No cover requirement or checker was waived.
Source attribution: shared run9(false) excludes check_context9's `netcomp N9: all actual exchanges intercepted` cover.
Terse evidence reports aggregate4/5 only, without cover label; the label attribution is source reasoning, not a named runtime property.
Per-row leaf/B proof and both controls succeeded for this exact N9 domain; overall calibration gate remains unaccepted.
Observed VT(B9)+VT(leaf9)=161.109356s vs A9=260.72028s (38.205% less); no accepted measurement/speedup gate claim.
Jobs1 CBMC peak=max(B9,leaf9)=988628KiB vs A9=275776KiB (~3.585x higher), not a memory improvement.
Compiler VmHWM1651644KiB; kani-driver3915648KiB; sampled process-sum3652644KiB; command wall566.02s incl compilation.
Cloud Build start->finish981.710067s; own1/2 builds, cost$0.2295, reserved$0; cap$2.50, project cap$88.96 unchanged.
Static ordinary exact200/cfg-on391 and runtime/tooling preserved; library/request unchanged after G1; no new ordinary proof credit.
Next: STOP. G2/N13 NOT_RUN; no compile error, so coverage/semantic retry is outside this task's allowed retry branch.
Open: accepted full-cover matching A/B calibration; N13 leaf/caller/controls; old function-item F transfer and broader domains.
No arbitrary T/FnMut/backing/offset/N18, stability/init-detection/full alias-validity/unwind, trait-PFC or Part1/v6 claim.
Evidence: netcomp/g1.{summary.md,rows.txt,peaks.txt,checks-lines.txt,cover-grep.txt,tooling.txt,status.json,cost.txt,assessment.json}.
NETCOMP ЗАВЕРШЁН
