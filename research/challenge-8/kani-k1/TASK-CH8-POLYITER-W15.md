# TASK — worker15: разбор `PolymorphicIter<[MaybeUninit<T>; N]>` unsupported (статическая стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Факты A1-R3 ([RESULT](kani3300/w0-a1/r3/run-43779285270/RESULT.md)): на SEL1 `14bc57fdb9` с `-Z uninit-checks`
N32 stable_freeze (895 props) и general_nocopy (907) падают ровно на одном свойстве:
`array::iter::iter_inner::PolymorphicIter::<[MaybeUninit<usize>; 2]>::new_unchecked.unsupported_construct.1` —
"Checking memory initialization of type PolymorphicIter<[MaybeUninit<usize>; 2]> is not supported. Cannot determine
layout for a type that contains union of type MaybeUninit<usize> as a field" (iter_inner.rs:96; источник —
`[usize; 2].into_iter()` в smallsort.rs:307). При этом #5151 (`[MaybeUninit<D>; 2]` напрямую) SEL1 уже поддерживает.
Network N32 с ON — RSS watchdog 13.57 GB.

Только чтение/проектирование, без compiler patch и без CI (WIP-правило: новый compiler design — решение владельца).

1. По коду C2/SEL1: какая ветка layout/uninit-анализа даёт этот отказ для struct, содержащего массив union,
   и почему путь #5151 его не покрывает (file:line на `14bc57fdb9`). Какой срез стека C2 отвечает за #5151.
2. Минимальное направление исправления (в рамках существующего механизма C2 — расширение того же случая
   на вложение в struct/ManuallyDrop) и его риск; отдельное upstream issue или часть стека.
3. MRE single-file fixture (negative + initialized companion), не std; ожидаемые исходы на 0aac и SEL1.
4. Можно ли обойти в A1-кампании без изменения runtime std (например другой корень без into_iter) — только
   как диагностика, не как proof claim.
5. Network N32 ON: оценка, что делает её >13 GB (по export/receipt сравнению с general N32, если данных хватает);
   иначе — какие bounded измерения нужны.
g0 `kani3300/w0-a1/polyiter/`: ANALYSIS.md, MRE/, HANDOFF.md. Последней строкой `READY <g0>` или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
