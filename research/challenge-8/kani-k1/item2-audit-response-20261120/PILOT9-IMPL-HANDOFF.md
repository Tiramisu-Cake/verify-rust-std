# Кампания 9 q-пилота — handoff реализации

Подготовлен локальный пакет для одного setup/build и последовательного сбора результатов по 15 exact roots на одном std pin. В пакет входят 10 positives и 5 controls. Request имеет статус `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Для запуска нужны отдельное ревью и GO координатора. [Задание](PILOT9-IMPL-TASK.md) · [Офлайн qualification](QUALIFICATION-CHECKLIST.md)

## Пины

| Объект | Worktree и ветка | Commit | Tree |
| --- | --- | --- | --- |
| Control | `/root/kani-ch8-q-pilot-control-v9`, `experiment/ch8-q-pilot-control-v9` | `baad011375b727383f7ea0abe429763c1a78ab13` | `f4fc5af6131e0418236ff65f4d2282358a0e58ee` |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `d968b9a8c341485e4df63ad852ac0806f37bb71b` | `d8eaa9033b531e8be2413599e19315f294c5aafb` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Единственный parent control — `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Дельта к v8 `f8399974170e0a85b0e20b7bc2290431fb47c357` состоит из request, roster в `run.py` и fixture expectations в `test_run.py`. Workflow из v8 закреплён побайтно, включая прежнее имя шага `Run seven q-pilot roots`. Порядок корней задаёт request. Event ref — `refs/heads/uninit-ci/ch8-q-pilot-v1`.

Единственный parent std — `1b82e2a9a70f0712986fab263c5e336e6edef3ca`, tree базы — `8d66a57644630c07fb19e0948b48c3e3e2fc8441`. Дельта добавляет harnesses в `sorting_q_pilot.rs` и `sorting_q_controls.rs`. Существующие harnesses, атрибуты, регистрация, модели и runtime совпадают с базой.

| Файл control | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `b68f21c2a8ed5e1be22fa026aebd45f72e314dc4cdad11c5b95ed61ca83b822b` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `95d479a3be0323e71f80f70fc124f028fc2b295b3cdc3bd4fc49b6e09d60b8e1` |
| `ch8-q-pilot-control/test_run.py` | `3fbd74e30c0068aeb4e492bef67470bdf5f3ebed5aa5b0121b15fda0f77d9667` |

Пути в таблице std относительны к `library/core/src/slice/sort/shared/`.

| Файл std | SHA-256 |
| --- | --- |
| `smallsort.rs` | `200f4832551309317ecc3786df9aa5943434b8d25a2b58f869b554f0080c8ceb` |
| `smallsort/verify.rs` | `24e4b3042118d8904824a21dd72c46e7fc9384ef512f3bd10b412b4493d6177d` |
| `smallsort/verify/sorting_model.rs` | `dec45747dde28e0861becf4c0c089d2a9899ad035db30e9967d0a0041845fb88` |
| `smallsort/verify/sorting_q_model.rs` | `5e5eac5ad26d1352df52b659a12eb5396ef23872f724c1b460441eb6a37520f0` |
| `smallsort/verify/sorting_q_pilot.rs` | `5d227cd73ec644c27eacf0aec5d66f2a2793f9fb4137cfe093c78b81a0f5a9f8` |
| `smallsort/verify/sorting_q_controls.rs` | `0ee56705b083f7610b764bc8bc164a81eae94de9229b33baf0169f6c7b8df9ff` |

## Roster

У всех selectors общий префикс `slice::sort::shared::smallsort::verify::`. PFC означает `proof_for_contract`. В колонке Replace перечислены verified stubs, ordinary stubs везде пусты. Последняя колонка содержит ожидания для последующего разбора.

| № | ID | Суффикс exact selector | Cfg / режим | Replace | Child, с | Ожидание и маршрут по исходникам |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | P-1 | `sorting_q_pilot::p1_swap_u8_v34_q_any` | normal / PFC swap | ∅ | 600 | SUCCESS. `q:any`, V34, base 0–20, оба индекса <13 |
| 2 | P-3 | `sorting_q_pilot::p3_insert_u8_b01_rel1_16_q_any` | normal / PFC insert | ∅ | 600 | SUCCESS. `q:any`, V34/base1, tails 1–16 |
| 3 | N17-PLAIN-STUB-SWAP-INSERT | `sorting_q_pilot::n17_plain_stub_swap_insert` | normal / Proof | swap, insert | 600 | SUCCESS. sort13 × 45 swap, tails 13–16 |
| 4 | N17-PLAIN-QPOST-CORRUPT | `sorting_q_controls::n17_plain_qpost_corrupt` | normal / Proof | swap, insert | 600 | FAILURE по `N17_CORRUPT_QPOST` |
| 5 | P-5a | `sorting_q_controls::p5_swap_false_or_q_any` | mutant / PFC swap | ∅ | 600 | FAILURE по роли `swap_false_or_post`, split cover до swap |
| 6 | P-5b | `sorting_q_controls::p5_swap_false_or_q_fixed0` | mutant / PFC swap | ∅ | 600 | Native SUCCESS при q=0, офлайн gate `Q_DOMAIN_NOT_UNIVERSAL` |
| 7 | N01-PLAIN | `sorting_q_pilot::n01_plain_no_merge` | normal / Proof | ∅ | 300 | SUCCESS. Ранний возврат для N0 и N1, весь V34 равен входу |
| 8 | N02-PLAIN | `sorting_q_pilot::n02_plain_no_merge` | normal / Proof | insert | 300 | SUCCESS. Tail 1 |
| 9 | N08-PLAIN | `sorting_q_pilot::n08_plain_no_merge` | normal / Proof | insert | 600 | SUCCESS. Tails 1–7 |
| 10 | N09-PLAIN | `sorting_q_pilot::n09_plain_no_merge` | normal / Proof | swap | 600 | SUCCESS. sort9 × 25 swap, 0 вставок |
| 11 | N12-PLAIN | `sorting_q_pilot::n12_plain_no_merge` | normal / Proof | swap, insert | 600 | SUCCESS. sort9 × 25 swap, tails 9–11 |
| 12 | N13-PLAIN | `sorting_q_pilot::n13_plain_no_merge` | normal / Proof | swap | 600 | SUCCESS. sort13 × 45 swap, 0 вставок |
| 13 | N16-PLAIN | `sorting_q_pilot::n16_plain_no_merge` | normal / Proof | swap, insert | 600 | SUCCESS. sort13 × 45 swap, tails 13–15 |
| 14 | N02-PLAIN-QPOST-CORRUPT | `sorting_q_controls::n02_plain_qpost_corrupt` | normal / Proof | insert | 300 | FAILURE по `N02_CORRUPT_QPOST` |
| 15 | N13-PLAIN-QPOST-CORRUPT | `sorting_q_controls::n13_plain_qpost_corrupt` | normal / Proof | swap | 300 | FAILURE по `N13_CORRUPT_QPOST` |

Plain-маршруты используют exact `u8/KeyLess<u8>`, независимые V34 и `q:any`, base1 и длины до merge. При `--no-assert-contracts` actual sort13 в N13/N16 идёт в режиме `Original`, а `len == 17` относится к его контрактной обвязке. Геометрия вызовов сверена по исходникам. Native caller Pre, привязка свойств, covers и qualification подлежат сверке по evidence будущего запуска.

## Профиль и бюджет

`normal` задаёт `kani_smallsort_sorting` и `kani_smallsort_q_pilot`, `mutant` добавляет `kani_smallsort_q_controls` только для P-5a/b. Все команды используют `--exact`, `--no-assert-contracts`, `--jobs=1`, unwind36, CaDiCaL по умолчанию, `--object-bits 12`, пустой список extra `cbmc_args` и отдельные target dirs на root. Профиль OFF для uninit, validity и extra pointer checks. Loop contracts и quantifiers отсутствуют. Regular stdout/stderr и stock export собираются по формату v8.

Child budget — 7 800 с (11 × 600 с и 4 × 300 с), включая std compile. Job — 180 мин, setup/build — до 1 800 с от setup epoch, резерв завершения/upload — 540 с. Номинально остаётся 660 с. Latest start приходится на 630 или 330 с до supervisor cutoff. Stop reason сохраняется, а оставшиеся корни получают `NOT_RUN` по данным lifecycle.

Лимиты памяти — 10 GiB (10 485 760 KiB) nominal child, 12 GiB (12 582 912 KiB) outer, резерв 2 GiB (2 097 152 KiB). Effective child cap — минимум nominal child cap и бюджета process group по доступной памяти хоста и cgroup с вычетом резерва. Receipt включает оба child cap, отдельный outer cap, sampled PGID и component RSS, start/exit/signal и cleanup.

Пределы stdout/stderr/export — 16/1/8 MiB на корень, общий предел — 256 MiB вместе с индексом `q-pilot-raw.json`. При 15 корнях сумма индивидуальных максимумов достигает 375 MiB. Если фактический суммарный объём превысит 256 MiB, унаследованный validator отклонит итоговый артефакт на шаге materialization, от которого зависит upload.

## Локальные проверки

- `check-source` сверил чистые точные std/tool checkout, commit/tree и SHA-256 всех шести std-файлов.
- `validate` с синтетическими GitHub metadata подтвердил control commit/tree/parent, event/ref/attempt, состав изменённых файлов и хеши payload.
- `python3 -m unittest -v test_run.py` прошёл 14 из 14 тестов на подставных Python-процессах. Покрыты порядок всех 15 roots, обе cfg, оба таймаута в argv и latest start, отдельные target dirs, caps, отклонение дрейфа roster/профиля, cleanup, cutoff и fallback.
- Сверены дельта из добавлений в двух std-файлах, побайтное совпадение прежних harnesses, соответствие selectors/cfg/режимов/Replace исходникам, границы sort9/sort13 и insertion loop. Прошли `rustfmt --edition 2024 --check` из `nightly-2026-10-23` для добавленного кода и `git diff --check`.

Native результаты для этого пакета пока отсутствуют. Cargo, rustc, Kani, CBMC и CI не запускались. Пушей не было. Ожидаемые native статусы из roster, итог qualification и решение о допуске сохраняются как раздельные записи.
