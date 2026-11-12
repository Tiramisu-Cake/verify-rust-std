# KANI3300 M2-B/R — PFC+uninit resource regression и private frame, worker 15

**В очередь после B3-CI и отдельного handoff координатора; B3 не прерывать.** Runtime **Codex**, одна аналитическая сессия,
**Cloud $0**, без локальных compiler/verifier запусков; fork CI только координатора.
Это верификация корректности, не security-работа.

**Новый handoff:** M2-B/R @c90cb9466d; R01–R04 probes A2R43249040713/A3R43249047207 оба heavy
после reported symex/postprocess. Worker15 переходит к TASK-KANI3300-M2BR2.md: actual widths/DFCC use и early-Part1
bisect ≤4pins; прежнюю очередь не повторять. Release repair/seed gate не открыты, historical m2br results не менять.

## Вход и цель

Прочитать TASK-KANI3300-M2B.md (таблица трёх runs — coordinator-reported facts), M2-A @
**ea0fbb5931f08bd1a253db9d023a24f94f365a30**, `kani3300/m2a/{cases/scalar-pfc-legal.rs,cases/scalar-pfc-hole.rs,SITE-MAP.md}`,
M2 QUALIFICATION-MAP и stage results `kani3300/{a1,a2,a2r,a2r2,a3,a3r,b1i}/`.
P1/P2 с actual proof_for_contract и uninit нужны неизменными во всех matched comparisons; записать input hashes.
M1+M2 run43243491671 и B1I-A43244391200 превысили watchdogRSS; upstream43244395728 закончил с frame/Unsupported,
а не с доказательством. Установить, **на каком этапе pipeline и после какой source delta** растёт модель/ресурс,
и как store_argument взаимодействует с modifies. Не обещать устранить OOM до причинного binding.

Source pins: upstream **bf9c58e662fd65c64381ef2ac97a6397ffc0693a**;
B1I-A **6134e42dd1c65dc980336e7d9455aba02d423edf** (test-only поверх B1I production);
M1+M2 **5f7f2b7364135a0a8b7cfd86c43b4491a8911bac** (production254ae69662).
Оригинальные source clones read-only. Результаты/fixtures worker14 не менять, release model не чинить в этой стадии.
Если потребуется diagnostic source ablation: отдельный clone **/root/kani-fix-3300-m2b-resource**, ветка
**experiment/kani-3300-m2b-resource** от exact6134, manifests с каждым parent/delta; existing/dirty destination → STOP.
Не reset/stash/rebase source других стадий. Любой diagnostic commit — NOT_RELEASE_CANDIDATE, Kani не пушить.

## 1. История и source/size hypotheses, до новой CI очереди

Построить фактическую ancestry/source-delta карту upstream→Part1→A1→A2/A2R→A3/repairs→B1I→M1.
Кандидаты границ: A1 final613c188313, pre-A3 **b207847932**, A3 final0b1d68ac69, A2R2 **585c93b2ff**,
A3R **a0a2386001**, B1I production **cdb439b0a4**, B1I testsdc5f5a4067/A6134; подтвердить fullSHA/tree/parent,
порядок по git, не по номеру стадии (A2R2 шёл после A3). Не смешивать test-only/workflow changes с production suspects.
Некоторые старые pins могут иметь known build/Unsupported defects: такой outcome не resource verdict, не патчить их молча.

Source anchors для проверки, не диагноз:

- `library/kani_core/src/mem_init.rs::{store_argument,load_argument}`: signature/count/index, demonic selection,
  fields marked MEM_INIT_STATE, layout_size, witness retarget, false snapshot и source-before-Move/reset.
- `check_uninit/ptr_uninit/uninit_visitor.rs` и lowering `check_uninit/mod.rs`: количество injected stores/loads/checks,
  actual reached call kinds/generated wrappers, extra monomorphizations. Buffer protocol/private-state расширение — гипотеза.
- `codegen_cprover_gotoc/codegen/contract.rs::codegen_modifies_contract`: marked shadow-static assigns exemption,
  emitted symbol и DFCC instrumented assigns writes; `contracts.rs` и generated Check/ensures/modifies wrappers.
- M1 immutable branches/extent могут менять размер, но observed resource threshold уже есть без M1. Worker14 владеет
  immutable_allocations/anonymous_origins/operand/compiler-interface и seed fix: их не редактировать параллельно.

Отделить rustc/codegen, goto instrumentation/DFCC/inlining, symbolic execution/VC generation, CNF/SAT стадии.
Для matched P1/P2 запросить доступные curated phase milestones, argv, object/symbol/function/instruction/check counts,
array/layout extents, VCC/variables/clauses и RSS/elapsed именно соответствующего процесса. Не определять стадию по названию cbmc.
Большой backend object либо пропавший store/load/early Unsupported upstream объясняет несопоставимость; не заявлять speedup
за счёт отсутствующего пути. No-match/partial report — UNKNOWN; отсутствующие sizes не выдумывать из source lines.

## 2. Минимальная адаптивная CI-очередь

Сначала использовать existing curated results и source audit; при необходимости non-solving model inventories на тех же
P1/P2 через существующий quick/probe. Не строить runner, новые глобальные traces или автоматический полный git-bisect Builds.
Первый новый запрос **до4 input×pin configurations**, последовательных, не весь history×P1×P2 product:
выбрать P1 legal как первый фиксированный input, две наиболее различающие границы (например pre-A3 b207 против A3R a0,
если source это обосновывает), затем P2/более узкая граница по результату. Upstream/6134/M1 не повторять без причины.
Один root/solver, existing timeout300s и watchdogRSS>6GiB; записать sampling/overshoot, process-tree vs per-process,
raw RSS units/actual limits и signal/exit, не выдавать 6GiB за точный hardware cap. Cutoff = RESOURCE_INCOMPLETE.
Для следующего batch — отдельный handoff после результатов, не автономное разрастание матрицы.

При невозможности дешёвого historical comparison — подготовить **одну узкую source-bound ablation** причинного кандидата
в diagnostic branch, с exact hunk и lost-obligation ledger. Отключение transfer/private-state/PFC/checks/no-assert/seed
даёт только отрицательный диагностический контроль, никогда release fix/semantic PASS. Не переносить blanket skip в кандидата.
Предпочесть маленькие probes с одним paired call/минимальным useful ensures; semantic gap от удаления select/return MU/
frame/false-source отметить отдельно. Не уменьшать unwind/assume initializedness или менять solver между matched сторонами.

## 3. Frame: точная причина, без расширения user modifies

Связать upstream `Check that *var_8 is assignable` с actual write lvalue/object/range, callee store_argument и enclosing
modifies wrapper; определить, какой **private** symbol/field отсутствует в разрешённом set и почему.
Проверить marker→static→emitted assigns lambda→DFCC write instrumentation по каждой стороне. `load_argument` unreachable
отделить от lost-instrumentation и от legitimate unreachable path; ранний Unsupported сам не доказывает отсутствие вызова.
Whole private-static exemption может быть намеренной; сравнить before/after state fields и writes, не предполагать blanket fix.
Не добавлять user memory в private set, не расширять public modifies, не выключать frame checks/протокол ради результата.
Предложение узкого frame/performance repair передать координатору/worker14; его реализация — следующая стадия с review.
Для будущего repair сохранить legal roundtrip/ensures PASS, false-return ensures intended uninitFAIL,
user out-of-frame write intended frameFAIL, lawful modifies PASS и unchanged ordinary/false/typed masks.

## Результаты, type audit и STOP

g0 **kani3300/m2br/**: `INPUTS.json`, `HISTORY-MAP.md`, `RESOURCE-MAP.md`, `FRAME-BINDINGS.md`,
`DIAGNOSTIC-MANIFEST.json` (inputs/pins/flags, hypotheses, removed obligations), `CI-REQUEST.md`, `REVIEW.md`,
`RESULT-KANI3300-M2BR.md` (≤25 строк; established/UNKNOWN, next discriminating experiment, no invented cause).
Отсутствие достаточного receipt → PREPARED/AWAITING_CI с bounded запросом; resource root cause не объявлять установленным.
Любой Rust delta/probe снабдить **TYPE-AUDIT.md**: operand/result/API types, usize/u64/u128, deref/references,
conversion bounds и обе стороны comparisons. Rustfmt/Luna не compiler: учесть B3R2 E0308/E0277, compilation NOT_RUN.
Статика/hash/diff --check, разрешённая rustfmt-обёртка TASK-M1; один bounded Luna High review hypotheses/diagnostic validity,
без nested delegation/повторного seed audit. Local cargo/rustc/Kani/CBMC/Miri/builds запрещены.
Research [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, stage только m2br/, push g0 без force;
diagnostic Kani commit без [skip ci], тот же author/committer, не push. Concurrency → handoff без reset/stash/чужих файлов.
Без CI/Actions/Cloud dispatch/workflow edits, raw archives/full logs/credentials, PR/issue/комментариев/сторонних PR links.
После reviewed package STOP. M3 HELD до semantic и resource/frame gates; последняя строка: `READY <sha research-коммита M2-B/R>`.
