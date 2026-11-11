# KANI3300 G1R3A — bounded result

- Build `eb04f8fc-4ee3-4568-8053-388b7ffa72c7`: **FAILURE / TOOL_ERROR**, gate false; source `98d6fffaf96c9a02d989ba1208365bd45f23ef2f`; attempt 1/1 terminal, no repair/retry/B.
- **1 native PASS, 1 FAIL** (negative reporter ERROR). Kani/compiletest builds source-reported successful: 351 s / 17 s.
- Request `2f5bdab60569918095f22b818bc403c572b0973f40f11ab6b1051022ddc675c5`, patch `59e556e7942bf717107a6ff293fef66b13d3e3994d8c931ec8dba7f8c2e41e87`, applied tree `1faeb244d2b054393141ce971180cdc2a5b6e64e` match approved A3.
- Native pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; `check-tooling` against KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` PASS (pool/lane/6 bound files/request/patch/tree).
- Build wall 660.372 s; queue 51.557 s; summed native wall 75.454 s. Spend **$0.1620** (12 rounded min), cumulative G1 **$0.4860 ≤ $0.80**, reserved $0; four-build G1 ledger `4 0.4860 0.0000`.
- Brief exit 1: `Reader report or query route is unavailable (HTTP 404)`; authorized bounded summary/native/native-field used. Summary SHA-256 `c945b701df809c118922bbc2f9509beb3d5817eabe7694c938ea55c1be6d2971`; independent B1/B2 credit NONE.

| Selector under tests/expected/uninit | Native | Reporter / terminal / exit | Wall s | Kani harness outcomes |
|---|---|---|---|---|
| `g1-union-pointee-negative/main.rs` | FAIL | ERROR / FAILED / 1 | 74.586 | Expected 0 SUCCESS / 70 FAILURE; observed counts and complete per-harness list UNKNOWN. |
| `g1-union-pointee-unsupported-reject_manuallydrop_union/main.rs` | PASS | PASS / ok / 0 | 0.868 | Exact helper-owned golden matched; 0 SUCCESS / 1 FAILURE is source-reported inference from PASS. |

Bounded negative Failed Checks excerpt (diagnostic context, **not established cause of native failure**):

| Property | Failure | Location in negative/main.rs |
|---|---|---|
| `fat_pointer_field_value_uninit_rust.safety_check.3` and `.4` | Uninitialized pointer read of `*const [u8]` | 715:24; same function |
| `fat_pointer_field_value_uninit_c.safety_check.3` | Uninitialized pointer read of `*const [u8]` | 708:24; same function |

- These are intended negative controls. Reporter error is only `requested native PASS did not pass`; bounded output does not identify which golden expectation failed or establish the four repaired moved-source harness outcomes.
- Excerpt retains 16 lines; 1952 of 1968 failure-context lines and 50240 total lines omitted (duplicated streams included; not counts of unique checks/harnesses). No Complete counters or exhaustive failure list; do not infer outcomes from expected 70 or omitted lines.
- ManuallyDrop diagnostic: unsupported tracking of `ManuallyDrop<U>` because it contains union U as a field; native PASS matches `std::mem::ManuallyDrop::<U>::new.unsupported_construct.1` with unchanged reason/FAILURE/summary.
- Receipts: `G1R3A-OBSERVATIONS.json`, `G1R3A-NATIVE-{NEGATIVE,MANUALLYDROP}.json`, `G1R3A-NEGATIVE-EXCERPT{,-META}.json`, `G1R3A-NEGATIVE-ERRORS.json`, `G1R3A-G1-BUDGET.txt`.
- No raw logs/archives/credentials read; no source/golden/tool repair, ledger-history edits, proof credit, retry or B. Preparation inventory remains the approved snapshot at `3b2861eda4`. Stop for coordinator review.
