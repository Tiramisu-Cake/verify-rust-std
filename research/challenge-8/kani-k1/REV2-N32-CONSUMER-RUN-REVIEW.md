# REV2 · N32 consumer · ревью пакета запуска

Ревьюер: субагент Claude `smallsort-reviewer` (read-only). [Run handoff](REV2-N32-CONSUMER-RUN-HANDOFF.md) (g0 `e2e71ff957`)

**GO_WITH_NITS на один диагностический Ubuntu-прогон.** Пакет: control `b3b6b42b845e2a590149d6d0d2e430c3a2f95427`, tree `adda4d22098a1bbf99e77ac674b9eaa3c95cee61`, единственный parent `efaf43d823`, Std overlay `b93859fb447a39c0c8c7d854f70dedf9a47b263f`, request `5cefc5d2…78a2`, bundle `21dda558…f046`. Блокеров нет.

## Замечания

1. **Trigger ещё не создан.** Его нужно собрать `commit-tree adda4d… -p 467af9cb8dba0e3be78a8d7d07672a1943c4806b` с сообщением без `[skip ci]`. До push задать `CH8_REV2_N32_CONSUMER_TRIGGER_TREE=adda4d…`.
2. **Узкий таймаут self-test в `pins`** (`ch8-q-pilot.yml:51-52`). Suite идёт около 23–24 с на 2 CPU при таймауте 50 с. Runner GitHub имеет 4 vCPU, предыдущие пакеты проходили self-test за 13–20 с.
3. **Setup трижды компилирует core в бюджете 45:00.** Поздний старт первого слота совпадает с концом setup. Медленный setup приведёт к fail-closed `NOT_STARTED`. Тайминг унаследован.
4. **Matcher контроля требует точного имени функции и колонки.** Если Kani напечатает иначе, будет `MISMATCHED` (fail-closed).
5. **`PAIR_WITHIN_PROFILE` описывает только пару bits/corrupt.** Байтовые корни вставок принимать по `roster_within_profile` и `expected_result` каждой строки.
6. **Сумма таймаутов шагов (113 мин) больше job (90 мин).** Это не дефект: внутренние дедлайны от epoch завершают обычный путь к 72:40.

## Проверено

- **Идентичности.** Bundle (prereq `dab03cf510`, единственный HEAD `b93859fb`) и цепочка CAL1 → CAL2 → FIX3 → binding → geometries → N32 сходятся. `check_overlay_layout` проходит, `smallsort.rs` не менялся с FIX3.
- **Roster.** Digest `b8b7a67b…`, селекторы и порядок совпадают с исходником. Вставки ожидают VERIFIED, bits — VERIFIED, corrupt — единственный FAILURE `POPCOUNT` на `:54:5` в `check_network::<true>`, одинаково в regular и stock. Все четыре корня — plain Proof без Replace и stubs.
- **Риск компиляции.** Не найден: видимость, bounds и cfg сверены.
- **Control.** Pin берётся из переменной и проверяется во всех шагах. Отклоняются неверный pin и изменённое дерево с trailer. Caps 4/2/10 GiB, все внутренние бюджеты меньше таймаутов шагов, затенения имён нет.
- **Команды.** Suite 104/104 с обычными часами и с часами от 60 с. Прошли YAML, `bash -n`, `git diff --check`, rustfmt `--check` и bundle verify/unbundle.
