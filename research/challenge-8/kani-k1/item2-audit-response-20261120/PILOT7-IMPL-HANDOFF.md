# Кампания 7 q-пилота — handoff реализации

Подготовлен локальный пакет `RESEARCH_ONLY` для plain-композиции Q13/N17. Request имеет статус `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. [Задание](PILOT7-IMPL-TASK.md)

## Пины

| Объект | Worktree и ветка | Commit | Tree |
| --- | --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `1b82e2a9a70f0712986fab263c5e336e6edef3ca` | `8d66a57644630c07fb19e0948b48c3e3e2fc8441` |
| Control | `/root/kani-ch8-q-pilot-control-v1`, `experiment/ch8-q-pilot-control-v7` | `bc7fb06c3967184df78aaa3ba72da8d8b1764b56` | `a2a2dbdd39eecc1453d4c8d8acf386032fac9234` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Parent std — `c8b703918a40c03d5b889d3018d8d818a70c233f`. В std добавлены три корня в `sorting_q_pilot.rs` и `sorting_q_controls.rs`. Control v7 подготовлен из v6 `87c9919ffa3de7d63e6d4cf15f29209ec30ba821` с единственным parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Дельта к v6 состоит из request, runner и его тестов. Закреплённый event ref — `refs/heads/uninit-ci/ch8-q-pilot-v1`.

| Файл | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `d5d742f6812aeef70f345c2b6bc078f47c57fd18388fa44db573525f18c7e5ee` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `b6236462e69f88658057c25fff457f97bbc4456a4d3b65b77d73b6a9dfb228a9` |
| `ch8-q-pilot-control/test_run.py` | `eb25cabdfee6c9af17e4d17cc94c29e87234455ba871dd52bb8ee47b954bc6eb` |
| `verify/sorting_q_pilot.rs` | `1dcd6abd81201647e6f0393bc75536c8032ce115db5553eb42379099e61bbccb` |
| `verify/sorting_q_controls.rs` | `2272507c8c34c1fafbd8fd551d22c0f5139aafce9d13d7714c9dae0fb9702411` |

## Roster

| Порядок | ID | Суффикс exact selector | Ожидаемый результат |
| ---: | --- | --- | --- |
| 1 | `Q13-PLAIN-STUB-SWAP` | `sorting_q_pilot::q13_plain_stub_swap` | `SUCCESS`, включая `Q13_PLAIN_ORDER_QPOST`, q-frame, четыре байта хвоста и V34 frame |
| 2 | `N17-PLAIN-STUB-SWAP-INSERT` | `sorting_q_pilot::n17_plain_stub_swap_insert` | `SUCCESS`, включая `N17_PLAIN_QPOST`, q-frame и V34 frame вне `v[1..18]` |
| 3 | `N17-PLAIN-QPOST-CORRUPT` | `sorting_q_controls::n17_plain_qpost_corrupt` | Назначенная `FAILURE` на `N17_CORRUPT_QPOST` и достижимый `N17_CORRUPT_Q_ONE_CORRUPTION_PATH` |

Префикс селекторов — `slice::sort::shared::smallsort::verify::`. Все три корня используют `normal` cfg, `[u8; 34]`, `v[1..18]`, произвольные входные байты и `q`, unwind 36, `--no-assert-contracts`, `--jobs=1`, `--object-bits 12`, пустой `cbmc_args` и child timeout 600 с. Лимиты RSS для child, outer и резерва составляют 6, 12 и 2 GiB соответственно. Сумма child timeouts — 1 800 с. Для каждого корня запас между latest start и общим cutoff составляет 630 с.

Q13 исполняет тело `sort13_optimal` с 45 подменами `swap_if_less` по контракту P-1. N17 исполняет тела `small_sort_network`, `sort13_optimal` и `insertion_sort_shift_left` с теми же 45 подменами и четырьмя подменами `insert_tail` по P-3 на позициях 13–16. Два положительных корня сохраняют по шесть условий covers из P-2 и P-4 соответственно. Контроль повторяет вызов N17 и при `[0; 17]` и `q = 1` записывает `255` в первый элемент после возврата. Входная маска-цель равна нулю, а бит 0 результата установлен принудительно. Все новые метки уникальны.

## Локальные проверки

- `rustfmt --check` из `nightly-2026-11-19` прошёл на новых блоках. Полные файлы показали прежние семь замечаний в `sorting_q_pilot.rs` и два в `sorting_q_controls.rs`.
- Сверены условия covers, подмены и точные селекторы. Перебор исходной модели проверил 8 192 маски Q13, 131 072 маски N17, предусловие порогового порядка на каждом из четырёх шагов вставки и маску контрольного входа.
- `run.py validate` с синтетическими GitHub metadata проверил закоммиченный control, единственного parent и хеши payload. `run.py check-source` подтвердил чистоту checkout std и tool, commit/tree и хеши шести файлов std. `test_run.py` прошёл 14 из 14 тестов с подставными процессами. `git diff --check` прошёл.

Компиляция Rust, проверки памяти и результаты формальной верификации остаются открытыми. Cargo, rustc, Kani, CBMC и CI не запускались. Пушей не было.
