CFG/PFC map — static registration only; compilation NOT_RUN, proof credit NONE.

Source `9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6`, tree `64d96010b0b4b896322e26d700c253f834ba9fd6`.
Checker sha256 `d533349c1046c105b7ecaaf897041e949c19aafe989ed2198b9d5fda9c132a19`; all eight consumed source hashes in JSON.

Actual common cfg: `kani`, `kani_smallsort_sorting`, `kani_smallsort_controls`, `kani_smallsort_s2_assumed`. Each row is explicitly evaluated under this same invocation cfg.

| Root | Active stub_verified full target → matching PFC |
|---|---|
| swap_pfc | none |
| summary_witness | none |
| merge32_real | none |
| sort13_assumed | `core::slice::sort::shared::smallsort::swap_if_less` → `core::slice::sort::shared::smallsort::verify::helper_contracts::swap_safety_u8_backing4`, `core::slice::sort::shared::smallsort::verify::helper_contracts::swap_safety_u64_backing4`, `core::slice::sort::shared::smallsort::verify::helper_contracts::swap_safety_bytes17_backing4`, `core::slice::sort::shared::smallsort::verify::helper_contracts::swap_safety_u8_backing9`, `core::slice::sort::shared::smallsort::verify::helper_contracts::swap_safety_u8_backing13`, `core::slice::sort::shared::smallsort::verify::helper_contracts::rejects_swap_comparator_writing_outside_frame_u8`, `core::slice::sort::shared::smallsort::verify::sorting_s2_batch::swap_pfc` |
| general32_assumed | `core::slice::sort::shared::smallsort::sort8_stable` → `core::slice::sort::shared::smallsort::verify::sorting_s2_batch::sort8_registration_only`<br>`core::slice::sort::shared::smallsort::insert_tail` → `core::slice::sort::shared::smallsort::verify::helper_contracts::insert_tail_safety_u64_tail1_to4_backing5`<br>`core::slice::sort::shared::smallsort::bidirectional_merge` → `core::slice::sort::shared::smallsort::verify::helper_contracts::merge_safety_u64_len2`, `core::slice::sort::shared::smallsort::verify::helper_contracts::merge_safety_u64_len4` |
| merge_order_corrupt | none |
| merge_count_corrupt | none |
| checker_count_corrupt | none |
| checker_order_corrupt | none |
| sort13_weak | none |
| general32_weak | `core::slice::sort::shared::smallsort::sort8_stable` → `core::slice::sort::shared::smallsort::verify::sorting_s2_batch::sort8_registration_only`<br>`core::slice::sort::shared::smallsort::insert_tail` → `core::slice::sort::shared::smallsort::verify::helper_contracts::insert_tail_safety_u64_tail1_to4_backing5` |

Plain stubs: sort13_weak→weak_swap; general32_weak merge→weak_merge. No PFC required for explicit stubs.

This is a conservative registration-provider slice: helper_contracts and sorting_s2_batch. Other compiled providers are never counted to obtain acceptance. Ancestors from core/lib.rs through verify.rs and target declarations are parsed and hash bound. Unsupported imports/targets/cfgs, ambiguous aliases, opaque or body-local registrations fail closed. Existing u64 safety PFC registrations establish lookup presence only; they do not qualify u8 semantic summaries.

Supported syntax: explicit nested use trees/as/self/super/crate/core paths; free-function and external-module items; cfg/cfg_attr (nested all/any/not, active attribute expansion). Bodies are skipped as balanced tokens; comments, literals and raw strings cannot register a PFC. Unknown relevant cfg atoms fail closed. Attributes unrelated to item existence or registration (e.g. target-dependent allow(dead_code)) cannot affect this gate. No Rust type resolution, macro expansion, compiler-instance binding or successful compilation is claimed.

Production path: workflow checkout export → runner.py check-source → verify_source → s2_policy.validate_source → cfg_pfc.check. This precedes tool setup/build and verification. The same path runs during validate_package.py; workflow synthetic tests exercise the parser before source checkout.
