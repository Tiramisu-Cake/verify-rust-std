# TYPED — PARTIAL; G1 complete, gate=false; recommendation STOP

Coordinator Claude Code; worktree `/root/verify-rust-std-kani-typedoracle` only.
T0 conservative2026-10-31 12:46:00 UTC (first clock12:46:33); deadline17:46, closing17:16 UTC.
Branch `experiment/kani-k1-typedoracle-20261031`; commits [skip ci], no force/history rewrite.
Base `e0ff82577dc58950621dadc9c141d88a5821987f`, library
`c522edd42ae67c385e1ee42a1c4d1bffb611c90b` (INTEG2 candidate, not green full CI).
Cap `6b12002d79b6ccb4ded6c4790b1c592c65d6c591`: existing CAP_USD88.96 exception unchanged.
Library source commit `241d94a41182ed6850244e0b51ddc8031daf7435`;
frozen pilot library tree `702a552ae226f885fe03ef5e8af0a386848587ac`, unchanged after GO.
G1 source/request SHA `cb7445b2b4d4b6714c3ac7cf7a1757314d463e8f` (explicit coordinator GO).
G1 UUID `c8365803-0352-4695-a86d-8ecee29b59fe`, request `typed-oracle-g1-20261031-r1`;
request SHA256 `66c2af602d22e45d3756349143aa42258fdde2dbc244ae06111bb0c9a5596895`.
Kani `9461e07af7ec929f050aa4192f29363c9be07779`; repository toolchain nightly-2026-10-12 unchanged.
check-tooling PASS actual pool/lane/six bound files vs full cap SHA; runtime rustc string UNKNOWN.
Actual gcb-e2-standard-4/k1-standard4, Linux jobs1,controls ON,swap OFF,uninit checks OFF.
Cloud FAILURE; summary COMPLETE/tool build success; Kani exit1, aggregate gate/measurement=false.
Own costUSD0.5400/reserved0, builds1/2; no active own build. MaxUSD2 preserved.
Cloud execution12:53:42.927707637→13:33:22.779046 UTC; verify starts330s after validation.
Whole verify invocation incl library compilation: wall1998.06s,maxRSS2322532KiB; separate from pairs.

Native B: real G8/S8 u64 sortedness+full-value count, original lt_u64, scratch/F/unwind34 preserved.
G8 projected-generic changes initializer only; native variants replace final count, add safety checks.
Projected actual A13: original PFC actual bidirectional_merge, generic callee ensures/layout/F unchanged.
Bridge: full arbitrary u64/u8 x,p and unused tail, no assumptions/stubs; SUCCESS with completion.

| Entry (merge:: prefix; new entries typed_oracle::) | Status | Verify s | fail/total(unreach) | covers | CBMC PID:KiB |
| --- | --- | --- | --- | --- | --- |
| general_direct_u64_n8 | SUCCESS | 190.83966 | 0/407(62) | 1/1 | 9294:1584636 |
| general_u64_n8_projected_generic | SUCCESS | 274.23306 | 0/434(62) | 1/1 | 9488:1597668 |
| general_u64_n8_native | SUCCESS | 245.28836 | 0/611(54) | 1/1 | 9459:1543356 |
| stable_direct_u64_n8 | SUCCESS | 130.50938 | 0/405(62) | 1/1 | 9267:770328 |
| stable_u64_n8_native | SUCCESS | 127.12238 | 0/609(54) | 1/1 | 9430:726920 |
| merge_contract_u64_n13 | SUCCESS | 434.62630 | 0/442(84) | 1/1 | 9332:2231068 |
| merge_u64_n13_projected_actual_pfc | SUCCESS | 467.07452 | 0/469(84) | 1/1 | 9401:2235640 |
| probe_bridge_u64_u8 | SUCCESS | 1.3681898 | 0/190(70) | 1/1 | 9517:43416 |
| value_corruption_control_u64_n2 | FAILED | 5.6921606 | 1/613(67) | 1/1 | 9361:193352 |

All9/9 covers satisfied; each wrapper has one completion cover; exact property IDs/messages UNKNOWN.
No TIMEOUT/OOM/missing rows. CBMC9/9 direct metadata/PID attribution, sampling2s; source/request bound.
Per-harness wall and driver/PID RSS UNKNOWN: bounded interface supplies no such fields.
Whole-command driver peak1226980KiB cannot be allocated to individual harnesses.
Count assertion source `typed_oracle.rs:60`, macro invocation68(u64)/69(u8); control cover after flip.
Actual single failure: placeholder message at typed_oracle.rs:68 in assert_u64_properties::<lt_u64,2>.
Both sortedness/count assertions share that expansion location; exact property/class UNKNOWN.
Thus count-only control acceptance remains PARTIAL/UNKNOWN; source reasoning is not proof binding.
expect_check mismatch stays gate=false; no source/matcher fix or automatic retry.
Eight accepted positive bounded rows retained separately; no pilot/theorem/migration credit transfer.

| Pair | Verification time change | CBMC RSS change |
| --- | --- | --- |
| G8 projection vs baseline | +43.70% | +0.82% |
| G8 native vs baseline | +28.53% | -2.61% |
| S8 native vs baseline | -2.60% | -5.64% |
| A13 projection vs baseline | +7.47% | +0.20% |
| G8 projected→native, count-only observation | -10.55% | -3.40% |

Ratios are single-run positive-row observations; extra checks/bridge/control/setup remain separate.
No consistent useful gain across required pairs: recommend STOP; no migration/X6/ordinary/P2 admission.
G2 u8 NOT_RUN (current GO G1 only); request `typed-oracle-g2-20261031-r1` retained, no measured u8 savings.
Native u8 helper/G9 copy/N2 control prepared. Budget alone would permit G2, but supplies no GO.
Static A-u8 audit COMPLETE/source-only,50lines; actual consumers/shifted geometry and gaps documented.
Prescribed rustfmt PASS both .rs; validator PASS G1/G2; ordinary source projection byte-identical,
other old library/lane/pins/flags unchanged. No local compiler/proofs or raw/archive evidence access.
Evidence/metrics/manifest/session and G1-ANALYSIS.md are in typed-oracle/; requests remain reviewable.
B1 bounded positive results only; uninit off, jobs3/Mac,N16,new typed A backend and B2/general proof OPEN.
