# Кампания 18. Handoff N25, память N20 и Check sort13

Подготовлены локальные std и Control с 11 exact roots. Статус пакета `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`, `RESEARCH_ONLY`. Для dispatch требуются review и отдельный GO. Квалификация N13–N20 ведётся по отдельному заданию. [Задание 18](PILOT18-IMPL-TASK.md) · [Qualification](PILOT18-QUALIFICATION-TASK.md) · [Handoff 17](PILOT17-IMPL-HANDOFF.md)

## Пины и SHA-256

| Объект | Worktree / ветка | Commit | Tree |
| --- | --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1` · `experiment/ch8-q-pilot-v1` | `a9e7dba799a22b49f4bad3be1579c08d9e0763a3` | `78079cf6e72d4cc56f77876c4ba61e98fe689dbf` |
| Control 18 | `/root/kani-ch8-q-pilot-control-v18` · `experiment/ch8-q-pilot-control-v18` | `92dbec90b1358e58449b617d041835612c52339f` | `08f3d66bdc054ea0ad682b98846897ef49e0f53c` |
| Tool | `/root/kani-upstream-ch8-s1` · detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Единственный parent std — `3fff6aa0dbab95e9889ab864e6b88596c4e452fe`, tree `a41b4c4822ab9df70db698ce576b3112a670ba80`. Единственный parent Control — `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. База содержимого Control 17A — `cb81adc41d7bce501d8a93c4e90bb236a27b550f`, tree `647b4bf6a9c749e5983159181216565467de46a4`. Workflow сохранён побайтно, event ref — `refs/heads/uninit-ci/ch8-q-pilot-v1`. [Замороженный request](/root/kani-ch8-q-pilot-control-v18/ch8-q-pilot-control/CI-REQUEST.json)

| Файл из `library/core/src/slice/sort/shared/` | SHA-256 |
| --- | --- |
| `smallsort.rs` | `bd4eb6faffe3992d26c282553b01b4008c88cfe75e820f622c40e4d50bde408a` |
| `smallsort/verify.rs` | `b4ecd70c29b636f918c0916718ed6a79349932fe1e9713911d0a0c8e3e62e210` |
| `smallsort/verify/sorting_model.rs` | `dec45747dde28e0861becf4c0c089d2a9899ad035db30e9967d0a0041845fb88` |
| `smallsort/verify/sorting_q_controls.rs` | `0ee56705b083f7610b764bc8bc164a81eae94de9229b33baf0169f6c7b8df9ff` |
| `smallsort/verify/sorting_q_model.rs` | `5e5eac5ad26d1352df52b659a12eb5396ef23872f724c1b460441eb6a37520f0` |
| `smallsort/verify/sorting_q_pilot.rs` | `ac755d455d7a0f5fbd706c90bb6bae02ffd4a4c41125db7e5fb28833da55a8b6` |
| `smallsort/verify/sorting_q_merge.rs` | `8146e51caa53754ca2f43b52cd36c7c2233bc7399a10e40396d391228b25ac0c` |
| `smallsort/verify/sorting_q_merge_model.rs` | `d7a7fea7ac679b5adf611aee8cb714d6bec59e13b4493d610e0eacea958ffd9f` |

| Файл Control | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `ce4d59ec1a27f1cac31ff0d98460b6061af8e4c274f05c7bb10d82dfb75a47bb` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `4d7ceab7f47c0016a19324e00831a39ccecf9289c22577a669129f12b34b3fd1` |
| `ch8-q-pilot-control/test_run.py` | `c73dd4943f35a73b16135868421527e999a815440685fcc234270d5277554878` |

## Roster и ожидаемые исходы

Префикс каждого selector — `slice::sort::shared::smallsort::verify::sorting_q_merge::`. Везде пустые ordinary stubs и extra CBMC args. В строках 1–10 `merge_wide`. В строке 11 `no_merge_sort13_compact` равен `no_merge_sort13` с дополнительным `--cfg=kani_smallsort_q_compact_presort13`. Строки 8–11 выполняют Check actual тела с пустыми verified stubs. Следующие исходы относятся к штатному завершению root.

| № | ID | Суффикс selector | OB / child, с | Verified stubs или Check | Ожидание |
| ---: | --- | --- | --- | --- | --- |
| 1 | MW-NETWORK-N25-OB13 | `mw_network_n25` | 13 / 450 | sort9, sort13, insert_tail, merge | Измерение capacity, SUCCESS при завершении |
| 2 | MW-N25-QPOST-CORRUPT-OB13 | `mw_network_n25_corrupt` | 13 / 300 | sort9, sort13, insert_tail, merge | Единственный FAILURE `MW_N25_CORRUPT_QPOST` |
| 3 | COMPACT-N25-OB12 | `compact_network_n25` | 12 / 450 | sort9, sort13, insert_tail, merge | SUCCESS |
| 4 | COMPACT-N25-CORRUPT-OB12 | `compact_network_n25_corrupt` | 12 / 300 | sort9, sort13, insert_tail, merge | Единственный FAILURE `COMPACT_N25_CORRUPT_QPOST` |
| 5 | COMPACT-N20-OB12 | `compact_network_n20` | 12 / 450 | sort9, insert_tail, merge | SUCCESS |
| 6 | COMPACT-N20-CORRUPT-OB12 | `compact_network_n20_corrupt` | 12 / 300 | sort9, insert_tail, merge | Единственный FAILURE `COMPACT_N20_CORRUPT_QPOST` |
| 7 | COMPACT-N20-ACT-INSERT-OB12 | `compact_network_n20_actual_insert` | 12 / 600 | sort9, merge | SUCCESS |
| 8 | MW-INSERT-L9-OB11 | `mw_insert_left_literal_rel9` | 11 / 600 | Check insert_tail, base1/rel9 | SUCCESS |
| 9 | MW-INSERT-L10-OB11 | `mw_insert_left_literal_rel10` | 11 / 600 | Check insert_tail, base1/rel10 | SUCCESS |
| 10 | MW-INSERT-L11-OB11 | `mw_insert_left_literal_rel11` | 11 / 600 | Check insert_tail, base1/rel11 | SUCCESS |
| 11 | NM-S13-L17-COMPACT-OB11 | `nm_sort13_left_len17` | 11 / 1200 | Check sort13, `v[1..18]` | SUCCESS |

## Геометрия и эквивалентность

- Существующие harnesses сохранены побайтно, включая строки исходника двух повторов N25 и selector L17. Дельта std состоит из новых fixtures в `sorting_q_merge.rs` и двух блоков `all(no_merge_sort13, compact_presort13)` / `PREFIX == 13` в `sorting_q_merge_model.rs`. Исключение этих двух блоков восстанавливает модель базы побайтно. При `merge_wide` доступны прежние reachable bodies, guards и clauses N25. При legacy `no_merge_sort13` действует прежний observer. [Базовый consumer](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1574) · [Observer](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge_model.rs:504)
- Неповреждённые compact-конфигурации по-прежнему получают произвольные V34 и q, захватывают тот же активный target через `merge_wide::merge_capture` и вызывают actual `small_sort_network` на `v[1..21]` или `v[1..26]`. Frame хранит левый байт и правый tail из 13 или 8 байтов. Это те же внешние индексы, что у `outside_span_unchanged`. Индексный проход складывает дизъюнкции `byte < q`, `byte >= q` и `prev == byte`, а также конъюнкцию `byte != q`. Инициализация берёт первый активный байт, цикл перебирает остальные байты и каждую соседнюю пару ровно один раз. Так получаются прежние mixed threshold, ties и q absent, а q zero/max вычисляются из того же q. Все шесть covers, включая useful return, стоят после actual возврата, как и q-mask, q-frame и outside frame. [Compact harness](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1874)
- N20 делится на `v[1..11]` и `v[11..21]`, два sort9 и по одной вставке rel9. N25 делится на `v[1..13]` и `v[13..26]`, sort9 слева, sort13 справа, слева вставки rel9–11, справа нулевой цикл. Во всех маршрутах whole merge принимает активный span и отдельный scratch32 с offset 0. Actual network сохраняет split, insertion loop и copy-back. В каждом Replace активен прежний native caller Pre, включая numeric order обеих половин у merge. В строке 7 две вставки исполняют actual sift с обычными memory/bounds/overflow/unwind checks. [Network и scratch](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:335) · [Numeric Pre](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:1244)
- Три literal Check используют base1, абсолютные tail 10/11/12 и inclusive длины 10/11/12. V34 и q произвольные. Check прежнего wide контракта сохраняет q-монотонный Pre, q-post, условный numeric post, inclusive assigns и frame. Прежние семь общих covers включают numeric и q-only предпосылки, early return, full sift, q=0/max и useful return. Восьмой cover привязывает точный rel к конкретному root. [Literal Check](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1837) · [Frame и covers](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1301)
- L17 сохраняет `v[1..18]`, 45 actual swaps, thin modifies `v[1..14]`, q-frame, полный внешний frame `v[..1]` и `v[14..]` и семь covers. `presort_prefix` и `presort_geometry` оставляют тот же exact тип, guards на длину, read/write и размер префикса 13. После `k` итераций capture счётчик равен сумме `u8::from(byte < q)` по первым `k` байтам и лежит в `0..=k`. При `k=13` результат совпадает с filter/count, прибавление в `u8` безопасно. Post сначала сравнивает q, затем в одном проходе считает те же 13 индикаторов и проверяет все пары `(i-1,i)` при `i=1..12`. Любая инверсия даёт false, как и прежний `numeric_order`. При отсутствии инверсии тот же count и q определяют ту же threshold mask. Оставлен прежний owned `Option<PrefixSnapshot>` с `Clone + Copy` в одном `old` и одном `ensures`. Узкий аккумулятор расширяется при записи снимка и при финальном сравнении, поэтому layout снимка и реализация для ширины 9 сохраняются. [L17 selector](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1767) · [Контракт и swaps](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:624) · [Новый observer](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge_model.rs:504)

## Контроли и зависимости

| Строка | Единственное ожидаемое свойство класса `assertion` в FAILURE | Ожидаемые достижимые covers |
| ---: | --- | --- |
| 2 | `MW_N25_CORRUPT_QPOST` [assert](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1621) | `MW_N25_CORRUPT_USEFUL_RETURN`, `MW_N25_CORRUPT_PATH` |
| 4 | `COMPACT_N25_CORRUPT_QPOST` [assert](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1982) | `COMPACT_N25_CORRUPT_USEFUL_RETURN`, `COMPACT_N25_CORRUPT_PATH` |
| 6 | `COMPACT_N20_CORRUPT_QPOST` [assert](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:2024) | `COMPACT_N20_CORRUPT_USEFUL_RETURN`, `COMPACT_N20_CORRUPT_PATH` |

Для всех контролей q=1, активный вход заполнен нулями и внешние байты произвольны. После copy-back нулевая threshold mask влечёт `v[1] == 0` в байтовом домене. Запись `255` делает достижимым второй cover и меняет младший бит маски. Ожидаются успешные capture valid, q и outside frame, все caller Pre и обычные safety checks. Привязка полных native ID с ordinal, класса и экспортированного location к трём указанным assert требует результатов запуска.

| Consumer и контроль | Провайдеры для точных call sites |
| --- | --- |
| N25, строки 1–4 | Pilot 16 OB11 `MW-S9-L12` на base1/len12, `MW-S13-R13` на base13/len13, `MW-MERGE-N25` на split 12+13 с odd copy. Строки 8–10 дают exact Check трёх левых вставок. Исторический grouped Check 17A OB12 — прежний источник для rel9–11. |
| N20, строки 5–6 | Pilot 16 OB11 `MW-S9-L10`, `MW-S9-R10` на base1/11 len10, `MW-INSERT-R` на base11/rel9 и `MW-MERGE-N20` на split 10+10. Строка 8 даёт exact Check левой вставки. |
| N20 actual insert, строка 7 | Те же два Check sort9 и Check whole merge. Две вставки actual, их Check не входит в зависимость. При выборе маршрута для допуска нужен matched контроль с теми же stubs. |
| Check L17, строка 11 | Самостоятельный Check, без провайдеров. Связь с потребителями Pilot 17B зависит от сверки observer, профиля и width. |

Исторические результаты провайдеров — исходные claims из сводок. Для смешанных рёбер сверить точные clauses и native binding обеих сторон, домен и frame, provenance V34/scratch32, signed offsets, one-past, merge sentinels, pointer casts/comparisons/overflow и havoc. На x86_64 OB11/12/13 дают split 11+53/12+52/13+51. Успешная capacity и fit каждого корня проверяются по отдельности. [Провайдеры Pilot 16](run-44890498157/SUMMARY.md) · [Критерии смешанных рёбер](PILOT18-QUALIFICATION-TASK.md#решение-по-смешанным-object-bits)

## Лимиты, измерения и preflight

CaDiCaL по умолчанию закреплённого tool, профиль OFF, `--exact --jobs=1 --no-assert-contracts`, unwind36 и отдельные target dirs. Job 10 800 с, setup/build до 1 800 с, финализация 540 с, сумма child timeout 5 850 с, остаток 2 610 с. Последний старт за 330/480/630/1 230 с до supervisor cutoff для child 300/450/600/1 200 с соответственно. Local cap 10 485 760 KiB, outer 12 582 912 KiB, reserve 2 097 152 KiB и штатный effective cap. Capture 16/1/8 MiB на stdout/stderr/export, aggregate 384 MiB. Сбор bounded observations и cleanup сохранены.

При запуске фиксировать phase capacity/CNF/solve, native inventory и U, nominal/effective, sampled child PGID, отдельно outer и component RSS, VT/child и все причины cutoff. Для завершившихся корней отмечать fit ≤6 291 456 KiB по sampled child PGID. Сравнить 1–2 с exact повторами 17A OB12, 3–4 с той же парой 17A OB12, 5 с N20 на 8,65 GiB из 17A, 7 с 5, 11 с L17 на 7,35 GiB и 25,5 млн дизъюнктов из 17A. Literal Check сравнить с grouped L 17A OB12 (7,12 GiB) и right rel9 из 16 OB11 (3,30 GiB). [Сводка 17A](run-44896810040/SUMMARY.md) · [Сводка 16](run-44890498157/SUMMARY.md)

- Статическая сверка подтвердила побайтное сохранение прежних fixtures, модели с отключёнными cfg-блоками и runtime/контрактных атрибутов. Сверены 45 swaps, геометрии, исходные covers, форма контракта с `old`, q/frame и точные source anchors трёх контролей.
- Check-only `rustfmt 1.11.0-nightly (7189d39d9c 2026-10-22)` с `--edition 2024 --config skip_children=true,use_small_heuristics=Max --unstable-features` прошёл на затронутых блоках. Полные файлы дали те же 30 и 4 замечания, что и база, с одинаковым содержимым всех замечаний. `git diff --check` прошёл для std и Control.
- `validate` с синтетическими GitHub metadata подтвердил clean Control, sole parent, event ref, workflow и payload SHA-256. `check-source` подтвердил чистые закреплённые std/tool, их commits/trees и восемь std SHA-256. Сопоставление запроса с таблицей задания подтвердило порядок, exact selectors, source Check/Replace, cfg и бюджеты.
- `python3 -m unittest -v test_run.py` прошёл 15/15 с синтетическими Python-процессами. Проверены bits 11/12/13, четыре окна latest start, argv, раздельные target dirs, nominal/effective RSS, capture, cleanup, cfg/timeout/hash drift, timeout и error paths. Тесты сохраняют original exit, частичный или отсутствующий export, неправильный тип и явный `NOT_RUN`.

Стадия завершена локальным handoff. Компиляция, native inventory, resource fit и proof credit остаются открытыми до запуска. Push, CI и изменение триггера в этой стадии отсутствовали.
