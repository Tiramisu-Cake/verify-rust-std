# Повтор диагностики kani5196 · Item 1

`status=READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`

Пакет для одного Ubuntu job проверяет воспроизведение ITER и SELECT на новой голове kani5196. Он сравнивается с `45163409005` на Kani `bcdc1a0f8dc566654da1f18b4e502f0f4e7ad40a` и `nightly-2026-11-19`. В сравнении меняются Kani и nightly, поэтому причинность отдельного изменения требует отдельного эксперимента. [Задание](DIAG-RECHECK-TASK.md) · [Предыдущие наблюдения](DIAG-RUN-45163409005-ANALYSIS.md)

## Локальные коммиты

| Поле | Значение |
| --- | --- |
| Worktree | `/root/kani-ch8-kani5196-diag-recheck-control-20261126` |
| Control branch | `ch8-kani5196-diag-recheck-control` |
| Control commit | `5ff3ce873558c80003b32851bc2223988f098ca4` |
| Control parent | `5b5aa3cb619d65378d691cf5ad05a48cce341a9c` |
| Control parent tree | `5a7cb9a17c58218475865915aa2e8326f7f0364a` |
| Control tree | `e1791b8ff50ed9d6b486acfee8d2c687ee22d6a8` |
| Review-trigger branch | `ch8-kani5196-diag-recheck-review-trigger` |
| Review-trigger commit | `1db313afad71517f56e1f91d6b552d2415582274` |
| Review-trigger tree | `e1791b8ff50ed9d6b486acfee8d2c687ee22d6a8` |
| Единственный родитель review-trigger | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Author и committer обоих коммитов | `Tiramisu-Cake <igkharin@gmail.com>` |
| SHA-256 CI-REQUEST.json | `600e301506ff42bc037209a31818a53ba44d90367dee3a5c4a71d48fd53c0db3` |

Control и review-trigger локальные, оба с `[skip ci]`. Событие `push`, репозиторий `Tiramisu-Cake/kani`, ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt `1` и parent gate сохранены. В workflow изменено только отображаемое имя шага collection. В пакете 35 SHA-256 control payload. [Замороженный запрос](/root/kani-ch8-kani5196-diag-recheck-control-20261126/ch8-kani5196-diag-control/CI-REQUEST.json) · [Workflow](/root/kani-ch8-kani5196-diag-recheck-control-20261126/.github/workflows/ch8-q-pilot.yml)

## Пин Kani

| Поле | Значение |
| --- | --- |
| Источник точного read-only fetch | `https://github.com/feliperodri/kani.git` |
| Commit | `1c6e63b1f786612b7302df6c94abe5248906de12` |
| Tree | `724e184dc3978a7c2f08059a556eb1a291ca3b7f` |
| Первый родитель | `cfcd2eb1d41f7209723b13ce02d512831405cc3b` |
| Второй родитель | `8c6dba5935e8b37a905145c57572d1b67489bae2` |
| Blob `rust-toolchain.toml` | `864a9691aa2c3f1a51f652bc52c388cdad51edb6` |
| Toolchain | `nightly-2026-11-23` |
| Компоненты | `llvm-tools`, `rustc-dev`, `rust-src`, `rustfmt` |
| Blob `Cargo.lock` | `24a5c536d891c35713cf90dffcffb5c6170d4363` |
| Gitlink `charon` | `e21fb23e3c936e3a8bcfc13c63d076bd539e4601` |
| Gitlink `firecracker` | `cd36c699f3cb3d531289aadee26c45c1306edcfc` |
| Gitlink `tests/perf/s2n-quic` | `d7b71409c3bba3e577f76c0dbc4a579ebf16f131` |
| Backend | CBMC, goto-cc и goto-instrument `6.11.0`, Kissat `4.0.1`, solver CaDiCaL |

Все 41 SHA-256 проверены по Git-объектам и повторно по файлам чистой копии. Для обоих путей `scripts/setup/ubuntu-24.04/*` проверена tracked symlink `ubuntu`, хэши взяты по целевым файлам. Аттестация передаёт один и тот же замороженный commit/tree на этапе сборки и при открывающей и закрывающей перепроверках. Matcher версий FIX2 используется без правок. Live-аттестация должна записать версии и хэши бинарников, фактический компилятор и оба sysroot. [Аттестация](/root/kani-ch8-kani5196-diag-recheck-control-20261126/ch8-kani5196-control/tool_attestation.py) · [Kani commit](https://github.com/feliperodri/kani/commit/1c6e63b1f786612b7302df6c94abe5248906de12)

## Roster, часы и наблюдения

| Пара | Fixture | Exact selector | Слоты в порядке запуска | Ожидания OFF / ON |
| --- | --- | --- | --- | --- |
| ITER | `iter.rs` | `iter_by_value` | `ITER-OFF`, `ITER-ON` | `SUCCESS` / `MEASURE` |
| ITER-INIT | `iter.rs` | `iter_initialized` | `ITER-INIT-OFF`, `ITER-INIT-ON` | `SUCCESS` / `SUCCESS` |
| SELECT | `select.rs` | `select_pointer` | `SELECT-OFF`, `SELECT-ON` | `SUCCESS` / `MEASURE` |
| SELECT-INIT | `select.rs` | `select_initialized` | `SELECT-INIT-OFF`, `SELECT-INIT-ON` | `SUCCESS` / `SUCCESS` |

Каждая из восьми записей совпадает с соответствующей записью FIX2. В каждой паре ON добавляет только `-Z uninit-checks`. Сохранены `--exact --jobs=1`, regular и stock export, `--keep-temps`, unwind 16, object bits 12, harness timeout 60 с, child watchdog 90 с и штатные safety/unwind checks. Fixtures запускаются standalone со stock sysroot. CAL и SLICE исключены из roster. CAL не запускались, поэтому `calibration.state=INCOMPLETE` и `canaries={}`. Оба файла `nested-unions` совпадают с прежними fixture hashes. Проверка их содержимого и координат чтения при setup сохранена.

`ubuntu-24.04`, 75 мин (4 500 с). Setup занимает до 1 800 с, включая лимит сборки 900 с. Финализация и upload резервируют 540 с. Слот корня `90+3+6+15+8=122` с, восемь слотов занимают 976 с. После резерва 30 с на запуск остаётся `4500−1800−976−540−30=1154` с. Лимиты RSS составляют 8 GiB для child и 12 GiB для outer с резервом памяти 2 GiB. Пределы проекции и артефакта составляют 4 MiB на корень и 72 MiB суммарно.

`finish` строит `pairs/ITER.json`, `pairs/ITER-INIT.json`, `pairs/SELECT.json` и `pairs/SELECT-INIT.json` по ID пары и режиму. Индекс хранит запрошенный и фактический argv, нативный исход и exit, фазы, cutoff и reap. Regular и stock сохраняют нативные записи со статусами, ID, описаниями и координатами, доступными в каждом формате. Для нового пина `assert!` выделяется среди свойств класса `panic` по `assertion failed: ` и прежней координате. Остальные panic-свойства остаются в нативном инвентаре. Binder и правила захвата не менялись. Публикация остаётся в `ch8-kani5196-diag-<run_id>-<attempt>`, путь `${RECEIPT_ROOT}/artifact/`, retention 7 дней, доступ ждёт подтверждения перед GO.

## Ручная проверка после отдельного GO и run

- ITER. Привязать чтения из `iter.rs:11` и `:13` через by-value iterator к typed `ptr::read::<usize>` в аттестованном sysroot. В `iter.rs:15` проверяется исчерпание итератора. Для ITER-INIT подтвердить оба прямых `assume_init_read` из инициализированных слотов на `:23` и `:25`. Старый binder может пропустить вызовы с параметром типа на receiver `MaybeUninit<usize>`.
- SELECT. Привязать `select.rs:31` к конкретному вызову `select_unpredictable` и преобразованию `MaybeUninit<*const u64>` в `*const u64` внутри callee. SELECT-INIT выполняет контрольное преобразование на `:40`. Чтение `*selected` имеет отдельную координату `select.rs:22` внутри `observe`, вызываемой на `:32` и `:41`. Старый matcher `select_call` мог выбирать несколько достижимых кандидатов.
- Использовать фактические координаты нового sysroot и непротиворечивый путь от выбранного root. При `INCOMPLETE` сверить regular, stock, checks и доступные rooted edges вручную. `trace_available` без шагов фиксирует только доступность trace. Live unsupported guard, несовместимый layout, недостижимость и cutoff учитываются отдельно.
- Для каждой пары отдельно выставить офлайн `REPRODUCED`, `NOT_REPRODUCED` или `INCONCLUSIVE`. Воспроизведение требует привязанного отчёта на инициализированной операции и сверки OFF и INIT. Для исчезновения нужны завершённый ON и подтверждение выполнения целевой операции. При воспроизведении черновик готовит планер, при исчезновении координатор вносит результат в TODO. Публикация за координатором.

Live-версии, sysroot, точные native IDs и rooted GOTO нового пина ждут разрешённого run. Результат сравнения пока открыт. [ITER fixture](/root/kani-ch8-kani5196-diag-recheck-control-20261126/ch8-kani5196-diag-control/fixtures/iter.rs) · [SELECT fixture](/root/kani-ch8-kani5196-diag-recheck-control-20261126/ch8-kani5196-diag-control/fixtures/select.rs)

## Локальная валидация

| Проверка | Результат |
| --- | --- |
| Чистый shallow checkout review-trigger, глубина 3 | `diagnostic.py validate` прошёл. Проверены event, ref, attempt, trigger SHA, sole parent, список изменённых путей, 35 хэшей payload и пять fixtures. Неверные event, ref, attempt и SHA отклонены. |
| Чистая отдельная копия tool | `diagnostic.py check-source` прошёл. Независимо перепроверены commit, tree, родители, toolchain, Cargo.lock, gitlinks и все 41 SHA-256. |
| Исходные координаты | Проверены fixture-селекторы, operation anchors, assertions и covers, включая SELECT `:22`. Все шаблоны tool-side anchors binder нашли совпадения в закреплённом tool repo. |
| Синтетические тесты из shallow checkout | 26 прошли. Восемь синтетических запусков, нативный exit 1 для измеряемого ITER-ON, regular и stock после timeout и подтверждённого reap, восемь `NOT_RUN` после раннего отказа setup, четыре pair manifests с ITER при переставленных строках, границы допуска и лимиты артефакта. |
| Унаследованные тесты | 28 прошли для `ch8-kani5196-control`, включая отрицательные тесты версий FIX2, проверку drift и неверных commit/tree. 14 прошли для `ch8-q-pilot-control`. |
| Статика | YAML с одним job и изменения только в названии roster step, `bash -n` для семи run-блоков, AST Python, `git diff --check` для control и trigger прошли. |

Локально использованы Git, статика и синтетические Python-процессы. CI и верификаторы не запускались. Review-trigger предназначен для ревью. Независимое ревью и разрешение на запуск остаются отдельными этапами.

## SHA-256 fixtures

| Файл | SHA-256 |
| --- | --- |
| `iter.rs` | `6a36f2a4cc988ff3e09e3f5d67a9bbe91b112f9246ca314eba2f3a205050a61d` |
| `main.rs` | `3e71829b6ee39601ad29546aefb71ae861505bd9b4b555c36ea9d595468d63bb` |
| `nested-unions.expected` | `7c4b4bd80f002d4dc0c8c0180f8c01dbfcee18da9dc1a6ac967cac24282d5bcd` |
| `select.rs` | `75b3bdb7dd1287891db2ae8c78e559b41ab397d216a6151484829dc6b0c73d1b` |
| `slice.rs` | `973d57a7c28952bb6a833e2cdea77f62641e37722837d033c1077433b143b226` |

## SHA-256 tool inventory

| Файл | SHA-256 |
| --- | --- |
| `.cargo/config.toml` | `8a7317c9b5e38ee2e842086a154e99f9bae4e2bc1118cae9e5b7cd5ee7c3547c` |
| `.github/actions/setup/action.yml` | `6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307` |
| `.gitmodules` | `bed047cc36087a49620c1d0035dc09895b33c66b8364c561e349cc5e090c8863` |
| `Cargo.lock` | `a0927ce8f4ecfe2fc827ad1817e98314783142264409999d102984d6cd00ed21` |
| `Cargo.toml` | `2241ce462f11b55683959b4d57020f23d81e0bc360ec3cb4a375165353c33bea` |
| `kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs` | `f45442c85b163384a9688e8a24c1e1c12d1f09b4a07a7bb4839f69b8f31d80b6` |
| `kani-compiler/src/codegen_cprover_gotoc/codegen/foreign_function.rs` | `735ef91ce34fef900d184ea171580f02b236ac6a7287cd07a4a6dd7b94ce6c95` |
| `kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs` | `d0eea04db226b5a196164159b7c3df446724ca0abce54b3c1b35716c66d5b774` |
| `kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs` | `d91ce4f689ea9a74cb7b403adfe7f0dcefe8f0f4ad9b4386e400aacc3763b61c` |
| `kani-compiler/src/intrinsics.rs` | `732170d21942005d891f79c7901ef71e1c49dda4040129bad1aca8fdccf38462` |
| `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` | `f1f318f621f717a95427f67a1b38655059ca3d3f008ecddb1c1f1c66f803f40c` |
| `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` | `a738301f4277b3bfd96a70c2a1485be3f520736a2388643f526e5f42bdbc265d` |
| `kani-compiler/src/kani_middle/transform/check_values.rs` | `9cb8f95b3c4de8c08c33e388cdd2e7e5439732e8c6b501b2c5353a1d0fb3dc79` |
| `kani-compiler/src/kani_middle/transform/contracts.rs` | `94b7b6d80bcefa9215f0e0107a49f500289e66de790de5a46197efb83de1ac14` |
| `kani-dependencies` | `6d6a66509732d5f1d859021a95524bd1e6e804edf037e9af9a096d7b5a4eed37` |
| `kani-driver/src/call_cargo.rs` | `e4e359177ebaac7d2fadee5b36e63ee6d0d7193e3e2571378bf7cd0032751e06` |
| `kani-driver/src/call_cbmc.rs` | `d41f5e0f7d32c5c3cdeb98203b98cfe237e8b1ed915f5c859badbdb54e851de3` |
| `kani-driver/src/call_goto_cc.rs` | `15cd54e4c07a0f196801a408dbd6e39acf4cc8d6e43314e12810691a07b890d0` |
| `kani-driver/src/call_goto_instrument.rs` | `981387b38ad3455a440aecb606266f546423084b69ece1ab47711e05e3cd68c2` |
| `kani-driver/src/call_single_file.rs` | `5e918902c7f015d62d6e0527cb0d22df220146f28b0f067199a0c1a6b460a9fb` |
| `kani-driver/src/cbmc_output_parser.rs` | `efdc704e083c0a9b357e6258ef6312669091dca4fbbe102852c94c5e1fd7bfc1` |
| `kani-driver/src/cbmc_property_renderer.rs` | `f2f6be1b2a2e29e340e17c5859fa5a0f5c7d90bacb9287d082af23d442737c42` |
| `kani-driver/src/frontend/schema_utils.rs` | `a1cb929a3fd070a8180fbada431e8d64f00d565686b77efacb62de1f80560604` |
| `kani-driver/src/project.rs` | `d420d0163e49f9acc2ce49674ad5deaf6a423537eecaa14497d735a6ee0d3878` |
| `kani-driver/src/session.rs` | `8957dedfdb0658ee69fa2398f8de17cc9f132910423136093c8ff65fa3f47b26` |
| `library/kani/kani_lib.c` | `248084132118b427e510b019db271c869bd9deaf1ff0c85730eefce7e8896a94` |
| `library/kani/src/lib.rs` | `ad28e7d4abfe51dcc51d73ea91774aa773edd8cb5046fe46c3807e865c741586` |
| `library/kani_core/src/lib.rs` | `edf5ba0454a483467851df2449d978c26c8db79ef5f9d90116f209b433a342c6` |
| `library/kani_core/src/mem.rs` | `598428730a32f2c4034091688b50dde5a44deb69e2e3c61e08a0d394a5e42844` |
| `library/kani_macros/src/sysroot/contracts/helpers.rs` | `710d7ef9ca4ca6e2fc277a56d3f1f1b1008ae7162eaf7d8f3fc0c1826810fd30` |
| `rust-toolchain.toml` | `5eef55b5e6e89d717b045d7a9a89e4639ec94a8f172603cbe1a6d387000fd0cc` |
| `scripts/kani` | `28a81c48fd72627ed2449993730636bc830abeffeaea4d85d9297b2ec4393af2` |
| `scripts/setup/install_kissat.sh` | `27fb589377f37077742f2d1f518f9275baef365d7d461c540fad48455fce8b32` |
| `scripts/setup/install_rustup.sh` | `ce02a8a4042b4f6d2b8ffc0905f50284e77d7772b2ed3a2760cdb17db728adb5` |
| `scripts/setup/ubuntu-24.04/install_cbmc.sh` | `378294d7c13cc0d3c90403cf31a5c577d5292d2f5aee3274977a4446060eda54` |
| `scripts/setup/ubuntu-24.04/install_deps.sh` | `820a436228d735c1231d09a791de1cb56958d9be42778bb422735183c749bc50` |
| `scripts/setup/ubuntu/install_cbmc.sh` | `378294d7c13cc0d3c90403cf31a5c577d5292d2f5aee3274977a4446060eda54` |
| `scripts/setup/ubuntu/install_deps.sh` | `820a436228d735c1231d09a791de1cb56958d9be42778bb422735183c749bc50` |
| `tests/expected/uninit/nested-unions/expected` | `7c4b4bd80f002d4dc0c8c0180f8c01dbfcee18da9dc1a6ac967cac24282d5bcd` |
| `tests/expected/uninit/nested-unions/main.rs` | `3e71829b6ee39601ad29546aefb71ae861505bd9b4b555c36ea9d595468d63bb` |
| `tools/build-kani/src/sysroot.rs` | `b1d7631408629db2d6230c2d8081ed2f8e3524369ea114a9ff3f0d2819c1be8a` |
