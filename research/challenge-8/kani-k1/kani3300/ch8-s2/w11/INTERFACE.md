# W11 → W13: S2 swap/sort13 и API S3, proposal v1

Предложение для последующей интеграции, не принятие P1/P2. S1 API не изменён.
Три новых модуля: sorting_leaf_swap.rs, sorting_leaf_probe.rs,
sorting_leaf_controls.rs. Область видимости facade — smallsort; fields приватны.

## Что уже реализовано

```rust
sorting_leaf_swap::enabled::<T,F>() -> bool
sorting_leaf_swap::capture::<T,F>(base: *const T, a: usize, b: usize) -> PairSnapshot
sorting_leaf_swap::post::<T,F>(pre: PairSnapshot, base: *const T, a: usize, b: usize) -> bool
```

Unconditional facade без новых T/F bounds, приватная min_specialization по точной
паре (u8, KeyLess<u8>). Только она active; Cell/NonCopyByte ещё НЕ swap-qualified.
PairSnapshot: Copy, собственные a,b:u8 + valid. capture активной пары читает ровно
две initialized позиции после original requires. Inactive не читает даже указатели;
invalid active token → false. post задаёт точный if old_b<old_a then (b,a) else (a,b).
Отсюда порядок пары и полные кратности; для a=b сохраняется единственное значение.
Это не frame: frame берётся из actual modifies(a,b). Comparator — закрытый ZST
KeyLess; произвольный effectful F не получает semantic claim и нарушает element-only
frame, если пишет вовне. Tokens не аутентифицируют provenance: old/call pairing —
обязанность контракта, не возможность передать произвольный снимок.

## Только proposal для13: actual attrs и registration

После всех существующих safety requires/modifies на actual swap_if_less добавить:

```rust
#[cfg_attr(all(kani, kani_smallsort_sorting), crate::kani::ensures(|_| {
    !verify::sorting_leaf_swap::enabled::<T, F>()
        || verify::sorting_leaf_swap::post::<T, F>(
            old(verify::sorting_leaf_swap::capture::<T, F>(v_base, a_pos, b_pos)),
            v_base, a_pos, b_pos)
}))]
```

Существующие requires/modifies и runtime тело/signature сохранить. Не вызывать F
из ensures, не использовать старый FnPtr profile. Requires должны проверяться ДО
spec reads; это отдельно квалифицирует wrong-precondition control. Capture —
пара значений, не old(pointer). Никакого нового assumed summary.

В verify.rs под kani_smallsort_sorting зарегистрировать:

```rust
pub(super) mod sorting_leaf_swap;
mod sorting_leaf_probe;
#[cfg(kani_smallsort_controls)]
mod sorting_leaf_controls;
```

Нужны S1 model/feature gates13. Пока attrs/registration не интегрированы,
consumer НЕ квалифицирован: старый swap summary содержит лишь safety/frame.
Сначала exact combined-head s2_swap_u8_backing13 PFC + controls, затем consumer
s2_sort13_u8_verified_swap на ТОМ ЖЕ source/tool/flags. Root использует настоящий
sort13_optimal, 45 actual calls, stub_verified(actual swap_if_less); не wrapper/network replica.
Нельзя принять consumer PASS при failed/NOT_RUN leaf. Неактивный model должен
сломать root assertion. Stub body не обязан вызывать comparator: covers стоят после return.

## API S3: фиксируем семантику, не выдаём реализацию за qualified

Общие proposed adapters в будущем новом sorting_leaf_model.rs (сейчас НЕ реализованы):

```rust
capture_span::<T,F>(src: *const T, len: usize) -> sorting_model::Snapshot
sorted_span::<T,F>(pre: Snapshot, dst: *const T, len: usize) -> bool
ordered_span::<T,F>(src: *const T, len: usize) -> bool
```

Геометрия/initialization должны быть установлены ДО любого active read. CAP32;
len>CAP или invalid → false для active post, invalid для capture; inactive read-free.
Обёртки используют S1 projection/order, не меняют его API и не вводят T:Copy/Ord.
Generic enables для span — ровно S1 pairs; каждый конкретный leaf сохраняет свою
таблицу qualified T/F. Этот proposal сам по себе не включает Cell/nonCopy в leaves.
Пустые spans не читаются; raw→typed slice допустим лишь после validity/init, при len0
не строить slice из null. requires sort4/sort8 НЕ читают destination или unused scratch.

| Actual helper | Proposed semantic attrs (в дополнение к safety/frame) | Writable frame |
|---|---|---|
| swap_if_less | exact pair transfer через PairSnapshot; active guard | только a,b |
| sort4_stable | sorted_span(old(capture_span(src,4)), dst,4) | dst[0..4] |
| sort8_stable | sorted_span(old(capture_span(src,8)), dst,8) | dst[0..8], scratch[0..8] |
| sort9_optimal | sorted_span(old(capture_span(v.ptr,9)), v.ptr,9); len>=9 | только v[..9] |
| sort13_optimal | аналогично prefix13; len>=13 | только v[..13] |
| insert_tail | requires ordered_span(begin,p), 1<=p<=16; sorted_span(old(capture_span(begin,p+1)),begin,p+1) | [begin,tail] включительно |

Actual network helper принимает длинный slice, но сортирует ТОЛЬКО prefix9/13.
Нельзя писать post на полном v, если len>width. Остаток slice/backing сохраняет frame.
Позиция tail=p — относительная begin, значит максимальная active длина17, НЕ16.
Requires insert_tail не предполагает sorted tail и читает только initialized prefix p.
Safe-total geometry helper вычисляет p только после same-allocation/nonzero-size/
nonwrapping checks; никаких безусловных offset_from/underflow в spec.
S3 attrs к actual functions ставит13. sort8 нуждается в semantic sort4 и merge8;
sort9/13 — semantic swap; insert_tail finite bounded body без assumed invariant.
Каждый leaf post проверяет ПОЛНЫЕ values, не единственный fixed probe и не только key.
