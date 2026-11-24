# REV2 fallback · независимое diff-ревью второго пакета

**GO** для `06d94b3715..b82cc453ed`. Блокирующих замечаний нет. Ревью выполнено по заданию g0 `efc79919f4`. Данные handoff g0 `28bda22c74` сверены с Git-объектами, кодом и локальными проверками. База сравнения — control, одобренный в Round 3 (`c62004f050`). `proof_credit=NONE`. [Задание](REV2-FALLBACK-BATCH2-TASK.md) · [Handoff](REV2-FALLBACK-BATCH2-HANDOFF.md) · [Предыдущее ревью](REV2-FALLBACK-CONTROL-REVIEW.md)

## Входы и допуск

- Control `b82cc453ed3c916f6996f2ab05f3d5180ac12dcc` имеет единственного parent `06d94b37158d559e538a5c8fe93e2d8d813204f9`. Tree control и будущего trigger совпадает с `e62bd43f3f11951fd1deb3aa55c7d474ef7d9f76`. Локальный `pins` принял синтетический push с этим tree и единственным parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Другой tree с тем же parent, предыдущий pin, отсутствующий pin, другой parent, два parent и attempt `2` отклонены без сигнала допуска. Workflow сохраняет exact push gate, `contents: read`, передачу `CH8_REV2_FALLBACK_TRIGGER_TREE` и условия финализации и upload. [Tree guard](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_request.py:99) · [Workflow](/root/kani-rev2-fallback-control-w11/.github/workflows/ch8-q-pilot.yml:14)
- SHA-256 request `3df45f95aca05071ac4b43c6680434298251a9f09a7e89f27878e42aa5158ecc`. Bundle побайтно совпадает с одобренной базой, SHA-256 `43a7369986aca65aeaf19f36c7d96fc623dd3464d6353fbf5ce825aa25584c45`. Цепочка std, overlay `fb82da3c78`, stock Kani `9834c96c`, проверка CBMC `6.11.0` и аттестация совпадают с одобренной базой. Проверка bundle на shallow checkout прошла. [Пины и проверка входов](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_request.py:14) · [Аттестация](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py:100)

## Roster и сроки

В overlay `fb82da3c78` каждый из шести селекторов зарегистрирован ровно один раз под `slice::sort::shared::smallsort::verify::fallback_rev2::`. Порядок и object bits совпадают в request, argv и summary. [Overlay](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/fallback_rev2.rs:56) · [Roster](/root/kani-rev2-fallback-control-w11/ch8-cal1/FALLBACK-REQUEST.json:54) · [Argv](/root/kani-rev2-fallback-control-w11/ch8-cal1/run.py:371)

| Слот | Суффикс селектора | Object bits | Последний старт от epoch | Конец при последнем старте |
| --- | --- | ---: | ---: | ---: |
| 1 | `u64_n08` | 12 | 45:00 | 55:00 |
| 2 | `u8_n12` | 12 | 55:10 | 65:10 |
| 3 | `u8_n16` | 12 | 65:20 | 75:20 |
| 4 | `cell_unstable_n08` | 12 | 75:30 | 85:30 |
| 5 | `cell_unstable_n10` | 12 | 85:40 | 95:40 |
| 6 | `cell_unstable_n16` | 11 | 95:50 | 105:50 |

- Сравнение шести сгенерированных argv с одобренными профилями на одинаковых путях показало только ожидаемые различия в селекторе и значении `--cbmc-args --object-bits`. `--jobs=1`, набор `-Z`, `--no-assert-contracts` и отсутствие opt-in флагов uninit и validity подтверждены. Каждый слот получает собственные cwd, target, export и tmp. [Вызов слота](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py:262)
- Workflow задаёт 140 мин, request — 8400 с. Setup с preflight до 180 с завершается к 45:00. Шесть окон по 600 с с интервалами по 10 с дают границу измерений 106:00. Постаттестация до 108:00, финализация до 113:00, upload до 120:00. После резерва до 129:00 остаётся 11 мин. В каждом слоте дедлайн supervisor на 5 с раньше дедлайна receipt. [Лимиты](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_request.py:28) · [Расчёт границ](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py:40)

## Отсечки и receipts

- `supervisor.py` и `telemetry.py` побайтно совпадают с одобренной базой. Номинал 6 GiB, резерв 2 GiB, RSS-стоп, проверка reap и пороги остановки кампании сохранены. В синтетической кампании с валидным сэмплером и подтверждённым reap после `TIMEOUT` и `RSS_LIMIT` запустились все следующие слоты. Тесты ошибки сэмплера и неподтверждённого reap сохранили причину остановки и пять именных `NOT_STARTED`. Тесты просроченного staging сохранили технический исход и отметку дедлайна. [Остановка слота и кампании](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py:276) · [RSS-стоп](/root/kani-rev2-fallback-control-w11/ch8-cal1/supervisor.py:821)
- При раздельной порче request и bundle на допущенных синтетических деревьях `pins` завершался ошибкой с `trigger_admitted=true`. `finish` сформировал `error.json` и шесть именных `NOT_STARTED` с точными selectors, object bits и причиной. Setup и рабочие каталоги отсутствовали. Размеры и SHA-256 членов индекса совпали с файлами. [CLI](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py:370) · [Финализатор](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_report.py:43)
- Receipt сохраняет первую CNF по каждому потоку с числом переменных, дизъюнктов и фазой, нативные маркеры стадий и ограниченный timeline supervisor. Переиспользована телеметрия CAL2 с пиком RSS CBMC и доступным PSS выбранного PID вблизи пика. Ориентиры 120 с VT и 4 GiB остались диагностическими. Синтетический ненулевой выход OB11 со строкой `too many addressed objects` в формулировке CBMC 6.11.0, отображённой stock Kani, дал `OBJECT_BITS_EXHAUSTED` и `INADMISSIBLE_PROFILE` с исходной строкой из потока и её координатами. Тот же диагностический маркер на OB12 в тесте сохранил `INCOMPLETE`. [Парсер CNF](/root/kani-rev2-fallback-control-w11/ch8-cal1/native_metrics.py:82) · [Ошибка профиля](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_projection.py:62) · [Сводка](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_report.py:13)

## Локальная валидация

- `python3 -B -m unittest discover -s ch8-cal1 -q` — 139 тестов прошли. `git diff --check` прошёл для control diff и синтетического trigger относительно parent. PyYAML разобрал workflow из точного tree, `bash -n` прошёл для шести shell-шагов.
- Проверки ограничены локальным diff, Git-объектами и синтетическими входами. Фактические discovery, компиляция, VT, RSS, PSS и исходы проверки свойств остаются `UNKNOWN`.
