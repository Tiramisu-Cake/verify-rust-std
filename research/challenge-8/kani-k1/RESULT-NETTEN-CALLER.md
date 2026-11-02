# RESULT NETTEN-CALLER — PASS (actual Unstable u8/U8Cmp N10 composition, opt-in research)
Runtime Claude Code, no subagents. Coordinator GO for reviewed `d6947d47679387c632a25fc187067bc0f0505b1f` (nettencall/PREBUILD.md).
Build `ea3fee3a-98aa-47f2-aa6e-d13c5cb546a0`, pool k1-standard4, source_sha = reviewed SHA, Cloud SUCCESS, lane COMPLETE.
Request `nettencall-u8-n10-swap9-insert-tail-caller-20261102`, agent k1-merge, SHA256 `799bc58a…c180d34dab` matches.
Library commit `2ebda13e1445186f53a12b69a4419aafe4f17e1b`, tree `40d3b22c82551eafb6d55510bf0bba2bcfbebf74` (base 23ba8cfddb/74e42aaa19).
Pin Kani 9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12; check-tooling vs 30f77e8599 exit0, 6 bound hashes match.
measurement, controls:true, jobs1, uninit off, 600s/row, k1-standard4 4CPU/16GiB, swap off, unwind25/unwinding assertions.
Domain: T=u8; F=U8Cmp=fn(&u8,&u8)->bool, value StrictU8::CMP = reified strict_less::<u8>; full-value model, `<`.
Positive: unrestricted any [u8;10], independent any u8 probe, exact initialized backing10, offset0; no assume/any_where.
Route unchanged: entry -> Freeze/Copy -> network -> sort9 (25 raw swap_if_less) -> insertion offset9 -> one raw insert_tail(0,9) -> return.
Binding (trace of every row): Stub swap_if_less->swap_adapter10, insert_tail->insert_adapter10; Verified stub swap_net9,
  insert_tail_profile. Closed u8/U8Cmp impls forward actual args and `*is_less` unchanged; failures located inside
  SwapBridge10::exchange / InsertBridge10::insert for fn(&u8,&u8)->bool.
Shared probe: register10 sets ContextTen.probe and StrictU8::set_probe(probe) once before entry; prefix9 sorted ASSERTED pre-insert.
Count: initial_count10 = prefix9 + (tail==probe) computed and checked; prefix9/tail kept by swaps, count10 by insert.

| netten::caller:: row | Expect | Status | VT s | CBMC RSS KiB | Failed/total; unreachable | Covers |
|---|---|---|---:|---:|---|---|
| nettencall_positive_u8_n10 | SUCCESS | SUCCESS | 332.92896 | 2362004 | 0/1106;62 | 8/8 |
| nettencall_swap_binding_negative_u8_n10 | FAILED | FAILED expected | 1.9009693 | 39772 (1 sample, hint-only) | 1/1054;114 | 1/1 |
| nettencall_insert_binding_negative_u8_n10 | FAILED | FAILED expected | 123.02263 | 1344460 | 1/1054;76 | 1/1 |
| nettencall_count_negative_u8_n10 | FAILED | FAILED expected | 267.89996 | 2077184 | 1/1092;62 | 2/2 |

Only failed checks: `nettencall actual swap adapter binding control` caller.rs:101; `nettencall actual insert adapter
binding control` :162; `nettencall negative: full-value count preserved` :320 (span; literal :322). No other failures.
Insert control passes 25 swaps and all insert premises, then the marker; count control passes hits/frames/posts, sorted after v[9]=1, count(0) 10->9.
Gate: identities/domain/reuse match; positive SUCCESS 0 unintended failed, 8/8; controls only designated literals 1/1,1/1,2/2.
expectation_met=true, measurement_ok=true, gate=true, Kani exit1 (expected controls); no TIMEOUT/OOM (dmesg none_seen).
Matching leaves (old Build f6fdbf06, source 1914e42274, byte-identical deps per reuse-dependencies.md): swap_net9 prefix9/
  backing10 SUCCESS 8/8 77.10969s; insert_tail_profile<StrictU8> begin0/tail9 SUCCESS 8/8 59.589855s. Not rows of this Build.
Mixed-run estimate VT(B10_new)+77.10969+59.589855 = 469.628505s; NOT a same-build measurement; no direct A10, no speedup.
CBMC max over own rows 2362004KiB (positive); leaves' old max 1013808KiB, not summed.
Compiler VmHWM 2376040KiB; kani-driver VmHWM 14781664KiB (~14.10GiB, near 16GB, @816s); process-sum 14.11GiB @816s; wall 819.28s; Cloud 1202.72s.
Own 1/1 Build, spent $0.2835, reserved $0 (reserve was $0.945 <= stage cap $2.00). No G2 (no compile error).
Established: actual u8/U8Cmp/default-< N10 Unstable composition on exact backing10/offset0, unrestricted input, independent
  probe, both matching leaves, checked raw->summary binding, prefix-sorted premise, frames; opt-in research only.
Not established: function-item F, arbitrary T/FnMut, N11/N14/N18/32, other backings/offsets, stability, uninit detection/full
  alias-validity/unwind, trait-PFC. Ordinary200 / Part1-v6 202 unchanged; U64-N13 remains PARTIAL. Static cfg-on 401.
Evidence: nettencall/g1.{summary.md,status.txt,tooling.txt,cost.txt,peaks.txt,checks-grep.txt,checks-lines.txt,covers-grep.txt}.
Next: STOP after this one stage. NETTEN-CALLER ЗАВЕРШЁН
