# Unreachable roles — v3

Политика: required postcondition/frame/relation/section для target/wrapper блокирует
admission; неизвестная роль остаётся UNKNOWN. Defensive guards допускаются только
по явной таблице ниже. Function и file — fullmatch regex; line — точный source site;
ID класса assertion нужен дополнительно. Все правила и буквальные description
patterns находятся в ROLE-RULES.json, pinned source SHA — ACCEPT.json/source_sites.
Строки таблицы относятся к конкретным bounded instances, не дают broad helper exemption.

`model_sorted` / `model_count` входят в relation/post computation, но перечисленные
properties — generated arithmetic error guards, а не сам обязательный результат:
i-1 использует literals 1..31; c имеет максимум 32 increments. Model/post assertions
с другим description/ID не получают exemption. Отсутствие вычисления для i>=len
не означает пропуска required postcondition; её gates и post-target covers сохранены.

`ptr_offset_from::<()>` разобран отдельно от non-ZST instances: входной size assertion
ложен для unit, поэтому такой вызов запрещён API и не требуется сценарием. Недостижимы
entry guard и последующее zero-size arithmetic (10 occurrences, две строки sort4 b16).
Это не предположение о nonzero size unit и не новое доверенное правило memory model.
Сам same-allocation/divisibility/provenance результат по имени helper не освобождён.

Для UNREACHABLE статус проверяется до role lookup; каждый exact occurrence имеет
собственную запись с coordinates и хешем полного stdout в ACCEPT.json.

| Семейство | Function pattern | File:line | Роль | Occurrences | Причина |
|---|---|---|---|---:|---|
| required-postcondition | `.*smallsort.*` | `library/core/src/slice/sort/shared/smallsort(?:/.*|.rs):*` | postcondition | 0 | Explicit mandatory target/wrapper obligation; it must execute in the declared scenario. |
| required-frame | `.*smallsort.*` | `library/core/src/slice/sort/shared/smallsort(?:/.*|.rs):*` | frame | 0 | Explicit mandatory target/wrapper obligation; it must execute in the declared scenario. |
| required-relation | `.*smallsort.*` | `library/core/src/slice/sort/shared/smallsort(?:/.*|.rs):*` | relation | 0 | Explicit mandatory target/wrapper obligation; it must execute in the declared scenario. |
| required-required_section | `.*smallsort.*` | `library/core/src/slice/sort/shared/smallsort(?:/.*|.rs):*` | required_section | 0 | Explicit mandatory target/wrapper obligation; it must execute in the declared scenario. |
| fmt-static-shift | `fmt::Arguments::<'_>::from_str` | `library/core/src/fmt/mod.rs:820` | defensive_branch | 53 | Formatting error guard, not a sorting/frame/relation obligation. Static panic messages use shift count 1; no invalid shift is in the declared bounded scenario. |
| alignment-sub | `ptr::const_ptr::<impl \*const \(\)>::is_aligned_to` | `library/core/src/ptr/const_ptr.rs:1479` | defensive_branch | 53 | align - 1 follows the power-of-two check, which excludes zero; unreachable subtraction-error branch is defensive. |
| usize-abs-diff | `num::<impl usize>::abs_diff` | `library/core/src/num/uint_macros.rs:3222,3224` | defensive_branch | 100 | Both subtractions are selected by operand ordering; the underflow error branch is impossible. |
| usize-multiple | `num::<impl usize>::is_multiple_of` | `library/core/src/num/uint_macros.rs:3916` | defensive_branch | 3 | The rhs == 0 match arm returns before remainder; zero-divisor error branch is defensive. |
| allocation-size | `ub_checks::is_valid_allocation_size` | `library/core/src/ub_checks.rs:148` | defensive_branch | 6 | size == 0 selects usize::MAX; division is in the nonzero arm. The actual validity result/check is not exempted. |
| model-sorted-index | `slice::sort::shared::smallsort::verify::merge::profiles::model_sorted::<.+>` | `library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs:134` | defensive_branch | 669 | Macro index i is a literal in 1..31, so i - 1 cannot underflow. This is an arithmetic error guard, not the model_sorted result or required relation assertion. |
| model-count-add | `slice::sort::shared::smallsort::verify::merge::profiles::model_count::<.+>` | `library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs:153` | defensive_branch | 582 | c starts at zero and has at most 32 single increments; overflow is outside the bounded model. The required model-count equality is not exempted. |
| region-distance-negate | `slice::sort::shared::smallsort::verify::merge::regions_are_disjoint::<(?:u8&#124;u64&#124;\[u8; 16\])>` | `library/core/src/slice/sort/shared/smallsort/verify/merge.rs:111` | defensive_branch | 17 | Negation guard in optional same-allocation geometry arm; offsets in these bounded initialized buffers cannot be isize::MIN. The geometry result is not an unreachable mandatory post/frame assertion. |
| dispatch-stack-size | `<(?:u8&#124;slice::sort::shared::smallsort::verify::forwarding_contracts::NonCopyU8) as slice::sort::shared::smallsort::UnstableSmallSortFreezeTypeImpl>::small_sort::<.+>` | `library/core/src/slice/sort/shared/smallsort.rs:130,164,167` | defensive_branch | 6 | Only fixed one-byte u8/NonCopyU8 instances; element size times the fixed scratch length fits usize. This generated arithmetic guard is not a required dispatch/return section. |
| general-add | `slice::sort::shared::smallsort::small_sort_general_with_scratch::<.+>` | `library/core/src/slice/sort/shared/smallsort.rs:232,249` | defensive_branch | 12 | Bounded forwarding buffers have len <= 16 and fixed scratch; len + 16 / len + 8 cannot overflow. No body/cover obligation is waived. |
| general-div | `slice::sort::shared::smallsort::small_sort_general_with_scratch::<.+>` | `library/core/src/slice/sort/shared/smallsort.rs:237` | defensive_branch | 5 | Divisor is literal 2; zero-divisor error branch is impossible. |
| general-sub | `slice::sort::shared::smallsort::small_sort_general_with_scratch::<.+>` | `library/core/src/slice/sort/shared/smallsort.rs:272` | defensive_branch | 5 | len_div_2 = len / 2 <= len, so len - len_div_2 cannot underflow. |
| network-div | `slice::sort::shared::smallsort::small_sort_network::<.+>` | `library/core/src/slice/sort/shared/smallsort.rs:331` | defensive_branch | 1 | Divisor is literal 2; zero-divisor error branch is impossible. |
| network-sub | `slice::sort::shared::smallsort::small_sort_network::<.+>` | `library/core/src/slice/sort/shared/smallsort.rs:362` | defensive_branch | 4 | len_div_2 = len / 2 <= len; right-region length subtraction cannot underflow. Required network execution covers remain separate. |
| sort4-bool-index | `slice::sort::shared::smallsort::sort4_stable::<.+>` | `library/core/src/slice/sort/shared/smallsort.rs:715,716` | defensive_branch | 22 | 2 + bool-as-usize is in {2,3}; index-add overflow guard is impossible, not a sorting postcondition. |
| merge-div | `slice::sort::shared::smallsort::bidirectional_merge::<.+>` | `library/core/src/slice/sort/shared/smallsort.rs:898` | defensive_branch | 18 | Divisor is literal 2; zero-divisor error branch is impossible. |
| merge-sub | `slice::sort::shared::smallsort::bidirectional_merge::<.+>` | `library/core/src/slice/sort/shared/smallsort.rs:914,915,916` | defensive_branch | 54 | Declared merge lengths are >= 2; len_div_2 and len are >= 1. Subtraction error guards lie outside the declared merge domain, not the required merge postcondition. |
| offset-nonzst | `kani::rustc_intrinsics::ptr_offset_from::<(?:u8&#124;u64&#124;\[u8; 16\]&#124;cell::Cell<u8>)>` | `library/core/src/lib.rs:357` | defensive_branch | 18 | Optional offset helper guard, not a mandatory target/wrapper section. These four concrete element types are non-ZST; the ZST rejection case is outside the scenario. Other offset/provenance/same-allocation checks receive no exemption. |
| offset-remainder | `kani::rustc_intrinsics::ptr_offset_from::<(?:u8&#124;u64&#124;\[u8; 16\]&#124;cell::Cell<u8>)>` | `library/kani_core/src/models.rs:93` | defensive_branch | 36 | Concrete type sizes are 1, 8 or 16, hence positive and never -1 as isize. Remainder error guards are impossible; actual same-allocation/divisibility assertions are not exempted. |
| offset-division | `kani::rustc_intrinsics::ptr_offset_from::<(?:u8&#124;u64&#124;\[u8; 16\]&#124;cell::Cell<u8>)>` | `library/kani_core/src/models.rs:97` | defensive_branch | 36 | Concrete type sizes are positive 1, 8 or 16, never zero or -1; division error branches are outside these concrete instances. No provenance premise is added. |
| offset-zst-forbidden-call-entry | `kani::rustc_intrinsics::ptr_offset_from::<\(\)>` | `library/core/src/lib.rs:357` | defensive_branch | 2 | Unit is a ZST: the model entry assertion is always false. Executing offset_from::<()> is forbidden by this API, never a required sorting/wrapper section. Its unreachable entry guard and subsequent zero-size arithmetic are the excluded invalid-operation path; no mandatory post/frame/relation property is exempted. |
| offset-zst-forbidden-call-remainder | `kani::rustc_intrinsics::ptr_offset_from::<\(\)>` | `library/kani_core/src/models.rs:93` | defensive_branch | 4 | Unit is a ZST: the model entry assertion is always false. Executing offset_from::<()> is forbidden by this API, never a required sorting/wrapper section. Its unreachable entry guard and subsequent zero-size arithmetic are the excluded invalid-operation path; no mandatory post/frame/relation property is exempted. |
| offset-zst-forbidden-call-division | `kani::rustc_intrinsics::ptr_offset_from::<\(\)>` | `library/kani_core/src/models.rs:97` | defensive_branch | 4 | Unit is a ZST: the model entry assertion is always false. Executing offset_from::<()> is forbidden by this API, never a required sorting/wrapper section. Its unreachable entry guard and subsequent zero-size arithmetic are the excluded invalid-operation path; no mandatory post/frame/relation property is exempted. |
