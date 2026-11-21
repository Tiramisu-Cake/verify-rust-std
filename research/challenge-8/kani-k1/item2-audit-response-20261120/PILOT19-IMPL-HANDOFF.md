# Кампания 19. Handoff matched-width N13–N19

Подготовлен локальный Control с 11 последовательными exact roots на OB11, каждый с nominal cap 6 GiB. Frozen request имеет `status=READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Пакет остаётся `RESEARCH_ONLY`. Для dispatch требуются review и отдельный GO. [Задание](PILOT19-IMPL-TASK.md) · [Native inventory](NATIVE-INVENTORY-N13-N20.md)

## Пины и SHA-256

| Объект | Commit | Tree |
| --- | --- | --- |
| Control 19 | `400b54a57cc1b1de2ebeca3060e95cf5954ec69c` | `e548edece4474ec5412c29e359b3959fa2716095` |
| Единственный parent Control 19 | `ba32286ee4f370593a2c9f0d8834a12d473c82d7` | `53b372008b70704b15a404275f81fa078ed50034` |
| База содержимого Control 17B | `628a03ef3d24ad433e977a7e3cfec003c9993292` | `26558404aa1e4a58c86ad7d3084230c60123b09b` |
| Std 17A/17B | `3fff6aa0dbab95e9889ab864e6b88596c4e452fe` | `a41b4c4822ab9df70db698ce576b3112a670ba80` |
| Tool | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |
| g0 задания | `41d0f2e379c939fca50be322cbd31f4f1bb41220` | `e55b22d6ec1753489f06eab660a8a68ae15e1d93` |
| g0 native inventory | `2547412124d253c44c97ec3e28391866f49d4cb9` | `21633f444c48aca7a16eb4cecbfb9f761e417daa` |

Control находится в `/root/kani-ch8-q-pilot-control-v19` на ветке `experiment/ch8-q-pilot-control-v19`. Дельта от 17B состоит из `ROOTS` в `run.py`, roster и хэшей payload в request, а также тестовых fixtures и проверок. Workflow и event ref `refs/heads/uninit-ci/ch8-q-pilot-v1` совпадают с 17B. Имя шага `Run seven q-pilot roots` унаследовано, фактические запуски задаёт roster. [Frozen request](/root/kani-ch8-q-pilot-control-v19/ch8-q-pilot-control/CI-REQUEST.json)

| Файл Control | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `3ead3a6a7b5065396d25e438684fcccfd1ac6243c3e1a67eb83994db4720d4dd` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `c5ae3ce6cd5ac83890539e3dd8121ffea4897d09f6a67bbf0cee967d8f18dd37` |
| `ch8-q-pilot-control/test_run.py` | `4aa65ae976f0a720ffdc76453dd56d32a49c31ec35fa3b1fdb73f8317931a410` |

| Файл std из `library/core/src/slice/sort/shared/` | SHA-256 |
| --- | --- |
| `smallsort.rs` | `bd4eb6faffe3992d26c282553b01b4008c88cfe75e820f622c40e4d50bde408a` |
| `smallsort/verify.rs` | `b4ecd70c29b636f918c0916718ed6a79349932fe1e9713911d0a0c8e3e62e210` |
| `smallsort/verify/sorting_model.rs` | `dec45747dde28e0861becf4c0c089d2a9899ad035db30e9967d0a0041845fb88` |
| `smallsort/verify/sorting_q_controls.rs` | `0ee56705b083f7610b764bc8bc164a81eae94de9229b33baf0169f6c7b8df9ff` |
| `smallsort/verify/sorting_q_model.rs` | `5e5eac5ad26d1352df52b659a12eb5396ef23872f724c1b460441eb6a37520f0` |
| `smallsort/verify/sorting_q_pilot.rs` | `ac755d455d7a0f5fbd706c90bb6bae02ffd4a4c41125db7e5fb28833da55a8b6` |
| `smallsort/verify/sorting_q_merge.rs` | `55f94471200deb46a264a8b3e8589caa8767ea6db252de0e161d01cc03cc00ce` |
| `smallsort/verify/sorting_q_merge_model.rs` | `ce43ccd53d0e0764374b1e0c87749a563b49f11c262cf6dd6ec2f41f9ac4e3fa` |

## Frozen roster

Префикс selector — `slice::sort::shared::smallsort::verify::`. Ordinary stubs и extra CBMC args пусты. Check выполняют actual тела с пустыми verified stubs. Для положительных корней ожидается native `SUCCESS` со всеми указанными covers.

| № | Root ID | Exact selector suffix | Cfg | Роль или verified stubs | Child, с | Covers |
| ---: | --- | --- | --- | --- | ---: | ---: |
| 1 | MB-MERGE-N18-OB11 | `sorting_q_merge::mb_merge_n18` | `merge_b` | Check `bidirectional_merge`, 9+9 | 600 | 6 |
| 2 | MB-MERGE-N19-OB11 | `sorting_q_merge::mb_merge_n19` | `merge_b` | Check `bidirectional_merge`, 9+10 | 600 | 6 |
| 3 | MA-INSERT-RIGHT-OB11 | `sorting_q_merge::ma_insert_right_b10_rel9` | `merge_a` | Check `insert_tail`, base10/rel9 | 600 | 7 |
| 4 | NM-INSERT-P3-OB11 | `sorting_q_pilot::p3_insert_u8_b01_rel1_16_q_any` | `no_merge_sort13` | Check q-only `insert_tail`, base1/rel1–16 | 600 | 24 |
| 5 | NM-NETWORK-N17-OB11 | `sorting_q_merge::nm_network_n17` | `no_merge_sort13` | sort13, insert_tail | 450 | 6 |
| 6 | NM-N17-QPOST-CORRUPT-OB11 | `sorting_q_merge::nm_network_n17_corrupt` | `no_merge_sort13` | sort13, insert_tail | 300 | 2 |
| 7 | NM-NETWORK-N13-OB11 | `sorting_q_merge::nm_network_n13` | `no_merge_sort13` | sort13 | 450 | 6 |
| 8 | NM-N13-QPOST-CORRUPT-OB11 | `sorting_q_merge::nm_network_n13_corrupt` | `no_merge_sort13` | sort13 | 300 | 2 |
| 9 | NM-NETWORK-N14-OB11 | `sorting_q_merge::nm_network_n14` | `no_merge_sort13` | sort13, insert_tail | 450 | 6 |
| 10 | NM-NETWORK-N15-OB11 | `sorting_q_merge::nm_network_n15` | `no_merge_sort13` | sort13, insert_tail | 450 | 6 |
| 11 | NM-NETWORK-N16-OB11 | `sorting_q_merge::nm_network_n16` | `no_merge_sort13` | sort13, insert_tail | 450 | 6 |

## Привязка по исходникам

Сверены 11/11 exact selectors, доступность по cfg guards, Check/Proof, наборы stubs и число covers в закреплённом std. Положительные fixtures используют exact `u8/KeyLess<u8>`, независимые произвольные V34 и q. Доменные предпосылки относятся к соответствующему Check. Профиль OFF сохраняет обычные memory, bounds, overflow и unwind checks. Ниже `S` — `library/core/src/slice/sort/shared/smallsort.rs`, `H` — соседний `smallsort/verify/sorting_q_merge.rs`.

- **N18/N19.** Check `H:521/548` используют `v[1..19]` и `v[1..20]`, сохраняют q и весь исходный V34, пишут в отдельный scratch32 с offset 0. Actual `merge_up/down` покрывают scratch `[0..9) + [9..18)` при N18 и `[0..9) + {9} + [10..19)` при N19. Slot 9 в N19 пишет odd copy. Normal return проходит финальный guard. Сверка с 12b `8ae4029765` и consumer pin 15 `c5dc2a415e` подтвердила совпадение активных clauses B, модели `merge_b` и тела whole merge. Сверены actual шаги и их clauses с 12b. Numeric Pre обеих половин, readable/writable/disjoint geometry, scratch assigns и q-post активны под `merge_b` и `merge_c_sort9`. Network и copy-back сверены с 15. [Роли и native anchors](NATIVE-INVENTORY-N13-N20.md#n18n19n20)
- **Правый insert N19.** Check `H:127` выполняет actual base10/rel9 с inclusive footprint `v[10..20)` и q/outside frame. Тело и активные pointer/q Pre, assigns, q-post и условный numeric post совпадают с 11 `2dc2afe895` и consumer pin 15. В общей модели добавлена wide-геометрия. При `merge_a` и `merge_c_sort9` наружный guard допускает только `len=10`, поэтому `old` читает 9, post читает 10, как у 11. [Insert и caller Pre](NATIVE-INVENTORY-N13-N20.md)
- **Зависимости 15, OB11.** У `MD-NETWORK-N18-OB11` два sort9 на `v[1..10)` и `v[10..19)` с `MD-SORT9-L1-ACT-OB11` и `MD-SORT9-R9-ACT-OB11`. У `MD-NETWORK-N19-OB11` и `MD-N19-QPOST-CORRUPT-OB11` второй sort9 получает `v[10..20)` с `MD-SORT9-R10-ACT-OB11`, сохраняя `v[19]` до вставки. Right insert есть только у N19. После whole merge обе сети выполняют actual copy-back. Исторический `MB-PRE-NUMERIC-N18` остаётся наблюдением о caller Pre в своём OB12 маршруте. [Inventory по ролям](NATIVE-INVENTORY-N13-N20.md)
- **N13–N17.** Из `S:351–373,868` и пар в `H:1675–1769` следует один Replace sort13 на `v[1..1+N)`, thin modifies `v[1..14)` и frame хвоста. Соответствующие `NM-S13-L13`…`NM-S13-L17` из 17A имеют тот же std pin и OB11, выполняют actual sort13. N13 возвращается без вставок. N14/N15/N16/N17 выполняют соответственно rel13, rel13–14, rel13–15, rel13–16. Для каждого rel P‑3 покрывает pointer geometry и q-monotone caller Pre, q order-stat post и inclusive `v[1..2+rel)` при неизменном q. P‑3 использует прежний q-only контракт и covers всех rel1–16. Positive consumer после actual network проверяет q/order-stat, q-frame и внешний frame. Исторический L17 Check достиг 7,35 GiB по сводке 17A. [Handoff 17](PILOT17-IMPL-HANDOFF.md) · [Сводка 17A](run-44896810040/SUMMARY.md)

## Endpoint controls и сверка результатов

В обоих endpoint controls q=1 и активный срез нулевой. Внешние байты произвольны. После возврата из сети cover полезного возврата проверяет `v[1] == 0`. Запись `v[1] = 255` меняет младший бит ожидаемой нулевой маски. Затем cover проверяет путь порчи. Ожидается ровно одна native `FAILURE` класса `assertion` на контроль.

| Корень | Назначенная метка и source Location | Covers | Ориентир из 17B OB12 |
| --- | --- | --- | --- |
| `NM-N17-QPOST-CORRUPT-OB11` | `NM_N17_CORRUPT_QPOST`, `H:1833:5` | `NM_N17_CORRUPT_USEFUL_RETURN`, `NM_N17_CORRUPT_PATH` | `nm_network_n17_corrupt.assertion.6`, `Check 33` |
| `NM-N13-QPOST-CORRUPT-OB11` | `NM_N13_CORRUPT_QPOST`, `H:1800:5` | `NM_N13_CORRUPT_USEFUL_RETURN`, `NM_N13_CORRUPT_PATH` | `nm_network_n13_corrupt.assertion.6`, `Check 131` |

Для офлайн-сверки использовать согласованную structured native projection `RESULTS` и `SUMMARY` с manifest и provenance. Inventory g0 содержит 30 терминальных корней и 23 331 запись свойств. Сверять exact root и invocation, pin/tree и hashes, полные native ID, class, status, location, ordinal, descriptions и coverage. Проверить S/F/U и covers по regular summary и доступным записям export. Для обоих controls заново подтвердить ID, класс, Location и два ожидаемых covers на OB11. При общем ID для повторных sort9 или вставок привязать каждое динамическое исполнение по exact lowering и пути. Совпадение source clause устанавливает роль на уровне исходника. Native binding каждого повторного исполнения остаётся открытым. [Формат projection и критерии полноты](INVENTORY-TASK.md#формат-и-проверка-полноты)

## Лимиты и локальная валидация

- CaDiCaL, `--exact --jobs=1 --no-assert-contracts`, unwind36, regular output и JSON export, отдельные Kani/Cargo target dirs. Child budget 5 250 с, setup/build до 1 800 с, финализация 540 с, job 10 800 с, запас 3 210 с. Latest start за 630/480/330 с до supervisor cutoff для child 600/450/300 с.
- Nominal local cap 6 291 456 KiB, outer 12 582 912 KiB, резерв 2 097 152 KiB. При штатном outer budget synthetic test подтвердил effective local cap 6 291 456 KiB у каждой строки. Capture 16/1/8 MiB stdout/stderr/export, aggregate 384 MiB. При запуске фиксировать nominal/effective cap, sampled child PGID в KiB, outer/component peaks, VT/child, CNF и terminal outcome либо первопричину cutoff/`NOT_RUN`. Для P‑3 на OB11 отдельно проверить capacity. Подъём RSS cap не меняет ёмкость object IDs.
- `git diff --check` прошёл относительно 17B и единственного parent. Независимая сверка request с таблицей задания подтвердила 11/11 строк по порядку, OB11, таймауты, cfg, пустые extra CBMC args и budgets. Workflow, frozen settings и `run.py` за пределами `ROOTS` совпадают с 17B побайтно.
- `validate` прошёл на чистом Control с синтетическими GitHub metadata для push, нужного ref, attempt 1 и SHA кандидата. `check-source` прошёл на чистом временном detached checkout std и существующем detached checkout tool. Проверены commits/trees и SHA-256 восьми std-файлов, с удалением временного checkout после проверки.
- `python3 -m unittest -v test_run.py` прошёл 14/14 на синтетических процессах. Проверены serial order, exact argv и профили, оба тестовых nonzero exit, 6 GiB и снижение effective cap, latest-start, limits, drift request/payload, cleanup, timeout/reap, read/setup ошибки и `NOT_RUN`.

Итог стадии — локальная готовность пакета. Native outcomes OB11, измерения RSS и proof credit открыты.
