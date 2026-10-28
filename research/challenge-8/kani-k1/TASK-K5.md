# K-5 — контракты корректности на трёх trait-методах `small_sort`: ограничение Kani или нет

Дата: 2026-10-28. Исполнитель: Codex, одна сессия, окно до 2 ч. Worktree `/root/verify-rust-std-kani-k5`, ветка `experiment/kani-k1-k5contracts-20261028` (от `0f5ad96d` = код пакета подачи `6cfc76cb` + файлы лейна GCB с модулем `verify`). **Бюджет Cloud Build: не более $1 и не более 4 сборок**, lane `gcb-e2-standard-4`, kind `measurement` (timeout 10 мин/гармоника).

## Зачем

Организаторы в review #576 (12.09) и #678 (13.09) указывают: «0/3 sorting-correctness contracts» — на трёх `small_sort` нет `#[ensures]` сортированности с соответствующими `proof_for_contract`. В нашем пакете тоже 0/3: корректность проверяется assert-ами в гармониках и внутренними контрактами (`swap_if_less`, `insert_tail`, `sort4_stable`, `bidirectional_merge`). Владелец хочет в PR **доказательно** объяснить, упирается ли это в Kani. Сейчас у нас нет собственного воспроизведения: строка «невозможны (E0520/E0599)» в наших отчётах взята из чужих сообщений. Наши обходы уже известны (`git show origin/experiment/kani-k1-finalci-20261028:research/challenge-8/kani-k1/RESULT-network.md`, раздел «Журнал решений» п. 1–6, 10): `old()` раскрывается в `.clone()` (E0599 для `T` без `Clone`) — обход счётчиком пробы через `usize`; `FnMut`-компаратор — через `&raw mut`; два `ensures` с `old()` над `&mut [T]` — E0502, обход одним `ensures`.

Результат K-5 — точные факты для текста PR, любой исход полезен: воспроизводимая ошибка инструмента с минимальным примером **или** доказательство, что форма возможна.

## Что сделать

Цели: шесть тел в `library/core/src/slice/sort/shared/smallsort.rs` — `StableSmallSortTypeImpl::small_sort` (default `impl<T>` ≈38 и `impl<T: FreezeMarker>` ≈56), `UnstableSmallSortTypeImpl::small_sort` (≈82 и ≈97), `UnstableSmallSortFreezeTypeImpl::small_sort` (default и специализации ниже). Спецификация — та же, что у внутренних контрактов: на выходе `v` отсортирован по `is_less`, и число элементов, побайтно равных пробе, сохранено (`CopyOnDrop::<T>::…` помощники в `verify/merge.rs`, схема `set_probe`); `modifies(v)`; предусловий нет, кроме тех, что нужны для пробы. Runtime-тела не менять.

1. **A — атрибут на impl-методе.** Повесить `#[cfg_attr(kani, kani::ensures(…))]` (+ `modifies`) на одну реализацию: сначала `default fn small_sort` в `impl<T> UnstableSmallSortTypeImpl for T`. Добавить одну гармонику `proof_for_contract(<путь к этому методу>)` для `u64`, `N` ≤ 4 (новый файл `verify/k5.rs`, `mod k5` в `verify.rs`, под `#[cfg(kani)]`). Если путь к методу trait-impl в `proof_for_contract` не выражается — это отдельный факт; записать точную ошибку и попробовать формы `<u64 as Trait>::small_sort`, путь через `crate::…::Trait::small_sort`.
2. Сборка: `RUN-REQUEST.json` (как в `0f5ad96d`, `agent: coordinator` не использовать — `k1-network`), `k1g.sh dispatch experiment/kani-k1-k5contracts-20261028`, ожидание `k1g.sh watch <build>`. Ошибку компиляции читать только через `k1g.sh summary` / `k1g.sh log-grep BUILD 'error\[E|error:' 60` / `log-lines` (≤200 строк). Записать дословно код ошибки, сообщение, место (≤20 строк на сборку).
3. **Если A не компилируется** — минимизировать причину следующими сборками (всего ≤4): атрибут на специализирующей (не default) реализации; на объявлении метода в трейте; на свободной обёртке `fn` с тем же телом-вызовом (контроль: так компилируется?). Цель — отделить «контракт на `default fn` при специализации» от «контракт на методе трейта вообще» и от нашей спецификации. Связать ошибку с кодом макроса Kani на pin `9461e07a` (`library/kani_macros/src/sysroot/contracts/…` — читать на GitHub, не клонировать).
4. **Если A компилируется** — выполнить `proof_for_contract` для `u64` N 0..4 (и записать время), затем то же для второй реализации (Freeze-специализация). Если доказывается — это не ограничение инструмента; оценить, до какой длины реально (по времени), без длинных прогонов.
5. Поиск по трекеру Kani (issues/PR, открытые и закрытые) по найденной ошибке: `E0520`, `specialization contract`, `default fn contract`, `trait method contract`, `proof_for_contract trait impl`. Только чтение; записать ближайшие аналоги со ссылками.

## Результат

`research/challenge-8/kani-k1/RESULT-K5.md` (русский) + короткий английский абзац для раздела PR «Known limitations» (до 6 строк, сухо, только установленное, со ссылкой на build ID и на issue Kani, если есть аналог; если аналога нет — так и написать). Плюс, если ошибка инструмента установлена: самостоятельный минимальный пример вне std (≤40 строк Rust: trait со специализацией + `#[kani::ensures]` на `default fn` + `proof_for_contract`) в `research/challenge-8/kani-k1/k5-repro.rs` — **не запускать локально**; пометить, что он не проверен, если не проверялся в GCB.

## Ограничения

- **Все коммиты этой ветки — с `[skip ci]` в сообщении** (в форке сейчас включены workflow организаторов с триггером на push в `library/**`; без `[skip ci]` push запустит полный CI). Push без force.
- Ветку `submission/ch8-smallsort-min-20261028` не трогать.
- Сборки только `k1g.sh` в пределах бюджета; Actions/CircleCI нет; локально rustc/cargo/Kani/CBMC не запускать. Полные/сырые логи не читать — только интерфейс `k1g.sh`.
- Код и ветки PR #576/#678/#694/#701 не открывать (их review-тексты организаторов можно).
- Не упоминать rust-lang issues. Внешних действий (issues, комментарии) нет — только подготовить текст.
- Спорное решать самому; владельца не ждать.

## Завершение

Commit + push. Последние строки ответа координатору:

```
REVIEW REQUEST <sha>
K5 ЗАВЕРШЁН
```

После маркера сессию не продолжать.
