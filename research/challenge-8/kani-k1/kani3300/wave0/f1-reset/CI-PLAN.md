# План стандартного CI в форке

Подготовлен без push, dispatch, PR или изменения настроек Actions. Все команды ниже предназначены для следующего отдельно разрешённого запуска.

## Зафиксированный кандидат

- Worktree: `/root/kani-fix-autoharness-uninit-reset-w14`.
- Ветка: `fix/autoharness-uninit-reset`.
- Source: `bc8f8bb57edc6ed600d331ad8ea8a40776474433`.
- Единственный родитель: upstream `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- Форк: `Tiramisu-Cake/kani`; локальный `origin` указывает на другой локальный репозиторий, поэтому команда публикации использует явный URL.

## Как получен пример #5153

Проверены [текст смерженного PR](https://github.com/model-checking/kani/pull/5153), [метаданные запуска](https://api.github.com/repos/Tiramisu-Cake/kani/actions/runs/43028586621), список jobs и список workflow runs для его head.

Прогон [43028586621](https://github.com/Tiramisu-Cake/kani/actions/runs/43028586621) создан событием `push` в `fix/default-fn-contracts-5116-v2`, head `a139af7ac47b794eaf7b8bdcae52a7ba0a866fea`, workflow `.github/workflows/kani.yml`. Actor и triggering actor — `Tiramisu-Cake`; `pull_requests` пуст. Это обычный push workflow, а не `workflow_dispatch` или специальный runner. YAML на том head разрешает push во все ветки через `branches: ['**']`.

На том же head API возвращает три workflow: Kani CI `43028586621` (aggregate `cancelled`), Kani Format Check `43028586622` (`success`), Cargo Deny `43028586891` (`success`). У Kani CI прошли regression на Ubuntu 22.04, Ubuntu 24.04, Ubuntu 24.04 ARM и macOS 15 Intel, benchcomp-tests, perf, llbc-regression и documentation. `regression (macos-14)` отменён; в тексте #5153 причина — retired runner image. Этот запуск является образцом механизма, а не результатом нового кандидата.

## Стандартный push-набор на новом head

Workflow-файлы кандидата совпадают с закреплённым upstream. Их не нужно менять или переносить из старой CI-ветки.

| Workflow | Ожидаемый набор |
| --- | --- |
| `kani.yml` — Kani CI | regression: `macos-15-intel`, `ubuntu-22.04`, `ubuntu-24.04`, `macos-15`, `ubuntu-24.04-arm`; benchcomp-tests; perf; llbc-regression; documentation |
| `format-check.yml` — Kani Format Check | format-check и clippy-check |
| `deny.yml` — Cargo Deny | audit |

Каждый regression job выполняет штатный `scripts/kani-regression.sh`, включая script-based-pre и новый каталог `autoharness_uninit_reset`. Перфоманс, LLBC и остальные suite сохраняют штатные настройки. У новой матрицы `macos-15` заменяет старый `macos-14`.

После разрешения публикации:

1. Проверить чистоту worktree, source/parent и отсутствие удалённой ветки с чужой историей. Убедиться, что Actions и используемые actions разрешены в форке. При отказе сохранить причину; настройки в текущем задании не менять.
2. Опубликовать именно подготовленный source обычным push, без force и без изменения commit message:

   ```bash
   git -C /root/kani-fix-autoharness-uninit-reset-w14 push https://github.com/Tiramisu-Cake/kani.git bc8f8bb57edc6ed600d331ad8ea8a40776474433:refs/heads/fix/autoharness-uninit-reset
   ```

3. Проверить удалённый SHA. В Actions найти все три запуска с `event=push`, `head_branch=fix/autoharness-uninit-reset` и полным `head_sha` кандидата. У этих workflow отсутствует `workflow_dispatch`; `gh workflow run` для них не подходит. Отсутствие запуска не обходить повторными коммитами или изменением workflow.
4. Дождаться terminal результатов всех jobs во всех трёх workflow. Проверить новую фикстуру на каждой платформе, успешную проверку initialized-read и обнаружение uninitialized-read. Cancelled/skipped/timeout не объявлять успешными проверками.
5. Заменить `FULL_FORK_CI_RUN_URL` в PR-TEXT.md одной ссылкой на новый Kani CI; обновить Testing по фактическим результатам всего push-набора. Историческую ссылку #5153 в PR не переносить.

## Дополнительные стандартные PR workflow

Обычный push даёт полный набор, полученный для #5153 в форке, но upstream также имеет workflow, зависящие от PR. Если под полным набором требуется весь стандартный PR CI, следующим отдельно разрешённым действием нужен PR **внутри форка**, head `fix/autoharness-uninit-reset`, base `main`:

| Workflow | Событие / условие |
| --- | --- |
| `release.yml` — Release Bundle | `pull_request`; сборка и проверка bundles |
| `verify-std-check.yml` — Check Std Verification | `pull_request`; Ubuntu 22.04 и macOS 15 |
| `extra_jobs.yml` — Kani Extra | `pull_request_target`; auto-label, исполняется workflow из base |
| `bench-pr.yml` — Kani Benchmarks | `pull_request`; jobs зависят от `Z-EndToEndBenchCI` / `Z-CompilerBenchCI` |

Kani CI, Format Check и Cargo Deny также создадут PR-прогоны. Проверить base, head и merge SHA: обычный checkout PR тестирует merge ref; tree должен совпадать с кандидатом, чтобы приписывать результат этой голове. Если fork `main` разошёлся, сначала зафиксировать различие и согласовать отдельный путь, не менять кандидата молча. Benchmark jobs запускаются при соответствующих labels; автоматический label через GITHUB_TOKEN сам не создаёт событие для benchmark run, ручной label или следующий synchronize обрабатывается штатно. Такие labels сейчас не добавлялись.

Scheduled/manual Slow tests, CBMC Latest, dependency update automation и main-only сравнительные benchmarks имеют отдельные триггеры. Они не входят в обычный push-набор #5153. Публикацию upstream PR и запуск дополнительных автоматизаций это задание не разрешает.

## Проверка различающего теста

Ожидается: fixture падает на upstream из-за принятого uninitialized-read; с патчем обе команды соответствуют expected. Это пока вывод из кода, не результат исполнения. После отдельного разрешения CI базовый контроль должен сохранить новый test-каталог и убрать только compiler hunk в отдельном CI-кандидате, основанном на том же upstream. Он должен подтвердить неправильное принятие uninitialized-read; финальный штатный прогон выполняется на source SHA выше. Этот дополнительный контроль сейчас не создан и не запущен.
