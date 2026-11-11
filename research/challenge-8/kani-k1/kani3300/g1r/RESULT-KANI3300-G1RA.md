# KANI3300 G1RA — bounded result

- Build `8b32494f-c7bb-415c-acd6-8e64575fc447`: **FAIL / TOOL_ERROR**, gate false; source `132bb47b1c8688297d784f52b71bd1b5db97cf44`.
- Kani/compiletest **build success (source-reported)**: 259 s / 18 s. Runtime patch `47e625bab9d19dab22e4ec0682ecd4f561a180c022e7c09e29b205d7abcb7339`, tree `2fdd891e1c8e7d9fbaf51a6c7170d5dea6f127c5` and request `996eaa06da3e57d4d44bcc962e9f3301265f4eb9301cd30b97489ce67a051bcd` match approved identities.
- Build wall **458.809 s**, queue **59.284 s**, summed native invocation wall **16.353 s**. Spend **$0.1080** (8 rounded minutes × $0.0135); cumulative G1 **$0.1755 ≤ $0.80**, reserved $0.
- **15 PASS, 5 FAIL (reporter ERROR)**. Aggregate positive/negative fixtures did not compile: their 63/70 harness expectations were not exercised. Expected rejection PASS does not give positive proof credit.
- Evidence Brief returned HTTP 404. Results are source-reported through the requested bounded summary/native-field routes; summary SHA-256 `72d5516353e7738d50062bc84796c38de51ade3918ed5234e27df674a310824a`. Independent B1/B2 credit NONE; no raw logs/archives read.

| # | Selector under tests/expected | PASS/FAIL | Reporter | Wall s |
|---|---|---|---|---|
| 01 | `uninit/g1-union-pointee-positive/main.rs` | FAIL | ERROR | 0.316 |
| 02 | `uninit/g1-union-pointee-negative/main.rs` | FAIL | ERROR | 0.316 |
| 03 | `uninit/g1-union-pointee-unsupported-reject_array_element/main.rs` | PASS | PASS | 0.767 |
| 04 | `uninit/g1-union-pointee-unsupported-reject_bodyless_transfer/main.rs` | PASS | PASS | 0.767 |
| 05 | `uninit/g1-union-pointee-unsupported-reject_fn_pointer_field/main.rs` | PASS | PASS | 0.667 |
| 06 | `uninit/g1-union-pointee-unsupported-reject_foreign_mutation/main.rs` | PASS | PASS | 0.918 |
| 07 | `uninit/g1-union-pointee-unsupported-reject_indirect_call/main.rs` | PASS | PASS | 0.868 |
| 08 | `uninit/g1-union-pointee-unsupported-reject_init_predicate/main.rs` | FAIL | ERROR | 1.169 |
| 09 | `uninit/g1-union-pointee-unsupported-reject_manuallydrop_union/main.rs` | FAIL | ERROR | 0.316 |
| 10 | `uninit/g1-union-pointee-unsupported-reject_niche_enum/main.rs` | PASS | PASS | 0.768 |
| 11 | `uninit/g1-union-pointee-unsupported-reject_select_unpredictable/main.rs` | PASS | PASS | 0.919 |
| 12 | `uninit/g1-union-pointee-unsupported-reject_struct_field/main.rs` | PASS | PASS | 0.767 |
| 13 | `uninit/g1-union-pointee-unsupported-reject_typed_swap/main.rs` | PASS | PASS | 1.620 |
| 14 | `uninit/g1-union-pointee-unsupported-reject_unaligned_read/main.rs` | PASS | PASS | 1.068 |
| 15 | `uninit/g1-union-pointee-unsupported-reject_unaligned_write/main.rs` | PASS | PASS | 1.370 |
| 16 | `uninit/g1-union-pointee-unsupported-reject_union_in_union/main.rs` | PASS | PASS | 0.717 |
| 17 | `uninit/g1-union-pointee-unsupported-reject_union_transmute/main.rs` | FAIL | ERROR | 0.266 |
| 18 | `uninit/g1-union-pointee-unsupported-reject_variant_padding/main.rs` | PASS | PASS | 0.667 |
| 19 | `uninit/g1-union-pointee-unsupported-reject_volatile_read/main.rs` | PASS | PASS | 0.918 |
| 20 | `uninit/g1-union-pointee-unsupported-reject_volatile_write/main.rs` | PASS | PASS | 1.169 |

Compiler errors (four selectors, six errors reported; no production Kani build error):

| Frozen source location | Error | Coordinate assurance |
|---|---|---|
| `tests/expected/uninit/g1-union-pointee-positive/main.rs:565` | E0133: holder.ptr outside unsafe | Source-located inference; diagnostic arrow unavailable |
| `tests/expected/uninit/g1-union-pointee-positive/main.rs:580` | E0133: holder.ptr outside unsafe | Source-located inference; diagnostic arrow unavailable |
| `tests/expected/uninit/g1-union-pointee-negative/main.rs:665` | E0133: holder.ptr outside unsafe | Source-located inference; diagnostic arrow unavailable |
| `tests/expected/uninit/g1-union-pointee-negative/main.rs:680` | E0133: holder.ptr outside unsafe | Source-located inference; diagnostic arrow unavailable |
| `tests/expected/uninit/g1-union-pointee-unsupported-reject_manuallydrop_union/main.rs:13` | dangerous_implicit_autorefs: Implicit autoref of raw ManuallyDrop<U> pointer | Source-located inference; diagnostic arrow unavailable |
| `tests/expected/uninit/g1-union-pointee-unsupported-reject_union_transmute/main.rs:10` | E0422: TransmuteU absent from scope | Source-located inference; diagnostic arrow unavailable |

The excerpts report aborting due to 2/2/1/1 errors, but omit complete diagnostic coordinates. Locations above are explicit inferences from the unchanged candidate, not a claim that every stderr location was observed. Exact exhaustive diagnostics remain UNKNOWN; requested permitted bounded file:line records from the coordinator. No repair or raw fallback.
- `reject_init_predicate`: intended Unsupported appeared at `library/kani/src/lib.rs:63:1`; actual property `kani::mem::is_initialized::<U>.unsupported_construct.1` differs from golden `reject_init_predicate.unsupported_construct.`. Source-observed golden mismatch; no golden changed.
- Receipts: `G1RA-OBSERVATIONS.json`, `G1RA-DIAGNOSTIC-EXCERPTS.json` (including omission counts).
- Attempt **1/1** finished. No repair/retry; Kani candidate remains unchanged and local. **B not installed or run**. Stop for coordinator review.
