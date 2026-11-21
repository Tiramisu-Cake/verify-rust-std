# Кампания 8 q-пилота — handoff реализации

Подготовлен локальный control-пакет `RESEARCH_ONLY` для двух plain-корней N17 с номинальным RSS-лимитом 10 GiB. Статус request — `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. [Задание](PILOT8-IMPL-TASK.md) · [Сводка кампании 7](run-44856804576/SUMMARY.md)

## Пины

| Объект | Worktree и ветка | Commit | Tree |
| --- | --- | --- | --- |
| Control | `/root/kani-ch8-q-pilot-control-v8`, `experiment/ch8-q-pilot-control-v8` | `f8399974170e0a85b0e20b7bc2290431fb47c357` | `16e25d76f192ee7b23e9a8aebfa919dca2cc941b` |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `1b82e2a9a70f0712986fab263c5e336e6edef3ca` | `8d66a57644630c07fb19e0948b48c3e3e2fc8441` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Ветка v8 подготовлена из v7 `bc7fb06c3967184df78aaa3ba72da8d8b1764b56` в отдельном worktree. У коммита v8 единственный parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Дельта к v7 состоит из request, runner и его тестов. Закреплённый event ref — `refs/heads/uninit-ci/ch8-q-pilot-v1`.

| Файл control | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `192f9253b512aec8fa144dd8b56382f46bf2273b8a0f285a4a8305ce7f570092` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `ba2b6ced2f425fdbe90720b4332faf93099ecdb952289608fe0c4a69a9a143e6` |
| `ch8-q-pilot-control/test_run.py` | `dd0b74849a61e8f47415f9a015cc536be9ee3a9c81fd41178dbd1728bc043148` |

## Порядок и лимиты

| Порядок | ID | Суффикс exact selector | Ожидаемый результат |
| ---: | --- | --- | --- |
| 1 | `N17-PLAIN-STUB-SWAP-INSERT` | `sorting_q_pilot::n17_plain_stub_swap_insert` | `SUCCESS` для `N17_PLAIN_QPOST`, q-frame и V34 frame вне `v[1..18]` |
| 2 | `N17-PLAIN-QPOST-CORRUPT` | `sorting_q_controls::n17_plain_qpost_corrupt` | Назначенная `FAILURE` на `N17_CORRUPT_QPOST` и достижимый `N17_CORRUPT_Q_ONE_CORRUPTION_PATH` |

Префикс селекторов — `slice::sort::shared::smallsort::verify::`. Оба корня используют `normal` cfg, `--exact`, `--no-assert-contracts`, `--jobs=1`, unwind 36, `--object-bits 12`, пустой `cbmc_args` и child timeout 600 с. Сумма child timeouts — 1 200 с. Для каждого корня latest start на 630 с раньше общего cutoff.

Номинальные лимиты составляют 10 GiB (`10485760` KiB) для child и 12 GiB (`12582912` KiB) для outer. Резерв — 2 GiB (`2097152` KiB). Эффективный лимит child — `min(local, min(12 GiB, A − 2 GiB))`, где `A` учитывает `MemAvailable` и доступную память cgroup. В `q-pilot-raw.json` для запущенного child эти значения записываются в `child.nominal_rss_cap_kib` и `child.rss_cap_kib` соответственно. `supervisor.rss_cap_kib` отражает отдельный замер outer.

## Локальные проверки

- `run.py validate` с синтетическими GitHub metadata подтвердил control commit/tree, единственного parent, состав файлов и SHA-256 payload.
- `run.py check-source` подтвердил чистоту checkout std и tool, commit/tree и SHA-256 шести файлов std.
- `python3 -m unittest -v test_run.py` прошёл 14 из 14 тестов на подставных Python-процессах. Проверены порядок N17, запись nominal/effective при 10 GiB, остановка по меньшему эффективному лимиту, отклонение дрейфа roster/cap и обработка ошибок runner.
- `git diff --check` прошёл. Сравнение request с v7 подтвердило точное совпадение обоих профилей N17 и остальных пинов.

Результаты решателя и поведение N17 при 10 GiB остаются открытыми. Cargo, rustc, Kani, CBMC и CI не запускались. Пушей не было.
