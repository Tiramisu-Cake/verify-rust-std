# KANI3300 G1R2A — bounded result

- Build `669a0594-fd09-4879-b2f3-245438d7a947`: **FAIL / TOOL_ERROR**, gate false; source `b77f5d830daf0f9efc1e3dff6250c6b0556b920a`.
- Kani / compiletest build success **source-reported**: 266 s / 17 s. Approved request `dc67daf8fce5fad977c38329133748923ebddd375924275d7537c07205f5f006`, patch `7c277d4226960f7f5907790aa9fe3022dc06567525a2ef33d0fc88747b71153b`, applied tree `f0ac57ef6ddfc8d5b24454faef807439212abc0e` match runtime report.
- **18 selectors PASS, 2 FAIL** (native reporter ERROR): aggregate negative and reject_manuallydrop_union; no retry/repair, attempt 1/1 terminal. B NOT_RUN.
- Build wall **638.907 s**, queue **53.987 s**, summed native invocation wall **167.917 s**. Spend **$0.1485** (11 rounded minutes × $0.0135), cumulative G1 **$0.3240 ≤ $0.80**, reserved $0.
- Brief: exit 1, `Reader report or query route is unavailable (HTTP 404)`. Authorized bounded summary/native/native-field only; summary SHA-256 `926b850f77f22233d7d22109ac268b120aceee02bdda282791646f9d58fe1352`. Independent B1/B2 credit NONE.

| # | Selector under tests/expected/uninit | PASS/FAIL | Reporter | Wall s |
|---|---|---|---|---|
| 01 | `g1-union-pointee-positive/main.rs` | PASS | PASS | 68.093 |
| 02 | `g1-union-pointee-negative/main.rs` | FAIL | ERROR | 72.259 |
| 03 | `g1-union-pointee-unsupported-reject_array_element/main.rs` | PASS | PASS | 0.717 |
| 04 | `g1-union-pointee-unsupported-reject_bodyless_transfer/main.rs` | PASS | PASS | 0.717 |
| 05 | `g1-union-pointee-unsupported-reject_fn_pointer_field/main.rs` | PASS | PASS | 0.667 |
| 06 | `g1-union-pointee-unsupported-reject_foreign_mutation/main.rs` | PASS | PASS | 0.867 |
| 07 | `g1-union-pointee-unsupported-reject_indirect_call/main.rs` | PASS | PASS | 0.867 |
| 08 | `g1-union-pointee-unsupported-reject_init_predicate/main.rs` | PASS | PASS | 1.118 |
| 09 | `g1-union-pointee-unsupported-reject_manuallydrop_union/main.rs` | FAIL | ERROR | 0.867 |
| 10 | `g1-union-pointee-unsupported-reject_niche_enum/main.rs` | PASS | PASS | 0.667 |
| 11 | `g1-union-pointee-unsupported-reject_select_unpredictable/main.rs` | PASS | PASS | 0.817 |
| 12 | `g1-union-pointee-unsupported-reject_struct_field/main.rs` | PASS | PASS | 0.717 |
| 13 | `g1-union-pointee-unsupported-reject_typed_swap/main.rs` | PASS | PASS | 3.133 |
| 14 | `g1-union-pointee-unsupported-reject_unaligned_read/main.rs` | PASS | PASS | 2.683 |
| 15 | `g1-union-pointee-unsupported-reject_unaligned_write/main.rs` | PASS | PASS | 3.385 |
| 16 | `g1-union-pointee-unsupported-reject_union_in_union/main.rs` | PASS | PASS | 1.728 |
| 17 | `g1-union-pointee-unsupported-reject_union_transmute/main.rs` | PASS | PASS | 1.929 |
| 18 | `g1-union-pointee-unsupported-reject_variant_padding/main.rs` | PASS | PASS | 1.626 |
| 19 | `g1-union-pointee-unsupported-reject_volatile_read/main.rs` | PASS | PASS | 2.229 |
| 20 | `g1-union-pointee-unsupported-reject_volatile_write/main.rs` | PASS | PASS | 2.831 |

Aggregate harness outcomes (Kani results distinct from native selector PASS/FAIL):

| Fixture | Expected SUCCESS / FAILURE | Observed SUCCESS / FAILURE | Basis |
|---|---|---|---|
| positive | 63 / 0 | 63 / 0 | Native PASS, exit 0 with --require-success, exact unchanged Complete-63 golden; source-reported inference, no separate per-harness raw read. |
| negative | 0 / 70 | UNKNOWN / UNKNOWN | Complete counters and harness status list absent from bounded summary/excerpt; no inference from expected golden or count of failed-check lines. |

Observed failure diagnostics (exact bounded excerpts; not an exhaustive negative-harness inventory):

| Selector | Failed Check / property | Reported location |
|---|---|---|
| negative | Unsupported initialization tracking of `ManuallyDrop<NonCopyFieldR>`; property `std::mem::ManuallyDrop::<NonCopyFieldR>::new.unsupported_construct.1` | Pinned core `mem/manually_drop.rs:181:9`, function `ManuallyDrop::<NonCopyFieldR>::new` |
| negative | Same unsupported tracking for `ManuallyDrop<NonCopyFieldC>`; property `std::mem::ManuallyDrop::<NonCopyFieldC>::new.unsupported_construct.1` | Pinned core `mem/manually_drop.rs:181:9`, function `ManuallyDrop::<NonCopyFieldC>::new` |
| reject_manuallydrop_union | Same UnionAsField(U) reason, actual `std::mem::ManuallyDrop::<U>::new.unsupported_construct.1`; golden expects caller-owned `reject_manuallydrop_union.unsupported_construct.`; compiletest reports expected output absent | Pinned core `mem/manually_drop.rs:181:9`, function `ManuallyDrop::<U>::new` |

- Pinned core path root: `/root/.rustup/toolchains/nightly-2026-10-23-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/core/src/`. These are verifier Failed Checks, not observed Rust compilation errors.
- Negative excerpt: selected 12 lines; 2004 of 2016 failure-context lines omitted (counts include different streams, not unique checks/harnesses); 51484 total lines omitted. Harness association and exhaustive differences from 70 expected uninit failures remain UNKNOWN.
- ManuallyDrop excerpt: all 12 failure-context lines retained, 1080 other lines omitted; exact helper-owned property demonstrates a golden-owner mismatch with the same intended rejection reason.
- Receipts: G1R2A-OBSERVATIONS.json, G1R2A-NATIVE-POSITIVE.json, G1R2A-{NEGATIVE,MANUALLYDROP}-EXCERPT{,-META}.json. Runtime error/native_status receipts supplement these.
- Координатор, вопрос: provide a bounded negative Complete line (SUCCESS/FAILURE/total), differing harness names and Failed Checks with file:line. Brief HTTP404 and current summary schema cannot supply these. No raw fallback or additional Build authorized.
- No tests/production/goldens changed; no raw logs/archives or credentials read; no repair/retry/B. Historical preparation inventory remains at approved research SHA.
