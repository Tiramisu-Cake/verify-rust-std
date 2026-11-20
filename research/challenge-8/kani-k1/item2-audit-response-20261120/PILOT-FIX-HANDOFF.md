# Передача исправленного q-пилота

**`READY_FOR_DELTA_REVIEW`** · `native=NOT_RUN` · `GO=NOT_GRANTED` · `proof_credit=NONE`.

Основание — задание на g0 `5eee65bcc9daf6dd5f48f67d199e19b87ecaad20`, решение координатора и вердикт `CHANGES_REQUIRED`. Для оценки будущих наблюдений применяется закреплённый офлайн-чек-лист. [Задание](PILOT-FIX-TASK.md) · [Решение](FIX-DIRECTION.md) · [Ревью](PILOT-REVIEW.md) · [Чек-лист](PILOT-ANALYSIS-CHECKLIST.md)

## Закреплённый пакет

| Worktree | Ветка | Commit | Tree | Единственный parent |
| --- | --- | --- | --- | --- |
| `/root/verify-rust-std-ch8-q-pilot-v1` | `experiment/ch8-q-pilot-v1` | `5544e01921d5c67c21d4ab919e8f76b43f884d92` | `551a7300bb76807dc80efd56f9e1603e19706c84` | `61d3f7c004b2edffc6ce9da454640def72691d5e` |
| `/root/kani-ch8-q-pilot-control-v1` | `experiment/ch8-q-pilot-control-v1` | `876a75ca9f7e78ddb2e98bd9ff5b7ed1314feb8f` | `3cead694cbc4ae70b39be2a6b5f12284838305bb` | `ba32286ee4f370593a2c9f0d8834a12d473c82d7` |
| `/root/kani-upstream-ch8-s1` | detached, read-only | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` | `3e095c22a231de1d7acd2410b71f0fc8e6970c19` |

Оба коммита исправлений локальные, с `[skip ci]`. Автор и коммитер — `Tiramisu-Cake <igkharin@gmail.com>`.

| Файл control | SHA-256 |
| --- | --- |
| `.github/workflows/ch8-q-pilot.yml` | `9dbe69d506737cea41b18e01c72d19d26eb93ca24e36be7e49f22b4e6324f39e` |
| `ch8-q-pilot-control/CI-REQUEST.json` | `827d58e5e4981ca4ee9d51f02a353b176365930e0c0c024cc1c81945c1be94b9` |
| `ch8-q-pilot-control/run.py` | `913c2c8e9024ac3ff3148b748afcd36116bfa9c0474b5468a208bf7b2ac15f0b` |
| `ch8-q-pilot-control/test_run.py` | `e15ee2df72bfca9f102463848e07c27bea9c25329e6eba761e61eccfa94a4f19` |

После delta review координатор привязывает GO и ledger к проверенному control tree, его единственному parent и SHA-256 request из таблиц. Для будущего same-tree trigger он сверяет эти три значения, оба source pins и хэши payload до dispatch. Runner повторно сверяет `HEAD` с `GITHUB_SHA`, проверяет parent, чистоту трёх checkout и payload, а в index пишет фактические tree и хэши request/workflow. Доступность точного std SHA для будущего fetch и привязка будущего trigger остаются непроверенными.

## Карта std

Пути ниже относительны к `library/core/src/slice/sort/shared/` в std worktree. `rustfmt` также перенёс строки нескольких соседних вызовов.

| Точка | Файл и строки |
| --- | --- |
| `P1_Q_ABSENT`, оба сравниваемых байта из `before` | `smallsort/verify/sorting_q_pilot.rs:57–60` |
| `P2_Q_ABSENT`, `before[1..14]` | `smallsort/verify/sorting_q_pilot.rs:91` |
| `P3_Q_ABSENT`, `before[1..1 + len]`, включая tail при `len = tail + 1` | `smallsort/verify/sorting_q_pilot.rs:106,150` |
| `P4_Q_ABSENT`, `before[1..18]` | `smallsort/verify/sorting_q_pilot.rs:190` |
| P-5a, geometry и guarded `P5_SWAP_SPLIT_THRESHOLD` до actual swap, затем `P5_SWAP_USEFUL_RETURN` | `smallsort/verify/sorting_q_controls.rs:20–30,41,47–49` |
| P-5a/b, mutant ensures `swap_false_or_post` и его определение | `smallsort.rs:461`, `smallsort/verify/sorting_q_model.rs:176–185` |
| P-5b, фиксированные `q=0` и `cover_split_threshold=false` | `smallsort/verify/sorting_q_controls.rs:52–56` |
| P-5c, порча, `P5C_ALL_ZERO_INPUT`, `P5C_Q_ONE_CORRUPTION_PATH` и `P5C_CORRUPT_QPOST` | `smallsort/verify/sorting_q_controls.rs:71–79,88–91` |

### Exact roster в очереди запуска

| Root | Selector | Cfg |
| --- | --- | --- |
| P-1 | `slice::sort::shared::smallsort::verify::sorting_q_pilot::p1_swap_u8_v34_q_any` | normal |
| P-2 | `slice::sort::shared::smallsort::verify::sorting_q_pilot::p2_sort13_u8_b01_len17_q_any` | normal |
| P-3 | `slice::sort::shared::smallsort::verify::sorting_q_pilot::p3_insert_u8_b01_rel1_16_q_any` | normal |
| P-4 | `slice::sort::shared::smallsort::verify::sorting_q_pilot::p4_network_u8_b01_n17_q_any` | normal |
| P-5a | `slice::sort::shared::smallsort::verify::sorting_q_controls::p5_swap_false_or_q_any` | mutant |
| P-5b | `slice::sort::shared::smallsort::verify::sorting_q_controls::p5_swap_false_or_q_fixed0` | mutant |
| P-5c | `slice::sort::shared::smallsort::verify::sorting_q_controls::p5_network_n17_qpost_corrupt` | normal |

Normal — `--cfg=kani_smallsort_sorting --cfg=kani_smallsort_q_pilot`. Mutant добавляет `--cfg=kani_smallsort_q_controls`. Request фиксирует полный singleton argv и подстановки локальных путей. Runner формирует окружение child из разрешённого списка системных переменных и закреплённых flags. Каждый root получает отдельные CLI `--target-dir`, `CARGO_TARGET_DIR` и `TMPDIR`. Область временных файлов удаляется после подтверждения очистки. [CI-REQUEST.json](/root/kani-ch8-q-pilot-control-v1/ch8-q-pilot-control/CI-REQUEST.json)

## Схема `q-pilot-raw.json`

| Блок | Наблюдения |
| --- | --- |
| Запуск | `schema=ch8-q-pilot-raw-v1`, `proof_credit=NONE`, GitHub run ID/attempt/event/ref/trigger SHA, фактические `identities`, `last_validated_inputs`, `setup` с receipt и SHA-256 или причиной, `limits`, `job_boundary`, исходы шагов и `stop_reason` с ошибкой при наличии. |
| Корень | ID, selector, cfg, фактически переданный argv при подтверждённом старте, `invocation` с ID и путями, `started` с PID и двумя часами, `child` с моментом получения исхода, монотонным wall через cleanup, исходными exit/signal, timeout/cutoff и sampled RSS/областью. `worker_exit_code`, `supervisor`, `supervisor_cleanup_verified` и `temp_cleanup` записываются отдельно. |
| Файлы | До трёх членов под каталогом ID корня. `stdout.log`, `stderr.log` и `export.json` получают относительный путь, длину и SHA-256 сохранённых байтов, cap, truncation и `snapshot_after_reap`. При отсутствии есть причина, при ошибке чтения — её тип и сообщение. Для malformed export может присутствовать `decode_error`. Значения JSON сохраняются побайтно. |

Внутренний журнал атомарно фиксирует успешный `Popen`, получение исхода child до чтения export и полученный supervisor receipt. При прерывании между `Popen` и записью старта состояние может остаться `UNKNOWN`. При записанном старте без outer receipt fallback сохраняет известные наблюдения с `INTERRUPTED` и `supervisor_cleanup_verified: null`. `NOT_RUN` требует известной причины отсутствия запуска. Hard stop GitHub может прервать финализацию и upload, оставив пробел в наблюдениях.

Child получает 600 с вместе с компиляцией. Основание границы запуска — монотонная отметка первого шага и job cap 180 мин. От последнего разрешённого старта до расчётного job cap предусмотрены 600 с для одного child, 30 с для подготовки и reap и 540 с для завершения, fallback и upload. Supervisor использует общий job cutoff с полями helper для фактического elapsed и sampled RSS. Отметка первого шага задаёт расчётную границу на runner, а GitHub отдельно применяет жёсткий job timeout. Штатные лимиты setup/build — 1800/900 с.

Префиксы stdout/stderr сохраняются в исходном порядке. Caps на корень — 16/1/8 MiB для stdout/stderr/export. Перед upload проверяются обычные файлы, отсутствие symlink, точный состав, размеры и SHA-256 членов. Общий предел 256 MiB включает index. Upload берёт отдельный каталог артефакта после успешной проверки.

## Выполненные проверки

- `git diff --check` для обеих дельт и сверка локальных веток, HEAD/tree/parent, авторства, состава файлов, SHA-256 и чистоты, включая untracked. Control `validate` прошёл на закоммиченном пакете с синтетическими GitHub metadata. `check-source` прошёл на двух фактических checkout.
- `rustfmt --edition 2024 --check` указанным локальным rustfmt с заданным `LD_LIBRARY_PATH`. Статическое сравнение std дельты подтвердило четыре covers по owned `before` и перенос прежнего guarded cover. Проверены семь селекторов, unwind36 и выбор cfg. YAML, argv и JSON request проверены статически.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_run.py` — **9/9**. Использовались временные Git checkout и малые Python-процессы. Проверены порядок и точный argv/cfg, изоляция target dirs, wrong SHA/tree и untracked drift, timeout с исходными exit/signal и reap отсоединённого потомка, job cutoff с `NOT_RUN`, продолжение после локального отказа и остановка при неподтверждённом reap.
- Проверки итогового index охватили malformed/missing/read-error export, JSON `null`, scalar, `INCOMPLETE`, `PARTIAL` и `COMPLETE`, байтовые caps, хэши и точный состав, а также fallback с setup receipt и `started` без outer receipt.

Следующая стадия — независимое delta review этого пакета.
