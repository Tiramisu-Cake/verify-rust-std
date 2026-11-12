# Coordinator-only CI request

Candidate: `6134e42dd1c65dc980336e7d9455aba02d423edf`, parent `dc5f5a406749a73f1c3192e0b5338441e79508bb`; exact tree recorded in TEST-MANIFEST.json. Kani candidate remains local and unpushed. Coordinator owns source delivery, workflow checkout and all CI execution. Cloud $0; this stage dispatched nothing.

Run these six corrected selectors as singletons with their exact named harnesses, plus the two initialized companions (all under `tests/expected/uninit/unresolved-calls/`):

| Selector | Harness | Required outcome |
|---|---|---|
| `fn-trait-pointer-plain`, `fn-trait-pointer-seeded` | `check` | FnPtr Unsupported, preserved scalar 42 assertion source; no bodyless Shim claim |
| `tuple-maybe-uninit-plain`, `tuple-maybe-uninit-seeded` | `tuple_maybe_uninit_layout_is_unsupported` | Exact tuple-type layout Unsupported, not arbitrary failure or direct-shadow guard |
| `item-return-uninit-plain`, `item-return-uninit-seeded` | `item_return_preserves_uninitialized_read` | Reached u16 uninit-read FAILURE through Item return0, preserving false |
| `item-return-initialized-plain`, `item-return-initialized-seeded` | `item_return_preserves_initialized_value` | Reached u16 read SUCCESS, scalar assume_init()==7 SUCCESS through Item return0, preserving true |

Export curated JSON property data per harness, preserving original process exits and exact source/test/toolchain/flags identities. Bind every expected named property to its exact source/terminator and inspect all extra failures; no invented property IDs. Confirm no unexpected FAIL/ICE and no lost read/load or protocol properties. Goldens are substring contracts; they do not establish property counts or execution order.

Provide actual MIR and resolved call kind/body/ABI, tuple argument form and destination, not just source FnOnce syntax. For Item companions confirm supported bodyful nonforeign Item pairing, mandatory return0, signature/count/index/size checks, false/true transfer and reached read. For tuple controls provide complete diagnostic and its layout site. For FnPtr controls bind the actual local rejection and no earlier seed/points-to abort.

Where required for B1I acceptance, include unchanged entry-initialized/partial and pending-ops plain/seeded controls plus the four compiler-input specifications in COVERAGE-GAPS.md: entry loads → operand checks → Unsupported, exactly one call target, retained prior seeds/edges. Establish actual initial target set for plain and actual copy seed collection/relevance/delayed pass activation for seeded; helper presence alone proves neither. Specifications lacking an executor remain NOT_RUN, not source-probe PASS.

After targeted validation, run the existing complete Uninit Quick on this exact candidate SHA (or record exact workflow-only child/source relation and diff): fmt/build/Clippy, expected uninit, kani Uninit, ui, mem-init-reinstrumentation; retain all existing controls and report updated selector inventory/counts. Source inventory is 26 unresolved-call selectors/harnesses (4 expected SUCCESS, 22 negatives), 33 unchanged existing-control harness entries, and 4 unexecuted compiler specifications. These are not a prediction of full Quick totals or proof obligations.

List known `maybe-uninit-initialized` legal raw_eq failure separately: D0/model blocker, goldens unchanged. Expected final Part 1 remains **BLOCKED** under decision B until model and gates close. Any other new FAIL/ICE or missing required read/load property → STOP and separate production-repair task; do not alter checks/goldens just to make CI green. Stop this stage after static handoff; targeted/Quick results require a subsequent coordinator-authorized stage.
