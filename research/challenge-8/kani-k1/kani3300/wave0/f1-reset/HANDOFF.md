# F1: самостоятельный reset automatic harness

Статус: локальный кандидат и план CI готовы; проверка Kani на upstream и исправленном head не запускалась.

## Идентичности

- Задание: `TASK-CH8-W0-F1-RESET-W14.md`, исходный g0 `18743fb816465180215fcd86410ecfd46763b0ed`.
- Source worktree: `/root/kani-fix-autoharness-uninit-reset-w14`.
- Ветка: `fix/autoharness-uninit-reset`.
- Source commit: `bc8f8bb57edc6ed600d331ad8ea8a40776474433`.
- Parent: `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- Author/committer: `Tiramisu-Cake <igkharin@gmail.com>`; сообщение без `[skip ci]` и Co-Authored-By.

## Изменение и тест

В `ptr_uninit::is_harness` перенесено распознавание `KaniIntrinsic::AutomaticHarness` из `05da1a7a8c`, включая его комментарий. Compiler diff — один import и семь добавленных строк. Другие части стека не перенесены.

AutomaticHarnessPass строит wrapper на instance intrinsic; UninitPass затем проверяет is_harness и вставляет вызов initialize_memory_initialization_state в начало wrapper. В upstream проверка ограничена proof/proof_for_contract attributes. Без вызова модель сохраняет начальные tracked_object_id/offset, равные нулю, вместо nondeterministic выбора; это объясняет ожидаемое пропущенное чтение padding. Остальные способы распознавания harness сохранены.

Единственный новый каталог: `tests/script-based-pre/autoharness_uninit_reset`, четыре файла. Две функции используют `#[repr(C)]` структуру `{ u8, u32 }`:

- `uninit_read` читает padding по offset 1 через raw pointer; script требует exit 1, expected — FAILURE рядом с описанием `Reading from an uninitialized pointer`, FAILED и summary одной failed function.
- `initialized_read` сначала записывает этот байт через raw pointer и затем читает его без перемещения структуры; script требует exit 0, expected — SUCCESSFUL и summary одной verified function.

Тип указателя в ожидаемом сообщении не закреплён. Сведения задания о run 43783429976 приняты как уточнение владельца: прежняя фикстура обнаруживала чтение, а expected ошибочно требовал `u8` вместо `*const u8`. Raw logs этого прогона не читались. Исторические результаты и ledger не переписывались.

## Выполненная проверка

- `git diff --check` и `bash -n` прошли.
- Штатный `scripts/ci/copyright_check.py` прошёл для изменённого compiler-файла и трёх новых файлов с copyright headers.
- Статически проверены преобразование automatic harness, порядок passes, TryFrom<Instance> и substring/consecutive matching expected в compiletest.
- Подтверждены единственный заданный parent, executable mode 100755 у run.sh и чистый source worktree после коммита.
- cargo/rustc/Kani/CBMC, format/build/Clippy и verifier suites не запускались. Ожидания регрессии на upstream и исправленном head требуют будущего CI.

## Тексты и следующий шаг

PR-TEXT.md следует структуре #5153: два абзаца сути, короткий Testing, лицензия и заданное AI disclosure. Первое предложение содержит воспроизводимую команду; терминология сверена с upstream (automatic harness, memory initialization state, padding, raw pointer). Ссылок на результаты текущего кандидата пока нет: единственный CI URL — явный placeholder `FULL_FORK_CI_RUN_URL`; текст остаётся черновиком до фактического прогона. Указаны ожидаемые различия main/fix без заявления о выполненном тестировании.

CI-PLAN.md фиксирует подтверждённый push-механизм #5153 и полный стандартный push-набор, а также PR-зависимые workflow. Следующее действие владельца — отдельно разрешить публикацию source и CI, подтвердить baseline regression, затем заполнить Testing фактическими результатами. До этого runtime verdict — NOT_RUN.

В ходе задания g0 продвинулся на чужой commit `6aaa7d732d84abbde71acfe4d9dde0adf1b7dc72` (ledger). Он сохранён; собственное изменение ограничено этими тремя файлами в `kani3300/wave0/f1-reset/`. Push, CI, публикации, изменения ledger и настроек workflow не выполнялись.
