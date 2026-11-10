# KANI5116 KT1 — K-1 runner: patch поверх пина Kani и native regression-тесты Kani

**Выдано координатором 2026-11-10, GO владельца на доработку GCB-сборки Kani.** Research-ветка, в подачу не идёт.
Dispatch только после exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Зачем

Готовим проверку исправления [kani#5116](https://github.com/model-checking/kani/issues/5116) (контрактные атрибуты на
specialization `default fn` не парсятся). Локальная сборка Kani запрещена, публичного fork нет. Нужна возможность
собрать в GCB Kani = официальный пин + наш patch-файл и прогнать выбранные regression-тесты самого Kani. Сам фикс —
следующий этап (KF1), не здесь.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani5116**, ветка **experiment/kani-k1-kani5116-20261110** от `9b1758ab81`
  (пин Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, nightly-2026-10-23). Пин и toolchain не менять.
- Исходники Kani для чтения: read-only clone `f046b70644` в `/root/kani-src-f046b70644` (не коммитить в
  verify-rust-std, не собирать).
- Slug **kani5116**, stage `kani5116-kt1`, stable owner **k1-merge**, request `kani5116-kt1-*`. Параллельно на
  ветке experiment/kani-k1-traitpfc-20261110 идёт другой этап: его файлы, ledger и сборки не трогать.
- Свой cap **$0.80**: одна калибровочная сборка (резерв ≤ 59 мин timeout); repair только если влезает по
  фактическому ledger. Окно: main 300 + closeout 30 мин; T0 — при GO.

## Изменения tooling (только `research/challenge-8/kani-k1/tools/` и при необходимости cloudbuild)

1. **`kani_patch` в request** (необязательный): путь внутри опубликованного research-дерева (без `..`/symlink) +
   SHA-256. До дорогой сборки: наличие, digest, `git apply --check` на свежем checkout пина. Применять ровно
   проверенные байты после checkout, до сборки. Любое расхождение/конфликт → request-error без сборки. В summary —
   pin SHA, patch SHA-256, identity дерева после apply (включая новые файлы; HEAD после apply не идентифицирует
   дерево), diffstat, `kani --version`. Без нового remote/fork/pool/IAM.
2. **Новый kind `kani-tests`**: typed manifest `{suite, mode, file}` → runner строит полные имена и запускает
   `cargo run -p compiletest -- --suite <s> --mode <m> --src-base … --exact '<name>'` из корня Kani (уточни точную
   форму по исходникам `f046b70644`), `RUST_TEST_THREADS=1`, per-test и общий wall-time лимиты. verify-std не
   запускается. Не использовать `scripts/kani-regression.sh` целиком. Release-сборка — документированной формой
   (`cargo build-dev -- --release`, проверь), без смешения со старыми debug-артефактами; учесть сборку compiletest
   и фактические binary paths.
3. **Gate по native результатам compiletest:** точные имена выполненных тестов = manifest, `running N tests`, итоги
   по каждому; ноль тестов, ignored, filtered-out, timeout, частичный/повреждённый summary — не PASS. Слова
   SUCCESS/FAILED в выводе Kani итогом не считаются. Expected-тесты: положительным нужен `--require-success`
   (или эквивалент по исходникам), отрицательным — конкретная ожидаемая диагностика. Поддержать ожидаемый отказ
   теста (`expect: fail` + обязательная подстрока диагностики), чтобы baseline repro засчитывался только при
   нужной ошибке.
4. Существующие kinds без `kani_patch` — неизменные args/routes/status/binding/резервы; бюджет нового kind
   согласован в `k1g.sh`, `kani_k1.py`, `gcb-k1.sh`. Optional `kani_patch` поддержать и для diagnostic/verify-std
   маршрута (понадобится в KF2), но в KT1 его не прогонять.
5. Кеш сборки Kani не вводить (свежая сборка).

## Тесты и приёмка

- `test_kani_k1.py` + штатные service/error-path checks: bad path/hash, symlink/`..`, missing patch, apply conflict,
  неизвестный/пустой/дублированный selector, несовпадение фактического набора, nonzero exit, timeout,
  ignored/filtered, отсутствующий/повреждённый summary, сборочный отказ, бюджет/дедлайн, gate после upload. Плюс
  неизменность старых веток (не только happy path). Все проходят локально (Python), check-tooling по diff.
- **Калибровочная сборка** `kani-tests` на пине **с test-only patch** (только новые fixtures, без фикса макросов):
  - `kani/FunctionContracts/generic_fn_pointer_argument.rs`, `kani/Stubbing/stub_set_multiple_use.rs`,
    `ui/function-contracts/trait_default_fn_err.rs`, `expected/function-contract/generic_default_missing_required.rs`
    (существующие, под `tests/`) — PASS;
  - наш repro из #5116 как новый fixture (`tests/kani/FunctionContracts/…`) — `expect: fail` с диагностикой
    «expected `fn`» (EXPECTED_REPRO_FAILURE), любой другой отказ — не засчитывается.
  Это «код Kani без исправления + тестовый patch», не неизменённое дерево.
- PASS: все tooling checks; калибровка — 4 соседних PASS, repro — ровно ожидаемый отказ, identity patch/дерева в
  evidence. После приёмки этот полный commit = **новая tooling base для KF1/KF2** (записать SHA в RESULT).

## RESULT

**RESULT-KANI5116-KT1.md**, ≤ 40 строк: identities (commit, pin, patch SHA-256, дерево после apply); схема request и
manifest; список изменённых файлов tooling; error-path checks; таблица тестов калибровки (имя, ожидание, итог,
время, ключевая строка диагностики); время сборки Kani и compiletest; расход; новая tooling base; ограничения
(subset ≠ полный upstream CI).

## Коммиты, ожидание, запреты

- Коммиты `[skip ci]`, push без force, глобальный git config не менять, `git stash` не использовать.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded K-1 summaries/rows/log-grep через `k1g.sh` (`smallsort-brief`, если индексирован). Прямых
  GCS/storage/download/logging-команд нет; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC; Python-тесты tooling и rustfmt-обёртка — можно. Никаких
  Actions/PR/issue/комментариев на GitHub, никакого fork Kani.
- Только наш код, исходники/тесты/документация Kani на `f046b70644`. Чужие PR verify-rust-std, их ветки и код не
  открывать. Gcloud config/IAM не менять.

Маркеры `REVIEW REQUEST <sha>` / **KANI5116 KT1 ЗАВЕРШЁН**, одна стадия, затем стоп.
