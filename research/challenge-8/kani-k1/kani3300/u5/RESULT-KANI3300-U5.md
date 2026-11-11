# KANI3300 U5 — bounded diagnostic complete
Build `f4cf7bbd-b5ac-40df-b777-4ddaeb27d7f9`; head `f53c4611f8abbf0b495cccfcf8eb72a61b09fd51`.
Kani-reported COMPLETE, gate true; Cloud SUCCESS; Kani exit 1 from expected negative controls.
| Row | Status | Failed/total | Covers | Failed Checks / location |
|---|---|---|---|---|
| B1 Stable u64/N4, scratch[3] | SUCCESS | 0/547 | 3/3 | None |
| B2 Stable u64/N4, scratch[4] | FAILED, expected | 2/564 | 4/4 | Uninit `*const u64`; uninit `u64`; both `/workspace/src/library/core/src/ptr/mod.rs:1769` |
| B3 U8 general u8/N4 | SUCCESS | 0/550 | 1/1 | None |
| B4 U1 uninitialized u8 | FAILED, expected | 1/30 | 3/3 | Uninit `u8`, `/workspace/src/library/core/src/mem/mod.rs:1283` |
| B5 U2 initialized u8 | SUCCESS | 0/31 | 3/3 | None |
Source-reported bounded replay of the real Stable u64/N4 general scratch path: B1 SUCCESS, sortedness/count and normal return; no reported uninit/Unsupported/other failures.
B2 separately reading unwritten scratch[4] reports target u64 uninit plus a pointer-typed *const u64 uninit failure. This observes sensitivity for this width/path.
Pointer failure is classified separately: its cause, relation to the payload failure and independent MIR/call-site binding remain UNKNOWN.
Only normal returns with the existing panic stub, specified type/length/comparator/CMP2 patch. Reported unreachable checks B1/B2/U8: 13/13/19; calibration: 0/0.
Brief HTTP404; literal actual argv, property IDs, per-failure columns/call sites and individual cover records UNKNOWN. Post-UB covers confer no credit.
Independent B1/B2 proof credit NONE; general compound/native acceptance and Challenge 8 remain open.
Exact head/request/pin/patch/applied tree match; KT2 tooling PASS. Evidence and coverage recorded in POST-BUILD-OBSERVATIONS.json and EVIDENCE-INDEX.json.
One attempt; spend $0.1620, unfinished reserve $0, cap $0.80 (unused $0.6380); planned reserve was $0.6075. No retry or further stage.
