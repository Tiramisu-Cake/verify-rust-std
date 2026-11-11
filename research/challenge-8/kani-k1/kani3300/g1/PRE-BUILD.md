# KANI3300 G1 — PRE-BUILD REVIEW

**PREPARED, NOT AUTHORIZED, NOT RUN. Runtime Codex; one static stage; Cloud $0.**

- Kani local candidate: `45d0300e054345b4f6bdf89528195ee7c5dba8a5`; branch `fix/kani-3300-g1` in `/root/kani-fix-3300-g1`.
- Production head: `c82672f6b92b7cf0cbf28d6f645dbd0e71529e05`; tests are a separate commit. All commits authored Tiramisu-Cake; no Kani push.
- Base: `657c2b24516b967f67ce71994299d0ef328aede9`; production byte-equal to c39cc1121. No CMP2.
- Native pin: `f046b70644e113be0df9c22c2e6ea44a65a57566`. Both build patches include **all required P1 + G1 production**, relative to full f046.
- Tooling KT2: `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`, unchanged. Slug `kani3300`, stage `kani3300-g1`, owner `k1-merge`, kind `kani-tests`.
- No root lane request installed, phase/slot/ledger registered, reservation made, or Build/Actions/PR/issue/comment created.

## Exact package identities

| Package | Request SHA-256 | Patch SHA-256 | Applied tree | Diffstat bytes |
|---|---|---|---|---|
| A: `RUN-REQUEST.json` | `48bb88e982606c52aef64c5c9f9f3b0be81cb03569764074dffc21f000119ace` | `35cae231c17b836a1d0191ee417a6e9a875eb41f2f8cf353ef2b1442bf78e40b` | `bb3cb747eab1f81de9511733ec65f21fcff0bbeb` | 3013 |
| B: `RUN-REQUEST-B.json` | `ae774c0135ad562ba7f846d0de935336b3167a99bce4aa9d7ba62cb04bddc0d1` | `f9b65990a0fcb4793a5bfe54bb9fedadf4f26f8d08dc0ab817d854cb2c8a2945` | `37b330554636052a8a944b2130751b1db174ccd7` | 2734 |

Full source patch: `kani3300-g1-full.patch`, SHA-256 `61b5409610fab344ec45301a5036e7e4fe0f4315dba49f2ffbef9853356a0c76`. Its default diffstat is 5180 bytes (>4096), so the two build patches reduce **test selection only**; production is complete and identical in each.
Applied-file SHA inventories: `APPLIED-INVENTORY-A.json`, `APPLIED-INVENTORY-B.json`; preflights: `preflight-a.json`, `preflight-b.json`.
Pinned review dependencies outside the seven exported production paths have no f046-to-base drift.

## Expectations by selector

Exact source/golden/helper SHA-256, flags, all 205 named harness expectations, read/type/property bindings and request membership are in `TEST-MANIFEST.json`.
There are 23 new G1 selectors (154 harnesses) and 17 unchanged base657c/existing union selectors. Every current native outcome is **NOT_RUN**.
The 15 P1 selectors and frame golden are the renamed 657c set; their complete bytes match that base. No old c39 fixture names are dispatched.

| Package | Selector (under tests/expected) | Required outcome |
|---|---|---|
| A | `uninit/g1-union-pointee-positive/main.rs` | All 63 harnesses SUCCESS; --require-success. |
| A | `uninit/g1-union-pointee-negative/main.rs` | All 70 named FAILURE properties, own read/type bound; complete golden. |
| A | `uninit/g1-union-pointee-unsupported-reject_array_element/main.rs` | Explicit Unsupported; reject_array_element; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_bodyless_transfer/main.rs` | Explicit Unsupported; reject_bodyless_transfer; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_fn_pointer_field/main.rs` | Explicit Unsupported; reject_fn_pointer_field; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_foreign_mutation/main.rs` | Explicit Unsupported; reject_foreign_mutation; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_indirect_call/main.rs` | Explicit Unsupported; reject_indirect_call; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_init_predicate/main.rs` | Explicit Unsupported; reject_init_predicate; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_manuallydrop_union/main.rs` | Explicit Unsupported; reject_manuallydrop_union; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_niche_enum/main.rs` | Explicit Unsupported; reject_niche_enum; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_select_unpredictable/main.rs` | Explicit Unsupported; reject_select_unpredictable; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_struct_field/main.rs` | Explicit Unsupported; reject_struct_field; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_typed_swap/main.rs` | Explicit Unsupported; reject_typed_swap; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_unaligned_read/main.rs` | Explicit Unsupported; reject_unaligned_read; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_unaligned_write/main.rs` | Explicit Unsupported; reject_unaligned_write; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_union_in_union/main.rs` | Explicit Unsupported; reject_union_in_union; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_union_transmute/main.rs` | Original incompatible-layout safety FAILURE; reject_union_transmute; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_variant_padding/main.rs` | Explicit Unsupported; reject_variant_padding; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_volatile_read/main.rs` | Explicit Unsupported; reject_volatile_read; own diagnostic and 0/1/1 summary. |
| A | `uninit/g1-union-pointee-unsupported-reject_volatile_write/main.rs` | Explicit Unsupported; reject_volatile_write; own diagnostic and 0/1/1 summary. |
| B | `uninit/g1-union-pointee-unsupported-reject_bodyless_return/main.rs` | Explicit Unsupported; reject_bodyless_return; own diagnostic and 0/1/1 summary. |
| B | `uninit/g1-union-pointee-unsupported-reject_foreign_mutation_erased/main.rs` | Explicit Unsupported; reject_foreign_mutation_erased; own diagnostic and 0/1/1 summary. |
| B | `uninit/g1-union-pointee-unsupported-reject_forget_union_array/main.rs` | Explicit Unsupported; reject_forget_union_array; own diagnostic and 0/1/1 summary. |
| B | `uninit/maybe-uninit-transmute/main.rs` | All 7 harnesses SUCCESS; --require-success. |
| B | `uninit/maybe-uninit-transfers/main.rs` | All 7 harnesses SUCCESS; --require-success. |
| B | `uninit/maybe-uninit-initialized/main.rs` | All 8 harnesses SUCCESS; --require-success. |
| B | `uninit/maybe-uninit-transmute-padding/main.rs` | Expected FAILURE: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u8`; unchanged complete golden. |
| B | `uninit/maybe-uninit-transmute-source-read/main.rs` | Expected FAILURE: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u64`; unchanged complete golden. |
| B | `uninit/maybe-uninit-argument-buffer/main.rs` | Expected FAILURE: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u16`; unchanged complete golden. |
| B | `uninit/maybe-uninit-contract-clause/main.rs` | Expected FAILURE: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u16`; unchanged complete golden. |
| B | `uninit/maybe-uninit-contract-frame/main.rs` | Expected FAILURE: Failed Checks: Check that *var_7 is assignable; unchanged complete golden. |
| B | `uninit/maybe-uninit-partial-copy/main.rs` | Expected FAILURE: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `[u8; 4]`; unchanged complete golden. |
| B | `uninit/maybe-uninit-reset-alias/main.rs` | Expected FAILURE: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u8`; unchanged complete golden. |
| B | `uninit/maybe-uninit-argument-return/main.rs` | Expected FAILURE: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u16`; unchanged complete golden. |
| B | `uninit/maybe-uninit-overwrite-copy/main.rs` | Expected FAILURE: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `[u8; 2]`; unchanged complete golden. |
| B | `uninit/maybe-uninit-overlap-copy/main.rs` | Expected FAILURE: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u8`; unchanged complete golden. |
| B | `uninit/maybe-uninit-repeat-local/main.rs` | Expected FAILURE: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u64`; unchanged complete golden. |
| B | `uninit/maybe-uninit-reset-zst/main.rs` | Expected FAILURE: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u64`; unchanged complete golden. |
| B | `uninit/unions.rs` | Original 7 SUCCESS + 7 FAILURE; each original named/type-bound golden. |
| B | `uninit/uninhabited-union-field/uninhabited-union-field.rs` | read_init_ok SUCCESS; read_uninit_bytes_should_fail D(u64); no crash. |

D(T) means the exact uninitialized read diagnostic for T in the manifest/golden. Expected-mode selectors themselves must PASS compiletest; failing Kani properties are intentional only where named. Unsupported/OOM/timeout/compile/setup error never substitutes for a required uninitialized failure.

## Static validation and review

- `rustfmt` wrapper with edition 2024 and repository config: PASS; all changed Rust/include sources parsed and checked.
- New source licenses, exact manifest-to-source harness inventory, `git diff --check`: PASS.
- Both requests validate on unchanged KT2. Both patches pass `git apply --check --index` and `prepare-kani` on fresh detached f046 clones; source/golden/helper bytes equal the exact candidate.
- Independent Luna HIGH review: `REVIEW-INVARIANTS.md`, final packet `review-packet-ready/`. Initial blocking findings were repaired: pointer-byte checks before compound dereferences, rustc offsets/extent, true-Move source invalidation, and G2 ingress/no-op guards.
- Cargo/rustc/Kani/CBMC, native gate, full regression and core replay: **NOT_RUN**. Runner unchanged, so no runner service-test change is required. No independent B1/B2/general proof credit.

## Future budget proposal; no authorization

Two serial standard4 requests, each 20 selectors, 150 seconds per selector, **29 minutes native work + 30 minutes existing overhead**.
Per-request reservation: `(29 + 30) × $0.0135 = $0.7965`; proposed cap **$0.80 each**. Total reservation **$1.593**, total cap **$1.60**.
This replaces the one-packet draft budget; current spend/reservation remains **$0/$0**. Work time is an unmeasured envelope, not a claim all obligations will fit.
Before any dispatch the coordinator must review these exact requests/patches, verify cumulative ledger/deadline/slot availability and preserve the T1 priority/reserve. Each installation/dispatch requires its own exact GO. No auto-repair/retry or shortened checks/timeouts.

## Boundaries and next step

- G2 containers/wrappers, including Unaligned<U>, remain rejected; no [U;N] workaround. G1 overlap fixtures use raw aligned ordinary-byte backing plus self-copy. They do not establish every multi-slot-U overlap form.
- Typed transfers preserve only the layout-derived union-data mask; the rule is stated explicitly in `SEMANTIC-DIFF.md`, not inferred from backend observations. Padding/tail are not initialized by preservation.
- Inherited P1 limitation: non-Copy `MaybeUninit<T> ↔ T` transmute Move-source alias invalidation is not repaired by this direct-U change. The MU whitelist remains unchanged; MU<U> is G2-rejected. No general P1 soundness claim.
- Existing PFC MU-roundtrip limitation remains open. The three existing `union/static_union.rs`, `static_union2.rs`, `union_transmute.rs` belong to later full regression, with original flags/outcomes; not declared passed here.
- Coordinator review/GO is the only next boundary. Terminal evidence from any future authorized Build must use Evidence Brief; no raw log/archive fallback.

**KANI3300 G1 ПАКЕТ ГОТОВ** — static preparation only; stop at PRE-BUILD REVIEW.
