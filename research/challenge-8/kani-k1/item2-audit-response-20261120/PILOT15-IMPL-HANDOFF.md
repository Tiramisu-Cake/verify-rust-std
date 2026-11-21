# Кампания 15. Handoff Check sort9 на 11 object bits

Подготовлены девять точных корней на едином профиле `--object-bits 11`: три Check `sort9_optimal` с Replace `swap_if_less`, три Check с реальными swap, два потребителя N18/N19 и контроль порчи q-post. Пакет остаётся `RESEARCH_ONLY`. Статусы request — `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. [Задание Pilot 15](PILOT15-IMPL-TASK.md) · [Handoff Pilot 14](PILOT14-IMPL-HANDOFF.md)

В кампании 14b на 12 object bits все три Check с Replace swap достигли cap 10 GiB до CNF. Сводка координатора сообщает SUCCESS зависимых N18/N19 и целевую FAILURE контроля. В кампании 5 полный Check `sort13_optimal` с реальными swap на 11 object bits дошёл до CNF при 5,45 GiB и завершился по таймауту 600 с. Это исходные наблюдения для сравнения. [Сводка 14b](run-44883003487/SUMMARY.md) · [Сводка 5](run-44849901344/SUMMARY.md)

## Pins и SHA-256

| Объект | Worktree и ветка | Commit | Tree |
| --- | --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `c5dc2a415eb11cb12d1e3a2af8e311739e085f92` | `ceca4e449422c32e307b4cde6a1490423ed4b8dc` |
| Control | `/root/kani-ch8-q-pilot-control-v12`, `experiment/ch8-q-pilot-control-v15` | `29e75d9887c2145b5beedf9eb6b170d13bf9218a` | `1b6ae480bc28d83df61c4e5f0907e5f4ef3282d6` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Единственный parent std — `ad2c458a679bcf55691e5a208adc8d27ca3e31c3`. Дельта затрагивает только `sorting_q_merge.rs`. Его SHA-256 — `448121c179dc7224e969c37449be19b3d2c36272a1466401ad9537e10155d5de`. Хэши остальных семи проверяемых std-файлов совпадают с 14b и перечислены в request. [Verification-модуль](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:766) · [Request](/root/kani-ch8-q-pilot-control-v12/ch8-q-pilot-control/CI-REQUEST.json)

Ветка control создана на `c01bf94117ecda58271369f5b44e0be1fc56dd79` (`experiment/ch8-q-pilot-control-v14b`). Итоговый коммит на новой ветке имеет единственный parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. От базы 14b изменены roster, тестовые fixtures, std pin/tree и хэши. Workflow и event ref `refs/heads/uninit-ci/ch8-q-pilot-v1` побайтно совпадают с 14b. Название шага `Run seven q-pilot roots` осталось историческим. Фактическое число запусков задаёт roster.

| Control-файл | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `b9c6e56a65d8719e47d19c7613941ec3d6d186febfa81c76b93b96ec01371639` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `9a6bbc1ef3fd32a7325cf5b62b4f3a6cfaa6a69e6f251ec84ca85ececf08a7f2` |
| `ch8-q-pilot-control/test_run.py` | `c2fdafc208f2bcd07c7fa5d486c7ce1a690edee63ef0ad73489ffbd9e2ae5a5f` |

## Порядок запуска и роли

Префикс всех селекторов — `slice::sort::shared::smallsort::verify::sorting_q_merge::`. Столбец исходов задаёт ожидаемые результаты.

| № | Root ID | Суффикс selector | Режим и вход | Verified stubs | Ожидание |
| ---: | --- | --- | --- | --- | --- |
| 1 | `MD-SORT9-L1-OB11` | `md_sort9_left_b01_len09` | Check sort9, `v[1..10]` | `swap_if_less` | SUCCESS |
| 2 | `MD-SORT9-R9-OB11` | `md_sort9_right_b10_len09` | Check sort9, `v[10..19]` | `swap_if_less` | SUCCESS |
| 3 | `MD-SORT9-R10-OB11` | `md_sort9_right_b10_len10` | Check sort9, `v[10..20]` | `swap_if_less` | SUCCESS |
| 4 | `MD-SORT9-L1-ACT-OB11` | `md_sort9_left_b01_len09_actual_swaps` | Check sort9, `v[1..10]` | — | SUCCESS |
| 5 | `MD-SORT9-R9-ACT-OB11` | `md_sort9_right_b10_len09_actual_swaps` | Check sort9, `v[10..19]` | — | SUCCESS |
| 6 | `MD-SORT9-R10-ACT-OB11` | `md_sort9_right_b10_len10_actual_swaps` | Check sort9, `v[10..20]` | — | SUCCESS |
| 7 | `MD-NETWORK-N18-OB11` | `md_network_n18_b01` | Proof, `v[1..19]` | `sort9_optimal`, `bidirectional_merge` | SUCCESS |
| 8 | `MD-NETWORK-N19-OB11` | `md_network_n19_b01` | Proof, `v[1..20]` | `sort9_optimal`, `insert_tail`, `bidirectional_merge` | SUCCESS |
| 9 | `MD-N19-QPOST-CORRUPT-OB11` | `md_network_n19_corrupt_literal` | Proof, `v[1..20]` | `sort9_optimal`, `insert_tail`, `bidirectional_merge` | Единственная FAILURE `MD_N19_CORRUPT_QPOST` |

На всех строках `merge_c_sort9`, unwind36, обычные stubs отсутствуют, дополнительные CBMC-аргументы пусты. Профиль использует CaDiCaL, `--exact --jobs=1 --no-assert-contracts`, OFF и отдельные target dirs. Child cap 10 GiB, outer 12 GiB, резерв 2 GiB. Девять последовательных child по 600 с дают 5 400 с child budget. Setup/build один, до 1 800 с. Job 180 мин с резервом финализации 540 с. Latest start за 630 с до supervisor cutoff. Capture caps stdout/stderr/export — 16/1/8 MiB, суммарно 256 MiB.

## Сверка Check и формы контракта

- В каждом новом Check те же guards, `proof_for_contract(sort9_optimal)`, `unwind(36)`, произвольные initialized V34 и q, `KeyLess<u8>` и прямой вызов на том же литеральном срезе. R10 проверяет frame за пределами `v[10..19]`, включая сохранность `v[19]` для правого `insert_tail`. Варианты actual выполняют те же 25 вызовов `swap_if_less` по реальному телу. [Новые корни](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:884)
- Общий макрос генерирует helper с двумя frame assertions и семью covers. Для Replace сохранены исходные предикаты и метки `MD_SORT9_*`. Для actual префиксы `MD_SORT9_L1_ACT`, `MD_SORT9_R9_ACT` и `MD_SORT9_R10_ACT` дают 27 новых уникальных меток. `concat!` формирует строковые литералы в исходнике. Native locations свойств после раскрытия макроса подлежат сверке на новом pin. [Helper](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:766)
- Образец формы — `sort13_optimal` на std `c8b703918a40c03d5b889d3018d8d818a70c233f`, где полный Check из кампании 5 дошёл до CNF. Контракт использует один `ensures` с `old(prefix_capture(v, is_less))`, а возвращаемый `PrefixSnapshot` имеет `Clone + Copy`. У `sort9_optimal` на базе 14b уже один `ensures`, объединяющий q-post и numeric post через `&&`. Единственный `old(capture(v, is_less))` возвращает `Option<Snapshot>` с `Clone + Copy` у `Snapshot`. `smallsort.rs` и модели побайтно совпадают с parent. [Образец sort13](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:580) · [Контракт sort9](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:511) · [Snapshot sort9](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge_model.rs:412)

## Локальная проверка и открытые результаты

- `validate` с синтетическими GitHub metadata подтвердил control commit/tree/parent, event/ref/attempt, замороженные поля request и SHA-256 payload. `check-source` подтвердил чистые std/tool checkout, оба commit/tree и все восемь std SHA-256. `python3 -m unittest -v test_run.py` прошёл 14/14 на синтетических Python-процессах. Проверены девять последовательных запусков, exact argv с `11` и `600s`, номинальный и нижний effective cap, latest start, capture caps, cleanup, drift и error paths.
- `git diff --check` прошёл для std и control. Статическая сверка подтвердила побайтное совпадение прежних Check корней и потребителей с 14b, эквивалентность предикатов общего helper, три точные пары fixture и 27 новых меток. Cargo, rustc, Kani, CBMC, CI и push в этой стадии не выполнялись. Компиляция и все native outcomes Pilot 15 открыты.
- Для квалификации сравнить обе серии Check и данные 14b по последней фазе, первой CNF, VT, child time, nominal/effective cap и PGID/component RSS. На 11 object bits отдельно сверить native pointer/allocation checks, Pre, обе части post, assigns на первых девяти байтах, frame и covers. Для N18/N19 сверить обе инстанциации Replace sort9, связанные сводки insert/merge, copy-back и целевой `MD_N19_CORRUPT_QPOST` по native ID/class/location. Результаты зависимых потребителей сохраняют условный статус до квалификации провайдеров и matched-профиля. Native uninit/validity относятся к отдельной matched ON-проверке. [Привязка Check к Replace](PILOT14-IMPL-HANDOFF.md#привязка-check-к-replace) · [Чек-лист qualification](QUALIFICATION-CHECKLIST.md)
