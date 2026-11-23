# CAL1 · пакет диагностики pr752

`READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Локальный пакет после run 45249887979 восстанавливает feature gate `fn_traits`, проверяет cfg-on `core` до полного discovery и сохраняет первые ошибки обоих потоков. Ревью `4f83c2a283` относится к исходному control tree. Исправленный пакет готов к независимому ревью. [Задание](CAL1-FIX-TASK.md) · [Handoff исправления](CAL1-FIX-HANDOFF.md) · [Frozen request](/root/kani-cal1-control-w11/ch8-cal1/CI-REQUEST.json)

## Идентичность и trigger

| Объект | Commit | Tree | Parent |
| --- | --- | --- | --- |
| std base | `dab03cf510df5c35141cde49f1368b1242f5035e` | `7fd542ad59723ff2beeacb9632fb0568e81b0655` | `1d2706e31f0cd909bd784fa43adf9a1d55be8469` |
| std overlay исправленный | `4afdf5f965b95446dbab90533645f43877f511be` | `3362e67c770b87934154f3de75f74ff63128c8f7` | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| std overlay прогона 45249887979 | `6e5b28070d72adefae7c259c6f33ffcebcd9a314` | `d4ab1d4f0749019d9f5568bfc4c62e54066de4a2` | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| Kani stock | `9834c96ce90ff57d8495416530b080dc3d52ce25` | `938e9932cb2127239afb4f093f6302652c053398` | `70d7da0ae18991f9604d299784b974a43636945a` |
| Control CAL1 исправленный | `cb4867dcd387e2062b04f4f3cbe5b439cd518597` | `fb468137deac4d0020e37897da4460649e3c83a9` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Control CAL1 прогона 45249887979 | `496851502d6fa6c773472ddc1981b62c9d948f3a` | `f85bab20a00b5651050733c1e2d5aedff24d140e` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| g0 задания на исправление | `d8667dc7c3a8471cf612d2edd1ef5cc3ef8262d3` | `69fb1a850bd3642f0a85709d16e43df77167566f` | `8bfe740b784742d0a920c6aff47f7406481c1270` |

- Оба checkout detached. Workflow проверяет SHA-256 bundle, импортирует объекты overlay без ref и сверяет commit/tree и единственного parent. После пробы и полного cfg-on discovery выполняется cfg-off inventory. Перед замерами runner восстанавливает точный detached overlay. [Std](/root/verify-rust-std-cal1-w11) · [Control](/root/kani-cal1-control-w11) · [Bundle](/root/kani-cal1-control-w11/ch8-cal1/std-overlay.bundle)
- Целевой fork `Tiramisu-Cake/kani`, событие `push`, единственный ref `refs/heads/uninit-ci/ch8-q-pilot-v1`. После отдельного решения координатора форма trigger — `git commit-tree fb468137deac4d0020e37897da4460649e3c83a9 -p 467af9cb8dba0e3be78a8d7d07672a1943c4806b` с сообщением, допускающим CI. Workflow на обоих jobs проверяет fork, event и полный ref. Runner сверяет push SHA и единственного родителя. [Workflow](/root/kani-cal1-control-w11/.github/workflows/ch8-q-pilot.yml)
- Receipt прогона 45249887979 зафиксировал предыдущий trigger `4b7e292777412a5a239d7afbf283ad08bac8e75a` с тем же родителем. Исправленный trigger будет его sibling. Состояние удалённой дорожки и разрешение на запуск остаются у координатора. [Source receipt](/root/ch8-artifacts/run-45249887979/ch8-cal1-Linux-X64-45249887979-1/source.json)

| SHA-256 | Исправленный пакет | Пакет прогона 45249887979 |
| --- | --- | --- |
| Frozen request | `5017a37ee49906b18c8ed0dfc59afc2217c294bf9f470d601e47c41f724b58ba` | `de9d0586b681c86cfb85aff85eec8c5450e3d3caaad2a3101f2af60bdb9a4cfc` |
| Std bundle | `cdaf3949c8f88ddfd93572dcddd31b328eb8539373b418fb4804bbf4f015b9df` | `4de024a3b2f844c186be8271c24ef757d402d94098c3e1b07b12a7e22dc610e8` |

## Overlay и frozen roster

Guard восстанавливает исходные `smallsort.rs`, `verify.rs` и `core/Cargo.toml` удалением добавленных опциональных атрибутов, деклараций четырёх модулей и записи `check-cfg`. В `core/src/lib.rs` он требует единственную строку `#![cfg_attr(all(kani, kani_smallsort_cal1), feature(fn_traits))]` и проверяет, что её удаление восстанавливает исходный blob побайтно. Все 11 строк roster используют `RUSTFLAGS=--cfg=kani_smallsort_cal1`. [Guard](/root/kani-cal1-control-w11/ch8-cal1/request.py) · [Feature gate](/root/verify-rust-std-cal1-w11/library/core/src/lib.rs)

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
  -Z stubbing --no-assert-contracts --no-codegen --only-codegen --quiet
  --target-dir {preflight}/kani-target {std}/library

{tool}/scripts/kani verify-std -Z unstable-options -Z function-contracts
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers
  -Z stubbing --no-assert-contracts --harness {selector} --exact --jobs=1
  --output-format=regular -Z export-json --export-json {slot}/export.json
  --verbose --target-dir {slot}/kani-target {std}/library --cbmc-args --object-bits 12
```

Проба `OVERLAY_COMPILE_PREFLIGHT` получает до 180 с внутри setup-дедлайна, отдельный target и `CARGO_TERM_VERBOSE=true` для записи команды компилятора. Успех требует exit 0, подтверждённого reap, наблюдения `kani-compiler` с `--crate-name core`, обоими cfg и `-Z no-codegen`, а также нуля наблюдавшихся verifier children. После пробы runner сверяет exact selector/kind по cfg-on списку, затем снимает cfg-off список и возвращает точный overlay. `common_ready` публикуется после обоих списков и сверки. [Порядок фаз и привязка к пину](CAL1-FIX-HANDOFF.md)

Проба, оба списка и каждый измерительный слот получают отдельный `CARGO_TARGET_DIR`. Runner очищает inherited `RUSTFLAGS` и `CARGO_ENCODED_RUSTFLAGS` перед установкой cfg. Stock checks, reachability, unwind и CaDiCaL остаются штатными. Uninit и validity выключены. Export сверяет exact selectors, Check/Replace, resolved unwind, solver, OB12 и включённые проверки.

Batch содержит ровно `NET-U8-N08` и `NET-U8-N09` в этом порядке. Допуск требует завершённых singleton-терминалов с полными receipts, сумму wall с запасом 30 с в 600 с, и сумму изолированных пиков ≤80% начального доступного batch cap данной платформы. При недопуске batch получает `NOT_RUN`, список корней сохраняется. На Ubuntu команда использует `KANI_JOBS=2` и `--jobs=2`. В одном macOS job команды идут последовательно с незаданным `KANI_JOBS` и `-j`, затем с `KANI_JOBS=1` и `--jobs=1`. Каждая команда использует повторённый `--harness` и общий `--exact`. Все batch-варианты используют `terse` и stock export. Pinned Kani требует `terse` при многопоточном `--jobs`. Совпадение составов и наличия результата фиксируется отдельно. [Сбор argv](/root/kani-cal1-control-w11/ch8-cal1/run.py)

Оба job ограничены 225 мин. В окне 45 мин идут source/deps setup, одна сборка stock Kani и discovery. Успешный Linux discovery даёт допуск macOS job. Лимиты одиночных слотов суммарно составляют 139 мин, каждый batch получает до 600 с. Latest-start требует полного окна слота и 10 с headroom до 202-й минуты. Поздние слоты получают `NOT_STARTED`, если окно уже не помещается. Версионные пробы и повторные проверки обоих checkout делят до 120 с с общим дедлайном на 204-й минуте. Дальше выделены 5 мин на финализацию, 7 мин на upload и 9 мин резерва. После таймаута аттестации сохранённые слоты и `attestation.json` входят в частичный артефакт. Внутри слота зарезервированы 5 с на фиксацию результата и 10 с на TERM/KILL/wait. После проверенной очистки следующие независимые слоты продолжаются.

| Платформа | Singleton cap | Batch cap | Резерв |
| --- | ---: | ---: | ---: |
| Ubuntu | 10 GiB | 12 GiB | 2 GiB |
| macOS | 5,5 GiB | 5,5 GiB | 1,25 GiB |

Supervisor проверяет доступную память и давление при допуске и во время работы. Linux читает `/proc` и PSI. Darwin наблюдает RSS через `ps`, оценивает доступную память через `hw.memsize` и `memory_pressure -Q`, а уровень получает из `kern.memorystatus_vm_pressure_level`. Warning и critical блокируют допуск или останавливают запуск даже при достаточном резерве. Receipt сохраняет свободный процент, уровень и ошибки проб. RSS — сумма KiB по выбранной process group и обнаруженным потомкам в одном сэмпле. Общие страницы могут учитываться несколько раз. Receipt фиксирует cadence, пропуски, stop/reap и эффективный предел. Batch timeline сохраняет изменения набора наблюдавшихся CBMC PID. Индивидуальный RSS batch-корня остаётся неизвестным. [Supervisor](/root/kani-cal1-control-w11/ch8-cal1/supervisor.py) · [Коды давления XNU](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/event_private.h#L276-L278)

## Артефакт и локальные проверки

- `index.json` связывает run/attempt, trigger, source/checkouts, версии, frozen request, размеры и SHA-256 members и все ожидаемые слоты. Setup receipt связывает launcher, pinned nightly, CBMC, goto-cc/goto-instrument, установленный Kissat и чистоту Kani до/после. Версия используемой CaDiCaL берётся из native solver banner при наличии. Первые строки version probes сохраняются даже при отклонённом пине. [Баннер goto-cc](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-cc/gcc_mode.cpp#L323-L333) · [Версия CaDiCaL](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/sat/satcheck_cadical.cpp#L38-L41)
- При ошибке сборки Kani, ранней пробы или discovery `setup.json` сохраняет отдельные первые ошибки stdout и stderr, до 80 строк и 16 KiB на поток. При отсутствии заголовка сохраняется помеченный префикс. Итог Cargo доступен в отдельном хвосте stderr. В `error.json` есть фаза, указатель на запись и распознанное первичное сообщение. [Проекция диагностик](/root/kani-cal1-control-w11/ch8-cal1/setup_diagnostics.py)
- На слот сохраняются `receipt.json`, bounded `projection.json` и для batch `timeline.json`. Singleton содержит native checks/covers с ID, status, description и location плюс stock totals. Batch содержит stock totals и идентификаторы, метки отдельных свойств при terse остаются `UNKNOWN`. Receipt хранит отдельно фазу stdout с доступным native timestamp и фазу sampler с временем monotonic. В частичном итоге с нетаймированной строкой stdout отображается наблюдение sampler с его временем. Compile/symex/SSA/SAT записываются при наблюдаемом источнике. Окно под projection — до 4 MiB, суммарно до 96 MiB на job. Index, summary и receipts сохраняются при усечении.
- `VERIFIED` и `FAILED` описывают наблюдаемые согласованные терминалы Kani. `TIMEOUT`, `RSS_LIMIT`, pressure/cleanup, сигнал, setup failure, `NOT_STARTED`, `NOT_RUN` и `INCOMPLETE` сохраняют причины и доступные частичные сведения. Отсечённые длительности остаются censored. `SUMMARY.md/json` сравнивают по каждой ОС standard + contract в штатном порядке, `ceil(total/4)`, перемещения и вклад выбранных корней. Отдельно приведены холодная компиляция, native verifier work/span, полный wall и наблюдённый batch. Для каждой метрики с выбранными корнями `UNKNOWN` означает отсутствие завершённых значений. Частичный агрегат показывает долю замеров и ID недоступных и отсечённых корней. Абсолютный прогноз и stock baseline macOS jobs=1 имеют статус `UNKNOWN`. Замер macOS p2 от 45173593629 закреплён в request. [Штатный run](https://github.com/model-checking/verify-rust-std/actions/runs/45173593629)
- Для исправления прошли 43 offline-теста Python, replay bundle на shallow std base, synthetic trigger на итоговом control, `git diff --check`, PyYAML и `bash -n` для обоих jobs. Сравнение с исходным пакетом подтвердило сохранение измерительных функций, roster, часов слотов, аттестации, RSS и upload. Фактический compile PASS исправленного overlay остаётся критерием будущего hosted запуска. [Подробности проверок](CAL1-FIX-HANDOFF.md)
