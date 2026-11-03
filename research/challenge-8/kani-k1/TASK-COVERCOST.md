# COVERCOST — память kani-driver у композиции u64 N10 без covers (диагностика)

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-covercost**, ветка **experiment/kani-k1-covercost-20261103** от
  **5737fa738bac360f19dd0113b2b8640f16bea5f5** (terminal U64-TEN-CALLER).
- Slug **covercost**, stable owner **k1-merge**. Запускать только после terminal/accounting PERMPROBE: это тот же owner.
  Новые stage/ledger/UUID/request_id `covercost-*`. Чужие ledgers (ROUTESAB, k1-network) не трогать.
- Project cap **$88.96**, свой cap **$0.60**. **Один Build**, retry нет. Исключение — один compile-error repair с
  новым review/GO, если own spent + reserve ≤ cap.
- Окно: main 90 мин + closeout 30 мин.

## Вопрос

В U64-TEN-CALLER ([RESULT](research/challenge-8/kani-k1/RESULT-U64-TEN-CALLER.md)) положительная гармоника
`tenleaves::caller::u64tencall_positive_u64_n10` упала по OOM:
- kani-driver вырос до 15.3 GB, тогда как CBMC держал около 2.7 GB;
- driver был около 7 MiB до ~270 с, затем рос ~0.77 GiB / 30 с, пока работал CBMC.

Гипотеза: память driver растёт из-за обработки вывода CBMC, связанного с covers и трассами. Проверяем её одним
диагностическим root **без covers**. Это только измерение памяти: proof credit нет, исходные reachability obligations
не заменяются.

## Source scope

В том же модуле `caller.rs` (или в новом child-файле рядом — выбрать наименее инвазивное и обосновать в PREBUILD)
добавить **один** root **`u64tencall_positive_nocover_u64_n10`**. Он должен быть точной копией
`u64tencall_positive_u64_n10`:
- те же `#[kani::proof]`, `#[kani::stub]`, `#[kani::stub_verified]`, unwind;
- те же inputs, probe, context, asserts и их порядок.

Единственное отличие — удалены все `kani::cover` **в теле этого root**. Если covers стоят в общих helpers или
adapters, их **не трогать**: перечислить в PREBUILD, сколько covers останется достижимыми. Тело по возможности
вынести в общий helper без изменения исходного root. Если исходный root при этом меняется хоть на байт — так не
делать, а дублировать тело.

Неизменно:
- исходный positive, controls, leaves, adapters, профили, runtime, tooling, pins;
- ordinary 202 и PFC 36;
- static cfg-on +1 имя, проверить exact delta.

## Пакет G1

Одна строка: `...::tenleaves::caller::u64tencall_positive_nocover_u64_n10`.

- Kind **diagnostic**, если tooling 30f77e85 допускает diagnostic с `controls:true` на standard4 и без требования
  covers. Сверить с `tools/kani_k1.py` до GO.
- Если допустим только measurement с обязательным ≥ 1 cover — стоп и ко мне. Covers обратно не добавлять, tooling не
  менять.
- gcb-e2-standard-4, kani_jobs:1, uninit_checks:false, harness_timeout_minutes:10.
- Kani 9461e07a, frozen tooling 30f77e85, check-tooling.
- Резерв **(10+30)×$0.0135 = $0.540 ≤ cap $0.60**.

Project ≤ 2 unfinished Builds, ≤ 1 на k1-merge. Global spent + reserves ≤ $88.96.

PRE-BUILD содержит:
- byte-diff исходного root против клона (только удалённые covers);
- список оставшихся достижимых covers в helpers;
- неизменность остального;
- hashes и budget/slots.

Library и research коммиты отдельно, `[skip ci]`, push без force. Последней строкой `PRE-BUILD REVIEW <sha>`, стоп
до GO. Ждать `k1g.sh wait BUILD` в фоне (run_in_background) и завершить ход.

## Что измерить и RESULT

Статус (SUCCESS / FAILED / TIMEOUT / OOM) и VT. Пики по процессам: kani-driver (time -v и sampled), CBMC,
process-sum, wall. Рост driver во времени, если он есть в bounded peaks. dmesg OOM.

**RESULT-COVERCOST.md**, ≤ 30 строк, сравнение с U64-TEN-CALLER G1 (driver 15.29 GB OOM, CBMC ~2.7 GB):
- **driver ≪ 15 GB, SUCCESS** → covers/трассы — главный источник памяти. Positive с covers на 16 GB остаётся OPEN;
  дальше это решает координатор: covers можно вынести в отдельный reachability-root.
- **Снова OOM или driver растёт так же** → covers не причина. Гипотеза снята, композиция u64 N10 на 16 GB — барьер.
- **SUCCESS без covers** — не доказательство теоремы с исходными obligations. Писать «diagnostic, no proof credit».

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **COVERCOST ЗАВЕРШЁН**, одна стадия, затем стоп.
