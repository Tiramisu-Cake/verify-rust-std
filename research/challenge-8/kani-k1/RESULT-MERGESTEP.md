# RESULT MERGESTEP — PARTIAL (both step leaves SUCCESS, binding confirmed; composed merge4 TIMEOUT)
Coordinator GO/reviewed source `3e3357d6e4f11c8137c313e2cac2cda1bf56ed51`; one exact six-row G1; Runtime Claude Code, no subagents.
Build `1e9c0ac0-ce89-498f-bc5b-d25c70af2279`; request `mergestep-up-down-steps-merge4-calibration-20261102`, SHA256 `fa2a217f…bc679f` matches.
Library commit `91d4d9f77a5a6e7f27b151839e6ac42114523a89`, tree `dc7c79bb9b2a779a6db2977f6142adfea835441b` (base 1fa41b3a…); owner k1-network.
Pin Kani9461e07af7 / nightly-2026-10-12; check-tooling vs30f77e8599 PASS; bound hashes = NET18-LEAVES. Branch slug letters only, no alias.
measurement, controls:true, jobs1, uninit off, 600s/row, k1-standard4/16GiB, swap off; unwind34, unwinding assertions on.
T=u8; F=U8Cmp, value StrictU8::CMP=reified strict_less::<u8>. Return encoding: scalar `bool take_left` + shared wrapping decoder.
Leaves: PFC up_step_u8/down_step_u8, no stubs; source[u8;18]=any, i!=j<18; separate MaybeUninit<[u8;32]>, up k<32 / down 1<=k<32,
mask32+init32 any (only mask cells initialized), probe any. Composed: PFC merge_profile::<StrictU8>, source18[..4] -> scratch32+0.

| network::netcomp::mergestep:: row | Status | VT s | CBMC RSS KiB | Failed/total; unreachable | Covers |
|---|---|---:|---:|---|---|
| mergestep_up_leaf_u8 | SUCCESS | 68.24657 | 440604 | 0/534;10 | 11/11 |
| mergestep_down_leaf_u8 | SUCCESS | 61.10075 | 407980 | 0/546;10 | 12/12 |
| mergestep_composed_merge4_u8 | TIMEOUT (cap600) | UNKNOWN | 2607368 | UNKNOWN | UNKNOWN |
| mergestep_up_binding_negative_u8 | FAILED, literal only | 1.0452672 | UNKNOWN | 1/528;52 | 2/4 |
| mergestep_down_binding_negative_u8 | FAILED, literal only | 2.9483438 | UNKNOWN | 1/528;27 | 3/4 |
| mergestep_count_negative_u8 | FAILED, literal only | 20.115993 | 242468 | 1/614;7 | 6/6 |

Failed literals only: `mergestep actual up adapter binding control` (:394) and `…down…` (:415), both inside
`<u8 as MergeStepBridge<fn(&u8,&u8)->bool>>::up/down`; `mergestep calibration negative: full-value count preserved` (:576).
Composed CBMC pid active128..726s, "CBMC timed out", no VT; peak 2607368KiB (= time -v whole-run max), dmesg OOM none_seen: time-bound.
Compiler2268520KiB; kani-driver1943364KiB; sampled process-sum3121728KiB; command wall902.64s; Cloud start->finish1304.04s.
Cloud FAILURE; gate=false, expectation_met=false, measurement_ok=false; Kani exit1 (timeout + expected controls).
Gate: FAIL. Composed positive TIMEOUT; binding rows miss PREBUILD-declared covers (up 2/4, down 3/4).
Cover miss cause (inferred, terse log does not name covers): Kani `kani::assert` is assert+assume, so a failed guard cuts the
path; `control: merge returned` (both) and `down adapter entered` (up row) are then unreachable. My PREBUILD reachability was wrong.
New facts: (1) up_step_u8/down_step_u8 contracts proved on the real helpers with no stubs, incl. in-target assertion that the
helper's actual raw tuple equals the shared decoder, tie/edge/partial-init covers complete. (2) Raw->summary binding on this
pin: log lists `Stub: merge_up -> up_adapter`, `merge_down -> down_adapter`, verified stubs up/down_step_u8 in all 4 roots, and
each binding guard failed inside its own adapter impl: inline(always) helpers were intercepted (H1 holds). PFC+stub+stub_verified
compiled and ran without unsupported (H2), but did not finish. (3) Count control: concrete zero input runs the whole composed
path (adapters, verified steps, ledgers, front/back order, std consumption check, post checks) and fails only on its literal.
NOT established: symbolic composed merge4 PFC (no outer sortedness/count theorem via summaries); any merge speedup (no direct4
baseline); N18/N32 caller, merge18; arbitrary backing/T/FnMut, ties stability, init detection/alias/unwind, ordinary/Part1-v6 credit.
Inherited unchanged: NET18-LEAVES swap18 credit and historical merge18 TIMEOUT (not rewritten).
Own 1/1 Build, spent$0.2970, reserved$0 (initial reserve$1.215 <= stage cap$2.50); project cap$88.96. No G2: resource/coverage failure.
Static: ordinary200 unchanged; cfg-on398->404; pfc_order24/bad0; rustfmt/diff-check PASS. Not proofs.
Evidence: mergestep/g1.{summary.md,rows.txt,checks-lines.txt,peaks.txt,tooling.txt,status.json,cost.txt}, runs.json, PREBUILD.md.
Open (coordinator decision): composed merge4 under600s; binding-cover expectations after a failing guard. Next: STOP. MERGESTEP ЗАВЕРШЁН
