# RESULT K1-network

Агент: K1-network (Claude Code, Opus 5.5). Ветка `experiment/kani-k1-network-20261024`. Норматив — [EXPERIMENT.md](EXPERIMENT.md), задание — [TASK-network.md](TASK-network.md).

## Фаза 1

- T0: 2026-10-24T14:58:09Z (`date -u`)
- T0+120 (последний dispatch): 2026-10-24T16:58:09Z
- T0+140 (конец отчёта): 2026-10-24T17:18:09Z
- Dispatch в фазе: 2 / 6 (job 5, job 6); сумма таймаутов: 20 + 36 = 56 / 120 мин.
- Счётчики STOP: формулировок контракта с провалом — 0; минут без продвижения — 0.

## 1. Вердикт

(в работе)

## 2. Таблица обязательств

Все job — `circleci-linux-large`; check-tooling — `bash <(git show 77479d23:…/k1.sh) check-tooling <job> 77479d23…`.

| Обязательство | Гармоника | request_id | job | head SHA | статус | время, с | пик. память (весь прогон) | cover | check-tooling |
|---|---|---|---|---|---|---|---|---|---|
| `swap_if_less` контракт, u8 (diagnostic) | `network::swap_if_less_u8` | net-p1-01-swap-old-r11 | 5 | 65805cfa | SUCCESS | 7.6 | 1.64 ГБ | 5/5 | ok |
| `swap_if_less` контракт, i32 (diagnostic) | `network::swap_if_less_i32` | net-p1-01-swap-old-r11 | 5 | 65805cfa | SUCCESS | 8.6 | 1.64 ГБ | 5/5 | ok |
| `swap_if_less` контракт, u64 (diagnostic) | `network::swap_if_less_u64` | net-p1-01-swap-old-r11 | 5 | 65805cfa | SUCCESS | 10.4 | 1.64 ГБ | 5/5 | ok |
| R11 контроль предусловий | `network::r11_control_swap_if_less_requires` | net-p1-01-swap-old-r11 | 5 | 65805cfa | FAILED (ожидаемо): `a_pos != b_pos @ smallsort.rs:387` | 0.15 | — | 0/1 | ok |

Job 5: COMPLETE, gate true, expectation met. Diagnostic-прогоны в зачёт PASS не идут; measurement ещё не было.

### R11 (для обоих агентов)

**Предусловия в точках `stub_verified` проверяются** при флагах CI организаторов (`--no-assert-contracts`): вызов `swap_if_less(p, 1, 1, …)` под `stub_verified(swap_if_less)` дал FAILED ровно на проверке `a_pos != b_pos` (job 5, SHA 65805cfa). Композиция через `stub_verified` засчитывается.

## 3. Редукции

(пока нет)

## 4. Журнал решений

1. **old() и `T: Clone`.** По исходнику Kani на pin 9461e07a (`library/kani_macros/src/sysroot/contracts/shared.rs`, `build_ensures`) `old(e)` раскрывается в `let remember = (e).clone();` — для обобщённого `T` без `Clone` это E0599. Отдельный прогон с `old(*p)` поэтому не тратился. Обход: `old({ struct Pre<U>(…); impl<U> Clone for Pre<U> { ptr::read(self) } … })` — побитовый снимок в локальном типе, определённом внутри выражения атрибута; `ManuallyDrop`/`MaybeUninit` исключают drop. Проверено job 5: компилируется и доказывается для u8/i32/u64. Альтернатива — вспомогательный тип в `smallsort.rs` — отвергнута: R2 разрешает там только атрибуты.
2. **Comparator в `ensures`.** `kani::internal::apply_closure` требует `Fn` для замыкания `ensures`, а `is_less: &mut F` — `FnMut`. Обход: `let cmp = old(&raw mut *is_less);` и вызов `(*cmp)(…)` в post-state. Проверено job 5 (второе `ensures` у `swap_if_less`). Для `swap_if_less` основное постусловие точное: решение comparator фиксируется в pre-state (`old(is_less(b, a))`), значения сравниваются побайтно.
3. **Равенство элементов в контрактах** — побайтное (`size_of::<T>()` байт), т.к. у обобщённого `T` нет `PartialEq`. Для u8/i32/u64 паддинга нет. В гармониках перестановка проверяется по `==` полного значения.
4. **Один `F` для доказательства и заглушки.** Kani не сверяет инстанциацию `stub_verified` с инстанциацией `proof_for_contract`. Все гармоники используют именованную функцию `lt::<T>` (строгий порядок по полному значению), так что доказанный и подставляемый контракт имеют одинаковые `T` и `F`.
5. **Домены предусловий = call sites network.** `sort9/13_optimal`: `n <= len <= 17`; `insertion_sort_shift_left`: `2 <= len <= 17`, `offset` = 13/9/1 по длине, префикс отсортирован. Гармоники `proof_for_contract` перебирают весь домен символьно (объединение по классам offset). Шире не нужно: регионы network имеют длину ≤ 17.
6. **`use crate::kani;`** добавлен в `smallsort.rs` в том же месте и в том же виде, что у K1-merge (перед `mod kani_k1;`), чтобы merge их ветки не дал двойного импорта.
7. `swap_if_less`: гармоника перебирает позиции в массиве из 4 элементов, в обоих порядках. Тело не зависит от размера аллокации, кроме проверок границ, которые выражены в `requires`.

## 5. Отвергнутые подходы

- `old(*v_base.add(i))` на обобщённом `T` — E0599 по устройству макроса (см. журнал, п. 1).

## 6. Открытые вопросы

- Время гармоник с полной шириной u64 на длинах 13–17 (job 6).

## 7. Review

(не проводился; требуется только для PASS/FAIL)
