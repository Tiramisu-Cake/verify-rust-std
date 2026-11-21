# Кампания 12. Handoff пакета B

Подготовлены локальные std и control кандидаты для одного setup/build и четырёх последовательных корней. Request имеет статусы `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Для запуска требуются отдельное ревью и GO. [Задание Pilot 12](PILOT12-IMPL-TASK.md) · [Merge-план](MERGE-PLAN.md) · [Handoff Pilot 11](PILOT11-IMPL-HANDOFF.md)

## Идентичности

| Объект | Worktree и ветка | Commit | Tree |
| --- | --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `4707a7354a2f3240493d030dfae7d618706f8a1a` | `226dc00ff58fb8d3b16bd13214413692a1e407e7` |
| Control | `/root/kani-ch8-q-pilot-control-v12`, `experiment/ch8-q-pilot-control-v12` | `7ad0c3d567c33215a806809799db315ad2a55eb9` | `85379c97b808733c4070e33d9a7a8f49ce9bba03` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

У std единственный parent `2dc2afe895679773f443642685fabaab049d80bd` с tree `5edab97d7ee1ea95f87877a2017679c08edb3ce0`. Дельта содержит один блок Kani-only атрибутов у actual `bidirectional_merge` и дополнения в двух verification-модулях. Сигнатуры и тела runtime std совпадают с базой побайтно. Старые A-clauses, A roots, оба прежних H10 и q-модель с `CAP=17` сохранены.

У control единственный parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. База для содержимого — v11 `e18c9d5489108e6ab036af22a53b0f50a30b1506` с tree `8cd7914665cfff6c8ac9997669c26582267da78d`. Обновлены roster, cfg, pins и хэши std, Python fixtures. Workflow совпадает с v11 побайтно и сохраняет event ref `refs/heads/uninit-ci/ch8-q-pilot-v1`. Логика сбора и ограничения raw runner совпадают с v11. [Request кандидата](/root/kani-ch8-q-pilot-control-v12/ch8-q-pilot-control/CI-REQUEST.json)

| Control-файл | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `534253a00942de505497a1e5a43ece23ac0c3354f6547f760f15b49007f0d3ac` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `ca13da90c7eb1103ae7bb1c57d95e7fd4b0ca05be304ec0744f7f173c90bc81d` |
| `ch8-q-pilot-control/test_run.py` | `883aa79309b92f7c6a9da0c57f2b5e78470e3f2151bfbe206376c77a606b217b` |

| Std-файл относительно `library/core/src/slice/sort/shared/` | SHA-256 |
| --- | --- |
| `smallsort.rs` | `9adbedd4ee038ea711f9c82546b6080578adcee27a0617d304bd2453b737f8d4` |
| `smallsort/verify.rs` | `b4ecd70c29b636f918c0916718ed6a79349932fe1e9713911d0a0c8e3e62e210` |
| `smallsort/verify/sorting_model.rs` | `dec45747dde28e0861becf4c0c089d2a9899ad035db30e9967d0a0041845fb88` |
| `smallsort/verify/sorting_q_controls.rs` | `0ee56705b083f7610b764bc8bc164a81eae94de9229b33baf0169f6c7b8df9ff` |
| `smallsort/verify/sorting_q_model.rs` | `5e5eac5ad26d1352df52b659a12eb5396ef23872f724c1b460441eb6a37520f0` |
| `smallsort/verify/sorting_q_pilot.rs` | `ac755d455d7a0f5fbd706c90bb6bae02ffd4a4c41125db7e5fb28833da55a8b6` |
| `smallsort/verify/sorting_q_merge.rs` | `2db8ce8ca6c338e0fea68c51d3e1bf58f371b296e0c9226bfee35e9a060307e7` |
| `smallsort/verify/sorting_q_merge_model.rs` | `ee0167764ee75f0bb810a5a9653bb1d9f28e7c944a988f3e7a57c4fbf3b97fb7` |

## Roster и профиль

Префикс exact selectors — `slice::sort::shared::smallsort::verify::sorting_q_merge::`. Ordinary stubs пусты у всех корней. Статусы в таблице описывают ожидаемый результат будущего прогона.

| № | ID | Суффикс | Cfg и режим | Verified stubs | Child, с | Ожидание |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | MB-MERGE-N18 | `mb_merge_n18` | `merge_b`, Check `bidirectional_merge` | ∅ | 600 | SUCCESS |
| 2 | MB-MERGE-N19 | `mb_merge_n19` | `merge_b`, Check `bidirectional_merge` | ∅ | 600 | SUCCESS |
| 3 | MB-PRE-NUMERIC-N18 | `mb_pre_numeric_n18` | `merge_b`, Proof | `bidirectional_merge` | 300 | Одна FAILURE у caller `merge_halves_numeric_order` |
| 4 | MB-H10-CORRUPT-LITERAL | `mb_h10_corrupt_literal` | `merge_a`, Proof | `swap_if_less`, `insert_tail` | 300 | Одна FAILURE `MB_H10_LITERAL_CORRUPT_NUMERIC_ORDER` |

- `merge_a` задаёт `--cfg=kani_smallsort_sorting --cfg=kani_smallsort_q_pilot --cfg=kani_smallsort_q_merge`. `merge_b` добавляет `--cfg=kani_smallsort_q_merge_b`. B-атрибуты и корни исключают S2, q-mutant и bad-tie. ByteModel активирует B-контракт для точной пары `u8/KeyLess<u8>`. H10 literal выбирается в `merge_a`.
- Сохранены CaDiCaL, 12 object bits, `--exact --jobs=1 --no-assert-contracts`, unwind36, отдельные target dirs и пустые extra CBMC args. OFF оставляет обычные memory, bounds, overflow и unwind checks. Для native uninit/validity нужна отдельная ON-проверка.
- Child budget 1 800 с, job 180 мин, setup/build до 1 800 с, финализация 540 с. Latest start за 630 или 330 с до supervisor cutoff. Nominal local cap 10 GiB, outer 12 GiB, резерв 2 GiB. Effective RSS ограничен доступным process-group budget. Capture caps составляют 16/1/8 MiB для stdout/stderr/export, общий cap 256 MiB. Унаследованы cleanup, component RSS, lifecycle, caps, длительность child и bounded capture для сверки фаз, первой CNF, VT, terminal inventory и первопричины остановки. Cutoff оставляет обязательство открытым.

## Контракт и привязка к actual merge

Пакет B исполняет actual `merge_up` и `merge_down` в обоих Check. Это отклонение от Replace шагов в Merge-плане. На tool pin генератор создаёт весь return через `any_modifies`, который transform заменяет на `any<T: Arbitrary>`. Возврат шагов имеет тип `(*const T, *const T, *mut T)`. Tuple требует `Arbitrary` для каждого компонента, а stock raw pointers этого trait не реализуют. `any_ptr(storage)` использует отдельную модель autoharness и не задаёт return, связанный с provenance аргументов этих шагов. Результаты Check из A служат для сверки ролей и границ. Для контроля caller Pre whole-merge Replace подходит unit return. Допуск whole-merge summary для потребителя требует успешной квалификации на той же геометрии. [Генератор Replace](/root/kani-upstream-ch8-s1/library/kani_macros/src/sysroot/contracts/replace.rs:19) · [Проверка trait bound](/root/kani-upstream-ch8-s1/kani-compiler/src/kani_middle/transform/contracts.rs:191) · [Unit и tuple Arbitrary](/root/kani-upstream-ch8-s1/library/kani_core/src/arbitrary.rs:63) · [Tuple bound](/root/kani-upstream-ch8-s1/library/kani_core/src/arbitrary.rs:552)

- **Домен.** Корни Check передают литеральные `&v[1..19]` и `&v[1..20]` с произвольным инициализированным V34, независимым `q:any<u8>` и отдельным `MaybeUninit<[u8;32]>` с dst +0. `merge_geometry` проверяет длину, читаемый source, writable dst и непересечение. Отдельный `merge_halves_numeric_order` задаёт полный числовой порядок внутри обеих половин, split после девятого байта. Предикат возвращает false на неподдерживаемой длине активной пары без индексации. У неактивных T/F модель пропускает проверки и capture возвращает `None` без чтений. [Атрибуты](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:1029) · [Модель merge B](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge_model.rs:283)
- **Записи и guard.** Actual цикл выполняет девять пар вызовов. В каждой паре оба шага реально вызывают `copy_nonoverlapping(..., 1)`. От исходных адресов dst +0 и dst +(N−1) up безусловно делает `add(1)`, down делает `sub(1)`. Поэтому up пишет offsets 0..8, down пишет 9..17 для N18 либо 10..18 для N19. При N19 ветка `!len.is_multiple_of(2)` всегда выполняется и её actual copy пишет offset 9 перед финальным guard. Guard сверяет `left/left_end` и `right/right_end` с исходной wrapping-арифметикой. Путь `panic_on_ord_violation` остаётся в actual графе. На normal return завершены все девять пар, при N19 также odd copy, и guard пройден. Полное покрытие следует из этих записей и адресного движения. Единственный `modifies(dst[0..N])` задаёт допустимый диапазон DFCC. Сопоставлять native `assigns` с actual stores. [Up и Down](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:877) · [Цикл, odd copy и guard](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:1107)
- **Пост и покрытия.** `merge_capture` читает только source и сохраняет q, N и маску `(1 << N) - (1 << count(source < q))`. Отдельный oracle работает до N19. `merge_q_post` после actual возврата сравнивает все N пороговых битов dst с этой маской и проверяет q. Harness также проверяет q-frame и весь V34. Old dst, хвост scratch и типизированный `[u8;32]` не читаются. Covers стоят после возврата и отмечают q endpoints, смешанные пороговые биты, равные первые байты половин и отсутствие q. `MB_MERGE_N19_ODD_USEFUL_RETURN` привязан к литеральной N19 ветке. Проверять native `merge_q_post`, `MB_MERGE_Q_FRAME`, `MB_MERGE_V34_SOURCE_FRAME`, safety, unwind, assigns и covers по каждому exact selector. [N18](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:480) · [N19](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:507) · [Capture и post](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge_model.rs:335)

## Контроли

- **Numeric Pre N18.** Отдельный valid writable scratch и `&v[1..19]` с `[1, 0 × 16, 1]` при q=2. До вызова covers подтверждают witness, q-монотонность обеих половин и левую numeric inversion. Plain proof вызывает verified Replace целого `bidirectional_merge`. Необходимы достижимые pre-call covers, успешные активация и геометрия и ровно одна FAILURE по caller `requires` с именем `merge_halves_numeric_order`. Генератор Replace ставит геометрию перед numeric assert, а preconditions перед old и havoc. Назначенный отказ проверяется до постусловия и actual merge в этом корне отсутствует. [Harness](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:536) · [Разворачивание requires в Replace](/root/kani-upstream-ch8-s1/library/kani_macros/src/sysroot/contracts/replace.rs:101)
- **H10 literal.** Произвольный V34 с нулевым `v[10..20]` и q=2 проходит actual `sort_right_ten` с теми же verified swap/insert. Затем без развилки записываются `v[10]=1` и `v[11]=0`. Сохраняются q-пост относительно исходного span, q-frame, внешний V34 frame, cover numeric prefix внутри `sort_right_ten` и `MB_H10_LITERAL_CORRUPT_PATH` перед назначенным assertion. Ожидается ровно одна FAILURE `MB_H10_LITERAL_CORRUPT_NUMERIC_ORDER`. [Actual H10 маршрут](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:392) · [Harness](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:572)

## Офлайн-проверки и открытые обязательства

- Прошли `rustfmt 1.12.0-nightly (65ce8611fe 2026-11-18) --edition 2024 --check` для обоих verification-модулей и изолированного нового блока атрибутов, `git diff --check`, побайтная сверка runtime-файла после исключения блока атрибутов и статическая сверка режимов, stubs, cfg, source bindings и диапазона `modifies`.
- В отдельном Python расчёте перебраны 26 620 комбинаций для двух численно упорядоченных половин над `{0, 1, 255}` и порогов `{0, 1, 2, 255}`. Сверены движение курсоров, диапазоны каждой записи, odd slot, guard и пороговая маска. Проверены формулы обоих literal witnesses. Это проверка исходной кодировки в ограниченной модели.
- `validate` с синтетическими GitHub metadata подтвердил commit/tree/parent control, event/ref/attempt и хэши. `check-source` подтвердил чистые std/tool checkout, оба commit/tree и SHA-256 восьми std-файлов. `python3 -m unittest -v test_run.py` прошёл 14 из 14 тестов с синтетическими Python-процессами, включая оба cfg и таймаута, exact argv, caps/latest start, cleanup, drift и унаследованные error paths.

Cargo, rustc, Kani, CBMC и CI не запускались. Пушей не было. Компиляция, native diagnostics, property bindings, applicability, resource fit и исходы всех четырёх корней открыты. Proof credit — `NONE`. Caller `small_sort_network`, его numeric Pre на actual состояниях и actual copy-back остаются пакету C. Выбор композиции C зависит от замеров B.
