# Provisional S1 qualification — no admission

|Root|Native|Producer|Provisional assessment|Properties/U/covers/guards|
|---|---|---|---|---|
|checker_order_corrupt|FAILURE|OBSERVED/RECORDED|PROVISIONAL_S1_FIXED_NEGATIVE_LABEL_DETECTED|24/8/0/0|
|checker_count_corrupt|FAILURE|OBSERVED/RECORDED|PROVISIONAL_S1_FIXED_NEGATIVE_LABEL_DETECTED|26/1/0/0|
|sort13_weak|FAILURE|OBSERVED/RECORDED|PROVISIONAL_S1_FIXED_NEGATIVE_LABEL_DETECTED|25/8/0/0|
|i_p01_b1_16|UNKNOWN_INCOMPLETE_EXPORT|UNKNOWN/UNKNOWN|NO_COMPLETED_NATIVE_RESULT|UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY/UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY/?/?|
|m8_s32_d00_allinit|SUCCESS|UNKNOWN/UNKNOWN|PROVISIONAL_S1_BOUNDED_PFC_PENDING_LOCATION_DECISION|386/8/6/4|
|i_p16_b1_16|UNKNOWN_INCOMPLETE_EXPORT|UNKNOWN/UNKNOWN|NO_COMPLETED_NATIVE_RESULT|UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY/UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY/?/?|
|m8_s32_d00_partial_diag|SUCCESS|UNKNOWN/UNKNOWN|DIAG_INIT_OPEN|386/8/6/4|
|m8_s40_d16_partial_diag|SUCCESS|UNKNOWN/UNKNOWN|DIAG_INIT_OPEN|386/8/6/4|

Assurance: Profiles v4 SOURCE_REPORTED, exact source/cfg/native registration and property/site links; no independent AST/MIR/expansion/property-to-wrapper/caller provenance or formal B1/B2 proof. Native compilation and PFC registration alone establish no result. The stock PFC actual-body single_top_level_call/no_recursive_call and checked ensures links are recorded for each completed PFC. All literal roles/covers, including positive SUCCESS assertions, are exact same-invocation/source-site matches. Strict0/8 remains unchanged.

## checker_order_corrupt

Classification: `FIXED_NEGATIVE_CONTROL`. Assessment: `PROVISIONAL_S1_FIXED_NEGATIVE_LABEL_DETECTED`. Native `FAILURE`; producer `OBSERVED/RECORDED`; admitted false; init/provider eligibility false.

Exact domain: `{"input":[1,2],"output":[2,1]}`. Unwind34; u8 independent full0..255 subject to source order premises for symbolic fixtures. Fixed negative fixture scope stays literal. KeyLess<u8> is the stateless byte `<` comparator. SOURCE_REPORTED normal-return functional/footprint/frame scope only; no generic T/F/stability/termination/unwind/caller theorem.

|Literal role/cover|Required status|Native observation|Source site|
|---|---|---|---|
|S2_NEG_CHECKER_ORDER|FAILURE|FAILURE:slice::sort::shared::smallsort::verify::sorting_s2_batch::checker_order_corrupt.assertion.1|library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs:140|

Native class/status inventory: `{"array_bounds":{"SUCCESS":3},"assertion":{"SUCCESS":6,"UNREACHABLE":8,"FAILURE":1},"pointer_dereference":{"SUCCESS":6}}`.

Unsupported guards: observed empty for this exact negative invocation.

## checker_count_corrupt

Classification: `FIXED_NEGATIVE_CONTROL`. Assessment: `PROVISIONAL_S1_FIXED_NEGATIVE_LABEL_DETECTED`. Native `FAILURE`; producer `OBSERVED/RECORDED`; admitted false; init/provider eligibility false.

Exact domain: `{"input":"[1u8;32]","output":"out[31]=2"}`. Unwind34; u8 independent full0..255 subject to source order premises for symbolic fixtures. Fixed negative fixture scope stays literal. KeyLess<u8> is the stateless byte `<` comparator. SOURCE_REPORTED normal-return functional/footprint/frame scope only; no generic T/F/stability/termination/unwind/caller theorem.

|Literal role/cover|Required status|Native observation|Source site|
|---|---|---|---|
|S2_NEG_CHECKER_COUNT|FAILURE|FAILURE:slice::sort::shared::smallsort::verify::sorting_s2_batch::checker_count_corrupt.assertion.2|library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs:134|

Native class/status inventory: `{"array_bounds":{"SUCCESS":4},"assertion":{"SUCCESS":14,"UNREACHABLE":1,"FAILURE":1},"pointer_dereference":{"SUCCESS":6}}`.

Unsupported guards: observed empty for this exact negative invocation.

## sort13_weak

Classification: `FIXED_NEGATIVE_CONTROL`. Assessment: `PROVISIONAL_S1_FIXED_NEGATIVE_LABEL_DETECTED`. Native `FAILURE`; producer `OBSERVED/RECORDED`; admitted false; init/provider eligibility false.

Exact domain: `{"input":[12,11,10,9,8,7,6,5,4,3,2,1,0],"copy":"sort13_fault_network","ordinary_seam":"s2_swap_seam -> weak_swap","claim":"fixed descending len13 negative, not arbitrary-byte theorem"}`. Unwind34; u8 independent full0..255 subject to source order premises for symbolic fixtures. Fixed negative fixture scope stays literal. KeyLess<u8> is the stateless byte `<` comparator. SOURCE_REPORTED normal-return functional/footprint/frame scope only; no generic T/F/stability/termination/unwind/caller theorem.

|Literal role/cover|Required status|Native observation|Source site|
|---|---|---|---|
|S2_NEG_SORT13_WEAK|FAILURE|FAILURE:slice::sort::shared::smallsort::verify::sorting_s2_batch::sort13_weak.assertion.1|library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs:149|

Native class/status inventory: `{"array_bounds":{"SUCCESS":3},"assertion":{"FAILURE":1,"SUCCESS":7,"UNREACHABLE":8},"pointer_dereference":{"SUCCESS":6}}`.

Unsupported guards: observed empty for this exact negative invocation.

## i_p01_b1_16

Classification: `BOUNDED_ACTUAL_BODY_PFC_CANDIDATE`. Assessment: `NO_COMPLETED_NATIVE_RESULT`. Native `UNKNOWN_INCOMPLETE_EXPORT`; producer `UNKNOWN/UNKNOWN`; admitted false; init/provider eligibility false.

Exact domain: `{"backing":"initialized [u8;34]","begin_inclusive":[1,16],"relative_tail":1,"span":2,"premise":"prefix of length p sorted","original_pairs":16}`. Unwind36; u8 independent full0..255 subject to source order premises for symbolic fixtures. Fixed negative fixture scope stays literal. KeyLess<u8> is the stateless byte `<` comparator. SOURCE_REPORTED normal-return functional/footprint/frame scope only; no generic T/F/stability/termination/unwind/caller theorem.

|Literal role/cover|Required status|Native observation|Source site|
|---|---|---|---|
|S32_I_D1_ACTIVE|SUCCESS|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:25|
|S32_I_D1_SORTED_FULL_COUNT|SUCCESS|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:34|
|S32_I_D1_OUTSIDE_FRAME|SUCCESS|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:36|
|S32_I_D1_CANARY|SUCCESS|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:40|
|S32_I_D1_BASE_FIRST|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:41|
|S32_I_D1_BASE_LAST|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:42|
|S32_I_D1_EARLY_RETURN|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:43|
|S32_I_D1_FULL_SIFT|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:44|
|S32_I_D1_DUPLICATE|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:45|
|S32_I_D1_NONCONSTANT|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:46|
|S32_I_D1_USEFUL_RETURN|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:47|

Native class/status inventory: `{}`.

Unsupported guards: UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY.

## m8_s32_d00_allinit

Classification: `BOUNDED_ACTUAL_BODY_PFC_CANDIDATE`. Assessment: `PROVISIONAL_S1_BOUNDED_PFC_PENDING_LOCATION_DECISION`. Native `SUCCESS`; producer `UNKNOWN/UNKNOWN`; admitted false; init/provider eligibility false.

Exact domain: `{"backing":"[MaybeUninit<u8>;48]","src":32,"dst":0,"span":8,"source_sorted_halves":[4,4],"initialized_intervals":[[8,48]],"uninitialized":"complement in [0,48), including dst","prior_initialized_values":"arbitrary full bytes, source halves alone sorted","original_allinit_pairs":1,"sort8_n32_side":null}`. Unwind50; u8 independent full0..255 subject to source order premises for symbolic fixtures. Fixed negative fixture scope stays literal. KeyLess<u8> is the stateless byte `<` comparator. SOURCE_REPORTED normal-return functional/footprint/frame scope only; no generic T/F/stability/termination/unwind/caller theorem.

Known initialized outside-destination values[8,48); source[32,40), destination[0,8). Source slice contains two sorted halves4+4; output is loaded as eight typed bytes after the call, order/full multiplicity is checked, source and known initialized outside values/canary are compared. No uninitialized backing value is read by the frame/spec. A typed read plus successful stock checks is not a separate initialization-mask theorem.

|Literal role/cover|Required status|Native observation|Source site|
|---|---|---|---|
|S32_M8_ALL_ACTIVE|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.assertion.1|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:82|
|S32_M8_ALL_FUNCTIONAL_SORTED_FULL_COUNT|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.assertion.11|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:97|
|S32_M8_ALL_KNOWN_VALUE_FRAME|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.assertion.15|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:100|
|S32_M8_ALL_SOURCE_FRAME|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.assertion.20|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:104|
|S32_M8_ALL_KNOWN_CANARY|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.assertion.24|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:108|
|S32_M8_ALL_LEFT_FIRST|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.cover.1|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:109|
|S32_M8_ALL_RIGHT_FIRST|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.cover.2|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:110|
|S32_M8_ALL_TIE|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.cover.3|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:111|
|S32_M8_ALL_UNSORTED|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.cover.4|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:112|
|S32_M8_ALL_NONCONSTANT|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.cover.5|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:113|
|S32_M8_ALL_USEFUL_RETURN|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.cover.6|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:114|

Native class/status inventory: `{"arithmetic_overflow":{"SUCCESS":11},"array_bounds":{"SUCCESS":21},"assertion":{"UNREACHABLE":8,"SUCCESS":95},"assigns":{"SUCCESS":5},"assume":{"SUCCESS":2},"bit_count":{"SUCCESS":3},"cover":{"SATISFIED":6},"division-by-zero":{"SUCCESS":2},"frees":{"SUCCESS":1},"no_alloc_dealloc_in_ensures":{"SUCCESS":1},"no_alloc_dealloc_in_requires":{"SUCCESS":1},"no_recursive_call":{"SUCCESS":1},"pointer":{"SUCCESS":4},"pointer_dereference":{"SUCCESS":138},"precondition_instance":{"SUCCESS":9},"safety_check":{"SUCCESS":26},"single_top_level_call":{"SUCCESS":1},"unreachable":{"SUCCESS":43},"unsupported_construct":{"SUCCESS":4},"unwind":{"SUCCESS":4}}`.

Every unsupported guard remains visible and distinct from statusUNREACHABLE U:

|ID|Class/status|Description|Location|
|---|---|---|---|
|kani::mem::is_inbounds::<[u8]>.unsupported_construct.1|unsupported_construct/SUCCESS|Kani does not support reasoning about pointer to unallocated memory|/home/runner/work/kani/kani/export/library/core/src/lib.rs:358|
|kani::mem::cbmc::same_allocation.unsupported_construct.1|unsupported_construct/SUCCESS|Kani does not support reasoning about pointer to unallocated memory|/home/runner/work/kani/kani/export/library/core/src/lib.rs:358|
|panicking::panic_nounwind_fmt::runtime.unsupported_construct.1|unsupported_construct/SUCCESS|call to foreign "Rust" function `_RNvCseilXckri75C_7___rustc17rust_begin_unwind` is not currently supported by Kani. Please post your example at https://github.com/model-checking/kani/issues/new/choose|/home/runner/work/kani/kani/export/library/core/src/panicking.rs:110|
|panic::location::Location::<'_>::caller.unsupported_construct.1|unsupported_construct/SUCCESS|caller_location is not currently supported by Kani. Please post your example at https://github.com/model-checking/kani/issues/374|/home/runner/work/kani/kani/export/library/core/src/panic/location.rs:185|

## i_p16_b1_16

Classification: `BOUNDED_ACTUAL_BODY_PFC_CANDIDATE`. Assessment: `NO_COMPLETED_NATIVE_RESULT`. Native `UNKNOWN_INCOMPLETE_EXPORT`; producer `UNKNOWN/UNKNOWN`; admitted false; init/provider eligibility false.

Exact domain: `{"backing":"initialized [u8;34]","begin_inclusive":[1,16],"relative_tail":16,"span":17,"premise":"prefix of length p sorted","original_pairs":16}`. Unwind36; u8 independent full0..255 subject to source order premises for symbolic fixtures. Fixed negative fixture scope stays literal. KeyLess<u8> is the stateless byte `<` comparator. SOURCE_REPORTED normal-return functional/footprint/frame scope only; no generic T/F/stability/termination/unwind/caller theorem.

|Literal role/cover|Required status|Native observation|Source site|
|---|---|---|---|
|S32_I_D16_ACTIVE|SUCCESS|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:53|
|S32_I_D16_SORTED_FULL_COUNT|SUCCESS|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:62|
|S32_I_D16_OUTSIDE_FRAME|SUCCESS|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:64|
|S32_I_D16_CANARY|SUCCESS|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:68|
|S32_I_D16_BASE_FIRST|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:69|
|S32_I_D16_BASE_LAST|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:70|
|S32_I_D16_EARLY_RETURN|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:71|
|S32_I_D16_FULL_SIFT|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:72|
|S32_I_D16_DUPLICATE|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:73|
|S32_I_D16_NONCONSTANT|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:74|
|S32_I_D16_USEFUL_RETURN|SATISFIED|UNKNOWN_NO_COMPLETED_INVENTORY|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:75|

Native class/status inventory: `{}`.

Unsupported guards: UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY.

## m8_s32_d00_partial_diag

Classification: `DIAGNOSTIC_ONLY_INITIALIZATION_OPEN`. Assessment: `DIAG_INIT_OPEN`. Native `SUCCESS`; producer `UNKNOWN/UNKNOWN`; admitted false; init/provider eligibility false.

Exact domain: `{"backing":"[MaybeUninit<u8>;48]","src":32,"dst":0,"span":8,"source_sorted_halves":[4,4],"initialized_intervals":[[32,40]],"uninitialized":"complement in [0,48), including dst","prior_initialized_values":"arbitrary full bytes, source halves alone sorted","original_allinit_pairs":0,"sort8_n32_side":0}`. Unwind50; u8 independent full0..255 subject to source order premises for symbolic fixtures. Fixed negative fixture scope stays literal. KeyLess<u8> is the stateless byte `<` comparator. SOURCE_REPORTED normal-return functional/footprint/frame scope only; no generic T/F/stability/termination/unwind/caller theorem.

Known initialized values only[32,40), source[32,40), destination[0,8). Other outside-dst bytes initially uninitialized and their state is not a checked frame theorem. Source slice contains two sorted halves4+4; output is loaded as eight typed bytes after the call, order/full multiplicity is checked, source and known initialized outside values/canary are compared. No uninitialized backing value is read by the frame/spec. A typed read plus successful stock checks is not a separate initialization-mask theorem.

|Literal role/cover|Required status|Native observation|Source site|
|---|---|---|---|
|S32_M8_L_DIAG_ACTIVE|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.assertion.1|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:121|
|S32_M8_L_DIAG_FUNCTIONAL_SORTED_FULL_COUNT|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.assertion.11|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:136|
|S32_M8_L_DIAG_KNOWN_VALUE_FRAME|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.assertion.15|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:139|
|S32_M8_L_DIAG_SOURCE_FRAME|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.assertion.20|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:143|
|S32_M8_L_DIAG_KNOWN_CANARY|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.assertion.24|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:147|
|S32_M8_L_DIAG_LEFT_FIRST|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.cover.1|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:148|
|S32_M8_L_DIAG_RIGHT_FIRST|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.cover.2|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:149|
|S32_M8_L_DIAG_TIE|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.cover.3|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:150|
|S32_M8_L_DIAG_UNSORTED|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.cover.4|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:151|
|S32_M8_L_DIAG_NONCONSTANT|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.cover.5|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:152|
|S32_M8_L_DIAG_USEFUL_RETURN|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.cover.6|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:153|

Native class/status inventory: `{"arithmetic_overflow":{"SUCCESS":11},"array_bounds":{"SUCCESS":21},"assertion":{"UNREACHABLE":8,"SUCCESS":95},"assigns":{"SUCCESS":5},"assume":{"SUCCESS":2},"bit_count":{"SUCCESS":3},"cover":{"SATISFIED":6},"division-by-zero":{"SUCCESS":2},"frees":{"SUCCESS":1},"no_alloc_dealloc_in_ensures":{"SUCCESS":1},"no_alloc_dealloc_in_requires":{"SUCCESS":1},"no_recursive_call":{"SUCCESS":1},"pointer":{"SUCCESS":4},"pointer_dereference":{"SUCCESS":138},"precondition_instance":{"SUCCESS":9},"safety_check":{"SUCCESS":26},"single_top_level_call":{"SUCCESS":1},"unreachable":{"SUCCESS":43},"unsupported_construct":{"SUCCESS":4},"unwind":{"SUCCESS":4}}`.

Every unsupported guard remains visible and distinct from statusUNREACHABLE U:

|ID|Class/status|Description|Location|
|---|---|---|---|
|panic::location::Location::<'_>::caller.unsupported_construct.1|unsupported_construct/SUCCESS|caller_location is not currently supported by Kani. Please post your example at https://github.com/model-checking/kani/issues/374|/home/runner/work/kani/kani/export/library/core/src/panic/location.rs:185|
|kani::mem::is_inbounds::<[u8]>.unsupported_construct.1|unsupported_construct/SUCCESS|Kani does not support reasoning about pointer to unallocated memory|/home/runner/work/kani/kani/export/library/core/src/lib.rs:358|
|panicking::panic_nounwind_fmt::runtime.unsupported_construct.1|unsupported_construct/SUCCESS|call to foreign "Rust" function `_RNvCseilXckri75C_7___rustc17rust_begin_unwind` is not currently supported by Kani. Please post your example at https://github.com/model-checking/kani/issues/new/choose|/home/runner/work/kani/kani/export/library/core/src/panicking.rs:110|
|kani::mem::cbmc::same_allocation.unsupported_construct.1|unsupported_construct/SUCCESS|Kani does not support reasoning about pointer to unallocated memory|/home/runner/work/kani/kani/export/library/core/src/lib.rs:358|

## m8_s40_d16_partial_diag

Classification: `DIAGNOSTIC_ONLY_INITIALIZATION_OPEN`. Assessment: `DIAG_INIT_OPEN`. Native `SUCCESS`; producer `UNKNOWN/UNKNOWN`; admitted false; init/provider eligibility false.

Exact domain: `{"backing":"[MaybeUninit<u8>;48]","src":40,"dst":16,"span":8,"source_sorted_halves":[4,4],"initialized_intervals":[[0,8],[32,48]],"uninitialized":"complement in [0,48), including dst","prior_initialized_values":"arbitrary full bytes, source halves alone sorted","original_allinit_pairs":0,"sort8_n32_side":1}`. Unwind50; u8 independent full0..255 subject to source order premises for symbolic fixtures. Fixed negative fixture scope stays literal. KeyLess<u8> is the stateless byte `<` comparator. SOURCE_REPORTED normal-return functional/footprint/frame scope only; no generic T/F/stability/termination/unwind/caller theorem.

Known initialized values[0,8) and[32,48), source[40,48), destination[16,24). Other outside-dst byte states remain open. Source slice contains two sorted halves4+4; output is loaded as eight typed bytes after the call, order/full multiplicity is checked, source and known initialized outside values/canary are compared. No uninitialized backing value is read by the frame/spec. A typed read plus successful stock checks is not a separate initialization-mask theorem.

|Literal role/cover|Required status|Native observation|Source site|
|---|---|---|---|
|S32_M8_R_DIAG_ACTIVE|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.assertion.1|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:160|
|S32_M8_R_DIAG_FUNCTIONAL_SORTED_FULL_COUNT|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.assertion.11|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:175|
|S32_M8_R_DIAG_KNOWN_VALUE_FRAME|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.assertion.15|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:178|
|S32_M8_R_DIAG_SOURCE_FRAME|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.assertion.20|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:182|
|S32_M8_R_DIAG_KNOWN_CANARY|SUCCESS|SUCCESS:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.assertion.24|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:186|
|S32_M8_R_DIAG_LEFT_FIRST|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.cover.1|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:187|
|S32_M8_R_DIAG_RIGHT_FIRST|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.cover.2|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:188|
|S32_M8_R_DIAG_TIE|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.cover.3|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:189|
|S32_M8_R_DIAG_UNSORTED|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.cover.4|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:190|
|S32_M8_R_DIAG_NONCONSTANT|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.cover.5|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:191|
|S32_M8_R_DIAG_USEFUL_RETURN|SATISFIED|SATISFIED:slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.cover.6|library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs:192|

Native class/status inventory: `{"arithmetic_overflow":{"SUCCESS":11},"array_bounds":{"SUCCESS":21},"assertion":{"SUCCESS":95,"UNREACHABLE":8},"assigns":{"SUCCESS":5},"assume":{"SUCCESS":2},"bit_count":{"SUCCESS":3},"cover":{"SATISFIED":6},"division-by-zero":{"SUCCESS":2},"frees":{"SUCCESS":1},"no_alloc_dealloc_in_ensures":{"SUCCESS":1},"no_alloc_dealloc_in_requires":{"SUCCESS":1},"no_recursive_call":{"SUCCESS":1},"pointer":{"SUCCESS":4},"pointer_dereference":{"SUCCESS":138},"precondition_instance":{"SUCCESS":9},"safety_check":{"SUCCESS":26},"single_top_level_call":{"SUCCESS":1},"unreachable":{"SUCCESS":43},"unsupported_construct":{"SUCCESS":4},"unwind":{"SUCCESS":4}}`.

Every unsupported guard remains visible and distinct from statusUNREACHABLE U:

|ID|Class/status|Description|Location|
|---|---|---|---|
|kani::mem::is_inbounds::<[u8]>.unsupported_construct.1|unsupported_construct/SUCCESS|Kani does not support reasoning about pointer to unallocated memory|/home/runner/work/kani/kani/export/library/core/src/lib.rs:358|
|panic::location::Location::<'_>::caller.unsupported_construct.1|unsupported_construct/SUCCESS|caller_location is not currently supported by Kani. Please post your example at https://github.com/model-checking/kani/issues/374|/home/runner/work/kani/kani/export/library/core/src/panic/location.rs:185|
|kani::mem::cbmc::same_allocation.unsupported_construct.1|unsupported_construct/SUCCESS|Kani does not support reasoning about pointer to unallocated memory|/home/runner/work/kani/kani/export/library/core/src/lib.rs:358|
|panicking::panic_nounwind_fmt::runtime.unsupported_construct.1|unsupported_construct/SUCCESS|call to foreign "Rust" function `_RNvCseilXckri75C_7___rustc17rust_begin_unwind` is not currently supported by Kani. Please post your example at https://github.com/model-checking/kani/issues/new/choose|/home/runner/work/kani/kani/export/library/core/src/panicking.rs:110|

## All41 U occurrences

Each row below has a separate exact property/member/namespace/source hash/context/domain/cfg/target/registration record in QUALIFICATION.json. These are independently reasoned source-local arithmetic/bounds arguments within this intake; they do not enable or reuse a blanket std whitelist. Actual property-to-MIR origin remains UNKNOWN. classunreachable/statusSUCCESS metadata records are excluded from this U list.

|Root|U property ID|Source site|Predicate|Source-local argument|
|---|---|---|---|---|
|checker_order_corrupt|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.4|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:100|i<L<=32 implies i+1<=32|Order loop starts i=1 and increments only with i<L<=32, so i+1<=32.|
|checker_order_corrupt|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.5|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:106|i<L<=CAP32|Count outer loop uses i<L<=CAP32; before.values[i] is in bounds.|
|checker_order_corrupt|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.6|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:111|j<L<=32 and old_count<=j|Count inner loop uses j<L<=CAP32, bounding before.values[j]; old_count starts0 and is at most j before at most one increment.|
|checker_order_corrupt|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.7|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:111|j<L<=32 and old_count<=j|Count inner loop uses j<L<=CAP32, bounding before.values[j]; old_count starts0 and is at most j before at most one increment.|
|checker_order_corrupt|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.8|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:112|j<values.len<=32 and new_count<=j|Entry L=before.len=values.len; inner j<L bounds values[j]; new_count starts0 and is at most j before at most one increment.|
|checker_order_corrupt|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.9|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:112|j<values.len<=32 and new_count<=j|Entry L=before.len=values.len; inner j<L bounds values[j]; new_count starts0 and is at most j before at most one increment.|
|checker_order_corrupt|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.10|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:113|j<L<=32 implies j+1<=32|Inner loop increments only with j<L<=32, so j+1<=32.|
|checker_order_corrupt|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.11|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:118|i<L<=32 implies i+1<=32|Outer loop increments only with i<L<=32, so i+1<=32.|
|checker_count_corrupt|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.11|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:118|i<L<=32 implies i+1<=32|Outer loop increments only with i<L<=32, so i+1<=32.|
|sort13_weak|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.4|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:100|i<L<=32 implies i+1<=32|Order loop starts i=1 and increments only with i<L<=32, so i+1<=32.|
|sort13_weak|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.5|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:106|i<L<=CAP32|Count outer loop uses i<L<=CAP32; before.values[i] is in bounds.|
|sort13_weak|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.6|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:111|j<L<=32 and old_count<=j|Count inner loop uses j<L<=CAP32, bounding before.values[j]; old_count starts0 and is at most j before at most one increment.|
|sort13_weak|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.7|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:111|j<L<=32 and old_count<=j|Count inner loop uses j<L<=CAP32, bounding before.values[j]; old_count starts0 and is at most j before at most one increment.|
|sort13_weak|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.8|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:112|j<values.len<=32 and new_count<=j|Entry L=before.len=values.len; inner j<L bounds values[j]; new_count starts0 and is at most j before at most one increment.|
|sort13_weak|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.9|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:112|j<values.len<=32 and new_count<=j|Entry L=before.len=values.len; inner j<L bounds values[j]; new_count starts0 and is at most j before at most one increment.|
|sort13_weak|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.10|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:113|j<L<=32 implies j+1<=32|Inner loop increments only with j<L<=32, so j+1<=32.|
|sort13_weak|slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.11|library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:118|i<L<=32 implies i+1<=32|Outer loop increments only with i<L<=32, so i+1<=32.|
|m8_s32_d00_allinit|num::<impl usize>::abs_diff.assertion.1|library/core/src/num/uint_macros.rs:3222|self<other implies other-self defined|The self<other branch evaluates other-self with other>=self.|
|m8_s32_d00_allinit|slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.1|library/core/src/slice/sort/shared/smallsort.rs:974|2 != 0|Divisor is literal2, hence nonzero for every length.|
|m8_s32_d00_allinit|slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.2|library/core/src/slice/sort/shared/smallsort.rs:990|len8 implies len/2-1=3|Exact source slice has length8, half4; half-1=3 is defined.|
|m8_s32_d00_allinit|slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.3|library/core/src/slice/sort/shared/smallsort.rs:991|len8 implies len-1=7|Exact source slice has length8, so right_rev len-1=7 is defined.|
|m8_s32_d00_allinit|slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.4|library/core/src/slice/sort/shared/smallsort.rs:992|len8 implies len-1=7|Exact source slice has length8, so dst_rev len-1=7 is defined; writability and initialization remain separate.|
|m8_s32_d00_allinit|fmt::Arguments::<'_>::from_str.assertion.1|library/core/src/fmt/mod.rs:820|1 < usize::BITS64|The literal shift count1 is below x86_64 usize width64, independently of string length. No lost-bit claim.|
|m8_s32_d00_allinit|ub_checks::is_valid_allocation_size.assertion.1|library/core/src/ub_checks.rs:148|else(size==0) implies size!=0|The size==0 arm skips division; the else arm divides only by size!=0. Concrete u8 size=1 independently.|
|m8_s32_d00_allinit|ptr::const_ptr::<impl *const ()>::is_aligned_to.assertion.1|library/core/src/ptr/const_ptr.rs:1479|is_power_of_two(align) implies align>=1|Normal continuation follows is_power_of_two(align); zero is not a power of two, hence align>=1 and align-1 is defined.|
|m8_s32_d00_partial_diag|fmt::Arguments::<'_>::from_str.assertion.1|library/core/src/fmt/mod.rs:820|1 < usize::BITS64|The literal shift count1 is below x86_64 usize width64, independently of string length. No lost-bit claim.|
|m8_s32_d00_partial_diag|ptr::const_ptr::<impl *const ()>::is_aligned_to.assertion.1|library/core/src/ptr/const_ptr.rs:1479|is_power_of_two(align) implies align>=1|Normal continuation follows is_power_of_two(align); zero is not a power of two, hence align>=1 and align-1 is defined.|
|m8_s32_d00_partial_diag|slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.1|library/core/src/slice/sort/shared/smallsort.rs:974|2 != 0|Divisor is literal2, hence nonzero for every length.|
|m8_s32_d00_partial_diag|slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.2|library/core/src/slice/sort/shared/smallsort.rs:990|len8 implies len/2-1=3|Exact source slice has length8, half4; half-1=3 is defined.|
|m8_s32_d00_partial_diag|slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.3|library/core/src/slice/sort/shared/smallsort.rs:991|len8 implies len-1=7|Exact source slice has length8, so right_rev len-1=7 is defined.|
|m8_s32_d00_partial_diag|slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.4|library/core/src/slice/sort/shared/smallsort.rs:992|len8 implies len-1=7|Exact source slice has length8, so dst_rev len-1=7 is defined; writability and initialization remain separate.|
|m8_s32_d00_partial_diag|num::<impl usize>::abs_diff.assertion.1|library/core/src/num/uint_macros.rs:3222|self<other implies other-self defined|The self<other branch evaluates other-self with other>=self.|
|m8_s32_d00_partial_diag|ub_checks::is_valid_allocation_size.assertion.1|library/core/src/ub_checks.rs:148|else(size==0) implies size!=0|The size==0 arm skips division; the else arm divides only by size!=0. Concrete u8 size=1 independently.|
|m8_s40_d16_partial_diag|num::<impl usize>::abs_diff.assertion.1|library/core/src/num/uint_macros.rs:3222|self<other implies other-self defined|The self<other branch evaluates other-self with other>=self.|
|m8_s40_d16_partial_diag|ptr::const_ptr::<impl *const ()>::is_aligned_to.assertion.1|library/core/src/ptr/const_ptr.rs:1479|is_power_of_two(align) implies align>=1|Normal continuation follows is_power_of_two(align); zero is not a power of two, hence align>=1 and align-1 is defined.|
|m8_s40_d16_partial_diag|slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.1|library/core/src/slice/sort/shared/smallsort.rs:974|2 != 0|Divisor is literal2, hence nonzero for every length.|
|m8_s40_d16_partial_diag|slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.2|library/core/src/slice/sort/shared/smallsort.rs:990|len8 implies len/2-1=3|Exact source slice has length8, half4; half-1=3 is defined.|
|m8_s40_d16_partial_diag|slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.3|library/core/src/slice/sort/shared/smallsort.rs:991|len8 implies len-1=7|Exact source slice has length8, so right_rev len-1=7 is defined.|
|m8_s40_d16_partial_diag|slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.4|library/core/src/slice/sort/shared/smallsort.rs:992|len8 implies len-1=7|Exact source slice has length8, so dst_rev len-1=7 is defined; writability and initialization remain separate.|
|m8_s40_d16_partial_diag|ub_checks::is_valid_allocation_size.assertion.1|library/core/src/ub_checks.rs:148|else(size==0) implies size!=0|The size==0 arm skips division; the else arm divides only by size!=0. Concrete u8 size=1 independently.|
|m8_s40_d16_partial_diag|fmt::Arguments::<'_>::from_str.assertion.1|library/core/src/fmt/mod.rs:820|1 < usize::BITS64|The literal shift count1 is below x86_64 usize width64, independently of string length. No lost-bit claim.|

The insertion property/U/guard status sets are unobserved because there is no completed inventory; no native count is predicted from58 source literal sites/26 assertions/32 covers. All11 deferred roots in INVENTORY.json are NOT_SELECTED with no promotion. Prospective coverage remains at most32/256 original insertion pairs and1/1122 original allinit merge pairs if later admitted; the current censored insertions close none. Partial diagnostics close0 qualified mask/provider contexts; all34 sort8 initialization/caller contexts, generic providers, fullN16/N32 remain OPEN.
