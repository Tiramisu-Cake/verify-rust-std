# REV2 · валидность на Kani main с nightly 11-21 · handoff

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE` · ledger **Item 2** · control **`e4b3eced27`**, tree `817a5db4e9`. Инструмент в отчётах — **«Kani main `8c6dba5935` с nightly-2026-11-21»**: это не upstream-коммит, а локальный кандидат `4caf097d84`. [Задание](REV2-VALIDITY-MAIN-REPIN-TASK.md) · [Записка координатора](COORD-NOTE-20261126-VALIDITY-PIN-AND-KANI5196-RECHECK.md) · [FIX1](REV2-VALIDITY-MAIN-HANDOFF.md)

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
