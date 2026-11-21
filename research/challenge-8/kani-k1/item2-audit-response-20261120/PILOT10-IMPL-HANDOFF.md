# Кампания 10 q-пилота — handoff реализации

Подготовлен локальный кандидат для одного setup/build и последовательного запуска 13 exact roots. В roster входят 11 positives для оставшихся длин до merge и два контроля порчи q-post. Request `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Запуск требует отдельного ревью и GO координатора. [Задание Pilot 10](PILOT10-IMPL-TASK.md) · [Handoff Pilot 9](PILOT9-IMPL-HANDOFF.md)

## Пины и дельта

| Объект | Worktree и ветка | Commit | Tree |
| --- | --- | --- | --- |
| Control | `/root/kani-ch8-q-pilot-control-v10`, `experiment/ch8-q-pilot-control-v10` | `6f5009f3be62aabe867be0ff27230b941c8decd2` | `5f5e2a6a76ae847972fa93853d7807325f73ad5f` |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `632e4e8d3b8cd94c918979ac7f076afebd327c0f` | `439f17e9b980366910bf2d064ea8a4ecb1d76fec` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Единственный parent control — `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Дельта к v9 `baad011375b727383f7ea0abe429763c1a78ab13` состоит из roster в `run.py`, ожиданий fixtures в `test_run.py` и `CI-REQUEST.json`. Workflow побайтно совпадает с v9, включая event ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, guard и имя шага `Run seven q-pilot roots`. Порядок корней берётся из request.

Единственный parent std — `d968b9a8c341485e4df63ad852ac0806f37bb71b`, tree `d8eaa9033b531e8be2413599e19315f294c5aafb`. Дельта дописывает 11 harnesses в `smallsort/verify/sorting_q_pilot.rs`. Исходный файл до добавлений, прежние controls, runtime, leaf contracts, `KeyLess`, q-модель и регистрация совпадают с базой побайтно.

| Файл control | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `572b293ed71f62384c705530b4dc4ea7e419b9e431b52729a032f483b49b22a9` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `91e1ab48623e2b3d55364f545d69cb862e0dac5ac9e1a0d355fa374f0ca5c712` |
| `ch8-q-pilot-control/test_run.py` | `d83e24bf6acfeec35d69f402475261574bd43c9d45a83dd00da7f553afa019af` |

Пути std в таблице относительны к `library/core/src/slice/sort/shared/`.

| Файл std | SHA-256 |
| --- | --- |
| `smallsort.rs` | `200f4832551309317ecc3786df9aa5943434b8d25a2b58f869b554f0080c8ceb` |
| `smallsort/verify.rs` | `24e4b3042118d8904824a21dd72c46e7fc9384ef512f3bd10b412b4493d6177d` |
| `smallsort/verify/sorting_model.rs` | `dec45747dde28e0861becf4c0c089d2a9899ad035db30e9967d0a0041845fb88` |
| `smallsort/verify/sorting_q_model.rs` | `5e5eac5ad26d1352df52b659a12eb5396ef23872f724c1b460441eb6a37520f0` |
| `smallsort/verify/sorting_q_pilot.rs` | `ac755d455d7a0f5fbd706c90bb6bae02ffd4a4c41125db7e5fb28833da55a8b6` |
| `smallsort/verify/sorting_q_controls.rs` | `0ee56705b083f7610b764bc8bc164a81eae94de9229b33baf0169f6c7b8df9ff` |

## Roster

У всех selectors общий префикс `slice::sort::shared::smallsort::verify::`. Каждый корень идёт в normal / Proof с unwind36. В Replace перечислены все verified stubs. Ordinary stubs везде пусты. Последняя колонка фиксирует ожидаемый native исход.

| № | Root ID | Суффикс exact selector | Срез | Replace | Child, с | Маршрут и ожидаемый исход |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | N00-PLAIN | `sorting_q_pilot::n00_literal_plain_no_merge` | `v[1..1]` | ∅ | 300 | Ранний возврат, `SUCCESS` |
| 2 | N01-LITERAL-PLAIN | `sorting_q_pilot::n01_literal_plain_no_merge` | `v[1..2]` | ∅ | 300 | Ранний возврат, `SUCCESS` |
| 3 | N03-PLAIN | `sorting_q_pilot::n03_plain_no_merge` | `v[1..4]` | insert | 600 | Tails 1–2, `SUCCESS` |
| 4 | N04-PLAIN | `sorting_q_pilot::n04_plain_no_merge` | `v[1..5]` | insert | 600 | Tails 1–3, `SUCCESS` |
| 5 | N05-PLAIN | `sorting_q_pilot::n05_plain_no_merge` | `v[1..6]` | insert | 600 | Tails 1–4, `SUCCESS` |
| 6 | N06-PLAIN | `sorting_q_pilot::n06_plain_no_merge` | `v[1..7]` | insert | 600 | Tails 1–5, `SUCCESS` |
| 7 | N07-PLAIN | `sorting_q_pilot::n07_plain_no_merge` | `v[1..8]` | insert | 600 | Tails 1–6, `SUCCESS` |
| 8 | N10-PLAIN | `sorting_q_pilot::n10_plain_no_merge` | `v[1..11]` | swap, insert | 600 | Sort9 × 25, tail 9, `SUCCESS` |
| 9 | N11-PLAIN | `sorting_q_pilot::n11_plain_no_merge` | `v[1..12]` | swap, insert | 600 | Sort9 × 25, tails 9–10, `SUCCESS` |
| 10 | N14-PLAIN | `sorting_q_pilot::n14_plain_no_merge` | `v[1..15]` | swap, insert | 600 | Sort13 × 45, tail 13, `SUCCESS` |
| 11 | N15-PLAIN | `sorting_q_pilot::n15_plain_no_merge` | `v[1..16]` | swap, insert | 600 | Sort13 × 45, tails 13–14, `SUCCESS` |
| 12 | N02-PLAIN-QPOST-CORRUPT | `sorting_q_controls::n02_plain_qpost_corrupt` | `v[1..3]` | insert | 300 | Tail 1, `FAILURE` ровно `N02_CORRUPT_QPOST` |
| 13 | N17-PLAIN-QPOST-CORRUPT | `sorting_q_controls::n17_plain_qpost_corrupt` | `v[1..18]` | swap, insert | 600 | Sort13 × 45, tails 13–16, `FAILURE` ровно `N17_CORRUPT_QPOST` |

Для N00/N01 литеральный вызов проверяет равенство всего V34 и q-frame. У обоих есть `Q_ZERO`, `Q_MAX`, `USEFUL_RETURN`, у N01 также `Q_ABSENT` по `before[1] != q`. У остальных positives проверяются `order_target`/`order_post` на всём активном срезе, q-frame и byte frame вне него. Шесть covers используют активный вход для `Q_ABSENT` и ставят `USEFUL_RETURN` после проверок. Оба controls сохраняют по три covers, включая нулевой вход, q=1 на пути порчи и полезный возврат. При `--no-assert-contracts` actual sort13 идёт в `Original`, включая N14 и N15. Контрактный `requires(len == 17)` относится к контрактной обвязке.

## Профиль и границы

Normal cfg задаёт `kani_smallsort_sorting` и `kani_smallsort_q_pilot`. Используются CaDiCaL по умолчанию, `--exact`, `--jobs=1`, `--default-unwind 36`, `--no-assert-contracts`, `--object-bits 12`, пустые extra `cbmc_args` и отдельные Cargo/Kani target dirs на каждый root. В OFF-профиле сохраняются обычные memory/overflow/unwind checks.

Child budget с компиляцией — 6 900 с, из них 10 × 600 с и 3 × 300 с. При job 180 мин, setup/build ≤ 1 800 с и резерве завершения/upload 540 с номинально остаётся 1 560 с. Latest start для каждого корня — за 630 или 330 с до supervisor cutoff. Journal сохраняет lifecycle, PGID, component RSS, cleanup и первичную причину остановки. После остановки уже собранные записи сохраняются, невыполненные roots получают `NOT_RUN` с причиной.

Nominal child cap — 10 GiB (10 485 760 KiB), outer cap — 12 GiB (12 582 912 KiB), резерв — 2 GiB (2 097 152 KiB). Effective child cap — минимум nominal cap и бюджета process group по доступной памяти хоста и cgroup с вычетом резерва. Пределы на stdout/stderr/export — 16/1/8 MiB на корень, aggregate — 256 MiB с индексом. Сумма индивидуальных максимумов составляет 325 MiB. При фактическом превышении 256 MiB унаследованный validator отклоняет materialization и шаг upload пропускается.

## Офлайн-сверка

- `rustfmt --edition 2024 --check` прошёл на добавленных harnesses. Использован установленный `nightly-2026-11-19`, `rustfmt 1.12.0-nightly (65ce8611fe 2026-11-18)`. `git diff --check` прошёл для std и control.
- `validate` с синтетическими `GITHUB_*` подтвердил control commit/tree, единственного parent, event/ref/attempt, список payload и хеши. `check-source` подтвердил чистые std/tool checkout, commit/tree и SHA-256 всех шести std-файлов.
- `python3 -m unittest -v test_run.py` прошёл 14 из 14 тестов на подставных Python-процессах. Проверены exact roster и argv, отклонение дрейфа cfg/argv/лимитов, latest start обеих длительностей, отдельные target dirs, caps, cutoff, cleanup и существующие error paths.
- Сверены все 13 selectors, литеральные срезы, proof attrs, Replace и covers. В исходниках подтверждены ранние возвраты N00/N01, no-merge для остальных, 25 swap sites sort9 и 45 sort13, а также диапазоны tails. Для девяти новых Replace-маршрутов перебраны 52 472 входные пороговые маски на уровне сводок листьев. Перед каждой вставкой выполнен битовый q-Pre, итоговая маска совпала с `order_target`.

В qualification кампании 9 P‑1/P‑3 и N2/N8/N9/N12/N13/N16/N17 имеют статус `QUALIFIED` на прежнем pin. На новом std pin сверены побайтные тела, атрибуты и контракты, cfg и профиль. Геометрия новых вызовов укладывается в домены провайдеров, base1 и индексы <13 для P‑1, base1 и tails 1–16 для P‑3. При офлайн-разборе Pilot 10 остаётся подтвердить native bindings и успешные caller Pre для фактических Replace-вызовов, covers и свойства каждого корня. Результаты с Replace условны до подтверждения переноса. N00/N01 используют actual ранний возврат с пустым Replace. [Qualification Pilot 9](QUALIFICATION-RUN9.md) · [Чек-лист](QUALIFICATION-CHECKLIST.md)

Native результатов кампании 10 пока нет. Cargo, rustc, Kani, CBMC и CI не запускались. Пушей не было.
