# REALCONTRACTS — safety-контракты на настоящих хелперах (спайк, шаг 1)

**Выдано координатором 2026-11-04 (ночь), спайк одобрен владельцем.** **Dispatch только после exact-packet PRE-BUILD
review/GO координатора.** Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-realcontracts**, ветка **experiment/kani-k1-realcontracts-20261104** от
  **59893bff1f**: upstream `233f96f66a` (Kani `cd355b0b`), library Part 1 v7, тулинг K-1 (потолок $120).
- Slug **realcontracts**, stable owner **k1-merge**. Новые stage/ledger/UUID/request_id `realcontracts-*`.
- Project cap **$118.96**, свой cap **$3.00**. **До двух сборок**: G1, затем G2 по итогам G1. Retry нет. Один
  compile-error repair на сборку, если own spent + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**.
- Окно: main 240 + closeout 30 мин.

## Цель

Challenge просит контракты на функциях. Part 1 v7 проверяет контракты на `cfg(kani)`-профилях, которые фиксируют
один компаратор. На методах `small_sort` контракты не принимаются на текущем pin (`default fn`, trait-метод с
собственным generic `F`).

Но `swap_if_less` и `insertion_sort_shift_left` — свободные generic-функции. Их safety-предусловие не зависит от
семантики компаратора. Шаг 1 спайка проверяет:
- можно ли повесить `requires`/`modifies` прямо на эти функции в `smallsort.rs`;
- доказываются ли эти контракты PFC на текущем pin;
- не ломают ли и не замедляют ли они существующие корни.

`ensures` о порядке в этот шаг не входит.

## Что сделать

1. **Контракты в `library/core/src/slice/sort/shared/smallsort.rs`** по существующим конвенциям `core` в этом
   репозитории. Посмотреть, как оформлены `#[safety::requires]`/`#[requires]` и `kani::modifies` в `core` (например,
   `ptr/mod.rs`). Только атрибуты, без изменения тел и сигнатур; вне Kani поведение и codegen не меняются.
   - **`swap_if_less`:** `requires` выражает ровно safety-комментарий функции — обе позиции дают валидные для
     чтения и записи указатели в одной аллокации. Не требовать `a_pos != b_pos`: комментарий этого не запрещает.
     `modifies` — две позиции.
   - **`insertion_sort_shift_left`:** функция safe и сама проверяет `offset`. Контракт: `requires` на `offset`
     (`offset != 0 && offset <= v.len()`, если это соответствует коду), `modifies` — срез. Если на safe-функции
     контракт оформить нельзя, записать точную причину и ограничиться `swap_if_less`.
2. **PFC в новом модуле `verify/realcontracts.rs`** под `cfg(kani_smallsort_controls)`: для спайка набор opt-in;
   решение о переносе в ordinary примет координатор.
   - `swap_if_less`: u8 и u64 (и при запасе времени `[u8; 17]`); backing из 4 элементов; позиции `kani::any()`
     в пределах backing, включая равные; компаратор с произвольным ответом.
   - `insertion_sort_shift_left`: u64, длины 1..=6, `offset` — `kani::any()` в пределах контракта; компаратор с
     произвольным ответом.
   - Covers: обе ветви ответа компаратора, равные позиции (для swap), offset < len.
3. **Негативный контроль:** consumer с `stub_verified(swap_if_less)`, который вызывает его с позицией вне backing.
   Должен упасть на `requires`.
4. **Регрессия:** 2–3 существующих ordinary-корня, которые много раз вызывают эти функции. Например:
   - `network::dispatch_safety_stable_u8_n0_1_2_7_8` — на старой базе NEWPINCAL 11.6 с;
   - `network::swap_contract_four_positions_u8` — 12.8 с;
   - один корень `insertion_safety_u64_*`.

   Сравнить статус и время с прежним.

## Сборки

- **G1:** kind diagnostic, `controls: true`, jobs 1. Строки: PFC пунктов 2–3 и регрессия пункта 4, ≤ 9 строк.
- **G2** (необязательная, после разбора G1 и только с GO координатора): одна из трёх.
  - Если G1 прошла: расширить домены, например `[u8; 17]`, backing 9 или `insertion_sort_shift_left` до 8.
  - Если G1 прошла: первый `requires`/`modifies` на `insert_tail`.
  - Если G1 упала на инструменте: минимальная фикстура для локализации.

## Коммиты

- Library-коммит `[skip ci]`: атрибуты в `smallsort.rs` и новый opt-in модуль. Отдельно research `[skip ci]`.
- Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход. Не
  опрашивать статус в цикле.

## RESULT

**RESULT-REALCONTRACTS.md**, ≤ 35 строк:
- identities;
- точный текст добавленных контрактов;
- таблица строк G1 (и G2);
- регрессия: время до и после;
- что это даёт для `stub_verified` на реальных местах вызова и для следующего шага (`insert_tail`,
  `bidirectional_merge`, модель для `ensures`);
- что не проверено.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep. Raw logs, archives, Cloud Logging и credentials не
  читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Тела runtime-функций, workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **REALCONTRACTS ЗАВЕРШЁН**, одна стадия, затем стоп.
