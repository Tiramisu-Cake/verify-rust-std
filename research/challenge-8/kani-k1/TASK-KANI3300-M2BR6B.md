# KANI3300 M2-B/R6b — reset self-instrumentation repair и matched control, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна стадия подготовки, **Cloud $0**.
Fork CI только координатора, local compiler/verifier/builds запрещены. Это верификация корректности, не security-работа.
Ремонтируем несопоставимый diagnostic input, не продолжаем Hrepr bisect до восстановления пути к ensures.

**Новый handoff:** package @13eb2c6310; repaired R6-02b/run43276309576 решаем, но private-buffer frameFAIL;
R1+same-skip/run43276317655 heavy. R7 на текущей4f64 цепочке: TASK-KANI3300-M2BR7.md (15) и
TASK-KANI3300-M2BR7-CONTROLS.md (14). Historical m2br6b не менять; старый pointer-runtime не переносить в release.

## Вход и статус предыдущей пары

Прочитать `kani3300/m2br6/` @ **54252f16e48bf5e08f4eaad2fc36ee07a75c4325**, patches/HBUF-MAP/TYPE-AUDIT.
Исторические результаты не менять. По координатору P1:

- R6-01 **25197eb23e9d4b0d6b69d69ff21c2de135bdda7c**, run**43271948094**:
  144props,11167steps,563→162VCC, >6.46GiB, killed. Joint U selection/reset не снимает reported cutoff.
- R6-02 **258d6af1ea44411ec3f3aa0a4921c05c3700d6f9**, run**43271955539**:
  **1049steps,28→19VCC,0.8s**, единственный Failed Check — uninit layout Unsupported
  `Option<kani::mem_init::ArgumentBuffer>`/Enum в initialize (library/kani/src/lib.rs:63).
  Reset Option write инструментируется и рано прерывает путь; **NON_COMPARABLE**, не resource relief/подтверждение Hrepr.

Нужно сохранить exact R6-02 runtime: отдельный unmarked U pointer Option-buffer, R1 mandatory return0 и реальный epoch reset
`ARGUMENT_BUFFER = None`, exact R1 Hcopy/GLUE. Reset не удалять, не возвращать demonic return и не менять payload representation.

## Предпочтённый минимальный source-supported repair

В R1 `initialize_memory_initialization_state` уже имеет `#[kanitool::disable_checks(pointer)]` и существующий marker
`InitializeMemoryInitializationStateModel`. Pointer attribute **не** исключает UninitPass/DelayedUbPass.
В `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs::UninitInstrumenter::instrument` оба прохода используют
общий guard `KaniFunction::try_from(instance)` / **SKIPPED_ITEMS** до body instrumentation. В списке уже store/load,
copy/set/get и contract-depth models, но initializer отсутствует.

Приоритет: добавить **только существующую identity KaniModel::InitializeMemoryInitializationState** в этот skip-list
(по стилю constant + array entry), с коротким bootstrap/self-instrumentation rationale.
Это исключает только private initializer body из обоих uninit instrumentation providers; исходный вызов на harness entry,
все reset statements и их выполнение сохраняются. Не нужны новый marker/helper/sentinel/Option-layout support или ABI.
Проверить exact identity по pinned source, а не pretty-name/module wildcard. Нельзя пропускать все kani functions/все
initializers/все Enum writes или выключать пользовательские uninit/pointer/valid-value checks.
Global target/reachability collection и остальные passes не переписывать. Этот guard не меняет assigns/frame registration:
unmarked buffer не становится verifier-private target автоматически.

Trust-boundary audit: initializer на этом pin пишет только verifier-owned state, вызывает исходный any(), не содержит user
callback/reads. Обосновать исключение **всего body**, а не только Option statement. Отметить какие его прежние checks/setters
исчезнут и почему runtime reset/пользовательские checks остаются. Не выдавать такой diagnostic skip за уже принятый production fix.
Если source показывает невозможность узкого guard — STOP с конкретным API finding, не обходить его active-flag/model rewrite.

## Два local diagnostic commits — одна поправка и контроль её влияния

Source `/root/kani-fix-3300-m2br6` read-only. Создать **/root/kani-fix-3300-m2br6b**;
existing/dirty destination → STOP без reset/stash. Local branches:

1. **experiment/kani-3300-m2br6b** от exact R6-02 (fullSHA выше): R6-02b, только narrow initializer-skip compiler delta;
   mem_init.rs **побайтно unchanged** от R6-02, включая Option=None. Это основной repaired candidate.
2. **experiment/kani-3300-m2br6b-r1-control** от **1cd96e354ec45346b61c245554a50a8af8cb5ce7**:
   **тот же exact compiler delta**, runtime побайтно R1. Нужен потому, что skip удаляет всю self-instrumentation initializer,
   а не только неудачную Option запись. Compiler file hashes двух candidates должны совпадать.

До2 source-ready diagnostic commits, NOT_RELEASE_CANDIDATE, не push. Не cherry-pick repair в release/S3/M1/M2 и не менять работу14.
Проверить source reachability/marker identity/skip scope для обоих providers и неизменность user bodies/normal calls/CFG.
TYPE-AUDIT обязателен: enum variant существует, constant type KaniFunction, slice element/entry и imports/used references,
сохранённые normalized model signatures/арности; usize/bool/Option reset types unchanged. Учесть B3 E0308/E0277.
Pinned rustfmt TASK-M1/diff/source/hash/Python checks разрешены; rustfmt/Luna не compilation.
Один bounded Luna High review narrow trust boundary, source scope и matched-control logic, без nested delegation.

## CI-request: сначала путь, затем resource comparison

Тот же P1 SHA256 **fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b**,
root `postcondition_reads_initialized_return`, source bytes не менять ради cover. Existing argv/env/target/toolchain/solver/
PFC/uninit/checks/unwind/object-bits/slicing/inlining из m2br6/CI-REQUEST; actual expanded argv/identities сохранить.
Сначала build + singleton inventory **R6-02b**, затем admitted solver. R1+same-skip control — второй matched P1 configuration,
после устранения раннего Unsupported; максимум2 normal solver invocations, без P2/baseline reruns/других variants.
Existing timeout300s/watchdog>6GiB, sampling/overshoot/RSS units/PID/exit/phase limits неизменны; CI запускает координатор.

Обязательный path gate: вызов initialize и Option reset выполняются, artificial Enum Unsupported исчез,
retained target/select/store/load/return0 и ensures payload-read/assertion находятся **после** reset в emitted PFC path.
Получить location/property/guard bindings и available feasibility/reachability evidence; presence alone не доказательство
достижимости. Counts — sanity: прежние полные P1 модели порядка10^4steps и сотен properties/VCC,
R5-01 11639steps/476→182VCC, R6-01 11167/563→162; exact равенства не требовать из-за removal private instrumentation.
Повтор порядка1049steps/единственного Unsupported — провал path gate, не cheap model.
Ensures может быть упрощён: тогда дать explicit simplification/path binding, не молчаливое отсутствие property.

Report per configuration: source/tree/input, build status, GOTO/props/eloc, steps/VCC, reset/ensures/transfer bindings,
ConvertSSA milestones/runtime, vars/clauses если напечатаны, SAT-entry и bounded полный failure inventory/coverage.
Early frame/Unsupported/invalid-source снова делает semantic/resource сравнение неполным; не расширять assigns для их сокрытия.
Missing/capped fields UNKNOWN, build error solver NOT_RUN, cutoff INCOMPLETE; job/parser success не proof verdict.
Если R6-02b конвертируется, а R1+skip heavy — восстановлен различающий Hrepr experiment. Если оба конвертируются —
self-instrumentation init сама существенна/меняет пути, прежнюю Hrepr attribution пересмотреть. Если repair всё ещё рано
обрывается — разобрать именно новый boundary, не продолжать bisect. В любом случае следующие шаги отдельным handoff.

## Результат и STOP

g0 **kani3300/m2br6b/**: INPUTS.json, REPAIR-BINDINGS.md, TYPE-AUDIT.md, DIAGNOSTIC-MANIFEST.json,
patches/, STATIC-CHECKS.json, REVIEW.md, CI-REQUEST.md, RESULT-KANI3300-M2BR6B.md (≤25 строк).
Указать full parent/candidate/tree/patch/runtime/compiler hashes; reported/source-predicted/observed отдельно.
Readiness только SOURCE_READY/NOT_COMPILED до fork CI; M3/интеграция/тяжёлые M2 gates HELD, proof credit0.
Local diagnostics без [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, не push.
Research [skip ci], тот же author/committer, stage только m2br6b/, push g0 без force; concurrency → handoff без reset/stash/чужих файлов.
Без local cargo/rustc/Kani/CBMC/Miri/builds, CI/Actions/Cloud dispatch/workflow/runner edits, raw logs/archives/credentials,
PR/issue/комментариев/сторонних PR links. После reviewed repair+control STOP.
Последняя строка: `READY <sha research-коммита M2-B/R6b>`.
