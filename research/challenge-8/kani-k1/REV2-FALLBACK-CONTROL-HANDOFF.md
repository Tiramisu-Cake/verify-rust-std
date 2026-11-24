# REV2 fallback · Ubuntu control для воркера 13

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`. Пакет замораживает один диагностический run и три singleton. Фактические discovery, compile, proof outcomes, native binding, VT и RSS остаются `UNKNOWN`. Исходное задание закреплено в g0 `694a6046aeb243efb9e77abd40fed709ad10b514`, FIX1 — в `ad8223b9dbfaca9d268a76df298147a8fd36b79e`, FIX2 — в `d149ad261634e42b2ba28f406ec5c8d36c943e14`. [Задание FIX2](REV2-FALLBACK-CONTROL-FIX2-TASK.md) · [Round 2](REV2-FALLBACK-CONTROL-REVIEW.md#round-2--fix1) · [Source handoff](REV2-FALLBACK-HANDOFF.md)

## Git и замороженные входы

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| CAL2 FIX8 | `1b65866c1b037767d7ccf3262d05098ed9b2dc2b` | `339e8a63e08d068fec5973e896d8481fc8651978` | `52b3048ca119828d41d383f3c85dac51313c4aba` |
| Исходный REV2 control | `210a1d74b37c81e0451ae8f8b311130308bec8f3` | `7adcda65704085f19769a73cdb23cf3672c491f1` | `1b65866c1b037767d7ccf3262d05098ed9b2dc2b` |
| Локальный REV2 control FIX1 | `d5910e387248acc8531aa8752b72ddbe3746dc9a` | `f75ae0336b0bf7b8a26be01400f629ed3dfd4ee3` | `210a1d74b37c81e0451ae8f8b311130308bec8f3` |
| Локальный REV2 control FIX2 | `06d94b37158d559e538a5c8fe93e2d8d813204f9` | `f5ef8d130ceba129d808535948c59697c9601172` | `d5910e387248acc8531aa8752b72ddbe3746dc9a` |
| Будущий trigger | после GO | `f5ef8d130ceba129d808535948c59697c9601172` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Опубликованная std база | `dab03cf510df5c35141cde49f1368b1242f5035e` | `7fd542ad59723ff2beeacb9632fb0568e81b0655` | `1d2706e31f0cd909bd784fa43adf9a1d55be8469` |
| Std промежуточный кандидат | `dfdc70f8ccce6365f88fa489968508fa326ec60f` | `9f967855a6e6b71a7f81ecbc81e45a4d388443aa` | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| Std overlay | `fb82da3c788c0e705cd598abee723200c0f28c42` | `4329b593bdb0d4f3972452648396170f94adea8e` | `dfdc70f8ccce6365f88fa489968508fa326ec60f` |
| Stock tool | `9834c96ce90ff57d8495416530b080dc3d52ce25` | `938e9932cb2127239afb4f093f6302652c053398` | `70d7da0ae18991f9604d299784b974a43636945a` |

Control находится в `/root/kani-rev2-fallback-control-w11`, ветка `work/rev2-fallback-control-w11`. Diff FIX2 для воркера 13 — `d5910e387248acc8531aa8752b72ddbe3746dc9a..06d94b37158d559e538a5c8fe93e2d8d813204f9`. Родитель trigger имеет tree `cf85db18831eea84e66723b16de37da08ef5fdd3`. Локальный control использует `[skip ci]` и автора `Tiramisu-Cake <igkharin@gmail.com>`. [Workflow](/root/kani-rev2-fallback-control-w11/.github/workflows/ch8-q-pilot.yml) · [Runner](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py)

Перед будущим dispatch координатор сверяет созданный trigger с одобренными tree и parent и закрепляет `f5ef8d130ceba129d808535948c59697c9601172` в Actions variable репозитория `Tiramisu-Cake/kani` с именем `CH8_REV2_FALLBACK_TRIGGER_TREE` на весь run. Workflow передаёт её в `REV2_FALLBACK_TRIGGER_TREE`. Внешний pin позволяет вычислить tree после сборки коммита и сверять весь tree без циклической зависимости. `pins` и остальные команды требуют заданный корректный pin и сверяют с ним checkout. Локальная стадия использовала переменную только в синтетических событиях. [Guard](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_request.py:87) · [Workflow](/root/kani-rev2-fallback-control-w11/.github/workflows/ch8-q-pilot.yml)

| Вход | SHA-256 |
| --- | --- |
| `ch8-cal1/FALLBACK-REQUEST.json` | `45c3c97225ca7072a0a4f8047058dc25494526de07e7b37a5bc07637c84db70b` |
| `ch8-cal1/fallback-overlay.bundle` | `43a7369986aca65aeaf19f36c7d96fc623dd3464d6353fbf5ce825aa25584c45` |

Bundle объявляет только `fb82da3c788c0e705cd598abee723200c0f28c42 HEAD`. `git bundle verify` и `git bundle unbundle` выполняются на detached shallow std базе. Проверяются refs до и после, SHA-256, commits, trees, parents и ровно пять путей относительно базы. Это `library/core/Cargo.toml`, `library/core/src/slice/sort/shared/smallsort/verify.rs`, а также `fallback_rev2.rs`, `merge.rs` и `trait_model.rs` внутри каталога `smallsort/verify/`. Guard сверяет единственное cfg-объявление и регистрацию, cfg-off проекцию модели, runtime и отсутствие изменений штатного workflow по полному набору diff-путей. [Frozen request](/root/kani-rev2-fallback-control-w11/ch8-cal1/FALLBACK-REQUEST.json) · [Source guard](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_request.py)

## Последовательность и argv

Общий префикс `slice::sort::shared::smallsort::verify::fallback_rev2::`. У каждой строки четыре общих cover `sorted input returns`, `strictly descending input returns`, `duplicate input returns` и `fallback useful return`.

| Порядок | Суффикс exact selector | Режим | Unwind из атрибута | Пятый cover |
| ---: | --- | --- | ---: | --- |
| 1 | `cell_unstable_n16` | Check `<Cell<u8> as UnstableSmallSortTypeImpl>::small_sort`, default Unstable, actual fallback, V34/base1, `CellCmp` = `canonical_less_cell` | 36 | `sort model enabled before call` |
| 2 | `u8_n07` | Original `kani::proof`, прямой `small_sort_fallback`, `[u8;7]` base0, `merge::lt_u8` | 34 | `distinct inputs with equal keys return` |
| 3 | `u64_n07` | Original `kani::proof`, прямой `small_sort_fallback`, `[u64;7]` base0, `merge::lt_u64` | 34 | `distinct inputs with equal keys return` |

Примитивы упорядочены по `value >> 1`, кратности сверяются по полным значениям. Stock tool готовится один раз на job. CBMC `6.11.0`, штатный CaDiCaL, OB12, обычные memory/bounds/overflow/unwind/reachability, uninit и validity выключены. CAL2 compile preflight использует `verify-std` с флагами профиля и `--no-assert-contracts --no-codegen --only-codegen --quiet --target-dir <overlay-compile>/kani-target <std>/library`. После него один `list -Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing <std>/library --std --format json`. Проверяются 32 уникальные регистрации нового модуля, 12 Check и 20 Original. 29 других регистраций остаются только в inventory.

Ниже переменные обозначают пути внутри одного job. Каждый argv исполняется из собственного свежего cwd `$s_cell`, `$s_u8` или `$s_u64`. Для каждого cwd установлены отдельные `CARGO_TARGET_DIR=<cwd>/cargo-target` и `TMPDIR=<cwd>/tmp`. Перед вызовом унаследованные `RUSTFLAGS` и `CARGO_ENCODED_RUSTFLAGS` удаляются. Фактический env содержит `RUSTFLAGS=--cfg=kani_smallsort_fallback_rev2` и `KANI_JOBS=1`. `cfg(kani)` добавляет Kani.

```bash
tool="$GITHUB_WORKSPACE/tool"
std="$GITHUB_WORKSPACE/std"
work="$RUNNER_TEMP/ch8-rev2-fallback/work"
s_cell="$work/cell_unstable_n16"
s_u8="$work/u8_n07"
s_u64="$work/u64_n07"
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing --no-assert-contracts --harness slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n16 --exact --jobs=1 --output-format=regular -Z export-json --export-json "$s_cell/export.json" --verbose --target-dir "$s_cell/kani-target" "$std/library" --cbmc-args --object-bits 12
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing --no-assert-contracts --harness slice::sort::shared::smallsort::verify::fallback_rev2::u8_n07 --exact --jobs=1 --output-format=regular -Z export-json --export-json "$s_u8/export.json" --verbose --target-dir "$s_u8/kani-target" "$std/library" --cbmc-args --object-bits 12
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing --no-assert-contracts --harness slice::sort::shared::smallsort::verify::fallback_rev2::u64_n07 --exact --jobs=1 --output-format=regular -Z export-json --export-json "$s_u64/export.json" --verbose --target-dir "$s_u64/kani-target" "$std/library" --cbmc-args --object-bits 12
```

## Окна и receipts

| Граница от monotonic epoch | Значение |
| --- | ---: |
| Setup, включая preflight до 180 с | 45:00 |
| Три окна по 600 с и по 10 с latest-start headroom | 75:30 |
| Постаттестация | 77:30 |
| Финализация и upload | 89:30 |
| Резерв | 98:30 |
| Job cap с дополнительным запасом 90 с | 100:00 |

Setup использует номинал 10 GiB, каждый singleton 6 GiB. Effective cap равен `min(nominal, available − 2 GiB)` по sampled group RSS, с прежними live guards. CAL2 supervisor, инструментальная аттестация и нативный CNF-парсер побайтово совпадают с FIX8. Из каждого окна 600 с последние 5 с выделены на проекцию и receipt. TERM/KILL и reap проходят внутри дедлайна supervisor. После RSS/TIMEOUT следующий слот допускается при валидном сэмплере и подтверждённой очистке. При потере resource control, drift пинов или недоказанной очистке оставшиеся строки получают именные `NOT_STARTED` с причиной.

Запись временного файла receipt ограничена остатком окна. Runner повторно сверяет часы перед атомарной заменой и измеряет её завершение. После таймаута timed write runner атомарно сохраняет последний вычисленный receipt обычной записью. В отметке `receipt_deadline` фиксируются `slot_window_exceeded`, момент обнаружения превышения, фактический момент завершения записи и признак восстановления `recovered_after_timed_write_timeout`. Следующие слоты получают именные `NOT_STARTED`. `finish` добавляет отметку в receipt и сводку, сохраняя вычисленный outcome и связанную проекцию. [Запись receipt](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py:225) · [Финализатор](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_report.py)

`VERIFIED` требует согласованных regular/export терминалов, свойств и пяти уникальных достигнутых covers. `120 с VT` и `4 GiB` выводятся как ориентиры. Receipt сохраняет exact argv, cfg, jobs, OB, resolved unwind и его источник, wall/VT, compile и phase, sampled peak, effective cap, cleanup, CNF/phase markers и компактную выборку native property ID/status/location. Для Cell проекция связывает stock `target_fn` и `contracted_function_name` с verbose цепочкой goto-cc, DFCC и CBMC для одного prepared path. Она сохраняет координаты и доступные записи native ensures, assigns и frame, включая кандидаты DFCC. При отсутствии или неоднозначности нужного якоря binding остаётся `UNKNOWN` независимо от времени и технического исхода. Для примитивов фиксируются stock Proof и отсутствие Replace. [Projection](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_projection.py) · [Binding](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_binding.py)

Артефакт `ch8-rev2-fallback-<os>-<arch>-<run>-<attempt>` содержит компактные структурированные receipts, до 4 MiB на опциональную CAL2 projection и до 96 MiB на весь job. `index.json` содержит SHA-256 и размеры членов. При ограничении бюджета удаляются опциональные проекции, а обязательные поля остаются в receipts. Setup failure публикует ограниченную диагностику, включая первые ошибки компилятора при их наличии. [Publication](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_report.py)

`pins` выставляет `trigger_admitted` после GitHub/Git guard и до проверки request и bundle. При ошибке входов подготовка и измерения пропускаются, а `finish` сверяет допуск и публикует `error.json` и три именных `NOT_STARTED` из доверенного roster. Upload требует допуска trigger и успешного `finish`. Отказ trigger guard оставляет публикацию закрытой. [Workflow](/root/kani-rev2-fallback-control-w11/.github/workflows/ch8-q-pilot.yml) · [Runner](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py)

## Локальная проверка и передача

- `python3 -B -m unittest discover -s ch8-cal1 -q` — **137 тестов прошли**. `git diff --check` прошёл для FIX2 и будущего trigger tree от их родителей. PyYAML проверил YAML из точного tree. `bash -n` прошёл для шести shell-шагов.
- `fallback_run.py pins` принял синтетический push с полным tree FIX2, соответствующим внешним pin и единственным parent. Тот же checkout с pin FIX1 отклонён. Python suite также проверил tree с одним добавленным файлом, отсутствующий pin, другой parent, подмены полей события и commit с несколькими parents.
- На сохранённом артефакте таймаут staging `AFTER_CHILD` сохранил `RSS_LIMIT`, причину отсечки, peak 6291500 KiB, scope, effective cap 6291456 KiB, фазу `cbmc` и подтверждение reap. Таймаут staging `FINAL` сохранил `VERIFIED / EXITED`, завершённую проекцию, VT `1.5` с из stock export, пять достигнутых covers и подтверждение reap. Оба артефакта показывают дедлайн `1600.0`, обнаружение `1600.1`, завершение восстановительной записи `1600.2` и два именных `NOT_STARTED`. Эти регрессии на FIX1 воспроизвели оба устаревших `INCOMPLETE` в артефакте. Отдельный тест сохранил `RSS_LIMIT` при завершении самой атомарной замены в `1600.1`.
- Для двух допущенных синтетических triggers проверены порча request и порча bundle. CLI `pins` сохранил допуск и завершился с ошибкой, а CLI `finish` собрал индекс, `error.json` и три именных `NOT_STARTED`. YAML пропускает setup и слоты при ошибке `pins` и допускает upload после такого `finish`.
- Стадия выполнена локально. CI, push, ledger и запуски Cargo, rustc, Kani и CBMC отсутствуют.

Следующий шаг — независимое diff-ревью воркера 13 и отдельный GO планера. Координатор может создать фактический trigger после GO и завершения macOS run `45338903191`. Допустим один attempt на `refs/heads/uninit-ci/ch8-q-pilot-v1` в `Tiramisu-Cake/kani`, в общей очереди, без повтора. Фактический trigger использует указанные tree и единственного parent и сообщение без метки пропуска CI.
