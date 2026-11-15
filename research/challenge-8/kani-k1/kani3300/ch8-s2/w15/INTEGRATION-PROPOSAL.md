# Только worker13: registration и перенос loop attrs

S2 source.patch добавляет только четыре новых sorting_merge*.rs. Применить после
S1 model/feature integration; dependency — sorting_model v1 без изменения API.
Ни smallsort.rs, ни verify.rs не менялись worker15. Предложение registration:

```rust
#[cfg(kani_smallsort_sorting)]
mod sorting_merge_model;
#[cfg(kani_smallsort_sorting)]
mod sorting_merge_probe;
#[cfg(kani_smallsort_sorting)]
mod sorting_merge_invariant;
#[cfg(all(kani_smallsort_sorting, kani_smallsort_controls))]
mod sorting_merge_controls;
```

Actual std len32 root — sorting_merge_probe::s2_merge_u8_len32_real_body, обычный
proof, Original mode; НЕТ proof_for_contract или stub_verified. Existing safety
requires остаются; P1 real KeyLess activation/ABI уже должен быть qualified.
Нельзя применять старый verify/merge::profiles comparator (u8>>1) к этому claim.

Loop attrs в sorting_merge_invariant::s2_merge_loop_pilot_cap32 уже реализованы,
но actual core for-loop пока не получает semantic attrs. Для его S3 переноса
ниже точный контракт адаптации (proposal, не применяемый patch и не существующий
unchecked summary):

```rust
// At actual for _ in 0..len_div_2, preserve both existing runtime statements:
#[kani::loop_invariant(
    !core_merge_enabled::<T,F>() || core_merge_head::<T,F>(
        v, on_entry(dst), kani::index,
        left, right, left_rev, right_rev, dst, dst_rev)
)]
#[kani::loop_modifies(&left, &right, &left_rev, &right_rev, &dst, &dst_rev,
    ptr::slice_from_raw_parts_mut(on_entry(dst), len))]
for _ in 0..len_div_2 {
    (left, right, dst) = merge_up(left, right, dst, is_less);
    (left_rev, right_rev, dst_rev) = merge_down(left_rev, right_rev, dst_rev, is_less);
}
```

`core_merge_enabled/head` здесь — SPECIFICATION будущего raw adapter, НЕ код для
вставки без реализации. В S2 реализован pure initialized-array pilot. Worker13
и15 в S3 сначала отдельно реализуют/квалифицируют adapter, затем13 ставит attrs:

- Только exact u8/KeyLess; inactive/read-free true guard для остальных T/F;
  CAP overflow/invalid active geometry не должен молча выключать claim.
- Immutable input сохраняется, len и entry destination base фиксированы. Four
  counters извлекаются через checked pointer geometry, а не безусловный offset_from
  от reverse sentinel. Обязательно i+j=index=ir+jr и bindings всех output pointers.
- Читает только src[..len] и initialized dst bands [0..k),[len-k..len), никогда
  middle scratch. Перенос в массив32 zero-fills только нечитанную модельную часть,
  не реальную память. Invariant = sorting_merge_model::invariant с тем же fixed q.
- Query следует захватить неизменным ghost state через проверенный adapter API;
  нельзя новый nondet q при каждом вызове/внутри predicate и нельзя const0 вместо
  arbitrary q. Actual comparator/runtime не должен зависеть от q.
- on_entry(dst), kani::index и explicit modifies в actual for-loop требуют matched
  extraction controls (for-index writes, initial base capture, missing-frame false).
  Нельзя использовать pure pilot PASS как их замену. Не добавлять decreases expression.
- Epilogue сохраняется буквально; до применимости summary доказать actual panic
  guard false, odd, memory/init/frame obligations и все required source geometries.

Это оставляет runtime CFG/signatures/algorithm без изменений. No core-loop
integration или PFC qualification в этой сессии; S2 READY — готовность probe/pilot
и reviewable transfer proposal. CI этого пакета выполняет только module pilot,
без фиктивного core adapter и без новых core-loop attrs.
