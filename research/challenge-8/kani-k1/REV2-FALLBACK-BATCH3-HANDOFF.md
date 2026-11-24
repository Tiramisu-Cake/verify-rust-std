# REV2 fallback · третий диагностический пакет

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`. Локальный FIX выполнен по уточнению планера в g0 `7749e479e1c4b4d08349671465f88ed1b4c452e3` после первого ревью `1a8454bf7f`. Следующие этапы — независимое diff-ревью FIX воркером 13 и отдельный GO планера. [Задание](REV2-FALLBACK-BATCH3-TASK.md#fix-после-первого-ревью) · [Первое ревью](REV2-FALLBACK-BATCH3-REVIEW.md)

## Git и замороженные входы

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Std overlay | `7419ecfa6a2acea1adf1f98d3de5a253d8d716b3` | `44c21cb5518ed210910c3799f263e414891b08b2` | `fb82da3c788c0e705cd598abee723200c0f28c42` |
| Control FIX | `7d991c2515b9203dfee2da1276c423188bcf7a23` | `013ed9c24eba33b8db127786ae26bdff8b24ff49` | `2cb29b59a4c1fd4a071f6202d9d4f9cdce500d26` |
| Будущий trigger | Формируется после GO | `013ed9c24eba33b8db127786ae26bdff8b24ff49` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Std находится в `/root/verify-rust-std-rev2-fallback-w11` на `work/rev2-fallback-w11`. Diff — `fb82da3c788c0e705cd598abee723200c0f28c42..7419ecfa6a2acea1adf1f98d3de5a253d8d716b3`, только `verify/fallback_rev2.rs` и `verify/trait_model.rs`. [Harnesses](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/fallback_rev2.rs) · [Модель](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/trait_model.rs)

Control находится в `/root/kani-rev2-fallback-control-w11` на `work/rev2-fallback-control-w11`. Diff для повторного ревью — `2cb29b59a4c1fd4a071f6202d9d4f9cdce500d26..7d991c2515b9203dfee2da1276c423188bcf7a23`. Handoff находится в `/root/verify-rust-std-kani3300-g0` на `experiment/kani-k1-kani3300g0-20261111`. [Control](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py) · [Workflow](/root/kani-rev2-fallback-control-w11/.github/workflows/ch8-q-pilot.yml)

```bash
git -C /root/verify-rust-std-rev2-fallback-w11 diff fb82da3c788c0e705cd598abee723200c0f28c42 7419ecfa6a2acea1adf1f98d3de5a253d8d716b3
git -C /root/kani-rev2-fallback-control-w11 diff 2cb29b59a4c1fd4a071f6202d9d4f9cdce500d26 7d991c2515b9203dfee2da1276c423188bcf7a23
```

| Вход | SHA-256 |
| --- | --- |
| `ch8-cal1/FALLBACK-REQUEST.json` | `f1ae7c7a4e531d117b125bb5d8a6a749bd196acdad0bae9fff47189cdea9ffea` |
| `ch8-cal1/fallback-overlay.bundle` | `26cf923804117e9b28b5e83715deb6c8648dee51aa193a25b90714ba791ab552` |

| Цепочка std | Commit | Tree |
| --- | --- | --- |
| Shallow base | `dab03cf510df5c35141cde49f1368b1242f5035e` | `7fd542ad59723ff2beeacb9632fb0568e81b0655` |
| Intermediate | `dfdc70f8ccce6365f88fa489968508fa326ec60f` | `9f967855a6e6b71a7f81ecbc81e45a4d388443aa` |
| Batch 2 overlay | `fb82da3c788c0e705cd598abee723200c0f28c42` | `4329b593bdb0d4f3972452648396170f94adea8e` |
| Batch 3 overlay | `7419ecfa6a2acea1adf1f98d3de5a253d8d716b3` | `44c21cb5518ed210910c3799f263e414891b08b2` |

Std, request и bundle сохранены побайтно. Bundle рекламирует только `HEAD` Batch 3. Импорт в detached shallow checkout базы оставляет HEAD и refs прежними. У каждого перехода проверяется точный единственный parent. Stock Kani закреплён на `9834c96ce90ff57d8495416530b080dc3d52ce25`, CBMC — `6.11.0`. Перед разрешённым push координатор задаёт `CH8_REV2_FALLBACK_TRIGGER_TREE` с указанным деревом. Gate принимает attempt 1 события push в `refs/heads/uninit-ci/ch8-q-pilot-v1` репозитория `Tiramisu-Cake/kani`. [Замороженный request](/root/kani-rev2-fallback-control-w11/ch8-cal1/FALLBACK-REQUEST.json) · [Валидатор](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_request.py)

## Селекторы, режимы и сроки

Все селекторы имеют префикс `slice::sort::shared::smallsort::verify::fallback_rev2::`. Единственный cfg-on discovery ожидает 14 Check и 22 Original с точными именами и единичной регистрацией. Слоты идут последовательно, с отдельными рабочими каталогами, target, export и tmp.

| Слот | Суффикс | Роль | Unwind | Обязательство | Старт до | Конец окна |
| ---: | --- | --- | ---: | --- | ---: | ---: |
| 1 | `cell_unstable_n08` | Check | 36 | Полный контракт, `usize`, V34/base1 `[1..9]`, фрагмент GOTO для ручного разбора DFCC | 45:00 | 55:00 |
| 2 | `cell_unstable_n08_narrow` | Check | 36 | Полный контракт, `u8`, V34/base1 `[1..9]` | 55:10 | 65:10 |
| 3 | `u8_n08` | Original | 34 | Порядок и полные кратности | 65:20 | 75:20 |
| 4 | `u64_n08_order` | Original | 34 | Порядок | 75:30 | 85:30 |
| 5 | `u64_n08_counts` | Original | 34 | Полные кратности | 85:40 | 95:40 |
| 6 | `cell_unstable_n10_narrow` | Check | 36 | Полный контракт, `u8`, V34/base1 `[1..11]` | 95:50 | 105:50 |

В каждом Check ожидается `<Cell<u8> as UnstableSmallSortTypeImpl>::small_sort` с `CellCmp = canonical_less_cell`. Слоты 2 и 6 ожидают ровно одну обычную подстановку `crate::slice::sort::shared::smallsort::verify::trait_model::cell_narrow_count_encoding` → `crate::slice::sort::shared::smallsort::verify::trait_model::cell_narrow_count_encoding_enabled`. У слотов 1, 3, 4 и 5 список обычных стубов пуст. Список `verified_stubs` пуст везде. Receipt сохраняет ожидаемую пару, фактические имена из stock export и разрыв A/B при расхождении. Отдельно сохраняется терминал stock, в том числе при `SUCCESS` с неверным списком. [Проверка stock](/root/kani-rev2-fallback-control-w11/ch8-cal1/results.py) · [Привязка](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_binding.py)

В обоих вариантах Cell сохраняются полный побайтовый `old`, порядок проверок и ранние возвраты, внешний frame и пять covers. Для фиксированного `pre.cell_vals[i]` обе кодировки на каждой итерации `j` добавляют индикаторы `pre.cell_vals[j] == value` и `post.cell_vals[j] == value` к соответствующим счётчикам. Любая частичная сумма лежит между 0 и `len ≤ 16`. Преобразования `u8::from` и `usize::from` дают одинаковые 0 или 1, поэтому сравнения точных кратностей совпадают на любых допустимых снимках, включая дубликаты и различающиеся кратности. Селектор — отдельная обычная функция без контракта и состояния. Она вызывается в ветке постусловия после прежних проверок и не используется в активации, компараторе или runtime. Подстановка по исходникам относится только к выбору кодировки. Check выполняет default Unstable, fallback, вставки, `CopyOnDrop` и контрактные функции. [Модель Cell](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/trait_model.rs)

Оба split-корня берут произвольный инициализированный `[u64; 8]`, вызывают настоящий fallback с `merge::lt_u64` и сохраняют проверки безопасности и пять covers, включая разные значения с равным ключом `value >> 1`. Корень порядка проверяет соседние элементы. Корень кратности фиксирует независимый полный probe до вызова и использует `probe_count_unrolled` до и после, включая младший бит. Предположения о втором свойстве отсутствуют. Исходные `u8_n08` и `u64_n08` сохраняют обе проверки и свой домен. [Split-корни](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/fallback_rev2.rs)

Ubuntu job ограничена 140 минутами. Setup с preflight до 180 с заканчивается к 45:00, измерения к 106:00, постаттестация к 108:00, финализация к 113:00 и upload к 120:00. Резерв заканчивается к 129:00, ещё 11 минут остаются в общем окне. На каждом слоте 600 с, launch headroom 10 с, номинальный RSS cap 6 GiB и резерв памяти 2 GiB. Аргументы включают `--exact --jobs=1`, прежний профиль `-Z`, `--no-assert-contracts` и OB12 только через `--cbmc-args --object-bits 12`; uninit и validity выключены. После `TIMEOUT` или `RSS_LIMIT` продолжение требует валидной телеметрии и подтверждённого reap. Receipt сохраняет argv, cfg, задачу слота, решение по caps, regular/export, первую CNF, стадии, VT, RSS группы и RSS/PSS CBMC. Диагностические ориентиры — VT 120 с и RSS 4 GiB. [Runner](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py) · [Summary](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_report.py)

## Материал для ручного разбора DFCC слота 1

После записи самостоятельного исхода Check по regular/export инспекция использует аттестованный `goto-instrument --show-goto-functions`. Подготовленный вход связывается с exact selector, выполненными `goto-cc`, `--dfcc` с `--enforce-contract`, stock `contracted_function_name` и CBMC argv. В receipt записываются SHA-256 и идентичность обычного GOTO-файла внутри приватного work слота до и после показа. Там же остаются argv и ссылки на regular/export этого слота. [Инспекция](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_inspection.py)

`native-excerpt.json` — отдельный индексируемый член артефакта. В нём сохраняются исходные строки с номерами и смещениями в байтах, заголовки и контекст вызовов `insert_object_upto` и `insert_assignable`. Метаданные включают SHA-256 и размер захвата, пропущенные участки и признаки отсечки. Полный дамп остаётся в scratch до очистки. Фрагмент служит навигацией для ручного разбора. Поле write set в receipt и summary всегда `UNKNOWN` с режимом `MANUAL_REVIEW`. Недостающий или неполный фрагмент получает отдельную причину. Regular-инвентарь с ID, статусом, текстом и `Location` сохраняется в проекции. `ensures` снова имеет статус кандидата по координате, как в batch2. Guard/frame и именованная подстановка на B по-прежнему проверяются. [Отбор строк](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_native.py) · [Regular-проекция](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_binding.py)

Подготовка и хеширование, показ GOTO и потоковое извлечение выполняются под тем же supervisor с общим дедлайном до 45 с в окне слота. Сохраняются cap 6 GiB, резерв 2 GiB, общие пределы временных stdout 64 MiB и stderr 1 MiB. Время, RSS и reap записываются отдельно от Check. Итог Check сохраняется при таймауте, отсечке и отсутствии фрагмента. В пределах 4 MiB на слот и 96 MiB на job основной receipt и regular-проекция имеют приоритет над фрагментом. Неподтверждённый reap останавливает кампанию и сохраняет scratch. При `STOCK_EXPORT_TOOL_PIN_DRIFT` подтверждённый reap разрешает очистку в остатке срока. Причина остановки и именные `NOT_STARTED` сохраняются. [Runner](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py) · [Индекс артефакта](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_report.py)

## Локальная проверка

- Std и обе замороженные части входа сохранены. Предыдущие статические проверки Std и результаты первого ревью относятся к тому же commit/tree. Шесть слотов, их argv, часы, workflow и gate сохранены.
- Полный синтетический suite `python3 -B -m unittest discover -s ch8-cal1 -q` — прошли 153 теста. Проверены исходные строки и координаты `insert_object_upto`, чужой владелец, обход `GOTO`, чужой write set, отсечки потока и извлечения, лимиты публикации, сохранение Check, reap и обе ветки очистки при pin drift.
- `git diff --check` прошёл для FIX. Точное будущее дерево принято локальным синтетическим событием push с указанным единственным parent. Старый tree, отсутствующий pin и неверный parent отклонены.
- CI, push, Cargo, rustc, Kani и CBMC не запускались. Фактический фрагмент, нативные результаты и метрики предстоит получить в разрешённой job. Привязка диапазона DFCC потребует ручного разбора материала того же Check.
