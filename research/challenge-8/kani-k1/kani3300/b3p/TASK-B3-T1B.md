# B3 T1b — смысловое сравнение уже снятых моделей (без пересборки)

2026-11-15. Одна стадия подготовки, worker15. Это верификация корректности, не security-работа. Владелец одобрил T1b.
Локальные cargo/rustc/Kani/CBMC/builds запрещены (Python/git/static только). Без push/CI/PR/issue: запуск — координатор.

## Вход

- `b3p/TASK-B3-T1.md`, `b3p/t1/DESIGN.md`, `b3p/t1/RUN-43701550489.md` (t0 `a4e0340967`) — обязательно прочитать.
- Артефакт `b3-t1-43701550489-1` run [43701550489](https://github.com/Tiramisu-Cake/kani/actions/runs/43701550489)
  (567 MB, хранение 14 дней): A1/B1/A2 по 409 моделей (`records/*.json` → `files/<sha>`), `tools.json`, argv.
- Итог T1: сырые байты A1≠A2 в 72/131 final-моделей. Причины: нумерация rustc `AllocId(N, ThreadLocalIndex)` в именах
  и порядок-зависимая сериализация GOTO-бинарника (нумерованные ссылки на строки/ireps). Положительный контроль
  `control/array_typed_copy`: A1=A2≠B1. Сравнитель упал на `[Errno 36] File name too long`.
- CI-ветка T1: `/root/kani-b3-t1` (head `cfa4b0c52`), там же `.github/b3-t1/` — переиспользовать полезное.

## Задача

CI-only пакет одного короткого job (ubuntu-24.04, ≤ 60 min, без retry), который **не собирает Kani и не пересоздаёт модели**:

1. Скачивает артефакт run 43701550489 (`actions/download-artifact` с `run-id` и `github-token`, `permissions: actions: read`)
   в каталог вне checkout; проверяет sha256 каждого файла против `records/*.json`.
2. Ставит тот же CBMC/goto-instrument 6.11.0, что в T1 (штатный setup Kani на A `0aac16ef62` или эквивалент);
   сверяет sha256 `goto-instrument` с `tools.json` T1 (иначе INVALID).
3. Для каждой логической модели (final обязательно; linked/symtab — желательно) и каждого плеча снимает текстовые
   дампы `goto-instrument --show-symbol-table` и `--show-goto-functions` (только печать, SAT нет); exit каждого вызова
   в журнал, без `|| true`. Имена выходных файлов — короткие хэши, отображение имя→файл в индексе.
4. **Проверка детерминизма инструмента:** для ≥ 3 моделей дамп одного файла дважды — тексты обязаны совпасть.
5. Нормализация — только объяснённая: перенумерация `AllocId(N, ThreadLocalIndex)` по первому вхождению в дампе.
   Любую другую нормализацию добавлять только с обоснованием и A/A-проверкой, что она ничего смыслового не стирает.
6. Сравнение: сначала A1 vs A2 по нормализованным дампам; затем A1 vs B1 (и A2 vs B1). Положительный контроль:
   `control/array_typed_copy` обязан дать A1=A2≠B1, и diff обязан быть в типе-обёртке `tag-<union>::<arm>`
   (payload `[(); 2]` → `Unit`); иначе INVALID_CONTROL.
7. Для каждой модели, где A1=A2≠B1, — unified diff нормализованных дампов в artifact и автоматическая классификация:
   изменения только в компонентах padded-union-обёрток нулевой ширины / изменения в функциях (byte-операции, typecast,
   новые/пропавшие инструкции) / прочее. Классификация — вспомогательная, финальный вывод за координатором.
8. Итог `RESULT.json`: `AA_EQUAL_AFTER_NORMALIZATION` (сколько из 131) / список оставшихся A/A-различий с категориями;
   `B_DIFF` список и классы; статус: `MODELS_EQUAL` / `WRAPPER_ONLY` / `OTHER_CHANGES` / `INCONCLUSIVE_AA` / `INVALID`.
   Интерпретация — по `t1/RESULT-template.md` и ответу 9 аудитора; «только нулевой ширины» не считать безвредным автоматически.

## Где

- Worktree `/root/kani-b3-t1` (ветка T1): новый CI-only коммит поверх текущего head, workflow с push trigger
  `uninit-ci/b3-t1b**` (старый T1 workflow не должен срабатывать на этой ветке), скрипты в `.github/b3-t1b/`.
  Автор per-command Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By. Исходники Kani не менять.
- Research: t0 `research/challenge-8/kani-k1/kani3300/b3p/t1b/` — DESIGN.md, CI-REQUEST.md, synthetic Python-тесты
  нормализатора/классификатора/индекса (без сборок). Commit в t0 с `[skip ci]`, без push.

Финал: `READY <kani CI sha> <t0 sha>` или `STOP <причина>`.
