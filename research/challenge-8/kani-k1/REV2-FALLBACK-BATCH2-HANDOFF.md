# REV2 fallback · второй диагностический пакет

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`. Подготовлена одна Ubuntu job с шестью последовательными singleton. Фактические результаты discovery, компиляции, измерений и проверки свойств остаются `UNKNOWN`. [Задание](REV2-FALLBACK-BATCH2-TASK.md)

## Git и входы

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Локальный control | `b82cc453ed3c916f6996f2ab05f3d5180ac12dcc` | `e62bd43f3f11951fd1deb3aa55c7d474ef7d9f76` | `06d94b37158d559e538a5c8fe93e2d8d813204f9` |
| Будущий trigger | После GO | `e62bd43f3f11951fd1deb3aa55c7d474ef7d9f76` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Ветка control `work/rev2-fallback-control-w11` в `/root/kani-rev2-fallback-control-w11`. Диапазон diff для ревью — `06d94b37158d559e538a5c8fe93e2d8d813204f9..b82cc453ed3c916f6996f2ab05f3d5180ac12dcc`. Задание закреплено в g0 `efc79919f4ddb3b283049fb32a8384b03455bbaf`. [Workflow](/root/kani-rev2-fallback-control-w11/.github/workflows/ch8-q-pilot.yml)

Перед будущим dispatch координатор закрепляет ожидаемое дерево `e62bd43f3f11951fd1deb3aa55c7d474ef7d9f76` в переменной `CH8_REV2_FALLBACK_TRIGGER_TREE` репозитория `Tiramisu-Cake/kani` и сверяет единственного parent. Допуск рассчитан на первый attempt push в `refs/heads/uninit-ci/ch8-q-pilot-v1`. [Guard](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_request.py)

| Вход | SHA-256 |
| --- | --- |
| `ch8-cal1/FALLBACK-REQUEST.json` | `3df45f95aca05071ac4b43c6680434298251a9f09a7e89f27878e42aa5158ecc` |
| `ch8-cal1/fallback-overlay.bundle` | `43a7369986aca65aeaf19f36c7d96fc623dd3464d6353fbf5ce825aa25584c45` |

Std overlay `fb82da3c788c0e705cd598abee723200c0f28c42`, stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, CBMC `6.11.0`. [Request](/root/kani-rev2-fallback-control-w11/ch8-cal1/FALLBACK-REQUEST.json)

## Слоты и время

Префикс exact selector — `slice::sort::shared::smallsort::verify::fallback_rev2::`. Все границы отсчитываются от monotonic epoch job.

| Слот | Суффикс селектора | Object bits | Последний старт | Конец окна при последнем старте |
| ---: | --- | ---: | ---: | ---: |
| 1 | `u64_n08` | 12 | 45:00 | 55:00 |
| 2 | `u8_n12` | 12 | 55:10 | 65:10 |
| 3 | `u8_n16` | 12 | 65:20 | 75:20 |
| 4 | `cell_unstable_n08` | 12 | 75:30 | 85:30 |
| 5 | `cell_unstable_n10` | 12 | 85:40 | 95:40 |
| 6 | `cell_unstable_n16` | 11 | 95:50 | 105:50 |

| Этап | Бюджет | Граница |
| --- | ---: | ---: |
| Setup с preflight до 180 с | 45:00 | 45:00 |
| Шесть окон по 600 с и по 10 с на слот | 61:00 | 106:00 |
| Постаттестация | 2:00 | 108:00 |
| Финализация | 5:00 | 113:00 |
| Upload | 7:00 | 120:00 |
| Резерв | 9:00 | 129:00 |
| Дополнительный запас | 11:00 | 140:00 |

Каждый слот использует `--jobs=1`, профиль `-Z` и `--no-assert-contracts`, выключенные uninit и validity, отдельные target, output и tmp. Object bits берутся из строки request и передаются через `--cbmc-args --object-bits <n>`. Номинальный RSS cap слота — 6 GiB, резерв памяти — 2 GiB. Пять секунд внутри окна слота выделены на проекцию и receipt. После отсечки по времени или памяти следующие слоты допускаются при валидном сэмплере и подтверждённом reap. При срабатывании остановки контроля остаток roster получает именные `NOT_STARTED`. [Runner](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py)

Receipt сохраняет первые CNF по потокам с числом переменных, дизъюнктов и фазой, маркеры нативных стадий и ограниченный timeline supervisor. Телеметрия CAL2 отдельно фиксирует пик RSS CBMC и доступный PSS наблюдаемого PID вблизи пика. Ориентиры 120 с VT и 4 GiB служат для диагностики. При штатном ненулевом выходе с `too many addressed objects` на OB11 receipt фиксирует `OBJECT_BITS_EXHAUSTED` и `INADMISSIBLE_PROFILE` с исходной диагностической строкой и координатами в потоке. Сравнение с N16 OB12 из run `45358377716` относится к последующему разбору. [Receipt и summary](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_report.py)

## Локальные проверки

- Полный Python suite control, `python3 -B -m unittest discover -s ch8-cal1 -q` — 139 тестов прошли. Покрыты порядок, argv для шести слотов, бюджет 140 минут, продолжение после TIMEOUT и RSS_LIMIT, сохранение стадийности, CNF, RSS/PSS и классификация ошибки OB11. При порче request и bundle после допуска trigger проверены `error.json` и шесть именных `NOT_STARTED` с object bits.
- `git diff --check` прошёл для диапазона control и для синтетического trigger относительно его parent. PyYAML разобрал workflow из точного дерева, `bash -n` проверил шесть shell-шагов.
- Локальное синтетическое событие push с точным деревом и единственным parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b` принято командой `pins`. С pin предыдущего дерева событие отклонено. На принятом событии локальный `finish` сформировал шесть именных `NOT_STARTED` с ожидаемыми object bits.
- Стадия полностью локальная, без CI, push и запусков Cargo, rustc, Kani или CBMC.
