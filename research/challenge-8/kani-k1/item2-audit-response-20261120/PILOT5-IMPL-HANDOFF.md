# Кампания 5 q-пилота — handoff реализации

Измерительный пакет P‑2 подготовлен локально. Режим `RESEARCH_ONLY`, request `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. [Задание](PILOT5-IMPL-TASK.md) · [Анализ кампании 4](PILOT-RUN4-ANALYSIS.md)

## Идентичности

| Объект | Worktree и ветка | Commit | Tree |
| --- | --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `c8b703918a40c03d5b889d3018d8d818a70c233f` | `7ebee5d0bf4a1b1b0fb53c21f30e41c49294aed5` |
| Control | `/root/kani-ch8-q-pilot-control-v1`, `experiment/ch8-q-pilot-control-v5` | `d453bb80a574ffbfd09a6f9d8dcdc08d118ea9a1` | `7b63b948ef5886ddbb979048871b19fd64b787bc` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Parent std — `c59b0d2a21c84bcf9786cd2b4c4c152be23588ae`. Кандидат control подготовлен из v4 `9fb54361f51eda0609821b83d30411c2747b789f` на новой локальной ветке с единственным parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. v4 сохранил прежний указатель. Workflow и frozen ref `refs/heads/uninit-ci/ch8-q-pilot-v1` взяты из v4. Шаг workflow с историческим названием `Run seven q-pilot roots` передаёт управление runner с новым roster из пяти корней.

| Файл | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `d5bcb268ac34d0b3039ab10a376b0dcf2966517f2fb27afbeed1f466e92ff0e2` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `fad74e3796eb52bb0768767c84409d93a0cbd48ab6844d61790ad771da68c524` |
| `ch8-q-pilot-control/test_run.py` | `0ffec32cdca23c51854841ebc29ca46cac9a18dae27ae74c01bac85be202de87` |
| `smallsort/verify/sorting_q_model.rs` | `5e5eac5ad26d1352df52b659a12eb5396ef23872f724c1b460441eb6a37520f0` |
| `smallsort/verify/sorting_q_pilot.rs` | `0875b58abeb8f87957c8f2335b5bfb650418127cdaf99693bb72c31f65e562cb` |

## Порядок измерений

| Корень | Суффикс exact selector | Object bits | Таймаут child, с | Обязательство |
| --- | --- | ---: | ---: | --- |
| P-2b-OB11 | `p2b_sort13_u8_b01_len17_q_any_actual_swaps` | 11 | 600 | Прежний Check на V34 с 45 вызовами actual swap |
| D13-BODY-V34 | `d13_body_v34` | 12 | 180 | Plain proof на V34 с явной проверкой len и active, `prefix_capture` до прямого вызова и `prefix_post` после него |
| D13-CHECK-V19 | `d13_check_v19` | 12 | 180 | Полный Check на V19 с canary в позициях 0 и 18 и четырьмя байтами хвоста |
| D13-CHECK-P17 | `d13_check_p17` | 12 | 180 | Check первых 17 компараторов на V34, сохранение числа установленных битов пороговой маски |
| D13-CHECK-P31 | `d13_check_p31` | 12 | 180 | Check первых 31 компаратора на V34 с тем же контрактом |

Все пять селекторов начинаются с `slice::sort::shared::smallsort::verify::sorting_q_pilot::`. У всех `u8/KeyLess<u8>`, произвольные q и входные байты, base 1, len 17, unwind 36, шесть одинаковых условий covers и свои метки ролей. P17 и P31 используют одну модель постусловия, которая захватывает q, `count_ones` пороговой маски первых 13 байт и четыре байта хвоста. Оба разрешают запись в первые 13 байт среза и отдельно проверяют внешний байтовый frame.

Control использует `normal` cfg, `--no-assert-contracts`, `--jobs=1` и CaDiCaL по умолчанию закреплённого tool. У каждого корня свой target dir и bounded capture. Номинальный child cap 6 GiB (6 291 456 KiB), outer cap 12 GiB (12 582 912 KiB), резерв 2 GiB (2 097 152 KiB). Эффективный child cap равен минимуму номинального и доступного group cap. Сумма таймаутов child составляет 1 320 с, окно setup/build составляет 1 800 с.

Таймаут из roster задаёт `--harness-timeout`, внешний timeout дочернего процесса и latest start. Последний вычисляется вычитанием таймаута корня и 30 с запаса запуска из общего supervisor cutoff. В `q-pilot-raw.json` записываются `roots[].object_bits`, `roots[].timeout_seconds` и `job_boundary.latest_root_start_monotonic_by_root`. Поля `roots[].child.component_group_peak_kib` и `component_rss_scope` сохраняют sampled peaks групп процессов с исходным scope stock runner. Эти пики могут относиться к разным моментам времени.

## Локальная проверка std

- Статически сверены порядок и литеральные пары первых 17 и 31 вызовов `swap_if_less` с 45 call sites `sort13_optimal`. Перебор 8 192 пороговых масок для каждого префикса подтвердил сохранение `count_ones` в модели компараторов.
- P‑2b, runtime `smallsort.rs` и прежние определения q-модели побайтно совпадают с базой. У пяти измерительных корней сверены шесть условий covers и уникальные явные метки.
- `rustfmt --check` из nightly-2026-11-19 прошёл на новых блоках и на полном `sorting_q_model.rs`. Полный `sorting_q_pilot.rs` выдаёт те же семь замечаний форматирования, что и база. `git diff --check` прошёл.

## Локальная проверка control

- `run.py validate` на закоммиченном кандидате с синтетическими GitHub metadata проверил commit, tree, parent и хэши payload. `run.py check-source --std /root/verify-rust-std-ch8-q-pilot-v1 --tool /root/kani-upstream-ch8-s1` проверил чистоту обоих checkout, commit/tree и хэши шести файлов std.
- Для всех пяти корней сверены exact selectors с std, построенный argv и арифметика latest start. У первого корня подстановка `--object-bits 11` даёт единственную дельту к argv кампании 4 при одинаковых путях.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_run.py` прошёл 13 из 13 тестов. Проверены порядок roster, неверные значения и типы параметров, nominal и effective RSS cap, child timeout, latest start, запись component peaks и очистка после прерывания.

Коммиты std, control и g0 оформлены от `Tiramisu-Cake <igkharin@gmail.com>` с `[skip ci]`. Cargo, rustc, Kani, CBMC и CI не запускались. Пушей не было. Статус Rust-компиляции и результаты измерений остаются открыты.
