# CAL1 · пакет диагностики pr752

`READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Пакет подготовлен локально для одного fork run. В control внесены исправления по четырём блокерам ревью `d2fb3e493c`. Следующая стадия — повторный независимый review. [Задание](CAL1-IMPL-TASK-20261123.md) · [Ревью](CAL1-REVIEW.md) · [Frozen request](/root/kani-cal1-control-w11/ch8-cal1/CI-REQUEST.json)

## Идентичность и trigger

| Объект | Commit | Tree | Parent |
| --- | --- | --- | --- |
| std base | `dab03cf510df5c35141cde49f1368b1242f5035e` | `7fd542ad59723ff2beeacb9632fb0568e81b0655` | `1d2706e31f0cd909bd784fa43adf9a1d55be8469` |
| std overlay | `6e5b28070d72adefae7c259c6f33ffcebcd9a314` | `d4ab1d4f0749019d9f5568bfc4c62e54066de4a2` | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| Kani stock | `9834c96ce90ff57d8495416530b080dc3d52ce25` | `938e9932cb2127239afb4f093f6302652c053398` | `70d7da0ae18991f9604d299784b974a43636945a` |
| Control CAL1 | `496851502d6fa6c773472ddc1981b62c9d948f3a` | `f85bab20a00b5651050733c1e2d5aedff24d140e` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| g0 задания | `00d3fd3df44358ef9462aab4c99ceff6d3aa08a3` | `ee304db27f6a161b7e4327caee86d78abdf2e8f4` | `39afc8dcdda99b5ab81799566620c06ba180660b` |

- Std overlay находится в [verify-rust-std-cal1-w11](/root/verify-rust-std-cal1-w11), control в [kani-cal1-control-w11](/root/kani-cal1-control-w11). Оба checkout detached. [Bundle](/root/kani-cal1-control-w11/ch8-cal1/std-overlay.bundle) содержит только объекты overlay поверх std base. Workflow проверяет SHA-256 bundle, импортирует объекты без ref, сверяет commit/tree/parent и снимает cfg-off список на std base до переключения в detached overlay.
- Целевой fork `Tiramisu-Cake/kani`, событие `push`, единственный ref `refs/heads/uninit-ci/ch8-q-pilot-v1`. Единственная форма trigger после решения координатора — `git commit-tree f85bab20a00b5651050733c1e2d5aedff24d140e -p 467af9cb8dba0e3be78a8d7d07672a1943c4806b` с сообщением без `[skip ci]`. Ожидаемый tree полностью совпадает с Control CAL1. Workflow на обоих jobs проверяет fork, event и полный ref, а runner проверяет push SHA и единственного родителя. [Workflow](/root/kani-cal1-control-w11/.github/workflows/ch8-q-pilot.yml)
- При подготовке исходного пакета `git ls-remote` показал на заданном ref `6e2922538d721509e9788d00298e07a2ad99d6b7`, прямого потомка того же `467af9cb8d`. Будущий trigger будет соседним коммитом, поэтому fast-forward с того head невозможен. Решение о состоянии дорожки остаётся у координатора. Подготовительные коммиты локальны.

SHA-256 frozen request — `de9d0586b681c86cfb85aff85eec8c5450e3d3caaad2a3101f2af60bdb9a4cfc`. SHA-256 std bundle — `4de024a3b2f844c186be8271c24ef757d402d94098c3e1b07b12a7e22dc610e8`.

## Overlay и frozen roster

Guard восстанавливает исходные `smallsort.rs`, `verify.rs` и `core/Cargo.toml` удалением добавленных опциональных атрибутов, деклараций четырёх модулей и одной записи `check-cfg`. Остальные tracked файлы исходной std, в том числе штатные script, workflow и tool pin, сохраняются побайтно. Все строки используют `RUSTFLAGS=--cfg=kani_smallsort_cal1`. [Guard](/root/kani-cal1-control-w11/ch8-cal1/request.py)

Полный префикс каждого селектора — `slice::sort::shared::smallsort::verify::`. Исходные cover labels зафиксированы в roster.

| ID | Суффикс селектора | Роль | Unwind | Слот, с |
| --- | --- | --- | ---: | ---: |
| NET-U8-N08 | `cal1_direct::cal1_net_u8_n08` | Original, вставки | 40 | 300 |
| NET-U8-N09 | `cal1_direct::cal1_net_u8_n09` | Original, sort9 | 40 | 300 |
| S13-N13 | `cal1::nm_sort13_left_len13` | Check `sort13_optimal` | 36 | 1080 |
| S13-N17 | `cal1::nm_sort13_left_len17` | Check `sort13_optimal` | 36 | 1080 |
| S13-N32-R | `cal1::mw_sort13_right_b17_len16` | Check `sort13_optimal` | 36 | 1080 |
| MERGE-N32 | `cal1::mw_merge_n32` | Check `bidirectional_merge` | 36 | 780 |
| NET-N25 | `cal1::compact_network_n25_actual_insert` | Replace `sort9_optimal`, `sort13_optimal`, `bidirectional_merge` | 36 | 480 |
| NET-U64-N13 | `cal1_direct::cal1_net_u64_n13` | Original, sort13 | 40 | 720 |
| NET-U64-N32 | `cal1_direct::cal1_net_u64_n32` | Original, sort13, вставки, merge, copy-back | 96 | 1080 |
| GEN-N16-SMALL | `cal1_direct::cal1_gen_u64_n16_small` | Original, general scratch48 и два sort8 | 96 | 720 |
| GEN-N16-WIDE | `cal1_direct::cal1_gen_wide_n16` | Original, general scratch48 и два sort4 | 96 | 720 |

- S13 переносит q-post и запись в первые 13 элементов для `V34/base1/len13`, `V34/base1/len17` и `V34/base17/len16` из `3fff6aa0db` и `e2bd3c6adc`. Check выполняет реальные swaps. N32 merge сохраняет две численно упорядоченные половины 16+16, отдельный writable scratch32, исходный frame и observer `54123e752d`. Observer считает входы `<q` в `u8` и сверяет предикат на каждой из 32 позиций.
- N25 переносит `bfa60b19cc`, включая ветку insertion на левой половине длины 12 и реальный copy-back. Для N25 сохранена исходная маска q, компактный observer применяется при длине 32. Зарегистрированы два дополнительных Check для sort9 и merge N25. Они участвуют в discovery и исключены из 11 измерительных слотов и сценария партиций. N25 измеряется условно на Replace до отдельных точных повторов провайдеров на этом пине.
- Direct roots проверяют сортировку и кратности полных значений плюс внешний frame. Wide — `repr(C)` с тремя `u64` и проверкой размера 24, ключ задаёт порядок, оба payload участвуют в равенстве. Covers наблюдают сравнения внутри реальных тел, равные ключи, восходящие и нисходящие пары и нормальный возврат фиксированного маршрута. [Q roots](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1.rs) · [Observer](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs) · [Direct roots](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_direct.rs)

## Команды, бюджет и сравнение

```text
{tool}/scripts/kani list -Z function-contracts -Z mem-predicates -Z float-lib
  -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing {std}/library --std --format json

{tool}/scripts/kani verify-std -Z unstable-options -Z function-contracts
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers
  -Z stubbing --no-assert-contracts --harness {selector} --exact --jobs=1
  --output-format=regular -Z export-json --export-json {slot}/export.json
  --verbose --target-dir {slot}/kani-target {std}/library --cbmc-args --object-bits 12
```

Списки без cfg и с cfg выполняются на одном пути std с раздельными чистыми output/target. Для каждого измерения задаётся отдельный `CARGO_TARGET_DIR={slot}/cargo-target`; из окружения удаляются inherited `RUSTFLAGS` и `CARGO_ENCODED_RUSTFLAGS`. Stock checks, reachability, unwind и CaDiCaL остаются штатными. Uninit и validity выключены. Export сверяет exact selectors, Check/Replace, resolved unwind, solver, OB12 и включённые проверки.

Batch содержит ровно `NET-U8-N08` и `NET-U8-N09` в этом порядке. Допуск требует завершённых singleton-терминалов с полными receipts, сумму wall с запасом 30 с в 600 с, и сумму изолированных пиков ≤80% начального доступного batch cap данной платформы. При недопуске batch получает `NOT_RUN`, список корней сохраняется. На Ubuntu команда использует `KANI_JOBS=2` и `--jobs=2`. В одном macOS job команды идут последовательно с незаданным `KANI_JOBS` и `-j`, затем с `KANI_JOBS=1` и `--jobs=1`. Каждая команда использует повторённый `--harness` и общий `--exact`. Все batch-варианты используют `terse` и stock export. Pinned Kani требует `terse` при многопоточном `--jobs`. Совпадение составов и наличия результата фиксируется отдельно. [Сбор argv](/root/kani-cal1-control-w11/ch8-cal1/run.py)

Оба job ограничены 225 мин. В окне 45 мин идут source/deps setup, одна сборка stock Kani и discovery. Успешный Linux discovery даёт допуск macOS job. Лимиты одиночных слотов суммарно составляют 139 мин, каждый batch получает до 600 с. Latest-start требует полного окна слота и 10 с headroom до 202-й минуты. Поздние слоты получают `NOT_STARTED`, если окно уже не помещается. Версионные пробы и повторные проверки обоих checkout делят до 120 с с общим дедлайном на 204-й минуте. Дальше выделены 5 мин на финализацию, 7 мин на upload и 9 мин резерва. После таймаута аттестации сохранённые слоты и `attestation.json` входят в частичный артефакт. Внутри слота зарезервированы 5 с на фиксацию результата и 10 с на TERM/KILL/wait. После проверенной очистки следующие независимые слоты продолжаются.

| Платформа | Singleton cap | Batch cap | Резерв |
| --- | ---: | ---: | ---: |
| Ubuntu | 10 GiB | 12 GiB | 2 GiB |
| macOS | 5,5 GiB | 5,5 GiB | 1,25 GiB |

Supervisor проверяет доступную память и давление при допуске и во время работы. Linux читает `/proc` и PSI. Darwin наблюдает RSS через `ps`, оценивает доступную память через `hw.memsize` и `memory_pressure -Q`, а уровень получает из `kern.memorystatus_vm_pressure_level`. Warning и critical блокируют допуск или останавливают запуск даже при достаточном резерве. Receipt сохраняет свободный процент, уровень и ошибки проб. RSS — сумма KiB по выбранной process group и обнаруженным потомкам в одном сэмпле. Общие страницы могут учитываться несколько раз. Receipt фиксирует cadence, пропуски, stop/reap и эффективный предел. Batch timeline сохраняет изменения набора наблюдавшихся CBMC PID. Индивидуальный RSS batch-корня остаётся неизвестным. [Supervisor](/root/kani-cal1-control-w11/ch8-cal1/supervisor.py) · [Коды давления XNU](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/event_private.h#L276-L278)

## Артефакт и локальные проверки

- `index.json` связывает run/attempt, trigger, source/checkouts, версии, frozen request, размеры и SHA-256 members и все ожидаемые слоты. Setup receipt связывает launcher, pinned nightly, CBMC, goto-cc/goto-instrument, установленный Kissat и чистоту Kani до/после. Версия используемой CaDiCaL берётся из native solver banner при наличии. Первые строки version probes сохраняются даже при отклонённом пине. [Баннер goto-cc](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-cc/gcc_mode.cpp#L323-L333) · [Версия CaDiCaL](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/sat/satcheck_cadical.cpp#L38-L41)
- На слот сохраняются `receipt.json`, bounded `projection.json` и для batch `timeline.json`. Singleton содержит native checks/covers с ID, status, description и location плюс stock totals. Batch содержит stock totals и идентификаторы, метки отдельных свойств при terse остаются `UNKNOWN`. Receipt хранит отдельно фазу stdout с доступным native timestamp и фазу sampler с временем monotonic. В частичном итоге с нетаймированной строкой stdout отображается наблюдение sampler с его временем. Compile/symex/SSA/SAT записываются при наблюдаемом источнике. Окно под projection — до 4 MiB, суммарно до 96 MiB на job. Index, summary и receipts сохраняются при усечении.
- `VERIFIED` и `FAILED` описывают наблюдаемые согласованные терминалы Kani. `TIMEOUT`, `RSS_LIMIT`, pressure/cleanup, сигнал, setup failure, `NOT_STARTED`, `NOT_RUN` и `INCOMPLETE` сохраняют причины и доступные частичные сведения. Отсечённые длительности остаются censored. `SUMMARY.md/json` сравнивают по каждой ОС standard + contract в штатном порядке, `ceil(total/4)`, перемещения и вклад выбранных корней. Отдельно приведены холодная компиляция, native verifier work/span, полный wall и наблюдённый batch. Для каждой метрики с выбранными корнями `UNKNOWN` означает отсутствие завершённых значений. Частичный агрегат показывает долю замеров и ID недоступных и отсечённых корней. Абсолютный прогноз и stock baseline macOS jobs=1 имеют статус `UNKNOWN`. Замер macOS p2 от 45173593629 закреплён в request. [Штатный run](https://github.com/model-checking/verify-rust-std/actions/runs/45173593629)
- `git diff --check` для обоих commits, PyYAML и `bash -n` для обоих jobs, статическая проверка окон и условий финализации и upload. Предыдущая валидация overlay включает layout, 11 selector/roles/unwind, pinned rustfmt новых Rust-файлов и replay bundle на отдельном shallow base. `cd /root/kani-cal1-control-w11/ch8-cal1 && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v` — 35 прошедших тестов. Новые сценарии покрывают исчерпание окна аттестации с публикацией сохранённых слотов, общий дедлайн проверок checkout, Darwin warning/critical с достаточным резервом и ошибки pressure probe, regular и terse jobs=1 при таймауте, а также `UNKNOWN` и покрытие частичных агрегатов.
- Реальные GitHub hosted Linux/macOS setup, компиляция overlay и результаты проверок ожидают запуска после review и отдельного решения. Локальная валидация ограничена Git, разбором исходников, форматированием и синтетическими тестами.
