# TASK — worker11: Profiles OFF CI-only пакет (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

## Контекст

Твой запрос [ch8-profiles/CI-REQUEST.md](kani3300/ch8-profiles/CI-REQUEST.md) (+ JSON, REVIEW)
принят координатором как основа: один OFF batch из 62 строк на stock `0aac16ef62…`, caps из запроса.
Ledger: Profiles получает 1 OFF dispatch (ON остаётся отдельно, cap 3, после 15).
Хост CI: `Tiramisu-Cake/kani` — std-форк этой ночью не создаёт Actions runs на push
(подробно в [TASK-CH8-S1K-HOST-W13.md](TASK-CH8-S1K-HOST-W13.md)); worker13 параллельно делает такой же
хост для S1. Схема одинаковая, согласовывать с ним не нужно — только следовать этому заданию.

## Что сделать

1. CI-only control commit в kani-клоне (worktree `/root/kani-ch8-prof-off-w11`), parent = upstream
   `0aac16ef62da9e9d5645782d458593e5d78143ba`; изменены только `.github/workflows/` и один каталог
   control. Stock push workflows удалить в этом коммите.
2. Workflow: push на `uninit-ci/ch8-prof-off-*`, guard repository `Tiramisu-Cake/kani`; checkouts:
   control (depth 2) + твой точный profiles std source (из CI-REQUEST.json, репозиторий
   `Tiramisu-Cake/verify-rust-std`; если source commit ещё не опубликован, перечисли что координатор
   должен запушить и под каким [skip ci] именем ветки) + tool `model-checking/kani@0aac16ef62…`.
   Внешний `KANI_TOML_FILE`/отдельно собранный stock binary — как в запросе, не tool_config base std.
3. Runner: переиспользовать reviewed S1 runner (g0 `e6ee41020e`, `ch8-s1/integration/ci`) по
   возможности без изменения логики; manifest — твои 62 строки, порядок leaf → consumers, cfg/RUSTFLAGS
   per row, caps, receipts, NOT_RUN fallback, preflight error paths (success/error/timeout/partial/
   missing/null/wrong-type/NOT_RUN/source-stage-target mismatch) synthetic tests.
4. Чеклист: `runner.*` только в step env, fetch-depth ≥2, sibling layout, path normalization от cwd,
   static YAML/actionlint, attempt 1 only.
5. Независимое review, findings исправить. g0 `kani3300/ch8-profiles/off-ci/`: CI-REQUEST
   (SHA/tree/manifest SHA256), REVIEW, HANDOFF. Коммиты `[skip ci]`, author
   `Tiramisu-Cake <igkharin@gmail.com>` в команде. Последней строкой: `READY <control-sha> <g0-sha>`
   или `STOP <причина>`.

## Ограничения

Без push/CI/публикаций/ledger. Без локальных cargo/rustc/Kani/CBMC. Без compiler patch, ослабления
свойств, KeyLess-замены. ON не готовить.
