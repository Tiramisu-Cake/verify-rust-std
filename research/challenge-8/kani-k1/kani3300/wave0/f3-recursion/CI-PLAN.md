# План CI F3: два запуска координатора

Подготовка выполнена без push, CI и публикаций. Лимит задания — две стадии: быстрый uninit-ci, затем полный стандартный набор на финальной голове. Запуски выполняет координатор; автоматических retries и дополнительного baseline-запуска этот план не предусматривает.

## Кандидат

- Worktree: `/root/kani-fix-delayed-ub-recursion-w14`.
- Ветка: `fix/delayed-ub-recursion`.
- Source: `b69f484e8c7bf43783bfcf29793429b3ad0ae9f3`.
- Source tree: `a0c935194321484d9e9bb1cb284ee736d72a99b3`.
- Единственный parent: upstream `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- Автор/коммиттер: `Tiramisu-Cake <igkharin@gmail.com>`; без `[skip ci]` и Co-Authored-By.

Workflow-файлы source совпадают с upstream. Быстрый CI требует отдельной служебной ветки `uninit-ci/**`, подготовленной координатором по принятому механизму; в upstream-коммит её инфраструктура не входит. Перед запуском проверить exact source SHA и совпадение compiler/test bytes со source. Stock push-workflows имеют wildcard branches: изоляция quick-ветки должна сохранить бюджет и исключить случайный дополнительный полный набор.

## 1. Быстрый uninit-ci

Одна сборка Kani на Ubuntu 24.04 x86_64, затем штатный compiletest `expected` с фильтром `uninit/`:

```bash
cargo build-dev
cargo run -p compiletest -- --suite expected --mode expected --no-fail-fast --timeout 2400 uninit/
```

Команды предназначены для CI. Использовать зависимости pinned source, `scripts` в PATH и `KANI_FAIL_ON_UNEXPECTED_DESCRIPTION=true`, как в штатном regression script. Новые файлы задают edition 2021; при прямом вызове Kani передавать `RUSTFLAGS=--edition=2021`. `--require-success` неприменим к expected suite: диагностические и отрицательные тесты намеренно возвращают ошибку.

Проверить компактный результат каждого теста и фактический запуск новых файлов:

- `recursive-delayed.rs`: сообщение `error: Kani does not support memory initialization checks across recursive calls.`, source line `recurse(value, depth - 1);`, ненулевой обычный compiler exit; без stack overflow, ICE, signal или timeout. Исходный helper вызывается с depth 0: диагностика относится к статическому анализу достижимого тела.
- `repeated-calls.rs`: `repeated_calls_uninitialized` обнаруживает чтение uninitialized `u128`; `repeated_calls_initialized` успешно проверяется. Summary: один успешный harness и один failure. Оба последовательных вызова helper допускаются, в том числе с разными указателями.
- Существующие `uninit/delayed-ub`, `uninit/delayed-ub-unsupported-call` и остальные uninit tests сохраняют expected. Compiler error вместо их верификации считается регрессией.

Сохранить source/CI head и tree identities, команды, native exits, test verdicts и termination reason. Build error, missing output, skipped, timeout и частичный прогон не считать PASS. Для исходной регрессии использовать уже сообщённый в задании run `43882466907` на pinned main; это сведения владельца, самостоятельно здесь не подтверждённые. Дополнительный baseline CI в эти две стадии не включён.

## 2. Полный стандартный набор на финальной голове

После успешного quick CI координатор проверяет финальный source SHA, чистоту ветки и сохранность единственного upstream parent. При исправлении кандидата зафиксировать новый SHA; полный набор относится именно к финальной голове. Публикация и запуск — действия координатора в следующей стадии, здесь они не выполнялись.

Стандартный push на `fix/delayed-ub-recursion` в `Tiramisu-Cake/kani` запускает:

| Workflow | Что проверить |
| --- | --- |
| Kani CI (`kani.yml`) | regression на macOS 15 Intel, macOS 15 ARM, Ubuntu 22.04, Ubuntu 24.04, Ubuntu 24.04 ARM; benchcomp-tests, perf, llbc-regression, documentation |
| Kani Format Check | copyright/format и оба Clippy режима |
| Cargo Deny | audit |

В каждом regression job штатный `scripts/kani-regression.sh` включает новый expected-каталог, unit tests и все стандартные suites. Проверить форматирование Rust в regression, фактическую диагностику рекурсии и оба companion harness на каждой платформе. Не изменять expected, controls или workflow ради PASS.

Для полного стандартного **PR** набора координатор должен также включить штатные PR-триггеры в эту вторую стадию:

| Workflow | Условия и проверки |
| --- | --- |
| Release Bundle | PR/merge_group; сборка и тесты bundles, local toolchain |
| Check Std Verification | PR; Ubuntu 22.04 и macOS 15 |
| Kani Extra | pull_request_target; auto-label, workflow из base |
| Kani Benchmarks | PR; end-to-end/compiler jobs по штатным labels |

Один push не запускает весь PR-набор. Для PR checkout зафиксировать head/base/merge SHA и tree, чтобы связать проверку с финальным кандидатом. Отдельные schedule/manual workflow и release tags в план не входят; публикация release не требуется. Условные benchmark skips записать как skips. Для каждого стандартного workflow сохранить итог jobs; cancelled/skipped/timeout не подменять успехом. Две стадии бюджета не означают два отдельных workflow run ID: вторая стадия по заданию состоит из полного стандартного набора.

После фактического прогона заменить единственный `FULL_FORK_CI_RUN_URL` в PR-TEXT.md ссылкой на финальный Kani CI и обновить Testing по результатам всего набора. До этого PR-текст — черновик, runtime verdict кандидата — NOT_RUN.
