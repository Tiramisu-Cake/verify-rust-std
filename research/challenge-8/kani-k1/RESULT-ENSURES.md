# ENSURES — итог G1/G2
G1 build `6d95823e-445b-446c-b016-914589a03b6e`, source `2d68c777cfb3221fd07bb70d1cc31e46273fe72e`: COMPLETE, Cloud SUCCESS, gate/expectations true; Kani exit1 для ожидаемого negative.
G2 build `e8526f1c-c5f7-48c8-a314-fb50bed6b517`, source `9286a7713f4a8331184004ccc435055968e1ff16`: COMPLETE, Cloud SUCCESS, gate/expectations true; Kani exit0, все восемь SUCCESS.
G2 request `ensures-g2-20261105`, SHA-256 `a78d65680499ede6d7e510b29e2854c9cba316e6676c6da494bcadd104133a2f`; страница 0/8, next_offset=done, совпали request/build/source. Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, owner k1-network по обоим GO.
Механизм: cfg(kani) trait InsertTailComparatorModel<T>, blanket default «модели нет», специализация (u64, InsertTailU64Less), ручной FnOnce/FnMut со строгим полным u64 <. Неизменный произвольный полный u64 probe из kani::any() хранится в F; для прочих F ensures тривиальны. Специализация осуществима.
Точные ensures настоящего insert_tail, одинаковые в G1/G2 (свёрнуты только пробелы/переносы):
```rust
#[cfg_attr(kani, crate::kani::ensures(|_| !old(<F as InsertTailComparatorModel<T>>::has_model(is_less)) || !old(unsafe { <F as InsertTailComparatorModel<T>>::model_sorted( is_less, begin, insert_tail_contract_len(begin, tail).saturating_sub(1), ) }) || unsafe { <F as InsertTailComparatorModel<T>>::model_sorted( is_less, begin, insert_tail_contract_len(begin, tail), ) } ))]
#[cfg_attr(kani, crate::kani::ensures(|_| !old(<F as InsertTailComparatorModel<T>>::has_model(is_less)) || old(unsafe { <F as InsertTailComparatorModel<T>>::model_count( is_less, begin, insert_tail_contract_len(begin, tail), ) }) == unsafe { <F as InsertTailComparatorModel<T>>::model_count( is_less, begin, insert_tail_contract_len(begin, tail), ) } ))]
```

| Этап | Корень realcontracts:: | Статус | Время, с | Failed/total | Covers |
| --- | --- | --- | --- | --- | --- |
| G1 | insert_tail_ensures_u64_tail1_to4_backing5 | SUCCESS | 229.96153 | 0/533 | 10/10 |
| G1 | insertion_ensures_u64_n5_stubbed | SUCCESS | 247.8377 | 0/496 | 4/4 |
| G1 | rejects_insertion_ensures_u64_n5_corruption | FAILED, ожидаемый | 137.15259 | 1/496 | 1/4 |
| G1 | insert_tail_safety_u64_tail1_to4_backing5 | SUCCESS | 29.752695 | 0/349 | 7/7 |
| G2 | insert_tail_ensures_u64_tail1_backing8 | SUCCESS | 69.21353 | 0/531 | 5/6 |
| G2 | insert_tail_ensures_u64_tail2_backing8 | SUCCESS | 80.58219 | 0/531 | 6/6 |
| G2 | insert_tail_ensures_u64_tail3_backing8 | SUCCESS | 92.28954 | 0/531 | 6/6 |
| G2 | insert_tail_ensures_u64_tail4_backing8 | SUCCESS | 92.91752 | 0/531 | 6/6 |
| G2 | insert_tail_ensures_u64_tail5_backing8 | SUCCESS | 113.276955 | 0/531 | 6/6 |
| G2 | insert_tail_ensures_u64_tail6_backing8 | SUCCESS | 130.98123 | 0/531 | 6/6 |
| G2 | insert_tail_ensures_u64_tail7_backing8 | SUCCESS | 117.54943 | 0/531 | 6/6 |
| G2 | insertion_ensures_u64_n8_stubbed | SUCCESS | 548.07477 | 0/492 | 4/4 |

**Объединение доменов PFC ⊇ домен consumer:** D_i = произвольный u64 backing8, F=InsertTailU64Less с произвольным probe, begin=base, tail=base+i; семь PFC покрывают ∪(i=1..7)D_i. Все семь вызовов реального insertion_sort_shift_left(N8, offset1) лежат в этом объединении. G1 отдельно совпадает по backing5/tails1..4.
**N5 и N8: ДА — sortedness и full-value probe count всего среза проверены через ensures.** Реальный insertion-loop исполняется; #[kani::stub_verified(insert_tail)] заменяет только helper на requires/modifies/ensures без раскрытия его тела по семантике Kani. Суффикс/probe сохраняет frame; PFC исполняют настоящее тело без sorted-prefix assume. Отдельного IR/callgraph-аудита нет.
G2 covers: consumer 4/4, PFC tails2..7 6/6. Tail1: 5/6, 1 unreachable; по исходнику лишний cover находится под константно ложным if TAIL>1 (unsorted singleton). Terse bounded-вывод не даёт individual cover ID. Unreachable checks tails1..6=4, tail7=6, consumer=4 не добавляют proof credit. G1 negative упал только на named sortedness.
Времена vs N5: consumer 247.8377 → 548.07477 с = 2.2114× (N8 9:08, до 10мин осталось 51.93 с). G2 fixed-tail PFC 69.21–130.98 с, сумма 696.810395 с; G1 symbolic-tail PFC 229.96153 с. Разбиение и домен различны, поэтому сумма/229.96=3.0301× не является изолированным эффектом N.
Прогноз N16, только эвристика: линейно по N от N8 ≈18.27мин; степенная подгонка двух consumer-точек (p≈1.689) ≈29.44мин. Это не гарантированный диапазон: SAT нелинеен; при N8 CBMC peak уже 8.94 GiB против N5 3.58 (2.50×), риск превышения 10мин/16GB реален.
До N16/32 доказательства нет: нужны PFC backing16/tails1..15, проверенные unwind bounds и новый GO; при лимите8 строк весь набор из15 PFC+consumer требует ≥2 пакетов. Count — bounded full-value-probe evidence, не универсальное multiset-ограничение каждого отдельного havoc outcome.
Оба check-tooling PASS: pool standard4, source/run binding, protected lane paths и шесть SHA-256 против `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`. Diagnostic/controls=true/jobs1/10мин; runtime-тела, сигнатуры, модель, ensures и tooling в G2 не менялись.
G2 wall включая компиляцию 24:23.93, max RSS 9374368 KiB, sampled sum RSS 8.93 GiB; OOM none_seen не доказывает запас. Расход G1 $0.2565 + G2 $0.4185 = $0.6750 <= cap $4.00 (`2 0.6750 0.0000`); dispatch maximum $101.3955 < $118.96. Две primary build, без repair/дополнительных запусков.
Generic/stateful callbacks, Drop/ZST, panic unwinding, uninit/value-validity и пороги16/32 остаются вне доказанного. После G2 только отчёты; raw logs/credentials/конкурирующий код и локальные cargo/rustc/Kani/CBMC не использовались. Пакеты/история: [G1](PREBUILD-ENSURES.md), [G2](PREBUILD-ENSURES-G2.md).
