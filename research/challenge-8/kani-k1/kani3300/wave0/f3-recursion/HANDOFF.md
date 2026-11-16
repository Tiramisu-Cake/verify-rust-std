# F3: диагностика рекурсии в delayed UB analysis

Статус: локальный кандидат готов, независимый статический review без блокирующих findings. Компиляция и verifier tests — NOT_RUN; результат будущего CI неизвестен.

## Идентичности

- Задание: `TASK-CH8-W0-F3-RECURSION-W14.md`.
- Входной g0: `0e196f01289020cab84bcb8c78e346c9c52d2fc3`.
- Source worktree: `/root/kani-fix-delayed-ub-recursion-w14`.
- Source branch: `fix/delayed-ub-recursion`.
- Source commit: `b69f484e8c7bf43783bfcf29793429b3ad0ae9f3`.
- Source tree: `a0c935194321484d9e9bb1cb284ee736d72a99b3`.
- Единственный parent: `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- Author/committer: `Tiramisu-Cake <igkharin@gmail.com>`; без `[skip ci]` и Co-Authored-By.

## Изменение

Единственный compiler-файл — `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs`, 24 добавленных и 3 удалённых строки. Для каждого entry создаётся общий для вложенных анализов `RefCell<HashSet<Instance>>`. Instance добавляется перед fixpoint и удаляется после сбора результатов, включая cursor replay. Перед анализом regular callee повтор активного Instance вызывает `tcx.dcx().span_err` на span вызова и `abort_if_errors`. Это уже используемый в pinned main механизм диагностики; частичный граф после обнаружения рекурсии не возвращается.

Ключ включает полный Instance с generic args. Последовательный повторный вызов допускается после возврата предыдущего анализа. Прямая и взаимная рекурсия образуют повтор активного Instance; разрастающиеся цепочки разных generic instances этим условием не ограничиваются. Статическая диагностика возможна даже при runtime depth 0, поскольку анализ обходит тело helper.

Справочный `d82752c8bc` просмотрен для active-call идеи; его contract bodies, provenance, Result/error infrastructure и остальные изменения не перенесены. Зависимость от #5172 отсутствует. Source содержит ровно один коммит поверх заданного upstream; workflow-файлы и прочие compiler passes сохранены.

## Тесты

Один новый каталог `tests/expected/uninit/recursive-delayed/`, две пары `.rs`/`.expected`:

- `recursive-delayed`: helper и harness из confirm-main, с обновлённым описанием. Pointer cast в tuple создаёт delayed UB target. Ожидаются compiler error о recursive calls и строка рекурсивного вызова. Вместо ожидаемого сообщения baseline по сведениям задания падает с `has overflowed its stack` (run `43882466907`, main `0aac16ef62`). Этот run и его raw logs здесь не читались; это переданные сведения, не самостоятельное подтверждение.
- `repeated-calls`: два harness с повторными последовательными вызовами helper. Первый передаёт разные объекты и читает uninitialized padding во втором; ожидается failure чтения `u128`. Второй инициализирует объект после helper и успешно проверяется. Expected фиксирует failed-check description, успешную верификацию и итог одного success/одного failure.

## Проверки и review

- `git diff --check` прошёл; source worktree чистый.
- Штатный `scripts/ci/copyright_check.py` прошёл для compiler-файла и обоих новых Rust-файлов.
- Статически сверены pinned-main `span_err`/`abort_if_errors`, оба места вызова `PointsToAnalysis::run`, entry lifetime и cursor replay, механизм substring/consecutive matching compiletest, edition headers и стандартные workflow triggers.
- Независимый review: агент `review_recursion`, GPT-6 Luna HIGH, отдельный контекст, read-only, без вложенной делегации; проверял exact source commit/tree. Блокирующих findings нет. Assurance — STATIC_ONLY, runtime NOT_RUN.
- Отклонение от запрета локального rustc: во время review ошибочно выполнена shell-подстановка `$(rustc --print sysroot 2>/dev/null)` для поиска rust-src через `rg`. Stderr подавлен, exit code не сохранён; фактическое исполнение rustc либо отказ rustup shim — UNKNOWN. Компиляция и тесты не выполнялись. Это отклонение явно сообщено пользователю; утверждать полное отсутствие попыток локального rustc-вызова нельзя.
- cargo, Kani, CBMC, format/build/Clippy и verifier suites не запускались. Исполнимость кандидата и expected требуют CI.

## Передача координатору

`PR-TEXT.md` содержит два абзаца сути, Testing, лицензию и AI disclosure по STYLE-UPSTREAM-RULES. Единственная CI-ссылка — placeholder `FULL_FORK_CI_RUN_URL`; заменить после фактического финального прогона. `CI-PLAN.md` описывает две стадии бюджета: uninit-ci и полный стандартный набор. Quick-инфраструктура в source не добавлялась; её подготовка и все запуски остаются координатору.

Во время работы g0 продвинулся на чужой `b8c5219a82c1deee3771af4e0817169067466bb1`; он сохранён. Изменения этого задания в g0 ограничены тремя файлами `kani3300/wave0/f3-recursion/`, коммит g0 с `[skip ci]`. Push, CI, публикации и ledger changes не выполнялись.
