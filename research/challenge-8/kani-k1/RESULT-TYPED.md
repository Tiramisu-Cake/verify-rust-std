# TYPED — G1 submitted, PARTIAL / evidence pending

Coordinator Claude Code; worktree `/root/verify-rust-std-kani-typedoracle` only.
T0 conservative 2026-10-31 12:46:00 UTC (first clock12:46:33); deadline17:46, closing17:16 UTC.
Branch `experiment/kani-k1-typedoracle-20261031`; no force/history rewrite.
Base `e0ff82577dc58950621dadc9c141d88a5821987f`, library
`c522edd42ae67c385e1ee42a1c4d1bffb611c90b` (frozen INTEG2 candidate, no green full CI claim).
Cap `6b12002d79b6ccb4ded6c4790b1c592c65d6c591`: CAP_USD88.96, existing exception only.
Source `241d94a41182ed6850244e0b51ddc8031daf7435`, pilot library
`702a552ae226f885fe03ef5e8af0a386848587ac`; same tree required for G1/G2 after GO.
Kani `9461e07af7ec929f050aa4192f29363c9be07779`, toolchain nightly-2026-10-12;
lane/flags/pins unchanged, --no-assert-contracts / --object-bits12 retained, uninit checks OFF.
Source/research commits separate, all [skip ci]. No local compiler/proof runs; authorized Cloud G1 submitted.

Prepared native B: real G8/S8 u64 sortedness + full-value count; optional real G9 u8 native.
G8 projected-generic isolates initializer; native B removes old generic count from final checker.
S8 preserves const-repeat scratch48; G9 preserves original real general/nonconst internal fixture.
Projected actual A13 uses original bidirectional_merge PFC/contract/F/layout; generic ensures unchanged.
Bridge uses arbitrary u64/u8 x,p and arbitrary unobserved tails, no assumptions/stubs; NOT_RUN.
Payload controls: real general N2, low-bit flip, cover, same native checker; NOT_RUN.
Count semantic assertion `typed_oracle.rs:60`, macro instantiations68(u64)/69(u8);
actual Kani failure file:line/class UNKNOWN until build. Sortedness must pass, only count may fail.

| Pair | Old | New | Verification/wall/RSS/checks/covers |
| --- | --- | --- | --- |
| G8 projection | general_direct_u64_n8 | general_u64_n8_projected_generic | NOT_RUN / UNKNOWN |
| G8 native | general_direct_u64_n8 | general_u64_n8_native | NOT_RUN / UNKNOWN |
| S8 native | stable_direct_u64_n8 | stable_u64_n8_native | NOT_RUN / UNKNOWN |
| A13 projection | merge_contract_u64_n13 | merge_u64_n13_projected_actual_pfc | NOT_RUN / UNKNOWN |
| Optional u8 | general_direct_u8_n9 | general_u8_n9_native | NOT_RUN / UNKNOWN |

G1 `c8365803-0352-4695-a86d-8ecee29b59fe`, request `typed-oracle-g1-20261031-r1`, source `cb7445b2b4d4b6714c3ac7cf7a1757314d463e8f`.
G2 `typed-oracle-g2-20261031-r1` NOT_RUN; current GO authorizes G1 only.
G1 9entries/120min/USD1.620; conditional G2 3entries/60min/USD0.810; both measurement/jobs1/controls.
Own spent0/reserved1.620/builds1 of2; capUSD2. Full reserves2.430 exceed cap, G2 not promised.
Fresh global and UUID/request-specific own ledger, GO, full envelope+30min closing required before dispatch.
Preparation global snapshot builds127/usedUSD65.5395/reserved1.2150/cap88.96 is not dispatch authorization.
No measured economy or proof credit. TIMEOUT censored; missing fields UNKNOWN; matcher mismatch gate=false.
After dispatch use watch and end turn; post-terminal only bounded K-1 evidence interfaces.

Prescribed rustfmt: PASS both changed .rs. Existing Python validator: PASS G1/G2 (9/3 exact entries).
Source audit: PASS ordinary parent byte identity after removing declaration; other old library unchanged;
lane/pins/flags equal cap, Rust<=100 columns. Compiler/inventory/positive/control evidence NOT_RUN.
Static A-u8 audit: COMPLETE source-only, 50 lines, `typed-oracle/A-U8-CONSUMERS.md`; gaps documented.
Artifacts: `typed-oracle/PRE-BUILD-REVIEW.md`, `SEMANTIC-AUDIT.md`, `manifest.json`, source audit,
static checker, session ledger, both requests plus validator outputs; root RUN-REQUEST is G1.
Coordinator GO for cb7445b2b4/G1 received; submitted, watcher next. No automatic retry/G2.
No native A backend, N16, ordinary/P2 migration, X6, Mac/jobs3 or B2/general proof claim.
