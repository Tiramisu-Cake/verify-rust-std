# RESULT U64-TEN-LEAVES — PASS (matching u64 N10 leaf credit only, not an N10 theorem)
Runtime Claude Code, no subagents. Coordinator GO for reviewed `9009451c82740af506708b7a2217099b57970807` (PREBUILD.md).
Build `dd2f7e52-52a5-46fd-a8a2-d5658713ad90`, pool k1-standard4, source_sha = reviewed SHA, Cloud SUCCESS, lane COMPLETE.
Request `usixtyfourten-swap9-backing10-insert-tail9-20261102`, agent k1-network, SHA256 `251b71d5…fe5d4da42` matches.
Library commit `e4c696648a5a4ff4f92dbe1ec7ed145afea25ee8`, tree `3c600416e508b037ebdfe817f6dc93d0314c9b21` (base 9ab925b157/fddf308321/d22566ab5a).
Pin Kani 9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12; check-tooling vs 30f77e8599 exit0, 6 bound hashes match.
measurement, controls:true, jobs1, uninit off, 600s/row, k1-standard4 4CPU/16GiB, swap off, unwind25/unwinding assertions.
Both rows: T=u64; F=U64Cmp=fn(&u64,&u64)->bool, value StrictU64::CMP = reified strict_less::<u64>; full-value model, `<`; no stubs.
Swap leaf: PFC of unchanged swap_u64_net9 (real swap_if_less::<u64,U64Cmp>); exact any [u64;10], base+0, a!=b any <9 (prefix9),
  independent by-value any u64 probe; pair/order, count active9 and whole10, 8 non-pair cells incl. v[9]==pre[9].
Insert leaf: PFC of unchanged insert_tail_profile::<StrictU64> (real insert_tail::<u64,U64Cmp>); StrictU64::set_probe(any)
  then any [u64;10]; begin base+0, tail base+9, whole backing10 writable; sorted prefix9 only from the profile requires;
  contract sorted/model-count/region assigns + typed sorted10_u64, count(pre)=count(post), probe unchanged.

| network::u64nine::tenleaves:: row | Status | VT s | CBMC RSS KiB | Failed/total; unreachable | Covers |
|---|---|---:|---:|---|---|
| u64ten_swap_prefix9_backing10 | SUCCESS | 100.61334 | 397352 | 0/413;5 | 9/9 |
| u64ten_insert_strict_u64_begin0_tail9 | SUCCESS | 79.74734 | 992880 | 0/640;48 | 9/9 |

Gate: identities match; both real-body PFC SUCCESS, 0 unintended failed checks, 9/9 covers each incl. high-bit (>=2^40) hits;
no TIMEOUT/OOM (dmesg none_seen); expectation_met=true, measurement_ok=true, gate=true, Kani exit0 (2/2 verified).
Static (unchanged by run): ordinary exact200, cfg-on 399->401 (+2 tenleaves names), pfc_order 21/bad0. New fixtures; no u8 speed claim.
Compiler VmHWM 1793664 KiB (time -v max 1796156); kani-driver 1102256 KiB; sampled process-sum 2050316 KiB @48s.
Command wall 260.64s incl. compile; Cloud start->finish 609.48s. Own 1/1 Build, spent $0.1485, reserved $0 (reserve $0.675 <= cap $1.40).
Established: leaf credit for u64 swap-prefix9/backing10 (frame v[9]) and StrictU64 insertion10 begin0/tail9 on these exact domains.
Not established: whole actual N10 route/caller, prefix-sorted9 from the real network, raw->summary binding, shared probe init/
  frame; function-item F, generic T/FnMut, other N/backings/offsets, tie stability, uninit detection/full alias-validity/unwind,
  ordinary v6 credit. Caller = new stage (NETTEN-CALLER driver~14GiB: consider highmem in advance); not started. No G2.
Evidence: u64ten-leaves/g1.{summary.md,status.txt,tooling.txt,cost.txt,peaks.txt,checks-grep.txt,checks-lines.txt}, PREBUILD.md.
Next: STOP after this one stage. U64-TEN-LEAVES ЗАВЕРШЁН
