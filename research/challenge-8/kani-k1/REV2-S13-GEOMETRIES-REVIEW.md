# REV2 · три геометрии S13 · независимое ревью R1

Ревьюер: субагент Claude `smallsort-reviewer` (read-only). [Handoff](REV2-S13-GEOMETRIES-HANDOFF.md) · [Задание](REV2-S13-GEOMETRIES-TASK.md)

**NO-GO** для Std `217b8efaa6c9c0d6e5d44f77e98d74bd5493360a`, control `7eb91451d891bfdd802591b30b065f941c51b019` (tree `7665875a52…`), review-trigger `7e8cf4c0e3…`, request `f60a71e6…69e8`, bundle `922639b1…0fc16`. Корни Std и схема доказательства корректны. Блокер один, в control, правка в одну строку.

## Блокер

**B1.** `ch8-cal1/report.py:202-204`, используется в `:212`. Функция `finish` переиспользует имя `pending`. Сначала это словарь `finalization.get("pending", {})`, затем переменная цикла `for pending in artifact.glob("slots/*/*.tmp")`. Если `receipt_window` прервал `dump()` и оставил `.tmp`, то `pending.get(key)` падает с `AttributeError`. `finish` не завершается, upload не происходит, receipts прогона теряются. Это именно путь позднего receipt и медленной проекции. Воспроизведено скриптом: с частичным `receipt.tmp` и отложенной записью — `AttributeError`, без `.tmp` — OK. Исправление: переименовать переменную цикла и добавить тест с частичным `.tmp` рядом с отложенной записью, который проверяет сохранение истинного исхода и предусловия upload.

## Замечания

1. Таймаут шага finish — 5 мин (`ch8-q-pilot.yml:98`), а внутренний дедлайн абсолютный, epoch+72:30 (`run.py:633`). Если setup рано падает, зависший finish убьёт Actions, а не собственный alarm, и upload потеряется. Предложение: `min(publication_deadline, finish_start + 5 мин − запас)`.
2. Сообщение review-trigger содержит `[skip ci]`. Для запуска нужен новый коммит с тем же tree и parent `467af9cb…`.
3. Из `finish` убран fallback request, `spec.load()` идёт до `finish`. Допустимо, так как `pins` уже загрузил request.
4. Нативный ID контроля пока UNKNOWN. Координата 69:5 соответствует прецеденту base1.

## Проверено

- **Идентичности.** Commit, tree, parent, авторы, SHA-256, roster, bundle (prereq `dab03cf510`, единственный HEAD) и цепочка CAL1 → CAL2 → FIX3 → binding → geometries совпадают. `check_overlay_layout` проходит, Std diff затрагивает три пути.
- **Корни.** Все шесть вызывают реальные `sort13_optimal` и `swap_if_less` без stubs. Геометрии [1,18), [13,26), [17,33). Контроль инвертирует один бит и должен упасть только на 69:5 в обоих каналах.
- **45 пар и маска.** 45 пар из тела совпадают на базах 1, 13 и 17. Сеть сортирует все 8192 входа.
- **Лист.** Лист FIX3 зависит только от `v_base, a, b` и покрывает base 1. Для баз 13 и 17 добавлены свои байтовые Check с тем же контрактом.
- **Риск компиляции.** Не найден: импорты и видимость повторяют уже компилировавшиеся модули.
- **Control.** Gate отклоняет неверные pin и изменённое дерево с согласованным trailer. План 88:30 укладывается в job 90 мин. Все таймауты шагов, кроме finish (замечание 1), не короче бюджетов.
- **Команды.** Suite 98/98 с обычными часами и с часами от 60 с. Прошли YAML, `bash -n`, `git diff --check` и rustfmt `--check` новых файлов.

## R2 · FIX1

**GO** на один диагностический Ubuntu-прогон. Control `efaf43d82324fd4d76d07e6bf77bbc7a78434700`, tree `0d4e157ede9479cd50de0c8df3755e40fd85cbd1`, parent `7eb91451d8`. Review-trigger `f8695c617c` с тем же tree и parent `467af9cb…`. Std `217b8efaa6`. Pin для запуска: `CH8_REV2_S13_GEOMETRIES_TRIGGER_TREE=0d4e157ede9479cd50de0c8df3755e40fd85cbd1`.

- **B1 исправлен.** В `report.py:203` переменная цикла переименована в `partial_path`. Воспроизведение даёт `finish OK`, исход `FAILED` сохранён, `.tmp` удалён, `index.json` записан. Новый тест падает на старом коде с тем же `AttributeError`.
- **Дедлайн finish.** Равен `min(epoch+4350, start+290)`, где start берётся при входе в CLI. Тесты проходят на обеих ветках, старый код не выдерживает новый тест.
- **Затенение имён.** AST-сканирование `run.py`, `report.py`, `results.py` и `request.py` других случаев не нашло.
- **Неизменное.** Workflow, CI-REQUEST, bundle, `request.py` и `results.py` побайтно совпадают с R1, хэши `f60a71e6…` и `922639b1…` прежние, Std не менялся.
- **Проверки.** Suite 100/100 с обычными часами и с часами от 60 с, `git diff --check` проходит.
- **Запуск.** Нужен новый trigger-коммит без `[skip ci]`. FIX1 лежит в worktree `/root/kani-rev2-s13-geometries-fix1-control-w14`.
