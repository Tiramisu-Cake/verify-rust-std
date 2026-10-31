# WRAP-N2 — PRE-BUILD REVIEW, WAITING FOR GO

Task `TASK-WRAPTWO.md`; worktree `/root/verify-rust-std-kani-wraptwo` only.
Branch `experiment/kani-k1-wraptwo-20261031`, base `6f3a2629615cc7184b840d3c21aaea54b129267e`.
Library commit `471db13c99bde77722a8f717e8efeef3397eb683`; library tree `20c91cb296489182f14384a1b78b31f04eb16932`.
Pin Kani9461e07af7 / nightly-2026-10-12 unchanged. No build submitted, no proof credit.

| PFC | Selected real implementation | Domain / clauses | Result |
|---|---|---|---|
| wrap::stable_cell_n2 | Cell stable blanket fallback insertion | N2, canonical typed F, sorted >>1, scalar old full-u8 count, input-only frame | NOT_RUN |
| wrap::unstable_byte_n2 | u8 unstable → Freeze/Copy network, N2 insertion | same; real trait call, no sort9/sort13 | NOT_RUN |
| wrap::freeze_noncopy_n2 | local NonCopyU8 default Freeze general | same; local scratch, real merge/copy bodies | NOT_RUN |

Independent arbitrary u8 probe is passed by value, shared pre/post, never derived from input.
Full models are u8 / Cell.get() / inner u8; no shared statics, byte comparisons or F calls in specs.
Backing[4] active[1..3] checks prefix/suffix frame. Stable scratch backing2 exposed len0..2:
slot0 initialized and checked unchanged; uninit slot1 never read. All use unwind16.

| G1 row | Expect / literal control check | Covers | VT / RSS / failure |
|---|---|---|---|
| 1 stable_cell_n2 | SUCCESS | NOT_RUN (planned9) | NOT_RUN |
| 2 unstable_byte_n2 | SUCCESS | NOT_RUN (planned7) | NOT_RUN |
| 3 freeze_noncopy_n2 | SUCCESS | NOT_RUN (planned7) | NOT_RUN |
| 4 rejects_always_true | FAILED: wrap canonical comparator required | NOT_RUN (planned3) | NOT_RUN; guard wrap.rs:61 |
| 5 rejects_payload_corruption | FAILED: wrap full-value checker rejects payload corruption | NOT_RUN (planned1) | NOT_RUN; assert wrap.rs:227 |

Row4 reaches all three wrapper guards with invalid typed pointers, before any trait forwarding.
Row5 is a separate plain real-body call; same checker passes before the external low-bit mutation.

Own UUIDs none; spent/reserved$0. G1 request `wraptwo-g1-20261031`, measurement, controls true,
kani_jobs1, uninit off, timeout10min, exactly5 rows; reserve$1.08 (80min). ≤2 builds/≤$2.
Prebuild project ledger used$69.9135/reserved$0/cap$88.96; recheck after GO before dispatch.
G2 only after semantic/compile fix: repeat all5, own actual+reserve≤$2, else PARTIAL.
Ordinary inventory NOT_RUN: cfg-off library projection byte-identical; controls:false sees no wrap.
Optional inventory is work20+30min/$0.675 on unchanged tree only; at most2 builds in total.

Static source/request gate30 checks PASS; changed Rust rustfmt and diff --check PASS.
Separate Luna High source review found no issue; compile/PFC/native covers remain NOT_RUN.
Runtime bodies/signatures, existing verify modules, lane flags/pin/tools byte-identical to base.
F03 ordinary consumers remain StageA OPEN. Wrapper contracts are concrete forwarding contracts,
not literal trait annotations, integrated PASS or threshold-wide correctness. Three selected
specialization paths do not cover all implementations. N7/N8 needs new proofs/resources,
nontrivial general halves/merge and larger insertion; no extension or leaf stubs prepared.
Artifacts: `wraptwo/PREBUILD.md`, manifest, exact G1/G2/inventory requests, static-check and review.
Stop at PRE-BUILD REVIEW: explicit coordinator GO required before dispatch; task not complete.
