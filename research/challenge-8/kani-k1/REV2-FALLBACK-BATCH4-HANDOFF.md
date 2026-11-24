# REV2 fallback · четвёртый диагностический пакет

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`. После Round 3 исправлен порядок применения лимитов публикации. Следующий этап — независимое diff-ревью исправления и отдельный GO. [Round 3](REV2-FALLBACK-BATCH4-REVIEW.md#round-3--control-после-round-2) · [Round 2](REV2-FALLBACK-BATCH4-REVIEW.md#round-2--fix1-control) · [Задание FIX1](REV2-FALLBACK-BATCH4-FIX1-TASK.md) · [Задание batch4](REV2-FALLBACK-BATCH4-TASK.md)

## Коммиты и замороженные входы

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Std overlay | `2130533d334d18919f39e03a80642ff2be6eea62` | `d1c3b7a820b7818864181146226c48f88203711a` | `7419ecfa6a2acea1adf1f98d3de5a253d8d716b3` |
| Control после Round 3 | `efcee7470a89d29e4da964a012856ba01318bb36` | `7c0be30d76e0b0ec61f17aa8745e3034929f51de` | `638f25c7e3b04490c60147507ca8fe8f4f6fab6b` |
| Будущий trigger | Формируется после GO | `7c0be30d76e0b0ec61f17aa8745e3034929f51de` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Std — worktree `/root/verify-rust-std-rev2-fallback-w11`, ветка `work/rev2-fallback-w11`. Control — worktree `/root/kani-rev2-fallback-control-w11`, ветка `work/rev2-fallback-control-w11`. Handoff фиксируется поверх g0 `9a9e8fdd9b231d2f777fc83c31aa50af9c746115`. [Std overlay](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/fallback_rev2.rs) · [Control runner](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py)

```bash
git -C /root/verify-rust-std-rev2-fallback-w11 diff 7419ecfa6a2acea1adf1f98d3de5a253d8d716b3 2130533d334d18919f39e03a80642ff2be6eea62
git -C /root/kani-rev2-fallback-control-w11 diff 638f25c7e3b04490c60147507ca8fe8f4f6fab6b efcee7470a89d29e4da964a012856ba01318bb36
git -C /root/kani-rev2-fallback-control-w11 diff 467af9cb8dba0e3be78a8d7d07672a1943c4806b 7c0be30d76e0b0ec61f17aa8745e3034929f51de
```

| Вход | SHA-256 |
| --- | --- |
| `ch8-cal1/FALLBACK-REQUEST.json` | `17f8def71e172b698aefe80eb397ca64dd20e80d53755d0b6caf799caf3e7e62` |
| `ch8-cal1/fallback-overlay.bundle` | `1fa35064730bbae033593303189e6990d893c6257e53858c1dd98dc0679775a2` |

| Цепочка std | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Shallow base | `dab03cf510df5c35141cde49f1368b1242f5035e` | `7fd542ad59723ff2beeacb9632fb0568e81b0655` | `1d2706e31f0cd909bd784fa43adf9a1d55be8469` |
| Intermediate | `dfdc70f8ccce6365f88fa489968508fa326ec60f` | `9f967855a6e6b71a7f81ecbc81e45a4d388443aa` | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| Batch 2 | `fb82da3c788c0e705cd598abee723200c0f28c42` | `4329b593bdb0d4f3972452648396170f94adea8e` | `dfdc70f8ccce6365f88fa489968508fa326ec60f` |
| Batch 3 | `7419ecfa6a2acea1adf1f98d3de5a253d8d716b3` | `44c21cb5518ed210910c3799f263e414891b08b2` | `fb82da3c788c0e705cd598abee723200c0f28c42` |
| Batch 4 | `2130533d334d18919f39e03a80642ff2be6eea62` | `d1c3b7a820b7818864181146226c48f88203711a` | `7419ecfa6a2acea1adf1f98d3de5a253d8d716b3` |

Bundle рекламирует только новый overlay как `HEAD`. Импорт в свежий detached shallow checkout базы сохраняет checkout HEAD и refs. Валидатор сверяет все пять деревьев и четыре перехода с единственным parent. Stock Kani закреплён на `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`, CBMC на версии `6.11.0`. Перед разрешённым push координатор закрепляет `CH8_REV2_FALLBACK_TRIGGER_TREE`. Gate принимает attempt 1 события push в `refs/heads/uninit-ci/ch8-q-pilot-v1` репозитория `Tiramisu-Cake/kani`. [Замороженный request](/root/kani-rev2-fallback-control-w11/ch8-cal1/FALLBACK-REQUEST.json) · [Валидатор](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_request.py)

## Roster и ожидаемые свойства

Префикс всех exact selectors — `slice::sort::shared::smallsort::verify::fallback_rev2::`. Единственный cfg-on discovery ожидает 38 точных регистраций, 14 Check и 24 Original, каждую ровно один раз.

| Слот | Суффикс | Роль | Unwind | Ожидаемое свидетельство | Latest start | Конец окна при latest start |
| ---: | --- | --- | ---: | --- | ---: | ---: |
| 1 | `cell_unstable_n08` | Check | 36 | `VERIFIED`, активная модель, контракт и внешний frame для V34/base1 `[1..9]`, счётчик `usize`, 5/5 covers и фрагмент GOTO | 45:00 | 55:00 |
| 2 | `u64_n08_counts_typed` | Original | 34 | `VERIFIED`, `REV2_TYPED_PROBE_FULL_COUNTS` со статусом `SUCCESS`, 5/5 covers | 55:10 | 65:10 |
| 3 | `u64_n08_counts_typed_corrupt_lsb` | Original | 34 | `FAILED`, единственная `FAILURE` у `REV2_TYPED_PROBE_FULL_COUNTS`, 5/5 covers, успешные достигнутые safety и unwind | 65:20 | 75:20 |
| 4 | `u8_n09` | Original | 34 | `VERIFIED`, порядок и полные кратности в `merge::assert_sorted_and_probe_preserved::<…, 9>` на `merge.rs:348:9` и `merge.rs:350:5`, 5/5 covers | 75:30 | 85:30 |

Оба typed-корня используют один harness с произвольным инициализированным `[u64; 8]` целиком на base0. Независимый скалярный `u64` probe фиксируется перед вызовом реального `small_sort_fallback` с опубликованным `merge::lt_u64` по `value >> 1`. Один и тот же probe сравнивается с полными `u64` до и после, частичные суммы `usize` лежат в `0..=8`. Для `u64` без padding равенство полных слов эквивалентно прежнему побайтовому представлению. Равенство точных кратностей для каждого произвольного probe устанавливает равенство мультимножеств. В matched-контроле единственная дельта — `active[0] ^= 1` после fallback. Она меняет одно полное значение и сохраняет ключ и длину. Общий `kani::assert` находится на `fallback_rev2.rs:219:5` в `u64_n08_counts_typed_impl::<false>` или `::<true>`. [Harness](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/fallback_rev2.rs:195)

У четырёх слотов общие covers для отсортированного и строго убывающего входа, дубликатов и полезного возврата. Пятый cover — активация модели у Check и разные значения с равным ключом у Original. Списки обычных и verified stubs пусты у всех четырёх. Слот 1 использует `CellCmp = canonical_less_cell` и default `UnstableSmallSortTypeImpl::small_sort`. Его receipt держит regular ID активации, внешнего frame и кандидата `ensures`, найденного по исходной координате.

Для контроля сохраняются отдельно технический исход и совпадение ожидания. Приёмка требует точного селектора, `VERIFICATION:- FAILED`, stock `COMPLETED/FAILURE`, exit 1 и подтверждённого reap. Полный инвентарь должен согласоваться между regular и export по агрегатам, отказавшим и недостижимым ID и удовлетворённым covers. Ровно один отказ должен принадлежать мономорфизации `::<true>` на закреплённой координате, с одинаковыми ID и метаданными обоих источников. `SUMMARY.json` содержит отдельную запись контроля. Отсечка, лишний или чужой отказ и неожиданный результат оставляют `expectation_matches=false`. Принятый ожидаемый `FAILED` позволяет продолжить измерения и характеризует чувствительность oracle. [Сверка regular/export](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_projection.py)

FIX1 требует stock `failure_kind` со значением `PANICS_ONLY` или `OTHER`, отсутствие диагностики ошибки анализа в regular и согласованную singleton summary по вердикту, checks и covers. При `failure_kind=ERROR` с согласованными терминалами receipt и summary сохраняют фактический `FAILED` и `expectation_matches=false`. Причина отказа в приёмке указана в receipt. [Приёмка LSB-контроля](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_projection.py)

## Профиль и часы

Одна Ubuntu 24.04 job с верхней границей 140 минут. Setup занимает до 45:00 от epoch, включая один preflight с лимитом 180 с и один cfg-on discovery. Четыре окна по 600 с и четыре интервала по 10 с дают границу измерений 85:40. Пост-аттестация заканчивается к 87:40, финализация к 92:40 и upload к 99:40. Девятиминутный резерв заканчивается к 108:40, остаток до job cap — 31:20. Внутри каждого окна 5 с оставлены для записи receipt.

Во всех слотах `--exact --jobs=1`, `--no-assert-contracts`, OB12 только через `--cbmc-args --object-bits 12`, прежний набор `-Z`, uninit и validity выключены. Номинальный cap — 6 GiB, резерв — 2 GiB. Cwd, оба target, export и tmp изолированы по слоту. `TIMEOUT` или `RSS_LIMIT` при валидной телеметрии и подтверждённом reap сохраняют последующие слоты. Receipt хранит исходы regular/export и их хеши, pins, argv, cfg, первую CNF, стадии, VT/wall, RSS группы и RSS/PSS CBMC. A/B в summary использует базу `u64_n08_counts` из run `45387382477`, VT 480,10 с на том же профиле. Ориентиры 120 с VT и 4 GiB остаются диагностическими. [Workflow](/root/kani-rev2-fallback-control-w11/.github/workflows/ch8-q-pilot.yml) · [База A/B](REV2-FALLBACK-BATCH3-ANALYSIS.md#примитивы-n8-и-стоимость-кратностей)

## Материал GOTO для Cell N8

Инспекция только в слоте 1 после записи обычного исхода Check. Receipt связывает точные команды `goto-cc` → `--dfcc … --enforce-contract` → CBMC с тем же подготовленным GOTO и ссылками на regular/export. SHA-256, размер и файловая идентичность GOTO сверяются до и после read-only `goto-instrument --show-goto-functions`. [Инспекция](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_inspection.py)

`native-excerpt.json` содержит целые блоки от заголовка до `END_FUNCTION`. Приоритет у exact root, Cell default dispatcher, зарегистрированной Check closure, enforced wrapper и `contract::<checked_symbol>::assigns`. Используются реальные имена из команд и заголовков, а для выбора Check closure — строка вызова точного wrapper. Сохраняются исходные строки, их байтовые интервалы, полный текст инструкций, `GOTO`, аргументы и `insert_object_upto`. Пропуск, неоднозначность, усечение или лимит записываются по блоку. Write set в receipt и summary остаётся `UNKNOWN` в режиме `MANUAL_REVIEW`. [Отбор блоков](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_native.py)

Подготовка, показ и потоковый отбор вместе используют до 45 с в остатке слота под тем же supervisor. Временные caps — 64 MiB stdout и 1 MiB stderr, сериализованный фрагмент — до 1 MiB, слот — 4 MiB, job — 96 MiB. Receipt и regular/export имеют приоритет. Полный дамп остаётся в приватном scratch до очистки. Wall и RSS инспекции записываются отдельно. Пробел сохраняет исход Check, а неподтверждённый reap останавливает кампанию и оставляет scratch по правилам FIX.

При дедлайне первого прохода receipt ставит `FUNCTION_BLOCK_DEADLINE` для закрытых, но ещё не перечитанных блоков, текущего блока и ролей из непрочитанного хвоста. При дедлайне повторного чтения уже собранные целые блоки сохраняются. `FUNCTION_HEADER_NOT_FOUND` используется после полного сканирования. [Причины пропусков](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_native.py) · [Receipt инспекции](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_inspection.py)

При отказе инспекции или публикации `function_block_gaps` перечисляет причины для всех неопубликованных ролей. Если supervisor одновременно сообщает `primary_stop_reason=TIMEOUT` и `stop_reason=REAP_UNVERIFIED`, все пять ролей получают `FUNCTION_BLOCK_DEADLINE`. Check остаётся `VERIFIED`, scratch сохраняется, кампания завершается с `PROCESS_CLEANUP_COULD_NOT_BE_VERIFIED` и тремя именными `NOT_STARTED`. [Receipt инспекции](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_inspection.py)

`function_block_gaps` хранит до пяти записей, по одной на роль, с именем блока и кодом причины длиной до 64 ASCII-символов. Перед применением cap к основной проекции финализатор освобождает место за счёт диагностики GOTO. Если список причин не помещается, receipt сохраняет `GOTO_TRUNCATED` и `gaps_omitted`, а основная regular/export-проекция сохраняет свойства, covers, VT, CNF и unwind. [Причины пропусков](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_inspection.py) · [Финализатор](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_report.py)

## Локальная проверка

- Std сохранён на проверенном overlay `2130533d33`, request и bundle сверены побайтно с базой control.
- `python3 -B -m unittest discover -s ch8-cal1 -q` — 169 тестов прошли. Регрессия воспроизвела удаление основной проекции на базе `638f25c7e3` при запасе 150 байт и при точных 4 MiB. После исправления оба случая сохраняют SHA-256 проекции, `expectation_matches=true`, поля исхода и `GOTO_TRUNCATED` с `gaps_omitted=5`. Тест Round 2 по-прежнему проверяет пять причин таймаута, три `NOT_STARTED` и сохранность scratch.
- Точное будущее дерево прошло gate с синтетическим push и указанным единственным parent. Старый и пустой tree pin отклонены. Suite проверил также другой event, attempt 2, чужие SHA/ref/repository и неверные родители. PyYAML и `bash -n` прошли для workflow из будущего дерева и всех шести shell-шагов. `git diff --check` прошёл для текущего исправления и будущего дерева относительно trigger parent.
- CI, push, Cargo, rustc, Kani, CBMC и нативный инспектор не запускались. Результаты измерений и материал для ручной привязки DFCC появятся в разрешённой job.
