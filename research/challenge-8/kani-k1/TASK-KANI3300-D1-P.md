# KANI3300 D1-P — bounded A + B-lite, worker 15

**Выдано координатором 2026-11-13.** Runtime **Codex**, одна сессия подготовки, **Cloud $0**.
Владелец одобрил только один диагностический пакет; исполнение fork CI, push Kani-веток и dispatch — координатор.
Это верификация корректности, не security-работа.
Цель — attribution данных, не новая memory model, representation variant, scope cut или закрытие M3.

## Вход, изоляция, неизменность модели

Прочитать целиком `AUDIT-REPORT-KANI3300-PFC-RESOURCE-RU.md` @ **ab7509822453bbf0778da0265c67f51bc08b4755**,
особенно §2.3,4,7,9; brief v2 @cbf575f3aa и `kani3300/m2br6b/{DIAGNOSTIC-MANIFEST.json,CI-REQUEST.md}`.
Два независимых exact parents (не накладывать один на другой):

| Case | Source parent | Tree |
|---|---|---|
| R1+skip | **56cbc5c4a479bc3fb25310b14fcf279d90581a02** | a97ec3d06efd827829f550f1e7a98f29538758fe |
| R6-02b | **405c1f059264d8f7cedeeaa01c6d4ad6867a419e** | 162e8ad1e76e842b18c24a4ac2986335902834d7 |

Источник `/root/kani-fix-3300-m2br6b` read-only. Создать отдельный `/root/kani-fix-3300-d1p`,
ветки `diagnostics/kani-3300-d1p-r1-skip` и `diagnostics/kani-3300-d1p-r6b` от соответствующих parents.
Existing/dirty destination или другой pin → STOP без reset/stash/чужих файлов. До одного CI-only коммита на parent.
Разрешены только новый manual `workflow_dispatch` workflow и его capture/parser scripts + frozen input copies в
отдельной diagnostic directory. Existing suites/goldens/workflows не удалять и не ослаблять.
Compiler/runtime/driver/library/toolchain/CBMC source, checks, flags и модель **не менять**; C/патч CBMC запрещён.
Одинаковые scripts/workflow/input bytes на обоих parents; зафиксировать allowlist diff и hashes unchanged production trees.
Само наблюдение — внешние wrappers/штатные dumps; не добавлять GOTO/MIR calls, assumptions, state writes или instrumentation skips.

P1 из `kani3300/m2a/cases/scalar-pfc-legal.rs`: SHA256
`fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b`, root `postcondition_reads_initialized_return`.
P2 `scalar-pfc-hole.rs`: `61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759`,
root `postcondition_reads_returned_hole`. Не добавлять covers/переименования/упрощения ради данных.
Основной Kani argv/env — m2br6b/CI-REQUEST: edition2021, -Dwarnings, --emit=mir, singleton --exact,
`-Z uninit-checks -Z function-contracts --keep-temps`; сохранить фактические checks/solver/target/object-bits/slicing/defaults.
`--output-format=old` запрещён: нет полноценного property inventory. Template argv не выдавать за actual invocation.

## 1. Сначала исправить diagnostic workflow (§2.3)

Workflow только manual, jobs/cases последовательно, один real CBMC одновременно, без automatic retry.
Каждому pin/input/root/phase — отдельные paths и receipts: source/CI/tree/fixture hashes, root, run/job,
working directory, resolved executable/version/SHA256, **actual argv как JSON array** и allowlisted flags, не весь environment.
Логировать реальный spawn, не повторять Kani/solver ради argv. Wrapper вызывает resolved real binary ровно один раз,
исключает PATH recursion, сохраняет original stdout/stderr/exit/signal и не ломает JSON stream/pipe semantics.
Отдельные статусы setup/build, capture, symex-only, verification, parser и artifact upload; verification здесь NOT_RUN.

Убрать `grep | head` как evidence interface. Раздельные bounded phase logs и curated summaries, начальные counters и
финальный outcome независимо; каждый cap: limit/emitted/dropped/bytes/records, `truncated` и parser completeness.
Collector продолжает drain после лимита записи, без SIGPIPE производителю; ограничение времени/памяти остаётся явным.
Raw RSS и maxrss хранить **в KiB**; GiB = KiB/1048576. Watchdog sample, sampled max и time-v maxrss — разные поля.
Записать прежний cutoff 6291456 KiB/2s/300s как historical context; новые symex-only limits заданы ниже.
Сохранять timestamps, actual CBMC PID/PGID, accounting scope, limiter reason и last completed phase.
Управлять **собственной process group/session** case, включая потомков; никаких общего `pkill cbmc` или убийства runner.
Сохранить исходный rc/signal отдельно от exit wrapper, watchdog и Kani Timeout; killed JSON может быть incomplete.

Список observed failed properties — отдельный структурированный файл: ID/class/location/description/status, totals,
точное число разобранных records и complete flag; не только первые 30 строк. При kill/обрыве JSON **полнота UNKNOWN**,
известные failures сохранить, пустой список не трактовать как отсутствие failures. Без SAT failure inventory NOT_RUN/UNKNOWN;
не повторять normal verification ради полного списка. Полнота streamed records и полнота semantic verdict — разные поля.
Не восстанавливать хвост из старого run; записи failures не обрезать display-лимитом top-30.
Ориентиры caps: logs ≤8 MiB/stream/case/phase, failure inventory ≤2 MiB, selected projections ≤16 MiB/phase,
summary ≤200 строк и top-30 expression roots; binary snapshots целиком ≤64 MiB каждый, иначе cap receipt и STOP completeness.
Выбранные limits явно записать в CI-REQUEST; limits вывода не разрешают неограниченный parser traversal.
Artifacts с manifests/SHA256/coverage выгружать при `always()` после failure/kill; paths детерминированы, upload failure виден.
Kill/timeout/setup/collector error не дают итоговый PASS; tool failures не скрывать общим green step.
Collector может продолжить сбор второй конфигурации после отказа первой; diagnostic completion ≠ verification SUCCESS.

## 2. A — actual pre/post-DFCC и solver input

Использовать pinned `kani-driver/src/call_goto_instrument.rs::instrument_model/instrument_contracts`,
`harness_runner.rs` и `call_cbmc.rs`; проверить API на **обоих** parents, не только на позднем R8.
Внешняя обёртка реального `goto-instrument --dfcc` сохраняет input **до** in-place вызова и output после него.
В argv input/output могут быть одним файлом: копировать заранее. Pre-DFCC здесь уже specialized, не raw compiler output;
post-DFCC — до последующих library/undefined-function/drop-unused/backedge/synthesis преобразований.
Отдельно сохранить **точный GOTO на actual CBMC spawn**, его hash/bytes и связь с post-DFCC: позже файл мог измениться.
Подготовить штатный diagnostic invocation, проходящий тот же Kani frontend/DFCC pipeline без SAT; записать добавленный
symex-only option явно. Возможную несовместимость diagnostic stdout с Kani JSON parser отличать от CBMC/capture failure;
не подделывать JSON/успешный verdict для продолжения. Если pipeline так не запускается, STOP с точным source finding.
Записать все фактические DFCC invocations/root/modes/input/output/exit; missing/duplicate/failed invocation — явный статус,
не произвольный `find | head -1`. Нельзя дополнительно вызывать mutating compiler transformations для снимка.

Штатными stock CBMC/goto-instrument views построить выбранные symbol/function/type projections и карту:
transfer Store/Load/Begin/return0, init/reset, generated PFC/clauses/Assert bodies, marked state, private assigns и actual writes.
Для monomorphized `Layout<N>` — N/элемент/extent bytes/bit width, associated type/callsite и откуда взято значение;
отделить payload, backing object, pointer width и shadow metadata. Нет точного вывода из type/model → UNKNOWN, не «N=1».
Для private writes различить cell address/extent и pointer value/pointee; привязать symbol → target → write/guard → PC/property.
Оригинальные snapshots не переписывать inspection-командой; все диагностические exports в отдельных paths.

## 3. B-lite — stock symex view + офлайн-сводка

Только CBMC **6.11.0**, фактический backend argv и exact saved CBMC input. Diagnostic argv должен отличаться
только штатным режимом вывода; solver/checks/property-set/object bits/slicing не менять ради маленького вывода.
Начать с `--program-only`; `--show-vcc` или `--show-byte-ops --json-ui` только как дополнительный нужный view.
До двух stock symex-only invocations на P1/pin, каждый ≤60s и ≤2 GiB, без SAT; cap/timeouts явно INCOMPLETE.
Не включать --full-slice, --property narrowing, arrays-uf changes, solver-stats collector, DIMACS или полный expression dump.
Штатный режим сам может форматировать большие выражения: caps/time/node budgets нужны до/во время обработки, не один head.

Узкий streaming/offline Python-анализ: all/ignored/retained **видимые** SSA steps и категории, source function/PC,
visible operators, constant/symbolic offsets/indices, exact known widths и top-30 expression roots по width и occurrences.
Описать parser grammar, normalization/fingerprint и denominators; VCC повторяет prefixes — не считать их новыми SSA steps.
`--program-only`/VCC/byte-ops не дают полный converter workload: не потерять guards/assumptions/auxiliary categories молча.
Byte-ops dump может включать ignored steps; текст не всегда несёт types, sharing или все категории `convert_without_assertions`.
Отделить exact / source-derived / textual heuristic / UNKNOWN; unique textual fingerprints **не** unique IREP DAG nodes.
Нет ширины/owner/ignore bit/PC либо output truncated → заполнить gap/coverage, не реконструировать по скалярному P1.
Сохранять bounded term excerpts с model hash, function/PC, record/byte coordinates и excerpt hash, а не только aggregate counts.
Без патча CBMC точная сводка может оказаться неполной: это допустимый результат с `offender не найден`, не повод начать C.

## Объём CI, подготовка и handoff

Обязательны оба P1 cases: A+B-lite. **Normal SAT/verification не запускается**, verification/failure inventory
NOT_RUN/UNKNOWN, не приписывать им результат symex-only. Никаких normal solver replay/retries.
P2 default OFF: только по выбору координатора после дешёвого полного P1 symex capture обоих pins (≤60s/2GiB без caps),
только A+B-lite, не более тех же двух symex views/pin; новый normal P2 solver в эту стадию не входит.
Никаких R7/R8/upstream reruns, новых representation вариантов, fixes, scope decisions, M3 или full gate.

Подготовка без local cargo/rustc/Kani/CBMC/Miri/builds. Разрешены Git/hash/diff, shell syntax и Python synthetic tests:
success/failure JSON, signal/timeout, malformed/partial/empty input, cap+continued drain, missing tools/identity mismatch,
duplicate snapshots, UNKNOWN widths/ignored steps, повторяющиеся VCC prefixes, subprocess-group cleanup на fake child.
Fake child не запускает verifier/compiler. Проверить quoting/argv/no shell-eval, types/units и отсутствие secret/env dump.
Один bounded Luna High review scripts/status/capture boundary, без nested delegation; исправить конкретные замечания.

В g0 **kani3300/d1p/**: INPUTS.json, PLAN.md, CI-REQUEST.md (commands для координатора, cases/limits/expected artifacts),
ARTIFACT-SCHEMA.json, parser/capture synthetic tests или ссылка на exact overlay scripts, STATIC-CHECKS.json, REVIEW.md,
RESULT-KANI3300-D1-P.md (≤25 строк), patches/ и manifest двух CI-only commits/parents/trees/allowlist hashes.
До CI: SOURCE_READY/NOT_COMPILED, observed bindings UNKNOWN, proof credit0. Local CI-only commits нейтральные,
author/committer Tiramisu-Cake <igkharin@gmail.com>, **не push**; координатор публикует и запускает.
Research commit [skip ci], тот же author/committer, stage только d1p/, push g0 без force; concurrency → handoff без reset/stash.
Не читать старые raw logs/архивы/GCS, не публиковать PR/issues, не включать сторонние PR links; credentials не трогать.
После reviewed preparation STOP. D1-A выдаётся координатором в следующей сессии по локальным bounded данным.
Последняя строка: `READY <sha research-коммита D1-P>`; READY не означает CI/solver PASS.
