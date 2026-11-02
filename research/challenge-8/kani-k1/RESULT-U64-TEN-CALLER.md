# RESULT U64-TEN-CALLER — PARTIAL (positive G1 OOM/UNKNOWN; G2 controls gate PASS)
Runtime Claude Code, no subagents. Library a6010df7b451da55d4227ad5960b0c93992f10f0, tree 514c6f841cf2af3b27f6d9aa8f27c86e24c562af
(base e4c696648a/3c600416e5, registration + caller.rs only), same tree in G1 and G2. Pin Kani 9461e07af7ec929f050aa4192f29363c9be07779 /
nightly-2026-10-12; check-tooling vs 30f77e8599 exit0 (6 bound hashes) for both Builds. measurement, controls:true, jobs1, uninit off,
600s/row, gcb-e2-standard-4 -> k1-standard4 4CPU/16GiB, swap off, unwind25/unwinding assertions; no highmem/tooling/narrowing.
Route: <u64 as UnstableSmallSortTypeImpl>::small_sort -> Freeze/Copy -> network -> sort9 (25 raw swap_if_less::<u64,U64Cmp>) ->
  insertion offset9 -> one raw insert_tail(begin0,tail9) -> no_merge return. T=u64, F=U64Cmp, value StrictU64::CMP (strict_less::<u64>).
Binding (every row's log): Stub swap_if_less->swap_adapter_u64ten, insert_tail->insert_adapter_u64ten; Verified stub swap_u64_net9,
  insert_tail_profile. Closed u64/U64Cmp impls forward actual args/`*is_less`; one probe -> ContextU64Ten + StrictU64::set_probe;
  prefix9 sorted ASSERTED before insertion; count10 = prefix9 + (tail==probe) computed and checked.

| Pkg | Build / request / reviewed source | Row (...::tenleaves::caller::) | Status | VT s | CBMC RSS KiB | Failed/total; unr. | Covers |
|---|---|---|---|---:|---:|---|---|
| G1 | 06da11e6-9985-4965-9464-215cc3ddf390 / usixtyfourtencall-g1-positive-u64-n10-20261102 (628c4bfe…) / 656e806666 | u64tencall_positive_u64_n10 | UNKNOWN (OOM) | UNKNOWN | 2711020 | not printed | not printed |
| G2 | e5d4b707-4110-49ca-902e-902f171befc4 / usixtyfourtencall-g2-controls-u64-n10-20261102 (2344a3b8…) / 623c2228ca | u64tencall_swap_binding_negative_u64_n10 | FAILED expected | 1.9865115 | 48840 (1 sample, hint-only) | 1/1054;114 | 1/1 |
| G2 | same | u64tencall_insert_binding_negative_u64_n10 | FAILED expected | 130.20987 | 1409568 | 1/1054;76 | 1/1 |
| G2 | same | u64tencall_count_negative_u64_n10 | FAILED expected | 288.65643 | 2317032 | 1/1092;62 | 2/2 |

G1: Cloud FAILURE, Kani exit137; compile finished (1m04s), harness started with the 4 expected stub lines, then dmesg global OOM
  killed kani-driver (anon-rss 15764868 KiB). No VT/checks/covers. Driver ~7MiB until ~270s, then grew ~0.77GiB/30s while CBMC ran.
  Not a compile error -> G1R not allowed/not run; positive OPEN. Fresh-process hypothesis refuted: one u64 positive alone > RAM.
G1 peaks: compiler 1865500; kani-driver 15285244 sampled @503s (time -v max 15764976); process-sum 15302404 @503s; wall 9:01.43;
  Cloud 17:31:22Z->17:47:03Z. G2 peaks: compiler 2229632; kani-driver 11507076 (time -v max = same) @365s; CBMC max 2317032;
  process-sum 11500452 @365s; dmesg none_seen; wall 8:30.91; Cloud 17:53:29Z->18:08:22Z. Peaks of different Builds are not summed.
G2 only failed checks: `u64tencall actual swap adapter binding control` caller.rs:111; `u64tencall actual insert adapter binding control`
  :172; `u64tencall negative: full-value count preserved` :337 (assert span; literal :339). No other failure; no TIMEOUT/OOM.
G2 gate: expectation_met=true, measurement_ok=true, gate=true, Kani exit1 (expected), Complete 0/3 verified, 3 failures (all designated).
  Insert control passed 25 swaps + all insert premises before its marker; count control passed run/hits/frames/final posts, sorted
  after v[9]=2^41, and the same full-u64 count predicate failed (count(2^40) 10->9, low 32 bits equal).
Packages: G1 OOM (positive UNKNOWN); G1R NOT_RUN (no compile error); G2 COMPLETE gate PASS; G2R NOT_RUN (no compile error).
  No repairs applied. Own 2/4 Builds, spent $0.2160 + $0.2025 = $0.4185, reserved $0 (cap $2.80). Ledger after: builds176, used $80.3085.
Matching leaves (old Build dd2f7e52, source 9009451c82, byte-identical deps, reuse-dependencies.md): swap_u64_net9 SUCCESS 9/9
  100.61334s; insert_tail_profile<StrictU64> SUCCESS 9/9 79.74734s. Applicable, not rows of these Builds. No mixed-run VT estimate:
  positive VT UNKNOWN. No speedup claim; u8 NETTEN timings are not a u64 forecast.
Stage gate: identities/domain/reuse match; G2 controls PASS; positive NOT established (OOM) -> overall PARTIAL, no defect found.
Established: the composed u64 route compiles; raw->adapter->verified-summary binding is reached and its marker controls fire; the
  insert premises (incl. prefix9 sorted by the real network) and the count control path hold on the concrete control inputs.
Not established: the actual u64/U64Cmp N10 theorem for any [u64;10]/any probe (positive UNKNOWN); function-item F, generic T/FnMut/N,
  other backings/offsets, stability, uninit/alias-validity/unwind, trait-PFC, ordinary v6/202. Static ordinary200, cfg-on 405.
  U64-N13 remains PARTIAL. Positive needs a coordinator decision (memory profile); not started here, no further Builds.
Evidence: u64tencall/g{1,2}.{summary.md,status.txt,tooling.txt,cost.txt,peaks.txt,checks-grep.txt,checks-lines.txt}, PREBUILD.md,
  PREBUILD-G2.md, static-check.json. Next: STOP after this one stage.
