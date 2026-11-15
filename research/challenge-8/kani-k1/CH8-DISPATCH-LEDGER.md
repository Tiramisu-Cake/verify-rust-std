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
- Shared base P′ `c5ff36ff43` (merge 872d + upstream main 6079edcda3) on std fork `experiment/ch8-pprime-20261116`.

Item 1 used: 3 of 18 (A1 2 of 3, B 1 of 3). Item 2 used: 1 of 14 (S1 1 of 2; S1-02 = last S1 credit, after P′ rebase). Total 4 of 32.
