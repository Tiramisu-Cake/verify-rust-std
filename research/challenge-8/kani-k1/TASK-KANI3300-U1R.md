# KANI3300 U1R — независимое статическое ревью soundness патча U1 (Kani uninit-checks для `MaybeUninit`)

**Выдано координатором 2026-11-11, ночной GO владельца; план согласован с планером.** Только чтение и анализ, **без
сборок** (Cloud Build $0). Runtime **Codex**, одна стадия. Ты не автор патча — ищи ошибки, а не подтверждение.

## Объект

- Патч: `research/challenge-8/kani-k1/kani3300/u1/kani-uninit.patch` на ветке
  `experiment/kani-k1-kani3300u1-20261111` (worktree **/root/verify-rust-std-kani3300-u1**, head `7c0d8e8413`), SHA-256
  `306851ac5dd4f28a11778dfc49e878a5bb62fd7c35a2ad7ad0419053b9504467`. Production 7 файлов, +548/−150, в
  `kani-compiler/src/kani_middle/transform/check_uninit/` и `library/kani_core/src/mem_init.rs`; тесты в
  `tests/expected/uninit/maybe-uninit-*`.
- Эталон без патча: `/root/kani-src-f046b70644` (read-only). Для чтения патченного дерева — новый временный клон
  `/root/kani-review-3300` на `f046b70644` + `git apply` патча (локально, без push). Клон автора `/root/kani-fix-3300`
  не трогать.
- Контекст: `RESULT-KANI3300-U1.md` и `kani3300/u1/PRE-BUILD-KANI3300-U1*.md` в той же ветке (20/20 native PASS).

## Модель shadow в Kani (проверь по исходникам)

Один недетерминированно выбранный байт (object ID + offset) + init bit (`library/kani_core/src/mem_init.rs`). Любая
операция должна быть корректна **для любого выбранного байта**: если какой-то байт может быть неинициализирован, а
проверка его не ловит — это **ложный SUCCESS** (хуже отказа).

## Что проверить (в этом порядке)

1. copy/assign целого слота поверх ранее заполненного dst; сохранение отслеживаемого символического байта при
   переключении адреса; alias/overlap источника и назначения.
2. Extent слота против маски поля; stride/offset массивов и срезов `[MaybeUninit<T>]`; padding; ZST; очистка всего
   слота через пустой aggregate (`MaybeUninit::uninit()` поверх заполненного).
3. `Rvalue::Repeat`: константа, локальный источник, источник из самого назначения; непокрытые формы должны давать
   Unsupported, а не молча проходить.
4. transmute `MaybeUninit<T> -> T` и через `ManuallyDrop<T>`: проверка маски T по адресу источника **до** формирования T.
5. Перенос через аргументы/результаты MIR-вызовов (`LoadArgument`/`StoreArgument`, индекс 0 — return place); raw address
   без инициализации payload.
6. Неизвестные тела (без MIR), непокрытые union (вложенные, произвольные) — должны сохранять диагностический отказ.
7. Взаимодействие с delayed-UB (points-to) и validity passes: не ослаблены ли существующие проверки.

## Результат

**REVIEW-KANI3300-U1R.md** в `research/challenge-8/kani-k1/kani3300/u1/`, ≤ 60 строк:
- вердикт: **SOUND / ISSUES / BLOCKER** (BLOCKER = обоснованный путь к ложному SUCCESS);
- инварианты transfer, которые патч поддерживает (кратко, с файл:строка в патченном клоне);
- контрпримеры: для каждого — минимальная Rust-программа (≤ 15 строк, в стиле `tests/expected/uninit/`, `--edition 2021`,
  `-Z uninit-checks`), ожидаемое поведение корректного инструмента и прогноз поведения патча; классифицировать
  (ложный SUCCESS / ложный отказ / Unsupported, где должна быть поддержка);
- 2–6 regression-кандидатов (файлы `.rs` в `kani3300/u1/review/`, не запускаются);
- замечания по стилю/объёму для upstream (кратко).

## Запреты

- Никаких сборок/dispatch/Cloud, никаких локальных cargo/rustc/Kani/CBMC; Python и `git` — можно.
- Патч U1 и клон автора не менять. Коммит только research-файлов `[skip ci]`, push без force, глобальный git config не
  менять, без `git stash`.
- Никаких Actions/PR/issue/комментариев на GitHub; push в model-checking/kani или Tiramisu-Cake/kani запрещён.
- Чужие PR verify-rust-std не открывать.
- Это верификация корректности инструмента Kani и стандартной библиотеки Rust, не security-работа.

Маркер **KANI3300 U1R ЗАВЕРШЁН** + `REVIEW REQUEST <sha>`, одна стадия, затем стоп.
