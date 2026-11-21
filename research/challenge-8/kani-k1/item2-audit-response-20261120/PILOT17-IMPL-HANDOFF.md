# Кампания 17. Handoff повторов wide и цепочки sort13

Подготовлены один std-кандидат и два локальных Control-кандидата. 17A содержит четыре повтора wide на OB12 и пять Check sort13 на OB11. 17B содержит Check P‑3, пять no-merge consumers и два контроля на OB12. Оба request имеют `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Кампания остаётся `RESEARCH_ONLY`. [Задание 17](PILOT17-IMPL-TASK.md) · [Handoff 16](PILOT16-IMPL-HANDOFF.md)

## Пины и SHA-256

| Объект | Worktree | Ветка | Commit | Tree |
| --- | --- | --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1` | `experiment/ch8-q-pilot-v1` | `3fff6aa0dbab95e9889ab864e6b88596c4e452fe` | `a41b4c4822ab9df70db698ce576b3112a670ba80` |
| Control 17A | `/root/kani-ch8-q-pilot-control-v17a` | `experiment/ch8-q-pilot-control-v17a` | `cb81adc41d7bce501d8a93c4e90bb236a27b550f` | `647b4bf6a9c749e5983159181216565467de46a4` |
| Control 17B | `/root/kani-ch8-q-pilot-control-v17b` | `experiment/ch8-q-pilot-control-v17b` | `628a03ef3d24ad433e977a7e3cfec003c9993292` | `26558404aa1e4a58c86ad7d3084230c60123b09b` |
| Tool | `/root/kani-upstream-ch8-s1` | detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Единственный parent std — `ed184d3f172def1b4d1bf6281a03ba2a0d5bb8f1`, tree базы — `e2a757c2ca5659a83e70f3775ebce3e672dd0463`. Единственный parent обоих Control — `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. База содержимого Control — v16 `0578f584b650488cee98281961e8f699a82ab942` / `6e0f3a04555c4dfe90a5d3195610b86c541cc253`. Workflow, event ref `refs/heads/uninit-ci/ch8-q-pilot-v1` и жизненный цикл runner сохранены. [Request 17A](/root/kani-ch8-q-pilot-control-v17a/ch8-q-pilot-control/CI-REQUEST.json) · [Request 17B](/root/kani-ch8-q-pilot-control-v17b/ch8-q-pilot-control/CI-REQUEST.json)

| Изменённый файл std | SHA-256 |
| --- | --- |
| `smallsort.rs` | `bd4eb6faffe3992d26c282553b01b4008c88cfe75e820f622c40e4d50bde408a` |
| `sorting_q_merge.rs` | `55f94471200deb46a264a8b3e8589caa8767ea6db252de0e161d01cc03cc00ce` |
| `sorting_q_merge_model.rs` | `ce43ccd53d0e0764374b1e0c87749a563b49f11c262cf6dd6ec2f41f9ac4e3fa` |

Оба request фиксируют все восемь SHA-256 std. Хэши оставшихся пяти файлов совпадают с Pilot 16.

| Файл Control | SHA-256 17A | SHA-256 17B |
| --- | --- | --- |
| `CI-REQUEST.json` | `0a33bf5f542d8aacf29f15a0a18abaa94eeb20024f5287b610333f2f084db6e7` | `50b729ca18c9124fc523ccbba4e622012af75800f3d3cdaa6efd3843e0b87f1b` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `run.py` | `9f5f43798ba7b0a5015b754408648f3e3d0beb62a2b74ee2453024460b70cec6` | `c95397405255700f9fafd670ac931b2976d80396fe104ec4fe8ae73fe777da18` |
| `test_run.py` | `60e538b59c411fa50a6995411e719cbda46451e428f5dc7d5e94a59e64b3c83e` | `7694425637696d00c84dc17a997259a0309b3c730f101f576a34d79afd7c2438` |

## Roster и бюджеты

Префикс exact selectors — `slice::sort::shared::smallsort::verify::`. Модуль всех строк — `sorting_q_merge`, кроме P‑3 в `sorting_q_pilot`. Ordinary stubs и дополнительные CBMC args пусты у всех строк. Check выполняют actual leaf. Verified stubs для четырёх повторов wide совпадают с Pilot 16. [Roster 16](PILOT16-IMPL-HANDOFF.md#roster-и-зависимости)

| Пакет | Root ID | Суффикс selector | Cfg / OB | Child, с | Геометрия или verified stubs |
| --- | --- | --- | --- | ---: | --- |
| 17A | MW-INSERT-L-OB12 | `mw_insert_left_rel9_11` | merge_wide / 12 | 600 | Check insert, base1/rel9–11 |
| 17A | MW-NETWORK-N20-OB12 | `mw_network_n20` | merge_wide / 12 | 450 | sort9, insert, merge |
| 17A | MW-NETWORK-N25-OB12 | `mw_network_n25` | merge_wide / 12 | 450 | sort9, sort13, insert, merge |
| 17A | MW-N25-QPOST-CORRUPT-OB12 | `mw_network_n25_corrupt` | merge_wide / 12 | 300 | Те же stubs, что у N25 |
| 17A | NM-S13-L13 | `nm_sort13_left_len13` | no_merge_sort13 / 11 | 1200 | Check sort13, `v[1..14]` |
| 17A | NM-S13-L14 | `nm_sort13_left_len14` | no_merge_sort13 / 11 | 1200 | Check sort13, `v[1..15]` |
| 17A | NM-S13-L15 | `nm_sort13_left_len15` | no_merge_sort13 / 11 | 1200 | Check sort13, `v[1..16]` |
| 17A | NM-S13-L16 | `nm_sort13_left_len16` | no_merge_sort13 / 11 | 1200 | Check sort13, `v[1..17]` |
| 17A | NM-S13-L17 | `nm_sort13_left_len17` | no_merge_sort13 / 11 | 1200 | Check sort13, `v[1..18]` |
| 17B | NM-INSERT-P3-OB12 | `p3_insert_u8_b01_rel1_16_q_any` | no_merge_sort13 / 12 | 600 | Check insert, base1/rel1–16 |
| 17B | NM-NETWORK-N13 | `nm_network_n13` | no_merge_sort13 / 12 | 450 | sort13, 0 inserts |
| 17B | NM-NETWORK-N14 | `nm_network_n14` | no_merge_sort13 / 12 | 450 | sort13, insert rel13 |
| 17B | NM-NETWORK-N15 | `nm_network_n15` | no_merge_sort13 / 12 | 450 | sort13, insert rel13–14 |
| 17B | NM-NETWORK-N16 | `nm_network_n16` | no_merge_sort13 / 12 | 450 | sort13, insert rel13–15 |
| 17B | NM-NETWORK-N17 | `nm_network_n17` | no_merge_sort13 / 12 | 450 | sort13, insert rel13–16 |
| 17B | NM-N13-QPOST-CORRUPT | `nm_network_n13_corrupt` | no_merge_sort13 / 12 | 300 | Те же stubs, что у N13 |
| 17B | NM-N17-QPOST-CORRUPT | `nm_network_n17_corrupt` | no_merge_sort13 / 12 | 300 | Те же stubs, что у N17 |

В обоих пакетах CaDiCaL, `--exact --jobs=1 --no-assert-contracts`, unwind36 и отдельные target dirs. Профиль OFF сохраняет обычные memory/bounds/overflow/unwind checks. Job 10 800 с, setup/build до 1800 с, финализация 540 с, на child доступны 8460 с. У 17A child budget 7800 с, остаток 660 с, local cap 10 485 760 KiB. У 17B child budget 3450 с, остаток 5010 с, local cap 6 291 456 KiB. Outer cap 12 GiB, резерв 2 GiB. Latest start за timeout + 30 с до supervisor cutoff, то есть за 330/480/630/1230 с для четырёх timeout. Capture 16/1/8 MiB stdout/stderr/export и aggregate 384 MiB.

Для допуска ресурсная цель — sampled child PGID peak ≤6 291 456 KiB на каждом корне цепочки, включая Check и wide-повторы 17A. Сохранять nominal/effective cap, PGID и component RSS, отдельно outer RSS, phase, VT/child, CNF и native terminal inventory либо первопричину cutoff и `NOT_RUN`. Сравнивать OB12 повторы с остановками OB11 и Check sort13 с правой геометрией из 16, где исходная сводка сообщает 875 с child, 833,6 с VT, 7,32 GiB и 25,5 млн дизъюнктов. Исторические 6,04 GiB у wide N32 также оставляют ресурсную цель открытой. [Сводка 16](run-44890498157/SUMMARY.md)

Если завершившийся Check выйдет за 6 GiB, следующий замер — один exact A/B формы frame или observer с теми же actual swaps, assigns, семантикой и safety checks. Если на OB12 повторится ошибка ёмкости, следующий шаг — локализация адресуемых temporaries в этом exact root.

## Контракты и геометрия

- `no_merge_sort13` добавляет `--cfg=kani_smallsort_q_no_merge_sort13` к `merge_wide` с прежними normal guards. Только здесь sort13 принимает 13–17 вместо 13–16. Pre проверяет exact `u8/KeyLess<u8>`, читаемость initialized span и writable prefix. Sort13 использует один `ensures` с `old(presort_capture(v, is_less))` в форме wide: owned `Option<PrefixSnapshot>`, снимок `Clone + Copy`. Post проверяет числовой порядок первых 13 байтов, сохранение их `count(byte < q)` и q. Порядок и count определяют пороговую маску. Под `merge_wide` сохранились предыдущие guards, эффективная геометрия и все активные clauses. [Контракт](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:609) · [Модель](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge_model.rs:470)
- Во всех пяти Check произвольный initialized V34 и независимый q. Литералы диапазонов задаёт общая декларация пар Check/consumer. Check исполняют 45 actual swaps и используют прежний wide frame/cover helper. `modifies(v.as_mut_ptr().cast::<[T; 13]>())` покрывает ровно `v[1..14]`. Frame проверяет `v[..1]`, `v[14..]` с полным хвостом и q. Семь covers проверяют mixed threshold, ties, q=0, q=255, отсутствие q во входном префиксе, инверсию и возврат. [Frame и covers](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:788) · [Литералы и selectors](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1758)
- `insert_tail` в новом cfg использует единственный прежний q-only `ensures` P‑3 с `old(capture(begin, inclusive_len, is_less))` и owned `Snapshot: Clone + Copy`. Pointer Pre и q-монотонность старого префикса активны. `modifies` покрывает inclusive span. Post сохраняет q и задаёт q order-stat с учётом добавленного байта. P‑3 сохранён побайтно с произвольным V34 и q, base1/rel1–16, frame и 24 covers. Rel16 захватывает ровно 17 байтов. Форма P‑3 совпадает с кампанией 9, где исходная сводка сообщает 452 с и 5,45 GiB при OB12. [Контракт](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:717) · [Harness P‑3](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_pilot.rs:315) · [Сводка 9](run-44862241314/SUMMARY.md)
- Positive consumers подтверждают активность q/byte моделей и захватывают target исходного полного среза через q-model `CAP=17`. Actual network передаёт полный срез в один Replace sort13. Insertion loop начинает с rel13 и останавливается на one-past `base + N`. N13 имеет пустой loop, N14–N17 имеют 1–4 Replace insert. Все Replace проверяют native caller Pre. Numeric Pre merge отсутствует на этом маршруте. После возврата проверяются q order-stat полного среза, q, все внешние байты и шесть covers C13. [Маршрут](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:332) · [Loop](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:868) · [Consumers](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1675)

## Контроли

| Корень | Ожидаемая единственная native FAILURE класса `assertion` | Ожидаемые covers |
| --- | --- | --- |
| MW-N25-QPOST-CORRUPT-OB12 | `MW_N25_CORRUPT_QPOST`, [assert в `mw_network_n25_corrupt`](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1621) | `MW_N25_CORRUPT_USEFUL_RETURN`, `MW_N25_CORRUPT_PATH` |
| NM-N13-QPOST-CORRUPT | `NM_N13_CORRUPT_QPOST`, [assert в `nm_network_n13_corrupt`](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1800) | `NM_N13_CORRUPT_USEFUL_RETURN`, `NM_N13_CORRUPT_PATH` |
| NM-N17-QPOST-CORRUPT | `NM_N17_CORRUPT_QPOST`, [assert в `nm_network_n17_corrupt`](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1833) | `NM_N17_CORRUPT_USEFUL_RETURN`, `NM_N17_CORRUPT_PATH` |

У всех трёх q=1 и нулевой активный вход с произвольными внешними байтами. После actual network cover проверяет `v[1] == 0`. Запись 255 меняет младший бит ожидаемой нулевой маски. Второй cover проверяет мутацию, q и outside frame проверяются отдельно. Привязка native ID с ordinal, класса и экспортированного location к указанному assert остаётся до появления native inventory. Для MW-INSERT-L-OB12 ожидаются SUCCESS и covers rel9, rel10, rel11. Для остальных положительных корней ожидается SUCCESS со всеми заявленными covers.

## Mixed-рёбра для review

| Consumer OB12 | Check OB11 | Совпадающие call sites |
| --- | --- | --- |
| `NM-NETWORK-N13` … `NM-NETWORK-N17` | `NM-S13-L13` … `NM-S13-L17` соответственно | Полный `v[1..1+N]`, запись `v[1..14]` |
| `NM-N13-QPOST-CORRUPT`, `NM-N17-QPOST-CORRUPT` | `NM-S13-L13`, `NM-S13-L17` соответственно | Те же срезы и footprint при q=1 |
| `MW-NETWORK-N20-OB12` | Pilot 16 `MW-S9-L10`, `MW-S9-R10`, `MW-INSERT-R`, `MW-MERGE-N20` | Presort `v[1..11]` и `v[11..21]`, правый insert base11/rel9, merge `v[1..21]` → scratch32 +0 |
| `MW-NETWORK-N25-OB12`, `MW-N25-QPOST-CORRUPT-OB12` | Pilot 16 `MW-S9-L12`, `MW-S13-R13`, `MW-MERGE-N25` | Presort `v[1..13]` и `v[13..26]`, merge `v[1..26]` → scratch32 +0 |

Отдельно сопоставить same-width рёбра OB12. `MW-INSERT-L-OB12` обслуживает base1/rel9 у N20 и base1/rel9–11 у N25 и его контроля. P‑3 обслуживает все insert у N14–N17 и контроля N17. Пять левых Check имеют собственную геометрию и новый cfg.

Для каждого mixed-ребра сверить exact type/body/clauses, tool/checks/unwind, домен, allocation и offsets, native caller Pre, Check post, frame/assigns и нужные U. Полные native inventory и terminal outcomes обеих сторон должны подтверждать отсутствие ошибки ёмкости. На x86_64 OB11 и OB12 дают 53 и 52 signed offset bits. Review должен сопоставить provenance, one-past и merge sentinels, поведение сравнений, cast-to-int и `checked_sub` inclusive длины вставки, ветвление на `same_allocation` и `abs_diff` в merge geometry, overflow и havoc. Границы V34/scratch32 дают аргумент по размерам, а связь с выражениями проверяется по каждому call site. Для открытых рёбер нужен bridge либо exact matched-width replay там, где хватает object IDs. При cutoff, незавершённой привязке или превышении 6 GiB admission остаётся открытым независимо от native итога consumer. [Критерии 17](PILOT17-IMPL-TASK.md#квалификация-смешанных-object-bits) · [Чек-лист](QUALIFICATION-CHECKLIST.md)

## Локальные проверки

- Статическая сверка подтвердила побайтное совпадение `smallsort.rs` после исключения `cfg_attr` и прежних активных clauses для 2048 комбинаций флагов без нового cfg. Дополнительно проверены guards двух изменённых контрактов, прежний исходник всех harnesses, четыре wide-повтора и их достижимый исходник при `merge_wide`, точные литералы, 45 swaps, frame, P‑3 и `CAP=17`. Форма `old` сверена с компилировавшимися sort13 из 16 и P‑3 из 9.
- `rustfmt --check` из `nightly-2026-11-19` с `--edition 2024 --config skip_children=true,use_small_heuristics=Max --unstable-features` прошёл на затронутых блоках. Полные файлы выдали прежние 1/30/4 замечания для `smallsort.rs`, `sorting_q_merge.rs` и `sorting_q_merge_model.rs`, соответственно. Новых замечаний нет. `git diff --check` прошёл.
- `validate` с синтетическими GitHub metadata и `check-source` на чистых закреплённых checkout прошли для обоих Control. Независимо сверены порядок и поля всех exact roots, оба cap, бюджеты, SHA-256, event ref, parent и сохранение runner/cleanup. `python3 -m unittest -v test_run.py` прошёл 14/14 на каждом кандидате с синтетическими Python-процессами. Проверены argv, drift ширины/cfg/timeout, nominal/effective RSS, latest start, capture, cleanup, error paths и `NOT_RUN`. `git diff --check` прошёл для обоих Control.

Компиляция на новых pins, native outcomes, ресурсные замеры и proof credit остаются открытыми. Для dispatch требуются review и отдельный GO.
