# Challenge 8 — единый ledger fork dispatch

2026-11-16. Владелец принял P0: прежние18 пункта1 + дополнительные14 пункта2, **совместно≤32**.
Это верификация корректности, не security-работа. Только fork CI; Cloud $0.
Ledger — учёт разрешённого envelope, не самостоятельное разрешение запускать workflow.
Push/dispatch/резерв/receipt reconciliation ведёт **координатор**, worker14 помогает inventory/review.
Workers11/13/15 сюда параллельно не пишут: передают CI-REQUEST и желаемый slot координатору.

## 1. Правила списания и привязки

1. Период — новая согласованная итерация W0/S1–S5. Исторические C2/SEL1/replay runs не переносятся в
   расход этой итерации. На момент создания W0 не запущен; **recorded actual=0**. Перед первым новым
   запуском координатор сверяет, не было ли dispatch после этого сообщения; неизвестное не считать0.
2. Единица — один реально принятый fork workflow run; каждое начатое rerun/attempt расходует ещё1.
   Matrix/jobs/количество roots не умножают dispatch count, но их time/RSS/runner-min envelope обязателен.
   Ошибка setup/infra, cancel или watchdog после принятия run тоже расходуют1; без auto-rerun.
3. Сначала запись RESERVED с точным request SHA, source/tool/tree/flags/rows/caps и coordinator GO;
   затем run ID/attempt и CHARGED. Неиспользованная reservation может быть RELEASED только без принятого
   запуска. QUEUED/RUNNING/UNKNOWN принятого run уже charged; неизвестное отсутствие run сверить до retry.
4. Run, заранее спроектированный для двух дорожек, списывается **один раз** на основной bucket; в строке
   есть вторичные evidence bindings. Нельзя задним числом уменьшить расход за похожие имена roots.
   Другая source/flags/comparator/property остаётся отдельным свидетельством, даже если общий run.
5. Локальные preparation/static/synthetic checks стоят0 dispatch. Upstream automatic PR CI отдельно
   помечать EXTERNAL и не выдавать за fork allocation; ручные fork runs нельзя так исключить из бюджета.
6. Внутри row/lane cap, item1≤18, S≤14, total≤32 одновременно. Резервный cap — не задача использовать всё.
   Перераспределение между дорожками/повышение cap требует решения координатора в пределах уже принятой
   постановки, а при смене scope/потолка — владельца; записать решение **до** следующего dispatch.
   Нет неявного займа S credits для safety или второго S1 бюджета worker11.
7. Scheduler учитывает совокупный runner load: один prepared workflow не резервирует все slots.
   Prototype jobs1; concurrent jobs/run caps из CI-REQUEST, не число работников. Никаких uncapped matrix.

## 2. Потолки по дорожкам

Все значения cap — верхние; будущие conditional stages остаются NOT_RUN/не выданы до своих gates.
Диапазоны оценок из планов здесь заменены конкретными максимальными buckets, без двойного запаса.

| Bucket | Responsible / writer | Cap | Recorded charged | Remaining | Gate / использование |
|---|---|---:|---:|---:|---|
| U | 14; публикация владельцем | 1 | 0 | 1 | Metadata/text preparation0; только конкретный разрешённый integration check |
| A1 | 15 | 3 | 0 | 3 | R1 scale + R2 native controls; R3 только адресный reserve |
| E | 15 design;13 core | 4 | 0 | 4 | Unbounded insertion safety-only; отдельная постановка/STOP |
| Profiles-ON | 11 profiles;15 ON | 3 | 0 | 3 | Статический dispatch с сохранением P-specific orders, не только S KeyLess |
| B | 14 census; compiler owner отдельно | 3 | 0 | 3 | Valid-value census/canaries; WIP/design gate |
| C-now | 14+13 inventory/frame | 2 | 0 | 2 | Ограниченные frame claims; не новый alias model |
| D | 14 coordination | 2 | 0 | 2 | #5104, maintainer coordination; отдельный GO |
| **Item1 subtotal** | | **18** | **0** | **18** | Прежний allocation |
| S1 | 11 model;13 integration;14 review | 2 | 0 | 2 | Один combined smoke batch + один условный corrective dispatch |
| S2 | 11/13/15;14 inventory | 2 | 0 | 2 | Три cost probes + ранний bounded merge pilot |
| S3 | 11/15 leaves;13 integration | 5 | 0 | 5 | Только после P2, qualified semantic domains |
| S4 | 13 entries;11/14/15 review | 2 | 0 | 2 | Symbolic N/classes, все применённые leaves qualified |
| S5 | 13 freeze;14 CI inventory | 3 | 0 | 3 | Matched Linux/macOS costs/ordinary CI fit и controls |
| **Item2 S subtotal** | | **14** | **0** | **14** | Новый принятый allocation |
| **TOTAL** | coordinator | **32** | **0** | **32** | Одновременно соблюдать все caps |

S1-01 обязателен после review подготовленного пакета; S1-02 **условный**, не заранее выданный второй прогон.
A1 имеет2 mandatory+1 conditional, как в обновлённом W0-A1. Очередь S1 smoke/A1 scale/S2 costs
согласуется координатором; наличие пакета не создаёт дополнительного dispatch/первоочередного runner slot.

## 3. Source/claim profiles

| Profile | Frozen начальные inputs | Flags / смысл |
|---|---|---|
| S | std872d5a43380752786415bc00d2a12ce0e930cb37 + named S export; stock Kani0aac16ef62da9e9d5645782d458593e5d78143ba | Organizer flags, object-bits12, uninit/value OFF; threshold sorting |
| A1 scale | std70ba5befc617627073738e26cb1466bd4fb76e41 +6075e7ce17179f45642c9ffe8fe09e3ec9395726 + named A1 overlay; SEL114bc57fdb99960240c4944845a3d985c8af4dcf7 | Uninit ON, actual bodies/arbitrary-bool closure, normal-return scope |
| A1 native | Exact issue fixture bytes, stock0aac vs SEL114bc | Отдельные native inputs/modes/argv, не std-root verdict |

Object bits, comparator, PFC/Original/Replace mode, model/contract version, T/N/geometry — часть каждой
привязки. Stock tool0aac общий для S и A1 baseline не делает их результаты взаимозаменяемыми.
Не запускать safety root с новым S KeyLess без отдельной ON qualification.

## 4. Actual runs — append-only учёт

Ниже пока **нет принятых запусков новой итерации**. Не записывать подготовку workflow как run.

| ID / bucket | State / charged | Run ID / attempt / URL | Request SHA + owner GO | Std export SHA/tree; tool SHA/tree; CI-control SHA | Roots/mode/T/N/geometry; flags/model | Runner/jobs/time/RSS/output caps | Outcome/receipt; secondary evidence |
|---|---|---|---|---|---|---|---|

Перед dispatch добавлять одну полную строку. Точные длинные manifest/argv/row oracles можно вынести в
связанный CI-REQUEST, но его path+SHA обязательны. Для новой попытки — новая строка с previous ID/reason,
не переписывание потерянной истории. После terminal run: время/exit/signal, raw RSS KiB и перевод в
GiB `/1048576`, все failed properties/useful covers, UNKNOWN/TRUNCATED, curator acceptance link,
source-clean/binary hashes. Verifier intended failure, workflow failure и proof acceptance различать.

## 5. Предстоящие reservations (пока не заняты)

| Suggested ID | Task/request | State | Precondition |
|---|---|---|---|
| S1-01 | `TASK-CH8-S1-W13.md`; integration CI-REQUEST ещё NOT_READY | NOT_RESERVED / NOT_RUN | Модель11+интеграция13 reviewed, точные SHA/rows/caps известны |
| S1-02 | Условная адресная поправка/repro | NOT_RESERVED / NOT_RUN | Review S1-01 + coordinator GO, не sweep/новый compiler patch |
| A1-R1 | `TASK-CH8-W0-A1.md` | NOT_RESERVED / NOT_RUN | Пакет15 reviewed, slot согласован рядом с S |
| A1-R2 | Тот же TASK, native controls | NOT_RESERVED / NOT_RUN | R1 review/independent controls readiness, отдельный GO |
| A1-R3 | Conditional fixture/middle-pin reserve | NOT_RESERVED / NOT_RUN | Конкретный вывод R1/R2 и coordinator GO |

Последняя сверка: создание ledger после принятия P0, CI в этой planner-сессии не выполнялся.
Расход обновляется по actual runs, не по запланированным строкам. Full old C2/SEL1 Gate A не повторять
автоматически для S annotations; quality/combined-ON — отдельные будущие решения, не скрытые S1 jobs.

## Coordinator note 2026-11-16 ~01:45 UTC — branch-creation side effect (not a planned dispatch)

Creating fork branches `fix/kani-3300-init-01-analysis` (`d82752c8bc`) and `fix/kani-3300-init-02-immutable` (`932fb8395a`) for the
owner's PR-01/02 triggered the stock workflows (Kani CI, Format Check, Cargo Deny) on both heads: runs 43770775497/532/486 and
43770775542/591/535. All six were cancelled within ~1 minute; no results are used as evidence. Not counted against any track cap
(no planned evidence produced). Lesson: create PR branches only when the owner opens the PR, or push a commit whose workflows are
inactive; upstream PR CI provides the full matrix.

## Coordinator dispatch log

| UTC 2026-11-16 | ID | Track | Head / trigger | Run | Note |
|---|---|---|---|---|---|
| ~02:00 | A1-R2 | A1 (item 1) | pkg `bf81a1f14f` → trigger `71b4a05915` | 43772128176 | baseline 0aac vs SEL1 issue controls #5020/#4854/#5151 |
| ~02:00 | A1-R1 | A1 (item 1) | pkg `bf81a1f14f` → trigger `a47d28da27` | 43772128212 | 8 SEL1 ON scratch roots (N32 first); queued behind R2 (concurrency group) |

| 23:11Z (02:11 MSK) | S1-01 | S1 (item 2) | std pkg `e6ee41020e` → control `f88bf3f0ea` on Tiramisu-Cake/verify-rust-std `uninit-ci/ch8-s1-a` | none created | Std fork created no Actions run/check suite; same-tree sibling `ed145ae990` (branch -c) and minimal probe `7d49b71cb1` also produced nothing; extra branches deleted. Charged 1 (attempt). Contingency: kani-fork host variant (TASK-CH8-S1K-HOST-W13). If a std-fork run appears late, keep one, cancel the other. |
| 23:27Z (02:27 MSK) | B-01 | B (item 1) | pkg `5ee153ec2b` (tree `f9d2bfdc79`) → trigger `08e556fe14` on Tiramisu-Cake/kani `uninit-ci/ch8-b-census-a` | 43774504122 | 235 roots, shards 2+4, request SHA256 `a443bb3f…1724`, roots SHA256 `7dee264d…8a85`; review READY_WITH_LIMITATIONS. |

Reservations (not dispatched yet): U-01 PR-02 entry-reset fix CI (TASK-CH8-PR02-RESET-W15); PROF-OFF-01 profiles OFF batch (TASK-CH8-PROF-OFF-W11).
Note: earlier rows "~02:00" are MSK (≈23:00Z on 2026-11-15).

| 23:40Z (02:40 MSK) | S1-01k | S1 (item 2) | kani-host control `36db70978a` (tree `f3d36d51f5`, parent tool 0aac) → same-tree sibling `83f88a9075` on Tiramisu-Cake/kani `uninit-ci/ch8-s1k-a` | 43775527125 | Same 23 rows/runner bytes as `f88bf3f0ea` (g0 `dd6a00ec38`, kani-host/BATCH-IDENTITY.json). Std-fork branch `uninit-ci/ch8-s1-a` deleted; a late std run, if any, is cancelled and not used. |

Charging decision (coordinator): S1-01 on the std fork produced no run/check suite (no runner time, no evidence) — recharged to 0, same treatment as the branch-creation note; S1-01k is the charged S1 dispatch.

Outcomes:
- S1-01k 43775527125: FAILURE at compile of `core` (setup/build OK, 349 s, 1.39 GiB); 23/23 rows NOT_RUN. Cause: std 872d (nightly-10-22 library) vs Kani 0aac (nightly-10-23) — missing upstream #745; plus one E0369 typo in S. Charged 1. See TASK-CH8-PPRIME-REBASE.md.
- B-01 43774504122: CANCELLED by coordinator ~23:55Z (same 872d+0aac incompatibility; result would be compile failures only). Charged 1.
- A1-R1 43772128212: FAILURE, 8/8 matrix rows UNKNOWN — each `kani verify-std` exited 1 after ~20 s compiling `core` with **8652 errors** (std base `70ba5befc6`, nightly-10-23 = same as Kani SEL1 `14bc57fdb9`; the SEL1 replay 43751703000 compiled this base fine, so not a toolchain mismatch). Env had `RUSTFLAGS=--cfg kani_smallsort_controls` + `-Z uninit-checks`. stdout.log (10.7 MB, sha256 436210c7…) was removed by the artifact metadata cap, so the first errors are not preserved — runner must keep a bounded stdout head/tail. Charged 1 (A1 2 of 3 used; R3 reserve must cover this + #5151 fixture).
- Shared base P′ `c5ff36ff43` (merge 872d + upstream main 6079edcda3) on std fork `experiment/ch8-pprime-20261116`.

| ~00:10Z | S1-02 | S1 (item 2) | S′ `f22f84f316` (P′ + S commits + E0369 fix; std fork `experiment/ch8-s1-pprime-20261116`); control `8c8ac10d67` (tree `f0a7d1d51f`) → sibling `79542c7733` on Tiramisu-Cake/kani `uninit-ci/ch8-s1k-b` | 43777127361 | Same 23 rows/caps; upload excludes target/. g0 `e766e3993f` kani-host-pprime. Profiles OFF (source `9fa2f7f977`, control `6269319aec`) held until S1-02 passes the core compile. |

| ~00:20Z | U-01 | U (item 1) | source `f695f653ef` (PR-02 `932fb8395a` + entry-reset fix + 7 fixtures); CI pkg `b4edbb18bc` (tree `a5a1c0b0b0`) → trigger `e4bf2df0ca` on Tiramisu-Cake/kani `uninit-ci/ch8-pr02-reset-a` | 43777434715 | Arm A PR-02+fix vs old PR-02 matched; arm B SEL1+fix with original #4854 autoharness + explicit companion. g0 `21b3174275` ch8-pr02-reset/. |

- S1-02 43777127361: FAILURE at list phase — P′ + Kani 0aac **compiles** (core/alloc/std Finished in 5m22s; setup 215.6 s, 1.39 GiB), but `kani list` over verify-std does per-harness codegen and was killed at the 600 s per-invocation timeout; 23/23 NOT_RUN. Charged 1. Coordinator reserves S1-03 from the item-2 pool (≤14 unchanged) as a retry after infra-only failures; S1-03 is the last S1 attempt without owner input. Fix task TASK-CH8-S1-LIST-W13.

- U-01 43777434715: arm B SUCCESS — SEL1+fix: original #4854 autoharness SUCCESS 154/0 (was fatal `reset is absent`), explicit companion SUCCESS 156/0. Arm A FAILURE (packaging): compiler units 66/66, suites 56/0 and 134/0, then compiletest rejected nested `script-based-pre/autoharness_entry_reset/<case>/` (no config.yml) → new regressions + old-PR-02 controls NOT_RUN; arm A had no upload step. Charged 1. U-02 (arm A only) reserved from the item-1 pool (U 2, item 1 ≤18 unchanged). Task TASK-CH8-PR02-RESET-FIX2-W15.

| ~00:40Z | A1-R3 | A1 (item 1) | pkg `e3e9f138b7` (tree `483b25c43c`, parent `bf81a1f14f`; std fix `312ff625b9` = `super::super` trait import in wave0_a1.rs, #5151 edition fixture, bounded stdout head/tail, fail-fast) → trigger `efddfd120b` on Tiramisu-Cake/kani `uninit-ci/ch8-w0-a1-r3-a` | 43779285270 | Last A1 credit; ≤230 runner-min. g0 `724a115fd0` w0-a1/r3/. |
| ~00:55Z | U-02 | U (item 1) | source `09a6d1cb2c` (PR-02 + same compiler diff as U-01, fixtures flattened to top-level script-based-pre dirs); pkg `952ea771be` (tree `6635864584`) → trigger `235b30ffb8` on `uninit-ci/ch8-pr02-reset-b` | 43780092728 | Arm A only (B already SUCCESS in U-01 with identical compiler diff, sha256 f7beb5f9…). g0 `c45f6fac53` u02/. |
S1 list fix (a) `c03363b3b0` (list timeout 1500 s) rejected by coordinator: organizers' `Run Kani List` on verify-rust-std main takes 73 min (run 43765200249). Redo as per-row binding (TASK-CH8-S1-LIST2-W13).
- A1-R3 43779285270: std compiles; SEL1+uninit N32 stable_freeze (895 props) and general_nocopy (907) each fail exactly 1 property — unsupported uninit layout of `PolymorphicIter<[MaybeUninit<usize>;2]>` (array::IntoIter from smallsort.rs:307); network N32 killed by RSS watchdog at 13.57 GB; other 5 rows NOT_RUN (fail-fast). #5151: baseline 0aac unsupported (both), SEL1 negative = intended UB failure, companion SUCCESS 142/0 → C2 fixes #5151. Details w0-a1/r3/run-43779285270/RESULT.md. A1 cap exhausted.
- U-02 43780092728: fmt/build/clippy OK; compiler units 66/66; expected uninit 56/0, function-contract 134/0; new autoharness_entry_reset 5 passed / 2 failed — both failures are fixture defects (`Interaction between raw pointers and unions is not yet supported` in initialized_read/uninit_read); old-controls NOT_RUN (runner stopped). Charged 1. U-03 needed (fixtures via padding byte, independent gates) — item-1 pool. TASK-CH8-PR02-RESET-U03.
| ~01:35Z | PROF-OFF-01 | Profiles (item 1) | source `9fa2f7f977` (P′; std fork `experiment/ch8-profiles-pprime-20261116`); control `242ca63174` (tree `41888f1116`, parent 0aac) → sibling `56caab8637` on `uninit-ci/ch8-prof-off-a` | 43782419242 | First batch-mode std runner: 2 groups (53 ordinary + 9 controls-cfg), no global list, 900 s compile deadline per group. g0 `6ebb06255c` off-ci-batch/. |
- PROF-OFF-01 43782419242: FAILURE in 1 s at control validation — workflow `--repo ../..` points at the workspace root (S1 uses `--repo ..`); nothing built or run. Charged 1 (accepted attempt). Fix task TASK-CH8-PROF-OFF-FIX-W11; retry PROF-OFF-02 from the item-1 pool.
| ~01:55Z | U-03 | U (item 1) | pkg `80d0d98529` (tree `4237f7d2c8`; padding-byte uninit fixtures, independent gates) → trigger `a7c80d91b4` on `uninit-ci/ch8-pr02-reset-c` | 43783429976 | Arm A only; same compiler diff. |
| ~01:55Z | E-01 | E (item 1) | control `628ba7fd9b` (tree `72cbddf7e0`, parent 0aac) → sibling `3219b3f220` on `uninit-ci/ch8-e-ctl-a` | 43783430196 | Isolated single-file E-Q/E-S/E-H controls, matrix upstream 0aac + SEL1; no std build. g0 `74e78ab8cb`. |
| ~02:10Z | S1-03 | S1 (item 2) | S′ `f22f84f316`; grouped control `40b5d9cf48` (tree `c17af28753`, parent 0aac; 5 groups by variant/unwind, no global list) → sibling `8233b98c15` on `uninit-ci/ch8-s1k-c` | 43784240498 | Last S1 attempt. g0 `2b49cb29d9` kani-host-nolist/batch/. Per-root RSS UNKNOWN by design (group-scoped). |
| ~02:20Z | PROF-OFF-02 | Profiles (item 1) | control `741b7183b4` (tree `452b26330b`, parent 0aac; `--repo ..` + static path preflight) → sibling `075750ca90` on `uninit-ci/ch8-prof-off-b` | 43784551069 | Retry of PROF-OFF-01. g0 `9edcf937b7` fix1/. |
- E-01 43783430196: completed (runner success). Export verdicts: E-Q pointer invariants FAIL even OFF (positive too), ON no export; scalar invariant SUCCESS all; E-H OFF SUCCESS, ON upstream unsupported MaybeUninit arrays, ON SEL1 `self->value is assignable` failures (shadow vs loop assigns?); E-S no export. Intake TASK-CH8-E01-INTAKE-W15.
- U-03 43783429976: units 66/66, uninit 56/0, contracts 134/0, autoharness suite 54 passed + new entry_reset 6/7; only `uninit_read` fixture failed (padding read not treated as uninit → SUCCESS). Matched old PR-02: seed_only/argument_seed/contract_seed fatal `reset is absent`, no_seed completed. Coordinator: drop uninit_read, finalize PR-02 with 6 fixtures (no further CI). TASK-CH8-PR02-FINAL-W11.
- E-01 intake (g0 `4596de81f5`): STOP E for current encoding — loop frame lacks shadow-memory allowance under uninit ON (function contracts have it); `kani::exists` ignored OFF; E-S fixture namespace error (E0425). Issue draft unpublished.
- PROF-OFF-02 43784551069: batch mode works — group-00 53/53 SUCCESS (covers 179/179), group-01 9/9 FAILURE on their named checks; compile 53 s/33 s; phase 1661 s; group RSS 4.0 GiB. Runner classified all 62 rows UNKNOWN (`SOURCE_STAGE_TARGET_MISMATCH`) — binding defect under investigation (TASK-CH8-PROF-OFF-INTAKE-W11).
| ~01:50Z (02:… local next day) | C-01 | C (item 1) | std `d073585946` (P′ + c_controls; std fork `experiment/ch8-c-ctl-pprime-20261116`); batch control `64ec781bc1` (tree `33e95dc779`) → sibling `d224c83361` (parent 0aac) on `uninit-ci/ch8-c-ctl-a` | 43788110742 | Batch mode. g0 `7577118b79` ch8-c-ctl/batch/. |
| ~01:50Z | B-02 | B (item 1) | std P′ `c5ff36ff43`; batch pkg `99dbb2157b` (tree `10421f334c`) → child trigger `f601ca74ca` on `uninit-ci/ch8-b-census-b` | 43788110361 | 235 roots, one multi-harness invocation per shard. g0 `7577118b79` ch8-b/pprime-batch/. |
- C-01 43788110742: N1 merge write-restore caught (`Check that *dst is assignable`) + unwinding assertion; merge read-only companion fails only on unwinding assertion (fixture unwind); N2 live-shared SUCCESS (documented alias gap); L3/L4 SUCCESS. Covers 18/30. Intake + C-02 (unwind fix) → TASK-CH8-C01-INTAKE-W14.
- B-02 43788110361: success; 235/235 complete in one invocation, wall 887 s, peak 3.29 GB: PASS 11, copy Unsupported 224 (`ptr::copy_nonoverlapping::<u8>.unsupported_construct.1` under `-Z valid-value-checks`). Intake TASK-CH8-B02-INTAKE-W14.
- S1-03 43784240498: batch completed 3 of 5 groups. SUCCESS: stable/unstable_default_cell (≈327 s each), stable_freeze_activation (35 s), stable_default_activation, swap type matrix, inactive pairs, snapshot companion, corruption companion, 3 models N0..3. TIMEOUT 600 s: freeze_copy_u8, freeze_default_noncopy, stable_freeze_u8, unstable_freeze_u8. 6 negatives fail with runtime-formatted placeholder description (oracle must bind by property ID). 2 activation groups NOT_RUN (phase exhausted). S1 cap (3) exhausted — S1-04 only with owner. Intake TASK-CH8-S1-03-INTAKE-W13.
| ~02:20Z | C-02 | C (item 1) | std `597e54c5cb` (merge pair unwind 17; std fork `experiment/ch8-c-ctl-pprime-c02-20261116`); control `59b5c663e3` (tree `e10c359aba`) → sibling `b97c4d6cf6` on `uninit-ci/ch8-c-ctl-b` | 43790257718 | Last C credit. g0 `905a3550b8`. |
- C-02 43790257718: N1 write-restore FAILURE exactly `Check that *dst is assignable` (covers 4/4); read-only companion SUCCESS (covers 3/4). C cap exhausted. Intake TASK-CH8-C02-INTAKE-W14.
| ~02:40Z | E-02 | E (item 1) | control `79baf66106` (tree `c07b5aded5`, parent 0aac) → sibling `4a8f7e7b10` on `uninit-ci/ch8-e-ctl-b` | 43792979809 | E-S namespace fix + primitive H positive/no-write/OFF + MRE row; pins 0aac + SEL1. g0 `39c756108c`. |
- E-02 43792979809: success (runner). primitive_write ON fails exactly `Check that self->value is assignable` on **upstream 0aac and SEL1**; OFF / no_write / no_loop SUCCESS → loop contracts × uninit-checks defect is upstream. E-S positive OFF fails offset check; ON unsupported intrinsic. Intake TASK-CH8-E02-INTAKE-W15.
- PROF-OFF-02 acceptance v4 (offline, g0 `9c7ffcb385`, accept-v4/): **62 ACCEPTED / 0 PENDING / 0 UNKNOWN** (53 positive, 9 negative) under ACCEPTANCE-POLICY-BATCH.md; exact contract-wrapper binding, unsupported/unreachable roles, cover→obligation mapping established. Proof credit NONE (bounded source-reported observations).
| ~03:35Z | PROF-ON-01 | Profiles (item 1) | source `9fa2f7f977` (P′); control `d569db0c1f` (tree `660633a37f`, parent SEL1 `14bc57fdb9`) → sibling `7f33fb9067` on `uninit-ci/ch8-prof-on-a` | 43798838603 | Uninit ON on SEL1, same 62 rows, accept-v4 classifier reuse. Known risk: rows 47/59 reach PolymorphicIter. g0 `2469887b0e`. **Outcome:** all 62 OBSERVED; intake w15 accept-v4 (g0 `32d701fbfd`): **49 ACCEPTED, 13 BLOCKED_TOOL** (array_assume_init 8, PolymorphicIter 2, write_any_slice havoc 2, fn-item layout 1), 0 rejected. Harness workarounds → PROF-ON-02 (w11). |
| ~08:20Z | PROF-ON-02 | Profiles (item 1) | source `166a406e22` (tree `460029c0d9`, on P′ `9fa2f7f977`; std branch `experiment/ch8-prof02-pprime-20261116`); reviewed control `1352f9d15d` (tree `1352d0b759`) → trigger `5710dd6758` (parent SEL1) on `uninit-ci/ch8-prof02-a` | 43808894294 | One dispatch, two sequential jobs: ON on SEL1, then OFF on 0aac (OFF runs even if ON fails). 63 rows = 62 + new `profile_merge4_contract_u8_len4`. Harness workarounds A (array literal), B (thin modifies sort4; exact merge4 profile), C (closure comparator); PolyIter rows remain BLOCKED_TOOL. Static review GO, g0 `7d1ae3dd04`. **Outcome:** ON **61 ACCEPTED / 2 BLOCKED_TOOL** (PolymorphicIter: freeze_noncopy_n2, rejects_always_true; w15 accept-on); OFF **63/63 ACCEPTED**, all 62 prior verdicts kept + merge4 leaf (w11 accept-off, g0 `b044aa4502`). |
| ~07:58Z | S1-04 (a) | S1 (item 2, owner GO 2026-11-16 morning) | std `5be85699b8` (std branch `experiment/ch8-s1-04-pprime-20261116`); control `5fd5387308` on `uninit-ci/ch8-s1k-d` | 43827636574 | **Rejected by GitHub workflow schema, 0 jobs** (quoted booleans/numbers after YAML re-serialization). Package defect; no execution. Charge 0. Fix: w13 `2a532e5913`. |
| ~08:10Z | S1-04 (b) | S1 (item 2) | same std; control `2a532e5913` on `uninit-ci/ch8-s1k-e` | 43829165289 | **Validate step failed in every started job** (`git diff 0aac..HEAD` exit 128: control checkout fetch-depth 2 < ancestry depth 3). Cancelled by coordinator before any build. Package defect; no proof result. Charge 0. Fix: w13 depth-fix. |
| ~08:35Z | S1-04 (c) | S1 (item 2) | same std `5be85699b8`; control `205b0e98c7` (parent `40b5d9cf4`, control checkout depth 3) on `uninit-ci/ch8-s1k-f` | 43830757263 | 14 groups, max-parallel 1, light→activation→Cell→heavy; heavy rows split exact N=0..3. g0 depth-fix `b7268f6f79`. Outcome: 35 executed, 27 SUCCESS / 8 FAILURE (negatives). Offline acceptance w11 (g0 `64eded688d`): PENDING — positive 0, 3 qualified negatives, 30 UNKNOWN, 2 OBSERVED_UNQUALIFIED; cause: runner `--output-format=terse` drops descriptions/locations of unreachable checks and covers, so roles cannot be bound. Next package must keep the rich export. |
| 12:15Z | S1-05 | S1 (item 2, owner: more runs allowed 2026-11-16) | same std `5be85699b8`; control `8860d38558` (parent `40b5d9cf48`; regular output + rich inventory, record-only runner, F7/F8 oracles frozen) on `uninit-ci/ch8-s1k-g` | 43864841077 | g0 package `9a798b848f` (w13, 46 tests, independent review). Acceptance offline per ACCEPTANCE-POLICY-BATCH. |
| ~08:35Z | ISSUE-MRE-01 | Issues (item 1) | clean upstream `0aac16ef62`; control `d860e30592` (tree `ba4b7298f0`) → sibling `e6e2a06ccf` on `uninit-ci/ch8-issue-mre-a` | 43830763471 | Owner: publish issues after review. 10 invocations: valid-value copy (copy_integer, raw_bool_overwrite/read) + slice havoc (orig / initialized / thin targets / negative uninit read). Predeclared 5 SUCCESS, 3 COPY_UNSUPPORTED, 2 UNINIT_FAILURE. g0 `e609557732`. **Outcome:** valid-value confirmed (copy_integer: sole failure `copy_nonoverlapping::<u8>.unsupported_construct.1`; bool controls Unsupported) → #3762 comment draft. Slice havoc NOT reproduced: missing `-Z stubbing` (compile error) and upstream lacks uninit support for `[MaybeUninit<u8>;2]` → MRE v2. |
| ~08:55Z | ISSUE-MRE-02 | Issues (item 1) | clean upstream `0aac16ef62`; control `47616f4105` (tree `4700ee944e`) → sibling `66625d5267` on `uninit-ci/ch8-issue-mre2-a` | 43833191287 | Slice havoc v2: alloc-based buffer (no union), `-Z function-contracts -Z uninit-checks -Z stubbing`; 7 harnesses, predeclared 5 SUCCESS / 2 UNINIT_FAILURE. g0 `a0c7d25936`. Last item-1 dispatch. **Outcome:** all 7 match predictions: slice havoc on uninit output — sole failure `write_any_slice::<u8>.safety_check.1`; initialized / thin targets / bodies SUCCESS; negative read FAILURE as expected. Defect reproduced on clean upstream → issue draft `kani3300/issue-mre2/ISSUE-DRAFT.md`. |
C-01 dispatched (was held for the list fix; now batch, no global list).
C-01 held (superseded): C controls (std `d073585946` on P′, control `cdd3c6d041`, g0 `425f10fbfd`) use the same global `kani list` that timed out in S1-02 — dispatch after the list fix.

Item 1 used: 18 of 18 (A1 3, B 2, U 3, Profiles 4, E 2, C 2, Issue-MRE 2). Item 2 used: 5 of 14 (S1 5; S1-04 a/b charged 0). Total 23 of 32.
