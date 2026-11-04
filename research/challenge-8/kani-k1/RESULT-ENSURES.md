# ENSURES — итог G1
Build `6d95823e-445b-446c-b016-914589a03b6e`, source `2d68c777cfb3221fd07bb70d1cc31e46273fe72e`, owner `k1-network` (GO координатора подтвердил, что свободен).
Bounded summary COMPLETE; Cloud SUCCESS; gate/expectations true; Kani exit 1 соответствует ожидаемому negative FAILED. Страница строк 0/4, next_offset=done, совпали build/source/request identities.
Request `ensures-g1-20261105`, SHA-256 `44acf34a023016972263cff248e4465f72fed07d4d094b6c28ae5f4fd2db5139`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Модель осуществима: cfg(kani) trait InsertTailComparatorModel<T>, blanket default «модели нет», специализация пары (u64, InsertTailU64Less); ручной FnOnce/FnMut сравнивает полные u64 строгим <. min_specialization/unboxed_closures и cfg(kani) fn_traits скомпилировались.
Probe — произвольный полный u64 из kani::any(), неизменяемое поле компаратора на всю композицию; спецификации чистые, без нового nondeterminism и globals. Для прочих F оба ensures тривиальны.

Точные ensures на настоящем insert_tail (свёрнуты только пробелы/переносы):
```rust
#[cfg_attr(kani, crate::kani::ensures(|_| !old(<F as InsertTailComparatorModel<T>>::has_model(is_less)) || !old(unsafe { <F as InsertTailComparatorModel<T>>::model_sorted( is_less, begin, insert_tail_contract_len(begin, tail).saturating_sub(1), ) }) || unsafe { <F as InsertTailComparatorModel<T>>::model_sorted( is_less, begin, insert_tail_contract_len(begin, tail), ) } ))]
#[cfg_attr(kani, crate::kani::ensures(|_| !old(<F as InsertTailComparatorModel<T>>::has_model(is_less)) || old(unsafe { <F as InsertTailComparatorModel<T>>::model_count( is_less, begin, insert_tail_contract_len(begin, tail), ) }) == unsafe { <F as InsertTailComparatorModel<T>>::model_count( is_less, begin, insert_tail_contract_len(begin, tail), ) } ))]
```

| Корень realcontracts:: | Статус | Время, с | Failed/total | Covers |
| --- | --- | --- | --- | --- |
| insert_tail_ensures_u64_tail1_to4_backing5 | SUCCESS | 229.96153 | 0/533 | 10/10 |
| insertion_ensures_u64_n5_stubbed | SUCCESS | 247.8377 | 0/496 | 4/4 |
| rejects_insertion_ensures_u64_n5_corruption | FAILED, ожидаемый | 137.15259 | 1/496 | 1/4 |
| insert_tail_safety_u64_tail1_to4_backing5 | SUCCESS | 29.752695 | 0/349 | 7/7 |

**Consumer N5: ДА — проверены sortedness и full-value count всего среза v[0..5]**, от произвольного входа и probe. Реальный insertion_sort_shift_left(offset=1) исполнялся; его четыре вызова insert_tail заменены #[kani::stub_verified(insert_tail)].
Тело insert_tail в consumer не раскрывалось по stub_verified-семантике Kani: используются requires, havoc в modifies и ensures; порядок/count получены из ensures, сохранение суффикса/probe — из frame. Отдельный IR/callgraph-аудит не проводился; вывод основан на атрибуте, привязанном исходнике и стандартной семантике stub_verified.
**Домены совпали:** PFC — T=u64, F=InsertTailU64Less, backing [u64;5], tail любой из 1..4; consumer — та же пара T/F и backing5, реальные хвосты 1/2/3/4. Произвольный probe одинаков на всех вызовах; вне begin..=tail действует modifies-frame.
PFC проверял настоящее тело без sorted-prefix assume: order условен на pre-state sorted prefix, count безусловен для canonical F. Отсортированный singleton запускает индукцию consumer. Независимые от trait-модели harness-checkers проверяют весь результат.
Все positive covers достигнуты: PFC tails1..4, sorted/unsorted premise, движение/ранний возврат, present probe, return; consumer return/present probe/nonconstant result/assertions. Unreachable checks PFC/consumer/negative/safety: 4/6/8/4, отдельно от proof credit.
Negative после того же stubbed entry пишет MAX/0 в v[0]/v[1]; единственная ошибка — `ensures consumer n5 sortedness` в realcontracts.rs:406; посторонняя ошибка не засчитана. Его 1/4 covers не заменяют positive nonvacuity.
Это bounded full-value-probe evidence сохранения перестановки: count для произвольного полного значения, без усечения. Не утверждается универсально квантифицированное multiset-ограничение каждого отдельного havoc outcome.
Для порогов 16/32 показана осуществимость порядка/count через контракт настоящего insertion-helper на N5. N8/N16 и merge/порог32 не доказаны: backing5/tail1..4 их не покрывает; нужны расширенный PFC и отдельный G2 GO.
Неудавшихся positive строк и compile-error repair нет; ограничение — ещё не расширенный bounded domain, а не отказ специализации. Generic/stateful callbacks, Drop/ZST, panic unwinding, uninit/value-validity не доказаны; соответствующие extra checks выключены.
Check-tooling PASS: ожидаемый standard4 pool, source/run binding, все protected lane paths и шесть SHA-256 против `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; diagnostic/controls=true/jobs1/10min, flags сохранены.
Run wall (включая компиляцию) 12:09.49, max RSS 3755488 KiB; per-CBMC peak 3.58 GiB, sampled sum RSS 3.96 GiB. OOM none_seen не доказывает запас памяти.
Расход `k1g budget BUILD`: `1 0.2565 0.0000`, $0.2565 <= свой cap $3.50; dispatch maximum $98.8710 < project cap $118.96. Одна primary build, без repair/G2; watch отработал, status polling loop не применялся.
Runtime-тела/сигнатуры и tooling не менялись; после build меняются только отчёты. Никаких локальных cargo/rustc/Kani/CBMC, credentials, raw logs или конкурирующего кода. [Точный пакет](PREBUILD-ENSURES.md).
