# CH8 W0-A1 — actual scratch routes, scale и точные issue controls

2026-11-16. Worker15, одна сессия подготовки; после reviewable package STOP до запуска координатором.
Это верификация корректности, не security-работа.

Владелец подтвердил решения `PLAN-CH8-ITEM1-REMAINING-v2.md` @ `dea4b12168`, затем P0 пункта2
и поправки §7 `ROADMAP-CH8-ITEMS1-2-FOUR-WORKERS.md`. Это единая обновлённая редакция W0-A1,
не дополнительная стадия/квота. Четыре роли:11 модели S,13 core-интегратор,14 U/CI inventory,15 A1→merge→E.
**WIP: никакого нового compiler/runtime-кода, моделей, summaries, contracts или алгоритмических изменений.**
Разрешены test-only fixtures, CI-only обвязка и research. Локальные cargo/rustc/Kani/CBMC/Miri/builds запрещены.
Fork CI, Cloud $0. Push, non-skip trigger, remote branches и все запуски — координатор; публикаций нет.
В этой сессии не запускаешь CI: готовишь проверяемый пакет и CI-REQUEST, затем `READY`.

## 1. Вход, identities и read-only источники

- Candidate: SEL1 freeze **`14bc57fdb99960240c4944845a3d985c8af4dcf7`**,
  tree **`1efb6e4dfa69d346df8e23741d11839b1932403d`**.
- Baseline: общий upstream parent стека **`0aac16ef62da9e9d5645782d458593e5d78143ba`**,
  tree **`9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`**. Это frozen upstream reference, не текущая ветка `main`.
- C2 **`8e299aa6243bc5f06a29c51e98aafa9564478220`**, tree `9829702c1aa0ecb73c860fc0ad5451757917d6cb`:
  static attribution reference. Обязательный runtime issue comparison — baseline и SEL1; не делать трёхпиновую матрицу автоматически.
- Std frozen target **`70ba5befc617627073738e26cb1466bd4fb76e41`** + принятый SEL1 test-only package
  **`6075e7ce17179f45642c9ffe8fe09e3ec9395726`**. Новый A1 overlay строится поверх6075,
  сохраняя production std bytes и старые test fixtures. Текущий g0 HEAD не подменяет этот std target.
- Принятый recipe: `kani3300/sel1-c2/replay/`, особенно `HANDOFF.md`, `CI-REQUEST.{md,json}`,
  `CI-OVERLAY.json`, `full-export/`, `run-43751703000/RESULT.md`.
  Package `fff42ed46992c7d00463a21561093cfde5dce330`, accepted trigger
  `1ce0b1e5b62660bdc5809318689eeea287af064c`; Quick43740679160/Gate A43744142824 уже приняты.
- Дополнительно: v2 §§3/5/13/14, `TASK-KANI3300-SEL1-C2.md`, `kani3300/sel1/STD-OVERLAY.json`,
  `kani3300/final-gate/REPLAY-ROOT-MAP.md`, `kani3300/c2-slices/slice-03/` и `/slice-04/` по нужным controls.

Сначала root/project AGENTS. Read-only Kani repo `/root/kani-fix-3300-c2-s6`, recipe worktree
`/root/kani-fix-3300-sel1-c2-w15`, std package repo `/root/verify-rust-std-kani3300-sel1-swap`.
Не checkout/reset/clean/stash чужие области. Новые области — только worktrees, без полных clones/копий target:
Kani `/root/kani-fix-ch8-w0-a1-w15` от candidate; std `/root/verify-rust-std-ch8-w0-a1-w15` от6075.
Занятый/dirty путь или неверный SHA/tree — STOP без перезаписи. Git object transfer из локального repo допустим.
Создавать отдельную локальную std-ветку `work/ch8-w0-a1-w15` от exact6075; это safety campaign A,
не sorting-ветка S от#752. Единственное registration exception worker15 — `verify.rs` в этой A1-ветке
и новый `verify/wave0_a1.rs`; не переносить регистрацию в S и не править `smallsort.rs`.
Любые будущие core/helper/loop attrs передаются единственному интегратору worker13 отдельным заданием.

Чистый upstream0aac одновременно выбран tool pin для S, но совпадение tool source не переносит verdict
между разными std sources, flags, comparator и свойствами. Новый KeyLess из S в A1 не подставлять:
остаётся прежняя actual-body closure; её отдельная ON квалификация не подразумевается S1 smoke.

Research write scope: **`research/challenge-8/kani-k1/kani3300/w0-a1/`** в g0.
Worker14 владеет W0-U/pr-texts; туда не писать. Исторические receipts и задачи не менять.

## 2. Std test-only overlay: реальные targets, восемь ON строк

Добавить `verify/wave0_a1.rs` и его opt-in регистрацию в `verify.rs` под уже известным
`cfg(kani_smallsort_controls)`. Больше production/core файлов не менять. Не включать новые roots в ordinary CI.
Структура функций должна быть короткой и проверяемой; предпочесть отдельный exact selector каждой строке,
не nondet выбор маршрута внутри одного root. Префикс selectors:
`slice::sort::shared::smallsort::verify::wave0_a1::`.

| Suffix selector | Вызов actual body / input | Реальная scratch и ветвь |
|---|---|---|
| `stable_freeze_u64_n8` | `<u64 as StableSmallSortTypeImpl>::small_sort`, N8 | Отдельные flat `[MaybeUninit<u64>;48]`, sort4→insert→merge |
| `stable_freeze_u64_n16` | тот же target, N16 | flat48, sort8→insert→merge |
| `stable_freeze_u64_n32` | тот же target, N32 | flat48; кандидат масштаба |
| `unstable_general_nocopy_u64_n8` | `<A1FreezeNonCopy as UnstableSmallSortTypeImpl>::small_sort`, N8 | Реальный default Freeze !Copy general, private `MU<[T;48]>` |
| `unstable_general_nocopy_u64_n16` | тот же target, N16 | private48; sort8→insert→merge |
| `unstable_general_nocopy_u64_n32` | тот же target, N32 | private48; кандидат масштаба |
| `unstable_network_u64_n18` | `<u64 as UnstableSmallSortTypeImpl>::small_sort`, N18 | Реальный Freeze+Copy network, `MU<[u64;32]>`, merge branch |
| `unstable_network_u64_n32` | тот же target, N32 | network32; кандидат масштаба |

`A1FreezeNonCopy` — verification-only transparent wrapper одного u64, **без Copy и Drop**;
computable field layout, размер8, Freeze. U64 на unstable trait выбирает network, поэтому его нельзя подписывать general.
Все input элементы — независимые произвольные initialized u64, не fixed witnesses.
Для wrapper использовать прямое создание полностью initialized элементов (например literal macro),
не создавать случайно новый unsupported path через `array::map`/IntoIter/вложенный MU-of-flat.
Если предпочитаешь иной constructor — сначала явно проверить его source path; constructor refusal отдельно от target refusal.

Comparator — конкретная **closure без coercion в fn pointer**, которая читает оба фактических аргумента
(у wrapper — u64 payload) и возвращает arbitrary bool. Не ограничивать ответы lawful order ради уменьшения модели.
Не использовать P::CMP, profile copies, PFC или `stub_verified`: это actual-body scale probe.
Все сортирующие callees реальны. Сохранить только уже применявшийся в соответствующих safety fixtures
explicit `panic_on_ord_violation` stub, если он нужен для normal-return scope; записать exact replacement и source.
Никаких новых assume(false), panic/body stubs или preconditions для прохождения A1. ON/OFF имеют одинаковый panic scope.

После вызова: reached-return cover, volatile reads **всех active output payloads** и frame/readbacks по доступной геометрии.
Не читать unused MU scratch/tail как initialized T. Sortedness от arbitrary bool не требовать.
Показать по исходникам/доступной metadata выбранные impl/body/type predicates, actual callbacks и raw scratch views.
Не заключать «ветвь достигнута» только из имени root; inlining/unknown binding отметить явно.
Статически выписать types/lengths/offset arithmetic новых Rust fixtures; локального подтверждения компиляции нет.

## 3. R1: bounded scale probe на SEL1, без переписывания модели

Первый future dispatch: восемь строк ON из §2, самые дорогие N32 — в начале очереди.
Три N32 нужны, чтобы не объявлять один маршрут «самым тяжёлым» без сравнения flat/general/network.
Это восемь ON safety cases пункта1 и три его N32 samples, **не** три функциональных R6/S2 probes пункта2:
arbitrary-bool normal-return cost не измеряет lawful sortedness/multiset consumer.
Записать max complete elapsed/RSS и censored timeout/OOM отдельно; после cap нельзя ранжировать неизвестные времена как измеренные.
«Как есть» означает реальные тела без composition/новых stubs или ослабления checks ради масштабирования.

Профиль как в accepted replay: `ubuntu-24.04`, jobs1/max-parallel1, uninit ON, object-bits12,
valid-value OFF, controls cfg ON, default solver/slicing/checks, organizer flags включая `--no-assert-contracts`.
Существующий source unwind34 для этих finite domains — исходный ориентир; подтвердить достаточность
по actual loops и всем unwinding checks. Нельзя скрывать unwinding failure увеличением bound/отключением assertion без review.
**600s на verifier invocation после setup**, including driver/codegen/backend; embedded harness timeout не выше600.
Setup отдельно; job≤60min/строка с reserve≥10min на receipt/upload; общий R1 envelope≤480 runner-min.
Одна попытка, matrix fail-fast false. Это dispatch limit, не гарантированный расход или успешное завершение.

STOP R1 при cap/runner loss, unexpected failure/Unsupported, fixture-level refusal, недостигнутом return/readbacks,
wrong source/root/body, неполных events. Подготовленные независимые строки могут завершиться при fail-fast false;
**никакого нового варианта/перезапуска** вместо разбора первого blocker.
Малые helper SUCCESS предыдущего replay не заменяют это scale evidence.

## 4. R2: точные native issue reproducers на baseline и SEL1

Сохранить exact исходные файлы из официальных issues с URL, body hash, reported tested pin/command и diff любых адаптаций.
Сами fixtures находятся **в control package вне compiler export**; это не новые expected-тесты внутри frozen Kani.
Обе версии инструмента получают одинаковые fixture bytes, modes, flags и toolchain/dependency policy.
Каждый selector/file исполняется отдельно; parser не может сопоставить output соседнего root.

| Issue / обязательный случай | Baseline hypothesis, не результат | Candidate oracle / companion |
|---|---|---|
| [#5020](https://github.com/model-checking/kani/issues/5020): `repr(C) { a:u64, p:NonNull<u8> }`, allocation; записаны только первые8 bytes, затем whole typed read | Reported false SUCCESS из-за Pat-mask offset. На frozen baseline это ещё надо воспроизвести | Ровно intended uninitialized pointer-field read; same-type fully initialized legal companion SUCCESS. Raw `*const` sibling не заменяет NonNull repro; Box не заявлять покрытым |
| [#4854](https://github.com/model-checking/kani/issues/4854): `const MEMCPY_RET: MU<*const i32>` с `MU::new(null())`, `reassemble_ptr_fragments_in_static`, assume_init | Reported ICE в Unsupported/operand_ty path | Исходный **autoharness** path без ICE; SUCCESS либо precise Unsupported различать. Explicit-proof/observable-null-read companion отдельно, не подмена исходного автокорня |
| [#5151](https://github.com/model-checking/kani/issues/5151): `[MU<D>;2]`, `D(u8)` с **пустым Drop**, записан slot0, `drop_in_place` slot1 | Reported layout Unsupported; отдельный исторический crash не считать тем же результатом | Exact uninitialized-slot negative; legal companion сначала инициализирует и slot1. Если empty Drop ведёт к SUCCESS — зафиксировать missed check, не вставлять чтение поля в исходный destructor ради ожидаемого FAILURE |

Для #4854 сохранить исходный autoharness invocation, включая sanity mode, edition/cap-lints и исходный набор flags
в manifest; любые CLI normalization записать и обосновать. Proof-wrapper сам по себе не доказывает исправление autoharness path.
Его RUSTFLAGS scoped только этому native case, не setup/std или остальным fixtures.
Если original mode недоступен/ломается раньше selected function, outcome NOT_RUN/BLOCKED, companion остаётся отдельным случаем.
Для #5151 допускается отдельный диагностический Drop-reading-field sibling, но не вместо точного empty-Drop repro и не автоматически.

Полный минимальный пакет: три original cases + три явно названных companion cases, на двух pins.
Expected baseline outcomes из issue — **hypotheses**: если дефект уже не проявляется на0aac, назвать BASELINE_NOT_REPRODUCED,
не подобрать тихо более старый pin и не приписать отличие C2. Candidate unexpected SUCCESS для actual hole — STOP/MISSED_CHECK.
Для #4854 «no crash, still Unsupported» — улучшение диагностики, не support/легальный proof.
Все failed properties и useful statuses, phase/exit/signal и actual selected input нужны для каждого случая.

В R2 можно добавить **один OFF companion** самого тяжёлого/первого capped N32 из R1:
тот же std/fixture/root, только uninit flag удалён. Никаких иных изменений comparator, unwind, slicing, solver, geometry.
Это сравнение стоимости/фазы, не новый proof и не разрешение ковырять исходники при timeout.

## 5. Бюджет: максимум три A1 dispatch из прежних18, общий ceiling32

- **R1:** один dispatch std scale/landmarks, §3.
- **R2:** один dispatch original native cases/companions на двух pins + при необходимости один std OFF companion.
  Native cases последовательно, ≤600s/invocation; job≤90min/pin с setup/upload reserve, max-parallel1.
  OFF job≤60min. Конкретную job matrix и aggregate envelope записать до запуска, не после отказа.
- **R3 резерв:** только решение координатора после R1/R2: одна адресная **fixture/обвязка** поправка либо
  дополнительный C2 middle-pin comparison для атрибуции. Не использовать резерв на compiler patch, иной solver или новый sweep.

Это 2 обязательных и до1 резервного dispatch, **не число verifier invocations**. В READY-пакете runtime ещё NOT_RUN;
координатор списывает фактически начатые dispatch, включая infrastructure failure, в единый
`CH8-DISPATCH-LEDGER.md`: A1 cap3 внутри прежнего item1 cap18; item2 получил отдельные14, всего≤32.
Нет auto-rerun, увеличения caps, новых historical pins или расходования резерва по умолчанию.
Если A1 выдаёт named blocker, handoff в U/E/решение по Replace, а не новый compiler feature от worker15.
R1/R2 dispatch планирует координатор рядом с S1 smoke/S2 cost jobs; готовый A1 workflow не резервирует
все CI slots и не даёт приоритета над S. Общее расписание, а не worker, решает одновременность тяжёлых jobs.

## 6. CI-only overlay и обязательный control/export чек-лист

Переиспользовать **реально работавшую** SEL1-C2 replay обвязку, не первоначальные неисправленные templates.
Для native fixture command допускается узкий adapter к тому же process/receipt wrapper;
не строить новый runner framework. Изменённые error paths проверить synthetic subprocess fixtures без verifier.

1. Два sibling checkout: exact CI-control и readonly `export/` с literal source SHA из manifest; никакого Cargo workspace вокруг них.
   Std находится в отдельном RUNNER_TEMP root; actual cwd и `./library` согласованы; бинарник — absolute export/scripts/kani.
2. Для native cases — отдельный isolated cwd/input file hash и фактический sysroot/toolchain identity;
   это не std SmallSort selector и не тот же library-tree binding.
3. На каждый pin свой frozen `.github/actions/setup`, штатные deps/toolchain (nightly-2026-10-23, CBMC6.11, solver pins
   проверить по исходникам), никаких compiler/runtime edits/upgrades/патченного backend.
4. Удалить стандартные workflows **только в CI-only overlay**, оставить один узкий workflow с repository/branch guard.
   Использовать accepted fork push-trigger pattern: package `[skip ci]`, non-skip same-tree trigger создаёт координатор.
   Worker не публикует branch, не dispatch и не создаёт PR. Оба checkout fetch-depth≥2, persist-credentials false.
5. Source binding пересоздать для каждого source pin. Старые570 hashes/7 subtrees — образец coverage, не baseline manifest.
   Exact std overlay/test paths, source/tree/submodules/setup/request/checksums проверить до/после; никаких cleanup для сокрытия drift.
6. Actual argv/env allowlist, Rust/types/target/root/mode, binary/runtime/solver hashes, begin/end phase, durations,
   raw wait4 RSS KiB и правильные MiB/GiB, driver/backend и aggregate RSS. Не складывать peaks разных моментов как simultaneous RSS.
7. Group timeout TERM→grace→KILL, original exit/signal, OOM/runner loss отдельно. Bounded output, explicit TRUNCATED/UNKNOWN;
   artifacts `always()`, fallback receipt, retention7d. Не ставить RLIMIT_FSIZE глобально на setup/build.
8. Per-invocation stdout/stderr≤32MiB, metadata≤16MiB/job, artifacts≤256MiB/job; превышение — INCOMPLETE,
   а не PASS. RSS-watchdog/порог с резервом ОС записать по доступной RAM до dispatch; не повышать после kill.
9. Synthetic tests: success/intended verifier failure, parser failure, setup-only, timeout/signal/output cap,
   wrong pin/tree/fixture/selector, post-run source drift, missing row, native-vs-std argv mixup; known recipe wiring-error mutations.
   Не запускать локально cargo/Kani/setup scripts. Исторические raw logs/archives не скачивать; использовать curated evidence.

## 7. Deliverables, приёмка подготовки и handoff

В `kani3300/w0-a1/`: INPUTS/identities; ROUTE-MAP + exact selectors/expected useful covers;
ISSUE-REPRO-MAP (official bytes/commands/adaptations/oracles); std-test-only patch/manifest;
native fixtures (копии source, не runtime logs); R1/R2 requests и условие R3; CI-only patch(es)/commit identities;
CHECKLIST, offline VALIDATION с результатами synthetic tests, RESULT template со всеми полями UNKNOWN/NOT_RUN.
Приёмка подготовки — согласованная source/fixture/mode/budget привязка и отсутствие compiler/runtime diff.
Ожидаемый future legal PASS требует0 unexpected failures, достигнутых return/readbacks и прошедших unwinding checks;
named hole/canonical crash cases оцениваются по §4. Receipt UNKNOWN сам по себе не proof.

Статический diff allowed: CI-only workflow/scripts/native fixtures; std — новый verification module и registration.
Любая необходимость менять target algorithm/preconditions/Kani implementation → STOP с reproducer/design question.
Не подменять controls соседними padded/Copy тестами; не менять empty Drop; не добавлять предположения о holes.
Все future outcomes должны различать bug reproduced/fixed, baseline already different, Unsupported, timeout и fixture-blocked.

Source-test package и CI-only packages — локальные отдельные commits; research commit только своих путей,
`[skip ci]`, author/committer Tiramisu-Cake <igkharin@gmail.com> через per-command `git -c`, без Co-Authored-By.
Без push. Завершить `READY <g0 research sha> <local package sha(s)>` и путём к CI-REQUEST.
Это готовность материала координатору, не выполненный A1/proof gate. Анализ запущенных им R1/R2 — следующая сессия.
