# RESULT NET18-LEAVES — PARTIAL (both swap placements SUCCESS, merge18 TIMEOUT)
Coordinator GO/reviewed source `8567fa24d2226aafc2539fd990f777216c291199`; one exact three-row G1 packet, Runtime Claude Code.
Build `b05d30cc-f789-4946-b0c7-e1cbad944aae`; request `net18-leaves-swap18-merge18-scratch32-20261102`, SHA256 `bee157bf…3459d` matches.
Library commit `4eb7e81259f843da6517a8de97c68e23b584eb76`, tree `1fa41b3a5f101ee3981787f71588bfc22e2aae5b` (base tree 3b6d2a51…).
Pin Kani9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12; check-tooling vs30f77e8599 PASS; bound hashes = NETCOMP2.
Dispatch via same-SHA alias branch `experiment/kani-k1-neteighteenleaves-20261102`: k1g.sh regex [a-z]+ rejects digits (g1.dispatch.txt).
measurement, controls:true, jobs1, uninit off, 600s/row, k1-standard4/16GiB, swap off; unwinding assertions on.
T=u8; F=U8Cmp=fn(&u8,&u8)->bool, value StrictU8::CMP=reified strict_less::<u8>; no stubs/assumes; targets unchanged.
Swap leaves: PFC swap_net9, unrestricted initialized [u8;18], independent by-value probe, local a!=b<9; left base+0
(active9 global0..8), right base+9 (active9 global9..17); unwind25. Checked pair transfer/order, active9 and
whole-backing18 count, every backing18 value outside the global pair unchanged (frame across the half boundary).
Merge leaf: PFC merge_profile::<StrictU8>, set_probe(any) then any source[u8;18], sorted halves9 only via requires;
dst separate MaybeUninit<[u8;32]> offset0, prefix18 written, tail never read; unwind34.

| network::netcomp::neteighteen:: row | Status | VT s | CBMC RSS KiB | Failed/total; unreachable | Covers |
|---|---|---:|---:|---|---|
| net18_swap_left_backing18 | SUCCESS | 63.211487 | 388296 | 0/409;5 | 7/7 |
| net18_swap_right_backing18 | SUCCESS | 71.6207 | 354188 | 0/409;5 | 7/7 |
| net18_merge_strict_scratch32 | TIMEOUT (cap600) | UNKNOWN | 3245732 (sampled) | UNKNOWN | UNKNOWN |

Merge CBMC pid active 78..676s of the run ("CBMC timed out"); no VT printed; dmesg OOM none_seen, not OOM.
Merge peak: time -v single-process max 3245924KiB, above sampled 3245732KiB; well under 16GiB, so time-bound, not memory.
Compiler VmHWM1855968KiB; kani-driver464012KiB; sampled process-sum3271456KiB; command wall846.73s incl. compile.
Cloud start->finish1266.857s; Cloud FAILURE / lane COMPLETE; gate=false, expectation_met=false; Kani exit1 from the timeout.
Own1/1 Build, spent$0.2970, reserved$0 (reserve$0.810 <= stage cap$1.70); project cap$88.96. No G2: resource failure.
Static: ordinary exact200 unchanged; cfg-on395->398 (3 new names); pfc_order21/bad0; rustfmt/diff-check PASS. Not proofs.
Established: matching leaf credit only for swap_net9 at backing18 offsets0 and9 in the stated u8/U8Cmp/StrictU8 domain.
NOT established: merge18 source->scratch32 prefix18 leaf (TIMEOUT); actual N18 composition; caller binding,
half-count invariants, merge premises or copy-back. No arbitrary backing/offset/T/FnMut/function-item F/N32,
tie stability, init detection, full alias-validity/unwind, ordinary or Part1/v6 credit.
Open: merge18 under600s needs a coordinator decision (not narrowed input/probe, no bound change here).
Evidence: net18leaves/g1.{summary.md,rows.txt,checks-lines.txt,peaks.txt,tooling.txt,status.json,cost.txt,dispatch.txt}; PREBUILD.md.
Next: STOP. NET18-LEAVES ЗАВЕРШЁН
