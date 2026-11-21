# Кампания 11. Handoff пакета A для N18/N19

Подготовлены два локальных кандидата для одного setup/build и девяти последовательных корней. Request имеет статусы `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Перед запуском нужны отдельное ревью и GO. Полный merge и проверка вызывающей сети входят в пакеты B и C. [Задание Pilot 11](PILOT11-IMPL-TASK.md) · [Merge-план](MERGE-PLAN.md) · [Handoff Pilot 10](PILOT10-IMPL-HANDOFF.md)

## Идентичности кандидатов

| Объект | Worktree и ветка | Commit | Tree |
| --- | --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `2dc2afe895679773f443642685fabaab049d80bd` | `5edab97d7ee1ea95f87877a2017679c08edb3ce0` |
| Control | `/root/kani-ch8-q-pilot-control-v11`, `experiment/ch8-q-pilot-control-v11` | `e18c9d5489108e6ab036af22a53b0f50a30b1506` | `8cd7914665cfff6c8ac9997669c26582267da78d` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Единственный parent std — `632e4e8d3b8cd94c918979ac7f076afebd327c0f`, tree `439f17e9b980366910bf2d064ea8a4ecb1d76fec`. Дельта состоит из четырёх блоков Kani-only атрибутов, регистрации и двух новых модулей. Тела и сигнатуры совпадают с базой побайтно. Старые q-pilot, q-controls, `KeyLess` и модель с `CAP=17` совпадают по SHA-256.

Единственный parent control — `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Относительно v10 `6f5009f3be62aabe867be0ff27230b941c8decd2` с tree `5f5e2a6a76ae847972fa93853d7807325f73ad5f` обновлены roster, cfg, std inventory и соответствующие fixtures Python. Workflow совпадает побайтно, включая ref `refs/heads/uninit-ci/ch8-q-pilot-v1` и имя шага `Run seven q-pilot roots`. Runner читает девять корней из request. [Request кандидата](/root/kani-ch8-q-pilot-control-v11/ch8-q-pilot-control/CI-REQUEST.json)

| Control-файл | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `1ce754f9e623bed11368a64b681fe8ee3a6d92f8d75b3039297c4c48d3577a34` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `ff00d95c733d0e7c62d5cf7875d674eca95e4cdc3e73c6f158277cfa091e00e9` |
| `ch8-q-pilot-control/test_run.py` | `66d1868ccc53c3cf5dccc0361061420a0da3eb0e734f2606a7b6df1abbc47acd` |

| Std-файл относительно `library/core/src/slice/sort/shared/` | SHA-256 |
| --- | --- |
| `smallsort.rs` | `ec030f502a315489b17ee8a1744baaa50f81ee0494d2484c86e5408ea4e758b8` |
| `smallsort/verify.rs` | `b4ecd70c29b636f918c0916718ed6a79349932fe1e9713911d0a0c8e3e62e210` |
| `smallsort/verify/sorting_model.rs` | `dec45747dde28e0861becf4c0c089d2a9899ad035db30e9967d0a0041845fb88` |
| `smallsort/verify/sorting_q_controls.rs` | `0ee56705b083f7610b764bc8bc164a81eae94de9229b33baf0169f6c7b8df9ff` |
| `smallsort/verify/sorting_q_model.rs` | `5e5eac5ad26d1352df52b659a12eb5396ef23872f724c1b460441eb6a37520f0` |
| `smallsort/verify/sorting_q_pilot.rs` | `ac755d455d7a0f5fbd706c90bb6bae02ffd4a4c41125db7e5fb28833da55a8b6` |
| `smallsort/verify/sorting_q_merge.rs` | `42a8e7629ca4bfdb36b6de38373c8b9fd284224305e05f8bcd181939ba1b8820` |
| `smallsort/verify/sorting_q_merge_model.rs` | `3c6ac93147202ead891b7ada1cdb4a05b79d350a18f2f8d64756f58f4c62de32` |

## Roster и профиль

Префикс exact selectors — `slice::sort::shared::smallsort::verify::sorting_q_merge::`. Ordinary stubs везде пусты. Таблица указывает ожидаемые исходы будущего запуска.

| № | ID | Суффикс selector | Профиль и режим | Verified stubs | Child, с | Ожидаемый исход |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | MA-SWAP-BYTE-Q | `ma_swap_byte_q` | `merge_a`, Check `swap_if_less` | ∅ | 600 | SUCCESS |
| 2 | MA-INSERT-RIGHT | `ma_insert_right_b10_rel9` | `merge_a`, Check `insert_tail` | ∅ | 600 | SUCCESS |
| 3 | MA-MERGE-UP | `ma_merge_up` | `merge_a`, Check `merge_up` | ∅ | 600 | SUCCESS |
| 4 | MA-MERGE-DOWN | `ma_merge_down` | `merge_a`, Check `merge_down` | ∅ | 600 | SUCCESS |
| 5 | MA-H9-L1 | `ma_h9_left_b01` | `merge_a`, Proof | swap | 600 | SUCCESS |
| 6 | MA-H9-R10 | `ma_h9_right_b10` | `merge_a`, Proof | swap | 600 | SUCCESS |
| 7 | MA-H10-R10 | `ma_h10_right_b10` | `merge_a`, Proof | swap, insert | 600 | SUCCESS |
| 8 | MA-UP-BAD-TIE | `ma_merge_up_wrong_tie` | `merge_a_bad_tie`, Check `merge_up` | ∅ | 300 | Одна FAILURE в `merge_up_wrong_tie_cursors` |
| 9 | MA-H10-CORRUPT-ORDER | `ma_h10_right_corrupt_order` | `merge_a`, Proof | swap, insert | 300 | Одна FAILURE в `MA_R10_CORRUPT_NUMERIC_ORDER` |

- `merge_a` задаёт `--cfg=kani_smallsort_sorting --cfg=kani_smallsort_q_pilot --cfg=kani_smallsort_q_merge`. `merge_a_bad_tie` добавляет `--cfg=kani_smallsort_q_merge_bad_tie`. Старый q-controls и S2 несовместимы с профилем. Положительные корни и H10-контроль исключены из bad-tie cfg. При выключенном merge cfg действуют прежние leaf-контракты и корни.
- Профиль использует CaDiCaL по умолчанию tool pin, 12 object bits, `--exact --jobs=1 --no-assert-contracts`, unwind36, отдельные Cargo/Kani target dirs, пустые extra CBMC args. Uninit/validity и extra pointer выключены. Обычные bounds/pointer/overflow/unwinding checks включены. Loop contracts и quantifiers отсутствуют. [Выбор solver на tool pin](/root/kani-upstream-ch8-s1/kani-driver/src/call_cbmc.rs:105)
- Child budget 4 800 с, job 180 мин, setup/build до 1 800 с, финализация 540 с. Остаток при номинальных пределах составляет 3 660 с. Latest start за 630 или 330 с до supervisor cutoff. После остановки runner сохраняет lifecycle, первичную причину и `NOT_RUN` для корней, до которых очередь не дошла.
- Nominal child cap 10 GiB (10 485 760 KiB), outer 12 GiB (12 582 912 KiB), reserve 2 GiB (2 097 152 KiB). Effective cap ограничен доступным process-group budget. Пределы stdout/stderr/export составляют 16/1/8 MiB на корень, общий предел с индексом 256 MiB. Runner сохраняет actual caps, child time, component RSS, bounded stdout/stderr и native export для офлайн-сверки фаз, VT, property inventory и причин остановки. Время и RSS этих Check и probes ещё не измерены.

## Домены и привязки свойств

Корни используют независимые `[u8;34]` и `q: u8` из `kani::any()` и явные проверки `MA_BYTE_MODEL_ACTIVE` и `MA_Q_MODEL_ACTIVE` для `u8/KeyLess<u8>`. Компаратор сравнивает полные байты. Для других пар T/F специализированный посредник отключает новые чтения, в том числе внутри lifted `old`. Snapshot пары хранит значения двух байтов, numeric snapshot вставки хранит флаг порядка префикса, прежние q-снимки хранят пороговые значения и q. Step snapshot владеет двумя source bytes, исходным q и тремя значениями указателей. Pre и captures проверяют границы, no-wrap, allocation и читаемость там, где выполняется чтение. [Модель](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge_model.rs:10)

В таблице указаны якоря для сопоставления с native property IDs. При разборе нужно связать exact selector, actual target, класс свойства, native description и location на закреплённом std pin. Дублирующие harness assertions задают стабильные описания для поиска, а native ID и результат определятся после запуска. Для footprint нужны свойства DFCC `assigns` соответствующих actual writes, для probes нужны свойства `requires` каждого Replace. [Чек-лист qualification](QUALIFICATION-CHECKLIST.md)

| Check | Preconditions и DFCC footprint | Контракт и harness assertions для сопоставления |
| --- | --- | --- |
| Swap | V34, base 1 или 10, все 36 пар `0 <= a < b < 9` на каждой базе. Прежние no-wrap, same allocation, read/write. `modifies` разрешает два адресуемых байта. | `swap_byte_post` ↔ `MA_SWAP_BYTE_POST`, прежний `swap_post` ↔ `MA_SWAP_Q_POST` и `MA_SWAP_Q_FRAME`. `MA_SWAP_V34_FRAME` проверяет остальные байты. |
| Правая вставка | Литеральные begin/tail `V34+10` и `V34+19`, relative tail 9. Read/write inclusive span, same allocation, begin < tail, прежний `insert_pre` с q-монотонностью. `modifies` покрывает `v[10..20]`. | Прежний `insert_post` ↔ `MA_INSERT_Q_POST` и `MA_INSERT_Q_FRAME`. `insert_numeric_post` для len10 ↔ `MA_INSERT_NUMERIC_ORDER`, импликация из числового порядка старого префикса. `MA_INSERT_V34_FRAME` покрывает внешний V34. |
| Up | `step_pre(Up)` проверяет оба readable initialized source, writable dst, disjoint исходных байтов с dst и допустимость трёх инкрементов. `modifies(dst)` покрывает байт в текущем scratch slot. | `step_byte_post(Up)` ↔ `MA_UP_BYTE_POST`. `step_q_post(Up)` ↔ `MA_UP_Q_POST` (AND) и `MA_UP_Q_FRAME`. `merge_up_cursors` ↔ `MA_UP_CURSOR_POST`, весь V34 сверяет `MA_UP_SOURCE_FRAME`. |
| Down | `step_pre(Down)` проверяет оба readable initialized source, writable dst, disjoint исходных байтов с dst и допустимость `dst.sub(1)`. `modifies(dst)` покрывает байт в текущем scratch slot. | `step_byte_post(Down)` ↔ `MA_DOWN_BYTE_POST`. `step_q_post(Down)` ↔ `MA_DOWN_Q_POST` (OR) и `MA_DOWN_Q_FRAME`. `merge_down_cursors` ↔ `MA_DOWN_CURSOR_POST`, весь V34 сверяет `MA_DOWN_SOURCE_FRAME`. |

Якоря actual targets и harness calls. [Swap contract](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:406) · [Swap call](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:49) · [Insert contract](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:650) · [Insert call](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:92) · [Up contract](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:874) · [Down contract](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:942)

- **Swap и insert.** Covers swap подтверждают базы 1 и 10, обе ветки, равные байты на разных индексах, split q и endpoints. У insert домен сохраняет q-монотонные числовые инверсии, что проверяет отдельный cover. Covers числового префикса, раннего возврата и полного sift используют тот же литеральный span. Оба корня покрывают useful return.
- **Up и down.** Source начинается с `v[1]`, scratch — отдельный `MaybeUninit<[u8;32]>`. При `N∈{18,19}` и `0<=k<=8` Up читает `L=a`, `R=9+k-a`, пишет `D=k`, где `0<=a<=k`. Down читает `LR=8-k+d`, `RR=N-1-d`, пишет `DR=N-1-k`, где `0<=d<=k`. Отсортированность входа для шага не требуется. При `right < left` Up копирует right и продвигает R, Down копирует left и уменьшает LR. При `left <= right` Up выбирает left, Down выбирает right. Down уменьшает source через `wrapping_sub` и dst через `sub`. `MA_DOWN_DST_SUB_RANGE` проверяет `N-10..N-1`, `MA_DOWN_DST_SUB_LAST` проверяет 8 для N18 и 9 для N19 при k=8.
- **Границы scratch и курсоров.** Up пишет `scratch[0..9]`, Down пишет `scratch[9..18]` или `scratch[10..19]`. Пороговый и byte posts читают только записанный байт, `old` читает только два source bytes. Scratch frame задаёт DFCC. Курсоры только сравниваются. Covers отдельно отмечают правый Up offset 18 для N18 и N19, левый Down −1 в координатах source (`v[0]`), правый Down 8/9 и последний destination каждого направления. Новое чтение по возвращённому указателю требует caller Pre. Native credit для uninit/validity требует отдельной ON-проверки. [Actual Up call](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:190) · [Actual Down call](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:268)
- **Probes половин.** Actual `sort9_optimal` вызывается на `v[1..10]`, `v[10..19]` или `v[10..20]`. Каждый маршрут имеет 25 исходных swap call sites, включая повторяющиеся пары. H10R10 устанавливает `MA_R10_PRESORT_NUMERIC_PREFIX` и `MA_R10_PRESORT_TAIL_FRAME`, покрывает порядок перед вызовом actual `insertion_sort_shift_left(...,9,...)`, а его единственный Replace insert передаёт begin/tail 10/19. Все probes проверяют числовой порядок, `MA_HALF_ORDER_Q_POST` относительно pre-state того же span, `MA_HALF_Q_FRAME`, `MA_HALF_V34_FRAME` и шесть обычных covers. При qualification надо подтвердить native caller Pre и фактические Replace bindings для каждого из этих call sites, с учётом дедупликации property IDs. Числовой pre у actual `bidirectional_merge` остаётся задачей пакета C. [25 call sites sort9](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:511) · [Actual insertion loop](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:743) · [Маршрут H10](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:382)
- **Контроли.** `MA_UP_BAD_TIE_INPUT` стоит перед actual Up, `MA_UP_USEFUL_RETURN` после byte/q/frame проверок. В bad-tie cfg только cursor ensures требует выбрать R на равных байтах. Ожидается одна native FAILURE с описанием `merge_up_wrong_tie_cursors` и успешные byte/q/assigns/frame. H10-контроль сохраняет actual маршрут и оба Replace. При нулевом pre-span и независимом q=2 после возврата он пишет 1 и 0 в первые два байта. `MA_R10_CORRUPT_PATH` стоит после мутации и проверок q/frame, до `MA_R10_CORRUPT_NUMERIC_ORDER`. Все пороговые биты остаются нулевыми. Ожидаются ровно одна назначенная FAILURE, успешные q/frame и покрытия пути порчи и useful return. [Назначенный Up ensures](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:902) · [H10-контроль](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:418)

## Граница Replace для пакета B

Replace генерирует `kani::any_modifies` для всего возвращаемого значения и на pinned tool преобразует его в `kani::any<T: Arbitrary>`. Stock tuple требует `Arbitrary` каждого компонента, а stock реализаций для `*const T` и `*mut T` нет. `any_ptr(storage)` обслуживает autoharness и требует выделенный storage. Для `stub_verified` с кортежем `(*const T, *const T, *mut T)` в B нужна отдельная проверка применимости. В A оба merge шага и tie-control исполняют actual тела в Check без verified stubs, tool и return signatures сохранены. [Генерация Replace](/root/kani-upstream-ch8-s1/library/kani_macros/src/sysroot/contracts/replace.rs:20) · [Преобразование и проверка trait bound](/root/kani-upstream-ch8-s1/kani-compiler/src/kani_middle/transform/contracts.rs:112) · [Tuple Arbitrary](/root/kani-upstream-ch8-s1/library/kani_core/src/arbitrary.rs:552) · [Модель any_ptr](/root/kani-upstream-ch8-s1/library/kani_core/src/arbitrary.rs:174)

## Локальные проверки

- `rustfmt --edition 2024 --check` прошёл на двух новых модулях и изолированных добавленных атрибутах и регистрации. Использован локальный `rustfmt 1.12.0-nightly (65ce8611fe 2026-11-18)`. `git diff --check` прошёл. Сравнение с базой показало четыре вставки атрибутов и добавление регистрации в конец `verify.rs`, с побайтным сохранением прежних строк.
- Сверены режимы, cfg и stubs всех девяти корней, все 25 исходных пар sort9 и правая вставка. Статически перебраны 512 H9 и 1 024 H10 пороговых масок на уровне листовых сводок и 270 сочетаний геометрии/сравнения для обоих шагов вместе, включая ties и последний down `sub(1)`. Эти вычисления проверяют формулы исходников.
- `validate` с синтетическими GitHub metadata подтвердил exact control commit/tree, parent, event/ref/attempt и hash inventory. `check-source` подтвердил чистые std/tool checkout, оба commit/tree и SHA-256 всех восьми std-файлов.
- `python3 -m unittest -v test_run.py` прошёл 14 из 14 тестов с синтетическими Python-процессами. Проверены оба cfg, exact selectors и порядок, argv и 12 object bits, обе длительности и latest start, caps, target dirs, drift, cutoff, cleanup и унаследованные error paths.

Cargo, rustc, Kani, CBMC и CI не запускались. Пушей не было. Native роли, properties и применимость Replace для merge остаются открыты. Proof credit — `NONE`.
