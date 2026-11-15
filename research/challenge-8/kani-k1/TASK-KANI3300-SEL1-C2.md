# SEL1 поверх итогового C2 — порт, Quick, Gate A и SmallSort replay

2026-11-15. Worker14 + worker15, последовательные стадии, одна стадия на сессию.
Это верификация корректности, не security-работа.

Владелец разрешил порт и последующую проверку через **fork CI**. Cloud $0.
Локальные cargo/rustc/Kani/CBMC/Miri и сборки запрещены. Разрешены Git, чтение исходников,
Python/shell synthetic tests обвязки без toolchain/verifier. Push и dispatch выполняет только координатор;
без upstream PR/issue, новых fork refs от исполнителей и публикаций. PR-текст SEL1 — отдельная будущая стадия.
Этот файл — задание, а не свидетельство выполненных проверок: новые Quick/Gate A/replay пока NOT_RUN.

## 1. Зафиксированные входы

- Итоговый C2: **`8e299aa6243bc5f06a29c51e98aafa9564478220`**,
  tree **`9829702c1aa0ecb73c860fc0ad5451757917d6cb`**. Это дерево freeze `ad499e41dd`, но портировать
  нужно именно поверх `8e299aa624`, завершающего нарезанный стек. Не rebase на новый upstream и не менять C2 refs.
- Старый SEL1: **`39a6521bf1b042358801cf613fd340623f35f851`** от C2-S1
  `69b13711e60a87458200833445d47488ab466344`. Production — `ec85b782a1b7156ad434cfac25403acd4e326dc1`;
  `39a6521bf1` исправляет только tests/goldens. Брать **net delta `69b13711e..39a6521bf1`**, не старую историю C2.
- Старые результаты: select controls **29/0**, run **43613912120** на `39a6521bf1`;
  шестистрочный SmallSort replay **43611601987** на **`ec85b782a1`**, не на `39a6521bf1`.
- C2 Gate A: **43665002636**, все 33 стадии на `ubuntu-24.04`, `ubuntu-24.04-arm`, `macos-15`;
  C2 Gate B′: **43683557088**, две merge SUCCESS, sort4 — ровно граница `select_unpredictable`.
  Это ориентиры; они не заменяют gates нового дерева SEL1-C2.
- Read-only Kani sources: `/root/kani-fix-3300-c2-s6` (нужный объект `8e299aa624` уже есть),
  `/root/kani-fix-3300-sel1` (старый SEL1). HEAD checkout не подменяет exact input SHA.
- В g0 сначала читать `TASK-KANI3300-SEL1.md`, `kani3300/sel1/{RESULT.md,TRANSFER-MAP.md,CONTROL-MANIFEST.md,STD-OVERLAY.json}`,
  `kani3300/sel1/followup-43611512375/RESULT.md`, `kani3300/sel1/replay-43611601987/RESULT.md`,
  `kani3300/c2-gatea/ACCEPTANCE.md`, `kani3300/c2-gateb/RESULT.md`, `kani3300/c2-slices/slice-07/ci-43723531871/ACCEPTANCE.md`.

Новые рабочие области — worktrees существующих клонов, без копий target/sysroot и полных новых клонов:
worker14 `/root/kani-fix-3300-sel1-c2-w14`, локальная ветка `work/kani3300-sel1-c2-w14` от exact C2;
worker15 `/root/kani-fix-3300-sel1-c2-w15`, отдельная локальная CI-ветка после freeze source.
Занятый/dirty путь, неправильный parent/tree → STOP без reset/stash/clean и движения чужих refs.
Research: `kani3300/sel1-c2/` в g0; worker14 владеет `port/`, worker15 — `review/`, `quick/`, `gatea/`, `replay/`.

## 2. Стадия P — worker14: один отдельный SEL1-коммит

Перенести SEL1 на exact C2 с сохранением окончательных исправлений C2: immutable/F5, F6 reset,
парности аргумент/возврат, hook boundaries, closure layout, S3/CC и **F7 изоляции изменённых тел**.
Не заменять целые C2-файлы старыми из C2-S1. Итог — один SEL1-коммит с parent `8e299aa624`; C2 история неизменна.

Production scope старой delta — пять файлов:

1. `kani-compiler/src/kani_middle/mod.rs`;
2. `kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs`;
3. `kani-compiler/src/kani_middle/reachability.rs`;
4. `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs`;
5. `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs`.

Перенести 12 групп `tests/expected/uninit/select-unpredictable-*`, включая исправленные goldens `39a6521bf1`.
Worker14 также делает узкую правку текущего `docs/src/rust-feature-support.md`: blanket отказ для
`select_unpredictable` теперь заменяется точной новой границей. Остальные ограничения C2 сохраняются;
не заявлять поддержку всех intrinsic/T/N, всего SmallSort или исправление #5104.
Другой production/runtime/DFCC diff либо новая модель intrinsic — STOP с объяснением, не расширение порта.

Обязательные инварианты порта (сверить с TRANSFER-MAP и новым C2 кодом):

- Единый fallback predicate для codegen/reachability; select classifier проверяет именно core intrinsic,
  usable fallback body, сигнатуру `(bool,T,T)->T`, размер и поддерживаемую layout/mask до изменения shadow.
- Points-to следует реальному fallback и объединяет **referents обоих value arms**; bool не становится target,
  адреса caller-слотов не заменяют referents, выбор указателя не означает чтение/инициализацию pointee.
- Shadow передаётся для argument slots **2 и 3**, bool исключён; обе arm-маски снимаются до deinit любого Move.
  Copy не убивается; argument/return pairing использует ту же реальную instance signature.
- Обычный fallback/body владеет переносом выбранной маски, включая false и padding по C2 typed mask;
  обязательный return slot0 Store и caller Load только на normal edge. Не добавлять второй backend copy/bless.
- Исключение для Intrinsic в transfer допускает только валидированный select; прочие unsupported intrinsics,
  bodyless/shim/foreign/hook boundaries не ослаблять. Сохранить B1 traversal/flush.
- Все изменения DelayedUbPass через актуальный F7 journal/`replace_delayed_body`; без прямых правок общего cache.

Статически выписать типы операндов, числовых сравнений и conversions на конфликтных хунках; без локального компилятора
не писать «компилируется». Worker15 независимо просматривает только delta и стыки C2, пишет компактный REVIEW;
исправления source/tests/docs вносит только worker14.
Артефакты: INPUTS, PORT-MAP (старый→новый хунк), TRANSFER-MAP, CONTROL-MAP, static REVIEW, SHA/tree/parent/diffstat.
Все 29 selectors старого набора сохранить: 12 intended SUCCESS + 17 intended FAILURE/Unsupported, с точной причиной.
`nested-unsupported` с UnionAsField при создании Nested не выдавать за достигнутый select-specific guard.
Отсутствующий/overridden fallback и unsized T без runtime-контроля честно отметить как static-only review.

## 3. Стадия Q — worker15: Quick-пакет; запуск координатором

После принятия порта зафиксировать candidate SHA/tree. Взять последний рабочий uninit Quick из slice-07,
пересоздать source binding/хеши для candidate, отдельный CI-only overlay; не править export для запуска тестов.
Стандартные workflows удалить только в CI-only коммите; оставить один manual fork-only workflow.
Рабочие artifacts/observer находятся вне source checkout. Только координатор push/dispatch, одна попытка,
без автоматического retry и без изменения тестов/ожиданий ради зелёного результата.

Приёмка Quick: fmt/build/clippy/LLBC build; прежние C2 units и suites (kani Uninit, expected Uninit/delayed-UB,
ui, script/reinstrumentation, json-handler, std-checks) плюс **все 29 select controls**, ноль неожиданных failures.
Сохранить также S5 mutations 4/4 DETECTED и F7 structural isolation: 18 mixed-vs-own-isolated comparisons,
как в принятом slice-07 Quick. Ожидаемые verifier exit1 его negative/cycle roots не путать с ошибкой suite.
Ни C2 negatives, ни mode/Replace/Recursive/hook/mixed-root границы не исчезают; старых JSON DRIFT-исключений уже нет.
Сохранить полный список selectors и intended outcomes, полезные SUCCESS/точные негативные отказы и reachability;
29/0 — результат compiletest, а не 29 доказанных legal harnesses. Новые ignores/фильтры требуют STOP/review.
Caps — рабочий ограниченный Quick-профиль slice-07 без повышения, записать фактические пределы в CI-REQUEST.
Ненулевой exit/timeout/OOM/setup loss не становится PASS по совпадению одной подстроки.

После принятия Quick — **freeze точного SEL1 source SHA/tree**. Любая последующая правка source/tests/docs
создаёт новую голову и требует повторной проверки затронутых стадий; final gates относятся к одной голове.

## 4. Стадия A — worker15: новый Gate A; worker14 review, координатор запускает

Адаптировать **принятый** `kani3300/c2-gatea/` пакет и working overlay `39bcdd7ad51dc169f75a9974e43717205553bad0`,
а не первоначальную неисправленную заготовку. Сохранить sibling checkouts control/export (без вложения Cargo workspace)
и Bash 3.2 owner guard observer на macOS. Нужен новый binding на SEL1 freeze, не старый C2 receipt.

- Exact source из freeze; его собственный setup/dependency/toolchain pins, без upgrades или патченного CBMC.
- Matrix ровно `ubuntu-24.04`, `ubuntu-24.04-arm`, `macos-15`, fail-fast false, max-parallel3, одна попытка.
- Полный неизменный `bash scripts/kani-regression.sh`, **33/33 стадии** на каждой платформе; никаких фильтров,
  новых ignores, global object-bits12/arrays-uf/check disables. Штатные per-fixture12 flags остаются.
- Caps как в принятом Gate A: job360 min, regression≤20400s с резервом10 min, compiletest2400s/test;
  stdout/events≤256MiB, metadata≤16MiB, artifacts≤384MiB/платформа, retention14d. Без RSS-watchdog для полного gate.
- Process-group timeout, original exit/signal, artifacts `always()`, полный observer/receipt и clean source до/после;
  отдельный aggregate отмечает missing/failed rows. Не маскировать потерю runner или truncation зелёным summary.

Приёмка: все три полных receipts, 33 стадии, exit0, без новых failures/ignores/потерянных suites;
разницу счётчиков против C2 объяснить добавленными SEL1 tests, не требовать старых totals.
Подготовка пакета не означает Gate A PASS; UNKNOWN/неполные события требуют явного review координатора.

## 5. Стадия B — worker15: шесть уникальных SmallSort строк на той же freeze

После принятия нового Gate A выполнить bounded replay. Std exact **`70ba5befc617627073738e26cb1466bd4fb76e41`**,
SEL1 test-only пакет **`6075e7ce17179f45642c9ffe8fe09e3ec9395726`** из STD-OVERLAY.json.
Не менять std production bytes, preconditions, comparator или oracle. Совместить рабочую C2 Gate B′ обвязку
с шестистрочным SEL1 пакетом; обновить source tree/file/subtree hashes, request и все вложенные checksum bindings.
Одна замена tool SHA недостаточна. Старые `504 files/6 subtrees` — образец binding coverage, не готовый новый manifest.

Профиль: ubuntu-24.04; uninit ON; object-bits12; valid-value OFF; controls cfg ON;
штатный solver/slicing/checks и organizer flags, включая `--no-assert-contracts` где в исходном рецепте.
Шесть jobs последовательно, jobs1/max-parallel1; cap2400s/root, job60min, без retry; общий envelope≤360 runner-min.
Все selectors ниже имеют префикс `slice::sort::shared::smallsort::verify::`; выбирать exact root, не подстроку.

| Row / selector suffix | Геометрия; unwind | Ожидание на SEL1-C2 |
|---|---|---|
| `merge-raw-closure-on` / `helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0` | u64 len8, flat MU scratch48, src[32..40], dst[0..8]; 34 | SUCCESS, 0 failures, covers5/5 |
| `merge-profile-closure-on` / `replay_gateb_prime::merge_profile_closure_scratch48_u8_n9` | u8 N9, scratch48, обе подложки; 34 | SUCCESS, 0 failures, covers2/2, ensures достигнуты |
| `sort4-closure-on` / `helper_contracts::sort4_safety_u64` | PFC sort4, src4/dst4; 16 | SUCCESS, 0 failures, covers3/3 включая return; прежнего select Unsupported нет |
| `swap-if-less-closure-on` / `helper_contracts::swap_safety_u64_backing4` | PFC swap, backing4, a==b и оба порядка; 8 | SUCCESS, 0 failures, covers6/6, frame/readback сохранены |
| `raw-legal-on` / `replay_uninit_controls::sort4_raw_all_initialized_u64` | ordinary sort4, src4/dst4; 16 | SUCCESS, 0 failures, covers2/2; положительная пара следующей строке |
| `raw-negative-on` / `replay_uninit_controls::sort4_raw_hole_negative_u64` | та же геометрия, только source[1] не записан; 16 | Ровно один задуманный uninit-read source[1], никаких иных failures |

Gate B′ уже содержит sort4: не запускать его второй раз под другим именем. Raw-legal сохранён как существующий
парный контроль raw-negative. Для PFC comparator оставить реальные closures, без coercion в fn-pointer;
profile row — конкретный companion, не доказательство generic `merge_profile<P>`.
Негатив привязать по исходной операции/описанию/корню: старый `sort4_stable::<u64,…read_less_u64>.safety_check.1`,
«Reading from an uninitialized pointer of type `*const u64`», smallsort.rs:751:26. Не подменять его requires,
layout, frame, comparator или select Unsupported; source drift/location/name drift только после review binding.
Полный список failed properties и полезные SUCCESS/covers обязателен; unreachable return запрещает legal PASS.

Сравнить с C2 B′: merge остаются SUCCESS, sort4 переходит от единственной select-границы к SUCCESS с return cover.
Сравнить с SEL1 43611601987: sort4 0/753, swap0/585, raw0/382, merge0/572 и0/1030 — старые ориентиры,
не фиксированные новые totals. Объяснить добавленные/удалённые checks и unreachable, исключить потерю safety obligations.
Записать actual argv, selected PFC bodies, source/std/overlay identities, runtime/binary/solver hashes,
original exit/signal и caps. Intended negative verifier exit1 отдельно от сбоя обвязки. UNKNOWN не автоматический PASS.

## 6. Итоговые deliverables и STOP

Worker14: один source commit и `port/` карта/статический разбор. Worker15: review, manifests/CI-REQUEST/overlay patches
и receipt templates для Q/A/B; после каждого координаторского запуска — curated RESULT со ссылкой на run.
В g0 писать только свои research-подкаталоги; source и CI-only коммиты разделены, автор Tiramisu-Cake
<igkharin@gmail.com> через per-command `-c`; research/CI commits с `[skip ci]`, без Co-Authored-By, без push.
При подготовке можно параллельно делать review и шаблоны A/B, но binding финализировать после freeze;
порядок приёмки **P → Q → freeze → A → B → итоговый handoff**. Достаточно двух воркеров, третий не нужен.

STOP: конфликт за рамками SEL1, необходимость менять runtime/DFCC/F7 смысл, lost C2 oracle/check,
необъяснённый новый отказ/ignore, source drift, неверный binding, неполный receipt или превышение caps.
Не запускать дополнительные варианты/перезапуски самостоятельно и не чинить #5104 внутри этого порта.
Принимаются только эта отдельная source delta + Quick + новый Gate A трёх платформ + все шесть replay строк
на одной голове. Это bounded helper evidence; ни всё SmallSort, ни все T/N, ни #5104 этим не закрываются.
Каждая сессия завершается `READY <source-or-CI-overlay sha>` и путём к её research handoff; blocker — явно STOP.
