# REV2 fallback · Ubuntu control для воркера 13

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`. Пакет замораживает один диагностический run и три singleton. Фактические discovery, compile, proof outcomes, native binding, VT и RSS остаются `UNKNOWN`. Задание взято из g0 `694a6046aeb243efb9e77abd40fed709ad10b514`. [Задание](REV2-FALLBACK-CONTROL-TASK.md) · [Source handoff](REV2-FALLBACK-HANDOFF.md)

## Git и замороженные входы

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| CAL2 FIX8 | `1b65866c1b037767d7ccf3262d05098ed9b2dc2b` | `339e8a63e08d068fec5973e896d8481fc8651978` | `52b3048ca119828d41d383f3c85dac51313c4aba` |
| Локальный REV2 control | `210a1d74b37c81e0451ae8f8b311130308bec8f3` | `7adcda65704085f19769a73cdb23cf3672c491f1` | `1b65866c1b037767d7ccf3262d05098ed9b2dc2b` |
| Будущий trigger | после GO | `7adcda65704085f19769a73cdb23cf3672c491f1` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Опубликованная std база | `dab03cf510df5c35141cde49f1368b1242f5035e` | `7fd542ad59723ff2beeacb9632fb0568e81b0655` | `1d2706e31f0cd909bd784fa43adf9a1d55be8469` |
| Std промежуточный кандидат | `dfdc70f8ccce6365f88fa489968508fa326ec60f` | `9f967855a6e6b71a7f81ecbc81e45a4d388443aa` | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| Std overlay | `fb82da3c788c0e705cd598abee723200c0f28c42` | `4329b593bdb0d4f3972452648396170f94adea8e` | `dfdc70f8ccce6365f88fa489968508fa326ec60f` |
| Stock tool | `9834c96ce90ff57d8495416530b080dc3d52ce25` | `938e9932cb2127239afb4f093f6302652c053398` | `70d7da0ae18991f9604d299784b974a43636945a` |

Control находится в `/root/kani-rev2-fallback-control-w11`, ветка `work/rev2-fallback-control-w11`. Diff для воркера 13 — `1b65866c1b037767d7ccf3262d05098ed9b2dc2b..210a1d74b37c81e0451ae8f8b311130308bec8f3`. Родитель trigger имеет tree `cf85db18831eea84e66723b16de37da08ef5fdd3`. Локальный control использует `[skip ci]` и автора `Tiramisu-Cake <igkharin@gmail.com>`. [Workflow](/root/kani-rev2-fallback-control-w11/.github/workflows/ch8-q-pilot.yml) · [Runner](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_run.py)

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

`VERIFIED` требует согласованных regular/export терминалов, свойств и пяти уникальных достигнутых covers. `120 с VT` и `4 GiB` выводятся как ориентиры. Receipt сохраняет exact argv, cfg, jobs, OB, resolved unwind и его источник, wall/VT, compile и phase, sampled peak, effective cap, cleanup, CNF/phase markers и компактную выборку native property ID/status/location. Для Cell проекция связывает stock `target_fn` и `contracted_function_name` с verbose цепочкой goto-cc, DFCC и CBMC для одного prepared path. Она сохраняет координаты и доступные записи native ensures, assigns и frame, включая кандидаты DFCC. При отсутствии или неоднозначности нужного якоря binding остаётся `UNKNOWN` независимо от времени и технического исхода. Для примитивов фиксируются stock Proof и отсутствие Replace. [Projection](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_projection.py) · [Binding](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_binding.py)

Артефакт `ch8-rev2-fallback-<os>-<arch>-<run>-<attempt>` содержит компактные структурированные receipts, до 4 MiB на опциональную CAL2 projection и до 96 MiB на весь job. `index.json` содержит SHA-256 и размеры членов. При ограничении бюджета удаляются опциональные проекции, а обязательные поля остаются в receipts. Setup failure публикует ограниченную диагностику, включая первые ошибки компилятора при их наличии. [Publication](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_report.py)

## Локальная проверка и передача

- `python3 -B -m unittest discover -s ch8-cal1 -q` — **132 теста прошли**, включая точный порядок и argv, мутации пинов/cfg/селекторов/режима/unwind, shallow import, границы часов и caps, отсечки и reap, частичные receipts, удаление проекции, усечение и потерю нативных якорей.
- `git diff --check` прошёл для control и trigger tree от их родителей. PyYAML подтвердил Ubuntu job, push/ref gate, read-only permissions и общую очередь `ch8-s2-fork`. `bash -n` прошёл для шести shell-шагов.
- В отдельном временном Git checkout `fallback_run.py pins` принял synthetic push с точным trigger tree и единственным parent. Проверка отклонила подмены SHA, ref, event, attempt, тот же tree с parent FIX8 и синтетический commit с несколькими parents.
- Стадия выполнена локально. CI, push, ledger и запуски Cargo, rustc, Kani и CBMC отсутствуют.

Следующий шаг — независимое diff-ревью воркера 13 и отдельный GO планера. Координатор может создать фактический trigger после GO и завершения macOS run `45338903191`. Допустим один attempt на `refs/heads/uninit-ci/ch8-q-pilot-v1` в `Tiramisu-Cake/kani`, в общей очереди, без повтора. Фактический trigger использует указанные tree и единственного parent и сообщение без метки пропуска CI.
