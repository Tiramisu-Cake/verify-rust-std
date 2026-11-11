# KANI KT2 — tooling: failed-check строки в native excerpt + полевое чтение больших native-записей

**Выдано координатором 2026-11-11, ночной GO владельца на доработку K-1 сборки Kani в GCB.** Tooling-стадия; без
Cloud-сборок ($0), только Python и локальные unit/service-тесты tooling. Runtime **Codex**, одна стадия.

## Проблема (две последние сборки, U1T ff0988c7 и U3 14dd0792)

1. `native_output_excerpt` (`research/challenge-8/kani-k1/tools/kani_k1.py` ≈ :286) выбирает «error lines and tail».
   Строки отказавших проверок Kani — `Failed Checks: …` (terse/regular), блок `Check N: <name>` / `- Status: FAILURE` /
   `- Description: "…"` / `- Location: …` (regular) — в excerpt не попадают, если не содержат слова error. В итоге
   compiletest-ошибка «expected output to contain the line(s)» не диагностируется: неизвестно, какая проверка упала.
2. `k1g.sh native BUILD OFFSET COUNT` → `page-native` падает `one native record exceeds the bounded page size`
   (MAX_MD_BYTES 12000), если одна запись (argv/env/excerpt/metadata) больше страницы; полевого или постраничного
   чтения записи нет. Brief отвечает HTTP 404.

## Что сделать

- Worktree **/root/verify-rust-std-kani-kt2**, ветка **experiment/kani-k1-kt2-20261111** от `c98d7cee0d`. Менять только
  `research/challenge-8/kani-k1/tools/kani_k1.py`, `k1g.sh` (если нужно для новой подкоманды) и тесты
  `test_kani_k1.py` / `test_gcb_native.py`. Lane/workflow/gcb YAML, пин, toolchain — не менять.
1. **Excerpt:** наивысший приоритет кандидатов — строки отказавших проверок: `Failed Checks:` (+ следующая строка
   `File: …`, если есть), и для regular-формата блок из строки `Check N: …` перед `- Status: FAILURE` и следующих
   `- Description:` / `- Location:`. Затем — прежние error/tail. Сохранить все существующие лимиты
   (NATIVE_EXCERPT_LINES, NATIVE_EXCERPT_BYTES, обрезка строк, JSON-escape bound), порядок строк и поля метаданных;
   добавить в `selection` честное описание. Не давать этим строкам gate-credit (excerpt остаётся `diagnostic_only`).
   Если отказавших проверок больше, чем помещается, — явный счётчик omitted failed-check lines.
2. **Чтение записи:** новая подкоманда `k1g.sh native-field BUILD OFFSET FIELD [START [COUNT]]` (или эквивалент в
   `page-native`) — выдаёт одно поле записи (`errors`, `output_excerpt.records`, `diagnostic`, `argv`, …) постранично в
   пределах MAX_MD_BYTES, с identity build/offset/file и `next_start`. Только из summary.json (summaries scope, без raw
   logs). Ошибки — тем же стилем, что существующие.
3. **Тесты:** unit-тесты на (а) terse `Failed Checks:` и regular `Status: FAILURE` блоки (в т.ч. многие отказы,
   длинные строки, Unicode), (б) приоритет над error/tail и соблюдение байтового лимита, (в) отсутствие gate-credit,
   (г) native-field: постраничность, неизвестное поле, offset вне диапазона, слишком большая единица. Service error-path
   тесты для затронутого runner-кода. Все существующие тесты tooling — PASS (`python3 -B -m unittest …`, команды как в
   истории KT1: `git log --format=%B 383fd70895`).
4. **Ретро-проверка без Cloud:** прогнать новую excerpt-функцию нельзя (нет raw output) — не пытаться. Новую подкоманду
   проверить на закешированных summary `/tmp/kani-k1-gcb/summary-ff0988c7-d2f2-4872-b4ea-be581d9de02f/summary/summary.json`
   и `/tmp/kani-k1-gcb/summary-14dd0792-1c06-47be-b931-94f6096a664a/summary/summary.json` (bounded summary, не raw):
   показать в отчёте, что запись offset 1 (U1T) читается постранично.

## Результат

Коммит(ы) `[skip ci]` автор Tiramisu-Cake (через `-c user.name/-c user.email`), push без force. **RESULT-KANI-KT2.md**
(≤ 25 строк): diff summary, новые/изменённые тесты и их результат, новый tooling SHA (для последующих стадий как
tooling base), что не изменилось (gate, лимиты, lanes). Затем маркер `REVIEW REQUEST <sha>` и
**KANI KT2 ЗАВЕРШЁН**. Независимое ревью — по процессу tooling (subagent/Luna), отметить в RESULT.

## Запреты

- Никаких Cloud/dispatch, локальных cargo/rustc/Kani/CBMC; raw logs/archives/credentials не читать; GCS/storage/logging
  напрямую не использовать (кеш summary.json уже локальный).
- Не трогать другие worktree (`kani3300*`, `kani5072`, `kani5116`, `kani-traitpfc`) и клоны Kani.
- Никаких Actions/PR/issue/комментариев.
- Это доработка инфраструктуры верификации стандартной библиотеки Rust, не security-работа. Отвечай кратко.
