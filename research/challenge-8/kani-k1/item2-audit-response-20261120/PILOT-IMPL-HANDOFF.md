# Handoff реализации q-пилота SmallSort N17

**READY_FOR_REVIEW** · native **NOT_RUN** · `GO=NOT_GRANTED` · `proof_credit=NONE`

Задание зафиксировано на `98029e90552445d89a152011475f2684b55d11ac`.
Два локальных кандидата по одному коммиту поверх заданных баз. У обоих
автор и коммитер `Tiramisu-Cake <igkharin@gmail.com>`, сообщение с `[skip ci]`.

| Вход | Локальный путь и ветка | Commit | Tree | Sole parent |
| --- | --- | --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1` · `experiment/ch8-q-pilot-v1` | `61d3f7c004b2edffc6ce9da454640def72691d5e` | `9303586b845bee4a0f7be9d847cb6f8fdfe496b9` | `7b31b060b90ce286e94547993f6a698c549bc5fa` |
| Fork control | `/root/kani-ch8-q-pilot-control-v1` · `experiment/ch8-q-pilot-control-v1` | `ba32286ee4f370593a2c9f0d8834a12d473c82d7` | `53b372008b70704b15a404275f81fa078ed50034` | `65a9ea656a4b5f1e66f7b31eceffb5eefeba7541` |
| Kani read-only | `/root/kani-upstream-ch8-s1` | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` | `3e095c22a231de1d7acd2410b71f0fc8e6970c19` |

Tree базы std `fccf3284bd678626c8f8cea72bbe6ec72964dbd9`.
Tree базы control `09938d27a127351f5c51b6c9f451602d797a1c0f`.
Шесть SHA-256 исходников std зафиксированы в `CI-REQUEST.json`.

| Control файл | SHA-256 |
| --- | --- |
| `.github/workflows/ch8-q-pilot.yml` | `6570df6f7b51b1f6fbde69cbc02a64ecd82e2abf9461d3fbc9932100bf26b07d` |
| `ch8-q-pilot-control/CI-REQUEST.json` | `a1967e0391e77e5ac5fdd5b4ed35ce0f47982e88acda19a45ef7298ebb6c70cc` |
| `ch8-q-pilot-control/run.py` | `7017c52d193dd8fae46fc63da0340b8e78bbd58a1058f876b314f2a4b288ebcb` |
| `ch8-q-pilot-control/test_run.py` | `b268631307a51a45520ca10225b7630803f936a7e589997884dddb50f441740e` |

## Конфигурации и вызовы

Общий префикс селекторов `slice::sort::shared::smallsort::verify::`.
Обычный q-профиль передаёт `--cfg=kani_smallsort_sorting --cfg=kani_smallsort_q_pilot`.
P-5a и P-5b дополнительно передают `--cfg=kani_smallsort_q_controls`.
`cfg(kani)` задаёт инструмент. Совместный S2/q-режим отклоняется при включённом sorting cfg.

| Корень | Нормальный q / mutant | Хвост селектора | Режим / verified stubs |
| --- | --- | --- | --- |
| P-1 | q | `sorting_q_pilot::p1_swap_u8_v34_q_any` | Check `swap_if_less` |
| P-2 | q | `sorting_q_pilot::p2_sort13_u8_b01_len17_q_any` | Check `sort13_optimal`, Replace `swap_if_less` |
| P-3 | q | `sorting_q_pilot::p3_insert_u8_b01_rel1_16_q_any` | Check `insert_tail` |
| P-4 | q | `sorting_q_pilot::p4_network_u8_b01_n17_q_any` | Actual network и insertion loop, Replace `sort13_optimal`, `insert_tail` |
| P-5a | mutant | `sorting_q_controls::p5_swap_false_or_q_any` | Check `swap_if_less` с false-OR |
| P-5b | mutant | `sorting_q_controls::p5_swap_false_or_q_fixed0` | Тот же Check, q-domain `{0}` |
| P-5c | q | `sorting_q_controls::p5_network_n17_qpost_corrupt` | Те же Replace и actual вызовы, что у P-4 |

- **P-1 → P-2.** Для `u8/KeyLess<u8>` в initialized V34 P-1 охватывает base 0–20 и
  независимо a,b 0–12, включая совпадение. P-2 вызывает все 45 пар на base 1.
  Swap summary сохраняет q, меняет только два адреса и задаёт AND/OR для текущего q.
- **P-2 → P-4/P-5c.** При base 1 и len 17 post задаёт order-stat для первых 13
  элементов. Havoc ограничен ими. Capture хранит порог, готовый булев target и байты
  хвоста `V34[14..18]`. Harness проверяет также все внешние байты.
- **P-3 → P-4/P-5c.** P-3 охватывает base 1 и relative tails 1–16 с тем же
  `all_u8` по q и условием q-монотонности `[begin, tail)`. Actual N17 после
  sort13 проходит tails 13–16 в `insertion_sort_shift_left`. Replace проверяет
  `insert_pre`, затем вводит piecewise q-shift post. Modifies охватывает ровно
  inclusive span. Все fixtures используют полные символьные байты V34.
- **Контроли.** P-5a ожидает единственное назначенное нарушение `swap_false_or_post`
  при разных индикаторах. P-5b ожидает native SUCCESS и отдельно синтетический
  `Q_DOMAIN_NOT_UNIVERSAL`. P-5c вызывает actual N17 и пишет 255 в `V34[1]`,
  когда входной region был полностью нулевым. При q=1 в этой позиции до записи
  возможен только 0. Назначенная property — `P5C_CORRUPT_QPOST`.
  Exact labels, source sites, cover map и зависимости зафиксированы в `CI-REQUEST.json`.

## Предлагаемый envelope

Будущий trigger ref `uninit-ci/ch8-q-pilot-v1` в `Tiramisu-Cake/kani`.
Один exact root на процесс, jobs1, unwind36, object-bits12, штатный CaDiCaL.
Loop contracts, quantifiers, uninit и validity OFF.
Setup с build ≤1800 с, build ≤900 с. На root compile ≤180 с, child ≤600 с,
slot ≤720 с. Семь roots дают 4200 с child и 5040 с слотов.
Campaign ≤6900 с, outer ≤7500 с, step ≤7560 с, phase ≤8100 с, job ≤180 мин.
Номинальный local RSS ≤6 GiB и outer ≤12 GiB с запасом 2 GiB. Stdout 16 MiB,
stderr 1 MiB и export 8 MiB на root, итоговый артефакт ≤256 MiB.
Исследовательская цель для P-2 и P-4 — child ≤300 с на каждый.

## Локальные проверки std

- `git diff --check HEAD^ HEAD` — PASS. У каждого из шести файлов проверен scope.
- Python static check — восстановили исходник байт в байт после удаления семи q-атрибутов
  и нормализации 12 safety guards. Прежняя часть `verify.rs`, тела `call_once/call_mut`
  и остальная модель тоже совпали с базой. Сверены 32 строки таблицы cfg.
- Из исходника извлечены 45 пар `sort13_optimal`, все входят в домен P-1.
  Синтетическая AND/OR модель сети отсортировала все 8192 входных битовых вектора N13.
  Путь N17 до tails 13–16 и возврата перед merge сверён статически.
- На шести изменённых .rs выполнен локальный check-only
  `LD_LIBRARY_PATH=/root/rustfmt-toolchains/nightly-2026-11-19/lib /root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --check --edition 2024 --config skip_children=true,use_small_heuristics=Max --unstable-features FILE`.
  В std pin корневого `rustfmt.toml` нет. Три новых файла прошли с кодом 0.
  Для `smallsort.rs`, `verify.rs` и `sorting_model.rs` код 1 и строки
  предложенного diff совпали с проверкой тех же файлов в базе.

## Локальные проверки control

- `git diff --check HEAD^ HEAD` — PASS. В diff только workflow и три файла control.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ch8-q-pilot-control -p test_run.py -v`
  — 14/14 PASS. Проверены exact singleton argv, закрытый cfg, отказ при повреждённых pins
  и переставленных roots, q-domain gate, согласование stock и regular inventory,
  точные sites и неоднозначность, initial marker, missing/null/wrong-type/partial export,
  `NOT_RUN` fallback, original exit, timeout и verified reap.
- Дополнительный процессный тест с Python подтвердил сохранение exit 7, cutoff с
  signal и cleanup, а также reap отсоединённого потомка на slot cutoff.
- `run.py check-source --std /root/verify-rust-std-ch8-q-pilot-v1 --tool /root/kani-upstream-ch8-s1`
  — MATCH. С g0 вместо кандидата — ожидаемый exit 1 и `std identity mismatch`.
- `run.py validate --repo .` с локальными значениями `GITHUB_REPOSITORY=Tiramisu-Cake/kani`,
  `GITHUB_EVENT_NAME=push`, точным ref, SHA control и `GITHUB_RUN_ATTEMPT=1` — STATIC_PASS.
  Отдельно проверены YAML scalar types, единственный push ref/job, permissions, сериализация
  и upload только `q-pilot-results.json`. JSON schema, типы, source spans и hashes сверены
  против закреплённых деревьев.

## Открытые проверки

Регистрация, компиляция, применимость Check/Replace на конкретных
инстанцированиях, native property bindings, семь native verdicts и timings
остаются `NOT_RUN`. Статическая сверка режимов опирается на исходники пина Kani.
При отсутствии однозначной native привязки runner оставляет роль `UNKNOWN`.
RSS наблюдается по периодическим выборкам группы процессов и дерева владения.
Из внешнего лимита слота зарезервировано 8 с на reap.

Перед dispatch нужны [независимое ревью](PILOT-REVIEW-TASK.md), доступный координатору
для fetch точный std SHA, сверка trigger tree и sole parent, отдельные GO, окно и ledger.
Публикация, CI и native инструменты на этой стадии `NOT_RUN`.
