# REV2 · валидность на Kani main с nightly 11-21 · handoff

**READY_FOR_REVIEW** (FIX5) · `go=NOT_GRANTED` · `proof_credit=NONE` · ledger **Item 2** · control **`fc3a0e654e`**, tree `e9b8b46457`, review-trigger `a41dcc74de`, Std overlay `fe3fe324bf` ([FIX5](#fix5-по-разбору-фазы-b)). FIX4: control `e2a3e6d48e`, tree `f46e65c42c`. FIX3: control `0a4f85d930`, tree `c575224396`. Разделы до FIX2 описывают R1-кандидат: control `e4b3eced27`, tree `817a5db4e9`. FIX2: control `bf4e1d882a`, tree `6d51ab4ed0`. Инструмент в отчётах — **«Kani main `8c6dba5935` с nightly-2026-11-21»**: это не upstream-коммит, а локальный кандидат `4caf097d84`. [Задание](REV2-VALIDITY-MAIN-REPIN-TASK.md) · [Записка координатора](COORD-NOTE-20261126-VALIDITY-PIN-AND-KANI5196-RECHECK.md) · [FIX1](REV2-VALIDITY-MAIN-HANDOFF.md)

Совместимость пары до CI остаётся **UNKNOWN**. Cargo, rustc, сборка Kani, Kani и CBMC локально не запускались, toolchain не ставился. Push, CI, изменений Actions variables, обновления ветки pr752 и публикаций не было.

## Слои

| Слой | Commit | Tree | Parents |
| --- | --- | --- | --- |
| Kani public main | `8c6dba5935e8b37a905145c57572d1b67489bae2` | `3ae54fa78d0e7ab1fbaec728ced37cbd59127834` | `18a8d8031e…` |
| **Kani candidate** | `4caf097d845ae8b859a18c4327b3694efd6f743a` | `082872b48f061601c75aa8576963ee563b2198dd` | `8c6dba5935…` |
| Std pr752, frozen | `dab03cf510df5c35141cde49f1368b1242f5035e` | `7fd542ad59723ff2beeacb9632fb0568e81b0655` | `1d2706e31f…` |
| Std upstream main | `f94155ef2983580c9c012740b75793df2922d2e5` | `eac26ed069fe2a5f9d362efe4c9f5f5514e951bd` | `1feeadd937…` |
| **Std merge** | `7f961eda87f25cf422b2f0a444c9ef7edf2296c9` | `46b1fc246c08718662dd953643653fe18597cf3c` | `dab03cf510…` первый, `f94155ef29…` второй |
| Std overlay 1, корни | `cac978ee4659f99dfc1d9de60d5239a956f79e04` | `122589bc0828dc909f2df59c58cbc59662e93412` | merge `7f961eda87…` |
| **Std overlay 2**, типизированные чтения | `bc866f8dfa4ad517b2d67e2d3d812729d82d5148` | `079e0660cfdcbdb23c960969c0cc9d6926bd9cad` | overlay 1 `cac978ee46…` |
| **Control** | `e4b3eced27aef7a926ae90b82a21411fcde24cc4` | `817a5db4e9eedc486148ec6018b9ce35685c0a93` | FIX1 `3ca002452456f9fdfe303ad01acd439960833429` |
| Review-trigger | `0650c59e24ebd22bac7cec686e690d9d56ef7732` | `817a5db4e9eedc486148ec6018b9ce35685c0a93` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b`, единственный |

- Worktrees: [Kani candidate](/root/kani-rev2-validity-repin-tool-w11) detached, [Std](/root/verify-rust-std-rev2-validity-repin-w11) на ветке `work/rev2-validity-repin-std-w11`, [control](/root/kani-rev2-validity-repin-control-w11) на ветке `work/rev2-validity-repin-control-w11`. Trigger лежит в `local/rev2-validity-repin-trigger-review`, его checkout — [trigger-ws](/root/rev2-validity-repin-review/trigger-ws/control).
- Upstream получен read-only fetch по полному SHA в локальный ref `refs/local/upstream-f94155ef29` общего Std-репозитория.
- Автор и коммиттер всех новых коммитов — `Tiramisu-Cake <igkharin@gmail.com>`. Все сообщения содержат `[skip ci]`, знака решётки перед цифрой нет.

## Kani: выбор и точная дельта

- `git diff 87c87010ed 8c6dba5935^ -- kani-compiler kani-driver kani-verifier library` пуст, каталога `kani-verifier` в дереве нет. Полный промежуточный diff — ровно `Cargo.lock`, `rust-toolchain.toml`, `.github/actions/build-bundle/action.yml` и `scripts/setup/install_kissat.sh`. Изменения action и kissat касаются только macOS: проверка minimum macOS и `MACOSX_DEPLOYMENT_TARGET=11.0` под `Darwin`.
- Cherry-pick `8c6dba5935` на `87c87010ed`, сделанный через `git merge-tree` без записи, даёт tree `22d6de4a3c`. От `8c6dba5935` он отличается теми же четырьмя путями. Деревья `kani-compiler`, `kani-driver`, `library`, `tests`, `kani_metadata`, `cprover_bindings`, `src` и `tools` совпадают по хешам. Выбран полный main с одной заменой TOML: lockfile, скрипты и исходники совпадают с комплектом, собранным 11-23 в `45685044990`.
- Дельта кандидата: `:100644 100644 864a9691aa2c3f1a51f652bc52c388cdad51edb6 7f0da183eccb81b65dbcf69b81cf4f39c4b78304 M rust-toolchain.toml`. Новый blob совпадает с `87c87010ed:rust-toolchain.toml`. Остальные 4021 записи `ls-tree -r`, включая режимы, совпадают с `8c6dba5935`. Совпадают `Cargo.lock` `24a5c536d8…` и gitlinks `charon` `e21fb23e3c…`, `firecracker` `cd36c699f3…`, `tests/perf/s2n-quic` `d7b71409c3…`. Lockfile пина `87c87010ed` другой, `4d6271c38a…`, от cargo update 11-23.
- Равенство исходников не даёт равенства бинарников. Риск фазы 0 `KANI_BUILD`: valid-value checks писались против rustc 11-23, а lockfile обновлён 11-23. Сборка на 11-21 измеряется только в CI.

| Сторона | Канал | Компоненты | Пин Kani |
| --- | --- | --- | --- |
| Kani candidate `4caf097d84` | `nightly-2026-11-21` | `llvm-tools`, `rustc-dev`, `rust-src`, `rustfmt` | — |
| Std merge `7f961eda87` = upstream `f94155ef29` | `nightly-2026-11-21` | `llvm-tools-preview`, `rustc-dev`, `rust-src`, `rustfmt` | `87c87010eda7797d7fa14033ca68bcbe17184a63` |

Std компилируется toolchain Kani: `kani-driver` вызывает `cargo +<RUSTUP_TOOLCHAIN времени сборки>` с `RUSTC=<kani-compiler>`. Теперь каналы обеих сторон совпадают. Компоненты различаются только именем `llvm-tools` и `llvm-tools-preview`. Фаза 0 проверяет установленные компоненты 11-21 через `rustup component list --installed`, а также rustc/cargo/sysroot и `kani-compiler -Vv`. Setup action ставит toolchain по `rust-toolchain.toml` уже материализованного кандидата. `frozen_env` удаляет `RUSTUP_TOOLCHAIN` и `RUSTC*`.

## Std: merge и overlay

- Merge без конфликтов. Merge base `b5adb2c5c9`: pr752 впереди на 5 коммитов и меняет 19 путей, upstream впереди на 2 коммита и меняет 41 путь. Пересечения нет. Каждая запись merge совпадает с upstream на его 41 пути и с pr752 на его 19 путях. Toolchain и пин в merge — из upstream.
- Штатная дельта `pr752 → merge`: 41 путь, все `M`. SHA-256 вывода `git diff --raw --no-abbrev --no-renames` равен `edec6685ccf393496de74175d5dcb19ddc00f2a14d8755b6d6ebb4049d48c6f1`. В `library/core` 14 файлов: alloc, any, cmp, error, field, fmt, intrinsics ×2, lib.rs, marker, mem/type_info, panicking, ub_checks. Среди них `cmp.rs` с `lang = "partial_eq"`/`"eq"` и `mem/type_info.rs` — места ошибок `E0718`/`E0522` фазы 0 от 11-23. `slice/sort`, `core/Cargo.toml`, `hint.rs`, `mem/mod.rs`, `num`, `ptr` не затронуты. В `lib.rs` снят только `#[allow(missing_docs)]` у `alloc`, в `marker.rs` добавлен только `lang = "send"`. [Дельта](/root/rev2-validity-repin-review/merge-delta-from-pr752.raw)
- Verification-only дельта `merge → overlay` побайтно равна дельте FIX1 `dab03cf510 → 75ab1822ac`. Оба вывода raw diff дают SHA-256 `77ad2cc4bf60912d7d597841579b2a434b4ef0b8662818a157b553b8be172a61`. По отдельности совпадают и дельты обоих overlay-коммитов. Blobs: `library/core/Cargo.toml` `ece364742a` → `52285c638f`, `smallsort.rs` `73e2898580` → `9f671ae369`, новый `validity_main.rs` `6bd163c9fd`, режимы прежние. Базовые blobs двух изменяемых файлов в merge те же, что в pr752. Cfg `kani_rev2_validity_main`, имена корней и маршруты прежние. [Патч overlay](/root/rev2-validity-repin-review/std-overlay-from-merge.patch)
- Видимость и сигнатуры: `smallsort.rs` и `validity_main.rs` не изменились, а импорты модуля (`super::*`, `hint::black_box`, `mem::{MaybeUninit, size_of}`, `num::NonZeroU8`, `kani`, `ptr`) вне дельты merge. `kani_core::kani_lib!(core)` в `lib.rs:365` на месте. `library/` кандидата Kani совпадает с `8c6dba5935`. Поэтому сверка FIX1 по видимости, `FreezeMarker` и `Arbitrary` переносится без изменений.

## Доставка и импорт

| Файл control | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-validity-repin-control-w11/ch8-rev2-validity/CI-REQUEST.json) | `005ebf08bc662eee10bf1ae33c61b0489eaee99ca24bb1966a965a5c62fb1fbe` |
| [tool-patch.bundle](/root/kani-rev2-validity-repin-control-w11/ch8-rev2-validity/tool-patch.bundle), 603 B | `51ba5593376a9ec9c2b3c0d7c8e2af4975a99ae1a5035101dc8033ec1c0b6843` |
| [std-overlay.bundle](/root/kani-rev2-validity-repin-control-w11/ch8-rev2-validity/std-overlay.bundle), 4874 B | `fbcab32cf1d74d896a99364a5001d17b349f3cd99a0ae198ad0b3f0ab554ff9e` |
| [validity_fixture.rs](/root/kani-rev2-validity-repin-control-w11/ch8-rev2-validity/validity_fixture.rs), без изменений | `eb9575b09117594fa57ea5c3dc64752b37f41584c232c25b476dddb6b35a1f16` |
| [ch8-q-pilot.yml](/root/kani-rev2-validity-repin-control-w11/.github/workflows/ch8-q-pilot.yml) | `87125e1d84eac3ebc54e4a727c00f37ec044bda2a6d22ad8e9dece2b84b3e5c5` |

- Digest roster прежний: `6a89e1e970d44938bef0bd2864d235d4f69f1e8cd46c1648adf3c7c87862deea`. Bundle Kani — v2, один prerequisite `8c6dba5935`, один `HEAD` `4caf097d84`. Bundle Std — v2, prerequisites `f94155ef29` и `dab03cf510`, один `HEAD` `bc866f8dfa`.
- Frozen request (schema `smallsort-rev2-validity-repin-v1`) хранит раздельно: `tool_public`, `tool`, `tool_patch` (путь, режим, оба blob, источник `87c87010ed`, lockfile, gitlinks), `std_parents.pr752/upstream`, `std_sources` (fork, URL upstream, локальный ref), `base` = merge, `merge_delta`, `overlay_chain`, `overlay_source_chain` FIX1, `overlay_delta_sha256`, `toolchains` с пином Kani, `tool_label`, `ledger_item: 2`. `source.json`, `phase-0.json`, `attestation.json` и `SUMMARY.json` несут ту же раздельную идентичность.
- Workflow checkout-ит `Tiramisu-Cake/verify-rust-std` на `dab03cf510` и `model-checking/kani` на `8c6dba5935`: полные SHA, depth 2, submodules recursive. **`sources` идёт до `./tool/.github/actions/setup`**. Порядок шагов внутри:
  1. Identity обеих публичных основ с submodules. Затем bundle Kani: разбор заголовка, точный набор prerequisites, единственный `HEAD`, `bundle verify`, `unbundle` без изменения refs, форма commit/tree/parent, однострочная raw-дельта, lockfile, gitlinks и TOML кандидата. После этого `checkout --detach` кандидата и identity с submodules.
  2. Если upstream отсутствует, его коммит подтягивается `fetch --depth=2` по полному SHA из `https://github.com/model-checking/verify-rust-std.git` в `refs/ch8-rev2/upstream`. Fetch ограничен 240 с, затем сверяется tree, ref и отсутствие alternates. `bundle verify` ищет prerequisites от `--all`, поэтому нужен локальный ref.
  3. Bundle Std с двумя prerequisites. Порядок родителей merge, digest дельты pr752 → merge, равенство записей upstream, отсутствие путей pr752-scope в дельте, пины merge против upstream. Затем цепочка overlay из одиночных родителей, digest дельты merge → overlay, layout guard, пины overlay, все координаты и covers по реальному тексту overlay.
  4. `checkout --detach` чистого merge и `source_pins`: identity с submodules, оба TOML и пин Kani.
- Тот же `source_pins` вызывается в начале фазы 0 до сборки и в финальной аттестации, на overlay или merge. Фаза 0 стартует только при `source.json` со статусом `PASS`. Если импорт не завершён, все 30 слотов получают `NOT_RUN` с причиной `SOURCES_NOT_COMPLETED`.
- Окно `sources` — 6:00 от старта шага, timeout шага 8 мин. Оно входит в окно фазы 0 до 30:00 от epoch. Self-test связывает timeout с бюджетом.

## CI-последовательность, roster и флаги

Без изменений относительно FIX1. [Roster и правила](REV2-VALIDITY-MAIN-HANDOFF.md#точный-roster-и-ожидания)

- Фаза 0: `rustup component list --installed --toolchain nightly-2026-11-21`, `cargo build-dev --release`, attestation против CBMC/goto-cc/goto-instrument 6.11.0. Затем штатный compile-only preflight чистого merge без overlay и без cfg: точная команда CAL2, 300 с, Cargo- и procfs-witness ядра без `--cfg=kani_rev2_validity_main`, sysroot ядра против sysroot пина. Классы сбоев прежние. `UNCHANGED_STD_COMPILE` теперь означает «чистый merge не компилируется»; пишутся первая диагностика, код, `file:line:column` и выпуск rustc.
- **A**: 9 корней fixture × OFF/ON = 18 слотов, unwind 16, 45 с cold wall на слот. **B**: 6 корней `slice::sort::shared::smallsort::validity_main::*` × OFF/ON = 12 слотов, включая контроль `vv_stable_char_n09_corrupt`, unwind 64/64/96/96/96/96, 180 с на слот. B требует `PASS` фазы 0 и все 18 `MATCH` в A. Перед слотами идут overlay preflight с cfg и один cfg-on `kani list` с ровно шестью `standard-harnesses`.
- Все слоты: `--exact --jobs=1 --output-format=regular --solver cadical --unwind <N> --verbose --cbmc-args --object-bits 12`. ON отличается только парой `-Z valid-value-checks`, `-Z uninit-checks` не передаётся. B — `verify-std` с восемью `-Z` и `--no-assert-contracts`. Safety checks штатные. Отдельно публикуются `read_binding`, `resource_status` и полные terminal outcomes. `SUCCESS` без привязки чтения даёт `read_binding=UNKNOWN`.
- Координаты пересняты после merge и совпали: строки чтения 41/78/166 fixture и 111 `validity_main.rs`, записи, внутренние чтения `smallsort.rs` и covers. В реальном статическом импорте `check_coordinates` дал `PASS`.

| Фаза | Окно | Конец от epoch |
| --- | --- | ---: |
| Checkout, pins, **sources ≤ 6:00**, deps, build, attestation, preflight ≤ 300 с | 30:00 | 30:00 |
| A: 18 × (45 + 10 + 5 + 5) | 19:30 | 49:30 |
| B setup, также ≤ 30:00 от старта шага | 30:00 | 79:30 |
| B: 12 × (180 + 10 + 5 + 5), также ≤ 40:00 от конца setup | 40:00 | 119:30 |
| Финальная аттестация | 2:00 | 121:30 |
| Finalize + upload | 5:00 + 7:00 | 133:30 |
| Job | запас 6:30 | 140:00 |

Таймауты шагов: pins 3, sources 8, setup 15, фаза 0 30, A 21, B 80, finish 5, upload 7 мин. Ресурсные лимиты прежние: VT ≤ 120 с, группа 4 GiB на проверку, резерв 2 GiB, setup 10 GiB. Ожидаемая фактическая длительность — как в FIX1, 45–70 мин, плюс импорт: локальный fetch upstream занял 3,4 с, из GitHub ожидается до минуты. Ubuntu-результат не закрывает профиль macOS.

## Trigger и gate

- Новая независимая переменная **`CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE`**, env `REV2_VALIDITY_REPIN_TRIGGER_TREE`. Gate прежний: `Tiramisu-Cake/kani`, `push`, `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, `after` = `GITHUB_SHA` = HEAD, единственный parent `467af9cb8d`, tree = переменная. Finish и upload — только после допуска.
- Review-trigger `0650c59e24` содержит `[skip ci]` и для запуска не годится. После GO координатор пересоздаёт коммит с tree `817a5db4e9eedc486148ec6018b9ce35685c0a93`, parent `467af9cb8d` и сообщением без `[skip ci]`, а переменной задаёт этот tree.
- Переменная FIX1 `CH8_REV2_VALIDITY_MAIN_TRIGGER_TREE` всё ещё указывает на `697dc737fe`. Новый workflow её не читает: проверено, что с ней одной допуск отклоняется. Повторный push старого tree снова запустил бы пакет FIX1. Предлагаю после GO очистить старую переменную — это решение координатора.

## Проверки

- `python3 -B -m unittest discover`: **109/109** за 29–32 с, последовательно. Блок self-test из workflow с часами от 60 с — 109/109 дважды. Под нагрузкой load 7,5 на 2 CPU один прогон уронил `test_escaped_descendant_is_killed_by_its_owned_pid` с `REAP_UNVERIFIED` и ещё несколько supervisor-тестов. `supervisor.py` побайтно равен FIX1. Отдельно тест прошёл 5/5 и в FIX1, и здесь, а полные прогоны при нагрузке около 2 — 109/109.
- На detached review-trigger `0650c59e24` с синтетическим push выполнен `run.py pins`. Tree FIX1 `697dc737fe` отклонён (`trigger tree mismatch`). Одна старая переменная отклонена (`missing or malformed`), outputs и `trigger.json` не появились. С новым tree допуск прошёл, outputs — `std=dab03cf510…`, `tool=8c6dba5935…`. Затем self-test 109/109 за 31,2 с, а `phase-a`, `phase-b` и `finish` без импорта дали 30 receipts `NOT_RUN`/`SOURCES_NOT_COMPLETED`, `SUMMARY.json` и `index.json` на 35 членов. Checkout остался чистым.
- **Статический импорт на реальных объектах.** Скрипт [static_import.py](/root/rev2-validity-repin-review/static_import.py) создаёт два чистых `git init`. В каждый `fetch --depth=2` по полному SHA кладёт ровно одну публичную основу. Alternates и refs нет. Затем исполняется настоящий `run.sources` с замороженным request. Результат `PASS`: tool HEAD `4caf097d84`, Std HEAD `7f961eda87`, shallow-границы `1d2706e31f` и `1feeadd937`, единственный ref `refs/ch8-rev2/upstream`. Есть два отличия от CI. URL upstream — локальное хранилище `file://`, его подменили после `load()`. Identity submodules не проверялась: локально их содержимого нет. [Вывод](/root/rev2-validity-repin-review/static_import.out)
- `test_sources.py`, 6 тестов, строит синтетические миры Git с фиксированными датами: публичный Kani и кандидат, Std base/pr752/upstream/merge/два overlay и оба bundle. Счастливый путь проходит через настоящий `run.sources` с shallow-основами без alternates, проверка координат там подменена. Отклоняются:
  - прежний pin: неизменённый main как кандидат и request с tool/base/каналами/переменной/bundle FIX1;
  - upstream на `nightly-2026-11-23` и кандидат на другом канале;
  - обратный порядок родителей merge и bundle, обрезанный только по pr752 (лишний prerequisite base);
  - отсутствующий upstream и изменённый lockfile, gitlink или лишний файл кандидата;
  - overlay с изменённым runtime `smallsort.rs`, bundle с `HEAD` на overlay 1, повреждённый pack, неизвестный формат заголовка.
- `test_run.py`, 29 тестов. Добавлен e2e: ранний `E0718` в `cmp.rs:243` при компиляции чистого merge даёт `UNCHANGED_STD_COMPILE` с координатой и без cfg. Ни один слот A/B после этого не запускается, все 30 получают `NOT_RUN`/`PHASE_0_BASE_COMPILE_PREFLIGHT`, финальной аттестации нет. Gate A без импорта даёт `SOURCES_NOT_COMPLETED`, без фазы 0 — `PHASE_0_NOT_COMPLETED`. `declarations` отвергает 11-23/11-19 у обеих сторон, `llvm-tools-preview` у Kani и старый пин `9834c96ce9`. Мутации request покрывают и три bundle/fixture digest.
- Патч `3ca0024524..e4b3eced27` воспроизвёл tree `817a5db4e9` во временном Git index. [Patch control](/root/rev2-validity-repin-review/control-from-fix1.patch) · [Patch Kani](/root/rev2-validity-repin-review/tool-toolchain.patch)
- PyYAML разобрал workflow без дублей ключей: 12 шагов, семь shell-блоков прошли `bash -n`. `ch8-s2.yml` срабатывает только на `uninit-ci/ch8-s4p-*`. `git diff --check` чист для control и Std. `rustfmt --check` назначенным `nightly-2026-11-19/bin/rustfmt` прошёл для `validity_main.rs` и `smallsort.rs` merge-overlay (`--edition 2024`, `skip_children`, `reorder_modules=false`, `use_small_heuristics=Max`) и для fixture (`--edition 2021`). Rustfmt 11-21 локально нет и не ставился; файлы побайтно равны FIX1.

## UNKNOWN и следующий шаг при блокере

- До фазы 0 неизвестны сборка кандидата на 11-21 (`KANI_BUILD`), компоненты, компиляция чистого merge под kani-compiler 11-21 и всё последующее. Ограничения модели Kani 5205 и вне-scope пункты FIX1 сохраняются.
- `KANI_BUILD` на кандидате: передать первую ошибку компилятора. Альтернатива — пин `87c87010ed` плюс cherry-pick valid-value checks: исходники те же, отличаются только lockfile и macOS-скрипты. Это отдельное решение координатора.
- `UNCHANGED_STD_COMPILE` на чистом merge: передать первую диагностику с `file:line` и выпуском rustc. Std-фазы не запускаются, пока merge не компилируется.
- Сбой импорта (`SOURCES_NOT_COMPLETED`, например недоступный fetch upstream): в `error.json` будет точное сообщение. Повтор без изменения пакета.
- Merge пригоден для будущего обновления pr752 отдельным шагом. Ветка pr752 не тронута.

## FIX2 после ревью R1

[Задание FIX2](REV2-VALIDITY-MAIN-REPIN-FIX2-TASK.md) · [Ревью R1](REV2-VALIDITY-MAIN-REPIN-REVIEW.md). Kani-кандидат, Std merge, overlay, оба bundle, fixture, roster, workflow и `CI-REQUEST.json` не изменились.

| Объект | R1 | FIX2 |
| --- | --- | --- |
| Control | `e4b3eced27aef7a926ae90b82a21411fcde24cc4` / tree `817a5db4e9eedc486148ec6018b9ce35685c0a93` | **`bf4e1d882a6a7247a87a7dac5890738507eb4d06`** / tree **`6d51ab4ed08f87d01d9be5f783c63f751a08e3ac`**, sole parent `e4b3eced27` |
| Review-trigger (`[skip ci]`) | `0650c59e24` | **`13e1ebf83ade3d25dbd6a4ee6d5e7b61c40ba8c2`**, tree `6d51ab4ed0`, sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`, ref `local/rev2-validity-repin-fix2-trigger-review` |
| Значение `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE` | `817a5db4e9…` | **`6d51ab4ed08f87d01d9be5f783c63f751a08e3ac`** |
| `request.py` | — | blob `9355c6192452c0f4f1d55e9aa3860801086f292c` |
| `test_sources.py` | — | blob `cb53bdc5714c3493a2eb030c6356feccd66df7a1` |
| `test_supervisor.py` | `5f7889280b9cac99471eda153a2477bfa49313c4` | **`df63a457c3adf648d360f3d559d5d40ef00a9427`** |
| Без изменений | `supervisor.py` `151af5b128…`, request SHA-256 `005ebf08…1fbe`, Std bundle `fbcab32c…ff9e`, Kani bundle `51ba5593…6843`, fixture `eb9575b0…`, workflow | те же |

Дельта `e4b3eced27..bf4e1d882a` затрагивает только три файла: `request.py` +35/−20, `test_sources.py` +54/−3, `test_supervisor.py` +222/−116. [Patch](/root/rev2-validity-repin-review/control-fix2-from-r1.patch), SHA-256 `d8fe4899…95a8`. Коммит от Tiramisu-Cake <igkharin@gmail.com> (автор и коммиттер), `[skip ci]`, без решётки перед цифрой.

### 1. Флейк escaped-descendant

**Причина.** Это тайминг теста, а не дефект supervisor. Старый тест ставил абсолютный дедлайн `+1,25 с` при TERM 0,2 с и KILL 0,5 с. В этот бюджет должны уложиться запуск двух Python-процессов, публикация `ready` и полный нативный census. Выборочный KILL по PID/start ID требует ещё двух census. Под нагрузкой бюджет кончается раньше, чем supervisor успевает отправить KILL_DESCENDANT. Supervisor при этом поступает правильно: он честно сообщает `REAP_UNVERIFIED` с живым потомком в `remaining_processes`. Production-гонки 5+5 с этот тест не измеряет.

**Воспроизведение до правки** на `5f78892…`: 10 прогонов только этого теста подряд под двумя busy-loop на 2 CPU (load 3–5). Итог: **9 падений из 10**, все `REAP_UNVERIFIED != TIMEOUT`. По receipt: START→REAP занимал 1,4–3,2 с, `KILL_DESCENDANT` не было ни разу, потомок оставался живым. В трёх случаях из девяти census до TERM вообще не увидел отделившегося потомка, `TERM_DESCENDANT` отсутствует. [Логи](/root/rev2-validity-repin-review/fix2-evidence/targeted/)

**Правка.** Побайтно принят reviewed-образец `df63a457c3adf648d360f3d559d5d40ef00a9427` из control-пакетов q-pilot, `/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/`, коммит `8e1603eef9`. Он прошёл [ревью self-test](REV2-SUPERVISOR-SELFTEST-REVIEW.md): R2 GO для `637387c038`. В g0 он принят в `423f971b2e` при том же исходном blob `5f78892…`. [Обоснование и сохранённые проверки](REV2-SUPERVISOR-SELFTEST-HANDOFF.md#сохранённые-проверки).

Что меняется по сути:
- Worker атомарно публикует PID после `SIG_IGN`.
- Тестовые часы переходят к TIMEOUT только после того, как нативный census увидел этот PID с нужными PPID и PGID.
- Затем TERM 0,5 с и KILL 6 с идут в реальном темпе через настоящий `_signal_owned`.
- Тест требует: TERM_DESCENDANT и KILL_DESCENDANT на тот же PID/start ID, `reaped=true`, пустые `remaining_processes` и `cleanup_errors`, статус `waitpid` −SIGKILL.
- Тестовый subreaper убирает orphan-процессы при падении.

`supervisor.py` (`151af5b128…`) не менялся: дефекта supervisor не найдено. После правки тот же целевой тест под той же нагрузкой прошёл **10/10**.

**Серия полного suite под нагрузкой.**
- **24 прогона подряд**, на каждом 110 тестов. Нечётные — `python3 -m unittest discover`, чётные — блок self-test из workflow с часами от 60 с.
- Фон: два `python3 -c 'while True: pass'` на 2 CPU всю серию, load average в начале прогонов 3,3–7,3.
- Результат: **24/24 OK**, 0 failures, 0 errors, 0 skipped. Время suite 45,5–76,7 с, медиана около 61 с. Это меньше трёх минут, которые даёт шаг `pins`.
- [Сводка и логи](/root/rev2-validity-repin-review/fix2-evidence/stress/summary.txt) · [скрипт](/root/rev2-validity-repin-review/fix2-evidence/stress.sh)

### 2. Точный путь отказа при отсутствующем upstream

В R1 `import_bundle` проверял prerequisite через `git cat-file -t`. Для отсутствующего объекта эта команда падала `CalledProcessError`, поэтому сообщение «bundle prerequisite … is missing» было недостижимо. Теперь отсутствие проверяет `git_probe(cat-file -e)`, и отказ идёт с этим сообщением до `bundle verify`/`unbundle`. Отдельная проверка типа выдаёт «is not a commit».

Тест `test_unconfirmed_parent_or_prerequisite_is_rejected` проверяет два точных пути:
- **`ensure_upstream` подменён без fetch.** Ожидается `ValueError` ровно `^bundle prerequisite <upstream> is missing$`. Подмена вызвана один раз, upstream и overlay в Std-checkout отсутствуют, refs нет, `source.json` в состоянии `RUNNING`.
- **Upstream SHA, которого remote не выдаёт.** Ожидается `CalledProcessError` именно из команды `fetch` с refspec `+<sha>:refs/ch8-rev2/upstream`. Refs нет, записи `upstream` в `source.json` нет.

На старом `request.py` первый сценарий падает с `CalledProcessError` из `cat-file -t`.

### 3. Проба `cat-file -e` ограничена дедлайном `sources`

- Общая функция `bounded(deadline, 30)` используется в `git`, новом `git_probe` и `git_blob`.
- Проба upstream в `ensure_upstream` и проверка prerequisites в `import_bundle` идут через `git_probe` с дедлайном шага.
- В том же шаге дедлайн теперь получают и чтения `git_blob`/`mode` в `check_tool_patch`, `std_pins` и `check_overlay_layout`. Раньше у них были фиксированные 30 с.
- После дедлайна процесс не запускается, сразу `TimeoutError("git deadline exhausted")`.

Новый тест `test_upstream_probe_and_blob_reads_are_bounded_by_the_sources_deadline` проверяет:
- исчерпанный дедлайн не порождает ни одного `subprocess.run`, ни для пробы, ни для `git_blob`;
- при окне 5 с проба `cat-file -e` получает timeout ≤ 5 с, остальные git-вызовы `ensure_upstream` тоже.

На старом коде тест падает: проба уходила с `timeout=30` даже при исчерпанном окне.

### Повторные проверки

- Без фоновой нагрузки (load около 2,9): `python3 -B -m unittest discover` — 110/110 за 33 с. Блок workflow с часами от 60 с — 110/110 дважды, 29 и 31 с.
- Статический импорт на реальных объектах (`static_import.py`, чистые shallow-репозитории без alternates): **PASS**. Головы Kani `4caf097d84` и Std `7f961eda87`, overlay `bc866f8dfa`, координаты PASS. Вывод совпадает с R1 везде, кроме времени. [Вывод](/root/rev2-validity-repin-review/static_import-fix2.out)
- `run.py pins` на detached trigger `13e1ebf83a` с синтетическим push:
  - tree `6d51ab4ed0` допущен, outputs `std=dab03cf510`, `tool=8c6dba5935`;
  - tree R1 `817a5db4e9` отклонён: `trigger tree mismatch`;
  - одна старая переменная отклонена: `missing or malformed`;
  - при отказе нет ни outputs, ни receipt.
- Self-test на checkout trigger: 110/110, checkout чистый.
- Workflow не менялся. PyYAML разобрал его, `bash -n` прошёл для семи shell-блоков, `git diff --check` чист. Rust-файлы не менялись, поэтому rustfmt не запускался.

### Для координатора

- Перед запуском значение `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE` должно быть `6d51ab4ed08f87d01d9be5f783c63f751a08e3ac`, а не `817a5db4e9…` из R1. Для запуска нужен новый коммит без `[skip ci]` с этим tree и родителем `467af9cb8d`.
- Совет из R1 в силе: после GO очистить старую `CH8_REV2_VALIDITY_MAIN_TRIGGER_TREE`, сейчас `697dc737fe`.
- Пункт 4 ревью, отсутствие `kani-verifier` в `8c6dba5935`, только информационный и правки не требует.
- Push, CI, изменений Actions variables, cargo/rustc/Kani/CBMC, установки toolchain и публикаций не было. Совместимость пары остаётся **UNKNOWN** до фазы 0.

## FIX3 после run 45857466917

[Задание FIX3](REV2-VALIDITY-MAIN-REPIN-FIX3-TASK.md), включая раздел «Уточнение по опубликованным receipts» (g0 `214d45d613`) · [Артефакты](/root/ch8-artifacts/run-45857466917/ch8-rev2-validity-repin-Linux-X64-45857466917-1/).

### Результат прогона

Фаза 0 — **PASS**: Kani `0.68.0 (4caf097)` на nightly-2026-11-21, CBMC 6.11.0, чистый Std merge `7f961eda87` скомпилирован. Пара совместима.

Фаза A — 18/18 `MISMATCH`, хотя нативные terminal и коды выхода совпали с ожиданием во всех 18 слотах. Причин две:
- гейт `unsupported_construct`: в каждом слоте 2–4 таких свойства со статусом `SUCCESS`;
- у трёх invalid-read ON по два `FAILURE` на одном typed read, а правило FIX1 требовало ровно один.

Фаза B — `NOT_RUN` по гейту A. Receipts и решение ledger остаются историческими записями, я их не менял.

### 1. Почему `SUCCESS`, а не `UNREACHABLE`

Ответ по исходникам кандидата `4caf097d84`.

- **Какое утверждение генерируется.** Все emit sites класса `unsupported_construct` на пине сводятся к `assert(false); assume(false)` в той точке, где выполнилась бы неподдерживаемая операция. Обёртка `codegen_assert_assume` для не-`Panic` классов — `assert.rs:137-174`. Emit sites:
  - `codegen_unimplemented_stmt` (`assert.rs:334-353`). Через него идёт `caller_location`: `intrinsics.rs:298` → `intrinsic.rs:769`.
  - `codegen_mimic_unimplemented` (`assert.rs:363-380`).
  - Вызов foreign-функции (`foreign_function.rs:262-277`).
  - `codegen_fatal_error` для неподдерживаемого intrinsic (`intrinsic.rs:100-104` → `assert.rs:276-284`).
  - Hook `UnsupportedCheck` (`hooks.rs:242-283`). Его вызывают `kani::unsupported` (`kani_core/src/mem.rs:197,268`, `iter.rs:159`) и вставки valid-value pass: `UnsupportedCheck` (`check_values.rs:150-155,355-366`), `unsupported_check_if` (`:263-270,277-320`) и `kani_intrinsics.rs:182-192`.
- **Парной reach-проверки нет.** `codegen_reachability_check` (`assert.rs:239-262`) вызывается только для `Assert`-терминаторов и assert/cover-hooks (`statement.rs:584`, `hooks.rs:118,230,388`). Kani-driver ставит `UNREACHABLE` только свойству с парной reach-проверкой со статусом `SUCCESS` (`cbmc_property_renderer.rs:540-575,669-690`). Поэтому у класса `unsupported_construct` статус `UNREACHABLE` на этом пине не возникает никогда. Гейт FIX1 «только `UNREACHABLE`» здесь невыполним.
- **Что означает `SUCCESS`.** CBMC доказал, что ни один путь в пределах границ не достигает этого `assert(false)`. Если хоть одно такое свойство `FAILURE` с текстом «is not currently supported by Kani», driver переводит все `SUCCESS` в `UNDETERMINED` (`:542-575`). Для условных семейств недостижима именно guarded-ветка, а сама функция может исполняться:
  - `same_allocation` — ветка, где ни один указатель не allocated (`mem.rs:266-270`);
  - untyped read — ветка `untyped` в `SwitchInt` (`check_values.rs:263-270,295-318`).
- **Unwinding assertions.** Kani передаёт CBMC только отрицательный флаг `--no-unwinding-assertions`, когда unwinding checks выключены. Когда они включены, он добавляет `--no-self-loops-to-assumptions` (`call_cbmc.rs:351-355`, `args/mod.rs:617-631`). Значит, при включённых проверках assertions даёт умолчание CBMC 6. Во всех 18 профилях `OBSERVED`:
  - есть `--unwind 16` и `--no-self-loops-to-assumptions`;
  - нет `--no-unwinding-assertions` и `--partial-loops`;
  - в argv Kani нет `--no-unwinding-checks` и `--no-default-checks`.

  Unwind records среди свойств нет ни в одном слоте. CBMC создаёт unwinding assertion там, где путь упирается в границу, поэтому отсутствие записей означает, что граница не срезала ни одного пути. Обязательный `unwind.SUCCESS` здесь был бы ложным блокером. Проваленная unwinding assertion сама переводит все `SUCCESS` в `UNDETERMINED` (`:544,565-569`).

Итог: `SUCCESS` у свойства установленного семейства означает «guarded-точка недостижима» при двух условиях: unwinding assertions подтверждённо включены, и ни одна unwind-проверка не провалена и не `UNDETERMINED`.

### 2. Гейт

`verdict.py`, функция `decide()` выделена из `project()`.

- `UNREACHABLE` чисто, как раньше. `SUCCESS` чисто, только если свойство относится к установленному семейству: класс `unsupported_construct` и в поле, и в точном ID, плюс `fullmatch` описания одного из четырёх семейств пина:
  - `intrinsic_caller_location`;
  - `foreign_call` (`Rust`/`C`, issue `new/choose`/`2423`);
  - `kani_same_allocation_guard` — точное сообщение `mem.rs:268`;
  - `untyped_read_validity_guard` (`check_values.rs:265-268`).
- `SUCCESS` установленного семейства требует подтверждённого профиля, иначе `UNKNOWN`:
  - наблюдённая CBMC-команда передаётся из `native_profile`, только при состоянии `OBSERVED`;
  - в ней `--unwind <n>` и `--no-self-loops-to-assumptions`, нет `--no-unwinding-assertions`/`--partial-loops`;
  - в argv Kani нет отключающих флагов;
  - все unwind/recursion records `SUCCESS`.
- `FAILURE`, `UNDETERMINED`, `ERROR`, неизвестный статус, неизвестное семейство и совпадение только по словам «unsupported construct» в описании дают `MISMATCH`, как в FIX1. Правило общее для фаз A и B.
- `run.py`: профиль считается до вердикта. Противоречие CBMC-команды запросу даёт `MISMATCH` и тогда, когда вердикт был `UNKNOWN` из-за неподтверждённого guard.

### 3. Привязанная группа typed read (второй блокер)

Kani ставит на одно typed read через сырой указатель две проверки с одним сообщением и одним span:
- `UntypedRead`: `visit_operand` → `check_untyped_read` (`check_values.rs:1054-1056,696-707`), условие «не untyped или значение валидно» (`:225-262`);
- `DerefValidity`: вложенный `visit_place` → `check_place_access` → `check_place_value` (`:976-980,819-827,796-810`).

Обе используют один `build_limits` для `char` с двумя интервалами (`:421-431`), так что это не две половины диапазона.

- **Request.** Добавлен ключ `read_groups`, roster и его digest `6a89e1e9…` не изменились. Для каждого из восьми A-корней с typed read закреплены column 29, class `safety_check`, type `char`, function = имя корня и точные ID. Пары ID: `.8`/`.11` у `copy_valid_read`, `.6`/`.9` у `nonoverlap_valid_read`, `.5`/`.8` у остальных шести. Файл и строку задаёт `read` корня. `load()` требует, чтобы группы покрывали ровно A-корни с read. `slots()` даёт `read_group` только ON-слотам A.
- **ON-negative MATCH.** Множество всех `FAILURE` совпадает с группой, все свойства группы `FAILURE`, cover сырой записи до чтения `SATISFIED`. Отказ дают:
  - сдвиг строки или столбца, другая функция, другой тип или класс;
  - пропуск или переименование ID;
  - третий отказ на месте или посторонний отказ;
  - `SUCCESS` у одной проверки пары.
- **Positive ON.** `read_binding=OBSERVED` только при полной опубликованной группе, иначе `UNKNOWN`. OFF и ON raw-only дают `NOT_REQUESTED`.
- **Фаза B** без группы сохраняет прежнее правило: одно свойство на read, один отказ.

Группы взяты из этого же прогона. Повтор на тех же receipts — проверка согласованности, а не независимое свидетельство. Независимой проверкой будет следующий прогон.

### 4. Офлайн-переклассификация

Скрипт `/root/rev2-validity-repin-review/fix3-offline/reclassify.py` читает 18 receipts как данные. Он запускается через `python3 -I` из отдельного каталога, без инструментов, и импортирует только `request.py`/`verdict.py` из control `0a4f85d930`.
- Строки roster берутся из FIX3-request. Roots совпадают с `request.json` прогона, отличие только в `read_groups`.
- CBMC argv берётся из `native_profile` каждого receipt.
- Результаты: [вывод](/root/rev2-validity-repin-review/fix3-offline/reclassify.out), SHA-256 `58aafc31…f06a`; скрипт `7a1a6135…506a`.

| Слот A | Expected | Terminal | CI | FIX3 | read_binding (ID группы) | Guards `SUCCESS` по семействам |
| --- | --- | --- | --- | --- | --- | --- |
| `copy_valid_read-off` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | NOT_REQUESTED (—) | foreign_call 1, intrinsic_caller_location 1, kani_same_allocation_guard 1 |
| `copy_valid_read-on` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | OBSERVED (`.8`, `.11`) | foreign_call 1, intrinsic_caller_location 1, kani_same_allocation_guard 1 |
| `copy_invalid_read-off` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | NOT_REQUESTED (—) | foreign_call 1, intrinsic_caller_location 1 |
| `copy_invalid_read-on` | FAILURE | `FAILED`, код 1 | MISMATCH | **MATCH** | OBSERVED (`.5`, `.8`) | foreign_call 1, intrinsic_caller_location 1 |
| `nonoverlap_valid_read-off` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | NOT_REQUESTED (—) | foreign_call 1, intrinsic_caller_location 1 |
| `nonoverlap_valid_read-on` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | OBSERVED (`.6`, `.9`) | foreign_call 1, intrinsic_caller_location 1, untyped_read_validity_guard 2 · усечение: 1 из 257, см. ниже |
| `nonoverlap_invalid_read-off` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | NOT_REQUESTED (—) | foreign_call 1, intrinsic_caller_location 1 |
| `nonoverlap_invalid_read-on` | FAILURE | `FAILED`, код 1 | MISMATCH | **MATCH** | OBSERVED (`.5`, `.8`) | foreign_call 1, intrinsic_caller_location 1 |
| `copy_overwritten-off` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | NOT_REQUESTED (—) | foreign_call 1, intrinsic_caller_location 1 |
| `copy_overwritten-on` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | OBSERVED (`.5`, `.8`) | foreign_call 1, intrinsic_caller_location 1 |
| `write_bytes_zero-off` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | NOT_REQUESTED (—) | foreign_call 1, intrinsic_caller_location 1 |
| `write_bytes_zero-on` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | OBSERVED (`.5`, `.8`) | foreign_call 1, intrinsic_caller_location 1 |
| `write_bytes_raw_only-off` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | NOT_REQUESTED (—) | foreign_call 1, intrinsic_caller_location 1 |
| `write_bytes_raw_only-on` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | NOT_REQUESTED (—) | foreign_call 1, intrinsic_caller_location 1 |
| `write_bytes_valid_read-off` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | NOT_REQUESTED (—) | foreign_call 1, intrinsic_caller_location 1 |
| `write_bytes_valid_read-on` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | OBSERVED (`.5`, `.8`) | foreign_call 1, intrinsic_caller_location 1 |
| `write_bytes_invalid_read-off` | SUCCESS | `SUCCESSFUL`, код 0 | MISMATCH | **MATCH** | NOT_REQUESTED (—) | foreign_call 1, intrinsic_caller_location 1 |
| `write_bytes_invalid_read-on` | FAILURE | `FAILED`, код 1 | MISMATCH | **MATCH** | OBSERVED (`.5`, `.8`) | foreign_call 1, intrinsic_caller_location 1 |

**Итог: 18/18 `MATCH`.** Все 8 ON-слотов с read дают `OBSERVED`, OFF и raw-only — `NOT_REQUESTED`.

У трёх negative выполнены cover сырой записи до чтения: `raw_copy_complete_before_read` у обоих copy-корней и `raw_write_complete_before_read` у `write_bytes_invalid_read`. Профиль `OBSERVED` во всех 18, unwinding `ENABLED_ALL_SUCCESS`, unwind records 0.

Контрфактический прогон с `--no-groups`, только с исправлением гейта, оставляет три negative в `MISMATCH`. Это подтверждает второй блокер. [Вывод](/root/rev2-validity-repin-review/fix3-offline/reclassify-no-groups.out)

**Усечение в `A-nonoverlap_valid_read-on`.** Свойств 257, опубликовано 256 (`MAX_EVIDENCE`). Разность полных `status_counts` receipt и сохранённого инвентаря — один `SUCCESS`. Сохранились:
- validity 31/31;
- unsupported 4/4 (foreign, caller_location и два untyped-read guard);
- failures 0/0, covers 2/2;
- обе проверки typed read на `:59`, `.6` и `.9`.

Пропущенная запись — чистая проверка вне anchors, поэтому решение `MATCH`. Пометка `binding_hidden_by_bounded_publish` сохранена. Если бы счётчики не сошлись, скрипт выдал бы `UNKNOWN`.

### 5. Тесты

Новые тесты в `test_verdict.py` (24, было 16):
- `SUCCESS` всех четырёх семейств при подтверждённом профиле — без unwind records и с `unwind.SUCCESS`;
- `FAILURE`/`UNDETERMINED`/`ERROR`/неизвестный статус блокируют;
- неподтверждённое семейство, чужое сообщение `kani::unsupported` и совпадение только по описанию блокируют;
- `SUCCESS` без профиля, без `--unwind` или маркера, с `--no-unwinding-assertions`/`--partial-loops`/`--no-unwinding-checks`/`--no-default-checks`, с проваленной или `UNDETERMINED` unwind- или recursion-проверкой даёт `UNKNOWN`;
- группа negative: девять отвергаемых вариантов и обязательный cover сырой записи;
- полнота группы для `OBSERVED`;
- правило одного свойства без группы (B);
- валидация `read_group` и `decide()`.

В `test_run.py` синтетический Kani теперь выдаёт закреплённую пару, foreign-guard `SUCCESS` и маркер unwinding во всех слотах. Добавлен e2e-тест: профиль без маркера даёт `UNKNOWN`, `--no-unwinding-assertions` — `MISMATCH` по профилю, проваленный `unwind` — не `MATCH`.

Suite: 119/119 за 36 с, на свежей шкале от 60 с — 119/119 дважды (38 с). На checkout trigger — тоже 119/119. YAML, `bash -n` для семи shell-блоков, `git diff --check` — чисто. Workflow не менялся.

### 6. Пины FIX3

| Объект | Значение |
| --- | --- |
| Control | **`0a4f85d930e47ffad9062131e6f57c6bde5989e6`**, tree **`c5752243969498403dc09f21404030ab702523ee`**, parent `bf4e1d882a` |
| Review-trigger (`[skip ci]`) | **`0aa3c3071c62808ed896519a752743e4bdf99804`**, tree `c575224396`, sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`, ref `local/rev2-validity-repin-fix3-trigger-review` |
| Новое значение `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE` (меняет координатор после GO) | **`c5752243969498403dc09f21404030ab702523ee`** |
| `CI-REQUEST.json` | SHA-256 **`553e9cd83cd4f0b9b280f0e445081e9a25b666d92df0f8bbdd7d4c0daf30fcf3`** (было `005ebf08…1fbe`), единственная дельта — ключ `read_groups` |
| Roster digest | `6a89e1e970d44938bef0bd2864d235d4f69f1e8cd46c1648adf3c7c87862deea`, без изменений |
| Blobs | `verdict.py` `40a166aa…`, `request.py` `d01a9070…`, `run.py` `a49d4d2f…`, `test_verdict.py` `eae1d6fd…`, `test_run.py` `def13033…` |
| Без изменений | Kani `4caf097d84`, Std merge `7f961eda87`, overlay `bc866f8dfa`, bundles `fbcab32c…`/`51ba5593…`, fixture `eb9575b0…`, roster, selectors, режимы, argv, workflow, `supervisor.py` |

Дельта `bf4e1d882a..0a4f85d930`:

| Файл | Строк добавлено / удалено |
| --- | --- |
| `CI-REQUEST.json` | +82 / −0 |
| `request.py` | +14 / −0 |
| `run.py` | +7 / −3 |
| `test_run.py` | +47 / −10 |
| `test_verdict.py` | +172 / −1 |
| `verdict.py` | +201 / −32 |

[Patch](/root/rev2-validity-repin-review/control-fix3-from-fix2.patch), SHA-256 `d2e41500…df6e`. Author и committer обоих коммитов — Tiramisu-Cake <igkharin@gmail.com>, `[skip ci]`, без решётки перед цифрой.

`run.py pins` на detached trigger `0aa3c3071c`: tree `c575224396` допущен, outputs `std=dab03cf510`, `tool=8c6dba5935`. Tree FIX2 `6d51ab4ed0` отклонён (`trigger tree mismatch`), без outputs и receipt. Checkout чистый.

### Риски следующего прогона

- **Фаза B.** По заданию B сохраняет правило одного свойства. Если на typed read в `validity_main.rs` Kani тоже поставит пару, `vv_stable_char_n09_corrupt` ON даст `MISMATCH`, а позитивные B — `read_binding=UNKNOWN`. Такой результат стал бы привязанным свидетельством для группы B следующим FIX.
- **Guards в Std-коде B.** Если B встретит семейство вне четырёх установленных, его `SUCCESS` блокирует по строгому правилу. Это ожидаемо и потребует разбора emit site.

Push, CI, Actions variables, cargo/rustc/Kani/CBMC не запускались. Публикаций не было.

## FIX4 после ревью R3

[Задание FIX4](REV2-VALIDITY-MAIN-REPIN-FIX4-TASK.md) · [Ревью R3](REV2-VALIDITY-MAIN-REPIN-REVIEW.md#r3--fix3). Дельта FIX3 сохранена. Kani, Std merge, overlay, bundles, fixture, roster, selectors, режимы, argv и workflow не менялись.

### 1. Структурная группа typed read в фазе B (блокер B1)

**Сверка по `check_values.rs` кандидата `4caf097d84`.** Чтения B `validity_main.rs:111` (`stable_char_n09_body::<CORRUPT_OUTPUT>`, общее для `vv_stable_char_n09` и `_corrupt`) и `:153` (`vv_sort8_char_n08`) имеют ту же форму, что чтения A, — `copy (*p)`, где `p` — временный `*const char`.

- `visit_operand` вызывает `check_untyped_read` (`:1054-1056`). Для `Deref` `may_be_untyped` истинно (`:656-659`), `char` sized, его требования непусты. Получается `UntypedRead` (`:696-707`): проверка «не untyped или значение валидно» без assume (`:225-262`).
- Затем `with_access(Read)` → `visit_place`. Место `[Deref]` проходит точный путь (`:976-980`), первый projection — `Deref` локала-указателя. Значит, `check_place_access` (`:819-827`) → `check_place_value` → `DerefValidity` (`:796-810`).
- Для `char` это один `ValidValueReq` с двумя интервалами (`:424-431`), то есть одна проверка на каждую операцию. Сообщения одинаковые: `` Undefined Behavior: Invalid value of type `char` `` (`:140,255`).
- Обе операции вставляются перед одной инструкцией, поэтому у них один span, одна функция и класс `safety_check`. Одна MIR-инструкция даёт два свойства, сколько бы раз её ни исполнял цикл `:152-153`.
- **Column.** Это 1-based позиция `*` в полной строке источника, как 29 в A:
  - `:111` — 4 + 21 + 1 = **26**;
  - `:153` — 8 + 21 + 1 = **30**.

  Новая проверка в `check_coordinates` сверяет это на этапе `sources`: в строке ровно одна `*`, и её позиция равна закреплённому column. Проверка действует для групп A и структур B. Статический импорт на реальном overlay `bc866f8dfa` её прошёл (`coordinates: PASS`), а неверный column 29 для `:153` отвергнут.
- **Внутренние чтения (`internal_reads`, `smallsort.rs`).** Формы вроде `is_less(&*a, &*b)` — заимствование через сырой указатель (`Rvalue::Ref`, `SharedBorrow`, `:1231`). Ветка `Rvalue::Ref` для них пропускает `check_untyped_read` (`:1213-1216`), остаётся только `DerefValidity` через `check_place_access`. Это одно свойство на операнд, не пара.

  `tail.read()`/`ptr::read(..)` читают внутри `core::ptr::read`, свойство там имеет location `ptr/mod.rs`, а не строку `smallsort.rs`. Внутренние чтения в решение не входят: они публикуются как сопоставленные или `UNKNOWN` по строке. Правило пары к ним не применяется, менять ничего не нужно.

**Правило.** Request получил ключ `read_structures` для трёх `char`-корней B: column 26/26/30, class `safety_check`, type `char`, count 2. ID в нём нет. `slots()` даёт `read_structure` только ON-слотам. Требования:
- на `row.read` (file + line) ровно два validity-свойства;
- у обоих column равен закреплённому, функция F из location одна;
- ID различны и каждый `fullmatch` `re.escape(F) + r'\.safety_check\.[0-9]+'`;
- класс `safety_check` и в поле, и в ID;
- description ровно `` Undefined Behavior: Invalid value of type `char` ``.

Для отрицательного слота дополнительно:
- множество всех `FAILURE` равно этой паре, обе `FAILURE`;
- нужный cover `SATISFIED`;
- terminal `FAILED`, exit ≠ 0.

Одно или три свойства, другой column, функция, тип или класс, ID вне F, дубликат ID, посторонний `FAILURE` или отсутствие cover дают `MISMATCH`. У положительных слотов `read_binding=OBSERVED` только при этой структуре, иначе `UNKNOWN`.

Корни `bool` и `NonZeroU8` (`:54`, `:70`, `:179`) сохраняют правило одного свойства. Это положительные слоты, поэтому пара там даст только `read_binding=UNKNOWN`, вердикт не изменится. Строка с одновременно `read_group` и `read_structure` даёт `UNKNOWN`.

**Остаточный риск.** Column 26 для `:111` получен так же, как в A: инициализация `let x = unsafe { *p }`, совпавшая с наблюдением 29. Для `:153` форма другая: присваивание `output[i] = unsafe { *p }`. Её column 30 выведен из того же правила (span хвостового выражения блока), но прогоном не подтверждён. Если он окажется другим, `vv_sort8_char_n08` ON получит `read_binding=UNKNOWN`, а MATCH сохранится. Единственный отрицательный слот B читает `:111`.

### 2. Порядок решений (R3, неблокирующее 1)

Ветка «guard не установлен → `UNKNOWN`» вынесена в конец. Она лишь удерживает уже полученный `MATCH`. Раньше неё решаются:
- блокирующий `unsupported_construct`;
- неверный terminal или код;
- `FAILURE` не там, где ожидается, `UNDETERMINED` в положительном слоте;
- отсутствующий cover.

Все они дают `MISMATCH` и при неподтверждённом профиле. Пример: проваленная unwind-проверка в положительном слоте теперь `MISMATCH`, а состояние `NOT_SUCCESS` по-прежнему публикуется в `unwinding_assertions`.

### 3. Флаги CBMC (R3, неблокирующее 2)

К отсекаемым добавлены `--depth`, `--unwindset`, `--no-assertions` и `--cover`, вместе с прежними `--no-unwinding-assertions` и `--partial-loops`. Флаг совпадает и как точный токен, и в форме `flag=value`. Проверяются CBMC argv и argv Kani (через `--cbmc-args`), в argv Kani дополнительно `--no-default-checks`/`--no-unwinding-checks`.

Белый список я не выбрал. Argv фиксирован запросом, а профиль уже требует `--unwind <n>` и `--no-self-loops-to-assumptions`, поэтому чёрный список здесь закрывает все известные способы ослабить границу.

### 4. Тесты и проверки

- `test_verdict.py`, 26 тестов.
  - B-структура: пара → `MATCH`/`OBSERVED`/`STRUCTURAL`. Отвергаются: одно, три, другой column, другая функция, ID вне F, дубликат ID, другой тип, другой класс, `SUCCESS` у одной из пары, посторонний `FAILURE` — всё `MISMATCH`. Отсутствие cover — `MISMATCH` с `missing_covers`. У положительного одно свойство или другой column дают `UNKNOWN`. Одновременные group и structure дают отказ.
  - Порядок решений: проваленная или `UNDETERMINED` unwind-проверка, recursion и посторонний assertion в положительном слоте — `MISMATCH` с профилем и без. У отрицательного без профиля `FAILURE` не там, неверный terminal и отсутствие cover — `MISMATCH`, точная пара — `UNKNOWN`. Пара с `UNDETERMINED`-unwind даёт `UNKNOWN` (`NOT_SUCCESS`).
  - Флаги: `--depth`, `--unwindset` (и с `=`), `--no-assertions`, `--cover`, `--depth` через argv Kani — guard `UNKNOWN`.
- `test_run.py`:
  - синтетический Kani выдаёт структурную пару для трёх `char`-корней B, все 30 слотов `MATCH`;
  - сдвиг отступа строки чтения при том же тексте отвергается как `pinned read column`;
  - проваленный unwind в e2e — `MISMATCH`.
- Suite 121/121 штатно и дважды на свежей шкале от 60 с (31–32 с). На checkout trigger — 121/121, checkout чистый. YAML, `bash -n` для семи shell-блоков, `git diff --check` — чисто.
- **Офлайн-replay 18 receipts A** скриптом FIX3 (`python3 -I`): **18/18 `MATCH`**, 8 `OBSERVED`. Вывод побайтно совпал с FIX3 (`58aafc31…f06a`). [Вывод](/root/rev2-validity-repin-review/fix4-replay.out)
- Статический импорт на реальных объектах: `PASS`, координаты и column `PASS`. [Вывод](/root/rev2-validity-repin-review/static_import-fix4.out)
- `run.py pins` на detached trigger `b0ce856748`: tree `f46e65c42c` допущен, outputs `std=dab03cf510`, `tool=8c6dba5935`. Tree FIX3 `c575224396` отклонён без outputs и receipt.

### 5. Пины FIX4

| Объект | Значение |
| --- | --- |
| Control | **`e2a3e6d48e98693074f51e93369917948f6790bf`**, tree **`f46e65c42c7ddb45a725569265b8dc7c0fd7a88a`**, parent `0a4f85d930` |
| Review-trigger (`[skip ci]`) | **`b0ce856748185bdfa3ac20969cbaa72f13841272`**, tree `f46e65c42c`, sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`, ref `local/rev2-validity-repin-fix4-trigger-review` |
| `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE` (меняет координатор после GO) | **`f46e65c42c7ddb45a725569265b8dc7c0fd7a88a`** |
| `CI-REQUEST.json` | SHA-256 **`bdd69de4e0245ad241b22b144a104fdb69256d6c2fb1620d26eda57ccf76a6a2`** (было `553e9cd8…fcf3`). Дельта — ключ `read_structures`, `read_groups` не изменился |
| Roster digest | `6a89e1e970d44938bef0bd2864d235d4f69f1e8cd46c1648adf3c7c87862deea`, без изменений |
| Blobs | `verdict.py` `e37dd3bf…`, `request.py` `cb694efb…`, `test_verdict.py` `46ce8d6b…`, `test_run.py` `a156b6ea…`; `run.py` без изменений |

Дельта `0a4f85d930..e2a3e6d48e`:

| Файл | Строк добавлено / удалено |
| --- | --- |
| `CI-REQUEST.json` | +20 / −0 |
| `request.py` | +18 / −0 |
| `verdict.py` | +67 / −16 |
| `test_verdict.py` | +104 / −4 |
| `test_run.py` | +21 / −7 |

[Patch](/root/rev2-validity-repin-review/control-fix4-from-fix3.patch), SHA-256 `199adf9c…c7d3`. Author и committer обоих коммитов — Tiramisu-Cake <igkharin@gmail.com>, `[skip ci]`, без решётки перед цифрой.

R3 неблокирующие 3 (семейства по тексту) и 4 (replay A — проверка согласованности) остаются как отмечено: их снимет следующий прогон.

Push, CI, Actions variables, cargo/rustc/Kani/CBMC не запускались. Публикаций не было.

## FIX5 по разбору фазы B

[Задание FIX5](REV2-VALIDITY-MAIN-REPIN-FIX5-TASK.md) · [Разбор фазы B](REV2-VALIDITY-MAIN-REPIN-B-ANALYSIS.md) (g0 `daf13e3d1a`). Пакет собран по разделу 4 разбора. Kani-кандидат `4caf097d84` и Std merge `7f961eda87` не менялись, bundle Kani тот же.

### 1. Overlay `validity_main.rs`

Новый коммит **`fe3fe324bf`** (tree `0289b60ea3`) поверх `bc866f8dfa`. Меняется только диагностический модуль (+83/−27, blob `141b3d3128`). Delta merge → overlay — те же три пути: `M Cargo.toml`, `M smallsort.rs`, `A validity_main.rs`. `smallsort.rs` не тронут, поэтому все внутренние координаты, включая `:423`, прежние.

- **Чтение через заранее взятый указатель.** Во всех корнях B указатель берётся отдельной строкой: `let values_ptr = values.as_ptr();`, в `stable` — `as_mut_ptr()` до порчи. Строка чтения — `let first = unsafe { *values_ptr };`, а в `sort8` — `output[i] = unsafe { *dst_ptr.add(i) };`. Проверки `[T; N]` от autoref остаются на строке взятия указателя. На строке чтения — только пара элемента.
- **`bool`.** `bool_less(a, b) = (*a as u8) < (*b as u8)`. `check_sorted_and_full_multiset` получает компаратор `less: F` (`F: Fn(&T, &T) -> bool`, без function pointer) и проверяет сортированность им. Граница `T: Copy + Eq`. Covers `vv_swap_bool_n02` тоже переведены на `bool_less`.
- **Ранговый домен.**
  - `ranked_chars::<N>()`: `kani::any::<[char; N]>()` плюс `assume(c as u32 < N)`. Используется в `vv_stable_char_n09`/`_corrupt` (< 9) и `vv_sort8_char_n08` (< 8).
  - `ranked_nonzero::<N>()`: `get() ≤ N`. Используется в network n10/n18.
  - Обоснование ранговым аргументом — в комментарии модуля.
  - `vv_fallback_nonzero_n03` не тронут, кроме формы чтения.
- **Corrupt.** `stable_char_n09_body::<true>` пропускает функциональную проверку: остаются covers, порча через `values_ptr.cast::<u8>()` и типизированное чтение.
- **Network.**
  - `vv_network_nonzero_n10` — no-merge: `sort9_optimal` и один `insert_tail` (ветка `region.len() >= 9`).
  - `vv_network_nonzero_n18` — merge, только ON. Covers до приведения: «split into two 9 element halves» и «right last element precedes left first element». Cover «… even merge, copy-back returned» закреплён как UNREACHABLE.
- **Формат.** rustfmt `nightly-2026-11-19` с настройками rust-lang (`style_edition 2024`, `use_small_heuristics = "Max"`), под которые старый файл проходит без диффа: `FMT_OK`.
- **Bundle `std-overlay.bundle`.** Prerequisites прежние (`dab03cf510`, `f94155ef29`), HEAD `fe3fe324bf`, SHA-256 **`92e618444d81d3595ebf0d0c0bf120ff57ef45a681f2a4569b006ae09957bae2`**.
- **Цифры запроса.**
  - `OVERLAY_DELTA_SHA256` — `a61e0eb4…df1a`;
  - `OVERLAY_CHAIN` получил третью пару;
  - комментарий у `OVERLAY_SOURCE_CHAIN` уточнён: FIX1-реплей — первые два коммита.

### 2. Fixture A: четыре probe

`validity_fixture.rs` +41 строка, SHA-256 `948abd15…f8ad`, rustfmt Kani — чисто. Существующие девять корней и их строки не сдвинуты: probes дописаны в конец.

| Probe | OFF | ON |
| --- | --- | --- |
| `bool_order_probe`: `kani::assert((a < b) == (!a && b), …)`, `:178:5` | `ASSERTION_FAILURE_PINNED` | `ASSERTION_FAILURE_PINNED` |
| `bool_order_u8_control`: то же через `as u8` | SUCCESS | SUCCESS |
| `array_elem_cast_nonzero`: `MaybeUninit<[NonZeroU8; 4]>` → `*mut NonZeroU8`, запись, `:198:19` | SUCCESS | `UNSUPPORTED_PINNED`, cover `write_complete` UNREACHABLE |
| `array_elem_cast_u8_control`: то же для `u8` | SUCCESS | SUCCESS |

У `array_elem_cast_nonzero` cover `write_complete` — off-only. Это допускается только потому, что тот же cover назван в unreachable-списке pin.

**Probes не гейтят.** Они решаются как любой слот, но `run_phase` считает их отдельно: `probe_status` в `phase-A.json`, `phases.A_probes` в `SUMMARY.json`. Статус фазы A считается только по 18 прежним слотам, поэтому неожиданный исход probe не блокирует B. В `diagnostic_status` probes входят: `EXPECTED_OUTCOMES` требует и `A_probes=PASS`. Тест закрепляет все три свойства.

Тип в описании unsupported для standalone crate заранее не известен (в `core` он печатается как `num::nonzero::NonZero<u8>`). Поэтому fixture-pin задан `fullmatch`-шаблоном: путь `(core::|std::)?num::(nonzero::)?NonZero<u8>`, длина `4`. Тип и длина фиксированы, допускается только вариант пути. Шаблон записан литералом, а не через `re.escape`, чтобы frozen JSON не зависел от версии Python.

### 3. Гейт

**Классы** (`verdict.py`). Pin задаётся в request `pinned_failures[root][mode]` с ключами `kind, class, function, file, line, column, anchor, description | description_pattern, unreachable_covers`.

Свойство совпадает с pin, только если совпадают все поля:
- file по суффиксу, line и column;
- функция из location — точно;
- class и в поле, и в ID;
- ID — `fullmatch` `re.escape(function).class.N`;
- description — точно, либо `fullmatch` шаблона.

Решение для pinned-слота:
- terminal `FAILED` и exit ≠ 0, иначе MISMATCH;
- ровно одно совпадение, со статусом `FAILURE`, и множество всех `FAILURE` равно ему, иначе MISMATCH;
- нет другого статуса вне SUCCESS/UNREACHABLE и нет validity-свойств в OFF, иначе MISMATCH;
- если всё выполнено: `ASSERTION_FAILURE_PINNED` → `MATCH`, `UNSUPPORTED_PINNED` → **`MATCH_KNOWN_LIMITATION`**;
- каждый `unreachable_covers` присутствует и весь UNREACHABLE, иначе MISMATCH; при скрытии bounded publish — UNKNOWN;
- обязательные covers и правило «guard не установлен → UNKNOWN» действуют как прежде и для `MATCH_KNOWN_LIMITATION`.

**Общее правило unsupported не ослаблено.** Из него выводится только одно свойство: единственное совпадение с unsupported-pin, и только при статусе `FAILURE`. Второе совпадение, совпадение со статусом SUCCESS, другой unsupported `FAILURE`, другой тип или координата оставляют прежний MISMATCH «reachable or undecided unsupported_construct».

Валидация строки (`_pinned_error`) возвращает UNKNOWN, если:
- unsupported-pin стоит в OFF;
- assertion-pin задаёт unreachable covers;
- pin на validity-negative;
- unreachable cover одновременно обязательный;
- не совпадает пара kind/class, ключи или column < 1;
- шаблон не компилируется.

Request (`check_expectations`) отвергает:
- pin на negative, неизвестном корне или в незапускаемом режиме;
- лишние ключи, неизвестный kind, несоответствие class;
- пустые, повторные или неизвестные mode-наборы;
- probe вне фазы A.

**Координаты на этапе `sources`.** `check_coordinates` сверяет: `anchor` начинается ровно с закреплённого column закреплённой строки, а каждый unreachable cover встречается в источнике один раз. Проверено на реальном overlay:
- `smallsort.rs:423:28` начинается с `stack_array.as_mut_ptr() as *mut T;`;
- в fixture `:178:5` и `:198:19`.

**`read_structures` — для всех семи корней B.**

| Корень | Чтение | Column | Type |
| --- | --- | --- | --- |
| `vv_swap_bool_n02` | `:80` | 26 | `bool` |
| `vv_fallback_nonzero_n03` | `:97` | 26 | `num::nonzero::NonZero<u8>` |
| `vv_stable_char_n09` / `_corrupt` | `:143` | 26 | `char` |
| `vv_sort8_char_n08` | `:186` | 30 | `char` |
| `vv_network_nonzero_n10` | `:210` | 26 | `num::nonzero::NonZero<u8>` |
| `vv_network_nonzero_n18` | `:235` | 26 | `num::nonzero::NonZero<u8>` |

Count у всех 2. Load требует, чтобы структуры покрывали ровно все чтения B. Строки типа для `NonZero` взяты из описаний receipts run 45870184232: `:70:26`, `:179:26`.

**`cbmc_ignoring_warnings`** (non-gating) в `native_metrics` по stdout и stderr: число вхождений `warning: ignoring` по всему захвату (длинные JSON-строки не теряются) и координата первого, без текста выражения.

**Режимы.** `ROOT_MODES = {vv_network_nonzero_n18: ["on"]}`. `slots()` порождает слоты по режимам, `phase_slot_count` считает их сумму. В слотах и receipts появились поля `probe` и `pinned`.

### 4. Roster и ожидания

**A — 26 слотов.** 18 прежних, без изменений (8 закреплённых групп чтения, 3 отрицательных ON), плюс 8 probe-слотов из таблицы выше.

**B — 13 слотов:**

| Корень | OFF | ON |
| --- | --- | --- |
| `vv_swap_bool_n02` | SUCCESS | SUCCESS, структура `bool` |
| `vv_fallback_nonzero_n03` | SUCCESS | SUCCESS, структура `NonZero<u8>` |
| `vv_stable_char_n09` | SUCCESS | SUCCESS, структура `char` |
| `vv_stable_char_n09_corrupt` | SUCCESS | **FAILURE** = ровно пара `char` на `:143` |
| `vv_sort8_char_n08` | SUCCESS | SUCCESS, структура `char` |
| `vv_network_nonzero_n10` | SUCCESS | SUCCESS, структура `NonZero<u8>` |
| `vv_network_nonzero_n18` | — | **`UNSUPPORTED_PINNED`** → `MATCH_KNOWN_LIMITATION`, без validity-кредита |

Строки `writes` и `internal_reads` для n10/n18 взяты из n19 по маршруту:
- n10: swap `:497-498`, вставка `:682`, `:362`; чтения `:483`, `:496`, `:666`, `:675`, `:691`;
- n18: только swap `:497-498`; чтения `:483`, `:496`.

Запись порчи — новая строка `validity_main.rs`. Корни собраны скриптом из FIX4-запроса и текстов источников: [build_roots.py](/root/rev2-validity-repin-review/fix5/build_roots.py).

### 5. Часы

| Блок | FIX4 | FIX5 |
| --- | --- | --- |
| Phase 0 | 1800 | 1800 |
| A (слоты × (cold + reap 10 + receipt 5 + headroom 5)) | 18 × 65 = 1170 | **26 × 50 = 1300** |
| B setup | 1800 | 1800 |
| B | 12 × 200 = 2400 | **13 × 200 = 2600** (+195 окна +5 headroom) |
| Post-attestation, finalize, publication | 120 + 300 + 420 | без изменений |
| Сумма / job 140 мин | 8010 / 8400 | **8340 / 8400**, запас 60 с |

С прежним A cold 45 с план занял бы 8730 с и не уложился бы в 140 мин: +520 с на 8 probe-слотов и +200 на B. Поэтому **A cold cap снижен с 45 до 30 с**. Обоснование: в run 45857466917 и run 45870184232 самый долгий из 36 A-слотов шёл 0,95 с cold wall. Пределы B не менялись: 180 с cold wall, 120 с VT, caps 4 GiB на слот и 10 GiB на setup.

Таймауты шагов workflow: `phase-a` 21 → **23** мин (бюджет 1300 + 60 с), `phase-b` 80 → **81** мин (1800 + 2600 + 120 + 300 с). Job по-прежнему 140 мин. Тест бюджетов шагов это проверяет.

Альтернатива, если координатор не хочет трогать A cap: убрать `vv_sort8_char_n08` OFF (12 слотов B). Тогда понадобилось бы ещё снизить phase 0 (наблюдалось 207–234 с из 1800).

### 6. Тесты и replay

**Синтетика новых классов** (`test_verdict.PinnedFailureTests`, 8 тестов):
- **точное свойство:** assertion OFF/ON → `MATCH`; unsupported → `MATCH_KNOWN_LIMITATION`; шаблон принимает три рендеринга пути и отвергает `[u8; 4]`;
- **лишний FAILURE:** посторонний assertion, второй unsupported `FAILURE` на другой строке, двойное точное совпадение, `UNDETERMINED`-проверка — MISMATCH;
- **другой тип или координата:** длина 31, `NonZero<u16>`, другой construct, line ± 1, column ± 1, другая функция (другой компаратор), другой файл, класс в ID, чужое описание assertion — MISMATCH, `matched_ids` пуст;
- **cover reachable у `UNSUPPORTED_PINNED`:** SATISFIED / UNSATISFIABLE / UNDETERMINED → MISMATCH с `reached_covers`; отсутствующий cover → MISMATCH; обязательный cover по-прежнему обязателен;
- **terminal и код:** pin со статусом SUCCESS и terminal SUCCESSFUL, FAILED с exit 0 — MISMATCH; pinned unsupported со статусом SUCCESS — MISMATCH по общему правилу;
- **guard:** `MATCH_KNOWN_LIMITATION` без наблюдаемого профиля → UNKNOWN;
- **валидация:** девять видов неверной строки → UNKNOWN.

**Run-уровень** (`test_run.py`):
- все 39 синтетических слотов дают ожидаемое: n18 — `MATCH_KNOWN_LIMITATION`, остальные `MATCH`, `read_binding=OBSERVED` у каждого ON с чтением;
- probe с неподтверждённой гипотезой → A `PASS`, `A_probes=UNEXPECTED`, B запускается и даёт `PASS`, `diagnostic_status=INCOMPLETE_OR_UNEXPECTED`; гейтящий слот по-прежнему гейтит;
- n18 без приведения и с достигнутым cover → MISMATCH, receipt несёт `pinned`;
- сдвиг строки probe → `pinned failure coordinate`, переименованный unreachable cover → `cover description`;
- `check_expectations` отвергает 12 мутаций;
- счётчик `warning: ignoring` находит вхождение и в строке длиннее 4096 байт, текст не публикует;
- мутации запроса: `pinned_failures`, `probes`, `root_modes`, `read_structures`, off-only cover без pin;
- часы и бюджеты шагов пересчитаны.

**Suite 133/133:**
- штатно — 34 с;
- дважды на свежей шкале от 60 с — 32 и 33 с;
- на checkout trigger `a41dcc74de` — 133/133, checkout чистый.

YAML разбирается, `bash -n` по всем семи `run`-блокам чисто, `git diff --check` чисто, rustfmt нового Rust-кода: `FMT_OK` для overlay и fixture.

**Replay A** (`python3 -I`, receipts как данные). Скрипт FIX3 `reclassify.py`, у которого изменён только фильтр roster: строки берутся из FIX5-запроса для корней прогона, и они проверяются на равенство корням `request.json` прогона ([reclassify5.py](/root/rev2-validity-repin-review/fix5/reclassify5.py)).
- **run 45870184232: 18/18 MATCH**, вывод побайтно равен выводу того же скрипта с FIX4-control (`0a243b90…`);
- run 45857466917: 18/18 MATCH, побайтно `58aafc31…` (как в FIX3/FIX4).

**Replay B run 45870184232.** Строки — FIX4-ряды самого прогона, verdict — FIX5 ([replay.py](/root/rev2-validity-repin-review/fix5/replay.py), [вывод](/root/rev2-validity-repin-review/fix5/replay-B-45870184232-run-rows.out)). Гейт не падает, все 12 исходов совпадают с CI:
- `swap_bool` OFF/ON — MISMATCH (terminal);
- fallback OFF/ON — MATCH;
- семь TIMEOUT — INCOMPLETE;
- network n19 ON — MISMATCH (unsupported).

**Pin на реальном выводе.** Pin n18 перенесён на receipt n19 ON с его собственным пост-merge cover ([вывод](/root/rev2-validity-repin-review/fix5/pin-on-n19.out)):
- точный pin → **`MATCH_KNOWN_LIMITATION`**: ID, функция, координата и описание `[NonZero<u8>; 32]` совпадают с реальным выводом Kani;
- line+1, длина 31, достигнутый cover → MISMATCH.

Решение принято по 256 опубликованным записям из 1651; в CI гейт видит все.

**Статический импорт** на реальных объектах (чистые shallow-репозитории, точные базы, без alternates): `PASS`; bundle-импорт `fe3fe324bf`, delta merge → overlay, координаты, column и pins — `PASS` ([вывод](/root/rev2-validity-repin-review/static_import-fix5.out)).

**`check_trigger` на detached trigger `a41dcc74de`:** tree `e9b8b46457` допущен, parent `467af9cb8d`; tree FIX4 `f46e65c42c` отклонён («trigger tree mismatch»).

### 7. Риски

- **`bool_order_probe`** — гипотеза разбора. Если `<` на `c_bool` всё же кодируется, probe даст MISMATCH и `A_probes=UNEXPECTED`, но B пройдёт. Тогда `vv_swap_bool_n02` покажет, был ли дефект в обмене.
- **Описание в fixture** может отличаться от шаблона сильнее, чем вариантом пути. Тогда `array_elem_cast_nonzero` ON даст MISMATCH и только `A_probes=UNEXPECTED`.
- **Время B.** Ранговый домен должен снять финальный UNSAT, но прогоном это не подтверждено. При TIMEOUT следующий шаг из разбора — разделить корни на validity-only и функциональные. n18 ON обрезается на `:423`, как n19 ON (85 с).
- **Column 30 для `:186`** (`output[i] = …`) выведен, но не подтверждён, как и `:153` в FIX4. При расхождении только `read_binding=UNKNOWN` у положительного `sort8` ON.
- **Запас часов** — 60 с. Пределы расчётные и не зависят от длительности слотов.

### 8. Пины FIX5

| Объект | Значение |
| --- | --- |
| Std overlay | **`fe3fe324bfccaf309b5c5e20ce28dccd7759b45c`**, tree **`0289b60ea3228cf2fbac93865b33cd5564dc9de1`**, parent `bc866f8dfa`; chain `cac978ee46` → `bc866f8dfa` → `fe3fe324bf` |
| `std-overlay.bundle` | SHA-256 **`92e618444d81d3595ebf0d0c0bf120ff57ef45a681f2a4569b006ae09957bae2`** |
| Overlay delta (`--raw`) | SHA-256 `a61e0eb406a91c82f443085cf595bb280690ab187fb9fcb47d14142d3dbadf1a` |
| Fixture | SHA-256 `948abd1573a0a41644d9987899da2426a37d12198988695d8c939523977bf8ad` |
| Roster digest | `1f5826b797c510cefae04d1fdb69f50e36e9fd7f61895e2202efe9a99e5daeea` |
| `CI-REQUEST.json` | SHA-256 **`ebd7d551946e0e4b731fc428197b0778423087467e6f830fc80216d016b17f68`** |
| Control | **`fc3a0e654efe2076c5e9d0139ac6cd8d5b62eae2`**, tree **`e9b8b464573e3bb534df18c8ab86f2508366c6c5`**, parent `e2a3e6d48e` |
| Review-trigger (`[skip ci]`) | **`a41dcc74deb282a1f22de64092a2cb2251b8fed0`**, tree `e9b8b46457`, sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`, ref `local/rev2-validity-repin-fix5-trigger-review` |
| `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE` (меняет координатор после GO) | **`e9b8b464573e3bb534df18c8ab86f2508366c6c5`** |
| Kani, Std merge, tool bundle | без изменений: `4caf097d84`, `7f961eda87`, `51ba5593…6843` |

Diffstat control от FIX4:

| Файл | Строки |
| --- | --- |
| `verdict.py` (`3a365a844a`) | +99 / −6 |
| `request.py` (`9c45d2692c`) | +113 / −24 |
| `run.py` (`b972182cc6`) | +17 / −9 |
| `native_metrics.py` (`58223492d4`) | +12 / −0 |
| `validity_fixture.rs` (`674ceb2f4d`) | +41 / −0 |
| `CI-REQUEST.json` (`4bcbf741c5`) | +225 / −54 |
| `test_verdict.py` (`f72f851556`) | +158 / −0 |
| `test_run.py` (`0f8f4e6c14`) | +175 / −26 |
| `ch8-q-pilot.yml` (`c7ee165b06`) | +3 / −3 |
| `std-overlay.bundle` | заменён |

[Patch control](/root/rev2-validity-repin-review/control-fix5-from-fix4.patch), SHA-256 `c4b51c2d…ab7b`. [Patch overlay](/root/rev2-validity-repin-review/fix5/std-overlay-fix5-from-fix4.patch), SHA-256 `5341fab5…f6c7`. Author и committer overlay, control и trigger — Tiramisu-Cake <igkharin@gmail.com>, `[skip ci]`, без решётки перед цифрой.

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE` · ledger Item 2. Push, CI, Actions variables, cargo/rustc/Kani/CBMC не запускались, toolchain не ставился (rustfmt — локальный бинарь, разрешённый владельцем). Публикаций не было.
