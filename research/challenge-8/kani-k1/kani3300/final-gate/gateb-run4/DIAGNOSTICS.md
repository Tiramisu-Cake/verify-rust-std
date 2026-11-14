# Gate B run 43533328479 — дословные описания упавших свойств (ON-строки)

Из stdout.log артефактов kani3300-replay-<row> (координатор, 2026-11-14). Только блоки Status: FAILURE.

## raw-legal-on

```
Check 227: hint::select_unpredictable::<*const u64>.unsupported_construct.1
 - Status: FAILURE
 - Description: "Kani does not support reasoning about memory initialization of intrinsic `Unimplemented { name: "select_unpredictable", issue_link: "https://github.com/model-checking/kani/issues/new/choose" }`."
 - Location: library/core/src/hint.rs:871:21 in function hint::select_unpredictable::<*const u64>

```

## raw-negative-on

```
Check 124: slice::sort::shared::smallsort::sort4_stable::<u64, for<'a, 'b> fn(&'a u64, &'b u64) -> bool {slice::sort::shared::smallsort::verify::replay_uninit_controls::read_less_u64}>.safety_check.1
 - Status: FAILURE
 - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `*const u64`"
 - Location: library/core/src/slice/sort/shared/smallsort.rs:751:26 in function slice::sort::shared::smallsort::sort4_stable::<u64, for<'a, 'b> fn(&'a u64, &'b u64) -> bool {slice::sort::shared::smallsort::verify::replay_uninit_controls::read_less_u64}>

--
Check 177: hint::select_unpredictable::<*const u64>.unsupported_construct.1
 - Status: FAILURE
 - Description: "Kani does not support reasoning about memory initialization of intrinsic `Unimplemented { name: "select_unpredictable", issue_link: "https://github.com/model-checking/kani/issues/new/choose" }`."
 - Location: library/core/src/hint.rs:871:21 in function hint::select_unpredictable::<*const u64>

```

## sort8-boundary-on

```
Check 134: hint::select_unpredictable::<*const u64>.unsupported_construct.1
 - Status: FAILURE
 - Description: "Kani does not support reasoning about memory initialization of intrinsic `Unimplemented { name: "select_unpredictable", issue_link: "https://github.com/model-checking/kani/issues/new/choose" }`."
 - Location: library/core/src/hint.rs:871:21 in function hint::select_unpredictable::<*const u64>

```

## sort4-pfc-on

```
Check 95: <for<'a, 'b> fn(&'a u64, &'b u64) -> bool {slice::sort::shared::smallsort::verify::helper_contracts::arbitrary_less::<u64>} as ops::function::FnMut<(&u64, &u64)>>::call_mut.unsupported_construct.1
 - Status: FAILURE
 - Description: "Kani currently doesn't support checking memory initialization for pointers to `for<'a, 'b> fn(&'a u64, &'b u64) -> bool {slice::sort::shared::smallsort::verify::helper_contracts::arbitrary_less::<u64>}. Cannot determine layout for an unsupported type for<'a, 'b> fn(&'a u64, &'b u64) -> bool {slice::sort::shared::smallsort::verify::helper_contracts::arbitrary_less::<u64>}."
 - Location: library/core/src/ops/function.rs:166:5 in function <for<'a, 'b> fn(&'a u64, &'b u64) -> bool {slice::sort::shared::smallsort::verify::helper_contracts::arbitrary_less::<u64>} as ops::function::FnMut<(&u64, &u64)>>::call_mut

```

## merge-raw-pfc-on

```
Check 90: <for<'a, 'b> fn(&'a u64, &'b u64) -> bool {slice::sort::shared::smallsort::verify::helper_contracts_wide::tail_less_u64} as ops::function::FnMut<(&u64, &u64)>>::call_mut.unsupported_construct.1
 - Status: FAILURE
 - Description: "Kani currently doesn't support checking memory initialization for pointers to `for<'a, 'b> fn(&'a u64, &'b u64) -> bool {slice::sort::shared::smallsort::verify::helper_contracts_wide::tail_less_u64}. Cannot determine layout for an unsupported type for<'a, 'b> fn(&'a u64, &'b u64) -> bool {slice::sort::shared::smallsort::verify::helper_contracts_wide::tail_less_u64}."
 - Location: library/core/src/ops/function.rs:166:5 in function <for<'a, 'b> fn(&'a u64, &'b u64) -> bool {slice::sort::shared::smallsort::verify::helper_contracts_wide::tail_less_u64} as ops::function::FnMut<(&u64, &u64)>>::call_mut

```

## merge-profile-pfc-on

```
Check 452: <for<'a, 'b> fn(&'a u8, &'b u8) -> bool as ops::function::FnMut<(&u8, &u8)>>::call_mut.unsupported_construct.1
 - Status: FAILURE
 - Description: "Kani does not support memory initialization checks across calls through function pointers. For more information about planned support, see https://github.com/model-checking/kani/issues/3300."
 - Location: library/core/src/ops/function.rs:166:5 in function <for<'a, 'b> fn(&'a u8, &'b u8) -> bool as ops::function::FnMut<(&u8, &u8)>>::call_mut

```
