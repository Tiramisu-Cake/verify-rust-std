# RESULT NETTEN-LEAVES — PASS (matching u8 N10 leaf credit only, not an N10 theorem)
Runtime Claude Code, no subagents. Coordinator GO for reviewed `1914e42274cb2a7e574a0d6497c4a9922983a9cf` (PREBUILD.md).
Build `f6fdbf06-58fa-4c1d-9692-c8236cc38892`, pool k1-standard4, source_sha = reviewed SHA, Cloud SUCCESS, lane COMPLETE.
Request `netten-leaves-swap9-backing10-insert-tail9-20261102`, agent k1-merge, SHA256 `83e3a471…291c6f8094` matches.
Library commit `23ba8cfddbce1cf0313ab402fd6376d157a0f845`, tree `74e42aaa191879280e8e7827c1e32a4ac65d5f18` (base f4d3775dc5/3b6d2a51).
Pin Kani 9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12; check-tooling vs 30f77e8599 exit0, 6 bound hashes match.
measurement, controls:true, jobs1, uninit off, 600s/row, k1-standard4 4CPU/16GiB, swap off, unwind25/unwinding assertions.
Both rows: T=u8; F=U8Cmp=fn(&u8,&u8)->bool, value StrictU8::CMP = reified strict_less::<u8>; full-value model, `<`; no stubs.
Swap leaf: PFC of unchanged swap_net9 (real swap_if_less::<u8,U8Cmp>); exact any [u8;10], base+0, a!=b any <9 (prefix9),
  independent by-value any u8 probe; pair/order, count active9 and backing10, 8 non-pair cells incl. v[9] unchanged.
Insert leaf: PFC of unchanged insert_tail_profile::<StrictU8> (real insert_tail::<u8,U8Cmp>); StrictU8::set_probe(any)
  then any [u8;10]; begin base+0, tail base+9, whole backing10 writable; sorted prefix9 only from the profile requires;
  contract sorted10/count/region assigns + typed sorted10, count(pre)=count(post), probe unchanged.

| network::netcomp::netten:: row | Status | VT s | CBMC RSS KiB | Failed/total; unreachable | Covers |
|---|---|---:|---:|---|---|
| netten_swap_prefix9_backing10 | SUCCESS | 77.10969 | 355216 | 0/412;5 | 8/8 |
| netten_insert_strict_u8_begin0_tail9 | SUCCESS | 59.589855 | 1013808 | 0/631;48 | 8/8 |

Gate: identities match; both real-body PFC SUCCESS, 0 unexpected failed checks, 8/8 covers each; no TIMEOUT/OOM (dmesg none).
expectation_met=true, measurement_ok=true, gate=true, Kani exit0; static ordinary exact200 / cfg-on 397 unchanged by run.
Compiler VmHWM 1785056 KiB; kani-driver 899912 KiB; sampled process-sum 1.97 GiB @50s; command wall 220.58s incl. compile.
Cloud start->finish 604.99s; own 1/1 Build, spent $0.1485, reserved $0 (reserve was $0.675 <= stage cap $1.40).
Established: leaf credit for swap-prefix9/backing10 (frame v[9]) and StrictU8 insertion10 begin0/tail9 on these exact domains.
Not established: actual N10 route/caller composition, prefix-sorted9 from the real network, raw->summary binding, shared probe
  init/frame; other N/backings/offsets, generic T/FnMut/function-item F, tie stability, uninit detection/full alias-validity/
  unwind, Part1-v6/ordinary. U64-N13 consumer remains OPEN. No G2 (no compile error).
Evidence: netten-leaves/g1.{summary.md,status.txt,tooling.txt,cost.txt,peaks.txt,checks-grep.txt,checks-lines.txt}, PREBUILD.md.
Next: STOP after this one stage. NETTEN-LEAVES ЗАВЕРШЁН
