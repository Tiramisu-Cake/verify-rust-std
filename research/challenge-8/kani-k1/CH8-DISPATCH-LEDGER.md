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
| 12:15Z | S1-05 | S1 (item 2, owner: more runs allowed 2026-11-16) | same std `5be85699b8`; control `8860d38558` (parent `40b5d9cf48`; regular output + rich inventory, record-only runner, F7/F8 oracles frozen) on `uninit-ci/ch8-s1k-g` | 43864841077 | g0 package `9a798b848f` (w13, 46 tests, independent review). Acceptance offline per ACCEPTANCE-POLICY-BATCH. | **Outcome (w13 intake g0 `117211ae14`):** 35/35 harness completed (27 SUCCESS, 8 FAILURE — same as S1-04); runner decoder aborted on stock properties without file/line in 10 groups (2976 of 9986 rich records kept). Acceptance: 0 qualified, 3 exact negatives. Decoder fix `b25dd39a46`. |
| 13:40Z | W0-F1 | Item 1 (wave 0, owner +6) | F1 source `bc8f8bb57e` (parent 0aac; is_harness recognises automatic harnesses + script-based-pre test) pushed as `fix/autoharness-uninit-reset` → stock Kani CI / Format / Deny | 43875368192 | Full standard workflows (5 regression platforms). Testing link for the F1 PR. |
| 13:50Z | W0-5172-fixup | Item 1 (wave 0) | fixup `80e5d6fabc` (single commit on #5172 head `6fe484b300`; tree = w11 `5d5035f5a`: checked_body in resolve_call + comment rewording, diagnostics unchanged) as `fix/kani-uninit-unresolved-call-v3-fixup` → stock Kani CI / Format / Deny | 43876038189 | Push of the same SHA to #5172 only after owner review. |
| 14:30Z | W0-CONFIRM (a) | Item 1 (wave 0) | control `6b653427d2` (stock 0aac + F1–F4 probe tests) → same-tree trigger `fd036c225f` on `uninit-ci/confirm-main-w15` | 43878357528 | **Rejected by GitHub as a workflow-file error, 0 jobs** (`runner` context in `jobs.<id>.env`). Charge 0. Fix: w15. |
| 14:45Z | W0-5151 | Item 1 (wave 0) | control `0a9e3bdb8a` (w13; #5151 reproducer: initialized-slot, original-empty-drop, read-in-drop on stock 0aac vs prototype 8e299aa624) → trigger `dbfb4d8bd8` on `uninit-ci/ch8-5151-a` | 43878900159 | Part 1 only. #649 part (56 candidates, 77 unconfirmed) gated separately. **Outcome: all 6 rows UNKNOWN — tests fail to compile (E0433 `core` with edition 2015 on single files). Package defect; fix w13.** |
| 14:55Z | W0-CONFIRM (b) | Item 1 (wave 0) | control `bb427b45f3` (workflow env fixed) → trigger `9a40f247ee` on `uninit-ci/confirm-main-w15-b` | 43879576728 | F1–F4 probes on stock 0aac + access-padding control. g0 `712cb6fac0`. **Outcome: all rows INCONCLUSIVE incl. control, no artifact (upload path with `..`). Package defect; fix w15.** |
| 15:05Z | W0-5151 (b) | Item 1 (wave 0) | control `5725e5ca3d` (edition 2021 via compile-flags) → trigger `1d81977607` on `uninit-ci/ch8-5151-b` | 43881766306 | Same three tests; g0 `744098133f`. **Outcome (coordinator read of artifacts):** stock — all three UNSUPPORTED (union / raw-pointer interaction); prototype — initialized-slot SUCCESSFUL; original issue example and read-in-drop FAILED at `drop_in_place::<D>.safety_check.1` "Reading from an uninitialized pointer of type `*mut D`" (the invalid drop is detected). Runner labels prototype rows UNKNOWN (its oracle expected a different property). |
| 15:10Z | W0-CONFIRM (c) | Item 1 (wave 0) | control `2e889f7571` (artifact path in workspace, bounded per-row diagnostics, edition 2021 for single files) → trigger `d7e0c6bea9` on `uninit-ci/confirm-main-w15-c` | 43882466907 | g0 `561bc4e0c0`. Item 1 budget exhausted after this run. **Outcome (coordinator read of artifacts; runner marks all INCONCLUSIVE because of benign `same_allocation`/`Location::caller` unsupported constructs):** control FAILED as expected; **F1 confirmed** (autoharness: both functions SUCCESSFUL, padding read missed); **F2 not shown** (typed read correctly FAILED); **F3 confirmed** (`rustc` stack overflow, SIGABRT); **F4 inconclusive** (all six cargo-kani runs exit 1, no export). |
| 16:45Z | S1-06 | S1 (item 2) | same std `5be85699b8`; control `b25dd39a46` (decoder keeps records with missing locations; completeness still fail-closed) → sibling `a14a513eb7` on `uninit-ci/ch8-s1k-h` | 43889560779 | Full rich inventory for offline acceptance. |
| ~08:35Z | ISSUE-MRE-01 | Issues (item 1) | clean upstream `0aac16ef62`; control `d860e30592` (tree `ba4b7298f0`) → sibling `e6e2a06ccf` on `uninit-ci/ch8-issue-mre-a` | 43830763471 | Owner: publish issues after review. 10 invocations: valid-value copy (copy_integer, raw_bool_overwrite/read) + slice havoc (orig / initialized / thin targets / negative uninit read). Predeclared 5 SUCCESS, 3 COPY_UNSUPPORTED, 2 UNINIT_FAILURE. g0 `e609557732`. **Outcome:** valid-value confirmed (copy_integer: sole failure `copy_nonoverlapping::<u8>.unsupported_construct.1`; bool controls Unsupported) → #3762 comment draft. Slice havoc NOT reproduced: missing `-Z stubbing` (compile error) and upstream lacks uninit support for `[MaybeUninit<u8>;2]` → MRE v2. |
| ~08:55Z | ISSUE-MRE-02 | Issues (item 1) | clean upstream `0aac16ef62`; control `47616f4105` (tree `4700ee944e`) → sibling `66625d5267` on `uninit-ci/ch8-issue-mre2-a` | 43833191287 | Slice havoc v2: alloc-based buffer (no union), `-Z function-contracts -Z uninit-checks -Z stubbing`; 7 harnesses, predeclared 5 SUCCESS / 2 UNINIT_FAILURE. g0 `a0c7d25936`. Last item-1 dispatch. **Outcome:** all 7 match predictions: slice havoc on uninit output — sole failure `write_any_slice::<u8>.safety_check.1`; initialized / thin targets / bodies SUCCESS; negative read FAILURE as expected. Defect reproduced on clean upstream → issue draft `kani3300/issue-mre2/ISSUE-DRAFT.md`. |
C-01 dispatched (was held for the list fix; now batch, no global list).
C-01 held (superseded): C controls (std `d073585946` on P′, control `cdd3c6d041`, g0 `425f10fbfd`) use the same global `kani list` that timed out in S1-02 — dispatch after the list fix.

2026-11-16 | W0-F1 | kani#5183 opened (head bc8f8bb57e) on owner command; #5172 fixup 80e5d6fabc pushed + comment | charge 0
| 2026-11-16 ~18:10Z | S1-07 | S1 (item 2) | same std `5be85699b8`; control `9208b373c0` (snapshot finalization, location exception for 2 exact IDs, native metadata capture) → sibling `b37f6f75c5` on `uninit-ci/ch8-s1k-i` | 43923266772 | Closes binary-after identity gate; binding fields not exported by producer 0aac stay UNKNOWN. |
| 2026-11-17 ~13:55Z | S1-08 | S1 (item 2) | std `99e8456d20` (parent `5be85699b8`; role labels via `kani::assert` in positive smoke!/positive!, published as `experiment/ch8-s1-08-pprime-20261117`); reviewed control `7c41333f9b` (w14 delta APPROVE `e14db2d0dd`) → sibling `21592884db` (same tree `7ba8030690`, parent `9208b373c0`) on `uninit-ci/ch8-s1k-j`; GO request g0 `0e3cb41d9b`; owner policy 2026-11-17 | 44095954742 (attempt 1) | Distinct role labels for 111 success messages; U per-site, PFC source-reported (Profiles v4). One attempt, no auto-rerun. |
| 2026-11-17 ~16:45Z | S1-08 cell retry r1 | S1 (item 2) | std `99e8456d20` (unchanged, already published); reviewed control `e27ec119ee` (cell-u34 only, 2 roots, per-harness 1200 s; w14 APPROVE `86c0b15f2f`, package `6b51a4df02`) → sibling `4336dfed5a` (same tree `2c4475bf17`, parent `9208b373c0`) on `uninit-ci/ch8-s1k-k`; cause: `stable_default_cell` CBMC TIMEOUT at 600 s in 44095954742 (diag `929f21bb1f`), intake `6d300f3ab9` median timing ratio 1.009, cell 1.61 | 44128268928 (attempt 1) | Targeted retry of the only incomplete group; cross-run composition needs a separate decision. One attempt, no auto-rerun. |
| 2026-11-17 ~21:20Z | F4 confirm main | F4 (item 1, owner +2) | upstream main `faffcee3bc` (identical to main at dispatch); reviewed control `1ec3318f5e` (tests/script-based-pre/delayed-shared-body + workflow only; w14 APPROVE `8c37ad792e`, package `1bd7d58e6c`) → empty same-tree child `bbbe2d18d2` (tree `34a402bd4e`) on `f4-confirm-ci/main-20261118` | 44177926794 (attempt 1) | Shared-function delayed UB cache: singleton vs paired per-harness verdicts, 2 feature configs, uninit control. One attempt, no auto-rerun. |
| 2026-11-18 ~08:30Z | S2 batch3probes | S2 (item 2) | std `97ac4d39d7` (tree `2b305686df`, descends from S1-08 std `99e8456d20`; published as `experiment/ch8-s2-batch3probes-20261118`); stock Kani `0aac16ef62`; reviewed control `fc058c9733` (w14 APPROVE `0468ccf26c`, package `ae8f7b2feb`, GO request `13dc947ad2`) → sibling `056c7d2ae4` (same tree `829f2a6ce4`, parent `9e14e033f9`) on `uninit-ci/ch8-s2-batch3probes-20261118`; owner GO 2026-11-18 | 44264952389 (attempt 1) | One serial group `s2-batch3probes-u34`, 11 roots: merge32 with sorted halves, diagnostic sort13/general32 summaries, swap PFC, summary witness, 6 negative controls; cost measurement. No proof credit for assumed summaries. One attempt, no auto-rerun. **Outcome (coordinator read of bounded artifact `ch8-s2-batch3probes-44264952389-1`): compile FAILED at 23.6 s, 0 roots ran** — `error: stub verified target slice::sort::shared::smallsort::sort8_stable does not have a corresponding #[proof_for_contract] harness` at `sorting_s2_batch.rs:155` (`#[kani::stub_verified(sort8_stable)]`) under cfg `kani_smallsort_sorting kani_smallsort_controls kani_smallsort_s2_assumed`. Package defect; tool/source identities MATCH, peak RSS 1.35 GiB. **Owner 2026-11-18: not charged (0 roots ran).** |
| 2026-11-18 ~09:25Z | F4 fix full CI | F4 (item 1, owner +2) | upstream main `faffcee3bc` (no drift at dispatch); reviewed candidate `cab66681c9` (tree `8585336ed3`; w14 source review `cbfd888f27`, plan delta APPROVE `4d79ed98f4`, GO request `45726b201a`) → final PR head `b5a9678fd7` (same tree, parent `faffcee3bc`, no skip directive) on `fix/per-harness-global-transforms` | Kani CI 44274306776, Format 44274306711, Deny 44274306733 (attempt 1) | Push-triggered standard workflows (Kani CI incl. 5-OS regression, format, deny), as for F3/#5184. PR-only workflows (release, verify-std-check, bench-pr) run on the upstream PR itself; a fork PR against unsynced fork main would not test the reviewed tree. One attempt, no auto-rerun. **Outcome:** Format SUCCESS; Deny FAILURE — external advisory RUSTSEC-2026-0543 (chrono unmaintained), Cargo.lock identical to main; Kani CI: regression ubuntu-22.04/24.04/24.04-arm and macos-15-intel SUCCESS (script-based-pre 103/103 on ubuntu-24.04), documentation/benchcomp/llbc/perf SUCCESS, regression macos-15 CANCELLED (job not acquired by a hosted runner, 0 steps; owner: no re-run). |
| 2026-11-18 ~10:25Z | S2 batch3probes r1 | S2 (item 2) | std `9fd558c9da` (tree `64d96010b0`; +13 lines registering sort8 PFC under consumer cfg; published as `experiment/ch8-s2-batch3probes-r1-20261118`); stock Kani `0aac16ef62`; reviewed control `2ecf5e839f` (w13 package `0a4cef493f`, w14 APPROVE `e40ac8e8dd`, GO request `1ce52e417e`) → sibling `bdedeae662` (same tree `b04ce6fd7a`, parent `9e14e033f9`) on `uninit-ci/ch8-s2-batch3probes-r1-20261118`; owner GO 2026-11-18 | 44284869572 (attempt 1) | Same scope as r0 (11 roots, one serial group); cfg gate before tool build. One attempt, no auto-rerun. **Outcome: compile FAILED again at 27.6 s, 0 roots ran** (`Found 1 compilation errors`; cfg gate passed). The rustc diagnostic text fell into the omitted middle of the bounded stdout preview (preview_omitted_bytes 16235) and is not in the artifact or the job log: cause UNKNOWN from evidence. Peak RSS 1.85 GiB. **Not charged** (coordinator+planner 2026-11-18 under owner delegation; rule below). |
| 2026-11-18 ~11:35Z | F4 fix option A full CI | F4 (item 1, owner +1) | upstream main `faffcee3bc` (no drift); reviewed candidate `ca1452227d` (tree `baedd51d92`, parent `b5a9678fd7`; w15 package `a16ef717e1`, independent w11 APPROVE `516bf3aea7`, GO request `64b2cc9f48`) → final PR head `9b67828707` (same tree, parent `b5a9678fd7`, no skip directive; check_push_head PASS) on `fix/per-harness-global-transforms` (fast-forward) | Kani CI 44295027834, Format 44295027924, Deny 44295028060 (attempt 1) | Clone body transformer per harness only when the delayed UB pass is enabled (`-Z uninit-checks`); fixture checks both modes. Push-triggered Kani CI, format, deny. One attempt, no auto-rerun. **Outcome:** Format SUCCESS; Deny FAILURE (same external chrono advisory); Kani CI: regression ubuntu-22.04/24.04/24.04-arm and macos-15-intel SUCCESS (script-based-pre 103/103 on ubuntu-24.04), documentation/benchcomp/llbc/perf SUCCESS, regression macos-15 CANCELLED (not acquired by a hosted runner again; no re-run per owner). |
| 2026-11-18 ~12:20Z | S2 batch3probes r2 | S2 (item 2) | std `efb1aba7fc` (tree `4563e06722`, parent `97ac4d39d7`; r1 registration removed, both general32 sort8 stubs use the ordinary diagnostic model; published as `experiment/ch8-s2-batch3probes-r2-20261118`); stock Kani `0aac16ef62`; reviewed control `2ce62b5bb3` (w11 runner B-01/B-02 repairs; combined w14 APPROVE `a2d6428b35`, package `5a9e715ad9`, GO request `5c992a095b`) → sibling `59ff2f1d98` (same tree `dadbd71077`, parent `9e14e033f9`) on `uninit-ci/ch8-s2-batch3probes-r2-20261118`; GO coordinator+planner under owner delegation | 44302170220 (attempt 1) | Same 11-root scope and caps; full rustc diagnostics retained. One attempt, no auto-rerun. **Outcome: compile FAILED at 23.4 s, 0 roots ran; diagnostics complete:** `error: Failed to find contract closure __kani_recursion_check_swap_if_less in function core::slice::sort::shared::smallsort::swap_if_less` (only error). **Not charged** (confirmed compile failure before the first root). |
| 2026-11-18 ~13:10Z | S2 batch3probes r3 | S2 (item 2) | std `478dbf10d3` (tree `b5b25f4e59`, parent `97ac4d39d7`; uniform `crate::kani::*` contract stacks under S2 cfg for swap_if_less/insert_tail/insertion_sort_shift_left/sort4/merge; published as `experiment/ch8-s2-batch3probes-r3-20261118`); stock Kani `0aac16ef62`; reviewed control `dc1ad0f9ce` (w13 package `ba7286f5f7`, w14 APPROVE `379d32fcf6`, GO request `bcaf60f3e5`) → sibling `6d7f3c4b5b` (same tree `1c199ee220`, parent `9e14e033f9`) on `uninit-ci/ch8-s2-batch3probes-r3-20261118`; GO coordinator+planner under owner delegation | 44310254730 (attempt 1) | Same 11-root scope and caps; cause target: r2 `Failed to find contract closure __kani_recursion_check_swap_if_less`. One attempt, no auto-rerun. **Outcome: compile FAILED at 21.9 s, 0 roots ran, same single error** (`Failed to find contract closure __kani_recursion_check_swap_if_less`): uniform macro paths did not fix it; hypothesis falsified. **Not charged.** |
| 2026-11-18 ~14:50Z | S2 batch3probes r4-r1 | S2 (item 2) | std `bd62e54df1` (tree `dc2e7a7f25`, parent `97ac4d39d7`; no ordinary `kani::stub` of contracted functions; published as `experiment/ch8-s2-batch3probes-r4-20261118`); stock Kani `0aac16ef62`; control `0e8c836857` (w13 package `474e0b4209`; w14 review `e7837b0f70` CHANGES_REQUIRED with R14-01/02 closed, R14-03 gate-completeness deferred for this one run; GO request `6db728b62b`) → sibling `173ed30be4` (same tree `9f7c903f20`, parent `9e14e033f9`) on `uninit-ci/ch8-s2-batch3probes-r4-20261118`; GO coordinator+planner under owner delegation | 44328364855 (attempt 1) | Same 11-root scope and caps; cause target: ordinary stub body vs contract-closure lookup (r0–r3). One attempt, no auto-rerun. **Outcome: FAILED in step 4 `Validate control and synthetic wrapper` — `timeout-minutes: 1` exceeded (all observed self-tests ok; the grown cfg/lexical gate suite took ~70 s on the runner). Tool not built, source not compiled, 0 roots. Not charged (pre-build failure, 0 roots; coordinator, to confirm with planner).** |
| 2026-11-18 ~15:35Z | S2 batch3probes r4-r2 | S2 (item 2) | std `bd62e54df1` (unchanged from r4-r1, already published as `experiment/ch8-s2-batch3probes-r4-20261118`); stock Kani `0aac16ef62`; control `d33a0900da` (validate step 10 min, R14-03 gate fix integrated; w13 package `3cdec7455c`, w14 APPROVE `7c0a05d5bd`, GO request `3c52f8191d`) → sibling `6157554df8` (same tree `fe7c05829a`, parent `9e14e033f9`) on `uninit-ci/ch8-s2-batch3probes-r4r2-20261118`; GO coordinator+planner under owner delegation | 44336681406 (attempt 1) | Same 11-root scope and caps. One attempt, no auto-rerun. **Outcome: compile COMPLETE in 35.5 s (r0–r4 contract/stub failure fixed).** First root `general32_weak`: CBMC symex 488.5 s, 4.18M steps, 376,543 VCCs (155,645 after simplification), backend RSS reached the 12 GiB group cap → group interrupted at 569.7 s (`group_execution_interrupted_or_capped`); the other 10 roots did not run (UNKNOWN). **Charged** (a root executed). |
| 2026-11-18 ~19:05Z | S2 batch3probes r5-r1-stable | S2 (item 2) | std `bd62e54df1` (unchanged, published as `experiment/ch8-s2-batch3probes-r4-20261118`); stock Kani `0aac16ef62`; control `63535098ab` (9 isolated singleton roots, 6 GiB/720 s each, both general32 deferred; portable prefix seal; deterministic process test; Validate 12 min; w14 APPROVE `c9e0f9aefa`, GO request `e304910c33`) → sibling `33c687e43d` (same tree `20f53f18ea`, parent `9e14e033f9`) on `uninit-ci/ch8-s2-batch3probes-r5-20261118`; GO coordinator+planner under owner delegation | 44375519132 (attempt 1) | 9 roots / 16 covers / 5 negatives. One attempt, no auto-rerun. **Outcome (coordinator read, intake pending):** campaign STOPPED at 1372.9 s (`GlobalFailure: source_tool_request_binary_snapshot_drift_or_unavailable` during `merge_count_corrupt`, whose compile was interrupted). `swap_pfc` VERIFICATION SUCCESSFUL (verification 10.7 s, slot 45.8 s, 2.39 GiB). Negatives `checker_count_corrupt`, `checker_order_corrupt`, `sort13_weak` VERIFICATION FAILED as intended, but the failed check carries Kani's runtime-format placeholder message instead of the S2_NEG label, so `r5_expected_match=false` (labels need `kani::assert`, as in S1-08). `merge32_real` and `sort13_assumed` hit the 600 s child wall (2.4 GiB). `summary_witness`, `merge_order_corrupt` NOT_RUN; general32 pair deferred. Each compile ~29–31 s. **Charged** (roots executed). |
| 2026-11-18 ~19:35Z | Stub/contract confirm main | Finding (item 1, owner +1) | upstream main `faffcee3bc` (no drift); reviewed push-only control `e9f0e9a38b` (tree `76ffe2048b`, parent `faffcee3bc`, no skip; w15 package `5bb7ec9a01`, w11 APPROVE `615f027b4e`; check_push_head FINAL_HEAD_REQUEST_GATE_PASS, request `45b074506b`) pushed as-is on `stub-contract-confirm-ci/w15-push`; GO coordinator+planner under owner delegation | 44380273557 (attempt 1) | Ordinary `kani::stub` of a contracted function vs provider/verified controls; oracle DEFECT_PRESENT/ABSENT/INCONCLUSIVE. One attempt, no auto-rerun. **Outcome:** stock build SUCCESS (121 s). Controls `provider` and `verified_control` exit 0, VERIFICATION SUCCESSFUL, but the oracle marked them INCONCLUSIVE (`check counts` — pre-registered property counts did not match). `ordinary_stub` exit 1 with exactly `error: Failed to find contract closure __kani_recursion_check_f in function stub_contract_confirm::f` (only error); oracle labelled it ambiguous because the controls were not accepted. Overall classification INCONCLUSIVE; substantively the abort reproduces on stock main with the MRE (coordinator reading, intake pending). |
| 2026-11-18 ~20:10Z | #5159 merge main | PR maintenance (owner command) | merged upstream main `faffcee3bc` into `fix/volatile-zst-5072` (merge commit `78f745bb69`, no conflicts, PR diff unchanged: 6 files) to drop the retired macos-14 runner config | fork push runs Kani CI 44387663982, Deny 44387663841, Format 44387663939 (side effect) | Purpose: upstream PR CI (awaiting maintainer approval, `action_required`). Fork push runs are a side effect of updating the PR branch; not charged to item 1 (owner to object). |
| 2026-11-18 ~21:20Z | kani#4591 fix full CI | #4591 (item 1, owner +1) | upstream main `969f464898` (no drift at launch); reviewed candidate `3a770b5db5` (tree `7a3d5c05b5`; w15 package `ad50aaeaab`, w11 APPROVE `0f4e2830d9`, GO request `1a32f0ad57`) → final PR head `6fca00af80` (same tree, parent `969f464898`, no skip; check_push_head MATCH) on `fix/stub-contracted-function`; GO coordinator+planner under owner delegation | Kani CI 44399789701, Format 44399789719, Deny 44399789794 (attempt 1) | Ordinary `kani::stub` of a contracted function: skip the target's contract instrumentation in the replaced body; regression tests for ensures/requires/both, PFC/stub_verified controls, overlap. Push-triggered Kani CI, format, deny. One attempt, no auto-rerun. **Outcome:** Format SUCCESS, Deny SUCCESS (chrono advisory gone on main 969f). Kani CI: documentation/perf/benchcomp/llbc SUCCESS; regression (ubuntu-24.04) FAILED in the first compiletest suite `kani` (658 passed, 1 failed): new test `tests/kani/FunctionContracts/ordinary_stub.rs`, harness `replacement_contract_target` — `Only a single top-level call to function contracted_replacement…{closure} when checking contract` (line 146); all other harnesses in that file verified. Later suites (expected, script-based-pre, ui) did not run; other regression matrix jobs cancelled by fail-fast; macos-15 no runner. Item 1 budget now exhausted. |
| 2026-11-18 ~21:55Z | S3-1 actual leaves | S3 (item 2) | std `513341f41c` (tree `a818efb215`, parent `97ac4d39d7`; published as `experiment/ch8-s3-1-20261119`); stock Kani `0aac16ef62`; control `fc29b93b1e` (snapshot fail-closed + receipt provenance repairs; w14 APPROVE `27040e2cd8`, GO request `99291133b2`) → sibling `d92581141b` (same tree `c0368fa64a`, parent `9e14e033f9`) on `uninit-ci/ch8-s3-1-20261119`; GO coordinator+planner under owner delegation | 44405927807 (attempt 1) | 9 serial singleton roots: checker_order_corrupt, checker_count_corrupt, swap_geometry, sort4_separate, sort4_same_alloc, insert_tail_rel16, merge8_separate, merge8_same_alloc, sort13_weak (6 actual PFC candidates + 3 labelled negatives). One attempt, no auto-rerun. **Outcome:** campaign STOPPED after 41.2 s of the root phase: `GlobalFailure: worker protected/provenance evidence rejected: recorded worker binary drift: before` on the first root (`checker_order_corrupt` INTERRUPTED); the other 8 roots NOT_RUN; no verification result. The new fail-closed snapshot gate fired on the worker's BEFORE binary snapshot (likely a false positive of the gate itself; intake pending). **Not charged** (controller failure before any root completed; coordinator+planner to confirm). |
| 2026-11-18 ~23:00Z | S3-1-r2 actual leaves | S3 (item 2) | std `513341f41c` (unchanged, already published as `experiment/ch8-s3-1-20261119`); stock Kani `0aac16ef62`; control `cb63033ffc` (canonical paths in the binary snapshot guard; w13 package `008fcb7705`, w14 APPROVE `12c4dc5502`, GO request `c59d410e99`) → sibling `7497ecdb39` (same tree `287ebfc7b0`, parent `9e14e033f9`) on `uninit-ci/ch8-s3-1-r2-20261119`; GO coordinator+planner under owner delegation | 44416629057 (attempt 1) | Same 9 serial singleton roots as S3-1. One attempt, no auto-rerun. **Outcome (coordinator read, intake pending):** campaign SELECTED_PARTIAL, 1454 s, no global stop. Negatives FAILED with their own labels: `checker_order_corrupt` (S2_NEG_CHECKER_ORDER), `checker_count_corrupt` (S2_NEG_CHECKER_COUNT), `sort13_weak` (S2_NEG_SORT13_WEAK). VERIFICATION SUCCESSFUL: `s3_swap_u8_geometry` 27.3 s, `s3_sort4_u8_separate` 79.0 s, `s3_merge8_u8_separate` 151.0 s; `s3_sort4_u8_same_alloc` 212.2 s but receipt UNKNOWN (`rich metadata incomplete: file/line missing`). `s3_insert_tail_u8_rel16` and `s3_merge8_u8_same_alloc` interrupted or capped. **Charged** (roots executed). Qualification pending intake. |
| 2026-11-19 ~01:50Z | S3-2-r1 capped leaves | S3 (item 2) | std `1b4a904f81` (tree `ac51d04e17`, parent `97ac4d39d7`; published as `experiment/ch8-s3-2-r1-20261119`); stock Kani `0aac16ef62`; control `775574eb2f` (eight-row profile, partial-MU rows diagnostic with initialization OPEN; w13 package `792ca31fa8`, w14 APPROVE `b5a0878d35`, GO request `1c9272aaa8`) → sibling `474a9d1617` (same tree `ef1cf70982`, parent `9e14e033f9`) on `uninit-ci/ch8-s3-2-r1-20261119`; GO coordinator+planner under owner delegation | 44439462279 (attempt 1) | 8 rows incl. insert_tail/merge8 same-alloc alternatives. One attempt, no auto-rerun. **Outcome (coordinator read, intake pending):** SELECTED_PARTIAL, 1068.8 s, no global stop. Negatives FAILED with own labels (checker_order, checker_count, sort13_weak). `m8_s32_d00_allinit` 197.4 s, `m8_s32_d00_partial_diag` 195.1 s, `m8_s40_d16_partial_diag` 198.9 s VERIFICATION SUCCESSFUL, receipts UNKNOWN (`rich metadata incomplete: file/line missing`, same lib.rs:0:0 pattern as sort4same). `i_p01_b1_16`, `i_p16_b1_16` (insert_tail) interrupted or capped. **Charged.** |
| 2026-11-19 ~04:50Z | S3-3/S4 bridge-1-r1 | S3/S4 (item 2) | std `f1bdf11902` (tree `f7856aae7a`, parent `97ac4d39d7`; published as `experiment/ch8-s3s4-bridge-1-20261119`); stock Kani `0aac16ef62`; control `d675ef70dc` (count repair; w13 package `9c4ce67e06`, w14 APPROVE `24872d1553`, GO request `ffe4f1b88a`) → sibling `c2bbdb972c` (same tree `6280a305cb`, parent `9e14e033f9`) on `uninit-ci/ch8-s3s4-bridge-1-20261119`; GO coordinator+planner under owner delegation | 44460583125 (attempt 1) | Combined: insert_tail fixed-base p1 at 6 GiB + first S4 candidates (7 selected rows). One attempt, no auto-rerun. **Outcome (coordinator read, intake pending):** SELECTED_PARTIAL, 1672 s, no global stop. Negatives FAILED with own labels. `i_p01_b01_fullu8` (insert_tail fixed base) VERIFICATION SUCCESSFUL 51.9 s; `sort9_v34_b01_len09_real` VERIFICATION SUCCESSFUL 223.2 s. `fallback_cell_b01_n00_16` and `network_u8_b01_n00_08` interrupted or capped. Counted. |
| 2026-11-19 ~04:55Z | kani#4591 fix full CI r3 | #4591 (item 1, owner +1 2026-11-19) | PR branch head `031fc085cd` (no skip; tree `2ff34bc99e`, parent `6fca00af80` = previous head; reviewed candidate `f82934ca97`, w11 APPROVE `19079d1315`, GO request `issue4591-singlecall-go-r3`; check_push_head errors=[]) fast-forward on `fix/stub-contracted-function`; base main `969f464898`; upstream main now `c25a57bcbf` (drift in 30 files, none overlapping, merge-tree clean) | Kani CI 44461123962, Format 44461124056, Deny 44461124017 (attempt 1) | Fixture repair: single-call PFC callers for ordinary replacements. Push-triggered Kani CI, format, deny. **Outcome:** Format SUCCESS, Deny SUCCESS. Kani CI: regression on all five OSes (ubuntu-22.04/24.04/24.04-arm, macos-15, macos-15-intel), documentation, benchcomp, LLBC SUCCESS. `perf` FAILED: the runner received a shutdown signal during `perf/s2n-quic/quic/s2n-quic-core` (`##[error]The runner has received a shutdown signal`); infrastructure, not a test result. perf passed on the previous head `6fca00af80` (run 44399789701) with the same compiler change; r3 changed only tests. |
| 2026-11-19 ~07:45Z | S4P1-r1 | S4 (item 2) | std `985062ebad` (tree `c937101b30`, parent `97ac4d39d7`; published as `experiment/ch8-s4p-1-20261119`); stock Kani `0aac16ef62`; control `2db5d2c088` (w13 repair `5b0ed64d86`, w14 APPROVE `eff6c707a3`, GO request `1f9f9d9995`) → sibling `563a899dce` (same tree `96b03b52cd`, parent `9e14e033f9`) on `uninit-ci/ch8-s4p-1-r1-20261119`; GO coordinator+planner | 44481580554 (attempt 1) | 8 roots: fallback/network length blocks 0..2 / 3..4 plus controls; no summaries. Counted (tracking only). **Outcome (coordinator read, intake pending):** SELECTED_PARTIAL, 1780 s, no global stop. Negatives FAILED with own labels incl. new S4_NEG_CELL_COUNT. `s4p_fallback_b01_n00_02_fullbyte` 140.7 s and `s4p_fallback_b01_n03_04_fullbyte` 144.6 s VERIFICATION SUCCESSFUL, receipts UNKNOWN (lib.rs:0:0 metadata). `s4p_network_b01_n00_02_fullbyte`, `s4p_network_b01_n03_04_fullbyte` interrupted or capped. |
| 2026-11-19 ~10:25Z | S4P2 network | S4 (item 2) | std `c12867b1e6` (tree `47cca4ee59`, parent `97ac4d39d7`; published as `experiment/ch8-s4p-2-20261119`); stock Kani `0aac16ef62`; control `4059c900e5` (w13 package `90d861e59f`, w14 APPROVE `8a0083897b`, GO request `9123b93890`) → sibling `9c63491609` (same tree `48c726afdc`, parent `9e14e033f9`) on `uninit-ci/ch8-s4p-2-20261119`; GO coordinator+planner | 44505531344 (attempt 1) | Network sort full-u8 partitions {0,1},{2},{3},{4} + 4 negative controls. Counted (tracking only). **Outcome (coordinator read, intake pending):** SELECTED_PARTIAL, 2536 s, no global stop. 4 negatives FAILED with own labels. All four network partitions ({0,1}, {2}, {3}, {4}) interrupted or capped — cost does not shrink with length, so the bottleneck is the harness/model overhead rather than N. |
| 2026-11-19 ~11:40Z | kani#4591 fix full CI r4 | #4591 (item 1) | PR branch head `b3019ab3f9` (no skip; tree `b05ea48016`, parent `031fc085cd`; tests reduced 38→7 harnesses after owner-requested slop review; w15 package `2a11df42b9`, w11 APPROVE `2b733341d6`, GO request `be748cef7b`; check_push_head MATCH) fast-forward on `fix/stub-contracted-function`; upstream main `c25a57bcbf` (no overlap) | Kani CI 44516395307, Format 44516395718, Deny 44516395278 (attempt 1) | Push-triggered Kani CI, format, deny. Counted (tracking only). **Attempt 1 outcome:** regression on all 5 OSes, docs, LLBC, benchcomp, Format, Deny SUCCESS; perf FAILURE (`hosted runner lost communication`, 80 min, s2n-quic). **Attempt 2:** rerun-failed-jobs (perf only), GO `ca0f669dfa`, counted. **Attempt 2 outcome:** perf FAILURE again (`hosted runner lost communication`, 13:03→14:18Z). Attribution: r2→r4 diff touches only `tests/kani` and `tests/expected`; perf runs only `tests/perf`, so r4 perf inputs equal r2 (`6fca00af80`, perf SUCCESS). Fork perf fails the same way on unrelated branches (6 of 13 attempts 2026-11-16..19, all ~72–80 min: autoharness-uninit-reset, delayed-ub-recursion, kani-uninit-unresolved-call-v3); upstream perf 8/8 SUCCESS in the same window. Treated as fork-runner flake; no further perf reruns. |
| 2026-11-19 ~14:58Z | S4P2-r2 network concrete calls | S4 (item 2) | std `8faf8e62af` (tree `91f097cdb4`, parent `c12867b1e6`; published as `experiment/ch8-s4p-2-r2-20261119`, remote head/tree/parent verified); stock Kani `0aac16ef62`; control `3d3fb71527` (w13 plan `cdedf547df`, w11 plan APPROVE `2b7872e84c`; w13 package `d10b721e5f`, w11 exact-package APPROVE `0c2784fabe`; root final Validate 366 PASS 685.015 s margin 1.5766; GO request `fef8170d86`) → sibling `d88fac48cf` (same tree `628a9aa91c`, parent `4059c900e5`, no skip; check_future_trigger MATCH) on `uninit-ci/ch8-s4p-2-r2-20261119`; GO coordinator+planner | 44548842328 (attempt 1; push, ch8-s2.yml, head `d88fac48cf`) | Network sort with concrete call lengths: N2/N3/N4 literal slices, N01 bool with both literal calls; 4 unchanged negatives first; unwind 36 positives; caps unchanged (child 600 incl compile 180, slot 720, campaign 6900). Counted (tracking only). One attempt, no auto-retry. **Outcome (coordinator read of group-evidence, intake pending):** job failure 14:54→15:09Z, campaign 359 s, state SELECTED_PARTIAL, no stop. All four positives VERIFICATION SUCCESSFUL: N0..1 33.4 s (211/227 SUCCESS, 16 UNREACHABLE), N2 3.1 s, N3 3.8 s, N4 4.7 s (241/252, 11 UNREACHABLE each); peak RSS ≤2.6 GiB. 4 negatives FAILED with own labels. s3_expected_match False on every row (ZERO_U/REJECT_ALL: UNREACHABLE checks present); admission needs per-site S1 arguments. Network cost hypothesis confirmed: 600 s timeouts → seconds. |
| 2026-11-19 ~16:55Z | kani#5195 cleanup full CI | open-PR cleanup (item 1) | PR head `9b67828707` + cleanup `153be639a0` (tree `7f784cca53`; w11 package `9510aaf3ca`, w15 APPROVE `eb342ddebf`; owner chose cleanup order 2026-11-19) pushed as NEW fork branch `cleanup/pr5195-20261119` (not the PR branch); GO coordinator+planner | Kani CI 44570271305, Format 44570271286, Deny 44570271333 (attempt 1) | Test-only cleanup: 14→8 driver invocations, label renames, compiler byte-identical. Push-triggered Kani CI + Format. Counted (tracking only). No rerun. **Outcome:** regression ubuntu-22.04/24.04/24.04-arm and macos-15-intel, docs, LLBC, benchcomp, format, Clippy SUCCESS; macos-15 not acquired; perf runner shutdown signal (infra; perf passed on PR head 44295027834); Deny FAILURE on chrono RUSTSEC-2026-0543 (old base, fixed on main). |
| 2026-11-19 ~17:00Z | kani#5176 cleanup full CI | open-PR cleanup (item 1) | PR head `3d9a180938` + cleanup `06e1533360` (w13 package `64ed31eaa4`, w14 APPROVE `a522e9fa61`; planner GO `d27c166e7f`) pushed as NEW fork branch `cleanup/pr5176-20261119` (not the PR branch); GO coordinator+planner | Kani CI 44571603075, Format 44571603023, Deny 44571602925 (attempt 1) | Test-only cleanup: 14 cases kept, edge fixtures merged into main, typ.rs byte-identical. Push-triggered Kani CI + Format + Deny. Counted (tracking only). No rerun. **Outcome:** Linux regression ×3, docs, LLBC, benchcomp, format SUCCESS; macos-15-intel FAILURE only in unrelated `script-based-pre/cargo_autoharness_multichareq_searcher` (same on #5172 cleanup); macos-15 not acquired; perf FAILURE; Deny chrono. Cleanup deferred: maintainer merged main into PR 2026-11-19, owner: no changes. |
| 2026-11-19 ~17:00Z | kani#5172 cleanup full CI | open-PR cleanup (item 1) | PR head `80e5d6fabc` + cleanup `fef46d2d9d` (w11 package `f38425fbc1`, w13 APPROVE `2a5d5af750`; planner GO `d27c166e7f`) pushed as NEW fork branch `cleanup/pr5172-20261119` (not the PR branch); GO coordinator+planner | Kani CI 44571610404, Format 44571610523, Deny 44571610409 (attempt 1) | Cleanup: 24 harnesses kept, shared auxiliary helpers, merged expected files, compiler comment-only fix. Push-triggered Kani CI + Format + Deny. Counted (tracking only). No rerun. **Outcome:** all Linux regression, macos-15, docs, LLBC, benchcomp, perf, format SUCCESS; macos-15-intel FAILURE only in unrelated `script-based-pre/cargo_autoharness_multichareq_searcher`; Deny chrono. Cleanup deferred (maintainer merged main; owner: no cleanup changes). |
| 2026-11-19 ~17:05Z | kani#5159 cleanup full CI | open-PR cleanup (item 1) | PR head `78f745bb69` + cleanup `282d007d06` (tree `7a71034212`; w13 package `88948daa1d`, w14 APPROVE `b26412da5c`; planner GO `83d652f93d`) pushed as NEW fork branch `cleanup/pr5159-20261119` (not the PR branch); GO coordinator+planner | Kani CI 44572313224, Format 44572313357, Deny 44572313459 (attempt 1) | Test-only cleanup: stronger expected for unaligned/uninhabited negatives, comment trims; 8 harnesses and compiler fix byte-identical. Push-triggered Kani CI + Format + Deny. Counted (tracking only). No rerun. **Outcome:** all regression incl. macos-15-intel, docs, LLBC, benchcomp, perf, format SUCCESS; macos-15 not acquired; Deny chrono. Cleanup deferred (maintainer merged main; owner: no changes). |
| 2026-11-19 ~17:10Z | kani#5183 cleanup full CI | open-PR cleanup (item 1) | PR head `19a42e1a21` + cleanup `d1f1bca80e` (tree `436debfa7b`; w11 package `a394355e96`, w14 APPROVE `7c07bd0346`; planner GO `79aef134f7`) pushed as NEW fork branch `cleanup/pr5183-20261119` (not the PR branch); GO coordinator+planner | Kani CI 44574132948, Format 44574132963, Deny 44574133198 (attempt 1) | Test-only cleanup: two named automatic-target banners in expected; compiler/body/shell byte-identical. Push-triggered Kani CI + Format + Deny. Counted (tracking only). No rerun. |
| 2026-11-19 ~17:30Z | S4P3 network N8/N9/N13/N17 | S4 (item 2) | std `7b31b060b9` (tree `fccf3284bd`, parent `8faf8e62af`; published as `experiment/ch8-s4p-3-20261119`, remote head/tree/parent verified); stock Kani `0aac16ef62`; control `65a9ea656a` (w13 plan `c0de847180`, w14 plan APPROVE `762a2a678e`; w15 package `f485968493`, w11 exact-package APPROVE `507dbcfd52`; root final Validate 389 PASS 701.37 s margin 1.54; GO `7d7e814de5`) → sibling `960cc68609` (same tree `09938d27a1`, parent `3d3fb71527`, no skip; check_future_trigger MATCH) on `uninit-ci/ch8-s4p-3-20261119`; GO coordinator+planner | 44577116178 (attempt 1; push, ch8-s2.yml, head `960cc68609`) | Network concrete-call roots N8, N9, N13, N17 (N17 still merge-free) + 4 unchanged negatives; caps unchanged. Counted (tracking only). One attempt, no auto-retry. **Outcome (coordinator read of group-evidence, intake pending):** job failure 17:27→18:09Z, campaign 1723 s, SELECTED_PARTIAL, no stop. N8 VERIFICATION SUCCESSFUL 109.3 s, N9 SUCCESSFUL 207.1 s; N13 and N17 UNKNOWN (group_execution_interrupted_or_capped, 600 s). 4 negatives FAILED with own labels. Admission of N8/N9 needs intake + per-site S1 arguments. |
| 2026-11-19 ~19:10Z | kani#5206 fix full CI | follow-up to #5204 (item 1) | squash `e17417b570` (tree `798c53188f`, parent upstream main `0997d11c14`; w13 fix `e586239678` + w11 revision `a5ebb0bf8a`; w15 reviews `1740ff1d50`, `b9a7905ffa` APPROVE; planner GO `5c9d9e2e28`) pushed as NEW fork branch `fix/stub-contract-target-conflict` (future PR head; no PR yet); GO coordinator+planner | Kani CI 44594824154, Format 44594824149, Deny 44594824179 (attempt 1) | Reject ordinary stub of a proof_for_contract / stub_verified target with a diagnostic. Push-triggered Kani CI + Format + Deny. Counted (tracking only). No rerun. **Outcome:** regression ubuntu-24.04 and llbc FAILED on the rustfmt check in the test scripts (`stubbing/mod.rs:52` for-loop layout); other regressions cancelled by fail-fast; docs, perf, benchcomp, Format workflow, Deny SUCCESS. Fixed by exact rustfmt diff → `a65ffdbdcc`. |
| 2026-11-19 ~19:10Z | kani#5172 copilot/toolchain fix full CI | open PR (item 1) | `cea872ac97` (tree `b8292f0333`, parent = maintainer merge `ac0304a8bf` = PR head; w15 fix, w13 APPROVE `0a52785cc0`; planner GO `5e59d01caf`) pushed as NEW fork branch `fix/pr5172-copilot-20261119` (not the PR branch); GO coordinator+planner | Kani CI 44594829817, Format 44594829848 (attempt 1; Cargo Deny not triggered by this push) | `*args` for nightly-2026-11-18 FieldDef::ty, visited-type set (Copilot high), reuse checked body in resolve_call (Copilot medium). Push-triggered Kani CI + Format + Deny. Counted (tracking only). No rerun. |
| 2026-11-20 ~00:15Z | kani#5206 fix full CI v2 | follow-up to #5204 (item 1) | `a65ffdbdcc` (tree `3b62ab0119`, parent upstream main `0997d11c14`) = reviewed `e17417b570` + exact rustfmt hunk from CI log; planner GO `b4b6a33d8a` (no new worker review needed) → NEW fork branch `fix/stub-contract-target-conflict-v2` (future PR head); GO coordinator+planner | Kani CI 44616139446 (attempts 1–2), Format 44616139604, Deny 44616139673 | Push-triggered Kani CI + Format + Deny. Counted (tracking only). **Attempt 1:** rustfmt OK; docs, perf, llbc, benchcomp, Format, Clippy, Deny SUCCESS; regression ubuntu-22.04 FAILED only in `script-based-pre/codegen_cache` ('no cache statistics were printed', kani exit 0, cause UNKNOWN; same test passed on the same main base in #5172 run 44594829817); 4 regressions cancelled by fail-fast. **Attempt 2:** `--failed` rerun of those five jobs, planner GO `8249e329aa`; counted; no third run. |
| 2026-11-20 ~00:30Z | kani#5172 comment cleanup full CI | open PR (item 1) | `be926954f` (tree `d49c05df79`, parent `cea872ac97`; comment-only, texts from w11 slop review r2 `16b5608bf9`, applied by w13 `1b1785e15a`; owner approved all three proposals; planner GO) fast-forward on fork branch `fix/pr5172-copilot-20261119` (not the PR branch); GO coordinator+planner | Kani CI 44618255171, Format 44618255117, Deny 44618255221 (attempt 1) | Comment/doc edits only incl. factual fix of the union return-state comment. Push-triggered Kani CI + Format + Deny. Counted (tracking only). No rerun. **Outcome:** regression ubuntu-22.04/24.04/24.04-arm and macos-15-intel, docs, LLBC, benchcomp, Format, Clippy, Deny SUCCESS; perf runner lost communication; macos-15 no runner. |
| 2026-11-20 ~01:55Z | kani#5159 follow-up full CI | follow-up to merged #5159 (item 1) | `73edbdd8ae` (single commit on main `fca73e1318`; port of reviewed `a197a690e4`, w13 APPROVE; planner GO `e58a813481`) → NEW fork branch `fix/volatile-zst-test-followup-main` (future PR head); GO coordinator+planner | Kani CI 44632134521, Format 44632134508, Deny 44632134531 (attempt 1) | Local unit in read_volatile_unit_reference (maintainer nit), helper + shared message constant. Push-triggered Kani CI + Format + Deny. Counted (tracking only). No rerun. **Outcome:** regression ubuntu-24.04 and llbc FAILED on the scripts' rustfmt check (`intrinsic.rs:92` match arm layout); Format/Clippy, Deny, docs, benchcomp SUCCESS; other regressions cancelled. Fixed by exact rustfmt diff → `19f7c1af19`. |
| 2026-11-20 ~02:00Z | kani#5172 merged-head fix full CI | open PR (item 1) | merge `7e53bc6539` (tree `46f343ba30`; parents `be926954f` + new PR head `d91aeeea94`; no conflicts; w15 `843ce7ccc5`; planner GO `e1f093d120`) fast-forward on fork branch `fix/pr5172-copilot-20261119` (not the PR branch); GO coordinator+planner | Kani CI 44633285784, Format 44633285808, Deny 44633285668 (attempt 1) | Same reviewed fix on top of the maintainer's second main merge (nightly-2026-11-19). Push-triggered Kani CI + Format + Deny. Counted (tracking only). No rerun. **Outcome:** regression ubuntu-24.04, perf, docs, LLBC, benchcomp, Format, Clippy, Deny SUCCESS; regression ubuntu-24.04-arm FAILED only in `script-based-pre/codegen_cache` (known upstream flake: also failed in upstream merge-queue runs 44590803353 for #5201 and 44605372437 for #5045); ubuntu-22.04 and macos-15-intel cancelled by fail-fast; macos-15 no runner. |
| 2026-11-20 ~03:00Z | kani#5159 follow-up full CI v2 | follow-up to merged #5159 (item 1) | `19f7c1af19` (single commit on main `fca73e1318`) = `73edbdd8ae` + exact rustfmt hunk; planner GO `d4c0727a53` → NEW fork branch `fix/volatile-zst-test-followup-main-v2` (future PR head); GO coordinator+planner | Kani CI 44641742091, Format 44641742096, Deny 44641742154 (attempt 1) | Push-triggered Kani CI + Format + Deny. Counted (tracking only). No rerun. **Outcome:** all 12 SUCCESS (5 regression OS incl. macos-15, docs, perf, LLBC, benchcomp, Format, Clippy, Deny). |
| 2026-11-20 ~08:10Z | kani#5172 re-merge main full CI | open PR (item 1) | merge `88fec3b397` (parents `7e53bc6539` + main `0601bc57f0`; one conflict in `points_to_analysis.rs` after #5184: kept main's recursive-call check, then our body guard; dropped unused `DUMMY_SP` import) on NEW fork branch `fix/pr5172-merge-main-20261120` (not the PR branch); owner command 2026-11-20 "мерж main в 5172 и CI в форке"; conflict-resolution review pending in parallel | Kani CI 44756041900, Format 44756041884, Deny 44756041870 (attempt 1) | Attempt 1: Format, Deny SUCCESS; Kani CI FAILURE only in regression (macos-15-intel): `script-based-pre/verify_std_cmd` timed out at 2400 s (suite 2646 s vs 1045–1359 s in earlier fork runs and 1198 s upstream). Unrelated to the change: `UninitPass`/`DelayedUbPass` run only with `-Z uninit-checks`, which `verify_std.sh` does not pass. All other 8 jobs SUCCESS. Conflict review w14 `dd3d5a5ef2` APPROVE. |
| 2026-11-20 ~17:00Z | kani#5172 re-merge CI: rerun failed job | open PR (item 1) | same head `88fec3b397`; rerun of regression (macos-15-intel) only, flake attribution; GO coordinator, planner informed | Kani CI 44756041900 attempt 2 | Success: all 9 Kani CI jobs green incl. macos-15-intel and macos-15; verify_std_cmd timeout on attempt 1 was a runner-speed flake |
| 2026-11-21 ~03:30Z | item 2 q-pilot campaign 1 (research lane) | item 2 | std 5544e01921, control tree 3cead694 (sibling of 876a75ca9f), tool 0aac16ef; 7 roots P-1…P-5c; GO coordinator under owner autonomy 2026-11-21, planner agreed; delta-review residual risk accepted (PILOT-GO.md) | ch8-q-pilot.yml 44834533774: workflow file issue, no jobs (charged 0); retry trigger 0bf2794faa (runner paths fix) — run 44834820115 | Completed 23:36Z: P-1 SUCCESS, P-5a designated FAILURE, P-5b SUCCESS (expected); P-2/P-4/P-5c RSS cap 6 GiB, P-3 timeout 600 s; see item2-audit-response-20261120/run-44834820115/SUMMARY.md |
| 2026-11-21 ~05:00Z | item 2 q-pilot campaign 2 (research lane, packed u32 threshold masks) | item 2 | std 0e9b28b293, control tree 1c7d61e3 (trigger 86d670c170), tool 0aac16ef; same 7 roots/caps as campaign 1; review PILOT2-REVIEW.md GO_FOR_DISPATCH; GO coordinator | ch8-q-pilot.yml 44840444710 | Completed: P-1, P-3 (VT 447 s), P-4 (N17 consumer, VT 100 s) SUCCESS; P-5a/P-5c designated FAILURE; P-5b SUCCESS; P-2 RSS cap 6 GiB at 88 s; see run-44840444710/SUMMARY.md |
| 2026-11-21 ~06:30Z | item 2 q-pilot campaign 3 (P-2 only, local RSS cap 9 GiB) | item 2 | std 0e9b28b293 (unchanged), control b716a7f821 tree df067af9 (trigger 31450d1720), tool 0aac16ef; coordinator review of control-only delta (roster+cap, tests 12/12); GO coordinator per PILOT-RUN2-ANALYSIS | ch8-q-pilot.yml 44844623193 | Completed: P-2 RSS cap 9 GiB at 98 s, before first CNF (SSA conversion); see run-44844623193/SUMMARY.md |
| 2026-11-21 ~07:30Z | item 2 q-pilot campaign 4 (P-2b: sort13 PFC with actual swaps, cap 6 GiB) | item 2 | std c59b0d2a21 (+1 harness), control 9fb54361f5 (trigger 403f3bde46), tool 0aac16ef; coordinator review of +28-line harness and roster/cap delta; GO coordinator per PILOT-RUN2-ANALYSIS fallback | ch8-q-pilot.yml 44846171602 | Completed: P-2b RSS cap 6 GiB at 66 s, before first CNF; 211k steps, 937 VCC; see run-44846171602/SUMMARY.md |
| 2026-11-21 ~09:00Z | item 2 q-pilot campaign 5 (P-2 measurement pack: P-2b-OB11, D13-BODY-V34, D13-CHECK-V19/P17/P31) | item 2 | std c8b703918a, control d453bb80a5 (trigger 6fe0fed608), tool 0aac16ef; coordinator review (prefix pairs = first 17/31 sort13 call sites, tests OK); GO coordinator per PILOT-RUN4-ANALYSIS | ch8-q-pilot.yml 44849901344 | Completed: P-2b-OB11 timeout 600 s (CNF 25.4M clauses, 5.45 GiB); D13-BODY timeout 180 s (0.94M clauses); V19/P31 RSS cap; P17 timeout 180 s (18.8M); see run-44849901344/SUMMARY.md |
| 2026-11-21 ~11:00Z | item 2 q-pilot campaign 6 (refine-arrays A/B: P17 base/refine, P-2b/P-2 on 11 bits with refine) | item 2 | std c8b703918a (unchanged), control 87c9919ffa (trigger e0ad63e26c), tool 0aac16ef; layers deferred (would refactor runtime sort13); planner concurred (PILOT6-PLANNER-NOTE.md); GO coordinator | ch8-q-pilot.yml 44853799226 | Completed: refine-arrays no effect (same CNF); P17 timeouts, P-2b-OB11 timeout 600 s, P-2-OB11 RSS cap; see run-44853799226/SUMMARY.md |
| 2026-11-21 ~12:30Z | item 2 q-pilot campaign 7 (plain composition: q13 with stub swap; N17 with stub swap+insert; corrupt control) | item 2 | std 1b82e2a9a7 (+3 harnesses), control bc7fb06c39 (trigger cd6c5d7372), tool 0aac16ef; planner soundness note PILOT7-PLANNER-NOTE.md; GO coordinator | ch8-q-pilot.yml 44856804576 | Completed: Q13 plain SUCCESS (VT 80 s); N17 plain and corrupt control RSS cap 6 GiB in solver stage (7.0M/6.6M clauses); see run-44856804576/SUMMARY.md |
| 2026-11-21 ~13:30Z | item 2 q-pilot campaign 8 (N17 plain composition + corrupt control, local cap 10 GiB) | item 2 | std 1b82e2a9a7 (unchanged), control f839997417 (trigger 82d9f85bc7), tool 0aac16ef; coordinator review (roster/cap only); GO coordinator | ch8-q-pilot.yml 44858566553 | Completed: N17 plain SUCCESS (VT 244 s, 9.04 GiB, 0/946, 6/6 covers); corrupt control FAILURE exactly N17_CORRUPT_QPOST; see run-44858566553/SUMMARY.md |
| 2026-11-21 ~15:30Z | item 2 q-pilot campaign 9 (matched qualification pack P-1/P-3/N17+controls; no-merge grid N0/1,2,8,9,12,13,16 + controls; 15 roots, cap 10 GiB) | item 2 | std d968b9a8c3 (+harnesses, runtime unchanged), control baad011375 (trigger d872e81f2f), tool 0aac16ef; planner task PILOT9-IMPL-TASK.md + QUALIFICATION-CHECKLIST.md; coordinator review; GO coordinator | ch8-q-pilot.yml 44862241314 | Completed: 14/15 expected outcomes (P-1, P-3, N17, N2/8/9/12/13/16 SUCCESS; 5 controls as designed); N01 timeout 300 s; see run-44862241314/SUMMARY.md |
| 2026-11-21 (MSK ~07:40) | item 2 q-pilot campaign 10 (remaining no-merge network N0, N1, N3–7, N10, N11, N14, N15 + 2 controls; 13 roots, cap 10 GiB) | item 2 | std 632e4e8d3b (+harnesses only), control 6f5009f3be (trigger db700c6c0b), tool 0aac16ef; planner task PILOT10-IMPL-TASK.md; coordinator review; GO coordinator | ch8-q-pilot.yml 44867764794 | Completed: 13/13 expected (N0, N1, N3–7, N10, N11, N14, N15 SUCCESS; 2 controls designated FAILURE); see run-44867764794/SUMMARY.md |
| 2026-11-21 (MSK ~10:00) | item 2 q-pilot campaign 11 (merge package A: swap byte+q PFC, right insert b10, merge_up/down PFC, half probes, 2 controls; 9 roots, cap 10 GiB) | item 2 | std 2dc2afe895 (verification attrs/modules only; runtime equal modulo cfg_attr, coordinator-checked), control e18c9d5489 (trigger 4bd023abd7), tool 0aac16ef; planner task PILOT11-IMPL-TASK.md; GO coordinator | ch8-q-pilot.yml 44872078840 | Completed: 8/9 expected (4 merge leaves PFC + 3 half probes SUCCESS, bad-tie control FAILURE); H10 corrupt control RSS cap 10 GiB; see run-44872078840/SUMMARY.md |
| 2026-11-21 (MSK ~11:30) | item 2 q-pilot campaign 12 (merge package B: Check bidirectional_merge N18/N19, numeric-Pre control, light H10 control; 4 roots, cap 10 GiB) | item 2 | std 4707a7354a (verification attrs/modules; runtime equal modulo cfg_attr, coordinator-checked), control 7ad0c3d567 (trigger 8f33dfb1b1), tool 0aac16ef; planner task PILOT12-IMPL-TASK.md; GO coordinator | ch8-q-pilot.yml 44875428505 | Completed: 3 merge roots compile error (MergeSnapshot lacked Clone for old()); light H10 control FAILURE designated; see run-44875428505/SUMMARY.md |
| 2026-11-21 (MSK ~12:10) | item 2 q-pilot campaign 12b (retry merge package B after Clone fix) | item 2 | std 8ae4029765 (+derive Clone, Copy on MergeSnapshot; coordinator fix), control 38ef437cb8 (trigger 794e116a2f), same 4-root roster; GO coordinator | ch8-q-pilot.yml 44876372471 | Completed: 4/4 expected (merge Check N18/N19 SUCCESS ~195 s, 4.7 GiB; numeric-Pre and H10 controls designated FAILURE); see run-44876372471/SUMMARY.md |
| 2026-11-21 (MSK ~13:00) | item 2 q-pilot campaign 13 (merge package C: actual network N18/N19 with Replace swap/insert/merge + N19 corrupt control; 3 roots, cap 10 GiB) | item 2 | std b7cea7f60a (+harnesses; runtime equal modulo cfg_attr), control 65a35d901f (trigger a5610bfa0f), tool 0aac16ef; planner task PILOT13-IMPL-TASK.md; GO coordinator | ch8-q-pilot.yml 44878875303 | Completed: all 3 roots RSS cap 10 GiB in solver stage (CNF 7.7M/9.2M/8.7M clauses); see run-44878875303/SUMMARY.md |
| 2026-11-21 (MSK ~14:10) | item 2 q-pilot campaign 14 (Check sort9 provider x3 geometries; N18/N19 consumers with Replace sort9/insert/merge; N19 corrupt control; 6 roots, cap 10 GiB) | item 2 | std d02d5872c7 (verification attrs/modules; runtime equal modulo cfg_attr), control 8794a0215d (trigger 96f15c3ef4), tool 0aac16ef; planner task PILOT14-IMPL-TASK.md; GO coordinator | ch8-q-pilot.yml 44882208314 | Completed: all 6 roots compile error E0502 (two ensures with old() on &mut v in sort9 contract); see run-44882208314/SUMMARY.md |
| 2026-11-21 (MSK ~14:40) | item 2 q-pilot campaign 14b (retry after single-ensures fix) | item 2 | std ad2c458a67 (coordinator fix: one ensures for sort9), control c01bf94117 (trigger 9b45aa16e3), same 6-root roster; GO coordinator | ch8-q-pilot.yml 44883003487 | Completed: N18/N19 consumers SUCCESS (34/73 s), corrupt control designated FAILURE; sort9 Check providers RSS cap 10 GiB before CNF; see run-44883003487/SUMMARY.md |
| 2026-11-21 (MSK ~15:30) | item 2 q-pilot campaign 15 (sort9 Check provider on 11 object bits: Replace-swap and actual-swap variants x3 geometries; N18/N19 consumers + control on 11 bits; 9 roots, cap 10 GiB) | item 2 | std c5dc2a415e (verification modules only), control 29e75d9887 (trigger e8d4c482cd), tool 0aac16ef; coordinator task PILOT15-IMPL-TASK.md; GO coordinator | ch8-q-pilot.yml 44884852864 | Completed: sort9 Check on actual swaps SUCCESS x3 (~165 s, 4.3 GiB, 11 bits); Replace-swap variant RSS cap; N18/N19 consumers SUCCESS; control designated FAILURE; see run-44884852864/SUMMARY.md |
| 2026-11-21 (MSK ~17:00) | item 2 q-pilot campaign 16 (wide merge: N20 full chain, N25 mixed, sort13 Check provider 1800 s, merge N32, 2 controls; 13 roots, 11 bits, cap 10 GiB) | item 2 | std ed184d3f17 (attrs/modules; runtime equal modulo cfg_attr; contract-shape lint checked), control 0578f584b6 (trigger 94e5fba795), tool 0aac16ef; planner task PILOT16-IMPL-TASK.md; GO coordinator | ch8-q-pilot.yml 44890498157 | Completed: sort13 Check provider SUCCESS (VT 834 s, 7.3 GiB); merge N20/N25/N32, sort9 len10/12, insert-R SUCCESS; N32 numeric-Pre control designated FAILURE; insert-L, N20, N25, N25-control hit 'too many addressed objects' at 11 bits; see run-44890498157/SUMMARY.md |
| 2026-11-21 10:58Z | item 2 q-pilot campaign 17A (4 wide roots rerun at 12 bits; sort13 Check provider x5 geometries N13–N17 at 11 bits; 9 roots, cap 10 GiB) | item 2 | std 3fff6aa0db (attrs/modules; runtime equal modulo cfg_attr), control cb81adc41d (trigger 22a6422e6d), tool 0aac16ef; planner task PILOT17-IMPL-TASK.md; GO coordinator | ch8-q-pilot.yml 44896810040 | Completed (job success): sort13 Check provider SUCCESS in all 5 geometries N13–N17 (11 bits, VT ~780 s, 7.35 GiB each); insert-L and full N20 chain SUCCESS at 12 bits (7.12 / 8.65 GiB); N25 and N25 control hit 'too many addressed objects' at 12 bits too; see run-44896810040/SUMMARY.md |
| 2026-11-21 10:59Z | item 2 q-pilot campaign 17B (N13–N17 consumers via sort13 summary, P-3 at 12 bits, 2 controls; 8 roots, cap 6 GiB) | item 2 | same std, control 628a03ef3d (trigger 8992b29e86); GO coordinator; triggered after 17A starts | ch8-q-pilot.yml 44896876797 | Completed (job success): N13–N17 consumers via sort13 summary SUCCESS at 12 bits within 6 GiB (2.46–4.03 GiB, VT 16–93 s); P-3 SUCCESS at 12 bits (5.62 GiB); N13/N17 q-post controls FAILURE on their designated labels; see run-44896876797/SUMMARY.md |
| 2026-11-21 13:20Z | item 2 q-pilot campaign 18 (N25 at 13 bits + compact N25/N20 at 12 bits with controls, N20 actual inserts, 3 literal Check insert-L rel9/10/11 at 11 bits, compact sort13 observer L17 at 11 bits; 11 roots, cap 10 GiB) | item 2 | std a9e7dba799 (verify/ only; smallsort.rs unchanged), control 92dbec90b (trigger c8959e6308), tool 0aac16ef; planner task PILOT18-IMPL-TASK.md; GO coordinator | ch8-q-pilot.yml 44907708573 | Completed (job success): compact N20 with actual inserts SUCCESS 2.49 GiB / VT 34 s; compact N20 with Replace inserts SUCCESS 8.34 GiB and its q-post control FAILURE on designated label; literal Check insert-L rel9/10/11 SUCCESS at 11 bits 3.2–3.7 GiB; compact sort13 observer L17 SUCCESS 7.23 GiB (no real saving); N25 + control RSS cap 10 GiB at 13 bits, compact N25 + control too many objects at 12 bits; see run-44907708573/SUMMARY.md |
| 2026-11-21 13:55Z | item 2 q-pilot campaign 19 (matched OB11 replays: Check B18/B19, MA insert-right b10/rel9, q-only P-3, consumers N13–N17, endpoint controls N13/N17; 11 roots, cap 6 GiB) | item 2 | std 3fff6aa0db (unchanged, as 17A/17B), control 400b54a57c (trigger e2800a1137), tool 0aac16ef; planner task PILOT19-IMPL-TASK.md; GO coordinator; queued behind 18 | ch8-q-pilot.yml 44911175814 | Completed (job success): all 11 roots within 6 GiB at OB11 (max 4.43 GiB): Check merge N18/N19, Check insert-right b10/rel9, q-only P-3, consumers N13–N17 SUCCESS; N13/N17 q-post controls FAILURE on designated labels; mixed-OB edges for N13–N19 replaced by matched OB11; see run-44911175814/SUMMARY.md |
| 2026-11-21 14:30Z | item 2 q-pilot campaign 20 (actual inserts at OB11: N20 consumer + new q-post control, N25 consumer + control, N24 with right sort9 b13/len12 and merge N24 Checks, N27 with right sort13 b14/len14 and merge N27 Checks; 10 roots, cap 6 GiB) | item 2 | std bfa60b19cc (verify/sorting_q_merge.rs only; smallsort.rs unchanged), control 0b4ba53bc4 (trigger 97f552174e), tool 0aac16ef; planner task PILOT20-IMPL-TASK.md; GO coordinator; queued behind 19 | ch8-q-pilot.yml 44913550779 | Completed (job success): actual-insert consumers N20/N24/N25/N27 SUCCESS at OB11 2.5–3.0 GiB; N20/N25 q-post controls FAILURE on designated labels; Check sort9 b13/len12, merge N24, merge N27 SUCCESS ≤4.64 GiB; Check sort13 right b14/len14 hit RSS cap 6 GiB (expected ~7.3 GiB); see run-44913550779/SUMMARY.md |
| 2026-11-21 15:40Z | item 2 q-pilot campaign 21A (N21–N23 with sort9/merge Checks and controls; controls for N24/N27; 15 roots, OB11, cap 6 GiB) | item 2 | std e2bd3c6adc (verify/sorting_q_merge.rs only), control 2fa3734008 (trigger 2ffd91183e), tool 0aac16ef; planner task PILOT21-IMPL-TASK.md; GO coordinator | ch8-q-pilot.yml 44919576152 | Completed (job success): 15/15 expected — Check sort9 b01/len11, b11/len11, b12/len11, b12/len12 and merge N21/N22/N23 SUCCESS ≤4.37 GiB; consumers N21–N23 SUCCESS ≤2.66 GiB; controls N21/N22/N23/N24/N27 FAILURE on designated labels; see run-44919576152/SUMMARY.md |
| 2026-11-21 15:41Z | item 2 q-pilot campaign 21B (N26, N28–N32 consumers, merge Checks and controls; 18 roots, OB11, cap 6 GiB) | item 2 | same std, control d62b75ddd9 (trigger 74e03c5955); GO coordinator; queued behind 21A. 21C (right sort13 Checks, 8 GiB) waits for owner decision | ch8-q-pilot.yml 44919643424 | Completed (job success): 17/18 expected — consumers N26, N28–N32 SUCCESS 2.7–3.7 GiB; six controls FAILURE on designated labels; merge N26, N28–N31 SUCCESS ≤5.27 GiB; merge N32 hit RSS cap 6 GiB (SUCCESS at 6.04 GiB in campaign 16); see run-44919643424/SUMMARY.md |
| 2026-11-21 16:12Z | item 2 q-pilot campaign 21C (7 right Check sort13 b14/13, b14/14, b15/14, b15/15, b16/15, b16/16, b17/16; OB11, cap 8 GiB under owner decision for all sort13) | item 2 | same std e2bd3c6adc, control 5eef2b4861 (trigger 86bd362993); GO coordinator after owner 8 GiB decision; queued behind 21B | ch8-q-pilot.yml 44923999242 | success: 7/7 right Check sort13 SUCCESS, RSS 7.28–7.30 GiB, child ≤958 s; [summary](item2-audit-response-20261120/run-44923999242/SUMMARY.md) |
| 2026-11-21 17:35Z | item 2 q-pilot campaign 22 (compact N32 merge observer under cfg compact_merge32 + plain observer-equivalence root; 2 roots, OB11, cap 6 GiB) | item 2 | std 54123e752d (verify/ model + harness only; smallsort.rs unchanged), control 6518a69cbe (trigger 2961f5e228), tool 0aac16ef; planner task PILOT22-IMPL-TASK.md; GO coordinator; queued behind 21C | ch8-q-pilot.yml 44930211919 | success: observer equivalence SUCCESS 1.86 GiB; compact merge N32 Check SUCCESS 5.07 GiB, 525 s; [summary](item2-audit-response-20261120/run-44930211919/SUMMARY.md) |
| 2026-11-21 20:40Z | #5172 pre-merge quick CI: approved head 88fec3b397 merged with kani main b62331c9d (nightly-2026-11-20) | item 1 | fork Tiramisu-Cake/kani uninit-ci/pr5172-premerge-20261121, commit d22c845f4a (clean merge-tree); no push to the PR; GO coordinator | Kani CI 44941433558, Format 44941433551, Deny 44941433564 | Format/Deny success; Kani CI: regression on ubuntu-22.04, 24.04, 24.04-arm, macos-15, macos-15-intel, llbc, docs, benchcomp success; perf failure = hosted runner lost communication (infrastructure, same class as the upstream perf-benchcomp shutdown) |
| 2026-11-21 21:00Z | #752 on the new organizer Kani pin 9834c96ce9 (verify-rust-std #784): PR head 872d5a4338 merged with upstream main b5adb2c5c9, organizer kani.yml unchanged | item 2 | fork Tiramisu-Cake/verify-rust-std ci/ch8-pin9834-20261121, commit 5402b33188 (clean merge-tree 7ad88a0e11); Kani workflow enabled for one workflow_dispatch and disabled again; GO owner 2026-11-21 | kani.yml 44946596047 | success: all 16 jobs (4 partitions × ubuntu/macos, autoharness, metrics, list); 235/235 Challenge 8 smallsort harnesses verified (partitions 2 and 4), 0 failures; partition summaries 549/547 total, 0 failures; 20:30Z–23:29Z |
| 2026-11-22 12:00Z | #752 direct trait-method contracts candidate (6 impls incl. 3 default fn; 235 -> 245 SmallSort harnesses; opt-in controls excluded) on organizer pin 9834c96ce9 | item 2 | fork ci/ch8-pr752-trait-contracts-20261122, std 152f11556a (tree 08c6c08235, parent 5402b33188); planner PLAN.md/REVIEW.md GO (g0 1d249ce855); Kani workflow enabled for one dispatch and disabled again | kani.yml 45018616243 | success: 16/16 jobs; 245 SmallSort roots per platform incl. 10 trait_contracts; 0 failures; longest shard 79 min (macOS p2); default-fn binding open (terse output) |
Item 1 used: 50 (#5172 pre-merge quick CI 1; #5172 re-merge macOS Intel rerun 1; #5172 re-merge main CI 1; #5159 follow-up CI v2 1; #5172 merged-head CI 1; #5159 follow-up CI 1; #5206 v2 rerun 1; #5172 comment cleanup CI 1; #5206 fix CI v2 1; #5206 fix CI 1; #5172 copilot fix CI 1; #5183 cleanup CI 1; #5159 cleanup CI 1; #5176 cleanup CI 1; #5172 cleanup CI 1; #5195 cleanup CI 1; #4591 r4 perf rerun 1; #4591 r4 1; owner +1 on 2026-11-19 for #4591 CI r3; owner +1 on 2026-11-18 for the fix PR resolving kani#4591 (plain stub of a contracted function): full CI of the PR head; owner +1 on 2026-11-18 for the stub-on-contracted-function finding: confirm MRE on main; owner +1 on 2026-11-18 for F4 option A: copy the body cache per harness only when the delayed UB pass is enabled, full CI of the new head; owner +2 on 2026-11-17 for F4: confirm on main + full CI of the future PR, 2 used — confirm-main, fix full CI; A1 3, B 2, U 3, Profiles 4, E 2, C 2, Issue-MRE 2; owner +6 on 2026-11-16 for wave 0: confirm-main, F1 full CI, #5151 repro/#649, reserve; owner +2 on 2026-11-16 for F3 standalone PR: 2 used — full stock CI 43912461616 on b69f484e8c (new tests failed: `// edition: 2021` header → `--edition= 2021`), then 43920609175 on f99713506f (header fix); quick uninit-ci skipped). Item 2 used: 47 (#752 trait contracts candidate CI 1; #752 organizer pin 9834c96ce9 check 1; q-pilot campaign 22 1; q-pilot campaign 21C 1; q-pilot campaign 21B 1; q-pilot campaign 21A 1; q-pilot campaign 20 1; q-pilot campaign 19 1; q-pilot campaign 18 1; q-pilot campaign 17B 1; q-pilot campaign 17A 1; q-pilot campaign 16 1; q-pilot campaign 15 1; q-pilot campaign 14b 1; q-pilot campaign 14 1; q-pilot campaign 13 1; q-pilot campaign 12b 1; q-pilot campaign 12 1; q-pilot campaign 11 1; q-pilot campaign 10 1; q-pilot campaign 9 1; q-pilot campaign 8 1; q-pilot campaign 7 1; q-pilot campaign 6 1; q-pilot campaign 5 1; q-pilot campaign 4 1; q-pilot campaign 3 1; q-pilot campaign 2 1; q-pilot campaign 1 1; S4P3 1; S4P2-r2 1; S4P2 1; S4P1-r1 1; bridge-1-r1 1; S3-2-r1 1; S3-1-r2 1; S3-1 44405927807 charged 0 — controller stop before any root completed; S2 r5 1; owner +3 on 2026-11-18 for S2-r5…S5 with one reserve; S1 9, S2 r4-r2 1; S2 r4-r1 44328364855 charged 0 (pre-build validation timeout); S2 r0 44264952389, r1 44284869572, r2 44302170220 and r3 44310254730 charged 0 (compile failure before any root; rule from 2026-11-18: a confirmed compile failure before the first root is not charged, each retry still needs its own review and GO); S1-04 a/b charged 0). Total 97. **Owner 2026-11-19: budgets are tracked, not limiting — every run still needs review, GO and a ledger row.** F4 fix full CI: regression (macos-15) not acquired by a GitHub runner; owner 2026-11-18: no re-run, macOS coverage comes from the upstream PR CI.


## S1 admission — 2026-11-17

Coordinator records **ADMITTED_BOUNDED_SOURCE_REPORTED_S1_COMPOSITE**,35/35 QUALIFIED,
following the owner's confirmation and independent W14 APPROVE
`c4e619d9668eeea860bda1de1790665357a6e399` (no concrete findings).
Exact accepted candidate: `3c40a15d37890c8b5ef7ba49308e81279a494b05`,
[kani3300/ch8-s1/s1-08/composite-44095954742-44128268928/accept/ACCEPTANCE.md](kani3300/ch8-s1/s1-08/composite-44095954742-44128268928/accept/ACCEPTANCE.md).
Independent review:
[review/REVIEW.md](kani3300/ch8-s1/s1-08/composite-44095954742-44128268928/review/REVIEW.md).
ACCEPT.json raw SHA256: `76addef689c8808658be0bc85619b413d279ce9d692e4199822ea2284e2b97c2`.
Coordinator checked all10 candidate hashes against the review and all5 committed review files.

Fixed evidence origins, preserved without rewriting historical outcomes:

- Run44095954742/attempt1:13 complete groups/33 rows, intake
  `6d300f3ab9801c808612b562588af06e0f7b4ff9`; original cell remains incomplete/UNKNOWN.
- Run44128268928/attempt1:complete atomic cell-u34/2 rows, intake
  `0beb690dfa99e4524de71b2ffc311fe7d7556cc1`; trigger
  `4336dfed5af21660b9ac82907107be839ce13977`, tree
  `2c4475bf17bb0354e9b204e19c652549c263f90f`.
- Common std `99e8456d200fff1299ee5756279cddb23921dc65`, stock Kani
  `0aac16ef62da9e9d5645782d458593e5d78143ba`; separate requests77ae/3e61 and origin namespaces.

Admitted gates:127 fresh required obligations(111labels+16semantic bindings/sets),
113 required SAT covers,439 reviewed U records(437checks+2covers),22 Profiles-v4 PFC
chains,8 exact negatives,8 same-run companions,4 complete N0..3 unions; compatibility
PASS. Read-only replay MATCH,39 author mutations and18 independent reviewer controls PASS.
Scope is **S1 smoke N0..3**, selected concrete type/comparator/fixture instances,
U per-site/source-local and trusted stock-producer source-reported PFC policy.
This closes the S1/P1 mechanism gate on the selected six implementation bodies;
full functional coverage of lengths16/32 is not established. Independent compiler/
AST/MIR/B1/B2/general theorem credit remains NONE.

Original run remains FAILED. This is a reviewed composite, not a single successful
14-of14 workflow or uniform600s profile. Retry cell uses1200s; observed stable617.990s,
unstable485.290s. Fit600, aggregate matrix runtime/organizer CI fit and label causality
are unestablished. Published PR#752 and its source/tool pins are unchanged by admission.

**Accounting unchanged:** item2 **9/14**, total **35/40**, remaining5 fork attempts.
Admission/review costs0 additional dispatches; this note changes no reservation,
budget or historical run record. Owner requested planning only after S1: no new tasks,
CI/rerun/cancel/push/publication. Codex limit23% until2026-11-18 13:34 (owner report).


## S3-r2 exact location admission — 2026-11-19, coordinator+planner

Explicit coordinator03:15 + planner/root agreement under owner night delegation:
**ADMITTED_EXACT_LOCATION_METADATA_GATE_ONLY**, reversible, for run44416629057/
attempt1 and the original authenticated same-invocation evidence only.
Exact id AND display_id:
`slice::sort::shared::smallsort::verify::sorting_s3_leaf::s3_sort4_u8_same_alloc.unreachable.1`;
class `unreachable`, status `SUCCESS`, description `unreachable code`, file/line
both present-null, exact display `library/core/src/lib.rs:0:0 in function slice::sort::shared::smallsort::verify::sorting_s3_leaf::s3_sort4_u8_same_alloc`.

Decision/pins/constraints:
[kani3300/ch8-s3/admission-r2-location/ADMISSION.md](kani3300/ch8-s3/admission-r2-location/ADMISSION.md)
and [ADMISSION.json](kani3300/ch8-s3/admission-r2-location/ADMISSION.json).
Independent review `a9fe0055aab3279e3f5bb71bde9667925da80e65`; intake
`d29ab46dbbb45d7106fa30c3ac04bb419a2ac286`. Preserve exact head7497/source513/
stocktool0aac/controlcb6303/requestefbc/workflow8d5/compact/member/invocation
identities, 363properties/356checks/351SUCCESS/5U/0FAILURE/7SAT, exactly one missing
location, all5 located SUCCESS roles/all7 located SAT covers, every U separately
argued and all other strict checks/guards/protected identities. True positive
source origin remains UNKNOWN. No global/future-run/ID/prefix/stdlib waiver.

The original producer UNKNOWN/rejection, REJECT_ALL/proposalDISABLED/0-of9 and
historical evidence are unchanged; no decoder/request/runtime patch. This admits
only the exact metadata gate at SOURCE_REPORTED S1 assurance, not full leaf,
caller/generic/init/B1/B2 proof or an assumed summary. Overall qualification
awaits W14-01/W14-02 reporting corrections and SAME14 delta; other gates remain.
Reversible by a later append-only decision; coordinator informs owner morning.
**Accounting/reservation unchanged:** item1 **31/31**, item2 **12/17**, total
**43/48**. No dispatch, charge/refund, extra item1 grant or publication authorized.


## S3-1-r2 admission — 2026-11-19, coordinator+planner

User03:27 explicitly authorized admission after committed APPROVE. Planner/root
records **ADMITTED_BOUNDED_SOURCE_REPORTED_S3_1_R2_CASES:7/7 completedcases QUALIFIED**:
4 actual-body bounded PFC leaves (swapgeometry,sort4separate,sort4same,merge8separate)
+3 intendednegativefixtures (checkerorder,checkercount,sort13weak).
Acceptedintake31c1dbfc7ca2df34b28bb5eb7ee81bc207ee5642; independentdelta
657b1e0f97244bdc0ce67fa90c6581bff35fdb84 APPROVE/W14-01+02CLOSED.
Decision [ACCEPTANCE.md](kani3300/ch8-s3/admission-r2-qualified/ACCEPTANCE.md),
[ACCEPTANCE.json](kani3300/ch8-s3/admission-r2-qualified/ACCEPTANCE.json).

Exact S1/Profilesv4 SOURCE_REPORTED bindings:42 per-site source-local U arguments,
16 located SUCCESS roles,3 intended FAILURE roles,24 located SATcovers (43literal
sites). Corrected sort13weak domain=fixeddescendinglen13[12..0]/sourceboundcaller
copy+weak_swap seam; no arbitrarybytes/actualsort13proof. FourSUCCESSunsupported
records perpositive/16total retained; no empty-array claim/FAILED-UNKNOWN waiver.
Exact reversible f740 originalrun sort4same systemSUCCESS.unreachable.1 location
exception only, fulltuple/count/invocation/protectedidentities/nulls/originUNKNOWN
preserved. No global/future-case/reader/runtime exception. Originald29/reviewa9fe/
nativeevidence/producerUNKNOWN/REJECT_ALL/proposalDISABLED/strict0of9 untouched.

Run44416629057/1/head7497/source513/tool0aac/controlcb6303/requestefbc/workflow8d5/
compactb9a024 remain bound. All9 sealed/noglobalstop;2 capped roots remainUNKNOWN
(insertRSS112.349s,merge8samechild600.205s),8sourceIDsdeferred. NotfullS3/N16/N32,
not universalfunctioncontract/assumedsummary/caller/generic/allallocation/init/
AST/MIR/compiler/B1/B2/fit600 theorem. Exactdomain/frame/init/provider/type/cfg/
caller restrictions in ACCEPTANCE.json remain mandatory for everyfutureuse.

**Accounting/reservation unchanged:item1 31/31,item2 12/17,total43/48**. Admission
adds0 dispatches, no budgetgrant/charge/refund/CI/push/publication. User03:27
separatelyauthorized offlineS3-2implementationplan86f/taskbe420 afteradmission;
finalexactpackage independentreview/root+coordinatorGO before anynewworkflow.
All earlier ledger bytes/historicalrecords retained unchanged.


## S3-2-r1 exact metadata + bounded case admission — 2026-11-19 coordinator+planner

Coordinator05:39 requested intake review and location decision;05:54 reported
RECOMMEND_EXACT_CASES. Root agrees after committed intake5d9439a764 and independent
review028531727f APPROVE_INTAKE_WITH_PRESERVED_LIMITS/zero blockers.
Decision [ADMISSION.md](kani3300/ch8-s3/admission-s3-2-r1-exact-location/ADMISSION.md),
[ADMISSION.json](kani3300/ch8-s3/admission-s3-2-r1-exact-location/ADMISSION.json).

ADMITTED_EXACT_LOCATION_METADATA_GATE_ONLY for THREE separately pinned packets in
run44439462279/1: m8_s32_d00_allinit, m8_s32_d00_partial_diag,
m8_s40_d16_partial_diag. Each exact harness.unreachable.1/systemSUCCESS/nullfileline/
lib.rs:0:0 record, cardinality1, all386properties/380checks/372SUCCESS/8U/6SAT and
source1b4/tool0aac/control775/head474/request756/workflow0fde/invocation/namespace/
parser/schema/member/fingerprint constraints are mandatory. Every other gate stays
strict. Actual shared emitter/source-MIR origin UNKNOWN; GENERAL_RULE PENDING,
no wildcard/future-run transfer. Oldf740 original-run-only decision unchanged.

ONE QUALIFIED_BOUNDED_SOURCE_REPORTED actual-body PFC case: m8_s32_d00_allinit,
source[32,40),dst[0,8),backingMU48,fullu8/KeyLess/sorted4+4,knowninitial[8,48).
FiveSUCCESSliteralroles+sixSATcovers/eightper-siteU/fourSUCCESSguards retained,
S1 source-local/Profilesv4 source-reported assurance only. No actual init-mask/
dstinit/universalcontract/provider/ASTMIR/B1B2/generic/fullN16N32 theorem.
BOTH partialrows remain DIAG_INIT_OPEN/nonproviders and close0qualifiedinitcontexts;
all34sort8init/callercontexts OPEN. Two insertion roots RSS-censored UNKNOWN.
Three fixed negative labels reviewed, no additional control admission in this note.

Original evidence/workflowFAILURE/producer3OBSERVED5UNKNOWN/strict0of8/U-REJECT_ALL/
proposalDISABLED/nullcoordinates are unchanged. Reversible by append-only decision
if any exact identity/fingerprint/source-local premise fails; no runtime/parser/
policy patch or automatic S3-3 implementation/run.
**Accounting/reservation unchanged:item1 31/31,item2 13/17,total44/48.**
No dispatch/charge/refund/reservation/grant/publication.


## Bridge-1-r1 bounded admission — 2026-11-19 coordinator+planner

Coordinator08:54 explicitly requests admission after independent review. Root
records **2 QUALIFIED_BOUNDED_SOURCE_REPORTED cases**: `i_p01_b01_fullu8`
(actual insert_tail PFC fixedV34/base1/tail1/span2/u8/KeyLess) and
`sort9_v34_b01_len09_real` (Original actual25swaps/V34/base1/len9/u8/KeyLess).
Accepted intake97eaff96cd28267e36af69fe98077dd08737eea6, independent review
135c04791a779e949079db723bdbc0e636873b37 APPROVE/no findings.
Decision [ADMISSION.md](kani3300/ch8-s3-s4/admission-bridge-1-r1/ADMISSION.md),
[ADMISSION.json](kani3300/ch8-s3-s4/admission-bridge-1-r1/ADMISSION.json).

Exact run44460583125/1/headc2bb/sourcef1bdf/tool0aac/controltree6280/request23c137/
workflow317f/payload32fdc7 and per-case invocation/property/member fingerprints
remain mandatory. Each has4locatedSUCCESSroles+5SATcovers;11 reviewed positive
source-localU and7SUCCESSunsupportedguards retained. **No location exception**
needed/applied: all602 completed native records are located; oldf740/ff193 remain
original-run-only. One insertiongeometry is not all tails/bases; actualsort9case
is not a universal contract/verified summary. No independent init-mask/provider/
ASTMIR/B1B2/generic/Cell/fullN16N32 credit. Both capped families remainUNKNOWN
(child600wall),3negative labels remain reviewed observations/no extra admission.
OriginalworkflowFAILURE/strict0of7/REJECT_ALL/proposalDISABLED/history unchanged;
no source/runtime/parser/request/policy patch. Reversible append-only decision.
**Accounting unchanged:** item1 32/32,item2 14/17,total46/49 references only;
owner budgets tracking-only. Admission adds0 runs, no charge/refund/reservation/
budget grant/implementation/CI/push/publication. Old ledger prefix retained.


## S4P1-r1 fallback admission — coordinator+planner 2026-11-19 11:59

Usercoordinator11:59 explicitly accepts both fallback blocks; root AGREE.
ADMISSION: kani3300/ch8-s4/admission-s4p1-r1-fallback/ADMISSION.json.
Two QUALIFIED_BOUNDED_SOURCE_REPORTED cases only:
s4p_fallback_b01_n00_02_fullbyte and s4p_fallback_b01_n03_04_fullbyte,
actual Original Cell<u8>/KeyLess<Cell<u8>> on initialized V34/base1/all34
independent logicalu8/fullsortedcount/everyoutsideframe/canary. Their disjoint
length union is N0..4 for this exact family/context; no generic or universal
function-contract/provider/summary/init-mask/MIR/B1B2/fullN16N32 promotion.
Exact intake842984040e87b8b8594653634b72df7d800ca198 and independent review
3c7bd65cf0bb758cb82dc56ef71a8b8e23efd5c0 APPROVE/no blockers; each4 located
SUCCESS roles,8/7 SAT covers. All source-local U and SUCCESS guards retained.

Exactly one systemclassunreachable/statusSUCCESS/descriptionunreachablecode/
unreachable.1/nullfile+line/lib.rs:0:0 dictionary per exact fullfallback ID is
admitted for run44481580554/attempt1 ONLY, under full invocation/namespace/
property-inventory/count/status/source985/tool0aac/control2db/head563/request3d135/
workflowa567/membercf4a2cbd/payload455302/epoch fingerprints in ADMISSION.json.
All other metadata/status/roles/covers/U/guards/extra-failure/identity gates stay
strict. Common emitter/source/MIR origin UNKNOWN; no suffix/std/general/future
waiver. Old f740/ff193 remain original-run-only; new general rule NOT_APPLIED.

Both network roots remain UNKNOWN_CENSORED at child600 wholechild wall; four
intended negative controls remain reviewed observations/no extra admission in
this note. Native workflowFAILURE/producerUNKNOWN/strict0of8/U-REJECT_ALL/
proposalDISABLED/old evidence and nulls unchanged. No parser/runtime/request/
source/policy patch. Reversible only by append-only decision.
Accounting unchanged: item1used32,item2used15,total47, tracking-only reference.
This admission adds0 runs and no charge/refund/reservation/grant/CI/publication.


## S4P2-r2 network admission — coordinator + root, 2026-11-19

Координатор запросил admission после независимого APPROVE; root согласен
после проверки точных intake/review/pins/119 structured members и всех1,143
нативных свойств. Решение: [ADMISSION.md](kani3300/ch8-s4/admission-s4p2-r2-network/ADMISSION.md),
[ADMISSION.json](kani3300/ch8-s4/admission-s4p2-r2-network/ADMISSION.json).

Приняты FOUR QUALIFIED_BOUNDED_SOURCE_REPORTED cases:
- s4p2r2_network_b01_n02_fullbyte;
- s4p2r2_network_b01_n03_fullbyte;
- s4p2r2_network_b01_n04_fullbyte;
- s4p2r2_network_b01_n00_01_fullbyte.

Это actual Original small_sort_network<u8,KeyLess<u8>> на initializedV34/base1,
all34independentfullu8, с полными sortedness/count/frame/canary. Точный
дизъюнктный union — N0..4 в этом контексте. Intake7c66fb85b99f77801ff10e99ccc5d37761ba5442;
review2d872340cdea8c5ff39fbf2cc181af823dcb36a6 APPROVE/zero blockers.
Run44548842328/1, head d88fac48cf50a742f9f00026ba66e5e4353e1019; source8faf8e62af8f82b5c46af020086f8df591b6757e;
stocktool0aac16ef62da9e9d5645782d458593e5d78143ba. Все полные request/workflow/member/
payload/invocation/namespace/source/property/protected fingerprints — в решении.

Каждый positive имеет4 SUCCESS-роли; SAT covers6/6/6/3, обе длиныN01 достигнуты.
49 positive U получают только exact per-instance S1 source-аргументы:
25 source-path exclusions и24 generated failure-edge exclusions. Из всех67
проверены16 merge U через actual helper branching;18 negative U остаются
наблюдениями контролей без нового admission. У12 positive SUCCESS guards
статусы сохранены;12 model/builtin records разобраны по точным tuple.
Missing/zero locations нет: нового location exception или общего правила нет.
Причина native U classification и backend builtin/MIR origin остаётся UNKNOWN.

Исторические workflow FAILURE/SELECTED_PARTIAL/strict0of8/REJECT_ALL/disabledproposal/
s3_expected_match=False/все исходные статусы и receipts не изменены.
N2/N3/N4 экспортируют0 residual unwind assertions;N01 —1 SUCCESS; resolved36
и complete export зафиксированы без выдуманного unexported/MIR safety credit.
Provider/initmask/generic/caller/ownership/panic/Drop/summary/fullN16N32/MIR/B1B2
OPEN. Старый S1 smoke-domain и прежние location admissions не переписаны.

ADMISSION_ONLY, append-only. Accounting unchanged; runs_added0.
Нет нового dispatch/charge/refund/reservation/grant/source/parser/policy/CI/push/publication.
Отзыв — только следующей append-only записью при нарушении любого exact premise.


## S4P3 network N8/N9 admission — coordinator + root, 2026-11-19

[ADMISSION.md](kani3300/ch8-s4/admission-s4p3-network/ADMISSION.md), [ADMISSION.json](kani3300/ch8-s4/admission-s4p3-network/ADMISSION.json).

Координатор запросил admission после независимого review; **root AGREE**.
Приняты **два QUALIFIED_BOUNDED_SOURCE_REPORTED cases**: actual
`small_sort_network<u8,KeyLess<u8>>`, exact N8 и N9, Original/null,
initialized V34/base1/all34independentfullu8, полный sortedness/count/frame/canary.
N8 выполняет insertion tails1..7; N9 — actual sort9 и zero-body insertion entry.
Это только множество {8,9}, без интерполяции длин или переписывания старых admissions.

Intake **8bf99aa314310e4a3d5b86b8d0f112ddff2886ab**; review **ec49aa6408fdb2bce6f1e15511162aa8664ea0ae APPROVE**, zero blockers.
Root:48 intake files/47 hashes,8 review files/7 hashes,119 structured members,
173 controlpayload,43 source hashes; **1480 targeted checks PASS**.
Frozen local/upload collectors и prefixes0..8 совпали. Повторной acquisition,
native/full Validate/CI не было. Exact fingerprints — ADMISSION.json/PROVENANCE.json.

Каждый positive:4 SUCCESS-роли,6 SAT covers, complete258 properties
(241 SUCCESS+11 U+6 SAT), requested/resolved unwind36,0 exported residual unwind records.
22 positive U приняты по exact intake и independent reviewer arguments:
10 source-path exclusions (8 merge,2 caller) и12 generated failure-edge exclusions.
Причина producer check-site UNREACHABLE, emitter/MIR и builtin origin UNKNOWN.
6 positive SUCCESS guards и6 model/builtin records сохранены отдельно.
Все655 observed records имеют положительные coordinates:
**нового missing/zero-location exception не требуется и не применено**.

N13/N17 остаются **BLOCKER**: child600 timeout, incomplete inventories,
properties/roles/covers/unwind UNKNOWN, не ноль. Оба пути ещё до merge.
655 — subtotal шести complete inventories, не total восьми полных native proofs.
Четыре expected negative FAILURE и18 negative U — наблюдения без нового admission.
Workflow FAILURE, SELECTED_PARTIAL, strict0/8, s3_expected_match=False,
ZERO_U/REJECT_ALL/disabledproposal и все original receipts/statuses неизменны.
Generic/type/provider/caller/summary/initmask/dstinit/ownership/panic/Drop/fullN16N32/
independent AST-MIR/B1-B2 OPEN; independent proof credit NONE.

Ledger — только ADMISSION_ONLY append с сохранённым prefix hash.
Accounting/runs/charge/refund/reservation/grant не менялись.
Нет source/tool/control/parser/policy/CI/push/publication изменений.
При нарушении exact premise — отдельная append-only запись об отзыве.

Run44577116178/1; head960cc686097c093fe0d64f73f4f4a9736e06eec2; source7b31b060b90ce286e94547993f6a698c549bc5fa; stocktool0aac16ef62da9e9d5645782d458593e5d78143ba.
ADMISSION_ONLY. runs_added0; accounting unchanged.

2026-11-21 ADMISSION_ONLY: q-pilot network N13–N19 admitted (item2-audit-response-20261120/ADMISSION-N13-N19-FINAL.md, g0 1e21c9976b). N18/N19 fit 6 GiB (max 4 539 168 KiB); N13–N17 under owner 8 GiB lane for the five Check sort13 roots only (max 7 709 832 KiB), other roots ≤6 GiB. Runs 44884852864, 44896810040, 44911175814 (+15/12b providers as listed). runs_added 0; accounting unchanged.

2026-11-21 ADMISSION_ONLY: q-pilot network N20, N25 (sort13 8 GiB lane) and N21–N24 admitted (ADMISSION-N20-N24-N25.md g0 8352229ebb/467f28457e, ADMISSION-N21-N24.md g0 da7c88e787). Admitted network lengths now 0–25. runs_added 0; accounting unchanged.

2026-11-21 ADMISSION_ONLY: q-pilot network N26–N31 admitted (item2-audit-response-20261120/ADMISSION-N26-N31.md, g0 c013306bdd). Check sort13 roots in owner 8 GiB lane (max 7 709 832 KiB), all other roots ≤6 GiB (max 5 527 296 KiB, merge N31). Runs 44896810040, 44913550779, 44919576152, 44919643424, 44923999242. Admitted network lengths now 0–31. runs_added 0; accounting unchanged.

2026-11-21 ADMISSION_ONLY: q-pilot network N32 admitted (item2-audit-response-20261120/ADMISSION-N32.md, g0 4f44620532). Compact merge32 observer Check (std 54123e752d, cfg kani_smallsort_q_compact_merge32) 5.07 GiB linked by source and equivalence root to the Replace contract used by consumer on e2bd3c6adc; sort13 Checks in owner 8 GiB lane. Runs 44896810040, 44919643424, 44923999242, 44930211919. Admitted network lengths now 0–32 (all). runs_added 0; accounting unchanged.
